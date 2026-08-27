# RQ2 Power Iteration 三次运行评估报告

状态：扩展 pilot、人工裁决前报告。本文件汇总 run-01、run-02 和 run-03；原有单次运行报告与原始 judgement 均保留不变。

评估日期：2026 年 8 月 26 日  
协议：RQ2-EVAL-v1  
主题：Power Iteration

## 核心结论

原先的 RQ2 结果确实不足，最直接的问题是每个 profile-condition cell 只有一次 lesson generation。现在已补齐 run-02 和 run-03，在 lesson generation 层面达到三次运行：共 21 份 lesson、27 个 profile-relative blind samples、54 份独立上下文 judgement 和 54 份 `valid=true` 的 score report。

扩展后的结论仍然只是 pilot 证据：

- H2a 相对 P0 得到部分支持。合并三次运行后，P2 在 disciplinary framing 的 P2-P0 配对差中位数为 +1.0，在 sequence quality 上为 +0.5；prerequisite match 和 context-boundary awareness 的中位数差为 0。
- H2a 相对强控制 P1 不支持。P2-P1 在四个主要维度上的配对差中位数全部为 0；framing 为 1 胜、6 平、2 负，sequence 为 1 胜、8 平、0 负，另外两个维度全部平局。P1/P2 仍有明显 ceiling effect。
- H2b 的既有结论保持：三个 profile 的 P2 pathway 在 selection/order/grouping/bridge/depth 上存在经过验证、由 profile rationale 支持的 material differences。但是 run-02/run-03 复用了已审查并 materialize 的最终 pathway，因此新增的是独立 lesson composition，不是两次独立 pathway planning replication。
- H2c 不满足。要求两次 evaluator pass 都通过时，P0 为 9/9，P1 为 8/9，P2 仅为 4/9。P2 的高教学评分不能抵消 conjunctive safety gate 失败。

因此，补样强化了一个稳定的描述性发现：profile-aware P1/P2 都优于通用 P0 的部分教学表现，但 dependency-aware P2 尚未显示出优于 P1 的 rubric 增益，而且当前 P2 composition 更容易暴露公式、边界条件或 authority 外扩展问题。

## 样本与生成审计

每次运行包含 1 份共享 P0、3 份 P1 和 3 份 P2，共 7 份 lesson。三次运行合计：

| 条件 | 实际独立生成 lesson | Profile-relative blind samples | 每个 sample 的 evaluator passes |
|---|---:|---:|---:|
| P0 | 3 | 9 | 2 |
| P1 | 9 | 9 | 2 |
| P2 | 9 | 9 | 2 |
| 合计 | 21 | 27 | 54 judgements |

P0 每次只生成一次并在三个 profile 下重复评估，因此 9 个 P0 blind samples 不能解释为 9 份独立 lesson。所有 21 个 `lesson.md` 的 SHA-256 均不同。21 份 Composer validation report 全部为 `valid=true`、0 errors、0 warnings；英文正文均在 1,500–2,000 词范围内，所要求的 Python execution validation 也全部通过。

生成环境没有完全冻结：run-01 的 manifest 记录为 GitHub Copilot / GPT-5.6 Luna / VS Code Copilot Chat，run-02 和 run-03 为 OpenAI / gpt-5.6-sol / codex-exec-ephemeral。评审环境也从 run-01 的 `codex-default` 改为 run-02/run-03 的 `gpt-5.6-sol`。因此三次运行可以扩展 pilot，但不能作为满足“same model family and generation settings”的严格 confirmatory replication。

## 逐次运行结果

四个主要维度依次为 disciplinary framing、prerequisite match、context-boundary awareness 和 sequence quality。每个样本先对两次 judge 评分取中位数，再进行 profile-matched comparison。

| Run | H2c P0 | H2c P1 | H2c P2 | P2-P1 配对差中位数 | P2-P0 配对差中位数 |
|---|---:|---:|---:|---|---|
| run-01 | 3/3 | 2/3 | 2/3 | (0, 0, 0, 0) | (+1.0, 0, 0, +0.5) |
| run-02 | 3/3 | 3/3 | 1/3 | (0, 0, 0, 0) | (+1.0, 0, 0, +1.0) |
| run-03 | 3/3 | 3/3 | 1/3 | (0, 0, 0, 0) | (+1.0, +0.5, 0, 0) |

三次运行中，P2-P1 的四项中位数差始终为 0。P2-P0 的 framing 改善在三次运行中方向一致；sequence 改善在 run-01/run-02 更明显，run-03 的 prerequisite match 则出现 +0.5。

## 合并 H2a 结果

| 主要指标 | P0 中位数 | P1 中位数 | P2 中位数 | P2-P1 配对差中位数 | P2-P0 配对差中位数 |
|---|---:|---:|---:|---:|---:|
| Disciplinary framing appropriateness | 4.0 | 5.0 | 5.0 | 0.0 | +1.0 |
| Prerequisite match | 5.0 | 5.0 | 5.0 | 0.0 | 0.0 |
| Context-boundary awareness | 5.0 | 5.0 | 5.0 | 0.0 | 0.0 |
| Sequence quality | 4.5 | 5.0 | 5.0 | 0.0 | +0.5 |

P2-P1 的 framing 描述性 mean paired difference 为 -0.056，sequence 为 +0.056，另外两项为 0；这些效应接近零，且当前只有一个 topic，不作显著性或 portability 声明。example authenticity 继续作为 exploratory outcome，不用于接受 H2a。

