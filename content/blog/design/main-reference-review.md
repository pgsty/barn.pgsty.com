---
title: "Main and command reference review"
description: Git state, version boundaries, command coverage, and validation evidence from the 2026-11-11 Barn review.
date: 2026-11-11
weight: 5
categories: [Design]
tags: [CLI, Documentation, Validation]
---

**Reviewed on 2026-11-11.** Both repositories were on `main`, but neither had a clean working tree or matched its fetched remote head. The source checks passed on the reviewed working tree. The documentation now has a [complete command reference](/docs/reference/commands/) with explicit stable, local-main, and uncommitted-feature labels.

## Git and release state {#git-state}

| Repository | Local main | Fetched origin/main | State at review entry |
|---|---|---|---|
| `pgsty/barn` | `6ab0cd5` | `b2cc8da` (`v1.1.0`) | Ahead 3; 11 tracked paths changed, plus `.idea/`, `barn.yml`, and `cmd/barn/hosts_inventory_test.go` untracked |
| `pgsty/barn.pgsty.com` | `bc7968a` | `d392cd5` | Ahead 3; four reference files modified and six design-article files untracked |
{.wide .expand}

GitHub's latest regular release was [v1.1.0](https://github.com/pgsty/barn/releases/tag/v1.1.0), published on 2026-11-09. No v1.2.0 tag was present on the remote. The local 1.2.0 notes were marked as a draft.

The three source commits add configurable Linux lifecycle concurrency (`158786a`), unified specification inputs and recoverable root growth (`1e24768`), and the 1.2.0 toolchain/release preparation (`6ab0cd5`). The `vm_hosts` parser and `hosts install -f` CLI extension remained uncommitted. A build of that working tree therefore exposes an interface that a checkout of the remote main or even the local HEAD commit does not contain.

Existing edits and deletions were retained. This review changed documentation without creating commits, pushing branches, or deploying the site. Before bringing main to a clean, shared state, review and commit the intended hosts implementation together with its tests, decide the intended disposition of the pre-existing untracked files and two deleted historical root documents, and reconcile the three local commits with the remote. Source and site changes need separate commits and publication decisions.

## Findings and corrections {#findings}

| Finding | Correction |
|---|---|
| The reference summarized commands but lacked complete per-command usage | Added 57 operation entries across seven command families, each with syntax, all local options, examples, and operation scope; root/help and groups are covered by the index |
| Stable 1.1.0, local main, and uncommitted hosts features were easy to confuse | Added a dated version baseline and option-level availability; clarified configuration, project status, source builds, and Linux operations |
| README described 2 vCPUs/4 GiB as the default without distinguishing development | Kept that released default and documented local main's 1 vCPU/2 GiB default |
| Development articles linked new files under remote main before those files were pushed | Replaced those unavailable links with the reviewed local commit and repository-relative source/test paths |
| Contributor instructions said Ubuntu images retained the upstream bytes | Corrected them against catalog provenance: Ubuntu 22.04/24.04/26.04 are offline-normalized with `dba`, UID/GID 88, locales, and verified upstream XFS tools; they use the direct pipeline outside the eight-image wrapper matrix |
| A Mac command summary implied all configuration changes required stopping | Clarified that clipboard configuration can be saved while running and takes effect at the next start |
{.wide .expand}

The existing image reference's nine families, 17 artifacts, exact stable versions, and aliases agree with `internal/image/default-catalog.json`. Catalog `source_user` and provenance, rather than stale prose, were used to distinguish normalized images from unmodified distribution images. The command reference also retains the custom HTTPS/local unsigned-catalog policy, scoped aliases, explicit remote `--` separators, and the different confirmation rules for `purge`, `destroy`, and Mac commands.

## Implementation review {#implementation-review}

The reviewed changes include specification precedence and type validation (`cmd/barn/vm_inputs.go`, `internal/config/inventory.go`, `internal/config/resources.go`), concurrency limits (`internal/private/concurrency.go`), and root-growth recovery (`internal/private/root_resize.go`, its guest helper, and `internal/state/root_resize.go`). Root growth verifies the managed root path/serial and proven QEMU process death before image mutation, persists recovery stages, checks guest partition/filesystem identity and capacity, and retains the original power-state intent for retry.

For the uncommitted hosts extension, the review checked inventory-only mappings, case-insensitive conflict detection, subnet constraints, preview without deployment state, and preservation of an explicit inventory in follow-up commands. Relevant regressions are in `cmd/barn/hosts_inventory_test.go`, `internal/config/inventory_test.go`, and `internal/hostconfig/hostconfig_test.go`. These files must travel with the corresponding implementation when it is committed.

## Validation evidence {#validation}

- **Source:** `make check` passed on the current source working tree: module/shell/maintenance checks, unit and race tests, vet, Staticcheck, dead-code intersection, errcheck, vulnerability scanning, four-target cross-builds, image-pipeline boundaries, installer tests, Mac payload tests, and licenses. The scanner reported no reachable vulnerabilities, plus one vulnerability at the unused module-package level. The native offline image-mutation test was explicitly skipped by the normal boundary suite.
- **Image repositories:** `make catalog-check` activated both official signed catalogs in fresh temporary roots, matched embedded revision `2026110502` byte-for-byte, and checked availability/size for all 17 stable artifacts on each mirror. The catalog SHA-256 was `d41e46d20bc57cb1b071e3919a27a8f7f703df2addca879970a528e7ab004065`. Artifact payloads were not streamed for full digest recomputation (`verified_bytes: false`).
- **CLI coverage:** Separately built v1.1.0 and working-tree CLIs supplied the real help output. Each language covers all 57 operation commands and 174 visible local-option rows; stable-only rows were compared with the release binary's help. Paired heading IDs, syntax blocks, and command examples match.
- **Examples:** All four generated templates passed `init`, `validate`, and `plan` with both builds in isolated temporary `BARN_HOME` directories. Defaults were checked numerically, as were development scaling and root-size inputs. Five complete inventory examples from the guide/reference pages passed validation with the applicable versions.

- **Site:** Production `make check` passed, including internal links, fragments, and assets; the only warning was the expected upstream LibSass deprecation. The built-in browser control timed out, so visual page inspection was not completed.

No live VM lifecycle, host-network mutation, or privileged hosts installation was executed for this documentation review. Native hypervisor acceptance and a signed release-package run remain separate checks when delivering runtime changes or a formal release.
