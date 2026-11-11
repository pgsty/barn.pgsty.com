---
title: "根盘原地扩容：恢复协议与真机验收"
linkTitle: "根盘扩容验收"
description: "resize -D 的只增不减契约、停机与客机扩展流程、失败恢复，以及 ext4/XFS 真机验收。"
date: 2026-11-11
lastmod: 2026-11-11
weight: 74
categories: [设计]
tags: [CLI, QEMU, 存储]
icon: fa-solid fa-hard-drive
---

**状态（2026-11-11）**：未发布开发版本已实现 `barn resize -D`，并在 macOS/arm64 的 QEMU/HVF 客机上完成 ext4 与 XFS 验收。已发布 1.1.0 的 resize 仍只修改 CPU/内存。参数优先级见 [VM 规格设计](../vm-resource-overrides/)，命令契约见 [根盘扩容](/zh/docs/reference/cli/#root-disk-growth)。

## 使用范围 {#scope}

```bash
barn resize -D 128GiB meta
BARN_DISK=128GiB barn resize meta
```

目标是根盘的绝对容量，支持扩容，不支持缩盘。已完成的同目标操作不修改镜像，也不重启 VM。CPU/内存变更可以与根盘扩容一起提交，scale 不乘磁盘。镜像、架构、数据盘、网络及共享目录的变更仍需显式重建。

MBR 的目标容量不能超过 2 TiB。首版支持普通 ext4/XFS 根分区：逻辑扇区为 512 字节，分区表为 GPT 或主 MBR，根分区位于物理末端且与其他分区不重叠。LVM、加密根设备、后置分区及缺失的客机工具会在修改镜像前被拒绝。检查使用磁盘序列号、UUID、PARTUUID、分区编号和起始位置绑定原设备；不会格式化磁盘或重建分区。

原本运行的节点会停机扩盘，再恢复运行。原本停机的节点需临时启动检查客机布局，停机扩盘，再启动完成文件系统扩展，最后恢复停机。整个流程持有部署锁，其他生命周期操作不能在镜像修改期间启动 QEMU。

## 恢复协议 {#recovery}

节点状态中的 `root_resize` 保存原容量、目标容量、原开关机状态和客机根分区身份。每次执行都重新读取当前状态，不对已经扩大的值再次加容量。

| 持久阶段 | 下一步 | 中断后的处理 |
|---|---|---|
| `preflight` | 启动或检查客机，探测布局与工具 | 保留原开关机意图，重新探测 |
| `image` | 核验 QEMU 已退出，调用 `qemu-img resize`，核对并同步镜像 | 再次检查实际虚拟容量；已经达到目标就不再增长 |
| `guest` | 对账应用状态，启动并执行 growpart 与 resize2fs/xfs_growfs | 保留已扩展的镜像和分区，继续扩展并核验文件系统 |
| `verified` | 恢复原开关机状态，再清除记录 | 重试状态恢复及最终记录写入 |

预检失败且原开关机状态已恢复时，清除尚未触碰磁盘的记录，允许修正目标。镜像增长前已经持久化 `image`，因此即使 `qemu-img` 成功而 CLI 来不及收到结果，重试也不会丢失目标。元数据写入失败只恢复元数据记录，不会缩小真实磁盘来模拟回滚。应用状态可能已保存新的根盘容量，而客机仍待完成；此时 `status` 和 `plan` 保留待完成提示，重复相同目标的 resize 才会清除记录。修复客机工具或连接问题后按提示重试，不需要另一个 repair 命令。

成功前核对镜像虚拟大小、客机块设备大小、分区末端和文件系统几何容量。ext4 使用块数量乘块大小，XFS 使用数据区块数量乘块大小；不把 `df` 可用空间当成磁盘容量。检查允许分区表尾部和文件系统对齐开销。在线 CPU/内存热插拔的 `resize_incomplete` 标记与根盘恢复记录保持独立。

## 真机验收 {#acceptance}

使用独立的临时 `BARN_HOME`、两台 1c1g 客机和 12 GiB 初始根盘。Debian 13 镜像为 `20261103.2651.1`，Rocky Linux 9 镜像为 `9.8.20260525.2`，均为 arm64。所有数值单位为字节。

| 客机 | 根盘：扩容前 → 后 | 根分区：扩容前 → 后 | 文件系统：扩容前 → 后 |
|---|---|---|---|
| Debian 13 / ext4 | 12,884,901,888 → 15,032,385,536 | 12,750,667,264 → 14,898,150,912 | 12,750,663,680 → 14,898,147,328 |
| Rocky Linux 9 / XFS | 12,884,901,888 → 15,032,385,536 | 11,730,402,816 → 13,877,886,464 | 11,730,399,232 → 13,877,882,880 |
{.wide .expand}

- ext4 从运行状态扩容到 14 GiB 后仍运行；重复目标保持相同 QEMU PID，13 GiB 缩盘请求在修改前拒绝。
- XFS 从停机状态扩容到 14 GiB 后仍停机；重复目标保持根盘文件修改时间不变。
- 在 ext4 的 `resize2fs` 注入失败后，根盘和分区已达到 18 GiB 对应大小，文件系统仍为 17,045,630,976 字节。状态保留 `guest` 阶段；恢复工具并重复 18 GiB 后完成。
- 在下一次增长到 20 GiB 时，让宿主工具在实际扩盘完成后杀死 Barn CLI。此时镜像已是 21,474,836,480 字节，状态仍为 `image`，VM 停机；重试同目标后恢复运行，文件系统达到 21,340,598,272 字节。
- 全程保留 VM UUID、generation、磁盘序列号、文件系统 UUID、PARTUUID、SSH 主机公钥，以及预先写入的 1 MiB 随机数据的 SHA-256。

Debian 13 的 systemd-growfs 也会在启动时扩展根文件系统。故障验收通过 `/etc/growroot-disabled` 及屏蔽测试客机的 `systemd-growfs-root.service` 关闭自动路径，确认 Barn 的扩展脚本独立完成；另验证了文件系统已被启动服务扩展、但客机命令失败时仍可重试收敛。测试节点已销毁，宿主原有六个 QEMU 进程及启动参数保持不变，宿主网络未改动。Linux 宿主、amd64 客机及 MBR 布局本轮没有真机重放。

## 代码与检查 {#implementation}

[恢复编排](https://github.com/pgsty/barn/blob/main/internal/private/root_resize.go) 持有部署锁并复用已有启动、停止与进程身份核验；[客机脚本](https://github.com/pgsty/barn/blob/main/internal/private/root_resize_guest.py) 做布局、身份及容量校验；[恢复记录](https://github.com/pgsty/barn/blob/main/internal/state/root_resize.go) 随节点状态原子写入；[磁盘层](https://github.com/pgsty/barn/blob/main/internal/disk/disk.go) 只在离线状态增长 qcow2。

[故障边界测试](https://github.com/pgsty/barn/blob/main/internal/private/root_resize_test.go) 覆盖各阶段在副作用前后失去响应、重复执行、缩盘拒绝、节点选择、容量已记账但操作未完成，以及身份和容量验证失败。CLI 回归覆盖 `-D/BARN_DISK`、重试参数、停机节点的恢复提示及 SPEC/ROOT 输出。交付检查使用源码 `make check` 与站点 `make check`。

离线修改镜像及后续扩展客机分区/文件系统的边界依据 [QEMU 磁盘工具文档](https://www.qemu.org/docs/master/tools/qemu-img.html)；growpart 的无变化退出码按 [cloud-utils 手册](https://github.com/canonical/cloud-utils/blob/main/man/growpart.1) 处理。后续在线 QMP 扩盘及其他根布局应单独设计和验收。
