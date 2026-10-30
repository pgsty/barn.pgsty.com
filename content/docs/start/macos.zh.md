---
title: macOS 虚拟机
linkTitle: macOS 虚拟机
description: 用 barn mac 在 Apple 芯片 Mac 上运行 macOS 27 虚拟机：创建、连接、共享文件与剪贴板，以及清理。
weight: 20
icon: fa-brands fa-apple
---

> [!NOTE]
> **Unreleased**：下文关于共享名称与数量放宽、共享源符号链接及状态路径支持的变更需要包含源码提交 `27f17bb` 的构建，Barn 0.9.2 尚未包含这些行为。详见[未发布变更](/zh/docs/about/unreleased/)。

`barn mac` 用于在 Apple Silicon Mac 上创建和管理可随时重建的 macOS 虚拟机，适合编译构建、自动化测试以及复现 macOS 专属问题。每台虚拟机自带管理员账号、免密 `sudo`、固定绑定的 SSH 密钥与独立私网地址，基于 Apple Virtualization 框架直接以当前用户身份运行，全程无需 `sudo`。

Mac 虚拟机与 Linux 实验环境完全独立：它不读取 `barn.yml`，所有数据保存在 `$BARN_HOME/mac`（默认 `~/.barn/mac`）下，执行 Linux 的 `barn destroy` 或 `barn purge` 不会影响任何 Mac 虚拟机。

## 前提条件

- 一台运行 **macOS 27 或更高版本**的 Apple Silicon Mac，且当前用户已登录图形桌面会话（客机同样运行 macOS 27）。
- 首次创建约需 **65 GiB** 可用磁盘空间，用于存放从 Apple 下载的恢复镜像（`.ipsw`，约 25 GiB）、安装后的基础镜像（约 27 GiB）以及启动写入空间。后续每台虚拟机通过 APFS 写时复制克隆基础镜像，按实际改动增长（默认容量上限为 100 GiB）。
- 与 `0.9.2` CLI 配套的原生应用包 **`Barn.app`**，Apple Silicon 发行包与 Homebrew 安装均已包含。
- 无需 `sudo` 权限。

受 Apple Virtualization 框架限制，单台 Mac **最多同时运行两台 macOS 虚拟机**（其他虚拟化工具启动的实例及正在执行的 macOS 基础镜像安装均计入配额）。你可以创建更多已停止的虚拟机并按需启动其中任意两台（须遵守适用的 Apple 软件许可协议）。

## 安装 {#install}

通过 Homebrew 安装预编译发行版：

```bash
brew install pgsty/infra/barn
barn version
barn mac doctor
```

Homebrew 会一并安装经过签名、公证的 `Barn.app` 及配套 CLI/helper，无需安装 Go 或 Xcode。Apple Silicon 的[安装脚本与手动归档](../installation/)同样包含原生 App。升级或替换 App 前请先停止运行中的 Mac 虚拟机。

