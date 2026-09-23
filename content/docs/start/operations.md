---
title: Daily Operations
description: "The normal lifecycle for the one deployment: inspect, access, scale, change, stop, and destroy."
weight: 20
icon: fa-solid fa-gears
aliases: [/docs/start/lifecycle/, /docs/start/provisioning/]
---

## Inspect and access

```bash
farrow status
farrow ssh meta
farrow exec node-1 -- hostname
farrow logs meta --source serial
```

Applied state is under `~/.farrow`; these commands work from any directory.
Status shows images and resources; `--verbose` adds architecture, accelerator,
SSH ports, and PID. TCG is marked in ordinary output, and a degraded node does
not hide its peers.
`farrow up` rebuilds the default SSH aliases from the complete applied
deployment after the selected VMs are started, so a scoped `up` never drops
unselected peers and plain `ssh meta` just works; `farrow ssh-config --install`
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
farrow stop
farrow start
farrow restart node-1
farrow reload -f farrow.yml       # stop, re-read config, converge
```

`start` powers on stopped VMs and re-checks readiness of running ones. Both
`start` and `restart` use applied state and refresh SSH aliases, including any
reassigned automatic ports. `reload` reads the Inventory and checks drift and startup dependencies before
stopping selected nodes and following the full `up` path.

Starting commands also refresh Farrow hosts and control-node SSH entries in
running guests. `--no-wait` skips readiness, guest recovery, and this refresh; run `up` later
to finish them.

## Change the deployment

```bash
farrow plan
farrow up                         # create/start selected nodes and install SSH aliases
farrow recreate node-1            # applies a changed VM definition
```

`recreate` and `destroy` ask you to type the confirmation word on a terminal;
pass `--force` only in scripts.

`plan` works before host setup and shows images, total resources, change reasons,
and disk effects. CPU/memory changes still require recreate: root and ephemeral
data disks are replaced, while persistent disks are kept. A selected recreate
blocked by unselected peer changes refuses before deletion and names the nodes
that need attention.

Inventory changes appear in these fields:

| Field | Meaning | Action |
|---|---|---|
| `create` | desired node has no state | `farrow up` |
| `recreate` | VM definition changed | `farrow recreate <node>` |
| `missing` | stateful node left the file | restore it, or destroy it explicitly |

Deleting YAML never deletes a VM. Unconsumed Pigsty changes produce
`action:none`; native naming and node-admin fields are consumed even though
they do not begin with `vm_`. Successful recreate refreshes the complete SSH
fragment as well.

## Destroy

```bash
farrow destroy node-3
farrow destroy
farrow destroy --delete-persistent
farrow destroy --purge
farrow purge                         # discard everything without confirmation
```

`--delete-persistent` and `--purge` are valid only for whole-deployment
destroy, not with node selectors. `--purge` removes persistent disks, keys,
and deployment state; images remain cached. Node destroy refreshes the SSH
fragment for remaining peers, while whole destroy removes the default Farrow
SSH integration. Host network removal is separate
and refuses while a VM is attached:

`farrow purge` is the concise disposable-lab path. It is
equivalent to `destroy --force --purge`, accepts no node selectors, and is
idempotent when no deployment exists. It keeps the image cache and host
network, and it does not bypass process, ownership, or path-integrity checks.

```bash
farrow network uninstall --yes
```

See [Image Repositories](../images/) for image selection, mirrors, and cache
pruning, or [Uninstall and Clean Up](../uninstall/) to remove host state.
