---
title: Barn documentation
linkTitle: Docs
description: Install Barn 0.9.1, create your first Linux or macOS VM, and find the guides and reference for your next task.
weight: 10
icon: fa-solid fa-book
cascade:
  type: docs
---

Barn creates local virtual machines for development and testing. These docs cover
**Barn 0.9.1**. Start with [installation](start/installation/), then choose your guest:

| I want to… | Start here | What I need |
|---|---|---|
| Run a Linux VM or a multi-node lab | [Linux quick start](start/tutorial/) | A macOS or Linux host; Barn prepares QEMU and networking |
| Run macOS with a desktop and SSH | [macOS virtual machines](start/macos/) | Apple Silicon, macOS 27+, and the Barn.app component |

For Linux, define your nodes in an Ansible-compatible YAML inventory, such as
`barn.yml` or `pigsty.yml`. Barn manages one Linux lab per user, regardless of
the working directory. For macOS, use `barn mac` to manage each machine by name.
Barn stores both kinds of VM state under `~/.barn` by default.

## After your first VM

- For daily tasks, see [daily operations](start/operations/), [files and service access](start/storage/), [images](start/images/), and [automation](start/automation/).
- For specific settings, see [Linux configuration](reference/configuration/), [CLI options](reference/cli/), and [Mac commands](reference/mac/).
- For help, see [troubleshooting](start/troubleshooting/), [platforms and limits](about/status/), or [report an issue](https://github.com/pgsty/barn/issues).

Read [what changed in 0.9.1](../blog/release/0.9.1/) for release details.
For implementation and build details, see the [design](about/design/) and
[contributor guide](start/source-build/).
