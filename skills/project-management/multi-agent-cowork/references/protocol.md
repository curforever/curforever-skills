# 状态与脚本接口

Python 3 标准库，Windows msvcrt / POSIX flock；元数据位于项目 .ai-cowork，辅助脚本不调用 AI。以 S 指代从 SKILL.md 解析出的 scripts/cowork.py 绝对路径。下列均为实际终端命令，不要求用户记忆。

~~~sh
python3 "$S" --root "/absolute/project" init
python3 "$S" --root "/absolute/project" feature --title "登录优化"
python3 "$S" --root "/absolute/project" task --feature FEATURE_ID --title "修复回退" --goal "保留登录回退语义" --scope 'src/login/**' --acceptance "约定回归通过" --plan "/absolute/plan.md"
python3 "$S" --root "/absolute/project" list
python3 "$S" --root "/absolute/project" show --task "/absolute/task-record"
python3 "$S" --root "/absolute/project" claim --task TASK_ID --actor "Agent2/session-label" --expect-version 1
python3 "$S" --root "/absolute/project" checkpoint --task TASK_ID --token RUN_TOKEN --expect-version VERSION --report "/absolute/checkpoint.md" --disposition blocked
python3 "$S" --root "/absolute/project" claim --task TASK_ID --actor "Agent1/session-label" --purpose repair --expect-version VERSION
python3 "$S" --root "/absolute/project" finish --task TASK_ID --token RUN_TOKEN --expect-version VERSION --report "/absolute/result.md"
python3 "$S" --root "/absolute/project" review --task TASK_ID --actor "Reviewer/session-label" --expect-version VERSION --revision REV --expect-run RUN_ID --expected-evidence HASH --verdict accepted --report "/absolute/review.md"
python3 "$S" --root "/absolute/project" handoff --task TASK_ID --action repair
~~~

init/feature/task 是写操作。feature --id 可以定位已有 feature，不用新建同名任务；任务 ID 跨 feature 唯一。其他命令见各自 --help，失败返回非零且不自动重试。

## 状态转换

| 操作 | 前置 | 结果 |
|---|---|---|
| task / revise | 新任务 / 无运行者且未完成 | planned |
| claim | planned / paused / blocked / changes_requested，依赖已交付 | running，新 run/token |
| claim purpose=repair | 上述状态或 awaiting_review | running，新修复轮次 |
| checkpoint continue | running，token/version匹配 | running，保存检查点并持锁 |
| checkpoint paused/blocked | running，匹配 | paused/blocked，保存并释放 |
| finish | running，匹配 | awaiting_review；只读或明确豁免可 completed |
| review | awaiting_review，版本/run/文件证据匹配 | accepted / changes_requested / awaiting_review（证据不足） |
| recover | 精确旧 run 的锁，旧执行已停止且有证据 | paused，旧轮次 interrupted或保留已有终态 |
| handoff / list / show | 已存在记录 | 不改变状态，不发送消息 |

version 每次状态写入递增，不等于计划 revision。旧 version/token 不能重复提交。重试先 show，不盲目再次写；同一次完成提交重复会明确拒绝，而不是覆盖旧回执。自动重试、跨任务无限修复不在本协议内。

## 数据与工作区身份

project.json 记录项目根；features/<id>/context.md 保存共同背景；tasks/<id>/plans/<revision>.md 不可变；state.json 是当前状态和历史 run/review 的真源；runs/<id>/ 下每个回执独立保存。所有元数据拒绝 symlink，计划内容有 hash。state 内部 token 是本轮归属标识，不是安全凭证，不能把咨询锁当权限沙箱。

actor 是稳定的参与者标识，角色切换时沿用，不通过改名字伪装独立审查。原生会话 ID 是可选的 session 字段；缺失不伪造。第一版保守拒绝任务任一历史执行参与者将审查标为 independent；单独的新审查参与者可以审查，用户明确省略独立审查时可用 self-check 加 waiver。脚本不能证明不同 actor 标签背后一定是不同模型/会话，代理必须如实记录。

执行 workspace 为规范化的 Git worktree 根或已登记非 Git 项目根；子目录调用规范化至相同根。跨记录目录指向同一 workspace 时，共用 workspace/.ai-cowork/workspace.lock。不要同时登记相互嵌套的非 Git 项目；遇到嵌套项目/子模块的范围交叠先显式隔离，不声称脚本能锁住所有外部工具。

基线是 scope 内真实文件/缺失项与 Git HEAD 信息，内容 evidence hash 覆盖 scope 文件列表和内容。脚本跳过自有 .ai-cowork；scope 不是工具访问控制。执行前实际检查预存改动；检查点和恢复重新记录当前基线。读 show 计算当前 evidence，但不将其自动写成已审查结果。

## 并发与异常恢复

元数据事务用 flock 串行化，workspace.lock 用排他创建，存储 task/root/run/token。写回执 → 原子写 state → 释放匹配工作区锁。辅助脚本不常驻，不能用其 PID 的存活判断 AI 是否还在执行。

进程在多文件操作间崩溃可能留下回执或残留锁；遇到不一致失败关闭，不自动删除。recover 要求 expect-run、expect-version、reason、stopped-evidence；只有精确对应任务的锁可释放，保留恢复说明。即使 state 已 paused/awaiting_review，但旧锁未释放，也可以按精确身份恢复；原有终态/回执不被抹掉。没有匹配锁不进行“恢复”。

~~~sh
python3 "$S" --root "/absolute/project" recover --task TASK_ID --expect-version VERSION --expect-run OLD_RUN --reason "用户要求规划者接手修复" --stopped-evidence "已确认原执行会话取消且没有残留写入命令"
~~~

recover 不会杀进程也不能验证自然语言停止证据真实性，代理必须先核对。成功后再 claim；咨询锁与状态不一致的未知占用应人工核对，不能 force-clear。

review 提交取得短期工作区锁，校验期望 task version、plan revision、last run 及 evidence。提交后模型外的文件写入仍可能改变结果，后续操作需重新核对；不会把历史 accepted 当永远有效。
