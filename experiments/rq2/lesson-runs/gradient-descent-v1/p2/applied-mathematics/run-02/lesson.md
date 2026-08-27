# Gradient Descent: Assumptions, Steps, and Rates

Gradient descent is simple to write down, but its behaviour is governed by precise assumptions. In this lesson, we will build the method from the optimisation problem, connect smoothness to descent, distinguish convex from strongly convex structure, and finish with constant and backtracked step choices. Keep track of which conclusion uses which assumption: that discipline is as important as manipulating the formulas.

<!-- section: SEC-01 -->
## The unconstrained optimisation problem

We consider the canonical unconstrained problem

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where $f:\mathbb{R}^d\to\mathbb{R}$ is at least continuously differentiable, written $f\in C^1$. The vector $x$ contains the quantities we may vary, while the scalar $f(x)$ measures the objective value. “Unconstrained” matters: every vector in $\mathbb{R}^d$ is admissible. Adding restrictions on $x$ would define a different problem.

An applied-mathematics model may supply a concrete objective, but differentiability alone says neither that a minimizer exists nor that the objective is convex. Our immediate task is therefore narrower: understand a first-order iteration for seeking low objective values, then state separately the assumptions that justify descent and convergence claims.

It helps to separate the objects in the formulation. The input $x$ is a point in a finite-dimensional vector space, $f(x)$ is a real number that can be compared with other objective values, and $\nabla f(x)$ will be a vector of the same dimension as $x$. The dimension $d$ is arbitrary but fixed. None of this notation supplies a feasible boundary or a hidden restriction: the search domain in the displayed problem remains all of $\mathbb{R}^d$.

<!-- section: SEC-02 -->
## What a local minimizer must satisfy

Suppose $x^*$ is a local minimizer and $f$ is differentiable at $x^*$. The first-order necessary condition is

$$
\nabla f(x^*)=0.
$$

The gradient collects the first partial derivatives, so stationarity says that every first-order directional change vanishes at the candidate point. The logical direction is essential: differentiable local minimum implies zero gradient. A zero gradient by itself is not sufficient to certify a minimum without additional assumptions.

This condition suggests a computational target. If an iterate has a large gradient, it is not stationary; reducing the influence of that gradient can move the iteration toward a stationary point. Yet stationarity alone does not say whether that point is local or global, and it supplies no rate. Those stronger conclusions will require explicit structural assumptions later.

The necessity can be read through one-dimensional slices. Fix any direction $v$ and consider the scalar function obtained by moving from $x^*$ along $v$. A local minimum at the zero displacement has zero derivative, and the chain rule identifies that derivative with $\nabla f(x^*)^Tv$. Because this holds for every $v$, choosing $v=\nabla f(x^*)$ gives a squared norm equal to zero. Hence the gradient vanishes. This argument establishes only the necessary implication already stated; it does not reverse it.

<!-- section: SEC-03 -->
## Euclidean distance and Lipschitz vector maps

Before imposing smoothness, recall the measurement used in its definition. For $z\in\mathbb{R}^d$, the Euclidean norm is

$$
\|z\|_2=\sqrt{z^Tz},
$$

and $\|x-y\|_2$ is the Euclidean distance between $x$ and $y$. For a vector-valued map $G$ and a constant $L>0$, the statement that $G$ is $L$-Lipschitz means

$$
\|G(x)-G(y)\|_2\leq L\|x-y\|_2
$$

for every pair $x,y$ in its domain. It compares an output-vector change with the corresponding input-vector change.

For example, if $G(x)=2x$, then

$$
\|G(x)-G(y)\|_2=\|2(x-y)\|_2=2\|x-y\|_2,
$$

so the inequality holds with $L=2$. When $G$ is a gradient map, the left side measures a difference between gradient vectors. It is not the scalar quantity $|f(x)-f(y)|$ and must not be read as a claim that function values themselves are Lipschitz.

<!-- section: SEC-04 -->
## Smoothness as control of gradient change

A continuously differentiable function is called $L$-smooth, for $L>0$, when its gradient is $L$-Lipschitz in the Euclidean norm:

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|,
\qquad \forall x,y\in\mathbb{R}^d.
$$

