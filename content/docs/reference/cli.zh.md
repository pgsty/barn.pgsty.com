---
title: 命令行
description: Farrow 命令、关键参数、结构化输出与退出码。
weight: 20
icon: fa-solid fa-terminal
aliases: [/docs/reference/json-api/]
---

```text
farrow [--json|--yaml] [-v|--verbose] <command> [flags] [node...]
```

已安装的二进制是当前版本最准确的参考。每一条可见命令都自带操作边界与可复制样例：

```bash
farrow --help
farrow setup --help
farrow image pull --help
```

直接运行 `farrow` 会显示简短欢迎信息和下一步命令，并以 2 退出；`farrow image` 这样的
裸命名空间打印帮助并以 2 退出。
JSON/YAML 模式下，空命名空间返回结构化用法错误。显式 `--help` 始终输出供人阅读的
帮助文本。

## 命令

| 范围 | 命令 |
|---|---|
| 准备 | `setup`、`init`、`validate`、`doctor` |
| 生命周期 | `plan`、`up`、`start`、`stop`、`restart`、`reload`、`recreate`、`status`、`destroy`、`purge` |
| 访问 | `ssh`、`exec`、`logs`、`provision`、`ssh-config`、`hosts install/uninstall` |
| 镜像 | `update`、`image list/info/pull/import/sync/prune/reset`、`repo scan/build/verify` |
| 宿主网络 | `network status/install/uninstall` |
| 其他 | `version`、`completion` |

没有命令会隐式刷新 Catalog。`update` 获取配置仓库的 Catalog，校验并激活；
`image sync` 是为精确 URL 或文件准备的显式恢复路径。普通命令只使用当前本地 Catalog。
两者都不更新 Farrow 可执行文件。

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
`completion` 没有别名；`purge` 也刻意不设别名，两个字母不应丢弃整个实验室。
命名空间内部，`hosts` 与 `network` 的 install/uninstall 使用
`i`/`u`，`network status` 使用 `st`；`image` 使用 `list=ls`、`info=in`、`pull=p`、
`prune=pr`、`sync=sy`、`import=i`。`image reset` 保留 `reset-manifest` 作为兼容别名。

使用已应用状态的命令可在任意目录运行。配置来源由命令决定，`-f` 刻意不做全局参数：

| 命令 | 期望状态来源 |
|---|---|
| `setup [template]` | 显式 `-f`，否则发现配置，否则生成 `meta`；模板与 `-f` 互斥 |
| `init [template]` | 生成新 Inventory，不读取期望状态；`--force` 显式替换输出文件 |
| `validate` | 显式 `-f`，再发现配置；绝不回退到已应用状态 |
| `plan`、`up`、`reload`、`recreate` | 显式 `-f`，再发现配置，最后回退到已应用规格 |
| 其他生命周期/访问命令 | 不读取期望配置；使用已应用状态 |

没有配置文件且没有已应用部署时，交互式 `up` 可以生成默认配置；它也能准备缺少的宿主
依赖、恢复完整但未激活的 Farrow 网络。该内部准备流程接受 setup 计划，sudo 仍可能
请求凭据；可先用 `setup --dry-run` 查看宿主计划。脚本应显式执行 `setup --yes`，
没有配置文件时无需另行 `init`。

## 关键参数

| 参数 | 含义 |
|---|---|
| `--json`、`--yaml` | stdout 机器可读；进度仍写 stderr；刻意不设短参数 |
| `-v`、`--verbose` | stderr 有界诊断 |
| `-c`、`--cidr` | 为 `init`/`setup` 生成模板或宿主网络检查/安装选择 RFC1918 `/24` |
| `-f`、`--file` | 为读取期望状态的命令选择 Inventory |
| `-r`、`--repo` | 选择镜像/制品仓库；覆盖 `--mirror` 与 `FARROW_REPO` |
| `--mirror` | 为 setup、Catalog 与需要解析镜像的生命周期命令选择中国官方仓库 |
| `-m`、`--mode` | 在提供该参数的命令中选择 macOS `host`/`shared` 网络模式 |
| `-d`、`--dry-run` | 只展示 setup/image 计划，不改变状态 |
| `-y`、`--yes` | 应用已展示的宿主/setup/image 计划 |
| `--force`（`init`、`destroy`、`recreate`） | 覆盖生成文件或跳过输入确认词；因为 `-f` 用于选择 Inventory，所以只保留长参数 |
| `-n`、`--no-wait` | QEMU 运行后即返回，跳过 Guest 就绪检查、恢复与元数据刷新 |
| `--rollback`（`up`、`reload`） | 清除本次运行中 prepare 失败节点的残留产物 |
| `--delete-persistent` | 整体销毁时也删持久盘；不能与节点选择器一起使用 |
| `--purge` | 整体处置：删除磁盘、密钥与 deployment 状态，保留镜像 |

