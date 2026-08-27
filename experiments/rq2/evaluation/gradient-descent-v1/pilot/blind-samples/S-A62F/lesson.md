# Gradient Descent: From an Update Rule to Conditional Guarantees

Gradient descent is a compact algorithm: evaluate a gradient, multiply it by a positive step size, and subtract. Understanding the method, however, requires more than memorising that line. We need to know what problem the line addresses, what its state variables mean, when a step is guaranteed to decrease the objective, and which assumptions support a convergence statement. Throughout the lesson, you can read an iterate as the current state of an optimisation program. A machine-learning loss is one possible motivation for such an objective, but the mathematical model here is deliberately bounded: real training objectives need not be convex, and basic full-batch gradient descent is not a complete production training system.

<!-- section: SEC-01 -->
## From an optimisation problem to stationarity

We begin with an unconstrained problem

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where $f:\mathbb{R}^d\to\mathbb{R}$ is at least continuously differentiable, written $f\in C^1$. The vector $x$ contains every quantity the algorithm may change, and $f(x)$ is the scalar objective value. “Unconstrained” matters: the domain is all of $\mathbb{R}^d$, so this formulation has not introduced a feasible region or an operation that projects iterates into one.

It helps to separate the mathematical interface from any motivating application. The algorithm receives a point and needs the objective value and gradient at that point. It does not know what individual coordinates represent. If the coordinates happen to be model parameters and the scalar is an educational loss, that interpretation changes the names in a trace but not the optimisation problem. Continuous differentiability ensures that the gradient used by the update is defined and changes continuously; it does not yet provide convexity, smoothness, or a convergence rate.

To discuss what the algorithm is seeking, recall two multivariable-calculus ideas. A point $a$ is a local minimum when some neighbourhood of $a$ has $f(a)\leq f(x)$ for every nearby $x$. Local is not the same as global: the comparison is limited to that neighbourhood. For $f(x_1,\ldots,x_d)$, assemble the first partial derivatives into the column vector

$$
\nabla f(x)=\left(\frac{\partial f}{\partial x_1},\ldots,
\frac{\partial f}{\partial x_d}\right)^T.
$$

For example, if $f(x,y)=x^2+xy$, then $\nabla f(x,y)=(2x+y,x)^T$, so $\nabla f(1,2)=(4,1)^T$. This calculation alone makes no claim that $(1,2)$ is a minimum.

Now suppose $x^*$ really is a local minimiser and $f$ is differentiable at $x^*$. A necessary first-order condition is

$$
\nabla f(x^*)=0.
$$

This is a one-way statement: a differentiable local minimum must be stationary, but stationarity by itself is not sufficient to identify a minimum without further assumptions. It nevertheless gives the algorithm a useful target condition: make the current gradient approach the zero vector.

The logical direction is worth checking whenever you read an implementation report. A small gradient is evidence about proximity to stationarity, not by itself a certificate of being at a local or global minimum. Conversely, if a differentiable point is already known to be a local minimum, then a nonzero computed gradient would conflict with the necessary condition and should prompt a check of the derivative or the claimed point. These statements use only first derivatives; no second-order test is being introduced.

<!-- section: SEC-02 -->
## The gradient-descent state transition

Choose an initial state $x_0\in\mathbb{R}^d$ and positive step sizes $\alpha_k$. Standard gradient descent applies

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),\qquad k=0,1,2,\ldots.
$$

The evaluation point and sign are essential. The gradient is evaluated at the current iterate $x_k$, not at a future or look-ahead point, and its positive multiple is subtracted. In program terms, iteration $k$ reads the current state, computes one gradient, and writes the next state. A trace should therefore record at least $k$, $x_k$, $f(x_k)$, and $\|\nabla f(x_k)\|$ before the update.

This ordering also prevents a subtle trace mismatch. If a program overwrites `x` and only then prints the old gradient beside the new point, the row no longer represents a single algorithm state. A faithful row pairs $x_k$ with $f(x_k)$ and $\nabla f(x_k)$; the next row begins after applying the transition. The index counts transitions, while the vector and diagnostics describe the state available at that index. None of these bookkeeping checks supplies a descent theorem, but they let you verify that the program implements the displayed recurrence.

The following self-contained trace uses the educational objective
$f(x)=\tfrac12(x_1^2+4x_2^2)$ and a fixed positive step. Its printed decrease is an observation about this run, not yet a general guarantee.

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
    print(k, x.copy(), objective(x), np.linalg.norm(g))
    x = x - alpha * g
