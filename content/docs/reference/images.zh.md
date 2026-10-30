---
title: 镜像
description: 签名镜像目录、内置别名、仓库选择、本地缓存校验、导入与清理。
weight: 30
icon: fa-solid fa-compact-disc
---

> [!NOTE]
> **Unreleased**：下文关于本地仓库路径、镜像导入命名、镜像大小及本地别名数量的变更需要包含源码提交 `27f17bb` 的构建，Barn 0.9.2 尚未包含这些行为。详见[未发布变更](/zh/docs/about/unreleased/)。

Barn 通过静态镜像目录与不可变 `qcow2` 产物解析 Linux 客机镜像。官方仓库与 HTTP 仓库必须提供 Ed25519/minisign 目录签名，用户显式指定的本地目录仓库与 HTTPS 仓库则允许不签名。日常可通过 `barn update` 激活新版镜像目录而无需升级 `barn` 二进制；受信任的签名公钥与 `qcow2` 安全检查规则则由二进制本身固定。

> [!WARNING]
> `el7`、`el9`（`9.3` / `9.6`）与 `el10`（`10.0`）属于 `deprecated`（已弃用）兼容镜像；其余内置目录版本均为 `supported`。

## 别名与拉取顺序

Barn `0.9.2` 内置镜像目录 `2026093001`，涵盖 9 个发行版系列、共 41 个镜像产物（除 `el7` 仅提供 `amd64` 外，其余系列均同时提供 `amd64` 与 `arm64`；其中 `el9` 包含 `9.3`、`9.6`、`9.7`、`9.8`，`el10` 包含 `10.0`、`10.1`、`10.2`）。缺省请求为宿主原生架构的 `u24:stable`（Ubuntu 24.04 LTS）。

下表列出内置镜像目录 `2026093001` 中各系列的 `stable` 版本快照。运行 `barn update` 后再执行 `barn image list` 可查看所选仓库当前的实时目录；宿主平台兼容性详见[平台与限制](../../about/status/)。

| 镜像系列 | 内置 `stable` | 可用别名 |
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
{.wide}

发行版说明：

- `u22`、`u24`、`u26` 分别对应 Ubuntu 22.04、24.04、26.04 LTS，直接采用 Canonical 官方原始云镜像，并在首次启动时由 `cloud-init` 完成账号与网络配置。
- `d12` 与 `d13` 预装了离线 XFS 工具集并预生成 `en_US.UTF-8` 区域设置，默认区域设置保持为 `C.UTF-8`。
- `el7` 为 CentOS Linux 7.9（`amd64` BIOS），`el8`、`el9`、`el10` 为 Rocky Linux（`amd64` 与 `arm64` UEFI）。
- 运行 `barn update` 只会更新新节点的 `:stable` 或版本前缀解析结果，已运行的虚拟机和显式锁定 `@version` 的节点继续使用原有基础镜像。若现有清单使用的通道或版本前缀在新目录中指向了新版本，后续执行 `barn plan` 或 `barn up` 会报告镜像漂移，需显式运行 `barn recreate` 才会替换节点。

| 别名 | 发行版 | 架构 | 引导方式 | 状态 |
|---|---|---|---:|---|
| `el7` | CentOS Linux 7.9 / 2211 | `amd64` | BIOS | `deprecated` |
| `el8` | Rocky Linux 8.10 | `amd64`、`arm64` | UEFI | `supported` |
| `el9` | Rocky Linux 9.7 / 9.8 | `amd64`、`arm64` | UEFI | `supported` |
| `el9` | Rocky Linux 9.3 / 9.6 | `amd64`、`arm64` | UEFI | `deprecated` |
| `el10` | Rocky Linux 10.1 / 10.2 | `amd64`、`arm64` | UEFI | `supported` |
| `el10` | Rocky Linux 10.0 | `amd64`、`arm64` | UEFI | `deprecated` |
| `d12`、`d13` | Debian 12 / 13 | `amd64`、`arm64` | UEFI | `supported` |
| `u22`、`u24`、`u26` | Ubuntu 22.04 / 24.04 / 26.04 LTS | `amd64`、`arm64` | UEFI | `supported` |
{.wide}

