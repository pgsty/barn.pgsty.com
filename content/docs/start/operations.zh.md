---
title: 日常管理
description: 唯一部署的正常生命周期：检查、访问、扩容、变更、停止与销毁。
weight: 30
icon: fa-solid fa-gears
aliases: [/docs/start/lifecycle/, /docs/start/provisioning/]
---

本页介绍 **Barn 0.9.1** 的 Linux 环境操作。Mac 虚拟机请看
[macOS 日常管理](../macos/#日常管理)。

## 检查与访问

```bash
barn status
barn ssh meta
barn exec node-1 -- hostname
barn logs meta --source serial
```

Barn 默认将已有部署的记录保存在 `~/.barn`，可由 `BARN_HOME` 覆盖。
上面的命令使用这些已应用状态，可在任意目录执行。切换目录不会创建另一套部署。

状态默认显示镜像和资源。`--verbose` 还显示架构、加速器、SSH 端口和 PID。
普通输出也标记 TCG；异常节点不会隐藏其他节点的状态。
选中的虚拟机启动后，`barn up` 会根据完整已应用部署重建 SSH 别名。
局部 `up` 会保留未选中节点的别名，因此 `ssh meta` 等连接仍然可用。
如需手工重写别名，使用 `barn ssh-config --install`。

`plan`、`up`、`reload`、`recreate` 优先使用显式 `-f`，其次查找当前目录的清单。
自动查找不到文件时，才回退到已应用规格。`validate` 始终需要文件。
查找顺序为 `barn.yml`、`barn.yaml`、`pigsty.yml`、`pigsty.yaml`，不会向父目录查找。
如果首个找到的文件格式错误，命令直接失败，不再尝试其他文件或已应用状态。
两种配置同时存在时，通过 `-f pigsty.yml` 明确选择 Pigsty 文件。

再次执行 `up` 会重试未完成的客机初始化、原位更新旧脚本，健康虚拟机无需重启。结果会列出
可选功能限制，JSON/YAML 提供 `nodes[].warnings` 与 `nodes[].repairs`。无法识别或确认损坏的测试数据文件系统可能被清空重建，包括持久盘，详见[数据盘说明](../../reference/configuration/#数据盘)。

## 停止与启动

```bash
barn stop
barn start
barn restart node-1
barn reload -f barn.yml       # 读取并检查配置、停止、收敛
```

`start` 启动已停止的虚拟机，并复查运行中虚拟机的就绪状态。`start` 与 `restart` 都使用已应用状态。它们还会刷新 SSH 别名，包括重新分配的自动端口。停止选中节点前，`reload` 会读取清单，检查配置变化与启动依赖。之后，它执行完整的 `up` 流程。

`up`、`start`、`restart`、`reload`、`recreate` 还会刷新运行中客机的 Barn hosts
和控制节点 SSH 条目。`--no-wait` 跳过就绪检查、客机恢复与客机刷新。后续运行 `up` 完成这些步骤。

## 变更部署

```bash
barn plan
barn up                         # 创建/启动选中节点，并安装 SSH 别名
barn recreate node-1            # 应用某个节点的 VM 定义变化
```

`plan` 可在宿主准备前展示镜像目录中的镜像、资源总量、变更原因与磁盘影响。
规划导入的 `local-*` 镜像还会校验缓存，因此需要 `qemu-img`。

CPU、内存等定义变化需要 recreate，重建会替换根盘与非持久数据盘，保留兼容的持久盘。
如果未选中节点的配置变化阻碍本次重建，Barn 会在删除磁盘前拒绝操作，并列出需要处理的节点。

`recreate` 与 `destroy` 在终端上展示磁盘范围，再要求输入确认词。`--force` 跳过提示。无终端时，必须显式传入此参数。

| 字段 | 含义 | 操作 |
|---|---|---|
| `create` | 配置有、状态无 | `barn up` |
| `recreate` | 虚拟机定义改变 | `barn recreate <node>` |
| `missing` | 状态有、配置无 | 恢复配置，或显式 destroy |

删除 YAML 不会删除虚拟机。Barn 不使用的 Pigsty 字段变化会得到 `action:none`。命名与 node-admin 字段虽然不以 `vm_` 开头，Barn 仍会使用这些字段。成功的 recreate 也会刷新完整 SSH 配置片段。

## 并发命令

修改部署的命令（包括 `provision`）会等待其他 Barn 操作释放锁，最长十分钟。命令自身的超时限制可能缩短等待时间。等待信息会显示持锁命令、PID 与开始时间。等待超时返回退出码 4，JSON
为 `error: conflict`、`reason: deployment_busy`。持锁操作完成后再重试。持锁进程退出时，锁自动释放。不要通过删除锁文件打断仍在运行的操作。

`status`、`ssh`、`exec`、`ssh-config`，以及 `hosts` 读取部署状态的步骤不会排队等待
这把锁，而是读取已写入的状态。其他命令持锁时，`status` 会附带 `note`。它不会收敛该命令尚未完成的状态转换。因此尚在启动中的虚拟机可能暂时无法 SSH。

中断恢复见[故障排查](../troubleshooting/#命令被中断)，脚本处理结果见
[自动化](../automation/)。

## 销毁

按要删除的范围选择一条命令，不要依次执行全部示例：

```bash
barn destroy node-3
barn destroy
barn destroy --delete-persistent
barn destroy --purge
barn purge                         # 无需确认，处置整套实验室
```

`--delete-persistent` 与 `--purge` 只适用于整体销毁，不能和节点选择器一起使用。
`--purge` 删除持久盘、密钥和部署状态，但保留镜像。节点级 destroy 会刷新
剩余节点的 SSH 配置片段，整体 destroy 会移除默认 Barn SSH 集成。宿主网络单独卸载，
仍有虚拟机挂接时会拒绝。

`barn purge` 会删除实验环境，无需确认。对已有部署，它等价于 `destroy --force --purge`。它不接受节点选择器。没有部署时，它仍会返回成功，也可清除归属明确的保留盘。它保留镜像缓存与宿主网络，并继续检查进程身份、属主和路径完整性。

没有部署时，普通 `destroy` 直接成功。状态已删除但还有
归属明确的持久盘时，使用 `purge`。`destroy --delete-persistent` 或 `destroy --purge` 会提示改用该命令。旧的 `rm` 别名已移除，必须写出 `purge`。

```bash
barn network uninstall --yes
```

镜像选择、镜像站与缓存清理见[镜像仓库](../images/)；彻底移除宿主状态见
[卸载与清理环境](../uninstall/)。
