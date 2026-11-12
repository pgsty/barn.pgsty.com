---
title: Preparation and Utilities
description: Initialize inventories, prepare the host, validate configuration, and inspect the CLI.
weight: 10
date: 2026-11-11
---

Initialize inventories, prepare the host, validate configuration, and inspect the CLI.

This reference covers **Barn 1.2.0**. Option tables distinguish options also available in **1.1.0** from additions in **1.2.0**; see the [version baseline](/docs/reference/commands/#versions). All commands inherit the [global options](/docs/reference/commands/#global-options).

## `barn setup` {#barn-setup}

```text
barn setup [meta|dual|trio|full] [flags]
```

Prepare host packages, the fixed-IP network, images, and the selected inventory. It does not create the Linux VMs: run `barn up` afterward. With no template or `-f`, reuse the discovered inventory or generate `meta`. The templates `meta`, `dual`, `trio`, and `full` contain 1, 2, 3, and 4 nodes. `-c` and specification flags customize a generated template; explicit specification flags cannot be used to rewrite an existing inventory. In 1.2.0, specification environment variables are also ignored when setup reuses an inventory.

`--dry-run` previews the transaction. Applying it requires terminal confirmation or `--yes`; operating-system privilege prompts can still occur. On a fresh unedited default template, setup may choose a free private `/24` and save `barn.yml.before-network-change` if the default subnet conflicts. Explicit inventories retain their subnet. On Linux, foreign-architecture QEMU emulators and firmware need separate installation.

Aliases: `s`.

| Option | Meaning / default | Available in |
|---|---|---|
| `-A, --arch string` | override deployment vm_arch: native, amd64, or arm64; environment overrides require 1.2.0 | 1.1.0 |
| `-c, --cidr string` | generated template network as a canonical RFC1918 IPv4 /24 | 1.1.0 |
| `-C, --cpu string` | Base vCPUs before scale, integer 1–256; effective CPU count is also limited to 256; overrides BARN_CPU | 1.2.0 |
| `-D, --disk string` | Absolute root capacity, at least the base virtual size; bare integer means GiB; overrides BARN_DISK | 1.2.0 |
| `-d, --dry-run` | show the resolved setup plan without changing anything | 1.1.0 |
| `-f, --file string` | Inventory to prepare; mutually exclusive with a template argument | 1.1.0 |
| `-I, --image string` | override vm_image/vm_version for selected nodes; environment overrides require 1.2.0 | 1.1.0 |
| `-M, --mem string` | Base memory before scale, minimum 512 MiB; bare integer means MiB; overrides BARN_MEM | 1.2.0 |
| `--mirror` | use the China official repository at repo.pigsty.cc; overridden by `--repo` | 1.1.0 |
| `-m, --mode string` | macOS fixed-IP network backend: host or shared (default "host") | 1.1.0 |
| `-r, --repo string` | image repository URL or local directory, also used for socket_vmnet; overrides `--mirror` and $BARN_REPO | 1.1.0 |
| `-S, --scale string` | Integer 1–256 multiplying base CPU and memory only; disk does not scale; overrides BARN_SCALE | 1.2.0 |
| `-y, --yes` | accept the one-time setup plan (required without a terminal) | 1.1.0 |
{.wide .expand}

```bash
barn setup --dry-run
barn setup full -I el9 --yes
barn setup -f pigsty.yml --yes
barn up
```

## `barn init` {#barn-init}

```text
barn init [meta|dual|trio|full] [flags]
```

Generate a Pigsty-compatible YAML inventory. The default is the one-node `meta` template in `./barn.yml`; `dual`, `trio`, and `full` add nodes at `.11`, `.12`, and `.13`. The control node is `.10`. Existing files require `--force`; `-o -` prints the inventory. This command does not download images or prepare the host.

Barn 1.2.0 defaults to 1 vCPU and 2 GiB per node, with a 64 GiB root and a separate 128 GiB `/data` disk. Generated templates persist all six specification fields, including `vm_scale`. Version 1.1.0 used 2 vCPUs and 4 GiB by default. See [specification defaults](../../configuration/#specification-overrides).

| Option | Meaning / default | Available in |
|---|---|---|
| `-A, --arch string` | override deployment vm_arch: native, amd64, or arm64; environment overrides require 1.2.0 | 1.1.0 |
| `-c, --cidr string` | rebase the generated template to a canonical RFC1918 IPv4 /24 | 1.1.0 |
| `-C, --cpu string` | Base vCPUs before scale, integer 1–256; effective CPU count is also limited to 256; overrides BARN_CPU | 1.2.0 |
| `-D, --disk string` | Absolute root capacity, at least the base virtual size; bare integer means GiB; overrides BARN_DISK | 1.2.0 |
| `--force` | Overwrite the destination inventory; default preserves existing files | 1.1.0 |
| `-I, --image string` | override vm_image/vm_version for selected nodes; environment overrides require 1.2.0 | 1.1.0 |
| `-M, --mem string` | Base memory before scale, minimum 512 MiB; bare integer means MiB; overrides BARN_MEM | 1.2.0 |
| `-o, --output string` | write to this path instead of ./barn.yml; '-' writes to stdout | 1.1.0 |
| `-S, --scale string` | Integer 1–256 multiplying base CPU and memory only; disk does not scale; overrides BARN_SCALE | 1.2.0 |
{.wide .expand}

```bash
barn init
barn init full -I el9 -A amd64 -o lab.yml
barn init dual -c 10.20.30.0/24 -o -
```

## `barn validate` {#barn-validate}

```text
barn validate [flags]
```

Read one inventory, validate the fields Barn consumes, and report the resolved nodes. It accepts no node selectors. Discovery checks `barn.yml`, `barn.yaml`, `pigsty.yml`, then `pigsty.yaml` in the current directory; no inventory means an error even if applied state exists. Overrides affect this validation only. Use `--json` to inspect the resolved specification, and `plan` to compare it with an existing deployment.

Aliases: `v`.

| Option | Meaning / default | Available in |
|---|---|---|
| `-A, --arch string` | override deployment vm_arch: native, amd64, or arm64; environment overrides require 1.2.0 | 1.1.0 |
| `-C, --cpu string` | Base vCPUs before scale, integer 1–256; effective CPU count is also limited to 256; overrides BARN_CPU | 1.2.0 |
| `-D, --disk string` | Absolute root capacity, at least the base virtual size; bare integer means GiB; overrides BARN_DISK | 1.2.0 |
| `-f, --file string` | Inventory to validate; otherwise use local discovery, with no applied-state fallback | 1.1.0 |
| `-I, --image string` | override vm_image/vm_version for selected nodes; environment overrides require 1.2.0 | 1.1.0 |
| `-M, --mem string` | Base memory before scale, minimum 512 MiB; bare integer means MiB; overrides BARN_MEM | 1.2.0 |
| `-r, --repo string` | image repository whose catalog checks the images; overrides $BARN_REPO | 1.1.0 |
| `-S, --scale string` | Integer 1–256 multiplying base CPU and memory only; disk does not scale; overrides BARN_SCALE | 1.2.0 |
{.wide .expand}

```bash
barn validate -f lab.yml
barn --json validate -f lab.yml -I u24 -A arm64
```

## `barn doctor` {#barn-doctor}

```text
barn doctor [flags]
```

Probe QEMU, native acceleration, firmware, OpenSSH, a short accelerated boot test, and host networking. This is a host diagnostic and takes no inventory or node arguments. Missing compute capabilities fail the command; missing network setup is reported as informational. Inspect `barn network status` for the detailed network plan and `barn mac doctor` for native macOS VMs.

Aliases: `dt`.

No local options beyond `--help`; global presentation options still apply.

```bash
barn doctor
barn --json doctor
barn doctor --verbose
```

## `barn version` {#barn-version}

```text
barn version [flags]
```

Print version, source commit, build time, host OS, and architecture. Development builds normally report `dev`; release identity comes from the build stamp. Use this report when matching documentation or filing an issue. The root shortcut `barn --version` is also available.

Aliases: `ver`.

No local options beyond `--help`; global presentation options still apply.

```bash
barn version
barn --json version
```

## `barn completion` {#barn-completion}

```text
barn completion [bash|zsh|fish|powershell] [flags]
```

Require one shell name: `bash`, `zsh`, `fish`, or `powershell`. Print its completion script to stdout; the command does not install the script. Completion includes scoped flags, templates, image aliases, and best-effort node names. Reload it after upgrading Barn. Use text output when sourcing shell code.

No local options beyond `--help`; global presentation options still apply.

```bash
source <(barn completion bash)
barn completion zsh > "${fpath[1]}/_barn"
barn completion fish > ~/.config/fish/completions/barn.fish
barn completion powershell
```

## Implementation {#implementation}

[command_setup.go](https://github.com/pgsty/barn/blob/v1.2.0/cmd/barn/command_setup.go) · [command_misc.go](https://github.com/pgsty/barn/blob/v1.2.0/cmd/barn/command_misc.go) · [command_root.go](https://github.com/pgsty/barn/blob/v1.2.0/cmd/barn/command_root.go)

The [version baseline](/docs/reference/commands/#versions) identifies the released source and the changes since 1.1.0.
