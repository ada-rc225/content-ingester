# RQ2 Gradient Descent Pilot 评估报告

状态：pilot、人工裁决前报告。本中文文件仅用于研究者辅助审阅；正式使用时应以同目录英文报告为准，并只发布英文版。

评估日期：2026 年 8 月 20 日  
协议：RQ2-EVAL-v1  
主题：Gradient Descent

## 核心结论

Gradient Descent pilot 对 RQ2 提供的是部分支持，而不是 confirmatory 证明。

依赖感知的 P2 planning 生成了与 profile 有依据关联、通过确定性验证且 materially different 的 pathway 结构。相对于 P0，P2 改善了 disciplinary framing 和 sequence quality；但相对于更强的 P1 control，P2 在四个主要教学指标上均没有正的配对差中位数。对于 applied mathematics 和 computer science，P2 与 P1 基本持平；对于 mechanical engineering，P2 在 disciplinary framing 和 prerequisite match 上反而较低。因此，P2 当前最清楚的贡献是 pathway 结构适配，而不是更高的自动教学评分。

所选数学核心表现较强：所有 selected Contract items、learning goals、公式和所选算法均被判断为完整正确，dependency coherence 也全部通过。但安全性并未统一满足。mechanical-engineering P2 在两次 evaluator pass 中均因加入 Frozen Contract 和 released bridge authority 之外的算法或数学诊断建议而未通过 H2c。问题来自无来源扩展，而不是所选 gradient-descent 数学核心本身发生错误。

结合此前 Power Iteration pilot，当前结果说明同一框架可以迁移到两个数学主题，并持续生成 materially different、profile-linked pathways。跨主题来看，P2 相对 P0 改善了 disciplinary framing 和 sequence quality；但 P2 没有在主要指标上超过 P1，也没有让每个输出都通过 conjunctive safety gate。因此，RQ2 可以作为 feasibility 和 structural-adaptation 结论得到支持，但不能声称 P2 的教学质量优于 P1，也不能声称所有输出都保持了完整的 correctness 与 provenance。

## 实验设计与分析样本

| 条件 | 实验作用 |
|---|---|
| P0 | 使用固定 canonical pathway 的一份通用 lesson，并分别针对三个 profile 评估 |
| P1 | 在不改变 P0 selection 和 sequence 的前提下，按 profile 调整措辞和例子 |
| P2 | 按 learner profile 和依赖关系调整顺序、分组、深度，并加入 released prerequisite bridges |

pilot 包含 7 份独立生成的 lesson：1 份 P0、3 份 P1 和 3 份 P2。为了进行 matched analysis，同一份 P0 分别针对三个 profile 评分，因此共建立 9 个 profile-relative blind samples。P0 的三组评分不能解释为三份独立生成结果。

每个匿名样本进行了两次全新、相互隔离的 evaluator pass，共得到 18 份 judgement 和 18 份通过确定性验证的 score report。pointwise judgement 看不到 condition label 和 source path，但可以看到 learner profile，因为 profile fit 是评估结果之一。两次 pass 用于测量自动 judge 稳定性，不是两位独立专家，也不会增加 lesson sample size。

所有 lesson 使用相同的 2,200–2,500 英文正文词数协议：

| 条件/profile | 英文正文词数 | Sections | Selected Contract items | Released bridges | Python blocks |
|---|---:|---:|---:|---:|---:|
| P0，共用 | 2,268 | 6 | 12 | 0 | 2 |
| P1，applied mathematics | 2,203 | 6 | 12 | 0 | 2 |
| P1，computer science | 2,219 | 6 | 12 | 0 | 2 |
| P1，mechanical engineering | 2,253 | 6 | 12 | 0 | 2 |
| P2，applied mathematics | 2,209 | 15 | 12 | 3 | 2 |
| P2，computer science | 2,207 | 7 | 12 | 4 | 2 |
| P2，mechanical engineering | 2,242 | 15 | 12 | 3 | 3 |

代码数量不作为教学质量指标。只有在 Contract 选择了相应 algorithm/code opportunity，或 lesson 新增了算法性断言时，才审核算法和代码安全性。

## H2a：主要教学指标

分析先对每个 profile-condition 样本的两次 pass 取中位数，再汇总三个 matched profiles。四个主要指标保持独立，没有计算 composite score。

| 指标 | P0 中位数 | P1 中位数 | P2 中位数 | P2-P1 配对差中位数 | P2-P0 配对差中位数 |
|---|---:|---:|---:|---:|---:|
| Disciplinary framing appropriateness | 3.0 | 5.0 | 5.0 | 0.0 | +1.0 |
| Prerequisite match | 5.0 | 5.0 | 5.0 | 0.0 | 0.0 |
| Context-boundary awareness | 5.0 | 5.0 | 5.0 | 0.0 | 0.0 |
| Sequence quality | 4.0 | 5.0 | 5.0 | 0.0 | +1.0 |

