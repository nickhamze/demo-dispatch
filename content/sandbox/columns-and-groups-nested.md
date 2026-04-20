---
slug: columns-and-groups-nested
title: Columns and groups, nested
author: daniyal
date: 2024-08-30 14:30:00
category: sandbox
tags: [typography]
format: standard
block_safe: false
---

> This is sample content for theme previews. (Sandbox post.)

A nested layout test for the Columns and Group blocks.

<!-- wp:group {"align":"wide"} -->
<div class="wp-block-group alignwide">

<!-- wp:columns -->
<div class="wp-block-columns">

<!-- wp:column {"width":"33.33%"} -->
<div class="wp-block-column" style="flex-basis:33.33%">
<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">First column</h3>
<!-- /wp:heading -->
<!-- wp:paragraph -->
<p>A paragraph nested in the first column. Testing how the active theme
balances three columns at the wide alignment, including the small bit of
prose you would actually expect to read inside one.</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->

<!-- wp:column {"width":"33.33%"} -->
<div class="wp-block-column" style="flex-basis:33.33%">
<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">Second column</h3>
<!-- /wp:heading -->
<!-- wp:columns -->
<div class="wp-block-columns">
<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:paragraph -->
<p>Nested column A, inside column two.</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->
<!-- wp:column -->
<div class="wp-block-column">
<!-- wp:paragraph -->
<p>Nested column B, inside column two.</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->
</div>
<!-- /wp:columns -->
</div>
<!-- /wp:column -->

<!-- wp:column {"width":"33.33%"} -->
<div class="wp-block-column" style="flex-basis:33.33%">
<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">Third column</h3>
<!-- /wp:heading -->
<!-- wp:paragraph -->
<p>A third column, slightly longer in prose to verify that columns balance
at unequal lengths and that vertical alignment behaves sensibly when one
column has more content than its neighbours.</p>
<!-- /wp:paragraph -->
</div>
<!-- /wp:column -->

</div>
<!-- /wp:columns -->

</div>
<!-- /wp:group -->
