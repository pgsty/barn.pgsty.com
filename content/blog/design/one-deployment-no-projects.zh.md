---
title: "为什么 Farrow 没有 Project"
linkTitle: "单 Deployment，无 Project"
description: "为什么 Farrow 用一份 Pigsty Inventory 驱动一个 Owner-scope Deployment，取代按目录组织的 Project 状态。"
date: 2026-08-27T19:00:00+08:00
weight: 10
categories: [设计]
tags: [架构, Inventory, 状态]
icon: fa-solid fa-layer-group
lastmod: 2026-09-26
---

> [!NOTE]
> **2026-09-26 校准：** 保留原始写作日期；下文已按当前实现更新。公开版本与未发布候选的
> 边界见[当前状态](/zh/docs/about/status/)，不以本文日期代替发布或验收日期。

Farrow 最初采用了一套很熟悉的虚拟机管理器抽象：工作目录就是 Project，隐藏 Marker 提供
身份，注册表负责重新发现 Project，宿主全局 Lease 防止它们争用私有网络。这种模型可以承载
多套彼此独立的虚拟机，但它并不适合 Farrow 最终要成为的产品。

Farrow 不是通用 Hypervisor 前端，而是一套本地、固定 IP 的 Pigsty 实验室。操作者本来就有
一份完整描述：Pigsty Inventory。再加入第二份 VM Manifest 与第二套 Project 身份，只会让
每个普通问题变复杂。

> [!NOTE]
> **决策状态：当前有效。** 本文解释产品模型；当前文件名、字段与命令以
> [配置参考](/zh/docs/reference/configuration/)为准。

旧抽象会把普通问题转化为 Project 管理问题：

- 节点名称和地址究竟以哪份文件为准？
- 移动目录代表移动实验室，还是创建新实验室？
- Marker 还在、注册表丢了怎么办？
- 目录消失代表废弃 Project，还是移动硬盘暂时没有挂载？
- 唯一的宿主私有网络归哪个 Project 所有？

这些都是合理的多 Project 问题。Farrow 的选择是不再制造它们。

## 一份 Inventory 已经足够

交给 Pigsty 的 Inventory 同时就是 Farrow 的期望状态。Farrow 只读取一个很小、明确记录的
边界：Host 地址、少量 Pigsty 原生身份字段，以及 `vm_*` 命名空间。命名空间内部严格校验，
Inventory 的其余部分保持不透明，原样留给 Pigsty。

这种不对称很重要。`vm_mem` 拼错必须报错，因为它会改变 Farrow 创建的机器；新增一项
PostgreSQL 调优参数却不应该因为 VM 层从未见过而失败。于是同一份文件可以继续作为 Pigsty
Inventory 演进，而不会暗中变成第二种 Farrow 配置格式。

命名遵循同一原则：优先使用 `nodename`，其次按 Pigsty Cluster/Sequence 稳定派生，最后才
回退到地址尾段。Farrow 不再增加一个可能与 Pigsty Hostname 冲突的 `vm_name`。

## 一个 Owner-scope 状态根

应用状态位于 `FARROW_HOME`，默认是 `~/.farrow`。工作目录里没有 Marker，也没有按目录维护
的注册表。只读取应用状态的命令可以从任何目录运行；提出新期望状态的命令才需要发现或显式
接收 Inventory。

这里的“一个 Deployment”是 Owner-scope，而不是 root 强制的整机单例。每个 Unix 用户拥有
独立状态根。Farrow 面向可信开发工作站，不承诺共享服务器上的敌对用户仲裁。

这项简化带来直接结果：

- 移动或重命名源码目录不会改变 Deployment 身份；
- Inventory 丢失不会擦除已经应用的状态；
- 清理通过显式生命周期命令完成；删除状态目录不能替代停止 VM 或移除托管集成；
- 镜像缓存、密钥、节点、磁盘、锁与 Deployment 状态集中在同一个可检查的 Home 中；
  短 QMP/PID 路径、SSH 客户端集成与宿主全局网络仍有各自的托管位置，完整清理见
  [卸载](/zh/docs/start/uninstall/)。

## 配置缺席不是操作意图

单 Deployment 并不意味着 Inventory 可有可无，而是让 Farrow 可以区分“期望配置”与“已应用
证据”。需要期望状态时，命令契约允许的场景可以回退到已有 Deployment 的 Applied Spec；
文件缺失永远不会被理解成删除节点的请求。

这条规则贯穿生命周期的每一层：[规划与删除必须显式](/zh/blog/design/convergence-without-surprise/)，
恢复流程也会保留有歧义的资源，而不是猜测用户意图。

## 这是刻意接受的取舍

Farrow 不支持同一用户同时运行多套 Deployment。Project、注册表与地址级 Lease 不是藏起来
等待未来开启的功能；它们被明确否决，因为会重新引入产品刚刚删除的抽象。

如果需求变成多租户或多宿主编排，那已经是另一个产品边界。对本地 Pigsty 实验室而言，一份
Inventory 与一个 Deployment 能让地址、属主、Drift、恢复和清理都更容易解释，也更容易证明。

下一篇：[为什么每个 Farrow 节点都有两张网卡](/zh/blog/design/fixed-ip-two-nics/)。
