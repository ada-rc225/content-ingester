# Gradient descent and optimisation for mechanical engineering

<!-- section: SEC-01 -->
## From equilibrium to an optimisation problem

A mechanical system is often described by a scalar potential energy. An equilibrium configuration is a point where a small admissible displacement does not produce a first-order change in that scalar quantity. This gives a useful entry point for optimisation: imagine moving through a landscape, asking which direction reduces the quantity being minimised. The analogy is limited, however. The mathematical objective need not be a physical energy, and the variables need not be positions. The canonical problem is an unconstrained objective on a Euclidean space.

### The optimisation problem

In unconstrained optimisation we seek

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where $f:\mathbb{R}^d\to\mathbb{R}$ is at least continuously differentiable, written $f\in C^1$. The vector $x$ may contain design parameters, displacement coordinates, or coefficients in a model. “Unconstrained” means that every vector in $\mathbb{R}^d$ is part of the mathematical search domain; bounds or equilibrium constraints would define a different problem setting.

If $x^*$ is a local minimiser and $f$ is differentiable at $x^*$, then

$$
\nabla f(x^*)=0.
$$

This is a necessary condition, not a complete test. A stationary point can be a local maximum or a saddle point. In the energy picture, zero slope means only that the first-order driving force vanishes; it does not by itself tell us whether the equilibrium is stable.

### Second-order information

When $f\in C^2$, the Hessian supplies curvature. At a local minimiser, stationarity and a positive-semidefinite Hessian are necessary:

$$
\nabla f(x^*)=0,\qquad \nabla^2 f(x^*)\succeq 0.
$$

Conversely, if

$$
\nabla f(x^*)=0,\qquad \nabla^2 f(x^*)\succ 0,
$$

then $x^*$ is a strict local minimiser. Notice the difference between positive semidefinite and positive definite. The first condition allows zero curvature directions and is necessary; the second rules out those directions and is sufficient for a strict local result. Neither statement says that an arbitrary stationary point is globally best.

For numerical relaxation, this distinction matters. A method can reduce an objective locally while still finding a local rather than global minimiser, unless additional structure is available.

<!-- section: SEC-02 -->
## Smoothness, convexity, and conditioning

The next question is how reliably a gradient predicts nearby objective values. Three ideas answer it: smoothness controls how quickly the gradient changes, convexity controls global shape, and strong convexity supplies a quantitative curvature floor.

### Smoothness and a quadratic local model

A continuously differentiable function is $L$-smooth, with $L>0$, when its gradient is Lipschitz in the Euclidean norm:

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|,\qquad \forall x,y\in\mathbb{R}^d.
$$

This is a statement about the gradient, not about the function value itself. It says that changing the configuration by $x-y$ cannot change the gradient by more than a factor $L$ in norm.

Smoothness gives the Descent Lemma, a quadratic upper bound valid for all $x,y\in\mathbb{R}^d$:

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle+\frac{L}{2}\|y-x\|^2.
$$

The linear term is the local slope and the positive quadratic term is a curvature allowance. The coefficient is exactly $L/2$, and the inequality is an upper bound. This result is the bridge from a gradient formula to a step-size condition.

### Convexity and strong convexity

A differentiable function is convex when its first-order approximation is a global lower bound:

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle,\qquad \forall x,y\in\mathbb{R}^d.
$$

A convex landscape has no misleading lower valleys separated by higher barriers in the mathematical sense. Any local minimiser is also global, although the set of minimisers can contain more than one point.

A function is $\mu$-strongly convex when $\mu>0$ and the lower bound gains a quadratic term:

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle+\frac{\mu}{2}\|y-x\|^2,
\qquad \forall x,y\in\mathbb{R}^d.
$$

Strong convexity provides a uniform positive curvature floor. For a $C^2$ objective, the Hessian characterisation is

$$
0\preceq\nabla^2 f(x)\preceq LI,\qquad \forall x,
$$

for smooth convexity, where the two-sided bound includes the convexity qualifier, and

$$
\nabla^2 f(x)\succeq\mu I,\qquad \forall x,
$$

for $\mu$-strong convexity. The identity matrix $I$ makes these matrix inequalities directional statements: every curvature direction lies in the stated range.

If the objective is both $L$-smooth and $\mu$-strongly convex, its condition number is

$$
\kappa=\frac{L}{\mu}\geq 1.
$$

A large $\kappa$ describes an elongated landscape: progress can be rapid in one direction and slow in another. In a discretised mechanical model this can resemble modes with widely separated stiffness scales, but the optimisation statement itself is purely mathematical.

<!-- section: SEC-03 -->
## Gradient descent and choosing a step

