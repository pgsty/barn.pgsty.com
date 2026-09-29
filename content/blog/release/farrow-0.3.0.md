---
title: "Farrow 0.3.0: explicit catalogs and actionable readiness"
linkTitle: Farrow 0.3.0
description: Explicit image-catalog updates, per-node bootstrap diagnostics, native guest interface names, and a smaller CLI.
date: 2026-09-02
weight: 2
categories: [Release]
tags: [Farrow 0.3.0, QEMU, Catalog, Readiness, Release]
icon: fa-solid fa-rocket
---

Farrow 0.3.0 was the public pre-1.0 release superseded by 0.4.0. It removes implicit
Catalog refreshes, turns guest bootstrap failures into actionable per-node
results, and simplifies the CLI without changing the Pigsty Inventory or
fixed-IP deployment model.

## What changed

- `up`, `plan`, and ordinary `image` commands use one active local Catalog
  snapshot and never fetch Catalog metadata implicitly. `farrow update`
  explicitly fetches the configured repository; `image sync` activates an
  exact URL or file.
- Guest bootstrap writes an atomic failure stage. Partial operations report
  every failed node, stage, and error, and readiness failures point directly to
  `farrow logs <node>`.
- Already-running guests can be rechecked without restarting QEMU. A partial
  lifecycle still rebuilds the SSH client configuration from every committed
  node.
- Netplan matches deterministic MAC addresses without renaming interfaces.
  `vm_disks[].fs: auto` prefers XFS and falls back to ext4 when necessary.
- The redundant `ss` command and ambiguous root/flag shorthands are removed.
  `image reset` replaces `reset-manifest`, which remains an alias.

## Verification boundary

Source commit `da6d02426da93c677c94c67fec4eb4fcecf4766a` passed the complete local
source gate and a full GoReleaser snapshot: unit and race tests, vet,
Staticcheck, `govulncheck`, four target builds, image-pipeline and installer
boundaries, archive/package parity, dependency licenses, SBOMs, and native
Linux package verification. The tag workflow repeated those checks before the
Release was made public.

This release does not claim a new native VM replay. The dated macOS arm64/HVF
and Ubuntu amd64/KVM evidence remains listed on the [Status](../../../docs/about/status/)
page; source, package, release, and native-host evidence remain separate gates.

## Install or upgrade

Download the installer and assets from the
[Farrow 0.3.0 GitHub Release](https://github.com/pgsty/farrow/releases/tag/v0.3.0):

```bash
curl -fLO https://github.com/pgsty/farrow/releases/download/v0.3.0/install.sh
chmod +x install.sh
FARROW_VERSION=0.3.0 ./install.sh
farrow version
farrow doctor
```

Homebrew formula and amd64/arm64 DEB/RPM packages are attached to the same
pre-release. Existing 0.1/0.2 deployment and Catalog state remains readable;
Catalog refresh is now always explicit.
