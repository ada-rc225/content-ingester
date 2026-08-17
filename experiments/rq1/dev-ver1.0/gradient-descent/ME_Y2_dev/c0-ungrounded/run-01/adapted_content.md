# Gradient Descent and Optimisation for Mechanical Engineers

## 1. From equilibrium to optimisation

A useful mechanical starting point is equilibrium. Imagine a mass moving in a conservative force field. If its potential energy is $U(q)$, where $q$ collects the coordinates describing the configuration, then the conservative force is

$$
F(q)=-\nabla U(q).
$$

An equilibrium configuration $q^*$ satisfies $F(q^*)=0$, or equivalently

$$
\nabla U(q^*)=0.
$$

This suggests a numerical relaxation procedure: start from an admissible configuration, compute the force, and move a short distance in the force direction. Since the force is the negative gradient of potential energy, this becomes

$$
q_{k+1}=q_k-\alpha_k\nabla U(q_k),
$$

where $lpha_k>0$ is a step size. This is the gradient descent method.

The mechanical picture is valuable because it gives intuition for the sign: a positive gradient points towards increasing energy, so subtracting the gradient moves downhill. However, the optimisation problem is more general than a physical potential-energy problem. The function being minimised might be a least-squares error, a design objective, or a numerical residual measure; it need not be a physical energy, and the coordinates need not be positions. We therefore use the mechanical picture as an entry point, then state the mathematics independently.

The general unconstrained optimisation problem is

$$
\min_{x\in\mathbb{R}^n} f(x),
$$

where $f:\mathbb{R}^n\to\mathbb{R}$ is an objective function and $x$ is a vector of design or state variables. “Unconstrained” means that every $x\in\mathbb{R}^n$ is allowed. In an engineering model, constraints such as a maximum displacement or a required mass would require a different formulation, for example constrained or projected optimisation.

A global minimiser $x^*$ satisfies

$$
 f(x^*)\leq f(x) \quad\text{for every }x\in\mathbb{R}^n.
$$

A local minimiser only needs to have this property in some neighbourhood of $x^*$. Algorithms can converge to a local minimiser, a saddle point, or sometimes fail to converge, depending on the objective and the assumptions made.

## 2. Optimality conditions

Suppose $f$ is differentiable and $x^*$ is an interior local minimiser. The first-order necessary condition is

$$
\nabla f(x^*)=0.
$$

Such a point is called stationary. The condition follows from considering any direction $d$. The one-dimensional function $\phi(t)=f(x^*+td)$ must have a minimum at $t=0$, so $\phi'(0)=\nabla f(x^*)^Td=0$ for every $d$. Hence the gradient is zero.

The first-order condition is necessary, not sufficient. For example, $f(x)=x^3$ has $f'(0)=0$, but $x=0$ is neither a minimum nor a maximum. A stationary point can also be a saddle point. The multivariable second-order necessary condition adds information: if $f$ is twice differentiable at a local minimiser, then

$$
\nabla^2 f(x^*)\succeq 0,
$$

meaning that $d^T\nabla^2f(x^*)d\geq0$ for every direction $d$. The Hessian must be positive semidefinite. If instead the Hessian has a negative curvature direction, the point cannot be a local minimum.

A sufficient second-order condition is stronger. If

$$
\nabla f(x^*)=0
\quad\text{and}\quad
\nabla^2f(x^*)\succ0,
$$

then $x^*$ is a strict local minimiser. Here positive definite means $d^T\nabla^2f(x^*)d>0$ for every nonzero $d$. These conditions are local: they do not by themselves establish that the point is globally best.

For a convex function, the situation improves. A differentiable function $f$ is convex on a convex domain if

$$
 f(\theta x+(1-\theta)y)\leq \theta f(x)+(1-\theta)f(y)
$$

for all $x,y$ in the domain and $\theta\in[0,1]$. Geometrically, the graph lies below the straight chord joining any two points. A differentiable convex function also satisfies the supporting-hyperplane inequality

$$
 f(y)\geq f(x)+\nabla f(x)^T(y-x).
$$

Therefore, if $\nabla f(x^*)=0$, then $f(y)\geq f(x^*)$ for every $y$: every stationary point is a global minimiser. Convexity does not necessarily give uniqueness. A flat valley may contain many global minimisers.

## 3. Smoothness, convexity, and conditioning

