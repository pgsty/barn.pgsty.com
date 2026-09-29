---
title: "Farrow 0.5.0: explicit disposal, explicit repositories, reproducible images"
linkTitle: Farrow 0.5.0
description: A no-confirmation whole-lab purge, explicit global and China repository selection, no hidden artifact fallback, and an eight-target official-image candidate pipeline.
date: 2026-09-03
weight: 2
categories: [Release]
tags: [Farrow 0.5.0, QEMU, Images, Supply Chain, Release]
icon: fa-solid fa-rocket
---

> [!NOTE]
> This page describes 0.5.0. Official mirror failover was added in 0.7.0,
> and the unreleased 0.9 candidate removes the `rm` alias. Use
> [current CLI guidance](../../../docs/reference/cli/) for your installed version.

Farrow 0.5.0 was the public pre-1.0 release superseded by 0.6.0. It adds an explicit command
for disposable labs, makes repository geography an operator choice, and adds a
reproducible path for preparing the next official guest images. The Pigsty
Inventory contract, deployment state format, and embedded Catalog revision
`2026082903` are unchanged.

## What changed

- `farrow purge` (alias `farrow rm`) removes the complete deployment,
  persistent data disks, deployment keys and state, and the default SSH
  fragment without confirmation. The verified image cache and host-global
  network remain. Absence is idempotent, while unidentifiable residual node
  artifacts still fail closed.
- Released binaries use `https://repo.pigsty.io/farrow` by default. Long-only
  `--mirror` selects `https://repo.pigsty.cc/farrow`; `--repo` remains the
  highest-precedence override, followed by `--mirror`, `FARROW_REPO`, and the
  global default. Both official roots keep canonical signed-Catalog trust.
- Catalog upstream URLs are provenance, not a fallback. A selected repository
  must contain the exact Catalog-named qcow2 or the pull fails with guidance to
  choose another root or import a local image.
- The source tree now has a digest-pinned offline builder for Debian 12/13 and
  Rocky Linux 8/9 on amd64/arm64. It records the exact package closure, SBOM,
  provenance, and `testing` manifest, and can assemble an unsigned candidate
  repository for later native smoke and signing review.
- The pinned source/release toolchain moves to Go 1.27.1, GoReleaser 2.18.0,
  golangci-lint 2.13.2, and current selected Go modules.

## Image boundary

The eight-target matrix fixes concrete guest prerequisites: Debian 12/13 gain
the XFS userspace needed for explicitly XFS-formatted data disks; Rocky Linux 8
gains `/usr/bin/python3`, working SSH drop-in inclusion, and clean interface
naming state; Rocky Linux 9 receives the same legacy-network cleanup.

Those are candidate-build inputs, not newly published Catalog artifacts. Every
result remains unsigned and `testing` until native boot/readiness smoke,
repeat-build comparison, production signing, upload, and Catalog publication
complete.

## Upgrade and disposal

No state, Inventory, or Catalog migration is required from 0.4.0. Existing
cached images remain usable. New downloads use the global repository unless
`--mirror`, `--repo`, or `FARROW_REPO` selects another root.

`purge` is deliberately non-interactive and irreversible for deployment disks
and keys. Continue to use confirmed `farrow destroy` when preserving persistent
disks or removing selected nodes.

## Verification boundary

Release source commit `fc85b65ff6a24b0933b56ae1179be9ada2ba91b1` passed the
complete local source gate: module and shell checks, unit and race tests, vet,
Staticcheck, deadcode, errcheck, `govulncheck`, four target builds, simulated
image-pipeline boundaries, installer tests, and exact dependency-license
verification. GoReleaser 2.18.0 also accepted the release configuration.

The tag workflow independently repeats those checks and builds and verifies
every archive, native package, SBOM, formula, installer, release metadata file,
and checksum before the pre-release is published. No new native VM lifecycle
replay or published-image claim is inherited from these source gates.

## Install or upgrade

Download the installer and assets from the
[Farrow 0.5.0 GitHub Release](https://github.com/pgsty/farrow/releases/tag/v0.5.0):

```bash
curl -fLO https://github.com/pgsty/farrow/releases/download/v0.5.0/install.sh
chmod +x install.sh
FARROW_VERSION=0.5.0 ./install.sh
farrow version
farrow doctor
```

The same pre-release includes the Homebrew formula and amd64/arm64 DEB/RPM
packages.
