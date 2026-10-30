---
title: macOS Virtual Machines
linkTitle: macOS VMs
description: Run macOS 27 virtual machines on Apple Silicon with barn mac — create, connect, share files and the clipboard, and clean up.
weight: 20
icon: fa-brands fa-apple
---

> [!NOTE]
> **Unreleased**: The changes below to expanded share names and counts, linked share sources, and flexible state paths require a build containing source commit `27f17bb`; they are not included in Barn 0.9.2. See [Unreleased Changes](/docs/about/unreleased/).

`barn mac` provisions disposable macOS VMs on Apple Silicon Macs for building, testing, and reproducing macOS-specific issues. Each VM comes with an administrator account, passwordless `sudo`, pinned SSH keys, and a dedicated private IP, running directly under your user account via Apple's Virtualization framework without `sudo`.

Mac VMs are managed independently from the Linux lab: they do not read `barn.yml`, they store their state under `$BARN_HOME/mac` (default `~/.barn/mac`), and Linux `barn destroy` or `barn purge` commands never touch them.

## Requirements

- An Apple Silicon Mac running **macOS 27 or later** with an active logged-in desktop session (guests also run macOS 27).
- Roughly **65 GiB** of free disk space for the first VM—covering Apple's ~25 GiB restore image (`.ipsw`), the ~27 GiB installed base image, and initial guest writes. Each VM clones the base image on APFS and grows up to its configured capacity (100 GiB by default).
- The native **`Barn.app`** bundle paired with the `0.9.2` CLI, included in the Apple Silicon release and Homebrew installation.
- No `sudo` privileges required.

Apple's Virtualization framework allows **at most two running macOS VMs at a time** per Mac across all virtualization tools (including an active macOS base-image installation). You can keep additional stopped VMs on disk and start any two at once, subject to the Apple software license.

## Install {#install}

Install the prebuilt release with Homebrew:

```bash
brew install pgsty/infra/barn
barn version
barn mac doctor
```

Homebrew installs the signed, notarized `Barn.app` and matching CLI/helper together. No Go or Xcode installation is needed. The [download installer and manual archive](../installation/) also include the app on Apple Silicon. Stop running Mac VMs before upgrading or replacing the app.

