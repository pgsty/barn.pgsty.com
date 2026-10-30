---
title: Guides
linkTitle: Guides
description: Install Barn, start a Linux or macOS VM, then manage machines, files, images, and automation.
weight: 10
icon: fa-solid fa-rocket
no_list: true
cascade:
  type: docs
---

These guides cover **Barn 0.9.2** and explicitly marked [Unreleased Changes](../about/unreleased/). You can run both Linux labs and isolated macOS VMs on the same Apple Silicon Mac—each workflow manages its own VMs under `~/.barn`.

## Get started

- [Install Barn](installation/) — Install the `0.9.2` CLI on macOS or Linux, check host requirements, and upgrade existing installations.
- [Linux Quick Start](tutorial/) — Bring up an Ubuntu 24.04 VM, connect over SSH, and scale to a multi-node fixed-IP lab from one `barn.yml`.
- [macOS Virtual Machines](macos/) — Create and manage macOS 27 guests on Apple Silicon with a native desktop, SSH, shared folders, and clipboard sync.
{.cards}

## Day-to-day Linux operations

- [Daily Operations](operations/) — Inspect status, stop and start nodes, preview inventory changes with `plan`, and `recreate` or `destroy` machines.
- [Storage and Access](storage/) — Configure persistent test data disks, transfer files over SSH, forward ports, and mount Virtio-9p host shares.
- [Image Repositories](images/) — Pick from 9 distribution families, switch to the China mirror, build a static image repository, or import a local `qcow2`.
- [Automation](automation/) — Run unattended host setup, validate `--json` output with `jq`, execute scripts via `barn provision`, and pair with Pigsty.
{.cards}

## Diagnostics, source builds, and cleanup

- [Troubleshooting](troubleshooting/) — Runbooks for host readiness, network repairs, guest stage warnings, SSH keys, and interrupted commands.
- [Build from Source](source-build/) — Compile the `v0.9.2` CLI, `barn-hosts-helper`, and native `Barn.app` bundle, and run contributor test gates.
- [Uninstall and Clean Up](uninstall/) — Tear down Linux and macOS VMs cleanly, prune image caches, remove host networking, and uninstall Barn.
{.cards}
