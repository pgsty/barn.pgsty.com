---
title: Linux 快速上手
linkTitle: Linux 快速上手
description: 启动 Ubuntu 虚拟机，通过 SSH 连接，再用同一份主机清单扩展为固定 IP 的 Linux 实验环境。
weight: 10
icon: fa-brands fa-linux
aliases: [/docs/start/lab/, /docs/start/pigsty/, /docs/features/]
---

先在 Mac 或 Linux 电脑上创建一台 Ubuntu 24.04 虚拟机，再按需增加节点。
运行 Barn 的电脑称为宿主，虚拟机中的操作系统称为客机。
macOS 客机请使用独立的 [Mac 教程](../macos/)。

## 开始之前 {#install}

[安装 Barn 0.9.1](../installation/)，为客机预留至少 4 GiB 内存，并为宿主保留余量。
在终端中以普通用户执行以下命令。Barn 可以准备 QEMU 和私有网络，宿主变更可能需要 sudo。

首次准备要求标准输入连接交互终端，CI 等非交互场景请使用[自动化指南](../automation/)。

## 启动并连接

```bash
mkdir -p ~/barn-lab && cd ~/barn-lab
barn up
barn ssh
```

定义实验环境节点的 YAML 配置文件称为清单。
首次使用，且既没有配置文件也没有已有部署时，`up` 会生成只有一个 `meta` 节点的 `barn.yml`。
它先准备宿主依赖，再下载并校验镜像，最后等待 SSH 就绪。

启动成功后会显示连接命令：

```text
  ✓  1 node ready
connect:   barn ssh meta
```

此时你已通过密钥以 `dba` 登录客机，可以使用免密 sudo。
执行 `exit` 返回宿主后，再运行其他 Barn 命令。

| 默认配置 | 值 |
|---|---|
| 节点与地址 | `meta`，`10.10.10.10` |
| 镜像 | Ubuntu 24.04，`u24:stable`，与宿主相同的架构 |
| CPU 与内存 | 2 vCPU、4 GiB |
| 磁盘 | 64 GiB 根盘，挂载到 `/data` 的 128 GiB 测试数据盘 |

磁盘文件随写入增长。如果全新、未编辑的默认模板遇到子网冲突，setup 可以选择其他私有 `/24`。实际地址以生成后的 `barn.yml` 和 `barn status` 为准。

Barn 在选定的 `BARN_HOME`（默认 `~/.barn`）中管理一套 Linux 部署。
切换工作目录不会新建部署。当前目录没有配置文件时，`up` 会继续已有部署。用 `barn status` 查看现有虚拟机。

## 查看并使用虚拟机

```bash
barn status
barn exec meta -- hostname
barn exec meta -- df -h / /data
barn ssh meta
```

`status` 展示虚拟机进程状态。`up` 等待管理 SSH 可用，并报告数据盘、私网等客机功能的
限制。修正问题或中断初始化后，再次执行 `barn up` 继续。健康虚拟机保持运行。
中国地区可使用 `barn up --mirror` 优先从中国官方仓库下载镜像。

> [!WARNING]
> 数据盘用于可丢弃的测试数据。客机初始化时，Barn 可能清空重建无法识别或确认损坏的
> 文件系统，包括持久盘。请将有价值的数据另行保存。[存储与恢复说明](../storage/)
> 解释了保留磁盘与保护磁盘内容之间的区别。

## 首次启动前定制配置

以下步骤是默认启动的替代方案：先定制配置，再首次启动。
如果已经按上文启动实验环境，请跳过这组命令，按下文说明修改已有配置。

```bash
barn init
# 编辑 barn.yml。
barn validate
barn plan
barn up
```

以下是一份完整的单节点配置：

```yaml
all:
  vars:
    admin_ip: 10.10.10.10
    vm_image: u24
    vm_cpu: 2
    vm_mem: 4GiB
  children:
    nodes:
      hosts:
        10.10.10.10: { nodename: meta }
```

`barn init dual`、`trio`、`full` 分别生成双节点、三节点和四节点配置。
`barn init full -c 10.20.30.0/24` 指定其他子网。除非显式使用 `--force`，否则 Barn 会保留已有文件。配置校验和镜像目录规划不要求先准备宿主。全部字段见[配置参考](../../reference/configuration/)。

## 添加更多节点

在现有 `barn.yml` 的同一个 `hosts` 下补充节点条目：

```yaml
        10.10.10.10: { nodename: meta }
        10.10.10.11: { nodename: node-1 }
        10.10.10.12: { nodename: node-2 }
        10.10.10.13: { nodename: node-3 }
```

沿用实际网段和其他已有设置。这只是配置片段，不要用它替换整个文件。
四节点环境按默认规格需要 16 GiB 客机内存。

```bash
barn plan
barn up
```

仅有这些新增行时，计划会列出三台新节点。Barn 创建它们时不重启 `meta`。

修改已有节点的 CPU、内存或其他虚拟机定义，需要执行 `barn recreate <node>`，该操作会替换根盘。
从 YAML 删除节点条目会保留虚拟机，直到你执行 `barn destroy <node>`。

## 停止、恢复与清理

```bash
barn stop
barn start
```

两条命令都会保留磁盘。环境不再需要时，执行 `barn destroy` 并输入 `destroy` 确认。
它会删除根盘与非持久数据盘，保留持久盘、镜像缓存、密钥和宿主网络。
[彻底清理](../uninstall/)有独立的操作步骤。

## 接下来

- [日常管理](../operations/)：连接、日志、重启、配置变更与删除。
- [存储与访问](../storage/)：传输文件，访问客机服务。
- [镜像](../images/)：选择 Debian、Rocky Linux、Ubuntu 或本地镜像。
- [自动化](../automation/)：`setup --yes`、JSON 结果、客机脚本，以及与 Pigsty 共用 `pigsty.yml`。

Barn 准备虚拟机与访问环境。通过 Pigsty 另行部署 PostgreSQL 等服务。内置模板描述虚拟机拓扑，不包含完整的服务配置。
