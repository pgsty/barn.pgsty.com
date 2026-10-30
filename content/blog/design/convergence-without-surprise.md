---
title: "Declarative Does Not Mean Destructive"
linkTitle: "Convergence without surprise"
description: "How Barn uses per-node hashes and explicit operations so missing configuration can never authorize deletion."
date: 2026-08-27T21:00:00+08:00
weight: 30
categories: [Design]
tags: [Lifecycle, Drift, Safety]
icon: fa-solid fa-arrows-rotate
lastmod: 2026-10-30
---

This essay explains the Linux VM convergence model in Barn `0.9.2` ([macOS guests](/docs/start/macos/) are managed independently).

> [!NOTE]
> **2026-10-30 update:** The unreleased source changes scope `plan`, `up`, `reload`, and `recreate` to explicit node selections and retain unselected peers' applied definitions. The whole-inventory drift rules described below still apply when no nodes are selected. See [selected-node operations](/docs/start/operations/#selected-nodes).

A declarative tool compares live state against a configuration file—but in daily development, that file might be temporarily edited for debugging, checked out on another git branch, or missing a YAML group after a merge. If a local VM manager treats an omitted YAML block as permission to destroy a virtual machine, a single typo can wipe out a database node.

Barn enforces a strict asymmetry between creation and destruction:

> Desired state authorizes creation and describes drift, but never authorizes destruction by omission.

Root overlays, data disks, SSH host identities, and local databases hold state that takes time to rebuild. When a change requires replacing or deleting a node, the operator must invoke that action explicitly.

## From Pigsty inventory to per-node spec hash

When reading `barn.yml`, Barn extracts the fields in its contract, fills defaults, and normalizes image selectors and architecture into a resolved specification. Exact catalog image digests are resolved separately so that running `barn update` does not silently invalidate every node's specification hash. Each node's hash combines two inputs:

- **The deployment envelope** shared by all nodes (the `/24` subnet, login username, `vm_arch` policy, and deployment-level default image selector).
- **That node's resolved definition** (`nodename`, IP, vCPUs, memory, root disk, `vm_disks`, `vm_shares`, and `vm_alias`).

Adding a second node leaves the first node's hash untouched, and editing upper-layer Pigsty variables (`pg_version`, `node_packages`, `pg_role`) produces zero VM drift.

> [!NOTE]
> `barn up` converges additions and stopped nodes automatically, while specification changes and node removals use explicit `barn recreate` and `barn destroy` commands. See [Daily Operations](/docs/start/operations/) for the command workflow.

## Five explicit `barn plan` outcomes

`barn plan` compares the desired inventory against committed deployment and node state and classifies every node into one of five outcomes:

| Outcome | Meaning | Resolution command |
|---|---|---|
| `create` | Node exists in the inventory with no committed VM state | `barn up` creates and boots the node |
| `unchanged` | Resolved definition and runtime policy match committed state | `barn up` keeps running nodes untouched and starts stopped nodes |
| `recreate` | Node's hardware, image, disk, or share definition changed | `barn recreate <node>` (or `--force` in scripts) |
| `missing` | Committed node is absent or marked `vm_skip: true` in the inventory | `barn destroy <node>`, or restore the node to `barn.yml` |
| Envelope drift | Deployment subnet, login user, `vm_arch`, or runtime policy changed | Whole-deployment `barn recreate` |
{.wide}

`barn plan` is completely read-only and prints the exact command needed to resolve any `recreate` or `missing` drift.

## Why `barn up` stops on node drift

Rather than hot-plugging vCPUs/memory or silently rebuilding a root disk when `vm_image` changes, `barn up` stops with a `conflict` error whenever an existing node's specification has drifted. Requiring an explicit `barn recreate <node>` gives you two guarantees:

1. Every change that replaces a guest's root filesystem goes through one visible, confirmed command.
2. Barn validates all prerequisites—target QEMU emulator, accelerator policy, UEFI firmware, cached or downloadable image bytes, network backend, shared directory paths, and persistent-disk compatibility—**before** stopping or deleting the existing VM. If a foreign-architecture emulator is missing or a share path is invalid, the running VM stays untouched.

## Why missing nodes block `barn up`

A node can vanish from `barn.yml` for plenty of routine reasons that do not mean "delete this database server":

- You passed a smaller test inventory while debugging a single node.
- You renamed a group or toggled `vm_skip: true` on a host entry.
- A branch switch or merge conflict dropped a host stanza.
- You ran a command from a directory with a different `barn.yml`.

When committed state contains a node that is absent from the desired inventory, `barn up` halts and names the missing node so you can either restore it to `barn.yml` or run `barn destroy <node>` explicitly.

When you do destroy or recreate nodes, data-disk lifetimes follow clear boundaries:

- Ordinary `barn destroy` and `barn recreate` preserve `persistent: true` data disks on disk.
- Whole-deployment `barn destroy --delete-persistent` removes persistent data disks as well, and `barn purge` (or `barn destroy --purge`) removes all disks, SSH keys, and deployment state in one step.
- During `barn up` recovery, unrecognized or confirmed-corrupt data-disk filesystems are automatically formatted to the configured `fs` type (see [Data Disks](/docs/reference/configuration/#data-disks)).

## Incremental convergence without collateral damage

Because convergence is evaluated per node, `barn up` scales a 1-node lab out to 4 nodes without restarting the running control node, and `barn recreate node-2` replaces `node-2` while leaving `meta` and `node-1` online and reattaching `node-2`'s compatible persistent data disks.

Read next: [A PID Is Not a Virtual Machine](/blog/design/identity-before-pid/).
