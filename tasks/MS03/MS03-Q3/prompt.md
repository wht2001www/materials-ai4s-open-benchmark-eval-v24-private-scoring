# MS03-Q3｜Matbench 结构尺度与折射率的关联分析

- ID：MS03-Q3
- Domain / sub-domain：materials_science / structure_property_relationship
- Level / time：L2 / 55 分钟
- Task / priority：MS03 / P0
- 大任务：材料实验数据处理、性能表征与结构—性能关联分析
- 来源方式：Matbench dielectric 官方记录固定子集
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

读取 structure_property.csv，完成缺失/finite 检查，计算 n_sites 与 refractive_index_n、volume_a3 与 refractive_index_n 的 Pearson r 和 Spearman rho；用 bootstrap 1000 次给出 95% CI，并绘制双面板散点图。只报告相关，不作因果推断。

## Deliverables

- association.csv（feature,pearson_r,spearman_rho,ci_low,ci_high,n）
- summary.json
- report.md（不超过 300 字）
- analyze.py（从 workspace 根目录运行）
- run_log.jsonl
- association.png

## Hard gates

- 不得修改 inputs；必须按 input_manifest.json 校验 SHA-256。
- 主表须 UTF-8、固定表头、稳定排序；数值必须 finite，未知值留空并显式标状态。
- analyze.py 必须只从公开 inputs 重建主结果，不得读取 private、oracle、gold、answer 或 scoring_spec。
- 报告不得把模型输出或代理指标写成实验事实；所有结论须与主表一致。
- bootstrap 必须固定 seed 并按样本重采样。
- 报告不得把相关性解释为因果。

## DeterministicArtifactScore（0–80）

- 相关系数 30：容差 1e-6
- bootstrap 区间 15：固定 seed oracle 容差
- 数据审计 10：n/缺失/finite
- 科研图 10：双面板与底表一致
- 复现 10：脚本
- 报告 5：克制

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较原始尺度特征与每原子体积特征的相关性稳定性。
