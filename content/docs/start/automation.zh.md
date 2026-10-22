---
title: 自动化与客机脚本
linkTitle: 自动化
description: 准备无人值守实验环境，检查 JSON 结果，并在选定客机内运行可重复执行的脚本。
weight: 60
icon: fa-solid fa-terminal
---

本文示例以 **Barn 0.9.1** 为准。
以拥有部署的普通 Unix 用户运行宿主命令。每次调用使用同一份清单和 `BARN_HOME`。切换工作目录不会创建独立实验环境。

## 准备可预测的实验环境

使用自定义镜像仓库时，setup 与 up 应传入相同的 `--repo`。规划前，用 `barn update --repo URL` 显式激活该仓库的镜像目录。详见[镜像仓库](../images/)。

第一次部署时，先生成并审查配置，再交给自动化运行：

```bash
mkdir -p ~/barn-lab
cd ~/barn-lab
barn init dual
# 继续之前先编辑 barn.yml。
barn version
barn validate -f barn.yml
barn plan -f barn.yml
barn setup -f barn.yml --dry-run
```

将选定的清单纳入版本管理。显式设置 `vm_image`。如果更新镜像目录后创建的新节点也必须使用同一基础镜像，可固定为 `vm_image: u24@20260926.0.0`。
显式 `-f` 还会禁止首次 setup 自动把未编辑的默认模板迁移到其他子网。

审查宿主计划后，执行一次宿主准备：

```bash
barn setup -f barn.yml --yes
barn up -f barn.yml --json > up.json
```

`--yes` 表示接受 setup 计划，不会提供 sudo 凭据。
无人值守执行 `up` 前，必须准备好宿主依赖、网络和权限策略。
非交互式 `up` 不会执行首次宿主准备，也没有 `--yes` 参数。

## 不只检查退出码

Barn 将结构化结果写到 stdout，诊断写到 stderr。保留两种输出与命令退出码，
避免后续 Shell 命令覆盖需要检查的状态。下面是额外依赖 `jq` 的 Bash 示例：

```bash
#!/usr/bin/env bash
set -euo pipefail

if barn up -f barn.yml --json > up.json 2> up.stderr; then
  jq -e '
    (.nodes | type == "array" and length > 0) and
    all(.nodes[];
      .state == "running" and .ready == true and
      ((.warnings // []) | length == 0) and
      ((.repairs // []) | length == 0)) and
    ((.warnings // []) | length == 0)
  ' up.json || exit 1
else
  barn_exit=$?
  cat up.stderr >&2
  cat up.json
  exit "$barn_exit"
fi
```

此示例采用严格的验收策略：`jq` 要求每个返回节点均已就绪，且没有功能限制或已报告的修复动作。
客机可用但可选数据盘、共享或节点间 SSH 失败时，Barn 仍可能返回**退出码 0**，
并在 `nodes[].warnings` 中列出限制。`nodes[].repairs` 可能报告已丢弃测试数据的
文件系统重置。根据工作负载的验收策略检查这些字段。顶层 warnings
还可能描述可选 SSH 集成或元数据刷新失败。验收失败时，显式 `|| exit 1` 会终止脚本。即使后续追加其他命令，失败状态也不会被覆盖。

下一步依赖客机就绪时，不要使用 `--no-wait`。`status --json` 是虚拟机状态与缓存警告
的快照，不是新一轮客机就绪测试。用 `up` 完成初始化。如果流程依赖某个服务，还需在客机内执行相应的应用检查。

### 失败与版本边界

结合[命令行退出码](../../reference/cli/#退出码)与具体命令的结果结构判断。
部分失败可能保留已经成功的节点；重试前查看结果中存在的 `nodes` 或 `failures`。

Barn 0.9.1 使用明确的错误分类。例如首次缺少配置、未知镜像均为 usage/2；
`recreate_required` 与 `nodes_removed` 是 conflict/4 下的 `reason`。
它还使用有上限的锁等待，超时报 `deployment_busy`。

并非每个失败命令都返回通用的 `error`/`message` 结构。doctor、network status、provision 与 SSH 执行可能返回各自的报告。

例如，`doctor` 的 network 类检查未通过时，也可能退出 0。依赖宿主网络时，应检查 `checks[]` 与 `barn network status --json`。

`ssh`/`exec` 透传远程退出状态，包括 OpenSSH 的 255。
请检查结构化执行结果中的 `success`、`exit_code`、`stdout` 与 `stderr`，不要把远程退出状态当成 Barn 错误分类。

## 执行单条命令或脚本

显式指定节点，用 `--` 分隔远程命令：

```bash
barn exec meta -- hostname
barn exec node-1 -- sh -c 'id; df -h /data'
barn exec meta --json -- uname -a > uname.json
```

多个客机需要执行相同检查时，将以下 Bash 脚本保存为 `check-lab.sh`：

```bash
#!/usr/bin/env bash
set -euo pipefail
hostname
id
findmnt /data
test -d /data
```

然后在选定节点运行：

```bash
barn provision --script ./check-lab.sh meta node-1
barn provision --script ./check-lab.sh --parallel 2 --timeout 5m --json > provision.json
```

不带节点选择器时，`provision` 面向部署状态中记录的全部节点。
这些节点必须已运行；该命令不会创建或启动虚拟机。

宿主脚本必须是非空、非符号链接的普通文件，最大 4 MiB，无需可执行权限。
Barn 将同一份已验证的脚本内容传给各客机的 Bash，并记录 SHA-256，不在客机保存脚本文件。

默认串行执行，`--parallel` 可设为 1 到 4。`--timeout` 默认为一小时，
是整个操作的期限，最大 24 小时。`--sudo` 在客机使用 `sudo -n`，无法提示输入密码。
结果包含 `results[]`、各节点 stdout/stderr 与退出码，以及 `successful`/`failed`
计数。部分失败时，已经成功的变更可能保留。编写脚本时，确保重复执行安全。Barn 不会回滚客机命令，也不会在下一次 `up` 自动重跑该脚本。

每个节点最多捕获 1 MiB stdout 和 1 MiB stderr。需要完整输出时，先检查 `stdout_truncated`、`stderr_truncated`。脚本执行期间持有部署锁，生命周期变更
会等待它结束。`audit_error` 表示执行后的审计记录或释放锁失败。退出码 1 不表示脚本未产生变更。

provision 同时有成功与失败目标时退出 5。整个操作只有一个目标且执行失败时，它透传其大于零且不为 255 的远程状态。其他全部失败的情况退出 1。具体客机/SSH 状态见 `results[].exit_code`。

## 与 Pigsty 一起使用

Barn 与 Pigsty 可以读取同一份 `pigsty.yml`，但 `barn init dual` 只生成虚拟机
拓扑，不会配置 PostgreSQL 集群。应从当前 Pigsty 仓库合适的服务配置开始并审查：

```bash
barn validate -f pigsty.yml
barn plan -f pigsty.yml
barn up -f pigsty.yml
barn ssh
```

Barn 准备客机管理员，并把部署私钥复制到 `admin_ip` 选定的控制节点，供它连接其他节点。生成的控制节点 SSH 配置会关闭节点间主机密钥校验；宿主到客机的管理连接
则使用按实例区分的主机密钥信任，详见[安全边界](../../about/security/)。
检查配置和客机连通性后，再通过 Pigsty 部署服务，具体步骤见 [Pigsty 文档](https://pigsty.cc/docs/)。
宿主文件传输与端口隧道见[存储与访问](../storage/)。
