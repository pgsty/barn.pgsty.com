---
title: Image Repositories
description: Choose guest images, use a mirror, import a local qcow2, and prune the cache.
weight: 40
icon: fa-solid fa-box-archive
---

Normal use needs no image command first: `farrow up` resolves `u24:stable` for
the native host architecture and pulls the resulting immutable version.
Farrow uses the Catalog embedded in the installed build until you run
`farrow update`, which fetches, verifies, and activates the repository's current
Catalog. Nothing refreshes it automatically; `image sync` explicitly activates
an exact URL or file for recovery.

## Choose an image

Inspect the available aliases:

```bash
farrow image list
farrow image info u24
farrow image info u24:stable
```

Built-in families are `el7`, `el8`, `el9`, `el10`, `d12`, `d13`, `u22`,
`u24`, and `u26`. A bare name selects `stable`; `name:channel` selects a
channel. An exact `name@version` key wins; a shorter numeric selector chooses
the newest matching version on dot-component boundaries:

```yaml
all:
  vars:
    vm_image: el9
    vm_version: "9.7"
```

Here `9.7` selects the newest 9.7.x build; `9` selects the newest 9.x release.
Use `vm_image: el9:stable` and remove `vm_version` when the repository's movable
stable channel is the intended policy. A separate `vm_version` cannot be
combined with `:channel` or `@version` in `vm_image`.

Run `farrow plan` after editing the inventory. Changing an existing node's image
request requires an explicit `farrow recreate <node>`; `up` reports the definition
drift instead of rebuilding it. Updating the Catalog alone does not change
existing nodes or their stored base-image identity. Newly created or explicitly
recreated nodes resolve the selector against the active Catalog.

For a reproducible lab, pin the complete version shown by `image info`, rather
than a movable channel or a numeric prefix:

```yaml
all:
  vars:
    vm_image: d13@20260914.2601.1
```

Quote numeric `vm_version` values in YAML so their original text is preserved.

> [!WARNING]
> Built-in versions are `supported` except deprecated compatibility images:
> EOL `el7`, EL9 9.3/9.6, and EL10 10.0.

## Use a mirror

Released builds use `https://repo.pigsty.io/farrow` by default. Select the
official China repository for one command with long-only `--mirror`, or name a
custom root with `--repo`:

```bash
farrow image pull u24 --mirror
farrow up --mirror
farrow update --repo https://mirror.example/farrow
farrow image pull u24 --repo https://mirror.example/farrow
farrow up --repo https://mirror.example/farrow
```

Or set the default repository for the current shell:

```bash
export FARROW_REPO=https://mirror.example/farrow
farrow update
farrow up
```

Selection precedence is `--repo`, `--mirror`, `FARROW_REPO`, then the global
default. `--mirror` resolves to `https://repo.pigsty.cc/farrow` and both
official roots retain canonical signed-Catalog trust. `FARROW_REPO` may also be
an absolute local directory. Explicit local and HTTPS repositories may use an
unsigned Catalog; HTTP repositories require a Catalog signed by a trusted key.
Artifact size, SHA-256, and qcow2 structure are always verified.

Image downloads retry transient failures and resume interrupted transfers. Since
0.7.0, the two official repositories can fall back to one another if the selected
endpoint cannot supply an image; the same Catalog size and digest must still
match. Custom repositories remain exclusive. Catalog upstream URLs are
provenance, never an alternate download source.

This fallback concerns image artifacts. `farrow update` fetches the selected
repository's Catalog; `image sync` reads the exact URL or file you supply.
Neither command upgrades the Farrow executable. The active Catalog is scoped
to the selected repository. A new `--repo` uses the embedded Catalog until you
activate that root's Catalog; changing the download source alone does not make
custom aliases appear.

## Build a static repository

A repository is an ordinary directory that can be copied with `rsync` or served
by a static HTTP server:

```text
farrow/
├── repo.yaml
├── catalog.json
├── catalog.json.minisig       # required for official and HTTP repositories
└── images/
    └── d13-1-arm64.qcow2
```

`repo.yaml` is the only human-maintained source. For the single arm64 image
shown above, a minimal complete source is:

```yaml
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

Place your independently verified, cloud-init-capable image at
`/srv/farrow/images/d13-1-arm64.qcow2`. Use `amd64` in both the filename and
variant for an x86 guest, and set `source_user` to the image's source identity.
The repository root must be an absolute, non-symlink directory that is not
writable by group or others. Generate `catalog.json` locally:

```bash
farrow repo scan /srv/farrow
farrow repo build /srv/farrow
farrow repo verify /srv/farrow
```

Scan is read-only. Build never changes `repo.yaml` or image bytes; it performs a
full `qemu-img check` and materializes file names, SHA-256, artifact size, and
virtual size. `build` and `verify` require local `qemu-img`; `scan` does not.
Build on a machine with QEMU, then publish immutable QCOW files first and
`catalog.json` with its matching signature last. The local/HTTPS example may
remain unsigned; plain HTTP and official repositories require a trusted
signature. Increase `revision` whenever Catalog contents change.

Activate and inspect this local repository before creating VMs:

```bash
farrow update --repo /srv/farrow
farrow image info d13 --arch arm64 --repo /srv/farrow
farrow image pull d13 --arch arm64 --repo /srv/farrow
```

Use the same `--repo /srv/farrow` for `plan`, `up`, and `recreate`, or export
`FARROW_REPO=/srv/farrow`. In the Inventory select `vm_image: d13@1` and
`vm_arch: arm64`; importing a Catalog does not rewrite Inventory defaults.
`farrow image reset --repo /srv/farrow` restores the embedded Catalog for that
root while preserving its anti-rollback history.

## Import and prune

For a single custom image on the host's native architecture, import it with
an independently obtained digest. `--sha256` is optional in the CLI but is
recommended when you have a trusted digest:

```bash
farrow image import --name local-mybase --boot uefi \
  --source-user ubuntu --sha256 <digest> /path/to/base.qcow2
```

Custom aliases must begin with `local-`; `--name`, `--boot`, and `--source-user`
are required together. Import checks the qcow2 and copies it into Farrow's
cache without preparing its guest software. The image must already support
Farrow's cloud-init bootstrap. Named imports record the host architecture, so
use a static repository for foreign-architecture images. Select the alias with
`vm_image: local-mybase`, then run `farrow plan`.

Prune protects every image in the selected active Catalog, every applied node
image, and every registered local alias. It therefore does not empty the
cache merely because all VMs were destroyed. Inspect candidates before deletion:

```bash
farrow image prune --dry-run
farrow image prune --yes
```

See [Images](../../reference/images/) for signatures, rollback protection,
cache layout, architecture, and TCG rules. See the
[Image Pipeline](../../reference/image-pipeline/) for preparing image candidates
and the separate checks required before publication.
