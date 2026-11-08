---
title: "The Lifetime of a Native Mac VM"
linkTitle: "Native Mac lifecycle"
description: "Why Barn uses named Mac machines, process-owned networks, narrow locks, and explicit recovery evidence."
date: 2026-09-29T10:00:00+08:00
lastmod: 2026-11-08
weight: 110
categories: [Design]
tags: [macOS, Recovery, Architecture]
icon: fa-brands fa-apple
---

`barn mac` manages named macOS VMs through Apple's `Virtualization.framework`, independently of the Linux inventory. Introduced in `0.9.0`, it uses the native host app `Barn.app`, included in Apple Silicon release archives since `0.9.2`. This essay distills the [named-machine implementation record](https://github.com/pgsty/barn/blob/main/docs/mac-implementation-log.md) and earlier Mac reviews, with the current implementation checked on 2026-11-08. Commands and defaults are in the [Mac reference](/docs/reference/mac/).

## A machine owns its network {#network-ownership}

The early design had two fixed slots and a privileged network helper. The 2026-09-29 redesign replaced that model with named machines and a private `/24` NAT network created inside each runner process. The guest receives `.10` on its own subnet. Two is the simultaneous-running limit, shared with other macOS virtualization tools and restore installation; stored machines are not restricted to two fixed names.

Network ownership now follows VM lifetime. Starting the runner creates the network, and stopping it releases the network. There is no separate root network daemon to install or reconcile for `barn mac`. The retired helper protocol remains in the [historical network document](https://github.com/pgsty/barn/blob/main/docs/history/mac-network-20260928.md).

This topology also supports first-contact SSH trust. On an uninitialized VM, Barn checks the runner's identity before and after connecting to the reserved address, authenticates the guest, and pins its host key under the instance UUID. The guest is the only peer besides the trusted host on that runner's private network. Later connections require the pinned key; changing the subnet keeps the instance identity, while recreation creates a new one. See [`readySSH`](https://github.com/pgsty/barn/blob/main/internal/macvm/ssh.go).

## Locks protect different lifetimes {#locks}

The acquisition order is machine operation → shared state → native runner:

| Lock | What it protects |
|---|---|
| Machine operation | Serializes lifecycle changes to one named VM |
| Shared state | Coordinates image and machine records used across operations |
| Runner lifetime | Establishes whether the native process still owns the VM |
{.wide}

Runtime-only changes can use the machine lock, so preparing an image does not prevent an unrelated VM from shutting down. A stop request can interrupt that machine's SSH-readiness wait through an operation nonce, then take the operation lock; cancellation does not grant two commands simultaneous write access. The rules live in [`operations.go`](https://github.com/pgsty/barn/blob/main/internal/macvm/operations.go) and [`readiness_interrupt.go`](https://github.com/pgsty/barn/blob/main/internal/macvm/readiness_interrupt.go).

A successful shutdown request begins a transition. Barn waits for evidence that the runner has released the VM before treating it as stopped. SSH disconnection or an unavailable RPC socket alone cannot establish that fact. When runtime evidence is ambiguous, status reports `unknown` and destructive work stops. This protects disks still attached to a live VM; see [`status.go`](https://github.com/pgsty/barn/blob/main/internal/macvm/status.go).

## Publish a base only after restore stops {#base-images}

Apple's installer completion callback can arrive while the restore VM is still running. Barn therefore waits for the installer to finish, verifies or completes the restore VM's stop, and only then publishes a read-only base with `ready=true` and `first_boot=false`. A timeout or uncertain state prevents publication. See [`finishRestoreMachine`](https://github.com/pgsty/barn/blob/main/native/mac-runner/Sources/Images.swift).

New machines clone that base and receive their own identities and credentials. Cache reuse also checks compatibility: Apple's online metadata may select a different hardware model for the same build, so Barn validates the saved model's hash and current host support before reusing an existing ready base. A matching build label alone is insufficient.

Recreation adds another reference lifetime. An unfinished recreate journal may still need the old machine's base even after the replacement is ready. Image pruning includes those journal references and refuses ambiguous records. A diagnostic list can report a bad record and continue; pruning needs a complete reference set before deleting anything. The [1.0 hardening review](https://github.com/pgsty/barn/blob/v1.0.0/docs/release-1.0-hardening.md) records this recovery decision.

## Keep guest credentials within one boundary {#credentials}

Each machine stores its GUI password beside its SSH private key, both protected by private file permissions. The key already grants passwordless sudo inside that guest. Moving only the GUI password into Keychain would not strengthen that local access boundary, but would add signing-identity changes, locked-keychain failures, and credential migration to normal app upgrades.

Barn therefore removed Keychain storage for guest passwords; [`secret.go`](https://github.com/pgsty/barn/blob/main/internal/macvm/secret.go) states this rationale. Developer ID signing and notarization still use their own Keychain/profile configuration. Readiness checks preserve existing SSH material, and app replacement preserves machine identity and host pins. Credentials change through explicit machine recreation, not merely because the executable was rebuilt.

## Validate transitions and recovery {#acceptance}

The historical tests exposed failures that successful startup alone would miss: first SSH can need a bounded wait; shutdown must be observed to completion; replacing an app must retain credentials; and a failed recreation must keep the base needed to recover. The [validation history](/docs/about/history/) preserves the dates, candidate identities, reused-base conditions, and later release checks.

For a change to these boundaries, use the [Mac release acceptance procedure](/docs/about/mac-release/#acceptance) and the existing live harness. Record whether the run includes a fresh IPSW download, prepared-base reuse, GUI/clipboard checks, or only core lifecycle steps. Unit tests cover lock cancellation and metadata failures; a physical Apple Silicon host supplies the runtime evidence for restore, networking, SSH, and shutdown.
