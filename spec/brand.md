# Demo Dispatch — Brand Spec

Version: 2.0.0
Status: Locked
Last reviewed: 2026-04-20

This document is the single source of truth for **what Demo Dispatch is** and
**how its content sounds, looks, and behaves across rendering contexts**. Any
content authored for the dataset that does not pass the rules in this file is
not allowed in `content/`.

If `art-direction.md` governs how images look, this file governs everything
else: who the studio is, who writes for it, how copy reads, and which block
markup is allowed.

---

## 1. The conceit

**Demo Dispatch is a small fictional creative studio.** It is part press,
part design studio, part tiny shop, part neighborhood kitchen. It genuinely
does many things. The site is its public face.

This single conceit is what makes the dataset both interesting and useful:

- It carries one voice and one visual identity (so themes get a coherent
  brand to render, not lorem-ipsum noise).
- It plausibly produces every content shape themes are designed around (so
  every theme genre on `wp-themes.com` finds something flattering to render).

The studio is **competent and self-aware**. They write like adults who like
their work. Think small-town letterpress shop crossed with a design studio
that also makes lemon cake on Thursdays.

### Identity

| Field             | Value                                                |
| ----------------- | ---------------------------------------------------- |
| Name              | Demo Dispatch                                        |
| Tagline           | A studio, a press, and a small kitchen.              |
| Founded           | 2019 (fictional)                                     |
| Where             | A fictional neighborhood, deliberately unnamed.      |
| What they do      | Publish a journal, take on design and editorial projects, run a small shop, serve a short menu in the front room. |
| Who they are      | Four named studio members (see authors).             |

### Things the studio does (and the content shapes they produce)

| The studio does this    | Which produces this content shape                       | Which flatters these theme genres        |
| ----------------------- | ------------------------------------------------------- | ---------------------------------------- |
| Publishes a journal     | Long-form essays (Field Notes), short journal entries (Dispatch) | Blog, news, magazine, journal            |
| Takes on client work    | Project case studies                                    | Portfolio, agency                        |
| Runs a small shop       | Product-shaped posts (Shop Shelf), Shop index page      | Shop-adjacent themes                     |
| Serves food in the front room | Kitchen posts, Menu page                          | Restaurant, food                         |
| Has a team and a place  | Team page, Visit page, Studio (services) page           | Business, agency                         |
| Produces visual work    | Photo essays, gallery posts                             | Photography                              |
| Holds workshops & openings | Event-shaped Dispatch posts                          | Events (folded into Dispatch for v1)     |

---

## 2. Voice and content rules

### Voice rules (the "stays fun" guardrails)

1. **Every title does work.** Never "Sample Post," never "About Page." Titles
   are specific, evocative, and descriptive of the actual thing.
2. **One voice across content shapes.** A case study, a menu item, a long
   essay, and a product description all sound like the same studio wrote them.
   Warm, specific, curious, dry where it helps.
3. **Specific beats abstract.** "Three short paragraphs about the lemon cake
   we made on Thursday" beats "Lorem ipsum dolor sit amet."
4. **No twee, no precious.** The studio is competent, not whimsical-for-its-
   own-sake. No "wee" or "lovely" or "magical" without earning it.
5. **Self-aware where it helps.** The Colophon and Press kit pages can wink
   at the fact this is a demo, briefly. Other pages stay in character.
6. **Real-feeling but unmistakably fictional.** No real addresses. No real
   product prices a reader could mistake for an actual storefront. Plausible
   currency formats, plausible-but-fictional details.
7. **No filler.** Every sentence either advances the meaning, sets the tone,
   or carries a specific image. Cut the rest.
8. **Short sentences when they earn it. Long ones when they earn it.**
   Vary rhythm. Avoid monotony.
9. **Plain English over jargon.** No "leveraging synergies." If a real word
   exists, use it.
10. **Inclusive by default.** No assumed gender, no assumed nationality, no
    assumed wealth. The studio reads as a place that anyone could walk into.

### Voice patterns to use

- Concrete sensory detail (light, weather, the sound of a kettle).
- Brief asides in dashes — like this — when they sharpen a sentence.
- Lists when a real list exists. Prose when prose is doing more work.
- One-sentence opens that orient the reader fast.

### Voice patterns to avoid

