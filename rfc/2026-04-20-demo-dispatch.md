# RFC: Refresh `themeunittestdata.wordpress.xml` as Demo Dispatch v2

- **Author:** Demo Dispatch maintainer
- **Date:** 2026-04-20
- **Audience:** `make.wordpress.org/themes` (theme review, accessibility,
  polyglots, meta, Playground)
- **Status:** Draft — feedback open for 30 days
- **Repo:** <https://github.com/WordPress/theme-test-data> (proposed v2/
  directory)

## TL;DR

The dataset that powers WordPress.org's theme preview button has been
substantially the same since around 2010: "Hello world!", lorem ipsum,
"John Doe" comments, and Flickr-hosted images that are fragile, dated, and
no longer sell themes the way they could. We propose a single replacement
dataset, **Demo Dispatch**, that:

- Renders **amazing in block themes and dignified in classic themes** from
  the same WXR — every visually meaningful block carries both a slug
  class and an inline style so block themes can layer hover states, dark
  mode, and fluid typography on top while classic themes get a
  statically-styled fallback. (See `spec/brand.md` §3.)
- Flatters **every common theme genre on `wp-themes.com`** — blog, news,
  magazine, business, agency, portfolio, restaurant, food, shop,
  photography, journal, events, personal, and press — by reframing the
  publication as a small fictional creative studio that genuinely does
  many things. One coherent voice, every content shape.
- Bundles all media (no remote dependencies, no CORS issues for Playground).
- Uses one consistent illustration style across the entire image corpus.
- Avoids any likeness/representation calibration by deliberately containing
  no human figures.
- Coexists with the WP default install content (`Hello world!`,
  `Sample Page`, `Uncategorized`, `admin`) without duplicating it.
- Ships with nine CI guards that enforce the constraints in perpetuity,
  including a new `check_genre_coverage.py` that fails the build if any
  required theme genre has zero representative content.

The dataset is one file (`themeunittestdata-v2.xml`, ~380 KB) plus ~35 MB
of bundled images and ~10 KB of bundled MP3/PDF/MP4. It imports through
the unmodified WordPress Importer, `wp-cli import`, and Playground's
`importWxr` step.

## Why now

The current dataset has four structural problems that compound:

1. **It assumes classic themes.** Most blocks are absent, so block themes
   look thin under preview. And what blocks it does include only carry
   slug classes, so non-FSE themes get unstyled output.
2. **It assumes one theme genre.** The dataset reads as a generic blog —
   fine for blog themes, awkward for portfolio themes, useless for
   restaurant themes, embarrassing for shop themes. Theme reviewers
   currently compensate by mentally imagining how their theme *would*
   render different content.
3. **It assumes no defaults.** Imports re-create `Hello world!` and
   `Sample Page` style content that the WP Importer also leaves in place,
   producing duplicates.
