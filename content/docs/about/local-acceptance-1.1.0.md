---
title: Barn 1.1.0 Local Acceptance
linkTitle: 1.1.0 Local Acceptance
description: Upgrade an Apple Silicon host in place, rebuild Linux and macOS labs, and record reviewable acceptance runs.
date: 2026-11-09
weight: 46
icon: fa-solid fa-vial
---

This run starts with the installed Barn 1.0.0, installs the public 1.1.0 Homebrew formula, checks upgrade and everyday workflows, then rebuilds the test environment. **The script was written before execution. This run has ended: core checks passed, one recovery gap was found, and clipboard/privileged-host checks remain incomplete.** The owner authorized deletion of existing local Barn VMs.

## Environment and evidence {#environment}

- Host: macOS 27.0.1, Apple Silicon, 18 logical CPUs, 128 GiB RAM; QEMU 11.1.3.
- Initial state: eight running Linux VMs and one running macOS VM named `mac1`; the normal executable is `/opt/homebrew/bin/barn`.
- Upgrade target: public tag `v1.1.0`, commit `b2cc8da8983e710255d504bf26bf5d7b3f182790`.
- Recordings, raw output, assertions, and executable scripts live in a separate acceptance directory outside Git. Each stage produces an asciicast v2 recording with original timing and a viewing copy with shortened waits.
- Linux checks use the actual user's `~/.barn`. Detailed native Mac checks reuse `tests/mac-live-acceptance.py` with a dedicated test root and an APFS clone of the prepared base; final checks cover the normal user path.
- Terminal recordings capture output without keyboard input, passwords, or private SSH keys. Desktop checks use native application controls; the screenshot is in the acceptance chat. Clipboard status is recorded below.

## Execution order {#sequence}

| Stage | Operations | Pass condition |
|---|---|---|
| U01 Upgrade baseline | Record the old version, node identities, public SSH fingerprints, and data sentinels; stop Linux and Mac VMs | Reviewable baseline; every target stops cleanly |
| U02 Local installation | `brew upgrade pgsty/infra/barn`; check version, helper, signatures, notarization, and `brew test` | Normal PATH resolves to public 1.1.0; CLI, helper, and App match |
| U03 Upgrade recovery | Start existing VMs and compare identities, data, and SSH; then remove old VMs | Upgrade preserves identities and data; explicit disposal succeeds |
| L01 First run | Run `barn up` from an empty directory; check generated inventory, confirmation, progress, and SSH | Default native Ubuntu 24.04 guest becomes ready |
| L02 Inventory and catalog | Four templates; valid/invalid YAML; `-I/-A` and aliases; both signed official repositories; metadata and cache | Valid input resolves consistently; failures have correct classification and exit codes; overrides leave inventory unchanged |
| L03 Two nodes and storage | Ubuntu/Debian pair; persistent ext4, temporary data, XFS, space/Unicode paths, read-only and writable 9p shares | Filesystem types, permissions, and bidirectional reads/writes match the inventory |
| L04 Network and access | Fixed IPs, control-node SSH to its peer, DNS/HTTPS, SSH config, exec argument boundaries and remote exit codes | Correct addresses, targets, output streams, and exits |
| L05 Lifecycle | Repeated up, selected stop/start/restart, CPU/memory increase/decrease, reload, selected recreation | Idempotent calls retain PIDs; resources change in the guest; peers and persistent data remain intact |
| L06 Failures and deletion | Omitted nodes, missing share paths, interrupted guest process recovery, provision success/failure/timeout, purge cancellation | No implicit deletion; actionable failures; retries recover; cancellation preserves state |
| L07 Retention | Recreate, selected and whole destroy, create again, purge | Root/temporary data resets; persistent data follows each command's retention rules |
| L08 Image matrix | Eight supported arm64 image families and Debian amd64 under TCG | SSH, architecture, OS identity, and data disk work; el8 arm64 uses expected TCG |
| M01 Multiple Macs and identity | Automated two-VM checks, independent identities and disks, immutable shared base | Identities differ; cloning and lifecycle operations preserve the base |
| M02 Mac networks and shares | Separate subnets, host access, guest isolation, DNS/HTTPS, VirtioFS, remote arguments | Network and sharing behavior matches the reference |
| M03 Mac lifecycle | Stop/start, resource configuration, third-running-VM limit, recreate identity rotation, selected destruction | Identity retention/rotation matches the operation; the peer remains intact |
| M04 Desktop and clipboard | Open desktop, verify login, copy text both ways, close the window, check SSH | Usable desktop; exact text transfer; window closure keeps the VM running |
| F01 Final state | Remove dedicated test VMs; check normal installation, state, diagnostics, and SSH config; index recordings | No leftover test processes; every result has output or visual evidence |
{.wide .expand}

## Assertions and retries {#criteria}

Every command records arguments, exit status, duration, and raw output. Failed assertions preserve the environment. Script corrections create separate retry records; product defects are recorded independently. Failed footage remains available. Only viewing copies shorten waits.

The existing host network is checked and reused first. Operations requiring host sudo inspect actual authorization and the execution plan; unavailable checks are marked blocked. Apple OS image updates, physical Intel Macs, and Linux KVM are separate environment coverage.

## Results and playback {#results}

This run ended at 11:08 on 2026-11-09 (Asia/Shanghai). The normal PATH resolves to public Barn 1.1.0. Upgrade recovery passed for the original eight Linux VMs and one Mac VM before their authorized deletion. All test VMs, the dedicated Mac data root, and the additional 120 GiB base were removed; the original default macOS base remains.

### Stage results {#stage-results}

