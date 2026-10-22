---
title: 命令行
description: Barn 命令、关键参数、结构化输出与退出码。
weight: 20
icon: fa-solid fa-terminal
aliases: [/docs/reference/json-api/]
---

本页说明 **Barn 0.9.1** 的通用参数与 Linux 环境命令。
macOS 客机参见 [Mac 命令](../mac/)。使用其他版本时，请先核对 `barn version`。

```text
barn [--json|--yaml] [-v|--verbose] <command> [flags] [node...]
```

查询已安装版本支持的参数时，请使用命令帮助。每条可见命令都说明操作范围，并提供示例：

```bash
barn --help
barn setup --help
barn image pull --help
```

直接运行 `barn` 会显示简短欢迎信息和下一步命令，以 0 退出。JSON/YAML 输出包含 `actions[]`。
`barn image` 等未指定子命令的命名空间以 2 退出。文本模式打印帮助，JSON/YAML 模式返回结构化用法错误。
显式 `--help` 始终输出供人阅读的帮助文本，并以 0 退出。
用 `barn --version` 或 `barn version` 查看构建身份。

## 命令

| 范围 | 命令 |
|---|---|
| 准备 | `setup`、`init`、`validate`、`doctor` |
| 生命周期 | `plan`、`up`、`start`、`stop`、`restart`、`reload`、`recreate`、`status`、`destroy`、`purge` |
| 访问 | `ssh`、`exec`、`logs`、`provision`、`ssh-config`、`hosts install/uninstall` |
| 镜像 | `update`、`image list/info/pull/import/sync/prune/reset`、`repo scan/build/verify` |
| 宿主网络 | `network status/install/uninstall` |
| macOS 客机 | `mac …`，见 [Mac 命令](../mac/) |
| 其他 | `version`、`completion` |

Barn 不会隐式刷新镜像目录。`update` 获取、校验并激活所选仓库的镜像目录。
需要从精确 URL 或文件恢复时，使用 `image sync`。普通命令只使用当前本地镜像目录。
这两个命令都不更新 Barn 可执行文件。

以下短别名只在对应命令的作用域内生效：

| 命令 | 别名 | 命令 | 别名 |
|---|---|---|---|
| `setup` | `s` | `validate` | `v` |
| `plan` | `pl` | `recreate` | `rc` |
| `status` | `st` | `destroy` | `de` |
| `ssh-config` | `sc` | `image` | `images`、`im` |
| `doctor` | `dt` | `network` | `n`、`net` |
| `exec` / `logs` | `ex` / `l` | `version` | `ver` |

`up`、`ssh`、`init`、`start`、`stop`、`restart`、`reload`、`provision`、`hosts`、
`completion` 没有别名。请使用明确的 `barn purge` 拼写；`rm` 不是命令别名。
命名空间内部，`hosts` 与 `network` 的 install/uninstall 使用
`i`/`u`，`network status` 使用 `st`；`image` 使用 `list=ls`、`info=in`、`pull=p`、
`prune=pr`、`sync=sy`、`import=i`。

Barn 在选定的 `BARN_HOME`（默认 `~/.barn`）中管理一套部署。部署身份与清单所在目录无关。
使用已应用状态的命令可在任意目录运行。各命令自行确定配置来源，因此 `-f` 不是全局参数：

| 命令 | 期望状态来源 |
|---|---|
| `setup [template]` | 显式 `-f`，否则发现配置，否则生成 `meta`；模板与 `-f` 互斥 |
| `init [template]` | 生成新清单，不读取期望状态；`--force` 显式替换输出文件 |
| `validate` | 显式 `-f`，再发现配置；绝不回退到已应用状态 |
| `plan`、`up`、`reload`、`recreate` | 显式 `-f`，再发现配置，最后回退到已应用规格 |
| 其他生命周期/访问命令 | 不读取期望配置；使用已应用状态 |

没有配置文件且没有已应用部署时，交互式 `up` 可以生成默认配置。
它也能安装缺少的宿主依赖，或恢复完整但未激活的 Barn 网络。
自动准备不会再次请求 Barn 确认，但 sudo 仍可能要求输入密码。可先用 `setup --dry-run` 查看宿主计划。
脚本应显式执行 `setup --yes`。没有配置文件时，无需另行 `init`。

如果全新、未编辑的默认模板遇到子网冲突，setup 可以选择其他私有 `/24`，
并将已有模板备份为 `barn.yml.before-network-change`。显式 `-f` 文件、编辑过的模板和已有部署保留原网段。

## 关键参数

