# Gradient Descent and Optimisation for Mechanical Engineers

<!-- section: SEC-01 -->
## Equilibrium, stationarity, and curvature

### An objective as a design measure

Unconstrained optimisation asks us to minimise a continuously differentiable objective over all of $\mathbb{R}^d$:

$$
\min_{x\in\mathbb{R}^d} f(x).
$$

The vector $x$ can collect design variables, calibration parameters, or coefficients in a model. A potential-energy picture is useful for intuition: equilibrium points are places where a small displacement does not produce a first-order change. The boundary of that analogy is important: an optimisation objective need not be physical energy, and an algorithmic iterate is not automatically a system state evolving in physical time.

If $x^*$ is a differentiable local minimiser, then

$$
\nabla f(x^*)=0.
$$

This is a first-order necessary condition. It says that every feasible small direction has zero first-order slope in the unconstrained setting. It does not say that every stationary point is a minimum. A stationary point can be a maximum or a saddle, just as a force-balance calculation can identify an unstable equilibrium.

### What curvature can and cannot tell us

For a $C^2$ objective, stationarity together with a positive-semidefinite Hessian is necessary at a local minimum:

$$
\nabla f(x^*)=0,\qquad \nabla^2 f(x^*)\succeq 0.
$$

The same stationarity condition together with a positive-definite Hessian is sufficient for a strict local minimum:

$$
\nabla f(x^*)=0,\qquad \nabla^2 f(x^*)\succ 0.
$$

The distinction between semidefinite and definite matters. A zero eigenvalue can leave a flat direction, so a semidefinite Hessian does not by itself provide the strict-minimum conclusion. These are local statements; they do not establish that the point minimises the objective globally.

<!-- section: SEC-02 -->
## Smoothness, convexity, and conditioning

### Smoothness and a quadratic upper model

An objective is $L$-smooth when its gradient is $L$-Lipschitz in the Euclidean norm:

$$
\|\nabla f(x)-\nabla f(y)\|\le L\|x-y\|\quad\text{for every }x,y\in\mathbb{R}^d,
$$

where $L>0$. This is a statement about gradient variation, not about the function value itself. Smoothness gives the Descent Lemma:

$$
f(y)\le f(x)+\langle\nabla f(x),y-x\rangle+\frac{L}{2}\|y-x\|^2.
$$

The right side is a quadratic upper bound. It explains why a step based on the current gradient can be controlled: the linear term predicts reduction, while the quadratic term limits how much curvature can spoil it.

### Convex and strongly convex geometry

A differentiable function is convex when its tangent plane is a global lower bound:

$$
f(y)\ge f(x)+\langle\nabla f(x),y-x\rangle\quad\text{for all }x,y.
$$

For a $\mu$-strongly convex function, with $\mu>0$, the lower bound gains a quadratic term:

$$
f(y)\ge f(x)+\langle\nabla f(x),y-x\rangle+\frac{\mu}{2}\|y-x\|^2.
$$

Convexity rules out a lower valley hidden below a tangent plane; strong convexity additionally gives a definite amount of curvature in every direction. Thus strong convexity supplies a unique global minimiser when the other standard assumptions ensure one exists.

For a $C^2$ objective, the Hessian characterisations are

$$
0\preceq\nabla^2 f(x)\preceq LI\quad\text{for every }x
$$

for the smooth convex case, where the lower bound includes the convexity qualifier, and

$$
\nabla^2 f(x)\succeq\mu I\quad\text{for every }x
$$

for $\mu$-strong convexity. Eigenvalues make these conditions concrete: they bound curvature in every principal direction. If an objective is both $L$-smooth and $\mu$-strongly convex, its condition number is

$$
\kappa=\frac{L}{\mu}\ge 1.
$$

A large $\kappa$ means that the narrow and broad directions of a quadratic valley differ greatly. A relaxation method then tends to zig-zag unless its step is chosen with that geometry in mind.

<!-- section: SEC-03 -->
## Gradient descent and step selection

### The basic update

Gradient descent evaluates the gradient at the current iterate and moves in the opposite direction:

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),\qquad k=0,1,2,\ldots,
$$

with $x_0\in\mathbb{R}^d$ and positive $\alpha_k$. The minus sign is the descent choice. It is an algorithmic relaxation step, not a claim that a mechanical component physically travels through the same path.

