---
title: Images
description: Signed catalogs, built-in aliases, repository selection, local cache verification, imports, and pruning.
weight: 30
icon: fa-solid fa-compact-disc
---

> [!NOTE]
> **Unreleased**: The changes below to local repository paths, image import naming, image-size limits, and local alias counts require a build containing source commit `27f17bb`; they are not included in Barn 0.9.2. See [Unreleased Changes](/docs/about/unreleased/).

Barn resolves Linux guest images from a static catalog and immutable `qcow2` artifacts. Official and HTTP repositories require Ed25519/minisign catalog signatures, while explicitly selected local directory and HTTPS repositories may be unsigned. You can activate newer image catalogs with `barn update` without replacing the `barn` binary; the binary defines the trusted signing public keys and `qcow2` safety rules.

> [!WARNING]
> `el7`, `el9` (`9.3` / `9.6`), and `el10` (`10.0`) are `deprecated` compatibility images. All other built-in catalog versions are `supported`.

## Aliases and pull order

Barn `0.9.2` embeds image catalog `2026093001`, covering 9 distribution families and 41 image artifacts (`el7` is `amd64`-only; every other family provides both `amd64` and `arm64`, with `el9` offering `9.3`, `9.6`, `9.7`, and `9.8` and `el10` offering `10.0`, `10.1`, and `10.2`). When no image is specified, Barn selects `u24:stable` (Ubuntu 24.04 LTS) on the host's native architecture.

The table below lists the `stable` channel targets in embedded catalog `2026093001`. Run `barn update` followed by `barn image list` to inspect the latest catalog published on your selected repository, and see [Platforms and Limits](../../about/status/) for host support details.

| Family | Embedded `stable` | Accepted aliases |
|---|---|---|
| `d12` | `20260923.2610.1` | `debian12`, `bookworm` |
| `d13` | `20260914.2601.2` | `debian13`, `debian`, `trixie` |
| `el7` | `7.9.20221112.0` | `c7`, `centos7`, `centos79` |
| `el8` | `8.10.20240528.3` | `rocky8` |
| `el9` | `9.8.20260525.2` | `rocky9`, `rocky` |
| `el10` | `10.2.20260525.0` | `rocky10` |
| `u22` | `20260926.0.0` | `ubuntu22`, `ubuntu2204`, `jammy` |
| `u24` | `20260926.0.0` | `ubuntu`, `ubuntu24`, `ubuntu2404`, `noble` |
| `u26` | `20260927.0.0` | `ubuntu26`, `ubuntu2604`, `resolute` |
{.wide}

Distribution notes:

- `u22`, `u24`, and `u26` correspond to Ubuntu 22.04, 24.04, and 26.04 LTS using Canonical's unmodified upstream cloud images; `cloud-init` configures accounts and networking on first boot.
- `d12` and `d13` include offline-installed XFS userspace tools and a pre-generated `en_US.UTF-8` locale while keeping `C.UTF-8` as the default locale.
- `el7` is CentOS Linux 7.9 (`amd64` BIOS), and `el8`, `el9`, and `el10` are Rocky Linux (`amd64` and `arm64` UEFI).
- Running `barn update` updates what `:stable` or a numeric prefix resolves to for new nodes without altering running VMs or pinned `@version` selectors. If an existing inventory uses a channel or prefix whose target changed in the updated catalog, `barn plan` and `barn up` report the image drift and require `barn recreate` before replacing any node.

