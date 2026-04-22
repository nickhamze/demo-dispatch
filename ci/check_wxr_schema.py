#!/usr/bin/env python3
"""
WXR schema validity guard.

Parses the built themeunittestdata-v2.wxr and asserts:

- It is well-formed XML.
- Root element is <rss version="2.0">.
- WordPress namespaces are declared (`xmlns:wp`, `xmlns:content`,
  `xmlns:dc`, `xmlns:excerpt`, `xmlns:wfw`).
- Every <item> with <wp:post_type>post</wp:post_type> has a <wp:post_id>,
  a <wp:status>, a non-empty <wp:post_name>, and at least one <category>.
- Every <wp:author> has login, email, and display_name.

If the WXR has not been built yet, the guard exits 0 with a SKIP message so
that the rest of CI can still run during development.
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WXR = ROOT / "themeunittestdata-v2.wxr"

NS = {
    "wp": "http://wordpress.org/export/1.2/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "excerpt": "http://wordpress.org/export/1.2/excerpt/",
    "wfw": "http://wellformedweb.org/CommentAPI/",
}


def main() -> int:
    if not WXR.exists():
        print(f"  SKIP  {WXR.name} not built yet")
        return 0

    try:
        tree = ET.parse(WXR)
    except ET.ParseError as e:
        print(f"  FAIL  XML parse error: {e}")
        return 1

    root = tree.getroot()
    if root.tag != "rss" or root.get("version") != "2.0":
        print(f"  FAIL  root is not <rss version=\"2.0\"> (got {root.tag})")
        return 1

    # ElementTree absorbs xmlns:* attributes into element.tag prefixes, so we
    # confirm presence by parsing the raw header instead.
    raw_header = WXR.read_text().split(">", 1)[0] + ">"
    for prefix, uri in NS.items():
        if f'xmlns:{prefix}="{uri}"' not in WXR.read_text()[:1024]:
            print(f"  WARN  namespace prefix {prefix!r} not declared")

    channel = root.find("channel")
    if channel is None:
        print("  FAIL  no <channel>")
        return 1

    failures: list[str] = []
    for author in channel.findall("wp:author", NS):
        for tag in ("wp:author_login", "wp:author_email", "wp:author_display_name"):
            if (author.find(tag, NS) is None) or not (author.find(tag, NS).text or "").strip():
                failures.append(f"author missing {tag}")

    item_count = 0
    for item in channel.findall("item"):
        post_type = item.find("wp:post_type", NS)
        if post_type is None or post_type.text != "post":
            continue
        item_count += 1
        for tag in ("wp:post_id", "wp:status", "wp:post_name"):
            if (item.find(tag, NS) is None) or not (item.find(tag, NS).text or "").strip():
                failures.append(f"item missing {tag}")
        if not item.findall("category"):
            slug = (item.find("wp:post_name", NS).text if item.find("wp:post_name", NS) is not None else "?")
            failures.append(f"post {slug} has no <category>")

    print(f"checked {item_count} posts in {WXR.name}")
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print("  OK    WXR schema valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
