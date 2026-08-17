## Gradient descent as numerical relaxation

### Why optimisation matters in mechanics

In mechanical engineering, many calculations ask for a state in which a system is balanced. A structure may settle into a configuration with no net force, a mechanism may adopt a stable position, or a design may need to minimise mass while satisfying performance requirements. A useful starting picture is potential energy. If a conservative mechanical system has configuration vector $x$ and potential energy $U(x)$, an equilibrium is associated with a stationary point:

$$
\nabla U(x^*)=0.
$$

A stable equilibrium is usually a local minimum: a small displacement increases the potential energy and the system tends to relax back towards the equilibrium. Numerical optimisation borrows this landscape picture. We represent the quantity to improve by an objective function $f(x)$ and seek a point with a small value.

Gradient descent updates a trial point by moving opposite to the gradient:

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),
$$

where $\alpha_k>0$ is the step size, or learning rate. The gradient points in the direction of greatest local increase, so its negative is the direction of greatest local decrease per unit distance. The iteration is a numerical relaxation procedure: it repeatedly proposes lower-objective states.

The analogy has a boundary. An optimisation objective need not be a physical energy, and algorithmic iterations need not represent physical time evolution. The energy picture is an entry point for understanding slopes, stationary points, and stability, not a universal physical interpretation.

### A small geometric example

Consider

$$
f(x)=\frac12 x^2.
$$

Its gradient is $f'(x)=x$, and the update is

$$
x_{k+1}=(1-\alpha)x_k.
$$

If $0<\alpha<2$, the magnitude decreases: $|1-\alpha|<1$. For $0<\alpha<1$, the sequence approaches zero without crossing it. If $1<\alpha<2$, it crosses zero on alternate steps while still converging. At $\alpha=2$, the iterates oscillate with constant magnitude; for $\alpha>2$, they diverge. Thus, choosing a step is not a minor programming detail. It controls numerical stability.

## Stationary points and optimality conditions

### Unconstrained first-order conditions

For an unconstrained differentiable problem

$$
\min_{x\in\mathbb{R}^n} f(x),
$$

a local minimiser $x^*$ must satisfy

$$
\nabla f(x^*)=0.
$$

This is the first-order necessary condition. It says that every small directional derivative vanishes. It does not say that the point is a minimum. A stationary point can be a local maximum or a saddle point.

For example, $f(x)=-x^2$ has $f'(0)=0$, but $x=0$ is a maximum. For $f(x,y)=x^2-y^2$, the gradient vanishes at $(0,0)$, but moving along the $x$ direction increases the objective while moving along the $y$ direction decreases it. This is a saddle point.

In numerical work, a small gradient norm, such as $\|\nabla f(x)\|\leq\varepsilon$, is a useful stopping test, but it is not by itself a certificate of a good minimum. The result must also be interpreted using curvature, the objective value, constraints if present, and the engineering context.

### Second-order conditions

Suppose $f$ is twice continuously differentiable and let $H(x)=\nabla^2 f(x)$ denote its Hessian. At a stationary point $x^*$:

- If $H(x^*)$ is positive semidefinite, the second-order condition is necessary for a local minimum.
- If $H(x^*)$ is positive definite, the point is a strict local minimum.
- If $H(x^*)$ has a negative direction, the point is not a local minimum.
- If the Hessian is indefinite, the point is a saddle.

Positive definite means $v^THv>0$ for every nonzero vector $v$. For a two-variable quadratic, the Hessian reveals the shape of the surface: positive curvature in all directions gives a bowl; curvature of opposite signs gives a saddle.

These conditions are local. A strict local minimum need not be the global minimum when the objective is nonconvex. Conversely, a global minimum can be non-strict, with a flat direction or a whole set of minimisers.

## Smoothness, convexity, and the shape of the landscape

### Smoothness controls gradient variation

A differentiable function has an $L$-Lipschitz gradient if

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|
$$

