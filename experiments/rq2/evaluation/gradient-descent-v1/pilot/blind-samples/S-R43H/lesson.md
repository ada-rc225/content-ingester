# Gradient Descent: Assumptions, Rates, and Reliable Step Selection

Gradient descent is a first-order method for moving through a differentiable objective landscape. This lesson develops the method from its mathematical setting, through the assumptions that justify useful inequalities, to convergence rates and practical step selection. The central habit is to keep each conclusion attached to the assumptions that support it. A stationary point need not be a minimum, convexity is a global property, and a convergence guarantee for one step size cannot automatically be transferred to another.

<!-- section: SEC-01 -->
## The unconstrained optimisation problem

In unconstrained optimisation, the variable is a vector $x\in\mathbb{R}^d$, and the objective is a continuously differentiable function $f:\mathbb{R}^d\to\mathbb{R}$. The problem is

$$
\min_{x\in\mathbb{R}^d} f(x).
$$

“Unconstrained” means that every vector in $\mathbb{R}^d$ is an admissible candidate; there are no equality or inequality constraints restricting the search region. The differentiability assumption makes the gradient available as a local description of how the objective changes. It does not by itself make the objective convex, guarantee a minimiser, or guarantee that an iterative method will converge. Those are separate structural or algorithmic questions.

For an applied-mathematical analysis, it is useful to distinguish three objects: the function value $f(x)$, the point $x$, and the gradient vector $\nabla f(x)$. The method will alter the point using the gradient, while the theorems will measure progress using either distance to a minimiser or objective-value gap.

<!-- section: SEC-02 -->
## Stationarity is necessary at a differentiable local minimum

Suppose $x^*$ is a local minimiser and $f$ is differentiable at $x^*$. Then the first-order necessary condition is

$$
\nabla f(x^*)=0.
$$

The word “necessary” matters. The equation says that there is no first-order directional slope at the local minimiser. It does not say that every point with zero gradient is a minimum. A stationary point may instead be a local maximum or a saddle point. Therefore, when gradient descent approaches a point with a small gradient, that observation alone does not classify the point or establish global optimality.

This condition explains why the gradient is a natural search direction: away from stationarity, it records first-order change. Gradient descent uses the negative gradient because, for a sufficiently small positive step, it is the direction suggested by the local linear term for reducing the objective.

<!-- section: SEC-03 -->
## A short bridge: norms and Lipschitz continuity

For a vector $z\in\mathbb{R}^d$, its Euclidean norm is

$$
\|z\|_2=\sqrt{z^Tz},
$$

and $\|x-y\|_2$ measures the Euclidean distance between two points. For example, if $z=(3,4)^T$, then $\|z\|_2=5$. A vector-valued map $G$ is $L$-Lipschitz when, for all points in its domain,

$$
\|G(x)-G(y)\|_2\le L\|x-y\|_2,
$$

where $L>0$. The output-vector change is therefore bounded by $L$ times the input-vector change. When $G$ is a gradient map, this compares changes in gradient vectors. It is not a statement that function values satisfy $|f(x)-f(y)|\le L\|x-y\|_2$.

As a small vector-map example, let $G(x)=2x$. Then $G(x)-G(y)=2(x-y)$, so $\|G(x)-G(y)\|_2=2\|x-y\|_2$. Thus $G$ is Lipschitz with constant $2$. This example only illustrates the norm inequality; it does not assert a gradient-descent result.

<!-- section: SEC-04 -->
## Smoothness of the gradient

A continuously differentiable objective is called $L$-smooth when its gradient is $L$-Lipschitz in the Euclidean norm:

$$
\|\nabla f(x)-\nabla f(y)\|_2\le L\|x-y\|_2,
\qquad\forall x,y\in\mathbb{R}^d,
$$

with $L>0$. This is a global assumption: the same constant controls every pair of points. It says that the gradient cannot change arbitrarily rapidly relative to the distance moved. It does not say that $f$ is convex, and it does not say that the function values themselves are Lipschitz.

The distinction between local differentiability and global gradient smoothness is important. Differentiability supplies a gradient at each point. Smoothness supplies a uniform comparison between gradients at all points. The latter is what permits a global quadratic upper bound and makes a globally selected step size meaningful in the results that follow.