`--mirror`、`--force`、`--rollback`、`--remove`、`--allow-downgrade`、`--sudo`、
`--delete-persistent`、`--purge` 等低频或扩大风险边界的参数只保留长版本。读取
Inventory 的命令中 `-f` 始终选择文件；`logs -f` 保留惯用的 `--follow`。
`-n` 始终表示 `--no-wait`，`-d` 始终表示 Dry-run。

`farrow purge`（别名 `farrow rm`）是不经确认的
`farrow destroy --force --purge` 快捷路径。它不接受节点或 Inventory，删除整套 Deployment、
持久盘、密钥、状态和默认 SSH Fragment，保留镜像与宿主网络。没有 Deployment 时幂等成功；
缺少状态文件绝不会授权按路径删除无法证明身份的遗留节点工件。

如果失败命令尚未输出更丰富的类型化结果，结构化模式会先输出一份包含 `error` 与
`message` 的对象，再返回约定的非零退出码；已经携带失败状态的结果后面绝不会追加第二份
JSON/YAML 文档。

`plan` 是只读操作，即使 action 为 `recreate` 或 `blocked-removal` 也返回成功；自动化必须
检查 action 与 `create`、`start`、`recreate`、`missing`、`blocked` 字段。计划只读取
本地配置和 Catalog，无需先安装 QEMU 或宿主网络；它显示精确镜像、资源总量、变更原因
和磁盘影响。宿主能力与地址可用性由 `up` 在执行前检查。`up` 会创建缺失节点、启动已停止
节点、复查运行中节点的就绪状态，并根据完整的 applied deployment 重写 Farrow 安装的
SSH 客户端配置；`recreate` 同样执行全量刷新，节点级 destroy 删除旧条目，整体 destroy
移除该配置。`start` 启动已停止节点并复查运行中节点的就绪状态，`start` 与 `restart` 也会刷新 SSH 别名。
破坏性 drift 返回冲突，并给出下一步命令：先 `farrow plan`，再 `farrow recreate <node>`
或 `farrow destroy <node>`；终端上这两条命令会要求输入确认词，`--force` 仅用于脚本。
如果 VM 生命周期成功但 SSH 客户端配置无法写入，命令会给出警告并返回成功；
`farrow ssh` 仍然可用。结构化输出通过 `warnings[]` 报告集成问题。

就绪边界是管理 SSH 可用。可选初始化问题通过 `nodes[].warnings` 报告，已完成的恢复
操作（包括数据盘重置）写入 `nodes[].repairs`。客机可用但有这些限制时返回 0；重复 `up`
会重试未完成步骤，无需重启运行中的 VM。要求全部配置功能可用的自动化应检查警告字段。