4. **It hotlinks remote images.** Playground previews fail under CORS;
   wp-themes.com has historically had broken image rot. (See
   [WordPress/wordpress-playground#718](https://github.com/WordPress/wordpress-playground/issues/718).)

It also reads, frankly, like a 2008 testing checklist. Themes deserve
better preview content than that.

## What Demo Dispatch is

Demo Dispatch is a small fictional creative studio. It is **part press,
part design studio, part tiny shop, part neighborhood kitchen**. It
genuinely does many things. The site is its public face.

This single conceit is what makes the dataset both interesting and useful:

- It carries one voice and one visual identity (so themes get a coherent
  brand to render, not lorem-ipsum noise).
- It plausibly produces every content shape themes are designed around
  (so every theme genre on `wp-themes.com` finds something flattering to
  render).

The studio is **competent and self-aware**. Authors write like adults who
like their work. Voice rules are locked in `spec/brand.md` §2 — never
"Sample Post," never lorem ipsum, every title does work. The Colophon
page winks at being a demo; everything else stays in character.

### What the studio does (and what each activity produces)

| The studio does this           | Which produces this content shape                                      | Which flatters these theme genres        |
| ------------------------------ | ---------------------------------------------------------------------- | ---------------------------------------- |
| Publishes a journal            | Long-form essays (Field Notes), short journal entries (Dispatch)       | Blog, news, magazine, journal            |
| Takes on client work           | Project case studies                                                   | Portfolio, agency                        |
| Runs a small shop              | Product-shaped posts (Shop Shelf) + Shop landing page                  | Shop-adjacent themes                     |
| Serves food in the front room  | Kitchen posts + Menu page                                              | Restaurant, food                         |
| Has a team and a place         | Team page, Visit page, Studio (services) page                          | Business, agency                         |
| Produces visual work           | Photo essays, gallery posts                                            | Photography                              |
| Holds workshops & openings     | Event-shaped Dispatch posts                                            | Events (folded into Dispatch in v1)      |

### Content set

- **~30 public-feed posts** distributed across Dispatch, Field Notes,
  Projects, Shop Shelf, and Kitchen, deliberately interleaved so page 1
  of the blog index shows a representative slice of every category above
  the fold.
- **~13 sandbox posts** for theme stress tests (cover blocks, query loop,
  password protected, empty title/body, scheduled, draft, every i18n
  script, emoji title, etc.) — dated 18-24 months back so they never
  appear on page 1.
- **14 pages** including a designed Home, Studio (services), Team, Shop
  (landing), Menu (restaurant), Visit (hours/address), About, Contact,
  Press kit, Privacy, Colophon, Elements (typography reference), and a
  Notebooks parent/child hierarchy test. Marketing pages are assembled
  from the seven dual-render patterns in `spec/brand.md` §3.
- **4 authors** recast as studio roles (editor, designer, kitchen,
  shopkeeper) with distinct beats but a shared voice. Illustrated avatars
  served via Gravatar (`*@demo-dispatch.example`).
- **6 categories**, **14 tags**, **3 menus** (primary, footer, social).
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

### The dual-render design system

The dataset is engineered so the same block markup looks **amazing in
block themes** and **dignified in classic themes**. Block themes and
classic themes render the same block HTML; only the CSS on top differs.
So we engineer the markup so the same WXR carries the full ambition
without breaking the conservative context.

Every visually meaningful block in the marketing surface carries **both**:

- The **slug class** (`has-primary-color`, `has-large-font-size`) that
  block themes' `theme.json` resolves into hover states, dark mode, fluid
  typography.
- The **inline style** (`style="color:#B8533A;font-size:2.25rem"`) that
  renders the same intent statically in any theme.

Plus a strict **approved block vocabulary** (no `wp:template-part`,
`wp:post-title`, `wp:query`, etc. in post/page bodies — those are
FSE-only), and seven reusable patterns (hero, three-up grid,
feature+image, quote callout, card row, CTA band, section header).

CI guard `ci/check_classic_degradation.py` enforces the dual-style rules
mechanically.

### Visual identity

- **48 hand-drawn editorial illustrations** in a single locked palette of
  six colors. Each subject uses at most two of four accent colors. No
  human figures. (See `spec/art-direction.md` and
  `spec/subject-palette-map.md`.)
- v2 extends the v1 corpus from 30 to 48 subjects to cover the new
  content shapes (shop products, kitchen subjects, project metaphors,
  studio interior, place-at-a-distance) without breaking visual coherence
  — same prompt template, same palette, same line treatment, same paper
  background.
- Each illustration ships at 4 crops (1:1, 4:5, 16:9, 21:9) × up to 3
  widths (1200/2000/3200) × 3 formats (WebP/AVIF/JPEG), plus alt-text
  and AI-provenance sidecars.

## Constraints we worked under

We ran the plan through 13 audits against the constraints WP themes
infrastructure imposes. The non-obvious ones:

- **No companion plugin.** wp-themes.com does not allow custom plugins.
  Every job a plugin would have done is solved another way (or accepted
  as a documented trade-off; see "Known limitations" below).
- **No remote media.** Bundle is ~35 MB of images, all CC0,
  AI-generated against a published prompt template (see
  `spec/art-direction.md`).
- **No likeness calibration.** Forbidding human figures sidesteps the
  representation/diversity calibration problem that ages every photo
  dataset.
- **Globally respectful.** Diverse author names, `@example.com` emails,
  no political/religious content, no dated memes, fictional but
  unspecified neighborhood (no real addresses, no real prices).
- **Size budget**: 2 MB WXR, 40 MB total media, 400 KB single image at
  1200w WebP. Currently 380 KB / 35 MB / well under per-image cap.
- **Static dating with refresh cadence.** Dates are anchored at release
  date; the dataset ships every 6 months with a date bump. We document
  the staleness window in the README.

## Known limitations

The honest list:

1. **Site title and tagline.** WXR cannot carry options. The preview will
   show whatever the install's defaults are unless the meta team sets the
   defaults at the network template level. We are asking them to.
2. **Static front page setting.** WXR cannot reliably set
   `show_on_front=page`. Block themes with a `front-page.html` template
   render `pages/home` regardless; classic themes show the blog index. We
   accept this — both render attractively.
3. **Menu-to-location auto-assignment.** Some classic themes that don't
   match menu-by-slug will show no menu in the preview until a reviewer
   manually assigns one. Block themes are unaffected. We will file a
   small theme-handbook PR recommending themes auto-assign by slug match
   in `after_switch_theme`.
4. **Dataset staleness between releases.** Posts will sometimes look up
   to six months old. This matches every other demo content product.
5. **`Hello world!` may briefly outrank the lead post.** On installs that
   publish their default post late, the WP Importer's append-only
   semantics combined with our static dating means the canonical "first
   post" sometimes appears at the top. We treat this as on-brand for the
   self-aware Demo Dispatch voice.
6. **AI-generated illustrations.** AI-generated work has unsettled
   licensing status in some jurisdictions. We ship per-image
   `provenance.json` so reviewers can audit. License intent: CC0.
7. **The "shop" surface is structural, not transactional.** Shop Shelf
   posts and the Shop landing page exercise the *layout* every shop
   theme is built around (product card grids, hero + price + availability
   line) but the dataset does not pretend to be a real cart. Themes that
   integrate with WooCommerce specifically will still need WooCommerce
   sample data; we don't substitute for it.

## What we need from the community

| From                         | What we need                                                                                       |
| ---------------------------- | -------------------------------------------------------------------------------------------------- |
| **Theme review team**        | Smoke-test 5 representative themes spanning genres (one block-first blog, one classic news, one business, one restaurant, one portfolio) on the staging subsite. Report any layout regressions. |
| **Accessibility team**       | Audit alt text, heading hierarchy on the Elements page, color contrast in the bundled palette and on every cover-block hero, comment moderation styling, and the Cover block stress test. |
| **Polyglots**                | Translate the English masthead, tagline, and the lead post title and the seven marketing-page titles into the top 10 locales via GlotPress. |
| **Meta team**                | See `docs/wp-themes-com-coordination.md` in the dataset repo — five concrete asks, all small.       |
| **Playground**               | Verify the WXR plus bundled media imports cleanly on a fresh Playground instance.                  |
| **License/legal**            | Sanity-check the AI-generated CC0 intent against current WP.org policy.                            |

## Migration plan

Five phases over roughly two months. Detail in
`docs/wp-themes-com-coordination.md`. Headline: v1 stays importable for
one release cycle (six months) so any theme that breaks under v2 can roll
back without intervention.

## Decision questions

We are explicitly asking the community to weigh in on:

1. **License for AI-generated images.** CC0 is our default; is that
   acceptable to the WP.org image policy?
2. **Companion plugin reconsideration.** We removed the plugin to satisfy
   the wp-themes.com constraint. If the meta team would consider a
   one-off reviewed network plugin for site-title, static-front-page,
   and menu-location-assignment, the dataset would lose its three
   largest known limitations. Worth discussing on its merits.
3. **Refresh cadence.** Six months feels right. Faster would mean more
   churn for translators; slower would mean staler dates.
4. **Studio framing vs. neutral skeleton.** The first draft of this RFC
   pitched a deliberately neutral dataset; this version commits to a
   personality (the studio). The trade-off: a personality-led dataset
   makes every theme look more interesting in preview, but a small
   subset of themes whose target audience differs sharply from the
   studio's voice may feel a tonal mismatch. We believe the upside
   dominates, but the community should call it.

Comments open. We will collate feedback, revise the dataset accordingly,
and target merge for the WordPress 6.9 cycle. Thank you for reading.
