---
title: Uninstall and Clean Up
description: Safely remove the Farrow deployment, integrations, images, host network, and default state directory.
weight: 60
icon: fa-solid fa-trash-can
---

This page deletes VMs and local data. Inspect the current state and stop if any
Farrow VM must remain:

```bash
farrow st
```

## 1. Remove the deployment

Delete nodes, persistent disks, keys, and deployment state:

```bash
farrow purge
```

This whole-deployment command asks for no confirmation. The image cache and
host network remain. Use the granular,
confirmed `farrow destroy` command instead when preserving persistent disks or
removing selected nodes.

## 2. Remove optional integrations

Whole-deployment destroy already removes the default `farrow` SSH integration.
If you installed a custom fragment name or `/etc/hosts` entries:

```bash
farrow ssh-config --remove --name lab
farrow hosts uninstall
farrow hosts uninstall --yes
```

The first `hosts uninstall` only shows the marker-owned plan. Apply the second
command after confirming its exact target.

## 3. Remove cached images

```bash
farrow image prune --dry-run
farrow image prune --yes
```

Prune removes only images not referenced by applied deployment state and stale
staging files.

## 4. Uninstall host networking

```bash
farrow network uninstall
farrow network uninstall --yes
```

The first command only shows the owned removal plan. Uninstall refuses to run
while any VM remains attached.

## 5. Clean up a source setup

Network uninstall preserves the independently useful hosts helper. Only after
confirming Farrow is no longer needed, remove these exact paths:

```bash
sudo rm -f -- /opt/farrow/libexec/farrow-hosts-helper
sudo rmdir /opt/farrow/libexec /opt/farrow
```

With the default state directory, and only after every earlier step succeeds,
remove the remaining state:

```bash
farrow_state_root="$(cd "$HOME" && pwd -P)/.farrow"
printf 'removing exact state root: %s\n' "$farrow_state_root"
test "$(basename "$farrow_state_root")" = '.farrow'
find "$farrow_state_root" -depth -delete
```

Never substitute `$HOME`, `/`, a workspace root, or an unverified custom
`FARROW_HOME` as that deletion target.

QEMU may be shared by other tools, so keep it by default. On macOS, remove it
only when nothing else needs it:

```bash
brew uninstall qemu
```

Verify the reset:

```bash
farrow st || true
ifconfig bridge100 2>/dev/null || echo 'no Farrow bridge'
test ! -e "$HOME/.farrow" && echo 'no Farrow state'
```

Remove an Archive, Homebrew, DEB, or RPM binary through its installation
channel. The `bin/` directory from a source build is only a checkout artifact,
separate from the host state above.
