---
title: Configuration
description: The Pigsty-compatible Inventory fields Farrow reads, their defaults, and node-level drift behavior.
weight: 10
icon: fa-solid fa-file-code
aliases: [/docs/concepts/project-model/]
---

**Version scope:** the inventory format below applies to public prerelease
v0.8.0 and local source `b91ec37` (unreleased 0.9 candidate), reviewed on
2026-09-26. New validation diagnostics are marked explicitly; see the
[version matrix](../../about/status/#documentation-baseline).

## Discovery

Configuration lookup order is explicit `-f`, then `farrow.yml`,
`farrow.yaml`, `pigsty.yml`, and `pigsty.yaml` in the current directory. Every
name uses the same Pigsty-compatible YAML Inventory format.

For `plan`, `up`, `reload`, and `recreate`, absence of a file falls back to
the applied spec when a deployment exists. `validate` has no fallback. A
configuration must be a regular non-symlink file no larger than 4 MiB. The first
existing discovery candidate wins; if it is invalid, Farrow reports the error
instead of trying the next filename. Renaming a file or moving directories does
not create another deployment; applied state lives in `FARROW_HOME`.

## A complete inventory

```yaml
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

This creates two managed definitions; the control node is `meta`. Save it as
`farrow.yml`, then inspect it without starting VMs:

```bash
farrow validate -f farrow.yml
farrow --json validate -f farrow.yml
farrow plan -f farrow.yml
```

The JSON validation result includes `valid`, `source`, `spec_hash`, and `resolved`.
In the **0.9 candidate**, `validate` also resolves catalog image references and
accepts `--repo`; an unreadable catalog adds a warning instead of a false success
claim about images, and `local-*` image-byte checks remain the responsibility of
`up`. Validation does not prove host resources, share access, networking, image
bytes, or guest readiness. It never starts VMs or downloads images.

## What Farrow reads

Farrow reads host IPs, `nodename`, `admin_ip`, `pg_cluster`, `pg_seq`,
`node_admin_username`, `node_admin_uid`, and the documented `vm_*` variables.
`admin_ip` is read from `all.vars`; it selects the control node, or the first
managed host is used. All nodes must resolve the same login username. For the
default `dba` user, an explicit `node_admin_uid` must be 88. For a custom user,
`node_admin_uid` is validated as an integer but does not set the guest UID;
Farrow does not expose a general UID customization contract.

Everything else is opaque and cannot create drift. This means unconsumed
fields such as `pg_role`, `pg_version`, `repo_*`, and `node_packages`, not all
possible `pg_*` or `node_*` names.

Inside this namespace validation is strict: unknown `vm_*` names, wrong
types, Jinja expressions, invalid addresses, and conflicting sibling-group
values are errors. Inheritance is `all.vars` → deeper `children.<group>.vars` →
host variables. Host values replace an entire list such as `vm_disks`; lists are
not appended. Different values inherited from groups at the same depth must be
resolved with a host-level override. YAML anchors and merge keys are supported;
explicit keys win, and the first mapping in a merge sequence wins. Duplicate
mapping keys and multiple YAML documents are errors.

Host keys must be IPv4 addresses even for `vm_skip: true` entries. Skipped hosts
do not consume the 20-node budget or determine the managed subnet, but the
inventory must still contain at least one managed host. Skipping an already
applied node marks it as removed; it does not destroy that VM.

The **0.9 candidate** improves errors with the offending rule, value, and line
where available, and suggests a nearby `vm_*` spelling. Those diagnostics do
not add new inventory variables.

## VM variables

| Variable | Default | Meaning |
|---|---|---|
| `vm_skip` | `false` | do not virtualize this real/external host |
| `vm_image` | `u24` | image family, channel reference, or `image@version` selector |
| `vm_version` | unset | newest numeric version matching this prefix, such as `9` or `9.7` |
| `vm_arch` | `native` | deployment-wide Guest architecture: `native`, `amd64`, or `arm64` |
| `vm_cpu` | `2` | vCPU count |
| `vm_mem` | `4096` | MiB integer, or a size such as `8GiB` |
| `vm_disk` | `64` | root disk: GiB integer or an explicit size such as `64GiB` |
| `vm_disks` | `[{path: /data}]` | extra disks (one 128 GiB non-persistent disk at `/data` by default) |
| `vm_alias` | `[]` | guest `/etc/hosts`, SSH-config, and optional host aliases |
| `vm_shares` | `[]` | QEMU 9p host-directory shares |

An empty host entry is a complete VM. A deployment contains 1–20 managed
hosts; `vm_cpu` accepts 1–256 and memory must be at least 512 MiB.
Bare integer memory is MiB; bare integer disk sizes are GiB. Explicit size
strings accept positive integers plus `B`, `KiB`, `MiB`, `GiB`, `TiB`, `KB`,
`MB`, `GB`, or `TB` (case-sensitive). `8GiB` is valid; `8G`, `1.5GiB`, and the
quoted unitless string `"8192"` are not. Root/data disk sizes must be positive;
`up` also checks the root disk against the selected base image's virtual size.

Since Farrow 0.6.0, omitting `vm_image` selects Ubuntu 24.04 instead of Debian 13.
To keep an existing Debian lab, set `vm_image: d13` under `all.vars`.
Upgrading the executable does not replace VM disks; inspect `farrow plan`
before applying the inventory again.

`vm_version` keeps short version intent separate from the image family:

```yaml
vm_image: el9
vm_version: 9.7
```

An exact Catalog version wins first. Otherwise Farrow matches only on a dot
component boundary and selects the numerically newest match: `9.7` resolves to
the newest `9.7.*` build, while `9` resolves to the newest 9.x release. Numeric
components are compared as integers, so 9.10 sorts after 9.9. Do not combine
`vm_version` with a `vm_image` that already contains `:channel` or `@version`.

`vm_arch` is stricter than ordinary per-host VM fields: when present it must
resolve to one value on every managed host, so define it once in `all.vars`.
Changing it is a deployment-envelope change and requires whole-deployment
recreation. Linux setup installs only the native emulator; a foreign
architecture also needs its matching `qemu-system-*` binary and firmware.

## Data disks

```yaml
vm_disks:
  - path: /data
    size: 128
    fs: auto
    persistent: false
```

`path` is the disk identity and mount point. `fs` is `auto` (the default), `xfs`,
or `ext4`. A blank `auto` disk is formatted XFS when the guest has `mkfs.xfs`
and ext4 otherwise, which matches what the Vagrant flow did. Explicit `xfs` and
`ext4` never fall back. Healthy existing filesystems are reused.
`persistent: true` keeps the disk across an ordinary destroy; `vm_disks: []`
means no extra disk. `size` defaults to 128 GiB for each entry; integer sizes
are GiB and explicit size strings are accepted.

Use clean absolute mount paths such as `/data` or `/data/pg`. The derived disk
identity trims leading/trailing `/` and replaces inner `/` separators with `-` and must match `[a-z][a-z0-9-]{0,31}`;
identities and mount paths must be unique within the node. `/`, system paths
such as `/etc`, `/usr`, `/root`, and `/var/lib/farrow`, and their overlapping
parents/children are refused. Changing a persistent disk's identity or declaration
can require explicit migration; persistent does not mean every new definition
can automatically reuse the old disk.

**Data disks are disposable test storage.** `up` resets unrecognized or confirmed
damaged filesystems to the configured type and reports that old data was
discarded. This includes persistent disks: persistence controls destroy/recreate,
not retention of corrupt contents. Probe errors, missing devices, busy mounts,
and backend I/O failures do not authorize formatting. Root disks and host
shares are outside this recovery path.

## Shares

**macOS limitation in v0.8 and the 0.9 candidate:** Farrow's guarded directory
sharing is not supported on macOS; a node with `vm_shares` cannot start. The
candidate also warns during `validate` and `plan`. Omit shares in new macOS labs; full macOS sharing support remains pending.
Changing an existing node's shares requires `recreate`, which replaces the root
disk. Preserve needed data before considering that operation. Farrow does not
fall back to unchecked host paths.

```yaml
vm_shares:
  - host: /absolute/owned/source
    guest: /src
    readonly: true
```

`readonly` defaults to `true`; each node accepts at most eight shares. Host and
guest paths must be clean absolute paths; `~` and relative paths are not expanded.
Host directories must already exist, be caller-owned, have no symlink path
components, and not overlap `FARROW_HOME`. On Linux, prefer the real path (`realpath /path/to/source`). The
**0.9 candidate** includes that replacement path in a symlink diagnostic.

Within one node, host sources and guest targets must not overlap. Across nodes,
overlapping host sources are allowed only when all are read-only. Guest targets
must not overlap data-disk mounts, reserved system paths, or the login user's
`.ssh` directory. Shares are for trusted development files, not PostgreSQL data. If a requested writable share
cannot support guest writes, Farrow tries read-only access and reports the
limitation. Correct permissions and repeat `up` to retry; Farrow does not
recursively change the ownership of host files.

In Farrow 0.8, a missing source fails only its node during
`up` or `start`. Other selected nodes continue. Restore the original directory or
its host mount and retry that node; Farrow never creates an empty replacement.
Restart, reload and recreate validate sources before stopping existing nodes.

## Names and addresses

Node name order: `nodename`, then `<pg_cluster>-<pg_seq>`, then
`node-<last-octet>`. Names must be unique, 1–63 lowercase letters/digits/hyphens,
and may not begin or end with `-`. An explicit non-empty `nodename` takes
precedence, so unrelated `pg_cluster` or `pg_seq` values need not derive a name.
`vm_alias` is a list of lowercase DNS-style names; aliases must not duplicate a
node name or any other alias in the deployment.

All managed hosts must be in one RFC1918 `/24`: `.1` is the host, `.2`–`.8`
are reserved, and nodes use `.9`–`.254`.

Inside the guest the fixed-IP interface is the one carrying the inventory
address (`ip -br addr`); its name is not a Farrow contract.

## Drift

Farrow hashes each resolved node. Added hosts are created by `up`; selected
existing stopped nodes are started; running peers keep their processes while unfinished guest setup is retried. Changed VM
definitions require per-node recreate; removed hosts are reported but never
destroyed. Deployment architecture, user, or subnet changes require whole-deployment
recreation. Image selectors are resolved to exact image identities by `plan`/`up`;
review the plan after a catalog update, even if the inventory text is unchanged.
Changing a field used to derive a node name appears as a missing
old node plus a new node, so prefer stable explicit `nodename` values.
