---
title: 参考
linkTitle: 参考
description: Barn 0.9.2 的配置字段、命令参数、输出格式与镜像仓库说明。
weight: 20
icon: fa-solid fa-book-open
no_list: true
cascade:
  type: docs
---

本节汇总 **Barn 0.9.2** 的配置字段、命令行参数、结构化输出格式与镜像仓库规范，尚未发布的行为会单独标注并汇总到[未发布变更](../about/unreleased/)。需要按步骤上手操作时，请先阅读[使用指南](../start/)。

- [Linux 配置](configuration/) — 清单发现顺序、变量继承、默认值、数据盘、目录共享与节点漂移规则
- [命令行](cli/) — 全局参数、Linux 生命周期命令、JSON/YAML 结构化输出与退出码
- [Mac 命令](mac/) — `barn mac` 子命令、虚拟机设置、JSON 输出结构、失败原因与文件布局
- [Linux 镜像](images/) — 内置镜像目录 `2026093001`、版本别名、仓库验签、本地导入与缓存清理
- [镜像流水线](image-pipeline/) — 面向贡献者的 Linux qcow2 候选镜像校验与离线归一化工具
{.cards}

Barn 对外承诺的稳定接口是 `barn` 命令行（可通过 `barn version` 与 `barn <command> --help` 查看当前安装版本）；Go 仓库 `internal/` 下的包属于内部实现。镜像表对应 Barn `0.9.2` 二进制内置的镜像目录快照，日常运行 `barn update` 即可激活更新的签名仓库元数据，无需升级可执行文件。构建与发布门禁详见[发布工程](../about/engineering/)。
