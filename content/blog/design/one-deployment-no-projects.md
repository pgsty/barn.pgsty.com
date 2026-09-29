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

This article describes Barn 0.9.0. The VM lifecycle and network design here
apply to Linux guests; [Mac machines](/docs/start/macos/) are managed independently.

Barn began with a familiar VM-manager abstraction: a working directory was
a project, a hidden marker gave it identity, a registry found projects again,
and a host-global lease kept their private networks from colliding. That model
can support many independent VM sets. It was also the wrong model for the
product Barn was actually becoming.

The target is not a general-purpose hypervisor front end. It is one local,
fixed-IP Pigsty lab. The operator already has a complete description of that
lab: the Pigsty inventory. Adding a second VM manifest and a second project
identity made every ordinary question harder.

> [!NOTE]
> This record explains the product model. For
> current filenames, fields, and commands, use the
> [configuration reference](/docs/reference/configuration/).

The old abstraction turned ordinary questions into project-management
questions:

- Which file is authoritative for a node's name and address?
- Does moving a directory move the lab or create a new one?
- What happens when the marker survives but the registry does not?
- Is a missing directory an abandoned project or an unavailable disk?
- Which project owns the one host network?

Those are legitimate multi-project questions. Barn chose to stop creating
them.

## One inventory is enough

The inventory handed to Pigsty is also Barn's desired state. Barn reads a
small, documented boundary: host addresses, a few Pigsty-native identity
fields, and the `vm_*` namespace. Validation is strict inside that namespace;
the rest of the inventory stays opaque and passes to Pigsty untouched.

This asymmetric rule matters. A misspelled `vm_mem` must fail because it would
change the machine Barn builds. A new PostgreSQL tuning parameter must not
fail merely because the VM layer has never heard of it. The same file can
therefore evolve as a Pigsty inventory without becoming a second Barn
format in disguise.

Names follow the same principle. A node uses `nodename` when present, then a
stable Pigsty cluster/sequence derivation, then its address suffix. Barn does
not add a parallel `vm_name` that can disagree with the hostname Pigsty sees.

## One owner-scoped state root

Applied state lives under `BARN_HOME`, normally `~/.barn`. There is no
marker in the working directory and no per-directory registry. Commands that
operate on applied state can run from any directory; commands that propose new
desired state discover or receive an inventory explicitly.

This is an owner-scoped deployment, not a root-enforced machine-wide
singleton. Each Unix user has an independent state root. Barn is intended
for a trusted development workstation, not hostile-user arbitration on a
shared server.

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

One deployment does **not** mean the inventory is disposable. It means Barn
can distinguish desired configuration from applied evidence. When a command
needs desired state, an existing deployment can supply its applied spec where
the command contract allows that fallback. A missing file is never interpreted
as a request to remove nodes.

That rule survives every layer of the lifecycle: [planning and deletion stay
explicit](/blog/design/convergence-without-surprise/), and recovery preserves
ambiguous resources instead of guessing what the user meant.

## The trade-off is deliberate

Barn does not support multiple concurrent deployments per user. Projects,
registries, and address-level leasing are not hidden future features; they
were rejected because they would reintroduce the abstraction the product
removed.

If the requirement changes to multi-tenant or multi-host orchestration, that
is a different product boundary. For a local Pigsty lab, one inventory and one
deployment make the important things—addresses, ownership, drift, recovery,
and cleanup—much easier to explain and prove.

Read next: [Why every Barn node has two NICs](/blog/design/fixed-ip-two-nics/).