如需开发 Barn 本身，请参阅[构建 Mac 原生组件](../source-build/#mac-component)。

## 创建第一台机器

```bash
barn mac up
```

如果本机尚未准备 macOS 基础镜像，`barn mac up` 会先列出下载体积与磁盘空间并请求确认：

```text
→ macOS 27.0 (26A428) is not prepared on this Mac yet.
download:  24.8 GiB from Apple (updates.cdn-apple.com)
then:      install macOS once into a reusable base (about 20 minutes)
free:      551.2 GiB
Download macOS from Apple now? [Y/n]
```

确认后，Barn 会依次完成以下三步：

1. **从 Apple 官方（`updates.cdn-apple.com`）下载恢复镜像**，支持断点续传并自动核对 Apple 公布的 SHA-256 校验值。
2. **一次性安装 macOS 基础镜像**，生成一份未启动过的干净母盘（安装期间会临时占用两个运行配额之一）。
3. **通过 APFS 写时复制克隆出 `mac1`**，启动客机并自动配置同名管理员账号，等待 SSH 与免密 `sudo` 就绪。
{.steps}

```text
  ✓  mac1 created and ready · macOS 27.0 (26A428) · alice@10.10.20.10
shell:     barn mac ssh mac1
desktop:   barn mac open mac1
```

后续新建虚拟机都会直接克隆这份基础镜像，几秒内即可完成创建，无需重复执行漫长的系统恢复安装。Barn `0.9.2` 首次下载默认固定为 **macOS 27.0 (26A428)**；如需跟进更新的 macOS 27 版本，可显式运行 `barn mac image update`。

如果本机已下载好 Apple 恢复镜像，可通过 `--ipsw` 直接传入（位于同一 APFS 卷时将直接克隆数据块而无需复制）：

```bash
barn mac up --ipsw ~/Downloads/UniversalMac_27.0_26A428_Restore.ipsw
```

在无终端脚本中，需传入 `--yes` 才会自动下载 25 GiB 镜像；也可使用 `barn mac setup` 提前准备基础镜像而不创建虚拟机。如果创建新虚拟机时传入了 `--no-wait`（虚拟机进程启动即返回），在使用 `ssh` 或 `exec` 前请再执行一次不带 `--no-wait` 的 `barn mac up NAME` 以完成密钥与 `sudo` 初始化。

## 使用机器

### 终端与命令

```bash
barn mac ssh                                  # 进入交互式终端
barn mac exec -- sw_vers                      # 直接执行单个程序
barn mac ssh -- 'id; sudo -n true && echo sudo works'
```

```text
ProductName:		macOS
ProductVersion:		27.0
BuildVersion:		26A428
```

客机管理员账号默认与宿主 macOS 用户名一致（创建时可通过 `--user` 自定义），并具备免密 `sudo`。请在远端命令前加上 `--`：`ssh` 会将命令行交给客机 Shell 执行，`exec` 则直接按参数列表调用目标程序（需要管道或重定向时请显式调用 `sh -c`，详见 [SSH/exec 契约](../../reference/mac/#ssh-与-exec)）。两者都会透传客机命令的退出码，配合 `--json` 可结构化捕获 `stdout`、`stderr` 与 `exit_code`：

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

完整 JSON 字段说明见 [Mac 命令参考](../../reference/mac/#json-output)。

### 桌面

```bash
barn mac open
```

`barn mac open` 会在原生窗口中打开客机桌面，缩放窗口即可动态调整客机分辨率（可通过 **View → Enter Full Screen** 切换全屏）。直接关闭窗口不会停止虚拟机；再次运行 `barn mac open` 可重新唤出窗口，若虚拟机已停止则会先启动它。

当客机窗口处于焦点状态时，键盘快捷键会直接发送给客机，宿主侧操作请通过顶部菜单栏执行：

| 菜单项 | 作用 |
|---|---|
| **Machine → Share Clipboard** | 在当前会话中开关纯文本剪贴板共享 |
| **Machine → Restart…** | 重启客机内的 macOS 系统 |
| **Machine → Shut Down…** | 正常关闭客机（等同于 `barn mac stop`） |
| **Window → Keep Running in Background** | 隐藏桌面窗口，让虚拟机继续在后台运行 |
| **Barn → Quit Barn…** | 选择让虚拟机在后台保持运行，或直接关机 |

宿主注销或关机时，Barn 会先请求客机正常关机，若超时仍未停止则强制断电。

每台虚拟机还会随机生成一组用于锁屏解锁和桌面管理员弹窗的登录密码。如需复制到剪贴板而不在终端明文回显，可执行：

```bash
barn mac password --copy
```

### 剪贴板

剪贴板共享会在窗口焦点切换时通过虚拟机自身的 SSH 通道自动同步纯文本，无需在客机内安装额外代理：点击进入客机窗口时可使用在宿主 Mac 上复制的文本，切回宿主应用时则会同步客机内复制的文本。密码管理器标记为敏感的条目、图片和文件不会跨机同步。

如需为某台虚拟机长期关闭剪贴板同步，可执行 `barn mac configure mac1 --clipboard off`（下次启动时生效）。

### 共享目录 {#共享目录}

创建虚拟机时可通过 `--share` 将宿主目录共享给客机，客机会将其自动挂载到 `/Volumes/My Shared Files/<名称>`：

```bash
barn mac up dev --cpu 8 --memory 16G --share ~/src --share docs=~/Documents:ro
barn mac exec dev -- ls "/Volumes/My Shared Files"
```

共享名称默认取目录路径的最后一段，末尾追加 `:ro` 表示只读挂载。共享路径须解析为已存在的目录（支持符号链接），且 Barn 绝不会自动创建或删除宿主共享目录。若需修改已有虚拟机的共享目录，请先停机再运行 `barn mac configure`：

```bash
barn mac stop dev
barn mac configure dev --share data=/Volumes/Work/data --unshare docs
barn mac start dev
```

由于 macOS 客机的 VirtioFS 在宿主修改文件后可能短暂缓存旧内容，若构建任务需要立即读取最新字节，建议使用 `scp` 或 `rsync` 将文件同步到客机本地磁盘。

### 在其他工具中使用 SSH

当第一台 Mac 虚拟机就绪时，Barn 会在 `~/.ssh/config` 中添加一行带标记的 `Include`，使 `ssh mac1`、`scp`、`rsync` 以及支持 Remote-SSH 的编辑器能够直接按名称连接每台虚拟机，并自动使用该虚拟机的专属密钥与固定主机密钥：

```bash
ssh mac1 'uptime'
rsync -a ./project/ mac1:project/
barn mac ssh-config              # 查看生成的 SSH 配置条目
barn mac ssh-config --remove     # 移除 Barn 添加的 Include 并关闭自动写入
```

如果 `~/.ssh/config` 是由 dotfile 工具管理的符号链接，Barn 不会直接修改它，而是打印出需要手动添加的 `Include` 行。执行 `--remove` 后如需恢复自动集成，可运行 `barn mac ssh-config --install`。若你的个人 SSH 配置已占用某个虚拟机同名别名，Barn 会保留你的原有别名，仅按 IP 地址发布该虚拟机的配置。

## 多台机器

每台虚拟机使用以字母开头的小写字母、数字或内部连字符命名。创建参数（`--cpu`、`--memory`、`--disk`、`--user`、`--share`）仅在首次创建该虚拟机时生效：

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

省略机器名称时，命令默认作用于当前唯一存在的虚拟机或 `mac1`（存在多台机器且目标不唯一时会提示显式指定名称）。如果 `--disk` 指定的容量与现有基础镜像不同，Barn 会先用恢复镜像安装一份对应容量的基础镜像。

每台虚拟机拥有独立的 `/24` 私有子网（默认从 `10.10.20.0/24` 起分配，客机地址为 `.10`），并自动避开局域网、VPN、Linux 实验环境及其他 Mac 虚拟机占用的网段。当同一数据目录下已有两台 Mac 虚拟机在运行时，启动第三台会立即报错并提示可停止的机器：

```bash
barn mac up build --user ci
```

```text
error: dev and mac1 are running; macOS allows 2 macOS virtual machines at a time
next: barn mac stop mac1
```

## 日常管理 {#日常管理}

```bash
barn mac stop dev               # 请求客机正常关机（超时 2 分钟后断电）
barn mac start dev              # 启动并等待 SSH 就绪
barn mac restart dev            # 重启以应用待生效的 configure 变更
barn mac stop --all             # 停止所有运行中的 Mac 虚拟机
```

传入 `barn mac stop --force` 可立即断电，传入 `barn mac start --recovery` 则会启动至 macOS 恢复模式并打开桌面窗口。

`barn mac up` 不会修改已有虚拟机的硬件配置；若对已存在的虚拟机传入不同的创建参数，命令会拒绝执行并提示改用 `barn mac configure`：

```text
error: dev already exists, so --cpu would not apply; its configuration and data were preserved
next: barn mac configure dev --cpu 4
```

修改 CPU、内存、共享目录或网段前请先停止虚拟机（剪贴板开关可随时修改），变更将在下次启动时生效：

```bash
barn mac stop dev
barn mac configure dev --cpu 6 --memory 12G --subnet auto
barn mac start dev
```

`barn mac recreate` 会基于基础镜像用全新 macOS 替换虚拟机磁盘，同时保留机器名称、账号、资源规格、共享目录与 IP 地址；`barn mac destroy` 则会彻底删除虚拟机（非交互脚本请传入 `--force`）：

```bash
barn mac recreate dev
barn mac destroy dev
```

| 操作 | 客机磁盘与已安装应用 | 规格设置、IP 地址与账号 |
|---|---|---|
| `stop` / `start`、`restart`、重复 `up` | 保留 | 保留 |
| `configure` | 保留 | 按指定参数更新 |
| `recreate` | 替换为全新的 macOS 克隆盘 | 保留（重新生成登录密码与 SSH 密钥） |
| `destroy` | 删除 | 删除（共享基础镜像仍会保留） |

## macOS 版本与磁盘空间

```bash
barn mac image ls
```

```text
KIND  OS          BUILD   STATE  ON DISK   CAPACITY  USED BY
base  macOS 27.0  26A428  ready  26.7 GiB  100 GiB   mac1,default
```

运行 `barn mac image update` 可向 Apple 查询最新的受支持 macOS 27 版本，确认后下载恢复镜像并为后续新建虚拟机准备新的默认基础镜像。已有虚拟机会保持原有系统版本，直到你显式执行 `barn mac recreate NAME --update`（若该虚拟机使用了如 `200G` 的自定义磁盘容量，请先按提示执行 `barn mac setup --disk 200G` 准备同容量的新基础镜像）。

使用 `barn mac image prune` 可查看未被任何虚拟机引用的非默认基础镜像，加上 `--installers` 会一并纳入已下载的 `.ipsw` 恢复镜像与未完成下载，加上 `--yes` 执行删除：

```bash
barn mac image prune --installers         # 预览可清理的镜像文件
barn mac image prune --installers --yes   # 确认删除
```

由于 APFS 克隆与基础镜像共享底层物理数据块，`ON DISK` 与各虚拟机的磁盘占用统计存在重叠，请勿直接相加计算总占用。

## 故障排查 {#故障排查}

遇到问题时先运行 `barn mac doctor`，它会依次检查宿主环境、`Barn.app` 原生组件、基础镜像和每台虚拟机的状态并给出修复命令；`barn mac logs [名称]` 则用于查看启动、网络、关机及 Apple Virtualization 运行时日志。

| 常见现象 | 处理方法 |
|---|---|
| 启动时报 `network … overlaps route …` | VPN 或新路由占用了当前网段，执行 `barn mac configure NAME --subnet auto` 重新分配子网。 |
| `macOS allows 2 macOS virtual machines at a time` | 停止提示中的某台虚拟机（`barn mac stop NAME`），或退出其他工具运行的 macOS 虚拟机。 |
| 第三方客户端执行 `ssh mac1` 报 `No route to host` | 在 **系统设置 → 隐私与安全性 → 本地网络** 中为该终端或 IDE 开启本地网络权限，或改用系统自带的 `/usr/bin/ssh`（`barn mac ssh` 与 `exec` 默认调用系统自带客户端）。 |
| `mac_runner_missing` 或 `mac_runner_protocol` | 确保 `barn`、`barn-hosts-helper`、`barn-mac-runner` 与 `Barn.app` 来自同一次 `make mac-build` 输出目录且保持相对路径不变。 |
| 通过远端 SSH 登录宿主 Mac 后启动失败 | 请在 Mac 本机已登录图形桌面会话的终端中运行 `barn mac`，并确保登录钥匙串处于解锁状态。 |

Apple Virtualization 框架尚不支持在虚拟机中稳定登录 Apple 账户，也不支持 USB 设备直通、快照与挂起恢复。

## 清理

```bash
barn mac ls                                 # 查看现有 Mac 虚拟机名称
barn mac destroy mac1 dev                   # 确认删除指定虚拟机
barn mac image prune --installers --yes     # 删除已缓存的恢复镜像与闲置基础镜像
```

销毁最后一台 Mac 虚拟机时，Barn 会自动清理 `~/.ssh/config` 中的对应条目，并保留默认基础镜像供日后复用。如需彻底移除所有 Mac 虚拟机文件：

1. 销毁所有 Mac 虚拟机（`barn mac destroy ...`），并执行 `barn mac ssh-config --remove`。
2. 删除 `$BARN_HOME/mac`（默认 `~/.barn/mac`）。
3. 按需删除保存桌面窗口位置的 `~/Library/Preferences/com.pgsty.barn.plist`（`0.9.0` 版本为 `io.pgsty.barn.mac-runner.plist`）。
{.steps}
