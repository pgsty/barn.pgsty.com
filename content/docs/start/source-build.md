---
title: Build from Source
description: Build Barn 1.1.0 or the development branch, including the native Mac component, and run the contributor checks.
weight: 80
icon: fa-solid fa-hammer
---

Build Barn from source when developing a change or auditing a release tag. For prebuilt CLI binaries and the native `Barn.app` included in the Apple Silicon release, see [Install Barn](../installation/).

## Check out the source {#check-out-the-source}

Clone tag **v1.1.0** to reproduce the documented release (or omit `--branch v1.1.0` to work on `main`), and record `git log -1 --oneline` and `git status --short` alongside any build report:

```bash
git clone --branch v1.1.0 https://github.com/pgsty/barn.git
cd barn
```

Tag `v1.1.0` reproduces the published release described in the [Barn 1.1.0 release notes](/blog/release/1.1.0/). Leave `BARN_VERSION` unset for a development build.

## Build the CLI {#build-the-cli}

Barn `1.1.0` pins **Go 1.27.3** in `go.mod` and `packaging/toolchain.env`, and requires Git, Make, Bash, and standard C/POSIX build tools (compiling the CLI does not require QEMU or host-network setup):

```bash
BARN_VERSION=1.1.0 make build
export PATH="$PWD/bin:$PATH"
barn version
```

`make build` compiles both `barn` and `barn-hosts-helper` into `bin/.barn-releases/`, embeds the helper's SHA-256 digest into the CLI, and creates entry-point symlinks under `bin/`. Always use `make build` rather than a bare `go build ./cmd/barn`, and keep `bin/.barn-releases/` alongside the `bin/` links if you move the build output.

Without `BARN_VERSION`, development builds report `dev` (or use `BARN_VERSION=1.1.0-dev.1` to stamp a local candidate), and the commit field marks modified working trees as `uncommitted`.

To cross-compile the Go CLI and helper for all four supported targets (`darwin_amd64`, `darwin_arm64`, `linux_amd64`, and `linux_arm64`), run `make cross`. Keep build artifacts (`bin/`, `dist/`, `.goreleaser-*/`) and lab inventories out of version control; check ignore rules before generating them in the working tree.

Run the contributor checks below against the exact checkout you intend to use. Earlier dated acceptance records are kept in [Validation History](../../about/history/).

## Build the Mac component {#mac-component}

Before rebuilding a local Mac bundle, stop any running Mac VMs that use it.

On an Apple Silicon Mac running macOS 27+ with **Xcode 27+** selected for `xcrun` (providing the macOS 27 SDK and Swift compiler), run:

```bash
BARN_VERSION=1.1.0 make mac-build
export PATH="$PWD/bin/mac:$PATH"
barn mac doctor
```

`make mac-build` produces a matched bundle under `bin/mac` (`barn`, `barn-hosts-helper`, standalone `barn-mac-runner`, and `Barn.app`) as well as `bin/barn-mac-darwin-arm64.tar.gz`. Run `make mac-native-test` to execute the Swift component test suite, and follow the [macOS VM guide](../macos/) to provision a guest.

| Source tag | Native app bundle | Bundle identifier |
|---|---|---|
| `v0.9.0` | `Barn Mac.app` | `io.pgsty.barn.mac-runner` |
| `v0.9.1` and later | `Barn.app` | `com.pgsty.barn` |

The current CLI discovers both `Barn.app` and legacy `Barn Mac.app` bundles, whereas the `0.9.0` CLI only looks for `Barn Mac.app`—always use the `barn` CLI and native app built together in `bin/mac`.

### Code signing and notarization {#code-signing-and-notarization}

When signing environment variables are unset, `make mac-build` applies an **ad-hoc signature** for local development. For signed or notarized builds:

- Set `BARN_CODESIGN_IDENTITY` to sign `Barn.app` with a Developer ID certificate.
- Set `BARN_NOTARY_PROFILE` and `BARN_MAC_REQUIRE_NOTARIZATION=1` to submit `Barn.app` for Apple notarization, staple the ticket, and verify Gatekeeper acceptance.
- With `BARN_CODESIGN_IDENTITY` set, `make mac-build` also signs the Go helper before embedding its final SHA-256 in the CLI, then signs the CLI. The [Mac release handbook](../../about/mac-release/) adds joint notarization of the CLI/helper/app and verification of the exported release payload.

## Run contributor checks {#run-contributor-checks}

Running the full `make check` suite requires Python 3, `jq`, a C compiler (for `-race`), and the linter/scanner versions pinned in `packaging/toolchain.env`:

```bash
go install honnef.co/go/tools/cmd/staticcheck@v0.8.2
go install golang.org/x/tools/cmd/deadcode@v0.52.0
go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.15.0
go install golang.org/x/vuln/cmd/govulncheck@v1.9.0
```

Ensure `GOBIN` (or `$(go env GOPATH)/bin`) is on your `PATH`, then run:

```bash
make test
make check
```

`make check` verifies `go.mod`, shell scripts, repository maintenance rules, unit and race tests, `go vet`, `staticcheck`, `deadcode`, `golangci-lint`, `govulncheck`, four-target cross-builds, image-pipeline and installer tests, and dependency licenses. See [Contributing and Release Engineering](../../about/engineering/) for packaging snapshot checks.
