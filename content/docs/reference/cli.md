---
title: CLI
description: Farrow commands, important flags, structured output, and exit codes.
weight: 20
icon: fa-solid fa-terminal
aliases: [/docs/reference/json-api/]
---

```text
farrow [--json|--yaml] [-v|--verbose] <command> [flags] [node...]
```

The installed binary is the authoritative reference for its own version. Every
visible command includes its operational boundary and copyable examples:

```bash
farrow --help
farrow setup --help
farrow image pull --help
```

Bare `farrow` prints a short welcome with next commands and exits 2; a bare namespace such as
`farrow image` prints help and also exits 2. In JSON/YAML mode a bare namespace is a
structured usage error; explicit `--help` always renders human help.

## Commands

| Area | Commands |
|---|---|
| Prepare | `setup`, `init`, `validate`, `doctor` |
| Lifecycle | `plan`, `up`, `start`, `stop`, `restart`, `reload`, `recreate`, `status`, `destroy`, `purge` |
| Access | `ssh`, `exec`, `logs`, `provision`, `ssh-config`, `hosts install/uninstall` |
| Images | `update`, `image list/info/pull/import/sync/prune/reset`, `repo scan/build/verify` |
| Host network | `network status/install/uninstall` |
| Misc | `version`, `completion` |

No command refreshes the Catalog implicitly. `update` fetches the configured
repository's Catalog, verifies it, and activates it; `image sync` is the
explicit recovery path for an exact URL or file. Ordinary commands use the
active local Catalog. Neither operation updates the Farrow executable.

Frequently used commands have scoped aliases:

| Command | Aliases | Command | Aliases |
|---|---|---|---|
| `setup` | `s` | `validate` | `v` |
| `plan` | `pl` | `recreate` | `rc` |
| `status` | `st` | `destroy` | `de` |
| `ssh-config` | `sc` | `image` | `images`, `im` |
| `doctor` | `dt` | `network` | `n`, `net` |
| `exec` / `logs` | `ex` / `l` | `version` | `ver` |

`up`, `ssh`, `init`, `start`, `stop`, `restart`, `reload`, `provision`,
`hosts`, `purge`, and `completion` have no aliases; two letters must not
discard a lab. Inside a namespace, `hosts` and
`network` use `i`/`u` for install/uninstall; `network status` uses `st`; and
`image` maps `list=ls`, `info=in`, `pull=p`, `prune=pr`, `sync=sy`,
and `import=i`. `image reset` keeps `reset-manifest` as a compatibility alias.

Commands using applied state work from any directory. Configuration selection
is command-scoped; `-f` is deliberately not a global flag:

| Commands | Desired-state source |
|---|---|
| `setup [template]` | explicit `-f`, otherwise discovery, otherwise generate `meta`; template and `-f` are exclusive |
| `init [template]` | generate a new inventory; read no desired state; `--force` explicitly replaces the output |
| `validate` | explicit `-f`, then discovery; never applied state |
| `plan`, `up`, `reload`, `recreate` | explicit `-f`, then discovery, then the applied resolved specification |
| other lifecycle/access commands | no desired-state inventory; they use applied state |

When neither an inventory nor an applied deployment exists, interactive `up`
can generate the default inventory. It can also prepare missing host dependencies
and restore an intact inactive Farrow network. This implicit preparation accepts
the setup plan; sudo may still request credentials. Use `setup --dry-run` to
review the host plan first. Scripts should run `setup --yes` explicitly; `init`
is optional when no inventory exists.

## Important flags

