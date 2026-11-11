---
title: "Pigsty 用 Barn 替换 Vagrant：资源、域名与迁移清单"
linkTitle: "Pigsty 沙盒迁移"
description: "梳理 Pigsty Vagrant 脚本的设计，定义 vm_scale 与本机域名发布，并记录 54 份配置的离线审计和迁移顺序。"
date: 2026-11-10
lastmod: 2026-11-11
weight: 71
categories: [设计]
tags: [Pigsty, Vagrant, DNS]
icon: fa-solid fa-boxes-stacked
---

Pigsty 可以用同一份主机清单驱动 Barn 与 Ansible。迁移时需要保留拓扑选择、镜像矩阵、资源缩放、固定地址和 SSH 工作流，并清理旧脚本隐含的地址、节点名及销毁行为。

**状态（2026-11-10）**：`vm_scale`、1 核 / 2 GiB 默认规格、`vm_hosts`、`barn hosts install -f` 及 Pigsty 的 `bin/sandbox-dns` 已在本地工作区实现并完成下述离线验证，尚未发布。Pigsty 的 Makefile 仍使用 Vagrant；本文后半部分是下一阶段实施清单。Barn 1.1.0 的实际清单默认值仍是 2 核 / 4 GiB，且不支持上述新增参数。

## Vagrant 脚本真正提供了什么 {#vagrant-contract}

| 入口 | 当前设计 | 迁移决定 |
|---|---|---|
| `vagrant/config`、`vagrant/spec/*.rb` | 将拓扑、发行版、倍数、provider、架构组合成 Vagrantfile；倍数为 1–64；构建 profile 保留逐节点镜像 | 拓扑与资源迁入 Pigsty 清单的 `vm_*`；保留镜像选择和缩放概念，由 Barn 处理平台后端 |
| `meta/full/simu` 等 Make 别名 | 先配置 Pigsty，再选 VM spec，默认走 EL9；不少目标隐含 `del` | 新入口默认镜像按前一轮方案选 `u26`，后缀选发行版；创建、重建、销毁拆开，配置变更先 `plan` |
| `vagrant/ssh` | 从 VM spec 与 `vagrant ssh-config` 拼接宿主 SSH 配置 | 使用 Barn 自动维护的 SSH 配置；保留密钥、管理端口、known-hosts 和实例身份 |
| `vagrant/dns` | 从 Ruby spec 提取节点名，并给首节点拼上一组写死的 `.pigsty` 名称 | 从 Pigsty 清单及角色默认值提取域名，默认预览，显式发布 |
| provider 模板 | 禁用默认 `/vagrant` 共享，补 SSH 公钥、设置网络与附加盘 | Barn 管理客机初始化、用户、网络和磁盘；源码交付显式选择 scp/rsync 或 `vm_shares` |
| `new`、`del`、`nuke`、`suspend` | 重建、无确认销毁、清理，以及 Vagrant 内存挂起 | 显式映射生命周期，保留销毁范围确认；`stop/start` 不承诺恢复内存状态 |
| `bin/boot-pkg`、Makefile copy/sync 目标、`bin/release` | 依赖 `meta`/发行版别名分发软件；发布包继续携带 Vagrant 脚本 | 核对 SSH 别名与目录，再迁移打包清单，避免只换 `make up` |
{.wide .expand}

旧规格不宜机械照搬：`meta` 为 2 核 / 4 GiB，`full` 为一个 2 核 / 4 GiB 加三个 1 核 / 2 GiB，`simu` 混合多种规格。新的统一基数是每节点 1 核 / 2 GiB；数据库、构建或应用测试需要更多资源时，显式提高基数或倍数。该基数描述 VM 默认值，不能替代各模块的容量要求。

`new: del up`、`meta9: cmeta del vmeta9 up ssh` 这类前置依赖没有表达可靠的执行顺序，`make -j` 可以让配置、销毁与启动并行。迁移入口应使用单个顺序执行的 recipe 或脚本，任一步失败即停。

