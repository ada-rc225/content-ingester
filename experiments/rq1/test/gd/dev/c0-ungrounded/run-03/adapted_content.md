# Numerical Optimisation Through Energy, Equilibrium, and Curvature

## 1. Local optimisation and equilibrium

An unconstrained optimisation problem has the form
\[
\min_{x\in\mathbb{R}^n} f(x),
\]
where every vector $x$ is allowed. The function $f$ is an objective, not automatically a physical energy. Potential energy is a useful analogy: an equilibrium of a conservative mechanical system often occurs where the gradient of its potential energy vanishes. However, an optimisation objective may measure cost, error, or data fit and need not have units of joules or represent a physical quantity.

If $x_*$ is a local minimiser and $f$ is differentiable, the first-order necessary condition is
\[
\nabla f(x_*)=0.
\]
This condition is necessary, not sufficient: a stationary point can be a maximum or a saddle. For twice continuously differentiable $f$, the second-order Taylor expansion near a stationary point is
\[
f(x_*+p)=f(x_*)+\tfrac12p^T\nabla^2f(x_*)p+o(\|p\|^2).
\]
Thus a second-order necessary condition for a local minimum is
\[
p^T\nabla^2 f(x_*)p\geq 0\quad\text{for every }p,
\]
meaning that the Hessian is positive semidefinite. A second-order sufficient condition is stronger: if
\[
p^T\nabla^2 f(x_*)p>0\quad\text{for every nonzero }p,
\]
so the Hessian is positive definite, then $x_*$ is a strict local minimiser. In mechanics, positive curvature corresponds to a locally stable equilibrium, while a flat direction gives only the necessary test and does not establish stability.

## 2. Smoothness, convexity, and conditioning

A differentiable function is $L$-smooth if its gradient is Lipschitz continuous:
\[
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|.
\]
For a twice differentiable function, this is implied by $\nabla^2f(x)\preceq LI$ everywhere. Smoothness limits how quickly slope can change. The Descent Lemma makes that geometric statement quantitative:
\[
f(y)\leq f(x)+\nabla f(x)^T(y-x)+\frac L2\|y-x\|^2.
\]
It is a global upper quadratic model, not a claim that the physical system follows a quadratic energy.

A function is convex when
\[
f(\theta x+(1-\theta)y)\leq \theta f(x)+(1-\theta)f(y),\qquad 0\leq\theta\leq1.
\]
For differentiable functions this is equivalent to the supporting-plane inequality
\[
f(y)\geq f(x)+\nabla f(x)^T(y-x).
\]
For twice differentiable functions, convexity is equivalent to $\nabla^2f(x)\succeq0$. Every local minimiser of a convex function is global, although it need not be unique.

Strong convexity with parameter $\mu>0$ strengthens the supporting-plane inequality:
\[
f(y)\geq f(x)+\nabla f(x)^T(y-x)+\frac\mu2\|y-x\|^2.
\]
Its Hessian characterisation is $\nabla^2f(x)\succeq\mu I$. If $f$ is both $\mu$-strongly convex and $L$-smooth, then $0<\mu\leq L$, the minimiser $x_*$ is unique, and the condition number is
\[
\kappa=\frac L\mu.
\]
A large $\kappa$ means elongated level sets: gradient steps zig-zag across a narrow valley, much as a relaxation process can respond rapidly in one stiffness direction and slowly in another. The condition number describes the objective's geometry; it is not itself a physical material property unless the model gives it that interpretation.

## 3. Gradient descent and line searches

Gradient descent uses the update
\[
x_{k+1}=x_k-\alpha_k\nabla f(x_k).
\]
The negative gradient is a local steepest-descent direction. With a constant step $\alpha_k=\alpha$, the Descent Lemma gives, for $0<\alpha<2/L$,
\[
f(x-\alpha\nabla f(x))\leq f(x)-\alpha\left(1-\frac{L\alpha}{2}\right)\|\nabla f(x)\|^2.
\]
The common safe choice $0<\alpha\leq1/L$ guarantees descent. The iterations are algorithmic states, not necessarily snapshots in physical time; the parameter $\alpha$ is a numerical step length, not automatically a time increment.

Exact line search chooses
\[
\alpha_k\in\arg\min_{\alpha\geq0}f(x_k-\alpha\nabla f(x_k)).
\]
It can be effective but requires solving a one-dimensional minimisation, and may be expensive. Armijo backtracking starts with a trial $\alpha$ and repeatedly multiplies it by $\rho\in(0,1)$ until
\[
f(x_k-\alpha\nabla f(x_k))
\leq f(x_k)-c\alpha\|\nabla f(x_k)\|^2,
\]
where $c\in(0,1)$. The sufficient-decrease test prevents steps that are too large. For an $L$-smooth function, sufficiently reduced steps pass this test.

