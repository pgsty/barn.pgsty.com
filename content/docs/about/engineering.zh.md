---
title: 参与贡献
description: 参与 Barn 源码、文档、软件包与镜像目录的维护。
weight: 30
icon: fa-solid fa-screwdriver-wrench
---

Barn 采用 Apache-2.0 许可证，欢迎参与命令行工具、macOS 原生组件、文档和镜像工具的改进。

## 选择仓库

| 想改进什么 | 在哪里修改 |
| --- | --- |
| 命令行行为、虚拟机生命周期、macOS 原生组件、安装器与软件包 | [pgsty/barn](https://github.com/pgsty/barn) |
| 本网站、教程、命令参考与翻译 | [pgsty/barn.pgsty.com](https://github.com/pgsty/barn.pgsty.com) |
| 镜像定义或镜像归一化步骤 | Barn 源码仓库中的 `packaging/image-repository/` 与 `packaging/image-pipeline/` |

报告问题时，请附上 `barn version` 的输出、宿主操作系统与架构、执行的命令和相关报错。
分享日志与主机清单前，请移除私钥、密码等敏感信息。安全问题请按
[安全策略](https://github.com/pgsty/barn/blob/main/SECURITY.md)中的方式报告。

较大的实现改动，建议先通过 Issue 说明问题与预期行为。代码约定、模块职责与拉取请求要求见
[贡献指南](https://github.com/pgsty/barn/blob/main/CONTRIBUTING.md)。

## 构建与测试

按[从源码构建](../../start/source-build/)安装固定版本的工具链后，运行：

```bash
make check
```

这项检查涵盖模块与 Shell 检查、单元与竞态测试、静态分析、漏洞扫描、四个目标平台的交叉构建、
安装器与镜像流水线测试，以及许可证检查。完整清单以 Makefile 为准。CI 还会检查代码格式、
空白字符与发布配置。

涉及虚拟机行为的改动，还需要在相应宿主上验证。交叉构建通过，并不能验证 macOS HVF、
Linux KVM 与网络，或 macOS 原生组件。请在拉取请求中说明测试环境和实际验证的行为。

修改打包逻辑时，使用本地快照检查：

```bash
make release-check
make release-snapshot SNAPSHOT_DIST=.goreleaser-review
```

安装 `packaging/toolchain.env` 中指定版本的工具，以及验证脚本所需的归档与软件包检查工具。
输出路径必须是工作区根目录下尚不存在的新目录；快照目标会拒绝覆盖已有输出，也不会上传构建结果。

## 修改文档

英文与中文页面相邻存放，分别命名为 `page.md` 与 `page.zh.md`。请保持命令、默认值、链接与
注意事项一致，先解释用户要完成的任务，再介绍实现细节，并区分 Linux 与 macOS 客机的使用方式。

在网站仓库中运行：

```bash
make check
```

这会使用固定版本的 Hugo 主题构建网站，并检查内部链接、资源和页面锚点。修改布局后，请预览
中英文页面及浅色、深色主题。

## 了解发布产物

Barn 0.9.0 提供 macOS 与 Linux 压缩包、Linux 软件包、校验和、发布元数据及 SPDX 软件物料清单。
CLI 与 `barn-hosts-helper` 配套分发。压缩包中的二进制位于 `bin/`，许可证位于 `licenses/`；
Linux 软件包安装 `/usr/bin/barn` 与 `/opt/barn/libexec/barn-hosts-helper`。

`Barn Mac.app` 是运行 macOS 客机所需的附加组件，构建与签名要求见
[原生组件发布指南](https://github.com/pgsty/barn/blob/main/docs/mac-release.md)。只包含 CLI 的构建仍可用于 Linux 客机。

应用校验和、原生应用签名与镜像目录签名各有用途。应用发布流程提供校验和，不生成单独的发布签名
或来源证明包；原生应用有独立的 Developer ID 签名与公证流程；Minisign 则用于认证镜像目录。

## 维护镜像目录

从[镜像流水线参考](../../reference/image-pipeline/)开始。底层构建器接受本地 qcow2 镜像，完成校验，
并可在离线 QEMU 沙箱中执行归一化。官方构建入口为 amd64/arm64 的 Debian 12/13、Rocky Linux 8/9
使用锁定的输入，生成未签名的 `testing` 条目，供真机启动测试、签名和发布前审核。

将内置镜像目录导出到新路径：

```bash
go run ./tools/catalogexport /absolute/new/catalog.json
```

导出器原子写入，并拒绝已存在的输出路径。`make catalog-sign` 与 `make catalog-verify`
使用独立的 Minisign 密钥对；生产私钥不进入源码或 CI。用户侧的镜像行为见[镜像参考](../../reference/images/)。
