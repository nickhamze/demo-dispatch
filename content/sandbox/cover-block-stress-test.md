---
slug: cover-block-stress-test
title: Cover block - text overlay at every alignment
author: mira
date: 2024-09-18 12:00:00
category: sandbox
tags: [typography]
format: standard
block_safe: false
featured_image: harbor
---

> This is sample content for theme previews. (Sandbox post.)

This post puts the Cover block through its paces. It is not intended to be
read; it is intended to be inspected by a theme reviewer who wants to know
how the active theme styles overlay text on full-width imagery.

<!-- wp:cover {"url":"harbor.webp","dimRatio":40,"contentPosition":"top left","align":"full"} -->
<div class="wp-block-cover alignfull"><span aria-hidden="true" class="wp-block-cover__background has-background-dim"></span><img class="wp-block-cover__image-background" alt="" src="harbor.webp"/><div class="wp-block-cover__inner-container">
<!-- wp:heading {"level":2,"textAlign":"left","textColor":"white"} -->
<h2 class="wp-block-heading has-text-align-left has-white-color">Top-left, light overlay</h2>
<!-- /wp:heading -->
</div></div>
<!-- /wp:cover -->

<!-- wp:cover {"url":"lighthouse.webp","dimRatio":70,"contentPosition":"center center","align":"wide"} -->
<div class="wp-block-cover alignwide"><span aria-hidden="true" class="wp-block-cover__background has-background-dim-70 has-background-dim"></span><img class="wp-block-cover__image-background" alt="" src="lighthouse.webp"/><div class="wp-block-cover__inner-container">
<!-- wp:heading {"level":2,"textAlign":"center","textColor":"white"} -->
<h2 class="wp-block-heading has-text-align-center has-white-color">Centered, heavy overlay, wide alignment</h2>
<!-- /wp:heading -->
</div></div>
<!-- /wp:cover -->

<!-- wp:cover {"url":"sailboat.webp","dimRatio":20,"contentPosition":"bottom right"} -->
<div class="wp-block-cover"><span aria-hidden="true" class="wp-block-cover__background has-background-dim-20 has-background-dim"></span><img class="wp-block-cover__image-background" alt="" src="sailboat.webp"/><div class="wp-block-cover__inner-container">
<!-- wp:heading {"level":2,"textAlign":"right","textColor":"white"} -->
<h2 class="wp-block-heading has-text-align-right has-white-color">Bottom-right, very light overlay</h2>
<!-- /wp:heading -->
</div></div>
<!-- /wp:cover -->

<!-- wp:cover {"url":"observatory.webp","dimRatio":50,"contentPosition":"center center","hasParallax":true,"align":"full"} -->
<div class="wp-block-cover alignfull has-parallax" style="background-image:url(observatory.webp);background-position:50% 50%"><span aria-hidden="true" class="wp-block-cover__background has-background-dim"></span><div class="wp-block-cover__inner-container">
<!-- wp:heading {"level":2,"textAlign":"center","textColor":"white"} -->
<h2 class="wp-block-heading has-text-align-center has-white-color">Parallax / fixed background</h2>
<!-- /wp:heading -->
</div></div>
<!-- /wp:cover -->