## 4. Convergence guarantees for gradient descent

Assume $f$ is convex, differentiable, has an $L$-Lipschitz gradient, and has a minimiser $x_*$. For constant $0<\alpha\leq1/L$, gradient descent satisfies the objective-gap bound
\[
f(x_k)-f(x_*)\leq \frac{\|x_0-x_*\|^2}{2\alpha k},\qquad k\geq1.
\]
With $\alpha=1/L$, this is $O(L\|x_0-x_*\|^2/k)$. The guarantee concerns function values; iterates need not approach a unique point when the minimiser is not unique. A useful distance statement, obtained by nonexpansiveness for the same step range, is
\[
\|x_k-x_*\|\leq\|x_0-x_*\|.
\]
This is a bounded-distance guarantee, not generally a rate of convergence of distance.

Now additionally assume $f$ is $\mu$-strongly convex. For $0<\alpha\leq1/L$,
\[
f(x_k)-f(x_*)\leq (1-\alpha\mu)^k\,[f(x_0)-f(x_*)],
\]
and
\[
\|x_k-x_*\|\leq(1-\alpha\mu)^{k/2}\|x_0-x_*\|.
\]
A sharper quadratic-style contraction is available when $0<\alpha<2/L$ under standard smooth strongly convex analysis; the familiar optimal fixed step for the interval of Hessian eigenvalues is $\alpha=2/(L+\mu)$, giving factor $(\kappa-1)/(\kappa+1)$ in distance for quadratics. These statements require the stated smoothness, convexity, and existence assumptions. Without them, a gradient update can diverge or converge to a nonminimum stationary point.

## 5. Momentum and acceleration

Heavy Ball adds a velocity-like numerical memory:
\[
x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1}),
\]
with $\beta\geq0$. This difference $x_k-x_{k-1}$ is an algorithmic displacement, not physical velocity. For a strongly convex quadratic whose Hessian eigenvalues lie in $[\mu,L]$, a classical parameter result uses
\[
\alpha=\frac{4}{(\sqrt L+\sqrt\mu)^2},\qquad
\beta=\left(\frac{\sqrt L-\sqrt\mu}{\sqrt L+\sqrt\mu}\right)^2,
\]
under the quadratic setting and its associated spectral analysis. Heavy Ball can be sensitive outside that setting.

Nesterov's accelerated-gradient method uses a look-ahead point. One standard strongly-convex form is
\[
y_k=x_k+\beta(x_k-x_{k-1}),\qquad
x_{k+1}=y_k-\frac1L\nabla f(y_k),
\]
with a suitable $\beta$ depending on $\mu$ and $L$. For merely convex, $L$-smooth $f$, a common recurrence is
\[
t_0=1,\quad t_{k+1}=\frac{1+\sqrt{1+4t_k^2}}2,
\]
\[
y_k=x_k+\frac{t_k-1}{t_{k+1}}(x_k-x_{k-1}),\qquad
x_{k+1}=y_k-\frac1L\nabla f(y_k).
\]
With $x_{-1}=x_0$, its objective guarantee is $O(L\|x_0-x_*\|^2/k^2)$, specifically a standard bound is
\[
f(x_k)-f(x_*)\leq\frac{2L\|x_0-x_*\|^2}{(k+1)^2}.
\]
The extrapolation is numerical acceleration, not accelerated physical motion.

## 6. Finite-sum stochastic objectives

Many data-fitting objectives are finite sums:
\[
F(x)=\frac1m\sum_{i=1}^m f_i(x).
\]
A stochastic-gradient method samples an index $i_k$ and uses $g_k=\nabla f_{i_k}(x_k)$. Uniform sampling gives the unbiasedness condition
\[
\mathbb E[g_k\mid x_k]=\nabla F(x_k).
\]
A common noise assumption is bounded conditional variance:
\[
\mathbb E[\|g_k-\nabla F(x_k)\|^2\mid x_k]\leq\sigma^2.
\]
With a constant step, the random fluctuations generally prevent convergence to an exact point: under suitable smooth strongly convex assumptions, the expected objective gap approaches a neighbourhood whose scale is typically $O(\alpha\sigma^2/\mu)$ rather than zero. Smaller steps reduce the floor but slow progress.

