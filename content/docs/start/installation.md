---
title: Install Barn
linkTitle: Installation
description: Install Barn 1.2.0 on macOS or Linux, check requirements, and keep the application up to date.
weight: 5
icon: fa-solid fa-download
aliases: [/docs/start/upgrade/]
---

Barn 1.2.0 ships archives for macOS and Linux on **arm64 and amd64**, along with DEB and RPM packages for Linux. Always run `barn` as your normal Unix user; after installing, continue with the [Linux quick start](../tutorial/) or [macOS VM guide](../macos/).

> [!NOTE]
> [Barn 1.2.0](https://github.com/pgsty/barn/releases/tag/v1.2.0) is the current stable release. It is published on GitHub's regular release channel, so `releases/latest`, the installer without `BARN_VERSION`, and the Homebrew formula select it; set `BARN_VERSION=1.2.0` to pin it. The Apple Silicon archive includes the matching `barn`, `barn-hosts-helper`, and native macOS app bundle (`Barn.app`), signed with Developer ID and notarized by Apple. Go and Xcode are only needed for [source builds](../source-build/).

| Component | Purpose | Included in 1.2.0 downloads |
|---|---|---|
| `barn` | Go CLI for Linux labs and macOS VM lifecycle | All four platform archives and Linux packages |
| `barn-hosts-helper` | Companion binary for `/etc/hosts` name integration | Packaged alongside its matching CLI |
| `Barn.app` | Native `Virtualization.framework` runner and macOS guest desktop | Included in the Darwin arm64 archive and Apple Silicon Homebrew install; macOS guests only |
{.wide .expand}

## Install the release {#install-the-release}

Choose the operating system of your **host** machine. Use Homebrew on macOS or the release installer script on Linux.

{{< tabs group="barn-install" default="macos" label="Host operating system" >}}
{{< tab label="macOS" value="macos" >}}

Install Barn and its QEMU dependency with [Homebrew](https://brew.sh/) as your normal user:

```bash
brew install pgsty/infra/barn
barn version
```

On Apple Silicon, the [Homebrew formula](https://github.com/pgsty/homebrew-infra/blob/main/Formula/barn.rb) also installs `Barn.app` under `libexec`, where the CLI discovers it automatically. On macOS 27+, run `barn mac doctor` and continue with the [Mac guide](../macos/#install). Intel Macs use the CLI and helper for Linux guests.

{{< /tab >}}
{{< tab label="Linux" value="linux" >}}

Download `install.sh` and run it. Without `BARN_VERSION`, it installs the latest stable release; set `BARN_VERSION=1.2.0` to pin this one. The script detects `amd64` or `arm64`, verifies the archive SHA-256 against `checksums.txt`, and installs the CLI and matching `barn-hosts-helper` under `~/.local/bin` without `sudo`:

```bash {wrap=true}
curl -fLO https://github.com/pgsty/barn/releases/latest/download/install.sh
bash install.sh
export PATH="$HOME/.local/bin:$PATH"
barn version
```

Add `export PATH="$HOME/.local/bin:$PATH"` to your shell startup file (such as `~/.bashrc` or `~/.zshrc`), and keep the versioned `.barn-releases/` directory layout intact. You can also run this same installer on macOS if you prefer not to use Homebrew; `barn setup` will handle QEMU and host-network dependencies separately.

{{< /tab >}}
{{< /tabs >}}

When you run `barn up` interactively for the first time, Barn checks for missing Linux-guest dependencies and host networking, shows the host-preparation plan, and asks once before installing anything; it requests administrator access (`sudo`) only when a step needs it. Without a terminal, `barn up` only reports what is missing, so run `barn setup --yes` for unattended preparation. To preview the host changes without applying them, run `barn setup --dry-run`.

## System requirements {#system-requirements}

| Guest | Host | Runtime |
|---|---|---|
| Linux | macOS, Apple Silicon or Intel | QEMU 8.2.1+, HVF |
| Linux | Linux, arm64 or amd64 | QEMU 6.2+, usable KVM, NetworkManager or systemd-networkd |
| macOS 27 | Apple Silicon, macOS 27+, logged-in desktop session | `Barn.app` native component; no QEMU required |
{.platform-table .wide .expand}

A default Linux VM uses **1 vCPU and 2 GiB of memory**, backed by thin-provisioned `qcow2` disks (64 GiB root disk and 128 GiB test data disk) that grow as data is written.

The first macOS VM requires roughly **65 GiB of free disk space** to hold Apple's ~25 GiB restore image, the ~27 GiB installed base image, and initial guest writes. By default, a Mac VM uses 4 vCPUs, 8 GiB of memory, and a 100 GiB APFS clone disk. Later Mac VMs inherit the prepared base image's capacity unless you pass `--disk`. See [Platforms and limits](../../about/status/) for guest-specific constraints.

## Other installation methods {#other-installation-methods}

### Linux packages {#linux-packages}

The DEB and RPM packages declare their QEMU, UEFI firmware, and OpenSSH dependencies automatically. On ARM64 hosts, replace `amd64` with `arm64`:

```bash {tab="Debian / Ubuntu" group="linux-package" value="deb"}
barn_release=https://github.com/pgsty/barn/releases/download/v1.2.0
curl -fLO "$barn_release/barn_1.2.0_linux_amd64.deb"
sudo apt install ./barn_1.2.0_linux_amd64.deb
barn version
```

```bash {tab="RHEL / Fedora" group="linux-package" value="rpm"}
barn_release=https://github.com/pgsty/barn/releases/download/v1.2.0
curl -fLO "$barn_release/barn_1.2.0_linux_amd64.rpm"
sudo dnf install ./barn_1.2.0_linux_amd64.rpm
barn version
```

### Manual archives {#manual-archives}

Download `barn_1.2.0_<os>_<arch>.tar.gz` (`darwin` or `linux`, `arm64` or `amd64`) and `checksums.txt` from [Barn 1.2.0 on GitHub](https://github.com/pgsty/barn/releases/tag/v1.2.0), then verify the SHA-256 digest before extracting:

```bash
barn_release=https://github.com/pgsty/barn/releases/download/v1.2.0
curl -fLO "$barn_release/barn_1.2.0_darwin_arm64.tar.gz"
curl -fLO "$barn_release/checksums.txt"
shasum -a 256 -c checksums.txt --ignore-missing
```

Extract the archive and add its `bin/` directory to `PATH`. Keep the packaged layout intact: `barn` and `barn-hosts-helper` must stay paired, and the Darwin arm64 archive also contains `bin/Barn.app`. The CLI verifies the helper's embedded SHA-256 before invoking it and discovers the app beside the binary.

### Build from source {#build-from-source}

To work on Barn or compile the native `Barn.app` bundle for macOS guests, see [Build from Source](../source-build/).

## Upgrade Barn {#upgrade-barn}

Upgrading from **1.1.0 to 1.2.0** preserves VM disks, SSH keys, state, and configuration under `~/.barn`. Stop running Mac VMs before replacing the CLI, helper, and `Barn.app` together. Linux inventories that omit CPU/memory now resolve to 1 vCPU / 2 GiB; explicitly set `vm_cpu: 2` and `vm_mem: 4GiB` to preserve the old defaults and inspect `barn plan`. Existing applied VMs keep their resources until a resource-changing operation is requested. See the [1.2.0 release notes](/blog/release/1.2.0/).

Upgrade using the same channel you used to install Barn. On macOS with Homebrew:

```bash
brew update
brew upgrade pgsty/infra/barn
barn version
```

On Linux, re-run `install.sh` (it selects the latest stable release unless `BARN_VERSION` is set) or install the newer `.deb` / `.rpm` package, then run `command -v barn` and `barn version` to confirm the active binary.

Barn decouples CLI upgrades from guest image updates so existing VMs never change OS versions unexpectedly:

| Target | Command | Effect on existing VMs |
|---|---|---|
| Barn CLI, helper & bundled app | Reinstall or `brew upgrade` | Preserves all VM disks and state |
| Linux image catalog | `barn update` (or `barn update --mirror`) | Updates catalog for new or `recreate`d nodes |
| macOS base image | `barn mac image update` | Prepares a new base image; apply to an existing VM with `barn mac recreate NAME --update` |
{.wide .expand}

For proxy or `PATH` issues, see [Troubleshooting](../troubleshooting/#download-and-path-problems). To remove Barn and its host state, see [Uninstall and Clean Up](../uninstall/).
