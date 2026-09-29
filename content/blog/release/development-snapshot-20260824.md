---
title: "Development snapshot: the Go 1.27 product surface"
linkTitle: 2026-08-24 development snapshot
description: Quick and four-node private semantics, schema-3 owned profiles, Pigsty inventory integration, persistence, state migration, and verified release mechanisms.
date: 2026-08-24
weight: 10
categories: [Development]
tags: [Go 1.27, Quick, Private, Pigsty, QEMU, macOS, Linux]
icon: fa-solid fa-flask
---

> [!CAUTION]
> Pre-Barn historical record. Names, commands, paths, hashes, and claims on
> this page describe the predecessor snapshot only. Use the current
> [Barn status](/docs/about/status/) and guides for present behavior.

Piglet's 2026-08-24 source snapshot has moved well beyond an initial QEMU
spike. It now presents one coherent local-VM product: zero-configuration Quick,
fixed-address private labs, 13 Piglet-owned profiles, an audited Pigsty
inventory boundary, explicit persistence/state migration, diagnostics, and a
reproducible release toolchain.

It is still a development snapshot—not a stable release.

> [!NOTE]
> This page is a historical 2026-08-24 snapshot. A later predecessor candidate
> is archived separately; neither page is current Barn release evidence.

> [!WARNING]
> There is no public v1.0 tag, signed production artifact, Homebrew tap, or
> DEB/RPM repository. All embedded image records remain `testing`. Local
> packages and signature round trips prove mechanisms, not production custody.

## One native runtime

Piglet directly drives native QEMU through HVF on macOS and KVM on Linux. It
owns strict specification resolution, image/qcow2 verification, pure-Go NoCloud
CIDATA, QMP/process identity, SSH readiness, atomic state, journals, events,
repair, and bounded deletion. QEMU runs as the invoking user and never silently
falls back to TCG.

There is no second provider/runtime path and no arbitrary QEMU-argument escape.

## Quick on both Tier-1 hosts

The retained Go 1.27 Quick runs cover the public no-YAML path on macOS arm64 and
Linux amd64. The contract is `meta`/`dba`, 2 vCPU, 4 GiB memory, 64 GiB root,
sparse 64 GiB `/data`, user NAT, SSH, and four loopback forwarding conventions.

The product supports plan, up, status, SSH/exec, stop/start/restart, drift
classification, guarded recreate/destroy, no-wait, persistent-disk retention,
key retirement, logs, repair, and redacted debug bundles.

Those forwards do not install applications. Pigsty/PostgreSQL bootstrap remains
a separate integration gate.

## Private labs and host networking

Private mode now has public preflight/status/install/uninstall flows on both
Tier-1 host families. macOS uses pinned `socket_vmnet` v1.2.2 with host mode by
default and evidence-backed shared/FD paths. Linux uses a reversible
systemd-networkd/NetworkManager/bridge-helper transaction. Both keep QEMU
unprivileged and block uninstall while the global lease is active.

The default `10.10.10.0/24` can be replaced by one explicit canonical RFC1918
`/24`. Profile, host install, lease, state, node addresses, and Pigsty inventory
must move together. No random collision escape is chosen.

Retained four-node `full` and MinIO runs exercised fixed IPs, control-only
lateral SSH, management internet, storage identity, stop/start persistence, and
clean destroy on both Tier-1 paths. Earlier runs also cover crash recovery and
30/30 soak. The MinIO profile runs validate 16 VM data disks, not the MinIO
application.

## Schema-3 owned profiles and Pigsty inventory

The 13 embedded profiles contain 85 nodes, all using `dba`. Ordinary nodes have
one 128 GiB `/data`; MinIO nodes have four 32 GiB disks. Catalog schema 3 owns
scalability, image policy, and Pigsty inventory binding, with direct and
`build_subset` modes.

`piglet pigsty inventory` reads a real Pigsty source tree, classifies and
validates host/VIP/admin/service address semantics, rebases a coordinated custom
subnet, and can atomically publish a mode-0600 marker-owned output. `pigsty-vm`
exposes the same profile, network, lifecycle, and inventory contract through a
small typed environment.

The wrapper has no provider fallback. Operational rollback means a prior
verified Piglet artifact plus matching state backup.

## Persistence, upgrade, and automation

Disks marked `persistent: true` survive ordinary destroy and compatible
recreate. The current safety contract requires an independent TTY phrase or
`destroy --force --delete-persistent --yes-delete-persistent`; project keys
have a separate default-dry-run `project purge-keys --yes` boundary.

Schema 0→1 migration is stopped-only, no-lease, backup-first, atomic, and
explicit through `project upgrade-state --dry-run|--yes`. Newer schemas are
refused rather than downgraded.

Private node selectors, `--no-wait`, stable JSON responses, typed exit classes,
shell completion, SSH config, marker-owned hosts blocks, per-node logs, and
redacted support bundles complete the current operator/automation surface.

## Images and release mechanisms

The formal embedded image set is `el9`, `el10`, `d12`, `d13`, `u22`, `u24`,
and `u26` on both Tier-1 native architectures. Retained matrix records report
7/7 per architecture; EL8 was retired from v1 because its arm64 kernel cannot
satisfy the tested native HVF contract. The entries remain `testing` pending a
production image channel and custody.

The source tree can build and verify four native archives, a Homebrew formula,
Linux amd64/arm64 RPM and DEB packages, checksums, SPDX SBOMs, a combined
release assembly, and Cosign signature/SLSA-provenance positive and tamper
tests. Isolated package install/verify/remove and two-run reproducibility passed
for the tested snapshots. The checked-in release workflow has not executed for
a real tag.

## Evidence must follow exact bytes

At this snapshot, catalog schema 3 and inventory integration had changed the
checked-in profile/resolved digests after the retained `full`/MinIO runs, so
exact-current native refresh was still required. Custom-subnet hosts
publishing, applied `storage.data_root`/`ssh.wait_timeout`, and generic
Quick users were also open.

RC6 later closed those implementation and exact-profile gaps. Historical native
runs remain valid only for the bytes and behavior they actually exercised.

## What remains before v1.0

The snapshot's exact-profile, Pigsty-bootstrap, and Rocky 9.8 private-host gates
were later exercised. The current remaining gates are production
image/manifest/release custody, durable runner ownership, literal reboot
recovery, Tier-2 native smoke, published package consumption, and a real
signed/attested tag-bound release.

See the current [tutorial](/docs/start/tutorial/),
[design](/docs/about/design/), and [status](/docs/about/status/) for the
maintained boundary.
