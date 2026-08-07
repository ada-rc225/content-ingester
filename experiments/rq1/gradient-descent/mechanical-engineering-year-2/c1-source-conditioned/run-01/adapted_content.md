# Gradient Descent and First-Order Optimisation for Mechanical Engineers

Many engineering problems can be viewed as a search for the lowest energy state. A mass-spring system settles to equilibrium when its potential energy is minimised, at least locally. A controller is tuned to reduce a tracking error, a design is adjusted to reduce a penalty function, and a fitted model is improved by making a residual measure smaller. In each case, the underlying task is an optimisation problem.

This chapter introduces first-order optimisation through the lens of potential energy, equilibrium and numerical relaxation. The goal is not to present a complete theory of convex optimisation, but to build an intuitive and useful understanding of how optimisation algorithms work and why they are so widely used.

## 1. Optimisation as a search for equilibrium

Let $x$ denote a vector of decision variables. We often want to choose $x$ so that some objective function $f(x)$ becomes as small as possible. In mechanics, $f$ may represent potential energy. In data fitting, $f$ may represent total error. In design, $f$ may represent cost or penalty.

The unconstrained optimisation problem is

$$
\min_{x \in \mathbb{R}^d} f(x).
$$

Here $d$ is the number of variables. If there are no restrictions on $x$, then the problem is unconstrained. The quantity we seek is a minimiser $x^*$ such that

$$
x^* = \arg\min_x f(x).
$$

The connection with mechanics is direct. A system at equilibrium is not moving because its potential energy is at a stationary point. If the system is displaced slightly, the tendency to return to equilibrium is governed by the shape of the energy landscape. Optimisation algorithms mimic this behaviour numerically by moving downhill in the objective landscape.

## 2. Stationary points and the first-order condition

Suppose $f$ is differentiable. A point $x^*$ is called a stationary point if

$$
\nabla f(x^*) = 0.
$$

The symbol $\nabla f$ is the gradient. In one dimension, this is just the derivative $f'(x)$. In several dimensions, it is a vector of partial derivatives. A stationary point is a candidate for a minimum, maximum or saddle point. It is not automatically a minimiser.

For example, the function $f(x)=x^3$ has derivative $f'(x)=3x^2$, so $x=0$ is stationary. But $x=0$ is neither a minimum nor a maximum; it is a point where the slope changes sign in a way that does not produce a local extremum. This illustrates that the condition $\nabla f(x^*)=0$ is necessary for a smooth local minimum, but not sufficient on its own.

In practice, this first-order condition is often the starting point. If a gradient-based method reaches a point where the gradient is nearly zero, then it has found a point where the objective is no longer changing much in the immediate neighbourhood.

## 3. Smoothness and convexity

An optimisation method needs the objective to behave in a reasonably regular way. A smooth function is one that is differentiable and changes gradually. For first-order methods, smoothness is especially important because the gradient is then a reliable guide to local descent.

A standard form of smoothness is $L$-smoothness. A function is $L$-smooth if its gradient does not change too abruptly. In mathematical terms,

$$
\|\nabla f(x)-\nabla f(y)\| \le L\|x-y\|,
$$

for all points $x$ and $y$. The constant $L$ gives a bound on how rapidly the gradient can change. This matters because it limits how aggressively we can move without overshooting the intended descent direction.

Convexity is another important structural property. A differentiable function is convex if, for every pair of points $x$ and $y$,

$$
f(y) \ge f(x) + \langle \nabla f(x), y-x \rangle.
$$

The geometric meaning is that the graph of the function lies above its tangent lines. This is helpful because for a convex differentiable function, any stationary point is a global minimiser. In other words, if the objective is convex and smooth, then solving $\nabla f(x)=0$ is often enough to identify the global minimum.

For non-convex functions, the situation is more complicated. The function may have several local minima and even saddle points. A numerical method may then converge to a local minimum rather than the best one. This is one reason why the shape of the objective matters so much in optimisation.

## 4. The gradient descent update

The basic idea of gradient descent is simple: move in the direction that lowers the objective most quickly. Since the gradient points in the direction of steepest increase, the negative gradient points in the direction of steepest decrease.

