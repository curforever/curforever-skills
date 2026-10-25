# curforever-skills

一组可复用的 Agent Skills，帮助 AI 编码 Agent 以更稳定、可审阅的流程完成特定任务。

> Practical Agent Skills for learning, development, design, and project continuity.

40 个可单独安装的技能，按六个主题分组。现有安装路径保持稳定；每个技能只携带可复用的说明、脚本和参考资料。

## 从任务选择技能

| 你想完成的事 | 建议入口 |
| --- | --- |
| 判断材料是否值得读，并通过问答掌握 | `read-coach` |
| 从日常疑问写短故事，理解机制与不同人的代价 | `everyday-mechanisms` |
| 读懂真实代码的业务流程 | `code-reading-coach` |
| 从笔记、课程或培训中找到可用方法 | `training-apply` |
| 查看 AI 资讯、整理后续追问 | `ai-news-local`、`ai-news-qa` |
| 编写或改进提示词 | `prompt-writer`；需要框架选择时用 `prompt-architect` |
| 澄清需求并形成实施计划 | `brainstorming` → `writing-plans` |
| 设计新界面、审查已有界面 | `frontend-design`；需要完整工具流程时用 `impeccable` |
| 设计落地页或作品集、改版现有页面 | `design-taste-frontend`、`redesign-existing-projects` |
| 切换会话或安排多个 Agent 接力 | `handoff`、`multi-agent-cowork` |
| 维护项目状态、知识与修复经验 | `project-*` 系列 |

按任务选一个入口，需要时再组合；不要一次加载全部设计/流程技能。`grill-me`、`grill-with-docs` 与 `handoff` 保留显式调用设置。`multi-agent-cowork` 使用本地共享文件，不会自行启动其他 AI 或发送消息。

## Skills

<!-- skill-catalog:start -->

### 开发与工程

| Skill | 说明 | 安装路径 |
| --- | --- | --- |
| [brainstorming](skills/development/brainstorming/) | 在创作或实现前梳理需求与设计 | `skills/development/brainstorming` |
| [code-planner](skills/development/code-planner/) | 生成范围清晰、可执行的编码任务提示 | `skills/development/code-planner` |
| [code-reading-coach](skills/development/code-reading-coach/) | 以业务问题驱动的交互式源码学习 | `skills/development/code-reading-coach` |
| [code-reviewer](skills/development/code-reviewer/) | 只读审查代码变更及其测试证据 | `skills/development/code-reviewer` |
| [domain-modeling](skills/development/domain-modeling/) | 澄清领域术语并维护术语表与架构决策 | `skills/development/domain-modeling` |
| [find-skills](skills/development/find-skills/) | 查找并评估适合当前任务的公开技能 | `skills/development/find-skills` |
| [github-project-planner](skills/development/github-project-planner/) | 调研 GitHub 同类开源项目并制定可落地的开发方案 | `skills/development/github-project-planner` |
| [grill-me](skills/development/grill-me/) | 通过逐轮追问检验方案与设计 | `skills/development/grill-me` |
| [grill-with-docs](skills/development/grill-with-docs/) | 检验方案并沉淀领域术语与决策 | `skills/development/grill-with-docs` |
| [grilling](skills/development/grilling/) | 梳理方案的决策依赖并追问关键选择 | `skills/development/grilling` |
| [prompt-architect](skills/development/prompt-architect/) | 按任务意图分析并改进提示词 | `skills/development/prompt-architect` |
| [prompt-writer](skills/development/prompt-writer/) | 为其他 AI 编写明确、可执行的提示词 | `skills/development/prompt-writer` |
| [skill-manager](skills/development/skill-manager/) | 脱敏、规范化并发布本地技能集合 | `skills/development/skill-manager` |
| [workflow-to-skill](skills/development/workflow-to-skill/) | 从会话与项目记录提炼重复工作流并整理为 skill | `skills/development/workflow-to-skill` |
| [writing-plans](skills/development/writing-plans/) | 将已确认需求拆为有验收依据的实施计划 | `skills/development/writing-plans` |

### 界面设计

| Skill | 说明 | 安装路径 |
| --- | --- | --- |
| [design-taste-frontend](skills/design/design-taste-frontend/) | 设计有明确视觉方向的落地页与作品集 | `skills/design/design-taste-frontend` |
| [frontend-design](skills/design/frontend-design/) | 为新界面选择有辨识度的视觉方向 | `skills/design/frontend-design` |
| [impeccable](skills/design/impeccable/) | 设计、审查和改进界面体验 | `skills/design/impeccable` |
| [redesign-existing-projects](skills/design/redesign-existing-projects/) | 审查并改进已有网站或应用的视觉设计 | `skills/design/redesign-existing-projects` |

### 学习与知识

| Skill | 说明 | 安装路径 |
| --- | --- | --- |
| [ai-news-local](skills/learning/ai-news-local/) | 核实 AI 资讯并生成本地日报，保留延伸问答 | `skills/learning/ai-news-local` |
| [ai-news-qa](skills/learning/ai-news-qa/) | 按主题整理指定日期日报的本地延伸问答 | `skills/learning/ai-news-qa` |
| [read-coach](skills/learning/read-coach/) | 评估学习材料并通过问答帮助掌握内容 | `skills/learning/read-coach` |
| [training-apply](skills/learning/training-apply/) | 从已授权学习资料中提取方法并应用到实际问题 | `skills/learning/training-apply` |

