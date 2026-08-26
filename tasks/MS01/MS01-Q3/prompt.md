# MS01-Q3｜Matbench 玻璃形成能力成分分类基线

- ID：MS01-Q3
- Domain / sub-domain：materials_science / materials_property_prediction
- Level / time：L3 / 90 分钟
- Task / priority：MS01 / P0
- 大任务：目标性能约束下的新材料候选发现与优先级排序
- 来源方式：官方 Matbench 任务固定重划分
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

使用 inputs/train.csv 训练仅依赖 composition 的可复现二分类基线，预测 test.csv。必须解析元素及其化学计量，不得用 sample_id 泄漏标签。固定随机种子写入脚本；报告 5 折分层交叉验证 balanced accuracy、macro-F1 与不确定性。

## Deliverables

- predictions.csv（sample_id,gfa_probability,gfa_pred）
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
- test 每个 sample_id 恰好一行；概率在 [0,1]。
- 训练不得读取隐藏测试标签。

## DeterministicArtifactScore（0–80）

- 隐藏测试 balanced accuracy 30：私有标签计算
- 隐藏测试 macro-F1 20：私有标签计算
- 概率与覆盖 10：finite、范围与 ID 完整
- 交叉验证协议 10：分层、固定 seed、无泄漏
- 复现 5：隔离运行
- 报告 5：误差边界

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较 composition 字符串词袋与显式元素分数特征；报告 hidden test 分数差。