Gradient descent uses the negative gradient as a local downhill direction. Starting from $x_0\in\mathbb{R}^d$, with positive step sizes $\alpha_k$, its standard update is

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),\qquad k=0,1,2,\ldots.
$$

The gradient is evaluated at the current iterate. The minus sign is essential: it moves opposite to the direction of greatest local increase. A numerical relaxation loop repeats this update until a chosen stopping test, such as a small gradient norm or a small change in objective, is reached; the stopping rule is separate from the update definition.

### Fixed and adaptive choices

With a constant step, $\alpha_k=\alpha$. If $L$ is known, a common source choice is $\alpha=1/L$. Under the usual smooth-convex assumptions, a common admissible interval is $\alpha\in(0,2/L)$. That interval is not a universal rule for arbitrary nonsmooth or nonconvex objectives.

Exact line search chooses the positive step that minimises the objective along the current negative-gradient ray:

$$
\alpha_k=\arg\min_{\alpha>0}f\bigl(x_k-\alpha\nabla f(x_k)\bigr).
$$

This is an exact one-dimensional minimisation, not merely an acceptance test. It can be expensive when each objective evaluation requires a substantial simulation.

Armijo backtracking instead starts with a positive trial step $\bar\alpha$ and contracts it using a factor $\eta\in(0,1)$. With $c\in(0,1)$, it selects the smallest nonnegative integer $m$ for which $\alpha_k=\eta^m\bar\alpha$ satisfies

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)
\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
$$

The squared gradient norm is part of the sufficient-decrease condition. The procedure trades extra objective evaluations for a step that responds to local scale.

<!-- section: SEC-04 -->
## What convergence guarantees actually say

A convergence rate is a conditional statement. It is not evidence that every gradient descent run will converge, and it does not replace checking whether the model has the required structure.

### Convex gradient descent

Suppose $f$ is $L$-smooth and convex, has a global minimiser $x^*$, and gradient descent uses $\alpha_k=1/L$. For $k\geq1$,

$$
f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k}.
$$

The objective gap therefore has an $O(1/k)$ bound. Every hypothesis matters: smoothness controls the upper model, convexity supplies global shape, the minimiser is global, and the step is exactly the stated one.

### Strongly convex gradient descent

If $f$ is $L$-smooth and $\mu$-strongly convex, two different choices give two different bounds. With $\alpha=2/(L+\mu)$,

$$
\|x_k-x^*\|^2\leq
\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}\|x_0-x^*\|^2.
$$

With $\alpha=1/L$, the objective gap satisfies

$$
f(x_k)-f(x^*)\leq
\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).
$$

Do not attach the distance contraction to the second step or the objective contraction to the first. The assumptions and the step size belong to each statement.

### Momentum and acceleration

Heavy Ball adds a fraction of the previous displacement:

$$
x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1}),
$$

where $\beta\in[0,1)$ and parameters must keep the iteration stable. The gradient remains at $x_k$; this is not a look-ahead method.

For the special quadratic $f(x)=\tfrac12x^TAx$, where $A$ is symmetric positive definite with spectrum in $[\mu,L]$, the stated Heavy-Ball parameters are

$$
\alpha^*=\frac{4}{(\sqrt L+\sqrt\mu)^2},\qquad
\beta^*=\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^2.
$$

The improved condition-number dependence belongs specifically to that quadratic setting; it must not be generalised to every objective.

The supplied NAG variant starts with $y_0=x_0$ and $\lambda_0=1$. For $k=0,1,\ldots$ it uses

$$
x_{k+1}=y_k-\frac1L\nabla f(y_k),
$$
$$
\lambda_{k+1}=\frac{1+\sqrt{1+4\lambda_k^2}}2,
\qquad
y_{k+1}=x_{k+1}+\frac{\lambda_k-1}{\lambda_{k+1}}(x_{k+1}-x_k).
$$

The gradient is evaluated at $y_k$, not $x_k$. For an $L$-smooth convex objective with a global minimiser, this exact parameterisation has

$$
f(x_k)-f(x^*)\leq\frac{2L\|x_0-x^*\|^2}{(k+1)^2}=O(1/k^2).
$$

Changing the recurrence changes the theorem’s scope.

<!-- section: SEC-05 -->
## Stochastic and adaptive gradient methods

Many objectives are empirical averages,

$$
f(x)=\frac1N\sum_{i=1}^N f_i(x).
$$

A stochastic method uses a random estimate $g_k(x_k)$. The source model assumes conditional unbiasedness and bounded conditional variance:

$$
\mathbb E[g_k(x_k)\mid x_k]=\nabla f(x_k),
$$
$$
\mathbb E[\|g_k(x_k)-\nabla f(x_k)\|^2\mid x_k]\leq\sigma^2.
$$

