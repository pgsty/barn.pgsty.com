---
title: 配置
description: Barn 读取的 Pigsty 主机清单字段、默认值与节点级漂移行为。
weight: 10
icon: fa-solid fa-file-code
aliases: [/docs/concepts/project-model/]
---

本参考对应 Barn 1.1.0，包含命令行镜像与架构覆盖。请通过 `barn version` 和命令的 `--help` 核对已安装版本。

## 发现顺序 {#discovery}

Barn 先检查命令行显式传入的 `-f` 路径；未指定 `-f` 时，依次在当前工作目录查找 `barn.yml`、`barn.yaml`、`pigsty.yml` 与 `pigsty.yaml`。四种文件名均使用同一种兼容 Pigsty 的 YAML 主机清单格式。

当前目录没有任何清单文件、但 `BARN_HOME`（默认 `~/.barn`）中已存在部署时，`plan`、`up`、`reload`、`recreate` 与 `resize` 会直接使用已应用的部署规格；`validate` 则始终要求磁盘上存在清单文件。配置文件须解析为不超过 4 MiB 的普通文件，支持符号链接；共享源的相对路径以清单真实文件所在目录为基准。Barn 会采用按顺序找到的第一个候选文件；若该文件存在语法或规则错误，Barn 会直接报错退出，不会继续尝试后续文件名。

已应用的部署状态统一保存在 `BARN_HOME` 中，重命名清单文件不会改变部署；跨工作目录操作同一套部署时，请将 `BARN_HOME` 设为绝对路径。

## 完整配置示例 {#a-complete-inventory}

`barn init [meta|dual|trio|full]` 分别生成 1、2、3、4 节点的拓扑模板。`meta` 使用 `.10`，更大的模板依次增加 `.11`（`node-1`）、`.12`（`node-2`）与 `.13`（`node-3`）；这些模板只定义虚拟机拓扑，上层 Pigsty 服务角色由你的 Ansible 剧本决定。使用 `--cidr` 可在保留末位主机号的前提下更换 `/24` 网段；运行 `barn init full -o -` 可将模板直接打印到标准输出而不落盘。

