---
title: 平台与限制
linkTitle: 平台与限制
description: Barn 0.9.2 的宿主要求、Linux 镜像兼容性、macOS 运行条件与存储限制。
weight: 10
icon: fa-solid fa-laptop-code
---

Barn 专为**本地开发与测试**设计。在搭建实验环境前，可通过本页核对宿主软硬件要求及两类客机的支持范围。

## 版本 {#documentation-baseline}

当前文档对应 **Barn 0.9.2**（安装方式与版本变更详见[安装指南](../../start/installation/)与 [0.9.2 发布说明](/zh/blog/release/0.9.2/)）。可通过 `barn version` 查看本地安装版本；Linux 镜像目录通过 `barn update` 独立更新。

- **预发布渠道**：[Barn 0.9.2](https://github.com/pgsty/barn/releases/tag/v0.9.2) 于 2026-10-30 通过 Barn `0.x` 使用的 GitHub pre-release 渠道发布；使用安装脚本下载时请显式传入 `BARN_VERSION=0.9.2`。
- **macOS 原生组件**：Darwin arm64 归档与 Apple Silicon Homebrew 安装均包含经过签名、公证的 `Barn.app` 及配套 CLI/helper，无需安装 Go 或 Xcode，详见 [macOS 客机指南](../../start/macos/#install)。
- **未发布变更**：源码提交 `27f17bb` 的路径、共享、节点选择与上限调整尚未包含在 0.9.2 中，集中说明见[未发布变更](../unreleased/)。
- **历史验证记录**：早期版本的真机验收与测试记录归档在[验证历史](../history/)中。

## Linux 客机

| 宿主 | 架构 | 原生加速 | 最低 QEMU 版本 |
|---|---|---|---|
| macOS | `arm64`（Apple Silicon）、`amd64`（Intel） | HVF | `8.2.1` |
| Linux | `amd64`、`arm64` | KVM | `6.2` |
{.platform-table}

Barn 为上述四个平台构建发行二进制，真机虚拟化测试主要覆盖 `darwin/arm64` 与 `linux/amd64`。Linux 宿主需要可访问的 `/dev/kvm` 以及 NetworkManager 或 `systemd-networkd`。可运行 `barn doctor` 检查宿主环境，或用 `barn setup --dry-run` 预览依赖安装与网络配置计划。

Barn 0.9.2 内置镜像目录 `2026093001` 提供 **9 个发行版系列、41 个镜像产物**：Ubuntu 22.04/24.04/26.04 LTS、Debian 12/13、Rocky Linux 8/9/10 与 CentOS 7（具体版本号见[镜像参考](../../reference/images/)）：

- **Unreleased 源码**：每位用户管理一套 Linux 部署，使用私有 RFC1918 `/24` 网段，不再另设 20 节点上限。
- 跨架构客机使用 QEMU TCG 软件模拟；Rocky Linux 8 `arm64` 因采用与 Apple HVF 不兼容的 64 KiB 页大小内核，在 Apple Silicon 上同样自动使用 TCG。
- CentOS 7（`el7`）为 `deprecated`（已弃用）兼容镜像，仅支持在 `linux/amd64` 宿主上原生运行。
- **Unreleased 源码**：`vm_shares`（QEMU Virtio-9p）支持 Linux 与 macOS 宿主，要求 QEMU 与客机内核支持 9p。Barn 0.9.2 在 macOS 宿主上仍需通过 SSH/SCP/rsync 与 Linux 客机交换文件。

## macOS 客机 {#macos-guests}

`barn mac` 需要 **Apple Silicon 芯片、macOS 27 或更高版本、已登录的图形桌面会话以及 `Barn.app` 原生组件**。客机基于 Apple `Virtualization.framework` 运行 macOS 27，不依赖 QEMU 或 Linux 宿主网络（详见[macOS 客机指南](../../start/macos/)）：

- **磁盘空间**：准备首台 macOS 虚拟机约需 65 GiB 可用空间，用于存放 `.ipsw` 恢复镜像、未启动过的基础镜像及虚拟机的 APFS 写时复制克隆。下载支持断点续传，也可通过 `--ipsw` 指定本地恢复镜像。
- **并发上限**：受 Apple 虚拟化框架限制，每台 Mac 最多同时运行两台 macOS 虚拟机（跨所有虚拟化工具及正在安装的基础镜像统一计数）；已停止的虚拟机数量不受此限制。
- **隔离与共享**：每台虚拟机拥有独立的私有 `/24` NAT 子网、SSH 密钥、登录密码和 APFS 克隆磁盘，支持 VirtioFS 目录共享（`--share`）与纯文本剪贴板同步。
- **能力边界**：不支持 USB 透传、虚拟机快照与挂起恢复；虚拟机内的 Apple 账户登录可能受系统限制。

请使用 `barn mac doctor` 与 `barn mac ls` 检查和管理 Mac 虚拟机；顶层 `barn status`、`destroy` 与 `purge` 仅作用于 Linux 实验环境。

## 数据与生命周期

请将重要代码与数据保存在宿主目录或版本库中：

- **Linux 实验环境**：`barn recreate` 会替换根盘与非持久数据盘并保留 `persistent: true` 的持久盘；`barn destroy` 会删除根盘与非持久盘；客机恢复流程在遇到无法识别或确认损坏的数据盘文件系统时会自动重格式化（详见[存储与访问](../../start/storage/)）。
- **macOS 虚拟机**：`barn mac recreate` 会用基础镜像的全新克隆替换客机磁盘；`barn mac destroy` 会删除该虚拟机的磁盘、密钥与状态，宿主上的共享源目录保持不变。

日常排障请参考[故障排查](../../start/troubleshooting/)，宿主特权、SSH 凭据与镜像信任边界请参考[安全与信任](../security/)，源码构建与发布流程请参考[参与贡献](../engineering/)。
