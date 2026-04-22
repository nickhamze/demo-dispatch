# Demo Dispatch - WordPress theme preview dataset (v2)

A single, universal demo dataset to replace
`themeunittestdata.wordpress.xml` for the WordPress.org theme directory's
preview button, `wp-themes.com`, `wp-env`, Playground Blueprints, and theme
reviewers' local environments.

> "A sample site for previewing WordPress themes."

## What this is

- **One WXR file** (`themeunittestdata-v2.wxr`, ~240 KB) imported through
  the standard WordPress Importer, `wp-cli import`, or Playground
  `import-content`. No new tooling required.
- **One illustration corpus** (`images/`) of 30 hand-drawn editorial
  illustrations in a single locked palette of six colors, each delivered
  at 4 crops x up to 3 widths x 3 formats, with alt text and AI-provenance
  sidecars.
- **One bundled MP3, PDF, and (optional) MP4** in `images/_media/` to
  exercise self-hosted audio, downloadable attachments, and
  self-hosted video.

## What it covers

Every theme template, every standard post format, every default block
that degrades cleanly in classic themes, plus a quarantined Sandbox
category for stress tests. Full coverage matrix in
`spec/structural-matrix.md`.

## Building

```bash
# Resize and re-encode every master illustration into the deliverable matrix.
python3 scripts/process_images.py

# Build the bundled MP3, PDF, and (if ffmpeg is available) MP4.
python3 scripts/build_media.py

# Assemble themeunittestdata-v2.wxr from the manifest, content, comments,
# and authors.
python3 scripts/build_wxr.py

# Run all eight CI guards.
bash ci/run_all.sh
```

Dependencies: `Pillow` (image processing), `reportlab` (PDF generation),
`PyYAML` (manifest parsing), and optionally `ffmpeg` for the MP4 sample.

## Layout

```
content/
  manifest.yaml              authoritative list of posts, pages, categories, tags, menus
  authors/                   the four fictional authors
  articles/                  marquee post bodies (block-safe)
  sandbox/                   stress-test post bodies (any block)
  pages/                     static pages including Elements (typography reference)
  comments/                  comment data per post
  widgets/                   classic and block widget areas
images/
  _originals/                master PNG sources (not bundled)
  {slug}/                    deliverable crops, alt.txt, provenance.json
  _media/                    MP3 / PDF / (MP4)
spec/
  art-direction.md           visual identity spec (palette, prompt, acceptance)
  subject-palette-map.md     30 subjects x 4 accent pairings
  alt-text.yaml              alt sentence per illustration
  structural-matrix.md       feature -> asset coverage matrix
  dating-scheme.md           how Sandbox stays below the fold without a plugin
ci/                          eight guard scripts; run_all.sh wraps them
scripts/                     image, media, and WXR builders
docs/
  gravatar-runbook.md        one-time author-avatar provisioning
  wp-themes-com-coordination.md   what the meta team needs to do
rfc/
  2026-04-20-demo-dispatch.md     the public RFC draft
blueprint/blueprint.json     one-click Playground import
themeunittestdata-v2.wxr     the built artefact (regenerate with build_wxr.py)
```

## Constraints

- Renders acceptably in classic themes; beautifully in block themes.
- No companion plugin (wp-themes.com policy).
- All media bundled (no remote dependencies, no CORS).
- No human figures in any illustration.
- WXR ≤ 2 MB; bundled media ≤ 25 MB; single image ≤ 800 KB; 1200w WebP
  ≤ 400 KB.
- Coexists with WP defaults (`Hello world!`, `Sample Page`,
  `Uncategorized`, `admin`, the WordPress Commenter sample comment); does
  not duplicate any of them.

See `spec/` for the locked design and `rfc/` for the RFC.
