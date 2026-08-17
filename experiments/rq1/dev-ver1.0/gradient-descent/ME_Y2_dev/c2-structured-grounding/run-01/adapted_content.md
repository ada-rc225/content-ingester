# Gradient Descent and Optimisation for Mechanical Engineering

This lesson develops optimisation from a mechanical-engineering starting point: a system tends toward an equilibrium configuration, and a numerical relaxation method can search for a low value of a scalar measure. The central mathematical object is more general than potential energy. We will repeatedly use the engineering picture to build intuition, then return to the canonical optimisation statement and its assumptions.

<!-- section: SEC-01 -->
## From equilibrium to an optimisation problem

Imagine that a configuration is described by a vector $x\in\mathbb{R}^d$: coordinates, design parameters, or other variables. A potential-energy picture suggests that a stable equilibrium may be found by seeking a low value of a scalar function. In optimisation, that scalar function is the objective $f$; it need not be a physical energy, and $x$ need not describe a real-time state.

The unconstrained problem is

$$
\min_{x\in\mathbb{R}^d} f(x).
$$

More precisely, unconstrained optimisation minimises a continuously differentiable objective $f:\mathbb{R}^d\to\mathbb{R}$ over all of $\mathbb{R}^d$. “Unconstrained” means that no additional equations or inequalities restrict the search domain. If a displacement, angle, or parameter must obey a bound, that is a different problem setting and must not be silently folded into this one.

At an interior differentiable local minimiser $x^*$, every small directional change fails to reduce the objective. The first-order optimality condition is therefore

$$\nabla f(x^*)=0.$$

This is a necessary condition, not a complete test. A stationary point can be a maximum or a saddle. For a twice continuously differentiable objective, a local minimiser must have a positive-semidefinite Hessian together with stationarity. Conversely, positive-definite Hessian together with stationarity is sufficient for a strict local minimiser. The two statements have different logical directions: positive semidefiniteness is necessary, while positive definiteness gives sufficiency for a strict local minimum.

The analogy boundary matters here. Mechanical equilibrium can often be described by a vanishing force, and a force may be related to a negative energy gradient. But an optimisation iteration is not automatically a physical relaxation trajectory, and an arbitrary engineering objective may have no potential-energy interpretation. The safe transfer is the question “which change decreases the objective?” followed by the canonical formulation above.

A useful diagnostic follows immediately: if a computed point has a small gradient, it may be near a stationary point, but that alone does not certify a minimum. Inspect curvature or use additional problem assumptions.

<!-- section: SEC-02 -->
## Geometry: smoothness, convexity, and conditioning

The behaviour of a numerical relaxation depends on the geometry of $f$. First, $L$-smoothness means that the gradient is $L$-Lipschitz in the Euclidean norm:

$$
\|\nabla f(x)-\nabla f(y)\|\le L\|x-y\|,\qquad\forall x,y\in\mathbb{R}^d.
$$

Here $L$ is positive and the inequality must hold for every pair of points. This is not the same as saying that function values are Lipschitz. Smoothness limits how rapidly the slope changes. It gives the Descent Lemma, a quadratic upper bound:

$$
f(y)\le f(x)+\langle\nabla f(x),y-x\rangle+\frac{L}{2}\|y-x\|^2,
\qquad\forall x,y\in\mathbb{R}^d.
$$

The linear term predicts the local change and the quadratic term protects against curvature. This is why a step-size rule can be tied to $L$.

Differentiable convexity is described by a global first-order lower bound:

$$
f(y)\ge f(x)+\langle\nabla f(x),y-x\rangle,
\qquad\forall x,y\in\mathbb{R}^d.
$$

Every tangent plane lies below the graph. In the energy picture, there are no misleading separated bowls: a local minimum is also a global minimum when the relevant convex assumptions hold. The definition itself, however, is the inequality above, not the picture.

$\mu$-strong convexity strengthens that lower bound by a positive quadratic term:

$$
f(y)\ge f(x)+\langle\nabla f(x),y-x\rangle+\frac{\mu}{2}\|y-x\|^2,
\qquad\forall x,y\in\mathbb{R}^d,
$$

where $\mu$ is positive. Strong convexity expresses a uniform amount of curvature. It is stronger than convexity; the quadratic term cannot be omitted or given the opposite sign.

For a $C^2$ objective, the Hessian gives a local curvature test. Under convexity, smoothness and convexity are characterised by

$$0\preceq\nabla^2 f(x)\preceq LI,\qquad\forall x,$$

and strong convexity is characterised by

$$\nabla^2 f(x)\succeq \mu I,\qquad\forall x.$$

The convexity qualifier is important for the two-sided bound: the positive-semidefinite lower bound cannot be dropped when interpreting it as the smooth-convex characterisation. When an objective is both $L$-smooth and $\mu$-strongly convex, its condition number is

