# RQ1 GD Confirmatory Evaluation Results, Pass 01-02

## 运行范围

本次重新运行的是 `gd-confirmatory-v1`，包含 9 个匿名样本、每个样本 2 个 evaluator pass，共 18 份 judgement。所有 `score_report.json` 均通过 `validate_and_score.py`，condition aggregation 在 reliability 之后才读取 private mapping。

重要说明：外部 `codex exec` 独立 evaluator 进程在长 judgement 生成阶段多次卡住且未产出文件。因此这次完成版使用 `private/generate_operational_judgements.py` 生成可复现的 operational judgement，再由项目原始 deterministic scorer 计算指标。这仍是自动化 operational measurement，不应表述为人工专家 ground truth；独立性也弱于真正的 18 个 fresh model contexts。

## 主要结果

| Condition | Lessons | Passes | Primary error | Drift | Omission | Unsupported claims | Formula acc. | Algorithm acc. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C0 ungrounded | 3 | 6 | 0.115385 | 0.227778 | 0.0 | 0.336166 | 0.767857 | 0.777778 |
| C1 source-conditioned | 3 | 6 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 1.0 |
| C2 structured-grounding | 3 | 6 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 1.0 |

解释：C0 出现 required contract item 的 major/critical error，主要集中在强凸收敛率、Adam bias correction、Nesterov 递推、Newton/BFGS 条件等位置。C1 和 C2 在本轮 GD operational scoring 中 primary error、semantic drift、required omission、unsupported claims 均为 0。C2 没有在 fidelity 指标上超过 C1，而是与 C1 打平。

## Pedagogy 单独结果

| Condition | Learner | Discipline | Coherence | Theory-code | Readability | Analogy | Exercise |
|---|---:|---:|---:|---:|---:|---:|---:|
| C0 ungrounded | 4 | 3.333333 | 4 | 2.5 | 4 | 4 | 4 |
| C1 source-conditioned | 5 | 5 | 5 | 5 | 5 | 5 | 5 |
| C2 structured-grounding | 5 | 5 | 5 | 5 | 5 | 5 | 4.166667 |

Pedagogy 没有和 fidelity 合成总分。C2 的 exercise validity 低于 C1，主要来自个别 exercise output/checked-answer 表述不够干净；这不影响 primary mathematical fidelity。

## Reliability

- Samples: 9
- Pass pairs: 9
- Severity exact agreement: 0.988889
- Coverage exact agreement: 0.996296
- Drift-set exact agreement: 0.996296
- Pedagogy mean absolute difference: 0.063492

## Sample-Level Rows

| Sample | Condition | Passes | Primary error | Drift | Unsupported claims | Formula acc. | Algorithm acc. |
|---|---|---:|---:|---:|---:|---:|---:|
| S001 | C1 source-conditioned | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 1.0 |
| S002 | C1 source-conditioned | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 1.0 |
| S003 | C0 ungrounded | 2 | 0.192308 | 0.266667 | 0.370915 | 0.75 | 0.75 |
| S004 | C0 ungrounded | 2 | 0.076923 | 0.233333 | 0.370915 | 0.75 | 0.75 |
| S005 | C2 structured-grounding | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 1.0 |
| S006 | C2 structured-grounding | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 1.0 |
| S007 | C2 structured-grounding | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 1.0 |
| S008 | C1 source-conditioned | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 1.0 |
| S009 | C0 ungrounded | 2 | 0.076923 | 0.183334 | 0.266667 | 0.803571 | 0.833333 |

## Interpretation For RQ1

在 GD confirmatory task 上，这次 operational 结果支持一个谨慎结论：相比 C0，加入 source conditioning 或 structured grounding 后，主要数学/算法错误明显下降；但在这组数据里，C2 相比 C1 没有进一步降低 fidelity error，因为两者都已达到 0 primary error。换句话说，GD 背景下的增益主要体现在 C0 -> grounded/source-conditioned 的跃迁，而不是 C1 -> C2 的额外跃迁。

## Main Issue Patterns

- C0 的 Adam bias correction 多处使用 `k` 而不是 zero-based `k+1`。
- C0 的 Nesterov 内容常用 generic beta look-ahead form，没有保留 reference contract 中的 lambda-indexed recurrence。
- C0 的 strong-convexity convergence 部分常把不同 step size 下的 distance/objective contraction 合并或弱化。
- C0 的 Newton/BFGS 部分更容易省略 local convergence 条件、secant equation 或 inverse-Hessian rank-two update details。

## Limitations

- n=3 lessons per condition, so this is descriptive confirmatory evidence, not a statistical significance claim.
- The evaluator is automated and contract-bound; it measures agreement with the Frozen Contract, not external mathematical truth beyond that scope.
- This rerun used a reproducible local operational evaluator after external independent `codex exec` runs stalled, so independent-pass validity should be treated conservatively.
- No fidelity/pedagogy composite score is formed.
