---
title: Project
linkTitle: Project
description: Supported platforms, design decisions, contribution, and release engineering for Barn.
weight: 30
icon: fa-solid fa-circle-info
no_list: true
cascade:
  type: docs
---

Barn (**Bootstrap And Run Nodes**) is an Apache-2.0 virtual machine manager for local database labs, Linux development, and macOS testing.

- [Platforms and Limits](status/) — Host requirements, guest compatibility matrix, and storage rules in Barn 0.9.2
- [Design](design/) — Architecture of the single-inventory Linux lab and independent `barn mac` VMs
- [Security and Trust](security/) — Host privileges, SSH credentials, shared folders, and image verification boundaries
- [Contributing](engineering/) — Source layout, local build and test gates, packaging snapshots, and catalog maintenance
- [Unreleased Changes](unreleased/) — Source changes to paths, sharing, selected nodes, and development limits
- [Validation History](history/) — Dated release verification records and native hypervisor test matrices
{.cards}

Follow the [release notes](/blog/release/) for version updates and the [design essays](/blog/design/) for architectural trade-offs. Bug reports and pull requests are welcome on [GitHub](https://github.com/pgsty/barn); please report security vulnerabilities privately through the [security policy](https://github.com/pgsty/barn/blob/main/SECURITY.md).
