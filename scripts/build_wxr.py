#!/usr/bin/env python3
"""
Demo Dispatch - WXR builder.

Reads the manifest, all post and page Markdown bodies, the comments file,
and the authors file, and assembles `themeunittestdata-v2.xml` at the repo
root. The output is RSS 2.0 with the WordPress export 1.2 namespaces, the
exact dialect the WP Importer, wp-cli import, and Playground import-content
all consume unchanged.

Markdown-to-HTML conversion is intentionally minimal:
  - Front matter (YAML between leading `---` fences) is parsed for metadata.
  - Headings (#, ##, ###, ####) become <h1>-<h4>.
  - Blockquotes (>) become <blockquote><p>...</p></blockquote>.
  - Lists (-, 1.) become <ul>/<ol> with <li>.
  - Inline emphasis (**, *) becomes <strong>/<em>.
  - Inline code (`...`) becomes <code>.
  - Links [text](url) become <a href="url">text</a>.
  - Images ![alt](path) become <figure><img/></figure>.
  - Raw HTML and raw <!-- wp:* --> block comments are passed through unchanged.

Posts in the sandbox/ folder typically already contain block markup, which is
preserved verbatim so block themes render the intended stress test.
"""

from __future__ import annotations

import html
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
MANIFEST = CONTENT / "manifest.yaml"
AUTHORS = CONTENT / "authors" / "authors.yaml"
COMMENTS = CONTENT / "comments" / "comments.yaml"
WXR_OUT = ROOT / "themeunittestdata-v2.xml"

SITE_URL = "https://example.com"
SITE_TITLE = "Demo Dispatch"
SITE_TAGLINE = "A sample site for previewing WordPress themes."

# Where attachment files actually live. Override at build time, e.g.:
#   MEDIA_BASE_URL=https://raw.githubusercontent.com/nickhamze/demo-dispatch/main/images
# When set, attachment URLs in the WXR resolve to {MEDIA_BASE_URL}/{slug}/{slug}--16x9-1200.webp.
MEDIA_BASE_URL = os.environ.get("MEDIA_BASE_URL", "")

# Stable starting IDs - leave room above the WP defaults (1, 2).
POST_ID_BASE = 1000
ATTACHMENT_ID_BASE = 5000
COMMENT_ID_BASE = 9000
USER_ID_BASE = 10  # admin is 1


# ---------------------------------------------------------------------------
# Markdown to HTML
# ---------------------------------------------------------------------------

INLINE_RULES = [
    (re.compile(r"\*\*(.+?)\*\*"), r"<strong>\1</strong>"),
    (re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)"), r"<em>\1</em>"),
    (re.compile(r"`([^`]+)`"), r"<code>\1</code>"),
    (re.compile(r"!\[([^\]]*)\]\(([^)]+)\)"),
     r'<figure class="wp-block-image"><img src="\2" alt="\1"/></figure>'),
    (re.compile(r"\[([^\]]+)\]\(([^)]+)\)"), r'<a href="\2">\1</a>'),
]


def render_inline(text: str) -> str:
    for rx, repl in INLINE_RULES:
        text = rx.sub(repl, text)
    return text


def md_to_html(body: str) -> str:
    """Tiny line-based Markdown subset, keeps embedded HTML and wp:* comments."""
    out: list[str] = []
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Pass through raw HTML / WP block markers.
        if stripped.startswith("<!--") or stripped.startswith("<"):
            out.append(line)
            i += 1
            continue

        if not stripped:
            out.append("")
            i += 1
            continue

        m = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if m:
            level = len(m.group(1))
            text = render_inline(m.group(2))
            out.append(f"<h{level}>{text}</h{level}>")
            i += 1
            continue

        if stripped.startswith(">"):
            quote_lines: list[str] = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(lines[i].strip().lstrip(">").strip())
                i += 1
            inner = render_inline(" ".join(quote_lines))
            out.append(f"<blockquote><p>{inner}</p></blockquote>")
            continue

        if re.match(r"^[-*]\s+", stripped):
            items: list[str] = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(re.sub(r"^[-*]\s+", "", lines[i].strip()))
                i += 1
            ul = "<ul>" + "".join(f"<li>{render_inline(it)}</li>" for it in items) + "</ul>"
            out.append(ul)
            continue

        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            ol = "<ol>" + "".join(f"<li>{render_inline(it)}</li>" for it in items) + "</ol>"
            out.append(ol)
            continue

        # Paragraph: gather until blank line. Note: a line beginning with `*`
        # or `-` is only a list item when followed by whitespace; otherwise it
        # is a normal paragraph using emphasis markup, e.g. `*scale 1:50,000*`.
        para: list[str] = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if not nxt:
                break
            if nxt.startswith(("#", ">", "<")):
                break
            if re.match(r"^[-*]\s+", nxt):
                break
            if re.match(r"^\d+\.\s+", nxt):
                break
            para.append(nxt)
            i += 1
        out.append(f"<p>{render_inline(' '.join(para))}</p>")

    return "\n\n".join(line for line in out if line != "")


