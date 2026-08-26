# MS02-Q2｜AlchemyBench MIL-100(Fe) 功能化合成流程生成

- ID：MS02-Q2
- Domain / sub-domain：materials_science / synthesis_planning
- Level / time：L3 / 75 分钟
- Task / priority：MS02 / P0
- 大任务：材料合成路线设计、配方计算与实验条件规划
- 来源方式：AlchemyBench 流程生成任务直接实例
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

依据 inputs/case.json 生成有序实验流程。每步需包含 action、materials、equipment、temperature、time、atmosphere、workup 和 evidence_status；输入未给出的数值不得伪造，应写 null/uncertain。另给出可执行性检查表与缺失参数清单。

## Deliverables

- procedure.json（case_id,steps[],missing_parameters[]）
- summary.json
- report.md（不超过 300 字）
- analyze.py（从 workspace 根目录运行）
- run_log.jsonl

## Hard gates

- 不得修改 inputs；必须按 input_manifest.json 校验 SHA-256。
- 主表须 UTF-8、固定表头、稳定排序；数值必须 finite，未知值留空并显式标状态。
- analyze.py 必须只从公开 inputs 重建主结果，不得读取 private、oracle、gold、answer 或 scoring_spec。
- 报告不得把模型输出或代理指标写成实验事实；所有结论须与主表一致。
- 步骤顺序明确；任何精确条件须能在输入中定位。
- 预测内容必须与输入事实分层。

## DeterministicArtifactScore（0–80）

- 关键步骤覆盖 30：与私有 recipe 的动作锚点比较
- 顺序一致性 15：成对顺序准确率
- 材料/设备覆盖 15：实体 F1
- 缺参克制 10：未给数值不伪造
- 复现与格式 5：schema
- 报告 5：风险和边界

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较无摘要与含摘要条件下的动作覆盖和虚构数值率。
