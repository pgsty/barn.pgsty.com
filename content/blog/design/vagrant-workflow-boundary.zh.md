---
title: "Barn 可以向 Vagrant 学什么"
linkTitle: "Vagrant 与开发循环"
description: "面向 Pigsty 实验环境的可重复配置、环境记录、文件传输与恢复方案。"
date: 2026-11-08T10:00:00+08:00
weight: 70
categories: [设计]
tags: [Vagrant, Pigsty, 工作流]
icon: fa-solid fa-arrows-rotate
lastmod: 2026-11-08
---

Barn 已经能从兼容 Pigsty 的主机清单创建多节点 Linux 实验环境，管理生命周期，并提供 SSH 与结构化输出。Vagrant 值得借鉴的是从“建好虚拟机”到“重复一次实验”之间的工作：执行配置步骤、搬运源码与构建产物、记录环境，以及回到已知状态。

本文是基于 **2026-11-08** Barn 源码核查形成的设计提案。以下优先级是待实现候选，没有指定发布版本或交付日期。当前可用命令见 [CLI 参考](/zh/docs/reference/cli/)。

## 已有能力与实际缺口 {#capabilities}

| 工作流 | Barn 当前能力 | 可改进的方向 |
|---|---|---|
| 定义实验环境 | 静态清单、分组变量继承、逐节点镜像/资源/磁盘、节点选择 | 可复用环境配方；分组选择需要单独定义契约 |
| 收敛节点 | `plan`、`up`，以及显式 `resize`、`recreate`、`destroy` | 保留“节点缺席不能授权删除”的原则 |
| 配置客机 | 可手动重跑的 Bash `provision`，支持 sudo、超时、并发与脚本摘要 | 与生命周期关联的具名步骤和执行策略 |
| 搬运文件 | Virtio-9p 宿主共享与 OpenSSH 连接配置导出 | 内置上传/下载及可选的单向 rsync |
| 恢复实验 | 持久数据盘在普通销毁/重建时保留 | 覆盖相关状态的具名冷快照 |
| 复现镜像 | 签名目录、完整版本选择、导入、缓存和静态仓库工具 | 可携带的环境记录，以及已配置 VM 的导出 |
| 访问服务 | 固定私网地址与 loopback 管理 SSH | 用户声明服务端口及显式绑定地址 |
{.wide}

`barn provision` 已能按需重跑脚本；摘要记录执行内容，不会让脚本自动幂等，也不会跳过相同脚本。清单分组已经支持变量继承，操作选择器则按节点选择。持久盘能跨生命周期操作保留数据，但不能恢复到某个时间点。

这些区别可以从[命令定义](https://github.com/pgsty/barn/tree/main/cmd/barn)、[清单解析器](https://github.com/pgsty/barn/blob/main/internal/config/inventory.go)与 [provision 执行器](https://github.com/pgsty/barn/tree/main/internal/provision)核对。内部端口转发结构，以及名称中含有 “snapshot” 或 “commit” 的函数，都要按实际暴露的行为判断，才能算作产品功能。

## 保持 Pigsty 接入简单 {#pigsty}

Pigsty 需要稳定的节点私网地址、数据盘、管理员账户、SSH 访问和部署代码的交付方式。Barn 提供虚拟机这一层，数据库与服务配置继续由 Pigsty 和 Ansible 负责。

第一步应复用 `barn ssh-config`，保留其中的连接地址、密钥、known-hosts 文件与 VM 身份。客机私网 IP 和宿主侧的 loopback SSH 地址用途不同；使用 scp、rsync 或 Ansible 的脚本除了清单地址，还需要实际连接参数。替换 Vagrant 生成的 SSH 片段时，应明确每个片段由哪个工具维护，避免旧 OpenSSH 条目优先匹配。

Vagrant box 名称也需要显式映射到 Barn 镜像引用，两种格式携带的元数据不同。同一份 Barn 清单可以混用多个发行版，但客机架构作用于整套部署；架构构建矩阵应在当前单部署模型下作为独立实验任务运行。

这样可以继续使用[固定 IP 网络](/zh/blog/design/fixed-ip-two-nics/)与[单部署模型](/zh/blog/design/one-deployment-no-projects/)，并让服务编排保持在已有工具中。

## 建议的实现顺序 {#priorities}

| 优先级 | 最小范围 | 验收条件 |
|---|---|---|
| P0：具名配置步骤 | 有序 shell 步骤、首次/每次执行策略、显式选择与重试；外部 Ansible 调用 | 单独重试失败步骤，不重跑成功步骤；报告节点、步骤、退出码与脚本摘要 |
| P0：环境记录 | 精确镜像版本/摘要/架构、目录 revision、解析后的 VM 规格与脚本摘要 | 用保留的制品在全新临时 `BARN_HOME` 重建拓扑，镜像身份一致且 `plan` 无漂移 |
| P1：文件传输 | 沿用 SSH 契约上传/下载，再补可选单向 rsync | 在客机本地盘构建，取回产物并核对摘要 |
| P1：冷快照 | 从已停机的 Linux VM 开始，一并定义根盘/数据盘、backing 链、NVRAM、规格与身份 | 文件、挂载和客机身份回到保存状态，不影响未选节点 |
| P1：服务端口 | 显式绑定地址、宿主/客机端口、冲突处理与结构化结果 | 重启后服务仍可达；向局域网开放需要显式地址 |
| P1：VM 导出 | 停机、展开 backing 依赖、清理机器/SSH 凭据，输出 qcow2 与元数据 | 导入全新实验环境后以新身份达到 SSH 就绪 |
{.wide}

Vagrant 的[具名配置与运行策略](https://developer.hashicorp.com/vagrant/docs/provisioning/basic_usage)、内置[上传](https://developer.hashicorp.com/vagrant/docs/cli/upload)与[单向 rsync](https://developer.hashicorp.com/vagrant/docs/synced-folders/rsync)提供了可参考的行为。它的[快照](https://developer.hashicorp.com/vagrant/docs/cli/snapshot)依赖 provider 支持，[`package`](https://developer.hashicorp.com/vagrant/docs/cli/package)则列明了 VirtualBox 与 Hyper-V 支持。Barn 应为自己的后端定义具体保证。

环境记录必须保留对精确镜像字节的访问。数字版本前缀可能在目录更新后解析到不同版本；即使锁定完整版本，也无法恢复已下线的制品。VM 磁盘和导出镜像应存放在制品位置，配方、manifest 与摘要可以提交到 Git。

## 需要另行决定的产品范围 {#scope}

不同 `BARN_HOME` 已能隔离持久状态与运行时套接字。完整的并发项目支持还需要网络、端口和 SSH 归属，因为这些宿主集成仍共享资源；增加网卡或子网则会扩大网络验收矩阵。这两类能力应由具体实验需求推动，作为后续候选。Windows 后端、通用 provider/plugin API 和内存态挂起恢复，也各自需要独立设计与维护投入。

第一批改进应以三个流程验收：Pigsty 多节点 PostgreSQL 实验、按发行版和架构组织的扩展构建矩阵，以及源码上传和产物取回的单机开发。改动应减少这些流程中的手工步骤，同时保留显式销毁、镜像输入校验和稳定的机器可读输出。