```bash
barn image list
barn image info d13
barn image info d13:stable
barn image info el9@9.7
barn image pull d13@20260914.2601.2
barn image pull d13 --arch arm64
barn update
```

`barn image list` 会列出当前激活目录中的全部版本、架构以及已注册的 `local-*` 本地别名。`barn image info` 与 `image pull` 一样默认采用本机架构；未缓存时无需安装 QEMU 即可查看目录元数据，已缓存时则会调用 `qemu-img` 校验本地缓存文件。`list` 与 `info` 都不会发起镜像下载。

目录中的 `status` 字段标识支持等级（`supported`、`testing`、`deprecated` 或 `unknown`）；非 `supported` 状态的镜像依然可以正常启动，并会在输出中附带状态警告。

拉取镜像时，Barn 依次执行以下四步：

1. **读取本地活动目录** — 为本次命令加载一次所选仓库的本地活动镜像目录（即二进制内置目录，或最近一次通过 `barn update` / `barn image sync` 为该仓库激活的目录）。
2. **解析选择器与架构** — 解析 `image[:channel]` 或 `image@version-prefix`（官方目录缺省为 `u24:stable`）及目标架构（独立执行 `image pull` 时默认取本机架构并支持 `--arch` 覆盖；生命周期命令遵循 `vm_arch`）。
3. **校验本地缓存** — 若本地已存在对应缓存文件，且文件大小、SHA-256 摘要与 `qemu-img` 结构检查全部通过，则直接复用。
4. **断点续传与落盘校验** — 若未命中缓存，则从所选仓库下载对应产物（支持自动重试与断点续传），待文件大小、SHA-256 与 `qcow2` 格式全部校验通过后移入缓存。两个官方源（`https://repo.pigsty.io/barn` 与 `https://repo.pigsty.cc/barn`）在下载镜像文件时支持自动互备回退，自定义 `--repo` 仓库则严格只从指定源下载；目录中记录的上游 URL 仅用于构建溯源。
{.steps}

仓库选择优先级依次为 `--repo` → `--mirror`（`https://repo.pigsty.cc/barn`）→ `BARN_REPO` → 编译期默认源（`https://repo.pigsty.io/barn`）。两个官方仓库均要求有效的 minisign 镜像目录签名。

由于每个仓库根路径在 `$BARN_HOME/images/manifests/` 下独立维护各自的活动目录记录，使用自定义仓库时请始终传入相同的 `--repo`（或设置 `BARN_REPO`）；首次切换到带有自定义别名的新仓库时，请先执行 `barn update --repo <root>` 激活其目录。只要本地已具备激活目录与通过校验的缓存镜像，日常命令即可完全离线运行。

Barn 会自动将通过校验的缓存镜像恢复为只读权限（`0444`）。如果未被虚拟机引用的缓存文件校验失败，Barn 会先将其重命名为 `.corrupt-<timestamp>` 留存，再重新下载；若该基础镜像仍被现有虚拟机引用，则保持原文件不动并直接报错。

## 运行时策略

当客机架构与宿主架构一致时，Barn 默认启用硬件加速虚拟化（macOS 使用 Apple HVF，Linux 使用 KVM），仅有一项内置例外：Rocky Linux 8（`el8`）的 `arm64` 原生内核使用 64 KiB 内存页，而 Apple HVF 不支持 64 KiB 页大小，因此 Apple Silicon 宿主运行 `el8` 时会自动切换为同架构 QEMU TCG 并在状态输出中标注 `tcg`。跨架构客机（`vm_arch` 与宿主不同）同样使用 TCG；在 `arm64` 宿主上模拟 `amd64` 客机时，Barn 会将 TCG 固定为单翻译线程以保证 x86 内存序正确。

`el7` 仅支持在 `linux/amd64` 宿主上原生运行。Linux 宿主的 `barn setup` 默认只安装本机架构的 QEMU；在通过 `up` 或 `recreate` 启动跨架构客机前，请先安装对应架构的 `qemu-system-*` 模拟器与 UEFI 固件（`barn plan` 无需安装这些工具即可解析目录镜像，但解析 `local-*` 导入镜像仍需 `qemu-img`）。

