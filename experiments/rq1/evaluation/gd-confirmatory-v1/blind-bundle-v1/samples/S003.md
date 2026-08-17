# Gradient Descent and Optimisation

## 1. What optimisation means in engineering

Optimisation is the systematic search for a design or operating condition that makes an objective as small or as large as possible. In mechanical engineering, the design variables might be a beam thickness, a motor current, a joint angle, or a vector of parameters in a simulation model. The objective might measure mass, compliance, energy consumption, tracking error, or a weighted combination of these quantities. We will write a minimisation problem as

$$
\min_{x\in\mathbb{R}^n} f(x).
$$

Here, $x$ is the vector of decision variables and $f$ is a scalar objective. Constraints are important in real design, but this chapter concentrates first on unconstrained optimisation so that the central ideas are clear. The same ideas later appear inside constrained, penalised, and machine-learning algorithms.

A point $x^*$ is a global minimiser if $f(x^*)\leq f(x)$ for every admissible $x$. It is a local minimiser if the inequality holds in some neighbourhood of $x^*$. A local minimum is often all that a numerical method can guarantee. Understanding the shape of $f$ tells us when a local answer is also global and how quickly an algorithm approaches it.

For a mechanical example, suppose $x$ contains two controller gains and $f(x)$ is the simulated integral of squared vibration plus a small penalty on actuator effort. Each evaluation may require solving differential equations. An optimisation method therefore needs not only a sensible direction but also a manageable number of objective and gradient evaluations.

## 2. Derivatives and optimality conditions

For a differentiable function, the gradient $\nabla f(x)$ is the vector of first partial derivatives. It points in the direction of steepest local increase under the Euclidean norm. A small displacement $p$ gives the first-order approximation

$$
f(x+p)\approx f(x)+\nabla f(x)^Tp.
$$

If $x^*$ is an interior local minimiser and $f$ is differentiable, the first-order necessary condition is

$$
\nabla f(x^*)=0.
$$

This is necessary, not sufficient. A stationary point can be a minimum, a maximum, or a saddle point. For example, $f(x)=x^3$ has zero derivative at zero but no local minimum there, while $f(x,y)=x^2-y^2$ has a stationary saddle.

When $f$ is twice differentiable, the Hessian $\nabla^2f(x)$ contains the second partial derivatives. Its quadratic approximation is

$$
f(x+p)\approx f(x)+\nabla f(x)^Tp+\frac12p^T\nabla^2f(x)p.
$$

At an interior local minimum, the second-order necessary condition is that the Hessian at the point is positive semidefinite:

$$
p^T\nabla^2f(x^*)p\geq 0\quad\text{for every }p.
$$

If the Hessian is positive definite, meaning the inequality is strict for every nonzero $p$, then $x^*$ is a strict local minimum. This is a second-order sufficient condition. Positive definiteness says that the objective curves upward in every direction. Semidefiniteness allows flat directions, so it cannot by itself distinguish a minimum from a higher-order saddle.

For example, the potential-energy-like objective $f(x)=\tfrac12x^TAx-b^Tx$ has gradient $Ax-b$ and Hessian $A$. If $A$ is symmetric positive definite, the stationary equation $Ax=b$ has one solution and that solution is the unique global minimiser. This observation connects optimisation directly to linear algebra and to many discretised mechanical models.

## 3. Smoothness, convexity, and strong convexity

A function is $L$-smooth if its gradient is Lipschitz continuous:

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|.
$$

For a twice differentiable function, a sufficient condition is that every Hessian eigenvalue is at most $L$. Smoothness limits how sharply the gradient can change. It makes a gradient step predictable because the function cannot rise unexpectedly far above its linear approximation.

A differentiable function is convex when

$$
f(y)\geq f(x)+\nabla f(x)^T(y-x)
$$

for all $x$ and $y$. Thus every tangent plane lies below the graph. A twice differentiable function is convex if its Hessian is positive semidefinite everywhere. Convexity rules out troublesome non-global local minima: every local minimiser is global, although there may be several minimisers.

A function is $\mu$-strongly convex when

$$
f(y)\geq f(x)+\nabla f(x)^T(y-x)+\frac{\mu}{2}\|y-x\|^2,
$$

where $\mu>0$. Equivalently, for a twice differentiable function, the Hessian is bounded below by $\mu I$. Strong convexity gives a definite bowl shape, so the minimiser is unique. If a function is both $L$-smooth and $\mu$-strongly convex, its condition number is $\kappa=L/\mu$. A large $\kappa$ means a long, narrow valley; such a problem is often slow for ordinary gradient descent.

