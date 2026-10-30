---
title: 自动化与客机脚本
linkTitle: 自动化
description: 准备无人值守实验环境，检查 JSON 结果，并在选定客机内运行可重复执行的脚本。
weight: 60
icon: fa-solid fa-gears
---

> [!NOTE]
> **Unreleased**：下文关于脚本符号链接及 provision 并发、节点数与超时上限的移除的变更需要包含源码提交 `27f17bb` 的构建，Barn 0.9.2 尚未包含这些行为。详见[未发布变更](/zh/docs/about/unreleased/)。

本指南介绍如何在无人值守脚本与 CI 流水线中调用 **Barn 0.9.2**。请始终以拥有该部署的普通 Unix 用户身份执行命令，并在每次调用时传入相同的 `-f <清单>` 与 `BARN_HOME`。

## 准备可预测的实验环境

建议将主机清单纳入版本控制，并将 `vm_image` 锁定为完整版本号（如 `vm_image: u24@20260926.0.0`），确保后续更新镜像目录不会意外改变流水线所使用的基础镜像。显式传入 `-f` 还能防止首次 `setup` 在遇到网段冲突时自动改写默认模板的子网。若使用自定义镜像仓库，请先执行 `barn update --repo URL` 激活其镜像目录，再向 `setup` 和 `up` 传入相同的 `--repo`。

在启动自动化流程前，先生成并校验配置文件：

```bash
mkdir -p ~/barn-lab
cd ~/barn-lab
barn init dual
# 编辑 barn.yml，锁定 vm_image 与节点规格。
barn version
barn validate -f barn.yml
barn plan -f barn.yml
barn setup -f barn.yml --dry-run
```

核对宿主变更计划并配置好免交互 `sudo` 凭据（或 `NOPASSWD` 策略）后，执行宿主准备并拉起环境：

```bash
barn setup -f barn.yml --yes
barn up -f barn.yml --json > up.json
```

`barn setup --yes` 用于自动确认宿主准备计划；而非交互模式下的 `barn up` 不会自动触发首次宿主准备，要求宿主依赖和私有网络已提前就绪。

## 结合退出码校验 JSON 结果

Barn 将结构化 JSON/YAML 结果输出到 `stdout`，将诊断信息输出到 `stderr`。需要注意的是，只要管理 SSH 就绪，`barn up` 就会返回**退出码 `0`**——即使附加数据盘、Virtio-9p 共享或节点间 SSH 存在功能限制（记录于 `nodes[].warnings`），或者自动重置了损坏的测试数据盘（记录于 `nodes[].repairs`）。因此自动化脚本应当同时校验退出码与 JSON 字段：

```bash {title="up-check.sh"}
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

当后续步骤要求客机完全就绪时，请勿在 `barn up` 中使用 `--no-wait`（`barn status --json` 仅读取已缓存的状态与警告，不会重新探测客机 SSH）。

### 错误退出码与专用报告结构

请结合[命令行退出码](../../reference/cli/#退出码)与各命令的 JSON 结构判断执行结果：

- **退出码 `2`（`usage`）**：首次运行缺少配置文件、参数非法或镜像别名未知。
- **退出码 `4`（`conflict`）**：清单发生需要显式处理的漂移（`reason: recreate_required` 或 `nodes_removed`），或等待部署锁超过 10 分钟（`reason: deployment_busy`）。
- **退出码 `5`（`partial`）**：多节点 `up` 或 `provision` 部分成功、部分失败——重试前请先检查 `nodes[]` 或 `results[]`。
- **专用报告格式**：
  - `barn doctor --json` 在宿主计算能力检查通过时即退出 `0`，即使 `class: network` 检查报错；若工作流依赖私网通信，请同时检查 `checks[]` 与 `barn network status --json`。
  - `barn ssh` 和 `barn exec` 直接透传远端命令的退出码（含 OpenSSH 连接失败的 `255`），并在 `--json` 模式下通过 `success`、`exit_code`、`stdout` 和 `stderr` 返回结果。

## 执行单条命令或批量脚本

在节点名称与远端命令之间始终使用 `--` 分隔，并将 Barn 自身的参数（如 `--json`、`--verbose`）放在 `--` 之前：

```bash
barn exec meta -- hostname
barn exec node-1 -- sh -c 'id; df -h /data'
barn exec meta --json -- uname -a > uname.json
```

调用 `barn exec` 时请将程序名与参数分开传递；若需使用管道、重定向或环境变量展开，请显式调用 `sh -c`（详见 [SSH 透传与命令补全](../../reference/cli/#ssh-透传与命令补全)）。

如需在多台运行中的 Linux 客机上批量执行巡检或初始化脚本，可先在宿主保存一份 Bash 脚本（普通文件或指向普通文件的符号链接，不超过 4 MiB）：

```bash {title="check-lab.sh"}
#!/usr/bin/env bash
set -euo pipefail
hostname
id
findmnt /data
test -d /data
```

通过 `barn provision` 在目标节点上运行：

```bash
barn provision --script ./check-lab.sh meta node-1
barn provision --script ./check-lab.sh --parallel 2 --timeout 5m --json > provision.json
```

省略节点选择器时，`provision` 会作用于部署中的全部节点（所有目标节点必须已处于运行状态）。Barn 会将校验后的脚本字节流直接通过 SSH 传给客机 Bash 执行，并记录脚本的 SHA-256 摘要，不在客机磁盘上落盘保存脚本文件。

- **并发与超时**：默认串行执行；`--parallel` 接受正整数，工作线程数不超过所选节点数。`--timeout` 限制整次操作时长，默认 `1h`，接受任意正时长。`--sudo` 通过客机免交互 `sudo -n` 执行。
- **输出截断与幂等性**：每个节点最多捕获 1 MiB `stdout` 与 1 MiB `stderr`（超出时标记 `stdout_truncated` / `stderr_truncated`）。由于部分失败不会回滚已执行成功的客机操作，请确保编写的脚本可安全重跑。
- **退出码规则**：目标节点部分成功、部分失败时退出 `5`；仅针对单个节点且远端返回大于 `0` 且非 `255` 的状态码时直接透传该状态码；其余全失败情况退出 `1`。

## 与 Pigsty 配合使用

Barn 与 [Pigsty](https://pigsty.cc/docs/) 原生共用同一套 Ansible YAML 清单格式。`barn init` 生成的模板仅定义虚拟机硬件拓扑，而 Pigsty 仓库中的 `pigsty.yml` 则包含完整的 PostgreSQL 集群与监控服务配置。先用 Barn 根据 `pigsty.yml` 拉起虚拟机：

```bash
barn validate -f pigsty.yml
barn plan -f pigsty.yml
barn up -f pigsty.yml
barn ssh
```

在 `barn up` 期间，Barn 会初始化客机管理员账号，并将部署私钥复制到 `admin_ip` 指定的控制节点上，使其能够直接通过固定私网 IP 免密连接集群内的其他节点（详见[安全与信任](../../about/security/)）。待 `barn up` 就绪后，登录控制节点即可按照 [Pigsty 文档](https://pigsty.cc/docs/)部署数据库服务。
