# Gradient Descent and Optimisation

## 1. Why optimisation matters in mechanical engineering

Optimisation is the systematic search for a design or operating condition that makes an objective as small or as large as possible. In mechanical engineering, the objective might be mass, fuel consumption, temperature, vibration amplitude, manufacturing cost, or the error between a simulated response and a measured response. The adjustable quantities are collected in a vector $x\in\mathbb{R}^n$. These quantities could be beam dimensions, controller gains, material parameters, or coordinates describing a mechanism. An objective function $f(x)$ assigns a numerical score to each possible choice.

The aim is often written as

$$
\min_{x\in\mathbb{R}^n} f(x).
$$

The word “optimisation” does not mean that every problem has one easily calculable answer. A function may have many local minima, flat regions, sharp valleys, or no finite minimum at all. Numerical optimisation methods therefore combine calculus with iterative computation. Starting from an initial estimate $x_0$, an algorithm generates a sequence $x_1,x_2,\ldots$ that is intended to approach a useful minimiser.

This chapter develops the main ideas behind gradient-based methods. The gradient tells us the locally steepest uphill direction, so its negative is a natural downhill direction. Curvature information explains why some valleys are difficult to traverse and motivates acceleration, adaptive step sizes, Newton’s method, and quasi-Newton methods. The same principles translate directly into short Python programs.

## 2. What it means to be optimal

Suppose $f$ is differentiable and $x^*$ is an interior local minimiser. A small displacement $p$ must not decrease the objective. The first-order Taylor approximation is

$$
f(x^*+tp)\approx f(x^*)+t\nabla f(x^*)^Tp.
$$

If the gradient were nonzero, choosing $p=-\nabla f(x^*)$ would make the linear term negative for sufficiently small positive $t$. Therefore every differentiable unconstrained local minimiser satisfies the first-order necessary condition

$$
\nabla f(x^*)=0.
$$

A point satisfying this condition is called stationary. However, a stationary point need not be a minimum. For example, the function $f(x)=x^3$ has zero derivative at the origin, but the origin is neither a local minimum nor a local maximum. Stationarity is a candidate condition, not a complete test.

If $f$ is twice differentiable, the second-order Taylor approximation is

$$
f(x^*+p)\approx f(x^*)+\nabla f(x^*)^Tp+\frac12p^T\nabla^2f(x^*)p.
$$

At a stationary point, the first-order term vanishes. A necessary second-order condition for a local minimum is

$$
p^T\nabla^2f(x^*)p\geq 0\quad\text{for every }p,
$$

which means that the Hessian is positive semidefinite. If the Hessian is positive definite, so that the quadratic form is strictly positive for every nonzero $p$, then the stationary point is a strict local minimum under the usual smoothness assumptions. The converse is not always true: a local minimum can have a Hessian that is only semidefinite, as with $f(x)=x^4$ at zero.

For constrained problems, feasible directions and Lagrange multipliers replace the simple condition $\nabla f=0$. This chapter concentrates on unconstrained optimisation, although bounds and physical constraints can often be handled by projection, reparameterisation, or a separate constrained solver.

## 3. Smoothness, convexity, and strong convexity

A differentiable function is $L$-smooth if its gradient does not change too rapidly:

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|.
$$

For a twice-differentiable function, a sufficient interpretation is that all Hessian eigenvalues are at most $L$. Smoothness gives a quadratic upper bound,

$$
f(y)\leq f(x)+\nabla f(x)^T(y-x)+\frac L2\|y-x\|^2.
$$

This inequality says that the graph cannot rise above a particular quadratic model based at $x$. It is the key tool for analysing a gradient step.

A function is convex when every line segment lies above its graph:

$$
f(\theta x+(1-\theta)y)\leq \theta f(x)+(1-\theta)f(y),\qquad 0\leq\theta\leq1.
$$

For a differentiable function, an equivalent global first-order description is

$$
f(y)\geq f(x)+\nabla f(x)^T(y-x).
$$

Thus every tangent plane is a global under-estimator. For a twice-differentiable function, convexity is equivalent to a positive-semidefinite Hessian everywhere. In a convex problem, every local minimum is global, and every stationary point is a global minimiser.

Strong convexity adds a uniform amount of curvature. A function is $\mu$-strongly convex when

$$
f(y)\geq f(x)+\nabla f(x)^T(y-x)+\frac\mu2\|y-x\|^2,
$$

for some $\mu>0$. In the twice-differentiable case, this corresponds to Hessian eigenvalues being at least $\mu$. If a function is both $L$-smooth and $\mu$-strongly convex, its condition number is $\kappa=L/\mu$. A large condition number describes a long, narrow valley, a common pattern in least-squares models and mechanical parameter fitting. Strong convexity also ensures a unique minimiser.

