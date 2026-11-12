---
title: "Barn 1.2.0 release readiness and acceptance"
description: "Release gates, upgrade compatibility, packaging, and physical-host acceptance for Barn 1.2.0."
date: 2026-11-12
lastmod: 2026-11-12
weight: 76
categories: [Design]
tags: [Release, Testing, CLI]
icon: fa-solid fa-clipboard-check
---

**Status, 2026-11-12:** [Barn 1.2.0](https://github.com/pgsty/barn/releases/tag/v1.2.0) is published as stable/latest. Its final acceptance is recorded below; the candidate sections preserve the earlier review and its original scope.

## Final release {#final-release}

Tag `v1.2.0` points to `90f615804b823b4eb491101e642073dcd37a9700`. [Source/Mac CI](https://github.com/pgsty/barn/actions/runs/43121333312) and [complete packaging CI](https://github.com/pgsty/barn/actions/runs/43121333418) passed that exact commit before tagging. All 437 reviewed build inputs match the candidate manifest. The signed catalog gate passed again before formal packaging.

The release used the documented local signing path because GitHub signing secrets remain unconfigured. Apple accepted notarization `165b486b-5055-4eca-a595-54bed6bdd6c1`. `make release-local` passed archive, DEB/RPM, SPDX, helper-pairing, timestamp, and package/archive checks. Downloaded CLI/helper/app bytes passed Developer ID, staple, and Gatekeeper checks. All 20 draft attachments and all 20 anonymous public downloads match the verified sizes and SHA-256 digests.

The final downloaded archives passed 18 Linux/KVM operations and all 15 native Mac lifecycle phases. Additional native UI checks confirmed desktop login, two-way plain-text clipboard transfer, a closed window leaving the VM and SSH running, and normal shutdown. Isolated 1.1.0 → 1.2.0 upgrade and repeat installation passed. Both `darwin/arm64` and `linux/amd64` passed public latest and pinned installation. The [Homebrew update](https://github.com/pgsty/homebrew-infra/commit/f1b83ae) covers four platforms; real 1.1.0 → 1.2.0 upgrade, `brew test`, style, and strict online audit passed.

[Three-platform Homebrew CI](https://github.com/pgsty/homebrew-infra/actions/runs/43128081768) passed `e633aee` on Linux, Apple Silicon, and Intel macOS, covering syntax, style, updater tests, readall, and audit. Intel setup previously built OpenSSL while automatically migrating the runner's preinstalled Azure CLI. Limiting setup to metadata refresh resolved that delay; all subsequent formula checks remained enabled.

The final Mac run retained an initial Apple HTTPS TLS timeout. The identical request subsequently returned HTTP 200; the harness resumed after rechecking both guest identities, disk sentinels, and the base digest, then completed the remaining phases. The test VM was stopped after GUI acceptance. GitHub direct-download timeouts were resolved using the hosts' existing proxies; the public downloads used no authentication. Failure logs were retained.

The homepage keeps its explicitly dated 1.1.0 recording and explains the 1.2.0 default/output changes. A fresh four-node first-run recording needs free `.10–.13` addresses; existing host VMs occupied them during this release. Release identity and public-channel evidence are also listed in [Validation History](/docs/about/history/#release-1-2-0).

The 1.2.0 site update at `b9e6498` passed [site CI](https://github.com/pgsty/barn.pgsty.com/actions/runs/43125783766) and became the active Cloudflare production deployment. The production build checked 303 HTML pages; 19 public checks covered bilingual release, installation and command pages, canonical URLs, sitemaps, search indexes, robots, and a real 404. The final browser connection timed out, so visual evidence retains the earlier local spot-check scope.

## Candidate identity {#candidate-identity}

This table records the state at the start of preparation, before the final release commits.

| Item | Reviewed state |
|---|---|
| Source repository | Local `main` at `6ab0cd5`, three commits ahead of fetched `origin/main` at `b2cc8da`; additional hosts changes remain uncommitted |
| Documentation repository | Local `main` at `bc7968a`, three commits ahead of fetched `origin/main` at `d392cd5`; the command reference and corrections remain uncommitted |
| Snapshot | `.goreleaser-preflight-1.2.0-20261112`, version `1.1.1-next`, binary commit `uncommitted` |
| Source inputs | SHA-256 `9a4d4dd378d4b5762a4d06bd8e19830a09e0919e808f5fffc4c154fbdf55e01a` for the manifest of 437 source, test, native, and packaging files |
| Catalog | Revision `2026110502`, default `u24:stable` on the native architecture |
{.wide .expand}

The snapshot version follows the existing `incpatch` rule from the last tag, `v1.1.0`. Formal `1.2.0` assets were subsequently rebuilt from the final `v1.2.0` commit. Snapshot binaries deliberately identify the modified tree as `uncommitted`.

## Issues resolved during preparation {#resolved}

- The default shell selected GoReleaser 2.18.3 while the source requires 2.20.1. The validation run used the already downloaded pinned tools, and `packaging/check-toolchain.sh all` confirmed every version before packaging.
- The changelog and release-note drafts omitted the Linux default change from 2 vCPUs / 4 GiB to 1 vCPU / 2 GiB. They now explain how to preserve the earlier defaults with explicit `vm_cpu: 2` and `vm_mem: 4GiB`. Both binaries were checked against implicit and explicit inventories.
- The release drafts now include `all.vars.vm_hosts` and `hosts install -f`. Their implementation and tests subsequently entered commit `ad74cc9`. The candidate's inventory-only preview was exercised before VM creation.
- Root-level `.idea/` and the local `barn.yml` are now ignored and were retained on disk. Existing source edits and historical-document deletions were preserved.

## Completed gates {#completed-gates}

| Gate | Evidence |
|---|---|
| Source | `make check` passed: unit/race tests, static analysis, four-target builds, installer and image-pipeline boundaries, and licenses |
| Native components | `make mac-native-test` passed bridge, image, menu, and exit-prompt tests |
| Catalog | Both official mirrors passed signature verification, activation in new data roots, embedded-byte comparison, and size/availability checks for 17 stable artifacts each |
| Packaging | `make release-snapshot` passed with `BARN_MAC_REQUIRE_PAYLOAD=1` and the freshly built native payload; archives, Linux DEB/RPM, SPDX, checksums, helper pairing, timestamps, and package/archive parity were verified |
| Linux runtime | 18 operations passed on Ubuntu 26.04.1 / x86_64 with KVM, using the extracted snapshot archive |
| Mac runtime | All 15 automated lifecycle phases passed on macOS 27.0.1 / arm64 with Xcode 27.2, using the extracted snapshot archive |
| Upgrade | A VM created by the published 1.1.0 archive retained its process and identity when adopted by the candidate; root growth and teardown passed |
| Documentation | Production `make check` and a separate build including drafts passed internal-link and asset checks for 301 and 303 HTML pages; browser spot checks covered the Chinese command index, English lifecycle reference, and Chinese readiness record |
{.wide .expand}

The catalog bytes retain SHA-256 `d41e46d20bc57cb1b071e3919a27a8f7f703df2addca879970a528e7ab004065`, so no embedded catalog update was needed. The catalog gate did not stream every artifact to recompute payload digests; the Linux acceptance image downloads did verify their selected payloads. `govulncheck` found no reachable vulnerabilities; its unused-module report remains documented in the candidate release notes. Native offline image mutation was skipped by the ordinary source suite; the image pipeline was unchanged in this release candidate.

## Linux acceptance {#linux-acceptance}

Two isolated guests used Debian 13 `20261103.2651.1` and Rocky Linux 9 `9.8.20260525.2`, with 1 vCPU / 1 GiB, 12 GiB roots, and persistent 1 GiB XFS data disks. The host's prepared Barn network was reused.

- A running ext4 root grew to 14 GiB and stayed running. Repeating the target preserved its QEMU PID; a 13 GiB shrink was rejected before mutation.
- A stopped XFS root grew to 14 GiB through temporary boots and returned to stopped. Repeating the target preserved its root-image modification time.
- A deliberately failing `resize2fs` left a recoverable `guest` journal for a 16 GiB target. Restoring the tool and retrying completed filesystem growth.
- Killing the CLI after `qemu-img` enlarged the image left the `image` journal at an 18 GiB target. Retry completed growth and restored running state.
- VM UUID, generation, disk serial, partition identity, filesystem UUID, SSH host key, and root/data-disk sentinels survived growth and recovery. Serial stop (`-p 1`) and unrestricted start (`-p 0`) passed.
- Test nodes and their explicitly selected persistent disks were destroyed. The host's SSH configuration and `/etc/hosts` matched their original bytes afterward.

The initial harness attempt created a group-writable image-cache directory, which Barn rejected before creating any guest. The fixture was corrected to use private permissions, and its failed evidence was retained. This was a harness setup error.

A separate upgrade run created a guest with the published 1.1.0 archive (SHA-256 `09fa37b35ac15763320898bdf81fe0051e83f6b8f3a4898fb01149e6c2611926`). The candidate read its applied 2 vCPU / 4 GiB state. Adding explicit CPU/memory values to the inventory let `up` preserve its running PID and VM UUID; `resize -D 14GiB` then grew the old 12 GiB root while retaining machine ID, host key, generation, and a data sentinel. Teardown restored the host SSH configuration. An initial harness command assumed that Linux `ssh` quoted a `sh -c` argument; the documented raw-SSH contract requires shell quoting. The resumed test used an explicit quoted SSH command and retained the first failure log.

Implementation evidence is in `internal/private/root_resize.go`, `internal/private/root_resize_guest.py`, `internal/private/root_resize_test.go`, `internal/private/concurrency_test.go`, and `cmd/barn/lifecycle_parallel_test.go`. The earlier [arm64 ext4/XFS acceptance](../root-disk-growth/#acceptance) retains its own date and measurements. MBR layouts and native Linux/arm64 hosts still have no new physical-host replay in this round.

## Mac acceptance {#mac-acceptance}

The test root used an APFS clone of the prepared macOS 27.0 base (`26A428`). Its configuration disabled automatic host SSH integration. The 15-phase harness covered two independent VMs, guest account policy, private networks, DNS/HTTPS, remote argument and exit-code preservation, shared-folder writes, stop/start, CPU/memory reconfiguration, the two-VM host limit, recreate identity rotation, base-image immutability, repeated `up`, and destruction of one VM while preserving its peer. The survivor was stopped after the automated run.

The packaged app also opened the survivor's desktop, and visual inspection confirmed automatic login to the macOS Finder desktop. The VM was then shut down normally. This check did not establish the close-window behavior or clipboard transfer. The snapshot used ad-hoc signing; the final Developer ID/notarized release subsequently passed Gatekeeper, installation, window-close, and clipboard checks as recorded above.

## Release execution {#remaining}

1. Source changes were committed in `ad74cc9` and `90f6158`; the command reference and documentation review were separately committed in `24ff1e2`. Both repositories were pushed and their CI passed.
2. Source and packaging CI passed `90f6158`, then `v1.2.0` was tagged and pushed.
3. The catalog gate passed, and the [local Mac release procedure](/docs/about/mac-release/#local-release) produced matching signed/notarized assets. `make release-local` verified the complete release.
4. Final archive acceptance and all 20 draft re-downloads passed before stable/latest publication. All 20 public downloads and both platform installers passed afterward.
5. Homebrew and the bilingual guides were updated to 1.2.0, including default resources, command options, upgrade notes, and release evidence.
{.steps}

This release used an existing local Developer ID identity and stored notary profile. No keys were exported or signing credentials changed.
