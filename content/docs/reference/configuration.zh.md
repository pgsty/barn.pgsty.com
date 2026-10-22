---
title: 配置
description: Barn 读取的 Pigsty 主机清单字段、默认值与节点级漂移行为。
weight: 10
icon: fa-solid fa-file-code
aliases: [/docs/concepts/project-model/]
---

本参考描述 **Barn 0.9.1**。使用其他版本时，请先核对 `barn version`。

## 发现顺序

依次查找：显式 `-f`、当前目录的 `barn.yml`、`barn.yaml`、`pigsty.yml`、
`pigsty.yaml`。所有文件名都使用同一种 Pigsty 兼容 YAML 清单。

找不到配置文件但已有部署时，`plan`、`up`、`reload`、`recreate` 使用已应用规格。
`validate` 不会回退。配置必须是最大 4 MiB 的普通文件，不能是符号链接。
Barn 使用按发现顺序找到的第一个文件。如果该文件无效，Barn 直接报错，不再尝试下一个文件。
重命名文件或切换目录不会创建另一套部署。Barn 将已应用状态保存在 `BARN_HOME`。

## 完整配置示例

`barn init [meta|dual|trio|full]` 分别生成 1、2、3、4 个节点。`meta` 使用 `.10`，
更大的模板依次增加 `.11` 的 `node-1`、`.12` 的 `node-2`、`.13` 的 `node-3`。
这些模板只定义节点拓扑，不定义 Pigsty 服务角色。`--cidr` 改变生成的 `/24`，
保留上述地址末段。用 `barn init full -o -` 可在不创建文件的情况下检查模板。

```yaml
all:
  vars:
    admin_ip: 10.10.10.10
    vm_image: u24
    vm_cpu: 2
    vm_mem: 4GiB
    vm_disk: 64
  children:
    lab:
      hosts:
        10.10.10.10: { nodename: meta }
        10.10.10.11:
          nodename: worker
          vm_mem: 8GiB
          vm_disks:
            - { path: /data, size: 128, fs: auto, persistent: true }
```

此清单定义两个托管节点，控制节点为 `meta`。保存为 `barn.yml` 后，执行以下检查，不启动虚拟机：

```bash
barn validate -f barn.yml
barn --json validate -f barn.yml
barn plan -f barn.yml
```

JSON 校验结果包含 `valid`、`source`、`spec_hash`、`resolved`。
Barn 0.9.1 的 `validate` 还会解析镜像目录中的镜像引用，并接受 `--repo`。
镜像目录无法读取时，结果会包含警告，镜像引用仍未校验。
`local-*` 镜像字节仍由 `up` 校验。
配置校验不检查宿主资源、共享访问、网络、镜像文件或客机就绪状态，也不会启动虚拟机或下载镜像。

## Barn 读取什么

文档必须包含顶层 `all:` 分组。Barn 遍历其中的 `hosts` 和嵌套 `children` 映射。
它不执行 Ansible 动态清单插件或 Jinja 表达式，也不加载 `group_vars` 或 `host_vars` 文件。
同一地址出现在多个组时，仍只定义一个节点。Barn 合并解析各组的继承值。

Barn 读取节点 IP、`nodename`、`admin_ip`、`pg_cluster`、`pg_seq`、
`node_admin_username`、`node_admin_uid` 和已记录的 `vm_*` 变量。

**控制节点。** Barn 只从 `all.vars` 读取 `admin_ip`。未设置或没有匹配的托管节点时，使用第一个托管节点。
遍历遵循 YAML 顺序，先读取当前组的节点，再读取子组。需要固定控制节点时，请显式设置 `admin_ip`。

**登录账号。** 所有节点必须使用同一登录用户名，且匹配 `[a-z_][a-z0-9_-]{0,31}`。
默认用户 `dba` 的显式 `node_admin_uid` 必须为 88。
使用自定义用户名时，Barn 仍检查 `node_admin_uid` 是否为整数，但不据此设置客机 UID。
Barn 不支持任意定制客机 UID。

**忽略的字段。** Barn 不读取 `pg_role`、`pg_version`、`repo_*`、`node_packages` 等字段，因此它们不会产生配置差异。
前文列出的部分 `pg_*` 和 `node_*` 字段仍会读取。

**继承与校验。** Barn 严格校验已读取的字段。未知 `vm_*`、错误类型、Jinja 表达式、非法地址和同级分组冲突都会报错。
继承顺序是 `all.vars` → 更深层的 `children.<group>.vars` → 节点变量。
节点上的 `vm_disks` 等列表整体替换继承列表，不会追加。
同一深度的组提供不同值时，必须在节点层覆盖并消除冲突。

