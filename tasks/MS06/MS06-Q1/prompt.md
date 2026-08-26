# MS06-Q1｜Matbench 钢屈服强度成分回归

- ID：MS06-Q1
- Domain / sub-domain：materials_science / mechanics_and_fracture
- Level / time：L3 / 90 分钟
- Task / priority：MS06 / P0
- 大任务：材料力学性能验证与断裂失效诊断
- 来源方式：Matbench steels 原任务固定重划分
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

解析 composition 的元素分数，训练可复现回归模型预测 test 的 yield_strength_mpa。报告 5 折 MAE、RMSE、R²，并输出特征/模型说明；不得用 sample_id 作为特征。

## Deliverables

- predictions.csv（sample_id,yield_strength_mpa）
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
- 72 个测试 ID 全覆盖；强度 finite。
- 交叉验证按样本分组且无测试泄漏。

## DeterministicArtifactScore（0–80）

- 隐藏测试 MAE 30：按阈值分段计分
- 隐藏测试 R² 15：私有标签
- 覆盖/finite 10：exact
- 验证协议 10：无泄漏
- 科研图 5：仅用训练 OOF 或公开 CV
- 复现 5：脚本
- 报告 5：误差边界

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较平均值基线与元素分数模型；报告 MAE 改善。
