---
title: Automation and Guest Scripts
linkTitle: Automation
description: Prepare an unattended lab, check JSON results, and run repeatable scripts inside selected guests.
weight: 60
icon: fa-solid fa-gears
---

This guide shows how to drive Barn from unattended scripts and CI pipelines. Run all commands as the Unix user who owns the deployment, and pass the same `-f <inventory>` and `BARN_HOME` across invocations.

## Prepare a predictable lab

Keep your inventory file in version control and pin `vm_image` to an exact version (such as `vm_image: u24@20261017.0.1`) so catalog updates never alter your base image mid-pipeline. Passing `-f` explicitly also prevents first-run setup from relocating an unedited default template to a different subnet. If you use a custom image repository, activate its catalog first with `barn update --repo URL` and pass the same `--repo` to `setup` and `up`.

Generate and validate the inventory before running host setup:

```bash
mkdir -p ~/barn-lab
cd ~/barn-lab
barn init dual
# Edit barn.yml to pin vm_image and node settings.
barn version
barn validate -f barn.yml
barn plan -f barn.yml
barn setup -f barn.yml --dry-run
```

Once you have reviewed the host plan and ensured non-interactive `sudo` credentials (or a `NOPASSWD` policy) are available, prepare the host and bring up the lab:

```bash
barn setup -f barn.yml --yes
barn up -f barn.yml --json > up.json
```

For a generated inventory, `barn init [template] --image <reference>` writes `all.vars.vm_image`, so every node inherits the same image. References can be catalog aliases (`el9`), channels (`u24:stable`), or version selectors (`u24@20261017.0.1`). `barn setup [template] --image <reference>` also selects an image during generation, but rejects this generation flag when using an existing inventory.

On `main`, `--image/-I` and `--arch/-A` share consistent spellings: `barn init full -I u24 -A amd64` saves both choices in a new inventory; the same flags on `validate`, `plan`, `up`, `reload`, `recreate`, and `resize` only override desired state for that invocation. For example, preview `barn plan -f barn.yml -I u24 -A arm64 --json`, then use the same overrides when applying it. Setup's `-I/-A` remain limited to template generation. These extensions are unreleased after 1.0.0; check your binary's `--help`.

Without an architecture flag, Barn uses inventory `vm_arch`, falling back to the host when unset; `-A native` overrides the inventory and follows the host. Existing VMs require `recreate` to change image or architecture. For repeatable CI, save `vm_image`, `vm_arch`, and an exact image version; see the [configuration reference](../../reference/configuration/#image-and-architecture).

`barn setup --yes` accepts the host-preparation plan without asking. On a terminal, `up`, `start`, `restart`, and `reload` show the same plan and ask once before installing packages or the Barn network; without a terminal they only report what is missing, so run `barn setup --yes` before them.

## Validate JSON output alongside the exit code

Barn writes structured JSON/YAML payloads to `stdout` and human diagnostics to `stderr`. Because `barn up` returns **exit code `0`** when management SSH is ready—even if an optional stage such as a secondary data disk, Virtio-9p share, or peer SSH config reported a limitation (`nodes[].warnings`) or reformatted a damaged test disk (`nodes[].repairs`)—automation scripts should inspect the JSON payload alongside the exit code:

```bash {title="up-check.sh"}
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

When a subsequent pipeline step requires ready guests, omit `--no-wait` on `barn up` (`barn status --json` reads cached state without re-probing guest SSH).

### Exit codes and command-specific payloads

Pair [CLI exit codes](../../reference/cli/#exit-codes) with each command's JSON schema:

- **Exit `2` (`usage`)**: Missing inventory on first run, invalid flags, unknown image aliases, or `destroy`/`recreate` without `--yes` when stdin is not a terminal (`purge` runs without asking).
- **Exit `4` (`conflict`)**: Inventory drift requiring explicit action (`reason: recreate_required` or `nodes_removed`), applied state that changed during a `recreate` preflight (`reason: deployment_changed`), or a deployment lock timeout (`reason: deployment_busy` after waiting up to 10 minutes).
- **Exit `5` (`partial`)**: Multi-node `up` or `provision` where some nodes succeeded and others failed—inspect `nodes[]` or `results[]` before retrying.
- **Exit `7` (`integrity`)**: A digest, signature, or identity check failed, including a catalog signature or signed revision that does not verify (`reason: catalog_signature` or `catalog_equivocation`).
- **Command-specific reports**:
  - `barn doctor --json` exits `0` when host compute passes even if a `class: network` check reports an error; check `checks[]` and `barn network status --json` before relying on the private bridge.
  - `barn ssh` and `barn exec` return the remote command's exit status (or `255` on OpenSSH transport failure) and record `success`, `exit_code`, `stdout`, and `stderr` in `--json` mode.
  - `network` and `hosts` `install`/`uninstall` without `--yes` only print the plan and exit `0` when stdin is not a terminal or the output is `--json`/`--yaml`; check `applied` in the result, or pass `--yes`.

## Run single commands or batch scripts

Always place `--` between the node selector and the remote command, and put Barn flags (`--json`, `--verbose`) before `--`:

```bash
barn exec meta -- hostname
barn exec node-1 -- sh -c 'id; df -h /data'
barn exec meta --json -- uname -a > uname.json
```

Pass the program and its arguments as separate tokens to `barn exec`, using `sh -c` explicitly for pipes, redirection, or shell variables (see [SSH passthrough and completion](../../reference/cli/#ssh-passthrough-and-completion)).

To run a health check or setup script across multiple running Linux nodes, save a local Bash script (a regular file or symlink to one, up to 4 MiB):

```bash {title="check-lab.sh"}
#!/usr/bin/env bash
set -euo pipefail
hostname
id
findmnt /data
test -d /data
```

Execute it with `barn provision`:

```bash
barn provision --script ./check-lab.sh meta node-1
barn provision --script ./check-lab.sh --parallel 2 --timeout 5m --json > provision.json
```

Omitting node selectors runs the script on every node in the deployment (all target nodes must already be running). Barn streams the verified script bytes directly to Bash over SSH without writing a temporary script file in the guest, and records the script's SHA-256 in the audit result.

- **Concurrency and timeouts**: Serial by default; `--parallel` accepts positive integers, with workers capped at the selected node count. `--timeout` bounds the whole operation, defaults to `1h`, and accepts any positive duration. `--sudo` uses non-interactive `sudo -n`.
- **Output capture and idempotency**: Each node captures up to 1 MiB of `stdout` and 1 MiB of `stderr` (setting `stdout_truncated` / `stderr_truncated` when exceeded). Because partial runs leave completed guest changes in place, write idempotent scripts that are safe to re-run.
- **Exit codes**: `provision` exits `5` when some nodes succeed and others fail, passes through a single target's positive non-`255` exit code on failure, and exits `1` otherwise.

## Pair the lab with Pigsty

Barn and [Pigsty](https://pigsty.io/docs/) share the same Ansible YAML format. While `barn init` generates VM hardware topology, Pigsty provides complete service inventories (`pigsty.yml`) for PostgreSQL, Redis, and monitoring stacks. Provision the VMs with Barn first:

```bash
barn validate -f pigsty.yml
barn plan -f pigsty.yml
barn up -f pigsty.yml
barn ssh
```

During `barn up`, Barn provisions the guest administrator account and installs the deployment private key on the control node designated by `admin_ip`, configuring its `~/.ssh/config` so Ansible can reach all peer nodes over their fixed private IPs (see [Security and Trust](../../about/security/)). Once `barn up` completes, SSH into the control node and run Pigsty's deployment playbooks.
