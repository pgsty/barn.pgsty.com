---
title: CLI
description: Barn commands, important flags, structured output, and exit codes.
weight: 20
icon: fa-solid fa-terminal
aliases: [/docs/reference/json-api/]
---

This reference covers common options and Linux lab commands in **Barn 0.9.1**.
For macOS guests, see [Mac commands](../mac/). Check
`barn version` when using another version.

```text
barn [--json|--yaml] [-v|--verbose] <command> [flags] [node...]
```

For the options available in your installed version, use command help. Each visible command describes its scope and provides examples:

```bash
barn --help
barn setup --help
barn image pull --help
```

Without a command, `barn` prints a welcome and suggested commands, then exits 0. JSON/YAML output includes `actions[]`.
A namespace without a subcommand, such as `barn image`, exits 2.
Text mode prints help. JSON/YAML mode returns a structured usage error.
Explicit `--help` always prints human-readable help and exits 0.
To inspect the build identity, use `barn --version` or `barn version`.

## Commands

| Area | Commands |
|---|---|
| Prepare | `setup`, `init`, `validate`, `doctor` |
| Lifecycle | `plan`, `up`, `start`, `stop`, `restart`, `reload`, `recreate`, `status`, `destroy`, `purge` |
| Access | `ssh`, `exec`, `logs`, `provision`, `ssh-config`, `hosts install/uninstall` |
| Images | `update`, `image list/info/pull/import/sync/prune/reset`, `repo scan/build/verify` |
| Host network | `network status/install/uninstall` |
| macOS guests | `mac …`; see [Mac Commands](../mac/) |
| Misc | `version`, `completion` |

No command refreshes the image catalog implicitly.
`update` fetches, verifies, and activates the configured repository's image catalog.
`image sync` recovers an image catalog from an exact URL or file.
Ordinary commands use the active local image catalog. Neither operation updates the Barn executable.

Frequently used commands have aliases within their command scope:

| Command | Aliases | Command | Aliases |
|---|---|---|---|
| `setup` | `s` | `validate` | `v` |
| `plan` | `pl` | `recreate` | `rc` |
| `status` | `st` | `destroy` | `de` |
| `ssh-config` | `sc` | `image` | `images`, `im` |
| `doctor` | `dt` | `network` | `n`, `net` |
| `exec` / `logs` | `ex` / `l` | `version` | `ver` |

`up`, `ssh`, `init`, `start`, `stop`, `restart`, `reload`, `provision`,
`hosts`, and `completion` have no aliases. Use the explicit `barn purge` spelling; `rm` is not a command alias.
Inside a namespace, `hosts` and
`network` use `i`/`u` for install/uninstall; `network status` uses `st`; and
`image` maps `list=ls`, `info=in`, `pull=p`, `prune=pr`, `sync=sy`,
and `import=i`.

Barn manages one deployment in the selected `BARN_HOME` (default `~/.barn`).
The inventory directory does not determine deployment identity. Commands that use applied state work from any directory.
Each command determines its configuration source. `-f` is not a global flag:

| Commands | Desired-state source |
|---|---|
| `setup [template]` | explicit `-f`, otherwise discovery, otherwise generate `meta`; template and `-f` are exclusive |
| `init [template]` | generate a new inventory; read no desired state; `--force` explicitly replaces the output |
| `validate` | explicit `-f`, then discovery; never applied state |
| `plan`, `up`, `reload`, `recreate` | explicit `-f`, then discovery, then the applied resolved specification |
| other lifecycle/access commands | no desired-state inventory; they use applied state |

If neither an inventory nor an applied deployment exists, interactive `up` can generate the default inventory.
It can also prepare missing host dependencies and restore an intact inactive Barn network.
This automatic preparation proceeds without a separate Barn confirmation, but sudo can still request credentials.
To review the host plan first, use `setup --dry-run`. Scripts should run `setup --yes` explicitly.
If no inventory exists, `init` is optional.

If the default subnet is occupied, setup can select another private `/24` for a fresh, unedited default template.
It backs up an existing template as `barn.yml.before-network-change`.
Explicit `-f` files, edited templates, and existing deployments retain their subnet.

## Important flags

