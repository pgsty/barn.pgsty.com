---
title: "VM specification parameters: commands, short flags, environment, and root disks"
linkTitle: "VM parameter design"
description: "A unified CLI, environment, inventory precedence, command scope, and persistence contract for image, architecture, CPU, memory, scale, and root disk size."
date: 2026-11-11
lastmod: 2026-11-11
weight: 72
categories: [Design]
tags: [CLI, Pigsty, Configuration]
icon: fa-solid fa-sliders
---

Image, architecture, CPU, memory, scale, and root disk size form one set of **VM specification inputs**, with consistent names, value rules, and source tracking. Each command declares which fields it accepts and which changes it can apply; the resolution process has one implementation.

**Status (2026-11-11):** This approved design is implemented: six CLI/environment inputs, command integration, inventory generation, source tracking, `SPEC` display, and in-place root growth. These changes remain unreleased. Working-tree inventories default to 1 vCPU / 2 GiB; released Barn 1.1.0 still defaults to 2 vCPU / 4 GiB.

## Six parameters with consistent names {#parameters}

| Meaning | Inventory field | Long flag | Short flag | Environment variable | Candidate default |
|---|---|---|---|---|---|
| Image | `vm_image` | `--image` | `-I` | `BARN_IMAGE` | Embedded catalog default `u24` |
| Architecture | `vm_arch` | `--arch` | `-A` | `BARN_ARCH` | `native` |
| Base CPU | `vm_cpu` | `--cpu` | `-C` | `BARN_CPU` | `1` |
| Base memory | `vm_mem` | `--mem` | `-M` | `BARN_MEM` | `2048` MiB |
| Resource multiplier | `vm_scale` | `--scale` | `-S` | `BARN_SCALE` | `1` |
| System root disk size | `vm_disk` | `--disk` | `-D` | `BARN_DISK` | `64` GiB |
{.wide .expand}

Uppercase short flags form a consistent specification group and avoid existing lowercase flags: `-c` for CIDR, `-m` for setup mode, `-s` for script/source, and `-d` for dry-run. Register the six flags only on supporting subcommands, rather than as persistent root flags, so they do not intercept options passed through to SSH.

Use `mem` consistently with `vm_mem` and `BARN_MEM`. The first version needs only one canonical name for each field, without extra aliases such as `--memory`, `--cpus`, or `--root-disk-size`. `--image` retains its existing family, channel, and version syntax and replaces the inventory's `vm_image/vm_version` pair; no separate version flag is needed. Other specification overrides must leave image selection alone.

CPU, memory, scale, disk, and image apply to selected nodes. Architecture remains deployment-wide; selecting nodes cannot create a deployment with mixed guest architectures.

## Precedence and calculation order {#base-values}

Resolve each field independently:

```text
Explicit CLI > corresponding nonempty environment variable > host > deepest child group > parent group > all.vars > default

Effective CPU    = selected vm_cpu × selected vm_scale
Effective memory = selected vm_mem × selected vm_scale
Root disk size   = selected vm_disk
```

Both CLI and environment values are overrides and can replace explicit host values on selected nodes. To retain host exceptions, put default multipliers in `all.vars` or narrow the node selection. `--scale 3` replaces the inventory or environment multiplier; all sources produce one final multiplier. Root disks, data disks, node count, and networking do not scale.

Given inventory values `vm_cpu: 2`, `vm_mem: 4GiB`, `vm_scale: 2`, and `vm_disk: 64`:

| Override input | Effective CPU | Effective memory | Root disk |
|---|---:|---:|---:|
| None | 4 | 8 GiB | 64 GiB |
| `--scale 3` | 6 | 12 GiB | 64 GiB |
| `BARN_SCALE=3` with `--scale 1` | 2 | 4 GiB | 64 GiB |
| `--cpu 4` | 8 | 8 GiB | 64 GiB |
| `--cpu 4 --mem 8GiB --scale 1 --disk 128GiB` | 4 | 8 GiB | 128 GiB |

CLI CPU and memory still specify base values. Corresponding YAML, CLI, and environment inputs therefore participate in the same formula; use `--scale 1` to specify exact final resources. `plan` should show the bases, multiplier, result, and sources so `--cpu 4` is not mistaken for an unconditional final count of four CPUs. Source and calculation details stay outside the VM specification hash.

CPU and scale accept only positive integers, and effective CPU cannot exceed 256. Base memory must be at least 512 MiB, with overflow checks for capacity calculations. CLI and environment inputs use the same size parser: bare memory integers mean MiB, and bare disk integers mean GiB. Existing unit syntax such as `4G` and `4GiB` remains available; examples should prefer explicit units. Invalid values fail without rounding, clipping, or falling back to defaults.

