# Gradient Descent and Optimisation: From Equilibrium to Reliable Algorithms

## 1. Local Optimisation and Equilibrium

An unconstrained optimisation problem has the form

$$
\min_{x\in\mathbb{R}^n} f(x),
$$

where $x$ is a vector of design or model variables and there are no explicit restrictions such as $x_i\geq 0$. In mechanical engineering, a potential-energy function can provide a useful analogy: an equilibrium configuration is often a stationary point of energy. However, an optimisation objective is not necessarily a physical energy. It might be a data-fitting error, a manufacturing cost, or a dimensionless numerical criterion. Likewise, an algorithmic iteration is not necessarily physical time evolution; it is a computational sequence chosen to reduce an objective.

If $x^*$ is an interior local minimiser and $f$ is differentiable, then the first-order necessary condition is

$$
\nabla f(x^*)=0.
$$

This is necessary, not sufficient. A stationary point can be a maximum or a saddle. For twice continuously differentiable $f$, the second-order necessary condition is

$$
\nabla^2 f(x^*)\succeq 0,
$$

meaning that $v^T\nabla^2f(x^*)v\geq0$ for every direction $v$. If instead

$$
\nabla^2 f(x^*)\succ0,
$$

so every eigenvalue is strictly positive, then $x^*$ is a strict local minimiser: the second-order sufficient condition. In one dimension this is the familiar statement $f''(x^*)>0$. A zero or indefinite Hessian requires further analysis; the second-order test can be inconclusive or can identify a saddle when a negative curvature direction exists.

Curvature describes how rapidly the slope changes. Near a stable mechanical equilibrium, positive curvature means a small displacement produces a restoring tendency. In optimisation, curvature is a property of the objective's local geometry, whether or not any force or energy is involved.

## 2. Smoothness, Convexity, and Conditioning

A differentiable function is $L$-smooth if its gradient is Lipschitz continuous:

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|.
$$

For a twice differentiable function, a sufficient Hessian condition is $\nabla^2f(x)\preceq LI$ throughout the region of interest. Smoothness limits positive curvature and makes a gradient step predictable. The Descent Lemma states that

$$
 f(y)\leq f(x)+\nabla f(x)^T(y-x)+\frac{L}{2}\|y-x\|^2.
$$

It follows by substituting $y=x-\alpha\nabla f(x)$ that, for $0<\alpha\leq1/L$,

$$
 f(x-\alpha\nabla f(x))\leq f(x)-\alpha\left(1-\frac{L\alpha}{2}\right)\|\nabla f(x)\|^2.
$$

Thus a sufficiently small fixed step decreases the objective unless the gradient is zero.

A function is convex if

$$
 f(\theta x+(1-\theta)y)\leq \theta f(x)+(1-\theta)f(y),\qquad 0\leq\theta\leq1.
$$

For differentiable $f$, an equivalent first-order characterisation is
$f(y)\geq f(x)+\nabla f(x)^T(y-x)$. For twice differentiable $f$, convexity is equivalent on a convex domain to $\nabla^2f(x)\succeq0$. Every local minimiser of a convex function is global, although it need not be unique.

Strong convexity with parameter $\mu>0$ strengthens the inequality to

$$
 f(y)\geq f(x)+\nabla f(x)^T(y-x)+\frac{\mu}{2}\|y-x\|^2.
$$

Its Hessian characterisation is $\nabla^2f(x)\succeq\mu I$. If $f$ is both $\mu$-strongly convex and $L$-smooth, then $0<\mu\leq L$. There is a unique minimiser $x^*$, and the condition number

$$
\kappa=\frac{L}{\mu}
$$

measures anisotropy. A large condition number corresponds to a long, narrow valley: progress is possible, but a single isotropic step must be cautious in the steep direction and is slow in the shallow direction.

## 3. Gradient Descent and Step Selection

The gradient-descent update is

$$
 x_{k+1}=x_k-\alpha_k\nabla f(x_k).
$$

The negative gradient is a local downhill direction because its directional derivative is $-\|\nabla f(x_k)\|^2$. With a constant step, $\alpha_k=\alpha$, smooth analysis commonly uses $0<\alpha\leq1/L$. For a quadratic, stability can permit a broader interval, but an unnecessarily large step can oscillate or diverge.

Exact line search chooses the best distance along the current direction:

$$
\alpha_k\in\arg\min_{\alpha\geq0}f(x_k-\alpha\nabla f(x_k)).
$$

