---
title: "开发快照：Go 1.27 产品能力面"
linkTitle: 2026-08-24 开发快照
description: Quick 与四节点 Private 语义、Schema-3 自有 Profile、Pigsty Inventory 集成、持久化、状态迁移与已验证发布机制。
date: 2026-08-24
weight: 10
categories: [开发]
tags: [Go 1.27, Quick, Private, Pigsty, QEMU, macOS, Linux]
icon: fa-solid fa-flask
---

> [!CAUTION]
> Barn 之前的历史记录。本页名称、命令、路径、Hash 与结论只描述前任快照；当前行为以
> [Barn 状态](/zh/docs/about/status/)和使用指南为准。

Piglet 的 2026-08-24 源码快照已经远不止最初的 QEMU Spike。它现在提供一套连贯本地 VM 产品：
零配置 Quick、固定地址私有实验室、13 份 Piglet 自有 Profile、可审计 Pigsty Inventory 边界、
显式持久化/状态迁移、诊断与可复现 Release Toolchain。

它仍是开发快照，不是稳定 Release。

> [!NOTE]
> 本页是 2026-08-24 历史快照。后续前任候选另行归档；两者都不是当前 Barn Release 证据。

> [!WARNING]
> 当前没有公开 v1.0 Tag、生产签名 Artifact、Homebrew Tap 或 DEB/RPM 仓库。所有内置镜像记录
> 仍为 `testing`。本地 Package 与签名 Round Trip 证明机制，不证明生产托管。

## 一套原生 Runtime

Piglet 在 macOS 通过 HVF、Linux 通过 KVM 直接驱动原生 QEMU，并负责严格 Spec Resolution、
镜像/qcow2 校验、纯 Go NoCloud CIDATA、QMP/进程身份、SSH 就绪、原子状态、Journal、Event、
Repair 与有界删除。QEMU 以调用用户运行，也不会静默回退 TCG。

没有第二 Provider/Runtime 路径，也没有任意 QEMU 参数逃生口。

## 两条 Tier 1 上的 Quick

保留的 Go 1.27 Quick 运行覆盖 macOS arm64 与 Linux amd64 公开无 YAML 路径。契约是
`meta`/`dba`、2 vCPU、4 GiB、64 GiB 根盘、稀疏 64 GiB `/data`、User NAT、SSH 与四条
回环转发约定。

产品支持 Plan、Up、Status、SSH/Exec、Stop/Start/Restart、漂移分类、受保护 Recreate/Destroy、
No-wait、持久盘保留、密钥退役、日志、Repair 与脱敏 Debug Bundle。

这些 Forward 不会安装应用；Pigsty/PostgreSQL Bootstrap 仍是独立集成门槛。

## Private Lab 与宿主网络

Private 模式现在在两类 Tier 1 宿主上都有公开 Preflight/Status/Install/Uninstall。macOS 使用固定
`socket_vmnet` v1.2.2，默认 Host Mode，并有 Shared/FD 路径证据。Linux 使用可逆
systemd-networkd/NetworkManager/bridge-helper 事务。两者都让 QEMU 保持非特权，并在全局租约
活跃时阻止 Uninstall。

默认 `10.10.10.0/24` 可以被一个显式规范 RFC1918 `/24` 替代。Profile、宿主 Install、租约、
状态、节点地址与 Pigsty Inventory 必须一起迁移，不会随机选择冲突逃生网段。

保留的四节点 `full` 与 MinIO 运行在两个 Tier 1 路径验证固定 IP、控制节点独占横向 SSH、管理
互联网、存储身份、Stop/Start 持久与干净 Destroy。更早运行还覆盖 Crash Recovery 与 30/30
Soak。MinIO Profile 运行验证的是 16 块 VM 数据盘，不是 MinIO 应用。

## Schema-3 自有 Profile 与 Pigsty Inventory

13 份内置 Profile 共 85 个节点，全部使用 `dba`。普通节点一块 128 GiB `/data`；MinIO 节点
四块 32 GiB 磁盘。Catalog Schema 3 自有管理 Scalability、Image Policy 与 Pigsty Inventory
Binding，并包含 Direct 与 `build_subset` Mode。

`piglet pigsty inventory` 读取真实 Pigsty Source Tree，对 Host/VIP/Admin/Service Address 语义分类
校验，Rebase 协调自定义子网，并可原子发布 `0600` Marker-owned 输出。`pigsty-vm` 通过一组小型
类型化环境变量暴露同一 Profile、网络、生命周期与 Inventory 契约。

Wrapper 没有 Provider Fallback。运维回滚是上一版已验证 Piglet Artifact 与匹配 State Backup。

## 持久化、升级与自动化

标记 `persistent: true` 的磁盘会在普通 Destroy 与兼容 Recreate 后保留。当前安全契约要求
独立 TTY Phrase，或
`destroy --force --delete-persistent --yes-delete-persistent`；项目密钥有独立默认 Dry-run
的 `project purge-keys --yes` 边界。

Schema 0→1 迁移只允许停止、要求无租约、先备份、原子并显式通过
`project upgrade-state --dry-run|--yes` 执行。更高 Schema 会拒绝，不会降级。

Private 节点 Selector、`--no-wait`、稳定 JSON、类型化退出码、Shell Completion、SSH Config、
Marker-owned Hosts Block、逐节点日志与脱敏 Support Bundle 构成当前操作者/自动化界面。

## 镜像与 Release 机制

内置正式镜像集合是 `el9`、`el10`、`d12`、`d13`、`u22`、`u24`、`u26`，覆盖两个 Tier 1
原生架构。保留矩阵记录每个架构报告 7/7；EL8 因 arm64 Kernel 无法满足已测试原生 HVF 契约而
退出 v1。生产镜像渠道与托管责任落实前，条目继续保持 `testing`。

源码可以构建并校验四种原生 Archive、Homebrew Formula、Linux amd64/arm64 RPM 与 DEB、
Checksum、SPDX SBOM、组合 Release Assembly，以及 Cosign Signature/SLSA Provenance 正向与
Tamper 测试。测试快照的隔离 Package Install/Verify/Remove 与两轮可复现通过；已检入 Release
Workflow 尚未针对真实 Tag 执行。

## 证据必须跟随准确字节

在该快照时间点，Catalog Schema 3 与 Inventory 集成晚于已保留 `full`/MinIO 运行，因此准确
当前 Profile 仍需原生刷新；自定义子网 Hosts 发布、落实 `storage.data_root`/
`ssh.wait_timeout` 与通用 Quick User 也仍开放。

RC6 后续关闭了这些实现与准确 Profile 缺口。历史原生运行仍只对自身真实执行过的字节与行为
有效。

## v1.0 前仍需完成

该快照中的准确 Profile、Pigsty Bootstrap 与 Rocky 9.8 Private-host Gate 后续已经运行。当前
剩余门槛是生产 Image/Manifest/Release 托管、持久 Runner Ownership、真实 Reboot Recovery、
Tier 2 原生 Smoke、已发布 Package 消费，以及真实签名/证明 Tag-bound Release。

当前维护边界见[教程](/zh/docs/start/tutorial/)、[设计](/zh/docs/about/design/)与
[当前状态](/zh/docs/about/status/)。
