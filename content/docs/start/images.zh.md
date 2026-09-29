---
title: 镜像仓库
description: 选择 Guest 镜像、使用镜像站、导入本地 qcow2，并清理缓存。
weight: 40
icon: fa-solid fa-box-archive
---

正常使用不需要先执行镜像命令：`farrow up` 默认按本机架构解析 `u24:stable`，并拉取
最终对应的不可变版本。
Farrow 一直使用已安装构建内置的 Catalog，直到你运行 `farrow update`：它会获取、校验并
激活仓库当前的 Catalog；没有任何自动刷新。恢复时可用 `image sync` 显式激活精确 URL
或文件。

## 选择镜像

先查看可用别名：

```bash
farrow image list
farrow image info u24
farrow image info u24:stable
```

内置 Family 包括 `el7`、`el8`、`el9`、`el10`、`d12`、`d13`、`u22`、`u24`、
`u26`。裸名称选择 `stable`，`name:channel` 选择频道；`name@version` 优先精确匹配，
较短的数值 Selector 则按点分量边界选择最新匹配版本：

```yaml
all:
  vars:
    vm_image: el9
    vm_version: "9.7"
```

这里 `9.7` 选择最新 9.7.x Build，`9` 选择最新 9.x Release。若希望跟随仓库可移动的
Stable Channel，则改用 `vm_image: el9:stable` 并删除 `vm_version`。独立的
`vm_version` 不能与 `vm_image` 中的 `:channel` 或 `@version` 同时使用。

修改配置后先运行 `farrow plan`。已有节点的镜像请求改变时，需要显式执行
`farrow recreate <node>`；`up` 会报告定义漂移而不会自动重建。仅更新 Catalog 不会改变
已有节点或它保存的基础镜像身份。新增或显式重建的节点才会按照活动 Catalog 解析选择器。

需要可重复的实验环境时，应锁定 `image info` 显示的完整版本，而不是可移动的 Channel
或数值前缀：

```yaml
all:
  vars:
    vm_image: d13@20260914.2601.1
```

YAML 中的数值 `vm_version` 建议加引号，以保留完整原文。

> [!WARNING]
> 除兼容用途的 EOL `el7`、EL9 9.3/9.6 与 EL10 10.0 为 `deprecated` 外，
> 其余内置版本均为 `supported`。

## 使用镜像站

Release 构建默认使用 `https://repo.pigsty.io/farrow`。单条命令可通过仅有长参数的
`--mirror` 选择中国官方仓库，也可以用 `--repo` 指定自定义根：

```bash
farrow image pull u24 --mirror
farrow up --mirror
farrow update --repo https://mirror.example/farrow
farrow image pull u24 --repo https://mirror.example/farrow
farrow up --repo https://mirror.example/farrow
```

或为当前 Shell 设置默认仓库：

```bash
export FARROW_REPO=https://mirror.example/farrow
farrow update
farrow up
```

选择优先级依次为 `--repo`、`--mirror`、`FARROW_REPO`、全球默认仓库。`--mirror`
解析为 `https://repo.pigsty.cc/farrow`，两个官方根都保持规范的签名 Catalog 信任。
`FARROW_REPO` 也可以是绝对本地目录。显式本地或 HTTPS 仓库可使用未签名 Catalog；HTTP
仓库必须提供可信密钥签名。文件大小、SHA-256 与 qcow2 结构始终校验。

镜像下载会重试临时故障，并接续中断的传输。自 0.7.0 起，选定官方端点无法提供镜像时，
两个官方仓库可以互相回退，仍须匹配同一 Catalog 中的尺寸与摘要。自定义仓库不会回退
到其他站点；Catalog Upstream URL 只用于溯源，始终不是备用下载源。

这项回退只针对镜像工件。`farrow update` 获取选定仓库的 Catalog，`image sync` 读取
明确指定的 URL 或文件；两者都不会升级 Farrow 程序。活动 Catalog 按仓库分别记录。
新 `--repo` 在激活该根的 Catalog 前使用内置 Catalog；只改变下载源不会让自定义别名出现。

## 构建静态仓库

仓库只是一个可以直接 rsync 或静态 HTTP 托管的目录：

```text
farrow/
├── repo.yaml
├── catalog.json
├── catalog.json.minisig       # 官方与 HTTP 仓库必需
└── images/
    └── d13-1-arm64.qcow2
```

`repo.yaml` 是唯一人工维护源。上面单个 arm64 镜像的最小完整配置如下：

```yaml
schema: 1
revision: 1
defaults: { image: d13, channel: stable, arch: native, boot: uefi }
images:
  d13:
    channels: { stable: "1" }
    versions:
      "1":
        status: testing
        variants:
          arm64:
            source_user: debian
```

将独立校验且已具备 cloud-init 的镜像放到
`/srv/farrow/images/d13-1-arm64.qcow2`。若是 x86 Guest，文件名与 Variant 都改用
`amd64`；`source_user` 应填写镜像的源身份。仓库根必须是绝对路径、非符号链接，且不能
允许组或其他用户写入。在本机生成 `catalog.json`：

```bash
farrow repo scan /srv/farrow
farrow repo build /srv/farrow
farrow repo verify /srv/farrow
```

`scan` 只读；`build` 永不修改 `repo.yaml` 或镜像字节，它运行完整的 `qemu-img check`，
并物化文件名、SHA-256、工件大小和虚拟大小。`build`、`verify` 需要本机
`qemu-img`，`scan` 不需要。在安装 QEMU 的机器上构建后，发布时先上传不可变 QCOW，
最后发布 `catalog.json` 与匹配签名。本地/HTTPS 示例可以不签名；普通 HTTP 与官方仓库
必须具有可信签名。每次修改 Catalog 内容都应增加 `revision`。

创建 VM 前，先激活并检查这个本地仓库：

```bash
farrow update --repo /srv/farrow
farrow image info d13 --arch arm64 --repo /srv/farrow
farrow image pull d13 --arch arm64 --repo /srv/farrow
```

`plan`、`up`、`recreate` 都传入相同的 `--repo /srv/farrow`，也可设置
`FARROW_REPO=/srv/farrow`。Inventory 中选择 `vm_image: d13@1` 与
`vm_arch: arm64`；导入 Catalog 不会改写 Inventory 默认值。
`farrow image reset --repo /srv/farrow` 将该根恢复到内置 Catalog，同时保留防回滚记录。

## 导入与清理

本机原生架构的单个自定义镜像可以直接导入，并提供独立获得的摘要。CLI 中 `--sha256`
是可选参数；有可信摘要时建议填写：

```bash
farrow image import --name local-mybase --boot uefi \
  --source-user ubuntu --sha256 <digest> /path/to/base.qcow2
```

自定义别名必须以 `local-` 开头；`--name`、`--boot`、`--source-user` 必须一起提供。
导入只检查 qcow2 并复制到 Farrow 缓存，不会准备 Guest 软件；镜像必须已经支持 Farrow
使用的 cloud-init 初始化。命名导入记录宿主架构，外来架构镜像应使用静态仓库。
在 Inventory 中设置 `vm_image: local-mybase`，再运行 `farrow plan`。

Prune 会保护选定活动 Catalog 的全部镜像、已应用节点的镜像，以及全部已注册本地别名，
因此销毁所有 VM 后也不会简单清空缓存。删除前先看候选列表：

```bash
farrow image prune --dry-run
farrow image prune --yes
```

签名、回滚保护、缓存布局、架构与 TCG 规则见[镜像参考](../../reference/images/)；准备镜像
Candidate 及发布前的独立验证要求见[镜像流水线](../../reference/image-pipeline/)。
