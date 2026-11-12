---
title: Linux 生命周期
description: 规划、创建、启停、调整、查看和显式删除 Linux 虚拟机。
weight: 20
date: 2026-11-11
---

规划、创建、启停、调整、查看和显式删除 Linux 虚拟机。

本参考对应 **Barn 1.2.0**；选项表区分 **1.1.0 已有选项** 与 **1.2.0 新增选项**，具体范围见[版本基线](/zh/docs/reference/commands/#versions)。所有命令继承[全局选项](/zh/docs/reference/commands/#global-options)。

节点参数使用 `meta`、`node-1` 等解析后的名称，省略时选择该命令清单或已应用范围内的全部节点；IP、组名、`vm_alias` 均不能作为选择器。`plan`、`up`、`reload`、`resize`、`recreate` 依次读取 `-f`、当前目录清单、已应用状态，其他生命周期命令直接使用已应用状态。

规格覆盖、缩放和环境变量见[配置参考](../../configuration/#specification-overrides)。1.2.0 并发选项只适用于下文列出 `--parallel` 的命令，`plan`、`resize`、`status` 不接受它。结构化结果与退出码见 [CLI 契约](../../cli/#lifecycle-results)。

## `barn plan` {#barn-plan}

```text
barn plan [node...] [flags]
```

将有效期望清单与已应用状态比较，输出精确镜像、资源、逐盘动作，以及需要创建、调整资源、重建、启动或显式移除的节点，不改变 VM 或下载镜像。目录镜像仅需本地元数据，具名本地镜像还需要 `qemu-img`。

退出码 `0` 表示成功生成计划，也可能是因清单遗漏节点而阻塞的计划；脚本需检查 `action`、`blocked` 和变更数组。显式选择节点时保留其他节点的已应用定义。结果格式见[计划输出](../../cli/#planning)。

别名：`pl`。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-A, --arch string` | 客机架构：`native`、`amd64`、`arm64`；也接受 `x86_64`、`x64`、`aarch64`、`a64` | 1.1.0 |
| `-C, --cpu string` | 缩放前的基础 vCPU 数，整数 1–256；最终 CPU 数也不能超过 256 | 1.2.0 |
| `-D, --disk string` | 根盘绝对容量，裸整数单位为 GiB，例如 `128GiB`；至少达到基础镜像虚拟容量 | 1.2.0 |
| `-f, --file string` | 显式清单路径；生命周期命令依次使用该文件、当前目录发现的清单、已应用状态 | 1.1.0 |
| `-I, --image string` | 镜像引用，如 `u24`、`el9:stable` 或 `d13@20261103`；覆盖所选节点的 `vm_image/vm_version` | 1.1.0 |
| `-M, --mem string` | 缩放前的基础内存，裸整数单位为 MiB，例如 `4GiB`；至少 512 MiB | 1.2.0 |
| `-r, --repo string` | 镜像仓库 URL 或本地目录，优先于 `BARN_REPO`；支持 `--mirror` 的命令中也优先于该选项 | 1.1.0 |
| `-S, --scale string` | CPU 与内存的整数倍率，1–256；磁盘容量不缩放 | 1.2.0 |
{.wide .expand}

```bash
barn plan
barn plan -f pigsty.yml meta
barn --json plan -I u24 -A amd64
```

## `barn up` {#barn-up}

```text
barn up [node...] [flags]
```

创建缺失节点、启动已停止节点，并在保留健康 VM 进程的同时重试未完成的客机配置。默认等待管理 SSH 就绪，随后更新宿主 SSH 别名、客机 hosts 与控制节点 SSH 条目；非致命客机配置问题放入 `warnings`，已就绪节点仍视为成功。

首次交互运行时可以准备缺失的宿主依赖；清单与部署状态都不存在时会生成 `meta`。脚本应先运行 `setup --yes`。已有节点的定义变化需用 `resize` 或 `recreate`，清单遗漏的节点需显式 `destroy`。`--rollback` 仅清理本轮准备失败节点中尚未提交且可安全回收的制品。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-A, --arch string` | 客机架构：`native`、`amd64`、`arm64`；也接受 `x86_64`、`x64`、`aarch64`、`a64` | 1.1.0 |
| `-C, --cpu string` | 缩放前的基础 vCPU 数，整数 1–256；最终 CPU 数也不能超过 256 | 1.2.0 |
| `-D, --disk string` | 根盘绝对容量，裸整数单位为 GiB，例如 `128GiB`；至少达到基础镜像虚拟容量 | 1.2.0 |
| `-f, --file string` | 显式清单路径；生命周期命令依次使用该文件、当前目录发现的清单、已应用状态 | 1.1.0 |
| `-I, --image string` | 镜像引用，如 `u24`、`el9:stable` 或 `d13@20261103`；覆盖所选节点的 `vm_image/vm_version` | 1.1.0 |
| `-M, --mem string` | 缩放前的基础内存，裸整数单位为 MiB，例如 `4GiB`；至少 512 MiB | 1.2.0 |
| `--mirror` | 使用中国官方源 `https://repo.pigsty.cc/barn`；显式 `--repo` 优先 | 1.1.0 |
| `-n, --no-wait` | QEMU 启动并通过进程身份核验后返回；SSH 就绪与客机恢复延后到下一次 `up` | 1.1.0 |
| `-p, --parallel int` | 节点并发上限；省略时为 `max(1, 逻辑 CPU 数 - 2)`，`0` 表示所选节点全部并发 | 1.2.0 |
| `-r, --repo string` | 镜像仓库 URL 或本地目录，优先于 `BARN_REPO`；支持 `--mirror` 的命令中也优先于该选项 | 1.1.0 |
| `--rollback` | 清理本次准备失败节点中尚未提交、可以安全回收的制品 | 1.1.0 |
| `-S, --scale string` | CPU 与内存的整数倍率，1–256；磁盘容量不缩放 | 1.2.0 |
{.wide .expand}

```bash
barn up
barn up -f pigsty.yml meta
barn up --mirror --rollback
barn up meta --no-wait
```

## `barn start` {#barn-start}

```text
barn start [node...] [flags]
```

按已应用状态启动所选已停止节点并等待 SSH，使用同一 `BARN_HOME` 时可从任意目录执行，不读取清单或创建新节点。启动会刷新 SSH 访问配置；已经运行的 VM 需要补做客机配置时用 `up`。共享目录不可用只影响对应节点，独立节点继续执行。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-n, --no-wait` | QEMU 启动并通过进程身份核验后返回；SSH 就绪与客机恢复延后到下一次 `up` | 1.1.0 |
| `-p, --parallel int` | 节点并发上限；省略时为 `max(1, 逻辑 CPU 数 - 2)`，`0` 表示所选节点全部并发 | 1.2.0 |
{.wide .expand}

```bash
barn start
barn start meta --no-wait
```

## `barn stop` {#barn-stop}

```text
barn stop [node...] [flags]
```

核验已记录的进程身份后停止所选 Linux VM，保留根盘、数据盘、密钥与部署状态。未指定名称时停止整套 Linux 部署；原生 macOS VM 和宿主网络分别由各自命令管理。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-p, --parallel int` | 节点并发上限；省略时为 `max(1, 逻辑 CPU 数 - 2)`，`0` 表示所选节点全部并发 | 1.2.0 |
{.wide .expand}

```bash
barn stop meta
barn stop
```

## `barn restart` {#barn-restart}

```text
barn restart [node...] [flags]
```

使用已应用状态停止并重新启动已有节点，不读取清单修改。需要重新读取清单用 `reload`，应用已有节点的定义变化用 `resize` 或 `recreate`。默认等待 SSH，`--no-wait` 可跳过等待。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-n, --no-wait` | QEMU 启动并通过进程身份核验后返回；SSH 就绪与客机恢复延后到下一次 `up` | 1.1.0 |
| `-p, --parallel int` | 节点并发上限；省略时为 `max(1, 逻辑 CPU 数 - 2)`，`0` 表示所选节点全部并发 | 1.2.0 |
{.wide .expand}

```bash
barn restart
barn restart meta --no-wait
```

## `barn reload` {#barn-reload}

```text
barn reload [node...] [flags]
```

先校验期望规格与启动依赖，通过后才停止所选节点并按 `up` 流程收敛，可以创建清单中新增加的节点。需要调整资源或重建的变更，以及清单遗漏的已应用节点，都会在停止任何 VM 前阻止执行。仅按已记录配置重启时用 `restart`。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-A, --arch string` | 客机架构：`native`、`amd64`、`arm64`；也接受 `x86_64`、`x64`、`aarch64`、`a64` | 1.1.0 |
| `-C, --cpu string` | 缩放前的基础 vCPU 数，整数 1–256；最终 CPU 数也不能超过 256 | 1.2.0 |
| `-D, --disk string` | 根盘绝对容量，裸整数单位为 GiB，例如 `128GiB`；至少达到基础镜像虚拟容量 | 1.2.0 |
| `-f, --file string` | 显式清单路径；生命周期命令依次使用该文件、当前目录发现的清单、已应用状态 | 1.1.0 |
| `-I, --image string` | 镜像引用，如 `u24`、`el9:stable` 或 `d13@20261103`；覆盖所选节点的 `vm_image/vm_version` | 1.1.0 |
| `-M, --mem string` | 缩放前的基础内存，裸整数单位为 MiB，例如 `4GiB`；至少 512 MiB | 1.2.0 |
| `--mirror` | 使用中国官方源 `https://repo.pigsty.cc/barn`；显式 `--repo` 优先 | 1.1.0 |
| `-n, --no-wait` | QEMU 启动并通过进程身份核验后返回；SSH 就绪与客机恢复延后到下一次 `up` | 1.1.0 |
| `-p, --parallel int` | 节点并发上限；省略时为 `max(1, 逻辑 CPU 数 - 2)`，`0` 表示所选节点全部并发 | 1.2.0 |
| `-r, --repo string` | 镜像仓库 URL 或本地目录，优先于 `BARN_REPO`；支持 `--mirror` 的命令中也优先于该选项 | 1.1.0 |
| `--rollback` | 清理本次准备失败节点中尚未提交、可以安全回收的制品 | 1.1.0 |
| `-S, --scale string` | CPU 与内存的整数倍率，1–256；磁盘容量不缩放 | 1.2.0 |
{.wide .expand}

```bash
barn reload -f pigsty.yml
barn reload meta --mirror
```

## `barn resize` {#barn-resize}

```text
barn resize [node...] [flags]
```

调整 CPU/内存并扩大根盘，保留 VM 身份、磁盘与 SSH 密钥。目标规格来自清单、环境变量或命令行覆盖。支持的 CPU/内存增加操作使用热插拔，减少资源或不支持在线修改时使用停机再启动。镜像、架构、数据盘、网络、共享目录、节点创建和移除均不能通过 resize 应用。

1.2.0 还接受资源参数，并可用 `-D 128GiB` 原地扩容根盘：停止 QEMU、扩展镜像、启动客机扩展并核验最后一个普通 ext4/XFS 根分区，原先停止的 VM 最后恢复为停止状态。目标只能增加，且须对齐 512 字节。中断后用同一目标重试；不支持缩小、LVM、加密根盘或非末尾分区。详见[根盘扩容与恢复](../../cli/#root-disk-growth)。命令行覆盖不改写清单。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-A, --arch string` | 客机架构：`native`、`amd64`、`arm64`；也接受 `x86_64`、`x64`、`aarch64`、`a64` | 1.1.0 |
| `-C, --cpu string` | 缩放前的基础 vCPU 数，整数 1–256；最终 CPU 数也不能超过 256 | 1.2.0 |
| `-D, --disk string` | 根盘绝对容量，裸整数单位为 GiB，例如 `128GiB`；至少达到基础镜像虚拟容量 | 1.2.0 |
| `-f, --file string` | 显式清单路径；生命周期命令依次使用该文件、当前目录发现的清单、已应用状态 | 1.1.0 |
| `-I, --image string` | 镜像引用，如 `u24`、`el9:stable` 或 `d13@20261103`；覆盖所选节点的 `vm_image/vm_version` | 1.1.0 |
| `-M, --mem string` | 缩放前的基础内存，裸整数单位为 MiB，例如 `4GiB`；至少 512 MiB | 1.2.0 |
| `-S, --scale string` | CPU 与内存的整数倍率，1–256；磁盘容量不缩放 | 1.2.0 |
{.wide .expand}

```bash
barn plan -f pigsty.yml meta
barn resize -f pigsty.yml meta
barn --json status meta
```

## `barn recreate` {#barn-recreate}

```text
barn recreate [node...] [flags]
```

按期望清单替换所选 VM，会删除这些节点的根盘与非持久数据盘，并重新挂接兼容的持久盘。先用 `plan` 检查范围；终端要求输入 `recreate`，脚本必须传 `--yes` 或 `--force`，没有 `-y` 简写。

不选节点时应用整个清单；清单遗漏已有节点会在停止 VM 前报错，需先显式销毁该节点或将它加回清单。选择性重建保留其他节点，成功后也会刷新 SSH 访问配置。

别名：`rc`。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-A, --arch string` | 客机架构：`native`、`amd64`、`arm64`；也接受 `x86_64`、`x64`、`aarch64`、`a64` | 1.1.0 |
| `-C, --cpu string` | 缩放前的基础 vCPU 数，整数 1–256；最终 CPU 数也不能超过 256 | 1.2.0 |
| `-D, --disk string` | 根盘绝对容量，裸整数单位为 GiB，例如 `128GiB`；至少达到基础镜像虚拟容量 | 1.2.0 |
| `-f, --file string` | 显式清单路径；生命周期命令依次使用该文件、当前目录发现的清单、已应用状态 | 1.1.0 |
| `--force` | 跳过交互确认；无终端执行销毁或重建时必须显式确认 | 1.1.0 |
| `-I, --image string` | 镜像引用，如 `u24`、`el9:stable` 或 `d13@20261103`；覆盖所选节点的 `vm_image/vm_version` | 1.1.0 |
| `-M, --mem string` | 缩放前的基础内存，裸整数单位为 MiB，例如 `4GiB`；至少 512 MiB | 1.2.0 |
| `--mirror` | 使用中国官方源 `https://repo.pigsty.cc/barn`；显式 `--repo` 优先 | 1.1.0 |
| `-n, --no-wait` | QEMU 启动并通过进程身份核验后返回；SSH 就绪与客机恢复延后到下一次 `up` | 1.1.0 |
| `-p, --parallel int` | 节点并发上限；省略时为 `max(1, 逻辑 CPU 数 - 2)`，`0` 表示所选节点全部并发 | 1.2.0 |
| `-r, --repo string` | 镜像仓库 URL 或本地目录，优先于 `BARN_REPO`；支持 `--mirror` 的命令中也优先于该选项 | 1.1.0 |
| `-S, --scale string` | CPU 与内存的整数倍率，1–256；磁盘容量不缩放 | 1.2.0 |
| `--yes` | 确认并执行显示的计划；系统 `sudo` 仍可能要求密码 | 1.1.0 |
{.wide .expand}

```bash
barn plan meta
barn recreate meta
barn recreate -f pigsty.yml meta --yes
```

## `barn status` {#barn-status}

```text
barn status [node...] [flags]
```

检查已记录的节点配置与当前 QEMU 进程身份，无需位于清单目录。`running` 表示已核验 VM 进程存在，不能据此判断 SSH 就绪。`--verbose` 增加运行时细节，`--json` 返回节点记录、正在进行的操作说明和失败信息。退化节点可能使命令退出 `5`，健康节点仍会列出。1.2.0 文本输出使用 `2c4g` 这样的紧凑 `SPEC` 值。

别名：`st`。

除 `--help` 外没有局部选项，仍可使用全局输出选项。

```bash
barn status
barn status meta --verbose
barn --json status
```

## `barn destroy` {#barn-destroy}

```text
barn destroy [node...] [flags]
```

删除所选 VM，未指定节点时删除整套部署。根盘与非持久数据盘会被删除，持久盘默认保留；终端要求输入 `destroy`，脚本必须传 `--yes` 或 `--force`，没有 `-y`。

`--delete-persistent` 和 `--purge` 仅支持整套部署，后者还删除部署密钥与状态。镜像缓存、宿主网络和原生 Mac VM 保留。删除控制节点后，第一个剩余节点接任控制角色；随后更新 `admin_ip` 并运行 `up` 配置其控制 SSH 访问。

别名：`de`。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `--delete-persistent` | 同时删除归 Barn 所有的持久数据盘，仅支持整套部署 | 1.1.0 |
| `--force` | 跳过交互确认；无终端执行销毁或重建时必须显式确认 | 1.1.0 |
| `-p, --parallel int` | 节点并发上限；省略时为 `max(1, 逻辑 CPU 数 - 2)`，`0` 表示所选节点全部并发 | 1.2.0 |
| `--purge` | 同时删除持久盘、部署密钥与状态，仅支持整套部署 | 1.1.0 |
| `--yes` | 确认并执行显示的计划；系统 `sudo` 仍可能要求密码 | 1.1.0 |
{.wide .expand}

```bash
barn destroy meta
barn destroy --yes
barn destroy --yes --purge
```

## `barn purge` {#barn-purge}

```text
barn purge [flags]
```

立即删除整套 Linux 部署，包括根盘、持久数据盘、密钥、状态和默认 SSH 配置片段，不接受节点名或读取清单。没有 `--yes`、`-y`、`--force` 选项；需要先审阅范围时用 `--ask`，输入 `y/yes` 确认，回车取消。

镜像缓存、宿主网络和 Mac VM 保留。部署不存在时幂等成功，遗留制品身份不明时仍需核验。1.2.0 的 `--parallel` 控制清理过程中的节点并发。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `--ask` | 先显示节点与删除范围，要求输入 `y/yes`；`n/no` 或回车取消 | 1.1.0 |
| `-p, --parallel int` | 节点并发上限；省略时为 `max(1, 逻辑 CPU 数 - 2)`，`0` 表示所选节点全部并发 | 1.2.0 |
{.wide .expand}

```bash
barn purge --ask
barn --json purge
```

## 实现依据 {#implementation}

[command_lifecycle.go](https://github.com/pgsty/barn/blob/v1.2.0/cmd/barn/command_lifecycle.go) · [main.go](https://github.com/pgsty/barn/blob/v1.2.0/cmd/barn/main.go)

发布源码与相对 1.1.0 的变化见[版本基线](/zh/docs/reference/commands/#versions)。
