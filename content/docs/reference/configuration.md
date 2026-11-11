---
title: Configuration
description: The Pigsty-compatible inventory fields Barn reads, their defaults, and node-level drift behavior.
weight: 10
icon: fa-solid fa-file-code
aliases: [/docs/concepts/project-model/]
---

This reference covers Barn 1.1.0 and explicitly marked development changes checked on 2026-11-11. Local main `6ab0cd5` defaults to 1 vCPU and 2 GiB and adds `vm_scale` and specification overrides; `vm_hosts` and `hosts install -f` are additional uncommitted working-tree changes. Released 1.1.0 defaults to 2 vCPUs and 4 GiB and has none of those additions. See the [version baseline](../commands/#versions) and check your build with `barn version` and `--help`.

## Discovery {#discovery}

Barn resolves the inventory path by checking an explicit `-f` argument first, then searching the current working directory for `barn.yml`, `barn.yaml`, `pigsty.yml`, and `pigsty.yaml` in that order. All four filenames use the same Pigsty-compatible YAML inventory format.

When no inventory file is present in the current directory, `plan`, `up`, `reload`, `recreate`, and `resize` fall back to the applied specification stored in `BARN_HOME` (default `~/.barn`) if a deployment already exists. `validate` always requires an inventory file on disk. The file must resolve to a regular file no larger than 4 MiB; symlinks are supported. Relative shared-directory paths resolve beside the inventory’s real file. Barn stops at the first matching filename and reports any parse or validation error directly rather than falling through to the next candidate.

Barn stores applied deployment state in `BARN_HOME`. Renaming the inventory does not change the deployment; use an absolute `BARN_HOME` to address the same deployment across working directories.

## A complete inventory {#a-complete-inventory}

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

`validate` checks YAML syntax, field rules, and image catalog references (pass `--repo` to check against another repository's catalog) without starting VMs or downloading images. Its JSON output includes `valid`, `source`, `spec_hash`, and `resolved`; if the local image catalog cannot be read, it emits a warning and leaves image selectors unresolved. During `up`, Barn verifies `local-*` imported image bytes, host capabilities, shared directories, networking, and guest SSH readiness.

## What Barn reads {#what-barn-reads}

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
| `vm_arch` | `native` | Deployment-wide guest architecture; follows the host unless explicitly set to `amd64` or `arm64` |
| `vm_cpu` | `2` (1.1.0), `1` (local main) | Base vCPU count; the effective count after scaling must be `1`–`256` |
| `vm_mem` | `4096` (1.1.0), `2048` (local main) | Base memory size: bare integer in MiB, or an explicit unit string such as `8GiB` (minimum `512MiB`) |
| `vm_scale` | `1` (local main) | Positive integer multiplying CPU and memory only |
| `vm_hosts` | `[]` (working tree) | Extra local hosts mappings, declared only in `all.vars` |
| `vm_disk` | `64` | Root disk capacity: bare integer in GiB, or an explicit unit string such as `64GiB` |
| `vm_disks` | `[{path: /data}]` | Extra data disks (defaults to one 128 GiB non-persistent disk mounted at `/data`) |
| `vm_alias` | `[]` | Additional guest `/etc/hosts`, SSH config, and optional host `/etc/hosts` aliases |
| `vm_shares` | `[]` | QEMU 9p host-directory shares on Linux and macOS hosts |
{.wide .expand}

An empty host mapping (`10.10.10.10: {}`) is enough to define a complete VM with default settings. Managed nodes require distinct usable addresses in the configured `/24`.

Bare integers specify MiB for `vm_mem` and GiB for disks. Size strings accept positive integers with case-insensitive units, including `8G`, `512m`, `4gib`, and `64GB`. `K/M/G/T` and `KiB/MiB/GiB/TiB` use binary powers; `KB/MB/GB/TB` use decimal powers. Fractions such as `1.5GiB` and unitless strings such as `"8192"` are invalid. `up` checks that the root disk is at least as large as the base image's virtual size.

When `vm_image` is omitted, Barn defaults to `u24` (Ubuntu 24.04) from the binary's embedded catalog regardless of any default declared in a custom repository. Built-in aliases such as `ubuntu` → `u24` are normalized against the embedded catalog during inventory parsing, so custom repositories should use their canonical family names in `vm_image` rather than reassigning built-in aliases.

Use `vm_version` when you want to keep the image family and version prefix in separate fields:

```yaml {title="barn.yml"}
vm_image: el9
vm_version: "9.8"
```

If an exact version match exists in the catalog, Barn selects it; otherwise it matches dot-separated numeric prefixes and picks the highest version (`9.8` selects the latest `9.8.*` build, `9` selects the latest `9.x` release, and `9.10` sorts after `9.9`). Use `vm_version` only with a bare family name in `vm_image` (without `:channel` or `@version`).

## Resource scaling in the development version {#resource-scaling}

Resolve `vm_cpu`, `vm_mem`, and `vm_scale` independently: host variables override the deepest group, which overrides parent groups and `all.vars`. Missing values default to 1 vCPU, 2048 MiB, and a scale of 1. Multiply once after inheritance:

```text
CPU    = resolved(vm_cpu, default=1) × resolved(vm_scale, default=1)
Memory = resolved(vm_mem, default=2048 MiB) × resolved(vm_scale, default=1)
```

| Settings | Effective CPU | Effective memory |
|---|---:|---:|
| None | 1 | 2 GiB |
| `vm_scale: 3` | 3 | 6 GiB |
| `vm_cpu: 2`, `vm_scale: 3` | 6 | 6 GiB |
| `vm_mem: 4GiB`, `vm_scale: 3` | 3 | 12 GiB |
| `vm_cpu: 2`, `vm_mem: 4GiB`, `vm_scale: 3` | 6 | 12 GiB |

A host's `vm_scale: 1` replaces a group's `vm_scale: 3`; group and host scales do not compound. Equal-depth conflicts require a host override. Scale accepts integers from 1 to 256, subject to the effective 256-vCPU limit and memory overflow checks. Quoted numbers, fractions, booleans, null, zero, and negative values fail validation. Base memory still requires at least 512 MiB. Root disks, data disks, and shares are unaffected. Use the exact keys `vm_cpu` and `vm_mem`; `vm_memory` is not an alias.

Inspect `barn plan -f pigsty.yml`, then apply CPU/memory changes with `barn resize -f pigsty.yml`. Existing deployments that omit these fields will show a resource decrease when their inventory is read by the new build. Add `vm_cpu: 2` and `vm_mem: 4096` before upgrading to preserve the previous defaults. Commands using applied state without an inventory keep the recorded resources.

## Local service names in the development version {#local-hosts}

This section describes the uncommitted hosts extension, absent from both v1.1.0 and local main commit `6ab0cd5`.

Declare finite service mappings in `all.vars.vm_hosts`. Barn combines them with node names and `vm_alias` when publishing from an explicit inventory:

```yaml {title="pigsty.yml"}
all:
  vars:
    vm_hosts:
      - {address: 10.10.10.10, names: [i.pigsty, m.pigsty]}
      - {address: 10.10.10.100, names: [pg-dns-service]}
  hosts:
    10.10.10.10: {nodename: meta}
```

```bash
barn hosts install -f pigsty.yml --json  # preview, including before VM creation
barn hosts install -f pigsty.yml --yes  # publish; sudo may ask for a password
barn hosts uninstall --yes
```

Each entry requires `address` and a non-empty `names` list. Addresses must be canonical IPv4 addresses in the inventory's private `/24`, within `.9`–`.254`; `.1`–`.8` are reserved for the host and DHCP. Identical name/address pairs deduplicate; names compare without case, and different destinations fail validation. Existing conflicting names outside the Barn-owned block also stop publication. A hosts record does not configure a VIP in a guest.

These mappings affect only the host's `/etc/hosts`. Editing them does not change the VM spec hash, configure guest DNS, or trigger VM drift. Without `-f`, `hosts install` publishes only names and aliases from applied VM state, replacing the whole Barn block; repeat the explicit inventory command to retain service names. `up` never publishes this file automatically. An unchanged plan needs no sudo; each changed system hosts file requires privilege. Wildcards, SRV records, and live primary discovery require a DNS service.

Pigsty's development `bin/sandbox-dns` extracts its portal, node, PostgreSQL, VIP, and MinIO names for this interface. See the [migration audit](/blog/design/pigsty-barn-migration/).

## Development specification overrides {#specification-overrides}

As of 2026-11-11, the working-tree development build accepts unified CLI and environment inputs for six specification fields. Released 1.1.0 does not support the four new resource flags or these environment variables.

| Inventory field | CLI | Environment variable | Default |
|---|---|---|---|
| `vm_image` | `--image/-I` | `BARN_IMAGE` | `u24` |
| `vm_arch` | `--arch/-A` | `BARN_ARCH` | `native` |
| `vm_cpu` | `--cpu/-C` | `BARN_CPU` | 1 |
| `vm_mem` | `--mem/-M` | `BARN_MEM` | 2048 MiB |
| `vm_scale` | `--scale/-S` | `BARN_SCALE` | 1 |
| `vm_disk` | `--disk/-D` | `BARN_DISK` | 64 GiB |
{.wide .expand}

Each field follows `CLI > nonempty environment > host > deepest child group > parent group > all.vars > default`. CPU and memory always specify bases; multiply each once by the final scale after applying overrides. Disk capacity does not scale. `-S 3` replaces the previous multiplier; add `-S 1` for exact final CPU/memory. CLI and environment override host values on selected nodes. Put common defaults in `all.vars` when host exceptions should remain effective. Inventory syntax, field types, and inheritance conflicts must remain valid.

```bash
barn init full -C 2 -M 4GiB -S 2 -D 128GiB
barn plan -f barn.yml -S 3
BARN_SCALE=2 barn validate -f barn.yml -S 1
```

`init` and template-generating `setup` write all six choices, including defaults, and save CPU/memory bases and scale. The first interactive `up` also saves its choices if it needs to generate an inventory. Lifecycle overrides on an existing file change only the current desired specification without rewriting YAML; reading the original file later reports drift. When only applied state remains, `--scale` or `BARN_SCALE` requires `-f`; CPU/memory can set absolute values with an implicit scale of 1.

Environment variables affect only commands accepting the corresponding specifications. `status/start/stop/restart/destroy/purge`, independent image management, and `barn mac` ignore these six variables. So does `setup` when reusing an inventory. `resize` accepts CPU/memory/scale, root capacity, and its existing I/A consistency checks; `BARN_DISK` only grows the root disk. Whitespace-only environment values mean unset, and invalid values shadowed by CLI do not fail: `BARN_CPU=bad barn plan -C 2` uses 2. Effective environment overrides are preserved as explicit flags in follow-up commands.

`--disk` sets the absolute system root capacity, which must be at least the base image's virtual size. Planning checks catalog metadata; creation checks the actual image again. It applies to creation, explicit recreation, and in-place root growth through `resize -D`. Growth supports last plain ext4/XFS root partitions and never shrinks them; see [root disk growth](../cli/#root-disk-growth) for the workflow and recovery. Recreation replaces root and nonpersistent data disks. The default 128 GiB `/data` disk remains separate.

## Image and architecture overrides {#image-and-architecture}

The following I/A behavior applies to 1.1.0. The development build additionally reads `BARN_IMAGE/BARN_ARCH` between CLI and inventory precedence, as described above.

Guests default to the host architecture: `arm64` on Apple Silicon and `amd64` on Intel/AMD hosts. Another architecture is selected only when explicitly requested in the inventory or command line. Precedence is **`--arch/-A` → inventory `vm_arch` → `native` (host architecture)**. Use `-A native` to override a fixed inventory architecture and follow the host again.

| Architecture | Aliases | Meaning |
|---|---|---|
| `native` | — | Follow the current host; also the default when unset |
| `amd64` | `x86_64`, `x64` | Select an x86-64 guest |
| `arm64` | `aarch64`, `a64` | Select an ARM64 guest |
{.wide .expand}

`vm_arch` applies to the entire deployment; define it once under `all.vars`. Every managed node must resolve to the same architecture. Node variables and selectors cannot create a deployment with mixed architectures.

`--image/-I` overrides `vm_image` and `vm_version` for selected nodes without changing the architecture. The catalog must provide the requested architecture variant; a missing variant is an error and never selects another architecture automatically.

```bash
barn plan -I u24                 # Ubuntu 24.04; retain the inventory or host architecture
barn up -I u24 -A amd64          # Use amd64 Ubuntu 24.04 for this invocation
barn plan -A native              # Override the inventory architecture with the host's
barn init full -I u24 -A arm64   # Save both choices in a new inventory
```

Overrides on `up`, `plan`, `reload`, `recreate`, `resize`, and `validate` change only the desired configuration for that invocation. To keep a choice, set `all.vars.vm_arch` and the relevant node or group `vm_image`, removing any superseded `vm_version`. `init` and template-generating `setup` write the choices into the new inventory. Setup's `-I/-A` flags cannot be used with an existing inventory.

When no inventory file exists, lifecycle commands use the saved deployment specification before applying explicit overrides. `start` and `restart` always use applied state. Omitting `-A` or editing the inventory never converts an existing VM: `up` reports drift, and switching architecture requires `recreate` with all existing nodes selected. Although `resize` accepts overrides to check desired state, it still applies only CPU and memory changes.

Guests whose architecture differs from the host use QEMU TCG. On Linux, `barn setup` installs the native emulator; install the target `qemu-system-*` binary and UEFI firmware before starting a foreign guest. See [Runtime policy](../images/#runtime-policy) for acceleration and image exceptions.

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
> **Data disks are disposable test storage.** During `up`, Barn formats a blank data disk with the configured `fs`. It resets an existing ext4 or XFS filesystem, `persistent: true` disks included, only when the guest's read-only check (`e2fsck -fn` or `xfs_repair -n`) reports recognized corruption, and records the reset in `nodes[].repairs`. A disk with a partition table, a signature without a filesystem UUID, another filesystem type, features the guest tools do not support, or an unrecognized checker failure keeps its data and gets a warning in `nodes[].warnings`; so do transient probe errors, missing block devices, busy mounts, and host I/O errors. Root disks and host shares are never formatted.

## Shares {#shares}

```yaml {title="barn.yml"}
vm_shares:
  - host: ./src
    guest: /src
    readonly: true
```

`vm_shares` mounts host directories into Linux guests through QEMU Virtio-9p on Linux and macOS hosts, with `readonly: true` by default. Host QEMU and the guest kernel must support 9p; backend device limits apply. Native macOS guests use VirtioFS through `barn mac --share`.

Shared sources use the invoking user’s actual filesystem permissions:

- `host` accepts absolute paths, `~/`, inventory-relative paths, and directory symlinks. `guest` must be absolute and is normalized automatically; spaces, Unicode, and shell punctuation are accepted, while control characters are rejected.
- Resolved host directories must exist, be accessible, and not overlap `BARN_HOME`; ownership by the invoking user is not required.
- Host sources may overlap and may be shared by multiple readers or writers. Users coordinate concurrent writes. Guest mount targets within one node must not overlap.
- `guest` paths cannot overlap data-disk mounts, system directories, or the login user's `.ssh` directory. Use 9p shares for source code and build artifacts rather than PostgreSQL data directories.
- If a writable share (`readonly: false`) cannot be written by the guest user, Barn mounts it read-only, reports a warning, and leaves host file ownership untouched; fix host permissions and re-run `barn up` to upgrade the mount.
- Changing `vm_shares` on an existing node requires `barn recreate`. Missing host directories during `up` or `start` fail only the affected node, while `restart`, `reload`, and `recreate` verify share paths before stopping running VMs.

## Names and addresses {#names-and-addresses}

Barn resolves each node's name from the first available source: explicit `nodename`, `<pg_cluster>-<pg_seq>`, or `node-<last-octet>`. Node names must be unique across the deployment, be 1–63 characters long, contain only lowercase letters, digits, and hyphens, and neither start nor end with `-`. `vm_alias` accepts additional lowercase DNS names (dots allowed) that must be distinct from all node names and other aliases.

All managed nodes in a deployment must belong to a single RFC1918 `/24` subnet: `.1` is the host gateway, `.2`–`.8` are reserved, and `.9`–`.254` are available for nodes. Inside the guest, the fixed-IP NIC carries the configured inventory address (inspectable via `ip -br addr`).

## Drift {#drift}

Explicit node selectors apply only selected changes: `plan node-1`, `up node-1`, `reload node-1`, `recreate node-1`, and `resize node-1` retain the applied definitions of unselected peers, even when edited or omitted in the inventory. The entire inventory must still parse correctly. Images for uncreated, unselected nodes are not resolved. Conflicts with applied addresses, aliases, control-node roles, or deployment-wide settings are still rejected.

Barn computes a specification hash for every resolved node:

- `barn up` creates newly added nodes, starts stopped nodes, and retries unfinished guest provisioning on running nodes without restarting their QEMU processes.
- Modifying a node's CPU or memory uses `barn resize <node>` and preserves its identity and disks. The development build also supports grow-only root capacity through `resize -D`. Image, data-disk, share, or other VM definition changes require `barn recreate <node>`. Removing a node from the inventory (or setting `vm_skip: true`) reports the node as `missing` in `plan` without automatically destroying it.
- Changing deployment-wide settings (`vm_arch`, login username, or the `/24` subnet) requires recreating the entire deployment.
- Because `plan` and `up` resolve image channels and version prefixes against the active catalog, running `barn update` can introduce image drift even when `barn.yml` has not changed. Always keep an explicit `nodename` on each host so renaming `pg_cluster` does not turn an existing node into a `missing` old node plus a new node.
