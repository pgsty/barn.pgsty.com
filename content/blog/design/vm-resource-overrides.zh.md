---
title: "VM 规格参数统一设计：命令、短参数、环境变量与根盘"
linkTitle: "VM 规格参数设计"
description: "统一镜像、架构、CPU、内存、缩放和根盘的 CLI、环境变量、清单优先级、命令范围与持久化契约。"
date: 2026-11-11
lastmod: 2026-11-11
weight: 72
categories: [设计]
tags: [CLI, Pigsty, 配置]
icon: fa-solid fa-sliders
---

镜像、架构、CPU、内存、倍数和根盘组成同一组 **VM 规格输入**，统一名称、取值规则与来源追踪。命令声明自己接收哪些规格，以及允许应用哪些变更；解析过程只实现一份。

**状态（2026-11-11）**：本方案已确认，六项 CLI/环境输入、命令接入、清单生成、来源追踪、`SPEC` 显示和根盘原地扩容均已实现，尚未发布。工作区清单默认 1 核 / 2 GiB，已发布 Barn 1.1.0 仍默认 2 核 / 4 GiB。

## 六个参数，一套命名 {#parameters}

| 含义 | 清单字段 | 长参数 | 短参数 | 环境变量 | 候选版默认值 |
|---|---|---|---|---|---|
| 镜像 | `vm_image` | `--image` | `-I` | `BARN_IMAGE` | 内置目录默认 `u24` |
| 架构 | `vm_arch` | `--arch` | `-A` | `BARN_ARCH` | `native` |
| 基础 CPU | `vm_cpu` | `--cpu` | `-C` | `BARN_CPU` | `1` |
| 基础内存 | `vm_mem` | `--mem` | `-M` | `BARN_MEM` | `2048` MiB |
| 资源倍数 | `vm_scale` | `--scale` | `-S` | `BARN_SCALE` | `1` |
| 系统根盘容量 | `vm_disk` | `--disk` | `-D` | `BARN_DISK` | `64` GiB |
{.wide .expand}

大写短参数形成统一的规格参数组，也避开现有小写的 `-c`（CIDR）、`-m`（setup mode）、`-s`（script/source）和 `-d`（dry-run）。六个参数只注册在对应子命令上，不设为根命令的全局参数，因而不会截获 SSH 透传选项。

统一使用 `mem`，对应 `vm_mem` 与 `BARN_MEM`。首版只保留一套规范名称，无需同时增加 `--memory`、`--cpus`、`--root-disk-size` 等同义入口。`--image` 继续接受已有的 family、channel 与版本选择语法，不再新增独立的版本参数；它覆盖清单中的 `vm_image/vm_version` 组合。其他规格覆盖不能顺带修改镜像。

CPU、内存、倍数、根盘和镜像作用于所选节点；架构仍作用于整套部署，不能通过节点选择将部署变成混合架构。

## 优先级与计算顺序 {#base-values}

每个字段独立求值，采用：

```text
显式 CLI > 对应的非空环境变量 > 主机变量 > 最深子组 > 父组 > all.vars > 默认值

有效 CPU  = 选定的 vm_cpu × 选定的 vm_scale
有效内存  = 选定的 vm_mem × 选定的 vm_scale
根盘容量  = 选定的 vm_disk
```

CLI 与环境变量都是覆盖输入，可以替代所选节点的显式主机值。需要保留主机特例时，把默认倍数放在 `all.vars`，或缩小节点选择范围。`--scale 3` 替换清单或环境中的倍数，所有来源只产生一个最终倍数。根盘、数据盘、节点数量和网络不参与缩放。

假定清单为 `vm_cpu: 2`、`vm_mem: 4GiB`、`vm_scale: 2`、`vm_disk: 64`：

| 覆盖输入 | 最终 CPU | 最终内存 | 根盘 |
|---|---:|---:|---:|
| 无 | 4 | 8 GiB | 64 GiB |
| `--scale 3` | 6 | 12 GiB | 64 GiB |
| `BARN_SCALE=3` 加 `--scale 1` | 2 | 4 GiB | 64 GiB |
| `--cpu 4` | 8 | 8 GiB | 64 GiB |
| `--cpu 4 --mem 8GiB --scale 1 --disk 128GiB` | 4 | 8 GiB | 128 GiB |

