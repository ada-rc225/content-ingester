# Gradient Descent: Assumptions, Descent, and Rates

<!-- section: SEC-01 -->
## The optimisation problem

We study the unconstrained problem

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where $f:\mathbb{R}^d\to\mathbb{R}$ is at least continuously differentiable, written $f\in C^1$. A point $x$ is therefore a vector of $d$ real decision variables, while $f(x)$ is a scalar objective value. “Unconstrained” matters: every vector in $\mathbb{R}^d$ is admissible. Adding a restriction on $x$ would define a different problem setting.

The gradient $\nabla f(x)$ collects the first partial derivatives. It describes the local first-order change of the objective and will be the only derivative used by the method in this lesson. The central questions are not merely how to write an iteration, but which assumptions let us deduce decrease and convergence from it.

<!-- section: SEC-02 -->
## What a local minimiser must satisfy

Suppose $x^*$ is a local minimiser and $f$ is differentiable at $x^*$. The first-order necessary condition is

$$
\nabla f(x^*)=0.
$$

This is a one-way implication: differentiable local minimiser implies stationary point. Stationarity alone is not sufficient to identify a minimum without additional assumptions. Thus a small or zero gradient is naturally connected to the search for a minimiser, but it does not by itself classify the point. Gradient descent will move using the current gradient; the condition above explains why vanishing gradients are relevant while keeping the logical limitation explicit.

The condition can be read direction by direction. At a differentiable local minimum, moving a sufficiently small amount along either sign of any direction cannot give a first-order decrease. The directional first-order change must therefore vanish in every direction. Since that change is the inner product of the gradient with the chosen direction, the only gradient vector compatible with all directions is the zero vector. This reasoning establishes necessity only. It gives no licence to reverse the implication, so a stationary point encountered in a nonconvex objective has not been certified as a minimum by this condition.

<!-- section: SEC-03 -->
## Norms and Lipschitz change

For $z\in\mathbb{R}^d$, the Euclidean norm is

$$
\|z\|_2=\sqrt{z^Tz},
$$

and $\|x-y\|_2$ measures the Euclidean distance between two vectors. If $G$ is a vector-valued map, then for $L>0$ it is $L$-Lipschitz when

$$
\|G(x)-G(y)\|_2\le L\|x-y\|_2
$$

for every pair $x,y$ in its domain. Read this as a comparison: the change in the output vector is no more than $L$ times the change in the input vector. For example, if $G(x)=2x$, then

$$
\|G(x)-G(y)\|_2=2\|x-y\|_2,
$$

so the inequality holds with $L=2$. This example is only about a vector map. When $G$ is a gradient, the same form controls changes in gradient vectors; it is not a claim that $|f(x)-f(y)|$ is bounded in this way.

For a component-level reading, take $z=(3,4)^T$. Then $z^Tz=3^2+4^2=25$ and $\|z\|_2=5$. If two points differ by this vector, their Euclidean distance is five. A Lipschitz inequality compares two nonnegative lengths of this kind. The left length belongs to the output space and the right length belongs to the input space, scaled by $L$. It does not compare vectors component by component. This norm-based reading is especially useful for a gradient map because gradients at two points may change direction as well as magnitude.

<!-- section: SEC-04 -->
## Smoothness as a gradient assumption

A continuously differentiable function is called $L$-smooth, with $L>0$, if its gradient is $L$-Lipschitz in the Euclidean norm:

$$
\|\nabla f(x)-\nabla f(y)\|
\le L\|x-y\|,
\qquad \forall x,y\in\mathbb{R}^d.
$$

The quantifier is global: the same positive constant must work for every pair of points. Geometrically, this limits how quickly the gradient vector can change as the point moves. It does not say that the objective is convex, and it does not replace the gradient-difference expression by a function-value difference. Smoothness will support an upper model for $f$ and will qualify the step-size and convergence statements that follow.

