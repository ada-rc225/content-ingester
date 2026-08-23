# Gradient Descent: From Objective to Convergence

Gradient descent is a first-order optimisation method. In this lesson, we will build the method in a fixed order: formulate the objective, connect local calculus to stationarity, trace the update, establish the smoothness bound that controls a step, compare constant and Armijo steps, and then interpret convex and strongly convex convergence. The examples use small vectors and executable NumPy traces. A machine-learning loss is a useful motivation for an objective, but this lesson does not claim that production training objectives are convex or that full-batch gradient descent is a complete training system.

<!-- section: SEC-01 -->
## The optimisation problem and local calculus

An unconstrained differentiable optimisation problem has the form

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where $f:\mathbb{R}^d\to\mathbb{R}$ is at least continuously differentiable. “Unconstrained” means that the candidate vector $x$ ranges over all of $\mathbb{R}^d$; no feasible-set restriction has been added. The objective is a scalar, while the decision variable is a vector. For a computational learner, it is helpful to keep these types visible: an implementation stores $x$ as an array and returns a scalar loss $f(x)$ and a vector gradient $\nabla f(x)$.

Before using a gradient algorithm, recall two local multivariable ideas. A point $a$ is a local minimum of $f$ when there is a neighbourhood of $a$ in which $f(a)\leq f(x)$ for every nearby $x$. For $f(x_1,\ldots,x_d)$, form the gradient by differentiating with respect to each coordinate:

$$
\nabla f(x)=\left(\frac{\partial f}{\partial x_1},\ldots,\frac{\partial f}{\partial x_d}\right)^T.
$$

For example, if $f(x,y)=x^2+xy$, then $\nabla f(x,y)=(2x+y,x)^T$. At $(1,2)$ it is $(4,1)^T$. This calculation does not establish that $(1,2)$ is a minimum, and it makes no Hessian or definiteness claim.

If $x^*$ is a local minimiser and $f$ is differentiable at $x^*$, then the first-order necessary condition is

$$
\nabla f(x^*)=0.
$$

This is a stationarity condition, not a sufficient condition for a minimum by itself. A stationary point can require additional assumptions before its optimisation role is known. Gradient descent searches for a point whose gradient becomes small by moving in the negative current gradient direction.

<!-- section: SEC-02 -->
## The update and an executable state trace

Given $x_0\in\mathbb{R}^d$ and positive step sizes $\alpha_k$, standard gradient descent uses the gradient at the current iterate:

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),\qquad k=0,1,2,\ldots.
$$

The subtraction is important: the gradient points toward local increase, so its negative is the first-order decrease direction. The rule is not a look-ahead update. Each iteration evaluates the objective and gradient at the current state, chooses a positive step, and then constructs the next state.

A small quadratic gives a transparent trace. Let $f(x)=\tfrac12\|x-b\|_2^2$, so $\nabla f(x)=x-b$. The code below is self-contained and prints the iteration, current vector, gradient, and objective. It demonstrates the update mechanics only; it does not add a general convergence guarantee.

```python
import numpy as np

b = np.array([1.0, -2.0])
x = np.array([4.0, 2.0])
alpha = 0.5

def objective(x):
    return 0.5 * np.dot(x - b, x - b)

def gradient(x):
    return x - b

for k in range(5):
    g = gradient(x)
    print(k, np.round(x, 3), round(objective(x), 6), np.round(g, 3))
    x = x - alpha * g
```

Read the printed state as an algorithm diagnostic. The gradient is computed before the assignment to `x`; the next state is the current state minus a positive multiple of that gradient. A decreasing objective in this particular trace is evidence about this chosen function, starting point, and step, not a universal claim about every differentiable objective.

<!-- section: SEC-03 -->
## Norms, Lipschitz continuity, and smoothness

For a vector $z\in\mathbb{R}^d$, its Euclidean norm is

$$
\|z\|_2=\sqrt{z^Tz},
$$

and $\|x-y\|_2$ measures the distance between two vectors. An $L$-Lipschitz vector map $G$ satisfies

