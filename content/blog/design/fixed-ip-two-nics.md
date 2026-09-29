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

> [!NOTE]
> This article describes the **unreleased Barn 0.9.0 candidate**. See
> [Status](/docs/about/status/) for current validation and remaining release checks.

A Pigsty Inventory names machines by stable addresses. PostgreSQL replication,
etcd membership, HAProxy backends, VIPs, monitoring targets, and Ansible all
assume that `10.10.10.11` continues to mean the same node. A loopback port
forward can expose SSH or PostgreSQL to the host, but it cannot provide that
network identity to peers.

This is why Barn does not choose between a convenient NAT mode and an
advanced fixed-network mode. Every normal node gets both jobs, on separate
interfaces.

## One interface should not do two incompatible jobs

| Interface | Addressing | Responsibility |
| --- | --- | --- |
| management | QEMU user-mode NAT, DHCP | DNS, default route, outbound internet, and loopback SSH fallback |
| private, MAC-matched | fixed Inventory address | host-to-node, node-to-node, Ansible, Pigsty services, and VIP traffic |

Barn matches both virtual interfaces by their deterministic MAC addresses
and does not rename them. Guest-visible names are whatever the image's network
stack chooses (commonly `eth0` or `enp0s4`); the MAC and address contract, not
the display name, determines each interface's role.

The management interface is deliberately ordinary. It lets a new cloud image
reach package repositories before any application exists, without installing
NAT rules or a DHCP service on the host.

The private interface has one deterministic RFC1918 address, no default route,
and no DNS. Guest setup checks those properties, but since 0.7 private-network
checks are optional: a failure is recorded as a `private-network` warning and
does not prevent readiness when management SSH and guest identity are usable.
An operation can therefore succeed with limited fixed-IP connectivity. Before
deploying a service that needs this interface, inspect the warnings and test
the relevant host/peer connection. Repeat `up` after correcting the cause.

> [!NOTE]
> **Decision status: current.** The topology is part of Barn's normal
> lifecycle, not an optional “private mode.” See the
> [design reference](/docs/about/design/) for the current platform boundary.

## The Inventory owns the address plan

All managed hosts belong to one canonical RFC1918 `/24`:

| Range | Meaning |
| --- | --- |
| `.1` | host side of the private network |
| `.2`–`.8` | reserved boundary, including valid L2 VIP space |
| `.9`–`.254` | fixed node addresses |

The guest private interface does not request DHCP: cloud-init receives the
exact address already declared in the Inventory. On macOS, vmnet's configured
DHCP range ends at `.8`; managed node addresses begin at `.9`. Linux uses a
bridge with static guest addresses. The VM address contract therefore does not
depend on a lease database, and Ansible uses the same address throughout the
deployment.

For generated configuration, setup can choose from a small bounded set when
the default subnet is already occupied. An explicitly supplied Inventory is
never silently rewritten to escape a collision. The whole lab—host interface,
nodes, Pigsty addresses, and aliases—must agree on one subnet.

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

Supporting both Linux managers is not abstraction for its own sake. Starting
networkd on a desktop or RHEL-family host merely because Barn knows how to
write `.network` files can disrupt the host's real network. The backend must
follow the component already in charge.

## Host networking is a transaction

A bridge or vmnet daemon outlives one CLI process and crosses a privilege
boundary, so Barn treats installation as a reversible host transaction:

1. inspect routes, interfaces, services, ownership, and existing state;
2. print the exact plan before mutation;
3. re-check the preconditions immediately before apply;
4. write root-owned state describing what Barn created and what existed
   before it;
5. prove an unprivileged QEMU attachment;
6. accept the installation only after readiness checks pass.

A foreign interface that happens to use the same `.1/24` is not adopted. A
modified owned file is not overwritten. Uninstall refuses while recorded nodes
are live and restores only the prestate named by the manifest. Failure is a
reason to stop, not permission to delete whatever appears to be in the way.

## The accepted trade-off

Guest internet traffic uses QEMU's user-mode network. That is not the fastest
possible forwarding path, but it keeps ordinary egress unprivileged and
portable. The traffic that matters to a Pigsty lab—host-to-guest, replication,
service calls, and package distribution from a local control node—stays on the
private link.

The result is a useful separation of concerns: the management NIC makes a
machine easy to bootstrap; the private NIC makes it a stable member of the
lab. Neither has to pretend to be the other.

Read next: [Declarative does not mean destructive](/blog/design/convergence-without-surprise/).
