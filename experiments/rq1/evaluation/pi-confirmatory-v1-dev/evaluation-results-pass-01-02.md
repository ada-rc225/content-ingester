# PI 背景 RQ1 自动评估结果（Pass 01–02）

## 结论摘要

在本次 Power Iteration confirmatory-v1 数据上，`c2-structured-grounding` 呈现出最好的综合描述性结果：13 个 generation-required Contract 条目的重大/严重错误率为 **0%**，公式条目准确率为 **100%**，算法条目准确率为 **81.25%**，且 7 个教学维度中的 5 个取得三组最高值。`c1-source-conditioned` 的主要错误率也低于 C0，并取得最低的不受支持陈述率 **2.64%**。`c0-ungrounded` 在主要错误、语义漂移、不受支持陈述、公式与算法准确率上均最弱。

不过，这还不能作为统计显著或可推广的因果结论。最关键的限制是：C2 的三次运行具有完全相同的内容哈希，因此名义样本数为 3，实际唯一文本数只有 1。当前结果支持“结构化 grounding 在该 PI 文本上表现最好”，但不能证明它在独立重复生成中稳定优于其他条件。

## 条件级 fidelity 结果

每个 lesson 先对两个独立 evaluator pass 取平均，再在条件内对三个名义 run 取平均。错误率越低越好；准确率越高越好。

| 条件 | 名义 run / 唯一文本 | 重大/严重错误率 | 语义漂移率 | 必需项遗漏率 | 不受支持陈述率 | 条件失败率 | 公式准确率 | 算法准确率 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C0 ungrounded | 3 / 3 | 5.13% | 20.37% | 0.00% | 18.47% | 9.90% | 76.67% | 66.67% |
| C1 source-conditioned | 3 / 3 | 3.85% | 9.26% | 0.00% | **2.64%** | 2.60% | **100.00%** | 79.17% |
| C2 structured-grounding | 3 / 1 | **0.00%** | **8.33%** | 0.00% | 4.97% | **1.56%** | **100.00%** | **81.25%** |

相对 C0，C2 的语义漂移率降低约 **59.1%**，不受支持陈述率降低约 **73.1%**，条件失败率降低约 **84.2%**；公式准确率提高 23.33 个百分点，算法准确率提高 14.58 个百分点。C1 的不受支持陈述率比 C2 更低，因此不能简单地说 C2 在所有 fidelity 指标上都占优。

三组的 required-item omission 都是 0%，说明主要差异不是“完全没有提到某个必需主题”，而是已覆盖内容中的条件丢失、实现契约变化、公式/示例变化和未经契约支持的陈述。

## 条件级教学质量结果

教学维度使用 1–5 分，越高越好；没有把这些维度合成为单一总分。

| 条件 | 学习者适配 | 学科真实性 | 教学连贯性 | 理论—实现一致性 | 可读性 | 类比安全性 | 练习有效性 |
|---|---:|---:|---:|---:|---:|---:|---:|
| C0 ungrounded | 4.00 | 3.33 | 3.83 | 2.00 | 4.67 | 5.00 | 2.50 |
| C1 source-conditioned | 4.00 | 3.33 | 3.83 | 3.00 | **5.00** | 5.00 | 2.00 |
| C2 structured-grounding | **5.00** | **4.00** | **5.00** | **4.00** | 4.83 | 5.00 | **4.33** |

C2 的优势不只是 fidelity：它对二年级机械工程背景的定位更明确，概念—算法—代码的组织更完整，指定的三类练习也更接近任务要求。C1 在内容忠实度上明显优于 C0，但其三份输出的练习有效性均只有 2.0，主要因为手算题和代码诊断题没有完整满足 task brief 规定的形式。三组的类比安全性均为 5.0，说明机械工程类比总体都有清楚的范围边界。

## run 级结果

下表为两个 evaluator pass 的 lesson 内平均值。匿名 sample ID 仅用于追踪审计文件。

| 条件 | run | sample | 重大/严重错误率 | 漂移率 | 不受支持陈述率 | 公式准确率 | 算法准确率 | 练习有效性 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| C0 | run-01 | S004 | 3.85% | 19.44% | 17.70% | 80.00% | 68.75% | 2.0 |
| C0 | run-02 | S002 | 3.85% | 22.22% | 20.09% | 75.00% | 62.50% | 2.5 |
| C0 | run-03 | S005 | 7.69% | 19.44% | 17.62% | 75.00% | 68.75% | 3.0 |
| C1 | run-01 | S006 | 3.85% | 8.33% | 4.69% | 100.00% | 81.25% | 2.0 |
| C1 | run-02 | S003 | 7.69% | 11.11% | 1.67% | 100.00% | 75.00% | 2.0 |
| C1 | run-03 | S008 | 0.00% | 8.33% | 1.56% | 100.00% | 81.25% | 2.0 |
| C2 | run-01 | S007 | 0.00% | 11.11% | 7.13% | 100.00% | 75.00% | 4.5 |
| C2 | run-02 | S009 | 0.00% | 8.33% | 4.14% | 100.00% | 81.25% | 4.5 |
| C2 | run-03 | S001 | 0.00% | 5.56% | 3.64% | 100.00% | 87.50% | 4.0 |

