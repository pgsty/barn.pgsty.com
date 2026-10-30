---
title: Validation History
description: Original Barn release validation, native VM tests, image checks, and design history.
weight: 40
icon: fa-solid fa-clock-rotate-left
---

> [!NOTE]
> This page archives the pre-0.9.0 validation baseline (documentation commit `4c03fc9`, 2026-09-29) alongside dated verification records for earlier releases (`0.1.0` through `0.8.0`). For current host support and release notes, see [Platforms and Limits](../status/) and the [Barn 0.9.2 Release Notes](/blog/release/0.9.2/).

At the 2026-09-29 checkpoint, Barn `0.9.0` was the first release candidate prepared under the `barn` name prior to publication. For current installation commands, use the [Quick Start](../../start/installation/).

## Documentation baseline {#documentation-baseline}

| Component | Identity at the 2026-09-29 checkpoint | Scope notes |
|---|---|---|
| Application and docs | Barn `0.9.0` release candidate | Built from the renamed source tree prior to public tag release |
| CLI and configuration | `barn`, `barn.yml`, `BARN_*` | Clean break from earlier internal names |
| State and host resources | `~/.barn`, Barn networking, and `barn-hosts-helper` | Uses fresh `~/.barn` state without migrating pre-rename development directories |
| Image repository | `/barn` on the official endpoints | Requires valid minisign catalog signatures |
{.wide}

## macOS guests {#macos-guests}

At the 2026-09-29 checkpoint, `barn mac` ran macOS 27 guests on Apple Silicon via `Barn Mac.app` (`io.pgsty.barn.mac-runner`; subsequently renamed to `Barn.app` / `com.pgsty.barn` in [Barn 0.9.1](/blog/release/0.9.1/)) with state under `$BARN_HOME/mac` (see the current [macOS Guests guide](../../start/macos/) and [Mac Commands reference](../../reference/mac/)).

Following the rename on 2026-09-29, local CLI and `barn-hosts-helper` unit suites, native bridge/image/exit-prompt/menu tests, the runner bundle build, ad-hoc code-signature verification, and `probe` checks all passed, building on the full 16-phase live macOS VM acceptance run recorded earlier that day.

## Remaining pre-0.9.0 release checks

At the 2026-09-29 checkpoint, the remaining pre-publication gates for `0.9.0` were:

- Full source, archive, DEB/RPM, installer, and four-platform checks on the final tagged commit.
- Fresh host setup and Linux/macOS VM lifecycle and cleanup verification under the renamed binary and paths.
- macOS Developer ID signing, notarization, and release publication.
- Verification of the public GitHub repository, Homebrew tap, official `/barn` image endpoints, and `barn.pgsty.com`.

## Barn Mac native record: 2026-09-29

On 2026-09-29, the pre-rename development tree was validated on an Apple Silicon Mac running macOS `27.0` (`26A428`) using an ad-hoc signed development build and APFS clones of a base image prepared on 2026-09-26 from Apple's pinned `27.0` restore image:

- **Source and bundle checks**: Full `make check`, native Swift component tests, and the Mac bundle build with extracted-archive checksum, signature, and `probe` checks passed.
- **Automated 16-phase live acceptance (244.9 s)**: Verified VM creation from the base image, named VM creation with a VirtioFS shared folder, independent machine identities, `sshd` hardening, disk and per-VM subnet isolation, DNS, outbound HTTPS, exit-code propagation, `exec` argument boundaries, bidirectional shared-folder writes, clean `stop`/`start`, `configure`, enforcement of the two-VM running limit, `recreate` identity rotation, desktop window display, two-way plain-text clipboard sync, idempotent `up`, and `destroy`.
- **Manual timing and recovery checks**: First boot from a prepared base image reached SSH readiness in `22 s`; clean shutdown completed in `6.5 s`; subsequent starts reached SSH readiness in `6–12 s`; forced power-off completed in `0.7 s`. Also verified booting into macOS Recovery (`--recovery`), changing `--subnet` while preserving the pinned SSH host key, and connecting via `ssh mac1` through installed `~/.ssh/barn-mac_config` entries.

Items deferred to subsequent release milestones at that checkpoint:

- Developer ID signing, Apple notarization, and public distribution of the app bundle.
- End-to-end IPSW download + base preparation via first-time `barn mac up` or `barn mac image update`.
- Desktop menu **Restart…** and **Shut Down…** actions, additional Apple Silicon models, and host reboot persistence.

