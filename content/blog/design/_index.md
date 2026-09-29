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

Start with the product model, then follow the boundaries outward:

1. [Why Barn has no projects](one-deployment-no-projects/) — one inventory,
   one owner-scoped deployment, and no second source of truth.
2. [Why every node has two NICs](fixed-ip-two-nics/) — fixed identity for the
   lab, separate from management egress.
3. [Declarative does not mean destructive](convergence-without-surprise/) —
   per-node drift with explicit recreate and removal.
4. [A PID is not a virtual machine](identity-before-pid/) — QMP identity,
   process evidence, journals, and bounded recovery.
5. [`repo.yaml` is intent; `catalog.json` is evidence](repo-yaml-catalog-json/)
   — a static image repository whose generated metadata is checked against the
   actual qcow2 bytes.

Use the [documentation](/docs/) for commands and configuration, and
[Platforms and Limits](/docs/about/status/) to check whether Barn fits your host.