# ---------------------------------------------------------------------------
# Content loaders
# ---------------------------------------------------------------------------

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def load_md(path: Path) -> tuple[dict, str]:
    text = path.read_text()
    m = FM_RE.match(text)
    if not m:
        return {}, text
    front = yaml.safe_load(m.group(1)) or {}
    body = text[m.end():]
    return front, body


def load_manifest() -> dict:
    return yaml.safe_load(MANIFEST.read_text())


def load_authors() -> list[dict]:
    return yaml.safe_load(AUTHORS.read_text())


def load_comments() -> dict:
    raw = yaml.safe_load(COMMENTS.read_text())
    src = raw.get("comments", {}) if raw else {}
    out: dict[str, list[dict]] = {}
    for slug, value in src.items():
        if isinstance(value, list):
            out[slug] = value
            continue
        if isinstance(value, dict) and "template" in value:
            out[slug] = expand_template(value["template"])
            continue
        out[slug] = []
    return out


def expand_template(tpl: dict) -> list[dict]:
    """Generate the 53 templated comments for many-comments-pagination-test."""
    authors = tpl.get("authors", [])
    sentences = tpl.get("sentences", [])
    nested_one = {5, 12, 17, 25, 30, 38, 47}
    nested_two = {18, 41}
    post_author = {7}
    base_dt = datetime(2024, 6, 3, 8, 0, 0)
    out: list[dict] = []
    for n in range(1, 54):
        author = authors[(n - 1) % len(authors)]
        sentence = sentences[(n - 1) % len(sentences)]
        item: dict = {
            "id": n,
            "author": "tomas" if n in post_author else author,
            "author_email": (
                "tomas@demo-dispatch.example" if n in post_author
                else f"{author.split()[0].lower()}@example.com"
            ),
            "date": base_dt.replace(
                hour=(8 + n) % 24,
                minute=(n * 7) % 60,
            ).isoformat(sep=" "),
            "content": sentence,
        }
        if n in post_author:
            item["author_user"] = "tomas"
        if n in nested_one:
            item["parent"] = n - 1
        if n in nested_two:
            item["parent"] = n - 2
        out.append(item)
    return out


def load_post_body(slug: str) -> str:
    for sub in ("articles", "sandbox", "pages"):
        path = CONTENT / sub / f"{slug}.md"
        if path.exists():
            _, body = load_md(path)
            return body
    return ""


# Bare media references in post bodies (e.g. ![alt](lighthouse.webp) or
# src="harbor.webp") are rewritten to absolute URLs at build time so they
# resolve in any preview environment.
_BARE_MEDIA_RE = re.compile(
    r'(?P<prefix>"|\(|src=")(?P<slug>[a-z][a-z0-9\-]*)\.(?P<ext>webp|mp4|mp3|pdf|jpg|jpeg|png)(?P<suffix>"|\))'
)


_LEADING_H1_RE = re.compile(r"^\s*#\s+[^\n]+\n+")


def strip_leading_h1(body: str) -> str:
    # WordPress renders the post/page title as <h1>; a leading H1 in the body
    # produces a visual double title in most themes. Authors keep the H1 in
    # markdown for readability; we strip it at build time.
    return _LEADING_H1_RE.sub("", body, count=1)


