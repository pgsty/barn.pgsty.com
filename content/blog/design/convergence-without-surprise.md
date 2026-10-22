---
title: "Declarative Does Not Mean Destructive"
linkTitle: "Convergence without surprise"
description: "How Barn uses per-node hashes and explicit operations so missing configuration can never authorize deletion."
date: 2026-08-27T21:00:00+08:00
weight: 30
categories: [Design]
tags: [Lifecycle, Drift, Safety]
icon: fa-solid fa-arrows-rotate
lastmod: 2026-09-29
---

This article explains the Linux VM lifecycle in Barn 0.9.0. [Mac machines](/docs/start/macos/) are managed independently.

A declarative tool compares actual state with a configuration file. The file can be incomplete, come from the wrong branch, or temporarily omit a YAML group.
If the tool treats an omitted definition as deletion permission, an editing mistake can destroy a VM.

Barn uses this rule:

> Desired state may authorize creation. It can describe drift. It never
> authorizes destruction by omission.

Root disks, data disks, SSH keys, and local records retain state. Recreating these resources can be necessary, but the operator must explicitly select that operation.

## From inventory to node identity

Barn first extracts the fields it owns from the Pigsty inventory. It fills defaults and normalizes image selectors and architecture to produce a resolved spec.
Barn resolves exact catalog artifacts separately. Therefore, a channel update alone does not change a node's spec hash. Each node's hash includes:

- the deployment envelope shared by every node, such as subnet, login user,
  architecture policy, and the deployment-level default image request; and
- exactly that node's resolved definition.

Adding a node does not change an existing node's hash. Changes to other Pigsty fields, such as PostgreSQL version, packages, or service policy, do not produce VM drift. Barn checks only the fields in its VM configuration contract.

Barn does not implement Ansible's entire variable system. It rejects unknown `vm_*` keys and conflicting values inside its namespace. It does not interpret fields outside the documented boundary.

> [!NOTE]
> Barn converges additions automatically, but
> definition changes and removal require explicit commands. See
> [Daily Operations](/docs/start/operations/) for the command workflow.

## The five plan outcomes

`barn plan` compares desired state, applied deployment state, and committed
node state. It reports these outcomes:

| Outcome | Meaning | Apply path |
| --- | --- | --- |
| create | desired node has no committed state | `barn up` creates it |
| unchanged | definition and runtime still match | running peer stays untouched; stopped peer may start |
| recreate | node definition changed | explicit `barn recreate --force <node>` |
| missing | applied node is absent or skipped in the inventory | explicit `barn destroy <node> --force`, or restore it to the file |
| envelope drift | subnet, login identity, architecture, or runtime policy changed | whole-deployment recreate |

Plan is read-only. It reports the exact node sets and, in text mode, the command
that applies the required explicit transition.

## Why `up` stops at drift

Barn 0.9.0 does not apply CPU or memory changes automatically. It also does not rebuild a root disk automatically when the image changes.
A changed VM definition requires recreation, so `up` returns a typed conflict.

This rule provides two benefits:

1. all changes that can invalidate guest state share one visible operation;
2. Barn can finish every prerequisite check before touching the current
   node.

The recreate path resolves the selected emulator, acceleration policy,
firmware, image bytes, network backend, shares, and persistent-disk contract
before it destroys the node. If a foreign-architecture emulator is missing or a share is unsafe, Barn preserves the existing VM.

## Why missing nodes block convergence

A node can disappear from desired state for many reasons that do not express
deletion intent:

- the operator opened a reduced inventory while debugging;
- a group was renamed or filtered;
- `vm_skip` temporarily marks a real or external host;
- a merge conflict dropped a YAML branch;
- the configuration file itself is unavailable.

When applied state contains an omitted node, `up` stops and names that node. The operator must restore its definition or run the explicit destroy command. This step prevents configuration omissions from deleting disks automatically.

Normal destroy preserves persistent data disks.
Whole-deployment `destroy --delete-persistent` explicitly includes owned
persistent disks, including retained disks. It accepts no node selectors.
Deleting deployment keys as well requires whole-deployment
`destroy --purge` or `purge`. Retention is not a backup guarantee: guest
bootstrap can reset unrecognized or confirmed damaged test filesystems, even
on persistent disks. See [Data disks](/docs/reference/configuration/#data-disks).
Each confirmation applies only to its stated operation.

## Convergence is still incremental

Barn creates new nodes without stopping existing ones and starts selected stopped nodes without recreating running peers. A per-node recreate preserves other nodes and retains persistent data when the disk contract requires it.

Barn uses desired state to create nodes and calculate drift. It requires explicit commands for irreversible changes. The operator reviews the difference before authorizing a destructive operation.

Read next: [A PID is not a virtual machine](/blog/design/identity-before-pid/).
