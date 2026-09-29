---
title: CLI
description: Farrow commands, important flags, structured output, and exit codes.
weight: 20
icon: fa-solid fa-terminal
aliases: [/docs/reference/json-api/]
---

**Version scope:** the public prerelease is v0.8.0. This page also describes
local source `b91ec37`, an unreleased 0.9 candidate reviewed on 2026-09-26.
Candidate-only changes are marked below. Check `farrow version` before using
these contracts in scripts; see the [version matrix](../../about/status/#documentation-baseline).

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

Bare `farrow` prints a short welcome with next commands: v0.8 exits 2, while
**0.9 candidate exits 0** and exposes `actions[]` in JSON/YAML. A bare namespace
such as `farrow image` still exits 2 (human help in text mode, a structured usage
error in JSON/YAML). Explicit `--help` always renders human help and exits 0.
The **0.9 candidate** also accepts `farrow --version`; `farrow version` works in both versions.

## Commands

| Area | Commands |
|---|---|
| Prepare | `setup`, `init`, `validate`, `doctor` |
| Lifecycle | `plan`, `up`, `start`, `stop`, `restart`, `reload`, `recreate`, `status`, `destroy`, `purge` |
| Access | `ssh`, `exec`, `logs`, `provision`, `ssh-config`, `hosts install/uninstall` |
| Images | `update`, `image list/info/pull/import/sync/prune/reset`, `repo scan/build/verify` |
| Host network | `network status/install/uninstall` |
| macOS guests (unreleased) | `mac …`; see [Mac Commands](../mac/) |
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
`hosts`, and `completion` have no aliases. The **0.9 candidate removes** the
v0.8 `rm` alias for `purge`; use the explicit `farrow purge` spelling.
Inside a namespace, `hosts` and
`network` use `i`/`u` for install/uninstall; `network status` uses `st`; and
`image` maps `list=ls`, `info=in`, `pull=p`, `prune=pr`, `sync=sy`,
and `import=i`. `image reset` keeps `reset-manifest` as a compatibility alias.

Farrow manages one deployment in the selected `FARROW_HOME` (default
`~/.farrow`), independently of the inventory directory. Commands using applied
state work from any directory. Configuration selection
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
| `-r`, `--repo` | select a repository where exposed; overrides `--mirror` and `FARROW_REPO`; `validate` gains this flag in the **0.9 candidate** |
| `--mirror` | use the China official repository for setup, Catalog, and image-resolving lifecycle commands |
| `-m`, `--mode` | select `host` or `shared` where the command exposes the macOS network mode |
| `-d`, `--dry-run` | show a setup/image plan without changing state |
| `-y`, `--yes` | apply a displayed host/setup/image plan |
| `--force` (`init`, `destroy`, `recreate`) | overwrite generated output or skip the typed confirmation; long-only because `-f` selects the Inventory |
| `-n`, `--no-wait` | return once QEMU is running, without readiness or guest recovery checks |
| `--rollback` (`up`, `reload`) | remove the prepare artifacts of nodes that failed to prepare in this run |
| `--delete-persistent` | during whole destroy, also delete retained data disks; invalid with node selectors |
| `--purge` | whole-deployment disposal: delete disks, keys, and deployment state; keep images |

Flags belong to commands; the following table lists the less obvious scopes:

| Command | Local controls |
|---|---|
| `init` | `--output/-o` (default `./farrow.yml`; `-` prints), `--cidr/-c`, `--force` |
| `plan` | `--file/-f`, `--repo/-r`; no `--mirror` or `--dry-run` |
| `start`, `restart` | `--no-wait/-n`; no `--file` or repository selection |
| `provision` | required `--script/-s`; `--sudo` uses guest `sudo -n`; `--parallel/-p` is 1–4 (default 1); `--timeout/-t` is positive, at most 24h (default 1h) |
| `ssh-config` | `--install/-i` or `--remove` (exclusive); `--name` defaults to `farrow`; removal accepts no nodes and requires no deployment |
| `logs` | `--source/-s serial\|qemu\|events` (default `serial`); `--follow/-f`; events accept no node |
| `image info`, `image pull` | optional image selector, `--arch/-a amd64\|arm64`, `--repo/-r`; only pull accepts `--mirror` |
| `image import` | `--sha256/-s`; `--name local-*` also requires `--boot/-b bios\|uefi` and `--source-user/-u` |
| `image prune` | `--dry-run/-d` or `--yes/-y` (exclusive); `--repo/-r` |
| `image sync` | URL or path, `--repo/-r`, and explicit `--allow-downgrade` |
| `network install` | `--cidr/-c` (default `10.10.10.0/24`), `--mode/-m` (default `host`), `--yes/-y`; macOS-only `--archive/-a`, `--interface-id/-i` |
| `network status` | optional `--cidr/-c`; no `--file` |
| `network uninstall`, `hosts install/uninstall` | `--yes/-y` |

`setup --dry-run` and `setup --yes` are mutually exclusive. `--cidr` rebases a
generated template; it does not rewrite an explicitly selected inventory.
`validate --repo` is available in the **0.9 candidate** and has no `--mirror`;
use `--repo https://repo.pigsty.cc/farrow` when checking that catalog.

In the **0.9 candidate**, `network` and `hosts` install/uninstall show a plan and
ask on a terminal (install defaults to yes, uninstall to no); without a terminal
they only show the plan unless `--yes` is supplied. In v0.8 these commands only
show the plan unless `--yes` is supplied, including on a terminal. For a fresh
macOS network, use `setup`; the candidate's `network install` directs you there
before asking for sudo. `--yes` accepts Farrow's plan but cannot supply a sudo password.

Rare, selection, or safety-widening controls such as `--mirror`, `--force`,
`--rollback`, `--remove`, `--allow-downgrade`, `--sudo`,
`--delete-persistent`, and `--purge` are
long-only. On commands that read an Inventory, `-f` always selects a file;
`logs -f` retains the conventional `--follow`. `-n` always means `--no-wait`,
and `-d` always means a dry run.

With a deployment, `farrow purge` performs the same disposal as
`farrow destroy --force --purge`, without confirmation. It accepts no nodes or Inventory, removes the
complete deployment plus persistent disks, keys, state, and the default SSH
fragment, and keeps images and the host network. With no deployment it succeeds
without changing the image cache, and can remove provably owned retained disks.
Missing state never authorizes deletion of residual node artifacts whose identity
cannot be proven. In the **0.9 candidate**, plain whole-deployment `destroy`
without a deployment also succeeds; `destroy --force --delete-persistent` and
`destroy --force --purge` without state instead fail with a hint to use `purge`.

## Structured failures (0.9 candidate)

The following unified failure contract belongs to the **unreleased 0.9 candidate**.
In v0.8, generic failures have `error`, `message`, and sometimes `operation_id`,
but classes and typed results differ; do not require the candidate's fields from v0.8.

Ordinary failures print `error: <message>` on stderr, the failing program's last
stderr lines when an external tool failed, and a `next:` line when there is one
clear action. SSH child exit failures are silent because the child has its own
output. If a failing command supplies no richer typed result, structured mode
writes a generic failure object before returning the exit code:
`error` (the class below), `message`, and where they apply a stable `reason`,
`next`, `operation_id`, and `command` (`name`, `argv`, `exit_status`, `signal`, `timed_out`,
`stderr`) for a failed external program. Existing typed failure results are
never followed by a second JSON/YAML document. The closed generic `error` classes
are listed below. `recreate_required` and `nodes_removed` are now `reason` values
under `error: "conflict"`, and the old `resource_conflict` class is now `resource`.

**A nonzero exit does not guarantee that stdout has this generic envelope.**
`doctor`, `network`, `provision`, lifecycle operations, and remote commands can
return their own report schemas. SSH child exits are internally classified as
`remote_exit`, but their public result has fields such as `success`, `exit_code`,
`stdout`, and `stderr`; its optional `error` is not the generic class contract.
Always preserve the process exit code and interpret the payload for that command.

## Lifecycle results

`plan` is read-only and returns success even when its action is `recreate` or
`blocked-removal`; automation must inspect the action and `create`, `recreate`,
`start`, `missing`, and `blocked` fields. For catalog images, plans read local
configuration and catalog data without requiring QEMU or host networking.
A registered `local-*` image also undergoes cache validation and requires
`qemu-img`. Plans download no images. They show exact images, total resources, change reasons, and disk effects. The **0.9 candidate**
also lists each data disk, including the implicit 128 GiB `/data`. `up` checks
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
The **0.9 candidate** leaves symlinked or hard-linked `~/.ssh/config` untouched,
publishes its fragment, and reports the `Include` line to add manually.

Guest management SSH is the readiness boundary. Optional setup failures are
reported in `nodes[].warnings`; completed recovery actions, including data resets,
are in `nodes[].repairs`. A usable guest with these limitations exits 0. Repeat
`up` to retry unfinished stages without restarting running VMs. Inspect the
warning fields when automation requires every configured feature.

A lifecycle batch with isolated node failures can exit 5 even when every selected
node failed; it reports
`N of M node(s) failed: <node> (<stage>: <error>); ...`. Common stages include `prepare`,
`start`, `readiness`, `bootstrap`, `guest-setup`, `stop`, and `status`; `readiness`
or `bootstrap` failures add
`run \`farrow logs <node>\` for the guest console`. Structured output carries
`failures[]` with `node`, `stage`, and `error` (and optional `reason` in the
**0.9 candidate**), plus `rolled_back` when
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

## Interrupted operations (0.9 candidate)

The candidate recognizes a recorded QEMU PID reused by an unrelated process as
a stopped node. An interrupted stop whose VM still runs is reconciled to running;
other unfinished transitions name the command that can finish them. `destroy`
settles interrupted transitions itself. A failed first `up` can be retried after
editing the inventory because its uncommitted artifacts are rolled back from the
journal. These are candidate recovery improvements, not additional v0.8 guarantees.

## Logs and environment

`logs` defaults to the guest serial console; `--source qemu` reads QEMU diagnostics,
and `--source events` reads the deployment-wide bounded event log. With `--follow`,
text output streams bytes and JSON emits NDJSON records (YAML emits a document
stream). The **0.9 candidate** renders ordinary event/QEMU log reads as readable
records, showing a QEMU argv only with `--verbose`.

| Environment variable | Purpose |
|---|---|
| `FARROW_HOME` | absolute private state directory; default `~/.farrow`; not a symlink or broad directory such as your home |
| `FARROW_REPO` | repository default; overridden by `--mirror`, then `--repo` where exposed |
| `FARROW_OUTPUT` | `text`, `json`, or `yaml`; presentation flags override it |
| `FARROW_VERBOSE` | boolean diagnostic default; presentation flags override it |
| `FARROW_VMNET_ARCHIVE` | absolute path to the pinned socket_vmnet archive for macOS setup; digest checks still apply |
| `NO_COLOR` | non-empty disables color |

## SSH passthrough and completion

`farrow ssh [node] [--] [command ...]` opens a session or runs an optional
command. `farrow exec [node] [--] <command ...>` requires a command and passes
through its exit status. Presentation flags before `--` belong to Farrow;
`ssh` arguments after `--` are joined with spaces and interpreted by the remote
shell, like plain SSH. `exec` preserves argument boundaries; explicitly use
`sh -c` when you need shell expansion or pipelines. A single command string
retains the shell shorthand. Before `--`, only zero or one known node is accepted.
For convenience, omitting `--` uses a known first argument as the node, or
runs all arguments as a command on the default node with a warning.
In the **0.9 candidate**, a first argument containing a digit or `-` is checked
for a near-miss node name: at most one edit for words of four characters or fewer,
or two edits for longer words. Such a typo is refused; ordinary commands such as
`ls`, `df`, and `wc` still run. Use an explicit `--` in scripts.

Load `farrow completion bash|zsh|fish|powershell` for command and scoped-flag
completion. It also provides command aliases, templates, image aliases, closed
flag choices, and best-effort node names from the desired or applied
specification. In the **0.9 candidate**, `-f` completion filters for YAML files.

## Exit codes

Numbers 0–7 and 130 exist in v0.8 as well, but this table gives their **0.9 candidate**
classification. In particular, v0.8 uses 4 for missing inventory on `up`/`plan`,
1 for unknown images, and 7 for some setup/network failures; the candidate uses
2 for missing inventory/unknown images and 1 or 3 for those setup/network failures.

| Code | `error` | Meaning |
|---:|---|---|
| 0 | | success, including usable guests with optional limitations |
| 1 | `runtime` | the operation ran and failed (a tool, download, or guest failed) |
| 2 | `usage` | the command line or inventory is wrong |
| 3 | `capability` | the host lacks a tool, the Farrow network, or a privilege |
| 4 | `conflict` | the deployment's state forbids it, or another farrow command holds it |
| 5 | `partial` | node-level batch failures; inspect `failures[]`; any successful peers are retained |
| 6 | `resource` | a host address, port, subnet, or disk is taken |
| 7 | `integrity` | a verified digest, signature, identity, or ownership did not match |
| 130 | `cancelled` | interrupted (SIGINT/SIGTERM) or confirmation declined |

In the **0.9 candidate**, a modifying command that finds another Farrow command
holding the deployment waits up to 10 minutes and names it; timeout is exit 4
with `reason: "deployment_busy"`. `status`, `ssh`, `exec`, `ssh-config`, and
`hosts` do not wait. `status` reports the concurrent operation in `note` while
showing recorded state; this is not a guarantee of a completed deployment.

`ssh` and `exec` pass through the SSH child exit code unchanged, including
255. That value may indicate an SSH connection failure or a remote command
returning 255; text, JSON, and process exit status agree.
