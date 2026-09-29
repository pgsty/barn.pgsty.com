---
title: macOS 虚拟机
linkTitle: macOS 虚拟机
description: 用 barn mac 在 Apple 芯片 Mac 上运行 macOS 27 虚拟机：创建、连接、共享文件与剪贴板，以及清理。
weight: 38
icon: fa-brands fa-apple
---

> [!IMPORTANT]
> **Barn 0.9.0 发布候选，尚未发布。** 当前验证结果与发行前检查见
> [当前状态](../../about/status/#macos-guests)。请以实际运行的 `barn mac --help` 为准。

`barn mac` 在 Apple 芯片 Mac 上创建并运行 macOS 虚拟机。每台机器都是干净、可随时
丢弃的 macOS：带管理员账号、免密 sudo、固定的 SSH 密钥和固定地址，适合测试、构建与复现
macOS 特有的问题。它直接使用 Apple 的 Virtualization 框架，全程不需要管理员权限。

Mac 机器与 Linux 实验环境相互独立：不读取 `barn.yml`，不加入 Pigsty Inventory，
所有文件都在 `$BARN_HOME/mac`（默认 `~/.barn/mac`）下。Linux 的 `destroy` 与
`purge` 不会触碰它们。

## 前提条件

- 一台运行 **macOS 27 或更高版本**的 Apple 芯片 Mac，且已有用户登录桌面。客机同样运行 macOS 27。
- 第一台机器约需 **65 GiB** 可用空间：从 Apple 下载的约 25 GiB 恢复镜像（清理前一直保留）、
  安装后约 27 GiB 的基础镜像，以及启动所需的余量。此后每台机器按自身改动增长，
  上限是磁盘容量，默认 100 GiB。
- 在正式发布包含 Mac 组件之前，从源码构建需要 **Xcode 27**。
- 不需要 sudo：每台机器、它的网络和桌面都以当前用户身份运行。

Apple 规定一台 Mac 上**同时最多运行两台 macOS 虚拟机**，其他工具的虚拟机和 macOS
安装过程也计算在内。机器可以创建多台，任意两台可以同时运行。

## 构建 Mac 组件

在包含 `barn mac` 的 Barn 源码目录中执行：

```bash
make mac-build
export PATH="$PWD/bin/mac:$PATH"
barn mac doctor
```

`bin/mac` 中包含命令行、`Barn Mac.app`（运行机器及其桌面的原生组件）和使用说明，
请保持它们放在一起。本地构建使用 ad-hoc 签名。`doctor` 会检查 macOS 版本、组件与可用空间：

```text
CHECK           RESULT  DETAIL
component       ok      /path/to/barn/bin/mac/Barn Mac.app/Contents/MacOS/barn-mac-runner
virtualization  ok      macOS 27.0.0 on Apple Silicon; virtualization supported
disk            ok      549.8 GiB free
data            ok      no Mac machines yet; barn mac up creates the first
```

## 创建第一台机器

```bash
barn mac up
```

这台 Mac 上还没有准备好 macOS 时，`up` 会先列出需要做的事并请你确认：

```text
→ macOS 27.0 (26A428) is not prepared on this Mac yet.
download:  24.8 GiB from Apple (updates.cdn-apple.com)
then:      install macOS once into a reusable base (about 20 minutes)
free:      551.2 GiB
Download macOS from Apple now? [Y/n]
```

确认后，Barn 依次：

1. **只从 Apple 官方下载恢复镜像**，并用 Apple 公布的 SHA-256 校验；下载中断后从断点继续。
2. **一次性安装 macOS**，得到一个从未启动过的*基础镜像*。安装期间会占用两个 macOS
   虚拟机名额中的一个。
3. **创建 `mac1`**：以写时复制的方式克隆基础镜像，启动、创建你的账号，并等到 SSH 与
   sudo 可用。

```text
  ✓  mac1 created and ready · macOS 27.0 (26A428) · alice@10.10.20.10
shell:     barn mac ssh mac1
desktop:   barn mac open mac1
```

之后的每台机器都复用这个基础镜像，几十秒即可就绪；在验证主机上，从已准备好的基础镜像
创建一台机器用时 22 秒。

如果手上已有 Apple 的恢复镜像，可以直接使用，不必重新下载。它与数据在同一个 APFS
卷上时，Barn 以克隆方式引入，不占额外空间；否则校验后原地使用：

```bash
barn mac up --ipsw ~/Downloads/UniversalMac_27.0_26A428_Restore.ipsw
```

没有终端时（例如在脚本中），`up` 需要 `--yes` 才会下载，否则直接拒绝，绝不会悄悄下载
25 GiB。`barn mac setup` 可以提前准备基础镜像而不创建机器。

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

账号名与你的 macOS 用户名相同（创建时可用 `--user` 另选），并拥有免密 sudo。`ssh`
像普通 ssh 一样把命令行交给客机 shell；`exec` 保留参数边界。两者都返回客机命令的退出码，
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

桌面在一个与屏幕大小相称的原生窗口中打开。调整窗口大小时客机分辨率随之改变，
**View → Enter Full Screen** 照常可用。关闭窗口后机器继续运行；
再次执行 `open` 即可找回窗口，机器已停止时会先启动它。窗口获得焦点时，键盘快捷键都交给客机，
所以宿主侧的操作都放在菜单栏：

| 菜单 | 作用 |
|---|---|
| **Machine → Share Clipboard** | 在本次运行中开关剪贴板共享 |
| **Machine → Restart…** | 重启客机中的 macOS |
| **Machine → Shut Down…** | 正常关机，与 `barn mac stop` 相同 |
| **Window → Keep Running in Background** | 隐藏窗口，机器继续运行 |
| **Barn Mac → Quit Barn Mac…** | 选择让机器在后台继续运行，或关机 |

锁屏和桌面中的管理员授权需要登录密码。每台机器的密码随机生成，可以直接复制而不在终端显示：

```bash
barn mac password --copy
```

### 剪贴板

纯文本随焦点同步：在 Mac 上复制的内容，点进客机窗口后即可粘贴；在客机中复制的内容，
切换到其他应用时同步回 Mac。内容经由这台机器自己的 SSH 连接传输，客机中无需安装任何程序。
被密码管理器标记为敏感的内容不会离开 Mac；图片和文件不会同步。

执行 `barn mac configure mac1 --clipboard off` 可为某台机器关闭剪贴板共享，
从这台机器下次启动起生效。

### 共享目录

创建机器时共享 Mac 上的目录，客机把它们挂载在 `/Volumes/My Shared Files/<名称>`：

```bash
barn mac up dev --share ~/src --share docs=~/Documents:ro
barn mac exec dev -- ls "/Volumes/My Shared Files"
```

名称默认取目录路径的最后一段；`:ro` 表示只读。共享的必须是已存在的目录，不能是符号链接；
Barn 从不创建或删除共享目录。之后要调整共享，先停机再用 `configure`：

```bash
barn mac stop dev
barn mac configure dev --share data=/Volumes/Work/data --unshare docs
barn mac start dev
```

Mac 修改共享文件后，macOS 客机可能在短时间内仍看到旧内容。需要即时一致的结果时，
请通过 SSH 或 `exec` 操作。

### 在其他工具中使用 SSH

第一台机器就绪时，Barn 会在 `~/.ssh/config` 中加入一个带标记的 `Include`。之后
`ssh mac1`、`scp`、`rsync` 以及支持 Remote-SSH 的编辑器都能按名称访问每台机器，
并使用它自己的密钥和固定的主机密钥：

```bash
ssh mac1 'uptime'
rsync -a ./project/ mac1:project/
barn mac ssh-config              # 打印这些条目
barn mac ssh-config --remove     # 只移除 Barn 添加的内容
```

生命周期命令会保持这些条目为最新。若 `~/.ssh/config` 是由 dotfile 工具管理的链接，
Barn 不会修改它，而是打印需要你手动添加的 `Include` 行。

## 多台机器

为每台机器命名。创建参数只对新机器生效：

```bash
barn mac up dev --cpu 8 --memory 16G
barn mac ls
```

```text
NAME  STATE    ADDRESS      SSH    USER   OS          CPU  MEMORY  DISK                 SHARED
dev   running  10.10.21.10  ready  alice  macOS 27.0    8  16 GiB  504.0 MiB / 100 GiB
mac1  running  10.10.20.10  ready  alice  macOS 27.0    4   8 GiB  4.7 GiB / 100 GiB    src
limit:     2 of 2 macOS VMs are running; stop one before starting another
```

名称使用小写字母、数字和中间连字符，以字母开头。不带名称的命令作用于唯一的一台机器或
`mac1`；无法确定时会请你指定。`DISK` 显示机器当前占用的空间与容量。容量属于基础镜像：
`--disk` 与已准备的基础镜像不同时，会先安装另一个基础镜像，这需要再次使用恢复镜像。

每台机器有自己的私有网络：`mac1` 使用 `10.10.20.10`，之后的机器依次使用下一个空闲的
`/24`，并避开局域网、VPN 与 Linux 实验环境。机器可以访问互联网和 Mac，但彼此不通。
已有两台机器在运行时，第三台会在创建任何内容之前被拒绝，并指出可以停止哪一台：

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

`stop` 执行正常关机；两分钟后仍在运行的机器会被断电，结果中会明确说明。
`stop --force` 立即断电，相当于长按电源键，客机中未保存的内容会丢失。
`start --recovery` 启动到 macOS 恢复模式并显示桌面。

`up` 从不重新配置已有机器。传入与现有配置不同的参数时，它会拒绝执行并给出应使用的命令：

```text
error: dev already exists, so --cpu would not apply; its configuration and data were preserved
next: barn mac configure dev --cpu 4
```

`configure` 在机器停止时修改 CPU、内存、共享目录与网络，剪贴板共享可随时修改；
变更从下次启动起生效：

```bash
barn mac stop dev
barn mac configure dev --cpu 6 --memory 12G --subnet auto
barn mac start dev
```

`recreate` 用基础镜像中全新的 macOS 替换机器，保留名称、账号、资源、共享目录与地址；
`destroy` 删除机器。两者都会先说明将删除的内容，并要求输入命令名确认；
没有终端时用 `--force` 确认。

```bash
barn mac recreate dev
barn mac destroy dev build
```

| 操作 | 客机磁盘与应用 | 设置、地址与账号 |
|---|---|---|
| `stop`/`start`、`restart`、重复 `up` | 保留 | 保留 |
| `configure` | 保留 | 按要求修改 |
| `recreate` | 换成全新的 macOS | 保留；密码与 SSH 密钥重新生成 |
| `destroy` | 删除 | 删除 |

以上操作都不会修改共享的基础镜像；删除机器时基础镜像也会保留。

## macOS 版本与磁盘空间

```bash
barn mac image ls
```

```text
KIND  OS          BUILD   STATE  ON DISK   CAPACITY  USED BY
base  macOS 27.0  26A428  ready  26.7 GiB  100 GiB   mac1,default
```

升级总是显式进行。`barn mac image update` 向 Apple 查询最新的 macOS 27，确认后下载，
并将其设为新机器的基础镜像。已有机器保持原来的 macOS，直到执行
`barn mac recreate NAME --update`。`up` 与 `start` 从不改变机器的 macOS 版本。

`image prune` 列出没有机器使用、且不是默认的基础镜像，加 `--yes` 才会删除；
`--installers` 会一并处理已下载的恢复镜像。APFS 克隆共享数据块，因此 `ON DISK`
与各机器的磁盘数字都不是独占空间，不要相加。

```bash
barn mac image prune --installers         # 先查看
barn mac image prune --installers --yes   # 再删除
```

## 故障排查

先执行 `barn mac doctor`：它检查宿主、组件、基础镜像与每台机器，并为每个失败项给出
`next:` 命令。`barn mac logs [名称]` 显示机器的运行日志：启动、网络、关机以及 Apple
Virtualization 的错误。

| 现象 | 处理方法 |
|---|---|
| 启动时报 `network … overlaps route …` | VPN 或其他工具占用了该网段。执行 `barn mac configure NAME --subnet auto`。 |
| `macOS allows 2 macOS virtual machines at a time` | 停止提示中的某台机器，或退出其他工具的 macOS 虚拟机。 |
| 第三方 SSH 客户端执行 `ssh mac1` 报 "No route to host" | macOS 的“本地网络”隐私控制阻止了该应用访问私有网络。在**系统设置 → 隐私与安全性 → 本地网络**中允许它，或改用 `/usr/bin/ssh`。`barn mac ssh` 与 `exec` 始终使用 Apple 自带工具，不受影响。 |
| `the Barn Mac component is not installed` 或 `speaks protocol …` | 同一次构建的 `barn` 与 `Barn Mac.app` 需放在一起；用 `make mac-build` 重新构建。 |
| 通过 SSH 登录 Mac 后启动失败 | 请在 Mac 桌面会话的终端中运行 `barn mac`：机器需要已登录用户的会话和已解锁的登录钥匙串。 |

在虚拟机中登录 Apple 账户并不可靠；不支持 USB 设备、快照和挂起机器。

## 清理

```bash
barn mac destroy --force mac1 dev           # 删除机器
barn mac image prune --installers --yes     # 删除不再使用的镜像
```

删除最后一台机器时，`~/.ssh/config` 中的相应条目也会一并移除。默认基础镜像会保留，
供之后创建机器使用；如需删除包括它在内的所有 Mac 文件，先删除全部机器，再删除
`$BARN_HOME/mac`（默认 `~/.barn/mac`）。除该目录外，Barn 只会写入
`~/.ssh/config` 中的条目、保存在 `~/Library/Preferences/io.pgsty.barn.mac-runner.plist`
中的桌面窗口位置，以及 `/tmp` 下的一个短路径运行目录。整个过程都不需要 sudo。