Thus $L$ bounds how rapidly the gradient vector can change relative to displacement in the input. This is a global, all-pairs assumption. It does not assert convexity, and it is not function-value Lipschitz continuity.

For analysis, smoothness is useful because it turns control of gradient variation into a quadratic upper estimate for $f$. Geometrically, the linear approximation at one point may miss the function at another, but smoothness limits that miss by a term proportional to squared distance. We will make that statement precise after defining the iteration.

The all-pairs quantifier also tells you how to audit the assumption. It is not enough for two conveniently chosen gradients to obey the inequality, and the constant must not change with the pair. For a displacement $y-x$, the right side scales its Euclidean length by one common $L$, while the left side measures the resulting gradient change. A smaller valid $L$ represents tighter control in this inequality; the definition itself still makes no claim about where a minimum lies.

<!-- section: SEC-05 -->
## The current-gradient update

Choose an initial point $x_0\in\mathbb{R}^d$ and positive step sizes $\alpha_k$. Gradient descent generates

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),
\qquad k=0,1,2,\ldots.
$$

The gradient is evaluated at the current iterate $x_k$, not at a future or look-ahead point. The subtraction sign selects the negative-gradient direction, and $\alpha_k>0$ scales the displacement. One iteration therefore has a traceable order: evaluate $\nabla f(x_k)$, select a positive step, and update $x_k$.

The formula defines the method but does not, by itself, guarantee that every step lowers $f$. A step can be incompatible with the available smoothness information. To connect the update to objective decrease, we next need the upper bound supplied by $L$-smoothness.

<!-- section: SEC-06 -->
## The quadratic upper bound

If $f$ is $L$-smooth, then for every $x,y\in\mathbb{R}^d$ the Descent Lemma states

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle
+\frac{L}{2}\|y-x\|^2.
$$

Here $\langle u,v\rangle=u^Tv$ is the Euclidean inner product, a scalar, and $\|v\|^2$ is the squared Euclidean norm. The inequality is an upper bound: it combines the linear model at $x$ with a nonnegative quadratic allowance whose coefficient is exactly $L/2$.

Insert $x=x_k$ and $y=x_{k+1}=x_k-\alpha_k\nabla f(x_k)$. Since $y-x=-\alpha_k\nabla f(x_k)$, the bound becomes

$$
f(x_{k+1})\leq f(x_k)
-\alpha_k\|\nabla f(x_k)\|^2
+\frac{L\alpha_k^2}{2}\|\nabla f(x_k)\|^2.
$$

This calculation exposes the competition controlled by the step size: the linear term decreases the upper estimate, while the quadratic term offsets part of that decrease. We have not used convexity here; the bound follows from smoothness.

Every part of the substitution can be checked independently. The inner product with the displacement is $-\alpha_k\langle\nabla f(x_k),\nabla f(x_k)\rangle$, which is $-\alpha_k\|\nabla f(x_k)\|^2$. The displacement norm is $\|-\alpha_k\nabla f(x_k)\|$, so its square contributes $\alpha_k^2\|\nabla f(x_k)\|^2$. The first contribution is linear in the step and the second is quadratic in it. This is why the update formula alone is insufficient: the upper estimate depends quantitatively on both $L$ and $\alpha_k$.

<!-- section: SEC-07 -->
## Inner products and convex combinations

Convexity uses two pieces of vector notation. For real vectors $u$ and $v$ of the same dimension,

$$
u^Tv=\sum_i u_iv_i
$$

is a scalar inner product. To parse $g^T(y-x)$, first form the displacement $d=y-x$, then compute $g^Td$. Its sign describes alignment between $g$ and that displacement, but the arithmetic alone proves no convexity theorem.

For $\theta\in[0,1]$, the point $\theta x+(1-\theta)y$ is a convex combination. A set is convex when it contains every such combination of each pair of its points. For instance, with $x=(0,0)^T$, $y=(2,4)^T$, and $\theta=1/4$, the combination is $(3/2,3)^T$. If $g=(1,-1)^T$, then $g^T(y-x)=-2$. These computations illustrate the notation only; they do not establish convexity or optimality.

