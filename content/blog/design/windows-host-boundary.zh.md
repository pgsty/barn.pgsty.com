---
title: "从 Windows 使用 Barn"
linkTitle: "Windows 宿主边界"
description: "为什么仍需 Linux 宿主、WSL2 需要验证什么，以及原生 Windows 后端涉及哪些工作。"
date: 2026-11-08T10:00:00+08:00
weight: 80
categories: [设计]
tags: [Windows, WSL, QEMU]
icon: fa-solid fa-laptop-code
lastmod: 2026-11-08
---

Barn 当前的宿主配置与发布二进制覆盖 macOS、Linux 上的 `amd64` 和 `arm64`，没有原生 Windows 发行版。Windows 用户可以通过 Linux 宿主操作 Barn；WSL2 和嵌套 Linux VM 是把这层宿主放到 Windows 本机上的候选方式。

本评估复核于 **2026-11-08**。下述 WSL2 与 Hyper-V 路径仍需完成 Barn 全生命周期实测，才能成为受支持的安装指南。当前平台契约见[平台与限制](/zh/docs/about/status/)和 [`internal/platform`](https://github.com/pgsty/barn/blob/main/internal/platform/platform.go)。

## 选择 Barn 实际运行的位置 {#host-options}

| 宿主环境 | 可复用的部分 | 需要确认的条件 |
|---|---|---|
| 远程 Linux/KVM 宿主 | 现有 Linux Barn 二进制与宿主集成 | SSH 访问、足够资源及常规 Linux 宿主检查 |
| WSL2 发行版 | Linux 二进制、QEMU、OpenSSH 与 Linux 文件系统 | 嵌套 KVM、systemd、bridge helper、私网和 Windows 到客机的访问 |
| Hyper-V 中的完整 Linux VM | 常规 Linux 安装与网络管理器 | 嵌套虚拟化、`/dev/kvm`、两层 VM 的资源和 Windows 访问路径 |
| 原生 Windows/QEMU | QEMU 的 WHPX 加速器 | 新的 Barn 宿主后端、网络集成、安装器与验收矩阵 |
{.wide .expand}

本地实验可以先评估 WSL2，因为它能复用 Linux 实现。嵌套虚拟化不可用或需要可靠性能时，可直接使用远程 Linux/KVM 宿主。Docker Desktop 会在 Barn 所需的宿主功能外再加一层 VM/容器边界，不纳入这条安装方案。

## WSL2 的两种配置作用域 {#wsl-config}

WSL2 全局虚拟机选项位于 Windows 的 `%UserProfile%\.wslconfig`；各发行版的启动配置，包括 systemd，位于 Linux 内的 `/etc/wsl.conf`。微软的[配置参考](https://learn.microsoft.com/en-us/windows/wsl/wsl-config)说明了这一区别与 `nestedVirtualization` 选项。写入配置后，仍需在实际机器上确认 KVM 设备可用并能启动客机。

`BARN_HOME`、缓存镜像和客机磁盘应放在 WSL Linux 文件系统中，例如默认的 `~/.barn`。微软的[文件系统建议](https://learn.microsoft.com/en-us/windows/wsl/filesystems)也要求 Linux 工作负载优先使用 Linux 文件系统。外层 WSL 虚拟磁盘承载 Linux 文件系统，内部的 qcow2 则是 Barn 单独管理的客机磁盘。

PowerShell 可以通过 `wsl.exe` 调用 Linux CLI，但状态、SSH 配置、宿主共享目录和私网桥仍属于这个 Linux 环境。

## 先验收，再形成安装建议 {#acceptance}

WSL2 或 Hyper-V Linux 候选环境应依次通过以下检查：

1. 确认 Linux init/网络管理器正常，当前用户能访问 `/dev/kvm`；用 KVM 启动一个小型 QEMU 探针，仅检查设备路径还不够。
2. 执行 `barn setup --dry-run` 查看依赖与网络变更，再按 Barn 的 Linux 检查核对已安装的 `qemu-bridge-helper`、发行版包归属、权限和 `barn0` 网桥。
3. 在可丢弃实验环境中启动同架构客机并达到 SSH 就绪，验证出站流量、宿主访问和两台客机在私网中的互通。
4. 测试 Windows 实际使用的访问路径，将管理端点、所需服务和私网路由分别检查。
5. 启停客机、重启外层 Linux 环境，验证恢复、持久盘和 Barn 所属网络资源的清理。
{.steps}

Windows 到 WSL 的 localhost 转发或[镜像网络模式](https://learn.microsoft.com/en-us/windows/wsl/networking)，本身不能证明嵌套客机子网已有可达路由。测试记录应说明选用的路由或隧道及防火墙要求。完整 Hyper-V Linux VM 的[嵌套虚拟化](https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/nested-virtualization)同样依赖外层宿主配置。

Barn 只为跨架构客机和特定镜像兼容情况选择 TCG；普通原生 KVM 启动失败时，不会静默切换到 TCG。因此，没有可用原生加速的 WSL 环境不能按普通 Linux Barn 宿主宣传。

## 原生 Windows 后端需要独立实现 {#native-backend}

QEMU 可以通过 [WHPX](https://www.qemu.org/docs/master/system/whpx.html)使用硬件加速，Barn 仍需实现加速器周围的宿主契约：

| 领域 | 当前依赖 | Windows 所需工作 |
|---|---|---|
| 平台与打包 | Darwin/Linux 配置与发布目标 | Windows 配置、依赖检测、二进制与安装器 |
| 进程身份与恢复 | POSIX 进程证据和信号 | Windows 进程句柄、身份核验、取消与恢复 |
| 状态与锁 | Unix 文件系统元数据与 `flock` | 等价的锁、权限和原子状态更新 |
| QMP 与宿主共享 | Unix socket、继承的目录描述符、Virtio-9p | 可用的传输方式与经过验证的共享语义 |
| 私网 | `barn0`、bridge helper 与 Linux 网络管理器 | 明确管理特权和防火墙归属的 Windows 后端 |
{.wide .expand}

这些实现边界可从 [`internal/process`](https://github.com/pgsty/barn/tree/main/internal/process)、[`internal/lock`](https://github.com/pgsty/barn/tree/main/internal/lock)、[`internal/hostshare`](https://github.com/pgsty/barn/tree/main/internal/hostshare)和 [`internal/network`](https://github.com/pgsty/barn/tree/main/internal/network)核对。为现有二进制包一层调用脚本无法提供这些契约。

Vagrant 展示了为什么必须明确 provider 的差异：其 [Hyper-V 限制](https://developer.hashicorp.com/vagrant/docs/providers/hyperv/limitations)说明 Vagrantfile 网络配置会被忽略，由用户选择现有虚拟交换机。Barn 的固定地址实验环境需要先建立自己的网络保证，再把 Windows 加入受支持的宿主矩阵。
