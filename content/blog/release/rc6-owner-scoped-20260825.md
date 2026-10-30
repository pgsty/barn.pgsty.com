---
title: "RC6 development candidate: owner-scoped Tier-1 delivery"
linkTitle: 2026-08-25 RC6 candidate
description: Exact RC6 identity, four requested native product passes, durable network transactions, reproducible local archives, and the boundary that keeps this candidate unpublished.
date: 2026-08-25
weight: 110
categories: [Development]
tags: [RC6, QEMU, Networking]
icon: fa-solid fa-vial-circle-check
---

> [!NOTE]
> Pre-Barn historical archive (`Piglet 1.0.0-rc.6`, 2026-08-25). This candidate was a local verification milestone and was never published as a GitHub Release or package repository; the SHA-256 digests below record the retained local build artifacts. For current Barn usage and support status, see the [documentation](/docs/) and [status page](/docs/about/status/).

Piglet `1.0.0-rc.6` was a local development candidate that validated the Quick and four-node `full` profiles on both Tier-1 native hypervisor platforms (`macOS arm64 / HVF` and `Linux amd64 / KVM`) and introduced journaled host-network transactions for crash recovery.

## Frozen build identity

| Field | RC6 value |
| --- | --- |
| Version | `1.0.0-rc.6` |
| Source commit | `7db733184463cc189ffa738335c213fc9a2982de` |
| Go | `go1.27.0` |
| Source epoch | `1787657920` |
| Build timestamp | `2026-08-25T11:38:40Z` |
| Channel | `development` |
| Signature / attestation | `false` / `false` |
| Exact `full` profile SHA-256 | `912fea61bf1602c2a437570561a6ab4d0a5a8c152695147ad9e96ae831bc9336` |
{.wide}

## Four native product scenarios

| Host | Scenario | Result | Guest contract |
| --- | --- | --- | --- |
| macOS `arm64` / HVF | Quick | PASS | Ubuntu 24.04.4, `dba` UID/GID 88, 2 vCPU, 64 GiB root, 64 GiB `/data` |
| Linux `amd64` / KVM | Quick | PASS | Ubuntu 24.04.4, `dba` UID/GID 88, 2 vCPU, 64 GiB root, 64 GiB `/data` |
| macOS `arm64` / HVF | Exact `full` | PASS | `.10`–`.13`, UID 88, 64 GiB roots, 128 GiB data disks, 2/1/1/1 vCPU, 4-way peer mesh |
| Linux `amd64` / KVM | Exact `full` | PASS | `.10`–`.13`, UID 88, 64 GiB roots, 128 GiB data disks, 2/1/1/1 vCPU, 4-way peer mesh |
{.wide}

All eight `full`-profile guests booted Ubuntu 24.04.4, passed contract assertions, and were cleanly destroyed afterward while retaining shared image caches, project markers, and keys.

## Journaled host-network transactions

Network install and uninstall use a root-owned, strict-prefix transaction:

- Root planning produces a token bound to the invoking owner, host identity, and observed prestate.
- Apply re-evaluates the plan under the host-global lock and accepts only that token.
- A typed, `fsync`-committed journal is written before any host mutation begins.
- Each step records a checkpoint only after verifying its postcondition.
- If a transaction is interrupted, ordinary network changes are blocked until an explicit forward or rollback recovery plan is approved.

macOS completed an interrupted forward-recovery test and converged to a healthy default `host` network. Linux completed install, rollback/retry, four-node operation, uninstall, and host restoration prior to a final patch that tightened socket-state canonicalization, `systemd` unit enablement scope, NetworkManager ordering, and recovery field scoping (verified via source checks and `-race` tests).

## macOS shared mode and subnet conflicts

The default macOS mode is `socket_vmnet` `host` mode; `shared` mode also passed a two-node test on an alternate free subnet as an explicit opt-in fallback.

During testing, the default subnet encountered `VMNET_SHARING_SERVICE_BUSY (1009)` when an older Piglet-created `bridge100` interface was still present. Preflight checks interface ownership markers rather than adopting an existing interface just because its `.1/24` address matches. When a subnet conflict occurs, operators can either remove the conflicting interface or move the entire lab to a clean RFC 1918 `/24` subnet—the runtime never renumbers individual guests or picks a random subnet on its own.

## Reproducible local archives

Two independent local RC6 build trees produced byte-identical archives, checksums, release metadata, and Homebrew formula files:

| Archive | SHA-256 |
| --- | --- |
| Darwin `amd64` | `1295288ff198b53fcb761a6e8794087d75a46105fc19980fabcd44f0c70fb9ef` |
| Darwin `arm64` | `308310b0f2d179f98c8be78ea09f89d226167072c936387bc42d717a922ec0c6` |
| Linux `amd64` | `547a61f6cc0768071df349cbf5c17d7ddfe3ab3cea59e6b4026e3e3e616a5550` |
| Linux `arm64` | `afc9ce1043d377cc3b4ef8bdf77826a8139a8c839685025853e8bee8100c6a2e` |
{.wide}

## Remaining work before public release

At the close of RC6, the remaining items before public release were:
- Physical host-reboot persistence checks on both Tier-1 platforms
- Native smoke tests on macOS `amd64` and Linux `arm64`
- Re-running the Linux network install/uninstall/reinstall cycle with the final post-audit patch
- Guest image normalization, hosting, and active/standby manifest signing keys
- Public release tags, Homebrew tap and DEB/RPM package publication, and clean-host installer verification

See the [tutorial](/docs/start/tutorial/), [architecture guide](/docs/about/design/), and [status page](/docs/about/status/) for how these items were completed in subsequent Barn releases.