<!-- section: SEC-08 -->
## The global first-order inequality

For a differentiable function on $\mathbb{R}^d$, convexity is characterized by the global lower bound

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle,
\qquad \forall x,y\in\mathbb{R}^d.
$$

The affine first-order model at $x$ lies below the function everywhere. Notice how this differs from the Descent Lemma: convexity gives a lower bound, whereas smoothness gives a quadratic upper bound. Neither assumption should be silently substituted for the other.

The global quantifier gives stationarity more force. If $\nabla f(x)=0$ at a point of a convex differentiable objective, the inequality reduces to $f(y)\geq f(x)$ for every $y$, so that stationary point is a global minimizer. This conclusion depends on convexity; it is unavailable for an arbitrary differentiable objective.

There is also a useful geometric reading that stays within the inequality. For fixed $x$, the expression on the right is affine in $y$: it begins at the height $f(x)$ and changes according to the inner product of the gradient with the displacement. Convexity says that this entire affine model is a global under-estimator. Smoothness placed a curved quadratic model above the function; convexity now places a linear model below it. Later, the rate argument will use both sides of this analytic sandwich for distinct steps in the reasoning.

<!-- section: SEC-09 -->
## Strong convexity

A differentiable function is $\mu$-strongly convex, with $\mu>0$, when for every $x,y\in\mathbb{R}^d$,

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle
+\frac{\mu}{2}\|y-x\|^2.
$$

Compared with convexity, the lower bound contains the positive quadratic term $(\mu/2)\|y-x\|^2$. The sign, squared norm, and coefficient $\mu/2$ are part of the assumption. Dropping that term returns the weaker convex inequality.

Smoothness and strong convexity play different roles. Smoothness limits how quickly gradients can change and supplies an upper model; strong convexity strengthens the global lower model. When both hold, the constants $L$ and $\mu$ provide two scales with which to describe the iteration.

The added term is zero when $y=x$ and positive whenever $y\ne x$. Thus the lower model is separated from the convex affine model by an amount that grows with squared Euclidean distance. The assumption is global because it must hold for every pair. A positive value of $\mu$ is part of the definition, so ordinary convexity with no such positive quadratic strengthening should not be relabelled as strong convexity. This distinction is exactly what separates the two convergence regimes used below.

<!-- section: SEC-10 -->
## Ratios and multiplicative separation

For positive constants satisfying $0<\mu\leq L$, define

$$
\kappa=\frac{L}{\mu}.
$$

Dividing $0<\mu\leq L$ by the positive number $\mu$ gives $\kappa\geq1$. The ratio records multiplicative separation: if $L=12$ and $\mu=3$, then $\kappa=4$, so $L$ is four times $\mu$; if $L=\mu$, then $\kappa=1$. A value near one means the constants are close, while a larger value means they are more widely separated multiplicatively.

The positivity condition is indispensable. When $\mu=0$, $L/\mu$ is not a finite condition ratio. Here we use only this ratio of the two scalar constants; no matrix, spectral, or other condition measure is being introduced.

<!-- section: SEC-11 -->
## The condition number for the objective

When the same objective is both $L$-smooth and $\mu$-strongly convex, its condition number is

$$
\kappa=\frac{L}{\mu}\geq1.
$$

The ratio is $L$ divided by $\mu$, not the inverse. It compresses the separation between the smoothness upper scale and strong-convexity lower scale into one dimensionless quantity. This definition requires both assumptions; an $L$-smooth objective with no positive strong-convexity constant does not receive a finite $\kappa$ from this formula.

The usefulness of $\kappa$ will become visible in the strongly convex contraction factors. Reading those factors through this ratio makes conditioning part of the rate interpretation rather than an informal label attached to a plot.

<!-- section: SEC-12 -->
## Constant steps under stated assumptions

A constant-step iteration sets $\alpha_k=\alpha$ for every $k$. When $L$ is known, a common choice is

$$
\alpha=\frac{1}{L}.
$$

Under the usual smooth-convex assumptions, common constant choices also include $\alpha\in(0,2/L)$. The qualifier belongs with the interval: it is not a universal prescription for every differentiable objective.

