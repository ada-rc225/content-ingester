# Gradient Descent: From an Update Rule to Conditional Guarantees

Gradient descent is an iterative method for changing a vector of parameters so that a differentiable objective becomes smaller. In computer science, the objective might be presented as a loss, and each iterate can be treated as the current program state. That viewpoint is useful for tracing the algorithm, but it has a firm boundary: a small educational loss is not a model of every production training objective, and basic full-batch gradient descent is not a complete training system.

This lesson builds the method in dependency order. We will first state the optimisation problem and the stationarity condition that motivates the target. We will then implement the update, identify assumptions that support decrease, distinguish convex from strongly convex structure, interpret two convergence guarantees, and finally implement a step-selection rule for cases where a suitable constant is not supplied.

<!-- section: SEC-01 -->
## The optimisation problem and what stationarity tells us

Let the decision variable be a vector $x\in\mathbb{R}^d$. The unconstrained problem is

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where $f:\mathbb{R}^d\to\mathbb{R}$ is at least continuously differentiable, written $f\in C^1$. “Unconstrained” matters: every vector in $\mathbb{R}^d$ is in the domain of the minimisation. Adding a requirement such as nonnegative coordinates would define a different problem.

For a computer-science interpretation, $x$ can represent a program’s current parameter vector, while $f(x)$ is a scalar loss returned by evaluating those parameters. The mathematical problem only says to minimise a differentiable scalar function over all of $\mathbb{R}^d$; it does not assert that a real machine-learning loss has any of the stronger structure introduced later.

Suppose $x^*$ is a local minimizer and $f$ is differentiable at $x^*$. A necessary first-order condition is

$$
\nabla f(x^*)=0.
$$

The gradient collects the partial derivatives, so the zero vector means there is no first-order change indicated in any coordinate direction. The direction of the implication is important. A differentiable local minimum must be stationary, but a stationary point is not automatically a minimum without additional assumptions. Thus a zero-gradient check is evidence that the first-order method has reached a stationary point; on its own, it is not a certificate of the kind of point reached.

It helps to separate three questions that can otherwise become blurred. The optimisation problem asks which vector gives the smallest objective value. The stationarity equation identifies vectors that meet a necessary first-order condition for being a local minimum. An iterative algorithm describes how to generate candidate vectors from an initial state. These are related, but they are not equivalent. Writing down the problem does not say that an algorithm will find a solution, and observing a small gradient does not erase the conditions needed to interpret it. This separation is similar to distinguishing a program’s specification, a testable invariant, and an execution trace: each supplies different information.

As a small traceable objective, consider

$$
f(x)=\tfrac12(4x_1^2+x_2^2),
\qquad
\nabla f(x)=(4x_1,x_2).
$$

Solving $\nabla f(x)=0$ gives the candidate $x=(0,0)$. This calculation illustrates the stationarity target. The algorithm still needs a rule for moving from an arbitrary initial vector toward such a target.

<!-- section: SEC-02 -->
## Turning the gradient into an iteration

Choose an initial point $x_0\in\mathbb{R}^d$ and positive step sizes $\alpha_k$. Standard gradient descent applies

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),
\qquad k=0,1,2,\ldots.
$$

At iteration $k$, the gradient is evaluated at the current state $x_k$. The program then subtracts a positive multiple of that gradient to create the next state. Evaluating the gradient at a future or look-ahead point would not be this update, and changing subtraction to addition would reverse its sign.

A useful implementation separates three operations: evaluate the objective for diagnostics, evaluate the gradient at the current vector, and update the vector. The trace below uses the toy objective from the previous section. It records the iteration index, the state before the update, the objective value at that state, and the gradient norm. The code is self-contained, and the explicit copy prevents a later mutation from changing an earlier trace entry.

Read a single loop pass in the same order as the recurrence. At the beginning of the pass, `x` represents $x_k$. The call to `gradient(x)` therefore returns $\nabla f(x_k)$, and all diagnostics on that line describe the same current state. Only the final assignment constructs $x_{k+1}$. This makes the index convention visible and prevents an off-by-one interpretation of the printed record. Positivity of `alpha` is also part of the algorithm’s stated conditions; it is not merely a convenient coding convention.

