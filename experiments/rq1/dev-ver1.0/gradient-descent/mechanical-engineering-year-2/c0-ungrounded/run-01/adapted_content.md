# Gradient Descent and Optimisation: Relaxing a Mechanical System to Equilibrium

## Why optimisation appears in mechanics

A mechanical engineer often asks for a configuration that is stable, efficient, or as light as possible. A stretched cable settles into a shape, a linkage finds a position in which forces balance, and a component can be designed to minimise mass while meeting performance requirements. These questions can be expressed mathematically by choosing variables, defining an objective, and finding a point where the objective is as small as possible.

Let $x\in\mathbb{R}^n$ collect the design or state variables. An objective function $f(x)$ assigns a scalar value to each choice. The basic unconstrained optimisation problem is

$$
\min_{x\in\mathbb{R}^n} f(x).
$$

For a conservative mechanical system, potential energy is a natural example of an objective. A configuration with lower potential energy is often preferred, and equilibrium configurations occur where small admissible displacements do not produce a first-order change in energy. Numerical relaxation methods imitate the useful idea of moving downhill until no further downhill direction is apparent.

This analogy has a boundary: an optimisation objective need not be a physical energy, and algorithmic iterations are not generally physical time evolution. For example, a least-squares fitting error or manufacturing cost may have no mechanical interpretation. We use potential energy as an entry point, not as a claim about all objectives.

The lesson develops the mathematical conditions behind a minimum, the geometry that controls algorithm speed, and practical algorithms that can be implemented in Python.

## Equilibrium, stationarity, and optimality

### First-order conditions

Suppose $f$ is differentiable and $x^*$ is an interior local minimiser. If we move a small distance $t$ in any direction $d$, the function

$$
\phi(t)=f(x^*+td)
$$

