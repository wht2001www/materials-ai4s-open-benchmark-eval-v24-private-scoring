# MS05-Q2｜AlchemyBench 镁离子固态聚合物电解质流程生成

- ID：MS05-Q2
- Domain / sub-domain：materials_science / electrochemistry_and_energy_materials
- Level / time：L3 / 80 分钟
- Task / priority：MS05 / P0
- 大任务：电池与电化学材料性能评估及配方筛选
- 来源方式：AlchemyBench 流程生成任务直接实例
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

生成 solution-casting 合成流程，区分溶解、混合、浇铸、干燥和储存阶段；输出每步的 action/material/equipment/temperature/time/atmosphere。未在输入出现的条件必须为 null/uncertain；最后列出离子电导、热稳定性和电化学窗口所需验证实验，但不得给未经测量的结果。

## Deliverables

- procedure.json
- summary.json
- report.md（不超过 300 字）
- analyze.py（从 workspace 根目录运行）
- run_log.jsonl

## Hard gates

- 不得修改 inputs；必须按 input_manifest.json 校验 SHA-256。
- 主表须 UTF-8、固定表头、稳定排序；数值必须 finite，未知值留空并显式标状态。
- analyze.py 必须只从公开 inputs 重建主结果，不得读取 private、oracle、gold、answer 或 scoring_spec。
- 报告不得把模型输出或代理指标写成实验事实；所有结论须与主表一致。
- 流程阶段顺序明确；验证建议不得伪装成结果。

## DeterministicArtifactScore（0–80）

- 动作覆盖 25：私有 recipe 锚点
- 顺序 15：成对顺序准确率
- 材料/条件实体 20：F1
- 缺参克制 10：虚构数值率
- 复现与格式 5：schema
- 报告 5：验证方案

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较自由生成与结构化 step schema 对顺序和缺参率的影响。
