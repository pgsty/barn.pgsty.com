---
title: 存储、文件与服务访问
linkTitle: 存储与访问
description: 配置测试数据盘，理解保留规则，传输文件，并通过 OpenSSH 访问客机服务。
weight: 40
icon: fa-solid fa-hard-drive
---

本教程使用 **Barn 0.9.1** 的接口，基本操作可参考[快速上手](../tutorial/)。
下方磁盘示例用于新环境。
示例使用 `meta` 节点与默认子网，调整已有清单时应沿用实际节点名称与地址。

## 创建 VM 前选择磁盘

每个节点默认有 64 GiB 根盘，以及挂载到 `/data` 的 128 GiB 非持久数据盘。
`vm_disk` 的整数以 GiB 设置根盘大小，也接受 `64GiB` 这样的显式单位。
`vm_disks` 替换整个数据盘列表。`vm_disks: []` 表示不配置额外数据盘。

新建单节点实验环境时，将以下内容保存为 `storage.yml`：

```yaml
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

如果同名节点已存在且定义不同，`up` 会报告配置差异。
重建会替换根盘与非持久数据盘；请先检查 `plan` 并备份所需数据，再显式执行 `recreate`。

新建环境时，检查配置、创建虚拟机，再检查磁盘挂载：

```bash
barn validate -f storage.yml
barn plan -f storage.yml
barn up -f storage.yml
barn exec meta -- findmnt /data
barn exec meta -- findmnt /scratch
barn exec meta -- df -h / /data /scratch
```

`size: 64` 表示 64 GiB。数据盘也可写成 `size: 64GiB`。这些是虚拟容量，不会立即占用相应宿主空间。qcow2 文件增长时，监测宿主剩余容量。
`fs: auto` 在客机具备 `mkfs.xfs` 时优先使用 XFS，否则使用 ext4。
虚拟机进程启动成功不代表数据盘已挂载。检查客机结果与警告。

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
Barn 会拒绝不兼容的保留盘。不要手工修改状态文件来强行挂载。

**持久盘仍然是可丢弃的测试存储。** 客机恢复期间，`up` 可能清空重建无法识别或
确认损坏的文件系统，并报告数据丢弃。持久性只控制虚拟机销毁/重建时的保留行为。
缺少设备、探测失败、挂载点忙碌和 I/O 错误不会触发格式化。
测试故障恢复之前，应将有价值的数据另行保存。

新格式化的数据文件系统由 root 拥有，因此下面的写入检查使用客机 sudo。
应用需要写入时，也可以另行配置目录权限。
在已创建的环境中，检查普通停止和启动后是否保留数据：

```bash
barn exec meta -- sudo -n sh -c \
  'printf "retention check\n" > /data/barn-retention.txt'
barn stop meta
barn start meta
barn exec meta -- cat /data/barn-retention.txt
```

这个示例检查虚拟机停止和启动后的数据保留。请在实验环境之外保存备份。
macOS 客机的文件夹共享见 [Mac 教程](../macos/#共享目录)。

## 使用管理 SSH 连接传输文件

从运行中的部署生成独立 OpenSSH 配置：

```bash
barn ssh-config > barn-ssh.conf
ssh -F ./barn-ssh.conf barn-meta hostname
scp -F ./barn-ssh.conf ./storage.yml barn-meta:/tmp/storage.yml
scp -F ./barn-ssh.conf barn-meta:/data/barn-retention.txt ./barn-retention.txt
```

生成的片段包含当前回环 SSH 端口、部署密钥路径与实例主机密钥身份。
重建虚拟机或管理端口变化后，应重新生成。如果希望普通 SSH 配置也能使用这些别名，
可选用 `barn ssh-config --install`。上面的 `-F` 用法无需这项集成。
导出的配置只引用部署密钥，不会内嵌或导出私钥内容。

## 访问客机内的服务

服务监听客机固定 IP，且客机防火墙允许访问时，宿主就能连接该服务。
例如，在客机中安装并配置 PostgreSQL 后，可以通过 `10.10.10.10:5432` 访问。
Barn 启动虚拟机不会自动安装 PostgreSQL。

如果服务只监听客机回环地址，可以使用刚才生成的 OpenSSH 配置建立隧道：

```bash
ssh -F ./barn-ssh.conf -N \
  -L 127.0.0.1:15432:127.0.0.1:5432 barn-meta
```

保持该宿主终端打开，再让本地客户端连接 `127.0.0.1:15432`。
客机服务必须已经监听 5432。Ctrl-C 关闭隧道。如果宿主 15432 已占用，换一个本地端口。
显式绑定回环地址，使此示例仅供本机访问。

SSH 别名与普通主机名解析是两件事。即使 `ssh meta` 可用，浏览器或数据库客户端也
未必能解析 `meta`。需要把部署节点名称和 `vm_alias` 发布到宿主时，先预览再应用
可选的 hosts 集成：

```bash
barn hosts install --json
barn hosts install --yes
```

第一条只预览，第二条执行时可能需要 sudo。节点名称或地址改变后重新执行。
这只修改当前宿主，不会让局域网其他机器自动获得名称解析或私网路由。

清单没有 `vm_ports` 或 `vm_forwards` 字段，未知 `vm_*` 会被拒绝。
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

将其放入目标节点变量或 `all.vars`。把宿主路径替换为已存在的真实目录。当前 Barn 用户必须能访问该目录，并且是该目录的属主。只读共享也有相同要求。
宿主路径必须为绝对路径，不能穿过符号链接，也不能与 Barn 数据根重叠。
源文件共享可以先设为只读。可写共享还取决于客机用户权限。Barn 可能回退到只读并报告限制。它不会修改宿主目录属主。

**在 macOS 宿主上运行 Linux 客机时，请省略 `vm_shares`，改用 SSH 文件传输。**
已测 macOS/QEMU 运行时无法重新打开 Barn 安全持有的目录句柄，配置此共享的节点无法启动。

宿主源目录或挂载丢失时，先恢复原目录或挂载，再重试 `up`。Barn 不会新建空目录替代。
修改已有节点的共享定义需要显式重建。完整磁盘与共享约束见[配置参考](../../reference/configuration/)。