## H2b：结构差异的解释边界

既有 confirmed report 仍表明 P2 的三个跨 profile comparison 均为 material difference：

| P2 profile pair | Selection distance | Normalized order distance | Grouping distance | Bridge distance |
|---|---:|---:|---:|---:|
| Applied mathematics vs computer science | 0.0556 | 0.6667 | 0.3000 | 1.0000 |
| Applied mathematics vs mechanical engineering | 0.0556 | 0.6667 | 1.0000 | 1.0000 |
| Computer science vs mechanical engineering | 0.0000 | 0.1176 | 1.0000 | 0.0000 |

这些差异不是简单换词，并且由 hash-bound review/materialization authority 支持。但三次 lesson run 使用相同的最终 pathway 文件，所以 H2b 是同一组已确认结构经过三次 composition 的结果，不是三组独立 Planner 输出。

## H2c：失败样本

双 pass safety gate 的合并结果为：P0 9/9、P1 8/9、P2 4/9。

需要人工裁决的 gate failures：

1. P1 computer science run-01（S-C08S）：一个 evaluator 认为正的非整数 `max_iterations` 未被显式拒绝，RC-017 仅部分满足。
2. P2 computer science run-01（S-H65S）：两次 evaluator 都发现 Frozen Contract/released bridge authority 之外的 complexity/reproducibility 断言。
3. P2 applied mathematics run-02（S-M52V）和 run-03（S-Z82P）：两次 evaluator 都发现 FM-005 中缺失反斜杠、渲染为 literal `qquad` 的轻微公式错误，formula accuracy 为 15/16。
4. P2 mechanical engineering run-02（S-P63H）：两次 evaluator 都认为正的非整数 `max_iterations` 没有得到 Contract 所要求的清晰 `ValueError`。
5. P2 mechanical engineering run-03（S-D94H）：一个 evaluator 将“应用 A 保持 eigenvector eigendirection”的无条件表述判为未排除 λ=0 的数学例外；另一 evaluator 未判为错误，因此必须保留分歧并人工裁决。

另外，一些 H2c 通过的样本因 bounded、`not_verifiable` 的学科应用类比而被建议进行 discipline-authenticity adjudication。这与数学/算法 safety gate 分开，不能把自动 evaluator 的类比可信度判断当作领域专家事实。

## Evaluator reliability

| 指标 | Exact agreement | Mean absolute difference | 差值至少为 2 | Ordinal Krippendorff alpha |
|---|---:|---:|---:|---:|
| Disciplinary framing appropriateness | 0.815 | 0.185 | 0 | 0.678 |
| Prerequisite match | 0.778 | 0.222 | 0 | -0.104 |
| Context-boundary awareness | 1.000 | 0.000 | 0 | 1.000 |
| Sequence quality | 0.815 | 0.185 | 0 | 0.681 |

没有任何主要维度出现相差 2 分或以上。prerequisite match 的 exact agreement 已提高，但由于评分几乎全部集中在 4–5 分，ordinal alpha 仍为负；context-boundary 的完美一致性同样受到全体 5 分的 ceiling saturation 影响。两次 pass 是自动 evaluator 的重复测量，不是两位独立人类专家。

## RQ2 判定

| 组成部分 | 三次运行后的判定 |
|---|---|
| H2a：P2 具有更高教学评分 | 相对 P0 部分支持；相对 P1 不支持 |
| H2b：P2 生成 materially different、profile-linked pathways | 既有结构证据支持；run-02/run-03 没有独立重跑 Planner，因此未增加 planning replication |
| H2c：每条所选 pathway 保持 correctness、provenance 和 dependency coherence | 不满足；P2 仅 4/9 双 pass 通过 |
| 总体 RQ2 | 支持 pathway adaptation 的可行性和相对 P0 的部分描述性收益；尚不支持 P2 优于 P1，也不支持统一安全性 |

## 下一步

1. 人工裁决全部 gate failures 和 bounded disciplinary claims，保留两轮原始 judgement。
2. 在 confirmatory run 前冻结同一 generation/evaluator model family、prompt、budget 和输出设置。
3. 如果研究主张需要独立 pathway replication，必须为每个 P2 cell 独立重跑 Planner，而不只是复用 pathway 后重跑 Composer。
4. 调整 prerequisite-match 和 context-boundary anchors，降低 4–5 分 ceiling saturation。
5. 按同样设计完成 Gradient Descent，并在多 topic、适当嵌套不确定性模型下再讨论 portability。
6. 没有学生实验或独立学科专家审查前，不声称 learner comprehension、learning gain 或真实专业实践有效性。

## 主要证据文件

- `aggregate-results-run-01-03.json`：三次运行合并后的条件汇总与配对比较；
- `aggregate-results.json`、`aggregate-results-run-02.json`、`aggregate-results-run-03.json`：逐次运行汇总；
- `reliability-report-run-01-03.json`：54 份原始 judgement 的总体一致性；
- `reliability-report.json`、`reliability-report-run-02.json`、`reliability-report-run-03.json`：逐次运行一致性；
- `pathway-difference-report-confirmed.json`：现有 P2 跨 profile 结构差异；
- `blind-samples/`、`judge-pass-01/`、`judge-pass-02/`、`private-mappings/`：可审计的 pointwise evidence。
