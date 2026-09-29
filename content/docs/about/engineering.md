---
title: Contributing
description: Work on Barn's source, documentation, packages, and image catalog.
weight: 30
icon: fa-solid fa-screwdriver-wrench
---

Barn is an Apache-2.0 project. Contributions to the CLI, native macOS
component, documentation, and image tooling are welcome.

## Choose a repository

| What you want to change | Where to work |
| --- | --- |
| CLI behavior, VM lifecycle, native macOS component, installer, packages | [pgsty/barn](https://github.com/pgsty/barn) |
| This website, tutorials, command reference, translations | [pgsty/barn.pgsty.com](https://github.com/pgsty/barn.pgsty.com) |
| An image definition or normalization step | `packaging/image-repository/` and `packaging/image-pipeline/` in the Barn source repository |

For a bug report, include `barn version`, the host OS and architecture, the
command you ran, and the relevant error. Remove private keys, passwords, and
other secrets from logs and inventories. Report security issues using the
[security policy](https://github.com/pgsty/barn/blob/main/SECURITY.md).

Before a substantial implementation change, open an issue describing the
problem and expected behavior. The source repository's
[contribution guide](https://github.com/pgsty/barn/blob/main/CONTRIBUTING.md)
covers coding conventions, ownership boundaries, and pull requests.

## Build and test

Follow [Build from Source](../../start/source-build/) to install the pinned
toolchain, then run:

```bash
make check
```

This runs module and shell checks, unit and race tests, static analysis,
vulnerability scanning, four-target cross-builds, installer and image-pipeline
tests, and license checks. The Makefile defines the complete list. CI also
checks formatting, whitespace, and release configuration.

VM behavior needs a relevant host test as well: a successful cross-build does
not exercise macOS HVF, Linux KVM and networking, or the native macOS component.
Describe which environment and behavior you tested in the pull request.

For packaging changes, use a local snapshot:

```bash
make release-check
make release-snapshot SNAPSHOT_DIST=.goreleaser-review
```

Install the versions in `packaging/toolchain.env` and the archive/package
inspection tools required by the verification scripts. Use a new output
directory directly under the checkout; the snapshot target refuses existing
output and does not upload it.

## Edit the documentation

English and Chinese pages live beside each other as `page.md` and `page.zh.md`.
Keep commands, defaults, links, and warnings aligned. Explain the user's task
before the implementation, and keep Linux and macOS guest workflows distinct.

In the website repository, run:

```bash
make check
```

This builds with the pinned Hugo theme and checks internal links, assets, and
anchors. Preview changes in both languages and both color themes before
submitting a layout change.

## Understand release outputs

Barn 0.9.0 provides macOS and Linux archives, Linux packages, checksums,
release metadata, and SPDX software bills of materials. The CLI and
`barn-hosts-helper` travel together. Archives place binaries under `bin/` and
license texts under `licenses/`; Linux packages install `/usr/bin/barn` and
`/opt/barn/libexec/barn-hosts-helper`.

`Barn Mac.app` is an additional component for macOS guests. Its build and
signing requirements are documented in
[the native release guide](https://github.com/pgsty/barn/blob/main/docs/mac-release.md).
A CLI-only build remains usable for Linux guests.

Application checksums, native app signatures, and image-catalog signatures
serve different purposes. The application workflow provides checksums but no
separate release-signature or provenance bundle. The native app has its own
Developer ID and notarization process. Minisign authenticates image catalogs.

## Maintain the image catalog

Start with the [image pipeline reference](../../reference/image-pipeline/).
The low-level builder accepts a local qcow2 image, validates it, and optionally
normalizes it in an offline QEMU sandbox. The official wrapper uses pinned
inputs for Debian 12/13 and Rocky Linux 8/9 on amd64/arm64. It emits unsigned
`testing` entries for review before native smoke tests, signing, and publication.

Export the built-in catalog to a new path with:

```bash
go run ./tools/catalogexport /absolute/new/catalog.json
```

The exporter writes atomically and refuses an existing output path.
`make catalog-sign` and `make catalog-verify` use a separate Minisign key pair;
production private keys stay outside source and CI. See the
[image reference](../../reference/images/) for the catalog's user-facing contract.
