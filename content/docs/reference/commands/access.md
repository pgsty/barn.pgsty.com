---
title: Guest Access and Hosts
description: Connect to Linux guests, run scripts, read logs, and publish SSH or hosts entries.
weight: 30
date: 2026-11-11
---

Connect to Linux guests, run scripts, read logs, and publish SSH or hosts entries.

Availability labels distinguish **1.1.0**, **local main**, and **working tree**; see the [version baseline](/docs/reference/commands/#versions). All commands inherit the [global options](/docs/reference/commands/#global-options).

## `barn ssh` {#barn-ssh}

```text
barn ssh [flags] [node] [-- command...]
```

Open an interactive SSH session on the selected prepared node, defaulting to the prepared control node (or first prepared node). Remote commands require `--`; arguments after it are joined for the remote shell like ordinary `ssh`. Put Barn options before the separator. Node selectors are resolved node names, not IP addresses, aliases, or groups.

A remote command returns its exit status unchanged. Structured interactive SSH sends session output to stderr and the final report to stdout. See [SSH argument rules](../../cli/#ssh-passthrough-and-completion).

No local options beyond `--help`; global presentation options still apply.

```bash
barn ssh
barn ssh meta
barn ssh meta -- 'df -h /data; id'
```

## `barn exec` {#barn-exec}

```text
barn exec [flags] [node] -- command...
```

Run one remote command on the selected prepared node, with the same default-node selection as `ssh`. `--` and a non-empty first command argument are required. Separate arguments preserve spaces, quotes, and later empty values. Use `sh -c` for pipelines, redirection, or variable expansion; a single command string is also accepted as compatibility shell shorthand.

Text mode forwards the child output and exit status. Structured output includes `success`, `exit_code`, `stdout`, and `stderr`. A nonzero remote exit is passed through, so inspect that result before interpreting the number as a Barn error class.

Aliases: `ex`.

No local options beyond `--help`; global presentation options still apply.

```bash
barn exec meta -- hostname
barn exec meta -- printf '<%s>\n' 'a b' ''
barn --json exec meta -- sh -c 'echo out; exit 17'
```

## `barn logs` {#barn-logs}

```text
barn logs [node] [flags]
```

Read the selected node’s serial console or QEMU diagnostic log, defaulting to the prepared control/first node. `--source events` selects the deployment-wide bounded event log and takes no node argument; it can be read before deployment state exists. Following logs emits a stream rather than one final document. `-f` means follow here, not inventory. QEMU argv is hidden unless verbose output is enabled.

Aliases: `l`.

| Option | Meaning / default | Available in |
|---|---|---|
| `-f, --follow` | continue streaming appended log data | 1.1.0 |
| `-s, --source string` | log source: serial, qemu, or events (default "serial") | 1.1.0 |
{.wide .expand}

```bash
barn logs meta
barn logs meta --source qemu
barn logs --source events --follow
barn --json logs meta --follow
```

## `barn provision` {#barn-provision}

```text
barn provision [node...] [flags]
```

Stream a local Bash script over the verified deployment SSH connection to selected running nodes, or all nodes if no names are supplied. The script is not left behind as a guest file; its digest is recorded for auditing. It does not create or start VMs.

`--script` is required. The default concurrency is 1 and the timeout is one hour for the operation. Unlike development lifecycle concurrency, `--parallel 0` is invalid. `--sudo` uses noninteractive guest `sudo -n`; ensure the guest user has the required permission. Review per-node output and failures in structured mode.

| Option | Meaning / default | Available in |
|---|---|---|
| `-p, --parallel int` | Positive concurrency limit; default 1; zero is invalid | 1.1.0 |
| `-s, --script string` | local Bash script to stream to each selected guest | 1.1.0 |
| `--sudo` | run the guest script through sudo -n | 1.1.0 |
| `-t, --timeout duration` | hard deadline for the operation (default 1h0m0s) | 1.1.0 |
{.wide .expand}

```bash
barn provision --script ./check.sh meta
barn provision --script ./bootstrap.sh --sudo --parallel 2 --timeout 30m
```

## `barn ssh-config` {#barn-ssh-config}

```text
barn ssh-config [node...] [flags]
```

Print the Linux deployment’s OpenSSH fragment. `--install` writes a fragment and one `Include` in `~/.ssh/config`; printing and installation accept node selectors. `--remove` removes only the named Barn fragment, needs no deployment state, and takes no nodes. Install and remove are mutually exclusive.

The default prefix is `barn` and its fragment is `~/.ssh/barn_config`. Normal lifecycle commands maintain the default fragment automatically. If the user’s SSH configuration cannot be safely edited, Barn reports the manual `Include` instruction; direct `barn ssh` remains usable.

Aliases: `sc`.

| Option | Meaning / default | Available in |
|---|---|---|
| `-i, --install` | install the deployment fragment and one Include in ~/.ssh/config | 1.1.0 |
| `--name string` | SSH Host and fragment prefix (default "barn") | 1.1.0 |
| `--remove` | remove the Include and fragment Barn installed | 1.1.0 |
{.wide .expand}

```bash
barn ssh-config
barn ssh-config --install meta
barn ssh-config --install --name lab
barn ssh-config --remove --name lab
```

## `barn hosts install` {#barn-hosts-install}

```text
barn hosts install [flags]
```

Publish applied node names and aliases in the Barn-owned block of the host’s `/etc/hosts`, using the digest-matched privileged helper. On a terminal it shows the change and asks before applying; in noninteractive or structured mode it only previews unless `--yes` is passed. An unchanged block requires no privilege. This file is not automatically published by `up`.

The uncommitted working-tree extension adds `-f pigsty.yml`, publishing inventory nodes plus `all.vars.vm_hosts` before VM creation. It replaces the whole Barn block, so a later call without `-f` drops inventory-only service names. This option is absent from both v1.1.0 and local commit `6ab0cd5`; see [local service names](../../configuration/#local-hosts).

Aliases: `i`.

| Option | Meaning / default | Available in |
|---|---|---|
| `-f, --file string` | Inventory nodes, aliases and vm_hosts; usable before VM creation (working tree only) | Working tree |
| `-y, --yes` | apply the displayed privileged plan without confirmation (sudo may still ask for a password) | 1.1.0 |
{.wide .expand}

```bash
barn hosts install --json
barn hosts install --yes
```

## `barn hosts uninstall` {#barn-hosts-uninstall}

```text
barn hosts uninstall [flags]
```

Remove only the Barn-owned `/etc/hosts` block while retaining other entries. It needs no inventory or deployment state. Terminal mode displays a plan and asks; noninteractive/structured mode previews unless `--yes` is supplied. Removing the block does not delete VMs or change guest DNS configuration.

Aliases: `u`.

| Option | Meaning / default | Available in |
|---|---|---|
| `-y, --yes` | apply the displayed privileged plan without confirmation (sudo may still ask for a password) | 1.1.0 |
{.wide .expand}

```bash
barn hosts uninstall --json
barn hosts uninstall --yes
```

## Implementation {#implementation}

[command_root.go](https://github.com/pgsty/barn/blob/v1.1.0/cmd/barn/command_root.go) · [command_access.go](https://github.com/pgsty/barn/blob/v1.1.0/cmd/barn/command_access.go) · [main.go](https://github.com/pgsty/barn/blob/v1.1.0/cmd/barn/main.go)

The [version baseline](/docs/reference/commands/#versions) records the additional local commits and uncommitted extension checked on 2026-11-11.
