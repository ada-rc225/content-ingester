# Gradient Descent: From an Engineering Objective to Convergence Guarantees

Gradient descent is a first-order method for adjusting a vector of parameters to reduce a differentiable objective. In this lesson, an idealized mechanical-engineering calibration provides the setting, while the mathematics states exactly when decrease or convergence is supported. The setting is deliberately limited: real engineering objectives need not have the properties used in the guarantees, a stationary point need not be a physical optimum, and gradient descent is not automatically suitable for every design problem.

<!-- section: SEC-01 -->
## An idealized engineering objective

Suppose a vector $x\in\mathbb{R}^d$ collects adjustable model parameters. An idealized calibration objective $f(x)$ might summarize mismatch between model predictions and selected measurements, while an idealized energy objective might assign a scalar energy to a configuration. In either framing, the mathematical problem considered here is the unconstrained problem

\[
\min_{x\in\mathbb{R}^d} f(x),
\]

where $f:\mathbb{R}^d\to\mathbb{R}$ is at least continuously differentiable, written $f\in C^1$. Thus every real vector is in the mathematical search domain; adding parameter bounds or other constraints would define a different problem. The objective converts each candidate vector into one scalar value, and lower values are preferred within this idealized model. The dimension $d$ counts adjustable components, so one candidate is a complete vector rather than a separate optimization of each component.

This formulation separates the model from the method. First decide what scalar objective is being minimized; then gradient descent generates candidate vectors for that stated objective. That separation is useful in calibration because changing the mismatch definition changes $f$, even if the update rule later retains the same form. The framing still does not assert that every engineering objective has a convenient shape or that its mathematical minimizer is automatically the right physical design.

<!-- section: SEC-02 -->
## Stationarity is necessary, not sufficient

If $x^*$ is a local minimizer and $f$ is differentiable at $x^*$, then the first-order necessary condition is

\[
\nabla f(x^*)=0.
\]

The gradient gathers the partial derivatives with respect to the components of $x$. A zero gradient therefore identifies a stationary point. The direction of the statement matters: differentiable local minimizer implies zero gradient. A zero gradient alone does not guarantee a minimum without additional assumptions.

Read this as a one-way diagnostic. If a differentiable candidate is claimed to be a local minimizer but its gradient is nonzero, it fails the necessary condition. If its gradient is zero, the test is passed but the claim is not proved. Consequently, finding a very small gradient is useful evidence about stationarity in the mathematical objective, but it does not by itself certify global optimality, local minimality, or physical acceptability.

<!-- section: SEC-03 -->
## The gradient-descent update

Starting from $x_0\in\mathbb{R}^d$ and using positive step sizes $\alpha_k$, gradient descent applies

\[
x_{k+1}=x_k-\alpha_k\nabla f(x_k),\qquad k=0,1,2,\ldots.
\]

At iteration $k$, the gradient is evaluated at the current vector $x_k$, multiplied by the positive step size, and subtracted. The sign and evaluation point are essential: this standard update does not evaluate the gradient at a future point. The gradient, step, and updated vector all have compatible dimensions: $\nabla f(x_k)$ is a vector in $\mathbb{R}^d$, while $\alpha_k$ is a positive scalar. A trace should therefore record the current vector, its objective value, and the update index consistently.

To trace one iteration by hand, begin with the recorded current vector, evaluate every component of the gradient there, scale the resulting vector by the current positive step, and subtract component by component. Label the result with the next index only after those operations are complete. Repeating this layout prevents the current and updated vectors from being mixed in one row.

The following self-contained trace uses an idealized two-parameter quadratic calibration objective. Its purpose is to make the update and iteration history visible, not to claim that all calibration objectives are quadratic.

```python
import numpy as np

A = np.diag([4.0, 1.0])
target = np.array([1.0, -0.5])

def objective(x):
    offset = x - target
    return 0.5 * offset @ A @ offset

def gradient(x):
    return A @ (x - target)

x = np.array([-1.0, 1.5])
alpha = 0.2
print(" k |       x[0]       x[1] |       f(x)")
for k in range(6):
    print(f"{k:2d} | {x[0]:11.6f} {x[1]:11.6f} | {objective(x):10.6f}")
    x = x - alpha * gradient(x)
```

Each printed row records the current parameters before the next update. This makes the sequence $x_0,x_1,\ldots$ traceable rather than hiding it behind a final answer. Comparing adjacent rows also shows exactly which current point supplied the gradient for the next row.

