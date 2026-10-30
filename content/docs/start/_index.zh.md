---
title: 使用指南
linkTitle: 使用指南
description: 安装 Barn，启动 Linux 或 macOS 虚拟机，再按需管理机器、文件、镜像与自动化。
weight: 10
icon: fa-solid fa-rocket
no_list: true
cascade:
  type: docs
---

本章节指南面向 **Barn 0.9.2**，并明确标注[未发布变更](../about/unreleased/)。你可以在同一台 Apple Silicon Mac 上同时使用 Linux 实验环境与 macOS 虚拟机，两套流程在 `~/.barn` 下各自独立管理虚拟机。

## 快速上手

- [安装 Barn](installation/) — 在 macOS 或 Linux 上安装 `0.9.2` CLI，核对宿主软硬件要求并了解版本升级方式。
- [Linux 快速上手](tutorial/) — 启动单节点 Ubuntu 24.04 虚拟机，通过 SSH 登录，并用一份 `barn.yml` 扩展为多节点固定 IP 实验环境。
- [macOS 虚拟机](macos/) — 在 Apple Silicon 上创建和管理 macOS 27 虚拟机，使用原生桌面、SSH、共享目录与剪贴板同步。
{.cards}

## Linux 实验环境日常运维

- [日常管理](operations/) — 查看状态、启停节点、用 `plan` 预览清单差异，以及按需执行 `recreate` 或 `destroy`。
- [存储与访问](storage/) — 配置持久测试数据盘、通过 SSH 传输文件与转发端口，或挂载 Virtio-9p 宿主共享目录。
- [镜像仓库](images/) — 选择 9 大发行版家族镜像、切换中国镜像站、构建静态镜像仓库或导入本地 `qcow2` 镜像。
- [自动化](automation/) — 执行无人值守宿主初始化、用 `jq` 校验 `--json` 结果、通过 `barn provision` 批量运行脚本并配合 Pigsty 使用。
{.cards}

## 故障排查、源码构建与清理

- [故障排查](troubleshooting/) — 针对宿主依赖、私网修复、客机阶段警告、SSH 密钥与中断恢复的排查手册。
- [从源码构建](source-build/) — 从 `v0.9.2` 标签编译 CLI、`barn-hosts-helper` 与原生应用包 `Barn.app`，并运行贡献者检查。
- [卸载与清理](uninstall/) — 按序销毁 Linux 与 macOS 虚拟机、清理镜像缓存、卸载宿主网络并移除 Barn 程序。
{.cards}
