---
title: 开始使用
linkTitle: 开始使用
description: 用 up 启动 Farrow、用 ssh 进入客机，其余管理、排障、镜像、构建与清理按需阅读。
weight: 10
icon: fa-solid fa-rocket
cascade:
  type: docs
---

安装 Farrow 后，新用户只需按[快速上手](tutorial/)启动测试环境：

```bash
farrow up
farrow ssh
```

没有配置文件且没有已有部署时，交互式 `up` 会生成默认配置；它也能准备缺少的宿主依赖与网络。重复执行
`farrow up` 可重试未完成的客机初始化，不会重启已经健康运行的 VM。无人值守时，
先执行 `farrow setup --yes`，再执行 `farrow up`。

公开软件包状态见[当前状态](../about/status/)；开发者与源码审查者可使用
[从源码构建](source-build/)。

其余内容按任务拆开：

1. [日常管理](operations/)：状态、访问、启停、变更、缩容与销毁。
2. [故障排查](troubleshooting/)：诊断信息与常见问题修复。
3. [镜像仓库](images/)：选择镜像、使用镜像站、导入与清理缓存。
4. [从源码构建](source-build/)：开发者构建、检查与本地 PATH。
5. [卸载与清理环境](uninstall/)：移除 deployment、镜像、网络与状态。
6. [自动化与客机脚本](automation/)：无人值守准备、JSON 验收、可重复执行的客机脚本与 Pigsty 衔接。
7. [存储与访问](storage/)：磁盘保留、文件传输、SSH 隧道与 Linux 目录共享。
8. [macOS 虚拟机](macos/)：尚未发布的 `farrow mac`，在 Apple 芯片上运行带桌面、SSH、
   共享目录与剪贴板的 macOS 27 客机。
