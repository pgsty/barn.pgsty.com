# Barn Documentation

This directory contains the bilingual documentation site for Barn. English
is served at `/`; Simplified Chinese is served at `/zh/`. The site uses Hugo
Extended and Oink 1.1.0.

Barn is pre-1.0. Public pages must describe only source repositories,
Releases channels, and package paths that are actually available at the same
checkpoint; a local build or draft is never publication evidence.

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

Keep product pages focused on the current Barn candidate and verified release
status. Build and validation records must not imply that a release has been
published.
