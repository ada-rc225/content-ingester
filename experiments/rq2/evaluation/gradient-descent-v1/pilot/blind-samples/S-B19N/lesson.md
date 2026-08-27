# Gradient Descent: From an Update Rule to Convergence Guarantees

<!-- section: SEC-01 -->
## The optimisation problem and stationary points

Gradient descent addresses the unconstrained optimisation problem

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where the objective $f:\mathbb{R}^d\to\mathbb{R}$ is at least continuously differentiable, written $f\in C^1$. A point $x$ is a vector of $d$ decision variables, while $f(x)$ is the scalar value to be made as small as possible. “Unconstrained” is important: every vector in $\mathbb{R}^d$ is eligible. Adding restrictions on $x$ would define a different problem.

Differentiability gives a local description of how the objective changes. The gradient

$$
\nabla f(x)=
\begin{bmatrix}
\frac{\partial f}{\partial x_1}(x)&\cdots&\frac{\partial f}{\partial x_d}(x)
\end{bmatrix}^{\!T}
$$

collects the first partial derivatives at $x$. It therefore provides the first-order information used throughout this lesson.

Suppose $x^*$ is a local minimiser and $f$ is differentiable at $x^*$. A necessary first-order condition is

$$
\nabla f(x^*)=0.
$$

Such a point is called stationary. The logical direction matters: a differentiable local minimiser must be stationary, but stationarity alone is not sufficient to establish that a point is a minimum. For example, the one-dimensional function $f(x)=x^3$ has derivative zero at $x=0$, yet values immediately to the left are smaller and values immediately to the right are larger. The first-order condition identifies candidates; it does not, by itself, classify them.

The word “local” also deserves attention. A local minimiser is no worse than nearby eligible points, whereas the optimisation problem asks for a point whose value is no worse than that of any eligible point when a global solution is available. The necessary stationarity statement applies to a differentiable local minimiser, so it also applies to a differentiable global minimiser. Its converse is still unavailable without further structure. Keeping these statements separate prevents two common logical jumps: treating every stationary point as a minimiser, or treating a merely local comparison as a global conclusion. At this stage, continuous differentiability provides the gradient and the necessary condition, but it supplies neither a classification of every stationary point nor a convergence guarantee for a sequence.

This motivates an iterative method. Rather than trying to solve the stationary equation in a single symbolic step, gradient descent repeatedly uses the gradient at the current point to choose a new point. Before discussing whether those points converge, we first need to state the update precisely.

<!-- section: SEC-02 -->
## Following the negative gradient

Choose an initial point $x_0\in\mathbb{R}^d$ and positive step sizes $\alpha_k$. Gradient descent generates a sequence by

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),
\qquad k=0,1,2,\ldots.
$$

Three details define the rule. The gradient is evaluated at the current iterate $x_k$, the gradient term is subtracted, and the step size is positive. The vector $-\nabla f(x_k)$ supplies the direction, while $\alpha_k$ scales the displacement. The new point then becomes the current point for the next iteration.

It is helpful to read the subscripts as a timeline. At index zero, the method knows the chosen starting point, evaluates its gradient, and forms the point with index one. At index one, it discards neither the new location nor its changed gradient: it evaluates the gradient at that current location to form the point with index two. Thus the sequence is linked, but each update is fully determined by the present iterate and its corresponding positive step size. Replacing the subtraction by addition would change the stated rule. Likewise, inserting the newly proposed point into the gradient before the update had been completed would no longer be the current-iterate formula given here.

Consider the one-dimensional objective $f(x)=\tfrac12(x-3)^2$, whose derivative is $f'(x)=x-3$. Starting from $x_0=-1$ with the constant positive step $\alpha_k=0.25$, the first update is

$$
x_1=-1-0.25(-1-3)=0.
$$

The next update uses the derivative at this new current point, not the derivative previously calculated at $x_0$:

$$
x_2=0-0.25(0-3)=0.75.
$$

The following self-contained program traces the same rule in two dimensions. It stores each current iterate and objective value before applying the update, so the printed rows correspond directly to the index $k$.

