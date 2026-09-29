---
title: "Farrow 0.3.0：显式 Catalog 与可操作的就绪诊断"
linkTitle: Farrow 0.3.0
description: 显式镜像 Catalog 更新、逐节点 Bootstrap 诊断、发行版原生 Guest 网卡名与更小的 CLI。
date: 2026-09-02
weight: 2
categories: [发布]
tags: [Farrow 0.3.0, QEMU, Catalog, 就绪, 发布]
icon: fa-solid fa-rocket
---

Farrow 0.3.0 是被 0.4.0 取代的公开 pre-1.0 发布。它移除隐式 Catalog 刷新，把 Guest Bootstrap
失败变成可操作的逐节点结果，并在不改变 Pigsty Inventory 与固定 IP Deployment 模型的
前提下简化 CLI。

## 变化

- `up`、`plan` 与普通 `image` 命令只使用一份当前本地 Catalog 快照，绝不隐式获取
  Catalog 元数据。`farrow update` 显式获取配置仓库；`image sync` 激活精确 URL 或文件。
- Guest Bootstrap 原子写入失败阶段。部分操作报告每个失败节点、阶段与错误；就绪失败
  会直接指向 `farrow logs <node>`。
- 已运行 Guest 可在不重启 QEMU 的情况下复查。生命周期部分失败后，SSH 客户端配置仍会
  根据全部 committed 节点重建。
- Netplan 按确定性 MAC 匹配且不再重命名接口。`vm_disks[].fs: auto` 优先 XFS，必要时
  回退到 ext4。
- 删除冗余 `ss` 命令与含义模糊的根/参数短写；`image reset` 取代
  `reset-manifest`，旧名称仍是别名。

## 验证边界

源码 Commit `da6d02426da93c677c94c67fec4eb4fcecf4766a` 通过完整本地源码门禁与
GoReleaser 全量 Snapshot：单测与 Race、Vet、Staticcheck、`govulncheck`、四目标构建、
镜像流水线与 Installer 边界、Archive/Package 一致性、依赖许可证、SBOM 和 Linux 原生
Package 校验。Tag 工作流在公开 Release 前重复执行了这些检查。

本发布不声称新增真机 VM Replay。带日期的 macOS arm64/HVF 与 Ubuntu amd64/KVM 证据
仍列在[状态页](../../../docs/about/status/)；源码、打包、发布与真机证据继续作为独立门禁。

## 安装或升级

从 [Farrow 0.3.0 GitHub Release](https://github.com/pgsty/farrow/releases/tag/v0.3.0)
下载 Installer 与资产：

```bash
curl -fLO https://github.com/pgsty/farrow/releases/download/v0.3.0/install.sh
chmod +x install.sh
FARROW_VERSION=0.3.0 ./install.sh
farrow version
farrow doctor
```

同一 Pre-release 附带 Homebrew Formula 与 amd64/arm64 DEB/RPM 软件包。现有 0.1/0.2
Deployment 与 Catalog 状态仍可读取；Catalog 刷新从本版本开始始终显式。
