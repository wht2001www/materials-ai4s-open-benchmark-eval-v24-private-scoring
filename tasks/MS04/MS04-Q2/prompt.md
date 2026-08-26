# MS04-Q2｜CSPBenchmark 预测结构归档的覆盖率与 CIF 完整性审计

- ID：MS04-Q2
- Domain / sub-domain：materials_science / crystal_structure_prediction
- Level / time：L2 / 60 分钟
- Task / priority：MS04 / P0
- 大任务：晶体、MOF与多孔材料结构解析及性质评估
- 来源方式：CSPBenchmark 官方 23 结构预测包直接采用
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

解压 23-predicted-data.zip，按 algorithm × metadata.pretty_formula 审计文件覆盖、文件名化学式、CIF 是否含 data_、cell length/angle、atom_site loop 以及至少一个原子行。输出每个算法/化学式的逐项状态和算法级汇总；不可解析必须计为 invalid，不得静默跳过。

## Deliverables

- cif_audit.csv（algorithm,formula,path,present,parseable,formula_match,issue_codes）
- summary.json
- report.md（不超过 300 字）
- analyze.py（从 workspace 根目录运行）
- run_log.jsonl
- algorithm_summary.csv

## Hard gates

- 不得修改 inputs；必须按 input_manifest.json 校验 SHA-256。
- 主表须 UTF-8、固定表头、稳定排序；数值必须 finite，未知值留空并显式标状态。
- analyze.py 必须只从公开 inputs 重建主结果，不得读取 private、oracle、gold、answer 或 scoring_spec。
- 报告不得把模型输出或代理指标写成实验事实；所有结论须与主表一致。
- 必须审计 2×23 个组合；缺文件也要有行。
- invalid 不得从分母移除。

## DeterministicArtifactScore（0–80）

- 覆盖矩阵 30：46 行 exact
- CIF 质检 25：官方文件逐项规则 oracle
- 算法汇总 15：分母固定 23
- 复现 5：脚本
- 报告 5：错误类型

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较把 invalid 排除与把 invalid 计零的算法级通过率。
