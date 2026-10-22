---
title: Configuration
description: The Pigsty-compatible inventory fields Barn reads, their defaults, and node-level drift behavior.
weight: 10
icon: fa-solid fa-file-code
aliases: [/docs/concepts/project-model/]
---

This reference covers **Barn 0.9.1**. Check
`barn version` when using another version.

## Discovery

Barn first checks an explicit `-f` path. Otherwise, it searches the current directory for `barn.yml`,
`barn.yaml`, `pigsty.yml`, and `pigsty.yaml`, in that order. All names use the same Pigsty-compatible YAML inventory format.

If no inventory file exists, `plan`, `up`, `reload`, and `recreate` use the applied specification when a deployment exists.
`validate` does not use applied state. The configuration must be a regular file, not a symlink, and no larger than 4 MiB.
Barn uses the first existing candidate. If that file is invalid, Barn reports the error without trying the next filename.
Renaming the file or changing directories does not create another deployment. Barn stores applied state in `BARN_HOME`.

## A complete inventory

`barn init [meta|dual|trio|full]` generates 1, 2, 3, or 4 nodes respectively.
`meta` uses `.10`. Larger templates add `node-1` at `.11`, `node-2` at `.12`, and `node-3` at `.13`.
These templates define node topology, not Pigsty service roles.
`--cidr` changes the generated `/24` and preserves the final address octets.
To inspect a template without creating a file, use `barn init full -o -`.

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

This inventory defines two managed nodes, with `meta` as the control node. Save it as `barn.yml`, then inspect it without starting VMs:

```bash
barn validate -f barn.yml
barn --json validate -f barn.yml
barn plan -f barn.yml
```

The JSON validation result includes `valid`, `source`, `spec_hash`, and `resolved`.
In Barn 0.9.1, `validate` also resolves image catalog references and accepts `--repo`.
If the image catalog cannot be read, the result includes a warning and the image references remain unchecked.
`up` remains responsible for checking `local-*` image bytes.
Validation does not verify host resources, share access, networking, image bytes, or guest readiness.
It does not start VMs or download images.

## What Barn reads

The document must have a top-level `all:` group. Barn reads its `hosts` and nested `children` mappings.
It does not evaluate Ansible inventory plugins or Jinja expressions, or load `group_vars` or `host_vars` files.
An address in several groups defines one node. Barn combines its inherited values.

Barn reads node IPs, `nodename`, `admin_ip`, `pg_cluster`, `pg_seq`,
`node_admin_username`, `node_admin_uid`, and the documented `vm_*` variables.

**Control node.** Barn reads `admin_ip` from `all.vars`. If it is absent or matches no managed node, Barn selects the first managed node.
Traversal follows YAML order, reading each group's nodes before its child groups.
Set `admin_ip` explicitly to keep the selection stable.

**Login account.** All nodes must use the same login username, matching `[a-z_][a-z0-9_-]{0,31}`.
For the default `dba` user, an explicit `node_admin_uid` must be 88.
For a custom user, Barn checks that `node_admin_uid` is an integer but does not use it to set the guest UID.
Barn does not support general guest UID customization.

**Ignored fields.** Fields that Barn does not read, such as `pg_role`, `pg_version`, `repo_*`, and `node_packages`, cannot cause configuration drift.
Some `pg_*` and `node_*` fields are read, as listed above.

**Inheritance and validation.** Barn strictly validates the fields it reads. Unknown `vm_*` names, wrong types, Jinja expressions, invalid addresses, and conflicting sibling-group values cause errors.
Inheritance follows `all.vars` → deeper `children.<group>.vars` → node variables.
Node values replace whole lists such as `vm_disks`; Barn does not append lists.
If groups at the same depth provide different values, resolve the conflict with an override on the node.

Barn supports YAML anchors and merge keys: explicit keys take priority, followed by the first mapping in a merge sequence.
Duplicate mapping keys and multiple YAML documents cause errors.

