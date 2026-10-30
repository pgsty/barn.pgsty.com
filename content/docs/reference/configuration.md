---
title: Configuration
description: The Pigsty-compatible inventory fields Barn reads, their defaults, and node-level drift behavior.
weight: 10
icon: fa-solid fa-file-code
aliases: [/docs/concepts/project-model/]
---

> [!NOTE]
> **Unreleased**: The changes below to linked inventories, shared folders, mount paths, size shorthand, skipped external hosts, node counts, and selected-node drift require a build containing source commit `27f17bb`; they are not included in Barn 0.9.2. See [Unreleased Changes](/docs/about/unreleased/).

This reference describes Barn 0.9.2 plus the source changes identified above. Run `barn version` to check your build.

## Discovery

Barn resolves the inventory path by checking an explicit `-f` argument first, then searching the current working directory for `barn.yml`, `barn.yaml`, `pigsty.yml`, and `pigsty.yaml` in that order. All four filenames use the same Pigsty-compatible YAML inventory format.

When no inventory file is present in the current directory, `plan`, `up`, `reload`, and `recreate` fall back to the applied specification stored in `BARN_HOME` (default `~/.barn`) if a deployment already exists. `validate` always requires an inventory file on disk. The file must resolve to a regular file no larger than 4 MiB; symlinks are supported. Relative shared-directory paths resolve beside the inventory’s real file. Barn stops at the first matching filename and reports any parse or validation error directly rather than falling through to the next candidate.

Barn stores applied deployment state in `BARN_HOME`. Renaming the inventory does not change the deployment; use an absolute `BARN_HOME` to address the same deployment across working directories.

## A complete inventory

`barn init [meta|dual|trio|full]` generates a 1-, 2-, 3-, or 4-node topology template. `meta` uses `.10`, and larger templates add `node-1` at `.11`, `node-2` at `.12`, and `node-3` at `.13` (defining VM topology while leaving Pigsty service roles to your upper-layer playbook). Pass `--cidr` to change the `/24` prefix while keeping the host octets, or run `barn init full -o -` to print a template to stdout without writing a file.

```yaml {title="barn.yml"}
all:
  vars:
    admin_ip: 10.10.10.10
    vm_image: u24
    vm_cpu: 2
    vm_mem: 4GiB
    vm_disk: 64
  children:
    lab:
      hosts:
        10.10.10.10: { nodename: meta }
        10.10.10.11:
          nodename: worker
          vm_mem: 8GiB
          vm_disks:
            - { path: /data, size: 128, fs: auto, persistent: true }
```

This inventory defines two managed nodes with `meta` as the control node. Save it as `barn.yml` and inspect the resolved configuration before starting any VMs:

```bash
barn validate -f barn.yml
barn --json validate -f barn.yml
barn plan -f barn.yml
```

`validate` checks YAML syntax, field rules, and image catalog references (accepting `--repo` in Barn 0.9.2) without starting VMs or downloading images. Its JSON output includes `valid`, `source`, `spec_hash`, and `resolved`; if the local image catalog cannot be read, it emits a warning and leaves image selectors unresolved. During `up`, Barn verifies `local-*` imported image bytes, host capabilities, shared directories, networking, and guest SSH readiness.

## What Barn reads

An inventory must contain a top-level `all:` group, from which Barn traverses `hosts` and nested `children` mappings. Barn parses static YAML directly—without evaluating Ansible inventory plugins, Jinja expressions, `group_vars`, or `host_vars`. If the same IPv4 address appears in multiple groups, Barn merges its inherited variables into a single node definition.

Barn reads node IPv4 keys, `nodename`, `admin_ip`, `pg_cluster`, `pg_seq`, `node_admin_username`, `node_admin_uid`, and the `vm_*` variables listed below:

