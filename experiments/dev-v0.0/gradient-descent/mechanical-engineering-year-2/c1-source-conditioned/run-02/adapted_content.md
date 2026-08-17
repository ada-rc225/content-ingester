# Gradient Descent as a Way of Finding Equilibrium

In many engineering problems, the central question is not merely “what is the answer?” but “what state is the system most stable in?” A mechanical system, for example, tends to move toward a configuration of lower potential energy. If we describe that energy by a function $f(x)$, then the problem of finding equilibrium becomes an optimisation problem: we seek a point $x$ at which the system is no longer driven to move further.

This is why optimisation is so useful in engineering. The same mathematics that helps us find the lowest energy state of a structure also helps us tune a controller, fit a model, or solve a numerical problem. In this chapter, we will connect optimisation to the familiar ideas of potential energy, equilibrium, and relaxation.

## 1. Optimisation, equilibrium and stationary points

Suppose we want to minimise an unconstrained function

$$
\min_{x \in \mathbb{R}^d} f(x).
$$

Here $x$ may be a single scalar, a vector of design variables, or a state vector. In mechanics, $f(x)$ might represent potential energy $U(x)$. A local minimum of $f$ is a point where the energy is lower than nearby states. At such a point, the system is at rest in the sense that there is no first-order tendency to move downhill.

The first-order necessary condition for a smooth minimiser $x^*$ is

$$
\nabla f(x^*) = 0.
$$

This means that every component of the gradient vanishes. In physical terms, the force is zero. If $f$ is potential energy, then the force is related to the negative gradient:

$$
F(x) = -\nabla f(x).
$$

So at equilibrium, the force is zero and the gradient is zero.

To decide whether a stationary point is a minimum, we use second derivatives. If $f$ is twice differentiable and the Hessian matrix $\nabla^2 f(x^*)$ is positive definite, then $x^*$ is a strict local minimum. In one dimension, this reduces to the familiar condition $f''(x^*) > 0$.

A useful engineering interpretation is this: a stationary point may be a minimum, a maximum, or a saddle point. The gradient tells us where the system is “flat” in the first-order sense, but the Hessian tells us whether that flatness is a valley, a hill, or a saddle.

## 2. Smoothness and convexity

The ideas of smoothness and convexity are important because they tell us how predictable an optimisation problem is.

A function is smooth if it has no sharp corners or sudden jumps. In the context of gradient-based methods, we usually require differentiability, and often Lipschitz continuity of the gradient. A function is $L$-smooth if there exists a constant $L > 0$ such that

$$
\|\nabla f(x) - \nabla f(y)\| \le L\|x-y\|.
$$

This says that the gradient cannot change too abruptly. In a mechanical analogy, the force cannot jump wildly from one position to another. Smoothness makes the problem easier to solve numerically because the slope changes gradually.

Convexity is a stronger structural property. A differentiable function is convex if

$$
f(y) \ge f(x) + \langle \nabla f(x), y-x \rangle
$$

for all $x$ and $y$. Geometrically, the graph of a convex function lies above every tangent line. This means it has no “holes” or multiple competing valleys. A strongly convex function has a curvature lower bound, so it is not only convex but curved enough to make the minimum more well-behaved.

For engineering students, the key message is simple: if the objective is smooth and convex, then there is usually a single well-defined minimum, and optimisation methods tend to behave more reliably.

## 3. Gradient descent as numerical relaxation

The most basic optimisation algorithm is gradient descent. It is based on a very simple idea: move in the direction that reduces the objective most quickly.

If the gradient $\nabla f(x_k)$ points in the direction of steepest increase, then the negative gradient $-\nabla f(x_k)$ points in the direction of steepest decrease. The update is

$$
x_{k+1} = x_k - \alpha_k \nabla f(x_k),
$$

where $\alpha_k > 0$ is the step size, or learning rate.

This is the mathematical version of relaxation. You start at some guess $x_0$, compute the local slope, and then move downhill. If the step is chosen well, the objective decreases:

