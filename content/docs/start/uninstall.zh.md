---
title: 卸载与清理环境
description: 安全移除 Farrow deployment、集成、镜像、宿主网络与默认状态目录。
weight: 60
icon: fa-solid fa-trash-can
---

本页会删除虚拟机与本地数据。先确认当前状态，不要在仍需保留 Farrow VM 时继续：

```bash
farrow st
```

## 1. 删除 deployment

彻底删除节点、持久盘、密钥与 deployment 状态：

```bash
farrow purge
```

这条整套处置命令无需确认；镜像缓存与宿主网络仍然保留。若要保留
持久盘或只删除选中节点，继续使用粒度更细且带确认的 `farrow destroy`。

## 2. 移除可选集成

整体 destroy 已自动移除默认 `farrow` SSH integration。如果使用过自定义 fragment 名称或
`/etc/hosts` 条目：

```bash
farrow ssh-config --remove --name lab
farrow hosts uninstall --json
farrow hosts uninstall --yes
```

未加 `--yes` 的 `--json` 命令只展示 Farrow 标记范围内的计划。确认目标正确后再执行
带 `--yes` 的命令。0.9 候选版的普通终端输出会询问 `[y/N]`，同意后立即卸载；0.8.0 的普通
终端命令仍只展示计划。候选版读取 hosts 计划无需 sudo，实际修改仍需要权限。

## 3. 删除镜像缓存

```bash
farrow image prune --dry-run
farrow image prune --yes
```

Prune 删除未引用的缓存镜像与遗留 staging 文件，但会保护已应用 deployment、当前
Catalog 和已注册本地别名引用的镜像，因此不等于清空全部缓存。后面的可选状态目录
清理会一并删除剩余缓存。

## 4. 卸载宿主网络

```bash
farrow network uninstall --json
farrow network uninstall --yes
```

第一条 JSON 命令只展示归属明确的删除计划，但可能需要 sudo 读取受保护的网络状态。
只要仍有 VM 接入，网络卸载就会拒绝执行。宿主网络由用户共享；清理自己的部署不代表
其他用户的 VM 也已停止。

## 5. 清理源码安装残留

宿主网络卸载会保留可独立使用的 hosts helper。仅在确认不再使用 Farrow 后，删除下面的准确路径：

```bash
sudo rm -f -- /opt/farrow/libexec/farrow-hosts-helper
sudo rmdir /opt/farrow/libexec /opt/farrow
```

若使用默认状态目录，并且前面所有步骤均已完成，可最后删除空余状态：

```bash
(
  set -eu
  test -z "${FARROW_HOME:-}"
  farrow_state_root="$(cd "$HOME" && pwd -P)/.farrow"
  test ! -L "$farrow_state_root"
  if test -d "$farrow_state_root"; then
    printf 'removing exact state root: %s\n' "$farrow_state_root"
    find "$farrow_state_root" -depth -delete
  fi
)
```

此段命令在设置了 `FARROW_HOME` 或默认路径为符号链接时停止。自定义状态目录必须
另行核对，不要把目标替换为 `$HOME`、`/`、工作区根目录或未经确认的路径。删除后不要
再次运行生命周期命令来验证目录不存在，因为命令可能重新创建锁目录。

QEMU 可能被其他工具共用，默认不要卸载。只有确定没有其他用途时，macOS 才执行：

```bash
brew uninstall qemu
```

检查网络与默认状态目录：

```bash
farrow network status --json
test ! -e "$HOME/.farrow" && echo 'no Farrow state'
```

卸载后的网络预期报告缺失或未就绪，应检查具体结果，不应要求退出码为零。不要把
`bridge100` 是否消失当作依据：macOS 决定桥接名称，其他软件也可能使用 vmnet 桥。

Archive、Homebrew、DEB 或 RPM 安装的 Farrow 二进制应使用对应安装渠道移除；源码构建生成的
`bin/` 只是工作区构件，与上述宿主状态无关。
