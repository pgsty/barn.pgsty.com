---
title: Barn 文档
linkTitle: 文档
description: 安装 Barn 0.9.0，创建第一台 Linux 或 macOS 虚拟机，再按任务查阅使用指南与参考。
weight: 10
icon: fa-solid fa-book
cascade:
  type: docs
---

Barn 用于创建本地开发与测试虚拟机。本文档适用于 **Barn 0.9.0**。
先[安装 Barn](start/installation/)，再选择你需要的客机：

| 我想要…… | 从这里开始 | 所需环境 |
|---|---|---|
| 运行 Linux 虚拟机或多节点实验环境 | [Linux 快速上手](start/tutorial/) | macOS 或 Linux 宿主；Barn 可准备 QEMU 与网络 |
| 运行带桌面和 SSH 的 macOS | [macOS 虚拟机](start/macos/) | Apple Silicon、macOS 27+ 和 Barn Mac 原生组件 |

Linux 环境使用兼容 Ansible 的 YAML 主机清单，如 `barn.yml` 或 `pigsty.yml`，
每个用户管理一套实验环境。`barn mac` 则独立管理多台命名的 macOS 虚拟机。
两者默认都将状态保存在 `~/.barn` 下，切换工作目录不会新建环境。

## 创建虚拟机之后

- **完成日常工作：**[启停与变更](start/operations/)、[文件传输和服务访问](start/storage/)、[选择镜像](start/images/)、[编写自动化](start/automation/)。
- **查找具体用法：**[Linux 配置](reference/configuration/)、[命令行参数](reference/cli/)、[Mac 命令](reference/mac/)。
- **解决问题：**[故障排查](start/troubleshooting/)、[平台与限制](about/status/)，或[报告问题](https://github.com/pgsty/barn/issues)。

想进一步了解项目，可以阅读 [0.9.0 发布说明](../blog/release/0.9.0/)、
[设计说明](about/design/)与[源码构建指南](start/source-build/)。
