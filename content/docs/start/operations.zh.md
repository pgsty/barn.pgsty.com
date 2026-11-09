---
title: 日常管理
description: 唯一部署的正常生命周期：检查、访问、扩容、变更、停止与销毁。
weight: 30
icon: fa-solid fa-sliders
aliases: [/docs/start/lifecycle/, /docs/start/provisioning/]
---

本页介绍 Linux 实验环境的日常运维操作。macOS 虚拟机请参阅 [macOS 日常管理](../macos/#everyday-lifecycle)。

## 检查与访问 {#inspect-and-access}

```bash
barn status
barn ssh meta
barn exec node-1 -- hostname
barn logs meta --source serial
```

以上命令直接读取 `BARN_HOME`（默认 `~/.barn`）中记录的已应用状态，只要该路径指向同一位置，就可在任意工作目录下执行。自行设置 `BARN_HOME` 时，跨目录操作请使用绝对路径。`barn status` 默认展示各节点的镜像与资源规格（并在使用软件模拟时标注 `tcg`）；加上 `--verbose` 还会列出客机架构、虚拟化加速器、回环 SSH 端口和 QEMU PID。

每次执行 `barn up`（包括只针对部分节点的局部 `up`）后，Barn 都会根据整套已应用部署刷新 `~/.ssh/barn_config` 中的 SSH 别名，确保 `ssh meta` 等连接始终可用；你也可以随时通过 `barn ssh-config --install` 手动刷新别名。

涉及配置收敛的命令（`plan`、`up`、`reload`、`resize` 和 `recreate`）按以下优先级查找清单：

1. 显式传入的 `-f /path/to/inventory.yml` 参数（当同一目录下同时存在 `barn.yml` 和 `pigsty.yml` 且希望使用后者时必须指定）。
2. 当前工作目录下按顺序匹配到的第一个文件：`barn.yml`、`barn.yaml`、`pigsty.yml`、`pigsty.yaml`（不会向上搜索父目录）。
3. `BARN_HOME` 中记录的已应用规格（`barn validate` 除外，它始终要求提供配置文件）。

重复运行 `barn up` 会自动重试未完成的客机初始化阶段并原位更新旧版客机辅助脚本，已健康的虚拟机无需重启。任何可选功能限制或自动执行的测试盘修复都会显示在终端摘要及 JSON/YAML 的 `nodes[].warnings` 与 `nodes[].repairs` 字段中（详见[数据盘说明](../../reference/configuration/#data-disks)）。

## 停止与启动 {#stop-and-start}

```bash
barn stop
barn start
barn restart node-1
barn reload -f barn.yml       # 校验清单、停止目标节点并重新收敛
```

`barn start` 会启动已停止的虚拟机并复查运行中节点的就绪状态，同时刷新因端口占用而重新分配的回环 SSH 端口与别名。`barn reload` 在停止目标节点前会先校验清单语法、配置漂移与启动依赖，随后对这些节点执行 `barn up` 流程。

`reload` 是受控的“停止后重新启动”流程，可以新增节点或启动已停止节点；但对于已有节点的 CPU、内存、镜像、磁盘、共享目录、地址等虚拟机规格变更，它会在停止任何节点前拒绝执行。修改 CPU 或内存时，请编辑 `vm_cpu` 或 `vm_mem` 后执行 `barn resize`。支持的增加操作可以热插拔；减少资源或后端不支持时会自动停机再启动，同时保留虚拟机身份与磁盘。`resize` 不处理镜像、磁盘、网络或共享目录变更，这些变更使用 `recreate`。

在线 resize 在热插拔后中断时，`barn status` 会提示实际 CPU 和内存可能与已应用配置不一致（`reason: resize_incomplete`）。再次运行 `barn resize NODE` 可继续调整，或执行 `barn restart NODE` 恢复已提交的资源配置。离线 resize 在停止节点和更新状态期间持续持有部署锁。

启动命令传入 `--no-wait` 时会在 QEMU 进程拉起后立即返回，跳过就绪检查、客机恢复以及客机 `/etc/hosts` 和控制节点 SSH 刷新；后续运行一次 `barn up` 即可补齐这些步骤。

## 变更部署 {#change-the-deployment}

```bash
barn plan
barn up                         # 创建或启动目标节点并刷新 SSH 别名
barn resize node-1              # 应用 CPU/内存变更，不重建虚拟机
barn recreate node-1            # 重建规格发生变更的节点
```

`barn plan` 会对比清单文件与已应用状态，展示目标镜像版本、资源总量、漂移原因及磁盘影响：

| 检测到的变化 | 含义 | 应用方式 |
|---|---|---|
| `create` | 清单中新增了尚未创建的节点 | `barn up` |
| `resize` | 节点 CPU 或内存发生变化 | `barn resize <node>` |
| `recreate` | 节点镜像、磁盘、共享目录或其他虚拟机规格发生变化 | `barn recreate <node>` |
| `missing` | 已创建的节点从 YAML 清单中被移除 | 恢复 YAML 条目，或执行 `barn destroy <node>` |
{.wide .expand}

JSON 输出中的 `start`、`create`、`resize`、`recreate` 与 `missing` 是节点列表，顶层 `action` 概括整次计划，取值为 `create`、`start`、`converge`、`resize`、`recreate`、`blocked-removal`、`repair` 或 `none`；可选字段 `blocked` 是说明原因的字符串。`whole_deployment: true` 表示需要重建整个部署；按提示执行命令，确保新节点也一并纳入。

删改 YAML 条目绝不会自动销毁虚拟机；修改 Barn 不消费的 Pigsty 服务级变量则会显示 `action: none`。在交互式终端中执行 `recreate` 和 `destroy` 需输入命令名确认，非交互脚本中则需传入 `--yes`（或 `--force`）。

`recreate` 是显式的替换路径。Barn 会先校验新镜像、网络、共享目录以及持久数据盘的挂载契约，然后销毁选定节点的虚拟机产物，再按目标清单启动全新的虚拟机。根盘和非持久数据盘会被替换；兼容的持久数据盘继续保留并重新挂载。替换后的虚拟机会获得新的身份，同时刷新 SSH 主机密钥状态。

不带节点名的 `recreate` 会替换部署中的全部节点，并在确认提示中逐一列出。如果清单缺少某个已有节点，它会在停止任何虚拟机前拒绝执行（退出码 `4`，`reason: nodes_removed`）：请用 `barn destroy <node>` 显式删除该节点，或把它加回清单。Barn 会在销毁锁内再次核对范围，预检期间已应用状态发生变化时报告 `deployment_changed`。

### 分批应用节点变更 {#selected-nodes}

可以一次编辑多个节点，再分批应用：

```bash
barn plan node-1 -f barn.yml
barn recreate node-1 -f barn.yml
barn plan node-2 -f barn.yml
```

显式选择节点执行 `plan`、`up`、`reload`、`recreate` 或 `resize` 时，未选中节点保留已应用定义，即使 YAML 已修改或暂时省略它们。未创建且未选中的节点会在选中时才解析镜像。整份清单仍须通过语法解析，所选变更也不能与已应用节点的地址、别名、控制节点角色或部署公共设置发生冲突。

不传节点名时，Barn 会检查整份清单：CPU 与内存变更使用 `resize`，其他已有节点规格变更需要 `recreate`，清单中缺失的节点需要恢复定义或显式销毁。

## 并发命令 {#concurrent-commands}

修改部署状态的命令（`up`、`start`、`stop`、`restart`、`reload`、`resize`、`recreate`、`destroy`、`purge` 和 `provision`）会获取 `BARN_HOME` 下的部署锁。若其他操作正在运行，命令最长等待 10 分钟（`provision --timeout` 可指定更短的期限），并打印持锁命令、PID 与启动时间；等待超时将返回退出码 `4`（`error: conflict`、`reason: deployment_busy`）。持锁进程退出后锁会自动释放，切勿手动删除锁文件。

只读与连接类命令（`status`、`ssh`、`exec`、`ssh-config` 以及 `hosts` 的状态读取）无需等待锁，直接读取最新已发布的状态。若后台正有变更命令持锁运行，`barn status` 会附带一条 `note` 说明当前正在执行的操作。异常中断后的恢复步骤见[故障排查](../troubleshooting/#a-command-was-killed)。

## 销毁 {#destroy}

请根据需要清理的范围选择对应的销毁命令：

```bash {tab="销毁单个节点" group="destroy-scope" value="node"}
barn destroy node-3
```

```bash {tab="销毁环境（保留持久盘）" group="destroy-scope" value="lab"}
barn destroy
```

```bash {tab="连同持久盘一并删除" group="destroy-scope" value="persistent"}
barn destroy --delete-persistent
```

```bash {tab="快速清空整套实验环境" group="destroy-scope" value="purge"}
barn purge
```

- `barn destroy <node>` 仅删除指定节点，并为剩余节点刷新 SSH 配置片段。删除控制节点时，剩余的第一个节点接任控制节点，`ssh-config`、`hosts`、`exec` 与 `provision` 可继续使用；请将清单中的 `admin_ip` 改为该节点的地址（除非希望 `up` 重新创建已删除的节点，否则一并删除其条目），再执行 `barn up` 安装其控制 SSH 访问。
- `barn destroy` 删除整套部署的虚拟机、根盘、非持久数据盘、部署状态以及 Barn 安装的 SSH 别名，同时保留持久数据盘、部署密钥、镜像缓存和宿主网络。之后再次运行 `barn up` 即可根据清单重建实验环境。
- `barn destroy --delete-persistent` 与 `barn destroy --purge` 仅适用于整套部署（不支持与节点名称同用），其中 `--purge` 会一并删除持久数据盘、密钥和部署状态。
- `barn purge` 默认立即清空整套 Linux 实验环境，并删除归属明确的遗留持久盘、密钥与部署状态，保留镜像缓存与宿主网络。需要查看节点列表和清理范围后再确认时，运行 `barn purge --ask`，输入 `y`/`yes` 确认或 `n`/`no` 取消；空行和 EOF 也会取消。它不接受 `--yes`、`-y` 或 `--force`。

所有虚拟机移除后，如需卸载多用户共享的 Linux 宿主网络：

```bash
barn network uninstall --yes
```

镜像缓存管理请参阅[镜像仓库](../images/)，完整卸载宿主文件请参阅[卸载与清理](../uninstall/)。
