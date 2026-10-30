---
title: 故障排查
description: 面向 setup、网络、镜像、漂移、中断状态与 SSH 的简短安全手册。
weight: 70
icon: fa-solid fa-life-ring
---

本手册提供 **Barn 0.9.2** 下 Linux 实验环境的常见问题排查步骤。macOS 客机请运行 `barn mac doctor` 并参阅 [Mac 故障排查章节](../macos/#故障排查)。

排查问题时，建议先采集以下三份 JSON 诊断报告（当没有其他命令持有部署锁时，`barn status` 还会自动收敛中断的虚拟机状态）：

```bash
barn doctor --json
barn network status --json
barn status --json
```

只要宿主计算能力检查通过，即使 `class: network` 检查报错，`barn doctor` 也会返回退出码 `0`——因此判断 `barn up` 能否正常接入私网前，请同时查看 `checks[]` 与 `barn network status --json`。

## 下载与 PATH 问题 {#下载与-path-问题}

安装脚本从 GitHub Releases 下载发行归档（`--mirror` 仅用于切换客机镜像仓库，不会重定向安装脚本下载）。若访问 GitHub 需要代理，请在终端中设置 `HTTPS_PROXY` 或 `ALL_PROXY` 环境变量（macOS 系统设置中的图形代理不会自动注入命令行环境）。

用户态安装脚本默认将程序安装到 `~/.local/bin`。若安装后提示找不到 `barn` 或仍显示旧版本，请检查当前 `PATH`：

```bash
export PATH="$HOME/.local/bin:$PATH"
command -v barn
barn version
```

请始终保持同一版本打包的 `barn` 与 `barn-hosts-helper` 处于原有的相对目录结构中。

## 找不到主机清单

当既没有配置文件也没有已应用部署时，交互式运行 `barn up` 会自动生成初始 `barn.yml`。如需使用现有清单，请在 `barn.yml` / `pigsty.yml` 所在目录运行 `plan`、`up` 或 `validate`，或显式传入 `-f /path/to/file`（也可先运行 `barn init` 生成模板）。

未指定 `-f` 时，`plan`、`up`、`reload` 和 `recreate` 会按 `barn.yml`、`barn.yaml`、`pigsty.yml`、`pigsty.yaml` 的顺序查找当前工作目录，仅在四个文件都不存在时回退到 `BARN_HOME` 中的已应用规格。若匹配到的第一个文件存在语法错误，命令会立即报错退出；当旧的 `barn.yml` 与目标 `pigsty.yml` 同处一个目录时，请显式传入 `-f pigsty.yml`。

若 `barn status` 提示 `no deployment state found`，说明当前 `BARN_HOME` 下尚无已应用部署（全新环境或刚执行过 `purge`）。

## init 拒绝目录符号链接 {#linked-directory}

Barn 0.9.2 报出 `atomic create parent is not a real directory: ...` 时，可能只是输出目录为符号链接，即使其目标是可写的真实目录也会触发。[未发布的路径修复](../../about/unreleased/#paths)已支持解析目录链接，并为 `init -o` 创建缺失的父目录。

使用 0.9.2 时，可临时改用物理目录路径输出：

```bash
barn init -o "$(pwd -P)/barn.yml"
```

也可先执行 `cd -P .` 再运行 `barn init`，原目录符号链接可以保留。0.9.2 输出到多级新路径时，请先创建父目录。覆盖已有文件仍需 `--force`，写入操作不会跟随输出文件本身的符号链接。

## setup 需要 sudo

`barn setup` 在请求密码前会先打印即将执行的宿主变更明细，并在特权步骤开始时将当前终端直接交给 `sudo`。`--yes` 仅用于自动确认 Barn 的变更计划，不会绕过 `sudo` 本身的身份认证；无人值守环境需预先配置免密 `sudo`（`NOPASSWD`）或有效凭据缓存。你可以随时运行 `barn setup --dry-run` 预览计划。

在 macOS 上，`barn setup` 会先完成固定版本 `socket_vmnet` 软件包的下载与校验，随后才请求管理员权限，因此下载失败不会触发密码提示。

## 原生加速或兼容运行时不可用 {#原生加速或兼容运行时不可用}

Barn 依赖 macOS HVF 或 Linux KVM 提供原生硬件虚拟化加速，仅在显式配置跨架构 `vm_arch` 或命中内置兼容规则（如在 Apple Silicon 上运行 `el8` `arm64`）时启用 QEMU TCG 软件模拟；原生 HVF/KVM 异常绝不会自动降级为 TCG。

Homebrew 的 `qemu` 配方已同时包含 `arm64` 与 `amd64` 系统模拟器，而 Linux 宿主的 `barn setup` 仅安装宿主原生架构的模拟器——在 Linux 上运行跨架构客机前，请先安装对应的 `qemu-system-*` 二进制与 UEFI 固件。

## 网络状态为 partial 或 invalid

若宿主网络配置完整但处于未激活状态，交互式运行 `barn up` 即可自动恢复。若 `barn network status` 报告 `partial` 或 `invalid`，请通过内置卸载命令预览并清理受管资源，切勿手动删除系统网络配置文件：

```bash
barn network status --json --verbose
barn network uninstall --json
barn network uninstall --yes
```

若 Linux 网桥冒烟测试在 `setup` 期间失败，Barn 会自动回滚网络配置；仅当输出明确的 `automatic rollback failed` 时才需人工介入。

在 macOS 上，`barn setup` 可自动修复缺失或权限过严的 `/var/log/barn-vmnet` 目录（标准权限为 `root:wheel 0755`），但若该路径被替换为符号链接、属主异常或对同组/其他用户可写，Barn 会拒绝自动修改——请按 `barn network status` 给出的诊断命令手动修复。

## Linux bridge helper 失败

在 Debian / Ubuntu 宿主上，请检查 `/usr/lib/qemu/qemu-bridge-helper` 的属主、属组与 setuid 权限位（应为 `root:<当前用户所属组> 4750`）：

```bash
id
stat -c '%U:%G %a %n' /usr/lib/qemu/qemu-bridge-helper
dpkg-statoverride --list /usr/lib/qemu/qemu-bridge-helper
```

## plan 报告 recreate 或 missing

- **`recreate`**：节点的虚拟机规格定义已变更。请先查看 `barn plan` 并备份根盘或非持久数据盘上的文件，再运行 `barn recreate <node>`（非交互环境需加 `--force`）。
- **`missing`**：已创建的节点从 YAML 清单中被移除。可恢复该节点的 YAML 条目，或执行 `barn destroy <node>` 将其销毁。

采用[未发布的节点选择规则](../operations/#selected-nodes)后，`barn plan node-1` 与 `barn recreate node-1` 会保留未选中节点的已应用定义，无关节点的编辑不再要求一起重建。地址、别名、控制节点角色及部署公共设置的真实冲突仍需处理。

## 节点未就绪 {#节点未就绪}

节点就绪要求管理 SSH 可连通且客机实例 UUID 校验一致。若某个节点无法创建、启动或建立管理 SSH 连接，`barn up` 会指出故障节点与所处阶段，并以退出码 `5` 结束。请先查看对应日志：

```bash
barn logs <node>                  # 客机串口控制台日志
barn logs <node> --source qemu    # QEMU 进程标准错误与诊断日志
barn logs --source events         # 宿主准备与部署事件日志
barn status
```

附加数据盘、Virtio-9p 共享目录、主机名、客机 `/etc/hosts`、控制节点 SSH 与固定 IP 私网网卡均在管理 SSH 就绪后独立初始化。单一步骤失败不会阻断管理 SSH，`barn up` 仍会返回退出码 `0` 并在 `nodes[].warnings` 中列出受限项：

| 报告的功能限制 | 处理方法 |
|---|---|
| 数据盘不可用 | 排查设备缺失、文件系统工具、挂载繁忙或宿主 I/O 错误后，重新运行 `barn up` |
| 共享目录只读 | 核对宿主与客机的实际写权限后，重新运行 `barn up` |
| 客机 hosts 或控制节点 SSH 未完成 | 重新运行 `barn up` 刷新客机内的托管文件 |
| 私网网卡不可用 | 检查 `barn network status`，修复宿主网桥或 vmnet 后重新运行 `barn up` |

排除故障后再次运行 `barn up`，Barn 会仅重试未完成的阶段而不重启健康节点（若测试数据盘文件系统无法识别或已确认损坏，恢复流程可能会将其重新格式化；详见[数据盘说明](../../reference/configuration/#数据盘)）。若希望在首次准备失败时当场清理未完成产物，可在运行 `barn up` 时加上 `--rollback`。

Linux 目录共享要求 QEMU 与客机内核均支持 9p；如果客机内核不支持，修正宿主路径也无法挂载，可改用 SSH/SCP/rsync 或支持 9p 的内核。macOS 宿主向 Linux 客机共享目录还需要[未发布的修复](../../about/unreleased/#sharing)；原生 macOS 客机使用独立的 VirtioFS。

## SSH 失败

请依次检查 `barn status`、`barn ssh-config` 与 `barn logs <node>`：

- **部署密钥恢复**：若宿主侧公钥文件缺失，Barn 会在启动时根据完好的私钥自动重新派生；若私钥本身丢失，请从备份恢复原私钥——Barn 不会为已存在的虚拟机重新生成新身份。若控制节点内的私钥副本丢失，`barn up` 会报告 `control-ssh` 限制，此时宿主到客机的管理 SSH 依然可用。
- **端口重分配与主机密钥隔离**：若已停止虚拟机的回环管理端口被其他进程占用，下次启动时会自动改用空闲端口并刷新 `~/.ssh/barn_config`。SSH 主机密钥按虚拟机实例 UUID 独立记录，因此重建节点不会引发 `known_hosts` 冲突。
- **由 dotfile 工具管理的 `~/.ssh/config`**：当 `~/.ssh/config` 是符号链接或硬链接时，Barn 只会生成 `~/.ssh/barn_config` 并提示你手动添加 `Include` 行。若 `barn ssh meta` 正常而直接执行 `ssh meta` 失败，请先核对该 `Include` 配置。
- **远端命令分隔符**：在节点名与远端命令之间请使用 `--` 分隔（如 `barn exec meta -- hostname`），详见 [SSH 透传与命令补全](../../reference/cli/#ssh-透传与命令补全)。

## 镜像目录或镜像校验失败

Barn 二进制内置了 active 与 standby Minisign 公钥，会严格拦截未知签名者、目录版本回滚、文件尺寸或 SHA-256 不匹配以及存在安全隐患的 `qcow2` 结构。请始终使用正确签名的镜像仓库，或通过 `barn image import --sha256 ...` 导入本地镜像，切勿直接将文件手动拷入 `~/.barn/images`。

## 命令被中断 {#命令被中断}

请先运行 `barn status`：若后台仍有其他 Barn 命令持有部署锁，输出会附带 `note` 提示——请等待该命令自然结束，切勿将其视为异常中断。

当没有进程持锁时，`barn status` 会比对记录的 QEMU PID 与进程启动时间戳，确认进程真实身份后自动收敛状态：

| 中断场景 | 自动恢复与后续操作 |
|---|---|
| 宿主重启，或原 QEMU PID 被其他无关进程复用 | `barn status` 识别出进程身份不匹配后将节点标记为 `stopped`，随后执行 `barn start` 即可 |
| `barn stop` 中断，但 QEMU 仍在运行 | `barn status` 将状态恢复为 `running`；仍需关机时再次执行 `barn stop` |
| 首次 `barn up` 在准备阶段中断 | 修正清单后重新执行 `barn up -f barn.yml`，Barn 会自动回滚事务日志中未完成的产物 |
| `barn destroy` 执行中途中断 | 按相同的销毁范围重新运行 `barn destroy` 或 `barn purge` 即可完成清理 |

如果 Barn 无法确认记录的进程身份（或者 QEMU 进程仍在运行但 QMP 套接字丢失），它会拒绝后续变更操作以防误杀无关进程。请保留现场状态目录并通过 `barn logs <node> --source qemu --verbose` 排查原因，切勿手动删除节点目录、套接字或篡改状态文件中的 PID。

在 GitHub 提交问题报告时，请附上完整命令与退出码、`barn version`、宿主操作系统与架构、QEMU 版本，以及开头三份 `--json` 诊断输出。
