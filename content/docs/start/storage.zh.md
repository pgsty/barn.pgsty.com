---
title: 存储、文件与服务访问
linkTitle: 存储与访问
description: 配置测试数据盘，理解保留规则，传输文件，并通过 OpenSSH 访问客机服务。
weight: 40
icon: fa-solid fa-hard-drive
---

> [!NOTE]
> **Unreleased**：下文关于macOS 宿主 9p 共享、共享源与客机挂载路径支持的变更需要包含源码提交 `27f17bb` 的构建，Barn 0.9.2 尚未包含这些行为。详见[未发布变更](/zh/docs/about/unreleased/)。

本指南介绍 **Barn 0.9.2** 下 Linux 实验环境的数据盘配置、文件传输与服务访问，示例沿用 [Linux 快速上手](../tutorial/)中的 `meta` 节点（`10.10.10.10`）。

## 创建虚拟机前配置磁盘

默认情况下，每个 Linux 节点配有一块 64 GiB 根盘写时复制层，以及一块挂载在 `/data` 的 128 GiB 非持久数据盘。`vm_disk` 用于以 GiB 为单位设置根盘大小（可填整数 `64` 或带单位的 `64GiB`）；`vm_disks` 则会替换整个数据盘列表（设为 `vm_disks: []` 即不挂载额外数据盘）。

新建单节点实验环境时，可将以下配置保存为 `storage.yml`：

```yaml {title="storage.yml"}
all:
  vars:
    admin_ip: 10.10.10.10
    vm_image: u24@20260926.0.0
  children:
    nodes:
      hosts:
        10.10.10.10:
          nodename: meta
          vm_cpu: 2
          vm_mem: 4096
          vm_disk: 64
          vm_disks:
            - {path: /data, size: 64, fs: auto, persistent: true}
            - {path: /scratch, size: 32, fs: ext4, persistent: false}
```

若同名节点已存在且磁盘配置不同，`barn up` 会提示配置漂移；请先查看 `barn plan` 并备份所需数据，再显式执行 `barn recreate meta`（重建会替换根盘与非持久数据盘）。

校验配置文件、创建虚拟机并验证挂载结果：

```bash
barn validate -f storage.yml
barn plan -f storage.yml
barn up -f storage.yml
barn exec meta -- findmnt /data
barn exec meta -- findmnt /scratch
barn exec meta -- df -h / /data /scratch
```

磁盘容量（`size: 64` 或 `size: 64GiB`）均为按需分配的稀疏虚拟容量，随实际写入增长。当 `fs: auto` 时，若客机安装了 `mkfs.xfs` 则优先格式化为 XFS，否则使用 `ext4`。启动后请结合 `barn up` 输出警告与 `findmnt` 确认数据盘已正常挂载。

## 各类操作的磁盘保留规则

| 操作 | 根盘与非持久数据盘 | 持久数据盘（`persistent: true`） |
|---|---|---|
| `stop` 后 `start`，或 `restart` | 保留 | 保留 |
| 健康状态下重复执行 `up` | 保留 | 保留 |
| 规格兼容的 `recreate` | 替换 | 保留并重新挂载 |
| 普通 `destroy` | 删除 | 保留 |
| 整套部署 `destroy --delete-persistent` 或 `purge` | 删除 | 删除（含已保留的持久盘） |

Barn 依据磁盘身份与规格参数复用持久数据盘：在 `recreate` 或 `destroy` 后重新挂载保留盘时，节点名称、挂载路径 `path`、容量 `size` 和文件系统 `fs` 必须保持一致。规格不匹配时 Barn 会拒绝挂载，而不会自动执行扩容、改名或文件系统转换。

> [!WARNING]
> **持久数据盘依然属于可丢弃的测试存储。** `persistent: true` 仅控制虚拟机销毁或重建时是否保留磁盘文件；但在客机恢复期间，若 `barn up` 检测到文件系统无法识别或已确认损坏，仍会将其重新格式化（并在 `nodes[].repairs` 中记录）。设备暂缺、探测失败、挂载点繁忙或宿主 I/O 错误绝不会触发格式化。重要数据请务必备份在宿主上。

