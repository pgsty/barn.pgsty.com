---
title: 快速上手
linkTitle: 快速上手
description: 安装 Farrow 0.8.0，用 up 启动 Ubuntu 实验环境，用 ssh 进入，再通过同一份配置增量扩容。
weight: 10
icon: fa-solid fa-play
aliases: [/docs/start/installation/, /docs/start/upgrade/, /docs/start/lab/, /docs/start/pigsty/, /docs/features/]
---

## 安装

本教程面向公开版 **0.8.0**。命令行参考还会说明尚未发布的 0.9 变化，
并明确标注；详见[版本基线](../../about/status/#documentation-baseline)。

当前公开版本为 [Farrow 0.8.0](https://github.com/pgsty/farrow/releases/tag/v0.8.0)，
在 GitHub 上标记为 **Pre-release**。用户态安装器支持 macOS / Linux 的 arm64 与 amd64，
会校验归档的 Checksum，安装过程无需 sudo：

```bash
curl -fLO https://github.com/pgsty/farrow/releases/download/v0.8.0/install.sh
chmod +x install.sh
FARROW_VERSION=0.8.0 ./install.sh
export PATH="$HOME/.local/bin:$PATH"
farrow version
```

默认安装目录为 `~/.local/bin`；把同一行 PATH 设置加入 Shell 配置，后续打开的终端也能使用。
`farrow version` 应显示 `0.8.0`。GitHub 的 `/releases/latest` 不包含预发布版本，
因此需要保留显式的 `FARROW_VERSION`。

GitHub 下载超时时，请配置终端的代理环境，见[下载与 PATH 问题](../troubleshooting/#下载与-path-问题)。

### 其他安装方式

任选一种安装方式即可。[官方 Homebrew Tap](https://github.com/pgsty/homebrew-infra/blob/main/Formula/farrow.rb)
当前提供 0.8.0，并依赖 QEMU。下面的 Linux 示例使用 amd64 软件包；ARM64 Linux 请使用
对应的 `linux_arm64` 资产。

```bash {tab="Homebrew" group="install" value="brew"}
brew install pgsty/infra/farrow
farrow version
```

```bash {tab="Debian / Ubuntu" value="deb"}
farrow_release=https://github.com/pgsty/farrow/releases/download/v0.8.0
curl -fLO "$farrow_release/farrow_0.8.0_linux_amd64.deb"
sudo apt install ./farrow_0.8.0_linux_amd64.deb
farrow version
```

```bash {tab="RHEL / Fedora" value="rpm"}
farrow_release=https://github.com/pgsty/farrow/releases/download/v0.8.0
curl -fLO "$farrow_release/farrow_0.8.0_linux_amd64.rpm"
sudo dnf install ./farrow_0.8.0_linux_amd64.rpm
farrow version
```

开发者可使用[从源码构建](../source-build/)。

当前支持 Linux 客机。下表中的 macOS 指运行 Farrow 的宿主，不表示提供 macOS 客机镜像。

### 宿主要求

| 宿主 | 原生加速 | 最低 QEMU 版本 |
|---|---|---|
| macOS arm64 / amd64 | HVF | 8.2.1 |
| Linux amd64 / arm64 | KVM | 6.2 |

宿主还需要 `qemu-img`、OpenSSH 与所选客机对应的固件。交互式 `up` 可以通过 macOS 的
Homebrew，或受支持 Linux 发行版的 apt/dnf 补齐依赖，并安装固定 IP 网络。宿主软件包与
网络变更可能需要 sudo；Farrow 本身应以普通用户运行。Linux 需要可用的 KVM，以及
NetworkManager 或 systemd-networkd。带日期的真机验证覆盖 macOS arm64 与 Ubuntu amd64，
其他构建平台的验证范围较窄，详见[当前状态](../../about/status/)。

## 启动第一个实验环境

首次部署时，在终端中进入一个空目录：

```bash
mkdir -p ~/farrow-lab && cd ~/farrow-lab
farrow up
farrow ssh
```

用 `exit` 从客机返回宿主终端后，再执行后续 Farrow 命令。

没有配置文件、也没有已应用部署时，交互式 `up` 会生成只有一个 `meta` 节点的
`farrow.yml`，准备缺少的宿主依赖与网络，下载并校验镜像，启动 QEMU，然后等待管理 SSH
就绪。宿主变更会显示出来，sudo 可能要求输入密码。如果希望先查看完整宿主计划，运行
`farrow setup --dry-run`。

> [!NOTE]
> 换目录不会新建一套实验环境。状态位于 `$FARROW_HOME`，默认是 `~/.farrow`。
> 如果已有部署且当前目录没有配置文件，`up` 会继续该部署；可先用 `farrow status` 查看。

默认模板解析为：

| 配置项 | 默认值 |
|---|---|
| 节点 / 固定 IP | `meta` / `10.10.10.10` |
| 客机镜像 | Ubuntu 24.04，`u24:stable`，与宿主相同的架构 |
| 登录用户 | `dba`，使用 SSH 密钥认证 |
| CPU / 内存 | 每节点 2 vCPU / 4 GiB |
| 根盘 / 数据盘 | 64 GiB 根盘 + 挂载到 `/data` 的 128 GiB 非持久数据盘 |

磁盘大小是虚拟容量，qcow2 文件随写入增长。四节点环境共配置 8 vCPU、16 GiB 客机内存，
还需为宿主保留资源；启动前可用 `farrow plan` 查看总量。

首次使用、尚未编辑且采用默认网段的内置模板遇到子网冲突时，setup 可以改用可用的私有 `/24`；若模板文件
已经存在，会备份为 `farrow.yml.before-network-change`。请以生成后的 `farrow.yml` 和
`farrow status` 为准。显式 `-f` 文件、编辑过的模板与已有部署会保留选定网段。

健康的首次启动会以类似结果结束：

```text
  ✓  1 node ready
connect:   farrow ssh meta
```

`farrow ssh` 默认连接控制节点，在此模板中就是 `meta`。也可以显式指定节点，或直接执行命令：

```bash
farrow ssh meta
farrow exec meta -- hostname
farrow st
```

`st` 是 `status` 的别名；
其中的 `running` 表示 VM 进程在运行，不代表刚刚重新检查了客机就绪状态。

### 继续未完成的初始化

重复 `farrow up` 可以接续中断的操作、重试未完成的客机初始化、更新旧的客机脚本。
健康的运行中 VM 会保留进程与根盘。管理 SSH 可用时，即使共享目录只读、私网不可用等功能
受限，客机仍可完成启动。请查看这些提示；自动化应检查 `farrow up --json` 的
`nodes[].warnings` 与 `nodes[].repairs`，因为这些限制仍返回退出码 0。

> [!WARNING]
> 数据盘是可丢弃的测试存储。`up` 可能清空重建无法识别或确认损坏的文件系统，
> **包括持久盘**，并报告旧数据已丢弃。`persistent` 只控制 destroy/recreate 时保留磁盘，
> 不保证恢复时保留损坏的内容。详见[数据盘说明](../../reference/configuration/#数据盘)。

`--no-wait` 会跳过客机就绪、恢复与元数据刷新，后续执行 `farrow up` 补齐。
镜像下载支持重试与断点续传；使用 `farrow up --mirror` 优先访问中国官方仓库。
镜像选择与回退规则见[镜像仓库](../images/)。

## 启动前选择配置

这是前面自动启动流程的另一种入口。在新的实验目录中，先生成并检查配置，再启动：

```bash
farrow init
farrow validate
farrow plan
farrow up
```

对于本文使用的 Catalog 镜像，`init`、`validate`、`plan` 都不要求先安装 QEMU
或配置宿主网络。规划已注册的 `local-*` 镜像时，则需要 `qemu-img` 校验缓存字节。默认 `meta` 配置为：

```yaml
all:
  vars:
    admin_ip: 10.10.10.10
  children:
    nodes:
      hosts:
        10.10.10.10: { nodename: meta }
```

内置四种模板：

| 模板 | 节点数 | 默认地址 |
|---|---:|---|
| `meta` | 1 | `10.10.10.10` |
| `dual` | 2 | `10.10.10.10`–`10.10.10.11` |
| `trio` | 3 | `10.10.10.10`–`10.10.10.12` |
| `full` | 4 | `10.10.10.10`–`10.10.10.13` |

例如 `farrow init full` 生成四节点配置，`farrow init full -c 10.20.30.0/24` 指定另一网段。
现有文件不会被覆盖，除非显式传入 `--force`。在第一次 `up` 前调整 `vm_cpu`、`vm_mem`、
`vm_image` 等字段，全部字段见[配置参考](../../reference/configuration/)。

### 显式准备宿主

`setup` 只准备依赖与网络，不启动 VM：

```bash
farrow setup --dry-run
farrow setup
```

与 `up` 内部的准备流程不同，单独执行 `setup` 会在应用有变更的计划前请求确认。
它会复用当前目录发现的配置，没有文件时生成 `meta`。可选的 `/etc/hosts` helper
仅在 `farrow hosts install --yes` 需要时安装；普通启动与 `farrow ssh` 不依赖这项集成。

下载尊重 `HTTP_PROXY`、`HTTPS_PROXY`、`ALL_PROXY`、`NO_PROXY` 及其小写形式。
无人值守的首次部署可在空目录执行：

```bash
farrow setup --yes
farrow up --json
```

`setup --yes` 本身就能生成配置，只有需要预先编辑时才必须单独 `init`。自动化环境仍需为
必要的 sudo 操作准备凭据；`--yes` 不会提供管理员凭据。
[自动化教程](../automation/)说明如何保存命令结果、检查客机限制后再继续。

### 使用现有 Pigsty 配置

```bash
farrow validate -f pigsty.yml
farrow plan -f pigsty.yml
farrow up -f pigsty.yml
```

Farrow 读取已记录的 VM、命名与登录字段，其余 Pigsty 参数保持原样。以上步骤启动虚拟机；
PostgreSQL 与其他 Pigsty 服务仍需通过 Pigsty 单独安装。内置模板只描述 VM 拓扑，
不包含完整的 Pigsty 服务配置。
衔接方式见[自动化与客机脚本](../automation/#与-pigsty-一起使用)，
文件传输与服务连接见[存储与访问](../storage/)。

## 扩容与日常操作

扩展默认单节点环境时，保留已有设置，在 `farrow.yml` 中增加三台主机：

```yaml
all:
  vars:
    admin_ip: 10.10.10.10
  children:
    nodes:
      hosts:
        10.10.10.10: { nodename: meta }
        10.10.10.11: { nodename: node-1 }
        10.10.10.12: { nodename: node-2 }
        10.10.10.13: { nodename: node-3 }
```

此例假定使用默认网段；如果 setup 选择了其他网段，所有地址及 `admin_ip` 都应沿用该网段。
不要为了扩容而用 `init --force` 覆盖已经定制的配置。

```bash
farrow plan
farrow up
farrow st
```

仅增加这三行时，计划应列出三个待创建节点。`up` 会创建它们，保留正在运行的 `meta`
进程，并刷新客机 hosts 与控制节点 SSH 配置。健康的结果为 `4 nodes ready`。
0.8.0 内置 Catalog 将 `u24:stable` 解析为 `u24@20260911.0.0`；手动更新 Catalog 后
可能解析为其他版本，准确版本显示在 `plan` 和 `status` 中。

修改 CPU、内存或其他被读取的 VM 字段，需要显式执行 `farrow recreate <node>`；
删除 YAML 条目不会删除 VM。停止并恢复环境，不重建磁盘：

```bash
farrow stop
farrow start
```

使用完毕后销毁部署：

```bash
farrow destroy
```

在终端输入 `destroy` 确认。根盘与非持久数据盘会被删除，镜像缓存、密钥、声明为持久的
数据盘与宿主网络保留。彻底清理见[卸载与清理环境](../uninstall/)；重启、日志、显式变更与
缩容见[日常管理](../operations/)。

## 升级已有安装

沿用原来的安装渠道：重新运行固定版本的安装器，执行 `brew update` 后再执行
`brew upgrade pgsty/infra/farrow`，或安装新版 DEB/RPM。之后先检查 `farrow version`
与 `farrow plan`，再运行 `farrow up`。`farrow update` 更新的是镜像 Catalog，不是 Farrow 程序。
恢复改进与真机验证范围见 [0.8.0 发布说明](../../../blog/release/farrow-0.8.0/)。

从更老版本升级、且原 Debian 环境省略了 `vm_image` 时，在 `all.vars` 设置 `vm_image: d13`
以保留原来的镜像选择；默认值在 0.6.0 改为 Ubuntu 24.04。数据盘恢复策略，以及 0.6.0
初始化中断后控制节点 SSH 的限制，见 [0.7.0 升级说明](../../../blog/release/farrow-0.7.0/)。
