---
title: Host Network Commands
description: Inspect, install, and remove the fixed-IP network used by Linux guests.
weight: 60
date: 2026-11-11
---

Inspect, install, and remove the fixed-IP network used by Linux guests.

Availability labels distinguish **1.1.0**, **local main**, and **working tree**; see the [version baseline](/docs/reference/commands/#versions). All commands inherit the [global options](/docs/reference/commands/#global-options).

## `barn network status` {#barn-network-status}

```text
barn network status [flags]
```

Inspect the one host-wide Linux-guest network: backend, installed CIDR, ownership, health, and lifecycle preflight findings. `--cidr` checks an expected subnet; omitting it inspects the installed one. It is read-only. This network is separate from each native Mac VM’s private network.

Aliases: `st`.

| Option | Meaning / default | Available in |
|---|---|---|
| `-c, --cidr string` | Optional expected private /24; otherwise inspect the installed subnet | 1.1.0 |
{.wide .expand}

```bash
barn network status
barn --json network status --cidr 10.10.10.0/24
```

## `barn network install` {#barn-network-install}

```text
barn network install [flags]
```

Inspect or install the host-wide backend: `socket_vmnet` on macOS or `barn0` through the active Linux network manager. On a terminal it shows a privileged plan and asks; structured/noninteractive calls only preview unless `--yes` is supplied. On a fresh Mac, use `setup` to obtain the pinned socket_vmnet archive first.

`--archive` and `--interface-id` are macOS-only. `host`/`shared` are macOS vmnet modes; Linux rejects `shared`. An existing network must match the chosen configuration; review status before changing subnet or mode.

Aliases: `i`.

| Option | Meaning / default | Available in |
|---|---|---|
| `-a, --archive string` | macOS: pinned socket_vmnet archive | 1.1.0 |
| `-c, --cidr string` | network: an RFC1918 IPv4 /24 (default "10.10.10.0/24") | 1.1.0 |
| `-i, --interface-id string` | macOS: persistent vmnet UUID | 1.1.0 |
| `-m, --mode string` | macOS vmnet mode: host or shared (default "host") | 1.1.0 |
| `-y, --yes` | apply the displayed privileged plan without confirmation (sudo may still ask for a password) | 1.1.0 |
{.wide .expand}

```bash
barn network install --json
barn network install --cidr 10.10.10.0/24 --yes
```

## `barn network uninstall` {#barn-network-uninstall}

```text
barn network uninstall [flags]
```

Remove only Barn-owned network configuration and restore recorded host settings. Stop running Linux guests first: the operation refuses a live deployment. Terminal mode asks after showing the plan; structured/noninteractive calls preview unless `--yes` is set. This does not delete VM disks or native Mac networks.

Aliases: `u`.

| Option | Meaning / default | Available in |
|---|---|---|
| `-y, --yes` | apply the displayed privileged plan without confirmation (sudo may still ask for a password) | 1.1.0 |
{.wide .expand}

```bash
barn stop
barn network uninstall --json
barn network uninstall --yes
```

## Implementation {#implementation}

[command_network.go](https://github.com/pgsty/barn/blob/v1.1.0/cmd/barn/command_network.go)

The [version baseline](/docs/reference/commands/#versions) records the additional local commits and uncommitted extension checked on 2026-11-11.
