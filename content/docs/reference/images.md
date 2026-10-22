---
title: Images
description: Signed catalogs, built-in aliases, repository selection, local cache verification, imports, and pruning.
weight: 30
icon: fa-solid fa-hard-drive
---

Barn uses a static image catalog and immutable qcow2 artifacts.
Official and HTTP image catalogs require signatures. Explicitly selected local and HTTPS repositories may be unsigned.
Updating the image catalog does not require a new Barn binary.
The binary determines which signing keys and image safety rules Barn trusts.

> [!WARNING]
> EL7, EL9 9.3/9.6, and EL10 10.0 are `deprecated` compatibility images. All
> other built-in versions are `supported`.

## Aliases and pull order

Barn 0.9.1 embeds image catalog `2026093001`: 9 families and 41 artifacts. `el7` is
amd64-only; every other family has amd64 and arm64 artifacts. EL9 includes 9.3, 9.6, 9.7, and 9.8;
EL10 includes 10.0, 10.1, and 10.2. `u24:stable` (Ubuntu 24.04) on the native
architecture is the default request.

The stable versions below include amd64 and arm64, except `el7`, which includes only amd64.
This table describes the embedded image catalog snapshot, not the current repository contents.
Run `barn update`, then `barn image list` to inspect the selected repository.
For host compatibility and restrictions, see [Platforms and Limits](../../about/status/).

| Family | Embedded stable | Accepted aliases |
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

The Ubuntu families are 22.04, 24.04, and 26.04 LTS respectively. `el7` is
CentOS Linux 7.9; `el8`, `el9`, and `el10` use Rocky Linux.

Debian retains the offline-installed XFS tools and generated `en_US.UTF-8` locale. `C.UTF-8` remains the default.
Ubuntu retains Canonical's original image bytes. Cloud-init configures accounts and networking at startup.
An image catalog update changes newly resolved `stable` requests.
Existing VMs and explicitly pinned versions continue to use their original base images.
If the inventory selects a channel or numeric prefix that changed, a later `plan` or `up` can detect drift.
Replacing the existing node then requires `recreate`.

| Alias | Distribution | Architectures | Boot | Status |
|---|---|---|---|---|
| `el7` | CentOS Linux 7.9 / 2211 | amd64 | BIOS | deprecated |
| `el8` | Rocky Linux 8.10 | amd64, arm64 | UEFI | supported |
| `el9` | Rocky Linux 9.7 / 9.8 | amd64, arm64 | UEFI | supported |
| `el9` | Rocky Linux 9.3 / 9.6 | amd64, arm64 | UEFI | deprecated |
| `el10` | Rocky Linux 10.1 / 10.2 | amd64, arm64 | UEFI | supported |
| `el10` | Rocky Linux 10.0 | amd64, arm64 | UEFI | deprecated |
| `d12`, `d13` | Debian | amd64, arm64 | UEFI | supported |
| `u22`, `u24`, `u26` | Ubuntu | amd64, arm64 | UEFI | supported |

```bash
barn image list
barn image info d13
barn image info d13:stable
barn image info el9@9.7
barn image pull d13@20260914.2601.2
barn image pull d13 --arch arm64
barn update
```

`image list` lists all versions and architectures, including registered local aliases. It has no `--arch` filter.
`image info` defaults to the native architecture, like `pull`.
You can inspect an uncached image catalog entry without QEMU. If a cache entry exists, Barn verifies it and requires `qemu-img`.
Neither `list` nor `info` downloads an image.

Image catalog status describes support policy, not whether an image can run.
`supported` means the image passed the declared support checks.
`testing` permits explicit testing with accepted risk, but does not indicate support.
`deprecated` retains an image only for EOL compatibility. `unknown` means the image has no support classification.
Non-`supported` entries remain runnable and produce a warning.

For a pull, Barn:

1. Reads the selected repository's active local image catalog once for the whole command.
   This is the embedded image catalog or the one last activated for that repository by `barn update` or `image sync`.
2. Resolves `image[:channel]` or `image@version-prefix`. With the official image catalog, the default is `u24:stable`.
   Standalone `image pull` defaults to the native architecture and accepts `--arch`. Lifecycle commands use `vm_arch`.
3. Reuses a local file only after its size, SHA-256, and qcow2 checks pass.
4. Otherwise, downloads the exact artifact named by the image catalog, with retries and resumption.
   The two official repositories can fall back to each other. A custom repository remains the only source.
   Accepted bytes must match the image catalog. An immutable upstream URL records provenance; it is not a fallback.

Released builds default to `https://repo.pigsty.io/barn`.
The long-only `--mirror` flag selects `https://repo.pigsty.cc/barn`.
Precedence is `--repo`, `--mirror`, `BARN_REPO`, then the global default.
Both official roots require trusted image catalog signatures.

