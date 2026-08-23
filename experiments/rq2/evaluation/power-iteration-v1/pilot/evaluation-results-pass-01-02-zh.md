# RQ2 Power Iteration Pilot 评估报告

状态：pilot、人工裁决前报告。本中文文件仅用于本次研究者辅助审阅；正式使用时应以同目录英文报告为准，并只发布英文版。

评估日期：2026 年 8 月 19 日  
协议：RQ2-EVAL-v1  
主题：Power Iteration

## 核心结论

本次 pilot 对 RQ2 提供的是部分支持，而不是 confirmatory 证明。

依赖感知的 P2 planner 确实生成了结构明显不同、与 learner profile 有依据关联、并通过确定性验证的 pathway。相对于 P0，P2 在学科框架适切性和教学顺序质量上得到更高评分；但相对于更强的 P1 control，P2 在四个主要教学指标上几乎没有进一步提升：四个维度的配对差中位数均为 0，只有学科框架出现一次 P2 胜出，其余均为平局。这说明 P1 的局部 profile-aware 表达已经在本次 pilot 中接近评分上限，P2 最清楚的贡献是路径结构差异，而不是明显更高的 rubric 分数。

大多数输出中的所选数学内容完整、来源映射正确、公式准确且依赖顺序连贯，但 H2c 没有全部通过。computer-science P2 在两次评审中都因为加入 Frozen Contract 和 released bridge authority 之外的算法复杂度及复现性断言而失败。computer-science P1 还有一次评审发现了轻微输入验证缺陷。因此，目前不能声称所有 pilot 输出都保持了完整的 correctness 和 provenance。

当前证据支持 dependency-aware pathway adaptation 的可行性，并按照预先规定的结构指标确认了 materially different、profile-linked 的 P2 pathways；但尚不能证明 P2 的教学质量优于 P1，也不能证明所有 profile 均满足 H2c。

## 实验设计与分析样本

| 条件 | 实验作用 |
|---|---|
| P0 | 使用固定完整路径的通用 lesson，并分别针对三个 profile 评估 |
| P1 | 在不改变 P0 selection 和 sequence 的前提下调整措辞、表示和例子 |
| P2 | 可根据 profile 调整选择、顺序、分组、深度，并使用 released prerequisite bridges |

pilot 一共包含 7 份独立生成的 lesson：1 份 P0、3 份 P1 和 3 份 P2。为了完成 profile-matched comparison，同一份 P0 分别按照三个 profile 评分，因此建立了 9 个 profile-relative blind samples。P0 的三组评分不能解释为三份独立生成结果。

每个盲样本进行了两次全新的自动评审，共得到 18 份 judgement 和 18 份通过确定性校验的 score report。pointwise evaluation 看不到条件标签，但可以看到 learner profile，因为 profile fit 本身是评估指标。这两次评审是自动 evaluator 的重复测量，不是两位独立人类专家，也不能增加 lesson sample size。

字数控制基本可比：

| 条件/profile | 英文正文词数 | section 数 | 所选 Contract items | released bridges |
|---|---:|---:|---:|---:|
| P0，共用 | 1,636 | 8 | 18 | 0 |
| P1，applied mathematics | 1,500 | 8 | 18 | 0 |
| P1，computer science | 1,516 | 8 | 18 | 0 |
| P1，mechanical engineering | 1,554 | 8 | 18 | 0 |
| P2，applied mathematics | 1,568 | 7 | 18 | 1 |
| P2，computer science | 1,500 | 8 | 17 | 3 |
| P2，mechanical engineering | 1,554 | 18 | 17 | 3 |

代码块数量没有被用作教学质量指标。只有 pathway 选择了相应 Contract algorithm/code opportunity 时，才评估算法和代码安全性。

## H2a：主要教学指标

下表先对同一样本的两次评分取中位数，再汇总三个配对 profile。四个指标保持独立，没有计算综合总分。

