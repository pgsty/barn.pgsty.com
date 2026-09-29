---
title: Troubleshooting
description: Short, safe runbooks for setup, networking, images, drift, interrupted state, and SSH.
weight: 30
icon: fa-solid fa-life-ring
---

This page covers public 0.8.0 behavior and explicitly marked **0.9 candidate**
changes from the unreleased source tree reviewed on 2026-09-26. Check
`farrow version` before applying version-specific guidance.

Start with diagnostics (`status` may reconcile interrupted runtime state):

```bash
farrow doctor --json
farrow network status --json
farrow status --json
```

## Download and PATH problems

The installer uses GitHub Release assets; `--mirror` selects the Farrow image
repository and does not redirect installer downloads. If your network needs a
proxy, set `HTTPS_PROXY` or `ALL_PROXY` in the terminal to your existing proxy's
address. A macOS system proxy setting alone does not configure these environment
variables for command-line tools.

The user-scoped installer defaults to `~/.local/bin`. If `farrow` is missing or
reports an older version after installation, check which executable is selected:

```bash
export PATH="$HOME/.local/bin:$PATH"
command -v farrow
farrow version
```

For Homebrew or native packages, use that channel's executable instead. Keep the
CLI and its packaged `farrow-hosts-helper` from the same release together.

## No inventory found

Interactive `up` can create the first default inventory when no deployment
exists. For an explicit configuration, run `plan`, `up`, or `validate` beside
`farrow.yml`/`pigsty.yml`, pass `-f /path/to/file`, or run `farrow init` to
write one. Once state exists, `plan`, `up`, `reload`, and `recreate` can fall
back to its applied spec. Status, start, stop, SSH, and destroy always use
applied state. If `status` reports `no deployment state found`, the selected
`FARROW_HOME` has no applied deployment; it may be fresh or previously purged.

## Setup needs sudo

The line before the prompt names the exact host mutation. Farrow attaches an
interactive terminal directly to sudo when the privileged step begins.
`--yes` accepts the setup plan; it does not bypass sudo authentication.
Automation needs an existing credential or a suitable NOPASSWD policy. Use
`farrow setup --dry-run` to inspect the plan first.

On macOS, setup prepares the pinned socket_vmnet source before requesting
administrator authentication. A download failure therefore does not require a
password. **0.9 candidate:** the setup plan spells out sudo use and the
socket_vmnet source; if an automatically selected subnet changes after the
first confirmation, setup asks again unless `--yes` was supplied.

## Native acceleration or compatibility runtime is unavailable

Native paths require HVF on macOS or KVM on Linux. TCG is selected only for an
explicit foreign `vm_arch` or a built-in image/host compatibility rule; an
arbitrary native failure never falls back. Homebrew QEMU contains both system
emulators. Linux setup installs only the native family, so a foreign Guest also
requires its matching `qemu-system-*` binary and firmware.

`plan` resolves Catalog-backed images and their intended runtime without QEMU
installed; imported `local-*` images still need `qemu-img` and a valid cache.
`up` and `recreate`
check the selected emulator and firmware before changing VM resources.
Performance results from TCG are not meaningful.

## Network is partial or invalid

An intact but inactive Farrow network can be restored by interactive `up`.
For partial or invalid installations, do not delete host files by hand; review
the owned cleanup plan:

```bash
farrow network status --json --verbose
farrow network uninstall --json
```

Without `--yes`, JSON output only plans removal. The network plan may still
need sudo to read protected ownership state. Apply the reviewed plan with
`farrow network uninstall --yes`. **0.9 candidate:** ordinary terminal output
asks `[y/N]` and can apply removal immediately after confirmation; in 0.8.0
plain `network uninstall` only displays the plan. A failed Linux
bridge smoke test rolls the install back automatically; an explicit
`automatic rollback failed` message means manual inspection is required.

On macOS, a missing or restrictive root-owned `/var/log/farrow-vmnet` is
repairable. Read the finding from `network status`: the expected directory is
`root:wheel 0755`. `farrow setup` repairs a recognized installation; follow the
exact diagnostic command if repairing manually. A symlink, wrong owner, or
group/world-writable directory is not repaired automatically. Do not diagnose
a route conflict from the bridge name alone.

## Linux bridge helper fails

```bash
id
stat -c '%U:%G %a %n' /usr/lib/qemu/qemu-bridge-helper
dpkg-statoverride --list /usr/lib/qemu/qemu-bridge-helper
```

Debian/Ubuntu uses `root:<caller-accessible-group> 4750`; the caller does not
have to belong to `kvm` when `/dev/kvm` access comes from a desktop ACL.

## Plan reports recreate or missing

`recreate` means the node's definition changed: review it with `farrow plan`,
then run `farrow recreate <node>`. On a terminal the command asks you to type
`recreate`; without a terminal it requires `--force`. `missing` is only a report: restore the
host entry or run `farrow destroy <node>`.

## A node did not become ready

Management SSH and guest instance identity are required for readiness. If a node
cannot be created, started, or reached, a node-level partial result reports
the node and stage and exits 5. A command-wide failure, such as a missing host
capability or an inventory conflict, uses its own exit class. Read its logs:

```bash
farrow logs <node>                  # serial console
farrow logs <node> --source qemu    # QEMU diagnostics
farrow logs --source events        # deployment/setup events, even before the first VM
farrow status
```

