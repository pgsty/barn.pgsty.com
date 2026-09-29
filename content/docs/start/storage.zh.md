---
title: 存储、文件与服务访问
linkTitle: 存储与访问
description: 配置测试数据盘，理解保留规则，传输文件，并通过 OpenSSH 访问客机服务。
weight: 36
icon: fa-solid fa-hard-drive
---

本教程使用 **Barn 0.9.0 发布候选**的接口。执行客机内检查之前，
先完成[快速上手](../tutorial/)。示例使用 `meta` 节点与默认子网；调整已有配置时，
请沿用实际节点名称与地址。

## 创建 VM 前选择磁盘

每个节点默认有 64 GiB 根盘，以及挂载到 `/data` 的 128 GiB 非持久数据盘。
`vm_disk` 以 GiB 设置根盘大小，`vm_disks` 替换整个数据盘列表；
`vm_disks: []` 表示不配置额外数据盘。

新建单节点实验环境时，将以下内容保存为 `storage.yml`：

```yaml
all:
  vars:
    admin_ip: 10.10.10.10
    vm_image: u24@20260911.0.0
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

审查配置，然后创建：

```bash
barn validate -f storage.yml
barn plan -f storage.yml
barn up -f storage.yml
barn exec meta -- findmnt /data
barn exec meta -- findmnt /scratch
barn exec meta -- df -h / /data /scratch
```

`size: 64` 表示 64 GiB；数据盘也可写成 `size: 64GiB`。这些是虚拟容量，
不是立即占用的宿主空间；qcow2 文件增长时仍需关注宿主剩余容量。
`fs: auto` 在客机具备 `mkfs.xfs` 时优先使用 XFS，否则使用 ext4。
VM 进程启动成功不代表数据盘已挂载，请检查客机结果与警告。

此例用于首次创建。如果同名节点已经存在且定义不同，`up` 会报告漂移。
检查 `plan` 并备份所需数据后，才能显式执行 `recreate`；它会替换根盘与非持久数据盘。

## 各种操作会保留什么

| 操作 | 根盘与非持久数据盘 | 持久数据盘 |
|---|---|---|
| `stop` 后 `start`，或 `restart` | 保留 | 保留 |
| 健康状态重复 `up` | 保留 | 保留 |
| 规格兼容的 `recreate` | 替换 | 保留并重新挂载 |
| 普通 `destroy` | 删除 | 保留 |
| 整套部署 `destroy --delete-persistent` | 删除 | 删除，包括已保留的磁盘 |
| 整套部署 `purge` | 删除 | 删除，包括已保留的磁盘 |

保留盘复用依赖磁盘身份和兼容的规格。再次使用时应保持节点、挂载路径、大小和
文件系统定义一致。它不是自动扩容、改名、文件系统转换、备份或快照功能。
Barn 会拒绝不兼容的保留盘，不要通过手改状态文件强行挂载。

**持久盘仍然是可丢弃的测试存储。** 客机恢复期间，`up` 可能清空重建无法识别或
确认损坏的文件系统，并报告数据丢弃。持久性只控制 VM 销毁/重建时的保留行为。
缺少设备、探测失败、挂载点忙碌和 I/O 错误不会触发格式化。
测试故障恢复之前，应将有价值的数据另行保存。

新格式化的数据文件系统由 root 拥有。下面的写入检查使用客机 sudo；应用所需的目录权限
应另行明确配置。在已创建的环境中，可以验证普通重启的数据保留：

```bash
barn exec meta -- sudo -n sh -c \
  'printf "retention check\n" > /data/barn-retention.txt'
barn stop meta
barn start meta
barn exec meta -- cat /data/barn-retention.txt
```

这只检查 VM stop/start，不是物理宿主重启后的持久性验证。
原生验证范围见[当前状态](../../about/status/)。

## 使用管理 SSH 连接传输文件

从运行中的部署生成独立 OpenSSH 配置：

```bash
barn ssh-config > barn-ssh.conf
ssh -F ./barn-ssh.conf barn-meta hostname
scp -F ./barn-ssh.conf ./storage.yml barn-meta:/tmp/storage.yml
scp -F ./barn-ssh.conf barn-meta:/data/barn-retention.txt ./barn-retention.txt
```

生成的片段包含当前回环 SSH 端口、部署密钥路径与实例主机密钥身份。
重建 VM 或管理端口变化后，应重新生成。如果希望普通 SSH 配置也能使用这些别名，
可选用 `barn ssh-config --install`；上面的 `-F` 用法无需这项集成。
导出的配置只引用部署密钥，不会内嵌或导出私钥内容。

## 访问客机内的服务

宿主可以通过客机固定 IP 访问监听在该地址上的服务，前提是客机防火墙与服务配置允许。
例如 `10.10.10.10:5432` 上的 PostgreSQL 服务需要另外安装；Barn 启动 VM
不会自动安装 PostgreSQL。

如果服务只监听客机回环地址，可以使用刚才生成的 OpenSSH 配置建立隧道：

```bash
ssh -F ./barn-ssh.conf -N \
  -L 127.0.0.1:15432:127.0.0.1:5432 barn-meta
```

保持该宿主终端打开，再让本地客户端连接 `127.0.0.1:15432`。
客机服务必须已经监听 5432。Ctrl-C 关闭隧道；如果宿主 15432 已占用，请换一个本地端口。
显式绑定回环地址，使此示例仅供本机访问。

Inventory 没有 `vm_ports` 或 `vm_forwards` 字段，未知 `vm_*` 会被拒绝。
请使用固定 IP 网络或 OpenSSH 转发。管理 SSH 使用独立的回环连接，固定 IP
网络报告限制时，管理连接仍可能可用。

## Linux 宿主目录共享

Linux 宿主可以在首次 `up` 前配置只读共享：

```yaml
vm_shares:
  - host: /srv/barn-project
    guest: /workspace
    readonly: true
```

将其放入目标主机变量或 `all.vars`，把宿主路径替换为已存在、Barn 用户能够访问的
真实目录，而且目录必须属于当前 Barn 用户，只读共享也不例外。
宿主路径必须为绝对路径，不能穿过符号链接，也不能与 Barn 数据根重叠。
源文件共享可以从显式只读开始；可写共享还取决于客机用户权限，Barn 可能回退到
只读并报告限制，不会修改宿主目录属主。

**不要在当前文档所述运行时的 macOS 环境中添加 `vm_shares`。** 已测 macOS/QEMU
路径无法重新打开安全持有的目录描述符，受影响节点无法启动；这里应使用 SSH 文件传输。
宿主源目录或挂载丢失时，恢复原目录/挂载后再重试 `up`；Barn 不会新建空目录替代。
修改已有节点的共享定义需要显式重建。完整磁盘与共享约束见[配置参考](../../reference/configuration/)。