For the quadratic objective with symmetric positive-definite $A$, $L$ can be chosen as the largest eigenvalue of $A$, and $\mu$ as its smallest eigenvalue. In a finite-element stiffness problem, scaling or preconditioning attempts to reduce the corresponding condition number.

## 4. Gradient descent and choosing a step

Gradient descent uses the update

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),
$$

where $\alpha_k>0$ is the step size, or learning rate. The negative gradient is a descent direction whenever the gradient is nonzero because

$$
\nabla f(x_k)^T(-\nabla f(x_k))=-\|\nabla f(x_k)\|^2<0.
$$

A step that is too small makes progress painfully slow. A step that is too large can overshoot, oscillate, or diverge. For an $L$-smooth convex function, a standard safe fixed choice is $0<\alpha\leq 1/L$. For a strongly convex quadratic, the sharper stability range is $0<\alpha<2/L$; the best fixed step based only on the extreme eigenvalues is $2/(L+\mu)$.

Exact line search chooses the best distance along the current descent direction:

$$
\alpha_k=\arg\min_{\alpha\geq0} f(x_k-\alpha\nabla f(x_k)).
$$

It can be inexpensive for a quadratic because the one-dimensional minimisation has a closed form. For $f(x)=\tfrac12x^TAx-b^Tx$ with symmetric positive-definite $A$, writing $g_k=\nabla f(x_k)$ gives

$$
\alpha_k=\frac{g_k^Tg_k}{g_k^TAg_k}.
$$

For a general simulation objective, exact line search may require many expensive evaluations, so an approximate rule is preferable.

Armijo backtracking starts with a trial step, often $\alpha=1$, and repeatedly multiplies it by a factor $\rho\in(0,1)$ until

$$
f(x_k-\alpha g_k)\leq f(x_k)-c\alpha\|g_k\|^2,
$$

where $g_k=\nabla f(x_k)$ and $c\in(0,1)$ is small, such as $10^{-4}$. The right-hand side demands a sufficient decrease relative to the linear prediction. Backtracking is adaptive, needs no known value of $L$, and usually avoids catastrophic steps.

In Python, the update must use the gradient evaluated at the old point, not the newly updated point. A basic structure is `x = x - alpha * grad(x)`. In practical code, separate objective and gradient functions, record the objective history, and stop when the gradient norm or step norm is below a tolerance. If gradients come from an automatic-differentiation package, ensure that the update is performed outside the differentiation graph when appropriate.

## 5. Convergence of gradient methods

For an $L$-smooth convex objective with a minimiser $x^*$, gradient descent with $\alpha=1/L$ satisfies a function-value bound of the form

$$
f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k}.
$$

Thus the error decreases as $O(1/k)$. This is a sublinear rate: obtaining another decimal place eventually requires substantially more iterations. The result assumes smoothness and convexity; without them, the same statement is not valid.

For an $L$-smooth, $\mu$-strongly convex objective, a fixed step $\alpha\leq1/L$ yields geometric convergence. A representative distance bound is

$$
\|x_k-x^*\|\leq(1-\alpha\mu)^k\|x_0-x^*\|.
$$

The factor is less than one, so each iteration contracts the error. With $\alpha=1/L$, the contraction is approximately $1-1/\kappa$. This explains why conditioning matters. Newton and quasi-Newton methods try to account for curvature and reduce the effects of narrow valleys.

For nonconvex smooth objectives, gradient descent generally guarantees only that some gradient norms become small, under suitable boundedness and step assumptions. A small gradient is a first-order stationary condition, not proof of a global minimum. In mechanical calibration, this distinction matters when several physically plausible operating regimes exist.

## 6. Momentum: Heavy Ball and Nesterov acceleration

Momentum remembers previous motion. Polyak's Heavy Ball method uses

$$
v_{k+1}=\beta v_k+\nabla f(x_k),\qquad x_{k+1}=x_k-\alpha v_{k+1},
$$

with $0\leq\beta<1$. An equivalent convention stores a displacement and writes $x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1})$. Momentum can carry the method through shallow directions while damping alternating motion across a steep direction. It can, however, overshoot and its cleanest guarantees require careful parameter restrictions.

Nesterov's accelerated gradient evaluates the gradient at a look-ahead point. One common form is

$$
y_k=x_k+\beta_k(x_k-x_{k-1}),\qquad x_{k+1}=y_k-\alpha\nabla f(y_k).
$$

For smooth convex objectives, appropriately selected coefficients give an $O(1/k^2)$ function-value rate, faster in theory than ordinary gradient descent. For strongly convex objectives, a constant momentum choice can produce a rate depending on $\sqrt{\kappa}$ rather than $\kappa$. The look-ahead evaluation is the defining distinction: Heavy Ball uses the current point, whereas Nesterov designs the extrapolation and gradient evaluation together.

