---
title: Reference
linkTitle: Reference
description: Barn 0.9.0 configuration, command options, output formats, and image repositories.
weight: 20
icon: fa-solid fa-book-open
cascade:
  type: docs
---

Use these pages to look up a field, flag, or result in **Barn 0.9.0**.
For a walkthrough, start with the [guides](../start/).

| Reference | Contents |
|---|---|
| [Linux configuration](configuration/) | inventory discovery, variables, defaults, disks, shares, and changes |
| [CLI](cli/) | Common options, Linux commands, structured results, and exit codes |
| [Mac commands](mac/) | macOS machine commands, settings, JSON results, and files |
| [Linux images](images/) | Image versions, repositories, signatures, imports, and cache management |
| [Image pipeline](image-pipeline/) | Contributor tools for preparing and checking Linux images |

Check `barn version` and `barn <command> --help` when working with another
version. Barn's supported interface is the command line; the Go `internal/`
packages are implementation details.