```python
import numpy as np

def objective(x):
    return 0.5 * ((x[0] - 3.0) ** 2 + 2.0 * (x[1] + 1.0) ** 2)

def gradient(x):
    return np.array([x[0] - 3.0, 2.0 * (x[1] + 1.0)])

x = np.array([-1.0, 2.0])
alpha = 0.25

for k in range(6):
    print(f"k={k}, x={x}, f(x)={objective(x):.6f}")
    x = x - alpha * gradient(x)
```

This trace illustrates the mechanics, but it is not yet a general convergence argument. To justify when a step decreases an objective and to connect a constant step to convergence, we need a property that controls how rapidly the gradient can change.

<!-- section: SEC-03 -->
## Smoothness, descent, and a constant step

A continuously differentiable function is $L$-smooth, for some $L>0$, when its gradient is $L$-Lipschitz with respect to the Euclidean norm:

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|,
\qquad \forall x,y\in\mathbb{R}^d.
$$

This is a bound on differences between gradients, not a claim that the function values themselves are Lipschitz. It says that changing the input by a given Euclidean distance cannot change the gradient by more than $L$ times that distance.

Every part of the definition carries information. The same positive constant must work for every pair of points in the whole domain, and both norms are Euclidean. A smaller separation between two inputs forces a proportionally smaller upper bound on the difference between their gradients. The definition does not say that the gradients are equal, only that their difference is controlled. Nor does it place an upper bound directly on the size of a single gradient. Its role here is more specific: it lets information evaluated at one point control the possible objective value at another point through the quadratic upper bound that follows.

The key consequence is the Descent Lemma. If $f$ is $L$-smooth, then for every $x,y\in\mathbb{R}^d$,

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle
+\frac{L}{2}\|y-x\|^2.
$$

The right-hand side is a quadratic upper bound on $f(y)$ built from information at $x$. The linear inner-product term records the first-order change, and the positive quadratic term allows for the gradient to vary between the two points.

Read this as a one-sided guarantee rather than an exact prediction. The actual value at the second point can lie below the displayed right-hand side; the lemma only prevents it from lying above that bound under smoothness. The order of the two points also matters to the expression: the objective and gradient in the linear model are evaluated at the base point, while the displacement points from the base point to the candidate point. The coefficient of the squared displacement is one half of the smoothness constant. Reversing the inequality or changing that coefficient would produce a different statement.

Now substitute one gradient-descent step, $y=x-\alpha\nabla f(x)$, into this bound. Since $y-x=-\alpha\nabla f(x)$, we obtain

$$
\begin{aligned}
f\bigl(x-\alpha\nabla f(x)\bigr)
&\leq f(x)-\alpha\|\nabla f(x)\|^2
+\frac{L\alpha^2}{2}\|\nabla f(x)\|^2\\
&=f(x)-\alpha\left(1-\frac{L\alpha}{2}\right)
\|\nabla f(x)\|^2.
\end{aligned}
$$

This calculation makes the role of the step size visible. In particular, choosing $\alpha=1/L$ gives

$$
f\left(x-\frac1L\nabla f(x)\right)
\leq f(x)-\frac{1}{2L}\|\nabla f(x)\|^2.
$$

Thus, under $L$-smoothness, this step cannot increase the objective, and it gives a strict decrease whenever the current gradient is nonzero. The conclusion is tied to the smoothness assumption; the update formula alone does not supply it.

A constant-step version of gradient descent sets $\alpha_k=\alpha$ for every iteration. When $L$ is known, a common choice is $\alpha=1/L$. Under the usual smooth convex assumptions, another standard range is

$$
0<\alpha<\frac{2}{L}.
$$

This interval must retain that qualification; it is not a universal rule for every differentiable objective. Notice also that a decrease statement concerns consecutive objective values, whereas a convergence-rate statement compares an iterate with an optimum. Establishing the latter requires additional global structure.

<!-- section: SEC-04 -->
## Convexity, strong convexity, and conditioning

For a differentiable function, convexity can be expressed as a global first-order lower bound. The function $f$ is convex when, for all $x,y\in\mathbb{R}^d$,

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle.
$$