新格式化的数据盘默认归 `root` 所有。你可以用以下命令验证写入 `/data` 的数据在普通停机重启后依然保留：

```bash
barn exec meta -- sudo -n sh -c \
  'printf "retention check\n" > /data/barn-retention.txt'
barn stop meta
barn start meta
barn exec meta -- cat /data/barn-retention.txt
```

macOS 客机的目录共享用法请参阅 [macOS 虚拟机教程](../macos/#共享目录)。

## 通过管理 SSH 传输文件

从运行中的部署导出独立的 OpenSSH 配置文件，即可直接使用 `ssh`、`scp` 或 `rsync`：

```bash
barn ssh-config > barn-ssh.conf
ssh -F ./barn-ssh.conf barn-meta hostname
scp -F ./barn-ssh.conf ./storage.yml barn-meta:/tmp/storage.yml
scp -F ./barn-ssh.conf barn-meta:/data/barn-retention.txt ./barn-retention.txt
```

生成的配置片段引用当前回环 SSH 端口、部署密钥路径以及按实例隔离的 `known_hosts` 文件，不会内嵌私钥原文。重建节点或管理端口变动后请重新导出，或执行 `barn ssh-config --install` 将别名写入 `~/.ssh/config`，从而免去 `-F` 参数。

## 访问客机内的服务

只要客机内的服务监听在节点的固定私网 IP 上（例如监听在 `10.10.10.10:5432` 的 PostgreSQL）且客机防火墙放行，宿主与其他节点即可直接通过该 IP 访问。

如果服务仅监听在客机回环地址 `127.0.0.1` 上，可通过 OpenSSH 建立本地端口转发隧道：

```bash
ssh -F ./barn-ssh.conf -N \
  -L 127.0.0.1:15432:127.0.0.1:5432 barn-meta
```

保持该终端运行，宿主本地客户端即可连接 `127.0.0.1:15432`（按 `Ctrl-C` 关闭隧道）。

SSH 别名（如 `ssh meta`）仅对 OpenSSH 工具生效。如果希望浏览器、`psql` 等常规宿主程序也能直接解析节点名与 `vm_alias`，可预览并启用 `/etc/hosts` 集成：

```bash
barn hosts install --json
barn hosts install --yes
```

`barn hosts install --yes` 会更新当前宿主的 `/etc/hosts`（必要时请求 `sudo`）；增删节点或修改 IP 后重新执行即可刷新。

Barn 清单不提供 `vm_ports` 或 `vm_forwards` 字段，请直接使用固定私网 IP 或 OpenSSH 端口转发。由于管理 SSH 走独立的宿主回环端口，即便固定 IP 私网受限，`barn ssh` 与 `-L` 隧道依然可用。

## 宿主目录共享

Linux 与 macOS 宿主均可通过 QEMU Virtio-9p 向 Linux 客机共享目录。首次 `barn up` 前在 `all.vars` 或节点变量下设置：

```yaml {title="barn.yml"}
vm_shares:
  - host: ./src
    guest: /workspace
    readonly: true
```

`host` 支持相对清单真实文件目录的路径、`~/` 与目录符号链接。目录须已存在、当前用户可访问且不与 `BARN_HOME` 重叠，无须归当前用户所有；多个客机可以读写同一目录，由用户协调写入。

宿主 QEMU 与客机内核须支持 9p。可写共享还受客机用户权限约束；无法写入时会降级只读并报告警告，不会修改宿主属主。修改已有节点共享后执行 `barn recreate <node>`。原生 macOS 客机使用 `barn mac --share` 提供的 VirtioFS。

完整的磁盘与共享字段约束请参阅[配置参考](../../reference/configuration/#数据盘)。
