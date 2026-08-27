# Gradient Descent: From an Update Rule to a Guarantee

Gradient descent is an iterative method for reducing a differentiable objective. Its update is compact enough to fit on one line, but that line is only the beginning: the behaviour of the iteration depends on what the objective is like and how the step size is chosen. In this lesson, you will move from the optimisation problem and the current-gradient update to executable traces, sufficient-decrease checks, and convergence statements whose assumptions remain visible. A machine-learning loss can motivate the objective, but the mathematics here concerns a basic full-gradient method; it does not imply that a production training objective is convex or that this iteration is a complete training system.

The central reading habit is to separate three layers. An update rule says what computation to perform. A diagnostic says what happened in one execution. A theorem says what must happen whenever all of its hypotheses hold. Keeping those layers distinct prevents a successful numerical example from being promoted into an unsupported general claim, and it makes each assumption useful rather than decorative.

<!-- section: SEC-01 -->
## The objective, gradients, and stationary points

We begin with the unconstrained problem

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where $f:\mathbb{R}^d\to\mathbb{R}$ is at least continuously differentiable, written $f\in C^1$. The vector $x$ is the state we may change, and the scalar $f(x)$ is the value we want to make small. “Unconstrained” matters: every vector in $\mathbb{R}^d$ is in the stated search domain. Adding a restriction on $x$ would define a different problem.

In a computer program, you might represent $x$ as a length-$d$ array and implement $f$ as a function returning one number. That representation does not alter the mathematical problem. The array may contain parameters of an educational loss example, but the lesson needs only the stated map from vectors to scalars. Continuously differentiable means that the first partial derivatives exist and fit together as a continuous gradient map, which is the information the update will query.

Two multivariable-calculus ideas prepare us to reason about this objective. First, a point $a$ is a local minimum when some neighbourhood of $a$ has $f(a)\leq f(x)$ for every nearby $x$. This compares values locally; it does not say that $a$ is best over the whole domain. Second, for $f(x_1,\ldots,x_d)$, assemble the first partial derivatives into the column vector

$$
\nabla f(x)=\left(\frac{\partial f}{\partial x_1},\ldots,
\frac{\partial f}{\partial x_d}\right)^T.
$$

For example, if $f(x,y)=x^2+xy$, then $\nabla f(x,y)=(2x+y,x)^T$, so $\nabla f(1,2)=(4,1)^T$. This is only a gradient calculation; it makes no claim that $(1,2)$ is a minimum.

If $x^*$ is a local minimiser and $f$ is differentiable at $x^*$, then the necessary first-order condition is

$$
\nabla f(x^*)=0.
$$

Such a point is stationary. Be precise about the logic: a differentiable local minimum must be stationary, but stationarity by itself is not sufficient to identify a minimum without additional assumptions. Gradient descent searches by reacting to nonzero current gradients; the condition above describes what must be true at a differentiable local solution, not a standalone test that every stationary point passes.

It is helpful to phrase this as a one-way implication. Begin with the claim that the point is a differentiable local minimiser; stationarity follows. Beginning with a zero gradient does not let you reverse that implication. This logical direction will matter later, when convexity adds global structure. For now, the result supplies a necessary target condition while deliberately making no claim about whether an iteration reaches such a point.

<!-- section: SEC-02 -->
## Turning the current gradient into an iteration

Choose an initial state $x_0\in\mathbb{R}^d$ and positive step sizes $\alpha_k$. Standard gradient descent performs

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),
\qquad k=0,1,2,\ldots.
$$

Read the update as a state transition. At iteration $k$, evaluate the gradient at the current state $x_k$, scale it by a positive number, subtract it, and store the result as $x_{k+1}$. The evaluation point and sign are essential: this rule does not use a future gradient, and it does not add the current gradient.

The iteration index also gives the trace a clear contract. A record for iteration $k$ should contain the state before the update, the gradient computed from that same state, the selected positive step, and the resulting next state. If the stored gradient came from a different state, the record would no longer demonstrate this rule. This explicit state transition is especially useful when reviewing array code, because an in-place assignment can otherwise obscure which value supplied the gradient.

In pseudocode, the data flow is:

```text
x = x0
for k = 0, 1, ..., K-1:
    g = gradient_f(x)
    alpha = positive_step_for_iteration(k)
    x_next = x - alpha * g
    record(k, x, g, alpha, x_next)
    x = x_next
```

Here is a self-contained trace for the illustrative objective $f(x)=\tfrac12(x_1^2+4x_2^2)$. The output exposes the state used for each gradient call rather than hiding the iteration inside an optimiser.

