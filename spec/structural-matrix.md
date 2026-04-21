# Structural coverage matrix

Every theme feature the dataset is responsible for exercising, mapped to the
post or page that exercises it. If a row has no asset, the dataset is not
covering that feature and CI should flag it.

This document is the contract between the content manifest
(`content/manifest.yaml`), the brand spec (`spec/brand.md`), and the CI
guards (`ci/`). When a feature row is added here, a matching post or page
must exist in the manifest. When a post is removed from the manifest, its
rows here must be reassigned or this document flagged.

Legend:

- **Asset** is `posts/{slug}` or `pages/{slug}` from the manifest.
- **Why this asset** explains the test intent for theme reviewers.

---

## Theme genre coverage

The studio reframe (see `spec/brand.md`) means a single dataset must
flatter every common theme genre on `wp-themes.com`. Each genre below maps
to at least one representative asset. CI guard
`ci/check_genre_coverage.py` enforces this.

| Theme genre   | Representative asset(s)                                                                  | Why these                                                                                              |
| ------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Blog          | `posts/how-a-lighthouse-works`, `posts/notes-on-the-color-blue`, `posts/why-we-still-write-postcards` | Long-form Field Notes essays with hero, inline figures, captions, and pullquote.                       |
| News          | `posts/spring-show-now-open`, `posts/issue-three-now-shipping`, `posts/closing-early-thursday`        | Short Dispatch entries with a date-led structure and small hero, exercising news-style summary cards.  |
| Magazine      | `category/field-notes`, `category/dispatch`                                              | Multi-author archives with mixed long and short entries; magazine themes render category landing well. |
| Business      | `pages/studio`, `pages/about`, `pages/contact`, `pages/team`                             | Marketing pages assembled from the seven patterns; render as services pages in business themes.        |
| Agency        | `pages/studio`, `category/projects`, `posts/project-bell-press-rebrand`                  | Services + a portfolio archive + a flagship case study.                                                |
| Portfolio     | `category/projects`, `posts/project-bell-press-rebrand`, `posts/project-harbor-museum-wayfinding`, `posts/project-quarterly-cookbook` | Three case studies with hero, brief/approach/outcome structure, and a 4-image gallery in the third.    |
| Restaurant    | `pages/menu`, `pages/visit`, `category/kitchen`, `posts/lemon-cake-thursday`             | Menu page, visit/hours page, "what's on this week" feed, and a flagship kitchen post.                  |
| Food          | `category/kitchen`, `posts/lemon-cake-thursday`, `posts/lemon-ice`, `posts/morning-bread-from-the-bakery-down-the-block` | A coherent food category with a recipe-fragment, a sourcing note, and a "what's on" announcement.      |
| Shop          | `pages/shop`, `category/shop-shelf`, `posts/shop-quiet-rooms-zine`, `posts/shop-pocket-notebook`, `posts/shop-harbor-print`, `posts/shop-house-tea-tin` | Shop landing page + four product-shaped posts each with hero, price line, and availability line.       |
| Photography   | `posts/twelve-fountain-pens`, `posts/harbor-light-at-five-oclock`, `posts/things-found-in-a-library-window`, `posts/two-photographs-of-snow` | Gallery-format and image-format posts that lean on hero imagery with captions.                         |
| Journal       | `category/field-notes`, `posts/folding-a-paper-boat`, `posts/an-evening-on-the-pier`     | Sustained essay archive plus shorter, slower entries.                                                  |
| Events        | `posts/workshop-letterpress-saturday`, `posts/spring-show-now-open`                      | Event-shaped Dispatch posts (workshop announcement, exhibition opening). Folded into Dispatch in v1.   |
| Personal      | `pages/about`, `pages/team`, `posts/on-quiet-rooms`                                      | Quiet about-page surfaces with a strong voice.                                                         |
| Press / news  | `pages/press-kit`, `category/dispatch`                                                   | Press materials page and a recent-announcements feed.                                                  |

## Template hierarchy

