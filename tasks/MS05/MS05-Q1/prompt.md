# MS05-Q1｜AlchemyBench 锂富层状正极原料预测

- ID：MS05-Q1
- Domain / sub-domain：materials_science / electrochemistry_and_energy_materials
- Level / time：L3 / 65 分钟
- Task / priority：MS05 / P0
- 大任务：电池与电化学材料性能评估及配方筛选
- 来源方式：AlchemyBench 原料预测任务直接实例
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

预测制备 SiO2-coated Li-rich layered oxide 所需原料，并把主体正极前驱体、锂源、包覆源、溶剂/分散介质和后处理辅助剂分栏。给出 normalized_name、role、confidence、evidence_status；输入不支持的化学计量不得虚构。

## Deliverables

- raw_materials.json
- summary.json
- report.md（不超过 300 字）
- analyze.py（从 workspace 根目录运行）
- run_log.jsonl

## Hard gates

- 不得修改 inputs；必须按 input_manifest.json 校验 SHA-256。
- 主表须 UTF-8、固定表头、稳定排序；数值必须 finite，未知值留空并显式标状态。
- analyze.py 必须只从公开 inputs 重建主结果，不得读取 private、oracle、gold、answer 或 scoring_spec。
- 报告不得把模型输出或代理指标写成实验事实；所有结论须与主表一致。
- 主体与包覆步骤的原料角色不得混淆。

## DeterministicArtifactScore（0–80）

- 原料实体 F1 40：私有 recipe
- 角色 F1 15：主体/包覆/辅助
- 步骤归属 10：阶段分类
- 克制与格式 10：不编造数值
- 报告 5：电化学验证边界

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较只给材料名与加入摘要/工艺类型后的原料召回率。
