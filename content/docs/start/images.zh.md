---
title: 镜像仓库
description: 选择客机镜像、使用镜像站、导入本地 qcow2，并清理缓存。
weight: 50
icon: fa-solid fa-boxes-stacked
---

> [!NOTE]
> **Unreleased**：下文关于本地仓库路径放宽与镜像导入按内容摘要缓存的变更需要包含源码提交 `27f17bb` 的构建，Barn 0.9.2 尚未包含这些行为。详见[未发布变更](/zh/docs/about/unreleased/)。

本指南介绍 **Barn 0.9.2** 下 Linux 客机镜像的选择、镜像站切换、静态仓库构建与本地缓存清理。

使用默认配置时，`barn up` 会自动按宿主架构解析 `u24:stable` 并按需下载经过校验的不可变 `qcow2` 镜像，无需提前手动拉取。Barn 初始使用二进制内置的镜像目录；执行 `barn update` 可从远端仓库获取、校验并激活最新镜像目录（或用 `barn image sync` 从指定 URL 或本地文件加载目录）。

## 选择镜像

查看当前镜像目录中的发行版家族与版本详情：

```bash
barn image list
barn image info u24
barn image info u24:stable
```

Barn 内置 9 个发行版家族：`el7`、`el8`、`el9`、`el10`、`d12`、`d13`、`u22`、`u24` 和 `u26`。直接填写家族名（如 `el9`）默认使用 `stable` 通道，`name:channel` 指定通道，而 `name@version` 则精确锁定某个不可变构建版本。你也可以在 `vm_version` 中填写数字前缀，按点号分隔的版本段自动匹配最新的小版本：

```yaml {title="barn.yml"}
all:
  vars:
    vm_image: el9
    vm_version: "9.7"
```

上例中 `"9.7"` 会匹配活动镜像目录中最新的 `9.7.x` 构建，`"9"` 则匹配最新的 `9.x` 构建（YAML 中的纯数字 `vm_version` 请加双引号以保持字符串类型）。独立设置的 `vm_version` 不能与 `vm_image` 中的 `:channel` 或 `@version` 后缀同时使用。

若需要跨镜像目录更新保持严格可复现，请直接锁定 `barn image info` 显示的完整版本号：

```yaml {title="barn.yml"}
all:
  vars:
    vm_image: d13@20260914.2601.2
```

修改 `vm_image` 或 `vm_version` 后，先运行 `barn plan` 查看变更。已有节点会保留当前根盘，直到显式执行 `barn recreate <node>`；运行 `barn update` 仅影响后续新建或重建的节点。

`barn image list` 会列出所有架构，而 `info` 和 `pull` 默认按宿主架构查询（可通过 `--arch amd64` 或 `--arch arm64` 指定）：