C2 三行的文本内容实际上相同；行间差别来自同一文本在不同独立 judge pass 中的判断波动，而不是三份不同生成内容的变化。

## 主要问题模式

### C0 ungrounded

- 最常见的问题是丢失 Power Iteration 收敛所需的条件，特别是初始向量对主特征向量的非零投影、严格主模条件和 breakdown 条件。
- Python 实现经常缺少正的 `max_iterations`/tolerance 验证，改变异常行为或返回元组顺序，并替换任务指定的矩阵和初始向量。
- 公式和算法准确率最低；练习常未包含“一个归一化步骤 + Rayleigh quotient + residual”和完整的 buggy/corrected code。

### C1 source-conditioned

- 数学公式保持得很好，三份输出的公式准确率均为 100%，不受支持陈述率也是三组最低。
- 主要剩余问题集中在收敛条件和实现契约，尤其是参数验证与最大迭代路径。
- 教学练习没有充分遵守 task brief 的精确结构，因此 fidelity 提升没有自动转化为高练习有效性。

### C2 structured-grounding

- generation-required 条目中没有 major/critical error，公式与算法保持最好，教学结构也最完整。
- 剩余漂移主要在实现细节：例如没有强制正 tolerance，以及把 Contract 规定的 breakdown `RuntimeError` 改成 `ValueError`。评估器对这些边界项有轻微分类差异。
- 代码诊断练习是否提供“完整”的 corrected routine 在两个 pass 间存在判断差异，但整体练习质量仍明显高于 C0/C1。
- 三次输出完全一致，说明当前 C2 流程的确定性很强，也意味着本次实验未观察到 C2 的生成变异性。

## evaluator 可靠性

共评估 9 个匿名 lesson，每个 lesson 使用两个全新的 pointwise evaluator context，共 18 个 pass；18/18 的 judgement 均通过 schema、哈希绑定和确定性计分校验。两个 pass 使用同一模型 `gpt-5.6-sol`，但互相不能读取对方结果。

| 重复性指标 | 总体结果 |
|---|---:|
| 严重度精确一致率 | 92.59% |
| coverage 精确一致率 | 93.21% |
| drift-set 精确一致率 | 87.65% |
| 教学评分平均绝对差 | 0.254 / 5 |

主要分歧集中在 S002、S004、S005 和 S006 的 `minor`/`major` 边界，以及 S005 手算残差是否应构成严重错误。汇总没有人工选择某一次判断，而是按既定规则对两个 pass 取平均。上述一致率表示同一 AI judge 的可重复性，不表示与人类专家的一致性或真实准确率。

## 方法与输入完整性

- 评估协议：`RQ1-EVAL-v1`。
- evaluator：OpenAI Codex CLI，模型 `gpt-5.6-sol`，evaluator ID `rq1-pi-judge-sol`。
- Frozen Contract：`power-iteration` v1.0.0，共 18 项，其中 13 项为 generation-required；SHA-256 为 `3c749a34a0bc3d1bacd3022a8e403c4f6b090afcd99359245d51987db45e2ce7`。
- blind bundle manifest SHA-256：`7159b8a785d6e73ae43da27f27aa97d7f6bc0c4c854a133b5adc5e3938b1f2d1`。
- 解盲前完成全部 18 次判分和总体可靠性计算；评估器不能读取 condition mapping、生成过程产物或其他 lesson。
- `experiments/rq1/evaluation-specs/pi-confirmatory-v1/task_brief.txt` 在评估前被发现误含 Gradient Descent 任务。为避免用错误任务评测 PI 输出，已依据三次 PI C2 run manifest、adaptation plan 和 Frozen Contract 中保存的一致任务要求，先恢复为 PI task brief，再构建盲包。该修正应在实验审计中保留；后续实验应在生成前冻结并哈希 task brief。

## 解释边界

这些结果是 AI agent 基于 Frozen Contract 的自动化操作性测量，不是人工专家 ground truth。两个 pass 来自同一模型，只能评估重复性，不能替代跨模型或专家效度。每组只有三个名义 run，且仅覆盖一个 Power Iteration 主题；C2 又只有一个唯一文本。因此本报告不进行显著性检验、不报告因果效应，也不定义单一综合分数。更稳健的下一轮应确保每个条件产生多个不同文本，并加入已知标签的 mutation benchmark 来估计 evaluator 的错误检出灵敏度和特异度。

## 产物索引

- `condition-summary-pass-01-02.json`：fidelity 条件汇总、sample 行与 pass 行。
- `pedagogy-summary-pass-01-02.json`：教学维度和 condition-failure 汇总。
- `reliability-report-pass-01-02.json`：总体与逐 sample 的重复判分可靠性。
- `judgements/S001`–`judgements/S009`：18 份原始 judgement、score report 及逐 sample 可靠性报告。

