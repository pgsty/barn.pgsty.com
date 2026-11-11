---
title: "Pigsty 宿主初始化：固定域名与 CA 信任"
linkTitle: "Pigsty 宿主初始化"
description: "用一个显式的 macOS / Linux 初始化操作，配置固定 Pigsty 入口域名并信任实验环境的根 CA。"
date: 2026-11-11
weight: 72
categories: [设计]
tags: [Pigsty, DNS, Security]
icon: fa-solid fa-lock
---

**建议提供一个可选的宿主初始化操作：安装固定 Pigsty 域名，并信任实验环境的公共根 CA 证书。** 入口地址只有一个，默认 `10.10.10.10`；普通实验环境重建继续使用同一 CA。名称、地址和 CA 信任状态不变时，重复 setup 直接返回，无需提权。常见情况下，宿主集成只需初始化一次。

**状态——2026-11-11：设计提案，尚未实现。** 相比此前的 [完整宿主 DNS 方案](/zh/blog/design/pigsty-host-dns/)，本方案收敛了首期交付范围。通用清单提取、动态节点／PG／VIP 名称发布、按域转发和常驻 DNS 服务保留为后续选项，不作为固定配置的实现前提。本轮只修改文档，没有读取 CA 私钥、安装信任、修改系统 hosts 或操作 VM。

## 发布一份小而稳定的名称表 {#fixed-names}

拟议的 `core-v1` 包含八个精确名称，全部指向一个明确选择的入口 IP。名称表带版本号，启用或关闭应用不会改变宿主配置。

| 名称 | 预定用途 |
|---|---|
| `i.pigsty` | Pigsty 首页、监控及首页 portal 提供的各路径 |
| `sss.pigsty`、`m.pigsty` | 对象存储服务及可选的控制台 portal |
| `adm.pigsty`、`ddl.pigsty` | 可选的 pgAdmin、Bytebase portal |
| `supa.pigsty`、`api.pigsty`、`cli.pigsty` | 预留的应用／API 别名 |
{.wide}

```text {title="拟议 core-v1 hosts 内容"}
10.10.10.10 i.pigsty sss.pigsty m.pigsty adm.pigsty ddl.pigsty supa.pigsty api.pigsty cli.pigsty
```

这里的 `*.pigsty` 指一组精确名称，`/etc/hosts` 不支持通配匹配。新增任意名称，例如 `new-app.pigsty`，需要审查后更新名称表；真正的通配解析另行选择 DNS 方案。每行固定把 `i.pigsty` 放在首位，保持规范名称顺序稳定。

