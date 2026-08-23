# Gradient Descent: Assumptions, Rates, and Step Selection

Gradient descent is a first-order method for solving an unconstrained optimisation problem. The central idea is simple: use the gradient at the current point to choose a direction in which the objective decreases locally, then decide how far to move. The interesting mathematics is not only the update itself. It is the chain of assumptions that turns a local direction into a useful descent guarantee and, under stronger structure, into a convergence rate.

This lesson develops that chain analytically. We will distinguish necessary stationarity from sufficient optimality, track the role of smoothness in controlling curvature-like behaviour without introducing a second-order method, and compare convex and strongly convex guarantees. A short implementation makes the index and sign conventions explicit. Throughout, a displayed inequality should be read together with its hypotheses; changing the assumptions changes what may be concluded.

<!-- section: SEC-01 -->
## 1. The optimisation objective and first-order stationarity

The unconstrained problem is

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where $f:\mathbb{R}^d\to\mathbb{R}$ is at least continuously differentiable, so $f\in C^1$. The variable is a vector, and the objective assigns one real number to each vector. “Unconstrained” means that every vector in $\mathbb{R}^d$ is an admissible candidate; no equality or inequality constraints are part of this problem statement.

Suppose that $x^*$ is a local minimiser and that $f$ is differentiable at $x^*$. A necessary first-order condition is

$$
\nabla f(x^*)=0.
$$

The word necessary matters. Every differentiable local minimiser is stationary, but the equation $\nabla f(x)=0$ by itself does not say that $x$ is a minimum. A stationary point can have another local character, and deciding more would require additional assumptions or information. Gradient descent therefore seeks points where the gradient becomes small, while the interpretation of such a point depends on the structure of $f$.

For a one-dimensional picture, if $f'(x)>0$, increasing $x$ initially increases the objective, so moving in the negative direction is locally appropriate. If $f'(x)<0$, the positive direction is locally appropriate. In several dimensions, the gradient collects these directional rates, and $-\nabla f(x)$ is the corresponding first-order descent direction whenever the gradient is nonzero. This motivates the update developed next, but it does not yet provide a step-size guarantee.

<!-- section: SEC-02 -->
## 2. The gradient-descent update

Choose an initial point $x_0\in\mathbb{R}^d$ and positive step sizes $\alpha_k$. Standard gradient descent evaluates the gradient at the current iterate and uses

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),\qquad k=0,1,2,\ldots.
$$

The subtraction sign is essential: the method moves opposite to the current gradient. The gradient is evaluated at $x_k$, not at a future or look-ahead point. The scalar $\alpha_k>0$ controls the length of the move, while the vector $\nabla f(x_k)$ controls its direction and scale.

To see the mechanics, consider the quadratic objective

$$
f(x)=\tfrac12 x^\mathsf{T}Ax,
$$

with $A=\operatorname{diag}(1,4)$ and $x_0=(2,1)^\mathsf{T}$. Its gradient is $\nabla f(x)=Ax$. With a chosen constant step $\alpha=0.2$, one iteration is obtained by evaluating $Ax_0$, multiplying by $0.2$, and subtracting the result from $x_0$. This is a trace of the rule, not a new convergence claim. A numerical implementation should make the same operations visible.

```python
import numpy as np

A = np.diag([1.0, 4.0])
x = np.array([2.0, 1.0])
alpha = 0.2

for k in range(5):
    value = 0.5 * x @ A @ x
    gradient = A @ x
    print(f"k={k}, x={x}, f(x)={value:.6f}, grad={gradient}")
    x = x - alpha * gradient
```

The block is self-contained: it fixes its matrix, initial vector, step, and computation. In general, implementation diagnostics should record objective values, gradient norms, and iterates so that a suspected sign or step-size error can be distinguished from a property of the objective. Such diagnostics do not replace the assumptions behind a theorem.

<!-- section: SEC-03 -->
## 3. Smoothness, the descent bound, and constant steps

