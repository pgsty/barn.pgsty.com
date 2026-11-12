---
title: 命令参考
linkTitle: 命令参考
description: 逐项介绍 Barn 全部命令的语法、局部选项、默认值、使用示例与版本范围。
weight: 5
date: 2026-11-11
lastmod: 2026-11-12
icon: fa-solid fa-terminal
no_list: true
---

从下表选择命令，查看参数、完整局部选项、示例与操作范围。组织方式参考 [PIG](https://pig.pgsty.com/zh/cmd/) 的命令索引与命令组详解；结构化输出及退出码见 [CLI 契约](../cli/)，清单字段见[配置参考](../configuration/)。

## 版本基线 {#versions}

本参考对应 **2026-11-12** 发布的 **Barn 1.2.0**，源码为 [`90f6158`](https://github.com/pgsty/barn/tree/v1.2.0)。中英文页面均已对照 CLI 帮助核对，覆盖 57 个操作命令与 174 项局部选项。

| 标记 | 可用范围 | 行为 |
|---|---|---|
| **1.1.0** | 1.1.0 与 1.2.0 均支持的选项 | 1.1.0 默认 2 vCPU / 4 GiB，通过清单调整 CPU/内存 |
| **1.2.0** | 1.2.0 新增 | 规格选项与环境变量、`vm_scale`、根盘扩容、生命周期 `--parallel`、`vm_hosts` 和 `hosts install -f`；默认规格改为 1 vCPU / 2 GiB |
{.wide .expand}

升级时如需保留旧默认值，请显式设置 `vm_cpu: 2`、`vm_mem: 4GiB`，并检查 `barn plan`。已应用 VM 的资源会保留到显式执行资源变更操作为止。用 `barn version` 和 `barn COMMAND --help` 核对已安装构建；另见[发布说明](/zh/blog/release/1.2.0/)与[发布验收](/zh/blog/design/release-1-2-0-readiness/)。

## 命令索引 {#command-index}

| 任务 | 命令与详细参考 |
|---|---|
| 准备环境 | [setup](setup/#barn-setup)、[init](setup/#barn-init)、[validate](setup/#barn-validate)、[doctor](setup/#barn-doctor) |
| 规划与创建 | [plan](lifecycle/#barn-plan)、[up](lifecycle/#barn-up) |
| 启停节点 | [start](lifecycle/#barn-start)、[stop](lifecycle/#barn-stop)、[restart](lifecycle/#barn-restart)、[reload](lifecycle/#barn-reload) |
| 调整与检查 | [resize](lifecycle/#barn-resize)、[recreate](lifecycle/#barn-recreate)、[status](lifecycle/#barn-status) |
| 删除部署 | [destroy](lifecycle/#barn-destroy)、[purge](lifecycle/#barn-purge) |
| 访问 Linux 客机 | [ssh](access/#barn-ssh)、[exec](access/#barn-exec)、[logs](access/#barn-logs)、[provision](access/#barn-provision)、[ssh-config](access/#barn-ssh-config) |
| 发布宿主名称 | [hosts install](access/#barn-hosts-install)、[hosts uninstall](access/#barn-hosts-uninstall) |
| 刷新目录 | [update](image/#barn-update)、[image sync](image/#barn-image-sync)、[image reset](image/#barn-image-reset) |
| 管理 Linux 镜像 | [image list](image/#barn-image-list)、[info](image/#barn-image-info)、[pull](image/#barn-image-pull)、[import](image/#barn-image-import)、[prune](image/#barn-image-prune) |
| 维护镜像仓库 | [repo scan](repo/#barn-repo-scan)、[build](repo/#barn-repo-build)、[verify](repo/#barn-repo-verify) |
| 宿主网络 | [network status](network/#barn-network-status)、[install](network/#barn-network-install)、[uninstall](network/#barn-network-uninstall) |
| 原生 macOS VM | [mac ls](mac/#barn-mac-ls)、[up](mac/#barn-mac-up)、[start](mac/#barn-mac-start)、[stop](mac/#barn-mac-stop)、[restart](mac/#barn-mac-restart)、[configure](mac/#barn-mac-configure)、[recreate](mac/#barn-mac-recreate)、[destroy](mac/#barn-mac-destroy) |
| Mac 访问 | [mac open](mac/#barn-mac-open)、[ssh](mac/#barn-mac-ssh)、[exec](mac/#barn-mac-exec)、[password](mac/#barn-mac-password)、[ssh-config](mac/#barn-mac-ssh-config)、[logs](mac/#barn-mac-logs) |
| Mac 准备 | [mac setup](mac/#barn-mac-setup)、[doctor](mac/#barn-mac-doctor)、[image ls](mac/#barn-mac-image-ls)、[image update](mac/#barn-mac-image-update)、[image prune](mac/#barn-mac-image-prune) |
| CLI 工具 | [version](setup/#barn-version)、[completion](setup/#barn-completion)、[help](#barn-help) |
{.wide .expand}

## 全局选项 {#global-options}

```text
barn [--json|--yaml] [-v|--verbose] COMMAND [arguments] [local options]
```

| 选项 | 含义 |
|---|---|
| `-h`、`--help` | 显示所选命令的可读帮助，退出 `0` |
| `--json` | stdout 输出结构化 JSON，进度与诊断保留在 stderr |
| `--yaml` | stdout 输出结构化 YAML，与 `--json` 互斥 |
| `-v`、`--verbose` | 向 stderr 输出有界诊断信息 |
| `--version` | 根命令的版本快捷选项；结构化版本报告用 `barn version --json` |

全局输出选项可放在子命令前后，但必须在 `ssh`、`exec` 使用的远程命令分隔符 `--` 之前。`-f`、`-I`、`-A`、`-p`、`--yes` 都是局部选项，以对应命令的表格为准。`logs -f` 表示跟随日志，`mac logs -n` 表示行数。长布尔选项支持 `=true` 或 `=false`。

`BARN_OUTPUT`、`BARN_VERBOSE` 设置输出默认值。`BARN_HOME` 选择私有状态目录，默认 `~/.barn`，跨目录操作时建议使用绝对路径。Linux 与 Mac 机器共用数据根目录，但生命周期相互独立。详见[环境变量](../cli/#logs-and-environment)与[退出码](../cli/#exit-codes)。

## barn 与帮助 {#barn-help}

```bash
barn
barn --help
barn help resize
barn image pull --help
barn --json
```

无参数时，文本模式打印完整帮助并退出 `0`，JSON/YAML 模式返回建议操作 `actions[]`。显式帮助始终输出可读文本。`image`、`repo`、`network`、`hosts`、`mac image` 命令组要求子命令，缺少时退出 `2`；`mac` 是例外，默认执行 `mac ls`。Linux 和 Intel Mac 的根帮助隐藏 `mac`，但仍可显式查看 Mac 命令帮助。

简写在父命令范围内生效，例如 `barn im ls` 等同 `barn image list`，`barn mac st` 等同 `barn mac ls`；各命令页列出了对应别名。`purge` 没有 `rm` 别名。
