# Demo Dispatch - Art Direction Spec

Version: 1.0.0
Status: Locked
Last reviewed: 2026-04-20

This document is the single source of truth for every illustration that ships
with the Demo Dispatch dataset. Any image that does not pass the checks at the
bottom of this file is not allowed in `images/`.

## 1. Medium

Editorial illustration. Flat color fields filled inside hand-drawn ink contour
lines. Subtle paper-grain texture overlaid at low opacity. The corpus should
read as if a single illustrator working in a small notebook produced it.

What the medium is **not**:

- Not photography or photorealistic rendering.
- Not 3D rendering, isometric vector illustration, or "tech-y" gradient
  illustration.
- Not heavy-shaded painting. No gradients inside shapes.
- Not cartoon, manga, anime, comic, or chibi style.

## 2. Subject rules

Allowed subject categories:

- Objects (typewriter, fountain pen, paperweight, brass key, lantern, kettle,
  teacup, ink bottle, telescope).
- Plants and natural materials (fern, snowdrop, fig, lemon, pinecone, river
  stones).
- Architecture and place at a distance (lighthouse, harbor, observatory,
  library window, café table).
- Vehicles in landscape (sailboat, train, bicycle, kite, paper boat).
- Tools of orientation (compass, map, weather vane).

**Forbidden in every image:**

- No human faces, bodies, hands, silhouettes, or implied figures.
- No text, lettering, numerals, or logos rendered into the illustration.
- No brand-identifying marks (no real-world product names, no flags).
- No animals with humanoid expressions.
- No religious symbols.

## 3. Composition

- Single subject, centered or rule-of-thirds.
- Generous negative space around the subject (at least 20 percent of the frame
  on each side at the master crop).
- Subject framed so the same image crops cleanly to 1:1, 4:5, 16:9, and 21:9
  without losing the recognizable silhouette.
- Mood: calm, observational, slightly nostalgic. Field-guide rather than
  marketing.

## 4. Palette (locked, six colors)

| Role            | Hex       | Name             |
| --------------- | --------- | ---------------- |
| Background      | `#F4EFE6` | Paper warm white |
| Linework        | `#1B1B1F` | Ink near-black   |
| Accent 1        | `#B8533A` | Terracotta       |
| Accent 2        | `#2F6F6A` | Ocean teal       |
| Accent 3        | `#D6A24E` | Mustard ochre    |
| Accent 4        | `#7A8C6F` | Sage green       |

Rules:

- Every illustration uses **exactly** the paper background plus the ink
  linework plus **at most two** accent colors.
- No image uses three or four accents.
- No additional colors are introduced (no white, no pure black, no other
  greys).

## 5. Linework

- Hand-drawn pencil-like contour line in `#1B1B1F`.
- Effective line weight 1.5pt at 2000px wide; scales proportionally at other
  resolutions.
- Lines have natural taper variation (not uniform vector strokes).
- No outline halo, no double-stroke, no glow.

## 6. Generation prompt template

A single template, slot-filled per subject. Slots: `{subject}` and
`{two-of}` (the two-color accent pairing for that image, drawn from the
subject-to-palette map below).

```text
Editorial illustration of {subject}, hand-drawn pencil contour lines in
near-black ink (#1B1B1F), flat color fields filling the shapes using two
colors from this palette only: {two-of}. Warm paper-textured off-white
background (#F4EFE6) with subtle grain. No gradients, no shading, no people,
no faces, no text, no logos. Single subject, centered, generous negative
space, framed to crop cleanly at 1:1, 4:5, 16:9, and 21:9. Field-guide
aesthetic. Calm and observational.
```

`{two-of}` is always one of the four pairs:

- `terracotta #B8533A and ocean teal #2F6F6A`
- `mustard ochre #D6A24E and sage green #7A8C6F`
- `terracotta #B8533A and mustard ochre #D6A24E`
- `ocean teal #2F6F6A and sage green #7A8C6F`

The pairings are distributed evenly across the corpus so no two adjacent
illustrations in any post share the same accents. See
[subject-palette-map.md](subject-palette-map.md).

## 7. Deliverables per illustration

Each subject is rendered once at the master resolution (3200px on the long
side), then cropped (not regenerated) to four aspect ratios. Each crop is
exported at three resolutions and three formats.

- Crops: 1:1, 4:5 (portrait), 16:9 (landscape), 21:9 (banner).
- Resolutions per crop: 1200w, 2000w, 3200w.
- Formats per resolution: WebP (primary), AVIF (modern), JPEG (fallback).

Naming convention (under `images/`):

```
images/
  {slug}/
    {slug}--master.png
    {slug}--1x1-1200.webp
    {slug}--1x1-1200.avif
    {slug}--1x1-1200.jpg
    {slug}--1x1-2000.webp
    ... (one file per crop x resolution x format)
    {slug}.alt.txt
```

`{slug}.alt.txt` carries one to two factual sentences describing the image,
used as the WordPress `_wp_attachment_image_alt` value at import time.

## 8. Acceptance checks

A generated illustration is accepted only if all of the following hold:

1. Background colour is visually `#F4EFE6` paper warm white.
2. Linework reads as near-black hand-drawn contour, not vector or marker.
3. The image uses exactly the paper, the ink, and at most two of the four
   accent colours, matching the pairing assigned for that subject.
4. No human faces, bodies, hands, text, numerals, or logos are visible.
5. The subject silhouette is recognisable when cropped to 1:1, 4:5, 16:9,
   and 21:9.
6. The mood is calm and observational, not glossy or marketing-coded.

If any check fails, the image is regenerated against the same prompt slot
fill until it passes. The repo only ever contains accepted images.

## 9. Provenance

Each image ships a sidecar `{slug}.provenance.json` recording:

- `prompt`: the exact slot-filled prompt used.
- `model`: the generation model identifier.
- `generated_at`: ISO 8601 timestamp.
- `accepted_by`: the human reviewer's handle.
- `accepted_at`: ISO 8601 timestamp.

This is what reviewers asking "is this AI-generated?" can audit.
