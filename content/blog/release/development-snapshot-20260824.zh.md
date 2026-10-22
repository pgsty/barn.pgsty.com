---
title: "开发快照：Go 1.27 产品能力面"
linkTitle: 2026-08-24 开发快照
description: Quick 与四节点 Private 行为、格式 3 的自有配置模板、Pigsty 清单集成、持久化、状态迁移与已验证的发布机制。
date: 2026-08-24
weight: 10
categories: [开发]
tags: [Go 1.27, Quick, Private, Pigsty, QEMU, macOS, Linux]
icon: fa-solid fa-flask
---

> [!NOTE]
> 本文记录 Barn 前身 Piglet 的开发快照，保留当时的方案、版本、命令、路径、校验值与验证结果。当前 Barn 行为见[使用文档](/zh/docs/)与 [Barn 状态](/zh/docs/about/status/)。

Piglet 的 2026-08-24 源码快照已从 QEMU 原型发展为本地虚拟机产品。
它支持零配置 Quick、固定地址私有实验环境、13 份 Piglet 自有配置模板和可审计的 Pigsty 清单集成。
它还提供显式持久化、状态迁移、诊断与可复现的发布工具链。

该 2026-08-24 快照尚未稳定发布，后续前身候选另行归档；两者均保留各自的历史证据。

> [!WARNING]
> 当时没有公开 v1.0 标签、生产签名产物、Homebrew 软件源或 DEB/RPM 仓库。
> 所有内置镜像记录仍为 `testing`。本地软件包与签名往返测试验证了机制，尚未验证生产托管。

## 一套原生 Runtime

Piglet 在 macOS 通过 HVF、Linux 通过 KVM 直接驱动原生 QEMU。
它严格解析规格，并负责镜像/qcow2 校验、纯 Go NoCloud CIDATA、QMP/进程身份和 SSH 就绪检查。
它还管理原子状态写入、事务日志、事件、修复和限定范围的删除。QEMU 以调用用户身份运行，不会静默回退到 TCG。

系统不提供第二套运行后端，也不接受任意 QEMU 参数。

## 两条 Tier 1 上的 Quick

保留的 Go 1.27 Quick 运行记录覆盖 macOS arm64 与 Linux amd64 无需 YAML 的公开用法。
配置约定为 `meta`/`dba`、2 vCPU、4 GiB、64 GiB 根盘、稀疏 64 GiB `/data`、用户态 NAT、SSH 与四条回环端口转发。

产品支持规划、启动、状态查询、SSH/远程执行、停止、再次启动和重启。
它还支持漂移分类、有保护措施的重建与销毁、异步返回、持久盘保留、密钥退役、日志、修复和脱敏调试包。

这些端口转发不会安装应用。Pigsty/PostgreSQL 初始化仍需通过独立的集成验证。

## Private Lab 与宿主网络

Private 模式在两类 Tier 1 宿主上都提供公开的预检、状态、安装和卸载操作。
macOS 固定使用 `socket_vmnet` v1.2.2，默认为 host 模式，shared/FD 路径也有验证记录。
Linux 使用可回退的 systemd-networkd/NetworkManager/bridge-helper 事务。
两类宿主上的 QEMU 都以非特权用户身份运行。全局租约有效时，系统阻止卸载。

用户可以显式指定一个规范的 RFC1918 `/24` 子网，替换默认的 `10.10.10.0/24`。
配置模板、宿主网络安装、租约、状态、节点地址与 Pigsty 清单必须一起迁移。系统不会随机选择子网来绕过冲突。

保留的四节点 `full` 与 MinIO 运行记录覆盖两个 Tier 1 平台。
它们验证了固定 IP、仅控制节点可用的横向 SSH、管理网互联网访问、存储身份、停止后启动的持久性和完整销毁。
更早的运行还覆盖崩溃恢复与 30/30 耐久测试。MinIO 配置模板的运行验证了 16 块虚拟机数据盘，未验证 MinIO 应用。

## Schema-3 自有 Profile 与 Pigsty Inventory

13 份内置配置模板共包含 85 个节点，全部使用 `dba`。普通节点有一块 128 GiB `/data`，MinIO 节点有四块 32 GiB 磁盘。
格式 3 的模板目录管理扩展规则、镜像策略与 Pigsty 清单绑定，支持直接使用和 `build_subset` 模式。

`piglet pigsty inventory` 读取真实的 Pigsty 源码树，对宿主/VIP/管理/服务地址的语义进行分类和校验。
它会协调自定义子网的地址变换，并可原子发布权限为 `0600`、带归属标记的文件。
`pigsty-vm` 通过一组类型明确的环境变量提供相同的配置模板、网络、生命周期与清单约定。

包装脚本不会回退到其他运行后端。运维回滚需要上一版已验证的 Piglet 产物及其匹配的状态备份。

## 持久化、升级与自动化

标记 `persistent: true` 的磁盘会在普通销毁与兼容重建后保留。
删除这些磁盘需要在 TTY 中单独输入确认短语，或使用
`destroy --force --delete-persistent --yes-delete-persistent`。
项目密钥清理默认只预览，实际删除需执行独立的 `project purge-keys --yes` 命令。

格式 0→1 迁移仅在节点停止且没有租约时允许执行。迁移先备份，再通过
`project upgrade-state --dry-run|--yes` 显式执行原子更新。系统拒绝读取更高版本的格式，不会将其降级。

Private 节点选择器、`--no-wait`、稳定的 JSON 响应和分类退出码支持人工操作与自动化。
系统还提供 Shell 补全、SSH 配置、带归属标记的 hosts 块、逐节点日志与脱敏支持包。

## 镜像与 Release 机制

内置镜像集合为 `el9`、`el10`、`d12`、`d13`、`u22`、`u24`、`u26`，覆盖两个 Tier 1 原生架构。
保留的矩阵记录显示，每个架构均通过 7/7。EL8 的 arm64 内核无法满足已测试的原生 HVF 约定，因此退出 v1。
生产镜像渠道与托管责任落实前，条目保持 `testing`。

源码可以构建并校验四种原生归档、Homebrew 配方、Linux amd64/arm64 RPM 与 DEB、校验和、SPDX SBOM 及完整发布产物集。
它还支持 Cosign 签名/SLSA 来源证明的正向与篡改测试。
测试快照通过了隔离环境中的软件包安装、校验、移除及两轮可复现验证。仓库中的发布工作流尚未针对真实标签执行。

## 证据必须跟随准确字节

在该快照时间点，格式 3 的模板目录和清单集成已改变配置模板及解析结果的摘要。
这些变化晚于已保留的 `full`/MinIO 运行，因此仍需对快照中的配置模板重跑原生验证。
自定义子网的 hosts 发布、应用 `storage.data_root`/`ssh.wait_timeout` 配置及通用 Quick 用户支持也尚未完成。

RC6 后续补齐了这些实现和配置模板验证。历史原生运行只证明实际测试过的产物与行为。

## v1.0 前仍需完成

该快照中的配置模板、Pigsty 初始化和 Rocky 9.8 私有网络宿主验证已在后续运行中完成。该阶段剩余工作为：

- 明确生产镜像、清单、发布产物与长期运行器的维护责任。
- 验证真实重启恢复、Tier 2 宿主原生运行，以及已发布软件包的安装。
- 发布绑定真实标签、附带签名与来源证明的版本。

当前维护边界见[教程](/zh/docs/start/tutorial/)、[设计](/zh/docs/about/design/)与
[当前状态](/zh/docs/about/status/)。
