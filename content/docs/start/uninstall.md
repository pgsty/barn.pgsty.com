---
title: Uninstall and Clean Up
description: Remove Linux and macOS VMs deliberately, then clean up integrations, images, networking, and the application.
weight: 90
icon: fa-solid fa-trash-can
---

Barn manages Linux and macOS VMs separately. **`barn purge` deletes only the Linux deployment. It does not remove Mac VMs.** Keep Barn installed
until you have finished VM and host cleanup.

## Choose what to remove

| Goal | Operation |
|---|---|
| Free running resources, keep disks | `barn stop`; `barn mac stop --all` for Mac VMs |
| Delete a Linux node | `barn destroy <node>` |
| Delete the Linux lab, keep persistent disks | `barn destroy` |
| Delete the Linux lab, including persistent disks and keys | `barn purge` — no confirmation |
| Delete named Mac VMs | `barn mac destroy <name...>` — asks for confirmation |

Use actual names from `barn status` and, if you use Mac guests, `barn mac ls`.
Back up files you need before deleting VMs.

## 1. Remove the machines

To discard the complete Linux lab, including retained persistent disks:

```bash
barn purge
```

Images and host networking remain. If you have not used Mac guests, skip the Mac commands.
Otherwise, inspect the VM list and specify the names to delete. This example deletes `mac1` and `dev`:

```bash
barn mac ls
barn mac destroy mac1 dev
```

Mac destruction removes disks, credentials, and settings, while keeping the
shared base image and host folders.

## 2. Remove optional integrations

Whole-deployment Linux destruction removes its default SSH integration.
Remove any custom fragment and optional hosts-file entries you installed:

```bash
barn ssh-config --remove --name lab
barn hosts uninstall --json
barn hosts uninstall --yes
```

`lab` is an example custom fragment name. The JSON command previews the hosts-file removal. `--yes` applies it. For Mac SSH entries:

```bash
barn mac ssh-config --remove
```

These commands remove only Barn's managed entries, preserving your own SSH
configuration and hosts-file content.

## 3. Prune cached images

```bash
barn image prune --dry-run
barn image prune --yes
```

Linux prune protects the active catalog, applied VMs, and registered local
aliases. It will not necessarily empty the cache after VM deletion.
For Mac images:

```bash
barn mac image prune --installers
barn mac image prune --installers --yes
```

Mac prune keeps base images still used by a VM and the default base image.

## 4. Remove Linux host networking

```bash
barn network uninstall --json
barn network uninstall --yes
```

The JSON command previews removal and may need sudo to inspect protected host state.
After reviewing the plan, use the second command to apply it. The network is shared across
users and cannot be uninstalled while a VM is attached. Mac private networks
disappear when their VMs stop and need no separate uninstall.

## 5. Remove the application and remaining files

For package-manager installations, use the matching command:

```bash {tab="Homebrew" group="uninstall" value="brew"}
brew uninstall barn
```

```bash {tab="Debian / Ubuntu" value="deb"}
sudo apt remove barn
```

```bash {tab="RHEL / Fedora" value="rpm"}
sudo dnf remove barn
```

For the user-scoped installer, inspect the installation directory (default
`~/.local/bin`). Its Barn-owned files are the `barn` and `barn-hosts-helper`
symlinks, `.barn-current`, `.barn-releases/`, and `.barn-install.lock`.
After all VMs have stopped and integrations are removed, remove those exact items.
For a manual archive or source bundle, remove its directory or PATH entry instead.

If you separately installed a native Mac app from source, first stop all Mac guests. Then remove that exact app. The 0.9.0 source uses `Barn Mac.app`. Version 0.9.1 uses `Barn.app`. Inspect the actual
location (for example `~/Applications` or `/Applications`) and any runner path
override. Uninstalling the CLI does not remove an independently copied app.
See [Mac installation](../macos/) for the release/source distinction.

If a manually installed hosts helper remains, its path is
`/opt/barn/libexec/barn-hosts-helper`. Remove it only after uninstalling the
hosts integration and confirming no other Barn user needs it.

**Delete `~/.barn` only after removing both Linux and Mac VMs.** It contains
both kinds of VM state, credentials, persistent disks, and image caches. Linux
`purge` alone is not sufficient. If you set `BARN_HOME`, inspect that exact path
instead. If a VM directory remains or destroy fails, investigate the cause. Do not recursively delete the directory. Deleting just `~/.barn/mac` also requires all Mac
VMs to have been destroyed first.

Barn stores Mac window preferences separately at `~/Library/Preferences/io.pgsty.barn.mac-runner.plist`. Removing them only resets window positions.

Other tools may use QEMU, so keep it until you know it is no longer needed.