A constant step sets $\alpha_k=\alpha$. If $L$ is known, $\alpha=1/L$ is a common choice. Under the usual smooth-convex assumptions, the interval $0<\alpha<2/L$ is also a common stability range. The assumptions matter: a step interval quoted without them is not a universal guarantee.

### Exact and sufficient-decrease searches

A fixed step is simple but may be conservative. Exact line search chooses the positive scalar that minimises the objective along the current negative-gradient ray:

$$
\alpha_k=\arg\min_{\alpha>0}f\bigl(x_k-\alpha\nabla f(x_k)\bigr).
$$

This is an exact one-dimensional minimisation, not merely a test that the objective went down.

Armijo backtracking instead begins with a positive trial $\bar\alpha$, contracts it by a factor $\eta\in(0,1)$, and accepts the first trial indexed by the smallest nonnegative integer $m$ that satisfies the sufficient-decrease inequality. With $\alpha_k=\eta^m\bar\alpha$ and $c\in(0,1)$, acceptance requires

$$
f(x_k-\alpha_k\nabla f(x_k))\le f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
$$

The squared gradient norm measures the predicted scale of decrease. Exact search optimises along one ray; Armijo search seeks a reliable decrease without solving that one-dimensional problem exactly.

<!-- section: SEC-04 -->
## What gradient descent guarantees

### Smooth convex objectives

Suppose $f$ is $L$-smooth and convex, has a global minimiser $x^*$, and gradient descent uses $\alpha_k=1/L$. For every $k\ge1$,

$$
f(x_k)-f(x^*)\le\frac{L\|x_0-x^*\|^2}{2k}.
$$

The objective gap therefore has an $O(1/k)$ bound. The statement is useful only with its full hypothesis list: smoothness, convexity, a global minimiser, and the specified step.

### Smooth strongly convex objectives

Suppose instead that $f$ is $L$-smooth and $\mu$-strongly convex. With the distance-oriented step

$$
\alpha=\frac{2}{L+\mu},
$$

we have

$$
\|x_k-x^*\|^2\le\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}\|x_0-x^*\|^2.
$$

With the objective-oriented step $\alpha=1/L$, the objective gap satisfies

$$
f(x_k)-f(x^*)\le\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).
$$

The two bounds are paired with different stated step sizes. Strong curvature changes the qualitative result from the sublinear convex bound to geometric contraction, but only under strong convexity and smoothness.

<!-- section: SEC-05 -->
## Momentum and acceleration

### Heavy Ball on a quadratic

Heavy Ball adds a fraction of the previous displacement to the current gradient step:

$$
x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1}),
$$

where $\beta\in[0,1)$ and the parameters must keep the iteration stable. The gradient is still evaluated at $x_k$; this is not a look-ahead method.

For the specific quadratic $f(x)=\tfrac12x^TAx$, where $A$ is symmetric positive definite with spectrum in $[\mu,L]$, the stated optimal parameters are

$$
\alpha^*=\frac{4}{(\sqrt L+\sqrt\mu)^2},\qquad
\beta^*=\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^2.
$$

The improved condition-number dependence belongs specifically to this quadratic setting. It should not be transferred automatically to arbitrary nonlinear objectives.

### Nesterov acceleration

The specified NAG recurrence starts with $y_0=x_0$ and $\lambda_0=1$. At iteration $k$, it evaluates the gradient at $y_k$:

$$
x_{k+1}=y_k-\frac1L\nabla f(y_k),
$$

then updates

$$
\lambda_{k+1}=\frac{1+\sqrt{1+4\lambda_k^2}}2,
\qquad
y_{k+1}=x_{k+1}+\frac{\lambda_k-1}{\lambda_{k+1}}(x_{k+1}-x_k).
$$

The index placement is part of the algorithm. For an $L$-smooth convex objective with a global minimiser, this parameterisation gives

$$
f(x_k)-f(x^*)\le\frac{2L\|x_0-x^*\|^2}{(k+1)^2}=O\left(\frac1{k^2}\right).
$$

Heavy Ball and NAG both use history, but their recurrences and guarantees are not interchangeable.

<!-- section: SEC-06 -->
## Stochastic gradients and adaptive scaling

### Finite sums and stochastic estimates

An empirical objective can be written

$$
f(x)=\frac1N\sum_{i=1}^N f_i(x).
$$

