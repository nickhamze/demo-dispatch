# RFC: Refresh `themeunittestdata.wordpress.xml` as Demo Dispatch v2

- **Author:** Demo Dispatch maintainer
- **Date:** 2026-04-20
- **Audience:** `make.wordpress.org/themes` (theme review, accessibility,
  polyglots, meta, Playground)
- **Status:** Draft - feedback open for 30 days
- **Repo:** <https://github.com/WordPress/theme-test-data> (proposed v2/
  directory)

## TL;DR

The dataset that powers WordPress.org's theme preview button has been
substantially the same since around 2010: "Hello world!", lorem ipsum,
"John Doe" comments, and Flickr-hosted images that are fragile, dated, and
no longer sell themes the way they could. We propose a single replacement
dataset, **Demo Dispatch**, that:

- Renders cleanly in classic *and* block themes.
- Bundles all media (no remote dependencies, no CORS issues for Playground).
- Uses one consistent illustration style across the entire image corpus.
- Avoids any likeness/representation calibration by deliberately containing
  no human figures.
- Coexists with the WP default install content (`Hello world!`,
  `Sample Page`, `Uncategorized`, `admin`) without duplicating it.
- Ships with eight CI guards that enforce the constraints in perpetuity.

The dataset is one file (`themeunittestdata-v2.xml`, ~240 KB) plus ~18 MB
of bundled images and ~10 KB of bundled MP3/PDF/MP4. It imports through the
unmodified WordPress Importer, `wp-cli import`, and Playground's
`import-content` step.

## Why now

The current dataset has three structural problems that compound:

1. **It assumes classic themes.** Most blocks are absent, so block themes
   look thin under preview.
2. **It assumes no defaults.** Imports re-create `Hello world!` and
   `Sample Page` style content that the WP Importer also leaves in place,
   producing duplicates.