$$
f(x_{k+1}) < f(x_k).
$$

In mechanics, this is similar to letting a damped system relax toward equilibrium. The gradient acts like a restoring force, and the step size controls the amount of motion at each iteration.

The update is easy to implement in code. If we have a scalar function $f(x)$, then the gradient is simply the derivative, but in higher dimensions it becomes a vector of partial derivatives. The code operation

```python
x = x - alpha * grad(x)
```

implements the mathematical update

$$
x_{k+1} = x_k - \alpha_k \nabla f(x_k).
$$

## 4. Choosing the step size

Step-size selection is one of the central practical issues in optimisation. If the step is too small, progress is slow. If it is too large, the method may overshoot and even increase the objective.

A simple choice is a constant step size $\alpha_k = \alpha$. In many smooth problems, a value smaller than $2/L$ is safe when $L$ is the smoothness constant. A more practical strategy is backtracking line search. Here we try a candidate step, check whether the objective has decreased enough, and reduce the step if necessary. The condition is often written as

$$
f(x_k - \alpha_k \nabla f(x_k)) \le f(x_k) - c\alpha_k\|\nabla f(x_k)\|^2,
$$

with $0 < c < 1/2$.

This rule says that we accept the step only if it gives a sufficient decrease in the objective. In engineering language, we do not want to take a step that causes the system to “bounce past” the equilibrium point without settling.

## 5. Convergence behaviour

Gradient descent is reliable when the objective is smooth and the step size is chosen carefully. For an $L$-smooth convex function, using a suitable step size gives a convergence rate of order $O(1/k)$. That means the error reduces roughly like $1/k$ after $k$ iterations. For strongly convex functions, the behaviour is faster: the method converges linearly, which is much more attractive.

In practice, the observed behaviour depends on the shape of the objective. If the function is narrow and elongated, like a valley, gradient descent can zigzag and take many steps. This is the same as a damped particle moving in a shallow bowl with strong anisotropy. The method still converges, but not always efficiently.

When the gradient becomes very small, the update becomes small too. That is why gradient descent naturally slows down near a minimum. In real systems, that is often desirable: the motion becomes gentler as the system approaches equilibrium.

## 6. Momentum and acceleration

The basic gradient descent update can be improved by adding momentum. Instead of relying only on the current gradient, the method also carries some of the previous direction forward. The heavy-ball update is

$$
x_{k+1} = x_k - \alpha \nabla f(x_k) + \beta(x_k - x_{k-1}),
$$

where $\beta \in [0,1)$ is the momentum coefficient.

Momentum helps when the optimisation path oscillates. In a narrow valley, the iterates may repeatedly overshoot the centreline. Momentum acts like inertia and can help the method continue moving in a useful direction rather than reversing too quickly.

Nesterov acceleration is a related idea. Instead of evaluating the gradient at the current point, the method first makes a look-ahead step and then evaluates the gradient there. The update is

$$
y_k = x_k + \beta_k(x_k - x_{k-1}),
$$

$$
x_{k+1} = y_k - \alpha \nabla f(y_k).
$$

This is often more effective than plain momentum because it uses a slightly more informed direction. In engineering terms, it is like giving the relaxation process a bit of anticipation rather than reacting only to the current slope.

## 7. Stochastic and adaptive optimisation

So far, we have assumed that we can evaluate the full gradient exactly. In many modern applications, that is too expensive. If the objective is a sum of many terms,

$$
f(x) = \frac{1}{N}\sum_{i=1}^N f_i(x),
$$

then computing the full gradient may be costly. Stochastic gradient descent replaces the exact gradient by a noisy estimate based on one term, or a small batch of terms. The update becomes

$$
x_{k+1} = x_k - \eta_k g_k(x_k),
$$

where $g_k(x_k)$ is a stochastic estimate of the gradient.

