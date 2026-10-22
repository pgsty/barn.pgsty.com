---
title: Mac Commands
description: barn mac commands and flags, machine rules, JSON results, failure reasons, networks, and files.
weight: 25
icon: fa-brands fa-apple
---

```text
barn [--json|--yaml] [-v|--verbose] mac <command> [flags] [name...]
```

To run macOS guests, use Apple Silicon with macOS 27 or later, as the logged-in user.
Commands that require the native runner reject root with `mac_root` and unsupported hosts with `mac_host_unsupported`.
Top-level help hides the command on Linux and Intel Macs. Local-record reads such as `image ls` do not require a native runner.
Without a subcommand, `barn mac` runs `barn mac ls`.

This reference describes the 0.9.1 command interface and `Barn.app`, using
runner protocol 2. The native component requires a source build in 0.9.1; see
[installation](../../start/macos/#install) and [source builds](../../start/source-build/#mac-component).

## Commands

| Command | Purpose |
|---|---|
| `ls` | list every VM with state, address, SSH, macOS, resources and shares; aliases `list`, `status`, `st` |
| `up [name]` | create the VM if needed, start it, wait for SSH and sudo |
| `start [name...]` | start existing VMs |
| `stop [name...]` | shut down normally; power off after two minutes |
| `restart [name]` | stop, then start, applying configuration changes |
| `open [name]` | show the desktop, starting the VM first if needed |
| `ssh [name]` | interactive shell, or, after `--`, a command line for the guest shell |
| `exec [name] -- cmd` | run a command, keeping argument boundaries |
| `configure name` | change a VM's settings |
| `recreate name` | replace the VM with a fresh macOS, keeping its settings |
| `destroy name...` | delete VMs |
| `password [name]` | show or copy the login password |
| `ssh-config` | print, install or remove the OpenSSH entries |
| `logs [name]` | recent runtime log |
| `setup` | prepare the macOS base image without creating a VM |
| `image ls` | list restore images and base images with the VMs using them; alias `list` |
| `image update` | prepare Apple's newest macOS 27 as the default base image |
| `image prune` | list, and with `--yes` delete, unused images |
| `doctor` | check the host, the component, the base image, and every VM |

### Flags by command

| Command | Flags |
|---|---|
| `up` | `--cpu` `--memory` `--disk` `--user` `--share` `--clipboard` `--subnet` `--ipsw` `-y`/`--yes` `-n`/`--no-wait` `--open` |
| `start` | `--all` `-n`/`--no-wait` `--open` `--recovery` |
| `stop` | `--all` `--force` |
| `restart` | `-n`/`--no-wait` `--open` |
| `configure` | `--cpu` `--memory` `--share` `--unshare` `--clipboard` `--subnet` |
| `recreate` | `--update` `--force` `-n`/`--no-wait` |
| `destroy` | `--force` |
| `password` | `-c`/`--copy` |
| `ssh-config` | `-i`/`--install` `--remove` |
| `logs` | `-n`/`--lines` (default 100, at most 10000) |
| `setup` | `--ipsw` `--disk` `-y`/`--yes` |
| `image update` | `--ipsw` `-y`/`--yes` |
| `image prune` | `--installers` `-y`/`--yes` |

For commands with an optional VM name, omitting it selects the only VM, or `mac1`.
If several VMs exist and none is named `mac1`, the command asks for a name.
`start` and `stop` accept several names, or `--all`.
`destroy` and `recreate` describe what they will delete and require you to type the command name.
Without a terminal, use `--force` to confirm.

`--no-wait` means that the VM is running; it does not mean that the guest is ready.
For a new VM, run `up NAME` without that flag to complete SSH key installation and sudo setup.

`ls` does not complete provisioning. Ordinary `start` requires a VM that completed its first boot.
For an uninitialized VM that is already running, use `open` to show its first boot. For a stopped one, use `up NAME --open`.
`--recovery` skips the normal readiness wait and always shows the Recovery desktop.

### Flag values

| Flag | Value |
|---|---|
| `--cpu` | virtual CPUs, at least 2 and at most the Mac's logical CPUs; default 4 |
| `--memory` | `16G`, `16GiB`, `16GB` or bytes; whole MiB, at least 4 GiB and at most installed memory; default 8 GiB |
| `--disk` | base image capacity, at least 32 GiB. Default: the prepared base image's capacity, or 100 GiB for the first base image. Another capacity requires a matching base image; Barn installs one if absent |
| `--user` | administrator account; default your macOS user name, or `barn` when that is not a valid account name |
| `--share` | `[name=]path[:ro\|:rw]`, repeatable, at most 8; the name defaults to the last path component; `~/` expands to your home |
| `--clipboard` | `on` or `off` (also `true`/`false`, `yes`/`no`); default on |
| `--subnet` | a canonical private `/24` such as `10.10.30.0/24`, or `auto` for the first free one |

If creation options differ from an existing VM, `up` refuses them. Its `next:` line identifies the corrective action.
Use `configure` to change CPUs, memory, shares, subnet, or clipboard settings.
The account and disk capacity remain fixed for the VM's lifetime. `recreate` preserves them.
To use a different account or disk capacity, create another VM. To change macOS, run `image update`, then `recreate --update`.

`recreate --update` also preserves disk capacity.
If that macOS build has no base image at the VM's capacity, prepare one first.
For example, run `barn mac setup --disk 200G`, then retry `barn mac recreate NAME --update`.

Mac sizes use binary units: `16G`, `16GB`, and `16GiB` all mean 16 GiB.
Share names contain 1–64 letters, digits, dots, underscores, or hyphens. They must start with a letter or digit.
If `configure --share` reuses a name, it replaces that share's path and options. `--unshare` removes only the named share.

Stop the VM before changing hardware, shares, or subnet.
You can change the saved clipboard setting while the VM runs, but it applies at the next start.
Use the desktop menu to control clipboard synchronization in the current session.

## Machines

- **Names**: 1–32 lowercase letters, digits, and inner hyphens. Names start with a letter: `mac1`, `dev`, `build-2`.
- **Running limit**: two macOS VMs per Mac, including VMs from other tools and macOS installation.
  Barn never stops a VM to release capacity for another.
- **Account**: an administrator with passwordless sudo, SSH key login, desktop automatic login, and Remote Login.
  Barn disables SSH password login. It stores the random login password in the VM's `password` file.
- **Guest names**: the computer name matches the VM name.
  The local host name is `barn-<name>`, so the guest answers as `barn-<name>.local`.
- **Shares**: macOS mounts one VirtioFS device under `/Volumes/My Shared Files/<name>`.
  Shares must be existing directories, not symlinks. Change shares only while the VM is stopped.
- **Clipboard**: Barn synchronizes plain text over the VM's SSH connection when its window gains or loses focus.
  The limit is 1 MiB. Barn never sends items marked concealed.
- **Stop**: Barn requests normal shutdown through the guest's macOS.
  If the VM still runs after two minutes, Barn powers it off and returns `"forced": true`.
  `--force` powers it off immediately.

`ls.running` counts running, starting, and stopping VMs in this `BARN_HOME`.
It does not count VMs from other applications or Barn data roots. Apple's runtime still enforces the host-wide VM limit.

## Networks

Each VM's runner process creates its network at startup and removes it at shutdown, without a daemon or root privileges.

| Item | Value |
|---|---|
| Subnet | first free private `/24` from `10.10.20.0/24` to `10.10.59.0/24`, avoiding host routes and other VMs; `--subnet` selects one |
| Gateway | `.1`, the Mac |
| Guest address | `.10`, by DHCP reservation for the VM's MAC address |
| Reachability | host access and outbound NAT; separate subnets, no LAN bridge or incoming port forwards |

Barn uses Apple's [shared-mode vmnet network](https://developer.apple.com/documentation/vmnet/vmnet_network_configuration_create(_:_:)).
A separate subnet describes the topology; it is not a firewall policy.

If a host route now overlaps the subnet, such as a VPN route, `start` refuses it with reason `mac_subnet_in_use`.
SSH host keys are pinned to the VM instance, not its address. Thus `configure --subnet` preserves trust.

macOS Local Network privacy can block third-party client connections to these networks.
The client can report "No route to host". Check its access under **Privacy & Security → Local Network**.
Barn uses Apple's `/usr/bin/nc` for Go SSH transport and `/usr/bin/ssh` for user commands.
This avoids the restriction observed with direct third-party connections. Ordinary routing failures can also cause the error.

## JSON output {#json-output}

Commands support `--json` and `--yaml` results. An interactive `ssh` session has no structured output.
Barn writes progress to stderr.

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
| `state` | `prepared` (never booted to readiness), `starting`, `running`, `stopping`, `stopped`, `unknown` |
| `ready` | `true` only when this check reached the guest over SSH with sudo |
| `ssh` | `ready`, `pending` (first boot in progress), `unavailable`, `offline`, `unchecked` |
| `observed` | present when the guest reports a different macOS build than its base image |
| `window_visible` | present while the desktop window is shown |
| `error`, `warnings` | the last recorded failure, and SSH problems found by this check |

### Lifecycle results

`up`, `restart`, `open`, `recreate`, and `configure` return one result.
`start`, `stop`, and `destroy` return `{"machines": [...]}`, even for one name.
If an operation on several VMs partially succeeds, the result includes successful VMs and reports failures separately.
The command exits 5. Inspect the result before retrying the whole group.

```json
{"name": "mac1", "action": "created", "state": "running", "ready": true,
 "address": "10.10.20.10", "user": "alice", "version": "27.0", "build": "26A428"}
```

| Field | Values |
|---|---|
| `action` | `created`, `started`, `running` (already running), `restarted`, `recreated`, `opened`, `configured`, `stopped`, `powered_off`, `already_stopped`, `destroyed`, `absent` |
| `forced` | `true` when a normal stop had to power the VM off |
| `window` | `true` when the desktop was shown |
| `warnings` | non-fatal follow-ups, such as a change that applies at the next start |

`exec --json` returns the same object as Linux `barn exec --json`.
`node` is the VM name. `exit_code`, `stdout`, and `stderr` come from the guest.
Interactive `ssh` has no JSON output.

`password --json` includes the password. `password --copy --json` instead returns `{"name":"mac1","copied":true}`.
If neither install nor remove is requested, `ssh-config` returns a `fragment` string.
`logs` returns `name` and `logs`.
`doctor` returns `ok` and `checks`. Each check contains `name`, `ok`, `detail`, and optional `next`.
A failed diagnosis exits 3.

## Failures

Exit codes follow the [Barn CLI](../cli/#exit-codes).
`ssh` and `exec` return a remote command's exit status unchanged.
Where defined, JSON failures include stable `reason` values. They also include a `next` command when available.
Common failures include:

| Reason | Exit | Meaning and next step |
|---|---|---|
| `mac_host_unsupported` | 3 | not Apple Silicon, or older than macOS 27 |
| `mac_runner_missing` | 3 | the Mac component is not installed next to the CLI |
| `mac_runner_protocol` | 3 | the component uses an incompatible runner protocol; reinstall matching components |
| `mac_root` | 2 | run as your normal login user, not with sudo |
| `mac_download_consent` | 2 | downloading macOS needs `--yes` without a terminal, or use `--ipsw` |
| `mac_machine_absent` | 4 | no VM by that name; `barn mac up NAME` |
| `mac_not_initialized` | 4 | the VM has not finished its first boot; `barn mac up NAME` |
| `mac_not_running` | 4 | `ssh`/`exec` need a running VM; `barn mac start NAME` |
| `mac_running` | 4 | a change needs the VM stopped; `barn mac stop NAME` |
| `mac_configuration_conflict` | 4 | `up` options differ from the existing VM; run the specified `configure` or `recreate` command |
| `ssh_config_linked` | 4 | `~/.ssh/config` is a link; add the printed `Include` line yourself |
| `mac_vm_limit` | 6 | two macOS VMs already run; stop the named one |
| `mac_subnet_in_use` | 6 | a host route now overlaps the VM's network; `configure NAME --subnet auto` |
| `disk_full` | 6 | not enough free space to download or install macOS |
| `mac_machine_damaged` | 7 | a VM that booted before lost disk or identity files; its directory is kept |
| `mac_readiness_interrupted` | 130 | a `stop` interrupted a first-boot SSH wait |

## Files

```text
$BARN_HOME/mac/
  config.json                        installation identity and default base
  images/ipsw/<build>.ipsw(.json)    Apple restore images; .partial while downloading
  images/base/<id>/                  read-only, unbooted macOS bases
  slots/<name>/state.json            the machine record (schema 2)
  slots/<name>/disk.asif             copy-on-write disk layer over the base
  slots/<name>/machine-id.bin        Apple machine identifier
  slots/<name>/auxiliary-storage.bin boot storage
  slots/<name>/id_ed25519(.pub)      the machine's SSH key pair
  slots/<name>/known_hosts           the pinned host key, under barn-mac-<instance>
  slots/<name>/password              login password, mode 0600
  slots/<name>/runner.log            runtime log (barn mac logs)
  runtime/                          state and per-machine operation locks
```

Runtime sockets use `/tmp/barn-mac-<uid>-<hash>/`.
`ssh-config` writes `~/.ssh/barn-mac_config` and one `# barn-mac:include` block in `~/.ssh/config`.
This is independent of the Linux `# barn:include` block.

The 0.9.0 app saves desktop window positions in `~/Library/Preferences/io.pgsty.barn.mac-runner.plist`.
The 0.9.1 app uses `~/Library/Preferences/com.pgsty.barn.plist`.

Removing SSH integration sets `ssh_config_off` in `config.json`.
Lifecycle commands do not reinstall the SSH entries until you run `ssh-config --install`.

The CLI finds the runner relative to its resolved executable path. It supports app bundle, installer, and Homebrew `libexec` layouts.
For a developer override, set `BARN_MAC_RUNNER` to an absolute executable path.
Before VM operations, the CLI checks runner protocol 2.
`doctor` verifies the runner's code signature. It does not verify Apple notarization.

Inside the guest, Barn writes `~/.ssh/authorized_keys`, `/private/etc/sudoers.d/80-barn`, and `/etc/ssh/sshd_config.d/000-barn.conf`.
It sets the computer and local host names. It disables sleep with `pmset`.
