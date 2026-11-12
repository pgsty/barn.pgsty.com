---
title: Command Reference
linkTitle: Commands
description: Every Barn command with syntax, all local options, defaults, examples, and version availability.
weight: 5
date: 2026-11-11
lastmod: 2026-11-12
icon: fa-solid fa-terminal
no_list: true
---

Find a command below for its arguments, complete local option table, examples, and effects. This reference follows the command-index and command-family organization of [PIG](https://pig.pgsty.com/cmd/). Barn's [CLI contracts](../cli/) describe structured output and exit codes; [Configuration](../configuration/) defines inventory fields.

## Version baseline {#versions}

This reference covers **Barn 1.2.0**, released on **2026-11-12** from [`90f6158`](https://github.com/pgsty/barn/tree/v1.2.0). Its 57 operation commands and 174 local option entries were checked against the CLI help output in both languages.

| Label | Availability | Behavior |
|---|---|---|
| **1.1.0** | Options available in both 1.1.0 and 1.2.0 | 1.1.0 used 2 vCPUs / 4 GiB by default and accepted CPU/memory resize through the inventory |
| **1.2.0** | Added in 1.2.0 | Resource flags and environment overrides, `vm_scale`, root-disk growth, lifecycle `--parallel`, `vm_hosts`, and `hosts install -f`; defaults are now 1 vCPU / 2 GiB |
{.wide .expand}

To preserve the previous defaults when upgrading, set `vm_cpu: 2` and `vm_mem: 4GiB` explicitly and inspect `barn plan`. Existing applied VMs keep their resources until a resource-changing operation is requested. Use `barn version` and `barn COMMAND --help` to check an installed build. See the [release notes](/blog/release/1.2.0/) and [release validation](/blog/design/release-1-2-0-readiness/).

## Command index {#command-index}

| Task | Commands and detailed reference |
|---|---|
| Prepare | [setup](setup/#barn-setup), [init](setup/#barn-init), [validate](setup/#barn-validate), [doctor](setup/#barn-doctor) |
| Plan and create | [plan](lifecycle/#barn-plan), [up](lifecycle/#barn-up) |
| Start and stop | [start](lifecycle/#barn-start), [stop](lifecycle/#barn-stop), [restart](lifecycle/#barn-restart), [reload](lifecycle/#barn-reload) |
| Change and inspect | [resize](lifecycle/#barn-resize), [recreate](lifecycle/#barn-recreate), [status](lifecycle/#barn-status) |
| Delete | [destroy](lifecycle/#barn-destroy), [purge](lifecycle/#barn-purge) |
| Access Linux guests | [ssh](access/#barn-ssh), [exec](access/#barn-exec), [logs](access/#barn-logs), [provision](access/#barn-provision), [ssh-config](access/#barn-ssh-config) |
| Publish host names | [hosts install](access/#barn-hosts-install), [hosts uninstall](access/#barn-hosts-uninstall) |
| Refresh catalog | [update](image/#barn-update), [image sync](image/#barn-image-sync), [image reset](image/#barn-image-reset) |
| Manage Linux images | [image list](image/#barn-image-list), [info](image/#barn-image-info), [pull](image/#barn-image-pull), [import](image/#barn-image-import), [prune](image/#barn-image-prune) |
| Maintain a repository | [repo scan](repo/#barn-repo-scan), [build](repo/#barn-repo-build), [verify](repo/#barn-repo-verify) |
| Host network | [network status](network/#barn-network-status), [install](network/#barn-network-install), [uninstall](network/#barn-network-uninstall) |
| Native macOS VMs | [mac ls](mac/#barn-mac-ls), [up](mac/#barn-mac-up), [start](mac/#barn-mac-start), [stop](mac/#barn-mac-stop), [restart](mac/#barn-mac-restart), [configure](mac/#barn-mac-configure), [recreate](mac/#barn-mac-recreate), [destroy](mac/#barn-mac-destroy) |
| Mac access | [mac open](mac/#barn-mac-open), [ssh](mac/#barn-mac-ssh), [exec](mac/#barn-mac-exec), [password](mac/#barn-mac-password), [ssh-config](mac/#barn-mac-ssh-config), [logs](mac/#barn-mac-logs) |
| Mac preparation | [mac setup](mac/#barn-mac-setup), [doctor](mac/#barn-mac-doctor), [image ls](mac/#barn-mac-image-ls), [image update](mac/#barn-mac-image-update), [image prune](mac/#barn-mac-image-prune) |
| CLI utilities | [version](setup/#barn-version), [completion](setup/#barn-completion), [help](#barn-help) |
{.wide .expand}

## Global options {#global-options}

```text
barn [--json|--yaml] [-v|--verbose] COMMAND [arguments] [local options]
```

| Option | Meaning |
|---|---|
| `-h`, `--help` | Human-readable help for the selected command; exits `0` |
| `--json` | Structured JSON on stdout; progress and diagnostics stay on stderr |
| `--yaml` | Structured YAML on stdout; mutually exclusive with `--json` |
| `-v`, `--verbose` | Bounded diagnostics on stderr |
| `--version` | Root-command shortcut to display build identity; use `barn version --json` for a structured report |

Global output options can appear before or after a subcommand, but must precede the remote-command `--` separator used by `ssh` and `exec`. `-f`, `-I`, `-A`, `-p`, and `--yes` are local options: consult the selected command's table. `-f` means follow for `logs`; `-n` means line count for `mac logs`. Long boolean options accept `=true` or `=false`.

`BARN_OUTPUT` and `BARN_VERBOSE` set presentation defaults. `BARN_HOME` selects private state (default `~/.barn`); use an absolute path when changing directories. Linux and Mac machines share that data root but have independent lifecycles. See [environment variables](../cli/#logs-and-environment) and [exit codes](../cli/#exit-codes).

## barn and help {#barn-help}

```bash
barn
barn --help
barn help resize
barn image pull --help
barn --json
```

With no arguments, text mode prints complete help and exits `0`; JSON/YAML mode returns suggested `actions[]`. Explicit help always prints human-readable text. Groups `image`, `repo`, `network`, `hosts`, and `mac image` require a subcommand and exit `2` without one. The `mac` group is the exception: it defaults to `mac ls`. It is hidden from root help on Linux and Intel Macs, while explicit Mac help remains available.

Short aliases are scoped to their parent. `barn im ls` is `barn image list`; `barn mac st` is `barn mac ls`. The per-command pages list each alias. There is no `rm` alias for `purge`.
