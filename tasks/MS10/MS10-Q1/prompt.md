# MS10-Q1｜AlchemyBench 纳米氧化铈流程危险触发项审查

- ID：MS10-Q1
- Domain / sub-domain：materials_science / chemical_safety_and_environment
- Level / time：L3 / 65 分钟
- Task / priority：MS10 / P1
- 大任务：材料合成与应用过程的化学安全及环境风险审查
- 来源方式：真实 Benchmark 合成文本的透明 EHS 情境化改编
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

读取 procedure.txt 与 hazard_rules.json，按规则抽取化学品/材料、温度、时间、气氛、密闭/加压和后处理证据，并触发 rule code。每个 flag 必须给原文字符 offset 与 evidence_text；按规则计算 severity。另列出规则无法覆盖、必须由 SDS/EHS 人工确认的事项。不得把关键词命中写成法规结论。

## Deliverables

- safety_audit.json（entities,conditions,flags,severity,manual_review_items）
- summary.json
- report.md（不超过 300 字）
- analyze.py（从 workspace 根目录运行）
- run_log.jsonl

## Hard gates

- 不得修改 inputs；必须按 input_manifest.json 校验 SHA-256。
- 主表须 UTF-8、固定表头、稳定排序；数值必须 finite，未知值留空并显式标状态。
- analyze.py 必须只从公开 inputs 重建主结果，不得读取 private、oracle、gold、answer 或 scoring_spec。
- 报告不得把模型输出或代理指标写成实验事实；所有结论须与主表一致。
- 每个 flag 必须有可验证 offset；无证据不得触发。
- severity 只按公开规则计算，不得凭主观改级。

## DeterministicArtifactScore（0–80）

- 规则触发 35：flag code exact
- 证据 offset 20：exact/overlap
- severity 10：规则 exact
- 实体与条件覆盖 10：锚点
- 报告 5：规则边界

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较纯关键词命中与加入 offset、条件数值和上下文去重后的误报变化。
