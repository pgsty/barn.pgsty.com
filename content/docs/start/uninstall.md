---
title: Uninstall and Clean Up
description: Remove Linux and macOS VMs deliberately, then clean up integrations, images, networking, and the application.
weight: 90
icon: fa-solid fa-trash-can
---

Barn manages Linux labs and macOS VMs independently. **`barn purge` removes only the Linux deployment—it does not delete Mac VMs.** Keep the `barn` CLI installed until you have finished removing VMs, integrations, cached images, and host networking.

## Choose what to remove

| Goal | Command |
|---|---|
| Stop running VMs while keeping disks | `barn stop`; `barn mac stop --all` for Mac VMs |
| Delete a single Linux node | `barn destroy <node>` |
| Delete the Linux lab, keeping persistent disks | `barn destroy` |
| Delete the Linux lab, persistent disks, and keys | `barn purge` (no confirmation prompt) |
| Delete named Mac VMs | `barn mac destroy <name...>` (prompts for confirmation) |

Check `barn status` (for Linux nodes) and `barn mac ls` (for Mac VMs), and copy any files you want to keep onto the host before destroying machines.

## Full teardown steps

1. **Destroy Linux and Mac virtual machines**

   To discard the entire Linux lab—including retained persistent disks and deployment keys—run:

   ```bash
   barn purge
   ```

   If you also created macOS VMs, list and destroy them by name:

   ```bash
   barn mac ls
   barn mac destroy mac1 dev
   ```

2. **Remove SSH and `/etc/hosts` integrations**

   Whole-deployment Linux `destroy` / `purge` removes the default `~/.ssh/barn_config` integration automatically. If you installed a custom named SSH fragment, `/etc/hosts` entries, or Mac SSH aliases, remove them:

   ```bash
   barn ssh-config --remove --name lab
   barn hosts uninstall --json
   barn hosts uninstall --yes
   barn mac ssh-config --remove
   ```

   These commands remove only Barn's managed blocks, leaving your personal `~/.ssh/config` and `/etc/hosts` entries intact.

3. **Prune cached images**

   Preview and delete cached Linux and macOS images:

   ```bash
   barn image prune --dry-run
   barn image prune --yes
   barn mac image prune --installers
   barn mac image prune --installers --yes
   ```

4. **Uninstall Linux host networking**

   Preview and remove the shared Linux host network (requires all Linux VMs to be stopped and removed first; Mac VM networks tear down automatically when the VM stops):

   ```bash
   barn network uninstall --json
   barn network uninstall --yes
   ```

5. **Uninstall the Barn application and remaining state**

   If you installed Barn through a package manager, remove the package:

   ```bash {tab="Homebrew" group="uninstall" value="brew"}
   brew uninstall barn
   ```

   ```bash {tab="Debian / Ubuntu" group="uninstall" value="deb"}
   sudo apt remove barn
   ```

   ```bash {tab="RHEL / Fedora" group="uninstall" value="rpm"}
   sudo dnf remove barn
   ```

   - **User-scoped `install.sh`**: Remove `barn`, `barn-hosts-helper`, `.barn-current`, `.barn-releases/`, and `.barn-install.lock` from `~/.local/bin` (and remove the `PATH` entry from your shell rc file).
   - **Manual archive or source build**: After stopping all Mac guests, remove the extracted release directory, `bin/mac`, or any copied `Barn.app` (`Barn Mac.app` in `0.9.0`), plus `~/Library/Preferences/com.pgsty.barn.plist` (`io.pgsty.barn.mac-runner.plist` in `0.9.0`).
   - **Manually installed hosts helper**: If `/opt/barn/libexec/barn-hosts-helper` was installed manually and no other user on the host uses Barn, remove it after running `barn hosts uninstall --yes`.
{.steps}

> [!WARNING]
> **Delete `~/.barn` (or your custom `BARN_HOME`) only after destroying both Linux and Mac VMs.** `~/.barn` holds active VM state, keys, persistent disks, and base images for both workflows; if a VM is still running or `destroy` fails, resolve the error with `barn status` / `barn mac ls` before deleting the directory.
