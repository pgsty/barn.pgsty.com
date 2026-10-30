---
title: Image Repositories
description: Choose guest images, use a mirror, import a local qcow2, and prune the cache.
weight: 50
icon: fa-solid fa-boxes-stacked
---

> [!NOTE]
> **Unreleased**: The changes below to flexible local repository paths and image imports cached by content digest require a build containing source commit `27f17bb`; they are not included in Barn 0.9.2. See [Unreleased Changes](/docs/about/unreleased/).

This guide covers Linux guest image selection, mirrors, static repositories, and cache management in **Barn 0.9.2**.

With the default inventory, `barn up` automatically resolves `u24:stable` for your host architecture and downloads the matching verified `qcow2` image on demand. Barn starts with the image catalog embedded in the binary; run `barn update` whenever you want to fetch, verify, and activate the latest catalog from the repository (or `barn image sync` to load an exact catalog URL or local file).

## Choose an image

Inspect the available distribution families and channels:

```bash
barn image list
barn image info u24
barn image info u24:stable
```

Barn provides nine built-in distribution families: `el7`, `el8`, `el9`, `el10`, `d12`, `d13`, `u22`, `u24`, and `u26`. A bare family name such as `el9` selects the `stable` channel, `name:channel` selects an explicit channel, and `name@version` pins an exact immutable build. You can also set a numeric prefix in `vm_version` to pick the newest matching release along dot boundaries:

```yaml {title="barn.yml"}
all:
  vars:
    vm_image: el9
    vm_version: "9.7"
```

Here `"9.7"` selects the newest `9.7.x` build in the active catalog, while `"9"` selects the newest `9.x` build (quote numeric `vm_version` values in YAML so they remain strings). Do not combine `vm_version` with a `:channel` or `@version` suffix in `vm_image`.

For strict reproducibility across catalog updates, pin the full version string reported by `barn image info`:

```yaml {title="barn.yml"}
all:
  vars:
    vm_image: d13@20260914.2601.2
```

After changing `vm_image` or `vm_version`, preview the change with `barn plan`. Existing nodes keep their current root disk until you run `barn recreate <node>`; updating the catalog with `barn update` only affects newly created or recreated nodes.

`barn image list` displays all architectures, while `info` and `pull` default to the host architecture unless you pass `--arch amd64` or `--arch arm64`:

