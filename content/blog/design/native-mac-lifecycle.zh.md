---
title: "一台原生 Mac 虚拟机的生命周期"
linkTitle: "原生 Mac 生命周期"
description: "Barn 为什么采用具名 Mac 虚拟机、随进程存续的网络、细分锁与明确的恢复证据。"
date: 2026-09-29T10:00:00+08:00
lastmod: 2026-11-08
weight: 110
categories: [Design]
tags: [macOS, Recovery, Architecture]
icon: fa-brands fa-apple
---

`barn mac` 通过 Apple `Virtualization.framework` 管理具名 macOS 虚拟机，独立于 Linux 主机清单。这项功能从 `0.9.0` 引入，使用 macOS 宿主上的原生应用包 `Barn.app`，从 `0.9.2` 起随 Apple Silicon 发行归档交付。本文提炼具名机器实现记录及早期 Mac 复核结论，于 2026-11-08 对照当前实现核验；带日期的证据汇总在[验证历史](/zh/docs/about/history/#mac-native-record)，命令与默认值见 [Mac 参考](/zh/docs/reference/mac/)。

## 网络归机器所有 {#network-ownership}

早期设计使用两个固定槽位与特权网络 helper。2026-09-29 的重构改为具名机器，每个 runner 进程创建自己的 `/24` NAT 网络，客机使用本子网的 `.10` 地址。两台限制针对同时运行的 VM，并与其他 macOS 虚拟化工具和恢复安装共享；已保存的机器并不限于两个固定名字。

网络现在随 VM 生命周期存续：runner 启动时创建，退出时释放。`barn mac` 无需另行安装或协调 root 网络守护进程；早期 helper 协议只作为历史背景保留。

这一拓扑也为首次 SSH 连接提供信任依据。VM 尚未初始化时，Barn 在连接预留地址前后检查 runner 身份，认证客机，再按实例 UUID 固定主机密钥。在该 runner 的私有网络中，除受信任宿主外只有这台客机。后续连接必须匹配已固定的密钥；更换子网保留实例身份，重建则生成新身份。实现见 [`readySSH`](https://github.com/pgsty/barn/blob/main/internal/macvm/ssh.go)。

## 用锁区分不同生命周期 {#locks}

锁的获取顺序为：实例操作 → 共享状态 → 原生 runner。

| 锁 | 保护对象 |
|---|---|
| 实例操作锁 | 串行化同一具名 VM 的生命周期修改 |
| 共享状态锁 | 协调多个操作共同使用的镜像与机器记录 |
| runner 生命周期锁 | 确认原生进程是否仍持有 VM |
{.wide .expand}

仅修改运行时的操作可以使用实例锁，因此准备镜像不会阻塞另一台 VM 关机。停止请求通过操作 nonce 中断本实例的 SSH 就绪等待，再取得操作锁；取消等待并不会允许两条命令同时写状态。规则见 [`operations.go`](https://github.com/pgsty/barn/blob/main/internal/macvm/operations.go) 与 [`readiness_interrupt.go`](https://github.com/pgsty/barn/blob/main/internal/macvm/readiness_interrupt.go)。

关机请求成功只表示状态转换开始。Barn 必须确认 runner 已释放 VM，才能将其视为停止；SSH 断开或 RPC socket 不可用都不足以证明这一点。运行证据不明确时，状态显示 `unknown`，销毁操作中止，保护仍可能挂载在运行中 VM 上的磁盘。实现见 [`status.go`](https://github.com/pgsty/barn/blob/main/internal/macvm/status.go)。

## 恢复安装停止后再发布基底 {#base-images}

Apple 安装器完成回调到达时，恢复安装 VM 仍可能在运行。Barn 会等待安装完成，确认或完成恢复 VM 停机，再发布 `ready=true`、`first_boot=false` 的只读基底；超时或状态不明时拒绝发布。实现见 [`finishRestoreMachine`](https://github.com/pgsty/barn/blob/main/native/mac-runner/Sources/Images.swift)。

新机器从基底克隆磁盘，并获得独立身份和凭据。缓存复用还要检查兼容性：Apple 的在线元数据可能为同一个 build 选择不同的硬件模型，因此 Barn 在复用 ready 基底前，会核对已保存模型的摘要及当前宿主支持情况，不能只比较 build 标签。

重建又引入了一层引用生命周期。即便新机器已经就绪，尚未完成的 recreate 日志仍可能需要旧机器的基底。镜像清理必须统计这些日志引用，遇到无法确认的记录就中止。诊断列表可以报告坏记录并继续显示其他机器，清理操作则必须先得到完整引用集合。这项恢复取舍记录在 [1.0 加固复核](/zh/docs/about/history/#release-1-0-candidates)中。

## 让客机凭据遵循同一边界 {#credentials}

每台机器将 GUI 密码保存在 SSH 私钥旁，两者均使用私有文件权限。SSH 私钥已经授予该客机免密 sudo 权限，单独把 GUI 密码放进 Keychain 无法进一步加强这一宿主本地访问边界，却会给普通 App 升级引入签名身份变化、钥匙串锁定与凭据迁移故障。

因此 Barn 移除了客机密码的 Keychain 存储，理由直接记录在 [`secret.go`](https://github.com/pgsty/barn/blob/main/internal/macvm/secret.go) 中。Developer ID 签名与公证仍使用各自的钥匙串或配置。就绪检查保留已有 SSH 材料，替换 App 保留机器身份与主机密钥固定记录；显式重建机器才更换凭据，重新编译可执行文件不会触发更换。

## 验证状态转换与恢复 {#acceptance}

历史测试暴露了单次启动成功无法覆盖的问题：首次 SSH 需要有界等待，关机必须观察到完成，替换 App 应保留凭据，失败的重建必须保留恢复所需基底。[验证历史](/zh/docs/about/history/)记录了这些实验的日期、候选身份、复用基底的条件与后续正式版检查。

修改这些边界时，使用 [Mac 发布验收流程](/zh/docs/about/mac-release/#acceptance)与已有真机脚本，注明覆盖了从零下载 IPSW、复用已准备基底、GUI/剪贴板，还是仅核心生命周期。单元测试覆盖锁取消和元数据失败，物理 Apple Silicon 宿主提供恢复安装、网络、SSH 与关机的运行证据。
