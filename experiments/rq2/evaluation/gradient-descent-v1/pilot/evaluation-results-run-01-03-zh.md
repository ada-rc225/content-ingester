# RQ2 Gradient Descent 三次运行评估报告

状态：扩展 pilot、人工裁决前报告。本文件汇总 run-01、run-02 和 run-03；原有单次运行报告与原始 judgement 保留不变。

评估日期：2026 年 8 月 26 日  
协议：RQ2-EVAL-v1  
主题：Gradient Descent

## 核心结论

Gradient Descent 已补齐 run-02 和 run-03，并完成三次 lesson-generation run 的盲评校验。现有证据包括 21 份 lesson、27 个 profile-relative blind samples、54 份隔离 evaluator judgement，以及 54 份 `valid=true` 的 score report。

三轮合并结果仍应解释为扩展 pilot：

- H2a 相对 P0 得到部分支持。P2-P0 的 disciplinary framing 配对差中位数为 +1.0，sequence quality 为 +0.5；prerequisite match 和 context-boundary awareness 均为 0。
- H2a 相对强控制 P1 不支持。P2-P1 在四个主要维度上的配对差中位数全部为 0；framing 和 prerequisite 的描述性均值甚至略低于 P1。P1/P2 评分存在明显 ceiling concentration。
- H2b 的结构结论保持支持：P2 的三个 profile pathway 都有经过验证、与 profile rationale 关联的 material differences。但 run-02/run-03 复用了同一组最终 pathway，因此增加的是 lesson composition replication，而不是两次独立 pathway planning replication。
- H2c 未能统一满足。双 pass safety gate 结果为 P0 9/9、P1 9/9、P2 8/9。唯一失败是 run-01 mechanical-engineering P2；run-02 和 run-03 的全部样本都双 pass 通过。

因此，最稳妥的 RQ2 结论是：profile-aware P1/P2 相对通用 P0 改善了部分自动教学指标，P2 能产生真实的结构适配；但当前证据没有表明 P2 的 rubric 表现优于 P1，也不能声称所有 P2 输出都满足 conjunctive safety gate。

## 样本与生成审计

每次运行包含 1 份共享 P0、3 份 P1 和 3 份 P2，共 7 份 lesson。三次运行合计：

| 条件 | 独立生成 lesson | Profile-relative blind samples | Evaluator judgements |
|---|---:|---:|---:|
| P0 | 3 | 9 | 18 |
| P1 | 9 | 9 | 18 |
| P2 | 9 | 9 | 18 |
| 合计 | 21 | 27 | 54 |

P0 每次只生成一次并在三个 profile 下分别评估，因此 9 个 P0 samples 不能解释为 9 份独立 lesson。21 个 `lesson.md` 的 SHA-256 全部不同。全部 21 份 Composer validation report 均为 `valid=true`、0 errors、0 warnings；21 份 code validation 均为 `passed`；英文正文均满足预先规定的 2,200–2,500 词范围。

生成设置没有完全冻结。run-01 manifest 记录为 GitHub Copilot / GPT-5.6 Luna / VS Code agent，run-02 和 run-03 为 OpenAI / gpt-5.6-sol / codex-exec-ephemeral。54 次评审则都记录为 OpenAI / gpt-5.6-sol / RQ2-EVAL-v1。由此，新增结果适合扩展 pilot 和检查稳健性，但不能视作满足相同生成环境要求的严格 confirmatory replication。

## 逐次运行结果

四元组顺序为 disciplinary framing、prerequisite match、context-boundary awareness、sequence quality。每个 profile-condition sample 先对两次 judge 评分取中位数，再做 matched comparison。

| Run | H2c P0 | H2c P1 | H2c P2 | P2-P1 配对差中位数 | P2-P0 配对差中位数 |
|---|---:|---:|---:|---|---|
| run-01 | 3/3 | 3/3 | 2/3 | (0, 0, 0, 0) | (+1.0, 0, 0, +1.0) |
| run-02 | 3/3 | 3/3 | 3/3 | (0, 0, 0, 0) | (+1.0, 0, 0, 0) |
| run-03 | 3/3 | 3/3 | 3/3 | (0, 0, 0, 0) | (+1.5, 0, 0, +0.5) |

P2-P1 的四项配对差中位数在每次运行中都为 0。P2-P0 的 framing 改善在三次运行中方向一致；sequence 的中位改善出现在 run-01 和 run-03，run-02 的该项中位数为 0。

## 合并 H2a 结果

| 主要指标 | P0 中位数 | P1 中位数 | P2 中位数 | P2-P1 配对差中位数 | P2-P0 配对差中位数 |
|---|---:|---:|---:|---:|---:|
| Disciplinary framing appropriateness | 3.5 | 5.0 | 5.0 | 0.0 | +1.0 |
| Prerequisite match | 5.0 | 5.0 | 5.0 | 0.0 | 0.0 |
| Context-boundary awareness | 5.0 | 5.0 | 5.0 | 0.0 | 0.0 |
| Sequence quality | 4.5 | 5.0 | 5.0 | 0.0 | +0.5 |

P2-P1 的 matched win/tie/loss 分别为：framing 1/6/2、prerequisite 0/6/3、boundary 1/7/1、sequence 1/8/0。对应 mean paired differences 为 -0.222、-0.222、0 和 +0.056。P2-P0 的 framing 为 6/3/0，sequence 为 5/4/0；这两项的改善最稳定。当前样本只覆盖一个 topic，不进行显著性或普适性声明。

