---
title: 镜像
description: 签名镜像目录、内置别名、仓库选择、本地缓存校验、导入与清理。
weight: 30
icon: fa-solid fa-hard-drive
---

Barn 使用生成的静态镜像目录与不可变 qcow2 产物。官方与 HTTP 镜像目录必须签名。
用户显式选择的本地或 HTTPS 仓库可以不签名。
更新镜像目录无需发布新的 Barn 二进制。但二进制决定受信任的签名公钥和镜像安全规则。

> [!WARNING]
> EL7、EL9 9.3/9.6 与 EL10 10.0 是 `deprecated` 兼容镜像；其余内置版本均为
> `supported`。

## 别名与拉取顺序

Barn 0.9.1 内置镜像目录 `2026093001`，包含 9 个镜像系列、41 个产物。
`el7` 只有 amd64，其余镜像系列均有 amd64 与 arm64。
EL9 包含 9.3、9.6、9.7、9.8；EL10 包含 10.0、10.1、10.2。
默认请求为本机架构的 `u24:stable`（Ubuntu 24.04）。

以下 `stable` 除 `el7` 只有 amd64 外，均覆盖 amd64 和 arm64。这是内置镜像目录快照，不是实时仓库列表。
运行 `barn update`，再用 `barn image list` 查看选定仓库当前的目录。
宿主兼容性与使用限制见[平台与限制](../../about/status/)。

| 镜像系列 | 内置 stable | 可用别名 |
|---|---|---|
| `d12` | `20260923.2610.1` | `debian12`、`bookworm` |
| `d13` | `20260914.2601.2` | `debian13`、`debian`、`trixie` |
| `el7` | `7.9.20221112.0` | `c7`、`centos7`、`centos79` |
| `el8` | `8.10.20240528.3` | `rocky8` |
| `el9` | `9.8.20260525.2` | `rocky9`、`rocky` |
| `el10` | `10.2.20260525.0` | `rocky10` |
| `u22` | `20260926.0.0` | `ubuntu22`、`ubuntu2204`、`jammy` |
| `u24` | `20260926.0.0` | `ubuntu`、`ubuntu24`、`ubuntu2404`、`noble` |
| `u26` | `20260927.0.0` | `ubuntu26`、`ubuntu2604`、`resolute` |

Ubuntu 三个系列分别为 22.04、24.04、26.04 LTS。`el7` 为 CentOS Linux 7.9；
`el8`、`el9`、`el10` 使用 Rocky Linux。

Debian 保留离线安装的 XFS 工具和已生成的 `en_US.UTF-8`，默认区域设置仍为 `C.UTF-8`。
Ubuntu 保留 Canonical 原始镜像。cloud-init 在启动时配置账户与网络。
更新镜像目录只改变新解析的 `stable`。已有虚拟机和显式锁定版本继续引用原来的基础镜像。
如果清单中的通道或数值前缀解析到新版本，后续 `plan`、`up` 会检测到差异。
替换已有节点仍需显式 `recreate`。

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

`image list` 列出所有版本、架构和已注册本地别名，没有 `--arch` 过滤参数。
`image info` 与 `pull` 一样，默认选择本机架构。
没有缓存时，查看镜像目录条目不需要 QEMU。缓存存在时，Barn 会校验缓存，因此需要 `qemu-img`。
`list` 与 `info` 均不下载镜像。

镜像目录状态只表达支持策略，不决定能否启动。
`supported` 表示已通过声明的支持检查。
`testing` 可在显式测试或接受风险的前提下使用，但不受支持。
`deprecated` 只为 EOL 兼容保留，`unknown` 尚无支持分类。
非 `supported` 条目仍可运行，但会打印警告。

拉取时 Barn 会：

1. 为整条命令读取一次选定仓库的本地镜像目录：即本次构建内置的镜像目录，或最近一次
   为该仓库通过 `barn update`/`image sync` 激活的镜像目录；
