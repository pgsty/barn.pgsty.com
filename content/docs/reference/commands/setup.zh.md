---
title: 准备与工具
description: 生成清单、准备宿主、校验配置，以及查看版本和生成补全脚本。
weight: 10
date: 2026-11-11
---

生成清单、准备宿主、校验配置，以及查看版本和生成补全脚本。

本参考对应 **Barn 1.2.0**；选项表区分 **1.1.0 已有选项** 与 **1.2.0 新增选项**，具体范围见[版本基线](/zh/docs/reference/commands/#versions)。所有命令继承[全局选项](/zh/docs/reference/commands/#global-options)。

## `barn setup` {#barn-setup}

```text
barn setup [meta|dual|trio|full] [flags]
```

准备宿主软件包、固定 IP 网络、镜像与所选清单，然后运行 `barn up` 创建 Linux VM。`meta`、`dual`、`trio`、`full` 模板分别包含 1、2、3、4 个节点；未指定模板或 `-f` 时复用发现的清单，没有清单才生成 `meta`。`-c` 与规格选项用于生成模板，显式规格选项不能用来改写已有清单；1.2.0 复用清单时也忽略规格环境变量。

`--dry-run` 预览整个事务。执行需要终端确认或 `--yes`，系统提权仍可能询问密码。新生成且未经编辑的默认模板遇到子网冲突时，setup 可以选择空闲私有 `/24`，并将原模板备份为 `barn.yml.before-network-change`；显式清单保留原子网。Linux 宿主运行异架构客机时，需要另外安装目标 QEMU 模拟器与固件。

别名：`s`。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-A, --arch string` | 客机架构：`native`、`amd64`、`arm64`；也接受 `x86_64`、`x64`、`aarch64`、`a64` | 1.1.0 |
| `-c, --cidr string` | 规范的 RFC1918 IPv4 `/24` 子网；模板与网络安装默认 `10.10.10.0/24` | 1.1.0 |
| `-C, --cpu string` | 缩放前的基础 vCPU 数，整数 1–256；最终 CPU 数也不能超过 256 | 1.2.0 |
| `-D, --disk string` | 根盘绝对容量，裸整数单位为 GiB，例如 `128GiB`；至少达到基础镜像虚拟容量 | 1.2.0 |
| `-d, --dry-run` | 仅预览计划，不修改状态 | 1.1.0 |
| `-f, --file string` | 要准备的清单；不能与模板位置参数同时使用 | 1.1.0 |
| `-I, --image string` | 镜像引用，如 `u24`、`el9:stable` 或 `d13@20261103`；覆盖所选节点的 `vm_image/vm_version` | 1.1.0 |
| `-M, --mem string` | 缩放前的基础内存，裸整数单位为 MiB，例如 `4GiB`；至少 512 MiB | 1.2.0 |
| `--mirror` | 使用中国官方源 `https://repo.pigsty.cc/barn`；显式 `--repo` 优先 | 1.1.0 |
| `-m, --mode string` | macOS 的 `socket_vmnet` 模式：`host`（默认）或 `shared` | 1.1.0 |
| `-r, --repo string` | 镜像仓库 URL 或本地目录，优先于 `BARN_REPO`；支持 `--mirror` 的命令中也优先于该选项 | 1.1.0 |
| `-S, --scale string` | CPU 与内存的整数倍率，1–256；磁盘容量不缩放 | 1.2.0 |
| `-y, --yes` | 确认并执行显示的计划；系统 `sudo` 仍可能要求密码 | 1.1.0 |
{.wide .expand}

```bash
barn setup --dry-run
barn setup full -I el9 --yes
barn setup -f pigsty.yml --yes
barn up
```

## `barn init` {#barn-init}

```text
barn init [meta|dual|trio|full] [flags]
```

生成兼容 Pigsty 的 YAML 清单，默认在 `./barn.yml` 写入单节点 `meta` 模板，控制节点地址为 `.10`；`dual`、`trio`、`full` 依次增加 `.11`、`.12`、`.13` 节点。覆盖已有文件必须加 `--force`，`-o -` 将清单输出到 stdout。本命令不下载镜像或准备宿主。

Barn 1.2.0 每节点默认 1 vCPU、2 GiB，使用 64 GiB 根盘和独立的 128 GiB `/data` 盘；生成的模板保存六项规格字段，包括 `vm_scale`。1.1.0 的 CPU 与内存默认值为 2 vCPU、4 GiB。详见[规格默认值](../../configuration/#specification-overrides)。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-A, --arch string` | 客机架构：`native`、`amd64`、`arm64`；也接受 `x86_64`、`x64`、`aarch64`、`a64` | 1.1.0 |
| `-c, --cidr string` | 规范的 RFC1918 IPv4 `/24` 子网；模板与网络安装默认 `10.10.10.0/24` | 1.1.0 |
| `-C, --cpu string` | 缩放前的基础 vCPU 数，整数 1–256；最终 CPU 数也不能超过 256 | 1.2.0 |
| `-D, --disk string` | 根盘绝对容量，裸整数单位为 GiB，例如 `128GiB`；至少达到基础镜像虚拟容量 | 1.2.0 |
| `--force` | 覆盖目标清单文件；默认保留已有文件 | 1.1.0 |
| `-I, --image string` | 镜像引用，如 `u24`、`el9:stable` 或 `d13@20261103`；覆盖所选节点的 `vm_image/vm_version` | 1.1.0 |
| `-M, --mem string` | 缩放前的基础内存，裸整数单位为 MiB，例如 `4GiB`；至少 512 MiB | 1.2.0 |
| `-o, --output string` | 目标文件，默认 `./barn.yml`；`-` 表示输出到 stdout | 1.1.0 |
| `-S, --scale string` | CPU 与内存的整数倍率，1–256；磁盘容量不缩放 | 1.2.0 |
{.wide .expand}

```bash
barn init
barn init full -I el9 -A amd64 -o lab.yml
barn init dual -c 10.20.30.0/24 -o -
```

## `barn validate` {#barn-validate}

```text
barn validate [flags]
```

读取清单并校验 Barn 使用的字段，输出解析后的节点；不接受节点位置参数。未指定 `-f` 时依次在当前目录寻找 `barn.yml`、`barn.yaml`、`pigsty.yml`、`pigsty.yaml`；找不到清单就报错，即使存在已应用状态也不回退。覆盖参数仅对本次校验生效，`--json` 可查看解析后的规格，与现有部署比较则用 `plan`。

别名：`v`。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-A, --arch string` | 客机架构：`native`、`amd64`、`arm64`；也接受 `x86_64`、`x64`、`aarch64`、`a64` | 1.1.0 |
| `-C, --cpu string` | 缩放前的基础 vCPU 数，整数 1–256；最终 CPU 数也不能超过 256 | 1.2.0 |
| `-D, --disk string` | 根盘绝对容量，裸整数单位为 GiB，例如 `128GiB`；至少达到基础镜像虚拟容量 | 1.2.0 |
| `-f, --file string` | 要校验的清单；省略时在当前目录发现，不回退到已应用状态 | 1.1.0 |
| `-I, --image string` | 镜像引用，如 `u24`、`el9:stable` 或 `d13@20261103`；覆盖所选节点的 `vm_image/vm_version` | 1.1.0 |
| `-M, --mem string` | 缩放前的基础内存，裸整数单位为 MiB，例如 `4GiB`；至少 512 MiB | 1.2.0 |
| `-r, --repo string` | 镜像仓库 URL 或本地目录，优先于 `BARN_REPO`；支持 `--mirror` 的命令中也优先于该选项 | 1.1.0 |
| `-S, --scale string` | CPU 与内存的整数倍率，1–256；磁盘容量不缩放 | 1.2.0 |
{.wide .expand}

```bash
barn validate -f lab.yml
barn --json validate -f lab.yml -I u24 -A arm64
```

## `barn doctor` {#barn-doctor}

```text
barn doctor [flags]
```

检查 QEMU、原生加速、固件、OpenSSH、短暂的加速启动测试和宿主网络；不接受清单或节点参数。缺少计算能力时命令失败，尚未准备网络则作为提示报告。网络细节用 `barn network status` 检查，原生 macOS VM 用 `barn mac doctor`。

别名：`dt`。

除 `--help` 外没有局部选项，仍可使用全局输出选项。

```bash
barn doctor
barn --json doctor
barn doctor --verbose
```

## `barn version` {#barn-version}

```text
barn version [flags]
```

输出版本、源码提交、构建时间、宿主操作系统与架构。1.2.0 通常显示 `dev`，正式版本标识来自构建时写入的信息。核对文档或提交问题时保留这份输出，也可用根命令的 `barn --version`。

别名：`ver`。

除 `--help` 外没有局部选项，仍可使用全局输出选项。

```bash
barn version
barn --json version
```

## `barn completion` {#barn-completion}

```text
barn completion [bash|zsh|fish|powershell] [flags]
```

必须指定 `bash`、`zsh`、`fish` 或 `powershell` 中的一种 shell，将补全脚本输出到 stdout；命令本身不安装脚本。补全涵盖各命令的选项、模板、镜像别名与可读取的节点名，升级 Barn 后应重新加载。加载 shell 代码时使用文本输出。

除 `--help` 外没有局部选项，仍可使用全局输出选项。

```bash
source <(barn completion bash)
barn completion zsh > "${fpath[1]}/_barn"
barn completion fish > ~/.config/fish/completions/barn.fish
barn completion powershell
```

## 实现依据 {#implementation}

[command_setup.go](https://github.com/pgsty/barn/blob/v1.2.0/cmd/barn/command_setup.go) · [command_misc.go](https://github.com/pgsty/barn/blob/v1.2.0/cmd/barn/command_misc.go) · [command_root.go](https://github.com/pgsty/barn/blob/v1.2.0/cmd/barn/command_root.go)

发布源码与相对 1.1.0 的变化见[版本基线](/zh/docs/reference/commands/#versions)。
