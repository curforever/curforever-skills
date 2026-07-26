# curforever-skills README 改写设计

**状态：** 待审阅

## 目标

将仓库首页从内部技能索引改为面向公开读者的产品式 README，使首次访问者能在最短路径内理解：

1. 这个仓库提供什么；
2. `read-coach` 是否适合自己；
3. 如何为自己的 AI agent 全局安装；
4. 使用后会得到什么；
5. 是否存在隐私、网络或外部 API 风险。

README 以中文为主，在标题区和安装区保留简短英文信息。内容只声明已经验证的能力和平台，不宣称安装量、成熟度或未验证的兼容性。

## 信息架构

1. 项目名称、中文价值主张和简短英文说明；
2. 面向 Codex 的快速开始；
3. `read-coach` 的核心能力；
4. Codex、Claude Code、Cursor、GitHub Copilot 的全局安装命令；
5. 从给出文章路径到生成学习报告的最短使用示例；
6. `.read-coach.md` 的六个固定章节与原文不被修改的承诺；
7. 隐私与安全边界；
8. 技能目录、开发状态、贡献入口与许可证。

## 安装策略

主路径采用 GitHub CLI 的 `gh skill install`，使用精确子路径：

```bash
gh skill install curforever/curforever-skills skills/learning/read-coach \
  --agent <agent> --scope user
```

支持的 `agent` 值仅列出已由 GitHub CLI 官方文档确认的：`codex`、`claude-code`、`cursor` 和 `github-copilot`。安装后提示用户重启对应 agent。

由于 `gh skill` 仍为预览功能，Codex 区保留系统 `skill-installer` 的 Python 备用方案，并提示用户先审阅 skill 内容。

## 示例与安全说明

README 展示一个简短的本地 Markdown 路径示例，以及五步结果流程：快速结论、学习模式选择、知识地图、逐题互动、单份学习报告。

安全说明明确以下事实：

- skill 仅读取用户指定的材料，不修改原文；
- 随附脚本仅使用 Python 标准库，不调用外部 API；
- 评分是带依据的辅助判断，不等同于事实核验；
- 用户可在安装前审阅 `SKILL.md` 与脚本；
- 真实材料和生成报告不应提交到仓库。

## 非目标

- 不提供未验证的平台专用命令；
- 不添加虚构 badge、下载量、star 数或性能承诺；
- 不把完整技术设计重复到 README；
- 不包含本机绝对路径、雇主信息、个人邮箱或其他身份信息。
