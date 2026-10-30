---
title: "repo.yaml 是意图，catalog.json 是证据"
linkTitle: "镜像仓库契约"
description: "为什么 Barn 把人工维护的镜像策略与必须匹配实际 qcow2 工件的生成元数据分离。"
date: 2026-08-29T19:00:00+08:00
weight: 50
categories: [设计]
tags: [镜像, 供应链, 镜像目录]
icon: fa-solid fa-box-archive
lastmod: 2026-10-26
---

本文阐述 Barn `0.9.2` 的 Linux 静态镜像仓库契约（[Mac 虚拟机](/zh/docs/start/macos/)的 `.ipsw` 恢复镜像与 APFS 基础镜像由 `barn mac` 独立管理）。

一个静态虚拟机镜像仓库包含两类截然不同的元数据：一类是维护者的**策略意图**（哪个版本对应 `:stable`、哪些旧版本标为 `deprecated`、每个发行版系列支持哪些短别名），另一类是镜像文件的**物理事实**（精确字节数、SHA-256 摘要、`qcow2` 虚拟容量）。如果把这两类信息混在同一份手写 JSON 文件里，不仅手动复制哈希和字节数极易出错，审查 PR 时还会让关键的通道变更淹没在大段哈希差异之中。

因此，Barn 将维护者编写的策略与工具从真实镜像提取的证据拆分为两个文件：`repo.yaml` 表达意图，`catalog.json` 记录证据。

## `repo.yaml`：由维护者编写的策略意图

纳入版本控制的 `repo.yaml`（`schema: 1`）由维护者直接编辑，仅声明策略信息：

- 仓库修订号（`revision`）与全局默认值（`image`、`channel`、`arch`、`boot`）
- 镜像系列名称与可用别名
- `stable` 等可移动通道指向的目标版本
- 精确版本号与支持的架构（`amd64`、`arm64`）
- 引导方式（`uefi` 或 `bios`）、支持状态（`status`）、源镜像默认账号（`source_user`）及上游溯源 URL

`repo.yaml` 中**不包含**任何手写的镜像文件大小、SHA-256 或虚拟磁盘容量：

```yaml {title="repo.yaml"}
defaults: { image: d13, channel: stable, arch: native, boot: uefi }
images:
  d13:
    aliases: [debian13, debian, trixie]
    channels: { stable: "20260810.2566.0" }
    versions:
      "20260810.2566.0":
        status: supported
        variants:
          amd64: {}
          arm64: {}
```

得益于这种精简结构，每次提交 PR 时都可以一目了然地审查通道切换、版本弃用与上游来源变更（完整搭建流程见[镜像仓库指南](/zh/docs/start/images/)，内置目录 `2026093001` 的完整列表见[镜像参考](/zh/docs/reference/images/)）。

> [!NOTE]
> 仓库格式与客户端验签规则详见[镜像参考](/zh/docs/reference/images/)；候选镜像的离线定制流程详见[镜像流水线](/zh/docs/reference/image-pipeline/)。

## `catalog.json`：由工具生成的物理证据

`catalog.json`（`schema: 3`）由 `barn repo build` 根据 `repo.yaml` 和磁盘上的真实 `.qcow2` 文件自动生成。针对每个 `(image, version, arch)` 变体，`barn repo build` 会依次执行三步：

1. 校验 `repo.yaml` 中的策略声明（引导方式、`source_user`、支持状态与上游溯源信息）。
2. 调用 `qemu-img` 检查对应的 `images/<image>-<version>-<arch>.qcow2` 文件，拒绝包含后端依赖链（backing file）、外部数据文件、加密或未知不兼容特性的镜像。
3. 计算精确的文件字节数、SHA-256 摘要与 `qcow2` 虚拟容量，校验通过后原子写入 `catalog.json`。
{.steps}

每个镜像产物的不可变身份由三元组 `(image, exact version, architecture)` 唯一确定，并使用直观可读的文件名存放：

```text
images/d13-20260810.2566.0-arm64.qcow2
```