```python
import numpy as np

def objective(x):
    return 0.5 * (x[0] ** 2 + 4.0 * x[1] ** 2)

def gradient(x):
    return np.array([x[0], 4.0 * x[1]], dtype=float)

x = np.array([2.0, -1.0], dtype=float)
alpha = 0.25

for k in range(4):
    g = gradient(x)
    x_next = x - alpha * g
    print(k, x.copy(), objective(x), g.copy(), alpha, x_next.copy())
    x = x_next
```

This finite trace demonstrates the update mechanically. Observed decreases in a particular run are diagnostics, not a general convergence guarantee; guarantees require assumptions that we now make explicit.

When reading the printed rows, compare each row’s last vector with the next row’s current vector. That check confirms state transfer. You can also recompute one subtraction by hand to confirm that the gradient was evaluated before the state changed. Neither check says how other objectives or step choices will behave.

<!-- section: SEC-03 -->
## Measuring change and bounding a smooth objective

For a vector $z\in\mathbb{R}^d$, its Euclidean norm is

$$
\|z\|_2=\sqrt{z^Tz},
$$

and $\|x-y\|_2$ measures the Euclidean distance between two vectors. A vector-valued map $G$ is $L$-Lipschitz, for $L>0$, when

$$
\|G(x)-G(y)\|_2\leq L\|x-y\|_2
$$

for every pair $x,y$ in its domain. This says that the output-vector change is bounded relative to the input-vector change. For $G(x)=2x$, the equality $\|G(x)-G(y)\|_2=2\|x-y\|_2$ shows that the inequality holds with $L=2$. This example is about a vector map and carries no gradient-descent conclusion.

The norm turns two vector differences into nonnegative scalar magnitudes, so the comparison is meaningful even when the vectors point in different directions. The constant is a uniform multiplier: the same value must work for every permitted input pair, not only for points observed in a trace. A single successful comparison can illustrate how to read the inequality, but it cannot establish the required universal statement for an arbitrary map.

Apply that language to the gradient map. A continuously differentiable objective is $L$-smooth when $L>0$ and

$$
\|\nabla f(x)-\nabla f(y)\|_2
\leq L\|x-y\|_2,
\qquad \text{for all }x,y\in\mathbb{R}^d.
$$

The left side measures a change in gradient vectors. It is not a function-value Lipschitz condition involving $|f(x)-f(y)|$. Informally, smoothness limits how abruptly the gradient can change as the state changes, and the constant $L$ quantifies that bound.

The consequence we need is the Descent Lemma. If $f$ is $L$-smooth, then for every $x,y\in\mathbb{R}^d$,

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle
+\frac{L}{2}\|y-x\|_2^2.
$$

This is a quadratic upper bound: a linear prediction from the gradient is supplemented by a nonnegative quadratic allowance. Substituting the gradient-descent candidate $y=x-\alpha\nabla f(x)$ gives

$$
f\bigl(x-\alpha\nabla f(x)\bigr)
\leq f(x)-\alpha\left(1-\frac{L\alpha}{2}\right)
\|\nabla f(x)\|_2^2.
$$

The substitution shows why step size cannot be discussed independently of smoothness. It provides a bound on the candidate’s objective value; it does not yet supply either convexity or a convergence theorem.

Notice the roles of the three terms in the upper bound. The current value is the baseline, the inner product measures the first-order change along the proposed displacement, and the squared norm allows for curvature of the objective within the smoothness bound. After substituting the update, both correction terms depend on the same current gradient. Their combined coefficient exposes why increasing the step changes what the bound can certify, even though the update formula itself remains syntactically valid for any positive step.

<!-- section: SEC-04 -->
## Choosing and checking a constant step

A constant-step implementation sets $\alpha_k=\alpha$ at every iteration. When $L$ is known, a common choice is $\alpha=1/L$. Under the usual smooth-convex assumptions, the stated constant-step interval is

$$
0<\alpha<\frac{2}{L}.
$$

Keep that qualification attached: the interval is not a universal recommendation for an arbitrary objective. In the smooth setting, the bound from the previous section also makes the role of $L\alpha$ visible. A state trace should therefore record the objective, gradient norm, and chosen step, so that the numerical transition can be checked against the precise rule without being mistaken for a theorem.

Constant means constant across iteration indices, not constant across every possible problem. Once the objective and value of $L$ have been fixed for the stated setting, the implementation stores one positive scalar and reuses it. Recording that scalar on every row may look redundant, but it makes the trace auditable: a reader can distinguish an intended constant-step run from code that silently changes the step between iterations.

The next block independently traces the illustrative quadratic with its constant $L=4$ and checks both the update equation and observed objective values.

