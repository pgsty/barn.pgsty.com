---
title: "RC6 开发候选：Owner-scope Tier 1 交付"
linkTitle: 2026-08-25 RC6 候选
description: RC6 准确身份、四个原生产品场景验证、可持久恢复的网络事务、可复现本地归档，以及未公开发布的范围。
date: 2026-08-25
weight: 110
categories: [开发]
tags: [RC6, QEMU, 网络]
icon: fa-solid fa-vial-circle-check
---

> [!NOTE]
> Barn 前身历史归档（`Piglet 1.0.0-rc.6`，2026-08-25）。该候选版为本地验收里程碑，未创建公开 GitHub Release 或软件包仓库，下方 SHA-256 摘要用于记录当时的本地构建产物。当前 Barn 的用法与支持范围请参见[使用文档](/zh/docs/)与[支持状态](/zh/docs/about/status/)。

Piglet `1.0.0-rc.6` 是在两类 Tier 1 原生虚拟化平台（`macOS arm64 / HVF` 与 `Linux amd64 / KVM`）上完成 Quick 及四节点 `full` 场景验收的本地开发候选版，并引入了基于持久化事务日志的特权网络安装与崩溃恢复机制。

## 冻结构建身份

| 字段 | RC6 值 |
| --- | --- |
| 版本 | `1.0.0-rc.6` |
| 源码提交 | `7db733184463cc189ffa738335c213fc9a2982de` |
| Go | `go1.27.0` |
| 源码时间戳 | `1787657920` |
| 构建时间戳 | `2026-08-25T11:38:40Z` |
| 通道 | `development` |
| 签名 / 证明 | `false` / `false` |
| 指定 `full` 配置模板 SHA-256 | `912fea61bf1602c2a437570561a6ab4d0a5a8c152695147ad9e96ae831bc9336` |
{.wide}

## 四个原生产品场景

| 宿主 | 场景 | 结果 | 客机约定 |
| --- | --- | --- | --- |
| macOS `arm64` / HVF | Quick | PASS | Ubuntu 24.04.4、`dba` UID/GID 88、2 vCPU、64 GiB 根盘、64 GiB `/data` |
| Linux `amd64` / KVM | Quick | PASS | Ubuntu 24.04.4、`dba` UID/GID 88、2 vCPU、64 GiB 根盘、64 GiB `/data` |
| macOS `arm64` / HVF | 指定 `full` | PASS | `.10`–`.13`、UID 88、64 GiB 根盘、128 GiB 数据盘、2/1/1/1 vCPU、四节点互通 |
| Linux `amd64` / KVM | 指定 `full` | PASS | `.10`–`.13`、UID 88、64 GiB 根盘、128 GiB 数据盘、2/1/1/1 vCPU、四节点互通 |
{.wide}

八台 `full` 场景客机全部正常启动 Ubuntu 24.04.4 并通过契约断言；测试结束后通过 CLI 正常销毁项目，并按预期保留了共享镜像缓存、项目标记与密钥。

## 持久化原生网络事务

宿主网络安装与卸载采用由 `root` 持有、严格限定路径前缀的事务模型：

- `root` 规划阶段生成绑定调用用户、宿主身份与变更前状态的令牌；
- 执行阶段在宿主全局锁内重新校验计划，且仅接受该令牌；
- 任何宿主配置修改开始前，先写入结构化事务日志并执行 `fsync` 落盘；
- 每个固定步骤仅在后置条件校验通过后记录检查点；
- 若事务中途中断，普通网络变更会被锁定，直至显式批准继续执行（forward）或回滚（rollback）恢复计划。

macOS 宿主通过了真实中断后的继续恢复验证，最终收敛至受保护的默认 `host` 模式；Linux 宿主完成了真实安装、回滚重试、四节点运行、卸载与宿主还原测试，并在最后合入了收紧套接字状态规范化、`systemd` 单元启用范围、NetworkManager 顺序及恢复字段范围的补丁（通过全量源码检查与 `-race` 竞态测试）。

## macOS Shared Mode 与子网冲突处理

macOS 默认支持模式为 `socket_vmnet` `host` 模式；`shared` 模式作为需显式指定的备选模式，也在空闲替代子网上通过了双节点契约验证。

测试期间，当宿主机残留旧版创建的 `bridge100` 接口时，默认子网会触发 `VMNET_SHARING_SERVICE_BUSY (1009)`。网络预检严格凭接口归属标记识别自有网卡，绝不会仅因现有网卡配置了 `.1/24` 地址就直接接管。遇到子网冲突时，操作者可清理占用接口，或将整套实验环境显式迁移至另一个规范的 RFC 1918 `/24` 子网——运行时绝不会单独改动客机 IP 或随机挑选子网。

## 可复现本地归档

两次独立执行的本地 RC6 构建产出了字节完全一致的四平台归档、校验和、发布元数据与 Homebrew 配方：

| 归档 | SHA-256 |
| --- | --- |
| Darwin `amd64` | `1295288ff198b53fcb761a6e8794087d75a46105fc19980fabcd44f0c70fb9ef` |
| Darwin `arm64` | `308310b0f2d179f98c8be78ea09f89d226167072c936387bc42d717a922ec0c6` |
| Linux `amd64` | `547a61f6cc0768071df349cbf5c17d7ddfe3ab3cea59e6b4026e3e3e616a5550` |
| Linux `arm64` | `afc9ce1043d377cc3b4ef8bdf77826a8139a8c839685025853e8bee8100c6a2e` |
{.wide}

## 公开发布前待办项

在 RC6 节点上，距离公开发布尚余以下工作：
- 两类 Tier 1 宿主的物理重启持久性验证
- macOS `amd64` 与 Linux `arm64` 原生冒烟测试
- 包含最终补丁的 Linux 网络安装/卸载/重装真机重放
- 客机镜像规范化构建、线上托管与主备清单密钥管理
- 正式发布标签、Homebrew 软件源与 DEB/RPM 渠道发布及全新宿主安装验证

后续 Barn 版本对上述工作的落地情况请参见[快速上手](/zh/docs/start/tutorial/)、[架构设计](/zh/docs/about/design/)与[支持状态](/zh/docs/about/status/)。
