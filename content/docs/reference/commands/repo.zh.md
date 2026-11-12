---
title: 仓库命令
description: 根据 repo.yaml 与 qcow2 制品扫描、构建和校验静态镜像仓库。
weight: 50
date: 2026-11-11
---

根据 repo.yaml 与 qcow2 制品扫描、构建和校验静态镜像仓库。

本参考对应 **Barn 1.2.0**；选项表区分 **1.1.0 已有选项** 与 **1.2.0 新增选项**，具体范围见[版本基线](/zh/docs/reference/commands/#versions)。所有命令继承[全局选项](/zh/docs/reference/commands/#global-options)。

## `barn repo scan` {#barn-repo-scan}

```text
barn repo scan <root> [flags]
```

扫描包含 `repo.yaml` 与平铺 `images/` 目录的仓库根路径，报告已跟踪、缺失、未跟踪和不安全的 qcow2 文件，不修改文件，也不需要 `qemu-img`。扫描成功即退出 `0`，即使发现问题也是如此；自动化必须检查 `missing` 和 `unsafe`，不能只看退出码。

除 `--help` 外没有局部选项，仍可使用全局输出选项。

```bash
barn repo scan /srv/barn
barn --json repo scan /srv/barn
```

## `barn repo build` {#barn-repo-build}

```text
barn repo build <root> [flags]
```

校验 `repo.yaml`，通过 `qemu-img` 检查声明的 qcow2 制品，计算最终摘要与大小，并原子生成 `catalog.json`。缺失或不安全的制品导致构建失败，未跟踪文件不会收录；`repo.yaml` 与镜像字节保持原样。

本命令不签名或发布目录。内容变化时递增 revision，保持制品文件名不可变，并在发布前使用独立的贡献者签名工具。详见[仓库格式](../../images/#static-repository-format)。

除 `--help` 外没有局部选项，仍可使用全局输出选项。

```bash
barn repo build /srv/barn
barn --json repo build /srv/barn
```

## `barn repo verify` {#barn-repo-verify}

```text
barn repo verify <root> [flags]
```

根据 `repo.yaml` 与实际镜像字节在内存中重建预期目录，要求与已有 `catalog.json` 逐字节一致，需要 `qemu-img`。本命令检查仓库内容一致性，分离签名由目录激活流程或签名工具验证。

除 `--help` 外没有局部选项，仍可使用全局输出选项。

```bash
barn repo verify /srv/barn
barn --json repo verify /srv/barn
```

## 实现依据 {#implementation}

[command_repo.go](https://github.com/pgsty/barn/blob/v1.2.0/cmd/barn/command_repo.go)

发布源码与相对 1.1.0 的变化见[版本基线](/zh/docs/reference/commands/#versions)。