The earlier upper-bound calculation explains the role of the scale $L$. Its two gradient-norm terms combine as

$$
-\alpha\left(1-\frac{L\alpha}{2}\right)\|\nabla f(x_k)\|^2.
$$

For the selected value $\alpha=1/L$, the Descent Lemma yields

$$
f(x_{k+1})\leq f(x_k)-\frac{1}{2L}\|\nabla f(x_k)\|^2.
$$

This is a descent statement under $L$-smoothness. Convergence rates require further assumptions, which we now attach explicitly.

The statement compares consecutive objective values, but its right-hand decrease can become zero when the current gradient is zero. It should therefore be read as nonincrease together with a quantified decrease term, not as an unconditional strict reduction at every index. The constant rule also presumes the relevant value of $L$ is known for the listed choices. Backtracking later gives a way to test candidate steps directly, but it will not change the current-gradient form of the iteration.

<!-- section: SEC-13 -->
## The smooth-convex objective-gap rate

Assume that $f$ is both $L$-smooth and convex, that a global minimizer $x^*$ exists, and that gradient descent uses $\alpha_k=1/L$. For every $k\geq1$,

$$
f(x_k)-f(x^*)
\leq
\frac{L\|x_0-x^*\|^2}{2k}.
$$

Here is the assumption-to-conclusion mechanism. Convexity, evaluated at $x_k$ and $x^*$, gives

$$
f(x_k)-f(x^*)\leq
\langle\nabla f(x_k),x_k-x^*\rangle.
$$

Expanding the squared distance after the $1/L$ update relates this inner product to the change in $\|x_k-x^*\|^2$. Meanwhile, the Descent Lemma gives the objective decrease established in the previous section. Combining the two relations yields

$$
f(x_{k+1})-f(x^*)\leq
\frac{L}{2}\left(\|x_k-x^*\|^2-\|x_{k+1}-x^*\|^2\right).
$$

To see the combination explicitly, expand

$$
\|x_{k+1}-x^*\|^2
=\|x_k-x^*\|^2
-\frac{2}{L}\langle\nabla f(x_k),x_k-x^*\rangle
+\frac{1}{L^2}\|\nabla f(x_k)\|^2.
$$

Convexity bounds the inner product below by the current objective gap. Smooth descent bounds the squared-gradient term through the difference $f(x_k)-f(x_{k+1})$. Substituting both inequalities and rearranging gives the one-step relation displayed above. Each ingredient has a separate job: convexity connects gradient alignment to the global minimizer, while smoothness connects the gradient norm to actual decrease under the selected step.

Summing from the initial iterate makes the squared-distance terms telescope. The objective values are nonincreasing under the selected step, so the final gap is no larger than the average of the preceding gaps, producing the stated bound.

More precisely, summing the one-step relation over the first $k$ updates leaves at most $(L/2)\|x_0-x^*\|^2$ because the final squared distance is nonnegative. The sum contains $k$ nonnegative objective gaps, and monotonicity makes every one of them at least as large as the final gap. Multiplying that final gap by $k$, then dividing by $k$, produces the denominator $2k$. This is why the initial squared distance and the factor $L/2$ appear in the final estimate.

The notation $O(1/k)$ describes the reciprocal dependence on the iteration count in this upper bound. To make the right side at most a tolerance $\varepsilon>0$, the bound requires $k\geq L\|x_0-x^*\|^2/(2\varepsilon)$. This is an objective-gap guarantee, not a claim that every differentiable objective has a global rate.

<!-- section: SEC-14 -->
## Strongly convex contractions

Now assume that $f$ is $L$-smooth and $\mu$-strongly convex, and let $\kappa=L/\mu$. Two guarantees must be paired with their own step sizes.

With

$$
\alpha=\frac{2}{L+\mu},
$$

gradient descent satisfies the squared-distance contraction

$$
\|x_k-x^*\|^2
\leq
\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}
\|x_0-x^*\|^2.
$$

With the different choice $\alpha=1/L$, it satisfies the objective-gap contraction

