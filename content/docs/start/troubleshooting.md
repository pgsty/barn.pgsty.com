---
title: Troubleshooting
description: Short, safe runbooks for setup, networking, images, drift, interrupted state, and SSH.
weight: 70
icon: fa-solid fa-life-ring
---

This guide covers Linux lab diagnostics for **Barn 0.9.2**. For macOS guests, run `barn mac doctor` and see the [Mac troubleshooting section](../macos/#troubleshooting).

Start by collecting the three JSON diagnostic reports (`barn status` also reconciles interrupted process state when no other command holds the lock):

```bash
barn doctor --json
barn network status --json
barn status --json
```

`barn doctor` exits `0` whenever host compute checks pass, even if a `class: network` check reports an error—inspect both `checks[]` and `barn network status --json` before assuming `barn up` can attach to the private network.

## Download and PATH problems {#download-and-path-problems}

The release installer downloads binaries from GitHub Releases (`--mirror` only selects the guest image repository). If your network requires a proxy to reach GitHub, export `HTTPS_PROXY` or `ALL_PROXY` in your terminal session (macOS System Settings proxy entries are not inherited by CLI tools automatically).

The user-scoped installer places binaries in `~/.local/bin`. If `barn` is not found or runs an older version after installation, verify your `PATH`:

```bash
export PATH="$HOME/.local/bin:$PATH"
command -v barn
barn version
```

Always keep `barn` and its packaged `barn-hosts-helper` from the same release in their relative directory layout.

## No inventory found

When neither an inventory file nor an applied deployment exists, an interactive `barn up` generates a starter `barn.yml`. To use an existing file, run `plan`, `up`, or `validate` in the directory containing `barn.yml` / `pigsty.yml` or pass `-f /path/to/file` (or generate a template first with `barn init`).

Without `-f`, `plan`, `up`, `reload`, and `recreate` check the current directory for `barn.yml`, `barn.yaml`, `pigsty.yml`, and `pigsty.yaml` in that order, falling back to the applied specification in `BARN_HOME` only when none of those files exist. If the first matching file contains syntax errors, Barn fails immediately rather than falling back; pass `-f pigsty.yml` when an older `barn.yml` sits in the same directory.

If `barn status` reports `no deployment state found`, the active `BARN_HOME` has no applied deployment (either fresh or previously purged).

## init rejects a directory symlink {#linked-directory}

`atomic create parent is not a real directory: ...` in Barn 0.9.2 can mean that the output directory is a symlink, even when its target is a writable directory. The [Unreleased path fix](../../about/unreleased/#paths) resolves directory aliases and creates missing parents for `init -o`.

With 0.9.2, use the physical directory path for the output:

```bash
barn init -o "$(pwd -P)/barn.yml"
```

You can also run `cd -P .` before `barn init`; the directory symlink can remain in place. For a nested output path on 0.9.2, create its parent directory first. Existing output files still require `--force`, and output-file symlinks are not followed for writes.

## Setup needs sudo

Before prompting for a password, `barn setup` prints the exact host mutation it is about to perform and hands the interactive terminal directly to `sudo`. Passing `--yes` auto-confirms Barn's plan prompt, while `sudo` authentication itself still requires an interactive terminal, cached credentials, or a `NOPASSWD` sudoers rule. Run `barn setup --dry-run` to preview the host plan without executing it.

On macOS, `barn setup` downloads and verifies the pinned `socket_vmnet` package before requesting `sudo`, so a network failure never prompts for a password.

## Native acceleration or compatibility runtime is unavailable {#native-acceleration-or-compatibility-runtime-is-unavailable}

Barn requires HVF on macOS or KVM on Linux for native hardware acceleration, and uses QEMU TCG software emulation only when you explicitly request a foreign `vm_arch` or run an image covered by a built-in compatibility rule (such as `el8` `arm64` on Apple Silicon). It never falls back to TCG after a native HVF/KVM failure.

Homebrew's `qemu` formula includes both `arm64` and `amd64` system emulators, whereas Linux `barn setup` installs only the host-native emulator—install the matching `qemu-system-*` binary and UEFI firmware manually before running foreign-architecture guests on Linux.

## Network is partial or invalid

An intact but stopped Barn host network is restarted automatically by an interactive `barn up`. If `barn network status` reports a `partial` or `invalid` state, inspect and apply Barn's managed cleanup plan instead of deleting system network files by hand:

```bash
barn network status --json --verbose
barn network uninstall --json
barn network uninstall --yes
```

If the Linux bridge smoke test fails during `setup`, Barn rolls back the network changes automatically; only an explicit `automatic rollback failed` message requires manual cleanup.

On macOS, `barn setup` automatically repairs a missing or overly restrictive `/var/log/barn-vmnet` directory (`root:wheel 0755`), while refusing to touch a symlink, foreign owner, or group/world-writable directory—follow the exact remediation command printed by `barn network status`.

## Linux bridge helper fails

On Debian and Ubuntu hosts, check the ownership and setuid mode on `/usr/lib/qemu/qemu-bridge-helper` (expected `root:<caller-accessible-group> 4750`):

```bash
id
stat -c '%U:%G %a %n' /usr/lib/qemu/qemu-bridge-helper
dpkg-statoverride --list /usr/lib/qemu/qemu-bridge-helper
```

## Plan reports recreate or missing

- **`recreate`**: The node's inventory specification changed. Inspect `barn plan` and back up any data on the root or non-persistent disks before running `barn recreate <node>` (pass `--force` in non-interactive scripts).
- **`missing`**: A provisioned node was removed from the YAML inventory. Either restore its YAML entry or run `barn destroy <node>` to delete the VM.

With the [Unreleased node-selection changes](../operations/#selected-nodes), `barn plan node-1` and `barn recreate node-1` retain unselected peers' applied definitions. An unrelated peer edit no longer requires rebuilding it together. Real conflicts in addresses, aliases, control-node roles, or deployment-wide settings still need to be resolved.

## A node did not become ready {#a-node-did-not-become-ready}

Readiness requires a working management SSH connection and a verified guest instance UUID. When a node fails to create, boot, or become reachable over management SSH, `barn up` reports the failing node and stage and exits with code `5`. Inspect its logs:

```bash
barn logs <node>                  # guest serial console
barn logs <node> --source qemu    # QEMU stderr and diagnostics
barn logs --source events         # host setup and deployment event log
barn status
```

Secondary guest stages—data disks, Virtio-9p shares, hostname, `/etc/hosts`, control-node SSH, and the fixed-IP private interface—run independently after management SSH comes up. If one of those stages fails, `barn up` exits `0` and records the limitation under `nodes[].warnings`:

| Reported limitation | Remediation |
|---|---|
| Data disk unavailable | Resolve the missing device, filesystem tool, busy mount, or host I/O error, then re-run `barn up` |
| Shared directory is read-only | Check host and guest write permissions, then re-run `barn up` |
| Guest hosts or control-node SSH incomplete | Re-run `barn up` to refresh the managed files inside the guest |
| Private interface unavailable | Check `barn network status`, repair the host bridge/vmnet, and re-run `barn up` |

Re-running `barn up` retries only the unfinished stages without restarting healthy VMs (and may reformat unrecognized or confirmed damaged test data filesystems; see [Data disks](../../reference/configuration/#data-disks)). Pass `--rollback` to `barn up` if you want failed initial preparation artifacts removed in the same run.

For Linux shared folders, both QEMU and the guest kernel need 9p support. A valid host path cannot make an unsupported guest kernel mount 9p; use SSH/SCP/rsync or a kernel with 9p support. Linux-guest sharing on a macOS host also requires the [Unreleased fix](../../about/unreleased/#sharing); native macOS guests use VirtioFS separately.

## SSH fails

Check `barn status`, `barn ssh-config`, and `barn logs <node>`.

- **Deployment SSH keys**: If the host's `.pub` file is missing, Barn derives it from the intact private key on startup. If the private key itself is missing, restore it from backup—Barn never generates a replacement key for existing VMs. If the control node's copy of the private key is missing, `barn up` reports a `control-ssh` warning while host-to-guest management SSH continues to work.
- **Port reassignment and host keys**: If another process occupies a stopped VM's loopback SSH port, the next `barn start` or `barn up` picks a free port and updates `~/.ssh/barn_config`. SSH host-key verification is scoped to each VM instance UUID, so recreating a node never triggers stale `known_hosts` errors.
- **Dotfile-managed `~/.ssh/config`**: If `~/.ssh/config` is a symlink or hard link, Barn writes `~/.ssh/barn_config` and prints the `Include` line for you to add. If `barn ssh meta` works but `ssh meta` fails, verify that `Include` line.
- **Remote command syntax**: Place `--` between the node name and remote command (`barn exec meta -- hostname`); see [SSH passthrough and completion](../../reference/cli/#ssh-passthrough-and-completion).

## Catalog or image verification fails

Barn embeds active and standby Minisign public keys and rejects unknown signers, catalog revision rollbacks, file size or SHA-256 mismatches, and malformed `qcow2` files. Always pull from a validly signed repository or register local images through `barn image import --sha256 ...` rather than copying files directly into `~/.barn/images`.

## A command was killed {#a-command-was-killed}

First run `barn status`. If another Barn process currently holds the deployment lock, `status` displays a `note`—wait for that operation to finish before intervening.

When no command holds the lock, `barn status` verifies each recorded QEMU process identity (matching both PID and process start time) and reconciles the state automatically:

| Interrupted state | Automatic recovery / next step |
|---|---|
| Host rebooted or QEMU PID was recycled by an unrelated process | `barn status` detects the mismatched process identity and marks the VM `stopped`; run `barn start` |
| `barn stop` was interrupted while QEMU stayed running | `barn status` restores `running` state; re-run `barn stop` if you still want to shut it down |
| Initial `barn up` failed during preparation | Fix the inventory and re-run `barn up -f barn.yml`; Barn rolls back journaled unfinished artifacts |
| `barn destroy` was interrupted midway | Re-run the same `barn destroy` or `barn purge` command to finish cleanup |

If Barn cannot confirm whether a recorded process belongs to the node (or if a QEMU process is alive but its QMP socket is missing), it blocks further mutations so it never kills an unrelated process. Preserve the state directory and logs (`barn logs <node> --source qemu --verbose`) rather than deleting PID or lock files by hand.

When filing an issue on GitHub, include the exact command and exit code, `barn version`, host OS/architecture, QEMU version, and the JSON output of `barn doctor`, `barn network status`, and `barn status`.
