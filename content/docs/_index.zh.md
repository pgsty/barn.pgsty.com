---
title: Barn 文档
linkTitle: 文档
description: 安装 Barn 1.0.0，创建第一台 Linux 或 macOS 虚拟机，并按任务查找指南与参考手册。
weight: 10
icon: fa-solid fa-book
cascade:
  type: docs
---

Barn 用于在本地创建和管理开发测试虚拟机。本文档适用于首个稳定版 **Barn 1.0.0**，相对 0.9.3 的变化见 [1.0.0 发布说明](../blog/release/1.0.0/)。可从以下入口快速开始：

- [安装 Barn 1.0.0](start/installation/) — 在 macOS 或 Linux 上通过 Homebrew、发布安装脚本或原生软件包安装 CLI。
- [Linux 快速上手](start/tutorial/) — 在 macOS（HVF）或 Linux（KVM）上基于 Ansible YAML 清单启动单节点或多节点固定 IP 实验集群。
- [原生 macOS 虚拟机](start/macos/) — 在 Apple Silicon 上运行相互隔离的 macOS 27+ 虚拟机，提供原生桌面窗口、SSH、VirtioFS 共享目录与剪贴板同步。
{.cards}

## 常见任务

- [日常操作](start/operations/) — 查看状态、启停节点、通过 `plan` 预览配置变更，以及重建或销毁虚拟机。
- [存储与服务访问](start/storage/) — 挂载持久化测试数据盘、配置 Virtio-9p 宿主共享目录与访问客机端口。
- [镜像与仓库](start/images/) — 从 9 个 Linux 发行版系中选择镜像、更新镜像目录或导入自定义 `qcow2` 镜像。
- [脚本与自动化](start/automation/) — 使用 `--yes`、`--json` 与结构化退出码在脚本或 CI 中驱动 Barn。
- [故障排查](start/troubleshooting/) — 使用 `barn doctor` 诊断宿主就绪状态、网络、SSH 与中断的生命周期操作。
- [1.0.0 版本更新](../blog/release/1.0.0/) — 了解 1.x 兼容性范围、更安全的重建与数据盘恢复、新增确认流程与升级步骤。
{.cards}

## 按栏目浏览