Conditioning on $x_k$ is important: the statement describes the random estimate after the current iterate is fixed.

SGD updates according to

$$
x_{k+1}=x_k-\eta_k g_k(x_k).
$$

With persistent nonzero variance and a small constant step, the iterates generally approach a nonzero error floor rather than converge exactly. Diminishing steps are one response. The Robbins–Monro conditions are

$$
\sum_{k=1}^{\infty}\eta_k=\infty,
\qquad
\sum_{k=1}^{\infty}\eta_k^2<\infty.
$$

These two series conditions are not sufficient alone: a convergence theorem also needs suitable assumptions on the objective, bias, moments, and iterate stability.

### Coordinate scaling

AdaGrad begins with $v_{-1}=0$ and accumulates element-wise squared gradients:

$$
v_k=v_{k-1}+g_k\odot g_k,
$$
$$
x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k,
$$

where $\epsilon>0$. The accumulation is a sum, not an exponential average.

RMSProp instead uses an exponential moving average, with $\gamma\in[0,1)$ and $v_{-1}=0$:

$$
v_k=\gamma v_{k-1}+(1-\gamma)g_k\odot g_k,
$$
$$
x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k.
$$

The $(1-\gamma)$ factor and positive $\epsilon$ are part of the algorithm.

Adam keeps both first and second exponential moments, also starting at index $-1$:

$$
m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,
\qquad
v_k=\beta_2v_{k-1}+(1-\beta_2)(g_k\odot g_k).
$$

For $k$ starting at zero, bias correction uses $k+1$:

$$
\hat m_k=\frac{m_k}{1-\beta_1^{k+1}},\qquad
\hat v_k=\frac{v_k}{1-\beta_2^{k+1}},
$$
$$
x_{k+1}=x_k-\frac{\eta}{\sqrt{\hat v_k}+\epsilon}\odot\hat m_k.
$$

Here $\beta_1,\beta_2\in[0,1)$ and $\epsilon>0$. Using uncorrected moments or replacing $k+1$ by $k$ changes the method.

<!-- section: SEC-06 -->
## Second-order optimisation

Gradient descent uses slope; second-order methods also model curvature. Around $x_k$, Newton’s method uses the second-order Taylor model

$$
f(x_k+p)\approx f(x_k)+\nabla f(x_k)^Tp+\frac12p^T\nabla^2f(x_k)p.
$$

The approximation is in the step $p$; it is not an exact identity for a general objective. The Newton step solves the linear system

$$
\nabla^2f(x_k)p_k=-\nabla f(x_k),
\qquad x_{k+1}=x_k+p_k.
$$

Writing $x_{k+1}=x_k-[\nabla^2f(x_k)]^{-1}\nabla f(x_k)$ is mathematically equivalent only when the Hessian is invertible. In numerical code, solve the linear system rather than explicitly forming the inverse. This is especially important when the Hessian is large or poorly conditioned.

Newton’s local quadratic result is also conditional. If $\nabla f(x^*)=0$, the Hessian at $x^*$ is positive definite, the Hessian is locally Lipschitz, and $x_0$ is sufficiently close to $x^*$, then locally

$$
\|x_{k+1}-x^*\|\leq C\|x_k-x^*\|^2.
$$

This is local quadratic convergence, not a global guarantee from an arbitrary initial configuration.

BFGS avoids forming the exact Hessian by building an approximation. Define

$$
s_k=x_{k+1}-x_k,\qquad y_k=\nabla f(x_{k+1})-\nabla f(x_k),
$$

and impose the secant equation

$$
B_{k+1}s_k=y_k.
$$

For positive curvature $y_k^Ts_k>0$, inverse-Hessian BFGS uses

$$
H_{k+1}=(I-\rho_ks_ky_k^T)H_k(I-\rho_ky_ks_k^T)+\rho_ks_ks_k^T,
\qquad \rho_k=\frac1{y_k^Ts_k}.
$$

Its search direction is $p_k=-H_k\nabla f(x_k)$, and a suitable line search supports the curvature condition. The step vector and gradient-difference vector have different roles, so they must not be interchanged.

### Synthesis

A practical workflow is: formulate the unconstrained objective; inspect whether smoothness, convexity, or strong convexity is justified; choose an update whose evaluation points and indices are explicit; and interpret a rate only with its hypotheses attached. Potential-energy language can make the direction intuitive, but the final check is always the canonical objective, gradient, curvature model, and algorithm.

This habit makes debugging a numerical model a reproducible engineering calculation rather than a visual judgement about a trajectory.