<!-- section: SEC-04 -->
## Norms and bounded changes

Before discussing smoothness, recall how vector changes are measured. For $z\in\mathbb{R}^d$, the Euclidean norm is

\[
\|z\|_2=\sqrt{z^Tz},
\]

and $\|x-y\|_2$ is the Euclidean distance between $x$ and $y$. For a vector-valued map $G$, an $L$-Lipschitz bound with $L>0$ is

\[
\|G(x)-G(y)\|_2\le L\|x-y\|_2
\]

for every pair $x,y$ in the domain. It says that the change in the output vector is at most $L$ times the change in the input vector. The statement compares two norms, so both sides are nonnegative scalars even though $G(x)$ and $G(y)$ are vectors. For example, if $G(x)=2x$, then $\|G(x)-G(y)\|_2=2\|x-y\|_2$, so $L=2$ satisfies the bound.

The constant is a uniform multiplier in the inequality. Checking one pair can illustrate the calculation, but the definition requires the same bound for all pairs in the domain. This distinction between an example and a universal condition is important when the gradient map replaces the generic vector map.

When $G$ is a gradient map, the two output vectors being compared are gradients. One may read the inequality by first calculating the input displacement, then the output-vector difference, and finally their norms. This is specifically a statement about changes in gradient vectors; it is not a statement that bounds $|f(x)-f(y)|$. Keeping those two meanings separate will matter in the next section.

<!-- section: SEC-05 -->
## Smoothness controls gradient variation

A continuously differentiable function is $L$-smooth, for $L>0$, when its gradient is $L$-Lipschitz in the Euclidean norm:

\[
\|\nabla f(x)-\nabla f(y)\|\le L\|x-y\|,
\qquad \text{for all }x,y\in\mathbb{R}^d.
\]

This is an explicit assumption about how rapidly the gradient vector can vary as the parameter vector changes. The universal phrase “for all” is important: the displayed inequality is not merely an observation along one computed iteration history. In an engineering calculation, it must not be inferred merely from the fact that $f$ represents energy or calibration mismatch. Nor should it be confused with function-value Lipschitz continuity. Here $L$ controls the difference between two gradients.

<!-- section: SEC-06 -->
## The quadratic upper bound and decrease

If $f$ is $L$-smooth, the Descent Lemma states that, for all $x,y\in\mathbb{R}^d$,

\[
f(y)\le f(x)+\langle\nabla f(x),y-x\rangle
+\frac{L}{2}\|y-x\|^2.
\]

This is an upper bound on the value at $y$, built from the value and gradient at $x$ plus a quadratic term. The inner product is the linear contribution from the displacement $y-x$; the final term is quadratic in the Euclidean distance. The inequality points upward: the expression on the right bounds $f(y)$ from above.

To connect it to one gradient-descent step, set $y=x-\alpha\nabla f(x)$. Direct substitution gives

\[
f\bigl(x-\alpha\nabla f(x)\bigr)
\le f(x)-\alpha\left(1-\frac{L\alpha}{2}\right)\|\nabla f(x)\|^2.
\]

Thus the mechanism behind a safe decrease is conditional on $L$-smoothness and on the coefficient determined by the positive step. The substitution uses exactly the current gradient and the subtraction sign from the update. It is not a universal statement about an arbitrary engineering objective or arbitrary step size.

<!-- section: SEC-07 -->
## Choosing a constant step

A constant-step implementation sets $\alpha_k=\alpha$ at every iteration. When $L$ is known, a common choice is

\[
\alpha=\frac{1}{L}.
\]

Under the usual smooth-convex assumptions, another stated range is $\alpha\in(0,2/L)$. The qualification belongs with the interval: it is not a rule that applies regardless of the objective's properties. The endpoints are not included in the displayed open interval. A constant step makes an iteration table easy to compare because the multiplier does not change, but its mathematical support still comes from the assumptions attached to the chosen result. In particular, knowing only that $\alpha$ is positive is enough to define an update, not enough to import a convergence guarantee.

<!-- section: SEC-08 -->
## Armijo backtracking

When using Armijo backtracking, choose an initial trial step $\bar\alpha>0$, a contraction factor $\eta\in(0,1)$, and $c\in(0,1)$. Beginning with $m=0$, form

\[
\alpha_k=\eta^m\bar\alpha
\]

and take the smallest nonnegative integer $m$ for which

\[
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)
\le f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
\]

