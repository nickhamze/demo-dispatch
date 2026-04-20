# Dating scheme

The single hardest constraint of this dataset is keeping the Sandbox posts off
the home page **without filtering the query**, because we have no companion
plugin and the WP Importer cannot set options. The mechanism is dating
discipline, locked in this document.

## Inputs

- WordPress default `posts_per_page` is **10**.
- WordPress default ordering is `post_date DESC`.
- The blog index will include the WP default `Hello world!` post (date varies
  by install). We design around it.
- The dataset's **release date floor** is the date the WXR is published. For
  v1 of Demo Dispatch this is `2026-04-20`.

## Layered date bands

```
+----------------+----------------+----------------+-----------------+
| Band           | Date range     | Count          | Visible where?  |
+----------------+----------------+----------------+-----------------+
| Lead           | release+7      | 1              | Page 1, top     |
| Marquee        | release-180    | ~9             | Page 1          |
| Filler         | -180 to -540   | ~15            | Pages 1-2       |
| Sandbox        | -540 to -730   | ~17            | Below page 2    |
| Future / draft | future / N/A   | 2              | Hidden          |
+----------------+----------------+----------------+-----------------+
```

### Lead

The single sticky lead post (`how-a-lighthouse-works`) is dated **release + 7
days** so that on installs imported within the first week it sits above
`Hello world!`. After a week, `Hello world!` may briefly outrank it on installs
that publish their default post late, which is acceptable: the meta-aware
voice ("a sample site for previewing themes") makes Hello world! reading as
the publication's earliest post on-brand.

### Marquee

Nine non-sticky Articles posts dated between **release-7d and release-180d**.
With the lead this fills page 1 of the blog index (10 posts). Spread across ~6
months at irregular intervals so date archives populate naturally.

### Filler

Fifteen Articles, Notes, Recipes, How-To, Reviews, Audio, and Video posts
dated between **release-180d and release-540d**. Carries pages 2 and 3 of the
blog index. Each category has at least 3 posts so category archives are
non-trivial.

### Sandbox buffer

Sandbox posts are dated between **release-540d and release-730d**. With ~25
visible Articles+filler posts dated more recently, the first Sandbox post is
the 26th post in date-DESC order. At 10 posts per page that is page 3 of the
blog index. Reviewers must click into `/category/sandbox/` to see them, which
is the desired behaviour.

The buffer is sized so that *removing one filler post* still keeps Sandbox off
page 1 (24 visible posts -> Sandbox starts on page 3). Two filler posts
removed -> Sandbox starts on page 3. Removing more than four filler posts
without re-balancing breaks this guarantee, and the CI guard
`sandbox-below-fold` will fail (see `ci/sandbox-below-fold.md`).

### Future / draft

Two intentionally hidden posts:

- `scheduled-future` dated `2099-01-01`, status `future`. Should not appear in
  any public query.
- `a-draft-not-yet-published`, status `draft`. Should not appear in any public
  query.

## Refresh cadence

The dataset is re-released on a **6-month cadence**. On each release:

1. The `release_date` floor in `content/manifest.yaml` is bumped to the new
   release date.
2. A migration script (`scripts/bump_dates.py`) shifts every post's date
   forward by `(new_release_date - old_release_date)` days while preserving
   the relative ordering and the irregular gaps.
3. CI re-runs the `sandbox-below-fold` guard.
4. The `Audit log` in the plan file is appended with the bump.

This is the *only* way the dataset stays roughly fresh without a companion
plugin. Posts will sometimes look up to 6 months old between releases, which
is the trade-off documented in the plan.

## Why we didn't pick alternatives

- **A static "release date" carried in the README**: doesn't help because
  `post_date` is what the query orders by.
- **Anchoring dates to the import date with a plugin filter**: the constraint
  is no plugin.
- **Sticky-flagging every Sandbox post off the index**: stickies appear *at
  the top*, the opposite of what we want.
- **Marking Sandbox posts as private**: kills the actual feature - reviewers
  need to see them, just not on the front page.

Date discipline is the only mechanism that works under WXR-only.

## CI obligations

- The CI guard `sandbox-below-fold` (see `ci/sandbox-below-fold.md`) parses
  `content/manifest.yaml`, sorts all posts by `date` desc, and asserts that
  the index of the first `category: sandbox` post is `>= posts_per_page * 2`,
  i.e. page 3 or later.
- The CI guard `dating-monotone-buffer` asserts that the gap between the
  newest Sandbox post and the oldest filler post is **>= 30 days**, so a
  single date-correction does not collapse the buffer.