- **`el7`** is supported only on native `linux/amd64` hosts.
- **`el8` on `arm64`** automatically runs under QEMU TCG software emulation on Apple Silicon because the stock RHEL/Rocky 8 `arm64` kernel requires a 64 KiB page granule that macOS HVF does not support. See [Runtime rules](../troubleshooting/#native-acceleration-or-compatibility-runtime-is-unavailable) for foreign-architecture emulator requirements.

> [!NOTE]
> All image versions in the `0.9.2` embedded catalog carry `supported` status except legacy compatibility builds marked `deprecated`: EOL `el7`, EL9 `9.3` / `9.6`, and EL10 `10.0`.

## Use a mirror

Release builds default to `https://repo.pigsty.io/barn`. Pass `--mirror` to use the China mirror (`https://repo.pigsty.cc/barn`), or `--repo` to point at a custom repository URL or local directory:

```bash
barn image pull u24 --mirror
barn up --mirror
barn update --repo https://mirror.example/barn
barn image pull u24 --repo https://mirror.example/barn
barn up --repo https://mirror.example/barn
```

To set a default repository for your current shell session, export `BARN_REPO`:

```bash
export BARN_REPO=https://mirror.example/barn
barn update
barn up
```

Repository selection follows the precedence `--repo` → `--mirror` → `BARN_REPO` → global default (`https://repo.pigsty.io/barn`). Both official repositories and any plain `http://` repository require a valid Minisign signature (`catalog.json.minisig`); explicit local directory paths and custom `https://` endpoints may use an unsigned `catalog.json`. Every image download is verified against the catalog's byte size, SHA-256 digest, and `qemu-img` structural checks.

When downloading from either official repository, Barn automatically retries transient network errors, resumes partial transfers, and falls back to the peer official mirror if an artifact is unreachable. Custom `--repo` endpoints never fall back to external servers.

Each repository root maintains its own active catalog state under `BARN_HOME`. When you point `--repo` at a custom repository that defines new image entries, run `barn update --repo <root>` first to activate its catalog before running `plan` or `up`.

## Build a static repository

A Barn image repository is a plain directory that you can serve over static HTTP/HTTPS, copy with `rsync`, or read directly from a local path:

```filetree {title="/srv/barn"}
barn/
├── repo.yaml                # Human-maintained image definitions and channels
├── catalog.json             # Generated catalog with SHA-256 and file sizes
├── catalog.json.minisig     # Minisign signature (required for official and HTTP repos)
└── images/
    └── d13-1-arm64.qcow2    # Verified cloud-init qcow2 base image
```

`repo.yaml` is the sole human-edited file. For the single `arm64` image above, create `/srv/barn/repo.yaml`:

```yaml {title="/srv/barn/repo.yaml"}
schema: 1
revision: 1
defaults: { image: d13, channel: stable, arch: native, boot: uefi }
images:
  d13:
    channels: { stable: "1" }
    versions:
      "1":
        status: testing
        variants:
          arm64:
            source_user: debian
```

Place your cloud-init-capable `qcow2` image at `/srv/barn/images/d13-1-arm64.qcow2` (relative roots, directory symlinks, and shared writable directories are supported), then generate and verify `catalog.json` on a host with `qemu-img` installed:

```bash
barn repo scan /srv/barn
barn repo build /srv/barn
barn repo verify /srv/barn
```

`barn repo scan` inspects the directory layout read-only, while `barn repo build` runs `qemu-img check` and writes `catalog.json` with exact filenames, SHA-256 digests, compressed sizes, and virtual capacities. Increment `revision` whenever you update `repo.yaml` or add images, and upload immutable `.qcow2` files before publishing the updated `catalog.json` (and `.minisig` signature).

Activate and test the local repository:

```bash
barn update --repo /srv/barn
barn image info d13 --arch arm64 --repo /srv/barn
barn image pull d13 --arch arm64 --repo /srv/barn
```

Pass `--repo /srv/barn` (or `export BARN_REPO=/srv/barn`) to `plan`, `up`, and `recreate`, and set `vm_image: d13@1` in your inventory. To revert `/srv/barn` back to the binary's embedded catalog while keeping its anti-rollback high-water mark, run `barn image reset --repo /srv/barn`.

## Import a local image and prune the cache

To use a single custom `qcow2` image on your host's native architecture without creating a repository, import it into Barn's local cache with a `local-` alias:

```bash
barn image import --name local-mybase --boot uefi \
  --source-user ubuntu --sha256 <digest> /path/to/base.qcow2
```

`--name` (must start with `local-`), `--boot` (`uefi` or `bios`), and `--source-user` are required together when registering an alias; omitting them caches the verified `qcow2` bytes by content digest without creating an alias. The image must already include cloud-init support for Barn's first-boot provisioning. Named `local-*` aliases are immutable—register a new `local-*` name whenever you rebuild the image, and reference it in `barn.yml` with `vm_image: local-mybase`.

To reclaim disk space from unreferenced images and interrupted download staging files:

```bash
barn image prune --dry-run
barn image prune --yes
```

`barn image prune` (which requires `qemu-img`) preserves all images listed in the selected repository's active catalog, all base images used by existing nodes in `BARN_HOME`, and all registered `local-*` aliases.

See [Linux Images](../../reference/images/) for catalog signature rules, anti-rollback protection, and cache layout, or [Image Pipeline](../../reference/image-pipeline/) for building new base images from upstream cloud releases.
