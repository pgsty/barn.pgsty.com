---
title: "从上游镜像到签名目录"
linkTitle: "镜像更新证据"
description: "Barn 如何区分上游版本元数据、目录事实、运行时支持与正式发布验收。"
date: 2026-11-08T10:00:00+08:00
weight: 60
categories: [设计]
tags: [镜像, 供应链, 发布]
icon: fa-solid fa-shield-halved
lastmod: 2026-11-09
---

镜像核查回答的问题比镜像发布更窄：它可以找到上游更新文件，但 Barn 只有在制品、运行时配置和启动路径都通过验证后，才能把文件加入签名目录。[镜像参考](/zh/docs/reference/images/)说明用户可见的目录契约；本文记录如何让目录更新可复现。

## “更新”有四种含义 {#four-meanings}

如果把四种独立的版本值混为一谈，镜像更新就容易出错：

| 数值 | 描述的对象 | 所需证据 | 能否单独更新目录 |
|---|---|---|---|
| 操作系统版本 | 发行版的版本或点版本，例如 Ubuntu `24.04 LTS` | 发布元数据与软件包或构建记录 | 不能 |
| 云镜像构建号 | 某次带日期的上游磁盘构建，例如 `YYYYMMDD` 格式的标识 | 带日期的目录、文件名与校验记录 | 不能；它只是来源候选 |
| Barn 版本 | Barn 归一化后的版本和修订后缀 | 镜像配方与目录映射 | 不能；必须能复现归一化过程 |
| 运行时支持 | Barn 是否能启动并使用该制品 | QEMU 配置、固件、网络、cloud-init 与 SSH 证据 | 必须满足 |
{.wide .expand}

Barn 版本中的后缀不一定是操作系统点版本。Debian、Ubuntu、Rocky 与 CentOS 使用不同的构建标识，Barn 还可能增加自己的归一化修订号；发布说明、源配方和目录条目必须保留这些命名空间的区别。

## 只比较同类制品 {#compare-like-with-like}

更新比较必须使用与当前目录条目相同的制品类别。通用云盘可以和另一份通用云盘比较；安装 ISO、容器归档、daily 构建或板卡专用镜像回答的是不同问题。发布页上较新的时间戳不足以直接替换 Barn 的源地址。

可复现的输入应使用带日期的上游 URL。`latest` 页面适合发现候选，随后必须还原到带日期的构建、确切的制品和对应校验记录。还要记录所选格式的摘要：qcow2 上传文件的摘要不能代替 raw 磁盘或压缩归档的摘要。

核查时还应并列保存操作系统元数据、云镜像元数据和 Barn 本地流水线元数据。如果流水线配方比内置目录更旧，正确结论是需要维护配方；不能用旧配方覆盖目录，让产品版本倒退。

## 识别配方与目录的漂移 {#recipe-drift}

2026-11-08 核对时，[`official-v1.json`](https://github.com/pgsty/barn/blob/v1.1.0/packaging/image-pipeline/official-v1.json) 的 Debian 12 目标仍选择 `20260923.2610.1`，而[内置目录 revision `2026110502`](https://github.com/pgsty/barn/blob/v1.1.0/internal/image/default-catalog.json) 已选择 `20261026.2643.1`。其来源构建为 `20261026-2643`，末尾 `.1` 属于 Barn 归一化修订。这是可以复核的本地元数据漂移案例，也说明重建已发布镜像前必须检查源配方。

上游输入摘要与归一化产物摘要要分别保留。客机定制会改变磁盘字节，目录必须对最终制品计算摘要。现有目录 provenance 已记录独立重建时归一化标记一致、制品字节却不同，因此没有承诺字节级可复现。配方可复现与输出逐字节一致是两项不同属性。

架构发现同样需要精确：发行版端口或安装 ISO 只是未来目标的一部分证据。Barn 当前只接受 `native`、`amd64` 和 `arm64`；新增镜像候选还需要完成[客机架构契约](/zh/blog/design/multi-architecture-boundary/)中的运行时工作。

## 目录条目就是运行时契约 {#runtime-contract}

对 Barn 来说，一个有效的镜像条目必须同时满足以下条件：

| 契约部分 | 必须满足的条件 |
|---|---|
| 制品 | 确切的路径、格式、字节大小和摘要唯一指向一个文件 |
| 客机架构 | 目录中的架构与请求的客机架构一致 |
| QEMU 配置 | Barn 选择正确的系统模拟器、机器类型、CPU 策略和加速器 |
| 固件 | 制品具备已验证的引导路径；UEFI 使用匹配的代码与每台 VM 独立的变量存储，BIOS 镜像走 BIOS 路径 |
| 客机初始化 | cloud-init 或镜像初始化路径创建预期的用户、密钥、主机名和网络 |
| 运行时测试 | 全新的临时 `BARN_HOME` 能启动到预期架构并达到 SSH 就绪状态 |
{.wide .expand}

因此，“上游有镜像”和“Barn 支持该镜像”是两句话。[镜像仓库契约](/zh/blog/design/repo-yaml-catalog-json/)把人工策略放在 `repo.yaml`，把生成的文件事实放在 `catalog.json`；运行时仍需要目标模拟器和冷启动检查。摘要正确但无法完成 SSH 的目录条目，不能算作可用的 Barn 镜像。

## 正式发布门禁 {#release-gate}

每次正式发布 Barn 前：

1. 从官方镜像仓库取得最新签名 `catalog.json` 并验证签名。
2. 将 revision、默认镜像以及每个 stable artifact 的路径、架构、摘要和大小与内置目录逐项比较；同步更新内置目录版本与日期，仓库源文件变化时更新 `repo.yaml`。
3. 执行 `make catalog-check`，对两个官方源验签、比较内置目录字节，并检查每个 stable 制品的可达性与大小；运行镜像目录测试，并用全新临时 `BARN_HOME` 执行 `barn update`。需要流式读取所有 stable 制品并复算摘要时，使用 `go run ./tools/catalogcheck -verify-bytes`。
4. 目录门禁通过后再构建和发布。正式版本不能继续携带官方仓库已经下线的 artifact。
{.steps}

[目录检查器](https://github.com/pgsty/barn/tree/main/tools/catalogcheck)负责核对仓库一致性。新增或重建镜像在提升为正式制品前，还需对每个变化的架构完成启动与 SSH 验收，详见[镜像流水线](/zh/docs/reference/image-pipeline/)。已发布的目录 revision 不得复用于不同字节。

## 让决策和证据放在一起 {#decision-record}

源码仓库负责签名目录、配方、代码、测试和带日期的发布证据；伴生站点负责说明这些字段和门禁为什么存在。镜像决策发生变化时，同时更新设计文章以及相关参考或发布记录；原始目录抓取结果和被舍弃的候选不要重新放回公共源码树。

接下来阅读：[镜像仓库契约](/zh/blog/design/repo-yaml-catalog-json/)与[超越 amd64 与 arm64](/zh/blog/design/multi-architecture-boundary/)。
