---
title: "开发快照：Go 1.27 产品能力面"
linkTitle: 2026-08-24 开发快照
description: Quick 与四节点 Private 行为、格式 3 的自有配置模板、Pigsty 清单集成、持久化、状态迁移与已验证的发布机制。
date: 2026-08-24
weight: 120
categories: [开发]
tags: [早期原型, QEMU, Pigsty]
icon: fa-solid fa-flask
---

> [!NOTE]
> Barn 前身历史归档（`Piglet`，2026-08-24）。该快照时间点尚无公开版本标签、生产签名产物或软件包仓库，所有内置镜像条目均标为 `testing`。当前 Barn 的设计与支持状态请参见[使用文档](/zh/docs/)与[支持状态](/zh/docs/about/status/)。

2026-08-24 源码快照将早期的 QEMU 原型演进为完整的 Go 1.27 本地虚拟机管理工具，具备零配置 Quick 模式、固定 IP 私有实验网、13 份内置配置模板、Pigsty 清单生成、持久数据盘、状态格式迁移与可复现打包流水线。

## 单一原生虚拟化运行时

Piglet 在 macOS 上通过 HVF、在 Linux 上通过 KVM 直接以当前用户身份驱动原生 QEMU，不回退到 TCG 软件模拟，也不接受任意透传的 QEMU 命令行参数。运行时负责校验镜像摘要与 `.qcow2` 文件头、生成纯 Go 实现的 NoCloud `cidata` 引导镜像、核对 QMP 与进程身份、检查 SSH 就绪状态，并维护原子状态文件、事务日志与事件记录。

## 两类 Tier 1 宿主上的 Quick 模式

无需编写 YAML 的 Quick 模式在 macOS `arm64` 与 Linux `amd64` 上均已完成验证，默认启动单台 `meta` 客机（`dba` 用户、2 vCPU、4 GiB 内存、64 GiB 根盘、稀疏 64 GiB `/data` 数据盘、用户态 NAT、SSH 及四条本地回环端口转发），支持 `plan`、`up`、`status`、`ssh`/`exec`、`stop`/`start`/`restart`、配置漂移识别、带保护的 `recreate`/`destroy`、`--no-wait`、持久盘保留、密钥轮换、日志查看、故障修复与脱敏诊断包导出。

## 私有实验网与宿主网络管理

Private 模式在两类 Tier 1 宿主上提供统一的 `preflight`、`status`、`install` 与 `uninstall` 操作：
- **macOS**：固定使用 `socket_vmnet` v1.2.2（默认 `host` 模式，同时验证了 `shared`/FD 路径）。
- **Linux**：采用可回滚的 `systemd-networkd` / NetworkManager / `qemu-bridge-helper` 事务。

两类宿主上的 QEMU 均以非特权用户运行，且在全局租约有效期间阻止卸载网络。操作者可显式指定一个规范的 RFC 1918 `/24` 子网替换默认的 `10.10.10.0/24`，并同步迁移配置模板、宿主网络、租约、节点地址与 Pigsty 清单。

四节点 `full` 与 MinIO 配置在两个 Tier 1 平台上完成了固定 IP、控制节点横向 SSH、管理网出网、存储身份、`stop`/`start` 持久性、崩溃恢复、30/30 连续耐久测试以及 16 块数据盘挂载验证。

## Schema-3 配置模板与 Pigsty 清单集成

13 份内置 Schema-3 配置模板共定义 85 个节点（统一使用 `dba` 账户；普通节点挂载一块 128 GiB `/data` 数据盘，MinIO 节点挂载四块 32 GiB 数据盘）。`piglet pigsty inventory` 可直接读取 Pigsty 源码树，校验宿主/VIP/管理/服务地址语义，完成自定义子网地址重映射，并原子写入权限为 `0600`、带归属标记的清单文件；`pigsty-vm` 则通过一组强类型环境变量暴露相同的生命周期接口。

## 持久化、状态迁移与自动化接口

- **持久数据盘**：标记 `persistent: true` 的磁盘在普通 `destroy` 与兼容 `recreate` 中予以保留；彻底删除需在 TTY 中输入确认短语或显式传入 `destroy --force --delete-persistent --yes-delete-persistent`。项目密钥清理默认仅预览，实际删除需执行 `project purge-keys --yes`。
- **状态格式迁移**：Schema `0 -> 1` 迁移要求所有节点已停止且无活动租约，先自动备份再通过 `project upgrade-state --dry-run|--yes` 原子更新。
- **自动化支持**：提供节点选择器、`--no-wait`、结构化 JSON 输出、分类退出码、Shell 补全、受管 SSH 与 `/etc/hosts` 片段、逐节点日志及脱敏诊断包。

## 镜像矩阵与发布打包机制

内置镜像集覆盖 `el9`、`el10`、`d12`、`d13`、`u22`、`u24` 与 `u26` 的 `amd64` 和 `arm64` 架构（双架构 7/7 全部通过启动验证；`el8` 在后续 Barn 版本完成规范化后重新加入）。构建工具链支持生成并校验四平台归档、Homebrew 配方、Linux `amd64`/`arm64` DEB 与 RPM 软件包、SHA-256 校验清单、SPDX SBOM 以及 Cosign/SLSA 签名测试夹具，并通过了双次构建可复现性比对。

## 后续在 RC6 与 Barn 0.x 中的演进

由于 Schema-3 模板目录与清单集成在首轮 `full`/MinIO 测试后更新了摘要，精确模板的真机重放、自定义子网 `/etc/hosts` 发布以及 `storage.data_root` / `ssh.wait_timeout` 接线在次日的 [2026-08-25 RC6 候选](rc6-owner-scoped-20260825/)中全部补齐；随后项目在 Barn `0.1.0`+ 中进一步收敛为单一的 Pigsty 原生 `barn.yml` 清单模型。当前 Barn 的设计与使用方式见[快速上手](/zh/docs/start/tutorial/)、[架构设计](/zh/docs/about/design/)与[支持状态](/zh/docs/about/status/)。
