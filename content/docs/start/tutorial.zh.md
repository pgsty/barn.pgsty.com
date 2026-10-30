---
title: Linux 快速上手
linkTitle: Linux 快速上手
description: 启动 Ubuntu 虚拟机，通过 SSH 连接，再用同一份主机清单扩展为固定 IP 的 Linux 实验环境。
weight: 10
icon: fa-brands fa-linux
aliases: [/docs/start/lab/, /docs/start/pigsty/, /docs/features/]
---

在 Mac 或 Linux 宿主上创建一台 Ubuntu 24.04 虚拟机，通过 SSH 登录，再用同一份 YAML 清单扩展为多节点固定 IP 实验环境。如需在 Apple Silicon 上运行 macOS 客机，请阅读 [macOS 虚拟机教程](../macos/)。

## 开始之前 {#install}

[安装 Barn 0.9.2](../installation/)，并确保宿主至少预留 4 GiB 可用内存供客机使用。请在交互式终端中以普通用户执行以下命令——Barn 会自动配置 QEMU 与私有网络，仅在需要修改宿主系统配置时提示输入 `sudo` 密码（CI 等非交互场景请参阅[自动化指南](../automation/)）。

## 启动并连接

```bash
mkdir -p ~/barn-lab && cd ~/barn-lab
barn up
barn ssh
```

首次运行且既没有配置文件也没有已有部署时，`barn up` 会自动生成包含单个 `meta` 节点的 `barn.yml`，准备宿主依赖，下载并校验基础镜像，随后等待 SSH 就绪：

```text
  ✓  1 node ready
connect:   barn ssh meta
```

`barn ssh` 会使用部署密钥以管理员用户 `dba` 登录客机，支持免密 `sudo`。输入 `exit` 退回宿主终端后，即可继续运行其他 `barn` 命令。

| 默认配置 | 值 |
|---|---|
| 节点与地址 | `meta`（`10.10.10.10`） |
| 镜像 | Ubuntu 24.04（`u24:stable`，与宿主架构一致） |
| CPU 与内存 | 2 vCPU、4 GiB |
| 磁盘 | 64 GiB 根盘写时复制层，以及挂载到 `/data` 的 128 GiB 测试数据盘 |

两块磁盘均为按需增长的 `qcow2` 稀疏文件。如果默认网段 `10.10.10.0/24` 与本机现有路由冲突，首次 `setup` 会为未修改过的默认模板自动选择另一个空闲的私有 `/24` 网段——实际分配的地址以生成的 `barn.yml` 和 `barn status` 为准。

> [!NOTE]
> **每个 `BARN_HOME` 对应唯一一套 Linux 部署**：Barn 默认将 Linux 实验环境的状态保存在 `BARN_HOME`（即 `~/.barn`）下。切换工作目录不会创建第二套实验环境；在没有清单文件的目录中运行 `barn up` 会直接恢复现有部署。设计背景详见[一套部署，没有项目概念](/zh/blog/design/one-deployment-no-projects/)。

## 查看并使用虚拟机

```bash
barn status
barn exec meta -- hostname
barn exec meta -- df -h / /data
barn ssh meta
```

`barn status` 用于查看虚拟机进程状态，`barn up` 则会确认管理 SSH 可用，并报告数据盘、私网等客机阶段是否存在功能限制。修复问题或中断初始化后，重新运行 `barn up` 即可继续收敛，已处于健康状态的虚拟机不会重启。中国大陆网络环境可使用 `barn up --mirror` 从中国官方镜像站拉取镜像。

> [!WARNING]
> 数据盘属于可丢弃的测试存储。在客机恢复期间，`barn up` 可能会重新格式化无法识别或确认损坏的文件系统（包括持久数据盘）。重要数据请保存在宿主上，磁盘保留与恢复边界详见[存储与访问](../storage/)。

## 首次启动前定制配置

如果希望在首次创建虚拟机前自定义拓扑、网段或操作系统镜像，可以先生成并编辑清单：

1. 生成初始配置文件（`barn init dual`、`trio`、`full` 分别生成 2、3、4 节点模板，`-c 10.20.30.0/24` 可指定网段，`--force` 覆盖已有文件）：

   ```bash
   barn init
   ```

2. 编辑 `barn.yml`，调整镜像或硬件资源：

   ```yaml {title="barn.yml"}
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

3. 校验 YAML 语法、预览变更计划并启动环境：

   ```bash
   barn validate
   barn plan
   barn up
   ```
{.steps}

`barn validate` 和 `barn plan` 可在未安装 QEMU 或宿主网络前直接运行。完整配置字段见[配置参考](../../reference/configuration/)。

## 扩容为多节点环境

要将现有的单节点环境扩展为四节点集群（按默认每节点 4 GiB 计算共需 16 GiB 客机内存），只需在 `barn.yml` 的 `all.children.nodes.hosts` 下追加新节点：

```yaml {title="barn.yml"}
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
        10.10.10.11: { nodename: node-1 }
        10.10.10.12: { nodename: node-2 }
        10.10.10.13: { nodename: node-3 }
```

预览差异并拉起新增节点：

```bash
barn plan
barn up
```

`barn plan` 会列出 3 个 `create` 动作，随后 `barn up` 会在不重启 `meta` 的前提下创建 `node-1` 至 `node-3`。

如果修改了已有节点的 CPU、内存或镜像，需执行 `barn recreate <node>` 使其生效（这会替换该节点的根盘）。从 `barn.yml` 中删除节点条目不会自动销毁虚拟机，需显式运行 `barn destroy <node>`。

## 停止、恢复与清理

```bash
barn stop
barn start
```

`stop` 与 `start` 都会保留虚拟机磁盘。不再需要实验环境时，运行 `barn destroy` 并输入 `destroy` 确认——Barn 会删除虚拟机及其根盘与非持久数据盘，同时保留持久数据盘、镜像缓存、密钥和宿主网络。如需彻底移除所有残留文件，请参阅[卸载与清理](../uninstall/)。

## 接下来

- [日常管理](../operations/) — 查看日志、重启节点、应用配置变更与销毁虚拟机。
- [存储与访问](../storage/) — 配置持久数据盘、通过 OpenSSH 传输文件并访问客机端口。
- [镜像仓库](../images/) — 选择 Debian、Rocky Linux、Ubuntu 或导入本地 `qcow2` 镜像。
- [自动化](../automation/) — 无人值守 `setup --yes`、解析 `--json` 输出、执行客机脚本，以及与 Pigsty 共用 `pigsty.yml`。
{.cards}
