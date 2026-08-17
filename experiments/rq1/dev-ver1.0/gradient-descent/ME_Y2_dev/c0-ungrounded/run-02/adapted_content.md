# Gradient Descent and Optimisation Through Mechanical Equilibrium

## 1. Why optimisation looks like relaxation

A useful way to begin is with a mechanical system that is allowed to relax. Imagine a mass attached to a spring. If the mass is displaced from its unloaded position and released, the spring force pushes it back towards equilibrium. With damping, the motion loses energy and eventually settles at a position where the net force is zero. The final position is an equilibrium, and for a stable equilibrium the potential energy is locally minimal.

This gives a helpful intuition for optimisation: a scalar objective function can be viewed as a landscape, and an algorithm can move through that landscape looking for a low point. In this chapter, the variable being adjusted may be a displacement, a vector of design parameters, or the weights of a simple model. The objective may be potential energy, compliance, error, or another scalar performance measure.

The analogy has limits. Gradient descent is not normally a physical time simulation. Its iteration number is an algorithmic index, not necessarily time, and its step size is not automatically a mass, damping coefficient, or physical time step. A discrete optimisation method can also move in ways that no actual mechanical system would follow. The canonical mathematical problem is simply

$$
\min_{x\in\mathbb{R}^n} f(x),
$$

where $x$ is a vector and $f(x)$ is a scalar objective. We will return to this formulation throughout.

For an unconstrained problem, every vector $x\in\mathbb{R}^n$ is allowed. There are no explicit restrictions such as fixed bounds, geometric compatibility equations, or positive-only design variables. Constraints are important in engineering, but unconstrained optimisation is the cleanest setting in which to understand the central ideas.

## 2. Stationary points and optimality conditions

Suppose $f$ is differentiable and $x^*$ is an interior local minimiser. A necessary first-order condition is

$$
\nabla f(x^*)=0.
$$

The gradient is the vector of first partial derivatives,

$$
\nabla f(x)=
\begin{bmatrix}
\partial f/\partial x_1\\
\vdots\\
\partial f/\partial x_n
\end{bmatrix}.
$$

It points in the direction of greatest local increase of $f$. Therefore, $-\nabla f(x)$ is the direction of greatest local decrease. In a potential-energy interpretation, the negative gradient is analogous to a force derived from the potential, although the units and physical meaning depend on the chosen objective and coordinates.

The condition $\nabla f(x^*)=0$ is necessary, not sufficient. A stationary point may be a minimum, a maximum, or a saddle point. For example, for

$$
f(x)=x^2,
$$

$x=0$ is a minimum, while for $f(x)=-x^2$ it is a maximum. The function $f(x,y)=x^2-y^2$ has zero gradient at $(0,0)$, but that point is a saddle: the function increases along the $x$ direction and decreases along the $y$ direction.

If $f$ is twice differentiable, the Hessian matrix is

$$
\nabla^2 f(x)=\left[\frac{\partial^2 f}{\partial x_i\partial x_j}\right]_{i,j=1}^n.
$$

At a local minimum, a necessary second-order condition is that the Hessian at the point is positive semidefinite:

$$
v^T\nabla^2 f(x^*)v\geq 0 \quad\text{for every }v.
$$

If the Hessian is positive definite,

$$
v^T\nabla^2 f(x^*)v>0 \quad\text{for every nonzero }v,
$$

then $x^*$ is a strict local minimum. These conditions are local. They do not by themselves prove that the point is the best point globally.

For a spring with potential energy $U(q)=\tfrac12 kq^2$, the equilibrium equation is $U'(q)=kq=0$. The positive curvature $U''(q)=k>0$ identifies stable local behaviour. This is a close and useful example, but a general engineering objective need not be a potential energy and need not have a physical force interpretation.

## 3. Smoothness, convexity, and strong convexity

Three properties help us state reliable convergence results.

### Smoothness

A differentiable function is $L$-smooth if its gradient is Lipschitz continuous:

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\| \quad\text{for all }x,y.
$$

Here $\|\cdot\|$ is usually the Euclidean norm. Smoothness limits how rapidly the slope can change. If $f$ is twice differentiable, a sufficient condition is

$$
\|\nabla^2f(x)\|_2\leq L
$$

throughout the region of interest, where $\|\cdot\|_2$ is the spectral norm.

Smoothness gives the descent lemma:

$$
f(y)\leq f(x)+\nabla f(x)^T(y-x)+\frac{L}{2}\|y-x\|^2.
$$

The linear term predicts the local change and the quadratic term bounds the error in that prediction. This inequality is central to choosing a safe step size.

### Convexity

A function is convex on a convex domain if

$$
f(\theta x+(1-\theta)y)\leq \theta f(x)+(1-\theta)f(y)
$$

for all $x,y$ in the domain and $\theta\in[0,1]$. Geometrically, the graph lies below the straight line joining any two graph points. A differentiable equivalent is

$$
f(y)\geq f(x)+\nabla f(x)^T(y-x).
$$

Thus every tangent plane is a global under-estimator. For a twice differentiable function, convexity is equivalent to a positive-semidefinite Hessian everywhere on the domain.

For a differentiable convex function, every stationary point is a global minimiser. This is a major simplification: there are no non-global local minima. The minimiser need not be unique; a flat valley can contain many minimisers.

### Strong convexity

A function is $\mu$-strongly convex, with $\mu>0$, if

$$
f(y)\geq f(x)+\nabla f(x)^T(y-x)+\frac{\mu}{2}\|y-x\|^2
$$

for all $x,y$. For a twice differentiable function, $\nabla^2 f(x)\succeq \mu I$. Strong convexity means that the landscape curves upward in every direction by at least some positive amount. Consequently, there is a unique global minimiser.

A quadratic model illustrates all three ideas:

$$
f(x)=\frac12x^TAx-b^Tx,
$$

where $A$ is symmetric. If the eigenvalues of $A$ lie between $\mu$ and $L$, with $0<\mu\leq L$, then $f$ is $L$-smooth and $\mu$-strongly convex. The condition number $\kappa=L/\mu$ measures anisotropy. A large condition number produces a long, narrow valley: the steep direction and shallow direction have very different curvatures. This is analogous to a mechanical energy surface with very different stiffnesses in different coordinates.

## 4. The gradient descent algorithm

At a current iterate $x_k$, use the negative gradient direction:

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),
$$

where $\alpha_k>0$ is the step size, also called the learning rate. The algorithm is a numerical relaxation rule: evaluate the local slope, move downhill, and repeat.

A first-order Taylor approximation gives

$$
f(x_k-\alpha\nabla f(x_k))
\approx f(x_k)-\alpha\|\nabla f(x_k)\|^2.
$$

For a sufficiently small positive $alpha$, this predicts a decrease whenever the gradient is nonzero. The smoothness bound makes the statement rigorous. Substituting $y=x-\alpha\nabla f(x)$ into the descent lemma gives

$$
f(x-\alpha\nabla f(x))
\leq f(x)-\alpha\left(1-\frac{L\alpha}{2}\right)\|\nabla f(x)\|^2.
$$

Therefore, for $0<\alpha<2/L$, the objective decreases at every non-stationary step. A common conservative choice is $\alpha=1/L$. If $L$ is unknown, backtracking line search can start with a trial step and reduce it until a sufficient-decrease inequality is satisfied.

For a one-dimensional spring energy $f(q)=\tfrac12kq^2$, gradient descent becomes

$$
q_{k+1}=q_k-\alpha kq_k=(1-\alpha k)q_k.
$$

The iterates converge to zero when $|1-\alpha k|<1$, namely when $0<\alpha<2/k$. If the step is too large, the sequence can oscillate or diverge. This is a precise example of numerical relaxation, not a claim that every gradient method is a physical trajectory.

## 5. Convergence guarantees

Assume that $f$ is convex and $L$-smooth, has a minimiser $x^*$, and use a fixed step $\alpha=1/L$. Then gradient descent satisfies the function-value bound

$$
f(x_k)-f(x^*)\leq \frac{L\|x_0-x^*\|^2}{2k}.
$$

Thus the error is $O(1/k)$. To achieve an objective error at most $\varepsilon$, this bound suggests a number of iterations proportional to $L\|x_0-x^*\|^2/\varepsilon$.

If $f$ is also $\mu$-strongly convex, then the convergence is linear (geometric). With a suitable fixed step, for example $\alpha=1/L$, one obtains a bound of the form

$$
f(x_k)-f(x^*)\leq \left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).
$$

The exact best contraction factor depends on the chosen step and the particular theorem used, but the important point is geometric decay rather than $1/k$ decay. The ratio $L/\mu$ controls the speed. Large $\kappa$ means slow progress because the iterates tend to zig-zag across a narrow valley.

