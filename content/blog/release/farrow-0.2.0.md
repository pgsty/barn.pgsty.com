---
title: "Farrow 0.2.0: selected convergence and release integrity"
linkTitle: Farrow 0.2.0
description: VPN-aware network preflight, truly selected scale-out, committed-state integrations, checksum-verified multi-platform artifacts, and the 0.1.0 upgrade boundary.
date: 2026-09-01
weight: 2
categories: [Release]
tags: [Farrow 0.2.0, QEMU, macOS, Linux, Release, Supply Chain]
icon: fa-solid fa-rocket
---

Farrow 0.2.0 was the public pre-1.0 release superseded by 0.3.0. It keeps the Pigsty
inventory and on-disk deployment format introduced by 0.1.0 while fixing the
network and selected-convergence boundaries found during the final native
replay.

## What changed

- A less-specific VPN exclusion such as `10.0.0.0/8` no longer blocks
  Farrow's owned `10.10.10.0/24`; equal or more-specific foreign routes,
  overlapping interfaces, occupied addresses, and a missing owned route still
  fail closed.
- `farrow up <node>` downloads and prepares only the selected node. Desired
  inventory peers without state appear as `absent`; SSH/hosts/provisioning,
  UUID and port allocation, lifecycle commands, and persistent-disk checks use
  the committed node set without losing future scale-out intent.
- New guests write `# farrow-deployment-host` and remove both that marker and
  the released `# farrow-project-host` marker before adding current host rows.
- Command cancellation, structured output, confirmation, `reload`, diagnostic
  redaction, installer retention, and the smaller dependency graph from the
  unpublished intermediate work are included directly in 0.2.0.

## Native and release evidence

The exact source commit completed a macOS arm64/HVF replay with MonoProxy
active: selected `u24-1` create/SSH/stop/start, incremental cached `el9-1`
create, two-node SSH, five explicit absent peers, and whole destroy all passed.
On Ubuntu 26.04 amd64/KVM, the current Linux binary audited an existing
four-node deployment and reached its control guest without mutation.

Local `make check`, source CI, and the complete packaging workflow passed. The
tag workflow built four archives, amd64/arm64 DEB and RPM packages, SPDX SBOMs,
Homebrew formula, installer, checksums, and release metadata. GitHub Actions uploads those verified CI outputs to a draft for review before
public release, without a separate application signature or provenance bundle.

The signed image Catalog remains revision `2026082903` with 9 families and 27
architecture artifacts. The default repository remains
`https://repo.pigsty.cc/farrow`; `repo.pgsty.com/farrow` is an independently
verified source/alternate endpoint, not the compiled default.

## Install or upgrade

Download `install.sh` and the assets from the
[Farrow 0.2.0 GitHub Release](https://github.com/pgsty/farrow/releases/tag/v0.2.0):

```bash
chmod +x install.sh
FARROW_VERSION=0.2.0 ./install.sh
farrow version
farrow doctor
```

0.1.0 deployment state remains readable. Run `farrow status` while retained
VMs are live to converge any pre-release process-birth identity. Existing
guests adopt the new `/etc/hosts` marker when recreated.

Because Farrow is still below 1.0, GitHub labels 0.2.0 as a pre-release.
