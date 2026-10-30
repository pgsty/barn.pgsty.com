---
title: 验证历史
description: Barn 历次发布、原生虚拟机测试、镜像校验与设计演进的原始记录。
weight: 40
icon: fa-solid fa-clock-rotate-left
---

> [!NOTE]
> 本页归档了 0.9.0 发布前的验证基线（2026-09-29，文档提交 `4c03fc9`）以及早期版本（`0.1.0` 至 `0.8.0`）的实机测试与镜像校验记录。当前宿主支持范围与最新版本说明请查阅[平台与限制](../status/)与 [Barn 0.9.2 发布说明](/zh/blog/release/0.9.2/)。

在 2026-09-29 检查点时，Barn `0.9.0` 是完成项目更名后的首个候选发布版本。现行安装方式请参见[快速上手](../../start/installation/)。

## 文档基线 {#documentation-baseline}

| 对象 | 2026-09-29 检查点状态 | 范围说明 |
|---|---|---|
| 程序与文档 | Barn `0.9.0` 候选版本 | 基于完成更名的源码树构建 |
| CLI 与配置文件 | `barn`、`barn.yml`、`BARN_*` | 全面启用新命令名与环境变量，不保留旧内部名称回退 |
| 状态与宿主资源 | `~/.barn`、Barn 网络与 `barn-hosts-helper` | 使用全新 `~/.barn` 状态目录，不迁移更名前的旧开发状态 |
| 镜像仓库 | 官方端点 `/barn` 路径 | 强制校验 minisign 镜像目录签名 |
{.wide}

## macOS 客机 {#macos-guests}

在 2026-09-29 检查点，`barn mac` 通过 `Barn Mac.app`（签名标识 `io.pgsty.barn.mac-runner`，后于 [Barn 0.9.1](/zh/blog/release/0.9.1/) 统一为 `Barn.app` / `com.pgsty.barn`）在 Apple Silicon 上运行 macOS 27 客机，状态独立保存在 `$BARN_HOME/mac` 下（现行用法见[macOS 客机指南](../../start/macos/)与 [Mac 命令参考](../../reference/mac/)）。

2026-09-29 完成更名后，本地 CLI 与 `barn-hosts-helper` 单元测试、原生 Bridge/镜像/退出提示/菜单测试、runner 编译、ad-hoc 签名校验与 `probe` 探测全部通过，与同日早些时候完成的 16 阶段 Mac 真机生命周期验收相衔接。

## 0.9.0 发布前待收口项

在 2026-09-29 检查点，正式公开 `0.9.0` 前剩余的门禁项包括：

- 最终发布标签提交上的完整源码测试、四平台归档、DEB/RPM 软件包、安装脚本与跨平台检查。
- 新名称下的全新宿主环境准备、Linux/macOS 虚拟机生命周期与卸载清理复核。
- macOS 原生组件的 Developer ID 签名、公证与发布。
- GitHub 仓库、Homebrew Tap、两地 `/barn` 官方镜像源与 `barn.pgsty.com` 公开可用性核验。

## Barn Mac 实机记录：2026-09-29

2026-09-29，更名前的开发源码在搭载 Apple Silicon、运行 macOS `27.0`（`26A428`）的 Mac 上使用 ad-hoc 签名构建完成全套实机验证；测试复用 2026-09-26 基于 Apple `27.0` 恢复镜像准备好的基础镜像 APFS 克隆：

- **源码与组件包检查**：完整 `make check`、原生 Swift 组件测试，以及应用包构建、解包校验和、代码签名与 `probe` 检查全部通过。
- **16 阶段自动化真机验收（耗时 244.9 秒）**：覆盖从基础镜像创建虚拟机、带 VirtioFS 共享目录的命名虚拟机、独立机器标识与 `sshd` 策略、磁盘隔离、每台虚拟机独立的子网隔离、DNS 与公网 HTTPS、退出码透传、`exec` 参数边界、共享目录双向读写、正常 `stop`/`start`、`configure`、拒绝启动第三台并发虚拟机、`recreate` 重置身份、打开桌面窗口、双向纯文本剪贴板同步、重复 `up` 幂等性以及 `destroy`。
- **人工计时与恢复验证**：从已准备好的基础镜像创建虚拟机到 SSH 就绪耗时 `22 秒`，正常关机耗时 `6.5 秒`，二次启动到 SSH 就绪耗时 `6–12 秒`，强制断电耗时 `0.7 秒`。同时验证了引导进入 macOS 恢复模式（`--recovery`）、更换 `--subnet` 后保持固定 SSH 主机密钥，以及通过已安装的 `~/.ssh/barn-mac_config` 直接执行 `ssh mac1`。

当时留待后续里程碑验证的事项：

