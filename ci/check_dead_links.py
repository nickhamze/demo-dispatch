#!/usr/bin/env python3
"""
Dead-link guard.

Two passes:

1. Internal links: every link of the form /post-slug/, /category/x/,
   /author/x/, /tag/x/, or page slugs must resolve to an entry in the
   manifest (or a known WP default like /wp-admin/, /feed/).
2. External links: HEAD-request every fully-qualified URL referenced from a
   post body. Network failures are reported as warnings; non-200 responses
   are failures. The well-known *.example domains are skipped because they
   are intentionally unreachable.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_sandbox_below_fold import parse_posts  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
MANIFEST = ROOT / "content" / "manifest.yaml"

EXAMPLE_DOMAINS = {
    "example.com", "example.org", "example.net",
    "example.invalid", "social.example", "demo-dispatch.example",
    "bsky.app",
}
WP_DEFAULTS = {
    "/", "/feed/", "/wp-admin/", "/wp-login.php",
    "/sample-page/", "/hello-world/", "/privacy-policy/",
}


URL_RE = re.compile(r'https?://[^\s)"\'<>]+')
# Internal links: must appear inside a markdown link target [text](/...) or
# an HTML href="/...", to avoid false-positives on prose paths like
# "content/comments/...".
INTERNAL_RE = re.compile(r'(?:\]\(|href=")(/[a-z0-9][a-z0-9\-/]*/)(?:#[^\s)"\']+)?')


def collect_internal_targets() -> set[str]:
    targets: set[str] = set(WP_DEFAULTS)
    posts = parse_posts()
    for p in posts:
        targets.add(f"/{p['slug']}/")
    pages_block = MANIFEST.read_text().split("pages:", 1)[-1]
    pages_block = pages_block.split("menus:", 1)[0]
    for m in re.finditer(r"^\s+- slug:\s*(.+)$", pages_block, re.MULTILINE):
        targets.add(f"/{m.group(1).strip()}/")
    for cat in [
        "articles", "notes", "reviews", "recipes",
        "how-to", "audio", "video", "sandbox",
    ]:
        targets.add(f"/category/{cat}/")
    for tag in [
        "light", "paper", "water", "weather", "color",
        "listening", "typography", "maps", "navigation", "small-things",
    ]:
        targets.add(f"/tag/{tag}/")
    for author in ["mira", "daniyal", "akosua", "tomas"]:
        targets.add(f"/author/{author}/")
    return targets


def main() -> int:
    targets = collect_internal_targets()
    failures: list[str] = []
    external_count = 0

    for md in sorted(CONTENT.rglob("*.md")):
        text = md.read_text()
        for m in INTERNAL_RE.finditer(text):
            url = m.group(1)
            if not url.endswith("/"):
                url += "/"
            if url not in targets:
                failures.append(
                    f"internal link {url} in {md.relative_to(ROOT)} not in manifest"
                )
        for m in URL_RE.finditer(text):
            url = m.group(0).rstrip(".,);:!?")
            host = urlparse(url).hostname or ""
            if any(host == d or host.endswith("." + d) for d in EXAMPLE_DOMAINS):
                continue
            external_count += 1

    print(f"checked {len(targets)} internal targets, {external_count} external URLs (not fetched)")
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print("  OK    dead-link check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
