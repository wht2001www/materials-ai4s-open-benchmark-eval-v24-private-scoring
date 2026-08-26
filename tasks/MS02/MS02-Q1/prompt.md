# MS02-Q1｜AlchemyBench 纳米氧化铈合成原料预测

- ID：MS02-Q1
- Domain / sub-domain：materials_science / synthesis_planning
- Level / time：L3 / 60 分钟
- Task / priority：MS02 / P0
- 大任务：材料合成路线设计、配方计算与实验条件规划
- 来源方式：AlchemyBench 原料预测任务直接实例
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

根据 inputs/case.json 预测完成目标材料合成所需的原料集合。输出规范化名称、角色（前驱体/沉淀剂/溶剂/洗涤或后处理试剂）、置信度及证据句；不得编造精确用量。若摘要不足以确定某项，标记 uncertain。

## Deliverables

- raw_materials.json（case_id,materials[]）
- summary.json
- report.md（不超过 300 字）
- analyze.py（从 workspace 根目录运行）
- run_log.jsonl

## Hard gates

- 不得修改 inputs；必须按 input_manifest.json 校验 SHA-256。
- 主表须 UTF-8、固定表头、稳定排序；数值必须 finite，未知值留空并显式标状态。
- analyze.py 必须只从公开 inputs 重建主结果，不得读取 private、oracle、gold、answer 或 scoring_spec。
- 报告不得把模型输出或代理指标写成实验事实；所有结论须与主表一致。
- 不得在公开输入之外声称已知精确配比。
- 同义词需规范化并保留原文别名。

## DeterministicArtifactScore（0–80）

- 原料实体 F1 40：与私有 reference recipe 的规范化实体集比较
- 角色 macro-F1 15：私有角色锚点
- 不确定性标注 10：不可判项不得伪造
- 格式与覆盖 10：schema/ID
- 报告 5：依据与限制

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较只给目标名称与加入摘要/工艺类型后的原料实体 F1。
