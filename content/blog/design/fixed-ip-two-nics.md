---
title: "Why Every Barn Node Has Two NICs"
linkTitle: "Fixed IP, two NICs"
description: "Why Barn separates management egress from the fixed-address network used by the host, peers, Ansible, and Pigsty."
date: 2026-08-27T20:00:00+08:00
weight: 20
categories: [Design]
tags: [Networking, QEMU, Pigsty]
icon: fa-solid fa-network-wired
lastmod: 2026-10-26
---

This essay explains the Linux lab network architecture in Barn `0.9.2` ([macOS guests](/docs/start/macos/) use independent per-VM `vmnet` NAT subnets).

A Pigsty inventory identifies every database node by a stable IPv4 address: PostgreSQL streaming replication, Patroni/etcd consensus, HAProxy backends, keepalived VIPs, Prometheus targets, and Ansible playbooks all expect `10.10.10.11` to name the same host across boots. Forwarding a loopback port on the host can expose SSH or port `5432` to your laptop, but peer VMs cannot form a cluster over host loopback forwards.

At the same time, freshly booted cloud images need effortless outbound internet access to download packages without requiring you to maintain custom host NAT/MASQUERADE firewall rules. Barn solves both problems cleanly by giving every Linux node two virtual network interfaces (NICs).

## Two interfaces, two distinct jobs

| Interface | Addressing | Responsibility |
|---|---|---|
| Management NIC | QEMU user-mode NAT (`slirp`), DHCP | Outbound internet access, DNS, default route, and host-loopback SSH port forwarding |
| Fixed-IP lab NIC (MAC-matched) | Static RFC1918 `/24` inventory IP | Host-to-node, node-to-node, Ansible, Pigsty services, and L2 VIP traffic |
{.wide}

Barn binds each interface inside the guest by its deterministic MAC address rather than relying on kernel interface names (`eth0`, `enp0s4`, etc., which vary across distributions):

- **The management NIC** gives a new VM immediate outbound internet access, DNS resolution, and a host-loopback SSH forward (`127.0.0.1:<port>`) with zero host firewall configuration.
- **The fixed-IP lab NIC** configures the exact IPv4 address from `barn.yml` with no default gateway and no DNS servers. During `barn up`, guest bootstrap verifies this interface; if the fixed-IP link has an issue while management SSH is healthy, Barn marks the node ready with a `private-network` warning in `nodes[].warnings` so you can inspect the guest and re-run `barn up` after fixing the host bridge or route conflict.

> [!NOTE]
> Dual-NIC networking is built into every Barn Linux VM. See [Design](/docs/about/design/) for an overview of the Linux and macOS runtime architectures.

## The inventory owns the `/24` address plan

All managed nodes in a deployment share one canonical RFC1918 `/24` subnet:

| Address range | Allocation |
|---|---|
| `.1` | Host gateway interface on the private lab subnet |
| `.2`–`.8` | Reserved range (available for L2 VIPs; also bounds macOS `vmnet` DHCP) |
| `.9`–`.254` | Static node addresses declared in `barn.yml` |
{.wide}

Because `cloud-init` writes the static inventory address directly from `barn.yml` (on macOS, `socket_vmnet`'s DHCP pool ends at `.8`; on Linux, the `barn0` bridge uses static guest addressing), node IPs never depend on a DHCP lease database. Ansible and Pigsty use the exact same IP from the first `barn up` through every subsequent reboot.

When generating a fresh default template on a host where `10.10.10.0/24` is already in use, `barn setup` can automatically pick another free RFC1918 `/24`; explicit `-f` inventories and edited configurations always keep their declared subnet.

## Platform-native backends, identical guest topology

Inside the guest, every distribution sees the exact same two-NIC layout. On the host, Barn integrates with the platform's native network manager so QEMU always runs as an unprivileged user process:

- **macOS (`socket_vmnet`)**: Runs a pinned `socket_vmnet` launchd service (`host` mode by default, or `shared` mode with `--mode shared`) while QEMU runs under your normal user account.
- **Linux with active NetworkManager**: Creates and manages the `barn0` bridge via `nmcli` and integrates with active `firewalld` zones.
- **Linux with `systemd-networkd`**: Installs dedicated `barn0` networkd units and uses the distribution's `qemu-bridge-helper` for unprivileged tap attachment.
- **Linux with inactive `systemd-networkd`**: Before starting an inactive `systemd-networkd` service, Barn scans existing `.network` units on the host and proceeds only if none of them could claim a physical host interface—preventing a lab setup from disrupting workstation or server networking.

## Host networking as a reversible transaction

Because a host bridge or `socket_vmnet` service persists across CLI runs and requires `sudo` to install, Barn executes host network setup as a six-step reversible transaction:

1. **Inspect host state** — Checks routing tables, existing interfaces, active network services, file ownership, and prior Barn state.
2. **Display the plan** — Prints the exact files, interfaces, and service changes before requesting privileges.
3. **Re-verify preconditions** — Re-checks for route or interface collisions immediately before applying changes.
4. **Record root-owned rollback state** — Writes `/etc/barn/network.json` (or platform equivalent) recording both what Barn created and the prior host state.
5. **Smoke-test unprivileged QEMU attachment** — Verifies that an unprivileged QEMU process can attach to the bridge/socket before committing (rolling back automatically if the test fails).
6. **Commit after readiness** — Marks the network installation active only after all interface and service checks pass.
{.steps}

Barn never hijacks an existing non-Barn interface that happens to use `.1/24`, never overwrites modified files outside its recorded digest, and refuses `network uninstall` while lab VMs are running.

## Why this split works

Routing outbound internet traffic through QEMU's user-mode stack trades raw WAN throughput for zero-configuration portability, while keeping all latency-sensitive traffic—host-to-guest psql/SSH, PostgreSQL replication, etcd heartbeats, and local package mirror pulls from the `meta` node—on the fast, fixed-IP virtual bridge.

Read next: [Declarative Does Not Mean Destructive](/blog/design/convergence-without-surprise/).
