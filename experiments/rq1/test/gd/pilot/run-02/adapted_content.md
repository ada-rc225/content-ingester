# Gradient Descent and Optimisation for Mechanical Engineers

<!-- section: SEC-01 -->
## Optimisation, stationarity, and curvature

### The problem and its local geometry

Unconstrained optimisation asks us to minimise a continuously differentiable objective over all vectors in $\mathbb{R}^d$:

$$\min_{x\in\mathbb{R}^d} f(x).$$

The word objective is deliberately broader than energy. In a mechanical model, potential energy can be an objective, but a fitting error, a design penalty, or a numerical residual can also be one. An optimisation iteration is likewise a computational update, not automatically a physical time step or a real relaxation trajectory.

At a differentiable local minimiser $x^*$, small changes cannot decrease the objective, so the first-order necessary condition is $\nabla f(x^*)=0$. This is stationarity, not a guarantee of a minimum: a stationary point can be a maximum or a saddle. For a $C^2$ objective, a local minimiser must also have a positive-semidefinite Hessian at a stationary point. Positive semidefinite means no negative curvature direction.

The sufficient local test is stronger. If $\nabla f(x^*)=0$ and $\nabla^2f(x^*)$ is positive definite, then $x^*$ is a strict local minimiser. Thus necessity and sufficiency use different curvature conditions. A flat direction can make the necessary test inconclusive; it does not turn stationarity into a conclusion.

### A mechanical reading of curvature

Imagine measuring how sharply a scalar function rises around an equilibrium configuration. The gradient gives the local slope, while the Hessian describes how that slope changes with direction. This picture helps interpret the tests, but an objective need not be physical energy and a zero gradient need not be force balance.

<!-- section: SEC-02 -->
## Smoothness, convexity, and conditioning

### Bounds on change

An objective is $L$-smooth when its gradient is $L$-Lipschitz:

$$\|\nabla f(x)-\nabla f(y)\|\le L\|x-y\|,\qquad \forall x,y\in\mathbb{R}^d,$$

where $L>0$. This is a bound on gradient change, not a claim that function values themselves are Lipschitz. Smoothness gives the Descent Lemma:

$$f(y)\le f(x)+\langle\nabla f(x),y-x\rangle+\frac{L}{2}\|y-x\|^2.$$

The right side is a quadratic upper model. It says that curvature cannot make the function rise faster than the stated quadratic bound.

A differentiable function is convex when its tangent plane is a global lower bound:

$$f(y)\ge f(x)+\langle\nabla f(x),y-x\rangle.$$

It is $\mu$-strongly convex when the lower bound has an additional positive quadratic term:

$$f(y)\ge f(x)+\langle\nabla f(x),y-x\rangle+\frac{\mu}{2}\|y-x\|^2,$$

with $\mu>0$. Convexity prevents a valley from bending below its tangents; strong convexity supplies a uniform amount of curvature.

### Hessian characterisations and condition number

For a $C^2$ objective, convexity and smoothness can be expressed through Hessian bounds. The smooth convex case has

$$0\preceq\nabla^2f(x)\preceq LI,\qquad \forall x,$$

where the positive-semidefinite lower bound includes the convexity qualifier. Strong convexity is characterised by

$$\nabla^2f(x)\succeq\mu I,\qquad \forall x.$$

When both $L$-smoothness and $\mu$-strong convexity hold, the condition number is

$$\kappa=\frac{L}{\mu}\ge1.$$

A large $\kappa$ describes an elongated valley: one direction changes rapidly while another changes slowly. Numerical relaxation then tends to zig-zag or progress cautiously. This is a geometric explanation, not a new convergence theorem.

<!-- section: SEC-03 -->
## Gradient descent and step selection

### The basic update

Gradient descent evaluates the current gradient and moves in the opposite direction:

$$x_{k+1}=x_k-\alpha_k\nabla f(x_k),\qquad k=0,1,2,\ldots,$$

with $x_0\in\mathbb{R}^d$ and $\alpha_k>0$. The minus sign is essential: locally, the negative gradient is the direction of decrease. A constant-step method sets $\alpha_k=\alpha$. Two common choices are $\alpha=1/L$ when $L$ is known and, under the usual smooth-convex assumptions, $\alpha\in(0,2/L)$. The interval is not assumption-free.

### Choosing steps by search