The update is

$$
x_{k+1} = x_k - \eta\,\nabla f(x_k),
$$

where $x_k$ is the current iterate, $\eta>0$ is the step size, and $k$ indexes the iteration. This is the canonical first-order update because it uses only the gradient, not second derivatives.

In one dimension, this becomes

$$
x_{k+1}=x_k-\eta f'(x_k).
$$

If the derivative is positive, the next point moves left; if the derivative is negative, it moves right. This is exactly the sort of downhill motion one might imagine in a potential-energy landscape. The algorithm repeatedly relaxes the current state toward lower energy.

The interpretation is mechanical. Imagine a ball rolling on a surface whose height is $f(x)$. The force is related to the slope, and the negative gradient is the downhill direction. Gradient descent is a discrete-time version of that motion.

## 5. Step-size selection

The step size $\eta$ controls how far the method moves at each iteration. If $\eta$ is too large, the method can overshoot the minimum and oscillate. If $\eta$ is too small, it may converge very slowly.

For the quadratic function

$$
f(x)=\tfrac{1}{2}ax^2, \quad a>0,
$$

the gradient is $f'(x)=ax$, so the update becomes

$$
x_{k+1}=(1-\eta a)x_k.
$$

This simple case reveals the basic rule. If $0<\eta a<2$, the iterates shrink toward zero. If $\eta a=1$, convergence is immediate in one step for this particular example. If $\eta a>2$, the iteration oscillates and may diverge. This shows why step-size choice is central to stability.

In practice, a constant step size is often used at first, but more robust methods choose the step size adaptively. One common strategy is backtracking: start with a candidate step size, try it, and reduce it if the objective does not decrease sufficiently. The idea is to keep the step large enough to make progress but small enough to remain reliable.

## 6. Convergence behaviour

The behaviour of gradient descent depends on the shape of the objective. For smooth convex functions, the method usually converges to a minimiser, though the rate may be slow if the function is elongated or ill-conditioned. In such cases, the landscape has a narrow valley, and the method may take many steps to move along it.

To see the effect more clearly, consider a quadratic function in two variables. If the curvature is very different in different directions, the method can zigzag and make slow progress. This is why the basic version of gradient descent is often improved by momentum or adaptive scaling.

The important point is that gradient descent is not just a one-step recipe; it is a repeated relaxation procedure. Each step reduces the objective by moving in a descent direction. When the gradient becomes small, the iterates approach a stationary point.

## 7. Momentum and acceleration

A drawback of ordinary gradient descent is that it reacts only to the current gradient. Momentum adds memory by carrying along a velocity term. A common form is

$$
v_{k+1}=\beta v_k - \eta \nabla f(x_k),
$$

$$
x_{k+1}=x_k+v_{k+1},
$$

where $v_k$ is a velocity-like variable and $0\le \beta <1$ is the momentum parameter. If the gradient points in approximately the same direction over several steps, then the velocity builds up and the method moves faster.

This is useful when the objective landscape is curved. Ordinary gradient descent may take many small steps and appear hesitant; momentum allows the method to keep moving in a useful direction. The analogy is to a particle rolling downhill with inertia.

A related technique is Nesterov acceleration. Instead of evaluating the gradient at the current point, it evaluates it at a look-ahead point,

$$
y_k = x_k + \beta v_k,
$$

$$
x_{k+1}=y_k - \eta\nabla f(y_k).
$$

This can improve convergence on smooth convex problems, especially when the objective is not too difficult.

## 8. Stochastic and adaptive optimisation

In large-scale problems, computing the full gradient can be expensive. Suppose the objective is a sum of many terms,

$$
f(x)=\frac{1}{N}\sum_{i=1}^N f_i(x).
$$

Then the full gradient requires evaluating all $N$ terms. Stochastic gradient descent replaces the full gradient by an estimate based on one randomly chosen term or a small batch of terms:

$$
\nabla f(x) \approx \nabla f_i(x).
$$

The update becomes

$$
x_{k+1}=x_k - \eta_k g_k(x_k),
$$

