---
title: 镜像流水线
description: 不下载、不上传、不签名地校验或离线归一化显式 qcow2 候选镜像。
weight: 40
icon: fa-solid fa-diagram-project
---

在 Barn 源码仓库下使用 `packaging/image-pipeline/build.sh`，可对照已知的 SHA-256 摘要校验或离线归一化已下载的 `qcow2` 候选镜像。该工具全程在本地运行，不联网、不读取签名密钥、也不修改 Barn 运行时与网络状态，输出状态为 `testing` 的候选产物包，供后续真机冒烟测试与发布审核使用。

构建宿主环境要求：

- **依赖工具**：所有模式均需 Python 3 与 `qemu-img`；`offline` 模式还需安装可用的 `libguestfs` 工具（`virt-customize` 与 `virt-cat`）。可通过 `--qemu-img`、`--virt-customize`、`--virt-cat` 参数或 `QEMU_IMG`、`VIRT_CUSTOMIZE`、`VIRT_CAT` 环境变量指定工具路径。
- **工作树外存储**：请将源镜像、RPM/DEB 软件包缓存和输出目录放在 Git 工作树之外（源码仓库只跟踪构建配方与锁定清单）。
- **架构匹配**：`--arch` 用于记录候选镜像的目标架构元数据；执行 `offline` 定制时，构建宿主上的 `libguestfs` 必须能够运行目标客机架构。

## 模式与处理方案

- **`validate`（校验模式）**：复制源镜像并重算哈希，调用 `qemu-img check` 强制检查单文件 `qcow2` 结构，不修改客机文件与凭据，直接生成证据产物包。
- **`offline`（离线归一化模式）**：在暂存副本上运行 `virt-customize --no-network` 与 `virt-cat`：确认 UID/GID `88` 未被其他账号占用后，配置固定的 `dba`/`admin` 管理身份，禁用 SSH 密码登录与 root 登录，清理残留密钥、命令历史、机器标识与 `cloud-init` 缓存，恢复 SELinux 标签，并读回客机内的确定性标记以验证定制结果。

`build.sh` 默认使用 `--profile base`。各处理方案（profile）的作用范围如下：

| 处理方案 | 归一化操作 | 软件包输入 |
|---|---|---|
| `base` | 仅执行账号、sudo、SSH 与 cloud-init 身份归一化 | 无（拒绝传入软件包参数） |
| `el8` | 基础归一化 + 安装 Python 3、加载 SSH 配置片段、清理旧网络配置、配置 `chronyd` 与恢复 SELinux 标签 | 锁定的 RPM 依赖包集合 |
| `el9` | 基础归一化 + 清理旧网络配置与恢复 SELinux 标签 | 无（拒绝传入软件包参数） |
| `d12`、`d13` | 基础归一化 + 离线安装 XFS 用户态工具并生成 `en_US.UTF-8` / `C.UTF-8` 区域设置 | 锁定的 DEB 依赖包集合 |
{.wide}

`validate` 模式仅支持 `--profile base`。在 `offline` 模式下使用 `el8`、`d12` 或 `d13` 时，必须同时传入与方案及架构匹配的 `--package-lock` 和 `--package-cache`。构建官方镜像时，直接使用下方的 `build-official.py` 封装脚本即可自动传入锁定的软件包集合。

## 官方候选镜像矩阵

`packaging/image-pipeline/build-official.py` 封装了八个官方离线归一化目标——Debian 12/13（`d12`、`d13`）与 Rocky Linux 8/9（`el8`、`el9`）各自的 `amd64` 与 `arm64` 变体，所有上游 `qcow2` URL、RPM/DEB 依赖包、发布版本号、SHA-256 摘要与 `SOURCE_DATE_EPOCH` 均锁定在 `official-v1.json` 中（Ubuntu 直接使用固定日期的官方原始云镜像，不经过此离线定制矩阵）。

```bash
./packaging/image-pipeline/build-official.py --list

./packaging/image-pipeline/build-official.py \
  --source-cache /absolute/source-cache \
  --package-cache /absolute/package-cache \
  --output /absolute/existing-output-root \
  --target d13/arm64 --fetch
```

使用说明：