It can be expensive because it requires solving a one-dimensional minimisation problem, but it illustrates the separation between a direction and a step length.

Armijo backtracking is cheaper. Start with a trial $\alpha=\alpha_0$, choose $0<\rho<1$ and $0<c<1$, and repeatedly replace $\alpha$ by $\rho\alpha$ until

$$
 f(x_k-\alpha\nabla f(x_k))
 \leq f(x_k)-c\alpha\|\nabla f(x_k)\|^2.
$$

The test demands a sufficient decrease relative to the linear prediction. Under smoothness and a descent direction, it terminates for positive parameters. It does not require knowing $L$ exactly.

## 4. Convergence for Convex Objectives

Assume throughout this chapter that $f$ is differentiable, bounded below, convex, and $L$-smooth, and let $x^*$ be a minimiser. With a constant step $0<\alpha\leq1/L$, gradient descent gives the standard objective-gap estimate

$$
 f(x_k)-f(x^*)\leq\frac{\|x_0-x^*\|^2}{2\alpha k},\qquad k\geq1.
$$

For $\alpha=1/L$, this is an $O(L/k)$ bound. It is a function-value guarantee, not necessarily a claim that each individual iterate moves monotonically in distance toward $x^*$. If $x^*$ is not unique, a particular distance statement must be formulated carefully.

Under $\mu$-strong convexity as well as $L$-smoothness, the minimiser is unique. For $0<\alpha\leq1/L$, one useful objective-gap bound is

$$
 f(x_k)-f(x^*)\leq(1-\alpha\mu)^k\,[f(x_0)-f(x^*)],
$$

and strong convexity also yields

$$
\|x_k-x^*\|^2\leq\frac{2}{\mu}(1-\alpha\mu)^k[f(x_0)-f(x^*)].
$$

A direct distance contraction is available with the more restrictive but simple choice $0<\alpha\leq2/(L+\mu)$ in standard smooth strongly convex analysis; in particular, gradient descent converges linearly. The iteration count scales with the condition number, approximately like $O(\kappa\log(1/\varepsilon))$ for a target accuracy. A relaxation computation may resemble a structure settling toward equilibrium, but these bounds describe numerical iterations, not elapsed physical time.

## 5. Momentum and Acceleration

Heavy Ball adds a velocity-like computational memory:

$$
 x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1}),
$$

where $\beta$ is the momentum coefficient. The analogy with velocity is pedagogical only. For a strongly convex quadratic with Hessian eigenvalues in $[\mu,L]$, the classical tuned parameter result uses

$$
\alpha=\frac{4}{(\sqrt L+\sqrt\mu)^2},\qquad
\beta=\left(\frac{\sqrt L-\sqrt\mu}{\sqrt L+\sqrt\mu}\right)^2,
$$

with an asymptotic factor governed by
$({\sqrt L-\sqrt\mu})/({\sqrt L+\sqrt\mu})$. This is a special quadratic result, not a universal promise for arbitrary objectives or arbitrary parameters; momentum can overshoot.

Nesterov's accelerated-gradient method uses a look-ahead point. One common convex recurrence is

$$
 y_k=x_k+\frac{k-1}{k+2}(x_k-x_{k-1}),
 \qquad x_{k+1}=y_k-\frac1L\nabla f(y_k).
$$

For convex, differentiable, $L$-smooth $f$, with suitable initialisation such as $x_{-1}=x_0$, it satisfies

$$
 f(x_k)-f(x^*)\leq\frac{2L\|x_0-x^*\|^2}{(k+1)^2},
$$

up to indexing conventions. The $O(1/k^2)$ rate improves the basic convex gradient method's $O(1/k)$ objective rate. The look-ahead evaluation is an algorithmic device, not a prediction of a body at a future physical time.

## 6. Stochastic Finite-Sum Optimisation

Many learning and simulation objectives are finite sums:

$$
 F(x)=\frac1N\sum_{i=1}^N f_i(x).
$$

A stochastic method samples an index $i_k$ and uses $g_k=\nabla f_{i_k}(x_k)$. Uniform sampling gives the unbiasedness condition

$$
\mathbb E[g_k\mid x_k]=\nabla F(x_k).
$$

A common bounded conditional-variance assumption is

$$
\mathbb E[\|g_k-\nabla F(x_k)\|^2\mid x_k]\leq\sigma^2.
$$

With a constant step, random fluctuations generally prevent exact convergence to a point: the method reaches an error floor whose scale depends on the step size and variance. Decreasing the steps can reduce this floor, but slows progress. Under suitable smoothness, lower boundedness, and noise assumptions, Robbins--Monro conditions are

