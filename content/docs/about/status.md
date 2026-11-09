---
title: Platforms and Limits
linkTitle: Platforms and Limits
description: Barn 1.1.0 host requirements, Linux guest compatibility, macOS requirements, and storage limits.
weight: 10
icon: fa-solid fa-laptop-code
---

Barn is built for **local development and testing**. Use this page to check host requirements and guest capabilities before setting up a lab.

## Version {#documentation-baseline}

This documentation covers **Barn 1.1.0** (see the [Installation Guide](../../start/installation/) and [1.1.0 Release Notes](/blog/release/1.1.0/)). Run `barn version` to check your installed binary; the Linux image catalog updates independently via `barn update`.

- **Stable channel**: [Barn 1.1.0](https://github.com/pgsty/barn/releases/tag/v1.1.0) was published on 2026-11-09 as a regular GitHub release, so `releases/latest`, the download installer without `BARN_VERSION`, and the Homebrew formula select it; DEB and RPM packages are downloaded from the release. Set `BARN_VERSION=1.1.0` to pin it.
- **Native macOS component**: The Darwin arm64 archive and Apple Silicon Homebrew install include the signed, notarized `Barn.app` alongside the matching CLI and helper. Go and Xcode are not required; see [macOS Guests](../../start/macos/#install).
- **Changes in 1.1.0**: Command-line `--image/-I` and `--arch/-A` overrides select the base image and guest architecture without rewriting `barn.yml`, terminal progress uses one live table for Linux and `barn mac` commands, interrupted online `resize` is detected by `status` and recovered by `up`, `start`, or `resize`, and `barn purge` removes the deployment immediately unless `--ask` is passed. Upgrading from `1.0.0` or `0.9.3` keeps existing VMs; earlier changes are recorded in the [1.0.0 Release Notes](/blog/release/1.0.0/) and [Barn 0.9.3 Changes](../0.9.3-changes/).
- **Historical verification**: Dated test records are archived in [Validation History](../history/) and [Barn 1.1.0 Local Acceptance](../local-acceptance-1.1.0/).

## Linux guests {#linux-guests}

| Host | Architecture | Native acceleration | Minimum QEMU |
|---|---|---|---|
| macOS | `arm64` (Apple Silicon), `amd64` (Intel) | HVF | `8.2.1` |
| Linux | `amd64`, `arm64` | KVM | `6.2` |
{.platform-table .wide .expand}

Barn builds release binaries for all four host targets, with primary live-hypervisor test coverage on `darwin/arm64` and `linux/amd64`. On Linux hosts, Barn requires accessible `/dev/kvm` and either NetworkManager or `systemd-networkd`. Run `barn doctor` to inspect host readiness or `barn setup --dry-run` to preview dependency and network setup.

The catalog embedded in Barn 1.1.0, revision `2026110502`, provides **9 distribution families and 17 image artifacts** with `u24:stable` as the default: Ubuntu 22.04/24.04/26.04 LTS, Debian 12/13, Rocky Linux 8/9/10, and CentOS 7 (see [Linux Images](../../reference/images/) for exact versions):

- Each user manages one Linux lab in a private RFC1918 `/24`; the node count is limited only by the subnet's usable addresses and host resources.
- Foreign-architecture guests run under QEMU TCG software emulation. Rocky Linux 8 `arm64` also uses TCG on Apple Silicon because its 64 KiB page-size kernel is incompatible with Apple HVF.
- CentOS 7 (`el7`) is a `deprecated` compatibility image restricted to native `linux/amd64`.
- `vm_shares` (QEMU Virtio-9p) supports Linux and macOS hosts when QEMU and the guest kernel support 9p. SSH/SCP/rsync remain alternatives when a guest kernel lacks 9p.

## macOS guests {#macos-guests}

`barn mac` requires **Apple Silicon, macOS 27 or later, an active desktop login session, and the `Barn.app` native component**. Guests run macOS 27 on Apple's `Virtualization.framework` without needing QEMU or the Linux host network (see the [macOS Guests guide](../../start/macos/)):

- **Disk space**: Preparing the first macOS VM requires roughly 65 GiB of free disk space for the cached `.ipsw` restore image, the unbooted base image, and the VM's APFS clone. Downloads support HTTP range resumption, or you can pass a local file via `--ipsw`.
- **Concurrency limit**: Apple's framework allows at most two running macOS VMs at a time per Mac (counting VMs across all apps and any active `.ipsw` base installation); you can keep additional VMs in the `stopped` state.
- **Isolation and sharing**: Each macOS VM gets its own private `/24` NAT subnet, SSH keypair, login password, and APFS copy-on-write disk, plus VirtioFS directory shares (`--share`) and plain-text clipboard sync.
- **Framework boundaries**: USB passthrough, VM snapshots, and suspend/resume are not supported, and Apple Account sign-in inside a virtual machine may be restricted by macOS.
- **Damaged Mac state**: A malformed recovery journal stops `barn mac image ls`, the space estimate in `barn mac doctor`, and image pruning until it is repaired. One unreadable machine state stops `barn mac ls`, while the other machines stay usable by name.

Use `barn mac doctor` and `barn mac ls` to inspect macOS VMs; top-level `barn status`, `destroy`, and `purge` apply only to the Linux lab.

## Data and lifecycle {#data-and-lifecycle}

Keep important work backed up on the host or in version control:

- **Linux lab**: `barn recreate` replaces root disks and non-persistent data disks while retaining `persistent: true` disks, and a whole-deployment `recreate` refuses an inventory that omits an existing node; `barn destroy` removes root and non-persistent disks. During recovery, `barn up` formats a data disk that carries no signature and resets an existing ext4 or XFS filesystem only when the checker reports recognized corruption. A partition table, a signature without a UUID, unsupported filesystem features, or an unknown checker failure keeps the data and reports a warning (see [Storage and Access](../../start/storage/)).
- **macOS VMs**: `barn mac recreate` replaces the VM's disk with a fresh clone from the base image, and `barn mac destroy` deletes the VM's disk, keys, and state while leaving shared host directories untouched.

For diagnostics, see [Troubleshooting](../../start/troubleshooting/); for privilege and trust boundaries, see [Security and Trust](../security/); and for build and release workflows, see [Contributing](../engineering/).
