# MS08-Q2｜LLM4Mat 化学式—晶体描述联合带隙预测

- ID：MS08-Q2
- Domain / sub-domain：materials_science / electronic_magnetic_optical_properties
- Level / time：L3 / 100 分钟
- Task / priority：MS08 / P1
- 大任务：半导体与光电材料电子输运及光学响应评估
- 来源方式：LLM4Mat-Bench 官方 train/test 固定子集
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

分别训练 A=formula_pretty-only 与 B=formula_pretty+description 两个可复现回归器，对 test 输出两列预测。报告训练集固定 5 折 MAE，并解释 description 可能造成的信息泄漏或文本模板偏差；主提交使用 B，但必须保留 A。

## Deliverables

- predictions.csv（material_id,pred_formula_only_ev,pred_formula_description_ev）
- summary.json
- report.md（不超过 300 字）
- analyze.py（从 workspace 根目录运行）
- run_log.jsonl
- cv_metrics.json

## Hard gates

- 不得修改 inputs；必须按 input_manifest.json 校验 SHA-256。
- 主表须 UTF-8、固定表头、稳定排序；数值必须 finite，未知值留空并显式标状态。
- analyze.py 必须只从公开 inputs 重建主结果，不得读取 private、oracle、gold、answer 或 scoring_spec。
- 报告不得把模型输出或代理指标写成实验事实；所有结论须与主表一致。
- 两个模型使用同一 split；test 100 个 ID 全覆盖。
- 不得从其他列或外部数据库取 test 标签。

## DeterministicArtifactScore（0–80）

- B 模型隐藏 MAE 25：私有标签
- A 模型隐藏 MAE 15：私有标签
- A/B 差异与覆盖 10：ID/finite
- 消融协议 15：同划分、特征隔离
- 复现 10：脚本
- 报告 5：泄漏讨论

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

题内强制 formula-only vs formula+description；比较 MAE 与逐样本绝对误差。
