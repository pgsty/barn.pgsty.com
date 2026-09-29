---
title: 配置
description: Barn 读取的 Pigsty Inventory 字段、默认值与节点级漂移行为。
weight: 10
icon: fa-solid fa-file-code
aliases: [/docs/concepts/project-model/]
---

本参考描述 **Barn 0.9.0 发布候选**。Barn 只使用新名称与全新的 Barn 状态，
不提供旧开发版本的兼容或迁移层。编写脚本前先核对 `barn version`，
发布进度见[当前状态](../../about/status/#documentation-baseline)。

## 发现顺序

依次查找：显式 `-f`、当前目录的 `barn.yml`、`barn.yaml`、`pigsty.yml`、
`pigsty.yaml`。所有文件名都使用同一种 Pigsty 兼容 YAML Inventory。

`plan`、`up`、`reload`、`recreate` 找不到文件时，如果 deployment 已存在，会回退到
已应用规格；`validate` 不会回退。配置必须是最大 4 MiB 的普通非符号链接文件。
发现顺序中第一个存在的文件生效；它若无效会直接报错，不会继续尝试下一个文件名。
重命名文件或切换目录不会产生另一套部署，已应用状态保存在 `BARN_HOME`。

## 完整配置示例

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

这里定义了两个托管节点，控制节点为 `meta`。保存为 `barn.yml` 后，可以先检查而不启动 VM：

```bash
barn validate -f barn.yml
barn --json validate -f barn.yml
barn plan -f barn.yml
```

JSON 校验结果包含 `valid`、`source`、`spec_hash`、`resolved`。**0.9 候选版本**的
`validate` 还会解析 Catalog 镜像引用，并接受 `--repo`；Catalog 无法读取时会报告警告，
不会声称镜像已检查；`local-*` 镜像字节校验仍由 `up` 完成。配置校验不能证明宿主资源、
共享访问、网络、镜像字节或客机就绪可用，也不会启动 VM 或下载镜像。

## Barn 读取什么

Barn 读取主机 IP、`nodename`、`admin_ip`、`pg_cluster`、`pg_seq`、
`node_admin_username`、`node_admin_uid` 与已记录的 `vm_*` 变量。`admin_ip` 只从
`all.vars` 读取，用于选择控制节点；没有匹配时使用第一台托管主机。所有节点必须解析为
同一个登录用户名；默认用户 `dba` 的显式 `node_admin_uid` 必须为 88。
自定义用户名下，`node_admin_uid` 仍需通过整数校验，但不会设置客机 UID；Barn
没有提供任意定制客机 UID 的配置契约。

其余内容完全不读，也不会产生 drift。这里指 `pg_role`、`pg_version`、`repo_*`、
`node_packages` 等未消费字段，不能泛化为所有 `pg_*` 或 `node_*`。

命名空间内严格校验：未知 `vm_*`、错类型、Jinja 表达式、非法地址、同级分组冲突都会报错。
继承顺序是 `all.vars` → 更深层的 `children.<group>.vars` → 主机变量。
主机上的 `vm_disks` 等列表整体替换继承列表，不会追加。相同深度的组给出不同值时，
必须在主机层覆盖消除冲突。支持 YAML 锚点与合并键：显式键优先，合并序列中靠前的映射优先。
重复映射键和多个 YAML 文档都会报错。

即使 `vm_skip: true`，主机键也必须是 IPv4 地址。跳过的主机不计入 20 节点上限、也不参与
托管子网推导，但至少要有一台托管主机。跳过已应用节点只会将它标为从配置移除，不会销毁 VM。

**0.9 候选版本**改进了错误诊断，在可定位时显示规则、错误值、行号，并提示相近的 `vm_*`
拼写；这些诊断改进没有增加新的 Inventory 变量。

## VM 变量

| 变量 | 默认值 | 含义 |
|---|---|---|
| `vm_skip` | `false` | 不虚拟化这台真实/外部主机 |
| `vm_image` | `u24` | 镜像 Family、Channel 引用或 `image@version` Selector |
| `vm_version` | 未设置 | 匹配 `9`、`9.7` 等数值前缀的最新版本 |
| `vm_arch` | `native` | 部署级 Guest 架构：`native`、`amd64` 或 `arm64` |
| `vm_cpu` | `2` | vCPU 数量 |
| `vm_mem` | `4096` | MiB 整数，或 `8GiB` 等尺寸 |
| `vm_disk` | `64` | 根盘：GiB 整数或 `64GiB` 等显式尺寸 |
| `vm_disks` | `[{path: /data}]` | 额外数据盘，默认一块挂载到 `/data` 的 128 GiB 非持久盘 |
| `vm_alias` | `[]` | Guest `/etc/hosts`、SSH config 与可选宿主别名 |
| `vm_shares` | `[]` | QEMU 9p 宿主目录共享 |

空主机条目就是一台完整 VM。每套 deployment 支持 1–20 台托管主机；`vm_cpu` 范围
1–256，内存至少 512 MiB。内存裸整数单位为 MiB，磁盘裸整数单位为 GiB。
显式尺寸字符串支持正整数加 `B`、`KiB`、`MiB`、`GiB`、`TiB`、`KB`、`MB`、`GB`、`TB`
（区分大小写）。`8GiB` 合法，`8G`、`1.5GiB` 和无单位的引号字符串 `"8192"` 不合法。
根盘与数据盘尺寸必须为正值；`up` 还会检查根盘不小于所选基础镜像的虚拟尺寸。

省略 `vm_image` 时默认选择 Ubuntu 24.04。使用 Debian 13 时，在 `all.vars` 中
写明 `vm_image: d13`；修改已有 Barn 配置后先查看 `barn plan`。

`vm_version` 将简短的版本意图与镜像 Family 分开：

```yaml
vm_image: el9
vm_version: 9.7
```

Catalog 中存在完全相同的版本时优先精确匹配；否则只在点分量边界匹配，并选择数值语义上
最新的结果：`9.7` 选择最新 `9.7.*` Build，`9` 选择最新 9.x Release。各分量按整数
比较，因此 9.10 晚于 9.9。`vm_version` 不能与已经带 `:channel` 或 `@version` 的
`vm_image` 同时使用。

`vm_arch` 比普通逐主机字段更严格：出现时必须在所有托管主机上解析为同一个值，因此
应只在 `all.vars` 定义一次。修改它属于 deployment envelope 变化，必须整体重建。
Linux setup 只安装宿主原生模拟器；外来架构还需要对应 `qemu-system-*` 与固件。

## 数据盘

```yaml
vm_disks:
  - path: /data
    size: 128
    fs: auto
    persistent: false
```

`path` 同时是磁盘身份与挂载点；`fs` 为 `auto`（默认）、`xfs` 或 `ext4`。空白的
`auto` 磁盘在 guest 有 `mkfs.xfs` 时格式化为 XFS，否则为 ext4，与 Vagrant 流程的
行为一致；显式 `xfs`、`ext4` 不会降级，健康的已有文件系统直接复用。`persistent: true`
在普通 destroy 后保留；`vm_disks: []` 表示不要额外盘。每项 `size` 默认 128 GiB，
整数单位为 GiB，也接受显式尺寸字符串。

挂载点需是 `/data`、`/data/pg` 等规范绝对路径。磁盘身份由路径去除首尾 `/`，再把中间的
`/` 替换为 `-`，必须匹配 `[a-z][a-z0-9-]{0,31}`；单个节点内磁盘身份与挂载点均不得重复。
`/`、`/etc`、`/usr`、`/root`、`/var/lib/barn` 等系统路径及与它们重叠的父子路径会被拒绝。
修改持久盘身份或声明可能需要显式迁移；persistent 不表示任意新定义都能自动复用旧盘。

**数据盘按可丢弃的测试存储处理。** `up` 会将无法识别或确认损坏的文件系统清空重建为
配置的类型，并报告旧数据已丢弃。这同样适用于 persistent 盘：持久性控制销毁、重建 VM
时是否保留盘，不保证保留损坏内容。探测失败、设备暂缺、挂载占用或底层 I/O 故障不会
触发格式化；系统盘和宿主共享目录不属于此恢复范围。

## 目录共享

**macOS 限制：** Barn 的目录身份保护共享方式尚不支持
macOS，配置了 `vm_shares` 的节点无法启动；候选版本还会在 `validate`、`plan` 时发出警告。新建 macOS 实验环境
应先省略共享；完整共享支持仍待完成。修改已有节点的共享配置需要 `recreate`，会替换
根盘，请先保留所需数据。Barn 不会退回未经身份校验的宿主路径。

```yaml
vm_shares:
  - host: /absolute/owned/source
    guest: /src
    readonly: true
```

`readonly` 默认为 `true`，每个节点最多八个共享。宿主与客机路径必须是规范绝对路径，
不会展开 `~` 或相对路径。源目录必须已经存在、属于调用者，路径的任何分量都不能是
符号链接，也不能与 `BARN_HOME` 重叠。Linux 上请优先使用真实路径（`realpath /path/to/source`）；**0.9 候选版本**
会在符号链接错误中提示应该填写的真实路径。

同一节点内宿主源目录、客机目标目录均不得相互重叠；不同节点只有全部只读时才允许宿主
源目录重叠。客机目标不能覆盖数据盘挂载点、保留系统路径或登录用户的 `.ssh` 目录。
9p 只适合可信开发文件，不能放 PostgreSQL 数据。
请求可写共享但客机无法写入时，Barn 尝试只读访问并报告限制；修正权限后再次 `up`
即可重试。Barn 不会递归修改宿主文件的属主。

Barn 的 `up`、`start` 会将源目录缺失的影响限制在对应节点，其余选中节点
继续执行。恢复原目录或宿主挂载后，再重试该节点；Barn 不会创建空目录代替。
restart、reload、recreate 会在停止已有节点前校验源目录。

## 名称与地址

节点名依次取 `nodename`、`<pg_cluster>-<pg_seq>`、`node-<IP末段>`，且必须唯一。
名称长度为 1–63，只能包含小写字母、数字和连字符，不能以 `-` 开头或结尾。
非空显式 `nodename` 优先，此时无需使用其他 `pg_cluster`、`pg_seq` 值派生名称。
`vm_alias` 是小写 DNS 风格名称列表，不能与节点名或部署内任何其他别名重复。

所有托管主机必须位于同一个 RFC1918 `/24`：`.1` 属于宿主，`.2`–`.8` 保留，节点使用
`.9`–`.254`。

Guest 内部，固定 IP 网卡就是承载 Inventory 地址的那块网卡（`ip -br addr`）；其名称不是
Barn 契约。

## 漂移

Barn 对每个解析后节点计算哈希。新增主机由 `up` 创建；选中的已停止节点会启动，
运行中同伴保留进程，同时重试未完成的客机初始化。VM 定义变化需要节点级 recreate；删除主机条目只报告、绝不销毁。
deployment 架构、用户或子网变化需要整体重建。`plan`/`up` 会把镜像选择器解析为精确镜像身份，
因此 Catalog 更新后即使 Inventory 文本未改动，也应检查计划。修改用于派生节点名的字段会表现为旧节点
`missing` 加新节点，建议使用稳定、显式的 `nodename`。
