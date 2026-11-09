---
title: Security and Trust
description: Host privileges, guest credentials, shared folders, and the separate trust boundaries in Barn 1.0.0.
weight: 25
icon: fa-solid fa-shield-halved
---

Barn is designed for trusted local development workstations. All Linux lab nodes share a private subnet, and the control node holds the SSH key needed to administer every peer node in the lab. Barn's ownership and identity checks prevent accidental damage to unrelated host files or processes, rather than isolating mutually untrusted local users.

## Host privileges {#host-privileges}

Always run `barn` as your normal desktop or shell user. QEMU processes, `Barn.app` macOS VMs, image downloads, VM disks, and state files all run under and belong to your user account. Administrator (`sudo`) privileges are used only for three explicit host-level tasks:

| Task | Privileged scope |
|---|---|
| `barn setup` (Linux dependency install) | Runs the distribution package manager (`apt`/`dnf`) to install QEMU, firmware, and OpenSSH (macOS Homebrew runs as your normal user) |
| `barn network install` / `uninstall` | Configures or removes the host-wide fixed-IP network backend (`barn0` bridge on Linux, `socket_vmnet` launchd service on macOS) |
| `barn hosts install` / `uninstall` | Updates only Barn's marker-delimited block in `/etc/hosts` through the dedicated `barn-hosts-helper` binary |
{.wide .expand}

Before prompting for `sudo`, `setup`, `network`, and `hosts` display the exact plan they will execute. On a terminal, `up`, `start`, `restart`, and `reload` can offer to prepare a host that lacks a dependency or an intact Barn network; they run the same `setup` plan with the same single confirmation and never assume `--yes`. Without a terminal they only report what is missing, so run `barn setup --yes` for unattended preparation.

Keep `barn` and `/opt/barn/libexec/barn-hosts-helper` installed from the same release build: the CLI verifies the helper's embedded SHA-256 digest before invoking it, and the helper checks `/etc/hosts` ownership, permissions, link count, and pre/post content digests on every write.

By contrast, `barn mac` creates per-VM user-space `vmnet` networks on demand without any root daemon or privileged network setup (see [Design](../design/) and [Uninstall](../../start/uninstall/)).

## Guest access and SSH trust {#guest-access-and-ssh-trust}

In Linux labs, the default guest account is `dba` with a locked password, passwordless `sudo`, and an Ed25519 deployment SSH keypair generated in `$BARN_HOME`. Barn also installs that private key on the control node so Ansible playbooks and administrative scripts can reach every node in the lab—meaning anyone with shell access to the control node has administrative access to the entire Linux lab.

Barn applies distinct OpenSSH host-key policies across its three connection paths:

| Connection path | Host-key policy |
|---|---|
| Host → Linux guest (via `barn` or `~/.ssh/barn_config`) | `StrictHostKeyChecking accept-new` against a private `known_hosts` file keyed by VM UUID alias (pins on first connection; rejects later mismatches; explicit `recreate` generates a new VM UUID) |
| Linux control node → lab peers | `StrictHostKeyChecking no` with `UserKnownHostsFile /dev/null` for Barn-managed peer aliases so recreated lab nodes remain reachable without manual `known_hosts` edits |
| Host → macOS guest (via `barn mac` or `~/.ssh/barn-mac_config`) | Strict host-key verification against the per-VM `known_hosts` file keyed by `barn-mac-<instance_id>`, with SSH agent forwarding disabled |
{.wide .expand}

Each macOS VM generates its own Ed25519 SSH keypair and random local administrator password (stored in a `0600` `password` file inside the VM slot directory and readable via `barn mac password`). Once guest initialization completes, both Linux and macOS guests enforce SSH public-key authentication, disable SSH password authentication and root SSH login, and grant passwordless `sudo` to the configured admin user. Strip private keys, passwords, and sensitive state before sharing logs or inventories in bug reports.

On first Mac contact, trust comes from the runner-owned private network and runner identity checks before and after the SSH connection; the observed host key is then pinned to the instance UUID. The GUI password shares the SSH key's file-permission boundary: that key already grants guest sudo, so storing only the password in Keychain would add signing and lock-state failures without protecting additional guest authority. See [Native Mac lifecycle](/blog/design/native-mac-lifecycle/#credentials).

## Shared folders and disposable disks {#shared-folders-and-disposable-disks}

- **Host directory shares**: Writable shares (`readonly: false` in Linux `vm_shares` or `:rw` in `barn mac --share`) grant guest processes direct write access to the shared host directory, and changes made inside the shared directory persist after the VM is destroyed. Share dedicated project folders and prefer read-only shares whenever guests do not need to modify host files.
- **Persistent and disposable data disks**: Ordinary Linux `destroy` and `recreate` retain `persistent: true` data disks. During recovery, `up` formats a data disk without any signature and resets an existing ext4 or XFS filesystem, persistent or not, when the checker reports recognized corruption; other probe or checker failures keep the data and report a warning. Keep important data backed up on the host (see [Storage and Access](../../start/storage/)).

## Downloads and image trust {#downloads-and-image-trust}

Barn separates trust verification across four independent mechanisms:

| Mechanism | What it verifies |
|---|---|
| Release `checksums.txt` | Lists the SHA-256 digests of every release asset—CLI archives, `.deb`/`.rpm` packages, SPDX SBOMs, the Homebrew formula, the installer, and release metadata; the installer verifies the selected archive against it |
| macOS release signatures | The Apple Silicon release CLI, helper, and `Barn.app` use Developer ID signatures and Apple notarization; the app carries a stapled ticket. Local source builds default to ad-hoc signing |
| Linux catalog signature (`catalog.json.minisig`) | Verifies with Barn's embedded Ed25519 public keys that `catalog.json` was signed by a trusted key and satisfies per-repository anti-rollback revision rules |
| Image artifact verification | Verifies before use that every downloaded or imported `.qcow2` matches its catalog byte size, SHA-256 digest, virtual capacity, and standalone `qcow2` format rules |
{.wide .expand}

Release assets are built from the exact tag, by the tag workflow when its Mac signing secrets are configured and otherwise by the documented local release path. Source CI must pass on the release commit first. Both paths require package, archive, SBOM, and checksum verification before creating a draft GitHub Release; local publication follows the [Mac release handbook](../mac-release/).

In `1.0.0`, `release.json` records `signed:false, attested:false` for the general release envelope. The Git tag and general checksums/release metadata have no separate cryptographic signature or attestation. Catalog Minisign verification and Apple Silicon code signing/notarization retain the distinct scopes listed above; the [final acceptance record](../history/#release-1-0-0) verifies them separately.

The two official image repositories (`https://repo.pigsty.io/barn` and `https://repo.pigsty.cc/barn`) always require valid minisign catalog signatures, even when passed explicitly via `--repo`. Custom HTTPS or local directory repositories may use unsigned catalogs when explicitly selected with `--repo` or `BARN_REPO` (see [Linux Images](../../reference/images/)).

## Report a vulnerability {#report-a-vulnerability}

Report security vulnerabilities privately via [GitHub Security Advisories](https://github.com/pgsty/barn/security/advisories/new) or by emailing [repo@pigsty.cc](mailto:repo@pigsty.cc) with `barn --json version`, your host OS and architecture, and a minimal reproduction with credentials removed. Security fixes land in the latest 1.x patch release; only the latest 1.x release is supported, and 0.x releases receive no further fixes. See [`SECURITY.md`](https://github.com/pgsty/barn/blob/main/SECURITY.md) for the full policy, and use [GitHub Issues](https://github.com/pgsty/barn/issues) for ordinary bug reports.
