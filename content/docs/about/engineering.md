---
title: Engineering
description: Source layout, build and test gates, image normalization, release outputs, and evidence policy.
weight: 30
icon: fa-solid fa-screwdriver-wrench
---

This page describes the **Barn 0.9.0 release candidate**. Build commands use
your current checkout; record its commit and uncommitted changes. Source builds
and local checks do not establish a published release.

## Repository boundary

The Barn source repository contains code, tests, build/package definitions,
legal notices, `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `SECURITY.md`,
and bilingual application release notes. This site provides user, design,
operator, and release documentation. Runtime behavior and command flags must
be checked against the matching source and binary; an unpublished source
change is not evidence that a public package has the same behavior.

Review transcripts, scratch inventories, generated binaries, and release
output trees are not production source inputs.

Generated output is disposable:

- `bin/` — development builds;
- `dist/` and `.goreleaser-*` — release/snapshot staging;
- root `barn`, `barn-hosts-helper`, and `catalogsign` binaries;
- Hugo `public/` and `resources/`.

## Build and source gates

```bash
make check
```

`make check` runs module and shell checks, maintenance ownership, unit/race
tests, Vet, Staticcheck, dead-code and errcheck checks, vulnerability scanning,
four-target cross-builds, installer/image-pipeline tests, and license checks.
The Makefile defines the exact list. CI additionally checks the pinned
toolchain, Go formatting, whitespace, and GoReleaser configuration. Installation
of the quality tools is covered in [Build from Source](../../start/source-build/).

Packaging changes have a separate snapshot gate:

```bash
make release-check
make release-snapshot SNAPSHOT_DIST=.goreleaser-review
```

Install the versions in `packaging/toolchain.env`, including GoReleaser, nFPM,
and Syft. The snapshot target also needs the archive/package inspection tools
used by the verification scripts. Choose a new output directory directly under
the checkout; existing output is refused. A snapshot is local and does not
upload a release.

A source gate is not native VM evidence. macOS HVF, Linux KVM/networking,
package consumption, release publication, and public website rendering remain
separate checks. `make image-pipeline-native-test` runs the separate native
image-pipeline gate with QEMU/libguestfs and explicit image inputs; the required
`BARN_IMAGE_PIPELINE_NATIVE_*` variables are documented in
`tests/image-pipeline-native-test.sh`. It never downloads a test image.

## Release and package contract

Release tooling under `packaging/`, `.goreleaser.yaml`, and `.github/workflows`
is source, even though its generated directories are not. Archives and Linux
packages contain the matching CLI and hosts-helper binaries, `LICENSE`, the
source README, and exact upstream license bytes reconstructed from modules
pinned by `go.mod`. Archives place the two binaries under `bin/` and the license
texts under `licenses/`. Linux packages install `/usr/bin/barn`,
`/opt/barn/libexec/barn-hosts-helper`, and documentation under
`/usr/share/doc/barn/`.

`BUILD_INFO.json` is included in Linux packages and the older development
archive format. Formal GoReleaser archives carry build identity in the binary,
with release metadata alongside the published assets; do not assume every
archive contains that file. Generated dependency license files are staged at
build time. Detailed user documentation stays on this site.

Application releases are built in GitHub Actions, with `checksums.txt`,
release metadata, and SPDX SBOM assets. The current workflow does not produce
a separate application-release signature or provenance/attestation bundle.
Catalog Minisign signatures authenticate image catalogs and are a separate
trust mechanism.

Commit, tag, archive/package verification, CI, draft upload, public release,
and anonymous consumption are separate evidence. The tag workflow creates a
draft; it does not publish it. Pre-1.0 versions are GitHub prereleases and the
installer requires an explicit `BARN_VERSION`.

`make release-local VERSION=<version>` builds and verifies without publishing.
It requires a clean checkout at the matching `v<version>` tag, an `origin`
remote, pinned tools, and unused staging/output directories. Use the snapshot
path for reviewing an untagged candidate.

## Image normalization

The low-level `packaging/image-pipeline/build.sh` accepts an explicit local
qcow2 source and never downloads or uploads. It copies and hashes the source,
forces qcow2 parsing, rejects backing/external/encrypted/unknown features, runs
`qemu-img check`, and can perform a no-network offline Guest mutation in an
explicit QEMU sandbox. UID/GID 88 collisions are rejected rather than rewritten
ambiguously.

`build-official.py` adds a fixed digest-pinned wrapper for Debian 12/13 and
Rocky Linux 8/9 on amd64/arm64. It may fetch only the locked source and offline
package inputs, then emits unsigned `testing` candidates and can assemble a
separate candidate repository. Native smoke, repeat-build comparison,
production signing, upload, and Catalog activation remain later gates.

Catalog bytes are exported with:

```bash
go run ./tools/catalogexport /absolute/new/catalog.json
```

The exporter is atomic and refuses an existing output path. `make catalog-sign`
and `make catalog-verify` use the catalog Minisign key pair; production private
keys stay outside source and CI. Application checksums do not replace catalog
signatures.

## Evidence policy

Historical M0–M4 notes were useful during implementation but are not product
documentation. Their durable conclusions are condensed into [Design](../design/)
and [Status](../status/). A later source edit inherits no native proof; every
status claim names its date, host, path, and remaining gates.