- 运行前请预先创建好 `--source-cache`、`--package-cache` 与 `--output` 目录，并传入规范化的绝对路径。加上 `--fetch` 时，脚本会从锁定的 HTTPS URL 下载缺失输入并在调用 `virt-customize --no-network` 前校验 SHA-256；不加 `--fetch` 时，所有锁定输入必须已存在于两个缓存目录中。
- 省略 `--target` 会构建全部八个目标，重复指定 `--target` 可构建指定子集。`--list` 会列出当前源码锁定的精确版本（当前为 Debian `20260923.2610.1` / `20260914.2601.2` 与 Rocky Linux `8.10.20240528.3` / `9.8.20260525.2`）。

八个目标全部构建完成后，将**包含各产物包目录的父目录**传给 `--assemble-from`（若分散在多个父目录可重复传入 `--assemble-from`），即可组装出静态候选仓库：

```bash
./packaging/image-pipeline/build-official.py \
  --assemble-from /absolute/existing-output-root \
  --output /absolute/new-candidate-repository
```

组装操作要求八个目标各有且仅有一个产物包，输出目标路径 `--output` 必须尚不存在，并会调用 `PATH` 中的 `barn`（或 `--barn /absolute/path/to/barn`）执行 `barn repo build` 与 `barn repo verify`。生成的候选仓库默认使用 `candidate` 通道（例如 `d13:candidate`）和 `testing` 状态，便于在提升为 `stable` / `supported` 之前执行真机冒烟测试。

## 校验单个已下载镜像

```bash
SOURCE_DATE_EPOCH=1787486400

./packaging/image-pipeline/build.sh \
  --mode validate \
  --source /absolute/source.qcow2 \
  --expected-sha256 <digest> \
  --output /absolute/new/evidence-directory \
  --name u24 --release 20260801.0.0 --arch amd64 \
  --source-user ubuntu --boot uefi \
  --source-uri https://immutable.example/source.qcow2 \
  --artifact-url 'https://images.example/u24/{sha256}.qcow2' \
  --license NOASSERTION \
  --source-date-epoch "$SOURCE_DATE_EPOCH" \
  --manifest-version 2026082903
```

路径与容量限制：

- `--source` 必须是规范化绝对路径的普通文件（非符号链接），大小不超过 16 GiB；`--output` 的父目录必须已存在，而目标目录本身必须尚不存在。
- Barn `0.9.2` 的运行时镜像产物上限为 8 GiB。2026-10-30 [尚未发布的源码变更](../../about/unreleased/#limits)已移除本地镜像及目录中声明了大小的镜像的这一上限；使用更大产物时需要对应源码版本。流水线本身仍遵循构建配方的大小边界。
- 构建器会在输出路径旁创建排他锁，在权限 `0700` 的临时目录中完成暂存，最后通过原子重命名发布到 `--output`（失败时仅清理本次构建的暂存目录）。

每个成功生成的产物包包含以下文件：

| 文件 | 用途 |
|---|---|
| `<name>-<release>-<arch>-<digest-prefix>.qcow2` | 通过校验的只读候选 `qcow2` 镜像文件 |
| `build-recipe.json` | 构建调用参数、工具版本与输入摘要记录 |
| `manifest-candidate.json` | 未签名的候选镜像元数据（`status: "testing"`） |
| `provenance.intoto.json` | SLSA 构建来源声明 |
| `sbom.spdx.json` | 覆盖流水线声明输入与注入软件包的 SPDX 物料清单 |
| `validation.json` | 处理前后的 `qcow2` 检查结果、客机标记校验与待完成的发布门禁项 |
| `checksums.txt` | 产物包内所有文件的 SHA-256 校验和 |
| `package-lock.json` | 使用锁定 RPM/DEB 软件包输入时附带的锁定清单 |
{.wide}

在输入文件与工具版本固定时，`validate` 模式可逐字节复现；使用 `offline` 模式准备发布证据时，请对同一候选镜像构建两次并比对结果。将候选镜像正式发布为 `supported` 状态时，还需在目标宿主与客机组合上完成真机启动测试、在 `repo.yaml` 中递增 `revision` 并更新状态、运行 `barn repo build` 与 `barn repo verify`、使用生产密钥签发 `catalog.json.minisig` 并验证公开仓库端点。
