---
title: "Pigsty 使用 Barn 时的宿主 DNS / 域名解析方案"
linkTitle: "Pigsty 宿主 DNS"
description: "以显式 hosts 同步为起点，明确 Pigsty 域名语义、来源替换保护，以及 macOS 与 Linux 的可选按域转发升级路径。"
date: 2026-11-10
lastmod: 2026-11-11
weight: 73
categories: [设计]
tags: [Pigsty, DNS, Networking]
icon: fa-solid fa-network-wired
---

> [!NOTE]
> **2026-11-11 范围收敛**：首期交付改为 [固定核心域名与 Pigsty CA 信任](/zh/blog/design/pigsty-host-setup/)。本页保留更广的导出器和解析器研究；通用清单与 split DNS 属于可选扩展，不作为固定配置的实现前提。

**当前推荐先做显式启用的 hosts 管理。** Pigsty 计算名称和服务目标，Barn 通过现有 helper 预览并安装一份中性的地址／名称快照。对于地址固定的 Linux 实验环境，这项功能值得做：宿主可以直接打开 portal，通过节点名连接机器，通过集群名或 VIP 名访问数据库。静态地址让重复同步成本很低，记录不变就无需特权操作。**但每次真正修改系统 hosts，包括删除记录，仍需 root 权限。** setup 不会永久授权以后的更新；sudo 缓存或免密策略省掉的是密码提示，并没有消除特权。现阶段保留按次授权，等到客机 DNS 入口稳定、命名空间完整后，再增加可选的后缀转发。宿主常驻 DNS 服务则需要前两种方案无法满足的明确需求。

