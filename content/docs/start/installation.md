---
title: Install Barn
linkTitle: Installation
description: Install Barn 0.9.1 on macOS or Linux, check requirements, and keep the application up to date.
weight: 5
icon: fa-solid fa-download
aliases: [/docs/start/upgrade/]
---

Barn 0.9.1 provides archives for macOS and Linux on **arm64 and amd64**,
plus DEB and RPM packages for Linux. Run Barn as your normal user.
After installation, follow the [Linux quick start](../tutorial/) or [macOS VM guide](../macos/).

[Barn 0.9.1](https://github.com/pgsty/barn/releases/tag/v0.9.1) uses the
pre-release channel. The downloads include the CLI and hosts helper;
`Barn.app` requires a [source build](../source-build/#mac-component).

Select the version explicitly. Barn's release workflow marks versions below
1.0.0 as GitHub pre-releases; `releases/latest` excludes them, and the installer
does not fall back to them.

| Component | Purpose | Included in 0.9.1 downloads |
|---|---|---|
| `barn` | Go CLI for Linux and macOS VM lifecycle | All four platform archives and Linux packages |
| `barn-hosts-helper` | Restricted companion for managed host-name integration | Packaged with its matching CLI |
| `Barn.app` | Virtualization.framework runner and macOS guest desktop | Not included in 0.9.1 downloads; build from tag `v0.9.1` |

Linux guests use QEMU and do not need the native Mac app. The app does not
replace the CLI or include QEMU, macOS restore images, or VM disks.

## Install the release

Choose the operating system of the computer that will run Barn—the **host**.
Use Homebrew on macOS or the download installer on Linux.

{{< tabs group="barn-install" default="macos" label="Host operating system" >}}
{{< tab label="macOS" value="macos" >}}

Install Barn and its QEMU dependency with [Homebrew](https://brew.sh/):

```bash
brew install pgsty/infra/barn
barn version
```

Run `brew` as your normal user, without sudo. The 0.9.1
[Homebrew formula](https://github.com/pgsty/homebrew-infra/blob/main/Formula/barn.rb)
installs the CLI and hosts helper. It does not include `Barn.app`. macOS guests
require Apple Silicon, macOS 27+, and a native component built from tag `v0.9.1`.
See the [Mac installation instructions](../macos/#install).

{{< /tab >}}
{{< tab label="Linux" value="linux" >}}

Download the installer and select the release when you run it.
It chooses the amd64 or arm64 archive, verifies its SHA-256, and installs it into `~/.local/bin` without sudo:

```bash {wrap=true}
curl -fLO https://github.com/pgsty/barn/releases/download/v0.9.1/install.sh
BARN_VERSION=0.9.1 bash install.sh
export PATH="$HOME/.local/bin:$PATH"
barn version
```

Add the PATH line to your shell's startup file, such as `~/.bashrc` for Bash.
The installer keeps the CLI and its matching hosts helper in a versioned directory. Preserve that layout.

If you prefer, use the same pinned installer on macOS instead of Homebrew.
It installs Barn; `barn setup` prepares Linux-guest dependencies separately.

{{< /tab >}}
{{< /tabs >}}

Check the installed version with `barn version`. Installing Barn does not start
a VM. Interactive `barn up` prepares missing Linux-guest dependencies and host networking. It requests administrator access when needed. Use
`barn setup --dry-run` to inspect the plan. Run Barn itself as your normal user.

## System requirements

| guest | Host | Runtime |
|---|---|---|
| Linux | macOS, Apple Silicon or Intel | QEMU 8.2.1+, HVF |
| Linux | Linux, arm64 or amd64 | QEMU 6.2+, usable KVM, NetworkManager or systemd-networkd |
| macOS 27 | Apple Silicon, macOS 27+, logged-in desktop session | Barn.app native component; no QEMU required |
{.platform-table}

A default Linux VM uses **2 vCPUs and 4 GiB of memory**, with a 64 GiB root
disk and a 128 GiB test data disk. These are virtual capacities; the files grow as data is written. Leave memory and disk space for the host as well.

The first Mac VM needs about **65 GiB of free disk space** for Apple's restore
image, the installed base image, and initial writes. Its defaults are 4 vCPUs, 8 GiB of memory, and a 100 GiB disk for the first base image. Unless you specify `--disk`, later VMs inherit the prepared base image's capacity. See [platforms and limits](../../about/status/)
for guest-specific restrictions.

## Other installation methods

### Linux packages

These examples use **amd64**; on ARM64, use the corresponding `linux_arm64` asset.
Packages declare their QEMU, firmware, and SSH dependencies.

```bash {tab="Debian / Ubuntu" group="linux-package" value="deb"}
barn_release=https://github.com/pgsty/barn/releases/download/v0.9.1
curl -fLO "$barn_release/barn_0.9.1_linux_amd64.deb"
sudo apt install ./barn_0.9.1_linux_amd64.deb
barn version
```

```bash {tab="RHEL / Fedora" value="rpm"}
barn_release=https://github.com/pgsty/barn/releases/download/v0.9.1
curl -fLO "$barn_release/barn_0.9.1_linux_amd64.rpm"
sudo dnf install ./barn_0.9.1_linux_amd64.rpm
barn version
```

### Manual archives

Download the archive matching your host from [Barn 0.9.1 on GitHub](https://github.com/pgsty/barn/releases/tag/v0.9.1).
Names follow `barn_0.9.1_<os>_<arch>.tar.gz`, where `os` is `darwin` or `linux`.
Verify the selected archive against the release's `checksums.txt` before
extracting it. For example, on Apple Silicon:

```bash
barn_release=https://github.com/pgsty/barn/releases/download/v0.9.1
curl -fLO "$barn_release/barn_0.9.1_darwin_arm64.tar.gz"
curl -fLO "$barn_release/checksums.txt"
shasum -a 256 barn_0.9.1_darwin_arm64.tar.gz
```

Compare the complete digest with that filename's entry in `checksums.txt`.
If it matches, extract the archive and add its `bin/` directory to PATH.
Keep `barn` and `barn-hosts-helper` in their packaged locations.
The helper must match the SHA-256 embedded in the CLI; an unrelated helper will not work.
The 0.9.1 archives do not include `Barn.app`; build the complete native bundle
from tag `v0.9.1` to run macOS guests.

### Build from source

To develop Barn or build the native Mac component yourself, follow
[Build from Source](../source-build/).

## Upgrade Barn

For 0.9.0 → 0.9.1, stop Mac VMs before replacing the app and update the CLI,
helper, and app together. The new CLI recognizes old `Barn Mac.app` bundles;
the old CLI does not discover `Barn.app`. Existing VM disks and configuration
stay in place. No VM recreation or image-catalog update is required. Desktop
window positions may reset because the app identifier changed. See the
[0.9.1 upgrade notes](/blog/release/0.9.1/).

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

The application, Linux images, and macOS base images have separate update commands:

| What to update | How |
|---|---|
| Barn application | Install the chosen release |
| Linux image catalog | `barn update` (or `barn update --mirror`) |
| macOS base image for new machines | `barn mac image update` |

Image updates keep existing VM disks intact. To replace a VM's OS, review the relevant `recreate` workflow. This operation replaces the guest disk.
Stop Mac machines before replacing their native component.

For network or PATH problems, see [troubleshooting](../troubleshooting/#download-and-path-problems).
For removal, see [uninstall and cleanup](../uninstall/).
