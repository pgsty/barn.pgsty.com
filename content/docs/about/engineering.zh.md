---
title: 工程与发布
description: 源码边界、构建测试门禁、镜像归一化、发布输出与证据纪律。
weight: 30
icon: fa-solid fa-screwdriver-wrench
---

本页以 2026-09-26 审核的源码 `b91ec37` 为准，其中的 0.9 变更尚未发布；
公开应用版本仍为 0.8.0。构建命令使用当前工作区，必须同时记录其提交。

## 仓库边界

Farrow 源码仓库包含代码、测试、构建/打包定义、法律声明、`README.md`、`CHANGELOG.md`、
`CONTRIBUTING.md`、`SECURITY.md` 与双语应用发布说明。本网站提供用户、设计、运维
与发布文档。运行行为和命令参数需要以匹配的源码及二进制核对；未发布源码的行为不能
代表公开软件包。

Review 记录、临时 Inventory、生成二进制与 Release 输出树不是生产源码输入。

以下输出随时可重建：

- `bin/`：开发构建；
- `dist/` 与 `.goreleaser-*`：Release/Snapshot Staging；
- 根目录 `farrow`、`farrow-hosts-helper`、`catalogsign` 二进制；
- Hugo 的 `public/` 与 `resources/`。

## 构建与源码门禁

```bash
make check
```

`make check` 包含模块与 Shell 检查、维护脚本归属、单元/Race 测试、Vet、Staticcheck、
死代码与 errcheck 检查、漏洞扫描、四目标跨平台构建、安装器/镜像流水线测试及许可证
检查，准确清单以 Makefile 为准。CI 还单独检查固定工具链、Go 格式、空白与 GoReleaser
配置。质量工具安装步骤见[从源码构建](../../start/source-build/)。

打包逻辑变更还需要独立 Snapshot 门禁：

```bash
make release-check
make release-snapshot SNAPSHOT_DIST=.goreleaser-review
```

安装 `packaging/toolchain.env` 指定的 GoReleaser、nFPM、Syft 等版本；Snapshot 还需要
验证脚本使用的归档与系统软件包检查工具。输出必须是工作区根目录下尚不存在的新目录，
已有目录会被拒绝。Snapshot 仅在本地生成，不上传 Release。

源码检查不等于真机验证。macOS HVF、Linux KVM/网络、软件包消费、Release 发布与
线上网站渲染需要分别验证。`make image-pipeline-native-test` 是独立真机镜像流水线
门禁，需要 QEMU/libguestfs 与显式镜像输入。必填的
`FARROW_IMAGE_PIPELINE_NATIVE_*` 变量见 `tests/image-pipeline-native-test.sh`，
该测试不会下载镜像。

## Release 与软件包契约

`packaging/`、`.goreleaser.yaml` 与 `.github/workflows` 属于源码；它们生成的目录不是。
Archive 与 Linux Package 携带配套 CLI 和 hosts-helper 二进制、`LICENSE`、源码
README，以及根据 `go.mod` 锁定模块版本重建的准确上游许可证字节。Archive 的二进制
位于 `bin/`、许可证位于 `licenses/`；Linux Package 安装 `/usr/bin/farrow`、
`/opt/farrow/libexec/farrow-hosts-helper`，文档位于 `/usr/share/doc/farrow/`。

Linux Package 与旧开发 Archive 格式包含 `BUILD_INFO.json`。正式 GoReleaser
Archive 的构建身份在二进制中，发布元数据随资产单独提供，不能假定每种 Archive 都包含
该文件。依赖许可证在构建时生成暂存，详细用户文档保留在本网站。

应用 Release 由 GitHub Actions 构建，提供 `checksums.txt`、发布元数据与 SPDX SBOM
资产。当前工作流不生成单独的应用发布签名或 provenance/attestation 包。用于认证镜像
Catalog 的 Minisign 签名属于另一套信任机制。

Commit、Tag、归档/软件包验证、CI、草稿上传、公开发行与匿名下载验证应分别记录。
Tag 工作流创建草稿，不会直接发布。pre-1.0 版本在 GitHub 标记为预发布，安装器需要
显式指定 `FARROW_VERSION`。

`make release-local VERSION=<version>` 在本地构建并验证，不执行发布。它要求干净
工作区正好位于对应 `v<version>` Tag，配置 `origin`，使用固定工具，并且暂存/输出
目录尚不存在。未打标签的候选版应使用 Snapshot 路径审核。

## 镜像归一化

底层 `packaging/image-pipeline/build.sh` 只接受显式本地 qcow2，不下载也不上传。它复制并
哈希源文件，强制 qcow2 解析，拒绝 Backing/External/Encryption/未知 Feature，运行
`qemu-img check`，并可在显式 QEMU Sandbox 中做无网络 Offline Guest Mutation。
UID/GID 88 冲突会拒绝，不会含糊改写。

`build-official.py` 为 Debian 12/13、Rocky Linux 8/9 的 amd64/arm64 目标增加固定、
摘要锁定的 Wrapper。它只允许获取锁定的源镜像与离线软件包输入，输出未签名的 `testing`
Candidate，并可组装独立候选仓库。真机 Smoke、双构建比较、生产签名、上传与 Catalog
激活仍是后续门禁。

Catalog 逐字节导出命令：

```bash
go run ./tools/catalogexport /absolute/new/catalog.json
```

导出器原子写入，拒绝已存在的输出路径。`make catalog-sign` 与 `make catalog-verify`
使用 Catalog Minisign 密钥对，生产私钥不进入源码或 CI。应用 checksum 不能替代
Catalog 签名。

## 证据纪律

历史 M0–M4 记录在实现期有价值，但不是产品文档。可长期保留的结论已收敛到[设计](../design/)
与[当前状态](../status/)。后续源码修改不会自动继承真机证明；每条状态结论都应说明日期、宿主、
路径与剩余门禁。
