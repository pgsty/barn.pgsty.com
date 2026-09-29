---
title: 镜像流水线
description: 不下载、不上传、不签名地校验或离线归一化显式 qcow2 Candidate。
weight: 40
icon: fa-solid fa-shield-halved
---

底层 `packaging/image-pipeline/build.sh` 接受一份已下载的不可变 qcow2 与独立获得的
SHA-256。它绝不下载、上传、修改 Barn 运行时/网络状态、读取签名密钥，也不会把镜像
标成 `supported`。

以下命令从 Barn 源码目录执行。需要 Python 3 与 `qemu-img`；`offline` 还需要可用的
libguestfs `virt-customize`、`virt-cat`。这是镜像构建宿主的依赖，与 `barn setup`
为运行 VM 安装的依赖是不同边界。

## 模式

- `validate`：复制并重哈希，强制 qcow2 检查，校验单元素 Backing Chain，运行
  `qemu-img check`，输出明确不可发布的证据 Bundle；不会修改 Guest 凭据。
- `offline`：额外在 Staged Copy 上使用 libguestfs `virt-customize --no-network` 与
  `virt-cat`。它拒绝无关 UID/GID 88 占用，归一化锁定的 `dba`/`admin` 身份，关闭密码与
  Root SSH，清理密钥/历史/Host Identity/cloud-init Cache，恢复定向 SELinux Label，
  并回读确定性 Marker。

## 官方 Candidate 矩阵

`build-official.py` 在同一离线边界上封装固定的八目标矩阵：Debian 12/13 与 Rocky Linux
8/9，各自覆盖 amd64、arm64。每份上游 qcow2、RPM/DEB 输入、Release 名称、Digest 与
Source Epoch 都锁定在 `official-v1.json`。

```bash
./packaging/image-pipeline/build-official.py --list

./packaging/image-pipeline/build-official.py \
  --source-cache /absolute/source-cache \
  --package-cache /absolute/package-cache \
  --output /absolute/existing-output-root \
  --target d13/arm64 --fetch
```

不加 `--fetch` 时，全部锁定输入必须已经位于两个 Canonical Cache 目录；加上后，Wrapper
也只下载固定 HTTPS URL，并在调用离线归一化前拒绝任何 Digest 不匹配。Debian 12/13
安装锁定的 XFS 用户态闭包；Rocky Linux 8 安装锁定的 `python36` 与 `python3-pip`
RPM；Rocky Linux 9 不需要额外软件包输入。SELinux 标签恢复属于归一化步骤，不是另一组
软件包输入。

Debian 同时生成 `en_US.UTF-8`，并保留 `C.UTF-8` 作为默认 locale；归一化脚本和
宿主端 Marker 校验都会检查这两项。镜像更新不能丢失这项历史调整。Ubuntu 使用固定
日期的官方原始镜像，不经过这套离线定制流程。

每份结果仍是未签名的 `testing` Candidate。不传 `--target` 时构建全部八个目标，重复
该参数可以选择多个目标。`--list` 显示当前源码锁定的精确版本；目前包含 Debian
`20260923.2610.1`/`20260914.2601.1` 与 Rocky Linux
`8.10.20240528.1`/`9.8.20260525.1`。

组装接收的是**包含按名称命名的 Bundle 的父目录**，不是各 Bundle 自身目录。若八个
构建都放在同一个输出根下，执行：

```bash
./packaging/image-pipeline/build-official.py \
  --assemble-from /absolute/existing-output-root \
  --output /absolute/new-candidate-repository
```

构建分散在不同根时，可以重复 `--assemble-from`。八个目标都必须有且只有一个 Bundle；
组装会创建新的静态仓库，并调用 PATH 中的 `barn` 执行 `repo build` 与 `verify`，
也可用 `--barn /absolute/path/to/barn` 指定程序。构建模式使用已存在的输出根，
组装模式的目标目录则必须不存在。生成仓库使用 `candidate` Channel，而不是 `stable`，
例如应选 `d13:candidate`。此过程不包含真机 Smoke、签名、上传或 Catalog 发布。

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

Source/Output 必须是绝对路径；Source 必须 Canonical、普通、非符号链接、复制期间稳定，
且不超过 16 GiB；Output 必须不存在。Builder 使用相邻排它锁、0700 Staging 与一次最终
Rename；失败只删除受保护的 Staging。

成功 Bundle 包含只读 qcow2、Recipe、SLSA Provenance、SPDX Boundary SBOM、状态为
`testing` 的 `manifest-candidate.json`、Validation Evidence 与 Checksums。候选 Manifest
是流水线证据格式；仓库组装才会生成运行时使用的 Schema-3 `catalog.json`。SPDX 文件
描述声明的输入/构建边界，并不是 Guest 文件系统的完整软件包清单。签名刻意位于流水线
之外。固定输入/工具下 validate 模式逐字节可复现；offline Mutation 必须构建两次并比较，
才能成为 Release Evidence。

发布仍需要对每条声明的宿主/Guest 路径进行运行时 Smoke，明确审查支持状态与溯源，
增加 Catalog Revision，进行生产签名，并校验公开工件。构建成功不能直接把 Candidate
改成 `supported`，也不能证明它已经公开可用。
