---
title: Status
description: Barn 0.9.0 release candidate, current validation, and remaining release checks.
weight: 20
icon: fa-solid fa-list-check
---

Barn 0.9.0 is an **unreleased candidate**. Source checks, local builds,
packages, CI, releases, and the public site are verified separately.
Installation instructions are in the [Quick Start](../../start/tutorial/#install).

## Documentation baseline {#documentation-baseline}

| Object | Current identity | How to use it |
|---|---|---|
| Application and current docs | Barn 0.9.0 release candidate | Build from source; package commands apply after publication. |
| CLI and configuration | `barn`, `barn.yml`, `BARN_*` | Check `barn version` before applying version-specific guidance. |
| State and host resources | `~/.barn`, Barn networking and helpers | One Linux deployment per user; macOS guests use separate state. |
| Image repository | `/barn` at the official endpoints | Signed Catalog `2026092901` published and publicly verified on 2026-09-29; see the image record below. |

The final release commit, artifact digests, and installation channels will be
recorded after publication and download verification.

## macOS guests {#macos-guests}

`barn mac` runs macOS 27 guests on Apple Silicon; see the [guide](../../start/macos/)
and [reference](../../reference/mac/). Its component is `Barn Mac.app`, with
signing identifier `io.pgsty.barn.mac-runner` and independent `$BARN_HOME/mac` state.

On 2026-09-29, local CLI/hosts-helper tests, native Bridge/image/exit-prompt/menu
tests, the runner build, ad-hoc signature checks, and `probe` passed.
These checks started no VM and do not establish complete Mac lifecycle acceptance.

## Remaining release checks

- The full source, archives, DEB/RPM, installer, and cross-platform checks at the final Barn commit;
- Fresh host setup and Linux/macOS VM lifecycle and cleanup;
- Mac Developer ID signing and notarization;
- Barn 0.9.0 publication and download verification, including Homebrew.

## Linux image Catalog: 2026-09-29

Catalog `2026092901` is published at both official `/barn` endpoints: nine
families and 45 artifacts, retaining all 37 earlier artifacts. Debian 12 is
`20260923.2610.1`, Ubuntu 22.04/24.04 are `20260926.0.0`, and Ubuntu 26.04 is
`20260927.0.0`, each on amd64 and arm64. Debian 13 keeps its existing version.

All eight new images passed native KVM/HVF UEFI boot, SSH, dual-NIC,
UID/GID 88, locale and XFS data-disk read/write checks using the current Barn
cloud-init. The Debian 12 upstream images still need the offline XFS and
`en_US.UTF-8` adjustments; Ubuntu retains the original Canonical bytes.
These checks used isolated QEMU user networks and do not replace the full
host networking and lifecycle checks above.

The embedded, local, LAN and public Catalog bytes match. Both public
signatures and isolated-client upgrades from `2026092001` passed. The eight
new objects at each endpoint passed size and first/last Range/If-Range checks;
COS CRC64 and R2 multipart ETags matched checksums recomputed from the full
local files. Initial R2 Range responses that returned 200 were retained as
evidence; after refreshing the new objects' cache, every check returned the
expected 206 and bytes. See [Images](../../reference/images/) for versions and
update behavior.