### 生产力

| Skill | 说明 | 安装路径 |
| --- | --- | --- |
| [daily-report](skills/productivity/daily-report/) | 规划、记录并汇总每日工作 | `skills/productivity/daily-report` |
| [decision-challenger](skills/productivity/decision-challenger/) | 以反方、支持方和证据裁决审查重要决策 | `skills/productivity/decision-challenger` |
| [knowledge-base](skills/productivity/knowledge-base/) | 查询、整理和复用本地工作知识 | `skills/productivity/knowledge-base` |
| [markitdown-docs](skills/productivity/markitdown-docs/) | 将常见文档转换为便于检索的 Markdown | `skills/productivity/markitdown-docs` |
| [premise-checker](skills/productivity/premise-checker/) | 核对关键前提、事实依据与遗漏变量，修正后继续任务 | `skills/productivity/premise-checker` |
| [task-status](skills/productivity/task-status/) | 概括当前任务状态并记录当天进度 | `skills/productivity/task-status` |

### 项目管理

| Skill | 说明 | 安装路径 |
| --- | --- | --- |
| [handoff](skills/project-management/handoff/) | 生成可供下一会话接手的精简交接文档 | `skills/project-management/handoff` |
| [multi-agent-cowork](skills/project-management/multi-agent-cowork/) | 通过本地任务记录协调跨 Agent 接力 | `skills/project-management/multi-agent-cowork` |
| [project-close](skills/project-management/project-close/) | 创建项目交接或轻量检查点 | `skills/project-management/project-close` |
| [project-init](skills/project-management/project-init/) | 初始化或同步项目连续性文档 | `skills/project-management/project-init` |
| [project-knowledge](skills/project-management/project-knowledge/) | 检索、沉淀并修订当前项目的可复用知识 | `skills/project-management/project-knowledge` |
| [project-lessons](skills/project-management/project-lessons/) | 记录真实错误与修复证据，按需复用经验 | `skills/project-management/project-lessons` |
| [project-refactor](skills/project-management/project-refactor/) | 结构调整后同步项目文档引用 | `skills/project-management/project-refactor` |
| [project-resume](skills/project-management/project-resume/) | 为接手项目生成只读上下文简报 | `skills/project-management/project-resume` |

### 沟通与写作

| Skill | 说明 | 安装路径 |
| --- | --- | --- |
| [ask-coach](skills/communication/ask-coach/) | 将职场沟通意图改写为可直接发送的版本 | `skills/communication/ask-coach` |
| [everyday-mechanisms](skills/writing/everyday-mechanisms/) | 从日常疑问写短故事，解释机制、处境差异与隐性代价 | `skills/writing/everyday-mechanisms` |
| [humanizer](skills/writing/humanizer/) | 减少 AI 写作惯性并保留自然表达 | `skills/writing/humanizer` |

<!-- skill-catalog:end -->

## 安装

使用支持 `gh skill` 的新版 [GitHub CLI](https://cli.github.com/) 将任一 skill 安装到用户范围：

```bash
gh skill install curforever/curforever-skills <技能安装路径> \
  --agent <agent> --scope user
```

将 `<技能安装路径>` 替换为上表中的安装路径，并按所用 Agent 设置 `<agent>`：Codex 使用 `codex`，Claude Code 使用 `claude-code`，Cursor 使用 `cursor`，GitHub Copilot 使用 `github-copilot`。安装后重启对应 Agent。

如果 Codex 尚不支持 `gh skill`，可使用其内置安装器：

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }

python (Join-Path $codexHome "skills\.system\skill-installer\scripts\install-skill-from-github.py") `
  --repo curforever/curforever-skills `
  --path <技能安装路径>
```

## 使用前提

- 只含说明的技能通常不需要额外运行时；脚本技能使用其目录内说明要求的 Python 或 PowerShell。
- `ai-news-local` 生成真实资讯需要联网核实来源。默认仅保存本地 Markdown；HTML 阅读页可选，需要 Python `Markdown` 包。
- `markitdown-docs` 需要当前环境可用的 MarkItDown 及相应格式依赖；不会假定某台设备已安装。
- `impeccable` 的工具流程需要其引擎二进制；首次运行可能下载，具体以包内启动器为准。
- `grill-me`、`grill-with-docs` 使用同组的 `grilling`，后者还需要 `domain-modeling`。同级目录可按相对路径读取；单独安装到不同位置时，应通过平台技能发现机制定位依赖。
- 学习资料、源码、日报目录由本次请求或项目配置确定；相对路径基于已确认的项目根。技能库不包含真实学习材料、工作报告或私人项目配置。

## 隐私与安全

- 安装前请审阅目标 skill 的 `SKILL.md`、脚本和随附参考文件。
- 不要向仓库提交真实材料、学习报告、访问令牌、私钥或本机绝对路径。
- 发布前使用 `skill-manager` 预演，确认目录、README 目录和脱敏检查均通过后再推送。

## 开发与贡献

欢迎通过 [Issues](https://github.com/curforever/curforever-skills/issues) 提出问题、改进建议或新的 skill 想法。提交改动前，请运行随附测试，并确保 README 的目录、描述与安装路径同步更新。

## License

原创内容与工具采用 [MIT License](LICENSE)。第三方技能保留各自许可与署名，详见 [第三方说明](THIRD_PARTY_NOTICES.md)；根许可证不替代这些条款。