$$\kappa=\frac{L}{\mu}\ge 1.$$

A large condition number indicates a wide range of curvature scales. In engineering language, one direction may be stiff while another is compliant. This is a useful intuition for slow zig-zagging, but it is not itself a new convergence theorem. The formal quantities controlling the later results are $L$, $\mu$, convexity, and the stated minimiser assumptions.

<!-- section: SEC-03 -->
## Gradient descent and choosing a step

Gradient descent uses the gradient at the current iterate and moves in the opposite direction:

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),\qquad k=0,1,2,\ldots,$$

with $x_0\in\mathbb{R}^d$ and positive $\alpha_k$. The negative gradient is the local descent direction because the directional derivative in direction $-\nabla f(x_k)$ is negative when the gradient is nonzero. This is a numerical update, not a claim about the system’s physical time evolution.

A constant step sets $\alpha_k=\alpha$. Common choices include $\alpha=1/L$ and, under the usual smooth-convex assumptions, $\alpha\in(0,2/L)$. The interval must not be quoted without its assumptions, and the value $L$ must be known for these listed choices. A step that is too large can overshoot a curved valley; a step that is too small may make progress unnecessarily slow.

Two alternatives adapt the step. Exact line search chooses the positive step that minimises the objective along the current negative-gradient ray:

$$\alpha_k=\arg\min_{\alpha>0}f\bigl(x_k-\alpha\nabla f(x_k)\bigr).$$

This is exact minimisation along that one-dimensional line, not merely an acceptance test. Armijo backtracking instead starts from a positive trial $\bar\alpha$ and contracts it, for example by a factor $\eta\in(0,1)$, until the sufficient-decrease inequality is satisfied:

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)
\le f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2,$$

where $c\in(0,1)$ and the accepted integer $m$ is the smallest nonnegative one producing the accepted contracted trial. The squared gradient norm is part of the test. The engineering interpretation is controlled relaxation: do not accept a proposed displacement unless the measured objective decrease is sufficient.

The Descent Lemma explains the logic. Substitute $y=x-\alpha\nabla f(x)$ into its quadratic upper bound. The linear term is negative and the quadratic term is positive. A step-size rule balances them. In code, a useful first implementation should record objective values and gradient norms, stop only according to a clearly stated criterion, and avoid treating a small step as evidence of physical equilibrium.

<!-- section: SEC-04 -->
## What convergence guarantees actually say

A convergence rate is a conditional statement. It is not a promise that every objective or every implementation reaches a desired answer. For an $L$-smooth convex $f$ with a global minimiser $x^*$, using gradient descent with $\alpha_k=1/L$ gives, for $k\ge1$,

$$
f(x_k)-f(x^*)\le\frac{L\|x_0-x^*\|^2}{2k}.$$

The objective gap has an $O(1/k)$ form. Every hypothesis matters: smoothness, convexity, existence of the global minimiser, and the particular step $1/L$. The bound is about objective values, not automatically distance between iterates.

With stronger geometry, the statement changes. If $f$ is $L$-smooth and $\mu$-strongly convex, gradient descent has the following two results, each tied to its own step size. At

$$\alpha=\frac{2}{L+\mu},$$

it satisfies the distance contraction

$$
\|x_k-x^*\|^2\le
\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}\|x_0-x^*\|^2.
$$

At the step $\alpha=1/L$, it satisfies the objective contraction

$$
f(x_k)-f(x^*)\le
\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).
$$

Do not attach the distance rate to $1/L$ or the objective rate to $2/(L+\mu); the statements are deliberately paired with different steps. Strong convexity also supplies a unique, well-shaped target in the mathematical model, while a real mechanical system may have symmetries, constraints, or nonconvex behaviour outside this lesson’s setting.

For practice, when reading a convergence claim ask four questions: What is assumed about curvature? Is the minimiser global? What quantity is bounded? Which update and step are being used? This habit is more valuable than memorising a rate without its scope.

For a numerical result, also distinguish an objective gap from a residual. A small gradient measures stationarity, while a small objective value depends on how the objective has been defined and shifted. A sequence of iterates can move very little because of a small step, because the gradient is small, or because the method is oscillating around a region; these explanations are not interchangeable. Reporting the iterate, objective, and gradient norm together makes the computational evidence easier to audit.

<!-- section: SEC-05 -->
## Momentum and acceleration

Momentum methods use recent motion as well as the current gradient. The Heavy Ball rule is

$$x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1}),$$

where $\beta\in[0,1)$ and the parameters must keep the iteration stable. The difference of the two most recent iterates is a memory term. It may help a method move through a long shallow direction, but it can also amplify oscillation. The gradient is still evaluated at $x_k$; Heavy Ball must not be confused with a look-ahead method.