2. 解析 `image[:channel]` 或 `image@version-prefix`，官方镜像目录缺省为 `u24:stable`；
   独立 `image pull` 默认使用本机架构，可通过 `--arch` 覆盖；生命周期解析遵循 `vm_arch`；
3. 只有尺寸、SHA-256、qcow2 结构全部匹配时才复用本地文件；
4. 否则下载镜像目录指定的镜像文件，支持重试和断点续传。两个官方仓库可互相回退，自定义仓库则只使用自身来源。
   下载内容必须通过镜像目录中的校验；不可变上游 URL 只用于溯源。

发布版本构建默认使用 `https://repo.pigsty.io/barn`。仅有长参数的 `--mirror` 选择 `https://repo.pigsty.cc/barn`。
优先级依次为 `--repo`、`--mirror`、`BARN_REPO`、全球默认仓库。
两个官方仓库都要求可信密钥签署的镜像目录。

仓库选择同时决定使用哪份本地镜像目录，以及从哪里下载镜像。即使镜像已缓存，仍需选择相同的自定义仓库。
Barn 不会自动刷新镜像目录。已有激活目录与已校验缓存时，普通镜像解析可以离线执行。

运行 `barn update` 可获取、校验并激活所选仓库当前的镜像目录。
镜像目录更新只使用该来源，无法获取有效目录时直接报错。
镜像下载可以尝试允许的备用来源；全部来源都无法提供校验通过的文件时，下载才失败。

仅改变 `--repo` 不会获取或激活该仓库的镜像目录。
使用该仓库的自定义别名前，先运行 `barn update --repo <root>`。

Barn 将已校验但可写的缓存文件恢复为只读。
缓存损坏且未被引用时，Barn 先将其保留为带 `.corrupt-<timestamp>` 后缀的文件，再重新下载。
基础镜像仍被虚拟机引用时，Barn 保持它的位置并报错。

## 运行时策略

架构匹配时，Barn 通常使用原生 HVF/KVM。镜像目录中只有一个已知例外。
原版 EL8 arm64 的内核使用 64 KiB 内存页，无法通过 Apple HVF 运行。
因此，Apple Silicon 会自动选择同架构 TCG，并在输出中显示。
显式外来 `vm_arch` 也使用 TCG。arm64 宿主上的 amd64 客机使用单翻译线程，以保留 x86 内存序。
TCG 结果不能作为性能证据。

EL7 仅支持 Linux/amd64 原生运行。Linux setup 只安装宿主原生 QEMU。
使用外来架构前，必须安装对应的系统模拟器与 UEFI 固件，`up`、`recreate` 才会继续。
`plan` 无需这些工具就能解析镜像目录中的镜像与运行时。
但解析 `local-*` 命名导入时，Barn 会检查缓存字节，因此仍需要 `qemu-img`。

```bash
barn image pull d13 --mirror
barn image pull d13 --repo https://mirror.example/barn
BARN_REPO=/absolute/local/repository barn up
```

未签名仓库必须是本地路径或 HTTPS。HTTP 仓库必须提供可信密钥签名；不可变上游
镜像 URL 必须使用 HTTPS。

## 信任与校验

当前普通构建内置两把生产校验公钥。私有签名密钥不在源码仓库中。
激活镜像目录时，Barn 拒绝未知密钥、畸形内容、同修订号的不同内容。
它也拒绝低于该仓库最高已接受修订号的更新。各仓库独立记录此值。
只有操作者显式允许时，Barn 才接受降级。

镜像必须是尺寸与 SHA-256 匹配的纯 qcow2。
镜像不得依赖其他基础文件（backing file）或外部数据文件，也不得使用加密或未知的不兼容特性。
通过校验后，Barn 将基础镜像设为只读。节点根盘使用写时复制层，不修改基础镜像。

```bash
barn update
barn image sync --repo https://repo.example/barn \
  https://repo.example/barn/catalog.json
barn image sync --repo /absolute/repo --allow-downgrade /absolute/repo/catalog.json
barn image reset
```