$$
\|G(x)-G(y)\|_2\leq L\|x-y\|_2
$$

for every pair $x,y$ in its domain, with $L>0$. The left side measures output-vector change and the right side scales input-vector change. When $G$ is a gradient, this is a statement about changes in gradient vectors, not about a bound on $|f(x)-f(y)|$.

For instance, for $G(x)=2x$, the norm identity $\|G(x)-G(y)\|_2=2\|x-y\|_2$ shows that $L=2$ works. This is a vector-map example, not a gradient-descent result.

A continuously differentiable objective $f:\mathbb{R}^d\to\mathbb{R}$ is $L$-smooth when its gradient is $L$-Lipschitz in the Euclidean norm:

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|,\qquad\forall x,y\in\mathbb{R}^d,
$$

where $L>0$. Smoothness controls how rapidly the gradient can change. It is an assumption about the whole domain in this statement, not merely an observation at one iterate.

<!-- section: SEC-04 -->
## The descent bound and step-size choices

The Descent Lemma is the quadratic upper bound implied by $L$-smoothness. For all $x,y\in\mathbb{R}^d$,

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle+\frac{L}{2}\|y-x\|^2.
$$

The inequality is an upper bound, and the coefficient is $L/2$. Substitute the gradient-descent trial point $y=x-\alpha\nabla f(x)$ to see the two competing terms. The inner-product term is negative when $\alpha>0$ and the gradient is nonzero; the squared-norm term is positive. Thus, under the smoothness assumption, a step must balance first-order decrease against the quadratic correction. This explains why a step that is too large need not decrease the objective.

With a constant step, $\alpha_k=\alpha$ for every iteration. If $L$ is known, a common choice is $\alpha=1/L$. Under the usual smooth-convex assumptions, the source also gives the qualified interval $\alpha\in(0,2/L)$. That interval is not a universal rule for arbitrary differentiable objectives. The assumptions must travel with the statement.

A useful implementation checklist is: verify that the gradient is evaluated at the current state, keep $\alpha>0$, record the objective before and after the candidate update, and avoid interpreting one successful trace as a theorem. If $L$ is estimated rather than known, the guarantee associated with the exact $1/L$ choice cannot simply be transferred without checking the estimate and assumptions.

<!-- section: SEC-05 -->
## Armijo backtracking as a bounded alternative

A constant step is not the only selected rule. Armijo backtracking starts with a positive trial step $\bar\alpha>0$, a contraction factor $\eta\in(0,1)$, and a parameter $c\in(0,1)$. At iteration $k$, test steps of the form $\alpha_k=\eta^m\bar\alpha$ for nonnegative integers $m$. Accept the smallest $m$ for which

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
$$

The right side demands a sufficient decrease proportional to the step and squared gradient norm. The acceptance inequality must not be reversed, and the squared norm is part of the rule. Backtracking contracts the trial step until this test passes; it does not introduce a look-ahead gradient.

The following complete implementation prints the accepted exponent and step. It uses a fixed quadratic only to make the test reproducible.

```python
import numpy as np

b = np.array([1.0, -2.0])
x = np.array([4.0, 2.0])
trial = 2.0
eta = 0.5
c = 0.25

def f(z):
    d = z - b
    return 0.5 * np.dot(d, d)

def grad(z):
    return z - b

g = grad(x)
for m in range(20):
    alpha = (eta ** m) * trial
    candidate = x - alpha * g
    if f(candidate) <= f(x) - c * alpha * np.dot(g, g):
        print("accepted", m, alpha, f(x), f(candidate))
        break
else:
    raise RuntimeError("no Armijo step accepted")
```

The printed acceptance is a diagnostic for this finite example. It does not claim that backtracking makes every objective convex or supplies a convergence theorem without the relevant hypotheses.

<!-- section: SEC-06 -->
## Inner products, convex combinations, and convexity

For equal-length real vectors, $u^Tv$ is the scalar sum of componentwise products. To parse $g^T(y-x)$, first form the displacement $d=y-x$, then compute the scalar $g^Td$. Its sign describes alignment between $g$ and the displacement; this arithmetic alone gives no convexity conclusion.

