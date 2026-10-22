---
title: macOS 虚拟机
linkTitle: macOS 虚拟机
description: 用 barn mac 在 Apple 芯片 Mac 上运行 macOS 27 虚拟机：创建、连接、共享文件与剪贴板，以及清理。
weight: 20
icon: fa-brands fa-apple
---

`barn mac` 在 Apple 芯片 Mac 上创建并运行可丢弃的 macOS 虚拟机，适合测试、构建与复现 macOS 特有的问题。
每台虚拟机带有管理员账号、免密 sudo、固定的 SSH 密钥和固定地址。
Barn 通过 Apple 的 Virtualization 框架以当前用户身份运行虚拟机，无需管理员权限。

Mac 虚拟机与 Linux 实验环境相互独立。它们不读取 `barn.yml`，也不加入 Pigsty 清单。虚拟机数据位于 `$BARN_HOME/mac`（默认 `~/.barn/mac`）下。Linux 的 `destroy` 与 `purge` 不会影响它们。

## 前提条件

- 一台运行 **macOS 27 或更高版本**的 Apple 芯片 Mac，且已有用户登录桌面。客机同样运行 macOS 27。
- 第一台虚拟机约需 **65 GiB** 可用空间。这包括从 Apple 下载的约 25 GiB 恢复镜像、安装后约 27 GiB 的基础镜像，以及启动所需的余量。Barn 会保留恢复镜像，直到你清理它。此后每台虚拟机按自身改动增长，
  上限是磁盘容量，默认 100 GiB。
- 与 0.9.1 CLI 配套的原生组件 **Barn.app**；只有自行构建组件时才需要 Xcode 27+。
- 不需要 sudo：每台虚拟机、它的网络和桌面都以当前用户身份运行。

原生运行时支持一台 Mac 上**同时最多运行两台 macOS 虚拟机**，其他工具的虚拟机和 macOS
安装过程也计算在内。可以创建多台虚拟机，同时运行其中任意两台。使用时须遵守适用的 Apple 软件许可。

## 安装 {#install}

[安装 Barn 0.9.1](../installation/) 后，检查 Mac 组件：

```bash
barn version
barn mac doctor
```

**0.9.1 发行归档与 Homebrew 配方不包含 `Barn.app`。** 原生组件继续作为源码预览，
需要自行构建；组件就绪前，`doctor` 会报告缺失。

在 Apple Silicon 上使用 **Xcode 27+** 与 [Go 1.27.3](../source-build/)，
从 `v0.9.1` 标签构建：

```bash
git clone --branch v0.9.1 https://github.com/pgsty/barn.git
cd barn
BARN_VERSION=0.9.1 make mac-build
export PATH="$PWD/bin/mac:$PATH"
barn version
barn mac doctor
```