**状态**：设计日期为 **2026-11-10**；取证与综合写作跨至 **2026-11-11，Asia/Shanghai**。核查的 Barn `v1.1.0` 标签源码 [b2cc8da](https://github.com/pgsty/barn/tree/b2cc8da8983e710255d504bf26bf5d7b3f182790) 已支持从已应用节点状态发布 hosts。`vm_hosts`、`hosts install -f`、大小写归一化及 Pigsty `bin/sandbox-dns` 是上述日期核查的 **未提交、未发布原型**。下文的来源保护、导出模式、事务增强和 DNS 适配器均为 **提案**。本轮没有验证发布二进制或真实平台行为。[迁移文章](/zh/blog/design/pigsty-barn-migration/) 提供整体背景；本文独立定义 DNS 部分的实施方案。

## 先选择成本最低且足够有用的发布方式 {#decision}

| 方案 | 覆盖范围与日常操作 | 权限与故障表现 | 决定 |
|---|---|---|---|
| 管理 hosts | 有限的短名与 FQDN；显式同步完整快照；客机停止后仍可解析，但连接会失败 | 每次实际写入／删除需要特权；相同快照无操作；无需常驻服务 | **首选实现**，始终显式启用 |
| 按后缀转发至客机 DNS | 只覆盖约定域内客机实际提供的记录；客机数据更新无需重写宿主路由 | 安装路由、修改入口与卸载需要特权；路由不变时，更新记录无需宿主特权；依赖客机 DNS | 可选的下一步；分别实现 macOS/Linux 适配器，并处理短名 |
| 宿主本机 DNS daemon | 可支持高频记录变更、通配符及更多 RR 类型；用户数据可独立于固定系统路由更新 | 服务／路由的安装和变更需要特权；服务身份、端口、启动、崩溃与升级都需要维护 | 等实测需求足以承担维护成本后再做 |
| 零自动配置／手工模式 | 使用 IP、已有 DNS，或经审查的应用／系统覆盖配置 | Barn 不修改系统状态；用户负责集成与清理 | 始终保留；普通 setup 和 VM 生命周期默认遵循这一策略 |
{.wide .expand}

不做自动配置时，Barn 的 SSH 别名和直接 IP 访问仍然可用。但多个 portal 的 Host／TLS 名称、浏览器 URL 和应用设置仍需要已有 DNS 或手工覆盖配置。单个应用的覆盖配置不能提供系统级解析，手工复制的映射也会随着清单变更而过期。

产品边界仍是一名用户的一套 Linux 部署、一种主机清单格式，以及宿主上唯一的 Barn 管理块。更换 `BARN_HOME` 不会产生独立的 hosts 命名空间。Pigsty 负责 portal、PostgreSQL、VIP 和 MinIO 的含义；Barn 不发现 Patroni leader，也不理解 Pigsty 角色。这符合 [Barn 开发契约](https://github.com/pgsty/barn/blob/b2cc8da8983e710255d504bf26bf5d7b3f182790/CONTRIBUTING.md)。

```mermaid
flowchart LR
  I["Pigsty 清单与上下文"] --> P["Pigsty 规则与所选视图"]
  P --> S["all.hosts + vm_hosts 快照"]
  S --> B["Barn 离线计划"]
  B --> H["特权 helper"]
  H --> F["唯一 hosts 管理块"]
```

## 先定义名称与视图，再选择解析器 {#names-and-views}

建议默认导出 **宿主访问意图**：合并所选 portal 入口名称、节点身份、显式记录及服务别名，形成有明确用途的集合。它可以有意包含客机 dnsmasq 中没有的名称。导出报告保留 `vm-identity`、`guest-hosts`、`infra-dns`、`portal-access`、`service-access` 分类，以及各条记录的来源、视图和目标类型。`guest-dns` 视图则按任务条件复现所选 infra 的 DNS 输出。共享计算规则需要统一身份与目标地址的推导，同时允许不同输出策略。

以下表格统一规定名称映射。中间一列描述已审计的 Pigsty 行为，最后一列是拟议的宿主访问发布策略。

| 名称来源 | 已核查的含义与目标 | 宿主访问发布策略 |
|---|---|---|
| Barn 节点身份与 `vm_alias` | 优先 `nodename`，其次 `pg_cluster-pg_seq`，最后 `node-末段`；别名指向节点地址 | 发布解析后的 VM 名称／别名。新增服务名使用 `vm_hosts`，避免改变 VM 规格。[Barn 清单解析](https://github.com/pgsty/barn/blob/b2cc8da8983e710255d504bf26bf5d7b3f182790/internal/config/inventory.go) |
| `node_default_etc_hosts`、`node_etc_hosts` | 客机 hosts 记录，受 `node_write_etc_hosts` 控制；使用该节点有效的 `${admin_ip}` | 将所选视图中启用的记录归为 `guest-hosts`，逐物理行解析。节点名称交换属于另一套任务上下文。[Node DNS 任务](https://github.com/pgsty/pigsty/blob/1ee6597dd806605b600e90cf01948277748b45f3/roles/node/tasks/dns.yml) |
| `dns_records` | 写入 infra hosts 数据文件，并替换 `${admin_ip}`；`dns_enabled` 控制服务启动，不控制所有文件生成，也不会自动移除已运行的服务 | 按期望配置发布显式记录，并标明来源；不能从开关推断 DNS 是否运行。客机 dnsmasq 使用 `no-hosts`，不会自动提供客机 `/etc/hosts` 中的记录。[Infra 任务](https://github.com/pgsty/pigsty/blob/1ee6597dd806605b600e90cf01948277748b45f3/roles/infra/tasks/dns.yml)、[dnsmasq 模板](https://github.com/pgsty/pigsty/blob/1ee6597dd806605b600e90cf01948277748b45f3/roles/infra/templates/dns/dnsmasq.conf) |
| `infra_portal.*.domain/domains` | Nginx 名称，不会自动成为 DNS 记录。任务要求非空 `domain`；标准 home/path/endpoint 模板支持别名 | 将启用的虚拟主机映射到明确选定的入口，通常是其有效 `admin_ip`。不能使用可能指向 loopback 的后端 `endpoint`。无法解释的自定义模板应拒绝；只有 `domains`、被任务跳过的条目不发布，并给出诊断。[Portal 任务](https://github.com/pgsty/pigsty/blob/1ee6597dd806605b600e90cf01948277748b45f3/roles/infra/tasks/nginx.yml) |
| PG 实例 `pg_cluster-pg_seq` | 指向清单地址；PG DNS 任务受 PG 节点的 `dns_enabled` 控制。实例名不附加 `pg_dns_suffix` | 有效实例别名作为 `service-access` 发布，即使客机 DNS 被禁用，也可明确标注为宿主便利别名；不能据此声称客机已发布该 DNS 记录。[PG DNS 任务](https://github.com/pgsty/pigsty/blob/1ee6597dd806605b600e90cf01948277748b45f3/roles/pgsql/tasks/dns.yml) |
| PG 集群 `pg_cluster + pg_dns_suffix` | 直接拼接后缀，默认后缀为空。`auto`：启用的 PG VIP，否则取声明的 primary；`primary`：声明的 primary；`vip`：启用的 VIP，未启用则无地址；`none`：无地址；显式 IP：配置的目标 | 按这些规则生成 `service-access`，并标明 DNS 禁用时的便利别名。需要 primary 时必须恰好有一个。拒绝显式 CIDR 目标：当前角色保留掩码，原型却静默剥离；PG VIP 分支本身则明确会剥离 VIP 掩码。[PG 默认值](https://github.com/pgsty/pigsty/blob/1ee6597dd806605b600e90cf01948277748b45f3/roles/pgsql/defaults/main.yml)、[PG 身份](https://github.com/pgsty/pigsty/blob/1ee6597dd806605b600e90cf01948277748b45f3/roles/pg_id/tasks/main.yml) |
| 节点 VIP `node_cluster + vip_dns_suffix` | 启用的 `vip_address`，独立于 PG VIP；依赖有效节点身份规则 | 发布校验后的裸 VIP 地址。当前 DNS 任务原样输出该值，因此在角色与导出器共同修正前，拒绝这里的 CIDR 输入。[Node monitor 任务](https://github.com/pgsty/pigsty/blob/1ee6597dd806605b600e90cf01948277748b45f3/roles/node_monitor/tasks/main.yml) |
| MinIO 成员名称 | 展开的 `minio_node` 与 `minio_cluster-minio_seq` 指向成员 IP | 发布成员身份。MinIO 服务名须来自 `dns_records`、启用的节点 hosts、portal 策略或显式 `vm_hosts`；`minio_domain` 本身用于证书／客户端命名，不会单独产生 DNS 记录。[MinIO 身份](https://github.com/pgsty/pigsty/blob/1ee6597dd806605b600e90cf01948277748b45f3/roles/minio/tasks/main.yml)、[MinIO 配置](https://github.com/pgsty/pigsty/blob/1ee6597dd806605b600e90cf01948277748b45f3/roles/minio/tasks/config.yml) |
| 显式 `all.vars.vm_hosts` | 仅原型支持的中性 `{address, names}` 记录 | 作为显式意图加入，遵循相同的冲突检查；不能静默覆盖与其矛盾的推导记录 |
{.wide .expand}

Barn VM 名称必须是小写短标签，最长 63 字符。Pigsty 可能把客机改成另一个名字：`node_id_from_pg: true` 可以覆盖显式 `nodename`，而 Barn 的回退推导不读取这个开关。若要保持身份一致，应明确设置短 `nodename`，并按需关闭 Pigsty 的 PG 身份覆盖；FQDN 放入别名。依据：[Pigsty 节点身份](https://github.com/pgsty/pigsty/blob/1ee6597dd806605b600e90cf01948277748b45f3/roles/node_id/tasks/main.yml)。

多台 infra 拥有不同的 `admin_ip` 和 `i.pigsty` 视图，可能完全合理。宿主必须明确选定一个入口／视图、使用不同名称，或配置稳定的共享入口；不能默认取第一台 infra。只有相关答案和发布代次一致的 DNS 副本，才可作为冗余上游。

## 复用现有清单形状，明确导出边界 {#export-contract}

原型可复用的边界是现有清单格式的最小投影。下面的 `.100` 只是示例，实际使用前须另行配置可达的 VIP。

```yaml {title="host-names.yml — 原型兼容形状"}
all:
  hosts:
    10.10.10.10: {nodename: meta}
  vars:
    vm_hosts:
      - address: 10.10.10.10
        names: [i.pigsty, meta]
      - address: 10.10.10.100
        names: [pg-meta]
```

`vm_hosts` 只能位于 `all.vars`；条目只接受 `address` 和非空字符串列表 `names`。来源信息单独放在报告中，不能塞进额外字段。**清单至少需要一个托管节点**：只有 `vm_hosts` 的文档当前会报 `inventory defines no hosts`。`all.hosts` 提供节点身份和 `/24` 上下文。这是可丢弃的生成结果，不是让用户维护第二份清单。它可以在 VM 创建前发布，但不能证明节点或服务已经存在。

当前 Barn 适配器要求每个名称只对应一个规范 RFC1918 IPv4 地址，地址位于托管 `/24` 的 `.9`–`.254`。`.1` 属于宿主，`.2`–`.8` 为保留范围，`.0` 和 `.255` 不可用。多 A 答案、外部目标、IPv6、通配符及非地址 RR 类型需要明确选择其他方案；hosts 格式或 DNS 协议本身的能力不会自动扩大适配器边界。自定义私有 `/24` 可以使用，但须同步调整 Pigsty 的 `admin_ip`、记录与 VIP。DNS 不负责创建路由或 VIP。[Barn 网络布局](https://github.com/pgsty/barn/blob/b2cc8da8983e710255d504bf26bf5d7b3f182790/internal/network/subnet/layout.go)

### 先交付受限字面模式，再支持完整 Ansible 语义 {#export-modes}

**拟议模式**：`literal` 为声明支持的静态 profile 生成宿主访问意图；`rendered` 使用正常 Pigsty 控制节点的有效变量与角色规则计算所选视图；`observed` 则显式采集指定 infra 节点已部署的 DNS 数据及服务观察结果。任务被跳过或失败后，渲染意图可能不同于已安装文件；文件也可能不同于服务实际回答。报告必须写清采集了什么证据、何时采集。任何模式都不等于实时 Patroni 权威信息。

第一阶段的字面模式严格限于：一个 YAML 来源、按角色上下文保留的已知默认值、无歧义继承、支持的标准 portal 模板，以及文档规定的 `${admin_ip}`／MinIO 占位符替换。检测并拒绝相邻目录或控制节点侧的 `group_vars`、`host_vars`，以及多来源／插件、DNS 相关 Jinja／lookup／facts、同级组歧义和不支持的任务上下文。不能静默忽略变量来源。转义换行与块文本换行必须逐行解析；错误类型和 CIDR 边界应明确拒绝，不能“修复”为另一种角色语义。

先在所有相关 Pigsty 主机上计算身份和目标，包括 `vm_skip` 的外部 primary／infra，再应用 Barn 的地址限制。在尚未支持这种计算前，应拒绝受影响的 profile，不能漏掉这些角色。VIP 冲突检查必须纳入所有已知外部地址；某台机器不交给 Barn 虚拟化，不代表可以丢弃它与 DNS 有关的配置。

第二阶段引入 Pigsty 共享纯函数与有效变量适配层，并在 **各自选定的视图内** 验证与角色渲染等价。`ansible-inventory --list` 能处理清单变量，却不会执行全部角色默认值、`set_fact`、任务条件或控制节点模板。通用支持需要明确提供这些上下文，并拒绝尚未解析的值。受控的只读导出可以在正常 Pigsty 控制节点执行，再把净化后的投影传给宿主，宿主用户无需安装 Ansible。完整的 VM 创建前导出仍只适用于不依赖客机事实的 profile。[Ansible 变量合并规则](https://docs.ansible.com/projects/ansible/latest/inventory_guide/intro_inventory.html#how-variables-are-merged)

校验与提取必须绑定同一代输入，发布前检查相关源文件和默认值文件是否变化。权限为 `0600` 的临时文件只写节点身份和名称，不持久化完整 hostvars、凭据或共享目录设置。拟议的 `--mode`、`--view`、`--export` 属于 Pigsty，不属于 Barn。默认 `--view host-access` 要求入口无歧义；`host-access:<infra-node>` 明确选择其视图，`guest-dns:<infra-node>` 选择 DNS 输出。第一阶段拒绝尚未支持的选择。`observed` 初期只支持 `guest-dns`，不凭空补充便利记录。`--export FILE` 只写投影，与应用操作互斥。现有 `--json` 继续表示 Barn 计划。

## 显式替换来源，防止服务名消失 {#source-selection}

| 证据 | 能说明什么 | 不能说明什么 |
|---|---|---|
| 当前期望清单／导出结果 | 本次要发布的名称，可早于 VM 创建 | 已应用节点、成功执行的 Pigsty 任务或运行中的 DNS |
| Barn 已应用节点状态 | 已提交的节点地址、名称与 `vm_alias`，包括停止的节点 | `vm_hosts`、portal、服务别名或当前 leader |
| 已安装管理块及元数据 | 宿主文件当前内容，以及记录的来源种类 | 当前源文件路径、存活客机或最新部署的 DNS |
{.wide}

原型替换整个管理块，因此在 `hosts install -f` 之后运行裸 `hosts install`，可能删掉只存在于清单中的服务别名。**最小保护提案**：在现有块内加入一个稳定的普通注释，值为 `# source-kind: inventory` 或 `# source-kind: applied`。不能新造 `# barn:` 标记，当前解析器会拒绝未知标记。这份元数据只保护 CLI 来源选择，与操作系统授权分开处理。

| 已安装管理块 | 提案中裸 `hosts install` 的行为 | 显式来源选择 |
|---|---|---|
| 不存在、无来源标记的旧块，或 `applied` | 保留标签版本行为：从已应用节点生成快照，照常预览／确认 | `-f FILE` 选择清单；`--from-applied` 选择已应用状态 |
| `inventory` | 在 sudo 前失败，即使带 `--yes` 也一样；提示如何保留或替换服务名 | `-f FILE` 用完整清单快照替换；拟议的 `--from-applied` 明确授权切换为节点快照，并展示删除项 |
| 未知／重复来源元数据，或损坏块 | 失败并给出修复说明 | 不自动覆盖 |
{.wide}

`-f` 与拟议的 `--from-applied` 互斥。改用另一个 `-f` 本身就代表明确切换来源。不要记忆源文件路径，尤其不能记忆 Pigsty 临时路径；不增加发布者注册表或项目作用域。下次完整同步中缺席的记录会删除。`vm_hosts: []` 保留该来源的节点名／别名。提取失败或非法空清单绝不能清空管理块，完全移除使用 `hosts uninstall`。删除名称不会销毁 VM。

用于语义 no-op 判断的摘要只依赖发布后的规范记录和来源种类。输入摘要、规则版本、所选视图与详细来源放在普通用户报告中，不写成管理块里的动态时间戳注释。密码、CPU、文件路径或无关清单修改不能导致每次都请求 root。但仍须比较目标实际字节，不能用相同的记录摘要掩盖损坏标记或外部编辑。给旧块增加来源注释属于一次性的特权迁移。

没有来源标记的原型块无法可靠判断是否含清单服务名。升级时先显式重装完整 `-f` 快照，再使用裸命令。最低要求是实现该保护的 CLI 及配套 helper，具体发布版本号尚待分配。旧 CLI 会无视注释并覆盖整个块，因此不能承诺安全降级。包装脚本应检查所需能力，不能只比较版本字符串。

## 离线预览，再授权实际变更 {#operator-workflow}

审计时的原型已具备以下接口，但接口存在不代表已经满足后文的实施门槛。

| 已有接口 | 准确行为 |
|---|---|
| `bin/sandbox-dns -f FILE --json` | 输出 Barn 计划 JSON，不是记录导出；默认文件为 `pigsty.yml` |
| `bin/sandbox-dns -f FILE --apply` | 包装脚本先预览，再以 `--yes` 调用 Barn |
| `barn hosts install -f FILE --json` | 从清单预览，不应用 |
| `barn hosts install -f FILE --yes` | 应用清单快照；Barn 没有 `--apply` 参数 |
| `barn hosts install -f FILE --json --yes` | 应用并返回结构化输出；JSON 不等于只读 |
| `barn hosts uninstall --json` / `--yes` | 预览／显式删除整个 Barn 管理块 |
{.wide}

**第一阶段验收后的拟议工作流**：通过 Pigsty 预览并显式应用；portal、节点或 VIP 改动后重复相同步骤。下面两条命令的写法已存在于原型，增强后的安全语义属于提案。

```bash {title="拟议的日常工作流"}
bin/sandbox-dns -f pigsty.yml --json
bin/sandbox-dns -f pigsty.yml --apply
```

为了审查或从控制节点向宿主传递结果，拟议导出器生成同样的临时投影。下面只有 `--mode`、`--view`、`--export` 是新增参数。

```bash {title="拟议的显式导出工作流"}
bin/sandbox-dns -f pigsty.yml --mode literal --view host-access --export host-names.yml
barn hosts install -f host-names.yml --json
barn hosts install -f host-names.yml --yes
```

切回纯节点发布会有意删除服务别名。拟议的 `--from-applied` 明确表达这种替换；uninstall 已存在，不要求清单或部署状态。

```bash {title="拟议来源切换，以及独立的清理示例"}
barn hosts install --from-applied --json
barn hosts install --from-applied --yes
barn hosts uninstall --json
barn hosts uninstall --yes
```

每次应用都必须 **先形成并展示完整计划，再请求 root**：新增、修改、删除和保留的名称，旧／新地址，分类、来源种类与具体出处，冲突，原生目标路径，以及记录代次和字节前提条件。即使旧记录没有字段级来源，也要展示从原管理块移除的名称。计划只读取本地文件与状态，不查 DNS、不连接客机、不下载、不安装 helper。观察模式的导出应在计划之前单独采集。不输出秘密或完整 hostvars。

| 拟议结果契约 | 结果 |
|---|---|
| 预览（`--json` 且不带 `--yes`，或无终端且不带 `--yes`） | 计划有效时退出 0，`applied: false`；即使有变更也不调用 sudo |
| 规范记录未变，且已安装字节有效 | 退出 0，`changed: false`，不安装 helper、不调用 sudo |
| 交互文本且不带 `--yes` | 展示计划并询问；Barn install 默认 Yes，uninstall 默认 No；包装脚本未带 `--apply` 时仍只预览 |
| 无终端的显式应用 | 使用非阻塞授权；权限不足则返回 capability 错误和非零退出码，不等待密码，不写 hosts |
| 非法输入、违规来源切换、冲突或过期代次 | 写入前以非零退出码失败；要求重新规划，不静默重算并提交另一份数据 |
| 写入验证成功／写后验证失败 | 仅验证成功才退出 0；否则报告失败及可能的部分状态，不谎报回滚成功 |
{.wide}

保留 Barn 的 `{plan, applied}` 报告形状。当前 plan 包含 `schema`、`action`、`target`、`changed`、前后摘要，以及可选的 `lines`／helper 摘要；来源与差异详情属于新增内容。当前 Python 包装脚本不保证错误也是 JSON，结构化错误对齐列为第一阶段工作。

### 加固现有特权边界 {#privilege-boundary}

当前 CLI 的正常规划只改自己的管理块。固定 helper 校验原生目标、调用者／暂存文件的所有者、权限和摘要，原子替换后复核字节以及 uid/gid/mode。**但它没有独立证明暂存文件只修改 Barn 块，也没有覆盖检查到 rename 全过程的事务锁。** 通过的测试未覆盖这两个缺口。调用者提供的摘要只能证明字节一致，不能证明修改范围被授权；原子 rename 也不是 compare-and-swap。[标签版本 helper 实现](https://github.com/pgsty/barn/blob/b2cc8da8983e710255d504bf26bf5d7b3f182790/internal/hostconfig/hostconfig.go#L595)

拟议写入流程保留原边界：helper 获取 root 所有的宿主级协作锁，重读目标并检查已审查摘要，校验有大小上限的记录、来源元数据及冲突，自行重建允许的替换结果，再比较、原子写入并复核。uninstall 只能移除该块。保留块外字节，首次追加需要补末尾换行的已知例外单独说明；承诺保留更多文件系统元数据前补充测试。其他 root 编辑器未必遵守 Barn 锁，因此仍需旧字节校验。应用期间固定生成源；包装脚本必须将已展示计划绑定到应用请求，或让同一次 Barn 调用展示并应用权威计划，不能在两个子进程之间丢弃之前的预览约束。

按次 sudo 仍为主要方式。setup 安装 root 所有、摘要配对的 helper，真正写入仍以特权执行。`--yes` 只跳过 Barn 确认。当前非交互授权使用 `sudo -n`，交互调用则可以要求认证。持久窄权限授权属于可选后续工作，必须先完成 helper 内部范围校验和锁；不能授权任意配置 include，也不能扩展为无限制 sudo。仅授权 helper 的规则还需要专门的能力探测，因为现有 `sudo -v`／`true` 探测可能误判这类策略不可用。[Sudo 行为](https://raw.githubusercontent.com/sudo-project/sudo/main/docs/sudo.man.in)、[sudoers 命令参数](https://raw.githubusercontent.com/sudo-project/sudo/main/docs/sudoers.man.in)

## 将名称清理与 VM 生命周期分开负责 {#lifecycle-and-migration}

| 事件 | 拟议职责与残留状态 |
|---|---|
| 首次 setup／boot／`up` | 按需准备网络／helper，提示显式 DNS 工作流；仅在用户选择后发布，清单意图可以早于 VM；不隐式同步 hosts |
| 重复同步／客机部署 | Pigsty 重新生成所选完整视图，Barn 比较并发布；部署客机不隐式提升宿主权限 |
| `stop`、启动或重启 | 保留名称，提示可解析地址可能离线；不因生命周期操作单独请求 root |
| 移除节点、`destroy` 或清空部署数据 | 保留管理块；展示残留名称与显式清理命令。有期望来源时显示差异，只有已应用状态时诊断缺席节点，不猜测服务意图 |
| `hosts uninstall` | 只移除 Barn 管理块，保留当前块外内容、VM、磁盘及客机 DNS |
| 删除 `BARN_HOME`／重装工具 | 仍可依据原生管理块清理。重装兼容 CLI/helper 后执行 `hosts uninstall`，不依赖已删除状态或记忆的源路径 |
| 卸载 Barn 软件 | 明确删除二进制会留下宿主记录；先提供独立、显式的清理操作，并保留兼容版本重装或管理员编辑管理块的恢复说明 |
{.wide}

拟议诊断比较来源种类、规范记录代次与当前字节，不能只看 begin 标记是否存在。它需要区分过期的期望导出、不可用的已应用状态与停止的客机。刚发布的名称也不等于服务健康。

旧 [Pigsty Vagrant DNS](https://github.com/pgsty/pigsty/blob/1ee6597dd806605b600e90cf01948277748b45f3/vagrant/dns) 使用 **逐行 `# pigsty dns` 注释**，没有成对的管理块，并把一组固定别名指向第一台 VM。Barn 必须保留这些外部记录：同地址的重复项会留下，不同地址则冲突。迁移时先盘点标记行，与完整新视图比较，突出只存在于旧记录中的名称。随后由显式 Pigsty 迁移步骤或管理员在重新比较文件后，仅删除已审查的旧记录，再交给 Barn 发布。不能按 `.pigsty` 后缀删除，也不能复用旧脚本宽泛的子串删除逻辑。Barn 的窄权限 helper 不应取得 Vagrant 行的所有权。最后确认重复记录已清除，以免以后 Barn uninstall 后名称仍然存在。

## 分别验证服务可达性与高可用 {#ha-and-addresses}

`pg_primary_ip` 是清单中唯一声明的 primary，计算时应包含相关外部主机；它不是实时 Patroni leader。已核查的 [故障切换回调](https://github.com/pgsty/pigsty/blob/1ee6597dd806605b600e90cf01948277748b45f3/files/postgres/pg-failover-callback) 不会更新 DNS。直连该地址的 PostgreSQL 端口仍具有静态节点语义。同一地址上的 HAProxy 角色端口可以路由到当前后端角色，但代理节点地址本身仍须可达。可达 VIP 或冗余代理入口才适合作为稳定发布目标；[vip-manager](https://github.com/pgsty/pigsty/blob/1ee6597dd806605b600e90cf01948277748b45f3/roles/pgsql/templates/vip-manager.yml) 可以根据 DCS leader 移动 PG VIP。DNS 服务器冗余、服务目标正确和客户端重连成功需要分别验收；DNS 改变不会迁移已有 TCP 连接。

九个已审计配置路径存在保留区 PG VIP 冲突：`demo/debian`、`demo/el`、`fat`、`ha/dual`、`ha/full`、`ha/octo`、`ha/safe`、`ha/simu`、`ha/trio`。当前 `pigsty.yml` 另有 `.2` 冲突。`build/dev` 与 `build/oss` 需要明确宿主选择哪个 `i.pigsty` 入口；`demo/demo` 需要把 FQDN `nodename` 改为短 Barn 名。修改时同步调整所有依赖记录、URL 和连接设置。

候选 `.100/.101/.102` 在原始文本与 YAML 解码扫描中均为零字面命中，扫描范围为 **54 个配置路径、当前 `pigsty.yml` 与 7 个角色默认值文件，共 62 个路径**。这只支持在该审计语料内考虑这些地址，不代表 IPAM 预留，也没有检查 DHCP 租约、ARP、外部节点、动态表达式或实际网络。每个目标平台仍需验证 VIP 冲突与切换；放宽 Barn 保留地址校验不能解决网络冲突。

## 命名空间完整后，再升级为按域转发 {#split-dns}

默认保留现有 `.pigsty`。可选的新域建议使用范围更窄的 `pigsty.test`；`.test` 为测试保留，`.pigsty` 则没有特殊用途保留资格。不要使用属于 mDNS 的 `.local`。更换域名还须同步修改记录、portal URL 和证书，单改路由规则不能给应用改名。[IANA 注册表](https://www.iana.org/assignments/special-use-domain-names/special-use-domain-names.xhtml)、[RFC 6761](https://www.rfc-editor.org/rfc/rfc6761.html#section-6.2)、[RFC 6762](https://www.rfc-editor.org/rfc/rfc6762.html#section-3)

**后缀转发不能解决当前短名。** `/etc/resolver/pigsty` 和 Linux 的 `~pigsty` 都不会自动把裸 `meta`、`pg-meta`、`pg-meta-1` 送往 Pigsty。已审计的集群后缀默认为空，实例记录也没有后缀。启用路由前，须先发布对应的节点／实例 FQDN，并为集群显式设置 `pg_dns_suffix`，例如 `.pigsty.test`。默认保留有限的 hosts 别名兼容短名。安装 search domain 属于另一项显式选择，且只有补全后的 FQDN 确实存在才有效。本机高端口 daemon 也有完全相同的路由前提。[systemd 路由域与搜索域](https://systemd.io/RESOLVED-VPNS/)

### macOS 使用一个独立管理的 resolver 文件 {#macos-routing}

**拟议配置，尚未安装**：

```text {title="/private/etc/resolver/barn.pigsty.test"}
domain pigsty.test
nameserver 10.10.10.10
port 53
```

macOS 支持按域选择 resolver 和显式端口。只有省略 `domain` 时才以文件名作为域名，并按最长后缀匹配。本提案显式写域名，不自动增加 search list。已有同域路由或目标路径冲突时拒绝安装，包括 VPN 配置。只创建缺失且属于自己的文件／目录，使用适当的 root 所有权；备份与暂存内容放在 resolver 目录之外。使用 `scutil --dns`、`dscacheutil` 和系统 `getaddrinfo()` 验证生效。直接运行 `dig @server` 只能测试 DNS 服务，不能证明 macOS 原生路由正确。重初始化与缓存收敛时间须在目标系统版本验收。[Apple resolver 手册](https://raw.githubusercontent.com/apple-oss-distributions/libresolv/main/resolver.5)、[Apple configd 解析器](https://github.com/apple-oss-distributions/configd/blob/585b7f2fca293f4642d21d15c5daf187f63c4796/dnsinfo/dnsinfo_flatfile.c#L366)

安装、修改入口和卸载需要特权；路由不变时，客机更新记录无需宿主特权。卸载只删除内容仍匹配的 Barn 文件，并验证路由已消失。保留 VPN／默认 resolver 及用户后续修改，不能恢复整份旧 DNS 配置。

### Linux 必须识别实际解析链路及其所有者 {#linux-routing}

检测过程只读：检查 resolved 是否运行、NSS `hosts:` 顺序、`/etc/resolv.conf` 指向，以及 NetworkManager 生效的 DNS plugin。若文件直接列出上游，部分客户端会绕过 resolved 的逐链路路由。仅有 NetworkManager 在运行，不能证明支持 split DNS。应探测版本和实际能力，而不是替用户切换整机 DNS 栈。[resolved 客户端路径](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd-resolved.service.xml)、[NetworkManager 插件](https://networkmanager.dev/docs/api/latest/NetworkManager.conf.html)

| 拟议支持的适配器 | 持久安装与激活 | 卸载及限制 |
|---|---|---|
| networkd + resolved，且链路归 Barn 独占 | 为已确认的 Barn `.network` 创建自有 drop-in：`DNS=10.10.10.10`、`Domains=~pigsty.test`、`DNSDefaultRoute=no`；只 reload/reconfigure 该链路 | 删除仍匹配的自有 drop-in，重读有效状态；保留其他文件与设置 |
| NetworkManager + resolved | 按 UUID 操作 Barn profile，设置 DNS 与 `ipv4.dns-search=~pigsty.test`，reapply 后核验 resolved | 只恢复仍与已应用值匹配的自有属性；不删除共享 profile，不改全局 plugin |
| NetworkManager 已使用 dnsmasq plugin | 利用 Barn profile 的条件转发；自定义端口另行探测 | 遵循相同的 profile 所有权规则；不自动启用新的全局 plugin |
| 运行态 resolved | 仅限活跃、Barn 独占的非 loopback 链路；明确提示不跨重启持久化 | 只有全部受影响配置都明确属于 Barn 时才可整链路 `revert`；共享／VPN／物理链路不适用 |
| 不支持的解析器或归属不明 | 说明缺失能力，继续使用 hosts／手工模式 | 不接管全局 nameserver 或 `/etc/resolv.conf` |
{.wide .expand}

绝不生成 `~.`。`DNSDefaultRoute=no` 无法抵消覆盖所有域的路由。保留优先级和 DHCP／VPN 设置，不用 NetworkManager 负优先级抢占无关域。第一版客机转发以端口 53 为基线，不能把新版 resolved 的自定义端口语法直接复制到旧 NM profile。loopback 不是通用的 resolved 路由作用域，本机 daemon 必须使用受支持的路由机制。最后一台客机关闭后，`barn0` 可能失去 carrier 或链路本身，导致 DNS scope 失效，查询重新跟随默认路由。因此，严格保证私域不外泄，需要稳定路由、服务端否定响应策略和真机测试。[networkd DNS 设置](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.network.xml)、[NM 优先级与搜索域](https://networkmanager.dev/docs/api/latest/settings-ipv4.html)、[resolvectl 重置范围](https://raw.githubusercontent.com/systemd/systemd/main/man/resolvectl.xml)、[resolved 链路有效性](https://github.com/systemd/systemd/blob/main/src/resolve/resolved-link.c)

两个平台都需要放在部署状态之外、由 root 所有的变更日志，记录自有路径／profile UUID、原先是否存在、已应用值和元数据。先准备并验证上游 UDP/TCP 服务，再启用路由；写入前重新比较已审查配置，写入后验证原生解析。回滚只撤销仍归自己的变化；发现漂移或中断时报告部分状态。保存的 ifindex 不能作为跨重启的持久身份。从 hosts 切换时，显式移除重叠的 Barn 记录，并报告外部 hosts 覆盖。NM 的 profile 持久状态和运行态激活需要分别检查。[nmcli 持久化与 reapply](https://networkmanager.dev/docs/api/latest/nmcli.html)

### 常驻服务必须证明其维护成本值得承担 {#daemon-and-resolution-limits}

未来 daemon 应只绑定 loopback，优先使用受支持的高端口；仅接受目标用户提交的、有大小限制的记录；完整验证新一代数据后再原子激活，坏输入保留最后成功版本。固定的 root 服务／路由配置不能以 root 执行用户可修改的程序，也不能接受任意 include。安装、服务升级和路由变更仍需要特权。用户 agent 会在注销时退出，系统服务则增加安装和维护成本。须测试启动顺序、退避重启、端口占用及进程身份。主动卸载 daemon 时，应先撤路由并验证，再停止服务。崩溃应可诊断，不能静默把私域转发到公共上游。[Apple 高端口实现](https://github.com/apple/container/blob/d5416e63231783c9699d31f35381caac941d3cde/Sources/Services/ContainerAPIService/Client/HostDNSResolver.swift#L38)

hosts 没有通配符行为。未来通配 DNS 只应覆盖明确共享入口的子域，不能笼统覆盖所有 Pigsty 名称。应为未知名称定义 NXDOMAIN，为缺少的记录类型定义 NODATA；dnsmasq 的域匹配与本地域策略需要仔细配置，并同时支持 UDP 和 TCP。AAAA 答案与查询 DNS 时使用的传输协议相互独立，不能编造不可达 IPv6 地址或 `::1`。当前 Barn 导出仍限于 IPv4，双栈记录需要另定适配契约。[dnsmasq 手册](https://thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html)、[RFC 3596](https://www.rfc-editor.org/rfc/rfc3596.html)、[RFC 7766](https://www.rfc-editor.org/rfc/rfc7766.html)

系统、应用和否定缓存都可能保留旧结果；浏览器／SDK 的 DoH 可能绕过原生路由。已有 hosts 记录可能遮蔽 DNS，具体取决于 NSS 路径；VPN 会同时影响地址可达性和域路由选择。应测试这些路径，报告实测收敛情况，不承诺瞬间生效，也不在每次同步时清空全部缓存。[DoH 客户端策略](https://www.rfc-editor.org/rfc/rfc8484.html#section-3)

## 现有证据支持原型，不等于完成平台验收 {#evidence}

| 已记录的离线证据 | 结果及含义 |
|---|---|
| Barn hosts/config/helper/CLI 测试 | **16 个顶层测试通过**；覆盖临时文件写入与预览，包括损坏块、冲突、保留地址、helper 配对及无部署清单预览 |
| Pigsty 提取器测试 | **11 项通过**；应用子进程使用 mock，覆盖净化投影与预览行为 |
| 对抗性样例 | **21 项观察被复现**，含 4 项 Ansible inventory 对照；它们揭示缺口，不是 21 项正确性测试通过 |
| 配置语料 | **54 个路径**，包括符号链接别名；**53 个通过 Barn VM 校验，42 个被提取器接受**。解析器接受不代表角色等价或部署成功 |
| 实际原型预览 | `conf/meta.yml` 生成 10 个名称，返回 `applied: false`；宿主原生 hosts 字节未变 |
{.wide}

对抗性证据发现了忽略 `group_vars`／`host_vars`、同级优先级不同、多行／转义换行导致地址错绑、发布已跳过的虚拟主机、遗漏外部角色及地址冲突检查不完整等问题，也暴露了混合视图歧义、无法表达多地址，以及显式 CIDR 目标被错误规范化。`dns_enabled: false` 时的 PG 别名应遵循前述明确的宿主便利策略，其存在本身不构成缺陷；静默错误地址，以及把这种结果声称为已部署 DNS 的等价输出，才是缺陷。

离线审查保留了样例、逐模板结果、执行命令和源码指纹。本文不复制私有配置或宿主 hosts 摘要。综合写作时，Barn DNS 相关文件仍与记录的指纹一致，尽管并发工作已将本地 HEAD 推进至 `158786a1fee011edf3a1673400b8dd40ba9a7261`；Pigsty 核查基线为 `1ee6597dd806605b600e90cf01948277748b45f3`。未发布证据位于 Barn 的 `internal/hostconfig`、`internal/config`、`cmd/barn/hosts_inventory_test.go`，以及 Pigsty 的 `bin/sandbox-dns`／`tests/test_sandbox_dns.py`。这些是文件路径，不代表公开基线链接中已经包含原型。

要用同一候选版本复现定向测试，先将 `DNS_AUDIT_DIR` 设置为仓库外一个已存在、可丢弃目录的绝对路径；以下命令用它存放全部缓存和状态。以下是 **复现说明，不是本次文档综合新增执行的检查**：

```bash {title="Barn 工作区——离线复现"}
export GOTOOLCHAIN=local GOPROXY=off GOSUMDB=off GOENV=off GOWORK=off
export GOFLAGS=-mod=readonly
export GOCACHE="${DNS_AUDIT_DIR:?}/go-cache"
export GOTMPDIR="${DNS_AUDIT_DIR:?}/go-tmp" TMPDIR="${DNS_AUDIT_DIR:?}/tmp"
export BARN_HOME="${DNS_AUDIT_DIR:?}/barn-home"
mkdir -p "$GOCACHE" "$GOTMPDIR" "$TMPDIR" "$BARN_HOME"
go test -count=1 -v \
  -run '^(TestReconcile.*|TestApplyHelper.*|TestInstalledHelperValidation.*|TestCompanionHelperDigest.*|TestHelper.*|TestParseInventoryVMHosts.*|TestHostsInventoryPreviewNeedsNoDeployment)$' \
  ./internal/hostconfig ./internal/config ./cmd/barn-hosts-helper ./cmd/barn
```

```bash {title="Pigsty 工作区——离线复现"}
python3 -B -m unittest discover -s tests -p test_sandbox_dns.py -v
```

记录中的环境为 darwin/arm64 上的 Go 1.27.3、Python 3.14、PyYAML 6.0.3；inventory 对照使用 Ansible 2.21.5。模板统计的复现方法是排序枚举 `conf/**/*.yml` 路径，保留符号链接入口，逐个运行候选 Barn 的 `validate --json`，再调用相同提取器。发布前应把保存的对抗样例纳入仓库测试。本轮研究没有执行 sudo、系统配置修改、VM 操作或 playbook。真实 resolver 激活、VPN 行为、缓存时限和 HA 仍待验收；站点检查由主文档流程另行执行。

## 分阶段实施，每阶段设置明确门槛 {#implementation-plan}

| 阶段与负责人 | 实施清单 | 验收门槛 |
|---|---|---|
| **0——Pigsty 语义** | 拆分输出视图；修复静默解析／覆盖／虚拟主机错误；支持或拒绝外部角色；明确 CIDR 规则；修正保留区 VIP、多 infra 选择及 VM 身份 | 每个支持的静态 profile 都有经审查的预期记录和来源；不支持的输入明确失败；21 项对抗观察转成预期结果回归测试 |
| **1——Pigsty 导出器 + Barn hosts** | 受限字面导出；复用准确投影格式；来源标记保护与显式 applied 替换；完整离线差异；固定输入；结构化错误；helper 范围校验与协作锁 | 裸 install 不能丢失清单服务名；no-op 不需要 sudo；每次实际写入都复核；定向测试与仓库要求的检查通过 |
| **2——集成与 HA** | 共享纯规则／有效变量适配层；控制节点侧 rendered／observed 导出；生命周期诊断、迁移和重装清理；真实平台验证 | 按视图验证角色等价和支持 profile 的覆盖；macOS arm64、Linux amd64 的宿主访问与 VIP 切换通过，并扩展到其他承诺支持的宿主 |
| **3——可选 split DNS** | FQDN 发布、稳定入口、能力探测、所有权日志及平台适配器 | 后缀隔离、持久化、回滚和故障矩阵通过；短名保持明确约定 |
| **需求门槛——本机 daemon** | 衡量前述方案无法满足的更新频率或 RR 需求；定义服务身份与生命周期 | 收益足以承担服务维护；停服、注销、端口和升级测试通过 |
{.wide .expand}

| 必须测试的领域 | 具体验收项目 |
|---|---|
| 语义 | 变量覆盖、同级组、默认值／模板、多行数据、portal 条件、PG 目标分支、MinIO 服务名来源、`vm_skip`、多 infra 与多地址拒绝 |
| 来源与文件安全 | inventory → 裸命令拒绝；显式 applied 替换／删除；旧块迁移；大小写冲突、尾点、重复／损坏标记；块外编辑；状态缺失；崩溃／并发／过期计划与 helper 范围测试 |
| 幂等 | 重复快照；无关凭据／资源修改；代次漂移；仅来源种类变化的迁移；no-op 不请求 root；非交互权限失败 |
| 原生访问与 HA | Portal Host／TLS 路由，节点／PG 短名与 FQDN，PG 直连端口与代理端口，VIP 可达性／切换，外部地址冲突，新旧连接差异 |
| 解析器集成 | macOS 原生解析；Linux NSS／stub／绕行路径；UDP/TCP、A/AAAA/NODATA/NXDOMAIN、域顶点／子域、公共域／VPN 隔离及一致的上游视图 |
| 持久化与恢复 | 重启、注销、客机／DNS 停机、最后客机停止、接口重建、DHCP 更新、VPN 重连、缓存／DoH、部分应用、外部编辑、卸载与重装 |
{.wide}

## 为剩余产品选择给出默认答案 {#remaining-decisions}

| 产品问题 | 推荐默认值 |
|---|---|
| 是否自动修改宿主？ | 否；由 Pigsty 显式预览／应用，生命周期只做诊断 |
| 选择什么视图／来源？ | 支持的 profile 默认使用 literal 期望 `host-access`；rendered／observed 是显式且有标签的替代来源，不推断部署权威性 |
| 多 infra 或外部入口怎么办？ | 拒绝歧义，明确选择入口／视图；网段外地址在另行设计能力前使用手工／已有 DNS |
| 来源迁移与最低版本？ | 保留裸 legacy／applied 行为，保护 inventory 块；探测首个包含保护及配套 helper 的版本能力；不承诺安全降级 |
| 如何规范名称？ | ASCII 转小写后比较／输出；相同映射去重，冲突地址拒绝；存在节点规范名时将其放在行首。第一阶段拒绝尾点输入，并保守检测块外等价拼写，不接受静默归一化差异 |
| 命名空间与短名？ | 保留 `.pigsty`，新路由可选 `pigsty.test`；短别名显式写 hosts，不自动安装 search domain 或改名证书 |
| 权限与缓存策略？ | 按次 sudo，不授予持久权限，不自动清空全局缓存；先测收敛时间，再确定文档承诺 |
| VIP 与服务生命周期？ | `.100/.101/.102` 仅为已审计模板的候选，须验证分配；停止／销毁保留名称，状态删除后仍能显式清理 |
| 通用导出器与 daemon 何时做？ | 先交付严格且有用的子集，通过逐视图等价门槛扩展；确认需求和维护归属后再做 daemon |
{.wide}
