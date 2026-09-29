---
title: 当前状态
description: Barn 0.9.0 发布候选、当前验证结果与发行前检查。
weight: 20
icon: fa-solid fa-list-check
---

Barn 0.9.0 是**尚未发布的候选版本**。源码检查、本地构建、软件包、CI、发行和线上文档
分别核验。安装方式见[快速上手](../../start/tutorial/#安装)。

## 文档基线 {#documentation-baseline}

| 对象 | 当前身份 | 使用方式 |
|---|---|---|
| 程序与当前文档 | Barn 0.9.0 发布候选 | 从源码构建；发行包命令在发布后使用。 |
| CLI 与配置 | `barn`、`barn.yml`、`BARN_*` | 使用版本相关说明前先检查 `barn version`。 |
| 状态与宿主资源 | `~/.barn`、Barn 网络与 helper | 每个用户一套 Linux 部署；macOS 客机使用独立状态。 |
| 镜像仓库 | 官方入口的 `/barn` 前缀 | 已于 2026-09-29 发布签名 Catalog `2026092901` 并完成公网核验，见下方镜像记录。 |

最终发布提交、制品摘要与安装渠道将在完成发布和下载核验后记录。

## macOS 客机 {#macos-guests}

`barn mac` 在 Apple 芯片上运行 macOS 27 虚拟机，见[教程](../../start/macos/)与
[命令参考](../../reference/mac/)。组件名称为 `Barn Mac.app`，签名标识为
`io.pgsty.barn.mac-runner`，状态独立保存在 `$BARN_HOME/mac`。

2026-09-29，本地 CLI/hosts-helper 测试、原生 Bridge/镜像/退出提示/菜单测试、runner 编译、
ad-hoc 签名验证与 `probe` 通过。这些检查没有启动 VM，不代表完整 Mac 实机生命周期验收。

## 发行前仍需核验

- 最终 Barn 提交的完整源码、归档、DEB/RPM、安装器与跨平台检查；
- 全新宿主准备、Linux/macOS VM 生命周期与清理；
- Mac Developer ID 签名与公证；
- Barn 0.9.0 的发布与下载核验，包括 Homebrew。

## Linux 镜像 Catalog：2026-09-29

两个官方 `/barn` 入口均已发布 Catalog `2026092901`：9 个系列、45 个工件，完整保留
原有 37 个工件。Debian 12 为 `20260923.2610.1`，Ubuntu 22.04/24.04 为
`20260926.0.0`，Ubuntu 26.04 为 `20260927.0.0`，均覆盖 amd64、arm64。
Debian 13 保持现版。

8 个新镜像使用当前 Barn cloud-init，通过原生 KVM/HVF 的 UEFI 启动、SSH、双网卡、
UID/GID 88、locale 与 XFS 数据盘读写检查。Debian 12 上游原版仍需离线补齐 XFS 工具
和 `en_US.UTF-8`；Ubuntu 保留 Canonical 原始字节。此次采用隔离的 QEMU user 网络，
完整宿主网络及生命周期验收仍按上文范围独立执行。

内嵌、本地、LAN 与公网 Catalog 字节一致。两个公开入口均通过签名校验，以及隔离
客户端从 `2026092001` 的实际升级。每端 8 个新对象通过尺寸和首尾 Range/If-Range
检查；COS CRC64、R2 分片 ETag 与本地完整文件重算结果一致。R2 首轮 Range 返回
200 的记录保留为证据；刷新新对象缓存后，全部复测返回预期的 206 和正确字节。
版本与更新行为见[镜像参考](../../reference/images/)。
