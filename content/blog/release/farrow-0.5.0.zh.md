---
title: "Farrow 0.5.0：显式处置、显式仓库、可复现镜像"
linkTitle: Farrow 0.5.0
description: 无需确认的整套实验室处置、全球与中国仓库显式选择、无隐藏工件回退，以及八目标官方镜像候选流水线。
date: 2026-09-03
weight: 2
categories: [发布]
tags: [Farrow 0.5.0, QEMU, 镜像, 供应链, 发布]
icon: fa-solid fa-rocket
---

> [!NOTE]
> 本页记录 0.5.0。0.7.0 已增加官方镜像源故障回退，未发布的 0.9 候选移除了
> `rm` 别名。请按安装版本阅读[当前命令行说明](../../../docs/reference/cli/)。

Farrow 0.5.0 是被 0.6.0 取代的公开 pre-1.0 发布。它为一次性实验室加入明确处置命令，让仓库地域
成为操作者的显式选择，并提供可复现的下一代官方 Guest 镜像准备路径。Pigsty Inventory
契约、Deployment 状态格式与内嵌 Catalog revision `2026082903` 均未变化。

## 变化

- `farrow purge`（别名 `farrow rm`）无需确认，删除完整 Deployment、持久数据盘、
  Deployment 密钥与状态，以及默认 SSH Fragment；已校验镜像缓存与宿主全局网络仍然保留。
  没有 Deployment 时幂等成功，无法证明身份的遗留节点工件仍会 Fail-closed。
- Release 二进制默认使用 `https://repo.pigsty.io/farrow`。仅有长参数的 `--mirror` 选择
  `https://repo.pigsty.cc/farrow`；优先级依次为 `--repo`、`--mirror`、`FARROW_REPO`、
  全球默认仓库。两个官方根都保持规范的签名 Catalog 信任。
- Catalog Upstream URL 只用于溯源，不再作为回退。选定仓库必须包含 Catalog 指定的准确
  qcow2，否则拉取会失败，并提示显式选择其他仓库或导入本地镜像。
- 源码新增 Debian 12/13、Rocky Linux 8/9 在 amd64/arm64 上的摘要锁定离线 Builder。
  它记录准确软件包闭包、SBOM、Provenance 与 `testing` Manifest，并可组装未签名候选仓库，
  留待真机 Smoke 与签名审查。
- 固定的源码/发布工具链升级到 Go 1.27.1、GoReleaser 2.18.0、golangci-lint 2.13.2
  与当前选定的 Go 模块版本。

## 镜像边界

八目标矩阵修复具体 Guest 前置条件：Debian 12/13 加入显式 XFS 数据盘所需的 XFS 用户态
工具；Rocky Linux 8 加入 `/usr/bin/python3`、有效的 SSH Drop-in Include 与干净网卡命名
状态；Rocky Linux 9 同样清理旧网络状态。

这些是 Candidate 构建输入，不是新发布的 Catalog 工件。每份结果在完成真机启动/就绪
Smoke、双构建比较、生产签名、上传与 Catalog 发布前，始终保持未签名和 `testing`。

## 升级与处置

从 0.4.0 升级无需迁移状态、Inventory 或 Catalog，现有缓存镜像仍可使用。新的下载默认走
全球仓库，除非用 `--mirror`、`--repo` 或 `FARROW_REPO` 选择其他根。

`purge` 刻意设计为无交互操作，会不可逆删除 Deployment 磁盘与密钥。若要保留持久盘或只
删除部分节点，请继续使用带确认的 `farrow destroy`。

## 验证边界

Release 源码 Commit `fc85b65ff6a24b0933b56ae1179be9ada2ba91b1` 已通过完整本地源码
门禁：模块与 Shell 检查、单测与 Race、Vet、Staticcheck、deadcode、errcheck、
`govulncheck`、四目标构建、模拟镜像流水线边界、Installer 测试与准确依赖许可证校验；
GoReleaser 2.18.0 也接受了发布配置。

Tag 工作流会独立重复这些检查，并在公开 Pre-release 前构建、验证全部 Archive、原生
Package、SBOM、Formula、Installer、Release Metadata 与 Checksum。源码门禁不会自动继承
新的真机 VM 生命周期证据，也不代表镜像 Candidate 已发布。

## 安装或升级

从 [Farrow 0.5.0 GitHub Release](https://github.com/pgsty/farrow/releases/tag/v0.5.0)
下载 Installer 与资产：

```bash
curl -fLO https://github.com/pgsty/farrow/releases/download/v0.5.0/install.sh
chmod +x install.sh
FARROW_VERSION=0.5.0 ./install.sh
farrow version
farrow doctor
```

同一 Pre-release 附带 Homebrew Formula 与 amd64/arm64 DEB/RPM 软件包。
