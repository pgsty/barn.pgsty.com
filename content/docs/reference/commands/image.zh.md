---
title: 镜像命令
description: 更新签名目录、查看和下载镜像、导入本地文件以及清理缓存。
weight: 40
date: 2026-11-11
---

更新签名目录、查看和下载镜像、导入本地文件以及清理缓存。

本参考对应 **Barn 1.2.0**；选项表区分 **1.1.0 已有选项** 与 **1.2.0 新增选项**，具体范围见[版本基线](/zh/docs/reference/commands/#versions)。所有命令继承[全局选项](/zh/docs/reference/commands/#global-options)。

官方仓库和 HTTP 源必须提供受信任的分离签名。显式选择的自定义 HTTPS 仓库或本地目录可以不签名，但来源必须恰好是该仓库的 `catalog.json`；只要提供了签名，就必须验签成功。详见[目录信任规则](../../images/#trust-and-verification)。

## `barn update` {#barn-update}

```text
barn update [flags]
```

从所选仓库取得 `catalog.json`，并按仓库策略获取所需签名，通过信任与 revision 检查后原子激活。普通命令只使用本地元数据，不隐式刷新。本命令更新镜像元数据，不升级 Barn 可执行文件。仓库选择顺序为 `--repo` > `--mirror` > `BARN_REPO` > 全球官方源，详见[仓库选择与信任](../../images/#runtime-policy)。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `--mirror` | 使用中国官方源 `https://repo.pigsty.cc/barn`；显式 `--repo` 优先 | 1.1.0 |
| `-r, --repo string` | 镜像仓库 URL 或本地目录，优先于 `BARN_REPO`；支持 `--mirror` 的命令中也优先于该选项 | 1.1.0 |
{.wide .expand}

```bash
barn update
barn update --mirror
barn --json update --repo /srv/barn
```

## `barn image list` {#barn-image-list}

```text
barn image list [flags]
```

列出目录中的所有架构和已注册本地镜像，不接受镜像位置参数或架构过滤选项。读取本地活动目录，需要刷新时显式运行 `barn update`。`barn images`、`barn im` 都是镜像命令组的别名。

别名：`ls`。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-r, --repo string` | 镜像仓库 URL 或本地目录，优先于 `BARN_REPO`；支持 `--mirror` 的命令中也优先于该选项 | 1.1.0 |
{.wide .expand}

```bash
barn image list
barn --json image list
barn image list --repo /srv/barn
```

## `barn image info` {#barn-image-info}

```text
barn image info [image[:channel]|image@version-prefix] [flags]
```

查看单个镜像的元数据与已验证缓存状态，省略镜像参数时使用目录默认值。可传家族名 `u24`、通道 `u24:stable` 或数字版本前缀 `el9@9`，架构默认原生。`--architecture/-a` 是 `--arch/-A` 的兼容写法，不下载镜像制品。别名与精确内置版本见 [Linux 镜像](../../images/)。

别名：`in`。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-A, --arch string` | 客机架构：`native`、`amd64`、`arm64`；也接受 `x86_64`、`x64`、`aarch64`、`a64` | 1.1.0 |
| `-r, --repo string` | 镜像仓库 URL 或本地目录，优先于 `BARN_REPO`；支持 `--mirror` 的命令中也优先于该选项 | 1.1.0 |
{.wide .expand}

```bash
barn image info
barn image info u24 -A arm64
barn --json image info el9@9
```

## `barn image pull` {#barn-image-pull}

```text
barn image pull [image[:channel]|image@version-prefix] [flags]
```

下载所选制品，核验 SHA-256、字节大小、qcow2 结构和虚拟容量后激活缓存。省略镜像和架构时使用目录默认镜像与宿主原生架构，已有有效缓存可以复用。目录中的 upstream URL 记录来源，不作为下载失败时的备用地址。仍支持兼容写法 `--architecture/-a`；下载异架构镜像不会安装对应 QEMU 模拟器。

别名：`p`。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-A, --arch string` | 客机架构：`native`、`amd64`、`arm64`；也接受 `x86_64`、`x64`、`aarch64`、`a64` | 1.1.0 |
| `--mirror` | 使用中国官方源 `https://repo.pigsty.cc/barn`；显式 `--repo` 优先 | 1.1.0 |
| `-r, --repo string` | 镜像仓库 URL 或本地目录，优先于 `BARN_REPO`；支持 `--mirror` 的命令中也优先于该选项 | 1.1.0 |
{.wide .expand}

```bash
barn image pull
barn image pull u24 --mirror
barn image pull d13 -A amd64 --repo /srv/barn
```

## `barn image import` {#barn-image-import}

```text
barn image import <path> [flags]
```

将本地普通 qcow2 文件复制到私有缓存并校验容器，可选核对预期摘要。接受相对路径、`~/` 与指向普通文件的符号链接，需要 `qemu-img`；导入不启动镜像、不安装 cloud-init，也不修改登录凭据。

指定 `local-*` 名称可注册不可变的清单引用，必须同时给出启动模式与源镜像登录用户。具名导入可用 `-A` 记录异架构，qcow2 元数据本身无法识别 CPU 架构；无名称导入不能使用 `-A`。使用时设置 `vm_image` 及匹配的 `vm_arch`。详见[导入与缓存规则](../../images/#local-image-import)。

别名：`i`。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-A, --arch string` | 与 `--name` 一起记录客机架构，默认 `native`；不会转换镜像架构 | 1.1.0 |
| `-b, --boot string` | 具名导入必填：`bios` 或 `uefi` | 1.1.0 |
| `--name string` | 不可变的 `local-*` 别名，必须同时指定 `--boot` 与 `--source-user` | 1.1.0 |
| `-s, --sha256 string` | 可选的预期 SHA-256；不匹配时导入失败 | 1.1.0 |
| `-u, --source-user string` | 具名导入必填：源镜像的登录用户 | 1.1.0 |
{.wide .expand}

```bash
barn image import ./base.qcow2
barn image import ./base.qcow2 --name local-dev --boot uefi --source-user ubuntu -A arm64
```

## `barn image sync` {#barn-image-sync}

```text
barn image sync <url|path> [flags]
```

从精确 URL 或本地文件激活目录，按上面的信任规则读取旁边的 `.minisig` 签名，适用于恢复或导入；正常刷新已配置仓库应使用 `update`。`--repo` 指定替换哪个仓库的活动元数据。无签名自定义源必须恰好是 `<repo>/catalog.json`，任意位置的恢复文件则需要受信任签名。

旧 revision 需要 `--allow-downgrade`；对于允许无签名目录的自定义仓库，从曾签名的目录切换到无签名目录也需要此选项。它不会接受无效签名，也不绕过官方仓库的签名要求和 revision 内容检查。后续回退保护仍记住历史最高 revision。

别名：`sy`。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `--allow-downgrade` | 允许激活比历史最高 revision 更旧的签名目录 | 1.1.0 |
| `-r, --repo string` | 要替换活动目录的仓库 | 1.1.0 |
{.wide .expand}

```bash
barn image sync /srv/barn/catalog.json
barn image sync --repo /srv/barn /srv/recovery/catalog.json
barn image sync --allow-downgrade /srv/recovery/catalog.json
```

## `barn image reset` {#barn-image-reset}

```text
barn image reset [flags]
```

为所选仓库重新激活当前二进制内置的镜像目录，保留回退保护使用的历史最高 revision。镜像缓存与 VM 磁盘保留；需要清理缓存时使用 `image prune`。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-r, --repo string` | 要恢复为内置目录的仓库 | 1.1.0 |
{.wide .expand}

```bash
barn image reset
barn --json image reset --repo /srv/barn
```

## `barn image prune` {#barn-image-prune}

```text
barn image prune [flags]
```

默认列出可回收缓存文件，`--yes` 才删除候选文件，与 `--dry-run` 互斥。所选仓库的活动目录、已应用节点的基础镜像摘要和本地别名注册表会保护所引用的文件；可识别的过期暂存文件也可清理，隔离的 `.corrupt-*` 文件保留。

预览和删除时应使用相同的仓库选择。删除按顺序执行，后续文件发生错误不会恢复已经删除的文件。详见[清理规则](../../images/#pruning)。

别名：`pr`。

| 选项 | 含义 / 默认值 | 可用版本 |
|---|---|---|
| `-d, --dry-run` | 仅预览计划，不修改状态 | 1.1.0 |
| `-r, --repo string` | 镜像仓库 URL 或本地目录，优先于 `BARN_REPO`；支持 `--mirror` 的命令中也优先于该选项 | 1.1.0 |
| `-y, --yes` | 删除列出的无引用文件；不能与 `--dry-run` 同时使用 | 1.1.0 |
{.wide .expand}

```bash
barn image prune --dry-run
barn image prune --repo /srv/barn --dry-run
barn image prune --repo /srv/barn --yes
```

## 实现依据 {#implementation}

[command_image.go](https://github.com/pgsty/barn/blob/v1.2.0/cmd/barn/command_image.go) · [images.go](https://github.com/pgsty/barn/blob/v1.2.0/cmd/barn/images.go)

发布源码与相对 1.1.0 的变化见[版本基线](/zh/docs/reference/commands/#versions)。