| Flag | Meaning |
|---|---|
| `--json`, `--yaml` | machine-readable stdout; progress remains on stderr; intentionally no shorthand |
| `-v`, `--verbose` | bounded diagnostics on stderr |
| `-c`, `--cidr` | select the RFC1918 `/24` for generated `init`/`setup` templates or host-network inspection/install |
| `-f`, `--file` | select an Inventory for commands that read desired state |
| `-r`, `--repo` | choose an image/artifact repository; overrides `--mirror` and `FARROW_REPO` |
| `--mirror` | use the China official repository for setup, Catalog, and image-resolving lifecycle commands |
| `-m`, `--mode` | select `host` or `shared` where the command exposes the macOS network mode |
| `-d`, `--dry-run` | show a setup/image plan without changing state |
| `-y`, `--yes` | apply a displayed host/setup/image plan |
| `--force` (`init`, `destroy`, `recreate`) | overwrite generated output or skip the typed confirmation; long-only because `-f` selects the Inventory |
| `-n`, `--no-wait` | return once QEMU is running, without readiness or guest recovery checks |
| `--rollback` (`up`, `reload`) | remove the prepare artifacts of nodes that failed to prepare in this run |
| `--delete-persistent` | during whole destroy, also delete retained data disks; invalid with node selectors |
| `--purge` | whole-deployment disposal: delete disks, keys, and deployment state; keep images |

Rare, selection, or safety-widening controls such as `--mirror`, `--force`,
`--rollback`, `--remove`, `--allow-downgrade`, `--sudo`,
`--delete-persistent`, and `--purge` are
long-only. On commands that read an Inventory, `-f` always selects a file;
`logs -f` retains the conventional `--follow`. `-n` always means `--no-wait`,
and `-d` always means a dry run.

`farrow purge` is the no-confirmation shortcut for
`farrow destroy --force --purge`. It accepts no nodes or Inventory, removes the
complete deployment plus persistent disks, keys, state, and the default SSH
fragment, and keeps images and the host network. With no deployment it succeeds
without changing the image cache. Missing state never authorizes deletion of
residual node artifacts whose identity cannot be proven.

A failure prints `error: <message>` on stderr, the failing program's last
stderr lines when an external tool failed, and a `next:` line when there is one
clear action. If a failing command has not already emitted a richer typed
result, structured mode writes one object before returning the exit code:
`error` (the class below), `message`, and where they apply a stable `reason`,
`next`, and `command` (`name`, `argv`, `exit_status`, `signal`, `timed_out`,
`stderr`) for a failed external program. Existing typed failure results are
never followed by a second JSON/YAML document.

`plan` is read-only and returns success even when its action is `recreate` or
`blocked-removal`; automation must inspect the action and `create`, `recreate`,
`start`, `missing`, and `blocked` fields. Plans only read local configuration
and catalog data, so QEMU and host networking need not be installed. They show
exact images, total resources, change reasons, and disk effects. `up` checks
host capabilities and address availability before applying changes. `up` creates missing nodes, starts stopped ones,
re-checks readiness of running ones, and rewrites the SSH client configuration
Farrow installed from the complete applied deployment. `recreate` performs the
same full refresh; node destroy removes stale entries, and whole destroy
removes that configuration. `start` powers on stopped nodes and re-checks
readiness of running ones; `start` and `restart` also refresh SSH aliases.
Destructive drift returns a conflict that names the next commands:
`farrow plan`, then `farrow recreate <node>` or `farrow destroy <node>`. On a
terminal those commands ask you to type the confirmation word; `--force` is for
scripts. If VM lifecycle succeeds but the SSH client configuration cannot be
written, the command reports a warning and remains successful; `farrow ssh`
still works. Structured output carries integration warnings in `warnings[]`.

Guest management SSH is the readiness boundary. Optional setup failures are
reported in `nodes[].warnings`; completed recovery actions, including data resets,
are in `nodes[].repairs`. A usable guest with these limitations exits 0. Repeat
`up` to retry unfinished stages without restarting running VMs. Inspect the
warning fields when automation requires every configured feature.

