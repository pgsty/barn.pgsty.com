---
title: Barn 文档
linkTitle: 文档
description: 安装 Barn 0.9.1，创建第一台 Linux 或 macOS 虚拟机，再按任务查阅使用指南与参考。
weight: 10
icon: fa-solid fa-book
cascade:
  type: docs
---

Barn 用于创建本地开发与测试用的虚拟机。本文档面向 **Barn 0.9.1**。
先[安装 Barn](start/installation/)，再选择你需要的客机：

| 我想要…… | 从这里开始 | 所需环境 |
|---|---|---|
| 运行 Linux 虚拟机或多节点实验环境 | [Linux 快速上手](start/tutorial/) | macOS 或 Linux 宿主；Barn 可准备 QEMU 与网络 |
| 运行带桌面和 SSH 的 macOS | [macOS 虚拟机](start/macos/) | Apple Silicon、macOS 27+ 和 Barn.app 原生组件 |

对于 Linux，用兼容 Ansible 的 YAML 清单定义节点，如 `barn.yml` 或 `pigsty.yml`。
每个用户管理一套 Linux 实验环境，与工作目录无关。对于 macOS，用 `barn mac` 按名称管理每台虚拟机。
两类虚拟机的状态默认都保存在 `~/.barn` 下。

## 创建虚拟机之后

- 日常操作见[启停与变更](start/operations/)、[文件传输和服务访问](start/storage/)、[选择镜像](start/images/)、[编写自动化](start/automation/)。
- 具体设置见[Linux 配置](reference/configuration/)、[命令行参数](reference/cli/)、[Mac 命令](reference/mac/)。
- 排查问题见[故障排查](start/troubleshooting/)、[平台与限制](about/status/)，或[报告问题](https://github.com/pgsty/barn/issues)。

版本变化见 [0.9.1 发布说明](../blog/release/0.9.1/)。
实现与构建方法见[设计说明](about/design/)和[源码构建指南](start/source-build/)。