For $\theta\in[0,1]$, $\theta x+(1-\theta)y$ is a convex combination. A set is convex when it contains that combination for every pair of its points and every such $\theta$. For $x=(0,0)^T$, $y=(2,4)^T$, and $\theta=1/4$, the combination is $(3/2,3)^T$. If $g=(1,-1)^T$, then $g^T(y-x)=-2$. These are interpretations of vectors and scalars, not proofs of global optimality.

A differentiable function is convex when, for all $x,y\in\mathbb{R}^d$,

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle.
$$

This is a global first-order lower bound. Notice its direction: it is a lower bound, unlike the smoothness-based quadratic upper bound. Convexity changes the interpretation of a stationary point and supports a global convergence statement, but it is an additional assumption rather than a consequence of observing a few iterations.

<!-- section: SEC-07 -->
## Strong convexity, conditioning, and the two guarantees

A differentiable function is $\mu$-strongly convex for $\mu>0$ when, for all $x,y\in\mathbb{R}^d$,

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle+\frac{\mu}{2}\|y-x\|^2.
$$

Strong convexity adds a positive quadratic term to the convex lower bound. It is a stronger assumption, and the term must not be dropped or given a negative sign. This lesson uses the inequality directly; it does not use a Hessian-order derivation.

When an objective is both $L$-smooth and $\mu$-strongly convex, define

$$
\kappa=\frac{L}{\mu}\geq1.
$$

Here $\mu>0$ and $L\geq\mu$, so the ratio is finite and at least one. For $L=12$ and $\mu=3$, $\kappa=4$: the constants are separated by a factor of four. A larger ratio indicates greater multiplicative separation in this selected condition measure; it is not a claim about another matrix or numerical condition number.

For the smooth convex case, if $x^*$ is a global minimiser and gradient descent uses $\alpha_k=1/L$, then for $k\geq1$,

$$
f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k}.
$$

Every hypothesis matters: $L$-smoothness, convexity, a global minimiser, and the specified step. The objective gap has an $O(1/k)$-type bound under these conditions.

Under the stronger assumptions of $L$-smoothness and $\mu$-strong convexity, there are two selected pairings. With $\alpha=2/(L+\mu)$,

$$
\|x_k-x^*\|^2\leq\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}\|x_0-x^*\|^2.
$$

With $\alpha=1/L$,

$$
f(x_k)-f(x^*)\leq\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).
$$

Do not swap the step sizes between these bounds. The distance contraction belongs to $2/(L+\mu)$, while the objective-gap contraction belongs to $1/L$. Both require smoothness and strong convexity. Conditioning appears through $\kappa=L/\mu$: the ratio helps describe how the contraction factor changes, but it does not remove the assumptions.

**A traceable workflow and boundary checks.**

A disciplined implementation can now be written as a sequence: formulate an unconstrained $C^1$ objective; compute a current gradient; choose a positive constant or Armijo step; update with the negative current gradient; and record states and objective values. Then ask which assumptions are available before attaching a guarantee. Smoothness supports the quadratic upper bound. Convexity supports the stated $1/k$ objective-gap result with $1/L$. Strong convexity, together with smoothness, supports the two stated linear contractions with their distinct step sizes.

For a computer-science use case, a loss function can motivate why one wants to reduce a scalar objective over a parameter vector. The mathematical lesson remains bounded: a production loss is not assumed convex merely because it is called a loss, and the deterministic full-batch iteration shown here is not a complete training system. The safe habit is to report the objective, gradient, step rule, and assumptions separately.

It is useful to separate three kinds of evidence in a debugging log. First, the state trace records what the program did: the current vector, gradient, selected step, candidate vector, and objective values. Second, a diagnostic records a local test, such as whether the Armijo inequality passed for the accepted candidate. Third, an assumption record states what is known about the objective, such as an available smoothness constant or a convexity hypothesis. These records should not be merged. A decreasing sequence in one run is a trace observation; it is not by itself evidence that the objective is convex, smooth, or strongly convex.

