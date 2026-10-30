---
title: 未发布变更
description: Barn 0.9.2 之后的开发工作流调整：路径、共享、节点选择、镜像与限制。
weight: 15
icon: fa-solid fa-code-branch
---

本页记录 **2026-10-30** 在源码提交 `27f17bb`（`fix: remove unnecessary restrictions from development workflows`）中实现的变更，**尚未包含在已发布的 0.9.2 下载包中**。如需试用，请从包含该提交的工作区[构建源码](../../start/source-build/)，并通过 `barn version` 核对构建身份。

已发布版本见 [Barn 0.9.2](/zh/blog/release/0.9.2/)。该版本的 Apple Silicon 软件包已经包含 `Barn.app`，SSH/exec 也已经要求使用 `--`。

## 路径 {#paths}

`barn init` 与 `setup` 支持通过目录符号链接工作，`init -o ./lab/config/barn.yml` 还会自动创建缺失的父目录。覆盖已有文件仍需 `--force`，写入不会跟随或替换输出文件本身的符号链接。0.9.2 中 `atomic create parent is not a real directory` 报错的临时解决方法见[故障排查](../../start/troubleshooting/#linked-directory)。

用户传入的路径支持常见开发目录布局：

| 输入 | 解析方式 |
|---|---|
| `BARN_HOME` | 支持相对路径、`~/` 与目录符号链接，也可以是当前工作目录 |
| 清单与 `provision --script` | 支持指向普通文件的符号链接；每个文件仍有 4 MiB 上限 |
| Linux `vm_shares.host` | 相对于清单真实文件所在目录，也接受绝对路径、`~/` 与目录符号链接 |
| 本地镜像仓库与 `image import` | 支持相对路径、`~/` 与符号链接输入 |
| `catalogexport` 输出 | 支持相对路径、`~/`、父目录符号链接及自动创建父目录；目标文件须不存在 |
| `BARN_MAC_RUNNER` 与本地 `socket_vmnet` 归档 | 支持相对路径与 `~/`；归档输入可为符号链接，仍需通过摘要校验 |
{.wide}

命令行相对路径以当前工作目录为基准，相对 `BARN_HOME` 也遵循这条规则。跨目录操作同一部署时，请使用绝对 `BARN_HOME`。Barn 仍拒绝将 `/` 或用户主目录作为数据根目录，并校验受管状态的属主与结构。归当前用户所有的 `~/.ssh` 目录可以通过目录符号链接访问；若 `~/.ssh/config` 本身是链接，仍需手动添加 `Include`。

## 共享目录与挂载路径 {#sharing}

Linux 客机使用 **QEMU Virtio-9p**，现已支持 macOS 与 Linux 宿主，但 QEMU 和客机内核均须支持 9p。原生 macOS 客机继续通过 `barn mac --share` 使用 **VirtioFS**。

- Linux 共享源按当前用户的实际文件系统权限访问，可归其他用户所有、与其他源重叠，或由多个客机同时读写。并发写入由用户协调，与多个宿主进程共用目录相同。
- 宿主源路径支持空格、Unicode 与逗号。Linux 客机挂载路径会自动规范化，并正确转义 Shell 命令与 `fstab` 中的空格、Unicode 和 Shell 标点。
- Mac 共享名称支持空格与中文，须为 1–255 字节的有效 UTF-8，不能是 `.`、`..`，也不能含 `/` 或 ASCII 控制字符；共享源支持目录符号链接。
- 移除 8 个共享的固定上限，实际仍受后端设备与宿主资源约束。Linux 共享源不能与 `BARN_HOME` 重叠，客机挂载目标不能与其他目标、系统目录、数据盘挂载点或客机 SSH 目录重叠。

Linux 共享示例见[存储与访问](../../start/storage/)，原生 macOS 共享见 [Mac 命令](../../reference/mac/)。Barn 不会为了让共享可写而修改宿主文件属主。

## 仅应用选定节点的变更 {#selection}

显式选择节点执行 `plan`、`up`、`reload` 或 `recreate` 时，其余节点保留已应用定义，即使当前清单已修改或省略它们。未创建且未选中的节点不要求解析镜像，因此可以一次编辑多个节点，再分批应用：

```bash
barn plan node-1 -f barn.yml
barn recreate node-1 -f barn.yml
barn plan node-2 -f barn.yml
```

整份清单仍须通过语法解析。与已应用节点的地址、别名、控制节点角色或部署公共设置发生冲突时，Barn 会在停机删盘前报错。不传选择器时仍检查整份清单，删除 YAML 条目不会自动删除虚拟机。操作流程见[日常管理](../../start/operations/#selected-nodes)。

## 镜像与开发工作流限制 {#limits}

| 项目 | 新行为 |
|---|---|
| Linux 节点数 | 不再另设 20 节点上限；节点须使用部署 `/24` 中互不重复的可用地址，且宿主资源充足 |
| 外部清单主机 | `vm_skip: true` 可使用主机名或 IPv6 键；托管虚拟机仍使用 IPv4，清单至少保留一个托管节点 |
| Linux 容量字符串 | 单位大小写不敏感；`K/M/G/T` 与 `KiB/MiB/GiB/TiB` 为二进制，`KB/MB/GB/TB` 仍为十进制 |
| Provisioning | `--parallel` 接受正整数，最多启动与所选节点数相同的工作线程；`--timeout` 接受任意正时长，移除原有 4 并发与 24 小时上限 |
| 镜像大小 | 本地导入及声明了大小的目录产物不再限于 8 GiB；未声明大小的旧协议下载仍保留 8 GiB 边界 |
| 镜像导入 | 源文件可任意命名；新缓存使用 `local/<sha256>.qcow2`，同名不同内容可共存，相同内容复用缓存 |
| 本地别名 | 移除 256 个别名上限；注册表元数据超过 1 MiB 时在写入前报错，重新导入已有别名时保留原缓存路径 |
| 本地仓库 | 支持相对根目录、目录链接与共享可写目录，`repo.yaml` 可以是指向普通文件的符号链接 |
| Mac 日志 | `--lines` 接受任意正整数，不再按 1 MiB 或 10000 行静默截断请求的日志 |
| 备用端口 | 按 `首选端口 + n × 10000` 尝试至 65535，不再仅尝试前五个候选值 |
{.wide}

Provisioning 仍默认串行、超时一小时，每个节点分别最多捕获 1 MiB 的 stdout 与 stderr。这些用户参数与内部虚拟机启动调度并发是不同的设置。镜像摘要、声明大小、`qcow2` 结构、持久盘兼容性及进程身份仍需通过校验；贡献者镜像流水线也保留自身的配方边界。