Gradient descent depends on how rapidly the gradient can change. A differentiable function is $L$-smooth if

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|
$$

for all $x,y$. For a twice-differentiable function, a sufficient condition is that the Hessian eigenvalues are at most $L$ everywhere. Smoothness prevents abrupt changes in slope and permits a quantitative descent bound:

$$
 f(y)\leq f(x)+\nabla f(x)^T(y-x)+\frac{L}{2}\|y-x\|^2.
$$

This is sometimes called the descent lemma.

A function is $strongly convex with parameter $\mu>0$ if

$$
 f(y)\geq f(x)+\nabla f(x)^T(y-x)+\frac{\mu}{2}\|y-x\|^2
$$

for all $x,y$. For a twice-differentiable function, the corresponding Hessian condition is

$$
\nabla^2f(x)\succeq \mu I.
$$

Strong convexity implies a unique minimiser, provided a minimiser exists. If $f$ is both $L$-smooth and $\mu$-strongly convex, then $0<\mu\leq L$. The condition number

$$
\kappa=\frac{L}{\mu}
$$

measures the difficulty of the problem for first-order methods. A large $\kappa$ corresponds to a narrow, elongated valley. In mechanical terms, this can resemble a system with very different stiffnesses in different modes: relaxation progresses quickly in a stiff direction but slowly in a compliant direction. The analogy is not universal, but the mathematical issue is anisotropic curvature.

A standard example is the quadratic

$$
 f(x)=\frac12x^TAx-b^Tx+c,
$$

where $A$ is symmetric positive definite. Then $\nabla f(x)=Ax-b$ and $\nabla^2f(x)=A$. The eigenvalues of $A$ give the curvature in principal directions. If $A$ has smallest eigenvalue $\mu$ and largest eigenvalue $L$, the quadratic is $\mu$-strongly convex and $L$-smooth.

## 4. The gradient descent algorithm

The gradient descent update is

$$
 x_{k+1}=x_k-\alpha_k\nabla f(x_k).
$$

The negative gradient is the direction of steepest local decrease in the Euclidean norm. The step size controls how far to travel. It is not merely a numerical detail: an unsuitable step can make the objective increase or cause divergence.

For constant step size $\alpha$, apply the descent lemma with $y=x-\alpha\nabla f(x)$:

$$
 f(x-\alpha\nabla f(x))
 \leq f(x)-\alpha\left(1-\frac{L\alpha}{2}\right)\|\nabla f(x)\|^2.
$$

Thus, for $0<\alpha<2/L$, the objective decreases at every nonstationary step under $L$-smoothness. The commonly used conservative choice $\alpha\leq1/L$ gives a particularly simple guarantee. In practice, $L$ may not be known. Options include estimating it, using backtracking line search, or trying a schedule of step sizes.

A backtracking line search starts with a trial step and reduces it, often by a factor such as $\beta=0.5$, until the Armijo condition holds:

$$
 f(x-\alpha g)\leq f(x)-c\alpha\|g\|^2,
 \qquad g=\nabla f(x),
$$

where $c$ is a small positive constant, commonly less than $1/2$. This uses function evaluations as well as gradients.

A basic implementation for a differentiable function is:

```python
import numpy as np


def gradient_descent(grad, f, x0, step=0.1, max_iter=10_000,
                     grad_tol=1e-8):
    x = np.asarray(x0, dtype=float).copy()
    values = [f(x)]

    for _ in range(max_iter):
        g = np.asarray(grad(x), dtype=float)
        if np.linalg.norm(g) <= grad_tol:
            break
        x = x - step * g
        values.append(f(x))

    return x, np.asarray(values)


def objective(x):
    # A quadratic with different curvatures in two directions.
    return 0.5 * (10.0 * x[0]**2 + x[1]**2)


def gradient(x):
    return np.array([10.0 * x[0], x[1]])

x_star, history = gradient_descent(gradient, objective, [4.0, 3.0], step=0.1)
print(x_star, history[-1])
```

The largest curvature here is $L=10$. A step of $0.1=1/L$ is at the edge of the simple conservative bound and is stable for this quadratic, although a smaller step is more cautious. The code stops when the gradient norm is small, not merely when consecutive iterates are close. Those stopping tests measure different things and can behave differently in ill-conditioned problems.

## 5. Convergence guarantees

Assume that $f$ is convex and $L$-smooth, and let $x^*$ be a minimiser. With a suitable constant step, such as $\alpha=1/L$, gradient descent has the function-value guarantee

