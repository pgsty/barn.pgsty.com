---
title: macOS Virtual Machines
linkTitle: macOS VMs
description: Run macOS 27 virtual machines on Apple Silicon with farrow mac — create, connect, share files and the clipboard, and clean up.
weight: 38
icon: fa-brands fa-apple
---

> [!IMPORTANT]
> **Unreleased.** `farrow mac` is not part of public 0.8.0, its packages, or
> the public source repository yet. This guide describes the development tree
> validated on 2026-09-29; see [Status](../../about/status/#macos-guests).
> Commands and output may still change before it ships.

`farrow mac` creates and runs macOS virtual machines on an Apple Silicon Mac.
Each machine is a clean, disposable macOS with an administrator account,
passwordless sudo, pinned SSH keys and a fixed address — for testing, building
and reproducing macOS-specific behavior. It uses Apple's Virtualization
framework directly and needs no administrator access.

Mac machines are separate from the Linux lab. They never read `farrow.yml`,
never join a Pigsty inventory, and keep their files under `$FARROW_HOME/mac`
(default `~/.farrow/mac`). Linux `destroy` and `purge` leave them alone.

## Requirements

- An Apple Silicon Mac running **macOS 27 or later**, with a user logged in to
  its desktop. Guests also run macOS 27.
- About **65 GiB** free for the first machine: the 25 GiB restore image from
  Apple (kept until you prune it), the 27 GiB installed base, and room to
  start. Each machine then grows with its own changes up to its disk capacity,
  100 GiB by default.
- **Xcode 27** to build the Mac component from source, until a release
  includes it.
- No sudo. Every machine, its network and its desktop run as your user.

Apple allows **two macOS virtual machines running at a time** on one Mac,
including those of other tools and macOS installation itself. You can create
more machines and start any two.

## Build the Mac component

From a Farrow source checkout that contains `farrow mac`:

```bash
make mac-build
export PATH="$PWD/bin/mac:$PATH"
farrow mac doctor
```

`bin/mac` holds the CLI, `Farrow Mac.app` (the native component that runs the
machines and their desktops) and the guide; keep them together. The build is
signed ad hoc for local use. `doctor` checks macOS, the component, and free
disk space:

```text
CHECK           RESULT  DETAIL
component       ok      /path/to/farrow/bin/mac/Farrow Mac.app/Contents/MacOS/farrow-mac-runner
virtualization  ok      macOS 27.0.0 on Apple Silicon; virtualization supported
disk            ok      549.8 GiB free
data            ok      no Mac machines yet; farrow mac up creates the first
```

## Create your first machine

```bash
farrow mac up
```

On a Mac without a prepared macOS, `up` first shows what it needs and asks:

```text
→ macOS 27.0 (26A428) is not prepared on this Mac yet.
download:  24.8 GiB from Apple (updates.cdn-apple.com)
then:      install macOS once into a reusable base (about 20 minutes)
free:      551.2 GiB
Download macOS from Apple now? [Y/n]
```

After you confirm, Farrow:

1. **Downloads the restore image from Apple only** and verifies it against
   Apple's published SHA-256. An interrupted download resumes where it
   stopped.
2. **Installs macOS once** into an unbooted *base*. Installation uses one of
   the two macOS VM slots while it runs.
3. **Creates `mac1`** as a copy-on-write clone of the base, boots it, creates
   your account, and waits until SSH and sudo work.

```text
  ✓  mac1 created and ready · macOS 27.0 (26A428) · alice@10.10.20.10
shell:     farrow mac ssh mac1
desktop:   farrow mac open mac1
```

Every later machine reuses the base and is ready in tens of seconds; a machine
created from a prepared base on the validation host was ready in 22 seconds.

If you already have Apple's restore image, pass it instead of downloading.
On the same APFS volume Farrow clones it without copying; elsewhere it verifies
and uses the file where it is:

```bash
farrow mac up --ipsw ~/Downloads/UniversalMac_27.0_26A428_Restore.ipsw
```

Without a terminal, for example in a script, `up` needs `--yes` to download:
it refuses rather than silently fetching 25 GiB. `farrow mac setup` prepares
the base ahead of time without creating a machine.

## Work in the machine

### Shell and commands

```bash
farrow mac ssh                                  # interactive shell
farrow mac exec -- sw_vers                      # one command
farrow mac ssh -- 'id; sudo -n true && echo sudo works'
```

```text
ProductName:		macOS
ProductVersion:		27.0
BuildVersion:		26A428
```

The account has your macOS user name (choose another with `--user` when
creating the machine) and passwordless sudo. `ssh` passes a command line to the
guest shell like plain ssh; `exec` keeps argument boundaries. Both return the
guest's exit status, and `--json` records stdout, stderr and the exit code:

```bash
farrow --json mac exec -- sh -c 'echo out; exit 3'
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

The JSON above is shortened; the [Mac reference](../../reference/mac/#json-output)
lists every field.

### Desktop

```bash
farrow mac open
```

The desktop opens in a native window sized to your screen. Resizing the window
changes the guest resolution, and **View → Enter Full Screen** works as usual.
Closing the window keeps the machine running; `open` brings it back, and starts
a stopped machine first. Keyboard shortcuts go to the guest while its window is
focused, so the host commands live in the menu bar:

| Menu | Action |
|---|---|
| **Machine → Share Clipboard** | turn clipboard sharing on or off for this session |
| **Machine → Restart…** | restart macOS in the guest |
| **Machine → Shut Down…** | shut down normally, like `farrow mac stop` |
| **Window → Keep Running in Background** | hide the window; the machine keeps running |
| **Farrow Mac → Quit Farrow Mac…** | choose to keep the machine running or shut it down |

The login password, needed for the lock screen and administrator prompts in the
desktop, is random per machine. Copy it without printing it:

```bash
farrow mac password --copy
```

### Clipboard

Plain text follows your focus. What you copied on the Mac is available in the
guest when you click into its window, and what you copy in the guest comes back
when you switch to another app. It travels over the machine's own SSH
connection; nothing is installed in the guest. Items that password managers
mark as concealed never leave the Mac. Images and files are not shared.

Turn it off for a machine with `farrow mac configure mac1 --clipboard off`;
the setting applies from the machine's next start.

### Shared folders

Share Mac folders when creating a machine. The guest mounts them under
`/Volumes/My Shared Files/<name>`:

```bash
farrow mac up dev --share ~/src --share docs=~/Documents:ro
farrow mac exec dev -- ls "/Volumes/My Shared Files"
```

The name defaults to the folder's last path component; `:ro` makes a share
read-only. A share must be an existing directory, not a symlink; Farrow never
creates or deletes shared folders. To change shares later, stop the machine
and use `configure`:

```bash
farrow mac stop dev
farrow mac configure dev --share data=/Volumes/Work/data --unshare docs
farrow mac start dev
```

macOS guests can show stale file contents for a short while after the Mac
changes a shared file. Use SSH or `exec` when you need an immediately
consistent view.

### SSH from other tools

When the first machine becomes ready, Farrow adds one marked `Include` to
`~/.ssh/config`, so `ssh mac1`, `scp`, `rsync`, and editors with Remote-SSH
reach every machine by name, with its own key and pinned host key:

```bash
ssh mac1 'uptime'
rsync -a ./project/ mac1:project/
farrow mac ssh-config              # print the entries
farrow mac ssh-config --remove     # remove only what Farrow added
```

Lifecycle commands keep the entries current. A `~/.ssh/config` managed by a
dotfile tool through a link is never edited; Farrow prints the `Include` line
to add instead.

## Several machines

Give each machine a name. Creation options apply only to a new machine:

```bash
farrow mac up dev --cpu 8 --memory 16G
farrow mac ls
```

```text
NAME  STATE    ADDRESS      SSH    USER   OS          CPU  MEMORY  DISK                 SHARED
dev   running  10.10.21.10  ready  alice  macOS 27.0    8  16 GiB  504.0 MiB / 100 GiB
mac1  running  10.10.20.10  ready  alice  macOS 27.0    4   8 GiB  4.7 GiB / 100 GiB    src
limit:     2 of 2 macOS VMs are running; stop one before starting another
```

Names use lowercase letters, digits and inner hyphens and start with a letter.
A command without a name acts on the only machine, or on `mac1`, and asks you
to choose when that is ambiguous. `DISK` shows the space the machine uses now
and its capacity. Capacity belongs to the base: a `--disk` other than the
prepared base's installs another base first, which needs the restore image
again.

Each machine has its own private network: `mac1` gets `10.10.20.10`, later
machines the next free `/24`, avoiding your LAN, VPNs and the Linux lab.
Machines reach the internet and the Mac, but not each other. With two machines
running, a third is refused before anything is created, naming a machine to
stop:

```bash
farrow mac up build --user ci
```

```text
error: dev and mac1 are running; macOS allows 2 macOS virtual machines at a time
next: farrow mac stop mac1
```

## Everyday lifecycle

```bash
farrow mac stop dev               # shut down through macOS
farrow mac start dev              # boot and wait for SSH
farrow mac restart dev            # stop, then start, applying changes
farrow mac stop --all             # every machine
```

`stop` shuts down normally. A machine still running after two minutes is
powered off, and the result says so. `stop --force` powers off at once, like
holding a power button; unsaved work in the guest is lost.
`start --recovery` boots macOS Recovery and shows its desktop.

`up` never reconfigures an existing machine. If you pass an option that
differs, it refuses and names the command to use:

```text
error: dev already exists, so --cpu would not apply; its configuration and data were preserved
next: farrow mac configure dev --cpu 4
```

`configure` changes CPUs, memory, shared folders and the network while the
machine is stopped, and clipboard sharing at any time. Changes apply at the next
start:

```bash
farrow mac stop dev
farrow mac configure dev --cpu 6 --memory 12G --subnet auto
farrow mac start dev
```

`recreate` replaces a machine with a fresh macOS from the base, keeping its
name, account, resources, shared folders and address. `destroy` deletes
machines. Both describe what they delete and ask you to type the command name;
`--force` confirms without a terminal.

```bash
farrow mac recreate dev
farrow mac destroy dev build
```

| Operation | Guest disk and apps | Settings, address, account |
|---|---|---|
| `stop`/`start`, `restart`, repeated `up` | kept | kept |
| `configure` | kept | changed as requested |
| `recreate` | replaced with a fresh macOS | kept; new password and SSH keys |
| `destroy` | deleted | deleted |

The shared base is never changed by any of these, and is kept when machines are
destroyed.

## macOS versions and disk space

```bash
farrow mac image ls
```

```text
KIND  OS          BUILD   STATE  ON DISK   CAPACITY  USED BY
base  macOS 27.0  26A428  ready  26.7 GiB  100 GiB   mac1,default
```

Updates are explicit. `farrow mac image update` asks Apple for the newest
macOS 27, downloads it after you confirm, and makes it the base for new
machines. Existing machines keep their macOS until you run
`farrow mac recreate NAME --update`. `up` and `start` never change a machine's
macOS.

`image prune` lists bases that no machine uses and that are not the default,
and deletes them with `--yes`; `--installers` adds downloaded restore images.
APFS clones share blocks, so `ON DISK` and machine disk figures are not
exclusive usage and should not be added up.

```bash
farrow mac image prune --installers         # review
farrow mac image prune --installers --yes   # delete
```

## Troubleshooting

Start with `farrow mac doctor`; it checks the host, the component, the base
and every machine, and prints a `next:` command for each failure.
`farrow mac logs [name]` shows the machine's runtime log: startup, network,
shutdown and Apple Virtualization errors.

| Symptom | What to do |
|---|---|
| `network … overlaps route …` on start | A VPN or another tool now uses that subnet. Run `farrow mac configure NAME --subnet auto`. |
| `macOS allows 2 macOS virtual machines at a time` | Stop one of the named machines, or quit another tool's macOS VM. |
| `ssh mac1` from a third-party client says "No route to host" | macOS Local Network privacy blocks that app from private networks. Allow it in **System Settings → Privacy & Security → Local Network**, or use `/usr/bin/ssh`. `farrow mac ssh` and `exec` always use Apple's tools and are not affected. |
| `the Farrow Mac component is not installed` or `speaks protocol …` | Keep `farrow` and `Farrow Mac.app` from the same build together; rebuild with `make mac-build`. |
| Starting fails from an SSH session to the Mac | Run `farrow mac` in a terminal of the Mac's desktop session: machines need the logged-in user's session and unlocked login keychain. |

Apple Account sign-in inside a virtual machine is unreliable, and USB devices,
snapshots and suspending a machine are not supported.

## Clean up

```bash
farrow mac destroy --force mac1 dev           # delete machines
farrow mac image prune --installers --yes     # delete unused images
```

Destroying the last machine also removes its entries from `~/.ssh/config`. The
default base stays for new machines; to remove every Mac file including it,
destroy all machines and then delete `$FARROW_HOME/mac` (default
`~/.farrow/mac`). Outside that directory Farrow writes only its
`~/.ssh/config` entries, the desktop window positions in
`~/Library/Preferences/io.pgsty.farrow.mac-runner.plist`, and a short runtime
directory under `/tmp`. Nothing needs sudo.
