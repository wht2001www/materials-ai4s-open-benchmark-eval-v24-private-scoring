# MS08-Q3｜JARVIS 介电函数谱峰值与谱形比较

- ID：MS08-Q3
- Domain / sub-domain：materials_science / electronic_magnetic_optical_properties
- Level / time：L2 / 55 分钟
- Task / priority：MS08 / P1
- 大任务：半导体与光电材料电子输运及光学响应评估
- 来源方式：JARVIS dielectric_function 官方测试谱固定子集
- Inputs：见 `inputs/` 与 `input_manifest.json`

## Prompt

按 jid 重建介电响应序列，计算 n_points、全局峰 point_id/value、均值、标准差、AUC（point_id 间距=1 的梯形积分），按峰值降序比较；绘制 8 条标准化谱线。不得把 point_id 擅自解释为 eV。

## Deliverables

- spectral_summary.csv（jid,n_points,peak_point_id,peak_value,mean,std,auc,rank）
- summary.json
- report.md（不超过 300 字）
- analyze.py（从 workspace 根目录运行）
- run_log.jsonl
- dielectric_spectra.png

## Hard gates

- 不得修改 inputs；必须按 input_manifest.json 校验 SHA-256。
- 主表须 UTF-8、固定表头、稳定排序；数值必须 finite，未知值留空并显式标状态。
- analyze.py 必须只从公开 inputs 重建主结果，不得读取 private、oracle、gold、answer 或 scoring_spec。
- 报告不得把模型输出或代理指标写成实验事实；所有结论须与主表一致。
- 不得把 point_id 标成真实能量。
- 每个 jid 点序完整。

## DeterministicArtifactScore（0–80）

- 谱统计 40：容差 1e-8
- 峰值与排名 15：exact
- 科研图 10：标准化方式、图例、横轴口径
- 复现 10：脚本
- 报告 5：轴口径边界

## JudgeScore（0–20）

证据 5；方法 5；克制 5；可读性 5。证据与方法须能追溯到输入和上游 Benchmark；不得因使用某个工具本身加分。

## Ablation

比较原始幅值与按各谱最大值归一化后的相似性/排名。