```yaml {title="barn.yml"}
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

上面的清单定义了两个托管节点，并以 `meta` 作为控制节点。将其保存为 `barn.yml` 后，可在不启动虚拟机的情况下校验配置并预览计划：

```bash
barn validate -f barn.yml
barn --json validate -f barn.yml
barn plan -f barn.yml
```

`validate` 只检查 YAML 语法、字段规则与镜像目录引用（传入 `--repo` 可改用其他仓库的目录校验），不会启动虚拟机或下载镜像。JSON 输出包含 `valid`、`source`、`spec_hash` 与 `resolved`；若本地镜像目录无法读取，结果会附带警告并跳过镜像选择器校验。真正执行 `up` 时，Barn 会进一步校验 `local-*` 导入镜像的缓存字节、宿主资源、共享目录、网络与客机 SSH 就绪状态。

## Barn 读取什么 {#what-barn-reads}

清单必须包含顶层 `all:` 分组，Barn 会遍历其中的 `hosts` 与嵌套 `children` 映射。Barn 直接解析静态 YAML，不执行 Ansible 动态清单插件或 Jinja 表达式，也不加载外部 `group_vars` 或 `host_vars` 文件。同一个 IPv4 地址出现在多个分组中时，Barn 会合并各组继承的变量，将其视为同一个节点。

Barn 只读取节点 IPv4 键、`nodename`、`admin_ip`、`pg_cluster`、`pg_seq`、`node_admin_username`、`node_admin_uid` 以及下表列出的 `vm_*` 变量：

- **控制节点**：Barn 从 `all.vars` 读取 `admin_ip`。未设置或未命中任何托管节点时，Barn 按 YAML 遍历顺序（先读当前组的 `hosts`，再递归读取 `children`）选择第一个托管节点。建议显式设置 `admin_ip`，以免调整分组顺序时改变控制节点。
- **登录账号**：所有节点必须使用同一个匹配 `[a-z_][a-z0-9_-]{0,31}` 的登录用户名。使用默认用户 `dba` 时，若显式设置 `node_admin_uid`，其值必须为 `88`；使用自定义用户名时，Barn 只检查 `node_admin_uid` 是否为整数，客机内实际 UID 由创建账号时自动分配。
- **上层 Pigsty 字段**：`pg_role`、`pg_version`、`repo_*`、`node_packages` 等不由 Barn 消费的字段会被安全忽略，修改它们不会触发虚拟机配置漂移。
- **继承与严格校验**：变量按 `all.vars` → 嵌套 `children.<group>.vars` → 节点变量的顺序覆盖。节点上声明的 `vm_disks` 等列表会整体替换组级列表，不会追加合并。同级分组对同一节点给出不同值时，必须在节点层级显式覆盖以消除冲突。未知的 `vm_*` 字段、错误类型、Jinja 表达式、重复 YAML 键以及多文档 YAML 流都会直接报错；报错时会指出违反的规则、问题值与行号，并提示拼写相近的 `vm_*` 字段名。支持 YAML 锚点与 `<<` 合并键（显式键优先，合并序列中排在前面的映射次之）。
- **跳过节点**：`vm_skip: true` 的外部主机可使用主机名或 IPv6 键，不参与推导托管 `/24`；清单仍须保留一个托管节点。已部署节点被跳过时，`plan` 会标记为 `missing`，不会自动销毁。

## VM 变量 {#vm-variables}

| 变量 | 默认值 | 含义 |
|---|---|---|
| `vm_skip` | `false` | 跳过该物理机或外部主机，不为它创建虚拟机 |
| `vm_image` | `u24` | 镜像系列、`:channel` 通道引用或 `image@version` 版本选择器 |
| `vm_version` | 未设置 | 匹配该数值前缀的最新版本，例如 `9` 或 `9.7` |
| `vm_arch` | `native` | 部署级客机架构，默认跟随宿主；可显式指定 `amd64` 或 `arm64` |
| `vm_cpu` | `2` | vCPU 核数（`1`–`256`） |
| `vm_mem` | `4096` | 内存容量：裸整数按 MiB 计，也支持 `8GiB` 等带单位字符串（最低 `512MiB`） |
| `vm_disk` | `64` | 根盘容量：裸整数按 GiB 计，也支持 `64GiB` 等带单位字符串 |
| `vm_disks` | `[{path: /data}]` | 额外数据盘列表（默认挂载一块 128 GiB 非持久盘到 `/data`） |
| `vm_alias` | `[]` | 写入客机 `/etc/hosts`、SSH 配置及可选宿主 `/etc/hosts` 的附加别名 |
| `vm_shares` | `[]` | QEMU 9p 宿主目录共享（Linux 与 macOS 宿主） |
{.wide .expand}

空节点条目（如 `10.10.10.10: {}`）即可使用默认参数定义一台完整虚拟机。不再另设 20 节点上限；托管节点须使用同一 `/24` 内互不重复的可用地址。

裸整数在 `vm_mem` 中表示 MiB，在磁盘容量中表示 GiB。显式容量字符串接受正整数和不区分大小写的单位，例如 `8G`、`512m`、`4gib`、`64GB`。`K/M/G/T` 与 `KiB/MiB/GiB/TiB` 使用二进制倍率，`KB/MB/GB/TB` 保留十进制倍率。小数 `1.5GiB` 和无单位字符串 `"8192"` 仍不接受。`up` 仍检查根盘不小于基础镜像虚拟大小。

省略 `vm_image` 时，Barn 始终按二进制内置目录选择 `u24`（Ubuntu 24.04），自定义仓库中的 `defaults.image` 不会改写未设置 `vm_image` 的清单。此外，Barn 在解析清单时会先按内置目录将 `ubuntu` 等内置别名归一化为 `u24`；使用自定义仓库时，请在 `vm_image` 中直接填写规范系列名，不要将内置别名改指其他系列。

需要把镜像系列与版本前缀分开书写时，可配合使用 `vm_version`：

```yaml {title="barn.yml"}
vm_image: el9
vm_version: "9.8"
```

若镜像目录中存在完全一致的版本号，Barn 优先精确匹配；否则按点号分段匹配版本前缀，并按整数大小选择匹配的最高版本（`9.8` 匹配最新的 `9.8.*` 构建，`9` 匹配最新的 `9.x` 版本，且 `9.10` 排在 `9.9` 之后）。`vm_version` 不能与已包含 `:channel` 或 `@version` 的 `vm_image` 同时使用。

## 镜像与架构覆盖 {#image-and-architecture}

默认客机架构与宿主一致：Apple Silicon 使用 `arm64`，Intel/AMD 宿主使用 `amd64`。只有清单或命令行显式指定其他架构时才切换。优先级为 **`--arch/-A` → 清单 `vm_arch` → `native`（宿主架构）**；`-A native` 可以覆盖清单中的固定架构，恢复跟随宿主。

| 架构值 | 别名 | 含义 |
|---|---|---|
| `native` | — | 跟随当前宿主架构，也是未设置时的默认值 |
| `amd64` | `x86_64`、`x64` | 固定使用 x86-64 客机 |
| `arm64` | `aarch64`、`a64` | 固定使用 ARM64 客机 |
{.wide .expand}

`vm_arch` 是整套部署共用的属性，请在 `all.vars` 中统一定义。每个托管节点必须解析为同一架构，不能用节点变量或节点选择器混合架构。

`--image/-I` 覆盖所选节点的 `vm_image` 与 `vm_version`，不改变架构。镜像目录必须提供目标架构的变体，否则报错；Barn 不会因为镜像缺少该变体而切换架构。

```bash
barn plan -I u24                 # 使用 Ubuntu 24.04，架构仍遵循清单或宿主默认值
barn up -I u24 -A amd64          # 本次使用 amd64 Ubuntu 24.04
barn plan -A native              # 覆盖清单架构，按宿主架构预览
barn init full -I u24 -A arm64   # 将镜像与架构写入新清单
```

`up`、`plan`、`reload`、`recreate`、`resize` 和 `validate` 的覆盖只对本次期望配置生效，不改写清单。要长期保留选择，请设置 `all.vars.vm_arch`、相应节点或组的 `vm_image`，并移除被替代的 `vm_version`；`init` 与生成模板的 `setup` 会直接写入这些选择。`setup` 的 `-I/-A` 不能用于已有清单。

没有清单文件时，生命周期命令沿用已保存的部署规格，再应用显式覆盖。`start` 和 `restart` 始终使用已应用状态。已有 VM 的架构不会因省略 `-A` 或修改清单而自动改变：`up` 会报告漂移，实际切换架构需要选择全部已有节点执行 `recreate`。`resize` 虽接受覆盖用于核对期望配置，仍只允许修改 CPU 与内存。

客机与宿主架构不同时使用 QEMU TCG。Linux 宿主的 `barn setup` 默认只安装本机架构的 QEMU；运行跨架构客机前，需安装对应的 `qemu-system-*` 与 UEFI 固件。加速方式与镜像例外见[运行时策略](../images/#runtime-policy)。

## 数据盘 {#data-disks}

```yaml {title="barn.yml"}
vm_disks:
  - path: /data
    size: 128
    fs: auto
    persistent: false