- **Control node**: Barn reads `admin_ip` from `all.vars`. If `admin_ip` is omitted or does not match a managed node, Barn selects the first managed node encountered in YAML traversal order (reading each group's `hosts` before its `children`). Set `admin_ip` explicitly so the control node stays fixed when you reorder groups.
- **Login account**: All nodes share one login username matching `[a-z_][a-z0-9_-]{0,31}`. For the default `dba` user, an explicit `node_admin_uid` must be `88`. For a custom username, Barn verifies that `node_admin_uid` is an integer if present, while the guest assigns the account's UID at creation time.
- **Upper-layer Pigsty fields**: Variables outside Barn's scope—such as `pg_role`, `pg_version`, `repo_*`, and `node_packages`—are ignored by Barn and never trigger VM configuration drift.
- **Inheritance and validation**: Variables inherit along `all.vars` → nested `children.<group>.vars` → host variables. Host-level list variables such as `vm_disks` replace inherited lists wholesale. If two sibling groups at the same depth set conflicting values for the same node, override the variable on the host entry. Unknown `vm_*` keys, invalid types, Jinja templates, duplicate YAML keys, and multi-document YAML streams fail validation with line numbers, violated rules, and spelling suggestions for mistyped `vm_*` names. YAML anchors and `<<` merge keys are supported (explicit keys win, followed by the first mapping in a merge sequence).
- **Skipped nodes**: Hosts with `vm_skip: true` may use hostnames or IPv6 keys and do not participate in the managed `/24`; at least one managed node must remain. Skipping an existing node marks it `missing` in `plan` without destroying it.

## VM variables {#vm-variables}

| Variable | Default | Meaning |
|---|---|---|
| `vm_skip` | `false` | Skip virtualization for this physical or external host |
| `vm_image` | `u24` | Image family, `:channel` reference, or `image@version` selector |
| `vm_version` | unset | Newest numeric version matching this prefix, such as `9` or `9.7` |
| `vm_arch` | `native` | Deployment-wide guest architecture: `native`, `amd64`, or `arm64` |
| `vm_cpu` | `2` | vCPU count (`1`–`256`) |
| `vm_mem` | `4096` | Memory size: bare integer in MiB, or an explicit unit string such as `8GiB` (minimum `512MiB`) |
| `vm_disk` | `64` | Root disk capacity: bare integer in GiB, or an explicit unit string such as `64GiB` |
| `vm_disks` | `[{path: /data}]` | Extra data disks (defaults to one 128 GiB non-persistent disk mounted at `/data`) |
| `vm_alias` | `[]` | Additional guest `/etc/hosts`, SSH config, and optional host `/etc/hosts` aliases |
| `vm_shares` | `[]` | QEMU 9p host-directory shares on Linux and macOS hosts |
{.wide}

An empty host mapping (`10.10.10.10: {}`) is enough to define a complete VM with default settings. There is no separate 20-node ceiling; managed nodes need distinct usable addresses in the configured `/24`.

Bare integers specify MiB for `vm_mem` and GiB for disks. Size strings accept positive integers with case-insensitive units, including `8G`, `512m`, `4gib`, and `64GB`. `K/M/G/T` and `KiB/MiB/GiB/TiB` use binary powers; `KB/MB/GB/TB` retain decimal powers. Fractions such as `1.5GiB` and unitless strings such as `"8192"` remain invalid. `up` still checks that the root disk is at least as large as the base image’s virtual size.

When `vm_image` is omitted, Barn defaults to `u24` (Ubuntu 24.04) from the binary's embedded catalog regardless of any default declared in a custom repository. Built-in aliases such as `ubuntu` → `u24` are normalized against the embedded catalog during inventory parsing, so custom repositories should use their canonical family names in `vm_image` rather than reassigning built-in aliases.

Use `vm_version` when you want to keep the image family and version prefix in separate fields:

```yaml {title="barn.yml"}
vm_image: el9
vm_version: "9.7"
```

If an exact version match exists in the catalog, Barn selects it; otherwise it matches dot-separated numeric prefixes and picks the highest version (`9.7` selects the latest `9.7.*` build, `9` selects the latest `9.x` release, and `9.10` sorts after `9.9`). Use `vm_version` only with a bare family name in `vm_image` (without `:channel` or `@version`).

`vm_arch` applies to the entire deployment and should be set once under `all.vars`. Changing `vm_arch` requires recreating the deployment. On Linux hosts, `barn setup` installs the native QEMU emulator; running a foreign guest architecture requires installing the corresponding `qemu-system-*` binary and UEFI firmware packages.

## Data disks {#data-disks}

```yaml {title="barn.yml"}
vm_disks:
  - path: /data
    size: 128
    fs: auto
    persistent: false
```

Each entry in `vm_disks` configures an additional virtual block device:

- **`path`**: Absolute mount path, normalized automatically; spaces, Unicode, and shell punctuation are supported. Simple paths retain existing disk names; other paths get stable digest-based names. Identities must be unique within a node. System directories and overlapping mount paths remain invalid.
- **`size`**: Disk capacity, defaulting to `128` (128 GiB). Accepts a GiB integer or an explicit size string.
- **`fs`**: Filesystem type—`auto` (default), `xfs`, or `ext4`. On a blank `auto` disk, Barn formats with XFS when `mkfs.xfs` is available in the guest and falls back to ext4 otherwise. Explicit `xfs` or `ext4` settings require that filesystem tool and never fall back. Healthy existing filesystems are mounted as-is.
- **`persistent`**: When `true`, ordinary `barn destroy` and `barn recreate` keep the disk image on the host so the recreated node reattaches it when the disk identity and definition remain compatible. Set `vm_disks: []` to create a node with no extra data disks.

> [!IMPORTANT]
> **Data disks are disposable test storage.** During `up`, if a data disk has an unrecognized or confirmed-corrupt filesystem, Barn formats it to the configured `fs` type and reports the reset in `nodes[].repairs` (including for `persistent: true` disks). Transient probe errors, missing block devices, busy mounts, and host I/O errors never trigger formatting, and root disks or host shares are never auto-formatted.

## Shares

```yaml {title="barn.yml"}
vm_shares:
  - host: ./src
    guest: /src
    readonly: true
```

`vm_shares` mounts host directories into Linux guests through QEMU Virtio-9p on Linux and macOS hosts, with `readonly: true` by default. Host QEMU and the guest kernel must support 9p. The eight-share ceiling is removed; backend device limits still apply. Native macOS guests use VirtioFS through `barn mac --share`.

Shared sources use the invoking user’s actual filesystem permissions:

- `host` accepts absolute paths, `~/`, inventory-relative paths, and directory symlinks. `guest` must be absolute and is normalized automatically; spaces, Unicode, and shell punctuation are accepted, while control characters are rejected.
- Resolved host directories must exist, be accessible, and not overlap `BARN_HOME`; ownership by the invoking user is not required.
- Host sources may overlap and may be shared by multiple readers or writers. Users coordinate concurrent writes. Guest mount targets within one node must not overlap.
- `guest` paths cannot overlap data-disk mounts, system directories, or the login user's `.ssh` directory. Use 9p shares for source code and build artifacts rather than PostgreSQL data directories.
- If a writable share (`readonly: false`) cannot be written by the guest user, Barn mounts it read-only, reports a warning, and leaves host file ownership untouched; fix host permissions and re-run `barn up` to upgrade the mount.
- Changing `vm_shares` on an existing node requires `barn recreate`. Missing host directories during `up` or `start` fail only the affected node, while `restart`, `reload`, and `recreate` verify share paths before stopping running VMs.

## Names and addresses

Barn resolves each node's name from the first available source: explicit `nodename`, `<pg_cluster>-<pg_seq>`, or `node-<last-octet>`. Node names must be unique across the deployment, be 1–63 characters long, contain only lowercase letters, digits, and hyphens, and neither start nor end with `-`. `vm_alias` accepts additional lowercase DNS labels that must be distinct from all node names and other aliases.

All managed nodes in a deployment must belong to a single RFC1918 `/24` subnet: `.1` is the host gateway, `.2`–`.8` are reserved, and `.9`–`.254` are available for nodes. Inside the guest, the fixed-IP NIC carries the configured inventory address (inspectable via `ip -br addr`).

## Drift

Explicit node selectors apply only selected changes: `plan node-1`, `up node-1`, `reload node-1`, and `recreate node-1` retain the applied definitions of unselected peers, even when edited or omitted in the inventory. The entire inventory must still parse correctly. Images for uncreated, unselected nodes are not resolved. Conflicts with applied addresses, aliases, control-node roles, or deployment-wide settings are still rejected.

Barn computes a specification hash for every resolved node:

- `barn up` creates newly added nodes, starts stopped nodes, and retries unfinished guest provisioning on running nodes without restarting their QEMU processes.
- Modifying a node's hardware, image, disk, or share definition requires `barn recreate <node>`. Removing a node from the inventory (or setting `vm_skip: true`) reports the node as `missing` in `plan` without automatically destroying it.
- Changing deployment-wide settings (`vm_arch`, login username, or the `/24` subnet) requires recreating the entire deployment.
- Because `plan` and `up` resolve image channels and version prefixes against the active catalog, running `barn update` can introduce image drift even when `barn.yml` has not changed. Always keep an explicit `nodename` on each host so renaming `pg_cluster` does not turn an existing node into a `missing` old node plus a new node.
