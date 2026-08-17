# Gradient-Based Optimisation: From Equilibrium to Algorithms

## 1. Optimisation and equilibrium

An unconstrained optimisation problem has the form

$$
\min_{x\in\mathbb{R}^n} f(x),
$$

where every vector $x$ is allowed. The variable might contain displacements, design dimensions, or model parameters. The objective $f$ measures what we want to reduce. It is important not to identify the objective automatically with physical energy: a least-squares error, manufacturing cost, or machine-learning loss is an algorithmic objective, not necessarily a stored physical energy. Similarly, an optimisation iteration is an algorithmic sequence, not necessarily a physical time evolution.

For a differentiable objective, a local minimiser $x^*$ cannot have a downhill first-order direction. Consequently, the first-order necessary condition is

$$
\nabla f(x^*)=0.
$$

This is the same equilibrium equation that appears when the gradient of potential energy vanishes, but the interpretation can differ. A stationary point may be a minimum, maximum, or saddle point. For twice continuously differentiable $f$, the second-order necessary condition at a local minimum is

$$
\nabla^2 f(x^*)\succeq 0,
$$

meaning $v^T\nabla^2 f(x^*)v\geq 0$ for every direction $v$. A second-order sufficient local condition is stronger: if

$$
\nabla f(x^*)=0,\qquad \nabla^2 f(x^*)\succ 0,
$$

then $x^*$ is a strict local minimiser. Positive curvature means that sufficiently small displacement raises the objective in every direction. Zero curvature does not by itself rule out a minimum; for example, $f(x)=x^4$ has a minimum at zero but a zero Hessian there.

## 2. Smoothness, convexity, and conditioning

A differentiable function is $L$-smooth if its gradient is Lipschitz continuous:

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|.
$$

For a twice differentiable function, a sufficient Hessian characterisation is $\nabla^2 f(x)\preceq LI$ everywhere. Smoothness gives the Descent Lemma:

$$
f(y)\leq f(x)+\nabla f(x)^T(y-x)+\frac{L}{2}\|y-x\|^2.
$$

The last term bounds the error in the linear approximation. It is the key inequality behind safe gradient steps.

A function is convex when

$$
f(y)\geq f(x)+\nabla f(x)^T(y-x)
$$

for all $x,y$. Its graph lies above every tangent plane. If $f$ is twice differentiable, convexity is equivalent to $\nabla^2 f(x)\succeq0$ everywhere. A convex stationary point is global, although it need not be unique.

Strong convexity with parameter $\mu>0$ means

$$
f(y)\geq f(x)+\nabla f(x)^T(y-x)+\frac{\mu}{2}\|y-x\|^2.
$$

For a twice differentiable function this is equivalent to

$$
\nabla^2 f(x)\succeq \mu I.
$$

Thus curvature is bounded below as well as above. Strong convexity gives a unique minimiser $x^*$ and relates gradient size, objective gap, and distance. If $f$ is both $L$-smooth and $\mu$-strongly convex, its condition number is

$$
\kappa=\frac{L}{\mu}\geq1.
$$

Large $\kappa$ describes an elongated bowl: progress is fast in stiff directions but slow in shallow directions. This is analogous to unequal stiffnesses in a mechanical potential, but again the objective need not be physical.

## 3. Gradient descent and step selection

The gradient-descent update is

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k).
$$

The gradient points in the direction of greatest local increase, so its negative is a local descent direction unless the gradient is zero. With an $L$-smooth objective, the Descent Lemma implies that any constant step $0<\alpha\leq1/L$ produces a decrease estimate

$$
f(x_{k+1})\leq f(x_k)-\alpha\left(1-\frac{L\alpha}{2}\right)\|\nabla f(x_k)\|^2.
$$

A common fixed choice is $\alpha=1/L$; a larger step can work, but it requires more information about curvature and can become unstable.

Exact line search chooses the best step along the current direction:

$$
\alpha_k\in\arg\min_{\alpha\geq0} f(x_k-\alpha\nabla f(x_k)).
$$

It can be expensive because each trial evaluates the objective, and the one-dimensional minimisation may itself require iterations. For a quadratic, exact line search has a particularly simple one-dimensional problem, but it still does not remove all conditioning effects.

Armijo backtracking avoids knowing $L$. Start with a trial $\alpha=\alpha_0$, choose $0<\rho<1$ and $0<c<1$, and repeatedly replace $\alpha$ by $\rho\alpha$ until

