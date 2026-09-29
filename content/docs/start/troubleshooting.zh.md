---
title: 故障排查
description: 面向 setup、网络、镜像、漂移、中断状态与 SSH 的简短安全手册。
weight: 70
icon: fa-solid fa-life-ring
---

本页描述 **Barn 0.9.0**。使用版本相关说明前，请先检查 `barn version`。

macOS 客机请使用 `barn mac doctor`，并查看 [Mac 故障排查](../macos/#故障排查)。
以下诊断针对 Linux 环境。

先收集诊断信息（`status` 可能收敛中断的运行时状态）：

```bash
barn doctor --json
barn network status --json
barn status --json
```

## 下载与 PATH 问题

安装器从 GitHub 发布版本下载程序；`--mirror` 选择的是 Barn 镜像仓库，不会重定向安装器
下载。如果访问 GitHub 需要代理，在终端将 `HTTPS_PROXY` 或 `ALL_PROXY` 设置为已有代理的
地址。macOS 系统代理设置本身不会替命令行工具配置这些环境变量。

用户态安装器默认写入 `~/.local/bin`。安装后找不到 `barn`，或版本仍旧时，检查当前使用的
程序路径：

```bash
export PATH="$HOME/.local/bin:$PATH"
command -v barn
barn version
```

Homebrew 或系统软件包安装应使用对应渠道的程序。CLI 与配套 `barn-hosts-helper` 应来自
同一发布版本，并保留软件包规定的相对位置。

## 找不到主机清单

尚无部署时，交互式 `up` 可以生成首份默认配置。显式使用配置时，在
`barn.yml`/`pigsty.yml` 所在目录运行 `plan`、`up`、`validate`，
传入 `-f /path/to/file`，或运行 `barn init` 生成一份。状态存在后，`plan`、`up`、
`reload`、`recreate` 可回退到已应用规格；status、start、stop、SSH 与 destroy 始终使用
已应用状态。如果 `status` 报告 `no deployment state found`，说明所选 `BARN_HOME`
没有已应用部署，可能是首次使用，也可能已执行过 purge。

## setup 需要 sudo

提示前一行会说明具体宿主变更；特权步骤开始时 Barn 会直接把交互终端交给 sudo。
`--yes` 只接受 setup 计划，不会绕过 sudo 认证。自动化环境需要已有凭据或合适的
NOPASSWD 策略。可以先用 `barn setup --dry-run` 查看计划。

macOS setup 会在请求管理员认证之前准备固定版本的 socket_vmnet 来源，下载失败不会
要求密码。setup 计划明确说明 sudo 用途与 socket_vmnet 来源；若首次
确认后自动选择的子网改变，会再次确认，除非已经传入 `--yes`。

## 原生加速或兼容运行时不可用

原生路径需要 macOS HVF 或 Linux KVM。只有显式外来 `vm_arch` 或内置镜像/宿主兼容规则
才会选择 TCG；任意原生失败绝不会静默回退。Homebrew QEMU 包含两个系统模拟器；
Linux setup 只安装宿主原生家族，因此外来客机还需要对应 `qemu-system-*` 与固件。

`plan` 解析镜像目录镜像及目标运行时时无需安装 QEMU；导入的 `local-*` 镜像仍需要
`qemu-img` 与有效缓存。`up`、`recreate` 在变更 VM 资源前检查
所选模拟器与固件。TCG 性能结果没有参考意义。

## 网络是 partial 或 invalid

完整但未激活的 Barn 网络可由交互式 `up` 恢复；对于 partial 或 invalid 安装，
不要手工删宿主文件，先查看受控清理计划：

```bash
barn network status --json --verbose
barn network uninstall --json
```

未加 `--yes` 的 JSON 输出只展示删除计划；网络计划仍可能需要 sudo 读取受保护的
归属状态。核对计划后，使用 `barn network uninstall --yes` 执行。
普通终端输出会询问 `[y/N]`，确认后立即执行。Linux bridge smoke 失败会自动回滚安装；
只有出现 `automatic rollback failed` 才表示必须人工检查。

macOS 的 `/var/log/barn-vmnet` 缺失或权限过紧时可以修复。查看 `network status`
的诊断，预期为 `root:wheel 0755` 目录。`barn setup` 能修复归属可确认的安装；
手工修复时使用诊断给出的准确命令。符号链接、错误属主或组/其他用户可写目录不会自动
修复。不要仅凭桥接接口名称判断路由冲突。

## Linux bridge helper 失败

```bash
id
stat -c '%U:%G %a %n' /usr/lib/qemu/qemu-bridge-helper
dpkg-statoverride --list /usr/lib/qemu/qemu-bridge-helper
```

Debian/Ubuntu 使用 `root:<调用者可用组> 4750`。桌面系统通过 ACL 获得 `/dev/kvm`
权限时，调用者不必静态加入 `kvm` 组。

## plan 报 recreate 或 missing

`recreate` 表示节点定义已改变：先用 `barn plan` 查看，再运行 `barn recreate <node>`。
终端上该命令会要求输入 `recreate` 确认，无终端时必须传入 `--force`。`missing` 只是报告：
恢复主机条目，或运行 `barn destroy <node>`。

## 节点未就绪

就绪要求管理 SSH 可用且客机实例身份一致。节点无法创建、启动或连接时，节点级部分
失败结果会指出节点和阶段，并以 5 退出。缺少宿主能力、主机清单冲突等全局失败则使用
各自的退出类别。先查看日志：

```bash
barn logs <node>                  # 串口控制台
barn logs <node> --source qemu    # QEMU 诊断
barn logs --source events        # 部署/setup 事件，首次 VM 创建前也可读取
barn status
```

数据盘、共享目录、主机名、客机 hosts、控制节点 SSH 与私网分别初始化，一项失败不会
阻止管理 SSH 或其他步骤。客机可用时返回 0，并列出具体限制；JSON/YAML 通过
`nodes[].warnings` 暴露这些问题。访问互联网不是就绪的前提。

| 功能限制 | 下一步 |
|---|---|
| 数据盘不可用 | 处理设备暂缺、探测、工具、挂载占用或 I/O 问题，再执行 `up` |
| 共享目录只读 | 修正宿主权限，再执行 `up` 重试可写挂载 |
| 客机 hosts 或控制节点 SSH 未完成 | 执行 `up` 刷新托管文件 |
| 私网网卡不可用 | 检查 `barn network status` 后再次 `up`；管理 SSH 仍可能可用 |

修正原因后重复 `up`：它会重试未完成步骤、原位更新旧客机脚本、跳过健康步骤，不重启
运行中的 VM。无法识别或确认损坏的测试数据文件系统会自动清空重建，**包括持久盘**，
结果会报告旧数据已丢弃。探测失败、忙碌挂载和 I/O 故障不会触发格式化。详见
[数据盘说明](../../reference/configuration/#数据盘)。

重复 `up` 也可清理能够确认归属的中断准备残留。`--rollback` 在同一次运行中清除 prepare
失败的产物，并在 `rolled_back` 中列出。`--no-wait` 在 QEMU 运行后即返回，跳过就绪检查、
客机恢复与元数据刷新；后续执行 `up` 补齐。

## SSH 失败

Barn 在启动时会从完好的原私钥恢复缺失的部署公钥。若私钥丢失，需要从备份恢复同一把私钥；Barn 不会为已有 VM 生成替代身份。
这是宿主侧派生公钥的恢复，与控制节点中缺失的客机私钥是两种情况。
`up` 也会检查当前安装的客机 key：文件缺失时报告 `control-ssh` 限制，管理 SSH
仍可使用。恢复原客机 key 后执行 `up` 会清除限制；Barn 不会自动向已有客机重新注入私钥。

检查 `barn status`、`barn ssh-config` 与串口日志。Barn 自身 SSH 使用回环管理端口；
Ansible 直连固定 IP。
若已停止 VM 的自动分配管理端口被其他进程占用，下次启动会选择空闲端口并刷新 SSH 别名；
运行中的 VM 保留原端口。SSH 主机密钥信任按 VM 实例 UUID 区分，重建 VM 无需删除无关的
known-host 条目；同一实例的密钥变化仍会校验失败。

`doctor` 的通用可用性扫描会排除已应用部署保留的固定 IP；`up` 与 `start` 仍会拒绝
已经接受 SSH 的新增节点或已停止节点地址。

`~/.ssh/config` 为符号链接或硬链接时不会被改写；Barn 会生成
fragment，并给出需要通过 dotfile 管理器添加的 `Include` 行。若 `barn ssh meta`
可用但 `ssh meta` 不可用，应先检查 Include，不要更换客机密钥。`ssh`/`exec`
会在含数字或 `-` 的参数匹配近似节点名规则时拒绝执行并给出建议；需要明确区分节点
选择器与远程命令时
使用 `--`。

## 镜像目录或镜像校验失败

当前二进制已内置 active 与 standby 镜像目录公钥。未知签名者、版本回滚/同版本异内容、
工件尺寸/SHA 不符、qcow2 结构不安全属于不同完整性错误。使用正确签名仓库，或通过
`barn image import --sha256 ...` 导入；不要直接向 `~/.barn/images` 复制字节。

## 命令被中断

先确认是否仍有其他 Barn 命令运行。Barn 0.9.0 的 `status` 不排队等待，
其他命令持有部署锁时会读取已写入状态并显示 `note`。应先等待该命令结束，再判断
中间状态是否属于异常中断。

没有操作持锁时，运行 `barn status`。可证明存活或死亡的运行时会按记录的完整身份
收敛；歧义进程继续阻塞。不要只凭状态文件里的 PID 就杀进程。

Barn 0.9.0还支持以下恢复：

| 中断场景 | 恢复步骤 |
|---|---|
| 宿主重启或 QEMU PID 被复用 | `status` 确认 PID 属于无关进程后将原 VM 标记为停止，再用 `start` 启动 |
| `stop` 中断，QEMU 仍在运行 | `status` 恢复运行状态；仍需关机时再次执行 `stop` |
| 首次 `up` 在准备阶段失败 | 修正主机清单后再次执行 `up -f /path/to/barn.yml`，只回滚日志记录的未完成产物 |
| `destroy` 执行到一半中断 | 使用相同的显式销毁范围重试；中间状态与已保留的持久盘都可继续处理 |

如果恢复仍然失败，请保留状态与日志，不要删除节点目录或改写 PID 来模拟恢复成功。

如果记录的 QEMU 进程仍存在，但 QMP 套接字缺失，应先保留证据并查看串口/QEMU 日志，
再决定是否用 `stop` 收敛。不要手工删除运行时套接字或状态文件。

通用错误信封的 `error` 字段使用稳定类别，另有可选的 `reason`、
`next` 与 `command` 中的外部程序详情；部分命令返回自身的诊断报告。根据原因与下一步
提示处理，不要把人类可读文本当作
接口解析。退出码与结果处理见[自动化](../automation/)。事件与 QEMU 日志按易读记录
展示，需要完整 QEMU 参数时加 `--verbose`。

提交问题时请包含准确命令与退出码、`barn version`、上面三份 JSON、宿主系统/架构与
QEMU 版本。