- Lorem ipsum, "sample text," "your text here."
- Pseudo-Latin, mock-French, decorative typography in copy.
- Sentences that exist only to demonstrate a feature ("This is an
  italic word.").
- Self-congratulation. The studio doesn't tell you it's good; the work does.
- Excessive em-dashes, ellipses, exclamation marks.

### Content rules per shape

- **Field Notes (long essay):** 1200–1800 words. One hero image, 1–3 inline
  figures with captions, optional pullquote.
- **Dispatch (journal entry / news):** 150–500 words. One hero image
  optional. May lead with a date or location.
- **Projects (case study):** 600–1000 words structured as
  `Client / Brief / Approach / Outcome`. One hero image, one gallery of
  3–6 images.
- **Shop Shelf (product post):** 200–400 words. Title, hero image, short
  description, "What's in it" list, plain-text price line, "Limited / In
  stock / Reprinting" availability line.
- **Kitchen (food post):** 200–500 words. Hero image. May embed a recipe
  fragment but isn't itself a recipe page.
- **Sandbox (stress test):** existing rules apply unchanged.

---

## 3. The dual-render design system

The dataset must look **amazing in block themes** and **dignified in classic
themes**. Block themes and classic themes render the same block HTML; the
only difference is what CSS sits on top. So we engineer the markup so the
same WXR can carry the full ambition without breaking the conservative
context.

### Core technique: every block carries its own paint

WordPress generates two kinds of styling for every styled block:

- **Slug classes** like `has-primary-color`, `has-large-font-size` — only
  resolve in themes whose `theme.json` defines those slugs.
- **Inline styles** like `style="color:#B8533A;font-size:2.25rem"` — applied
  directly, work everywhere.

Most demo content uses one or the other. **Demo Dispatch uses both,
deliberately, on every block that matters visually.**

Example — a hero headline:

```html
<!-- wp:heading {
  "level":1,
  "textColor":"ink",
  "fontSize":"display",
  "style":{
    "color":{"text":"#1B1B1F"},
    "typography":{"fontSize":"3.5rem","lineHeight":"1.05"}
  }
} -->
<h1 class="wp-block-heading has-ink-color has-text-color has-display-font-size"
    style="color:#1B1B1F;font-size:3.5rem;line-height:1.05">
  A studio, a press, and a small kitchen.
</h1>
<!-- /wp:heading -->
```

In a block theme that defines `ink` and `display` in `theme.json`: slug
classes resolve, the theme can layer hover states, dark-mode overrides,
fluid typography. In a classic theme: inline styles render the same intent,
just statically. **Same markup, two ceiling heights.**

### Layout: progressive bleed, never broken

`alignwide` and `alignfull` are progressive by design — they only activate
in themes that opt in. So we author "full-bleed in block themes, content-
width in classic themes" with no extra work:

- `wp:cover {"align":"full"}` — full-bleed hero in block themes; constrained
  but still a hero in classic.
- `wp:group {"align":"wide"}` — wide section in block themes; normal section
  in classic.
- `wp:columns` — flex grid in both; collapses to stacked on narrow viewports
  the same way in both.

The content never breaks. It just gets less ambitious.

### Approved block vocabulary

Three buckets. Locked.

**Use freely** — render well in both contexts:

`wp:group`, `wp:columns`/`wp:column`, `wp:cover`, `wp:media-text`,
`wp:image`, `wp:gallery`, `wp:heading`, `wp:paragraph`, `wp:buttons`/
`wp:button`, `wp:quote`, `wp:pullquote`, `wp:list`, `wp:separator`,
`wp:spacer`, `wp:table`, `wp:embed`, `wp:audio`, `wp:video`, `wp:file`,
`wp:code`, `wp:preformatted`.

**Use with inline styling discipline** — degrade visibly without it:

- `wp:cover` overlay text — **always** inline-color the headline so it reads
  against the background image.
- `wp:button` — **always** inline `backgroundColor` and `color` so the
  button is recognizable when palette slugs don't resolve.
- Any heading meant to read against a colored background — **always** inline
  color it.

**Forbidden in post and page bodies** — FSE-only, render wrong or empty in
classic themes:

`wp:template-part`, `wp:post-title`, `wp:post-content`,
`wp:post-featured-image`, `wp:query-title`, `wp:query-pagination`,
`wp:site-logo`, `wp:site-title`, `wp:archive-title`, `wp:term-description`,
`wp:loginout`.

`wp:query` is allowed only inside the Sandbox bucket as a stress test (it
renders a server-side loop in any theme but inherits zero styling from a
classic theme, so the Sandbox is the right home for it).

### Reference palette (the inline values)

| Role           | Hex       | Slug         | Usage                                    |
| -------------- | --------- | ------------ | ---------------------------------------- |
| Ink            | `#1B1B1F` | `ink`        | Body text, headlines on light bg, lines  |
| Paper          | `#F4EFE6` | `paper`      | Page background, light overlays          |
| Terracotta     | `#B8533A` | `terracotta` | Primary accent, CTAs                     |
| Teal           | `#2F6F6A` | `teal`       | Secondary accent, links on light bg      |
| Ochre          | `#D6A24E` | `ochre`      | Tertiary, highlights                     |
| Sage           | `#7A8C6F` | `sage`       | Tertiary, backgrounds for cards          |

Every block whose color matters MUST carry both the slug class and the
inline hex.

### Reference typography (the inline values)

| Role     | Slug       | Inline values                           | Use                       |
| -------- | ---------- | --------------------------------------- | ------------------------- |
| Display  | `display`  | `font-size:3.5rem; line-height:1.05`    | Hero headlines (Home, Visit) |
| XLarge   | `x-large`  | `font-size:2.5rem; line-height:1.1`     | Section titles            |
| Large    | `large`    | `font-size:1.5rem; line-height:1.3`     | Lead paragraphs, callouts |
| Medium   | `medium`   | `font-size:1.125rem; line-height:1.5`   | Body                      |
| Small    | `small`    | `font-size:0.875rem; line-height:1.4`   | Captions, fine print      |

### Pattern library (build once, reuse everywhere)

Engineer these seven patterns once. Reuse them across every marketing page.
Each is built dual-render.

| # | Pattern        | Description                                                                                              |
| - | -------------- | -------------------------------------------------------------------------------------------------------- |
| 1 | Hero           | `wp:cover {alignfull}` with overlay heading (inline color), lead paragraph, primary `wp:button`.        |
| 2 | Three-up grid  | `wp:columns {alignwide}` of three `wp:column` cards, each with `wp:image`, `wp:heading`, `wp:paragraph`. |
| 3 | Feature + image| `wp:media-text` with palette-accent inline border, image-left or image-right.                            |
| 4 | Quote callout  | `wp:pullquote {alignwide}` with inline border-color and inline text-color.                               |
| 5 | Card row       | `wp:group` containing `wp:columns` of cards (image, title, body) with inline padding & background.       |
| 6 | CTA band       | `wp:cover {alignfull}` solid-color overlay, centered `wp:heading` (inline white) + primary `wp:button`. |
| 7 | Section header | `wp:group` with eyebrow `wp:paragraph` (small, accent color) + `wp:heading` (xlarge) + optional intro.   |

The seven patterns assemble into all marketing pages. Authoring becomes
assembly.

### Forbidden visual habits

- Color-only signaling without inline fallback.
- Headlines whose hierarchy collapses to default `<h1>` size in classic
  themes (always carry inline `font-size`).
- `wp:cover` with overlay text and no inline text color.
- `wp:button` styled only via theme.json (always inline both bg and fg).
- Reliance on theme-provided spacing tokens (use inline `padding` /
  `margin` where spacing matters to the design).
- Background images bigger than 350 KB after compression.

---

## 4. Imagery direction (extends `art-direction.md`)

The illustration system is the personality. It carries the brand through any
rendering context — CSS can't make a stock photo look like Demo Dispatch,
but our illustrated heroes look like Demo Dispatch in IE6.

What changes from v1: extend the subject vocabulary to cover the new content
shapes (shop items, menu items, project metaphors, team avatars) without
breaking visual coherence. Same palette, same line treatment, same paper
background, same prompt template.

See `art-direction.md` for medium and prompt rules. See
`subject-palette-map.md` for the extended subject list.

---

## 5. Acceptance checks

Content authored against this spec is accepted only if all hold:

1. Voice matches the rules in §2 across every shape (essay, case study,
   product, menu item).
2. No forbidden block types appear in any post or page body (Sandbox
   exempt).
3. Every styled block carries both a slug class **and** an inline `style`
   for color and font-size.
4. Every `wp:cover` with overlay text inline-colors the text.
5. Every `wp:button` inline-styles its background and foreground.
6. Featured image set on every post (Sandbox exempt where intentional).
7. Every page in the marketing set assembles only from the seven patterns
   in §3 (or extends them with the same dual-render discipline).

CI guards in `ci/check_classic_degradation.py` enforce 2–5 mechanically.
Voice (1) is enforced by editorial review.

---

## 6. Versioning

`Version` at the top of this file moves to a new minor for additions
(e.g., a new approved block type) and a new major for breaking changes
(e.g., a forbidden block becomes allowed, or the palette shifts).
