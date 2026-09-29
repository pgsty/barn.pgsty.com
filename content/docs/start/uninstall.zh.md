---
title: 卸载与清理
description: 分别移除 Linux 与 macOS 虚拟机，再清理集成、镜像、网络和程序。
weight: 90
icon: fa-solid fa-trash-can
---

Barn 分别管理 Linux 和 macOS 虚拟机。**`barn purge` 只删除 Linux 部署，不删除
Mac 虚拟机。** 完成机器与宿主清理之前，请保留 Barn 程序。

## 选择清理范围

| 目标 | 操作 |
|---|---|
| 释放运行资源，保留磁盘 | `barn stop`；Mac 使用 `barn mac stop --all` |
| 删除某个 Linux 节点 | `barn destroy <node>` |
| 删除 Linux 环境，保留持久盘 | `barn destroy` |
| 删除 Linux 环境、持久盘和密钥 | `barn purge`，无需确认 |
| 删除指定 Mac 虚拟机 | `barn mac destroy <name...>`，需要确认 |

Linux 节点名以 `barn status` 为准，Mac 机器名以 `barn mac ls` 为准。
删除之前备份需要保留的文件。

## 1. 删除机器

丢弃整套 Linux 环境，包括之前保留的持久盘：

```bash
barn purge
```

镜像缓存和宿主网络会保留。对于 Mac 虚拟机，先查看列表，再明确指定要删除的名称。
下面的示例删除 `mac1` 和 `dev`：

```bash
barn mac ls
barn mac destroy mac1 dev
```

Mac 销毁会删除机器的磁盘、凭据和设置，保留共享基础镜像与宿主文件夹。
没有使用 Mac 客机时，跳过 Mac 命令。

## 2. 移除可选集成

整体销毁 Linux 部署时会移除默认 SSH 集成。若另外安装过自定义配置片段或 hosts 条目，
按实际使用情况移除：

```bash
barn ssh-config --remove --name lab
barn hosts uninstall --json
barn hosts uninstall --yes
```

`lab` 是自定义片段名称的示例。JSON 命令预览 hosts 删除计划，`--yes` 执行计划。
移除 Mac SSH 条目：

```bash
barn mac ssh-config --remove
```

这些命令只移除 Barn 管理的条目，保留用户自己的 SSH 配置和 hosts 内容。

## 3. 清理镜像缓存

```bash
barn image prune --dry-run
barn image prune --yes
```

Linux 清理会保护当前镜像目录、已有 VM 和已注册本地别名引用的镜像，
所以删除 VM 后，缓存不一定清空。Mac 镜像使用独立命令：

```bash
barn mac image prune --installers
barn mac image prune --installers --yes
```

Mac 清理会保留仍被机器使用的基础镜像，以及默认基础镜像。

## 4. 移除 Linux 宿主网络

```bash
barn network uninstall --json
barn network uninstall --yes
```

JSON 命令预览计划，读取受保护宿主状态时可能需要 sudo。核对后再执行带 `--yes` 的命令。
网络由多个用户共享，有 VM 接入时不能卸载。Mac 的私有网络会随机器停止而消失，无需单独卸载。

## 5. 移除程序与剩余文件

通过包管理器安装时，使用对应命令：

```bash {tab="Homebrew" group="uninstall" value="brew"}
brew uninstall barn
```

```bash {tab="Debian / Ubuntu" value="deb"}
sudo apt remove barn
```

```bash {tab="RHEL / Fedora" value="rpm"}
sudo dnf remove barn
```

使用用户级安装器时，检查安装目录，默认为 `~/.local/bin`。其中 Barn 管理的文件包括
`barn`、`barn-hosts-helper` 两个符号链接，以及 `.barn-current`、`.barn-releases/`
和 `.barn-install.lock`。全部 VM 停止、集成移除后，再删除这些明确的文件与目录。
手动归档或源码安装则移除对应目录或 PATH 设置。

手动安装的 hosts helper 若仍存在，其路径为 `/opt/barn/libexec/barn-hosts-helper`。
仅在 hosts 集成已卸载、其他 Barn 用户也不再需要时移除。

**只有 Linux 和 Mac 虚拟机都已删除，才能删除 `~/.barn`。** 该目录同时保存两类机器
的状态、凭据、持久盘与镜像缓存，仅执行 Linux `purge` 并不足够。设置了 `BARN_HOME`
时应检查实际路径。机器目录仍存在或 destroy 失败时，先排查原因，不要递归强删。
即使只删除 `~/.barn/mac`，也必须先销毁全部 Mac 虚拟机。

Mac 窗口偏好单独保存在 `~/Library/Preferences/io.pgsty.barn.mac-runner.plist`，
移除它只会重置窗口位置。QEMU 可能被其他工具共用，确认不再需要之前请保留。