`image reset` 恢复二进制内置的镜像目录，但不会清除用于防止回滚的最高已接受修订号。

用 `barn update` 从仓库刷新镜像目录，或用 `image sync` 从指定 URL 或文件恢复目录，也可显式允许降级。
普通命令继续使用当前已激活的本地目录。

按仓库恢复时要显式传入同一个根目录：

```bash
barn image sync --repo /srv/barn --allow-downgrade /srv/barn/catalog.json
barn image reset --repo /srv/barn
```

`--repo` 决定恢复哪一个仓库的活动镜像目录及最高已接受修订号记录。命令末尾的 URL 或文件路径只指定恢复来源，不改变所选仓库。
`image sync`、`image reset` 接受 `--repo`，不接受 `--mirror`。
省略 `--repo` 时，Barn 使用 `BARN_REPO` 或编译期默认值。
未签名自定义镜像目录的精确来源必须是所选根目录下的 `catalog.json`。

## 静态仓库格式

发布根目录包含以下文件：

```text
barn/
├── repo.yaml
├── catalog.json
├── catalog.json.minisig       # 官方与 HTTP 仓库必需
└── images/
    └── <image>-<version>-<arch>.qcow2
```

`repo.yaml` 保存人工配置：默认值、别名、通道、精确版本、架构、启动模式、状态，以及可选的上游 URL。
上游 URL 只用于溯源。
`source_user` 记录镜像声明的源登录身份，例如上游镜像的 `rocky`，或经 Barn 官方归一化后的 `dba`。
流水线清理候选镜像时，另行接收上游账号。
镜像目录与导入元数据不会替换部署 SSH 用户（默认 `dba`），也不会自行归一化镜像。

策略文件不保存生成的摘要或大小。
`catalog.json` 保持同一逻辑树，并为每个架构变体生成文件名、SHA-256、产物大小和虚拟大小。
`repo.yaml` 使用 `schema: 1`。生成的 `catalog.json` 是 Barn 内嵌并签名的 Schema-3 镜像目录。

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

未显式设置 `file` 时，预期产物为 `images/u24-1-amd64.qcow2` 与 `images/u24-1-arm64.qcow2`。
已有自定义文件时，可在架构变体中指定安全的文件基本名。

`repo scan/build/verify` 的根参数必须是绝对路径。
根目录与平铺的 `images/` 目录不能是符号链接，也不能对组或其他用户可写。
`repo.yaml` 必须是非空、最大 4 MiB 的普通文件，不能是符号链接。
`images/` 中，不符合安全 qcow2 文件名规则的额外文件或子目录会标为 unsafe（不安全）。
missing（缺失）或不安全的产物会阻止构建。安全但未声明的 qcow2 标为 untracked，只报告，不进入生成的镜像目录。
即使发现缺失或不安全的产物，`repo scan` 也会成功返回报告。
自动化必须检查对应数组，不能只看退出码 0。

