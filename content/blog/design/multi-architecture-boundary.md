---
title: "Beyond amd64 and arm64"
linkTitle: "Guest architecture contracts"
description: "How guest architecture selects an emulator, machine, firmware, devices, and acceptance tests in Barn."
date: 2026-11-08T10:00:00+08:00
weight: 90
categories: [Design]
tags: [Architecture, QEMU, Images]
icon: fa-solid fa-microchip
lastmod: 2026-11-08
---

Barn currently supports `amd64` and `arm64` Linux guests. QEMU can emulate more architectures, but each additional Barn target needs an image and a complete boot-and-operation contract. This design assessment, reviewed on **2026-11-08**, separates the existing runtime policy from possible future targets.

## Hardware acceleration follows the host ISA {#acceleration}

For Barn's current 64-bit guest targets, native virtualization uses the host's instruction set: HVF on macOS and KVM on Linux. QEMU TCG translates instructions for a foreign guest architecture. Rosetta can translate Intel Linux applications inside an Arm Linux VM; it does not provide an Intel Linux VM on Apple Silicon. See [QEMU's emulation overview](https://www.qemu.org/docs/master/about/emulation.html) and [Apple's Linux binary translation guide](https://developer.apple.com/documentation/virtualization/running-intel-binaries-in-linux-vms).

| Host | amd64 guest | arm64 guest | Current native release evidence |
|---|---|---|---|
| macOS arm64 | TCG | HVF, subject to image compatibility | Tier1 |
| macOS amd64 | HVF | TCG | Tier2 |
| Linux amd64 | KVM | TCG | Tier1 |
| Linux arm64 | TCG | KVM | Tier2 |
{.wide}

Barn's tiers describe release evidence. Native Darwin arm64 and Linux amd64 have the primary live acceptance coverage; Darwin amd64 and Linux arm64 remain Tier2 until equivalent physical-host evidence is recorded. All TCG profiles are Tier2. A binary that cross-compiles is not sufficient evidence to promote a runtime tier.

There are two image-specific restrictions: stock EL8 arm64 uses TCG on Apple Silicon because of its 64 KiB translation-granule requirement, and EL7 is limited to native Linux/amd64. An unexpected failure of native acceleration fails the operation rather than silently selecting TCG. The authoritative policy is in [`platform.go`](https://github.com/pgsty/barn/blob/main/internal/platform/platform.go) and [`selectRuntime`](https://github.com/pgsty/barn/blob/main/internal/private/manager.go).

## Keep the complete emulated boot profile {#boot-profile}

The existing arm64 TCG profile uses `qemu-system-aarch64`, the `virt` machine, and `cortex-a72`. Barn's arm64 images require UEFI, with a matching firmware code image and a writable per-VM variable store. The target emulator and firmware must be installed even when the host architecture differs; Linux setup currently plans native-host dependencies.

For amd64 guests on arm64 hosts, Barn explicitly uses `tcg,thread=single` to preserve the stronger x86 memory-ordering contract. Other emulated profiles use `tcg,thread=multi`. Increasing the vCPU count therefore does not imply more translation threads in every configuration.

QEMU's [`virt` documentation](https://www.qemu.org/docs/master/system/arm/virt.html) lists `cortex-a72` as a 64-bit CPU and warns that the `max` model can change across QEMU versions. A prior Barn investigation observed a firmware hang with one `max` configuration and a successful boot with `cortex-a72` plus explicit pflash code/vars. Because the firmware arguments also changed, that observation cannot isolate the CPU model as the cause. It supports retaining the tested profile while investigating any change with a controlled comparison.

Keep guest architecture explicit in inventory and catalog metadata. qcow2 metadata describes the disk container, not the guest instruction set. Selecting a foreign image requires both the correct image architecture and a matching runtime profile.

## Each new architecture needs different boot assumptions {#targets}

The following are QEMU integration candidates, not supported Barn values:

| Candidate | QEMU target and machine | Boot contract to establish |
|---|---|---|
| `ppc64le` | `qemu-system-ppc64`, `pseries` | Little-endian guest; SLOF or a validated VOF/direct-kernel path; pSeries console and devices |
| `s390x` | `qemu-system-s390x`, `s390-ccw-virtio` | CCW/virtio devices and explicit `bootindex`; replace PC-style boot assumptions |
| `riscv64` | `qemu-system-riscv64`, `virt` | OpenSBI/U-Boot or a validated EFI path; device tree, CPU extensions, and serial console |
| `loongarch64` | `qemu-system-loongarch64`, `virt` | A validated CPU model such as `la464`, matching EDK2 firmware, and compatible guest image |
{.wide}

The machine and boot differences are documented by QEMU for [pSeries](https://www.qemu.org/docs/master/system/ppc/pseries.html), [s390x boot devices](https://www.qemu.org/docs/master/system/s390x/bootdevices.html), [RISC-V virt](https://www.qemu.org/docs/master/system/riscv/virt.html), and [LoongArch virt](https://www.qemu.org/docs/master/system/loongarch/virt.html). All four candidates would use TCG on Barn's current amd64/arm64 hosts. Native Linux hosts for those instruction sets would be a separate host-support project.

Distribution support has several levels: a released CPU port, an installer, a root filesystem, and a generic cloud disk. A candidate must identify which one is available, its immutable source and checksum, and whether its bootloader and cloud-init configuration match the selected QEMU machine. Do not synthesize a download URL by replacing the architecture in another file name. The [image evidence workflow](/blog/design/image-update-evidence/) applies before any candidate enters the catalog.

## Implementation boundary {#implementation}

Adding a name to the architecture parser would leave the rest of the product incomplete. A target needs coordinated changes in:

- Platform and image schemas: canonical architecture names, aliases, validation, catalog entries, and release tier. Existing catalog readers reject unknown fields and unsupported architectures, so the rollout also needs an explicit compatibility policy for older clients.
- QEMU invocation: executable, machine, CPU, firmware/boot method, console, disk and NIC transports, and QMP identity.
- Guest initialization: seed delivery, user and key setup, interface naming, data-disk detection, and filesystem support.
- Host preparation: dependency packages, minimum QEMU capabilities, preflight diagnostics, and available firmware.
- Lifecycle operations: cold boot, SSH readiness, stop/start, resize capabilities, persistent disks, recreation, cancellation, and interrupted-operation recovery.

The existing entry points are [`internal/platform`](https://github.com/pgsty/barn/tree/main/internal/platform), [`internal/qemu`](https://github.com/pgsty/barn/tree/main/internal/qemu), [`internal/cloudinit`](https://github.com/pgsty/barn/tree/main/internal/cloudinit), [`internal/setup`](https://github.com/pgsty/barn/tree/main/internal/setup), and the [image pipeline](https://github.com/pgsty/barn/tree/main/packaging/image-pipeline).

## Acceptance for a new target {#acceptance}

Start with one generic cloud image per candidate. Record its source and digest, QEMU version, full launch profile, and firmware. In a fresh temporary data root, verify cold boot, the expected `uname -m`, SSH identity, outbound traffic, host access, peer communication, data mounts, and restart. Then test recreate/destroy boundaries, preserved disks, and recovery after cancellation. Unsupported optional features need explicit diagnostics.

The research suggests evaluating ppc64le and s390x first, followed by riscv64 and then loongarch64. This order is an engineering hypothesis based on image availability and boot integration work, not a committed roadmap; a better validated image or a concrete user workload can change it.

Measure functional compatibility and performance separately. TCG is useful for installation, packaging, and architecture checks; database throughput and compilation benchmarks need measurements on representative native hardware before informing capacity decisions.
