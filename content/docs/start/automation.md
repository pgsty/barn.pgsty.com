---
title: Automation and Guest Scripts
linkTitle: Automation
description: Prepare an unattended lab, check JSON results, and run repeatable scripts inside selected guests.
weight: 60
icon: fa-solid fa-terminal
---

These examples target **Barn 0.9.1**. Run host commands as the Unix user who owns the deployment.
Use the same inventory and `BARN_HOME` for every invocation. A new working directory does not create an independent lab.

## Prepare a predictable lab

For a custom repository, use the same `--repo` value for setup and up. Before planning, explicitly activate its image catalog with `barn update --repo URL`. See [Image Repositories](../images/).

For a first lab, create and review the inventory before starting automation:

```bash
mkdir -p ~/barn-lab
cd ~/barn-lab
barn init dual
# Edit barn.yml before proceeding.
barn version
barn validate -f barn.yml
barn plan -f barn.yml
barn setup -f barn.yml --dry-run
```

Keep the selected inventory in version control. Set `vm_image` explicitly. If new nodes must use the same base image after a catalog update, specify a version such as `vm_image: u24@20260926.0.0`. Explicit `-f` also prevents first-run setup
from automatically moving an untouched default template to another subnet.

After reviewing the host plan, prepare the host once:

```bash
barn setup -f barn.yml --yes
barn up -f barn.yml --json > up.json
```

`--yes` accepts the setup plan but does not supply sudo credentials.
Before unattended `up`, the host must have the required dependencies, network, and privilege policy.
Noninteractive `up` skips first-run host preparation and has no `--yes` flag.

## Check more than the exit code

Barn writes structured results to stdout and diagnostics to stderr. Preserve both outputs and the command's exit code. Do not let a later shell command overwrite the status you intend to inspect. This Bash example also uses `jq`:

```bash
#!/usr/bin/env bash
set -euo pipefail

if barn up -f barn.yml --json > up.json 2> up.stderr; then
  jq -e '
    (.nodes | type == "array" and length > 0) and
    all(.nodes[];
      .state == "running" and .ready == true and
      ((.warnings // []) | length == 0) and
      ((.repairs // []) | length == 0)) and
    ((.warnings // []) | length == 0)
  ' up.json || exit 1
else
  barn_exit=$?
  cat up.stderr >&2
  cat up.json
  exit "$barn_exit"
fi
```

The example uses a strict acceptance policy: `jq` requires every returned node to be ready, without limitations or reported repairs. If a guest is usable but an optional disk, share, or peer-SSH step fails, Barn can return **exit 0**. It lists `nodes[].warnings`.
`nodes[].repairs` can report a filesystem reset that discarded test data.
Check these fields against the acceptance policy for your workload. Top-level warnings can describe optional SSH integration or
metadata-refresh failures. The explicit `|| exit 1` stops the script when the
acceptance check fails, even if later commands are added.

Do not use `--no-wait` when the next step requires guest readiness. A `status --json` snapshot reports VM state and cached warnings. It does not test guest readiness again. Run `up` to complete setup. If your workflow depends on a service, run an application check inside the guest.

### Failures and version boundaries

Use [CLI exit codes](../../reference/cli/#exit-codes) together with the payload
for the command you ran. Partial operations can retain successful nodes. Before retrying, inspect `nodes` and/or `failures` when present.

Barn 0.9.1 uses explicit failure classes. For example,
a missing first inventory is usage/2 and an unknown image is usage/2;
`recreate_required` and `nodes_removed` are `reason` values under conflict/4.
It also uses bounded lock waiting and `deployment_busy` on timeout.

Not every failing command returns the generic `error`/`message` structure.
Doctor, network status, provision, and SSH execution can return their own reports.

For example, `doctor` can exit 0 while a network-class check is blocked.
Before relying on host networking, inspect `checks[]` and `barn network status --json`.

`ssh`/`exec` return the remote exit status, including 255 from OpenSSH.
Inspect `success`, `exit_code`, `stdout`, and `stderr` in structured execution results; a remote status is not a Barn error class.

## Run one command or a script

Use an explicit node and `--` to separate it from the remote command:

```bash
barn exec meta -- hostname
barn exec node-1 -- sh -c 'id; df -h /data'
barn exec meta --json -- uname -a > uname.json
```

For multiple guests, save a local Bash script as `check-lab.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
hostname
id
findmnt /data
test -d /data
```

Then run it on selected nodes:

```bash
barn provision --script ./check-lab.sh meta node-1
barn provision --script ./check-lab.sh --parallel 2 --timeout 5m --json > provision.json
```

With no selectors, `provision` targets all nodes recorded in the deployment.
They must already be running; this command does not create or start VMs.

The local script must be a nonempty regular file, not a symlink, and at most 4 MiB.
It does not need to be executable on the host.
Barn sends the same verified script contents to Bash on each guest and records the script's SHA-256, without saving a guest script file.

Execution is serial by default, with `--parallel` from 1 to 4. `--timeout` applies to the whole operation. It defaults to one hour and cannot exceed 24 hours.
`--sudo` runs through guest `sudo -n`, so it cannot prompt for a password.
Results contain `results[]`, per-node stdout/stderr and exit codes, and
`successful`/`failed` counts. A partial run can leave successful changes in
place. Write scripts that are safe to run again. Barn does not roll back guest commands or automatically rerun them on the next `up`.

Each node captures at most 1 MiB of stdout and 1 MiB of stderr. Before treating captured output as complete, check `stdout_truncated` and `stderr_truncated`. The operation holds the deployment lock while scripts execute, so
lifecycle changes wait. An `audit_error` means the final audit record or lock release failed after execution. Exit 1 does not imply the script made no changes.

A provision run with successful and failed targets exits 5. If the run has only one target and it fails, a positive remote status other than 255 is passed through. Other all-failed runs exit 1. Inspect `results[].exit_code` for the guest/SSH details.

## Use the lab with Pigsty

Barn and Pigsty can read the same `pigsty.yml`, but `barn init dual` only
creates VM topology. It does not configure a PostgreSQL cluster. Start with
the service inventory appropriate to your Pigsty checkout and review it:

```bash
barn validate -f pigsty.yml
barn plan -f pigsty.yml
barn up -f pigsty.yml
barn ssh
```

Barn prepares the guest administrator and copies the deployment private key into the control node selected by `admin_ip`.
The control node uses this key to connect to the other nodes.
The generated control-node SSH fragment disables peer host-key checking; the
host-to-guest management connection uses separate instance-scoped host-key trust.
See [Security boundaries](../../about/security/) for the access model. Deploy
services through Pigsty after checking the inventory and guest connectivity.
Follow [Pigsty documentation](https://pigsty.io/docs/) for service installation.
For host-side file transfer or port tunneling, see [Storage and Access](../storage/).
