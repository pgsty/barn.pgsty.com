---
title: 命令行
description: Barn 命令、关键参数、结构化输出与退出码。
weight: 20
icon: fa-solid fa-terminal
aliases: [/docs/reference/json-api/]
---

> [!NOTE]
> **Unreleased**：下文关于路径支持、显式节点选择及 provision 上限调整的变更需要包含源码提交 `27f17bb` 的构建，Barn 0.9.2 尚未包含这些行为。详见[未发布变更](/zh/docs/about/unreleased/)。

本页说明 **Barn 0.9.2** 的全局展示参数与 Linux 实验环境命令。macOS 客机命令请查阅 [Mac 命令](../mac/)。使用其他版本时，请先运行 `barn version` 核对版本号。

```text
barn [--json|--yaml] [-v|--verbose] <command> [flags] [node...]
```

每条命令都提供内置 `--help`，用于查看当前二进制支持的参数与示例：

```bash
barn --help
barn setup --help
barn image pull --help
```

不带参数直接运行 `barn` 会打印简要欢迎信息与常用命令建议（JSON/YAML 模式下返回 `actions[]` 数组），并以退出码 `0` 返回。只输入命令分组而不带子命令（如 `barn image`）会以退出码 `2` 返回（文本模式输出帮助，JSON/YAML 模式输出结构化 `usage` 错误）。显式传入 `--help` 始终打印人类可读的帮助文本并以 `0` 退出。查看构建版本信息请使用 `barn --version` 或 `barn version`。

## 命令

| 类别 | 命令 |
|---|---|
| 环境准备 | `setup`、`init`、`validate`、`doctor` |
| 生命周期 | `plan`、`up`、`start`、`stop`、`restart`、`reload`、`recreate`、`status`、`destroy`、`purge` |
| 节点访问 | `ssh`、`exec`、`logs`、`provision`、`ssh-config`、`hosts install/uninstall` |
| 镜像管理 | `update`、`image list/info/pull/import/sync/prune/reset`、`repo scan/build/verify` |
| 宿主网络 | `network status/install/uninstall` |
| macOS 客机 | `mac …` — 见 [Mac 命令](../mac/) |
| 其他工具 | `version`、`completion` |
{.wide}

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
{.wide}

`up`、`ssh`、`init`、`start`、`stop`、`restart`、`reload`、`provision`、`hosts`、`purge` 与 `completion` 不设顶层短别名（`rm` 也不是 `purge` 的别名）。在子命令命名空间内，`hosts` 与 `network` 的 `install`/`uninstall` 可简写为 `i`/`u`，`network status` 可简写为 `st`；`image` 下支持 `list=ls`、`info=in`、`pull=p`、`prune=pr`、`sync=sy` 与 `import=i`。