```

Notice the data dependency: the gradient stored as `g` is computed before `x` is overwritten. The formula defines valid gradient-descent iterates for any positive step sequence, but it does not by itself promise that objective values fall. To obtain such control, we next need a way to measure changes and an assumption about how rapidly gradients can change.

<!-- section: SEC-03 -->
## Norms, smoothness, and a bound on one step

For $z\in\mathbb{R}^d$, the Euclidean norm is
$\|z\|_2=\sqrt{z^Tz}$, and $\|x-y\|_2$ measures the Euclidean distance between two vectors. A vector-valued map $G$ is $L$-Lipschitz, for $L>0$, when

$$
\|G(x)-G(y)\|_2\leq L\|x-y\|_2
$$

for every pair $x,y$ in its domain. This compares output-vector change with input-vector change. For example, $G(x)=2x$ satisfies $\|G(x)-G(y)\|_2=2\|x-y\|_2$, so $L=2$ works.

The constant has an operational reading: the inequality permits at most $L$ units of output-vector change per unit of input distance. It is an upper bound that must hold for every pair, not a ratio estimated from one pair in a log. Norms turn vector differences into nonnegative scalar quantities that can be compared. When a diagnostic computes the two sides for selected points, it illustrates the inequality, but those finitely many checks do not establish its universal quantifier.

Apply that idea specifically to the gradient map. A continuously differentiable objective is $L$-smooth when $L>0$ and, for all $x,y\in\mathbb{R}^d$,

$$
\|\nabla f(x)-\nabla f(y)\|_2\leq L\|x-y\|_2.
$$

This is not a claim that $|f(x)-f(y)|$ is bounded in the same way. It controls changes in gradient vectors, which is precisely what matters when an update moves from one state to another.

The resulting Descent Lemma says that if $f$ is $L$-smooth, then for every $x,y\in\mathbb{R}^d$,

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle
+\frac{L}{2}\|y-x\|_2^2.
$$

This quadratic upper bound keeps its direction and its coefficient $L/2$. Substitute $x=x_k$ and $y=x_k-\alpha_k\nabla f(x_k)$ to obtain

$$
f(x_{k+1})\leq f(x_k)-\alpha_k
\left(1-\frac{L\alpha_k}{2}\right)\|\nabla f(x_k)\|_2^2.
$$

The calculation exposes the step-size mechanism. When the coefficient multiplying the squared gradient norm is positive, the upper bound lies below the current value unless the gradient is zero. Smoothness therefore connects an implementation parameter to a checkable statement about one update; without the assumption, the same code line has no such bound.

There are two different comparisons in this reasoning. Smoothness first compares gradients at arbitrary points and yields a quadratic upper model for objective values. The update is then substituted into that model, turning the displacement into a scaled negative gradient. The inner-product term contributes a negative squared norm, while the quadratic term contributes a positive squared norm. Their balance produces the factor $1-L\alpha_k/2$. Keeping this chain visible explains why merely subtracting a gradient and proving decrease are separate tasks.

<!-- section: SEC-04 -->
## Choosing a constant step

A constant-step implementation sets $\alpha_k=\alpha$ at every iteration. When $L$ is known, a common choice is $\alpha=1/L$. Under the usual smooth convex assumptions, another standard statement is that $\alpha\in(0,2/L)$. The qualification belongs beside the interval: it is not a universal setting for arbitrary objectives.

At $\alpha=1/L$, the previous one-step bound becomes

$$
f(x_{k+1})\leq f(x_k)-\frac{1}{2L}\|\nabla f(x_k)\|_2^2.
$$

This also explains the earlier trace. For its objective, $L=4$ and the chosen value $0.25$ equals $1/L$. Starting from $(2,-1)^T$, the first update uses gradient $(2,-4)^T$ and produces $(1.5,0)^T$. The trace then continues from that newly stored state.

Pseudocode makes the constant-state dependency explicit: initialise `x`; at each index compute `g = gradient(x)`; log the current diagnostics; then assign `x = x - alpha*g`. Useful trace checks are that the logged state precedes its update, the step remains positive and unchanged, and the gradient used in the assignment belongs to that same state. Falling objective values are consistent with the smoothness-based bound when its conditions hold; a printed decrease alone does not establish those conditions.

The constant rule therefore has a configuration layer and an iteration layer. The configuration supplies one positive value before the loop, based on the qualified information about $L$. The loop reuses that value without searching or contracting it. In a trace, identical step entries confirm constancy, while the stored states confirm the recurrence. The choice $1/L$ is especially useful for connecting the one-step calculation to the later convex guarantee, but that later result will still need convexity and a global minimiser in addition to smoothness.

<!-- section: SEC-05 -->
## Choosing a step by Armijo backtracking

When using the selected backtracking alternative, choose an initial trial step $\bar\alpha>0$, a contraction factor $\eta\in(0,1)$, and $c\in(0,1)$. Test steps $\eta^m\bar\alpha$ for nonnegative integers $m$, beginning at zero. Accept the smallest $m$ for which $\alpha_k=\eta^m\bar\alpha$ satisfies

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)
\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|_2^2.
$$

The inequality asks for sufficient decrease, not merely any smaller printed value. The squared gradient norm and the inequality direction must remain exactly as shown. This implementation prints every trial, making the first accepted index auditable.

```python
import numpy as np