has a local minimum at $t=0$. Therefore, $[1m\phi'(0)=\nabla f(x^*)^T d=0$ for every direction $d$. The only vector orthogonal to every direction is the zero vector, so

$$
\nabla f(x^*)=0.
$$

This is the first-order necessary condition. A point satisfying it is called stationary. In mechanics, a zero gradient of potential energy corresponds to zero resultant generalised force, because force is related to the negative gradient of potential energy. However, stationarity alone does not tell us whether the point is stable, unstable, or a saddle point.

For example, $f(x)=x^3$ has a stationary point at $x=0$, but no local minimum there. The graph passes through the point rather than turning upward on both sides. Also, $f(x,y)=x^2-y^2$ has zero gradient at the origin, but it decreases along the $y$ direction and increases along the $x$ direction. The origin is a saddle.

### Second-order conditions

If $f$ is twice differentiable, its Hessian matrix is

$$
\nabla^2 f(x)=\begin{bmatrix}
\frac{\partial^2 f}{\partial x_1^2} & \cdots & \frac{\partial^2 f}{\partial x_1\partial x_n}\\
\vdots & \ddots & \vdots\\
\frac{\partial^2 f}{\partial x_n\partial x_1} & \cdots & \frac{\partial^2 f}{\partial x_n^2}
\end{bmatrix}.
$$

Near a stationary point, Taylor expansion gives

$$
f(x^*+d)\approx f(x^*)+\nabla f(x^*)^Td+\frac12d^T\nabla^2f(x^*)d.
$$

The linear term vanishes at a stationary point. If the Hessian is positive definite, meaning $d^T\nabla^2 f(x^*)d>0$ for every nonzero $d$, then $x^*$ is a strict local minimum. If the Hessian is negative definite, it is a strict local maximum. If the Hessian has both positive and negative curvature directions, the point is a saddle.

Positive semidefiniteness gives only a necessary condition for a local minimum in the usual smooth setting: $d^T\nabla^2 f(x^*)d\geq 0$. It may still be a flat minimum, or higher-order terms may determine the result. For instance, $f(x)=x^4$ has Hessian zero at its minimum.

A positive-definite Hessian test is local. It does not by itself guarantee that the function has only one minimum elsewhere. Global conclusions require additional structure, especially convexity.

## Smoothness, convexity, and the shape of the problem

### Smoothness controls gradient change

A differentiable function is $L$-smooth if its gradient is Lipschitz continuous:

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|
$$

for all relevant $x$ and $y$. The constant $L$ bounds how quickly the slope can change. For a twice-differentiable function, a sufficient condition is that the largest Hessian eigenvalue is at most $L$ throughout the region of interest.

Smoothness gives the descent lemma:

$$
f(y)\leq f(x)+\nabla f(x)^T(y-x)+\frac{L}{2}\|y-x\|^2.
$$

This inequality is useful because it turns a local gradient into a reliable upper model. If $y=x-\alpha\nabla f(x)$, then

$$
f(y)\leq f(x)-\alpha\left(1-\frac{L\alpha}{2}\right)\|\nabla f(x)\|^2.
$$

Thus any $0<\alpha<2/L$ guarantees a decrease under this bound, with the commonly used conservative choice $\alpha\leq 1/L$.

### Convexity rules out misleading valleys

A function is convex on a convex domain if

$$
f(\theta x+(1-\theta)y)\leq \theta f(x)+(1-\theta)f(y)
$$

for $0\leq\theta\leq1$. Geometrically, the graph lies below the straight chord between two points. For a differentiable convex function, every tangent plane is a global under-estimator:

$$
f(y)\geq f(x)+\nabla f(x)^T(y-x).
$$

Consequently, if $\nabla f(x^*)=0$, then $f(y)\geq f(x^*)$ for every $y$, so every stationary point is a global minimiser. Convexity can therefore upgrade a first-order condition from local information to a global statement.

For twice-differentiable functions, convexity is equivalent on a suitable convex domain to $\nabla^2 f(x)\succeq0$, meaning the Hessian is positive semidefinite everywhere. Convex functions can have multiple minimisers, but they cannot have a strict local minimum that is not global.

### Strong convexity gives curvature and uniqueness

A function is $\mu$-strongly convex if $\mu>0$ and

$$
f(y)\geq f(x)+\nabla f(x)^T(y-x)+\frac{\mu}{2}\|y-x\|^2.
$$

For a twice-differentiable function, this corresponds to

$$
\nabla^2 f(x)\succeq \mu I.
$$

Strong convexity means there is curvature in every direction. It guarantees a unique minimiser $x^*$ and gives a useful relationship between gradient and distance to the solution. If $f$ is also $L$-smooth, then $0<\mu\leq L$.

The ratio

$$
\kappa=\frac{L}{\mu}
$$

is the condition number. A small $[1m\kappa$ means the curvature is reasonably balanced. A large condition number describes a long, narrow valley: progress is possible, but a method using the raw gradient may zigzag across the narrow direction while making slow progress along the long direction. Rescaling variables, changing units, or using a preconditioner can improve conditioning.

## Gradient descent as numerical relaxation

### The update rule

Gradient descent applies the iteration

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k).
$$

The gradient points in the direction of greatest local increase, so its negative is the steepest local descent direction in the Euclidean norm. The step size $\alpha_k$ controls how far we move. Starting from an initial guess, we evaluate the gradient, update the variables, and repeat until a stopping criterion is met.

For a quadratic objective

$$
f(x)=\frac12x^TAx-b^Tx+c,
$$

with symmetric positive-definite $A$, the gradient is $Ax-b$ and the minimiser solves $Ax^*=b$. The iteration becomes

$$
x_{k+1}=x_k-\alpha(Ax_k-b).
$$

If the eigenvalues of $A$ are positive, each eigenvector direction behaves like a one-dimensional recurrence with factor $1-\alpha\lambda$. Convergence requires $|1-\alpha\lambda|<1$ for all eigenvalues, hence $0<\alpha<2/\lambda_{\max}$. The best fixed step for this quadratic is

$$
\alpha^*=\frac{2}{\lambda_{\min}+\lambda_{\max}}.
$$

In practice, $\lambda_{\max}$ may not be known, and the objective may not be globally quadratic. Useful alternatives include backtracking line search, a schedule chosen from validation experiments, or a conservative estimate of $L$.

### Choosing and adapting the step size

A fixed step that is too small is safe but slow. A step that is too large can overshoot, produce oscillation, or diverge. Backtracking starts with a trial value and repeatedly multiplies it by a factor such as $\beta=0.5$ until a sufficient-decrease condition holds:

$$
f(x-\alpha g)\leq f(x)-c\alpha\|g\|^2,
$$

where $g=\nabla f(x)$ and $c$ is a small positive constant.

Stopping should reflect the purpose of the calculation. Common tests are $\|\nabla f(x_k)\|\leq\varepsilon_g$, a small step $\|x_{k+1}-x_k\|\leq\varepsilon_x(1+\|x_k\|)$, or a small relative objective change. A maximum iteration count is also needed. A small step does not always mean success: a method may be stuck near a saddle, limited by numerical precision, or using a poorly scaled objective.

## What convergence looks like

### Smooth convex objectives

For an $L$-smooth convex function, gradient descent with $0<\alpha\leq1/L$ satisfies a sublinear objective bound of the form

$$
f(x_k)-f(x^*)\leq\frac{\|x_0-x^*\|^2}{2\alpha k}.
$$

The error decreases like $O(1/k)$, so reducing the error by another factor of ten can require substantially more iterations. This is a worst-case guarantee, not a prediction that every iteration has exactly the same improvement.

### Smooth strongly convex objectives

If the function is also $\mu$-strongly convex, gradient descent has geometric, or linear, convergence. With $\alpha=1/L$, one standard bound is

$$
f(x_k)-f(x^*)\leq\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).
$$

