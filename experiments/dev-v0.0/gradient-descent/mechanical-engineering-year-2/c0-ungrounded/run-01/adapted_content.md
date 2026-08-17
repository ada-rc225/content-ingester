# Gradient Descent and First-Order Optimisation for Mechanical Engineering

Many engineering problems can be framed as a search for the lowest energy state. A structure settles into equilibrium when its potential energy is as small as possible, subject to the constraints that apply. In the same spirit, optimisation asks a simple question: which values of some design variables make a chosen objective function as small as possible? In this chapter, that idea is developed through the language of potential energy, equilibrium and numerical relaxation.

For a mechanical engineer, this is not an abstract mathematical exercise. If you are tuning a spring system, finding the best control input, fitting a model to measurements, or adjusting a design to reduce a penalty function, you are often solving an optimisation problem. The methods discussed here are among the most widely used because they are simple, scalable and effective.

## 1. Optimisation as a search for equilibrium

Suppose we have a scalar objective function $f(x)$, where $x$ is a vector of decision variables. In many applications, $f$ is a potential energy, a cost, a loss, or a residual measure. The goal is to find a point $x^*$ such that

$$
x^* = \arg\min_x f(x).
$$

The notation $\arg\min$ means “the argument that minimises the function”. If $f$ represents potential energy, then a minimum corresponds to a stable or at least locally stable equilibrium. A system at equilibrium does not move spontaneously because any small disturbance increases the energy, at least locally.

This is the key link between mechanics and optimisation: the mathematical problem of minimisation and the physical idea of relaxation are closely related. If a system is initially away from equilibrium, it can move downhill in energy until it reaches a lower state. Optimisation algorithms mimic this process numerically.

## 2. Unconstrained optimisation and stationary points

In an unconstrained problem, we are free to choose any value of $x$ without restrictions. The task is therefore to minimise $f(x)$ over all $x$ in the relevant space.

A necessary condition for a differentiable function to have a local minimum at $x^*$ is that the gradient vanishes:

$$
\nabla f(x^*) = 0.
$$

A point where the gradient is zero is called a stationary point. It may be a local minimum, a local maximum, or a saddle point. For example, for a one-dimensional function $f(x)=x^3$, we have $f'(x)=3x^2$, so $x=0$ is stationary, but it is neither a minimum nor a maximum. In two or more dimensions, saddle points can occur even when the gradient is zero.

A stationary point is therefore not automatically the answer. To know more, we need additional structure. In many engineering contexts, however, the first step is to find points where the derivative or gradient is zero, because these are the candidates for minima.

## 3. Smoothness and convexity

The methods in this chapter rely on the idea that the objective is smooth, meaning that it is differentiable and changes gradually. A smooth function has a well-defined gradient at each point, and that gradient changes in a controlled way. For many practical problems, this is a reasonable assumption.

A function is convex if, for any two points $x_1$ and $x_2$, the line segment between them lies above the graph of the function:

$$
f(\theta x_1 + (1-\theta)x_2) \le \theta f(x_1) + (1-\theta)f(x_2), \quad 0 \le \theta \le 1.
$$

Convexity is important because it removes much of the ambiguity of stationary points. For a differentiable convex function, any stationary point is a global minimum. This is a huge simplification. In contrast, a non-convex function can have many local minima and saddle points, so a method may converge to a local solution rather than the best one.

You do not need to know the full theory of convex optimisation to use these ideas. It is enough to remember that smoothness gives the gradient a clear meaning, and convexity makes the problem more forgiving.

## 4. The gradient descent update

The basic idea of gradient descent is simple: if you want to reduce a function, move in the direction in which the function decreases most quickly. The gradient points in the direction of steepest increase. Therefore, the negative gradient points in the direction of steepest decrease.

The update rule is

$$
x_{k+1} = x_k - \eta \, \nabla f(x_k),
$$

where:

- $x_k$ is the current estimate,
- $\nabla f(x_k)$ is the gradient at that point,
- $\eta > 0$ is the step size, sometimes called the learning rate.

This is the first-order update because it uses only the gradient, not higher derivatives. In one dimension, the rule becomes

$$
x_{k+1} = x_k - \eta f'(x_k).
$$

If $f'(x_k)$ is positive, the next point moves left; if it is negative, the next point moves right. The method is therefore a numerical version of downhill motion in the landscape of the function.

## 5. Step-size selection and convergence behaviour

The step size controls how aggressively the algorithm moves. If $\eta$ is too large, the method may overshoot the minimum and oscillate. If $\eta$ is too small, the method may progress very slowly.

For a quadratic function

$$
f(x)=\tfrac{1}{2}ax^2,
$$

with $a>0$, the gradient is $f'(x)=ax$. The update becomes

$$
x_{k+1}=x_k - \eta a x_k = (1-\eta a)x_k.
$$

This shows the behaviour clearly. If $0<\eta a<2$, the iterates shrink towards zero. If $\eta a=1$, convergence is immediate in one step for this simple case. If $\eta a>2$, the update oscillates and can diverge. The same principle applies in higher dimensions, although the geometry is more complicated.

In practice, step-size choice is often guided by experience or by a line search. A line search tries a candidate step and accepts it if the objective decreases sufficiently. A simple strategy is to reduce $\eta$ when the function does not decrease and increase it when progress is good. In engineering software, this is often done automatically.

The convergence behaviour of gradient descent depends on the shape of the function. For smooth convex functions, the method often converges to a minimum, but the rate may be slow when the landscape is elongated or ill-conditioned. In such cases, the method can take many steps to move along a narrow valley. This is why the basic form of gradient descent is often improved by momentum or adaptive methods.

## 6. Momentum and acceleration

The basic gradient descent update can be slow because it repeatedly reacts only to the current gradient. Momentum adds memory: the update continues in a direction that has been useful before. A common form is

$$
v_{k+1}=\beta v_k - \eta \nabla f(x_k),
$$

$$
x_{k+1}=x_k+v_{k+1},
$$

where $v_k$ is a velocity-like term and $0\le \beta <1$ is the momentum parameter. If the gradient points in roughly the same direction over several steps, the velocity builds up and the method moves faster.

This is similar to a damped particle moving through a potential landscape. If the particle is rolling downhill, inertia helps it maintain motion rather than stopping at every step. Momentum is especially useful when the objective has a curved valley, where ordinary gradient descent can zigzag.

A related acceleration idea is Nesterov acceleration, where the gradient is evaluated at a look-ahead point rather than the current one. The update is often written as

$$
y_k = x_k + \beta v_k,
$$

$$
v_{k+1}=\beta v_k - \eta \nabla f(y_k),
$$

$$
x_{k+1}=x_k+v_{k+1}.
$$

This can improve convergence in practice, especially for smooth convex problems.

## 7. Stochastic and adaptive optimisation

In large-scale problems, evaluating the full gradient may be expensive. In machine learning, the objective is often a sum over many data points:

$$
f(x)=\frac{1}{n}\sum_{i=1}^n f_i(x).
$$

Instead of computing the full gradient, a stochastic gradient descent method uses a single data point or a small batch:

$$
\nabla f(x) \approx \nabla f_i(x).
$$

This makes each step cheaper, but noisier. The iterates may bounce around, so the step size is usually reduced over time. The trade-off is that stochastic methods can reach a useful solution much faster than full-batch gradient descent when the dataset is large.

Adaptive methods adjust the step size per coordinate. Two well-known examples are AdaGrad and Adam. In Adam, the update uses an exponentially weighted average of gradients and squared gradients. This helps the optimiser move more effectively when different variables require very different scales of adjustment. The key idea is that the algorithm learns a kind of local step size during the optimisation process.

These methods are widely used in data-driven engineering and control problems, but the same principle applies more generally: adapt the search step to the geometry of the landscape.