```python
import numpy as np

def objective(x):
    return 0.5 * (4.0 * x[0] ** 2 + x[1] ** 2)

def gradient(x):
    return np.array([4.0 * x[0], x[1]], dtype=float)

x = np.array([2.0, -3.0], dtype=float)
alpha = 0.2
trace = []

for k in range(6):
    g = gradient(x)
    trace.append((k, x.copy(), objective(x), np.linalg.norm(g)))
    x = x - alpha * g

for k, state, value, grad_norm in trace:
    print(f"k={k}: x={state}, f={value:.6f}, ||grad||={grad_norm:.6f}")
```

The loop implements the recurrence literally: `gradient(x)` is computed before `x` is reassigned. The printed values are a diagnostic trace for this particular objective, initial point, and step size. They do not by themselves establish a general convergence guarantee. To justify why an update should decrease an objective, we need an assumption controlling how rapidly the gradient can change.

When inspecting the output, keep observation and guarantee distinct. You can verify that each displayed state produces the displayed objective and gradient norm, and you can compare consecutive values in this finite run. You cannot generalise those observations to every differentiable function. The next section supplies a named mathematical condition and an upper bound, allowing the relationship between step length and decrease to be stated with its hypotheses rather than inferred from a successful example.

<!-- section: SEC-03 -->
## Smoothness, decrease, and a constant step

A continuously differentiable function is $L$-smooth, for $L>0$, when its gradient is $L$-Lipschitz in the Euclidean norm:

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|,
\qquad \forall x,y\in\mathbb{R}^d.
$$

This condition limits changes in the gradient. It is not a claim that the function values themselves are Lipschitz. Under $L$-smoothness, the Descent Lemma supplies a quadratic upper bound for every $x,y\in\mathbb{R}^d$:

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle
+\frac{L}{2}\|y-x\|^2.
$$

Insert one gradient-descent step, $y=x-\alpha\nabla f(x)$. Then $y-x=-\alpha\nabla f(x)$, so the bound becomes

$$
f(x-\alpha\nabla f(x))
\leq f(x)-\alpha\left(1-\frac{L\alpha}{2}\right)
\|\nabla f(x)\|^2.
$$

This substitution explains the relationship among smoothness, the step, and predicted decrease. In particular, the factor multiplying the squared gradient norm depends on both $L$ and $\alpha$; the assumption must remain attached to the conclusion.

The substitution can be checked term by term. The inner product becomes $-\alpha\|\nabla f(x)\|^2$, because the displacement is the negative gradient scaled by $\alpha$. The squared displacement becomes $\alpha^2\|\nabla f(x)\|^2$. Combining those two contributions gives the displayed coefficient. This is useful when reviewing an implementation or derivation: the gradient must be evaluated at the same current point in both terms, the norm must be squared, and the upper-bound direction must remain unchanged. The conclusion is about the candidate generated by this particular step from $x$, under $L$-smoothness.

A constant-step implementation sets $\alpha_k=\alpha$ at every iteration. When $L$ is known, a common choice is $\alpha=1/L$. Under the usual smooth convex assumptions, the interval $\alpha\in(0,2/L)$ is also a standard constant-step range. The qualification matters: the interval is not a universal instruction for an arbitrary objective.

For the toy objective, use $L=4$ and compare two positive constants. This is a finite diagnostic experiment, not a replacement for the stated assumptions.

```python
import numpy as np

def objective(x):
    return 0.5 * (4.0 * x[0] ** 2 + x[1] ** 2)

def gradient(x):
    return np.array([4.0 * x[0], x[1]], dtype=float)

def run(alpha, steps=6):
    x = np.array([2.0, -3.0], dtype=float)
    values = [objective(x)]
    for _ in range(steps):
        x = x - alpha * gradient(x)
        values.append(objective(x))
    return values

L = 4.0
for alpha in (1.0 / L, 0.4):
    values = run(alpha)
    print(f"alpha={alpha:.2f}: " + ", ".join(f"{v:.6f}" for v in values))
```

Here both constants lie in $(0,2/L)=(0,0.5)$. The output lets you inspect the objective values rather than assuming behaviour from the update syntax alone. The next question is what additional global structure allows decrease to be converted into guarantees about a minimizer.