## 4. Gradient descent and choosing a step size

The negative gradient is the direction of greatest instantaneous decrease per unit distance. Gradient descent uses

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),
$$

where $\alpha_k>0$ is the step size, also called the learning rate. A small step is safe but may require many iterations. A large step can reduce the objective quickly, but it may overshoot, oscillate, or diverge.

For an $L$-smooth function, inserting $y=x-\alpha\nabla f(x)$ into the smoothness inequality gives

$$
f(x-\alpha\nabla f(x))\leq f(x)-\alpha\left(1-\frac{L\alpha}{2}\right)\|\nabla f(x)\|^2.
$$

Consequently, any constant step with $0<\alpha<2/L$ guarantees a decrease in this bound; the especially common choice $\alpha\leq1/L$ gives a simple robust guarantee. In practice, $L$ may be unknown, estimated poorly, or vary across a model, so a line search is useful.

With exact line search, the direction $d_k=-\nabla f(x_k)$ is chosen first and the step solves

$$
\alpha_k=\mathop{\arg\min}_{\alpha\geq0}f(x_k+\alpha d_k).
$$

For a quadratic objective this one-dimensional minimisation can often be done analytically. Exact line search is conceptually clean, but repeatedly solving a scalar optimisation problem may cost more than the gradient itself.

Armijo backtracking uses trial and error. Begin with a proposed step, often $\alpha=1$, and repeatedly multiply it by a factor $\rho\in(0,1)$ until

$$
f(x_k+\alpha d_k)\leq f(x_k)+c\alpha\nabla f(x_k)^Td_k,
$$

where $0<c<1$ and $d_k$ is a descent direction. For gradient descent, $\nabla f(x_k)^Td_k=-\|\nabla f(x_k)\|^2$. The right side therefore demands a meaningful decrease relative to the local linear prediction. Armijo search adapts to scaling and does not require knowing $L$ exactly.

A stopping rule should reflect the engineering purpose. Common choices include a small gradient norm, a small change in objective, a small change in $x$, or a maximum iteration count. A single rule can be misleading: a small gradient may occur in a broad flat region, while a small objective change can occur because the step size has become ineffective. Monitoring several quantities is better.

## 5. Convergence of basic gradient descent

For a convex, $L$-smooth function with a minimiser $x^*$, gradient descent with a suitable constant step, such as $\alpha=1/L$, has the sublinear objective bound

$$
f(x_k)-f(x^*)\leq \frac{L\|x_0-x^*\|^2}{2k}.
$$

The error decreases on the order of $1/k$. This is a guarantee, not a prediction that every iteration decreases by exactly the same amount. Near a minimiser, numerical precision, noise, and imperfect modelling affect the observed curve.

For an $L$-smooth, $\mu$-strongly convex function, the same method has linear, or geometric, convergence. With $\alpha=1/L$, a typical bound is

$$
f(x_k)-f(x^*)\leq \left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).
$$

The factor is close to one when $\kappa=L/\mu$ is large. This explains why an ill-conditioned mechanical model can make ordinary gradient descent crawl along a narrow valley. Rescaling variables, nondimensionalising physical quantities, or using a preconditioner can improve the effective condition number.

## 6. Momentum and acceleration

Heavy Ball adds a velocity-like term to the gradient update:

$$
x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1}),
$$

where $\beta$ controls momentum. The previous displacement carries the iteration through gently sloping regions, much as a mechanical mass carries velocity. It can also overshoot when curvature changes sharply, so parameters require care.

Nesterov’s accelerated gradient evaluates the gradient at a look-ahead point. One common form is

$$
y_k=x_k+\beta_k(x_k-x_{k-1}),\qquad x_{k+1}=y_k-\alpha\nabla f(y_k).
$$

For convex smooth objectives, carefully selected Nesterov parameters improve the worst-case rate from order $1/k$ to order $1/k^2$. For strongly convex objectives, tuned acceleration gives a rate related to $1-1/\sqrt{\kappa}$ rather than $1-1/\kappa$. These are theoretical improvements, but acceleration may be sensitive to noise and inaccurate parameter estimates. Restarting momentum after a function increase is a practical safeguard.

## 7. Stochastic gradients and adaptive methods

When an objective is an average over many measurements, evaluating its full gradient may be expensive. Stochastic gradient descent uses an estimate $g_k$ based on a randomly selected sample or mini-batch:

