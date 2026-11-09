---
title: "From Upstream Images to a Signed Catalog"
linkTitle: "Image update evidence"
description: "How Barn separates upstream release metadata, catalog evidence, runtime support, and release acceptance."
date: 2026-11-08T10:00:00+08:00
weight: 60
categories: [Design]
tags: [Images, Supply Chain, Releases]
icon: fa-solid fa-shield-halved
lastmod: 2026-11-08
---

An image audit answers a narrower question than an image release. It can find a newer upstream file, but Barn may add that file to its signed catalog only after the artifact, runtime profile, and boot path have all been verified. The [image reference](/docs/reference/images/) describes the user-facing catalog; this essay records the reasoning that keeps catalog updates reproducible.

## Four meanings of “new” {#four-meanings}

Image work becomes error-prone when four independent version values are treated as one:

| Value | What it describes | Evidence needed | Can it update the catalog by itself? |
|---|---|---|---|
| OS release | Vendor release or point version, such as Ubuntu `24.04 LTS` | Release metadata and package/build records | No |
| Cloud build | A dated upstream disk build, with a `YYYYMMDD` identifier | The dated directory, file name, and checksum record | No; it is a candidate source |
| Barn release | Barn’s normalized version and revision suffix | The image recipe and catalog mapping | No; normalization must be reproducible |
| Runtime support | Whether Barn can boot and operate that artifact | QEMU profile, firmware, network, cloud-init, and SSH evidence | Required |
{.wide .expand}

The suffix in a Barn version is not automatically an OS point version. Debian, Ubuntu, Rocky, and CentOS use different build identifiers, and Barn may add its own normalized revision. Keep those namespaces separate in release notes, source recipes, and catalog entries.

## Compare like with like {#compare-like-with-like}

An update comparison must use the same artifact class as the current catalog entry. A generic cloud disk can be compared with another generic cloud disk; an installer ISO, container archive, daily build, or board-specific image answers a different question. A release page’s newest timestamp is not enough to change a Barn source URL.

Use dated upstream URLs for reproducible inputs. Use a `latest` page to discover a candidate, then resolve it to the dated build, the exact artifact, and the checksum record. Record the checksum for the selected format: the digest for a qcow2 upload does not stand in for the digest of a raw disk or a compressed archive.

The audit should also keep OS metadata, cloud-image metadata, and Barn’s local pipeline metadata side by side. If the pipeline recipe is older than the embedded catalog, the safe conclusion is that the recipe needs review; replacing the catalog with the older recipe would move the product backwards.

## Detect drift between recipes and the catalog {#recipe-drift}

On 2026-11-08, the Debian 12 targets in [`official-v1.json`](https://github.com/pgsty/barn/blob/v1.0.0/packaging/image-pipeline/official-v1.json) still selected `20260923.2610.1`, while [embedded catalog revision `2026110502`](https://github.com/pgsty/barn/blob/v1.0.0/internal/image/default-catalog.json) selected `20261026.2643.1`. The source build was `20261026-2643`; the final `.1` belonged to Barn's normalized release. This is a reproducible example of local metadata drift, and a reason to check source recipes before rebuilding a published image.

Keep the upstream input digest separate from the normalized artifact digest. Guest customization changes the disk bytes, so the catalog must hash the final artifact. The existing catalog provenance records independent rebuilds with matching normalization markers but different artifact bytes; it makes no byte-for-byte reproducibility claim. A reproducible recipe and a bit-reproducible output are separate properties.

Architecture discovery needs the same precision. A distribution port or installer ISO is only one part of a future target's evidence. Barn currently accepts `native`, `amd64`, and `arm64`; new image candidates need the runtime work described in [guest architecture contracts](/blog/design/multi-architecture-boundary/).

## A catalog entry is a runtime contract {#runtime-contract}

For Barn, an image entry is valid only when these pieces agree:

| Contract part | What must be true |
|---|---|
| Artifact | The exact path, format, byte size, and digest identify one file |
| Guest architecture | The catalog architecture matches the requested guest architecture |
| QEMU profile | Barn selects the target system emulator, machine, CPU policy, and accelerator |
| Firmware | The image has a validated boot path; UEFI uses matching code and a per-VM variable store, while BIOS images use the BIOS path |
| Guest seed | Cloud-init or the image initialization path creates the expected user, keys, hostname, and network |
| Runtime test | A clean temporary `BARN_HOME` reaches the expected guest architecture and SSH state |
{.wide .expand}

This is why image availability and Barn support are separate statements. The [repository contract](/blog/design/repo-yaml-catalog-json/) keeps human policy in `repo.yaml` and generated file facts in `catalog.json`; the runtime still needs a target emulator and a cold-boot check. A catalog entry that has a good checksum but cannot reach SSH is not a usable Barn image.

## Release gate {#release-gate}

Before a formal Barn release:

1. Fetch the current signed `catalog.json` from the official image repository and verify its signature.
2. Compare its revision, default image, and every stable artifact’s path, architecture, digest, and size with the embedded catalog. Update the embedded manifest version and date, and update `repo.yaml` when the repository source changes.
3. Run `make catalog-check` to verify both official mirrors, require exact agreement with the embedded bytes, and check every stable artifact’s availability and size. Run the image catalog tests and execute `barn update` with a fresh temporary `BARN_HOME`. Use `go run ./tools/catalogcheck -verify-bytes` when all stable artifacts also need to be streamed and hashed.
4. Build and publish only after the catalog gate passes. A release must not carry an artifact that the official repository has removed.
{.steps}

The [catalog checker](https://github.com/pgsty/barn/tree/main/tools/catalogcheck) enforces repository agreement. New or rebuilt images also need startup and SSH acceptance for each changed architecture before promotion; see the [image pipeline](/docs/reference/image-pipeline/). Never reuse a published catalog revision for different bytes.

## Keep the decision with the evidence {#decision-record}

The source repository owns the signed catalog, recipes, code, tests, and dated release evidence. The companion site owns the durable explanation of why the fields and gates exist. When an image decision changes, update the design page and the relevant reference or release record together; keep raw directory scrapes and discarded candidates out of the public source tree.

Read next: [Image repository contract](/blog/design/repo-yaml-catalog-json/) and [Beyond amd64 and arm64](/blog/design/multi-architecture-boundary/).
