# MS03-Q1｜SimXRD 模拟衍射谱空间群识别与峰表生成

- ID：MS03-Q1
- Domain / sub-domain：materials_science / characterization_and_spectroscopy
- Level / time：L3 / 100 分钟
- Task / priority：MS03 / P0
- 大任务：材料实验数据处理、性能表征与结构—性能关联分析
- 来源方式：SimXRD 官方示例数据库直接划分
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

用 train_patterns.csv 建立可复现分类流程，预测 test_patterns.csv 的 space_group_number 和 symbol。每个 test sample 另提取局部极大值峰（相对强度>=0.10×样本最大值），输出按 x 升序的峰表；绘制三张测试谱叠加图。不得按 sample_id 猜标签。

## Deliverables

- predictions.csv（sample_id,space_group_number,space_group_symbol）
- summary.json
- report.md（不超过 300 字）
- analyze.py（从 workspace 根目录运行）
- run_log.jsonl
- peaks.csv
- patterns.png

## Hard gates

- 不得修改 inputs；必须按 input_manifest.json 校验 SHA-256。
- 主表须 UTF-8、固定表头、稳定排序；数值必须 finite，未知值留空并显式标状态。
- analyze.py 必须只从公开 inputs 重建主结果，不得读取 private、oracle、gold、answer 或 scoring_spec。
- 报告不得把模型输出或代理指标写成实验事实；所有结论须与主表一致。
- 按 sample_id 分组，不得混合不同谱图。
- 测试标签不得从私有文件或文件顺序推断。

## DeterministicArtifactScore（0–80）

- 空间群准确率 35：3 条 exact match
- 峰位与强度 20：容差 x 1e-6、强度 1e-6
- 科研图 10：轴、图例、单位/变量名与底表一致
- 复现 10：脚本
- 报告 5：方法边界

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较原始强度向量与峰表特征的空间群准确率。