| Template               | Asset                                           | Why this asset                                                                        |
| ---------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------- |
| `index.php`            | (whole blog)                                    | The blog index renders ten public-feed posts above any Sandbox content.               |
| `single.php`           | `posts/how-a-lighthouse-works`                  | The lead marquee post; sticky and longest, so it is the canonical single view.        |
| `page.php`             | `pages/about`                                   | A standard top-level page.                                                            |
| `archive.php`          | (category, tag, author, date archives)          | Studio categories all populate naturally; sandbox is reachable directly.              |
| `category.php`         | `category/field-notes`                          | The largest category archive (~10 posts).                                             |
| `tag.php`              | `tag/light`                                     | Tag archive populated by 4+ posts (`how-a-lighthouse-works`, `notes-on-the-color-blue`, `harbor-light-at-five-oclock`, `things-found-in-a-library-window`, `notes-from-a-small-observatory`, `an-evening-on-the-pier`). |
| `author.php`           | `author/mira`                                   | Mira owns the most posts (10+).                                                       |
| `date.php`             | `2026/04`                                       | The April 2026 date archive contains the lead marquee post.                           |
| `search.php`           | search for `lighthouse`                         | At least 4 posts contain the word "lighthouse" in title or body.                      |
| `404.php`              | `/no-such-url/`                                 | Any unmatched URL exercises the 404 template.                                         |
| `attachment.php`       | featured image of `how-a-lighthouse-works`      | Each featured image is a real attachment with alt text and caption.                   |
| `comments.php`         | `posts/many-comments-pagination-test`           | 53 threaded comments at WP default 5/page = 11 paginated pages.                       |
| `front-page.php`       | `pages/home`                                    | Block themes with `front-page.html` render `pages/home` as the static front page.     |
| `home.php`             | (blog index)                                    | Classic themes with `home.php` render their own layout for the posts page.            |
| `single-{format}.php`  | one post per format (see Post formats below)    | Each WP standard post format is exercised by exactly one post.                        |

## Post formats

| Format     | Asset                                                    | Notes                                                                                  |
| ---------- | -------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `standard` | `posts/how-a-lighthouse-works`                           | Default. Most posts are standard.                                                      |
| `aside`    | `posts/closing-early-thursday`                           | Two-paragraph note, no title displayed in some themes.                                 |
| `gallery`  | `posts/twelve-fountain-pens`, `posts/project-quarterly-cookbook` | Photo essays using the Gallery block.                                                  |
| `link`     | `posts/an-essay-elsewhere-worth-reading`                 | One-line link-format Dispatch entry.                                                   |
| `image`    | `posts/two-photographs-of-snow`, `posts/harbor-light-at-five-oclock`, `posts/things-found-in-a-library-window` | Image-format with caption.                                                             |
| `quote`    | `posts/on-quiet-rooms`                                   | Built around a single short pull-quote.                                                |
| `video`    | `posts/a-six-second-clip`                                | Self-hosted MP4 from `images/_media/episode-01.mp4`.                                   |
| `audio`    | `posts/episode-1-paper`                                  | Self-hosted MP3 from `images/_media/episode-01.mp3` plus chapter list.                 |
| `status`   | (none — dropped in v2)                                   | Status format collapsed into Dispatch aside; reviewers favor titled posts.             |

## Marketing patterns (the seven from spec/brand.md §3)

| Pattern        | Used by (page)                                          | Used by (post)                                       |
| -------------- | ------------------------------------------------------- | ---------------------------------------------------- |
| Hero           | `pages/home`, `pages/visit`, `pages/about`              | Each Project case study leads with a hero.           |
| Three-up grid  | `pages/home`, `pages/studio`, `pages/shop`              | n/a                                                  |
| Feature + image| `pages/visit` (hours block), `pages/team`               | `posts/project-bell-press-rebrand`                   |
| Quote callout  | `pages/about`, `pages/colophon`                         | `posts/on-quiet-rooms`                               |
| Card row       | `pages/team`, `pages/shop`, `pages/menu`                | n/a                                                  |
| CTA band       | `pages/home`, `pages/studio`, `pages/visit`             | n/a                                                  |
| Section header | every marketing page                                    | each Field Notes essay opens with one                |

## Block coverage (marquee tier — block-safe degradation)

These blocks are used in marquee posts and pages. Each has degradation
tested by CI: render through `the_content` with `<!-- wp:* -->` comments
stripped, expect non-empty output and no orphan wrapper divs.

| Block       | Asset                                                                                                  |
| ----------- | ------------------------------------------------------------------------------------------------------ |
| paragraph   | every post and page                                                                                    |
| heading     | `posts/how-a-lighthouse-works` uses h2 and h3                                                          |
| image       | `posts/notes-on-the-color-blue`, every Project case study                                              |
| quote       | `posts/on-quiet-rooms`                                                                                 |
| pullquote   | `pages/about`, several Field Notes essays                                                              |
| list        | `posts/lemon-ice` (ordered and unordered)                                                              |
| gallery     | `posts/twelve-fountain-pens`, `posts/project-quarterly-cookbook`                                       |
| embed       | `posts/a-six-second-clip` (YouTube fallback URL)                                                       |
| separator   | `posts/the-grammar-of-maps`                                                                            |
| table       | `posts/on-a-particular-teacup` (rating table), `pages/menu`                                            |
| cover       | `pages/home`, `pages/visit`, `pages/about` (always inline-colored overlay text per brand §3)           |
| columns     | `pages/home`, `pages/studio`, `pages/team`                                                             |
| group       | `pages/home`, `pages/studio`                                                                           |
| media-text  | `pages/visit`, `pages/team`                                                                            |
| buttons     | `pages/home`, `pages/visit`, `pages/studio` (always inline-colored per brand §3)                       |
| spacer      | most marketing pages                                                                                   |
| file        | `pages/press-kit` (links bundled PDF)                                                                  |