The formulas also suggest simple type and indexing checks. The vector $x_k$ and gradient $\nabla f(x_k)$ must have the same dimension, the objective values $f(x_k)$ and $f(x_{k+1})$ are scalars, and $\alpha_k\nabla f(x_k)$ has the same shape as $x_k$. The index $k$ labels the state before the update. If a program overwrites the state before saving the gradient or objective, it becomes harder to verify that the current-gradient rule was followed. Saving the old state and candidate explicitly makes the trace auditable.

For a constant step, the implementation should record whether the value is intended to be $1/L$ or another positive value. If the value is $1/L$, the smoothness constant must have the role required by the theorem being invoked. If the value is merely tuned for a small experiment, describe it as an experimental choice rather than attaching the $O(1/k)$ statement. Likewise, the interval $(0,2/L)$ belongs beside its smooth-convex qualification. Moving a formula away from its assumptions is a common source of overclaiming.

For Armijo backtracking, the trace should include $\bar\alpha$, $\eta$, $c$, each tested exponent $m$, and the first accepted step. The phrase “first accepted” means the smallest nonnegative integer satisfying the sufficient-decrease inequality. A later passing step is not the same recorded algorithm. The code example keeps the loop bounded and raises an error if no tested step passes, so failure is visible rather than silently returning an invalid update.

The convergence formulas are also best treated as paired records. One record contains the assumptions, the chosen step, the quantity being bounded, and the bound itself. For the convex result, the quantity is the objective gap and the denominator is $2k$. For the strongly convex distance result, the quantity is the squared distance and the step is $2/(L+\mu)$. For the strongly convex objective result, the quantity is the objective gap and the step is $1/L$. This structure makes it possible to check a theorem implementation without importing an unselected second-order argument or an acceleration method.

Finally, the pathway intentionally stops at standard deterministic gradient descent. It does not license claims about stochastic gradients, adaptive optimisers, Newton updates, quasi-Newton updates, or accelerated methods. Those methods may be important elsewhere, but mentioning their guarantees here would change the selected content. Staying within scope is part of a technically reliable explanation: say what the update is, show what the assumptions buy, and state clearly what the evidence does not establish.

When comparing two runs, compare like with like. Keep the objective, initial point, gradient implementation, stopping rule, and reporting convention visible. Changing several of these at once makes it impossible to attribute a different trace to the step rule. A numerical trace can also be checked algebraically on a small example: calculate one gradient by hand, calculate the candidate vector, and substitute it into the objective. This catches a reversed sign, a stale gradient, or an accidental change from $\alpha_k$ to a look-ahead quantity before any convergence discussion begins.

The word “convergence” should likewise be tied to a quantity. A sequence of vectors, objective values, and objective gaps are different objects. The selected convex theorem bounds an objective gap, whereas one selected strongly convex theorem bounds a squared distance and another bounds an objective gap. A small gradient norm is a stationarity diagnostic; it is not automatically one of these theorem bounds. Keeping these distinctions explicit is especially important when a program prints only a single loss value per iteration.

Use this final checklist when reading or implementing gradient descent:

1. Is the problem unconstrained over $\mathbb{R}^d$, with a continuously differentiable scalar objective?
2. Is stationarity being treated as necessary rather than automatically sufficient?
3. Is the gradient evaluated at $x_k$, with a positive step and a subtraction sign?
4. Is $L$-smoothness being used as a gradient Lipschitz condition, not a function-value Lipschitz condition?
5. Are the Descent Lemma inequality and its $L/2$ coefficient oriented correctly?
6. Are step-size qualifications and convergence hypotheses stated beside the claim they support?
7. Are the $2/(L+\mu)$ distance contraction and $1/L$ objective contraction kept paired with the correct formulas?

A trace is valuable because it makes behaviour inspectable. A theorem is valuable because it explains which behaviour is guaranteed and under exactly which assumptions. Gradient descent is understood when those two views—state-level execution and hypothesis-level reasoning—are kept connected without overstating either one.
