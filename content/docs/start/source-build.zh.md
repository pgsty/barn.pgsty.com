---
title: 从源码构建
description: 构建 Barn 0.9.1 或开发分支，准备 Mac 原生组件，并运行贡献者检查。
weight: 80
icon: fa-solid fa-code-branch
---

开发 Barn、检查代码变更或构建 Mac 原生组件时，可以使用源码构建。
安装打包好的 CLI 请看[安装指南](../installation/)。

## 选择版本

使用 **v0.9.1** 标签复现本文档对应的发行版本。记录 `git log -1 --oneline`
与 `git status --short`；仅填写版本号不能确定二进制的源码输入。

克隆本文档对应的版本：

```bash
git clone --branch v0.9.1 https://github.com/pgsty/barn.git
cd barn
```

开发主分支时省略 `--branch v0.9.1`。已发布的 0.9.0 不包含 Go 1.27.3 升级和
`Barn.app` 改名。

## 构建 CLI

Barn 0.9.1 的 `go.mod` 与 `packaging/toolchain.env` 固定使用 **Go 1.27.3**。
此外需要 Git、Make、Bash 和标准构建工具。编译 CLI 本身不需要 QEMU 或宿主网络。

2026-10-22 的本地 `make check` 已在升级后的模块与工具链上通过。
`govulncheck` 未发现受影响的已导入包或可达函数，仍报告模块层面的
[GO-2026-5932](https://pkg.go.dev/vuln/GO-2026-5932)：它涉及 `x/crypto/openpgp`，
Barn 在四个支持平台均未导入该包。依赖或漏洞数据库变化后，应重新检查。

这一结果取代了 2026-10-13 对 0.9.0 的检查结论：当时 Go 1.27.1 的八项可达漏洞
导致检查停止。当前 Go 与 `x/net` 已包含当时所需的修复。本地检查不代表托管 CI
或真实虚拟机验收。

```bash
BARN_VERSION=0.9.1 make build
export PATH="$PWD/bin:$PATH"
barn version
```

`bin/` 的入口链接指向 `bin/.barn-releases/` 中校验过的 CLI/helper 组合。移动开发构建时，同时保留该目录与两个链接。CLI 内嵌 helper 的摘要，
直接执行 `go build ./cmd/barn` 不能替代这一配套构建流程。
开发构建默认显示 `dev`，从发行标签构建也是如此。本地候选使用 `0.9.1-dev.1`；复现已发布标签时可使用 `BARN_VERSION=0.9.1 make build`。提交字段标明源码版本，工作区有变更时显示 `uncommitted`。

`make cross` 会在 `bin/darwin_amd64`、`bin/darwin_arm64`、`bin/linux_amd64`、
`bin/linux_arm64` 下生成四种平台的 Go CLI/helper，不会交叉编译 Swift Mac App。
不要将构建产物加入 Git。仓库已忽略 `bin/`、`dist/` 与 `.goreleaser-*/`。

运行 macOS 客机所需的原生组件请按下方步骤构建。
建议将实验清单保存在源码树之外。所有工作目录仍使用同一个 `BARN_HOME`。

## 构建 Mac 原生组件 {#mac-component}

重新构建已有本地组件时，先停止使用该组件的虚拟机。

在运行 macOS 27+ 的 Apple Silicon 上，确保 `xcrun` 使用 **Xcode 27+**，
包含 macOS 27 SDK 与 Swift 编译器：

```bash
BARN_VERSION=0.9.1 make mac-build
export PATH="$PWD/bin/mac:$PATH"
barn mac doctor
```

构建在 `bin/mac` 中生成 CLI、配套 hosts helper、独立的 `barn-mac-runner` 和原生 App，
还会输出校验过的本地归档 `bin/barn-mac-darwin-arm64.tar.gz`。
请保留完整 `bin/mac` 目录，并使用其中的 `barn`。
构建不会创建虚拟机；后续步骤见 [Mac 教程](../macos/)。
`make mac-native-test` 运行原生组件测试。

| 源码 | 原生 App | 应用标识 |
|---|---|---|
| `v0.9.0` 标签 | `Barn Mac.app` | `io.pgsty.barn.mac-runner` |
| `v0.9.1` 标签 | `Barn.app` | `com.pgsty.barn` |

0.9.1 CLI 兼容旧 App 名称。0.9.0 CLI 本身不会按新名称发现 `Barn.app`。请使用一起构建的 CLI 与 App。
App 包含原生 runner，不包含 Go CLI、hosts helper 或 QEMU。

### 签名与分发

未配置签名变量时，原生构建默认使用供本地开发的 **ad-hoc 签名**。
`BARN_CODESIGN_IDENTITY` 用于选择证书。仅有 Developer ID 签名不代表已完成公证，也不代表版本已公开发布。配置公证流程时使用 `BARN_NOTARY_PROFILE` 与
`BARN_MAC_REQUIRE_NOTARIZATION=1`。

请求公证后，App 构建流程会验证签名、等待 Apple 接受、装订票据并检查 Gatekeeper。
这些检查覆盖原生 App。Go CLI 与 hosts helper 使用独立的构建和分发流程。设置 `BARN_CODESIGN_IDENTITY` 不会为它们签名。为直接分发的 CLI/helper 签名时，先签 helper，将其最终 SHA-256 嵌入 CLI，再签 CLI。遵循
[Apple 公证要求](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution)
与[发布流程](../../about/engineering/)。

## 检查变更

完整检查还需要 Python 3、jq、供竞态测试使用的 C 工具链，以及
`packaging/toolchain.env` 固定版本的工具：

```bash
go install honnef.co/go/tools/cmd/staticcheck@v0.8.2
go install golang.org/x/tools/cmd/deadcode@v0.52.0
go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.15.0
go install golang.org/x/vuln/cmd/govulncheck@v1.9.0
```

将 Go 工具目录加入 PATH：优先使用 `GOBIN`，未设置时为 `$(go env GOPATH)/bin`。

```bash
make test
make check
```

`make check` 验证模块与 Shell 语法。它运行维护脚本检查、单元与竞态测试、Vet、Staticcheck、死代码与 errcheck 检查，以及漏洞检查。它还执行四目标构建、镜像流水线与安装器测试，以及依赖许可证检查。打包变更还需要验证快照制品，具体流程见[参与贡献](../../about/engineering/)。