## Block coverage (sandbox tier — stress tests)

These posts intentionally use blocks that do not degrade cleanly in classic
themes. They live in the `sandbox` category and are dated 18-24 months
back, so they never appear on page 1 of the blog index.

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
| One comment                            | `posts/an-essay-elsewhere-worth-reading`         |
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
| Author archive populated    | All four authors own at least 5 public-feed posts.                 |
| Author bio displayed        | `pages/team` cards plus archive headers.                           |
| Author social URL           | Each author record carries a `social.example` URL.                 |
| Author avatar (illustrated) | Gravatar-served, 1:1 crop from the corpus (paperweight, brass-key, teacup, compass). |
| Author roles (multi-author) | Each author has a distinct studio role (editor, designer, kitchen, shopkeeper). |

## Pages and navigation

| Feature                     | Asset                                          |
| --------------------------- | ---------------------------------------------- |
| Static front page           | `pages/home` (rendered by block-theme `front-page.html`) |
| Top-level page              | `pages/about`                                  |
| Services / business page    | `pages/studio`                                 |
| Team / about-the-people     | `pages/team`                                   |
| Shop landing               | `pages/shop`                                   |
| Restaurant menu            | `pages/menu`                                   |
| Visit / contact info       | `pages/visit`                                  |
| Static contact form markup | `pages/contact`                                |
| Press kit / downloadables  | `pages/press-kit`                              |
| Typography reference page  | `pages/elements`                               |
| Published privacy policy   | `pages/privacy` (note: distinct from default WP draft `/privacy-policy/`) |
| Colophon / dataset version | `pages/colophon`                               |
| Page hierarchy (parent + 2)| `pages/notebooks`, `notebooks/red`, `notebooks/blue` |
| Default WP `Sample Page`   | (preserved from fresh install, ID 2)           |

## Menus

| Menu        | Asset             | Notes                                                            |
| ----------- | ----------------- | ---------------------------------------------------------------- |
| Primary     | `primary-menu`    | 6 top-level items; "Journal" has a 4-item submenu.               |
| Footer      | `footer-menu`     | 5 short items (Contact, Press kit, Privacy, Colophon, Elements). |
| Social      | `social-menu`     | Bluesky, Mastodon, YouTube, RSS — mapped to social-links theme support. |

## Widgets / sidebars

Both classic and block widget areas are populated. See
`content/widgets/widgets.yaml`.

| Widget              | Sidebar         | Notes                                                |
| ------------------- | --------------- | ---------------------------------------------------- |
| Search              | sidebar-1       | Default WP search widget.                            |
| Recent Posts        | sidebar-1       | Shows the 5 newest public-feed posts.                |
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
| Hero image                             | every public-feed post has a featured image    |
| Inline images                          | `posts/how-a-lighthouse-works`, every Project  |
| Gallery (2+ images, captioned)         | `posts/twelve-fountain-pens`, `posts/project-quarterly-cookbook` |
| Self-hosted video (MP4)                | `posts/a-six-second-clip`                      |
| Self-hosted audio (MP3)                | `posts/episode-1-paper`                        |
| PDF attachment                         | linked from `pages/press-kit` and `posts/episode-1-paper` |
| Image alt text on every `<img>`        | enforced by CI (`alt-text-presence`)           |
| 4 crops per illustration               | `images/{slug}/{slug}--{1x1,4x5,16x9,21x9}-*`  |
| 3 resolutions per crop                 | `1200`, `2000`, `3200` widths                  |
| 3 formats per resolution               | WebP, AVIF, JPEG                               |
| Subject corpus                         | 48 master illustrations, dual-rendered into the matrix above. |

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

- **Custom post types.** WXR can carry CPTs but no theme can rely on them
  being registered. Excluded.
- **Plugin-provided shortcodes.** Out of scope.
- **WooCommerce, BuddyPress, bbPress.** Out of scope — those are their own
  preview problems. The "Shop" surface is structural only (Shop Shelf
  posts + a Shop landing page) and does not pretend to be a real cart.
- **Static front page setting persisted via `option_value`.** WXR cannot
  set `show_on_front` or `page_on_front` reliably across importers. Block
  themes with a `front-page.html` template render `pages/home` regardless;
  classic themes show the blog index. This is acceptable.
