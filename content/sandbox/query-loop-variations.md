---
slug: query-loop-variations
title: Query loop variations
author: tomas
date: 2024-08-12 09:00:00
category: sandbox
tags: []
format: standard
block_safe: false
---

> This is sample content for theme previews. (Sandbox post.)

Three Query Loop variations rendered in sequence. Each loop is restricted
to the Articles category and limited to four posts so the comparison is
fair across variants.

<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Default - title and excerpt</h2>
<!-- /wp:heading -->

<!-- wp:query {"queryId":1,"query":{"perPage":4,"taxQuery":{"category":[2]}}} -->
<div class="wp-block-query">
<!-- wp:post-template -->
<!-- wp:post-title {"isLink":true} /-->
<!-- wp:post-excerpt /-->
<!-- /wp:post-template -->
</div>
<!-- /wp:query -->

<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Grid with featured image</h2>
<!-- /wp:heading -->

<!-- wp:query {"queryId":2,"query":{"perPage":4,"taxQuery":{"category":[2]}},"displayLayout":{"type":"flex","columns":2}} -->
<div class="wp-block-query">
<!-- wp:post-template {"layout":{"type":"grid","columnCount":2}} -->
<!-- wp:post-featured-image {"isLink":true} /-->
<!-- wp:post-title {"isLink":true} /-->
<!-- /wp:post-template -->
</div>
<!-- /wp:query -->

<!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">Image-only</h2>
<!-- /wp:heading -->

<!-- wp:query {"queryId":3,"query":{"perPage":4,"taxQuery":{"category":[2]}},"displayLayout":{"type":"flex","columns":4}} -->
<div class="wp-block-query">
<!-- wp:post-template {"layout":{"type":"grid","columnCount":4}} -->
<!-- wp:post-featured-image {"isLink":true} /-->
<!-- /wp:post-template -->
</div>
<!-- /wp:query -->
