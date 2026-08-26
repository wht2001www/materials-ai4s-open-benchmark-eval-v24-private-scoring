# MS01-Q1｜MADE 热力学稳定候选的硬约束筛选与 Top-k 排序

- ID：MS01-Q1
- Domain / sub-domain：materials_science / materials_discovery
- Level / time：L2 / 45 分钟
- Task / priority：MS01 / P0
- 大任务：目标性能约束下的新材料候选发现与优先级排序
- 来源方式：官方数据固定子集 + 约束筛选改编
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

读取 inputs/candidates.csv 与 constraints.json。逐条解析化学式，先执行全部硬约束；不得先排序后截断。输出每个候选的通过/淘汰状态和逐项理由，再按 constraints.json 的稳定排序规则给出 Top-20。不得把 energy_above_hull 当作 formation_energy_per_atom，也不得用缺失值填 0。

## Deliverables

- screening.csv（material_id,formula,eligible,exclusion_reasons,rank）
- summary.json
- report.md（不超过 300 字）
- analyze.py（从 workspace 根目录运行）
- run_log.jsonl

## Hard gates

- 不得修改 inputs；必须按 input_manifest.json 校验 SHA-256。
- 主表须 UTF-8、固定表头、稳定排序；数值必须 finite，未知值留空并显式标状态。
- analyze.py 必须只从公开 inputs 重建主结果，不得读取 private、oracle、gold、answer 或 scoring_spec。
- 报告不得把模型输出或代理指标写成实验事实；所有结论须与主表一致。
- 禁限元素必须从化学式解析；所有淘汰理由可复算。

## DeterministicArtifactScore（0–80）

- 硬约束判定 40：逐行 exact match
- Top-k 排序 20：顺序 exact match
- 可复现与格式 15：脚本、schema、稳定排序
- 报告 5：结论与边界

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较：仅按单一性质排序 vs 先硬约束、再多字段稳定排序；报告候选集合和排序变化。