A useful control condition is $L$-smoothness. A continuously differentiable function $f:\mathbb{R}^d\to\mathbb{R}$ is $L$-smooth for $L>0$ when its gradient is Lipschitz with respect to the Euclidean norm:

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|,
\qquad \forall x,y\in\mathbb{R}^d.
$$

This is a statement about changes in the gradient, not a statement that the function values themselves are Lipschitz. It supplies a global upper control on how much the objective can rise away from a linear approximation. Specifically, the Descent Lemma says that, for an $L$-smooth function and all $x,y\in\mathbb{R}^d$,

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle+\frac{L}{2}\|y-x\|^2.
$$

The inequality is an upper bound. Substituting the gradient-descent trial point $y=x-\alpha\nabla f(x)$ gives

$$
f(y)\leq f(x)-\alpha\|\nabla f(x)\|^2+\frac{L\alpha^2}{2}\|\nabla f(x)\|^2.
$$

Thus the linear decrease is balanced against a nonnegative quadratic term. A suitable step can make the resulting right-hand side no larger than $f(x)$. The conclusion is conditional on $L$-smoothness and on the selected step; it is not a universal statement about every differentiable objective.

One constant-step rule is $\alpha_k=\alpha$. When $L$ is known, a common choice is $\alpha=1/L$. Under the usual smooth-convex assumptions, another stated range is $\alpha\in(0,2/L)$. The qualifier belongs to the interval: it must not be detached from its assumptions. If $L$ is estimated poorly, a nominally reasonable numerical step can behave differently from the theorem's setting, which is why recording objective and gradient diagnostics is useful.

<!-- section: SEC-04 -->
## 4. Convexity, strong convexity, and conditioning

Smoothness controls changes in the gradient. Convexity supplies a global lower-bound geometry. A differentiable function is convex when, for every $x,y\in\mathbb{R}^d$,

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle.
$$

The tangent plane is therefore a global lower bound. This is stronger than merely knowing that a particular point is stationary. In a convex problem, a global minimiser can be related to the first-order geometry in a way that supports objective-gap analysis.

Strong convexity adds quantitative curvature through a positive parameter $\mu>0$. A differentiable function is $\mu$-strongly convex when, for all $x,y\in\mathbb{R}^d$,

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle+\frac{\mu}{2}\|y-x\|^2.
$$

The extra term is positive and quadratic. It is not optional notation: its coefficient is $\mu/2$, and the inequality remains a lower bound. Strong convexity is a stronger assumption than convexity and is precisely the additional structure used for the selected linear-rate result.

When $f$ is both $L$-smooth and $\mu$-strongly convex, its condition number is

$$
\kappa=\frac{L}{\mu}\geq 1.
$$

The ratio compares the upper gradient-variation scale with the lower curvature scale. A large $\kappa$ indicates that the two scales are far apart, so the rate expressions will contract more slowly. This interpretation is about the stated bounds; it does not assert that every application objective is convex, strongly convex, or globally well-conditioned.

<!-- section: SEC-05 -->
## 5. Convergence guarantees and their boundaries

First consider the convex case. Let $f:\mathbb{R}^d\to\mathbb{R}$ be $L$-smooth and convex, let $x^*$ be a global minimiser, and use the constant step $\alpha_k=1/L$. Then, for $k\geq1$,

$$
f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k}.
$$

The objective gap has an $O(1/k)$ upper bound. Every hypothesis is active: smoothness provides the relevant upper control, convexity provides the global first-order structure, $x^*$ is a global minimiser, and the step is $1/L$. The bound does not say that an arbitrary differentiable objective has this rate, nor does it turn a local stationarity statement into a global result.

Now add $\mu$-strong convexity. For an $L$-smooth, $\mu$-strongly convex function, the selected distance contraction uses

$$
\alpha=\frac{2}{L+\mu}
$$

and satisfies

$$
\|x_k-x^*\|^2\leq
\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}
\|x_0-x^*\|^2.
$$