Robbins–Monro diminishing steps address this limitation. Typical conditions are
\[
\alpha_k>0,\qquad \sum_{k=0}^{\infty}\alpha_k=\infty,
\qquad \sum_{k=0}^{\infty}\alpha_k^2<\infty.
\]
For example, $\alpha_k=a/(k+b)$ with positive suitable constants meets these conditions. These are asymptotic conditions and do not by themselves guarantee convergence without assumptions on unbiasedness, variance, smoothness, and the objective.

## 7. Adaptive coordinate methods

Let $g_k$ be the current gradient or stochastic gradient, and let all products, powers, and divisions below be element-wise. AdaGrad initialises $s_0=0$ and computes
\[
s_k=s_{k-1}+g_k\odot g_k,\qquad
x_{k+1}=x_k-\frac{\alpha}{\sqrt{s_k}+\varepsilon}\odot g_k.
\]
Here $\varepsilon>0$ avoids division by zero. Coordinates with large accumulated gradients receive smaller effective steps.

RMSProp replaces the unbounded sum with an exponential moving average. With $v_0=0$ and decay $\rho\in[0,1)$,
\[
v_k=\rho v_{k-1}+(1-\rho)(g_k\odot g_k),\qquad
x_{k+1}=x_k-\frac{\alpha}{\sqrt{v_k}+\varepsilon}\odot g_k.
\]
Adam maintains both a first-moment average and a second-moment average:
\[
m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,
\quad v_k=\beta_2v_{k-1}+(1-\beta_2)(g_k\odot g_k),
\]
starting with $m_0=v_0=0$. Because zero initialisation biases early averages toward zero, Adam applies bias correction:
\[
\widehat m_k=\frac{m_k}{1-\beta_1^k},\qquad
\widehat v_k=\frac{v_k}{1-\beta_2^k}.
\]
The update is
\[
x_{k+1}=x_k-\alpha\frac{\widehat m_k}{\sqrt{\widehat v_k}+\varepsilon}.
\]
These methods change coordinates' numerical scaling; their internal moments are not physical momentum or stored physical energy.

## 8. Newton's method

Newton's second-order model at $x_k$ is
\[
m_k(p)=f(x_k)+\nabla f(x_k)^Tp+\tfrac12p^T\nabla^2f(x_k)p.
\]
Minimising this model gives the Newton equation
\[
\nabla^2f(x_k)p_k=-\nabla f(x_k),
\]
followed by $x_{k+1}=x_k+p_k$, or by a line-searched version $x_{k+1}=x_k+\alpha_kp_k$. One should solve the linear system rather than explicitly invert the Hessian. A positive-definite Hessian makes $p_k$ a descent direction away from stationarity. If $f$ is sufficiently smooth, the Hessian at a solution is nonsingular (positive definite for a strict minimum), and the initial point is sufficiently close, Newton's method has local quadratic convergence: roughly $\|x_{k+1}-x_*\|\leq C\|x_k-x_*\|^2$. Far away, an indefinite or singular Hessian can produce an ascent or undefined direction, so damping or a line search is often needed.

## 9. BFGS quasi-Newton updating

BFGS avoids calculating a Hessian by updating an inverse-Hessian approximation $H_k$. Define the step and gradient difference
\[
s_k=x_{k+1}-x_k,\qquad y_k=\nabla f(x_{k+1})-\nabla f(x_k).
\]
The secant equation requires
\[
H_{k+1}^{-1}s_k=y_k,
\]
meaning that the new approximate Hessian reproduces the observed gradient change along the latest step. The inverse-Hessian BFGS update is
\[
H_{k+1}=(I-\rho_ks_ky_k^T)H_k(I-\rho_ky_ks_k^T)+\rho_ks_ks_k^T,
\qquad \rho_k=\frac1{y_k^Ts_k}.
\]
The curvature condition is $y_k^Ts_k>0$. With $H_0$ positive definite and this condition maintained, $H_{k+1}$ remains positive definite. The search direction is
\[
p_k=-H_k\nabla f(x_k),
\]
and a line search selects $\alpha_k$ before forming $x_{k+1}=x_k+\alpha_kp_k$. Wolfe-type conditions are commonly used because they seek sufficient decrease and positive curvature. BFGS is not Newton: it estimates curvature from gradient differences and can be effective without storing a full Hessian.

## 10. Mathematical updates as executable operations

The following short program implements gradient descent for a two-variable quadratic. The mathematical objective is $f(x)=\tfrac12x^TAx+b^Tx$, whose gradient is $Ax+b$. Therefore `A @ x + b` is exactly the gradient, `x - alpha * grad` is exactly the update, and the loop index counts algorithmic iterations rather than time steps.

