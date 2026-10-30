---
title: Unreleased Changes
description: Development workflow changes after Barn 0.9.2, covering paths, sharing, node selection, images, and limits.
weight: 15
icon: fa-solid fa-code-branch
---

The changes on this page were implemented on **2026-10-30** in source commit `27f17bb` (`fix: remove unnecessary restrictions from development workflows`). They are **not included in the published 0.9.2 downloads**. To try them, use a [source build](../../start/source-build/) from a checkout containing that commit and check its identity with `barn version`.

For the published release, see [Barn 0.9.2](/blog/release/0.9.2/). Its Apple Silicon package already includes `Barn.app`, and its SSH/exec commands already require `--`.

## Paths {#paths}

`barn init` and `setup` work through directory symlinks. `init -o ./lab/config/barn.yml` also creates missing parent directories. Existing files still require `--force`, and writes never follow or replace an output-file symlink. The [troubleshooting guide](../../start/troubleshooting/#linked-directory) gives a workaround for 0.9.2's `atomic create parent is not a real directory` error.

User-selected paths now accept normal development layouts:

| Input | Resolution |
|---|---|
| `BARN_HOME` | Relative paths, `~/`, and directory symlinks; may also be the working directory |
| Inventory and `provision --script` | Symlinks to regular files; each file retains its 4 MiB limit |
| Linux `vm_shares.host` | Relative to the inventory's real file, or an absolute/`~/` path; directory symlinks work |
| Local image repository and `image import` | Relative paths, `~/`, and symlink inputs |
| `catalogexport` output | Relative paths and `~/`, directory aliases, and automatic parent creation; target must be absent |
| `BARN_MAC_RUNNER` and local `socket_vmnet` archive | Relative paths and `~/`; archive inputs may be symlinks and still undergo digest verification |
{.wide}

CLI-relative paths, including a relative `BARN_HOME`, are interpreted from the current working directory. Use an absolute `BARN_HOME` to reach the same deployment from different directories. Barn still rejects `/` and the user's home directory as data roots and checks the ownership and structure of its managed state. An owned `~/.ssh` directory may be reached through a directory symlink; a linked `~/.ssh/config` is still left for manual `Include` integration.

## Shared folders and mount paths {#sharing}

Linux guests use **QEMU Virtio-9p**, now supported on macOS hosts as well as Linux hosts. QEMU and the guest kernel must support 9p. Native macOS guests continue to use **VirtioFS** through `barn mac --share`.

- Linux share sources use the invoking user's actual filesystem permissions. A directory may belong to another user, overlap another source, or be writable by multiple guests. Coordinate concurrent writes as you would between host processes.
- Source paths support spaces, Unicode, and commas. Linux guest mount paths are normalized and escaped for shell commands and `fstab`, including spaces, Unicode, and shell punctuation.
- Mac share names support spaces and Unicode: valid UTF-8, 1–255 bytes, excluding `.`, `..`, `/`, and ASCII control characters. Share sources may be directory symlinks.
- The eight-share limit is removed. Backend device and host resource limits still apply. Linux sources must not overlap `BARN_HOME`, and mount targets must not overlap each other, system directories, data-disk mounts, or the guest SSH directory.

See [Storage and Access](../../start/storage/) for Linux shares and [Mac Commands](../../reference/mac/) for native macOS shares. Barn never changes host ownership to make a share writable.

## Apply only the selected node changes {#selection}

Explicit selections in `plan`, `up`, `reload`, and `recreate` preserve unselected peers' applied definitions, even if those peers were edited or omitted in the current inventory. Uncreated, unselected nodes do not require image resolution. This allows a multi-node edit to be applied in batches:

```bash
barn plan node-1 -f barn.yml
barn recreate node-1 -f barn.yml
barn plan node-2 -f barn.yml
```

The entire inventory must still parse correctly. Conflicts with applied addresses, aliases, control-node roles, or shared deployment settings are checked before stopping or deleting nodes. Omitting selectors evaluates the whole inventory; removing a YAML entry never deletes its VM. See [Daily Operations](../../start/operations/#selected-nodes).

## Images and development limits {#limits}

| Area | New behavior |
|---|---|
| Linux node count | No separate 20-node ceiling; nodes need distinct usable addresses in the deployment's `/24` and sufficient host resources |
| External inventory hosts | `vm_skip: true` entries may use hostnames or IPv6 keys; managed VMs still use IPv4, and at least one managed node is required |
| Linux capacity strings | Case-insensitive units; `K/M/G/T` and `KiB/MiB/GiB/TiB` are binary, while `KB/MB/GB/TB` remain decimal |
| Provisioning | `--parallel` accepts positive integers and uses at most the selected node count; `--timeout` accepts any positive duration, without the old four-worker or 24-hour ceilings |
| Image size | No 8 GiB artifact ceiling for local imports or catalog artifacts with declared sizes; downloads without a declared size retain the legacy 8 GiB bound |
| Image imports | Arbitrary source filenames; new cache entries use `local/<sha256>.qcow2`, so same-name files with different contents coexist and identical contents reuse the cache |
| Local aliases | No 256-alias ceiling; updates exceeding the 1 MiB registry metadata limit fail before writing. Reimporting an existing alias preserves its old cache path |
| Local repositories | Relative or linked roots and shared writable directories work; `repo.yaml` may be a symlink to a regular file |
| Mac logs | Any positive `--lines` count; requested lines are no longer silently clipped at 1 MiB or 10,000 lines |
| Fallback ports | Try `preferred + n × 10000` through port 65535, rather than stopping after five candidates |
{.wide}

Provisioning still defaults to one worker and a one-hour deadline, with 1 MiB of captured stdout and stderr per node. These user-facing limits are separate from the internal VM startup scheduler. Image digests, declared sizes, `qcow2` structure, retained-disk compatibility, and process identity are still verified. The contributor image pipeline retains its own recipe bounds.
