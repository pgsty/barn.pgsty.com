---
title: 镜像
description: 签名镜像目录、内置别名、仓库选择、本地缓存校验、导入与清理。
weight: 30
icon: fa-solid fa-hard-drive
---

Barn 使用物化的静态镜像目录与不可变 qcow2 工件。官方与 HTTP 镜像目录必须签名；
用户显式选择的本地或 HTTPS 仓库可以不签名。更新镜像目录不需要发布新的 Barn
二进制，但二进制决定信任哪些签名公钥与镜像安全规则。

> [!WARNING]
> EL7、EL9 9.3/9.6 与 EL10 10.0 是 `deprecated` 兼容镜像；其余内置版本均为
> `supported`。

## 别名与拉取顺序

Barn 0.9.0 内置镜像目录 `2026093001`，包含 9 个镜像系列、41 个工件。`el7` 只有 amd64，其余镜像系列均有 amd64 与 arm64。
EL9 包含 9.3、9.6、9.7、9.8；EL10 包含 10.0、10.1、10.2。
默认请求为本机架构的 `u24:stable`（Ubuntu 24.04）。

以下 `stable` 均覆盖 amd64 和 arm64。这是内置镜像目录快照，不是实时仓库列表。
运行 `barn update`，再用 `barn image list` 查看选定仓库当前的目录。
宿主兼容性与使用限制见[平台与限制](../../about/status/)。

| 镜像系列 | 内置 stable | 发行版系列 |
|---|---|---|
| `d12` | `20260923.2610.1` | Debian 12 |
| `d13` | `20260914.2601.2` | Debian 13 |
| `el8` | `8.10.20240528.3` | Rocky Linux 8.10 |
| `el9` | `9.8.20260525.2` | Rocky Linux 9.8 |
| `u22` | `20260926.0.0` | Ubuntu 22.04 LTS |
| `u24` | `20260926.0.0` | Ubuntu 24.04 LTS |
| `u26` | `20260927.0.0` | Ubuntu 26.04 LTS |

Debian 保留离线安装的 XFS 工具和已生成的 `en_US.UTF-8`，默认 locale 仍为
`C.UTF-8`。Ubuntu 保留Canonical 原始镜像，账户与网络由启动时的 cloud-init 配置。
更新镜像目录只改变新解析的 `stable`；既有 VM 和显式锁定版本继续引用原来的基础镜像。

| 别名 | 发行版 | 架构 | 启动 | 状态 |
|---|---|---|---|---|
| `el7` | CentOS Linux 7.9 / 2211 | amd64 | BIOS | deprecated |
| `el8` | Rocky Linux 8.10 | amd64、arm64 | UEFI | supported |
| `el9` | Rocky Linux 9.7 / 9.8 | amd64、arm64 | UEFI | supported |
| `el9` | Rocky Linux 9.3 / 9.6 | amd64、arm64 | UEFI | deprecated |
| `el10` | Rocky Linux 10.1 / 10.2 | amd64、arm64 | UEFI | supported |
| `el10` | Rocky Linux 10.0 | amd64、arm64 | UEFI | deprecated |
| `d12`、`d13` | Debian | amd64、arm64 | UEFI | supported |
| `u22`、`u24`、`u26` | Ubuntu | amd64、arm64 | UEFI | supported |

```bash
barn image list
barn image info d13
barn image info d13:stable
barn image info el9@9.7
barn image pull d13@20260914.2601.2
barn image pull d13 --arch arm64
barn update
```

镜像目录状态只表达支持策略，不是启动开关：`supported` 表示已通过声明的支持门禁；
`testing` 可在显式测试/风险接受下使用，但不受支持；`deprecated` 只为 EOL 兼容保留；
`unknown` 尚无支持分类。非 `supported` 条目仍可运行，但会打印警告。

拉取时 Barn 会：

1. 为整条命令读取一次选定仓库的本地镜像目录：即本次构建内置的镜像目录，或最近一次
   为该仓库通过 `barn update`/`image sync` 激活的镜像目录；
2. 解析 `image[:channel]` 或 `image@version-prefix`，官方镜像目录缺省为 `u24:stable`；
   独立 `image pull` 默认使用本机架构，可通过 `--arch` 覆盖；生命周期解析遵循 `vm_arch`；
3. 只有尺寸、SHA-256、qcow2 结构全部匹配时才复用本地文件；
4. 否则下载镜像目录指定的准确工件，并支持重试和断点续传；两个官方仓库可互相回退，
   自定义仓库仍为唯一来源。接受的字节始终须匹配镜像目录；不可变上游 URL 只用于溯源。

