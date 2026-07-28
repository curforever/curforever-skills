# curforever-skills

一组可复用的 Agent Skills，帮助 AI coding agent 用更稳定的流程完成特定任务。

> A growing collection of practical Agent Skills for AI coding agents.

## 快速开始：Read Coach

`read-coach` 帮你判断一篇文章或 Markdown 是否值得读，并通过逐题互动带你学会核心内容；它不会修改原文。

使用支持 `gh skill` 的新版 [GitHub CLI](https://cli.github.com/) 全局安装到 Codex：

```bash
gh skill install curforever/curforever-skills skills/learning/read-coach \
  --agent codex --scope user
```

重启 Codex 后，直接对它说：

```text
用 read-coach 帮我评估并学习这篇文章：<文件路径>
```

## Read Coach 能做什么

- **先判断是否值得读**：从可读性、可学习性、准确与可信度、信息密度、可应用性五个维度给出带依据的评分。
- **用问题带你学**：先建立知识地图，再一次只提出一个关键问题或短阅读任务，并根据回答调整下一步。
- **把学习过程留成一份报告**：原文保持不变；若原目录可写，生成同目录的 `<原文件名>.read-coach.md`。
- **支持中英材料**：关键术语保留原文，默认以中文解释和反馈。

评分是辅助判断，不等同于联网事实核验。

## 安装

以下命令都安装到用户范围（`--scope user`），即对该 agent 的所有项目生效。安装完成后请重启对应 agent。

下方示例使用 `read-coach`；要安装其他 skill，请将命令中的路径替换为 [Skills](#skills) 表中对应的“安装路径”。

### Codex

```bash
gh skill install curforever/curforever-skills skills/learning/read-coach \
  --agent codex --scope user
```

如果你的 Codex 尚不支持 `gh skill`，可使用其内置安装器：

<details>
<summary>Windows PowerShell 备用方式</summary>

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }

python (Join-Path $codexHome "skills\.system\skill-installer\scripts\install-skill-from-github.py") `
  --repo curforever/curforever-skills `
  --path skills/learning/read-coach
```

</details>

### Claude Code

```bash
gh skill install curforever/curforever-skills skills/learning/read-coach \
  --agent claude-code --scope user
```

### Cursor

```bash
gh skill install curforever/curforever-skills skills/learning/read-coach \
  --agent cursor --scope user
```

### GitHub Copilot

```bash
gh skill install curforever/curforever-skills skills/learning/read-coach \
  --agent github-copilot --scope user
```

`gh skill` 目前处于预览阶段；如命令不可用，请升级 GitHub CLI，或使用你的 agent 提供的技能安装方式。

### 安装其他 Skill（以 Codex 为例）

```bash
gh skill install curforever/curforever-skills skills/communication/ask-coach \
  --agent codex --scope user

gh skill install curforever/curforever-skills skills/productivity/daily-report \
  --agent codex --scope user
```

## 使用示例

```text
用 read-coach 帮我评估并学习：
~/notes/distributed-systems.md
```

Read Coach 会按以下顺序推进：

1. 给出 30 秒结论和五维评分；
2. 让你选择速览、重点学习或深度学习；
3. 展示核心知识地图；
4. 通过一次一个问题的互动学习，按回答调整难度；
5. 让你完成总结，并生成单份学习报告。

学习过程中可随时说：`速览`、`跳到第 N 点` 或 `结束并生成总结`。

## 学习报告

对本地文件，Read Coach 默认在原文同目录创建一份报告：

```text
distributed-systems.md
distributed-systems.read-coach.md
```

报告固定包含：

1. 30 秒结论
2. 质量评分与依据
3. 核心知识地图
4. 互动学习记录
5. 应用练习与答案要点
6. 最终掌握总结与下一步

若材料来自粘贴正文，或原目录不可写，Read Coach 会先询问保存位置，或仅在对话中输出相同结构。

## 隐私与安全

- 只读取你指定的材料，绝不自动修改原文。
- 随附脚本只使用 Python 标准库，不调用外部 API，也不建立跨会话学习档案。
- 安装第三方 skill 前，请先审阅其 [SKILL.md](skills/learning/read-coach/SKILL.md) 与 [脚本](skills/learning/read-coach/scripts/read_coach.py)。
- 不要提交真实文章、学习报告、访问令牌或私钥；仓库的 `.gitignore` 已忽略 `*.read-coach.md`。

## Skills

| Skill | 说明 | 安装路径 |
| --- | --- | --- |
| [read-coach](skills/learning/read-coach/) | 评估学习材料，并以自适应问答帮助掌握核心内容 | `skills/learning/read-coach` |
| [ask-coach](skills/communication/ask-coach/) | 将职场沟通意图改写为 2–3 个可直接发送的版本 | `skills/communication/ask-coach` |
| [daily-report](skills/productivity/daily-report/) | 规划、记录并汇总每日工作；支持 `plan`、`log`、`final` 三种模式 | `skills/productivity/daily-report` |

每个 skill 都保持自包含：`SKILL.md` 定义工作流，脚本处理确定性任务，参考文件保存可按需加载的细则。

## 开发与贡献

欢迎通过 [Issues](https://github.com/curforever/curforever-skills/issues) 提出问题、改进建议或新的 skill 想法。提交改动前，请运行该 skill 随附的测试，并避免加入真实材料、凭据或平台专属的隐藏依赖。

## License

本仓库采用 [MIT License](LICENSE)。