<!-- section: SEC-05 -->
## The current-gradient update

Given $x_0\in\mathbb{R}^d$ and positive step sizes $\alpha_k$, gradient descent uses

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),
\qquad k=0,1,2,\ldots.
$$

The gradient is evaluated at the current iterate $x_k$, and the subtraction sign makes the step point opposite to that gradient. The formula defines the iteration; decrease requires appropriate assumptions and step choices. Here is a self-contained trace for a two-dimensional quadratic objective. It deliberately performs a fixed number of updates rather than introducing a separate stopping rule.

```python
import numpy as np

def f(x):
    return 0.5 * (x[0] ** 2 + 4.0 * x[1] ** 2)

def grad_f(x):
    return np.array([x[0], 4.0 * x[1]])

x = np.array([2.0, -1.0])
alpha = 0.25
for k in range(5):
    print(k, x.copy(), f(x))
    x = x - alpha * grad_f(x)
print(5, x, f(x))
```

The first line of the trace starts at $x_0=(2,-1)^T$. Its gradient is $(2,-4)^T$, so with $\alpha=1/4$ the update subtracts $(1/2,-1)^T$ and gives $x_1=(3/2,0)^T$. Every subsequent printed point is obtained in exactly the same order: evaluate the gradient at the displayed point, multiply it by the positive step, and subtract. This small calculation illustrates the indexing and signs in the rule. Its observed values are properties of this chosen quadratic and this chosen step; the trace is not being used to assert a guarantee for an arbitrary differentiable function.

<!-- section: SEC-06 -->
## The quadratic upper bound

If $f$ is $L$-smooth, then for every $x,y\in\mathbb{R}^d$ the Descent Lemma gives

$$
f(y)\le f(x)+\langle\nabla f(x),y-x\rangle
+\frac{L}{2}\|y-x\|^2.
$$

Here $\langle u,v\rangle=u^Tv$ is a scalar inner product and $\|v\|^2$ is the squared Euclidean norm. The right-hand side is an upper model consisting of the value at $x$, a linear change, and a positive quadratic allowance. The inequality direction and the coefficient $L/2$ are essential.

Substitute the gradient-descent candidate $y=x-\alpha\nabla f(x)$. Then $y-x=-\alpha\nabla f(x)$, so

$$
f(y)\le f(x)-\alpha\left(1-\frac{L\alpha}{2}\right)
\|\nabla f(x)\|^2.
$$

This substitution shows analytically how the upper bound relates a step to possible decrease; it does not remove the smoothness assumption.

The algebra is worth following carefully. The inner-product term becomes $\langle\nabla f(x),-\alpha\nabla f(x)\rangle=-\alpha\|\nabla f(x)\|^2$. The quadratic term becomes $(L/2)\alpha^2\|\nabla f(x)\|^2$. Factoring their sum produces the displayed coefficient. Thus the negative linear contribution and positive quadratic allowance compete. This is the precise role of the upper model: it turns the geometric choice of the negative-gradient direction into an inequality for objective values. The conclusion remains an upper bound on the proposed value, not an equality describing every objective.

<!-- section: SEC-07 -->
## Inner products and convex sets

For real vectors $u$ and $v$ of the same dimension, $u^Tv$ is the scalar sum of their componentwise products. To parse $g^T(y-x)$, first form the displacement $d=y-x$, then compute $g^Td$. Its sign describes the alignment between $g$ and that displacement; this arithmetic alone proves no convexity statement.

For $\theta\in[0,1]$, the point $\theta x+(1-\theta)y$ is a convex combination. A set is convex when it contains every such combination of every pair of its points. For example, with $x=(0,0)^T$, $y=(2,4)^T$, and $\theta=1/4$, the combination is $(3/2,3)^T$. If $g=(1,-1)^T$, then $g^T(y-x)=-2$. These calculations prepare the notation used next; they are not themselves an optimisation theorem.

