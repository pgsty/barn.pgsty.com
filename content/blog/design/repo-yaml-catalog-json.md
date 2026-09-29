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

This article describes Barn 0.9.0. The VM lifecycle and network design here
apply to Linux guests; [Mac machines](/docs/start/macos/) are managed independently.

A static image repository sounds like a directory of qcow2 files plus a JSON
index. The difficult part is deciding which facts a maintainer may write by
hand and which facts must be derived from the bytes being published.

If checksums and sizes live in the hand-authored source, they are easy to copy
incorrectly. If policy exists only in generated JSON, reviewing a channel
change or deprecation requires reading machine output. Barn keeps the two
jobs separate.

## `repo.yaml`: what the maintainer means

The source-controlled `repo.yaml` contains author intent:

- repository revision and defaults;
- image families and aliases;
- movable channels such as `stable`;
- exact versions and architectures;
- boot mode and support status;
- immutable upstream locations and provenance notes.

It deliberately does **not** contain generated artifact size, SHA-256, or
virtual size. A compact entry can say that `d13:stable` points to one exact
version with amd64 and arm64 variants without pretending to know facts that
belong to the files. This policy excerpt illustrates the format;
see [Image Repositories](/docs/start/images/) for a complete working example
and the reference for current versions:

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

This is the right layer for review: a pull request can show that a channel
moved, a version was deprecated, or a provenance statement changed.

> [!NOTE]
> Repository syntax and client behavior are
> documented in [Images](/docs/reference/images/); candidate preparation is a
> separate [image-pipeline contract](/docs/reference/image-pipeline/).

## `catalog.json`: what the repository can prove

`catalog.json` materializes policy against the local repository. For every
variant it records the exact filename, byte count, SHA-256, qcow2 virtual size,
boot contract, source user, and immutable upstream provenance.

Filename, byte count, digest, and virtual size are materialized and checked
against the artifact. Boot mode, source user, status, and provenance are
validated policy copied from `repo.yaml`; inspection does not independently
prove those declarations. Build forces qcow2 parsing, rejects backing files,
external data,
encryption, and unknown incompatible features, and runs structural checks
before atomically replacing the catalog.

The artifact identity is the tuple `(image, exact version, architecture)`, not
the channel that selected it. Files keep readable immutable names:

```text
images/d13-20260810.2566.0-arm64.qcow2
```

Readable names are an operational feature: an administrator can inspect,
mirror, or recover a repository with ordinary filesystem tools. Integrity
still comes from generated metadata and verification, not from trusting the
name.

## Three operations, three responsibilities

The repository CLI keeps observation, generation, and proof separate:

| Command | Responsibility |
| --- | --- |
| `barn repo scan` | report tracked, missing, untracked, or unsafe artifacts without changing anything |
| `barn repo build` | validate source and artifacts, then atomically materialize the catalog |
| `barn repo verify` | rebuild the materialization in memory and require byte-for-byte equality with the published catalog |

`build` never edits `repo.yaml` or qcow2 bytes. `verify` is stronger than
“every checksum is valid”: it also proves that no source policy or artifact
change was omitted from the generated catalog.

Publication follows the same direction. Upload immutable image bytes first;
publish the catalog and its matching signature last. Publish that pair
together where possible. A client refuses a mismatched pair during a partial
upload; the order avoids advertising image bytes that are still in transit.

## Selectors may move; artifacts may not

Human configuration needs convenient selectors. `d13:stable`, `el9@9`, and
`el9@9.7` can resolve to newer exact versions as the repository evolves.
Numeric prefixes compare dot-separated components as integers, so 9.10 sorts
after 9.9.

After resolution, the client persists the exact version, architecture, size,
and digest. An already resolved node does not become a different machine
because a channel moves. Convenience exists at selection time; immutable
identity exists at execution time.

## Transport and trust are different questions

Official and plain-HTTP Catalogs require a trusted detached signature. An
operator who explicitly selects a local directory or HTTPS repository may use
an unsigned catalog because local ownership or authenticated transport is the
explicit trust decision. An implicit compiled default remains in the signed
trust domain even if its URL is HTTPS.

Accepted catalog state is tracked independently per repository. Barn rejects
unknown keys, a revision below that repository's high-water mark, and different
bytes at the same revision. An explicit downgrade is visible and scoped to the
selected repository; resetting to the embedded catalog does not erase the
anti-rollback record.

catalog acceptance is only the first half. Every pull still checks byte count,
SHA-256, and qcow2 structure. Verified base images become read-only, and node
root disks are overlays, so normal VM writes never mutate the trusted base.

## Separate trust domains stay separate

Image catalog keys authenticate image metadata. Application archives and packages
are distributed through GitHub Releases with SHA-256 checksums and SPDX SBOMs;
the application workflow does not produce a separate release signature or
attestation bundle. A bundled native Mac app has its own Developer ID signing
and notarization process. These mechanisms have different scopes; a catalog
signature does not authenticate the Barn executable.

The Barn 0.9.0 defaults to `https://repo.pigsty.io/barn` and exposes
`--mirror` for `https://repo.pigsty.cc/barn`; `--repo` remains the explicit
custom override. The two official repositories may
fall back to each other for image downloads, always verifying the same
catalog size and SHA-256. Custom repositories remain exclusive. catalog
updates still use the selected source; embedded upstream URLs remain
provenance and never become an artifact fallback. Source configuration,
generated catalog, uploaded artifacts, signing,
and public availability remain separate release gates.

That is the larger design principle: policy should be pleasant to review, but
facts about shipped bytes should be generated, reproducible, and independently
verifiable.