Repository selection determines the local image catalog record and download source.
Continue to select the same custom repository even when its image bytes are cached.
Barn does not refresh the image catalog automatically.
With an active local image catalog and verified cache, ordinary image resolution can work offline.

Run `barn update` to fetch, verify, and activate the selected repository's current image catalog.
Catalog updates use only that source and fail if it cannot supply a valid catalog.
Image downloads can try the permitted fallback sources and fail if none supplies verified bytes.

Changing `--repo` alone does not fetch or activate that repository's image catalog.
Before using its custom aliases, run `barn update --repo <root>`.

Barn restores read-only permissions on verified writable cache files.
Before replacing a damaged, unreferenced cache file, Barn preserves it with a `.corrupt-<timestamp>` suffix.
If a VM still references the base image, Barn keeps it in place and reports an error.

## Runtime policy

Matching architectures use native HVF/KVM, with one known image exception.
The stock EL8 arm64 64K-granule kernel cannot run through Apple HVF.
On Apple Silicon, Barn automatically selects and reports same-architecture TCG for that image.
Explicit foreign `vm_arch` also uses TCG.
For amd64 guests on arm64 hosts, Barn uses one translation thread to preserve x86 memory ordering.
TCG results are not performance evidence.

EL7 supports only native Linux/amd64. Linux setup installs only the native QEMU family.
Before `up` or `recreate` can use a foreign architecture, install the matching system emulator and UEFI firmware.
For image catalog entries, `plan` resolves the image and runtime without those tools.
During resolution, Barn checks named `local-*` import bytes and requires `qemu-img`.

```bash
barn image pull d13 --mirror
barn image pull d13 --repo https://mirror.example/barn
BARN_REPO=/absolute/local/repository barn up
```

Unsigned repositories must be local paths or HTTPS. HTTP repositories require an
image catalog signed by a trusted key. Immutable upstream artifact URLs must be HTTPS.

## Trust and verification

Current ordinary builds embed both production public verification keys. The source repository does not contain private signing keys.
Image catalog activation rejects unknown keys, malformed content, and different content at the same revision.
It also rejects revisions below the repository's highest accepted revision unless the operator explicitly allows a downgrade.

Every accepted image must be plain qcow2 with matching size and SHA-256.
It must have no backing file, external data file, encryption, or unknown incompatible feature.
Barn makes verified base images read-only. Node root disks use overlays and never modify the base image.

```bash
barn update
barn image sync --repo https://repo.example/barn \
  https://repo.example/barn/catalog.json
barn image sync --repo /absolute/repo --allow-downgrade /absolute/repo/catalog.json
barn image reset
```

`image reset` restores the embedded image catalog. It preserves the highest accepted revision used for downgrade protection.

Use `barn update` for a repository refresh or `image sync` for recovery from an exact URL or file, including an explicitly allowed downgrade.
Ordinary commands continue using the active local catalog.

For repository-scoped recovery, pass the same root explicitly:

```bash
barn image sync --repo /srv/barn --allow-downgrade /srv/barn/catalog.json
barn image reset --repo /srv/barn
```

`--repo` selects the independent active image catalog record and highest accepted revision.
The source argument does not change this selection.
`image sync` and `image reset` accept `--repo`, but not `--mirror`.
If you omit `--repo`, they use `BARN_REPO` or the compiled default.
For an unsigned custom image catalog, the source must be the selected root's `catalog.json`.

## Static repository format

The published root contains these files:

```text
barn/
├── repo.yaml
├── catalog.json
├── catalog.json.minisig       # required for official and HTTP repositories
└── images/
    └── <image>-<version>-<arch>.qcow2
```

`repo.yaml` stores the declared defaults, aliases, channels, exact versions, architectures, boot mode, status, and optional upstream URLs.
Upstream URLs record provenance only.
`source_user` records the image's declared source login account, such as `rocky` upstream or `dba` after Barn's official normalization.
The pipeline receives the upstream account separately when it sanitizes a candidate.
Image catalog and import metadata do not replace the deployment SSH user (`dba` by default) or normalize the image.

The policy file contains no generated checksum or size fields.
`catalog.json` uses the same logical structure and adds each variant's file, SHA-256, artifact size, and virtual size.
`repo.yaml` uses `schema: 1`. The generated `catalog.json` uses the schema-3 image catalog format embedded in Barn and used for signatures.