## Supported commands {#commands}

| Command or mode | Accepted specification inputs | Behavior and persistence |
|---|---|---|
| `init` | All six | Generate an inventory containing bases, scale, and other chosen specifications; `-o -` writes only to stdout |
| `setup` generating a template | All six | Use the same template resolution as `init`, display the preparation plan, then follow the existing host preparation and inventory publication flow |
| `setup -f` or discovered inventory | No specification overrides | Prepare the host for the existing file; reject explicit specification flags and ignore VM specification environment variables |
| `validate` | All six | Validate the entire inventory's effective specifications under these inputs, so the intended startup parameters can be checked consistently |
| `plan` | All six | Explain sources, calculate resources, check image and root disk constraints, and show changes and follow-up commands |
| `up` | All six | Create new nodes with the effective specifications; resource changes on existing nodes require `resize`, and other changes require explicit `recreate` |
| `reload` | All six | Share the desired specification with `up` for new nodes and preflight checks; reject unsupported changes to existing nodes before stopping them |
| `recreate` | All six | Rebuild explicitly using the effective specifications, retaining existing confirmation, root disk replacement, and persistent disk policies |
| `resize` | `C/M/S/D`; retain existing `I/A` checks | Apply CPU/memory changes and grow the root disk; never shrink it or change image/architecture |
| `start/stop/restart/status/destroy/purge` | None | Use applied state; specification environment variables do not affect these operations |
| `ssh/exec/logs/provision/hosts/network`, etc. | No generic specification inputs | Retain each command's own operation parameters |
{.wide .expand}

`validate` gains no node selectors. Other lifecycle commands that support selection override only selected nodes, or all nodes when no selector is given. Initially, the environment variables apply only to the Linux VM entry points listed above. `barn mac` and independent image management commands retain their own interfaces. For example, `image pull -A` selects an artifact architecture but does not automatically read this proposal's VM environment defaults.

`resize` already exposes I/A, and its tests and reference documentation preserve that interface, so this change should retain it. Keep the existing strict checks: users may use I/A to make the desired specification match the current image and architecture, but cannot change either through resize. Corresponding environment variables receive the same checks. Both `--disk/-D` and `BARN_DISK` are now accepted for root growth only.

Determine whether `setup` generates or reuses an inventory before reading specification environment variables. `setup full -C 2` selects template generation; if the destination exists and differs, preserve it and report a conflict. Bare `setup` that discovers an inventory prepares the host for that file, so an exported `BARN_IMAGE` cannot silently select another image.

## SPEC display contract {#spec-display}

Use `SPEC` as the column heading and a compact effective CPU/memory value such as `1c2g`, `2c4g`, or `8c16g`. Lowercase `c` means vCPU and `g` means GiB. The value contains the scaled resources; disk capacity and scale remain separate. Display 1536 MiB as `1.5g` and 512 MiB as `0.5g`, without rounding. Capacities not divisible by MiB retain their exact byte count with `b`. Unknown resources display `-` instead of assumed defaults.

| Location | Meaning of SPEC |
|---|---|
| `init` summary, `setup` preparation plan, `validate` | Effective generated or validated resources |
| `plan` | Desired resources; changes appear as `2c4g → 4c8g` |
| `status`, lifecycle completion results | Applied CPU/memory specifications |
| Live lifecycle progress | The operation's target specification; later status events can update it to applied resources |

`plan/setup/validate/status` show root capacity in a separate `ROOT` column, with old and desired values for changes; `init` lists root capacity separately. Lifecycle results without a live table list each node's SPEC. When scale differs from 1, show bases, multiplier, result, and sources; `--verbose` also explains calculations with scale 1. JSON retains numeric CPU, byte capacities, and structured `resources` explanations instead of replacing numbers with abbreviations. Formatting and explanations neither affect VM specification hashes nor become an input syntax.

## Root disk size and in-place growth {#root-disk}

`--disk/-D` maps to `vm_disk`, the absolute target size of the system root disk. Barn also provides a default 128 GiB data disk mounted at `/data`; this proposal retains that behavior and introduces no multi-disk CLI. With `-D 128GiB -S 3`, the root disk remains 128 GiB.

During creation and explicit recreation, Capacity must be positive and at least the selected base image's virtual size; download size is not the lower bound. Planning can use `virtual_size` from the verified catalog, followed by an actual image check during creation, without downloading the whole image for a read-only validation. If an existing root disk differs, `up` reports drift rather than modifying it with disk tools. Applying a size change through `recreate` replaces the original root disk and nonpersistent data disks; that operation is an explicit rebuild and must not be described as growth that preserves data.