发布版本构建默认使用 `https://repo.pigsty.io/barn`；仅有长参数的 `--mirror` 选择
`https://repo.pigsty.cc/barn`。优先级依次为 `--repo`、`--mirror`、`BARN_REPO`、
全球默认仓库，两个官方根都保持规范的签名镜像目录信任。仓库选择同时决定本地镜像目录
槽位和下载来源；即使字节已缓存，仍需选择相同的自定义仓库。Barn 不会自动刷新
镜像目录，已有激活目录与已校验缓存时，普通镜像解析可以离线进行。
运行 `barn update` 可获取、校验并激活选定
仓库当前的镜像目录。镜像目录更新使用该指定源，失败时直接报错；镜像下载则在所有
允许的来源均无法提供通过校验的字节时失败。
仅改变 `--repo` 不会获取或激活该仓库的镜像目录；使用它的自定义别名前，先运行
`barn update --repo <root>`。

已校验但可写的缓存文件会恢复为只读；损坏且未被引用的缓存会先保留为带
`.corrupt-<timestamp>` 后缀的文件，再重新下载。仍被 VM 引用的基础镜像保持原位并报错。

## 运行时策略

匹配架构正常使用原生 HVF/KVM，只有一个镜像目录已知例外：原版 EL8 arm64 使用 64 KiB 内存页的内核 无法通过 Apple HVF 运行，因此 Apple Silicon 会自动选择可见的同架构
TCG。显式外来 `vm_arch` 也会使用 TCG；arm64 宿主上的 amd64 客机使用单翻译线程，
以保留 x86 内存序。TCG 结果不能作为性能证据。

EL7 刻意仅支持 Linux/amd64 原生运行。Linux setup 只安装宿主原生 QEMU；外来架构必须
先安装对应系统模拟器与 UEFI 固件，`up`、`recreate` 才会继续；`plan` 无需
这些工具就能解析镜像目录镜像与运行时；但 `local-*` 命名导入在解析时会检查缓存字节，
仍然需要 `qemu-img`。

```bash
barn image pull d13 --mirror
barn image pull d13 --repo https://mirror.example/barn
BARN_REPO=/absolute/local/repository barn up
```

未签名仓库必须是本地路径或 HTTPS。HTTP 仓库必须提供可信密钥签名；不可变上游
工件 URL 必须使用 HTTPS。

## 信任与校验

当前普通构建已经内置两把生产校验公钥；私有签名密钥不在源码仓库中。镜像目录激活会拒绝
未知密钥、畸形内容、同修订号异内容，以及低于该仓库独立最高已接受值的
修订号；只有操作者显式允许时才可降级。

镜像必须是尺寸与 SHA-256 匹配的纯 qcow2，不得有 backing file、外部数据文件、加密或
未知不兼容特性。通过校验的基础镜像变成只读；节点根盘使用写时复制层，永不修改
基础镜像。

```bash
barn update
barn image sync --repo https://repo.example/barn \
  https://repo.example/barn/catalog.json
barn image sync --repo /absolute/repo --allow-downgrade /absolute/repo/catalog.json
barn image reset
```

`image reset` 恢复二进制内置的镜像目录，但不会清除防回滚最高已接受值。

`barn update` 立即检查仓库并激活更新的镜像目录。Barn 不会自动刷新镜像目录；每个版本
内嵌的镜像目录会一直使用到你运行 update。`image sync` 是指定精确 URL 或文件（含降级）的
恢复路径。

按仓库恢复时要显式传入同一个根目录：

```bash
barn image sync --repo /srv/barn --allow-downgrade /srv/barn/catalog.json
barn image reset --repo /srv/barn
```

`--repo` 决定独立的活动镜像目录与 最高已接受修订号的记录，位置参数中的源不会改变这个选择。
`image sync`、`image reset` 接受 `--repo`，不接受 `--mirror`；省略 `--repo` 时使用
`BARN_REPO` 或编译期默认值。未签名自定义镜像目录的精确源必须是选定根下的
`catalog.json`。

## 静态仓库格式

发布根刻意保持很小：

```text
barn/
├── repo.yaml
├── catalog.json
├── catalog.json.minisig       # 官方与 HTTP 仓库必需
└── images/
    └── <image>-<version>-<arch>.qcow2
```