When implementing a method, keep three layers separate. First, the model layer defines the variables and objective. Second, the numerical layer defines how gradients, Hessians, or estimates are computed. Third, the analysis layer states what assumptions justify a rate or local claim. A visually plausible displacement history does not verify the analysis layer. Conversely, a theorem can be correct while a program uses the wrong sign, stale gradient, index, or scaling factor. Recording the iterate, objective value, and gradient norm at each step is a simple way to make those layers inspectable. For a mechanical computation, it is also useful to ask whether a low objective corresponds to the intended physical quantity, rather than relying on the analogy alone.

<!-- section: SEC-07 -->
## Exercises and worked solutions

<!-- exercise: EX-001 -->
### Exercise 1 — concept_check: is this equilibrium conclusion justified?

A reduced model has a twice continuously differentiable objective $f:\mathbb R^2\to\mathbb R$. At a candidate configuration $q^*$, measurements of the model give $\nabla f(q^*)=0$ and a Hessian with eigenvalues $-2$ and $3$. A colleague says: “The gradient is zero, so $q^*$ is a stable minimum. The usual gradient-descent convergence theorem therefore applies.” Decide which parts of the statement are justified. State what the Hessian tells you and list the missing assumptions needed before using the convex $O(1/k)$ result or the local Newton result.

<!-- solution: EX-001 -->
### Worked solution

The conclusion is not justified. Zero gradient is necessary at a differentiable local minimum, but it is not sufficient. Because the Hessian has a negative eigenvalue, it is not positive semidefinite, so the stated necessary second-order condition for a local minimum fails. The point is therefore not a local minimum under the $C^2$ model; it has a direction of negative curvature.

The convex $O(1/k)$ result additionally requires an $L$-smooth convex objective, a global minimiser, and the step $\alpha_k=1/L$. None of those facts follows from stationarity. The local Newton result requires stationarity, a positive-definite Hessian at the target, local Hessian Lipschitz continuity, and sufficiently close initialisation. The negative eigenvalue rules out that positive-definite condition here. This reasoning requires expert semantic review because it checks theorem scope and interpretation rather than a numerical identity.

<!-- exercise: EX-002 -->
### Exercise 2 — hand_calculation: one relaxation step

Consider the two-parameter calibration objective

$$
f(u,v)=(u-3)^2+2(v+1)^2.
$$

At the current parameter vector $(u_0,v_0)=(1,2)$, use step size $\alpha=0.1$. Derive the gradient, evaluate it at the current vector, and perform one standard gradient descent update. Treat the objective as smooth and use the current iterate, not a look-ahead point.

<!-- solution: EX-002 -->
### Worked solution

The gradient is

$$
\nabla f(u,v)=\begin{bmatrix}2(u-3)\\4(v+1)\end{bmatrix}.
$$

At $(1,2)$ this is $(-4,12)^T$. Therefore

$$
\begin{bmatrix}u_1\\v_1\end{bmatrix}
=
\begin{bmatrix}1\\2\end{bmatrix}
-0.1\begin{bmatrix}-4\\12\end{bmatrix}
=
\begin{bmatrix}1.4\\0.8\end{bmatrix}.
$$

The stated objective and gradient are checked at $(1,2)$, and the deterministic update is recomputed below.

<!-- answer: EX-002 -->
**Checked answer:** `[1.4, 0.8]`

<!-- exercise: EX-003 -->
### Exercise 3 — code_diagnostic: inspect the update direction

A student writes the following NumPy code for the scalar objective $f(x)=\tfrac12x^2$, whose gradient is $x$:

```python
import numpy as np
x = np.array([4.0])
alpha = 0.25
for _ in range(4):
    gradient = x.copy()
    x = x + alpha * gradient
print(x)
```

Diagnose the update. Does it implement standard gradient descent? If not, identify the line-level correction and predict the printed value after four corrected steps. Explain why evaluating `gradient` before updating `x` is appropriate.

<!-- solution: EX-003 -->
### Worked solution

The code uses `x = x + alpha * gradient`, so it moves in the positive-gradient direction. That is ascent for this objective, not gradient descent. The correction is `x = x - alpha * gradient`. The gradient is copied before the update, so it is evaluated at the current iterate, as required by the standard rule.

With the corrected line, each step multiplies $x$ by $1-0.25=0.75$. Starting at $4$, four steps give $4(0.75)^4=1.265625$. The executable check is:

```python
import numpy as np
x = np.array([4.0])
alpha = 0.25
for _ in range(4):
    gradient = x.copy()
    x = x - alpha * gradient
assert np.allclose(x, np.array([1.265625]))
print(x)
```

The code check establishes that the corrected block runs and produces the stated value; the explanation of algorithm semantics remains part of the worked solution.

<!-- answer: EX-003 -->
**Checked answer:** `1.265625`
