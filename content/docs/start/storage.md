---
title: Storage, Files, and Service Access
linkTitle: Storage and Access
description: Configure test data disks, understand retention, transfer files, and reach guest services through OpenSSH.
weight: 36
icon: fa-solid fa-hard-drive
---

This guide uses the public 0.8.0 interface, also supported by the reviewed 0.9
candidate. Start with the [Quick Start](../tutorial/) before running the
guest-side checks. The examples use node `meta` and the default subnet; retain
your actual names and addresses when adapting an existing inventory.

## Choose disks before creating the VM

Every node has a 64 GiB root disk and, by default, one 128 GiB non-persistent
data disk at `/data`. `vm_disk` sets the root disk size in GiB. `vm_disks`
replaces the entire data-disk list; `vm_disks: []` disables extra data disks.

For a new single-node lab, save this as `storage.yml`:

```yaml
all:
  vars:
    admin_ip: 10.10.10.10
    vm_image: u24@20260911.0.0
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

Then review and create it:

```bash
farrow validate -f storage.yml
farrow plan -f storage.yml
farrow up -f storage.yml
farrow exec meta -- findmnt /data
farrow exec meta -- findmnt /scratch
farrow exec meta -- df -h / /data /scratch
```

`size: 64` means 64 GiB; `size: 64GiB` is also valid for a data disk. These are
virtual capacities, not immediately allocated host space. Monitor host free
space as the qcow2 files grow. `fs: auto` prefers XFS if the guest provides
`mkfs.xfs`, otherwise ext4. A successful VM process start alone does not prove
that either data disk mounted; check the guest result and warnings.

This is a first-creation example. If the same node already exists with another
definition, `up` reports drift. Review `plan` and back up needed data before
explicitly using `recreate`; that replaces the root and non-persistent disks.

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
backup, or snapshot facility. Farrow rejects incompatible retained disks;
do not edit state files to force attachment.

**A persistent disk is still disposable test storage.** During guest recovery,
`up` may reset an unrecognized or confirmed damaged filesystem and report the
discarded contents. Persistence only controls VM destruction/recreation.
Missing devices, failed probes, busy mounts, and I/O failures do not authorize
formatting. Copy valuable data elsewhere before testing failure recovery.

A freshly formatted data filesystem is owned by root. Use guest sudo for this
write check, or deliberately prepare permissions for your application.
To demonstrate normal restart retention on the created lab:

```bash
farrow exec meta -- sudo -n sh -c \
  'printf "retention check\n" > /data/farrow-retention.txt'
farrow stop meta
farrow start meta
farrow exec meta -- cat /data/farrow-retention.txt
```

This checks a VM stop/start, not persistence after a physical-host reboot.
See [Status](../../about/status/) for the native validation boundary.

## Copy files with the managed SSH connection

Generate a standalone OpenSSH configuration from the running deployment:

```bash
farrow ssh-config > farrow-ssh.conf
ssh -F ./farrow-ssh.conf farrow-meta hostname
scp -F ./farrow-ssh.conf ./storage.yml farrow-meta:/tmp/storage.yml
scp -F ./farrow-ssh.conf farrow-meta:/data/farrow-retention.txt ./farrow-retention.txt
```

The generated fragment selects the current loopback SSH port, deployment key,
and instance host-key identity. Regenerate it after recreation or a management
port change. `farrow ssh-config --install` is optional when you want these
aliases available in your normal SSH configuration; `-F` works without that
integration. The exported file references your deployment key; it does not
embed or export the private key.

## Reach a service inside the guest

From the host, a service listening on the guest's fixed IP can be reached on
that IP if its guest firewall and service configuration allow it. For example,
a PostgreSQL server on `10.10.10.10:5432` is a separate service you must install;
Farrow does not install PostgreSQL merely by booting a VM.

To reach a service listening only on the guest's loopback address, use OpenSSH
with the generated configuration:

```bash
ssh -F ./farrow-ssh.conf -N \
  -L 127.0.0.1:15432:127.0.0.1:5432 farrow-meta
```

Keep that host terminal open, then connect a local client to
`127.0.0.1:15432`. The guest service must already be listening on port 5432.
Ctrl-C closes the tunnel. Choose another local port if 15432 is occupied.
The explicit loopback bind keeps this example local to your host.

The inventory has no `vm_ports` or `vm_forwards` setting; an unknown `vm_*`
key is rejected. Use the fixed-IP network or OpenSSH forwarding. Management
SSH uses a separate loopback connection and can remain available while the
fixed-IP network has a reported limitation.

## Host directory sharing on Linux

For a Linux host, a read-only share can be added before the first `up`:

```yaml
vm_shares:
  - host: /srv/farrow-project
    guest: /workspace
    readonly: true
```

Put this under the intended host or `all.vars`. Replace the host path with an
existing real directory owned by your Farrow user and accessible to that user.
Read-only shares also require this ownership. Host paths must be
absolute, cannot pass through symlinks, and cannot overlap the Farrow data root.
An explicit read-only share is a useful starting point for source files.
For writable shares, guest-user permissions also matter; Farrow can fall back
to read-only and report a limitation without changing host ownership.

**Do not add `vm_shares` to a macOS lab using the currently documented runtime.**
The tested macOS/QEMU path cannot reopen the secure directory descriptor and
the affected node cannot start. Use SSH file transfer there. Restoring a missing
host directory or mount lets you retry `up`; Farrow never creates an empty
replacement source. Changing an existing node's share definition requires
explicit recreation. See [Configuration](../../reference/configuration/) for
the full disk and share constraints.
