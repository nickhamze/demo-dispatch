---
slug: elements
title: Elements
order: 3
---

# Elements

A typography and block reference. Every element a theme should style is on
this page. If anything below renders unexpectedly in the active theme, that
is a styling bug worth investigating.

## Headings

# Heading level one
## Heading level two
### Heading level three
#### Heading level four
##### Heading level five
###### Heading level six

## Paragraphs and inline elements

A paragraph at the body size. Inline elements include **bold text**,
*italic text*, ***bold italic***, ~~strikethrough~~, `inline code`,
[a link](https://example.com), and a <sup>superscript</sup> and a
<sub>subscript</sub>.

A second paragraph, slightly longer than the first, intended to give the
active theme a fair chance to demonstrate its line height, its measure,
and its handling of widows and orphans across a normal stretch of prose.

## Blockquote

> A standard blockquote, a single paragraph long. The active theme should
> distinguish this visually from body paragraphs.
>
> A second paragraph in the same blockquote, with a citation.
> --- Demo Dispatch

## Pullquote

<!-- wp:pullquote -->
<figure class="wp-block-pullquote"><blockquote><p>A pullquote, set apart from the body, demanding more visual weight.</p><cite>Demo Dispatch</cite></blockquote></figure>
<!-- /wp:pullquote -->

## Lists

Unordered:

- An unordered list item.
- Another item.
  - A nested item.
  - Another nested item.
    - A deeper nested item.
- Final item.

Ordered:

1. The first ordered item.
2. The second.
3. The third.
   1. A nested item.
   2. Another nested item.
4. The fourth.

Definition list:

<dl>
<dt>Generalisation</dt>
<dd>The cartographic technique of simplifying a real-world feature for the purpose of mapping it.</dd>
<dt>Fresnel lens</dt>
<dd>A lens whose volume has been carved into concentric rings to reduce its weight without sacrificing its optical properties.</dd>
</dl>

## Table

| Element       | Status   | Notes                              |
| ------------- | -------- | ---------------------------------- |
| H1 - H6       | Required | Six heading levels                 |
| Paragraph     | Required | Body text                          |
| Blockquote    | Required | Optional citation                  |
| Pullquote     | Optional | Block themes only                  |
| Code          | Required | Both inline and block              |
| Table         | Required | Should be horizontally scrollable  |
| Figure        | Required | Caption optional                   |

## Code

Inline: `const greeting = "Hello, world!"`.

Block:

```js
function greet(name) {
  return `Hello, ${name}!`;
}

console.log(greet("world"));
```

Preformatted:

```
A
 preformatted
  block
   that
    preserves
     whitespace.
```

## Buttons

<!-- wp:buttons -->
<div class="wp-block-buttons">
<!-- wp:button -->
<div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="#">Primary button</a></div>
<!-- /wp:button -->
<!-- wp:button {"className":"is-style-outline"} -->
<div class="wp-block-button is-style-outline"><a class="wp-block-button__link wp-element-button" href="#">Outline button</a></div>
<!-- /wp:button -->
</div>
<!-- /wp:buttons -->

## Image alignments

A left-aligned image (textual content wraps around it) followed by a
right-aligned image, then a centered, a wide, and a full-width image.

![Aligned left.](paperweight.webp){.alignleft}

A paragraph alongside the left-aligned image to demonstrate text wrap.
This paragraph contains enough prose to show how the active theme handles
the float-clearing margin between body text and an image floated to the
left edge of the content area.

![Aligned right.](compass.webp){.alignright}

A paragraph alongside the right-aligned image. Similar to the above but
mirrored. Themes should clear the float at the end of the next block
without leaving the body text wrapped under a tall image.

![Aligned centre.](teacup.webp){.aligncenter}

![Wide alignment.](harbor.webp){.alignwide}

![Full alignment.](lighthouse.webp){.alignfull}

## Palette

Six locked colours from the dataset's illustration palette.

<table class="palette">
<tr>
  <td style="background:#F4EFE6;color:#1B1B1F">#F4EFE6 paper</td>
  <td style="background:#1B1B1F;color:#F4EFE6">#1B1B1F ink</td>
  <td style="background:#B8533A;color:#F4EFE6">#B8533A terracotta</td>
  <td style="background:#2F6F6A;color:#F4EFE6">#2F6F6A ocean teal</td>
  <td style="background:#D6A24E;color:#1B1B1F">#D6A24E mustard ochre</td>
  <td style="background:#7A8C6F;color:#F4EFE6">#7A8C6F sage green</td>
</tr>
</table>
