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
from datetime import datetime, timedelta, timezone
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


# Stable per-slug term IDs. We hash so the same slug always gets the same ID
# across builds, which keeps menu items and term assignments coherent without a
# second pass to look IDs up.

def category_term_id(slug: str) -> int:
    return abs(hash("cat:" + slug)) % 100000


def tag_term_id(slug: str) -> int:
    return abs(hash("tag:" + slug)) % 100000


def menu_term_id(slug: str) -> int:
    return abs(hash("menu:" + slug)) % 100000


def format_term_id(fmt: str) -> int:
    return abs(hash("fmt:" + fmt)) % 100000


def render_category(slug: str, name: str, description: str,
                    parent_slug: str = "") -> str:
    """Categories as wp:term so we can express hierarchy via term_parent.

    The importer (class-wp-import.php process_term) accepts wp:term entries
    with term_taxonomy=category and resolves parent slugs through
    term_exists(parent_slug, taxonomy). It runs alongside process_categories,
    so wp:term and wp:category entries can coexist - we standardise on
    wp:term for everything to keep one code path.
    """
    return (
        "  <wp:term>\n"
        f"    <wp:term_id>{category_term_id(slug)}</wp:term_id>\n"
        "    <wp:term_taxonomy><![CDATA[category]]></wp:term_taxonomy>\n"
        f"    <wp:term_slug>{cdata(slug)}</wp:term_slug>\n"
        f"    <wp:term_parent>{cdata(parent_slug)}</wp:term_parent>\n"
        f"    <wp:term_name>{cdata(name)}</wp:term_name>\n"
        f"    <wp:term_description>{cdata(description)}</wp:term_description>\n"
        "  </wp:term>\n"
    )


def render_tag(slug: str) -> str:
    return (
        "  <wp:tag>\n"
        f"    <wp:term_id>{tag_term_id(slug)}</wp:term_id>\n"
        f"    <wp:tag_slug>{cdata(slug)}</wp:tag_slug>\n"
        f"    <wp:tag_name>{cdata(slug.replace('-', ' '))}</wp:tag_name>\n"
        "  </wp:tag>\n"
    )


def render_nav_menu_term(slug: str, name: str) -> str:
    """A nav_menu term is what classic-menu themes look up by location and what
    block themes can convert through WP_Navigation_Fallback when no
    wp_navigation post exists."""
    return (
        "  <wp:term>\n"
        f"    <wp:term_id>{menu_term_id(slug)}</wp:term_id>\n"
        "    <wp:term_taxonomy><![CDATA[nav_menu]]></wp:term_taxonomy>\n"
        f"    <wp:term_slug>{cdata(slug)}</wp:term_slug>\n"
        f"    <wp:term_name>{cdata(name)}</wp:term_name>\n"
        "  </wp:term>\n"
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
    ]
    # commentmeta is processed by class-wp-import.php process_comments, which
    # passes each entry through wp_filter_comment / add_comment_meta. Akismet,
    # rating plugins, and translation plugins all read these keys, so emitting
    # them lets a downstream plugin install pick the comment up correctly.
    for key, value in (c.get("meta") or {}).items():
        pieces.append(
            "      <wp:commentmeta>\n"
            f"        <wp:meta_key>{cdata(str(key))}</wp:meta_key>\n"
            f"        <wp:meta_value>{cdata(str(value))}</wp:meta_value>\n"
            "      </wp:commentmeta>"
        )
    pieces.append("    </wp:comment>")
    return "\n".join(pieces) + "\n"


