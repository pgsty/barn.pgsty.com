---
title: Status
description: Barn 0.9.0 rename candidate, publication boundaries, historical validation, and known limits.
weight: 20
icon: fa-solid fa-list-check
aliases: [/docs/project/, /docs/project/status/, /docs/project/roadmap/, /docs/project/release/, /docs/project/design-history/]
---

Barn 0.9.0 is the first release candidate under the new name and is **not yet
published**. Source checks, local builds, packages, CI, releases, and the public
site are verified separately. Renamed source alone does not establish public
delivery. Installation instructions are in the [Quick Start](../../start/tutorial/#install).

## Documentation baseline {#documentation-baseline}

| Object | Current identity | How to use it |
|---|---|---|
| Application and current docs | Barn 0.9.0 release candidate | Build a checkout containing the rename; package commands apply after publication. |
| CLI and configuration | `barn`, `barn.yml`, `BARN_*` | No old-name command aliases or environment fallbacks. |
| State and host resources | `~/.barn`, Barn networking and helpers | Create fresh Barn state; there is no development-state migration. |
| Image repository | `/barn` at the official endpoints | Catalog signatures remain required; cloud migration and public access need independent verification. |

Stop old internal environments and preserve needed data before creating a fresh
Barn installation. Do not simply rename an old state directory. The final
release commit, artifact digests, Homebrew and public endpoints will be recorded
after verification. Historical 0.2–0.8 records keep the Farrow name and do not
establish Barn 0.9.0 publication or acceptance.

## macOS guests {#macos-guests}

`barn mac` runs macOS 27 guests on Apple Silicon; see the [guide](../../start/macos/)
and [reference](../../reference/mac/). Its component is `Barn Mac.app`, with
signing identifier `io.pgsty.barn.mac-runner`. It uses independent
`$BARN_HOME/mac` state and has no command to migrate earlier development data.

After the rename on 2026-09-29, local CLI/hosts-helper tests, native
Bridge/image/exit-prompt/menu tests, the runner build, ad-hoc signature checks
and `probe` passed. These checks started no VM and did not repeat the complete
Mac native lifecycle. Earlier native results retain their original identity below.

## Remaining release checks

- The full source, archives, DEB/RPM, installer and cross-platform checks at the final Barn commit;
- Fresh host setup and Linux/macOS VM lifecycle and cleanup under the new names;
- Mac Developer ID signing, notarization and publication;
- The live GitHub repository, Homebrew, both image repositories and `barn.pgsty.com`.

The records below describe pre-rename checkpoints. Their old commands, paths,
versions and links are historical evidence only.

## Farrow Mac native record: 2026-09-29

The pre-rename Farrow development tree was validated on 2026-09-29 on an Apple Silicon Mac running macOS
27.0 (26A428), with an ad-hoc signed development build. No macOS image was
downloaded for the run: every test home used an APFS clone of a base prepared
on 2026-09-26 from Apple's pinned 27.0 restore image.

- **Source gates**: complete `make check`, native component tests, and the Mac bundle build with extracted-archive checksum, signature, and probe checks passed.
- **Automated live acceptance**: all 16 phases passed in 244.9 s: creation from the base, a named machine with a shared folder, independent identities and sshd policy, disk isolation, per-machine networks isolated from each other, DNS and public HTTPS, exit codes and argument boundaries, bidirectional shared-folder writes, normal stop/start, `configure`, refusal of a third running VM, `recreate` rotating identities, desktop and two-way clipboard, repeated `up` leaving the base unchanged, and `destroy`.
- **Manual checks**: creation to SSH-ready in 22 s from a prepared base; normal stop 6.5 s; start to SSH-ready 6–12 s; forced stop 0.7 s; macOS Recovery boot; a subnet change keeping the pinned host key; `ssh mac1` through the installed OpenSSH entries.

Still open for macOS guests: Developer ID signing, notarization, and a
published release; downloading and installing macOS through the current CLI
(a first `up` without a prepared base, or `image update`); the desktop's
**Restart…** and **Shut Down…** menu actions; other Apple Silicon models and
macOS 27 updates; and physical-host reboot.

## Pre-rename Linux validation summary {#summary}

| Host or artifact | Path | Last verified | Result |
|---|---|---|---|
| Two Linux amd64 hosts (`m0`, `m3`) | KVM, seven operating systems per host | 2026-09-21 (0.8.0) | clean initialization, first SSH, final candidate upgrade, repeated up, stop/start, disk identity, and Ansible configuration reads passed |
| Two macOS arm64 hosts (`m1`, `m5`) | HVF, seven operating systems per host | 2026-09-21 (0.8.0) | the same lifecycle checks plus seven-node Ansible ping passed |
| Catalog `2026092001` | 9 families, 37 artifacts; September Debian/Ubuntu refresh | 2026-09-21 | embedded/local/LAN/public Catalog bytes match; ten new image objects reachable at both public endpoints with expected sizes; selected images passed the four native pro runs |
| Ubuntu 26.04 amd64 | KVM, QEMU 10.2.1, Ubuntu 24.04 guest | 2026-09-16 (0.7.0 recovery) | damaged disk resets, failed probes, busy mounts, retained-disk recreation, share recovery, and repeated healthy up passed |
| macOS arm64 | HVF, Ubuntu 24.04.4 guests | 2026-09-05 (0.6.0 lifecycle changes) | create, scale-out, peer SSH, stop/start, reload, recreate, partial status, and scale-in passed |
| macOS 26.6.2 arm64 | HVF, QEMU 11.1, socket_vmnet | 2026-09-01 (`v0.2.0`) | selected create/SSH/stop/start, incremental cached create, whole status, whole destroy passed |
| macOS 26.6.2 arm64 | HVF, QEMU 11.1, socket_vmnet | 2026-08-27 | one node and additive four nodes passed |
| Ubuntu 26.04 amd64 (`mx`) | KVM, QEMU 10.2.1, NetworkManager | 2026-09-01 (`v0.2.0`) | audited an existing four-node deployment as live and reached its control guest |
| Ubuntu 26.04 amd64 (`mx`) | KVM, QEMU 10.2.1, NetworkManager | 2026-08-27 | setup, one node, additive four nodes, and uninstall passed |
| macOS arm64 | HVF host, TCG compatibility rule, Rocky Linux 8.10 arm64 | 2026-08-28 | boot, stop/start, readiness in 44.2 s passed |
| Published Catalog `2026090501` | 9 families, 27 qcow2 artifacts | 2026-09-05 | artifact verification, embedded/public byte equality, and signed update through both official endpoints passed |
| Published Catalog `2026082903` | 9 families, 27 signed qcow2 artifacts | 2026-08-29 | full SHA-256 sweep and clean-client `d13:stable` pull passed |

The 0.8 run covered Rocky Linux 9.8/10.2, Debian 12.15/13.7, and Ubuntu
22.04.5/24.04.5/26.04.1 on each host: 28 successful guest instances in total.
The temporary acceptance VMs were subsequently cleaned up. Both public Catalogs
have SHA-256 `23e8dbf6c19bd192d56c6d71eb30901f17945b3487e427a43abe108463780306`.
Isolated `farrow update` runs at both endpoints verified the signatures and
activated revision `2026092001`. The public image check used HEAD/content lengths
for ten new objects at each endpoint, not a fresh download/hash of every public
artifact.

## Coverage left open at the earlier checkpoint

- EL9 hosts with NetworkManager and firewalld, and a current systemd-networkd replay;
- physical-host reboot persistence;
- macOS amd64 and Linux arm64 native runs, beyond their build/package checks;
- EL7 through the current native Linux/amd64 lifecycle;
- macOS directory sharing: the tested QEMU cannot reopen Farrow's securely held directory descriptor;
- a complete current Pigsty `configure → farrow up → install.yml` run;
- a native replay of the corrected fresh Homebrew socket_vmnet authentication path;
- clean-host setup and VM creation through the public installer, Homebrew, or published DEB/RPM packages.

Current built-in versions are `supported`, except EOL EL7 and the retained
compatibility versions EL9 9.3/9.6 and EL10 10.0, which are `deprecated`.
Active and standby Catalog public keys are embedded. Private-key custody and
rotation, together with release custody, must be formalized before 1.0.

## Farrow verification history

Each entry belongs to the exact checkpoint exercised that day. Later source or
documentation edits do not inherit native proof without another replay.

### Farrow 0.8.0 — 2026-09-21

Release tag `v0.8.0` points to `320a32afa8f6fca02592215aa0d5607ca4e852b2`.
The [source CI](https://github.com/pgsty/farrow/actions/runs/35568664994), independent
[packaging snapshot](https://github.com/pgsty/farrow/actions/runs/35568664948), and
[tag workflow](https://github.com/pgsty/farrow/actions/runs/35569143101) passed.
The tag workflow produced 20 assets, including 19 checksummed payloads. The
publication commit changes only README and release notes relative to the tested
runtime below; a new local build at the tag passed the archive/package checks.

The release became public on 2026-09-21. All 20 assets were downloaded
anonymously through the host's configured proxy, without GitHub credentials.
Every request returned HTTP 200 and the full-body SHA-256 matched both the API
digest and inspected draft; all 19 checksummed payloads matched the manifest.
Public installers succeeded in isolated user directories on macOS arm64 and
Linux amd64. Both reported 0.8.0 / `320a32a` and installed exactly the CLI/helper
bytes from their verified public archives. Linux downloads used a temporary SSH
loopback forward to the existing proxy, removed afterward. Default installations
and VM/network state stayed unchanged. These checks verify binary installation;
fresh-host setup and VM creation through the public installer remain untested.

The [Homebrew tap](https://github.com/pgsty/homebrew-infra/commit/9c3401958a435248ebf0e5402e7efff712ee1c4c)
now selects 0.8.0 for all four targets with the public archive digests. Local
syntax, updater tests, consistency/style/platform checks, strict online audit,
and native arm64 `brew fetch` passed. Its macOS and Linux
[CI jobs](https://github.com/pgsty/homebrew-infra/actions/runs/35570285428)
also passed metadata, updater, style, platform, and audit checks. There was no
new `brew install`, upgrade, relink, or `brew test` in this release verification.

The clean initialization baseline was `6d7870e26cb2f4082a00c188f746783fc027687e`.
On each of four hosts, the run removed the owned old lab and network, started
from an empty Farrow user state/cache, and created the seven-system pro inventory
using one LAN repository. Linux used the actual DEB; macOS used a complete
checksum-verified user installation of the archive's paired CLI/helper.

The runtime candidate `1c054a027420b5410c6f6feb344e27e001ae1af1` added the
Homebrew authentication-order fix and passed complete local `make check` and
release archive/package verification. It was installed in place on all four
hosts, then passed healthy `up`, two rounds of guest SSH, stop/start, and Ansible
configuration reads. Both Macs also passed Ansible ping on every node. VM UUIDs,
image identities, and root/data disk paths and inodes were retained; healthy
`up` also kept the running processes. All runs checked real data-disk access,
Debian locales/XFS, and control-node SSH to the other guests.

This is a clean 6d baseline followed by a final 1c in-place lifecycle replay,
not a second clean initialization at 1c. The new Homebrew ordering has a regression
that fails before the fix and passes after it; the native clean runs used the
pinned backend archive, so they do not exercise a new Homebrew formula install.
No physical host was rebooted, and no full Pigsty installation or macOS shared
folder was included. The [release notes](../../../blog/release/farrow-0.8.0/)
include the measured lifecycle samples and image versions.

### Farrow 0.7.0 release — 2026-09-16

Release commit `9c6d4896d93733d1cb60a7e5d8591e9a06659c9d` passed the complete
[source CI](https://github.com/pgsty/farrow/actions/runs/35118137961) and independent
[packaging snapshot](https://github.com/pgsty/farrow/actions/runs/35118137990) before
tagging. The [tag workflow](https://github.com/pgsty/farrow/actions/runs/35119206685)
repeated the gates and published a draft with 20 assets. After inspection, the
release was made public; all 20 anonymous downloads returned HTTP 200 and matched
the inspected bytes, including all 19 checksummed payloads. Public installers on
macOS arm64 and Ubuntu amd64 installed the exact archive binaries. Download tests
used the host's configured proxy; m3 reached it through a temporary loopback tunnel.
The `pgsty/infra/farrow` formula was refreshed to `v0.7.0`; a local Homebrew
upgrade and `brew test` passed, while a clean-host formula install remains open.

The Ubuntu amd64/KVM recovery matrix covered corrupt ext4/XFS filesystems,
retained disks, failed probes, busy mounts, read-only shares, and repeated healthy
`up` without process replacement. A public 0.6.0 bootstrap failed its egress probe;
0.7.0 resumed that same VM in 3.3 seconds. Probe failure left existing disk data
and UUID intact. The old 0.6.0 CLI still completed status, stop, start, and destroy
after upgrade, including with a cached optional warning. A fresh VM from the
final 0.7.0 archive booted without warnings and ignored the old VM's cache.

The publicly installed Linux binary also reset a deliberately damaged disposable
ext4 disk in 3.2 seconds, reported discarded data, and retained the running VM's
process. Stop, start, and purge then passed.

That interrupted 0.6.0 bootstrap had already deleted its staged control-node SSH
key. Management access recovered, but missing peer SSH remained an explicit
`control-ssh` limitation; see the [upgrade notes](../../../blog/release/farrow-0.7.0/).
This release adds no guest images: Catalog `2026090501` remains unchanged.
There was no new macOS HVF, host reboot, or complete Pigsty replay.

### Farrow 0.6.0 release — 2026-09-05

The lifecycle and UX changes passed two adversarial Claude Code Fable 5.1
reviews at xhigh effort; release metadata and the CI test fixture received
follow-up approvals. Release commit `057774e3a13477782a2ae07bd71127d03c0f1ae7`
passed the complete Go 1.27.1 [source CI](https://github.com/pgsty/farrow/actions/runs/33959205857).
The latest packaging changes passed the independent
[snapshot and package checks](https://github.com/pgsty/farrow/actions/runs/33958857302)
at `13d9d70`. The [tag workflow](https://github.com/pgsty/farrow/actions/runs/33959431603)
repeated source checks and verified four platform archives, four Linux
packages, eight SPDX documents, the installer, Homebrew formula, release
metadata, and all 19 checksummed payloads before creating the 20-asset release.
The release is public. All asset digests match the checksum manifest. An
isolated macOS arm64 installation upgraded from public 0.5.0 to public 0.6.0;
both installed executables match the verified release archive. The released
binary also passed `init` and a fresh U24 `plan`.

An isolated macOS arm64/HVF U24 lab passed initial boot, expansion without
restarting the control node, control-to-peer SSH, stop/start, normal reload,
selected recreation, scale-in, and guest-name refresh. Invalid-image reload
and conflicting selected recreation stopped before disrupting the existing
VMs. Partial status kept the healthy peer visible, and SSH exit 255 passed
through. Effective OpenSSH configuration tests covered the final guest SSH
scope correction. The test lab was removed after validation.

Published Catalog `2026090501` defaults to `u24:stable` and incorporates the
Debian/Rocky image updates already published in Catalog `2026090302`. All 27
artifacts passed repository byte verification. Both official endpoints now
serve the exact embedded catalog and its production signature; isolated
clients completed `farrow update` against each endpoint.
This application release builds no new guest images. Linux-host VM lifecycle,
host reboot, and a complete Pigsty installation were not replayed for 0.6.0.

### Farrow 0.5.0 release — 2026-09-03

Exact commit `fc85b65ff6a24b0933b56ae1179be9ada2ba91b1` passed both main-branch
workflows before tagging: the complete Go 1.27.1 source gate and the independent
GoReleaser snapshot/package path. The exact tag workflow then repeated the
source/toolchain checks, built and verified four platform archives, four native
Linux packages, eight SPDX documents, the Homebrew formula, installer,
`release.json`, and the 19-entry checksum manifest before creating the
20-asset pre-release.

0.5.0 adds no-confirmation whole-deployment `purge`/`rm`, makes the global
`repo.pigsty.io` default and China `--mirror` explicit, removes hidden Catalog
upstream fallback, and adds the digest-pinned eight-target Debian/Rocky official
image candidate builder. The builder results remain unsigned `testing`
candidates; no image Catalog or native VM lifecycle result is promoted by this
application release.

### Farrow 0.4.0 release — 2026-09-02

The exact tag commit passed `make check` and the release workflow's archive,
DEB/RPM, SBOM, checksum, installer, Homebrew-formula, and package-parity gates.
`up` now runs `setup` itself on an unprepared terminal host, `vm_disks[].fs`
defaults to `auto`, readiness failures carry the guest's last error line, and
every command shares one output style. The first-run path was not replayed on a
fresh host; no new native VM replay is claimed here.

### Farrow 0.3.0 release — 2026-09-02

The exact tag commit passed `make check` and the release workflow's archive,
DEB/RPM, SBOM, checksum, installer, Homebrew-formula, and package-parity gates.
Catalog refresh is now explicit (`farrow update` for the configured repository,
`image sync` for an exact source), and guest readiness failures carry per-node
stages and next-step log commands. No new native VM replay is claimed here.

### Farrow 0.2.0 release — 2026-09-01

Source commit `59d1b62aebb3d044a317e4006cc8a0bf56f4feaf` is tagged `v0.2.0`.
Its source CI and independently dispatched packaging workflow passed the exact
commit. The stable local release path also built and verified all four platform
archives, amd64/arm64 DEB and RPM packages, eight SPDX documents, paired helper
digests, archive/package parity, Homebrew formula, installer, release metadata,
and 19 checksummed final assets.

The macOS arm64/HVF replay ran with MonoProxy's covering `10.0.0.0/8` exclusion
present. Selected `u24-1` create/SSH/stop/start, incremental cached `el9-1`
create, whole status with five absent desired peers, both SSH connections, and
whole destroy/SSH-fragment cleanup passed. On Ubuntu 26.04 amd64/KVM, the Linux
binary audited an existing four-node Farrow deployment as live and reached its
control guest without mutating that host.

The compiled default image repository remains the signed COS-backed
`https://repo.pigsty.cc/farrow`. The independently checked
`https://repo.pgsty.com/farrow` source endpoint serves identical Catalog,
authoring metadata, checksums, and image bytes with a read-only Nginx worker.

### Schema-3 Catalog closure — 2026-08-29

Catalog revision `2026082903` was the source and development-repository
checkpoint on that date: 9 families and 27 architecture-specific artifacts. The embedded
Catalog and published `catalog.json` have the same SHA-256
`571b1ff9c7d4d42355df3392ea62a339471c2d01d868669a7625fac8b93f245d`;
the published `repo.yaml` also matches the source-controlled authoring file.
Fresh HTTP and HTTPS clients accepted the detached signature from production
key `4686B39A40F9B562`.

All 27 published qcow2 files (19 GiB total) passed a full SHA-256 sweep against
the Catalog. A clean temporary Farrow home then downloaded the complete
409.3 MiB Darwin/arm64 default `d13:stable` artifact, rehashed it, and accepted
its qcow2 structure and virtual size. These are publication-integrity and
client-path checks, not a replacement for the native lifecycle matrix; no
existing VM was recreated for this Catalog check.

### 0.1.0 candidates — 2026-08-28 and 2026-08-29

Two isolated `v0.1.0` candidates passed the stable local release path before
0.2.0 superseded them. Two facts from those runs still stand on their own: the
Darwin/arm64 binary repaired two live nodes whose QMP sockets had been removed
externally by stopping and starting only those nodes, both reaching readiness in
13.7 seconds while the two untouched peers kept their boot IDs; and a full macOS
factory reset exposed a source-test dependency on an installed `qemu-img`, so
catalog-only `image list` could not run on a blank host. The store is resolved
lazily only when local qcow2 bytes need validation, regression tests explicitly
remove QEMU from `PATH`, and `make check` passes with QEMU, Farrow, and network
state absent.

### EL7/EL8 compatibility — 2026-08-28

Commit `7c666c7` restored EL7/EL8 after two independent adversarial reviews.
The first review blocked on destructive runtime preflight ordering and
signed-Catalog baseline migration; both were fixed, regression tested, and the
second review returned PASS with no required fixes.

At that checkpoint, Catalog `2026082801` was signed and active on the
development repository: 9 families, 17 image artifacts, and 19 SHA-verified
repository payloads including the two socket_vmnet archives. A clean client
accepted the public signature and exact embedded digest.

An isolated macOS arm64 lifecycle replay booted Rocky Linux 8.10 arm64 with the
built-in TCG compatibility rule, passed stop/start and readiness in 44.2 seconds,
and verified NetworkManager, fixed IP/no-route/no-DNS, `dba` UID/GID 88, and the
generation/spec marker. EL7 bytes, qcow2 structure, BIOS layout, and 4K XFS root
are verified; the native Linux/amd64 Farrow lifecycle replay remains open.

### Native replay — 2026-08-27

Both hosts in the summary table passed fixed IP, SSH readiness, default
CPU/memory/root/data disk, cloud-init, stop/start, cross-directory commands,
unchanged control-node boot ID during scale-out, control-to-peer SSH, ignored
unconsumed Pigsty changes, absence-never-destroys, and explicit destroy.

Linux additionally proved valid NOPASSWD automation, caller-accessible Debian
helper policy, unprivileged bridge smoke, refusal to uninstall with four tap
members, and exact restoration after destroy.

Interactive host-network and hosts commands invoke sudo themselves; an external
`sudo -v` is optional. Darwin cleanup can reconstruct an uninstall-only
ownership plan from byte-identical interface evidence, the exact launchd plist,
and installed binary digests when `network.json` is missing.

On 2026-08-28 the post-calibration tree passed unit, race, vet, staticcheck,
govulncheck, all four cross-builds, the simulated image-pipeline boundary,
license verification, and GoReleaser configuration validation. An isolated
local GoReleaser snapshot also built and verified all four archives, both
DEB/RPM architectures, SPDX documents, checksums, dependencies, modes, and
archive/package parity. Nothing was published, and those results do not extend
the native matrix.
