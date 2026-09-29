---
title: Design
description: How Barn models Linux labs and macOS guests, with predictable state and explicit lifecycle changes.
weight: 20
icon: fa-solid fa-compass-drafting
aliases: [/docs/concepts/, /docs/concepts/networking/, /docs/concepts/storage/, /docs/concepts/safety/, /docs/architecture/, /docs/architecture/overview/, /docs/architecture/networking/, /docs/architecture/security/]
---

Barn provides two workflows that share a CLI but keep their configuration and
lifecycle separate.

| | Linux labs | macOS guests |
| --- | --- | --- |
| Virtualization | QEMU with HVF or KVM; TCG for selected compatibility cases | Apple Virtualization.framework |
| Desired state | A Pigsty-compatible YAML inventory | Named machines configured with `barn mac` |
| State directory | `~/.barn` | `~/.barn/mac` |
| Networking | Management NIC plus a fixed-IP lab subnet | One NAT subnet and DHCP reservation per machine |
| Typical work | Database clusters, Linux development and automation | macOS builds, desktop tools and isolated development |

The sections below explain the Linux lab model. For the native macOS workflow,
see [macOS guests](../../start/macos/) and the [Mac reference](../../reference/mac/).

## One Linux lab per user

Barn boots one Pigsty-compatible inventory as one local QEMU deployment. It deliberately
has no project marker, project registry, lease model, provider layer, or
second configuration format.

State lives under `BARN_HOME` (default `~/.barn`) for one Unix user. The
Linux workflow is designed for one lab per user; this is not a root-enforced cross-user
singleton.

## Node-level convergence

Barn extracts only the documented VM and Pigsty-native fields, computes
per-node hashes, and keeps applied state plus process identity. Additions are
incremental. Changes require an
explicit per-node recreate. `up` also starts selected existing stopped nodes;
already-running peers keep their processes while unfinished guest setup and
managed hosts/SSH entries are refreshed. Unrecognized or confirmed damaged
test data filesystems may be reset, including persistent disks; see
[Data disks](../../reference/configuration/#data-disks). Absence never authorizes deletion.

## Runtime selection

guest architecture is deployment-wide desired state. Omitted/`native` follows
the host; explicit `amd64` or `arm64` selects that catalog artifact exactly.
Native HVF/KVM remains the default. A foreign architecture or one catalogued
image/host incompatibility selects a fixed TCG profile; there is no user
accelerator argument and no arbitrary failure fallback.

The effective architecture and accelerator are persisted in each QEMU
invocation and exposed by `status`. Before destructive recreate, Barn proves
the selected QEMU binary and version, network backend, image bytes, boot mode,
and firmware. A later binary changing runtime policy cannot mix new nodes with
old invocations: runtime drift requires whole-deployment recreation.

## Two NICs, one fixed subnet

The management NIC supplies DHCP, DNS, egress, and loopback SSH. The fixed-IP
NIC supplies host/peer/Ansible traffic. macOS uses socket_vmnet. Linux follows
active NetworkManager; otherwise it uses systemd-networkd and connects through
the distribution bridge helper. Inactive networkd is started only after an
activation-safety scan proves existing units cannot claim a real host link.

On Debian, the helper is temporarily and reversibly scoped to a group the
caller actually belongs to. A real unprivileged QEMU bridge smoke must pass
before setup accepts the network; failure rolls the install back automatically.

## Storage and configuration have different lifetimes

The inventory records desired VM definitions. Applied state records what was
created, including the exact base-image identity and runtime invocation.
Changing a catalog channel does not rewrite an existing root disk.

Verified base images are shared read-only; each VM writes to its own root
overlay. Data disks have a separate preservation contract: normal destroy
retains persistent disks, while explicit disk deletion or purge removes them.
Cache pruning has another boundary and also protects the active catalog and
registered local aliases. See [Storage and access](../../start/storage/) and
[Images](../../reference/images/).

## Safety boundary

QEMU and all guest artifacts run as the caller. Root is limited to host
package installation, network setup, and the optional hosts publisher. Destruction requires matching
ownership, containment, node identity, QMP/process identity, and an allowlist
of artifacts. Ambiguity stops the operation.
