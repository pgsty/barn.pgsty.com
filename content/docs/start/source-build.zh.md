---
title: 从源码构建
description: 构建 Barn 0.9.0 或开发分支，准备 Mac 原生组件，并运行贡献者检查。
weight: 80
icon: fa-solid fa-code-branch
---

开发 Barn、检查代码变更或构建 Mac 原生组件时，可以使用源码构建。
安装打包好的 CLI 请看[安装指南](../installation/)。

## 选择版本

克隆本文档对应的发行版本：

```bash
git clone --branch v0.9.0 https://github.com/pgsty/barn.git
cd barn
```

开发主分支时省略 `--branch v0.9.0`。比较行为前，用 `git log -1 --oneline`
和 `git status --short` 确认源码版本与工作区变更。

## 构建 CLI

Barn 0.9.0 的 `go.mod` 与 `packaging/toolchain.env` 固定使用 **Go 1.27.1**。
此外需要 Git、Make、Bash 和标准构建工具。编译 CLI 本身不需要 QEMU 或宿主网络。

```bash
make build
export PATH="$PWD/bin:$PATH"
barn version
```

`bin/` 包含 CLI 与配套的 `barn-hosts-helper`，请保留两者。
开发构建默认显示 `dev`，提交字段标明源码版本，工作区有变更时显示 `uncommitted`。

运行 macOS 客机所需的原生组件请按下方步骤构建。
建议将实验配置保存在源码树之外；所有工作目录仍使用同一个 `BARN_HOME`。

## 构建 Mac 原生组件 {#mac-component}

在运行 macOS 27 的 Apple Silicon 上，使用 **Xcode 27**：

```bash
make mac-build
export PATH="$PWD/bin/mac:$PATH"
barn mac doctor
```

该命令在 `bin/mac` 中生成 CLI 与原生 `Barn Mac.app`，采用供本地使用的 ad-hoc
签名，不会创建虚拟机。之后继续 [Mac 教程](../macos/)。
`make mac-native-test` 运行原生组件测试。

## 检查变更

完整检查还需要 Python 3、jq、供竞态测试使用的 C 工具链，以及
`packaging/toolchain.env` 固定版本的工具：

```bash
go install honnef.co/go/tools/cmd/staticcheck@v0.8.1
go install golang.org/x/tools/cmd/deadcode@v0.49.0
go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.13.2
go install golang.org/x/vuln/cmd/govulncheck@v1.7.0
```

将 Go 工具目录加入 PATH：优先使用 `GOBIN`，未设置时为 `$(go env GOPATH)/bin`。

```bash
make test
make check
```

`make check` 包含模块验证、Shell 语法、维护脚本检查、单元与竞态测试、Vet、
Staticcheck、死代码与 errcheck 检查、漏洞检查、四目标构建、镜像流水线与安装器测试，
以及依赖许可证检查。打包变更还需要验证快照制品，具体流程见[参与贡献](../../about/engineering/)。
