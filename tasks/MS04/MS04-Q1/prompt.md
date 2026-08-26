# MS04-Q1｜CSPBenchMetrics 晶体预测—真值多距离评估

- ID：MS04-Q1
- Domain / sub-domain：materials_science / crystallography_and_structure
- Level / time：L3 / 100 分钟
- Task / priority：MS04 / P0
- 大任务：晶体、MOF与多孔材料结构解析及性质评估
- 来源方式：CSPBenchMetrics 官方示例直接采用
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

对 SrTiO3 和 GdB2 的 predicted/ground-truth CIF 运行 CSPBenchMetrics 可用指标，至少输出 wyckoff_rmse、wyckoff_mae、sinkhorn_dist、chamfer_dist、hausdorff_dist、superpose_rmsd、edit_graph_distance、fingerPrint、XRD_dist、OFM_dist。无法计算的值必须保留 null/status，不得填 0。按材料各写一行并解释不同指标为何可能排序不一致。

## Deliverables

- distances.csv（structure + 指定指标 + status）
- summary.json
- report.md（不超过 300 字）
- analyze.py（从 workspace 根目录运行）
- run_log.jsonl

## Hard gates

- 不得修改 inputs；必须按 input_manifest.json 校验 SHA-256。
- 主表须 UTF-8、固定表头、稳定排序；数值必须 finite，未知值留空并显式标状态。
- analyze.py 必须只从公开 inputs 重建主结果，不得读取 private、oracle、gold、answer 或 scoring_spec。
- 报告不得把模型输出或代理指标写成实验事实；所有结论须与主表一致。
- 不得调换 gt/pred。
- 指标名称、单位/无量纲状态与官方库一致。

## DeterministicArtifactScore（0–80）

- 官方距离复现 55：逐字段容差 1e-4；不可用项按官方状态
- 状态与覆盖 10：字段完整
- 复现 10：脚本/版本
- 报告 5：指标差异

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较单一 RMSD 与多指标联合判断，报告材料排序或结论差异。