If the objective is smooth but nonconvex, a global minimum guarantee is generally unavailable. With a fixed sufficiently small step and a lower-bounded objective, one can often prove that the gradient becomes small on average. A typical result is

$$
\min_{0\leq k<N}\|\nabla f(x_k)\|^2
\leq \frac{C\,[f(x_0)-f_{\inf}]}{N}
$$

for an appropriate constant $C$ depending on the step and smoothness, where $f_{\inf}$ is a lower bound. This is a stationarity guarantee, not a guarantee of a global minimiser. In nonconvex engineering models, a stationary point may be a local minimum or a saddle.

## 6. Practical step-size selection and implementation

A step size is too small when progress is safe but needlessly slow. It is too large when the objective oscillates, increases persistently, or produces numerical overflow. A sensible workflow is:

1. Scale variables so that their typical magnitudes are comparable when possible.
2. Begin with a conservative step.
3. Monitor objective values and gradient norms.
4. Reduce the step if the objective repeatedly increases or iterates become unstable.
5. Stop using a clearly stated criterion, such as $\|\nabla f(x_k)\|\leq\text{tolerance}$ or a small relative objective change.

The following executable example minimises a two-variable quadratic. It records the path so that the narrow-valley behaviour can be plotted or inspected.

```python
import numpy as np

A = np.array([[10.0, 0.0], [0.0, 1.0]])
b = np.array([0.0, 0.0])

def f(x):
    return 0.5 * x @ A @ x - b @ x

def grad_f(x):
    return A @ x - b

x = np.array([8.0, 8.0])
alpha = 1.0 / np.linalg.eigvalsh(A).max()
path = [x.copy()]

for k in range(1000):
    g = grad_f(x)
    if np.linalg.norm(g) < 1e-8:
        break
    x = x - alpha * g
    path.append(x.copy())

print("iterations:", k + 1)
print("solution:", x)
print("objective:", f(x))
```

For a general differentiable function, the gradient may be derived analytically, approximated by finite differences, or supplied by automatic differentiation. Finite differences are useful for checking an analytic gradient, but they introduce truncation and round-off errors and can require many function evaluations.

        For a sufficiently small positive $\alpha$, this predicts a decrease whenever the gradient is nonzero. The smoothness bound makes the statement rigorous. Substituting $y=x-\alpha\nabla f(x)$ into the descent lemma gives

Plain gradient descent uses only the current gradient. Momentum adds a velocity-like state that accumulates recent directions:

$$
v_{k+1}=\beta v_k+\nabla f(x_k),
$$

$$
x_{k+1}=x_k-\alpha v_{k+1},
$$

where $0\leq\beta<1$. An equivalent convention changes signs and calls the state a velocity. The meaning is algorithmic; it should not be interpreted as a literal mechanical mass unless a specific discretisation and physical model justify that interpretation.

Momentum can reduce zig-zagging in directions where gradients alternate, while reinforcing consistent motion along a shallow valley. However, it can overshoot minima and may require tuning of both $\alpha$ and $\beta$. The objective is not guaranteed to decrease at every iteration under arbitrary momentum parameters.

Nesterov-style accelerated gradient evaluates the gradient at a look-ahead point. One common form is

$$
y_k=x_k+\beta_k(x_k-x_{k-1}),
$$

$$
x_{k+1}=y_k-\alpha\nabla f(y_k).
$$

For convex smooth functions, carefully selected momentum parameters give an $O(1/k^2)$ function-value rate, improving on the $O(1/k)$ rate of basic gradient descent. These guarantees depend on the assumptions and parameter schedule; acceleration is not universally faster on noisy or badly specified problems.

## 8. Stochastic gradient methods

Many engineering objectives are sums or expectations over data, samples, load cases, or simulations:

$$
f(x)=\frac1m\sum_{i=1}^m f_i(x).
$$

The full gradient costs $m$ component-gradient evaluations. A stochastic method chooses an index $i_k$ or a minibatch and uses

$$
x_{k+1}=x_k-\alpha_k\nabla f_{i_k}(x_k).
$$

If the sample is selected uniformly, then under suitable conditions the estimator is unbiased:

$$
\mathbb{E}[\nabla f_{i_k}(x)]=\nabla f(x).
$$