As $\theta$ moves from zero to one, the convex combination moves along the line segment from $y$ to $x$. The definition of a convex set says that the whole segment stays in the set. Separately, the inner product $g^T(y-x)$ compresses two vectors into one scalar. A negative value means that $g$ and the displacement have negative alignment, a positive value means positive alignment, and zero means their inner product vanishes. These are interpretations of the arithmetic. An inequality involving $f$ needs an additional function-level assumption, which is supplied in the next section rather than smuggled into this prerequisite notation.

<!-- section: SEC-08 -->
## The global first-order convexity bound

A differentiable function $f:\mathbb{R}^d\to\mathbb{R}$ is convex when, for all $x,y\in\mathbb{R}^d$,

$$
f(y)\ge f(x)+\langle\nabla f(x),y-x\rangle.
$$

This is a global lower bound: the first-order affine expression based at $x$ lies below the objective at every $y$. Notice the contrast with the smoothness upper bound. Convexity supplies the lower inequality, whereas smoothness supplies a quadratic upper inequality; neither assumption silently implies the other here.

If a convex differentiable objective has a stationary point $x^*$, substituting $x=x^*$ makes the inner-product term zero and yields $f(y)\ge f(x^*)$ for every $y$. In this convex setting, stationarity therefore has a global consequence that it did not have under differentiability alone.

The base point and comparison point play distinct roles. The gradient is evaluated at $x$, and the displacement points from $x$ to $y$. The inequality then compares the actual value at $y$ with the first-order expression built at $x$. Reversing the inequality would turn a global lower bound into a different and incorrect statement. Keeping “for all $x,y$” attached to the formula is also essential: convexity here is not a claim about one convenient pair of points or only about points generated by gradient descent.

<!-- section: SEC-09 -->
## Strong convexity

For $\mu>0$, the function is $\mu$-strongly convex when, for all $x,y\in\mathbb{R}^d$,

$$
f(y)\ge f(x)+\langle\nabla f(x),y-x\rangle
+\frac{\mu}{2}\|y-x\|^2.
$$

Compared with the convex lower bound, this adds a positive quadratic term with coefficient $\mu/2$. The strengthening is quantitative: as $y$ moves away from $x$, the lower model includes a squared-distance contribution. The positivity of $\mu$, the plus sign, and the coefficient are all part of the assumption. Strong convexity is not being inferred from differentiability or smoothness; it is an additional hypothesis used for the stronger rate statements later.

Compare the two lower models at the same $x$ and $y$. Convexity retains the value and linear term. Strong convexity retains both and adds a quantity that is nonnegative because it is a positive multiple of a squared norm. When $x=y$, that added quantity is zero; away from $x$, it is positive. This comparison explains the word “strong” without introducing a different test for the property. In every later use, $\mu$ refers to the positive constant in this particular global inequality.

<!-- section: SEC-10 -->
## Ratios of smoothness and strong convexity

For positive constants satisfying $0<\mu\le L$, define

$$
\kappa=\frac{L}{\mu}.
$$

Dividing $0<\mu\le L$ by the positive number $\mu$ gives $\kappa\ge1$. The ratio records the multiplicative separation of the constants: if $L=12$ and $\mu=3$, then $\kappa=4$, so $L$ is four times $\mu$; if $L=\mu$, then $\kappa=1$. A larger value means a wider multiplicative separation. This ratio requires $\mu>0$ and must not be treated as finite when $\mu=0$. The discussion concerns only $L/\mu$, not a different matrix or numerical condition measure.

The units in the numerator and denominator cancel in the ratio, so $\kappa$ records relative rather than additive separation. For instance, increasing from $(L,\mu)=(4,2)$ to $(8,4)$ leaves the ratio equal to two: both constants doubled, but their multiplicative separation stayed the same. By contrast, $(L,\mu)=(8,2)$ gives four. These are ratio calculations only. They do not select a step size and do not derive a convergence rate; those uses occur only after the relevant objective assumptions and algorithmic choices have been stated.