启动模式按架构变体 → 镜像系列 → `defaults.boot` 继承。
状态按架构变体 → 版本 → `unknown` 继承。
每个系列都必须定义默认通道，每个通道必须指向存在的精确版本。
系列名称和别名必须唯一，且不能使用保留的 `local-` 前缀。
面向 0.9.1 清单时，应避免把内置别名重新指向其他系列。
[清单别名归一化](../configuration/#vm-变量)会先使用二进制内置映射，再查询自定义镜像目录。

镜像目录更新后，同一通道或数值前缀可能解析到不同版本。
存在精确版本键时，Barn 优先精确匹配；否则按点号分隔的完整分量匹配前缀，并按数值选择最新版本。
`el9@9.7` 选择最新 9.7 构建，`el9@9` 选择最新 9.x 发布版本。
不可变产物身份仍是 `(image, exact version, arch)`：

```text
d13:stable + native
  -> d13@20260914.2601.2 + arm64
  -> images/d13-20260914.2601.2-arm64.qcow2
```

`barn repo scan` 只读。
`build` 严格校验 YAML，并完整检查 qcow2 的结构与一致性，再原子替换镜像目录。
它不修改 `repo.yaml` 或 QCOW 字节。`verify` 要求新生成的结果与现有镜像目录逐字节一致。
`build`、`verify` 需要本机 `qemu-img`，`scan` 不需要。
请在安装 QEMU 的机器上构建。先发布不可变产物，最后发布镜像目录与匹配签名，尽量一起切换两者。
正文与签名不一致时，验签会失败。修改镜像目录内容时，必须增加 `revision`。

## 本地布局与导入

镜像位于 `BARN_HOME/images`（默认 `~/.barn/images`）。各镜像系列目录保存下载产物。
`manifests/` 保存当前激活的镜像目录，以及每个仓库独立的最高已接受修订号。
`local/` 与 `local-images.json` 保存导入镜像。

```bash
barn image import --sha256 <digest> /path/to/base.qcow2
barn image import --name local-mybase --boot uefi \
  --source-user ubuntu --sha256 <digest> /path/to/base.qcow2
```

CLI 中 `--sha256` 是可选参数。
提供从可信来源独立获得的摘要，可在必要的 qcow2 检查之外，确认文件与该来源公布的内容一致。
导入只复制和校验文件。它不会清理凭据、安装 cloud-init、识别客机 CPU 架构或验证镜像能否启动。
建议使用绝对源路径，避免歧义。导入需要普通非符号链接文件与 `qemu-img`。

运行时导入、下载和静态仓库产物的文件大小上限为 8 GiB。
此限制不同于 qcow2 虚拟容量，以及配置的根盘和数据盘容量。

源文件名必须以字母或数字开头，只包含字母、数字、`.`、`_`、`+`、`-`，且以 `.qcow2` 或 `.img` 结尾。
导入文件共用按文件名索引的 `local/` 缓存。
文件字节不同但文件名相同时，即使指定新别名，也会冲突。需要并存时，请先更换源文件名。

本地镜像别名必须以 `local-` 开头，避免被未来的签名镜像目录覆盖。
`--name`、`--boot`、`--source-user` 必须同时提供。
命名导入记录执行导入的宿主原生架构，没有 `image import --arch` 参数。
外来架构镜像应使用明确声明架构变体的静态仓库。
别名不可变。镜像字节或元数据改变时，应使用新名字。
在清单中通过 `vm_image: local-mybase` 选择命名导入。不指定名字的导入只填充缓存。

## 清理

```bash
barn image prune --dry-run
barn image prune --yes
```

不带参数的 `prune` 与 `--dry-run` 只报告候选，`--yes` 才执行删除。
Barn 保护所选活动镜像目录中的全部产物、已应用节点的镜像摘要，以及注册的本地别名。
因此，即使没有虚拟机使用，当前镜像目录中的镜像和命名导入仍会保留。
未被保护的镜像与识别出的过期暂存文件才是候选。不安全或损坏的文件会导致报错。
检查自定义镜像目录的缓存策略时，要传入相同的 `--repo`。
执行 `destroy`、`destroy --purge` 与 `purge` 后，镜像仍会保留。

镜像目录保护只覆盖当前所选仓库，不覆盖曾经激活的所有仓库。
缓存仅属于其他仓库，且没有已应用节点或本地别名保护其摘要时，也可能成为候选。
删除前请先查看预演结果：如果后续候选检查失败，清理操作不会撤销已完成的删除。
清理不会移除隔离的 `.corrupt-*` 文件，也不会移除不符合已知镜像及暂存命名规则的其他文件。

使用 `go run ./tools/catalogexport /absolute/new/catalog.json` 可逐字节导出编译期 Schema-3 镜像目录。
公开镜像目录若使用相同版本，就必须使用完全相同的字节。
同一版本对应不同内容时，Barn 会因版本内容冲突而拒绝目录。
应用发行包的校验清单与镜像目录签名用途不同，详见[发布工程](../../about/engineering/)。
