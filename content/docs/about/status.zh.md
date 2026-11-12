---
title: 平台与限制
linkTitle: 平台与限制
description: Barn 1.2.0 的宿主要求、Linux 镜像兼容性、macOS 运行条件与存储限制。
weight: 10
icon: fa-solid fa-laptop-code
---

Barn 专为 **本地开发与测试** 设计。在搭建实验环境前，可通过本页核对宿主软硬件要求及两类客机的支持范围。

## 版本 {#documentation-baseline}

当前文档对应稳定版 **Barn 1.2.0**（安装方式与版本变更详见[安装指南](../../start/installation/)与 [1.2.0 发布说明](/zh/blog/release/1.2.0/)）。可通过 `barn version` 查看本地安装版本；Linux 镜像目录通过 `barn update` 独立更新。

- **稳定版渠道**：[Barn 1.2.0](https://github.com/pgsty/barn/releases/tag/v1.2.0) 于 2026-11-12 作为 GitHub 正式版发布，`releases/latest`、不带 `BARN_VERSION` 的下载安装器与 Homebrew 配方都会选择此版本，DEB 与 RPM 软件包从发布页下载；需要固定版本时设置 `BARN_VERSION=1.2.0`。
- **macOS 原生组件**：Darwin arm64 归档与 Apple Silicon Homebrew 安装均包含经过签名、公证的 `Barn.app` 及配套 CLI/helper，无需安装 Go 或 Xcode，详见 [macOS 客机指南](../../start/macos/#install)。
- **1.2.0 变更**：新增规格与环境变量覆盖、可恢复的根盘扩容、生命周期 `--parallel` 和清单 hosts 发布。Linux 默认规格改为 1 vCPU / 2 GiB；显式设置 `vm_cpu: 2`、`vm_mem: 4GiB` 可保留 1.1.0 的默认值。已应用 VM 的资源会保留到显式执行资源变更操作为止。
- **历史验证记录**：历次真机验收与测试记录归档在[验证历史](../history/)与 [Barn 1.1.0 本机完整验收](../local-acceptance-1.1.0/)中。

选项可用范围见[版本基线](../../reference/commands/#versions)，发布证据见 [1.2.0 验收记录](/zh/blog/design/release-1-2-0-readiness/)。

## Linux 客机 {#linux-guests}

| 宿主 | 架构 | 原生加速 | 最低 QEMU 版本 |
|---|---|---|---|
| macOS | `arm64`（Apple Silicon）、`amd64`（Intel） | HVF | `8.2.1` |
| Linux | `amd64`、`arm64` | KVM | `6.2` |
{.platform-table .wide .expand}

Barn 为上述四个平台构建发行二进制，真机虚拟化测试主要覆盖 `darwin/arm64` 与 `linux/amd64`。Linux 宿主需要可访问的 `/dev/kvm` 以及 NetworkManager 或 `systemd-networkd`。可运行 `barn doctor` 检查宿主环境，或用 `barn setup --dry-run` 预览依赖安装与网络配置计划。

Barn 1.2.0 内置镜像目录 revision `2026110502` 提供 **9 个发行版系列、17 个镜像产物**，默认镜像为 `u24:stable`：Ubuntu 22.04/24.04/26.04 LTS、Debian 12/13、Rocky Linux 8/9/10 与 CentOS 7（具体版本号见[镜像参考](../../reference/images/)）：

- 每位用户管理一套 Linux 部署，使用私有 RFC1918 `/24` 网段；节点数量只受网段可用地址与宿主资源限制。
- 跨架构客机使用 QEMU TCG 软件模拟；Rocky Linux 8 `arm64` 因采用与 Apple HVF 不兼容的 64 KiB 页大小内核，在 Apple Silicon 上同样自动使用 TCG。
- CentOS 7（`el7`）为 `deprecated`（已弃用）兼容镜像，仅支持在 `linux/amd64` 宿主上原生运行。
- `vm_shares`（QEMU Virtio-9p）支持 Linux 与 macOS 宿主，要求 QEMU 与客机内核支持 9p。若客机内核不支持 9p，仍可使用 SSH/SCP/rsync。

## macOS 客机 {#macos-guests}

`barn mac` 需要 **Apple Silicon 芯片、macOS 27 或更高版本、已登录的图形桌面会话以及 `Barn.app` 原生组件**。客机基于 Apple `Virtualization.framework` 运行 macOS 27，不依赖 QEMU 或 Linux 宿主网络（详见[macOS 客机指南](../../start/macos/)）：

- **磁盘空间**：准备首台 macOS 虚拟机约需 65 GiB 可用空间，用于存放 `.ipsw` 恢复镜像、未启动过的基础镜像及虚拟机的 APFS 写时复制克隆。下载支持断点续传，也可通过 `--ipsw` 指定本地恢复镜像。
- **并发上限**：受 Apple 虚拟化框架限制，每台 Mac 最多同时运行两台 macOS 虚拟机（跨所有虚拟化工具及正在安装的基础镜像统一计数）；已停止的虚拟机数量不受此限制。
- **隔离与共享**：每台虚拟机拥有独立的私有 `/24` NAT 子网、SSH 密钥、登录密码和 APFS 克隆磁盘，支持 VirtioFS 目录共享（`--share`）与纯文本剪贴板同步。
- **能力边界**：不支持 USB 透传、虚拟机快照与挂起恢复；虚拟机内的 Apple 账户登录可能受系统限制。
- **Mac 状态损坏**：恢复日志损坏时，`barn mac image ls`、`barn mac doctor` 的空间估算与镜像清理会失败，直到日志修复。单台机器的状态无法读取时，`barn mac ls` 会整体失败，其他机器仍可按名称操作。

请使用 `barn mac doctor` 与 `barn mac ls` 检查和管理 Mac 虚拟机；顶层 `barn status`、`destroy` 与 `purge` 仅作用于 Linux 实验环境。

## 数据与生命周期 {#data-and-lifecycle}

请将重要代码与数据保存在宿主目录或版本库中：

- **Linux 实验环境**：`barn recreate` 会替换根盘与非持久数据盘并保留 `persistent: true` 的持久盘，清单缺少已有节点时整套部署 `recreate` 会拒绝执行；`barn destroy` 会删除根盘与非持久盘。恢复客机时，`barn up` 会格式化没有任何签名的数据盘；已有的 ext4 或 XFS 文件系统只有在检查工具报告可识别的损坏时才会重置。带分区表、签名缺少 UUID、使用不支持的文件系统特性或检查工具未知失败的磁盘会保留数据并给出警告（详见[存储与访问](../../start/storage/)）。
- **macOS 虚拟机**：`barn mac recreate` 会用基础镜像的全新克隆替换客机磁盘；`barn mac destroy` 会删除该虚拟机的磁盘、密钥与状态，宿主上的共享源目录保持不变。

日常排障请参考[故障排查](../../start/troubleshooting/)，宿主特权、SSH 凭据与镜像信任边界请参考[安全与信任](../security/)，源码构建与发布流程请参考[参与贡献](../engineering/)。
