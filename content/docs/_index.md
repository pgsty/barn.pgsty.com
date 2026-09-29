---
title: Barn documentation
linkTitle: Docs
description: Start Barn with two commands, then look up operations, configuration, and CLI contracts as needed.
weight: 10
icon: fa-solid fa-book
cascade:
  type: docs
---

Barn turns one Pigsty-compatible Inventory into fixed-IP QEMU virtual
machines. It manages one deployment per Unix user; state lives under
`~/.barn`, so lifecycle and SSH commands work from any directory.

Choose the shortest path for your task:

- **[Start](start/)** — boot the first lab with two commands, then operate and troubleshoot it.
- **[Reference](reference/)** — exact Inventory fields, commands, flags,
  output, and exit codes.
- **[About](about/)** — design, native validation, limits, and
  release gates.

Start with the [Quick Start](start/tutorial/) to prepare the **Barn 0.9.0 release candidate**
from source. Once the CLI is ready, run `barn up` to start the lab, then `barn ssh` to connect.

> [!IMPORTANT]
> 0.9.0 is the first Barn release and is not yet published. It uses the new
> commands, environment variables and fresh state, without compatibility or
> migration for earlier development builds. See [release and validation status](about/status/#documentation-baseline).
