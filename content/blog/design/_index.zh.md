---
title: 设计注记
linkTitle: 设计
description: Barn 的架构决策、方案取舍与实现边界。
weight: 20
icon: fa-solid fa-pen-ruler
sidebar_root_menu: false
sidebar_expanded: true
blog_index: list
lastmod: 2026-09-29
---

本栏目说明 Barn 0.9.0 的架构与实现取舍。

建议从产品模型读起，再了解各部分的实现：

1. [为什么 Barn 没有项目](one-deployment-no-projects/)：一份清单驱动一套按用户管理的部署，无需另外维护虚拟机配置。
2. [为什么每个节点都有两张网卡](fixed-ip-two-nics/)：实验环境使用固定网络身份，管理网卡负责出网。
3. [声明式不等于破坏式](convergence-without-surprise/)：逐节点配置差异、显式重建与删除。
4. [PID 不是虚拟机身份](identity-before-pid/)：QMP 身份、进程证据、操作日志与有界恢复。
5. [`repo.yaml` 是意图，`catalog.json` 是证据](repo-yaml-catalog-json/)：生成元数据必须与
   实际 qcow2 字节一致的静态镜像仓库。

具体命令与配置见[使用文档](/zh/docs/)，宿主要求与功能限制见
[平台与限制](/zh/docs/about/status/)。

## 设计演进

原始的 [Mac 可行性研究](https://github.com/pgsty/barn/blob/5bce6b8824e63548d1066f6bd45942a08cdb00b8/MACOS-VM-RESEARCH-20260921.md)、
[双槽位产品方案](https://github.com/pgsty/barn/blob/5bce6b8824e63548d1066f6bd45942a08cdb00b8/MACOS-VM-PRODUCT-20260921.md)和
[实现与审查记录](https://github.com/pgsty/barn/blob/54315029d4a8d3ace7b4f7250d0381598f2d61dc/docs/mac-implementation-log.md)，记录了具名 Mac 虚拟机的设计取舍与实验。
[验证历史](/zh/docs/about/history/)记录历次发布与原生测试结果。已被替代的方案保留原有日期和范围。
