---
title: macOS Virtual Machines
linkTitle: macOS VMs
description: Run macOS 27 virtual machines on Apple Silicon with barn mac — create, connect, share files and the clipboard, and clean up.
weight: 20
icon: fa-brands fa-apple
---

`barn mac` creates disposable macOS VMs on an Apple Silicon Mac for testing, building, and reproducing macOS-specific behavior.
Each VM has an administrator account, passwordless sudo, pinned SSH keys, and a fixed address.
Barn uses Apple's Virtualization framework to run the VMs as your user, without administrator access.

Mac VMs are separate from the Linux lab. They do not read `barn.yml` or join a Pigsty inventory. Barn stores their data under `$BARN_HOME/mac` (default `~/.barn/mac`). Linux `destroy` and `purge` do not affect them.

## Requirements

- An Apple Silicon Mac running **macOS 27 or later**, with a user logged in to
  its desktop. Guests also run macOS 27.
- About **65 GiB** free for the first VM. This includes Apple's 25 GiB restore image, the 27 GiB installed base image, and startup space. Barn keeps the restore image until you prune it. Each VM then grows with its own changes up to its disk capacity,
  100 GiB by default.
- The native **Barn.app** component paired with the 0.9.1 CLI. Xcode 27+ is
  needed only to build the native component.
- No sudo. Every VM, its network and its desktop run as your user.

The native runtime supports **two macOS VMs running at a time**
on one Mac, counting those of other tools and macOS installation itself.
You can create more VMs and start any two, subject to the applicable
Apple software license.

## Install {#install}

[Install Barn 0.9.1](../installation/), then check the Mac component:

```bash
barn version
barn mac doctor
```

**The 0.9.1 downloads and Homebrew formula do not include `Barn.app`.**
The native component remains a source preview. Until it is built, `doctor`
reports the missing component.

On Apple Silicon, build tag `v0.9.1` with **Xcode 27+** and
[Go 1.27.3](../source-build/):

```bash
git clone --branch v0.9.1 https://github.com/pgsty/barn.git
cd barn
BARN_VERSION=0.9.1 make mac-build
export PATH="$PWD/bin/mac:$PATH"
barn version
barn mac doctor
```

