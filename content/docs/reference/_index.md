---
title: Reference
linkTitle: Reference
description: Barn 1.0.0 configuration, command options, output formats, and image repositories.
weight: 20
icon: fa-solid fa-book-open
no_list: true
cascade:
  type: docs
---

Use these pages to look up configuration fields, command flags, structured output schemas, and image catalog rules in **Barn 1.0.0**. The [1.0.0 release notes](../../blog/release/1.0.0/) summarize what changed since 0.9.3. For task-oriented walkthroughs, start with the [Guides](../start/).

- [Linux Configuration](configuration/) — Inventory discovery, variables, defaults, data disks, host shares, and node drift rules
- [CLI Reference](cli/) — Global flags, Linux lifecycle commands, structured JSON/YAML output, and exit codes
- [Mac Commands](mac/) — `barn mac` subcommands, VM settings, JSON schemas, error reasons, and runtime files
- [Linux Images](images/) — Embedded catalog `2026110502`, aliases, repository verification, local imports, and cache pruning
- [Image Pipeline](image-pipeline/) — Contributor tools for validating and offline-normalizing Linux qcow2 candidates
{.cards}

Barn's supported public interface is the `barn` CLI (`barn version`, `barn <command> --help`), with the stability scope listed in [1.x compatibility](cli/#compatibility); Go packages under `internal/` are internal implementation details. The image tables reflect the catalog embedded in Barn 1.0.0, while `barn update` can activate newer signed repository metadata without replacing the binary. For release verification and build gates, see [Release Engineering](../about/engineering/).
