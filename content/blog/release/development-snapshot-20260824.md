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

> [!NOTE]
> This pre-Barn snapshot preserves Piglet's design, versions, commands, paths, digests, and validation results as they stood at the time. For current Barn behavior, see the [documentation](/docs/) and [Barn status](/docs/about/status/).

Piglet's 2026-08-24 source snapshot extends the initial QEMU prototype into a local VM product.
It provides zero-configuration Quick, fixed-address private labs, 13 Piglet-owned profiles, and audited Pigsty inventory integration.
It also provides explicit persistence, state migration, diagnostics, and a reproducible release toolchain.

The 2026-08-24 snapshot had not reached a stable release. A later predecessor candidate is archived separately; both records preserve historical evidence.

> [!WARNING]
> At this snapshot, there was no public v1.0 tag, signed production artifact, Homebrew tap, or DEB/RPM repository.
> All embedded image records remained `testing`. Local packages and signature round trips verified the mechanisms but did not establish production custody.

## One native runtime

Piglet directly drives native QEMU through HVF on macOS and KVM on Linux.
It strictly resolves specifications and verifies images/qcow2 files, QMP/process identity, and SSH readiness.
It also manages pure-Go NoCloud CIDATA, atomic state updates, journals, events, repair, and deletion within defined limits.
QEMU runs as the invoking user and never silently falls back to TCG.

The system has no second runtime provider and does not accept arbitrary QEMU arguments.

## Quick on both Tier-1 hosts

The retained Go 1.27 Quick runs cover the public no-YAML path on macOS arm64 and
Linux amd64. The contract is `meta`/`dba`, 2 vCPU, 4 GiB memory, 64 GiB root,
sparse 64 GiB `/data`, user NAT, SSH, and four loopback forwarding conventions.

The product supports plan, up, status, SSH/exec, stop/start/restart, drift
classification, guarded recreate/destroy, no-wait, persistent-disk retention,
key retirement, logs, repair, and redacted debug bundles.

These forwards do not install applications. Pigsty/PostgreSQL bootstrap requires separate integration validation.

## Private labs and host networking

Private mode provides public preflight, status, install, and uninstall operations on both Tier-1 host families.
macOS uses pinned `socket_vmnet` v1.2.2 with host mode by default. Shared/FD paths also have validation records.
Linux uses a reversible systemd-networkd/NetworkManager/bridge-helper transaction.
Both host families keep QEMU unprivileged and block uninstall while the global lease is active.

The default `10.10.10.0/24` can be replaced by one explicit canonical RFC1918
`/24`. Profile, host install, lease, state, node addresses, and Pigsty inventory
must move together. The system does not select a random subnet to avoid a collision.

Retained four-node `full` and MinIO runs covered both Tier-1 platforms.
They verified fixed IPs, control-only lateral SSH, management internet access, storage identity, stop/start persistence, and complete destruction.
Earlier runs also covered crash recovery and 30/30 soak. The MinIO profile runs validated 16 VM data disks but did not validate the MinIO application.

## Schema-3 owned profiles and Pigsty inventory

The 13 embedded profiles contain 85 nodes, all using `dba`. Ordinary nodes have
one 128 GiB `/data`; MinIO nodes have four 32 GiB disks. Profile catalog schema 3 owns
scalability, image policy, and Pigsty inventory binding, with direct and
`build_subset` modes.

`piglet pigsty inventory` reads a real Pigsty source tree and classifies and validates host/VIP/admin/service address semantics.
It coordinates custom-subnet rebasing and can atomically publish output with mode 0600 and an ownership marker.
`pigsty-vm` exposes the same profile, network, lifecycle, and inventory contract through a small set of typed environment variables.

The wrapper does not fall back to another provider. Operational rollback requires a previously verified Piglet artifact and a matching state backup.

## Persistence, upgrade, and automation

Disks marked `persistent: true` survive ordinary destroy and compatible recreate.
Deletion requires a separate TTY confirmation phrase or `destroy --force --delete-persistent --yes-delete-persistent`.
Project-key cleanup defaults to a dry run and requires the separate `project purge-keys --yes` command to apply deletion.

Schema 0→1 migration requires stopped nodes and no lease.
It first makes a backup, then performs an explicit atomic update through `project upgrade-state --dry-run|--yes`.
The system rejects newer schemas without downgrading them.

Private node selectors, `--no-wait`, stable JSON responses, and typed exit classes support operators and automation.
The system also provides shell completion, SSH config, hosts blocks with ownership markers, per-node logs, and redacted support bundles.

## Images and release mechanisms

The formal embedded image set is `el9`, `el10`, `d12`, `d13`, `u22`, `u24`,
and `u26` on both Tier-1 native architectures. Retained matrix records report
7/7 per architecture; EL8 was retired from v1 because its arm64 kernel cannot
satisfy the tested native HVF contract. The entries remain `testing` pending a
production image channel and custody.

The source tree can build and verify four native archives, a Homebrew formula, and Linux amd64/arm64 RPM and DEB packages.
It also supports checksums, SPDX SBOMs, complete release assembly, and positive and tamper tests for Cosign signatures and SLSA provenance.
The tested snapshots passed isolated package install/verify/remove and two-run reproducibility checks.
The checked-in release workflow has not executed for a real tag.

## Evidence must follow exact bytes

At this snapshot, catalog schema 3 and inventory integration had changed the checked-in profile and resolved digests after the retained `full`/MinIO runs.
The snapshot therefore still required native validation with its exact profiles.
Custom-subnet hosts publishing, application of `storage.data_root`/`ssh.wait_timeout`, and generic Quick users also remained incomplete.

RC6 later completed these implementations and exact-profile checks. Historical native runs only validate the artifacts and behavior they tested.

## What remains before v1.0

The snapshot's exact-profile, Pigsty-bootstrap, and Rocky 9.8 private-host checks were completed later. The remaining work at that stage was:

- Assign responsibility for production images, manifests, releases, and long-running runners.
- Test recovery after a real reboot, native operation on Tier-2 hosts, and installation of published packages.
- Publish a signed release with provenance attestation tied to a real tag.

See the current [tutorial](/docs/start/tutorial/),
[design](/docs/about/design/), and [status](/docs/about/status/) for the
maintained boundary.