$$
f(x_k)-f(x^*)
\leq
\left(1-\frac{\mu}{L}\right)^k
\bigl(f(x_0)-f(x^*)\bigr).
$$

The first statement is about squared distance and uses $2/(L+\mu)$; the second is about objective gap and uses $1/L$. They are not interchangeable.

Conditioning is visible directly. Since $\mu/L=1/\kappa$, the objective factor is $1-1/\kappa$. As $\kappa$ grows, this factor approaches one, so the guaranteed contraction per iteration becomes weaker. Likewise, $(\kappa-1)/(\kappa+1)$ approaches one for large $\kappa$. These are geometric, or linear, rates under simultaneous global smoothness and strong convexity. They do not provide a global guarantee for an arbitrary differentiable or nonconvex objective, and no Hessian-based derivation is needed for the statements used here.

The exponents explain the term “contraction.” In the objective statement, each additional iteration multiplies the bound by the same factor $1-1/\kappa$. In the squared-distance statement, each additional iteration contributes two powers of $(\kappa-1)/(\kappa+1)$. When $\kappa=1$, both displayed factors are zero; as $\kappa$ becomes large, both approach one. This interpretation compares the certified upper bounds. It does not say that a particular numerical trace must attain equality at every step.

<!-- section: SEC-15 -->
## Armijo backtracking

When a fixed value based on $L$ is not being used, Armijo backtracking supplies a practical bounded alternative. Choose an initial trial step $\bar\alpha>0$, a contraction factor $\eta\in(0,1)$, and $c\in(0,1)$. At iteration $k$, test $\alpha_k=\eta^m\bar\alpha$ for $m=0,1,2,\ldots$ and take the smallest nonnegative integer $m$ for which

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)
\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
$$

If the trial fails, multiply it by $\eta$ and test again. The accepted inequality compares the candidate objective with a sufficient-decrease threshold; its direction and squared gradient norm are essential. Once accepted, use the standard update with that $\alpha_k$.

The phrase “smallest nonnegative integer” fixes the search order. Begin with $m=0$, so the first candidate is the full trial $\bar\alpha$. Only after a failed inequality should the code increase $m$ and contract the candidate. Accepting the first passing value prevents later, smaller candidates from replacing it within the same search. The parameters have separate roles: $\bar\alpha$ initializes the trial, $\eta$ determines each contraction, and $c$ sets the sufficient-decrease threshold. All three stated range conditions remain attached to the procedure.

The following self-contained trace compares the selected constant step with backtracking on a two-variable objective. It uses a fixed number of iterations so that the trace focuses on the update and accepted steps.

```python
import numpy as np

def f(x):
    return 0.5 * (x[0] ** 2 + 4.0 * x[1] ** 2)

def grad(x):
    return np.array([x[0], 4.0 * x[1]], dtype=float)

def constant_step_trace(x0, iterations):
    x = np.array(x0, dtype=float)
    L = 4.0
    alpha = 1.0 / L
    trace = []
    for k in range(iterations):
        trace.append((k, f(x), alpha, x.copy()))
        x = x - alpha * grad(x)
    trace.append((iterations, f(x), alpha, x.copy()))
    return trace

def armijo_trace(x0, iterations):
    x = np.array(x0, dtype=float)
    bar_alpha = 1.0
    eta = 0.5
    c = 0.25
    trace = []
    for k in range(iterations):
        g = grad(x)
        m = 0
        alpha = bar_alpha
        while f(x - alpha * g) > f(x) - c * alpha * np.dot(g, g):
            m += 1
            alpha = (eta ** m) * bar_alpha
        trace.append((k, f(x), alpha, m, x.copy()))
        x = x - alpha * g
    trace.append((iterations, f(x), None, None, x.copy()))
    return trace

np.set_printoptions(precision=4, suppress=True)
print("constant step")
for row in constant_step_trace([2.0, -1.0], 5):
    print(row)

print("armijo backtracking")
for row in armijo_trace([2.0, -1.0], 5):
    print(row)
```

In the backtracking rows, $m$ records how many contractions were needed and $\alpha_k$ is the accepted step. The trace is evidence of what this particular computation does, not a replacement for the assumption-dependent guarantees above.