Unlike the smoothness upper bound, this inequality places the function above its linear approximation at every $x$. It also clarifies the value of stationarity in this setting. If $\nabla f(x)=0$, the inequality reduces to $f(y)\geq f(x)$ for every $y$, so a stationary point of a differentiable convex function is a global minimiser.

Strong convexity adds a positive quadratic term. For $\mu>0$, a differentiable function is $\mu$-strongly convex when, for every $x,y\in\mathbb{R}^d$,

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle
+\frac{\mu}{2}\|y-x\|^2.
$$

The coefficient is exactly $\mu/2$, and the squared-norm term has a positive sign. Dropping that term recovers the convex lower bound, but retaining it supports a stronger convergence conclusion.

These two definitions can be compared without changing their scope. The convex inequality requires every function value to stay above a global linear lower model. Strong convexity requires it to stay above that same linear model plus a nonnegative quadratic amount, with a strictly positive parameter. Consequently, the strong condition includes the convex lower bound, while recording additional separation as the two points move apart. Both are global statements because they quantify over every pair of points. This differs from the earlier necessary condition, which concerned the gradient at a particular local minimiser. The global inequalities are what allow local first-order information to support conclusions about a global minimiser in the guarantees that follow.

When an objective is both $L$-smooth and $\mu$-strongly convex, its condition number is

$$
\kappa=\frac{L}{\mu}\geq 1.
$$

The ratio is $L$ divided by $\mu$, not its reciprocal. It combines the upper control on gradient variation with the lower curvature-like control supplied by strong convexity. In the convergence factors below, a larger $\kappa$ produces a factor closer to one, so more iterations may be needed to obtain the same reduction promised by those bounds.

<!-- section: SEC-05 -->
## Convergence guarantees and their limits

We can now distinguish two guarantees. They measure different quantities and depend on different assumptions, so each formula should be read together with its conditions.

First suppose that $f:\mathbb{R}^d\to\mathbb{R}$ is $L$-smooth and convex, that a global minimiser $x^*$ exists, and that gradient descent uses the constant step $\alpha_k=1/L$. Then, for every $k\geq1$,

$$
f(x_k)-f(x^*)
\leq
\frac{L\|x_0-x^*\|^2}{2k}.
$$

The left-hand side is the objective gap: it compares the value reached at iteration $k$ with the globally minimal value. The numerator on the right records the smoothness constant and the squared initial distance to a minimiser. The factor $1/k$ gives a sublinear rate: the stated upper bound shrinks inversely with the iteration index. It does not say that the iterate reaches $x^*$ after a fixed finite number of steps.

The inequality is an upper bound, not a formula for the exact gap at every iteration. A particular run may have a smaller gap, but the theorem guarantees no more than the displayed quantity from these assumptions. The initial point appears only through its squared distance from the chosen global minimiser: a larger initial distance makes this stated upper bound larger. The conclusion concerns function values rather than the distance between the iterate and the minimiser. That distinction matters because the left side and right side should be interpreted in the quantity the theorem actually controls. The step, smoothness, convexity, existence of the minimiser, and restriction to positive iteration indices are all part of the single statement.

Strong convexity permits geometric, often called linear, contraction. Suppose instead that $f$ is both $L$-smooth and $\mu$-strongly convex. With the constant step

$$
\alpha=\frac{2}{L+\mu},
$$

gradient descent satisfies the squared-distance bound

$$
\|x_k-x^*\|^2
\leq
\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}
\|x_0-x^*\|^2,
\qquad \kappa=\frac{L}{\mu}.
$$

Here the quantity being controlled is distance to the minimiser. The contraction factor is raised to $2k$, so the bound decreases geometrically when the stated assumptions hold.

There is a second strongly convex statement with a different step and a different measured quantity. With $\alpha=1/L$, the objective gap obeys

$$
f(x_k)-f(x^*)
\leq
\left(1-\frac{\mu}{L}\right)^k
\bigl(f(x_0)-f(x^*)\bigr).
$$