CPU 与内存在 CLI 中仍表示基础值。这样同一组参数在 YAML、命令行与环境变量中参与相同公式；指定最终规格时使用 `--scale 1`。`plan` 应展示基数、倍数、结果和来源，避免将 `--cpu 4` 误解为无条件指定最终 4 核。来源与计算说明不进入 VM 规格哈希。

CPU 与 scale 只接受正整数，最终 CPU 不超过 256；基础内存至少 512 MiB，并检查容量溢出。CLI 与环境变量使用相同的容量解析器：裸内存整数按 MiB，裸磁盘整数按 GiB；支持 `4G`、`4GiB` 等现有单位语法。推荐示例显式写单位。非法值不自动取整、裁剪或回退默认值。

## 哪些命令支持 {#commands}

| 命令/场景 | 接收规格参数 | 行为与写入边界 |
|---|---|---|
| `init` | 六项全部支持 | 生成清单，将基础值、倍数及其他规格写入新文件；`-o -` 只输出内容 |
| `setup` 生成新模板 | 六项全部支持 | 使用与 `init` 相同的模板求值，先展示准备计划，再按现有流程准备宿主及发布新清单 |
| `setup -f` 或复用已有清单 | 不接收规格覆盖 | 以现有文件准备宿主；显式规格参数报错，VM 规格环境变量不参与 |
| `validate` | 六项全部支持 | 校验整份清单在这些输入下的最终规格，保证将要启动的参数可被同样验证 |
| `plan` | 六项全部支持 | 解释来源、计算资源、检查镜像与根盘约束，并展示变更和后续命令 |
| `up` | 六项全部支持 | 新节点按最终规格创建；已有节点的资源变更需要 `resize`，其他变更需要显式 `recreate` |
| `reload` | 六项全部支持 | 与 `up` 共用期望规格，用于新节点及预检；已有节点不能应用的变更必须在停止 VM 前报错 |
| `recreate` | 六项全部支持 | 使用最终规格显式重建，沿用重建确认、根盘替换及持久盘策略 |
| `resize` | `C/M/S/D`；保留已有 `I/A` 核对 | 应用 CPU/内存变化与根盘原地增长；不改变镜像或架构，不缩盘 |
| `start/stop/restart/status/destroy/purge` | 不接收 | 只使用已应用状态；规格环境变量不影响这些操作 |
| `ssh/exec/logs/provision/hosts/network` 等 | 不接收这组规格输入 | 保留各命令自身的操作参数 |
{.wide .expand}

`validate` 不增加节点选择；其他支持选择的生命周期命令只覆盖所选节点，不选则覆盖全部。首版环境变量范围限于上表的 Linux VM 规格入口。`barn mac` 和独立镜像管理命令继续使用各自的接口；例如 `image pull -A` 选择制品架构，但不自动读取本方案的 VM 环境默认值。

`resize` 目前已暴露 I/A，测试和参考文档也固定了这一接口，因此不应顺手删除它们。保留现有的严格检查：用户可以用它们使期望值与当前镜像、架构匹配，但不能借 resize 改变这两项；其对应环境变量也接受同样的检查。`--disk/-D` 与 `BARN_DISK` 均已接入 resize，只用于根盘增长。

`setup` 的生成与复用两种模式必须在读取规格环境变量前确定。`setup full -C 2` 表示生成指定模板；目标已存在且不同就保留并报冲突。裸 `setup` 发现已有清单后按该文件准备宿主，不能因 shell 中导出了 `BARN_IMAGE` 就意外选择另一镜像。

## SPEC 显示契约 {#spec-display}

表头统一用 `SPEC`，值为有效 CPU 与内存的紧凑表示：`1c2g`、`2c4g`、`8c16g`。`c` 表示 vCPU，`g` 表示 GiB，大小写固定；它展示倍乘后的规格，磁盘与 scale 不拼进这个字符串。1536 MiB 显示 `1.5g`，512 MiB 显示 `0.5g`，不四舍五入；不能整除 MiB 的容量按精确字节数加 `b` 显示。未知资源用 `-`，不猜测默认值。

