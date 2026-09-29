---
title: Platforms and Limits
linkTitle: Platforms and Limits
description: Barn 0.9.0 host requirements, Linux guest compatibility, macOS requirements, and storage limits.
weight: 10
icon: fa-solid fa-laptop-code
---

Barn is built for **local development and testing**. This page helps you choose
a host and understand what each guest type supports.

## Version {#documentation-baseline}

These docs cover **Barn 0.9.0**. Install the [release](../../start/installation/),
check `barn version`, and read the [release notes](/blog/release/0.9.0/) for changes.
The Linux image catalog updates independently with `barn update`.

## Linux guests

| Host | Architecture | Native acceleration | Minimum QEMU |
|---|---|---|---|
| macOS | arm64 (Apple Silicon), amd64 (Intel) | HVF | 8.2.1 |
| Linux | amd64, arm64 | KVM | 6.2 |
{.platform-table}

Barn builds for all four targets. The principal native test paths are macOS
arm64 and Linux amd64; Intel macOS and Linux arm64 have narrower validation
coverage. Linux also requires usable `/dev/kvm` and NetworkManager or
systemd-networkd. `barn doctor` checks the host; `barn setup --dry-run` shows
the dependency and network changes for your machine.

The embedded catalog contains **nine image families and 41 artifacts**:
Ubuntu 22.04/24.04/26.04, Debian 12/13, Rocky Linux 8/9/10, and CentOS 7.
See [image versions and compatibility](../../reference/images/) for the exact matrix.

- Linux labs support 1–20 nodes in one private `/24`, with one deployment per user.
- Foreign architectures use QEMU TCG emulation. Rocky Linux 8 arm64 also uses
  TCG on Apple Silicon because its 64 KiB kernel is incompatible with HVF.
- CentOS 7 is a deprecated compatibility image limited to native Linux/amd64.
- `vm_shares` works on Linux hosts. For Linux guests on macOS, use SSH file
  transfer: the guarded QEMU 9p sharing path cannot start those nodes.

## macOS guests {#macos-guests}

`barn mac` requires **Apple Silicon, macOS 27 or later, a logged-in desktop
session, and the Barn Mac native component**. Guests run macOS 27. QEMU and
the Linux host network are not required. See [the Mac guide](../../start/macos/).

- The first machine needs about 65 GiB free for the restore image, installed
  base, and initial writes. Downloads are resumable; a local IPSW also works.
- At most two macOS VMs can run at once per Mac, including other tools and
  macOS installation. You may keep more stopped machines.
- Each machine has a separate private subnet, SSH keys, login password, and disk.
  Shared folders use VirtioFS, independently of Linux `vm_shares`.
- Clipboard sharing handles plain text, not images or files.
- USB passthrough, snapshots, and suspend/resume are not supported. Apple
  Account sign-in inside a VM may not work reliably.

Use `barn mac doctor` for Mac-specific diagnostics and `barn mac ls` to inspect
machines. `barn status`, `destroy`, and `purge` operate on the Linux lab only.

## Data and lifecycle

Keep important files backed up outside the lab. Linux root and non-persistent
data disks are replaced by `recreate` and removed by `destroy`. Persistent
disks survive ordinary destruction, but damaged or unrecognized data filesystems
can still be reset during guest recovery. [Storage and access](../../start/storage/)
describes these rules in detail.

Mac `recreate` replaces the guest disk with a fresh clone. Mac `destroy`
removes that machine's disk, credentials, and settings; shared host folders
remain unchanged.

For operational help, see [troubleshooting](../../start/troubleshooting/).
For the source and release validation process, see [contributing and releases](../engineering/).
