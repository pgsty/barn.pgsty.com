---
title: Mac 命令
description: barn mac 的命令与参数、机器规则、JSON 结果、失败原因、网络与文件。
weight: 25
icon: fa-brands fa-apple
---

```text
barn [--json|--yaml] [-v|--verbose] mac <command> [flags] [name...]
```

运行 macOS 客机需要 Apple 芯片与 macOS 27 或更高版本。请以已登录用户身份运行。
需要原生 runner 的命令会以 `mac_root` 拒绝 root，以 `mac_host_unsupported` 拒绝不支持的宿主。
Linux 与 Intel Mac 的顶层帮助默认隐藏该命令。
`image ls` 等读取本地记录的操作不需要原生 runner。
不带子命令的 `barn mac` 等同于 `barn mac ls`。

本页描述 0.9.1 命令接口与 `Barn.app`，runner 协议仍为 2。
0.9.1 的原生组件需要从源码构建，详情见[安装](../../start/macos/#install)与
[源码构建](../../start/source-build/#mac-component)。

## 命令

| 命令 | 用途 |
|---|---|
| `ls` | 列出所有虚拟机的状态、地址、SSH、macOS 版本、资源与共享；别名 `list`、`status`、`st` |
| `up [name]` | 按需创建虚拟机，启动并等待 SSH 与 sudo 可用 |
| `start [name...]` | 启动已有虚拟机 |
| `stop [name...]` | 正常关机，两分钟后仍未停止则断电 |
| `restart [name]` | 先停后启，使配置变更生效 |
| `open [name]` | 显示桌面，虚拟机已停止时先启动 |
| `ssh [name]` | 交互式终端；`--` 之后是交给客机 shell 的命令行 |
| `exec [name] -- cmd` | 执行命令并保留参数边界 |
| `configure name` | 修改虚拟机设置 |
| `recreate name` | 用全新的 macOS 替换虚拟机，保留其设置 |
| `destroy name...` | 删除虚拟机 |
| `password [name]` | 显示或复制登录密码 |
| `ssh-config` | 打印、安装或移除 OpenSSH 条目 |
| `logs [name]` | 最近的运行日志 |
| `setup` | 只准备 macOS 基础镜像，不创建虚拟机 |
| `image ls` | 列出恢复镜像与基础镜像及使用它们的虚拟机；别名 `list` |
| `image update` | 把 Apple 最新的 macOS 27 准备为默认基础镜像 |
| `image prune` | 列出不再使用的镜像，加 `--yes` 才删除 |
| `doctor` | 检查宿主、组件、基础镜像与每台虚拟机 |

### 各命令的参数

| 命令 | 参数 |
|---|---|
| `up` | `--cpu` `--memory` `--disk` `--user` `--share` `--clipboard` `--subnet` `--ipsw` `-y`/`--yes` `-n`/`--no-wait` `--open` |
| `start` | `--all` `-n`/`--no-wait` `--open` `--recovery` |
| `stop` | `--all` `--force` |
| `restart` | `-n`/`--no-wait` `--open` |
| `configure` | `--cpu` `--memory` `--share` `--unshare` `--clipboard` `--subnet` |
| `recreate` | `--update` `--force` `-n`/`--no-wait` |
| `destroy` | `--force` |
| `password` | `-c`/`--copy` |
| `ssh-config` | `-i`/`--install` `--remove` |
| `logs` | `-n`/`--lines`（默认 100，最多 10000） |
| `setup` | `--ipsw` `--disk` `-y`/`--yes` |
| `image update` | `--ipsw` `-y`/`--yes` |
| `image prune` | `--installers` `-y`/`--yes` |

对于名称可省略的命令，未指定名称时会选择唯一的虚拟机或 `mac1`。
有多台虚拟机且没有 `mac1` 时，命令会要求指定名称。
`start` 与 `stop` 可接收多个名称或 `--all`。
`destroy` 与 `recreate` 会先说明将删除的内容，再要求输入命令名确认。
没有终端时，用 `--force` 确认。

`--no-wait` 仅表示虚拟机已运行，不表示客机就绪。
新虚拟机仍需执行不带该参数的 `up NAME`，完成 SSH 密钥安装与 sudo 配置。

`ls` 不会完成初始化。普通 `start` 要求虚拟机已完成首次启动。
尚未初始化但已在运行的虚拟机，可用 `open` 显示首次启动界面。已停止时，使用 `up NAME --open`。
`--recovery` 跳过正常就绪等待，始终显示恢复模式桌面。

### 参数取值

| 参数 | 取值 |
|---|---|
| `--cpu` | 虚拟 CPU 数，至少 2，不超过 Mac 的逻辑 CPU 数；默认 4 |
| `--memory` | `16G`、`16GiB`、`16GB` 或字节数；须为整 MiB，至少 4 GiB，不超过物理内存；默认 8 GiB |
| `--disk` | 基础镜像容量，至少 32 GiB；默认沿用已准备基础镜像的容量，首个基础镜像为 100 GiB。其他容量需要匹配的基础镜像，不存在时会安装一个 |
| `--user` | 管理员账号；默认你的 macOS 用户名，该名称不合法时为 `barn` |
| `--share` | `[name=]path[:ro\|:rw]`，可重复，最多 8 个；名称默认取路径最后一段；`~/` 展开为主目录 |
| `--clipboard` | `on` 或 `off`（也接受 `true`/`false`、`yes`/`no`）；默认 on |
| `--subnet` | 规范的私有 `/24`，例如 `10.10.30.0/24`；`auto` 表示第一个空闲网段 |

创建参数与已有虚拟机不同时，`up` 拒绝执行，并在 `next:` 行给出修改方法。
使用 `configure` 修改 CPU、内存、共享、网段与剪贴板。
账号与磁盘容量在虚拟机的整个生命周期内固定，`recreate` 也会保留它们。
需要更换账号或磁盘容量时，请另建虚拟机。
更换 macOS 版本时，先执行 `image update`，再执行 `recreate --update`。

`recreate --update` 也会保留磁盘容量。
新 macOS 构建尚无对应容量的基础镜像时，请先准备该镜像。
例如，先执行 `barn mac setup --disk 200G`，再重试 `barn mac recreate NAME --update`。

Mac 容量使用二进制单位：`16G`、`16GB` 与 `16GiB` 都表示 16 GiB。
共享名称为 1–64 个字母、数字、点、下划线或连字符，必须以字母或数字开头。
`configure --share` 使用已有名称时，会替换其路径与选项。`--unshare` 仅移除该名称。

修改硬件、共享和网段前，必须停止虚拟机。
保存的剪贴板配置可在运行时修改，但下次启动才生效。若要立即控制本次会话的剪贴板同步，请使用桌面菜单。

## 机器

- **名称**：1–32 个小写字母、数字或中间连字符，以字母开头，例如 `mac1`、`dev`、`build-2`。
- **运行上限**：每台 Mac 同时运行两台 macOS 虚拟机，其他工具与 macOS 安装过程也计入此上限。
  Barn 不会为运行另一台虚拟机而停止已有虚拟机。
- **账号**：管理员账号，免密 sudo、SSH 密钥登录、桌面自动登录，并开启远程登录。
  Barn 关闭 SSH 密码登录。它随机生成登录密码，保存在虚拟机目录的 `password` 文件中。
- **客机名称**：电脑名称与虚拟机名相同。本地主机名为 `barn-<name>`，因此客机以 `barn-<name>.local` 应答。
- **共享**：macOS 将一个 VirtioFS 设备挂载到 `/Volumes/My Shared Files/<name>`。
  共享必须是已存在的目录，不能是符号链接。只能在虚拟机停止时修改共享。
- **剪贴板**：窗口获得或失去焦点时，Barn 经这台虚拟机的 SSH 连接同步纯文本。
  最大为 1 MiB。Barn 不发送标记为敏感的内容。
- **停止**：Barn 通过客机中的 macOS 请求正常关机。
  两分钟后仍在运行时，Barn 断电，结果中带 `"forced": true`。`--force` 立即断电。

`ls.running` 只统计当前 `BARN_HOME` 中运行、启动与停止过程中的虚拟机。
它不包含其他应用或其他 Barn 数据目录中的虚拟机。Apple 运行时仍执行宿主级虚拟机上限。

## 网络

每台虚拟机的运行进程（runner）在启动时创建网络，在停止时移除网络，无需守护进程或 root 权限。

| 项目 | 取值 |
|---|---|
| 网段 | 在 `10.10.20.0/24` 到 `10.10.59.0/24` 之间选择第一个空闲的私有 `/24`，避开宿主路由和其他虚拟机；也可用 `--subnet` 指定 |
| 网关 | `.1`，即 Mac |
| 客机地址 | `.10`，通过对虚拟机 MAC 地址的 DHCP 保留分配 |
| 可达性 | 访问宿主并通过 NAT 建立出站连接；各自使用独立子网，不桥接到局域网，也不配置入站端口转发 |

Barn 使用 Apple 的[共享模式 vmnet 网络](https://developer.apple.com/documentation/vmnet/vmnet_network_configuration_create(_:_:))。
独立子网描述网络拓扑，并不表示配置了防火墙隔离策略。

宿主路由（例如 VPN）与虚拟机网段重叠时，`start` 会以 `mac_subnet_in_use` 拒绝启动。
SSH 主机密钥绑定到虚拟机实例，而非地址。因此，`configure --subnet` 后信任关系不变。

macOS 的“本地网络”隐私控制可能阻止第三方客户端连接这些网络。
客户端有时会报告 "No route to host"。请检查**隐私与安全性 → 本地网络**中的应用权限。
Barn 的 Go SSH 传输使用 Apple 的 `/usr/bin/nc`，用户命令使用 `/usr/bin/ssh`。
此方式避开了直接第三方连接中观察到的限制。普通路由问题也可能引起该错误。

## JSON 输出 {#json-output}

命令支持 `--json` 与 `--yaml` 结构化结果。交互式 `ssh` 没有结构化输出。
Barn 将进度信息写入标准错误。

### `ls`

```json
{
  "schema_version": 2,
  "root": "/Users/alice/.barn/mac",
  "prepared": true,
  "base": {"version": "27.0", "build": "26A428", "base_id": "26A428-e16af589f4b705ca397f5b21"},
  "machines": [
    {
      "name": "mac1",
      "kind": "macos",
      "state": "running",
      "ready": true,
      "ssh": "ready",
      "address": "10.10.20.10",
      "address_stable": true,
      "ssh_host": "10.10.20.10",
      "ssh_port": 22,
      "user": "alice",
      "image": {"version": "27.0", "build": "26A428", "base_id": "26A428-e16af589f4b705ca397f5b21"},
      "cpus": 4,
      "memory_bytes": 8589934592,
      "disk": {"capacity_bytes": 107374182400, "allocated_bytes": 1202647040},
      "network": {"subnet": "10.10.20.0/24", "gateway": "10.10.20.1", "address": "10.10.20.10"},
      "shares": [{"name": "src", "host": "/Users/alice/src", "guest": "/Volumes/My Shared Files/src", "readonly": false}],
      "clipboard": true,
      "pid": 2545,
      "instance_id": "b1482ffc-2da7-45d9-ace5-c5f3193a9172",
      "warnings": []
    }
  ],
  "running": 1,
  "limit": 2
}
```

| 字段 | 取值 |
|---|---|
| `state` | `prepared`（尚未完成首次启动）、`starting`、`running`、`stopping`、`stopped`、`unknown` |
| `ready` | 仅当本次检查通过 SSH 登录客机并验证 sudo 时为 `true` |
| `ssh` | `ready`、`pending`（首次启动进行中）、`unavailable`、`offline`、`unchecked` |
| `observed` | 客机报告的 macOS 版本与基础镜像不同时出现 |
| `window_visible` | 桌面窗口显示期间出现 |
| `error`、`warnings` | 最近一次记录的失败，以及本次检查发现的 SSH 问题 |

### 生命周期结果

`up`、`restart`、`open`、`recreate` 与 `configure` 返回单个结果。
`start`、`stop` 与 `destroy` 返回 `{"machines": [...]}`，只指定一台时也是如此。
多台虚拟机的操作部分成功时，结果会保留成功项并单独报告失败，退出码为 5。
重试整组操作前，请先检查结果。

```json
{"name": "mac1", "action": "created", "state": "running", "ready": true,
 "address": "10.10.20.10", "user": "alice", "version": "27.0", "build": "26A428"}
```

| 字段 | 取值 |
|---|---|
| `action` | `created`、`started`、`running`（已在运行）、`restarted`、`recreated`、`opened`、`configured`、`stopped`、`powered_off`、`already_stopped`、`destroyed`、`absent` |
| `forced` | 正常关机未完成、只能断电时为 `true` |
| `window` | 显示了桌面时为 `true` |
| `warnings` | 不导致命令失败的提醒，例如变更要到下次启动才生效 |

`exec --json` 返回与 Linux `barn exec --json` 相同的对象。
`node` 为虚拟机名，`exit_code`、`stdout` 与 `stderr` 来自客机。
交互式 `ssh` 没有 JSON 输出。

`password --json` 包含密码。`password --copy --json` 则返回 `{"name":"mac1","copied":true}`。
未指定安装或移除时，`ssh-config` 返回 `fragment` 字符串。
`logs` 返回 `name` 与 `logs`。
`doctor` 返回 `ok` 和 `checks`。每项包含 `name`、`ok`、`detail` 以及可选的 `next`。
诊断未通过时，退出码为 3。

## 失败

退出码与 [Barn 命令行](../cli/#退出码)一致。
`ssh` 与 `exec` 原样返回远程命令自身的退出码。
已定义的失败使用稳定的 `reason`。有恢复建议时，结果附带 `next` 命令。
以下列出常见失败：

| 原因标识 | 退出码 | 含义与下一步 |
|---|---|---|
| `mac_host_unsupported` | 3 | 不是 Apple 芯片，或 macOS 低于 27 |
| `mac_runner_missing` | 3 | 命令行旁边没有安装 Mac 组件 |
| `mac_runner_protocol` | 3 | 组件使用不兼容的 runner 协议，请重新安装匹配的组件 |
| `mac_root` | 2 | 请以普通登录用户运行，不要使用 sudo |
| `mac_download_consent` | 2 | 没有终端时下载 macOS 需要 `--yes`，或改用 `--ipsw` |
| `mac_machine_absent` | 4 | 没有该名称的虚拟机；执行 `barn mac up NAME` |
| `mac_not_initialized` | 4 | 虚拟机尚未完成首次启动；执行 `barn mac up NAME` |
| `mac_not_running` | 4 | `ssh`/`exec` 需要虚拟机正在运行；执行 `barn mac start NAME` |
| `mac_running` | 4 | 该变更需要先停机；执行 `barn mac stop NAME` |
| `mac_configuration_conflict` | 4 | `up` 的参数与已有虚拟机不同；按提示执行 `configure` 或其他命令 |
| `ssh_config_linked` | 4 | `~/.ssh/config` 是链接；请手动加入打印出的 `Include` 行 |
| `mac_vm_limit` | 6 | 已有两台 macOS 虚拟机在运行；停止提示中的那台 |
| `mac_subnet_in_use` | 6 | 宿主路由与虚拟机网段重叠；执行 `configure NAME --subnet auto` |
| `disk_full` | 6 | 可用空间不足以下载或安装 macOS |
| `mac_machine_damaged` | 7 | 启动过的虚拟机丢失了磁盘或身份文件；其目录原样保留 |
| `mac_readiness_interrupted` | 130 | `stop` 中断了首次启动时的 SSH 等待 |

## 文件

```text
$BARN_HOME/mac/
  config.json                        安装标识与默认基础镜像
  images/ipsw/<build>.ipsw(.json)    Apple 恢复镜像；下载中为 .partial
  images/base/<id>/                  只读、从未启动过的 macOS 基础镜像
  slots/<name>/state.json            机器记录（schema 2）
  slots/<name>/disk.asif             基础镜像之上的写时复制磁盘层
  slots/<name>/machine-id.bin        Apple 机器标识
  slots/<name>/auxiliary-storage.bin 启动存储
  slots/<name>/id_ed25519(.pub)      机器的 SSH 密钥对
  slots/<name>/known_hosts           固定的主机密钥，别名为 barn-mac-<instance>
  slots/<name>/password              登录密码，权限 0600
  slots/<name>/runner.log            运行日志（barn mac logs）
  runtime/                          全局状态锁与各机器的操作锁
```

运行时套接字位于 `/tmp/barn-mac-<uid>-<hash>/`。
`ssh-config` 写入 `~/.ssh/barn-mac_config`，并在 `~/.ssh/config` 中加入一个 `# barn-mac:include` 区块。
此区块与 Linux 的 `# barn:include` 区块互不影响。

0.9.0 App 将桌面窗口位置保存在 `~/Library/Preferences/io.pgsty.barn.mac-runner.plist`。
0.9.1 App 使用 `~/Library/Preferences/com.pgsty.barn.plist`。

移除 SSH 集成时，Barn 在 `config.json` 中记录 `ssh_config_off`。
生命周期命令不会重新安装 SSH 条目，直到你显式执行 `ssh-config --install`。

CLI 根据解析符号链接后的自身位置查找 runner，支持 App 包、安装器与 Homebrew 的 `libexec` 布局。
开发调试时，可通过 `BARN_MAC_RUNNER` 指定绝对可执行文件路径。
CLI 在虚拟机操作前检查 runner 协议 2。
`doctor` 验证 runner 代码签名，不验证 Apple 公证。

Barn 在客机中写入 `~/.ssh/authorized_keys`、`/private/etc/sudoers.d/80-barn` 和 `/etc/ssh/sshd_config.d/000-barn.conf`。
它设置电脑名称与本地主机名，并用 `pmset` 关闭睡眠。
