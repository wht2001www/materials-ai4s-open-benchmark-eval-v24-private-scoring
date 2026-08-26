# MS06-Q3｜JARVIS 弹性模量物理有效性与脆韧代理筛查

- ID：MS06-Q3
- Domain / sub-domain：materials_science / mechanics_and_fracture
- Level / time：L2 / 50 分钟
- Task / priority：MS06 / P0
- 大任务：材料力学性能验证与断裂失效诊断
- 来源方式：JARVIS bulk/shear 官方测试标签配对
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

先检查 K、G 是否 finite 且>0；不满足者标 invalid_nonpositive_modulus，禁止计算 K/G。对有效行计算 Pugh 比并按 1.75 分为 ductile_proxy/brittle_proxy，按有效状态、K/G 降序、jid 升序输出。

## Deliverables

- elastic_screen.csv（jid,K,G,status,pugh_k_over_g,proxy_class,rank）
- summary.json
- report.md（不超过 300 字）
- analyze.py（从 workspace 根目录运行）
- run_log.jsonl

## Hard gates

- 不得修改 inputs；必须按 input_manifest.json 校验 SHA-256。
- 主表须 UTF-8、固定表头、稳定排序；数值必须 finite，未知值留空并显式标状态。
- analyze.py 必须只从公开 inputs 重建主结果，不得读取 private、oracle、gold、answer 或 scoring_spec。
- 报告不得把模型输出或代理指标写成实验事实；所有结论须与主表一致。
- 无效模量不得进入比值或排名；不得取绝对值修复。

## DeterministicArtifactScore（0–80）

- 物理有效性 25：逐行 exact
- K/G 与类别 30：有效行容差
- 稳定排名 10：exact
- 复现 10：脚本
- 报告 5：异常解释

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较忽略无效模量与先做物理硬门槛的排名变化。
