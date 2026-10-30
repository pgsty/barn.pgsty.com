---
title: Design
description: How Barn models Linux labs and macOS guests, with predictable state and explicit lifecycle changes.
weight: 20
icon: fa-solid fa-compass-drafting
aliases: [/docs/concepts/, /docs/concepts/networking/, /docs/concepts/storage/, /docs/concepts/safety/, /docs/architecture/, /docs/architecture/overview/, /docs/architecture/networking/, /docs/architecture/security/]
---

Barn provides two distinct virtualization workflows through one CLI: multi-node Linux labs and standalone macOS guests.

| Dimension | Linux labs (`barn …`) | macOS guests (`barn mac …`) |
|---|---|---|
| Hypervisor | QEMU with HVF or KVM (TCG for foreign architectures and `el8` on Apple Silicon) | Apple `Virtualization.framework` |
| Desired state | One Pigsty-compatible YAML inventory (`barn.yml`) | Named VMs configured via `barn mac` flags |
| State directory | `$BARN_HOME` (default `~/.barn`) | `$BARN_HOME/mac` (default `~/.barn/mac`) |
| Networking | User-mode management NIC + shared fixed-IP `/24` lab subnet | Dedicated `/24` NAT subnet and DHCP `.10` reservation per VM |
| Primary workloads | Database clusters, Ansible playbooks, multi-node Linux testing | macOS builds, GUI testing, isolated desktop environments |
{.wide}

The sections below summarize the Linux lab architecture; for the deeper rationale behind each decision, see the [Design Essays](/blog/design/), and for macOS guests see [macOS Guests](../../start/macos/) and [Mac Commands](../../reference/mac/).

## One Linux lab per user

Each Unix user manages one Linux lab deployment stored in `BARN_HOME` (default `~/.barn`) and driven by a single Pigsty-compatible YAML inventory (see [Why Barn Has No Projects](/blog/design/one-deployment-no-projects/)). Because deployment state lives in `BARN_HOME` rather than the working directory, lifecycle and access commands work from any directory.

## Node-level convergence

Barn computes a specification hash per node from the documented `vm_*` and Pigsty identity fields and records it alongside the node's committed state and QEMU process identity:

- `barn up` creates newly added nodes, starts stopped nodes, retries unfinished guest setup on running nodes without restarting their QEMU processes, and refreshes managed `/etc/hosts` and SSH entries.
- Changing an existing node's specification or removing a node from `barn.yml` never destroys a VM behind your back—modifications require `barn recreate`, and removals require `barn destroy` (see [Declarative Does Not Mean Destructive](/blog/design/convergence-without-surprise/)).

## Runtime selection

`vm_arch` applies across the entire deployment (`native` uses the host CPU architecture; explicit `amd64` or `arm64` selects that architecture from the catalog). Barn uses hardware acceleration (HVF on macOS, KVM on Linux) whenever guest and host architectures match, switching to QEMU TCG only for foreign architectures or catalog-declared kernel incompatibilities (`el8` `arm64` on Apple Silicon). If native HVF/KVM fails for any other reason, Barn fails closed rather than silently degrading to software emulation.

Each node's committed state records the effective architecture and accelerator (`barn status` displays both). Before executing a destructive `recreate`, Barn pre-validates the QEMU binary, version, network backend, base image bytes, boot mode, and firmware so a missing dependency never destroys a working VM.

## Two NICs, one fixed subnet

Every Linux VM attaches two virtual NICs (see [Why Every Barn Node Has Two NICs](/blog/design/fixed-ip-two-nics/)):

- **Management NIC**: QEMU user-mode networking providing DHCP, DNS, outbound internet access, and host-loopback SSH port forwarding without host firewall changes.
- **Fixed-IP lab NIC**: Carries the static RFC1918 `/24` address from `barn.yml` for host-to-node, node-to-node, and Ansible traffic.

To provide the fixed-IP subnet without running QEMU as root:

- **macOS hosts** run a pinned `socket_vmnet` daemon.
- **Linux hosts** use NetworkManager (`nmcli` managing `barn0`) when active, or `systemd-networkd` with the distribution `qemu-bridge-helper` (verifying beforehand that enabling an inactive `systemd-networkd` will not claim physical host interfaces). On Debian, `setup` grants `qemu-bridge-helper` access to a group containing the caller and smoke-tests an unprivileged QEMU attachment before committing the network transaction.

## Storage and configuration lifetimes

Desired configuration (`barn.yml`), applied deployment state (`$BARN_HOME`), and cached base images (`$BARN_HOME/images`) have independent lifecycles:

- Updating a catalog channel (`barn update`) does not rewrite existing VM root disks.
- Verified base images are stored read-only and shared across nodes via per-node `qcow2` copy-on-write root overlays.
- Ordinary `destroy` and `recreate` retain `persistent: true` data disks, while `up` automatically formats unrecognized or confirmed-corrupt data filesystems during guest recovery (see [Data Disks](../../reference/configuration/#data-disks) and [Storage and Access](../../start/storage/)).
- `barn image prune` protects images referenced by the active catalog, applied nodes, and `local-*` aliases (see [Images](../../reference/images/)).

## Safety boundary

QEMU processes and image downloads run as your normal user account; root privileges are used only during `setup`, `network install/uninstall`, and `hosts install/uninstall`. Before signaling a process or deleting a node file, Barn verifies file ownership, path containment, QMP UUID/name identity, process start-time/cmdline tuples, and the journal allowlist—stopping immediately if any check is ambiguous (see [A PID Is Not a Virtual Machine](/blog/design/identity-before-pid/)).
