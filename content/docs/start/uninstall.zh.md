---
title: 卸载与清理
description: 分别移除 Linux 与 macOS 虚拟机，再清理集成、镜像、网络和程序。
weight: 90
icon: fa-solid fa-trash-can
---

Barn 分别独立管理 Linux 实验环境与 macOS 虚拟机。**`barn purge` 仅删除 Linux 部署，不会删除任何 Mac 虚拟机。** 在完成虚拟机、宿主集成、镜像缓存和宿主网络的清理前，请先保留 `barn` 命令行程序。

## 选择清理范围

| 目标 | 命令 |
|---|---|
| 停止运行中的虚拟机并保留磁盘 | `barn stop`；Mac 虚拟机使用 `barn mac stop --all` |
| 删除单个 Linux 节点 | `barn destroy <node>` |
| 删除 Linux 实验环境，保留持久数据盘 | `barn destroy` |
| 删除 Linux 实验环境、持久数据盘与密钥 | `barn purge`（无需交互确认） |
| 删除指定的 Mac 虚拟机 | `barn mac destroy <name...>`（需输入确认词） |

执行删除前，请先通过 `barn status`（Linux 节点）和 `barn mac ls`（Mac 虚拟机）核对名称，并将需要保留的文件备份到宿主。

## 完整清理步骤

1. **销毁 Linux 与 Mac 虚拟机**

   清空整套 Linux 实验环境（含已保留的持久数据盘与部署密钥）：

   ```bash
   barn purge
   ```

   如果还创建过 macOS 虚拟机，先查看列表再按名称逐一销毁：

   ```bash
   barn mac ls
   barn mac destroy mac1 dev
   ```

2. **移除 SSH 与 `/etc/hosts` 集成**

   整套销毁 Linux 部署时会自动移除默认的 `~/.ssh/barn_config` 集成。若曾安装过自定义名称的 SSH 片段、`/etc/hosts` 主机名条目或 Mac SSH 集成，请依次清理：

   ```bash
   barn ssh-config --remove --name lab
   barn hosts uninstall --json
   barn hosts uninstall --yes
   barn mac ssh-config --remove
   ```

   以上命令仅清理 Barn 写入的受管配置块，不会影响你原有的 `~/.ssh/config` 和 `/etc/hosts` 条目。

3. **清理镜像缓存**

   预览并删除本地缓存的 Linux 与 macOS 镜像文件：

   ```bash
   barn image prune --dry-run
   barn image prune --yes
   barn mac image prune --installers
   barn mac image prune --installers --yes
   ```

4. **卸载 Linux 宿主网络**

   当所有 Linux 虚拟机均已停止并移除后，预览并卸载多用户共享的 Linux 宿主网络（Mac 虚拟机的私有网络会随虚拟机停止自动释放，无需单独卸载）：

   ```bash
   barn network uninstall --json
   barn network uninstall --yes
   ```

5. **卸载 Barn 程序与剩余文件**

   通过包管理器安装的 Barn 可直接用对应命令卸载：

   ```bash {tab="Homebrew" group="uninstall" value="brew"}
   brew uninstall barn
   ```

   ```bash {tab="Debian / Ubuntu" group="uninstall" value="deb"}
   sudo apt remove barn
   ```

   ```bash {tab="RHEL / Fedora" group="uninstall" value="rpm"}
   sudo dnf remove barn
   ```

   - **用户态安装脚本（`install.sh`）**：删除 `~/.local/bin` 下的 `barn`、`barn-hosts-helper`、`.barn-current`、`.barn-releases/` 与 `.barn-install.lock`，并移除 Shell 配置文件中的 `PATH` 设置。
   - **手动归档或源码构建**：停止全部 Mac 虚拟机后，删除解压后的发行目录、`bin/mac` 或单独复制出去的 `Barn.app`（`0.9.0` 版本为 `Barn Mac.app`），以及保存窗口位置的 `~/Library/Preferences/com.pgsty.barn.plist`（`0.9.0` 版本为 `io.pgsty.barn.mac-runner.plist`）。
   - **手动安装的 hosts helper**：若曾手动安装 `/opt/barn/libexec/barn-hosts-helper`，在完成 `barn hosts uninstall --yes` 且确认本机无其他用户使用 Barn 后即可删除。
{.steps}

> [!WARNING]
> **请务必在销毁全部 Linux 和 Mac 虚拟机之后再删除 `~/.barn`（或自定义 `BARN_HOME`）。** `~/.barn` 同时存放两类虚拟机的运行状态、密钥、持久数据盘与基础镜像；若仍有虚拟机目录残留或 `destroy` 报错，请先通过 `barn status` / `barn mac ls` 排查原因，切勿直接递归强删目录。