def absolutize_media(body: str) -> str:
    if not MEDIA_BASE_URL:
        return body

    def _sub(m: re.Match) -> str:
        slug = m.group("slug")
        ext = m.group("ext")
        if ext == "webp":
            url = f"{MEDIA_BASE_URL.rstrip('/')}/{slug}/{slug}--16x9-1200.webp"
        elif ext in {"mp3", "mp4", "pdf"}:
            url = f"{MEDIA_BASE_URL.rstrip('/')}/_media/{slug}.{ext}"
        else:
            url = f"{MEDIA_BASE_URL.rstrip('/')}/{slug}/{slug}--16x9-1200.{ext}"
        return f"{m.group('prefix')}{url}{m.group('suffix')}"

    return _BARE_MEDIA_RE.sub(_sub, body)


# ---------------------------------------------------------------------------
# WXR emission
# ---------------------------------------------------------------------------

def cdata(text: str) -> str:
    return f"<![CDATA[{text.replace(']]>', ']]]]><![CDATA[>')}]]>"


def fmt_dt(value) -> str:
    if isinstance(value, str):
        dt = datetime.fromisoformat(value.replace(" ", "T"))
    elif isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.combine(value, datetime.min.time())
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")


def fmt_sql(value) -> str:
    if isinstance(value, str):
        dt = datetime.fromisoformat(value.replace(" ", "T"))
    elif isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.combine(value, datetime.min.time())
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def render_author(author: dict, user_id: int) -> str:
    return (
        "  <wp:author>\n"
        f"    <wp:author_id>{user_id}</wp:author_id>\n"
        f"    <wp:author_login>{cdata(author['login'])}</wp:author_login>\n"
        f"    <wp:author_email>{cdata(author['email'])}</wp:author_email>\n"
        f"    <wp:author_display_name>{cdata(author['display_name'])}</wp:author_display_name>\n"
        f"    <wp:author_first_name>{cdata(author.get('first_name', ''))}</wp:author_first_name>\n"
        f"    <wp:author_last_name>{cdata(author.get('last_name', ''))}</wp:author_last_name>\n"
        "  </wp:author>\n"
    )


def render_category(slug: str, name: str, description: str) -> str:
    return (
        "  <wp:category>\n"
        f"    <wp:term_id>{abs(hash(slug)) % 100000}</wp:term_id>\n"
        f"    <wp:category_nicename>{cdata(slug)}</wp:category_nicename>\n"
        "    <wp:category_parent></wp:category_parent>\n"
        f"    <wp:cat_name>{cdata(name)}</wp:cat_name>\n"
        f"    <wp:category_description>{cdata(description)}</wp:category_description>\n"
        "  </wp:category>\n"
    )


def render_tag(slug: str) -> str:
    return (
        "  <wp:tag>\n"
        f"    <wp:term_id>{abs(hash('tag:' + slug)) % 100000}</wp:term_id>\n"
        f"    <wp:tag_slug>{cdata(slug)}</wp:tag_slug>\n"
        f"    <wp:tag_name>{cdata(slug.replace('-', ' '))}</wp:tag_name>\n"
        "  </wp:tag>\n"
    )


def render_comment(c: dict, base_id: int) -> str:
    cid = base_id + c["id"]
    parent = base_id + c["parent"] if c.get("parent") else 0
    pieces = [
        "    <wp:comment>",
        f"      <wp:comment_id>{cid}</wp:comment_id>",
        f"      <wp:comment_author>{cdata(str(c.get('author', '')))}</wp:comment_author>",
        f"      <wp:comment_author_email>{cdata(c.get('author_email', ''))}</wp:comment_author_email>",
        f"      <wp:comment_author_url>{cdata(c.get('author_url', ''))}</wp:comment_author_url>",
        f"      <wp:comment_date>{fmt_sql(c['date'])}</wp:comment_date>",
        f"      <wp:comment_date_gmt>{fmt_sql(c['date'])}</wp:comment_date_gmt>",
        f"      <wp:comment_content>{cdata(c.get('content', ''))}</wp:comment_content>",
        f"      <wp:comment_approved>{cdata('1' if c.get('approved', True) else '0')}</wp:comment_approved>",
        f"      <wp:comment_type>{cdata(c.get('type', ''))}</wp:comment_type>",
        f"      <wp:comment_parent>{parent}</wp:comment_parent>",
        "    </wp:comment>",
    ]
    return "\n".join(pieces) + "\n"


