---
title: Daily Operations
description: "The normal lifecycle for the one deployment: inspect, access, scale, change, stop, and destroy."
weight: 20
icon: fa-solid fa-gears
aliases: [/docs/start/lifecycle/, /docs/start/provisioning/]
---

This guide describes the **Barn 0.9.0 release candidate**. See
[Status](../../about/status/) for the publication and validation boundary.

## Inspect and access

```bash
barn status
barn ssh meta
barn exec node-1 -- hostname
barn logs meta --source serial
```

Applied state is under `~/.barn` by default (`BARN_HOME` overrides it); these
commands work from any directory. Changing the working directory does not create
a separate deployment.
Status shows images and resources; `--verbose` adds architecture, accelerator,
SSH ports, and PID. TCG is marked in ordinary output, and a degraded node does
not hide its peers.
`barn up` rebuilds the default SSH aliases from the complete applied
deployment after the selected VMs are started, so a scoped `up` never drops
unselected peers and plain `ssh meta` just works; `barn ssh-config --install`
rewrites it by hand if you ever need to.
`plan`, `up`, `reload`, and `recreate` prefer `-f`, then a discovered
Inventory, then the applied spec when no file exists. `validate` always needs
a file.

Repeat `up` to retry unfinished guest setup and refresh older guest helpers
without restarting healthy VMs. Optional limitations appear in the result;
JSON/YAML expose `nodes[].warnings` and `nodes[].repairs`. Unusable test data
filesystems may be reset, including persistent disks; see
[Data disks](../../reference/configuration/#data-disks).

## Stop and start

```bash
barn stop
barn start
barn restart node-1
barn reload -f barn.yml       # read/check config, stop, then converge
```

`start` powers on stopped VMs and re-checks readiness of running ones. Both
`start` and `restart` use applied state and refresh SSH aliases, including any
reassigned automatic ports. `reload` reads the Inventory and checks drift and startup dependencies before
stopping selected nodes and following the full `up` path.

Starting commands also refresh Barn hosts and control-node SSH entries in
running guests. `--no-wait` skips readiness, guest recovery, and this refresh; run `up` later
to finish them.

## Change the deployment

```bash
barn plan
barn up                         # create/start selected nodes and install SSH aliases
barn recreate node-1            # applies a changed VM definition
```

`recreate` and `destroy` ask you to type the confirmation word on a terminal;
`--force` skips that prompt and is required without a terminal.

`plan` can inspect Catalog-backed images before host setup and shows images,
total resources, change reasons, and disk effects. Planning an imported
`local-*` image also validates its cache and requires `qemu-img`. CPU/memory changes still require recreate: root and ephemeral
data disks are replaced, while persistent disks are kept. A selected recreate
blocked by unselected peer changes refuses before deletion and names the nodes
that need attention.

Inventory changes appear in these fields:

| Field | Meaning | Action |
|---|---|---|
| `create` | desired node has no state | `barn up` |
| `recreate` | VM definition changed | `barn recreate <node>` |
| `missing` | stateful node left the file | restore it, or destroy it explicitly |

Deleting YAML never deletes a VM. Unconsumed Pigsty changes produce
`action:none`; native naming and node-admin fields are consumed even though
they do not begin with `vm_`. Successful recreate refreshes the complete SSH
fragment as well.

## Concurrent commands (0.9 candidate)

Deployment mutations wait behind another Barn operation for up to ten
minutes, bounded by the command's own deadline. The waiting message identifies
the command, PID, and start time. A lock timeout returns exit 4, JSON
`error: conflict`, and `reason: deployment_busy`; retry after the holder finishes.
The lock is released automatically when the holding process exits. Do not
delete a lock file to interrupt a live operation.

`status`, `ssh`, `exec`, `ssh-config`, and the deployment-state read for `hosts`
do not queue behind this lock. They use the published state; `status` adds a
`note` when another command owns the deployment and does not reconcile its
transitions. A VM still starting may therefore be unavailable to SSH.

See [Troubleshooting](../troubleshooting/#a-command-was-killed) for interrupted
operations and [Automation](../automation/) for scriptable results.

## Destroy

```bash
barn destroy node-3
barn destroy
barn destroy --delete-persistent
barn destroy --purge
barn purge                         # discard everything without confirmation
```

`--delete-persistent` and `--purge` are valid only for whole-deployment
destroy, not with node selectors. `--purge` removes persistent disks, keys,
and deployment state; images remain cached. Node destroy refreshes the SSH
fragment for remaining peers, while whole destroy removes the default Barn
SSH integration. Host network removal is separate and refuses while a VM is attached.

`barn purge` is the concise disposable-lab path. It is
equivalent to `destroy --force --purge` for an existing deployment, accepts no
node selectors, and is
idempotent when no deployment exists. It keeps the image cache and host
network, and it does not bypass process, ownership, or path-integrity checks.

**0.9 candidate:** plain `destroy` succeeds when no deployment exists. If
deployment state is gone but owned persistent disks remain, use `purge`;
`destroy --delete-persistent` or `destroy --purge` points to that command.
The old `rm` alias has been removed; spell out `purge`.

```bash
barn network uninstall --yes
```

See [Image Repositories](../images/) for image selection, mirrors, and cache
pruning, or [Uninstall and Clean Up](../uninstall/) to remove host state.