## H2b：结构差异与重复运行边界

既有 confirmed report 中，三个 P2 跨 profile comparison 均为 material difference：

| P2 profile pair | Selection distance | Normalized order distance | Grouping distance | Bridge distance |
|---|---:|---:|---:|---:|
| Applied mathematics vs computer science | 0.0000 | 0.5000 | 0.0000 | 0.2500 |
| Applied mathematics vs mechanical engineering | 0.0000 | 0.5000 | 0.0000 | 0.0000 |
| Computer science vs mechanical engineering | 0.0000 | 0.0000 | 0.0000 | 0.2500 |

Gradient Descent 的三条 P2 pathway 选择了相同的 12 个 Contract items；material differences 来自 order、released bridges 和 declared depth，而不是 selection。所有 comparison 均绑定有效 pathway、profile rationale 和 approved parent-review/materialization authority，因此不是单纯措辞替换。

不过，三轮 composition 使用的是同一组最终 P0/P1/P2 pathway 文件。由此可以检验“固定 pathway 下 lesson 生成是否重复出现相似结果”，不能检验 Planner 在三次独立生成中是否稳定地产生同样的结构差异。

## H2c：安全门槛

| 条件 | 双 pass 均通过 | 结果 |
|---|---:|---|
| P0 | 9/9 | 全部通过 |
| P1 | 9/9 | 全部通过 |
| P2 | 8/9 | run-01 mechanical engineering 失败 |

54 份 score report 中，required-goal coverage、selected-Contract-item coverage、formula provenance、hard-dependency validation、released-bridge compliance、formula accuracy 和 algorithm accuracy 的最小值均为 1.0；critical error 总数为 0，dependency coherence verdict 全部为 `pass`。

唯一重复 gate failure 是 S-V95J（P2 mechanical engineering run-01）。两次 pass 都认为 lesson 加入了 Frozen Contract 和 released bridge authority 之外的算法或数学诊断建议，包括 finite-difference gradient check；第二次 pass 还标记了 step/acceptance 和梯度诊断建议。所选 gradient-descent 核心、公式和算法本身仍被判为完整正确，但 conjunctive H2c 不允许这种无来源扩展。

部分 H2c 通过样本仍因 bounded、无法由现有 authority 独立核验的学科应用类比而收到 discipline-authenticity adjudication 建议。这类建议不等同于数学/算法 safety failure，也不能替代领域专家审查。

## Evaluator reliability

| 指标 | Exact agreement | Mean absolute difference | 差值至少为 2 | Ordinal Krippendorff alpha |
|---|---:|---:|---:|---:|
| Disciplinary framing appropriateness | 0.852 | 0.148 | 0 | 0.930 |
| Prerequisite match | 0.852 | 0.148 | 0 | 0.264 |
| Context-boundary awareness | 0.926 | 0.074 | 0 | -0.019 |
| Sequence quality | 0.889 | 0.111 | 0 | 0.765 |

四个主要维度都没有出现相差 2 分或以上的 judgement。prerequisite 和 boundary 的 exact agreement 很高，但 alpha 较低或略为负，主要原因是评分高度集中在 4–5 分、边际方差很小；不能把它解释为量表具有很强区分度。两个 pass 是同一自动 evaluator 配置的隔离重复测量，不是两位独立人类专家。

## RQ2 判定

| 组成部分 | 三次运行后的判定 |
|---|---|
| H2a：P2 具有更高教学评分 | 相对 P0 的 framing 与 sequence 部分支持；相对 P1 不支持 |
| H2b：P2 生成 materially different、profile-linked pathways | 既有结构证据支持；新增运行没有独立重跑 Planner |
| H2c：每条所选 pathway 保持 correctness、provenance 和 dependency coherence | 不统一满足；P2 为 8/9 双 pass 通过 |
| 总体 RQ2 | 支持结构适配可行性和相对 P0 的部分描述性收益；尚不支持 P2 优于 P1，也不支持统一安全性 |

## 下一步

1. 人工裁决 S-V95J 以及 bounded disciplinary claims，同时保留两轮原始 judgement。
2. 在 confirmatory run 前冻结 generation model、access route、prompt、budget 和输出设置。
3. 若研究主张包含 planning replication，应为每个 P2 cell 独立重跑 Planner，而不只是复用 pathway 后重跑 Composer。
4. 改进 prerequisite 和 context-boundary 的评分锚点，降低 4–5 分 ceiling saturation。
5. 在多个 topic、领域专家审查或学生实验之前，不声称 learner comprehension、learning gain 或真实专业实践有效性。

## 主要证据文件

- `aggregate-results-run-01-03.json`：三轮合并条件汇总与配对比较；
- `aggregate-results.json`、`aggregate-results-run-02.json`、`aggregate-results-run-03.json`：逐次运行汇总；
- `reliability-report-run-01-03.json`：54 份 judgement 的总体一致性；
- `reliability-report.json`、`reliability-report-run-02.json`、`reliability-report-run-03.json`：逐次运行一致性；
- `pathway-difference-report-confirmed.json`：P2 跨 profile 结构差异；
- `blind-samples/`、`judge-pass-01/`、`judge-pass-02/`、`private-mappings/`：可审计的 pointwise evidence。
