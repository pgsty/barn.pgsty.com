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

本栏目说明 Barn 0.9.0 候选版本的架构与实现取舍。

建议从产品模型开始，再沿着边界向外阅读：

1. [为什么 Barn 没有 Project](one-deployment-no-projects/)：一份 Inventory、一个
   Owner-scope Deployment，不制造第二份事实。
2. [为什么每个节点都有两张网卡](fixed-ip-two-nics/)：实验室固定身份与管理出网分离。
3. [声明式不等于破坏式](convergence-without-surprise/)：逐节点 Drift、显式重建与删除。
4. [PID 不是虚拟机身份](identity-before-pid/)：QMP 身份、进程证据、Journal 与有界恢复。
5. [`repo.yaml` 是意图，`catalog.json` 是证据](repo-yaml-catalog-json/)：生成元数据必须与
   实际 qcow2 字节一致的静态镜像仓库。

当前行为以[文档](/zh/docs/)为准，带日期的验证边界见[当前状态](/zh/docs/about/status/)。
这些设计记录解释契约为何存在；它们不会把设计、构建或本地测试升级成发布证据。
