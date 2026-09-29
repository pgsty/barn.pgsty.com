---
title: Quick Start
linkTitle: Quick Start
description: Install Barn 0.9.0, start an Ubuntu lab with up, connect with ssh, and scale from the same inventory.
weight: 10
icon: fa-solid fa-play
aliases: [/docs/start/installation/, /docs/start/upgrade/, /docs/start/lab/, /docs/start/pigsty/, /docs/features/]
---

## Install

Install the current Barn 0.9.0 development version with Homebrew:

```bash
brew install --HEAD pgsty/infra/barn
barn version
```

The [Homebrew formula](https://github.com/pgsty/homebrew-infra/blob/main/Formula/barn.rb)
builds the CLI and hosts-file helper from the main branch. You can also
[build from source](../source-build/) manually.

### Release packages

The 0.9.0 release packages are not published yet. Once available, the
user-scoped installer supports macOS and Linux on arm64 and amd64,
verifies the archive checksum, and needs no sudo to install:

```bash
curl -fLO https://github.com/pgsty/barn/releases/download/v0.9.0/install.sh
chmod +x install.sh
BARN_VERSION=0.9.0 ./install.sh
export PATH="$HOME/.local/bin:$PATH"
barn version
```

The default installation directory is `~/.local/bin`; add the same PATH line
to your shell configuration. A release build should report `0.9.0`. GitHub
excludes prereleases from `/releases/latest`, so specify `BARN_VERSION=0.9.0`.

See [Download and PATH problems](../troubleshooting/#download-and-path-problems)
if downloads fail.

DEB and RPM packages will also be available with the release. The examples
below use amd64; use the corresponding `linux_arm64` asset on ARM64 Linux.

```bash {tab="Debian / Ubuntu" group="install" value="deb"}
barn_release=https://github.com/pgsty/barn/releases/download/v0.9.0
curl -fLO "$barn_release/barn_0.9.0_linux_amd64.deb"
sudo apt install ./barn_0.9.0_linux_amd64.deb
barn version
```

```bash {tab="RHEL / Fedora" value="rpm"}
barn_release=https://github.com/pgsty/barn/releases/download/v0.9.0
curl -fLO "$barn_release/barn_0.9.0_linux_amd64.rpm"
sudo dnf install ./barn_0.9.0_linux_amd64.rpm
barn version
```

The host requirements below apply to Linux guests. macOS guests use the
independent [barn mac](../macos/) command.

### Host requirements

| Host | Native acceleration | Minimum QEMU |
|---|---|---|
| macOS arm64 / amd64 | HVF | 8.2.1 |
| Linux amd64 / arm64 | KVM | 6.2 |

The host also needs `qemu-img`, OpenSSH, and firmware for the selected guest.
Interactive `up` can prepare missing dependencies through Homebrew on macOS
or apt/dnf on supported Linux distributions, and install the fixed-IP network.
Host package and network changes may require sudo; run Barn itself as your
normal user. Linux needs usable KVM and NetworkManager or systemd-networkd.
The dated native validation covers macOS arm64 and Ubuntu amd64; other build
platforms have narrower evidence. See [Status](../../about/status/).

## Boot the first lab

For a first deployment, open a terminal in an empty directory:

```bash
mkdir -p ~/barn-lab && cd ~/barn-lab
barn up
barn ssh
```

Use `exit` to return from the guest to your host terminal before running more
Barn commands.

When no inventory or applied deployment exists, interactive `up` creates
`barn.yml` with one `meta` node. It prepares missing host dependencies and
networking, downloads and verifies the image, starts QEMU, and waits for
management SSH. Host changes are displayed; sudo may ask for your password.
To review the full host plan before applying it, use `barn setup --dry-run`.

> [!NOTE]
> A new directory is not a new lab. State lives in `$BARN_HOME` (default
> `~/.barn`). If a deployment already exists and no inventory is found,
> `up` continues that deployment. Use `barn status` to inspect it first.

The default template resolves to:

| Setting | Default |
|---|---|
| Node / fixed IP | `meta` / `10.10.10.10` |
| Guest image | Ubuntu 24.04, `u24:stable`, native host architecture |
| Login | `dba`, with SSH key authentication |
| CPU / memory | 2 vCPUs / 4 GiB per node |
| Root / data disk | 64 GiB root + 128 GiB at `/data`, not persistent |

Disk sizes are virtual capacities; qcow2 files grow as data is written.
A four-node lab uses 8 vCPUs and 16 GiB of guest memory, in addition to host
resources. Use `barn plan` to inspect totals before starting.

A fresh, unedited built-in template on the default subnet may be moved to an available private `/24`
when setup finds a subnet conflict. An existing template is backed up as
`barn.yml.before-network-change`. Check the resulting `barn.yml` and
`barn status` for actual addresses; explicit `-f` files, edited templates,
and existing deployments keep their selected subnet.

A healthy first start ends with a result such as:

```text
  ✓  1 node ready
connect:   barn ssh meta
```

`barn ssh` selects the control node, `meta` in this template. You can also
name it or run a command directly:

```bash
barn ssh meta
barn exec meta -- hostname
barn st
```

`st` is the alias of `status`; its `running` state describes the VM
process, not a fresh guest-readiness check.

### Continue interrupted setup

Repeat `barn up` to continue interrupted work, retry unfinished guest setup,
or update older guest helpers. Healthy running VMs keep their process and
root disk. A guest with usable management SSH can finish with limitations,
such as a read-only share or unavailable private networking. Review those
messages; automation should inspect `nodes[].warnings` and `nodes[].repairs`
in `barn up --json`, as these limitations still return exit 0.

> [!WARNING]
> Data disks are disposable test storage. `up` can reset an unrecognized or
> confirmed damaged filesystem, **including a persistent disk**, and reports
> discarded data. `persistent` retains disks across destroy/recreate; it does
> not protect corrupt contents during recovery. See [Data disks](../../reference/configuration/#data-disks).

`--no-wait` skips guest readiness, recovery, and metadata refresh; a later
`barn up` completes them. Image downloads support retries and resumption.
Use `barn up --mirror` to prefer the official China repository; see
[Image Repositories](../images/) for image selection and fallback behavior.

## Choose an inventory before booting

This is an alternative to the automatic first run above. In a fresh lab
directory, generate and inspect the configuration before starting:

```bash
barn init
barn validate
barn plan
barn up
```

For the Catalog images used here, `init`, `validate`, and `plan` do not require
QEMU or host-network setup. Planning a registered `local-*` image does require
`qemu-img` to validate its cached bytes.
The default `meta` inventory is:

```yaml
all:
  vars:
    admin_ip: 10.10.10.10
  children:
    nodes:
      hosts:
        10.10.10.10: { nodename: meta }
```

There are four built-in templates:

| Template | Nodes | Default addresses |
|---|---:|---|
| `meta` | 1 | `10.10.10.10` |
| `dual` | 2 | `10.10.10.10`–`10.10.10.11` |
| `trio` | 3 | `10.10.10.10`–`10.10.10.12` |
| `full` | 4 | `10.10.10.10`–`10.10.10.13` |

For example, `barn init full` writes four nodes;
`barn init full -c 10.20.30.0/24` selects another subnet. Existing files are
preserved unless `--force` is explicit. Set `vm_cpu`, `vm_mem`, `vm_image`,
and other fields before the first `up`; see [Configuration](../../reference/configuration/).

### Prepare the host explicitly

`setup` prepares dependencies and networking without starting VMs:

```bash
barn setup --dry-run
barn setup
```

Unlike the preparation performed by `up`, standalone `setup` asks for
confirmation before applying a mutating plan. It reuses the discovered
inventory, or generates `meta` if no file exists. The optional `/etc/hosts`
helper is installed only when `barn hosts install --yes` needs it;
ordinary startup and `barn ssh` do not need that integration.

Downloads honor `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, and `NO_PROXY`,
including lowercase forms. For unattended first setup in an empty directory:

```bash
barn setup --yes
barn up --json
```

`setup --yes` can generate the inventory itself; a separate `init` is needed
only when you want to edit it first. Automation still needs credentials for
any required sudo operation; `--yes` does not supply them. The
[automation guide](../automation/) shows how to retain command results and
check guest limitations before proceeding.

### Use an existing Pigsty inventory

```bash
barn validate -f pigsty.yml
barn plan -f pigsty.yml
barn up -f pigsty.yml
```

Barn reads the documented VM, naming, and login fields and preserves other
Pigsty settings. This starts the virtual machines; installing PostgreSQL or
other Pigsty services is a separate Pigsty operation. The built-in templates
describe VM topology and do not include a complete Pigsty service configuration.
See [Automation and Guest Scripts](../automation/#use-the-lab-with-pigsty)
for the handoff, and [Storage and Access](../storage/) for file transfer and
service connections.

## Scale and operate

To expand the default one-node lab, preserve the existing settings and add
three hosts to `barn.yml`:

```yaml
all:
  vars:
    admin_ip: 10.10.10.10
  children:
    nodes:
      hosts:
        10.10.10.10: { nodename: meta }
        10.10.10.11: { nodename: node-1 }
        10.10.10.12: { nodename: node-2 }
        10.10.10.13: { nodename: node-3 }
```

This example assumes the default subnet; if setup chose another, use that
subnet for every address, including `admin_ip`. Do not overwrite a customized
inventory with `init --force` to expand it.

```bash
barn plan
barn up
barn st
```

With only these additions, the plan lists three nodes to create. `up` creates
them, keeps a running `meta` process, and refreshes guest hosts and control-node
SSH entries. A healthy result is `4 nodes ready`. The embedded 0.9.0 Catalog
resolves `u24:stable` to `u24@20260926.0.0`; a manually updated Catalog may
resolve another version, which appears in `plan` and `status`.

Changing CPU, memory, or other consumed VM fields requires an explicit
`barn recreate <node>`. Removing a YAML entry never deletes its VM. Stop
and resume the lab without recreating disks:

```bash
barn stop
barn start
```

When finished, destroy the deployment:

```bash
barn destroy
```

On a terminal, type `destroy` to confirm. Root and non-persistent data disks
are deleted; cached images, keys, declared persistent disks, and host networking
remain. See [Uninstall and Clean Up](../uninstall/) for complete disposal, or
[Daily Operations](../operations/) for restart, logs, explicit changes, and scale-in.

`barn update` refreshes the image Catalog. To install the Barn application,
use Homebrew or the source build described at the top; release packages
will be available after 0.9.0 is published.
