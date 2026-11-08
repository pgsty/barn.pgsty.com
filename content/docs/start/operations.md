---
title: Daily Operations
description: "The normal lifecycle for the one deployment: inspect, access, scale, change, stop, and destroy."
weight: 30
icon: fa-solid fa-sliders
aliases: [/docs/start/lifecycle/, /docs/start/provisioning/]
---

This guide covers day-to-day Linux lab management. For macOS guests, see the [macOS VM guide](../macos/#everyday-lifecycle).

## Inspect and access

```bash
barn status
barn ssh meta
barn exec node-1 -- hostname
barn logs meta --source serial
```

These commands read the active deployment under `BARN_HOME` (default `~/.barn`) and work from any directory when that path points to the same location. If you set `BARN_HOME` yourself, use an absolute path across working directories. `barn status` lists each node's image and resource allocation (including any software-emulated `tcg` notice), while `barn status --verbose` adds guest architecture, accelerator, loopback SSH port, and QEMU PID.

When you run `barn up` (including on a subset of nodes), Barn refreshes the `~/.ssh/barn_config` aliases for the entire applied deployment so `ssh meta` and peer aliases stay current. You can also regenerate those aliases at any time with `barn ssh-config --install`.

Commands that reconcile configuration—`plan`, `up`, `reload`, `resize`, and `recreate`—locate the inventory in this order:

1. An explicit `-f /path/to/inventory.yml` flag (required when both `barn.yml` and `pigsty.yml` exist in the same directory and you want `pigsty.yml`).
2. The first matching file in the current working directory (`barn.yml`, `barn.yaml`, `pigsty.yml`, then `pigsty.yaml`; parent directories are never searched).
3. The previously applied deployment specification in `BARN_HOME` (except `barn validate`, which always requires a file).

Re-running `barn up` retries any unfinished guest setup stages and updates guest helper scripts in place without restarting healthy VMs. Any remaining guest limitations or automatic test-disk repairs are surfaced in the terminal summary and under `nodes[].warnings` / `nodes[].repairs` in JSON/YAML output (see [Data disks](../../reference/configuration/#data-disks)).

## Stop and start

```bash
barn stop
barn start
barn restart node-1
barn reload -f barn.yml       # validate inventory, stop selected nodes, and run up
```

`barn start` boots stopped VMs, re-verifies running ones, and updates SSH aliases if any automatic loopback port was reassigned. `barn reload` validates the inventory and startup dependencies before stopping selected nodes, then runs `barn up` for that selection.

`reload` is a controlled stop-and-boot cycle. It can add new nodes and start
stopped nodes, but it refuses existing-node changes to CPU, memory, image,
disks, shares, addresses, or other VM definition before stopping anything.

For CPU or memory changes, edit `vm_cpu` or `vm_mem` and use `barn resize`.
Supported increases may be hot-plugged; decreases and unsupported backends use
a stop/start fallback while preserving the VM identity and disks. `resize`
does not apply image, disk, network, or share changes; use `recreate` for those.

Passing `--no-wait` to a start command returns as soon as QEMU starts, skipping readiness checks, guest recovery, and `/etc/hosts` or control-node SSH updates until your next `barn up`.

## Change the deployment

```bash
barn plan
barn up                         # create/start selected nodes and refresh SSH aliases
barn resize node-1              # apply vm_cpu/vm_mem changes without recreation
barn recreate node-1            # rebuild a node whose VM specification changed
```

`barn plan` compares your inventory against the applied state and reports image selections, aggregate resources, drift reasons, and disk impact:

| Detected change | Meaning | How to apply |
|---|---|---|
| `create` | Node is in the inventory but not yet provisioned | `barn up` |
| `resize` | Node CPU or memory changed | `barn resize <node>` |
| `recreate` | Node image, disk, share, or other VM specification changed | `barn recreate <node>` |
| `missing` | Provisioned node was removed from the inventory YAML | Restore the YAML entry, or run `barn destroy <node>` |
{.wide .expand}

In JSON output, `start`, `create`, `resize`, `recreate`, and `missing` are node lists. The top-level `action` summarizes the plan as one of `create`, `start`, `converge`, `resize`, `recreate`, `blocked-removal`, `repair`, or `none`; `blocked`, when present, is an explanation string.

Editing or deleting YAML entries never destroys a VM automatically, and changes to service-level Pigsty variables that Barn does not consume report `action: none`. When a node requires `recreate`, Barn replaces its root overlay and non-persistent data disks while preserving compatible persistent disks. Interactive `recreate` and `destroy` prompt you to type the command name to confirm; pass `--yes` (or `--force`) in non-interactive scripts.

`recreate` is the explicit replacement path. Barn validates the new image,
network, shares, and persistent-disk attachment contract first, then destroys
the selected VM artifacts and boots a fresh VM from the desired inventory.
Root and non-persistent data disks are replaced; compatible persistent disks
remain attached. The replacement gets a new VM identity and refreshes SSH
host-key state.

Without node names, `recreate` replaces every node in the deployment and lists
them in the confirmation. It refuses an inventory that no longer lists an
existing node before any VM stops (exit `4`, `reason: nodes_removed`): remove
that node explicitly with `barn destroy <node>` or add it back to the
inventory. Barn checks the scope again under the destruction lock and reports
`deployment_changed` if the applied state changed during preflight.

### Apply changes to selected nodes {#selected-nodes}

You can edit several nodes in the inventory and apply them in batches:

```bash
barn plan node-1 -f barn.yml
barn recreate node-1 -f barn.yml
barn plan node-2 -f barn.yml
```

`plan`, `up`, `reload`, `recreate`, and `resize` with explicit selectors retain every unselected peer's applied definition, including peers changed or temporarily omitted in YAML. Images for uncreated, unselected nodes are resolved when you select those nodes. The entire inventory must still parse correctly, and selected changes must not conflict with applied addresses, aliases, control-node roles, or deployment-wide settings.

Without selectors, Barn evaluates the whole inventory: CPU and memory changes use `resize`, other changed existing VMs require `recreate`, and missing VMs require restoring their definitions or explicitly destroying them.

## Concurrent commands

Mutating commands (`up`, `start`, `stop`, `restart`, `reload`, `resize`, `recreate`, `destroy`, `purge`, and `provision`) acquire the deployment lock in `BARN_HOME`, waiting up to 10 minutes (or the command's `--timeout`) if another operation is in flight. While waiting, Barn prints the lock holder's command, PID, and start time; if the wait times out, it exits with code `4` (`error: conflict`, `reason: deployment_busy`). The lock releases automatically when the holding process exits—never delete lock files manually.

Read-only and access commands (`status`, `ssh`, `exec`, `ssh-config`, and the state read in `hosts`) read the last published state without waiting on the lock. If a mutating command is currently running, `barn status` includes a `note` indicating the active operation. See [Troubleshooting](../troubleshooting/#a-command-was-killed) for interrupted runs.

## Destroy

Pick the teardown command that matches the scope you want to remove:

```bash {tab="Single node" group="destroy-scope" value="node"}
barn destroy node-3
```

```bash {tab="Keep persistent disks" group="destroy-scope" value="lab"}
barn destroy
```

```bash {tab="Delete persistent disks" group="destroy-scope" value="persistent"}
barn destroy --delete-persistent
```

```bash {tab="Purge lab & keys" group="destroy-scope" value="purge"}
barn purge
```

- `barn destroy <node>` deletes only the named node and refreshes SSH aliases for the remaining nodes. If it removes the control node, the first remaining node becomes the control node, so `ssh-config`, `hosts`, `exec`, and `provision` keep working; set `admin_ip` in the inventory to that node's address (and remove the destroyed entry unless you want `up` to create it again), then run `barn up` to install its control SSH access.
- `barn destroy` removes all VMs along with their root overlays and non-persistent data disks, the deployment state, and the SSH aliases Barn installed, while retaining persistent disks, deployment keys, cached images, and host networking. Run `barn up` again to build a fresh lab from the inventory.
- `barn destroy --delete-persistent` and `barn destroy --purge` apply to the entire deployment (they cannot be combined with node names). `--purge` also removes persistent disks, SSH keys, and deployment state.
- On `main`, `barn purge` immediately removes the entire Linux lab, verified retained persistent disks, keys, and deployment state; the image cache and host network remain. To review the node list and deletion scope first, use `barn purge --ask`: `y`/`yes` confirms; `n`/`no`, an empty line, or EOF cancels. It accepts no `--yes`, `-y`, or `--force`. This change is unreleased; 1.0.0 still asks terminal users to type `purge`.

To remove the shared Linux host network after all VMs are gone:

```bash
barn network uninstall --yes
```

See [Image Repositories](../images/) for image cache management, or [Uninstall and Clean Up](../uninstall/) for a full host teardown.
