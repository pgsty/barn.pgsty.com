---
title: Build from Source
description: Build Barn 0.9.0 or the development branch, including the native Mac component, and run the contributor checks.
weight: 80
icon: fa-solid fa-code-branch
---

Use a source build to develop Barn, inspect a change, or build the native Mac
component. For a packaged CLI, use [installation](../installation/).

## Select the version

Clone the documented release:

```bash
git clone --branch v0.9.0 https://github.com/pgsty/barn.git
cd barn
```

For the development branch, omit `--branch v0.9.0`. Check `git log -1 --oneline`
and `git status --short` to identify your source before comparing behavior.

## Build the CLI

Barn 0.9.0 pins **Go 1.27.1** in `go.mod` and `packaging/toolchain.env`.
You also need Git, Make, Bash, and standard build tools. Compiling the CLI
does not require QEMU or host-network setup.

```bash
make build
export PATH="$PWD/bin:$PATH"
barn version
```

The `bin/` directory contains the CLI and matching `barn-hosts-helper`.
Keep them together. Development builds report `dev` by default; the commit
field identifies the revision, or `uncommitted` for a modified checkout.

Build the native component below to run macOS guests.
Keep lab inventories outside the source tree, and remember
that working directories all use the same `BARN_HOME`.

## Build the Mac component {#mac-component}

On Apple Silicon with macOS 27 and **Xcode 27**:

```bash
make mac-build
export PATH="$PWD/bin/mac:$PATH"
barn mac doctor
```

This creates a CLI and native `Barn Mac.app` bundle under `bin/mac`, signed
ad hoc for local use. It creates no VM. Continue with the [Mac guide](../macos/).
`make mac-native-test` runs the native component tests.

## Check a change

The complete checks also need Python 3, jq, a C toolchain for race tests, and
the versions pinned in `packaging/toolchain.env`:

```bash
go install honnef.co/go/tools/cmd/staticcheck@v0.8.1
go install golang.org/x/tools/cmd/deadcode@v0.49.0
go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.13.2
go install golang.org/x/vuln/cmd/govulncheck@v1.7.0
```

Add the Go tools directory (`GOBIN`, or `$(go env GOPATH)/bin` when unset) to PATH.

```bash
make test
make check
```

`make check` includes module verification, shell syntax, maintenance checks,
unit and race tests, Vet, Staticcheck, dead-code and errcheck checks,
vulnerability checks, four-target builds, image-pipeline and installer tests,
and dependency licenses. Packaging changes also need a verified snapshot.
See [contributing and releases](../../about/engineering/) for that workflow.