依据：[配置生成器](https://github.com/pgsty/pigsty/blob/main/vagrant/config)、[Vagrant 目录](https://github.com/pgsty/pigsty/tree/main/vagrant)、[Pigsty Makefile](https://github.com/pgsty/pigsty/blob/main/Makefile)。

## vm_scale 的决定 {#scale}

`vm_cpu`、`vm_mem`、`vm_scale` 分别按 **主机 > 最深子组 > 父组 > all.vars > 默认值** 取值，随后执行一次倍乘：

```text
有效 CPU  = 基础 vm_cpu（默认 1）× vm_scale（默认 1）
有效内存  = 基础 vm_mem（默认 2048 MiB）× vm_scale（默认 1）
```

因此单写 `vm_scale: 3` 得到 3 核 / 6 GiB；再写 `vm_cpu: 2`、`vm_mem: 4GiB` 就得到 6 核 / 12 GiB。主机可以用 `vm_scale: 1` 覆盖组级倍数；多个层级不累乘。磁盘不缩放。参数的单位、边界和旧部署升级方式见 [配置参考](/zh/docs/reference/configuration/#resource-scaling)。

镜像、架构、CPU、内存、倍数与根盘的命令范围、短参数、环境变量、优先级和保存方式统一见 [VM 规格参数设计](/zh/blog/design/vm-resource-overrides/)。新提案中，Make 入口只将用户明确提供的 `IMAGE/ARCH/CPU/MEM/SCALE/DISK` 转为 CLI 覆盖，优先于对应的 `BARN_*` 环境变量；模板默认值与主机特例保留在 YAML 中，普通生命周期命令不保存隐藏偏好。普通同构 profile 可让 `IMAGE` 或发行版后缀覆盖镜像；构建 profile 必须保留逐节点 `vm_image`，仅在用户明确要求统一镜像时覆盖。

## DNS 可以做，而且适合显式设置 {#dns}

系统 `/etc/hosts` 的变更仍需要 root 权限。可改善的是把提取、校验和预览放在普通用户阶段，只将最后的受控写入交给 Barn helper；相同内容重复执行无需 sudo。首次设置只是一个时机，新增 portal 或更换 VIP 后同样需要再次发布。

职责分为两层：Pigsty 的 `bin/sandbox-dns` 解释服务语义；Barn 接受通用的 `all.vars.vm_hosts`，合并节点及别名，校验后替换 `# barn:begin/end` 管理块。域名数据不进入 VM 规格摘要，所以改域名不会要求 VM 重建或重启。

| 来源 | 本机目标地址 |
|---|---|
| Barn 节点名、`vm_alias`；Pigsty `nodename`、`pg_cluster-pg_seq` | 节点 IP |
| `infra_portal.*.domain/domains` | 对应 infra 配置的 `admin_ip` 入口；不使用可能为 `127.0.0.1` 的后端 endpoint |
| `node_default_etc_hosts`、`node_etc_hosts`、`dns_records` | 配置中的 IP，展开 `${admin_ip}`；尊重相关启用开关 |
| `pg_cluster + pg_dns_suffix` | `auto` 使用启用的 PG VIP，否则用清单声明的唯一主库；另支持 `primary`、`vip`、`none` 和显式 IP |
| `node_cluster + vip_dns_suffix` | 启用的节点 VIP；按 `node_id_from_pg` 处理集群身份 |
| `minio_node` 与 `minio_cluster-minio_seq` | MinIO 节点 IP，展开 MinIO 名称模板 |
| `vm_hosts` | 用户显式补充的私网映射 |
{.wide .expand}

在含有新命令的开发版本中，可从 Pigsty 仓库运行：

```bash {title="Pigsty 仓库"}
# 需要 Python 3、PyYAML，以及包含 hosts install -f 的 Barn
bin/sandbox-dns -f conf/meta.yml          # 默认只预览
bin/sandbox-dns -f conf/meta.yml --json
bin/sandbox-dns -f conf/meta.yml --apply  # 需要时由 Barn 请求 sudo
barn hosts uninstall --yes
```

尚未安装候选版时，可用 `BARN=/absolute/path/to/barn` 指定本地构建。脚本先调用 `barn validate`，再使用只含节点身份与域名的权限为 `0600` 的临时清单；不复制 Pigsty 密码、密钥或共享目录配置。重复映射会去重，同名不同 IP 会列出冲突来源，大小写不同也视为同名。系统文件中其他工具的记录保留，存在冲突时由用户决定如何迁移旧记录。

这个适配器与 Barn 一样只读取静态清单，不执行 Ansible inventory 插件、`group_vars`、`host_vars` 或通用 Jinja。相关字段中无法解析的模板、通配符、清单网段外地址会明确失败。`pg_dns_target: primary` 反映清单声明，不会跟随 Patroni 的实时主从切换；高可用入口宜使用已配置的 VIP。多台 infra 各自把 `i.pigsty` 指向自身时，宿主无法同时表达这些局部视图，必须先确定唯一入口或改用不同域名。

后续若确实需要通配域名与动态记录，可评估按域转发到 Pigsty DNS：macOS 的域级 resolver 与 Linux 的 resolver 集成应各自设计。当前阶段无需常驻宿主 DNS 进程或改写全局 nameserver。

## 54 份配置的离线审计 {#audit}

2026-11-10 使用本地候选 Barn，对 `conf/**/*.yml` 的 54 份文件执行 `barn validate --json`，并用提取器生成域名映射。**53 份通过 VM 校验，42 份通过域名提取**。这些数字表示静态配置检查，模块部署和 VIP 故障转移仍需真机验证。

| 配置/类别 | 结果与下一步 |
|---|---|
| `meta` | 1 节点，1 核 / 2 GiB；提取 10 个域名，真实 hosts 预览成功 |
| `ha/dual`、`ha/trio`、`ha/full` | 分别 2/3/4 节点，默认总量为 2/3/4 核、4/6/8 GiB；VM 合法，PG VIP 落入保留区 |
| `ha/simu` | 20 节点、20 核 / 40 GiB；PG VIP 落入保留区，且 MinIO 要求 `/data{1...4}`，但未声明四块 `vm_disks` |
| `demo/minio` | 4 节点，已声明每节点 4×64 GiB 数据盘，21 个域名可提取；节点 VIP `.9` 需纳入网络真机验收 |
| `build/oss` | 7 节点，显式 2 核 / 4 GiB，共 14 核 / 28 GiB，逐节点镜像齐全；本机 `i.pigsty` 存在多目标冲突 |
| `build/dev` | 7 节点可解析，但没有逐节点 `vm_image`，会全部使用 Barn 默认 `u24`；发行版 SSH 别名也需补齐；DNS 同样存在多目标冲突 |
| `demo/demo` | `nodename: pigsty.cc` 不符合 Barn VM 名称规则；需使用短节点名并将 FQDN 放入 `vm_alias` |
| 其余含保留区 VIP 的模板 | `demo/debian`、`demo/el`、`fat`、`ha/octo`、`ha/safe`；与前述四类 HA 模板合计 9 份 |
{.wide .expand}

Barn 的宿主占 `.1`，DHCP 占 `.2`–`.8`，静态节点从 `.9` 开始。Pigsty 常见的 `.2/.3/.4` VIP 必须迁出。当前 54 份模板未使用 `.100/.101/.102`，可将它们作为这轮沙盒 VIP 迁移的候选地址；改动时还需同步显式 DNS、连接串和示例，验证与所选清单节点及其他 VIP 不重叠。不能通过放宽 hosts 校验来解决真实网络冲突。

Barn 名称优先级为 `nodename > pg_cluster-pg_seq > node-末段`，Pigsty 的 `node_id_from_pg: true` 则可能在客机中覆盖显式 `nodename`。旧脚本常用的 `meta`、`node-1`、`el9` 等名称应通过清单与 `vm_alias` 明确保留，验收时同时检查宿主 SSH 别名和客机 hostname。

## 按这个顺序完成替换 {#rollout}

| 优先级 | 负责位置与范围 | 完成条件 |
|---|---|---|
| 已实现，待发布 | Barn 资源与 hosts 基础；Pigsty 域名提取 | 本文验证结果；发布前按仓库流程重新检查镜像目录与版本 |
| P0：清单修正 | Pigsty `conf/` 的 VIP、simu 四盘、dev 镜像、短节点名与 SSH 别名 | 全部目标 profile 通过 VM/域名检查，资源总量与镜像矩阵逐项符合预期 |
| P0：入口切换 | Makefile、统一 `bin/sandbox` 入口、`configure` 衔接；`meta/full/simu` 默认 `u26`；发行版后缀 `8/9/10/12/13/22/24/26` 分别映射到 `el8/el9/el10/d12/d13/u22/u24/u26` | `make -j` 也按顺序执行；明确 `-f`，不被工作目录中的 `barn.yml` 遮蔽；切换 profile 不隐含销毁；正常 up 不碰 hosts |
| P0：SSH 与制品交付 | 使用 `barn ssh-config`，迁移 copy/boot-pkg/sync 的别名；复用 `dba`/UID 88 与已验证的连接参数 | 宿主 SSH、scp/rsync、Ansible 控制节点到其他节点均可用；旧 Vagrant Include 不抢先匹配 |
| P0：真机验收 | macOS arm64 与 Linux amd64，至少覆盖 meta、full、simu 及混合镜像构建 | 1×/2×资源与 resize、DNS 幂等、VIP 访问/切换、四盘挂载、停止启动、失败重试和显式销毁；新环境可完成 Pigsty 部署 |
| P1：发布收口 | `bin/release`、安装依赖、双语用户指南与示例；退役 Vagrant 入口 | 发布包可用 Barn 完成完整沙盒流程，文档与包内脚本无过期入口 |
| P1：长期体验 | 环境精确版本记录、常用分组选择、上传/下载；按实测优化大拓扑启动 | 可重复构建并取回制品；部分失败可诊断、可重试 |
| P2：按需求增加 | 冷快照、VM 导出、动态 DNS/按域转发 | 各自定义身份、磁盘和网络恢复契约后实施 |
{.wide .expand}

Barn 仍是一名用户的一套 Linux 部署。不同 profile 是同一部署的期望拓扑；更换 `BARN_HOME` 不会隔离该用户共享的运行路径和宿主私网，不能把它当作多环境并行方案。镜像默认值也分层处理：Pigsty 新入口可以选择 `u26`，Barn 自身继续遵循内置目录的 `u24` 默认值。

## 实现与验证依据 {#evidence}

资源继承及缩放见 [inventory.go](https://github.com/pgsty/barn/blob/main/internal/config/inventory.go) 与 [inventory_test.go](https://github.com/pgsty/barn/blob/main/internal/config/inventory_test.go)；hosts 合并与权限边界见 [hostconfig](https://github.com/pgsty/barn/tree/main/internal/hostconfig) 与 `cmd/barn/hosts_inventory_test.go`。Pigsty 本地新增文件为 `bin/sandbox-dns` 和 `tests/test_sandbox_dns.py`，服务规则对照 [roles/infra](https://github.com/pgsty/pigsty/tree/main/roles/infra)、[roles/pgsql](https://github.com/pgsty/pigsty/tree/main/roles/pgsql)、[roles/node_id](https://github.com/pgsty/pigsty/tree/main/roles/node_id) 与 [roles/minio](https://github.com/pgsty/pigsty/tree/main/roles/minio)。这些链接指向仓库；本轮新增改动在提交发布前以本地工作区为准。

已完成 `make build`、Barn `make check`、Pigsty 提取器 11 项单元测试，以及 54 份模板离线审计。`conf/meta.yml` 的真实命令返回 `applied: false` 并展示 10 个域名。尚未执行系统 hosts 写入、VM 资源调整、VIP 切换或 Pigsty playbook；这些列入上面的真机验收阶段。
