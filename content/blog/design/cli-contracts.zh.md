---
title: "保留契约，演进 CLI"
linkTitle: "CLI 契约"
description: "拆分 Barn 命令树、应用编排与输出处理时，哪些行为必须保留。"
date: 2026-11-04T10:00:00+08:00
lastmod: 2026-11-09
weight: 100
categories: [Design]
tags: [CLI, Compatibility, Architecture]
icon: fa-solid fa-terminal
---

Barn 已经使用 Cobra。2026-11-04 CLI 提案最值得保留的部分，是对命令语法、应用编排与外部行为的拆分。本文结合 2026-11-09 发布的 `v1.1.0` 源码整理这些设计；包结构拆分与较大范围的命令重组仍是提案，当前用法见 [CLI 参考](/zh/docs/reference/cli/)。

## 保留已有边界 {#existing-boundaries}

`cmd/barn/command_*.go` 定义各命令族。每次执行都会新建 Cobra 命令树，避免参数值在多次调用间泄漏。处理函数收集 `commandOutcome`，由统一出口渲染文本或结构化结果；类型化错误保留退出码、原因、恢复建议以及可用的部分结果。Linux 生命周期、镜像校验和原生 Mac 行为继续由各领域包实现。

这些边界已经承载了几项重要契约：

| 契约 | 重构必须保留的行为 |
|---|---|
| 部署选择 | `BARN_HOME` 下的一套 Linux 部署，以及 `mac/` 子目录下的具名 Mac VM |
| 配置来源 | 期望状态命令解析清单；启动、停止、状态与访问命令使用已应用状态 |
| 机器可读输出 | 既有字段和类型、JSON/YAML 一致性，以及失败时有用的部分结果 |
| 交互访问 | 真实终端文件描述符、子进程信号与远端退出码 |
| 帮助与补全 | 既有别名、局部参数、平台范围与离线补全 |
{.wide .expand}

搬迁命令不能让无效清单悄悄回退到旧状态，不能把 `init -o FILE` 改作输出格式，也不能将 `up`、`restart`、`reload`、`recreate` 合并成一个动作。这些差异决定了命令读取哪份配置、可以修改哪些资源。

## 收敛展示参数的解析 {#presentation}

当前 `prepareOutput` 在 Cobra 之前扫描展示参数，并通过 `commandFlagValues` 区分参数名和参数值。后续简化应让同一棵命令树驱动正常解析、帮助、补全与命令说明导出，同时保留一个范围受限的入口，为解析失败选择错误展示格式。

优先级应始终是 **显式 CLI 值 → 选中的环境默认值 → 内置默认值**，确定最终来源后再验证。Barn `1.0.0` 已修复无效环境默认值阻断有效 CLI 覆盖的问题。重构还要保留显式布尔 `false` 和看起来像参数的值：`-o --json` 可能是在指定文件名，而远端 `--` 分隔符之后的内容全部属于客机命令。

`--json --help` 继续输出文本帮助；裸 `barn` 在文本模式打印完整帮助，在结构化模式保留 `actions[]`。提案中的机器可读帮助 schema 应作为独立、显式的接口，从命令树生成。

## 区分结果与数据流 {#output}

单次结果的 JSON/YAML 命令在 stdout 输出一个结果文档，进度、警告和诊断走 stderr。保留 `.nodes`、`.results` 等命令特有的结果结构；统一套上新的 `data` 对象会破坏已有自动化。

SSH 与持续跟随的日志需要流式路径，保留空参数、引用边界、第二个 `--`、取消与客机非零退出码。结构化模式的交互 SSH 将会话输出送到 stderr，最终报告送到 stdout；日志跟随则输出 NDJSON 或 YAML 文档流。渲染器不能把交互会话安全地缓存成普通结果对象，弃用提示也不能混入结构化 stdout。

## 先拆职责，再改行为 {#layering}

提案将职责分为三层：

| 层次 | 职责 |
|---|---|
| `cmd/barn` | 进程入口、信号与退出状态 |
| 拟新增的 `internal/cli` | Cobra 树、参数验证、展示与输入输出流连接 |
| 应用编排与既有领域包 | 类型化请求和结果、生命周期、宿主网络、镜像与 Mac VM |
{.wide .expand}

按操作实际需要注入输入输出流、环境读取、确认器与运行器。领域服务保持独立于 Cobra，避免用通用分发器抹掉请求类型。确认与 SSH 必须全程使用注入的输入流；只设置 Cobra 输入流、其他位置仍读取全局 `os.Stdin`，会让测试与嵌入调用出现分歧。

提案希望将副作用移到验证完成之后。锁定的 Cobra `1.10.2` 在必填参数与参数组校验之前调用 pre-run hook，因此这些 hook 只适合做规范化和检查。当前生命周期命令有意在部分配置检查前记录 `begin` 事件，让早期失败可追踪；改变这一顺序需要明确审计策略。新增 `--dry-run` 需要真正只读、与执行范围一致的规划器，不能调用修改逻辑后仅跳过最后一次写入。

确认、权限与执行是不同的事实。既有 `network` 和 `hosts` 命令可以成功返回 `applied=false` 的计划，自动化需要检查该字段或传入 `--yes`；确认不会绕过身份、归属或完整性检查。同样，`status` 可能协调中断后的运行记录，不能只凭命令名称像查询就认定它完全只读。

## 按实际进展修订提案 {#implementation-status}

原提案既包含长期契约，也包含有日期边界的产品选择。截至 2026-11-09：

- `1.0.0` 已实现裸命令完整帮助、结构化 `actions[]`、适用销毁命令的确认别名，以及输出环境变量优先级修复。
- CLI 仍位于 `cmd/barn/`。拟议的 `internal/cli` 提取、`--format`、`image update` 与 `ssh-config show/install/uninstall` 命令树尚未落地。
- `1.1.0` 已为适用的清单操作加入 `--image/-I` 与 `--arch/-A` 覆盖参数，统一了结果表格与终端实时进度表（在提示或报错前冻结已打印行），将终端输出收口为纯 ASCII 符号与 `[DONE]`/`[FAILED]`/`[CANCELLED]` 状态标签，并将 YAML 解析升级到 `go.yaml.in/yaml/v4`。

后续行为调整需要独立决策与迁移说明。

## 逐步验证契约 {#acceptance}

先在命令行为和状态格式不变的前提下提取职责，再增加兼容入口，最后单独审阅默认值或选择范围的变化。旧、新程序应依次操作受控测试夹具；帮助、补全与无效输入测试除了检查输出，还应检查是否意外创建文件、启动子进程或访问网络。

回归范围包括 CLI/环境优先级、stdout/stderr 分离、部分失败、远端参数边界、真实 PTY 信号以及确认范围。复用 [`cli_test.go`](https://github.com/pgsty/barn/blob/main/cmd/barn/cli_test.go)、[`output_test.go`](https://github.com/pgsty/barn/blob/main/cmd/barn/output_test.go)、[`remote_command_test.go`](https://github.com/pgsty/barn/blob/main/cmd/barn/remote_command_test.go) 与 [`signal_test.go`](https://github.com/pgsty/barn/blob/main/cmd/barn/signal_test.go)；测试搬入新包时，同步更新 CI 的包路径与构建目标。修改 VM 或宿主网络行为时，补充对应的物理宿主验收。