The factor $1-1/\kappa$ explains why conditioning matters. When $\kappa$ is large, the factor is close to one. An improved fixed step for quadratic-like problems can yield a factor related to $(\kappa-1)/(\kappa+1)$, but it still depends on the condition number.

These results assume the stated smoothness and convexity conditions and an appropriate step size. Nonconvex engineering models may have several local minima, saddle points, discontinuities, or constraints. In those settings, convergence may mean reaching a stationary point rather than proving global optimality.

## Momentum and acceleration

### Momentum

Momentum accumulates a velocity-like search direction:

$$
v_{k+1}=\gamma v_k+\nabla f(x_k),\qquad x_{k+1}=x_k-\alpha v_{k+1},
$$

where $0\leq\gamma<1$. In a long valley, successive gradients often point in a consistent direction along the valley but alternate across its narrow width. The accumulated direction can preserve useful motion while damping some zigzagging.

Momentum introduces another dynamical parameter and can overshoot if $\alpha$ or $\gamma$ is too large. Monitoring the objective and gradient remains important. A related formulation uses a displacement or exponentially weighted gradient; the exact indexing conventions differ, so implementation should be checked against the equations rather than copied by name alone.

### Nesterov acceleration

Nesterov's method evaluates the gradient at a look-ahead point. One common form is

$$
y_k=x_k+\beta_k(x_k-x_{k-1}),\qquad x_{k+1}=y_k-\alpha\nabla f(y_k).
$$

For suitable parameter choices, accelerated methods improve the worst-case rate for smooth convex problems from $O(1/k)$ to $O(1/k^2)$ in objective error. For smooth strongly convex problems, carefully tuned acceleration gives rates depending on approximately $1-1/\sqrt{\kappa}$ rather than $1-1/\kappa$.

The practical lesson is not that acceleration always wins. It can be sensitive to noise, poor curvature estimates, and stopping rules. In a mechanical computation, first establish that plain gradient descent is correctly scaled and converging before adding momentum.

## Stochastic and adaptive methods

### Stochastic gradients

Suppose the objective is an average of many contributions,

$$
f(x)=\frac1N\sum_{i=1}^N f_i(x).
$$

A stochastic gradient method samples one contribution or a mini-batch $B$ and uses

$$
g_k=\frac1{|B|}\sum_{i\in B}\nabla f_i(x_k),\qquad x_{k+1}=x_k-\alpha_k g_k.
$$

Each update is cheaper but noisy. The noise can help avoid some unhelpful stationary regions, but the objective may fluctuate rather than decrease at every step. Batch size trades computational cost against variance. For a fixed step, stochastic methods often approach a neighbourhood of the solution; decreasing step sizes are used when high-accuracy convergence is required.

The gradient estimate must be unbiased or at least sufficiently controlled for standard guarantees. Random seeds, data order, and batch construction affect reproducibility. In a finite-element or simulation setting, stochasticity might come from sampling load cases, geometries, or measurements rather than from a naturally labelled dataset.

### Adaptive per-coordinate steps

Adaptive methods maintain statistics of past gradients. AdaGrad uses

$$
r_{k}=r_{k-1}+g_k\odot g_k,
$$

and updates coordinates approximately as

$$
x_{k+1}=x_k-\frac{\alpha}{\sqrt{r_k}+\epsilon}\odot g_k.
$$

Coordinates with consistently large gradients receive smaller subsequent steps. RMSProp replaces the cumulative statistic by an exponential moving average, while Adam combines an exponential average of gradients with one of squared gradients and applies bias corrections.

These methods can be convenient when variables have different scales or stochastic gradients are present. They add state, hyperparameters, and possible failure modes. Adaptive scaling is not a substitute for checking units and physical meaning. For a small, well-conditioned deterministic engineering problem, a line-searched gradient method may be easier to interpret and just as effective.

## Newton and quasi-Newton methods

### Newton's local curvature model

Gradient descent uses a first-order model. Newton's method uses the quadratic approximation

