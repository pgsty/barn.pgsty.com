---
title: Build from Source
description: Build Barn 0.9.1 or the development branch, including the native Mac component, and run the contributor checks.
weight: 80
icon: fa-solid fa-code-branch
---

Use a source build to develop Barn, inspect a change, or build the native Mac
component. For a packaged CLI, use [installation](../installation/).

## Select the version

Use tag **v0.9.1** to reproduce this release. Record `git log -1 --oneline`
and `git status --short`; a version label alone does not identify the source
used to build a binary.

Clone the documented release:

```bash
git clone --branch v0.9.1 https://github.com/pgsty/barn.git
cd barn
```

For development, omit `--branch v0.9.1`. The published 0.9.0 release does not
contain the Go 1.27.3 upgrade or `Barn.app` rename.

## Build the CLI

Barn 0.9.1 pins **Go 1.27.3** in `go.mod` and `packaging/toolchain.env`.
You also need Git, Make, Bash, and standard build tools. Compiling the CLI
does not require QEMU or host-network setup.

The 2026-10-22 local `make check` passed with the upgraded modules and tools.
`govulncheck` found no affected imported packages or reachable functions.
It still reports the module-level [GO-2026-5932](https://pkg.go.dev/vuln/GO-2026-5932)
for `x/crypto/openpgp`; Barn does not import that package on any of its four
supported targets. Rerun the checks when dependencies or vulnerability data change.

This supersedes the 2026-10-13 check of 0.9.0, which stopped on eight reachable
Go 1.27.1 advisories. The current Go and `x/net` pins include the fixes identified
then. Local checks do not establish hosted CI or live VM acceptance.

```bash
BARN_VERSION=0.9.1 make build
export PATH="$PWD/bin:$PATH"
barn version
```

The `bin/` entry points link to a verified CLI/helper pair under
`bin/.barn-releases/`. Preserve that directory and both links when moving a
development build. The CLI embeds the helper's digest, so plain
`go build ./cmd/barn` is not a replacement for this paired build.
Development builds report `dev` by default, including builds from a release tag. Use `0.9.1-dev.1` for a local candidate, or `BARN_VERSION=0.9.1 make build`
when reproducing the published tag. The commit
field identifies the revision, or `uncommitted` for a modified checkout.

`make cross` produces all four supported Go CLI/helper pairs under
`bin/darwin_amd64`, `bin/darwin_arm64`, `bin/linux_amd64`, and `bin/linux_arm64`.
It does not cross-compile the Swift Mac app. Keep build outputs outside Git. The repository ignores `bin/`, `dist/`, and `.goreleaser-*/`.

Build the native component below to run macOS guests.
Keep lab inventories outside the source tree. All working directories use the same `BARN_HOME`.

## Build the Mac component {#mac-component}

If you are rebuilding a local bundle, first stop all VMs that use it.

On Apple Silicon with macOS 27+ and **Xcode 27+** selected for `xcrun`, including
the macOS 27 SDK and Swift compiler:

```bash
BARN_VERSION=0.9.1 make mac-build
export PATH="$PWD/bin/mac:$PATH"
barn mac doctor
```

The build creates a CLI, matching hosts helper, standalone `barn-mac-runner`, and native app under `bin/mac`.
It also creates a verified local archive at `bin/barn-mac-darwin-arm64.tar.gz`.
Keep the complete `bin/mac` bundle together and use its `barn`.
This build does not create a VM; follow the [Mac guide](../macos/) to create one.
`make mac-native-test` runs the native component tests.

| Source | Native app | Application identifier |
|---|---|---|
| `v0.9.0` tag | `Barn Mac.app` | `io.pgsty.barn.mac-runner` |
| `v0.9.1` tag | `Barn.app` | `com.pgsty.barn` |

The 0.9.1 CLI also recognizes the old app name. The 0.9.0 CLI does not discover the new `Barn.app` name by itself. Use the CLI and app built together. The app contains the native
runner, not the Go CLI, hosts helper, or QEMU.

### Signing and distribution

With signing variables unset, the native build uses an **ad-hoc signature**
for local development. `BARN_CODESIGN_IDENTITY` selects a certificate. A Developer ID signature alone does not establish notarization or public release status. The build supports `BARN_NOTARY_PROFILE` and
`BARN_MAC_REQUIRE_NOTARIZATION=1` for a configured notarization workflow.

When you request notarization, the app pipeline verifies the signature. It waits for Apple acceptance, staples the ticket, and checks Gatekeeper. These
checks cover the native app. The Go CLI and hosts helper use a separate build and delivery process. Setting `BARN_CODESIGN_IDENTITY` does not sign them.
If signing that pair for direct distribution, first sign the helper and embed its final SHA-256 in the CLI.
Sign the CLI **afterward**. Follow [Apple's notarization requirements](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution) and the [release workflow](../../about/engineering/).

## Check a change

The complete checks also need Python 3, jq, a C toolchain for race tests, and
the versions pinned in `packaging/toolchain.env`:

```bash
go install honnef.co/go/tools/cmd/staticcheck@v0.8.2
go install golang.org/x/tools/cmd/deadcode@v0.52.0
go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.15.0
go install golang.org/x/vuln/cmd/govulncheck@v1.9.0
```

Add the Go tools directory (`GOBIN`, or `$(go env GOPATH)/bin` when unset) to PATH.

```bash
make test
make check
```

`make check` verifies modules and shell syntax. It runs maintenance checks, unit and race tests, Vet, Staticcheck, dead-code and errcheck checks, and vulnerability checks. It also runs four-target builds, image-pipeline and installer tests, and dependency license checks. Packaging changes also need a verified snapshot.
See [contributing and releases](../../about/engineering/) for that workflow.
