---
title: 设计
description: Barn 如何组织 Linux 实验环境与 macOS 客机，以及配置、网络、存储和生命周期的设计取舍。
weight: 20
icon: fa-solid fa-compass-drafting
aliases: [/docs/concepts/, /docs/concepts/networking/, /docs/concepts/storage/, /docs/concepts/safety/, /docs/architecture/, /docs/architecture/overview/, /docs/architecture/networking/, /docs/architecture/security/]
---

Barn 通过同一个命令行入口提供两套独立的虚拟化工作流：多节点 Linux 实验环境与独立命名的 macOS 客机。

| 维度 | Linux 实验环境（`barn …`） | macOS 客机（`barn mac …`） |
|---|---|---|
| 虚拟化引擎 | QEMU + HVF/KVM 硬件加速（跨架构与 Apple Silicon 上的 `el8` 使用 TCG） | Apple `Virtualization.framework` |
| 期望配置 | 兼容 Pigsty 的单份 YAML 主机清单（`barn.yml`） | 通过 `barn mac` 参数管理的具名虚拟机 |
| 状态目录 | `$BARN_HOME`（默认 `~/.barn`） | `$BARN_HOME/mac`（默认 `~/.barn/mac`） |
| 网络模型 | 用户态管理网卡 + 共享固定 IP `/24` 实验子网 | 每台虚拟机独立的 `/24` NAT 子网与 `.10` DHCP 预留 |
| 典型场景 | 数据库集群、Ansible 剧本演练、多节点 Linux 联调 | macOS 编译打包、桌面应用测试、隔离开发环境 |
{.wide}

下文概述 Linux 实验环境的核心设计；各模块的深层设计取舍请阅读[设计注记](/zh/blog/design/)，原生 macOS 工作流请查阅[macOS 客机指南](../../start/macos/)与 [Mac 命令参考](../../reference/mac/)。

## 每位用户一套 Linux 实验环境

每位系统用户通过一份兼容 Pigsty 的 YAML 清单管理唯一一套存放在 `BARN_HOME`（默认 `~/.barn`）中的 Linux 部署（详见[为什么 Barn 没有项目](/zh/blog/design/one-deployment-no-projects/)）。由于部署状态与工作目录解耦，日常生命周期与节点访问命令可在任意目录下执行。

## 节点级收敛

Barn 根据文档规定的 `vm_*` 字段与 Pigsty 身份字段为每个节点计算规格哈希，并将其与已提交状态及 QEMU 进程身份一同落盘：

- `barn up` 会创建新增节点、启动已停止节点、在不中断运行中 QEMU 进程的前提下重试未完成的客机初始化，并刷新受管的 `/etc/hosts` 与 SSH 配置。
- 修改已有节点的规格或从 `barn.yml` 中删去节点绝不会在后台静默销毁虚拟机——变更配置需显式运行 `barn recreate`，删除节点需显式运行 `barn destroy`（详见[声明式不等于破坏式](/zh/blog/design/convergence-without-surprise/)）。

## 运行时选择

`vm_arch` 作用于整套部署（省略或设为 `native` 时取宿主架构；显式指定 `amd64` 或 `arm64` 时选用对应架构镜像）。当客机与宿主架构一致时，Barn 默认使用 HVF/KVM 原生硬件加速；仅在跨架构运行或命中目录声明的内核兼容例外（Apple Silicon 上的 `el8` `arm64`）时才使用 QEMU TCG。若原生加速因其他原因失败，Barn 会直接报错停止，而不会静默退化到软件模拟。

每个节点的已提交状态都会记录实际架构与加速器（可通过 `barn status` 查看）。在执行破坏性的 `recreate` 之前，Barn 会预先校验 QEMU 二进制、版本号、网络后端、基础镜像字节、引导方式与固件，确保缺少依赖时不会误删现有的正常节点。

## 双网卡与单个固定子网

每台 Linux 虚拟机均挂载两张虚拟网卡（详见[为什么每个 Barn 节点都有两张网卡](/zh/blog/design/fixed-ip-two-nics/)）：

- **管理网卡**：基于 QEMU 用户态网络，无需修改宿主防火墙即可提供 DHCP、DNS、外网访问与宿主回环端口 SSH 转发。
- **固定 IP 实验网卡**：承载 `barn.yml` 中声明的 RFC1918 `/24` 静态地址，供宿主与节点互访、节点间复制及 Ansible 连接使用。

为了在保持 QEMU 非特权运行的同时提供固定 IP 子网：

- **macOS 宿主**使用固定版本的 `socket_vmnet` 服务。
- **Linux 宿主**优先复用活跃的 NetworkManager（通过 `nmcli` 管理 `barn0` 网桥），否则使用 `systemd-networkd` 配合发行版 `qemu-bridge-helper`（启动未激活的 `systemd-networkd` 前会先扫描现有配置，确保不会误接管宿主物理网卡）。在 Debian 上，`setup` 会向当前用户所属组授予 `qemu-bridge-helper` 权限，并以普通用户身份实际运行一次 QEMU 挂桥测试，验证通过后才提交网络安装事务。

## 存储与配置生命周期分离

期望配置（`barn.yml`）、已应用状态（`$BARN_HOME`）与基础镜像缓存（`$BARN_HOME/images`）拥有各自独立的生命周期：

- 更新镜像目录通道（`barn update`）不会改写已创建节点的根盘。
- 通过校验的基础镜像以只读权限共享，每台虚拟机将根盘写入各自独立的写时复制层（root overlay）。
- 普通 `destroy` 与 `recreate` 会保留 `persistent: true` 的持久数据盘，而客机恢复流程在遇到无法识别或确认损坏的数据盘文件系统时会自动重格式化（详见[数据盘配置](../../reference/configuration/#数据盘)与[存储与访问](../../start/storage/)）。
- `barn image prune` 自动保护活动镜像目录、已应用节点与 `local-*` 别名所引用的镜像（详见[镜像参考](../../reference/images/)）。

## 安全边界

QEMU 进程与镜像下载均以当前普通用户身份运行；仅安装宿主依赖（`setup`）、配置宿主网络（`network install/uninstall`）与更新系统 `/etc/hosts`（`hosts install/uninstall`）需要管理员权限。在向进程发送信号或删除节点文件前，Barn 会逐一核验文件属主、路径边界、QMP UUID/名称身份、进程启动时间与命令行哈希元组以及操作日志白名单，任何一项存疑都会立即中止操作（详见[PID 不是虚拟机身份](/zh/blog/design/identity-before-pid/)）。
