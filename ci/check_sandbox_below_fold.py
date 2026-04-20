#!/usr/bin/env python3
"""
Sandbox-below-fold guard.

Parses content/manifest.yaml without requiring PyYAML (the manifest is
hand-authored YAML with a small subset of features).

Asserts that, after sorting all published posts by `date` desc, the index of
the first `sandbox`-category post is at least `posts_per_page * 2` (i.e. it
falls on page 3 of the blog index or later under WP defaults).

Drafts and `future` status posts are excluded from the count because they do
not appear in the public query.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "content" / "manifest.yaml"
POSTS_PER_PAGE = 10


def parse_posts() -> list[dict]:
    text = MANIFEST.read_text()
    posts: list[dict] = []
    in_posts_block = False
    current: dict | None = None
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("posts:"):
            in_posts_block = True
            continue
        if in_posts_block and line.startswith("pages:"):
            in_posts_block = False
        if not in_posts_block:
            continue
        if re.match(r"^  - slug:\s*(.+)$", line):
            if current:
                posts.append(current)
            current = {"slug": re.match(r"^  - slug:\s*(.+)$", line).group(1).strip()}
        elif current is not None:
            m = re.match(r"^    (\w+):\s*(.+)$", line)
            if m:
                current[m.group(1)] = m.group(2).strip().strip("'\"")
    if current:
        posts.append(current)
    return posts


def main() -> int:
    posts = parse_posts()
    visible = [
        p for p in posts
        if p.get("status") not in ("draft", "future")
    ]
    visible.sort(key=lambda p: p.get("date", ""), reverse=True)

    first_sandbox_idx = next(
        (i for i, p in enumerate(visible) if p.get("category") == "sandbox"),
        None,
    )

    if first_sandbox_idx is None:
        print("  WARN  no sandbox posts found")
        return 0

    threshold = POSTS_PER_PAGE * 2
    print(
        f"first sandbox post is at index {first_sandbox_idx} "
        f"(page {first_sandbox_idx // POSTS_PER_PAGE + 1}); "
        f"threshold is index >= {threshold} (page 3+)"
    )
    if first_sandbox_idx < threshold:
        print("  FAIL  sandbox post would appear on page 1 or 2 of blog index")
        return 1
    print("  OK    sandbox below the fold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