The corresponding objective-gap contraction uses a different step, $\alpha=1/L$:

$$
f(x_k)-f(x^*)\leq
\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).
$$

Do not exchange these step-size pairings. Both results require the smoothness and strong-convexity assumptions, and the condition number appears in the distance factor. The word “linear” describes geometric decay in the iteration count under this structure; it is not a claim that an unrestricted nonconvex problem behaves globally in the same way.

It is useful to compare the two convexity statements directly. Ordinary convexity says that the graph lies above each of its tangent planes. If the tangent plane at $x$ is evaluated at another point $y$, the difference between the objective and that plane is allowed to be zero. Strong convexity requires at least the additional quadratic amount $\frac{\mu}{2}\|y-x\|^2$. Consequently, the strong version records a quantitative separation away from the tangent plane, whereas the ordinary version records only a nonnegative separation. This is why a strong-convexity parameter can enter a geometric rate while convexity alone leads to the displayed reciprocal-iteration bound.

The condition number makes the pairing of assumptions and rates more interpretable. Since $\kappa=L/\mu$, a large upper gradient scale relative to the lower curvature scale produces a factor closer to one in the strong-convexity contraction. The formula does not say that one can improve the rate merely by labelling a problem well-conditioned. It says that, once the two constants and their hypotheses are established, the numerical value of the factor can be assessed. In an analysis, report which constants are known, how they were obtained, and which step-size case is being used rather than quoting a rate without its data.

A small symbolic check also prevents common substitutions. If the distance bound is being used, the step is $2/(L+\mu)$ and the factor is $((\kappa-1)/(\kappa+1))^{2k}$. If the objective-gap bound is being used, the step is $1/L$ and the factor is $(1-\mu/L)^k$. These are two separate statements. Neither formula authorises replacing $\mu$ by zero while retaining the same conclusion, because strong convexity is then no longer available. Similarly, a decreasing sequence of computed values is evidence about that run, not a proof that the corresponding global assumptions hold.

To interpret a rate, examine its hypotheses before its exponent. A slowly decreasing bound can reflect conditioning, while failure to meet convexity or strong convexity means that the displayed theorem is simply not the applicable guarantee. This assumption-to-conclusion discipline is more reliable than inferring global behaviour from a few decreasing numerical values.

<!-- section: SEC-06 -->
## 6. Armijo backtracking and a final synthesis

A constant step requires a usable choice of scale. Armijo backtracking provides a bounded practical alternative. Choose an initial trial step $\bar{\alpha}>0$, a contraction factor $\eta\in(0,1)$, and $c\in(0,1)$. At iteration $k$, test steps of the form

$$
\alpha_k=\eta^m\bar{\alpha},\qquad m=0,1,2,\ldots,
$$

and choose the smallest nonnegative integer $m$ for which

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)
\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
$$

The accepted step is therefore the first contracted trial that satisfies the sufficient-decrease inequality. The right side contains the squared Euclidean norm of the current gradient. The inequality direction matters: the trial objective must be no greater than the specified decrease target. Backtracking changes how the step is selected; it does not change the gradient-descent direction or introduce a new second-order method.

The smallest-$m$ requirement is part of the procedure, not merely an implementation preference. Starting from $m=0$ tests the original trial $\bar{\alpha}$. If it fails, multiplying by $\eta\in(0,1)$ contracts the step; repeated contractions give $\eta^m\bar{\alpha}$. The acceptance test then compares the actual objective at the candidate with a target that demands a decrease proportional to $\alpha_k\|\nabla f(x_k)\|^2$. A code implementation should recompute the candidate and objective for each new $m$, rather than changing the stored iterate before acceptance. Otherwise it would no longer be testing the stated trial points.

