#!/usr/bin/env python3
"""
Classic-theme degradation guard.

For every marquee post (i.e. every post not in the `sandbox` category), strip
all <!-- wp:* --> and <!-- /wp:* --> comments from the body and assert that
what remains is non-empty and contains no orphan wrapper divs that would
visually break a classic theme.

Sandbox posts are exempt by design (they exist to fail this check on purpose).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"

WP_COMMENT = re.compile(r"<!--\s*/?wp:[\w/-]+(\s+\{[^}]*\})?\s*/?-->", re.IGNORECASE)
ORPHAN_DIV = re.compile(
    r'<div\s+class="wp-block-[\w-]+"[^>]*>\s*</div>',
    re.IGNORECASE,
)
HTML_TAG = re.compile(r"<[^>]+>")


def is_sandbox(md: Path) -> bool:
    return md.parent.name == "sandbox"


def main() -> int:
    failures: list[str] = []
    for md in sorted(CONTENT.rglob("*.md")):
        if is_sandbox(md):
            continue
        text = md.read_text()
        body = text.split("---", 2)[-1] if text.startswith("---") else text
        stripped = WP_COMMENT.sub("", body)
        if ORPHAN_DIV.search(stripped):
            failures.append(f"orphan wrapper div in {md.relative_to(ROOT)}")
        text_only = HTML_TAG.sub("", stripped).strip()
        if not text_only:
            failures.append(f"empty after block-comment strip: {md.relative_to(ROOT)}")

    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print("  OK    classic-theme degradation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
