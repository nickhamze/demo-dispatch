# Structural coverage matrix

Every theme feature the dataset is responsible for exercising, mapped to the
post or page that exercises it. If a row has no asset, the dataset is not
covering that feature and CI should flag it.

This document is the contract between the content manifest
(`content/manifest.yaml`) and the CI guards (`ci/`). When a feature row is
added here, a matching post or page must exist in the manifest. When a post is
removed from the manifest, its rows here must be reassigned or this document
flagged.

Legend:

- **Asset** is `posts/{slug}` or `pages/{slug}` from the manifest.
- **Why this asset** explains the test intent for theme reviewers.

---

## Template hierarchy

| Template               | Asset                                           | Why this asset                                                                        |
| ---------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------- |
| `index.php`            | (whole blog)                                    | The blog index renders ten Articles posts above any Sandbox content.                  |
| `single.php`           | `posts/how-a-lighthouse-works`                  | The lead marquee post; sticky and longest, so it is the canonical single view.        |
| `page.php`             | `pages/about`                                   | A standard top-level page with no children.                                           |
| `archive.php`          | (category, tag, author, date archives)          | Categories `articles` and `notes` populate naturally; sandbox is reachable directly.  |
| `category.php`         | `category/articles`                             | Category archive with ~25 posts and pagination.                                       |
| `tag.php`              | `tag/light`                                     | Tag archive populated by 4+ posts (`how-a-lighthouse-works`, `notes-on-the-color-blue`, `harbor-light-at-five-oclock`, `things-found-in-a-library-window`). |
| `author.php`           | `author/tomas`                                  | Tomás owns 6+ posts.                                                                  |
| `date.php`             | `2026/04`                                       | The April 2026 date archive contains the lead marquee post.                           |
| `search.php`           | search for `lighthouse`                         | At least 4 posts contain the word "lighthouse" in title or body.                      |
| `404.php`              | `/no-such-url/`                                 | Any unmatched URL exercises the 404 template.                                         |
| `attachment.php`       | featured image of `how-a-lighthouse-works`      | Each featured image is a real attachment with alt text and caption.                   |
| `comments.php`         | `posts/many-comments-pagination-test`           | 53 threaded comments at WP default 5/page = 11 paginated pages.                       |
| `front-page.php`       | (blog index)                                    | We deliberately do not ship a static front page; block themes with `front-page.html` render that template anyway. |
| `home.php`             | (blog index)                                    | Same as above; classic themes with `home.php` render their own layout.                |
| `single-{format}.php`  | one post per format (see Post formats below)    | Each WP standard post format is exercised by exactly one post.                        |

## Post formats

| Format     | Asset                                  | Notes                                                                                  |
| ---------- | -------------------------------------- | -------------------------------------------------------------------------------------- |
| `standard` | `posts/how-a-lighthouse-works`         | Default. Most posts are standard.                                                      |
| `aside`    | `posts/an-aside-about-listening`       | Two-paragraph note, no title displayed in some themes.                                 |
| `gallery`  | `posts/twelve-fountain-pens`           | Photo essay using the Gallery block (degrades to flat figure list classically).        |
| `link`     | `posts/a-link-worth-keeping`           | One-line link-format post.                                                             |
| `image`    | `posts/two-photographs-of-snow`        | Single image with caption.                                                             |
| `quote`    | `posts/on-quiet-rooms`                 | Built around a single short pull-quote.                                                |
| `status`   | `posts/status-update-still-here`       | Twitter-length, intentionally empty title.                                             |
| `video`    | `posts/a-six-second-clip`              | Self-hosted MP4 from `images/_media/episode-01.mp4`.                                   |
| `audio`    | `posts/episode-1-paper`                | Self-hosted MP3 from `images/_media/episode-01.mp3` plus chapter list.                 |

## Block coverage (marquee tier - block-safe degradation)

These blocks are used in marquee Articles posts. Each has degradation tested by
CI: render through `the_content` with `<!-- wp:* -->` comments stripped, expect
non-empty output and no orphan wrapper divs.

