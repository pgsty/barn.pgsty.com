---
title: 验证历史
description: Barn 历次发布、原生虚拟机测试、镜像校验与设计演进的原始记录。
weight: 40
icon: fa-solid fa-clock-rotate-left
---

> [!NOTE]
> 本页保留截至 2026-09-29 的验证记录，来源为文档提交 `4c03fc9`。名称统一为 Barn，结果仍对应当时测试的版本。现行说明见[平台与限制](../status/)和 [0.9.0 发布说明](/zh/blog/release/0.9.0/)。

当时，Barn 0.9.0 是更名后的首个发行候选，**尚未发布**。待完成的发布检查列在下文。
安装请使用现行的[快速上手](../../start/installation/)。

## 文档基线 {#documentation-baseline}

| 对象 | 当时的身份 | 说明 |
|---|---|---|
| 程序与当前文档 | Barn 0.9.0 发布候选 | 从包含改名变更的源码构建；发行包命令在发布后使用。 |
| CLI 与配置 | `barn`、`barn.yml`、`BARN_*` | 不提供旧名称别名或环境变量回退。 |
| 状态与宿主资源 | `~/.barn`、Barn 网络与 helper | 使用新状态重新创建；不迁移旧开发环境。 |
| 镜像仓库 | 官方入口的 `/barn` 前缀 | 镜像目录仍需验签；云端迁移和公开访问要独立核验。 |

更名需要先停止旧内部环境并保留所需数据，再全新安装 Barn，不支持直接重命名旧状态目录。
当时尚未完成最终发布提交、制品摘要、Homebrew 与公开入口的核验。

## macOS 客机 {#macos-guests}

`barn mac` 在 Apple 芯片上运行 macOS 27 虚拟机，见[教程](../../start/macos/)与
[命令参考](../../reference/mac/)。组件名称为 `Barn Mac.app`，签名标识为
`io.pgsty.barn.mac-runner`。它使用独立的 `$BARN_HOME/mac`，不提供旧开发环境迁移命令。

2026-09-29 改名后，本地 CLI/hosts-helper 测试、原生 Bridge/镜像/退出提示/菜单测试、
runner 编译、ad-hoc 签名验证与 `probe` 通过。这些检查没有启动虚拟机，未重新执行完整
Mac 实机生命周期。此前的实机结果按原身份保留在下文。

## 发行前仍需核验

- 最终 Barn 提交的完整源码、归档、DEB/RPM、安装器与跨平台检查；
- 新名称下的全新宿主准备、Linux/macOS 虚拟机生命周期与清理；
- Mac Developer ID 签名、公证及正式发布；
- GitHub 仓库、Homebrew、两地镜像源与 `barn.pgsty.com` 的实际公开状态。

## Barn Mac 实机记录：2026-09-29

2026-09-29，改名前的 Barn 开发源码在 Apple 芯片 Mac 上完成验证。
宿主运行 macOS 27.0（26A428），测试使用 ad-hoc 签名的开发构建。
验证期间没有下载 macOS 镜像。每个测试目录都使用基础镜像的 APFS 克隆。
该基础镜像于 2026-09-26 由 Apple 固定版本 27.0 恢复镜像创建。

- **源码检查**：完整 `make check`、原生组件测试，以及 Mac 发布包构建与解包后的校验和、签名、探测检查均通过。
- **自动化实机验收**：16 个阶段全部通过，用时 244.9 秒。测试覆盖从基础镜像创建、带共享目录的命名虚拟机、独立身份与 sshd 策略。检查了磁盘隔离、每台虚拟机的网络隔离、DNS 与公网 HTTPS。还检查了退出码、参数边界及共享目录双向写入。生命周期测试覆盖正常停启、`configure`、拒绝第三台运行中的虚拟机，以及 `recreate` 更换身份。其他检查包括桌面、双向剪贴板、重复 `up` 保持基础镜像不变，以及 `destroy`。
- **人工检查**：从已准备的基础镜像创建到 SSH 就绪需 22 秒。正常关机需 6.5 秒。启动到 SSH 就绪需 6–12 秒。强制断电需 0.7 秒。还验证了 macOS 恢复模式启动、更换网段后保留固定主机密钥，以及通过已安装的 OpenSSH 条目执行 `ssh mac1`。

