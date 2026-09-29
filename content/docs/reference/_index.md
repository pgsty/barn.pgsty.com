---
title: Reference
linkTitle: Reference
description: Exact contracts for the Pigsty-compatible Inventory and Farrow command line.
weight: 20
icon: fa-solid fa-book-open
cascade:
  type: docs
---

The public release baseline is **v0.8.0 (a prerelease)**. This reference was
also checked against local source **`b91ec37`**, the **unreleased 0.9 candidate**, on
2026-09-26. Changes specific to that candidate are marked explicitly; a source
checkout does not establish a published release. See the
[version matrix](../about/status/#documentation-baseline).

- [Configuration](configuration/) — discovery, accepted variables, defaults, disks, shares, naming, and drift.
- [CLI](cli/) — commands, important flags, output modes, and exit codes.
- [Mac Commands](mac/) — the unreleased `farrow mac`: commands, JSON results, and failure reasons.
- [Images](images/) — signed catalogs, aliases, cache layout, pulls, imports, and pruning.
- [Image Pipeline](image-pipeline/) — candidate validation and offline normalization.

Farrow exposes no supported Go library API. Packages under `internal/` are
implementation details.