<!-- section: SEC-11 -->
## Conditioning of the objective

When the same objective is both $L$-smooth and $\mu$-strongly convex, its condition number is

$$
\kappa=\frac{L}{\mu}\ge1.
$$

The two assumptions are both needed for this definition in our setting. The ratio will appear directly in a contraction factor, connecting an assumption-level comparison of $L$ and $\mu$ to a rate-level statement. Keep the order of the ratio fixed: it is $L$ divided by $\mu$, not its reciprocal. The later formulas make the interpretation precise, so no convergence conclusion follows merely from computing the ratio here.

<!-- section: SEC-12 -->
## Constant step sizes

A constant-step method sets $\alpha_k=\alpha$ at every iteration. When $L$ is known, a common choice is

$$
\alpha=\frac{1}{L}.
$$

Under the usual smooth convex assumptions, another stated range is $\alpha\in(0,2/L)$. That interval is not an assumption-free prescription. Its smoothness and convexity qualification must remain attached to it, just as the choice $1/L$ presumes that $L$ is known.

The Descent Lemma substitution makes the role of size visible. With $\alpha=1/L$, its coefficient becomes

$$
\alpha\left(1-\frac{L\alpha}{2}\right)=\frac{1}{2L},
$$

so the upper model yields $f(x_{k+1})\le f(x_k)-\|\nabla f(x_k)\|^2/(2L)$. This is the constant step used in the smooth-convex objective-gap result.

A useful discipline is to label a formula by both its rule and its hypotheses. “Constant step” says only that the same positive number is reused; it does not identify that number or guarantee decrease. “Step $1/L$” additionally identifies a value based on a known smoothness constant. The interval statement adds its smooth-convex qualification. These are progressively more specific claims, not interchangeable descriptions. In particular, the convergence theorem in the next section uses exactly $1/L$, so its conclusion should not be silently attached to every constant inside the wider interval.

<!-- section: SEC-13 -->
## A smooth-convex objective-gap rate

Assume $f$ is $L$-smooth and convex, a global minimiser $x^*$ exists, and gradient descent uses $\alpha_k=1/L$. For every $k\ge1$,

$$
f(x_k)-f(x^*)\le
\frac{L\|x_0-x^*\|^2}{2k}.
$$

Here is the assumption-to-conclusion mechanism. Convexity with $y=x^*$ bounds the current objective gap using $\langle\nabla f(x_k),x_k-x^*\rangle$. Expanding $\|x_{k+1}-x^*\|^2$ under the update introduces that inner product and a squared-gradient term. The descent inequality from the preceding section controls the squared-gradient term. Combining them gives


$$
\|x_{k+1}-x^*\|^2
\le \|x_k-x^*\|^2
-\frac{2}{L}\bigl(f(x_{k+1})-f(x^*)\bigr).
$$

Summing this inequality telescopes the squared distances. Because the same step also makes objective values nonincreasing, the final gap is no greater than the average of the first $k$ gaps, producing the displayed bound. Its $O(1/k)$ meaning is that the guaranteed upper bound is proportional to $1/k$; it is an objective-value statement under all the listed hypotheses, not an unconditional claim about every differentiable objective.

To see the telescoping explicitly, rearrange the intermediate inequality so that

$$
f(x_{i+1})-f(x^*)
\le \frac{L}{2}\left(\|x_i-x^*\|^2-\|x_{i+1}-x^*\|^2\right).
$$

Adding this from $i=0$ through $i=k-1$ cancels every intermediate squared distance, leaving at most $L\|x_0-x^*\|^2/2$. The nonincreasing objective values imply that each earlier gap in this sum is at least the final gap. Hence the sum is at least $k\bigl(f(x_k)-f(x^*)\bigr)$, and division by the positive integer $k$ gives the theorem. This chain also identifies the roles of the assumptions: smoothness supplies decrease, convexity relates the gradient to a global minimiser, and the specified step aligns the coefficients.