```bash
barn image pull d13 --mirror
barn image pull d13 --repo https://mirror.example/barn
BARN_REPO=/absolute/local/repository barn up
```

## 信任与校验

正式发布构建内置了两把生产环境 Ed25519 校验公钥（签名私钥保存在源码仓库之外）。激活镜像目录时，Barn 会拒绝未知签名密钥、格式错误的 JSON、同一修订号下字节不同的内容，以及低于该仓库历史最高已接受修订号的目录（除非在 `barn image sync` 时显式传入 `--allow-downgrade`）。

所有缓存或导入的镜像都必须是文件大小与 SHA-256 严格匹配的独立 `qcow2` 文件，不得包含后端依赖链（backing file）、外部数据文件、加密或未知的不兼容特性位。通过校验后，Barn 将基础镜像设为只读，并为每个虚拟机节点创建独立的写时复制（CoW）overlay 根盘。

```bash
barn update
barn image sync --repo https://repo.example/barn \
  https://repo.example/barn/catalog.json
barn image sync --repo /srv/barn --allow-downgrade /srv/barn/catalog.json
barn image reset --repo /srv/barn
```

- **`barn update`**：从 `--repo` 或 `--mirror` 拉取、验签并激活最新镜像目录。
- **`barn image sync`**：从显式指定的 URL 或本地文件路径恢复镜像目录（对于未签名的自定义仓库，源路径必须指向该仓库根目录下的 `catalog.json`），支持 `--allow-downgrade` 显式降级。
- **`barn image reset`**：将 `--repo`（或默认仓库）的活动目录重置回二进制内置版本，同时保留防回滚所需的历史最高修订号水位线。

## 静态仓库格式

静态 Barn 镜像仓库的目录结构如下：

```filetree {title="/srv/barn"}
repo.yaml # 人工维护的策略与版本声明文件（schema 1）
catalog.json # 自动生成的运行时镜像目录，含摘要与大小（schema 3）
catalog.json.minisig # Minisign 签名文件（官方仓库与 HTTP 仓库必需）
images/
  <image>-<version>-<arch>.qcow2 # 不可变 qcow2 镜像产物
```

`repo.yaml`（`schema: 1`）负责声明默认配置、别名、通道、精确版本、架构、引导方式、支持状态、`source_user`（如上游镜像的 `rocky` 或经 Barn 官方归一化后的 `dba`）以及可选的上游溯源 URL，无需手写校验和与文件大小。`barn repo build` 会检查 `images/` 下的 `qcow2` 文件，并自动生成包含文件名、SHA-256、文件大小与虚拟容量的 `catalog.json`（`schema: 3`）。

```yaml {title="repo.yaml"}
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

未在变体下显式指定 `file` 时，默认对应 `images/<image>-<version>-<arch>.qcow2`（例如 `images/u24-1-amd64.qcow2` 与 `images/u24-1-arm64.qcow2`）。

静态仓库构建与校验规则（`barn repo scan|build|verify /absolute/repo`）：

- 仓库根目录接受相对路径、`~/` 与目录符号链接，根目录和 `images/` 可以共享可写。`repo.yaml` 可为指向不超过 4 MiB 非空普通文件的符号链接。镜像条目仍须为普通文件，输出 `catalog.json` 的符号链接不会被覆盖。
- 引导方式按 `variant` → `family` → `defaults.boot` 继承；状态按 `variant` → `version` → `unknown` 继承。每个系列都必须定义指向已有精确版本的默认通道；系列名与别名全局唯一且不能以 `local-` 开头。由于[清单别名归一化](../configuration/#vm-变量)会先查二进制内置目录，请勿将 `ubuntu`、`debian`、`rocky` 等内置别名改指其他系列。
- 通道与按点号分段的数值前缀（如 `el9@9.7`、`el9@9`）会解析为精确版本或匹配的最高版本，最终落定为不可变的三元组标识 `(image, exact version, arch)`：
  ```text
  d13:stable + native
    -> d13@20260914.2601.2 + arm64
    -> images/d13-20260914.2601.2-arm64.qcow2
  ```
- **`barn repo scan`** 为只读检查，不依赖 `qemu-img`；即使存在 `missing`（缺失）或 `unsafe`（命名/类型不安全）的文件也会返回退出码 `0`，自动化脚本需检查输出中的 `missing` 与 `unsafe` 数组是否为空。
- **`barn repo build`** 与 **`barn repo verify`** 依赖本机 `qemu-img`。`build` 校验 `repo.yaml` 并完整检查每个 `qcow2` 文件后原子替换 `catalog.json`（存在 `missing` 或 `unsafe` 文件时拒绝构建，`untracked` 未声明文件则仅报告而不写入目录）；`verify` 要求现有 `catalog.json` 与重新生成的结果逐字节一致。每次修改目录内容都必须递增 `revision`，发布时先上传不可变的 `.qcow2` 文件，最后同步更新 `catalog.json` 与 `catalog.json.minisig`。

<span id="local-image-import"></span>

## 本地布局与导入

Barn 将目录记录、下载缓存与本地导入文件统一存放在 `$BARN_HOME/images`（默认 `~/.barn/images`）：

```filetree {title="$BARN_HOME/images"}
manifests/ # 各仓库独立的活动 catalog.json 与历史最高修订号记录
local-images.json # 已注册的 local-* 本地镜像别名索引
local/
  <sha256>.qcow2 # 按内容摘要索引的本地导入 qcow2 镜像