P2-P1 中，disciplinary framing 和 prerequisite match 都是 0 次胜出、2 次平局、1 次落后，描述性 superiority probability 为 0.333；context-boundary awareness 和 sequence quality 在三个 profile 中全部平局。P2-P0 中，framing 和 sequence 都是 2 次胜出、1 次平局，superiority probability 为 0.833；prerequisite match 为 2 次平局、1 次落后；context-boundary awareness 因达到评分上限而全部平局。

这意味着：

- P2 相对于较弱的通用 P0，最明显改善了 disciplinary framing 和 sequence quality；
- P2 在本次 pilot 中没有超过 profile-aware P1；
- mechanical-engineering P2 拉低了 framing 和 prerequisite match 的描述性均值，虽然三个条件的总体中位数均为 5；
- P1 是较强的 control，因为即使不改变 selection 和 sequence，profile-aware composition 也能获得高分；
- 当前评分存在明显 ceiling concentration，尤其是 context-boundary awareness 和 sequence quality。

example authenticity 继续作为 exploratory outcome，不与主要指标合并。两次 pass 一致得到 P0 = 1、P1 = 3、P2 = 3。这表明 P1/P2 比 P0 更容易识别出学科框架，但不能证明案例代表真实专业实践，更不能证明学生获益。

## H2b：pathway 结构差异

P1 成功发挥了固定路径 control 的作用：三个 profile 之间的 selection、order、grouping、bridge 和 depth distance 全部为 0。

P2 的三个跨 profile comparison 均通过确定性验证、包含 profile-linked rationale，并通过 materialization receipt 的审核权威被 confirmed 为 material difference：

| P2 profile pair | Selection distance | Normalized order distance | Grouping distance | Bridge distance | 结构解释 |
|---|---:|---:|---:|---:|---|
| Applied mathematics vs computer science | 0.0000 | 0.5000 | 0.0000 | 0.2500 | order、released bridges 和 depth 改变 |
| Applied mathematics vs mechanical engineering | 0.0000 | 0.5000 | 0.0000 | 0.0000 | order 和 depth 改变 |
| Computer science vs mechanical engineering | 0.0000 | 0.0000 | 0.0000 | 0.2500 | released bridges 和 depth 改变 |

同一 profile 内，P2 相对于 P1 也发生了结构变化：

| Profile | Selection distance | Normalized order distance | Grouping distance | Bridge distance | Depth changed |
|---|---:|---:|---:|---:|---|
| Applied mathematics | 0.0000 | 0.3333 | 1.0000 | 1.0000 | 否 |
| Computer science | 0.0000 | 0.1667 | 1.0000 | 1.0000 | 是 |
| Mechanical engineering | 0.0000 | 0.1667 | 1.0000 | 1.0000 | 是 |

这些变化不是单纯换词。不过，Gradient Descent 没有实际触发 content selection 的差异：P0、P1、P2 都选择了相同的 12 个 Contract items。该案例的适配证据来自 sequence、grouping、bridge requirements 和 depth。此前 Power Iteration 案例还出现了 selected-item differences，因此两个主题共同覆盖了新版 RQ2 的不同组成部分。

三组最终 P2 comparison 能够 confirmed，是因为每份 `bridge-resolution-receipt.json` 都用 hash 将 materialized pathway 绑定到 approved parent review、released bridge catalog 和 bridge release report。这说明经过审核的 planning decisions 在确定性 bridge materialization 中得到保留；它不表示专家直接审核过最终 lesson 文本。

## H2c：所选内容安全性

| 条件 | 两次 evaluator pass 均通过 H2c 的样本数 |
|---|---:|
| P0 | 3/3 |
| P1 | 3/3 |
| P2 | 2/3 |

在 7 份 lesson 中，每个 selected Contract item、required capability、selected formula 和 selected algorithm 都被判断为完整且正确；formula provenance、结构验证、released-bridge compliance 和 dependency coherence 也全部通过。没有发现 critical mathematical 或 algorithmic error。

唯一重复失败的是 mechanical-engineering P2：

1. 两次 pass 都将 finite-difference gradient check 建议判断为无来源算法扩展；
2. 第二次 pass 还标记了“减小 step 或使用 bounded acceptance procedure”的建议，以及“函数值下降但梯度仍大表示仍有大量工作”的诊断推断；
3. 两次 pass 都另外记录了一项参数尺度的学科情境表述为 not verifiable，但它本身没有触发 H2c。

所选 gradient-descent 数学、公式和算法仍然正确。该样本失败是因为 H2c 是 conjunctive gate，不允许无来源的 mathematical/algorithmic extension。confirmatory 修复应删除这些扩展，或为其建立单独、经过审核的 grounding authority。修复规则必须在重新生成前冻结并一致应用，不能只对观察到的失败样本进行静默修改。

## Evaluator reliability

| 指标 | Exact agreement | Mean absolute difference | 差值至少为 2 的数量 | Ordinal Krippendorff alpha |
|---|---:|---:|---:|---:|
| Disciplinary framing appropriateness | 0.778 | 0.222 | 0 | 0.965 |
| Prerequisite match | 0.889 | 0.111 | 0 | 0.622 |
| Context-boundary awareness | 1.000 | 0.000 | 0 | 1.000 |
| Sequence quality | 1.000 | 0.000 | 0 | 1.000 |

