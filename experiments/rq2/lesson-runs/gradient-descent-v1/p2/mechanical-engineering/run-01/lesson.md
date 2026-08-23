# Gradient Descent for Energy and Parameter Calibration

Gradient descent is a first-order method for improving a model by repeatedly moving in the direction that most rapidly decreases a differentiable objective. In this lesson, the objective may represent an idealized energy mismatch or a parameter-calibration error. Those are useful engineering frames, not universal claims: an actual engineering objective may be nonconvex, constrained, noisy, or better suited to another method. We will keep every guarantee tied to its mathematical assumptions.

<!-- section: SEC-01 -->
## 1. The optimisation problem

Suppose a vector $x\in\mathbb{R}^d$ stores adjustable parameters, such as idealized coefficients in a calibration model. The unconstrained problem is

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where $f:\mathbb{R}^d\to\mathbb{R}$ is assumed to be continuously differentiable, at least $f\in C^1$. “Unconstrained” means that this mathematical formulation places no bounds, equality constraints, or inequality constraints on $x$. If a physical parameter must remain positive, that is a different problem setting and cannot be silently inserted into this formulation.

A small value of $f$ can be interpreted as a good fit or low idealized energy, depending on how the objective was constructed. The optimisation method only sees function values and gradients; it does not by itself establish that the objective captures every physical effect or that its minimizer is the best design.

<!-- section: SEC-02 -->
## 2. What stationarity tells us

If $x^*$ is a local minimizer and $f$ is differentiable at $x^*$, then the necessary first-order condition is

$$
\nabla f(x^*)=0.
$$

The gradient is therefore a useful stopping signal: a candidate point with a small gradient may be close to first-order stationarity. However, stationarity is not sufficient for a minimum in general. A stationary point can be a local maximum or a saddle point, and even a local minimum need not be globally best. A calibration workflow must therefore distinguish “the gradient vanishes” from “the model has reached the desired optimum.”

For an engineering interpretation, imagine changing two calibration parameters together. At a stationary point, the first-order change predicted by the gradient is zero in every direction. That is a local statement. It does not remove the need to inspect the objective, assumptions, and relevant physical context.

<!-- section: SEC-03 -->
## 3. The gradient-descent update

Starting from $x_0\in\mathbb{R}^d$ and choosing positive step sizes $\alpha_k$, standard gradient descent uses the current iterate:

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),\qquad k=0,1,2,\ldots.
$$

The minus sign matters. The gradient points toward local increase, so its negative is the first-order decrease direction. The gradient is evaluated at $x_k$, not at a future or look-ahead point. A larger $\alpha_k$ takes a longer move; a smaller one takes a shorter move.

For a trace, suppose a scalar parameter has $f(q)=\tfrac12(q-3)^2$, so $\nabla f(q)=q-3$. With $q_0=0$ and $\alpha=0.5$, the first update is $q_1=0-0.5(-3)=1.5$, and the second is $q_2=1.5-0.5(-1.5)=2.25$. The objective decreases here because the step is appropriate for this simple example, not because every positive step guarantees decrease.

```python
import numpy as np

q = 0.0
alpha = 0.5
for k in range(4):
    value = 0.5 * (q - 3.0) ** 2
    gradient = q - 3.0
    print(k, round(q, 4), round(value, 4), round(gradient, 4))
    q = q - alpha * gradient
```

<!-- section: SEC-04 -->
## 4. Bridge: measuring vector size and gradient change

For a vector $z\in\mathbb{R}^d$, the Euclidean norm is

$$
\|z\|_2=\sqrt{z^Tz},
$$

and $\|x-y\|_2$ measures the Euclidean distance between two parameter vectors. For a vector-valued map $G$, an $L$-Lipschitz bound has the form

$$
\|G(x)-G(y)\|_2\le L\|x-y\|_2
$$

for every pair of inputs in the domain. It says that output-vector change is bounded relative to input-vector change. When $G$ is a gradient map, this compares changes in gradient vectors. It is not a statement that function values satisfy $|f(x)-f(y)|\le L\|x-y\|$.

For example, if $G(x)=2x$, then $G(x)-G(y)=2(x-y)$ and $\|G(x)-G(y)\|_2=2\|x-y\|_2$. Thus $L=2$ works. In a two-parameter calibration setting, the norm treats the two coordinate changes together rather than judging only one component.

