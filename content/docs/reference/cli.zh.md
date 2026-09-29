---
title: 命令行
description: Barn 命令、关键参数、结构化输出与退出码。
weight: 20
icon: fa-solid fa-terminal
aliases: [/docs/reference/json-api/]
---

本参考描述 **Barn 0.9.0 发布候选**。Barn 只使用新名称与全新的 Barn 状态，
不提供旧开发版本的兼容或迁移层。编写脚本前先核对 `barn version`，
发布进度见[当前状态](../../about/status/#documentation-baseline)。

```text
barn [--json|--yaml] [-v|--verbose] <command> [flags] [node...]
```

已安装的二进制是当前版本最准确的参考。每一条可见命令都自带操作边界与可复制样例：

```bash
barn --help
barn setup --help
barn image pull --help
```

直接运行 `barn` 会显示简短欢迎信息和下一步命令，以 0 退出，
JSON/YAML 输出 `actions[]`。`barn image` 这样的裸命名空间仍以 2
退出，文本模式打印帮助，JSON/YAML 模式返回结构化用法错误。显式 `--help` 始终输出
供人阅读的帮助文本并以 0 退出。用 `barn --version` 或 `barn version` 查看构建身份。

## 命令

| 范围 | 命令 |
|---|---|
| 准备 | `setup`、`init`、`validate`、`doctor` |
| 生命周期 | `plan`、`up`、`start`、`stop`、`restart`、`reload`、`recreate`、`status`、`destroy`、`purge` |
| 访问 | `ssh`、`exec`、`logs`、`provision`、`ssh-config`、`hosts install/uninstall` |
| 镜像 | `update`、`image list/info/pull/import/sync/prune/reset`、`repo scan/build/verify` |
| 宿主网络 | `network status/install/uninstall` |
| macOS 客机（尚未发布） | `mac …`，见 [Mac 命令](../mac/) |
| 其他 | `version`、`completion` |

没有命令会隐式刷新 Catalog。`update` 获取配置仓库的 Catalog，校验并激活；
`image sync` 是为精确 URL 或文件准备的显式恢复路径。普通命令只使用当前本地 Catalog。
两者都不更新 Barn 可执行文件。

常用命令提供作用域明确的短别名：

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
`prune=pr`、`sync=sy`、`import=i`。`image reset` 保留 `reset-manifest` 作为兼容别名。

Barn 在选定的 `BARN_HOME`（默认 `~/.barn`）中管理一套部署，其身份与
Inventory 所在目录无关。使用已应用状态的命令可在任意目录运行。配置来源由命令决定，`-f` 刻意不做全局参数：

| 命令 | 期望状态来源 |
|---|---|
| `setup [template]` | 显式 `-f`，否则发现配置，否则生成 `meta`；模板与 `-f` 互斥 |
| `init [template]` | 生成新 Inventory，不读取期望状态；`--force` 显式替换输出文件 |
| `validate` | 显式 `-f`，再发现配置；绝不回退到已应用状态 |
| `plan`、`up`、`reload`、`recreate` | 显式 `-f`，再发现配置，最后回退到已应用规格 |
| 其他生命周期/访问命令 | 不读取期望配置；使用已应用状态 |

没有配置文件且没有已应用部署时，交互式 `up` 可以生成默认配置；它也能准备缺少的宿主
依赖、恢复完整但未激活的 Barn 网络。该内部准备流程接受 setup 计划，sudo 仍可能
请求凭据；可先用 `setup --dry-run` 查看宿主计划。脚本应显式执行 `setup --yes`，
没有配置文件时无需另行 `init`。

## 关键参数

| 参数 | 含义 |
|---|---|
| `--json`、`--yaml` | stdout 机器可读；进度仍写 stderr；刻意不设短参数 |
| `-v`、`--verbose` | stderr 有界诊断 |
| `-c`、`--cidr` | 为 `init`/`setup` 生成模板或宿主网络检查/安装选择 RFC1918 `/24` |
| `-f`、`--file` | 为读取期望状态的命令选择 Inventory |
| `-r`、`--repo` | 在提供此参数的命令上选择仓库；覆盖 `--mirror` 与 `BARN_REPO`；`validate` 在 **0.9 候选版本**新增此参数 |
| `--mirror` | 为 setup、Catalog 与需要解析镜像的生命周期命令选择中国官方仓库 |
| `-m`、`--mode` | 在提供该参数的命令中选择 macOS `host`/`shared` 网络模式 |
| `-d`、`--dry-run` | 只展示 setup/image 计划，不改变状态 |
| `-y`、`--yes` | 应用已展示的宿主/setup/image 计划 |
| `--force`（`init`、`destroy`、`recreate`） | 覆盖生成文件或跳过输入确认词；因为 `-f` 用于选择 Inventory，所以只保留长参数 |
| `-n`、`--no-wait` | QEMU 运行后即返回，跳过 Guest 就绪检查、恢复与元数据刷新 |
| `--rollback`（`up`、`reload`） | 清除本次运行中 prepare 失败节点的残留产物 |
| `--delete-persistent` | 整体销毁时也删持久盘；不能与节点选择器一起使用 |
| `--purge` | 整体处置：删除磁盘、密钥与 deployment 状态，保留镜像 |

参数属于各自命令，下表列出容易混淆的作用域：

| 命令 | 专用参数 |
|---|---|
| `init` | `--output/-o`（默认 `./barn.yml`，`-` 表示打印）、`--cidr/-c`、`--force` |
| `plan` | `--file/-f`、`--repo/-r`；没有 `--mirror` 或 `--dry-run` |
| `start`、`restart` | `--no-wait/-n`；没有 `--file` 或仓库选择参数 |
| `provision` | 必须提供 `--script/-s`；`--sudo` 使用客机 `sudo -n`；`--parallel/-p` 为 1–4，默认 1；`--timeout/-t` 为正值、最多 24h，默认 1h |
| `ssh-config` | `--install/-i` 与 `--remove` 互斥；`--name` 默认为 `barn`；移除不接受节点，也不要求部署状态存在 |
| `logs` | `--source/-s serial\|qemu\|events`，默认 `serial`；`--follow/-f`；events 不接受节点 |
| `image info`、`image pull` | 可选镜像选择器、`--arch/-a amd64\|arm64`、`--repo/-r`；只有 pull 接受 `--mirror` |
| `image import` | `--sha256/-s`；指定 `--name local-*` 还必须提供 `--boot/-b bios\|uefi` 与 `--source-user/-u` |
| `image prune` | `--dry-run/-d` 与 `--yes/-y` 互斥；`--repo/-r` |
| `image sync` | URL 或路径、`--repo/-r`、显式 `--allow-downgrade` |
| `network install` | `--cidr/-c` 默认 `10.10.10.0/24`，`--mode/-m` 默认 `host`，`--yes/-y`；`--archive/-a`、`--interface-id/-i` 仅限 macOS |
| `network status` | 可选 `--cidr/-c`；没有 `--file` |
| `network uninstall`、`hosts install/uninstall` | `--yes/-y` |

`setup --dry-run` 与 `setup --yes` 互斥。`--cidr` 用来调整生成模板的网段，不能重写显式
选择的 Inventory。`validate --repo` 是 **0.9 候选版本**新增参数，没有对应的 `--mirror`；
需要检查中国仓库时使用 `--repo https://repo.pigsty.cc/barn`。

**0.9 候选版本**中，`network` 与 `hosts` 的 install/uninstall 会在终端展示计划并询问确认
（安装默认同意，卸载默认拒绝）；非终端只展示计划，除非传入 `--yes`。
macOS 首次网络安装使用 `setup`；候选版本
的 `network install` 会在 sudo 提示前引导到该命令。`--yes` 接受 Barn 计划，不能提供 sudo 密码。

`--mirror`、`--force`、`--rollback`、`--remove`、`--allow-downgrade`、`--sudo`、
`--delete-persistent`、`--purge` 等低频或扩大风险边界的参数只保留长版本。读取
Inventory 的命令中 `-f` 始终选择文件；`logs -f` 保留惯用的 `--follow`。
`-n` 始终表示 `--no-wait`，`-d` 始终表示 Dry-run。

存在部署时，`barn purge` 与 `barn destroy --force --purge` 执行相同的整体处置，
且无需确认。它不接受节点或 Inventory，删除整套 Deployment、
持久盘、密钥、状态和默认 SSH Fragment，保留镜像与宿主网络。没有部署时幂等成功，
也可清除能够证明归属的保留盘；缺少状态文件绝不会授权按路径删除无法证明身份的遗留节点工件。
**0.9 候选版本**中，没有部署时的普通整体 `destroy` 也返回成功；但
`destroy --force --delete-persistent` 和 `destroy --force --purge` 会报错，提示改用 `purge`。

## 结构化失败（0.9 候选版本）

下列统一失败契约描述 **Barn 0.9.0 发布候选**。

普通失败会在 stderr 输出 `error: <消息>`；外部工具失败时附上它 stderr 的最后几行；
有明确下一步时再输出一行 `next:`。SSH 子进程退出失败不会重复打印错误，直接保留子进程输出。
如果命令没有提供更丰富的类型化结果，结构化模式会输出通用失败对象，包含
`error`、`message`，以及适用时的稳定 `reason`、`next`、`operation_id` 和外部程序详情
`command`（`name`、`argv`、`exit_status`、`signal`、`timed_out`、`stderr`），然后返回退出码。
已携带失败状态的结果后面不会追加第二份 JSON/YAML 文档。
通用对象的 `error` 使用下方表格中的固定类别；`recreate_required` 和 `nodes_removed`
改为 `error: "conflict"` 下的 `reason`，旧的 `resource_conflict` 类别改为 `resource`。

**非零退出不保证 stdout 一定是这个通用对象。** `doctor`、`network`、`provision`、
生命周期操作与远端命令可以返回各自的报告结构。SSH 子进程退出在内部归类为 `remote_exit`，
但公开结果包含 `success`、`exit_code`、`stdout`、`stderr` 等字段，可选 `error` 也不服从
通用错误分类契约。自动化应始终保留进程退出码，再按具体命令解释 payload。

## 生命周期结果

`plan` 是只读操作，即使 action 为 `recreate` 或 `blocked-removal` 也返回成功；自动化必须
检查 action 与 `create`、`start`、`recreate`、`missing`、`blocked` 字段。对于 Catalog
镜像，计划只读取本地配置和 Catalog，无需先安装 QEMU 或宿主网络；已注册的 `local-*`
镜像还会校验缓存，需要 `qemu-img`。计划不会下载镜像；它显示精确镜像、资源总量、变更原因
和磁盘影响。**0.9 候选版本**还逐项列出数据盘，包括隐式的 128 GiB `/data`。
宿主能力与地址可用性由 `up` 在执行前检查。`up` 会创建缺失节点、启动已停止
节点、复查运行中节点的就绪状态，并根据完整的 applied deployment 重写 Barn 安装的
SSH 客户端配置；`recreate` 同样执行全量刷新，节点级 destroy 删除旧条目，整体 destroy
移除该配置。`start` 启动已停止节点并复查运行中节点的就绪状态，`start` 与 `restart` 也会刷新 SSH 别名。
破坏性 drift 返回冲突，并给出下一步命令：先 `barn plan`，再 `barn recreate <node>`
或 `barn destroy <node>`；终端上这两条命令会要求输入确认词，`--force` 仅用于脚本。
如果 VM 生命周期成功但 SSH 客户端配置无法写入，命令会给出警告并返回成功；
`barn ssh` 仍然可用。结构化输出通过 `warnings[]` 报告集成问题。
**0.9 候选版本**不修改符号链接或硬链接形式的 `~/.ssh/config`，会发布独立配置片段，
并提示需手动加入的 `Include` 行。

就绪边界是管理 SSH 可用。可选初始化问题通过 `nodes[].warnings` 报告，已完成的恢复
操作（包括数据盘重置）写入 `nodes[].repairs`。客机可用但有这些限制时返回 0；重复 `up`
会重试未完成步骤，无需重启运行中的 VM。要求全部配置功能可用的自动化应检查警告字段。

生命周期批处理出现可隔离的节点级失败时，即使所有选中节点都失败也可能返回 5，并报告
`N of M node(s) failed: <node> (<stage>: <error>); ...`。常见阶段包括 `prepare`、`start`、
`readiness`、`bootstrap`、`guest-setup`、`stop`、`status`；`readiness` 或 `bootstrap` 失败会追加 `run \`barn logs <node>\` for the guest
console`。结构化输出携带 `failures[]`（`node`、`stage`、`error`，**0.9 候选版本**还有可选
`reason`）；当 `--rollback` 清除了
从未提交节点的 prepare 产物时，还会带上 `rolled_back`。参见
[节点未就绪](../../start/troubleshooting/#节点未就绪)。

`status` 默认展示节点、状态、IP、精确镜像和 CPU/内存；`--verbose` 展示 SSH 端口、
架构、加速器与 PID。TCG 在普通文本中也有标记。一个节点异常时，仍保留其他节点的
状态，并返回 5；结构化输出包含逐节点 `error` 和 `failures[]`。running 表示 VM
正在运行，不代表本次 status 检查了 guest 就绪状态。

启动命令完成后还会刷新运行中 guest 的 Barn hosts 和控制节点 SSH 配置；停止中的
节点在下次启动时更新。`--no-wait` 会跳过 guest 就绪检查、恢复和刷新，随后执行 `up` 补齐。
局部 recreate 若仍受未选节点的配置变化影响，会在停机、删盘前拒绝；按提示一次选择
需要重建的节点。

控制节点中由 Barn 管理的 SSH 条目不固定 guest 主机密钥，也不写入 known_hosts，
因此重建实验节点后可以直接连接。用户自行添加的 SSH 配置会保留。

## 恢复行为

`up`、`start` 按节点隔离宿主共享目录
缺失的影响；`up` 在新节点准备失败后仍会启动独立的已有停止节点。部分成功保留退出码
5 和成功节点。重试提示保留配置文件、镜像仓库及适用参数，`start` 的重试仍为 `start`。

setup 与随后生命周期重试使用同一个 `operation_id`。首次 setup 失败、尚无部署状态时，
也可通过 `barn logs --source events --json` 读取有大小上限的阶段日志。setup 日志不记录
命令参数和认证信息，详细根因以命令输出为准；`setup --dry-run` 不写日志。
`destroy --delete-persistent` 与 `purge` 成功摘要只描述最终删除、保留的资源；purge
仍保留镜像缓存和宿主网络。
先删除某个节点后留下的受管持久盘，不再阻断其余节点的销毁。普通 destroy 继续保留
这些盘，只有显式删除持久盘或 purge 才会移除它们。

macOS 新网络安装先完成 Homebrew 发现/安装或固定归档下载，再申请管理员认证。
这避免了 Homebrew 清除先前 sudo 凭据导致的安装失败，不扩大特权操作范围；
下载失败时不会提前要求输入密码。

## 中断操作恢复（0.9 候选版本）

候选版本会把已被无关进程复用的 QEMU PID 识别为节点停止。stop 中断而 VM 仍运行时，
状态会恢复为 running；其他未完成过渡会指出用于完成它的命令。`destroy` 会自行处理
中断过渡。首次 `up` 失败后可以编辑 Inventory 再重试，因为未提交产物按照日志记录回滚。

## 日志与环境变量

`logs` 默认读取客机串口；`--source qemu` 读取 QEMU 诊断，`--source events` 读取有大小
上限的部署事件日志。使用 `--follow` 时，文本流式输出字节，JSON 输出 NDJSON 记录，
YAML 输出文档流。**0.9 候选版本**将普通 events/qemu 日志读取显示为可读记录，
只有 `--verbose` 才显示 QEMU argv。

| 环境变量 | 用途 |
|---|---|
| `BARN_HOME` | 绝对路径的私有状态目录，默认 `~/.barn`；不能是符号链接或用户主目录等范围过大的目录 |
| `BARN_REPO` | 默认仓库；被命令提供的 `--mirror`、`--repo` 依次覆盖 |
| `BARN_OUTPUT` | `text`、`json`、`yaml`；展示参数优先 |
| `BARN_VERBOSE` | 布尔诊断默认值；展示参数优先 |
| `BARN_VMNET_ARCHIVE` | macOS setup 使用的固定 socket_vmnet 归档绝对路径，仍执行摘要检查 |
| `NO_COLOR` | 非空时关闭颜色 |

## SSH 透传与命令补全

`barn ssh [node] [--] [command ...]` 打开会话或运行可选命令；
`barn exec [node] [--] <command ...>` 必须给出命令并透传退出码。`--` 之前的展示参数
属于 Barn。`ssh` 中 `--` 之后的参数会像普通 SSH 一样以空格连接，再交给远端 shell 解释；
`exec` 保留多个参数的边界，需要 shell 展开或管道时请显式使用 `sh -c`；
单个命令字符串仍保留 shell 简写行为。
有 `--` 时，其前面只能是空或一个已知节点。为方便交互使用，也接受省略 `--`：已知
首参数选节点，否则把整段当成默认节点上的命令，并显示 warning。**0.9 候选版本**会检查
包含数字或 `-` 的首参数是否像节点名误拼：长度不超过四个字符时最多一个编辑距离，
更长时最多两个。符合时会拒绝执行；`ls`、`df`、`wc` 等普通命令仍可运行。脚本中请明确写 `--`。

加载 `barn completion bash|zsh|fish|powershell` 可获得命令与作用域准确的参数补全，
同时补全命令别名、模板、镜像别名、枚举参数，以及从期望/已应用规格只读解析出的节点名。
**0.9 候选版本**还会让 `-f` 补全只列出 YAML 文件。

## 退出码

此表列出 **Barn 0.9.0 发布候选**的退出码契约。缺少配置、未知镜像均为 usage（2）；
setup/network 失败按原因区分为 runtime（1）或 capability（3）。

| 代码 | `error` | 含义 |
|---:|---|---|
| 0 | | 成功，包括客机可用但可选功能受限 |
| 1 | `runtime` | 操作已执行但失败（外部工具、下载或客机失败） |
| 2 | `usage` | 命令行或 Inventory 有误 |
| 3 | `capability` | 宿主缺少工具、Barn 网络或权限 |
| 4 | `conflict` | Deployment 当前状态不允许，或另一个 barn 命令正持有它 |
| 5 | `partial` | 节点级批处理失败；检查 `failures[]`，已经成功的同伴会保留 |
| 6 | `resource` | 宿主地址、端口、网段或磁盘被占用 |
| 7 | `integrity` | 已校验的摘要、签名、身份或属主不一致 |
| 130 | `cancelled` | 被中断（SIGINT/SIGTERM）或拒绝确认 |

**0.9 候选版本**中，修改类命令遇到另一个 Barn 命令持有部署锁时，最多等待 10 分钟
并指出对方；超时以 4 退出，`reason` 为 `deployment_busy`。`status`、`ssh`、`exec`、
`ssh-config`、`hosts` 不等待。`status` 在显示已记录状态时通过 `note` 报告并发操作；
这不代表该部署操作已完成。

`ssh` 与 `exec` 原样透传 SSH 子进程退出码，包括 255；255 可能是 SSH 连接失败，
也可能是远端命令返回该值。文本、JSON 与进程退出码保持一致。
