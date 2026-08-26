# MS08-Q1｜Matbench 实验带隙成分回归

- ID：MS08-Q1
- Domain / sub-domain：materials_science / electronic_magnetic_optical_properties
- Level / time：L3 / 90 分钟
- Task / priority：MS08 / P1
- 大任务：半导体与光电材料电子输运及光学响应评估
- 来源方式：Matbench expt_gap 原任务固定重划分
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

解析化学式并训练成分到实验带隙的回归基线。输出 test 预测，并报告 5 折 MAE、RMSE 和零带隙样本误差；不得把预测值称为 HSE 或器件带隙。

## Deliverables

- predictions.csv（sample_id,gap_expt_ev）
- summary.json
- report.md（不超过 300 字）
- analyze.py（从 workspace 根目录运行）
- run_log.jsonl
- cv_metrics.json
- parity.png

## Hard gates

- 不得修改 inputs；必须按 input_manifest.json 校验 SHA-256。
- 主表须 UTF-8、固定表头、稳定排序；数值必须 finite，未知值留空并显式标状态。
- analyze.py 必须只从公开 inputs 重建主结果，不得读取 private、oracle、gold、answer 或 scoring_spec。
- 报告不得把模型输出或代理指标写成实验事实；所有结论须与主表一致。
- 200 个 test ID 全覆盖；预测 finite 且>=0。
- 不得从 sample_id 泄漏标签。

## DeterministicArtifactScore（0–80）

- 隐藏测试 MAE 30：私有标签
- 隐藏测试 R² 15：私有标签
- 覆盖/物理范围 10：exact
- CV 协议 10：无泄漏
- 科研图 5：训练 OOF
- 复现 5：脚本
- 报告 5：带隙口径

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较纯字符串特征与显式元素分数特征的 MAE。