To develop Barn itself, see [Build the Mac component](../source-build/#mac-component).

## Create your first machine

```bash
barn mac up
```

When no macOS base image exists yet, `barn mac up` displays the download and disk requirements before asking for confirmation:

```text
→ macOS 27.0 (26A428) is not prepared on this Mac yet.
download:  24.8 GiB from Apple (updates.cdn-apple.com)
then:      install macOS once into a reusable base (about 20 minutes)
free:      551.2 GiB
Download macOS from Apple now? [Y/n]
```

Once you confirm, Barn completes three steps:

1. **Downloads the restore image from Apple (`updates.cdn-apple.com`)**, resuming any partial transfer and verifying Apple's published SHA-256 digest.
2. **Installs macOS once into an unbooted base image**, temporarily using one of the two macOS VM slots during installation.
3. **Clones `mac1` from the base image** using APFS copy-on-write, boots the guest, configures your user account, and waits until SSH and passwordless `sudo` are ready.
{.steps}

```text
  ✓  mac1 created and ready · macOS 27.0 (26A428) · alice@10.10.20.10
shell:     barn mac ssh mac1
desktop:   barn mac open mac1
```

Subsequent VMs clone the prepared base image in seconds without repeating the IPSW restore. Barn `0.9.2` pins initial setup to **macOS 27.0 (26A428)**; use `barn mac image update` when you want to adopt a newer macOS 27 build.

If you already have a local copy of Apple's restore image, pass `--ipsw` to skip the download (Barn clones it without copying if it resides on the same APFS volume):

```bash
barn mac up --ipsw ~/Downloads/UniversalMac_27.0_26A428_Restore.ipsw
```

In non-interactive scripts, pass `--yes` to authorize the 25 GiB download, or run `barn mac setup` ahead of time to prepare the base image without creating a VM. If you start a new VM with `--no-wait` (which returns as soon as the VM process starts), run `barn mac up NAME` without `--no-wait` to finish SSH and `sudo` provisioning before calling `ssh` or `exec`.

## Work in the machine

### Shell and commands

```bash
barn mac ssh                                  # interactive shell
barn mac exec -- sw_vers                      # single program execution
barn mac ssh -- 'id; sudo -n true && echo sudo works'
```

```text
ProductName:		macOS
ProductVersion:		27.0
BuildVersion:		26A428
```

By default, the guest administrator account matches your host macOS username (override with `--user` at creation time). Place `--` before the remote command: `ssh` passes a command string to the guest shell, while `exec` passes the program and arguments directly (use `sh -c` for shell pipelines or redirection; see the [SSH/exec contract](../../reference/mac/#ssh-and-exec)). Both return the remote command's exit status, and `--json` captures `stdout`, `stderr`, and `exit_code`:

```bash
barn --json mac exec -- sh -c 'echo out; exit 3'
```

```json
{
  "command": "exec",
  "node": "mac1",
  "host": "10.10.20.10",
  "arguments": ["sh", "-c", "echo out; exit 3"],
  "success": false,
  "exit_code": 3,
  "stdout": "out\n"
}
```

See the [Mac command reference](../../reference/mac/#json-output) for the complete JSON schema.

### Desktop

```bash
barn mac open
```

`barn mac open` launches a native window that resizes the guest display dynamically (use **View → Enter Full Screen** for full-screen mode). Closing the window leaves the VM running in the background; run `barn mac open` again to reopen it, or to boot a stopped VM and open its display.

While the guest window has focus, keyboard shortcuts are sent to the guest OS, so use the macOS menu bar for host actions:

| Menu item | Action |
|---|---|
| **Machine → Share Clipboard** | Toggle plain-text clipboard sync for the current session |
| **Machine → Restart…** | Restart macOS inside the guest |
| **Machine → Shut Down…** | Perform a clean guest shutdown (equivalent to `barn mac stop`) |
| **Window → Keep Running in Background** | Hide the desktop window while keeping the VM running |
| **Barn → Quit Barn…** | Choose whether to keep the VM running in the background or shut it down |

When you log out of or shut down the host Mac, Barn requests a clean guest shutdown and powers off the VM if it does not stop before the timeout.

Each VM also generates a random password for the macOS lock screen and GUI administrator prompts. Copy it directly to your host clipboard without printing it to the terminal:

```bash
barn mac password --copy
```

### Clipboard

Clipboard sharing syncs plain text across focus changes over the VM's SSH channel without installing extra guest agents: focusing the guest window syncs text copied on the host Mac, and switching back to a host app syncs text copied inside the guest. Concealed items from password managers, images, and files are never transferred.

To disable clipboard sharing persistently for a VM, run `barn mac configure mac1 --clipboard off` (applied on the next start).

### Shared folders {#shared-folders}

Pass one or more `--share` flags when creating a VM to mount host directories inside the guest under `/Volumes/My Shared Files/<name>`:

```bash
barn mac up dev --cpu 8 --memory 16G --share ~/src --share docs=~/Documents:ro
barn mac exec dev -- ls "/Volumes/My Shared Files"
```

The share name defaults to the directory's basename, and appending `:ro` mounts it read-only. Each shared path must resolve to an existing directory (symlinks are supported); Barn never creates or deletes shared host directories. To add or remove shares on an existing VM, stop it first and run `barn mac configure`:

```bash
barn mac stop dev
barn mac configure dev --share data=/Volumes/Work/data --unshare docs
barn mac start dev
```

Because VirtioFS on macOS guests can briefly cache file contents after host-side edits, use `scp` or `rsync` to copy files onto the guest disk when a build requires immediate byte-level consistency.

### SSH from other tools

When the first Mac VM becomes ready, Barn adds a marked `Include` line to `~/.ssh/config` so `ssh mac1`, `scp`, `rsync`, and IDE Remote-SSH extensions work out of the box using each VM's dedicated key and pinned host key:

```bash
ssh mac1 'uptime'
rsync -a ./project/ mac1:project/
barn mac ssh-config              # print the generated SSH config entries
barn mac ssh-config --remove     # remove Barn's Include and disable auto-install
```

If `~/.ssh/config` is a symlink managed by a dotfile tool, Barn leaves the file untouched and prints the `Include` line for you to add. Re-enable automatic integration after `--remove` with `barn mac ssh-config --install`. If your personal `~/.ssh/config` already defines a `Host` alias with the same name as a VM, Barn preserves your alias and writes its managed entry by IP address only.

## Multiple machines

Assign each VM a lowercase alphanumeric name (starting with a letter, with optional internal hyphens). Creation flags (`--cpu`, `--memory`, `--disk`, `--user`, `--share`) apply only when creating a new VM:

```bash
barn mac up dev --cpu 8 --memory 16G
barn mac ls
```

```text
NAME  STATE    ADDRESS      SSH    USER   OS          CPU  MEMORY  DISK                 SHARED
dev   running  10.10.21.10  ready  alice  macOS 27.0    8  16 GiB  504.0 MiB / 100 GiB    src,data
mac1  running  10.10.20.10  ready  alice  macOS 27.0    4   8 GiB  4.7 GiB / 100 GiB
limit:     2 of 2 macOS VMs are running; stop one before starting another
```

When you omit the VM name, commands target the sole existing VM or `mac1` (and ask you to disambiguate when multiple VMs exist). If you request a `--disk` size that differs from the prepared base image's capacity, Barn installs a new base image at that capacity from the restore image first.

Each VM gets its own `/24` private subnet starting at `10.10.20.0/24` (guest IP `.10`), automatically skipping subnets that overlap with your LAN, VPNs, the Linux lab, or other Mac VMs. If two Mac VMs are already running, starting a third fails immediately and suggests a VM to stop:

```bash
barn mac up build --user ci
```

```text
error: dev and mac1 are running; macOS allows 2 macOS virtual machines at a time
next: barn mac stop mac1
```

## Everyday lifecycle {#everyday-lifecycle}

```bash
barn mac stop dev               # clean guest shutdown (powers off after 2m timeout)
barn mac start dev              # boot and wait for SSH
barn mac restart dev            # stop then start, applying pending configure changes
barn mac stop --all             # stop all running Mac VMs
```

Use `barn mac stop --force` for an immediate power-off, or `barn mac start --recovery` to boot into macOS Recovery with the desktop window open.

`barn mac up` never mutates an existing VM's specification—passing changed creation flags on an existing VM returns a hint pointing to `barn mac configure`:

```text
error: dev already exists, so --cpu would not apply; its configuration and data were preserved
next: barn mac configure dev --cpu 4
```

Stop the VM before changing CPUs, memory, shared folders, or subnet with `configure` (clipboard settings can be toggled while running):

```bash
barn mac stop dev
barn mac configure dev --cpu 6 --memory 12G --subnet auto
barn mac start dev
```

To reset a VM's disk to a clean clone of the base image while preserving its name, account, hardware settings, shares, and IP, run `barn mac recreate`. To delete the VM completely, run `barn mac destroy` (pass `--force` in non-interactive scripts):

```bash
barn mac recreate dev
barn mac destroy dev
```

| Operation | Guest disk and installed apps | Hardware settings, IP, and account |
|---|---|---|
| `stop` / `start`, `restart`, repeated `up` | Preserved | Preserved |
| `configure` | Preserved | Updated as requested |
| `recreate` | Replaced with a fresh macOS clone | Preserved (generates new login password and SSH keys) |
| `destroy` | Deleted | Deleted (base image is retained) |

## macOS versions and disk space

```bash
barn mac image ls
```

```text
KIND  OS          BUILD   STATE  ON DISK   CAPACITY  USED BY
base  macOS 27.0  26A428  ready  26.7 GiB  100 GiB   mac1,default
```

Run `barn mac image update` to query Apple for the newest supported macOS 27 build, download its IPSW, and prepare a new default base image for future VMs. Existing VMs stay on their current build until you run `barn mac recreate NAME --update` (if a VM uses a custom disk size such as `200G`, prepare the matching base image first with `barn mac setup --disk 200G`).

Use `barn mac image prune` to inspect unused non-default base images, adding `--installers` to include downloaded `.ipsw` files and `--yes` to delete them:

```bash
barn mac image prune --installers         # preview reclaimable images
barn mac image prune --installers --yes   # delete them
```

Because APFS clones share physical storage blocks with the base image, `ON DISK` and per-VM disk figures overlap and do not sum linearly.

## Troubleshooting {#troubleshooting}

Run `barn mac doctor` to check host compatibility, the native `Barn.app` bundle, base images, and every VM, and use `barn mac logs [name]` to inspect startup, network, and Virtualization framework logs.

| Symptom | Resolution |
|---|---|
| `network … overlaps route …` on start | A VPN or new host route now overlaps the VM's subnet. Run `barn mac configure NAME --subnet auto`. |
| `macOS allows 2 macOS virtual machines at a time` | Stop one of the running Mac VMs (`barn mac stop NAME`) or quit another tool's macOS VM. |
| Third-party SSH client reports `No route to host` for `ssh mac1` | Grant Local Network access to your terminal/IDE in **System Settings → Privacy & Security → Local Network**, or use `/usr/bin/ssh` (`barn mac ssh` and `exec` use Apple's system binary). |
| `mac_runner_missing` or `mac_runner_protocol` | Keep `barn`, `barn-hosts-helper`, `barn-mac-runner`, and `Barn.app` from the same `make mac-build` output directory together. |
| Starting a VM fails from a remote SSH session | Run `barn mac` inside a terminal attached to the Mac's logged-in graphical desktop session with the login keychain unlocked. |

Apple Account sign-in inside macOS guests is not reliably supported by Apple's Virtualization framework, and USB passthrough, snapshots, and VM suspend/resume are not supported.

## Clean up

```bash
barn mac ls                                 # list existing Mac VMs
barn mac destroy mac1 dev                   # delete selected VMs
barn mac image prune --installers --yes     # delete cached IPSWs and unused base images
```

Destroying the last Mac VM automatically cleans up its `~/.ssh/config` entries while keeping the default base image. For a complete removal of all Mac VM state:

1. Destroy all Mac VMs (`barn mac destroy ...`) and run `barn mac ssh-config --remove`.
2. Delete `$BARN_HOME/mac` (default `~/.barn/mac`).
3. Optionally remove `~/Library/Preferences/com.pgsty.barn.plist` (`io.pgsty.barn.mac-runner.plist` in `0.9.0`), which stores desktop window geometry.
{.steps}
