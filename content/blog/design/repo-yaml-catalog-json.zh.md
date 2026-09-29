---
title: "repo.yaml 是意图，catalog.json 是证据"
linkTitle: "镜像仓库契约"
description: "为什么 Barn 把人工维护的镜像策略与必须匹配实际 qcow2 工件的生成元数据分离。"
date: 2026-08-29T19:00:00+08:00
weight: 50
categories: [设计]
tags: [镜像, 供应链, Catalog]
icon: fa-solid fa-box-archive
lastmod: 2026-09-29
---

> [!NOTE]
> 本文描述尚未发布的 **Barn 0.9.0 候选版本**。当前验证结果与发行前检查见
> [当前状态](/zh/docs/about/status/)。

静态镜像仓库看起来只是一些 qcow2 文件加一个 JSON 索引。真正困难的问题是：哪些事实允许
维护者手写，哪些事实必须从即将发布的字节中推导。

如果 Checksum 与 Size 放在手写源文件里，它们很容易被错误复制；如果策略只存在于生成 JSON
中，审查 Channel 变化或弃用决定就要阅读机器输出。Barn 把这两项工作明确分开。

## `repo.yaml`：维护者表达什么意图

源码控制的 `repo.yaml` 记录作者意图：

- 仓库 Revision 与默认选择；
- Image Family 与 Alias；
- `stable` 等可移动 Channel；
- Exact Version 与 Architecture；
- Boot Mode 与支持状态；
- Immutable Upstream 与 Provenance 说明。

它刻意不包含生成的 Artifact Size、SHA-256 或 Virtual Size。一条简洁配置可以表达
`d13:stable` 指向某个准确版本，并提供 amd64/arm64 Variant，而不假装知道只属于文件本身的事实。
下面的策略片段演示格式；完整可用示例见[镜像仓库](/zh/docs/start/images/)，
当前版本以镜像参考为准：

```yaml
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

这是适合 Review 的层：Pull Request 可以清楚展示 Channel 移动、Version 弃用或 Provenance
描述变化。

> [!NOTE]
> **决策状态：当前有效。** 仓库语法与客户端行为见[镜像参考](/zh/docs/reference/images/)，
> Candidate 准备属于独立的[镜像流水线契约](/zh/docs/reference/image-pipeline/)。

## `catalog.json`：仓库能够证明什么

`catalog.json` 把策略落实到本地仓库。每个 Variant 都包含准确文件名、字节数、SHA-256、
qcow2 Virtual Size、Boot Contract、Source User 与 Immutable Upstream Provenance。

文件名、字节数、摘要与虚拟大小由工具物化并对照工件检查；启动模式、源用户、状态与溯源
则来自 `repo.yaml` 中经过校验的策略，文件检查本身不能独立证明这些声明。
Build 会强制解析 qcow2，拒绝 Backing File、
External Data、Encryption 与未知 Incompatible Feature，执行结构检查后才原子替换 Catalog。

Artifact 身份是 `(image, exact version, architecture)` 三元组，而不是选择它的 Channel。
文件保持可读、不可变的名字：

```text
images/d13-20260810.2566.0-arm64.qcow2
```

可读文件名是一项运维能力：管理员可以用普通文件系统工具检查、镜像或恢复仓库。完整性仍来自
生成元数据与验证，而不是相信名字。

## 三个操作，三种职责

仓库 CLI 把观察、生成与证明分开：

| 命令 | 职责 |
| --- | --- |
| `barn repo scan` | 只读报告 Tracked、Missing、Untracked 与 Unsafe Artifact |
| `barn repo build` | 校验 Source 与 Artifact，再原子生成 Catalog |
| `barn repo verify` | 在内存中重新物化，并要求与已发布 Catalog 逐字节一致 |

`build` 永远不修改 `repo.yaml` 或 qcow2 字节。`verify` 比“每个 Checksum 都正确”更强：它还能
证明没有任何源策略或工件变化被漏出生成 Catalog。

发布遵循同一方向：先上传不可变镜像字节，最后发布 Catalog 与匹配签名，尽量一起切换
这两个文件。部分上传造成正文与签名不匹配时，客户端会拒绝；先工件后目录则避免声明
仍在传输中的镜像字节。

## Selector 可以移动，Artifact 不能

人工配置需要方便的 Selector。随着仓库演进，`d13:stable`、`el9@9` 与 `el9@9.7` 可以解析到
更新的准确版本。数字前缀按点分组件的整数比较，因此 9.10 排在 9.9 之后。

解析完成后，客户端保存准确 Version、Architecture、Size 与 Digest。一个已经解析的节点不会
因为 Channel 移动就变成另一台机器。便利只存在于选择阶段，不可变身份存在于执行阶段。

## 传输与信任是两个问题

官方 Catalog 与普通 HTTP Catalog 必须具有受信 Detached Signature。操作者显式选择本地目录
或 HTTPS Repository 时，可以使用 Unsigned Catalog，因为本地属主或认证传输本身就是显式
信任决策。即使 URL 是 HTTPS，隐式 Compiled Default 仍属于签名信任域。

Accepted Catalog State 按 Repository 独立记录。Barn 会拒绝未知 Key、低于该仓库 High-water
Mark 的 Revision，以及同 Revision 不同字节。显式 Downgrade 可见且只影响选定 Repository；
重置到 Embedded Catalog 也不会擦掉防回滚记录。

接受 Catalog 只是前半程。每次 Pull 仍会检查 Byte Count、SHA-256 与 qcow2 结构。通过验证的
Base Image 变为只读，Node Root Disk 使用 Overlay，因此普通 VM 写入永远不会修改受信 Base。

## 不同信任域保持分离

Image Catalog Key 授权镜像策略；Release Signing 证明 Barn 应用工件与 Checksum Manifest。
两组 Key 刻意独立：有权发布 VM Image 不应自动获得发布 Barn Binary 的权限，反之亦然。

普通 Public Build 默认使用 `https://repo.pigsty.io/barn`，并通过 `--mirror` 显式选择
`https://repo.pigsty.cc/barn`；`--repo` 仍是自定义覆盖。两个
官方仓库在下载镜像时可以互相回退，始终校验同一 Catalog 的尺寸与 SHA-256。自定义仓库
仍是唯一工件源，Catalog 更新仍使用选定来源；Embedded Catalog 的 Upstream URL
只提供溯源，绝不会变成工件回退。源码配置、生成
Catalog、上传 Artifact、签名与公开可用性仍是彼此独立的发布门禁。

更大的设计原则是：策略应当便于人类审查，而关于已发布字节的事实必须可生成、可复现，并能
被独立验证。
