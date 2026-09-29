---
title: 设计
description: Barn 如何组织 Linux 实验室与 macOS 客机，以及配置、网络、存储和生命周期的设计取舍。
weight: 20
icon: fa-solid fa-compass-drafting
aliases: [/docs/concepts/, /docs/concepts/networking/, /docs/concepts/storage/, /docs/concepts/safety/, /docs/architecture/, /docs/architecture/overview/, /docs/architecture/networking/, /docs/architecture/security/]
---

Barn 提供两套使用方式，共享同一个命令行入口，分别管理配置与生命周期。

| | Linux 实验室 | macOS 客机 |
| --- | --- | --- |
| 虚拟化 | QEMU，使用 HVF 或 KVM 加速；特定兼容场景使用 TCG | Apple Virtualization.framework |
| 期望配置 | 兼容 Pigsty 的 YAML 主机清单 | 通过 `barn mac` 配置的具名虚拟机 |
| 状态目录 | `~/.barn` | `~/.barn/mac` |
| 网络 | 管理网卡与固定 IP 实验室子网 | 每台虚拟机一个 NAT 子网与 DHCP 地址预留 |
| 典型用途 | 数据库集群、Linux 开发与自动化 | macOS 构建、桌面工具与独立开发环境 |

下文介绍 Linux 实验室的设计。原生 macOS 用法见[macOS 客机](../../start/macos/)与
[Mac 参考](../../reference/mac/)。

## 每位用户一套 Linux 实验室

Barn 把一份兼容 Pigsty 的主机清单启动成一套本地 QEMU 环境，无需额外的项目标记、项目注册表、
租约模型、虚拟化平台适配层或第二种配置格式。

状态位于当前 Unix 用户的 `BARN_HOME`（默认 `~/.barn`）。Linux 工作流按每位用户一套实验室设计，
并不通过 root 强制限制不同用户只能运行同一套环境。

## 节点级收敛

Barn 只提取已记录的 VM 与 Pigsty 原生字段，计算逐节点哈希，并保存应用状态与完整
进程身份。新增节点增量创建；`up` 也会启动选中的已停止节点，保留运行中同伴的进程，
同时重试未完成的初始化、刷新托管 hosts 与 SSH 配置。无法识别或确认损坏的测试数据
文件系统可能被清空重建，包括持久盘，详见[数据盘](../../reference/configuration/#数据盘)。
定义变更需要显式节点重建；从主机清单中移除节点不会自动删除虚拟机。

## 运行时选择

客机架构是部署级期望状态。省略或 `native` 跟随宿主；显式 `amd64`/`arm64` 会准确
选择对应镜像目录工件。HVF/KVM 原生加速仍是默认路径；外来架构或镜像目录已知的
镜像/宿主不兼容规则才会选择固定 TCG 配置。没有用户可传的加速器参数，也不会
因任意原生失败静默回退。

实际架构与加速器保存在每个 QEMU 启动参数中，并通过 `status` 展示。执行破坏性
recreate 前，Barn 会检查所选 QEMU 二进制与版本、网络后端、镜像内容、启动模式与固件。
以后若新二进制改变运行时策略，也不能把新旧节点混跑：运行时差异必须整体重建。

## 双网卡与一个固定子网

管理网卡负责 DHCP、DNS、出网与回环 SSH；固定 IP 网卡负责宿主、节点间与 Ansible
流量。macOS 使用 socket_vmnet；Linux 优先跟随当前 NetworkManager，否则使用
systemd-networkd，并通过发行版 bridge helper 接入。若 networkd 尚未启动，只有在
激活安全扫描证明现有服务单元不会接管真实宿主链路后才启动。

Debian helper 会临时、可逆地限制给调用者真实加入的组。setup 必须通过一次非特权
QEMU bridge smoke；失败后自动回滚安装。

## 存储与配置有不同生命周期

主机清单保存期望的 VM 定义；应用状态记录已经创建的内容，包括精确基础镜像身份与
运行时启动参数。镜像目录通道移动不会改写已有根盘。

通过校验的基础镜像只读共享，每台 VM 写入自己的根盘写时复制层。数据盘遵循独立的保留
契约：普通销毁保留持久盘，显式磁盘删除或彻底清理才清除它们。镜像缓存清理又有
独立边界，还会保护活动镜像目录与已注册本地别名。详见[存储与访问](../../start/storage/)
和[镜像参考](../../reference/images/)。

## 安全边界

QEMU 与所有客机工件都以调用者身份运行。root 仅用于宿主软件包安装、网络与可选 hosts publisher。
销毁必须同时匹配属主、路径包含、节点身份、QMP/进程身份与工件白名单；任何歧义都会停止。
