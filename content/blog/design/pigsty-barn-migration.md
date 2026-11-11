---
title: "Replacing Vagrant with Barn in Pigsty: resources, names, and migration work"
linkTitle: "Pigsty sandbox migration"
description: "An audit of Pigsty's Vagrant workflow, the vm_scale and local hosts contracts, and an ordered migration plan based on 54 inventory templates."
date: 2026-11-10
lastmod: 2026-11-11
weight: 71
categories: [Design]
tags: [Pigsty, Vagrant, DNS]
icon: fa-solid fa-boxes-stacked
---

Pigsty can use one inventory for Barn and Ansible. The migration needs to preserve topology selection, image matrices, resource scaling, fixed addresses, and SSH workflows while replacing the old scripts' implicit addressing, naming, and destruction behavior.

**Status (2026-11-10):** `vm_scale`, the 1-vCPU / 2-GiB defaults, `vm_hosts`, `barn hosts install -f`, and Pigsty's `bin/sandbox-dns` are implemented in the local working trees and have passed the offline checks below. They are unreleased. Pigsty's Makefile still uses Vagrant; the second half of this article describes the remaining work. Released Barn 1.1.0 actually defaults to 2 vCPU / 4 GiB when parsing an inventory and does not support these additions.

## What the Vagrant scripts provide {#vagrant-contract}

| Entry point | Current design | Migration decision |
|---|---|---|
| `vagrant/config`, `vagrant/spec/*.rb` | Combine topology, distribution, scale, provider, and architecture into a Vagrantfile; accept scales of 1–64; preserve per-node images in build profiles | Move topology and resources into Pigsty inventory `vm_*` fields; retain image selection and scaling, with Barn handling platform backends |
| Make aliases such as `meta/full/simu` | Configure Pigsty, select a VM spec, and default to EL9; many targets implicitly depend on `del` | Follow the earlier proposal to default the new Pigsty entry point to `u26`, with distribution suffixes; separate creation, recreation, and destruction and inspect configuration changes with `plan` |
| `vagrant/ssh` | Combine VM specs and `vagrant ssh-config` into host SSH configuration | Use Barn's automatic SSH integration, preserving keys, management ports, known-hosts files, and instance identity |
| `vagrant/dns` | Read node names from Ruby specs and assign a fixed list of `.pigsty` names to the first node | Extract names from Pigsty inventory and role defaults; preview by default and publish explicitly |
| Provider templates | Disable the default `/vagrant` share, install an SSH public key, and configure networking and extra disks | Let Barn initialize guests, users, networks, and disks; choose scp/rsync or `vm_shares` explicitly for source delivery |
| `new`, `del`, `nuke`, `suspend` | Recreate, destroy without confirmation, clean up, and suspend guest memory | Map lifecycle operations explicitly and retain destruction scope confirmation; `stop/start` does not restore guest memory |
| `bin/boot-pkg`, Make copy/sync targets, `bin/release` | Distribute packages through `meta` and distribution aliases; continue shipping Vagrant scripts | Verify SSH aliases and directories, then migrate the release manifest as well as `make up` |
{.wide .expand}

Old resource differences need not carry over: `meta` uses 2 vCPU / 4 GiB; `full` uses one 2-vCPU / 4-GiB node and three 1-vCPU / 2-GiB nodes; `simu` mixes several sizes. The new base is 1 vCPU / 2 GiB per node. Database, build, or application tests can raise their base resources or scale explicitly. These VM defaults do not replace module capacity requirements.

Prerequisites such as `new: del up` and `meta9: cmeta del vmeta9 up ssh` do not establish a reliable execution order. `make -j` can configure, destroy, and start concurrently. The new entry point should use a sequential recipe or script that stops at the first failure.

