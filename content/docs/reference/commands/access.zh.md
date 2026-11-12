---
title: 客机访问与 hosts
description: 连接 Linux 客机、执行脚本、读取日志，以及发布 SSH 和 hosts 条目。
weight: 30
date: 2026-11-11
---

连接 Linux 客机、执行脚本、读取日志，以及发布 SSH 和 hosts 条目。

本参考对应 **Barn 1.2.0**；选项表区分 **1.1.0 已有选项** 与 **1.2.0 新增选项**，具体范围见[版本基线](/zh/docs/reference/commands/#versions)。所有命令继承[全局选项](/zh/docs/reference/commands/#global-options)。

## `barn ssh` {#barn-ssh}

```text
barn ssh [flags] [node] [-- command...]
```

打开所选已准备节点的交互 SSH 会话，默认选择已准备的控制节点，否则选第一个已准备节点。远程命令必须放在 `--` 后，参数会像普通 `ssh` 一样合并后交给远程 shell 解析；Barn 选项放在分隔符前。节点参数必须是解析后的节点名，不能使用 IP、别名或组名。

远程命令的退出码原样传回。结构化交互 SSH 将会话输出发送到 stderr，最终报告写入 stdout。详见 [SSH 参数规则](../../cli/#ssh-passthrough-and-completion)。

除 `--help` 外没有局部选项，仍可使用全局输出选项。

```bash
barn ssh
barn ssh meta
barn ssh meta -- 'df -h /data; id'
```

## `barn exec` {#barn-exec}

```text
barn exec [flags] [node] -- command...
```

在所选已准备节点运行一个远程命令，默认节点选择规则与 `ssh` 一致。必须使用 `--`，首个命令参数不能为空；分开的参数保留空格、引号以及后续空值。管道、重定向和变量展开请用 `sh -c`，也兼容将单个完整字符串作为 shell 命令。

文本模式转发子进程输出与退出码；结构化结果包含 `success`、`exit_code`、`stdout`、`stderr`。远程非零退出码原样返回，应先检查报告再判断是否属于 Barn 自身错误。

别名：`ex`。

除 `--help` 外没有局部选项，仍可使用全局输出选项。

```bash
barn exec meta -- hostname
barn exec meta -- printf '<%s>\n' 'a b' ''
barn --json exec meta -- sh -c 'echo out; exit 17'
```

## `barn logs` {#barn-logs}

```text
barn logs [node] [flags]
```

读取所选节点的串口或 QEMU 诊断日志，默认选已准备的控制节点或第一个已准备节点。`--source events` 读取部署级有界事件日志，不接受节点参数，可在部署状态建立前使用。跟随模式持续输出流，`-f` 在这里表示跟随日志，不是清单文件。QEMU 参数仅在详细输出开启时显示。

别名：`l`。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-f, --follow` | 持续读取新增日志；文本输出字节流，JSON 输出 NDJSON，YAML 输出文档流 | 1.1.0 |
| `-s, --source string` | 日志源：`serial`（默认）、`qemu` 或部署级 `events` | 1.1.0 |
{.wide .expand}

```bash
barn logs meta
barn logs meta --source qemu
barn logs --source events --follow
barn --json logs meta --follow
```

## `barn provision` {#barn-provision}

```text
barn provision [node...] [flags]
```

通过已验证的部署 SSH 连接，将本地 Bash 脚本流式发送给所选运行中节点；未选节点时针对全部节点。脚本不会作为文件留在客机，执行记录包含脚本摘要；命令不创建或启动 VM。

必须指定 `--script`，默认串行执行，整个操作默认超时一小时。此处 `--parallel 0` 无效，与 1.2.0 生命周期并发规则不同。`--sudo` 在客机使用非交互的 `sudo -n`，需确保客机用户已有权限。结构化输出可以检查各节点的执行结果与失败。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-p, --parallel int` | 正整数并发上限，默认 1；不接受 0 | 1.1.0 |
| `-s, --script string` | 必填：将此本地 Bash 脚本通过 SSH 传给所选客机执行 | 1.1.0 |
| `--sudo` | 在客机通过 `sudo -n` 执行脚本 | 1.1.0 |
| `-t, --timeout duration` | 整个操作的截止时间，正时长；默认 `1h` | 1.1.0 |
{.wide .expand}

```bash
barn provision --script ./check.sh meta
barn provision --script ./bootstrap.sh --sudo --parallel 2 --timeout 30m
```

## `barn ssh-config` {#barn-ssh-config}

```text
barn ssh-config [node...] [flags]
```

默认打印 Linux 部署的 OpenSSH 配置片段。`--install` 写入片段并在 `~/.ssh/config` 加一条 `Include`，打印和安装都可选节点；`--remove` 只移除指定的 Barn 片段，不依赖部署状态，也不接受节点名。安装与移除选项互斥。

默认前缀为 `barn`，片段路径为 `~/.ssh/barn_config`，普通生命周期命令会自动维护。用户 SSH 配置无法安全修改时，Barn 给出需要手工加入的 `Include`，直接使用 `barn ssh` 仍可连接。

别名：`sc`。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-i, --install` | 安装 SSH 配置片段，并在 `~/.ssh/config` 加入一条 `Include` | 1.1.0 |
| `--name string` | SSH 别名与配置片段前缀，默认 `barn` | 1.1.0 |
| `--remove` | 移除 Barn 安装的 SSH 配置片段与 `Include` | 1.1.0 |
{.wide .expand}

```bash
barn ssh-config
barn ssh-config --install meta
barn ssh-config --install --name lab
barn ssh-config --remove --name lab
```

## `barn hosts install` {#barn-hosts-install}

```text
barn hosts install [flags]
```

通过摘要匹配的提权 helper，将已应用节点的名称和别名写入宿主 `/etc/hosts` 的 Barn 区块。终端先展示变更并询问；非交互或结构化模式默认只预览，显式 `--yes` 才执行。区块内容未变化时无需提权，`up` 不会自动发布此文件。

Barn 1.2.0 新增 `-f pigsty.yml`，可在创建 VM 前发布清单节点及 `all.vars.vm_hosts`。每次替换整个 Barn 区块，后来不带 `-f` 执行会移除仅来自清单的服务名，详见[本机服务名](../../configuration/#local-hosts)。

别名：`i`。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-f, --file string` | 发布清单节点、别名与 `vm_hosts`；无需预先创建 VM | 1.2.0 |
| `-y, --yes` | 确认并执行显示的计划；系统 `sudo` 仍可能要求密码 | 1.1.0 |
{.wide .expand}

```bash
barn hosts install --json
barn hosts install --yes
```

## `barn hosts uninstall` {#barn-hosts-uninstall}

```text
barn hosts uninstall [flags]
```

只移除宿主 `/etc/hosts` 中 Barn 管理的区块，保留其他条目，不需要清单或部署状态。终端模式展示计划并询问；非交互或结构化模式默认预览，`--yes` 才执行。移除此区块不删除 VM 或修改客机 DNS 配置。

别名：`u`。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-y, --yes` | 确认并执行显示的计划；系统 `sudo` 仍可能要求密码 | 1.1.0 |
{.wide .expand}

```bash
barn hosts uninstall --json
barn hosts uninstall --yes
```

## 实现依据 {#implementation}

[command_root.go](https://github.com/pgsty/barn/blob/v1.2.0/cmd/barn/command_root.go) · [command_access.go](https://github.com/pgsty/barn/blob/v1.2.0/cmd/barn/command_access.go) · [main.go](https://github.com/pgsty/barn/blob/v1.2.0/cmd/barn/main.go)

发布源码与相对 1.1.0 的变化见[版本基线](/zh/docs/reference/commands/#versions)。
