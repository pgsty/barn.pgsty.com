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

## Find the implementation

Use tag **v0.9.1** for the current documentation baseline. Record the commit
and any uncommitted diff during validation. The
[v0.9.0 source tree](https://github.com/pgsty/barn/tree/v0.9.0) describes the
previous release, before the Go upgrade and native app rename.

| Behavior | Source location |
| --- | --- |
| Commands, flags, JSON output, error rendering | `cmd/barn/`, `internal/failure/` |
| Inventory parsing, defaults, resolved node hashes | `internal/config/`, `internal/spec/` |
| Linux convergence, journals, disks, SSH readiness | `internal/private/`, `internal/vm/`, `internal/cloudinit/`, `internal/state/` |
| Host networking, process identity, privileged hosts updates | `internal/network/`, `internal/process/`, `internal/hostconfig/`, `cmd/barn-hosts-helper/` |
| Catalog trust, qcow2 verification, repository materialization | `internal/image/`, `tools/catalogexport/`, `tools/catalogsign/` |
| Native Mac lifecycle and desktop | `internal/macvm/`, `native/mac-runner/` |
| Distribution and image builds | `packaging/`, `.github/workflows/`, `tests/` |

Read the relevant tests alongside the implementation. They distinguish
supported recovery from cases where Barn deliberately refuses to act.

## Build and test

Install the pinned toolchain as described in [Build from Source](../../start/source-build/).
Then run:

```bash
make check
```

This runs module and shell checks, unit and race tests, static analysis,
vulnerability scanning, four-target cross-builds, installer and image-pipeline
tests, and license checks. The Makefile defines the complete list. CI also
checks formatting, whitespace, and release configuration.

Test VM behavior on the relevant host. A successful cross-build does not test
macOS HVF, Linux KVM and networking, or the native macOS component.
Describe which environment and behavior you tested in the pull request.

For packaging changes, use a local snapshot:

```bash
make release-check
make release-snapshot SNAPSHOT_DIST=.goreleaser-review
```

Install the versions in `packaging/toolchain.env` and the archive/package
inspection tools required by the verification scripts. Use a new output
directory directly under the checkout. The snapshot target refuses existing
output. It does not upload the snapshot.

## Edit the documentation

Store each English page beside its Chinese translation as `page.md` and `page.zh.md`.
Keep commands, defaults, links, and warnings aligned. Explain the user's task
before the implementation, and keep Linux and macOS guest workflows distinct.

In the website repository, run:

```bash
make check
```

This builds with the pinned Hugo theme and checks internal links, assets, and
anchors. Preview changes in both languages and both color themes before
submitting a layout change.

`make check` and `make build` clear local theme replacements and disable Go
workspaces. Use `make check-local` or `make build-local` deliberately when
testing changes in the sibling Oink checkout. A successful site build does
not validate shell examples. Compare examples with command help. Run inventory
examples through `validate` and `plan` with an isolated `BARN_HOME`.

Keep dated release evidence intact. Link historical source to the commit that
contains it, and verify the link on GitHub.

## Understand release outputs

The release workflow marks versions below 1.0.0 as GitHub pre-releases.
Barn 0.9.1 provides macOS and Linux archives,
Linux packages, checksums, release metadata, and SPDX software bills of materials.
The CLI and `barn-hosts-helper` are packaged together. Archives contain binaries
under `bin/` and license texts under `licenses/`. Linux packages install
`/usr/bin/barn` and `/opt/barn/libexec/barn-hosts-helper`.

Barn 0.9.1 ships CLI/helper artifacts without `Barn.app`. In a release that
distributes the native component, the Darwin arm64 archive can include `Barn.app` only after its native payload
is Developer ID signed and notarized. When all six Mac signing/notarization
secrets are absent, the release workflow produces CLI-only artifacts; a partial
configuration fails, and a fully configured native build must pass before
publication. A CLI-only build remains usable for Linux guests. See the
[native release guide](https://github.com/pgsty/barn/blob/main/docs/mac-release.md).

Before publication, rerun source and packaging CI on the selected commit,
check the version, helper digest, licenses, native payload, SBOMs, and checksums,
and perform real Linux VM acceptance. Include Mac VM acceptance when shipping
a native payload. Publish the documentation after
the release assets and Homebrew formula are available, then verify the public
installation paths. Local builds do not establish those public results.

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
`make catalog-sign` and `make catalog-verify` use a separate Minisign key pair.
Keep production private keys outside source and CI. See the
[image reference](../../reference/images/) for the catalog's user-facing contract.
