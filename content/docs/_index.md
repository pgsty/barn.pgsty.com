---
title: Barn documentation
linkTitle: Docs
description: Install Barn 0.9.0, create your first Linux or macOS VM, and find the guides and reference for your next task.
weight: 10
icon: fa-solid fa-book
cascade:
  type: docs
---

Barn creates local virtual machines for development and testing. These docs cover
**Barn 0.9.0**. Start with [installation](start/installation/), then choose your guest:

| I want to… | Start here | What I need |
|---|---|---|
| Run a Linux VM or a multi-node lab | [Linux quick start](start/tutorial/) | A macOS or Linux host; Barn prepares QEMU and networking |
| Run macOS with a desktop and SSH | [macOS virtual machines](start/macos/) | Apple Silicon, macOS 27+, and the Barn Mac component |

The Linux path uses an Ansible-compatible YAML inventory, such as `barn.yml` or
`pigsty.yml`, and manages one lab per user. The `barn mac` path manages named
macOS machines independently. Both keep state under `~/.barn` by default;
changing directories does not create a new lab.

## After your first VM

- **Work with it:** [daily operations](start/operations/), [files and service access](start/storage/), [images](start/images/), and [automation](start/automation/).
- **Look something up:** [Linux configuration](reference/configuration/), [CLI options](reference/cli/), and [Mac commands](reference/mac/).
- **Get help:** [troubleshooting](start/troubleshooting/), [platforms and limits](about/status/), or [report an issue](https://github.com/pgsty/barn/issues).

Read [what changed in 0.9.0](../blog/release/0.9.0/) or explore the
[design](about/design/) and [contributor guide](start/source-build/) when you want to go deeper.
