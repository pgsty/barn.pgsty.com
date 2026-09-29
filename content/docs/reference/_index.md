---
title: Reference
linkTitle: Reference
description: Exact contracts for the Pigsty-compatible Inventory and Barn command line.
weight: 20
icon: fa-solid fa-book-open
cascade:
  type: docs
---

This reference describes the **Barn 0.9.0 release candidate**. Check
`barn version` before scripting against these contracts. See the [release status](../about/status/#documentation-baseline).

- [Configuration](configuration/) — discovery, accepted variables, defaults, disks, shares, naming, and drift.
- [CLI](cli/) — commands, important flags, output modes, and exit codes.
- [Mac Commands](mac/) — the unreleased `barn mac`: commands, JSON results, and failure reasons.
- [Images](images/) — signed catalogs, aliases, cache layout, pulls, imports, and pruning.
- [Image Pipeline](image-pipeline/) — candidate validation and offline normalization.

Barn exposes no supported Go library API. Packages under `internal/` are
implementation details.