## 8. A brief introduction to second-order methods

Second-order methods use the Hessian matrix, which contains the second derivatives of the objective. The Hessian gives curvature information. A Newton step is based on the quadratic approximation

$$
f(x+\Delta x) \approx f(x)+\nabla f(x)^T\Delta x + \tfrac{1}{2}\Delta x^T H(x)\Delta x,
$$

and the minimiser of this local approximation satisfies

$$
H(x)\Delta x = -\nabla f(x).
$$

So the update is

$$
x_{k+1}=x_k - H(x_k)^{-1}\nabla f(x_k).
$$

This can converge much faster than first-order methods near a minimum because it uses curvature. However, it is more expensive because it requires solving a linear system involving the Hessian. In large problems, forming and inverting the Hessian may be impractical. That is why first-order methods remain attractive in many applications.

## 9. A complete Python example

Here is a small, executable example. The function represents a simple potential energy surface in two dimensions. The minimum is at $(1,-0.5)$.

```python
import numpy as np


def f(x):
    # f(x) = potential energy
    return (x[0] - 1.0) ** 2 + 2.0 * (x[1] + 0.5) ** 2


def grad_f(x):
    # Gradient of f(x)
    return np.array([2.0 * (x[0] - 1.0), 4.0 * (x[1] + 0.5)])


def gradient_descent(x0, eta=0.1, n_steps=50):
    x = x0.copy()
    history = [x.copy()]
    for _ in range(n_steps):
        g = grad_f(x)                 # Computes \nabla f(x)
        x = x - eta * g              # Implements x_{k+1} = x_k - eta * \nabla f(x_k)
        history.append(x.copy())
    return history


x0 = np.array([0.0, 0.0])
history = gradient_descent(x0, eta=0.1, n_steps=50)

print("Initial point:", x0)
print("Final point:", history[-1])
print("Objective value:", f(history[-1]))
```

The link between mathematics and code is direct:

- The function `f(x)` corresponds to the objective $f(x)$.
- The function `grad_f(x)` computes the gradient $\nabla f(x)$.
- The line `x = x - eta * g` implements the gradient descent update $x_{k+1}=x_k-\eta\nabla f(x_k)$.
- The loop performs repeated relaxation steps until the point approaches a minimum.

If you run this example, you should see the point move toward $(1,-0.5)$, where the gradient is zero and the objective is smallest.

## 10. Summary and intuition

Gradient descent is a practical method for finding minima by moving downhill in the landscape of an objective function. It is built around the gradient, which tells us the direction of steepest increase. The negative gradient therefore gives the direction of steepest decrease. The algorithm repeats this step until it reaches a region where the gradient is small.

The central ideas are:

- Unconstrained optimisation seeks the argument that minimises an objective.
- Stationary points satisfy $\nabla f(x)=0$.
- Smoothness makes the gradient meaningful.
- Convexity makes local minima global minima.
- Gradient descent uses $x_{k+1}=x_k-\eta\nabla f(x_k)$.
- Step size controls stability and speed.
- Momentum and adaptive methods improve behaviour on difficult landscapes.
- Second-order methods use curvature and can converge faster, but at greater computational cost.

For a mechanical engineer, the most useful interpretation is physical: optimisation is a numerical version of a system relaxing toward equilibrium.

## Exercises

1. Consider the one-dimensional function $f(x)=x^2$. Derive the gradient descent update and explain what happens when $\eta=0.5$ and when $\eta=2$.
2. For the function $f(x)=\frac{1}{2}(x-3)^2$, find the stationary point and explain why it is a minimum.
3. Suppose a function is convex and differentiable. Why does a stationary point automatically give a global minimum?
4. Modify the Python example so that the step size is reduced over time, for example by using $\eta_k=0.1/(1+k)$, and observe how the behaviour changes.
5. Explain the difference between gradient descent and momentum-based gradient descent in terms of how each method responds to a curved valley in the objective landscape.