$$
f(x_k-\alpha\nabla f(x_k))\leq f(x_k)-c\alpha\|\nabla f(x_k)\|^2.
$$

Then accept the step. The right side requires a sufficient decrease proportional to the predicted first-order decrease. Under smoothness and a nonzero gradient, sufficiently small steps satisfy the test.

## 4. Convergence of gradient descent

Suppose $f$ is convex, $L$-smooth, has a finite minimiser $x^*$, and use $0<\alpha\leq1/L$. Then gradient descent has the objective-gap guarantee

$$
f(x_k)-f(x^*)\leq\frac{\|x_0-x^*\|^2}{2\alpha k}
$$

for $k\geq1$. With $\alpha=1/L$, this is $O(L\|x_0-x^*\|^2/k)$. The method therefore converges for convex problems, but only sublinearly in this general bound. Convexity alone permits flat directions, so distance to a particular minimiser need not contract geometrically and a unique minimiser need not exist.

If $f$ is additionally $\mu$-strongly convex and $L$-smooth, the minimiser is unique. For $0<\alpha\leq1/L$, one standard objective-gap bound is

$$
f(x_k)-f(x^*)\leq(1-\alpha\mu)^k\bigl(f(x_0)-f(x^*)\bigr).
$$

A corresponding distance bound is

$$
\|x_k-x^*\|^2\leq(1-\alpha\mu)^k\|x_0-x^*\|^2
$$

under the usual contraction result for this step range. Hence convergence is geometric. The choice $\alpha=1/L$ gives factor $1-1/\kappa$ in these bounds. For quadratics, sharper choices and analyses are possible, but they depend on the spectrum of the Hessian.

## 5. Momentum and acceleration

Heavy Ball adds a multiple of the previous displacement:

$$
x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1}).
$$

Here $\beta$ is a momentum parameter, often nonnegative. On a strongly convex quadratic $f(x)=\tfrac12x^TAx-b^Tx$, where the eigenvalues of $A$ lie in $[\mu,L]$, Polyak's parameter choice

$$
\alpha=\frac{4}{(\sqrt L+\sqrt\mu)^2},\qquad
\beta=\left(\frac{\sqrt L-\sqrt\mu}{\sqrt L+\sqrt\mu}\right)^2
$$

has asymptotic factor $(\sqrt\kappa-1)/(\sqrt\kappa+1)$ in the classical quadratic analysis. This result is specifically a strongly convex quadratic parameter result; it should not be transferred without qualification to arbitrary nonquadratic objectives.

Nesterov's accelerated-gradient method uses an extrapolated point. One common strongly convex recurrence is

$$
y_k=x_k+\beta_k(x_k-x_{k-1}),\qquad x_{k+1}=y_k-\alpha\nabla f(y_k),
$$

with parameters chosen from $L$ and $\mu$. For the convex, not necessarily strongly convex case, a standard formulation uses

$$
t_0=1,\quad t_{k+1}=\frac{1+\sqrt{1+4t_k^2}}2,\quad
\beta_k=\frac{t_k-1}{t_{k+1}},
$$

and $\alpha=1/L$ in the recurrence above. Its objective guarantee is

$$
f(x_k)-f(x^*)\leq\frac{2L\|x_0-x^*\|^2}{(k+1)^2}.
$$

The $O(1/k^2)$ rate improves the basic convex gradient method's $O(1/k)$ rate. Momentum creates algorithmic extrapolation, not a claim that the material system has acquired inertia or that the index $k$ is physical time.

## 6. Stochastic finite sums

Many objectives are finite sums:

$$
f(x)=\frac1m\sum_{i=1}^m f_i(x).
$$

Instead of evaluating the full gradient, select an index or minibatch and use a stochastic gradient $g_k$. Sampling uniformly gives

$$
\mathbb E[g_k\mid x_k]=\nabla f(x_k),
$$

so the estimator is conditionally unbiased. A common bounded conditional variance assumption is

$$
\mathbb E[\|g_k-\nabla f(x_k)\|^2\mid x_k]\leq\sigma^2.
$$

The stochastic update is $x_{k+1}=x_k-\alpha_k g_k$. A constant step does not generally converge exactly to a minimiser: noise remains at the solution and creates an error floor whose scale typically grows with $\alpha\sigma^2$ and worsens with curvature or conditioning. Constant steps can be useful when tracking a changing target or accepting approximate accuracy.

For classical Robbins--Monro convergence, steps usually satisfy

