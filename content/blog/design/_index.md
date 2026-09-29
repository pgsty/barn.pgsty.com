---
title: Design Notes
linkTitle: Design
description: Architecture decisions, trade-offs, and implementation boundaries behind Farrow.
weight: 20
icon: fa-solid fa-pen-ruler
sidebar_root_menu: false
sidebar_expanded: true
blog_index: list
lastmod: 2026-09-26
---

Farrow's source repository once carried the redesign brief, implementation
ADRs, and native evidence beside the code. That material was useful while the
product was changing quickly, but many early decisions were later superseded.
This section keeps the durable reasoning, rewritten against the current source
instead of republishing stale plans.

Start with the product model, then follow the boundaries outward:

1. [Why Farrow has no projects](one-deployment-no-projects/) — one Inventory,
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

Use the [documentation](/docs/) for current behavior and the
[status page](/docs/about/status/) for dated verification. These design records
explain why those contracts exist; they do not turn a design, build, or local
test into release evidence.

These articles retain their original publication dates and were last reviewed
against source on **2026-09-26**. Changes specific to an unreleased candidate
are marked separately; historical verification keeps its original date and scope.
