# curforever-skills

一组可复用的 Agent Skills，帮助 AI 编码 Agent 以更稳定、可审阅的流程完成特定任务。

> A growing collection of practical Agent Skills for AI coding agents.

## Skills

### 开发与工程

| Skill | 说明 | 安装路径 |
| --- | --- | --- |
| [brainstorming](skills/development/brainstorming/) | 在创作或实现前梳理需求与设计 | `skills/development/brainstorming` |
| [code-planner](skills/development/code-planner/) | 生成范围清晰、可执行的编码任务提示 | `skills/development/code-planner` |
| [code-reading-coach](skills/development/code-reading-coach/) | 以业务问题驱动的交互式源码学习 | `skills/development/code-reading-coach` |
| [code-reviewer](skills/development/code-reviewer/) | 只读审查代码变更及其测试证据 | `skills/development/code-reviewer` |
| [prompt-architect](skills/development/prompt-architect/) | 按任务意图分析并改进提示词 | `skills/development/prompt-architect` |
| [skill-manager](skills/development/skill-manager/) | 脱敏、规范化并发布本地技能集合 | `skills/development/skill-manager` |

### 学习与知识

| Skill | 说明 | 安装路径 |
| --- | --- | --- |
| [read-coach](skills/learning/read-coach/) | 评估学习材料并通过问答帮助掌握内容 | `skills/learning/read-coach` |

### 生产力

| Skill | 说明 | 安装路径 |
| --- | --- | --- |
| [daily-report](skills/productivity/daily-report/) | 规划、记录并汇总每日工作 | `skills/productivity/daily-report` |
| [knowledge-base](skills/productivity/knowledge-base/) | 查询、整理和复用本地工作知识 | `skills/productivity/knowledge-base` |

### 项目管理

| Skill | 说明 | 安装路径 |
| --- | --- | --- |
| [project-close](skills/project-management/project-close/) | 创建项目交接或轻量检查点 | `skills/project-management/project-close` |
| [project-init](skills/project-management/project-init/) | 初始化或同步项目连续性文档 | `skills/project-management/project-init` |
| [project-refactor](skills/project-management/project-refactor/) | 结构调整后同步项目文档引用 | `skills/project-management/project-refactor` |
| [project-resume](skills/project-management/project-resume/) | 为接手项目生成只读上下文简报 | `skills/project-management/project-resume` |

### 沟通与写作

| Skill | 说明 | 安装路径 |
| --- | --- | --- |
| [ask-coach](skills/communication/ask-coach/) | 将职场沟通意图改写为可直接发送的版本 | `skills/communication/ask-coach` |
| [humanizer](skills/writing/humanizer/) | 减少 AI 写作惯性并保留自然表达 | `skills/writing/humanizer` |

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

## 隐私与安全

- 安装前请审阅目标 skill 的 `SKILL.md`、脚本和随附参考文件。
- 不要向仓库提交真实材料、学习报告、访问令牌、私钥或本机绝对路径。
- 发布前使用 `skill-manager` 预演，确认目录、README 目录和脱敏检查均通过后再推送。

## 开发与贡献

欢迎通过 [Issues](https://github.com/curforever/curforever-skills/issues) 提出问题、改进建议或新的 skill 想法。提交改动前，请运行随附测试，并确保 README 的目录、描述与安装路径同步更新。

## License

本仓库采用 [MIT License](LICENSE)。
