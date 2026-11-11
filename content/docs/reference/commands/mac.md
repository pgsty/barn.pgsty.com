---
title: macOS Commands
description: Manage named native macOS VMs, desktop access, restore images, and shared bases.
weight: 70
date: 2026-11-11
---

Manage named native macOS VMs, desktop access, restore images, and shared bases.

All options below are present in 1.1.0 and the reviewed development tree.

Native macOS VMs require Apple Silicon, macOS 27+, and the matching `Barn.app` native app bundle, invoked as the logged-in desktop user. Their state lives under `$BARN_HOME/mac` and is independent of the Linux inventory.

For an optional name, Barn selects the sole existing VM or `mac1`; multiple VMs without `mac1` require an explicit name. `configure`, `recreate`, and `destroy` always require names. `start` and `stop` accept multiple names or `--all`. At most two macOS VMs can run concurrently across apps on the host, including an active base installation. See [machine rules, networking, output, and files](../../mac/).

Mac resource sizes use binary units even for `GB`, unlike Linux inventory decimal `GB`; a bare Mac size is bytes. These commands ignore Linux `BARN_IMAGE/BARN_ARCH/BARN_CPU/BARN_MEM/BARN_SCALE/BARN_DISK` overrides.

## `barn mac ls` {#barn-mac-ls}

```text
barn mac ls [flags]
```

Show every machine: its state, address, SSH readiness, macOS version and resources. It reads local records and asks each running machine, and never creates, downloads or starts anything.

Running `barn mac` without a subcommand also lists machines.

Aliases: `list`, `status`, `st`.

No local options beyond `--help`; global presentation options still apply.

```bash
barn mac ls
barn --json mac ls
```

## `barn mac up` {#barn-mac-up}

```text
barn mac up [name] [flags]
```

Create the named machine (`mac1` by default), start it, and wait until SSH and passwordless sudo work. Without a prepared macOS base, `up` first downloads the restore image from Apple after confirmation and installs it once; later machines clone that base.

Creation options apply to a new machine. For an existing machine, `up` starts it and rejects options that differ from its configuration; use `configure` for supported setting changes.

`--no-wait` returns once the VM is running. First-boot provisioning may still be in progress; run `barn mac up NAME` again to wait for SSH and finish initialization.

| Option | Meaning / default | Available in |
|---|---|---|
| `--clipboard on\|off` | on/off, true/false, or yes/no; default on, active while the desktop window is focused | 1.1.0 |
| `--cpu int` | vCPUs, default 4; minimum 2, maximum host logical CPU count | 1.1.0 |
| `--disk size` | Base capacity, minimum 32 GiB; default uses the prepared base, or 100 GiB initially | 1.1.0 |
| `--ipsw string` | install macOS from this restore image instead of downloading from Apple | 1.1.0 |
| `--memory size` | Memory, default 8 GiB; a whole MiB from 4 GiB to host RAM | 1.1.0 |
| `-n, --no-wait` | return once the VM runs; first boot may still be initializing | 1.1.0 |
| `--open` | show the desktop as soon as the VM runs | 1.1.0 |
| `--share [name=]path[:ro]` | Repeatable [name=]path[:ro\|:rw]; default writable, mounted under /Volumes/My Shared Files | 1.1.0 |
| `--subnet string` | Canonical private /24, or auto; default selects the first free subnet | 1.1.0 |
| `--user string` | Guest administrator; default is the host username, or barn if that name is invalid | 1.1.0 |
| `-y, --yes` | download macOS from Apple without asking (required without a terminal) | 1.1.0 |
{.wide .expand}

```bash
barn mac up
barn mac up dev --cpu 8 --memory 16G --share ~/src --open
barn mac up build --yes --no-wait
```

## `barn mac start` {#barn-mac-start}

```text
barn mac start [name...] [flags]
```

Start existing machines and wait for SSH without creating machines or downloading images. `--recovery` boots macOS Recovery with its desktop shown.

