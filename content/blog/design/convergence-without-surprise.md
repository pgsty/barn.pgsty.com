---
title: "Declarative Does Not Mean Destructive"
linkTitle: "Convergence without surprise"
description: "How Farrow uses per-node hashes and explicit operations so missing configuration can never authorize deletion."
date: 2026-08-27T21:00:00+08:00
weight: 30
categories: [Design]
tags: [Lifecycle, Drift, Safety]
icon: fa-solid fa-arrows-rotate
lastmod: 2026-09-26
---

> [!NOTE]
> **Reviewed 2026-09-26:** the original publication date is retained; the text
> below reflects the implementation reviewed on this date. See
> [Status](/docs/about/status/) for released versus candidate behavior and
> dated acceptance evidence.

“Declarative” is often shortened to “make reality equal the file.” That is a
useful slogan until the file is incomplete, the wrong branch is checked out,
or one YAML group is temporarily removed. If absence is treated as deletion,
an ordinary editing mistake becomes a destructive operation.

Farrow uses a narrower rule:

> Desired state may authorize creation. It can describe drift. It never
> authorizes destruction by omission.

The distinction is central to a VM runtime because roots, data disks, SSH keys,
and local evidence are not stateless replicas. Recreating them may be correct,
but it must be a decision the operator can see.

## From Inventory to node identity

Farrow does not hash the whole Pigsty Inventory. It first extracts the fields
it owns, fills defaults, canonicalizes image selectors and architecture, and
builds a canonical resolved spec. Exact Catalog artifact resolution remains
separate, so a channel update does not itself change a node's spec hash. Each
node then receives a hash of:

- the deployment envelope shared by every node, such as subnet, login user,
  architecture policy, and the deployment-level default image request; and
- exactly that node's resolved definition.

Adding a peer therefore does not change an existing node's hash. Editing an
unconsumed Pigsty field—PostgreSQL version, packages, or service policy—does
not produce VM drift. The VM layer reacts only to the contract it actually
understands.

This also avoids a dangerous half-promise: Farrow does not pretend to implement
Ansible's entire variable system. Unknown `vm_*` keys and conflicting values
inside the owned namespace fail. Everything outside the documented boundary
is opaque rather than partially interpreted.

> [!NOTE]
> **Decision status: current.** Farrow converges additions automatically, but
> definition changes and removal require explicit commands. See
> [Daily Operations](/docs/start/operations/) for the command workflow.

## The five plan outcomes

`farrow plan` compares desired state, applied deployment state, and committed
node state. The result is intentionally small:

| Outcome | Meaning | Apply path |
| --- | --- | --- |
| create | desired node has no committed state | `farrow up` creates it |
| unchanged | definition and runtime still match | running peer stays untouched; stopped peer may start |
| recreate | node definition changed | explicit `farrow recreate --force <node>` |
| missing | applied node is absent or skipped in the Inventory | explicit `farrow destroy <node> --force`, or restore it to the file |
| envelope drift | subnet, login identity, architecture, or runtime policy changed | whole-deployment recreate |

Plan is read-only. It reports the exact node sets and, in text mode, the command
that applies the required explicit transition.

## Why `up` stops at drift

Farrow could decide that changing CPU or memory is harmless enough to apply,
or that a new image should silently rebuild a root disk. Pre-1.0 intentionally
does neither. A changed VM definition is classified as recreate and `up`
returns a typed conflict.

That conservative boundary has two advantages:

1. all changes that can invalidate Guest state share one visible operation;
2. Farrow can finish every prerequisite check before touching the current
   node.

The recreate path resolves the selected emulator, acceleration policy,
firmware, image bytes, network backend, shares, and persistent-disk contract
before destruction. If a foreign emulator is missing or a share is unsafe,
the existing VM remains intact.

## Why missing nodes block convergence

A node can disappear from desired state for many reasons that do not express
deletion intent:

- the operator opened a reduced Inventory while debugging;
- a group was renamed or filtered;
- `vm_skip` temporarily marks a real or external host;
- a merge conflict dropped a YAML branch;
- the configuration file itself is unavailable.

When applied state contains such a node, `up` stops and names it. The operator
must either restore the definition or run the explicit destroy command. This
is deliberately more friction than automatic garbage collection—and far less
friction than recovering an unintended disk deletion.

Persistent data disks add another boundary. Normal destroy preserves them.
Whole-deployment `destroy --delete-persistent` explicitly includes owned
persistent disks, including retained disks, and accepts no node selectors;
deleting deployment keys as well requires whole-deployment
`destroy --purge` or `purge`. Retention is not a backup guarantee: guest
bootstrap can reset unrecognized or confirmed damaged test filesystems, even
on persistent disks. See [Data disks](/docs/reference/configuration/#data-disks).
One confirmation cannot silently grow into broader authority.

## Convergence is still incremental

Safety does not mean rebuilding everything. New nodes are created without
stopping existing peers. Selected stopped nodes start without recreating
running ones. A per-node recreate preserves peers and, when requested by the
disk contract, persistent data.

The result is declarative where desired state is strong evidence—creation and
comparison—and explicit where the cost is irreversible. Farrow does not make
the operator manually calculate drift, but it also does not confuse a diff
with permission.

Read next: [A PID is not a virtual machine](/blog/design/identity-before-pid/).
