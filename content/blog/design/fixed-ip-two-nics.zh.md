---
title: "为什么每个 Barn 节点都有两张网卡"
linkTitle: "固定 IP，双网卡"
description: "为什么 Barn 把管理出网与宿主、节点、Ansible 和 Pigsty 使用的固定地址网络分离。"
date: 2026-08-27T20:00:00+08:00
weight: 20
categories: [设计]
tags: [网络, QEMU, Pigsty]
icon: fa-solid fa-network-wired
lastmod: 2026-10-26
---

本文阐述 Barn `0.9.2` 的 Linux 实验环境网络设计（[Mac 虚拟机](/zh/docs/start/macos/)使用每台虚拟机独立的 `vmnet` NAT 子网）。

Pigsty 主机清单依靠固定 IPv4 地址标识每个数据库节点：PostgreSQL 流复制、Patroni/etcd 共识、HAProxy 后端、keepalived 二层 VIP、Prometheus 采集目标与 Ansible 剧本，都要求 `10.10.10.11` 始终指向同一个节点。宿主回环端口转发虽然能把 SSH 或 `5432` 端口暴露给宿主机，却无法让多台虚拟机之间通过固定内网地址组成集群。

与此同时，刚启动的云镜像又需要顺畅访问外网软件源，且不应要求用户在宿主上手工维护复杂的 NAT/MASQUERADE 防火墙规则。为此，Barn 为每个 Linux 节点配备了两张职责分明的虚拟网卡（NIC）。

## 两张网卡，各司其职

| 网卡 | 地址分配 | 核心职责 |
|---|---|---|
| 管理网卡 | QEMU 用户态 NAT（`slirp`）、DHCP | 提供 DNS、默认路由、互联网出站访问与宿主回环端口 SSH 转发 |
| 固定 IP 实验网卡（按 MAC 绑定） | 清单声明的 RFC1918 `/24` 静态地址 | 承载宿主到节点、节点与节点之间、Ansible、Pigsty 服务与二层 VIP 流量 |
{.wide}

Barn 通过确定性的 MAC 地址在客机内绑定两张虚拟网卡，而不依赖因发行版而异的内核网卡名（如 `eth0` 或 `enp0s4`）：

- **管理网卡**让新创建的虚拟机开箱即具备外网访问、DNS 解析与宿主回环 SSH 转发（`127.0.0.1:<端口>`），宿主无需配置任何额外 NAT 规则或 DHCP 服务。
- **固定 IP 实验网卡**直接配置 `barn.yml` 中的静态地址，不设默认网关与 DNS。`barn up` 在客机初始化阶段会校验该网卡；若管理 SSH 已就绪但私网连通性检查未通过，Barn 仍会将客机标记为可访问，并在 `nodes[].warnings` 中记录 `private-network` 告警，方便你登录排查宿主网桥或路由冲突后再次执行 `barn up` 收敛。

> [!NOTE]
> 双网卡拓扑是所有 Barn Linux 节点的标准配置。Linux 与 macOS 两套运行时架构的整体对比见[设计说明](/zh/docs/about/design/)。

## `/24` 地址规划完全由清单决定

同一套部署中的所有托管节点共享同一个规范的 RFC1918 `/24` 子网：

| 地址范围 | 用途划分 |
|---|---|
| `.1` | 宿主侧私网网关地址 |
| `.2`–`.8` | 保留地址段（可供二层 VIP 使用，同时作为 macOS `vmnet` 内置 DHCP 池的上限边界） |
| `.9`–`.254` | `barn.yml` 中声明的节点固定地址 |
{.wide}

由于客机私网网卡不走 DHCP，而是由 `cloud-init` 直接写入 `barn.yml` 中声明的静态地址（macOS 上 `socket_vmnet` 的 DHCP 池截止到 `.8`；Linux 上 `barn0` 网桥直接使用静态地址），节点 IP 完全不依赖租约数据库，Ansible 从首次连接到后续重启始终使用同一个地址。

在生成全新的默认模板时，若默认 `10.10.10.0/24` 已被宿主其他路由占用，`barn setup` 会自动从候选私有网段中改选空闲的 `/24`；对于用户显式传入的 `-f` 清单或已编辑过的配置文件，Barn 绝不会擅自改写网段。

## 遵循各平台原生网络管理，统一客机视图

在客机内部，所有 Linux 发行版看到的双网卡拓扑完全一致；在宿主侧，Barn 则顺应宿主当前活跃的网络管理服务，确保 QEMU 始终以非特权普通用户身份运行：

- **macOS（`socket_vmnet`）**：安装固定版本的 `socket_vmnet` launchd 服务提供二层私网（默认 `host` 模式，可通过 `--mode shared` 切换共享模式），QEMU 保持普通用户权限运行。
- **启用 NetworkManager 的 Linux**：通过 `nmcli` 创建并管理专属的 `barn0` 网桥，并与活跃的 `firewalld` 区域策略协同工作。
- **使用 `systemd-networkd` 的 Linux**：安装专属的 `barn0` networkd 单元，并配合发行版自带的 `qemu-bridge-helper` 实现普通用户 QEMU 挂接网桥。
- **`systemd-networkd` 未启动的 Linux**：在桌面或 RHEL 系宿主上贸然启动未激活的 `systemd-networkd` 可能会抢占物理网卡导致断网；因此 Barn 会在变更前扫描宿主现有的 `.network` 单元，只有确认它们不会匹配任何真实宿主网卡时才启用 `systemd-networkd`。

## 将宿主网络配置设计为可逆事务

由于网桥或 `socket_vmnet` 服务在 CLI 退出后仍常驻系统且安装过程需要 `sudo` 权限，Barn 将宿主网络安装设计为六步可逆事务：

1. **检查宿主现状** — 扫描当前路由表、网络接口、活跃网络服务、文件属主与已有的 Barn 网络状态。
2. **打印变更计划** — 在申请特权前完整展示即将创建的文件、接口与服务变更。
3. **执行前复核前置条件** — 在真正落盘修改前再次校验路由与接口冲突。
4. **记录 root 属主的回滚状态** — 在 `/etc/barn/network.json`（或对应平台路径）中精确记录 Barn 新建的资源及变更前的宿主状态。
5. **实测非特权 QEMU 挂桥** — 以普通调用用户身份实际运行一次 QEMU 网桥接入测试；若测试失败则立即自动回滚全部网络变更。
6. **就绪后提交事务** — 所有接口与连通性检查全部通过后，才将宿主网络标记为已完成安装。
{.steps}

Barn 绝不会强行接管宿主上已占用相同 `.1/24` 的外部接口，也不会覆盖被手工改动过的受管文件；当仍有节点处于运行状态时，`network uninstall` 会拒绝卸载网络，并在卸载时严格按记录还原到安装前的状态。

## 务实的工程取舍

让客机公网流量走 QEMU 用户态网络，是用少许外网吞吐换取“零防火墙改动、跨平台免特权运行”的极简体验；而宿主与节点互访、数据库流复制、etcd 心跳以及从 `meta` 控制节点分发软件包等所有对延迟和吞吐敏感的流量，则全部跑在固定 IP 的高速私网链路上。

下一篇：[声明式不等于破坏式](/zh/blog/design/convergence-without-surprise/)。
