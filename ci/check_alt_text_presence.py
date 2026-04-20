#!/usr/bin/env python3
"""
Alt-text presence guard.

Every illustration in images/{slug}/ must ship a non-empty {slug}.alt.txt
sidecar. Every <img> in any post body markdown must have an alt attribute,
either via Markdown ![alt](src) or HTML <img alt="...">.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "images"
CONTENT = ROOT / "content"


def check_alt_sidecars() -> list[str]:
    failures: list[str] = []
    for sub in sorted(IMG.iterdir()):
        if not sub.is_dir() or sub.name.startswith("_"):
            continue
        alt = sub / f"{sub.name}.alt.txt"
        if not alt.exists():
            failures.append(f"missing alt sidecar: {alt.relative_to(ROOT)}")
            continue
        if not alt.read_text().strip():
            failures.append(f"empty alt sidecar: {alt.relative_to(ROOT)}")
    return failures


MD_IMG = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
HTML_IMG = re.compile(r"<img\b([^>]*)>", re.IGNORECASE)
ALT_ATTR = re.compile(r'\balt\s*=\s*"([^"]*)"', re.IGNORECASE)


def check_post_bodies() -> list[str]:
    failures: list[str] = []
    for md in sorted(CONTENT.rglob("*.md")):
        text = md.read_text()
        for m in MD_IMG.finditer(text):
            if not m.group(1).strip():
                failures.append(
                    f"empty alt in {md.relative_to(ROOT)}: {m.group(0)}"
                )
        for m in HTML_IMG.finditer(text):
            attrs = m.group(1)
            am = ALT_ATTR.search(attrs)
            if not am:
                failures.append(
                    f"no alt attribute in {md.relative_to(ROOT)}: <img{attrs}>"
                )
    return failures


def main() -> int:
    failures = check_alt_sidecars() + check_post_bodies()
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print("  OK    alt text present everywhere")
    return 0


if __name__ == "__main__":
    sys.exit(main())
