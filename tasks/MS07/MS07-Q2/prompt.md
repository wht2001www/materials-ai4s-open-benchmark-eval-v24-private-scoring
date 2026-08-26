# MS07-Q2｜AlchemyBench 生物基聚酯有序合成流程生成

- ID：MS07-Q2
- Domain / sub-domain：materials_science / polymer_science
- Level / time：L3 / 85 分钟
- Task / priority：MS07 / P1
- 大任务：聚合物配方与重复单元结构—性能评估
- 来源方式：AlchemyBench procedure 任务直接实例
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

生成从 curcumin 基二醇与共聚单体/酸衍生物到聚酯的结构化流程；每步列 action、materials、equipment、temperature、time、atmosphere 和 evidence_status，未知条件写 null。

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
- 聚合物宏观性能预测必须标明推断性质，不得伪装成实测。

## DeterministicArtifactScore（0–80）

- 动作覆盖 30：reference recipe
- 步骤顺序 15：pairwise
- 实体/条件 F1 15：reference
- 缺参克制 10：虚构率
- 格式 5：schema
- 报告 5：边界

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较只有标题/目标与加入摘要、工艺类型、材料上下文后的覆盖率和虚构率。
