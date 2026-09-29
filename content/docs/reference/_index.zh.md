---
title: 参考
linkTitle: 参考
description: Barn 0.9.0 的配置字段、命令参数、输出格式与镜像仓库说明。
weight: 20
icon: fa-solid fa-book-open
cascade:
  type: docs
---

在这里查找 **Barn 0.9.0** 的字段、参数和命令结果。需要按步骤操作时，先看[使用指南](../start/)。

| 参考 | 内容 |
|---|---|
| [Linux 配置](configuration/) | 配置发现、变量、默认值、磁盘、共享与变更规则 |
| [命令行](cli/) | 通用参数、Linux 命令、结构化结果与退出码 |
| [Mac 命令](mac/) | macOS 虚拟机命令、设置、JSON 结果与文件布局 |
| [Linux 镜像](images/) | 镜像版本、仓库、签名、导入与缓存管理 |
| [镜像流水线](image-pipeline/) | 供贡献者使用的 Linux 镜像构建与检查工具 |

使用其他版本时，请核对 `barn version` 与 `barn <command> --help`。
Barn 对外提供命令行接口，Go `internal/` 下的包属于实现细节。
