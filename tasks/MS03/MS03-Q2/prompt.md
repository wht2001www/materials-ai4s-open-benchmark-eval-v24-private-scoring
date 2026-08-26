# MS03-Q2｜MatSci-NLP 合成操作词序列标注

- ID：MS03-Q2
- Domain / sub-domain：materials_science / experimental_data_processing
- Level / time：L3 / 80 分钟
- Task / priority：MS03 / P0
- 大任务：材料实验数据处理、性能表征与结构—性能关联分析
- 来源方式：MatSci-NLP synthesis action 原任务固定重划分
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

按 sentence_id/token_id 训练并预测合成操作标签。输出 test 的每个 token，标签集合只能取训练集中出现的值与 O。不得重新分词、合并标点或改变 token 顺序；报告 macro-F1 和稀有类别误差。

## Deliverables

- token_predictions.csv（sentence_id,token_id,token,tag）
- summary.json
- report.md（不超过 300 字）
- analyze.py（从 workspace 根目录运行）
- run_log.jsonl
- cv_metrics.json

## Hard gates

- 不得修改 inputs；必须按 input_manifest.json 校验 SHA-256。
- 主表须 UTF-8、固定表头、稳定排序；数值必须 finite，未知值留空并显式标状态。
- analyze.py 必须只从公开 inputs 重建主结果，不得读取 private、oracle、gold、answer 或 scoring_spec。
- 报告不得把模型输出或代理指标写成实验事实；所有结论须与主表一致。
- test token 集合与顺序必须 100% 覆盖。
- 不得重新分词。

## DeterministicArtifactScore（0–80）

- token macro-F1 35：私有官方标签
- 非 O micro-F1 20：私有官方标签
- 覆盖与对齐 10：ID/token exact
- 验证协议 10：按 sentence 分组、无泄漏
- 报告 5：类别误差

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较词典/规则基线与上下文序列模型的非 O F1。
