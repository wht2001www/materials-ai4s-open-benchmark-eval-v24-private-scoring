# Materials AI4S Open Benchmark Evaluation V24

全新独立题库：围绕固定的 MS01–MS10 十个物质科学科研任务，每个任务 3 题，共 30 题。

- 版本：24.0.0
- 公开题目不包含答案或隐藏测试标签。
- 每题均含真实可读取 `inputs/`、完整 `prompt.md`、`input_manifest.json` 和来源清单。
- 来源方式分为官方任务直接实例/固定子集、官方数据固定重划分、透明情境化改编；详情见 `benchmark_attribution.csv`。
- 当前统计：直接任务/实例/固定子集约 17 题；透明改编约 13 题。
- 满分：每题 100 分（DeterministicArtifactScore 80 + JudgeScore 20）。

## 目录

`tasks/MSxx/MSxx-Qy/inputs` 为真实模型输入；`prompt.md` 为完整公开题卡。运行者在题目目录创建 `output/`，不得修改 inputs。

## 上游 Benchmark

Matbench、JARVIS-Leaderboard、MADE、SimXRD、MatSci-NLP、LLM4Mat-Bench、CSPBenchmark、CSPBenchMetrics 与 AlchemyBench/Open Materials Guide。仓库、commit、文件路径和许可见逐题 source_manifest 与根目录 attribution 表。

## 重要边界

本仓库未假设任何 Skill/MCP/SCP 的可用性。题目用于评测科研任务完成能力，不对工具调用次数本身加分。MS10 因所列基准不存在独立 EHS 金标，明确采用真实合成文本 + 公开规则的情境化改编。
