---
title: CLI
description: Barn commands, important flags, structured output, and exit codes.
weight: 20
icon: fa-solid fa-terminal
aliases: [/docs/reference/json-api/]
---

This reference follows **Barn 1.1.0** for global presentation options and Linux lab commands. For macOS guests, see [Mac Commands](../mac/). Check your build with `barn version` and each command's `--help`.

```text
barn [--json|--yaml] [-v|--verbose] <command> [flags] [node...]
```

Every command documents its local flags and examples through `--help`:

```bash
barn --help
barn setup --help
barn image pull --help
```

Running `barn` with no arguments prints the same complete help as `barn --help` and exits `0`; with `--json` or `--yaml` it returns an `actions[]` array of suggested next commands instead. Invoking a command group without a subcommand—such as `barn image`—exits `2` (printing help in text mode or a usage error object in JSON/YAML mode). Explicit `--help` always prints human-readable help and exits `0`. Use `barn --version` or `barn version` to inspect the build identity.

## Commands {#commands}

| Area | Commands |
|---|---|
| Prepare | `setup`, `init`, `validate`, `doctor` |
| Lifecycle | `plan`, `up`, `start`, `stop`, `restart`, `reload`, `resize`, `recreate`, `status`, `destroy`, `purge` |
| Access | `ssh`, `exec`, `logs`, `provision`, `ssh-config`, `hosts install/uninstall` |
| Images | `update`, `image list/info/pull/import/sync/prune/reset`, `repo scan/build/verify` |
| Host network | `network status/install/uninstall` |
| macOS guests | `mac …` — see [Mac Commands](../mac/) |
| Misc | `version`, `completion` |
{.wide .expand}

Ordinary commands read the active local image catalog without contacting remote repositories. Run `barn update` to fetch, verify, and activate the configured repository's catalog, or `barn image sync` to recover a catalog from an exact URL or local file. Neither command replaces the `barn` executable.

Frequently used commands define short aliases within their scope:

| Command | Aliases | Command | Aliases |
|---|---|---|---|
| `setup` | `s` | `validate` | `v` |
| `plan` | `pl` | `recreate` | `rc` |
| `status` | `st` | `destroy` | `de` |
| `ssh-config` | `sc` | `image` | `images`, `im` |
| `doctor` | `dt` | `network` | `n`, `net` |
| `exec` / `logs` | `ex` / `l` | `version` | `ver` |
{.wide .expand}

`up`, `ssh`, `init`, `start`, `stop`, `restart`, `reload`, `resize`, `provision`, `hosts`, `purge`, `update`, `repo`, `mac`, and `completion` have no top-level shorthand (`rm` is not an alias for `purge`). Inside subcommand groups, `hosts` and `network` map `i`/`u` to `install`/`uninstall`, `network status` accepts `st`, and `image` maps `list=ls`, `info=in`, `pull=p`, `prune=pr`, `sync=sy`, and `import=i`.