def render_post(item: dict, body: str, post_id: int, author_login: str,
                comments: list[dict], comment_base_id: int) -> str:
    title = str(item.get("title", "") or "")
    slug = item["slug"]
    link = f"{SITE_URL}/{slug}/"
    pubdate = fmt_dt(item["date"])
    sql_date = fmt_sql(item["date"])
    status = item.get("status", "publish")
    post_type = item.get("post_type", "post")
    post_format = item.get("format", "standard")
    excerpt = (item.get("summary", "") or "").strip()
    sticky = "1" if item.get("sticky") else "0"
    password = item.get("password", "")

    cats: list[str] = []
    cat_slug = item.get("category")
    if cat_slug:
        cats.append(
            f'      <category domain="category" nicename="{xml_escape(cat_slug)}">'
            f"{cdata(cat_slug.title())}</category>"
        )
    for tag in item.get("tags", []) or []:
        cats.append(
            f'      <category domain="post_tag" nicename="{xml_escape(tag)}">'
            f"{cdata(tag.replace('-', ' '))}</category>"
        )
    if post_format != "standard":
        cats.append(
            f'      <category domain="post_format" nicename="post-format-{post_format}">'
            f"{cdata('Post Format: ' + post_format.title())}</category>"
        )

    meta_lines: list[str] = []
    meta_lines.append(
        "      <wp:postmeta>\n"
        f"        <wp:meta_key>{cdata('_edit_last')}</wp:meta_key>\n"
        f"        <wp:meta_value>{cdata('1')}</wp:meta_value>\n"
        "      </wp:postmeta>"
    )
    if item.get("featured_image"):
        meta_lines.append(
            "      <wp:postmeta>\n"
            f"        <wp:meta_key>{cdata('_thumbnail_id')}</wp:meta_key>\n"
            f"        <wp:meta_value>{cdata(str(item['_thumbnail_id']))}</wp:meta_value>\n"
            "      </wp:postmeta>"
        )

    comment_blocks = "\n".join(render_comment(c, comment_base_id) for c in comments)

    return (
        "    <item>\n"
        f"      <title>{cdata(title)}</title>\n"
        f"      <link>{xml_escape(link)}</link>\n"
        f"      <pubDate>{pubdate}</pubDate>\n"
        f"      <dc:creator>{cdata(author_login)}</dc:creator>\n"
        f"      <guid isPermaLink=\"false\">{xml_escape(SITE_URL)}/?p={post_id}</guid>\n"
        "      <description></description>\n"
        f"      <content:encoded>{cdata(body)}</content:encoded>\n"
        f"      <excerpt:encoded>{cdata(excerpt)}</excerpt:encoded>\n"
        f"      <wp:post_id>{post_id}</wp:post_id>\n"
        f"      <wp:post_date>{cdata(sql_date)}</wp:post_date>\n"
        f"      <wp:post_date_gmt>{cdata(sql_date)}</wp:post_date_gmt>\n"
        "      <wp:comment_status><![CDATA[open]]></wp:comment_status>\n"
        "      <wp:ping_status><![CDATA[open]]></wp:ping_status>\n"
        f"      <wp:post_name>{cdata(slug)}</wp:post_name>\n"
        f"      <wp:status>{cdata(status)}</wp:status>\n"
        f"      <wp:post_parent>{item.get('post_parent', 0)}</wp:post_parent>\n"
        f"      <wp:menu_order>{item.get('order', 0)}</wp:menu_order>\n"
        f"      <wp:post_type>{cdata(post_type)}</wp:post_type>\n"
        f"      <wp:post_password>{cdata(password)}</wp:post_password>\n"
        f"      <wp:is_sticky>{sticky}</wp:is_sticky>\n"
        + ("\n".join(cats) + "\n" if cats else "")
        + ("\n".join(meta_lines) + "\n" if meta_lines else "")
        + (comment_blocks if comment_blocks else "")
        + "    </item>\n"
    )


