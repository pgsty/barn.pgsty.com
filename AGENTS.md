# Barn 伴生文档站

本仓库维护 `barn.pgsty.com` 的英文（`/`）与简体中文（`/zh/`）文档、设计文章和发布记录；产品源码在 `../barn`。写作规范见 [STYLE_GUIDE.md](STYLE_GUIDE.md)，构建入口见 [Makefile](Makefile)。

## 内容归属

- `content/docs/start/` 放任务指南，`content/docs/reference/` 放命令与配置契约，`content/docs/about/` 放项目说明。
- 新的架构设计、方案取舍、可复用研究结论与验收记录统一维护在本站：设计内容放 `content/blog/design/`，发布记录放 `content/blog/release/`，任务与契约放 `content/docs/`。源码仓库不再维护 `docs/` 目录；涉及代码的文章直接链接源码、测试或发布提交。
- 每篇英文 `page.md` 与中文 `page.zh.md` 成对维护；路由、日期、权重、显式标题锚点、命令和技术事实对齐。中文段落不在汉字之间硬换行。
- 按 `../barn` 的当前代码、测试和已发布标签核对行为，明确区分稳定版、未发布的 `main` 与未来提案。临时研究笔记放仓库外，不再建立 `reports/`、`research_notes/` 归档。

## 构建与检查

- OINK 版本以 `go.mod` 为准（当前 `v1.5.1`）；使用最新 Hugo Extended。CI 使用 latest 通道；部署平台必须填字面版本时，当前为 `0.169.0`。
- `make check` 校验模块、使用锁定主题构建生产站点并检查内链、锚点和资源；它会清除主题替换并关闭 Go/Hugo workspace。`make dev`、`make check-local` 用于联调相邻 `../oink`。
- 保留并审查构建警告；上游 LibSass 弃用提示可接受，不启用 `--panicOnWarning` / `HUGO_PANICONWARNING`，不要求额外 Sass 编译器。
- CLI/YAML 示例对照源码和帮助校验；需要执行 Barn 时使用临时 `BARN_HOME`。本地构建、提交、推送、部署与公开验收分别报告，修改文档不自动发布站点。

## 本站扩展

- `layouts/_partials/landing/barn-quickstart.html` 渲染首页快速上手，数据来自 `data/home/<lang>.yaml`；Pigsty full 四节点说明与录像并排，下方显示 macOS/Linux 命令。
- `static/images/barn-first-run.cast` 是 macOS 上 Homebrew 安装与 Pigsty full 启动的真实录像；重录方法在 `bin/first-run-cast/`。输出变化后重新录制，输入命令与首页 macOS 命令一致。
- 首页终端示例必须匹配对应 Barn 版本的真实输出；样式在 `assets/scss/_styles_project.scss`，作用域限定为 `.td-home` 或 `.barn-quickstart`。这些都是本站代码。

## Git 与制品

- 修改前检查 Git 状态，保留其他未提交工作，不自动 reset/stash/clean。
- Git 只收源代码、配置、必要的轻量文档与元数据。构建输出、可执行文件、包、镜像、压缩包、数据库导出和大体积数据放仓库外，或先设忽略规则并用 `git check-ignore` 验证。
- 暂存或提交前核对新增文件的类型、大小和 staged 列表，不强制添加被忽略文件；优先保留来源、摘要和复现方法。二进制素材、数据集或生成文件是否入库不明确时先询问用户，例外须明确授权。
- 忽略规则不授权删除已有文件、stash、恢复快照、清理 Git 对象或改写历史；清理须另有明确范围。
