---
title: Mac 命令
description: barn mac 的命令与参数、机器规则、JSON 结果、失败原因、网络与文件。
weight: 25
icon: fa-brands fa-apple
---

> [!IMPORTANT]
> **Barn 0.9.0 发布候选，尚未发布。** 本页描述改名后的 `barn mac`，
> 使用全新 Barn 状态，不提供旧开发环境迁移。改名前的实机记录保留在
> [当前状态](../../about/status/#macos-guests)，不代表改名后已经完成同等验收。
> 请以实际运行的 `barn mac --help` 为准。

```text
barn [--json|--yaml] [-v|--verbose] mac <command> [flags] [name...]
```

`barn mac` 需要 Apple 芯片与 macOS 27 或更高版本，以已登录用户身份运行，拒绝以
root 运行。在其他宿主上该命令默认隐藏，需要 Mac 组件的命令会以
`mac_host_unsupported` 失败。不带子命令的 `barn mac` 等同于 `barn mac ls`。

## 命令

| 命令 | 用途 |
|---|---|
| `ls` | 列出所有机器的状态、地址、SSH、macOS 版本、资源与共享；别名 `list`、`status`、`st` |
| `up [name]` | 按需创建机器，启动并等待 SSH 与 sudo 可用 |
| `start [name...]` | 启动已有机器 |
| `stop [name...]` | 正常关机，两分钟后仍未停止则断电 |
| `restart [name]` | 先停后启，使配置变更生效 |
| `open [name]` | 显示桌面，机器已停止时先启动 |
| `ssh [name]` | 交互式终端；`--` 之后是交给客机 shell 的命令行 |
| `exec [name] -- cmd` | 执行命令并保留参数边界 |
| `configure name` | 修改机器设置 |
| `recreate name` | 用全新的 macOS 替换机器，保留其设置 |
| `destroy name...` | 删除机器 |
| `password [name]` | 显示或复制登录密码 |
| `ssh-config` | 打印、安装或移除 OpenSSH 条目 |
| `logs [name]` | 最近的运行日志 |
| `setup` | 只准备 macOS 基础镜像，不创建机器 |
| `image ls` | 列出恢复镜像与基础镜像及使用它们的机器；别名 `list` |
| `image update` | 把 Apple 最新的 macOS 27 准备为默认基础镜像 |
| `image prune` | 列出不再使用的镜像，加 `--yes` 才删除 |
| `doctor` | 检查宿主、组件、基础镜像与每台机器 |

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

不带机器名称的命令作用于唯一的一台机器或 `mac1`；有多台机器且没有 `mac1` 时会要求
指定名称。`start` 与 `stop` 可接收多个名称或 `--all`。`destroy` 与 `recreate` 会先说明
将删除的内容，并要求输入命令名确认；没有终端时用 `--force` 确认。

### 参数取值

| 参数 | 取值 |
|---|---|
| `--cpu` | 虚拟 CPU 数，至少 2，不超过 Mac 的逻辑 CPU 数；默认 4 |
| `--memory` | `16G`、`16GiB`、`16GB` 或字节数；至少 4 GiB，不超过物理内存；默认 8 GiB |
| `--disk` | 基础镜像容量，至少 32 GiB；默认沿用已准备的基础镜像，即 100 GiB。其他容量会安装另一个基础镜像 |
| `--user` | 管理员账号；默认你的 macOS 用户名，该名称不合法时为 `barn` |
| `--share` | `[name=]path[:ro\|:rw]`，可重复，最多 8 个；名称默认取路径最后一段；`~/` 展开为主目录 |
| `--clipboard` | `on` 或 `off`；默认 on |
| `--subnet` | 规范的私有 `/24`，例如 `10.10.30.0/24`；`auto` 表示第一个空闲网段 |

`up` 遇到与已有机器不同的创建参数时直接拒绝而不是忽略，并在 `next:` 行给出修改方法。
CPU、内存、共享、网段与剪贴板用 `configure` 修改。账号与磁盘容量在机器的整个生命周期内
固定，`recreate` 也会保留它们：需要其他取值时请另建机器。更换 macOS 版本需先执行
`image update`，再执行 `recreate --update`。

## 机器

- **名称**：1–32 个小写字母、数字或中间连字符，以字母开头，例如 `mac1`、`dev`、`build-2`。
- **运行上限**：每台 Mac 同时运行两台 macOS 虚拟机，其他工具与 macOS 安装过程也计算在内。
  Barn 从不为腾出名额而停止任何机器。
- **账号**：管理员账号，免密 sudo、SSH 密钥登录、桌面自动登录，并开启远程登录；
  SSH 密码登录被关闭。登录密码随机生成，保存在机器目录的 `password` 文件中。
- **客机名称**：电脑名称即机器名；本地主机名为 `barn-<name>`，因此客机以
  `barn-<name>.local` 应答。
- **共享**：一个由 macOS 挂载到 `/Volumes/My Shared Files/<name>` 的 VirtioFS 设备。
  共享必须是已存在的目录，不能是符号链接，只能在机器停止时修改。
- **剪贴板**：纯文本，在窗口获得或失去焦点时经这台机器的 SSH 连接同步；最大 1 MiB；
  标记为敏感的内容不会发送。
- **停止**：通过客机中的 macOS 正常关机；两分钟后仍在运行则断电，结果中带
  `"forced": true`。`--force` 立即断电。

## 网络

每台机器的网络由它自己的 runner 进程在启动时创建，停止时随之消失，不涉及任何守护进程或
root 权限。

| 项目 | 取值 |
|---|---|
| 网段 | 在 `10.10.20.0/24` 到 `10.10.59.0/24` 之间选择第一个空闲的私有 `/24`，避开宿主路由和其他机器；也可用 `--subnet` 指定 |
| 网关 | `.1`，即 Mac |
| 客机地址 | `.10`，通过对机器 MAC 地址的 DHCP 保留分配 |
| 可达性 | 经 NAT 访问 Mac 与互联网；不能访问其他机器与局域网 |

宿主路由（例如 VPN）与机器网段重叠时，`start` 会以 `mac_subnet_in_use` 拒绝启动。
SSH 主机密钥绑定到机器实例而不是地址，因此 `configure --subnet` 后信任关系不变。

macOS 的“本地网络”隐私控制会阻止未获授权的第三方程序连接这些网络，报错为
"No route to host"；需要在**隐私与安全性 → 本地网络**中允许对应应用。Barn 自身通过
Apple 的 `/usr/bin/nc` 与 `/usr/bin/ssh` 连接，不受该限制。

## JSON 输出 {#json-output}

所有命令都支持 `--json` 与 `--yaml`，进度信息输出到标准错误。

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

`up`、`restart`、`open`、`recreate` 与 `configure` 返回单个结果；`start`、`stop` 与
`destroy` 返回 `{"machines": [...]}`，每台机器一项，只指定一台时也是如此。

```json
{"name": "mac1", "action": "created", "state": "running", "ready": true,
 "address": "10.10.20.10", "user": "alice", "version": "27.0", "build": "26A428"}
```

| 字段 | 取值 |
|---|---|
| `action` | `created`、`started`、`running`（已在运行）、`restarted`、`recreated`、`opened`、`configured`、`stopped`、`powered_off`、`already_stopped`、`destroyed`、`absent` |
| `forced` | 正常关机未完成、只能断电时为 `true` |
| `window` | 显示了桌面时为 `true` |
| `warnings` | 不影响结果的后续事项，例如下次启动才生效的变更 |

`exec --json` 返回与 Linux `barn exec --json` 相同的对象：`node` 为机器名，
`exit_code`、`stdout` 与 `stderr` 来自客机。交互式 `ssh` 没有 JSON 形式。

## 失败

退出码与 [Barn 命令行](../cli/#退出码)一致；远程命令自身的退出码经 `ssh` 与
`exec` 原样返回。JSON 失败结果带有稳定的 `reason` 与 `next` 命令：

| Reason | 退出码 | 含义与下一步 |
|---|---|---|
| `mac_host_unsupported` | 3 | 不是 Apple 芯片，或 macOS 低于 27 |
| `mac_runner_missing` | 3 | 命令行旁边没有安装 Mac 组件 |
| `mac_runner_protocol` | 3 | 命令行与组件来自不同构建，请一起安装 |
| `mac_root` | 2 | 请以普通登录用户运行，不要使用 sudo |
| `mac_download_consent` | 2 | 没有终端时下载 macOS 需要 `--yes`，或改用 `--ipsw` |
| `mac_machine_absent` | 4 | 没有该名称的机器；执行 `barn mac up NAME` |
| `mac_not_initialized` | 4 | 机器尚未完成首次启动；执行 `barn mac up NAME` |
| `mac_not_running` | 4 | `ssh`/`exec` 需要机器正在运行；执行 `barn mac start NAME` |
| `mac_running` | 4 | 该变更需要先停机；执行 `barn mac stop NAME` |
| `mac_configuration_conflict` | 4 | `up` 的参数与已有机器不同；按提示执行 `configure` 或其他命令 |
| `ssh_config_linked` | 4 | `~/.ssh/config` 是链接；请手动加入打印出的 `Include` 行 |
| `mac_vm_limit` | 6 | 已有两台 macOS 虚拟机在运行；停止提示中的那台 |
| `mac_subnet_in_use` | 6 | 宿主路由与机器网段重叠；执行 `configure NAME --subnet auto` |
| `disk_full` | 6 | 可用空间不足以下载或安装 macOS |
| `mac_machine_damaged` | 7 | 启动过的机器丢失了磁盘或身份文件；其目录原样保留 |
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
```

运行时 socket 位于 `/tmp/barn-mac-<uid>-<hash>/`。`ssh-config` 写入
`~/.ssh/barn-mac_config`，并在 `~/.ssh/config` 中加入一个 `# barn-mac:include`
区块，与 Linux 的 `# barn:include` 区块互不影响。桌面窗口位置保存在
`~/Library/Preferences/io.pgsty.barn.mac-runner.plist`。

Barn 在客机中写入 `~/.ssh/authorized_keys`、`/private/etc/sudoers.d/80-barn`、
`/etc/ssh/sshd_config.d/000-barn.conf`，设置电脑名称与本地主机名，并用 `pmset`
关闭睡眠。