<!-- section: SEC-14 -->
## Strongly convex contractions

Now assume together that $f$ is $L$-smooth and $\mu$-strongly convex, and write $\kappa=L/\mu$. Two guarantees must be paired with their own step sizes. With

$$
\alpha=\frac{2}{L+\mu},
$$

the squared distance to the minimiser satisfies

$$
\|x_k-x^*\|^2
\le
\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}
\|x_0-x^*\|^2.
$$

With the different choice $\alpha=1/L$, the objective gap satisfies

$$
f(x_k)-f(x^*)
\le
\left(1-\frac{\mu}{L}\right)^k
\bigl(f(x_0)-f(x^*)\bigr).
$$

These are two distinct pairings: the first controls squared distance and the second controls objective gap. Since $\mu/L=1/\kappa$, the second contraction factor exposes conditioning directly. When $\kappa$ is larger, that factor is closer to one, so its guaranteed contraction per iteration is weaker. This interpretation remains conditional on both smoothness and strong convexity; no Hessian-based derivation is needed here.

The powers make these linear contraction statements different in form from the preceding reciprocal bound. In the distance statement, the base $((\kappa-1)/(\kappa+1))^2$ is raised to $k$ through the exponent $2k$ as displayed. In the objective statement, the base $1-\mu/L$ is raised directly to $k$. At $k=0$, each right side recovers its initial quantity; subsequent powers express repeated contraction. The formulas must not be cross-paired: using $2/(L+\mu)$ belongs with the squared-distance formula, while using $1/L$ belongs with the objective-gap formula.

<!-- section: SEC-15 -->
## Armijo backtracking

When a fixed step is not being used, Armijo backtracking offers a traceable alternative. Choose an initial trial step $\bar\alpha>0$, a contraction factor $\eta\in(0,1)$, and $c\in(0,1)$. For $m=0,1,2,\ldots$, form $\alpha_k=\eta^m\bar\alpha$ and accept the smallest nonnegative $m$ for which

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)
\le f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
$$

The left side evaluates the proposed next point. The right side demands sufficient decrease relative to the current value, the step, and the squared gradient norm. If a trial fails, multiplying by $\eta$ contracts it; the inequality is never reversed.

```python
import numpy as np

def f(x):
    return 0.5 * (x[0] ** 2 + 4.0 * x[1] ** 2)

def grad_f(x):
    return np.array([x[0], 4.0 * x[1]])

x = np.array([2.0, -1.0])
bar_alpha, eta, c = 1.0, 0.5, 0.25
g = grad_f(x)
m = 0
alpha = bar_alpha
while f(x - alpha * g) > f(x) - c * alpha * np.dot(g, g):
    m += 1
    alpha = (eta ** m) * bar_alpha

x_next = x - alpha * g
print("m =", m, "alpha =", alpha)
print("accepted:", f(x_next) <= f(x) - c * alpha * np.dot(g, g))
print("x_next =", x_next, "f(x_next) =", f(x_next))
```

This block starts at $m=0$ and increments in order, so the accepted value is the smallest tested nonnegative integer satisfying the stated condition. The resulting point still uses the current-gradient update; only the step-selection rule has changed.

Read the loop as a direct translation of the mathematics. Before any contraction, $m=0$ gives $\alpha_k=\eta^0\bar\alpha=\bar\alpha$. The loop condition is the negation of acceptance: it continues precisely while the proposed value is greater than the sufficient-decrease threshold. Each failure increases $m$ by one and recomputes the contracted trial from $\eta^m\bar\alpha$. When the loop ends, the acceptance inequality holds, and only then is the next iterate formed. The squared norm in the formula appears in code as the gradient’s inner product with itself. Nothing in this procedure changes the gradient evaluation point from $x_k$.
