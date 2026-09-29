---
title: Start
linkTitle: Start
description: Start Farrow with up, connect with ssh, and read the other guides only when needed.
weight: 10
icon: fa-solid fa-rocket
cascade:
  type: docs
---

With Farrow installed, new users can start a test lab with the [Quick Start](tutorial/):

```bash
farrow up
farrow ssh
```

When no inventory or deployment exists, interactive `up` creates the default
inventory. It can prepare missing host dependencies and networking. Repeat `farrow up` to retry unfinished guest setup without
restarting healthy VMs. For unattended setup, run `farrow setup --yes` before
`farrow up`.

Package availability is recorded on [Status](../about/status/); developers and
source reviewers can use [Build from Source](source-build/).

Everything else is separated by task:

1. [Daily Operations](operations/) — status, access, start/stop, changes,
   scale-in, and destroy.
2. [Troubleshooting](troubleshooting/) — diagnostics and common fixes.
3. [Image Repositories](images/) — choose images, use mirrors, import, and
   prune the cache.
4. [Build from Source](source-build/) — developer builds, checks, and local
   PATH setup.
5. [Uninstall and Clean Up](uninstall/) — remove the deployment, images,
   networking, and state.
6. [Automation and Guest Scripts](automation/) — unattended setup, JSON acceptance,
   repeatable guest commands, and the Pigsty handoff.
7. [Storage and Access](storage/) — disk retention, file transfer, SSH tunnels,
   and Linux directory sharing.
8. [macOS Virtual Machines](macos/) — unreleased `farrow mac`: macOS 27 guests
   on Apple Silicon with desktop, SSH, shared folders, and clipboard.
