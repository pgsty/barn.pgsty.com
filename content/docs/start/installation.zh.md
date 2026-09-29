---
title: 安装 Barn
linkTitle: 安装
description: 在 macOS 或 Linux 上安装 Barn 0.9.0，检查系统要求，并了解升级方式。
weight: 5
icon: fa-solid fa-download
aliases: [/docs/start/upgrade/]
---

Barn 0.9.0 提供 macOS 与 Linux 的 **arm64、amd64** 归档，以及 Linux DEB、RPM
软件包。以普通用户安装后，继续 [Linux 快速上手](../tutorial/)或 [macOS 虚拟机教程](../macos/)。

## 安装发行版本

按**宿主操作系统**选择安装方式：macOS 推荐使用 Homebrew，Linux 使用下载安装脚本。

{{< tabs group="barn-install" default="macos" label="宿主操作系统" >}}
{{< tab label="macOS" value="macos" >}}

使用 [Homebrew](https://brew.sh/) 安装 Barn 及 QEMU 依赖：

```bash
brew install pgsty/infra/barn
barn version
```

请在普通用户的终端中运行 `brew`，无需 sudo。运行 macOS 客机时，还需要 Apple Silicon、
macOS 27+ 与 `Barn Mac.app`；执行 `barn mac doctor` 检查原生组件，详情见
[Mac 安装说明](../macos/#install)。

{{< /tab >}}
{{< tab label="Linux" value="linux" >}}

下载安装脚本并指定版本。脚本会自动选择 amd64 或 arm64 归档，验证 SHA-256，
安装到 `~/.local/bin`，无需 sudo：

```bash {wrap=true}
curl -fLO https://github.com/pgsty/barn/releases/download/v0.9.0/install.sh
BARN_VERSION=0.9.0 bash install.sh
export PATH="$HOME/.local/bin:$PATH"
barn version
```

将 PATH 设置加入 Shell 启动文件，例如 Bash 的 `~/.bashrc`。安装器会把 CLI 与
配套的 hosts helper 保存在同一个版本目录中；请保持该目录布局。

{{< /tab >}}
{{< /tabs >}}

安装后用 `barn version` 核对版本。安装程序本身不会启动虚拟机。交互式 `barn up`
可以准备 Linux 客机所需的宿主依赖与网络，在需要提权时请求管理员权限。
可先用 `barn setup --dry-run` 查看计划；Barn 本身始终以普通用户运行。

## 系统要求

| 客机 | 宿主 | 运行依赖 |
|---|---|---|
| Linux | macOS，Apple Silicon 或 Intel | QEMU 8.2.1+、HVF |
| Linux | Linux，arm64 或 amd64 | QEMU 6.2+、可用的 KVM、NetworkManager 或 systemd-networkd |
| macOS 27 | Apple Silicon、macOS 27+，已登录桌面会话 | Barn Mac 原生组件，无需 QEMU |
{.platform-table}

一台默认 Linux 虚拟机使用 **2 vCPU、4 GiB 内存**，配有 64 GiB 根盘和 128 GiB
测试数据盘。这些是虚拟容量，文件随写入增长；请同时为宿主保留内存与磁盘空间。

首次创建 Mac 虚拟机约需 **65 GiB 可用磁盘空间**，用于 Apple 恢复镜像、已安装的
基础系统和初始写入。默认配置为 4 vCPU、8 GiB 内存、100 GiB 磁盘。
客机相关限制见[平台与限制](../../about/status/)。

## 其他安装方式

### Linux 软件包

以下示例使用 **amd64**；ARM64 宿主请选择对应的 `linux_arm64` 文件。
软件包已声明 QEMU、固件和 SSH 依赖。

```bash {tab="Debian / Ubuntu" group="linux-package" value="deb"}
barn_release=https://github.com/pgsty/barn/releases/download/v0.9.0
curl -fLO "$barn_release/barn_0.9.0_linux_amd64.deb"
sudo apt install ./barn_0.9.0_linux_amd64.deb
barn version
```

```bash {tab="RHEL / Fedora" value="rpm"}
barn_release=https://github.com/pgsty/barn/releases/download/v0.9.0
curl -fLO "$barn_release/barn_0.9.0_linux_amd64.rpm"
sudo dnf install ./barn_0.9.0_linux_amd64.rpm
barn version
```

### 手动安装归档

从 [GitHub 的 Barn 0.9.0 发行页](https://github.com/pgsty/barn/releases/tag/v0.9.0)
下载匹配宿主的归档，命名为 `barn_0.9.0_<os>_<arch>.tar.gz`，其中 `os` 为
`darwin` 或 `linux`。解压后将其中的 `bin/` 加入 PATH，保留 `barn`、
`barn-hosts-helper` 与随包提供的 `Barn Mac.app` 的相对位置。

### 从源码构建

开发 Barn 或自行构建 Mac 原生组件时，请参考[源码构建](../source-build/)。

## 升级 Barn

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
