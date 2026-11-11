---
title: "Main 与命令参考核对记录"
description: 2026-11-11 Barn 审查的 Git 状态、版本边界、命令覆盖与验证依据。
date: 2026-11-11
weight: 5
categories: [Design]
tags: [CLI, Documentation, Validation]
---

**核对日期：2026-11-11。** 两个仓库都在 `main`，但工作区均不干净，也未与拉取后的远端分支一致。源码检查在本次工作区上通过；文档已补齐[完整命令参考](/zh/docs/reference/commands/)，逐项区分稳定版、本地 main 和未提交功能。

## Git 与发布状态 {#git-state}

| 仓库 | 本地 main | 拉取后的 origin/main | 审查开始时的状态 |
|---|---|---|---|
| `pgsty/barn` | `6ab0cd5` | `b2cc8da`（`v1.1.0`） | 领先 3 个提交；11 个已跟踪路径有变更，另有未跟踪的 `.idea/`、`barn.yml`、`cmd/barn/hosts_inventory_test.go` |
| `pgsty/barn.pgsty.com` | `bc7968a` | `d392cd5` | 领先 3 个提交；四个参考文件已修改，六个设计文章文件未跟踪 |
{.wide .expand}

GitHub 最新正式发布仍是 2026-11-09 发布的 [v1.1.0](https://github.com/pgsty/barn/releases/tag/v1.1.0)，远端没有 v1.2.0 标签，本地 1.2.0 发布说明标记为草稿。

源码的三个本地提交分别引入 Linux 生命周期并发（`158786a`）、统一规格输入与可恢复根盘扩容（`1e24768`）、1.2.0 工具链和发布准备（`6ab0cd5`）。`vm_hosts` 解析与 `hosts install -f` 接口仍未提交，因此工作区构建包含远端 main、甚至本地 HEAD 提交中都不存在的接口。

本次保留了已有修改与删除，只修改文档，没有创建提交、推送分支或部署站点。要让 main 收敛为干净且共享的状态，需审阅 hosts 实现并与测试一同提交，确定已有未跟踪文件和两个根目录历史文档删除的归属，再处理三个本地提交与远端的同步。源码和站点分别提交，分别决定发布。

## 发现与修正 {#findings}

| 发现 | 修正 |
|---|---|
| Reference 以命令摘要为主，缺少逐命令完整用法 | 按七个命令组补齐 57 条操作命令，每条都有语法、全部局部选项、示例与作用范围；根命令、帮助和分组行为集中在索引页 |
| 稳定版 1.1.0、本地 main 和未提交 hosts 功能容易混淆 | 增加带日期的版本基线和逐选项可用性，修正配置、项目状态、源码构建和日常操作中的版本边界 |
| README 未区分版本，直接称默认规格为 2 vCPU/4 GiB | 保留发行版默认值，同时注明本地 main 默认 1 vCPU/2 GiB |
| 开发文章链接远端 main 中尚不存在的新文件 | 改为本次核对的本地提交与源码、测试的仓库相对路径 |
| 贡献者说明仍称 Ubuntu 制品保留上游字节 | 按目录溯源修正：Ubuntu 22.04/24.04/26.04 已离线归一化，包含 `dba`、UID/GID 88、区域设置及核验过的上游 XFS 工具；通过直接流水线构建，未进入八镜像包装器矩阵 |
| Mac 命令摘要暗示所有设置变更都必须停机 | 明确剪贴板配置可在运行时保存，下次启动生效 |
{.wide .expand}

原有镜像参考的九个家族、17 个制品、精确 stable 版本和别名与 `internal/image/default-catalog.json` 一致。归一化镜像与发行版原始镜像的区别，以目录 `source_user` 和溯源记录为依据。命令参考也保留了自定义 HTTPS/本地仓库允许无签名目录的规则、分组别名、远程命令显式 `--` 分隔符，以及 `purge`、`destroy` 和 Mac 命令不同的确认语义。

## 实现审查范围 {#implementation-review}

重点核对了规格优先级与类型校验（`cmd/barn/vm_inputs.go`、`internal/config/inventory.go`、`internal/config/resources.go`）、并发上限（`internal/private/concurrency.go`），以及根盘扩容恢复（`internal/private/root_resize.go`、客机辅助脚本和 `internal/state/root_resize.go`）。根盘扩容在修改镜像前核对受管根盘路径、序列号和 QEMU 已停止证据，持久化恢复阶段，检查客机分区及文件系统身份和容量，并保留原电源状态供重试恢复。

对未提交 hosts 扩展，核对了仅属于清单的映射、大小写无关冲突检测、子网范围、无部署状态下的预览，以及后续命令保留显式清单路径。相关回归在 `cmd/barn/hosts_inventory_test.go`、`internal/config/inventory_test.go`、`internal/hostconfig/hostconfig_test.go` 中，应与实现一起提交。

## 验证依据 {#validation}

- **源码**：当前工作区通过 `make check`，涵盖模块、Shell、维护归属、单元与竞态测试、vet、Staticcheck、死代码交集、errcheck、漏洞扫描、四平台交叉编译、镜像流水线边界、安装器、Mac 载荷与许可证检查。扫描器报告没有可达漏洞，另有一项位于未使用模块包中的漏洞。常规边界测试明确跳过了原生离线镜像修改测试。
- **镜像仓库**：`make catalog-check` 在全新临时目录中激活两个官方签名目录，逐字节匹配内置 revision `2026110502`，并检查两源各 17 个 stable 制品的可达性与大小。目录 SHA-256 为 `d41e46d20bc57cb1b071e3919a27a8f7f703df2addca879970a528e7ab004065`。未流式读取全部制品重算摘要（`verified_bytes: false`）。
- **CLI 覆盖**：分别构建 v1.1.0 与工作区 CLI 并读取真实帮助。每种语言覆盖全部 57 条操作命令、174 项可见局部选项，稳定版标记与发行标签构建的帮助逐项比较；双语标题锚点、语法块和命令示例对齐。
- **示例**：两种构建的四个模板均在隔离临时 `BARN_HOME` 中通过 `init`、`validate`、`plan`，并以数值检查默认规格、开发版缩放和根盘容量输入。教程与参考中的五份完整清单示例也通过了对应版本的校验。

- **站点**：生产模式 `make check` 通过，内部链接、锚点和资源检查通过；仅有预期的上游 LibSass 弃用提示。内置浏览器控制工具超时，本次未完成页面视觉检查。

本次文档审查没有执行真机 VM 生命周期、宿主网络修改或提权 hosts 安装。交付运行时变更或正式版本时，目标平台真机验收与签名发行包验证仍需分别执行。
