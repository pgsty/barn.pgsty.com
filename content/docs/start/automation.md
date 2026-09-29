---
title: Automation and Guest Scripts
linkTitle: Automation
description: Prepare an unattended lab, check JSON results, and run repeatable scripts inside selected guests.
weight: 35
icon: fa-solid fa-terminal
---

These examples target the **Barn 0.9.0 release candidate**. Run host commands as the Unix user who owns the deployment.
Use the same inventory and `BARN_HOME` on every invocation; a new working
directory does not create an independent lab.

## Prepare a predictable lab

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

Keep the selected inventory in version control. Set `vm_image` explicitly;
use a version such as `vm_image: u24@20260911.0.0` when new nodes must use the
same base after a Catalog update. Explicit `-f` also prevents first-run setup
from automatically moving an untouched default template to another subnet.

After reviewing the host plan, prepare the machine once:

```bash
barn setup -f barn.yml --yes
barn up -f barn.yml --json > up.json
```

`--yes` accepts the setup plan; it does not grant sudo credentials. An
unattended runner must already have the required host dependencies, network,
and privilege policy. Noninteractive `up` does not perform the interactive
first-run host preparation. `up` has no `--yes` flag.

For a custom repository, use the same `--repo` value for setup and up, and
explicitly activate its Catalog with `barn update --repo URL` before
planning. See [Image Repositories](../images/).

## Check more than the exit code

Barn writes structured results to stdout and diagnostics to stderr. Preserve
both outputs and the command's exit code; a later shell command must not
overwrite the status you intend to inspect. This Bash example also uses `jq`:

```bash
if barn up -f barn.yml --json > up.json 2> up.stderr; then
  jq -e '
    (.nodes | type == "array" and length > 0) and
    all(.nodes[];
      .state == "running" and .ready == true and
      ((.warnings // []) | length == 0) and
      ((.repairs // []) | length == 0)) and
    ((.warnings // []) | length == 0)
  ' up.json
else
  barn_exit=$?
  cat up.stderr >&2
  cat up.json
  exit "$barn_exit"
fi
```

The `jq` check deliberately asks for every returned node to be ready without
limitations or reported repairs. A usable guest with a failed optional disk,
share, or peer-SSH step can return **exit 0** and list `nodes[].warnings`.
`nodes[].repairs` can report a filesystem reset that discarded test data.
Choose the acceptance policy your workload needs instead of silently ignoring
these fields. Top-level warnings can describe optional SSH integration or
metadata-refresh failures. A failed `jq -e` returns nonzero to the caller.

Do not use `--no-wait` when the next step requires guest readiness. A
`status --json` snapshot reports VM state and cached warnings; it is not a new
guest readiness test. Run `up` to complete setup, then run an application check
inside the guest when your workflow depends on a service.

### Failures and version boundaries

Use [CLI exit codes](../../reference/cli/#exit-codes) together with the payload
for the command you ran. Partial operations can retain successful nodes;
inspect `nodes` and/or `failures` when present before retrying.

The **0.9 candidate** moves some failures to different classes. For example,
a missing first inventory is usage/2 and an unknown image is usage/2;
`recreate_required` and `nodes_removed` are `reason` values under conflict/4.
It also uses bounded lock waiting and `deployment_busy` on timeout.

Not every failing command returns the generic `error`/`message` envelope:
doctor, network status, provision, and SSH execution can return their own
reports. `ssh`/`exec` pass through the remote exit status, including 255 from
OpenSSH. In structured execution output, inspect `success`, `exit_code`,
`stdout`, and `stderr`; do not interpret a remote status as a Barn class.

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

With no selectors, `provision` targets all committed nodes; they must be
running. It does not create or start VMs. The local script must be a nonempty,
regular, non-symlink file of at most 4 MiB. Barn streams one verified snapshot
to guest Bash, records its SHA-256, and does not save the script as a guest file.
The script need not be executable on the host.

Execution is serial by default, with `--parallel` from 1 to 4. `--timeout`
defaults to one hour, applies to the whole operation, and cannot exceed 24 hours.
`--sudo` runs through guest `sudo -n`, so it cannot prompt for a password.
Results contain `results[]`, per-node stdout/stderr and exit codes, and
`successful`/`failed` counts. A partial run can leave successful changes in
place. Write scripts so that running them again is safe; Barn does not roll
back guest commands or automatically rerun them on the next `up`.

A provision run with successful and failed targets exits 5. With one failing
target, a positive remote status other than 255 is passed through. Other
all-failed runs exit 1; inspect `results[].exit_code` for the guest/SSH details.

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

Barn prepares the guest administrator and control-node SSH access. Deploy
services through Pigsty after checking the inventory and guest connectivity.
The [validation record](../../about/status/) distinguishes Ansible connectivity
checks from a complete Pigsty installation. For host-side file transfer or
port tunneling, see [Storage and Access](../storage/).
