---
title: Uninstall and Clean Up
description: Remove Linux and macOS VMs deliberately, then clean up integrations, images, networking, and the application.
weight: 90
icon: fa-solid fa-trash-can
---

Barn manages Linux and macOS machines separately. **`barn purge` deletes only
the Linux deployment; it does not remove Mac machines.** Keep Barn installed
until you have finished VM and host cleanup.

## Choose what to remove

| Goal | Operation |
|---|---|
| Free running resources, keep disks | `barn stop`; `barn mac stop --all` for Mac machines |
| Delete a Linux node | `barn destroy <node>` |
| Delete the Linux lab, keep persistent disks | `barn destroy` |
| Delete the Linux lab, including persistent disks and keys | `barn purge` — no confirmation |
| Delete named Mac machines | `barn mac destroy <name...>` — asks for confirmation |

Use actual names from `barn status` and, if you use Mac guests, `barn mac ls`.
Back up files you need before deleting machines.

## 1. Remove the machines

To discard the complete Linux lab, including retained persistent disks:

```bash
barn purge
```

Images and host networking remain. For Mac machines, inspect the list and
explicitly name those to delete; the following example deletes `mac1` and `dev`:

```bash
barn mac ls
barn mac destroy mac1 dev
```

Mac destruction removes disks, credentials, and settings, while keeping the
shared base and host folders. Skip Mac commands if you have not used Mac guests.

## 2. Remove optional integrations

Whole-deployment Linux destruction removes its default SSH integration.
Remove any custom fragment and optional hosts-file entries you installed:

```bash
barn ssh-config --remove --name lab
barn hosts uninstall --json
barn hosts uninstall --yes
```

`lab` is an example custom fragment name. The JSON command previews the
hosts-file removal; `--yes` applies it. For Mac SSH entries:

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

Mac prune keeps bases still used by a machine and the default base.

## 4. Remove Linux host networking

```bash
barn network uninstall --json
barn network uninstall --yes
```

The JSON command previews removal; it may need sudo to inspect protected
host state. Apply it after reviewing the plan. The network is shared across
users and cannot be uninstalled while a VM is attached. Mac private networks
disappear when their machines stop and need no separate uninstall.

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
Remove those exact items after all VMs have stopped and integrations are removed.
For a manual archive or source bundle, remove its directory or PATH entry instead.

If a manually installed hosts helper remains, its path is
`/opt/barn/libexec/barn-hosts-helper`. Remove it only after uninstalling the
hosts integration and confirming no other Barn user needs it.

**Delete `~/.barn` only after removing both Linux and Mac machines.** It contains
both kinds of VM state, credentials, persistent disks, and image caches. Linux
`purge` alone is not sufficient. If you set `BARN_HOME`, inspect that exact path
instead. A remaining machine directory or failed destroy needs investigation,
not recursive deletion. Deleting just `~/.barn/mac` also requires all Mac
machines to have been destroyed first.

The Mac window preferences are stored separately at
`~/Library/Preferences/io.pgsty.barn.mac-runner.plist`; removing them only resets
window positions. QEMU may be used by other tools, so keep it unless you know
it is no longer needed.
