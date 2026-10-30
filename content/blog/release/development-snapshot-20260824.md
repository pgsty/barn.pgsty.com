---
title: "Development snapshot: the Go 1.27 product surface"
linkTitle: 2026-08-24 development snapshot
description: Quick and four-node private semantics, schema-3 owned profiles, Pigsty inventory integration, persistence, state migration, and verified release mechanisms.
date: 2026-08-24
weight: 120
categories: [Development]
tags: [Prototype, QEMU, Pigsty]
icon: fa-solid fa-flask
---

> [!NOTE]
> Pre-Barn historical archive (`Piglet`, 2026-08-24). At this snapshot there was no public release tag, signed production artifact, or package repository, and all embedded image records were marked `testing`. For current Barn behavior and support status, see the [documentation](/docs/) and [status page](/docs/about/status/).

The 2026-08-24 source snapshot turned the initial QEMU prototype into a structured Go 1.27 VM manager with zero-configuration Quick mode, fixed-IP private labs, 13 built-in profiles, Pigsty inventory generation, persistent data disks, schema migration, and reproducible release packaging.

## One native runtime

Piglet drives QEMU directly through HVF on macOS and KVM on Linux, running QEMU as the invoking user without falling back to TCG emulation or accepting arbitrary pass-through QEMU flags. It validates image digests and `.qcow2` headers, generates pure-Go NoCloud `cidata` seed images, checks QMP and process identity, verifies SSH readiness, and records atomic state updates, journals, and event logs.

## Quick mode on both Tier-1 hosts

Zero-YAML Quick mode runs on macOS `arm64` and Linux `amd64`, provisioning a single `meta` guest (`dba` user, 2 vCPU, 4 GiB RAM, 64 GiB root disk, sparse 64 GiB `/data` disk, user-mode NAT, SSH, and four localhost port forwards) and supporting `plan`, `up`, `status`, `ssh`/`exec`, `stop`/`start`/`restart`, drift detection, guarded `recreate`/`destroy`, `--no-wait`, persistent disk retention, key rotation, logs, repair, and redacted debug bundles.

## Private labs and host networking

Private mode adds host-network `preflight`, `status`, `install`, and `uninstall` across both Tier-1 host families:
- **macOS** uses pinned `socket_vmnet` v1.2.2 in `host` mode by default (with `shared`/FD mode also tested).
- **Linux** uses a reversible `systemd-networkd` / NetworkManager / `qemu-bridge-helper` transaction.

Both platforms keep QEMU unprivileged and block network uninstallation while a lab lease is active. Operators can replace the default `10.10.10.0/24` subnet with another explicit RFC 1918 `/24` subnet, moving the profile, host network, lease, node addresses, and Pigsty inventory together.

Four-node `full` and MinIO runs on both Tier-1 platforms verified fixed IPs, control-node lateral SSH, management internet access, disk identity, `stop`/`start` persistence, crash recovery, 30/30 soak cycles, and 16-disk MinIO storage layouts.

## Schema-3 profiles and Pigsty inventory integration

The 13 embedded schema-3 profiles define 85 nodes using the `dba` account—standard nodes carry a 128 GiB `/data` disk, while MinIO nodes carry four 32 GiB disks. `piglet pigsty inventory` reads a Pigsty source tree, validates host/VIP/admin/service addresses, rebases custom subnets, and writes mode-`0600` inventory files with ownership markers, while `pigsty-vm` exposes the same lifecycle through typed environment variables.

## Persistence, schema upgrades, and automation

- **Persistent disks**: disks marked `persistent: true` survive ordinary `destroy` and compatible `recreate` runs; deleting them requires typing a confirmation phrase in a TTY or passing `destroy --force --delete-persistent --yes-delete-persistent`. Project key cleanup defaults to dry-run and requires `project purge-keys --yes`.
- **State migration**: schema `0 -> 1` upgrades require stopped nodes and no active lease, creating a backup before applying an atomic update via `project upgrade-state --dry-run|--yes`.
- **Automation surface**: includes node selectors, `--no-wait`, structured JSON responses, typed exit codes, shell completion, managed SSH and `/etc/hosts` blocks, per-node logs, and redacted support bundles.

## Images and release packaging

The embedded image matrix covers `el9`, `el10`, `d12`, `d13`, `u22`, `u24`, and `u26` across `amd64` and `arm64` (7/7 booted per architecture; `el8` was excluded from the initial matrix before being normalized in later Barn releases). The build toolchain produces and verifies four platform archives, a Homebrew formula, Linux `amd64`/`arm64` DEB and RPM packages, SHA-256 checksums, SPDX SBOMs, and Cosign/SLSA signing test fixtures across two-run reproducibility checks.

## Follow-up completed in RC6 and Barn 0.x

Because catalog schema-3 and inventory changes landed after the initial `full`/MinIO runs, exact-profile native replays, custom-subnet `/etc/hosts` publishing, and `storage.data_root` / `ssh.wait_timeout` wiring were completed the following day in the [2026-08-25 RC6 candidate](rc6-owner-scoped-20260825/), before the project simplified its model around a single Pigsty-native `barn.yml` inventory in Barn `0.1.0`+. See the [tutorial](/docs/start/tutorial/), [architecture guide](/docs/about/design/), and [status page](/docs/about/status/) for current Barn behavior.
