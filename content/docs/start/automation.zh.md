---
title: 自动化与客机脚本
linkTitle: 自动化
description: 准备无人值守实验环境，检查 JSON 结果，并在选定客机内运行可重复执行的脚本。
weight: 60
icon: fa-solid fa-gears
---

本指南介绍如何在无人值守脚本与 CI 流水线中调用 Barn。请始终以拥有该部署的普通 Unix 用户身份执行命令，并在每次调用时传入相同的 `-f <清单>` 与 `BARN_HOME`。

## 准备可预测的实验环境 {#prepare-a-predictable-lab}

建议将主机清单纳入版本控制，并将 `vm_image` 锁定为完整版本号（如 `vm_image: u24@20261017.0.1`），确保后续更新镜像目录不会意外改变流水线所使用的基础镜像。显式传入 `-f` 还能防止首次 `setup` 在遇到网段冲突时自动改写默认模板的子网。若使用自定义镜像仓库，请先执行 `barn update --repo URL` 激活其镜像目录，再向 `setup` 和 `up` 传入相同的 `--repo`。

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

生成新清单时，`barn init [模板] --image <引用>` 将镜像引用写入 `all.vars.vm_image`，让所有生成节点继承同一个镜像。引用可以是目录别名（`el9`）、频道（`u24:stable`）或版本选择器（`u24@20261017.0.1`）。`barn setup [模板] --image <引用>` 也支持生成时选镜像，但遇到已有清单时会拒绝该生成参数。

`main` 新增 `--image/-I`、`--arch/-A` 的统一用法：`barn init full -I u24 -A amd64` 将两项选择保存到新清单；`validate`、`plan`、`up`、`reload`、`recreate` 和 `resize` 的同名参数则只覆盖本次期望配置。例如 `barn plan -f barn.yml -I u24 -A arm64 --json`，执行时传入相同的覆盖参数。`setup` 的 `-I/-A` 仍只适用于生成模板。这些扩展尚未包含在 1.0.0 中，请检查当前二进制的 `--help`。

未指定架构时使用清单的 `vm_arch`，清单也未设置时跟随宿主；`-A native` 可以覆盖清单，恢复宿主架构。已有 VM 改镜像或架构需要 `recreate`。长期使用的 CI 配置宜保存 `vm_image`、`vm_arch` 与精确镜像版本，详见[配置参考](../../reference/configuration/#image-and-architecture)。

`barn setup --yes` 会直接接受宿主准备计划，不再询问。在终端中，`up`、`start`、`restart` 与 `reload` 安装软件包或 Barn 网络前会展示同样的计划并询问一次；没有终端时它们只报告缺少的条件，因此请先执行 `barn setup --yes`。

## 结合退出码校验 JSON 结果 {#validate-json-output-alongside-the-exit-code}

Barn 将结构化 JSON/YAML 结果输出到 `stdout`，将诊断信息输出到 `stderr`。需要注意的是，只要管理 SSH 就绪，`barn up` 就会返回 **退出码 `0`**——即使附加数据盘、Virtio-9p 共享或节点间 SSH 存在功能限制（记录于 `nodes[].warnings`），或者自动重置了损坏的测试数据盘（记录于 `nodes[].repairs`）。因此自动化脚本应当同时校验退出码与 JSON 字段：

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

### 错误退出码与专用报告结构 {#exit-codes-and-command-specific-payloads}

请结合[命令行退出码](../../reference/cli/#exit-codes)与各命令的 JSON 结构判断执行结果：

- **退出码 `2`（`usage`）**：首次运行缺少配置文件、参数非法、镜像别名未知，或标准输入不是终端时执行 `destroy`/`recreate` 却未传 `--yes`（`purge` 则直接执行，不会询问）。
- **退出码 `4`（`conflict`）**：清单发生需要显式处理的漂移（`reason: recreate_required` 或 `nodes_removed`），`recreate` 预检期间已应用状态发生变化（`reason: deployment_changed`），或等待部署锁超过 10 分钟（`reason: deployment_busy`）。
- **退出码 `5`（`partial`）**：多节点 `up` 或 `provision` 部分成功、部分失败——重试前请先检查 `nodes[]` 或 `results[]`。
- **退出码 `7`（`integrity`）**：摘要、签名或身份校验失败，包括目录签名或签名 revision 校验失败（`reason: catalog_signature` 或 `catalog_equivocation`）。
- **专用报告格式**：
  - `barn doctor --json` 在宿主计算能力检查通过时即退出 `0`，即使 `class: network` 检查报错；若工作流依赖私网通信，请同时检查 `checks[]` 与 `barn network status --json`。
  - `barn ssh` 和 `barn exec` 直接透传远端命令的退出码（含 OpenSSH 连接失败的 `255`），并在 `--json` 模式下通过 `success`、`exit_code`、`stdout` 和 `stderr` 返回结果。
  - 未传 `--yes` 时，如果标准输入不是终端或输出为 `--json`/`--yaml`，`network` 与 `hosts` 的 `install`/`uninstall` 只输出计划并退出 `0`；请检查结果中的 `applied`，或传入 `--yes`。

## 执行单条命令或批量脚本 {#run-single-commands-or-batch-scripts}

在节点名称与远端命令之间始终使用 `--` 分隔，并将 Barn 自身的参数（如 `--json`、`--verbose`）放在 `--` 之前：

```bash
barn exec meta -- hostname
barn exec node-1 -- sh -c 'id; df -h /data'
barn exec meta --json -- uname -a > uname.json
```

调用 `barn exec` 时请将程序名与参数分开传递；若需使用管道、重定向或环境变量展开，请显式调用 `sh -c`（详见 [SSH 透传与命令补全](../../reference/cli/#ssh-passthrough-and-completion)）。

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

## 与 Pigsty 配合使用 {#pair-the-lab-with-pigsty}

Barn 与 [Pigsty](https://pigsty.cc/docs/) 原生共用同一套 Ansible YAML 清单格式。`barn init` 生成的模板仅定义虚拟机硬件拓扑，而 Pigsty 仓库中的 `pigsty.yml` 则包含完整的 PostgreSQL 集群与监控服务配置。先用 Barn 根据 `pigsty.yml` 拉起虚拟机：

```bash
barn validate -f pigsty.yml
barn plan -f pigsty.yml
barn up -f pigsty.yml
barn ssh
```

在 `barn up` 期间，Barn 会初始化客机管理员账号，并将部署私钥复制到 `admin_ip` 指定的控制节点上，使其能够直接通过固定私网 IP 免密连接集群内的其他节点（详见[安全与信任](../../about/security/)）。待 `barn up` 就绪后，登录控制节点即可按照 [Pigsty 文档](https://pigsty.cc/docs/)部署数据库服务。
