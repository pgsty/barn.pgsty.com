---
title: Mac Commands
description: barn mac commands and flags, machine rules, JSON results, failure reasons, networks, and files.
weight: 25
icon: fa-brands fa-apple
---

> [!NOTE]
> **Unreleased**: The changes below to share names and counts, linked sources, runner paths, and log line limits require a build containing source commit `27f17bb`; they are not included in Barn 0.9.2. See [Unreleased Changes](/docs/about/unreleased/).

```text
barn [--json|--yaml] [-v|--verbose] mac <command> [flags] [name...]
```

Running macOS guests requires an Apple Silicon Mac on macOS 27 or later, invoked as the logged-in desktop user. Commands that talk to the native runner reject `root` with `mac_root` and unsupported hosts with `mac_host_unsupported`. Top-level `--help` hides `mac` on Linux and Intel Macs, while local-state queries such as `barn mac image ls` work without invoking the runner. Running `barn mac` with no subcommand executes `barn mac ls`.

This reference covers the **Barn 0.9.2** command interface and `Barn.app` (runner protocol `2`), plus the source changes identified above. The Apple Silicon release and Homebrew installation include the app; see [macOS Guests](../../start/macos/#install).

## Commands

| Command | Purpose |
|---|---|
| `ls` | List every VM with state, IP, SSH status, macOS build, resources, and shares (aliases: `list`, `status`, `st`) |
| `up [name]` | Create the VM if needed, start it, and wait for SSH and passwordless sudo |
| `start [name...]` | Start existing VMs |
| `stop [name...]` | Request a clean macOS shutdown, powering off after two minutes if still running |
| `restart [name]` | Stop and start a VM, applying any pending hardware, share, or subnet changes |
| `open [name]` | Open the desktop window, starting the VM first if needed |
| `ssh [name] [-- command...]` | Open an interactive shell, or pass a command string after `--` to the guest shell |
| `exec [name] -- command...` | Execute a remote program while preserving argument boundaries |
| `configure name` | Update a stopped VM's CPUs, memory, shares, subnet, or clipboard setting |
| `recreate name` | Replace a VM with a fresh macOS clone while keeping its hardware and network settings |
| `destroy name...` | Delete one or more VMs |
| `password [name]` | Print or copy the guest login password |
| `ssh-config` | Print, install, or remove `~/.ssh/barn-mac_config` entries |
| `logs [name]` | Read recent lines from the VM's `runner.log` |
| `setup` | Download and prepare the default macOS base image without creating a VM |
| `image ls` | List cached `.ipsw` restore files and prepared base images alongside the VMs using them (alias: `list`) |
| `image update` | Download and prepare Apple's latest macOS 27 build as the default base image |
| `image prune` | List unused images, or delete them when `--yes` is passed |
| `doctor` | Check host eligibility, `Barn.app`, base images, and every VM slot |
{.wide}

### SSH and exec {#ssh-and-exec}

> [!TIP]
> Since **0.9.2**, remote commands require `--`, for example `barn mac exec dev -- sw_vers`. Interactive `barn mac ssh dev` needs no separator.

Before `--`, pass Barn flags and at most one existing VM name (omitting the name selects the sole VM or `mac1`). `ssh` without a command opens an interactive shell; `exec` requires a non-empty command after `--`. Unknown VM names or invalid arguments fail with exit code `2` (`usage`) before attempting a connection and point to `barn mac ls`.

`ssh` joins arguments after `--` into a command string for the guest shell, whereas `exec` passes the program and arguments separately (preserving spaces, quotes, and subsequent empty arguments). Use `sh -c '...'` for pipelines, redirection, or compound commands. Put Barn flags (`--json`, `-v`, `--help`) before `--`; everything after `--` belongs to the guest command.

```bash
barn mac ssh dev
barn mac ssh dev -- 'sw_vers; id'
barn mac exec dev -- sw_vers
barn mac exec dev -- printf '<%s>\n' 'a b' ''
barn mac exec dev -- sh -c 'sw_vers; id'
barn --json mac exec dev -- sh -c 'echo out; exit 3'
```

### Flags by command

| Command | Flags |
|---|---|
| `up` | `--cpu`, `--memory`, `--disk`, `--user`, `--share`, `--clipboard`, `--subnet`, `--ipsw`, `-y`/`--yes`, `-n`/`--no-wait`, `--open` |
| `start` | `--all`, `-n`/`--no-wait`, `--open`, `--recovery` |
| `stop` | `--all`, `--force` |
| `restart` | `-n`/`--no-wait`, `--open` |
| `configure` | `--cpu`, `--memory`, `--share`, `--unshare`, `--clipboard`, `--subnet` |
| `recreate` | `--update`, `--force`, `-n`/`--no-wait` |
| `destroy` | `--force` |
| `password` | `-c`/`--copy` |
| `ssh-config` | `-i`/`--install`, `--remove` |
| `logs` | `-n`/`--lines` positive integer (default `100`); honors the requested count without the old 1 MiB cutoff |
| `setup` | `--ipsw`, `--disk`, `-y`/`--yes` |
| `image update` | `--ipsw`, `-y`/`--yes` |
| `image prune` | `--installers`, `-y`/`--yes` |
{.wide}

When a VM name is optional, omitting it selects the only existing VM or `mac1`; if multiple VMs exist and none is named `mac1`, Barn asks you to specify a name. `start` and `stop` accept multiple names or `--all`. `destroy` and `recreate` print what will be deleted and prompt for the command name on a terminal (pass `--force` in non-interactive scripts).

`--no-wait` returns as soon as the VM process is running; for a newly created VM, run `barn mac up NAME` without `--no-wait` to finish SSH key installation and sudo setup. Ordinary `start` requires a VM that has completed its first boot—if an uninitialized VM is already running, use `barn mac open NAME` to view its first boot, or `barn mac up NAME --open` if it is stopped. Passing `--recovery` boots directly into the macOS Recovery desktop without waiting for normal SSH readiness.

### Flag values

| Flag | Value |
|---|---|
| `--cpu` | vCPU count: at least `2` and at most the Mac's logical CPU count (default `4`) |
| `--memory` | Memory size in binary units (`16G`, `16GiB`, `16GB`) or exact bytes; must be a whole MiB between `4 GiB` and host RAM (default `8 GiB`) |
| `--disk` | Base image disk capacity, minimum `32 GiB` (defaults to the prepared base image's capacity, or `100 GiB` for the first base image; requesting another size installs a matching base image if needed) |
| `--user` | Guest administrator username (defaults to your host macOS username, or `barn` if the host name is not a valid account identifier) |
| `--share` | `[name=]path[:ro\|:rw]`, repeatable; `name` defaults to the last path component and `~/` expands to your home directory |
| `--clipboard` | `on` or `off` (also accepts `true`/`false`, `yes`/`no`; default `on`) |
| `--subnet` | Canonical private `/24` such as `10.10.30.0/24`, or `auto` for the first free subnet |
{.wide}

If you run `up` on an existing VM with creation flags that differ from its recorded settings, `up` exits with `mac_configuration_conflict` and prints the exact `configure` or `recreate` command in `next:`:

- Use `barn mac configure` while the VM is stopped to change `--cpu`, `--memory`, `--share`/`--unshare`, `--subnet`, or `--clipboard` (clipboard changes can also be saved while the VM is running and take effect on the next start; use the menu bar item to toggle clipboard sync for the active session). **Unreleased:** Share names may contain spaces and Unicode, must be valid UTF-8 of 1–255 bytes, and cannot be `.`, `..`, or contain `/` or ASCII control characters; reusing a share name in `configure --share` updates its path and mode, while `--unshare` removes that share.
- The guest administrator account (`--user`) and disk capacity (`--disk`) are fixed for the lifetime of a VM and preserved across `recreate`. Create a new VM if you need a different account or disk size.
- To upgrade a VM to a newer macOS build, run `barn mac image update` followed by `barn mac recreate NAME --update`. Because `recreate --update` preserves the VM's disk capacity, if the new macOS build does not yet have a base image at a custom disk size (for example, `200G`), prepare it first with `barn mac setup --disk 200G`.

## Machines

- **Names**: 1–32 characters starting with a lowercase letter and containing lowercase letters, digits, or internal hyphens (for example `mac1`, `dev`, `build-2`).
- **Two-VM host limit**: Apple's Virtualization framework allows at most two macOS VMs to run simultaneously on a single Mac across all apps (including an active `.ipsw` base-image installation). Barn never stops a running VM to make room for another. `ls.running` counts VMs in the current `BARN_HOME`, while Apple's framework enforces the host-wide limit.
- **Administrator account**: Configured with passwordless sudo, Ed25519 SSH key authentication, automatic desktop login, and Remote Login enabled. SSH password authentication is disabled, and the random local password is saved in the VM slot's `password` file (`0600`).
- **Hostnames**: The guest ComputerName matches `<name>` and LocalHostName is `barn-<name>` (`barn-<name>.local`).
- **Shared folders**: Mounted inside the guest via a single VirtioFS device at `/Volumes/My Shared Files/<name>`. Each host source must resolve to an existing directory; symlinks are supported. Names accept spaces and Unicode.
- **Clipboard sync**: Syncs plain text up to 1 MiB over the VM's SSH connection whenever the desktop window gains or loses focus, skipping pasteboard items marked concealed.
- **Shutdown**: `barn mac stop` requests a clean guest shutdown and waits up to two minutes before powering the VM off (`"forced": true`); `--force` powers off immediately.

## Networks

Each VM's runner process creates an isolated user-space network at startup and tears it down on exit—without root privileges or a background daemon—using Apple's [shared-mode `vmnet` API](https://developer.apple.com/documentation/vmnet/vmnet_network_configuration_create(_:_:)):

| Item | Value |
|---|---|
| Subnet | First free `/24` from `10.10.20.0/24` through `10.10.59.0/24` that avoids host routes and other VMs (or an explicit `--subnet`) |
| Gateway | `.1` on the Mac host |
| Guest IP | `.10`, assigned via a `vmnet` DHCP reservation for the VM's MAC address |
| Topology | Host-to-guest routing and outbound NAT per VM subnet, with no LAN bridging or inbound port forwards |
{.wide}

If a newly added host route (such as a VPN) overlaps the VM's saved subnet, `start` refuses to boot with `mac_subnet_in_use`; run `barn mac configure NAME --subnet auto` to move the VM to a free subnet. Because Barn pins SSH host keys to `barn-mac-<instance_id>` rather than the IP address, changing subnets keeps SSH trust intact.

If macOS Local Network privacy blocks a third-party terminal or IDE from reaching the guest subnet (often surfacing as `No route to host`), enable that app under **System Settings → Privacy & Security → Local Network**. Barn routes its own Go SSH transport through `/usr/bin/nc` and invokes `/usr/bin/ssh` for user sessions so Apple system binaries handle the local-network socket directly.

## JSON output {#json-output}

All `barn mac` commands except interactive `ssh` support `--json` and `--yaml` on stdout while writing progress to stderr.

### `ls`

```json
{
  "schema_version": 2,
  "root": "/Users/alice/.barn/mac",
  "prepared": true,
  "base": {"version": "27.0", "build": "26A428", "base_id": "26A428-e16af589f4b705ca397f5b21"},
  "machines": [
    {
      "name": "mac1",
      "kind": "macos",
      "state": "running",
      "ready": true,
      "ssh": "ready",
      "address": "10.10.20.10",
      "address_stable": true,
      "ssh_host": "10.10.20.10",
      "ssh_port": 22,
      "user": "alice",
      "image": {"version": "27.0", "build": "26A428", "base_id": "26A428-e16af589f4b705ca397f5b21"},
      "cpus": 4,
      "memory_bytes": 8589934592,
      "disk": {"capacity_bytes": 107374182400, "allocated_bytes": 1202647040},
      "network": {"subnet": "10.10.20.0/24", "gateway": "10.10.20.1", "address": "10.10.20.10"},
      "shares": [{"name": "src", "host": "/Users/alice/src", "guest": "/Volumes/My Shared Files/src", "readonly": false}],
      "clipboard": true,
      "pid": 2545,
      "instance_id": "b1482ffc-2da7-45d9-ace5-c5f3193a9172",
      "warnings": []
    }
  ],
  "running": 1,
  "limit": 2
}
```

| Field | Values |
|---|---|
| `state` | `prepared` (created, never completed first boot), `starting`, `running`, `stopping`, `stopped`, `unknown` |
| `ready` | `true` when this check verified guest SSH connectivity and passwordless sudo |
| `ssh` | `ready`, `pending` (first boot in progress), `unavailable`, `offline`, `unchecked` |
| `observed` | Present when the running guest reports a macOS build different from its base image |
| `window_visible` | Present while the VM's desktop window is open |
| `error`, `warnings` | Last recorded failure on the slot and any SSH issues detected during this check |
{.wide}

### Lifecycle results

Single-machine operations (`up`, `restart`, `open`, `recreate`, `configure`) return a single machine result object, while batch operations (`start`, `stop`, `destroy`) return `{"machines": [...]}` even when called with one name. If a multi-VM batch partially fails, the response includes both the succeeded entries and the failures and exits `5`.

```json
{"name": "mac1", "action": "created", "state": "running", "ready": true,
 "address": "10.10.20.10", "user": "alice", "version": "27.0", "build": "26A428"}
```

| Field | Values |
|---|---|
| `action` | `created`, `started`, `running` (already running), `restarted`, `recreated`, `opened`, `configured`, `stopped`, `powered_off`, `already_stopped`, `destroyed`, `absent` |
| `forced` | `true` when `stop` timed out and powered off the VM |
| `window` | `true` when the desktop window was opened |
| `warnings` | Non-fatal notices, such as a clipboard change that takes effect on next start |
{.wide}

Other structured responses:

- **`exec --json`**: Returns the same schema as Linux `barn exec --json` (`node`, `exit_code`, `stdout`, `stderr`).
- **`password --json`**: Returns the password, or `{"name": "mac1", "copied": true}` when combined with `--copy`.
- **`ssh-config --json`**: Returns `fragment` when printing, or installation status when combined with `--install`/`--remove`.
- **`logs --json`**: Returns `name` and `logs`.
- **`doctor --json`**: Returns `ok` and `checks[]` (`name`, `ok`, `detail`, and optional `next`), exiting `3` if any check fails.

## Failures

Exit codes follow the [Barn CLI exit code table](../cli/#exit-codes), and `ssh`/`exec` pass through the remote command's exit status. Structured error objects include stable `reason` codes and a `next` recovery command:

| Reason | Exit | Meaning and next step |
|---|---:|---|
| `mac_host_unsupported` | `3` | Host is not Apple Silicon or is running macOS older than 27 |
| `mac_runner_missing` | `3` | `Barn.app` / native runner is not installed alongside the `barn` CLI |
| `mac_runner_protocol` | `3` | Installed `Barn.app` uses a different runner protocol version; reinstall matching CLI and app builds |
| `mac_root` | `2` | Invoked as `root`; run as the logged-in desktop user without `sudo` |
| `mac_download_consent` | `2` | Non-interactive macOS download requires `--yes` (or supply a local file with `--ipsw`) |
| `mac_machine_absent` | `4` | Named VM does not exist; create it with `barn mac up NAME` |
| `mac_not_initialized` | `4` | VM has not finished its first boot; complete initialization with `barn mac up NAME` |
| `mac_not_running` | `4` | `ssh` or `exec` called on a stopped VM; run `barn mac start NAME` |
| `mac_running` | `4` | Requested configuration change requires the VM to be stopped; run `barn mac stop NAME` |
| `mac_configuration_conflict` | `4` | `up` flags differ from the existing VM; run the suggested `configure` or `recreate` command |
| `ssh_config_linked` | `4` | `~/.ssh/config` is a symlink or hard link; add the printed `Include` line manually |
| `mac_vm_limit` | `6` | Two macOS VMs are already running on this Mac; stop the reported VM first |
| `mac_subnet_in_use` | `6` | A host route overlaps the VM's subnet; run `barn mac configure NAME --subnet auto` |
| `disk_full` | `6` | Insufficient free disk space to download or install the macOS base image |
| `mac_machine_damaged` | `7` | An initialized VM slot is missing its disk or identity files (the slot directory is preserved for inspection) |
| `mac_readiness_interrupted` | `130` | `barn mac stop` interrupted a first-boot SSH readiness wait |
{.wide}

## Files

```filetree {title="$BARN_HOME/mac"}
config.json # Installation identity, default base image, and ssh_config_off flag
images/
  ipsw/
    <build>.ipsw # Cached Apple restore image (.partial while downloading)
    <build>.ipsw.json # Restore image metadata and digest
  base/
    <id>/ # Read-only, unbooted macOS base image bundle
slots/
  <name>/
    state.json # Machine record (schema 2)
    disk.asif # Copy-on-write APFS disk layer cloned from the base image
    machine-id.bin # Apple Virtualization machine identifier
    auxiliary-storage.bin # NVRAM / boot auxiliary storage
    id_ed25519 # Per-VM SSH private key
    id_ed25519.pub # Per-VM SSH public key
    known_hosts # Pinned guest host key under barn-mac-<instance>
    password # Generated guest login password (mode 0600)
    runner.log # Per-VM runtime log read by barn mac logs
runtime/ # Global state lock and per-machine operation locks
```

Additional host and guest paths:

- **Control sockets**: `/tmp/barn-mac-<uid>-<hash>/`.
- **OpenSSH fragment**: `barn mac ssh-config` manages `~/.ssh/barn-mac_config` and a `# barn-mac:include` block in `~/.ssh/config` (independent of the Linux `# barn:include` block). Running `barn mac ssh-config --remove` sets `ssh_config_off` in `config.json` so subsequent lifecycle commands do not re-add the `Include` block until you run `barn mac ssh-config --install`.
- **Desktop preferences**: Barn `0.9.2` stores window positions in `~/Library/Preferences/com.pgsty.barn.plist` (upgraded from `~/Library/Preferences/io.pgsty.barn.mac-runner.plist` in `0.9.0`).
- **Runner discovery**: The `barn` CLI locates the runner relative to its resolved binary path across app bundle (`Barn.app/Contents/MacOS/barn`), pkg installer, and Homebrew `libexec` layouts, or via `BARN_MAC_RUNNER` with an absolute path, relative path, or `~/` path. Before executing VM operations, the CLI verifies runner protocol `2`; `barn mac doctor` also verifies the runner's local code signature.
- **Guest configuration files**: Inside the macOS guest, Barn writes `~/.ssh/authorized_keys`, `/private/etc/sudoers.d/80-barn`, and `/etc/ssh/sshd_config.d/000-barn.conf`, configures `ComputerName` and `LocalHostName`, and disables idle sleep via `pmset`.