for all relevant $x,y$. This is called $L$-smoothness. It limits how quickly the slope can change. A central consequence is the descent lemma:

$$
f(y)\leq f(x)+\nabla f(x)^T(y-x)+\frac{L}{2}\|y-x\|^2.
$$

Set $y=x-\alpha\nabla f(x)$. Then

$$
f(x-\alpha\nabla f(x))
\leq f(x)-\alpha\left(1-\frac{L\alpha}{2}\right)\|\nabla f(x)\|^2.
$$

Therefore, any $0<\alpha<2/L$ guarantees a decrease at this model level, and $\alpha\leq 1/L$ is a common conservative choice. If the largest Hessian eigenvalue is at most $L$, the function is $L$-smooth.

### Convexity removes unwanted local minima

A function is convex when

$$
f(\theta x+(1-\theta)y)\leq \theta f(x)+(1-\theta)f(y)
$$

for $0\leq\theta\leq1$. Geometrically, the graph lies below every chord. For a differentiable convex function,

$$
f(y)\geq f(x)+\nabla f(x)^T(y-x).
$$

This supporting-plane inequality says that a first-order approximation never overestimates the improvement structure in the wrong way. Most importantly, every local minimiser is global, and every point satisfying $\nabla f(x)=0$ is a global minimiser.

For twice differentiable functions, convexity is equivalent to $\nabla^2f(x)\succeq0$ throughout the domain. A quadratic

$$
f(x)=\frac12x^TAx-b^Tx+c
$$

is convex when the symmetric matrix $A$ is positive semidefinite.

### Strong convexity and conditioning

A function is $\mu$-strongly convex when its curvature is bounded below by $\mu>0$. In Hessian language,

$$
\mu I\preceq \nabla^2f(x)\preceq LI.
$$

Strong convexity gives a unique minimiser and prevents arbitrarily flat valleys. The ratio

$$
\kappa=\frac{L}{\mu}
$$

is the condition number. A small $\kappa$ means that curvature is reasonably similar in all directions. A large $\kappa$ describes a long, narrow valley. Gradient descent then makes progress slowly: a step small enough for the steep direction is too small for the shallow direction, while a larger step may overshoot.

For a quadratic with eigenvalues $\lambda_i$ of $A$, the smoothness and strong-convexity constants can be chosen as $L=\lambda_{\max}$ and $\mu=\lambda_{\min}$ when $A$ is positive definite. Rescaling variables or using a sensible unit system can improve conditioning. This is analogous to choosing coordinates that make the numerical landscape less distorted.

## Gradient descent and choosing a step size

### Basic algorithm

For a differentiable objective, the basic loop is:

1. choose an initial vector $x_0$;
2. evaluate the gradient $g_k=\nabla f(x_k)$;
3. choose $\alpha_k$;
4. set $x_{k+1}=x_k-\alpha_kg_k$;
5. stop when a suitable convergence test is met.

Useful tests include gradient norm, change in objective, change in parameters, and a maximum iteration count. A robust implementation records the objective history so that increasing values, oscillations, or stagnation can be diagnosed.

### Fixed, exact, and line-searched steps

With known $L$, $\alpha=1/L$ is easy and usually safe for smooth convex objectives. For a strongly convex quadratic, the optimal fixed step in the worst-case spectral sense is

$$
\alpha^*=\frac{2}{L+\mu},
$$

although it requires knowledge of both curvature bounds. In one-dimensional problems, an exact line search chooses the step that minimises $f(x_k-\alpha g_k)$ along the current direction. Backtracking line search starts with a trial step and reduces it until a sufficient-decrease condition is satisfied. This is useful when $L$ is unknown, but each iteration may require extra objective evaluations.

A step can be too small, causing slow progress, or too large, causing oscillation and divergence. A practical workflow is to start conservatively, inspect the objective history, and adjust using a scale-aware method rather than guessing from the raw coordinates.

