---
title: "声明式不等于破坏式"
linkTitle: "不制造意外的收敛"
description: "Barn 如何用逐节点哈希与显式操作保证配置缺席永远不能授权删除。"
date: 2026-08-27T21:00:00+08:00
weight: 30
categories: [设计]
tags: [生命周期, 配置差异, 安全]
icon: fa-solid fa-arrows-rotate
lastmod: 2026-11-08
---

本文阐述 Barn `0.9.3` 的 Linux 虚拟机收敛模型，并补充下文 `1.0.0` 的恢复规则（[Mac 虚拟机](/zh/docs/start/macos/)独立管理）。

> [!NOTE]
> **2026-10-30 更新**：Barn 0.9.3 源码中的 `plan`、`up`、`reload` 与 `recreate` 按显式节点选择应用变更，保留未选中节点的已应用定义。下文的全清单漂移规则仍适用于未指定节点的操作，详见[分批应用节点变更](/zh/docs/start/operations/#selected-nodes)。
>
> **2026-11-04 更新**：Barn 1.0.0 让整套部署 `recreate` 同样不会因节点缺席而删除节点：清单缺少已有节点时，会在停止任何虚拟机前拒绝执行（`conflict`，reason `nodes_removed`，退出码 4），而 0.9.3 会删除被省略的节点。数据盘只在没有任何签名，或 ext4/XFS 文件系统被识别出损坏时才会重置；其他失败会保留数据并给出警告。详见 [1.0.0 发布说明](/zh/blog/release/1.0.0/)。

声明式工具通过对比实际状态与配置文件来驱动变更——但在日常开发中，配置文件可能为了调试被临时删减、切换到另一个 Git 分支，或在解决合并冲突时漏掉某个 YAML 主机组。如果本地虚拟机管理工具把“配置中少写了某个节点”直接当成“允许销毁该虚拟机”，一次普通的编辑失误就可能把正在测试的数据库节点连根抹掉。

因此，Barn 在“创建”与“销毁”之间划定了严格的不对称原则：

> 期望状态可以授权创建节点，也可以描述配置漂移；但它绝不能仅凭配置缺席就授权销毁资源。

根盘、数据盘、SSH 密钥与客机内已部署的数据库都承载着上下文状态。重建或删除这些资源必须由操作者通过显式命令确认。

## 从主机清单到节点级规格哈希

解析 `barn.yml` 时，Barn 提取契约范围内的字段、填入默认值，并将镜像选择器与架构归一化为解析后的节点规格。由于镜像目录中的具体镜像摘要另行解析，单纯执行 `barn update` 刷新通道不会无故改变既有节点的规格哈希。每个节点的哈希仅由两部分组成：

- **所有节点共享的部署级信封（Envelope）**：包括 `/24` 子网、登录用户名、`vm_arch` 架构策略与部署级默认镜像选择器。
- **该节点自身的解析后定义**：包括 `nodename`、IP、vCPU、内存、根盘容量、`vm_disks`、`vm_shares` 与 `vm_alias`。

因此，扩容新增节点不会改变已有节点的哈希；修改 PostgreSQL 版本、软件包列表或服务角色等上层 Pigsty 变量，也完全不会产生虚拟机层的配置漂移。

> [!NOTE]
> `barn up` 会自动收敛新增节点与已停止节点。CPU 与内存变更使用 `barn resize`，其他节点配置变更与节点移除则必须通过显式的 `barn recreate` 与 `barn destroy` 执行。日常操作流程见[日常管理](/zh/docs/start/operations/)。

## `barn plan` 的六种规划结果

`barn plan` 对比期望配置、已应用部署状态与已提交节点状态，将每个节点归类为以下六种结果之一：

| 结果 | 含义 | 处理命令 |
|---|---|---|
| `create` | 清单中新增的节点，尚无已提交的虚拟机状态 | 运行 `barn up` 创建并启动 |
| `unchanged` | 解析后的节点定义与运行时策略均未变化 | `barn up` 保持运行中节点不动，并启动已停止节点 |
| `resize` | 节点只修改了 `vm_cpu` 或 `vm_mem` | 运行 `barn resize <node>`，支持时热插拔扩容，否则停止并重新启动同一台虚拟机 |
| `recreate` | 节点的镜像、磁盘、共享目录或其他硬件定义发生变化 | 显式运行 `barn recreate <node>`（脚本中可加 `--yes`） |
| `missing` | 已提交的节点在当前清单中缺席，或被标为 `vm_skip: true` | 显式运行 `barn destroy <node>`，或在 `barn.yml` 中恢复该节点 |
| 部署级信封漂移 | 子网、登录用户名、`vm_arch` 或全局运行时策略改变 | 整套部署执行 `barn recreate` |
{.wide .expand}

`barn plan` 完全只读，并在文本模式下直接给出解决 `resize`、`recreate` 或 `missing` 漂移所需的具体命令。

## 为什么 `barn up` 遇到配置漂移会主动停下

当既有节点的 CPU、内存或镜像发生变化时，`barn up` 不会调整运行中虚拟机的规格，也不会在后台静默重做根盘，而是直接返回类型化的 `conflict` 冲突错误。CPU 与内存变更交给 `barn resize <node>`，它会保留虚拟机身份与磁盘；其余变更都要求显式执行 `barn recreate <node>`，这带来两个直接好处：

1. 所有会替换客机根盘的破坏性变更都集中到同一个需要确认的显式动作中。
2. Barn 可以在**停止或删除现有虚拟机之前**完成全部前置检查——包括核验目标 QEMU 模拟器、加速策略、UEFI 固件、镜像缓存字节、网络后端、共享源目录以及持久盘兼容性。一旦缺少跨架构模拟器或共享目录不合法，原有的虚拟机将完好无损地保留下来。

## 为什么节点缺席会阻止 `barn up`

一个节点从当前 `barn.yml` 中消失，往往源于许多并不代表“我要删库”的日常场景：

- 调试单机问题时临时打开了一份精简版清单；
- 重命名了某个分组，或临时用 `vm_skip: true` 跳过某台主机；
- 切换分支或解决合并冲突时漏掉了一段 YAML；
- 在另一个放有不同 `barn.yml` 的目录下执行了命令。

只要已应用状态中还记录着某个在当前清单中缺席的节点，`barn up` 就会立即停下并指出该节点名称，由你决定是把配置补回 `barn.yml`，还是显式运行 `barn destroy <node>` 将其销毁。

在执行销毁或重建时，数据盘的保留与清理同样遵循明确边界：

- 普通 `barn destroy` 与 `barn recreate` 默认保留 `persistent: true` 的持久数据盘。
- 整套部署执行 `barn destroy --delete-persistent` 会一并删除受管的持久盘；执行 `barn purge`（或 `barn destroy --purge`）则会一次性删除所有磁盘、密钥与部署状态。
- 在 `barn up` 客机恢复期间，Barn 只会格式化没有任何签名的数据盘，并且仅在检查工具报告可识别的损坏时重置 ext4 或 XFS 文件系统；遇到分区表、不支持的文件系统特性或未知的检查失败时，数据保持原样并报告警告（详见[数据盘配置](/zh/docs/reference/configuration/#数据盘)）。

## 1.0 恢复规则：区分角色变更与漂移 {#control-role-recovery}

删除控制节点后，由剩余定义中的第一个节点接任。`SpecHash` 表示当前已应用定义，`GuestSpecHash` 表示客机已有的就绪标记；控制角色变更时，两者可能不同，而 VM 身份与磁盘仍然有效。

在标记任何节点删除之前，Barn 必须先完成接任节点已提交的 prepare 日志，再原子发布部署状态，作为角色变更的提交记录，随后更新接任节点的定义哈希。两次写入之间若发生中断，恢复逻辑在部署锁内只接受能够由 `Control` 翻转精确解释的哈希差异，其他漂移仍然拒绝；它不会创建缺失状态、更换 VM UUID 或修改磁盘/进程身份。详见 [1.0 加固记录](https://github.com/pgsty/barn/blob/v1.0.0/docs/release-1.0-hardening.md)与[控制角色恢复测试](https://github.com/pgsty/barn/blob/v1.0.0/internal/private/control_test.go)。

更新清单中的控制角色后，再运行 `barn up` 安装控制节点 SSH 访问。通用的在线角色迁移还需要定义旧凭据撤销、离线重试与部分失败语义；随意放宽哈希检查会掩盖尚未完成的客机收敛。

## 1.0 恢复规则：先证明损坏 {#disk-recovery-evidence}

文件系统检查器的退出码不能单独授权格式化：ext4 的 `4`/`12` 与 XFS 的 `1` 必须伴随已识别的损坏诊断。不支持的特性、权限、I/O 或内存失败、分区表以及未知诊断都会保留磁盘并报告客机警告。`persistent` 控制 destroy/recreate 时的磁盘保留，识别出损坏后仍适用文档中的重置策略。

[数据盘恢复测试](https://github.com/pgsty/barn/blob/v1.0.0/internal/cloudinit/disk_recovery_test.go)使用哨兵检查 `mkfs` 是否实际执行，物理宿主验收则比较磁盘内容，同时验证破坏性副作用与警告文本。带日期的覆盖范围见[验证历史](/zh/docs/about/history/#release-1-0-candidates)。

## 无连带影响的增量收敛

由于收敛以节点为粒度独立计算，`barn up` 从 1 节点扩容到 4 节点时完全不会中断正在运行的控制节点；执行 `barn recreate node-2` 时也只会重建 `node-2` 并自动挂回其兼容的持久数据盘，而 `meta` 与 `node-1` 全程保持在线。

下一篇：[PID 不是虚拟机身份](/zh/blog/design/identity-before-pid/)。
