---
title: 平台与限制
linkTitle: 平台与限制
description: Barn 0.9.0 的宿主要求、Linux 镜像兼容性、macOS 运行条件与存储限制。
weight: 10
icon: fa-solid fa-laptop-code
---

Barn 面向**本地开发与测试**。本页帮助你选择宿主，并了解两类客机各自的支持范围。

## 版本 {#documentation-baseline}

本文档适用于 **Barn 0.9.0**。请[安装发行版本](../../start/installation/)，用
`barn version` 核对版本，通过[发布说明](/zh/blog/release/0.9.0/)了解变化。
Linux 镜像目录通过 `barn update` 独立更新。

## Linux 客机

| 宿主 | 架构 | 原生加速 | 最低 QEMU 版本 |
|---|---|---|---|
| macOS | arm64（Apple Silicon）、amd64（Intel） | HVF | 8.2.1 |
| Linux | amd64、arm64 | KVM | 6.2 |
{.platform-table}

Barn 为以上四个目标提供构建。主要原生测试路径为 macOS arm64 和 Linux amd64，
Intel macOS 与 Linux arm64 的验证覆盖相对较少。Linux 还需要可用的 `/dev/kvm`，
以及 NetworkManager 或 systemd-networkd。`barn doctor` 检查宿主，
`barn setup --dry-run` 展示当前机器需要的依赖和网络变更。

内置镜像目录包含 **9 个系列、41 个镜像文件**：Ubuntu 22.04/24.04/26.04、
Debian 12/13、Rocky Linux 8/9/10 与 CentOS 7。准确版本与兼容范围见[镜像参考](../../reference/images/)。

- 每个用户管理一套 Linux 部署，在同一个私有 `/24` 网段中支持 1–20 个节点。
- 跨架构客机使用 QEMU TCG 模拟。Rocky Linux 8 arm64 的 64 KiB 内核不兼容 HVF，
  因此在 Apple Silicon 上也使用 TCG。
- CentOS 7 是已弃用的兼容镜像，仅支持 Linux/amd64 原生运行。
- `vm_shares` 支持 Linux 宿主。在 macOS 宿主上运行 Linux 客机时，请使用 SSH
  传输文件；受路径保护的 QEMU 9p 共享方式会阻止这些节点启动。

## macOS 客机 {#macos-guests}

`barn mac` 需要 **Apple Silicon、macOS 27 或更高版本、已登录的桌面会话，以及
Barn Mac 原生组件**。客机运行 macOS 27，无需 QEMU 或 Linux 宿主网络。
具体操作见 [Mac 教程](../../start/macos/)。

- 首台机器约需 65 GiB 可用空间，用于恢复镜像、已安装的基础系统与初始写入。
  下载支持断点续传，也可以使用本地 IPSW。
- 每台 Mac 最多同时运行两台 macOS 虚拟机，包含其他工具与 macOS 安装过程。
  可以保留更多已停止的机器。
- 每台机器有独立的私有子网、SSH 密钥、登录密码与磁盘。共享目录使用 VirtioFS，
  与 Linux 的 `vm_shares` 相互独立。
- 剪贴板只共享纯文本，不共享图片或文件。
- 不支持 USB 透传、快照与挂起恢复。虚拟机中的 Apple 账户登录可能不稳定。

使用 `barn mac doctor` 诊断 Mac 环境，使用 `barn mac ls` 查看机器。
`barn status`、`destroy` 与 `purge` 只操作 Linux 部署。

## 数据与生命周期

请在实验环境之外备份重要文件。Linux 的 `recreate` 会替换根盘与非持久数据盘，
`destroy` 会删除它们。持久盘可在普通销毁后保留，但客机恢复仍可能清空重建损坏或无法
识别的数据文件系统。完整规则见[存储与访问](../../start/storage/)。

Mac 的 `recreate` 用新的克隆磁盘替换客机磁盘，`destroy` 删除机器的磁盘、凭据与设置；
宿主上的共享目录保持原样。

操作问题见[故障排查](../../start/troubleshooting/)；源码与发布验证流程见[参与贡献](../engineering/)。
