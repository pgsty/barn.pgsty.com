---
title: 从源码构建
description: 为开发与审查构建 Farrow，并运行完整源码检查。
weight: 50
icon: fa-solid fa-code-branch
---

普通用户应优先使用公开 Release 的 Archive 或系统软件包。截至 2026-09-26，公开版本为
**0.8.0**；由于 Farrow 仍是 pre-1.0，它在 GitHub 上标记为预发布。本次审核的本地
`b91ec37` 是**尚未发布的 0.9 候选源码**，不能作为可安装的 0.9 Release。
详见[当前状态](../../about/status/)。

## 选择源码

在新目录重现公开发行版：

```bash
git clone --branch v0.8.0 --depth 1 https://github.com/pgsty/farrow.git farrow-0.8.0
cd farrow-0.8.0
```

要审核候选版行为，需要使用实际包含候选提交的工作区。审核当日，新克隆的公开 `main`
并不包含 `b91ec37`，也不能通过获取不存在的 0.9 Tag 得到它。构建前先核对源码身份：

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
farrow version
```

`make build` 在被 Git 忽略的 `bin/` 下生成同一次构建配套的 `farrow` 与
`farrow-hosts-helper`。不要混用来自不同 Commit 或不同 Release 的两个二进制。开发
构建默认显示 `dev`；Commit 字段显示干净源码的提交，工作区有变更时显示 `uncommitted`。
不能只凭版本字符串判断是否包含候选功能。

将 Inventory 保存在单独的实验目录。这不会隔离 Farrow 状态；已有 deployment 时，
应先检查该部署，再运行 `up`：

```bash
mkdir -p ~/farrow-lab && cd ~/farrow-lab
farrow setup
farrow up
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