A precise accelerated result has a narrow scope. For

$$f(x)=\frac12x^TAx,$$

where $A$ is symmetric positive definite with spectrum in $[\mu,L]$, the stated Heavy Ball parameters are

$$\alpha^*=\frac{4}{(\sqrt L+\sqrt\mu)^2},\qquad
\beta^*=\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^2.$$

The improved condition-number dependence belongs specifically to this quadratic setting. It must not be generalised to arbitrary nonlinear objectives.

The approved NAG variant has different semantics. Initialise $y_0=x_0$ and $\lambda_0=1$. Starting at $k=0$, compute

$$x_{k+1}=y_k-\frac1L\nabla f(y_k),$$

then update

$$\lambda_{k+1}=\frac{1+\sqrt{1+4\lambda_k^2}}2,$$

and

$$y_{k+1}=x_{k+1}+\frac{\lambda_k-1}{\lambda_{k+1}}(x_{k+1}-x_k).$$

The gradient is evaluated at $y_k$, not $x_k$, and the indices are part of the algorithm. For an $L$-smooth convex objective with a global minimiser, this exact parameterisation gives

$$f(x_k)-f(x^*)\le\frac{2L\|x_0-x^*\|^2}{(k+1)^2}=O\left(\frac1{k^2}\right).$$

That rate is not a licence to use a different recurrence or to omit convexity. In an engineering workflow, momentum should be monitored rather than assumed beneficial: inspect objective values and detect oscillation or instability.

<!-- section: SEC-06 -->
## Stochastic and adaptive gradient methods

When an objective averages many contributions, write

$$f(x)=\frac1N\sum_{i=1}^N f_i(x).$$

A stochastic method uses an estimate $g_k(x_k)$. The approved model assumes conditional unbiasedness and bounded conditional variance:

$$\mathbb E[g_k(x_k)\mid x_k]=\nabla f(x_k),$$

$$\mathbb E\left[\|g_k(x_k)-\nabla f(x_k)\|^2\mid x_k\right]\le\sigma^2.$$

The conditioning is on the current iterate, and the variance bound is $\sigma^2$. In mechanical simulation or parameter fitting, this can represent evaluating a randomly selected contribution rather than the entire average. That is a pedagogical framing, not a claim that every engineering data set satisfies the model.

SGD uses

$$x_{k+1}=x_k-\eta_k g_k(x_k).$$

With persistent nonzero variance and a small constant step, the usual behaviour is generally a nonzero error floor rather than exact convergence. Diminishing steps can reduce the effect of noise, but the Robbins–Monro series conditions

$$\sum_{k=1}^{\infty}\eta_k=\infty,\qquad
\sum_{k=1}^{\infty}\eta_k^2<\infty$$

are not sufficient alone. A theorem must also state appropriate objective, bias, moment, and iterate-stability assumptions. Therefore, a noisy plateau is not automatically a coding failure, and a decreasing step is not automatically a convergence proof.

Three coordinate-scaling rules are useful to recognise. AdaGrad starts with $v_{-1}=0$, accumulates element-wise squared gradients, and updates

$$v_k=v_{k-1}+g_k\odot g_k,\qquad
x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k,$$

where gradients start at $k=0$ and $\epsilon>0$. RMSProp also starts with $v_{-1}=0$, but uses an exponential moving average:

$$v_k=\gamma v_{k-1}+(1-\gamma)g_k\odot g_k,$$

$$x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k,$$

with $\gamma\in[0,1)$ and $\epsilon>0$. The factor $(1-\gamma)$ and the distinction from cumulative AdaGrad accumulation are essential.

Adam keeps two exponential moments, both initialised at index $-1$:

$$m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,$$

$$v_k=\beta_2v_{k-1}+(1-\beta_2)(g_k\odot g_k).$$

For $k$ starting at zero, correct the initial bias using

$$\hat m_k=\frac{m_k}{1-\beta_1^{k+1}},\qquad
\hat v_k=\frac{v_k}{1-\beta_2^{k+1}},$$

and update

$$x_{k+1}=x_k-\frac{\eta}{\sqrt{\hat v_k}+\epsilon}\odot\hat m_k.$$

Here $\beta_1,\beta_2\in[0,1)$ and $\epsilon>0$. These rules change scaling semantics; they do not erase the need to examine objective behaviour and assumptions.

<!-- section: SEC-07 -->
## Second-order optimisation: Newton's method

Gradient descent uses slope information. Newton’s method additionally uses curvature. Around $x_k$, the second-order Taylor model is

$$f(x_k+p)\approx f(x_k)+\nabla f(x_k)^Tp+\frac12p^T\nabla^2f(x_k)p.$$

