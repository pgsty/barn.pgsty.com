---
title: "Farrow 0.4.0: one command, working data disks, one voice"
linkTitle: Farrow 0.4.0
description: A first run that is one command, a default data disk that works on every image, readiness failures that name the cause, and one output style across the CLI.
date: 2026-09-02
weight: 1
categories: [Release]
tags: [Farrow 0.4.0, QEMU, UX, Release]
icon: fa-solid fa-rocket
---

Farrow 0.4.0 was the public pre-1.0 release superseded by 0.5.0. It makes the first run one
command, fixes the default data disk on Debian and Ubuntu images, and gives every
command the same output style. The Pigsty Inventory format, the fixed-IP
deployment model, the state layout, and the embedded Catalog revision
`2026082903` are unchanged.

## What changed

- On a terminal, `farrow up` runs `farrow setup` itself when the fixed-IP
  network has never been installed, shows the setup plan, asks before the
  privileged step, and then continues. `farrow init` points at `farrow up`.
- `vm_disks[].fs` defaults to `auto`: a blank disk is formatted XFS when the
  guest has `mkfs.xfs` and ext4 otherwise, the same choice Pigsty's Vagrant flow
  makes. The old `xfs` default failed on Debian and Ubuntu images, which ship
  without xfsprogs. Deployments created with the old default are not reported
  as drift and their persistent disks stay compatible.
- The guest error marker carries the failing command's last message, so `up`
  reports `guest bootstrap failed during data-disks: xfs requested but mkfs.xfs
  is unavailable` instead of an exit status.
- Lifecycle commands and `status` print a node table and, after `up`, a
  `next: farrow ssh <node>` hint. `plan` and `validate` print one line when
  nothing changes; `image list`, `network status`, `doctor`, and preflight
  errors use plain sentences without machine codes; `spec hash` and other
  internals moved to `--json`. Errors about an unknown node list the nodes.
- `farrow ssh <node> -- 'df -h /data; id'` passes the remote command exactly as
  OpenSSH does.

## Upgrading

A d13, d12, or Ubuntu node created by 0.3.0 or earlier whose `/data` never
mounted needs one `farrow recreate <node>`; the disk is then formatted ext4 on
those images and XFS on Enterprise Linux images. Automation that runs `up` on an
unprepared host without a terminal still needs `farrow setup --yes` first.

## Verification boundary

Source commit `8ecb8476c7dbc934d8cbbee935ac53884d00fcdb` passed the complete
local source gate: unit and race tests, vet, Staticcheck, deadcode, errcheck,
`govulncheck`, shell and module checks, four target builds, the image-pipeline
and installer boundaries, and dependency licenses. The tag workflow repeated
those checks and built and verified every archive, native package, SBOM, and
the installer before the Release was made public.

The new first-run path (`up` running `setup`) is covered by unit tests and was
not replayed on a fresh host before this release. The dated macOS arm64/HVF and
Ubuntu amd64/KVM evidence remains listed on the
[Status](../../../docs/about/status/) page; source, package, release, and
native-host evidence remain separate gates.

## Install or upgrade

Download the installer and assets from the
[Farrow 0.4.0 GitHub Release](https://github.com/pgsty/farrow/releases/tag/v0.4.0):

```bash
curl -fLO https://github.com/pgsty/farrow/releases/download/v0.4.0/install.sh
chmod +x install.sh
FARROW_VERSION=0.4.0 ./install.sh
farrow version
farrow doctor
```

Homebrew formula and amd64/arm64 DEB/RPM packages are attached to the same
pre-release. Existing deployment and Catalog state remains readable.
