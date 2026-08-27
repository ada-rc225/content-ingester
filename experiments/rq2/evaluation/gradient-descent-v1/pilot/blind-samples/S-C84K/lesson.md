# Gradient Descent: From an Objective to a Traceable Iteration

<!-- section: SEC-01 -->
## From an engineering objective to stationarity

Many engineering calculations can be framed as choosing parameters that make a scalar objective small. In an idealized energy-minimisation problem, the vector might contain generalized displacements; in a parameter-calibration problem, it might contain coefficients of a simplified model. Here those settings are motivation, not a claim that every engineering task has the mathematical structure developed below.

The problem studied in this lesson is the unconstrained problem

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where $f:\mathbb{R}^d\to\mathbb{R}$ is at least continuously differentiable, written $f\in C^1$. “Unconstrained” matters: every vector in $\mathbb{R}^d$ is admissible in this formulation. Adding limits on stresses, dimensions, or parameters would define a different problem and is not part of the method considered here.

Differentiability gives a necessary first-order condition. If $x^*$ is a local minimizer and $f$ is differentiable at $x^*$, then

$$
\nabla f(x^*)=0.
$$

Such a point is called stationary. The direction and size of the gradient describe local first-order change, so the zero-gradient condition gives gradient descent a natural target. It does **not** say that every stationary point is a minimum. Stationarity is necessary for a differentiable local minimizer, not sufficient by itself. Likewise, even a mathematical minimizer of an idealized energy or calibration objective should not automatically be interpreted as a physically valid design; that interpretation depends on the model and its assumptions.

For parameter calibration, this distinction can be made concrete without adding a new mathematical setting. Imagine that $x$ collects adjustable coefficients and that $f(x)$ is a continuously differentiable scalar mismatch for an idealized model. Gradient descent addresses the numerical task of reducing that stated mismatch over all vectors in $\mathbb{R}^d$. It does not establish that the measurements, the model form, or the chosen mismatch adequately represent a physical system. In an energy framing, the same separation applies: the algorithm acts on the specified scalar function, while the physical meaning remains limited by how that function was constructed. These examples change the interpretation of $x$ and $f$, not the unconstrained optimisation problem itself.

It helps to separate three questions that will recur. First, what update moves from the current parameter vector to the next? Second, when does that update lower the objective? Third, under what additional structure can we bound progress toward a global minimizer? The assumptions become stronger as we answer those questions, and each conclusion must remain attached to the assumptions that support it.

<!-- section: SEC-02 -->
## The gradient-descent iteration

Choose an initial point $x_0\in\mathbb{R}^d$. Given a positive step size $\alpha_k$, gradient descent generates

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),
\qquad k=0,1,2,\ldots.
$$

There are three details worth reading literally. The gradient is evaluated at the current iterate $x_k$; the gradient term is subtracted; and the step size is positive. The result is a sequence $x_0,x_1,x_2,\ldots$, often accompanied by a convergence history such as $f(x_k)$ or $\|\nabla f(x_k)\|$. A small gradient can be a useful observation about stationarity, but the necessary condition above does not turn that observation into proof of a minimum.

As a bounded engineering-style example, consider two abstract parameters $x=(x_1,x_2)$ and the idealized objective

$$
f(x)=\frac12\left(x_1^2+4x_2^2\right),
\qquad
\nabla f(x)=\begin{bmatrix}x_1\\4x_2\end{bmatrix}.
$$

This expression can be viewed as a scaled quadratic energy for tracing the arithmetic, but it is not asserted to model a particular component. From $x_0=(2,-1)$ with $\alpha_k=0.2$, the first update is

$$
x_1=
\begin{bmatrix}2\\-1\end{bmatrix}
-0.2
\begin{bmatrix}2\\-4\end{bmatrix}
=
\begin{bmatrix}1.6\\-0.2\end{bmatrix}.
$$

The following self-contained program implements exactly the current-iterate update and prints an iteration table. Each row is printed before the next update, so row $k$ describes $x_k$.

```python
import numpy as np

def objective(x):
    return 0.5 * (x[0] ** 2 + 4.0 * x[1] ** 2)

def gradient(x):
    return np.array([x[0], 4.0 * x[1]], dtype=float)

x = np.array([2.0, -1.0])
alpha = 0.2

print(" k        x1        x2          f(x)      ||grad||")
for k in range(7):
    g = gradient(x)
    print(f"{k:2d}  {x[0]:9.5f} {x[1]:9.5f}  {objective(x):12.7f}  {np.linalg.norm(g):10.6f}")
    x = x - alpha * g
```

The table makes the algorithm traceable: calculate the gradient, multiply it by the chosen positive step, subtract, and repeat. It does not yet establish that the same step will be suitable for another objective. That requires information about how rapidly the gradient can change.