def objective(x):
    return 0.5 * (x[0] ** 2 + 4.0 * x[1] ** 2)

def gradient(x):
    return np.array([x[0], 4.0 * x[1]], dtype=float)

x = np.array([2.0, -1.0], dtype=float)
bar_alpha = 1.0
eta = 0.5
c = 0.25
g = gradient(x)
m = 0

while True:
    alpha = (eta ** m) * bar_alpha
    candidate = x - alpha * g
    left = objective(candidate)
    right = objective(x) - c * alpha * np.dot(g, g)
    accepted = left <= right
    print(m, alpha, left, right, accepted)
    if accepted:
        x = candidate
        break
    m += 1

print("accepted state", x)
```

The current gradient is computed once because all trials belong to the same current iterate. Only after acceptance is the state replaced. This is a bounded step-selection procedure, not a new optimisation method or an unconditional convergence claim.

For this block, the trials are visited in the exact order $1$, $1/2$, $1/4$, and so on because $\bar\alpha=1$ and $\eta=1/2$. Each printed Boolean compares the two displayed sides of the sufficient-decrease test. The loop stops at the first true result, so its accepted index is the smallest eligible $m$ rather than merely some successful index. Changing the current point would require recomputing its gradient and beginning a new search for the new iteration; rejected candidates never become algorithm states.

<!-- section: SEC-06 -->
## Inner products, convexity, and strong convexity

Before stating global shape assumptions, fix two pieces of notation. For real vectors $u$ and $v$ of the same dimension, $u^Tv$ is the scalar sum of componentwise products. Thus $g^T(y-x)$ is read by first forming the displacement $y-x$ and then taking its inner product with $g$; its sign describes their alignment, but no convexity conclusion follows from that arithmetic alone.

For points $x,y$ and $\theta\in[0,1]$, the vector $\theta x+(1-\theta)y$ is a convex combination. A set is convex when it contains every such combination of any two of its points. For example, with $x=(0,0)^T$, $y=(2,4)^T$, and $\theta=1/4$, the combination is $(3/2,3)^T$. If $g=(1,-1)^T$, then $g^T(y-x)=-2$; these remain arithmetic observations.

For a differentiable objective on $\mathbb{R}^d$, convexity is the global first-order lower bound

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle,
\qquad \text{for all }x,y\in\mathbb{R}^d.
$$

Unlike a merely local comparison, this inequality relates every pair of points. The affine expression based at $x$ lies below the objective at every $y$. In particular, if the gradient is zero at a point under this convexity assumption, the inequality identifies that point as a global minimiser.

Strong convexity adds a quantitative quadratic term. A differentiable $f$ is $\mu$-strongly convex, for $\mu>0$, when

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle
+\frac{\mu}{2}\|y-x\|_2^2,
\qquad \text{for all }x,y\in\mathbb{R}^d.
$$

The sign is positive and the coefficient is $\mu/2$. This is a stronger lower-bound structure than ordinary convexity. Keep it separate from smoothness: smoothness supplied an upper bound using $L$, whereas strong convexity supplies this lower bound using $\mu$.

You can parse both shape conditions with the same displacement $y-x$. Convexity says the first-order affine expression based at $x$ stays below every objective value. Strong convexity raises that lower expression by a nonnegative quadratic amount, which is positive whenever $x\ne y$. Smoothness points in the opposite bounding direction and limits how high the objective at $y$ can sit above the first-order expression. The later convergence results require particular combinations of these statements; sharing notation does not make their assumptions interchangeable.

<!-- section: SEC-07 -->
## Reading the condition ratio

When an objective is both $L$-smooth and $\mu$-strongly convex, with $0<\mu\leq L$, define

$$
\kappa=\frac{L}{\mu}\geq 1.
$$

Because $\mu$ is positive, dividing $0<\mu\leq L$ by $\mu$ proves the lower bound. The ratio measures the multiplicative separation of these two constants: if $L=12$ and $\mu=3$, then $\kappa=4$, so $L$ is four times $\mu$; if $L=\mu$, then $\kappa=1$. A value close to one means the constants are close, while a larger value means wider multiplicative separation. The ratio is not finite when $\mu=0$, and it is not being used here as a matrix or spectral condition number. Its role in this lesson is to make the contraction factors in the final guarantee readable.

When computing the ratio, check the prerequisites before the division: both constants belong to the same objective assumptions, $\mu$ is strictly positive, and the numerator is $L$. Inverting the ratio would reverse the intended comparison and lose the stated lower bound. This small check is similar to validating an algorithm parameter: the arithmetic is simple, but its meaning depends on the declarations attached to the symbols.

<!-- section: SEC-08 -->
## The convex objective-gap guarantee

We can now attach a convergence statement to a precise collection of assumptions. Let $f:\mathbb{R}^d\to\mathbb{R}$ be both $L$-smooth and convex, let $x^*$ be a global minimiser, and run gradient descent with $\alpha_k=1/L$. Then, for every $k\geq1$,

$$
f(x_k)-f(x^*)
\leq \frac{L\|x_0-x^*\|_2^2}{2k}.
$$

The left side is the objective gap, not the distance between iterates. The right side records three influences: the smoothness constant, the squared initial distance to a global minimiser, and the reciprocal of the iteration index. This is the $O(1/k)$ behaviour. For example, doubling $k$ halves this particular upper bound while the other quantities are fixed. Equivalently, making the bound at most a positive tolerance $\varepsilon$ requires
$k\geq L\|x_0-x^*\|_2^2/(2\varepsilon)$.

Read the theorem as a conditional worst-case ceiling, not as an equality predicted for every trace. Remove convexity, smoothness, the global-minimiser premise, or the specified $1/L$ step, and this statement no longer supplies a guarantee. An observed sequence of decreasing values is also not a substitute for checking the hypotheses.

The bound also distinguishes progress in function value from progress in state space. It says how far $f(x_k)$ can remain above the optimal value; it does not state that the Euclidean distance $\|x_k-x^*\|$ obeys the same reciprocal expression. The initial distance appears on the right as part of the ceiling, but the quantity being bounded on the left remains the objective gap. Reading both sides before naming a rate prevents a function-value theorem from being reported as a distance theorem.

<!-- section: SEC-09 -->
## Strong-convexity contractions and their limits

Under the stronger joint assumptions that $f$ is $L$-smooth and $\mu$-strongly convex, gradient descent has two selected step-and-rate pairings. They must not be swapped. With

$$
\alpha=\frac{2}{L+\mu},
$$

the squared distance contracts according to

$$
\|x_k-x^*\|_2^2
\leq
\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}
\|x_0-x^*\|_2^2.
$$

With the different choice $\alpha=1/L$, the objective gap obeys

$$
f(x_k)-f(x^*)
\leq
\left(1-\frac{\mu}{L}\right)^k
\bigl(f(x_0)-f(x^*)\bigr).
$$

These are geometric, often called linear, convergence bounds: the relevant initial error is multiplied by a fixed contraction factor at each iteration. Since $\mu/L=1/\kappa$, a larger condition ratio makes the objective-gap factor $1-1/\kappa$ closer to one. Likewise, $(\kappa-1)/(\kappa+1)$ approaches one as $\kappa$ grows. The bounds therefore expose why greater separation between $L$ and $\mu$ corresponds to a weaker guaranteed contraction.

The guarantee boundary is as important as the formulas. Both results require global $L$-smoothness and positive-$\mu$ strong convexity, and each result requires its own displayed step size. No Hessian-based derivation is needed here. These statements do not imply that an arbitrary machine-learning loss has the required shape, nor that a short trace certifies it.

Compare the pairings as typed interfaces. The distance result accepts the step $2/(L+\mu)$ and returns a bound on squared distance. The objective result accepts the step $1/L$ and returns a bound on objective gap. Passing the first step to the second displayed result, or relabelling its output quantity, is not licensed. In both cases the exponent makes repeated contraction explicit, while the condition ratio explains how close the factor is to one.

You can now read gradient descent as a complete chain rather than an isolated assignment statement: formulate the unconstrained differentiable objective; compute the gradient at the current state; select either the qualified constant rule or the stated Armijo test; and match any rate claim to its exact smoothness, convexity, step-size, and minimiser assumptions. That discipline keeps executable behaviour and mathematical guarantees connected without confusing one observed run with a theorem.