Notice what the experiment deliberately holds fixed: the objective, initial state, number of updates, and gradient routine. Only the constant step changes. This makes the trace a focused comparison of two allowed constants for this example. Even so, the displayed sequence is evidence about those two runs only. The mathematical range retains its smooth-convex qualification, and the later convergence theorems use their own precisely stated step choices rather than every value in that interval.

<!-- section: SEC-04 -->
## Convexity, strong convexity, and conditioning

For a differentiable convex function, the first-order lower bound

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle,
\qquad \forall x,y\in\mathbb{R}^d,
$$

holds globally. Compare its direction with the Descent Lemma: smoothness gave an upper bound with a quadratic term, while convexity gives a lower bound formed by the value and gradient at $x$. This global lower bound is the structure used by the convex convergence result in the next section.

Strong convexity strengthens that lower bound. A differentiable function is $\mu$-strongly convex, with $\mu>0$, if

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle
+\frac{\mu}{2}\|y-x\|^2,
\qquad \forall x,y\in\mathbb{R}^d.
$$

The positive quadratic term is essential: omitting it, changing its sign, or changing its coefficient would produce a different statement. Strong convexity supports a stronger contraction result than convexity alone.

When an objective is both $L$-smooth and $\mu$-strongly convex, define its condition number as

$$
\kappa=\frac{L}{\mu}\geq 1.
$$

The ratio is $L/\mu$, not its inverse. It places the two constants that control the upper and lower geometry on one scale. A convergence factor written in terms of $\kappa$ therefore exposes how those assumptions interact.

You can organise the definitions by the direction and role of their inequalities. Smoothness compares gradients at two arbitrary points and yields a quadratic upper bound on a function value. Convexity gives a global first-order lower bound. Strong convexity keeps that lower bound and adds a positive squared-distance term. Conditioning is defined only when the smoothness and strong-convexity constants are both available. Reading the definitions in this way prevents a common category error: $L$ and $\mu$ do not appear merely as tunable parameters in code; they belong to explicit properties of the objective.

This hierarchy also disciplines interpretation. Differentiability supports the stationarity condition and the update. Smoothness supplies the upper bound used to reason about a step. Convexity adds a global lower bound, and strong convexity adds a positive quadratic term. Do not silently infer a later property from an earlier one. In particular, calling an objective a “loss” does not establish convexity, strong convexity, or these constants. For real training software, those properties would require separate justification; here they are explicit mathematical hypotheses.

<!-- section: SEC-05 -->
## Reading convergence guarantees as conditional specifications

A convergence bound should be read like a function specification: first check the preconditions, then interpret the output guarantee. For the first result, suppose $f$ is $L$-smooth and convex, $x^*$ is a global minimizer, and gradient descent uses $\alpha_k=1/L$. Then, for every $k\geq1$,

$$
f(x_k)-f(x^*)
\leq
\frac{L\|x_0-x^*\|^2}{2k}.
$$

The left side is the objective gap, not the distance between iterates. The right side depends on the smoothness constant, the squared initial distance to a global minimizer, and $1/k$. This is the stated $O(1/k)$ behaviour. It does not apply merely because a loop uses the gradient-descent update: smoothness, convexity, existence of the global minimizer, the step $1/L$, and $k\geq1$ all belong to the result.

The bound can be used as a reading exercise without turning it into an equality. For fixed $L$, $x_0$, and $x^*$, doubling $k$ halves the right-hand upper bound. The theorem does not say that the observed objective gap must halve exactly, only that it is no larger than the displayed quantity. It also does not say that every iterate is the minimizer after a finite number of steps. This distinction between an upper bound and an exact trace is especially important when program output is available: measured values can sit below a valid bound.

Under the stronger pair of assumptions—$L$-smoothness and $\mu$-strong convexity—two linear contraction statements are available, each paired with its own step size. With

$$
\alpha=\frac{2}{L+\mu},
$$

the squared distance satisfies

$$
\|x_k-x^*\|^2
\leq
\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}
\|x_0-x^*\|^2.
$$

With the different choice $\alpha=1/L$, the objective gap satisfies

$$
f(x_k)-f(x^*)
\leq
\left(1-\frac{\mu}{L}\right)^k
\bigl(f(x_0)-f(x^*)\bigr).
$$

