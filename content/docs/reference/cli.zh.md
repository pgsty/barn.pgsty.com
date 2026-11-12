---
title: CLI 契约
description: Barn 命令、关键参数、结构化输出与退出码。
weight: 20
icon: fa-solid fa-terminal
aliases: [/docs/reference/json-api/]
---

本页说明 Barn 1.2.0 的全局展示、Linux 生命周期语义、结构化输出与退出码；各命令的语法、选项、默认值与示例见[命令参考](../commands/)。原生 Mac 运行时契约见 [Mac 参考](../mac/)。

```text
barn [--json|--yaml] [-v|--verbose] <command> [flags] [node...]
```

每条命令都提供内置 `--help`，用于查看当前二进制支持的参数与示例：

```bash
barn --help
barn setup --help
barn image pull --help
```

不带参数直接运行 `barn` 会打印与 `barn --help` 相同的完整帮助并以退出码 `0` 返回；传入 `--json` 或 `--yaml` 时则返回由建议命令组成的 `actions[]` 数组。只输入命令分组而不带子命令（如 `barn image`）会以退出码 `2` 返回（文本模式输出帮助，JSON/YAML 模式输出结构化 `usage` 错误）。显式传入 `--help` 始终打印人类可读的帮助文本并以 `0` 退出。查看构建版本信息请使用 `barn --version` 或 `barn version`。

## 命令 {#commands}

| 类别 | 命令 |
|---|---|
| 环境准备 | `setup`、`init`、`validate`、`doctor` |
| 生命周期 | `plan`、`up`、`start`、`stop`、`restart`、`reload`、`resize`、`recreate`、`status`、`destroy`、`purge` |
| 节点访问 | `ssh`、`exec`、`logs`、`provision`、`ssh-config`、`hosts install/uninstall` |
| 镜像管理 | `update`、`image list/info/pull/import/sync/prune/reset`、`repo scan/build/verify` |
| 宿主网络 | `network status/install/uninstall` |
| macOS 客机 | `mac …` — 见 [Mac 命令](../mac/) |
| 其他工具 | `version`、`completion` |
{.wide .expand}

日常命令只读取本地已激活的镜像目录，不会隐式联网刷新。执行 `barn update` 可拉取、验签并激活所选仓库的最新镜像目录；需要从指定 URL 或本地文件恢复目录时，使用 `barn image sync`。这两条命令都不会更新 `barn` 可执行文件本身。

常用命令在各自作用域内支持短别名：

| 命令 | 别名 | 命令 | 别名 |
|---|---|---|---|
| `setup` | `s` | `validate` | `v` |
| `plan` | `pl` | `recreate` | `rc` |
| `status` | `st` | `destroy` | `de` |
| `ssh-config` | `sc` | `image` | `images`、`im` |
| `doctor` | `dt` | `network` | `n`、`net` |
| `exec` / `logs` | `ex` / `l` | `version` | `ver` |
{.wide .expand}

`up`、`ssh`、`init`、`start`、`stop`、`restart`、`reload`、`resize`、`provision`、`hosts`、`purge`、`update`、`repo`、`mac` 与 `completion` 不设顶层短别名（`rm` 也不是 `purge` 的别名）。在子命令命名空间内，`hosts` 与 `network` 的 `install`/`uninstall` 可简写为 `i`/`u`，`network status` 可简写为 `st`；`image` 下支持 `list=ls`、`info=in`、`pull=p`、`prune=pr`、`sync=sy` 与 `import=i`。

