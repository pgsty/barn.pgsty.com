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
| Application and current docs | Barn 0.9.0 release candidate | Install Homebrew HEAD or build from source; release packages are not yet published. |
| CLI and configuration | `barn`, `barn.yml`, `BARN_*` | Check `barn version` before applying version-specific guidance. |
| State and host resources | `~/.barn`, Barn networking and helpers | One Linux deployment per user; macOS guests use separate state. |
| Image repository | `/barn` at the official endpoints | Signed Catalog `2026092902` published and publicly verified on 2026-09-29; see the image record below. |

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

Signed Catalog `2026092902` is published at both official `/barn` endpoints:
nine families and 39 artifacts. The normalized Debian and Rocky Linux images
use Barn configuration and metadata throughout.

| Family | Stable version | Architectures |
|---|---|---|
| Debian 12 | `20260923.2610.1` | amd64, arm64 |
| Debian 13 | `20260914.2601.2` | amd64, arm64 |
| Rocky Linux 8 | `8.10.20240528.2` | amd64, arm64 |
| Rocky Linux 9 | `9.8.20260525.2` | amd64, arm64 |
| Ubuntu 22.04 / 24.04 | `20260926.0.0` | amd64, arm64 |
| Ubuntu 26.04 | `20260927.0.0` | amd64, arm64 |

The six Debian 13 and Rocky Linux images passed UEFI boot, SSH, dual-NIC,
UID/GID 88, Python, cloud-init, and XFS data-disk checks. The amd64 images used
KVM; Debian 13 and Rocky Linux 9 arm64 used HVF. Rocky Linux 8 arm64 used TCG
because its upstream 64 KiB kernel is incompatible with Apple HVF. Rocky Linux
8 uses its shipped RHEL chrony template and `chronyd` service.

The Debian 12 and Ubuntu images passed native KVM/HVF boot, SSH, dual-NIC,
UID/GID 88, locale, and XFS data-disk checks. Debian images include the locked
XFS tools and `en_US.UTF-8`, retaining `C.UTF-8` as the default; Ubuntu keeps the
original Canonical bytes. These image checks used isolated QEMU user networks;
full host networking and VM lifecycle acceptance remains a separate release check.

The embedded and published Catalog bytes match. Both official endpoints pass
signature verification, and the new objects pass public download checks.
See [Images](../../reference/images/) for version selection and update behavior.