Barn 支持 YAML 锚点和合并键。显式键优先，合并序列中靠前的映射优先。
重复映射键和多个 YAML 文档都会报错。

**跳过节点。** 即使设置 `vm_skip: true`，节点键也必须是 IPv4 地址。
跳过的节点不计入 20 节点上限，也不参与托管子网推导。清单仍必须包含至少一个托管节点。
跳过已应用节点，只会将其标为从清单移除，不会销毁虚拟机。

Barn 0.9.1 在可定位时显示出错规则、错误值和行号，并提示相近的 `vm_*` 拼写。

## VM 变量

| 变量 | 默认值 | 含义 |
|---|---|---|
| `vm_skip` | `false` | 不虚拟化这台真实/外部主机 |
| `vm_image` | `u24` | 镜像系列、通道引用或 `image@version` 选择器 |
| `vm_version` | 未设置 | 匹配 `9`、`9.7` 等数值前缀的最新版本 |
| `vm_arch` | `native` | 部署级客机架构：`native`、`amd64` 或 `arm64` |
| `vm_cpu` | `2` | vCPU 数量 |
| `vm_mem` | `4096` | MiB 整数，或 `8GiB` 等尺寸 |
| `vm_disk` | `64` | 根盘：GiB 整数或 `64GiB` 等显式尺寸 |
| `vm_disks` | `[{path: /data}]` | 额外数据盘，默认一块挂载到 `/data` 的 128 GiB 非持久盘 |
| `vm_alias` | `[]` | 客机 `/etc/hosts`、SSH 配置与可选宿主别名 |
| `vm_shares` | `[]` | QEMU 9p 宿主目录共享 |

空节点条目就能定义完整的虚拟机。每套部署支持 1–20 个托管节点。
`vm_cpu` 范围为 1–256，内存至少为 512 MiB。内存裸整数使用 MiB，磁盘裸整数使用 GiB。
显式尺寸字符串接受正整数加 `B`、`KiB`、`MiB`、`GiB`、`TiB`、`KB`、`MB`、`GB`、`TB`，区分大小写。
`8GiB` 合法。`8G`、`1.5GiB` 和无单位的引号字符串 `"8192"` 不合法。
根盘和数据盘尺寸必须为正。`up` 还会检查根盘是否不小于所选基础镜像的虚拟尺寸。

省略 `vm_image` 时默认选择 Ubuntu 24.04。使用 Debian 13 时，在 `all.vars` 中
写明 `vm_image: d13`。此清单默认值来自二进制内置镜像目录；更改自定义仓库的
默认镜像，不会改写省略 `vm_image` 的清单。修改已有 Barn 配置后先查看 `barn plan`。

0.9.1 解析清单时，还会按内置镜像目录归一化已有别名，例如把 `ubuntu` 转为
`u24`。自定义仓库若把这些别名改指其他系列，清单解析可能与 `image info` 结果
不同。`vm_image` 应使用自定义镜像目录中的规范系列名，并避免将内置别名重新分配给
另一个系列。

用 `vm_version` 单独指定版本前缀：

```yaml
vm_image: el9
vm_version: "9.7"
```

镜像目录中存在完全相同的版本时，Barn 优先精确匹配。
否则，Barn 按点号分隔的完整分量匹配前缀，并按数值选择最新版本。
`9.7` 选择最新 `9.7.*` 构建，`9` 选择最新 9.x 发布版本。
各分量按整数比较，因此 9.10 晚于 9.9。
`vm_version` 不能与已带 `:channel` 或 `@version` 的 `vm_image` 同时使用。

设置 `vm_arch` 时，所有托管节点必须解析为同一个值。请只在 `all.vars` 定义一次。
修改它会改变部署级配置，必须重建整套部署。
Linux 的宿主准备流程只安装本机架构的模拟器。运行其他架构还需要对应的 `qemu-system-*` 和固件。

## 数据盘

```yaml
vm_disks:
  - path: /data
    size: 128
    fs: auto
    persistent: false
```

`path` 定义磁盘身份和挂载点。`fs` 接受 `auto`（默认）、`xfs` 或 `ext4`。
对于空白的 `auto` 磁盘，客机有 `mkfs.xfs` 时使用 XFS，否则使用 ext4。
显式指定 `xfs` 或 `ext4` 时不会改用其他文件系统。Barn 直接复用健康的已有文件系统。
`persistent: true` 在普通销毁后保留磁盘。`vm_disks: []` 表示不创建额外盘。
每项 `size` 默认 128 GiB。整数使用 GiB，也接受显式尺寸字符串。

