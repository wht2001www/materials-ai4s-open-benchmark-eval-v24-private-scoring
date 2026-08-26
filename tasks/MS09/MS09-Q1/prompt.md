# MS09-Q1｜Matbench 声子态密度末峰位置回归

- ID：MS09-Q1
- Domain / sub-domain：materials_science / thermal_properties
- Level / time：L3 / 90 分钟
- Task / priority：MS09 / P1
- 大任务：热管理材料传热性能与服役边界评估
- 来源方式：Matbench phonons 原任务固定重划分
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

训练结构摘要到 last_phdos_peak_cm1 的回归模型，输出 test 预测与 5 折 MAE/RMSE。公式解析失败的样本必须保留并显式处理；不得把末峰位置直接解释为热导率。

## Deliverables

- predictions.csv（sample_id,last_phdos_peak_cm1）
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
- 200 个 ID 全覆盖；预测 finite 且>=0。
- 不把声子峰等同于热导率。

## DeterministicArtifactScore（0–80）

- 隐藏 MAE 30：私有标签
- 隐藏 R² 15：私有标签
- 覆盖/物理范围 10：exact
- CV 协议 10：无泄漏
- 复现 10：脚本
- 报告 5：性质边界

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较几何-only 与几何+元素组成特征的 MAE。
