---
title: 镜像流水线
description: 不下载、不上传、不签名地校验或离线归一化显式 qcow2 候选镜像。
weight: 40
icon: fa-solid fa-shield-halved
---

使用 `packaging/image-pipeline/build.sh` 校验或规范化一个已下载的不可变 qcow2 文件，并提供独立获得的 SHA-256。
该底层工具只在本地处理文件，不下载、上传、读取签名密钥或修改 Barn 运行时及网络状态。
输出仍是候选镜像，不会标为 `supported`。

在 Barn 源码目录执行以下命令。需要 Python 3 与 `qemu-img`。
`offline` 还需要可用的 libguestfs `virt-customize`、`virt-cat`。
这些是镜像构建宿主的依赖，不属于 `barn setup` 为运行虚拟机安装的依赖。
请将源镜像、软件包缓存与输出产物放在 Git 工作树之外。
仓库保存配方与锁定清单，不保存下载或生成的镜像。
`--arch` 只声明候选镜像架构，不会转换镜像，也不检查构建宿主上的 libguestfs 能否执行该架构的客机。

## 模式

- `validate`：复制镜像并重新计算哈希，强制执行 qcow2 检查，校验仅含一个镜像的后端链。
  它运行 `qemu-img check`，输出用于审核、未经发布验证的产物包，不修改客机凭据。
- `offline`：额外在暂存副本上使用 libguestfs `virt-customize --no-network` 与 `virt-cat`。
  如果其他用户或组占用了 UID/GID 88，它会拒绝继续；否则按固定规则配置 `dba`/`admin` 身份，并禁用 SSH 的密码认证和 root 登录。
  它还会清理密钥、历史、主机身份和 cloud-init 缓存，恢复指定的 SELinux 标签，再读取写入客机的固定标记以确认处理结果。

底层构建器默认使用 `--profile base`。各处理方案（profile）的作用范围如下：

| 处理方案 | 额外处理 | 软件包输入 |
|---|---|---|
| `base` | 只归一化身份与凭据 | 无；拒绝软件包参数 |
| `el8` | Python 3、SSH 配置片段加载、旧网络清理、chrony 和 SELinux 处理 | 锁定的 RPM 依赖集合 |
| `el9` | 旧网络清理与身份归一化 | 无；拒绝软件包参数 |
| `d12`、`d13` | XFS 工具与区域设置校验 | 锁定的 DEB 依赖集合 |

`validate` 只接受 `base`。
`offline` 配合 `el8`、`d12`、`d13` 时，必须同时提供 `--package-lock` 和 `--package-cache`。
JSON 锁定清单必须符合规定格式，并与处理方案、架构匹配。构建官方镜像时，优先使用下一节封装脚本提供的固定软件包输入。
可通过 `--qemu-img`、`--virt-customize`、`--virt-cat` 指定工具路径。
默认也读取对应的 `QEMU_IMG`、`VIRT_CUSTOMIZE`、`VIRT_CAT` 环境变量。

## 官方候选镜像矩阵

`build-official.py` 沿用相同的离线限制，封装固定的八目标矩阵。
矩阵包含 Debian 12/13 与 Rocky Linux 8/9，各自覆盖 amd64、arm64。
每份上游 qcow2、RPM/DEB 输入、发布版本名称、摘要与源时间戳都锁定在 `official-v1.json`。

```bash
./packaging/image-pipeline/build-official.py --list

./packaging/image-pipeline/build-official.py \
  --source-cache /absolute/source-cache \
  --package-cache /absolute/package-cache \
  --output /absolute/existing-output-root \
  --target d13/arm64 --fetch
```

不加 `--fetch` 时，全部锁定输入必须已在两个规范化缓存目录中。
运行封装脚本前，先创建两个缓存根和构建输出根，并使用规范化绝对路径。
加上 `--fetch` 后，封装脚本也只下载固定 HTTPS URL。
它会在调用离线归一化前拒绝任何摘要不匹配。