```

`vm_disks` 列表中的每一项定义一块附加虚拟块设备：

- **`path`**：绝对挂载路径，自动规范化，支持空格、中文和 shell 标点。简单路径保留原有磁盘标识，其他路径生成稳定摘要标识。同一节点内标识须唯一，系统目录和重叠的挂载路径仍会被拒绝。
- **`size`**：磁盘容量，默认 `128`（128 GiB），支持 GiB 整数或显式容量字符串。
- **`fs`**：文件系统类型，支持 `auto`（默认）、`xfs` 或 `ext4`。对于空白的 `auto` 磁盘，客机具备 `mkfs.xfs` 时格式化为 XFS，否则使用 ext4；显式指定 `xfs` 或 `ext4` 时严格使用对应工具，不会降级回退。健康的已有文件系统会直接挂载复用。
- **`persistent`**：设为 `true` 时，普通 `barn destroy` 与 `barn recreate` 会在宿主上保留该磁盘镜像；只要磁盘标识与声明保持兼容，重建后的节点会自动重新挂载它。设为 `vm_disks: []` 则不挂载任何额外数据盘。

> [!IMPORTANT]
> **数据盘定位于可丢弃的测试存储。** 执行 `up` 时，Barn 会按配置的 `fs` 格式化空白数据盘。对于已有的 ext4 或 XFS 文件系统（包括 `persistent: true` 的持久盘），只有客机内的只读检查（`e2fsck -fn` 或 `xfs_repair -n`）报告可识别的损坏时才会重置，并在 `nodes[].repairs` 中记录。带分区表、签名缺少文件系统 UUID、其他文件系统类型、客机工具不支持的文件系统特性或检查工具未知失败的磁盘会保留数据，并在 `nodes[].warnings` 中给出警告；设备暂缺、探测命令报错、挂载忙碌或宿主 I/O 故障同样只报告警告。根盘与宿主共享目录绝不会被格式化。

## 目录共享 {#shares}

```yaml {title="barn.yml"}
vm_shares:
  - host: ./src
    guest: /src
    readonly: true
