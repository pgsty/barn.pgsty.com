---
title: "repo.yaml Is Intent; catalog.json Is Evidence"
linkTitle: "Image repository contract"
description: "Why Barn separates human-authored image policy from generated metadata that must match the actual qcow2 artifacts."
date: 2026-08-29T19:00:00+08:00
weight: 50
categories: [Design]
tags: [Images, Supply Chain, catalog]
icon: fa-solid fa-box-archive
lastmod: 2026-09-29
---

This article explains the Linux image repository in Barn 0.9.0. [Mac machines](/docs/start/macos/) use a separate image workflow.

A static image repository contains qcow2 files and a JSON index, but not all of its metadata should be maintained by hand. Manually copied checksums and sizes can contain errors, while policy buried in generated JSON makes channel changes and deprecations harder to review.

Barn therefore separates maintainer-defined policy from facts calculated from the published files.

## `repo.yaml`: what the maintainer means

The source-controlled `repo.yaml` defines image policy:

- repository revision and defaults;
- image families and aliases;
- movable channels such as `stable`;
- exact versions and architectures;
- boot mode and support status;
- immutable upstream locations and provenance notes.

The file does **not** contain generated artifact size, SHA-256, or virtual size. An entry can map `d13:stable` to an exact version with amd64 and arm64 variants.
Tools calculate the file metadata separately. This policy excerpt shows the format.
See [Image Repositories](/docs/start/images/) for a complete example and the reference for current versions:

```yaml
defaults: { image: d13, channel: stable, arch: native, boot: uefi }
images:
  d13:
    aliases: [debian13, debian, trixie]
    channels: { stable: "20260810.2566.0" }
    versions:
      "20260810.2566.0":
        status: supported
        variants:
          amd64: {}
          arm64: {}
```

A pull request can show channel changes, version deprecations, and changes to provenance statements directly in the policy file.

> [!NOTE]
> Repository syntax and client behavior are
> documented in [Images](/docs/reference/images/); candidate preparation is a
> separate [image-pipeline contract](/docs/reference/image-pipeline/).

## `catalog.json`: what the repository can prove

`catalog.json` records the local repository files that match the policy. Each variant includes its exact filename, byte count, SHA-256, qcow2 virtual size, boot contract, source user, and immutable upstream provenance.

The build derives filename, byte count, digest, and virtual size from the artifact and checks these values.
It copies validated boot mode, source user, status, and provenance from `repo.yaml`. File inspection alone does not prove these policy declarations.
The build parses qcow2 and rejects backing files, external data, encryption, and unknown incompatible features. It completes structural checks before atomically replacing the catalog.

The artifact identity is the tuple `(image, exact version, architecture)`, not
the channel that selected it. Files keep readable immutable names:

```text
images/d13-20260810.2566.0-arm64.qcow2
```

Readable filenames let administrators inspect, mirror, and recover a repository with standard filesystem tools. Generated metadata and verification establish integrity; the filename alone does not.

## Three operations, three responsibilities

The repository CLI keeps observation, generation, and proof separate:

| Command | Responsibility |
| --- | --- |
| `barn repo scan` | report tracked, missing, untracked, or unsafe artifacts without changing anything |
| `barn repo build` | validate source and artifacts, then atomically materialize the catalog |
| `barn repo verify` | rebuild the materialization in memory and require byte-for-byte equality with the published catalog |

`build` never edits `repo.yaml` or qcow2 bytes. By regenerating the catalog and comparing it byte for byte, `verify` detects changes to policy or files that checksum checks alone could miss.

Upload immutable image files first. Publish the catalog and its matching signature last, together where possible.
A client rejects a mismatched pair during a partial upload. Publishing images first prevents the catalog from advertising incomplete downloads.

## Selectors may move; artifacts may not

Human configuration needs convenient selectors. `d13:stable`, `el9@9`, and
`el9@9.7` can resolve to newer exact versions as the repository evolves.
Numeric prefixes compare dot-separated components as integers, so 9.10 sorts
after 9.9.

After resolution, the client stores the exact version, architecture, size, and digest. A channel change does not change an already resolved node.
Selectors can change at selection time, but execution uses the recorded immutable identity.

## Transport and trust are different questions

Official and plain-HTTP catalogs require a trusted detached signature. An operator can explicitly select a local directory or HTTPS repository with an unsigned catalog, trusting local ownership or authenticated transport. An implicit compiled default still requires the signed trust policy, even over HTTPS.

Barn tracks accepted catalog state separately for each repository. It rejects unknown keys, revisions below the highest accepted revision, and different bytes at the same revision.
An explicit downgrade affects only the selected repository. Resetting to the embedded catalog preserves the anti-rollback record.

Every image pull checks byte count, SHA-256, and qcow2 structure, even after catalog acceptance.
Verified base images become read-only, while node root disks use writable overlays. Normal VM writes therefore leave the trusted base unchanged.

## Separate trust domains stay separate

Image catalog keys authenticate image metadata. GitHub Releases distributes application archives and packages with SHA-256 checksums and SPDX SBOMs.
The application workflow does not produce a separate release signature or attestation bundle. A bundled native Mac app has its own Developer ID signing
and notarization process. These mechanisms have different scopes; a catalog
signature does not authenticate the Barn executable.

Barn 0.9.0 defaults to `https://repo.pigsty.io/barn` and exposes
`--mirror` for `https://repo.pigsty.cc/barn`; `--repo` remains the explicit
custom override. The two official repositories may
fall back to each other for image downloads, always verifying the same
catalog size and SHA-256. Custom repositories remain exclusive. Image catalog
updates still use the selected source; embedded upstream URLs remain
provenance and never become an artifact fallback. Source configuration,
generated catalog, uploaded artifacts, signing,
and public availability remain separate release gates.

Maintainers should be able to review policy directly. Tools should generate facts about published files so those facts are reproducible and independently verifiable.