四个主要指标均没有出现 2 分或以上的分歧。整体一致性明显优于 Power Iteration pilot，但 prerequisite-match alpha 仍只达到中等水平；同时，所有指标都受到小样本和 ceiling concentration 的影响。boundary 与 sequence 的完美一致性不能单独证明量表具有足够区分度。

## 跨主题结果：Gradient Descent 与 Power Iteration

跨主题 pooling 仅用于描述，并保留每个 topic 的独立检查。两个主题一共包含 14 份独立生成 lesson、18 个 profile-relative samples 和 36 次 blind judge pass。重复使用的 P0 ratings 和重复 judge 都不是独立 lesson generations。

| 指标 | 跨主题 P2-P1 配对差中位数 | 跨主题 P2-P0 配对差中位数 | 主题方向结果 |
|---|---:|---:|---|
| Disciplinary framing appropriateness | 0.0 | +1.0 | 两个主题的 P2-P0 均为正；P2-P1 均为 0 |
| Prerequisite match | 0.0 | 0.0 | 两个主题的配对差中位数均为 0 |
| Context-boundary awareness | 0.0 | 0.0 | 两个主题的配对差中位数均为 0 |
| Sequence quality | 0.0 | +0.75 | 两个主题的 P2-P0 均为正；P2-P1 均为 0 |

P2-P0 中，framing 和 sequence 在 6 个 matched profile-topic pairs 中均为 4 次胜出、2 次平局，superiority probability 为 0.833。P2-P1 中，四个指标的配对差中位数全部为 0；framing 为 1 胜、4 平、1 负，prerequisite match 为 5 平、1 负，boundary 和 sequence 全部平局。

跨主题 H2c 通过数为 P0 = 6/6、P1 = 5/6、P2 = 4/6。两个 P2 失败来自不同的 profile-topic cell：Power Iteration 的 computer science 和 Gradient Descent 的 mechanical engineering；但失败机制相同，都是加入 selected source authority 之外的合理但无来源算法断言。因此，这更像是 pipeline-level provenance-control weakness，而不是某个主题特有的数学失败。

## RQ2 判定

| 组成部分 | 两主题 pilot 判定 |
|---|---|
| H2a：P2 具有更高教学评分 | 相对 P0 的 framing 和 sequence 部分支持；相对 P1 不支持 |
| H2b：P2 生成 materially different、profile-linked pathways | 两个主题均支持；6 组跨 profile P2 comparison 全部 valid 且 confirmed |
| H2c：每条所选 pathway 都保持 correctness、provenance 和 dependency coherence | selected core correctness 与 dependency coherence 较强，但 uniform provenance preservation 未满足 |
| Cross-topic portability | 已支持 Power Iteration 与 Gradient Descent 之间的 feasibility；尚不能做 confirmatory generalization |
| 总体 RQ2 | dependency-aware adaptation 在结构上有效，并改善通用 P0；但尚未证明优于 P1，也未证明所有输出安全 |

因此，对 RQ2 最稳妥的回答是：dependency-aware、learner-profile-driven adaptation 能够生成 materially different 且教学上适切的 pathway 结构，并在大多数情况下保持所选数学内容正确；但当前系统仍不能稳定阻止无来源扩展，而且自动 rubric 没有证明 P2 的教学质量优于强 P1 baseline。

## 下一步建议

1. 人工裁决 mechanical-engineering P2 的 unsupported claims，并保留两份原始 judgement；
2. 为 composer 增加预先规定的规则：面向学生的 mathematical/algorithmic advice 必须映射到 selected Contract item 或 released bridge，否则必须删除或明确标记为 out of scope；
3. 决定是否按照冻结后的规则重新生成所有受影响的 condition cells，不能只修复失败样本；
4. 若需要更强的推断证据，应为每个 profile-condition-topic cell 生成多个独立 lesson；重复 judge 不能替代 generation replication；
5. 保留 topic-level 结果，并继续将 example authenticity 设为 exploratory；
6. 在没有学生实验的情况下，只能将 pedagogical appropriateness 表述为 automated operational measure，不能声称 comprehension、mastery 或 learning gain。

## 已生成的证据文件

- `aggregate-results.json`：Gradient Descent 条件汇总和配对比较；
- `cross-topic-aggregate-results.json`：Power Iteration 与 Gradient Descent 的联合描述性聚合；
- `reliability-report.json`：两次原始 blind pass 的一致性；
- `pathway-difference-report-confirmed.json`：带 receipt-based review authority 的 confirmed P2 跨 profile comparison；
- `p1-pathway-difference-report.json`：固定 pathway control 检查；
- 三份 profile-specific P2-vs-P1 结构报告；
- `blind-samples`、`judge-pass-01`、`judge-pass-02` 和 `private-mappings`：可审计的 pointwise evidence。