$$
\sum_{k=0}^{\infty}\alpha_k=\infty,
\qquad
\sum_{k=0}^{\infty}\alpha_k^2<\infty.
$$

They allow persistent cumulative movement while making accumulated variance finite. Typical choices include $\alpha_k=a/(k+b)^p$ with $1/2<p\leq1$, subject to the theorem's other assumptions.

## 7. Adaptive Coordinate Methods

Adaptive methods maintain element-wise statistics. For a gradient $g_k$, AdaGrad initialises $s_0=0$ and computes

$$
 s_k=s_{k-1}+g_k\odot g_k,
 \qquad
 x_{k+1}=x_k-\alpha\,g_k\oslash(\sqrt{s_k}+\varepsilon).
$$

Here $\odot$ and $\oslash$ mean element-wise multiplication and division, the square root is element-wise, and $\varepsilon>0$ prevents division by zero. Coordinates with repeatedly large gradients receive smaller effective steps.

RMSProp instead uses an exponential moving average, initialised for example by $v_0=0$:

$$
 v_k=\rho v_{k-1}+(1-\rho)(g_k\odot g_k),
 \qquad
 x_{k+1}=x_k-\alpha\,g_k\oslash(\sqrt{v_k}+\varepsilon).
$$

The forgetting factor satisfies $0<\rho<1$.

Adam keeps both a first-moment moving average and a second-moment moving average:

$$
 m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,
 \qquad
 v_k=\beta_2v_{k-1}+(1-\beta_2)(g_k\odot g_k),
$$

with $m_0=v_0=0$. Because early averages are biased toward zero, use bias correction

$$
 \widehat m_k=\frac{m_k}{1-\beta_1^k},
 \qquad
 \widehat v_k=\frac{v_k}{1-\beta_2^k},
$$

then update

$$
 x_{k+1}=x_k-\alpha\,\widehat m_k\oslash(\sqrt{\widehat v_k}+\varepsilon).
$$

These methods rescale coordinates; their practical behaviour and convergence guarantees depend on assumptions and tuning, so adaptive scaling is not automatically a replacement for curvature analysis.

## 8. Newton's Method

Newton's second-order model around $x_k$ is

$$
 m_k(p)=f(x_k)+\nabla f(x_k)^Tp+\frac12p^T\nabla^2f(x_k)p.
$$

Setting the model gradient to zero gives the linear system

$$
 \nabla^2f(x_k)p_k=-\nabla f(x_k),
 \qquad x_{k+1}=x_k+p_k.
$$

One should solve the system rather than explicitly forming an inverse. If the Hessian is positive definite near a solution, the Hessian is Lipschitz continuous, and the initial point is sufficiently close, Newton's method has local quadratic convergence: roughly, the error at the next step is proportional to the square of the current error. Far from a minimiser, an indefinite or ill-conditioned Hessian can give a non-descent direction or an unstable step. A line search or trust region is then commonly added.

## 9. BFGS Quasi-Newton Updating

BFGS avoids computing a Hessian by maintaining an inverse-Hessian approximation $H_k$. First calculate

$$
 s_k=x_{k+1}-x_k,\qquad y_k=\nabla f(x_{k+1})-\nabla f(x_k).
$$

The secant equation is $H_{k+1}y_k=s_k$ (equivalently, a Hessian approximation $B_{k+1}$ should satisfy $B_{k+1}s_k=y_k$). With $\rho_k=1/(y_k^Ts_k)$, the inverse-Hessian update is

$$
 H_{k+1}=(I-\rho_ks_ky_k^T)H_k(I-\rho_ky_ks_k^T)+\rho_ks_ks_k^T.
$$

The curvature condition $y_k^Ts_k>0$ is essential for preserving positive definiteness when $H_k\succ0$. In practice, a line search is used to choose $x_{k+1}=x_k+\alpha_kp_k$, with search direction

$$
 p_k=-H_k\nabla f(x_k).
$$

If the line search satisfies suitable Wolfe conditions, the curvature condition is typically secured. BFGS therefore combines gradient information, a learned local metric, and controlled step length without explicitly calculating second derivatives.

## 10. Mathematical Updates in Python

The following short program minimises $f(x)=\tfrac12x^TAx-b^Tx$ using gradient descent. The mathematical gradient is $\nabla f(x)=Ax-b$; the code computes `A @ x - b`, then applies the subtraction $x-\alpha\nabla f(x)$. The positive-definite matrix makes this a strongly convex quadratic.

