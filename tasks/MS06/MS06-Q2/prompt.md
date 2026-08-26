# MS06-Q2｜Matbench 体积模量—剪切模量还原与 Pugh 代理判定

- ID：MS06-Q2
- Domain / sub-domain：materials_science / mechanics_and_fracture
- Level / time：L2 / 55 分钟
- Task / priority：MS06 / P0
- 大任务：材料力学性能验证与断裂失效诊断
- 来源方式：Matbench K/G 两个官方任务按共同索引配对
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

将 log10_k_vrh、log10_g_vrh 还原为 GPa，计算 K/G。K/G>=1.75 标记 ductile_proxy，否则 brittle_proxy。按 K/G 降序、sample_id 升序排名；报告该阈值只是经验代理，不能替代断裂实验。

## Deliverables

- elastic_summary.csv（sample_id,k_gpa,g_gpa,pugh_k_over_g,class,rank）
- summary.json
- report.md（不超过 300 字）
- analyze.py（从 workspace 根目录运行）
- run_log.jsonl

## Hard gates

- 不得修改 inputs；必须按 input_manifest.json 校验 SHA-256。
- 主表须 UTF-8、固定表头、稳定排序；数值必须 finite，未知值留空并显式标状态。
- analyze.py 必须只从公开 inputs 重建主结果，不得读取 private、oracle、gold、answer 或 scoring_spec。
- 报告不得把模型输出或代理指标写成实验事实；所有结论须与主表一致。
- 必须使用 10 的幂而非自然指数。
- proxy 不得写成真实断裂结论。

## DeterministicArtifactScore（0–80）

- K/G 数值 40：相对容差 1e-6
- 类别 15：exact
- 排名 10：exact
- 复现 10：脚本
- 报告 5：代理边界

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较直接在 log 空间相减与先还原再求比值的数值一致性。