Backtracking is especially useful when a reliable value of $L$ is unavailable in practice, but its use should not be overinterpreted. The rule specifies how to accept a step at the current iterate. It does not by itself add convexity, strong convexity, or a convergence theorem to an objective. If a report uses a theorem involving $1/L$, it must still identify the smoothness constant and the theorem's other hypotheses, even if a separate experiment used Armijo steps. The practical procedure and the fixed-step analysis answer related but distinct questions.

There are several simple termination checks worth separating. A small gradient norm indicates approximate stationarity, but stationarity alone is only a necessary condition for a differentiable local minimiser. A small change in the iterate indicates that the chosen step has become small, but it does not identify the objective's global geometry. A small change in objective value is another numerical diagnostic, not a substitute for the assumptions of a rate theorem. In floating-point computation, these checks should be recorded with their tolerances and iteration limits so that a reported stopping point can be interpreted reproducibly.

```python
import numpy as np

def f(x):
    return 0.5 * (x[0] ** 2 + 4.0 * x[1] ** 2)

def grad_f(x):
    return np.array([x[0], 4.0 * x[1]])

x = np.array([2.0, 1.0])
eta = 0.5
c = 0.25
trial_step = 1.0

g = grad_f(x)
m = 0
while True:
    alpha = (eta ** m) * trial_step
    candidate = x - alpha * g
    if f(candidate) <= f(x) - c * alpha * np.linalg.norm(g) ** 2:
        break
    m += 1

print("accepted step:", alpha)
print("candidate:", candidate)
print("sufficient decrease:", f(candidate) <= f(x) - c * alpha * np.linalg.norm(g) ** 2)
```

The full chain is now visible. First formulate the unconstrained objective and remember that differentiable local minima are stationary. Then compute the current-iterate gradient and subtract a positive multiple. Next identify whether $L$-smoothness supports the Descent Lemma and whether the step is justified. Finally check whether convexity or strong convexity is available before interpreting an objective-gap or distance rate. Armijo backtracking supplies a practical sufficient-decrease test when a fixed scale is inconvenient, but its acceptance condition is still an explicit mathematical assumption about the chosen trial.

For a final diagnostic exercise, take any proposed gradient-descent claim and write it as two columns: assumptions and conclusion. Place $f\in C^1$, smoothness, convexity, strong convexity, the minimiser condition, and the step-size rule only where they are actually required. Then trace one update by hand and compare it with recorded objective and gradient values. If a conclusion cannot be supported by the assumptions in the left column, weaken the conclusion rather than silently adding an assumption. That habit is the main safeguard against confusing a useful local direction, a descent inequality, and a convergence theorem.

One worked reasoning pattern is as follows. Begin with a proposed point $x_k$ and compute $g_k=\nabla f(x_k)$. The trial point is $x_k-\alpha_k g_k$; it is not $x_k+\alpha_k g_k$, and it is not formed from a gradient evaluated after the move. If the objective is known to be $L$-smooth, use the Descent Lemma to place an upper bound on the trial value. If the step is $1/L$, a convex objective with a global minimiser falls under the stated $O(1/k)$ result. If strong convexity is additionally established, decide whether the desired statement is the distance contraction with $2/(L+\mu)$ or the objective contraction with $1/L$. Each choice determines the formula that may be cited.

A second reasoning pattern concerns a failed claim. Suppose an objective is differentiable and a computation reaches a point with a small gradient. The valid immediate interpretation is approximate first-order stationarity. It is not automatically valid to call the point a global minimiser, invoke the convex objective-gap bound, or report the strong-convexity contraction. To make one of those stronger conclusions, supply the corresponding global assumptions and the correctly qualified step size. If those assumptions are unavailable, describe the numerical observation without upgrading it to a theorem.

The same discipline applies to examples. A quadratic objective is convenient for tracing vector arithmetic, but the trace demonstrates the update rule only. It does not establish that every objective has the quadratic's geometry. An application may motivate why minimising an objective is useful, but it must not silently turn a differentiable objective into a convex one. Keeping the example's purpose explicit preserves the distinction between representation and authority: an example illustrates a selected rule, while the assumptions determine its mathematical consequence.