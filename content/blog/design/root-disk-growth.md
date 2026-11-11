---
title: "In-place root growth: recovery and native acceptance"
linkTitle: "Root growth acceptance"
description: "The grow-only resize -D contract, offline and guest expansion, failure recovery, and ext4/XFS native acceptance."
date: 2026-11-11
lastmod: 2026-11-11
weight: 74
categories: [Design]
tags: [CLI, QEMU, Storage]
icon: fa-solid fa-hard-drive
---

**Status (2026-11-11):** The unreleased development build implements `barn resize -D`, with ext4 and XFS acceptance on macOS/arm64 using QEMU/HVF guests. Released 1.1.0 still limits resize to CPU/memory. See [VM specification design](../vm-resource-overrides/) for input precedence and [root growth](/docs/reference/cli/#root-disk-growth) for the command contract.

## Supported scope {#scope}

```bash
barn resize -D 128GiB meta
BARN_DISK=128GiB barn resize meta
```

The target is an absolute root capacity. Growth is supported; shrinking is rejected. Repeating a completed target neither changes the image nor restarts the VM. CPU/memory changes may accompany growth; scale does not multiply disk size. Changes to images, architecture, data disks, networking, and shares still require explicit recreation.

MBR targets cannot exceed 2 TiB. Supported roots are plain ext4/XFS partitions with 512-byte logical sectors, in GPT or primary MBR layouts. The root must be physically last without overlapping other partitions. LVM, encrypted roots, later partitions, and missing guest tools fail before image modification. Disk serial, UUID, PARTUUID, partition number, and starting offset bind the operation to the original device. The workflow does not format disks or recreate partitions.

Running nodes stop for image growth and return to running. Stopped nodes temporarily boot to inspect the layout, stop for image growth, boot to expand the filesystem, then return to stopped. The deployment lock spans this workflow, preventing another lifecycle command from starting QEMU during image modification.

## Recovery protocol {#recovery}

The node's `root_resize` record stores original capacity, target capacity, original power state, and guest root identity. Each execution rereads current state rather than adding capacity to an already enlarged value.

| Durable stage | Next action | Recovery after interruption |
|---|---|---|
| `preflight` | Start or inspect the guest; probe layout and tools | Preserve original power intent and repeat the probe |
| `image` | Prove QEMU exited; run qemu-img resize; verify and sync the image | Inspect actual virtual size; an image at target is not grown again |
| `guest` | Reconcile applied state; boot and run growpart plus resize2fs/xfs_growfs | Keep the enlarged image and partition; continue filesystem growth and verification |
| `verified` | Restore original power state, then clear the record | Retry power restoration and the final state write |

A failed preflight clears its record once original power state is restored, allowing a corrected target before any disk mutation. `image` is durable before image growth, so a CLI killed after qemu-img succeeds still retains its target. A metadata write failure restores metadata only; it never shrinks the real disk to simulate rollback. Applied state may already record the enlarged capacity while guest completion is pending. `status` and `plan` keep that pending condition visible; retrying resize with the same target clears it after verification. Fix guest tooling or connectivity and retry the suggested command; no separate repair command is needed.

Completion verifies image virtual size, guest block device size, partition extent, and filesystem geometry. ext4 uses block count times block size; XFS uses data block count times block size. Free space from `df` is not a capacity measurement. Checks allow partition-table tail space and filesystem alignment. The CPU/memory hot-plug marker `resize_incomplete` stays separate from root recovery.

## Native acceptance {#acceptance}

Acceptance used an isolated temporary `BARN_HOME`, two 1c1g guests, and 12 GiB initial roots. Images were Debian 13 `20261103.2651.1` and Rocky Linux 9 `9.8.20260525.2`, both arm64. All measurements below are bytes.

| Guest | Root disk: before → after | Root partition: before → after | Filesystem: before → after |
|---|---|---|---|
| Debian 13 / ext4 | 12,884,901,888 → 15,032,385,536 | 12,750,667,264 → 14,898,150,912 | 12,750,663,680 → 14,898,147,328 |
| Rocky Linux 9 / XFS | 12,884,901,888 → 15,032,385,536 | 11,730,402,816 → 13,877,886,464 | 11,730,399,232 → 13,877,882,880 |
{.wide .expand}

- A running ext4 guest grew to 14 GiB and remained running. Repeating the target preserved its QEMU PID; a 13 GiB shrink failed before mutation.
- A stopped XFS guest grew to 14 GiB and returned to stopped. Repeating the target preserved the root file's modification time.
- Injecting a resize2fs failure left the ext4 disk and partition enlarged for an 18 GiB target while the filesystem stayed at 17,045,630,976 bytes. The journal retained `guest`; restoring the tool and repeating 18 GiB completed expansion.
- During growth to 20 GiB, a host tool killed the Barn CLI after actual image expansion. The image was already 21,474,836,480 bytes, the journal remained `image`, and the VM was stopped. Retrying restored running state and verified a filesystem capacity of 21,340,598,272 bytes.
- VM UUID, generation, disk serial, filesystem UUID, PARTUUID, SSH host public key, and the SHA-256 of a prewritten 1 MiB random data file were retained throughout.

Debian 13 also uses systemd-growfs at boot. The failure test disabled automatic growth with `/etc/growroot-disabled` and masked `systemd-growfs-root.service` in the disposable guest, proving Barn's script can complete growth independently. A separate case verified recovery when boot services had already grown the filesystem but a guest command failed. Test nodes were destroyed; the host's six existing QEMU processes and arguments were preserved, and host networking was unchanged. Linux hosts, amd64 guests, and MBR layouts were not replayed on real VMs in this round.

## Code and checks {#implementation}

[Recovery orchestration](https://github.com/pgsty/barn/blob/main/internal/private/root_resize.go) holds the deployment lock and reuses existing start, stop, and process identity checks. The [guest script](https://github.com/pgsty/barn/blob/main/internal/private/root_resize_guest.py) validates layout, identity, and capacity. The [recovery record](https://github.com/pgsty/barn/blob/main/internal/state/root_resize.go) is written atomically with node state. The [disk layer](https://github.com/pgsty/barn/blob/main/internal/disk/disk.go) grows qcow2 only while offline.

[Failure-boundary tests](https://github.com/pgsty/barn/blob/main/internal/private/root_resize_test.go) cover lost responses before and after side effects, retries, shrink rejection, node selection, capacity committed before completion, and identity/capacity failures. CLI regressions cover `-D/BARN_DISK`, retry inputs, recovery hints for stopped nodes, and SPEC/ROOT output. Delivery checks use source `make check` and site `make check`.

Offline image mutation and subsequent guest partition/filesystem expansion follow [QEMU's disk tool documentation](https://www.qemu.org/docs/master/tools/qemu-img.html). The growpart no-change exit code follows the [cloud-utils manual](https://github.com/canonical/cloud-utils/blob/main/man/growpart.1). Online QMP growth and additional root layouts require separate design and acceptance.
