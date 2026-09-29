<h1 align="center">
  <a href="https://barn.pgsty.com/">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="static/images/barn-logo-dark.svg">
      <img src="static/images/barn-logo.svg" alt="Barn" width="360">
    </picture>
  </a>
</h1>

<p align="center"><strong>Barn documentation and blog</strong></p>

<p align="center">
  <a href="https://barn.pgsty.com/">Website</a> ·
  <a href="https://barn.pgsty.com/docs/">Documentation</a> ·
  <a href="https://barn.pgsty.com/blog/">Blog</a> ·
  <a href="https://github.com/pgsty/barn">Source Code</a> ·
  <a href="https://barn.pgsty.com/zh/">中文</a>
</p>

This directory contains the bilingual documentation site for Barn. English
is served at `/`; Simplified Chinese is served at `/zh/`. The site uses Hugo
Extended and Oink 1.1.0.

The documentation targets **Barn 0.9.0**. Product pages describe the released
version in the present tense; stage these updates with the corresponding
application release.

## Brand assets

Barn uses **03 / Compute Barn** from `BARN-visual-concepts-v1.zip`: the
iron-oxide circular barn with three server bays, paired with the path-drawn
BARN wordmark and its copper A. Use this direction consistently.

| Asset | File | Use |
| --- | --- | --- |
| Graphic mark | [barn-mark.svg](static/images/barn-mark.svg) | Navbar, sidebar, favicon and application icons |
| Wordmark | [light](static/images/barn-wordmark.svg) · [dark](static/images/barn-wordmark-dark.svg) | Text-only SVG, transparent background |
| Combined logo | [light](static/images/barn-logo.svg) · [dark](static/images/barn-logo-dark.svg) | README and other horizontal placements |
| Dusk hero | [SVG](static/images/barn-hero.svg) · [PNG](static/images/barn-hero.png) | Homepage, default blog cover and social preview |

The palette is iron oxide `#A9573B`, slate `#344F60`, copper `#AF8250` and
warm ivory `#FFF9EB`. Both logo variants have transparent backgrounds; the
dark variant uses ivory lettering. The wordmarks contain paths, so no font
installation is required. The site theme toggle selects the matching wordmark.

The source repository's `.github/barn-logo.svg` and `barn-logo-dark.svg` are
copies of these combined logos. Its native `Barn.icns` and this site's
favicon/touch icons derive from the same selected mark; the original package
supplies simplified silhouettes for 16px and 32px sizes.

English and Chinese blog roots cascade `images/barn-hero.png` as the default
cover. A post can supply its own `images` front matter or a featured image in
its page bundle. Site-wide `params.images` supplies the social-preview default.

## Local development

The published dependency is pinned in `go.mod`. While Oink is developed from a
sibling checkout, use the local replacement target:

```bash
make dev
make check-local
```

The release-resolved paths are:

```bash
make build
make check
```

The production target is `https://barn.pgsty.com/` and its build is warning-
strict. Pages settings and DNS must authorize that domain before publication.

The source-controlled `wrangler.toml` defines the Pages project, output
directory, `HUGO_VERSION=0.165.0`, and `GO_VERSION=1.27.1` for both Production
and Preview. Keep Go aligned with `go.mod` so Pages installs it before Hugo
resolves modules. Cloudflare's default Hugo can be older than Oink requires;
`HUGO_SERVER` is not a recognized version selector.

## Content policy

English and Chinese pages live beside each other as `page.md` and
`page.zh.md`. Keep them aligned, concise, and grounded in the current checkout.
Blog posts live under `content/blog/article`, `content/blog/design`, or
`content/blog/release`; do not put regular posts directly under `content/blog`.

Lead with the reader’s task: choose a guest type, install, start, connect, and
manage it. Keep detailed options in the reference, design rationale in the
project pages and blog, and internal validation records out of product copy.
Verify behavior against the matching CLI and preserve the distinction between
application packages, the native macOS component, and image-catalog trust.