def render_attachment(slug: str, post_id: int, author_login: str,
                      attachment_id: int, alt: str, parent: int) -> str:
    if MEDIA_BASE_URL:
        url = f"{MEDIA_BASE_URL.rstrip('/')}/{slug}/{slug}--16x9-1200.webp"
    else:
        url = f"{SITE_URL}/wp-content/uploads/{slug}.webp"
    pubdate = fmt_dt(datetime(2026, 4, 20, tzinfo=timezone.utc))
    sql_date = fmt_sql(datetime(2026, 4, 20))
    return (
        "    <item>\n"
        f"      <title>{cdata(slug)}</title>\n"
        f"      <link>{xml_escape(SITE_URL + '/' + slug + '/')}</link>\n"
        f"      <pubDate>{pubdate}</pubDate>\n"
        f"      <dc:creator>{cdata(author_login)}</dc:creator>\n"
        f"      <guid isPermaLink=\"false\">{xml_escape(url)}</guid>\n"
        "      <description></description>\n"
        f"      <content:encoded>{cdata('')}</content:encoded>\n"
        f"      <excerpt:encoded>{cdata('')}</excerpt:encoded>\n"
        f"      <wp:post_id>{attachment_id}</wp:post_id>\n"
        f"      <wp:post_date>{cdata(sql_date)}</wp:post_date>\n"
        f"      <wp:post_date_gmt>{cdata(sql_date)}</wp:post_date_gmt>\n"
        "      <wp:comment_status><![CDATA[closed]]></wp:comment_status>\n"
        "      <wp:ping_status><![CDATA[closed]]></wp:ping_status>\n"
        f"      <wp:post_name>{cdata(slug)}</wp:post_name>\n"
        "      <wp:status><![CDATA[inherit]]></wp:status>\n"
        f"      <wp:post_parent>{parent}</wp:post_parent>\n"
        "      <wp:menu_order>0</wp:menu_order>\n"
        "      <wp:post_type><![CDATA[attachment]]></wp:post_type>\n"
        "      <wp:post_password><![CDATA[]]></wp:post_password>\n"
        "      <wp:is_sticky>0</wp:is_sticky>\n"
        f"      <wp:attachment_url>{cdata(url)}</wp:attachment_url>\n"
        "      <wp:postmeta>\n"
        f"        <wp:meta_key>{cdata('_wp_attachment_image_alt')}</wp:meta_key>\n"
        f"        <wp:meta_value>{cdata(alt)}</wp:meta_value>\n"
        "      </wp:postmeta>\n"
        "    </item>\n"
    )


# ---------------------------------------------------------------------------
# Navigation menus
#
# Block themes (Twenty Twenty-Five, Twenty Twenty-Four, etc.) render their
# header menu through a `wp:navigation` Navigation block. When no explicit
# ref is set, the block falls back to the first published `wp_navigation`
# post it can find, and if none exist it auto-generates a flat list of
# every page - which is the default "too many top-level items" look we want
# to replace.
#
# We emit one `wp_navigation` post per menu declared in `menus:`. Each item
# becomes a `wp:navigation-link` block (or a `wp:navigation-submenu` block
# when it has children). We resolve `page:`, `category:`, and `tag:` targets
# to plain URLs so the blocks render without needing exact post / term IDs
# on import.
#
# Classic themes do not use `wp_navigation`; they rely on menu locations
# registered via `register_nav_menus()` and assigned in the Customizer.
# Without setting theme mods (which a WXR cannot do) they show a flat page
# list, which is the acceptable "ok on non-ones" fallback.
# ---------------------------------------------------------------------------


def _resolve_menu_target(target: str) -> tuple[str, str, str]:
    """Return (kind, type, url) for a menu target string.

    Targets look like:
      page:home                -> post-type, page, /home/
      category:dispatch        -> taxonomy, category, /category/dispatch/
      tag:print                -> taxonomy, post_tag, /tag/print/
      https://example.invalid  -> custom, custom, https://example.invalid
      /feed/                   -> custom, custom, /feed/
    """
    if target.startswith("page:"):
        slug = target[len("page:"):]
        if slug in {"home", ""}:
            url = "/"
        else:
            url = f"/{slug}/"
        return ("post-type", "page", url)
    if target.startswith("category:"):
        slug = target[len("category:"):]
        return ("taxonomy", "category", f"/category/{slug}/")
    if target.startswith("tag:"):
        slug = target[len("tag:"):]
        return ("taxonomy", "post_tag", f"/tag/{slug}/")
    return ("custom", "custom", target)


