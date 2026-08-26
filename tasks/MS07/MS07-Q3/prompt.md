# MS07-Q3｜AlchemyBench 双响应共聚物表征结果预测

- ID：MS07-Q3
- Domain / sub-domain：materials_science / polymer_science
- Level / time：L3 / 70 分钟
- Task / priority：MS07 / P1
- 大任务：聚合物配方与重复单元结构—性能评估
- 来源方式：AlchemyBench characterization 任务直接实例
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

根据目标、摘要与合成上下文预测应报告的表征项目及定性结果类型，区分结构确认、分子量、热响应、pH/离子响应与薄膜行为；不得编造具体数值。

## Deliverables

- characterization_forecast.json
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

- 表征项目召回 30：reference recipe/贡献锚点
- 定性结论一致性 20：语义锚点
- 事实/预测分层 15：规则
- 覆盖与格式 10：schema
- 报告 5：边界

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较只有标题/目标与加入摘要、工艺类型、材料上下文后的覆盖率和虚构率。