| Block       | Asset                                               |
| ----------- | --------------------------------------------------- |
| paragraph   | every post                                          |
| heading     | `posts/how-a-lighthouse-works` uses h2 and h3       |
| image       | `posts/notes-on-the-color-blue`                     |
| quote       | `posts/on-quiet-rooms`                              |
| list        | `posts/lemon-ice` (ordered and unordered)           |
| gallery     | `posts/twelve-fountain-pens`                        |
| embed       | `posts/a-six-second-clip` (YouTube fallback URL)    |
| separator   | `posts/the-grammar-of-maps`                         |
| table       | `posts/on-a-particular-teacup` (rating table)       |

## Block coverage (sandbox tier - stress tests)

These posts intentionally use blocks that do not degrade cleanly in classic
themes. They live in the `sandbox` category and are dated 18-24 months back,
so they never appear on page 1 of the blog index.

| Block / feature        | Asset                                            |
| ---------------------- | ------------------------------------------------ |
| Cover                  | `posts/cover-block-stress-test`                  |
| Columns + Group nested | `posts/columns-and-groups-nested`                |
| Query Loop             | `posts/query-loop-variations`                    |
| Synced Pattern         | `posts/synced-pattern-references`                |
| Fluid typography       | `posts/fluid-typography-stress`                  |
| Long word wrap         | `posts/long-word-line-break-test`                |
| Password protected     | `posts/password-protected`                       |
| Empty title            | `posts/no-title`                                 |
| Empty body             | `posts/no-body`                                  |
| Scheduled (future)     | `posts/scheduled-future`                         |
| Draft                  | `posts/a-draft-not-yet-published`                |
| Many comments          | `posts/many-comments-pagination-test`            |

## Internationalisation

| Feature                    | Asset                          |
| -------------------------- | ------------------------------ |
| Japanese (CJK)             | `posts/japanese-script-test`   |
| Arabic (RTL)               | `posts/arabic-script-rtl-test` |
| Hindi (Devanagari)         | `posts/hindi-script-test`      |
| Russian (Cyrillic)         | `posts/cyrillic-script-test`   |
| Greek                      | `posts/greek-script-test`      |
| Emoji in title             | `posts/emoji-title`            |
| Diacritics in author name  | author `Tomás Quintero`        |

## Comments

| Comment shape                          | Asset                                            |
| -------------------------------------- | ------------------------------------------------ |
| Zero comments                          | `posts/the-grammar-of-maps`                      |
| One comment                            | `posts/a-link-worth-keeping`                     |
| Threaded discussion (~10 comments)     | `posts/how-a-lighthouse-works`                   |
| Heavy paginated comments (53)          | `posts/many-comments-pagination-test`            |
| Comment from post author               | `posts/how-a-lighthouse-works` (Tomás replies)   |
| Pending-moderation comment             | `posts/notes-on-the-color-blue`                  |
| Pingback                               | `posts/why-we-still-write-postcards`             |
| Trackback                              | `posts/the-grammar-of-maps`                      |
| Long URL inside comment body           | `posts/why-we-still-write-postcards`             |
| Emoji-only reply                       | `posts/a-six-second-clip`                        |
| Multilingual reply                     | `posts/japanese-script-test`                     |
| Code snippet inside comment            | `posts/episode-1-paper`                          |
| Anonymous default-WP "WordPress Commenter" comment | (default install, on `Hello world!`) |

## Authors and archives

| Feature                     | Asset                                                              |
| --------------------------- | ------------------------------------------------------------------ |
| Author archive populated    | All four authors own at least 5 posts.                             |
| Author bio displayed        | `pages/about` cards plus archive headers.                          |
| Author social URL           | Each author record carries a `social.example` URL.                 |
| Author avatar (illustrated) | Gravatar-served, 1:1 crop from the corpus (paperweight, brass-key, teacup, compass). |

## Pages and navigation