```yaml
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

With no explicit `file`, the two expected artifacts are
`images/u24-1-amd64.qcow2` and `images/u24-1-arm64.qcow2`. A variant may use a
safe basename override for an existing custom file.

`repo scan/build/verify` requires an absolute repository directory.
The root and its flat `images/` directory must not be symlinks or writable by group or other users.
`repo.yaml` must be a nonempty regular file, not a symlink, and at most 4 MiB.
Inside `images/`, Barn reports extra files or subdirectories without safe qcow2 basenames as unsafe.
Missing or unsafe artifacts block builds. Barn reports untracked safe qcow2 files but excludes them from the generated image catalog.
`repo scan` returns a report even if `missing` or `unsafe` is nonempty.
Automation must inspect those arrays; exit 0 alone is insufficient.

Boot mode follows variant → family → `defaults.boot`. Status follows variant → version → `unknown`.
Every family must define the default channel. Every channel must reference an existing exact version.
Family names and aliases must be unique. They cannot use the reserved `local-` prefix.
For 0.9.1 inventories, avoid redirecting a built-in alias to a different family.
[Inventory alias normalization](../configuration/#vm-variables) uses the binary's embedded mapping before it consults the custom image catalog.

Channels and numeric prefixes can resolve to different versions after an image catalog update.
An exact key takes priority. Otherwise, Barn matches the prefix at dot-component boundaries and selects the numerically newest version.
`el9@9.7` selects the newest 9.7 build. `el9@9` selects the newest 9.x release.
The immutable artifact identity remains `(image, exact version, arch)`:

```text
d13:stable + native
  -> d13@20260914.2601.2 + arm64
  -> images/d13-20260914.2601.2-arm64.qcow2
```

`barn repo scan` is read-only.
`build` strictly validates YAML, fully inspects and checks qcow2 files, and atomically replaces the image catalog.
It does not change `repo.yaml` or QCOW bytes.
`verify` requires the generated image catalog bytes to match a fresh build exactly.
`build` and `verify` require local `qemu-img`; `scan` does not.
Build on a QEMU host. Publish immutable artifacts first, then the image catalog and matching signature.
Where possible, update the image catalog and signature together. An inconsistent pair fails verification.
When image catalog contents change, increase `revision`.

## Local layout and imports

Barn stores images under `BARN_HOME/images` (default `~/.barn/images`).
Family directories contain downloaded artifacts.
`manifests/` stores the active image catalog and an independent highest accepted revision for each repository.
`local/` and `local-images.json` store imports.

```bash
barn image import --sha256 <digest> /path/to/base.qcow2
barn image import --name local-mybase --boot uefi \
  --source-user ubuntu --sha256 <digest> /path/to/base.qcow2
```

The CLI does not require `--sha256`. An independently obtained digest from a trusted source lets Barn confirm that the file matches the published content, in addition to inspecting qcow2.
Import copies and verifies the file. It does not clean credentials, install cloud-init, detect guest CPU architecture, or verify that the image boots.
Use an absolute source path to avoid ambiguity. Import requires a regular non-symlink file and `qemu-img`.

Runtime imports, downloads, and static repository artifacts have an 8 GiB file-size limit.
This limit is separate from qcow2 virtual capacity and configured root or data disk sizes.

The source basename must start with a letter or digit. It can contain only letters, digits, `.`, `_`, `+`, or `-`.
It must end in `.qcow2` or `.img`. Imported files share a filename-indexed `local/` cache.
Different bytes with the same filename conflict, even with a new alias. To keep both, rename the source file.

Named local aliases must start with `local-`. This prevents a future signed image catalog from replacing them.
Supply `--name`, `--boot`, and `--source-user` together.
A named import records the importing host's native architecture. There is no `image import --arch` option.
For foreign-architecture artifacts, use a static repository with explicit variants.
Aliases are immutable. For different bytes or metadata, choose a new name.
To select a named import, use `vm_image: local-mybase` in an inventory. Unnamed imports only populate the cache.

## Pruning

```bash
barn image prune --dry-run
barn image prune --yes
```

Without deletion flags, `prune` only reports candidates. `--dry-run` does the same. `--yes` deletes candidates.
Prune protects all artifacts in the selected active image catalog, applied node image digests, and registered local aliases.
Thus it retains a cached image catalog artifact or named import even when no VM uses it.
Unprotected images and recognized stale staging files are candidates. Unsafe or damaged files cause an error.
When inspecting a custom image catalog's cache policy, use the same `--repo`.
Images remain cached after `destroy`, `destroy --purge`, and `purge`.

Image catalog protection covers only the selected repository, not every previously activated image catalog.
Another repository's images can become candidates if no applied node or local alias protects their digest.
Review a dry run before deleting: prune does not roll back earlier deletions if inspection of a later candidate fails.
Prune does not remove quarantined `.corrupt-*` files or other files outside recognized image and staging patterns.

To export the compiled schema-3 image catalog byte-for-byte, use `go run ./tools/catalogexport /absolute/new/catalog.json`.
A public image catalog with the embedded version must use those exact bytes.
Barn rejects different bytes at the same version as equivocation.
Application checksums and image catalog signatures have different purposes. See [release engineering](../../about/engineering/).