Grow an existing root disk with `barn resize -D 128GiB meta`. The argument is an absolute target; repeating the same target makes no further disk change. Do not accept incremental syntax such as `+64GiB` or offer in-place shrinking.

Growth requires separate checks of the disk image, guest partition, and filesystem. QEMU requires extending guest partitions and filesystems after increasing image capacity, and warns against using offline `qemu-img` to modify an image in use. Prefer a recoverable offline flow for the first implementation; evaluate online QMP growth separately. [QEMU disk image tools](https://www.qemu.org/docs/master/tools/qemu-img.html)

Barn already writes `growpart` and `resize_rootfs: true` when creating guests. Cloud-init defines both modules with frequency `always`, but they can be disabled and partition layouts impose limits. A reboot alone cannot establish successful root disk growth. [Cloud-init Growpart](https://docs.cloud-init.io/en/latest/reference/modules.html#growpart), [Resizefs](https://docs.cloud-init.io/en/latest/reference/modules.html#resizefs)

The implementation persists `preflight → image → guest → verified`, recording the target before any disk mutation. Retry the same target to continue without shrinking to simulate rollback. Supported roots use 512-byte logical sectors and a last physical GPT or primary MBR partition with ext4/XFS. LVM, encrypted root devices, and other layouts are rejected before image modification. Initially stopped VMs temporarily boot for probing and expansion, then return to stopped. See [root growth acceptance](/blog/design/root-disk-growth/) for recovery details and native measurements.

## Environment variable rules {#environment}

Environment variables are useful once all six inputs share a resolution process that exposes their sources. They support CI matrices and temporary shell invocations with the same override semantics as CLI flags. They are inputs to the current command and therefore outrank host-level inventory values. Global defaults that must retain node exceptions belong in `all.vars`.

Invocations:

```bash
BARN_IMAGE=u26 BARN_SCALE=2 barn plan -f pigsty.yml
BARN_IMAGE=u26 BARN_SCALE=2 barn up -f pigsty.yml
BARN_SCALE=2 barn plan -f pigsty.yml -S 3  # The final multiplier is 3
```

Parse an environment variable only when the command accepts its field. `BARN_CPU=bad barn status` must succeed as usual; `up` with the same environment must report an error naming the variable. If CLI has already overridden the field, skip validation of the shadowed environment value: `BARN_CPU=bad barn up -C 2` uses 2.

An empty or whitespace-only environment value means unset, allowing an inherited value to be cleared for one invocation: `BARN_SCALE= barn plan` uses the inventory multiplier. Explicit `--scale=0`, `--scale=`, and invalid nonempty environment values still fail. Help and version commands remain unaffected by specification environment errors. The first version does not automatically read `.env`, global preference files, or historical parameters, and needs no ambiguous `--ignore-env` flag; `env -u BARN_SCALE` explicitly clears one input.

Specification explanations in `plan/validate/up` should identify sources, for example `scale: 3 (env BARN_SCALE)`. Structured output should provide the same information without dumping unrelated environment values. Suggested apply and failure-retry commands should freeze the effective environment overrides as explicit flags and retain the inventory path, node selectors, and argument values. Environment changes do not create hidden persistent settings.

Like `--image`, `BARN_IMAGE` on an inventory containing multiple images replaces the image for every selected node. Leave it unset to retain a build matrix's per-node image declarations. Existing variables such as `BARN_HOME`, `BARN_REPO`, output format, and debugging retain their separate contracts and do not join the scaling formula or specification table.

## Inventory, applied state, and persistence {#persistence}

Configuration generation and runtime overrides have separate persistence rules:

- `init` and template-generating `setup` explicitly write all six chosen values into `all.vars`, making defaults visible in the file. Record base CPU/memory and scale; never write multiplied results back as bases. `init` preserves existing files by default and replaces them only with explicit `--force`.
- The first interactive `up`, if it actually needs to generate a new inventory, uses the same generator and records its chosen specifications in that file. A subsequent ordinary `up` can read the same choices.
- With an existing inventory, `up/resize/recreate` override only the current desired specification without rewriting YAML. Successful operations record the actual effective specification in applied state. Reading the original inventory again shows differences, while commands such as `start` retain applied specifications.

For example, the commands below generate four nodes, each with 4 vCPU / 8 GiB and a 128 GiB root disk:

```bash
barn init full -I u26 -A arm64 -C 2 -M 4GiB -S 2 -D 128GiB
barn plan -f barn.yml
barn up -f barn.yml
```

When `setup <template>` decides whether an existing file can be reused, compare normalized bases and scale as well as final VM specifications. `2×2` and `4×1` produce the same CPU count but different results under a subsequent `--scale 3`; the generator cannot silently treat them as equivalent template choices. VM drift still compares final specifications, so different expressions of the same effective resources do not require a restart.

Applied state currently retains neither the original bases nor scale. Without a readable inventory, explicit CLI or environment scale must require `-f`; it must not multiply already-scaled applied resources again. CPU/memory alone can set absolute applied resources using an implicit scale of 1 while retaining the other applied specifications. Internal retries recompute from the same original inputs instead of applying another override to computed results.

## Pigsty integration {#pigsty}

Pigsty's Make entry point forwards only explicitly supplied `IMAGE/ARCH/CPU/MEM/SCALE/DISK` variables as corresponding CLI flags. Omit absent values, do not multiply resources in Make, and never inject `SCALE=1`. Explicit Make inputs become flags and therefore outrank `BARN_*` environment variables.

Pigsty's generator may write `u26` as the default image for homogeneous profiles, while Barn's own default remains `u24`. Build profiles retain per-node `vm_image`; do not append a uniform `-I` automatically. Save profile selections during generation when persistence is intended. Ordinary lifecycle commands retain the temporary override contract described above.

DNS has its own design. Host entry publication and service names do not belong among these six specification inputs.

## Implementation and delivery order {#implementation}

Use a small parameter table for names, short flags, environment names, parsing, and scope, plus a typed input structure carrying presence, value, and source. Commands declare accepted fields, supported changes, and whether they generate an inventory through a capability table. A generic configuration framework is unnecessary; individual commands should not independently call `os.Getenv` or duplicate similar flag registrations.

The shared process is: determine command mode and input source → collect permitted CLI/environment overrides → resolve inventory inheritance → apply fields to selected nodes → calculate effective specifications once → validate → plan or execute. Preserve the strict `vm_*` namespace. Inventory syntax, field types, and inheritance conflicts must remain valid; CLI overrides cannot bypass unknown fields, malformed YAML, or selector errors. Check the effective CPU limit and memory overflow after applying overrides.

The working tree uses `internal/config/resources.go` for bases, scale, and sources, and `cmd/barn/vm_inputs.go` to register the six inputs and parse permitted environment variables. [Inventory parsing](https://github.com/pgsty/barn/blob/main/internal/config/inventory.go) applies selected-node resource overrides before multiplication; image and architecture retain their existing override semantics. `init/setup` share template generation, and internal host preparation by `up` preserves resolved specifications. `internal/private/root_resize.go` reuses `disk.Manager.Grow` and holds the deployment lock across offline growth, guest verification, and recovery.

| Phase | Deliverables | Acceptance focus |
|---|---|---|
| A: Unified specification input | Six fields, C/M/S/D long and short flags, environment variables, precedence, provenance, and command capabilities; no growth of existing root disks | Parameter combinations, invalid input, environment shadowing, scope, equivalent outputs, and existing I/A behavior |
| B: Command integration | init, setup, validate, plan, up, reload, recreate; CPU/memory/scale for resize | Bases in generated inventories, existing files unchanged, selected-node scope, idempotent retries, and identical specifications in planning and execution |
| C: In-place root growth | D for resize, change classification, offline disk growth, guest expansion, and recovery from partial failure | No shrink or loss of existing data, retained identity, actual capacity checks, running/stopped state, and repeated execution |
{.wide .expand}

A, B, C, and SPEC display are implemented; root growth has separate ext4/XFS native acceptance. Source regression coverage should also exercise [template generation](https://github.com/pgsty/barn/blob/main/internal/config/template.go), [setup](https://github.com/pgsty/barn/blob/main/cmd/barn/setup.go), [resize boundaries](https://github.com/pgsty/barn/blob/main/internal/private/resize.go), and [root disk creation](https://github.com/pgsty/barn/blob/main/internal/disk/disk.go).

Acceptance covers `internal/config/resources_test.go` and `cmd/barn/vm_inputs_test.go`, along with `make build`, source `make check`, and site `make check`. Build and read-only CLI acceptance use a temporary `BARN_HOME`; existing VMs and host networking remain untouched. Root growth also has `internal/private/root_resize_test.go` and [native acceptance](/blog/design/root-disk-growth/) in an isolated temporary deployment. Current contracts are documented under [specification overrides](/docs/reference/configuration/#specification-overrides) and [SPEC display](/docs/reference/cli/#vm-specification-flags).

Implementation evidence is local commit `1e24768`, not yet present on the reviewed remote main. New source files below are identified by repository-relative paths; see the [command reference version baseline](/docs/reference/commands/#versions).
