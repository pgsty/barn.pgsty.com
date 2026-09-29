---
title: 参考
linkTitle: 参考
description: Barn 读取的 Pigsty Inventory 与命令行的准确契约。
weight: 20
icon: fa-solid fa-book-open
cascade:
  type: docs
---

本参考描述 **Barn 0.9.0 发布候选**。Barn 只使用新名称与全新的 Barn 状态，
不提供旧开发版本的兼容或迁移层。编写脚本前先核对 `barn version`，
发布进度见[当前状态](../about/status/#documentation-baseline)。

- [配置](configuration/)：发现顺序、变量、默认值、磁盘、共享、命名与漂移。
- [命令行](cli/)：命令、关键参数、输出模式与退出码。
- [Mac 命令](mac/)：尚未发布的 `barn mac` 的命令、JSON 结果与失败原因。
- [镜像](images/)：签名 Catalog、别名、本地缓存、拉取、导入与清理。
- [镜像流水线](image-pipeline/)：Candidate 校验与离线归一化。

Barn 不提供受支持的 Go Library API；`internal/` 下的包都是实现细节。