macOS 客机仍需完成以下检查：

- Developer ID 签名、公证与正式发布。
- 用当前 CLI 下载并安装 macOS：无基础镜像时首次 `up`，或 `image update`。
- 桌面菜单中的 **Restart…** 与 **Shut Down…**。
- 其他 Apple 芯片机型与 macOS 27 后续更新。
- 物理宿主重启。

## 改名前的 Linux 验证概览 {#summary}

| 宿主或产物 | 路径 | 最后验证 | 结果 |
|---|---|---|---|
| 两台 Linux amd64（`m0`、`m3`） | KVM，每机七系统 | 2026-09-21（0.8.0） | 从零初始化、首次 SSH、最终候选原位升级、重复 up、stop/start、磁盘身份与 Ansible 配置读取通过 |
| 两台 macOS arm64（`m1`、`m5`） | HVF，每机七系统 | 2026-09-21（0.8.0） | 同样的生命周期检查通过，另通过每机七节点 Ansible ping |
| 镜像目录 `2026092001` | 9 个系列、37 个工件；九月 Debian/Ubuntu 更新 | 2026-09-21 | 内置/本地/LAN/公开镜像目录字节一致；十个新增镜像在两个公开入口可访问且大小正确；所选镜像通过四机原生 pro 验收 |
| Ubuntu 26.04 amd64 | KVM、QEMU 10.2.1、Ubuntu 24.04 客机 | 2026-09-16（0.7.0 恢复） | 损坏盘重置、探测失败、忙碌挂载、保留盘重建、共享目录恢复与重复健康 up 通过 |
| macOS arm64 | HVF、Ubuntu 24.04.4 客机 | 2026-09-05（0.6.0 生命周期修改） | 创建、扩容、同伴 SSH、stop/start、reload、recreate、部分状态与缩容通过 |
| macOS 26.6.2 arm64 | HVF、QEMU 11.1、socket_vmnet | 2026-09-01（`v0.2.0`） | 选点创建/SSH/stop/start、增量创建已缓存镜像、整体 status、整体 destroy 通过 |
| macOS 26.6.2 arm64 | HVF、QEMU 11.1、socket_vmnet | 2026-08-27 | 单节点与增量四节点通过 |
| Ubuntu 26.04 amd64（`mx`） | KVM、QEMU 10.2.1、NetworkManager | 2026-09-01（`v0.2.0`） | 确认现存四节点部署正在运行，并进入控制客机 |
| Ubuntu 26.04 amd64（`mx`） | KVM、QEMU 10.2.1、NetworkManager | 2026-08-27 | setup、单节点、增量创建四节点与卸载通过 |
| macOS arm64 | HVF 宿主、TCG 兼容规则、Rocky Linux 8.10 arm64 | 2026-08-28 | 启动、stop/start、启动后 44.2 秒达到就绪状态 |
| 已发布镜像目录 `2026090501` | 9 个系列、27 个 qcow2 工件 | 2026-09-05 | 工件校验、内置/公开字节一致，以及两个官方入口的签名更新通过 |
| 已发布镜像目录 `2026082903` | 9 个系列、27 个已签名 qcow2 工件 | 2026-08-29 | 全量 SHA-256 校验与干净客户端拉取 `d13:stable` 通过 |

本轮每台宿主均覆盖 Rocky Linux 9.8/10.2、Debian 12.15/13.7、Ubuntu
22.04.5/24.04.5/26.04.1，共 28 个成功的客机实例。临时验收虚拟机已在之后清理。
两个公开镜像目录的 SHA-256 均为
`23e8dbf6c19bd192d56c6d71eb30901f17945b3487e427a43abe108463780306`。
两端分别执行隔离的 `barn update`，成功验签并激活修订版本 `2026092001`。
公开镜像检查覆盖每端十个新增对象的 HEAD/内容长度，没有重新下载并计算全部公开工件摘要。

## 旧检查点尚未覆盖的范围

