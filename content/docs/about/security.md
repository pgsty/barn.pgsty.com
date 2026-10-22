---
title: Security and Trust
description: Host privileges, guest credentials, shared folders, and the separate trust boundaries in Barn 0.9.1.
weight: 25
icon: fa-solid fa-shield-halved
---

Barn is intended for trusted local development. All Linux nodes share a private
network, and the control node can administer the other nodes. Ownership checks
prevent accidental changes to unrelated resources, but do not isolate untrusted users.

## Host privileges

Run `barn` as your ordinary user. QEMU and image downloads run under that
account. VM disks and state belong to the same account. Only these host tasks
require administrator access:

| Task | What changes |
| --- | --- |
| `setup` installs missing Linux dependencies | The distribution package manager installs QEMU, firmware, and OpenSSH; macOS Homebrew runs as your user |
| `network install` / `uninstall` | The host-wide fixed-IP backend and its recorded configuration |
| `hosts install` / `uninstall` | Only Barn's marker-delimited block in the system hosts file, through a separate helper |

Setup shows the required changes before asking for privileges. Install the CLI
and `barn-hosts-helper` from the same build. The helper under `/opt/barn/libexec/`
must match the digest embedded in the packaged CLI. For each write, the helper checks
file ownership, permissions, link count, and the expected contents before and after the change.

The native `barn mac` workflow uses a separate network for each machine.
It adds no root daemon or privileged network transaction. See [design](../design/) and
[uninstall](../../start/uninstall/) for resource lifetimes.

## Guest access and SSH trust

The Linux guest account defaults to `dba` with passwordless sudo. Its password
is locked, and Barn supplies a deployment SSH key. The control node also
receives that private key to run Ansible and administer the other nodes.
Access to the control node therefore gives administrative access to the entire Linux lab.

These SSH connections have different trust policies:

| Connection | Host-key policy |
| --- | --- |
| Host → Linux guest through Barn | `accept-new`, with a private known-hosts file and VM UUID alias; first use accepts a key, later mismatches fail |
| Linux control node → lab peers | The generated peer configuration uses `StrictHostKeyChecking no` and `/dev/null` for known hosts, to support routine lab recreation |
| Host → initialized macOS guest through Barn | A per-machine pinned host key with strict checking; agent forwarding is disabled |

The control node skips host-key checks when it uses the generated SSH configuration
to connect to other nodes. Use this configuration only in a trusted lab network.
An explicit recreate establishes a new VM identity,
even if the port number or fixed IP stays the same.

Each Mac machine has its own SSH key and random desktop password. Barn stores
the password in a mode-0600 file in the machine directory, not in Keychain.
Use `barn mac password` to display it.

After initial SSH setup, the guest uses key authentication. It disables SSH
password authentication and SSH login as root. The configured user has passwordless
sudo access. Do not copy state or command output with credentials into an
issue or shared repository.

## Shared files and disposable disks

Writable shares give guest processes access to the selected host directory.
Use a dedicated directory. If the guest does not need to write files, select
read-only access. The shared host folder and any changes made by the guest remain after VM removal.

Barn retains persistent Linux data disks during ordinary destroy/recreate.
However, guest recovery can format a filesystem that it cannot recognize or
confirms as damaged. Back up important data outside the lab. See
[storage](../../start/storage/) for deletion and recovery rules.

## Downloads and image trust

| Mechanism | What it checks |
| --- | --- |
| Application `checksums.txt` | Downloaded archives and packages match the release's published hashes |
| Native app code signature and notarization | A separate macOS distribution process; 0.9.1 does not distribute the native app; local source builds use ad-hoc signing by default |
| Signed Linux image catalog | Metadata was signed by an accepted catalog key and satisfies revision rules |
| Image download validation | Size, SHA-256, qcow2 structure, and virtual size match the accepted metadata |

Application checksums are not an independent release signature. A trusted
catalog also does not authenticate the Barn executable. The two official
image repositories require signatures, including when explicitly selected
with `--repo`. A custom HTTPS or local repository may accept unsigned
metadata. Use such a repository only if you trust its source. See
[image verification](../../reference/images/) for revision and cache rules.

## Report a vulnerability

Use [GitHub private vulnerability reporting](https://github.com/pgsty/barn/security/advisories/new)
or email [repo@pigsty.cc](mailto:repo@pigsty.cc). Include `barn --json version`,
the host platform, and a minimal reproduction with credentials removed.
The [security policy](https://github.com/pgsty/barn/blob/main/SECURITY.md)
describes support and disclosure. Report ordinary usage bugs in
[Issues](https://github.com/pgsty/barn/issues).