| 参数 | 含义 |
|---|---|
| `--json`、`--yaml` | stdout 机器可读；进度仍写 stderr；刻意不设短参数 |
| `-v`、`--verbose` | 向 stderr 输出限制长度的诊断信息 |
| `-c`、`--cidr` | 为 `init`/`setup` 生成模板或宿主网络检查/安装选择 RFC1918 `/24` |
| `-f`、`--file` | 为读取期望状态的命令选择清单 |
| `-r`、`--repo` | 在提供此参数的命令上选择仓库；覆盖 `--mirror` 与 `BARN_REPO`；`validate` 在 Barn 0.9.0 新增此参数 |
| `--mirror` | 为 setup、镜像目录与需要解析镜像的生命周期命令选择中国官方仓库 |
| `-m`、`--mode` | 在提供该参数的命令中选择 macOS `host`/`shared` 网络模式 |
| `-d`、`--dry-run` | 只展示 setup/image 计划，不改变状态 |
| `-y`、`--yes` | 应用已展示的宿主/setup/image 计划 |
| `--force`（`init`、`destroy`、`recreate`） | 覆盖生成文件或跳过输入确认词；因为 `-f` 用于选择清单，所以只保留长参数 |
| `-n`、`--no-wait` | QEMU 运行后即返回，跳过客机就绪检查、恢复与元数据刷新 |
| `--rollback`（`up`、`reload`） | 清除本次运行中准备失败节点的残留产物 |
| `--delete-persistent` | 整体销毁时也删持久盘；不能与节点选择器一起使用 |
| `--purge` | 删除整套部署的磁盘、密钥与状态，保留镜像 |

参数属于各自命令，下表列出容易混淆的作用域：

| 命令 | 专用参数 |
|---|---|
| `init` | `--output/-o`（默认 `./barn.yml`，`-` 表示打印）、`--cidr/-c`、`--force` |
| `setup [meta\|dual\|trio\|full]` | `--file/-f`、`--cidr/-c`、`--repo/-r`、`--mirror`、`--mode/-m`、`--dry-run/-d`、`--yes/-y`；默认模板为 `meta` |
| `validate` | `--file/-f`、`--repo/-r`；不接受节点 |
| `plan` | `--file/-f`、`--repo/-r`；没有 `--mirror` 或 `--dry-run` |
| `up`、`reload` | `--file/-f`、`--repo/-r`、`--mirror`、`--no-wait/-n`、`--rollback` |
| `recreate` | `--file/-f`、`--repo/-r`、`--mirror`、`--force`、`--no-wait/-n`；没有 `--rollback` |
| `start`、`restart` | `--no-wait/-n`；没有 `--file` 或仓库选择参数 |
| `stop`、`status` | 只接受节点选择器与通用展示参数 |
| `destroy` | `--force`、`--delete-persistent`、`--purge`；后两者只能用于整套部署 |
| `purge`、`doctor`、`version` | 没有专用参数或位置参数 |
| `provision` | 必须提供 `--script/-s`；`--sudo` 使用客机 `sudo -n`；`--parallel/-p` 为 1–4，默认 1；`--timeout/-t` 为正值、最多 24h，默认 1h |
| `ssh-config` | `--install/-i` 与 `--remove` 互斥；`--name` 默认为 `barn`；移除不接受节点，也不要求部署状态存在 |
| `logs` | `--source/-s serial\|qemu\|events`，默认 `serial`；`--follow/-f`；events 不接受节点 |
| `image info`、`image pull` | 可选镜像选择器、`--arch/-a amd64\|arm64`、`--repo/-r`；只有 pull 接受 `--mirror` |
| `image import` | `--sha256/-s`；指定 `--name local-*` 还必须提供 `--boot/-b bios\|uefi` 与 `--source-user/-u` |
| `image prune` | `--dry-run/-d` 与 `--yes/-y` 互斥；`--repo/-r` |
| `image sync` | URL 或路径、`--repo/-r`、显式 `--allow-downgrade` |
| `update` | `--repo/-r`、`--mirror`；不接受镜像选择器 |
| `image list`、`image reset` | `--repo/-r`；不接受选择器、`--arch` 或 `--mirror` |
| `repo scan/build/verify` | 必须提供一个绝对路径的仓库目录；没有专用参数 |
| `network install` | `--cidr/-c` 默认 `10.10.10.0/24`，`--mode/-m` 默认 `host`，`--yes/-y`；`--archive/-a`、`--interface-id/-i` 仅限 macOS |
| `network status` | 可选 `--cidr/-c`；没有 `--file` |
| `network uninstall`、`hosts install/uninstall` | `--yes/-y` |

