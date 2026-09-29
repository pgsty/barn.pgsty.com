---
title: Uninstall and Clean Up
description: Safely remove the Barn deployment, integrations, images, host network, and default state directory.
weight: 60
icon: fa-solid fa-trash-can
---

This page deletes VMs and local data. Inspect the current state and stop if any
Barn VM must remain:

```bash
barn st
```

## 1. Remove the deployment

Delete nodes, persistent disks, keys, and deployment state:

```bash
barn purge
```

This whole-deployment command asks for no confirmation. The image cache and
host network remain. Use the granular,
confirmed `barn destroy` command instead when preserving persistent disks or
removing selected nodes.

## 2. Remove optional integrations

Whole-deployment destroy already removes the default `barn` SSH integration.
If you installed a custom fragment name or `/etc/hosts` entries:

```bash
barn ssh-config --remove --name lab
barn hosts uninstall --json
barn hosts uninstall --yes
```

Without `--yes`, the `--json` command only shows the marker-owned plan. Apply
the `--yes` command after checking its target. In Barn 0.9.0, ordinary terminal output asks `[y/N]` and applies removal
after confirmation. Barn reads the hosts plan without sudo; applying
the change still needs privilege.

## 3. Remove cached images

```bash
barn image prune --dry-run
barn image prune --yes
```

Prune removes unreferenced cached images and stale staging files. It protects
images referenced by deployment state, the active Catalog, and registered local
aliases, so it is not a complete cache wipe. The optional final state-directory
cleanup below removes the remaining cache too.

## 4. Uninstall host networking

```bash
barn network uninstall --json
barn network uninstall --yes
```

The first JSON command only shows the owned removal plan, although sudo may
be needed to read protected network state. Uninstall refuses while any VM
remains attached. The network is shared across users; removing your deployment
does not establish that another user's VMs have stopped.

## 5. Clean up a source setup

Network uninstall preserves the independently useful hosts helper. Only after
confirming Barn is no longer needed, remove these exact paths:

```bash
sudo rm -f -- /opt/barn/libexec/barn-hosts-helper
sudo rmdir /opt/barn/libexec /opt/barn
```

With the default state directory, and only after every earlier step succeeds,
remove the remaining state:

```bash
(
  set -eu
  test -z "${BARN_HOME:-}"
  barn_state_root="$(cd "$HOME" && pwd -P)/.barn"
  test ! -L "$barn_state_root"
  if test -d "$barn_state_root"; then
    printf 'removing exact state root: %s\n' "$barn_state_root"
    find "$barn_state_root" -depth -delete
  fi
)
```

This snippet stops if `BARN_HOME` is set or the default path is a symlink.
Review a custom state directory separately; never substitute `$HOME`, `/`, a
workspace root, or an unverified path. After deletion, avoid running lifecycle
commands just to check that the directory is gone: they may recreate lock
directories.

QEMU may be shared by other tools, so keep it by default. On macOS, remove it
only when nothing else needs it:

```bash
brew uninstall qemu
```

Verify network removal and the default state directory:

```bash
barn network status --json
test ! -e "$HOME/.barn" && echo 'no Barn state'
```

An uninstalled network is expected to report an absent/not-ready finding;
inspect the result rather than requiring a zero exit code. Do not use
`bridge100` disappearing as proof: macOS chooses its bridge name and may use
other vmnet bridges for unrelated software.

Remove an Archive, Homebrew, DEB, or RPM binary through its installation
channel. The `bin/` directory from a source build is only a checkout artifact,
separate from the host state above.