**Skipped nodes.** Node keys must be IPv4 addresses, including `vm_skip: true` entries.
Skipped nodes do not count toward the 20-node limit or determine the managed subnet.
The inventory must still contain at least one managed node.
Skipping an applied node marks it as removed from the inventory. It does not destroy the VM.

In Barn 0.9.1, errors identify the invalid rule, value, and line where available.
They also suggest a similar `vm_*` spelling.

## VM variables

| Variable | Default | Meaning |
|---|---|---|
| `vm_skip` | `false` | do not virtualize this real/external host |
| `vm_image` | `u24` | image family, channel reference, or `image@version` selector |
| `vm_version` | unset | newest numeric version matching this prefix, such as `9` or `9.7` |
| `vm_arch` | `native` | deployment-wide guest architecture: `native`, `amd64`, or `arm64` |
| `vm_cpu` | `2` | vCPU count |
| `vm_mem` | `4096` | MiB integer, or a size such as `8GiB` |
| `vm_disk` | `64` | root disk: GiB integer or an explicit size such as `64GiB` |
| `vm_disks` | `[{path: /data}]` | extra disks (one 128 GiB non-persistent disk at `/data` by default) |
| `vm_alias` | `[]` | guest `/etc/hosts`, SSH-config, and optional host aliases |
| `vm_shares` | `[]` | QEMU 9p host-directory shares |

An empty node entry defines a complete VM. A deployment contains 1–20 managed nodes.
`vm_cpu` accepts 1–256. Memory must be at least 512 MiB.
Bare integer memory values use MiB; bare integer disk sizes use GiB.
Explicit size strings accept positive integers followed by `B`, `KiB`, `MiB`, `GiB`, `TiB`, `KB`, `MB`, `GB`, or `TB`.
Units are case-sensitive: `8GiB` is valid, while `8G`, `1.5GiB`, and the quoted unitless string `"8192"` are invalid.
Root and data disk sizes must be positive.

`up` also checks that the root disk is at least as large as the selected base image's virtual size.

If you omit `vm_image`, Barn selects Ubuntu 24.04.
To use Debian 13, set `vm_image: d13` under `all.vars`.
This default comes from the binary's embedded image catalog.
Changing a custom repository's default does not change an inventory that omits `vm_image`.
Before applying changes to an existing inventory, inspect `barn plan`.

In 0.9.1, inventory parsing converts built-in aliases through the embedded image catalog. For example, `ubuntu` becomes `u24`.
A custom repository cannot reliably redirect these aliases in an inventory, even if `image info` resolves them differently.
In `vm_image`, use the custom image catalog's canonical family name.
Do not reassign a built-in alias to another family.

Use `vm_version` to specify a version prefix separately from the image family:

```yaml
vm_image: el9
vm_version: "9.7"
```

If the requested version exists exactly in the image catalog, Barn selects it. Otherwise, it matches the prefix at dot-component boundaries and selects the numerically newest match.
`9.7` selects the newest `9.7.*` build. `9` selects the newest 9.x release.
Barn compares numeric components as integers, so 9.10 sorts after 9.9.
Do not combine `vm_version` with a `vm_image` that already contains `:channel` or `@version`.

If present, `vm_arch` must resolve to the same value on every managed node. Define it once in `all.vars`.
Changing it changes the deployment configuration and requires recreation of the whole deployment.
Linux setup installs only the native emulator. A foreign architecture also needs its matching `qemu-system-*` binary and firmware.

## Data disks

```yaml
vm_disks:
  - path: /data
    size: 128
    fs: auto
    persistent: false
```

`path` defines the disk identity and mount point. `fs` accepts `auto` (the default), `xfs`, or `ext4`.
For a blank `auto` disk, Barn uses XFS if the guest has `mkfs.xfs`; otherwise, it uses ext4.
Explicit `xfs` and `ext4` settings never fall back to another filesystem. Barn reuses healthy existing filesystems.
`persistent: true` keeps the disk across an ordinary destroy. `vm_disks: []` disables extra disks.
`size` defaults to 128 GiB for each entry. Integer sizes use GiB; explicit size strings are also accepted.

