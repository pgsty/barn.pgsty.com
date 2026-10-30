---
title: "为什么 Barn 没有项目"
linkTitle: "单部署，无项目"
description: "为什么 Barn 用一份 Pigsty 主机清单驱动一个用户范围内的部署，取代按目录组织的项目状态。"
date: 2026-08-27T19:00:00+08:00
weight: 10
categories: [设计]
tags: [架构, 主机清单, 状态]
icon: fa-solid fa-layer-group
lastmod: 2026-10-30
---

本文阐述 Barn `0.9.2` 的 Linux 实验环境部署模型（[Mac 虚拟机](/zh/docs/start/macos/)作为独立的具名虚拟机管理）。

> [!NOTE]
> **2026-10-30 更新**：未发布构建支持相对或符号链接形式的 `BARN_HOME`，并允许 `vm_skip: true` 外部主机使用主机名或 IPv6 清单键。跨目录操作同一部署时请使用绝对 `BARN_HOME`，详见[未发布变更](/zh/docs/about/unreleased/)。

Barn 的早期原型曾将每个工作目录视为一个独立“项目”：用隐藏目录标记项目身份，用全局注册表记录项目路径，再用宿主级租约表协调私有网段冲突。这套机制虽然能管理多组互不相关的虚拟机，但与 Barn 的核心场景格格不入——在本地拉起一套具有固定 IP 的 Pigsty 数据库实验集群。

由于 Pigsty 主机清单本身已经完整定义了所有节点的 IP 与角色，在它之上再叠一层“按目录划分的虚拟机项目”，反而制造出一系列与数据库测试无关的棘手问题：

- 节点的名称和 IP 究竟以虚拟机项目文件为准，还是以 `pigsty.yml` 为准？
- 移动或重命名源码目录，代表迁移原有实验环境，还是另起炉灶新建一套？
- 目录里的隐藏标记还在、全局注册表却丢了（或者反过来），该如何恢复？
- 某个项目目录消失，代表用户废弃了项目，还是外接硬盘暂时没挂载？
- 宿主上唯一的固定 IP 网段究竟归哪个项目所有？

多项目编排才需要回答这些问题，而本地单套 Pigsty 实验环境完全不需要。因此，Barn 彻底砍掉了“项目”概念。

> [!NOTE]
> 当前清单文件的发现顺序、字段规则与默认值详见[配置参考](/zh/docs/reference/configuration/)。

## 一份主机清单就够了

Pigsty 清单（`barn.yml` 或 `pigsty.yml`）直接作为 Barn 的期望状态配置。Barn 只读取主机 IPv4 键、少数 Pigsty 身份字段（`nodename`、`admin_ip`、`pg_cluster`、`pg_seq`、`node_admin_username`、`node_admin_uid`）以及文档定义的 `vm_*` 命名空间。

Barn 对自己消费的 `vm_*` 字段执行严格校验，对上层 Pigsty 专属变量（如 `pg_role`、`pg_version`、`repo_*`、`node_packages`）则原样透传、不作解释。这一边界兼顾了安全性与灵活性：把 `vm_mem` 拼错会在 `barn validate` 时立即报错，而在同一份 YAML 中调整 PostgreSQL 参数则完全不会触发虚拟机配置漂移。

节点命名同样遵循单一来源原则：优先采用显式的 `nodename`，其次由 `<pg_cluster>-<pg_seq>` 稳定派生，最后回退到 `node-<IP末段>`，绝不额外引入一个可能与 Pigsty 主机名打架的 `vm_name` 字段。

## 按用户隔离的单一状态根

所有已应用的部署状态统一存放在 `BARN_HOME`（默认 `~/.barn`）中。工作目录里不写任何隐藏标记，也不维护按路径索引的注册表。只读取已应用状态的命令（如 `barn status`、`barn ssh`、`barn stop`、`barn start`、`barn destroy`）在任意目录下执行效果完全一致；需要读取期望配置的命令（如 `barn validate`、`barn plan`、`barn up`、`barn reload`、`barn recreate`）则通过 `-f` 或当前目录自动发现清单。

由于 `BARN_HOME` 归属当前 Unix 登录用户，单部署模型天然按系统用户隔离，带来了一系列直观的工程收益：

- 移动或重命名工作目录绝不会让运行中的虚拟机变成孤儿，也不会误建第二套环境。
- 误删工作目录里的 `barn.yml` 不会抹掉 `~/.barn` 中的已应用状态（`plan` 与 `up` 仍可回退读取已提交的部署规格）。
- 镜像缓存、SSH 密钥、节点磁盘、锁文件与部署状态集中在同一个清晰的目录树下（Unix 短路径套接字、`~/.ssh/barn_config` 与宿主全局网络则保存在各自的标准位置，完整清理方式见[卸载指南](/zh/docs/start/uninstall/)）。

## 配置文件缺席不代表允许删除

Barn 严格区分期望配置与已提交状态。变更拓扑需要读取清单文件，但清单文件缺失或某个 YAML 分组被省略，绝不会成为自动删除已有虚拟机的依据。[变更规划与破坏性操作始终保持显式](/zh/blog/design/convergence-without-surprise/)，遇到任何归属存疑的资源，恢复流程都会优先保留现场而非猜测用户意图。

## 刻意保持精简的取舍

Barn 刻意将每个 `BARN_HOME` 限制为管理一套 Linux 实验环境，拒绝引入多项目并发、路径注册表与网段租约。对于本地数据库与基础架构开发而言，“一份清单驱动一套部署”让地址规划、属主核验、漂移检测、崩溃恢复与卸载清理都保持了最高的可预期性。

下一篇：[为什么每个 Barn 节点都有两张网卡](/zh/blog/design/fixed-ip-two-nics/)。
