---
title: 参考
linkTitle: 参考
description: Farrow 读取的 Pigsty Inventory 与命令行的准确契约。
weight: 20
icon: fa-solid fa-book-open
cascade:
  type: docs
---

公开发布基线为 **v0.8.0（预发布版本）**。本参考文档于 2026-09-26 同时对照了本地
源码 **`b91ec37`**，即**尚未发布的 0.9 候选版本**；候选版本特有的变化会明确标注。
源码检出状态不代表已经发布，详见[版本矩阵](../about/status/#documentation-baseline)。

- [配置](configuration/)：发现顺序、变量、默认值、磁盘、共享、命名与漂移。
- [命令行](cli/)：命令、关键参数、输出模式与退出码。
- [Mac 命令](mac/)：尚未发布的 `farrow mac` 的命令、JSON 结果与失败原因。
- [镜像](images/)：签名 Catalog、别名、本地缓存、拉取、导入与清理。
- [镜像流水线](image-pipeline/)：Candidate 校验与离线归一化。

Farrow 不提供受支持的 Go Library API；`internal/` 下的包都是实现细节。