| Feature                     | Asset                                       |
| --------------------------- | ------------------------------------------- |
| Top-level page              | `pages/about`                               |
| Static contact form markup  | `pages/contact`                             |
| Typography reference page   | `pages/elements`                            |
| Published privacy policy    | `pages/privacy` (note: distinct from default WP draft `/privacy-policy/`) |
| Colophon / dataset version  | `pages/colophon`                            |
| Page hierarchy (parent + 2) | `pages/notebooks`, `notebooks/red`, `notebooks/blue` |
| Default WP `Sample Page`    | (preserved from fresh install, ID 2)        |

## Menus

| Menu        | Asset             | Notes                                                            |
| ----------- | ----------------- | ---------------------------------------------------------------- |
| Primary     | `primary-menu`    | 5 top-level items, one with a 2-deep submenu.                    |
| Footer      | `footer-menu`     | 3 short items (Privacy, Colophon, Elements).                     |
| Social      | `social-menu`     | Bluesky, Mastodon, YouTube, RSS - mapped to social-links theme support. |

## Widgets / sidebars

Both classic and block widget areas are populated. See
`content/widgets/widgets.yaml`.

| Widget              | Sidebar         | Notes                                                |
| ------------------- | --------------- | ---------------------------------------------------- |
| Search              | sidebar-1       | Default WP search widget.                            |
| Recent Posts        | sidebar-1       | Shows the 5 newest Articles posts.                   |
| Recent Comments     | sidebar-1       | Populated by the comments dataset.                   |
| Categories          | sidebar-1       | Hierarchical with counts.                            |
| Tag Cloud           | sidebar-1       | Populated by the tags taxonomy.                      |
| Archives            | sidebar-1       | Date archives have realistic gaps.                   |
| Calendar            | sidebar-1       | Days with posts are linked.                          |
| Text                | sidebar-2       | "About Demo Dispatch" prose.                         |
| Media Image         | sidebar-2       | The lighthouse 1:1 illustration.                     |
| Nav Menu            | sidebar-2       | Footer menu rendered as a widget.                    |
| RSS                 | sidebar-2       | Points at `https://example.com/feed/`; treated as decorative if unreachable. |

## Media coverage

| Feature                                | Asset                                          |
| -------------------------------------- | ---------------------------------------------- |
| Hero image                             | every Articles post has a featured image       |
| Inline images                          | `posts/how-a-lighthouse-works`, others         |
| Gallery (2+ images, captioned)         | `posts/twelve-fountain-pens`                   |
| Self-hosted video (MP4)                | `posts/a-six-second-clip`                      |
| Self-hosted audio (MP3)                | `posts/episode-1-paper`                        |
| PDF attachment                         | linked from `posts/episode-1-paper`            |
| Image alt text on every `<img>`        | enforced by CI (`alt-text-presence`)           |
| 4 crops per illustration               | `images/{slug}/{slug}--{1x1,4x5,16x9,21x9}-*`  |
| 3 resolutions per crop                 | `1200`, `2000`, `3200` widths                  |
| 3 formats per resolution               | WebP, AVIF, JPEG                               |

## Coexistence with default WP install content

| Default item                    | Behaviour                                          |
| ------------------------------- | -------------------------------------------------- |
| `Hello world!` post (ID 1)      | Preserved. Lead marquee dated release+7 days so it sits above. |
| `Sample Page` (ID 2)            | Preserved. We do not ship a duplicate.             |
| `Privacy Policy` page (draft)   | Preserved as draft. Our `/privacy/` page is distinct. |
| `Uncategorized` category (ID 1) | Stays empty. CI guard enforces no imported post is in `Uncategorized`. |
| `admin` user                    | Untouched.                                         |
| WordPress Commenter sample comment | Counts as the dataset's anonymous-single-comment example. |

---

## Gaps deliberately left open

The following theme features are *not* exercised by this dataset, by design:

- **Custom post types.** WXR can carry CPTs but no theme can rely on them being
  registered. Excluded.
- **Plugin-provided shortcodes.** Out of scope.
- **WooCommerce, BuddyPress, bbPress.** Out of scope - those are their own
  preview problems.
- **Static front page.** See plan: dropped because no plugin can set the option
  and most preview environments effectively show the blog index anyway.
