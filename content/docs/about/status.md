---
title: Platforms and Limits
linkTitle: Platforms and Limits
description: Barn 0.9.1 host requirements, Linux guest compatibility, macOS requirements, and storage limits.
weight: 10
icon: fa-solid fa-laptop-code
---

Barn is built for **local development and testing**. This page helps you choose
a host and understand what each guest type supports.

## Version {#documentation-baseline}

These docs cover **Barn 0.9.1**. See the [installation guide](../../start/installation/)
and [release notes](/blog/release/0.9.1/). Use `barn version` to identify your installed version.
The Linux image catalog updates independently with `barn update`.

[Barn 0.9.1](https://github.com/pgsty/barn/releases/tag/v0.9.1) was released
on 2026-10-22 through the GitHub pre-release channel used by Barn 0.x.
Select `BARN_VERSION=0.9.1` explicitly with the download installer.

The 0.9.1 downloads include the CLI and hosts helper, without `Barn.app`.
Build the native component from source to run macOS guests; see the
[Mac guide](../../start/macos/#install).

Dated checks for earlier releases are preserved in the [validation history](../history/).

## Linux guests

| Host | Architecture | Native acceleration | Minimum QEMU |
|---|---|---|---|
| macOS | arm64 (Apple Silicon), amd64 (Intel) | HVF | 8.2.1 |
| Linux | amd64, arm64 | KVM | 6.2 |
{.platform-table}

Barn builds for all four targets. Most native tests cover macOS arm64 and
Linux amd64, with less coverage on Intel macOS and Linux arm64.

Linux requires usable `/dev/kvm` and NetworkManager or systemd-networkd.
Use `barn doctor` to inspect the host, or `barn setup --dry-run` to preview
dependency and network changes.

The embedded catalog contains **nine image families and 41 artifacts**:
Ubuntu 22.04/24.04/26.04, Debian 12/13, Rocky Linux 8/9/10, and CentOS 7.
See [image versions and compatibility](../../reference/images/) for the exact matrix.

- Linux labs support 1–20 nodes in one private `/24`, with one deployment per user.
- Foreign architectures use QEMU TCG emulation. Rocky Linux 8 arm64 also uses
  TCG on Apple Silicon because its 64 KiB kernel is incompatible with HVF.
- CentOS 7 is a deprecated compatibility image limited to native Linux/amd64.
- `vm_shares` works on Linux hosts. On macOS hosts, its QEMU 9p path protection
  prevents Linux guests from starting. Use SSH to transfer files instead.

## macOS guests {#macos-guests}

`barn mac` requires **Apple Silicon, macOS 27 or later, a logged-in desktop
session, and the Barn.app native component**. Guests run macOS 27. QEMU and
the Linux host network are not required. See [the Mac guide](../../start/macos/).

- The first machine needs about 65 GiB free for the restore image, installed
  base, and initial writes. Downloads support resumption. You can also use a local IPSW.
- At most two macOS VMs can run at once per Mac, including other tools and
  macOS installation. You may keep more stopped machines.
- Each machine has a separate private subnet, SSH keys, login password, and disk.
  Shared folders use VirtioFS, independently of Linux `vm_shares`.
- Clipboard sharing handles plain text, not images or files.
- USB passthrough, snapshots, and suspend/resume are not supported. Apple
  Account sign-in inside a VM may not work reliably.

Use `barn mac doctor` to diagnose the Mac environment. Use `barn mac ls` to inspect
machines. `barn status`, `destroy`, and `purge` operate on the Linux lab only.

## Data and lifecycle

Keep important files backed up outside the lab. Linux `recreate` replaces root and non-persistent
data disks, while `destroy` removes them. Both retain persistent disks. Guest recovery can still reset damaged or unrecognized
data filesystems. [Storage and access](../../start/storage/)
describes these rules in detail.

Mac `recreate` replaces the guest disk with a fresh clone. Mac `destroy`
removes that machine's disk, credentials, and settings. Shared host folders
remain unchanged.

For operational help, see [troubleshooting](../../start/troubleshooting/).
For privileges, SSH credentials, shared folders, and image trust, see
[Security and trust](../security/).
For the source and release validation process, see [contributing and releases](../engineering/).