| 显示位置 | SPEC 的含义 |
|---|---|
| `init` 摘要、`setup` 准备计划、`validate` | 生成或校验后的有效规格 |
| `plan` | 期望规格；有资源变化时为 `2c4g → 4c8g` |
| `status`、生命周期完成结果 | 已应用的 CPU/内存规格 |
| 生命周期动态进度 | 当前操作的目标规格；后续状态事件可更新为已应用资源 |

`plan/setup/validate/status` 的根盘放在单独的 `ROOT` 列，根盘变化也显示旧值与目标值；`init` 摘要单列 root。非动态的启动结果列出各节点 SPEC。倍数不为 1 时增加基数、倍数、结果和来源说明，`--verbose` 也显示倍数为 1 的计算。JSON 保留数值 CPU、字节容量与结构化的 `resources` 解释，不用缩写替代数值字段。格式化与说明不进入 VM 规格哈希，也不作为输入语法。

## 根盘参数与原地扩容 {#root-disk}

`--disk/-D` 对应 `vm_disk`，表示系统根盘的绝对目标容量。Barn 当前还有默认挂载到 `/data` 的 128 GiB 数据盘，本次不改变其语义，也不引入多盘 CLI。`-D 128GiB -S 3` 的根盘仍是 128 GiB。

创建与显式重建时，容量必须为正且不小于所选基础镜像的虚拟磁盘大小，不能使用下载文件大小代替这个下限。计划阶段可使用已验签目录的 `virtual_size` 检查下限，创建时再核对实际镜像；无需为了只读校验下载整个镜像。`up` 发现已有根盘容量不同，应展示漂移，不直接调用磁盘工具修改它。若选择 `recreate` 应用容量变化，其操作会替换原根盘及非持久数据盘，属于显式重建，不能把它描述为保留数据的扩容。

已有根盘原地扩容使用 `barn resize -D 128GiB meta`。这是绝对目标值，重复执行到相同容量不再修改磁盘；不接受 `+64GiB` 这样的增量语法，也不提供原地缩盘。