$$
\alpha_k>0,\qquad \sum_{k=0}^{\infty}\alpha_k=\infty,\qquad
\sum_{k=0}^{\infty}\alpha_k^2<\infty.
$$

For example, $\alpha_k=a/(k+b)$ with suitable positive constants meets these conditions. The first sum ensures continued movement toward the target; the second controls accumulated noise. Additional assumptions, such as unbiasedness, bounded variance, regularity, and an appropriate objective geometry, are still required.

## 7. Adaptive methods

Let $g_k$ be the current gradient (or stochastic gradient), and let all vector operations below be element-wise. AdaGrad accumulates squared gradients:

$$
r_k=r_{k-1}+g_k\odot g_k,
\qquad
x_{k+1}=x_k-\eta\frac{g_k}{\sqrt{r_k}+\varepsilon}.
$$

Initialise $r_{-1}=0$ and choose learning rate $\eta>0$ and small $\varepsilon>0$. The epsilon prevents division by zero. Coordinates with a large historical gradient receive smaller later steps.

RMSProp uses an exponential moving average instead of an ever-growing sum:

$$
r_k=\rho r_{k-1}+(1-\rho)(g_k\odot g_k),
\qquad
x_{k+1}=x_k-\eta\frac{g_k}{\sqrt{r_k}+\varepsilon},
$$

with $r_{-1}=0$ and $0<\rho<1$. Old information decays, so the denominator can adapt to recent scale.

Adam maintains both a first-moment average and a second-moment average:

$$
m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,
$$

$$
v_k=\beta_2v_{k-1}+(1-\beta_2)(g_k\odot g_k),
$$

starting with $m_{-1}=v_{-1}=0$. Zero initialisation biases these averages toward zero, especially at early iterations. Bias correction removes this startup effect:

$$
\widehat m_k=\frac{m_k}{1-\beta_1^{k+1}},\qquad
\widehat v_k=\frac{v_k}{1-\beta_2^{k+1}}.
$$

The Adam parameter update is

$$
x_{k+1}=x_k-\eta\frac{\widehat m_k}{\sqrt{\widehat v_k}+\varepsilon}.
$$

These methods rescale coordinates; their practical behaviour and convergence guarantees require assumptions and should not be confused with automatically selecting the globally best step.

## 8. Newton's method

Newton's second-order model at $x_k$ is

$$
m_k(p)=f(x_k)+\nabla f(x_k)^Tp+\frac12p^T\nabla^2f(x_k)p.
$$

Minimising this quadratic model gives the Newton equation

$$
\nabla^2f(x_k)p_k=-\nabla f(x_k),
$$

followed by $x_{k+1}=x_k+p_k$. In practice, solve the linear system rather than explicitly forming an inverse. Near a solution, if the Hessian is nonsingular and positive definite, the Hessian is sufficiently regular (for example, locally Lipschitz), and the initial point is sufficiently close, Newton's method has quadratic local convergence: the error is approximately proportional to the square of the previous error. Far from the solution the Hessian may be indefinite, the step may fail to descend, and a line search or damping is needed. A positive-definite Hessian also makes the Newton direction a descent direction when the gradient is nonzero.

## 9. BFGS quasi-Newton updating

BFGS avoids calculating a new Hessian by maintaining an inverse-Hessian approximation $H_k$. Define

$$
s_k=x_{k+1}-x_k,\qquad y_k=\nabla f(x_{k+1})-\nabla f(x_k).
$$

The secant equation requires

$$
H_{k+1}^{-1}s_k=y_k,
$$

or, in Hessian notation, $B_{k+1}s_k=y_k$. For an inverse approximation, the BFGS update is

$$
H_{k+1}=(I-\rho_ks_ky_k^T)H_k(I-\rho_ky_ks_k^T)+\rho_ks_ks_k^T,
\qquad
\rho_k=\frac1{y_k^Ts_k}.
$$

The curvature condition $y_k^Ts_k>0$ is essential. If $H_k\succ0$ and this condition holds, then $H_{k+1}\succ0$. The search direction is

$$
p_k=-H_k\nabla f(x_k),
$$

which is a descent direction under the same positive-definiteness condition. Usually a line search chooses $\alpha_k$ and sets $x_{k+1}=x_k+\alpha_kp_k$. Wolfe-type conditions are commonly used because they seek sufficient decrease and useful curvature. BFGS can approach Newton-like performance while using gradients and matrix updates rather than Hessians.

## 10. A small executable implementation