$$
f(x+p)\approx f(x)+\nabla f(x)^Tp+\frac12p^T\nabla^2f(x)p.
$$

Setting the derivative with respect to $p$ to zero gives

$$
\nabla^2f(x_k)p_k=-\nabla f(x_k),\qquad x_{k+1}=x_k+p_k.
$$

Near a well-behaved minimiser with a nonsingular positive-definite Hessian, Newton's method can converge quadratically: once sufficiently close, the number of correct digits can grow rapidly. It is not generally wise to explicitly form the inverse Hessian. Solve the linear system instead.

The Hessian may be expensive to assemble, expensive to factor, indefinite away from a minimum, or singular. A common safeguard is a damped step $x_{k+1}=x_k+\alpha p_k$ with a line search. If the Hessian is indefinite, modifications such as adding a multiple of the identity can produce a descent direction.

### Quasi-Newton updates

Quasi-Newton methods approximate inverse curvature using gradients and displacements. BFGS maintains an approximation $H_k$ to the inverse Hessian and uses $p_k=-H_k\nabla f(x_k)$. With $s_k=x_{k+1}-x_k$ and $y_k=\nabla f(x_{k+1})-\nabla f(x_k)$, the update uses the curvature information in the pair $(s_k,y_k)$. Under suitable conditions, BFGS preserves positive definiteness and often performs well with a line search.

L-BFGS stores only a limited number of recent pairs, making it suitable for high-dimensional problems. It is often a strong default for smooth deterministic optimisation when gradients are available but a full Hessian is impractical. It is less naturally suited to very noisy stochastic gradients unless modified carefully.

## Translating equations into Python

A reliable implementation separates the objective from its gradient and makes the state update explicit. The following example minimises a two-variable quadratic. The matrix is positive definite, so the problem has a unique solution.

```python
import numpy as np

A = np.array([[4.0, 0.0], [0.0, 1.0]])
b = np.array([8.0, 2.0])


def objective(x):
    return 0.5 * x @ A @ x - b @ x


def gradient(x):
    return A @ x - b

x = np.array([0.0, 0.0])
alpha = 0.2
history = []

for k in range(200):
    g = gradient(x)
    history.append(objective(x))
    if np.linalg.norm(g) < 1e-8:
        break
    x = x - alpha * g

print("solution:", x)
print("objective:", objective(x))
print("iterations:", k + 1)
```

The update follows the mathematical rule directly: calculate $g$, test a stopping condition, then replace $x$ by $x-\alpha g$. The exact minimiser satisfies $Ax=b$, giving $x^*=(2,2)$ in this example. Since the largest eigenvalue is $4$, $\alpha=0.2$ lies below the basic stability limit $2/4=0.5$.

Common implementation errors include using $x+\alpha g$, confusing the gradient with a force sign convention, evaluating the gradient at an old variable after partially updating it, and forgetting that Python's `*` is elementwise while `@` performs matrix multiplication. Also check that the objective and gradient describe the same function. A numerical gradient check can compare a directional derivative with

$$
\frac{f(x+hd)-f(x-hd)}{2h}\approx\nabla f(x)^Td.
$$

Logging objective values, gradient norms, and step sizes makes a numerical relaxation diagnosable rather than mysterious.

## Exercise 1: checking the scope of the theorems

A colleague makes three statements:

1. “If $\nabla f(x)=0$, then $x$ is the unique global minimiser.”
2. “If $f$ is convex and differentiable and $\nabla f(x^*)=0$, then $x^*$ is a global minimiser.”
3. “If $f$ is $L$-smooth, gradient descent with any positive step size must decrease the objective.”

For each statement, decide whether it is true as written. If it is false, give the missing assumptions or a counterexample.

### Worked solution

Statement 1 is false. A stationary point can be a maximum or saddle, as shown by $f(x)=x^3$ at zero or $f(x,y)=x^2-y^2$ at the origin. Even if the point is a global minimiser, uniqueness requires additional curvature or another condition; the constant function has infinitely many minimisers.

Statement 2 is true for an unconstrained problem on a convex domain. Convexity gives

$$
f(y)\geq f(x^*)+\nabla f(x^*)^T(y-x^*)=f(x^*)
$$

for every $y$. It does not guarantee uniqueness. Strong convexity would guarantee a unique minimiser.

Statement 3 is false. Smoothness supplies an upper bound involving the step size. A standard guarantee requires, for example, $0<\alpha\leq1/L$ (and appropriate convexity assumptions for some global error statements). A positive step larger than the stability range can overshoot or diverge, even for a simple quadratic.

## Exercise 2: a hand calculation on a mechanical-style quadratic