- 原生应用包的 Developer ID 签名、Apple 公证与公开发布。
- 通过 CLI 从零下载 IPSW 并准备基础镜像（无基础镜像时首次 `barn mac up` 或 `barn mac image update`）。
- 桌面窗口菜单中的 **Restart…** 与 **Shut Down…** 动作、更多 Apple Silicon 机型以及物理宿主重启验证。

## 更名前的 Linux 验证概览 {#summary}

| 宿主或产物 | 验证路径 | 验证日期 | 结果 |
|---|---|---|---|
| 两台 Linux `amd64` 宿主（`m0`、`m3`） | KVM，每机 7 个发行版 | 2026-09-21（`0.8.0`） | 从零初始化、首次 SSH、候选版本原位升级、重复 `up`、`stop`/`start`、磁盘身份与 Ansible 配置读取全部通过 |
| 两台 macOS `arm64` 宿主（`m1`、`m5`） | HVF，每机 7 个发行版 | 2026-09-21（`0.8.0`） | 完成相同生命周期检查，并通过每机 7 节点 `ansible all -m ping` |
| 镜像目录 `2026092001` | 9 个系列、37 个产物（9 月 Debian/Ubuntu 更新） | 2026-09-21 | 内置、本地、局域网与公网目录字节一致（`23e8dbf6...`）；10 个新镜像在两个公网端点大小匹配并通过四机真机验收 |
| Ubuntu 26.04 `amd64` | KVM、QEMU `10.2.1`、Ubuntu 24.04 客机 | 2026-09-16（`0.7.0` 恢复） | 损坏数据盘重置、探测失败保护、忙碌挂载、保留盘重建、共享目录恢复与幂等 `up` 全部通过 |
| macOS `arm64` | HVF、Ubuntu 24.04.4 客机 | 2026-09-05（`0.6.0` 生命周期） | 创建、扩容、节点间 SSH、`stop`/`start`、`reload`、`recreate`、降级 `status` 与缩容全部通过 |
| macOS 26.6.2 `arm64` | HVF、QEMU `11.1`、`socket_vmnet` | 2026-09-01（`v0.2.0`） | 选定节点创建/SSH/停启、增量创建已缓存镜像、全局 `status` 与全局 `destroy` 通过 |
| macOS 26.6.2 `arm64` | HVF、QEMU `11.1`、`socket_vmnet` | 2026-08-27 | 单节点与增量四节点生命周期通过 |
| Ubuntu 26.04 `amd64`（`mx`） | KVM、QEMU `10.2.1`、NetworkManager | 2026-09-01（`v0.2.0`） | 审计现存四节点运行中部署并连通控制节点 |
| Ubuntu 26.04 `amd64`（`mx`） | KVM、QEMU `10.2.1`、NetworkManager | 2026-08-27 | 宿主 `setup`、单节点、增量四节点与网络卸载通过 |
| macOS `arm64` | HVF 宿主、Rocky Linux 8.10 `arm64` TCG 兼容规则 | 2026-08-28 | 启动、`stop`/`start` 并在 `44.2 秒`内达到 SSH 就绪 |
| 已发布镜像目录 `2026090501` | 9 个系列、27 个 `qcow2` 产物 | 2026-09-05 | 产物校验、内置与公网字节一致，以及两个官方端点的签名 `barn update` 通过 |
| 已发布镜像目录 `2026082903` | 9 个系列、27 个签名 `qcow2` 产物 | 2026-08-29 | 19 GiB 全量 SHA-256 校验与干净客户端拉取 `d13:stable` 通过 |
{.wide}

在 `0.8.0` 四机验收中，每台宿主均实测了 Rocky Linux 9.8/10.2、Debian 12.15/13.7 与 Ubuntu 22.04.5/24.04.5/26.04.1（共 28 个客机实例全部通过，验收后已清理测试虚拟机）。两个公网端点提供的镜像目录 `2026092001` 摘要均为 `23e8dbf6c19bd192d56c6d71eb30901f17945b3487e427a43abe108463780306`，并通过了隔离客户端 `barn update` 验签以及 10 个新增镜像对象的 HTTP `HEAD` 长度核对。

## 当时待补充的测试覆盖

- 启用 NetworkManager + `firewalld` 的 EL9 宿主，以及最新 `systemd-networkd` 宿主重放。
- 物理宿主重启后的部署状态保持。
- `darwin/amd64` 与 `linux/arm64` 宿主的真机虚拟化运行（除交叉编译与打包检查外）。
- `linux/amd64` 原生 `el7` 完整生命周期重放。
- 完整 Pigsty `configure → barn up → install.yml` 部署流程。
- 通过公网安装脚本、Homebrew Formula 或已发布 DEB/RPM 软件包在全新宿主上从零执行 `setup` 与创建虚拟机。

## Barn 历次版本验证记录

### Barn 0.8.0 — 2026-09-21