A stochastic gradient estimate $g_k(x_k)$ is conditionally unbiased when

$$
\mathbb E[g_k(x_k)\mid x_k]=\nabla f(x_k),
$$

and the source model also assumes bounded conditional variance:

$$
\mathbb E[\|g_k(x_k)-\nabla f(x_k)\|^2\mid x_k]\le\sigma^2.
$$

The conditioning on the current iterate matters because the sampling distribution is considered after the current information is known.

SGD uses

$$
x_{k+1}=x_k-\eta_k g_k(x_k).
$$

With persistent nonzero variance, a small constant step generally produces a nonzero error floor rather than exact convergence. Diminishing steps are governed by the Robbins--Monro series conditions

$$
\sum_{k=1}^{\infty}\eta_k=\infty,
\qquad
\sum_{k=1}^{\infty}\eta_k^2<\infty.
$$

These two conditions are not sufficient alone: objective regularity, bias or unbiasedness, moment bounds, and iterate stability are also needed in a convergence theorem.

### Three element-wise adaptive methods

All three methods below use element-wise operations, so a vector such as $g_k\odot g_k$ squares each component separately. A positive $\epsilon$ prevents division by zero and affects numerical scaling.

AdaGrad starts with $v_{-1}=0$ and accumulates squared gradients:

$$
v_k=v_{k-1}+g_k\odot g_k,
\qquad
x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k.
$$

RMSProp also starts with $v_{-1}=0$, but forgets old information through an exponential moving average, with $\gamma\in[0,1)$:

$$
v_k=\gamma v_{k-1}+(1-\gamma)g_k\odot g_k,
\qquad
x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k.
$$

Adam maintains first and second moments, both initialised at index $-1$:

$$
m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,
\qquad
v_k=\beta_2v_{k-1}+(1-\beta_2)(g_k\odot g_k).
$$

For $k$ starting at zero, early moments are biased toward zero, so Adam corrects them using

$$
\hat m_k=\frac{m_k}{1-\beta_1^{k+1}},
\qquad
\hat v_k=\frac{v_k}{1-\beta_2^{k+1}}.
$$

Its update is

$$
x_{k+1}=x_k-\frac{\eta}{\sqrt{\hat v_k}+\epsilon}\odot\hat m_k,
$$

with $\beta_1,\beta_2\in[0,1)$ and $\epsilon>0$. AdaGrad accumulates indefinitely, RMSProp tracks a moving scale, and Adam combines moving first and second moments with bias correction.

<!-- section: SEC-07 -->
## Second-order and quasi-Newton methods

### Newton's model and step

Newton's method uses the second-order Taylor model around $x_k$:

$$
f(x_k+p)\approx f(x_k)+\nabla f(x_k)^Tp+\frac12p^T\nabla^2f(x_k)p.
$$

Minimising this model with respect to $p$ gives the linear system

$$
\nabla^2f(x_k)p_k=-\nabla f(x_k),
\qquad x_{k+1}=x_k+p_k.
$$

The inverse expression is mathematically equivalent only when the Hessian is invertible:
$x_{k+1}=x_k-[\nabla^2f(x_k)]^{-1}\nabla f(x_k)$. In numerical code, solve the linear system rather than explicitly forming an inverse.

Newton convergence is local and quadratic under these conditions: $\nabla f(x^*)=0$, the Hessian at $x^*$ is positive definite, the Hessian is locally Lipschitz, and $x_0$ is sufficiently close to $x^*$. Then for some $C$,

$$
\|x_{k+1}-x^*\|\le C\|x_k-x^*\|^2.
$$

This is not a global guarantee from an arbitrary initial guess.

### BFGS approximates curvature

BFGS avoids calculating a fresh Hessian. Define the step and gradient-difference vectors

$$
 s_k=x_{k+1}-x_k,
\qquad y_k=\nabla f(x_{k+1})-\nabla f(x_k).
$$

The next Hessian approximation is required to satisfy the secant equation

$$
B_{k+1}s_k=y_k.
$$

For an inverse-Hessian approximation $H_k$, the rank-two update is

$$
H_{k+1}=(I-\rho_ks_ky_k^T)H_k(I-\rho_ky_ks_k^T)+\rho_ks_ks_k^T,
\qquad \rho_k=\frac1{y_k^Ts_k}.
$$