| 指标 | P0 中位数 | P1 中位数 | P2 中位数 | P2-P1 配对差中位数 | P2-P0 配对差中位数 |
|---|---:|---:|---:|---:|---:|
| Disciplinary framing appropriateness | 4.0 | 5.0 | 5.0 | 0.0 | +1.0 |
| Prerequisite match | 4.5 | 5.0 | 5.0 | 0.0 | 0.0 |
| Context-boundary awareness | 5.0 | 5.0 | 5.0 | 0.0 | 0.0 |
| Sequence quality | 4.5 | 5.0 | 5.0 | 0.0 | +0.5 |

P2-P1 中，disciplinary framing 为一次 P2 胜出、两次平局，描述性 superiority probability 为 0.667；其余三个指标均为三次平局。P2-P0 中，framing 和 sequence 均为两次胜出、一次平局，superiority probability 为 0.833；prerequisite match 为一次胜出、两次平局；context-boundary awareness 因所有条件都达到上限而全部平局。

这意味着：

- P2 相对于较弱的通用 P0，最明显改善了学科框架和顺序质量；
- 在这次单 run pilot 中，P2 没有在主要评分上显著超过 P1；
- P1 是一个有效且较强的 control，因为仅通过 profile-aware 的措辞和表示，即使 pathway 固定，也可能得到很高评分；
- 当前材料和 rubric 存在明显 ceiling effect，尤其是 context-boundary awareness。

example authenticity 仍是 exploratory outcome。按样本中位数描述，约为 P0 = 2、P1 = 3、P2 = 3。这只能说明 P1/P2 的学科情境比通用 P0 更可信，不能证明其代表真实专业实践，也不能用于接受 H2a。

## H2b：pathway 结构差异

P1 成功发挥了固定路径 control 的作用：三个 profile 之间的 selection、order、grouping、bridge 和 depth distance 全部为 0。

P2 的三个跨 profile comparison 都通过了确定性验证、包含 profile-linked rationale，并被确认为 material difference：

| P2 profile pair | Selection distance | Normalized order distance | Grouping distance | Bridge distance | 结构解释 |
|---|---:|---:|---:|---:|---|
| Applied mathematics vs computer science | 0.0556 | 0.6667 | 0.3000 | 1.0000 | selection、order、grouping、bridge、depth 均改变 |
| Applied mathematics vs mechanical engineering | 0.0556 | 0.6667 | 1.0000 | 1.0000 | selection、order、grouping、bridge、depth 均改变 |
| Computer science vs mechanical engineering | 0.0000 | 0.1176 | 1.0000 | 0.0000 | selected items 相同，但 order、grouping、depth 改变 |

同一 profile 内，P2 相对 P1 也发生了结构变化：

| Profile | Selection distance | Normalized order distance | Grouping distance | Bridge distance |
|---|---:|---:|---:|---:|
| Applied mathematics | 0.0000 | 0.1111 | 0.5882 | 1.0000 |
| Computer science | 0.0556 | 0.6111 | 0.4667 | 1.0000 |
| Mechanical engineering | 0.0556 | 0.6111 | 1.0000 | 1.0000 |

这些变化不是单纯的换词。applied mathematics 保留全部 Contract items，但改变了顺序、分组、bridge 和教学深度；computer science 和 mechanical engineering 还各自排除了一个 item。

按照严格 metric，三个 comparison 现在都已 confirmed。每个最终 pathway 都有一份 `bridge-resolution-receipt.json`，将 materialized output 通过 hash 精确绑定到已批准的父 pathway review、released bridge catalog 和 bridge release report。evaluator 独立验证了所有引用文件及 hash、父 review 决定、catalog 对父 pathway/review 的精确绑定和 released 状态，之后才继承 review authority。这并不表示 reviewer 直接审阅了 materialized 文件，而是说明经过审阅的规划决策通过受约束的 bridge-materialization 步骤被保留下来。

## H2c：所选内容安全性

| 条件 | 两次 evaluator pass 均通过 H2c 的样本数 |
|---|---:|
| P0 | 3/3 |
| P1 | 2/3 |
| P2 | 2/3 |

总体上，required learning-goal coverage、公式 provenance、结构依赖验证和 released-bridge compliance 表现良好，没有发现 critical mathematical 或 algorithmic error。失败集中在两个位置：

