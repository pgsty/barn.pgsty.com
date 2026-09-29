---
title: Mac Commands
description: farrow mac commands and flags, machine rules, JSON results, failure reasons, networks, and files.
weight: 25
icon: fa-brands fa-apple
---

> [!IMPORTANT]
> **Unreleased.** `farrow mac` is not part of public 0.8.0 or any package yet.
> This reference describes the development tree validated on 2026-09-29; see
> [Status](../../about/status/#macos-guests). Check `farrow mac --help` of the
> binary you run. The task-oriented guide is [macOS Virtual Machines](../../start/macos/).

```text
farrow [--json|--yaml] [-v|--verbose] mac <command> [flags] [name...]
```

`farrow mac` requires Apple Silicon and macOS 27 or later, and runs as the
logged-in user; it refuses to run as root. On other hosts the command is
hidden, and commands that need the Mac component fail with
`mac_host_unsupported`. Bare `farrow mac` is `farrow mac ls`.

## Commands

| Command | Purpose |
|---|---|
| `ls` | every machine with state, address, SSH, macOS, resources and shares; aliases `list`, `status`, `st` |
| `up [name]` | create the machine if needed, start it, wait for SSH and sudo |
| `start [name...]` | start existing machines |
| `stop [name...]` | shut down normally; power off after two minutes |
| `restart [name]` | stop, then start, applying configuration changes |
| `open [name]` | show the desktop, starting the machine first if needed |
| `ssh [name]` | interactive shell, or, after `--`, a command line for the guest shell |
| `exec [name] -- cmd` | run a command, keeping argument boundaries |
| `configure name` | change a machine's settings |
| `recreate name` | replace the machine with a fresh macOS, keeping its settings |
| `destroy name...` | delete machines |
| `password [name]` | show or copy the login password |
| `ssh-config` | print, install or remove the OpenSSH entries |
| `logs [name]` | recent runtime log |
| `setup` | prepare the macOS base without creating a machine |
| `image ls` | restore images and bases with the machines using them; alias `list` |
| `image update` | prepare Apple's newest macOS 27 as the default base |
| `image prune` | list, and with `--yes` delete, unused images |
| `doctor` | check the host, the component, the base and every machine |

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

A command without a machine name acts on the only machine, or on `mac1`; with
several machines and none named `mac1`, it asks for a name. `start` and `stop`
accept several names, or `--all`. `destroy` and `recreate` describe what they
delete and ask for the command name to be typed; `--force` confirms without a
terminal.

### Flag values

| Flag | Value |
|---|---|
| `--cpu` | virtual CPUs, at least 2 and at most the Mac's logical CPUs; default 4 |
| `--memory` | `16G`, `16GiB`, `16GB` or bytes; at least 4 GiB and at most installed memory; default 8 GiB |
| `--disk` | capacity of the base, at least 32 GiB; default the prepared base's, 100 GiB. Another capacity installs another base |
| `--user` | administrator account; default your macOS user name, or `farrow` when that is not a valid account name |
| `--share` | `[name=]path[:ro\|:rw]`, repeatable, at most 8; the name defaults to the last path component; `~/` expands to your home |
| `--clipboard` | `on` or `off`; default on |
| `--subnet` | a canonical private `/24` such as `10.10.30.0/24`, or `auto` for the first free one |

`up` refuses creation options that differ from an existing machine instead of
ignoring them, and its `next:` line names the fix. CPUs, memory, shares, the
subnet and the clipboard change with `configure`. The account and disk capacity
are fixed for a machine's lifetime, and `recreate` keeps them: other values
need another machine. A different macOS comes from `image update`, then
`recreate --update`.

## Machines

- **Names**: 1–32 lowercase letters, digits and inner hyphens, starting with a
  letter: `mac1`, `dev`, `build-2`.
- **Running limit**: two macOS virtual machines per Mac, counting other tools
  and macOS installation. Farrow never stops a machine to make room.
- **Account**: an administrator with passwordless sudo, SSH key login, desktop
  automatic login and Remote Login. SSH password login is disabled. The login
  password is random and stored in the machine's `password` file.
- **Guest names**: the computer name is the machine name; the local host name is
  `farrow-<name>`, so the guest answers as `farrow-<name>.local`.
- **Shares**: one VirtioFS device mounted by macOS under
  `/Volumes/My Shared Files/<name>`. Shares must be existing directories, not
  symlinks, and change only while the machine is stopped.
- **Clipboard**: plain text, synchronized over the machine's SSH connection
  when its window gains or loses focus; at most 1 MiB; items marked concealed
  are never sent.
- **Stop**: normal shutdown through macOS in the guest; if the machine is still
  running after two minutes it is powered off and the result carries
  `"forced": true`. `--force` powers off at once.

## Networks

Each machine's network is created by its own runner process when the machine
starts and disappears when it stops. No daemon and no root is involved.

| Item | Value |
|---|---|
| Subnet | first free private `/24` from `10.10.20.0/24` to `10.10.59.0/24`, avoiding host routes and other machines; `--subnet` selects one |
| Gateway | `.1`, the Mac |
| Guest address | `.10`, by DHCP reservation for the machine's MAC address |
| Reachability | the Mac and the internet through NAT; not other machines, not the LAN |

`start` refuses a subnet that a host route now overlaps, such as a VPN, with
reason `mac_subnet_in_use`. SSH host keys are pinned to the machine instance,
not its address, so `configure --subnet` keeps trust.

macOS Local Network privacy stops third-party programs from connecting to
these networks unless their app is allowed under **Privacy & Security → Local
Network**; the error is "No route to host". Farrow itself connects through
Apple's `/usr/bin/nc` and `/usr/bin/ssh`, which are exempt.

## JSON output {#json-output}

Every command honors `--json` and `--yaml`. Progress goes to stderr.

### `ls`

```json
{
  "schema_version": 2,
  "root": "/Users/alice/.farrow/mac",
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
| `observed` | present when the guest reports another macOS build than its base |
| `window_visible` | present while the desktop window is shown |
| `error`, `warnings` | the last recorded failure, and SSH problems found by this check |

### Lifecycle results

`up`, `restart`, `open`, `recreate` and `configure` return one result;
`start`, `stop` and `destroy` return `{"machines": [...]}`, one result per
machine, even for a single name.

```json
{"name": "mac1", "action": "created", "state": "running", "ready": true,
 "address": "10.10.20.10", "user": "alice", "version": "27.0", "build": "26A428"}
```

| Field | Values |
|---|---|
| `action` | `created`, `started`, `running` (already running), `restarted`, `recreated`, `opened`, `configured`, `stopped`, `powered_off`, `already_stopped`, `destroyed`, `absent` |
| `forced` | `true` when a normal stop had to power the machine off |
| `window` | `true` when the desktop was shown |
| `warnings` | non-fatal follow-ups, such as a change that applies at the next start |

`exec --json` returns the same object as Linux `farrow exec --json`: `node` is
the machine name, and `exit_code`, `stdout` and `stderr` come from the guest.
An interactive `ssh` has no JSON form.

## Failures

Exit codes are the [Farrow CLI's](../cli/#exit-codes). A remote command's own
exit status passes through `ssh` and `exec` unchanged. JSON failures carry a
stable `reason` and a `next` command:

| Reason | Exit | Meaning and next step |
|---|---|---|
| `mac_host_unsupported` | 3 | not Apple Silicon, or older than macOS 27 |
| `mac_runner_missing` | 3 | the Mac component is not installed next to the CLI |
| `mac_runner_protocol` | 3 | CLI and component come from different builds; install them together |
| `mac_root` | 2 | run as your normal login user, not with sudo |
| `mac_download_consent` | 2 | downloading macOS needs `--yes` without a terminal, or use `--ipsw` |
| `mac_machine_absent` | 4 | no machine by that name; `farrow mac up NAME` |
| `mac_not_initialized` | 4 | the machine has not finished its first boot; `farrow mac up NAME` |
| `mac_not_running` | 4 | `ssh`/`exec` need a running machine; `farrow mac start NAME` |
| `mac_running` | 4 | a change needs the machine stopped; `farrow mac stop NAME` |
| `mac_configuration_conflict` | 4 | `up` options differ from the existing machine; the named `configure` or `recreate` |
| `mac_legacy_state` | 4 | Mac data from an unreleased development build; `farrow mac migrate` converts it |
| `ssh_config_linked` | 4 | `~/.ssh/config` is a link; add the printed `Include` line yourself |
| `mac_vm_limit` | 6 | two macOS VMs already run; stop the named one |
| `mac_subnet_in_use` | 6 | a host route now overlaps the machine's network; `configure NAME --subnet auto` |
| `disk_full` | 6 | not enough free space to download or install macOS |
| `mac_machine_damaged` | 7 | a machine that booted before lost disk or identity files; its directory is kept |
| `mac_readiness_interrupted` | 130 | a `stop` interrupted a first-boot SSH wait |
| `sudo_unavailable` | 3 | `migrate` needs sudo to remove the development builds' root daemon |

## Files

```text
$FARROW_HOME/mac/
  config.json                        installation identity and default base
  images/ipsw/<build>.ipsw(.json)    Apple restore images; .partial while downloading
  images/base/<id>/                  read-only, unbooted macOS bases
  slots/<name>/state.json            the machine record (schema 2)
  slots/<name>/disk.asif             copy-on-write disk layer over the base
  slots/<name>/machine-id.bin        Apple machine identifier
  slots/<name>/auxiliary-storage.bin boot storage
  slots/<name>/id_ed25519(.pub)      the machine's SSH key pair
  slots/<name>/known_hosts           the pinned host key, under farrow-mac-<instance>
  slots/<name>/password              login password, mode 0600
  slots/<name>/runner.log            runtime log (farrow mac logs)
```

Runtime sockets live in `/tmp/farrow-mac-<uid>-<hash>/`. `ssh-config` writes
`~/.ssh/farrow-mac_config` and one `# farrow-mac:include` block in
`~/.ssh/config`, independent of the Linux `# farrow:include` block. The desktop
window positions are saved in `~/Library/Preferences/io.pgsty.farrow.mac-runner.plist`.

Inside the guest, Farrow writes `~/.ssh/authorized_keys`,
`/private/etc/sudoers.d/80-farrow`, `/etc/ssh/sshd_config.d/000-farrow.conf`,
the computer and local host names, and disables sleep with `pmset`.
