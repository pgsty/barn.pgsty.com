---
title: Linux Lifecycle
description: Plan, create, start, resize, inspect, and explicitly remove Linux virtual machines.
weight: 20
date: 2026-11-11
---

Plan, create, start, resize, inspect, and explicitly remove Linux virtual machines.

This reference covers **Barn 1.2.0**. Option tables distinguish options also available in **1.1.0** from additions in **1.2.0**; see the [version baseline](/docs/reference/commands/#versions). All commands inherit the [global options](/docs/reference/commands/#global-options).

Node arguments are resolved names such as `meta` and `node-1`. Omit them to select all nodes in the command’s inventory/applied scope. IP addresses, groups, and `vm_alias` are not selectors. `plan`, `up`, `reload`, `resize`, and `recreate` read `-f`, then the current directory’s inventory, then applied state. Other lifecycle commands use applied state directly.

Specification overrides, scaling, and their environment variables are defined in [Configuration](../../configuration/#specification-overrides). The 1.2.0 concurrency option applies only where `--parallel` is listed; `plan`, `resize`, and `status` do not accept it. For structured results and exit codes, see [CLI contracts](../../cli/#lifecycle-results).

## `barn plan` {#barn-plan}

```text
barn plan [node...] [flags]
```

Compare the effective desired inventory with applied state without changing VMs or downloading images. Report exact images, resources, per-disk actions, and nodes needing creation, resize, recreation, start, or explicit removal. Catalog images need only local metadata; inspecting a named local image also needs `qemu-img`.

Exit `0` means the plan was produced, including plans blocked by omitted nodes. Automation must inspect `action`, `blocked`, and the change arrays. Explicit selectors retain the applied definitions of unselected peers. [Planning output](../../cli/#planning) describes the result.

Aliases: `pl`.

| Option | Meaning / default | Available in |
|---|---|---|
| `-A, --arch string` | override deployment vm_arch: native, amd64, or arm64; environment overrides require 1.2.0 | 1.1.0 |
| `-C, --cpu string` | Base vCPUs before scale, integer 1–256; effective CPU count is also limited to 256; overrides BARN_CPU | 1.2.0 |
| `-D, --disk string` | Absolute root capacity, at least the base virtual size; bare integer means GiB; overrides BARN_DISK | 1.2.0 |
| `-f, --file string` | desired inventory; defaults to the discovered inventory, then the applied state | 1.1.0 |
| `-I, --image string` | override vm_image/vm_version for selected nodes; environment overrides require 1.2.0 | 1.1.0 |
| `-M, --mem string` | Base memory before scale, minimum 512 MiB; bare integer means MiB; overrides BARN_MEM | 1.2.0 |
| `-r, --repo string` | image repository URL or directory; overrides $BARN_REPO | 1.1.0 |
| `-S, --scale string` | Integer 1–256 multiplying base CPU and memory only; disk does not scale; overrides BARN_SCALE | 1.2.0 |
{.wide .expand}

```bash
barn plan
barn plan -f pigsty.yml meta
barn --json plan -I u24 -A amd64
```

## `barn up` {#barn-up}

```text
barn up [node...] [flags]
```

Create missing nodes, start stopped nodes, and retry unfinished guest setup while keeping healthy running VMs alive. It waits for management SSH unless `--no-wait` is set, and refreshes host SSH aliases and guest host/control-node entries. Non-fatal guest setup problems appear in `warnings`; ready nodes still succeed.

On an interactive first run, it can prepare missing host dependencies and generate `meta` when no inventory or applied deployment exists. Scripts should run `setup --yes` first. Existing definition changes require `resize` or `recreate`; inventory omissions require explicit `destroy`. `--rollback` only removes safe, uncommitted artifacts from preparation failures in this run.

| Option | Meaning / default | Available in |
|---|---|---|
| `-A, --arch string` | override deployment vm_arch: native, amd64, or arm64; environment overrides require 1.2.0 | 1.1.0 |
| `-C, --cpu string` | Base vCPUs before scale, integer 1–256; effective CPU count is also limited to 256; overrides BARN_CPU | 1.2.0 |
| `-D, --disk string` | Absolute root capacity, at least the base virtual size; bare integer means GiB; overrides BARN_DISK | 1.2.0 |
| `-f, --file string` | desired inventory; defaults to the discovered inventory, then the applied state | 1.1.0 |
| `-I, --image string` | override vm_image/vm_version for selected nodes; environment overrides require 1.2.0 | 1.1.0 |
| `-M, --mem string` | Base memory before scale, minimum 512 MiB; bare integer means MiB; overrides BARN_MEM | 1.2.0 |
| `--mirror` | use the China official repository at repo.pigsty.cc; overridden by `--repo` | 1.1.0 |
| `-n, --no-wait` | return once QEMU is running, without waiting for the guest to boot | 1.1.0 |
| `-p, --parallel int` | Node concurrency: omitted = max(1, logical CPUs - 2); 0 = all selected nodes; positive = limit | 1.2.0 |
| `-r, --repo string` | image repository URL or directory; overrides `--mirror` and $BARN_REPO | 1.1.0 |
| `--rollback` | remove safe artifacts from nodes that fail to prepare | 1.1.0 |
| `-S, --scale string` | Integer 1–256 multiplying base CPU and memory only; disk does not scale; overrides BARN_SCALE | 1.2.0 |
{.wide .expand}

```bash
barn up
barn up -f pigsty.yml meta
barn up --mirror --rollback
barn up meta --no-wait
```

## `barn start` {#barn-start}

```text
barn start [node...] [flags]
```

Start selected stopped nodes from applied state and wait for SSH. It works from any directory using the same `BARN_HOME`, without reading an inventory or creating nodes. It refreshes SSH access; use `up` to retry unfinished guest setup on an already-running VM. An unavailable share fails its node while independent nodes continue.

| Option | Meaning / default | Available in |
|---|---|---|
| `-n, --no-wait` | return once QEMU is running, without waiting for the guest to boot | 1.1.0 |
| `-p, --parallel int` | Node concurrency: omitted = max(1, logical CPUs - 2); 0 = all selected nodes; positive = limit | 1.2.0 |
{.wide .expand}

```bash
barn start
barn start meta --no-wait
```

## `barn stop` {#barn-stop}

```text
barn stop [node...] [flags]
```

Stop selected running Linux VMs using their recorded process identities. It retains root disks, data disks, keys, and deployment state. With no names, stop the whole Linux deployment; it does not stop named macOS VMs or remove the host network.

| Option | Meaning / default | Available in |
|---|---|---|
| `-p, --parallel int` | Node concurrency: omitted = max(1, logical CPUs - 2); 0 = all selected nodes; positive = limit | 1.2.0 |
{.wide .expand}

```bash
barn stop meta
barn stop
```

## `barn restart` {#barn-restart}

```text
barn restart [node...] [flags]
```

Stop and start existing nodes using applied state. Inventory edits are not read. Use `reload` to re-read an inventory, or `resize`/`recreate` to apply changed definitions. It waits for SSH unless `--no-wait` is set.

| Option | Meaning / default | Available in |
|---|---|---|
| `-n, --no-wait` | return once QEMU is running, without waiting for the guest to boot | 1.1.0 |
| `-p, --parallel int` | Node concurrency: omitted = max(1, logical CPUs - 2); 0 = all selected nodes; positive = limit | 1.2.0 |
{.wide .expand}

```bash
barn restart
barn restart meta --no-wait
```

## `barn reload` {#barn-reload}

```text
barn reload [node...] [flags]
```

Validate the desired specification and startup dependencies before stopping selected nodes, then converge them through `up`. It can create newly added nodes. Changes requiring resize or recreation, and omitted applied nodes, fail preflight before any VM stops. Use `restart` when you want only the recorded configuration.

| Option | Meaning / default | Available in |
|---|---|---|
| `-A, --arch string` | override deployment vm_arch: native, amd64, or arm64; environment overrides require 1.2.0 | 1.1.0 |
| `-C, --cpu string` | Base vCPUs before scale, integer 1–256; effective CPU count is also limited to 256; overrides BARN_CPU | 1.2.0 |
| `-D, --disk string` | Absolute root capacity, at least the base virtual size; bare integer means GiB; overrides BARN_DISK | 1.2.0 |
| `-f, --file string` | desired inventory; defaults to the discovered inventory, then the applied state | 1.1.0 |
| `-I, --image string` | override vm_image/vm_version for selected nodes; environment overrides require 1.2.0 | 1.1.0 |
| `-M, --mem string` | Base memory before scale, minimum 512 MiB; bare integer means MiB; overrides BARN_MEM | 1.2.0 |
| `--mirror` | use the China official repository at repo.pigsty.cc; overridden by `--repo` | 1.1.0 |
| `-n, --no-wait` | return once QEMU is running, without waiting for the guest to boot | 1.1.0 |
| `-p, --parallel int` | Node concurrency: omitted = max(1, logical CPUs - 2); 0 = all selected nodes; positive = limit | 1.2.0 |
| `-r, --repo string` | image repository URL or directory; overrides `--mirror` and $BARN_REPO | 1.1.0 |
| `--rollback` | remove safe artifacts from nodes that fail to prepare | 1.1.0 |
| `-S, --scale string` | Integer 1–256 multiplying base CPU and memory only; disk does not scale; overrides BARN_SCALE | 1.2.0 |
{.wide .expand}

```bash
barn reload -f pigsty.yml
barn reload meta --mirror
```

## `barn resize` {#barn-resize}

```text
barn resize [node...] [flags]
```

Apply CPU and memory changes while preserving VM identity, disks, and SSH keys. Supported increases use hotplug; decreases or unsupported live changes use a stop/start fallback. Stable 1.1.0 reads CPU/memory changes from the inventory. Image, architecture, data-disk, network, share, create, and remove changes cannot be applied by resize.

Barn 1.2.0 additionally accepts resource flags and grows the existing root with `-D 128GiB`. Root growth stops QEMU, expands its image, boots the guest to grow and verify a last plain ext4/XFS root partition, then restores an initially stopped VM to stopped. Targets must grow and align to 512 bytes. Retry an interrupted growth with the same target; shrinking, LVM, encrypted roots, and non-last partitions are unsupported. See [root growth and recovery](../../cli/#root-disk-growth). CLI overrides do not rewrite the inventory.

| Option | Meaning / default | Available in |
|---|---|---|
| `-A, --arch string` | override deployment vm_arch: native, amd64, or arm64; environment overrides require 1.2.0 | 1.1.0 |
| `-C, --cpu string` | Base vCPUs before scale, integer 1–256; effective CPU count is also limited to 256; overrides BARN_CPU | 1.2.0 |
| `-D, --disk string` | Absolute root capacity, at least the base virtual size; bare integer means GiB; overrides BARN_DISK | 1.2.0 |
| `-f, --file string` | desired inventory; defaults to the discovered inventory, then the applied state | 1.1.0 |
| `-I, --image string` | override vm_image/vm_version for selected nodes; environment overrides require 1.2.0 | 1.1.0 |
| `-M, --mem string` | Base memory before scale, minimum 512 MiB; bare integer means MiB; overrides BARN_MEM | 1.2.0 |
| `-S, --scale string` | Integer 1–256 multiplying base CPU and memory only; disk does not scale; overrides BARN_SCALE | 1.2.0 |
{.wide .expand}

```bash
barn plan -f pigsty.yml meta
barn resize -f pigsty.yml meta
barn --json status meta
```

## `barn recreate` {#barn-recreate}

```text
barn recreate [node...] [flags]
```

Replace the selected VMs from the desired inventory. This deletes their root disks and non-persistent data disks; compatible persistent data disks are reattached. Inspect `plan` first. A terminal asks you to type `recreate`; scripts require `--yes` or `--force` (no `-y`).

No selector means the whole inventory. If it omits an applied node, the operation fails before stopping VMs; explicitly destroy that node or restore it in the inventory. Selected recreation preserves unselected peers. A successful recreation also refreshes SSH access.

Aliases: `rc`.

| Option | Meaning / default | Available in |
|---|---|---|
| `-A, --arch string` | override deployment vm_arch: native, amd64, or arm64; environment overrides require 1.2.0 | 1.1.0 |
| `-C, --cpu string` | Base vCPUs before scale, integer 1–256; effective CPU count is also limited to 256; overrides BARN_CPU | 1.2.0 |
| `-D, --disk string` | Absolute root capacity, at least the base virtual size; bare integer means GiB; overrides BARN_DISK | 1.2.0 |
| `-f, --file string` | desired inventory; defaults to the discovered inventory, then the applied state | 1.1.0 |
| `--force` | recreate without the interactive confirmation (required without a terminal) | 1.1.0 |
| `-I, --image string` | override vm_image/vm_version for selected nodes; environment overrides require 1.2.0 | 1.1.0 |
| `-M, --mem string` | Base memory before scale, minimum 512 MiB; bare integer means MiB; overrides BARN_MEM | 1.2.0 |
| `--mirror` | use the China official repository at repo.pigsty.cc; overridden by `--repo` | 1.1.0 |
| `-n, --no-wait` | return once QEMU is running, without waiting for the guest to boot | 1.1.0 |
| `-p, --parallel int` | Node concurrency: omitted = max(1, logical CPUs - 2); 0 = all selected nodes; positive = limit | 1.2.0 |
| `-r, --repo string` | image repository URL or directory; overrides `--mirror` and $BARN_REPO | 1.1.0 |
| `-S, --scale string` | Integer 1–256 multiplying base CPU and memory only; disk does not scale; overrides BARN_SCALE | 1.2.0 |
| `--yes` | same as `--force` | 1.1.0 |
{.wide .expand}

```bash
barn plan meta
barn recreate meta
barn recreate -f pigsty.yml meta --yes
```

## `barn status` {#barn-status}

```text
barn status [node...] [flags]
```

Inspect recorded node configuration and live QEMU process identity without requiring the inventory directory. `running` reports a verified VM process, not an SSH readiness probe. `--verbose` adds runtime details; `--json` exposes node records, active-operation notes, and failures. A degraded node can produce exit `5` while healthy peers are still listed. The 1.2.0 text output uses compact `SPEC` values such as `2c4g`.

Aliases: `st`.

No local options beyond `--help`; global presentation options still apply.

```bash
barn status
barn status meta --verbose
barn --json status
```

## `barn destroy` {#barn-destroy}

```text
barn destroy [node...] [flags]
```

Delete selected VMs, or the whole deployment without selectors. Root and non-persistent data disks are deleted; persistent data disks are retained unless a whole-deployment deletion flag is explicit. Terminal confirmation requires typing `destroy`; scripts need `--yes` or `--force`, with no `-y`.

`--delete-persistent` and `--purge` require whole-deployment scope. `--purge` also removes deployment keys and state. The image cache, host network, and native Mac VMs remain. Removing the control node promotes the first remaining node; update `admin_ip` and run `up` to configure its control SSH access.

Aliases: `de`.

| Option | Meaning / default | Available in |
|---|---|---|
| `--delete-persistent` | also delete owned persistent data disks | 1.1.0 |
| `--force` | destroy without the interactive confirmation (required without a terminal) | 1.1.0 |
| `-p, --parallel int` | Node concurrency: omitted = max(1, logical CPUs - 2); 0 = all selected nodes; positive = limit | 1.2.0 |
| `--purge` | terminal disposal: also delete persistent disks, keys, and deployment state | 1.1.0 |
| `--yes` | same as `--force` | 1.1.0 |
{.wide .expand}

```bash
barn destroy meta
barn destroy --yes
barn destroy --yes --purge
```

## `barn purge` {#barn-purge}

```text
barn purge [flags]
```

Immediately delete the entire Linux deployment, including root disks, persistent data disks, keys, state, and the default SSH fragment. It takes no node names and reads no inventory. It has no `--yes`, `-y`, or `--force`: use `--ask` when you want to review the scope and confirm with `y/yes` (Enter cancels).

Cached images, host networking, and Mac VMs remain. An absent deployment is an idempotent success; ambiguous retained artifacts still require identity checks. The 1.2.0 `--parallel` flag controls node work during disposal.

| Option | Meaning / default | Available in |
|---|---|---|
| `--ask` | show the deletion scope and ask for y/yes before purging | 1.1.0 |
| `-p, --parallel int` | Node concurrency: omitted = max(1, logical CPUs - 2); 0 = all selected nodes; positive = limit | 1.2.0 |
{.wide .expand}

```bash
barn purge --ask
barn --json purge
```

## Implementation {#implementation}

[command_lifecycle.go](https://github.com/pgsty/barn/blob/v1.2.0/cmd/barn/command_lifecycle.go) · [main.go](https://github.com/pgsty/barn/blob/v1.2.0/cmd/barn/main.go)

The [version baseline](/docs/reference/commands/#versions) identifies the released source and the changes since 1.1.0.
