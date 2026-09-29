---
title: Build from Source
description: Build Barn for development and review, then run the complete source gate.
weight: 50
icon: fa-solid fa-code-branch
---

Barn 0.9.0 is an **unreleased candidate**. Use this page to build and check the
source. Installation commands for the eventual release are in the
[Quick Start](../tutorial/).

## Choose the source

Clone the Barn repository:

```bash
git clone https://github.com/pgsty/barn.git
cd barn
```

Do not assume a `v0.9.0` tag exists before publication. Check the source identity
and working-tree changes first; `go.mod` must name `github.com/pgsty/barn` and
the command source must live in `cmd/barn`:

```bash
git log -1 --oneline
git status --short
```

## Build

The reviewed candidate tree pins Go 1.27.1 in `go.mod` and
`packaging/toolchain.env`. You also need Git, Make, Bash, and standard build
tools. QEMU and privileged network setup are needed to run VMs, not to compile
the CLI. From the selected checkout:

```bash
make build
export PATH="$PWD/bin:$PATH"
barn version
```

`make build` writes the matching `barn` and `barn-hosts-helper` binaries
under the Git-ignored `bin/` directory. Do not mix the two binaries across
commits or releases. Development builds report `dev` by default; their commit
field identifies a clean source revision or says `uncommitted` for a dirty
checkout. The version string alone does not prove candidate behavior.

Keep the inventory in a separate lab directory. This does not isolate Barn
state: if you already have a deployment, inspect it before running `up`:

```bash
mkdir -p ~/barn-lab && cd ~/barn-lab
barn setup
barn up
```

## Complete checks

The complete checks also need Python 3, jq, a working C toolchain for race
tests, and the pinned quality tools. Install the versions used by the reviewed
candidate's CI (check `CONTRIBUTING.md` and `packaging/toolchain.env` again when
using another revision):

```bash
go install honnef.co/go/tools/cmd/staticcheck@v0.8.1
go install golang.org/x/tools/cmd/deadcode@v0.49.0
go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.13.2
go install golang.org/x/vuln/cmd/govulncheck@v1.7.0
```

Ensure the Go tools installation directory (`GOBIN`, or `$(go env GOPATH)/bin`
when unset) is in `PATH`. Before submitting a source change, run:

```bash
make check
```

This gate includes module verification, shell syntax, maintenance ownership,
unit and race tests, Vet, Staticcheck, four-target dead-code checks, errcheck,
vulnerability checks, cross-builds, image-pipeline and installer tests, and
dependency-license verification. CI separately checks formatting, whitespace,
pinned tool versions, and GoReleaser configuration. Changes to packaging also
need a verified packaging snapshot.

A passing source gate is not package publication or a native VM lifecycle
replay; `make image-pipeline-native-test` is a separate native image gate.
That gate requires the explicit image inputs documented at the top of
`tests/image-pipeline-native-test.sh`; it does not download a test image.

See [Engineering](../../about/engineering/) for release tooling, dependency
licenses, and validation boundaries.