Because $\mu/L=1/\kappa$, the factor becomes closer to one as the condition number grows. This is the precise sense in which conditioning affects this guarantee: it appears directly in the contraction factor.

Geometric contraction means that the preceding upper-bound scale is multiplied repeatedly by a fixed factor through the power indexed by the iteration count. It should not be confused with the inverse dependence on the index in the general convex result. The two strongly convex formulas also begin from different initial errors: one starts with squared distance and the other with objective gap. They therefore answer different questions even though both express geometric reduction. Comparing them requires preserving those measured quantities, not just comparing the symbols in their factors. In both cases, the additional strong-convexity hypothesis is essential to the stated form of the guarantee.

Keep the pairings straight. The step $2/(L+\mu)$ accompanies the squared-distance contraction involving $((\kappa-1)/(\kappa+1))^{2k}$. The step $1/L$ accompanies the objective-gap contraction involving $(1-\mu/L)^k$. Neither strongly convex bound should be detached from $L$-smoothness and $\mu$-strong convexity, and the general convex $1/k$ result additionally states the existence of a global minimiser and uses its own $1/L$ step.

These are conditional guarantees, not conclusions about every differentiable function or every positive step. If a hypothesis or the paired step choice is absent, these particular bounds do not follow from the statements given here. This boundary is useful in practice: before interpreting an observed trace through one of these rates, identify the quantity being plotted, the assumptions being invoked, and the step used by the update.

<!-- section: SEC-06 -->
## Choosing a step by Armijo backtracking

A constant step such as $1/L$ relies on a usable value of $L$. Armijo backtracking is a bounded alternative for selecting the step at the current iterate. Choose an initial trial step $\bar\alpha>0$, a contraction factor $\eta\in(0,1)$, and a constant $c\in(0,1)$. Consider trial steps

$$
\alpha_k=\eta^m\bar\alpha,
\qquad m=0,1,2,\ldots.
$$

Starting with $m=0$, find the smallest nonnegative integer for which

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)
\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
$$

The left side evaluates the objective at the candidate gradient-descent point. The right side requires sufficient decrease relative to the current value, scaled by the trial step and the squared Euclidean norm of the current gradient. If the inequality fails, increasing $m$ by one multiplies the trial step by $\eta$, making it smaller. Once the first acceptable $m$ is found, the ordinary update uses that accepted positive step.

The phrase “smallest nonnegative integer” fixes the search order. The uncontracted trial is checked first. Only after it fails is the once-contracted trial checked, followed if necessary by successive contractions. Accepting a later trial while an earlier one already satisfied the inequality would not implement this rule. The gradient and its squared norm remain those of the current iterate throughout these tests; what changes is the trial step and therefore the candidate point. The accepted value becomes the step for that iteration, so the final move still has exactly the gradient-descent update form.

This self-contained implementation exposes both the smallest-$m$ search and the subsequent update. Each outer iteration begins again from the same chosen initial trial step, and every value needed by the block is defined locally.

```python
import numpy as np

def objective(x):
    return 0.5 * (x[0] ** 2 + 4.0 * x[1] ** 2)

def gradient(x):
    return np.array([x[0], 4.0 * x[1]])

x = np.array([2.0, -1.0])
bar_alpha = 1.0
eta = 0.5
c = 0.25

for k in range(5):
    g = gradient(x)
    m = 0
    alpha = (eta ** m) * bar_alpha
    while objective(x - alpha * g) > objective(x) - c * alpha * np.dot(g, g):
        m += 1
        alpha = (eta ** m) * bar_alpha
    x = x - alpha * g
    print(f"k={k}, m={m}, alpha={alpha:.6f}, x={x}, f(x)={objective(x):.6f}")
```

Backtracking changes step selection, not the gradient-descent direction: the gradient is still evaluated at $x_k$ and subtracted. It also uses an acceptance inequality rather than silently assuming that any positive trial step is suitable. Across the lesson, the logical progression is now complete: formulate the unconstrained differentiable problem, apply the current-gradient update, use smoothness to understand descent and constant steps, add convex structure for rate statements, and use Armijo backtracking when selecting a step through sufficient-decrease tests.
