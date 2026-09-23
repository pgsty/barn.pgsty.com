---
title: 日常管理
description: 唯一 deployment 的正常生命周期：检查、访问、扩容、变更、停止与销毁。
weight: 20
icon: fa-solid fa-gears
aliases: [/docs/start/lifecycle/, /docs/start/provisioning/]
---

## 检查与访问

```bash
farrow status
farrow ssh meta
farrow exec node-1 -- hostname
farrow logs meta --source serial
```

应用状态位于 `~/.farrow`，这些命令可在任意目录执行。
Status 默认显示镜像和资源；`--verbose` 显示架构、加速器、SSH 端口和 PID，
TCG 在普通输出中也明确标记。异常节点不会隐藏其他节点的状态。
`farrow up` 会在选中 VM 启动后，根据完整 applied deployment 重建默认 SSH 别名；因此
局部 `up` 不会删除未选中节点，可直接运行 `ssh meta`；如需手工重写，使用
`farrow ssh-config --install`。
`plan`、`up`、`reload`、`recreate` 依次优先使用 `-f`、当前目录发现的 Inventory，
两者都没有时才回退到已应用规格；`validate` 始终需要文件。

再次执行 `up` 会重试未完成的客机初始化、原位更新旧脚本，健康 VM 无需重启。结果会列出
可选功能限制，JSON/YAML 提供 `nodes[].warnings` 与 `nodes[].repairs`。不可用的测试
数据文件系统可能被清空重建，包括持久盘，详见[数据盘说明](../../reference/configuration/#数据盘)。

## 停止与启动

```bash
farrow stop
farrow start
farrow restart node-1
farrow reload -f farrow.yml       # 停止、重新读配置、收敛
```

`start` 启动已停止的 VM 并复查运行中 VM 的就绪状态；`start` 与 `restart` 都使用已应用
状态，并刷新 SSH 别名，包括重新分配的自动端口。`reload` 先读取 Inventory、检查配置变化与启动依赖，再停止选中节点
并执行完整的 `up` 路径。

`up`、`start`、`restart`、`reload`、`recreate` 还会刷新运行中 guest 的 Farrow hosts
和控制节点 SSH 条目。`--no-wait` 跳过就绪检查、客机恢复与 guest 刷新，后续运行 `up` 补齐。

## 变更 deployment

```bash
farrow plan
farrow up                         # 创建/启动选中节点，并安装 SSH 别名
farrow recreate node-1            # 应用某个节点的 VM 定义变化
```

`plan` 无需先准备宿主，展示镜像、资源总量、变更原因与磁盘影响。CPU/内存等定义
变化仍通过 recreate 应用，会替换根盘与非持久数据盘，持久盘保留。若多个节点同时
变化，局部重建受未选节点影响时会提前拒绝，并列出所需节点。

`recreate` 与 `destroy` 在终端上展示磁盘范围并要求输入确认词；脚本可传 `--force`。

| 字段 | 含义 | 操作 |
|---|---|---|
| `create` | 配置有、状态无 | `farrow up` |
| `recreate` | VM 定义改变 | `farrow recreate <node>` |
| `missing` | 状态有、配置无 | 恢复配置，或显式 destroy |

删除 YAML 永远不会删除 VM。未消费的 Pigsty 变更得到 `action:none`；命名与
node-admin 字段虽然不以 `vm_` 开头，仍会被消费。成功的 recreate 也会刷新完整 SSH
fragment。

## 销毁

```bash
farrow destroy node-3
farrow destroy
farrow destroy --delete-persistent
farrow destroy --purge
farrow purge                         # 无需确认，处置整套实验室
```

`--delete-persistent` 与 `--purge` 只适用于整体销毁，不能和节点选择器一起使用。
`--purge` 删除持久盘、密钥和 deployment 状态，但保留镜像。节点级 destroy 会刷新
剩余节点的 SSH fragment，整体 destroy 会移除默认 Farrow SSH 集成。宿主网络单独卸载，仍有
VM 挂接时会拒绝：

`farrow purge` 是一次性实验室的简洁路径，等价于
`destroy --force --purge`。它不接受节点选择器，没有 Deployment 时幂等成功，保留镜像缓存与
宿主网络，同时不会绕过进程身份、属主和路径完整性检查。

```bash
farrow network uninstall --yes
```

镜像选择、镜像站与缓存清理见[镜像仓库](../images/)；彻底移除宿主状态见
[卸载与清理环境](../uninstall/)。
