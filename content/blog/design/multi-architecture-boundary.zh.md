---
title: "超越 amd64 与 arm64"
linkTitle: "客机架构契约"
description: "客机架构如何决定 Barn 使用的模拟器、机器类型、固件、设备与验收测试。"
date: 2026-11-08T10:00:00+08:00
weight: 90
categories: [设计]
tags: [架构, QEMU, 镜像]
icon: fa-solid fa-microchip
lastmod: 2026-11-08
---

Barn 当前支持 `amd64` 与 `arm64` Linux 客机。QEMU 可以模拟更多架构，但每个新增 Barn 目标都需要镜像和完整的启动、操作契约。本设计评估复核于 **2026-11-08**，区分已有运行时策略与未来候选架构。

## 硬件加速跟随宿主指令集 {#acceleration}

对于 Barn 当前的 64 位客机，原生虚拟化使用宿主指令集：macOS 使用 HVF，Linux 使用 KVM；跨架构客机由 QEMU TCG 翻译指令。Rosetta 可以在 Arm Linux VM 内翻译 Intel Linux 应用，但不能在 Apple Silicon 上提供 Intel Linux VM。详见 [QEMU 模拟说明](https://www.qemu.org/docs/master/about/emulation.html)与 [Apple Linux 二进制翻译指南](https://developer.apple.com/documentation/virtualization/running-intel-binaries-in-linux-vms)。

| 宿主 | amd64 客机 | arm64 客机 | 当前原生运行发布证据 |
|---|---|---|---|
| macOS arm64 | TCG | HVF，受镜像兼容性限制 | Tier1 |
| macOS amd64 | HVF | TCG | Tier2 |
| Linux amd64 | KVM | TCG | Tier1 |
| Linux arm64 | TCG | KVM | Tier2 |
{.wide .expand}

Barn 的 tier 表示发布证据等级。原生 Darwin arm64 与 Linux amd64 有主要的真机验收覆盖；Darwin amd64 和 Linux arm64 在补齐同等真机证据前仍为 Tier2。所有 TCG 配置也属于 Tier2。二进制交叉编译成功，不足以提升运行时的证据等级。

另有两条镜像限制：原版 EL8 arm64 因要求 64 KiB 地址转换粒度，在 Apple Silicon 上使用 TCG；EL7 仅限原生 Linux/amd64。原生加速发生预期外故障时，操作会失败，不会静默改用 TCG。实际策略以 [`platform.go`](https://github.com/pgsty/barn/blob/main/internal/platform/platform.go)和 [`selectRuntime`](https://github.com/pgsty/barn/blob/main/internal/private/manager.go)为准。

## 保留完整的模拟启动配置 {#boot-profile}

现有 arm64 TCG 配置使用 `qemu-system-aarch64`、`virt` 机器与 `cortex-a72`。Barn 的 arm64 镜像需要 UEFI，使用匹配的固件代码和每台 VM 独立可写的变量存储。即使宿主架构不同，也必须安装目标模拟器与固件；Linux setup 当前按宿主架构规划依赖。

arm64 宿主运行 amd64 客机时，Barn 显式使用 `tcg,thread=single`，以保留 x86 更强的内存顺序契约；其他模拟配置使用 `tcg,thread=multi`。因此，增加 vCPU 数量并不总意味着增加翻译线程。

QEMU 的 [`virt` 文档](https://www.qemu.org/docs/master/system/arm/virt.html)将 `cortex-a72` 列为 64 位 CPU，并说明 `max` 模型可能随 QEMU 版本改变。此前 Barn 调查中，一组 `max` 配置停在固件阶段，而使用 `cortex-a72` 和显式 pflash code/vars 的配置成功启动。因为固件参数也变了，这项观察无法单独证明 CPU 模型是原因；应先保留已测试的配置，再通过控制变量的比较调查变更。

客机架构应在清单和目录元数据中显式记录。qcow2 元数据描述磁盘容器，无法识别客机指令集。选择异架构镜像时，镜像架构和运行时配置必须同时匹配。

## 每种新架构都有不同的引导条件 {#targets}

下列是 QEMU 接入候选，还不是 Barn 支持的参数值：

| 候选架构 | QEMU 目标与机器 | 需要建立的启动契约 |
|---|---|---|
| `ppc64le` | `qemu-system-ppc64`、`pseries` | 小端客机；SLOF 或已验证的 VOF/直接内核路径；pSeries 控制台和设备 |
| `s390x` | `qemu-system-s390x`、`s390-ccw-virtio` | CCW/virtio 设备与显式 `bootindex`，替换 PC 式引导假设 |
| `riscv64` | `qemu-system-riscv64`、`virt` | OpenSBI/U-Boot 或已验证的 EFI 路径；设备树、CPU 扩展与串口 |
| `loongarch64` | `qemu-system-loongarch64`、`virt` | 经过验证的 CPU 模型，例如 `la464`，以及匹配的 EDK2 固件和客机镜像 |
{.wide .expand}

机器与引导差异见 QEMU 的 [pSeries](https://www.qemu.org/docs/master/system/ppc/pseries.html)、[s390x 引导设备](https://www.qemu.org/docs/master/system/s390x/bootdevices.html)、[RISC-V virt](https://www.qemu.org/docs/master/system/riscv/virt.html)与 [LoongArch virt](https://www.qemu.org/docs/master/system/loongarch/virt.html)文档。这四种候选在 Barn 当前 amd64/arm64 宿主上都需要 TCG；支持对应指令集的原生 Linux 宿主则是另一项工程。

发行版支持分为正式 CPU 端口、安装介质、根文件系统和通用云盘等层次。候选必须说明实际提供哪一种、固定来源与摘要，以及其引导程序和 cloud-init 配置是否匹配选定的 QEMU 机器。不能替换另一个文件名中的架构来拼出下载地址。候选进入目录前，应先完成[镜像证据核查](/zh/blog/design/image-update-evidence/)。

## 实现边界 {#implementation}

只在架构解析器里增加一个名字，产品的其他部分仍不完整。每个目标都需要协调修改：

- 平台与镜像 schema：规范架构名、别名、校验、目录条目和发布等级。现有目录读取器会拒绝未知字段和不支持的架构，发布方案还需明确旧客户端的兼容策略。
- QEMU 启动参数：可执行文件、机器、CPU、固件/引导方式、控制台、磁盘和网卡传输方式，以及 QMP 身份。
- 客机初始化：seed 交付、用户和密钥、网卡命名、数据盘识别与文件系统支持。
- 宿主准备：依赖包、最低 QEMU 能力、预检诊断和可用固件。
- 生命周期操作：冷启动、SSH 就绪、启停、resize 能力、持久盘、重建、取消与中断恢复。

现有实现入口包括 [`internal/platform`](https://github.com/pgsty/barn/tree/main/internal/platform)、[`internal/qemu`](https://github.com/pgsty/barn/tree/main/internal/qemu)、[`internal/cloudinit`](https://github.com/pgsty/barn/tree/main/internal/cloudinit)、[`internal/setup`](https://github.com/pgsty/barn/tree/main/internal/setup)和[镜像流水线](https://github.com/pgsty/barn/tree/main/packaging/image-pipeline)。

## 新增架构的验收 {#acceptance}

每个候选先选一份通用云镜像，记录来源、摘要、QEMU 版本、完整启动配置与固件。在全新临时数据目录中检查冷启动、预期的 `uname -m`、SSH 身份、出站流量、宿主访问、客机互通、数据挂载和重启，再测试 recreate/destroy 边界、持久盘保留和取消后的恢复。不支持的可选功能应给出明确诊断。

研究建议先评估 ppc64le 与 s390x，再评估 riscv64 和 loongarch64。这个顺序是依据镜像供给与启动接入工作量提出的工程假设，不是已承诺的路线图；更成熟的镜像或明确用户负载都可以改变顺序。

功能兼容和性能要分别测量。TCG 适合安装、打包和架构检查；数据库吞吐与编译基准需要在有代表性的原生硬件上测量，才能用于容量判断。