`setup --dry-run` 与 `setup --yes` 互斥。`--cidr` 用来调整生成模板的网段，不能重写显式
选择的清单。`validate --repo` 是 Barn 0.9.0 新增参数，没有对应的 `--mirror`；
需要检查中国仓库时使用 `--repo https://repo.pigsty.cc/barn`。

Barn 0.9.1 中，`network` 与 `hosts` 的 install/uninstall 会在终端展示计划并要求确认。
安装默认同意，卸载默认拒绝。非终端只展示计划，除非传入 `--yes`。
macOS 首次网络安装使用 `setup`；`network install` 会在 sudo 提示前引导到该命令。
`--yes` 接受 Barn 计划，不能提供 sudo 密码。
节点运行时，`network uninstall` 会拒绝移除网络。停止或销毁部署不会卸载宿主级网络。

`--mirror`、`--force`、`--rollback`、`--remove`、`--allow-downgrade`、`--sudo`、
`--delete-persistent`、`--purge` 只提供长参数。读取清单的命令中，`-f` 选择文件；
`logs -f` 则表示 `--follow`。
以上是 Linux 命令的规则：`-n` 表示 `--no-wait`，`-d` 表示预演。
Mac 命令的 `barn mac logs -n` 用于设置日志行数。

存在部署时，`barn purge` 与 `barn destroy --force --purge` 执行相同的整体删除，且无需确认。
它不接受节点或清单。它删除整套部署、持久盘、密钥、状态和默认 SSH 配置片段，保留镜像与宿主网络。
没有部署时，它返回成功，也可清除能够证明归属的保留盘。
缺少状态文件时，Barn 不会仅凭路径删除无法证明身份的遗留节点产物。
Barn 0.9.1 中，没有部署时的普通整体 `destroy` 也返回成功。
但 `destroy --force --delete-persistent` 和 `destroy --force --purge` 会报错，提示改用 `purge`。

## 结构化失败

下列失败格式适用于 **Barn 0.9.1**。自动化应先检查进程退出码，再按具体命令解析输出。

普通失败会在 stderr 输出 `error: <消息>`。外部工具失败时，Barn 附上该工具 stderr 的最后几行。
有明确下一步时，Barn 再输出一行 `next:`。SSH 子进程退出失败时，Barn 保留子进程输出，不重复打印错误。
如果命令没有专用结果格式，结构化模式会输出通用失败对象，然后返回退出码。
该对象包含 `error`、`message`，以及适用时的稳定 `reason`、`next`、`operation_id`。
外部程序详情放在 `command` 中，包含 `name`、`argv`、`exit_status`、`signal`、`timed_out`、`stderr`。
已携带失败状态的结果后面不会追加第二份 JSON/YAML 文档。
通用对象的 `error` 使用下方表格中的固定类别。
`recreate_required` 和 `nodes_removed` 改为 `error: "conflict"` 下的 `reason`。
旧的 `resource_conflict` 类别改为 `resource`。

**非零退出不保证 stdout 一定是这个通用对象。**
`doctor`、`network`、`provision`、生命周期操作与远端命令可以返回各自的报告结构。
SSH 子进程退出在内部归类为 `remote_exit`。
公开结果包含 `success`、`exit_code`、`stdout`、`stderr` 等字段，可选 `error` 也不遵循通用错误分类。
解析结果时也应保留进程退出码。

## 生命周期结果

省略节点选择器时，生命周期命令作用于全部节点。
`ssh`、`exec` 与节点日志默认选择已完成准备的控制节点。
控制节点尚未完成准备时，Barn 回退到第一个已完成准备的节点。
选择器使用 `meta` 等节点名，不接受清单 IP、分组名或 `vm_alias` 别名。

