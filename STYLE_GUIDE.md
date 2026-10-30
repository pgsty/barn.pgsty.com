# Barn documentation style

Write for engineers who want to install Barn, bring up a VM, or look up a specific configuration field or CLI option. Use clear, direct technical prose in both English and Simplified Chinese.

## Core razor

Before keeping any caveat, transition, negative comparison, or summary sentence, ask:

> **If we delete this sentence, what specific command will the reader mistype, what parameter will they misconfigure, or what essential technical fact or design trade-off will they miss?**

If the answer is "nothing", delete it immediately.

## Organize around the reader's task

- Lead with the goal and prerequisites, then show the steps and expected output.
- Introduce a concept when the reader first needs it, explaining what it does before how it works internally.
- Keep tutorials focused on one working path; leave exhaustive option tables for the reference pages.
- Give each shared concept one authoritative home (`BARN_HOME` deployment scope, data-disk recovery boundaries, pre-release packaging, or CLI argument separators) and link to it from other pages instead of repeating boilerplate paragraphs.
- Place specific data-loss warnings immediately before the affected command, stating the trigger condition, what gets overwritten, and how to inspect the plan first.

## Write natural, connected prose

- **Favour rhythm and logical flow over rigid word-count caps.** Combine closely related facts (such as filename characters, extensions, and cache location) into a single coherent sentence instead of chopping them into robotic five-word fragments.
- Use active verbs and name the actor when ambiguity is possible. Keep "can", "must", and "should" distinct.
- State what a command or check actually verifies and what step comes next. Never pad sections with defensive disclaimers ("X does not establish Y", "A successful build does not prove Z", "No new VM replay is claimed here").
- Avoid false negative contrasts ("This is an excerpt, not a replacement for the entire file"; "A separate subnet describes the topology; it is not a firewall policy"). State directly how to use the snippet or where the boundary lies.
- Do not lecture the reader ("Do not parse human text as an API"). Show the `--json` flag and `jq` filter directly.

## 简体中文写作与排版规范

- **地道的技术母语表达**：像资深系统程序员一样用自然的中文主动句和动宾结构写作（例如写“检查配置”而非“对配置进行检查”，写“无法确认旧节点身份时，Barn 会中止操作”而非“遗留节点产物的身份无法确认时，Barn 仍会拒绝继续”）。
- **句群连贯**：将紧密相关的条件、原因和结果自然衔接，切勿按英文短句生硬切碎，也不要照搬欧化被动句式。
- **保留英文原样的标识符**：CLI 命令名、子命令、标志（`--json`）、配置键（`ip_base`）、环境变量（`BARN_HOME`）、镜像名称（`el10`）及路径保持英文原样并置于反引号内。首次出现 `Barn.app` 时，说明它是 macOS 宿主上的原生应用包。
- **中英文与加粗排版间距**：中文 `.zh.md` 中，`**加粗**`、`*斜体*` 与前后的普通中英文字符或数字之间保留一个半角空格（紧邻中文全角标点时除外），冒号放在加粗标记外部（写作 `**适用条件**：正文`）。

## Terms that need consistent names

| English | 中文 | Meaning |
| --- | --- | --- |
| host | 宿主 | The computer that runs Barn and the virtualization backend |
| guest | 客机 | The operating system inside a VM |
| virtual machine (VM) | 虚拟机 | The machine that Barn creates and manages |
| node | 节点 | A named member of a Linux lab |
| inventory | 主机清单；上下文明确时简称“清单” | The YAML file that defines Linux nodes |
| control node | 控制节点 | The Linux node that manages the other nodes |
| image repository | 镜像仓库 | The source of catalog metadata and image files |
| image catalog | 镜像目录 | Metadata that describes image versions and files |
| base image | 基础镜像 | The shared image from which a VM disk derives |
| root overlay | 根盘写时复制层 | A separate file that stores one VM's root disk changes |
| persistent data disk | 持久数据盘 | A data disk retained during ordinary VM destruction |

Use "Linux lab" / "Linux 实验环境" for the user's environment, and "deployment" / "部署" when explaining configuration or runtime state. Keep terminology consistent across pages.

## Use OINK v1.4.0 components purposefully

- Use ```` ```filetree ```` fences with `#` comments for directory layouts (`$BARN_HOME/images/`, `$BARN_HOME/mac/`).
- Add `{title="barn.yml"}` or script filenames to configuration and script code blocks, and use `{tab="..." group="..." value="..."}` on adjacent code fences for multi-platform command comparisons.
- Add `{.steps}` to sequential ordered lists in tutorials and operational runbooks, and `{.cards}` to navigation link lists on section index pages.
- Add `{.wide}` (and `{.expand}` where helpful) to dense reference tables while preserving project classes such as `{.platform-table}` and `{.evidence-table}`.
- Use GitHub-style callouts (`> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, `> [!CAUTION]`) sparingly; never stack two callouts back-to-back or nest them.

## Review the result

Read the page as a user: can you find the next command and its flags without wading through boilerplate? Read paragraphs aloud in both languages to verify that they flow naturally.

Compare English and Chinese pages side by side (`page.md` and `page.zh.md`). Preserve all front matter routing fields (`url`, `aliases`, `weight`, `date`, `version`), explicit heading anchors (`{#...}`), commands, defaults, paths, versions, dates, and test evidence. Run `make check` to validate the production Hugo build and internal link/fragment integrity before committing.
