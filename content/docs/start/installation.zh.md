---
title: 安装 Barn
linkTitle: 安装
description: 在 macOS 或 Linux 上安装 Barn 0.9.2，检查系统要求，并了解升级方式。
weight: 5
icon: fa-solid fa-download
aliases: [/docs/start/upgrade/]
---

Barn 0.9.2 提供 macOS 与 Linux 的 **arm64 和 amd64** 归档包，以及 Linux DEB 和 RPM 软件包。请始终以普通 Unix 用户身份运行 `barn`；安装完成后，可继续阅读 [Linux 快速上手](../tutorial/)或 [macOS 虚拟机教程](../macos/)。

> [!NOTE]
> [Barn 0.9.2](https://github.com/pgsty/barn/releases/tag/v0.9.2) 与所有 `0.x` 版本一样通过 GitHub Pre-release 渠道发布，`releases/latest` 不会命中该版本，因此运行安装脚本时请显式指定 `0.9.2`。Apple Silicon 归档包含配套的 `barn`、`barn-hosts-helper` 与 macOS 原生应用包 `Barn.app`，均经过 Developer ID 签名与 Apple 公证。只有[从源码构建](../source-build/)时才需要 Go 和 Xcode。

| 组件 | 用途 | 0.9.2 发行包是否包含 |
|---|---|---|
| `barn` | 管理 Linux 实验环境与 macOS 虚拟机生命周期的 Go CLI | 四种平台归档及 Linux 软件包均包含 |
| `barn-hosts-helper` | 负责 `/etc/hosts` 主机名集成的受限辅助程序 | 与同版本 CLI 配套打包 |
| `Barn.app` | 基于 `Virtualization.framework` 的原生运行器与 macOS 客机桌面 | Darwin arm64 归档与 Apple Silicon Homebrew 安装包含；仅 macOS 客机需要 |

## 安装发行版本

运行 Barn 的电脑称为**宿主**。请按宿主操作系统选择安装方式：macOS 推荐使用 Homebrew，Linux 推荐使用安装脚本。

{{< tabs group="barn-install" default="macos" label="宿主操作系统" >}}
{{< tab label="macOS" value="macos" >}}

在普通用户终端中使用 [Homebrew](https://brew.sh/) 安装 Barn 及 QEMU 依赖：

```bash
brew install pgsty/infra/barn
barn version
```

在 Apple Silicon 上，`0.9.2` 的 [Homebrew Formula](https://github.com/pgsty/homebrew-infra/blob/main/Formula/barn.rb) 还会将 `Barn.app` 安装至 `libexec`，CLI 会自动找到它。macOS 27+ 用户可运行 `barn mac doctor`，随后按 [Mac 指南](../macos/#install)创建客机。Intel Mac 使用 CLI 与 helper 运行 Linux 客机。

{{< /tab >}}
{{< tab label="Linux" value="linux" >}}

下载 `install.sh` 并传入 `BARN_VERSION=0.9.2`。脚本会自动识别 `amd64` 或 `arm64` 架构，校验归档 SHA-256，并将 CLI 与配套的 `barn-hosts-helper` 安装到 `~/.local/bin`（无需 `sudo`）：

```bash {wrap=true}
curl -fLO https://github.com/pgsty/barn/releases/download/v0.9.2/install.sh
BARN_VERSION=0.9.2 bash install.sh
export PATH="$HOME/.local/bin:$PATH"
barn version
```

请将 `export PATH="$HOME/.local/bin:$PATH"` 加入 `~/.bashrc` 或 `~/.zshrc` 等 Shell 启动文件，并保留 `.barn-releases/` 下的版本化目录结构。如果你在 macOS 上不想使用 Homebrew，也可以直接运行这段安装命令，后续再通过 `barn setup` 配置 QEMU 与宿主网络依赖。

{{< /tab >}}
{{< /tabs >}}

首次交互式执行 `barn up` 时，Barn 会自动检查 Linux 客机所需的宿主依赖与私有网络，列出待执行的变更明细，并在必要时请求管理员权限（`sudo`）。你也可以先运行 `barn setup --dry-run` 预览宿主准备计划。

## 系统要求

| 客机 | 宿主 | 运行时依赖 |
|---|---|---|
| Linux | macOS（Apple Silicon 或 Intel） | QEMU 8.2.1+、HVF |
| Linux | Linux（arm64 或 amd64） | QEMU 6.2+、可用的 KVM、NetworkManager 或 systemd-networkd |
| macOS 27 | Apple Silicon、macOS 27+、已登录图形桌面会话 | 原生应用包 `Barn.app`（无需 QEMU） |
{.platform-table}

一台默认规格的 Linux 虚拟机分配 **2 vCPU 与 4 GiB 内存**，搭配按需增长的 `qcow2` 稀疏磁盘（64 GiB 根盘与 128 GiB 测试数据盘）。

首次创建 macOS 虚拟机约需 **65 GiB 可用磁盘空间**，用于存放 Apple 恢复镜像（约 25 GiB）、已安装的基础镜像（约 27 GiB）以及初始写入数据。Mac 虚拟机默认分配 4 vCPU、8 GiB 内存和 100 GiB APFS 克隆磁盘；后续新建虚拟机除非通过 `--disk` 另行指定，否则默认沿用已有基础镜像的磁盘容量。各客机的具体约束见[平台与限制](../../about/status/)。

## 其他安装方式

### Linux 软件包

DEB 与 RPM 软件包已声明 QEMU、UEFI 固件和 OpenSSH 依赖。ARM64 宿主请将文件名中的 `amd64` 替换为 `arm64`：

```bash {tab="Debian / Ubuntu" group="linux-package" value="deb"}
barn_release=https://github.com/pgsty/barn/releases/download/v0.9.2
curl -fLO "$barn_release/barn_0.9.2_linux_amd64.deb"
sudo apt install ./barn_0.9.2_linux_amd64.deb
barn version
```

```bash {tab="RHEL / Fedora" group="linux-package" value="rpm"}
barn_release=https://github.com/pgsty/barn/releases/download/v0.9.2
curl -fLO "$barn_release/barn_0.9.2_linux_amd64.rpm"
sudo dnf install ./barn_0.9.2_linux_amd64.rpm
barn version
```

### 手动安装归档

从 [GitHub Barn 0.9.2 发布页](https://github.com/pgsty/barn/releases/tag/v0.9.2)下载对应宿主系统的 `barn_0.9.2_<os>_<arch>.tar.gz`（`darwin` 或 `linux`，`arm64` 或 `amd64`）与 `checksums.txt`，解压前先校验 SHA-256：

```bash
barn_release=https://github.com/pgsty/barn/releases/download/v0.9.2
curl -fLO "$barn_release/barn_0.9.2_darwin_arm64.tar.gz"
curl -fLO "$barn_release/checksums.txt"
shasum -a 256 -c checksums.txt --ignore-missing
```

校验通过后解压归档，将其中的 `bin/` 目录加入 `PATH`。请保持发行包目录结构完整：`barn` 与 `barn-hosts-helper` 必须配套，Darwin arm64 归档还包含 `bin/Barn.app`。CLI 调用 helper 前会核对其内嵌的 SHA-256 摘要，并自动发现旁边的 App。

### 从源码构建

如需参与开发或自行编译 macOS 原生应用包 `Barn.app`，请参阅[从源码构建](../source-build/)。

## 升级 Barn

升级至 **0.9.2** 前，请先停止正在运行的 Mac 虚拟机，并通过原安装渠道同步替换 CLI、`barn-hosts-helper` 与 `Barn.app`。虚拟机磁盘与配置会保留，无需重建。请更新脚本，在 SSH/exec 远端命令前加入 `--`，例如 `barn exec meta -- hostname`。详情见 [0.9.2 发布说明](/zh/blog/release/0.9.2/)。

请沿用最初的安装方式执行升级。macOS Homebrew 用户可直接运行：

```bash
brew update
brew upgrade pgsty/infra/barn
barn version
```

Linux 用户只需指定新版本号重新运行 `install.sh`，或安装新版 `.deb` / `.rpm` 软件包，随后通过 `command -v barn` 和 `barn version` 确认当前生效的二进制路径。

Barn 将程序升级与客机镜像更新解耦，避免升级工具时意外改动现有虚拟机的系统版本：

| 更新对象 | 命令 | 对现有虚拟机的影响 |
|---|---|---|
| Barn CLI、helper 与随包 App | 重新安装或 `brew upgrade` | 保留所有现有虚拟机磁盘与状态 |
| Linux 镜像目录 | `barn update`（或 `barn update --mirror`） | 仅对新建或显式 `recreate` 的节点生效 |
| macOS 基础镜像 | `barn mac image update` | 准备新基础镜像；已有虚拟机需执行 `barn mac recreate NAME --update` 才会切换 |

如遇下载代理或 `PATH` 问题，请参阅[故障排查](../troubleshooting/#下载与-path-问题)；如需移除程序与宿主状态，请参阅[卸载与清理](../uninstall/)。
