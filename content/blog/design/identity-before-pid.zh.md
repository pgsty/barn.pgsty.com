---
title: "PID 不是虚拟机身份"
linkTitle: "先证明身份，再处理 PID"
description: "为什么 Farrow 在发送信号或删除任何东西前，必须让 QMP 身份、进程证据、类型化 Invocation 与 Journal 相互吻合。"
date: 2026-08-28T10:00:00+08:00
weight: 40
categories: [设计]
tags: [QMP, 恢复, 安全]
icon: fa-solid fa-fingerprint
lastmod: 2026-09-26
---

> [!NOTE]
> **2026-09-26 校准：** 保留原始写作日期；下文已按当前实现更新。公开版本与未发布候选的
> 边界见[当前状态](/zh/docs/about/status/)，不以本文日期代替发布或验收日期。

Pidfile 只能回答一个问题：写入文件时，某个进程使用了哪个整数。它不能证明进程仍然存活，
不能证明 PID 没有被复用，不能证明可执行文件就是 QEMU，也不能证明这个 QEMU 正是操作者
想停止的节点。

这些证据不足以授权 `SIGKILL`，更不足以授权删除 Root Disk。

Farrow 把身份视为一条由独立证据组成的链。每一环承担不同职责；只有操作所需的证据全部一致，
破坏性动作才可以继续。

## QMP 是主要运行时身份

每台 VM 都有生成的 UUID 与预期 QEMU Name。启动后，Farrow 连接 QEMU Machine Protocol
Socket，并向 QEMU 查询这两个字段。仅仅因为进程启动命令返回，或某条 Socket 路径出现，并不
代表 VM 已经启动；QMP 必须报告预期 Name 与 UUID。

同一检查也保护关机。如果 QMP Endpoint 返回另一个 Name 或 UUID，它不会被解释成“大概就是
旧 VM”，而是明确的身份不匹配；Farrow 不会通过它发送任何命令。

QMP 同时提供干净关机路径：请求 Guest Powerdown，等待 Guest；若有界 Graceful Wait 到期，再
要求 QEMU Quit。进程信号只是备用工具，不是主要生命周期 API。

> [!NOTE]
> **决策状态：当前有效。** 本文解释 Fail-closed 生命周期边界。运维恢复应从
> [故障排查](/zh/docs/start/troubleshooting/)开始，而不是手工删除。

## 进程身份封住备用路径的缺口

Crash、Runtime Directory 损坏或半完成关机都可能让 QMP 不可用。为此 Farrow 会记录一组
进程身份：

- PID；
- 可执行文件路径；
- 进程启动时间；
- 实际命令行的 SHA-256。

完整的类型化 QEMU Invocation 与它一同保存。发送 `SIGTERM` 前，Farrow 会重新读取活进程，
要求整组身份完全匹配；升级到 `SIGKILL` 前还会再次捕获，专门封住有界 TERM 等待期间产生的
PID 复用窗口。

如果 QMP 仍然可用但某项 QMP 操作失败，Farrow 不会绕开活控制平面直接发信号；如果 QMP
报告另一个身份，它会停止；如果进程元组无法验证，它也会停止。“无法证明”本身就是结果，
不是降低检查强度的理由。

**未发布的 0.9 候选更新：** QMP 不可用、且记录的 PID 已被明确证明属于无关进程时，
Farrow 把旧 VM 视为已停止，绝不会向那个无关进程发送信号。这与身份不可读或有歧义不同，
后两种情况仍会阻止操作。

## Journal 描述 State 提交前的工作

Committed Node State 无法描述创建的最早阶段：Disk 与 Seed 必须先存在，VM 才能启动；进程
必须先启动，身份才能提交。若 CLI 在这个间隔 Crash，就可能留下没有可信 Owner 的工件。

Farrow 会先写一份 `0600` Prepare Journal，其中包含：

- Operation UUID 与 VM UUID；
- Node Name 与 Resolved-spec Hash；
- 固定 Kind/Path 白名单中的每个已完成工件；
- 准备完成后的类型化 QEMU Invocation；
- Commit 成功后的准确 Node-state Path。

Journal 是严格的版本化 JSON。未知字段、无效 UUID、不安全路径、重复工件、错误 Mode、Symlink，
或逃出 Node Directory 的路径都会使它无效。

于是恢复流程可以回答一个边界明确的问题：*这次尚未提交的操作创建了哪些工件？* 它不需要
扫描目录后猜测。

## Rollback 比 Cleanup 更窄

只有在 Committed Node State 不存在，并且类型化 Invocation 对应的 QMP Socket 与 Pidfile
都不存在时，才允许 Offline Rollback。Node Directory 里只能出现 Journal 与已完成白名单工件；
随后按逆序移除已完成工件，再移除 Journal 与空节点目录。

**未发布的 0.9 候选更新：** 首次 `up` 失败后，即使已经修改 Inventory 也可以重试。
安全清理按 Journal 的已完成工件列表执行，不再要求新期望配置与失败时的旧配置一致。

已提交节点绝不会因为旧 Prepare Journal 被回滚；已有磁盘不会被补进 Action List；未知文件
会阻止目录删除，而不是作为附带损失被一扫而空。

普通 Destroy 采用同样思路：证明路径包含、文件类型、属主边界、进程已经死亡，以及准确工件
集合。Persistent Disk 有独立保留与 Purge 规则。只有已知文件全部移除后才删除目录，所以任何
未知条目都会变成错误。

## 原子状态让证据持久

状态更新使用同目录临时文件、`fsync`、原子 Rename 与父目录 `fsync`，并拒绝 Symlink Target；
Deployment 与 Node Lock 串行化修改。目标不是让 Crash 永不发生，而是保证 Crash 后留下的要么
是旧的完整事实，要么是新的完整事实，再加一份描述两者之间有界阶段的 Journal。

这套设计刻意保守。它有时会要求操作者检查一个更激进工具可能直接删除的歧义资源。对本地
数据库实验室而言，保留证据是更安全的失败方式。

下一篇：[`repo.yaml` 是意图，`catalog.json` 是证据](/zh/blog/design/repo-yaml-catalog-json/)。