3. **It hotlinks remote images.** Playground previews fail under CORS;
   wp-themes.com has historically had broken image rot. (See
   [WordPress/wordpress-playground#718](https://github.com/WordPress/wordpress-playground/issues/718).)

It also reads, frankly, like a 2008 testing checklist. Themes deserve
better preview content than that.

## What Demo Dispatch is

Demo Dispatch is a fictional, self-aware publication that knows it is a
demo. Its tagline ("A sample site for previewing WordPress themes") and
its in-post leading line ("This is sample content for theme previews.")
make the meta-awareness explicit, which solves the longstanding
"is this the theme's actual content?" confusion that has dogged the
directory preview for over a decade.

Content set:

- **31 posts** across Articles, Notes, Reviews, Recipes, How-To, Audio,
  Video, and Sandbox.
- **8 pages** including About, Contact (with HTML form markup), Elements
  (typography reference), Privacy, Colophon, and a Notebooks page hierarchy
  test.
- **4 authors** with illustrated avatars served via Gravatar
  (`*@demo-dispatch.example`).
- **8 categories**, **10 tags**, **3 menus** (primary, footer, social).
- **Both classic and block widget areas populated** with Search, Recent
  Posts, Calendar, Tag Cloud, Categories, Archives, Text, Media Image,
  Nav Menu, and RSS widgets.
- **Comments coverage**: zero, one, threaded discussion (~10), and a
  53-comment paginated post; plus pingback, trackback, pending-moderation,
  emoji-only, multilingual, code snippet, long URL, and post-author reply.
- **i18n coverage**: posts in Japanese, Arabic (RTL), Hindi, Cyrillic,
  Greek, plus an emoji-titled post.
- **Edge cases**: empty title, empty body, password-protected, scheduled
  (in 2099), and a draft.

Visual identity:

- 30 hand-drawn editorial illustrations in a single locked palette of six
  colors. Each subject uses at most two of four accent colors. No human
  figures. (See `spec/art-direction.md` for the full spec.)
- Each illustration ships at 4 crops (1:1, 4:5, 16:9, 21:9) x up to 3
  widths (1200/2000/3200) x 3 formats (WebP/AVIF/JPEG), plus alt-text and
  AI-provenance sidecars.

## Constraints we worked under

We ran the plan through 13 audits against the constraints WP themes
infrastructure imposes. The non-obvious ones:

- **No companion plugin.** wp-themes.com does not allow custom plugins.
  Every job a plugin would have done is solved another way (or accepted
  as a documented trade-off; see "Known limitations" below).
- **No remote media.** Bundle is 18 MB of images, all CC0,
  AI-generated against a published prompt template (see
  `spec/art-direction.md`).
- **No likeness calibration.** Forbidding human figures sidesteps the
  representation/diversity calibration problem that ages every photo
  dataset.
- **Globally respectful.** Diverse author names, `@example.com` emails,
  no political/religious content, no dated memes.
- **Size budget**: 2 MB WXR, 25 MB total media, 400 KB single image at
  1200w WebP. Currently 240 KB / 18 MB / well under.
- **Static dating with refresh cadence.** Dates are anchored at release
  date; the dataset ships every 6 months with a date bump. We document
  the staleness window in the README.

## Known limitations

The honest list:

1. **Site title and tagline.** WXR cannot carry options. The preview will
   show whatever the install's defaults are unless the meta team sets the
   defaults at the network template level. We are asking them to.
2. **Menu-to-location auto-assignment.** Some classic themes that don't
   match menu-by-slug will show no menu in the preview until a reviewer
   manually assigns one. Block themes are unaffected. We will file a small
   theme-handbook PR recommending themes auto-assign by slug match in
   `after_switch_theme`.
3. **Dataset staleness between releases.** Posts will sometimes look up to
   six months old. This matches every other demo content product.
4. **`Hello world!` may briefly outrank the lead post.** On installs that
   publish their default post late, the WP Importer's append-only
   semantics combined with our static dating means the canonical "first
   post" sometimes appears at the top. We treat this as on-brand for the
   meta-aware Demo Dispatch voice.
5. **AI-generated illustrations.** AI-generated work has unsettled
   licensing status in some jurisdictions. We ship per-image
   `provenance.json` so reviewers can audit. License intent: CC0.

## What we need from the community

| From                         | What we need                                                                                       |
| ---------------------------- | -------------------------------------------------------------------------------------------------- |
| **Theme review team**        | Smoke-test 5 reference themes (Twenty Twenty-Five, Block Canvas, Astra, GeneratePress, OceanWP) on the staging subsite. Report any layout regressions. |
| **Accessibility team**       | Audit alt text, heading hierarchy on the Elements page, color contrast in the bundled palette, comment moderation styling, and the Cover block stress test. |
| **Polyglots**                | Translate the English masthead, tagline, and lead post titles into the top 10 locales via GlotPress. |
| **Meta team**                | See `docs/wp-themes-com-coordination.md` in the dataset repo - five concrete asks, all small.       |
| **Playground**               | Verify the WXR plus bundled media imports cleanly on a fresh Playground instance.                  |
| **License/legal**            | Sanity-check the AI-generated CC0 intent against current WP.org policy.                            |

## Migration plan

Five phases over roughly two months. Detail in
`docs/wp-themes-com-coordination.md`. Headline: v1 stays importable for one
release cycle (six months) so any theme that breaks under v2 can roll back
without intervention.

## Decision questions

We are explicitly asking the community to weigh in on:

1. **License for AI-generated images.** CC0 is our default; is that
   acceptable to the WP.org image policy?
2. **Companion plugin reconsideration.** We removed the plugin to satisfy
   the wp-themes.com constraint. If the meta team would consider a one-off
   reviewed network plugin for site-title and menu-location-assignment,
   the dataset would lose its largest known limitation. Worth discussing
   on its merits.
3. **Refresh cadence.** Six months feels right. Faster would mean more
   churn for translators; slower would mean staler dates.

Comments open. We will collate feedback, revise the dataset accordingly,
and target merge for the WordPress 6.9 cycle. Thank you for reading.
