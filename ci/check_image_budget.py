#!/usr/bin/env python3
"""
Image budget guard.

Per-image cap and bundle-wide cap. Master PNGs in images/_originals/ are not
counted toward the bundle (they are reference originals, not shipped to
wp-themes.com).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "images"

PER_IMAGE_KB = 800
PER_1200_WEBP_KB = 400
BUNDLE_MEDIA_MB = 25


def main() -> int:
    failures: list[str] = []
    bundle_bytes = 0

    for path in sorted(IMG.rglob("*")):
        if not path.is_file():
            continue
        if path.parent.name in ("_originals", "_media"):
            continue
        # The {slug}--master.png file is the reference original kept beside the
        # crops for repo-local convenience; it is not bundled to wp-themes.com.
        if path.name.endswith("--master.png"):
            continue
        size_kb = path.stat().st_size / 1024
        if size_kb > PER_IMAGE_KB:
            failures.append(
                f"OVER per-image cap ({PER_IMAGE_KB} KB): {path.relative_to(ROOT)} "
                f"is {size_kb:.0f} KB"
            )
        if path.name.endswith("-1200.webp") and size_kb > PER_1200_WEBP_KB:
            failures.append(
                f"OVER 1200w WebP cap ({PER_1200_WEBP_KB} KB): "
                f"{path.relative_to(ROOT)} is {size_kb:.0f} KB"
            )
        bundle_bytes += path.stat().st_size

    bundle_mb = bundle_bytes / (1024 * 1024)
    # _media (MP3, PDF, MP4) does count toward the bundle.
    media_dir = IMG / "_media"
    if media_dir.exists():
        for path in media_dir.iterdir():
            if path.is_file():
                bundle_mb += path.stat().st_size / (1024 * 1024)
    if bundle_mb > BUNDLE_MEDIA_MB:
        failures.append(
            f"OVER bundle cap ({BUNDLE_MEDIA_MB} MB): bundle is {bundle_mb:.1f} MB"
        )

    print(f"checked {bundle_mb:.1f} MB across images/")
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print("  OK    image budget")
    return 0


if __name__ == "__main__":
    sys.exit(main())
