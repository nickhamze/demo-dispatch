# CI guards

Eight automated checks that run on every PR and on every release tag. The
dataset is the artefact; CI exists to keep that artefact honest. A failing
guard blocks merge.

| Guard                          | Script                                  | Purpose                                                                 |
| ------------------------------ | --------------------------------------- | ----------------------------------------------------------------------- |
| Classic-theme degradation      | `check_classic_degradation.py`          | Strip block comments from every post body; assert non-empty + no orphan wrappers. |
| Image budget                   | `check_image_budget.py`                 | Per-image and bundle-wide size caps.                                    |
| Alt-text presence              | `check_alt_text_presence.py`            | Every `<img>` in every post body has a non-empty `alt`.                 |
| Dead-link check                | `check_dead_links.py`                   | Every internal link resolves to a manifest entry; external links return 200. |
| WXR schema validity            | `check_wxr_schema.py`                   | The built `themeunittestdata-v2.xml` parses as RSS 2.0 with the WP namespaces. |
| Sandbox below the fold         | `check_sandbox_below_fold.py`           | First sandbox post is at index >= `posts_per_page * 2`.                 |
| Uncategorized stays empty      | `check_uncategorized_empty.py`          | No imported post is in `Uncategorized`.                                 |
| Date-buffer monotonicity       | `check_dating_monotone_buffer.py`       | Gap between newest Sandbox and oldest Filler post is >= 30 days.        |

## Wiring

GitHub Actions workflow (`.github/workflows/ci.yml`, not committed yet) runs:

```yaml
- run: python3 -m pip install -r ci/requirements.txt
- run: python3 scripts/process_images.py
- run: python3 scripts/build_media.py
- run: node scripts/build_wxr.js
- run: ci/run_all.sh
```

`ci/run_all.sh` is a thin wrapper that invokes each guard in sequence and
exits non-zero on the first failure, with grouped log output for the GitHub
Actions UI.

## Local invocation

Each guard is runnable standalone:

```bash
python3 ci/check_image_budget.py
python3 ci/check_sandbox_below_fold.py
```

The two structural guards (`sandbox-below-fold`, `dating-monotone-buffer`) can
be run before the WXR is built; they read `content/manifest.yaml` directly.

## Budgets

| Item                                | Limit       |
| ----------------------------------- | ----------- |
| Built WXR                           | <= 2 MB     |
| All bundled media                   | <= 25 MB    |
| Single image (1200w WebP)           | <= 400 KB   |
| Single image (any format/resolution)| <= 800 KB   |
| Single MP3                          | <= 5 MB     |
| Single MP4                          | <= 8 MB     |
| Single PDF                          | <= 1 MB     |