Exact line search chooses the positive scalar that minimises the objective along the current negative-gradient ray:

$$\alpha_k=\arg\min_{\alpha>0}f\bigl(x_k-\alpha\nabla f(x_k)\bigr).$$

It can be expensive because it solves a one-dimensional optimisation problem at every iteration. Armijo backtracking instead starts with a positive trial $\bar\alpha$, contracts it by $\eta\in(0,1)$, and accepts the first $\alpha_k=\bar\alpha\eta^m$ satisfying

$$f(x_k-\alpha_k\nabla f(x_k))\le f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2,$$

where $c\in(0,1)$ and $m$ is the smallest nonnegative accepted integer. The squared gradient norm makes the sufficient-decrease requirement scale with the proposed direction.

<!-- section: SEC-04 -->
## Convergence of gradient descent

### Convex objective gap

Suppose $f$ is $L$-smooth and convex, has a global minimiser $x^*$, and gradient descent uses $\alpha_k=1/L$. For every $k\ge1$,

$$f(x_k)-f(x^*)\le\frac{L\|x_0-x^*\|^2}{2k}.$$

The objective gap therefore has an $O(1/k)$ bound. Every hypothesis matters: smoothness supplies controlled curvature, convexity links local slopes to the global minimum, the minimiser must be global, and the step must be $1/L$ for this stated bound.

### Strongly convex objective

If $f$ is both $L$-smooth and $\mu$-strongly convex, the condition number controls a geometric rate. With

$$\alpha=\frac{2}{L+\mu},$$

we have the distance contraction

$$\|x_k-x^*\|^2\le\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}\|x_0-x^*\|^2.$$

With the different step $\alpha=1/L$, the objective contraction is

$$f(x_k)-f(x^*)\le\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).$$

Do not attach the distance rate to $1/L$ or the objective rate to $2/(L+\mu)$. These are separate statements with separate step sizes.

<!-- section: SEC-05 -->
## Momentum and acceleration

### Heavy Ball

Heavy Ball adds a memory term to the current-gradient step:

$$x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1}),$$

where $\beta\in[0,1)$ and the parameters must keep the iteration stable. The extra difference carries directional information from the previous move. It is not a look-ahead gradient method.

For the special quadratic $f(x)=\tfrac12x^TAx$, with $A$ symmetric positive definite and spectrum in $[\mu,L]$, the stated parameters are

$$\alpha^*=\frac{4}{(\sqrt L+\sqrt\mu)^2},\qquad \beta^*=\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^2.$$

The improved condition-number dependence belongs specifically to this symmetric-positive-definite quadratic setting; it is not a blanket guarantee for arbitrary nonlinear objectives.

### Nesterov accelerated gradient

The specified NAG variant begins with $y_0=x_0$ and $\lambda_0=1$. For $k=0,1,\ldots$, it evaluates the gradient at $y_k$:

$$x_{k+1}=y_k-\frac1L\nabla f(y_k),$$
$$\lambda_{k+1}=\frac{1+\sqrt{1+4\lambda_k^2}}2,$$
$$y_{k+1}=x_{k+1}+\frac{\lambda_k-1}{\lambda_{k+1}}(x_{k+1}-x_k).$$

The gradient is not evaluated at $x_k$. For an $L$-smooth convex objective with a global minimiser, this recurrence has

$$f(x_k)-f(x^*)\le\frac{2L\|x_0-x^*\|^2}{(k+1)^2}=O(1/k^2).$$

That rate is tied to the stated recurrence and assumptions.

<!-- section: SEC-06 -->
## Stochastic objectives and step schedules

### Finite sums and noisy gradients

For data or repeated simulations, write the empirical objective as

$$f(x)=\frac1N\sum_{i=1}^N f_i(x).$$

A stochastic gradient estimate $g_k(x_k)$ is conditionally unbiased when

$$\mathbb E[g_k(x_k)\mid x_k]=\nabla f(x_k),$$

and has bounded conditional variance when

$$\mathbb E[\|g_k(x_k)-\nabla f(x_k)\|^2\mid x_k]\le\sigma^2.$$

The conditioning on the current iterate is part of the model. Stochastic gradient descent uses

$$x_{k+1}=x_k-\eta_kg_k(x_k).$$

Persistent nonzero variance means a small constant step generally produces a nonzero error floor under standard smooth strongly convex assumptions, rather than exact convergence. Smaller steps reduce the floor but also slow movement.

