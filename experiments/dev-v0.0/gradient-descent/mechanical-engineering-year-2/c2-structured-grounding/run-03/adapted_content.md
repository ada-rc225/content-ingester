# Gradient descent as a way of finding equilibrium

Mechanical engineering students often meet the idea of equilibrium in statics and dynamics: a system settles when the net force is zero. Optimisation uses the same idea in a more general form. Instead of asking only for a force balance, we ask for a point that makes an objective function as small as possible. In that setting, the objective plays the role of a potential energy surface and the optimiser searches for the lowest-energy configuration.

<!-- section: SEC-01 -->
## From potential energy to optimisation

A simple starting point is a one-dimensional potential energy function $V(q)$. If the system is at coordinate $q$, the force is

$$
F(q) = -\frac{dV}{dq}(q).
$$

Equilibrium occurs when the force is zero, so

$$
\frac{dV}{dq}(q)=0.
$$

That is the same mathematical structure as the stationarity condition in optimisation. If $x^*$ is a local minimiser of a differentiable function $f$, then

$$
\nabla f(x^*) = 0.
$$

The analogy is useful because it links the abstract optimisation problem to something concrete: the system is at rest when it has reached a minimum of potential energy. The difference is that optimisation may be applied to design variables, control parameters, or numerical state vectors, not only to a physical coordinate.

For a twice-differentiable objective, the second derivative or Hessian tells us more. If $\nabla^2 f(x^*)$ is positive definite, then the point is a strict local minimum. If it is indefinite, the point may be a saddle point rather than a stable equilibrium.

<!-- section: SEC-02 -->
## Smoothness, convexity, and the shape of the energy landscape

The next question is how easy it is to move towards the minimum. A function is $L$-smooth when its gradient does not change too abruptly. Formally,

$$
\|\nabla f(x) - \nabla f(y)\| \le L \|x-y\|, \quad \forall x,y \in \mathbb{R}^d.
$$

This matters because it limits how much the slope can change from one step to the next. In mechanical terms, the force field cannot change violently over a small displacement. The corresponding upper bound is the descent lemma:

$$
f(y) \le f(x) + \langle \nabla f(x), y-x \rangle + \frac{L}{2}\|y-x\|^2.
$$

This inequality says that if the step is not too large, the local linear model of the function is reliable enough to guarantee a decrease in the objective.

Convexity gives an even cleaner picture. A differentiable function is convex when

$$
f(y) \ge f(x) + \langle \nabla f(x), y-x \rangle,
$$

for all $x$ and $y$. The graph lies above its tangent lines, so the objective has a bowl-like shape rather than many local traps. Strong convexity adds a quadratic lower bound:

$$
f(y) \ge f(x) + \langle \nabla f(x), y-x \rangle + \frac{\mu}{2}\|y-x\|^2,
$$

with $\mu>0$. In engineering language, strong convexity means the energy surface is not merely bowl-shaped; it is a well-defined valley with a clear minimum.

<!-- section: SEC-03 -->
## Gradient descent as numerical relaxation

The most important algorithm is gradient descent. The update is

$$
x_{k+1} = x_k - \alpha_k \nabla f(x_k),
$$

where $\alpha_k > 0$ is the step size. In the potential-energy picture, this is a relaxation step: the state is nudged in the direction of lower energy.

The step size controls how aggressively we move. Three common choices are:

1. a constant step size, often $\alpha = 1/L$ or a value in $(0,2/L)$ for smooth problems;
2. exact line search, where $\alpha_k$ is selected to minimise the objective along the descent direction;
3. backtracking, where the step is reduced until the decrease condition is met.

The backtracking rule is usually written as

$$
f(x_k - \alpha_k \nabla f(x_k)) \le f(x_k) - c\alpha_k \|\nabla f(x_k)\|^2,
$$

with $0 < c < 1/2$. This condition says the step should lower the objective by a sufficient amount; if not, the step is too large and should be shrunk.

A simple Python example follows the same rule exactly. The code below minimises the quadratic objective $f(x) = (x-2)^2$ by repeatedly taking a small step downhill.

```python
import numpy as np


def f(x):
    return (x - 2.0) ** 2


def grad_f(x):
    return 2.0 * (x - 2.0)

x = 5.0
alpha = 0.2
for k in range(8):
    g = grad_f(x)
    x = x - alpha * g
    print(f"k={k}, x={x:.3f}, f(x)={f(x):.3f}")
```

The code is a direct implementation of the update $x_{k+1}=x_k-\alpha\nabla f(x_k)$. Each iteration is a small relaxation step that reduces the objective.

<!-- section: SEC-04 -->
## Convergence behaviour and step-size choices

For an $L$-smooth convex function, gradient descent with constant step size $1/L$ has the guarantee

$$
f(x_k) - f(x^*) \le \frac{L\|x_0-x^*\|^2}{2k}.
$$

This is a slow but dependable rate. It tells us the error falls like $O(1/k)$, so the method improves steadily but not dramatically.

If the function is also $\mu$-strongly convex, the rate improves. In that case, with $\alpha = 1/L$ the error can decay geometrically:

$$
f(x_k) - f(x^*) \le \left(1 - \frac{\mu}{L}\right)^k (f(x_0)-f(x^*)).
$$

The ratio $\kappa = L/\mu$ is the condition number. A large condition number means the energy valley is elongated, so plain gradient descent can require many steps to reach the bottom.

<!-- section: SEC-05 -->
## Momentum, stochastic updates, and second-order ideas

Momentum is one practical way to reduce oscillation. The heavy-ball update is

$$
x_{k+1} = x_k - \alpha \nabla f(x_k) + \beta (x_k - x_{k-1}),
$$

with $\beta \in [0,1)$. The extra term gives the iterate inertia, which can make the method less wobbly when the energy landscape is narrow or curved.

In large-scale problems, full gradients may be expensive. Stochastic gradient descent replaces the exact gradient by an unbiased estimate $g_k(x_k)$ and uses

$$
x_{k+1} = x_k - \eta_k g_k(x_k).
$$

The stochastic noise means the method usually does not converge exactly to the minimiser for a fixed step size. To keep learning without stalling, the step sizes should satisfy the Robbins-Monro conditions

$$
\sum_{k=1}^{\infty} \eta_k = \infty, \qquad \sum_{k=1}^{\infty} \eta_k^2 < \infty.
$$

A brief second-order view shows why curvature matters. Newton’s method uses the Hessian:

$$
x_{k+1} = x_k - [\nabla^2 f(x_k)]^{-1}\nabla f(x_k).
$$

The Hessian contains information about how sharply the energy surface bends. Near a minimum, that curvature information can make the method much faster than plain gradient descent.

### Exercises

1. For a one-dimensional potential energy function $V(q)=\tfrac{1}{2}k(q-q_0)^2$, find the stationary point and classify it as a minimum or maximum using the second derivative.
2. For the quadratic objective $f(x)=\tfrac{1}{2}(x-3)^2$, compute the first gradient descent step from $x_0=5$ using $\alpha=0.2$.
3. Explain why a very large step size can overshoot the minimiser, and describe how backtracking helps.
4. Compare plain gradient descent with momentum on a strongly convex quadratic. Which method is likely to be less oscillatory?
5. Modify the Python example so that it uses a backtracking step size instead of a fixed $\alpha$.
