---
title: Reference
linkTitle: Reference
description: Barn 1.1.0 configuration, command options, output formats, and image repositories.
weight: 20
icon: fa-solid fa-book-open
no_list: true
cascade:
  type: docs
---

Use these pages to look up every command, configuration field, output schema, and image catalog rule. **Barn 1.1.0** is the stable baseline; the [version table](commands/#versions) separately identifies local main and uncommitted development features checked on 2026-11-11. For task-oriented walkthroughs, start with the [Guides](../start/).

- [Command Reference](commands/) — Every Linux and macOS command, complete option tables, defaults, examples, and version availability
- [Linux Configuration](configuration/) — Inventory discovery, variables, defaults, data disks, host shares, and node drift rules
- [CLI Contracts](cli/) — Global flags, Linux lifecycle commands, structured JSON/YAML output, and exit codes
- [Mac Runtime Reference](mac/) — `barn mac` subcommands, VM settings, JSON schemas, error reasons, and runtime files
- [Linux Images](images/) — Embedded catalog `2026110502`, aliases, repository verification, local imports, and cache pruning
- [Image Pipeline](image-pipeline/) — Contributor tools for validating and offline-normalizing Linux qcow2 candidates
{.cards}

Barn's public interface is the `barn` CLI (`barn version`, `barn <command> --help`); Go packages under `internal/` are internal implementation details. The image tables reflect the catalog embedded in Barn 1.1.0, while `barn update` can activate newer signed repository metadata without replacing the binary. For release verification and build gates, see [Release Engineering](../about/engineering/).