| Area | Result and evidence |
|---|---|
| Homebrew installation and upgrade | Passed; matching CLI/native components, signatures, notarization, and `brew test`; existing VM identities and persistent-path data survived |
| CLI, inventory, and catalogs | Passed; first run, four templates, architecture aliases, invalid inputs, both signed official sources, local catalog build/verification/import/pruning |
| Linux pair and lifecycle | Passed; fixed IPs, control-node SSH, DNS/HTTPS, arguments/exits, ext4/XFS, read-only/writable 9p, resource changes, recreation, persistent disk reattachment |
| Failures and recovery | Missing shares, provision failure/timeout, cancelled purge, and process interruption after disk sync passed; immediate power-loss readiness issue below |
| Native Mac automated suite | All 15 phases passed; separate identities/disks/networks, unchanged base, resource settings, running-VM limit, recreation, selected destruction |
| Normal Mac data path | Passed; complete installation of a new 120 GiB base from the existing IPSW, read-only/writable VirtioFS, SSH Include, original default base retention, extra-cache pruning |
| Interactive terminals | Linux and Mac passed; real guest TTY allocation and interactive shell exit `17` propagated; all three Linux log sources parsed as JSON |
| Desktop | Logged-in Finder desktop visually confirmed; closing the window kept the same VM process and SSH available; bidirectional clipboard remains unverified |
| Source checks | `make check` and `make mac-native-test` passed on the release commit |
| Final state | Zero Linux or Mac VMs and no remaining test VM processes; `barn doctor`, `barn mac doctor`, and network status healthy |
{.wide .expand}

Deleting the control node promotes a remaining node. After updating `admin_ip` in the inventory as instructed, creating the former node again reattached its retained disk and preserved the peer's PID and data. With the old inventory requesting a control-role reversal, `up` correctly refused implicit recreation.

### Image matrix {#image-results}

All nine configurations passed image acquisition, boot, SSH, OS/architecture checks, data writes, stop/start, and cleanup. `-I/-A` left the inventory file unchanged. EL7/arm64 returned `usage / 2` because the catalog has no matching artifact. EL7/amd64 on this host returned `capability / 3` without creating a deployment.

| Image | Guest architecture | Accelerator | Result |
|---|---|---|---|
| `u22@20261020.0.1` | `arm64` | `hvf` | Passed |
| `u24@20261017.0.1` | `arm64` | `hvf` | Passed |
| `u26@20261016.0.1` | `arm64` | `hvf` | Passed |
| `d12@20261026.2643.1` | `arm64` | `hvf` | Passed |
| `d13@20261103.2651.1` | `arm64` | `hvf` | Passed |
| `el8@8.10.20240528.3` | `arm64` | `tcg,thread=multi` | Passed |
| `el9@9.8.20260525.2` | `arm64` | `hvf` | Passed |
| `el10@10.2.20260525.0` | `arm64` | `hvf` | Passed |
| `d13@20261103.2651.1` | `amd64` | `tcg,thread=single` | Passed |
{.wide .expand}

### Readiness marker after forced termination {#recovery-gap}

Immediately after successful recreation of an Ubuntu 24.04 arm64/HVF node, its verified QEMU process was forcibly terminated. The next `up` booted the guest, but both `/var/lib/barn/ready.json` and `error.json` were absent. SSH and persistent data worked and cloud-init had finished; `up` timed out after 180 seconds with exit `5`. This observed recovery gap is preserved in `03-linux-lifecycle-r3` and `03-power-loss-investigation`.

The following recovery restored readiness while preserving the running VM PID, its peer, and persistent data:

```bash
barn exec meta -- sudo -n /usr/local/libexec/barn-finalize
barn up meta -f barn.yml
```

In a second trial, the guest ran `sudo sync` before the process was terminated, again after checking its command line and QMP UUID. `up` recovered automatically. The immediate-interruption behavior was observed once under the stated conditions; persistence timing and other images need further investigation. Relevant 1.1.0 code is the [readiness probe](https://github.com/pgsty/barn/blob/v1.1.0/internal/vm/lifecycle.go#L584) and [guest-setup retry entry](https://github.com/pgsty/barn/blob/v1.1.0/internal/private/start.go#L162).

### Checks not completed {#limits}

- Bidirectional clipboard: native UI automation did not reliably inject the host system clipboard, and the browser tool has an isolated clipboard. Manual host input had not arrived when this run ended, so this remains unverified.
- Privileged host changes: `sudo -n` required a password, including access to root-owned network planning state. Existing network reuse, privilege-error classification, and read-only hosts plans were checked; network reinstall/uninstall and `/etc/hosts` writes were not executed.
- This host is Apple Silicon. Physical Intel Macs, Linux/KVM, and Apple OS image updates remain separate environment coverage.

### Local evidence {#playback}

Evidence lives at `~/barn-acceptance/1.1.0-20261109-101029/`. Open `player/index.html` for offline playback of 23 asciicasts: approximately 58.9 minutes of original timing or 12.1 minutes in the viewing copies. Viewing copies change timestamps only; output bytes and SHA-256 are checked per recording. Terminal recordings do not contain desktop frames; the desktop screenshot is in the acceptance chat.

`evidence/plan-before-execution.md` and `.zh.md` preserve the original plan. Stage directories contain script snapshots, commands, exit codes, and raw output; `findings.json` records the recovery gap and incomplete checks. Initial footage and retries remain for script corrections involving Homebrew prompts, SSH aliases, create/recreate plan categories, control-role promotion, TCG parameters, and error classification. Full recordings stay local; this site contains the acceptance account.