def _postmeta(key: str, value: str) -> str:
    return (
        "      <wp:postmeta>\n"
        f"        <wp:meta_key>{cdata(key)}</wp:meta_key>\n"
        f"        <wp:meta_value>{cdata(value)}</wp:meta_value>\n"
        "      </wp:postmeta>"
    )


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
    meta_lines.append(_postmeta("_edit_last", "1"))
    if item.get("featured_image"):
        meta_lines.append(
            _postmeta("_thumbnail_id", str(item["_thumbnail_id"]))
        )
    if item.get("template"):
        # _wp_page_template is read by get_page_template_slug() and tells the
        # theme to render this page through a specific template file. Block
        # themes register block templates under the same meta key, so the same
        # value works on both classic and block themes that ship the named
        # template; if the template is missing the theme falls back silently.
        meta_lines.append(_postmeta("_wp_page_template", item["template"]))
    enclosure = item.get("enclosure")
    if enclosure:
        # The enclosure postmeta takes the form `url\nlength\nmime` on a single
        # meta_value, with backfill_attachment_urls remapping the URL after
        # import. We also emit an RSS <enclosure /> element below for
        # podcasting clients that read the feed directly.
        meta_lines.append(
            _postmeta(
                "enclosure",
                f"{enclosure['url']}\n{enclosure.get('length', 0)}\n{enclosure.get('type', 'audio/mpeg')}",
            )
        )
    for key, value in (item.get("custom_fields") or {}).items():
        meta_lines.append(_postmeta(str(key), str(value)))

    enclosure_element = ""
    if enclosure:
        enclosure_element = (
            f'      <enclosure url="{xml_escape(enclosure["url"])}" '
            f'length="{int(enclosure.get("length", 0))}" '
            f'type="{xml_escape(enclosure.get("type", "audio/mpeg"))}"/>\n'
        )

    comment_blocks = "\n".join(render_comment(c, comment_base_id) for c in comments)

    # post_name for pages that live under a parent (slug "notebooks/red") is
    # only the leaf segment; WordPress reconstructs the full path from the
    # post_parent chain. Posts always use the literal slug.
    post_name = slug.rsplit("/", 1)[-1] if post_type == "page" else slug

    return (
        "    <item>\n"
        f"      <title>{cdata(title)}</title>\n"
        f"      <link>{xml_escape(link)}</link>\n"
        f"      <pubDate>{pubdate}</pubDate>\n"
        f"      <dc:creator>{cdata(author_login)}</dc:creator>\n"
        f"      <guid isPermaLink=\"false\">{xml_escape(SITE_URL)}/?p={post_id}</guid>\n"
        "      <description></description>\n"
        f"{enclosure_element}"
        f"      <content:encoded>{cdata(body)}</content:encoded>\n"
        f"      <excerpt:encoded>{cdata(excerpt)}</excerpt:encoded>\n"
        f"      <wp:post_id>{post_id}</wp:post_id>\n"
        f"      <wp:post_date>{cdata(sql_date)}</wp:post_date>\n"
        f"      <wp:post_date_gmt>{cdata(sql_date)}</wp:post_date_gmt>\n"
        "      <wp:comment_status><![CDATA[open]]></wp:comment_status>\n"
        "      <wp:ping_status><![CDATA[open]]></wp:ping_status>\n"
        f"      <wp:post_name>{cdata(post_name)}</wp:post_name>\n"
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


def render_navigation_post(menu: dict, post_id: int,
                           when: datetime) -> str:
    """Emit a `wp_navigation` post whose content is the menu block tree.

    `when` controls publish date; WP_Navigation_Fallback picks the most
    recently published wp_navigation post when the Navigation block has no
    explicit ref, so the primary menu's `when` must be newer than any other
    wp_navigation post in the dataset.
    """
    slug = menu["slug"]
    name = menu.get("name", slug.replace("-", " ").title())
    body = "".join(render_nav_block(item) for item in menu.get("items", []))
    pubdate = fmt_dt(when)
    sql_date = fmt_sql(when)
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


# ---------------------------------------------------------------------------
# Classic nav_menu / nav_menu_item emission
#
# The Customizer-era "Menus" UI in classic themes reads from the nav_menu
# taxonomy: each menu is a term, each menu item is a `nav_menu_item` post in
# that term, and ordering is by menu_order.  Hierarchy uses the postmeta
# `_menu_item_menu_item_parent`, which references another nav_menu_item's
# post ID.  Targets are encoded through three other postmeta entries:
#   - _menu_item_type   = 'post_type' | 'taxonomy' | 'custom'
#   - _menu_item_object = 'page' | 'category' | 'post_tag' | 'custom'
#   - _menu_item_object_id = the referenced post / term ID
# Custom URLs additionally use _menu_item_url.
#
# Emitting these alongside the wp_navigation post means classic themes get a
# full editable menu (assigned to `primary` by the blueprint runPHP step),
# while block themes still pick up the curated wp_navigation post and avoid
# the page-list fallback.
# ---------------------------------------------------------------------------


def _flatten_menu_items(menus: list[dict],
                        next_post_id_ref: list[int]) -> list[dict]:
    """Walk every menu tree, allocating a post_id per item.

    Returns a flat list of dicts ready for render_nav_menu_item().  IDs are
    allocated depth-first so children always have a stable numerical parent
    reference.
    """
    out: list[dict] = []
    for menu in menus:
        menu_slug = menu["slug"]
        menu_name = menu["name"]
        position = [0]

        def walk(items: list[dict], parent_post_id: int) -> None:
            for item in items:
                pid = next_post_id_ref[0]
                next_post_id_ref[0] += 1
                position[0] += 1
                out.append({
                    "menu_slug": menu_slug,
                    "menu_name": menu_name,
                    "label": item["label"],
                    "target": item["target"],
                    "post_id": pid,
                    "parent_post_id": parent_post_id,
                    "position": position[0],
                })
                if item.get("children"):
                    walk(item["children"], pid)

        walk(menu.get("items", []), 0)
    return out


def render_nav_menu_item(item: dict, page_id_by_slug: dict[str, int]) -> str:
    label = item["label"]
    target = item["target"]
    if target.startswith("page:"):
        slug = target[len("page:"):]
        item_type = "post_type"
        obj_type = "page"
        object_id = page_id_by_slug.get(slug, 0)
        url = ""
    elif target.startswith("category:"):
        slug = target[len("category:"):]
        item_type = "taxonomy"
        obj_type = "category"
        object_id = category_term_id(slug)
        url = ""
    elif target.startswith("tag:"):
        slug = target[len("tag:"):]
        item_type = "taxonomy"
        obj_type = "post_tag"
        object_id = tag_term_id(slug)
        url = ""
    else:
        item_type = "custom"
        obj_type = "custom"
        # WP convention: custom items store their own post_id in object_id.
        object_id = item["post_id"]
        url = target

    pubdate = fmt_dt(datetime(2026, 4, 20, tzinfo=timezone.utc))
    sql_date = fmt_sql(datetime(2026, 4, 20))

    # `_menu_item_classes` is stored as a serialised PHP array.  WP writes
    # `a:1:{i:0;s:0:"";}` for an empty class list and crashes on import if it
    # is missing entirely; the importer round-trips the value verbatim.
    metas = "\n".join([
        _postmeta("_menu_item_type", item_type),
        _postmeta("_menu_item_menu_item_parent", str(item["parent_post_id"])),
        _postmeta("_menu_item_object_id", str(object_id)),
        _postmeta("_menu_item_object", obj_type),
        _postmeta("_menu_item_target", ""),
        _postmeta("_menu_item_classes", 'a:1:{i:0;s:0:"";}'),
        _postmeta("_menu_item_xfn", ""),
        _postmeta("_menu_item_url", url),
    ])

    return (
        "    <item>\n"
        f"      <title>{cdata(label)}</title>\n"
        f"      <link>{xml_escape(SITE_URL + '/?p=' + str(item['post_id']))}</link>\n"
        f"      <pubDate>{pubdate}</pubDate>\n"
        f"      <dc:creator>{cdata('admin')}</dc:creator>\n"
        f"      <guid isPermaLink=\"false\">{xml_escape(SITE_URL)}/?p={item['post_id']}</guid>\n"
        "      <description></description>\n"
        f"      <content:encoded>{cdata('')}</content:encoded>\n"
        f"      <excerpt:encoded>{cdata('')}</excerpt:encoded>\n"
        f"      <wp:post_id>{item['post_id']}</wp:post_id>\n"
        f"      <wp:post_date>{cdata(sql_date)}</wp:post_date>\n"
        f"      <wp:post_date_gmt>{cdata(sql_date)}</wp:post_date_gmt>\n"
        "      <wp:comment_status><![CDATA[closed]]></wp:comment_status>\n"
        "      <wp:ping_status><![CDATA[closed]]></wp:ping_status>\n"
        f"      <wp:post_name>{cdata(str(item['post_id']))}</wp:post_name>\n"
        "      <wp:status><![CDATA[publish]]></wp:status>\n"
        "      <wp:post_parent>0</wp:post_parent>\n"
        f"      <wp:menu_order>{item['position']}</wp:menu_order>\n"
        "      <wp:post_type><![CDATA[nav_menu_item]]></wp:post_type>\n"
        "      <wp:post_password><![CDATA[]]></wp:post_password>\n"
        "      <wp:is_sticky>0</wp:is_sticky>\n"
        f'      <category domain="nav_menu" nicename="{xml_escape(item["menu_slug"])}">'
        f'{cdata(item["menu_name"])}</category>\n'
        f"{metas}\n"
        "    </item>\n"
    )


def render_term_for_format(fmt: str) -> str:
    return (
        "  <wp:term>\n"
        f"    <wp:term_id>{format_term_id(fmt)}</wp:term_id>\n"
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

        html_body = absolutize_media(md_to_html(strip_leading_h1(body)))
        posts_xml.append(
            render_post(item, html_body, post_id, author_login,
                        post_comments, comment_base)
        )

    # Pages: two-pass so post_parent backfill can use WXR-internal IDs.
    pages = [dict(p) for p in manifest.get("pages", [])]
    page_id_by_slug: dict[str, int] = {}
    for page in pages:
        page["_post_id"] = next_post_id
        next_post_id += 1
        page_id_by_slug[page["slug"]] = page["_post_id"]

    for page in pages:
        slug = page["slug"]
        body = load_post_body(slug.split("/")[-1])
        page["post_type"] = "page"
        # Resolve parent: explicit `parent` field, or implicit "parent/child"
        # in the slug (e.g. notebooks/red -> notebooks).
        parent_slug = page.get("parent")
        if not parent_slug and "/" in slug:
            parent_slug = slug.rsplit("/", 1)[0]
        page["post_parent"] = page_id_by_slug.get(parent_slug or "", 0)
        page.setdefault("date", "2026-04-20 09:00:00")
        page["category"] = None
        html_body = absolutize_media(md_to_html(strip_leading_h1(body)))
        posts_xml.append(
            render_post(page, html_body, page["_post_id"], "admin",
                        [], next_comment_base)
        )
        next_comment_base += 1000

    # ---------- Navigation menus ----------
    menus = manifest.get("menus", []) or []

    # Classic menus: one nav_menu term + one nav_menu_item post per menu item.
    nav_term_xml: list[str] = [
        render_nav_menu_term(m["slug"], m["name"]) for m in menus
    ]
    next_post_id_ref = [next_post_id]
    flat_menu_items = _flatten_menu_items(menus, next_post_id_ref)
    next_post_id = next_post_id_ref[0]
    nav_item_xml: list[str] = [
        render_nav_menu_item(it, page_id_by_slug) for it in flat_menu_items
    ]

    # Block-theme menu: one wp_navigation per declared menu, but stagger
    # publish dates so the primary menu is always the newest. WP_Navigation_
    # Fallback picks the most recently published wp_navigation post when no
    # explicit ref is set on the Navigation block, which is the case for the
    # built-in header pattern in Twenty Twenty-Four/Five.
    nav_post_xml: list[str] = []
    base_when = datetime(2026, 4, 19, 9, 0, 0, tzinfo=timezone.utc)
    for offset, menu in enumerate(menus):
        post_id = next_post_id
        next_post_id += 1
        # Primary first in manifest -> latest date; others walk backwards in
        # time so they exist (and remain editable) but never win the fallback.
        when = base_when - timedelta(days=offset)
        if menu["slug"] == "primary-menu":
            when = base_when + timedelta(days=1)
        nav_post_xml.append(render_navigation_post(menu, post_id, when))

    # The blueprint runPHP step looks up menus and pages by slug at runtime
    # (set_theme_mod('nav_menu_locations', ...), update_option('page_on_front',
    # ...)), so we deliberately don't ship a sidecar with the import IDs - WP
    # remaps every WXR-internal ID on import anyway.

    authors_xml = "".join(
        render_author(a, user_id_by_login[a["login"]]) for a in authors
    )
    cats_xml = "".join(
        render_category(
            c["slug"], c["name"], c.get("description", ""),
            parent_slug=c.get("parent", "")
        )
        for c in manifest.get("categories", [])
    )
    tags_xml = "".join(render_tag(t) for t in manifest.get("tags", []))
    formats = sorted({
        item.get("format", "standard")
        for item in manifest.get("posts", [])
        if item.get("format", "standard") != "standard"
    })
    terms_xml = "".join(render_term_for_format(f) for f in formats)
    terms_xml += "".join(nav_term_xml)

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
        "".join(nav_post_xml),
        "".join(nav_item_xml),
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
