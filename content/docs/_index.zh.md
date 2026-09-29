---
title: Farrow 文档
linkTitle: 文档
description: 两条命令启动 Farrow，再按需查阅管理、配置与命令契约。
weight: 10
icon: fa-solid fa-book
cascade:
  type: docs
---

Farrow 把一份 Pigsty 兼容的 Inventory 启动成固定 IP 的 QEMU 虚拟机。每个 Unix
用户只有一套 deployment，状态位于 `~/.farrow`，因此生命周期与 SSH 命令可在任意
目录运行。

按任务选择最短路径：

- **[开始使用](start/)**：两条命令启动第一个实验环境，再按需管理与排障。
- **[参考](reference/)**：Inventory 字段、命令、参数、输出与退出码。
- **[关于](about/)**：设计、真机验证、已知限制与发布门禁。

新手先按[快速上手](start/tutorial/)安装 Farrow 0.8.0。安装后，正常路径为 `farrow up`
启动环境，`farrow ssh` 进入虚拟机。

> [!IMPORTANT]
> 2026-09-26 核对的版本基线：公开版是 **0.8.0**，本次审查的本地源码
> `b91ec37` 是**未发布的 0.9 候选**。仅候选版具备的变化会在对应页面标明。
> 详见[基线与验证记录](about/status/#documentation-baseline)。