This is an approximation in the step $p$, not an exact identity for a general objective. Minimising the model with respect to $p$ leads to the Newton linear system

$$\nabla^2f(x_k)p_k=-\nabla f(x_k),\qquad x_{k+1}=x_k+p_k.$$

The equivalent inverse expression is

$$x_{k+1}=x_k-[\nabla^2f(x_k)]^{-1}\nabla f(x_k),$$

but it requires an invertible Hessian. Numerically, solve the linear system; do not explicitly form the inverse. For large engineering models, forming and factoring a Hessian may be expensive, so this is an introduction rather than a recommendation for every problem.

Newton’s attractive local result is also conditional. If $\nabla f(x^*)=0$, the Hessian at $x^*$ is positive definite, the Hessian is locally Lipschitz, and $x_0$ is sufficiently close to $x^*$, then the iterates converge locally quadratically:

$$\|x_{k+1}-x^*\|\le C\|x_k-x^*\|^2.$$

“Locally” and “sufficiently close” cannot be removed. Newton’s method can behave differently away from the target, especially when curvature is indefinite or nearly singular. A line search or damping strategy may be needed in practice, but any such method has to be specified rather than assumed.

The mechanical analogy is especially limited here. Curvature of an energy surface can motivate the Hessian, but a Newton step is a model-based computational correction, not a physical impulse. Return to the linear solve and its conditions when deciding whether it is appropriate.

<!-- section: SEC-08 -->
## BFGS and an engineering workflow

BFGS approximates curvature without requiring the exact Hessian at every iteration. Define the step and gradient-difference vectors by

$$s_k=x_{k+1}-x_k,\qquad y_k=\nabla f(x_{k+1})-\nabla f(x_k).$$

The next Hessian approximation satisfies the secant equation

$$B_{k+1}s_k=y_k.$$

The step vector and gradient-difference vector have different roles; they must not be interchanged. In inverse-Hessian form, for positive curvature $y_k^Ts_k$, use

$$H_{k+1}=(I-\rho_ks_ky_k^T)H_k(I-\rho_ky_ks_k^T)+\rho_ks_ks_k^T,$$

where

$$\rho_k=\frac1{y_k^Ts_k}.$$

The search direction is $p_k=-H_k\nabla f(x_k)$, and a suitable line search supports the curvature condition. Thus BFGS is not merely “gradient descent with a matrix”: curvature, transpose placement, the negative direction, and line-search behaviour are all part of the algorithm.

The following minimal example implements a deterministic quadratic relaxation. It uses lists so that it runs in a basic Python interpreter. The matrix is diagonal, making the gradient explicit. The code reports objective values for standard gradient descent and Heavy Ball; it does not assert a physical-time interpretation or a universal ranking.

```python

def objective(x):
    # A symmetric positive-definite quadratic: f(x) = 1/2 x^T A x.
    return 0.5 * (x[0] * x[0] + 4.0 * x[1] * x[1])


def gradient(x):
    return [x[0], 4.0 * x[1]]


def gradient_descent(x0, alpha, steps):
    x = list(x0)
    values = []
    for _ in range(steps):
        values.append(objective(x))
        g = gradient(x)
        x = [x[i] - alpha * g[i] for i in range(2)]
    values.append(objective(x))
    return x, values


def heavy_ball(x0, alpha, beta, steps):
    x_previous = list(x0)
    x = list(x0)
    values = []
    for _ in range(steps):
        values.append(objective(x))
        g = gradient(x)
        x_next = [
            x[i] - alpha * g[i] + beta * (x[i] - x_previous[i])
            for i in range(2)
        ]
        x_previous, x = x, x_next
    values.append(objective(x))
    return x, values


x_gd, gd_values = gradient_descent([3.0, 2.0], alpha=0.2, steps=20)
x_hb, hb_values = heavy_ball([3.0, 2.0], alpha=0.1, beta=0.4, steps=20)
print("GD final objective:", gd_values[-1])
print("Heavy Ball final objective:", hb_values[-1])
```

To use this responsibly, first identify the objective, variables, and gradient; then state the geometry and the step rule. Check that the code evaluates the gradient at the intended point, preserves the sign, and records a meaningful quantity. Finally, compare observed behaviour with the exact theorem scope: a quadratic result is not a general nonlinear guarantee, and a numerical trace is evidence about this run, not a proof of convergence.

A compact method-selection checklist is: use standard gradient descent when a reliable gradient and manageable step are available; consider line search when scale is uncertain; use momentum or the specified acceleration only with their exact recurrences and assumptions; use SGD when full gradients are costly, while planning for noise; and consider Newton or BFGS when curvature information can justify the extra computation. In every case, return to the unconstrained mathematical problem and make the assumptions visible.