Keep the pairings intact: the distance contraction above belongs with $2/(L+\mu)$, while the objective-gap contraction belongs with $1/L$. The powers of their factors shrink geometrically under the stated assumptions. Because $\mu/L=1/\kappa$, the second factor can also be read as $1-1/\kappa$; this makes the role of conditioning visible without changing the result.

A compact way to audit the two statements is to record four fields: assumptions, step size, measured quantity, and contraction factor. Both statements require smoothness and strong convexity. The first uses $2/(L+\mu)$, measures squared distance to $x^*$, and raises its factor to $2k$. The second uses $1/L$, measures objective gap, and raises its factor to $k$. Swapping either the diagnostic or the step between rows would no longer reproduce the stated guarantee. Treating each theorem as one inseparable record helps keep code comments and mathematical claims aligned.

These statements bound different diagnostics, so a trace should label what it records. Printing only `f(x)` allows observation of objective values for a known example; it does not directly display distance to an unknown minimizer. Likewise, a small gradient norm is a stationarity diagnostic, not the objective-gap bound above. Separating state, gradient norm, objective value, and distance avoids treating distinct quantities as interchangeable.

Finally, the guarantee boundary is part of the lesson. If a machine-learning objective is not known to be convex or strongly convex, these particular global rates cannot be attached to it. Gradient descent can still be executed as an algorithmic rule, but execution alone does not supply missing hypotheses.

<!-- section: SEC-06 -->
## Selecting a step with Armijo backtracking

A fixed choice such as $1/L$ requires a suitable known $L$. Armijo backtracking offers a bounded practical alternative for selecting the current step. Choose an initial trial step $\bar\alpha>0$, a contraction factor $\eta\in(0,1)$, and $c\in(0,1)$. Starting with $m=0$, form $\alpha_k=\eta^m\bar\alpha$ and accept the smallest nonnegative integer $m$ for which

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)
\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
$$

The right side specifies sufficient decrease relative to the current objective and squared gradient norm. If the inequality fails, increment $m$, contract the trial step by another factor of $\eta$, and test again. The first accepted trial is then used in the standard update.

There are two nested pieces of state here. The outer gradient-descent iteration owns $x_k$ and its gradient. The inner search owns the nonnegative counter $m$ and the corresponding trial step. During that inner search, the current point and current gradient stay fixed; only the trial step changes. Once the first acceptable candidate is found, the outer iteration advances. This division makes the smallest-integer rule testable: candidates are examined in the order $m=0,1,2,\ldots$, and the function returns immediately on the first successful inequality.

```python
import numpy as np

def objective(x):
    return 0.5 * (4.0 * x[0] ** 2 + x[1] ** 2)

def gradient(x):
    return np.array([4.0 * x[0], x[1]], dtype=float)

def armijo_step(x, bar_alpha=1.0, eta=0.5, c=0.1):
    g = gradient(x)
    m = 0
    while True:
        alpha = (eta ** m) * bar_alpha
        candidate = x - alpha * g
        if objective(candidate) <= objective(x) - c * alpha * np.dot(g, g):
            return alpha, m
        m += 1

x = np.array([2.0, -3.0], dtype=float)
for k in range(6):
    g = gradient(x)
    alpha, contractions = armijo_step(x)
    print(
        f"k={k}: f={objective(x):.6f}, alpha={alpha:.6f}, "
        f"m={contractions}, ||grad||={np.linalg.norm(g):.6f}"
    )
    x = x - alpha * g
```

Every call begins from the declared positive trial step and returns the smallest accepted $m$ because candidates are tested in increasing integer order. The parameter defaults satisfy the required ranges, the gradient is evaluated at the current state, and the accepted step is inserted into the same gradient-descent update used throughout the lesson.

The complete workflow is now traceable: formulate the unconstrained differentiable problem; recognise stationarity as necessary but not sufficient; update from the current gradient; attach descent reasoning to smoothness and an appropriate step; attach global rates only to their convex or strongly convex hypotheses; and, when using Armijo backtracking, accept the first contracted trial satisfying its precise inequality. In code as in mathematics, keeping assumptions beside conclusions prevents a successful execution trace from being mistaken for a universal guarantee.
