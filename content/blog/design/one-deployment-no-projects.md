---
title: "Why Barn Has No Projects"
linkTitle: "One deployment, no projects"
description: "Why Barn replaced per-directory project state with one owner-scoped deployment driven by one Pigsty inventory."
date: 2026-08-27T19:00:00+08:00
weight: 10
categories: [Design]
tags: [Architecture, inventory, State]
icon: fa-solid fa-layer-group
lastmod: 2026-09-29
---

This article explains the Linux deployment model in Barn 0.9.0. [Mac machines](/docs/start/macos/) are managed independently.

Barn originally treated each working directory as a project. A hidden marker identified the project, a registry located it, and a host-wide lease prevented private-network collisions.
This model supported independent VM sets, but it did not match Barn's intended use.

Barn is designed for one local Pigsty lab with fixed IP addresses, already described by the Pigsty inventory. A separate VM manifest and project identity introduced extra configuration and ownership questions:

- Which file is authoritative for a node's name and address?
- Does moving a directory move the lab or create a new one?
- What happens when the marker survives but the registry does not?
- Is a missing directory an abandoned project or an unavailable disk?
- Which project owns the one host network?

Multiple independent projects need these mechanisms; a single Pigsty lab does not. Barn therefore removed the project model.

> [!NOTE]
> This record explains the product model. For
> current filenames, fields, and commands, use the
> [configuration reference](/docs/reference/configuration/).

## One inventory is enough

The Pigsty inventory also defines Barn's desired state. Barn reads host addresses, selected Pigsty identity fields, and the documented `vm_*` namespace.
Barn strictly validates its namespace. It passes the rest of the inventory to Pigsty without interpretation or changes.

A misspelled `vm_mem` must fail because this field controls the VM definition. An unfamiliar PostgreSQL tuning parameter can pass through because the VM layer does not use it.
This rule lets the Pigsty inventory change without requiring a separate Barn configuration format.

Barn selects a node name from `nodename` when present. Otherwise, it derives a stable name from the Pigsty cluster and sequence, then falls back to the address suffix.
Barn does not add a separate `vm_name` that could conflict with Pigsty's hostname.

## One owner-scoped state root

Applied state lives under `BARN_HOME`, normally `~/.barn`. There is no
marker in the working directory and no per-directory registry. Commands that
operate on applied state can run from any directory.
Commands that propose new desired state discover or receive an inventory explicitly.

Each Unix user has an independent state root, so the single-deployment limit applies per user rather than to the whole host. Barn assumes a trusted development workstation and does not arbitrate between hostile users on a shared server.

The simplification has practical consequences:

- moving or renaming the source directory does not move deployment identity;
- losing the inventory does not erase the applied state;
- cleanup follows explicit lifecycle commands; deleting the state directory
  is not a substitute for stopping VMs or removing managed integrations;
- image cache, keys, nodes, disks, locks, and deployment state share one
  inspectable home. Short QMP/pid paths, SSH client integration, and host-global
  networking have their own managed locations; see
  [Uninstall](/docs/start/uninstall/) for complete cleanup.

## Configuration absence is not intent

Barn keeps desired configuration separate from applied state. The inventory remains necessary for configuration changes, while commands that permit fallback can use the existing deployment's applied spec. A missing file never authorizes node removal.

This rule applies throughout the lifecycle. [Planning and deletion remain explicit](/blog/design/convergence-without-surprise/).
Recovery preserves resources whose identity is ambiguous.

## The trade-off is deliberate

Barn does not support multiple concurrent deployments per user. The design excludes projects, registries, and address-level leases because these features would reintroduce the removed project model.

Multi-tenant or multi-host orchestration would require a different product scope.
For a local Pigsty lab, one inventory and one deployment simplify address management, ownership checks, drift detection, recovery, and cleanup.

Read next: [Why every Barn node has two NICs](/blog/design/fixed-ip-two-nics/).
