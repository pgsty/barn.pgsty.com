---
title: "Why Every Barn Node Has Two NICs"
linkTitle: "Fixed IP, two NICs"
description: "Why Barn separates management egress from the fixed-address network used by the host, peers, Ansible, and Pigsty."
date: 2026-08-27T20:00:00+08:00
weight: 20
categories: [Design]
tags: [Networking, QEMU, Pigsty]
icon: fa-solid fa-network-wired
lastmod: 2026-09-29
---

This article explains the Linux network design in Barn 0.9.0. [Mac machines](/docs/start/macos/) are managed independently.

A Pigsty inventory identifies nodes by stable addresses. PostgreSQL replication, etcd membership, HAProxy backends, VIPs, monitoring targets, and Ansible require `10.10.10.11` to identify the same node. A loopback port
forward can expose SSH or PostgreSQL to the host, but it cannot provide that
network identity to peers.

Barn therefore gives every normal node two interfaces: one for NAT connectivity and one for a fixed network address.

## One interface should not do two incompatible jobs

| Interface | Addressing | Responsibility |
| --- | --- | --- |
| management | QEMU user-mode NAT, DHCP | DNS, default route, outbound internet, and loopback SSH fallback |
| private, MAC-matched | fixed inventory address | host-to-node, node-to-node, Ansible, Pigsty services, and VIP traffic |

Barn matches both virtual interfaces by their deterministic MAC addresses, without renaming them. The image's network stack selects guest-visible names, commonly `eth0` or `enp0s4`; MAC and address settings determine each interface's role.

The management interface lets a new cloud image reach package repositories before applications are installed. The host does not need additional NAT rules or a DHCP service.

The private interface has one deterministic RFC1918 address, no default route, and no DNS. Guest setup checks these properties. Since 0.7, a failed private-network check produces a `private-network` warning but does not prevent readiness if management SSH and guest identity are usable.
An operation can therefore succeed with limited fixed-IP connectivity. Before
deploying a service that needs this interface, inspect the warnings and test
the relevant host/peer connection. Repeat `up` after correcting the cause.

> [!NOTE]
> The topology is part of Barn's normal
> lifecycle, not an optional “private mode.” See the
> [design reference](/docs/about/design/) for the current platform boundary.

## The inventory owns the address plan

All managed hosts belong to one canonical RFC1918 `/24`:

| Range | Meaning |
| --- | --- |
| `.1` | host side of the private network |
| `.2`–`.8` | reserved boundary, including valid L2 VIP space |
| `.9`–`.254` | fixed node addresses |

The guest private interface does not request DHCP: cloud-init receives the
exact address already declared in the inventory. On macOS, vmnet's configured
DHCP range ends at `.8`; managed node addresses begin at `.9`. Linux uses a
bridge with static guest addresses. The VM address contract therefore does not
depend on a lease database, and Ansible uses the same address throughout the
deployment.

For generated configuration, setup can choose from a bounded set if the default subnet is occupied. Barn does not rewrite an explicitly supplied inventory to avoid a collision.
The host interface, nodes, Pigsty addresses, and aliases must use the same subnet.

## Platform-specific backend, identical guest contract

The guest sees the same topology on every supported host, while Barn follows
the host's native networking owner:

- **macOS:** a pinned `socket_vmnet` service provides the private link. Host
  mode is the default; shared mode is explicit. QEMU still runs as the user.
- **Linux with active NetworkManager:** Barn creates an owned `barn0`
  bridge through `nmcli` and integrates with active firewalld policy.
- **Linux with systemd-networkd:** Barn installs owned units and uses the
  distribution `qemu-bridge-helper` so QEMU remains unprivileged.
- **Inactive networkd:** activation is allowed only after a pre-mutation scan
  proves that existing units cannot claim a real host interface.

Starting networkd on a desktop or RHEL-family host can disrupt its network. The ability to write `.network` files does not make activation safe.
Barn therefore uses the network manager that already controls the host.

## Host networking is a transaction

Because a bridge or vmnet daemon outlives the CLI and its installation requires privileges, Barn uses a reversible host transaction:

1. inspect routes, interfaces, services, ownership, and existing state;
2. print the exact plan before mutation;
3. re-check the preconditions immediately before apply;
4. write root-owned state describing what Barn created and what existed
   before it;
5. prove an unprivileged QEMU attachment;
6. accept the installation only after readiness checks pass.

Barn does not adopt a foreign interface that uses the same `.1/24`. It does not overwrite a modified owned file.
Uninstall refuses while recorded nodes are running. It restores only the previous state recorded in the manifest. A failure stops the operation without authorizing additional deletion.

## The accepted trade-off

Guest internet traffic uses QEMU's user-mode network. This path trades forwarding speed for unprivileged, portable internet access.
The private link carries host-to-guest traffic, replication, service calls, and package distribution from a local control node.

The management NIC lets the guest initialize itself, while the private NIC gives it the stable address the lab requires.

Read next: [Declarative does not mean destructive](/blog/design/convergence-without-surprise/).