| Alias | Distribution | Architectures | Boot | Status |
|---|---|---|---:|---|
| `el7` | CentOS Linux 7.9 / 2211 | `amd64` | BIOS | `deprecated` |
| `el8` | Rocky Linux 8.10 | `amd64`, `arm64` | UEFI | `supported` |
| `el9` | Rocky Linux 9.7 / 9.8 | `amd64`, `arm64` | UEFI | `supported` |
| `el9` | Rocky Linux 9.3 / 9.6 | `amd64`, `arm64` | UEFI | `deprecated` |
| `el10` | Rocky Linux 10.1 / 10.2 | `amd64`, `arm64` | UEFI | `supported` |
| `el10` | Rocky Linux 10.0 | `amd64`, `arm64` | UEFI | `deprecated` |
| `d12`, `d13` | Debian 12 / 13 | `amd64`, `arm64` | UEFI | `supported` |
| `u22`, `u24`, `u26` | Ubuntu 22.04 / 24.04 / 26.04 LTS | `amd64`, `arm64` | UEFI | `supported` |
{.wide}

```bash
barn image list
barn image info d13
barn image info d13:stable
barn image info el9@9.7
barn image pull d13@20260914.2601.2
barn image pull d13 --arch arm64
barn update
```

`barn image list` prints every version and architecture in the active catalog along with registered `local-*` aliases. `barn image info` defaults to the host architecture (like `image pull`) and can inspect uncached catalog metadata without QEMU; if a local cache file is present, `info` also runs `qemu-img` verification on it. Neither `list` nor `info` downloads image files.

Catalog `status` values indicate support tier (`supported`, `testing`, `deprecated`, or `unknown`); non-`supported` images still boot normally and emit a status warning.

When pulling an image, Barn executes four steps:

1. **Load the active catalog** — Reads the selected repository's active local catalog once for the command (either the binary's embedded catalog or the revision last activated for that repository by `barn update` or `barn image sync`).
2. **Resolve the selector and architecture** — Resolves `image[:channel]` or `image@version-prefix` (defaulting to `u24:stable` on the official catalog) and the target architecture (`--arch` for standalone `image pull`, or `vm_arch` for lifecycle commands).
3. **Verify the local cache** — Reuses an existing cached file immediately if its byte size, SHA-256 digest, and `qemu-img` structural checks all pass.
4. **Download with resume and digest checks** — Downloads the artifact from the selected repository with automatic retries and HTTP range resumption, verifying the final size, SHA-256, and `qcow2` header before moving it into the cache. The two official mirrors (`https://repo.pigsty.io/barn` and `https://repo.pigsty.cc/barn`) can fall back to each other during artifact downloads, while custom `--repo` sources download exclusively from the specified root. Upstream URLs recorded in the catalog serve as provenance metadata only.
{.steps}

Repository selection precedence is `--repo` → `--mirror` (`https://repo.pigsty.cc/barn`) → `BARN_REPO` → compiled default (`https://repo.pigsty.io/barn`). Both official endpoints require valid minisign catalog signatures.

Because each repository root maintains its own active catalog state in `$BARN_HOME/images/manifests/`, pass the same `--repo` (or `BARN_REPO`) when working with a custom repository—even after its images are cached locally—and run `barn update --repo <root>` before using custom aliases from a newly selected repository. Once the catalog and image files are cached and verified, all ordinary commands work offline.

Barn automatically restores read-only permissions (`0444`) on verified cache files. If an unreferenced cached file fails verification, Barn renames it to `.corrupt-<timestamp>` before re-downloading; if a VM still uses that base image, Barn leaves the file in place and reports an integrity error.

## Runtime policy

When guest and host architectures match, Barn uses hardware virtualization (Apple HVF on macOS, KVM on Linux) with one built-in exception: the stock Rocky Linux 8 `arm64` kernel uses a 64 KiB page size that Apple HVF does not support, so Barn automatically runs `el8` on Apple Silicon under same-architecture QEMU TCG and flags `tcg` in status output. Cross-architecture guests (`vm_arch` different from host) also run under TCG; for `amd64` guests on `arm64` hosts, Barn pins TCG to a single translation thread to preserve x86 memory ordering.

`el7` is supported only on native `linux/amd64`. On Linux hosts, `barn setup` installs the native QEMU package set; before booting a foreign `vm_arch` with `up` or `recreate`, install the target architecture's `qemu-system-*` emulator and UEFI firmware (`barn plan` can resolve catalog images without them, though `local-*` imports still require `qemu-img`).