You can also trace the second row by hand. At $x_1=(1.6,-0.2)$, the current gradient is $(1.6,-0.8)$. Multiplication by $0.2$ gives the change vector $(0.32,-0.16)$, and subtraction gives $x_2=(1.28,-0.04)$. Notice that the gradient used for this calculation is evaluated at $x_1$, not retained from $x_0$ and not evaluated at the unknown $x_2$. This is why an implementation normally recomputes the gradient inside its iteration loop. The arithmetic illustrates the defined update only; the fact that the objective decreases in these particular rows is not, on its own, a general convergence argument.

When reading any iteration history, keep the objects separate. The vector $x_k$ is the current candidate, $f(x_k)$ is its objective value, and $\nabla f(x_k)$ supplies the update direction before scaling. The iteration counter labels how many updates have already occurred. Thus the initial row has index zero, and the first application of the rule produces the row with index one. This indexing matches the statement of the algorithm and prevents an off-by-one interpretation of later bounds.

<!-- section: SEC-03 -->
## Smoothness, descent, and a constant step

A continuously differentiable function is $L$-smooth, for some $L>0$, when its gradient is $L$-Lipschitz in the Euclidean norm:

$$
\|\nabla f(x)-\nabla f(y)\|
\le L\|x-y\|,
\qquad \text{for every }x,y\in\mathbb{R}^d.
$$

This condition controls changes in the gradient, not changes in the function value itself. In engineering language, it supplies a global bound on how sharply the first-order sensitivity may vary across the domain. That wording is only an interpretation of the inequality; the mathematical condition is the displayed gradient bound.

The key consequence is the Descent Lemma. If $f$ is $L$-smooth, then for every $x,y\in\mathbb{R}^d$,

$$
f(y)\le f(x)+\langle\nabla f(x),y-x\rangle
+\frac{L}{2}\|y-x\|^2.
$$

The inequality is an upper bound: the linear prediction is supplemented by a positive quadratic term. Substitute one gradient-descent trial point, $y=x-\alpha\nabla f(x)$, into this bound. Since $y-x=-\alpha\nabla f(x)$,

$$
f\bigl(x-\alpha\nabla f(x)\bigr)
\le f(x)-\alpha\left(1-\frac{L\alpha}{2}\right)
\|\nabla f(x)\|^2.
$$

This calculation explains the link between smoothness and step size. When the coefficient multiplying the squared gradient norm is positive, the upper bound lies below $f(x)$ unless the gradient is zero. It is a one-step descent statement, not yet one of the convergence guarantees developed later.

A constant-step version sets $\alpha_k=\alpha$ for every iteration. When $L$ is known, a common choice is

$$
\alpha=\frac{1}{L}.
$$

Under the usual smooth-convex assumptions, another listed constant-step range is

$$
0<\alpha<\frac{2}{L}.
$$

The smooth-convex qualification belongs with that interval; it is not a universal rule for arbitrary engineering objectives. For the tracing example above, the gradient difference obeys

$$
\|\nabla f(x)-\nabla f(y)\|
\le 4\|x-y\|,
$$

so $L=4$ is a valid smoothness constant and the implemented step $0.2$ lies in $(0,2/L)$. The special choice $1/L$ would be $0.25$. Knowing a valid $L$ connects a numerical step choice to an explicit assumption rather than to the physical label attached to the variables.

The Descent Lemma is useful here because it makes the logical route visible. Start with a condition on gradient differences. That condition supplies an upper bound on the objective at any proposed point. Choosing the proposed point to be the gradient-descent update turns the general upper bound into a statement involving the step size and squared gradient norm. No appeal to an energy picture is needed for those steps; the result follows from $L$-smoothness. The picture may help you remember what is being minimized, but the displayed inequalities carry the mathematical authority.

It is also important not to confuse a valid smoothness constant with a unique measured quantity. If the Lipschitz inequality holds for one positive value of $L$, using a larger bound may still make the inequality true, but the listed choice $1/L$ then changes with the bound used. The lesson only requires that the step rule and the convergence statements use a valid constant satisfying the stated assumption. A step copied from a different scaling of the parameters has no guarantee here unless its relationship to the current objective’s assumptions is established.

As a reading check, inspect the factor $1-L\alpha/2$ in the one-step inequality. At $\alpha=1/L$, that factor is one half, so the right-hand side subtracts a nonnegative multiple of the squared gradient norm. As $\alpha$ approaches $2/L$ from below, the factor approaches zero. This observation explains why the scale $L$ appears in the interval; it does not extend the interval beyond its stated smooth-convex qualification or create a convergence theorem for an arbitrary function.