$$
 f(x_k)-f(x^*)\leq \frac{L\|x_0-x^*\|^2}{2k}
$$

for $k\geq1$. This is an $O(1/k)$ rate. It describes the worst-case decrease in objective error; it does not say that every practical problem visibly follows an exact inverse-linear curve.

If $f$ is additionally $\mu$-strongly convex and $L$-smooth, gradient descent converges geometrically. With $0<\alpha\leq1/L$,

$$
 f(x_k)-f(x^*)\leq (1-\alpha\mu)^k\bigl(f(x_0)-f(x^*)\bigr).
$$

Using $\alpha=1/L$ gives a factor $1-\mu/L=1-1/\kappa$. The number of iterations required for a prescribed accuracy therefore grows with the condition number. This is why scaling variables, nondimensionalising a model, and choosing sensible units can materially improve numerical optimisation.

These theorems require assumptions. Smoothness is not the same as differentiability at each point; it is a global Lipschitz-gradient property on the region being considered. Convexity excludes many nonlinear engineering objectives. Strong convexity excludes flat directions and nonunique minimisers. If these assumptions fail, gradient descent may still work, but the stated rates cannot automatically be applied.

For a general smooth nonconvex function, a typical guarantee is about stationarity rather than global optimality. If $f$ is bounded below and $L$-smooth, and $\alpha\leq1/L$, summing the descent inequality gives

$$
\min_{0\leq k<K}\|\nabla f(x_k)\|^2
\leq \frac{2\bigl(f(x_0)-f_{\inf}\bigr)}{\alpha K},
$$

where $f_{\inf}$ is a lower bound on $f$. This says that at least one iterate has a small gradient after sufficiently many steps. It does not establish closeness to a global minimiser; a small gradient can occur at a saddle or a poor local minimum.

## 6. Momentum and acceleration

In a narrow quadratic valley, ordinary gradient descent can zig-zag across the steep direction while making slow progress along the shallow direction. Momentum adds an accumulated velocity. One common heavy-ball form is

$$
 v_{k+1}=\beta v_k-\alpha\nabla f(x_k),
\qquad
 x_{k+1}=x_k+v_{k+1},
$$

with $0\leq\beta<1$. The previous motion influences the next motion, much as inertia influences a mechanical relaxation process. The correspondence is only an intuition: the algorithmic velocity is not necessarily a physical velocity, and poorly chosen momentum can overshoot or destabilise the iteration.

Another widely used form, often called Nesterov accelerated gradient for convex problems, evaluates the gradient at a look-ahead point:

$$
 y_k=x_k+\beta_k(x_k-x_{k-1}),
 \qquad
 x_{k+1}=y_k-\alpha\nabla f(y_k).
$$

For suitable schedules and assumptions, acceleration improves the convex smooth rate from $O(1/k)$ to $O(1/k^2)$ in function value. For strongly convex smooth functions, tuned accelerated methods achieve a dependence on approximately $\sqrt{\kappa}$ rather than $\kappa$. The exact constants and schedules matter, and acceleration is not a universal improvement for noisy or nonconvex objectives.

The practical lesson is to treat momentum parameters as part of the algorithm, not as harmless decoration. Monitor the objective and gradients. If iterates oscillate, reduce the step size or momentum. In applications with noisy gradients, momentum can smooth fluctuations, but it can also carry noise forward.

## 7. Stochastic gradient methods

Suppose the objective is an average over many measurements or samples:

$$
 f(x)=\frac1N\sum_{i=1}^N f_i(x).
$$

The full gradient costs $N$ component-gradient evaluations. A stochastic gradient method selects an index $i_k$ and uses

$$
 x_{k+1}=x_k-\alpha_k\nabla f_{i_k}(x_k).
$$

If $i_k$ is sampled uniformly, then

$$
\mathbb{E}[\nabla f_{i_k}(x)]=\nabla f(x),
$$

so the estimator is unbiased, although it has variance. A mini-batch replaces one sample by an average of $B$ samples, usually reducing variance at increased computational cost.

Unlike deterministic descent, a stochastic objective value can increase on an individual step. Under standard assumptions such as unbiased gradients, bounded variance, a lower-bounded objective, and diminishing step sizes satisfying

$$
\sum_{k=0}^{\infty}\alpha_k=\infty,
\qquad
\sum_{k=0}^{\infty}\alpha_k^2<\infty,
$$

