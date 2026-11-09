---
title: 发布 Mac 原生组件
linkTitle: Mac 发布
description: 构建、签名、公证并验证 Barn 的原生 macOS 发布载荷。
weight: 35
icon: fa-brands fa-apple
---

维护者通过常规的 `barn_VERSION_darwin_arm64.tar.gz` 归档交付 Mac 原生组件。从 `0.9.2` 起，标准安装脚本与 `pgsty/infra/barn` Homebrew Formula 会一并安装 CLI、配套的 hosts helper 与 macOS 宿主上的原生应用包 `Barn.app`。本文是维护中的发布手册，于 2026-11-08 对照发布脚本核验；开发构建请参阅[从源码构建](../../start/source-build/#mac-component)。

## 统一发布身份 {#release-identity}

原生载荷与 GoReleaser 归档必须使用同一个版本号和源码提交。`packaging/mac-release.py` 导出 `MACOS.md`、`MACOS.json`、`bin/barn`、`bin/barn-hosts-helper` 与 `Barn.app`，清单记录文件权限、摘要和签名状态。VM 磁盘、凭据、恢复镜像与已安装服务不属于发布载荷。

App 的 Bundle ID 为 `com.pgsty.barn`，内部可执行文件为 `barn-mac-runner`。CLI 会检查带版本号的 runner 协议，也识别早期的 `Barn Mac.app` 包名。替换 App 时，`$BARN_HOME/mac` 下的 VM 状态保持不变。

CLI 内嵌了 helper 的摘要，因此必须按以下顺序签名：

1. 构建并签名 `barn-hosts-helper`。
2. 构建 `barn` 时嵌入已签名 helper 的 SHA-256，再签名 CLI。
3. 为 `Barn.app` 签名，启用 hardened runtime 与安全时间戳。
4. 将 CLI、helper 与 App 一同提交 Apple 公证；获准后为 App 装订票据（staple），验证票据并检查 Gatekeeper。
5. 导出并重新解包载荷，再次核验签名与票据。组装发行包时，将 Darwin arm64 归档中的 CLI/helper 替换为这批已签名的字节，重新生成 SPDX 文档与校验和。
{.steps}

载荷构建器与归档检查器会强制核对配套关系。构建 CLI 后再次签名 helper 会改变摘要，导致配对失败。

## 在本地构建正式版本 {#local-release}

准备运行 macOS 27+ 的 Apple Silicon Mac、Xcode 27+、[锁定的工具链](../../start/source-build/)、Developer ID Application 身份及已保存的 `notarytool` 配置。用 `security find-identity -v -p codesigning` 选择签名身份，用 `xcrun notarytool store-credentials` 创建公证配置；证书私钥和密码保存在仓库外。

检出带有 `v$RELEASE_VERSION` 标签的干净源码，将 `RELEASE_VERSION` 设为目标发布版本，并在源码仓库外选择新的制品目录：

```bash
export BARN_CODESIGN_IDENTITY='Developer ID Application: your organization (TEAMID)'
export BARN_NOTARY_PROFILE=barn-release
export BARN_MAC_REQUIRE_NOTARIZATION=1
VERSION="${RELEASE_VERSION:?Set RELEASE_VERSION to the checked-out release tag version}"
COMMIT="$(git rev-parse HEAD)"
export SOURCE_DATE_EPOCH="$(git show -s --format=%ct HEAD)"
export BARN_BUILD_DATE="$(date -u -r "$SOURCE_DATE_EPOCH" +%Y-%m-%dT%H:%M:%SZ)"
RELEASE_DIR="$(mktemp -d "${TMPDIR:-/tmp}/barn-release.XXXXXX")"

python3 packaging/mac-release.py build \
  "$VERSION" "$COMMIT" "$SOURCE_DATE_EPOCH" "$RELEASE_DIR/native.tar.gz"
BARN_MAC_PAYLOAD="$RELEASE_DIR/native.tar.gz" \
  make release-local VERSION="$VERSION" OUTPUT="$RELEASE_DIR/assets"
```

正式原生构建与 `release-local` 都会在构建前执行 `make catalog-check` 对应的门禁。官方镜像目录发生变化时，先按[发布门禁](../engineering/#release-outputs-and-gates)同步并测试。快照或 `uncommitted` 载荷不能用于正式本地发布。`release-local` 核验归档、软件包、SBOM、校验和与 CLI/helper 配对，将完整制品写入指定目录。

开发打包逻辑时，可用 `BARN_MAC_PAYLOAD=/absolute/native.tar.gz make release-snapshot` 验证原生载荷合并。载荷版本必须匹配 `.goreleaser.yaml` 选择的快照版本，例如 `v1.1.0` 之后为 `1.1.1-next`；脏工作树使用 `uncommitted`，干净源码使用完整提交号。快照接受 ad-hoc 签名，正式发行检查要求载荷已经过 Developer ID 签名与公证。

## 配置自动签名 {#ci-signing}

标签工作流使用以下 6 项仓库密钥。全部未配置时跳过自动创建发布，维护者可使用本地流程；只配置部分时立即失败；全部配置后，原生构建、签名或公证任一失败都会阻止组装发行包。

| 密钥 | 内容 |
|---|---|
| `MAC_CERTIFICATE_BASE64` | 包含私钥的 Developer ID Application `.p12` 文件，经 Base64 编码 |
| `MAC_CERTIFICATE_PASSWORD` | `.p12` 的保护密码 |
| `MAC_CODESIGN_IDENTITY` | 导入后的身份名称或证书指纹 |
| `MAC_NOTARY_KEY_BASE64` | App Store Connect API `.p8` 密钥，经 Base64 编码 |
| `MAC_NOTARY_KEY_ID` | API 密钥标识符 |
| `MAC_NOTARY_ISSUER` | API 签发者标识符 |
{.wide .expand}

[Mac 工作流](https://github.com/pgsty/barn/blob/main/.github/workflows/mac.yml)将签名材料导入临时 runner 钥匙串，并在任务结束时删除。PR 与快照使用 ad-hoc 构建。[发布工作流](https://github.com/pgsty/barn/blob/main/.github/workflows/release.yml)验证完整载荷后创建发布草稿。

## 验证安装并发布 {#acceptance}

运行 `make check`、`make mac-native-test` 以及包含原生载荷的完整快照。在隔离目录中验证首次安装、重复安装与升级，并在受支持的物理 Mac 上使用打包后的 App 验证启动、SSH、桌面窗口与正常关机。替换 App 必须保留实例 ID、机器 ID、SSH 密钥和已固定的主机密钥。

已有的 [`tests/mac-live-acceptance.py`](https://github.com/pgsty/barn/blob/main/tests/mac-live-acceptance.py) 要求绝对 `--barn` 路径、专用可丢弃的 `--home`、与其分离的新建或空 `--output` 证据目录，并用 `--allow-test-root` 显式授权该测试目录。先用 `--plan` 查看流程；`--gui` 增加桌面/剪贴板检查，`--allow-download` 允许在未准备基底时从 Apple 下载。脚本保留失败现场与证据。测试 SSH 集成时，除了 `BARN_HOME` 还应隔离进程的用户主目录，因为受管的 `~/.ssh/config` 条目位于 VM 状态目录之外。

发布组装从 `packaging/homebrew/barn.rb.tmpl` 生成 `barn.rb`。Formula 将 `barn` 安装到 `bin`，将 helper 与 App 安装到 `libexec`；安装与测试逻辑应与 Tap 保持一致。带后缀的版本需要显式 `version` 行，避免 Homebrew 从架构后缀误推导出 `64`；普通版本省略该行。`0.9.1` 的公开归档早于 App 随包交付，仅支持 Linux 客机。

核对本地制品后，推送源码与标签，上传到 GitHub Release 草稿并核验上传字节，再公开发布。低于 `1.0.0` 或带预发布后缀的版本标记为 pre-release，稳定版设为 latest。公开制品可用后更新 Homebrew 四个平台的 URL 与摘要，随后用已发布的字节验证公开归档、安装脚本与 Homebrew 升级。签名、公证、VM 验收与公开安装的结果分别记入[验证历史](../history/)。