- **发布 CI 与公开制品**：标签 `v0.8.0`（`320a32afa8f6fca02592215aa0d5607ca4e852b2`）通过[源码 CI](https://github.com/pgsty/barn/actions/runs/35568664994)、[打包快照工作流](https://github.com/pgsty/barn/actions/runs/35568664948)与[标签发布工作流](https://github.com/pgsty/barn/actions/runs/35569143101)，产出 20 个发行资产（含 19 项校验和载荷）。全部 20 个公开资产通过匿名下载与 SHA-256 校验，公网安装脚本在 `darwin/arm64` 与 `linux/amd64` 的隔离用户目录中成功安装并验证 `0.8.0`（`320a32a`）。
- **Homebrew Tap**：提交 [`9c34019`](https://github.com/pgsty/homebrew-infra/commit/9c3401958a435248ebf0e5402e7efff712ee1c4c) 将四平台 Formula 更新至 `0.8.0`，通过本地 `brew fetch`、audit 及 [Tap CI](https://github.com/pgsty/homebrew-infra/actions/runs/35570285428)。
- **四机七系统真机验收**：在基线提交 `6d7870e26cb2f4082a00c188f746783fc027687e` 上清空四台宿主（两台安装 `.deb` 的 Linux `amd64` 宿主 `m0`/`m3`，两台使用校验归档安装的 macOS `arm64` 宿主 `m1`/`m5`），从局域网镜像源从零拉起七系统 `pro` 清单。随后将包含 Homebrew 认证顺序修复的候选提交 `1c054a027420b5410c6f6feb344e27e001ae1af1` 原位更新到四台宿主，验证幂等 `up`（保持 QEMU 进程、VM UUID 与磁盘 inode 不变）、两轮客机 SSH、`stop`/`start`、`/data` 数据盘读写、Debian locale/XFS、控制节点到各节点 SSH 以及 Ansible 配置读取（两台 Mac 额外跑通 7 节点 `ansible all -m ping`）。详细计时样本见 [0.8.0 发布说明](/zh/blog/release/0.8.0/)。

### Barn 0.7.0 — 2026-09-16

- **发布 CI 与公开制品**：提交 `9c6d4896d93733d1cb60a7e5d8591e9a06659c9d`（`v0.7.0`）通过[源码 CI](https://github.com/pgsty/barn/actions/runs/35118137961)、[打包快照工作流](https://github.com/pgsty/barn/actions/runs/35118137990)与[标签发布工作流](https://github.com/pgsty/barn/actions/runs/35119206685)。全部 20 个公开资产通过匿名下载与摘要核验，`darwin/arm64` 与 `linux/amd64` 公网安装脚本验证通过，`pgsty/infra/barn` Formula 通过本地升级与 `brew test`。
- **Ubuntu `amd64`/KVM 存储与中断恢复矩阵**：实测损坏的 `ext4`/`XFS` 数据盘自动重置（`3.2 秒`恢复并保留运行中 QEMU 进程）、`recreate` 保留持久盘、探测失败与忙碌挂载保护（保留原有数据与磁盘 UUID）、只读 9p 共享降级回退，以及在 `3.3 秒`内接续恢复一台此前因出网探测失败而中断的 `0.6.0` 虚拟机（由于 `0.6.0` 已清理暂存的控制节点私钥，恢复后按预期报告 `control-ssh` 告警，详见 [0.7.0 发布说明](/zh/blog/release/0.7.0/)）。镜像目录保持 `2026090501`。

### Barn 0.6.0 — 2026-09-05

- **发布 CI 与公开制品**：完成生命周期、命令交互、发布元数据与 CI 测试夹具审查后，提交 `057774e3a13477782a2ae07bd71127d03c0f1ae7`（`v0.6.0`）通过 Go `1.27.1` [源码 CI](https://github.com/pgsty/barn/actions/runs/33959205857)、[打包检查](https://github.com/pgsty/barn/actions/runs/33958857302)（`13d9d70`）与[标签工作流](https://github.com/pgsty/barn/actions/runs/33959431603)，生成并校验全部 20 个发布资产。在 `darwin/arm64` 隔离目录中验证了从 `0.5.0` 升级至 `0.6.0`、`barn init` 与 Ubuntu 24.04 `barn plan`。
- **macOS `arm64`/HVF 生命周期验收**：验证首次启动、不重启控制节点的在线扩容、控制节点到同伴节点 SSH、`stop`/`start`、`reload`、局部 `recreate`、缩容、客机 `/etc/hosts` 刷新、无效镜像 `reload` 与冲突局部 `recreate` 的停机前拦截、部分节点异常时的 `status` 展示，以及 SSH 退出码 `255` 原样透传。
- **镜像目录 `2026090501`**：将默认镜像切换为 `u24:stable`，合并 `2026090302` 的 Debian/Rocky 更新，全部 27 个产物通过字节校验并在两个官方端点完成隔离客户端 `barn update` 验签。

### Barn 0.5.0 — 2026-09-03

提交 `fc85b65ff6a24b0933b56ae1179be9ada2ba91b1`（`v0.5.0`）通过 Go `1.27.1` 源码门禁与 GoReleaser 打包检查并发布 20 个预发布资产。`0.5.0` 新增无需确认的整套部署清理命令 `barn purge`，将全球默认镜像源设为 `https://repo.pigsty.io/barn` 并提供 `--mirror` 切换 `https://repo.pigsty.cc/barn`，移除镜像下载时的隐式上游 URL 回退，并新增锁定摘要的八目标 Debian/Rocky 官方候选镜像构建脚本 `build-official.py`。

### Barn 0.4.0 — 2026-09-02

通过 `make check` 及发布工作流的归档、DEB/RPM、SBOM、校验和、安装脚本与 Homebrew Formula 门禁。`barn up` 支持在未初始化的交互式终端宿主上自动引导执行 `setup`，`vm_disks[].fs` 默认值改为 `auto`，客机就绪失败报错附带最后一行错误详情，并统一了全命令行的输出样式。

### Barn 0.3.0 — 2026-09-02

通过 `make check` 及全部发布打包门禁。将镜像目录刷新改为显式的 `barn update` 与 `barn image sync` 操作，并在客机就绪失败时输出各节点所处阶段与对应的 `barn logs` 排查命令。

### Barn 0.2.0 — 2026-09-01

提交 `59d1b62aebb3d044a317e4006cc8a0bf56f4feaf`（`v0.2.0`）通过源码 CI、打包工作流及本地四平台归档、DEB/RPM 与 SPDX 校验。`darwin/arm64` HVF 真机重放验证了选定节点 `u24-1` 的创建/SSH/停启、已缓存 `el9-1` 的增量创建、包含未创建节点的全局 `status`，以及全局 `destroy` 与 SSH 配置片段清理；Ubuntu 26.04 `amd64`/KVM 验证了存量四节点部署的状态审计与控制客机连通。

### Schema-3 镜像目录收口 — 2026-08-29

镜像目录 `2026082903`（9 个系列、27 个产物，SHA-256 `571b1ff9c7d4d42355df3392ea62a339471c2d01d868669a7625fac8b93f245d`，生产公钥 `4686B39A40F9B562` 签名）通过了内置目录与公网端点逐字节比对、全部 27 个 `qcow2` 文件（共 19 GiB）全量 SHA-256 扫描，以及 `darwin/arm64` 空白客户端拉取 `d13:stable`（`409.3 MiB`）与 `qemu-img` 结构检查。

### 0.1.0 候选验证 — 2026-08-28 与 2026-08-29

在 `0.2.0` 发布前验证了两项关键修复：

- **QMP 套接字局部恢复**：在 `darwin/arm64` 四节点环境中，当其中两台运行中节点的 QMP 套接字被外部删除后，Barn 仅重启受影响的两台节点（`13.7 秒`恢复就绪），其余两台正常节点的 boot ID 保持不变。
- **无 QEMU 环境下的目录查询**：消除了 `barn image list` 与源码测试在不校验本地 `qcow2` 缓存时对 `qemu-img` 的依赖，使 `make check` 在未安装 QEMU 的纯净机器上即可跑通。

### EL7/EL8 兼容性恢复 — 2026-08-28

提交 `7c666c7` 修复了破坏性操作前的运行时预检顺序与签名镜像目录基线迁移逻辑，补充回归测试并恢复了 `el7`/`el8` 支持。镜像目录 `2026082801`（9 个系列、17 个镜像产物及 2 份 `socket_vmnet` 归档）通过全量 SHA-256 与签名校验；`darwin/arm64` 隔离重放通过内置 TCG 兼容规则启动 Rocky Linux 8.10 `arm64`，`stop`/`start` 后在 `44.2 秒`内达到就绪状态，验证了 NetworkManager、固定 IP、`dba` UID/GID `88` 与客机初始化标记。

### 真机重放基线 — 2026-08-27

在 `darwin/arm64` 与 `linux/amd64`（`mx`）两台宿主上验证了固定 IP、SSH 就绪、默认 CPU/内存/根盘/数据盘、`cloud-init`、`stop`/`start`、跨目录命令执行、扩容期间保持控制节点 boot ID 不变、控制节点到同伴节点 SSH、忽略非 Barn 管理的 Pigsty 字段变更，以及仅在显式 `destroy` 时删除虚拟机。Linux 宿主额外验证了免密 `sudo` 自动化、Debian `qemu-bridge-helper` 用户组授权、普通用户 QEMU 挂桥测试、挂有四个 tap 接口时拒绝卸载网络，以及 `destroy` 后精确还原宿主状态。
