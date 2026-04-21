#!/usr/bin/env python3
"""
Uncategorized-empty guard.

Every imported post must have an explicit category from the dataset's own
taxonomy. None should fall back to the WP default `Uncategorized` category.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_sandbox_below_fold import parse_posts  # noqa: E402

ALLOWED = {
    "dispatch", "field-notes", "projects",
    "shop-shelf", "kitchen", "sandbox",
}


def main() -> int:
    posts = parse_posts()
    failures: list[str] = []
    for p in posts:
        cat = p.get("category", "")
        if not cat:
            failures.append(f"{p['slug']} has no category")
        elif cat not in ALLOWED:
            failures.append(f"{p['slug']} has unknown category {cat!r}")

    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print(f"  OK    all {len(posts)} posts categorized inside dataset taxonomy")
    return 0


if __name__ == "__main__":
    sys.exit(main())