Data disks, shares, hostnames, guest hosts, control-node SSH, and private-network
setup run independently. Failure of one does not prevent management SSH or the
other stages. A usable guest returns 0 with specific limitations; JSON/YAML
expose them as `nodes[].warnings`. Internet access is not a readiness requirement.

| Limitation | Next action |
|---|---|
| Data disk unavailable | Correct a missing device, probe, tool, busy mount, or I/O problem, then run `up` |
| Shared directory is read-only | Correct host permissions, then run `up` to retry writes |
| Guest hosts or control-node SSH incomplete | Run `up` to refresh the managed files |
| Private interface unavailable | Check `farrow network status`, then run `up`; management SSH can still work |

Repeat `up` after fixing the underlying issue. It retries unfinished stages,
upgrades old guest helpers in place, and skips healthy work without restarting
running VMs. Unrecognized or confirmed damaged test data filesystems are reset
automatically, **including persistent disks**; the result reports discarded data.
Failed probes, busy mounts, and I/O failures do not trigger formatting. See
[Data disks](../../reference/configuration/#data-disks).

After an interrupted 0.6.0 bootstrap, the staged control-node SSH key may already
be missing. In that case `up` restores management access but cannot reinject
the key in place. If peer SSH is required, review `farrow plan` and recreate
the affected control node; see the [0.7.0 upgrade notes](../../../blog/release/farrow-0.7.0/).

A repeated `up` can also clean recognized leftovers from interrupted preparation.
`--rollback` removes failed prepare artifacts in the same run and lists them in
`rolled_back`. `--no-wait` returns once QEMU is running and skips readiness,
guest recovery, and metadata refresh; a later `up` completes them.

## SSH fails

In Farrow 0.8, startup restores a missing deployment public
key from the intact original private key. It also covers VMs created with 0.7.0.
If the private key is missing, restore that same key from backup; Farrow refuses
to generate a replacement identity for existing VMs. This host-side recovery is
separate from the old control node's missing guest key described above.
`up` now checks that installed guest key as well: a missing copy is a
`control-ssh` limitation, not a management SSH failure. Restoring the original
guest key and running `up` clears the limitation. Automatic private-key
reinjection into old guests remains pending.

Check `farrow status`, `farrow ssh-config`, and the serial log. Farrow's own
SSH uses a loopback management port; direct Ansible traffic uses the fixed IP.
If another process occupies a stopped VM's automatically allocated management
port, the next start selects a free port and refreshes its SSH aliases. Running
VM ports stay unchanged. SSH host-key trust is scoped to the VM instance UUID,
so recreating a VM does not require deleting unrelated known-host entries.
A changed key for the same instance still fails verification.

`doctor` excludes fixed IPs reserved by the applied deployment from its generic
eligibility scan; `up` and `start` still reject a new or stopped node address
that already accepts SSH.

**0.9 candidate:** a symlinked or hard-linked `~/.ssh/config` is not rewritten.
Farrow publishes its fragment and shows the `Include` line to add through your
dotfile manager. If `ssh meta` fails while `farrow ssh meta` works, check that
include before changing guest keys. Near-miss node names in `ssh`/`exec` are rejected with a suggestion when they
contain a digit or `-` and match the typo heuristic; use `--` when
explicitly separating a node selector from its remote command.

## Catalog or image verification fails

The current binary embeds active and standby Catalog public keys. Unknown
signers, version rollback/equivocation, artifact size/SHA mismatch, and unsafe
qcow2 structure are distinct integrity failures. Use a correctly signed
repository or `farrow image import --sha256 ...`; do not copy bytes directly
into `~/.farrow/images`.

## A command was killed

First check whether another Farrow command is still running. In the **0.9
candidate**, `status` reads published state without waiting and reports a
`note` while another command holds the deployment lock. Wait for that command
to finish before treating its in-progress state as an interruption.

When no operation holds the lock, run `farrow status`. A provably live or dead
runtime is reconciled using its recorded identity; an ambiguous process remains
blocked. Never kill an unknown PID based only on a state file.

The **0.9 candidate** additionally handles these recovery cases:

| Interrupted operation | Recovery |
|---|---|
| Host reboot or recycled QEMU PID | `status` recognizes a provably unrelated PID and marks the old VM stopped; use `start` |
| `stop` while QEMU kept running | `status` restores running state; repeat `stop` if shutdown is still intended |
| First `up` failed during preparation | Correct the inventory and repeat `up -f /path/to/farrow.yml`; only journaled unfinished artifacts are rolled back |
| `destroy` stopped midway | Repeat the same explicit destroy scope; interrupted transitions and previously retained persistent disks can be resumed |

These fixes are not all present in 0.8.0. If that release blocks on a case above,
retain the state and logs; do not delete node directories or rewrite PIDs to
imitate the candidate's recovery.

If a recorded QEMU process still exists but its QMP socket is absent, preserve
the evidence and inspect serial/QEMU logs before using `stop` to converge it.
Do not delete runtime sockets or state files by hand.

**0.9 candidate:** the generic error envelope uses a stable class in `error`,
with optional `reason`, `next`, and external-program details in `command`.
Some commands return their own diagnostic reports. Read the cause and proposed
next step; do not parse human text as an API. See [Automation](../automation/)
for exit codes and result handling. Event and QEMU logs use readable records;
`--verbose` adds QEMU arguments when those are needed.

For a bug report include the exact command and exit code, `farrow version`,
the three JSON reports above, host OS/architecture, and QEMU version.
