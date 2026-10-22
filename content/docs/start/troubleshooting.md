---
title: Troubleshooting
description: Short, safe runbooks for setup, networking, images, drift, interrupted state, and SSH.
weight: 70
icon: fa-solid fa-life-ring
---

This page covers **Barn 0.9.1**. Check `barn version`
before applying version-specific guidance.

For macOS guests, use `barn mac doctor` and the [Mac troubleshooting guide](../macos/#troubleshooting).
The diagnostics below apply to Linux labs.

Start with diagnostics (`status` may reconcile interrupted runtime state):

```bash
barn doctor --json
barn network status --json
barn status --json
```

`doctor` exits 0 when host compute capability passes, even if a `class: network` check reports an error.
Read those checks and the separate network status before assuming that `up` can start a lab.
These commands diagnose the host and VM processes; `up` checks guest readiness.
Check any required application separately inside the guest.

## Download and PATH problems

The installer uses GitHub Release assets. `--mirror` selects the Barn image repository. It does not redirect installer downloads. If your network needs a proxy, set `HTTPS_PROXY` or `ALL_PROXY` to your existing proxy's address in the terminal. A macOS system proxy setting alone does not configure these environment
variables for command-line tools.

The user-scoped installer defaults to `~/.local/bin`. If `barn` is missing or
reports an older version after installation, check which executable is selected:

```bash
export PATH="$HOME/.local/bin:$PATH"
command -v barn
barn version
```

For Homebrew or native packages, use that channel's executable instead. Keep the
CLI and its packaged `barn-hosts-helper` from the same release together.

## No inventory found

If neither an inventory nor a deployment exists, interactive `up` can create the first default inventory.
To use an existing file, run `plan`, `up`, or `validate` beside `barn.yml`/`pigsty.yml`, or pass `-f /path/to/file`.
To generate a file yourself, run `barn init`.

Without an explicit file, `plan`, `up`, `reload`, and `recreate` search the current directory.
They check `barn.yml`, `barn.yaml`, `pigsty.yml`, then `pigsty.yaml`, in that order.
If discovery finds no file and deployment state exists, they use its applied specification.
If the first matching file is malformed, they fail without trying another file or applied state.
Pass `-f` explicitly if an old `barn.yml` shadows the intended `pigsty.yml`.

Status, start, stop, SSH, and destroy use applied state.
If `status` reports `no deployment state found`, the selected `BARN_HOME` has no applied deployment.
It may be fresh or previously purged.

## Setup needs sudo

The line before the prompt names the exact host mutation. Barn attaches an
interactive terminal directly to sudo when the privileged step begins.
`--yes` accepts the setup plan. It does not bypass sudo authentication.
Automation needs an existing credential or a suitable NOPASSWD policy. Use
`barn setup --dry-run` to inspect the plan first.

On macOS, setup obtains the pinned socket_vmnet package before requesting
administrator authentication. A download failure therefore does not require a
password. The setup plan specifies sudo use and the socket_vmnet source. If an automatically selected subnet changes after the first confirmation, setup asks again unless you supplied `--yes`.

## Native acceleration or compatibility runtime is unavailable

Native acceleration requires HVF on macOS or KVM on Linux. Barn uses TCG software emulation only for an explicit foreign `vm_arch` or a built-in image/host compatibility rule. It never falls back after an arbitrary native failure. Homebrew QEMU contains both system
emulators. Linux setup installs only the native family, so a foreign guest also
requires its matching `qemu-system-*` binary and firmware.

`plan` resolves images from the image catalog and their intended runtime without QEMU installed. Imported `local-*` images still need `qemu-img` and a valid cache.
`up` and `recreate`
check the selected emulator and firmware before changing VM resources.
TCG is useful for compatibility checks, but its timings do not represent native
VM performance.

## Network is partial or invalid

An intact but inactive Barn network can be restored by interactive `up`.
For partial or invalid installations, review the cleanup plan for Barn-owned resources. Do not delete host files by hand:

```bash
barn network status --json --verbose
barn network uninstall --json
```

Without `--yes`, JSON output only plans removal. The network plan may still
need sudo to read protected ownership state. Apply the reviewed plan with
`barn network uninstall --yes`. Ordinary terminal output
asks `[y/N]` and can apply removal immediately after confirmation. If the Linux bridge smoke test fails, Barn automatically rolls back the installation. An explicit `automatic rollback failed` message requires manual inspection.

On macOS, a missing or restrictive root-owned `/var/log/barn-vmnet` is
repairable. Read the finding from `network status`: the expected directory is
`root:wheel 0755`. `barn setup` repairs a recognized installation. If repairing manually, follow the exact diagnostic command. A symlink, wrong owner, or
group/world-writable directory is not repaired automatically. Do not diagnose
a route conflict from the bridge name alone.

## Linux bridge helper fails

```bash
id
stat -c '%U:%G %a %n' /usr/lib/qemu/qemu-bridge-helper
dpkg-statoverride --list /usr/lib/qemu/qemu-bridge-helper
```

Debian/Ubuntu uses `root:<caller-accessible-group> 4750`. If a desktop ACL provides `/dev/kvm` access, the caller does not have to belong to `kvm`.

## Plan reports recreate or missing

`recreate` means the node's definition changed. Review it with `barn plan` before running `barn recreate <node>`.
Recreation replaces root and non-persistent data disks, so preserve any needed data first.
On a terminal, type `recreate` to confirm; without a terminal, the command requires `--force`.

`missing` means an existing node is absent from the inventory; Barn has not deleted it.
Restore its inventory entry, or run `barn destroy <node>` to delete it.

## A node did not become ready

Management SSH and guest instance identity are required for readiness. If a node cannot be created, started, or reached, Barn returns a node-level partial result. It reports the node and stage, and exits 5. A command-wide failure, such as a missing host
capability or an inventory conflict, uses its own exit class. Read its logs:

```bash
barn logs <node>                  # serial console
barn logs <node> --source qemu    # QEMU diagnostics
barn logs --source events        # deployment/setup events, even before the first VM
barn status
```

Data disks, shares, hostnames, guest hosts, control-node SSH, and private-network
setup run independently. Failure of one does not prevent management SSH or the
other stages. A usable guest returns 0 with specific limitations. JSON/YAML expose them as `nodes[].warnings`. Internet access is not a readiness requirement.

| Limitation | Next action |
|---|---|
| Data disk unavailable | Correct a missing device, probe, tool, busy mount, or I/O problem, then run `up` |
| Shared directory is read-only | Correct host permissions, then run `up` to retry writes |
| guest hosts or control-node SSH incomplete | Run `up` to refresh the managed files |
| Private interface unavailable | Check `barn network status`, then run `up`; management SSH can still work |

After fixing the underlying issue, repeat `up`. It retries unfinished stages and upgrades old guest helpers in place. It skips healthy stages without restarting running VMs. Barn automatically resets unrecognized or confirmed damaged test data filesystems, **including persistent disks**. The result reports discarded data.
Failed probes, busy mounts, and I/O failures do not trigger formatting. See
[Data disks](../../reference/configuration/#data-disks).

A repeated `up` can also clean recognized leftovers from interrupted preparation.
`--rollback` removes failed prepare artifacts in the same run and lists them in
`rolled_back`. `--no-wait` returns once QEMU is running. It skips readiness, guest recovery, and metadata refresh. A later `up` completes these steps.

## SSH fails

Check `barn status`, `barn ssh-config`, and the serial log.

Startup restores a missing deployment public key from the intact original
private key.
If the private key is missing, restore that same key from backup. Barn refuses to generate a replacement identity for existing VMs. This host-side recovery is separate from a missing guest key in a control node.
`up` also checks the private-key copy installed in the control node.
If that copy is missing, it reports a `control-ssh` limitation; the host-to-guest management connection can still work. Restoring the original
guest key and running `up` clears the limitation. Automatic private-key reinjection into existing guests is not supported.

Barn's own SSH uses a loopback management port. Direct Ansible traffic uses the fixed IP.
If another process occupies a stopped VM's automatically allocated management port, the next start selects a free port. It refreshes the SSH aliases. Running
VM ports stay unchanged. SSH host-key trust is scoped to the VM instance UUID,
so recreating a VM does not require deleting unrelated known-host entries.
A changed key for the same instance still fails verification.

`doctor` excludes fixed IPs reserved by the applied deployment from its generic eligibility scan. `up` and `start` still reject a new or stopped node address that already accepts SSH.

A symlinked or hard-linked `~/.ssh/config` is not rewritten.
Barn publishes its fragment and shows the `Include` line to add through your
dotfile manager. If `ssh meta` fails while `barn ssh meta` works, check that
include before changing guest keys. If the first `ssh`/`exec` argument contains a digit or `-` and resembles a mistyped node name, Barn rejects it with a suggestion. To explicitly separate a node selector from its remote command, use `--`.

## Catalog or image verification fails

The current binary embeds active and standby catalog public keys. Unknown
signers, version rollback/equivocation, artifact size/SHA mismatch, and unsafe
qcow2 structure are distinct integrity failures. Use a correctly signed repository or `barn image import --sha256 ...`. Do not copy bytes directly into `~/.barn/images`.

## A command was killed

First check whether another Barn command is still running. In Barn 0.9.1, `status` reads published state without waiting and reports a
`note` while another command holds the deployment lock. Wait for that command
to finish before treating its in-progress state as an interruption.

When no operation holds the lock, run `barn status`. Barn checks the recorded process identity and updates the VM state if it can determine whether the process is running.
If the identity is uncertain, Barn blocks further operations. Never kill an unknown PID based only on a state file.

Barn 0.9.1 additionally handles these recovery cases:

| Interrupted operation | Recovery |
|---|---|
| Host reboot or recycled QEMU PID | `status` recognizes a provably unrelated PID and marks the old VM stopped; use `start` |
| `stop` while QEMU kept running | `status` restores running state; repeat `stop` if shutdown is still intended |
| First `up` failed during preparation | Correct the inventory and repeat `up -f /path/to/barn.yml`; only journaled unfinished artifacts are rolled back |
| `destroy` stopped midway | Repeat the same explicit destroy scope; interrupted transitions and previously retained persistent disks can be resumed |

If recovery still fails, retain the state and logs. Do not delete node directories or rewrite PIDs to imitate a successful recovery.

If a recorded QEMU process still exists but its QMP socket is absent, preserve the evidence. Inspect serial/QEMU logs before using `stop` to reconcile it.
Do not delete runtime sockets or state files by hand.

The generic error structure uses a stable class in `error`,
with optional `reason`, `next`, and external-program details in `command`.
Some commands return their own diagnostic reports. Read the cause and proposed next step. Do not parse human text as an API. See [Automation](../automation/)
for exit codes and result handling. Event and QEMU logs use readable records. If you need QEMU arguments, add `--verbose`.

For a bug report, include the exact command and exit code, `barn version`, and the three JSON reports above.
Also include the host OS/architecture and QEMU version.
