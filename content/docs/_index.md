---
title: Farrow documentation
linkTitle: Docs
description: Start Farrow with two commands, then look up operations, configuration, and CLI contracts as needed.
weight: 10
icon: fa-solid fa-book
cascade:
  type: docs
---

Farrow turns one Pigsty-compatible Inventory into fixed-IP QEMU virtual
machines. It manages one deployment per Unix user; state lives under
`~/.farrow`, so lifecycle and SSH commands work from any directory.

Choose the shortest path for your task:

- **[Start](start/)** — boot the first lab with two commands, then operate and troubleshoot it.
- **[Reference](reference/)** — exact Inventory fields, commands, flags,
  output, and exit codes.
- **[About](about/)** — design, native validation, limits, and
  release gates.

New users should install Farrow 0.8.0 with the [Quick Start](start/tutorial/).
With the CLI installed, the normal path is `farrow up` to start the lab, then `farrow ssh` to connect.

> [!IMPORTANT]
> Version baseline, checked 2026-09-26: the public release is **0.8.0**;
> the reviewed local source `b91ec37` is an **unreleased 0.9 candidate**.
> Candidate-only changes are marked on their pages. See the
> [baseline and validation record](about/status/#documentation-baseline).