```

`vm_shares` 通过 QEMU Virtio-9p 将 Linux 或 macOS 宿主目录挂载到 Linux 客机，默认 `readonly: true`。宿主 QEMU 与客机内核须支持 9p。不再另设 8 个共享的上限，实际受后端设备能力约束。原生 macOS 客机使用 `barn mac --share` 的 VirtioFS。

共享源按当前用户的实际文件系统权限访问：

- `host` 支持绝对路径、`~/`、相对清单目录的路径与目录符号链接。`guest` 须为绝对路径并自动规范化，接受空格、中文和 shell 标点，不接受控制字符。
- 解析后的宿主源须已存在、当前用户可访问且不与 `BARN_HOME` 重叠，无须归当前用户所有。
- 宿主源可以重叠，多个客机可以同时读写，由用户协调并发写入。同一客机内的挂载目标仍不能重叠。
- `guest` 路径不能覆盖数据盘挂载点、系统保留目录或登录用户的 `.ssh` 目录。9p 共享适合挂载开发源码与构建产物，请勿用于存放 PostgreSQL 数据目录。
- 若请求了可写共享（`readonly: false`）但客机用户无权写入，Barn 会自动降级为只读挂载并报告警告，而不会递归修改宿主文件属主；调整宿主目录权限后重新执行 `barn up` 即可恢复可写挂载。
- 修改已有节点的 `vm_shares` 需要执行 `barn recreate`。`up` 或 `start` 期间若某个节点的共享源目录缺失，只会使该节点失败，其余节点照常启动；`restart`、`reload` 与 `recreate` 则会在停止现有虚拟机前预先校验所有共享源目录。

## 名称与地址 {#names-and-addresses}

Barn 依次按显式 `nodename`、`<pg_cluster>-<pg_seq>`、`node-<IP末段>` 确定节点名称。节点名称在部署内必须唯一，长度为 1–63 个字符，只能包含小写字母、数字与连字符，且不能以 `-` 开头或结尾。`vm_alias` 接受额外的小写 DNS 名称（允许包含点号），且不能与任何节点名或其他别名重复。

同一套部署中的所有托管节点必须位于同一个 RFC1918 `/24` 私有网段内：`.1` 固定为宿主网关，`.2`–`.8` 保留，节点使用 `.9`–`.254`。客机内部由固定 IP 网卡承载清单地址（可通过 `ip -br addr` 查看）。

## 漂移 {#drift}

显式节点选择只应用所选节点的改动：`plan node-1`、`up node-1`、`reload node-1`、`recreate node-1` 和 `resize node-1` 保留其他节点的已应用配置，即使清单中已修改或省略它们。整份清单仍须通过语法解析，未创建且未选中的节点不要求解析镜像。与已应用节点冲突的地址、别名、控制节点角色或部署公共设置仍会报错。

Barn 为每个解析后的节点计算规格哈希：

- `barn up` 会创建新增节点、启动已停止节点，并在不重启 QEMU 进程的前提下重试运行中节点尚未完成的客机初始化步骤。
- 修改节点的 CPU 或内存后使用 `barn resize <node>`，该操作保留虚拟机身份与磁盘。修改镜像、磁盘、共享目录或其他虚拟机定义后，需要执行 `barn recreate <node>` 才能生效。从清单中删去节点（或设为 `vm_skip: true`）只会在 `plan` 中将其标记为 `missing`，Barn 绝不会自动销毁已有节点。
- 修改部署级属性（`vm_arch`、登录用户名或 `/24` 子网）需要重建整套部署。
- 由于 `plan` 与 `up` 会将镜像通道和版本前缀解析为具体的镜像摘要，执行 `barn update` 更新镜像目录后，即便 `barn.yml` 原文未改，也可能产生镜像版本漂移。建议为每个节点显式固定 `nodename`，避免修改 `pg_cluster` 时导致旧节点变成 `missing` 并额外派生出新节点。