## Pre-rename Linux validation summary {#summary}

| Host or artifact | Path | Last verified | Result |
|---|---|---|---|
| Two Linux `amd64` hosts (`m0`, `m3`) | KVM, 7 guest distributions per host | 2026-09-21 (`0.8.0`) | Clean initialization, first SSH, in-place candidate upgrade, repeated `up`, `stop`/`start`, disk identity, and Ansible inventory reads passed |
| Two macOS `arm64` hosts (`m1`, `m5`) | HVF, 7 guest distributions per host | 2026-09-21 (`0.8.0`) | Full 7-distro lifecycle checks plus 7-node `ansible all -m ping` passed |
| Catalog `2026092001` | 9 families, 37 artifacts (September Debian/Ubuntu refresh) | 2026-09-21 | Embedded, local, LAN, and public catalog bytes matched (`23e8dbf6...`); 10 new image objects verified at both public endpoints and booted across the 4 hosts |
| Ubuntu 26.04 `amd64` | KVM, QEMU `10.2.1`, Ubuntu 24.04 guest | 2026-09-16 (`0.7.0` recovery) | Corrupt data-disk reset, failed probes, busy mounts, retained-disk recreation, share recovery, and idempotent `up` passed |
| macOS `arm64` | HVF, Ubuntu 24.04.4 guests | 2026-09-05 (`0.6.0` lifecycle) | Create, scale-out, control-to-peer SSH, `stop`/`start`, `reload`, `recreate`, degraded `status`, and scale-in passed |
| macOS 26.6.2 `arm64` | HVF, QEMU `11.1`, `socket_vmnet` | 2026-09-01 (`v0.2.0`) | Selected node create/SSH/stop/start, incremental cached create, full `status`, and full `destroy` passed |
| macOS 26.6.2 `arm64` | HVF, QEMU `11.1`, `socket_vmnet` | 2026-08-27 | Single-node and additive four-node lifecycle passed |
| Ubuntu 26.04 `amd64` (`mx`) | KVM, QEMU `10.2.1`, NetworkManager | 2026-09-01 (`v0.2.0`) | Audited a live four-node deployment and connected to its control guest |
| Ubuntu 26.04 `amd64` (`mx`) | KVM, QEMU `10.2.1`, NetworkManager | 2026-08-27 | Host `setup`, single-node, additive four-node, and network `uninstall` passed |
| macOS `arm64` | HVF host, TCG rule for Rocky Linux 8.10 `arm64` | 2026-08-28 | Boot, `stop`/`start`, and SSH readiness in `44.2 s` passed |
| Published Catalog `2026090501` | 9 families, 27 `qcow2` artifacts | 2026-09-05 | Artifact verification, embedded/public byte equality, and signed `barn update` against both official endpoints passed |
| Published Catalog `2026082903` | 9 families, 27 signed `qcow2` artifacts | 2026-08-29 | Full 19 GiB SHA-256 sweep and clean-client `d13:stable` pull passed |
{.wide}

In the `0.8.0` four-host acceptance run, each host booted Rocky Linux 9.8 and 10.2, Debian 12.15 and 13.7, and Ubuntu 22.04.5, 24.04.5, and 26.04.1 (28 guest VMs total, all passing and cleaned up afterward). Both official endpoints served catalog `2026092001` with SHA-256 `23e8dbf6c19bd192d56c6d71eb30901f17945b3487e427a43abe108463780306`, verified via isolated `barn update` runs and HTTP `HEAD` content-length checks on the 10 new image objects.

## Open test items at the earlier checkpoint

- Rocky/EL9 hosts with NetworkManager + `firewalld`, and a fresh `systemd-networkd` host replay.
- Physical host reboot persistence across active deployments.
- Live hypervisor runs on `darwin/amd64` and `linux/arm64` hosts beyond cross-build and package verification.
- End-to-end `el7` VM lifecycle replay on native `linux/amd64`.
- Full Pigsty `configure → barn up → install.yml` playbook execution.
- Fresh-host `setup` and VM creation driven end-to-end from the public download installer, Homebrew formula, or published DEB/RPM packages.

## Barn verification history

### Barn 0.8.0 — 2026-09-21

