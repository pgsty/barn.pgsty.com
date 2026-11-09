---
title: "Declarative Does Not Mean Destructive"
linkTitle: "Convergence without surprise"
description: "How Barn uses per-node hashes and explicit operations so missing configuration can never authorize deletion."
date: 2026-08-27T21:00:00+08:00
weight: 30
categories: [Design]
tags: [Lifecycle, Drift, Safety]
icon: fa-solid fa-arrows-rotate
lastmod: 2026-11-09
---

This essay explains the Linux VM convergence model in Barn `1.1.0` ([macOS guests](/docs/start/macos/) are managed independently).

A declarative tool compares live state against a configuration file—but in daily development, that file might be temporarily edited for debugging, checked out on another git branch, or missing a YAML group after a merge. If a local VM manager treats an omitted YAML block as permission to destroy a virtual machine, a single typo can wipe out a database node.

Barn enforces a strict asymmetry between creation and destruction:

> Desired state authorizes creation and describes drift, but never authorizes destruction by omission.

Root overlays, data disks, SSH host identities, and local databases hold state that takes time to rebuild. When a change requires replacing or deleting a node, the operator must invoke that action explicitly.

## From Pigsty inventory to per-node spec hash {#from-pigsty-inventory-to-per-node-spec-hash}

When reading `barn.yml`, Barn extracts the fields in its contract, fills defaults, and normalizes image selectors and architecture into a resolved specification. Exact catalog image digests are resolved separately so that running `barn update` does not silently invalidate every node's specification hash. Each node's hash combines two inputs:

- **The deployment envelope** shared by all nodes (the `/24` subnet, login username, `vm_arch` policy, and deployment-level default image selector).
- **That node's resolved definition** (`nodename`, IP, vCPUs, memory, root disk, `vm_disks`, `vm_shares`, and `vm_alias`).

Adding a second node leaves the first node's hash untouched, and editing upper-layer Pigsty variables (`pg_version`, `node_packages`, `pg_role`) produces zero VM drift.

> [!NOTE]
> `barn up` converges additions and stopped nodes automatically. CPU and memory changes use `barn resize`; other specification changes and node removals use explicit `barn recreate` and `barn destroy` commands. See [Daily Operations](/docs/start/operations/) for the command workflow.

## Six explicit `barn plan` outcomes {#six-explicit-barn-plan-outcomes}

`barn plan` compares the desired inventory against committed deployment and node state and classifies every node into one of six outcomes:

| Outcome | Meaning | Resolution command |
|---|---|---|
| `create` | Node exists in the inventory with no committed VM state | `barn up` creates and boots the node |
| `unchanged` | Resolved definition and runtime policy match committed state | `barn up` keeps running nodes untouched and starts stopped nodes |
| `resize` | Only the node's `vm_cpu` or `vm_mem` changed | `barn resize <node>` hot-plugs supported increases, otherwise stops and starts the same VM |
| `recreate` | Node's image, disk, share, or other hardware definition changed | `barn recreate <node>` (or `--yes` in scripts) |
| `missing` | Committed node is absent or marked `vm_skip: true` in the inventory | `barn destroy <node>`, or restore the node to `barn.yml` |
| Envelope drift | Deployment subnet, login user, `vm_arch`, or runtime policy changed | Whole-deployment `barn recreate` |
{.wide .expand}

`barn plan` is completely read-only and prints the exact command needed to resolve any `resize`, `recreate`, or `missing` drift. When you pass explicit node selectors to `plan`, `up`, `reload`, or `recreate`, Barn scopes the operation to those nodes and retains unselected peers' applied definitions (see [selected-node operations](/docs/start/operations/#selected-nodes)).

## Why `barn up` stops on node drift {#why-barn-up-stops-on-node-drift}

Rather than resizing a running VM or silently rebuilding a root disk when `vm_image` changes, `barn up` stops with a `conflict` error whenever an existing node's specification has drifted. CPU and memory changes go through `barn resize <node>`, which keeps the VM identity and disks. Every other change requires an explicit `barn recreate <node>`, which gives you two guarantees:

