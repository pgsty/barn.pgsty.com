---
title: 镜像流水线
description: 不下载、不上传、不签名地校验或离线归一化显式 qcow2 候选镜像。
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

- `validate`：复制并重哈希，强制 qcow2 检查，校验单元素后端镜像链，运行
  `qemu-img check`，输出用于审核、未经发布验证的产物包；不会修改客机凭据。
- `offline`：额外在暂存副本上使用 libguestfs `virt-customize --no-network` 与
  `virt-cat`。它拒绝无关 UID/GID 88 占用，归一化锁定的 `dba`/`admin` 身份，关闭密码与
  root SSH 登录，清理密钥/历史/主机身份/cloud-init 缓存，恢复定向 SELinux 标签，
  并回读确定性标记。

## 官方候选镜像矩阵

`build-official.py` 在同一离线边界上封装固定的八目标矩阵：Debian 12/13 与 Rocky Linux
8/9，各自覆盖 amd64、arm64。每份上游 qcow2、RPM/DEB 输入、发布版本名称、摘要与
源时间戳都锁定在 `official-v1.json`。

```bash
./packaging/image-pipeline/build-official.py --list

./packaging/image-pipeline/build-official.py \
  --source-cache /absolute/source-cache \
  --package-cache /absolute/package-cache \
  --output /absolute/existing-output-root \
  --target d13/arm64 --fetch
```

不加 `--fetch` 时，全部锁定输入必须已经位于两个规范化缓存目录；加上后，封装脚本
也只下载固定 HTTPS URL，并在调用离线归一化前拒绝任何摘要不匹配。Debian 12/13
安装锁定的 XFS 用户态工具及其依赖；Rocky Linux 8 安装锁定的 `python36` 与 `python3-pip`
RPM，并在 cloud-init 启用 NTP 时使用镜像已有的 RHEL chrony 模板与 `chronyd` 服务；
Rocky Linux 9 不需要额外软件包输入。SELinux 标签恢复属于归一化步骤，不是另一组软件包输入。

Debian 同时生成 `en_US.UTF-8`，并保留 `C.UTF-8` 作为默认 locale；归一化脚本和
宿主端标记校验都会检查这两项。镜像更新也会保留这两项客机要求。Ubuntu 使用固定
日期的官方原始镜像，不经过这套离线定制流程。

每份结果仍是未签名的 `testing` 候选镜像。不传 `--target` 时构建全部八个目标，重复
该参数可以选择多个目标。`--list` 显示当前源码锁定的精确版本；目前包含 Debian
`20260923.2610.1`/`20260914.2601.2` 与 Rocky Linux
`8.10.20240528.3`/`9.8.20260525.2`。

组装接收的是**包含按名称命名的产物包的父目录**，不是各产物包自身目录。若八个
构建都放在同一个输出根下，执行：

```bash
./packaging/image-pipeline/build-official.py \
  --assemble-from /absolute/existing-output-root \
  --output /absolute/new-candidate-repository
```

构建分散在不同根时，可以重复 `--assemble-from`。八个目标都必须有且只有一个产物包；
组装会创建新的静态仓库，并调用 PATH 中的 `barn` 执行 `repo build` 与 `verify`，
也可用 `--barn /absolute/path/to/barn` 指定程序。构建模式使用已存在的输出根，
组装模式的目标目录则必须不存在。生成仓库使用 `candidate` 通道，而不是 `stable`，
例如应选 `d13:candidate`。此过程不包含真机启动测试、签名、上传或镜像目录发布。

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

源文件与输出必须是绝对路径；源文件必须使用规范化路径，且为普通文件、非符号链接，复制期间保持稳定，
且不超过 16 GiB；输出路径必须不存在。构建器使用相邻排它锁、0700 暂存目录与一次最终
重命名；失败只删除受保护的暂存目录。

成功产物包包含只读 qcow2、处理配方、SLSA 来源记录、SPDX 构建边界物料清单、状态为
`testing` 的 `manifest-candidate.json`、校验记录与校验和。候选清单
是流水线证据格式；仓库组装才会生成运行时使用的 Schema-3 `catalog.json`。SPDX 文件
描述声明的输入/构建边界，并不是客机文件系统的完整软件包清单。签名刻意位于流水线
之外。固定输入/工具下 validate 模式逐字节可复现；offline 修改必须构建两次并比较，
才能成为发布验证记录。

发布仍需要对每条声明的宿主与客机路径进行运行时启动测试，明确审查支持状态与溯源，
增加镜像目录修订号，进行生产签名，并校验公开工件。构建成功不能直接把候选镜像
改成 `supported`，也不能证明它已经公开可用。
