# Gradient descent as a mechanical relaxation method

In mechanical engineering, a system often settles into a configuration that minimises its potential energy. The same idea appears in optimisation. When we choose a design variable or a state vector $x$, we may ask for the value that makes an objective function $f(x)$ as small as possible. In that sense, optimisation is a generalised form of finding an equilibrium state.

<!-- claim-GEN-001 -->
A useful starting point is to think of the objective as a potential energy surface. If we denote the state by $x$, then the optimisation problem is

$$
\min_{x \in \mathbb{R}^d} f(x).
$$

For a simple mechanical system, the potential energy $V(q)$ is a scalar function of the coordinate $q$, and equilibrium occurs when the force is zero. Since the force is the negative gradient of potential energy, we have

$$
F(q) = -\frac{dV}{dq}(q),
$$

so equilibrium corresponds to $dV/dq = 0$. That is the same mathematical structure as the stationarity condition in optimisation.

<!-- claim-GEN-002 -->
If $x^*$ is a local minimiser of a differentiable function $f$, then the first-order necessary condition is

$$
\nabla f(x^*) = 0.
$$

This means the slope of the objective is zero at the minimiser. In mechanical terms, the system is at equilibrium because there is no net tendency to move downhill. For a twice-differentiable function, the second-order test is also useful. If the Hessian $\nabla^2 f(x^*)$ is positive definite, then the point is a strict local minimum; if it is indefinite, the point may be a saddle point rather than a stable equilibrium.

<!-- claim-GEN-003 -->
The next idea is smoothness. A function is $L$-smooth when its gradient does not change too abruptly. Formally,

$$
\|\nabla f(x) - \nabla f(y)\| \le L \|x-y\|, \quad \forall x,y \in \mathbb{R}^d.
$$

This condition matters because it limits how much the slope can change from one step to the next. In a mechanical analogy, it means the force field cannot change violently over a small displacement. The corresponding inequality, often called the descent lemma, is

$$
f(y) \le f(x) + \langle \nabla f(x), y-x \rangle + \frac{L}{2}\|y-x\|^2.
$$

The practical meaning is that a sufficiently small step in the direction of decreasing energy will not make the objective jump upward. To see why this matters, imagine moving a mass attached to a spring. If the force field changes too quickly, a large displacement could push the mass past the equilibrium position. The smoothness assumption prevents that kind of violent overshoot by limiting the local change in slope. In optimisation terms, it guarantees that the local linear model of the objective is not too misleading over a small step.

<!-- claim-GEN-004 -->
Convexity gives a cleaner geometric picture. A differentiable function is convex if, for all $x$ and $y$,

$$
f(y) \ge f(x) + \langle \nabla f(x), y-x \rangle.
$$

Geometrically, the graph of a convex function lies above all of its tangent lines. In our mechanical analogy, this means the potential energy surface is bowl-shaped rather than full of local traps. Strong convexity adds a quadratic lower bound,

$$
f(y) \ge f(x) + \langle \nabla f(x), y-x \rangle + \frac{\mu}{2}\|y-x\|^2,
$$

with $\mu>0$. This is useful because it makes the problem better behaved and often speeds up convergence.

<!-- claim-GEN-005 -->
The standard gradient descent update is

$$
x_{k+1} = x_k - \alpha_k \nabla f(x_k),
$$

where $\alpha_k > 0$ is the step size. This is the central algorithmic rule. In words, the next iterate moves in the direction of the negative gradient, which is the direction of steepest descent. If you think in terms of potential energy, the update nudges the system downhill.

A practical question is how to choose $\alpha_k$. Three common choices are:

1. a constant step size, often chosen as $\alpha = 1/L$ or a value in $(0, 2/L)$ for smooth problems;
2. an exact line search, where one chooses $\alpha_k$ to minimise the objective along the descent direction;
3. backtracking, where one starts with a trial step size and reduces it until the decrease condition is satisfied.

The source material also gives the standard Armijo-style condition

$$
f(x_k - \alpha_k \nabla f(x_k)) \le f(x_k) - c\alpha_k \|\nabla f(x_k)\|^2,
$$

with $0<c<1/2$. This says the chosen step should reduce the objective by a sufficient amount; otherwise the step is too large. A useful way to read this condition is as a compromise between ambition and safety. If the step is too ambitious, the update may overshoot the bottom of the valley; if it is too cautious, progress will be unnecessarily slow. Backtracking line search is a practical instrument for finding that compromise: start with a trial step, test the decrease condition, and shrink the step until it passes.

<!-- claim-GEN-006 -->
For an $L$-smooth convex objective, gradient descent with a constant step size $1/L$ has the general bound

$$
f(x_k) - f(x^*) \le \frac{L\|x_0-x^*\|^2}{2k}.
$$

This is a slow but dependable rate. It tells us that the error falls like $O(1/k)$, so the method improves steadily but not spectacularly. If the function is also $\mu$-strongly convex, the rate improves dramatically. In that case, the error can decrease geometrically, roughly like

$$
f(x_k) - f(x^*) \le \left(1 - \frac{\mu}{L}\right)^k (f(x_0)-f(x^*)).
$$

The quantity $\kappa = L/\mu$ is called the condition number. Large condition numbers mean the objective is elongated or ill-conditioned, so plain gradient descent can take many steps to reach the minimum.

