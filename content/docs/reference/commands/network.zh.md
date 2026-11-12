---
title: 宿主网络命令
description: 检查、安装和移除 Linux 客机使用的固定 IP 网络。
weight: 60
date: 2026-11-11
---

检查、安装和移除 Linux 客机使用的固定 IP 网络。

本参考对应 **Barn 1.2.0**；选项表区分 **1.1.0 已有选项** 与 **1.2.0 新增选项**，具体范围见[版本基线](/zh/docs/reference/commands/#versions)。所有命令继承[全局选项](/zh/docs/reference/commands/#global-options)。

## `barn network status` {#barn-network-status}

```text
barn network status [flags]
```

检查宿主上供 Linux 客机使用的唯一 Barn 网络，包括后端、已安装 CIDR、归属、健康状态和生命周期预检发现。`--cidr` 指定预期子网，省略时检查已安装子网；本操作只读。每个原生 Mac VM 的独立网络另行管理。

别名：`st`。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-c, --cidr string` | 可选的预期私有 `/24`；省略时检查已安装子网 | 1.1.0 |
{.wide .expand}

```bash
barn network status
barn --json network status --cidr 10.10.10.0/24
```

## `barn network install` {#barn-network-install}

```text
barn network install [flags]
```

检查或安装宿主网络后端：macOS 使用 `socket_vmnet`，Linux 通过活动网络管理器配置 `barn0`。终端先展示提权计划并询问；结构化或非交互调用默认仅预览，`--yes` 才执行。新 Mac 建议先用 `setup` 获取锁定的 socket_vmnet 压缩包。

`--archive`、`--interface-id` 仅适用于 macOS，`host/shared` 是 macOS vmnet 模式，Linux 不接受 `shared`。已有网络必须匹配所选配置，变更子网或模式前先检查状态。

别名：`i`。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-a, --archive string` | macOS 专用：锁定版本的本地 `socket_vmnet` 压缩包，仍需通过摘要校验 | 1.1.0 |
| `-c, --cidr string` | 规范的 RFC1918 IPv4 `/24` 子网；模板与网络安装默认 `10.10.10.0/24` | 1.1.0 |
| `-i, --interface-id string` | macOS 专用：持久化的 vmnet UUID | 1.1.0 |
| `-m, --mode string` | macOS 的 `socket_vmnet` 模式：`host`（默认）或 `shared` | 1.1.0 |
| `-y, --yes` | 确认并执行显示的计划；系统 `sudo` 仍可能要求密码 | 1.1.0 |
{.wide .expand}

```bash
barn network install --json
barn network install --cidr 10.10.10.0/24 --yes
```

## `barn network uninstall` {#barn-network-uninstall}

```text
barn network uninstall [flags]
```

仅移除 Barn 管理的网络配置并恢复已记录的宿主设置，运行中 Linux 客机会阻止卸载，应先停止。终端模式显示计划后询问，结构化或非交互调用默认预览，`--yes` 才执行。不会删除 VM 磁盘或原生 Mac 网络。

别名：`u`。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-y, --yes` | 确认并执行显示的计划；系统 `sudo` 仍可能要求密码 | 1.1.0 |
{.wide .expand}

```bash
barn stop
barn network uninstall --json
barn network uninstall --yes
```

## 实现依据 {#implementation}

[command_network.go](https://github.com/pgsty/barn/blob/v1.2.0/cmd/barn/command_network.go)

发布源码与相对 1.1.0 的变化见[版本基线](/zh/docs/reference/commands/#versions)。