挂载点必须是 `/data`、`/data/pg` 等规范绝对路径。
Barn 去除路径首尾的 `/`，再把中间的 `/` 替换为 `-`，得到磁盘身份。
磁盘身份必须匹配 `[a-z][a-z0-9-]{0,31}`。单个节点内，磁盘身份和挂载点均不能重复。
Barn 拒绝 `/`、`/etc`、`/usr`、`/root`、`/var/lib/barn` 等系统路径及其重叠的父子路径。
修改持久盘身份或声明可能需要显式迁移。持久性不保证新定义可以自动复用旧盘。

**数据盘按可丢弃的测试存储处理。** 对于无法识别或已确认损坏的文件系统，`up` 会清空并按配置类型重建。
Barn 会报告数据丢失，持久盘也适用这条规则。
持久性只控制销毁或重建虚拟机时是否保留磁盘，不保证保留损坏内容。
探测失败、设备暂缺、挂载占用和底层 I/O 故障不会触发格式化。此恢复不涉及根盘或宿主共享目录。

## 目录共享

**macOS 宿主上的 Linux 客机：** `vm_shares` 使用 QEMU 9p，Barn 不支持在 macOS 宿主上使用它。
配置了它的节点无法启动，`validate` 和 `plan` 会报告警告。这类客机请使用 SSH 传输文件。
独立的 `barn mac --share` 使用 VirtioFS，支持 macOS 客机共享目录。
修改已有节点的共享配置需要 `recreate`，该操作会替换根盘。请先保留所需数据。
Barn 不会退回未经身份校验的宿主路径。

```yaml
vm_shares:
  - host: /absolute/owned/source
    guest: /src
    readonly: true
```

`readonly` 默认为 `true`。每个节点最多接受八个共享。
宿主和客机路径必须是规范绝对路径。Barn 不展开 `~` 或相对路径。
源目录必须存在且属于调用者。路径的任何分量都不能是符号链接。
客机目标只接受字母、数字、`.`、`_`、`-`、`/`，不接受空格。
源目录不能与 `BARN_HOME` 重叠。Linux 上请使用真实路径（`realpath /path/to/source`）。
Barn 0.9.1 会在符号链接错误中提示可用的真实路径。

同一节点内，各宿主源目录之间不能重叠，各客机目标目录之间也不能重叠。
不同节点的源目录只有全部只读时才能重叠。
客机目标不能覆盖数据盘挂载点、保留系统路径或登录用户的 `.ssh` 目录。
9p 只适合可信开发文件，不能存放 PostgreSQL 数据。
请求可写共享但客机无法写入时，Barn 会尝试只读访问并报告限制。
修正权限后，再次执行 `up` 重试。Barn 不会递归修改宿主文件属主。

执行 `up` 或 `start` 时，源目录缺失只影响对应节点，其余选中节点继续执行。
恢复原目录或宿主挂载后，重试该节点。Barn 不会创建空目录代替。
重启、重新加载和重建操作会在停止已有节点前校验源目录。

## 名称与地址

节点名依次取 `nodename`、`<pg_cluster>-<pg_seq>`、`node-<IP末段>`，且必须唯一。
名称长度为 1–63，只能包含小写字母、数字和连字符，不能以 `-` 开头或结尾。
非空显式 `nodename` 优先，此时无需使用其他 `pg_cluster`、`pg_seq` 值派生名称。
`vm_alias` 是小写 DNS 风格名称列表，不能与节点名或部署内任何其他别名重复。

所有托管节点必须位于同一个 RFC1918 `/24`：`.1` 属于宿主，`.2`–`.8` 保留，节点使用
`.9`–`.254`。

客机内承载清单地址的是固定 IP 网卡，可用 `ip -br addr` 查看。Barn 不保证该网卡的名称。

## 漂移

Barn 对每个解析后节点计算哈希。`up` 创建新增节点，并启动选中的已停止节点。
运行中节点保留进程，Barn 重试未完成的客机初始化。
虚拟机定义变化需要重建对应节点。Barn 只报告已移除的节点，不会自动销毁它们。
部署架构、用户或子网变化需要重建整套部署。
`plan`/`up` 会把镜像选择器解析为精确镜像身份。镜像目录更新后，即使清单文本未变，也应检查计划。
修改用于生成节点名的字段，会产生旧节点 `missing` 和一个新节点。请使用稳定、显式的 `nodename`。