- **`el7`** 仅支持在原生 `linux/amd64` 宿主上运行。
- **Apple Silicon 上的 `el8`（`arm64`）** 会自动启用 QEMU TCG 软件模拟，因为上游 RHEL/Rocky 8 `arm64` 内核要求 64 KiB 页粒度，而 macOS HVF 硬件加速不支持该页大小。跨架构模拟器与固件要求见[运行时排查](../troubleshooting/#原生加速或兼容运行时不可用)。

> [!NOTE]
> `0.9.2` 内置镜像目录中，除仅供兼容旧环境使用的 EOL `el7`、EL9 `9.3` / `9.6` 和 EL10 `10.0` 标记为 `deprecated` 外，其余全部版本均为 `supported`。

## 使用镜像站

发行版默认使用全球镜像源 `https://repo.pigsty.io/barn`。单次命令可通过 `--mirror` 切换至中国官方镜像站（`https://repo.pigsty.cc/barn`），或通过 `--repo` 指定自定义仓库 URL 或本地目录路径：

```bash
barn image pull u24 --mirror
barn up --mirror
barn update --repo https://mirror.example/barn
barn image pull u24 --repo https://mirror.example/barn
barn up --repo https://mirror.example/barn
```

也可以通过环境变量 `BARN_REPO` 为当前 Shell 会话设置默认仓库：

```bash
export BARN_REPO=https://mirror.example/barn
barn update
barn up
```

仓库选择优先级依次为 `--repo` → `--mirror` → `BARN_REPO` → 全球默认源（`https://repo.pigsty.io/barn`）。两个官方仓库以及任何明文 `http://` 仓库都强制要求可信 Minisign 签名（`catalog.json.minisig`）；显式指定的本地目录和自定义 `https://` 仓库则允许使用未签名的 `catalog.json`。所有下载的镜像文件都会严格校验字节大小、SHA-256 摘要与 `qemu-img` 结构完整性。

使用官方仓库下载镜像时，Barn 会自动重试临时网络故障并支持断点续传；若所选官方站点不可达，还会自动回退到另一个官方镜像站。自定义 `--repo` 仓库则不会向外部站点回退。

每个仓库根路径在 `BARN_HOME` 下各自维护独立的活动镜像目录状态。首次将 `--repo` 指向包含自定义镜像的仓库时，请先执行 `barn update --repo <root>` 激活其镜像目录，再运行 `plan` 或 `up`。

## 构建静态仓库

Barn 镜像仓库是一个普通的静态目录，可直接通过本地路径读取、用 `rsync` 同步或由任意静态 HTTP/HTTPS 服务托管：

```filetree {title="/srv/barn"}
barn/
├── repo.yaml                # 人工维护的镜像版本与通道定义
├── catalog.json             # 自动生成的镜像目录（含 SHA-256 与文件尺寸）
├── catalog.json.minisig     # Minisign 签名（官方仓库与 HTTP 仓库必需）
└── images/
    └── d13-1-arm64.qcow2    # 经校验且支持 cloud-init 的 qcow2 基础镜像
```

`repo.yaml` 是唯一需要人工编辑的源文件。对应上方单个 `arm64` 镜像的最小配置如下：

```yaml {title="/srv/barn/repo.yaml"}
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

将准备好的 `qcow2` 镜像放入 `/srv/barn/images/d13-1-arm64.qcow2`（支持相对仓库路径、目录符号链接与共享可写目录），随后在安装了 `qemu-img` 的宿主上生成并校验 `catalog.json`：

```bash
barn repo scan /srv/barn
barn repo build /srv/barn
barn repo verify /srv/barn
```

`barn repo scan` 以只读方式检查目录结构，`barn repo build` 则会运行完整的 `qemu-img check`，将文件名、SHA-256、文件大小和虚拟容量写入 `catalog.json`。每次更新镜像目录内容时都请递增 `revision`；发布到远端服务器时，先上传不可变的 `.qcow2` 镜像文件，最后再更新 `catalog.json` 及其签名。

激活并验证该本地仓库：

```bash
barn update --repo /srv/barn
barn image info d13 --arch arm64 --repo /srv/barn
barn image pull d13 --arch arm64 --repo /srv/barn
```

后续运行 `plan`、`up` 和 `recreate` 时传入 `--repo /srv/barn`（或设置 `export BARN_REPO=/srv/barn`），并在清单中配置 `vm_image: d13@1`。如需将该仓库恢复为二进制内置目录（同时保留防回滚版本号记录），可执行 `barn image reset --repo /srv/barn`。

## 导入本地镜像与清理缓存

如果只需在宿主原生架构下使用单个自定义 `qcow2` 镜像，无需搭建静态仓库，可直接将其作为 `local-*` 别名导入本地缓存：

```bash
barn image import --name local-mybase --boot uefi \
  --source-user ubuntu --sha256 <digest> /path/to/base.qcow2
```

注册别名时需同时指定 `--name`（必须以 `local-` 开头）、`--boot`（`uefi` 或 `bios`）和 `--source-user`；省略这组参数则仅校验镜像并按内容摘要缓存。导入的镜像必须已预装并启用 cloud-init。命名别名一旦注册即不可变——重新制作镜像后请注册新的 `local-*` 名称，并在 `barn.yml` 中通过 `vm_image: local-mybase` 引用。

清理未被使用的缓存镜像与中断下载暂存文件：

```bash
barn image prune --dry-run
barn image prune --yes
```

`barn image prune`（依赖本机 `qemu-img`）会自动保护当前所选仓库活动镜像目录中的全部镜像、已有节点正在使用的基础镜像以及所有已注册的 `local-*` 别名。

签名信任链、防回滚机制、缓存目录结构及架构兼容规则详见[镜像参考](../../reference/images/)；从上游云镜像制作候选镜像并执行发布前验收的完整流程详见[镜像流水线](../../reference/image-pipeline/)。
