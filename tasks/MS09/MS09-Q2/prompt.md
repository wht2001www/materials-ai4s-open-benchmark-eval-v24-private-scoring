# MS09-Q2｜JARVIS 声子热容记录的物理审计与高热容候选排序

- ID：MS09-Q2
- Domain / sub-domain：materials_science / thermal_properties
- Level / time：L2 / 45 分钟
- Task / priority：MS09 / P1
- 大任务：热管理材料传热性能与服役边界评估
- 来源方式：JARVIS ph_heat_capacity 官方测试标签固定子集
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

检查 heat_capacity 是否 finite 且>0；无效行写 invalid_nonpositive_or_missing，不得进入排名。对有效行按 heat_capacity 降序、jid 升序排名，输出 Top-20、分位数和异常清单。不得在输入没有单位时自行补单位。

## Deliverables

- heat_capacity_ranking.csv（jid,heat_capacity,status,rank）
- summary.json
- report.md（不超过 300 字）
- analyze.py（从 workspace 根目录运行）
- run_log.jsonl

## Hard gates

- 不得修改 inputs；必须按 input_manifest.json 校验 SHA-256。
- 主表须 UTF-8、固定表头、稳定排序；数值必须 finite，未知值留空并显式标状态。
- analyze.py 必须只从公开 inputs 重建主结果，不得读取 private、oracle、gold、answer 或 scoring_spec。
- 报告不得把模型输出或代理指标写成实验事实；所有结论须与主表一致。
- 无单位不得擅自补单位；invalid 不进入排名。

## DeterministicArtifactScore（0–80）

- 物理审计 25：exact
- 排名 30：全量/Top20 exact
- 统计汇总 15：分位数容差
- 复现 5：脚本
- 报告 5：单位边界

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较包含无效值的朴素排序与先物理门槛的候选变化。