```python
import numpy as np

def objective(x):
    return 0.5 * (x[0] ** 2 + 4.0 * x[1] ** 2)

def gradient(x):
    return np.array([x[0], 4.0 * x[1]], dtype=float)

L = 4.0
alpha = 1.0 / L
x = np.array([2.0, -1.0], dtype=float)

for k in range(5):
    g = gradient(x)
    x_next = x - alpha * g
    assert np.allclose(x_next, x - alpha * gradient(x))
    print(k, objective(x), np.linalg.norm(g), alpha, objective(x_next))
    x = x_next
```

<!-- section: SEC-05 -->
## Selecting a step by Armijo backtracking

A fixed step requires a chosen constant. Armijo backtracking instead tests a decreasing sequence of trial steps against a sufficient-decrease condition. Choose an initial trial step $\bar\alpha>0$, a contraction factor $\eta\in(0,1)$, and $c\in(0,1)$. Test $m=0,1,2,\ldots$ in order, setting $\alpha_k=\eta^m\bar\alpha$, and accept the smallest nonnegative $m$ for which

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)
\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|_2^2.
$$

The right side is the current value reduced by a scaled squared gradient norm. The acceptance inequality points toward smaller values, and the square on the norm is part of the condition. Sequential testing is important: stopping at the first accepted candidate implements the smallest-$m$ rule.

Conceptually, the inner loop has one state that does not change and one trial value that does. During backtracking, $x_k$ and its gradient remain fixed while the exponent increases and the trial step contracts. Only after acceptance does the algorithm form the next iteration state. Logging both sides of the inequality makes the Boolean decision reproducible and reveals whether rejection resulted from the exact sufficient-decrease test rather than from an unrelated stopping rule.

```python
import numpy as np

def objective(x):
    return 0.5 * (x[0] ** 2 + 4.0 * x[1] ** 2)

def gradient(x):
    return np.array([x[0], 4.0 * x[1]], dtype=float)

x = np.array([2.0, -1.0], dtype=float)
alpha_bar = 1.0
eta = 0.5
c = 0.1
g = gradient(x)

accepted = None
for m in range(20):
    alpha = (eta ** m) * alpha_bar
    candidate = x - alpha * g
    left = objective(candidate)
    right = objective(x) - c * alpha * np.linalg.norm(g) ** 2
    print(m, alpha, left, right, left <= right)
    if left <= right:
        accepted = (m, alpha, candidate)
        break

if accepted is None:
    raise RuntimeError("No trial step was accepted in the diagnostic range")

m, alpha, x_next = accepted
print("accepted", m, alpha, x_next)
```

This block is an acceptance diagnostic for one objective and state. It illustrates the exact trial sequence and condition, without turning the observed accepted step into a guarantee for objectives outside the stated setting.

<!-- section: SEC-06 -->
## From inner products to convexity and strong convexity

Before stating global structure, recall two pieces of vector geometry. For real vectors $u$ and $v$ of the same dimension, the inner product $u^Tv$ is the scalar sum of their componentwise products. To parse $g^T(y-x)$, first form the displacement $d=y-x$, then compute the scalar $g^Td$. Its sign describes alignment between $g$ and the displacement, but that arithmetic alone implies no convexity theorem.

For $x,y$ and $\theta\in[0,1]$, the point $\theta x+(1-\theta)y$ is a convex combination. A set is convex if it contains every such combination of every pair of its points. For example, with $x=(0,0)^T$, $y=(2,4)^T$, and $\theta=1/4$, the combination is $(3/2,3)^T$. If $g=(1,-1)^T$, then $g^T(y-x)=-2$. These computations only establish the combination and inner-product values.

These two constructions prepare different parts of the next definition. Convex combinations describe the geometry associated with the word “convex,” while the inner product lets a gradient interact with a displacement. Neither construction alone states how a function behaves. That separation is useful: it prevents a negative inner product in one example, or membership of one combination in a set, from being treated as proof of a global property.

Now consider a differentiable function on $\mathbb{R}^d$. It is convex when, for all $x,y\in\mathbb{R}^d$,

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle.
$$

Unlike the smoothness upper bound, this is a global first-order lower bound. At any base point $x$, the affine expression built from $f(x)$ and $\nabla f(x)$ lies no higher than the function at every $y$. The universal “for all” is essential.

For $\mu>0$, the function is $\mu$-strongly convex when, for all $x,y\in\mathbb{R}^d$,

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle
+\frac{\mu}{2}\|y-x\|_2^2.
$$

Strong convexity adds a positive quadratic term to the convex lower bound. It is therefore a stronger assumption than the preceding inequality, not merely another name for convexity. We will use the definition directly, without a Hessian-based derivation.