### Convergence of convex gradient descent

For an $L$-smooth convex function, gradient descent with a suitable constant step, commonly $\alpha=1/L$, satisfies a sublinear objective bound of the form

$$
f(x_k)-f(x^*)\leq \frac{L\|x_0-x^*\|^2}{2k}.
$$

The notation $O(1/k)$ means that the error decreases proportionally to the reciprocal of iteration count, up to constants. This is reliable but can feel slow at high accuracy.

For an $L$-smooth, $\mu$-strongly convex function, the error decreases geometrically. With $\alpha=1/L$, a representative bound is

$$
f(x_k)-f(x^*)\leq \left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).
$$

The factor is less than one, so each step removes a roughly fixed fraction of the remaining error. With good conditioning, convergence is rapid; with large $\kappa$, many iterations may be needed.

## Momentum and acceleration

### Momentum as controlled memory

Momentum adds a velocity-like state. One common form is

$$
v_{k+1}=\beta v_k-\alpha\nabla f(x_k),\qquad x_{k+1}=x_k+v_{k+1},
$$

where $0\leq\beta<1$. The previous direction influences the next move. In a narrow valley, ordinary gradient descent can zigzag across the steep direction. Momentum can smooth that zigzag and build speed along a consistently downhill direction.

The mechanical language is useful for intuition, but the variable $v_k$ is an algorithmic memory state, not automatically a physical velocity. Momentum can also overshoot, especially when the step or $\beta$ is too large, so objective monitoring remains important.

### Nesterov-style acceleration

Accelerated methods evaluate the gradient at a look-ahead point. A simplified form uses

$$
y_k=x_k+\beta_k(x_k-x_{k-1}),\qquad x_{k+1}=y_k-\alpha\nabla f(y_k).
$$

For smooth convex problems, carefully chosen acceleration achieves an $O(1/k^2)$ objective rate rather than the usual $O(1/k)$. For strongly convex problems, accelerated rates depend on approximately $\sqrt{L/\mu}$ rather than $L/\mu$. These improvements rely on assumptions and parameter choices; acceleration is not simply “more momentum” with arbitrary settings.

## Stochastic and adaptive gradient methods

### Stochastic gradients

Suppose an objective is an average over many measurements:

$$
f(x)=\frac1N\sum_{i=1}^N f_i(x).
$$

A stochastic gradient method uses one sample or a mini-batch:

$$
x_{k+1}=x_k-\alpha_k\nabla f_{i_k}(x_k).
$$

If the sampled gradient is unbiased, its expected value equals the full gradient, but individual updates contain noise. This makes early progress inexpensive for large datasets, while near a minimiser the noise can produce a jittering iterated path. Decreasing step sizes, mini-batches, averaging, or stopping at a practical tolerance can help.

Stochastic optimisation is not automatically better for a small smooth engineering model. If the full gradient is cheap, deterministic descent may be simpler and more reproducible. Randomness also means that two runs can differ unless a seed and sampling policy are controlled.

### Adaptive methods

Adaptive methods maintain coordinate-wise statistics. In RMSProp-like form,

$$
s_{k+1}=\rho s_k+(1-\rho)g_k\odot g_k,
$$

$$
x_{k+1}=x_k-\frac{\alpha}{\sqrt{s_{k+1}}+\epsilon}\odot g_k.
$$

Here $\odot$ is element-wise multiplication and division is element-wise. Coordinates with historically large gradients receive smaller effective steps. Adam combines a first-moment estimate, related to momentum, with a second-moment estimate and usually applies bias correction.

Adaptive methods can be convenient when scales differ or gradients are noisy. Their practical behaviour and convergence guarantees depend on assumptions and variants. They do not remove the need to inspect units, scaling, objective values, and stopping criteria.

## Newton and quasi-Newton methods

### Newton's method

Near a point $x_k$, approximate the objective by a quadratic:

$$
f(x_k+p)\approx f(x_k)+g_k^Tp+\frac12p^TH_kp,
$$

where $g_k=\nabla f(x_k)$ and $H_k=\nabla^2f(x_k)$. Setting the quadratic model's gradient to zero gives

$$
H_kp_k=-g_k,
\qquad x_{k+1}=x_k+p_k.
$$

Do not explicitly compute $H_k^{-1}$ in code. Solve the linear system. Newton's method can converge very quickly near a well-behaved minimiser, but forming and factoring a large Hessian is expensive. If the Hessian is indefinite, the Newton direction may not be downhill. A line search, trust region, or a positive-definite modification can improve reliability.

For a quadratic objective with constant positive-definite Hessian, Newton reaches the exact minimiser in one ideal step. This special result should not be generalised to nonlinear or poorly scaled problems.

### Quasi-Newton ideas

Quasi-Newton methods build an approximation to the inverse Hessian using gradients and parameter changes. Define

$$
s_k=x_{k+1}-x_k,\qquad y_k=g_{k+1}-g_k.
$$

The secant condition asks an inverse-Hessian approximation $B_{k+1}$ to satisfy $B_{k+1}y_k=s_k$. BFGS updates this approximation while preserving positive definiteness under suitable curvature conditions. L-BFGS stores only a limited history, making it practical for larger problems.

These methods often require fewer iterations than plain gradient descent on smooth deterministic problems, but each iteration is more involved and line searches matter. The choice is an engineering trade-off between gradient cost, memory, robustness, and required accuracy.

## From equations to Python

### A transparent implementation

The following example minimises a two-variable quadratic. The exact minimiser is found by solving $Ax=b$, but the loop demonstrates the update rule directly.

```python
import numpy as np

A = np.array([[4.0, 0.0], [0.0, 1.0]])
b = np.array([8.0, 2.0])
x = np.array([0.0, 0.0])
alpha = 0.2
history = []

for k in range(200):
    value = 0.5 * x @ A @ x - b @ x
    gradient = A @ x - b
    history.append(value)
    if np.linalg.norm(gradient) < 1e-8:
        break
    x = x - alpha * gradient

print(x, history[-1], k + 1)
```

For $f(x)=\tfrac12x^TAx-b^Tx$, the gradient is $Ax-b$ and the Hessian is $A$. The largest eigenvalue of this $A$ is $4$, so $\alpha=0.2$ is below $1/L=0.25$. The code uses vector operations rather than separate coordinate formulas, which reduces transcription errors and makes the mathematical structure visible.

In a real model, separate the objective and gradient into functions, test the gradient on a small example, and record diagnostics. Use `np.linalg.norm(gradient)` for a stopping measure, but also guard against non-finite values. Keep the parameter units and scaling visible: a dimensionless algorithmic step may act very differently on millimetres, radians, and temperatures.

## Exercises

### Exercise 1 — Conceptual and theorem-scope check

A differentiable objective is convex and has an $L$-Lipschitz gradient. A point $\bar{x}$ satisfies $\nabla f(\bar{x})=0$. Decide whether each statement is guaranteed, not guaranteed, or guaranteed only after an additional assumption. Explain briefly.

1. $\bar{x}$ is a global minimiser.
2. $\bar{x}$ is the unique global minimiser.
3. Gradient descent with every positive step size converges.
4. With $\alpha=1/L$, gradient descent has an $O(1/k)$ objective bound.
5. If the function is also $\mu$-strongly convex, the minimiser is unique and convergence can be geometric.

### Worked solution