- **Release CI and assets**: Tag `v0.8.0` (`320a32afa8f6fca02592215aa0d5607ca4e852b2`) passed [source CI](https://github.com/pgsty/barn/actions/runs/35568664994), the [packaging snapshot workflow](https://github.com/pgsty/barn/actions/runs/35568664948), and the [release tag workflow](https://github.com/pgsty/barn/actions/runs/35569143101), publishing 20 release assets (19 checksummed payloads). All 20 assets were downloaded anonymously and verified against the release `checksums.txt` manifest, and isolated user-prefix installs on `darwin/arm64` and `linux/amd64` verified `0.8.0` (`320a32a`).
- **Homebrew tap**: Commit [`9c34019`](https://github.com/pgsty/homebrew-infra/commit/9c3401958a435248ebf0e5402e7efff712ee1c4c) updated `pgsty/infra/barn` to `0.8.0` across all four targets and passed local `brew fetch`, audit, and [tap CI](https://github.com/pgsty/homebrew-infra/actions/runs/35570285428).
- **Four-host 7-distro acceptance**: Clean initialization was run at baseline commit `6d7870e26cb2f4082a00c188f746783fc027687e` across two Linux `amd64` hosts (`m0`, `m3`, installed from the `.deb` package) and two macOS `arm64` hosts (`m1`, `m5`, installed from the verified archive), booting the 7-distro `pro` inventory from a local LAN repository. Runtime candidate `1c054a027420b5410c6f6feb344e27e001ae1af1` (adding the macOS Homebrew authentication-order fix) was then installed in place on all four hosts and verified across idempotent `up` (preserving running QEMU processes, VM UUIDs, and disk inodes), two rounds of guest SSH, `stop`/`start`, `/data` disk mounts, Debian locale/XFS checks, control-to-peer SSH, and Ansible inventory reads (`ansible all -m ping` on both Macs). See the [0.8.0 Release Notes](/blog/release/0.8.0/) for per-host timings.

### Barn 0.7.0 release — 2026-09-16

- **Release CI and assets**: Commit `9c6d4896d93733d1cb60a7e5d8591e9a06659c9d` (`v0.7.0`) passed [source CI](https://github.com/pgsty/barn/actions/runs/35118137961), the [packaging snapshot workflow](https://github.com/pgsty/barn/actions/runs/35118137990), and the [release tag workflow](https://github.com/pgsty/barn/actions/runs/35119206685). All 20 public release assets passed anonymous download and SHA-256 verification, public installer checks passed on `darwin/arm64` and `linux/amd64`, and `pgsty/infra/barn` passed local `brew upgrade` and `brew test`.
- **Ubuntu `amd64`/KVM storage & bootstrap recovery**: Tested corrupt `ext4`/`XFS` data-disk resets (`3.2 s` recovery while keeping the QEMU process alive), persistent disk retention across `recreate`, transient probe failures and busy mounts (preserving existing disk data and UUIDs), read-only 9p share fallback, and resuming a `0.6.0` VM whose initial egress probe had failed (`3.3 s` recovery, surfacing the expected `control-ssh` warning where `0.6.0` had already removed the staged control key; see the [0.7.0 Release Notes](/blog/release/0.7.0/)). Catalog `2026090501` remained unchanged.

### Barn 0.6.0 release — 2026-09-05

- **Release CI and assets**: Following lifecycle, UX, release-metadata, and CI fixture reviews, commit `057774e3a13477782a2ae07bd71127d03c0f1ae7` (`v0.6.0`) passed Go `1.27.1` [source CI](https://github.com/pgsty/barn/actions/runs/33959205857), [packaging checks](https://github.com/pgsty/barn/actions/runs/33958857302) (`13d9d70`), and the [release tag workflow](https://github.com/pgsty/barn/actions/runs/33959431603), producing 20 verified release assets. An isolated `darwin/arm64` installation verified upgrading from `0.5.0` to `0.6.0` via the public installer, plus `barn init` and `barn plan`.
- **macOS `arm64`/HVF lifecycle acceptance**: Verified initial boot, scale-out without restarting the control node, control-to-peer SSH, `stop`/`start`, `reload`, selective `recreate`, scale-in, guest `/etc/hosts` refresh, preflight rejection of invalid `reload` or conflicting partial `recreate` before stopping existing VMs, degraded `status` reporting, and SSH exit code `255` passthrough.
- **Catalog `2026090501`**: Switched the default image to `u24:stable` and incorporated the Debian/Rocky updates from `2026090302` across all 27 verified `qcow2` artifacts on both official endpoints.

### Barn 0.5.0 release — 2026-09-03

Commit `fc85b65ff6a24b0933b56ae1179be9ada2ba91b1` (`v0.5.0`) passed Go `1.27.1` source and GoReleaser packaging gates and published the 20-asset pre-release. `0.5.0` introduced confirmation-free whole-deployment `barn purge`, set `https://repo.pigsty.io/barn` as the global default repository with `--mirror` for `https://repo.pigsty.cc/barn`, removed implicit upstream URL fallback during artifact downloads, and added `packaging/image-pipeline/build-official.py` for the eight digest-pinned Debian/Rocky targets.

### Barn 0.4.0 release — 2026-09-02

Passed `make check` and all release archive, DEB/RPM, SBOM, checksum, installer, and Homebrew formula gates. `barn up` gained automatic interactive host `setup` when run on an unprepared terminal host, `vm_disks[].fs` defaulted to `auto`, readiness errors began surfacing the last guest error line, and CLI output formatting was unified across commands.

### Barn 0.3.0 release — 2026-09-02

Passed `make check` and all release packaging gates. Made catalog refreshes explicit via `barn update` and `barn image sync`, and added per-node failure stages and log inspection hints to guest readiness error messages.

### Barn 0.2.0 release — 2026-09-01

Commit `59d1b62aebb3d044a317e4006cc8a0bf56f4feaf` (`v0.2.0`) passed source CI, packaging workflows, and local four-platform archive, DEB/RPM, and SPDX verification. Live `darwin/arm64` HVF acceptance verified selective `u24-1` create/SSH/stop/start, incremental cached `el9-1` creation, whole-deployment `status`, and `destroy` with SSH config cleanup. On Ubuntu 26.04 `amd64`/KVM, the Linux binary audited a running four-node deployment and connected to its control guest.

### Schema-3 Catalog closure — 2026-08-29

Catalog `2026082903` (9 families, 27 artifacts, SHA-256 `571b1ff9c7d4d42355df3392ea62a339471c2d01d868669a7625fac8b93f245d`, signed by key `4686B39A40F9B562`) passed byte-for-byte equality checks between the embedded catalog and published endpoints, a full SHA-256 sweep across all 27 `qcow2` artifacts (19 GiB), and a clean-client `d13:stable` (`409.3 MiB`) download and `qemu-img` check on `darwin/arm64`.

### 0.1.0 candidates — 2026-08-28 and 2026-08-29

Validated two targeted fixes prior to `0.2.0`:

- **Targeted QMP recovery**: When QMP sockets were externally removed from two of four running nodes on `darwin/arm64`, Barn restarted only the two affected nodes (`13.7 s` to readiness) while keeping the two healthy nodes' boot IDs unchanged.
- **QEMU-free catalog inspection**: Decoupled `barn image list` and `make check` from requiring `qemu-img` on `PATH` when no local cached `qcow2` files need inspection.

### EL7/EL8 compatibility — 2026-08-28

Commit `7c666c7` restored `el7` and `el8` support with regression tests covering pre-recreate runtime preflight ordering and signed-catalog baseline migration. Catalog `2026082801` (9 families, 17 image artifacts, plus 2 `socket_vmnet` archives) passed full SHA-256 and signature checks, and an isolated `darwin/arm64` run booted Rocky Linux 8.10 `arm64` under the built-in TCG rule to SSH readiness in `44.2 s` (verifying NetworkManager, fixed IP, `dba` UID/GID `88`, and guest markers).

### Native replay — 2026-08-27

Verified fixed-IP networking, SSH readiness, default CPU/memory/root/data disks, `cloud-init`, `stop`/`start`, cross-directory CLI invocations, control-node uptime preservation during scale-out, control-to-peer SSH, ignoring upper-layer Pigsty variables, and explicit-only node destruction across `darwin/arm64` and `linux/amd64` (`mx`). On Linux, also verified passwordless `sudo` automation, Debian `qemu-bridge-helper` group permissions, unprivileged bridge attachment, refusal to uninstall an active bridge with four attached tap interfaces, and clean network teardown after `destroy`.
