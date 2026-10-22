---
title: 设计
description: Barn 如何组织 Linux 实验环境与 macOS 客机，以及配置、网络、存储和生命周期的设计取舍。
weight: 20
icon: fa-solid fa-compass-drafting
aliases: [/docs/concepts/, /docs/concepts/networking/, /docs/concepts/storage/, /docs/concepts/safety/, /docs/architecture/, /docs/architecture/overview/, /docs/architecture/networking/, /docs/architecture/security/]
---

Barn 分别管理 Linux 实验环境和 macOS 客机。两者共用命令行入口，各自管理配置与生命周期。

| | Linux 实验环境 | macOS 客机 |
| --- | --- | --- |
| 虚拟化 | QEMU，使用 HVF 或 KVM 加速；特定兼容场景使用 TCG | Apple Virtualization.framework |
| 期望配置 | 兼容 Pigsty 的 YAML 主机清单 | 通过 `barn mac` 配置的命名虚拟机 |
| 状态目录 | `~/.barn` | `~/.barn/mac` |
| 网络 | 管理网卡与固定 IP 实验网段 | 每台虚拟机一个 NAT 子网与 DHCP 地址预留 |
| 典型用途 | 数据库集群、Linux 开发与自动化 | macOS 构建、桌面工具与独立开发环境 |

下文介绍 Linux 实验环境的设计。原生 macOS 用法见[macOS 客机](../../start/macos/)与
[Mac 参考](../../reference/mac/)。

## 每位用户一套 Linux 实验室

每个 Unix 用户用一份兼容 Pigsty 的清单管理一套 Linux 实验环境。
Barn 将状态保存在 `BARN_HOME`（默认 `~/.barn`）中，与工作目录无关。
因此，切换目录不会新建实验环境。

## 节点级收敛

`up` 创建新节点，启动选中的已停止节点，并保留运行中的进程。
它还会重试未完成的初始化，更新托管的 hosts 与 SSH 配置。
修改已有节点的定义需要显式重建；从清单中移除节点不会自动删除虚拟机。

为识别变更，Barn 根据文档列出的虚拟机字段与 Pigsty 原生字段计算每个节点的哈希，
并将它与已应用状态、进程身份一起保存。

## 运行时选择

客机架构属于整个部署的期望状态。省略架构或选择 `native` 时，Barn 使用宿主架构。
显式选择 `amd64`/`arm64` 时，Barn 使用镜像目录中对应的文件。

Barn 默认使用 HVF/KVM 原生加速。仅在跨架构或镜像目录记录了镜像与宿主不兼容时，
Barn 才使用 TCG 软件模拟。用户不能通过参数选择加速器。其他原生加速失败不会触发 TCG 回退。

Barn 在每个 QEMU 启动参数中记录实际架构与加速器。`status` 显示这些值。
执行破坏性的 recreate 前，Barn 检查所选 QEMU 二进制与版本、网络后端、镜像内容、启动模式与固件。
如果 Barn 升级改变了运行时策略，需要重建整个部署才能应用新策略，以保持所有节点的运行时策略一致。

## 双网卡与一个固定子网

每台 Linux 虚拟机有两张网卡。管理网卡提供 DHCP、DNS、出网，以及通过宿主回环地址访问的 SSH。
固定 IP 网卡用于宿主与节点之间、节点与节点之间的通信，包括 Ansible。
在 macOS 宿主上，socket_vmnet 提供这套网络。

在 Linux 上，如果 NetworkManager 已启动，Barn 使用 NetworkManager。
否则，Barn 使用 systemd-networkd，并通过发行版 bridge helper 接入。
如果 networkd 尚未启动，Barn 先检查现有服务单元。只有确认它们不会接管真实宿主链路后，
Barn 才启动 networkd。

在 Debian 上，Barn 临时向调用者所属的组授予 bridge helper 权限。
setup 会以该普通用户运行 QEMU，测试网桥。如果测试失败，setup 自动回滚网络安装。

## 存储与配置有不同生命周期

清单保存期望的虚拟机定义。已应用状态记录已创建的资源，包括准确的基础镜像身份与启动参数。
镜像目录通道变化不会改写已有根盘。

虚拟机以只读方式共享已校验的基础镜像，每台虚拟机将根盘变更写入独立的文件（root overlay）。
普通销毁会保留持久数据盘，显式磁盘删除或彻底清理会删除这些磁盘。

客机恢复流程可能重新格式化无法识别或确认损坏的数据文件系统，包括持久盘上的文件系统。
详见[数据盘](../../reference/configuration/#数据盘)。

镜像缓存清理使用独立规则，保护活动镜像目录与已注册的本地别名。
详见[存储与访问](../../start/storage/)和[镜像参考](../../reference/images/)。

## 安全边界

QEMU 以调用者身份运行，所有客机文件都属于该用户。
只有安装宿主软件包、配置网络与可选的 hosts 更新需要 root 权限。

销毁前，Barn 检查属主、路径范围、节点身份、QMP/进程身份与文件白名单。
如果任何检查结果不明确，Barn 停止操作。
