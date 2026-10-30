---
title: "A PID Is Not a Virtual Machine"
linkTitle: "Identity before PID"
description: "Why Barn combines QMP identity, process evidence, typed invocations, and journals before it signals or deletes anything."
date: 2026-08-28T10:00:00+08:00
weight: 40
categories: [Design]
tags: [QMP, Recovery, Safety]
icon: fa-solid fa-fingerprint
lastmod: 2026-10-26
---

This essay explains Linux runtime process identity and crash recovery in Barn `0.9.2` ([macOS guests](/docs/start/macos/) use per-slot locks and runner protocol `2`).

A `pidfile` records a process ID at the moment it was written. Minutes or days later—especially after a crash or host reboot—that integer alone cannot tell you whether the original QEMU process is still running, whether the OS kernel recycled the PID for an unrelated user process, or which VM node that process belongs to.

Trusting a bare `pidfile` is how naive process managers end up sending `SIGKILL` to an unrelated process or deleting a disk that is still attached to a live VM. Barn never authorizes `SIGTERM`, `SIGKILL`, or disk deletion from a PID alone; destructive actions proceed only when independent identity checks agree.

## QMP is the primary runtime identity

Every Barn Linux VM is assigned a generated UUID and an expected QEMU instance name (`barn-<node>`). Immediately after spawning QEMU, Barn connects to the node's QEMU Machine Protocol (QMP) Unix socket and queries both values. A node launch succeeds only after QMP responds with the exact expected name and UUID.

Barn repeats that QMP handshake before every shutdown or status transition:

1. Barn queries QMP for the live instance name and UUID; if QMP returns a different identity, Barn aborts without sending any command to that socket.
2. To stop a verified VM, Barn first sends a clean guest ACPI `system_powerdown` over QMP, then sends QMP `quit` if the shutdown timeout expires, and falls back to OS signals only when QMP itself is unreachable.
{.steps}

> [!NOTE]
> When a command reports an interrupted transition or identity mismatch, start with [Troubleshooting](/docs/start/troubleshooting/) rather than deleting files in `~/.barn` by hand.

## Process four-tuples close the fallback gap

If QEMU crashes, the runtime socket directory is cleared, or a shutdown is interrupted mid-flight, the QMP socket may no longer respond. To handle signal fallback safely without QMP, Barn records a four-element process identity tuple alongside the full typed QEMU invocation when the VM starts:

- Process ID (`PID`)
- Resolved executable path
- OS process start timestamp
- SHA-256 digest of the observed command-line arguments (`argv`)

Before sending `SIGTERM`, Barn inspects the live OS process table and requires all four fields to match the recorded tuple. If the process does not exit within the `SIGTERM` grace window, Barn re-reads the process tuple a second time immediately before sending `SIGKILL`—closing the race window where the original process exits and the kernel reuses its PID during the wait.

If QMP is unreachable and the OS process table shows that the recorded PID now belongs to an unrelated process (or no longer exists), Barn marks the VM `stopped` without signaling that PID. Conversely, if QMP is still responsive or if the live process tuple cannot be read unambiguously, Barn refuses to send blind signals and stops with a diagnostic error.

## Prepare journals track work before state is committed

Creating a VM requires preparing disk overlays and `cloud-init` seed media on disk before the QEMU process even starts. If the CLI is killed (`SIGINT`/`SIGKILL`) or crashes mid-preparation, those files exist on disk before a committed node state record is written.

To recover cleanly without guessing from directory listings, Barn writes a `0600` versioned JSON **prepare journal** before creating any node file:

- Operation UUID and target VM UUID
- Node name and resolved specification hash
- An ordered log of each created artifact from a strict `(kind, path)` allowlist
- The typed QEMU invocation once disk preparation finishes
- The committed node-state file path once the transaction completes

During recovery, Barn validates the journal schema, UUIDs, file modes, symlink absence, and directory containment, then rolls back only the exact uncommitted files recorded in the journal.

## Narrow rollback and fail-closed teardown

Offline rollback of an uncommitted node runs only when three preconditions hold simultaneously:

1. No committed node state file exists for that node.
2. Neither the QMP socket nor the `pidfile` from the journal's QEMU invocation is present.
3. Every file in the node directory belongs to the journal and its allowlisted artifact set.

When all three hold, Barn removes the uncommitted artifacts in reverse creation order, deletes the journal, and removes the empty node directory. This lets you edit `barn.yml` after a failed first `barn up` and re-run `barn up` cleanly, while guaranteeing that a stale journal can never roll back an already committed node or delete pre-existing persistent disks.

Ordinary `barn destroy` applies the same discipline: it verifies path containment, file ownership, process termination, and the exact known artifact list before unlinking files, and removes the node directory only when it is empty (any unexpected file halts directory removal with an error).

## Atomic state updates

Every state update writes to a sibling temporary file in the same directory, calls `fsync`, performs an atomic `rename`, and `fsync`s the parent directory while holding the deployment and node locks. After any crash, on-disk state reflects either the prior committed state or the new committed state, with the prepare journal covering the bounded window in between.

Read next: [`repo.yaml` Is Intent; `catalog.json` Is Evidence](/blog/design/repo-yaml-catalog-json/).