<!-- section: SEC-05 -->
## The current-gradient update

Starting from $x_0\in\mathbb{R}^d$ and using positive step sizes $\alpha_k$, gradient descent updates the current iterate by

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),
\qquad k=0,1,2,\ldots.
$$

The gradient is evaluated at the current point $x_k$, not at a future or look-ahead point. The minus sign points opposite to the gradient, and positivity of $\alpha_k$ controls how far the method moves in that direction. A single iteration has three pieces: evaluate $f$'s gradient at $x_k$, multiply it by the chosen positive step, and subtract the result from $x_k$.

The update is a rule, not yet a convergence theorem. Its behaviour depends on the objective's structure and on how the step sizes are selected. In particular, a step that is too large can invalidate a local descent intuition even when the gradient is informative.

```python
import numpy as np

x = np.array([2.0, -1.0])
alpha = 0.25
gradient = 2.0 * x
next_x = x - alpha * gradient
print(next_x)
```

For this self-contained trace, the gradient is the gradient of $f(x)=\|x\|_2^2$ at the displayed point. The code implements only the current-gradient update; it does not add a stopping rule or claim a general convergence guarantee.

<!-- section: SEC-06 -->
## The Descent Lemma: a quadratic upper bound

If $f$ is $L$-smooth, then for every $x,y\in\mathbb{R}^d$,

$$
f(y)\le f(x)+\langle\nabla f(x),y-x\rangle+\frac{L}{2}\|y-x\|_2^2.
$$

The right-hand side combines a value at $x$, a linear prediction using the gradient, and a quadratic allowance for curvature. The inequality is an upper bound, not a lower bound. The coefficient is exactly $L/2$. These details matter because the bound will be evaluated at a gradient-descent trial point.

Set $y=x-\alpha\nabla f(x)$. Then $y-x=-\alpha\nabla f(x)$, so the inner-product term becomes $-\alpha\|\nabla f(x)\|_2^2$ and the squared-norm term becomes $\alpha^2\|\nabla f(x)\|_2^2$. Consequently,

$$
f(x-\alpha\nabla f(x))
\le f(x)-\left(\alpha-\frac{L\alpha^2}{2}\right)\|\nabla f(x)\|_2^2.
$$

This expression displays the step-size trade-off: the linear decrease is opposed by a quadratic curvature allowance. It is a sufficient analytic mechanism for descent under suitable positive choices of $\alpha$.

<!-- section: SEC-07 -->
## A short bridge: inner products and convex sets

For real vectors $u$ and $v$ of the same dimension, $u^Tv$ is the scalar sum of componentwise products. If $d=y-x$, then $g^T(y-x)=g^Td$ is the inner product of $g$ with the displacement. Its sign describes alignment: a negative value means that the vectors have an obtuse-angle relationship, while a positive value means that they point partly in the same direction.

For $\theta\in[0,1]$, the vector $\theta x+(1-\theta)y$ is a convex combination. A set is convex if it contains this combination for every pair of its points and every such $\theta$. For instance, with $x=(0,0)^T$, $y=(2,4)^T$, and $\theta=1/4$, the combination is $(3/2,3)^T$. With $g=(1,-1)^T$, $g^T(y-x)=-2$. These calculations explain notation used in the next result; neither calculation alone proves convexity or an optimisation conclusion.

<!-- section: SEC-08 -->
## Differentiable convexity as a global first-order bound

A differentiable function is convex when, for all $x,y\in\mathbb{R}^d$,

$$
f(y)\ge f(x)+\langle\nabla f(x),y-x\rangle.
$$

Unlike the local stationarity condition, this is a global comparison between every pair of points. The tangent-plane expression at $x$ lies below the function value at $y$. The inequality direction is therefore lower-bound direction. Convexity supplies a relationship between the gradient at the current iterate and objective gaps to a minimiser; smoothness supplies an upper-bound relationship that controls a trial step. Convergence proofs combine these two complementary inequalities.

Convexity alone does not imply that a particular implementation reaches a minimiser in finite time. The theorem used later also requires smoothness, existence of a global minimiser, and a specified step size. Keeping those hypotheses visible prevents a rate statement from being overextended.

<!-- section: SEC-09 -->
## Strong convexity adds quadratic growth

