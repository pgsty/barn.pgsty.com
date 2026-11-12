---
title: "Barn 1.2.0 发布准备与最终验收"
description: "Barn 1.2.0 的发布门禁、升级兼容性、打包与真机验收。"
date: 2026-11-12
lastmod: 2026-11-12
weight: 76
categories: [Design]
tags: [Release, Testing, CLI]
icon: fa-solid fa-clipboard-check
---

**状态，2026-11-12**：[Barn 1.2.0](https://github.com/pgsty/barn/releases/tag/v1.2.0) 已作为 stable/latest 发布。下方记录最终验收结果，候选版本章节保留早期审查及其原始范围。

## 最终发布 {#final-release}

标签 `v1.2.0` 指向 `90f615804b823b4eb491101e642073dcd37a9700`。[源码/Mac CI](https://github.com/pgsty/barn/actions/runs/43121333312)与[完整打包 CI](https://github.com/pgsty/barn/actions/runs/43121333418)在打标签前通过同一提交。437 个已审查构建输入均与候选摘要清单一致；正式打包前再次通过签名镜像目录门禁。

GitHub 签名 secrets 仍未配置，本次采用文档中的本机签名流程。Apple 接受公证提交 `165b486b-5055-4eca-a595-54bed6bdd6c1`；`make release-local` 通过归档、DEB/RPM、SPDX、helper 配对、时间戳与软件包/归档一致性检查。下载后的 CLI/helper/App 通过 Developer ID、staple 与 Gatekeeper 检查。20 个 draft 附件和全部 20 个匿名公开下载的大小与 SHA-256 均匹配已核验字节。

最终回下载归档通过 Linux/KVM 18 步和原生 Mac 全部 15 阶段。补充原生 UI 检查确认桌面登录、双向纯文本剪贴板、关闭窗口后 VM 与 SSH 继续运行，以及正常关机。隔离的 1.1.0 → 1.2.0 升级和重复安装通过；`darwin/arm64`、`linux/amd64` 均通过公网 latest 与指定版本安装。[Homebrew 更新](https://github.com/pgsty/homebrew-infra/commit/f1b83ae)覆盖四平台，真实 1.1.0 → 1.2.0 升级、`brew test`、style 和严格在线 audit 通过。

最终 Mac 验收保留了一次访问 Apple HTTPS 时的 TLS 超时。相同请求随后返回 HTTP 200；续跑前重新核验双机身份、磁盘哨兵和基础镜像摘要，再完成其余阶段。GUI 验收后测试 VM 已停止。GitHub 直连下载超时后改用宿主已有代理，公开下载未携带认证；失败日志均予保留。

首页保留明确标注日期与版本的 1.1.0 录像，并说明 1.2.0 的默认值和输出变化。重录四节点首次运行需要空闲的 `.10–.13` 地址，本次发布期间由宿主已有 VM 占用。发布身份与公开渠道证据另见[验证历史](/zh/docs/about/history/#release-1-2-0)。

1.2.0 站点更新 `b9e6498` 通过[站点 CI](https://github.com/pgsty/barn.pgsty.com/actions/runs/43125783766)，并成为 Cloudflare 生产部署。生产构建检查了 303 个 HTML 页面；19 项公开检查覆盖双语发布、安装与命令页面、canonical URL、站点地图、搜索索引、robots 和真实 404。最后一轮浏览器连接超时，因此目视证据保留此前本地抽查的范围。

## 候选版本身份 {#candidate-identity}

下表记录准备工作开始时的状态，早于正式发布提交。

| 项目 | 本次核对的状态 |
|---|---|
| 源码仓库 | 本地 `main` 为 `6ab0cd5`，领先已拉取的 `origin/main`（`b2cc8da`）三个提交；另有未提交的 hosts 改动 |
| 文档仓库 | 本地 `main` 为 `bc7968a`，领先已拉取的 `origin/main`（`d392cd5`）三个提交；命令参考与校正尚未提交 |
| Snapshot | `.goreleaser-preflight-1.2.0-20261112`，版本 `1.1.1-next`，二进制提交标识为 `uncommitted` |
| 源码输入 | 437 个源码、测试、原生组件与打包文件的摘要清单 SHA-256 为 `9a4d4dd378d4b5762a4d06bd8e19830a09e0919e808f5fffc4c154fbdf55e01a` |
| 镜像目录 | Revision `2026110502`，默认镜像为原生架构的 `u24:stable` |
{.wide .expand}

Snapshot 版本按现有 `incpatch` 规则从最近标签 `v1.1.0` 推导。正式 `1.2.0` 制品随后已从最终的 `v1.2.0` 提交重新构建；snapshot 二进制将修改工作树明确标记为 `uncommitted`。

## 已完成的收尾 {#resolved}

- 默认 shell 优先使用 GoReleaser 2.18.3，而源码要求 2.20.1。本次验证使用已下载的锁定工具，打包前执行 `packaging/check-toolchain.sh all` 核实了全部版本。
- Changelog 和发布草稿遗漏了 Linux 默认规格从 2 vCPU / 4 GiB 改为 1 vCPU / 2 GiB。现已补充显式设置 `vm_cpu: 2`、`vm_mem: 4GiB` 的保留方法，并用两个版本的二进制对比了隐式与显式清单。
- 发布草稿补齐了 `all.vars.vm_hosts` 和 `hosts install -f`。实现和测试随后纳入提交 `ad74cc9`；候选版已在创建 VM 前通过清单预览检查。
- 根目录的 `.idea/` 和本地 `barn.yml` 已加入忽略规则，文件仍保留在磁盘上。原有源码修改和历史文档删除均予保留。

## 已通过的门禁 {#completed-gates}

| 门禁 | 证据 |
|---|---|
| 源码 | `make check` 通过：单元与竞态测试、静态分析、四平台构建、安装器和镜像流水线边界、许可证检查 |
| 原生组件 | `make mac-native-test` 通过桥接、镜像、菜单和退出提示测试 |
| 镜像目录 | 两个官方源均通过签名验证、全新数据根激活、内置字节比对，以及各自 17 个 stable 制品的大小与可达性检查 |
| 打包 | 使用新构建的原生载荷并设置 `BARN_MAC_REQUIRE_PAYLOAD=1`，`make release-snapshot` 通过归档、Linux DEB/RPM、SPDX、校验和、helper 配对、时间戳与归档/软件包一致性检查 |
| Linux 运行时 | 在 Ubuntu 26.04.1 / x86_64、KVM 上使用解包后的 snapshot，18 步操作全部通过 |
| Mac 运行时 | 在 macOS 27.0.1 / arm64、Xcode 27.2 上使用解包后的 snapshot，15 阶段自动生命周期验收全部通过 |
| 升级 | 使用公开 1.1.0 归档创建的 VM 由候选版接管后保留进程与身份，根盘扩容和销毁通过 |
| 文档 | 生产 `make check` 与单独的含草稿构建通过内链和资源检查，分别覆盖 301 与 303 个 HTML 页面；浏览器抽查了中文命令索引、英文生命周期参考和中文发布准备记录 |
{.wide .expand}

目录字节的 SHA-256 仍为 `d41e46d20bc57cb1b071e3919a27a8f7f703df2addca879970a528e7ab004065`，因此无需更新内置目录。本次目录门禁未流式重算所有制品摘要；Linux 验收下载了选用的镜像并校验其摘要。`govulncheck` 未发现可达漏洞，未使用模块的报告保留在候选版发布说明中。常规源码套件跳过了原生离线镜像修改；本候选版本未修改镜像流水线。

## Linux 验收 {#linux-acceptance}

两台隔离客机分别使用 Debian 13 `20261103.2651.1` 和 Rocky Linux 9 `9.8.20260525.2`，规格为 1 vCPU / 1 GiB、12 GiB 根盘和持久化的 1 GiB XFS 数据盘。验收复用了宿主已有的 Barn 网络。

- 运行中的 ext4 根盘扩至 14 GiB 后继续运行；重复目标保留 QEMU PID，缩至 13 GiB 的请求在修改磁盘前被拒绝。
- 停止状态的 XFS 根盘经过临时启动扩至 14 GiB，并回到停止状态；重复目标保留根盘文件的修改时间。
- 人为使 `resize2fs` 失败后，16 GiB 目标保留可恢复的 `guest` 记录；恢复工具并重试后完成文件系统扩容。
- 在 `qemu-img` 扩大镜像后终止 CLI，18 GiB 目标保留 `image` 记录；重试完成扩容并恢复运行状态。
- VM UUID、generation、磁盘序列号、分区身份、文件系统 UUID、SSH 主机密钥以及根盘/数据盘哨兵在扩容和恢复过程中保持不变。串行停止（`-p 1`）与不限并发启动（`-p 0`）通过。
- 测试节点及显式选择的持久盘均已销毁，宿主 SSH 配置与 `/etc/hosts` 的字节与验收前完全一致。

首轮脚本将镜像缓存目录建为组可写，Barn 在创建任何客机前拒绝了该目录。修正为私有权限后重新验收，失败证据另行保留；这属于验收脚本的准备错误。

另一次升级验收使用公开的 1.1.0 归档（SHA-256 `09fa37b35ac15763320898bdf81fe0051e83f6b8f3a4898fb01149e6c2611926`）创建客机。候选版正确读取其已应用的 2 vCPU / 4 GiB 状态；在清单中补齐显式 CPU/内存后，`up` 保留了运行中的 PID 和 VM UUID，随后 `resize -D 14GiB` 将旧的 12 GiB 根盘扩容，同时保留 machine ID、主机密钥、generation 与数据哨兵。销毁后宿主 SSH 配置恢复到原始字节。初轮脚本错误地假定 Linux `ssh` 会为 `sh -c` 参数加引号；文档约定其保留原生 SSH 语义，需要调用者处理 shell 引号。续跑改用明确引用的 SSH 命令，保留了首轮失败日志。

实现与回归测试位于 `internal/private/root_resize.go`、`internal/private/root_resize_guest.py`、`internal/private/root_resize_test.go`、`internal/private/concurrency_test.go` 与 `cmd/barn/lifecycle_parallel_test.go`。此前的 [arm64 ext4/XFS 验收](../root-disk-growth/#acceptance)保留原日期和测量值。本轮尚未对 MBR 布局和原生 Linux/arm64 宿主补做真机重放。

## Mac 验收 {#mac-acceptance}

测试目录通过 APFS 克隆复用了已准备好的 macOS 27.0 基础镜像（`26A428`），并关闭了自动宿主 SSH 配置集成。15 阶段脚本覆盖双机身份隔离、客机账户策略、独立网络、DNS/HTTPS、远程参数与退出码、共享目录读写、停止/启动、CPU/内存配置、两台 VM 上限、重建后的身份轮换、基础镜像不变性、重复 `up`，以及销毁一台 VM 时保留另一台。自动验收结束后，保留的测试 VM 已停止。

解包后的 App 还打开了保留 VM 的桌面，目视检查确认其自动登录到 macOS Finder 桌面，随后正常关闭 VM。本次未确认关闭窗口后的行为或剪贴板传输。Snapshot 使用 ad-hoc 签名；最终 Developer ID 签名、公证版本随后通过了上方记录的 Gatekeeper、安装、关闭窗口和剪贴板检查。

## 发布执行记录 {#remaining}

1. 源码变更纳入 `ad74cc9`、`90f6158`，命令参考与文档核对单独纳入 `24ff1e2`；两个仓库均已推送并通过 CI。
2. 源码与打包 CI 通过 `90f6158` 后，创建并推送 `v1.2.0` 标签。
3. 目录门禁通过后，按[本机 Mac 发布流程](/zh/docs/about/mac-release/#local-release)构建同身份的签名、公证载荷，完整发行包通过 `make release-local`。
4. 最终归档验收与全部 20 个 draft 附件回下载通过后，公开为 stable/latest；随后核验全部 20 个公开下载及两平台安装器。
5. Homebrew 与双语指南更新到 1.2.0，涵盖默认规格、命令选项、升级说明与发布证据。
{.steps}

本次使用已有本机 Developer ID 身份及已保存的公证 profile，未导出密钥或修改签名凭据。