规范可读的文件名方便管理员使用标准文件系统工具或 `rsync` 检查、镜像与恢复仓库，而文件的完整性则由 `catalog.json` 及其 minisign 签名严格保障。

## 三条仓库命令，三项独立职责

| 命令 | 职责 |
|---|---|
| `barn repo scan /srv/barn` | 只读巡检：报告已跟踪、`missing`（缺失）、`untracked`（未声明）与 `unsafe`（不安全）的文件，不修改任何内容 |
| `barn repo build /srv/barn` | 严格校验 `repo.yaml` 与全部声明的 `.qcow2` 文件，通过后原子生成 `catalog.json` |
| `barn repo verify /srv/barn` | 在内存中重新构建目录，并要求与磁盘上已发布的 `catalog.json` 逐字节完全一致 |
{.wide}

`barn repo build` 绝不修改 `repo.yaml` 或 `.qcow2` 文件本身；而 `barn repo verify` 则能捕捉到策略文件、镜像文件与 `catalog.json` 之间的任何不一致。发布仓库更新时，请务必先上传不可变的 `.qcow2` 镜像文件，最后同步更新 `catalog.json` 与 `catalog.json.minisig`，避免客户端读到新目录时镜像文件尚未上传完毕。

## 选择器可以演进，已解析身份不可变

在编写 `barn.yml` 或执行命令行操作时，`d13:stable`、`el9@9`、`el9@9.7` 等选择器提供了便利的版本匹配（数值前缀按点号分段的整数比较，因此 `9.10` 排在 `9.9` 之后）。

一旦 `barn plan` 或 `barn up` 完成节点解析，客户端就会将精确版本号、架构、文件大小与 SHA-256 摘要固化到节点状态中。后续镜像目录中的通道指向新版本时，绝不会在后台静默替换已创建的节点。

## 传输安全与目录签名各司其职

Barn 将传输协议与目录信任分开处理：

- **官方仓库与普通 HTTP 仓库**：强制要求提供由 Barn 内置生产公钥验签的分离签名（`catalog.json.minisig`）。
- **显式指定的本地目录与 HTTPS 仓库**：通过 `--repo` 或 `BARN_REPO` 显式选中的自定义本地路径或 HTTPS 仓库允许使用未签名目录，由操作者自行把控本地目录属主或 HTTPS 端点。
- **按仓库隔离的防回滚水位线**：Barn 为每个仓库根路径独立记录历史最高已接受修订号（`revision`），自动拒绝低于该修订号的旧目录（除非在 `barn image sync` 时显式传入 `--allow-downgrade`），并拒绝同一修订号下字节不同的篡改目录。
- **拉取时的纵深校验**：即便镜像目录本身已通过验签，每次拉取或复用本地镜像时，Barn 仍会再次核对字节数、SHA-256 与 `qcow2` 结构，通过后将其设为只读（`0444`），供各节点的写时复制根盘安全挂载。

## 发行包、原生应用与镜像目录的信任域分离

Barn 的三类分发对象使用各自独立的信任机制：

1. **CLI 发行归档与 Linux 软件包**：通过 GitHub Releases 分发，提供 `checksums.txt` SHA-256 清单与 SPDX 物料清单。
2. **原生 macOS `Barn.app` 应用包**：使用 Apple Developer ID 代码签名与公证流程（本地源码构建默认使用 ad-hoc 签名）。
3. **Linux 镜像目录**：通过离线保存的 Ed25519 Minisign 密钥（`catalog.json.minisig`）进行独立认证。

在 Barn `0.9.2` 中，默认镜像源为 `https://repo.pigsty.io/barn`，`--mirror` 切换为中国官方源 `https://repo.pigsty.cc/barn`，`--repo` 则用于指定自定义仓库。两个官方镜像源在下载 `.qcow2` 文件时支持自动互备回退，并始终对照同一份目录校验文件大小与 SHA-256；而刷新镜像目录（`barn update`）以及使用自定义 `--repo` 仓库时，则严格只访问所选定的唯一来源。
