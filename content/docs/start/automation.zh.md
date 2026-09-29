---
title: 自动化与客机脚本
linkTitle: 自动化
description: 准备无人值守实验环境，检查 JSON 结果，并在选定客机内运行可重复执行的脚本。
weight: 35
icon: fa-solid fa-terminal
---

本文示例以 **Barn 0.9.0 发布候选**为准。
宿主命令应由拥有部署的普通 Unix 用户运行。每次调用使用同一份 Inventory 和
`BARN_HOME`；切换工作目录不会创建独立实验环境。

## 准备可预测的实验环境

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

将选定的配置纳入版本管理。显式设置 `vm_image`；如果更新 Catalog 后创建的新节点
也必须使用同一镜像，可固定为 `vm_image: u24@20260911.0.0`。
显式 `-f` 还会禁止首次 setup 自动把未编辑的默认模板迁移到其他子网。

审查宿主计划后，执行一次宿主准备：

```bash
barn setup -f barn.yml --yes
barn up -f barn.yml --json > up.json
```

`--yes` 表示接受 setup 计划，不会提供 sudo 凭据。无人值守执行环境必须提前具备
必要的宿主依赖、网络与权限策略。非交互式 `up` 不会执行交互式首次宿主准备，
`up` 也没有 `--yes` 参数。

使用自定义镜像仓库时，setup 与 up 应传入相同的 `--repo`；规划前先用
`barn update --repo URL` 显式激活该仓库的 Catalog，详见[镜像仓库](../images/)。

## 不只检查退出码

Barn 将结构化结果写到 stdout，诊断写到 stderr。保留两种输出与命令退出码，
避免后续 Shell 命令覆盖需要检查的状态。下面是额外依赖 `jq` 的 Bash 示例：

```bash
if barn up -f barn.yml --json > up.json 2> up.stderr; then
  jq -e '
    (.nodes | type == "array" and length > 0) and
    all(.nodes[];
      .state == "running" and .ready == true and
      ((.warnings // []) | length == 0) and
      ((.repairs // []) | length == 0)) and
    ((.warnings // []) | length == 0)
  ' up.json
else
  barn_exit=$?
  cat up.stderr >&2
  cat up.json
  exit "$barn_exit"
fi
```

此处 `jq` 要求每个返回节点均已就绪，且没有功能限制或已报告的修复动作。
客机可用但可选数据盘、共享或节点间 SSH 失败时，Barn 仍可能返回**退出码 0**，
并在 `nodes[].warnings` 中列出限制。`nodes[].repairs` 可能报告已丢弃测试数据的
文件系统重置。应根据工作负载选择验收策略，而不是忽略这些字段。顶层 warnings
还可能描述可选 SSH 集成或元数据刷新失败。`jq -e` 检查失败会向调用方返回非零状态。

下一步依赖客机就绪时，不要使用 `--no-wait`。`status --json` 是 VM 状态与缓存警告
的快照，不是新一轮客机就绪测试。用 `up` 补齐初始化；如果流程依赖某个服务，
还需在客机内执行相应的应用检查。

### 失败与版本边界

结合[命令行退出码](../../reference/cli/#退出码)与具体命令的结果结构判断。
部分失败可能保留已经成功的节点；重试前查看结果中存在的 `nodes` 或 `failures`。

**0.9 候选**调整了一些错误分类。例如首次缺少配置、未知镜像均为 usage/2；
`recreate_required` 与 `nodes_removed` 是 conflict/4 下的 `reason`。
它还使用有上限的锁等待，超时报 `deployment_busy`。

不是每个失败命令都返回通用的 `error`/`message` 信封：doctor、network status、
provision 与 SSH 执行可能返回各自的报告。`ssh`/`exec` 透传远程退出状态，
包括 OpenSSH 的 255。结构化执行结果应检查 `success`、`exit_code`、`stdout`
与 `stderr`，不要把远程退出状态当成 Barn 错误分类。

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

不带节点选择器时，`provision` 面向所有已提交节点；这些节点必须已运行。
它不会创建或启动 VM。宿主脚本必须是非空、非符号链接的普通文件，最大 4 MiB。
Barn 将同一份已验证的脚本快照流式传给客机 Bash，记录 SHA-256，不会在客机留下
脚本文件；宿主脚本无需可执行权限。

默认串行执行，`--parallel` 可设为 1 到 4。`--timeout` 默认为一小时，
是整个操作的期限，最大 24 小时。`--sudo` 在客机使用 `sudo -n`，无法提示输入密码。
结果包含 `results[]`、各节点 stdout/stderr 与退出码，以及 `successful`/`failed`
计数。部分失败时，已经成功的变更可能保留。脚本应允许安全地重复执行；Barn
不会回滚客机命令，也不会在下一次 `up` 自动重跑该脚本。

provision 同时有成功与失败目标时退出 5；只有一个失败目标时，透传其大于零且不为
255 的远程状态。其他全部失败的情况退出 1，具体客机/SSH 状态见 `results[].exit_code`。

## 与 Pigsty 一起使用

Barn 与 Pigsty 可以读取同一份 `pigsty.yml`，但 `barn init dual` 只生成 VM
拓扑，不会配置 PostgreSQL 集群。应从当前 Pigsty 仓库合适的服务配置开始并审查：

```bash
barn validate -f pigsty.yml
barn plan -f pigsty.yml
barn up -f pigsty.yml
barn ssh
```

Barn 准备客机管理员与控制节点 SSH 访问。检查配置和客机连通性后，再通过
Pigsty 部署服务。[验证记录](../../about/status/)区分了 Ansible 连通性检查与
完整 Pigsty 安装。宿主文件传输与端口隧道见[存储与访问](../storage/)。
