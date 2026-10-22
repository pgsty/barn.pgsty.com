---
title: "A PID Is Not a Virtual Machine"
linkTitle: "Identity before PID"
description: "Why Barn combines QMP identity, process evidence, typed invocations, and journals before it signals or deletes anything."
date: 2026-08-28T10:00:00+08:00
weight: 40
categories: [Design]
tags: [QMP, Recovery, Safety]
icon: fa-solid fa-fingerprint
lastmod: 2026-09-29
---

This article explains the Linux runtime identity and recovery in Barn 0.9.0. [Mac machines](/docs/start/macos/) are managed independently.

A pidfile records a process ID at the time of writing. It does not prove that the process still runs or that the PID was not reused.
It also does not identify the executable or prove that a QEMU process owns the selected node.

A pidfile alone cannot authorize `SIGKILL` or root-disk deletion.

Barn checks identity through independent evidence. Destructive operations proceed only when all required evidence agrees.

## QMP is the primary runtime identity

Every VM receives a generated UUID and an expected QEMU name. After launch,
Barn connects to the QEMU Machine Protocol socket and asks QEMU for both.
Barn reports a successful start only after QMP returns the expected name and UUID. A completed launch command or existing socket path is insufficient.

Barn repeats this identity check before shutdown. If the QMP endpoint returns a different name or UUID, Barn sends no command through that endpoint.

Barn first requests guest powerdown through QMP. If the bounded shutdown wait expires, Barn asks QEMU to quit. It uses process signals only as a fallback.

> [!NOTE]
> This record explains the fail-closed lifecycle
> boundary. Operational recovery starts with
> [Troubleshooting](/docs/start/troubleshooting/), not manual deletion.

## Process identity closes the fallback gap

QMP may be unavailable after a crash, a damaged runtime directory, or a
half-completed shutdown. For that case Barn records a process tuple:

- PID;
- executable path;
- process start time;
- SHA-256 of the observed command line.

The complete typed QEMU invocation is stored beside it. Before sending
`SIGTERM`, Barn re-reads the live process and requires the tuple to match.
Before escalating to `SIGKILL`, Barn captures the tuple again. This second check detects PID reuse during the bounded TERM wait.

If QMP still responds but an operation fails, Barn does not use a signal to bypass QMP.
Barn stops if QMP reports another identity or if the process tuple cannot be verified. Missing evidence does not relax the check.

If QMP is unavailable, Barn checks the recorded PID. When it belongs to an unrelated process, Barn treats the VM as stopped and leaves that process untouched. An unreadable or ambiguous identity blocks the operation.

## Journals describe work before state exists

Barn prepares disks and seed media before it starts the VM. It can record the VM's identity only after the process starts. A crash between these steps can leave files without a verified owner.

Barn writes a mode-0600 prepare journal first. It contains:

- operation and VM UUIDs;
- node name and resolved-spec hash;
- each completed artifact from a fixed kind/path allowlist;
- the typed QEMU invocation once preparation is complete;
- the exact node-state path once commit succeeds.

The journal uses strict versioned JSON. Barn rejects unknown fields, invalid UUIDs, unsafe paths, repeated artifacts, incorrect modes, symlinks, and paths outside the node directory.

Recovery uses the journal to identify artifacts created by the uncommitted operation. It does not infer ownership from a directory scan.

## Rollback is narrower than cleanup

Offline rollback requires all of these conditions:

- No committed node state exists.
- The QMP socket and pidfile from the recorded invocation are absent.
- The node directory contains only the journal and completed artifacts from the allowlist.

Rollback removes the completed artifacts in reverse order, followed by the
journal and empty node directory.

A failed first `up` can be retried after
the inventory is edited. Safe cleanup follows the journal's completed artifact
list rather than requiring the new desired spec to match the failed old spec.

A stale prepare journal cannot roll back a committed node. Barn does not add pre-existing disks to the removal list. An unexpected file blocks directory removal.

Normal destroy checks path containment, file type, ownership, process termination, and the exact artifact set. Persistent disks follow separate preservation and purge rules.
Barn removes directories only after all known files are gone; an unknown entry blocks removal with an error.

## Atomic state makes the evidence durable

State updates use a same-directory temporary file, `fsync`, atomic rename, and parent-directory `fsync`. Barn rejects symlink targets. Deployment and node locks serialize changes.
After a crash, the state should contain either the old committed record or the new committed record. A journal describes the bounded interval between those commits.

When resource identity is ambiguous, Barn preserves the evidence and asks the operator to inspect it. This behavior reduces the risk of unintended deletion in a local database lab.

Read next: [`repo.yaml` is intent; `catalog.json` is evidence](/blog/design/repo-yaml-catalog-json/).
