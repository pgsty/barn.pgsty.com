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

这五篇设计随笔阐述了 Barn Linux 实验环境的核心工程取舍：涵盖 `~/.barn` 单部署状态模型、Pigsty/Ansible 清单复用、运行中客机的就地收敛、镜像目录签名校验，以及 macOS 与 Linux 宿主网络拓扑。

关于 Barn `0.7.0` 引入的 Apple Silicon 原生 macOS 虚拟化子系统（`barn mac`），请参阅[原生 macOS 虚拟机](/zh/docs/start/macos/)、[`barn mac` 命令参考](/zh/docs/reference/mac/)与[架构与设计](/zh/docs/about/design/)。
