---
title: 安全与信任
description: Barn 0.9.1 的宿主权限、客机凭据、共享目录，以及应用与镜像的独立信任边界。
weight: 25
icon: fa-solid fa-shield-halved
---

Barn 用于可信的本地开发环境。Linux 节点共享一个私有网络，控制节点可以管理其他节点。
归属检查可防止误操作无关资源，但不能隔离互不信任的用户。

## 宿主权限

以普通用户运行 `barn`。QEMU 与镜像下载使用当前账户。虚拟机磁盘与状态也属于该账户。
只有以下宿主操作需要管理员权限：

| 操作 | 变更范围 |
| --- | --- |
| `setup` 安装缺失的 Linux 依赖 | 通过发行版包管理器安装 QEMU、固件与 OpenSSH；macOS Homebrew 以普通用户运行 |
| `network install` / `uninstall` | 宿主全局固定 IP 网络后端及其已记录配置 |
| `hosts install` / `uninstall` | 通过独立 helper 修改系统 hosts 文件中由 Barn 标记界定的区块 |

安装程序会在请求权限前展示所需变更。请配套安装同一次构建的 CLI 与 `barn-hosts-helper`。
`/opt/barn/libexec/` 下的 helper 必须匹配打包 CLI 内嵌的摘要。每次修改时，helper 会检查
文件属主、权限、链接数，以及写入前后内容的预期摘要。

原生 `barn mac` 为每台虚拟机使用独立网络。它不增加 root 守护进程或特权网络事务。
资源的生命周期见[设计说明](../design/)与[卸载](../../start/uninstall/)。

## 客机访问与 SSH 信任

Linux 客机账户默认为 `dba`，拥有免密 sudo 权限。该账户的密码处于锁定状态。
Barn 使用部署级 SSH 密钥登录。控制节点也会收到这把私钥，用于运行 Ansible 和管理其他节点。
能访问控制节点的用户具有整个 Linux 实验环境的管理权限。

不同 SSH 连接采用不同的主机密钥策略：

| 连接 | 主机密钥策略 |
| --- | --- |
| 宿主通过 Barn → Linux 客机 | 使用 `accept-new`、独立 known-hosts 文件与 VM UUID 别名；首次接受密钥，后续不匹配则拒绝 |
| Linux 控制节点 → 其他节点 | 自动生成的配置使用 `StrictHostKeyChecking no`，known-hosts 指向 `/dev/null`，方便频繁重建实验节点 |
| 宿主通过 Barn → 已初始化 macOS 客机 | 严格校验每台机器固定的主机密钥，禁用 agent forwarding |

控制节点使用生成的 SSH 配置连接其他节点时，会跳过主机密钥检查。请只在可信实验网络中使用这份配置。
显式重建会产生新的虚拟机身份，即使端口号或固定 IP 没有变化。

每台 Mac 虚拟机有独立的 SSH 密钥与随机桌面密码。密码保存在虚拟机目录内、权限为 0600
的文件中，不使用 Keychain。用 `barn mac password` 查看密码。

首次 SSH 初始化完成后，客机使用密钥认证。客机禁用 SSH 密码认证与 root 的 SSH 登录，
并授予配置用户免密 sudo 权限。不要将包含凭据的状态文件或命令输出复制到 Issue 或共享仓库。

## 共享文件与测试磁盘

可写共享允许客机进程访问选定的宿主目录。请使用专用目录。
如果客机不需要写入文件，选择只读模式。删除虚拟机不会删除宿主共享目录，
也不会撤销客机对该目录的修改。

普通销毁或重建会保留 Linux 持久数据盘，但客机恢复流程仍可能格式化无法识别或确认损坏的文件系统。
请在实验环境之外备份重要内容。删除和恢复规则见[存储与访问](../../start/storage/)。

## 下载与镜像信任

| 机制 | 校验对象 |
| --- | --- |
| 应用 `checksums.txt` | 下载的归档与软件包是否匹配该 Release 公布的哈希 |
| 原生应用代码签名与公证 | 独立的 macOS 分发流程；0.9.1 不分发原生应用；本地源码构建默认使用 ad-hoc 签名 |
| Linux 镜像目录签名 | 元数据是否由受信任目录密钥签署，并满足版本修订规则 |
| 镜像下载校验 | 大小、SHA-256、qcow2 结构与虚拟容量是否符合已接受的元数据 |

应用校验和不构成独立的发布签名。受信任的镜像目录也不能认证 Barn 可执行文件。
两个官方镜像仓库始终要求签名，包括用 `--repo` 显式选择它们时。自定义 HTTPS 或本地仓库
可以接受未签名元数据，请只使用你信任的来源。
修订版本与缓存规则见[镜像校验参考](../../reference/images/)。

## 报告安全漏洞

使用 [GitHub 私密漏洞报告](https://github.com/pgsty/barn/security/advisories/new)，
或发邮件至 [repo@pigsty.cc](mailto:repo@pigsty.cc)。附上 `barn --json version`、
宿主平台与移除凭据后的最小复现步骤。
[安全政策](https://github.com/pgsty/barn/blob/main/SECURITY.md)说明支持与披露方式。
普通使用问题请提交至 [Issues](https://github.com/pgsty/barn/issues)。