Barn 在每个 `BARN_HOME`（默认 `~/.barn`，详见[配置发现规则](../configuration/#discovery)）中管理唯一一套部署，只要 `BARN_HOME` 指向同一位置，操作已应用状态的命令就可在任意工作目录下执行；跨工作目录使用时请设置绝对 `BARN_HOME`。各条命令按如下规则确定期望配置来源（`-f` 是命令级参数而非全局参数）：

| 命令 | 期望状态来源 |
|---|---|
| `setup [template]` | 优先使用显式 `-f`，其次按目录发现，否则生成 `meta` 模板（`template` 与 `-f` 互斥） |
| `init [template]` | 直接生成新清单，不读取现有状态；传入 `--force` 可覆盖已有文件 |
| `validate` | 优先使用显式 `-f`，其次按目录发现；绝不回退到已应用状态 |
| `plan`、`up`、`reload`、`recreate`、`resize` | 依次查找显式 `-f`、当前目录清单，最后回退到已应用的部署规格 |
| 其他生命周期与访问命令 | 不读取清单文件，直接操作 `BARN_HOME` 中的已应用状态 |
{.wide .expand}

在终端中，如果宿主缺少依赖或 Barn 网络，`up`、`start`、`restart` 与 `reload` 会像 `barn setup` 一样准备宿主：先展示宿主准备计划，在安装软件包或网络前询问一次（涉及特权操作时 `sudo` 仍会提示输入系统密码）。当前目录没有清单且 `BARN_HOME` 中也没有已部署环境时，交互式 `barn up` 还会先生成默认 `meta` 清单。没有终端时，这些命令只报告缺少的条件。运行 `barn setup --dry-run` 可查看准备计划，在脚本中请执行 `barn setup --yes` 准备宿主。

对于全新、未修改的默认模板，若默认 `10.10.10.0/24` 网段与宿主现有路由冲突，`setup` 会自动改选另一个空闲的私有 `/24` 网段，并将原文件备份为 `barn.yml.before-network-change`。显式传入的 `-f` 清单、已手动编辑的模板以及已存在的部署始终保留各自配置的网段。

## 关键参数 {#important-flags}

| 参数 | 含义 |
|---|---|
| `--json`、`--yaml` | 在 stdout 输出机器可读结果，进度信息仍输出到 stderr（仅提供长参数） |
| `-v`、`--verbose` | 在 stderr 输出定长截断的诊断详情 |
| `-c`、`--cidr` | 为 `init`/`setup` 模板或宿主 `network` 检查/安装指定 RFC1918 `/24` 网段 |
| `-I`、`--image` | 为生成模板选择镜像，或在支持覆盖的命令中替代所选节点的 `vm_image`/`vm_version` |
| `-A`、`--arch` | 选择客机或镜像架构：`native`、`amd64`（`x86_64`、`x64`）、`arm64`（`aarch64`、`a64`） |
| `-f`、`--file` | 为读取期望状态的命令指定清单文件 |
| `-r`、`--repo` | 指定镜像仓库 URL 或本地路径，优先级高于 `--mirror` 与 `BARN_REPO` |
| `--mirror` | 为 `setup`、`up`、`reload`、`recreate`、`update` 与 `image pull` 选用中国官方镜像源（`https://repo.pigsty.cc/barn`） |
| `-m`、`--mode` | 在支持该参数的命令上选择 macOS `host` 或 `shared` 网络模式 |
| `-d`、`--dry-run` | 仅打印 `setup` 或 `image prune` 的执行计划，不修改系统状态 |
| `--yes` | 确认宿主、初始化、镜像或销毁计划；仅下表标明的命令支持 `-y` |
| `--force`（`init`、`destroy`、`recreate`） | 覆盖已有清单（`init`）或跳过交互式确认词（因 `-f` 已用于选择清单，故仅设长参数） |
| `--ask`（`purge`） | 删除前展示虚拟机列表与清理范围，要求输入 `y`/`yes` 确认 |
| `-n`、`--no-wait` | QEMU 进程启动后立即返回，跳过客机 SSH 就绪检查、磁盘恢复与配置刷新 |
| `--rollback`（`up`、`reload`） | 清理本次运行中准备失败、尚未提交状态的节点残留文件 |
| `--delete-persistent` | 整体销毁部署时一并删除 `persistent: true` 的持久数据盘 |
| `--purge` | 整体销毁部署时删除全部磁盘、密钥与状态，仅保留镜像缓存与宿主网络 |
{.wide .expand}

各命令支持的局部参数如下表所示：

| 命令 | 专用参数 |
|---|---|
| `init` | `--output/-o`（默认 `./barn.yml`，`-` 表示输出到 stdout）、`--cidr/-c`、`--image/-I`、`--arch/-A`、`--force` |
| `setup [meta\|dual\|trio\|full]` | `--file/-f`、`--cidr/-c`、`--image/-I`、`--arch/-A`、`--repo/-r`、`--mirror`、`--mode/-m`、`--dry-run/-d`、`--yes/-y`（默认模板为 `meta`） |
| `validate` | `--file/-f`、`--repo/-r`、`--image/-I`、`--arch/-A`；不接受节点参数 |
| `plan` | `--file/-f`、`--repo/-r`、`--image/-I`、`--arch/-A` |
| `up`、`reload` | `--file/-f`、`--repo/-r`、`--image/-I`、`--arch/-A`、`--mirror`、`--no-wait/-n`、`--rollback` |
| `recreate` | `--file/-f`、`--repo/-r`、`--image/-I`、`--arch/-A`、`--mirror`、`--yes`/`--force`、`--no-wait/-n` |
| `resize` | `--file/-f`、`--image/-I`、`--arch/-A`（仍只应用 CPU/内存变更） |
| `start`、`restart` | `--no-wait/-n` |
| `stop`、`status` | 仅接受节点选择器与全局展示参数 |
| `destroy` | `--yes`/`--force`、`--delete-persistent`、`--purge`（后两者仅限整套部署） |
| `purge` | 默认直接删除；`--ask` 开启确认；不接受节点参数或 `--yes`、`-y`、`--force` |
| `doctor`、`version` | 仅全局展示参数 |
| `provision` | 必填 `--script/-s`；`--sudo`；`--parallel/-p` 正整数（默认 `1`）；`--timeout/-t` 正时长（默认 `1h`） |
| `ssh-config` | 可选节点选择器；`--install/-i` 与 `--remove` 互斥；`--name` 默认为 `barn`。`--remove` 不接受节点参数，也不要求存在部署状态 |
| `logs` | `--source/-s serial\|qemu\|events`（默认 `serial`）；`--follow/-f`（`events` 为部署级日志，不接受节点名） |
| `image info`、`image pull` | 可选镜像选择器、`--arch/-A`（兼容旧 `-a`）、`--repo/-r`；`pull` 额外支持 `--mirror` |
| `image import` | `--sha256/-s`；命名导入（`--name local-*`）还必须同时传入 `--boot/-b bios\|uefi` 与 `--source-user/-u`，可用 `--arch/-A` 记录客机架构 |
| `image prune` | `--dry-run/-d` 与 `--yes/-y` 互斥；`--repo/-r` |
| `image sync` | 源 URL 或本地路径、`--repo/-r`、可选 `--allow-downgrade` |
| `update` | `--repo/-r`、`--mirror` |
| `image list`、`image reset` | `--repo/-r` |
| `repo scan/build/verify` | 必填一个仓库目录路径，支持相对路径、`~/` 与目录符号链接 |
| `network install` | `--cidr/-c`（默认 `10.10.10.0/24`）、`--mode/-m`（默认 `host`）、`--yes/-y`；macOS 专用 `--archive/-a`、`--interface-id/-i` |
| `network status` | 可选 `--cidr/-c` |
| `network uninstall`、`hosts install/uninstall` | `--yes/-y` |
| `hosts install`（1.2.0） | `--file/-f`：发布清单中的节点与 `vm_hosts`，不要求已创建 VM |
{.wide .expand}

参数使用说明：

- `setup --dry-run` 与 `setup --yes` 互斥。`--cidr` 仅调整新生成模板的网段，不会改写显式指定的 `-f` 清单。若要在 `validate` 时对照中国镜像源校验，请传入 `--repo https://repo.pigsty.cc/barn`。
- `init` 与生成模板的 `setup` 将 `-I`、`-A` 写入 `all.vars.vm_image`、`all.vars.vm_arch`；`setup` 遇到已有清单时拒绝这两个生成参数。`up`、`plan`、`reload`、`recreate`、`resize` 与 `validate` 则在内存中覆盖本次期望配置，不改写清单。镜像覆盖作用于所选节点，架构覆盖作用于整套部署；详见[覆盖优先级与默认值](../configuration/#image-and-architecture)。
- 独立的 `image info/pull/import` 默认取宿主架构，不读取清单的 `vm_arch`；用 `-A` 显式选择。`image import -A` 必须与 `--name` 同用；qcow2 元数据不能识别客机 CPU，所填架构须与实际镜像一致。
- `network` 与 `hosts` 的 `install`/`uninstall` 会先展示变更计划并在终端请求确认（安装默认同意，卸载默认拒绝）。未传 `--yes` 时，如果标准输入不是终端或输出为 `--json`/`--yaml`，命令只输出计划并退出 `0`；请检查结构化报告中的 `applied`，或传入 `--yes` 执行计划。macOS 首次配置宿主网络请使用 `barn setup`。有节点运行时 `network uninstall` 会拒绝卸载网络；停止或销毁虚拟机不会卸载宿主网络。在 Linux 上，若宿主还有其他网络链路，或无法确认 networkd 仅供 Barn 使用，`network uninstall` 会保留全局 networkd 单元状态；计划中报告 `preserve_networkd`，执行报告在 `checks.networkd` 中说明原因。
- 涉及安全确认与仓库选择的开关（`--ask`、`--mirror`、`--force`、`--rollback`、`--remove`、`--allow-downgrade`、`--sudo`、`--delete-persistent`、`--purge`）只提供长参数。在 Linux 命令中，`-f` 表示 `--file`（`barn logs -f` 例外，表示 `--follow`），`-n` 表示 `--no-wait`（而 `barn mac logs -n` 表示日志行数），`-d` 表示 `--dry-run`。
- `barn purge` 默认立即执行整套清理，删除所有节点、持久盘、密钥、部署状态与默认 SSH 配置片段，保留镜像缓存与宿主网络。只有传入 `--ask` 时才先展示节点列表与清理范围：输入 `y`/`yes` 确认，`n`/`no`、空行或 EOF 取消并返回 `130`；不接受 `--yes`、`-y` 或 `--force`。当环境中尚无部署时，默认 `barn purge` 与整体 `barn destroy` 均直接返回成功（`purge` 还会清理归属元数据完整的残留持久盘）。无法确认残留目录归属时仍会拒绝删除。若部署状态文件已缺失，执行 `destroy --force --delete-persistent` 或 `destroy --force --purge` 会报错并提示改用 `barn purge`。

### 1.2.0 规格参数与 SPEC 显示 {#vm-specification-flags}

Barn 1.2.0 新增 `--cpu/-C`、`--mem/-M`、`--scale/-S`、`--disk/-D`，与 `--image/-I`、`--arch/-A` 共用规格输入规则，支持范围如下：

| 命令 | 新增支持 |
|---|---|
| `init`、生成模板的 `setup` | C/M/S/D，写入新清单 |
| `validate`、`plan`、`up`、`reload`、`recreate` | C/M/S/D，仅覆盖本次期望规格 |
| `resize` | C/M/S/D，应用 CPU/内存变化与根盘增长；保留已有 I/A 核对 |
| 复用已有清单的 `setup` | 不接收规格覆盖，忽略规格环境变量 |
| `start/stop/restart/status/destroy/purge` | 不接收，沿用已应用状态 |

参数、单位、环境变量及保存规则见 [规格覆盖](../configuration/#specification-overrides)。`up/reload` 不会自动应用已有节点的资源变化，仍需 `resize` 或显式 `recreate`。

节点表用 `SPEC` 列表示有效 CPU 与内存，例如 `1c2g`、`2c4g`、`8c16g`。`c` 表示 vCPU，`g` 表示 GiB；1536 MiB 精确显示为 `1.5g`，512 MiB 为 `0.5g`。不能整除 MiB 的字节容量用 `b` 精确保留，未知规格显示 `-`。

`status` 和完成结果显示已应用规格；`plan/validate/setup` 显示期望规格。计划中的资源变化显示为 `2c4g → 4c8g`，根盘在 `ROOT` 列单独显示。`init` 摘要、生命周期动态进度及普通终端的完成结果也显示 `SPEC`。scale 不为 1 时展示基数、倍数、结果及来源；`--verbose` 也显示倍数为 1 的计算说明。JSON 保留数值 CPU 和字节容量，并在 `resources` 中提供基数、倍数、有效结果与来源，不要求脚本解析缩写。

### 1.2.0 根盘原地扩容 {#root-disk-growth}

```bash
barn resize -D 128GiB meta
BARN_DISK=128GiB barn resize meta
```

`-D` 是绝对目标容量，重复相同目标不再修改磁盘或重启 VM；缩盘直接报错。首次扩容需要停机，原本运行的节点完成后运行，原本停机的节点临时启动完成检查与扩展后恢复停机。支持 512 字节逻辑扇区、GPT 或主 MBR 分区表中位于末端的普通 ext4/XFS 根分区；LVM、加密设备、后置分区和缺少所需工具会在修改磁盘镜像前报错。根盘与原有数据、VM UUID、SSH 密钥均保留，数据盘不参与扩容。

Barn 持久化恢复阶段，核对镜像容量、客机磁盘、分区及文件系统后才完成操作。失败时 `status` 显示 `root-resize` 提示；修复报告的问题后，按提示重复相同 `resize -D` 目标。根盘已扩展但客机未完成时不会自动缩回。若清单仍保留旧容量，继续运行原清单会报告差异；需要长期保留新容量时更新 `vm_disk`。实现与测量见 [根盘扩容验收](/zh/blog/design/root-disk-growth/)。

### 1.2.0 的生命周期并发 {#lifecycle-concurrency}

Barn 1.2.0 将 Linux 虚拟机生命周期默认并发设为 `max(1, 逻辑 CPU 数 - 2)`，CPU 数取 Barn 进程检测到的可用逻辑 CPU 数，各阶段实际并发不超过该阶段所选节点数。已发布的 Barn 1.1.0 最多使用四个工作线程，生命周期命令尚不支持 `--parallel`。

1.2.0 的 `up`、`start`、`stop`、`restart`、`reload`、`recreate`、`destroy` 与 `purge` 接受零或正整数参数 `--parallel/-p`。省略参数时采用 CPU 默认策略，显式传入 `--parallel 0` 则让所选节点全部并行；正数指定并发上限，`--parallel 1` 可将节点操作设为串行。该参数覆盖命令涉及的磁盘准备、启动与停机阶段并发，状态提交与文件删除沿用原有顺序。超过 16 的值也会生效，超过节点数则不会多建工作线程。该选项仅作用于本次命令，失败后建议的重试命令会保留显式传入的值，包括零。

```bash
barn up -p 0
barn up --parallel 8
barn start -p 1
barn restart meta node-1 -p 2
```

启动工作线程在客机启动、等待 SSH 与就绪检查完成期间一直占用并发名额。传入 `--no-wait` 后，QEMU 启动且进程身份核验通过即可释放名额。磁盘准备阶段全部结束后才进入启动阶段。`provision --parallel` 保持独立的默认值 `1`；原生 macOS 客机的运行数量限制见 [Mac 命令](../mac/)。

实现与回归测试：[`concurrency.go`](https://github.com/pgsty/barn/blob/v1.2.0/internal/private/concurrency.go)、[`concurrency_test.go`](https://github.com/pgsty/barn/blob/v1.2.0/internal/private/concurrency_test.go) 与 [`lifecycle_parallel_test.go`](https://github.com/pgsty/barn/blob/v1.2.0/cmd/barn/lifecycle_parallel_test.go)。

2026-11-10 真机验收在具有 18 个逻辑 CPU 的 macOS/arm64 宿主上，通过临时 `BARN_HOME` 管理六台 Debian 13 客机：自动默认值为 16，实际启动并发峰值为六；显式设为 1 时，启动与停止均为串行；显式设为 32 时，重启并发峰值为六。全部客机通过就绪检查，测试部署已在结束后销毁。

2026-11-11 在同一宿主上另建临时部署，验证显式零值：18 台 Debian 13 客机全部并行启动，并在 39.6 秒内通过就绪检查。选择其中三台执行停止和启动，两阶段并发峰值均为三，其余 15 台虚拟机进程保持不变。测试部署已在结束后销毁，原有六台虚拟机进程保持不变。回归测试另覆盖超过 16 的正数并发上限、修改状态前拒绝负数，以及重试命令保留显式零值。

## 结构化失败 {#structured-failures}

编写自动化脚本时，请先检查进程退出码，再按所执行的命令解析输出。

在默认文本模式下，耗时满 1 秒的终端操作会在 stderr 动态重绘单张实时状态表（`NAME ADDRESS STATE MESSAGE`、`ITEM STATE MESSAGE` 或 `IMAGE STATE MESSAGE`），并在底部输出以 `[DONE]`、`[FAILED]` 或 `[CANCELLED]` 结尾的汇总行；当 stdout 与 stderr 都是终端且未启用 `--verbose` 时，完成后的表格会原地固定，stdout 只追加后续操作提示（如 `connect:`、`retry:`、`next:`）。常规错误会在 stderr 打印 `error: <消息>`；若外部命令调用失败，还会附上其最后几行 stderr 输出，并在有明确恢复步骤时打印 `next:` 建议命令。SSH 子进程执行远端命令返回非零退出码时，Barn 会直接透传远端输出，不再额外包装 `error:` 行。

在 `--json` 或 `--yaml` 模式下，定义了专属报告结构的命令（`doctor`、`network`、`provision`、生命周期命令以及 `ssh`/`exec`）会直接在 stdout 输出各自的报告结构（例如 `exec` 返回 `success`、`exit_code`、`stdout` 与 `stderr`）。如果命令在生成专属报告前就失败，Barn 会在 stdout 输出单个通用错误对象：

- `error`：取自[退出码](#exit-codes)表的固定错误类别（`recreate_required` 与 `nodes_removed` 现作为 `error: "conflict"` 下的 `reason` 返回，资源冲突统一使用 `error: "resource"`）。
- `message`：可读的错误说明。
- 可选上下文字段：`reason`、`next`、`operation_id`，以及记录外部命令失败详情的 `command`（含 `name`、`argv`、`exit_status`、`signal`、`timed_out`、`stderr`）。

单次结果命令输出一份 JSON 或 YAML 文档；`logs --follow` 使用 NDJSON 或 YAML 文档流，结构化模式的交互 SSH 将会话输出送往 stderr，最终报告送往 stdout。设计理由见 [CLI 契约](/zh/blog/design/cli-contracts/)。

## 生命周期结果 {#lifecycle-results}

不传节点名时，生命周期命令默认作用于部署中的全部节点；而 `ssh`、`exec` 与单节点 `logs` 默认作用于已完成准备的控制节点（若控制节点尚未准备就绪，则回退到第一个已准备就绪的节点）。节点选择器必须是解析后的节点名称（如 `meta`），不接受清单 IP、分组名或 `vm_alias` 别名。

- **`restart`**：不重新读取清单，直接按已应用状态重启节点。
- **`reload`**：先校验本次生效的期望规格与启动依赖，通过后再停止所选节点并对这些节点执行 `up`。该命令可以新增节点；需要替换已有虚拟机的变更仍需使用 `recreate`。
- **`resize`**：已发布 1.1.0 只应用 CPU 与内存变更；1.2.0 支持 `vm_scale` 的有效规格及[根盘增长](#root-disk-growth)。支持的增加操作可以热插拔；减少资源、旧虚拟机或后端不支持时会自动停机再启动，同时保留虚拟机身份与磁盘。镜像、数据盘、网络、共享目录、创建、删除及部署级变更会被拒绝。
- **`recreate`**：通过替换根盘和非持久数据盘来应用节点定义变更，同时保留兼容的[持久数据盘](../configuration/#data-disks)。显式选择节点执行 `plan`、`up`、`reload`、`recreate` 或 `resize` 时，其余节点保留已应用定义，即使 YAML 已修改或省略它们；未创建且未选中的节点不要求解析镜像。地址、别名、控制节点角色及部署公共设置的真实冲突仍会在预检时报错；省略选择器时则处理整份清单。
- 当配置漂移需要执行破坏性变更时，`up` 与 `reload` 会返回 `conflict` 错误，并提示先运行 `barn plan`，再运行 `barn recreate <node>` 或 `barn destroy <node>`。在终端上，`recreate` 与 `destroy` 会列出将被替换或删除的节点，并要求输入命令名确认，传入 `--yes`（或 `--force`）可跳过；没有终端且未传这两个参数时，命令以退出码 `2` 拒绝执行。不带节点参数时，两者都作用于整套部署。

不带节点参数的 `recreate` 遇到清单缺少已有节点时，会在任何虚拟机停机前拒绝执行（`conflict`，reason `nodes_removed`，退出码 `4`）。需要删除该节点时请显式执行 `barn destroy <node>`，否则把它加回清单。Barn 会在销毁锁内再次核对范围；若预检期间已应用状态发生变化，recreate 以 reason `deployment_changed` 退出，请重新检查计划后重试。

删除控制节点后，剩余的第一个节点接任控制节点。请在清单中把控制角色（`admin_ip`）改为该节点，再运行 `barn up` 安装其控制 SSH 访问；`--no-wait` 会推迟这一步。在此之前，仍把已删除节点设为控制节点的清单属于角色漂移，`up` 会拒绝执行；如需恢复原节点，请将其作为普通节点重新加入。接任节点存在无法完成的准备记录时，Barn 会在删除任何内容前拒绝删除控制节点，并在错误中指出接任节点。

### 计划 {#planning}

`barn plan` 是只读命令，即便计算出的 `action` 为 `resize`、`recreate` 或 `blocked-removal`，也会以退出码 `0` 返回；自动化脚本应检查 `action`、`create`/`resize`/`recreate`/`start`/`missing` 数组，以及可选的 `blocked` 原因字符串。

对于镜像目录中的标准镜像，`plan` 仅读取本地配置与镜像目录元数据，不依赖 QEMU 或宿主网络；对于已注册的 `local-*` 本地导入镜像，`plan` 还会调用 `qemu-img` 校验缓存文件。`plan` 不会下载镜像，并会展示精确的镜像版本、CPU/内存/磁盘资源总量、漂移原因以及每块数据盘的处理动作（包括默认的 128 GiB `/data` 盘）。

### 启动与 SSH 配置 {#starting-and-ssh-configuration}

`barn up` 会在执行前检查宿主虚拟化能力与地址可用性，依次创建缺失节点、启动已停止节点、检查运行中节点的 SSH 就绪状态，并根据完整的已应用部署重写宿主 SSH 客户端配置片段（`~/.ssh/barn_config`）以及运行中客机的 `/etc/hosts` 和控制节点 SSH 配置。`recreate` 同样会完整刷新上述配置；`start` 与 `restart` 也会刷新 SSH 别名；单节点 `destroy` 会移除对应条目，整体 `destroy` 则移除整份配置片段。

若虚拟机生命周期操作已成功，但写入 `~/.ssh/config` 失败（或者 `~/.ssh/config` 是符号链接/硬链接，Barn 从不修改链接文件），Barn 会写好独立的 `~/.ssh/barn_config` 片段、提示需手动添加的 `Include` 行，将告警记入 `warnings[]` 并以 `0` 退出（`barn ssh` 仍可正常连接）。

控制节点上由 Barn 管理的 SSH 条目不会把实验节点的主机密钥锁死在 `known_hosts` 中，从而保证节点重建后依然可以直接连通；用户在客机中自行添加的 SSH 配置会原样保留。

### 就绪 {#readiness}

管理 SSH 连通后，Barn 即判定 Linux 客机已就绪。非致命的客机初始化问题会记录在 `nodes[].warnings` 中，已自动完成的恢复动作（例如重置损坏的数据盘）会记录在 `nodes[].repairs` 中，命令退出码仍为 `0`。再次运行 `barn up` 可以在不重启 QEMU 进程的情况下，对运行中的节点重试未完成的初始化步骤。

传入 `--no-wait` 时，命令在 QEMU 进程启动后立即返回，把客机就绪检查、数据盘恢复与 SSH/`/etc/hosts` 刷新留给下一次 `barn up`。

哪些数据盘问题会被自动修复（记入 `repairs`）、哪些只报告（记入 `warnings`），见[数据盘](../configuration/#data-disks)。已有客机会在下一次 `barn up` 的就绪检查中获得当前的恢复脚本。

### 节点失败 {#node-failures}

批处理过程中若出现可隔离的单节点失败，Barn 会保留已成功的节点，以退出码 `5` 返回，并按 `N of M node(s) failed: <node> (<stage>: <error>); ...` 格式汇总错误（常见阶段包括 `prepare`、`start`、`readiness`、`bootstrap`、`guest-setup`、`stop` 与 `status`）。结构化输出在 `failures[]` 中提供 `node`、`stage`、`error` 及可选的 `reason`（若传入 `--rollback` 清理了未提交节点的准备产物，还会包含 `rolled_back`）。遇到 `readiness` 或 `bootstrap` 失败时，请运行 `barn logs <node>` 查看串口输出，并参考[节点未就绪排查](../../start/troubleshooting/#a-node-did-not-become-ready)。

### 状态 {#status}

`barn status` 默认展示节点名、IP（`ADDRESS`）、状态（`running` 表示 QEMU 进程存活，不主动探测客机 SSH）、精确镜像及 CPU/内存，并在使用 TCG 软件模拟时予以标记（在 Apple Silicon 上若存在 Mac 虚拟机，还会附加 `mac: <名称>; barn mac ls`）。加上 `--verbose` 可进一步查看 SSH 转发端口、架构、加速器与 QEMU PID。若个别节点异常——包括在线 `resize` 在热插拔后中断（`stage: "resize"`、`reason: "resize_incomplete"`）——`status` 仍会展示其余正常节点，在 `failures[]` 中附带节点错误并以 `5` 退出。

## 恢复与中断处理 {#recovery-and-interrupted-operations}

- **故障隔离**：执行 `up` 或 `start` 时，某个节点的宿主共享目录缺失或新节点准备失败只影响该节点，独立的已停止节点仍会正常启动；命令以 `5` 退出，并给出保留原 `-f`、`--repo` 及参数选项的重试命令。
- **阶段事件日志**：宿主 `setup` 与紧随其后的生命周期重试共用同一个 `operation_id`。即便首次 `setup` 在创建部署状态前就失败，也可以运行 `barn logs --source events --json` 读取定长轮转的阶段事件日志（日志自动脱敏命令参数与凭据；`setup --dry-run` 不写日志）。
- **遗留持久盘**：先前移除节点后保留下来的受管持久盘不会阻塞其余节点的销毁；需要连同这些持久盘一并清理时，请执行 `destroy --delete-persistent` 或 `purge`。
- **macOS 准备顺序**：在 macOS 上安装新网络时，`setup` 会先完成 Homebrew 查找/安装或下载固定版本的 `socket_vmnet` 归档，最后再请求管理员授权，避免安装或下载耗时导致先前的 `sudo` 凭据过期，也不会在下载失败时白白弹出密码框。
- **PID 与日志对账**：如果记录的 QEMU PID 已被无关进程复用，Barn 会将该节点识别为 `stopped`；若停止操作中断但虚拟机进程仍在运行，Barn 会将其恢复为 `running`。若在线 `resize` 在修改运行中客机后中断，`status` 会报告 `resize_incomplete`，可重新运行 `barn resize <node>` 或执行 `barn restart <node>`。其他中断状态会提示恢复命令（`destroy` 会直接完成中断清理）；首次 `up` 失败后，修改清单再重试时 Barn 会根据事务日志自动回滚未提交的残留产物。
- **取消操作**：命令被取消时，Barn 向正在运行的外部程序发送 SIGTERM，`sudo` 会将其转发给特权命令；Barn 最多等待 10 秒，让该进程及其继承的输出管道结束。忽略 SIGTERM 的后代进程仍需外部监管。

## 日志与环境变量 {#logs-and-environment}

`barn logs` 默认读取客机串口控制台（`--source serial`）。指定 `--source qemu` 可读取 QEMU 诊断输出，指定 `--source events` 可读取部署级的定长事件日志。配合 `--follow`（`-f`）时，文本模式流式输出字节，JSON 模式输出 NDJSON 行，YAML 模式输出文档流。Barn 默认将事件日志与 QEMU 日志格式化为简洁记录，仅在传入 `--verbose` 时展开完整的 QEMU 启动参数。

| 环境变量 | 用途 |
|---|---|
| `BARN_HOME` | 私有状态目录（默认 `~/.barn`），接受相对路径、`~/` 与目录符号链接，但不能是 `/` 或用户主目录；跨工作目录使用时建议设置绝对路径 |
| `BARN_IMAGE/BARN_ARCH/BARN_CPU/BARN_MEM/BARN_SCALE/BARN_DISK` | 1.2.0 VM 规格覆盖，CLI 优先；仅在接收该字段的命令中读取，详见[规格覆盖](../configuration/#specification-overrides) |
| `BARN_REPO` | 默认镜像仓库 URL 或路径；可被命令行的 `--mirror` 与 `--repo` 依次覆盖 |
| `BARN_OUTPUT` | 默认输出格式（`text`、`json` 或 `yaml`）；命令行展示参数优先 |
| `BARN_VERBOSE` | 诊断输出布尔开关默认值；命令行 `-v`/`--verbose` 优先 |
| `BARN_VMNET_ARCHIVE` | macOS `setup` 使用的本地 `socket_vmnet` 归档路径；支持相对路径、`~/` 与符号链接（仍强制校验 SHA-256） |
| `NO_COLOR` | 设为任意非空值时禁用终端颜色 |
{.wide .expand}

显式传入的 `--json`、`--yaml` 与 `-v`/`--verbose` 优先于 `BARN_OUTPUT` 和 `BARN_VERBOSE`；即使这两个变量取值无效，`--help` 仍可正常使用。其他命令在无效取值未被命令行参数覆盖时，以退出码 `2`（`usage`）报错。

## SSH 透传与命令补全 {#ssh-passthrough-and-completion}

```text
barn ssh [node] [-- command...]
barn exec [node] -- command...
```

> [!TIP]
> 远端命令前必须使用 `--`。请写成 `barn exec meta -- hostname` 而非 `barn exec meta hostname`；需要执行 Shell 命令字符串时显式调用 `sh -c`。

- **`barn ssh`**：不带远端命令时打开交互式登录终端；带上 `-- command...` 时，将 `--` 后的参数用空格拼接后交给远端 shell 解释。
- **`barn exec`**：要求提供 `-- command...`，并将程序名与各个参数分别传递，原样保留参数中的空格、引号、后续空字符串参数以及 shell 元字符。需要使用管道、重定向、变量展开或串行执行多条命令时，请显式调用 `sh -c '...'`。
- `--` 之前的位置参数最多只能包含一个已知节点名（省略时默认选择控制节点）。若 `--` 前出现未知节点名或多个选择器，命令会在发起连接前直接以退出码 `2`（`usage`）报错，列出已知节点并提示运行 `barn status`。
- `--json`、`-v`、`--help` 等 Barn 自身参数必须放在 `--` 之前；`--` 之后的所有内容（包括第二个 `--`、`-V` 或 `-o...`）都归属远端命令，不会修改本地 OpenSSH 客户端选项。

```bash
barn ssh meta
barn ssh meta -- 'df -h /data; id'
barn exec meta -- hostname
barn exec meta -- printf '<%s>\n' 'a b' ''
barn exec meta -- sh -c 'id; df -h /data'
barn exec meta --json -- uname -a
```

执行 `barn completion bash|zsh|fish|powershell` 可导出对应 shell 的自动补全脚本（升级版本后，Bash 用户可执行 `source <(barn completion bash)` 重新加载）。补全覆盖命令、短别名、拓扑模板、镜像别名、枚举参数、`-f` 的 YAML 文件以及当前清单或已应用状态中的节点名，并在输入 `--` 后停止提示 Barn 参数。

## 退出码 {#exit-codes}

| 代码 | `error` | 含义 |
|---:|---|---|
| `0` | | 成功（包含客机已就绪但带有非致命 `warnings[]` 或 `repairs[]` 的情形） |
| `1` | `runtime` | 命令已执行但运行失败（外部工具、网络下载或客机操作失败） |
| `2` | `usage` | 命令行语法有误、缺少配置文件，或清单/镜像选择器无效 |
| `3` | `capability` | 宿主缺少必需工具、未配置好 Barn 网络或缺少执行权限 |
| `4` | `conflict` | 当前部署状态不允许该操作，或另一个 `barn` 进程正持有部署锁 |
| `5` | `partial` | 节点级批处理部分或全部失败；请检查 `failures[]`，已成功的节点保持不变 |
| `6` | `resource` | 宿主 IP、端口、网段或磁盘路径已被占用 |
| `7` | `integrity` | 摘要、镜像目录签名或签名 revision、实例身份或文件属主校验未通过 |
| `130` | `cancelled` | 操作被 `SIGINT`/`SIGTERM` 中断，或在交互提示中拒绝确认 |
{.wide .expand}

镜像目录缺少签名或签名校验失败时返回 `reason: "catalog_signature"`；目录复用已接受或内置的 revision 号但内容字节不同时返回 `reason: "catalog_equivocation"`。读取缓存目录签名时遇到的权限或 I/O 错误属于运行时错误（退出码 `1`）。

若另一个 `barn` 命令正持有部署锁，修改类命令最多等待 10 分钟并指出持锁命令；等待超时则以退出码 `4`（`reason: "deployment_busy"`）退出。只读与访问类命令（`status`、`ssh`、`exec`、`ssh-config`、`hosts`）不会阻塞等待锁；其中 `status` 会展示最近一次提交的节点状态，并在 `note` 字段中注明正在并发执行的操作。

`ssh` 与 `exec` 会原样返回 SSH 子进程的退出码（包括 `255`，既可能表示 SSH 连接失败，也可能是远端命令自身返回 `255`），文本输出、JSON `exit_code` 与进程退出码三者始终保持一致。