Use normalized absolute mount paths such as `/data` or `/data/pg`.
Barn derives the disk identity by trimming leading and trailing `/` and replacing inner `/` separators with `-`.
The identity must match `[a-z][a-z0-9-]{0,31}`. Identities and mount paths must be unique within the node.
Barn refuses `/`, system paths such as `/etc`, `/usr`, `/root`, and `/var/lib/barn`, and overlapping parents or children.
Changing a persistent disk's identity or declaration can require explicit migration.
Persistence does not guarantee that a new definition can reuse the old disk.

**Data disks are disposable test storage.** `up` resets unrecognized or confirmed damaged filesystems to the configured type.
It reports the data loss, including when the affected disk is persistent.
Persistence controls disk retention during destroy and recreate, not retention of corrupt contents.
Probe errors, missing devices, busy mounts, and backend I/O failures do not trigger formatting.
This recovery does not apply to root disks or host shares.

## Shares

**Linux guests on macOS:** `vm_shares` uses QEMU 9p, which Barn does not support on macOS hosts.
A node configured with it cannot start. `validate` and `plan` report a warning.
Use SSH file transfer for these guests. The independent `barn mac --share` option uses VirtioFS for macOS guests.
Changing an existing node's shares requires `recreate`, which replaces the root disk.
Preserve required data before that operation. Barn does not fall back to unchecked host paths.

```yaml
vm_shares:
  - host: /absolute/owned/source
    guest: /src
    readonly: true
```

`readonly` defaults to `true`. Each node accepts at most eight shares.
Host and guest paths must be normalized absolute paths. Barn does not expand `~` or relative paths.
Guest targets accept only letters, digits, `.`, `_`, `-`, and `/`. They do not accept spaces.
Host directories must exist and belong to the caller. No path component can be a symlink.
Host directories must not overlap `BARN_HOME`. On Linux, use the real path (`realpath /path/to/source`).
Barn 0.9.1 includes the replacement path in a symlink diagnostic.

Within one node, host sources must not overlap each other, and guest targets must not overlap each other.
Across nodes, overlapping host sources are allowed only when all shares are read-only.
Guest targets must not overlap data-disk mounts, reserved system paths, or the login user's `.ssh` directory.
Use shares for trusted development files, not PostgreSQL data.
If a requested writable share cannot support guest writes, Barn tries read-only access and reports the limitation.
Correct the permissions and repeat `up` to retry. Barn does not recursively change host file ownership.

During `up` or `start`, a missing source fails only its node. Other selected nodes continue.
Restore the original directory or its host mount, then retry that node. Barn never creates an empty replacement directory.
Restart, reload, and recreate validate sources before stopping existing nodes.

## Names and addresses

Barn selects the node name from `nodename`, then `<pg_cluster>-<pg_seq>`, then `node-<last-octet>`.
Names must be unique and contain 1–63 lowercase letters, digits, or hyphens. They must not begin or end with `-`.
An explicit non-empty `nodename` takes priority. In that case, Barn need not derive a name from `pg_cluster` or `pg_seq`.
`vm_alias` accepts lowercase DNS-style names. Each alias must differ from every node name and every other alias in the deployment.

All managed nodes must be in one RFC1918 `/24`: `.1` is the host, `.2`–`.8`
are reserved, and nodes use `.9`–`.254`.

Inside the guest, the fixed-IP interface carries the inventory address (`ip -br addr`).
Barn does not guarantee the interface name.

## Drift

Barn hashes each resolved node. `up` creates added nodes and starts selected stopped nodes.
Running nodes keep their processes while Barn retries unfinished guest setup.
Changed VM definitions require recreation of the affected nodes. Barn reports removed nodes but never destroys them automatically.
Changes to deployment architecture, user, or subnet require recreation of the whole deployment.
`plan`/`up` resolve image selectors to exact image identities.
After an image catalog update, review the plan even if the inventory text has not changed.
Changing a field that determines a node name produces a missing old node and a new node.
Use stable, explicit `nodename` values.
