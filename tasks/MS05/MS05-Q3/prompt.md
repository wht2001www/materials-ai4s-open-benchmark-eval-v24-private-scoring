# MS05-Q3｜MatSci-NLP SOFC 材料、工况与性能槽位抽取

- ID：MS05-Q3
- Domain / sub-domain：materials_science / electrochemistry_and_energy_materials
- Level / time：L3 / 90 分钟
- Task / priority：MS05 / P0
- 大任务：电池与电化学材料性能评估及配方筛选
- 来源方式：MatSci-NLP SOFC token/slot 原任务固定切片
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

训练联合序列标注器，为 test 的每个 token 预测 token_label 与 slot_label。不得重新分词；输出 token 级结果，并从预测槽位汇总材料、工作温度、功率密度、电流密度和运行时间实体。

## Deliverables

- token_predictions.csv（sentence_id,token_id,token,token_label,slot_label）
- summary.json
- report.md（不超过 300 字）
- analyze.py（从 workspace 根目录运行）
- run_log.jsonl
- entities.jsonl

## Hard gates

- 不得修改 inputs；必须按 input_manifest.json 校验 SHA-256。
- 主表须 UTF-8、固定表头、稳定排序；数值必须 finite，未知值留空并显式标状态。
- analyze.py 必须只从公开 inputs 重建主结果，不得读取 private、oracle、gold、answer 或 scoring_spec。
- 报告不得把模型输出或代理指标写成实验事实；所有结论须与主表一致。
- token 对齐和覆盖 100%。
- 实体汇总必须可回指 token span。

## DeterministicArtifactScore（0–80）

- token label F1 25：官方 hidden labels
- slot label F1 30：官方 hidden labels
- 实体 span F1 10：从 BIO 还原
- 覆盖与对齐 10：exact
- 报告 5：类别误差

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较独立 token/slot 模型与联合模型的 slot F1。
