# 工作流程

## Plan：准备独立可理解的任务

1. 读取项目约定和相关真实源码，把仅存在于对话中的关键决定写入任务；未确认事实标明。先按用户目标查现有 feature/task，避免重复创建。
2. 用 templates/task.md 写完整计划：目标、背景、范围、步骤/依赖、验收、已知改动和未完成项。范围使用相对执行工作区的具体文件/目录或 glob；不要为了方便默认为整个项目。只读研究可声明必要读取范围。
3. helper init 建立本地记录，feature 创建持续目标，task 从计划文件建立版本 1。元数据记录在 .ai-cowork，不修改项目规范、不设置忽略、不提交。
4. 生成精简接手句；用户要求完整提示词时进入 handoff。准备计划不意味着已启动其他执行者。

## Execute：普通执行或修复接管

1. show 精确任务，读当前 plan、feature context、最近 result/review 和真实文件。确认依赖、版本、实际 cwd、初始改动及用户授权。
2. planned/paused/blocked/changes_requested 可 claim。awaiting_review 只有用户明确要求修复时用 purpose=repair；accepted/completed 不因“继续”而重跑。若还有依赖未交付，先解释依赖。
3. claim 返回新的 run/token，获取工作区咨询锁。真实改动限定在 scope；helper 检测文件漂移不能替代代理检查 diff 和副作用。
4. 在边界内调整实现步骤，无需逐项询问。用户请求及计划约定的验证执行后记录实际命令/结果，不能把未运行写成通过。
5. checkpoint disposition=continue 保存检查点并继续持锁；paused/blocked 保存并释放，为下一位接手留下当前症状、尝试过的方法、已完成项、残留改动及下一步。
6. finish 默认 awaiting_review。只读研究可 completed；代码变更直接 completed 要记录用户省略审查的明确依据。

结果反复不符合验收且没有新进展时，总结失败模式、尝试和现存改动，建议换执行者或由规划者修复，并可生成修复接管提示词；不要无限重试或为了“重来”清空历史。用户仍可选择继续当前执行者。

## 接管与交回：角色可变

“Agent1 规划 → Agent2 执行受阻 → Agent1 修复 → Agent2 继续”是同一个任务的多个 run，不是失败后另造任务。规划者也可一直执行到交付。

优先由原执行者 checkpoint paused/blocked，并确认它已停止写入。新执行者 claim purpose=repair，使用原计划和现存改动继续，不重做已完成步骤。

旧执行者无法配合时：用户提出接管仍不能证明旧进程已停止。先通过可用进程/工具或用户明确停止信息确认；记录停止证据、reason、预期旧 run/version，再 recover。该操作只将旧轮次标为 interrupted、保留证据并释放匹配锁，不自动清理其他任务的锁；之后再 claim 新 run。证据拿不到时报告占用未知，不强抢。

修好局部阻塞后可 checkpoint paused，报告修复内容、检查结果和剩余步骤，并 handoff 给原执行者。原执行者也用新 run 接回，旧 token 永久失效。若任务本身已完成则 finish，避免为交回而重复执行。

允许读取旧失败报告作为背景；不得将其状态冒充本轮结果。用户修改范围/验收时走 revise 创建新计划，运行中的计划不可改。独立审查必须由未承担该次执行的参与者进行；原规划者一旦亲自修改，本轮自查就不再独立。

## Review：验收真实结果

先 show，保存当前 version、plan revision、last run 和 evidence，然后读计划、回执、实际源码/diff及验证证据。必要验证遵循用户授权和计划。

review 提交时携带这些预期值。helper 会短暂取得同一工作区锁并重新核对文件证据；工作区或版本变化时拒绝旧结论。重新检查变化或让执行者补新回执，不能改数字蒙混。

verdict=accepted / changes_requested / insufficient_evidence。后两者记录可执行的问题、位置、触发条件或缺少的检查。self-check 与 independent/human 分开；self-check 想直接 accepted 需明确用户省略独立审查依据。

## Status

仅 list/show 当前任务及必要最近回执，不轮询其他 AI。无绑定且多个候选时让用户选；无任务则说明可开始规划，不自动建任务。stale 表示信息可能过时，不等于失败、终止或可接管。

## Handoff：独立的完整提示词流程

用户说“生成交接提示词”“给我一段发给另一个 Agent 的话”即触发，不要求记模式。可以在规划、执行中断、审查返工、修复后交回等任意阶段使用。

helper handoff 输出具有真实记录/计划路径的底稿；按 templates/handoff.md 整理为一个完整可复制文本块。保留关键原意，不仅输出“去读文件”。包含：接收者要做的事、目标/背景、当前状态/版本、已做和未做、症状/尝试、原始改动、允许范围和依赖、验收/停止条件、记录绝对路径、回执和归属要求。

对象未知时用“接手 Agent”，不假定产品、模型能力或对方拥有本机权限。接收方无本地路径访问时明确需要传递文件，不建议粘贴凭证或完整原始聊天日志。

handoff 生成本身不发送、不 claim/recover、不转换状态。running 时提示先确认暂停/停止；准备好提示词不能证明另一个 Agent 已接收或执行。要求对方接手后核对当前版本，不盲信生成时快照。
