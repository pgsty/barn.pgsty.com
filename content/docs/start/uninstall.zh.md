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
farrow hosts uninstall
farrow hosts uninstall --yes
```

第一条 `hosts uninstall` 只展示 marker-owned 计划，确认目标正确后再执行第二条。

## 3. 删除镜像缓存

```bash
farrow image prune --dry-run
farrow image prune --yes
```

Prune 只删除未被已应用 deployment 引用的镜像与遗留 staging 文件。

## 4. 卸载宿主网络

```bash
farrow network uninstall
farrow network uninstall --yes
```

第一条只展示归属明确的删除计划。只要仍有 VM 接入，网络卸载就会拒绝执行。

## 5. 清理源码安装残留

宿主网络卸载会保留可独立使用的 hosts helper。仅在确认不再使用 Farrow 后，删除下面的准确路径：

```bash
sudo rm -f -- /opt/farrow/libexec/farrow-hosts-helper
sudo rmdir /opt/farrow/libexec /opt/farrow
```

若使用默认状态目录，并且前面所有步骤均已完成，可最后删除空余状态：

```bash
farrow_state_root="$(cd "$HOME" && pwd -P)/.farrow"
printf 'removing exact state root: %s\n' "$farrow_state_root"
test "$(basename "$farrow_state_root")" = '.farrow'
find "$farrow_state_root" -depth -delete
```

不要把这段命令改成 `$HOME`、`/`、工作区根目录或未经核对的 `FARROW_HOME`。

QEMU 可能被其他工具共用，默认不要卸载。只有确定没有其他用途时，macOS 才执行：

```bash
brew uninstall qemu
```

最后检查是否归零：

```bash
farrow st || true
ifconfig bridge100 2>/dev/null || echo 'no Farrow bridge'
test ! -e "$HOME/.farrow" && echo 'no Farrow state'
```

Archive、Homebrew、DEB 或 RPM 安装的 Farrow 二进制应使用对应安装渠道移除；源码构建生成的
`bin/` 只是工作区构件，与上述宿主状态无关。
