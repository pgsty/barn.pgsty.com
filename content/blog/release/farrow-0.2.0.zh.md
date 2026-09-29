---
title: "Farrow 0.2.0：选点收敛与发布完整性"
linkTitle: Farrow 0.2.0
description: VPN 感知网络预检、真正的选点扩容、基于 committed state 的集成、CI 多平台构件与 0.1.0 升级边界。
date: 2026-09-01
weight: 2
categories: [发布]
tags: [Farrow 0.2.0, QEMU, macOS, Linux, 发布, 供应链]
icon: fa-solid fa-rocket
---

Farrow 0.2.0 是被 0.3.0 取代的公开 pre-1.0 发布。它保留 0.1.0 引入的 Pigsty Inventory 与
磁盘 Deployment 格式，同时修复最终真机重放中发现的网络与选点收敛边界。

## 主要变化

- `10.0.0.0/8` 等较宽 VPN 排除路由不再误拦 Farrow 自有的
  `10.10.10.0/24`；相同或更具体的外部路由、重叠接口、已占用地址与自有路由缺失
  仍然 Fail Closed。
- `farrow up <node>` 只下载并准备选中的节点。Inventory 中没有 State 的 desired
  peer 显示为 `absent`；SSH/hosts/provision、UUID/端口分配、生命周期与持久盘校验
  使用 committed 节点集合，同时保留后续扩容意图。
- 新 Guest 写入 `# farrow-deployment-host`；添加当前 hosts 行前，会同时清理该标记
  与 0.1.0 发布过的 `# farrow-project-host`。
- 未发布中间版本中的命令取消、结构化输出、确认、`reload`、诊断脱敏、Installer
  保留策略与依赖图精简，全部直接进入 0.2.0。

## 真机与发布证据

准确源码 Commit 在 MonoProxy 在线时完成 macOS arm64/HVF 重放：选点创建 `u24-1`、
SSH、stop/start、增量创建已缓存的 `el9-1`、两节点 SSH、五个显式 absent peer 与
whole destroy 全部通过。在 Ubuntu 26.04 amd64/KVM 上，当前 Linux 二进制无变更地
审计了一套现存四节点 Deployment，并进入控制 Guest。

本地 `make check`、源码 CI 与完整 Packaging Workflow 均通过。Tag Workflow 构建
四平台 Archive、amd64/arm64 DEB 与 RPM、SPDX SBOM、Homebrew Formula、Installer、
Checksum 与 Release Metadata。GitHub Actions 将这些已验证 CI 产物上传为草稿，经检查后公开；不附加应用
签名或 Provenance Bundle。

签名镜像 Catalog 仍为 Revision `2026082903`，包含 9 个 Family 与 27 个分架构工件。
默认仓库继续使用 `https://repo.pigsty.cc/farrow`；`repo.pgsty.com/farrow` 是独立验收
通过的源站/备用入口，不是编译默认值。

## 安装或升级

从 [Farrow 0.2.0 GitHub Release](https://github.com/pgsty/farrow/releases/tag/v0.2.0)
下载 `install.sh` 与对应构件：

```bash
chmod +x install.sh
FARROW_VERSION=0.2.0 ./install.sh
farrow version
farrow doctor
```

0.1.0 Deployment State 可直接读取。保留 VM 在线时运行一次 `farrow status`，可收敛
任何发布前进程出生身份；现有 Guest 在重建时采用新的 `/etc/hosts` 标记。

Farrow 尚未达到 1.0，因此 GitHub 会把 0.2.0 标为 Pre-release。