Barn 在每个 `BARN_HOME`（默认 `~/.barn`，详见[配置发现规则](../configuration/#发现顺序)）中管理唯一一套部署，只要 `BARN_HOME` 指向同一位置，操作已应用状态的命令就可在任意工作目录下执行；跨工作目录使用时请设置绝对 `BARN_HOME`。各条命令按如下规则确定期望配置来源（`-f` 是命令级参数而非全局参数）：

| 命令 | 期望状态来源 |
|---|---|
| `setup [template]` | 优先使用显式 `-f`，其次按目录发现，否则生成 `meta` 模板（`template` 与 `-f` 互斥） |
| `init [template]` | 直接生成新清单，不读取现有状态；传入 `--force` 可覆盖已有文件 |
| `validate` | 优先使用显式 `-f`，其次按目录发现；绝不回退到已应用状态 |
| `plan`、`up`、`reload`、`recreate` | 依次查找显式 `-f`、当前目录清单，最后回退到已应用的部署规格 |
| 其他生命周期与访问命令 | 不读取清单文件，直接操作 `BARN_HOME` 中的已应用状态 |
{.wide}

当当前目录没有清单且 `BARN_HOME` 中也没有已部署环境时，交互式运行 `barn up` 可以自动生成默认 `meta` 清单、补齐缺失的宿主依赖并拉起未激活的 Barn 网络（涉及特权操作时 `sudo` 仍会提示输入系统密码）。若希望先检查宿主变更计划，请运行 `barn setup --dry-run`；在非交互脚本中请显式执行 `barn setup --yes`。

对于全新、未修改的默认模板，若默认 `10.10.10.0/24` 网段与宿主现有路由冲突，`setup` 会自动改选另一个空闲的私有 `/24` 网段，并将原文件备份为 `barn.yml.before-network-change`。显式传入的 `-f` 清单、已手动编辑的模板以及已存在的部署始终保留各自配置的网段。

## 关键参数

| 参数 | 含义 |
|---|---|
| `--json`、`--yaml` | 在 stdout 输出机器可读结果，进度信息仍输出到 stderr（仅提供长参数） |
| `-v`、`--verbose` | 在 stderr 输出定长截断的诊断详情 |
| `-c`、`--cidr` | 为 `init`/`setup` 模板或宿主 `network` 检查/安装指定 RFC1918 `/24` 网段 |
| `-f`、`--file` | 为读取期望状态的命令指定清单文件 |
| `-r`、`--repo` | 指定镜像仓库 URL 或本地路径，优先级高于 `--mirror` 与 `BARN_REPO`（`validate` 自 0.9.0 起支持） |
| `--mirror` | 为 `setup`、镜像目录更新与拉取操作选用中国官方镜像源（`https://repo.pigsty.cc/barn`） |
| `-m`、`--mode` | 在支持该参数的命令上选择 macOS `host` 或 `shared` 网络模式 |
| `-d`、`--dry-run` | 仅打印 `setup` 或 `image prune` 的执行计划，不修改系统状态 |
| `-y`、`--yes` | 确认执行已展示的宿主、初始化或镜像计划 |
| `--force`（`init`、`destroy`、`recreate`） | 覆盖生成文件或跳过交互式确认词（因 `-f` 已用于选择清单，故仅设长参数） |
| `-n`、`--no-wait` | QEMU 进程启动后立即返回，跳过客机 SSH 就绪检查、磁盘恢复与配置刷新 |
| `--rollback`（`up`、`reload`） | 清理本次运行中准备失败、尚未提交状态的节点残留文件 |
| `--delete-persistent` | 整体销毁部署时一并删除 `persistent: true` 的持久数据盘 |
| `--purge` | 整体销毁部署时删除全部磁盘、密钥与状态，仅保留镜像缓存与宿主网络 |
{.wide}

各命令支持的局部参数如下表所示：

| 命令 | 专用参数 |
|---|---|
| `init` | `--output/-o`（默认 `./barn.yml`，`-` 表示输出到 stdout）、`--cidr/-c`、`--force` |
| `setup [meta\|dual\|trio\|full]` | `--file/-f`、`--cidr/-c`、`--repo/-r`、`--mirror`、`--mode/-m`、`--dry-run/-d`、`--yes/-y`（默认模板为 `meta`） |
| `validate` | `--file/-f`、`--repo/-r`；不接受节点参数 |
| `plan` | `--file/-f`、`--repo/-r` |
| `up`、`reload` | `--file/-f`、`--repo/-r`、`--mirror`、`--no-wait/-n`、`--rollback` |
| `recreate` | `--file/-f`、`--repo/-r`、`--mirror`、`--force`、`--no-wait/-n` |
| `start`、`restart` | `--no-wait/-n` |
| `stop`、`status` | 仅接受节点选择器与全局展示参数 |
| `destroy` | `--force`、`--delete-persistent`、`--purge`（后两者仅限整套部署） |
| `purge`、`doctor`、`version` | 仅接受全局展示参数 |
| `provision` | 必填 `--script/-s`；`--sudo`；`--parallel/-p` 正整数（默认 `1`）；`--timeout/-t` 正时长（默认 `1h`） |
| `ssh-config` | `--install/-i` 与 `--remove` 互斥；`--name` 默认为 `barn`（`--remove` 不要求存在已部署环境） |
| `logs` | `--source/-s serial\|qemu\|events`（默认 `serial`）；`--follow/-f`（`events` 为部署级日志，不接受节点名） |
| `image info`、`image pull` | 可选镜像选择器、`--arch/-a amd64\|arm64`、`--repo/-r`；`pull` 额外支持 `--mirror` |
| `image import` | `--sha256/-s`；命名导入（`--name local-*`）还必须同时传入 `--boot/-b bios\|uefi` 与 `--source-user/-u` |
| `image prune` | `--dry-run/-d` 与 `--yes/-y` 互斥；`--repo/-r` |
| `image sync` | 源 URL 或本地路径、`--repo/-r`、可选 `--allow-downgrade` |
| `update` | `--repo/-r`、`--mirror` |
| `image list`、`image reset` | `--repo/-r` |
| `repo scan/build/verify` | 必填一个仓库目录路径，支持相对路径、`~/` 与目录符号链接 |
| `network install` | `--cidr/-c`（默认 `10.10.10.0/24`）、`--mode/-m`（默认 `host`）、`--yes/-y`；macOS 专用 `--archive/-a`、`--interface-id/-i` |
| `network status` | 可选 `--cidr/-c` |
| `network uninstall`、`hosts install/uninstall` | `--yes/-y` |
{.wide}

参数使用说明：

- `setup --dry-run` 与 `setup --yes` 互斥。`--cidr` 仅调整新生成模板的网段，不会改写显式指定的 `-f` 清单。若要在 `validate` 时对照中国镜像源校验，请传入 `--repo https://repo.pigsty.cc/barn`。
- 在 Barn `0.9.2` 中，`network` 与 `hosts` 的 `install`/`uninstall` 会先展示变更计划并在终端请求确认（安装默认同意，卸载默认拒绝）；非终端环境下必须传入 `--yes` 才会执行。macOS 首次配置宿主网络请使用 `barn setup`。有节点运行时 `network uninstall` 会拒绝卸载网络；停止或销毁虚拟机不会卸载宿主网络。
- 涉及安全确认与仓库选择的开关（`--mirror`、`--force`、`--rollback`、`--remove`、`--allow-downgrade`、`--sudo`、`--delete-persistent`、`--purge`）只提供长参数。在 Linux 命令中，`-f` 表示 `--file`（`barn logs -f` 例外，表示 `--follow`），`-n` 表示 `--no-wait`（而 `barn mac logs -n` 表示日志行数），`-d` 表示 `--dry-run`。
- `barn purge` 直接执行与 `barn destroy --force --purge` 相同的整体清理，且无需交互确认：它会删除所有节点、持久盘、密钥、部署状态与默认 SSH 配置片段，同时保留镜像缓存与宿主网络。当环境中尚无部署时，`barn purge` 与整体 `barn destroy` 均直接返回成功（`purge` 还会清理归属元数据完整的残留持久盘，而不会盲目删除身份不明的目录）。若部署状态文件已缺失，执行 `destroy --force --delete-persistent` 或 `destroy --force --purge` 会报错并提示改用 `barn purge`。

## 结构化失败

编写自动化脚本时，请先检查进程退出码，再按所执行的命令解析输出。

在默认文本模式下，常规错误会在 stderr 打印 `error: <消息>`；若外部命令调用失败，还会附上其最后几行 stderr 输出，并在有明确恢复步骤时打印 `next:` 建议命令。SSH 子进程执行远端命令返回非零退出码时，Barn 会直接透传远端输出，不再额外包装 `error:` 行。

在 `--json` 或 `--yaml` 模式下，定义了专属报告结构的命令（`doctor`、`network`、`provision`、生命周期命令以及 `ssh`/`exec`）会直接在 stdout 输出各自的报告结构（例如 `exec` 返回 `success`、`exit_code`、`stdout` 与 `stderr`）。如果命令在生成专属报告前就失败，Barn 会在 stdout 输出单个通用错误对象：

- `error`：取自[退出码](#退出码)表的固定错误类别（`recreate_required` 与 `nodes_removed` 现作为 `error: "conflict"` 下的 `reason` 返回，资源冲突统一使用 `error: "resource"`）。
- `message`：可读的错误说明。
- 可选上下文字段：`reason`、`next`、`operation_id`，以及记录外部命令失败详情的 `command`（含 `name`、`argv`、`exit_status`、`signal`、`timed_out`、`stderr`）。

单次命令调用在 stdout 上绝不会追加输出第二份 JSON 或 YAML 文档。

## 生命周期结果

不传节点名时，生命周期命令默认作用于部署中的全部节点；而 `ssh`、`exec` 与单节点 `logs` 默认作用于已完成准备的控制节点（若控制节点尚未准备就绪，则回退到第一个已准备就绪的节点）。节点选择器必须是解析后的节点名称（如 `meta`），不接受清单 IP、分组名或 `vm_alias` 别名。

- **`restart`**：不重新读取清单，直接按已应用状态重启节点。
- **`reload`**：先校验本次生效的期望规格与启动依赖，通过后再停止所选节点并对这些节点执行 `up`。该命令可以新增节点；需要替换已有虚拟机的变更仍需使用 `recreate`。
- **`recreate`**：通过替换根盘和非持久数据盘来应用节点定义变更，同时保留兼容的[持久数据盘](../configuration/#数据盘)。**Unreleased**：显式选择节点执行 `plan`、`up`、`reload` 或 `recreate` 时，其余节点保留已应用定义，即使 YAML 已修改或省略它们；未创建且未选中的节点不要求解析镜像。地址、别名、控制节点角色及部署公共设置的真实冲突仍会在预检时报错；省略选择器时则处理整份清单。
- 当配置漂移需要执行破坏性变更时，`up` 与 `reload` 会返回 `conflict` 错误，并提示先运行 `barn plan`，再运行 `barn recreate <node>` 或 `barn destroy <node>`。在终端上，`recreate` 与 `destroy` 需要输入确认词，脚本可通过 `--force` 跳过确认。

### 计划

`barn plan` 是只读命令，即便计算出的 `action` 为 `recreate` 或 `blocked-removal`，也会以退出码 `0` 返回；自动化脚本应检查 `action`、`create`/`recreate`/`start`/`missing` 数组，以及可选的 `blocked` 原因字符串。

对于镜像目录中的标准镜像，`plan` 仅读取本地配置与镜像目录元数据，不依赖 QEMU 或宿主网络；对于已注册的 `local-*` 本地导入镜像，`plan` 还会调用 `qemu-img` 校验缓存文件。`plan` 不会下载镜像，并会展示精确的镜像版本、CPU/内存/磁盘资源总量、漂移原因以及每块数据盘的处理动作（Barn `0.9.2` 会显式列出默认的 128 GiB `/data` 盘）。

### 启动与 SSH 配置

`barn up` 会在执行前检查宿主虚拟化能力与地址可用性，依次创建缺失节点、启动已停止节点、检查运行中节点的 SSH 就绪状态，并根据完整的已应用部署重写宿主 SSH 客户端配置片段（`~/.ssh/barn_config`）以及运行中客机的 `/etc/hosts` 和控制节点 SSH 配置。`recreate` 同样会完整刷新上述配置；`start` 与 `restart` 也会刷新 SSH 别名；单节点 `destroy` 会移除对应条目，整体 `destroy` 则移除整份配置片段。

若虚拟机生命周期操作已成功，但写入 `~/.ssh/config` 失败（或者 `~/.ssh/config` 是符号链接/硬链接，Barn `0.9.2` 不会直接修改链接文件），Barn 会写好独立的 `~/.ssh/barn_config` 片段、提示需手动添加的 `Include` 行，将告警记入 `warnings[]` 并以 `0` 退出（`barn ssh` 仍可正常连接）。

控制节点上由 Barn 管理的 SSH 条目不会把实验节点的主机密钥锁死在 `known_hosts` 中，从而保证节点重建后依然可以直接连通；用户在客机中自行添加的 SSH 配置会原样保留。

### 就绪

管理 SSH 连通后，Barn 即判定 Linux 客机已就绪。非致命的客机初始化问题会记录在 `nodes[].warnings` 中，已自动完成的恢复动作（例如重置损坏的数据盘）会记录在 `nodes[].repairs` 中，命令退出码仍为 `0`。再次运行 `barn up` 可以在不重启 QEMU 进程的情况下，对运行中的节点重试未完成的初始化步骤。

传入 `--no-wait` 时，命令在 QEMU 进程启动后立即返回，把客机就绪检查、数据盘恢复与 SSH/`/etc/hosts` 刷新留给下一次 `barn up`。

### 节点失败

批处理过程中若出现可隔离的单节点失败，Barn 会保留已成功的节点，以退出码 `5` 返回，并按 `N of M node(s) failed: <node> (<stage>: <error>); ...` 格式汇总错误（常见阶段包括 `prepare`、`start`、`readiness`、`bootstrap`、`guest-setup`、`stop` 与 `status`）。结构化输出在 `failures[]` 中提供 `node`、`stage`、`error` 及可选的 `reason`（若传入 `--rollback` 清理了未提交节点的准备产物，还会包含 `rolled_back`）。遇到 `readiness` 或 `bootstrap` 失败时，请运行 `barn logs <node>` 查看串口输出，并参考[节点未就绪排查](../../start/troubleshooting/#节点未就绪)。

### 状态

`barn status` 默认展示节点名、状态（`running` 表示 QEMU 进程存活，不主动探测客机 SSH）、IP、精确镜像及 CPU/内存，并在使用 TCG 软件模拟时予以标记。加上 `--verbose` 可进一步查看 SSH 转发端口、架构、加速器与 QEMU PID。若个别节点异常，`status` 仍会展示其余正常节点，在 `failures[]` 中附带节点错误并以 `5` 退出。

## 恢复与中断处理

- **故障隔离**：执行 `up` 或 `start` 时，某个节点的宿主共享目录缺失或新节点准备失败只影响该节点，独立的已停止节点仍会正常启动；命令以 `5` 退出，并给出保留原 `-f`、`--repo` 及参数选项的重试命令。
- **阶段事件日志**：宿主 `setup` 与紧随其后的生命周期重试共用同一个 `operation_id`。即便首次 `setup` 在创建部署状态前就失败，也可以运行 `barn logs --source events --json` 读取定长轮转的阶段事件日志（日志自动脱敏命令参数与凭据；`setup --dry-run` 不写日志）。
- **遗留持久盘**：先前移除节点后保留下来的受管持久盘不会阻塞其余节点的销毁；需要连同这些持久盘一并清理时，请执行 `destroy --delete-persistent` 或 `purge`。
- **macOS 准备顺序**：在 macOS 上安装新网络时，`setup` 会先完成 Homebrew 查找/安装或下载固定版本的 `socket_vmnet` 归档，最后再请求管理员授权，避免安装或下载耗时导致先前的 `sudo` 凭据过期，也不会在下载失败时白白弹出密码框。
- **PID 与日志对账**：如果记录的 QEMU PID 已被无关进程复用，Barn 会将该节点识别为 `stopped`；若停止操作中断但虚拟机进程仍在运行，Barn 会将其恢复为 `running`。其他中断状态会提示恢复命令（`destroy` 会直接完成中断清理）；首次 `up` 失败后，修改清单再重试时 Barn 会根据事务日志自动回滚未提交的残留产物。

## 日志与环境变量

`barn logs` 默认读取客机串口控制台（`--source serial`）。指定 `--source qemu` 可读取 QEMU 诊断输出，指定 `--source events` 可读取部署级的定长事件日志。配合 `--follow`（`-f`）时，文本模式流式输出字节，JSON 模式输出 NDJSON 行，YAML 模式输出文档流。Barn `0.9.2` 默认将事件日志与 QEMU 日志格式化为简洁记录，仅在传入 `--verbose` 时展开完整的 QEMU 启动参数。

| 环境变量 | 用途 |
|---|---|
| `BARN_HOME` | 私有状态目录（默认 `~/.barn`），接受相对路径、`~/` 与目录符号链接，但不能是 `/` 或用户主目录；跨工作目录使用时建议设置绝对路径 |
| `BARN_REPO` | 默认镜像仓库 URL 或路径；可被命令行的 `--mirror` 与 `--repo` 依次覆盖 |
| `BARN_OUTPUT` | 默认输出格式（`text`、`json` 或 `yaml`）；命令行展示参数优先 |
| `BARN_VERBOSE` | 诊断输出布尔开关默认值；命令行 `-v`/`--verbose` 优先 |
| `BARN_VMNET_ARCHIVE` | macOS `setup` 使用的本地 `socket_vmnet` 归档路径；Unreleased 支持相对路径、`~/` 与符号链接（仍强制校验 SHA-256） |
| `NO_COLOR` | 设为任意非空值时禁用终端颜色 |
{.wide}

## SSH 透传与命令补全 {#ssh-透传与命令补全}

```text
barn ssh [node] [-- command...]
barn exec [node] -- command...
```

> [!TIP]
> 从 **0.9.2** 开始，远端命令前必须使用 `--`。请将旧脚本中的 `barn exec meta hostname` 改为 `barn exec meta -- hostname`；需要执行 Shell 命令字符串时显式调用 `sh -c`。

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

## 退出码 {#退出码}

| 代码 | `error` | 含义 |
|---:|---|---|
| `0` | | 成功（包含客机已就绪但带有非致命 `warnings[]` 或 `repairs[]` 的情形） |
| `1` | `runtime` | 命令已执行但运行失败（外部工具、网络下载或客机操作失败） |
| `2` | `usage` | 命令行语法有误、缺少配置文件，或清单/镜像选择器无效 |
| `3` | `capability` | 宿主缺少必需工具、未配置好 Barn 网络或缺少执行权限 |
| `4` | `conflict` | 当前部署状态不允许该操作，或另一个 `barn` 进程正持有部署锁 |
| `5` | `partial` | 节点级批处理部分或全部失败；请检查 `failures[]`，已成功的节点保持不变 |
| `6` | `resource` | 宿主 IP、端口、网段或磁盘路径已被占用 |
| `7` | `integrity` | 摘要、签名、实例身份或文件属主校验未通过 |
| `130` | `cancelled` | 操作被 `SIGINT`/`SIGTERM` 中断，或在交互提示中拒绝确认 |
{.wide}

在 Barn `0.9.2` 中，若另一个 `barn` 命令正持有部署锁，修改类命令最多等待 10 分钟并指出持锁命令；等待超时则以退出码 `4`（`reason: "deployment_busy"`）退出。只读与访问类命令（`status`、`ssh`、`exec`、`ssh-config`、`hosts`）不会阻塞等待锁；其中 `status` 会展示最近一次提交的节点状态，并在 `note` 字段中注明正在并发执行的操作。

`ssh` 与 `exec` 会原样返回 SSH 子进程的退出码（包括 `255`，既可能表示 SSH 连接失败，也可能是远端命令自身返回 `255`），文本输出、JSON `exit_code` 与进程退出码三者始终保持一致。