def _nav_block_attrs(item: dict) -> str:
    kind, obj_type, url = _resolve_menu_target(item["target"])
    attrs = {
        "label": item["label"],
        "url": url,
        "kind": kind,
        "type": obj_type,
    }
    import json as _json
    return _json.dumps(attrs, ensure_ascii=False, separators=(",", ":"))


def render_nav_block(item: dict) -> str:
    """Render a single menu item as a Gutenberg navigation block comment."""
    attrs = _nav_block_attrs(item)
    children = item.get("children") or []
    if not children:
        return f"<!-- wp:navigation-link {attrs} /-->\n"
    parts = [f"<!-- wp:navigation-submenu {attrs} -->\n"]
    for child in children:
        parts.append(render_nav_block(child))
    parts.append("<!-- /wp:navigation-submenu -->\n")
    return "".join(parts)


def render_navigation_post(menu: dict, post_id: int) -> str:
    """Emit a `wp_navigation` post whose content is the menu block tree."""
    slug = menu["slug"]
    name = menu.get("name", slug.replace("-", " ").title())
    body = "".join(render_nav_block(item) for item in menu.get("items", []))
    pubdate = fmt_dt(datetime(2026, 4, 20, tzinfo=timezone.utc))
    sql_date = fmt_sql(datetime(2026, 4, 20))
    return (
        "    <item>\n"
        f"      <title>{cdata(name)}</title>\n"
        f"      <link>{xml_escape(SITE_URL + '/' + slug + '/')}</link>\n"
        f"      <pubDate>{pubdate}</pubDate>\n"
        f"      <dc:creator>{cdata('admin')}</dc:creator>\n"
        f"      <guid isPermaLink=\"false\">{xml_escape(SITE_URL)}/?p={post_id}</guid>\n"
        "      <description></description>\n"
        f"      <content:encoded>{cdata(body)}</content:encoded>\n"
        f"      <excerpt:encoded>{cdata('')}</excerpt:encoded>\n"
        f"      <wp:post_id>{post_id}</wp:post_id>\n"
        f"      <wp:post_date>{cdata(sql_date)}</wp:post_date>\n"
        f"      <wp:post_date_gmt>{cdata(sql_date)}</wp:post_date_gmt>\n"
        "      <wp:comment_status><![CDATA[closed]]></wp:comment_status>\n"
        "      <wp:ping_status><![CDATA[closed]]></wp:ping_status>\n"
        f"      <wp:post_name>{cdata(slug)}</wp:post_name>\n"
        "      <wp:status><![CDATA[publish]]></wp:status>\n"
        "      <wp:post_parent>0</wp:post_parent>\n"
        "      <wp:menu_order>0</wp:menu_order>\n"
        "      <wp:post_type><![CDATA[wp_navigation]]></wp:post_type>\n"
        "      <wp:post_password><![CDATA[]]></wp:post_password>\n"
        "      <wp:is_sticky>0</wp:is_sticky>\n"
        "    </item>\n"
    )


def render_term_for_format(fmt: str) -> str:
    return (
        "  <wp:term>\n"
        f"    <wp:term_id>{abs(hash('fmt:' + fmt)) % 100000}</wp:term_id>\n"
        "    <wp:term_taxonomy><![CDATA[post_format]]></wp:term_taxonomy>\n"
        f"    <wp:term_slug>{cdata('post-format-' + fmt)}</wp:term_slug>\n"
        f"    <wp:term_name>{cdata('Post Format: ' + fmt.title())}</wp:term_name>\n"
        "  </wp:term>\n"
    )


