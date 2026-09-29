---
title: Install Barn
linkTitle: Installation
description: Install Barn 0.9.0 on macOS or Linux, check requirements, and keep the application up to date.
weight: 5
icon: fa-solid fa-download
aliases: [/docs/start/upgrade/]
---

Barn 0.9.0 provides archives for macOS and Linux on **arm64 and amd64**,
plus DEB and RPM packages for Linux. Install it as your normal user, then follow
the [Linux quick start](../tutorial/) or [macOS VM guide](../macos/).

## Install the release

Choose your **host operating system**: use Homebrew on macOS or the download
installer on Linux.

{{< tabs group="barn-install" default="macos" label="Host operating system" >}}
{{< tab label="macOS" value="macos" >}}

Install Barn and its QEMU dependency with [Homebrew](https://brew.sh/):

```bash
brew install pgsty/infra/barn
barn version
```

Run `brew` as your normal user, without sudo. macOS guests also require Apple
Silicon, macOS 27+, and `Barn Mac.app`. Run `barn mac doctor` to check the native
component; see the [Mac installation instructions](../macos/#install).

{{< /tab >}}
{{< tab label="Linux" value="linux" >}}

Download the installer and select the release. It chooses the amd64 or arm64
archive, verifies its SHA-256, and installs into `~/.local/bin` without sudo:

```bash {wrap=true}
curl -fLO https://github.com/pgsty/barn/releases/download/v0.9.0/install.sh
BARN_VERSION=0.9.0 bash install.sh
export PATH="$HOME/.local/bin:$PATH"
barn version
```

Add the PATH line to your shell's startup file, such as `~/.bashrc` for Bash.
The installer keeps the CLI and its matching hosts helper in a versioned
directory; preserve that layout.

{{< /tab >}}
{{< /tabs >}}

Check the installed version with `barn version`. Installing Barn does not start
a VM. Interactive `barn up` prepares missing Linux-guest dependencies and host
networking, requesting administrator access when needed. Use
`barn setup --dry-run` to inspect the plan. Run Barn itself as your normal user.

## System requirements

| guest | Host | Runtime |
|---|---|---|
| Linux | macOS, Apple Silicon or Intel | QEMU 8.2.1+, HVF |
| Linux | Linux, arm64 or amd64 | QEMU 6.2+, usable KVM, NetworkManager or systemd-networkd |
| macOS 27 | Apple Silicon, macOS 27+, logged-in desktop session | Barn Mac native component; no QEMU required |
{.platform-table}

A default Linux VM uses **2 vCPUs and 4 GiB of memory**, with a 64 GiB root
disk and a 128 GiB test data disk. Those are virtual capacities; the files grow
as data is written. Leave memory and disk space for the host as well.

The first Mac VM needs about **65 GiB of free disk space** for Apple's restore
image, the installed base, and initial writes. Its defaults are 4 vCPUs,
8 GiB of memory, and a 100 GiB disk. See [platforms and limits](../../about/status/)
for guest-specific restrictions.

## Other installation methods

### Linux packages

These examples use **amd64**; on ARM64, use the corresponding `linux_arm64` asset.
Packages declare their QEMU, firmware, and SSH dependencies.

```bash {tab="Debian / Ubuntu" group="linux-package" value="deb"}
barn_release=https://github.com/pgsty/barn/releases/download/v0.9.0
curl -fLO "$barn_release/barn_0.9.0_linux_amd64.deb"
sudo apt install ./barn_0.9.0_linux_amd64.deb
barn version
```

```bash {tab="RHEL / Fedora" value="rpm"}
barn_release=https://github.com/pgsty/barn/releases/download/v0.9.0
curl -fLO "$barn_release/barn_0.9.0_linux_amd64.rpm"
sudo dnf install ./barn_0.9.0_linux_amd64.rpm
barn version
```

### Manual archives

Download the archive matching your host from [Barn 0.9.0 on GitHub](https://github.com/pgsty/barn/releases/tag/v0.9.0).
Names follow `barn_0.9.0_<os>_<arch>.tar.gz`, where `os` is `darwin` or `linux`.
Extract it and put its `bin/` directory on PATH. Keep `barn`,
`barn-hosts-helper`, and any bundled `Barn Mac.app` together.

### Build from source

To develop Barn or build the native Mac component yourself, follow
[Build from Source](../source-build/).

## Upgrade Barn

Use the same installation method for upgrades. On macOS, update with Homebrew:

```bash
brew update
brew upgrade pgsty/infra/barn
barn version
```

On Linux, repeat the installer commands with the version you want, or install
the new DEB/RPM package.
Then check `command -v barn` and `barn version` to confirm which binary your
shell selects. Review the [release notes](/blog/release/) before upgrading.

The application, Linux images, and macOS bases have separate update commands:

| What to update | How |
|---|---|
| Barn application | Install the chosen release |
| Linux image catalog | `barn update` (or `barn update --mirror`) |
| macOS base for new machines | `barn mac image update` |

Image updates keep existing VM disks intact. To replace a machine's OS,
review the relevant `recreate` workflow; it replaces the guest disk.
Stop Mac machines before replacing their native component.

For network or PATH problems, see [troubleshooting](../troubleshooting/#download-and-path-problems).
For removal, see [uninstall and cleanup](../uninstall/).
