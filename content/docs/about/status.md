---
title: Platforms and Limits
linkTitle: Platforms and Limits
description: Barn 0.9.2 host requirements, Linux guest compatibility, macOS requirements, and storage limits.
weight: 10
icon: fa-solid fa-laptop-code
---

Barn is built for **local development and testing**. Use this page to check host requirements and guest capabilities before setting up a lab.

## Version {#documentation-baseline}

This documentation covers **Barn 0.9.2** (see the [Installation Guide](../../start/installation/) and [0.9.2 Release Notes](/blog/release/0.9.2/)). Run `barn version` to check your installed binary; the Linux image catalog updates independently via `barn update`.

- **Pre-release channel**: [Barn 0.9.2](https://github.com/pgsty/barn/releases/tag/v0.9.2) was published on 2026-10-30 on the GitHub pre-release channel used by Barn `0.x`. Pass `BARN_VERSION=0.9.2` explicitly when using the download installer script.
- **Native macOS component**: The Darwin arm64 archive and Apple Silicon Homebrew install include the signed, notarized `Barn.app` alongside the matching CLI and helper. Go and Xcode are not required; see [macOS Guests](../../start/macos/#install).
- **Unreleased changes**: Path, sharing, node-selection, and limit changes from source commit `27f17bb` are documented in [Unreleased Changes](../unreleased/) and are not included in 0.9.2.
- **Historical verification**: Dated test records for earlier releases are archived in [Validation History](../history/).

## Linux guests

| Host | Architecture | Native acceleration | Minimum QEMU |
|---|---|---|---|
| macOS | `arm64` (Apple Silicon), `amd64` (Intel) | HVF | `8.2.1` |
| Linux | `amd64`, `arm64` | KVM | `6.2` |
{.platform-table}

Barn builds release binaries for all four host targets, with primary live-hypervisor test coverage on `darwin/arm64` and `linux/amd64`. On Linux hosts, Barn requires accessible `/dev/kvm` and either NetworkManager or `systemd-networkd`. Run `barn doctor` to inspect host readiness or `barn setup --dry-run` to preview dependency and network setup.

The catalog embedded in Barn 0.9.2, `2026093001`, provides **9 distribution families and 41 image artifacts**: Ubuntu 22.04/24.04/26.04 LTS, Debian 12/13, Rocky Linux 8/9/10, and CentOS 7 (see [Linux Images](../../reference/images/) for exact versions):

- **Unreleased source:** Each user manages one Linux lab in a private RFC1918 `/24`; the separate 20-node ceiling has been removed.
- Foreign-architecture guests run under QEMU TCG software emulation. Rocky Linux 8 `arm64` also uses TCG on Apple Silicon because its 64 KiB page-size kernel is incompatible with Apple HVF.
- CentOS 7 (`el7`) is a `deprecated` compatibility image restricted to native `linux/amd64`.
- **Unreleased source:** `vm_shares` (QEMU Virtio-9p) supports Linux and macOS hosts when QEMU and the guest kernel support 9p. Barn 0.9.2 still requires SSH/SCP/rsync for Linux guests on macOS.

## macOS guests {#macos-guests}

`barn mac` requires **Apple Silicon, macOS 27 or later, an active desktop login session, and the `Barn.app` native component**. Guests run macOS 27 on Apple's `Virtualization.framework` without needing QEMU or the Linux host network (see the [macOS Guests guide](../../start/macos/)):

- **Disk space**: Preparing the first macOS VM requires roughly 65 GiB of free disk space for the cached `.ipsw` restore image, the unbooted base image, and the VM's APFS clone. Downloads support HTTP range resumption, or you can pass a local file via `--ipsw`.
- **Concurrency limit**: Apple's framework allows at most two running macOS VMs at a time per Mac (counting VMs across all apps and any active `.ipsw` base installation); you can keep additional VMs in the `stopped` state.
- **Isolation and sharing**: Each macOS VM gets its own private `/24` NAT subnet, SSH keypair, login password, and APFS copy-on-write disk, plus VirtioFS directory shares (`--share`) and plain-text clipboard sync.
- **Framework boundaries**: USB passthrough, VM snapshots, and suspend/resume are not supported, and Apple Account sign-in inside a virtual machine may be restricted by macOS.

Use `barn mac doctor` and `barn mac ls` to inspect macOS VMs; top-level `barn status`, `destroy`, and `purge` apply only to the Linux lab.

## Data and lifecycle

Keep important work backed up on the host or in version control:

- **Linux lab**: `barn recreate` replaces root disks and non-persistent data disks while retaining `persistent: true` disks; `barn destroy` removes root and non-persistent disks; and `barn up` automatically formats unrecognized or confirmed-corrupt data-disk filesystems during recovery (see [Storage and Access](../../start/storage/)).
- **macOS VMs**: `barn mac recreate` replaces the VM's disk with a fresh clone from the base image, and `barn mac destroy` deletes the VM's disk, keys, and state while leaving shared host directories untouched.

For diagnostics, see [Troubleshooting](../../start/troubleshooting/); for privilege and trust boundaries, see [Security and Trust](../security/); and for build and release workflows, see [Contributing](../engineering/).