`repo.yaml` 保存人工意图：默认值、别名、通道、精确版本、架构、启动模式、状态和可选、
只用于溯源的上游 URL。`source_user` 记录镜像声明的源登录身份，例如上游镜像的
`rocky`，或经过 Barn 官方归一化后的 `dba`。流水线清理候选镜像时另行接收上游账号。
镜像目录与导入元数据不会替换部署 SSH 用户（默认 `dba`），也不会自行归一化镜像。
该文件不保存任何生成的摘要或大小；`catalog.json` 保持同一逻辑树，
但为每个架构变体物化文件名、SHA-256、工件大小和虚拟大小。`repo.yaml` 是 `schema: 1`；
生成的 `catalog.json` 则是 Barn 内嵌并签名的 Schema-3 镜像目录。

```yaml
schema: 1
revision: 1
defaults: { image: u24, channel: stable, arch: native, boot: uefi }
images:
  u24:
    aliases: [ubuntu24, noble, ubuntu]
    channels: { stable: "1" }
    versions:
      "1":
        status: unknown
        variants:
          amd64: {}
          arm64: {}
```

不显式设置 `file` 时，两个预期工件分别是 `images/u24-1-amd64.qcow2` 与
`images/u24-1-arm64.qcow2`；已有自定义文件可在架构变体中覆盖为安全 basename。

通道与数值前缀都是可移动选择器。存在精确密钥时优先精确匹配；否则只在点分量
边界匹配并选择数值语义最新版本（`el9@9.7` 选择最新 9.7 构建，`el9@9` 选择最新
9.x 发布版本）。不可变工件身份仍是 `(image, exact version, arch)`：

```text
d13:stable + native
  -> d13@20260914.2601.2 + arm64
  -> images/d13-20260914.2601.2-arm64.qcow2
```

`barn repo scan` 只读；`build` 执行严格 YAML 校验、完整 qcow2 inspect/check，
并原子替换镜像目录，永不修改 `repo.yaml` 或 QCOW 字节；`verify` 要求新鲜物化结果与
现有镜像目录逐字节一致。`build`、`verify` 需要本机 `qemu-img`，`scan` 不需要。
应在安装 QEMU 的机器上构建，先发布不可变工件，最后发布镜像目录与匹配签名，尽量
一起切换两者；正文与签名不一致时验签会失败。
修改镜像目录内容时必须增加 `revision`。

## 本地布局与导入

镜像位于 `BARN_HOME/images`（默认 `~/.barn/images`）：各镜像系列目录保存下载工件，
`manifests/` 保存当前激活的镜像目录与每个仓库独立的 最高已接受修订号，`local/` 与
`local-images.json` 保存导入镜像。

```bash
barn image import --sha256 <digest> /path/to/base.qcow2
barn image import --name local-mybase --boot uefi \
  --source-user ubuntu --sha256 <digest> /path/to/base.qcow2
```

CLI 中 `--sha256` 是可选参数；提供独立获得的可信摘要，才能在必做的 qcow2 检查之外加入
显式真实性校验。导入只复制和校验文件，不会清理凭据、安装 cloud-init、识别客机 CPU
架构或证明镜像可启动。

命名本地别名必须以 `local-` 开头，避免未来签名镜像目录遮蔽它们。`--name`、`--boot`、
`--source-user` 必须同时提供。命名导入记录执行导入的宿主原生架构，没有
`image import --arch` 参数；外来架构镜像应使用声明明确架构变体的静态仓库。
别名不可变，镜像字节或元数据改变时应使用新名字。在主机清单中通过
`vm_image: local-mybase` 选择命名导入；不指定名字的导入只填充缓存。

## 清理

```bash
barn image prune --dry-run
barn image prune --yes
```

不带参数的 `prune` 与 `--dry-run` 只报告候选，`--yes` 才执行删除。保护集合是选定活动
镜像目录中的全部工件、已应用节点的镜像摘要，以及注册的本地别名。因此，即使没有 VM
使用，当前镜像目录镜像和命名导入仍会保留。未被保护的镜像与识别出的过期暂存文件
才是候选；不安全或损坏的文件会导致报错。检查自定义镜像目录的缓存策略时，要传入
相同 `--repo`。执行 `destroy`、`destroy --purge` 与 `purge` 后镜像仍会保留。

使用 `go run ./tools/catalogexport /absolute/new/catalog.json` 可逐字节导出编译期
Schema-3 镜像目录。
公开镜像目录若使用相同版本，就必须使用完全相同的字节；同版本不同内容会按 equivocation
拒绝。应用发行包的校验清单与镜像镜像目录签名用途不同，详见[发布工程](../../about/engineering/)。