1. Guaranteed. For a differentiable convex function, the supporting-plane inequality with zero gradient gives $f(y)\geq f(\bar{x})$ for every $y$.
2. Not guaranteed. Convexity permits a flat set of minimisers. Uniqueness is guaranteed by strong convexity, or by another condition that rules out multiple minimisers.
3. Not guaranteed. A step that is too large can overshoot or diverge. Smoothness gives useful upper bounds such as a sufficiently small step, not convergence for every positive step.
4. Guaranteed under the standard smooth convex assumptions and a suitable interpretation of the bound. The rate is sublinear, with constants depending on the initial distance and $L$.
5. Guaranteed. Strong convexity gives a unique minimiser, and smoothness plus strong convexity gives geometric convergence for suitable fixed steps.

### Exercise 2 — Hand calculation

Let

$$
f(x,y)=\frac12(4x^2+y^2),
$$

so $\nabla f(x,y)=(4x,y)$. Start at $(x_0,y_0)=(2,2)$ and use $\alpha=0.2$.

1. Calculate $(x_1,y_1)$ and $(x_2,y_2)$.
2. Calculate $f(x_0)$, $f(x_1)$, and $f(x_2)$.
3. Explain why the two coordinates decay at different rates.

### Worked solution

The update is

$$
x_{k+1}=x_k-0.2(4x_k)=0.2x_k,
\qquad y_{k+1}=y_k-0.2y_k=0.8y_k.
$$

Therefore $(x_1,y_1)=(0.4,1.6)$ and $(x_2,y_2)=(0.08,1.28)$. The objective values are

$$
f(x_0,y_0)=\frac12(4\cdot2^2+2^2)=10,
$$

$$
f(x_1,y_1)=\frac12(4\cdot0.4^2+1.6^2)=1.6,
$$

and

$$
f(x_2,y_2)=\frac12(4\cdot0.08^2+1.28^2)=0.8224.
$$

The curvature in the $x$ direction is $4$, while the curvature in the $y$ direction is $1$. The same step size therefore gives a multiplier $0.2$ in $x$ and $0.8$ in $y$. The shallow direction is slower, illustrating conditioning: the condition number is $4/1=4$.

### Exercise 3 — Code diagnostic

The following code is intended to minimise $f(x)=\tfrac12x^2$, but it does not converge as expected. Identify the bug, correct it, and state what sequence should result from the corrected code.

```python
import numpy as np

x = 2.0
alpha = 2.0

for k in range(5):
    gradient = x
    x = x + alpha * gradient
    print(k, x)
```

### Worked solution

The gradient of $f(x)=\tfrac12x^2$ is $x$. Gradient descent moves opposite to the gradient, so the update must subtract the step, not add it. The corrected executable code is:

```python
import numpy as np

x = 2.0
alpha = 0.5

for k in range(5):
    gradient = x
    x = x - alpha * gradient
    print(k, x)
```

The original code has two problems. First, adding the gradient moves uphill. Second, even if the sign were corrected, $\alpha=2$ is at the stability boundary for this function: the sequence would alternate between $2$ and $-2$ rather than decrease. With $\alpha=0.5$, the corrected update is $x_{k+1}=0.5x_k$, producing $1.0$, $0.5$, $0.25$, $0.125$, and $0.0625$ after the five printed updates. The objective decreases because each iterate is closer to the minimiser $x^*=0$.

## Closing perspective

Gradient descent is the simplest reliable connection between a local derivative and a global computational procedure. Calculus supplies the gradient, curvature explains stability and conditioning, and Python turns the recurrence into an experiment that can be inspected. Convexity tells us when local information is enough to identify a global solution; strong convexity tells us when that solution is unique and convergence is fast in a geometric sense. Momentum, stochastic estimates, adaptive scaling, Newton steps, and quasi-Newton curvature models improve different parts of the basic method, but none replaces careful modelling and diagnostics.

When applying these ideas to a mechanical engineering problem, begin by asking what the variables represent, what quantity is being minimised, whether constraints are present, and what accuracy is useful. Then derive or verify the gradient, estimate the curvature or scale the variables, choose an update rule, and monitor both numerical behaviour and engineering meaning. That workflow is more valuable than memorising a single optimiser.