### Diminishing steps

Robbins-Monro schedules require

$$\sum_{k=1}^{\infty}\eta_k=\infty,\qquad\sum_{k=1}^{\infty}\eta_k^2<\infty.$$

The first condition keeps total learning movement unbounded; the second controls accumulated noise. These two series conditions are not sufficient by themselves. A convergence theorem also needs suitable objective, bias, moment, and iterate-stability assumptions.

<!-- section: SEC-07 -->
## Adaptive first-order methods

All three methods below use element-wise products and division. The small positive $\epsilon$ protects denominators; it is not optional in the stated updates.

### AdaGrad and RMSProp

AdaGrad starts with $v_{-1}=0$ and accumulates squared gradients:

$$v_k=v_{k-1}+g_k\odot g_k,$$
$$x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k.$$

Coordinates that have accumulated large squared gradients receive smaller later scaling. RMSProp also starts with $v_{-1}=0$, but forgets old information exponentially:

$$v_k=\gamma v_{k-1}+(1-\gamma)g_k\odot g_k,$$
$$x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k,$$

with $\gamma\in[0,1)$. RMSProp is therefore not cumulative AdaGrad: the $(1-\gamma)$ factor and moving average are part of its semantics.

### Adam

Adam maintains first and second moments, both initialised at index $-1$ as zero vectors:

$$m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,$$
$$v_k=\beta_2v_{k-1}+(1-\beta_2)(g_k\odot g_k).$$

Because early moving averages start at zero, Adam applies bias correction for $k$ starting at zero:

$$\hat m_k=\frac{m_k}{1-\beta_1^{k+1}},\qquad \hat v_k=\frac{v_k}{1-\beta_2^{k+1}}.$$

The update is

$$x_{k+1}=x_k-\frac{\eta}{\sqrt{\hat v_k}+\epsilon}\odot\hat m_k,$$

where $\beta_1,\beta_2\in[0,1)$ and $\epsilon>0$. Using uncorrected moments, or using powers $k$ instead of $k+1$, changes the specified algorithm.

<!-- section: SEC-08 -->
## Newton's model and local convergence

### A second-order step

Newton's method uses the second-order model around $x_k$:

$$f(x_k+p)\approx f(x_k)+\nabla f(x_k)^Tp+\frac12p^T\nabla^2f(x_k)p.$$

The approximation is a model in $p$, not an exact identity for every objective. Minimising this quadratic model gives the linear system

$$\nabla^2f(x_k)p_k=-\nabla f(x_k),\qquad x_{k+1}=x_k+p_k.$$

The inverse expression $x_{k+1}=x_k-[\nabla^2f(x_k)]^{-1}\nabla f(x_k)$ is mathematically equivalent only when the Hessian is invertible. Numerically, solve the linear system rather than explicitly forming an inverse.

### Local, not global, speed

Newton iterates converge locally quadratically when $\nabla f(x^*)=0$, the Hessian at $x^*$ is positive definite, the Hessian is locally Lipschitz, and the initial point is sufficiently close to $x^*$. In that region,

$$\|x_{k+1}-x^*\|\le C\|x_k-x^*\|^2.$$

The close-initialisation condition is why a line search or a safer first-order phase can matter in practice. Quadratic convergence is not a global promise.

<!-- section: SEC-09 -->
## BFGS and quasi-Newton curvature

BFGS avoids computing an exact Hessian by learning curvature from successive points. Define

$$s_k=x_{k+1}-x_k,\qquad y_k=\nabla f(x_{k+1})-\nabla f(x_k).$$

The next Hessian approximation is required to satisfy the secant equation $B_{k+1}s_k=y_k$. For an inverse-Hessian approximation $H_k$, positive curvature means $y_k^Ts_k>0$, and

$$\rho_k=\frac1{y_k^Ts_k},$$
$$H_{k+1}=(I-\rho_ks_ky_k^T)H_k(I-\rho_ky_ks_k^T)+\rho_ks_ks_k^T.$$

The search direction is $p_k=-H_k\nabla f(x_k)$, so it points opposite the approximate gradient. A suitable line search supports the positive-curvature condition. The transposes and the order of $s_k$ and $y_k$ are important: swapping them breaks the stated secant meaning.

<!-- section: SEC-10 -->
## From equations to Python

