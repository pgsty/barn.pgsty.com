---
title: Image Pipeline
description: Validate or offline-normalize an explicit qcow2 candidate without downloading, uploading, or signing it.
weight: 40
icon: fa-solid fa-diagram-project
---

Use `packaging/image-pipeline/build.sh` in the Barn source checkout to validate or offline-normalize a downloaded `qcow2` candidate against an expected SHA-256 digest. The builder runs locally without network access, signing keys, or changes to Barn runtime state, and produces a `testing` candidate bundle ready for smoke testing and release review.

Host requirements:

- **Tools**: Python 3 and `qemu-img` for all modes; `offline` mode also requires working `libguestfs` tools (`virt-customize` and `virt-cat`). You can override tool binaries with `--qemu-img`, `--virt-customize`, and `--virt-cat` or the `QEMU_IMG`, `VIRT_CUSTOMIZE`, and `VIRT_CAT` environment variables.
- **Out-of-tree storage**: Keep source images, RPM/DEB package caches, and output directories outside the Git working tree (the repository tracks recipes and lockfiles only).
- **Architecture**: `--arch` records the target metadata architecture; run `offline` customization on a host where `libguestfs` can execute the guest's architecture.

## Modes and profiles

- **`validate`**: Copies and re-hashes the source image, verifies a single-file `qcow2` structure with `qemu-img check`, and writes an evidence bundle without modifying guest files or credentials.
- **`offline`**: Runs `virt-customize --no-network` and `virt-cat` on the staged copy to normalize guest access: it verifies that UID/GID `88` is free of unrelated accounts, configures the locked `dba`/`admin` identity, disables SSH password and root login, strips SSH host keys, shell history, machine-id, and `cloud-init` caches, restores SELinux labels, and verifies a deterministic guest marker.

`build.sh` defaults to `--profile base`. The available profiles are:

| Profile | Normalization steps | Package inputs |
|---|---|---|
| `base` | Account, sudo, SSH, and cloud-init normalization only | None (package flags rejected) |
| `el8` | Base normalization plus Python 3, SSH drop-in include, legacy network cleanup, `chronyd`, and SELinux relabeling | Locked RPM dependency set |
| `el9` | Base normalization plus legacy network cleanup and SELinux relabeling | None (package flags rejected) |
| `d12`, `d13` | Base normalization plus offline XFS userspace tools and `en_US.UTF-8` / `C.UTF-8` locale setup | Locked DEB dependency set |
{.wide}

`validate` mode accepts only `--profile base`. In `offline` mode, `el8`, `d12`, and `d13` require both `--package-lock` and `--package-cache` matching the profile and architecture. For official catalog targets, use `build-official.py` to drive these inputs automatically.

## Official candidate matrix

`packaging/image-pipeline/build-official.py` builds the eight offline-normalized official targets—Debian 12/13 (`d12`, `d13`) and Rocky Linux 8/9 (`el8`, `el9`) on `amd64` and `arm64`—using the upstream URLs, package locks, release versions, SHA-256 digests, and `SOURCE_DATE_EPOCH` pinned in `official-v1.json` (Ubuntu images use unmodified upstream cloud images outside this offline matrix).

```bash
./packaging/image-pipeline/build-official.py --list

./packaging/image-pipeline/build-official.py \
  --source-cache /absolute/source-cache \
  --package-cache /absolute/package-cache \
  --output /absolute/existing-output-root \
  --target d13/arm64 --fetch
```

Usage notes:

- Create `--source-cache`, `--package-cache`, and `--output` beforehand and pass canonical absolute paths. With `--fetch`, the wrapper downloads any missing pinned HTTPS inputs and verifies their SHA-256 digests before running `virt-customize --no-network`; without `--fetch`, all locked inputs must already be present in the cache directories.
- Omit `--target` to build all eight targets, or repeat `--target` to build a subset. `--list` prints the pinned releases in your checkout (currently Debian `20260923.2610.1` / `20260914.2601.2` and Rocky Linux `8.10.20240528.3` / `9.8.20260525.2`).

Once all eight target bundles have been built, assemble them into a candidate static repository by passing the **parent directory** (or repeating `--assemble-from` across multiple parent directories) that contains the bundle directories:

```bash
./packaging/image-pipeline/build-official.py \
  --assemble-from /absolute/existing-output-root \
  --output /absolute/new-candidate-repository
```

`--assemble-from` requires exactly one bundle for each of the eight targets and writes to a new `--output` path that does not yet exist, invoking `barn repo build` and `barn repo verify` (using `barn` on `PATH` or `--barn /absolute/path/to/barn`). The assembled repository maps its channels to `candidate` (for example `d13:candidate`) with status `testing` so you can run live VM acceptance checks before promoting images to `stable` and `supported`.

## Validate a single downloaded image

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

Path and size constraints:

- `--source` must be a canonical absolute path to a regular file (not a symlink) up to 16 GiB, and `--output` must be a new path inside an existing parent directory.
- Barn `0.9.2` limits runtime image artifacts to 8 GiB. The [unreleased source changes](../../about/unreleased/#limits) from 2026-10-30 remove that ceiling for local images and catalog artifacts with declared sizes; use a corresponding source build for larger artifacts. The pipeline itself retains its recipe bounds.
- The builder acquires an adjacent lockfile, stages work in a `0700` temporary directory, and atomically renames the completed bundle into `--output` (cleaning up only its staging directory on failure).

Each completed output bundle contains:

| File | Purpose |
|---|---|
| `<name>-<release>-<arch>-<digest-prefix>.qcow2` | Validated read-only candidate `qcow2` image |
| `build-recipe.json` | Builder invocation, tool versions, and input digests |
| `manifest-candidate.json` | Unsigned candidate metadata (`status: "testing"`) |
| `provenance.intoto.json` | SLSA build provenance statement |
| `sbom.spdx.json` | SPDX software bill of materials covering declared pipeline inputs and injected packages |
| `validation.json` | Before/after `qcow2` checks, normalization marker results, and pending release gates |
| `checksums.txt` | SHA-256 checksums of all files in the bundle |
| `package-lock.json` | Included when the profile installs locked RPM/DEB packages |
{.wide}

With fixed inputs and tool versions, `validate` mode is byte-for-byte reproducible; for `offline` mode, build the candidate twice and compare the bundles when preparing release evidence. Promoting a candidate to a public `supported` release requires running live VM smoke tests across target host/guest combinations, updating `repo.yaml` with the new catalog `revision` and `supported` status, running `barn repo build` and `barn repo verify`, signing `catalog.json.minisig`, and verifying the published repository endpoints.
