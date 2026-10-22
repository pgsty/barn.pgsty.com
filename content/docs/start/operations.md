---
title: Daily Operations
description: "The normal lifecycle for the one deployment: inspect, access, scale, change, stop, and destroy."
weight: 30
icon: fa-solid fa-gears
aliases: [/docs/start/lifecycle/, /docs/start/provisioning/]
---

This guide covers Linux labs in **Barn 0.9.1**. For Mac VMs, use the [macOS guide](../macos/#everyday-lifecycle).

## Inspect and access

```bash
barn status
barn ssh meta
barn exec node-1 -- hostname
barn logs meta --source serial
```

Barn records the existing deployment under `~/.barn` by default; `BARN_HOME` overrides this location.
The commands above use that applied state and work from any directory. Changing directories does not create another deployment.

Status shows images and resources. `--verbose` adds architecture, accelerator, SSH ports, and PID.
Ordinary output identifies TCG, and an abnormal node does not hide the other nodes' status.
After starting the selected VMs, `barn up` rebuilds SSH aliases from the complete applied deployment.
A scoped `up` retains unselected nodes' aliases, so connections such as `ssh meta` continue to work.
To rewrite the aliases manually, use `barn ssh-config --install`.

`plan`, `up`, `reload`, and `recreate` first use an explicit `-f`, then search for an inventory in the current directory.
If discovery finds no file, they use the applied specification. `validate` always needs a file.
The search order is `barn.yml`, `barn.yaml`, `pigsty.yml`, then `pigsty.yaml`; Barn does not search parent directories.
If the first existing file is malformed, the command fails without trying another file or applied state.
Use `-f pigsty.yml` when both Barn and Pigsty files exist.

Repeat `up` to retry unfinished guest setup and refresh older guest helpers
without restarting healthy VMs. The result lists optional limitations. JSON/YAML expose `nodes[].warnings` and `nodes[].repairs`. Barn may reset unrecognized or confirmed damaged test data filesystems, including persistent disks. See [Data disks](../../reference/configuration/#data-disks).

## Stop and start

```bash
barn stop
barn start
barn restart node-1
barn reload -f barn.yml       # read/check config, stop, then converge
```

`start` powers on stopped VMs and re-checks readiness of running ones. Both
`start` and `restart` use applied state and refresh SSH aliases, including any
reassigned automatic ports. Before stopping selected nodes, `reload` reads the inventory and checks drift and startup dependencies. It then runs the full `up` workflow.

Starting commands also refresh Barn hosts and control-node SSH entries in
running guests. `--no-wait` skips readiness, guest recovery, and this refresh. Run `up` later to complete these steps.

## Change the deployment

```bash
barn plan
barn up                         # create/start selected nodes and install SSH aliases
barn recreate node-1            # applies a changed VM definition
```

On a terminal, `recreate` and `destroy` ask you to type the confirmation word. `--force` skips that prompt. Without a terminal, this flag is required.

Before host setup, `plan` can show image catalog selections, total resources, change reasons, and disk effects.
Planning an imported `local-*` image also validates its cache and requires `qemu-img`.

CPU and memory changes require recreate, which replaces root and non-persistent data disks and retains compatible persistent disks.
If changes to unselected nodes block the requested recreate, Barn refuses before deletion and identifies the affected nodes.

Inventory changes appear in these fields:

| Field | Meaning | Action |
|---|---|---|
| `create` | desired node has no state | `barn up` |
| `recreate` | VM definition changed | `barn recreate <node>` |
| `missing` | stateful node left the file | restore it, or destroy it explicitly |

Deleting YAML never deletes a VM. Changes to Pigsty fields that Barn does not use produce `action:none`. Barn uses native naming and node-admin fields even though they do not begin with `vm_`. Successful recreate refreshes the complete SSH
fragment as well.

## Concurrent commands

Commands that modify the deployment, including `provision`, wait up to ten minutes for another Barn operation. The command's own deadline can shorten this wait. The waiting message identifies
the command, PID, and start time. A lock timeout returns exit 4, JSON `error: conflict`, and `reason: deployment_busy`. After the lock holder finishes, retry the command.
The lock is released automatically when the holding process exits. Do not
delete a lock file to interrupt a live operation.

`status`, `ssh`, `exec`, `ssh-config`, and the deployment-state read for `hosts`
do not queue behind this lock. They use the published state. If another command holds the deployment lock, `status` adds a `note`. It does not reconcile that command's transitions. A VM still starting may therefore be unavailable to SSH.

See [Troubleshooting](../troubleshooting/#a-command-was-killed) for interrupted
operations and [Automation](../automation/) for scriptable results.

## Destroy

Choose the command for the scope you want to delete. These are alternatives, not a sequence to run in full:

```bash
barn destroy node-3
barn destroy
barn destroy --delete-persistent
barn destroy --purge
barn purge                         # discard everything without confirmation
```

`--delete-persistent` and `--purge` are valid only for whole-deployment
destroy, not with node selectors. `--purge` removes persistent disks, keys, and deployment state. Images remain cached. Node destroy refreshes the SSH
fragment for remaining peers, while whole destroy removes the default Barn
SSH integration. Host network removal is separate and refuses while a VM is attached.

`barn purge` deletes the disposable lab without confirmation. For an existing deployment, it is equivalent to `destroy --force --purge`. It accepts no node selectors. If no deployment exists, it still succeeds and can remove owned retained disks. It keeps the image cache and host
network, and it does not bypass process, ownership, or path-integrity checks.

Plain `destroy` succeeds when no deployment exists. If deployment state is gone but owned persistent disks remain, use `purge`. `destroy --delete-persistent` or `destroy --purge` points to that command. The old `rm` alias has been removed. Spell out `purge`.

```bash
barn network uninstall --yes
```

See [Image Repositories](../images/) for image selection, mirrors, and cache
pruning, or [Uninstall and Clean Up](../uninstall/) to remove host state.