one can obtain convergence results for suitable convex problems. A common schedule is $\alpha_k=a/(k+1)^p$ with $1/2<p\leq1$, although practical schedules are often piecewise constant or decayed according to validation behaviour. With a fixed nonzero step size, stochastic methods generally approach a neighbourhood of the optimum rather than settling exactly, because gradient noise remains.

For mechanical engineering, stochasticity can represent varying load cases, sampled measurements, uncertain material data, or batches of simulation conditions. The update is mathematically justified only when the sampling and gradient assumptions are appropriate; randomising a deterministic calculation does not automatically make it a valid stochastic-gradient problem.

```python

def stochastic_gradient_descent(x0, gradients, step0=0.05, epochs=20):
    """Minimise an average of component objectives.

    gradients[i](x) returns grad f_i(x). One epoch visits every component
    once in a freshly shuffled order.
    """
    rng = np.random.default_rng(7)
    x = np.asarray(x0, dtype=float).copy()
    trajectory = [x.copy()]

    for epoch in range(epochs):
        order = rng.permutation(len(gradients))
        step = step0 / (1.0 + 0.1 * epoch)
        for i in order:
            x -= step * gradients[i](x)
        trajectory.append(x.copy())

    return x, np.asarray(trajectory)
```

## 8. A short introduction to second-order optimisation

Gradient methods use slope but not curvature. Second-order methods use the Hessian. Newton’s method approximates $f$ near $x_k$ by a quadratic:

$$
 f(x_k+p)\approx f(x_k)+\nabla f(x_k)^Tp+
 \frac12p^T\nabla^2f(x_k)p.
$$

Setting the approximate gradient with respect to $p$ to zero gives the Newton step

$$
\nabla^2f(x_k)p_k=-\nabla f(x_k),
\qquad
x_{k+1}=x_k+p_k.
$$

For a quadratic with positive-definite Hessian, Newton’s method reaches the minimiser in one exact step, ignoring numerical round-off. Near a sufficiently regular local minimiser with nonsingular Hessian, Newton’s method has quadratic local convergence: once close enough, the number of correct digits can grow rapidly.

The costs can be substantial. Storing a dense $n\times n$ Hessian requires $O(n^2)$ memory, and solving the linear system typically costs $O(n^3)$ for a dense factorisation. The Hessian may also be indefinite away from a minimum, so the Newton direction need not be a descent direction. Practical variants use a line search, trust region, regularisation, or quasi-Newton approximations such as BFGS and L-BFGS.

In mechanics, a Hessian can resemble a tangent stiffness matrix, but the equivalence depends on the model and variables. A physical stiffness matrix may have constraints, symmetries, or units that do not match an arbitrary optimisation Hessian. The canonical optimisation statement remains the local quadratic model and its linear system.

A useful hybrid strategy is to begin with a robust first-order method, then use curvature information when near a well-behaved solution. For large problems, gradient methods are often preferred because gradients can be computed efficiently and Hessian-vector products can be used without explicitly forming the Hessian.

## 9. A practical workflow

1. **Define the objective and variables.** State what is being minimised, the units of each variable, and whether the problem is truly unconstrained.
2. **Check derivatives.** Compare an analytical gradient with finite differences on a small test problem. A derivative error can look like poor optimisation.
3. **Inspect scaling.** Rescale variables so that typical changes have comparable numerical magnitudes where possible.
4. **Choose a method.** Use gradient descent for a simple baseline, line search when a reliable scale is unknown, stochastic methods for large averages, and second-order methods when curvature is affordable.
5. **Monitor meaningful diagnostics.** Record objective values, gradient norms, step norms, and possibly constraint violations if constraints are later introduced.
6. **Test sensitivity.** Try different initial points and step sizes. Agreement across starts is evidence, not a proof, of global behaviour.
7. **Interpret the result.** A numerical stationary point must still be checked against physical feasibility, model validity, and engineering requirements.

The central connection to equilibrium is therefore precise in one important case: minimising a differentiable potential energy seeks a configuration where its gradient, and hence conservative force, vanishes. The broader optimisation theory applies beyond that setting. Gradient descent is a controlled iteration driven by the mathematical gradient; smoothness determines safe step scales, convexity determines what stationarity means, strong convexity determines uniqueness and geometric rates, and curvature-aware methods can improve performance when their additional cost is justified.