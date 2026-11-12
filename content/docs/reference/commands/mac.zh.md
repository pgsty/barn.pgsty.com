---
title: macOS 命令
description: 管理具名原生 macOS VM、桌面访问、恢复镜像与共享基础镜像。
weight: 70
date: 2026-11-11
---

管理具名原生 macOS VM、桌面访问、恢复镜像与共享基础镜像。

下列选项均存在于 1.1.0 和 1.2.0。

原生 macOS VM 需要 Apple Silicon、macOS 27+ 与匹配的 `Barn.app`（宿主上的原生应用包），应由已登录桌面的普通用户运行。状态位于 `$BARN_HOME/mac`，独立于 Linux 清单。

省略可选名称时，Barn 选择唯一已有 VM 或 `mac1`；存在多台机器且没有 `mac1` 时需显式指定。`configure`、`recreate`、`destroy` 始终要求名称，`start`、`stop` 可以传多个名称或 `--all`。宿主各应用合计最多同时运行两台 macOS VM，正在安装的基础镜像也计入限制。详见[机器规则、网络、输出与文件](../../mac/)。

Mac 容量单位采用二进制，即使写作 `GB` 也是如此，与 Linux 清单中的十进制 `GB` 不同；Mac 裸容量数字表示字节。这些命令忽略 Linux 的 `BARN_IMAGE/BARN_ARCH/BARN_CPU/BARN_MEM/BARN_SCALE/BARN_DISK` 覆盖。

## `barn mac ls` {#barn-mac-ls}

```text
barn mac ls [flags]
```

列出每台 VM 的状态、地址、SSH 就绪情况、macOS 版本和资源，读取本地记录并查询运行中机器，不创建、下载或启动 VM。别名为 `list`、`status`、`st`；直接运行 `barn mac` 也执行此操作。

别名：`list`, `status`, `st`。

除 `--help` 外没有局部选项，仍可使用全局输出选项。

```bash
barn mac ls
barn --json mac ls
```

## `barn mac up` {#barn-mac-up}

```text
barn mac up [name] [flags]
```

创建并启动具名 VM，默认名称为 `mac1`，等待 SSH 和免密 sudo 可用。没有已准备基础镜像时，先确认从 Apple 下载并安装 macOS，后续机器复用基础镜像。

创建参数只用于新 VM，已有 VM 的参数不匹配会报配置冲突；修改 CPU、内存或共享目录用 `configure`。`--no-wait` 返回时首次初始化可能尚未完成，随后运行不带该选项的 `mac up NAME` 完成密钥和 sudo 配置。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `--clipboard on\|off` | `on/off`，也接受 `true/false`、`yes/no`；新 VM 默认开启，仅在桌面窗口聚焦时共享 | 1.1.0 |
| `--cpu int` | vCPU 数，默认 4；最小 2，最大为宿主逻辑 CPU 数；`configure` 省略时保留原值 | 1.1.0 |
| `--disk size` | 基础镜像磁盘容量，最小 32 GiB；首次默认 100 GiB，`up` 优先沿用已准备基础镜像的容量 | 1.1.0 |
| `--ipsw string` | 使用本地 Apple IPSW 恢复文件 | 1.1.0 |
| `--memory size` | 内存，默认 8 GiB；必须为整 MiB，范围为 4 GiB 至宿主内存；`configure` 省略时保留原值 | 1.1.0 |
| `-n, --no-wait` | VM 进程运行后返回；首次启动可能仍在初始化，随后运行 `mac up NAME` 完成就绪检查 | 1.1.0 |
| `--open` | VM 启动后打开桌面窗口 | 1.1.0 |
| `--share [name=]path[:ro]` | 可重复：`[name=]path[:ro\|:rw]`；默认可写，在客机 `/Volumes/My Shared Files` 中显示 | 1.1.0 |
| `--subnet string` | 独立的私有 `/24` 子网；`auto` 自动选择空闲子网，新 VM 默认自动选择 | 1.1.0 |
| `--user string` | 客机管理员用户名；默认宿主 macOS 用户名，名称无效时用 `barn` | 1.1.0 |
| `-y, --yes` | 下载 Apple 恢复镜像前跳过询问；无终端下载时需要 | 1.1.0 |
{.wide .expand}

```bash
barn mac up
barn mac up dev --cpu 8 --memory 16G --share ~/src --open
barn mac up build --yes --no-wait
```