Select names or `--all`, not both. Ordinary start requires completed first-boot initialization; use `up` to finish an uninitialized VM.

| Option | Meaning / default | Available in |
|---|---|---|
| `--all` | start every machine | 1.1.0 |
| `-n, --no-wait` | return once the VM runs, without waiting for SSH | 1.1.0 |
| `--open` | show the desktop as soon as the VM runs | 1.1.0 |
| `--recovery` | boot macOS Recovery and show its desktop | 1.1.0 |
{.wide .expand}

```bash
barn mac start mac1
barn mac start --all
barn mac start mac1 --recovery
```

## `barn mac stop` {#barn-mac-stop}

```text
barn mac stop [name...] [flags]
```

Shut machines down normally through macOS. A machine that has not stopped after two minutes is powered off, and the result says so. `--force` powers off at once, like holding a power button; unsaved work in the guest is lost.

| Option | Meaning / default | Available in |
|---|---|---|
| `--all` | stop every machine | 1.1.0 |
| `--force` | Power off immediately instead of requesting shutdown; unsaved guest work is lost | 1.1.0 |
{.wide .expand}

```bash
barn mac stop dev
barn mac stop --all
barn mac stop dev --force
```

## `barn mac restart` {#barn-mac-restart}

```text
barn mac restart [name] [flags]
```

Shut a machine down normally and start it again, applying configuration changes.

Accepts at most one name; there is no `--all`. Omitted names follow the default-machine rule above.

| Option | Meaning / default | Available in |
|---|---|---|
| `-n, --no-wait` | return once the VM runs, without waiting for SSH | 1.1.0 |
| `--open` | show the desktop as soon as the VM runs | 1.1.0 |
{.wide .expand}

```bash
barn mac restart dev
barn mac restart dev --open
```

## `barn mac configure` {#barn-mac-configure}

```text
barn mac configure <name> [flags]
```

Change settings of an existing machine without touching its disk or account. CPUs, memory, shared folders and the network change while the machine is stopped; the clipboard setting can change anytime. Saved configuration, including clipboard changes, applies at the next start; use the menu-bar control to toggle clipboard sharing in the current session.

An explicit name is required. Omitted flags retain their values. `--share` adds or replaces a named share; `--unshare` removes one.

| Option | Meaning / default | Available in |
|---|---|---|
| `--clipboard on\|off` | on/off, true/false, or yes/no; omitted retains the setting | 1.1.0 |
| `--cpu int` | vCPUs, minimum 2 and maximum host logical CPU count; omitted retains current value | 1.1.0 |
| `--memory size` | Memory, a whole MiB from 4 GiB to host RAM; omitted retains current value | 1.1.0 |
| `--share [name=]path[:ro]` | Add or replace a named share; repeatable, writable by default, optional :ro or :rw | 1.1.0 |
| `--subnet string` | move to this private /24 network, or auto for the first free one | 1.1.0 |
| `--unshare stringArray` | stop sharing the named folder (repeatable) | 1.1.0 |
{.wide .expand}

```bash
barn mac stop dev
barn mac configure dev --cpu 8 --memory 16G --share ~/src
barn mac configure dev --unshare src --clipboard off
barn mac start dev
```

## `barn mac recreate` {#barn-mac-recreate}

```text
barn mac recreate <name> [flags]
```

Erase the machine's disk and start a fresh macOS with the same name, account, resources, shared folders and address. `--update` uses the newest prepared base (see `barn mac image update`). Its files, apps and settings are lost.

A terminal asks you to type `recreate`; scripts require `--yes` or `--force`, with no `-y` shorthand.

| Option | Meaning / default | Available in |
|---|---|---|
| `--force` | skip the confirmation (required without a terminal) | 1.1.0 |
| `-n, --no-wait` | return once the VM runs, without waiting for SSH | 1.1.0 |
| `--update` | use the newest prepared macOS base | 1.1.0 |
| `--yes` | Same as `--force`; no -y shorthand | 1.1.0 |
{.wide .expand}

