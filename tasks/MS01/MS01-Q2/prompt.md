# MS01-Q2｜JARVIS energy-above-hull 稳定性分级与候选优先级

- ID：MS01-Q2
- Domain / sub-domain：materials_science / materials_informatics
- Level / time：L2 / 40 分钟
- Task / priority：MS01 / P0
- 大任务：目标性能约束下的新材料候选发现与优先级排序
- 来源方式：官方任务记录直接固定子集
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

对 inputs/jarvis_ehull_subset.csv 逐行分级：e_hull<=0.001 为 stable；0.001<e_hull<=0.05 为 near_stable；其余为 metastable。按 e_hull 升序、jid 升序给出全量排名和各类计数。不得改变官方 split。

## Deliverables

- stability_ranking.csv（jid,split,energy_above_hull_ev_atom,stability_class,rank）
- summary.json
- report.md（不超过 300 字）
- analyze.py（从 workspace 根目录运行）
- run_log.jsonl

## Hard gates

- 不得修改 inputs；必须按 input_manifest.json 校验 SHA-256。
- 主表须 UTF-8、固定表头、稳定排序；数值必须 finite，未知值留空并显式标状态。
- analyze.py 必须只从公开 inputs 重建主结果，不得读取 private、oracle、gold、answer 或 scoring_spec。
- 报告不得把模型输出或代理指标写成实验事实；所有结论须与主表一致。
- 阈值边界必须按题意闭区间处理。

## DeterministicArtifactScore（0–80）

- 分级 35：逐行 exact match
- 排名 25：全量顺序 exact match
- 汇总 10：类别和 split 计数
- 复现 5：脚本
- 报告 5：边界解释

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较连续 e_hull 排序与三分类决策；说明阈值离散化损失。