```python
import numpy as np

A = np.array([[4.0, 0.0], [0.0, 1.0]])
b = np.array([-4.0, 2.0])
x = np.array([3.0, -3.0])
alpha = 0.2

for k in range(40):
    grad = A @ x + b
    x = x - alpha * grad

value = 0.5 * x @ A @ x + b @ x
print("x =", x)
print("objective =", value)
```

The eigenvalues of $A$ are $1$ and $4$, so $L=4$ and $\alpha=0.2<2/L=0.5$. The iterates should settle near the unique solution of $Ax+b=0$, namely $(1,-2)$, and the objective should approach its minimum. This is numerical relaxation toward an optimum; it is not a claim that a mechanical part physically moves according to this code.

## Exercises and worked solutions

### Exercise 1 — Theorem-scope check

A colleague claims: “If a differentiable objective has a point with zero gradient, that point is the unique global minimiser, and gradient descent with any positive constant step must converge.” Identify every unsupported conclusion. State assumptions that would make the conclusions valid or partially valid.

**Worked solution.** Zero gradient is only the first-order necessary condition for an unconstrained local minimiser. It also holds at maxima and saddle points. Convexity makes a stationary point global, but ordinary convexity does not ensure uniqueness; strong convexity gives uniqueness. For gradient descent, $L$-smoothness and a suitable step such as $0<\alpha\leq1/L$ give standard convergence guarantees for convex functions, while $0<\alpha<2/L$ is the familiar stable range for strongly convex quadratics. “Any positive step” is false: a step that is too large can diverge. Strong convexity additionally gives geometric objective-gap and distance bounds. None of these algorithmic statements describes physical time evolution unless a separate dynamical model establishes that interpretation.

### Exercise 2 — Hand calculation

Let $f(x)=\tfrac12x^TAx$ with $A=\operatorname{diag}(2,8)$, $x_0=(4,-2)^T$, and use gradient descent with $\alpha=1/8$. Calculate $\nabla f(x_0)$, $x_1$, and the objective values $f(x_0)$ and $f(x_1)$. State $L$, $\mu$, and $\kappa$.

**Worked solution.** Since $\nabla f(x)=Ax$,
\[
\nabla f(x_0)=(8,-16)^T.
\]
The update gives
\[
x_1=x_0-\tfrac18(8,-16)^T=(3,-0)^T=(3,0)^T.
\]
The initial objective is
\[
f(x_0)=\tfrac12(2\cdot4^2+8\cdot(-2)^2)=\tfrac12(32+32)=32.
\]
The next value is $f(x_1)=\tfrac12(2\cdot3^2)=9$. The largest and smallest eigenvalues are $L=8$ and $\mu=2$, so $\kappa=L/\mu=4$. The first coordinate remains positive and the second reaches zero because the chosen step exactly removes the eigen-direction with eigenvalue $8$ in one update. The vector is not yet optimal because the first coordinate is still nonzero.

### Exercise 3 — Python code diagnostic

The following program is executable, but its update is mathematically incorrect for the stated quadratic. Identify the error and predict its behaviour.

```python
import numpy as np

A = np.diag([1.0, 4.0])
x = np.array([3.0, 2.0])
alpha = 0.2

for _ in range(50):
    gradient = A @ x
    x = x + alpha * gradient

print(x)
```

Provide a corrected program and explain the expected numerical behaviour.

**Worked solution.** The gradient of $f(x)=\tfrac12x^TAx$ is `A @ x`. The error is the plus sign: minimisation requires moving opposite to the gradient, so the update must be `x = x - alpha * gradient`. The supplied plus-sign program moves uphill. Its components are multiplied by $1+\alpha$ and $1+4\alpha$ each iteration, namely $1.2$ and $1.8$, so the vector grows rapidly rather than approaching the minimiser $x_*=0$.

A corrected executable program is:

```python
import numpy as np

A = np.diag([1.0, 4.0])
x = np.array([3.0, 2.0])
alpha = 0.2

for _ in range(50):
    gradient = A @ x
    x = x - alpha * gradient

value = 0.5 * x @ A @ x
print(x)
print(value)
```

Here $L=4$ and $0<\alpha=0.2<2/L=0.5$, so the quadratic iteration is stable. The first coordinate is multiplied by $0.8$ each iteration and the second by $0.2$; consequently both approach zero, with the second coordinate disappearing much faster. The printed objective should be small and nonnegative. These loop iterations are numerical updates, not elapsed physical time.