$$
x_{k+1}=x_k-\alpha_k g_k.
$$

A standard assumption is unbiasedness, $\mathbb{E}[g_k\mid x_k]=\nabla f(x_k)$, together with bounded variance, such as $\mathbb{E}[\|g_k-\nabla f(x_k)\|^2\mid x_k]\leq\sigma^2$. The iterates then fluctuate around a solution rather than following a perfectly smooth path.

For convergence to a minimiser in the classical diminishing-step setting, the steps often satisfy

$$
\sum_{k=0}^{\infty}\alpha_k=\infty,
\qquad
\sum_{k=0}^{\infty}\alpha_k^2<\infty.
$$

A schedule such as $\alpha_k=a/(k+b)^p$ with $1/2<p\leq1$ satisfies these conditions. A constant step can be preferable in practice, but with noise it generally reaches a neighbourhood whose size depends on the step and variance. Mini-batches reduce variance at greater computational cost.

AdaGrad accumulates squared gradients coordinate by coordinate:

$$
G_k=G_{k-1}+g_k\odot g_k,
\qquad
x_{k+1}=x_k-\frac{\alpha}{\sqrt{G_k}+\varepsilon}\odot g_k.
$$

Here $\odot$ denotes elementwise multiplication and division, and $\varepsilon$ prevents division by zero. Coordinates that have repeatedly received large gradients get smaller future steps. This is useful when parameters have very different scales, although the accumulated denominator can eventually become too large.

RMSProp replaces the ever-growing sum with an exponential moving average:

$$
v_k=\gamma v_{k-1}+(1-\gamma)g_k\odot g_k,
\qquad
x_{k+1}=x_k-\frac{\alpha}{\sqrt{v_k}+\varepsilon}\odot g_k.
$$

Adam combines RMSProp-like second-moment scaling with a moving average of gradients:

$$
m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,
\qquad
v_k=\beta_2v_{k-1}+(1-\beta_2)g_k\odot g_k.
$$

Because both averages start at zero, bias corrections are applied: $\widehat m_k=m_k/(1-\beta_1^k)$ and $\widehat v_k=v_k/(1-\beta_2^k)$. The update is $x_{k+1}=x_k-\alpha\widehat m_k/(\sqrt{\widehat v_k}+\varepsilon)$. Adam is convenient and often effective, but it is not a substitute for checking objective behaviour, scaling, and generalisation. Adaptive methods can settle at a nonzero gradient or behave poorly under unusual noise.

## 8. Newton and BFGS methods

Newton’s method uses a local quadratic model. If $H_k=\nabla^2f(x_k)$ is nonsingular, the Newton direction solves

$$
H_kd_k=-\nabla f(x_k),
\qquad x_{k+1}=x_k+d_k.
$$

Near a well-behaved minimiser, Newton’s method can converge quadratically: the number of correct digits may grow rapidly once the iterates enter a suitable neighbourhood. The cost is substantial. Forming and factorising a large Hessian can be expensive, and an indefinite Hessian may produce a direction that is not downhill. Damping or a line search is commonly added, and the linear system should be solved rather than explicitly computing $H_k^{-1}$.

BFGS avoids forming the exact Hessian. It builds an approximation to the inverse Hessian from successive changes

$$
s_k=x_{k+1}-x_k,\qquad y_k=\nabla f(x_{k+1})-\nabla f(x_k).
$$

The update preserves useful curvature information when $s_k^Ty_k>0$. The resulting direction is $d_k=-B_k\nabla f(x_k)$, where $B_k$ approximates the inverse Hessian. BFGS often performs well for smooth deterministic problems, while limited-memory BFGS stores compact information for large parameter vectors. A line search helps maintain descent and the curvature condition.

## 9. From equations to Python

An implementation should represent the mathematical state explicitly. A vector $x$ becomes a NumPy array, the gradient becomes a function returning an array of identical shape, and the update is ordinary elementwise arithmetic. The objective and gradient should be tested independently on simple points, using finite differences when appropriate.

For a deterministic method, record objective values and gradient norms so that convergence can be plotted. Do not confuse Python’s variable assignment with a mathematical copy: use a new array when preserving the old iterate. In stochastic code, sample mini-batches consistently, average their losses and gradients, and control random seeds during debugging.

Numerical details matter. Add a small $$epsilon$ only where division by a square root needs protection; do not hide a poor scaling problem behind an unnecessarily large value. Check shapes, avoid explicit matrix inverses, and use linear solves for Newton systems. A mechanical model may also require units: mixing millimetres with metres or newtons with kilonewtons changes the conditioning and can make a sensible step size unusable.

