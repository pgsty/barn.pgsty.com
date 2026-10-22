# Barn documentation style

Write for readers who want to install Barn, run a VM, or find a specific option.
Use [ASD-STE100 Issue 9](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf)
as the English writing reference. Apply the same clarity principles to Chinese,
with natural Chinese grammar. This guide records project conventions; it is not
a substitute for the standard or its dictionary.

## Organize around the reader's task

- Start with the purpose and prerequisites. Then give the steps and expected result.
- Introduce a term when the reader first needs it. Explain its effect before its implementation.
- Keep tutorials on one working path. Put alternative settings in the reference.
- Start each paragraph with its topic. Use the remaining sentences to develop that topic.
- Keep conditions, causes, and results connected. Use words such as “if”, “because”, and “then” where they clarify the relationship.
- Give each fact one useful place. Repeat it only when a reader needs it to complete the current task safely.
- Put a specific data-loss warning before the affected command. State the condition, consequence, and action to take.

## Write clear, connected sentences

In English, use at most 20 words per instruction and 25 per descriptive sentence.
Rewrite a long sentence around its meaning; do not split it at an arbitrary word count.
A sequence of short sentences must still explain how the ideas connect.

Use direct verbs and name the actor when it could be unclear. Use one instruction
per sentence and number steps that must run in order. Keep complete grammar,
including articles. Use a list for steps or parallel items, not for every sentence.

Use a consistent term for each concept. Refer to the STE dictionary for general
English words and their approved meanings. Retain established software terms and
literal command names. Avoid idioms, promotional claims, and abstract noun chains.

State known behavior directly. Keep “can”, “must”, and “should” distinct. Retain
real exceptions; do not add speculative warnings or general disclaimers.

## 简体中文

先说明读者要完成什么，再按操作顺序展开。需要某个术语时再解释，不在开头堆放实现细节。
“宿主”是运行 Barn 的电脑，“客机”是虚拟机内的系统。第一次出现时，可结合上下文说明。

使用直接、自然的表达，如“检查配置”，不写“对配置进行检查”。一句话说明一个主要意思，
但不要机械拆开紧密相关的条件、原因和结果。中文不套用英文词数限制。

能用常见中文说明的概念，不必夹杂英文。命令、参数、文件名和产品名称保持原样。
保留有实际意义的“可能”“仅”“必须”，删除重复提醒和无信息的强调。

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

Use “Linux lab” / “Linux 实验环境” for the user's environment. Use “deployment” /
“部署” when explaining configuration or state. Do not alternate terms for variety.

## Review the result

Read the page as a user: can you find the next action without learning unrelated details?
Read paragraphs aloud: do they flow, or do they sound like disconnected commands?
Keep an existing sentence when it already answers those questions well.

Compare both languages with the documented release. Preserve commands, defaults,
paths, versions, dates, test results, and real limits. If you remove a repeated fact,
make sure its explanation remains where the reader needs it. Preserve heading anchors
and valid link targets. Keep historical results separate from current instructions.

Run `make check` and preview changed pages. Sentence-length tools can identify
passages to review, but cannot establish clarity, technical accuracy, or STE compliance.
