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

[Install Barn](../installation/) and make sure your host has at least 4 GiB of free memory for the guest. Run the commands below as your normal user in an interactive terminal: Barn asks once before it changes the host and prompts for `sudo` only for the steps that need it. For unattended CI runs, see [Automation](../automation/). In mainland China, add `--mirror` to the first `barn up` to download images from the China repository at `repo.pigsty.cc`.

## Customize before the first start {#customize}

The default lab is one Ubuntu node using the host architecture: `arm64` on Apple Silicon, `amd64` on Intel/AMD. No architecture setting is needed for normal use; see [image and architecture settings](../../reference/configuration/#image-and-architecture) for cross-architecture selection and precedence. To keep the defaults, skip to [Start and connect](#start). To choose the topology, subnet, or OS image first, write and edit the inventory before the first `barn up`:

1. Generate a starter `barn.yml` (`dual`, `trio`, or `full` creates 2, 3, or 4 nodes; `-c 10.20.30.0/24` selects a custom subnet, and `--image el9` writes one image for every node):

   ```bash
   mkdir -p ~/barn-lab && cd ~/barn-lab
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

3. Validate the YAML and preview the plan:

   ```bash
   barn validate
   barn plan
   ```
{.steps}

`barn validate` and `barn plan` resolve catalog metadata without requiring QEMU or host-network setup, and the next section's `barn up` uses this `barn.yml`. See [Linux Configuration](../../reference/configuration/) for all inventory variables.

## Start and connect {#start}

```bash
mkdir -p ~/barn-lab && cd ~/barn-lab
barn up
```

When neither an inventory file nor an active deployment exists, `barn up` prints a short setup plan before it changes anything. Only the rows that apply appear: `install` lists missing packages (QEMU, UEFI firmware, OpenSSH) and the package manager, `network` names the fixed-IP subnet it prepares, `config` names the one-node `barn.yml` it writes, and `sudo` says which steps need root. On a host that already has QEMU:

```text
  network       prepare 10.10.10.0/24
  config        create /home/alice/barn-lab/barn.yml
  sudo          network (root-owned barn0 bridge)
Continue with this setup? [Y/n]
```

Answer once; `sudo` may then ask for your password. Barn downloads and verifies the base image and waits until SSH is ready:

```text
  ✓  1 node ready
connect:   barn ssh meta
```

If `barn up` stops with an error instead, run `barn doctor` to check the host and `barn logs meta` to read the guest console, fix the reported problem, and run `barn up` again. See [Troubleshooting](../troubleshooting/) for common failures.

Log in to the guest:

```bash
barn ssh
```

`barn ssh` logs you in as `dba` with key-based SSH and passwordless `sudo`. `barn up` also installs SSH aliases, so plain `ssh meta` works too. Type `exit` to return to your host shell; the remaining commands run on the host.

| Default | Value |
|---|---|
| Node and address | `meta` at `10.10.10.10` |
| Image | Ubuntu 24.04 (`u24:stable`, native host architecture) |
| CPU and memory | 2 vCPUs, 4 GiB |
| Disks | 64 GiB root overlay, 128 GiB test data disk mounted at `/data` |

Both disks are thin-provisioned `qcow2` files that grow as data is written. If `10.10.10.0/24` conflicts with an existing route on your machine, first-run setup automatically picks a free private `/24` for a fresh default template—check the generated `barn.yml` and `barn status` for the assigned IP.

> [!NOTE]
> **One Linux deployment per `BARN_HOME`:** Barn stores your active Linux lab under `BARN_HOME` (default `~/.barn`). Changing working directories does not create a second lab; running `barn up` in a directory without an inventory simply resumes the existing deployment. See [One Deployment, No Projects](/blog/design/one-deployment-no-projects/) for the rationale.

## Inspect and use the VM {#inspect}

```bash
barn status
```

```text
NAME  STATE    ADDRESS      IMAGE             CPU   MEMORY
meta  running  10.10.10.10  u24@20261017.0.1    2  4.0 GiB
```

`barn status` reports each node's recorded state, fixed address, image release, and size. Run guest commands from the host by putting `--` before the remote command:

```bash
barn exec meta -- hostname
barn exec meta -- df -h / /data
```

`barn up` verifies management SSH and reports guest-stage warnings such as an unavailable data disk or private interface. If setup is interrupted or you fix a host issue, run `barn up` again—healthy VMs stay running while Barn finishes the remaining steps.

> [!WARNING]
> Data disks are disposable test storage. During guest recovery, `barn up` resets an ext4 or XFS data filesystem when the filesystem checker reports recognized corruption, including on persistent disks. Keep important files on the host; see [Storage and Access](../storage/) for disk retention and recovery boundaries.

## Scale to a multi-node lab {#scale}

To grow the lab to four nodes (16 GiB of guest memory at the default 4 GiB per node), add three host entries under `all.children.nodes.hosts` in your existing `barn.yml`. Use addresses from the same `/24` as `meta`; if first-run setup chose another subnet, use that one:

```yaml {title="barn.yml"}
all:
  vars:
    admin_ip: 10.10.10.10
  children:
    nodes:
      hosts:
        10.10.10.10: { nodename: meta }
        10.10.10.11: { nodename: node-1 }   # new
        10.10.10.12: { nodename: node-2 }   # new
        10.10.10.13: { nodename: node-3 }   # new
```

Preview the change and converge the new nodes:

```bash
barn plan
barn up
```

`barn plan` reports `create: node-1, node-2, node-3`, and `barn up` creates them without restarting `meta`.

If you change an existing node's CPU or memory, apply the change with
`barn resize <node>`; it preserves the VM identity and disks. Image changes
still use `barn recreate <node>`, which replaces its root disk. Removing a host
entry from `barn.yml` leaves the VM untouched on disk until you run
`barn destroy <node>`.

## Stop, resume, and clean up {#cleanup}

```bash
barn stop
barn start
```

Both `stop` and `start` preserve all VM disks. When you finish with the lab, run `barn destroy` and type `destroy` to confirm. Barn deletes the VMs with their root overlays and non-persistent data disks, removes the deployment state and the SSH aliases it installed, and keeps persistent data disks, the deployment keys, cached base images, and the host network. Running `barn up` in `~/barn-lab` again builds a fresh lab from `barn.yml`. For a full teardown, see [Uninstall and Clean Up](../uninstall/).

## Next steps {#next}

- [Daily Operations](../operations/) — Inspect logs, restart nodes, apply inventory changes, and destroy VMs.
- [Storage and Access](../storage/) — Configure persistent disks, copy files with OpenSSH, and reach guest ports.
- [Image Repositories](../images/) — Select Debian, Rocky Linux, Ubuntu, or local `qcow2` images.
- [Automation](../automation/) — Run unattended `setup --yes`, parse `--json` output, run guest scripts, or pair `pigsty.yml` with Pigsty.
{.cards}