A reliable workflow is to begin with a quadratic objective whose solution is known. Verify the gradient by finite differences, run a few manually inspected updates, and then add line search or momentum. Compare the computed result with physical constraints and independent simulation. Optimisation is successful only when the code, mathematics, and engineering interpretation agree.

## 10. Final exercises

### Exercise 1: Conceptual and theorem scope

A differentiable function is convex and $L$-smooth but not strongly convex. A gradient-descent run uses a constant step $\alpha=1/L$. State what can be concluded about a stationary point, the global objective error, and the expected type of convergence. Then explain why a claim of a unique minimiser and geometric convergence would require an additional assumption.

#### Worked solution

For a differentiable convex function, every stationary point is a global minimiser. Thus, if an iterate reaches a point with $\nabla f(x)=0$, that point minimises the objective globally. Convexity alone does not guarantee uniqueness: a function can be flat along a direction and have many minimisers.

With smoothness and the stated step, the standard guarantee is a sublinear objective-error bound of order $1/k$, for example

$$
f(x_k)-f(x^*)\leq \frac{L\|x_0-x^*\|^2}{2k}.
$$

This is convergence in objective value under the usual existence assumptions, but it is not geometric convergence. Strong convexity would supply a positive curvature lower bound $\mu$, rule out flat minimising directions, give uniqueness, and produce a factor such as $(1-\mu/L)^k$. Therefore the missing assumption is strong convexity, together with the smoothness already stated.

### Exercise 2: One hand-calculated update

Consider the quadratic objective

$$
f(x_1,x_2)=\frac12(4x_1^2+x_2^2),
$$

starting from $x_0=(2,-1)^T$. Calculate the gradient, choose step size $\alpha=0.2$, and perform one gradient-descent update. Also calculate the objective before and after the update.

#### Worked solution

Differentiating component by component gives

$$
\nabla f(x_1,x_2)=\begin{pmatrix}4x_1\\x_2\end{pmatrix}.
$$

At $x_0=(2,-1)^T$, the gradient is

$$
\nabla f(x_0)=\begin{pmatrix}8\\-1\end{pmatrix}.
$$

The update is

$$
x_1=x_0-0.2\nabla f(x_0)
=\begin{pmatrix}2\\-1\end{pmatrix}-0.2\begin{pmatrix}8\\-1\end{pmatrix}
=\begin{pmatrix}0.4\\-0.8\end{pmatrix}.
$$

The initial objective is

$$
f(x_0)=\frac12(4(2)^2+(-1)^2)=\frac12(16+1)=8.5.
$$

At the new point,

$$
f(x_1)=\frac12(4(0.4)^2+(-0.8)^2)=\frac12(0.64+0.64)=0.64.
$$

The objective decreases from $8.5$ to $0.64$. The unequal coefficients make the $x_1$ direction steeper, so the same scalar step produces a larger change in that coordinate.

### Exercise 3: Python code diagnosis

The following code is intended to minimise $f(x)=\frac12\|x\|^2$ using gradient descent, but it contains bugs. Identify the problems and provide corrected code.

```python
import numpy as np

def f(x):
    return 0.5 * np.dot(x, x)

def grad(x):
    return x * x

x = np.array([3.0, -2.0])
alpha = 0.1
history = []

for k in range(100):
    history.append(f(x))
    x = x - alpha * grad(x)
    if np.linalg.norm(grad(x)) < 1e-6:
        break

print("x:", x)
print("objective:", history[-1])
```

#### Worked solution

The gradient of $f(x)=\frac12x^Tx$ is $\nabla f(x)=x$, not $x\odot x$. The expression in the buggy function squares each component and therefore gives a vector pointing in the wrong direction for negative components. The stopping test is mathematically acceptable after an update, but it recalculates the gradient unnecessarily. More importantly, the printed objective is the last value recorded before the final update, so it may not correspond to the printed $x$.

A corrected version is:

```python
import numpy as np

def f(x):
    return 0.5 * np.dot(x, x)

def grad(x):
    return x

x = np.array([3.0, -2.0], dtype=float)
alpha = 0.1
history = [f(x)]

for k in range(100):
    g = grad(x)
    if np.linalg.norm(g) < 1e-6:
        break
    x = x - alpha * g
    history.append(f(x))

print("x:", x)
print("objective:", f(x))
```

The corrected code uses the analytical gradient, ensures floating-point storage, tests the current gradient before updating, and evaluates the final objective at the final iterate. Since the exact minimiser is the zero vector and $0<\alpha<2$ for this objective’s unit curvature, the iterates converge geometrically toward zero.