```bash
barn mac recreate dev
barn mac image update --yes
barn mac recreate dev --update --yes
```

## `barn mac destroy` {#barn-mac-destroy}

```text
barn mac destroy <name...> [flags]
```

Power machines off and delete them: disk, keys, password and settings. The shared macOS base and other machines are kept; `barn mac image prune` removes unused bases.

Explicit names are required. A terminal asks you to type `destroy`; scripts require `--yes` or `--force`, with no `-y`. Shared host folders are retained.

| Option | Meaning / default | Available in |
|---|---|---|
| `--force` | skip the confirmation (required without a terminal) | 1.1.0 |
| `--yes` | Same as `--force`; no -y shorthand | 1.1.0 |
{.wide .expand}

```bash
barn mac destroy dev
barn mac destroy mac1 mac2 --yes
```

## `barn mac open` {#barn-mac-open}

```text
barn mac open [name] [flags]
```

Show the machine's desktop window, starting the machine first when it is stopped. Closing the window keeps the machine running in the background; the clipboard is shared while the window is focused.

An uninitialized running VM can be viewed here; for a stopped uninitialized VM use `mac up NAME --open`.

No local options beyond `--help`; global presentation options still apply.

```bash
barn mac open
barn mac open dev
```

## `barn mac ssh` {#barn-mac-ssh}

```text
barn mac ssh [flags] [name] [-- command...]
```

Connect with the machine's own key and pinned host key. Everything before -- must be empty or one known machine name, apart from Barn flags. A remote command requires --, and its first argument must not be empty. For exec, pass the program and its arguments separately to preserve argument boundaries, including later empty values. Use sh -c explicitly for shell expressions. A single command string remains supported as shell shorthand for compatibility. exec requires a command. ssh passes the command line to the remote shell like plain ssh. Without a command, ssh opens an interactive session.

No local options beyond `--help`; global presentation options still apply.

```bash
barn mac ssh dev
barn mac ssh dev -- 'sw_vers; id'
```

## `barn mac exec` {#barn-mac-exec}

```text
barn mac exec [flags] [name] -- command...
```

Connect with the machine's own key and pinned host key. Everything before -- must be empty or one known machine name, apart from Barn flags. A remote command requires --, and its first argument must not be empty. For exec, pass the program and its arguments separately to preserve argument boundaries, including later empty values. Use sh -c explicitly for shell expressions. A single command string remains supported as shell shorthand for compatibility. exec requires a command. ssh passes the command line to the remote shell like plain ssh. Without a command, ssh opens an interactive session.

No local options beyond `--help`; global presentation options still apply.

```bash
barn mac exec dev -- sw_vers
barn mac exec dev -- printf '<%s>\n' 'a b' ''
barn --json mac exec dev -- sh -c 'echo out; exit 3'
```

## `barn mac password` {#barn-mac-password}

```text
barn mac password [name] [flags]
```

Show the password of the machine's login account, needed for the lock screen and administrator prompts in its desktop. It is stored next to the machine's SSH key with the same protection. `--copy` puts it on the clipboard instead of printing it.

| Option | Meaning / default | Available in |
|---|---|---|
| `-c, --copy` | copy to the clipboard instead of printing | 1.1.0 |
{.wide .expand}

```bash
barn mac password dev
barn mac password dev --copy
```

## `barn mac ssh-config` {#barn-mac-ssh-config}

```text
barn mac ssh-config [flags]
```

Print the OpenSSH fragment that lets ssh, scp, rsync and editors reach each machine by name with its own key and pinned host key. The first machine to become ready installs it as one Include in ~/.ssh/config, and lifecycle commands keep it current. --remove deletes only what Barn installed and keeps it out until --install. A name that ~/.ssh/config already uses for another host is published by address only.

