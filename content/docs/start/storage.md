---
title: Storage, Files, and Service Access
linkTitle: Storage and Access
description: Configure test data disks, understand retention, transfer files, and reach guest services through OpenSSH.
weight: 40
icon: fa-solid fa-hard-drive
---

> [!NOTE]
> **Unreleased**: The changes below to macOS-host 9p sharing, flexible share sources, and guest mount paths require a build containing source commit `27f17bb`; they are not included in Barn 0.9.2. See [Unreleased Changes](/docs/about/unreleased/).

This guide covers disk configuration, file transfer, and service access for Linux labs in **Barn 0.9.2**. It builds on the [Linux Quick Start](../tutorial/) using node `meta` at `10.10.10.10`.

## Configure disks before creating the VM

By default, every Linux node gets a 64 GiB root overlay disk and one 128 GiB non-persistent data disk mounted at `/data`. `vm_disk` sets the root disk capacity in GiB (as an integer like `64` or with a unit like `64GiB`), while `vm_disks` replaces the default data-disk list (`vm_disks: []` disables extra data disks).

For a new single-node lab, save the following inventory as `storage.yml`:

```yaml {title="storage.yml"}
all:
  vars:
    admin_ip: 10.10.10.10
    vm_image: u24@20260926.0.0
  children:
    nodes:
      hosts:
        10.10.10.10:
          nodename: meta
          vm_cpu: 2
          vm_mem: 4096
          vm_disk: 64
          vm_disks:
            - {path: /data, size: 64, fs: auto, persistent: true}
            - {path: /scratch, size: 32, fs: ext4, persistent: false}
```

If `meta` already exists with a different disk layout, `barn up` reports drift; inspect `barn plan` and back up any needed files before running `barn recreate meta` (which replaces root and non-persistent disks).

Validate the inventory, provision the VM, and verify the mounted filesystems:

```bash
barn validate -f storage.yml
barn plan -f storage.yml
barn up -f storage.yml
barn exec meta -- findmnt /data
barn exec meta -- findmnt /scratch
barn exec meta -- df -h / /data /scratch
```

Disk sizes (`size: 64` or `size: 64GiB`) are thin-provisioned virtual capacities that consume host space as data is written. With `fs: auto`, Barn formats new disks as XFS when `mkfs.xfs` is available in the guest and falls back to `ext4` otherwise. Check `barn up` warnings and `findmnt` to confirm that every data disk mounted cleanly.

## What survives each operation

| Operation | Root and non-persistent disks | Persistent disks (`persistent: true`) |
|---|---|---|
| `stop` then `start`, or `restart` | Retained | Retained |
| Repeated `up` on a healthy node | Retained | Retained |
| Compatible `recreate` | Replaced | Retained and reattached |
| Ordinary `destroy` | Deleted | Retained |
| Whole-deployment `destroy --delete-persistent` or `purge` | Deleted | Deleted (including retained disks) |

Barn matches retained persistent disks by disk identity and specification: to reattach a retained disk across `recreate` or after `destroy`, keep the node name, mount `path`, `size`, and `fs` type identical. Barn rejects mismatched retained disks rather than attempting in-place resizing, renaming, or filesystem conversion.

> [!WARNING]
> **Persistent disks are still disposable test storage.** `persistent: true` preserves the disk across ordinary `destroy` and `recreate` runs, but during guest recovery `barn up` will still reformat a filesystem that is unrecognized or confirmed damaged (reporting the reset in `nodes[].repairs`). Transient device absences, failed probes, busy mounts, and host I/O errors never trigger formatting. Keep backups of valuable data on the host.

Newly formatted data filesystems are owned by `root`. You can verify that data written to `/data` persists across a `stop` and `start` cycle:

```bash
barn exec meta -- sudo -n sh -c \
  'printf "retention check\n" > /data/barn-retention.txt'
barn stop meta
barn start meta
barn exec meta -- cat /data/barn-retention.txt
```

For macOS guest folder sharing, see the [macOS VM guide](../macos/#shared-folders).

## Copy files over managed SSH

Export a standalone OpenSSH configuration from the running deployment to use `ssh`, `scp`, or `rsync` directly:

```bash
barn ssh-config > barn-ssh.conf
ssh -F ./barn-ssh.conf barn-meta hostname
scp -F ./barn-ssh.conf ./storage.yml barn-meta:/tmp/storage.yml
scp -F ./barn-ssh.conf barn-meta:/data/barn-retention.txt ./barn-retention.txt
```

The exported fragment points to the current loopback SSH port, deployment key path, and instance-scoped `known_hosts` file without embedding private key material. Regenerate `barn-ssh.conf` if you recreate a node or its loopback port changes, or run `barn ssh-config --install` so `ssh meta` and `scp` work without `-F`.

## Reach services inside the guest

When a service inside the guest listens on the node's fixed private IP (for example, PostgreSQL on `10.10.10.10:5432`) and the guest firewall permits it, your host and peer nodes can connect to that IP directly.

If a service binds only to `127.0.0.1` inside the guest, forward a local host port over SSH:

```bash
ssh -F ./barn-ssh.conf -N \
  -L 127.0.0.1:15432:127.0.0.1:5432 barn-meta
```

While that command remains running, connect local clients on the host to `127.0.0.1:15432` (press `Ctrl-C` to close the tunnel).

SSH aliases (`ssh meta`) apply only to OpenSSH tools. If you also want browsers, `psql`, or other host applications to resolve node names and `vm_alias` entries via `/etc/hosts`, preview and apply the optional hosts integration:

```bash
barn hosts install --json
barn hosts install --yes
```

`barn hosts install --yes` updates `/etc/hosts` on the local host (requesting `sudo` when needed); re-run it after adding nodes or changing IPs.

Barn inventories do not use `vm_ports` or `vm_forwards`—connect via the fixed-IP network or OpenSSH port forwarding. Because management SSH runs over an independent loopback port, `barn ssh` and `-L` tunnels remain usable even if the fixed-IP bridge reports a limitation.

## Host directory sharing

Linux and macOS hosts can share directories with Linux guests through QEMU Virtio-9p. Set `vm_shares` under `all.vars` or a host entry before the first `barn up`:

```yaml {title="barn.yml"}
vm_shares:
  - host: ./src
    guest: /workspace
    readonly: true
```

`host` accepts paths relative to the inventory’s real file, `~/`, and directory symlinks. The directory must exist, be accessible, and not overlap `BARN_HOME`; it need not belong to the Barn user. Multiple guests may write the same tree, with writes coordinated by the user.

Host QEMU and the guest kernel must support 9p. Writable shares also depend on guest permissions; failed writable mounts fall back to read-only with a warning without changing host ownership. After changing existing shares, run `barn recreate <node>`. Native macOS guests use VirtioFS through `barn mac --share`.

See [Linux Configuration](../../reference/configuration/#data-disks) for the complete disk and share schema.