It requires positive curvature, $y_k^Ts_k>0$. A suitable line search helps support this condition. The search direction is

$$
p_k=-H_k\nabla f(x_k),
$$

followed by a line search. The transposes, the negative sign, and the curvature denominator are structural parts of the update.

<!-- section: SEC-08 -->
## From updates to Python operations

A mathematical update becomes a small sequence of code operations: evaluate the objective gradient, multiply by a positive step, subtract from the current vector, and repeat. The following scalar version uses $f(x)=x^2$, $\nabla f(x)=2x$, and $\alpha=0.25$. It prints the objective before each update, so a decreasing sequence is visible.

```python
x = 3.0
alpha = 0.25
for k in range(6):
    print(k, x * x)
    gradient = 2.0 * x
    x = x - alpha * gradient
print("final", x, x * x)
```

This code is numerical relaxation in an objective landscape. The loop counter is not a physical clock, and the square is a chosen objective rather than a claim about a particular energy law.

<!-- section: SEC-09 -->
## Exercises and worked solutions

<!-- exercise: EX-001 -->
### Exercise 1: Check the scope of a theorem

A design objective has a stationary point $x^*$ and a $C^2$ model. A colleague says: “Because $\nabla f(x^*)=0$, this point is a strict local minimiser, and gradient descent must satisfy the $O(1/k)$ bound.” Is the statement justified? State the additional curvature information needed for the strict local conclusion, and list the hypotheses and step size needed for the $O(1/k)$ objective-gap result.

<!-- solution: EX-001 -->
### Worked solution

The statement is not justified from stationarity alone. For a $C^2$ function, a positive-semidefinite Hessian together with stationarity is necessary at a local minimum, while a positive-definite Hessian together with stationarity is sufficient for a strict local minimum. Thus the strict conclusion needs $\nabla^2f(x^*)\succ0$.

The $O(1/k)$ bound requires an $L$-smooth convex objective, a global minimiser $x^*$, gradient descent with $\alpha_k=1/L$, and $k\ge1$. Under those conditions the bound is $f(x_k)-f(x^*)\le L\|x_0-x^*\|^2/(2k)$. Stationarity alone supplies none of the global smoothness, convexity, minimiser, or step-size hypotheses.

<!-- exercise: EX-002 -->
### Exercise 2: Take one deterministic relaxation step

For the quadratic design surrogate

$$
f(x_1,x_2)=\frac12(2x_1^2+4x_2^2),
$$
start at $x_0=(1,-1)$ and use $\alpha=0.25$. Compute $\nabla f(x_0)$ and the next iterate using gradient descent. Check the gradient from the objective before completing the update.

<!-- solution: EX-002 -->
### Worked solution

Differentiating gives $\nabla f(x_1,x_2)=(2x_1,4x_2)$, so at $(1,-1)$ the gradient is $(2,-4)$. The update is

$$
x_1=x_0-0.25\nabla f(x_0)=(1,-1)-0.25(2,-4)=(0.5,0).
$$

<!-- answer: EX-002 -->
**Checked answer:** `[0.5, 0]`

<!-- exercise: EX-003 -->
### Exercise 3: Diagnose a code update

The program below is executable, but it is mathematically incorrect for minimising $f(x)=x^2$. Identify the algorithmic error and predict whether the printed objective will decrease.

```python
x = 3.0
alpha = 0.25
for k in range(5):
    print(k, x * x)
    gradient = 2.0 * x
    x = x + alpha * gradient
```

<!-- solution: EX-003 -->
### Worked solution

The gradient is evaluated correctly, but the update uses addition. Gradient descent must subtract the positive step-size multiple: $x_{k+1}=x_k-\alpha\nabla f(x_k)$. With addition, the first value is $x_1=3+0.25(6)=4.5$, so the magnitude grows and the objective increases rather than relaxes toward zero.

A corrected executable program is:

```python
x = 3.0
alpha = 0.25
for k in range(5):
    print(k, x * x)
    gradient = 2.0 * x
    x = x - alpha * gradient
print("final", x, x * x)
```

The corrected iteration multiplies the scalar by $1-2\alpha=0.5$ at every step. Therefore $x$ approaches zero geometrically and $x^2$ decreases at each printed iteration. The two programs execute successfully, but only the second implements descent.