<!-- section: SEC-05 -->
## 5. Smoothness as a controlled-gradient assumption

A continuously differentiable function $f:\mathbb{R}^d\to\mathbb{R}$ is $L$-smooth, with $L>0$, when its gradient is Lipschitz with respect to the Euclidean norm:

$$
\|\nabla f(x)-\nabla f(y)\|\le L\|x-y\|,\qquad\forall x,y\in\mathbb{R}^d.
$$

This assumption says that the gradient cannot change arbitrarily fast relative to the distance between parameter vectors. The constant $L$ is a bound, not necessarily the exact observed change for every pair. In an engineering model, using this assumption requires justification or estimation; the context alone does not make an objective smooth.

The distinction between gradient smoothness and function-value Lipschitzness is important. The left side contains a difference of gradients, so the assumption controls how the slope field changes. This is the assumption that supports the next upper-bound result.

<!-- section: SEC-06 -->
## 6. Why a smooth objective can decrease

If $f$ is $L$-smooth, the Descent Lemma gives, for all $x,y\in\mathbb{R}^d$,

$$
f(y)\le f(x)+\langle\nabla f(x),y-x\rangle+\frac{L}{2}\|y-x\|^2.
$$

This is a quadratic upper bound. Substitute the gradient-descent trial point $y=x-\alpha\nabla f(x)$. The linear term then points downward, while the quadratic term penalises a long step. The result explains why step size is a balance: a step that is too large can allow the quadratic term to dominate, whereas a suitably controlled step can produce a decrease.

The inequality is conditional on $L$-smoothness, holds with the upper-bound direction shown, and contains the coefficient $L/2$. It is not a claim that every engineering objective has this property. It is also not a complete convergence theorem by itself; convergence needs additional assumptions and a specified step rule.

<!-- section: SEC-07 -->
## 7. Constant step sizes

A constant-step implementation sets $\alpha_k=\alpha$. When $L$ is known, a common choice is

$$
\alpha=\frac1L.
$$

Under the usual smooth-convex assumptions, the source also records the interval $\alpha\in(0,2/L)$. The qualification belongs to the interval: it must not be quoted as a universal safe range for arbitrary objectives. In practice, an estimate of $L$ can be uncertain, so an iteration history should be inspected rather than assuming that a numerical result is guaranteed.

For an idealized quadratic calibration objective, compare two runs with different constant steps. Record the iterate, objective, gradient norm, and step. A decreasing objective and shrinking gradient are informative diagnostics, but they do not replace the hypotheses of a theorem. If a run oscillates or increases, reduce the step or use a bounded acceptance procedure.

<!-- section: SEC-08 -->
## 8. Armijo backtracking

Armijo backtracking provides a practical alternative when a useful constant step is not known. Choose an initial trial step $\bar\alpha>0$, a contraction factor $\eta\in(0,1)$, and $c\in(0,1)$. At iteration $k$, test steps of the form $\alpha_k=\eta^m\bar\alpha$ and choose the smallest integer $m\ge0$ for which

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)\le f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
$$

The right side specifies sufficient decrease. The procedure contracts the positive trial step until the displayed inequality is accepted; it does not reverse the inequality or omit the squared gradient norm. This is a step-selection rule, not permission to claim that every resulting run has a particular convergence rate without the corresponding assumptions.

```python
import numpy as np

def f(x):
    return 0.5 * (x[0] - 2.0) ** 2 + 2.0 * (x[1] + 1.0) ** 2

def grad_f(x):
    return np.array([x[0] - 2.0, 4.0 * (x[1] + 1.0)])

x = np.array([5.0, 3.0])
eta, c, trial = 0.5, 1e-4, 1.0
for k in range(5):
    g = grad_f(x)
    m, alpha = 0, trial
    while f(x - alpha * g) > f(x) - c * alpha * np.dot(g, g):
        m += 1
        alpha = eta ** m * trial
    print(k, round(f(x), 6), round(alpha, 6))
    x = x - alpha * g
```

<!-- section: SEC-09 -->
## 9. Bridge: inner products and convex combinations

For real vectors $u$ and $v$ of the same dimension, $u^Tv$ is the scalar sum of componentwise products. If $d=y-x$, then $g^T(y-x)=g^Td$ is the inner product of a gradient-like vector and a displacement. Its sign describes their alignment, but this arithmetic alone proves no convexity or optimality result.