`--install` and `--remove` are mutually exclusive. This command takes no machine selectors.

| Option | Meaning / default | Available in |
|---|---|---|
| `-i, --install` | install the entries as one Include in ~/.ssh/config | 1.1.0 |
| `--remove` | remove the entries Barn installed | 1.1.0 |
{.wide .expand}

```bash
barn mac ssh-config
barn mac ssh-config --install
barn mac ssh-config --remove
```

## `barn mac logs` {#barn-mac-logs}

```text
barn mac logs [name] [flags]
```

Show the last lines of the machine's runtime log: startup, network, shutdown and Apple Virtualization errors.

`--lines/-n` must be positive and defaults to 100. There is no follow flag; `-n` means lines, not no-wait.

| Option | Meaning / default | Available in |
|---|---|---|
| `-n, --lines int` | number of recent lines (default 100) | 1.1.0 |
{.wide .expand}

```bash
barn mac logs dev
barn mac logs dev --lines 200
```

## `barn mac setup` {#barn-mac-setup}

```text
barn mac setup [flags]
```

Download macOS from Apple after you confirm, or read --ipsw, and install it once into the unbooted base that every machine is cloned from. up does this automatically; setup lets you do it ahead of time.

| Option | Meaning / default | Available in |
|---|---|---|
| `--disk size` | Base capacity, minimum 32 GiB and default 100 GiB | 1.1.0 |
| `--ipsw string` | install macOS from this restore image instead of downloading from Apple | 1.1.0 |
| `-y, --yes` | download macOS from Apple without asking (required without a terminal) | 1.1.0 |
{.wide .expand}

```bash
barn mac setup --yes
barn mac setup --ipsw ~/Downloads/restore.ipsw --disk 200G
```

## `barn mac image ls` {#barn-mac-image-ls}

```text
barn mac image ls [flags]
```

List restore images and bases with their state, disk usage and the machines that use them.

This local-state query does not invoke the native runner.

Aliases: `list`.

No local options beyond `--help`; global presentation options still apply.

```bash
barn mac image ls
barn --json mac image ls
```

## `barn mac image update` {#barn-mac-image-update}

```text
barn mac image update [flags]
```

Ask Apple for the newest macOS 27 restore image, download it after you confirm, and install it as the default base for new machines. Existing machines keep their base until barn mac recreate --update.

| Option | Meaning / default | Available in |
|---|---|---|
| `--ipsw string` | use this restore image instead of downloading from Apple | 1.1.0 |
| `-y, --yes` | download without asking (required without a terminal) | 1.1.0 |
{.wide .expand}

```bash
barn mac image update --yes
barn mac image ls
```

## `barn mac image prune` {#barn-mac-image-prune}

```text
barn mac image prune [flags]
```

List unused bases except the current default base. `--installers` also includes downloaded restore images and partial downloads. Deletion requires `--yes`.

| Option | Meaning / default | Available in |
|---|---|---|
| `--installers` | include downloaded restore images and partial downloads | 1.1.0 |
| `-y, --yes` | Delete the listed unused images; otherwise only list candidates | 1.1.0 |
{.wide .expand}

```bash
barn mac image prune
barn mac image prune --installers --yes
```

## `barn mac doctor` {#barn-mac-doctor}

```text
barn mac doctor [flags]
```

Check macOS and Apple Silicon support, the Mac component's signature, free disk space, the prepared base, and every machine: its files, keys, shared folders, network and SSH. It changes nothing and starts nothing.

No local options beyond `--help`; global presentation options still apply.

```bash
barn mac doctor
barn --json mac doctor
```

## Implementation {#implementation}

[command_mac.go](https://github.com/pgsty/barn/blob/v1.1.0/cmd/barn/command_mac.go)

The [version baseline](/docs/reference/commands/#versions) records the additional local commits and uncommitted extension checked on 2026-11-11.