1. Every change that replaces a guest's root filesystem goes through one visible, confirmed command.
2. Barn validates all prerequisites—target QEMU emulator, accelerator policy, UEFI firmware, cached or downloadable image bytes, network backend, shared directory paths, and persistent-disk compatibility—**before** stopping or deleting the existing VM. If a foreign-architecture emulator is missing or a share path is invalid, the running VM stays untouched.

## Why missing nodes block `barn up` {#why-missing-nodes-block-barn-up}

A node can vanish from `barn.yml` for plenty of routine reasons that do not mean "delete this database server":

- You passed a smaller test inventory while debugging a single node.
- You renamed a group or toggled `vm_skip: true` on a host entry.
- A branch switch or merge conflict dropped a host stanza.
- You ran a command from a directory with a different `barn.yml`.

When committed state contains a node that is absent from the desired inventory, `barn up` and whole-deployment `barn recreate` halt before stopping any VM (`conflict`, reason `nodes_removed`, exit 4) and name the missing node so you can either restore it to `barn.yml` or run `barn destroy <node>` explicitly.

When you do destroy or recreate nodes, data-disk lifetimes follow clear boundaries:

- Ordinary `barn destroy` and `barn recreate` preserve `persistent: true` data disks on disk.
- Whole-deployment `barn destroy --delete-persistent` removes persistent data disks as well, and `barn purge` (or `barn destroy --purge`) removes all disks, SSH keys, and deployment state in one step.
- During `barn up` recovery, Barn formats a data disk that carries no signature and resets an ext4 or XFS filesystem only when the checker reports recognized corruption; a partition table, unsupported features, or an unknown checker failure keeps the data and reports a warning (see [Data Disks](/docs/reference/configuration/#data-disks)).

## Distinguish role changes from drift {#control-role-recovery}

Deleting the control node elects the first remaining node. `SpecHash` describes its current applied definition; `GuestSpecHash` describes the guest's existing readiness marker. A control-role change can therefore make these hashes differ while the VM identity and disks remain valid.

Before marking any node for deletion, Barn must finish the successor's committed prepare journal. It then atomically publishes the deployment as the role-change commit record and updates the successor's definition hash. If interrupted between those writes, recovery under the deployment lock accepts only a hash difference exactly explained by flipping `Control`; unrelated drift still fails. It does not create missing state, rotate the VM UUID, or change disk/process identity. See the [hardening record](/docs/about/history/#release-1-0-candidates) and [control recovery tests](https://github.com/pgsty/barn/blob/v1.1.0/internal/private/control_test.go).

Update the inventory's control role before the next `barn up` installs control SSH access. General live role migration would also need old-credential revocation, offline retries, and partial-failure semantics; accepting arbitrary hash changes would conceal that unfinished convergence.

## Require evidence of corruption {#disk-recovery-evidence}

Filesystem-checker exit codes alone cannot authorize formatting. ext4 codes `4`/`12` and XFS code `1` must accompany recognized corruption diagnostics. Unsupported features, permissions, I/O or memory failures, partition tables, and unknown diagnostics preserve the disk and produce a guest warning. `persistent` controls disk retention during destroy/recreate; it does not exempt recognized corruption from the documented reset policy.

The [disk recovery tests](https://github.com/pgsty/barn/blob/v1.1.0/internal/cloudinit/disk_recovery_test.go) check whether `mkfs` actually ran using a sentinel, while physical-host acceptance compares disk contents. This tests the destructive effect as well as the warning text; the dated coverage is in [validation history](/docs/about/history/#release-1-0-candidates).

## Incremental convergence without collateral damage {#incremental-convergence-without-collateral-damage}

Because convergence is evaluated per node, `barn up` scales a 1-node lab out to 4 nodes without restarting the running control node, and `barn recreate node-2` replaces `node-2` while leaving `meta` and `node-1` online and reattaching `node-2`'s compatible persistent data disks.

Read next: [A PID Is Not a Virtual Machine](/blog/design/identity-before-pid/).
