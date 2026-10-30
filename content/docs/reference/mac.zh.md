---
title: Mac 命令
description: barn mac 的命令与参数、机器规则、JSON 结果、失败原因、网络与文件。
weight: 25
icon: fa-brands fa-apple
---

> [!NOTE]
> **Unreleased**：下文关于共享名称与数量、源目录符号链接、runner 路径及日志行数限制的变更需要包含源码提交 `27f17bb` 的构建，Barn 0.9.2 尚未包含这些行为。详见[未发布变更](/zh/docs/about/unreleased/)。

```text
barn [--json|--yaml] [-v|--verbose] mac <command> [flags] [name...]
```

运行 macOS 客机需要搭载 Apple 芯片且运行 macOS 27 或更高版本的 Mac，并由当前登录桌面用户直接调用。需要调用原生 runner 的命令会以 `mac_root` 拒绝 `root` 身份，并以 `mac_host_unsupported` 拒绝不满足要求的宿主。在 Linux 与 Intel Mac 上，顶层 `--help` 默认隐藏 `mac` 命令；而 `barn mac image ls` 等只读取本地记录的子命令则无需启动原生 runner。不带子命令直接运行 `barn mac` 等同于 `barn mac ls`。

本参考说明 **Barn 0.9.2** 命令接口与 `Barn.app`（runner 协议版本 `2`），以及上方标注的源码变更。Apple Silicon 发行包与 Homebrew 安装已包含 App，安装步骤见 [macOS 客机指南](../../start/macos/#install)。

## 命令

| 命令 | 用途 |
|---|---|
| `ls` | 列出所有虚拟机的状态、IP、SSH 就绪情况、macOS 版本、资源与共享目录（别名：`list`、`status`、`st`） |
| `up [name]` | 按需创建并启动虚拟机，等待 SSH 与免密 sudo 就绪 |
| `start [name...]` | 启动已存在的虚拟机 |
| `stop [name...]` | 请求客机正常关机；超过两分钟仍未停止则强制断电 |
| `restart [name]` | 先停后启，使挂起的硬件、共享或网段变更生效 |
| `open [name]` | 打开桌面窗口；若虚拟机已停止则先启动 |
| `ssh [name] [-- command...]` | 打开交互式终端，或将 `--` 后的命令行交给客机 shell 执行 |
| `exec [name] -- command...` | 在客机中执行程序并保留参数边界 |
| `configure name` | 修改已停止虚拟机的 CPU、内存、共享目录、网段或剪贴板设置 |
| `recreate name` | 用全新的 macOS 克隆替换虚拟机，保留原有硬件与网络设置 |
| `destroy name...` | 删除一台或多台虚拟机 |
| `password [name]` | 显示或复制客机登录密码 |
| `ssh-config` | 打印、安装或移除 `~/.ssh/barn-mac_config` 条目 |
| `logs [name]` | 查看虚拟机最近的 `runner.log` 运行日志 |
| `setup` | 下载并准备默认 macOS 基础镜像，不创建虚拟机 |
| `image ls` | 列出已缓存的 `.ipsw` 恢复镜像、已准备好的基础镜像及使用它们的虚拟机（别名：`list`） |
| `image update` | 下载 Apple 最新的 macOS 27 构建并准备为默认基础镜像 |
| `image prune` | 列出未使用的镜像；传入 `--yes` 时执行删除 |
| `doctor` | 检查宿主环境、`Barn.app` 组件、基础镜像与每台虚拟机槽位 |
{.wide}

<span id="ssh-and-exec"></span>

### SSH 与 exec {#ssh-与-exec}

> [!TIP]
> 从 **0.9.2** 开始，远端命令前必须使用 `--`，例如 `barn mac exec dev -- sw_vers`。交互式登录 `barn mac ssh dev` 无需分隔符。

`--` 之前除 Barn 参数外，最多接受一个已存在的虚拟机名（省略名称时自动选择唯一虚拟机或 `mac1`）。`ssh` 不带命令时打开交互式终端；`exec` 必须在 `--` 后提供非空命令。未知的机器名或语法错误会在发起连接前直接返回退出码 `2`（`usage`），并提示运行 `barn mac ls` 查看现有机器。

`ssh` 会将 `--` 后的参数用空格拼接成命令行交给客机 shell；`exec` 则将程序名和各个参数分别传入，完整保留空格、引号及后续空字符串参数。需要管道、重定向、变量展开或串行执行多条命令时，请显式使用 `sh -c '...'`。`--json`、`-v`、`--help` 等 Barn 参数必须放在 `--` 前，其后的所有参数（包括第二个 `--`）都归属客机命令。

```bash
barn mac ssh dev
barn mac ssh dev -- 'sw_vers; id'
barn mac exec dev -- sw_vers
barn mac exec dev -- printf '<%s>\n' 'a b' ''
barn mac exec dev -- sh -c 'sw_vers; id'
barn --json mac exec dev -- sh -c 'echo out; exit 3'
```

### 各命令的参数

| 命令 | 参数 |
|---|---|
| `up` | `--cpu`、`--memory`、`--disk`、`--user`、`--share`、`--clipboard`、`--subnet`、`--ipsw`、`-y`/`--yes`、`-n`/`--no-wait`、`--open` |
| `start` | `--all`、`-n`/`--no-wait`、`--open`、`--recovery` |
| `stop` | `--all`、`--force` |
| `restart` | `-n`/`--no-wait`、`--open` |
| `configure` | `--cpu`、`--memory`、`--share`、`--unshare`、`--clipboard`、`--subnet` |
| `recreate` | `--update`、`--force`、`-n`/`--no-wait` |
| `destroy` | `--force` |
| `password` | `-c`/`--copy` |
| `ssh-config` | `-i`/`--install`、`--remove` |
| `logs` | `-n`/`--lines` 正整数（默认 `100`），按请求行数读取，不再按 1 MiB 静默截断 |
| `setup` | `--ipsw`、`--disk`、`-y`/`--yes` |
| `image update` | `--ipsw`、`-y`/`--yes` |
| `image prune` | `--installers`、`-y`/`--yes` |
{.wide}

对于名称可省略的命令，不传名称时会选中唯一的虚拟机或 `mac1`；若存在多台虚拟机且没有 `mac1`，命令会提示你显式指定名称。`start` 与 `stop` 支持传入多个名称或 `--all`。`destroy` 与 `recreate` 会先列出即将删除的内容，并在终端上要求输入命令名称确认（无终端脚本中请传 `--force`）。

`--no-wait` 会在虚拟机进程启动后立即返回；对于新建虚拟机，后续仍需运行一次不带 `--no-wait` 的 `barn mac up NAME` 以完成 SSH 密钥写入与 sudo 配置。普通 `start` 要求虚拟机已完成首次启动——若未完成首次启动的虚拟机已在运行，可执行 `barn mac open NAME` 查看首次启动画面；若已停止，则执行 `barn mac up NAME --open`。传入 `--recovery` 会跳过常规就绪等待，直接启动进入 macOS 恢复模式桌面。

### 参数取值

| 参数 | 取值 |
|---|---|
| `--cpu` | 虚拟 CPU 核数，最少 `2` 核，最多不超过宿主 Mac 的逻辑 CPU 数（默认 `4`） |
| `--memory` | 二进制单位容量（`16G`、`16GiB`、`16GB`）或字节数；须为整 MiB，介于 `4 GiB` 与宿主物理内存之间（默认 `8 GiB`） |
| `--disk` | 基础镜像磁盘容量，至少 `32 GiB`（默认沿用已准备基础镜像的容量，首个基础镜像为 `100 GiB`；指定其他容量时若尚无匹配基础镜像会自动安装一份） |
| `--user` | 客机管理员用户名（默认取宿主 macOS 用户名；若宿主名称不符合账号规范则回退为 `barn`） |
| `--share` | `[name=]path[:ro\|:rw]`，可重复指定，不再另设 8 个共享的上限；`name` 默认取路径最后一段，`~/` 会展开为用户主目录 |
| `--clipboard` | `on` 或 `off`（也接受 `true`/`false`、`yes`/`no`；默认 `on`） |
| `--subnet` | 规范的私有 `/24` 网段（如 `10.10.30.0/24`），或用 `auto` 自动选择第一个空闲网段 |
{.wide}

对已存在的虚拟机运行 `up` 时，若传入的创建参数与现有设置不一致，`up` 会以 `mac_configuration_conflict` 拒绝执行，并在 `next:` 行给出对应的 `configure` 或 `recreate` 命令：

- 在虚拟机停止状态下使用 `barn mac configure` 修改 `--cpu`、`--memory`、`--share`/`--unshare`、`--subnet` 或 `--clipboard`（剪贴板配置也可在运行时修改并保存到下次启动生效；当前会话可通过菜单栏图标即时开关剪贴板同步）。**Unreleased**：共享名称支持空格与中文，须为 1–255 字节的有效 UTF-8，不能是 `.`、`..`，也不能包含 `/` 或 ASCII 控制字符；`configure --share` 复用已有名称时会更新其路径与读写属性，`--unshare` 则按名称移除对应共享。
- 管理员账号（`--user`）与磁盘容量（`--disk`）在虚拟机整个生命周期内固定不变，`recreate` 也会保留它们；如需更改账号或磁盘大小，请创建一台新虚拟机。
- 升级虚拟机的 macOS 版本时，先运行 `barn mac image update`，再执行 `barn mac recreate NAME --update`。由于 `recreate --update` 会保留原虚拟机的磁盘容量，若新 macOS 版本下还没有对应自定义容量（如 `200G`）的基础镜像，请先执行 `barn mac setup --disk 200G` 准备好该容量的基础镜像。

## 机器规则

- **名称**：1–32 个字符，以小写字母开头，仅含小写字母、数字与中间连字符（例如 `mac1`、`dev`、`build-2`）。
- **单机两台并发上限**：受 Apple Virtualization 框架限制，每台 Mac 最多同时运行两台 macOS 虚拟机（跨所有虚拟化应用以及正在执行的 `.ipsw` 基础镜像安装任务统一计数）。Barn 绝不会为了腾出名额而停止已有虚拟机。`ls.running` 统计当前 `BARN_HOME` 内的活跃虚拟机数，宿主全局上限则由 Apple 运行时强制执行。
- **管理员账号**：默认配置免密 sudo、Ed25519 SSH 密钥登录、桌面自动登录与“远程登录”（SSH 服务），并关闭 SSH 密码认证；随机生成的本地登录密码保存在虚拟机槽位目录的 `password` 文件中（权限 `0600`）。
- **主机名**：客机电脑名称（ComputerName）与虚拟机名 `<name>` 一致，本地主机名（LocalHostName）设为 `barn-<name>`（可通过 `barn-<name>.local` 访问）。
- **目录共享**：客机内通过单个 VirtioFS 设备挂载到 `/Volumes/My Shared Files/<name>`。宿主源须解析为已存在的目录，支持符号链接；名称支持空格与中文。
- **剪贴板同步**：每当虚拟机桌面窗口获得或失去焦点时，Barn 通过该虚拟机的 SSH 连接双向同步不超过 1 MiB 的纯文本，并自动跳过标记为敏感（concealed）的剪贴板条目。
- **关机行为**：`barn mac stop` 会向客机发送正常关机请求，等待满两分钟仍未退出则强制断电（返回 `"forced": true`）；传入 `--force` 则立即断电。

## 网络

每台虚拟机的 runner 进程在启动时通过 Apple 的[共享模式 `vmnet` API](https://developer.apple.com/documentation/vmnet/vmnet_network_configuration_create(_:_:)) 创建独立的用户态网络，并在退出时自动销毁，全程无需守护进程或 root 权限：

| 项目 | 取值 |
|---|---|
| 网段 | 在 `10.10.20.0/24` 至 `10.10.59.0/24` 之间自动选择第一个避开宿主路由与其他虚拟机的空闲 `/24`（也可通过 `--subnet` 显式指定） |
| 网关 | `.1`（宿主 Mac） |
| 客机地址 | `.10`（按虚拟机 MAC 地址通过 `vmnet` DHCP 保留固定分配） |
| 连通范围 | 支持宿主与客机互访及通过 NAT 访问外网；各虚拟机使用独立子网，不桥接物理局域网，也不做入站端口转发 |
{.wide}

如果宿主新增的路由（如 VPN 路由）占用了虚拟机已保存的网段，`start` 会以 `mac_subnet_in_use` 拒绝启动；此时执行 `barn mac configure NAME --subnet auto` 即可改换到空闲网段。由于 SSH 主机密钥绑定在虚拟机实例标识 `barn-mac-<instance_id>` 而非 IP 地址上，更换网段不会破坏 SSH 信任链。

macOS 的“本地网络”隐私权限有时会拦截第三方终端或 IDE 访问 `vmnet` 子网（通常表现为 `No route to host`），请在 **系统设置 → 隐私与安全性 → 本地网络** 中为对应应用开启权限。Barn 自身的 Go SSH 连接通过系统内置的 `/usr/bin/nc` 转发，交互命令则直接调用 `/usr/bin/ssh`，从而避开第三方二进制直连本地子网时的权限限制。

## JSON 输出 {#json-output}

除交互式 `ssh` 外，所有 `barn mac` 命令均支持通过 `--json` 与 `--yaml` 在 stdout 输出结构化结果，同时将进度信息写往 stderr。

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
| `state` | `prepared`（已创建但未完成首次启动）、`starting`、`running`、`stopping`、`stopped`、`unknown` |
| `ready` | 本次检查通过 SSH 连通客机并验证免密 sudo 成功时为 `true` |
| `ssh` | `ready`、`pending`（首次启动进行中）、`unavailable`、`offline`、`unchecked` |
| `observed` | 运行中客机报告的 macOS 版本与基础镜像不一致时出现 |
| `window_visible` | 桌面窗口处于打开状态时出现 |
| `error`、`warnings` | 最近一次记录的槽位错误，以及本次检查发现的 SSH 告警 |
{.wide}

### 生命周期结果

单机操作（`up`、`restart`、`open`、`recreate`、`configure`）返回单个结果对象；批量操作（`start`、`stop`、`destroy`）即使只指定一台虚拟机也始终返回 `{"machines": [...]}`。多台虚拟机操作部分成功时，结果中会同时保留成功项与失败详情，并以退出码 `5` 返回。

```json
{"name": "mac1", "action": "created", "state": "running", "ready": true,
 "address": "10.10.20.10", "user": "alice", "version": "27.0", "build": "26A428"}
```

| 字段 | 取值 |
|---|---|
| `action` | `created`、`started`、`running`（已在运行）、`restarted`、`recreated`、`opened`、`configured`、`stopped`、`powered_off`、`already_stopped`、`destroyed`、`absent` |
| `forced` | 正常关机超时、转为强制断电时为 `true` |
| `window` | 本次操作打开了桌面窗口时为 `true` |
| `warnings` | 非致命提示（例如剪贴板变更将在下次启动时生效） |
{.wide}

其他命令的 JSON 输出：

- **`exec --json`**：返回与 Linux `barn exec --json` 相同的结构（`node`、`exit_code`、`stdout`、`stderr`）。
- **`password --json`**：返回明文密码；配合 `--copy` 时返回 `{"name": "mac1", "copied": true}`。
- **`ssh-config --json`**：默认返回 `fragment` 字符串；配合 `--install` 或 `--remove` 时返回安装状态。
- **`logs --json`**：返回 `name` 与 `logs`。
- **`doctor --json`**：返回 `ok` 与 `checks[]`（每项含 `name`、`ok`、`detail` 及可选的 `next`），任一检查未通过时退出码为 `3`。

## 失败原因

退出码遵循 [Barn 命令行退出码表](../cli/#退出码)，`ssh` 与 `exec` 原样透传远端命令退出码。结构化错误对象包含稳定的 `reason` 标识与 `next` 修复建议：

| 原因标识 | 退出码 | 含义与下一步 |
|---|---:|---|
| `mac_host_unsupported` | `3` | 宿主不是 Apple 芯片，或 macOS 版本低于 27 |
| `mac_runner_missing` | `3` | `barn` 可执行文件旁未安装 `Barn.app` 原生组件 |
| `mac_runner_protocol` | `3` | 已安装的组件使用不兼容的 runner 协议版本；请重新安装匹配的 CLI 与 App |
| `mac_root` | `2` | 使用了 `root` 身份调用；请切换回普通登录用户，不要加 `sudo` |
| `mac_download_consent` | `2` | 非交互环境下下载 macOS 镜像需要传入 `--yes`，或改用 `--ipsw` 指定本地文件 |
| `mac_machine_absent` | `4` | 指定名称的虚拟机不存在；请运行 `barn mac up NAME` 创建 |
| `mac_not_initialized` | `4` | 虚拟机尚未完成首次启动初始化；请运行 `barn mac up NAME` |
| `mac_not_running` | `4` | 对已停止的虚拟机调用了 `ssh`/`exec`；请先执行 `barn mac start NAME` |
| `mac_running` | `4` | 请求的配置变更需要先停机；请先执行 `barn mac stop NAME` |
| `mac_configuration_conflict` | `4` | `up` 参数与已有虚拟机配置不一致；请按提示运行 `configure` 或 `recreate` |
| `ssh_config_linked` | `4` | `~/.ssh/config` 是符号链接或硬链接；请手动将打印出的 `Include` 行加入配置文件 |
| `mac_vm_limit` | `6` | 当前 Mac 上已有两台 macOS 虚拟机在运行；请先停止提示中指明的那台 |
| `mac_subnet_in_use` | `6` | 宿主路由与虚拟机网段重叠；请执行 `barn mac configure NAME --subnet auto` |
| `disk_full` | `6` | 磁盘剩余空间不足以下载或安装 macOS 基础镜像 |
| `mac_machine_damaged` | `7` | 已完成过初始化的虚拟机丢失了磁盘或身份文件（其槽位目录会原样保留供排查） |
| `mac_readiness_interrupted` | `130` | `barn mac stop` 中断了首次启动期间的 SSH 就绪等待 |
{.wide}

## 文件

```filetree {title="$BARN_HOME/mac"}
config.json # 安装身份标识、默认基础镜像与 ssh_config_off 标记
images/
  ipsw/
    <build>.ipsw # 缓存的 Apple 恢复镜像（下载进行中为 .partial）
    <build>.ipsw.json # 恢复镜像元数据与校验摘要
  base/
    <id>/ # 只读、从未启动过的 macOS 基础镜像目录
slots/
  <name>/
    state.json # 虚拟机记录（schema 2）
    disk.asif # 基于基础镜像克隆的写时复制 APFS 磁盘层
    machine-id.bin # Apple Virtualization 机器标识
    auxiliary-storage.bin # NVRAM / 引导辅助存储
    id_ed25519 # 虚拟机专用 SSH 私钥
    id_ed25519.pub # 虚拟机专用 SSH 公钥
    known_hosts # 绑定到 barn-mac-<instance> 的固定主机密钥
    password # 随机生成的客机登录密码（权限 0600）
    runner.log # 虚拟机运行日志（由 barn mac logs 读取）
runtime/ # 全局状态锁与单机操作锁
```

其他宿主与客机文件路径：

- **运行时套接字**：`/tmp/barn-mac-<uid>-<hash>/`。
- **OpenSSH 配置片段**：`barn mac ssh-config` 负责维护 `~/.ssh/barn-mac_config` 以及 `~/.ssh/config` 中的 `# barn-mac:include` 区块（与 Linux 环境使用的 `# barn:include` 区块互不干扰）。执行 `barn mac ssh-config --remove` 会在 `config.json` 中写入 `ssh_config_off`，此后生命周期命令不会再自动写入 SSH 配置，直到你显式运行 `barn mac ssh-config --install`。
- **桌面窗口偏好设置**：Barn `0.9.2` 将窗口位置保存在 `~/Library/Preferences/com.pgsty.barn.plist`（`0.9.0` 使用 `~/Library/Preferences/io.pgsty.barn.mac-runner.plist`）。
- **Runner 查找机制**：CLI 根据解析符号链接后的自身可执行文件路径定位 runner，兼容 `Barn.app` 应用包、安装器与 Homebrew `libexec` 布局；开发调试时可通过环境变量 `BARN_MAC_RUNNER` 指定绝对路径、相对路径或 `~/` 路径。执行虚拟机操作前 CLI 会校验 runner 协议版本 `2`；`barn mac doctor` 还会检查 runner 的本地代码签名。
- **客机内部配置文件**：Barn 在客机内写入 `~/.ssh/authorized_keys`、`/private/etc/sudoers.d/80-barn` 与 `/etc/ssh/sshd_config.d/000-barn.conf`，设置电脑名称与本地主机名，并通过 `pmset` 禁用休眠。