```bash
barn image pull d13 --mirror
barn image pull d13 --repo https://mirror.example/barn
BARN_REPO=/absolute/local/repository barn up
```

## Trust and verification

Release binaries embed both production Ed25519 public verification keys (private signing keys live outside the source repository). Catalog activation rejects unknown signing keys, malformed JSON, conflicting content at the same revision number (equivocation), and revisions lower than the repository's highest accepted revision unless `--allow-downgrade` is passed to `barn image sync`.

Every cached or imported image must be a standalone `qcow2` file matching its declared byte size and SHA-256 digest, with no backing file, external data file, encryption, or unknown incompatible `qcow2` feature bits. Barn marks verified base images read-only and creates copy-on-write overlay disks for each VM node.

```bash
barn update
barn image sync --repo https://repo.example/barn \
  https://repo.example/barn/catalog.json
barn image sync --repo /srv/barn --allow-downgrade /srv/barn/catalog.json
barn image reset --repo /srv/barn
```

- **`barn update`** fetches, verifies, and activates the current catalog from `--repo` or `--mirror`.
- **`barn image sync`** activates a catalog from an explicit URL or file path (for unsigned custom repositories, the source path must be `<repo>/catalog.json`) and supports `--allow-downgrade`.
- **`barn image reset`** reverts the active catalog for `--repo` (or default repo) back to the binary's embedded catalog while keeping the recorded highest-revision watermark intact.

## Static repository format

A static Barn image repository uses the following directory layout:

```filetree {title="/srv/barn"}
repo.yaml # Authoritative human-edited policy and version declarations (schema 1)
catalog.json # Generated runtime image catalog with digests and sizes (schema 3)
catalog.json.minisig # Minisign signature (required for official and HTTP repositories)
images/
  <image>-<version>-<arch>.qcow2 # Immutable qcow2 image artifacts
```

`repo.yaml` (`schema: 1`) declares defaults, aliases, channels, versions, architectures, boot modes, support status, `source_user` (for example, `rocky` upstream or `dba` after official normalization), and optional upstream provenance URLs—without manual checksums or byte sizes. `barn repo build` inspects the `qcow2` files and generates `catalog.json` (`schema: 3`) with each variant's filename, SHA-256 digest, file size, and virtual disk capacity.

```yaml {title="repo.yaml"}
schema: 1
revision: 1
defaults: { image: u24, channel: stable, arch: native, boot: uefi }
images:
  u24:
    aliases: [ubuntu24, noble, ubuntu]
    channels: { stable: "1" }
    versions:
      "1":
        status: unknown
        variants:
          amd64: {}
          arm64: {}
```

When a variant omits `file`, Barn expects `images/<image>-<version>-<arch>.qcow2` (for example, `images/u24-1-amd64.qcow2` and `images/u24-1-arm64.qcow2`).

Repository management rules (`barn repo scan|build|verify /absolute/repo`):