`bin/mac` 包含 CLI、配套 hosts helper、原生 runner 与 `Barn.app`。保留完整目录。
未配置签名变量时，本地构建使用 ad-hoc 签名，并非已公证的发行下载。
`doctor` 检查宿主、组件签名、可用空间与已有虚拟机，不验证 Apple 公证状态。
详情见[源码构建与签名](../source-build/#mac-component)。替换已有组件前，先停止使用它的 Mac 虚拟机。

## 创建第一台机器

```bash
barn mac up
```

如果这台 Mac 尚未准备 macOS 基础镜像，`up` 会列出要求并请求确认：

```text
→ macOS 27.0 (26A428) is not prepared on this Mac yet.
download:  24.8 GiB from Apple (updates.cdn-apple.com)
then:      install macOS once into a reusable base (about 20 minutes)
free:      551.2 GiB
Download macOS from Apple now? [Y/n]
```

确认后，Barn 依次：

1. **只从 Apple 官方下载恢复镜像**。Barn 用 Apple 公布的 SHA-256 校验镜像。下载中断后从断点继续。
2. **一次性安装 macOS**，得到一个从未启动过的*基础镜像*。安装期间会占用两个 macOS
   虚拟机名额中的一个。
3. **创建 `mac1`**，以写时复制的方式克隆基础镜像。Barn 启动虚拟机并创建账号，再等待 SSH 与 sudo 可用。

```text
  ✓  mac1 created and ready · macOS 27.0 (26A428) · alice@10.10.20.10
shell:     barn mac ssh mac1
desktop:   barn mac open mac1
```

之后的虚拟机会复用已安装的基础镜像，跳过完整的 macOS 恢复安装。
启动耗时取决于宿主资源与首次初始化。Barn 0.9.1 首次下载固定使用
**macOS 27.0 (26A428)**。上面的耗时和可用空间为示例。`image update` 才会显式选择更新的受支持 macOS 27 基础镜像。

如果已有 Apple 的恢复镜像，可以直接使用。它与数据在同一个 APFS
卷上时，Barn 通过克隆共享已有数据块；否则校验后原地使用：

```bash
barn mac up --ipsw ~/Downloads/UniversalMac_27.0_26A428_Restore.ipsw
```

没有终端时（例如在脚本中），`up` 只有在传入 `--yes` 后才会下载 25 GiB 镜像。`barn mac setup` 可以提前准备基础镜像而不创建虚拟机。

`--no-wait` 在虚拟机开始运行后就返回，不等待 SSH 配置与就绪。如果新虚拟机使用了该参数，还需执行不带 `--no-wait` 的 `barn mac up NAME` 完成初始化，之后再使用 `ssh` 或 `exec`。仅轮询 `ls` 不会安装 SSH 密钥或 sudo 配置。

## 使用机器

### 终端与命令

```bash
barn mac ssh                                  # 交互式终端
barn mac exec -- sw_vers                      # 执行一条命令
barn mac ssh -- 'id; sudo -n true && echo sudo works'
```

```text
ProductName:		macOS
ProductVersion:		27.0
BuildVersion:		26A428
```

账号名与你的 macOS 用户名相同，并拥有免密 sudo。创建时，可用 `--user` 指定其他账号名。`ssh` 与普通 ssh 一样，把命令行交给客机 shell。`exec` 保留参数边界。两者都返回客机命令的退出码，
`--json` 会记录标准输出、标准错误与退出码：

```bash
barn --json mac exec -- sh -c 'echo out; exit 3'
```

```json
{
  "command": "exec",
  "node": "mac1",
  "host": "10.10.20.10",
  "arguments": ["sh", "-c", "echo out; exit 3"],
  "success": false,
  "exit_code": 3,
  "stdout": "out\n"
}
```

以上 JSON 有删节，完整字段见 [Mac 命令参考](../../reference/mac/#json-output)。

### 桌面

```bash
barn mac open
```

桌面在适合屏幕大小的原生窗口中打开，调整窗口大小时，客机分辨率随之改变。
使用 **View → Enter Full Screen** 进入全屏。

关闭窗口后虚拟机继续运行，执行 `open` 可重新显示窗口；如果虚拟机已停止，该命令会先启动它。
窗口获得焦点时，键盘快捷键交给客机，因此宿主操作需使用菜单栏：

| 菜单 | 作用 |
|---|---|
| **Machine → Share Clipboard** | 在本次运行中开关剪贴板共享 |
| **Machine → Restart…** | 重启客机中的 macOS |
| **Machine → Shut Down…** | 正常关机，与 `barn mac stop` 相同 |
| **Window → Keep Running in Background** | 隐藏窗口，虚拟机继续运行 |
| **Barn → Quit Barn…** | 选择让虚拟机在后台继续运行，或关机 |

App 改名变更中的对应菜单为 **Barn → Quit Barn…**。
宿主注销或关机时，Barn 会请求客机正常关机；如果客机超时仍未停止，Barn 会将其断电。

锁屏和桌面中的管理员授权需要登录密码。每台虚拟机的密码随机生成，可以直接复制而不在终端显示：

```bash
barn mac password --copy
```

### 剪贴板

剪贴板在焦点切换时同步纯文本。进入客机窗口后，可以粘贴在 Mac 上复制的内容。切换到其他应用时，在客机中复制的内容会同步回 Mac。内容经由这台虚拟机自己的 SSH 连接传输，客机中无需安装任何程序。
被密码管理器标记为敏感的内容不会离开 Mac。图片和文件不会同步。

执行 `barn mac configure mac1 --clipboard off` 可为某台虚拟机关闭剪贴板共享，
从这台虚拟机下次启动起生效。

### 共享目录

创建虚拟机时共享 Mac 上的目录，客机把它们挂载在 `/Volumes/My Shared Files/<名称>`：

```bash
barn mac up dev --cpu 8 --memory 16G --share ~/src --share docs=~/Documents:ro
barn mac exec dev -- ls "/Volumes/My Shared Files"
```

名称默认取目录路径的最后一段。`:ro` 表示只读。共享的目录必须已存在，不能是符号链接。Barn 不会创建或删除共享目录。之后要调整共享，先停机再用 `configure`：

```bash
barn mac stop dev
barn mac configure dev --share data=/Volumes/Work/data --unshare docs
barn mac start dev
```

Mac 修改共享文件后，macOS 客机可能在短时间内仍看到旧内容。需要立即使用最新文件时，
可通过 `scp` 或 `rsync` 将文件复制到客机自己的磁盘。

### 在其他工具中使用 SSH

第一台虚拟机就绪时，Barn 会在 `~/.ssh/config` 中加入一个带标记的 `Include`。之后
`ssh mac1`、`scp`、`rsync` 以及支持 Remote-SSH 的编辑器都能按名称访问每台虚拟机，
并使用它自己的密钥和固定的主机密钥：

```bash
ssh mac1 'uptime'
rsync -a ./project/ mac1:project/
barn mac ssh-config              # 打印这些条目
barn mac ssh-config --remove     # 只移除 Barn 添加的内容
```

生命周期命令会保持这些条目为最新。若 `~/.ssh/config` 是由 dotfile 工具管理的链接，
Barn 不会修改它，而是打印需要你手动添加的 `Include` 行。

`--remove` 还会禁用自动集成，直到执行 `barn mac ssh-config --install`。
如果 SSH 配置已将某个虚拟机名用于其他主机，Barn 会保留原别名，仅按 IP 地址发布该虚拟机
的条目。`barn mac ssh` 与 `exec` 始终使用虚拟机自己的密钥和固定的主机密钥，
不依赖你的个人 SSH 密钥与配置。

## 多台机器

为每台虚拟机命名。创建参数只对新虚拟机生效。下面沿用前面的 `dev` 示例：

```bash
barn mac up dev --cpu 8 --memory 16G
barn mac ls
```

```text
NAME  STATE    ADDRESS      SSH    USER   OS          CPU  MEMORY  DISK                 SHARED
dev   running  10.10.21.10  ready  alice  macOS 27.0    8  16 GiB  504.0 MiB / 100 GiB    src,data
mac1  running  10.10.20.10  ready  alice  macOS 27.0    4   8 GiB  4.7 GiB / 100 GiB
limit:     2 of 2 macOS VMs are running; stop one before starting another
```

名称使用小写字母、数字和中间连字符，以字母开头。不带名称的命令作用于唯一的一台虚拟机或
`mac1`。无法确定时，必须指定名称。`DISK` 显示虚拟机当前占用的空间与容量。容量属于基础镜像：
`--disk` 与已准备的基础镜像不同时，会先安装另一个基础镜像，这需要再次使用恢复镜像。

每台虚拟机有自己的私有网络。候选网段从 `10.10.20.0/24` 开始，客机地址为 `.10`；
Barn 会跳过与局域网、VPN、Linux 环境或其他 Mac 虚拟机冲突的子网。虚拟机可以访问宿主并通过 NAT 建立出站连接。
同一个 Barn 数据目录下已有两台虚拟机在运行时，第三台会在创建任何内容之前被拒绝，
并指出可以停止哪一台：

```bash
barn mac up build --user ci
```

```text
error: dev and mac1 are running; macOS allows 2 macOS virtual machines at a time
next: barn mac stop mac1
```

## 日常管理

```bash
barn mac stop dev               # 通过 macOS 正常关机
barn mac start dev              # 启动并等待 SSH
barn mac restart dev            # 先停再启，使配置变更生效
barn mac stop --all             # 所有机器
```

`stop` 执行正常关机。如果虚拟机在两分钟后仍运行，Barn 会将其断电，并在结果中说明。`stop --force` 立即断电。断电会丢失客机中未保存的内容。
`start --recovery` 启动到 macOS 恢复模式并显示桌面。

`up` 从不重新配置已有虚拟机。传入与现有配置不同的参数时，它会拒绝执行并给出应使用的命令：

```text
error: dev already exists, so --cpu would not apply; its configuration and data were preserved
next: barn mac configure dev --cpu 4
```

虚拟机停止时，`configure` 可以修改 CPU、内存、共享目录与网络。剪贴板共享可随时修改。变更从下次启动起生效：

```bash
barn mac stop dev
barn mac configure dev --cpu 6 --memory 12G --subnet auto
barn mac start dev
```

`recreate` 用基础镜像中全新的 macOS 替换虚拟机，同时保留名称、账号、资源、共享目录与地址。`destroy` 删除虚拟机。两者都会说明将删除的内容，再要求输入命令名确认。没有终端时，用 `--force` 确认。

按需选择重建或删除命令：

```bash
barn mac recreate dev
barn mac destroy dev
```

| 操作 | 客机磁盘与应用 | 设置、地址与账号 |
|---|---|---|
| `stop`/`start`、`restart`、重复 `up` | 保留 | 保留 |
| `configure` | 保留 | 按要求修改 |
| `recreate` | 换成全新的 macOS | 保留；密码与 SSH 密钥重新生成 |
| `destroy` | 删除 | 删除 |

以上操作都不会修改共享的基础镜像。删除虚拟机时，基础镜像也会保留。

## macOS 版本与磁盘空间

```bash
barn mac image ls
```

```text
KIND  OS          BUILD   STATE  ON DISK   CAPACITY  USED BY
base  macOS 27.0  26A428  ready  26.7 GiB  100 GiB   mac1,default
```

升级需要显式执行命令。`barn mac image update` 向 Apple 查询最新的 macOS 27。确认后，Barn 下载镜像，再将其设为新虚拟机的基础镜像。已有虚拟机保持原来的 macOS，直到执行
`barn mac recreate NAME --update`。`up` 与 `start` 从不改变虚拟机的 macOS 版本。

重建会保留磁盘容量。使用自定义 200 GiB 磁盘的虚拟机，需要新 macOS 的同容量基础镜像。若收到提示，先执行 `barn mac setup --disk 200G`，再重试 `recreate NAME --update`。
客机内部的修改（包括客机自己的系统更新）独立于 Barn 的基础镜像管理。

`image prune` 列出没有虚拟机使用、且不是默认的基础镜像。加 `--yes` 才会删除。
`--installers` 会一并处理已下载的恢复镜像与未完成的下载。APFS 克隆共享数据块，因此 `ON DISK` 与各虚拟机的磁盘数字可能重复计算同一空间。
不要将这些数字相加作为总占用。

```bash
barn mac image prune --installers         # 先查看
barn mac image prune --installers --yes   # 再删除
```

## 故障排查

先执行 `barn mac doctor`：它检查宿主、组件、基础镜像与每台虚拟机，并在有建议时给出
后续命令。其 40 GiB 空间检查不包含首次下载的全部需求：setup 还需为 IPSW 尚未下载的
部分预留空间，完整恢复镜像约 25 GiB。`barn mac logs [名称]` 显示虚拟机的运行日志：启动、网络、关机以及 Apple
Virtualization 的错误。

| 现象 | 处理方法 |
|---|---|
| 启动时报 `network … overlaps route …` | VPN 或其他工具占用了该网段。执行 `barn mac configure NAME --subnet auto`。 |
| `macOS allows 2 macOS virtual machines at a time` | 停止提示中的某台虚拟机，或退出其他工具的 macOS 虚拟机。 |
| 第三方 SSH 客户端执行 `ssh mac1` 报 "No route to host" | macOS 的“本地网络”隐私控制可能阻止该应用访问私有网络。请在**系统设置 → 隐私与安全性 → 本地网络**中检查并允许访问，或改用 `/usr/bin/ssh`。`barn mac ssh` 与 `exec` 使用 Apple 自带工具，通常可以避开第三方客户端的权限问题。 |
| `mac_runner_missing` 或 `mac_runner_protocol` | 保留 CLI 与原生组件的布局。按上文构建完整组件。仅含 CLI 的归档不会补上缺失的 App；需使用带原生载荷的发行包，或自行构建完整组件。 |
| 通过 SSH 登录 Mac 后启动失败 | 在 Mac 桌面会话的终端中运行 `barn mac`。虚拟机需要已登录用户的图形会话。确保登录钥匙串已解锁。 |

在虚拟机中登录 Apple 账户并不可靠。Barn 不支持 USB 设备、快照和挂起虚拟机。

## 清理

先检查还保留了哪些虚拟机，再将下面的示例名称替换为实际要删除的名称：

```bash
barn mac ls                               # 先检查机器名称
barn mac destroy mac1 dev                  # 确认删除这些机器
barn mac image prune --installers --yes     # 删除不再使用的镜像
```

删除最后一台虚拟机时，`~/.ssh/config` 中的相应条目也会一并移除。Barn 会保留默认基础镜像，供之后创建虚拟机使用。如需删除所有 Mac 文件（含默认基础镜像），先删除全部虚拟机。用 `barn mac ssh-config --remove` 移除 Mac SSH 集成。再删除 `$BARN_HOME/mac`（默认 `~/.barn/mac`）。除该目录外，Mac 功能还会写入：

- `~/.ssh/config` 集成及 `~/.ssh/barn-mac_config` 片段。
- `~/Library/Preferences/io.pgsty.barn.mac-runner.plist` 中的桌面窗口位置（改名后的 App 使用 `com.pgsty.barn.plist`）。
- `/tmp` 下的短路径运行目录。

整个过程都不需要 sudo。
