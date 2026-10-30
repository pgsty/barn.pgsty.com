---
title: Barn 文档
linkTitle: 文档
description: 安装 Barn 0.9.2，创建第一台 Linux 或 macOS 虚拟机，并按任务查找指南与参考手册。
weight: 10
icon: fa-solid fa-book
cascade:
  type: docs
---

Barn 用于在本地创建和管理开发测试虚拟机。本文档适用于 **Barn 0.9.2**，尚未发布的行为会标注为 **Unreleased**，详见[未发布变更](about/unreleased/)。可从以下入口快速开始：

- [安装 Barn 0.9.2](start/installation/) — 在 macOS 或 Linux 上通过 Homebrew、固定版本安装脚本或原生软件包安装 CLI。
- [Linux 快速上手](start/tutorial/) — 在 macOS（HVF）或 Linux（KVM）上基于 Ansible YAML 清单启动单节点或多节点固定 IP 实验集群。
- [原生 macOS 虚拟机](start/macos/) — 在 Apple Silicon 上运行相互隔离的 macOS 27+ 虚拟机，提供原生桌面窗口、SSH、VirtioFS 共享目录与剪贴板同步。
{.cards}

## 常见任务

- [日常操作](start/operations/) — 查看状态、启停节点、通过 `plan` 预览配置变更，以及重建或销毁虚拟机。
- [存储与服务访问](start/storage/) — 挂载持久化测试数据盘、配置 Virtio-9p 宿主共享目录与访问客机端口。
- [镜像与仓库](start/images/) — 从 9 个 Linux 发行版系中选择镜像、切换国内加速源或导入自定义 `qcow2` 镜像。
- [脚本与自动化](start/automation/) — 使用 `--yes`、`--json` 与结构化退出码在脚本或 CI 中驱动 Barn。
- [故障排查](start/troubleshooting/) — 使用 `barn doctor` 诊断宿主机依赖、桥接网络、SSH 密钥与中断操作。
- [0.9.2 版本更新](../blog/release/0.9.2/) — 了解随包提供的 macOS 原生 App、SSH/exec 命令规范与升级步骤。
{.cards}

## 按栏目浏览