- Repository roots accept relative paths, `~/`, and directory symlinks. The root and `images/` may be shared writable directories. `repo.yaml` may link to a non-empty regular file up to 4 MiB. Artifact entries remain regular files; `catalog.json` output symlinks are not overwritten.
- Boot mode inherits along `variant` → `family` → `defaults.boot`; status inherits along `variant` → `version` → `unknown`. Every family must define the default channel pointing to an existing version, and family/alias names must be unique and cannot start with `local-`. Avoid reassigning built-in aliases (`ubuntu`, `debian`, `rocky`, etc.) to different families, because [inventory parsing](../configuration/#vm-variables) normalizes built-in aliases via the embedded catalog first.
- Channels and dot-separated numeric prefixes (`el9@9.7`, `el9@9`) resolve to an exact version key when present or the highest matching numeric version, yielding an immutable artifact identity `(image, exact version, arch)`:
  ```text
  d13:stable + native
    -> d13@20260914.2601.2 + arm64
    -> images/d13-20260914.2601.2-arm64.qcow2
  ```
- **`barn repo scan`** is read-only and does not require `qemu-img`; it exits `0` while reporting any `missing`, `unsafe`, or `untracked` files in its output arrays (automation must check that `missing` and `unsafe` are empty).
- **`barn repo build`** and **`barn repo verify`** require `qemu-img`. `build` validates `repo.yaml`, inspects every `qcow2` artifact, and atomically writes `catalog.json` (failing if any declared artifact is `missing` or `unsafe`, and omitting `untracked` files). `verify` checks that the existing `catalog.json` matches a fresh build byte-for-byte. Increment `revision` whenever catalog contents change, upload immutable `.qcow2` files before updating `catalog.json` and `catalog.json.minisig`, and publish the catalog and signature together.

<span id="local-image-import"></span>

## Local layout and imports

Barn stores cached catalogs, downloaded images, and local imports under `$BARN_HOME/images` (default `~/.barn/images`):

```filetree {title="$BARN_HOME/images"}
manifests/ # Active catalog.json and highest accepted revision per repository
local-images.json # Registry of named local-* image aliases
local/
  <sha256>.qcow2 # Imported local qcow2 files indexed by content digest
d13/
  d13-20260914.2601.2-arm64.qcow2 # Verified read-only catalog artifacts by family
u24/
  u24-20260926.0.0-arm64.qcow2
```

Import a local `qcow2` file into the cache or register it under a `local-*` alias:

```bash
barn image import --sha256 <digest> /path/to/base.qcow2
barn image import --name local-mybase --boot uefi \
  --source-user ubuntu --sha256 <digest> /path/to/base.qcow2
```

Import rules:

- `image import` accepts relative paths, `~/`, and symlinks to regular files, and still requires `qemu-img`. Local images and catalog artifacts with declared sizes no longer have an 8 GiB ceiling. Reads are bounded by the actual or declared size; downloads stop on overflow. Legacy downloads without a declared artifact size retain an 8 GiB bound. Optional `--sha256` still verifies an expected digest.
- `image import` copies and validates the `qcow2` container as-is without modifying guest credentials, installing `cloud-init`, or booting the image.
- Source filenames may contain spaces or Unicode and need no particular extension; Barn validates the qcow2 contents. New imports use `local/<sha256>.qcow2`, so different images can share a source filename and identical bytes reuse a cache entry. Existing aliases keep their original cache paths when reimported. The former 256-alias ceiling is removed; updates exceeding the 1 MiB registry metadata limit fail before changing existing aliases.
- Named imports (`--name local-<alias>`) must include `--boot bios|uefi` and `--source-user <user>`, and are recorded for the host's native architecture (to distribute foreign-architecture images, use a static repository). Aliases are immutable once registered and can be referenced in `barn.yml` via `vm_image: local-mybase`. Unnamed imports simply pre-populate the cache.

## Pruning

```bash
barn image prune --dry-run
barn image prune --yes
```

`barn image prune` (or `barn image prune --dry-run`) lists candidate files that can be reclaimed; passing `--yes` deletes them.

`prune` protects all artifacts referenced by the selected repository's active catalog, all base image digests used by currently applied nodes, and all registered `local-*` aliases (preserving cached images across `destroy` and `purge`). Only unreferenced images from older catalogs or other repositories and recognized stale staging files become candidates; quarantined `.corrupt-*` files are left in place for manual inspection, and unexpected/unsafe files cause an error. Always preview with `--dry-run` (passing `--repo` when checking a custom repository), as `prune --yes` deletes candidates sequentially without rolling back earlier deletions if a later file fails inspection.

To export the binary's embedded schema-3 catalog byte-for-byte when bootstrapping a mirror, run `go run ./tools/catalogexport /absolute/new/catalog.json`. Any public catalog published at the embedded revision number must match those exact bytes.
