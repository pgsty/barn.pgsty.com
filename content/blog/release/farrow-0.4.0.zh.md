---
title: "Farrow 0.4.0：一条命令、能用的数据盘、统一的输出"
linkTitle: Farrow 0.4.0
description: 首次运行只需一条命令，默认数据盘在所有镜像上可用，就绪失败直接给出原因，全部命令统一输出风格。
date: 2026-09-02
weight: 1
categories: [发布]
tags: [Farrow 0.4.0, QEMU, 体验, 发布]
icon: fa-solid fa-rocket
---

Farrow 0.4.0 是被 0.5.0 取代的公开 pre-1.0 发布。它把首次运行压缩为一条命令，修复了 Debian 与
Ubuntu 镜像上的默认数据盘，并让全部命令使用同一套输出风格。Pigsty Inventory 格式、
固定 IP Deployment 模型、状态布局与内嵌 Catalog revision `2026082903` 均未变化。

## 变化

- 在终端里，固定 IP 网络尚未安装时 `farrow up` 会自己执行 `farrow setup`：展示 setup
  计划、在特权步骤前确认，然后继续。`farrow init` 的下一步提示改为 `farrow up`。
- `vm_disks[].fs` 默认值改为 `auto`：空白磁盘在 Guest 有 `mkfs.xfs` 时格式化为 XFS，
  否则为 ext4，与 Pigsty 的 Vagrant 流程一致。旧的 `xfs` 默认值在不带 xfsprogs 的
  Debian 与 Ubuntu 镜像上会失败。按旧默认值创建的 Deployment 不会被报告为漂移，持久盘
  也保持兼容。
- Guest 的错误标记携带失败命令的最后一行输出，`up` 会报告
  `guest bootstrap failed during data-disks: xfs requested but mkfs.xfs is unavailable`，
  而不是只有退出码。
- 生命周期命令与 `status` 打印节点表，`up` 成功后给出 `next: farrow ssh <node>`。
  没有变化时 `plan` 与 `validate` 只打印一行；`image list`、`network status`、`doctor`
  与预检错误使用没有机器码的自然语句；`spec hash` 等内部信息只在 `--json` 中出现。
  未知节点名的错误会列出现有节点。
- `farrow ssh <node> -- 'df -h /data; id'` 会把远程命令按 OpenSSH 的方式原样传递。

## 升级说明

由 0.3.0 或更早版本创建、`/data` 从未挂载的 d13、d12 或 Ubuntu 节点，运行一次
`farrow recreate <node>` 即可；这些镜像上磁盘会格式化为 ext4，Enterprise Linux 镜像上
为 XFS。在没有终端的自动化中，对未准备好的宿主机运行 `up` 之前仍需先执行
`farrow setup --yes`。

## 验证边界

源码 Commit `8ecb8476c7dbc934d8cbbee935ac53884d00fcdb` 通过完整本地源码门禁：单测与
Race、Vet、Staticcheck、deadcode、errcheck、`govulncheck`、Shell 与模块检查、四目标
构建、镜像流水线与 Installer 边界、依赖许可证。Tag 工作流在公开 Release 前重复执行了
这些检查，并构建、验证了全部 Archive、原生 Package、SBOM 与 Installer。

新的首次运行路径（`up` 自动执行 `setup`）有单元测试覆盖，但本次发布前未在全新宿主机上
重放。带日期的 macOS arm64/HVF 与 Ubuntu amd64/KVM 证据仍列在[状态页](../../../docs/about/status/)；
源码、打包、发布与真机证据继续作为独立门禁。

## 安装或升级

从 [Farrow 0.4.0 GitHub Release](https://github.com/pgsty/farrow/releases/tag/v0.4.0)
下载 Installer 与资产：

```bash
curl -fLO https://github.com/pgsty/farrow/releases/download/v0.4.0/install.sh
chmod +x install.sh
FARROW_VERSION=0.4.0 ./install.sh
farrow version
farrow doctor
```

同一 Pre-release 附带 Homebrew Formula 与 amd64/arm64 DEB/RPM 软件包。现有 Deployment 与
Catalog 状态仍可读取。