| Flag | Meaning |
|---|---|
| `--json`, `--yaml` | machine-readable stdout; progress remains on stderr; intentionally no shorthand |
| `-v`, `--verbose` | bounded diagnostics on stderr |
| `-c`, `--cidr` | select the RFC1918 `/24` for generated `init`/`setup` templates or host-network inspection/install |
| `-f`, `--file` | select an inventory for commands that read desired state |
| `-r`, `--repo` | select a repository where exposed; overrides `--mirror` and `BARN_REPO`; `validate` gains this flag in Barn 0.9.0 |
| `--mirror` | use the China official repository for setup, image catalog commands, and lifecycle commands that resolve images |
| `-m`, `--mode` | select `host` or `shared` where the command exposes the macOS network mode |
| `-d`, `--dry-run` | show a setup/image plan without changing state |
| `-y`, `--yes` | apply a displayed host/setup/image plan |
| `--force` (`init`, `destroy`, `recreate`) | overwrite generated output or skip the typed confirmation; long-only because `-f` selects the inventory |
| `-n`, `--no-wait` | return once QEMU is running, without readiness or guest recovery checks |
| `--rollback` (`up`, `reload`) | remove the prepare artifacts of nodes that failed to prepare in this run |
| `--delete-persistent` | during whole destroy, also delete retained data disks; invalid with node selectors |
| `--purge` | whole-deployment deletion: delete disks, keys, and deployment state; keep images |

Flags belong to commands; the following table lists the less obvious scopes:

| Command | Local controls |
|---|---|
| `init` | `--output/-o` (default `./barn.yml`; `-` prints), `--cidr/-c`, `--force` |
| `setup [meta\|dual\|trio\|full]` | `--file/-f`, `--cidr/-c`, `--repo/-r`, `--mirror`, `--mode/-m`, `--dry-run/-d`, `--yes/-y`; default template is `meta` |
| `validate` | `--file/-f`, `--repo/-r`; accepts no nodes |
| `plan` | `--file/-f`, `--repo/-r`; no `--mirror` or `--dry-run` |
| `up`, `reload` | `--file/-f`, `--repo/-r`, `--mirror`, `--no-wait/-n`, `--rollback` |
| `recreate` | `--file/-f`, `--repo/-r`, `--mirror`, `--force`, `--no-wait/-n`; no `--rollback` |
| `start`, `restart` | `--no-wait/-n`; no `--file` or repository selection |
| `stop`, `status` | node selectors and common presentation flags only |
| `destroy` | `--force`, `--delete-persistent`, `--purge`; the last two require whole-deployment scope |
| `purge`, `doctor`, `version` | no local flags or positional arguments |
| `provision` | required `--script/-s`; `--sudo` uses guest `sudo -n`; `--parallel/-p` is 1–4 (default 1); `--timeout/-t` is positive, at most 24h (default 1h) |
| `ssh-config` | `--install/-i` or `--remove` (exclusive); `--name` defaults to `barn`; removal accepts no nodes and requires no deployment |
| `logs` | `--source/-s serial\|qemu\|events` (default `serial`); `--follow/-f`; events accept no node |
| `image info`, `image pull` | optional image selector, `--arch/-a amd64\|arm64`, `--repo/-r`; only pull accepts `--mirror` |
| `image import` | `--sha256/-s`; `--name local-*` also requires `--boot/-b bios\|uefi` and `--source-user/-u` |
| `image prune` | `--dry-run/-d` or `--yes/-y` (exclusive); `--repo/-r` |
| `image sync` | URL or path, `--repo/-r`, and explicit `--allow-downgrade` |
| `update` | `--repo/-r`, `--mirror`; no image selector |
| `image list`, `image reset` | `--repo/-r`; no selector, `--arch`, or `--mirror` |
| `repo scan/build/verify` | exactly one absolute repository directory; no local flags |
| `network install` | `--cidr/-c` (default `10.10.10.0/24`), `--mode/-m` (default `host`), `--yes/-y`; macOS-only `--archive/-a`, `--interface-id/-i` |
| `network status` | optional `--cidr/-c`; no `--file` |
| `network uninstall`, `hosts install/uninstall` | `--yes/-y` |