## `barn mac start` {#barn-mac-start}

```text
barn mac start [name...] [flags]
```

启动已有 VM 并等待 SSH，不创建机器或下载镜像。可传多个名称或 `--all`，两者不能混用。普通启动要求机器已完成首次初始化；尚未初始化的 VM 用 `up` 完成，`--recovery` 则直接打开 macOS Recovery 桌面。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `--all` | 选择全部已有 VM；不能同时指定名称 | 1.1.0 |
| `-n, --no-wait` | VM 进程运行后返回；首次启动可能仍在初始化，随后运行 `mac up NAME` 完成就绪检查 | 1.1.0 |
| `--open` | VM 启动后打开桌面窗口 | 1.1.0 |
| `--recovery` | 启动 macOS Recovery 并打开桌面，不等待普通 SSH 就绪 | 1.1.0 |
{.wide .expand}

```bash
barn mac start mac1
barn mac start --all
barn mac start mac1 --recovery
```

## `barn mac stop` {#barn-mac-stop}

```text
barn mac stop [name...] [flags]
```

通过 macOS 正常关闭所选机器，等待两分钟后仍未停止则断电，并在结果中报告。可传多个名称或 `--all`；`--force` 立即断电，会丢失客机中未保存的工作。磁盘和机器配置保留。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `--all` | 选择全部已有 VM；不能同时指定名称 | 1.1.0 |
| `--force` | 立即断电，客机中未保存的工作会丢失 | 1.1.0 |
{.wide .expand}

```bash
barn mac stop dev
barn mac stop --all
barn mac stop dev --force
```

## `barn mac restart` {#barn-mac-restart}

```text
barn mac restart [name] [flags]
```

