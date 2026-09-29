---
title: Linux Quick Start
linkTitle: Linux Quick Start
description: Start an Ubuntu VM, connect over SSH, and expand it into a fixed-IP Linux lab with one inventory.
weight: 10
icon: fa-brands fa-linux
aliases: [/docs/start/lab/, /docs/start/pigsty/, /docs/features/]
---

Create an Ubuntu 24.04 VM on your Mac or Linux host, then expand it into a lab.
For macOS guests, use the separate [Mac guide](../macos/).

## Before you start {#install}

[Install Barn 0.9.0](../installation/) and reserve at least 4 GiB of guest memory
plus room for the host. Run these commands as your normal user in a terminal.
Barn can prepare QEMU and the private network; host changes may require sudo.

## Start and connect

```bash
mkdir -p ~/barn-lab && cd ~/barn-lab
barn up
barn ssh
```

On first use, when no inventory or deployment exists, `up` creates `barn.yml`
with one `meta` node. It prepares host dependencies, downloads and verifies the
image, and waits for SSH. A healthy start ends with a connection command:

```text
  ✓  1 node ready
connect:   barn ssh meta
```

You are now in the guest as `dba`, with key-based SSH and passwordless sudo.
Run `exit` to return to the host before running more Barn commands.

| Default | Value |
|---|---|
| Node and address | `meta`, `10.10.10.10` |
| Image | Ubuntu 24.04, `u24:stable`, native host architecture |
| CPU and memory | 2 vCPUs, 4 GiB |
| Disks | 64 GiB root, 128 GiB test data disk at `/data` |

Disk files grow as data is written. On a fresh, unedited default template,
setup can select another private `/24` if the default is occupied; check the
resulting `barn.yml` and `barn status` for the actual addresses. An existing
template is backed up as `barn.yml.before-network-change`. Explicit `-f` files,
edited templates, and existing deployments retain their subnet.

Barn keeps one Linux deployment per user under `~/.barn`. A different working
directory does not create a second lab: with no local inventory, `up` resumes
the applied deployment. Use `barn status` to see what already exists.

## Inspect and use the VM

```bash
barn status
barn exec meta -- hostname
barn exec meta -- df -h / /data
barn ssh meta
```

`status` describes the VM process. `up` waits for working management SSH and
reports any limited guest features, such as an unavailable data disk or private
network. Repeat `barn up` after fixing a problem or interrupting setup; healthy
VMs keep running. For China-region image downloads, use `barn up --mirror`.

> [!WARNING]
> Data disks are disposable test storage. During guest setup, Barn may reset an
> unrecognized or confirmed damaged filesystem, including a persistent disk.
> Keep valuable data elsewhere. [Disk retention and recovery](../storage/)
> explains the difference between preserving a disk and protecting its contents.

## Customize before the first start

To choose resources before creating a new lab, generate the file first:

```bash
barn init
# Edit barn.yml.
barn validate
barn plan
barn up
```

A complete one-node example:

```yaml
all:
  vars:
    admin_ip: 10.10.10.10
    vm_image: u24
    vm_cpu: 2
    vm_mem: 4GiB
  children:
    nodes:
      hosts:
        10.10.10.10: { nodename: meta }
```

`barn init dual`, `trio`, or `full` generates two, three, or four nodes.
`barn init full -c 10.20.30.0/24` chooses a different subnet. Existing files
are preserved unless you explicitly use `--force`. Configuration and catalog
planning need no host setup; planning an imported `local-*` image also needs
`qemu-img`. See [configuration](../../reference/configuration/) for all fields.

## Add more nodes

In your existing `barn.yml`, add hosts under the same `hosts` mapping:

```yaml
        10.10.10.10: { nodename: meta }
        10.10.10.11: { nodename: node-1 }
        10.10.10.12: { nodename: node-2 }
        10.10.10.13: { nodename: node-3 }
```

Keep your actual subnet and other settings. This is an excerpt, not a replacement
for the entire file. A four-node lab at the defaults needs 16 GiB of guest memory.

```bash
barn plan
barn up
```

With only these additions, the plan lists three new nodes. Barn creates them
without restarting `meta`. Changing an existing node's CPU, memory, or other VM
definition requires an explicit `barn recreate <node>`, which replaces its root
disk. Removing a host from YAML leaves its VM intact until `barn destroy <node>`.

## Stop, resume, and clean up

```bash
barn stop
barn start
```

Both retain the disks. When the lab is no longer needed, run `barn destroy`
and type `destroy` to confirm. It deletes root and non-persistent data disks,
while keeping persistent disks, image cache, keys, and host networking.
[Complete cleanup](../uninstall/) is a separate workflow.

## Next steps

- [Daily operations](../operations/) — access, logs, restart, changes, and removal.
- [Storage and access](../storage/) — transfer files and connect to guest services.
- [Images](../images/) — choose Debian, Rocky Linux, Ubuntu, or a local image.
- [Automation](../automation/) — `setup --yes`, JSON results, guest scripts, and using an existing `pigsty.yml` with Pigsty.

Barn prepares VMs and access. Deploy PostgreSQL or other services separately
with Pigsty; the built-in templates describe machines, not a complete service configuration.
