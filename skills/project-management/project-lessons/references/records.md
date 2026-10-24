# 经验主记录与工具

`scripts/lessons.py` 仅依赖 Python 3 标准库。始终用 Skill 所在绝对路径调用，并显式传 `--project`；不要假设安装在某个固定用户名下。下文 `<skill>`、`<project>` 是需替换的路径。

## 文件约定

```text
knowledge/project-lessons/
  INDEX.md                # 工具生成的检索索引
  records/<lesson-id>.json # 主数据，长期保存
  notes/<lesson-id>.md     # 工具生成的可读经验
```

工具生成的 Markdown 不手改，通过 upsert 修改主记录后重建。工具不修改 AGENTS、全局配置、项目知识总索引。首次写入后，Agent 向 `knowledge/INDEX.md` 最小追加子索引链接；按该项目既有格式登记来源、日期、状态、复核条件。

## 新增或更新

Agent 先根据真实证据准备输入 JSON（脱敏，放项目已有临时目录或系统临时目录，不把工具自测样例放入真实经验）：

```json
{
  "id": "timeout-empty-state",
  "title": "请求超时被误判为空数据",
  "categories": ["code"],
  "keywords": ["timeout", "空列表", "异常处理"],
  "scope": "当前项目的列表请求层；版本和调用接口须核对",
  "root_cause": "捕获超时后返回空列表，使调用方无法区分失败与正常空结果",
  "prevention": "修改请求封装时保留失败与正常空结果的区别",
  "solution": "沿用现有失败通道传递超时，调用方按失败状态呈现；核对其他调用方兼容性",
  "adaptation": "不同请求库的超时类型、失败协议和页面状态需分别适配",
  "verification": {
    "status": "unverified",
    "evidence": [],
    "next_check": "建议：模拟超时和正常空数据，分别检查失败态与空态；尚未执行"
  },
  "validity": "active",
  "updated_at": "2026-10-22",
  "review_trigger": "请求库、失败协议或页面状态模型变化",
  "events": [{
    "occurrence_id": "task-42-list-timeout-01",
    "date": "2026-10-22",
    "state": "confirmed",
    "basis": "direct_evidence",
    "summary": "真实输入、现象和错误判定依据；此处为格式示例，不是真实事件",
    "source_refs": ["task-42:tool-result-7:timeout-response"]
  }]
}
```

- `id`：稳定英文小写短名，允许数字/连字符；不要每次复盘重命名。
- `events`：每个事件一条；`state` 为 `confirmed` / `pending` / `retracted`。只有 confirmed 计数。
- `basis`：confirmed 仅允许 `user_correction` / `direct_evidence`；pending 可为 `uncertain`。`source_refs` 应标识具体会话消息、任务日志段落或执行回执，不能仅写“之前遇到过”。
- `occurrence_id`：优先复用既有 ID，不用本次复盘的时间或文件名制造新事件。同条经验中来源锚点交叉时工具会合并；语义上是否同一事件仍由 Agent 核对。
- `verification.status`：`unverified` / `partial` / `verified`；partial/verified 必须有非空 evidence。写明核验层级和证据，工具不能证明证据内容真实。
- `validity`：`active` / `needs-review` / `retired`；后两者仍保存真实历史，不重置次数。`review_trigger` 说明什么变化需要复核。
- `updated_at`：按用户当前日期/时区填写实际复核日期，不依赖执行主机时区。修改修法、根因或适用范围时须显式提供新的 verification，不继承旧方案的验证结论。
- 可选 `rule_candidate`：文本草案、适用范围、例外、检查方案和确认状态。此字段永远只是记录，不会使工具改写规则文件。

调用：

```text
python3 <skill>/scripts/lessons.py upsert --project <project> --input <input.json>
python3 <skill>/scripts/lessons.py search --project <project> --query "超时"
python3 <skill>/scripts/lessons.py show --project <project> --id timeout-empty-state
python3 <skill>/scripts/lessons.py check --project <project>
python3 <skill>/scripts/lessons.py rebuild --project <project>
```

`upsert` 允许部分更新：已有事件保留，提供的同 ID 事件合并来源并更新字段；其他未提供字段保留。同一次调用重复执行不会增加次数，内容无变化不重写。纠正事件时传原 occurrence_id 与 pending/retracted 状态，历史证据仍保留。

`search` 按标题、关键词、根因、范围、症状摘要匹配，默认排除 retired，用 `--include-retired` 查看历史。只读命令在无记录时返回空结果，不建目录。

`rebuild` 仅在主数据与视图不一致时使用；`check` 会检查格式、重复事件来源、视图一致性与索引。工具并发写入会明确拒绝，不自动删除其他会话的锁；写入失败后保留主记录并按回执恢复，不盲目重试真实外部动作。

## 人工判断边界

工具只保证结构和可计算的约束，不判断根因是否相同、用户是否真的纠正、日志是否足够、方案是否适用。不能把结构校验成功当作修法验证，也不能用合成测试增加真实次数。
