---
title: "RC6 开发候选：Owner-scope Tier 1 交付"
linkTitle: 2026-08-25 RC6 候选
description: RC6 准确身份、四个要求的原生产品通过、Durable 网络事务、可复现本地 Archive，以及保持未发布的边界。
date: 2026-08-25
weight: 5
categories: [开发]
tags: [RC6, Go 1.27, Quick, Private, QEMU, macOS, Linux]
icon: fa-solid fa-vial-circle-check
---

> [!CAUTION]
> Barn 之前的历史记录。本页保留前任候选的准确身份，不证明当前 Barn 二进制或路径。
> 当前边界见[当前状态](/zh/docs/about/status/)。

Piglet `1.0.0-rc.6` 是单一 Native-QEMU 路径的 Owner-scope 本地开发候选。它在两条 Tier 1
宿主上关闭了要求的 Quick 与准确四节点 `full` 场景，并加入 Durable 特权网络事务。
它刻意不是公开 Release。

> [!WARNING]
> 没有执行 Homebrew 操作、公开 Tag、远端 Push、GitHub Release、Package Repo、生产签名、
> Attestation 或支持承诺。下面 Hash 只标识保留本地 Artifact，本站不提供下载。

## 冻结身份

| 字段 | RC6 值 |
| --- | --- |
| Version | `1.0.0-rc.6` |
| Source Commit | `7db733184463cc189ffa738335c213fc9a2982de` |
| Go | `go1.27.0` |
| Source Epoch | `1787657920` |
| Build Timestamp | `2026-08-25T11:38:40Z` |
| Channel | `development` |
| Signature / Attestation | `false` / `false` |
| 准确 `full` Profile SHA-256 | `912fea61bf1602c2a437570561a6ab4d0a5a8c152695147ad9e96ae831bc9336` |

## 四个要求的产品场景

| 宿主 | 场景 | 结果 | Guest 契约 |
| --- | --- | --- | --- |
| macOS arm64 / HVF | Quick | PASS | Ubuntu 24.04.4、`dba` UID/GID 88、2 vCPU、64 GiB 根盘、64 GiB `/data` |
| Linux amd64 / KVM | Quick | PASS | 相同契约 |
| macOS arm64 / HVF | 准确 `full` | PASS | `.10`–`.13`、UID 88、64 GiB 根盘、128 GiB 数据盘、2/1/1/1 vCPU、四向互通 |
| Linux amd64 / KVM | 准确 `full` | PASS | 相同契约 |

最终八台 Full Profile Guest 全部报告 Ubuntu 24.04.4。断言完成后，项目通过 Piglet Destroy；
共享 Image Cache、Project Marker 与 Key 刻意保留。

## Durable 原生网络

Network Install/Uninstall 现在使用一套 root-owned Strict-prefix Transaction：

- Root Plan 返回与 Owner/Host/Prestate 绑定的 Token；
- Apply 在宿主全局锁内重新规划，只接受该 Token；
- 第一次修改前发布类型化、Fsync Journal；
- 每个固定 Action 在验证准确 Postcondition 后 Checkpoint；
- 中断后普通 Private 修改阻止，直到显式 Forward 或 Rollback Recovery Plan 单独经 Token 批准。

Darwin 完成真实中断 Forward Recovery，最终处于默认 Host Mode 的 Protected/Healthy 状态。
Linux 在最终 Adversarial Patch 前完成真实 Install、Rollback/Retry、四节点运行、Uninstall 与宿主
恢复。最终 Patch 关闭 Socket State 规范化、过宽 Systemd Enable、NetworkManager 顺序与
Field-scoped Recovery Effect 问题，随后通过整合 Source/Race Gate。

按 Owner 最终指令，最后 Patch 后没有再运行 VM 或网络测试。因此 Post-audit Linux
Install/Uninstall/Reinstall Replay 明确为**未运行**；本页不会把 Source/Race Evidence 升格成
原生结果。

## macOS Shared Mode 与子网冲突

受支持默认仍是 socket_vmnet Host Mode。Shared Mode 在证明空闲的替代子网上通过双节点契约，
但它是显式 Fallback，不是隔离边界。

历史默认子网失败为 `VMNET_SHARING_SERVICE_BUSY (1009)`。VirtualBox 是合理污染候选，但未被
证明为该事故 Owner。最终迁移前立即观察到的子网 Interface 是旧 Piglet 创建的 `bridge100`。
Preflight 现在按身份拒绝外部 Interface，不会因为 `.1/24` 地址匹配而接管。操作者可以移除已确认
Owner，或把整套实验室迁移到一份带 Warning 的规范 RFC1918 `/24`；Piglet 永远不会只修改 Guest
地址，也不会随机选择逃生子网。

## 可复现本地 Archive

两棵独立本地 RC6 输出均通过严格 Release Verifier，四个 Archive、Checksum、Release Metadata
与 Formula 字节一致：

| Archive | SHA-256 |
| --- | --- |
| Darwin amd64 | `1295288ff198b53fcb761a6e8794087d75a46105fc19980fabcd44f0c70fb9ef` |
| Darwin arm64 | `308310b0f2d179f98c8be78ea09f89d226167072c936387bc42d717a922ec0c6` |
| Linux amd64 | `547a61f6cc0768071df349cbf5c17d7ddfe3ab3cea59e6b4026e3e3e616a5550` |
| Linux arm64 | `afc9ce1043d377cc3b4ef8bdf77826a8139a8c839685025853e8bee8100c6a2e` |

Formula 只是惰性 Build Artifact。更早候选执行过离线 RPM/DEB Consumption 与临时
Cosign/SLSA Round Trip，但这些只属于机制证据，不能改名为 RC6 Publication/Signing。

## 公开 GA 仍需完成

- 两条 Tier 1 的 Literal Reboot 持久性；
- macOS amd64 与 Linux arm64 的当前原生 Smoke；
- 刻意延期的 Linux 最终网络 Replay；
- 剩余 Image Normalization、字节可复现决策、Hosting 与主备 Manifest Key Custody；
- 生产 Release Identity、Signing/Attestation、公开 Homebrew/Linux Package 渠道与干净宿主消费；
- 持久 Owner-operated macOS HVF Runner 与明确发布授权。

当前维护边界见[教程](/zh/docs/start/tutorial/)、[设计](/zh/docs/about/design/)与
[当前状态](/zh/docs/about/status/)。