The test compares the objective at the trial update with a sufficient-decrease threshold. If it fails, multiplying by $\eta$ contracts the trial step and the test is repeated. Because $0<\eta<1$, successive candidates are scaled versions of the positive initial trial step. Starting at $m=0$ and checking consecutive integers enforces the smallest-index rule. The squared gradient norm and the direction of the inequality are part of the acceptance condition.

A transparent trace can list the candidate index, its trial step, the trial objective value, and the right-hand threshold. Each rejected row leads to the next integer and a contracted candidate. The first row satisfying the less-than-or-equal comparison supplies the step for the gradient-descent update; later, smaller candidates are not examined for this smallest-index rule.

```python
import numpy as np

A = np.diag([4.0, 1.0])
target = np.array([1.0, -0.5])

def objective(x):
    offset = x - target
    return 0.5 * offset @ A @ offset

def gradient(x):
    return A @ (x - target)

x_k = np.array([-1.0, 1.5])
bar_alpha = 1.0
eta = 0.5
c = 1.0e-4
g_k = gradient(x_k)
m = 0

while True:
    alpha_k = (eta ** m) * bar_alpha
    trial_value = objective(x_k - alpha_k * g_k)
    threshold = objective(x_k) - c * alpha_k * (np.linalg.norm(g_k) ** 2)
    if trial_value <= threshold:
        break
    m += 1

print(f"smallest accepted m = {m}")
print(f"accepted alpha_k = {alpha_k:.6f}")
print(f"trial value = {trial_value:.6f}")
print(f"Armijo threshold = {threshold:.6f}")
```

Because the test starts at zero and increments $m$ one at a time, the printed accepted index is the first accepted index for this trace. The block reports both sides of the test so acceptance can be checked directly.

<!-- section: SEC-09 -->
## Inner products and convex sets

For real vectors $u$ and $v$ of the same dimension, the inner product $u^Tv$ is the scalar sum of their componentwise products. To read $g^T(y-x)$, first form the displacement $d=y-x$, then compute the scalar $g^Td$. Its sign describes the alignment of $g$ and that displacement, but this arithmetic alone establishes no convexity conclusion. In particular, an inner product turns two same-length vectors into one number; it is not another displacement vector.

For $x,y$ and $\theta\in[0,1]$, the vector

\[
\theta x+(1-\theta)y
\]

is a convex combination. The coefficients are nonnegative and sum to one. A set is convex if it contains this combination for every pair of points in the set and every such $\theta$. For example, with $x=(0,0)^T$, $y=(2,4)^T$, and $\theta=1/4$, the combination is $(3/2,3)^T$. If $g=(1,-1)^T$, then $g^T(y-x)=-2$. These calculations illustrate the objects; they do not by themselves prove a function convex or a point globally optimal. They prepare the notation needed to read the next global inequality without importing an optimization theorem into this bridge.

<!-- section: SEC-10 -->
## Convexity as a global lower bound

A differentiable function $f:\mathbb{R}^d\to\mathbb{R}$ is convex when, for every $x,y\in\mathbb{R}^d$,

\[
f(y)\ge f(x)+\langle\nabla f(x),y-x\rangle.
\]

The value and gradient at $x$ define a first-order expression that lies below the function value at every $y$. The inner product pairs the current gradient with the displacement from $x$ to $y$, producing the scalar linear term. Both the lower-bound direction and the requirement that it hold for every pair are essential.

This is a global condition, not a property that follows from calling an objective an energy or calibration mismatch. When a convergence statement below assumes convexity, this full lower-bound property is what must be available.

<!-- section: SEC-11 -->
## Strong convexity strengthens the bound

For $\mu>0$, a differentiable function is $\mu$-strongly convex when, for all $x,y\in\mathbb{R}^d$,

\[
f(y)\ge f(x)+\langle\nabla f(x),y-x\rangle
+\frac{\mu}{2}\|y-x\|^2.
\]

Compared with convexity, the lower bound contains the additional positive quadratic term. Because $\mu$ is positive and the norm is squared, this term is nonnegative. Both its sign and coefficient $\mu/2$ matter, as does the requirement that the inequality hold for all pairs. Strong convexity is therefore an additional mathematical assumption, not a synonym for convexity and not an automatic feature of an engineering model. No second-order characterization is needed for the statements used here.

<!-- section: SEC-12 -->
## A bridge from ratios to conditioning

For positive constants satisfying $0<\mu\le L$, define the condition ratio