For $\mu>0$, a differentiable function is $\mu$-strongly convex when, for all $x,y\in\mathbb{R}^d$,

$$
f(y)\ge f(x)+\langle\nabla f(x),y-x\rangle+\frac{\mu}{2}\|y-x\|_2^2.
$$

This strengthens the convex lower bound by adding a positive quadratic term. Strong convexity is not merely a statement that the graph “looks curved” near one point; it is a global inequality with the same positive parameter $\mu$ for every pair. The positive sign and the coefficient $\mu/2$ are part of the definition.

Because the added term grows with distance, strong convexity gives more information than ordinary convexity. It supports a contraction analysis, but only when paired with smoothness and the step size stated in the corresponding result. The presence of a strong-convexity parameter must never be silently assumed for an arbitrary differentiable objective.

<!-- section: SEC-10 -->
## A short bridge: ratios and the condition number

When an objective is both $L$-smooth and $\mu$-strongly convex, with $0<\mu\le L$, define the condition number

$$
\kappa=\frac{L}{\mu}\ge1.
$$

The inequality $\kappa\ge1$ follows by dividing $\mu\le L$ by the positive number $\mu$. If $L=12$ and $\mu=3$, then $\kappa=4$: the smoothness scale is four times the strong-convexity scale. If $L=\mu$, then $\kappa=1$. The ratio is meaningful only when $\mu>0$; it is not a finite condition ratio when $\mu=0$.

A larger ratio represents greater multiplicative separation between the two constants. In the strongly convex rates below, this separation appears directly in the contraction factors. This is a condition ratio for the pair of constants in the present analysis, not a claim about every matrix or numerical-linear-algebra condition number.

<!-- section: SEC-11 -->
## How conditioning changes the rate picture

The condition ratio helps interpret why two objectives with the same general algorithm can exhibit different progress. If $L$ and $\mu$ are close, then $\kappa$ is near one, and the contraction factor involving $(\kappa-1)/(\kappa+1)$ is small. If $L$ is much larger than $\mu$, then $\kappa$ is large and that factor is closer to one, so more iterations may be needed for a comparable reduction. This is an interpretation of the stated contraction, not a new convergence theorem.

The parameters also constrain step-size choices. $L$ controls how quickly gradients may vary, while $\mu$ supplies the positive quadratic growth used by the stronger result. A sound rate discussion therefore reports the assumptions, the step size, the quantity being contracted, and the factor together. Reporting only a phrase such as “linear convergence” hides the information needed to interpret the bound.

<!-- section: SEC-12 -->
## Constant step sizes under smoothness

A constant-step implementation sets $\alpha_k=\alpha$ for every iteration. When $L$ is known, a common choice is

$$
\alpha=\frac{1}{L}.
$$

Under the usual smooth-convex assumptions, another source-stated admissible interval is $\alpha\in(0,2/L)$. The qualifier belongs to the interval: it must not be presented as a universal rule for every differentiable objective. Likewise, knowing a numerical value of $L$ does not by itself supply convexity or a minimiser.

The choice $1/L$ is especially important because it is the step paired with the smooth-convex objective-gap theorem and with the strongly convex objective contraction below. The step controls the algorithm, while the assumptions control which theorem can be invoked. If $L$ is unknown or poorly estimated, a practical alternative is to test trial steps using a sufficient-decrease condition rather than silently treating an estimate as exact.

It is helpful to separate three questions when diagnosing an iteration. First, is the update coded with the gradient at the current point and a positive step? Second, does the chosen step satisfy the assumptions of the result being cited? Third, is the reported quantity the one controlled by that result: objective gap, squared distance, or merely the sufficient decrease observed at one trial? These questions prevent a successful numerical decrease from being mistaken for a proof of convergence. They also make comparisons reproducible: two runs should report their objective, gradient norm, step rule, and stopping convention rather than only the final point.

For a quadratic illustration, the scales can be read geometrically without claiming that every objective is quadratic. A large variation in curvature corresponds to a large separation between the smoothness and strong-convexity parameters. A conservative fixed step must respect the larger scale, while progress toward the minimiser is influenced by the smaller scale. The condition ratio records this tension compactly. It is a summary used by the selected theorem, not an instruction to replace the objective by a quadratic model.

<!-- section: SEC-13 -->
## Smooth-convex objective-gap convergence