1. computer-science P1：一次评审将 RC-017 判断为 partial coverage 和 minor algorithmic error。实现能够拒绝小于 1 的 max_iterations，但没有显式要求 integer；正的非整数会进入 range 并抛出 TypeError，而不是预期的清晰验证错误。另一次评审接受了该实现，因此需要人工 adjudication。
2. computer-science P2：两次评审都发现了 Contract/bridge authority 之外的算法复杂度断言。两次都标记了 dense O(n^2) 和 sparse nonzero-dependent cost；其中一次还标记了迭代工作量及复现性表述。其所选数学内容、公式和核心算法本身仍被判断为完整正确，但 H2c 是 conjunctive gate，因此这些无来源扩展导致整个样本失败。

P2 computer-science 问题可以直接修复：删除额外 complexity/reproducibility 断言，或者为它们建立独立、grounded、经过 review 的 source/bridge authority。但不能在看到结果后静默重生成；confirmatory 阶段的 regeneration policy 必须预先确定并对所有条件一致执行。

## Evaluator reliability

| 指标 | Exact agreement | Mean absolute difference | 差值至少为 2 的数量 | Ordinal Krippendorff alpha |
|---|---:|---:|---:|---:|
| Disciplinary framing appropriateness | 0.889 | 0.111 | 0 | 0.799 |
| Prerequisite match | 0.556 | 0.444 | 0 | -0.214 |
| Context-boundary awareness | 1.000 | 0.000 | 0 | 1.000 |
| Sequence quality | 0.778 | 0.222 | 0 | 0.655 |

四个主要指标都没有出现相差 2 分或以上的情况。prerequisite match 的负 alpha 出现在所有分歧都只有 1 分的情况下，主要反映小样本、分数高度集中在上限，以及该指标区分度不足；它仍然不能视为可靠。confirmatory 评分前，需要为 prerequisite-match anchors 增加正例、边界例和反例，并进行人工 calibration。context-boundary 的一致性虽然为 1，但同样受到 ceiling saturation 影响，因此高一致性并不自动代表该指标敏感。

## 本次 pilot 的 RQ2 判定

| 组成部分 | Pilot 判定 |
|---|---|
| H2a：P2 具有更高教学评分 | 相对 P0 部分支持；相对 P1 在本次 pilot 中不支持 |
| H2b：P2 生成 materially different、profile-linked pathways | 支持：三个跨 profile comparison 均通过确定性验证，并通过验证后的 materialization-receipt review authority 得到 confirmed |
| H2c：每条所选 pathway 都保持 correctness、provenance 和 dependency coherence | 人工裁决前未全部满足，因为一个 P1 和一个 P2 computer-science 样本未通过 conjunctive gate |
| 总体 RQ2 | 支持可行性和结构适配；尚未证明比较性教学优势和统一安全性 |

## 下一步必须完成的任务

1. 人工裁决 P1 的 RC-017 integer-validation 问题，以及 P2 computer-science 的 unsupported complexity claims，并保留两次原始 judgement。
2. 使用正例、边界例和反例校准 prerequisite-match anchors；当前重复评分可靠性不足。
3. 冻结修订后的 pilot protocol，然后按既定设计为每个 profile-condition cell 生成 3 个独立 run。不能将重复 judge 或 profile-relative P0 rating 当作独立 lesson run。
4. 用相同设计增加 Gradient Descent 案例后，再讨论 cross-topic portability；当前 cross-topic summary 只有 Power Iteration。
5. 继续将 example authenticity 作为 exploratory outcome；在没有学生实验的情况下，不得声称 learner comprehension 或 learning gain。

## 已生成的证据文件

- aggregate-results.json：条件汇总和配对比较；
- reliability-report.json：两次原始盲评的一致性；
- pathway-difference-report-confirmed.json：包含已验证 receipt-based review authority 的 confirmed P2 跨 profile 结构比较；
- pathway-difference-report.json：保留为继承审核权威之前的 candidate audit history；
- p1-pathway-difference-report.json：固定 pathway control 检查；
- 三份 profile-specific P2-vs-P1 pathway-difference report；
- blind-samples、judge-pass-01、judge-pass-02 和 private-mappings：可审计的 pointwise evidence。