\[
\kappa=\frac{L}{\mu}.
\]

Dividing $0<\mu\le L$ by the positive number $\mu$ gives $\kappa\ge1$. The ratio records multiplicative separation: a value near one means $L$ and $\mu$ are close, while a larger value means they are farther apart multiplicatively. If $L=12$ and $\mu=3$, then $\kappa=4$, so $L$ is four times $\mu$; if $L=\mu$, then $\kappa=1$.

The order of the ratio matters: it is $L/\mu$, not $\mu/L$. The requirement $\mu>0$ is also essential, so $L/\mu$ must not be treated as a finite ratio when $\mu=0$. This is the specific ratio used here, not a matrix or spectral condition number, and this bridge makes no step-size or convergence claim.

<!-- section: SEC-13 -->
## The condition number in convergence histories

When the same objective is both $L$-smooth and $\mu$-strongly convex, its condition number is

\[
\kappa=\frac{L}{\mu}\ge1.
\]

This definition joins the upper control on gradient variation with the positive parameter in the strong-convexity bound. In a convergence history, $\kappa$ provides a compact way to read the contraction factors stated later: first compute the ratio from the two constants, then substitute it without changing its orientation. It should be interpreted only under the simultaneous smoothness and strong-convexity assumptions, and the ratio must not be inverted. A history alone does not establish that those assumptions hold.

<!-- section: SEC-14 -->
## The convex objective-gap guarantee

Now assume that $f$ is both $L$-smooth and convex, that $x^*$ is a global minimizer, and that gradient descent uses $\alpha_k=1/L$. Then, for every $k\ge1$,

\[
f(x_k)-f(x^*)
\le \frac{L\|x_0-x^*\|^2}{2k}.
\]

The left side is an objective gap, while the right side depends on the smoothness constant, the squared initial distance to a global minimizer, and the iteration index. As $k$ appears in the denominator, the displayed upper bound has the stated order $1/k$. This describes the guaranteed bound, not an assertion that every recorded objective value follows the bound with equality.

To read the result at a particular allowed iteration, keep the original point and global minimizer fixed, compute their Euclidean distance, square it, multiply by $L$, and divide by twice the iteration index. The resulting number is an upper bound on the objective gap under the hypotheses. It is not an update formula for producing the next parameter vector.

All hypotheses travel with the result: smoothness, convexity, a global minimizer, the step $1/L$, and $k\ge1$. The bound must not be transferred to a nonconvex objective, a different step rule, or a setting without the stated global minimizer.

<!-- section: SEC-15 -->
## Strong-convexity contractions and their limits

Finally, assume that $f$ is $L$-smooth and $\mu$-strongly convex, and let $\kappa=L/\mu$. Two guarantees must be paired with their own step sizes. With

\[
\alpha=\frac{2}{L+\mu},
\]

the squared distance satisfies

\[
\|x_k-x^*\|^2
\le
\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}
\|x_0-x^*\|^2.
\]

With the different choice $\alpha=1/L$, the objective gap satisfies

\[
f(x_k)-f(x^*)
\le
\left(1-\frac{\mu}{L}\right)^k
\bigl(f(x_0)-f(x^*)\bigr).
\]

These are geometric contractions: the relevant factor is raised to a power that grows with $k$. Notice that the first statement bounds squared distance and uses exponent $2k$, whereas the second bounds objective gap and uses exponent $k$. Exchanging the two step sizes would no longer reproduce the stated guarantees.

This separation also guides a convergence-history table. A squared-distance column corresponds to the first contraction and requires the step based on both constants. An objective-gap column corresponds to the second contraction and requires the step based on $L$. The quantities and their initial values differ, so the two right-hand sides should not be merged even though both decrease through repeated powers.

The formulas also make conditioning visible. Since $\mu/L=1/\kappa$, greater separation between $L$ and $\mu$ changes the stated objective contraction factor toward one; the distance factor likewise depends explicitly on $\kappa$. This interpretation belongs only to objectives satisfying both assumptions. It does not establish those properties for an objective merely because its data came from mechanics.

The complete chain is therefore conditional. Gradient descent supplies a traceable current-gradient update; smoothness supports a decrease mechanism and qualified step choices; convexity supports the stated global objective-gap bound; and strong convexity supports the two stronger contractions, each with its recorded step. An idealized engineering objective can make that chain concrete, but its context cannot substitute for checking the mathematical conditions.
