---
title: 安全与信任
description: Barn 0.9.2 的宿主权限、客机凭据、共享目录，以及应用与镜像的独立信任边界。
weight: 25
icon: fa-solid fa-shield-halved
---

Barn 面向受信任的本地开发工作站。同一套 Linux 实验环境中的所有节点共享同一个私有子网，且控制节点持有可管理其余节点的部署级 SSH 私钥。Barn 的属主与身份检查旨在防止误删无关宿主文件或误杀进程，而非在共享服务器上隔离互不信任的多租户用户。

## 宿主权限

日常请始终以普通登录用户运行 `barn`。QEMU 进程、`Barn.app` 虚拟机、镜像下载、虚拟磁盘与状态文件均归当前普通用户所有并以该身份运行。只有以下三项宿主级操作需要管理员（`sudo`）权限：

| 操作 | 特权变更范围 |
|---|---|
| `barn setup`（安装 Linux 宿主依赖） | 调用发行版包管理器（`apt`/`dnf`）安装 QEMU、固件与 OpenSSH（macOS 上的 Homebrew 以普通用户身份运行） |
| `barn network install` / `uninstall` | 安装或卸载宿主全局固定 IP 网络后端（Linux 上的 `barn0` 网桥，macOS 上的 `socket_vmnet` launchd 服务） |
| `barn hosts install` / `uninstall` | 通过独立的 `barn-hosts-helper` 修改 `/etc/hosts` 中由 Barn 标记界定的区块 |
{.wide}

在请求 `sudo` 授权前，`setup`、`network` 与 `hosts` 都会先打印完整的变更计划。请确保 `barn` 与 `/opt/barn/libexec/barn-hosts-helper` 来自同一次构建：CLI 调用 helper 前会核对其内嵌 SHA-256 摘要，helper 在每次写入前后都会校验 `/etc/hosts` 的属主、权限、硬链接数及预期内容摘要。

相比之下，原生的 `barn mac` 工作流在虚拟机启动时按需创建用户态 `vmnet` 网络，不安装任何 root 守护进程或特权网络服务（详见[设计说明](../design/)与[卸载指南](../../start/uninstall/)）。

## 客机访问与 SSH 信任

Linux 实验环境的默认客机管理账号为 `dba`（密码已锁定、具备免密 `sudo` 权限，并使用 `$BARN_HOME` 中生成的 Ed25519 部署密钥登录）。Barn 同时会将该私钥分发到控制节点，以便在控制节点上运行 Ansible 剧本管理其他节点——因此能够登录控制节点的用户即拥有整套 Linux 实验环境的管理权限。

Barn 针对三类 SSH 连接路径采用不同的主机密钥校验策略：

| 连接路径 | 主机密钥策略 |
|---|---|
| 宿主 → Linux 客机（经由 `barn` 或 `~/.ssh/barn_config`） | 使用独立 `known_hosts` 文件与虚拟机 UUID 别名，并启用 `StrictHostKeyChecking accept-new`（首次连接自动记录密钥，后续若密钥不匹配则拒绝连接；显式 `recreate` 会生成新的虚拟机 UUID） |
| Linux 控制节点 → 实验环境其他节点 | 对 Barn 管理的节点别名配置 `StrictHostKeyChecking no` 与 `UserKnownHostsFile /dev/null`，使实验节点频繁重建后仍可直接连通 |
| 宿主 → 已初始化的 macOS 客机 | 对照绑定到 `barn-mac-<instance_id>` 的单机专属 `known_hosts` 严格校验主机密钥，并禁用 SSH agent forwarding |
{.wide}

每台 macOS 虚拟机拥有独立的 Ed25519 SSH 密钥对与随机生成的桌面管理员密码（保存在虚拟机目录内权限为 `0600` 的 `password` 文件中，可通过 `barn mac password` 查看）。首次初始化完成后，Linux 与 macOS 客机均强制使用 SSH 公钥认证，关闭 SSH 密码认证与 root 远程登录，并为管理账号配置免密 `sudo`。提交 Issue 或分享配置时，请先剔除日志和状态文件中的私钥与密码。

## 共享文件与测试磁盘

- **宿主目录共享**：可写共享（Linux `vm_shares` 中设 `readonly: false` 或 `barn mac --share` 使用 `:rw`）允许客机进程直接修改所挂载的宿主目录，且客机写入的内容在删除虚拟机后依然保留。请仅共享专门的工作目录；若客机无需写入宿主文件，请优先使用只读共享。
- **持久盘与测试数据盘**：普通 Linux `destroy` 与 `recreate` 会保留 `persistent: true` 的持久数据盘，但客机恢复流程在遇到无法识别或已确认损坏的文件系统时仍会自动格式化重建。重要数据请在实验环境之外做好备份（详见[存储与访问](../../start/storage/)）。

## 下载与镜像信任

Barn 将软件分发与镜像校验划分为四个彼此独立的信任机制：

| 机制 | 校验范围 |
|---|---|
| 发布资产 `checksums.txt` | 核对下载的 CLI 归档与 `.deb`/`.rpm` 软件包是否与该 GitHub Release 公布的 SHA-256 摘要一致 |
| macOS 发行包代码签名 | 0.9.2 Apple Silicon CLI、helper 与 `Barn.app` 均使用 Developer ID 签名并通过 Apple 公证，App 已装订票据；本地源码构建默认使用 ad-hoc 签名 |
| Linux 镜像目录签名（`catalog.json.minisig`） | 使用二进制内置的 Ed25519 生产公钥校验 `catalog.json` 签名，并执行按仓库隔离的修订号防回滚检查 |
| 镜像产物校验 | 在启用镜像前逐一核对 `.qcow2` 文件的字节大小、SHA-256 摘要、虚拟磁盘容量与独立 `qcow2` 结构安全性 |
{.wide}

两个官方镜像仓库（`https://repo.pigsty.io/barn` 与 `https://repo.pigsty.cc/barn`）无论通过默认配置还是 `--repo` 显式选中，均强制要求有效的 minisign 目录签名。通过 `--repo` 或 `BARN_REPO` 显式指定的自定义 HTTPS 仓库或本地目录仓库可以使用未签名目录，请仅添加你信任的镜像源（详见[镜像参考](../../reference/images/)）。

## 报告安全漏洞

发现安全漏洞时，请通过 [GitHub 私密安全通告](https://github.com/pgsty/barn/security/advisories/new)或发送邮件至 [repo@pigsty.cc](mailto:repo@pigsty.cc) 私下报告，并附上 `barn --json version`、宿主系统与架构以及脱敏后的最小复现步骤。支持范围与披露流程见 [`SECURITY.md`](https://github.com/pgsty/barn/blob/main/SECURITY.md)；日常功能缺陷请提交至 [GitHub Issues](https://github.com/pgsty/barn/issues)。