Momentum is useful when a design objective has an elongated valley, but it is not a substitute for sensible scaling. Normalising variables so that a millimetre, a kilogram, and an ampere do not create wildly different numerical magnitudes can improve all methods.

## 7. Stochastic gradients and adaptive methods

A stochastic gradient $g_k$ is a random estimate of the true gradient. A common assumption is unbiasedness conditioned on the current iterate:

$$
\mathbb{E}[g_k\mid x_k]=\nabla f(x_k),
$$

with bounded variance, for example

$$
\mathbb{E}[\|g_k-\nabla f(x_k)\|^2\mid x_k]\leq\sigma^2.
$$

This occurs when an objective is an average over experiments, samples, or operating conditions and only a mini-batch is used. The update is $x_{k+1}=x_k-\alpha_kg_k$. With diminishing steps satisfying $\sum_k\alpha_k=\infty$ and $\sum_k\alpha_k^2<\infty$, such as $\alpha_k=a/(k+1)$, stochastic noise can diminish while the algorithm continues to move toward a solution under standard assumptions. A constant step usually reaches a neighbourhood whose size depends on the noise and step size rather than converging exactly.

AdaGrad accumulates squared coordinates:

$$
r_k=r_{k-1}+g_k\odot g_k,\qquad x_{k+1}=x_k-\frac{\alpha}{\sqrt{r_k}+\epsilon}\odot g_k.
$$

Here $\odot$ and the square root act componentwise. Coordinates with persistently large gradients receive smaller future steps. AdaGrad is attractive for sparse signals, but its ever-growing accumulator can eventually make steps too small.

RMSProp replaces the cumulative sum with an exponential average:

$$
r_k=\gamma r_{k-1}+(1-\gamma)g_k\odot g_k,
$$

followed by the same scaled update. It therefore adapts to recent gradient magnitudes and avoids AdaGrad's permanent decay. Adam also tracks a first moment and a second moment:

$$
m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,
$$

$$
v_k=\beta_2v_{k-1}+(1-\beta_2)g_k\odot g_k.
$$

Because both start at zero, Adam uses bias corrections $\hat m_k=m_k/(1-\beta_1^k)$ and $\hat v_k=v_k/(1-\beta_2^k)$, then updates with $\hat m_k/(\sqrt{\hat v_k}+\epsilon)$. These methods are often effective in noisy, differently scaled problems, but adaptive performance is not a universal proof of convergence to the exact minimiser. Monitor the objective on a representative validation set and choose hyperparameters deliberately.

## 8. Newton and BFGS methods

Newton's method uses local curvature. At $x_k$, the quadratic model is minimised by solving

$$
\nabla^2f(x_k)p_k=-\nabla f(x_k),\qquad x_{k+1}=x_k+p_k.
$$

It is usually better to solve this linear system than to form an explicit inverse. Near a solution with a nonsingular Hessian and good regularity, Newton's method has quadratic local convergence: roughly, the number of correct digits can double per iteration. Far from a solution, an indefinite or poorly scaled Hessian may produce an ascent direction. Damping, line search, or a modified positive-definite Hessian is then needed.

For a large finite-element model, storing and factorising a dense Hessian may be prohibitive. BFGS avoids direct Hessian calculation by maintaining an approximation $B_k$ to the inverse Hessian. With $s_k=x_{k+1}-x_k$ and $y_k=\nabla f(x_{k+1})-\nabla f(x_k)$, the inverse-Hessian update is

$$
B_{k+1}=\left(I-\frac{s_ky_k^T}{y_k^Ts_k}\right)B_k\left(I-\frac{y_ks_k^T}{y_k^Ts_k}\right)+\frac{s_ks_k^T}{y_k^Ts_k},
$$

provided $y_k^Ts_k>0$. The search direction is $p_k=-B_k\nabla f(x_k)$, followed by a line search. BFGS learns curvature from gradient changes and often gives much faster progress than gradient descent while requiring only gradient vectors. Limited-memory BFGS stores compact history rather than a full matrix, making it suitable for many variables.

The choice is therefore a trade-off. Gradient descent is simple and cheap per iteration. Momentum improves first-order progress. Adaptive stochastic methods handle noisy data. Newton is powerful when reliable curvature is available. BFGS is a practical middle ground when gradients are available but Hessians are expensive.

## 9. Turning mathematics into reliable Python