正常关闭一台 VM 后重新启动并应用配置，省略名称时遵循默认机器选择规则。不接受多个名称或 `--all`；可用 `--open` 打开桌面，`--no-wait` 跳过 SSH 等待。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-n, --no-wait` | VM 进程运行后返回；首次启动可能仍在初始化，随后运行 `mac up NAME` 完成就绪检查 | 1.1.0 |
| `--open` | VM 启动后打开桌面窗口 | 1.1.0 |
{.wide .expand}

```bash
barn mac restart dev
barn mac restart dev --open
```

## `barn mac configure` {#barn-mac-configure}

```text
barn mac configure <name> [flags]
```

必须显式指定一台已有 VM，修改 CPU、内存、共享目录或子网时需先停止机器；剪贴板设置可以在运行时修改。磁盘和登录账户保持原样，配置在下次启动生效；当前会话的剪贴板同步可在菜单栏即时切换。省略的选项保留原设置，重复 `--share` 可添加或替换同名共享，`--unshare` 按名称移除共享。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `--clipboard on\|off` | `on/off`，也接受 `true/false`、`yes/no`；新 VM 默认开启，仅在桌面窗口聚焦时共享 | 1.1.0 |
| `--cpu int` | vCPU 数，默认 4；最小 2，最大为宿主逻辑 CPU 数；`configure` 省略时保留原值 | 1.1.0 |
| `--memory size` | 内存，默认 8 GiB；必须为整 MiB，范围为 4 GiB 至宿主内存；`configure` 省略时保留原值 | 1.1.0 |
| `--share [name=]path[:ro]` | 可重复：`[name=]path[:ro\|:rw]`；默认可写，在客机 `/Volumes/My Shared Files` 中显示 | 1.1.0 |
| `--subnet string` | 独立的私有 `/24` 子网；`auto` 自动选择空闲子网，新 VM 默认自动选择 | 1.1.0 |
| `--unshare stringArray` | 可重复：删除指定名称的共享目录配置 | 1.1.0 |
{.wide .expand}

```bash
barn mac stop dev
barn mac configure dev --cpu 8 --memory 16G --share ~/src
barn mac configure dev --unshare src --clipboard off
barn mac start dev
```

## `barn mac recreate` {#barn-mac-recreate}

```text
barn mac recreate <name> [flags]
```

必须显式指定机器名。擦除该 VM 磁盘，使用原名称、账户、资源、共享目录和地址重新克隆 macOS，客机文件、应用和设置全部丢失。终端要求输入 `recreate`，脚本需 `--yes` 或 `--force`，没有 `-y`。`--update` 使用最新已准备基础镜像，应先执行 `mac image update`。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `--force` | 跳过销毁或重建的确认；无终端时必须显式确认 | 1.1.0 |
| `-n, --no-wait` | VM 进程运行后返回；首次启动可能仍在初始化，随后运行 `mac up NAME` 完成就绪检查 | 1.1.0 |
| `--update` | 重建时使用最新已准备的基础镜像，先运行 `mac image update` | 1.1.0 |
| `--yes` | 等同于 `--force`；没有 `-y` 简写 | 1.1.0 |
{.wide .expand}

```bash
barn mac recreate dev
barn mac image update --yes
barn mac recreate dev --update --yes
```

## `barn mac destroy` {#barn-mac-destroy}

```text
barn mac destroy <name...> [flags]
```

必须显式指定一个或多个机器名，将机器断电并删除磁盘、密钥、密码和设置，保留共享基础镜像和其他机器。终端要求输入 `destroy`，脚本需 `--yes` 或 `--force`，没有 `-y`。宿主共享目录不会删除；未使用基础镜像用 `mac image prune` 清理。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `--force` | 跳过销毁或重建的确认；无终端时必须显式确认 | 1.1.0 |
| `--yes` | 等同于 `--force`；没有 `-y` 简写 | 1.1.0 |
{.wide .expand}

```bash
barn mac destroy dev
barn mac destroy mac1 mac2 --yes
```

## `barn mac open` {#barn-mac-open}

```text
barn mac open [name] [flags]
```

显示 VM 的桌面窗口，机器已停止时会先启动。关闭窗口后 VM 继续在后台运行，剪贴板在窗口聚焦时共享。尚未完成首次初始化且已运行的 VM 可直接打开桌面；未运行时用 `mac up NAME --open` 继续首次启动。

除 `--help` 外没有局部选项，仍可使用全局输出选项。

```bash
barn mac open
barn mac open dev
```

## `barn mac ssh` {#barn-mac-ssh}

```text
barn mac ssh [flags] [name] [-- command...]
```

使用该 VM 专属 SSH 私钥与固定的宿主密钥连接，省略远程命令时打开交互 shell。`--` 前最多传一个已有机器名及 Barn 选项；远程命令必须放在 `--` 后，按普通 SSH 方式拼接后交给远程 shell。远程退出码原样返回。

除 `--help` 外没有局部选项，仍可使用全局输出选项。

```bash
barn mac ssh dev
barn mac ssh dev -- 'sw_vers; id'
```

## `barn mac exec` {#barn-mac-exec}

```text
barn mac exec [flags] [name] -- command...
```

使用 VM 专属 SSH 连接运行远程程序，必须提供 `--` 和非空首参数；分开的参数保留边界及后续空值，shell 表达式请显式使用 `sh -c`。也兼容单个命令字符串。Barn 选项置于 `--` 前，远程退出码原样返回，结构化结果包含 stdout、stderr 和 exit_code。

除 `--help` 外没有局部选项，仍可使用全局输出选项。

```bash
barn mac exec dev -- sw_vers
barn mac exec dev -- printf '<%s>\n' 'a b' ''
barn --json mac exec dev -- sh -c 'echo out; exit 3'
```

## `barn mac password` {#barn-mac-password}

```text
barn mac password [name] [flags]
```

读取客机登录账户的密码，用于桌面解锁及管理员询问。默认输出密码，`--copy` 改为复制到宿主剪贴板。密码文件与机器 SSH 私钥采用相同保护；注意选择输出位置。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-c, --copy` | 复制登录密码到宿主剪贴板，替代终端明文输出 | 1.1.0 |
{.wide .expand}

```bash
barn mac password dev
barn mac password dev --copy
```

## `barn mac ssh-config` {#barn-mac-ssh-config}

```text
barn mac ssh-config [flags]
```