<!-- claim-GEN-007 -->
Momentum is a simple way to reduce oscillation and to accelerate progress in difficult landscapes. The heavy-ball update is

$$
x_{k+1} = x_k - \alpha \nabla f(x_k) + \beta (x_k - x_{k-1}),
$$

where $\beta \in [0,1)$ is the momentum coefficient. The extra term acts like inertia: the iterate remembers its previous direction. In the mechanical analogy, this is similar to a damped system that carries momentum rather than stopping immediately at each step. Nesterov’s method uses a look-ahead point,

$$
 y_k = x_k + \beta_k (x_k - x_{k-1}), \qquad x_{k+1} = y_k - \alpha \nabla f(y_k),
$$

and this often gives a faster decay rate on smooth convex problems.

<!-- claim-GEN-008 -->
So far, the discussion has assumed that the full gradient is available. In large-scale problems, however, computing $\nabla f(x)$ may be expensive. Stochastic gradient descent (SGD) replaces the full gradient with an unbiased estimate $g_k(x_k)$ and uses

$$
x_{k+1} = x_k - \eta_k g_k(x_k).
$$

The noise is the price paid for speed. The method usually does not converge to the exact minimiser for a fixed step size, because the stochastic error keeps the iterate moving around the minimum. For asymptotic convergence, the step sizes must satisfy the Robbins-Monro conditions

$$
\sum_{k=1}^{\infty} \eta_k = \infty, \qquad \sum_{k=1}^{\infty} \eta_k^2 < \infty.
$$

In other words, the steps must decrease slowly enough to keep learning, but not so slowly that progress stalls.

<!-- claim-GEN-009 -->
Adaptive methods try to adjust the step size automatically. AdaGrad accumulates squared gradients, RMSProp uses an exponential moving average of squared gradients, and Adam combines first-moment and second-moment estimates. The common theme is that the update is scaled differently in each coordinate, so the optimiser can take larger steps where the gradient is small and smaller steps where it is large. This is especially useful when the objective has very different sensitivities in different directions.

<!-- claim-GEN-010 -->
A brief look at second-order methods shows why curvature matters. Newton’s method uses the Hessian:

$$
x_{k+1} = x_k - [\nabla^2 f(x_k)]^{-1}\nabla f(x_k).
$$

The Hessian contains information about the local curvature of the energy surface. That makes Newton’s method much faster near a minimiser, because it adapts to the shape of the bowl. In one dimension, this is essentially the same as saying that the second derivative tells us whether the curve is bending gently or sharply. A large positive second derivative means the valley is narrow, and a method that uses curvature information can take a more informed step. Quasi-Newton methods, such as BFGS, approximate the Hessian using gradient differences rather than computing the full matrix explicitly. They are often a practical compromise between first-order and second-order methods, and they are particularly useful when the full Hessian is expensive to form or store.

<!-- claim-GEN-011 -->
The link between the mathematics and code is direct. In the update rule $x_{k+1}=x_k-\alpha\nabla f(x_k)$, the Python operation is simply an assignment of the new value using the current gradient. A small one-dimensional example is shown below.

```python
import numpy as np

# Objective: f(x) = (x - 2)^2
# Gradient: df/dx = 2(x - 2)

def f(x):
    return (x - 2.0) ** 2


def grad_f(x):
    return 2.0 * (x - 2.0)

x = 5.0
alpha = 0.2
for k in range(8):
    g = grad_f(x)          # this is the mathematical gradient
    x = x - alpha * g      # this is the update x_{k+1} = x_k - alpha * grad
    print(f"k={k}, x={x:.3f}, f(x)={f(x):.3f}")
```

The code follows the mathematical rule exactly: it evaluates the gradient, multiplies it by the step size, and subtracts that from the current point. In a mechanical analogy, each line of code performs a small relaxation step in the direction of lower potential energy.

<!-- claim-GEN-012 -->
Exercises:

1. For a one-dimensional potential energy function $V(q)=\frac{1}{2}k(q-q_0)^2$, find the stationary point and classify it as a minimum or maximum using the second derivative.
2. For the quadratic objective $f(x)=\frac{1}{2}(x-3)^2$, compute the first gradient descent step from $x_0=5$ using $\alpha=0.2$.
3. Explain why a very large step size can cause the iterate to overshoot the minimiser, and describe how backtracking helps.
4. Compare plain gradient descent with momentum on a strongly convex quadratic. Which method is likely to be less oscillatory?
5. Write a short Python function that implements gradient descent for a scalar function and plot the values of $x_k$ against $k$.

This lesson is intentionally compact, but it introduces a very important engineering habit of mind. When a problem is posed as an optimisation task, the first question is often not “what algorithm should I use?” but “what does the energy landscape look like?” That question, in turn, leads to stationarity, convexity, smoothness, and the choice of a step size. The important idea is that optimisation is not just an abstract algebraic exercise: it is a way of finding the point where a system is at equilibrium, whether that system is a mechanical structure, a design variable, or a numerical algorithm. In practice, a good optimiser is one that respects the geometry of the problem, not merely one that applies a formula blindly. That is why the gradient, the curvature, the learning rate, and the notion of relaxation all appear together in the same story.