where $g_k(x_k)$ is a noisy gradient estimate. This makes each step cheaper, but the method becomes noisier. In practice, the step size is often reduced over time to maintain stability.

Adaptive methods go further by adjusting the step size separately for different coordinates. In AdaGrad and Adam, the optimiser accumulates information about the size of earlier gradients and uses that to scale the update. The key idea is that variables that have been changing a lot receive smaller effective steps, while variables that have been changing less receive larger ones. This helps the algorithm adapt to the geometry of the problem.

## 9. A brief introduction to second-order methods

Second-order methods use curvature information through the Hessian matrix, which contains second derivatives. The Hessian is denoted $\nabla^2 f(x)$. A Newton step uses a local quadratic approximation to the objective.

The update is

$$
x_{k+1}=x_k - [\nabla^2 f(x_k)]^{-1}\nabla f(x_k).
$$

This can be very effective, because it accounts not just for the slope but also for the curvature. Near a minimum, the method can converge very quickly. However, it is more expensive because it requires the Hessian and a linear solve. For large engineering problems, first-order methods are often preferred because they are simpler and cheaper per iteration.

## 10. A complete Python example

The following example is fully executable. It minimises a simple two-variable objective that can be interpreted as a potential-energy surface. The minimum is at $(1,-0.5)$.

```python
import numpy as np


def f(x):
    # Objective: a smooth potential-energy-like function
    return (x[0] - 1.0) ** 2 + 2.0 * (x[1] + 0.5) ** 2


def grad_f(x):
    # Gradient of the objective
    return np.array([2.0 * (x[0] - 1.0), 4.0 * (x[1] + 0.5)])


def gradient_descent(x0, eta=0.1, n_steps=50):
    x = x0.copy()
    history = [x.copy()]
    for _ in range(n_steps):
        g = grad_f(x)                 # Computes \nabla f(x)
        x = x - eta * g               # Implements x_{k+1} = x_k - eta \nabla f(x_k)
        history.append(x.copy())
    return history


x0 = np.array([0.0, 0.0])
history = gradient_descent(x0, eta=0.1, n_steps=50)

print("Initial point:", x0)
print("Final point:", history[-1])
print("Objective value:", f(history[-1]))
```

The link between the mathematics and the code is explicit:

- The function `f(x)` represents the objective $f(x)$.
- The function `grad_f(x)` computes the gradient $\nabla f(x)$.
- The line `x = x - eta * g` implements the update $x_{k+1}=x_k-\eta\nabla f(x_k)$.
- The loop performs repeated relaxation steps until the iterate approaches a minimum.

If you run this code, the point moves toward $(1,-0.5)$, where the gradient is zero and the objective value is smallest.

## 11. Summary and intuition

Gradient descent is a practical first-order optimisation method. It works by moving downhill in the objective landscape, very much like a system relaxing toward a lower-energy state. The central ideas are:

- an unconstrained optimisation problem seeks a point that minimises an objective;
- stationary points satisfy $\nabla f(x)=0$;
- smoothness makes the gradient useful as a local guide;
- convexity makes stationary points correspond to global minima;
- gradient descent uses $x_{k+1}=x_k-\eta\nabla f(x_k)$;
- the step size controls stability and speed;
- momentum and adaptive methods help when the problem is curved or poorly scaled;
- second-order methods use curvature information and can converge faster, but at greater cost.

For a mechanical engineering student, the most useful image is that of a system moving through an energy landscape until it reaches equilibrium. Optimisation is the numerical version of that physical relaxation process.

## Exercises

1. Consider $f(x)=x^2$. Derive the gradient descent update and explain what happens when $\eta=0.5$ and when $\eta=2$.
2. For $f(x)=\tfrac{1}{2}(x-3)^2$, find the stationary point and explain why it is a minimum.
3. Suppose $f$ is differentiable and convex. Why does a stationary point give a global minimum?
4. Modify the Python example so that the step size decreases over time, for example with $\eta_k=0.1/(1+k)$, and describe how the behaviour changes.
5. Explain the difference between standard gradient descent and momentum-based gradient descent when the objective landscape is curved.