Consider

$$
f(q_1,q_2)=\frac12(4q_1^2+q_2^2)-8q_1-2q_2.
$$

Interpret $q=(q_1,q_2)$ as two coordinates of a simplified configuration and $f$ as an energy-like objective. Starting from $q_0=(0,0)$, perform two gradient-descent steps with $\alpha=0.2$. Calculate the gradient, both iterates, and the objective values. Then find the exact stationary point and explain why it is the unique global minimiser.

### Worked solution

The gradient is

$$
\nabla f(q)=\begin{bmatrix}4q_1-8\\q_2-2\end{bmatrix}.
$$

At $q_0=(0,0)$,

$$
\nabla f(q_0)=(-8,-2),
$$

so

$$
q_1=q_0-0.2(-8,-2)=(1.6,0.4).
$$

The initial objective is $f(q_0)=0$. At $q_1$,

$$
\nabla f(q_1)=(4(1.6)-8,\;0.4-2)=(-1.6,-1.6).
$$

Therefore,

$$
q_2=q_1-0.2(-1.6,-1.6)=(1.92,0.72).
$$

Using the objective formula, $f(q_1)=-7.2$ and $f(q_2)=-8.1792$. The values decrease, as expected for this step size.

The stationary point solves

$$
4q_1-8=0,\qquad q_2-2=0,
$$

so $q^*=(2,2)$. The Hessian is

$$
\nabla^2f=\begin{bmatrix}4&0\\0&1\end{bmatrix}.
$$

Its eigenvalues are $4$ and $1$, both positive. Thus the function is strongly convex, with $\mu=1$ and $L=4$. The stationary point is consequently the unique global minimiser. The calculation also shows that the first coordinate responds more strongly because its curvature is larger.

## Exercise 3: diagnosing an executable Python implementation

Run the following program. It is intended to minimise the same quadratic as in Exercise 2, but it contains two errors.

```python
import numpy as np

A = np.array([[4.0, 0.0], [0.0, 1.0]])
b = np.array([8.0, 2.0])

def f(x):
    return 0.5 * x @ A @ x - b @ x

def grad(x):
    return A @ x + b

x = np.array([0.0, 0.0])
alpha = 0.2
for k in range(20):
    x = x + alpha * grad(x)
    print(k, f(x))
```

Identify both errors, correct the code, and state what behaviour you expect after the correction. Your corrected version must be executable Python.

### Worked solution

The objective is $f(x)=\frac12x^TAx-b^Tx$. Differentiating gives $\nabla f(x)=Ax-b$, not $Ax+b$. The second error is the update direction: minimisation uses $x-\alpha\nabla f(x)$, not addition. The corrected program is:

```python
import numpy as np

A = np.array([[4.0, 0.0], [0.0, 1.0]])
b = np.array([8.0, 2.0])

def f(x):
    return 0.5 * x @ A @ x - b @ x

def grad(x):
    return A @ x - b

x = np.array([0.0, 0.0])
alpha = 0.2
for k in range(20):
    g = grad(x)
    print(k, x, f(x), np.linalg.norm(g))
    x = x - alpha * g
```

The corrected code should move toward $(2,2)$ and generally produce decreasing objective values. The step is stable because the largest eigenvalue of $A$ is $4$ and $0.2<2/4$. The objective need not reach its exact minimum in twenty iterations, but the gradient norm and distance to $(2,2)$ should become small. The diagnostic principle is general: derive the gradient independently, check the sign convention, and log enough quantities to distinguish descent from divergence.

## Summary: a practical workflow

Start by defining variables and an objective whose units and scaling are understood. Ask whether the problem is unconstrained, differentiable, convex, and smooth. Use $\nabla f=0$ as a stationarity condition, not automatically as proof of a minimum. Use Hessian curvature locally; use convexity and strong convexity for global conclusions and convergence rates.

For a first implementation, calculate the gradient and use gradient descent with a conservative step or backtracking. Monitor the objective, gradient norm, and iteration count. If a narrow valley causes zigzagging, improve scaling or consider momentum. If gradients come from sampled data, use stochastic or adaptive methods with appropriate schedules and reproducibility checks. If accurate gradients are available and curvature is useful, Newton or quasi-Newton methods can reduce iteration counts, especially with line-search safeguards.

Finally, treat every numerical result as something to diagnose. Check the gradient, units, stopping criterion, conditioning, and sensitivity to the initial guess and step size. The central habit is to connect the update rule to the geometry of the objective: each method is a different way of using slope and curvature to find a configuration with no profitable local improvement.