`setup --dry-run` and `setup --yes` are mutually exclusive. `--cidr` changes the subnet of a
generated template. It does not rewrite an explicitly selected inventory.
`validate --repo` is available in Barn 0.9.1 and has no `--mirror`;
use `--repo https://repo.pigsty.cc/barn` when checking that image catalog.

In Barn 0.9.1, `network` and `hosts` install/uninstall show a plan.
On a terminal, they ask for confirmation. Installation defaults to yes; uninstallation defaults to no.
Without a terminal, they show the plan but do not apply it unless you supply `--yes`.
For a new macOS network, use `setup`. `network install` directs you to that command before requesting sudo.
`--yes` accepts Barn's plan but cannot supply a sudo password.
While nodes are running, `network uninstall` refuses removal.
Stopping or destroying a deployment does not uninstall the host-wide network.

The following selection and safety controls have long forms only: `--mirror`, `--force`,
`--rollback`, `--remove`, `--allow-downgrade`, `--sudo`, `--delete-persistent`, and `--purge`.
On commands that read an inventory, `-f` selects a file. `logs -f` means `--follow`.
`-n` means `--no-wait`. `-d` means a dry run.
These shorthand rules apply to Linux commands. `barn mac logs -n` sets the number of log lines.

When a deployment exists, `barn purge` performs the same deletion as `barn destroy --force --purge`, without confirmation.
It accepts no nodes or inventory. It removes the complete deployment, persistent disks, keys, state, and default SSH fragment, while keeping images and the host network.
When no deployment exists, it succeeds without changing the image cache. It can also remove retained disks whose ownership it can verify.
If state is missing, Barn does not delete residual node artifacts whose identity it cannot verify.
In Barn 0.9.1, ordinary whole-deployment `destroy` also succeeds when no deployment exists.
Without state, `destroy --force --delete-persistent` and `destroy --force --purge` fail and suggest `purge`.

## Structured failures

The following failure format applies to **Barn 0.9.1**. Check the process exit code first, then interpret the output for the command you ran.

For ordinary failures, Barn prints `error: <message>` on stderr.
If an external program failed, Barn includes its last stderr lines. If one clear action exists, Barn also prints a `next:` line.
Barn does not add an error message for an SSH child exit failure, because the child provides its own output.
If a failed command has no command-specific result, structured mode writes a generic failure object before returning the exit code.
The object contains `error` (the class below) and `message`.
Where applicable, it also contains a stable `reason`, `next`, `operation_id`, and failed-program details in `command`.
Those details are `name`, `argv`, `exit_status`, `signal`, `timed_out`, and `stderr`.
Barn never appends a second JSON/YAML document after a command-specific failure result. The generic `error` classes are listed below.
`recreate_required` and `nodes_removed` are now `reason` values under `error: "conflict"`.
The former `resource_conflict` class is now `resource`.

**A nonzero exit does not guarantee this generic failure object on stdout.**
`doctor`, `network`, `provision`, lifecycle operations, and remote commands can return their own report formats.
Barn internally classifies SSH child exits as `remote_exit`.
Their public result instead contains fields such as `success`, `exit_code`, `stdout`, and `stderr`.
Its optional `error` field does not use the generic error classes.
Retain the process exit code alongside the parsed result.

## Lifecycle results

Without node selectors, lifecycle operations address all nodes.
`ssh`, `exec`, and node logs default to the committed control node.
If the control node has not been prepared, they select the first committed node.
Selectors are node names such as `meta`. Inventory IPs, group names, and `vm_alias` values are not selectors.

