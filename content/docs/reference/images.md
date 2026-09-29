---
title: Images
description: Signed catalogs, built-in aliases, repository selection, local cache verification, imports, and pruning.
weight: 30
icon: fa-solid fa-hard-drive
---

Barn uses a materialized static-file Catalog plus immutable qcow2 artifacts.
Official and HTTP Catalogs are signed; explicitly selected local and HTTPS
repositories may be unsigned. A Catalog update does not require a new Barn
binary, but the binary decides which signing keys and image safety rules are
trusted.

> [!WARNING]
> EL7, EL9 9.3/9.6, and EL10 10.0 are `deprecated` compatibility images. All
> other built-in versions are `supported`.

## Aliases and pull order

Barn 0.9.0 embeds Catalog `2026092902`: 9 families and 39 artifacts. `el7` is
amd64-only; every other family has amd64 and arm64 artifacts. EL9 includes 9.3, 9.6, 9.7, and 9.8;
EL10 includes 10.0, 10.1, and 10.2. `u24:stable` (Ubuntu 24.04) on the native
architecture is the default request.

The stable versions below include both amd64 and arm64. This is the
embedded Catalog snapshot, not a live repository listing. Run `barn update`
then `barn image list` to inspect the currently selected repository. Dated
public endpoint checks and guest point-release observations are recorded in
[Status](../../about/status/).

| Family | Embedded stable | Distribution series |
|---|---|---|
| `d12` | `20260923.2610.1` | Debian 12 |
| `d13` | `20260914.2601.2` | Debian 13 |
| `el8` | `8.10.20240528.2` | Rocky Linux 8.10 |
| `el9` | `9.8.20260525.2` | Rocky Linux 9.8 |
| `u22` | `20260926.0.0` | Ubuntu 22.04 LTS |
| `u24` | `20260926.0.0` | Ubuntu 24.04 LTS |
| `u26` | `20260927.0.0` | Ubuntu 26.04 LTS |

Debian retains offline-installed XFS tools and the generated `en_US.UTF-8`
locale, with `C.UTF-8` still the default. Ubuntu retains Canonical's original
image bytes; cloud-init configures accounts and networking at startup.
The Debian 12 upstream build dated September 23 still lacks XFS tools and
`en_US.UTF-8`, so those adjustments remain necessary. The Ubuntu builds above
already include both; their amd64 and arm64 guests passed locale and XFS
data-disk checks on September 29.
A Catalog refresh changes newly resolved `stable` requests. Existing VMs and
explicitly pinned versions continue using their original base images.

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

Catalog status values are advisory rather than an activation switch:
`supported` has passed the declared support gate; `testing` is available for
explicit test/risk acceptance but is not supported; `deprecated` is retained
only for EOL compatibility; and `unknown` has no support classification.
Non-`supported` entries remain runnable and print a warning.

For a pull, Barn:

1. reads the selected repository's active local Catalog once for the complete
   command: the Catalog embedded in this build, or the one last activated for
   that repository by `barn update` or `image sync`;
2. resolves `image[:channel]` or `image@version-prefix`, defaulting to
   `u24:stable` with the official Catalog; standalone `image pull` defaults to
   the native architecture and accepts `--arch`, while lifecycle resolution
   honors `vm_arch`;
3. reuses a local file only after size, SHA-256, and qcow2 checks pass;
4. otherwise downloads the exact Catalog-named artifact, with retries and
   resumption; the two official repositories can fall back to one another,
   while custom repositories remain exclusive. All accepted bytes must match
   the Catalog. An immutable upstream URL is provenance, not a fallback.

Released builds use `https://repo.pigsty.io/barn` by default. Long-only
`--mirror` selects `https://repo.pigsty.cc/barn`; precedence is `--repo`,
`--mirror`, `BARN_REPO`, then the global default. Both official roots retain
canonical signed-Catalog trust. Repository selection determines both the local
Catalog slot and the source of downloads. Keep selecting the same custom
repository even when its image bytes are cached. Barn never refreshes the
Catalog on its own; ordinary image resolution can work offline with an active
local Catalog and verified cache. Run
`barn update` to fetch, verify, and activate the selected repository's current
Catalog. Catalog updates use that selected source; a failed update is an error.
An image download fails when none of its permitted sources supplies verified bytes.
Changing `--repo` alone does not fetch or activate that repository's Catalog;
run `barn update --repo <root>` before using its custom aliases.

Verified writable cache files are made read-only again. A damaged, unreferenced
cache file is preserved with a `.corrupt-<timestamp>` suffix before replacement;
a base image still referenced by a VM is kept in place and reported as an error.

## Runtime policy

Matching architectures use native HVF/KVM except one catalogued incompatibility:
the stock EL8 arm64 64K-granule kernel cannot run through Apple HVF, so Apple
Silicon uses visible same-architecture TCG automatically. Explicit foreign
`vm_arch` also uses TCG. amd64-on-arm64 uses a single translation thread to
preserve x86 memory ordering. TCG results are not performance evidence.

EL7 is deliberately limited to native Linux/amd64. Linux setup installs only
the native QEMU family; foreign architectures require the matching system
emulator and UEFI firmware before `up` or `recreate` can proceed. For Catalog images, `plan`
resolves the intended image and runtime without requiring those tools. Named
`local-*` imports are byte-checked during resolution and still need `qemu-img`.

```bash
barn image pull d13 --mirror
barn image pull d13 --repo https://mirror.example/barn
BARN_REPO=/absolute/local/repository barn up
```