扩容需要分别验证磁盘镜像、客机分区和文件系统。QEMU 明确要求镜像增长后继续在客机内扩展分区/文件系统，并禁止用离线 `qemu-img` 修改正在使用的镜像。首版原地扩容因此优先采用可恢复的停机流程，在线 QMP 扩容后续再评估。[QEMU 磁盘工具文档](https://www.qemu.org/docs/master/tools/qemu-img.html)

Barn 创建客机时已写入 `growpart` 与 `resize_rootfs: true`。cloud-init 将这两个模块的频率定义为 `always`，但它们可以被关闭，分区布局也有限制；不能仅凭 VM 已重启就报告根盘扩容完成。[cloud-init Growpart](https://docs.cloud-init.io/en/latest/reference/modules.html#growpart)、[Resizefs](https://docs.cloud-init.io/en/latest/reference/modules.html#resizefs)

实现以 `preflight → image → guest → verified` 记录扩容进度，磁盘改动前持久化目标。失败后重复相同目标继续执行，不用缩盘回滚。首版支持 512 字节逻辑扇区、GPT 或主 MBR 分区中位于磁盘末端的普通 ext4/XFS 根分区；LVM、加密根设备及其他布局在修改镜像前拒绝。原本停机的 VM 会临时启动完成探测与扩展，成功后恢复停机。恢复机制和真机测量见 [根盘扩容验收](/zh/blog/design/root-disk-growth/)。

## 环境变量的规则 {#environment}

将六项规格放进一套来源可见的解析流程后，环境变量值得支持：它们便于 CI 矩阵和临时 shell 调用，同时保持与 CLI 一样的覆盖语义。它们是本次命令的覆盖输入，因此优先于主机级清单值；需要保留节点特例的全局默认值应写在 `all.vars`。

调用方式：

```bash
BARN_IMAGE=u26 BARN_SCALE=2 barn plan -f pigsty.yml
BARN_IMAGE=u26 BARN_SCALE=2 barn up -f pigsty.yml
BARN_SCALE=2 barn plan -f pigsty.yml -S 3  # 本次最终倍数为 3
```

环境变量只在命令接受该字段时解析。`BARN_CPU=bad barn status` 不应失败；同样的环境执行 `up` 时必须给出命名明确的错误。CLI 已覆盖某个字段时，不再校验被遮蔽的环境值，例如 `BARN_CPU=bad barn up -C 2` 使用 2。

空白或空字符串环境值视为未设置，便于单次清除继承值：`BARN_SCALE= barn plan` 使用清单倍数。显式 `--scale=0`、`--scale=` 或非法的非空环境值仍需报错。帮助与版本命令不受规格环境错误影响。首版不自动读取 `.env`、全局偏好文件或历史参数，也不新增名称含糊的 `--ignore-env`；系统自带的 `env -u BARN_SCALE` 可以明确清除某项输入。

`plan/validate/up` 等应在规格说明中标明来源，例如 `scale: 3 (env BARN_SCALE)`；结构化输出提供同样信息，不输出其他环境内容。后续应用或失败重试命令应将本次生效的环境覆盖转为显式 flags，保留 `-f`、节点选择与参数值。环境变化本身不成为隐藏的持久化设置。

将 `BARN_IMAGE` 用在混合镜像构建清单上，会像 `--image` 一样覆盖所有选中节点的镜像。保留构建矩阵时不设置此覆盖，镜像依旧来自逐节点声明。`BARN_HOME`、`BARN_REPO`、输出格式和调试等已有环境变量保持各自契约，不纳入资源缩放或本次规格表。

## 清单、应用状态与持久化 {#persistence}

配置生成和运行时覆盖分开处理：

- `init`、生成模板的 `setup` 将六项选定值明确写入 `all.vars`，使默认规格也能从文件直接看见。记录基础 CPU/内存与倍数，不把倍乘结果回写成基数。`init` 默认保留已有文件，只有显式 `--force` 才替换。
- 第一次交互式 `up` 若确实需要生成新清单，也复用这个生成流程，把本次选定规格写进新文件。下一次普通 `up` 可以读取相同的选择。
- 已有清单上的 `up/resize/recreate` 只覆盖本次期望值，不改写 YAML。成功后应用状态记录实际最终规格；再次读取原清单会显示差异，`start` 等则保持已应用规格。

例如下面的命令生成 4 节点配置，每节点 4 核 / 8 GiB，根盘 128 GiB：

```bash
barn init full -I u26 -A arm64 -C 2 -M 4GiB -S 2 -D 128GiB
barn plan -f barn.yml
barn up -f barn.yml
```

`setup <模板>` 判断已有文件能否复用时，除了最终 VM 规格，还应比较归一化后的基础值与倍数。`2×2` 和 `4×1` 虽然得到相同 CPU，但后续 `--scale 3` 的结果不同，不能声称这两份模板设置相同并静默复用。VM 漂移摘要仍只比较最终规格，因此两种写法在不改变最终资源时无需重启。

当前应用状态没有保留原始基数和倍数。如果找不到清单，显式 CLI 或环境中的 scale 都应要求提供 `-f`，不能再次倍乘已经缩放的应用状态。仅指定 CPU/内存时，可以在应用状态上以隐式倍数 1 设置绝对资源；其他规格沿用应用状态。内部重试从同一份原始输入重新求值，不能对已计算结果再叠加覆盖。

## Pigsty 接入 {#pigsty}

Pigsty Make 入口只把用户明确提供的 `IMAGE/ARCH/CPU/MEM/SCALE/DISK` 转为对应 CLI 参数，未提供则省略；不要在 Make 中再次倍乘，也不要自动注入 `SCALE=1`。用户提供的 Make 参数转为 flags 后优先于 `BARN_*` 环境变量。

普通同构 profile 的默认镜像可以由 Pigsty 生成器写为 `u26`，Barn 自身默认仍是 `u24`。构建 profile 保留逐节点 `vm_image`；不得为它们自动追加统一 `-I`。需要保存 profile 选择时，在生成阶段落入清单；普通生命周期命令沿用上述临时覆盖契约。

DNS 已拆成独立设计，不将 hosts 发布或服务域名混入这六个规格参数。

## 实现组织与交付顺序 {#implementation}

建议用一张小型参数表描述名称、短参数、环境名、解析方式和作用范围，用一份带“是否提供、值、来源”的输入结构传递规格。命令通过能力表声明可接收字段、可执行变更与是否生成清单。无需引入通用配置框架，也不要让各命令自行读取 `os.Getenv` 或重复注册一套相似参数。

统一流程为：选择命令模式与输入来源 → 收集允许的 CLI/环境覆盖 → 解析清单继承 → 按节点叠加对应字段 → 一次性计算有效规格 → 校验 → 计划/执行。保留严格 `vm_*` 命名空间；清单自身的语法、字段类型和继承冲突仍须有效，CLI 覆盖不能绕过未知字段、损坏 YAML 和选择器错误。倍乘后的 CPU 上限与内存溢出在覆盖完成后检查。

工作区使用 [resources.go](https://github.com/pgsty/barn/blob/main/internal/config/resources.go) 保存基础值、倍率与来源，[vm_inputs.go](https://github.com/pgsty/barn/blob/main/cmd/barn/vm_inputs.go) 统一注册六项输入并解析允许的环境变量。[inventory.go](https://github.com/pgsty/barn/blob/main/internal/config/inventory.go) 在倍乘前应用选中节点的资源覆盖；镜像和架构保留现有覆盖语义。`init/setup` 共用模板生成器，`up` 内部准备宿主时保留已求出的规格。[root_resize.go](https://github.com/pgsty/barn/blob/main/internal/private/root_resize.go) 复用 `disk.Manager.Grow`，在部署锁内编排停机扩盘、客机验证和失败恢复。

| 阶段 | 交付内容 | 验收重点 |
|---|---|---|
| A：统一规格输入 | 六项字段、C/M/S/D 长短参数、对应环境变量、优先级、来源与命令能力表；不做既有根盘扩容 | 参数组合、非法输入、环境遮蔽、作用范围及同义输出；已有 I/A 行为回归 |
| B：命令接入 | init、setup、validate、plan、up、reload、recreate；resize 接入 CPU/内存/scale | 新清单写入基数；旧文件不改写；所选节点范围；重试幂等；计划与应用使用同一规格 |
| C：根盘原地增长 | resize 的 D 参数、变化分类、停机扩盘、客机扩展、部分失败恢复 | 不缩盘、不丢原数据、身份保持、真实容量验证、运行/停机状态和重复执行 |
{.wide .expand}

A、B、C 与 SPEC 显示均已实现；根盘扩容经过独立的 ext4/XFS 真机验收。源码还应覆盖 [模板生成](https://github.com/pgsty/barn/blob/main/internal/config/template.go)、[setup](https://github.com/pgsty/barn/blob/main/cmd/barn/setup.go)、[resize 边界](https://github.com/pgsty/barn/blob/main/internal/private/resize.go) 与 [根盘创建](https://github.com/pgsty/barn/blob/main/internal/disk/disk.go) 的回归。

本轮验收覆盖 [资源解析与边界](https://github.com/pgsty/barn/blob/main/internal/config/resources_test.go)、[CLI/环境优先级、模板复用、重试及 SPEC](https://github.com/pgsty/barn/blob/main/cmd/barn/vm_inputs_test.go)，并运行 `make build`、源码 `make check` 和站点 `make check`。构建与只读 CLI 验收使用临时 `BARN_HOME`；没有对现有 VM 或宿主网络执行变更。根盘扩容还覆盖 [故障边界测试](https://github.com/pgsty/barn/blob/main/internal/private/root_resize_test.go) 与独立临时部署的 [真机验收](/zh/blog/design/root-disk-growth/)。当前契约见 [规格覆盖](/zh/docs/reference/configuration/#specification-overrides) 与 [SPEC 显示](/zh/docs/reference/cli/#vm-specification-flags)。
