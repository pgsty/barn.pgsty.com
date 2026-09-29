---
title: "Farrow 0.6.0：默认 U24，更顺手的本地虚拟机体验"
linkTitle: Farrow 0.6.0
description: 默认 Ubuntu 24.04，准备宿主前即可查看计划，状态更清晰，扩容与重建更可靠。
date: 2026-09-05
weight: 1
categories: [发布]
tags: [Farrow 0.6.0, QEMU, Ubuntu, 发布]
icon: fa-solid fa-rocket
---

Farrow 0.6.0 默认使用 Ubuntu 24.04，完善本地 Pigsty 实验环境的计划、启动、扩容和重建体验。

## 主要变化

- **默认 Ubuntu 24.04。** 新配置与内置镜像目录使用 `u24:stable`。目录版本
  `2026090501` 同时纳入官方仓库已经发布的 Debian 12/13、Rocky Linux 8/9 镜像更新。
- **准备宿主前就能查看计划。** Catalog 镜像的 `plan` 无需先安装 QEMU 或配置网络
  （已注册的 `local-*` 镜像仍需 `qemu-img` 校验缓存），展示准确镜像版本、
  资源总量、待启动节点、变化字段、磁盘影响，并保留自定义 `-f` 路径。
- **状态和错误更清晰。** 状态表直接显示镜像、CPU 与内存，异常节点不再遮住健康节点。
  状态损坏报告具体文件与原因；镜像摘要错误返回 7，SSH 的 255 原样透传；
  `--no-wait` 明确说明跳过就绪检查。
- **先检查，再中断。** 局部 `recreate` 在删除磁盘前发现同伴配置冲突；`reload` 在停机前
  检查启动依赖。停止、销毁和运行时清理沿用现有部署锁，一致地处理状态。
- **节点名称随环境更新。** 启动与删除节点后更新 Guest 内 Farrow 管理的 hosts 和控制节点
  SSH 配置；同名节点重建后可以直接连接，无需手动清理 Guest 的 `known_hosts`。
  用户 SSH 内容及全局选项的作用域得到保留。
- **减少命令行意外。** `init` 自定义路径给出可用的下一步命令，展示参数不再误读选项值，
  整数容量与多文档 YAML 不再被静默截断。`ALL_PROXY`/`all_proxy` 提供代理回退，
  同时尊重专用代理和 `NO_PROXY`。

## 升级说明

升级程序不会自动替换已有磁盘，也不会修改显式选择的镜像。旧配置若依赖隐式 Debian 13
默认值，请先在 `all.vars` 中加入 `vm_image: d13`，再使用 0.6.0 应用配置。执行变更前先看
`farrow plan`；`farrow start` 继续使用已应用状态。

CPU、内存变化仍通过 `recreate` 应用：根盘与非持久数据盘会被替换，持久数据盘保留。
`--no-wait` 跳过就绪检查和 Guest 信息刷新，之后执行 `farrow up` 即可补齐。
脚本应读取 `--json` 或 `--yaml`，避免依赖表格列位置；部分状态失败时仍返回健康节点与
`failures` 数组，退出码为 5。

## 安装或升级

```bash
curl -fLO https://github.com/pgsty/farrow/releases/download/v0.6.0/install.sh
chmod +x install.sh
FARROW_VERSION=0.6.0 ./install.sh
farrow version
farrow doctor
```

同一 Release 提供四个平台归档、amd64/arm64 的 DEB/RPM 软件包和 Homebrew Formula。
0.6.0 沿用 pre-1.0 发布规则，在 GitHub 标记为 Pre-release，安装器需要显式指定版本。
完整步骤见[快速上手](https://farrow.pgsty.com/zh/docs/start/tutorial/)。

## 验证范围

生命周期与 UX 修改通过了 Claude Code Fable 5.1 / xhigh 两轮对抗性审查和完整本地
`make check`。隔离的 macOS arm64/HVF 环境验证了 U24 启动、扩容、控制节点到同伴的
SSH、stop/start、reload、recreate、部分状态失败和缩容；最终的 Guest SSH 作用域修复
另经真实 OpenSSH 有效配置测试验证。

Tag 工作流重复源码检查，并验证归档、软件包、SBOM、安装器、Formula、发布元数据和
校验和。这些结果不代表新增 Linux 宿主 VM 重放、宿主重启测试或完整 Pigsty 安装。