`restart` 不读取清单，直接重启已应用节点。
`reload` 先检查期望清单，再停止所选节点并执行 `up`。它可以增加节点，但会拒绝定义变化或节点移除。
`recreate` 用于显式应用节点定义变化。它会替换根盘和非持久数据盘，保留兼容的持久盘。
执行前，请通过 `barn plan` 和[数据盘策略](../configuration/#数据盘)检查影响范围。

若未选节点仍有冲突的配置变化，Barn 会在停机、删盘前拒绝局部重建。请按提示一起选中需要重建的节点。

配置差异需要破坏性操作时，Barn 返回冲突，并给出下一步命令。
先运行 `barn plan`，再运行 `barn recreate <node>` 或 `barn destroy <node>`。
终端上这两条命令会要求输入确认词。脚本可用 `--force` 跳过此提示。

### 计划

`plan` 是只读操作，即使 action 为 `recreate` 或 `blocked-removal`，也返回成功。
自动化必须检查 action 与 `create`、`start`、`recreate`、`missing`、`blocked` 字段。

对于镜像目录中的镜像，计划只读取本地配置和镜像目录，无需先安装 QEMU 或宿主网络。
已注册的 `local-*` 镜像还会校验缓存，因此需要 `qemu-img`。
计划不会下载镜像。它显示精确镜像、资源总量、变更原因和磁盘影响。
Barn 0.9.1 还逐项列出数据盘，包括隐式的 128 GiB `/data`。

### 启动与 SSH 配置

`up` 会在执行前检查宿主能力与地址可用性。
`up` 创建缺失节点、启动已停止节点，并复查运行中节点的就绪状态。
它还根据完整的已应用部署重写 Barn 安装的 SSH 客户端配置。
`recreate` 同样刷新完整配置。节点级 destroy 删除旧条目，整体 destroy 移除该配置。
`start` 启动已停止节点，并复查运行中节点的就绪状态。`start` 与 `restart` 也会刷新 SSH 别名。

虚拟机生命周期操作成功，但 SSH 客户端配置无法写入时，命令会给出警告并返回成功。
`barn ssh` 仍然可用。结构化输出通过 `warnings[]` 报告集成问题。

Barn 0.9.1 不修改符号链接或硬链接形式的 `~/.ssh/config`。
它会写入独立配置片段，并提示需手动加入的 `Include` 行。

启动命令完成后，Barn 还会刷新运行中客机的 Barn hosts 和控制节点 SSH 配置。
已停止节点在下次启动时更新。

控制节点中由 Barn 管理的 SSH 条目不固定客机主机密钥，也不写入 known_hosts，
因此重建实验节点后可以直接连接。用户自行添加的 SSH 配置会保留。

### 就绪

管理 SSH 可用时，Barn 认为客机已就绪。
可选初始化问题通过 `nodes[].warnings` 报告。已完成的恢复操作（包括数据盘重置）写入 `nodes[].repairs`。
客机可用但存在这些限制时，命令返回 0。
再次执行 `up` 会重试未完成步骤，无需重启运行中的虚拟机。
自动化若要求全部配置功能可用，应检查警告字段。

`--no-wait` 跳过客机就绪检查、恢复和客机 SSH/hosts 刷新。随后执行 `up` 可完成这些步骤。

### 节点失败

生命周期批处理出现可隔离的节点级失败时，即使所有选中节点都失败，也可能返回 5。
错误格式为 `N of M node(s) failed: <node> (<stage>: <error>); ...`。
常见阶段包括 `prepare`、`start`、`readiness`、`bootstrap`、`guest-setup`、`stop`、`status`。
`readiness` 或 `bootstrap` 失败时，Barn 会提示运行 `barn logs <node>` 查看客机控制台。
结构化输出携带 `failures[]`，其中包含 `node`、`stage`、`error`。Barn 0.9.1 还有可选的 `reason`。
当 `--rollback` 清除了尚未提交状态的节点准备产物时，结果还会带上 `rolled_back`。
参见[节点未就绪](../../start/troubleshooting/#节点未就绪)。

### 状态

`status` 默认展示节点、状态、IP、精确镜像和 CPU/内存。
`--verbose` 还展示 SSH 端口、架构、加速器与 PID。普通文本也会标记 TCG。
一个节点异常时，Barn 保留其他节点的状态，并返回 5。结构化输出包含逐节点 `error` 和 `failures[]`。
running 只表示虚拟机进程正在运行；状态查询不会检查客机是否就绪。

## 恢复行为

执行 `up`、`start` 时，宿主共享目录缺失只影响对应节点。
`up` 在新节点准备失败后，仍会启动独立的已有停止节点。
操作部分成功时，命令以 5 退出，已成功的节点保持不变。重试提示保留配置文件、镜像仓库及适用参数。
`start` 的重试命令仍为 `start`。

宿主准备与随后的生命周期重试使用同一个 `operation_id`。
首次准备失败且尚无部署状态时，也可通过 `barn logs --source events --json` 读取有大小上限的阶段日志。
该日志不记录命令参数和认证信息，详细原因以命令输出为准。`setup --dry-run` 不写日志。

`destroy --delete-persistent` 与 `purge` 的成功摘要只描述最终删除或保留的资源。
purge 仍保留镜像缓存和宿主网络。

先删除某个节点后留下的受管持久盘，不再阻断其余节点的销毁。
普通 destroy 继续保留这些盘，只有显式删除持久盘或 purge 才会移除它们。

macOS 安装新网络时，先完成 Homebrew 发现和安装，或下载固定归档，再申请管理员认证。
此顺序避免 Homebrew 清除先前 sudo 凭据而导致安装失败，不改变特权操作范围。
下载失败时，Barn 不会提前要求输入密码。

## 中断操作恢复

QEMU PID 已被无关进程复用时，Barn 将节点识别为已停止。
停止操作中断但虚拟机仍在运行时，Barn 将状态恢复为 running。其他未完成操作会提示可继续执行的命令。
`destroy` 会继续处理被中断的状态转换。
首次 `up` 失败后，可以编辑清单再重试。Barn 会按日志记录回滚未提交的产物。

## 日志与环境变量

`logs` 默认读取客机串口。`--source qemu` 读取 QEMU 诊断，`--source events` 读取有大小上限的部署事件日志。
使用 `--follow` 时，文本流式输出字节，JSON 输出 NDJSON 记录，YAML 输出文档流。
Barn 0.9.1 将普通事件日志和 QEMU 日志显示为可读记录。只有 `--verbose` 才显示 QEMU 命令参数。

| 环境变量 | 用途 |
|---|---|
| `BARN_HOME` | 绝对路径的私有状态目录，默认 `~/.barn`；不能是符号链接或用户主目录等范围过大的目录 |
| `BARN_REPO` | 默认仓库；被命令提供的 `--mirror`、`--repo` 依次覆盖 |
| `BARN_OUTPUT` | `text`、`json`、`yaml`；展示参数优先 |
| `BARN_VERBOSE` | 布尔诊断默认值；展示参数优先 |
| `BARN_VMNET_ARCHIVE` | macOS setup 使用的固定 socket_vmnet 归档绝对路径，仍执行摘要检查 |
| `NO_COLOR` | 非空时关闭颜色 |

## SSH 透传与命令补全

`barn ssh [node] [--] [command ...]` 打开会话，或运行可选命令。
`barn exec [node] [--] <command ...>` 必须给出命令，并透传退出码。
`--` 之前的展示参数属于 Barn。
`ssh` 将 `--` 之后的参数按普通 SSH 的方式用空格连接，交给远端 shell 解释。
`exec` 保留多个参数的边界。需要 shell 展开或管道时，请显式使用 `sh -c`。
单个命令字符串仍保留 shell 简写行为。

有 `--` 时，其前面只能为空或一个已知节点。
交互使用时，也可以省略 `--`。首参数是已知节点时，Barn 选择该节点。
否则，Barn 把整段作为默认节点上的命令，并显示警告。

Barn 0.9.1 会检查包含数字或 `-` 的首参数是否像节点名误拼。
长度不超过四个字符时，允许的编辑距离最多为一个；更长时，最多为两个。符合时，Barn 拒绝执行。
`ls`、`df`、`wc` 等普通命令仍可运行。脚本中请明确写 `--`。

加载 `barn completion bash|zsh|fish|powershell` 可启用命令及其参数补全。
补全也支持命令别名、模板、镜像别名和枚举参数。节点名从期望规格或已应用规格中只读解析。
Barn 0.9.1 的 `-f` 补全只列出 YAML 文件。

## 退出码

此表列出 **Barn 0.9.1** 的退出码。缺少配置、未知镜像均为 usage（2）；
setup/network 失败按原因区分为 runtime（1）或 capability（3）。

| 代码 | `error` | 含义 |
|---:|---|---|
| 0 | | 成功，包括客机可用但可选功能受限 |
| 1 | `runtime` | 操作已执行但失败（外部工具、下载或客机失败） |
| 2 | `usage` | 命令行或清单有误 |
| 3 | `capability` | 宿主缺少工具、Barn 网络或权限 |
| 4 | `conflict` | 部署当前状态不允许，或另一个 barn 命令正持有它 |
| 5 | `partial` | 节点级批处理失败；检查 `failures[]`，已成功的节点会保留 |
| 6 | `resource` | 宿主地址、端口、网段或磁盘被占用 |
| 7 | `integrity` | 已校验的摘要、签名、身份或属主不一致 |
| 130 | `cancelled` | 被中断（SIGINT/SIGTERM）或拒绝确认 |

Barn 0.9.1 中，另一个 Barn 命令持有部署锁时，修改类命令最多等待 10 分钟，并指出持锁命令。
超时以 4 退出，`reason` 为 `deployment_busy`。
`status`、`ssh`、`exec`、`ssh-config`、`hosts` 不等待。
`status` 显示已记录状态，并通过 `note` 报告并发操作。这不代表该部署操作已完成。

`ssh` 与 `exec` 原样透传 SSH 子进程退出码，包括 255。
255 可能表示 SSH 连接失败，也可能是远端命令返回的值。文本、JSON 与进程退出码保持一致。
