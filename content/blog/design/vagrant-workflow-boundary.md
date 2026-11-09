---
title: "What Barn Can Learn from Vagrant"
linkTitle: "Vagrant and the development loop"
description: "A proposal for repeatable provisioning, environment records, file transfer, and recovery in Pigsty labs."
date: 2026-11-08T10:00:00+08:00
weight: 70
categories: [Design]
tags: [Vagrant, Pigsty, Workflow]
icon: fa-solid fa-arrows-rotate
lastmod: 2026-11-08
---

Barn already creates multi-node Linux labs from Pigsty-compatible inventories, manages their lifecycle, and exposes SSH and structured output. The useful lessons from Vagrant concern what happens between creating a VM and repeating an experiment: run setup steps, move source and build artifacts, record the environment, and return to a known state.

This is a design proposal based on the Barn source reviewed on **2026-11-08**. The priorities below are candidates for implementation, with no assigned release or delivery date. Current commands are documented in the [CLI reference](/docs/reference/cli/).

## Existing capabilities and actual gaps {#capabilities}

| Workflow | Barn today | Design opportunity |
|---|---|---|
| Define a lab | Static inventory, inherited group variables, per-node images/resources/disks, node selection | Reusable recipes; group selection would need its own contract |
| Converge nodes | `plan`, `up`, explicit `resize`, `recreate`, and `destroy` | Preserve the rule that an omitted node never authorizes deletion |
| Configure guests | Manually rerunnable Bash `provision`, with sudo, timeout, concurrency, and script digest | Named steps and execution policies attached to the lifecycle |
| Move files | Virtio-9p host shares and OpenSSH connection export | Integrated upload/download and optional one-way rsync |
| Restore an experiment | Persistent disks survive ordinary destroy/recreate | Named cold snapshots covering all participating state |
| Reproduce images | Signed catalogs, exact releases, import, cache, and static repository tools | A portable environment record and capture of a configured VM |
| Reach services | Fixed private addresses and loopback management SSH | User-declared service forwards with explicit bind addresses |
{.wide .expand}

`barn provision` already reruns a script on demand. Its digest records what ran; it does not make the script idempotent or skip an identical script. Inventory groups already supply variable inheritance, while operation selectors identify nodes. Persistent disks retain data across lifecycle operations but do not provide a point-in-time restore.

These distinctions follow the [command definitions](https://github.com/pgsty/barn/tree/main/cmd/barn), [inventory parser](https://github.com/pgsty/barn/blob/main/internal/config/inventory.go), and [provision executor](https://github.com/pgsty/barn/tree/main/internal/provision). Internal forwarding structures and functions named “snapshot” or “commit” should be evaluated by their exposed behavior before being counted as product features.

## Keep the Pigsty integration small {#pigsty}

Pigsty needs stable private node addresses, data disks, an administrator account, SSH access, and a way to deliver deployment code. Barn supplies the VM layer; Pigsty and Ansible continue to own database and service configuration.

The first integration should reuse `barn ssh-config` and preserve its endpoint, key, known-hosts file, and VM identity. A guest's private IP and its host-side loopback SSH endpoint serve different purposes. Scripts using scp, rsync, or Ansible need the connection parameters as well as the inventory address. When replacing Vagrant-generated SSH fragments, define which tool owns each fragment so an older OpenSSH entry cannot take precedence.

A Vagrant box name also needs an explicit mapping to a Barn image reference. The formats carry different metadata. Multiple distribution families can share one Barn inventory, but the guest architecture is deployment-wide; architecture build matrices should run as separate lab jobs under the current single-deployment model.

This keeps the [fixed-IP network](/blog/design/fixed-ip-two-nics/) and [single deployment](/blog/design/one-deployment-no-projects/) useful while avoiding a second service orchestrator.

## Proposed implementation order {#priorities}

| Priority | Minimum scope | Acceptance condition |
|---|---|---|
| P0: named provisioning | Ordered shell steps, first-run/every-run policy, explicit selection and retry; external Ansible invocation | Retry one failed step without replaying successful steps; report node, step, exit code, and script digest |
| P0: environment record | Exact image release/digest/architecture, catalog revision, resolved VM specifications, and script digests | Rebuild the topology from retained artifacts in a fresh temporary `BARN_HOME`; image identities match and `plan` is clean |
| P1: file transfer | Upload/download over the existing SSH contract, then optional one-way rsync | Build on guest-local storage, retrieve artifacts, and verify their hashes |
| P1: cold snapshots | Start with a stopped Linux VM; define root/data disks, backing chains, NVRAM, specification, and identity together | Restore files, mounts, and guest identity to the saved state without changing unselected nodes |
| P1: service forwards | Explicit bind address and host/guest ports, conflict handling, structured reporting | Services remain reachable after restart; LAN exposure requires an explicit address |
| P1: VM capture | Stop, flatten backing dependencies, remove machine/SSH credentials, and emit qcow2 plus metadata | Import into a fresh lab and reach SSH with a new identity |
{.wide .expand}

Vagrant's [named provisioning and run policies](https://developer.hashicorp.com/vagrant/docs/provisioning/basic_usage), built-in [upload](https://developer.hashicorp.com/vagrant/docs/cli/upload), and [one-way rsync](https://developer.hashicorp.com/vagrant/docs/synced-folders/rsync) provide useful reference behavior. Its [snapshots](https://developer.hashicorp.com/vagrant/docs/cli/snapshot) depend on provider support, and [`package`](https://developer.hashicorp.com/vagrant/docs/cli/package) documents VirtualBox and Hyper-V support. Barn needs explicit guarantees for its own backends.

An environment record must retain access to the exact image bytes. A numeric version prefix can resolve differently after a catalog update; even a complete version cannot recover a removed artifact. VM disks and exported images belong in artifact storage, while recipes, manifests, and digests can be committed.

## Changes that need a separate product decision {#scope}

Different `BARN_HOME` roots already separate stored state and runtime sockets. Complete concurrent-project support also needs network, port, and SSH ownership because those host integrations still share resources. More NICs or subnets expand the network validation matrix. Both are later candidates that should be driven by a concrete lab requirement. A Windows backend, a general provider/plugin API, and memory-state suspension each need independent design and maintenance commitments.

Evaluate the first additions against three workflows: a Pigsty multi-node PostgreSQL lab, a distribution/architecture extension-build matrix, and a single development VM with source upload and artifact retrieval. A successful change reduces manual steps in those workflows while preserving explicit destruction, verified image inputs, and stable machine-readable output.
