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

> [!NOTE]
> **Renamed 2026-09-29:** names now follow the unreleased Barn 0.9.0 candidate.
> The prior source review was on 2026-09-26: the original publication date is retained; the text
> below reflects the implementation reviewed on this date. See
> [Status](/docs/about/status/) for released versus candidate behavior and
> dated acceptance evidence.

A pidfile answers one question: which integer did a process have when the file
was written? It does not prove that the process is still alive, that the PID
was not reused, that the executable is QEMU, or that this particular QEMU owns
the node an operator wants to stop.

That is not enough authority for `SIGKILL`, and certainly not enough authority
to remove a root disk.

Barn treats identity as a chain of independent evidence. Each link has a
different job, and destructive action proceeds only when the required links
agree.

## QMP is the primary runtime identity

Every VM receives a generated UUID and an expected QEMU name. After launch,
Barn connects to the QEMU Machine Protocol socket and asks QEMU for both.
The VM is not considered started merely because the process returned or a
socket path appeared; QMP must report the expected name and UUID.

The same check guards shutdown. A QMP endpoint with a different name or UUID
is not “probably the old VM.” It is a hard identity mismatch, and Barn sends
no command through it.

QMP also provides the clean path: request Guest powerdown, wait for the Guest,
then ask QEMU to quit if the bounded graceful wait expires. Process signals
are fallback tools, not the primary lifecycle API.

> [!NOTE]
> **Decision status: current.** This record explains the fail-closed lifecycle
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
Before escalating to `SIGKILL`, it captures the tuple again, specifically to
close the PID-reuse window created by the bounded TERM wait.

If QMP still answers but a QMP operation fails, Barn does not bypass that
live control plane with a signal. If QMP reports another identity, it stops. If
the process tuple cannot be verified, it stops. “Unable to prove” is a result,
not a reason to weaken the check.

**Unreleased 0.9 candidate update:** when QMP is unavailable and the recorded
PID is positively identified as an unrelated process, Barn treats the old VM
as stopped and never signals that unrelated process. This differs from an
unreadable or ambiguous identity, which still blocks the operation.

## Journals describe work before state exists

Committed node state cannot describe the earliest part of creation: disks and
seed media must exist before the VM can start, and the process must start
before its identity can be committed. A crash in that interval would otherwise
leave artifacts with no trustworthy owner.

Barn writes a mode-0600 prepare journal first. It contains:

- operation and VM UUIDs;
- node name and resolved-spec hash;
- each completed artifact from a fixed kind/path allowlist;
- the typed QEMU invocation once preparation is complete;
- the exact node-state path once commit succeeds.

The journal is strict versioned JSON. Unknown fields, invalid UUIDs, unsafe
paths, repeated artifacts, wrong modes, symlinks, or a path outside the node
directory invalidate it.

Recovery can therefore answer a bounded question: *which artifacts did this
uncommitted operation create?* It is not a request to scan the directory and
guess.

## Rollback is narrower than cleanup

An offline rollback is allowed only when no committed node state exists and no
QMP socket or pidfile from the typed invocation remains. The node directory may
contain only the journal and the completed allowlisted artifacts. Rollback
then removes the completed artifacts in reverse order, followed by the journal
and empty node directory.

**Unreleased 0.9 candidate update:** a failed first `up` can be retried after
the Inventory is edited. Safe cleanup follows the journal's completed artifact
list rather than requiring the new desired spec to match the failed old spec.

A committed node is never rolled back by a stale prepare journal. A pre-existing
disk is never added to the action list. An unexpected file blocks directory
removal instead of being swept up as collateral damage.

Normal destroy follows the same philosophy. It proves containment, file type,
ownership boundary, process death, and an exact artifact set. Persistent disks
live behind their own preservation and purge rules. Directories are removed
only after the known files are gone, so an unknown entry turns into an error.

## Atomic state makes the evidence durable

State updates use a same-directory temporary file, `fsync`, atomic rename, and
parent-directory `fsync`; symlink targets are rejected. Deployment and node
locks serialize mutations. The goal is not to make crashes impossible—it is
to ensure a crash leaves either an old committed fact or a new committed fact,
plus a journal for the bounded interval between them.

This design is intentionally conservative. It may ask an operator to inspect
an ambiguous resource that a more aggressive tool would delete. For a local
database lab, preserving the evidence is the safer failure mode.

Read next: [`repo.yaml` is intent; `catalog.json` is evidence](/blog/design/repo-yaml-catalog-json/).
