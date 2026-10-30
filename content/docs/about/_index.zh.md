---
title: 项目
linkTitle: 项目
description: Barn 的适用平台、设计思路、贡献方式与发布工程。
weight: 30
icon: fa-solid fa-circle-info
no_list: true
cascade:
  type: docs
---

Barn（**Bootstrap And Run Nodes**）是面向本地数据库实验、Linux 开发与 macOS 测试的 Apache-2.0 开源虚拟机管理工具。

- [平台与限制](status/) — Barn 0.9.2 的宿主环境要求、客机兼容矩阵与存储规则
- [设计说明](design/) — 单清单 Linux 实验环境与独立 `barn mac` 虚拟机的架构设计
- [安全与信任](security/) — 宿主特权边界、SSH 凭据、共享目录与镜像验签机制
- [参与贡献](engineering/) — 源码目录结构、本地构建与测试门禁、打包快照及镜像目录维护
- [未发布变更](unreleased/) — 路径、共享、节点选择及开发工作流限制的源码调整
- [验证历史](history/) — 历次版本发布、真机虚拟化测试与镜像校验的归档记录
{.cards}

版本更新记录请查阅[发布说明](/zh/blog/release/)，架构取舍请阅读[设计文章](/zh/blog/design/)。欢迎在 [GitHub](https://github.com/pgsty/barn) 提交 Issue 与 Pull Request；安全漏洞请按[安全政策](https://github.com/pgsty/barn/blob/main/SECURITY.md)私密上报。
