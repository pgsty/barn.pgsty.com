---
title: Repository Commands
description: Scan, build, and verify static image repositories from repo.yaml and qcow2 artifacts.
weight: 50
date: 2026-11-11
---

Scan, build, and verify static image repositories from repo.yaml and qcow2 artifacts.

This reference covers **Barn 1.2.0**. Option tables distinguish options also available in **1.1.0** from additions in **1.2.0**; see the [version baseline](/docs/reference/commands/#versions). All commands inherit the [global options](/docs/reference/commands/#global-options).

## `barn repo scan` {#barn-repo-scan}

```text
barn repo scan <root> [flags]
```

Scan one repository root containing `repo.yaml` and a flat `images/` directory. Report tracked, missing, untracked, and unsafe qcow2 files without changing them or requiring `qemu-img`. Successful scanning exits `0` even with findings; automation must inspect `missing` and `unsafe` rather than rely on the exit code alone.

No local options beyond `--help`; global presentation options still apply.

```bash
barn repo scan /srv/barn
barn --json repo scan /srv/barn
```

## `barn repo build` {#barn-repo-build}

```text
barn repo build <root> [flags]
```

Validate `repo.yaml`, inspect the declared qcow2 artifacts with `qemu-img`, calculate final digests/sizes, and atomically generate `catalog.json`. Missing or unsafe artifacts fail the build; untracked files are omitted. `repo.yaml` and image bytes are preserved.

This command does not sign or publish a catalog. Increment the revision for changed contents, keep artifact filenames immutable, and use the separate contributor signing tools before publication. See [repository format](../../images/#static-repository-format).

No local options beyond `--help`; global presentation options still apply.

```bash
barn repo build /srv/barn
barn --json repo build /srv/barn
```

## `barn repo verify` {#barn-repo-verify}

```text
barn repo verify <root> [flags]
```

Rebuild the expected catalog in memory and require byte-for-byte agreement with the existing `catalog.json`, using `repo.yaml` and actual image bytes. Requires `qemu-img`. It checks repository consistency; detached-signature verification belongs to catalog activation and the signing tools.

No local options beyond `--help`; global presentation options still apply.

```bash
barn repo verify /srv/barn
barn --json repo verify /srv/barn
```

## Implementation {#implementation}

[command_repo.go](https://github.com/pgsty/barn/blob/v1.2.0/cmd/barn/command_repo.go)

The [version baseline](/docs/reference/commands/#versions) identifies the released source and the changes since 1.1.0.