名称表参考 Pigsty 的 [默认 DNS 别名](https://github.com/pgsty/pigsty/blob/8046eb4cbd65b2eef7c9e11b4e7ba4f401bec5bd/roles/infra/defaults/main.yml) 和 [MinIO 服务名](https://github.com/pgsty/pigsty/blob/8046eb4cbd65b2eef7c9e11b4e7ba4f401bec5bd/roles/minio/defaults/main.yml)，有意在应用部署前预留部分名称。名称可解析不会自动安装应用、开放端口或配置 Nginx。例如 `sss.pigsty` 可能使用 9000 端口，portal 通常使用 443。

单入口配置适用于这些服务位于入口节点，或已通过该节点代理的实验环境。若存储或应用位于其他机器，又没有入口代理，应通过更通用的 hosts 接口为该服务显式配置静态映射。不要从后端 endpoint 推导另一个地址，也不要默认选择第一台 infra。入口地址须满足 Barn 的私有 IPv4 `/24` 与 `.9`–`.254` 规则；自定义网段显式传 `--ip`，本命令不重新解释 `admin_ip` 或 Jinja。

## 给用户一个初始化入口 {#workflow}

Pigsty 专属的名称表放在拟议的 `bin/sandbox-host` 中，Barn 通过既有特权边界提供通用 hosts 和证书操作。下列示例全部属于 **新增接口提案**。

```bash {title="拟议的初始化、检查与移除"}
bin/sandbox-host setup --ip 10.10.10.10 --ca files/pki/ca/ca.crt
bin/sandbox-host setup --ip 10.10.10.10 --ca files/pki/ca/ca.crt --apply
bin/sandbox-host status
bin/sandbox-host status --probe
bin/sandbox-host remove --apply
```

`setup` 默认预览，展示精确域名／IP、CA 主题、有效期、SHA-256 指纹、信任目标、新增／删除项及所有权。`--apply` 表示应用这份具体操作；将两项变更合并为一次 setup，在系统允许时复用同一次管理员认证会话。认证提示次数由系统策略决定，不配置永久免密权限，也不启动后台进程。

`core-v1` 替换 Barn 唯一的完整 hosts 快照。若此前已发布节点／服务快照，应用前须展示将被删除的名称，并保留所有外部 hosts 行。这样每次发布结果都明确，不会静默合并过期记录。

推荐顺序是：先初始化 Pigsty，生成 CA；取得公共证书；再执行一次宿主 setup。仓库与控制节点共享时，证书可能已经位于示例路径；否则通过已建立且验证过宿主密钥的 SSH 连接，只复制 `ca.crt`。可选的 `--dns-only` 支持提前配置域名，`--ca-only` 支持稍后导入 CA，但它们是独立操作，可能分别需要授权。组合请求缺少 CA 时必须失败，不能静默只做一半。

`status` 只读检查所有权及实际 hosts／信任状态；`status --probe` 额外检查系统解析，以及首页 portal 的 HTTPS 证书链和主机名。分别报告 `names`、`system trust`、`portal HTTPS`：客机离线时，宿主配置仍可能完全正确。TLS 验证使用正常校验，不能通过跳过安全检查或另传 CA 覆盖正在测试的系统信任库。

非交互首次信任或替换 CA 时，要求通过拟议的 `--ca-sha256` 提供预期公共证书指纹，并在提权前比较；仍须显式 `--apply`。权限不足时走非阻塞失败路径，不等待密码。相同配置重复 setup 不要求认证。普通 `barn setup`、`up`、`stop`、`destroy` 不隐式导入 CA。

## 信任选定的 CA，并保持其身份稳定 {#ca-identity}

证书来源是实验环境已有的 `files/pki/ca/ca.crt`。Pigsty 的 [CA 角色](https://github.com/pgsty/pigsty/blob/8046eb4cbd65b2eef7c9e11b4e7ba4f401bec5bd/roles/ca/tasks/main.yml) 在控制节点创建或复用这套 CA。重建时保留控制节点上的 PKI；宿主只取得公共证书，私钥继续由 Pigsty 保管。

首版接受一张有大小限制的 PEM／DER 自签名根证书，检查解析、自签名、有效期、CA 基本约束及证书签名用途。拒绝私钥载荷、叶子证书、含义不明确的证书包和暂不支持的中间证书链。使用 DER 字节的 SHA-256 标识 CA，不按 `pigsty-ca` 这个通用名称匹配；PEM 排版改变仍应视为无变化。解析后的证书和 hosts 内容须绑定到已审查计划，并在特权 helper 内再次验证。

**系统对该 CA 的信任范围大于这八个域名。** hosts 条目和 CA 显示名称都不能将其签发权限限制在 `.pigsty`，setup 预览须明确这一点。macOS 在支持时使用仅针对 TLS 的信任策略；不关闭主机名／有效期校验，也不静默修改其他应用策略。

信任根 CA 后，服务证书仍须符合要求。Pigsty 的 [Nginx 证书任务](https://github.com/pgsty/pigsty/blob/8046eb4cbd65b2eef7c9e11b4e7ba4f401bec5bd/roles/infra/tasks/nginx.yml) 把已配置 portal 名称加入 SAN，并不会自动覆盖所有预留别名。启用 portal 时，需要对应的虚拟主机和包含正确 SAN 的有效叶子证书；通配证书与通配 DNS 是两项独立选择。同一 CA 签发的叶子证书续期不需要更新宿主信任。

## 使用原生信任库，单独说明应用覆盖范围 {#platforms}

| 平台 | 拟议系统适配器 | 精确移除 |
|---|---|---|
| macOS | 通过受支持的 `security` 操作导入 System Keychain，并设置管理员 TLS 信任；选择 SSL 策略，不设置允许错误的例外 | 按指纹移除本工具添加的管理员信任，再删除本工具拥有的钥匙串条目；保留原有证书／策略 |
| Debian / Ubuntu | 写入自有 PEM `.crt` 文件 `/usr/local/share/ca-certificates/barn-pigsty-<sha256>.crt`，运行 `update-ca-certificates` | 仅删除匹配的自有文件，按平台支持的移除流程重新生成并验证信任库 |
| RHEL / Rocky / AlmaLinux | 写入自有 anchor `/etc/pki/ca-trust/source/anchors/barn-pigsty-<sha256>.crt`，运行 `update-ca-trust extract` | 仅删除匹配的自有 anchor，重新 extract 并验证 |
| 其他 Linux 信任库布局 | 报告适配器暂不支持，并提供可导出的公共证书 | 保留显式手工导入路径 |
{.wide .expand}

这些机制依据 [Apple 信任设置](https://support.apple.com/en-asia/guide/keychain-access/kyca11871/mac)、[Ubuntu 安装／移除流程](https://ubuntu.com/server/docs/how-to/security/install-a-root-ca-certificate-in-the-trust-store/) 和 [RHEL 共享信任库](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/securing_networks/using-shared-system-certificates_securing-networks)。本机 `security help` 已确认管理员信任域、SSL 策略和按 SHA-256 删除条目的语法，没有执行修改命令。组合应用前，Linux 适配器须先检测相应能力，包括 CA 工具是否已安装。

系统信任与应用信任分别验收。macOS Chrome 支持 System Keychain 中显式设置的 SSL 信任；Firefox 在相应设置启用时支持 macOS 系统根证书。Linux Firefox、Chrome、隔离安装包及语言运行时须单独验证。若浏览器仍拒绝 CA，首版工具应报告并提供独立的显式导入路径，不能悄悄改写所有浏览器 profile，也不能因系统更新成功就宣称全部浏览器可用。依据：[Chrome 本地信任与证书管理器](https://chromium.googlesource.com/chromium/src/+/main/net/data/ssl/chrome_root_store/faq.md)、[Mozilla 各平台 CA 集成](https://support.mozilla.org/en-US/kb/setting-certificate-authorities-firefox)。

## 让重复初始化与清理可预测 {#lifecycle}

| 事件 | 宿主动作与授权 |
|---|---|
| 首次配置域名与 CA | 审查两项内容后，执行必要的特权写入 |
| IP、名称及已生效的 CA 信任相同 | 无操作，不调用 sudo，不重复生成信任库 |
| 客机停止／启动／重建，且保留同一 CA | 不更新宿主 |
| 同一 CA 下的叶子证书续期 | 不更新宿主 |
| 入口 IP 或固定名称表变化 | 显式更新 hosts，保留未变的 CA 信任 |
| 出现新的 CA 指纹 | 停止普通同步，要求显式传拟议的 `--replace-ca OLD_SHA256`，并预览／固定新 CA |
| `destroy` 或删除 `BARN_HOME` | 保留集成，直到显式移除；所有权信息保存在部署状态之外 |
| `remove --apply` | 仅移除自有名称和信任，保留初始化前已存在的内容 |
{.wide}

在 `BARN_HOME` 之外保存 root 所有的操作记录：所属 UID、profile 版本、规范名称／IP、公共 CA DER／指纹、精确信任目标、原先是否存在，以及本次真正拥有的变更。原本已受信任的相同 CA 标记为 `pre-existing`，不能取得其所有权。已有信任策略存在冲突时，需要显式手工处理，不能自动扩大信任。删除自有证书后，其他来源仍可能信任它；应报告剩余信任，不能删除外部副本。

CA 轮换必须显式进行：验证新根证书，安装并核实新信任，再仅在操作记录证明旧信任属于本工具且用户要求替换时移除旧信任。部署切换 CA 还可能需要更新服务证书，宿主命令不负责这一步。停用旧信任前，需要考虑其他实验环境是否仍复用该 CA。

hosts 与信任库不能组成一个原子事务。先同时检查两项，再依次应用 CA 信任和已审查的 hosts 快照，逐步记录完成状态。失败时只撤销本次新增且仍与记录匹配的变更，保留并发编辑，报告可能存在的部分状态。正常移除先删自有 hosts 发布，再删自有信任。不能恢复整份旧 hosts、钥匙串或信任设置快照。

## 保持实现规模小、边界清楚 {#implementation}

1. **Pigsty 固定配置**：实现 `bin/sandbox-host`，只处理固定名单、显式 IP 和公共 CA 输入，不解释 Ansible、不探测运行角色、不生成 CA 材料。发现旧 `# pigsty dns` 行时，按 [DNS 研究中的显式迁移流程](/zh/blog/design/pigsty-host-dns/#lifecycle-and-migration) 报告。
2. **Barn hosts 边界**：复用唯一管理块、规范记录及完整预览；为已有 `all.vars.vm_hosts` 形状增加纯 hosts 消费路径，不伪造 VM 节点，不增加第二种 VM 清单格式。从字面地址推导唯一私有 `/24` 并检查保留范围。这是必须新增的能力，已审计原型目前会拒绝纯记录清单；普通 VM 清单校验保持不变。采用前述 inventory 来源保护，防止裸节点发布删掉核心域名。
3. **Barn 信任边界**：新增通用 CA 计划／状态／安装／移除操作，以及供包装脚本使用的组合审查操作。扩展现有唯一特权 helper，使用有边界的类型化操作和固定平台目标；Pigsty 域名留在 Barn 之外。集成前补齐 helper 内部范围校验与宿主级锁，不给当前 helper 配置永久 sudo 权限。
4. **验收**：仓库检查及 macOS、Linux 真机验收通过后，才把命令写成可用功能。通用导出器和 DNS daemon 不作为这份固定配置的发布门槛。
{.steps}

| 测试领域 | 必须具备的证据 |
|---|---|
| 固定数据 | 精确八名称快照、自定义 IP、保留地址拒绝、大小写／冲突检查、不依赖清单或服务 |
| CA 输入 | PEM／DER 相同指纹身份，非法／过期／非 CA／私钥／证书包拒绝，CA 缺失，预览后输入变化 |
| 重复与所有权 | 第二次运行不调用特权路径；移除时保留原有信任；同名不同 CA 不静默替换；保留外部修改 |
| 失败恢复 | 信任工具失败、hosts 冲突／并发、两步之间中断、非交互授权失败、删除部署状态后的重装 |
| 真实客户端 | macOS System Keychain 与默认 TLS 客户端；Debian 系和 RHEL 系信任库；系统解析；首页 SAN／证书链；承诺支持的浏览器独立验收，不使用跳过校验的参数 |
| 生命周期 | 叶子续期、VM 重启无需 setup；CA 替换与入口 IP 变化只展示必要更新；完整移除后验证自有变更消失 |
{.wide}

本次修订核实了源码语义与官方平台机制，并运行文档检查；没有验收已安装的 CA 适配器或真实 HTTPS portal。产品默认方案已确定：固定域名与原生系统 CA 信任、显式 setup、重复无变化时不操作、按所有权清理。实际命令发布版本，以及逐个承诺支持的浏览器／平台组合，仍须经过验收决定。
