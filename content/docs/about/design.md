---
title: Design
description: How Barn models Linux labs and macOS guests, with predictable state and explicit lifecycle changes.
weight: 20
icon: fa-solid fa-compass-drafting
aliases: [/docs/concepts/, /docs/concepts/networking/, /docs/concepts/storage/, /docs/concepts/safety/, /docs/architecture/, /docs/architecture/overview/, /docs/architecture/networking/, /docs/architecture/security/]
---

Barn provides two workflows through one CLI: Linux labs and macOS guests.
Each workflow has its own configuration and lifecycle.

| | Linux labs | macOS guests |
| --- | --- | --- |
| Virtualization | QEMU with HVF or KVM; TCG for selected compatibility cases | Apple Virtualization.framework |
| Desired state | A Pigsty-compatible YAML inventory | Named machines configured with `barn mac` |
| State directory | `~/.barn` | `~/.barn/mac` |
| Networking | Management NIC plus a fixed-IP lab subnet | One NAT subnet and DHCP reservation per machine |
| Typical work | Database clusters, Linux development and automation | macOS builds, desktop tools and isolated development |

The sections below explain the Linux lab model. For the native macOS workflow,
see [macOS guests](../../start/macos/) and the [Mac reference](../../reference/mac/).

## One Linux lab per user

Each Unix user manages one Linux lab from one Pigsty-compatible inventory.
Barn stores its state under `BARN_HOME` (default `~/.barn`), independently of
the working directory. Changing directories therefore does not create another lab.

## Node-level convergence

`up` creates new nodes and starts selected nodes that are stopped. It leaves
running processes in place, retries unfinished guest setup, and updates managed
hosts and SSH entries. Changes to an existing node require an explicit recreate.
Removing a node from the inventory does not delete its VM.

To detect changes, Barn computes a hash from the documented VM and Pigsty-native
fields for each node. It stores that hash with the applied state and process identity.

## Runtime selection

The desired guest architecture applies to the whole deployment. If you omit
the architecture or select `native`, Barn uses the host architecture. An
explicit `amd64` or `arm64` selects that artifact from the image catalog.

Barn uses native HVF/KVM acceleration by default. It uses TCG software emulation
for a foreign architecture or an image/host incompatibility recorded in the catalog.
There is no user accelerator argument. Barn does not switch to TCG after other
native acceleration failures.

Barn records the effective architecture and accelerator in each QEMU invocation.
`status` shows these values. Before a destructive recreate, Barn verifies the
selected QEMU binary and version, network backend, image bytes, boot mode, and firmware.
If a Barn upgrade changes the runtime policy, recreate the whole deployment
to apply that policy. This keeps all nodes on the same runtime policy.

## Two NICs, one fixed subnet

Each Linux VM has two network interfaces (NICs). The management NIC supplies
DHCP, DNS, outbound access, and SSH through the host loopback address. The
fixed-IP NIC connects the host and nodes to each other, including for Ansible.
On macOS hosts, socket_vmnet provides this network.

On Linux, Barn uses NetworkManager if it is active. Otherwise, Barn uses
systemd-networkd and the distribution bridge helper. Before it starts inactive
networkd, Barn verifies that existing units cannot take control of a real host link.

On Debian, Barn temporarily grants bridge-helper access to a group that includes
the caller. Setup tests the bridge by running QEMU as that unprivileged user. If this test fails, setup automatically rolls back the
network installation.

## Storage and configuration have different lifetimes

The inventory records the desired VM definitions. Applied state records the
created resources, including the exact base image identity and runtime invocation.
A change to a catalog channel does not rewrite an existing root disk.

VMs share verified base images as read-only files. Each VM stores its root disk
changes in a separate file, called a root overlay. Normal destroy retains
persistent data disks, while explicit disk deletion or purge removes them.

Guest recovery can reset data filesystems that it cannot recognize or confirms
as damaged, including those on persistent disks. See
[Data disks](../../reference/configuration/#data-disks).

Cache pruning uses separate rules. It protects the active catalog and registered
local aliases. See [Storage and access](../../start/storage/) and
[Images](../../reference/images/).

## Safety boundary

QEMU runs as the caller. All guest artifacts belong to that user. Root
privileges are limited to host package installation, network setup, and optional
hosts updates.

Before destruction, Barn verifies ownership, path containment, node identity,
QMP/process identity, and the artifact allowlist. If any check is ambiguous,
Barn stops the operation.
