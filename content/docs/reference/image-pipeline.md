---
title: Image Pipeline
description: Validate or offline-normalize an explicit qcow2 candidate without downloading, uploading, or signing it.
weight: 40
icon: fa-solid fa-shield-halved
---

Use `packaging/image-pipeline/build.sh` to validate or normalize one downloaded immutable qcow2 file against an independently obtained SHA-256.
This low-level tool works locally: it does not download, upload, read signing keys, or modify Barn runtime or network state.
Its output is a candidate, not an image approved as `supported`.

Run these commands from the Barn source checkout. The build host requires Python 3 and `qemu-img`.
`offline` also requires working libguestfs tools: `virt-customize` and `virt-cat`.
These dependencies are separate from those that `barn setup` installs to run VMs.
Keep source images, package caches, and output bundles outside the Git checkout.
The repository tracks recipes and locks, not downloaded or generated images.
`--arch` declares the candidate architecture. It does not convert the image or verify that libguestfs can execute that guest on the build host.

## Modes

- `validate`: Copies and re-hashes the image, forces qcow2 inspection, and validates that the backing chain contains one image.
  It runs `qemu-img check` and emits an evidence bundle that is not ready for publication. It does not change guest credentials.
- `offline`: Also uses libguestfs `virt-customize --no-network` and `virt-cat` on the staged copy.
  It rejects unrelated UID/GID 88 occupants and normalizes the locked `dba`/`admin` identity.
  It disables SSH password login and SSH login as root. It removes keys, history, host identity, and cloud-init cache.
  It restores targeted SELinux labels and reads back a deterministic marker.

The low-level builder defaults to `--profile base`. Each profile has the following scope:

| Profile | Additional behavior | Package inputs |
|---|---|---|
| `base` | Identity and credential normalization only | none; package arguments rejected |
| `el8` | Python 3, SSH include, legacy network cleanup, chrony and SELinux handling | locked RPM dependency set |
| `el9` | Legacy network cleanup and identity normalization | none; package arguments rejected |
| `d12`, `d13` | XFS tools and locale verification | locked DEB dependency set |

`validate` accepts only `base`.
With `el8`, `d12`, or `d13`, `offline` requires both `--package-lock` and `--package-cache`.
The canonical JSON lock must match the profile and architecture.
For official images, use the wrapper in the next section to supply the pinned package inputs.
Select tool paths with `--qemu-img`, `--virt-customize`, and `--virt-cat`.
You can also set their defaults with `QEMU_IMG`, `VIRT_CUSTOMIZE`, and `VIRT_CAT`.

## Official candidate matrix

`build-official.py` uses the same offline process for eight fixed targets: Debian 12/13 and Rocky Linux 8/9, each on amd64 and arm64.
`official-v1.json` pins every upstream qcow2, RPM/DEB input, release name, digest, and source epoch.

```bash
./packaging/image-pipeline/build-official.py --list

./packaging/image-pipeline/build-official.py \
  --source-cache /absolute/source-cache \
  --package-cache /absolute/package-cache \
  --output /absolute/existing-output-root \
  --target d13/arm64 --fetch
```

Without `--fetch`, all locked inputs must already exist in the two canonical cache directories.
Before running the wrapper, create both cache roots and the build output root. Use absolute canonical paths.
With `--fetch`, the wrapper downloads only pinned HTTPS URLs.
It rejects digest mismatches before offline normalization.

Debian 12/13 install the locked XFS userspace tools and dependencies.
Rocky Linux 8 installs the locked `python36` and `python3-pip` RPMs. Rocky Linux 9 needs no extra package input.
When cloud-init enables NTP, Rocky Linux 8 uses its shipped RHEL chrony template and `chronyd` service.
Normalization restores SELinux labels without an additional package set.

Debian also generates `en_US.UTF-8` and retains `C.UTF-8` as the default.
Both the guest normalization script and host-side marker validation check these requirements, including after a base image update.
Ubuntu uses dated, unmodified official images outside this offline matrix.

Each result remains an unsigned `testing` candidate.
To build the complete matrix, omit `--target`. To select several targets, repeat the flag.
`--list` shows the exact releases pinned by this checkout.
The matrix currently contains Debian `20260923.2610.1`/`20260914.2601.2` and Rocky Linux `8.10.20240528.3`/`9.8.20260525.2`.

Assembly takes **parent directories containing the named bundles**, not the
individual bundle directories. If all eight builds were written below one
output root, assemble them with:

```bash
./packaging/image-pipeline/build-official.py \
  --assemble-from /absolute/existing-output-root \
  --output /absolute/new-candidate-repository
```

If builds are split across roots, repeat `--assemble-from`.
Assembly requires exactly one bundle for each of the eight targets. It creates a new static repository.
It runs `barn repo build` and `verify` with `barn` on PATH, or `--barn /absolute/path/to/barn`.
Build mode requires an existing output root. The assembly destination must not exist.
The generated channels use `candidate`, not `stable`. For example, use `d13:candidate`.
Assembly does not perform native smoke tests, signing, uploads, or image catalog publication.

## Validate one downloaded image

```bash
SOURCE_DATE_EPOCH=1787486400

./packaging/image-pipeline/build.sh \
  --mode validate \
  --source /absolute/source.qcow2 \
  --expected-sha256 <digest> \
  --output /absolute/new/evidence-directory \
  --name u24 --release 20260801.0.0 --arch amd64 \
  --source-user ubuntu --boot uefi \
  --source-uri https://immutable.example/source.qcow2 \
  --artifact-url 'https://images.example/u24/{sha256}.qcow2' \
  --license NOASSERTION \
  --source-date-epoch "$SOURCE_DATE_EPOCH" \
  --manifest-version 2026082903
```

Source and output paths must be absolute. The source must be canonical, regular, non-symlinked, stable during copying, and at most 16 GiB.
The output path must not exist, but its parent directory must already exist.

The pipeline's 16 GiB source allowance exceeds Barn 0.9.1's **8 GiB runtime/repository artifact limit**.
Pipeline success does not guarantee that Barn can import, assemble, or download the resulting qcow2 file.
Check the artifact's file size as well as its virtual capacity.
The builder uses an exclusive adjacent lock, mode-0700 staging, and one final rename.
On failure, it removes only its guarded staging directory.

Every successful bundle contains the read-only qcow2, recipe, SLSA provenance,
SPDX SBOM for the build scope, `manifest-candidate.json` (`testing`), validation evidence,
and checksums:

| File | Purpose |
|---|---|
| `<name>-<release>-<arch>-<digest-prefix>.qcow2` | validated candidate bytes |
| `build-recipe.json` | invocation, recipe/tool identities, and input records |
| `manifest-candidate.json` | unsigned testing candidate metadata |
| `provenance.intoto.json` | SLSA provenance statement |
| `sbom.spdx.json` | declared inputs and build scope |
| `validation.json` | before/after qcow2 checks, normalization result, and release checks that remain incomplete |
| `checksums.txt` | SHA-256 of bundle files |
| `package-lock.json` | included when the profile uses package inputs |

The candidate manifest is a pipeline evidence format. Repository assembly produces the runtime schema-3 `catalog.json`.
The SPDX file describes the declared input and build scope. It is not a complete package inventory of the guest filesystem.
Signing occurs outside this pipeline.
With fixed inputs and tools, validate mode produces identical bytes.
For offline mode, build the same candidate twice and compare the results before using them as release evidence.

A release still requires runtime smoke tests on each declared host and guest path.
It also requires review of support status and provenance, a new image catalog revision, production signing, and public artifact verification.
Build success alone does not authorize `supported` status or establish that a candidate is publicly available.
