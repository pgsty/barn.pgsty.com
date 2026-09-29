---
title: Barn 文档
linkTitle: 文档
description: 两条命令启动 Barn，再按需查阅管理、配置与命令契约。
weight: 10
icon: fa-solid fa-book
cascade:
  type: docs
---

Barn 把一份 Pigsty 兼容的 Inventory 启动成固定 IP 的 QEMU 虚拟机。每个 Unix
用户只有一套 deployment，状态位于 `~/.barn`，因此生命周期与 SSH 命令可在任意
目录运行。

按任务选择最短路径：

- **[开始使用](start/)**：两条命令启动第一个实验环境，再按需管理与排障。
- **[参考](reference/)**：Inventory 字段、命令、参数、输出与退出码。
- **[关于](about/)**：设计、真机验证、已知限制与发布门禁。

新手先按[快速上手](start/tutorial/)从源码准备 **Barn 0.9.0 发布候选**。
CLI 就绪后，用 `barn up` 启动实验环境，用 `barn ssh` 进入虚拟机。

> [!IMPORTANT]
> Barn 0.9.0 尚未发布。详见[发行与验证状态](about/status/#documentation-baseline)。
