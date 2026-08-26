# MS02-Q3｜MatSci-NLP 溶胶—凝胶合成实体、关系与事件抽取

- ID：MS02-Q3
- Domain / sub-domain：materials_science / synthesis_information_extraction
- Level / time：L3 / 90 分钟
- Task / priority：MS02 / P0
- 大任务：材料合成路线设计、配方计算与实验条件规划
- 来源方式：MatSci-NLP structured synthesis 原始实例
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

读取 procedure.txt 与 label_schema.json，按字符 offset 抽取全部实体、二元关系和合成事件。实体必须输出 start,end,text,type；关系引用实体 ID；事件包含 trigger 及 arguments。offset 采用 Python 半开区间 [start,end)，不得自行改写原文。

## Deliverables

- extraction.json（entities,relations,events）
- summary.json
- report.md（不超过 300 字）
- analyze.py（从 workspace 根目录运行）
- run_log.jsonl

## Hard gates

- 不得修改 inputs；必须按 input_manifest.json 校验 SHA-256。
- 主表须 UTF-8、固定表头、稳定排序；数值必须 finite，未知值留空并显式标状态。
- analyze.py 必须只从公开 inputs 重建主结果，不得读取 private、oracle、gold、answer 或 scoring_spec。
- 报告不得把模型输出或代理指标写成实验事实；所有结论须与主表一致。
- 所有 offset 必须精确回指原文；实体 ID 唯一。
- 类型只能来自 label_schema。

## DeterministicArtifactScore（0–80）

- 实体 span/type F1 30：exact span
- 关系 F1 15：端点+类型
- 事件 trigger/argument F1 20：官方标注
- offset 与 schema 10：合法性
- 报告 5：错误分析

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较仅实体抽取与实体—关系—事件联合抽取的级联误差。