Sources: [configuration generator](https://github.com/pgsty/pigsty/blob/main/vagrant/config), [Vagrant directory](https://github.com/pgsty/pigsty/tree/main/vagrant), and [Pigsty Makefile](https://github.com/pgsty/pigsty/blob/main/Makefile).

## The vm_scale decision {#scale}

Resolve `vm_cpu`, `vm_mem`, and `vm_scale` independently in this order: **host > deepest child group > parent group > all.vars > default**. Then multiply once:

```text
Effective CPU    = base vm_cpu (default 1) × vm_scale (default 1)
Effective memory = base vm_mem (default 2048 MiB) × vm_scale (default 1)
```

Setting only `vm_scale: 3` produces 3 vCPU / 6 GiB. Adding `vm_cpu: 2` and `vm_mem: 4GiB` produces 6 vCPU / 12 GiB. A host can set `vm_scale: 1` to override its group's multiplier; scales at different levels do not compound. Disks do not scale. See the [configuration reference](/docs/reference/configuration/#resource-scaling) for units, bounds, and upgrading existing deployments.

The [VM parameter design](/blog/design/vm-resource-overrides/) specifies command scope, short flags, environment variables, precedence, and persistence for image, architecture, CPU, memory, scale, and root disk size. The proposal forwards only explicitly supplied Make `IMAGE/ARCH/CPU/MEM/SCALE/DISK` variables as CLI flags, which outrank corresponding `BARN_*` environment variables. Template defaults and host exceptions remain in YAML, and ordinary lifecycle commands save no hidden preferences. An `IMAGE` option or distribution suffix may override images in homogeneous profiles. Build profiles must retain per-node `vm_image` unless the user explicitly requests one image for all nodes.

## DNS is feasible as an explicit operation {#dns}

Changing the system `/etc/hosts` still requires root. Extraction, validation, and preview can run as the ordinary user, with only the final controlled write delegated to Barn's helper. Repeating an unchanged plan needs no sudo. Initial setup is one occasion to publish names; adding a portal or changing a VIP requires another publication.

Pigsty's `bin/sandbox-dns` interprets service configuration. Barn accepts generic `all.vars.vm_hosts` mappings, combines them with node names and aliases, validates them, and replaces the `# barn:begin/end` block. These mappings stay outside the VM spec hash, so DNS edits do not require VM recreation or restart.

| Source | Host-side destination |
|---|---|
| Barn node names and `vm_alias`; Pigsty `nodename` and `pg_cluster-pg_seq` | Node IP |
| `infra_portal.*.domain/domains` | The infra configuration's `admin_ip` ingress, rather than a backend endpoint that may use `127.0.0.1` |
| `node_default_etc_hosts`, `node_etc_hosts`, `dns_records` | Declared IP with `${admin_ip}` expanded; relevant enable switches are honored |
| `pg_cluster + pg_dns_suffix` | `auto` uses an enabled PG VIP or the inventory's unique declared primary; also supports `primary`, `vip`, `none`, and explicit IPs |
| `node_cluster + vip_dns_suffix` | Enabled node VIP, applying `node_id_from_pg` cluster identity rules |
| `minio_node` and `minio_cluster-minio_seq` | MinIO node IP, expanding MinIO name placeholders |
| `vm_hosts` | Explicit additional private-network mappings |
{.wide .expand}

With the development commands available, run these from the Pigsty repository:

```bash {title="Pigsty repository"}
# Requires Python 3, PyYAML, and a Barn build with hosts install -f
bin/sandbox-dns -f conf/meta.yml          # preview by default
bin/sandbox-dns -f conf/meta.yml --json
bin/sandbox-dns -f conf/meta.yml --apply  # Barn requests sudo when necessary
barn hosts uninstall --yes
```

Set `BARN=/absolute/path/to/barn` to use a local build. The script first calls `barn validate`, then creates a temporary inventory with mode `0600` containing only node identities and names. It does not copy Pigsty credentials, keys, or share configuration. Identical mappings deduplicate; conflicting destinations identify their sources, with names compared without case. Records owned by other tools remain intact, and conflicts require an explicit decision about migrating those older records.

Like Barn, the adapter reads a static inventory without running inventory plugins, `group_vars`, `host_vars`, or general Jinja expressions. Unresolved templates in relevant fields, wildcards, and addresses outside the inventory subnet fail explicitly. `pg_dns_target: primary` reflects the declared inventory and does not follow live Patroni failover; an already configured VIP is preferable for an HA entry point. When several infra nodes each resolve `i.pigsty` to themselves, the host cannot represent all those local views simultaneously. Select one ingress or use distinct domain names first.

If wildcard names and dynamic records become necessary, evaluate domain-specific forwarding to Pigsty DNS. macOS domain resolvers and Linux resolver integration need separate designs. The current phase needs neither a resident DNS process on the host nor a global nameserver change.

## Offline audit of 54 configurations {#audit}

On 2026-11-10, the local candidate ran `barn validate --json` against all 54 `conf/**/*.yml` files and extracted their names. **53 passed VM validation; 42 passed DNS extraction.** These are static checks. Module deployment and VIP failover still require native acceptance tests.

| Configuration/category | Result and required work |
|---|---|
| `meta` | 1 node, 1 vCPU / 2 GiB; 10 names extracted and an actual hosts preview succeeded |
| `ha/dual`, `ha/trio`, `ha/full` | 2/3/4 nodes, totaling 2/3/4 vCPU and 4/6/8 GiB by default; valid VM specs, but PG VIPs occupy reserved addresses |
| `ha/simu` | 20 nodes, 20 vCPU / 40 GiB; reserved PG VIPs, and MinIO expects `/data{1...4}` without declaring four `vm_disks` |
| `demo/minio` | 4 nodes with 4×64 GiB data disks each; 21 names extracted; include its `.9` node VIP in native network acceptance |
| `build/oss` | 7 nodes with explicit 2 vCPU / 4 GiB each, totaling 14 vCPU / 28 GiB, and explicit per-node images; conflicting host-side destinations for `i.pigsty` |
| `build/dev` | 7 parseable nodes, but no per-node `vm_image`, so all would use Barn's `u24` default; distribution SSH aliases also need attention; DNS has the same multi-destination conflict |
| `demo/demo` | `nodename: pigsty.cc` violates Barn's VM naming rules; use a short node name and put the FQDN in `vm_alias` |
| Other templates with reserved VIPs | `demo/debian`, `demo/el`, `fat`, `ha/octo`, `ha/safe`; together with the four HA profiles above, 9 templates are affected |
{.wide .expand}

Barn reserves `.1` for the host and `.2`–`.8` for DHCP; static nodes start at `.9`. Pigsty's common `.2/.3/.4` VIPs must move. None of the current 54 templates uses `.100/.101/.102`, making them candidates for this sandbox migration. Update explicit DNS records, connection strings, and examples together, and check for collisions with the selected inventory's nodes and other VIPs. Relaxing hosts validation would not resolve the network conflict.

Barn names nodes using `nodename > pg_cluster-pg_seq > node-lastOctet`. Pigsty's `node_id_from_pg: true` can instead overwrite an explicit `nodename` in the guest. Preserve old script names such as `meta`, `node-1`, and `el9` explicitly through inventory names and `vm_alias`; verify both host SSH aliases and guest hostnames.

## Complete the replacement in this order {#rollout}

| Priority | Owner and scope | Acceptance condition |
|---|---|---|
| Implemented, unreleased | Barn resources and hosts foundation; Pigsty name extraction | Checks recorded here; repeat catalog/version release gates before publication |
| P0: inventory corrections | Pigsty `conf/` VIPs, simu disks, dev images, short names, and SSH aliases | Every target profile passes VM and name validation, with expected totals and image matrices |
| P0: switch entry points | Makefile, a common `bin/sandbox` entry point, and `configure` integration; default `meta/full/simu` to `u26`; map suffixes `8/9/10/12/13/22/24/26` to `el8/el9/el10/d12/d13/u22/u24/u26` | Sequential behavior even with `make -j`; explicit `-f` avoids a shadowing `barn.yml`; profile changes never imply destruction; ordinary up leaves hosts alone |
| P0: SSH and artifact delivery | Use `barn ssh-config`, migrate aliases in copy/boot-pkg/sync, and reuse `dba`/UID 88 and verified connection parameters | Host SSH, scp/rsync, and Ansible access from the control node work; old Vagrant Includes do not win matching |
| P0: native acceptance | macOS arm64 and Linux amd64, covering at least meta, full, simu, and a mixed-image build | 1×/2× resources and resize, idempotent DNS, VIP access/failover, four-disk mounts, stop/start, failure retry, explicit destruction, and a fresh Pigsty deployment |
| P1: release integration | `bin/release`, installation dependencies, bilingual guides and examples, and retiring Vagrant entry points | The release archive completes a sandbox workflow with Barn and contains no obsolete entry points in its scripts or guides |
| P1: ongoing usability | Exact environment records, common group selection, upload/download, and measured large-topology startup improvements | Reproducible builds and artifact retrieval, with diagnosable and retryable partial failures |
| P2: demand-driven additions | Cold snapshots, VM export, dynamic DNS/domain forwarding | Define identity, disk, and network recovery contracts for each feature first |
{.wide .expand}

Barn still manages one Linux deployment per user. Profiles describe desired topologies for that deployment. Changing `BARN_HOME` does not isolate the user's shared runtime paths or host private network, so it is not a concurrent-environment mechanism. Image defaults belong to separate layers too: the new Pigsty entry point can select `u26` while Barn retains its embedded catalog's `u24` default.

## Implementation and validation evidence {#evidence}

Resource inheritance and scaling are in [inventory.go](https://github.com/pgsty/barn/blob/main/internal/config/inventory.go) and [inventory_test.go](https://github.com/pgsty/barn/blob/main/internal/config/inventory_test.go). Hosts merging and privilege boundaries are covered by [hostconfig](https://github.com/pgsty/barn/tree/main/internal/hostconfig) and `cmd/barn/hosts_inventory_test.go`. Pigsty's new local files are `bin/sandbox-dns` and `tests/test_sandbox_dns.py`, with service rules checked against [roles/infra](https://github.com/pgsty/pigsty/tree/main/roles/infra), [roles/pgsql](https://github.com/pgsty/pigsty/tree/main/roles/pgsql), [roles/node_id](https://github.com/pgsty/pigsty/tree/main/roles/node_id), and [roles/minio](https://github.com/pgsty/pigsty/tree/main/roles/minio). These links identify the repositories; the local working trees remain authoritative for the unreleased changes until they are committed and published.

Completed checks include `make build`, Barn `make check`, 11 Pigsty extractor unit tests, and the 54-template offline audit. The real command for `conf/meta.yml` returned `applied: false` and displayed 10 names. System hosts writes, VM resource changes, VIP failover, and Pigsty playbooks have not been executed; they are assigned to the native acceptance phase above.