`bin/mac` contains the CLI, matching hosts helper, native runner, and `Barn.app`.
Keep the complete bundle together. With signing variables unset, this local
build uses an ad-hoc signature; it is not a notarized release download.
`doctor` checks the host, component signature, free disk space, and existing
VMs. It does not verify Apple notarization. See [source builds and signing](../source-build/#mac-component).
Stop existing Mac VMs before replacing their bundle.

## Create your first machine

```bash
barn mac up
```

If the Mac has no prepared macOS base image, `up` lists the requirements and asks for confirmation:

```text
→ macOS 27.0 (26A428) is not prepared on this Mac yet.
download:  24.8 GiB from Apple (updates.cdn-apple.com)
then:      install macOS once into a reusable base (about 20 minutes)
free:      551.2 GiB
Download macOS from Apple now? [Y/n]
```

After you confirm, Barn:

1. **Downloads the restore image from Apple only**. Barn verifies it against Apple's published SHA-256. It resumes interrupted downloads.
2. **Installs macOS once** into an unbooted *base image*. Installation uses one of
   the two macOS VM slots while it runs.
3. **Creates `mac1`** as a copy-on-write clone of the base image. Barn starts it and creates your account. It waits until SSH and sudo work.

```text
  ✓  mac1 created and ready · macOS 27.0 (26A428) · alice@10.10.20.10
shell:     barn mac ssh mac1
desktop:   barn mac open mac1
```

Later VMs reuse the installed base image, skipping the full macOS restore.
Startup time depends on host resources and first-boot provisioning. Barn 0.9.1 pins the first download to macOS **27.0 (26A428)**. The timing and free-space figures above are examples. `image update` explicitly selects a newer supported
macOS 27 base image.

If you already have Apple's restore image, pass it instead of downloading.
If the image is on the same APFS volume, Barn clones it without copying. Otherwise, Barn verifies the file and uses it in place:

```bash
barn mac up --ipsw ~/Downloads/UniversalMac_27.0_26A428_Restore.ipsw
```

Without a terminal, such as in a script, `up` downloads the 25 GiB image only if you supply `--yes`. `barn mac setup` prepares
the base image ahead of time without creating a VM.

`--no-wait` returns when the VM runs, before SSH provisioning and readiness.
If you used that flag for a new VM, finish initialization with `barn mac up NAME` without `--no-wait` before using `ssh` or `exec`. Polling `ls` alone does not install its SSH keys or sudo configuration.

## Work in the machine

### Shell and commands

```bash
barn mac ssh                                  # interactive shell
barn mac exec -- sw_vers                      # one command
barn mac ssh -- 'id; sudo -n true && echo sudo works'
```

```text
ProductName:		macOS
ProductVersion:		27.0
BuildVersion:		26A428
```

The account has your macOS user name and passwordless sudo. To choose another name, use `--user` when creating the VM. Like plain ssh, `ssh` passes a command line to the guest shell. `exec` keeps argument boundaries. Both return the guest's exit status. `--json` records stdout, stderr, and the exit code:

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

The JSON above is shortened. The [Mac reference](../../reference/mac/#json-output) lists every field.

### Desktop

```bash
barn mac open
```

The desktop opens in a native window sized to your screen. Resizing it changes the guest resolution.
To enter full screen, use **View → Enter Full Screen**.

Closing the window keeps the VM running. Use `open` to show it again; if the VM is stopped, the command starts it first.
While the window has focus, keyboard shortcuts go to the guest, so use the menu bar for host commands:

| Menu | Action |
|---|---|
| **Machine → Share Clipboard** | turn clipboard sharing on or off for this session |
| **Machine → Restart…** | restart macOS in the guest |
| **Machine → Shut Down…** | shut down normally, like `barn mac stop` |
| **Window → Keep Running in Background** | hide the window; the VM keeps running |
| **Barn → Quit Barn…** | choose to keep the VM running or shut it down |

The app-renaming changes use **Barn → Quit Barn…** instead.
Logging out or shutting down the host requests guest shutdown; if the guest does not stop, Barn eventually powers it off.

Each VM has a random login password for the lock screen and desktop administrator prompts.
To copy it without printing it:

```bash
barn mac password --copy
```

### Clipboard

Clipboard sharing transfers plain text when focus changes. When you click the guest window, text copied on the Mac becomes available in the guest. When you switch to another app, text copied in the guest becomes available on the Mac. Text travels over the VM's own SSH connection. Barn installs nothing in the guest for this feature. Items that password managers
mark as concealed never leave the Mac. Images and files are not shared.

To disable clipboard sharing for a VM, use `barn mac configure mac1 --clipboard off`. The setting applies at the VM's next start.

### Shared folders

Share Mac folders when creating a VM. The guest mounts them under
`/Volumes/My Shared Files/<name>`:

```bash
barn mac up dev --cpu 8 --memory 16G --share ~/src --share docs=~/Documents:ro
barn mac exec dev -- ls "/Volumes/My Shared Files"
```

The name defaults to the folder's last path component. `:ro` makes a share read-only. A share must be an existing directory, not a symlink. Barn never creates or deletes shared folders. To change shares later, stop the VM. Then use `configure`:

```bash
barn mac stop dev
barn mac configure dev --share data=/Volumes/Work/data --unshare docs
barn mac start dev
```

macOS guests can show stale file contents for a short while after the Mac
changes a shared file. If you need the latest bytes immediately, use `scp`
or `rsync` to copy the files onto the guest's own disk.

### SSH from other tools

When the first VM becomes ready, Barn adds one marked `Include` to `~/.ssh/config`. Then `ssh mac1`, `scp`, `rsync`, and editors with Remote-SSH can reach every VM by name. Each connection uses the VM's own key and pinned host key:

```bash
ssh mac1 'uptime'
rsync -a ./project/ mac1:project/
barn mac ssh-config              # print the entries
barn mac ssh-config --remove     # remove only what Barn added
```

Lifecycle commands keep the entries current. If a dotfile tool manages `~/.ssh/config` through a link, Barn does not edit it. Barn prints the `Include` line for you to add.

`--remove` also disables automatic integration until you run
`barn mac ssh-config --install`. If your SSH config already owns a VM's
name, Barn preserves that alias and publishes its entry by IP address only.
`barn mac ssh` and `exec` use the VM's own key and pinned host key,
independently of your personal SSH keys and config.

## Several machines

Give each VM a name. Creation options apply only to a new VM:

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

Names use lowercase letters, digits and inner hyphens and start with a letter.
A command without a name acts on the only VM, or on `mac1`. If the target is ambiguous, you must specify a name. `DISK` shows the space the VM uses now
and its capacity. The base image determines the capacity. If `--disk` differs from the prepared base image's capacity, Barn installs another base image first. This requires the restore image again.

Each VM has its own private network. The first available subnet is `10.10.20.0/24`, with the guest at `.10`. Barn skips subnets that conflict with your LAN, VPNs, the Linux lab, or another Mac VM.
VMs reach the Mac and use NAT for outbound connections. If two VMs in the same Barn data root are running, Barn refuses a third before creating anything. It names a VM to stop:

```bash
barn mac up build --user ci
```

```text
error: dev and mac1 are running; macOS allows 2 macOS virtual machines at a time
next: barn mac stop mac1
```

## Everyday lifecycle

```bash
barn mac stop dev               # shut down through macOS
barn mac start dev              # boot and wait for SSH
barn mac restart dev            # stop, then start, applying changes
barn mac stop --all             # every machine
```

`stop` shuts down normally. If a VM still runs after two minutes, Barn powers it off and reports the action. `stop --force` powers off immediately. Powering off loses unsaved work in the guest.
`start --recovery` boots macOS Recovery and shows its desktop.

`up` never reconfigures an existing VM. If you pass an option that
differs, it refuses and names the command to use:

```text
error: dev already exists, so --cpu would not apply; its configuration and data were preserved
next: barn mac configure dev --cpu 4
```

While the VM is stopped, `configure` changes CPUs, memory, shared folders, and the network. It can change clipboard sharing at any time. Changes apply at the next
start:

```bash
barn mac stop dev
barn mac configure dev --cpu 6 --memory 12G --subnet auto
barn mac start dev
```

`recreate` replaces a VM with a fresh macOS from the base image, keeping its
name, account, resources, shared folders and address. `destroy` deletes
VMs. Both describe what they delete and ask you to type the command name. Without a terminal, use `--force` to confirm.

Choose the operation you need:

```bash
barn mac recreate dev
barn mac destroy dev
```

| Operation | guest disk and apps | Settings, address, account |
|---|---|---|
| `stop`/`start`, `restart`, repeated `up` | kept | kept |
| `configure` | kept | changed as requested |
| `recreate` | replaced with a fresh macOS | kept; new password and SSH keys |
| `destroy` | deleted | deleted |

None of these operations changes the shared base image. Barn retains it when VMs are destroyed.

## macOS versions and disk space

```bash
barn mac image ls
```

```text
KIND  OS          BUILD   STATE  ON DISK   CAPACITY  USED BY
base  macOS 27.0  26A428  ready  26.7 GiB  100 GiB   mac1,default
```

Updates require an explicit command. `barn mac image update` asks Apple for the newest macOS 27. After you confirm, Barn downloads it and prepares the base image for new VMs. Existing VMs keep their macOS until you run
`barn mac recreate NAME --update`. `up` and `start` never change a VM's
macOS.

Recreation keeps disk capacity. A VM with a custom 200 GiB disk needs a base image of the new macOS at that capacity. If prompted, prepare it with `barn mac setup --disk 200G`. Then retry `recreate NAME --update`.
Changes made inside the guest, including its own system updates, are separate
from Barn's base-image lifecycle.

`image prune` lists non-default base images that no VM uses. `--yes` deletes them. `--installers` adds downloaded restore images and partial downloads.
APFS clones share blocks, so `ON DISK` and VM disk figures can include the same space.
Do not add them together to calculate total usage.

```bash
barn mac image prune --installers         # review
barn mac image prune --installers --yes   # delete
```

## Troubleshooting

Start with `barn mac doctor`. It checks the host, component, base image, and every VM. It suggests follow-up commands where available.
Its 40 GiB free-space check is not the entire first-download requirement:
setup also reserves space for the missing portion of the IPSW, about 25 GiB.
`barn mac logs [name]` shows the VM's runtime log: startup, network,
shutdown and Apple Virtualization errors.

| Symptom | What to do |
|---|---|
| `network … overlaps route …` on start | A VPN or another tool now uses that subnet. Run `barn mac configure NAME --subnet auto`. |
| `macOS allows 2 macOS virtual machines at a time` | Stop one of the named VMs, or quit another tool's macOS VM. |
| `ssh mac1` from a third-party client says "No route to host" | macOS Local Network privacy can block the app. Check its access in **System Settings → Privacy & Security → Local Network**, or use `/usr/bin/ssh`. `barn mac ssh` and `exec` use Apple's tools to avoid that restriction. |
| `mac_runner_missing` or `mac_runner_protocol` | Keep the CLI and native component together. Build the complete bundle above. A CLI-only archive cannot supply the missing app; use a release with the native payload or build the complete bundle. |
| Starting fails from an SSH session to the Mac | Run `barn mac` in a terminal of the Mac's desktop session. VMs need the logged-in user's graphical session. Make sure that the login keychain is unlocked. |

Apple Account sign-in inside a VM is unreliable, and USB devices,
snapshots and suspending a VM are not supported.

## Clean up

Inspect the remaining VMs and replace the example names with those
you want to remove:

```bash
barn mac ls                               # check the names first
barn mac destroy mac1 dev                  # confirm deletion of these machines
barn mac image prune --installers --yes     # delete unused images
```

Destroying the last VM also removes its entries from `~/.ssh/config`. Barn retains the default base image for new VMs. To remove every Mac file, including this base image, first destroy all VMs. Remove the Mac SSH integration with `barn mac ssh-config --remove`. Then delete `$BARN_HOME/mac` (default `~/.barn/mac`). Outside that directory, the Mac feature also writes:

- SSH integration in `~/.ssh/config` and the `~/.ssh/barn-mac_config` fragment.
- Desktop window positions in `~/Library/Preferences/com.pgsty.barn.plist`; the 0.9.0 app used `io.pgsty.barn.mac-runner.plist`.
- A short runtime directory under `/tmp`.

Nothing needs sudo.
