---
title: Design Notes
linkTitle: Design
description: Architecture decisions, trade-offs, and implementation boundaries behind Barn.
weight: 20
icon: fa-solid fa-pen-ruler
sidebar_root_menu: false
sidebar_expanded: true
blog_index: list
lastmod: 2026-09-29
---

This section explains the architecture and implementation choices in Barn 0.9.0.

Read the product model first, then the implementation details:

1. [Why Barn has no projects](one-deployment-no-projects/) — one inventory,
   one deployment per owner, and one authoritative configuration.
2. [Why every node has two NICs](fixed-ip-two-nics/) — fixed identity for the
   lab, with a separate interface for management egress.
3. [Declarative does not mean destructive](convergence-without-surprise/) —
   per-node drift with explicit recreate and removal.
4. [A PID is not a virtual machine](identity-before-pid/) — QMP identity,
   process evidence, journals, and bounded recovery.
5. [`repo.yaml` is intent; `catalog.json` is evidence](repo-yaml-catalog-json/)
   — a static image repository whose generated metadata is checked against the
   actual qcow2 bytes.

Use the [documentation](/docs/) for commands and configuration, and
[Platforms and Limits](/docs/about/status/) to check whether Barn fits your host.

## Design history

The original [Mac feasibility study](https://github.com/pgsty/barn/blob/5bce6b8824e63548d1066f6bd45942a08cdb00b8/MACOS-VM-RESEARCH-20260921.md),
[two-slot product proposal](https://github.com/pgsty/barn/blob/5bce6b8824e63548d1066f6bd45942a08cdb00b8/MACOS-VM-PRODUCT-20260921.md),
and [implementation and review records](https://github.com/pgsty/barn/blob/54315029d4a8d3ace7b4f7250d0381598f2d61dc/docs/mac-implementation-log.md)
explain the reasoning and experiments used to design named Mac machines.
The [validation history](/docs/about/history/) records dated release and native
test results. Earlier designs retain their original scope.
