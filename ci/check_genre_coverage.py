#!/usr/bin/env python3
"""
Genre-coverage guard.

The studio reframe (see spec/brand.md and spec/structural-matrix.md §
"Theme genre coverage") requires the dataset to flatter every common
theme genre on wp-themes.com. This guard fails CI if any required genre
has zero representative content asset (post or page).

A genre is "covered" if at least one slug in its required-set exists in
content/manifest.yaml.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_sandbox_below_fold import parse_posts  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "content" / "manifest.yaml"


def parse_pages() -> list[str]:
    """
    Walks the manifest and pulls page slugs. Mirrors the small
    PyYAML-free parser used in check_sandbox_below_fold.parse_posts.
    """
    text = MANIFEST.read_text()
    slugs: list[str] = []
    in_pages = False
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("pages:"):
            in_pages = True
            continue
        if in_pages and line.startswith("menus:"):
            in_pages = False
            break
        if not in_pages:
            continue
        if line.startswith("  - slug:"):
            slug = line.split(":", 1)[1].strip().strip("'\"")
            slugs.append(slug)
    return slugs


REQUIRED_GENRES: dict[str, dict[str, set[str]]] = {
    "blog": {
        "posts": {
            "how-a-lighthouse-works",
            "notes-on-the-color-blue",
            "why-we-still-write-postcards",
        },
    },
    "news": {
        "posts": {
            "spring-show-now-open",
            "issue-three-now-shipping",
            "closing-early-thursday",
        },
    },
    "magazine": {
        "categories": {"field-notes", "dispatch"},
    },
    "business": {
        "pages": {"studio", "about", "contact"},
    },
    "agency": {
        "pages": {"studio"},
        "posts": {"project-bell-press-rebrand"},
    },
    "portfolio": {
        "posts": {
            "project-bell-press-rebrand",
            "project-harbor-museum-wayfinding",
            "project-quarterly-cookbook",
        },
    },
    "restaurant": {
        "pages": {"menu", "visit"},
        "posts": {"lemon-cake-thursday"},
    },
    "food": {
        "posts": {
            "lemon-cake-thursday",
            "lemon-ice",
            "morning-bread-from-the-bakery-down-the-block",
        },
    },
    "shop": {
        "pages": {"shop"},
        "posts": {
            "shop-quiet-rooms-zine",
            "shop-pocket-notebook",
            "shop-harbor-print",
            "shop-house-tea-tin",
        },
    },
    "photography": {
        "posts": {
            "twelve-fountain-pens",
            "harbor-light-at-five-oclock",
            "things-found-in-a-library-window",
            "two-photographs-of-snow",
        },
    },
    "journal": {
        "categories": {"field-notes"},
        "posts": {"folding-a-paper-boat"},
    },
    "events": {
        "posts": {"workshop-letterpress-saturday", "spring-show-now-open"},
    },
    "personal": {
        "pages": {"about", "team"},
    },
    "press": {
        "pages": {"press-kit"},
        "categories": {"dispatch"},
    },
}


def main() -> int:
    posts = parse_posts()
    post_slugs = {p["slug"] for p in posts}
    page_slugs = set(parse_pages())
    categories = {p.get("category", "") for p in posts if p.get("category")}

    failures: list[str] = []
    coverage: list[tuple[str, str]] = []

    for genre, requirements in REQUIRED_GENRES.items():
        matched: list[str] = []
        for kind, names in requirements.items():
            for name in names:
                if kind == "posts" and name in post_slugs:
                    matched.append(f"posts/{name}")
                elif kind == "pages" and name in page_slugs:
                    matched.append(f"pages/{name}")
                elif kind == "categories" and name in categories:
                    matched.append(f"category/{name}")
        if not matched:
            failures.append(
                f"{genre}: no required asset present in manifest "
                f"(needed any of: {requirements})"
            )
        else:
            coverage.append((genre, ", ".join(matched[:3])))

    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1

    print(f"  OK    all {len(REQUIRED_GENRES)} theme genres have representative content")
    for genre, found in coverage:
        print(f"        {genre:13s} -> {found}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
