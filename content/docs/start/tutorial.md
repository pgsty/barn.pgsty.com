---
title: Linux Quick Start
linkTitle: Linux Quick Start
description: Start an Ubuntu VM, connect over SSH, and expand it into a fixed-IP Linux lab with one inventory.
weight: 10
icon: fa-brands fa-linux
aliases: [/docs/start/lab/, /docs/start/pigsty/, /docs/features/]
---

Create an Ubuntu 24.04 VM on your Mac or Linux host, connect over SSH, and scale it into a multi-node fixed-IP lab from a single YAML inventory. For macOS guests on Apple Silicon, see the [macOS VM guide](../macos/).

## Before you start {#install}

[Install Barn 0.9.2](../installation/) and make sure your host has at least 4 GiB of free memory for the guest. Run all commands as your normal user in an interactive terminal—Barn prepares QEMU and the private host network automatically, prompting for `sudo` only when a host change requires administrator privileges. (For non-interactive CI runs, see [Automation](../automation/).)

## Start and connect

```bash
mkdir -p ~/barn-lab && cd ~/barn-lab
barn up
barn ssh
```

When neither an inventory file nor an active deployment exists, `barn up` generates a starter `barn.yml` with one `meta` node, configures any missing host dependencies, downloads and verifies the base image, and waits until SSH is ready:

```text
  ✓  1 node ready
connect:   barn ssh meta
```

`barn ssh` logs you into the guest as `dba` with key-based SSH and passwordless `sudo`. Type `exit` to return to your host shell before running further `barn` commands.

| Default | Value |
|---|---|
| Node and address | `meta` at `10.10.10.10` |
| Image | Ubuntu 24.04 (`u24:stable`, native host architecture) |
| CPU and memory | 2 vCPUs, 4 GiB |
| Disks | 64 GiB root overlay, 128 GiB test data disk mounted at `/data` |

Both disks are thin-provisioned `qcow2` files that grow as data is written. If `10.10.10.0/24` conflicts with an existing route on your machine, first-run setup automatically picks a free private `/24` for a fresh default template—check the generated `barn.yml` and `barn status` for the assigned IP.

> [!NOTE]
> **One Linux deployment per `BARN_HOME`:** Barn stores your active Linux lab under `BARN_HOME` (default `~/.barn`). Changing working directories does not create a second lab; running `barn up` in a directory without an inventory simply resumes the existing deployment. See [One Deployment, No Projects](/blog/design/one-deployment-no-projects/) for the rationale.

## Inspect and use the VM

```bash
barn status
barn exec meta -- hostname
barn exec meta -- df -h / /data
barn ssh meta
```

`barn status` inspects the running VM processes, while `barn up` verifies management SSH and reports any guest-stage warnings (such as an unavailable data disk or private interface). If setup is interrupted or you fix a host issue, run `barn up` again—healthy VMs stay running while Barn converges unfinished steps. In mainland China, pass `barn up --mirror` to pull images from the China mirror.

> [!WARNING]
> Data disks are disposable test storage. During guest recovery, `barn up` may reformat an unrecognized or confirmed damaged test filesystem (including persistent disks). Keep important files on the host; see [Storage and Access](../storage/) for disk retention and recovery boundaries.

## Customize before the first start

If you want to customize the topology, subnet, or OS image before starting your first VM, generate and inspect the inventory first:

1. Generate a starter `barn.yml` (`dual`, `trio`, or `full` creates 2, 3, or 4 nodes; `-c 10.20.30.0/24` selects a custom subnet, and `--force` overwrites an existing file):

   ```bash
   barn init
   ```

2. Edit `barn.yml` to choose your image and resources:

   ```yaml {title="barn.yml"}
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

3. Validate the YAML syntax, preview the execution plan, and bring up the lab:

   ```bash
   barn validate
   barn plan
   barn up
   ```
{.steps}

`barn validate` and `barn plan` resolve catalog metadata without requiring QEMU or host-network setup. See [Linux Configuration](../../reference/configuration/) for all inventory variables.

## Scale to a multi-node lab

To expand a running single-node lab into a four-node cluster (requiring 16 GiB of total guest memory at the default 4 GiB per node), add the new host entries under `all.children.nodes.hosts` in your existing `barn.yml`:

```yaml {title="barn.yml"}
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
        10.10.10.11: { nodename: node-1 }
        10.10.10.12: { nodename: node-2 }
        10.10.10.13: { nodename: node-3 }
```

Preview the diff and converge the new nodes:

```bash
barn plan
barn up
```

`barn plan` shows three `create` actions, and `barn up` provisions `node-1` through `node-3` without restarting `meta`.

If you change an existing node's CPU, memory, or image, apply the change with `barn recreate <node>` (which replaces its root disk). Removing a host entry from `barn.yml` leaves the VM untouched on disk until you run `barn destroy <node>`.

## Stop, resume, and clean up

```bash
barn stop
barn start
```

Both `stop` and `start` preserve all VM disks. When you finish with the lab, run `barn destroy` and type `destroy` to confirm—Barn deletes the VMs along with their root overlays and non-persistent data disks, while retaining persistent disks, cached base images, SSH keys, and host networking. For a full teardown, see [Uninstall and Clean Up](../uninstall/).

## Next steps

- [Daily Operations](../operations/) — Inspect logs, restart nodes, apply inventory changes, and destroy VMs.
- [Storage and Access](../storage/) — Configure persistent disks, copy files with OpenSSH, and reach guest ports.
- [Image Repositories](../images/) — Select Debian, Rocky Linux, Ubuntu, or local `qcow2` images.
- [Automation](../automation/) — Run unattended `setup --yes`, parse `--json` output, run guest scripts, or pair `pigsty.yml` with Pigsty.
{.cards}
