---
title: "Why Barn Has No Projects"
linkTitle: "One deployment, no projects"
description: "Why Barn replaced per-directory project state with one owner-scoped deployment driven by one Pigsty inventory."
date: 2026-08-27T19:00:00+08:00
weight: 10
categories: [Design]
tags: [Architecture, inventory, State]
icon: fa-solid fa-layer-group
lastmod: 2026-10-30
---

This essay explains the Linux lab deployment model in Barn `0.9.2` ([macOS guests](/docs/start/macos/) are managed as independent named VMs).

> [!NOTE]
> **2026-10-30 update:** Unreleased builds accept relative and symlinked `BARN_HOME` paths and hostname/IPv6 inventory keys on `vm_skip: true` external hosts. Use an absolute `BARN_HOME` when changing directories to keep the same deployment. See [Unreleased Changes](/docs/about/unreleased/).

Early prototypes of Barn treated every working directory as a separate project: a hidden directory marker identified the project, a central registry tracked active project paths, and a host-wide lease table arbitrated private subnet collisions. While that model made sense for a generic multi-project VM runner, it fought against Barn's actual job: running a local Pigsty database lab with fixed IP addresses.

Because a Pigsty inventory already defines every node's IP address and role, layering a per-directory project identity on top created failure modes that had nothing to do with database testing:

- Which file is authoritative for a node's name and IP—the VM project file or `pigsty.yml`?
- Does moving or renaming a git checkout move the existing lab or spawn a second one?
- How should Barn recover when the directory marker survives but the central registry is lost (or vice versa)?
- Does a missing project directory mean the user deleted the project, or that an external drive is currently unmounted?
- Which project owns the single host-level `/24` bridge?

A single local Pigsty lab needs none of that machinery, so we removed the project layer entirely.

> [!NOTE]
> For current inventory discovery order, field rules, and defaults, see the [Configuration Reference](/docs/reference/configuration/).

## One inventory is enough

A Pigsty inventory (`barn.yml` or `pigsty.yml`) serves directly as Barn's desired-state configuration. Barn reads the host IPv4 keys, a small set of Pigsty identity fields (`nodename`, `admin_ip`, `pg_cluster`, `pg_seq`, `node_admin_username`, `node_admin_uid`), and the `vm_*` variable namespace.

Barn validates `vm_*` fields strictly and ignores upper-layer Pigsty variables (`pg_role`, `pg_version`, `repo_*`, `node_packages`, and so on). That boundary gives you the best of both worlds: a typo in `vm_mem` fails immediately during `barn validate`, while PostgreSQL and Ansible tuning parameters evolve freely in the same YAML file without triggering VM drift.

Node naming follows the same principle: Barn uses `nodename` when set, otherwise derives `<pg_cluster>-<pg_seq>`, and falls back to `node-<last-octet>`. There is no separate `vm_name` field that could drift out of sync with Pigsty's hostname.

## One owner-scoped state root

All applied deployment state lives in `BARN_HOME` (default `~/.barn`). There are no hidden markers in your working directory and no path-based project registries. Commands that inspect or operate on applied state (`barn status`, `barn ssh`, `barn stop`, `barn start`, `barn destroy`) work identically from any directory; commands that read desired state (`barn validate`, `barn plan`, `barn up`, `barn reload`, `barn recreate`) take `-f` or discover `barn.yml` / `pigsty.yml` in the current directory.

Because `BARN_HOME` belongs to your Unix user account, the single-deployment model is scoped per user on a development workstation:

- Moving or renaming your working directory never orphans running VMs or creates a duplicate lab.
- Accidentally deleting `barn.yml` leaves the applied state in `~/.barn` intact (`barn plan` and `barn up` can still fall back to the committed specification).
- Image caches, SSH keys, node disks, locks, and state files live under one predictable root (while short Unix socket paths, `~/.ssh/barn_config`, and host network configurations remain in their standard locations; see [Uninstall](/docs/start/uninstall/)).

## Missing configuration never implies deletion

Barn separates desired configuration from committed state. While modifying a lab's topology requires an inventory file, a missing file or an omitted YAML group never authorizes Barn to delete existing VMs. [Planning and destructive actions are always explicit](/blog/design/convergence-without-surprise/), and recovery preserves any resource whose identity cannot be verified unambiguously.

## A deliberate trade-off

Barn intentionally manages one Linux lab per `BARN_HOME` rather than multiplexing concurrent projects, registries, and subnet leases. For local database and infrastructure development, one inventory driving one deployment keeps IP addressing, ownership verification, drift detection, crash recovery, and teardown straightforward.

Read next: [Why Every Barn Node Has Two NICs](/blog/design/fixed-ip-two-nics/).
