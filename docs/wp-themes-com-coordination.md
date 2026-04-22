# wp-themes.com infrastructure coordination

[wp-themes.com](https://wp-themes.com) is the live preview surface that the
WordPress.org theme directory ("Preview" button) loads each theme into. It is
a multisite owned by the WordPress.org meta team. Adopting Demo Dispatch as
the preview dataset requires touching that infrastructure - this dataset
cannot ship itself.

This document is the briefing the maintainer carries into #meta and
#themereview to negotiate the rollout.

## What we are asking the meta team to do

1. **Import the Demo Dispatch WXR** (`themeunittestdata-v2.xml`) onto the
   wp-themes.com network's content template, so every newly-spawned theme
   subsite imports it instead of (or alongside) the current
   `themeunittestdata.wordpress.xml` from
   <https://github.com/WordPress/theme-test-data>.
2. **Bundle the media** under `wp-content/uploads/demo-dispatch/` once,
   network-wide. Individual theme subsites reference these by URL; this is
   the only way to satisfy the "no remote dependencies" constraint without
   duplicating media into every subsite.
3. **Set a default site title and tagline** on the network template:
   `Demo Dispatch` / `A sample site for previewing WordPress themes.` This
   is the only piece of "site setting" we cannot ship in the WXR, and it is
   the single highest-leverage change for visual quality.
4. **Configure Gravatar passthrough** so the four illustrated author avatars
   resolve in the preview environment. This is the default behavior on most
   WordPress installs; we just need to confirm it is not blocked at the
   network layer.
5. **Run the WXR through the existing import pipeline** (`wp import` or the
   meta-team-internal equivalent). No new tooling required.

## What we are *not* asking for

- We are not asking for a custom plugin. The plan was rewritten to remove
  that dependency.
- We are not asking for `posts_per_page`, permalink structure, or threaded
  comments to be customized. Defaults are fine.
- We are not asking for menu-to-location auto-assignment in the network
  config. The slugs are predictable; classic themes that don't auto-detect
  will show no menu, which we have documented as a known trade-off.

## Migration plan

| Phase | Action                                                                                                                  | Owner       | Done when                                 |
| ----- | ----------------------------------------------------------------------------------------------------------------------- | ----------- | ----------------------------------------- |
| 0     | RFC posted to `make.wordpress.org/themes` and linked from #meta and #themereview Slack channels.                        | Maintainer  | RFC URL exists and has 5 comments.        |
| 1     | Meta team imports the WXR onto a single staging theme subsite (e.g. `wp-themes.com/twentytwentyfive-staging/`).         | Meta team   | Staging URL is browsable.                 |
| 2     | Theme review team smoke-tests against five reference themes (Twenty Twenty-Five, Block Canvas, Astra, GeneratePress, OceanWP). | Theme review | All five render acceptably. |
| 3     | Switch the network template to use Demo Dispatch as the default import for newly-spawned subsites.                      | Meta team   | New subsites import v2.                   |
| 4     | Backfill: re-import v2 onto existing theme subsites in batches of 100, with rollback to v1 on the first 10 if any subsite fails import. | Meta team | All subsites on v2.                       |
| 5     | Deprecate v1: mark v1 read-only in the [theme-test-data repo](https://github.com/WordPress/theme-test-data) and update the README to point at v2. | Maintainer  | v1 README updated.                        |

## Rollback path

The meta team must keep v1 importable for at least one release cycle (six
months). If a subsite fails to render under v2 in a way that is not the
theme's fault, the meta team can re-import v1 onto that subsite without
asking. We commit to investigating any such report within seven days.

## Coordination contacts (template - fill in for the live submission)

- Meta team: `#meta` on WordPress Slack, plus `meta@wordpress.org`
  (general).
- Theme review team: `#themereview` on WordPress Slack.
- Polyglots: `#polyglots` on WordPress Slack (for GlotPress overlays).
- Playground: `#meta-playground` on WordPress Slack.

## Open infrastructure questions

These are the questions to bring into the first meta-team conversation:

1. Is there an existing automation that re-imports the WXR into every
   theme subsite, or is each subsite imported once at creation? (This
   determines whether step 4 is fast or painful.)
2. Are media files served from a shared CDN (`wp-content/uploads/`) or
   per-subsite? (This determines whether the 18 MB media bundle is shipped
   once or N times.)
3. Is there a network-level setting page where we can set the default site
   title and tagline, or do we need a one-line `wp option update` script?
4. Does the import pipeline currently run on a release cadence we can hook
   into (e.g. quarterly), or ad-hoc on PR merge?

## Risk assessment

| Risk                                                  | Likelihood | Mitigation                                        |
| ----------------------------------------------------- | ---------- | ------------------------------------------------- |
| Meta team has bandwidth concerns                      | High       | Phased rollout. v1 stays available throughout.    |
| A specific theme renders poorly under v2              | Medium     | Smoke-test five reference themes in phase 2.      |
| Media bundle exceeds wp-themes.com per-subsite quota  | Low        | Bundle is 25 MB, well under typical quotas.       |
| Translators object to "Demo Dispatch" naming          | Low        | Masthead is GlotPress-overrideable per locale.    |
| AI provenance of illustrations rejected by reviewers  | Medium     | `images/{slug}/{slug}.provenance.json` documents prompt+model+date for full audit. |

## What success looks like

A reviewer browses to <https://wp-themes.com/$theme/>, sees a marquee post
about lighthouses, three more articles below it, a populated sidebar with a
calendar and tag cloud, an author archive that has more than one post, a
search box that returns four hits for "lighthouse", and an Elements page
that exercises every block. They never see "John Doe" again.