Compare this lower bound with the earlier smoothness upper bound. Both start from the same current value and gradient inner product, but they constrain opposite sides and use different positive constants. Smoothness limits how high the function can lie above the linear expression, whereas strong convexity requires it to lie above that expression by an additional quadratic amount. Keeping those directions distinct is essential when matching assumptions to later guarantees.

<!-- section: SEC-07 -->
## Reading the condition ratio

Suppose $0<\mu\leq L$. The ratio

$$
\kappa=\frac{L}{\mu}
$$

measures their multiplicative separation. Dividing $0<\mu\leq L$ by the positive number $\mu$ gives $\kappa\geq1$. A value near one means the constants are close; a larger value means they are farther apart multiplicatively. For example, $L=12$ and $\mu=3$ give $\kappa=4$, while $L=\mu$ gives $\kappa=1$. The ratio requires $\mu>0$; it is not a finite ratio when $\mu=0$.

For an objective that is both $L$-smooth and $\mu$-strongly convex, this is its condition number: $\kappa=L/\mu\geq1$. This is the only condition measure needed here. Its relevance will be explicit in the contraction factors below, rather than imported from a matrix or numerical-linear-algebra definition.

The ratio is dimensionless in the sense relevant to these formulas: it reports how many times the positive lower constant fits into the smoothness constant. Computing it is an arithmetic step after both constants have been identified under the stated objective assumptions. It does not create strong convexity or smoothness; those properties must already be available before this condition number is defined.

<!-- section: SEC-08 -->
## Matching convergence guarantees to their assumptions

First take the convex case. Assume that $f$ is $L$-smooth and convex, that a global minimiser $x^*$ exists, and that gradient descent uses $\alpha_k=1/L$. Then for every $k\geq1$,

$$
f(x_k)-f(x^*)
\leq \frac{L\|x_0-x^*\|_2^2}{2k}.
$$

This is an $O(1/k)$ objective-gap guarantee. It bounds the difference between the current objective value and the global minimum value in terms of the initial squared distance, $L$, and the iteration count. It is not a claim that every differentiable objective has this rate, nor is it the same as a bound on $\|x_k-x^*\|$; all four hypotheses—smoothness, convexity, a global minimiser, and the $1/L$ step—belong with the statement.

The denominator explains the rate label: increasing the iteration count reduces the displayed upper bound in inverse proportion to that count. The numerator records the starting geometry and the smoothness scale. This is a worst-case upper bound under the hypotheses, not a prediction that every run attains equality. A trace may decrease faster or differently while still being compatible with the theorem.

Now strengthen the structural assumption. If $f$ is both $L$-smooth and $\mu$-strongly convex, gradient descent has the following distance contraction when the constant step is

$$
\alpha=\frac{2}{L+\mu}:
$$

$$
\|x_k-x^*\|_2^2
\leq
\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}
\|x_0-x^*\|_2^2.
$$

With the different constant step $\alpha=1/L$, the corresponding objective-gap contraction is

$$
f(x_k)-f(x^*)
\leq
\left(1-\frac{\mu}{L}\right)^k
\bigl(f(x_0)-f(x^*)\bigr).
$$

Do not swap these pairings: $2/(L+\mu)$ belongs with the squared-distance contraction, while $1/L$ belongs with the displayed objective-gap contraction. Both require smoothness and strong convexity. Because $\mu/L=1/\kappa$, the objective contraction factor is $1-1/\kappa$; as the multiplicative separation grows, that factor approaches one. Likewise, $(\kappa-1)/(\kappa+1)$ approaches one as $\kappa$ grows. Thus the formulas themselves expose how conditioning affects the guaranteed contraction.

The two conclusions also measure different quantities. One compares squared distances between iterates and the minimiser; the other compares objective values. Their exponents and factors should therefore be read with their own left-hand sides, not copied across measures. “Linear convergence” here refers to repeated multiplication by the stated factor across iterations, under the accompanying assumptions. It does not mean that the objective is a linear function.

The lesson’s hierarchy is now complete. Differentiability makes the gradient and stationary-point condition available. The current-gradient rule defines the algorithm. Smoothness controls gradient change and supplies a quadratic upper bound; constant and Armijo choices specify how a step is selected. Convexity supports the sublinear objective guarantee, while strong convexity and smoothness support the stated geometric contractions and make the condition ratio relevant. When an objective does not satisfy those assumptions—as may happen for a machine-learning loss—the corresponding guarantee cannot simply be carried over. An executable trace can confirm that code follows an update or acceptance rule, but it cannot replace the hypotheses of a theorem.
