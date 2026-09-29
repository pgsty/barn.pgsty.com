---
title: "RC6 development candidate: owner-scoped Tier-1 delivery"
linkTitle: 2026-08-25 RC6 candidate
description: Exact RC6 identity, four requested native product passes, durable network transactions, reproducible local archives, and the boundary that keeps this candidate unpublished.
date: 2026-08-25
weight: 5
categories: [Development]
tags: [RC6, Go 1.27, Quick, Private, QEMU, macOS, Linux]
icon: fa-solid fa-vial-circle-check
---

> [!CAUTION]
> Pre-Barn historical record. It preserves the predecessor candidate's exact
> identity and does not establish support for current Barn bytes or paths.
> See [current status](/docs/about/status/).

Piglet `1.0.0-rc.6` is the owner-scoped local development candidate for the
single native-QEMU path. It closes the requested Quick and exact four-node
`full` scenarios on both Tier-1 hosts and adds durable privileged-network
transactions. It is deliberately not a public release.

> [!WARNING]
> No Homebrew operation, public tag, remote push, GitHub Release, package
> repository, production signature, attestation, or support commitment was
> created. The hashes below identify retained local artifacts; this site does
> not provide them as downloads.

## Frozen identity

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

## Four requested product scenarios

| Host | Scenario | Result | Guest contract |
| --- | --- | --- | --- |
| macOS arm64 / HVF | Quick | PASS | Ubuntu 24.04.4, `dba` UID/GID 88, 2 vCPU, 64 GiB root, 64 GiB `/data` |
| Linux amd64 / KVM | Quick | PASS | same contract |
| macOS arm64 / HVF | exact `full` | PASS | `.10`–`.13`, UID 88, 64 GiB roots, 128 GiB data disks, 2/1/1/1 vCPU, four-way peers |
| Linux amd64 / KVM | exact `full` | PASS | same contract |

All eight final full-profile guests reported Ubuntu 24.04.4. The projects were
destroyed through Piglet after assertions; shared image caches, project
markers, and keys were intentionally retained.

## Durable native networking

Network install and uninstall now use one root-owned strict-prefix transaction:

- root planning returns an owner/host/prestate-bound token;
- apply replans under the host-global lock and accepts only that token;
- a typed, fsynced journal is published before mutation;
- each fixed action is checkpointed after exact postcondition verification;
- interrupted work blocks ordinary private mutation until an explicit forward
  or rollback recovery plan is separately token-approved.

Darwin completed a real interrupted forward recovery and ended protected and
healthy in default host mode. Linux completed real install, rollback/retry,
four-node operation, uninstall, and host restoration before the final
adversarial patch. That patch closed socket-state canonicalization, overly broad
systemd enablement, NetworkManager ordering, and field-scoped recovery effects,
then passed consolidated source/race gates.

Per the owner's final direction, no VM or network test ran after that last
patch. Therefore the post-audit Linux install/uninstall/reinstall replay is
explicitly **not run**. This page does not upgrade source/race evidence into a
native result.

## macOS shared mode and subnet conflicts

The supported default remains socket_vmnet host mode. Shared mode passed a
two-node contract on a proven-free alternate subnet, but it is an explicit
fallback and not an isolation boundary.

The historical default-subnet failure was
`VMNET_SHARING_SERVICE_BUSY (1009)`. VirtualBox was a plausible contaminant,
not a proven owner of that incident. Immediately before the final migration,
the observed subnet interface was the older Piglet-created `bridge100`.
Preflight now rejects foreign interfaces by identity instead of adopting a
matching `.1/24` address. Operators can remove the confirmed owner or move the
whole lab to one warned canonical RFC1918 `/24`; Piglet never changes only the
guest addresses or selects a random escape subnet.

## Reproducible local archives

Two independent local RC6 output trees passed the strict release verifier and
were byte-identical for the four archives, checksums, release metadata, and
formula:

| Archive | SHA-256 |
| --- | --- |
| Darwin amd64 | `1295288ff198b53fcb761a6e8794087d75a46105fc19980fabcd44f0c70fb9ef` |
| Darwin arm64 | `308310b0f2d179f98c8be78ea09f89d226167072c936387bc42d717a922ec0c6` |
| Linux amd64 | `547a61f6cc0768071df349cbf5c17d7ddfe3ab3cea59e6b4026e3e3e616a5550` |
| Linux arm64 | `afc9ce1043d377cc3b4ef8bdf77826a8139a8c839685025853e8bee8100c6a2e` |

The formula is an inert build artifact. Earlier candidates exercised offline
RPM/DEB consumption and ephemeral Cosign/SLSA round trips, but those results
are mechanism evidence and are not relabeled as RC6 publication/signing.

## What remains public-GA work

- literal reboot persistence on both Tier-1 hosts;
- current native smoke on macOS amd64 and Linux arm64;
- the deliberately deferred Linux final network replay;
- remaining image normalization, byte-reproducibility decision, hosting, and
  active/standby manifest-key custody;
- production release identity, signing/attestation, published Homebrew and
  Linux package channels, and clean-host consumption;
- a durable owner-operated macOS HVF runner and explicit release authorization.

See the current [tutorial](/docs/start/tutorial/),
[design](/docs/about/design/), and [status](/docs/about/status/) for the
maintained boundary.
