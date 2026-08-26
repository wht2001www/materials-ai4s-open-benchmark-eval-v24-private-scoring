# MS09-Q3｜Matbench 声子峰结构规模分布外泛化

- ID：MS09-Q3
- Domain / sub-domain：materials_science / thermal_properties_ood
- Level / time：L3 / 100 分钟
- Task / priority：MS09 / P1
- 大任务：热管理材料传热性能与服役边界评估
- 来源方式：Matbench 数据 + Structure-OOD 思路的透明改编
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

只用 train.csv 训练模型，预测 ood_test.csv。严格遵守 split_definition.json，不得把 OOD test 混入调参或标准化拟合。报告训练 5 折 MAE 与 OOD hidden MAE，并按 n_sites 分箱绘制绝对误差（评分环境补入 hidden 标签计算）。

## Deliverables

- predictions.csv（sample_id,last_phdos_peak_cm1）
- summary.json
- report.md（不超过 300 字）
- analyze.py（从 workspace 根目录运行）
- run_log.jsonl
- cv_metrics.json
- ood_protocol.json

## Hard gates

- 不得修改 inputs；必须按 input_manifest.json 校验 SHA-256。
- 主表须 UTF-8、固定表头、稳定排序；数值必须 finite，未知值留空并显式标状态。
- analyze.py 必须只从公开 inputs 重建主结果，不得读取 private、oracle、gold、answer 或 scoring_spec。
- 报告不得把模型输出或代理指标写成实验事实；所有结论须与主表一致。
- 所有预处理仅 fit 于 train。
- 180 个 OOD ID 全覆盖；不得重划分。

## DeterministicArtifactScore（0–80）

- OOD hidden MAE 35：私有标签
- 覆盖/finite 10：exact
- OOD 协议 15：无测试泄漏
- 训练 CV 10：可复核
- 复现 5：脚本
- 报告 5：分布偏移

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较随机切分 CV 与结构规模 OOD 的 MAE，量化乐观偏差。