A multi-node operation in which some nodes failed exits 5 and reports
`N of M node(s) failed: <node> (<stage>: <error>); ...`. Stages are `prepare`,
`start`, `readiness`, `guest-setup`, `stop`, and `status`; a `readiness` failure adds
`run \`farrow logs <node>\` for the guest console`. Structured output carries
`failures[]` with `node`, `stage`, and `error`, plus `rolled_back` when
`--rollback` removed the prepare artifacts of nodes that never committed. See
[A node did not become ready](../../start/troubleshooting/#a-node-did-not-become-ready).

`status` shows node, state, IP, exact image, and CPU/memory. Use `--verbose` for
SSH ports, architecture, accelerator, and PID. TCG is marked in ordinary text
as well. One degraded node does not hide its peers; status exits 5 and retains
per-node errors and `failures[]`. Running means the VM process is running;
status does not claim to have checked guest readiness.

Starting commands also refresh Farrow hosts and control-node SSH entries in
running guests. Stopped guests catch up when started. `--no-wait` skips guest
readiness, guest recovery, and that refresh; a later `up` completes them. Selected recreate
refuses remaining peer drift before stopping or deleting disks; select the
required nodes together as directed.

The control guest's Farrow-managed SSH entries accept replacement host keys
without recording them in known_hosts, so recreated lab nodes remain reachable.
User-added SSH entries are preserved.

## Recovery in 0.8

`up` and `start` isolate missing host-share failures by node; `up` also
continues existing stopped peers when a new node fails to prepare. Partial
results keep exit code 5 and preserve successful nodes. Retry hints retain the
inventory, repository and applicable flags; a `start` retry remains `start`.

Setup and its lifecycle retry share one `operation_id`. Even before deployment
state exists, `farrow logs --source events --json` can read the bounded phase
trace after failed setup. Setup traces omit command arguments and authentication
data; retain the command output for its detailed cause. `setup --dry-run` writes
no trace. Successful `destroy --delete-persistent` and `purge` summaries describe
the final deletion/retention result; purge leaves the image cache and host network.
Owned persistent disks left by a previously removed node no longer block
destroying the remaining nodes. Ordinary destroy retains those disks; explicit
persistent deletion or purge is still required to remove them.

On macOS, fresh network setup finishes Homebrew discovery/installation or the
pinned-archive download before requesting administrator authentication. Homebrew
can invalidate an earlier sudo credential; the new order avoids that failure
without widening the privileged operation. Failed downloads do not prompt.

## SSH passthrough and completion

`farrow ssh [node] [--] [command ...]` opens a session or runs an optional
command. `farrow exec [node] [--] <command ...>` requires a command and passes
through its exit status. Presentation flags before `--` belong to Farrow;
`ssh` arguments after `--` are joined with spaces and interpreted by the remote
shell, like plain SSH. `exec` preserves argument boundaries; explicitly use
`sh -c` when you need shell expansion or pipelines. A single command string
retains the shell shorthand. Before `--`, only zero or one known node is accepted.
For convenience, omitting `--` uses a known first argument as the node, or
runs all arguments as a command on the default node with a warning. A first
argument within two edits of a node name is refused as a likely typo. Use an
explicit `--` in scripts.

Load `farrow completion bash|zsh|fish|powershell` for command and scoped-flag
completion. It also provides command aliases, templates, image aliases, closed
flag choices, and best-effort node names from the desired or applied
specification.

## Exit codes

| Code | `error` | Meaning |
|---:|---|---|
| 0 | | success, including usable guests with optional limitations |
| 1 | `runtime` | the operation ran and failed (a tool, download, or guest failed) |
| 2 | `usage` | the command line or inventory is wrong |
| 3 | `capability` | the host lacks a tool, the Farrow network, or a privilege |
| 4 | `conflict` | the deployment's state forbids it, or another farrow command holds it |
| 5 | `partial` | some nodes succeeded and some failed |
| 6 | `resource` | a host address, port, subnet, or disk is taken |
| 7 | `integrity` | a verified digest, signature, identity, or ownership did not match |
| 130 | `cancelled` | interrupted (SIGINT/SIGTERM) or confirmation declined |

A command that finds another farrow command holding the deployment waits up to
10 minutes and names it; `status`, `ssh`, `exec`, `ssh-config`, and `hosts`
do not wait and show the recorded state with a `note`.

`ssh` and `exec` pass through the SSH child exit code unchanged, including
255. That value may indicate an SSH connection failure or a remote command
returning 255; text, JSON, and process exit status agree.