Because the estimate is noisy, the method does not converge to the exact minimum in the same way as full gradient descent. Instead, it approaches a neighbourhood of the minimum, and the step size must shrink carefully over time. This is why practical stochastic methods use diminishing step sizes.

Adaptive methods such as AdaGrad, RMSProp and Adam further improve robustness by scaling the update according to past gradients. In these methods, the update is not just a simple step in the gradient direction. Instead, the algorithm learns which directions have been important and adjusts the effective step size in each coordinate. This is especially helpful when different variables have very different scales.

## 8. A brief introduction to second-order methods

First-order methods use only the gradient. Second-order methods also use curvature information, which comes from the Hessian matrix. Newton’s method uses the update

$$
x_{k+1} = x_k - [\nabla^2 f(x_k)]^{-1}\nabla f(x_k).
$$

This is more powerful near the solution because it uses information about how sharply the objective curves. In a quadratic approximation, the Hessian tells us how the surface bends, so the method can take a much better step than simple gradient descent. The trade-off is that computing and inverting the Hessian is more expensive, especially in high dimensions.

For this reason, second-order methods are often used when the problem size is moderate and the Hessian is available or can be approximated efficiently.

## 9. A Python example: relaxing toward the minimum

Consider the potential-like objective

$$
f(x,y) = \frac{1}{2}(x-1)^2 + \frac{1}{2}(y+0.5)^2.
$$

This function has a unique minimum at $(1,-0.5)$. The gradient is

$$
\nabla f(x,y) = \begin{bmatrix} x-1 \\ y+0.5 \end{bmatrix}.
$$

The update rule is therefore

$$
\begin{bmatrix}x_{k+1} \\ y_{k+1}\end{bmatrix} = \begin{bmatrix}x_k \\ y_k\end{bmatrix} - \alpha \begin{bmatrix}x_k-1 \\ y_k+0.5\end{bmatrix}.
$$

Here is an executable Python implementation:

```python
import numpy as np

# Define the objective: f(x, y) = 1/2 (x-1)^2 + 1/2 (y+0.5)^2

def f(x):
    return 0.5 * (x[0] - 1.0) ** 2 + 0.5 * (x[1] + 0.5) ** 2

# Define the gradient: grad f = [x-1, y+0.5]

def grad(x):
    return np.array([x[0] - 1.0, x[1] + 0.5])

# Start from an initial guess far from the minimum
x = np.array([3.0, 2.0])
alpha = 0.2

for k in range(15):
    g = grad(x)                 # Computes the gradient ∇f(x_k)
    x = x - alpha * g           # Implements x_{k+1} = x_k - α∇f(x_k)
    print(f"k={k:2d}, x={x}, f(x)={f(x):.4f}")
```

In this code, the function `f` evaluates the objective, `grad` evaluates the gradient, and the line `x = x - alpha * g` implements the gradient descent update. As the loop runs, the point moves toward the minimum at $(1,-0.5)$.

## 10. Exercises

1. For the one-dimensional function $f(x) = (x-3)^2$, find the stationary point and determine whether it is a minimum, maximum, or neither. Explain your answer using the first and second derivatives.

2. Suppose $f(x) = x^4$. Show that $x=0$ is a stationary point. Why is it a minimum even though the second derivative is zero there?

3. For a smooth function with gradient Lipschitz constant $L$, explain why taking a step size $\alpha \le 1/L$ is often sensible for gradient descent.

4. Compare the behaviour of plain gradient descent and momentum on a narrow, elongated valley. Which method is likely to be more efficient, and why?

5. Modify the Python example so that it uses momentum. You can keep the same objective but introduce a term like `x_new = x - alpha * g + beta * (x - x_prev)`. Explain how the update changes in relation to the mathematical formula.

Gradient descent is not just a numerical trick. It is a way of turning the idea of “moving downhill” into a practical algorithm. When you connect that algorithm to potential energy, equilibrium and relaxation, it becomes much easier to see why optimisation is so central in engineering mathematics.