<!-- section: SEC-04 -->
## Convexity, strong convexity, and conditioning

Smoothness controls an upper model, while convexity supplies a global lower model. A differentiable function $f:\mathbb{R}^d\to\mathbb{R}$ is convex when, for every $x,y\in\mathbb{R}^d$,

$$
f(y)\ge f(x)+\langle\nabla f(x),y-x\rangle.
$$

Thus the first-order affine expression based at any $x$ is a global lower bound. This is a property of the whole objective over $\mathbb{R}^d$, not something guaranteed merely because the objective is called an energy or a calibration error. The lesson’s engineering framing therefore does not supply convexity; convexity must be an actual mathematical assumption about $f$.

For $\mu>0$, strong convexity strengthens the lower bound. A differentiable function is $\mu$-strongly convex when, for every $x,y\in\mathbb{R}^d$,

$$
f(y)\ge f(x)+\langle\nabla f(x),y-x\rangle
+\frac{\mu}{2}\|y-x\|^2.
$$

The sign, square, and factor $\mu/2$ are essential. Compared with convexity, this adds positive quadratic growth to the lower bound. Strong convexity is the additional structure used by the faster contraction results in the next section; it should not be silently inferred from smoothness.

When an objective is both $L$-smooth and $\mu$-strongly convex, define its condition number by

$$
\kappa=\frac{L}{\mu}\ge 1.
$$

The ratio is $L$ divided by $\mu$, not the reverse. It packages the two constants that appear in the selected rate statements. A larger $\kappa$ makes the contraction factors shown below closer to one, which means those bounds certify less reduction per iteration. This gives a precise sense in which conditioning affects the guaranteed history. It does not imply that a single observed run reveals $L$, $\mu$, or $\kappa$, and it does not establish that a general engineering model satisfies either defining assumption.

At this stage the roles are distinct. Smoothness restricts gradient variation and supports an upper bound for a step. Convexity gives a global first-order lower bound. Strong convexity adds a positive quadratic term. Conditioning combines the smoothness and strong-convexity constants only when both structures hold.

One way to test your reading is to ask which inequality you would write before interpreting a word such as “well conditioned.” If only smoothness has been stated, $\mu$ and $\kappa$ are not yet available. If convexity has been stated without strong convexity, the additional quadratic term cannot be inserted into the lower bound. Only after both $L$-smoothness and $\mu$-strong convexity are established does $L/\mu$ have the condition-number meaning used here. This order prevents an engineering description from being treated as a substitute for a mathematical premise.

The two lower bounds also clarify the relationship to stationarity. Convexity and strong convexity are global conditions because their inequalities must hold for every pair $x,y$ in the domain. The earlier zero-gradient condition concerned what must happen at a differentiable local minimizer. They answer different questions: stationarity identifies a necessary local feature, whereas the lower-bound assumptions supply the global structure used in the convergence results. Keeping those roles distinct avoids claiming that a zero gradient alone provides the later global guarantees.

<!-- section: SEC-05 -->
## Reading the convergence guarantees

The first guarantee uses convexity without requiring strong convexity. Suppose $f$ is $L$-smooth and convex, a global minimizer $x^*$ exists, and gradient descent uses $\alpha_k=1/L$. Then, for every $k\ge1$,

$$
f(x_k)-f(x^*)
\le
\frac{L\|x_0-x^*\|^2}{2k}.
$$

This is an objective-gap bound. The numerator records the smoothness constant and the initial squared distance to a global minimizer; the denominator grows as $2k$. The usual $O(1/k)$ description summarizes that dependence on the iteration count. It must not be detached from smoothness, convexity, existence of a global minimizer, the $1/L$ step, or the restriction $k\ge1$.

Stronger structure supports geometric contractions. If $f$ is both $L$-smooth and $\mu$-strongly convex, gradient descent with the constant step

$$
\alpha=\frac{2}{L+\mu}
$$

satisfies the squared-distance bound

$$
\|x_k-x^*\|^2
\le
\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}
\|x_0-x^*\|^2,
\qquad \kappa=\frac{L}{\mu}.
$$

Keep that step paired with that distance contraction. Under the same $L$-smooth and $\mu$-strongly convex assumptions, the different constant step $\alpha=1/L$ gives the objective-gap contraction

$$
f(x_k)-f(x^*)
\le
\left(1-\frac{\mu}{L}\right)^k
\bigl(f(x_0)-f(x^*)\bigr).
$$

These are called linear or geometric rates because the relevant factor is raised to the power $k$. They do not use the same step-and-measure pairing: $2/(L+\mu)$ is attached here to squared distance, while $1/L$ is attached to objective gap. Exchanging those pairings would change the stated guarantees.