An array implementation should mirror the mathematics: compute the current gradient, scale it by a scalar step, and subtract it from the current vector. In the following small example, `grad` is the vector $\nabla f(x_k)$ and `x_next` is $x_{k+1}=x_k-\alpha\nabla f(x_k)$.

```python
import numpy as np

x = np.array([1.0, 2.0])
grad = 2.0 * x
alpha = 0.25
x_next = x - alpha * grad
print(x_next)
```

The same correspondence applies element-wise in AdaGrad, RMSProp, and Adam: `*`, `/`, and `np.sqrt` operate coordinate by coordinate, while a matrix solve rather than explicit inversion represents the Newton linear system. Code makes an update concrete, but it does not remove the assumptions attached to its mathematical result.

When checking an implementation, inspect the order of operations as carefully as the numerical output. The gradient must be formed at the iterate named by the formula, the step size must have the intended sign and scale, and any stored state must be updated from the correct previous state. For a vector, a scalar step multiplies every component, whereas adaptive denominators act component by component. Printing a short sequence of iterates is often more informative than printing only the final value: descent should be compared with the objective, not inferred from a coordinate moving in a preferred physical direction. This habit separates a coding error from a legitimate difference between computational coordinates and physical variables.

<!-- section: SEC-11 -->
## Exercises and worked solutions

<!-- exercise: EX-001 -->
### Exercise 1: theorem-scope check

For each statement, decide whether it follows under the listed assumptions, and briefly correct any overclaim.

(a) If $\nabla f(x^*)=0$, then $x^*$ is a local minimum.

(b) If $f$ is $C^2$, $\nabla f(x^*)=0$, and $\nabla^2f(x^*)\succ0$, then $x^*$ is a strict local minimum.

(c) The strongly convex gradient-descent distance bound with step $2/(L+\mu)$ can be quoted for any smooth objective.

(d) The two Robbins-Monro series conditions alone guarantee stochastic convergence.

<!-- solution: EX-001 -->
### Worked solution

(a) No. Stationarity is necessary at a differentiable local minimiser, but it is not sufficient; a stationary point may be a maximum or saddle.

(b) Yes. The positive-definite Hessian plus stationarity gives the strict local-minimum test for a $C^2$ objective.

(c) No. The distance bound requires both $L$-smoothness and $\mu$-strong convexity, and its stated step is $2/(L+\mu)$.

(d) No. The divergent step-size sum and convergent squared-step sum are required conditions, not sufficient alone; objective, bias, moment, and iterate-stability assumptions are also needed.

<!-- exercise: EX-002 -->
### Exercise 2: one gradient-descent step

Consider $f(x,y)=x^2+2y^2$ at $(x_0,y_0)=(1,2)$ with constant step $\alpha=0.25$. Compute the gradient and one gradient-descent update. The minimiser is $(0,0)$.

<!-- solution: EX-002 -->
### Worked solution

The gradient is $(2x,4y)$, so $\nabla f(1,2)=(2,8)$. Therefore

$$(x_1,y_1)=(1,2)-0.25(2,8)=(0.5,0).$$

The checked update vector is recorded below. The objective gap at the new point is $f(0.5,0)-f(0,0)=0.25$.

<!-- answer: EX-002 -->
**Checked answer:** `[0.5, 1.0]`

<!-- exercise: EX-003 -->
### Exercise 3: diagnose an update in Python

The following program is executable, but its optimisation update is mathematically incorrect. Identify the algorithmic error and predict its behaviour for $f(x)=x^2$.

```python
x = 1.0
alpha = 0.25
for _ in range(4):
    grad = 2.0 * x
    x = x + alpha * grad
print(x)
```

<!-- solution: EX-003 -->
### Worked solution

The error is the plus sign. Standard gradient descent subtracts a positive step-size multiple of the gradient, so the incorrect program moves away from the minimiser at zero. Its magnitude grows geometrically here: each update is $x\leftarrow1.5x$, so the final value is $5.0625$.

The corrected executable program is:

```python
x = 1.0
alpha = 0.25
for _ in range(4):
    grad = 2.0 * x
    x = x - alpha * grad
print(x)
```

The corrected iteration is $x\leftarrow0.5x$, so it approaches zero and the objective decreases each step. Executing it prints `0.0625`, which is the expected numerical behaviour for this quadratic and step size.
