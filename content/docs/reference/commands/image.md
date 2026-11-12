---
title: Image Commands
description: Refresh signed catalogs, inspect or download images, import local files, and prune caches.
weight: 40
date: 2026-11-11
---

Refresh signed catalogs, inspect or download images, import local files, and prune caches.

This reference covers **Barn 1.2.0**. Option tables distinguish options also available in **1.1.0** from additions in **1.2.0**; see the [version baseline](/docs/reference/commands/#versions). All commands inherit the [global options](/docs/reference/commands/#global-options).

Official repositories and HTTP sources require a trusted detached signature. An explicitly selected custom HTTPS repository or local directory can be unsigned, provided the source is exactly that repository's `catalog.json`. Any supplied signature must verify. See [catalog trust](../../images/#trust-and-verification).

## `barn update` {#barn-update}

```text
barn update [flags]
```

Fetch `catalog.json` and its signature when required by repository policy, verify trust and revision rules, then atomically activate the catalog. Ordinary commands use local metadata and never update it implicitly. This updates image metadata, not the Barn executable. Repository precedence is `--repo` > `--mirror` > `BARN_REPO` > the global official repository. See [repository selection and trust](../../images/#runtime-policy).

| Option | Meaning / default | Available in |
|---|---|---|
| `--mirror` | use the China official repository at repo.pigsty.cc; overridden by `--repo` | 1.1.0 |
| `-r, --repo string` | image repository URL or directory; overrides `--mirror` and $BARN_REPO | 1.1.0 |
{.wide .expand}

```bash
barn update
barn update --mirror
barn --json update --repo /srv/barn
```

## `barn image list` {#barn-image-list}

```text
barn image list [flags]
```

List every catalog architecture and registered local image. It has no image selector or architecture filter. The active local catalog is used; run `barn update` explicitly to refresh it. Aliases `barn images` and `barn im` select the same image command group.

Aliases: `ls`.

| Option | Meaning / default | Available in |
|---|---|---|
| `-r, --repo string` | image repository URL or directory; overrides $BARN_REPO | 1.1.0 |
{.wide .expand}

```bash
barn image list
barn --json image list
barn image list --repo /srv/barn
```

## `barn image info` {#barn-image-info}

```text
barn image info [image[:channel]|image@version-prefix] [flags]
```

Inspect metadata and verified cache state for one image, using the catalog default if omitted. Select a family (`u24`), channel (`u24:stable`), or numeric version prefix (`el9@9`). Architecture defaults to native. The compatibility spelling `--architecture/-a` is also accepted for `--arch/-A`. It does not download the artifact. Supported aliases and exact embedded versions are in [Linux images](../../images/).

Aliases: `in`.

| Option | Meaning / default | Available in |
|---|---|---|
| `-A, --arch string` | artifact architecture (defaults to native): native, amd64 (x86_64, x64), or arm64 (aarch64, a64) | 1.1.0 |
| `-r, --repo string` | image repository URL or directory; overrides $BARN_REPO | 1.1.0 |
{.wide .expand}

```bash
barn image info
barn image info u24 -A arm64
barn --json image info el9@9
```

## `barn image pull` {#barn-image-pull}

```text
barn image pull [image[:channel]|image@version-prefix] [flags]
```

Download the selected artifact and verify its SHA-256, byte size, qcow2 structure, and virtual capacity before activating the cache entry. Omitted image and architecture select the catalog default and native host architecture. Existing valid cached bytes are reused. The catalog’s upstream URL is provenance, not a download fallback. `--architecture/-a` remains a compatibility alias. A foreign artifact does not install the corresponding QEMU emulator.

Aliases: `p`.

| Option | Meaning / default | Available in |
|---|---|---|
| `-A, --arch string` | artifact architecture (defaults to native): native, amd64 (x86_64, x64), or arm64 (aarch64, a64) | 1.1.0 |
| `--mirror` | use the China official repository at repo.pigsty.cc; overridden by `--repo` | 1.1.0 |
| `-r, --repo string` | image repository URL or directory; overrides `--mirror` and $BARN_REPO | 1.1.0 |
{.wide .expand}

```bash
barn image pull
barn image pull u24 --mirror
barn image pull d13 -A amd64 --repo /srv/barn
```

## `barn image import` {#barn-image-import}

```text
barn image import <path> [flags]
```

Copy a local regular qcow2 image into the private cache and validate its container, optionally against an expected digest. Relative paths, `~/`, and symlinks to regular files are accepted. `qemu-img` is required; importing does not boot the image, add cloud-init, or change credentials.

A `local-*` name registers an immutable inventory reference and requires boot mode plus the source login user. Named imports can record a foreign architecture with `-A`; qcow2 metadata does not identify CPU architecture, and unnamed imports cannot use `-A`. Set both `vm_image` and a matching `vm_arch` when using it. See [import and cache rules](../../images/#local-image-import).

Aliases: `i`.

| Option | Meaning / default | Available in |
|---|---|---|
| `-A, --arch string` | Guest architecture recorded with `--name`; defaults to native; does not convert the image | 1.1.0 |
| `-b, --boot string` | required with `--name`: bios or uefi | 1.1.0 |
| `--name string` | Immutable local-* alias; requires `--boot` and `--source-user` | 1.1.0 |
| `-s, --sha256 string` | optional expected SHA-256 | 1.1.0 |
| `-u, --source-user string` | required with `--name`: source image login user | 1.1.0 |
{.wide .expand}

```bash
barn image import ./base.qcow2
barn image import ./base.qcow2 --name local-dev --boot uefi --source-user ubuntu -A arm64
```

## `barn image sync` {#barn-image-sync}

```text
barn image sync <url|path> [flags]
```

Activate a catalog from one exact URL or local file, reading its adjacent `.minisig` signature under the trust policy above. This is the recovery/import path; use `update` for the configured repository's normal endpoint. `--repo` chooses which repository's active metadata to replace. An unsigned custom source must be exactly `<repo>/catalog.json`; an arbitrary recovery file requires a trusted signature.

Older revisions require `--allow-downgrade`. For custom repositories that allow unsigned catalogs, switching from a previously signed catalog to an unsigned one also requires this flag. It never permits an invalid signature or bypasses the official-repository signature requirement and revision-content checks. Future downgrade protection still remembers the highest revision.

Aliases: `sy`.

| Option | Meaning / default | Available in |
|---|---|---|
| `--allow-downgrade` | activate a catalog older than the newest revision seen so far | 1.1.0 |
| `-r, --repo string` | Repository whose active catalog is replaced | 1.1.0 |
{.wide .expand}

```bash
barn image sync /srv/barn/catalog.json
barn image sync --repo /srv/barn /srv/recovery/catalog.json
barn image sync --allow-downgrade /srv/recovery/catalog.json
```

## `barn image reset` {#barn-image-reset}

```text
barn image reset [flags]
```

Reactivate the catalog embedded in the current binary for the selected repository. It keeps the highest accepted revision used by downgrade protection. Cached images and VM disks are retained; this is not a cache deletion command.

| Option | Meaning / default | Available in |
|---|---|---|
| `-r, --repo string` | Repository whose active catalog is reset to the embedded catalog | 1.1.0 |
{.wide .expand}

```bash
barn image reset
barn --json image reset --repo /srv/barn
```

## `barn image prune` {#barn-image-prune}

```text
barn image prune [flags]
```

List reclaimable cache files by default. `--yes` deletes candidates; it is mutually exclusive with `--dry-run`. The selected active catalog, applied node base-image digests, and registered local aliases protect their referenced files. Stale recognized staging files can also be removed; quarantined `.corrupt-*` files remain.

Preview with the same repository selection you will use for deletion. Deletion is sequential; an error on a later file does not restore files already removed. See [pruning rules](../../images/#pruning).

Aliases: `pr`.

| Option | Meaning / default | Available in |
|---|---|---|
| `-d, --dry-run` | show unreferenced images and stale staging files without deleting | 1.1.0 |
| `-r, --repo string` | image repository URL or directory; overrides $BARN_REPO | 1.1.0 |
| `-y, --yes` | Delete the listed unreferenced files; mutually exclusive with `--dry-run` | 1.1.0 |
{.wide .expand}

```bash
barn image prune --dry-run
barn image prune --repo /srv/barn --dry-run
barn image prune --repo /srv/barn --yes
```

## Implementation {#implementation}

[command_image.go](https://github.com/pgsty/barn/blob/v1.2.0/cmd/barn/command_image.go) · [images.go](https://github.com/pgsty/barn/blob/v1.2.0/cmd/barn/images.go)

The [version baseline](/docs/reference/commands/#versions) identifies the released source and the changes since 1.1.0.