The bounds also explain the role of conditioning without promising identical observed histories. Since $\mu/L=1/\kappa$, a large condition number makes $1-\mu/L$ closer to one. Similarly, $(\kappa-1)/(\kappa+1)$ approaches one as $\kappa$ grows. These observations interpret the displayed formulas; they do not remove any hypothesis.

For a numerical reading exercise, suppose only for the purpose of evaluating the formulas that an objective satisfies the required assumptions with $L=4$ and $\mu=1$. Then $\kappa=4$. The distance factor inside the power for the $2/(L+\mu)$ step is $3/5$, and the bound raises it to $2k$. For the $1/L$ step, the objective-gap factor is $1-1/4=3/4$, raised to $k$. These two numbers should not be compared as though they bound the same quantity: one multiplies an initial squared distance and the other multiplies an initial objective gap. The exercise is about pairing each formula with its measure and step, not predicting the exact values that an iteration table must display.

The convex result has a different reading pattern. If the assumptions hold, choosing an iteration count $k$ places the objective gap below the displayed fraction. Increasing $k$ enlarges only the denominator in that expression, while the initial distance and $L$ remain in the numerator. This is a guarantee on an upper bound, not an equality describing every run. An observed objective may fall faster, but that observation does not alter the stated $O(1/k)$ result or weaken the need for its hypotheses.

For an engineering calculation, the boundary is as important as the rate. Not every energy or calibration objective is convex, let alone strongly convex. A stationary point need not be a physical optimum, and gradient descent is not universally appropriate for engineering design. If the stated structure has not been established, these particular global convergence bounds cannot simply be transferred because an iteration table appears to decrease. The table is evidence about one computation; the theorem is a conditional statement about an entire class of objectives.

<!-- section: SEC-06 -->
## Choosing a step by Armijo backtracking

A known smoothness constant may be unavailable even when we can evaluate the objective and gradient. Armijo backtracking is a bounded practical alternative for selecting the step within gradient descent. Choose an initial trial step $\bar\alpha>0$, a contraction factor $\eta\in(0,1)$, and a constant $c\in(0,1)$. For the current iterate $x_k$, find the smallest integer $m\ge0$ such that

$$
\alpha_k=\eta^m\bar\alpha
$$

satisfies

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)
\le
f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
$$

The procedure starts with $m=0$, tests the initial trial step, and increases $m$ only after rejection. Because $0<\eta<1$, each rejection contracts the trial step. Acceptance uses a sufficient-decrease inequality with the squared Euclidean norm of the current gradient. The inequality direction and the squared norm are part of the rule, and “smallest” means the first accepted member of the sequence $\bar\alpha,\eta\bar\alpha,\eta^2\bar\alpha,\ldots$.

Trace the first search in the program to see the smallest-integer rule. At $x_0=(2,-1)$, the objective is $4$, the gradient is $(2,-4)$, and its squared norm is $20$. With the initial trial step $1$, the proposed point is $(0,3)$ and its objective is $18$, so the sufficient-decrease test fails. The next trial uses $m=1$ and $\alpha=0.5$. Its proposed point is $(1,1)$ with objective $2.5$, which satisfies the displayed test for the chosen $c$. The algorithm therefore accepts $m=1$; it does not continue contracting after the first successful trial.

This final program applies that rule to the same idealized quadratic objective. It is self-contained: it defines the objective, gradient, parameters, backtracking loop, and gradient-descent update. The printed value of $m$ exposes how each accepted step was obtained.

```python
import numpy as np

def objective(x):
    return 0.5 * (x[0] ** 2 + 4.0 * x[1] ** 2)

def gradient(x):
    return np.array([x[0], 4.0 * x[1]], dtype=float)

x = np.array([2.0, -1.0])
bar_alpha = 1.0
eta = 0.5
c = 1.0e-4

print(" k          f(x)   m      alpha      ||grad||")
for k in range(8):
    g = gradient(x)
    m = 0
    alpha = bar_alpha
    while objective(x - alpha * g) > objective(x) - c * alpha * np.dot(g, g):
        m += 1
        alpha = (eta ** m) * bar_alpha
    print(f"{k:2d}  {objective(x):12.7f}  {m:2d}  {alpha:9.6f}  {np.linalg.norm(g):10.6f}")
    x = x - alpha * g
```

The constant-step and backtracking versions share the same core iteration: both subtract a positive multiple of the gradient evaluated at the current point. They differ only in how that multiple is selected. A disciplined reading therefore keeps the full chain visible: define the unconstrained differentiable objective, compute the current gradient, choose the step by a stated rule, update, and interpret any convergence claim only under its accompanying smoothness and convexity assumptions.
