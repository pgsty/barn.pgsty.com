---
title: 安装 Barn
linkTitle: 安装
description: 在 macOS 或 Linux 上安装 Barn 0.9.1，检查系统要求，并了解升级方式。
weight: 5
icon: fa-solid fa-download
aliases: [/docs/start/upgrade/]
---

Barn 0.9.1 提供 macOS 与 Linux 的 **arm64、amd64** 归档，以及 Linux DEB、RPM 软件包。
安装后，以普通用户运行 Barn，再继续 [Linux 快速上手](../tutorial/)或 [macOS 虚拟机教程](../macos/)。

[Barn 0.9.1](https://github.com/pgsty/barn/releases/tag/v0.9.1) 沿用预发布频道。
发行资产包含 CLI 与 hosts helper；`Barn.app` 需要[从源码构建](../source-build/#mac-component)。

安装时显式选择版本。Barn 的发布流程将 1.0.0 之前的版本标为 GitHub 预发布；
`releases/latest` 不包含它们，安装器也不会自动回退。

| 组件 | 用途 | 0.9.1 下载是否包含 |
|---|---|---|
| `barn` | 管理 Linux 与 macOS 虚拟机生命周期的 Go CLI | 四种平台归档及 Linux 软件包均包含 |
| `barn-hosts-helper` | 管理宿主名称集成的受限辅助程序 | 与匹配的 CLI 配套分发 |
| `Barn.app` | Virtualization.framework 运行器与 macOS 客机桌面 | 0.9.1 发行资产不包含；从 `v0.9.1` 源码构建 |

Linux 客机使用 QEMU，不需要 Mac 原生 App。App 不替代 CLI，也不包含 QEMU、
macOS 恢复镜像或虚拟机磁盘。

## 安装发行版本

运行 Barn 的电脑称为**宿主**。按其操作系统选择安装方式：macOS 推荐使用 Homebrew，Linux 使用下载安装脚本。

{{< tabs group="barn-install" default="macos" label="宿主操作系统" >}}
{{< tab label="macOS" value="macos" >}}

使用 [Homebrew](https://brew.sh/) 安装 Barn 及 QEMU 依赖：

```bash
brew install pgsty/infra/barn
barn version
```

请在普通用户的终端中运行 `brew`，无需 sudo。0.9.1 的
[Homebrew 配方](https://github.com/pgsty/homebrew-infra/blob/main/Formula/barn.rb)
安装 CLI 与 hosts helper，不包含 `Barn.app`。运行 macOS 客机还需要 Apple Silicon、
macOS 27+，以及从 `v0.9.1` 标签构建的原生组件，详见 [Mac 安装说明](../macos/#install)。

{{< /tab >}}
{{< tab label="Linux" value="linux" >}}

下载安装脚本并指定版本。脚本会自动选择 amd64 或 arm64 归档，验证 SHA-256，
安装到 `~/.local/bin`，无需 sudo：

```bash {wrap=true}
curl -fLO https://github.com/pgsty/barn/releases/download/v0.9.1/install.sh
BARN_VERSION=0.9.1 bash install.sh
export PATH="$HOME/.local/bin:$PATH"
barn version
```

将 PATH 设置加入 Shell 启动文件，例如 Bash 的 `~/.bashrc`。安装器会把 CLI 与配套的 hosts helper 保存在同一个版本目录中。保持该目录布局。

如果不使用 Homebrew，macOS 也可以运行同样的固定版本安装命令。此脚本安装 Barn，
Linux 客机所需的宿主依赖另由 `barn setup` 准备。

{{< /tab >}}
{{< /tabs >}}

安装后用 `barn version` 核对版本。安装程序本身不会启动虚拟机。交互式 `barn up`
可以准备 Linux 客机所需的宿主依赖与网络，在需要提权时请求管理员权限。
可以先用 `barn setup --dry-run` 查看计划。始终以普通用户运行 Barn。

## 系统要求

| 客机 | 宿主 | 运行依赖 |
|---|---|---|
| Linux | macOS，Apple Silicon 或 Intel | QEMU 8.2.1+、HVF |
| Linux | Linux，arm64 或 amd64 | QEMU 6.2+、可用的 KVM、NetworkManager 或 systemd-networkd |
| macOS 27 | Apple Silicon、macOS 27+，已登录桌面会话 | Barn.app 原生组件，无需 QEMU |
{.platform-table}

一台默认 Linux 虚拟机使用 **2 vCPU、4 GiB 内存**，配有 64 GiB 根盘和 128 GiB
测试数据盘。这些是虚拟容量，磁盘文件随写入增长。请同时为宿主保留内存与磁盘空间。

首次创建 Mac 虚拟机约需 **65 GiB 可用磁盘空间**，用于 Apple 恢复镜像、已安装的
基础系统和初始写入。默认配置为 4 vCPU、8 GiB 内存。首个基础镜像的磁盘为 100 GiB。除非用 `--disk` 另行指定，否则后续新虚拟机沿用已准备基础镜像的容量。
客机相关限制见[平台与限制](../../about/status/)。

## 其他安装方式

### Linux 软件包

以下示例使用 **amd64**；ARM64 宿主请选择对应的 `linux_arm64` 文件。
软件包已声明 QEMU、固件和 SSH 依赖。

```bash {tab="Debian / Ubuntu" group="linux-package" value="deb"}
barn_release=https://github.com/pgsty/barn/releases/download/v0.9.1
curl -fLO "$barn_release/barn_0.9.1_linux_amd64.deb"
sudo apt install ./barn_0.9.1_linux_amd64.deb
barn version
```

```bash {tab="RHEL / Fedora" value="rpm"}
barn_release=https://github.com/pgsty/barn/releases/download/v0.9.1
curl -fLO "$barn_release/barn_0.9.1_linux_amd64.rpm"
sudo dnf install ./barn_0.9.1_linux_amd64.rpm
barn version
```

### 手动安装归档

从 [GitHub 的 Barn 0.9.1 发行页](https://github.com/pgsty/barn/releases/tag/v0.9.1)
下载匹配宿主的归档，命名为 `barn_0.9.1_<os>_<arch>.tar.gz`，其中 `os` 为
`darwin` 或 `linux`。解压之前，用同一发行版本的 `checksums.txt` 核对归档。
例如 Apple Silicon：

```bash
barn_release=https://github.com/pgsty/barn/releases/download/v0.9.1
curl -fLO "$barn_release/barn_0.9.1_darwin_arm64.tar.gz"
curl -fLO "$barn_release/checksums.txt"
shasum -a 256 barn_0.9.1_darwin_arm64.tar.gz
```

将完整摘要与 `checksums.txt` 中同名文件的条目比较。确认一致后，再解压归档并将其中的 `bin/` 加入 PATH。
保留 `barn`、`barn-hosts-helper` 的打包布局。helper 必须匹配 CLI 内嵌的 SHA-256，不能任意替换。
0.9.1 归档不包含 `Barn.app`；运行 macOS 客机前，需从 `v0.9.1` 标签构建完整原生组件。

### 从源码构建

开发 Barn 或自行构建 Mac 原生组件时，请参考[源码构建](../source-build/)。

## 升级 Barn

从 0.9.0 升级至 0.9.1 时，替换 App 前先停止 Mac 虚拟机，并将 CLI、helper 与 App
一并更新。新 CLI 能识别旧 `Barn Mac.app`，旧 CLI 无法发现 `Barn.app`。
已有虚拟机磁盘与配置保留原位，无需重建虚拟机或更新镜像目录。
应用标识改变后，桌面窗口位置可能重置。详见 [0.9.1 升级说明](/zh/blog/release/0.9.1/)。

沿用原安装方式升级。macOS 上通过 Homebrew 更新：

```bash
brew update
brew upgrade pgsty/infra/barn
barn version
```

Linux 使用安装器时，将版本号改为目标版本后重新执行；使用 DEB/RPM 时，
安装对应的新软件包。随后用 `command -v barn` 和 `barn version` 确认 Shell 实际选择的
程序。升级前阅读[发布说明](/zh/blog/release/)。

Barn 程序、Linux 镜像目录和 macOS 基础镜像分别更新：

| 更新对象 | 操作 |
|---|---|
| Barn 程序 | 安装目标发行版本 |
| Linux 镜像目录 | `barn update`，或 `barn update --mirror` |
| 供新虚拟机使用的 macOS 基础镜像 | `barn mac image update` |

镜像更新会保留已有虚拟机的磁盘。更换客机系统时，请查看对应的 `recreate` 流程，
该操作会替换客机磁盘。替换 Mac 原生组件之前，先停止 Mac 虚拟机。

下载与 PATH 问题见[故障排查](../troubleshooting/#下载与-path-问题)，
移除程序与环境见[卸载与清理](../uninstall/)。
