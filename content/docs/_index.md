---
title: Barn documentation
linkTitle: Docs
description: Install Barn 1.0.0, create your first Linux or macOS VM, and find the guides and reference for your next task.
weight: 10
icon: fa-solid fa-book
cascade:
  type: docs
---

Barn provisions local virtual machines for development and testing. This documentation covers **Barn 1.0.0**, the first stable release; the [1.0.0 release notes](../blog/release/1.0.0/) summarize what changed since 0.9.3. Choose a starting workflow below:

- [Install Barn 1.0.0](start/installation/) — Install the CLI on macOS or Linux via Homebrew, the release installer script, or native packages.
- [Linux Quick Start](start/tutorial/) — Boot a single Ubuntu 24.04 node or a multi-node fixed-IP lab from an Ansible YAML inventory on macOS (HVF) or Linux (KVM).
- [Native macOS VMs](start/macos/) — Run isolated macOS 27+ machines on Apple Silicon with a native desktop window, SSH, VirtioFS shared folders, and clipboard sync.
{.cards}

## Common tasks

- [Daily operations](start/operations/) — Start, stop, inspect, plan changes, and recreate Linux lab nodes.
- [Storage and service access](start/storage/) — Add persistent data disks, mount Virtio-9p host shares, and reach guest ports.
- [Image selection](start/images/) — Choose from 9 Linux distribution families, update the catalog, or import custom `qcow2` images.
- [Scripting and automation](start/automation/) — Drive Barn from CI or shell scripts with `--yes`, `--json`, and structured exit codes.
- [Troubleshooting](start/troubleshooting/) — Diagnose host readiness, networking, SSH, and interrupted lifecycle runs with `barn doctor`.
- [What's new in 1.0.0](../blog/release/1.0.0/) — Review the 1.x compatibility scope, safer recreate and data-disk recovery, new confirmations, and upgrade notes.
{.cards}

## Browse by section