`restart` restarts applied nodes without reading an inventory.
Before stopping selected nodes, `reload` checks the desired inventory. It then runs `up`.
It can add nodes, but refuses changed definitions or removals.
`recreate` applies changed node definitions by replacing root and non-persistent data disks. It preserves compatible persistent disks.
First review the effects with [`barn plan` and the disk policy](../configuration/#data-disks).

Recreating selected nodes is blocked if unselected nodes still have conflicting configuration changes.
Barn checks this before stopping nodes or deleting disks and tells you which nodes to select together.

When configuration changes require a destructive operation, Barn returns a conflict with the next commands: `barn plan`, then `barn recreate <node>` or `barn destroy <node>`.
On a terminal, those commands request a confirmation word. Use `--force` when a script must skip that prompt.

### Planning

`plan` is read-only and returns success even when its action is `recreate` or `blocked-removal`.
Automation must inspect the action and the `create`, `recreate`, `start`, `missing`, and `blocked` fields.

For image catalog entries, plans read local configuration and image catalog data without requiring QEMU or host networking.
For a registered `local-*` image, plans also validate the cache and require `qemu-img`.
Plans do not download images. They show exact images, total resources, change reasons, and disk effects.
Barn 0.9.1 also lists each data disk, including the implicit 128 GiB `/data`.

### Starting and SSH configuration

Before applying changes, `up` checks host capabilities and address availability.
`up` creates missing nodes, starts stopped nodes, and checks running nodes for readiness.
It rewrites Barn's installed SSH client configuration from the complete applied deployment.
`recreate` performs the same full refresh. Node destroy removes stale entries; whole-deployment destroy removes the configuration.
`start` starts stopped nodes and checks running nodes for readiness. `start` and `restart` also refresh SSH aliases.

If the VM operation succeeds but writing SSH client configuration fails, the command reports a warning and remains successful.
`barn ssh` still works. Structured output reports integration warnings in `warnings[]`.

Barn 0.9.1 does not modify a symlinked or hard-linked `~/.ssh/config`.
It writes its fragment and shows the `Include` line to add manually.

Starting commands refresh Barn hosts and control-node SSH entries in running guests.
Stopped guests receive these updates when they start.

The control node's Barn-managed SSH entries accept replacement host keys without recording them in known_hosts.
This keeps recreated lab nodes reachable. Barn preserves user-added SSH entries.

### Readiness

Barn considers a guest ready when its management SSH connection works.
It reports optional setup failures in `nodes[].warnings`. It reports completed recovery actions, including data resets, in `nodes[].repairs`.
A usable guest with these limitations exits 0.
To retry unfinished stages without restarting running VMs, repeat `up`.
If automation requires every configured feature, inspect the warning fields.

`--no-wait` skips guest readiness, guest recovery, and guest SSH/hosts updates. A later `up` completes them.

### Node failures

A lifecycle batch can exit 5 for isolated node failures, even when every selected node fails.
It reports `N of M node(s) failed: <node> (<stage>: <error>); ...`.
Common stages include `prepare`, `start`, `readiness`, `bootstrap`, `guest-setup`, `stop`, and `status`.
For `readiness` or `bootstrap` failures, Barn suggests `barn logs <node>` to read the guest console.
Structured output includes `failures[]` with `node`, `stage`, and `error`, plus optional `reason` in Barn 0.9.1.
It also includes `rolled_back` when `--rollback` removed preparation artifacts for nodes that never committed.
See [A node did not become ready](../../start/troubleshooting/#a-node-did-not-become-ready).

### Status

`status` shows node, state, IP, exact image, and CPU/memory.
For SSH ports, architecture, accelerator, and PID, use `--verbose`. Ordinary text output also identifies TCG.
If one node is degraded, status still shows its peers. It exits 5 and retains per-node errors and `failures[]`.
Running means the VM process is running. Status does not check guest readiness.

## Recovery

`up` and `start` limit missing host-share failures to the affected nodes.
If a new node fails to prepare, `up` still starts independent existing stopped nodes.
Partial results use exit code 5 and preserve successful nodes.
Retry suggestions retain the inventory, repository, and applicable flags. A `start` retry remains `start`.

Setup and its lifecycle retry share one `operation_id`.
After failed setup, `barn logs --source events --json` can read the size-limited phase log even before deployment state exists.
Setup traces omit command arguments and authentication data. Keep the command output for the detailed cause.
`setup --dry-run` writes no trace.

Successful `destroy --delete-persistent` and `purge` summaries describe the final deletion and retention results.
Purge preserves the image cache and host network.

Owned persistent disks from a previously removed node do not block destruction of the remaining nodes.
Ordinary destroy retains those disks. Explicit persistent deletion or purge is required to remove them.

On macOS, new network setup completes Homebrew discovery or installation, or the pinned-archive download, before requesting administrator authentication.
This order prevents Homebrew from invalidating credentials obtained before installation; the privileged operation remains the same.
Failed downloads do not trigger an authentication prompt.

## Interrupted operations

If an unrelated process reuses a recorded QEMU PID, Barn identifies the node as stopped.
If stop was interrupted but the VM still runs, Barn records it as running.
For other unfinished transitions, Barn identifies the command that can complete them.
`destroy` resolves interrupted transitions itself.
After a failed first `up`, you can edit the inventory and retry. Barn rolls back uncommitted artifacts from the journal.

## Logs and environment

`logs` reads the guest serial console by default.
`--source qemu` reads QEMU diagnostics. `--source events` reads the deployment-wide bounded event log.
With `--follow`, text output streams bytes, JSON emits NDJSON records, and YAML emits a document stream.
Barn 0.9.1 shows ordinary event/QEMU log reads as readable records. It shows QEMU argv only with `--verbose`.

| Environment variable | Purpose |
|---|---|
| `BARN_HOME` | absolute private state directory; default `~/.barn`; not a symlink or broad directory such as your home |
| `BARN_REPO` | repository default; overridden by `--mirror`, then `--repo` where exposed |
| `BARN_OUTPUT` | `text`, `json`, or `yaml`; presentation flags override it |
| `BARN_VERBOSE` | boolean diagnostic default; presentation flags override it |
| `BARN_VMNET_ARCHIVE` | absolute path to the pinned socket_vmnet archive for macOS setup; digest checks still apply |
| `NO_COLOR` | non-empty disables color |

## SSH passthrough and completion

`barn ssh [node] [--] [command ...]` opens a session or runs an optional command.
`barn exec [node] [--] <command ...>` requires a command and returns its exit status.
Presentation flags before `--` belong to Barn.
Barn joins `ssh` arguments after `--` with spaces. The remote shell interprets them as it does for plain SSH.
`exec` preserves argument boundaries. For shell expansion or pipelines, explicitly use `sh -c`.
A single command string retains shell shorthand behavior.

Before `--`, Barn accepts no node or one known node.
If you omit `--`, a known first argument selects the node.
Otherwise, Barn runs all arguments as a command on the default node and reports a warning.

In Barn 0.9.1, Barn checks a first argument containing a digit or `-` for a possible node-name typo.
For words of four characters or fewer, the limit is one edit; for longer words, it is two edits.
Barn refuses such typos. Ordinary commands such as `ls`, `df`, and `wc` still run.
In scripts, use an explicit `--`.

Load `barn completion bash|zsh|fish|powershell` to complete commands and their flags.
It also completes command aliases, templates, image aliases, and enumerated flag values.
It attempts to read node names from the desired or applied specification.
In Barn 0.9.1, `-f` completion lists only YAML files.

## Exit codes

This table lists **Barn 0.9.1** exit codes.
Missing inventory and unknown images are usage errors (2); setup and network
failures use runtime (1) or capability (3), according to their cause.

| Code | `error` | Meaning |
|---:|---|---|
| 0 | | success, including usable guests with optional limitations |
| 1 | `runtime` | the operation ran and failed (a tool, download, or guest failed) |
| 2 | `usage` | the command line or inventory is wrong |
| 3 | `capability` | the host lacks a tool, the Barn network, or a privilege |
| 4 | `conflict` | the deployment's state forbids it, or another barn command holds it |
| 5 | `partial` | node-level batch failures; inspect `failures[]`; any successful peers are retained |
| 6 | `resource` | a host address, port, subnet, or disk is taken |
| 7 | `integrity` | a verified digest, signature, identity, or ownership did not match |
| 130 | `cancelled` | interrupted (SIGINT/SIGTERM) or confirmation declined |

In Barn 0.9.1, a modifying command waits up to 10 minutes if another Barn command holds the deployment lock.
It identifies the command holding the lock. A timeout exits 4 with `reason: "deployment_busy"`.
`status`, `ssh`, `exec`, `ssh-config`, and `hosts` do not wait.
`status` shows recorded state and reports the concurrent operation in `note`. This does not mean that the deployment operation has completed.

`ssh` and `exec` return the SSH child exit code unchanged, including 255.
That value can indicate an SSH connection failure or a remote command returning 255.
Text output, JSON output, and process exit status agree.