def main() -> int:
    manifest = load_manifest()
    authors = load_authors()
    comments = load_comments()

    author_by_login: dict[str, dict] = {a["login"]: a for a in authors}
    user_id_by_login: dict[str, int] = {
        a["login"]: USER_ID_BASE + i for i, a in enumerate(authors)
    }

    # Pre-allocate IDs.
    next_post_id = POST_ID_BASE
    next_att_id = ATTACHMENT_ID_BASE
    next_comment_base = COMMENT_ID_BASE

    posts_xml: list[str] = []
    attachments_xml: list[str] = []
    seen_attachments: dict[str, int] = {}

    # Build post items.
    for item in manifest.get("posts", []):
        slug = item["slug"]
        body = load_post_body(slug)
        author_login = item.get("author", "admin")
        post_id = next_post_id
        next_post_id += 1

        # Featured image attachment.
        feat = item.get("featured_image")
        if feat:
            if feat not in seen_attachments:
                aid = next_att_id
                next_att_id += 1
                alt_path = ROOT / "images" / feat / f"{feat}.alt.txt"
                alt = alt_path.read_text().strip() if alt_path.exists() else feat
                attachments_xml.append(
                    render_attachment(feat, post_id, author_login, aid, alt, post_id)
                )
                seen_attachments[feat] = aid
            item["_thumbnail_id"] = seen_attachments[feat]

        post_comments = comments.get(slug, [])
        comment_base = next_comment_base
        next_comment_base += 1000  # roomy stride per post

        # Convert markdown body to HTML, but preserve raw HTML / wp:* blocks.
        html_body = absolutize_media(md_to_html(strip_leading_h1(body)))
        posts_xml.append(
            render_post(item, html_body, post_id, author_login,
                        post_comments, comment_base)
        )

    # Build page items.
    for page in manifest.get("pages", []):
        slug = page["slug"]
        body = load_post_body(slug.split("/")[-1])
        page = dict(page)
        page["post_type"] = "page"
        page["post_parent"] = 0  # parent resolution would need a second pass
        post_id = next_post_id
        next_post_id += 1
        page["date"] = "2026-04-20 09:00:00"
        page["category"] = None
        html_body = absolutize_media(md_to_html(strip_leading_h1(body)))
        posts_xml.append(
            render_post(page, html_body, post_id, "admin",
                        [], next_comment_base)
        )
        next_comment_base += 1000

    # Emit a wp_navigation post per declared menu so block themes use the
    # curated structure instead of the default full-page-list fallback.
    nav_xml: list[str] = []
    for menu in manifest.get("menus", []) or []:
        post_id = next_post_id
        next_post_id += 1
        nav_xml.append(render_navigation_post(menu, post_id))

    authors_xml = "".join(
        render_author(a, user_id_by_login[a["login"]]) for a in authors
    )
    cats_xml = "".join(
        render_category(c["slug"], c["name"], c.get("description", ""))
        for c in manifest.get("categories", [])
    )
    tags_xml = "".join(render_tag(t) for t in manifest.get("tags", []))
    formats = sorted({
        item.get("format", "standard")
        for item in manifest.get("posts", [])
        if item.get("format", "standard") != "standard"
    })
    terms_xml = "".join(render_term_for_format(f) for f in formats)

    pieces = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        '<rss version="2.0"\n'
        '     xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"\n'
        '     xmlns:content="http://purl.org/rss/1.0/modules/content/"\n'
        '     xmlns:wfw="http://wellformedweb.org/CommentAPI/"\n'
        '     xmlns:dc="http://purl.org/dc/elements/1.1/"\n'
        '     xmlns:wp="http://wordpress.org/export/1.2/">\n',
        "  <channel>\n",
        f"    <title>{xml_escape(SITE_TITLE)}</title>\n",
        f"    <link>{xml_escape(SITE_URL)}</link>\n",
        f"    <description>{xml_escape(SITE_TAGLINE)}</description>\n",
        f"    <pubDate>{fmt_dt(datetime.now(timezone.utc))}</pubDate>\n",
        "    <language>en-US</language>\n",
        "    <wp:wxr_version>1.2</wp:wxr_version>\n",
        f"    <wp:base_site_url>{xml_escape(SITE_URL)}</wp:base_site_url>\n",
        f"    <wp:base_blog_url>{xml_escape(SITE_URL)}</wp:base_blog_url>\n",
        authors_xml,
        cats_xml,
        tags_xml,
        terms_xml,
        "".join(attachments_xml),
        "".join(nav_xml),
        "".join(posts_xml),
        "  </channel>\n",
        "</rss>\n",
    ]

    WXR_OUT.write_text("".join(pieces))
    print(f"-> wrote {WXR_OUT.relative_to(ROOT)} "
          f"({WXR_OUT.stat().st_size / 1024:.1f} KB, "
          f"{len(posts_xml)} items, {len(attachments_xml)} attachments)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
