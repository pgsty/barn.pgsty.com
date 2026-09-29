---
title: 日常管理
description: 唯一 deployment 的正常生命周期：检查、访问、扩容、变更、停止与销毁。
weight: 20
icon: fa-solid fa-gears
aliases: [/docs/start/lifecycle/, /docs/start/provisioning/]
---

本教程描述 **Barn 0.9.0 发布候选**。发布与验收边界见[当前状态](../../about/status/)。

## 检查与访问

```bash
barn status
barn ssh meta
barn exec node-1 -- hostname
barn logs meta --source serial
```

应用状态默认位于 `~/.barn`（可由 `BARN_HOME` 覆盖），这些命令可在任意目录执行。
切换工作目录不会创建另一套 deployment。
Status 默认显示镜像和资源；`--verbose` 显示架构、加速器、SSH 端口和 PID，
TCG 在普通输出中也明确标记。异常节点不会隐藏其他节点的状态。
`barn up` 会在选中 VM 启动后，根据完整 applied deployment 重建默认 SSH 别名；因此
局部 `up` 不会删除未选中节点，可直接运行 `ssh meta`；如需手工重写，使用
`barn ssh-config --install`。
`plan`、`up`、`reload`、`recreate` 依次优先使用 `-f`、当前目录发现的 Inventory，
两者都没有时才回退到已应用规格；`validate` 始终需要文件。

再次执行 `up` 会重试未完成的客机初始化、原位更新旧脚本，健康 VM 无需重启。结果会列出
可选功能限制，JSON/YAML 提供 `nodes[].warnings` 与 `nodes[].repairs`。不可用的测试
数据文件系统可能被清空重建，包括持久盘，详见[数据盘说明](../../reference/configuration/#数据盘)。

## 停止与启动

```bash
barn stop
barn start
barn restart node-1
barn reload -f barn.yml       # 读取并检查配置、停止、收敛
```

`start` 启动已停止的 VM 并复查运行中 VM 的就绪状态；`start` 与 `restart` 都使用已应用
状态，并刷新 SSH 别名，包括重新分配的自动端口。`reload` 先读取 Inventory、检查配置变化与启动依赖，再停止选中节点
并执行完整的 `up` 路径。

`up`、`start`、`restart`、`reload`、`recreate` 还会刷新运行中 guest 的 Barn hosts
和控制节点 SSH 条目。`--no-wait` 跳过就绪检查、客机恢复与 guest 刷新，后续运行 `up` 补齐。

## 变更 deployment

```bash
barn plan
barn up                         # 创建/启动选中节点，并安装 SSH 别名
barn recreate node-1            # 应用某个节点的 VM 定义变化
```

`plan` 规划 Catalog 镜像时无需先准备宿主，展示镜像、资源总量、变更原因与磁盘影响；
规划导入的 `local-*` 镜像还会校验缓存，需要 `qemu-img`。CPU/内存等定义
变化仍通过 recreate 应用，会替换根盘与非持久数据盘，持久盘保留。若多个节点同时
变化，局部重建受未选节点影响时会提前拒绝，并列出所需节点。

`recreate` 与 `destroy` 在终端上展示磁盘范围并要求输入确认词；`--force` 跳过提示，
无终端时必须显式传入。

| 字段 | 含义 | 操作 |
|---|---|---|
| `create` | 配置有、状态无 | `barn up` |
| `recreate` | VM 定义改变 | `barn recreate <node>` |
| `missing` | 状态有、配置无 | 恢复配置，或显式 destroy |

删除 YAML 永远不会删除 VM。未消费的 Pigsty 变更得到 `action:none`；命名与
node-admin 字段虽然不以 `vm_` 开头，仍会被消费。成功的 recreate 也会刷新完整 SSH
fragment。

## 并发命令（0.9 候选版）

修改 deployment 的命令会等待其他 Barn 操作释放锁，最长十分钟，同时受命令自身
超时限制。等待信息会显示持锁命令、PID 与开始时间。等待超时返回退出码 4，JSON
为 `error: conflict`、`reason: deployment_busy`；持锁操作完成后再重试。
持锁进程退出时锁自动释放；不要通过删除锁文件打断仍在运行的操作。

`status`、`ssh`、`exec`、`ssh-config`，以及 `hosts` 读取部署状态的步骤不会排队等待
这把锁，而是读取已写入的状态。其他命令持锁时，`status` 会附带 `note`，并且不会
收敛该命令正在进行的状态转换。因此尚在启动中的 VM 可能暂时无法 SSH。

中断恢复见[故障排查](../troubleshooting/#命令被中断)，脚本处理结果见
[自动化](../automation/)。

## 销毁

```bash
barn destroy node-3
barn destroy
barn destroy --delete-persistent
barn destroy --purge
barn purge                         # 无需确认，处置整套实验室
```

`--delete-persistent` 与 `--purge` 只适用于整体销毁，不能和节点选择器一起使用。
`--purge` 删除持久盘、密钥和 deployment 状态，但保留镜像。节点级 destroy 会刷新
剩余节点的 SSH fragment，整体 destroy 会移除默认 Barn SSH 集成。宿主网络单独卸载，
仍有 VM 挂接时会拒绝。

`barn purge` 是一次性实验室的简洁路径，等价于
对已有部署执行 `destroy --force --purge`。它不接受节点选择器，没有 Deployment 时
幂等成功，保留镜像缓存与
宿主网络，同时不会绕过进程身份、属主和路径完整性检查。

**0.9 候选版：**没有 deployment 时，普通 `destroy` 直接成功。状态已删除但还有
归属明确的持久盘时，使用 `purge`；`destroy --delete-persistent` 或 `destroy --purge`
会提示改用该命令。旧的 `rm` 别名已移除，必须写出 `purge`。

```bash
barn network uninstall --yes
```

镜像选择、镜像站与缓存清理见[镜像仓库](../images/)；彻底移除宿主状态见
[卸载与清理环境](../uninstall/)。
