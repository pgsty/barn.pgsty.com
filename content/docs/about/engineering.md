---
title: Contributing
description: Work on Barn's source, documentation, packages, and image catalog.
weight: 30
icon: fa-solid fa-screwdriver-wrench
---

Barn is an Apache-2.0 open-source project. Contributions to the CLI, native macOS component, documentation, and image pipeline are welcome.

## Choose a repository {#choose-a-repository}

| What you want to change | Where to work |
|---|---|
| CLI behavior, VM lifecycle, native macOS component (`Barn.app`), installer, and packages | [`pgsty/barn`](https://github.com/pgsty/barn) |
| Documentation site, guides, command reference, and translations | [`pgsty/barn.pgsty.com`](https://github.com/pgsty/barn.pgsty.com) |
| Official Linux image definitions or offline normalization rules | `packaging/image-repository/` and `packaging/image-pipeline/` in [`pgsty/barn`](https://github.com/pgsty/barn) |
{.wide .expand}

When filing a bug report, include `barn version`, your host OS and architecture, the exact command you ran, and the error output with private keys and passwords removed. Report security vulnerabilities privately via the [security policy](https://github.com/pgsty/barn/blob/main/SECURITY.md). For major behavioral changes, open an issue first to align on the design, and see [`CONTRIBUTING.md`](https://github.com/pgsty/barn/blob/main/CONTRIBUTING.md) for coding and pull-request conventions.

## Find the implementation {#find-the-implementation}

Tag **`v1.2.0`** is the current stable release; its changes since 1.1.0 are listed in the [1.2.0 release notes](/blog/release/1.2.0/). Find each subsystem here:

| Subsystem | Source paths |
|---|---|
| CLI commands, flags, JSON/YAML output, and error rendering | `cmd/barn/`, `internal/failure/` |
| Inventory parsing, defaults, and resolved node hashes | `internal/config/`, `internal/spec/` |
| Linux convergence, journals, disks, and SSH readiness | `internal/private/`, `internal/vm/`, `internal/cloudinit/`, `internal/state/` |
| Host networking, process identity, and privileged `/etc/hosts` updates | `internal/network/`, `internal/process/`, `internal/hostconfig/`, `cmd/barn-hosts-helper/` |
| Image catalog trust, `qcow2` verification, and repository build tools | `internal/image/`, `tools/catalogexport/`, `tools/catalogsign/` |
| Native macOS VM lifecycle and desktop app | `internal/macvm/`, `native/mac-runner/` |
| Packaging, CI workflows, and integration suites | `packaging/`, `.github/workflows/`, `tests/` |
{.wide .expand}

Read each package's tests alongside the implementation—they codify the exact boundary between automatic recovery and fail-closed safety checks.

## Build and test {#build-and-test}

Install the pinned toolchain listed in [Build from Source](../../start/source-build/) and run the full local gate:

```bash
make check
```

`make check` runs Go module and shell checks, unit and race-detector tests, `go vet`, `staticcheck`, `govulncheck`, four-target cross-builds (`darwin/arm64`, `darwin/amd64`, `linux/amd64`, `linux/arm64`), installer and image-pipeline tests, and license verification. When changing hypervisor, networking, or `Barn.app` behavior, also run live VM lifecycle tests on the target host (macOS HVF / Virtualization.framework or Linux KVM) and record the tested host environment in your pull request.

To verify packaging changes locally with the tools pinned in `packaging/toolchain.env`:

```bash
make release-check
make release-snapshot SNAPSHOT_DIST=.goreleaser-review
```

`SNAPSHOT_DIST` must be a new directory path inside the repository root; `release-snapshot` builds and verifies archives, `.deb`/`.rpm` packages, SBOMs, and checksums locally without uploading artifacts.

## Edit the documentation {#edit-the-documentation}

Maintain new design decisions, research conclusions, and acceptance records in this site's `content/blog/design/` and `content/blog/release/`, with their date, implementation status, source evidence, and acceptance conditions. The [design notes](/blog/design/) collect the durable explanations; task guides and reference contracts stay in `content/docs/`. The source repository no longer maintains a `docs/` directory.

Every documentation page is maintained as an English/Chinese pair (`page.md` and `page.zh.md`). Keep commands, defaults, explicit `{#id}` heading anchors (required by OINK `v1.5.1` Duo View `compare: true`), tables, and warnings in 1:1 parity across both languages, lead with the user's task, and keep Linux lab and `barn mac` workflows clearly separated.

Validate the website repository with:

```bash
make check
```

`make check` verifies the Go module graph, builds the site with Hugo Extended against the pinned OINK `v1.5.1` module (clearing any local theme replacements and disabling Go workspaces), and runs `bin/check_internal_links.py public` to verify all internal links, anchors, and assets. When testing against a local sibling OINK checkout, use `make check-local` or `make build-local`. Check CLI examples against `barn <command> --help` and test inventory examples with `barn validate` and `barn plan` using a temporary `BARN_HOME`.

## Release outputs and gates {#release-outputs-and-gates}

Stable versions from `1.0.0` on are published as the latest GitHub release; versions below `1.0.0` and versions with a prerelease suffix are GitHub pre-releases and need an explicit `BARN_VERSION` in the installer. Each release ships `darwin`/`linux` `.tar.gz` archives (containing `bin/barn`, `bin/barn-hosts-helper`, and `licenses/`), Linux `.deb` and `.rpm` packages (installing `/usr/bin/barn` and `/opt/barn/libexec/barn-hosts-helper`), `checksums.txt`, `release.json`, and SPDX SBOMs.

Since **0.9.2**, the Darwin arm64 archive also contains `bin/Barn.app`. Its CLI, helper, and app use Developer ID signatures and Apple notarization. Homebrew installs the app under `libexec`; ordinary installation needs no Go or Xcode.

The automatic release workflow requires all six Apple signing/notarization secrets and a successful native build. With none configured, it skips automatic release creation; partial configuration fails. The [Mac release handbook](../mac-release/) covers the local signed-release process, payload identity, CI secrets, and installation acceptance.

Before publishing a release:

1. Run `make catalog-check`: it verifies both official mirrors' signatures in fresh temporary data roots, requires the exact embedded catalog bytes, and checks all stable artifact URLs and sizes. If the catalog changed, synchronize the embedded snapshot, revision, date, and `repo.yaml` first. Run catalog tests and `barn update` with a fresh temporary `BARN_HOME`; `go run ./tools/catalogcheck -verify-bytes` also downloads and hashes every stable artifact without retaining it. Formal native builds and both release paths enforce the catalog gate.
2. Run the source CI and packaging workflows on the target commit and verify version strings, paired `barn-hosts-helper` digests, licenses, SBOMs, and `checksums.txt`.
3. Run live Linux VM acceptance tests (and live macOS VM acceptance when shipping `Barn.app`).
4. Publish the GitHub Release and update the Homebrew tap (`pgsty/infra/barn`), then publish the documentation site and verify the public download and package installation paths.
{.steps}

## Maintain the image catalog {#maintain-the-image-catalog}

Use the [Image Pipeline](../../reference/image-pipeline/) tools (`packaging/image-pipeline/build.sh` and `build-official.py`) to validate and offline-normalize candidate `qcow2` images before running live hypervisor smoke tests, updating `repo.yaml`, and signing `catalog.json`.

To export the binary's embedded schema-3 catalog to a new path:

```bash
go run ./tools/catalogexport /absolute/new/catalog.json
```

`catalogexport` writes atomically to a non-existent target path; it accepts relative paths, `~/`, and directory symlinks and creates missing parent directories. Use `make catalog-sign` and `make catalog-verify` with the offline Minisign keypair (keeping production private keys outside Git and CI). See [Linux Images](../../reference/images/) for the repository and client verification rules.