The individual updates are noisy, so the objective may rise on some iterations and the iterates may fluctuate near a solution. A constant step often reaches a neighbourhood of the optimum rather than converging exactly. Decreasing step sizes can support convergence, commonly with conditions such as

$$
\sum_{k=0}^{\infty}\alpha_k=\infty,
\qquad
\sum_{k=0}^{\infty}\alpha_k^2<\infty.
$$

A schedule such as $\alpha_k=\alpha_0/(k+1)$ satisfies these two conditions. In practice, minibatches reduce variance, and a stopping rule should account for noise rather than expecting a steadily decreasing objective.

```python
import numpy as np

rng = np.random.default_rng(4)
X = rng.normal(size=(1000, 2))
true_w = np.array([2.0, -3.0])
y = X @ true_w + 0.2 * rng.normal(size=1000)

w = np.zeros(2)
batch_size = 32
alpha0 = 0.2

for epoch in range(50):
    order = rng.permutation(len(X))
    alpha = alpha0 / (1.0 + 0.05 * epoch)
    for start in range(0, len(X), batch_size):
        ids = order[start:start + batch_size]
        residual = X[ids] @ w - y[ids]
        gradient = X[ids].T @ residual / len(ids)
        w -= alpha * gradient

print("estimated parameters:", w)
```

The least-squares example also shows why scaling matters. If one design variable has a much larger scale than another, the objective can become poorly conditioned, and stochastic or deterministic methods may need smaller steps.

## 9. Second-order optimisation

First-order methods use gradient information. Second-order methods also use curvature. Near a point $x$, a second-order Taylor model is

$$
f(x+p)\approx f(x)+\nabla f(x)^Tp+\frac12p^T\nabla^2f(x)p.
$$

Setting the model gradient to zero gives the Newton step

$$
\nabla^2f(x_k)p_k=-\nabla f(x_k),
\qquad
x_{k+1}=x_k+p_k.
$$

For a quadratic with an exact, nonsingular Hessian, Newton's method reaches the minimiser in one step from any starting point. For a general function, local quadratic convergence is possible when the function is sufficiently smooth, the Hessian at the solution is nonsingular, and the starting point is sufficiently close. Far from a solution, the Hessian may be indefinite, the step may point toward a maximum or saddle, and a full step may increase the objective.

Damped Newton methods use $x_{k+1}=x_k+\alpha_kp_k$ with line search. Trust-region methods instead restrict the model step to a region where the quadratic approximation is considered credible. If the Hessian is expensive to form or solve with, quasi-Newton methods such as BFGS build an approximation from gradients. Limited-memory variants are useful for large problems.

There is a direct mechanical connection when the Hessian represents a stiffness matrix: curvature tells us how strongly the objective resists displacement in each direction. But an optimisation Hessian is a matrix of second derivatives of the chosen objective, not automatically the physical stiffness matrix. The correspondence must be checked for the particular model.

## 10. Choosing a method and interpreting results

Use basic gradient descent when gradients are available, the problem is moderate in scale, and a simple robust baseline is valuable. Use momentum or acceleration when the objective is smooth and deterministic and the basic method is slowed by conditioning. Use stochastic gradients when full gradients are costly and the objective naturally decomposes into samples or cases. Consider Newton or quasi-Newton methods when curvature information can substantially reduce iteration count and the computational cost is justified.

Always state what has actually been established. A small gradient norm means approximate stationarity. It does not prove global optimality for a nonconvex objective. Convexity makes stationarity global, while strong convexity additionally gives uniqueness. A convergence theorem applies only under its assumptions: for example, smoothness, a lower bound, convexity, bounded variance, or an appropriate step-size schedule.

In a mechanical application, compare the optimisation result with engineering checks: equilibrium residuals, energy or compliance values, boundary conditions, units, and sensitivity to initialisation and tolerances. Numerical relaxation can provide insight into equilibrium, but it is not a substitute for validating the model or enforcing constraints. When constraints are essential, the unconstrained update must be replaced or extended by methods such as projection, penalty formulations, feasible parameterisations, or constrained optimisation algorithms.

The central pattern is simple:

$$
\text{measure the slope}\;\longrightarrow\;\text{choose a controlled step}\;\longrightarrow\;\text{check assumptions and progress}.
$$

Gradient descent is powerful because this pattern requires only first derivatives. Its reliability comes not from the downhill picture alone, but from precise properties—smoothness, convexity, curvature, and noise assumptions—that connect an update rule to a mathematical convergence guarantee.
