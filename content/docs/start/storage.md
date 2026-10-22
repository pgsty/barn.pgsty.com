---
title: Storage, Files, and Service Access
linkTitle: Storage and Access
description: Configure test data disks, understand retention, transfer files, and reach guest services through OpenSSH.
weight: 40
icon: fa-solid fa-hard-drive
---

This guide uses the **Barn 0.9.1** interface and assumes familiarity with the [Quick Start](../tutorial/).
The disk example below is for a new lab.
Examples use node `meta` and the default subnet; keep your actual names and addresses when adapting an existing inventory.

## Choose disks before creating the VM

By default, every node has a 64 GiB root disk and one 128 GiB non-persistent
data disk at `/data`. An integer `vm_disk` sets the root disk size in GiB. Barn also accepts an explicit unit such as `64GiB`. `vm_disks` replaces the entire data-disk list. `vm_disks: []` disables extra data disks.

For a new single-node lab, save this as `storage.yml`:

```yaml
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

If the same node already exists with a different definition, `up` reports a configuration difference.
Recreation replaces the root and non-persistent disks. Review `plan` and back up needed data before explicitly using `recreate`.

For a new lab, review the configuration, create the VM, and check its mounts:

```bash
barn validate -f storage.yml
barn plan -f storage.yml
barn up -f storage.yml
barn exec meta -- findmnt /data
barn exec meta -- findmnt /scratch
barn exec meta -- df -h / /data /scratch
```

`size: 64` means 64 GiB. `size: 64GiB` is also valid for a data disk. These are
virtual capacities, not immediately allocated host space. Monitor host free
space as the qcow2 files grow. If the guest provides `mkfs.xfs`, `fs: auto` prefers XFS. Otherwise, it uses ext4. A successful VM process start alone does not prove that either data disk mounted. Check the guest result and warnings.

## What survives each operation

| Operation | Root and non-persistent disks | Persistent disks |
|---|---|---|
| `stop` then `start`, or `restart` | retained | retained |
| Healthy repeated `up` | retained | retained |
| Compatible `recreate` | replaced | retained and reattached |
| Ordinary `destroy` | deleted | retained |
| Whole-deployment `destroy --delete-persistent` | deleted | deleted, including retained disks |
| Whole-deployment `purge` | deleted | deleted, including retained disks |

Persistence is based on disk identity and a compatible specification. Keep
the node, mount path, size, and filesystem definition consistent when reusing a
retained disk. It is not an automatic resize, rename, filesystem conversion,
backup, or snapshot facility. Barn rejects incompatible retained disks. Do not edit state files to force attachment.

**A persistent disk is still disposable test storage.** During guest recovery,
`up` may reset an unrecognized or confirmed damaged filesystem and report the
discarded contents. Persistence only controls VM destruction/recreation.
Missing devices, failed probes, busy mounts, and I/O failures do not authorize
formatting. Copy valuable data elsewhere before testing failure recovery.

A freshly formatted data filesystem is owned by root, so this write check uses guest sudo.
You can instead configure directory permissions for your application.
On the lab created above, check that data survives a normal stop and start:

```bash
barn exec meta -- sudo -n sh -c \
  'printf "retention check\n" > /data/barn-retention.txt'
barn stop meta
barn start meta
barn exec meta -- cat /data/barn-retention.txt
```

This checks retention across a VM stop/start. Keep backups outside the lab.
For macOS guest folders, see the [Mac guide](../macos/#shared-folders).

## Copy files with the managed SSH connection

Generate a standalone OpenSSH configuration from the running deployment:

```bash
barn ssh-config > barn-ssh.conf
ssh -F ./barn-ssh.conf barn-meta hostname
scp -F ./barn-ssh.conf ./storage.yml barn-meta:/tmp/storage.yml
scp -F ./barn-ssh.conf barn-meta:/data/barn-retention.txt ./barn-retention.txt
```

The generated fragment selects the current loopback SSH port, deployment key,
and instance host-key identity. Regenerate it after recreation or a management
port change. To add these aliases to your normal SSH configuration, optionally use `barn ssh-config --install`. `-F` works without that integration. The exported file references your deployment key. It does not embed or export the private key.

## Reach a service inside the guest

If a service listens on the guest's fixed IP and the guest firewall allows access, the host can connect to that IP.
For example, you can reach PostgreSQL at `10.10.10.10:5432` after installing and configuring it in the guest.
Starting a VM does not install PostgreSQL.

To reach a service listening only on the guest's loopback address, use OpenSSH
with the generated configuration:

```bash
ssh -F ./barn-ssh.conf -N \
  -L 127.0.0.1:15432:127.0.0.1:5432 barn-meta
```

Keep that host terminal open. Connect a local client to `127.0.0.1:15432`. The guest service must already be listening on port 5432.
Ctrl-C closes the tunnel. If 15432 is occupied, choose another local port.
The explicit loopback bind keeps this example local to your host.

SSH aliases and ordinary hostname resolution are separate. `ssh meta` can work
without `meta` resolving in a browser or database client. To publish the
deployment names and `vm_alias` entries on the host, review and apply the
optional hosts-file integration:

```bash
barn hosts install --json
barn hosts install --yes
```

The first command previews the change. The second may require sudo. Rerun it
after changing node names or addresses. It changes only this host, so another
computer on the LAN does not gain those names or a route to the private subnet.

The inventory has no `vm_ports` or `vm_forwards` setting. Barn rejects unknown `vm_*` keys. Use the fixed-IP network or OpenSSH forwarding. Management
SSH uses a separate loopback connection and can remain available while the
fixed-IP network has a reported limitation.

## Host directory sharing on Linux

For a Linux host, a read-only share can be added before the first `up`:

```yaml
vm_shares:
  - host: /srv/barn-project
    guest: /workspace
    readonly: true
```

Put this under the intended node's variables or `all.vars`. Replace the host path with an
existing real directory owned by your Barn user and accessible to that user.
Read-only shares also require this ownership. Host paths must be
absolute, cannot pass through symlinks, and cannot overlap the Barn data root.
An explicit read-only share is a useful starting point for source files.
Writable shares also depend on guest-user permissions. Barn can fall back to read-only access and report a limitation. It does not change host ownership.

**For Linux guests on a macOS host, omit `vm_shares` and use SSH file transfer.**
A node with such a share cannot start because the tested macOS/QEMU runtime cannot reopen Barn's secured directory handle.

If a source directory or host mount is missing, restore it before retrying `up`; Barn does not create an empty replacement.
Changing an existing node's share definition requires recreation.
See [Configuration](../../reference/configuration/) for the full disk and share constraints.