- EL9 宿主的 NetworkManager + firewalld，以及当前 systemd-networkd 重放；
- 物理宿主重启后的持久性；
- macOS amd64 与 Linux arm64 真机运行，目前仅有构建/打包检查；
- 当前 Linux/amd64 原生 EL7 生命周期；
- macOS 目录共享：已测 QEMU 无法重开 Barn 安全持有的目录描述符；
- 完整的 Pigsty `configure → barn up → install.yml`；
- 修正后的全新 Homebrew socket_vmnet 安装认证路径原生重放；
- 通过公开安装器、Homebrew 或公开 DEB/RPM 软件包完成干净宿主准备与虚拟机创建。

当前内置版本均为 `supported`，只有 EOL EL7 与保留兼容版本 EL9 9.3/9.6、EL10 10.0
为 `deprecated`。活动和备用镜像目录公钥已经内置。必须在 1.0 前明确私钥托管、轮换与发布职责。

## Barn 验证历史

以下按版本列出测试提交、环境与结果。

### Barn 0.8.0：2026-09-21

发布标签 `v0.8.0` 指向 `320a32afa8f6fca02592215aa0d5607ca4e852b2`。
[源码 CI](https://github.com/pgsty/barn/actions/runs/35568664994)、独立
[打包构建快照](https://github.com/pgsty/barn/actions/runs/35568664948) 和
[标签工作流](https://github.com/pgsty/barn/actions/runs/35569143101)通过。
标签工作流生成 20 个资产，其中 19 项列入校验清单。相对下述已验收运行时，
发布提交只更新 README 与发布说明。在该标签上重新本地构建也通过归档与软件包检查。

版本于 2026-09-21 公开。验证通过宿主已配置的代理匿名下载全部 20 个资产，未使用 GitHub 凭据。
每项均返回 HTTP 200。完整正文 SHA-256 与 API 摘要及已检查草稿一致。
19 项载荷全部匹配校验清单。公开安装器在 macOS arm64 与 Linux amd64 的隔离用户目录
均成功安装，报告 0.8.0 / `320a32a`，CLI/helper 字节与各自已校验的公开归档一致。
Linux 下载通过临时 SSH 回环转发访问已有代理，验证后已关闭。默认安装与虚拟机/网络状态
保持不变。这些检查验证了二进制安装。通过公开安装器准备全新宿主并创建虚拟机仍待验证。

[Homebrew Tap](https://github.com/pgsty/homebrew-infra/commit/9c3401958a435248ebf0e5402e7efff712ee1c4c)
四个平台均已选择 0.8.0，归档摘要与公开发布一致。本地语法、更新器测试、一致性/样式/
平台检查、严格在线 audit 和原生 arm64 `brew fetch` 通过。macOS 与 Linux 上的
[CI 任务](https://github.com/pgsty/homebrew-infra/actions/runs/35570285428)也通过元数据、
更新器、样式、平台和 audit 检查。本轮没有重新执行 `brew install`、升级、relink 或
`brew test`。

从零初始化的基线为 `6d7870e26cb2f4082a00c188f746783fc027687e`。四台宿主分别清理
已确认归属的旧环境与网络，从空 Barn 用户状态和缓存开始，使用同一局域网仓库创建
七系统 pro 配置。Linux 实际安装 DEB；macOS 使用完整已校验归档，以用户级安装保留
配对的 CLI/helper。

运行时候选 `1c054a027420b5410c6f6feb344e27e001ae1af1` 加入 Homebrew 认证顺序修复，
通过完整本地 `make check` 及发布归档/软件包检查。随后在四机原位安装，完成健康 `up`、
两轮客机 SSH、stop/start 和 Ansible 配置读取；两台 Mac 还分别通过七节点 Ansible ping。
虚拟机 UUID、镜像身份、根盘/数据盘路径及 inode 保持，健康重复 `up` 还保持运行进程。
验证包括真实数据盘访问、Debian locale/XFS 和控制节点到其他客机的 SSH。

验证先从零创建 6d 基线，再原位安装最终 1c 候选并复验生命周期。它没有从零初始化 1c。
Homebrew 顺序回归测试在修复前失败，修复后通过。原生从零阶段使用固定后端归档，
没有测试全新 Homebrew Formula 安装。没有重启物理宿主，没有运行完整 Pigsty 安装或
macOS 目录共享。[发布说明](../../../blog/release/0.8.0/)列出生命周期计时样本和镜像版本。

### Barn 0.7.0 发布：2026-09-16

发布提交 `9c6d4896d93733d1cb60a7e5d8591e9a06659c9d` 在打标签前通过完整
[源码 CI](https://github.com/pgsty/barn/actions/runs/35118137961) 与独立
[打包构建快照](https://github.com/pgsty/barn/actions/runs/35118137990)。
[标签工作流](https://github.com/pgsty/barn/actions/runs/35119206685) 重复检查并生成包含
20 个资产的草稿，检查后公开发布。20 个匿名下载均返回 HTTP 200，字节与检查过的草稿
一致，19 项载荷全部通过摘要校验。macOS arm64 与 Ubuntu amd64 的公开安装器安装结果
均与发布归档中的二进制一致。下载验证使用宿主现有代理，m3 通过临时回环隧道访问该代理。
`pgsty/infra/barn` Formula 已刷新到 `v0.7.0`，本机 Homebrew 升级与 `brew test` 通过；
干净宿主 Formula 安装仍待重放。

Ubuntu amd64/KVM 故障矩阵覆盖 ext4/XFS 损坏、持久盘、探测失败、忙碌挂载、只读共享
和重复健康 `up` 保留进程。公开版 0.6.0 因出网探测失败而中断，0.7.0 在 3.3 秒内接续
同一台虚拟机。探测失败期间，已有磁盘的数据与 UUID 保持不变。升级后回退 0.6.0，仍能执行
status、stop、start 与 destroy，包括存在可选警告缓存的情况。最终 0.7.0 归档新建的虚拟机
无警告启动，也不会继承旧实例的警告缓存。

公开安装器装出的 Linux 二进制还在 3.2 秒内重置了人为破坏的可丢弃 ext4 数据盘，
程序报告数据已丢弃，并保留虚拟机运行进程。随后 stop、start 与 purge 均通过。

该 0.6.0 中断现场已经删除了暂存的控制节点 SSH 私钥。管理访问恢复，但节点间 SSH
仍以 `control-ssh` 限制明确报告，详见[升级说明](../../../blog/release/0.7.0/)。
本次未发布新客机镜像，镜像目录 `2026090501` 不变；未新增 macOS HVF、宿主重启或完整
Pigsty 安装重放。

### Barn 0.6.0 发布：2026-09-05

生命周期与 UX 修改通过 Claude Code Fable 5.1 / xhigh 两轮对抗性审查。
发布元数据与 CI 测试夹具修复也通过后续审查。发布提交 `057774e3a13477782a2ae07bd71127d03c0f1ae7`
通过完整的 Go 1.27.1 [源码 CI](https://github.com/pgsty/barn/actions/runs/33959205857)，
最新打包改动在 `13d9d70` 通过独立的
[构建快照与软件包检查](https://github.com/pgsty/barn/actions/runs/33958857302)。
[标签工作流](https://github.com/pgsty/barn/actions/runs/33959431603) 重复源码检查，
验证四平台归档、四份 Linux 软件包、八份 SPDX、安装器、Homebrew Formula、发布元数据
及全部 19 项校验和，生成包含 20 个资产的发布。
发布已公开，全部资产摘要与校验清单一致。隔离的 macOS arm64 安装目录通过公开下载
路径从 0.5.0 升级到 0.6.0，两个已安装程序均与校验后的发布归档字节一致。
发布二进制还通过了 `init` 和新建 U24 环境的 `plan` 验证。

隔离的 macOS arm64/HVF U24 环境通过了首次启动、不重启控制节点的扩容、控制节点到
其他节点的 SSH、stop/start、正常 reload、局部重建、缩容和客机名称刷新。无效镜像 reload
与存在配置冲突的局部重建均在影响现有虚拟机前停止；部分状态损坏仍能展示健康节点，SSH 的
255 退出码原样透传。最终的客机 SSH 作用域修复经真实 OpenSSH 有效配置测试验证。
验证结束后已移除测试环境。

已发布镜像目录 `2026090501` 默认使用 `u24:stable`，并纳入镜像目录 `2026090302` 中已经
公开的 Debian/Rocky 镜像更新。27 个工件全部通过仓库字节校验。两个官方入口提供与内置
目录一致的内容及生产签名。隔离客户端分别完成了 `barn update`。本次应用发布没有构建新客机镜像。
没有重新执行 Linux 宿主虚拟机生命周期、宿主重启或完整 Pigsty 安装。

### Barn 0.5.0 发布：2026-09-03

提交 `fc85b65ff6a24b0933b56ae1179be9ada2ba91b1` 在打标签前同时通过主干的完整
Go 1.27.1 源码门禁与独立 GoReleaser 构建快照与软件包检查。该标签工作流随后再次执行
源码/工具链检查，构建并验证四个平台的归档、四份 Linux 原生软件包、八份 SPDX、
Homebrew Formula、安装器、`release.json` 与 19 项校验和清单，最后创建包含
20 个资产的预发布版。

0.5.0 加入无需确认的整套部署 `purge`/`rm`。默认仓库明确为全球 `repo.pigsty.io`，
中国入口使用 `--mirror`。该版本移除隐藏的镜像目录上游回退。
它还加入 Debian/Rocky 八目标官方候选镜像构建器，使用摘要锁定输入。
构建结果仍是未签名的 `testing` 候选版本。本次应用发布不变更镜像目录，也不增加真机生命周期验证结果。

### Barn 0.4.0 发布：2026-09-02

该标签提交通过 `make check`，以及发布工作流的归档、DEB/RPM、SBOM、校验和、
安装器、Homebrew Formula 与软件包一致性门禁。`up` 在未准备好的终端宿主机上会自己
执行 `setup`。`vm_disks[].fs` 默认为 `auto`。就绪失败信息包含客机的最后一行错误。
全部命令使用相同的输出风格。首次运行路径未在全新宿主上重放，本节没有新增真机验证结果。

### Barn 0.3.0 发布：2026-09-02

精确标签提交通过 `make check`，以及发布工作流的归档、DEB/RPM、SBOM、校验和、
安装器、Homebrew Formula 与软件包一致性门禁。镜像目录刷新改为显式操作。对配置的仓库使用 `barn update`，对指定来源使用 `image sync`。
客机就绪失败时，错误信息包含各节点所处阶段与后续日志命令。本节没有新增真机验证结果。

### Barn 0.2.0 发布：2026-09-01

源码提交 `59d1b62aebb3d044a317e4006cc8a0bf56f4feaf` 已标记 `v0.2.0`。
该提交通过源码 CI 与独立手动触发的打包工作流。稳定版的本地发布流程还构建并验证了
四平台归档、amd64/arm64 DEB 与 RPM，以及 8 份 SPDX 文档。检查包括配套 helper 摘要、
归档与软件包一致性、Homebrew Formula、安装器、发布元数据及 19 项最终校验和。

macOS arm64/HVF 重放在 MonoProxy 的 `10.0.0.0/8` 覆盖排除路由存在时执行：
选点创建 `u24-1`、SSH、stop/start、增量创建已缓存的 `el9-1`、对五个未创建的期望节点执行整体 status、两节点 SSH，以及整体 destroy 与 SSH 配置片段清理全部通过。
在 Ubuntu 26.04 amd64/KVM 上，Linux 二进制无变更地审计了一套现存四节点
Barn 部署，并进入控制客机。

编译默认镜像仓库仍是签名的 COS 入口 `https://repo.pigsty.cc/barn`。独立检查的
`https://repo.pgsty.com/barn` 源站提供字节一致的镜像目录、源元数据、
校验和与镜像，并将 Nginx 工作进程限制为只读权限。

### Schema-3 Catalog 收口：2026-08-29

镜像目录修订版本 `2026082903` 是当天的源码与开发仓库检查点：9 个系列、27 个分架构工件。
内置镜像目录与已发布 `catalog.json` 的 SHA-256 同为
`571b1ff9c7d4d42355df3392ea62a339471c2d01d868669a7625fac8b93f245d`；
已发布 `repo.yaml` 也与源码维护文件完全一致。全新 HTTP 与 HTTPS 客户端均接受了生产公钥
`4686B39A40F9B562` 对应的分离签名。

全部 27 个已发布 qcow2（合计 19 GiB）均按镜像目录完成全量 SHA-256 校验。随后一套空白
临时 Barn 主目录完整下载了 409.3 MiB 的 Darwin/arm64 默认 `d13:stable` 工件，重新计算
摘要，并通过 qcow2 结构与虚拟容量检查。这些只证明发布完整性与客户端路径，不能替代
真机生命周期矩阵；本次镜像目录核验没有重建任何现有虚拟机。

### 0.1.0 Candidate：2026-08-28 与 2026-08-29

两份隔离的 `v0.1.0` 候选版本通过了稳定版的本地发布流程，随后被 0.2.0 取代。
这些测试确认了两个独立结果。

两台运行中节点的 QMP 套接字被外部删除。Darwin/arm64 二进制仅停止并启动这两台节点，
13.7 秒后均恢复就绪状态。另外两台节点的 boot ID 保持不变。

完整的 macOS 出厂清理暴露了源码测试对已安装 `qemu-img` 的依赖。
空白宿主无法列出镜像目录。修复后，Barn 只在需要校验本地 qcow2 字节时才解析 Store。
回归测试从 `PATH` 移除 QEMU。`make check` 在没有 QEMU、Barn 状态和网络状态时通过。

### EL7/EL8 兼容性：2026-08-28

提交 `7c666c7` 在两轮独立对抗审查后恢复 EL7/EL8。第一轮发现破坏性操作前的运行时预检顺序问题，
以及签名镜像目录的基线迁移问题，结果为 BLOCK。修复并补充回归测试后，第二轮结果为 PASS，
没有必须修复的问题。

在当时的检查点，镜像目录 `2026082801` 已在开发仓库签名激活：9 个系列、17 个镜像
工件；包含两份 socket_vmnet 归档在内的 19 个仓库文件均重新通过完整
SHA 校验。干净客户端接受了公开签名与准确嵌入摘要。

隔离的 macOS arm64 生命周期重放用内置 TCG 兼容规则启动 Rocky Linux 8.10 arm64，
stop/start 后 44.2 秒达到就绪状态。测试还验证了 NetworkManager、固定 IP/无路由/无 DNS、
`dba` UID/GID 88 与 generation/spec marker。EL7 字节、qcow2、BIOS 布局与 4K XFS
根文件系统已验证；Linux/amd64 原生 Barn 生命周期仍待重放。

### 真机重放：2026-08-27

概览表中的两台宿主均通过固定 IP、SSH 就绪状态、默认 CPU/内存/根盘/数据盘、cloud-init、
stop/start 与跨目录操作检查。扩容时，控制节点 boot ID 保持不变，控制节点仍能通过 SSH 访问其他节点。
Barn 忽略不使用的 Pigsty 字段变更。清单中缺少节点时，它保留对应虚拟机。显式 destroy 删除虚拟机。

Linux 还验证了 NOPASSWD 自动化、调用者可用的 Debian helper 权限、普通用户 QEMU 网桥测试、
四个 tap 挂接时拒绝卸载，以及 destroy 后精确恢复宿主状态。

交互式宿主网络与 hosts 命令会自行调用 sudo，外部 `sudo -v` 只是可选优化。
Darwin 的 `network.json` 丢失时，也可用字节一致的接口双份证据、准确 launchd plist 与
已安装二进制摘要重建仅用于卸载的归属计划。

2026-08-28，校准后的工作树通过 unit、race、vet、staticcheck、govulncheck、四平台交叉
构建、模拟镜像流水线边界、许可证校验与 GoReleaser 配置校验。隔离的本地 GoReleaser
构建快照还构建并验证了四个平台归档、两个架构的 DEB/RPM、SPDX、校验和、依赖、权限
以及归档/软件包一致性。没有发布任何产物；这些结果不增加真机测试覆盖。
