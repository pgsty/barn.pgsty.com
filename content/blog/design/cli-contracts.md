---
title: "Evolving the CLI Without Breaking Its Contracts"
linkTitle: "CLI contracts"
description: "What to preserve when separating Barn's command tree, application orchestration, and output handling."
date: 2026-11-04T10:00:00+08:00
lastmod: 2026-11-08
weight: 100
categories: [Design]
tags: [CLI, Compatibility, Architecture]
icon: fa-solid fa-terminal
---

Barn already uses Cobra. The useful part of the [2026-11-04 CLI proposal](https://github.com/pgsty/barn/blob/main/docs/cobra-cli-design.md) is its separation of command syntax, application orchestration, and observable behavior. This essay retains that design, checked against `v1.0.0` and the 2026-11-08 development tree. The package split and broader command reorganization remain proposals; current usage belongs in the [CLI reference](/docs/reference/cli/).

## Keep the existing boundaries {#existing-boundaries}

`cmd/barn/command_*.go` defines the command families. Each execution constructs a fresh Cobra tree, avoiding flag values leaking between calls. Command handlers collect a `commandOutcome`; a shared renderer handles text or structured results, while typed failures retain their exit code, reason, recovery hint, and any partial result. Linux lifecycle, image verification, and native Mac behavior remain in their domain packages.

These boundaries already protect several contracts:

| Contract | What a refactor must preserve |
|---|---|
| Deployment selection | One Linux deployment under `BARN_HOME`; named Mac VMs remain under its `mac/` subtree |
| Configuration source | Desired-state commands resolve inventory; start, stop, status, and access use applied state |
| Machine-readable output | Existing payload fields and types, JSON/YAML parity, and useful partial results on failure |
| Interactive access | Real terminal descriptors, child-process signals, and remote exit status |
| Help and completion | Existing aliases, local flags, platform scope, and offline completion |
{.wide}

Moving a command must not turn an invalid inventory into a fallback to old state, reinterpret `init -o FILE` as an output format, or collapse `up`, `restart`, `reload`, and `recreate` into one operation. Their differences describe which configuration is read and which resources may change.

## Resolve presentation without parsing twice {#presentation}

The current `prepareOutput` adapter scans presentation options before Cobra, using `commandFlagValues` to distinguish flags from values. A future simplification should let the same command tree drive normal parsing, help, completion, and exported command descriptions. It still needs a narrow way to choose error presentation when parsing itself fails.

The invariant is **explicit CLI value → selected environment default → built-in default**. Validate the selected value after resolving precedence. Barn `1.0.0` already fixed valid CLI overrides being rejected by an invalid environment default. Preserve that fix, explicit boolean `false`, and values that resemble flags: `-o --json` may name a file, while anything after the remote `--` boundary belongs to the guest command.

Human help remains text with `--json --help`. Bare `barn` prints full help in text mode and retains `actions[]` in structured mode. A proposed machine-readable help schema would be a separate, explicit interface generated from the command tree.

## Separate results from streams {#output}

Single-result JSON/YAML commands emit one result document on stdout. Progress, warnings, and diagnostics use stderr. Preserve command-specific payloads such as `.nodes` and `.results`; wrapping every response in a new `data` object would break existing automation.

SSH and followed logs need streaming paths. They must retain empty arguments, quoting, a second `--`, cancellation, and the guest's nonzero exit code. Structured interactive SSH sends session output to stderr and the final report to stdout; followed logs emit NDJSON or a YAML document stream. A renderer cannot safely buffer an interactive session into an ordinary result object. Deprecation notices must also stay out of structured stdout.

## Move responsibility before changing behavior {#layering}

The proposed structure has three layers:

| Layer | Responsibility |
|---|---|
| `cmd/barn` | Process entry, signals, and exit status |
| Proposed `internal/cli` | Cobra tree, argument validation, presentation, and stream wiring |
| Application orchestration and existing domain packages | Typed requests and reports, lifecycle work, network setup, images, and Mac VMs |
{.wide}

Inject the streams, environment reader, prompter, and runners actually needed by each operation. Keep domain services independent of Cobra and avoid a generic dispatcher that erases request types. Confirmation and SSH must use the injected input stream throughout; setting a Cobra input stream while reading global `os.Stdin` elsewhere leaves tests and embedded calls inconsistent.

The proposal moves side effects after validation. In the locked Cobra `1.10.2`, pre-run hooks precede required-flag and flag-group validation, so they should perform only normalization and checks. Current lifecycle commands intentionally record a `begin` event before some configuration checks to make early failures traceable; changing that ordering needs an explicit audit-policy decision. A new `--dry-run` option needs a real read-only planner with the same scope as execution; calling a mutator and suppressing its final write is insufficient.

Confirmation, permission, and execution are separate facts. Existing `network` and `hosts` commands can successfully return a plan with `applied=false`; automation checks that field or passes `--yes`. Confirmation never bypasses identity, ownership, or integrity checks. Likewise, `status` can reconcile interrupted runtime records, so a query-like command name alone does not establish a read-only contract.

## Reconcile the proposal with shipped behavior {#implementation-status}

The original proposal contains both durable contracts and dated product choices. At the 2026-11-08 review:

- `1.0.0` already includes full bare-command help, structured `actions[]`, confirmation aliases on applicable destructive commands, and the output-environment precedence fix.
- CLI code still lives in `cmd/barn/`. The proposed `internal/cli` extraction, `--format`, `image update`, and `ssh-config show/install/uninstall` command tree have not landed.
- Current unreleased `main` adds `--image/-I` and `--arch/-A` overrides to applicable inventory operations. It also keeps `purge` immediate by default and offers `--ask` for confirmation. The proposal's mandatory-confirmation purge design is superseded by that choice.

Further behavior changes need their own decision and migration notes. The 1.x compatibility boundary in the [1.0.0 release notes](/blog/release/1.0.0/) applies to any accepted proposal.

## Validate the contract at each step {#acceptance}

First extract responsibilities with command behavior and state formats unchanged. Then add compatible entry points, followed by separately reviewed changes to defaults or selection scope. Compare old and new executables sequentially against controlled fixtures; help, completion, and invalid-input tests should check for unwanted files, subprocesses, or network access as well as output.

Regression coverage must include CLI/environment precedence, stdout/stderr separation, partial failures, remote argument boundaries, real PTY signals, and confirmation scope. Reuse [`cli_test.go`](https://github.com/pgsty/barn/blob/main/cmd/barn/cli_test.go), [`output_test.go`](https://github.com/pgsty/barn/blob/main/cmd/barn/output_test.go), [`remote_command_test.go`](https://github.com/pgsty/barn/blob/main/cmd/barn/remote_command_test.go), and [`signal_test.go`](https://github.com/pgsty/barn/blob/main/cmd/barn/signal_test.go). Moving tests into a new package also requires updating CI package paths and build targets. VM or host-network behavior changes need the corresponding physical-host acceptance.