Assume that $f:\mathbb{R}^d\to\mathbb{R}$ is $L$-smooth and convex, that $x^*$ is a global minimiser, and that gradient descent uses $\alpha_k=1/L$. Then, for $k\ge1$,

$$
f(x_k)-f(x^*)\le\frac{L\|x_0-x^*\|_2^2}{2k}.
$$

The right side decreases proportionally to $1/k$, which is the meaning of the $O(1/k)$ objective-gap rate here. It is a bound on the difference in objective values, not directly a bound on $\|x_k-x^*\|_2$. Every hypothesis is active: smoothness supports the upper bound, convexity supplies the global first-order relation, $x^*$ must be a global minimiser, and the step must be exactly $1/L$.

The result is asymptotic in its iteration description. It does not say that the gap is zero after a fixed number of steps, nor does it apply unchanged to a nonconvex objective, an unavailable global minimiser, or an arbitrary step sequence. In an application, the initial distance and the scale $L$ also affect the numerical size of the bound.

<!-- section: SEC-14 -->
## Strongly convex contractions

Assume now that $f$ is $L$-smooth and $\mu$-strongly convex. Let $x^*$ denote the minimiser and let $\kappa=L/\mu$. Two different statements use two different step sizes. With

$$
\alpha=\frac{2}{L+\mu},
$$

the squared distance satisfies

$$
\|x_k-x^*\|_2^2\le
\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}
\|x_0-x^*\|_2^2.
$$

With $\alpha=1/L$, the objective gap satisfies

$$
f(x_k)-f(x^*)\le
\left(1-\frac{\mu}{L}\right)^k
\bigl(f(x_0)-f(x^*)\bigr).
$$

The first bound contracts squared distance and is paired with $2/(L+\mu)$. The second contracts objective gap and is paired with $1/L$. Swapping these pairings would change the claim. Strong convexity is required for both statements, and the factors expose the role of conditioning through $\kappa=L/\mu$.

These rates are stronger than the smooth-convex $O(1/k)$ description because their factors are raised to the iteration count. They still remain conditional guarantees: they do not certify performance for an arbitrary differentiable objective or for a step selected without regard to the stated result.

<!-- section: SEC-15 -->
## Armijo backtracking as a bounded alternative

When a constant step is inconvenient, Armijo backtracking starts with a positive trial step $\bar\alpha>0$. Choose $\eta\in(0,1)$ and $c\in(0,1)$. For the current iterate, test steps of the form

$$
\alpha_k=\eta^m\bar\alpha,
$$

and choose the smallest integer $m\ge0$ for which

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)
\le f(x_k)-c\alpha_k\|\nabla f(x_k)\|_2^2.
$$

The procedure contracts the positive trial step until this sufficient-decrease inequality is satisfied. The squared gradient norm must remain in the acceptance test, and the inequality direction is a decrease condition. Backtracking adapts the trial length to observed function values, but this description does not attach the fixed-step convergence rates above to Armijo automatically.

```python
import numpy as np

x = np.array([2.0, -1.0])
eta = 0.5
c = 1e-4
trial = 1.0

def f(z):
    return float(np.dot(z, z))

def grad(z):
    return 2.0 * z

g = grad(x)
m = 0
while True:
    alpha = (eta ** m) * trial
    candidate = x - alpha * g
    if f(candidate) <= f(x) - c * alpha * np.dot(g, g):
        break
    m += 1
print(alpha, candidate)
```

The implementation fixes all inputs locally, uses a deterministic objective, and applies the smallest accepted nonnegative exponent. In a real computation, termination criteria would also need to address a small gradient, a small step, or a prescribed iteration limit; those practical criteria are separate from the mathematical acceptance rule.

## Synthesis

Gradient descent is the update $x_{k+1}=x_k-\alpha_k\nabla f(x_k)$, but its guarantees come from a structured chain. Smoothness yields a quadratic upper bound. Convexity supplies a global first-order lower bound, while strong convexity adds positive quadratic growth. The ratio $L/\mu$ describes the separation of the two scales. A constant step such as $1/L$ supports the selected objective-gap results under their hypotheses, while Armijo backtracking offers a sufficient-decrease mechanism for choosing a step. At every use, state what is assumed, what quantity is measured, and which step-size pairing makes the conclusion valid.
