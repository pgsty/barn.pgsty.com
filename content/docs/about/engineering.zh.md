---
title: 参与贡献
description: 参与 Barn 源码、文档、软件包与镜像目录的维护。
weight: 30
icon: fa-solid fa-screwdriver-wrench
---

Barn 采用 Apache-2.0 开源许可证，欢迎参与命令行工具、macOS 原生组件、文档站点与镜像构建流水线的改进。

## 选择仓库

| 修改内容 | 所在仓库 |
|---|---|
| 命令行行为、虚拟机生命周期、macOS 原生组件（`Barn.app`）、安装脚本与软件包 | [`pgsty/barn`](https://github.com/pgsty/barn) |
| 文档网站、上手指南、命令参考手册与双语内容 | [`pgsty/barn.pgsty.com`](https://github.com/pgsty/barn.pgsty.com) |
| 官方 Linux 镜像定义与离线归一化规则 | [`pgsty/barn`](https://github.com/pgsty/barn) 中的 `packaging/image-repository/` 与 `packaging/image-pipeline/` |
{.wide}

提交问题报告时，请附上 `barn version` 输出、宿主操作系统与架构、执行的完整命令以及脱敏后的报错信息（移除私钥与密码）。安全漏洞请按[安全政策](https://github.com/pgsty/barn/blob/main/SECURITY.md)私下报告。准备进行较大规模的实现调整前，建议先提交 Issue 对齐方案；代码规范与 PR 要求详见 [`CONTRIBUTING.md`](https://github.com/pgsty/barn/blob/main/CONTRIBUTING.md)。

## 定位源码实现

已发布基线对应 **`v0.9.2`** 标签；提交 `27f17bb` 的后续行为见[未发布变更](../unreleased/)。各子系统的实现位置如下：

| 子系统 | 源码路径 |
|---|---|
| 命令定义、参数解析、JSON/YAML 输出与错误渲染 | `cmd/barn/`、`internal/failure/` |
| 主机清单解析、默认值填充与节点规格哈希计算 | `internal/config/`, `internal/spec/` |
| Linux 节点收敛、事务日志、磁盘管理与 SSH 就绪检查 | `internal/private/`、`internal/vm/`、`internal/cloudinit/`、`internal/state/` |
| 宿主网络、进程身份核验与特权 `/etc/hosts` 更新 | `internal/network/`、`internal/process/`、`internal/hostconfig/`、`cmd/barn-hosts-helper/` |
| 镜像目录验签、`qcow2` 结构检查与静态仓库构建工具 | `internal/image/`、`tools/catalogexport/`、`tools/catalogsign/` |
| 原生 macOS 虚拟机生命周期与桌面应用 | `internal/macvm/`、`native/mac-runner/` |
| 打包配置、CI 工作流与集成测试套件 | `packaging/`、`.github/workflows/`、`tests/` |
{.wide}

阅读实现代码时请同步查看同目录下的单元测试——测试完整界定了哪些故障支持自动恢复、哪些歧义状态必须安全中止。

## 构建与测试

按[从源码构建](../../start/source-build/)安装锁定版本的工具链后，运行完整本地门禁：

```bash
make check
```

`make check` 会依次执行 Go 模块与 Shell 脚本检查、单元测试与竞态检测、`go vet`、`staticcheck`、`govulncheck`、四平台交叉编译（`darwin/arm64`、`darwin/amd64`、`linux/amd64`、`linux/arm64`）、安装器与镜像流水线测试以及许可证检查。如果改动涉及虚拟化加速、宿主网络或 `Barn.app` 行为，请在对应宿主平台（macOS HVF / Virtualization.framework 或 Linux KVM）上执行真机虚拟机生命周期测试，并在 PR 中注明实测环境。

修改打包逻辑时，安装 `packaging/toolchain.env` 中声明的工具版本并运行本地快照检查：

```bash
make release-check
make release-snapshot SNAPSHOT_DIST=.goreleaser-review
```

`SNAPSHOT_DIST` 需指定工作树根目录下尚不存在的新目录；`release-snapshot` 会在本地生成并校验归档包、`.deb`/`.rpm` 软件包、SBOM 与校验和，不会上传任何产物。

## 编写与校验文档

文档站点的每篇文档均由英文 `page.md` 与中文 `page.zh.md` 成对组成。修改时请保持中英文的命令、默认值、标题锚点、表格与注意事项严格对齐，先说明用户要完成的任务，再展开实现细节，并将 Linux 实验环境与 `barn mac` 工作流区分清楚。

在网站仓库根目录运行：

```bash
make check
```

`make check` 会校验 Go 模块、在清除本地主题替换并关闭 Go workspace 的纯净环境下使用 Hugo Extended 与锁定的 OINK `v1.4.0` 构建全站，随后调用 `bin/check_internal_links.py public` 检查全部内部链接、标题锚点与静态资源。需要联调本地相邻的 OINK 主题工作区时，请使用 `make check-local` 或 `make build-local`。文中的命令行示例请对照 `barn <command> --help` 核验，YAML 清单示例请使用临时 `BARN_HOME` 跑通 `barn validate` 与 `barn plan`。

## 发布产物与门禁

`1.0.0` 之前的版本在 GitHub 上均标记为 pre-release（预发布版）。每次发布包含 `darwin`/`linux` `.tar.gz` 归档（含 `bin/barn`、`bin/barn-hosts-helper` 与 `licenses/`）、Linux `.deb` 与 `.rpm` 软件包（安装至 `/usr/bin/barn` 与 `/opt/barn/libexec/barn-hosts-helper`）、`checksums.txt`、`release.json` 及 SPDX 物料清单。

从 **0.9.2** 开始，Darwin arm64 归档还包含 `bin/Barn.app`，CLI、helper 与 App 均经过 Developer ID 签名与 Apple 公证。Homebrew 将 App 安装在 `libexec` 下，普通安装无需 Go 或 Xcode。

自动发布工作流要求配齐全部 6 项 Apple 签名/公证密钥，并成功构建原生组件。6 项均未配置时跳过自动创建发布，可改用文档中的本地签名发布流程；仅配置部分时直接报错。详见 [`docs/mac-release.md`](https://github.com/pgsty/barn/blob/v0.9.2/docs/mac-release.md)。

正式发布版本的验收步骤：

1. 获取并验证官方最新签名镜像目录，同步内置快照与修订号，逐项比对 stable 产物路径、架构、摘要与大小；运行镜像目录测试，并用全新临时 `BARN_HOME` 执行一次 `barn update`。
2. 在目标提交上跑通源码 CI 与打包工作流，核对版本号、配对的 `barn-hosts-helper` 摘要、许可证、SBOM 与 `checksums.txt`。
3. 完成 Linux 真机虚拟机验收测试（分发 `Barn.app` 时同步完成 Mac 真机虚拟机验收）。
4. 公开 GitHub Release 并更新 Homebrew Formula（`pgsty/infra/barn`），最后发布文档站并验证公网安装脚本与包管理安装链路。
{.steps}

## 维护镜像目录

使用[镜像流水线](../../reference/image-pipeline/)工具（`packaging/image-pipeline/build.sh` 与 `build-official.py`）校验并离线归一化候选 `qcow2` 镜像，完成真机启动测试后更新 `repo.yaml` 并签发 `catalog.json`。

将二进制内置的 Schema-3 镜像目录逐字节导出到新路径：

```bash
go run ./tools/catalogexport /absolute/new/catalog.json
```

`catalogexport` 采用原子写入并要求目标路径尚不存在。**Unreleased**：还支持相对路径、`~/` 与目录符号链接，并自动创建缺失父目录。使用 `make catalog-sign` 与 `make catalog-verify` 配合离线保存的 Minisign 密钥完成签名与验签（生产环境私钥严禁进入源码仓库或 CI）。客户端侧的验签与缓存策略见[镜像参考](../../reference/images/)。