The following program implements gradient descent for a quadratic. The mathematical update is $x\leftarrow x-\alpha(Ax-b)$; in code, `A @ x - b` computes the gradient, multiplication by `alpha` scales it, and subtraction updates the vector.

```python
import numpy as np

A = np.array([[4.0, 0.0], [0.0, 1.0]])
b = np.array([8.0, 2.0])
x = np.array([0.0, 0.0])
alpha = 0.2

for k in range(30):
    gradient = A @ x - b
    x = x - alpha * gradient

print("x:", x)
print("gradient:", A @ x - b)
print("objective:", 0.5 * x @ A @ x - b @ x)
```

The exact minimiser solves $Ax^*=b$, so it is $(2,2)$. Since the largest eigenvalue of $A$ is $L=4$, the chosen step satisfies $0<\alpha<2/L$, and the iterates converge for this quadratic. The printed gradient should be close to zero and the objective close to its minimum.

## Exercises and worked solutions

### Exercise 1: Theorem-scope check

A learner claims: “If a differentiable objective has a stationary point, gradient descent with any positive constant step converges to that point, and the point is a unique global minimum.” Identify every missing or incorrect assumption. Explain separately what can be concluded under (a) differentiability only, (b) convexity and smoothness, and (c) strong convexity and smoothness.

**Worked solution.** Differentiability only gives the first-order necessary condition at a local minimum; a stationary point may be a maximum or saddle, and no convergence claim follows. For (b), convexity makes every stationary point global, while $L$-smoothness and a step such as $0<\alpha\leq1/L$ provide a standard objective-gap convergence result. Uniqueness and geometric distance contraction do not follow from convexity alone. For (c), $\mu$-strong convexity gives a unique minimiser; together with $L$-smoothness and $0<\alpha\leq1/L$, gradient descent has geometric objective-gap and distance bounds. “Any positive step” is false: sufficiently large steps can oscillate or diverge, even for a simple quadratic.

### Exercise 2: Hand calculation

Consider $f(x)=\tfrac12x^TAx-b^Tx$ with $A=\operatorname{diag}(4,1)$, $b=(8,2)^T$, and $x_0=(0,0)^T$. Perform one gradient-descent step with $\alpha=0.2$. Then compute the new gradient and objective values $f(x_0)$ and $f(x_1)$. State whether the step is compatible with the smoothness bound.

**Worked solution.** The gradient is $Ax-b$. At $x_0$, it is $(-8,-2)^T$. Therefore

$$
x_1=x_0-0.2(-8,-2)^T=(1.6,0.4)^T.
$$

The new gradient is $(4(1.6)-8,0.4-2)=(-1.6,-1.6)^T$. Also $f(x_0)=0$. At $x_1$, $\tfrac12x_1^TAx_1=\tfrac12(10.24+0.16)=5.2$ and $b^Tx_1=12.8+0.8=13.6$, so $f(x_1)=-8.4$. The largest eigenvalue is $L=4$, and $0.2\leq1/L=0.25$, so the step is within the standard smoothness-safe range.

### Exercise 3: Python code diagnostic

The following program is executable but mathematically incorrect. Identify the algorithmic error and predict why it fails to converge to $(2,2)$.

```python
import numpy as np

A = np.diag([4.0, 1.0])
b = np.array([8.0, 2.0])
x = np.zeros(2)
alpha = 0.2

for _ in range(30):
    gradient = A @ x - b
    x = x + alpha * gradient

print(x)
```

Provide a corrected executable program and describe its expected numerical behaviour.

**Worked solution.** The gradient points uphill, so the algorithm must subtract the scaled gradient. The incorrect line uses `x = x + alpha * gradient`, reversing the descent direction. For the first coordinate the effective scalar multiplier is $1+0.2(4)=1.8$, whose magnitude exceeds one, so that component diverges away from the minimiser.

A corrected program is:

```python
import numpy as np

A = np.diag([4.0, 1.0])
b = np.array([8.0, 2.0])
x = np.zeros(2)
alpha = 0.2

for _ in range(30):
    gradient = A @ x - b
    x = x - alpha * gradient

print("x:", x)
print("gradient:", A @ x - b)
```

The corrected iteration has error multipliers $1-0.2(4)=0.2$ and $1-0.2(1)=0.8$. Both have magnitude below one, so the iterates approach $(2,2)$, with the second coordinate converging more slowly. The final gradient should be small. This is algorithmic iteration indexed by loop count, not physical time integration.