```python
import numpy as np

A = np.array([[4.0, 1.0], [1.0, 3.0]])
b = np.array([1.0, 2.0])
alpha = 0.2
x = np.zeros(2)

for k in range(40):
    gradient = A @ x - b          # grad f(x) = A x - b
    x = x - alpha * gradient      # x_(k+1) = x_k - alpha grad f(x_k)

value = 0.5 * x @ A @ x - b @ x
print(x)
print(value)
```

For this quadratic, the exact minimiser solves $Ax^*=b$. A sufficiently small step should make the printed point approach that solution and the objective decrease toward its minimum. The loop index is an iteration counter, not a physical clock.

## Exercises and Worked Solutions

### Exercise 1: Theorem-scope check

A colleague claims: “If $\nabla f(x^*)=0$, then $x^*$ is the unique global minimiser, and gradient descent with any positive constant step converges.” Give a precise correction. State the additional assumptions needed for a global conclusion, and distinguish the roles of smoothness and strong convexity.

**Worked solution.** The stationary condition is only first-order necessary for an interior local minimiser. Without curvature information, $x^*$ may be a maximum or saddle. If $f$ is convex, every stationary point is a global minimiser, but it need not be unique. If $f$ is strongly convex, the minimiser is unique. For gradient-descent convergence, differentiability alone is insufficient. A standard guarantee assumes convexity and $L$-smoothness, with a step such as $0<\alpha\leq1/L$; the objective gap then decreases at an $O(1/k)$ rate. Strong convexity adds a linear, geometric rate and distance bounds. An arbitrary positive step can overshoot, oscillate, or diverge, especially when curvature is large.

### Exercise 2: Hand calculation

Let $f(x)=\tfrac12x^TAx-b^Tx$ with
$A=\begin{bmatrix}4&1\\1&3\end{bmatrix}$, $b=\begin{bmatrix}1\\2\end{bmatrix}$, and $x_0=(0,0)^T$. Perform one gradient-descent step with $\alpha=0.2$, and compute $f(x_0)$ and $f(x_1)$.

**Worked solution.** The gradient is $Ax-b$. At $x_0$, $\nabla f(x_0)=-b=(-1,-2)^T$. Therefore

$$
 x_1=x_0-0.2(-1,-2)^T=(0.2,0.4)^T.
$$

Clearly $f(x_0)=0$. Next, $Ax_1=(1.2,1.4)^T$, so $Ax_1-b=(0.2,-0.6)^T$. The value is

$$
 f(x_1)=\tfrac12x_1^TAx_1-b^Tx_1
 =\tfrac12(0.2\cdot1.2+0.4\cdot1.4)-(0.2+0.8)=-0.72.
$$

The objective decreased. This is a numerical relaxation step; it should not be interpreted as a claim that a physical structure moved for a time interval of $0.2$.

### Exercise 3: Python code diagnostic

The following program is executable, but it contains an algorithmic error. Identify it and predict why the objective does not converge to the minimum.

```python
import numpy as np

A = np.array([[4.0, 1.0], [1.0, 3.0]])
b = np.array([1.0, 2.0])
x = np.zeros(2)
alpha = 0.2

for _ in range(40):
    gradient = A @ x - b
    x = x + alpha * gradient       # suspicious update

print(0.5 * x @ A @ x - b @ x)
```

Provide a corrected executable program and explain its expected numerical behaviour.

**Worked solution.** The error is the plus sign. The gradient points uphill for a minimisation problem, so the update must subtract it. The corrected program is:

```python
import numpy as np

A = np.array([[4.0, 1.0], [1.0, 3.0]])
b = np.array([1.0, 2.0])
x = np.zeros(2)
alpha = 0.2

for _ in range(40):
    gradient = A @ x - b
    x = x - alpha * gradient

print(x)
print(0.5 * x @ A @ x - b @ x)
```

The incorrect code moves in the ascent direction. For this positive-definite quadratic, its iterates generally grow rather than approach $Ax=b$, and the objective eventually becomes very large. The corrected code approaches $x^*=A^{-1}b=(1/11,7/11)^T$, approximately $(0.0909,0.6364)^T$, and the objective approaches the finite minimum $-0.6818$ (approximately). The precise monotonicity and rate depend on the step size, but $\alpha=0.2$ is suitable here because it is below the reciprocal of the largest eigenvalue of $A$.
