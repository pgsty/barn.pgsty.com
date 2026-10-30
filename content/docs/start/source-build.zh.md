---
title: 从源码构建
description: 构建 Barn 0.9.2 或开发分支，准备 Mac 原生组件，并运行贡献者检查。
weight: 80
icon: fa-solid fa-hammer
---

开发新功能或审阅发行版本时，可从源码构建 Barn。预编译 CLI 与 Apple Silicon 发行包内的原生应用包 `Barn.app` 均可直接安装，详见[安装指南](../installation/)。

## 检出源码

克隆 **v0.9.2** 标签以复现本文档对应的发行版（开发主分支时可省略 `--branch v0.9.2`），并在提交构建记录时附上 `git log -1 --oneline` 与 `git status --short`：

```bash
git clone --branch v0.9.2 https://github.com/pgsty/barn.git
cd barn
```

`v0.9.2` 标签用于复现已发布版本，不包含[未发布变更](../../about/unreleased/)。测试这些修复时，请使用包含 `27f17bb` 的源码；不要设置 `BARN_VERSION`，或使用开发版本号，避免将开发构建标记为正式的 `0.9.2`。

## 构建 CLI

Barn `0.9.2` 在 `go.mod` 与 `packaging/toolchain.env` 中固定使用 **Go 1.27.3**，并依赖 Git、Make、Bash 与标准编译工具（仅编译 CLI 无需安装 QEMU 或配置宿主网络）：

```bash
BARN_VERSION=0.9.2 make build
export PATH="$PWD/bin:$PATH"
barn version
```

`make build` 会在 `bin/.barn-releases/` 下编译配套的 `barn` 与 `barn-hosts-helper`，将 helper 的 SHA-256 摘要嵌入 CLI，并在 `bin/` 下创建入口符号链接。请始终使用 `make build` 而非裸跑 `go build ./cmd/barn`；移动构建产物时请一并保留 `bin/.barn-releases/` 目录与 `bin/` 下的两个链接。

未指定 `BARN_VERSION` 时，开发构建默认将版本号标记为 `dev`（本地候选构建可传入 `BARN_VERSION=0.9.2-dev.1`），工作区存在未提交改动时 commit 字段会显示为 `uncommitted`。

执行 `make cross` 可在 `bin/darwin_amd64`、`bin/darwin_arm64`、`bin/linux_amd64` 与 `bin/linux_arm64` 下交叉编译四个目标平台的 Go CLI 与 helper。构建产物（`bin/`、`dist/`、`.goreleaser-*/`）及实验环境清单不应纳入版本控制；在工作树内生成前，请确认对应路径已被忽略。

请针对准备使用的源码运行下方贡献者检查；历次带日期的验收记录见[验证历史](../../about/history/)。

## 构建 Mac 原生组件 {#mac-component}

重新编译本地 Mac 组件前，请先停止正在使用它的所有 Mac 虚拟机。

在运行 macOS 27+ 的 Apple Silicon Mac 上，确认 `xcrun` 已指向 **Xcode 27+**（提供 macOS 27 SDK 与 Swift 编译器），然后执行：

```bash
BARN_VERSION=0.9.2 make mac-build
export PATH="$PWD/bin/mac:$PATH"
barn mac doctor
```

`make mac-build` 会在 `bin/mac` 下生成配套的 `barn`、`barn-hosts-helper`、独立运行器 `barn-mac-runner` 与原生应用包 `Barn.app`，同时打包生成 `bin/barn-mac-darwin-arm64.tar.gz`。可执行 `make mac-native-test` 运行原生组件测试套件，随后按 [macOS 虚拟机教程](../macos/)创建虚拟机。

| 源码标签 | 原生应用包 | 应用标识符（Bundle ID） |
|---|---|---|
| `v0.9.0` | `Barn Mac.app` | `io.pgsty.barn.mac-runner` |
| `v0.9.1`、`v0.9.2` | `Barn.app` | `com.pgsty.barn` |

`0.9.2` CLI 同时兼容 `Barn.app` 与旧版 `Barn Mac.app`，而 `0.9.0` CLI 仅查找 `Barn Mac.app`——请始终使用 `bin/mac` 下同批构建出的 CLI 与应用包。

### 代码签名与公证

未设置签名环境变量时，`make mac-build` 默认使用供本机开发测试的 **ad-hoc 签名**。如需进行证书签名或公证分发：

- 设置 `BARN_CODESIGN_IDENTITY` 以使用 Developer ID 证书为 `Barn.app` 签名。
- 设置 `BARN_NOTARY_PROFILE` 与 `BARN_MAC_REQUIRE_NOTARIZATION=1`，使构建流水线自动校验签名、提交 Apple 公证、装订票据（staple）并验证 Gatekeeper 状态。
- `make mac-build` 为原生组件签名；Go CLI/helper 的签名与公证请使用 [`docs/mac-release.md`](https://github.com/pgsty/barn/blob/v0.9.2/docs/mac-release.md) 中的正式发布流程。该流程先签名 helper，将最终 SHA-256 嵌入 CLI，再签名 CLI 并将配套产物一起提交公证。详见[发布工程](../../about/engineering/)。

## 运行贡献者检查

执行完整的 `make check` 还需要 Python 3、`jq`、支持竞态检测（`-race`）的 C 编译器，以及 `packaging/toolchain.env` 中固定版本的静态检查工具：

```bash
go install honnef.co/go/tools/cmd/staticcheck@v0.8.2
go install golang.org/x/tools/cmd/deadcode@v0.52.0
go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.15.0
go install golang.org/x/vuln/cmd/govulncheck@v1.9.0
```

将 `GOBIN`（或 `$(go env GOPATH)/bin`）加入 `PATH` 后运行：

```bash
make test
make check
```

`make check` 会依次验证 Go 模块、Shell 脚本语法、仓库维护检查、单元与竞态测试、`go vet`、`staticcheck`、`deadcode`、`golangci-lint`、`govulncheck`、四平台交叉编译、镜像流水线与安装器测试以及依赖许可证合规性。打包快照验证流程请参阅[发布工程](../../about/engineering/)。
