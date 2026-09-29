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

建议从产品模型开始，再沿着边界向外阅读：

1. [为什么 Barn 没有项目](one-deployment-no-projects/)：一份主机清单、一套
   按用户管理的部署，不制造第二份事实。
2. [为什么每个节点都有两张网卡](fixed-ip-two-nics/)：实验室固定身份与管理出网分离。
3. [声明式不等于破坏式](convergence-without-surprise/)：逐节点配置差异、显式重建与删除。
4. [PID 不是虚拟机身份](identity-before-pid/)：QMP 身份、进程证据、操作日志与有界恢复。
5. [`repo.yaml` 是意图，`catalog.json` 是证据](repo-yaml-catalog-json/)：生成元数据必须与
   实际 qcow2 字节一致的静态镜像仓库。

具体命令与配置见[使用文档](/zh/docs/)，宿主要求与功能限制见
[平台与限制](/zh/docs/about/status/)。