Debian 12/13 安装锁定的 XFS 用户态工具及其依赖。
Rocky Linux 8 安装锁定的 `python36` 与 `python3-pip` RPM。
cloud-init 启用 NTP 时，它使用镜像已有的 RHEL chrony 模板与 `chronyd` 服务。
Rocky Linux 9 不需要额外软件包输入。SELinux 标签恢复属于归一化步骤，不需要另一组软件包输入。

Debian 同时生成 `en_US.UTF-8`，并保留 `C.UTF-8` 作为默认区域设置。
客机处理脚本和宿主端标记校验都会检查这两项要求，基础镜像更新后也不例外。
Ubuntu 使用固定日期的官方原始镜像，不经过此离线定制流程。

每份结果仍是未签名的 `testing` 候选镜像。
不传 `--target` 时，脚本构建全部八个目标。重复该参数可以选择多个目标。
`--list` 显示当前源码锁定的精确版本。
目前包含 Debian `20260923.2610.1`/`20260914.2601.2` 与 Rocky Linux `8.10.20240528.3`/`9.8.20260525.2`。

组装参数接受**包含各命名产物包的父目录**，不能直接指定产物包目录。
八个构建都放在同一个输出根下时，执行：

```bash
./packaging/image-pipeline/build-official.py \
  --assemble-from /absolute/existing-output-root \
  --output /absolute/new-candidate-repository
```

构建分散在不同根目录时，可以重复 `--assemble-from`。八个目标都必须各有一个产物包。
组装会创建新的静态仓库，并调用 PATH 中的 `barn` 执行 `repo build` 与 `verify`。
也可用 `--barn /absolute/path/to/barn` 指定程序。
构建模式使用已存在的输出根。组装模式的目标目录必须不存在。
生成仓库使用 `candidate` 通道，而非 `stable`，例如应选 `d13:candidate`。
此过程不包含真机启动测试、签名、上传或镜像目录发布。

## 校验一个已下载镜像

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

源文件与输出必须是绝对路径。
源文件必须使用规范化路径，是普通文件且非符号链接，复制期间保持稳定，大小不超过 16 GiB。
输出路径必须不存在，但父目录必须已存在。

流水线允许最大 16 GiB 的源文件，超过 Barn 0.9.1 的 **8 GiB 运行时/仓库文件上限**。
因此，流水线成功不代表生成的 qcow2 一定能被导入、组装或下载。
请检查结果产物的文件大小，不能只看虚拟容量。
构建器在输出路径旁加排他锁，在权限为 0700 的目录中暂存文件，完成后通过一次重命名发布产物。
失败时只删除本次构建管理的暂存目录。

成功产物包包含只读 qcow2、处理配方、SLSA 来源记录、SPDX 构建范围物料清单、状态为
`testing` 的 `manifest-candidate.json`、校验记录与校验和：

| 文件 | 用途 |
|---|---|
| `<name>-<release>-<arch>-<digest-prefix>.qcow2` | 已校验的候选镜像字节 |
| `build-recipe.json` | 调用参数、配方/工具身份与输入记录 |
| `manifest-candidate.json` | 未签名 testing 候选元数据 |
| `provenance.intoto.json` | SLSA 来源声明 |
| `sbom.spdx.json` | 声明的输入与构建范围 |
| `validation.json` | qcow2 前后检查、归一化结果与尚未通过的发布检查 |
| `checksums.txt` | 产物包内文件的 SHA-256 |
| `package-lock.json` | 使用软件包输入时额外包含 |

候选清单是流水线证据格式。仓库组装才会生成运行时使用的 Schema-3 `catalog.json`。
SPDX 文件描述声明的输入和构建范围，不是客机文件系统的完整软件包清单。签名在流水线之外执行。
输入和工具固定时，validate 校验模式可逐字节复现。
offline 离线模式的结果用于发布验证前，必须对同一候选镜像构建两次并比较。

发布仍需对每条声明的宿主与客机路径执行运行时启动测试。
还需审查支持状态与溯源、增加镜像目录修订号、执行生产签名，并校验公开产物。
构建成功不能直接将候选镜像改为 `supported`，也不能证明它已经公开可用。