Barn manages a single deployment per `BARN_HOME` (default `~/.barn`; see [Configuration](../configuration/#discovery)), so commands that operate on applied state work from any directory when `BARN_HOME` points to the same location. Use an absolute `BARN_HOME` when changing working directories. Each command resolves its desired-state source independently (`-f` is a per-command flag rather than a global flag):

| Commands | Desired-state source |
|---|---|
| `setup [template]` | Explicit `-f`, then local discovery, otherwise generates `meta` (`template` and `-f` are mutually exclusive) |
| `init [template]` | Generates a new inventory without reading existing state; `--force` overwrites an existing file |
| `validate` | Explicit `-f`, then local discovery; never falls back to applied state |
| `plan`, `up`, `reload`, `recreate`, `resize` | Explicit `-f`, then local discovery, then the applied deployment specification |
| Other lifecycle & access commands | Operate directly on applied state in `BARN_HOME` |
{.wide .expand}

When a host dependency or the Barn network is missing, `up`, `start`, `restart`, and `reload` on a terminal prepare the host as `barn setup` does: they show the host-preparation plan and ask once before installing packages or the network (sudo may still prompt for your OS password). When neither an inventory file nor an applied deployment exists, an interactive `barn up` also generates the default `meta` inventory first. Without a terminal these commands only report what is missing. Run `barn setup --dry-run` to inspect the plan, and `barn setup --yes` to prepare the host from a script.

If the default `10.10.10.0/24` subnet conflicts with an existing host route while preparing a fresh, unedited default template, `setup` selects another free RFC1918 `/24` and backs up the prior template as `barn.yml.before-network-change`. Explicit `-f` inventories, edited files, and existing deployments always keep their configured subnet.

## Important flags {#important-flags}

| Flag | Meaning |
|---|---|
| `--json`, `--yaml` | Emit structured output on stdout while keeping progress on stderr (long-form only) |
| `-v`, `--verbose` | Emit bounded diagnostic logs on stderr |
| `-c`, `--cidr` | Set the RFC1918 `/24` subnet for `init`/`setup` templates or `network` inspection/installation |
| `-I`, `--image` | Choose an image for a generated template or override selected nodes' `vm_image`/`vm_version` on commands listed below |
| `-A`, `--arch` | Select guest or artifact architecture: `native`, `amd64` (`x86_64`, `x64`), or `arm64` (`aarch64`, `a64`) |
| `-f`, `--file` | Select an inventory file for commands that read desired state |
| `-r`, `--repo` | Select an image repository URL or path, overriding `--mirror` and `BARN_REPO` |
| `--mirror` | Use the China official repository (`https://repo.pigsty.cc/barn`) for `setup`, `up`, `reload`, `recreate`, `update`, and `image pull` |
| `-m`, `--mode` | Select `host` or `shared` network mode on macOS |
| `-d`, `--dry-run` | Print the execution plan for `setup` or `image prune` without modifying state |
| `--yes` | Confirm host, setup, image, or destruction plans; `-y` is available only where listed below |
| `--force` (`init`, `destroy`, `recreate`) | Overwrite an existing inventory (`init`) or skip the interactive confirmation word (long-form only, as `-f` means `--file`) |
| `--ask` (`purge`) | Display the VM list and deletion scope, then require `y`/`yes` before deleting |
| `-n`, `--no-wait` | Return as soon as QEMU starts, skipping guest SSH readiness and recovery checks |
| `--rollback` (`up`, `reload`) | Clean up uncommitted preparation artifacts for nodes that failed during the current run |
| `--delete-persistent` | Delete `persistent: true` data disks during a whole-deployment `destroy` |
| `--purge` | Delete all deployment disks, SSH keys, and state during a whole-deployment `destroy`, while keeping cached base images |
{.wide .expand}

Each command exposes only the flags that apply to its operation:

| Command | Local controls |
|---|---|
| `init` | `--output/-o` (default `./barn.yml`; `-` writes to stdout), `--cidr/-c`, `--image/-I`, `--arch/-A`, `--force` |
| `setup [meta\|dual\|trio\|full]` | `--file/-f`, `--cidr/-c`, `--image/-I`, `--arch/-A`, `--repo/-r`, `--mirror`, `--mode/-m`, `--dry-run/-d`, `--yes/-y` (defaults to `meta`) |
| `validate` | `--file/-f`, `--repo/-r`, `--image/-I`, `--arch/-A`; accepts no node arguments |
| `plan` | `--file/-f`, `--repo/-r`, `--image/-I`, `--arch/-A` |
| `up`, `reload` | `--file/-f`, `--repo/-r`, `--image/-I`, `--arch/-A`, `--mirror`, `--no-wait/-n`, `--rollback` |
| `recreate` | `--file/-f`, `--repo/-r`, `--image/-I`, `--arch/-A`, `--mirror`, `--yes`/`--force`, `--no-wait/-n` |
| `resize` | `--file/-f`, `--image/-I`, `--arch/-A` (still applies only CPU/memory changes) |
| `start`, `restart` | `--no-wait/-n` |
| `stop`, `status` | Node selectors and global presentation flags only |
| `destroy` | `--yes`/`--force`, `--delete-persistent`, `--purge` (the last two require whole-deployment scope) |
| `purge` | Deletes immediately; `--ask` enables confirmation; accepts no node arguments or `--yes`, `-y`, `--force` |
| `doctor`, `version` | Global presentation flags only |
| `provision` | Required `--script/-s`; `--sudo`; `--parallel/-p` positive integer (default `1`); `--timeout/-t` positive duration (default `1h`) |
| `ssh-config` | Optional node selectors; `--install/-i` or `--remove` (mutually exclusive); `--name` (default `barn`). `--remove` takes no nodes and works without deployment state |
| `logs` | `--source/-s serial\|qemu\|events` (default `serial`); `--follow/-f` (`events` is deployment-wide and takes no node) |
| `image info`, `image pull` | Optional image selector, `--arch/-A` (legacy `-a` also works), `--repo/-r`; `pull` also accepts `--mirror` |
| `image import` | `--sha256/-s`; named imports (`--name local-*`) also require `--boot/-b bios\|uefi` and `--source-user/-u`, with optional `--arch/-A` to record guest architecture |
| `image prune` | `--dry-run/-d` or `--yes/-y` (mutually exclusive); `--repo/-r` |
| `image sync` | Source URL or file path, `--repo/-r`, and optional `--allow-downgrade` |
| `update` | `--repo/-r`, `--mirror` |
| `image list`, `image reset` | `--repo/-r` |
| `repo scan/build/verify` | One repository directory; relative paths, `~/`, and directory symlinks are supported |
| `network install` | `--cidr/-c` (default `10.10.10.0/24`), `--mode/-m` (default `host`), `--yes/-y`; macOS-only `--archive/-a`, `--interface-id/-i` |
| `network status` | Optional `--cidr/-c` |
| `network uninstall`, `hosts install/uninstall` | `--yes/-y` |
{.wide .expand}

Notes on flag behavior:

- `setup --dry-run` and `setup --yes` are mutually exclusive. `--cidr` adjusts generated templates and never rewrites an existing `-f` file. For `validate` against the China mirror, pass `--repo https://repo.pigsty.cc/barn`.
- `init` and template-generating `setup` write `-I` and `-A` into `all.vars.vm_image` and `all.vars.vm_arch`; `setup` rejects these generation flags when using an existing inventory. `up`, `plan`, `reload`, `recreate`, `resize`, and `validate` apply overrides in memory for that invocation. Image overrides affect selected nodes; architecture affects the whole deployment. See [precedence and defaults](../configuration/#image-and-architecture).
- Standalone `image info/pull/import` default to the host architecture without reading inventory `vm_arch`; select another with `-A`. `image import -A` requires `--name`. Since qcow2 metadata cannot identify the guest CPU, the declared architecture must match the actual image.
- `network` and `hosts` `install`/`uninstall` display a plan and prompt for confirmation on a terminal (`install` defaults to yes; `uninstall` defaults to no). Without `--yes`, they only print the plan and exit `0` when stdin is not a terminal or the output is `--json`/`--yaml`; check `applied` in the structured report, or pass `--yes` to apply the plan. On macOS, first-time network installation is handled by `barn setup`. `network uninstall` refuses to remove the host network while VMs are running, and stopping or destroying a deployment leaves the host network installed. On Linux, `network uninstall` keeps the global networkd unit state when other host links exist or exclusive Barn use cannot be established; the plan reports `preserve_networkd`, and the applied report explains the decision in `checks.networkd`.
- Safety and repository flags (`--ask`, `--mirror`, `--force`, `--rollback`, `--remove`, `--allow-downgrade`, `--sudo`, `--delete-persistent`, `--purge`) are long-form only. On Linux commands, `-f` selects `--file` (except `barn logs -f`, where `-f` means `--follow`), `-n` means `--no-wait` (whereas `barn mac logs -n` sets the line count), and `-d` means `--dry-run`.
- `barn purge` deletes immediately by default: all nodes, persistent disks, SSH keys, deployment state, and the default SSH config fragment are removed; cached images and the host network remain. Only `--ask` displays the node list and deletion scope before prompting: `y`/`yes` confirms; `n`/`no`, an empty line, or EOF cancels with exit `130`. It does not accept `--yes`, `-y`, or `--force`. With no deployment, default `barn purge` and whole-deployment `barn destroy` succeed cleanly; purge also removes retained persistent disks with intact Barn ownership metadata. Unverifiable retained directories still prevent deletion. If deployment state is missing, `destroy --force --delete-persistent` and `destroy --force --purge` direct you to `barn purge`.

## Structured failures {#structured-failures}

Always check the process exit code first, then parse the command's output.

In human-readable text mode, operations lasting one second or longer on a terminal redraw a single live table (`NAME ADDRESS STATE MESSAGE`, `ITEM STATE MESSAGE`, or `IMAGE STATE MESSAGE`) on stderr above a completion line ending with `[DONE]`, `[FAILED]`, or `[CANCELLED]`. When both stdout and stderr are a terminal without `--verbose`, the completed table freezes in place so stdout prints only follow-up hints (`connect:`, `retry:`, `next:`). Ordinary failures print `error: <message>` on stderr, followed by the last stderr lines of any failed external program and an actionable `next:` command when available. SSH child exit failures pass the remote process output through directly without adding a wrapper error line.

In `--json` or `--yaml` mode, commands that define their own report schema (`doctor`, `network`, `provision`, lifecycle commands, and `ssh`/`exec`) return that report schema directly on stdout—for example, `exec` returns `success`, `exit_code`, `stdout`, and `stderr`. When a command fails before producing a command-specific report, Barn writes a single generic failure object to stdout:

- `error`: One of the stable error classes in the [Exit codes](#exit-codes) table (`recreate_required` and `nodes_removed` are reported as `reason` values under `error: "conflict"`, and resource collisions use `error: "resource"`).
- `message`: Human-readable summary.
- Optional context fields: `reason`, `next`, `operation_id`, and `command` (`name`, `argv`, `exit_status`, `signal`, `timed_out`, `stderr`).

Single-result commands emit one JSON or YAML document. `logs --follow` uses NDJSON or a YAML document stream; structured interactive SSH sends session output to stderr and its final report to stdout. The design rationale is in [CLI contracts](/blog/design/cli-contracts/).

## Lifecycle results {#lifecycle-results}

When invoked without node arguments, lifecycle commands target all managed nodes in the deployment, whereas `ssh`, `exec`, and per-node `logs` default to the prepared control node (or the first prepared node if the control node is not yet prepared). Node selectors must be resolved node names such as `meta`—IP addresses, group names, and `vm_alias` entries are not valid command-line selectors.

- **`restart`** restarts applied nodes using their committed state without re-reading `barn.yml`.
- **`reload`** validates the effective desired specification and startup dependencies before stopping selected nodes, then runs `up` for that selection. It can add nodes; changes that replace an existing VM still require `recreate`.
- **`resize`** applies only `vm_cpu` and `vm_mem` changes. Supported increases may be hot-plugged; decreases, older VMs, and unsupported backends use a stop/start fallback while preserving the VM identity and disks. It refuses image, disk, network, share, create, remove, and deployment-wide changes.
- **`recreate`** applies changed node definitions by replacing root disks and non-persistent data disks while reattaching compatible [persistent data disks](../configuration/#data-disks). Explicit `plan`, `up`, `reload`, `recreate`, and `resize` selections retain unselected peers' applied definitions, including peers edited or omitted in YAML. Uncreated, unselected nodes do not require image resolution. Conflicting addresses, aliases, control-node roles, or deployment-wide settings still fail preflight; omitting selectors applies the whole inventory.
- When configuration drift requires a destructive action, `up` and `reload` exit with a `conflict` error pointing to `barn plan` and `barn recreate <node>` or `barn destroy <node>`. On a terminal, `recreate` and `destroy` list the nodes they replace or remove and require typing the command name unless `--yes` (or `--force`) is passed; without a terminal they exit `2` unless one of those flags is present. Without node arguments, both apply to the whole deployment.

A whole-deployment `recreate` refuses an inventory that omits an existing node before any VM stops (`conflict`, reason `nodes_removed`, exit `4`). Remove that node explicitly with `barn destroy <node>`, or add it back to the inventory. Barn checks the scope again under the destruction lock; if the applied state changed during preflight, recreate exits with reason `deployment_changed`, and you can review the plan and retry.

Destroying the control node makes the first remaining node the control node. Update the inventory's control role (`admin_ip`) to that node, then run `barn up` to install its control SSH access; `--no-wait` defers that step. Until you do, an inventory that still names the deleted node as control is role drift and `up` refuses it; to bring the old node back, add it as a regular node. Barn refuses to destroy the control node, before deleting anything, when the successor has an unfinished prepare record that cannot be completed, and the error names the successor.

### Planning {#planning}

`barn plan` is read-only and exits `0` even when its recommended `action` is `resize`, `recreate`, or `blocked-removal`; automation scripts should inspect `action`, the `create`, `resize`, `recreate`, `start`, and `missing` arrays, and the optional `blocked` explanation string.

For catalog images, `plan` resolves configuration and catalog metadata locally without requiring QEMU or host networking; for `local-*` imported images, it also verifies the cached image via `qemu-img`. Plans never download images and display exact image versions, total CPU/memory/disk resources, drift reasons, and per-disk actions (including the default 128 GiB `/data` disk).

### Starting and SSH configuration {#starting-and-ssh-configuration}

`barn up` verifies host capabilities and IP availability, creates new nodes, starts stopped nodes, verifies SSH readiness on running nodes, and refreshes Barn's host SSH client fragment (`~/.ssh/barn_config`) and guest `/etc/hosts` + control-node SSH entries. `recreate` performs the same full refresh; `start` and `restart` also refresh SSH aliases; per-node `destroy` removes the destroyed node's SSH entry; and whole-deployment `destroy` removes the fragment.

If a VM lifecycle action succeeds but updating `~/.ssh/config` fails (or if `~/.ssh/config` is a symlink or hard link, which Barn never edits), Barn writes `~/.ssh/barn_config`, prints the `Include` line to add manually, records the notice in `warnings[]`, and exits `0` (`barn ssh` continues to work directly).

On the control node, Barn-managed SSH entries accept replacement host keys without writing to `known_hosts`, keeping recreated lab nodes reachable while preserving any custom SSH entries you added yourself.

### Readiness {#readiness}

A Linux guest is considered ready once management SSH succeeds. Non-fatal post-boot issues are reported in `nodes[].warnings`, and completed recovery actions (such as formatting a damaged data disk) are recorded in `nodes[].repairs`; the command still exits `0`. Re-running `barn up` retries any unfinished guest setup steps on running VMs without restarting them.

Passing `--no-wait` returns as soon as the QEMU process is running, deferring SSH readiness, disk recovery, and guest `/etc/hosts` updates to the next `barn up`.

[Data disks](../configuration/#data-disks) describes which disk problems Barn repairs (reported in `repairs`) and which it only reports (in `warnings`). Existing guests receive the current recovery helper on their next `barn up` readiness check.

### Node failures {#node-failures}

When one or more nodes fail during a batch operation, Barn preserves any nodes that succeeded, exits `5`, and summarizes each failure as `N of M node(s) failed: <node> (<stage>: <error>); ...` across stages such as `prepare`, `start`, `readiness`, `bootstrap`, `guest-setup`, `stop`, and `status`. Structured output populates `failures[]` with `node`, `stage`, `error`, and optional `reason` (plus `rolled_back` when `--rollback` cleaned up uncommitted node preparation files). For `readiness` or `bootstrap` failures, check `barn logs <node>` and see [A node did not become ready](../../start/troubleshooting/#a-node-did-not-become-ready).

### Status {#status}

`barn status` reports each node's name, IP (`ADDRESS`), state (`running` means the QEMU process is alive; it does not probe guest SSH), exact image, vCPUs, and memory, flagging TCG emulation when active (and on Apple Silicon when Mac VMs exist, appends `mac: <names>; barn mac ls`). Pass `--verbose` to include forwarded SSH ports, architecture, accelerator, and QEMU PID. If a node is degraded—including when an online `resize` was interrupted after hotplugging (`stage: "resize"`, `reason: "resize_incomplete"`)—`status` still lists its healthy peers, populates `failures[]`, and exits `5`.

## Recovery and interrupted operations {#recovery-and-interrupted-operations}

- **Fault isolation**: During `up` or `start`, a missing host share or failed new-node preparation affects only that node; independent stopped nodes still start, and the command exits `5` with a retry command that preserves your `-f`, `--repo`, and flag arguments.
- **Setup event log**: Host `setup` and its follow-up lifecycle run share one `operation_id`. If initial setup fails before a deployment exists, you can still inspect the bounded phase log via `barn logs --source events --json` (which records phase transitions without sensitive arguments or credentials; `setup --dry-run` writes no log).
- **Retained persistent disks**: Persistent disks left behind by a previously removed node do not block destroying the remaining nodes; use `destroy --delete-persistent` or `purge` to remove them.
- **macOS setup ordering**: On macOS, `setup` finishes Homebrew discovery/installation or the pinned `socket_vmnet` archive download before prompting for administrator privileges, so downloads neither expire an earlier `sudo` token nor prompt for a password when a download fails.
- **PID and journal reconciliation**: If a recorded QEMU PID has been reused by an unrelated process, Barn marks the node `stopped`; if a `stop` was interrupted while the VM process remained alive, Barn marks it `running`. If an online `resize` was interrupted after modifying the live guest, `status` reports `resize_incomplete`; retry `barn resize <node>` or run `barn restart <node>`. Other interrupted transitions print the recovery command (`destroy` resolves interrupted state directly), and a failed initial `up` automatically rolls back uncommitted journal artifacts on the next run.
- **Cancellation**: When a command is cancelled, Barn sends SIGTERM to the external program it is running, which `sudo` forwards to the privileged command, and waits at most 10 seconds for that process and its inherited output pipes. Descendants that ignore SIGTERM need external supervision.

## Logs and environment {#logs-and-environment}

`barn logs` reads the guest serial console (`--source serial`) by default. Pass `--source qemu` for QEMU stderr diagnostics or `--source events` for the deployment-wide bounded event log. Adding `--follow` (`-f`) streams raw bytes in text mode, NDJSON lines in `--json` mode, or YAML documents in `--yaml` mode. QEMU argv is omitted from normal log output unless `--verbose` is set.

| Environment variable | Purpose |
|---|---|
| `BARN_HOME` | Private state directory (default `~/.barn`); accepts relative paths, `~/`, and directory symlinks, but not `/` or the home root. Prefer an absolute path across working directories |
| `BARN_REPO` | Default image repository URL or path; overridden by `--mirror` and `--repo` |
| `BARN_OUTPUT` | Default output format (`text`, `json`, or `yaml`); overridden by `--json`/`--yaml` |
| `BARN_VERBOSE` | Boolean default for diagnostic output; overridden by `-v`/`--verbose` |
| `BARN_VMNET_ARCHIVE` | Path to a local pinned `socket_vmnet` archive for macOS setup; accepts relative paths, `~/`, and symlinks (SHA-256 verification still applies) |
| `NO_COLOR` | Any non-empty value disables ANSI color output |
{.wide .expand}

Explicit `--json`, `--yaml`, and `-v`/`--verbose` override `BARN_OUTPUT` and `BARN_VERBOSE`, and `--help` works even when those variables hold invalid values. Any other command exits `2` (`usage`) while an invalid value is not overridden on the command line.

## SSH passthrough and completion {#ssh-passthrough-and-completion}

```text
barn ssh [node] [-- command...]
barn exec [node] -- command...
```

> [!TIP]
> Remote commands require `--`. Pass `barn exec meta -- hostname` rather than `barn exec meta hostname`, and use `sh -c` explicitly for a shell command string.

- **`barn ssh`** without a command opens an interactive login shell; with `-- command...`, it joins the arguments after `--` with spaces and passes them to the guest shell.
- **`barn exec`** requires `-- command...` and passes the program and each argument separately, preserving spaces, quotes, empty arguments (after the first non-empty command token), and shell metacharacters literally. Wrap pipelines, redirections, variable expansion, or compound commands in `sh -c '...'`.
- Positional arguments before `--` may contain at most one known node name (defaulting to the control node when omitted). Unknown node names or extra selectors before `--` fail immediately with exit code `2` (`usage`), listing known nodes and suggesting `barn status`.
- Barn flags (`--json`, `-v`, `--help`) must appear before `--`; everything after `--` (including a second `--`, `-V`, or `-o...`) is passed to the remote command and cannot alter local OpenSSH client options.

```bash
barn ssh meta
barn ssh meta -- 'df -h /data; id'
barn exec meta -- hostname
barn exec meta -- printf '<%s>\n' 'a b' ''
barn exec meta -- sh -c 'id; df -h /data'
barn exec meta --json -- uname -a
```

Generate shell completion with `barn completion bash|zsh|fish|powershell` (for Bash, reload after upgrades via `source <(barn completion bash)`). Completion suggests commands, aliases, templates, image aliases, enumerated flags, YAML files for `-f`, and node names from the current inventory or applied state, and stops suggesting Barn flags after `--`.

## Exit codes {#exit-codes}

| Code | `error` | Meaning |
|---:|---|---|
| `0` | | Success (including ready guests with non-fatal `warnings[]` or `repairs[]`) |
| `1` | `runtime` | Operation executed and failed (external tool, download, or guest failure) |
| `2` | `usage` | Invalid CLI syntax, missing inventory file, or invalid configuration/image selector |
| `3` | `capability` | Host lacks a required dependency, active Barn network, or privilege |
| `4` | `conflict` | Operation conflicts with current deployment state or another active `barn` process |
| `5` | `partial` | Node-level batch failure; inspect `failures[]` (successful peer nodes remain intact) |
| `6` | `resource` | Host IP address, port, subnet, or disk path is already in use |
| `7` | `integrity` | Digest, catalog signature or signed revision, instance identity, or file ownership verification failed |
| `130` | `cancelled` | Interrupted by `SIGINT`/`SIGTERM` or interactive confirmation declined |
{.wide .expand}

An image catalog whose signature is missing or does not verify fails with `reason: "catalog_signature"`, and a catalog that reuses an accepted or embedded revision number with different bytes fails with `reason: "catalog_equivocation"`. Permission and I/O errors while reading a cached catalog signature are runtime failures (exit `1`).

When another `barn` process holds the deployment lock, mutating commands wait up to 10 minutes while reporting the lock holder, then exit `4` with `reason: "deployment_busy"` on timeout. Read-only and access commands (`status`, `ssh`, `exec`, `ssh-config`, `hosts`) do not wait on the lock; `status` displays the last committed state and notes the active operation in `note`.

`ssh` and `exec` return the remote command's exit code verbatim (including `255`, which can indicate either an OpenSSH transport failure or a remote command exiting `255`), keeping text output, JSON `exit_code`, and process exit status identical.
