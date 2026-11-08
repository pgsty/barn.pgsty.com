---
title: 设计随笔
linkTitle: 设计
description: Barn 背后的架构决策、方案取舍与实现边界。
weight: 20
icon: fa-solid fa-pen-ruler
blog_index: cards
blog_index_columns: 2
blog_index_toggle: true
featured_image: wash
cascade:
  featured_image: wash
  reading_time: true
  toc_taxonomies: false
---

这里记录 Barn 的状态模型、客机收敛、镜像信任、宿主网络、[CLI 契约](cli-contracts/)与[原生 Mac 生命周期](native-mac-lifecycle/)，也收录 Pigsty/Vagrant 开发循环、Windows 宿主和未来客机架构的设计提案。每份提案分别说明实现进度与验证状态。

Apple Silicon 原生 macOS 虚拟化子系统（`barn mac`）从 Barn `0.9.0` 引入，签名 App 从 `0.9.2` 起随 Apple Silicon 归档交付。请参阅[原生 macOS 虚拟机](/zh/docs/start/macos/)、[`barn mac` 命令参考](/zh/docs/reference/mac/)与 [Mac 发布手册](/zh/docs/about/mac-release/)。
