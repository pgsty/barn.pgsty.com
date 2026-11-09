---
title: "Running Barn from Windows"
linkTitle: "Windows host boundary"
description: "Why a Linux host remains necessary, what WSL2 must prove, and what a native Windows backend would require."
date: 2026-11-08T10:00:00+08:00
weight: 80
categories: [Design]
tags: [Windows, WSL, QEMU]
icon: fa-solid fa-laptop-code
lastmod: 2026-11-08
---

Barn's current host profiles and release binaries cover macOS and Linux on `amd64` and `arm64`. There is no native Windows Barn release. A Windows user can operate Barn through a Linux host; WSL2 and a nested Linux VM are candidates for bringing that host onto the Windows machine.

This assessment was reviewed on **2026-11-08**. The WSL2 and Hyper-V paths below still require a complete Barn lifecycle test before they can become supported installation guides. The current platform contract is in [platforms and limits](/docs/about/status/) and [`internal/platform`](https://github.com/pgsty/barn/blob/main/internal/platform/platform.go).

## Choose where Barn runs {#host-options}

| Host environment | What it reuses | What must be established |
|---|---|---|
| Remote Linux/KVM host | Existing Linux Barn binary and host integration | SSH access, suitable resources, and the normal Linux host checks |
| WSL2 distribution | Linux binary, QEMU, OpenSSH, and Linux filesystem | Nested KVM, systemd, bridge helper, private network, and Windows-to-guest access |
| Full Linux VM on Hyper-V | A conventional Linux installation and network manager | Nested virtualization, `/dev/kvm`, resources for both VM layers, and access from Windows |
| Native Windows/QEMU | QEMU's WHPX accelerator | A new Barn host backend, network integration, installer, and acceptance matrix |
{.wide .expand}

For a local experiment, WSL2 is the first candidate because it can reuse the Linux implementation. A remote Linux/KVM host remains the direct path when nesting is unavailable or when performance matters. Docker Desktop adds a VM/container boundary around the host functions Barn needs; it is outside this proposed installation path.

## WSL2 has two separate configuration scopes {#wsl-config}

WSL2-wide VM options belong in `%UserProfile%\.wslconfig` on Windows. Per-distribution boot settings, including systemd, belong in `/etc/wsl.conf` inside Linux. Microsoft's [configuration reference](https://learn.microsoft.com/en-us/windows/wsl/wsl-config) describes the distinction and the `nestedVirtualization` option. A configured option still needs a usable KVM device and a working launch on the actual machine.

Keep `BARN_HOME`, cached images, and guest disks in the WSL Linux filesystem, such as the default `~/.barn`. Microsoft's [filesystem guidance](https://learn.microsoft.com/en-us/windows/wsl/filesystems) recommends Linux filesystem storage for Linux workloads. The outer WSL virtual disk stores the Linux filesystem; Barn's inner qcow2 files remain separate guest disks managed by Barn.

PowerShell can invoke the Linux CLI through `wsl.exe`, but the state, SSH configuration, host shares, and private bridge still belong to that Linux environment.

## Acceptance before installation advice {#acceptance}

A WSL2 or Hyper-V Linux candidate should pass these checks in order:

1. Confirm the Linux init/network manager works and the current user can access `/dev/kvm`. Start a small QEMU probe with KVM; checking only the device path is insufficient.
2. Run `barn setup --dry-run` to inspect dependencies and network changes. Then verify the installed `qemu-bridge-helper`, its distribution ownership and permissions, and the `barn0` bridge using Barn's normal Linux checks.
3. In a disposable lab, boot a native-architecture guest and reach SSH. Verify outbound traffic, host-to-guest access, and communication between two guests on the private subnet.
4. Test the actual Windows access path. Check the management endpoint and any required service separately from reachability of the private subnet.
5. Stop and start the guests, restart the outer Linux environment, and verify recovery, persistent disks, and cleanup of Barn-owned network resources.
{.steps}

Windows-to-WSL localhost forwarding or [mirrored networking](https://learn.microsoft.com/en-us/windows/wsl/networking) does not establish routing to the nested guest subnet by itself. Record the chosen route or tunnel and its firewall requirements with the test result. For a full Hyper-V Linux VM, [nested virtualization](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/nested-virtualization) also depends on the outer host configuration.

Barn selects TCG for foreign guest architectures and specific image compatibility cases. It does not silently substitute TCG when a normal native KVM launch fails. A WSL installation without working native acceleration therefore cannot be advertised as a normal Linux Barn host.

## A native Windows backend is a separate implementation {#native-backend}

QEMU exposes hardware acceleration through [WHPX](https://www.qemu.org/docs/master/system/whpx.html). Barn would still need to implement the host contracts around that accelerator:

| Area | Current dependency | Windows work |
|---|---|---|
| Platform and packaging | Darwin/Linux profiles and release targets | Windows profile, dependency detection, binaries, and installer |
| Process identity and recovery | POSIX process evidence and signals | Windows process handles, identity checks, cancellation, and recovery |
| State and locks | Unix filesystem metadata and `flock` | Equivalent locking, permissions, and atomic state handling |
| QMP and host shares | Unix sockets, inherited directory descriptors, Virtio-9p | Supported transports and validated sharing semantics |
| Private network | `barn0`, bridge helper, and Linux network manager | A Windows backend with explicit privilege and firewall ownership |
{.wide .expand}

The implementation boundaries are visible in [`internal/process`](https://github.com/pgsty/barn/tree/main/internal/process), [`internal/lock`](https://github.com/pgsty/barn/tree/main/internal/lock), [`internal/hostshare`](https://github.com/pgsty/barn/tree/main/internal/hostshare), and [`internal/network`](https://github.com/pgsty/barn/tree/main/internal/network). A wrapper around the existing binary cannot supply those contracts.

Vagrant illustrates why provider-specific behavior must stay explicit: its [Hyper-V limitations](https://developer.hashicorp.com/vagrant/docs/providers/hyperv/limitations) state that Vagrantfile network settings are ignored and the user selects an existing virtual switch. Barn's fixed-address lab needs its own network guarantee before Windows can join the supported host matrix.