A mathematical algorithm becomes a program through a precise sequence: evaluate at the current point, compute a direction, select a step, update the point, and test a stopping rule. Keep these stages visible. A function should return a scalar objective, and a gradient function should return a vector with the same shape as `x`. Shape errors can silently produce incorrect broadcasting, so small tests with finite differences are valuable.

For a finite-difference check, compare a gradient component with

$$
\frac{f(x+he_i)-f(x-he_i)}{2h}
$$

for a small but not excessively small $h$. The comparison is diagnostic, not the preferred production gradient. Store copies of iterates if a history is required; storing the same mutable array repeatedly records only its final value. Also distinguish a minimisation objective from a maximisation score: maximising $q$ is equivalent to minimising $-q$.

A robust implementation should report the iteration count, final objective, gradient norm, and whether the stopping criterion was reached. For simulation-based objectives, catch invalid states and use a clear penalty policy rather than allowing undefined values to contaminate the iteration. Finally, test on a quadratic whose answer is known before applying the method to a complicated mechanical model.

## 10. Final exercises

### Exercise 1 — Scope of an optimality theorem

Suppose $f$ is twice continuously differentiable and $x^*$ is an interior point with $\nabla f(x^*)=0$ and a positive-semidefinite Hessian. Does this information alone prove that $x^*$ is a strict local minimum? State what additional second-order information would give that conclusion, and explain why convexity changes the interpretation.

**Worked solution.** No. The conditions are first-order necessary and second-order necessary, but a positive-semidefinite Hessian may contain zero-curvature directions. The point could be a non-strict minimum or a higher-order saddle. For example, $f(x,y)=x^2-y^4$ has zero gradient and a positive-semidefinite Hessian at the origin, yet points with small nonzero $y$ have smaller objective values, so the origin is not a local minimum. If the Hessian is positive definite at $x^*$, the second-order sufficient condition proves a strict local minimum. If $f$ is convex on its whole domain, every local minimum is global; if it is also strongly convex, the minimiser is unique. Convexity does not make a merely semidefinite Hessian at one point positive definite, but it does rule out a non-global local minimum.

### Exercise 2 — One gradient update

Consider the objective

$$
f(x_1,x_2)=(x_1-3)^2+2(x_2+1)^2.
$$

At $x_0=(1,2)^T$, calculate $\nabla f(x_0)$ and perform one gradient-descent update with step size $\alpha=0.1$. Also calculate the new objective value.

**Worked solution.** Differentiating componentwise gives

$$
\nabla f(x)=\begin{bmatrix}2(x_1-3)\\4(x_2+1)\end{bmatrix}.
$$

At $x_0=(1,2)^T$,

$$
\nabla f(x_0)=\begin{bmatrix}-4\\12\end{bmatrix}.
$$

The update is

$$
x_1=x_0-0.1\nabla f(x_0)=\begin{bmatrix}1\\2\end{bmatrix}-0.1\begin{bmatrix}-4\\12\end{bmatrix}=\begin{bmatrix}1.4\\0.8\end{bmatrix}.
$$

The starting value is $f(x_0)=4+18=22$. The new value is

$$
f(x_1)=(-1.6)^2+2(1.8)^2=2.56+6.48=9.04.
$$

The objective decreased substantially because the update moved in the negative-gradient direction. The exact minimiser is $(3,-1)^T$, so further steps are still needed.

### Exercise 3 — Diagnose and correct Python code

The following code is intended to minimise $f(x)=(x-4)^2$ using gradient descent, but it contains several bugs.

```python
def f(x):
    return (x - 4) ** 2

def grad(x):
    return 2 * (x - 4) ** 2

x = 0.0
alpha = 0.1
for k in range(20):
    x = x - alpha * grad(x)
    print(k, f(x))
```

Identify the mathematical error and provide corrected code. Explain one useful diagnostic that could be added.

**Worked solution.** The derivative of $(x-4)^2$ is $2(x-4)$, not $2(x-4)^2$. The buggy gradient is always nonnegative, so it cannot point left when $x<4$; the algorithm moves in the wrong direction from its initial value. A corrected version is:

```python
def f(x):
    return (x - 4.0) ** 2

def grad(x):
    return 2.0 * (x - 4.0)

x = 0.0
alpha = 0.1
for k in range(20):
    g = grad(x)
    x = x - alpha * g
    print(k, x, f(x), abs(g))
```

The additional gradient-norm output checks the first-order stopping condition. For production use, the loop could stop when `abs(g) < tolerance`, and a gradient check could compare `grad(x)` with a centred finite difference of `f`. The step size is stable here because the objective has curvature $2$ and $0<\alpha<2/2=1$; the chosen value $0.1$ is conservative.