For $\theta\in[0,1]$, the point $\theta x+(1-\theta)y$ is a convex combination. A set is convex when it contains that combination for every pair of its points and every such $\theta$. For $x=(0,0)^T$, $y=(2,4)^T$, and $\theta=1/4$, the combination is $(3/2,3)^T$. If $g=(1,-1)^T$, then $g^T(y-x)=-2$. These calculations prepare the notation used in first-order convexity, but they are not that theorem.

<!-- section: SEC-10 -->
## 10. Differentiable convexity

A differentiable function is convex when, for all $x,y\in\mathbb{R}^d$,

$$
f(y)\ge f(x)+\langle\nabla f(x),y-x\rangle.
$$

The tangent expression on the right is a global first-order lower bound. Notice the direction: the function value at $y$ is above the linear approximation formed at $x$. Convexity is a mathematical property to be checked or assumed; an energy or calibration interpretation does not establish it automatically. Some idealized engineering objectives may be convex, while other realistic objectives may not be.

This lower-bound viewpoint clarifies why convexity improves the interpretation of a stationary point. Under appropriate convex assumptions, first-order information can support global conclusions. Without those assumptions, the stationarity condition from earlier remains only necessary at a differentiable local minimizer.

<!-- section: SEC-11 -->
## 11. Strong convexity

A differentiable function is $\mu$-strongly convex for $\mu>0$ when, for all $x,y\in\mathbb{R}^d$,

$$
f(y)\ge f(x)+\langle\nabla f(x),y-x\rangle+\frac{\mu}{2}\|y-x\|^2.
$$

This strengthens the convex lower bound by adding a positive quadratic term. The coefficient is exactly $\mu/2$, and the inequality remains a global statement over all pairs. Strong convexity describes curvature in the objective-level assumptions used by the convergence result; it does not say that every physical design problem has that curvature.

Keep the roles separate: smoothness controls how rapidly gradients vary from above, while strong convexity supplies a quadratic lower bound. Their combination is stronger than either statement alone and will let us describe rates. A theorem using them cannot be extended to an objective that has not been shown or assumed to satisfy them.

<!-- section: SEC-12 -->
## 12. Bridge: ratios and conditioning

For positive constants $0<\mu\le L$, define the condition ratio

$$
\kappa=\frac{L}{\mu}\ge1.
$$

Because $\mu>0$, division preserves the inequality and gives the lower bound. If $L=12$ and $\mu=3$, then $\kappa=4$: the two constants are separated by a factor of four. If $L=\mu$, then $\kappa=1$. A larger ratio means greater multiplicative separation between these two constants. This lesson uses only this ratio; it is not introducing matrix or spectral condition numbers.

The positive lower constant is essential. When $\mu=0$, $L/\mu$ is not a finite condition ratio. In convergence histories, a large $\kappa$ can be used to anticipate a more difficult scale separation under the specific strong-convexity and smoothness theory, but it is not a universal diagnostic for every engineering objective.

<!-- section: SEC-13 -->
## 13. Reading convergence histories

For an $L$-smooth and $\mu$-strongly convex objective, the condition number is $\kappa=L/\mu$. Two objectives can have similarly scaled starting errors but different ratios, so their histories can contract at different rates under the theorem below. Use an iteration table to make this visible: list $k$, $f(x_k)$, $\|\nabla f(x_k)\|$, and, when a reference minimizer is available, the distance to it.

Do not infer the ratio from a noisy or nonconvex history alone. The ratio is defined here under both smoothness and strong convexity, and a history is evidence about a particular run rather than proof of the assumptions. In an engineering calibration study, report the modelling assumptions and the chosen step alongside the plot or table.

<!-- section: SEC-14 -->
## 14. The convex objective-gap guarantee

Let $f:\mathbb{R}^d\to\mathbb{R}$ be $L$-smooth and convex, let $x^*$ be a global minimizer, and use $\alpha_k=1/L$. Then, for $k\ge1$,

$$
f(x_k)-f(x^*)\le\frac{L\|x_0-x^*\|^2}{2k}.
$$

