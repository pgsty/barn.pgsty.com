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

[安装 Barn](../installation/)，并确保宿主至少预留 4 GiB 可用内存供客机使用。请在交互式终端中以普通用户执行下面的命令：Barn 改动宿主前会询问一次，只有需要管理员权限的步骤才会提示输入 `sudo` 密码。CI 等无人值守场景请参阅[自动化指南](../automation/)。在中国大陆，可以在首次 `barn up` 时加上 `--mirror`，从中国官方仓库 `repo.pigsty.cc` 下载镜像。

## 首次启动前定制配置 {#customize}

默认实验环境只有一个 Ubuntu 节点，架构跟随宿主：Apple Silicon 为 `arm64`，Intel/AMD 为 `amd64`。日常使用无需指定架构；跨架构选择与覆盖优先级见[镜像与架构配置](../../reference/configuration/#image-and-architecture)。保持默认即可直接跳到[启动并连接](#start)。如果希望先自定义拓扑、网段或操作系统镜像，请在首次 `barn up` 之前生成并编辑清单：

1. 生成初始配置文件（`dual`、`trio`、`full` 分别生成 2、3、4 节点模板，`-c 10.20.30.0/24` 指定网段，`--image el9` 为所有节点写入同一个镜像）：

   ```bash
   mkdir -p ~/barn-lab && cd ~/barn-lab
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

3. 校验 YAML 并预览变更计划：

   ```bash
   barn validate
   barn plan
   ```
{.steps}

`barn validate` 和 `barn plan` 无需安装 QEMU 或配置宿主网络即可运行，下一节的 `barn up` 会直接使用这份 `barn.yml`。完整配置字段见[配置参考](../../reference/configuration/)。

## 启动并连接 {#start}

```bash
mkdir -p ~/barn-lab && cd ~/barn-lab
barn up
```

首次运行且既没有配置文件也没有已有部署时，`barn up` 会在改动任何东西之前打印一份简短的准备计划，只列出适用的行：`install` 列出缺少的软件包（QEMU、UEFI 固件、OpenSSH）及所用的包管理器，`network` 给出要准备的固定 IP 网段，`config` 给出将要写入的单节点 `barn.yml`，`sudo` 说明哪些步骤需要 root 权限。在已经装有 QEMU 的宿主上，计划如下：

```text
  network       prepare 10.10.10.0/24
  config        create /home/alice/barn-lab/barn.yml
  sudo          network (root-owned barn0 bridge)
Continue with this setup? [Y/n]
```

确认一次后，`sudo` 可能会要求输入密码。随后 Barn 会下载并校验基础镜像，等待 SSH 就绪：

```text
  ✓  1 node ready
connect:   barn ssh meta
```

如果 `barn up` 报错退出，先运行 `barn doctor` 检查宿主，再用 `barn logs meta` 查看客机控制台输出，修复问题后重新运行 `barn up`。常见故障见[故障排查](../troubleshooting/)。

登录客机：

```bash
barn ssh
```

`barn ssh` 会使用部署密钥以管理员用户 `dba` 登录客机，支持免密 `sudo`。`barn up` 同时会安装 SSH 别名，所以直接运行 `ssh meta` 也能登录。输入 `exit` 退回宿主终端，后面的命令都在宿主上执行。

| 默认配置 | 值 |
|---|---|
| 节点与地址 | `meta`（`10.10.10.10`） |
| 镜像 | Ubuntu 24.04（`u24:stable`，与宿主架构一致） |
| CPU 与内存 | 2 vCPU、4 GiB |
| 磁盘 | 64 GiB 根盘写时复制层，以及挂载到 `/data` 的 128 GiB 测试数据盘 |

两块磁盘均为按需增长的 `qcow2` 稀疏文件。如果默认网段 `10.10.10.0/24` 与本机现有路由冲突，首次 `setup` 会为未修改过的默认模板自动选择另一个空闲的私有 `/24` 网段——实际分配的地址以生成的 `barn.yml` 和 `barn status` 为准。

> [!NOTE]
> **每个 `BARN_HOME` 对应唯一一套 Linux 部署**：Barn 默认将 Linux 实验环境的状态保存在 `BARN_HOME`（即 `~/.barn`）下。切换工作目录不会创建第二套实验环境；在没有清单文件的目录中运行 `barn up` 会直接恢复现有部署。设计背景详见[一套部署，没有项目概念](/zh/blog/design/one-deployment-no-projects/)。

## 查看并使用虚拟机 {#inspect}

```bash
barn status
```

```text
NAME  STATE    ADDRESS      IMAGE             CPU   MEMORY
meta  running  10.10.10.10  u24@20261017.0.1    2  4.0 GiB
```

`barn status` 列出每个节点记录的状态、固定地址、镜像版本与规格。在宿主上执行客机命令时，用 `--` 隔开远程命令：

```bash
barn exec meta -- hostname
barn exec meta -- df -h / /data
```

`barn up` 会确认管理 SSH 可用，并报告数据盘、私网等客机阶段是否存在功能限制。修复问题或初始化被中断后，重新运行 `barn up` 即可继续收敛，已处于健康状态的虚拟机不会重启。

> [!WARNING]
> 数据盘属于可丢弃的测试存储。在客机恢复期间，若文件系统检查工具报告 ext4 或 XFS 数据盘存在可识别的损坏，`barn up` 会将其重置（持久数据盘同样如此）。重要数据请保存在宿主上，磁盘保留与恢复边界详见[存储与访问](../storage/)。

## 扩容为多节点环境 {#scale}

要把实验环境扩展为四个节点（按默认每节点 4 GiB 计算共需 16 GiB 客机内存），在现有 `barn.yml` 的 `all.children.nodes.hosts` 下追加三个节点。新地址需要与 `meta` 位于同一个 `/24`；如果首次运行时 Barn 改选了其他网段，请使用那个网段：

```yaml {title="barn.yml"}
all:
  vars:
    admin_ip: 10.10.10.10
  children:
    nodes:
      hosts:
        10.10.10.10: { nodename: meta }
        10.10.10.11: { nodename: node-1 }   # 新增
        10.10.10.12: { nodename: node-2 }   # 新增
        10.10.10.13: { nodename: node-3 }   # 新增
```

预览差异并拉起新增节点：

```bash
barn plan
barn up
```

`barn plan` 会输出 `create: node-1, node-2, node-3`，随后 `barn up` 会在不重启 `meta` 的前提下创建这三个节点。

如果修改了已有节点的 CPU 或内存，执行 `barn resize <node>` 即可应用，并保留虚拟机身份与磁盘；镜像变更仍需执行 `barn recreate <node>`，这会替换该节点的根盘。从 `barn.yml` 中删除节点条目不会自动销毁虚拟机，需显式运行 `barn destroy <node>`。

## 停止、恢复与清理 {#cleanup}

```bash
barn stop
barn start
```

`stop` 与 `start` 都会保留虚拟机磁盘。不再需要实验环境时，运行 `barn destroy` 并输入 `destroy` 确认。Barn 会删除虚拟机及其根盘与非持久数据盘，移除部署状态和它安装的 SSH 别名，同时保留持久数据盘、部署密钥、基础镜像缓存与宿主网络。之后在 `~/barn-lab` 中再次运行 `barn up`，就会根据 `barn.yml` 重建一套新的实验环境。如需彻底移除所有残留文件，请参阅[卸载与清理](../uninstall/)。

## 接下来 {#next}

- [日常管理](../operations/) — 查看日志、重启节点、应用配置变更与销毁虚拟机。
- [存储与访问](../storage/) — 配置持久数据盘、通过 OpenSSH 传输文件并访问客机端口。
- [镜像仓库](../images/) — 选择 Debian、Rocky Linux、Ubuntu 或导入本地 `qcow2` 镜像。
- [自动化](../automation/) — 无人值守 `setup --yes`、解析 `--json` 输出、执行客机脚本，以及与 Pigsty 共用 `pigsty.yml`。
{.cards}
