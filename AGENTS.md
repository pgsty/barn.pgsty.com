# 项目代理说明

## OINK build baseline

As of 2026-11-04, this site uses OINK v1.5.0 and Hugo Extended from the current
release channel. Keep CI and local builds on the latest available Hugo; do not
pin a patch version. If a deployment platform requires a literal version, use
Hugo Extended 0.169.0 until that platform supports its latest channel. Do not
enable `--panicOnWarning` or `HUGO_PANICONWARNING`; keep warnings visible and
review them. The upstream LibSass deprecation warning is accepted. No external
Sass compiler is required.

## Site extensions

These are Barn site code, not OINK features:

- `layouts/_partials/landing/barn-quickstart.html` renders the home quick start
  (`{type: markdown, key: quickstart, partial: …}` in `data/home/<lang>.yaml`):
  default-node facts beside the `demo` recording, with the macOS and Linux
  commands from `body` in a row underneath.
- `static/images/barn-first-run.cast` is a real first run recorded on `m3`;
  `bin/first-run-cast/` holds the driver, timing scripts, and re-recording
  steps. Re-record it when the first-run output changes, and keep the typed
  commands identical to the Linux commands in `body`.
- Home-page styles in `assets/scss/_styles_project.scss` are scoped under
  `.td-home` or `.barn-quickstart`. Capability transcripts on the home page
  must match real Barn 1.0 output; check them against `cmd/barn` before
  editing.
- Write Chinese prose in `.zh.md` and `data/*/zh.yaml` without hard line breaks
  between Chinese characters; browsers render each break as a space.

## Git 内容与大文件规则

用户于 2026-10-10 明确的通用仓库规则：

- 仓库默认保存源代码、配置和必要的轻量文档、元数据。构建产物、可执行文件、软件包、容器/虚拟机镜像、下载压缩包、数据库导出和大体积原始数据默认不进入 Git；文本格式的数据大文件同样需要检查。
- 在工作树内下载或生成上述文件之前，先选择仓库外的制品/数据位置，或补上合理的 `.gitignore` 规则并验证实际路径已被忽略，防止暂存和代理恢复/差异快照将它们写入 Git 对象库。
- 暂存、提交前检查新增文件的大小、类型和 staged 文件列表，只加入本次需要的源文件；不得用强制添加绕过忽略规则。优先保留来源清单、校验值及可复现的下载/构建方法。
- 对二进制素材、数据集或生成文件是否应纳入版本控制拿不准时，先问用户，再暂存或提交；确需例外时也先取得用户明确指示。
- 本规则不授权删除已有文件、stash、恢复快照或改写 Git 历史。忽略规则不会清除已存在的 Git 对象，历史清理需要单独明确范围。