多节点操作中若有节点失败，退出码为 5，并报告
`N of M node(s) failed: <node> (<stage>: <error>); ...`。阶段为 `prepare`、`start`、
`readiness`、`guest-setup`、`stop`、`status`；`readiness` 失败会追加 `run \`farrow logs <node>\` for the guest
console`。结构化输出携带 `failures[]`（`node`、`stage`、`error`）；当 `--rollback` 清除了
从未提交节点的 prepare 产物时，还会带上 `rolled_back`。参见
[节点未就绪](../../start/troubleshooting/#节点未就绪)。

`status` 默认展示节点、状态、IP、精确镜像和 CPU/内存；`--verbose` 展示 SSH 端口、
架构、加速器与 PID。TCG 在普通文本中也有标记。一个节点异常时，仍保留其他节点的
状态，并返回 5；结构化输出包含逐节点 `error` 和 `failures[]`。running 表示 VM
正在运行，不代表本次 status 检查了 guest 就绪状态。

启动命令完成后还会刷新运行中 guest 的 Farrow hosts 和控制节点 SSH 配置；停止中的
节点在下次启动时更新。`--no-wait` 会跳过 guest 就绪检查、恢复和刷新，随后执行 `up` 补齐。
局部 recreate 若仍受未选节点的配置变化影响，会在停机、删盘前拒绝；按提示一次选择
需要重建的节点。

控制节点中由 Farrow 管理的 SSH 条目不固定 guest 主机密钥，也不写入 known_hosts，
因此重建实验节点后可以直接连接。用户自行添加的 SSH 配置会保留。

## 0.8 恢复行为

`up`、`start` 按节点隔离宿主共享目录
缺失的影响；`up` 在新节点准备失败后仍会启动独立的已有停止节点。部分成功保留退出码
5 和成功节点。重试提示保留配置文件、镜像仓库及适用参数，`start` 的重试仍为 `start`。

setup 与随后生命周期重试使用同一个 `operation_id`。首次 setup 失败、尚无部署状态时，
也可通过 `farrow logs --source events --json` 读取有大小上限的阶段日志。setup 日志不记录
命令参数和认证信息，详细根因以命令输出为准；`setup --dry-run` 不写日志。
`destroy --delete-persistent` 与 `purge` 成功摘要只描述最终删除、保留的资源；purge
仍保留镜像缓存和宿主网络。
先删除某个节点后留下的受管持久盘，不再阻断其余节点的销毁。普通 destroy 继续保留
这些盘，只有显式删除持久盘或 purge 才会移除它们。

macOS 新网络安装先完成 Homebrew 发现/安装或固定归档下载，再申请管理员认证。
这避免了 Homebrew 清除先前 sudo 凭据导致的安装失败，不扩大特权操作范围；
下载失败时不会提前要求输入密码。

## SSH 透传与命令补全

`farrow ssh [node] [--] [command ...]` 打开会话或运行可选命令；
`farrow exec [node] [--] <command ...>` 必须给出命令并透传退出码。`--` 之前的展示参数
属于 Farrow。`ssh` 之后的参数会像普通 SSH 一样以空格连接，再交给远端 shell 解释；
`exec` 保留多个参数的边界，需要 shell 展开或管道时请显式使用 `sh -c`；
单个命令字符串仍保留 shell 简写行为。
有 `--` 时，其前面只能是空或一个已知节点。为方便交互使用，也接受省略 `--`：已知
首参数选节点，否则把整段当成默认节点上的命令，并显示 warning。脚本中建议明确写 `--`。

加载 `farrow completion bash|zsh|fish|powershell` 可获得命令与作用域准确的参数补全，
同时补全命令别名、模板、镜像别名、枚举参数，以及从期望/已应用规格只读解析出的节点名。

## 退出码

| 代码 | `error` | 含义 |
|---:|---|---|
| 0 | | 成功，包括客机可用但可选功能受限 |
| 1 | `runtime` | 操作已执行但失败（外部工具、下载或客机失败） |
| 2 | `usage` | 命令行或 Inventory 有误 |
| 3 | `capability` | 宿主缺少工具、Farrow 网络或权限 |
| 4 | `conflict` | Deployment 当前状态不允许，或另一个 farrow 命令正持有它 |
| 5 | `partial` | 部分节点成功、部分失败 |
| 6 | `resource` | 宿主地址、端口、网段或磁盘被占用 |
| 7 | `integrity` | 已校验的摘要、签名、身份或属主不一致 |
| 130 | `cancelled` | 被中断（SIGINT/SIGTERM）或拒绝确认 |

失败时 stderr 输出 `error: <消息>`；外部工具失败时附上它 stderr 的最后几行；有明确下一步时
再输出一行 `next:`。结构化模式的失败对象包含 `error`（上表类别）、`message`，以及适用时的
稳定 `reason`、`next` 和描述外部程序的 `command`。遇到另一个 farrow 命令持有 Deployment 时，
修改类命令最多等待 10 分钟并指出对方；`status`、`ssh`、`exec`、`ssh-config`、`hosts`
不等待，直接显示已记录状态并附 `note`。

`ssh` 与 `exec` 原样透传 SSH 子进程退出码，包括 255；255 可能是 SSH 连接失败，
也可能是远端命令返回该值。文本、JSON 与进程退出码保持一致。
