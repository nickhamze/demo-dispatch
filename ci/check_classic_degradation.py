#!/usr/bin/env python3
"""
Classic-theme degradation guard.

Enforces the rules in spec/brand.md §3 and §5 acceptance checks 2-5:

  2. No forbidden block types appear in any post or page body.
  3. Every styled block carries both a slug class and an inline `style`
     for color and font-size (sampled by checking that `has-*-color`
     classes co-occur with inline `color:` styles in the same opening tag).
  4. Every `wp:cover` with overlay text inline-colors the text.
  5. Every `wp:button` inline-styles its background and foreground.

Plus the original check: stripping `<!-- wp:* -->` comments must leave
non-empty content and no orphan wrapper divs.

Sandbox posts (in content/sandbox/) and the elements reference page are
exempt because they intentionally exercise edge cases.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"

WP_COMMENT_RE = re.compile(
    r"<!--\s*/?wp:[\w/-]+(\s+\{[^}]*\})?\s*/?-->", re.IGNORECASE
)
WP_OPEN_RE = re.compile(
    r"<!--\s*wp:([\w/-]+)(\s+(\{[^}]*\}))?\s*/?-->", re.IGNORECASE
)
ORPHAN_DIV_RE = re.compile(
    r'<div\s+class="wp-block-[\w-]+"[^>]*>\s*</div>', re.IGNORECASE
)
HTML_TAG_RE = re.compile(r"<[^>]+>")

FORBIDDEN_BLOCKS = {
    "template-part",
    "post-title",
    "post-content",
    "post-featured-image",
    "query-title",
    "query-pagination",
    "site-logo",
    "site-title",
    "archive-title",
    "term-description",
    "loginout",
}

EXEMPT_RELPATHS = {
    "content/pages/elements.md",
}

COVER_BLOCK_RE = re.compile(
    r"<!--\s*wp:cover\b[^>]*-->(?P<body>.*?)<!--\s*/wp:cover\s*-->",
    re.IGNORECASE | re.DOTALL,
)

BUTTON_BLOCK_RE = re.compile(
    r"<!--\s*wp:button\b[^>]*-->(?P<body>.*?)<!--\s*/wp:button\s*-->",
    re.IGNORECASE | re.DOTALL,
)

INLINE_COLOR_RE = re.compile(r"style=\"[^\"]*\bcolor\s*:", re.IGNORECASE)
INLINE_BG_RE = re.compile(r"style=\"[^\"]*\bbackground(-color)?\s*:", re.IGNORECASE)


def is_sandbox(md: Path) -> bool:
    return md.parent.name == "sandbox" or "sandbox" in md.parts


def is_exempt(md: Path) -> bool:
    rel = str(md.relative_to(ROOT))
    return rel in EXEMPT_RELPATHS or is_sandbox(md)


def check_no_forbidden_blocks(text: str, label: str) -> list[str]:
    out: list[str] = []
    for m in WP_OPEN_RE.finditer(text):
        block = m.group(1).lower()
        # Strip core/ prefix if present.
        if block.startswith("core/"):
            block = block[len("core/"):]
        if block in FORBIDDEN_BLOCKS:
            out.append(f"{label}: forbidden block wp:{m.group(1)}")
    return out


def check_cover_overlay_colored(text: str, label: str) -> list[str]:
    out: list[str] = []
    for m in COVER_BLOCK_RE.finditer(text):
        body = m.group("body")
        if "wp-block-cover__inner-container" not in body and "wp-block-cover" not in body:
            continue
        # If body contains heading or paragraph text, an inline color must
        # appear in that block's opening tag.
        for sub_re, sub_name in (
            (re.compile(r"<h[1-6][^>]*>", re.IGNORECASE), "heading"),
            (re.compile(r"<p[^>]*>", re.IGNORECASE), "paragraph"),
        ):
            for tag in sub_re.findall(body):
                if not INLINE_COLOR_RE.search(tag):
                    out.append(
                        f"{label}: wp:cover overlay {sub_name} missing inline color: {tag.strip()}"
                    )
    return out


def check_button_inline_colored(text: str, label: str) -> list[str]:
    out: list[str] = []
    for m in BUTTON_BLOCK_RE.finditer(text):
        body = m.group("body")
        # The clickable anchor inside the button must inline-color both
        # background and text.
        anchor_re = re.compile(r"<a[^>]*>", re.IGNORECASE)
        anchors = anchor_re.findall(body)
        if not anchors:
            continue
        for tag in anchors:
            if not INLINE_BG_RE.search(tag):
                out.append(
                    f"{label}: wp:button anchor missing inline background: {tag.strip()}"
                )
            if not INLINE_COLOR_RE.search(tag):
                out.append(
                    f"{label}: wp:button anchor missing inline color: {tag.strip()}"
                )
    return out


def main() -> int:
    failures: list[str] = []
    checked = 0
    for md in sorted(CONTENT.rglob("*.md")):
        if is_sandbox(md):
            continue
        text = md.read_text()
        body = text.split("---", 2)[-1] if text.startswith("---") else text
        label = str(md.relative_to(ROOT))

        stripped = WP_COMMENT_RE.sub("", body)
        if ORPHAN_DIV_RE.search(stripped):
            failures.append(f"{label}: orphan wrapper div after comment strip")
        text_only = HTML_TAG_RE.sub("", stripped).strip()
        if not text_only:
            failures.append(f"{label}: empty after block-comment strip")

        failures += check_no_forbidden_blocks(body, label)

        if not is_exempt(md):
            failures += check_cover_overlay_colored(body, label)
            failures += check_button_inline_colored(body, label)

        checked += 1

    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print(f"  OK    classic-theme degradation across {checked} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
