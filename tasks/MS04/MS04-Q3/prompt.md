# MS04-Q3｜LLM4Mat 晶体 JSON—CIF—性质记录一致性核验

- ID：MS04-Q3
- Domain / sub-domain：materials_science / crystallography_and_structure
- Level / time：L3 / 80 分钟
- Task / priority：MS04 / P0
- 大任务：晶体、MOF与多孔材料结构解析及性质评估
- 来源方式：LLM4Mat-Bench 官方测试记录固定子集
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

逐行解析 structure 与 cif_structure，核对 formula_pretty、站点元素计数、晶胞体积和周期边界；比较 structure.lattice.volume 与记录 volume，给出绝对/相对误差。任何一个表示解析失败都须保留该 material_id 并写 issue_codes。

## Deliverables

- structure_qc.csv（material_id,formula_from_sites,n_sites,structure_volume_a3,record_volume_a3,volume_abs_error,volume_rel_error,cif_parseable,issue_codes）
- summary.json
- report.md（不超过 300 字）
- analyze.py（从 workspace 根目录运行）
- run_log.jsonl

## Hard gates

- 不得修改 inputs；必须按 input_manifest.json 校验 SHA-256。
- 主表须 UTF-8、固定表头、稳定排序；数值必须 finite，未知值留空并显式标状态。
- analyze.py 必须只从公开 inputs 重建主结果，不得读取 private、oracle、gold、answer 或 scoring_spec。
- 报告不得把模型输出或代理指标写成实验事实；所有结论须与主表一致。
- 24 个 material_id 全覆盖。
- 不得用记录 volume 覆盖结构解析值。

## DeterministicArtifactScore（0–80）

- 结构解析 30：n_sites/元素/volume oracle
- 一致性误差 20：容差 1e-6
- CIF 质检 15：parse/status
- 覆盖与复现 10：24 行+脚本
- 报告 5：错误分类

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较仅 formula 文本检查与同时解析 structure/CIF 的问题发现率。
