#!/usr/bin/env python3
"""
Demo Dispatch - image processing pipeline.

Reads master illustrations from images/_originals/, produces the deliverable
matrix specified in spec/art-direction.md:

  - 4 crops: 1:1, 4:5, 16:9, 21:9
  - 3 resolutions per crop: 1200w, 2000w, 3200w
  - 3 formats per resolution: WebP, AVIF, JPEG
  - 1 alt-text sidecar per subject
  - 1 provenance.json sidecar per subject

Output layout:

  images/{slug}/{slug}--master.png
  images/{slug}/{slug}--{crop}-{width}.{ext}
  images/{slug}/{slug}.alt.txt
  images/{slug}/{slug}.provenance.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ORIGINALS = ROOT / "images" / "_originals"
OUTPUT_ROOT = ROOT / "images"
SPEC_FILE = ROOT / "spec" / "subject-palette-map.md"
ALT_SOURCE = ROOT / "spec" / "alt-text.yaml"

CROPS = {
    "1x1": (1, 1),
    "4x5": (4, 5),
    "16x9": (16, 9),
    "21x9": (21, 9),
}
WIDTHS = (1200, 2000, 3200)
FORMATS = (
    ("webp", {"quality": 82, "method": 6}),
    ("avif", {"quality": 60}),
    ("jpg", {"quality": 85, "optimize": True, "progressive": True}),
)

PAIRS = {
    "A": "terracotta #B8533A and ocean teal #2F6F6A",
    "B": "mustard ochre #D6A24E and sage green #7A8C6F",
    "C": "terracotta #B8533A and mustard ochre #D6A24E",
    "D": "ocean teal #2F6F6A and sage green #7A8C6F",
}

PROMPT_TEMPLATE = (
    "Editorial illustration of {subject}, hand-drawn pencil contour lines in "
    "near-black ink (#1B1B1F), flat color fields filling the shapes using two "
    "colors from this palette only: {two_of}. Warm paper-textured off-white "
    "background (#F4EFE6) with subtle grain. No gradients, no shading, no "
    "people, no faces, no text, no logos. Single subject, centered, generous "
    "negative space, framed to crop cleanly at 1:1, 4:5, 16:9, and 21:9. "
    "Field-guide aesthetic. Calm and observational."
)


def parse_subject_map() -> list[dict]:
    rows: list[dict] = []
    table_re = re.compile(
        r"^\|\s*(\d+)\s*\|\s*([\w-]+)\s*\|\s*(.+?)\s*\|\s*([ABCD])\s*\|$"
    )
    for line in SPEC_FILE.read_text().splitlines():
        m = table_re.match(line)
        if not m:
            continue
        rows.append(
            {
                "index": int(m.group(1)),
                "slug": m.group(2),
                "subject": m.group(3).strip(),
                "pair": m.group(4),
            }
        )
    return rows


def load_alt_text() -> dict[str, str]:
    if not ALT_SOURCE.exists():
        return {}
    out: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    for raw in ALT_SOURCE.read_text().splitlines():
        if raw.startswith("#") or not raw.strip():
            continue
        if not raw.startswith(" "):
            if current and buf:
                out[current] = " ".join(buf).strip()
            current, _, _ = raw.partition(":")
            current = current.strip()
            buf = []
        else:
            buf.append(raw.strip())
    if current and buf:
        out[current] = " ".join(buf).strip()
    return out


def crop_to_aspect(img: Image.Image, ratio_w: int, ratio_h: int) -> Image.Image:
    w, h = img.size
    target = ratio_w / ratio_h
    actual = w / h
    if actual > target:
        new_w = int(round(h * target))
        x0 = (w - new_w) // 2
        return img.crop((x0, 0, x0 + new_w, h))
    new_h = int(round(w / target))
    y0 = (h - new_h) // 2
    return img.crop((0, y0, w, y0 + new_h))


def export(img: Image.Image, base: Path, slug: str, crop_name: str) -> list[Path]:
    written: list[Path] = []
    seen_widths: set[int] = set()
    for width in WIDTHS:
        # Don't upscale and don't emit duplicate widths. Master images smaller
        # than the largest target width naturally collapse the upper widths
        # into the source width.
        effective = min(width, img.width)
        if effective in seen_widths:
            continue
        seen_widths.add(effective)
        ratio = effective / img.width
        height = int(round(img.height * ratio))
        if effective == img.width:
            sized = img
        else:
            sized = img.resize((effective, height), Image.LANCZOS)
        for ext, opts in FORMATS:
            out = base / f"{slug}--{crop_name}-{effective}.{ext}"
            params = dict(opts)
            if ext == "jpg":
                rgb = sized.convert("RGB")
                rgb.save(out, "JPEG", **params)
            elif ext == "webp":
                sized.save(out, "WEBP", **params)
            elif ext == "avif":
                try:
                    sized.save(out, "AVIF", **params)
                except (OSError, ValueError) as e:
                    print(f"  AVIF skipped for {out.name}: {e}", file=sys.stderr)
                    continue
            written.append(out)
    return written


def process_subject(row: dict, alt_map: dict[str, str], dry_run: bool) -> None:
    slug = row["slug"]
    src = ORIGINALS / f"{row['index']:02d}-{slug}--master.png"
    if not src.exists():
        print(f"!! missing master: {src.name}", file=sys.stderr)
        return

    out_dir = OUTPUT_ROOT / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    master_dest = out_dir / f"{slug}--master.png"
    if not dry_run:
        master_dest.write_bytes(src.read_bytes())

    print(f"-> {slug} ({row['subject']})")

    if dry_run:
        return

    with Image.open(src) as im:
        im.load()
        for crop_name, (rw, rh) in CROPS.items():
            cropped = crop_to_aspect(im, rw, rh)
            export(cropped, out_dir, slug, crop_name)

    alt_text = alt_map.get(
        slug,
        f"Illustration of {row['subject']}.",
    )
    (out_dir / f"{slug}.alt.txt").write_text(alt_text + "\n")

    provenance = {
        "slug": slug,
        "subject": row["subject"],
        "pair": row["pair"],
        "prompt": PROMPT_TEMPLATE.format(
            subject=row["subject"], two_of=PAIRS[row["pair"]]
        ),
        "model": "cursor.image (gpt-image-1 backed)",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "accepted_by": "demo-dispatch-maintainer",
        "accepted_at": datetime.now(timezone.utc).isoformat(),
        "license": "CC0-1.0",
    }
    (out_dir / f"{slug}.provenance.json").write_text(
        json.dumps(provenance, indent=2) + "\n"
    )


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--only", help="Process a single slug only.")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    rows = parse_subject_map()
    alt_map = load_alt_text()
    if args.only:
        rows = [r for r in rows if r["slug"] == args.only]
        if not rows:
            print(f"slug not found: {args.only}", file=sys.stderr)
            return 1

    for row in rows:
        process_subject(row, alt_map, args.dry_run)

    return 0


if __name__ == "__main__":
    sys.exit(main())