d13/
  d13-20260914.2601.2-arm64.qcow2 # 按系列分目录存放的只读缓存镜像
u24/
  u24-20260926.0.0-arm64.qcow2
```

将本地 `qcow2` 文件导入缓存，或注册为 `local-*` 命名镜像：

```bash
barn image import --sha256 <digest> /path/to/base.qcow2
barn image import --name local-mybase --boot uefi \
  --source-user ubuntu --sha256 <digest> /path/to/base.qcow2
```

本地导入规则：

- `image import` 接受相对路径、`~/` 和普通文件的符号链接，仍需 `qemu-img`。本地镜像及目录中声明了大小的镜像不再受 8 GiB 文件大小上限约束；读取以实际或声明大小为界，下载超出声明大小时停止。未声明产物大小的旧协议下载仍保留 8 GiB 边界。可选 `--sha256` 继续核对预期摘要。
- `image import` 仅复制并校验 `qcow2` 文件结构，不会清理凭据、安装 `cloud-init` 或测试启动。
- 源文件名可包含空格或 Unicode，无需特定扩展名；Barn 校验实际 qcow2 内容。新导入使用 `local/<sha256>.qcow2`，同名不同内容可并存，相同内容复用缓存。重新导入已有别名时保留其原有缓存路径。原有的 256 个别名上限已移除；注册表元数据若超过 1 MiB，会在写入前报错并保留已有别名。
- 命名导入（`--name local-<alias>`）必须同时指定 `--boot bios|uefi` 与 `--source-user <user>`，并固定绑定当前宿主的原生架构（跨架构镜像请通过静态仓库管理）。别名一旦注册不可更改，可在 `barn.yml` 中通过 `vm_image: local-mybase` 引用；不带 `--name` 的导入则仅用于预填充缓存。

## 清理

```bash
barn image prune --dry-run
barn image prune --yes
```

`barn image prune`（或 `barn image prune --dry-run`）只列出可回收的候选文件，传入 `--yes` 才会实际删除。

`prune` 会自动保护当前所选仓库活动目录中的全部镜像、已应用节点正在引用的镜像摘要以及已注册的 `local-*` 别名（因此执行 `destroy` 或 `purge` 后基础镜像缓存依然保留）。只有不再受当前目录、节点或本地别名保护的旧镜像及过期暂存文件才会成为清理候选；已隔离的 `.corrupt-*` 文件会原样保留供排查，未知或不安全的文件则会触发报错。由于 `prune --yes` 按顺序逐个删除候选文件且在中途出错时不会回滚已删除的文件，清理前请先运行 `--dry-run` 确认列表（检查自定义仓库时请附上相同的 `--repo`）。

如需在初始化镜像站时逐字节导出二进制内置的 Schema-3 镜像目录，可在源码仓库下运行 `go run ./tools/catalogexport /absolute/new/catalog.json`；任何使用内置修订号发布的公开目录都必须与导出的字节完全一致。