打印全部 Mac VM 的 OpenSSH 配置片段，支持 ssh、scp、rsync 和编辑器按名称连接，每台机器使用独立私钥与固定宿主密钥。首台 VM 就绪时自动安装，生命周期命令持续更新。`--remove` 移除配置并保持停用，直到显式 `--install`；两选项互斥，也不接受机器选择器。已有 SSH 别名冲突时仅发布 IP 地址条目。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-i, --install` | 安装 `~/.ssh/barn-mac_config` 及其 `Include`，并重新启用自动维护 | 1.1.0 |
| `--remove` | 移除 Barn 安装的 Mac SSH 配置，并保持停用直到显式 `--install` | 1.1.0 |
{.wide .expand}

```bash
barn mac ssh-config
barn mac ssh-config --install
barn mac ssh-config --remove
```

## `barn mac logs` {#barn-mac-logs}

```text
barn mac logs [name] [flags]
```

读取 VM 的 `runner.log` 尾部，包含启动、网络、关闭和 Apple Virtualization 错误。`--lines/-n` 为正整数，默认 100；这里的 `-n` 表示行数，不是跳过等待。没有跟随选项。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-n, --lines int` | 读取最近的日志行数，正整数，默认 100 | 1.1.0 |
{.wide .expand}

```bash
barn mac logs dev
barn mac logs dev --lines 200
```

## `barn mac setup` {#barn-mac-setup}

```text
barn mac setup [flags]
```

提前准备共享 macOS 基础镜像：确认后从 Apple 下载 IPSW，或读取 `--ipsw` 指定的本地恢复文件，再安装为未启动的基础镜像。后续 VM 从它克隆。此命令不创建具名机器；直接 `mac up` 也会在需要时自动执行此准备。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `--disk size` | 基础镜像磁盘容量，最小 32 GiB；首次默认 100 GiB，`up` 优先沿用已准备基础镜像的容量 | 1.1.0 |
| `--ipsw string` | 使用本地 Apple IPSW 恢复文件 | 1.1.0 |
| `-y, --yes` | 下载 Apple 恢复镜像前跳过询问；无终端下载时需要 | 1.1.0 |
{.wide .expand}

```bash
barn mac setup --yes
barn mac setup --ipsw ~/Downloads/restore.ipsw --disk 200G
```

## `barn mac image ls` {#barn-mac-image-ls}

```text
barn mac image ls [flags]
```

列出缓存的 IPSW 恢复文件和已准备基础镜像，包括状态、占用空间及使用它们的 VM；别名为 `list`。这是本地状态查询，无需调用原生运行器。

别名：`list`。

除 `--help` 外没有局部选项，仍可使用全局输出选项。

```bash
barn mac image ls
barn --json mac image ls
```

## `barn mac image update` {#barn-mac-image-update}

```text
barn mac image update [flags]
```

从 Apple 查询最新 macOS 27 恢复镜像，经确认后下载并安装为新机器的默认基础镜像；也可通过 `--ipsw` 指定本地文件。已有 VM 继续使用原基础镜像，显式 `mac recreate NAME --update` 才替换该 VM 磁盘。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `--ipsw string` | 使用本地 Apple IPSW 恢复文件 | 1.1.0 |
| `-y, --yes` | 下载 Apple 恢复镜像前跳过询问；无终端下载时需要 | 1.1.0 |
{.wide .expand}

```bash
barn mac image update --yes
barn mac image ls
```

## `barn mac image prune` {#barn-mac-image-prune}

```text
barn mac image prune [flags]
```

默认列出没有机器使用、且不是当前默认基础镜像的清理候选，只有传 `--yes` 才删除。`--installers` 同时纳入下载的 IPSW 与未完成下载。VM 的引用关系会保护仍在使用的基础镜像。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `--installers` | 将下载的 IPSW 与未完成下载也纳入清理范围 | 1.1.0 |
| `-y, --yes` | 删除列出的未使用镜像；省略时仅预览 | 1.1.0 |
{.wide .expand}

```bash
barn mac image prune
barn mac image prune --installers --yes
```

## `barn mac doctor` {#barn-mac-doctor}

```text
barn mac doctor [flags]
```

只读检查宿主 macOS 与 Apple Silicon 支持、Mac 组件签名、可用磁盘空间、基础镜像以及每台 VM 的文件、密钥、共享目录、网络和 SSH，不修改或启动机器。Linux/QEMU 环境用顶层 `barn doctor` 检查。

除 `--help` 外没有局部选项，仍可使用全局输出选项。

```bash
barn mac doctor
barn --json mac doctor
```

## 实现依据 {#implementation}

[command_mac.go](https://github.com/pgsty/barn/blob/v1.2.0/cmd/barn/command_mac.go)

发布源码与相对 1.1.0 的变化见[版本基线](/zh/docs/reference/commands/#versions)。