Unsigned repositories must be local paths or HTTPS. HTTP repositories require a
Catalog signed by a trusted key. Immutable upstream artifact URLs must be HTTPS.

## Trust and verification

Current ordinary builds embed both production public verification keys. The
private signing keys are external to the source repository. Catalog activation
rejects unknown keys, malformed content, equivocation, and revisions below the
repository-scoped high-water mark unless the operator explicitly allows a
downgrade.

Every accepted image must be a size- and SHA-256-matched plain qcow2 with no
backing file, external data file, encryption, or unknown incompatible feature.
Verified base images become read-only; node root disks are overlays and never
modify the base.

```bash
barn update
barn image sync --repo https://repo.example/barn \
  https://repo.example/barn/catalog.json
barn image sync --repo /absolute/repo --allow-downgrade /absolute/repo/catalog.json
barn image reset
```

`image reset` restores the embedded Catalog but keeps the anti-rollback
high-water mark.

`barn update` checks the repository now and activates a newer Catalog. Barn
never refreshes the Catalog on its own; the Catalog embedded in each release is
used until you update. `image sync` is the recovery path for an exact URL or
file, including a downgrade.

For repository-scoped recovery, pass the same root explicitly:

```bash
barn image sync --repo /srv/barn --allow-downgrade /srv/barn/catalog.json
barn image reset --repo /srv/barn
```

`--repo` selects the independent active-Catalog and high-water slot. The source
argument does not change this selection. `image sync` and `image reset` accept
`--repo`, but not `--mirror`; when `--repo` is omitted they use `BARN_REPO`
or the compiled default. For an unsigned custom Catalog, the exact source must
be the selected root's `catalog.json`.

## Static repository format

The published root is deliberately small:

```text
barn/
├── repo.yaml
├── catalog.json
├── catalog.json.minisig       # required for official and HTTP repositories
└── images/
    └── <image>-<version>-<arch>.qcow2
```

`repo.yaml` stores author intent: defaults, aliases, channels, exact versions,
architectures, boot mode, status, and optional provenance-only upstream URLs.
`source_user` records the image's declared source login identity, for example
`rocky` in an upstream image or `dba` after Barn's official normalization.
The pipeline takes the upstream account separately when sanitizing a candidate.
Catalog/import metadata does not replace the deployment SSH user (`dba` by
default) or itself normalize the image. The file contains no generated
checksum or size fields. `catalog.json` uses the same logical tree but
materializes each variant's file, SHA-256, artifact size, and virtual size.
`repo.yaml` is `schema: 1`; the generated `catalog.json` is the schema-3
Catalog that Barn embeds and signs.

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

Channels and numeric prefixes are movable selectors. An exact key wins;
otherwise a prefix matches on dot-component boundaries and chooses the
numerically newest version (`el9@9.7` selects the newest 9.7 build, while
`el9@9` selects the newest 9.x release). The immutable artifact identity remains
`(image, exact version, arch)`:

```text
d13:stable + native
  -> d13@20260914.2601.2 + arm64
  -> images/d13-20260914.2601.2-arm64.qcow2
```

`barn repo scan` is read-only. `build` performs strict YAML validation,
full qcow2 inspection/checking, and atomic Catalog replacement without changing
`repo.yaml` or QCOW bytes. `verify` requires the generated Catalog bytes to
match a fresh materialization exactly. `build` and `verify` require local
`qemu-img`; `scan` does not. Build on a QEMU host, then publish immutable
artifacts first and the Catalog
plus its matching signature last. Update a signed Catalog/signature pair
together where possible; an inconsistent pair fails verification. Increase
`revision` when changing Catalog contents.

## Local layout and imports

Images live under `BARN_HOME/images` (default `~/.barn/images`): family
directories contain downloaded artifacts, `manifests/` stores the active
Catalog with an independent high-water entry per repository, and `local/` plus
`local-images.json` hold imports.

```bash
barn image import --sha256 <digest> /path/to/base.qcow2
barn image import --name local-mybase --boot uefi \
  --source-user ubuntu --sha256 <digest> /path/to/base.qcow2
```

The expected `--sha256` is optional in the CLI; supplying an independently
obtained trusted digest adds an explicit authenticity check to the mandatory qcow2
inspection. Import copies and verifies the file; it does not clean credentials,
install cloud-init, detect the guest CPU architecture, or prove that it boots.

Named local aliases must begin with `local-`, so a future signed Catalog cannot
shadow them. `--name`, `--boot`, and `--source-user` must be supplied together.
A named import records the importing host's native architecture; there is no
`image import --arch` option. Use a static repository with explicit variants
for foreign-architecture artifacts. Aliases are immutable: choose a new name
for different bytes or metadata. Use `vm_image: local-mybase` in an inventory
to select a named import; unnamed imports only populate the cache.

## Pruning

```bash
barn image prune --dry-run
barn image prune --yes
```

Bare `prune` and `--dry-run` only report candidates; `--yes` deletes them.
Prune protects the union of all artifacts in the selected active Catalog,
applied node image digests, and registered local aliases. Therefore a cached
Catalog image or named import is retained even when no VM uses it. Unprotected
images and recognized stale staging files are candidates; unsafe or damaged
files cause an error. Use the same `--repo` when inspecting a custom Catalog's
cache policy. Images remain cached after `destroy`, `destroy --purge`, and `purge`.

The compiled schema-3 Catalog can be exported byte-for-byte with
`go run ./tools/catalogexport /absolute/new/catalog.json`. A public Catalog at
the embedded version must use those exact bytes; same-version different bytes
are rejected as equivocation. Release signing and image Catalog signing remain
separate trust domains.