The objective gap is therefore bounded by a quantity proportional to $1/k$ under exactly these hypotheses. The result requires an $L$-smooth convex objective, existence of a global minimizer, and the constant step $1/L$. It does not assert that an arbitrary engineering objective is convex, that a minimizer exists, or that a different step inherits this bound. The notation $O(1/k)$ describes the rate pattern; it is not a promise about an unverified application.

As a check, if the hypotheses are accepted and $k$ is doubled, the displayed upper bound is halved, while the other factors remain the same. That is a statement about the bound, not necessarily an exact observation in every finite run.

<!-- section: SEC-15 -->
## 15. Strongly convex contractions and responsible use

If $f$ is both $L$-smooth and $\mu$-strongly convex, the following two bounds use different step sizes. With

$$
\alpha=\frac{2}{L+\mu},
$$

and $\kappa=L/\mu$, the squared-distance contraction is

$$
\|x_k-x^*\|^2\le\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}\|x_0-x^*\|^2.
$$

With $\alpha=1/L$, the objective-gap contraction is

$$
f(x_k)-f(x^*)\le\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).
$$

The first rate belongs to $2/(L+\mu)$ and the second to $1/L$; they must not be swapped. Both require smoothness and strong convexity. These are useful theoretical benchmarks for an idealized model, not evidence that gradient descent is universally appropriate for engineering design. A responsible workflow states assumptions, records the selected rule, checks objective and gradient histories, and treats constraints or nonconvex effects as reasons to reassess the method.

### Final worked exercise

Consider an idealized unconstrained calibration objective with an accepted smoothness estimate $L=12$ and strong-convexity estimate $\mu=3$. First compute $\kappa=12/3=4$. The distance-theory step is $2/(12+3)=2/15$, while the objective-gap theorem uses $1/L=1/12$. They are different choices because they support different displayed contractions. The convex $1/k$ bound also needs a global minimizer and convexity, and the linear objective-gap bound additionally needs strong convexity. Write those conditions beside any numerical prediction; do not attach a theorem to the engineering label alone.

```python
L = 12.0
mu = 3.0
kappa = L / mu
alpha_distance = 2.0 / (L + mu)
alpha_objective = 1.0 / L
print("kappa", kappa)
print("distance-step", alpha_distance)
print("objective-step", alpha_objective)
```

The central habit is to connect each update and each rate to its assumptions. Gradient descent is a transparent first-order procedure, but its guarantees are conditional mathematical statements rather than universal engineering conclusions.

### A practical reading checklist

Before running an iteration, write down what the coordinates of $x$ mean and what quantity $f(x)$ measures. Confirm that the intended mathematical problem is unconstrained, or explicitly record that a constrained formulation is needed instead. Compute or implement the gradient independently enough to notice a sign error. A gradient check can compare an analytic component with a small finite-difference estimate, but that check is a numerical diagnostic rather than a new convergence guarantee.

During the run, retain the step size used at every iteration. For a constant step, record the value of $L$ that motivated it and keep the smooth-convex qualification attached to any interval statement. For backtracking, retain the initial trial step, contraction factor, sufficient-decrease constant, and accepted contraction count. This makes an iteration reproducible and makes it possible to distinguish a change in the objective from a change in the step rule.

Scaling deserves the same attention. If one parameter is measured in millimetres and another in a much larger unit, Euclidean distances and gradient components can have different numerical scales. That observation does not alter any theorem, but it can affect the practical trace and the interpretation of a chosen step. Record the parameter units and any preprocessing, and do not describe improved numerical behaviour as a theorem unless the stated assumptions still apply.

When interpreting a table, look at more than one column. A decreasing function value with a large gradient may indicate that substantial work remains. A small gradient does not by itself certify a global minimum. If a reference solution is available, compare objective gaps or distances under the assumptions that justify those comparisons. If the history oscillates, stalls, or leaves a plausible modelling region, stop and examine the step, gradient, scaling, and objective construction rather than automatically increasing the iteration limit.

Finally, communicate the boundary of the result. State whether smoothness, convexity, a global minimizer, or strong convexity is assumed; identify which step size was used; and label a theorem-based upper bound as a bound rather than an observed equality. This discipline is especially important for idealized energy minimisation and parameter calibration, where the mathematical objective is a model of a physical task. Gradient descent can be a useful first-order tool without being the universally correct tool for every engineering design problem.
