---
title: 从源码构建
description: 为开发与审查构建 Barn，并运行完整源码检查。
weight: 50
icon: fa-solid fa-code-branch
---

Barn 0.9.0 目前是**尚未发布的候选版本**。本页用于从源码构建与检查；
正式发布后的安装方式见[快速上手](../tutorial/)。

## 选择源码

克隆 Barn 源码仓库：

```bash
git clone https://github.com/pgsty/barn.git
cd barn
```

尚未发布时不要假定 `v0.9.0` Tag 已存在。构建前核对源码身份与工作区变更，
确认 `go.mod` 的模块为 `github.com/pgsty/barn`，命令目录为 `cmd/barn`：

```bash
git log -1 --oneline
git status --short
```

## 构建

已审核候选源码的 `go.mod` 与 `packaging/toolchain.env` 固定 Go 1.27.1；此外需要
Git、Make、Bash 与标准构建工具。运行 VM 才需要 QEMU 与特权网络准备，编译 CLI
本身不需要。进入选定源码工作区执行：

```bash
make build
export PATH="$PWD/bin:$PATH"
barn version
```

`make build` 在被 Git 忽略的 `bin/` 下生成同一次构建配套的 `barn` 与
`barn-hosts-helper`。不要混用来自不同 Commit 或不同 Release 的两个二进制。开发
构建默认显示 `dev`；Commit 字段显示干净源码的提交，工作区有变更时显示 `uncommitted`。
不能只凭版本字符串判断是否包含候选功能。

将 Inventory 保存在单独的实验目录。这不会隔离 Barn 状态；已有 deployment 时，
应先检查该部署，再运行 `up`：

```bash
mkdir -p ~/barn-lab && cd ~/barn-lab
barn setup
barn up
```

## 完整检查

完整检查还需要 Python 3、jq、供 Race 测试使用的 C 工具链，以及固定版本的质量工具。
安装已审核候选版 CI 所用版本；换用其他源码版本时，重新核对其 `CONTRIBUTING.md`
与 `packaging/toolchain.env`：

```bash
go install honnef.co/go/tools/cmd/staticcheck@v0.8.1
go install golang.org/x/tools/cmd/deadcode@v0.49.0
go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@v2.13.2
go install golang.org/x/vuln/cmd/govulncheck@v1.7.0
```

确保 Go 工具安装目录（`GOBIN`，未设置时为 `$(go env GOPATH)/bin`）位于 `PATH`。
提交源码改动前运行：

```bash
make check
```

该门禁包含模块验证、Shell 语法、维护脚本归属、单元与 Race 测试、Vet、Staticcheck、
四目标死代码交集、errcheck、漏洞检查、跨平台构建、镜像流水线和安装器测试、依赖许可证
验证。CI 还单独检查格式、空白、工具准确版本与 GoReleaser 配置；修改打包逻辑还需通过
完整的打包 Snapshot 验证。

通过源码检查不等于已经发布软件包，也不等于完成真机生命周期验证；
`make image-pipeline-native-test` 是独立的真机镜像门禁，需要显式提供
`tests/image-pipeline-native-test.sh` 开头说明的镜像输入，不会下载测试镜像。

发布工程、依赖许可证与边界说明见[工程说明](../../about/engineering/)。
