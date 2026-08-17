# Gradient descent and first-order optimisation for mechanical engineering students

Many problems in engineering can be expressed as a search for the lowest possible energy, the smallest error, or the most efficient design. In mechanics, this idea appears naturally. A mass in a conservative force field moves in a way that lowers its potential energy, and a system settles near a point of equilibrium. In optimisation, we use the same intuition in a more general form: we try to find a point where a function is as small as possible.

This chapter introduces the core ideas of first-order optimisation by linking them to the familiar language of potential energy, equilibrium and numerical relaxation. The goal is not to turn you into a specialist in convex optimisation, but to give you a working understanding of the main ideas behind gradient descent, why it works, and where it can fail.

## 1. Optimisation as a search for equilibrium

Suppose we have a smooth scalar function $f(x)$, where $x$ might be a single variable or a vector of variables. In unconstrained optimisation, we want to find a point $x^*$ such that

$$
 f(x^*) \le f(x) \quad \text{for all } x.
$$

This is a global minimum. In many practical problems, we are content with a local minimum, where the value is smallest in a neighbourhood of the point.

For a mechanical engineer, this is familiar. If the potential energy of a system is $U(q)$, then a stable equilibrium is often associated with a local minimum of $U$. A small disturbance causes the system to move back towards that minimum. The same principle underlies numerical optimisation: we start from an initial guess and repeatedly adjust it so that the objective function decreases.

For a differentiable function, a necessary condition for a stationary point is

$$
\nabla f(x^*) = 0.
$$

In one dimension, this becomes $f'(x^*)=0$. A stationary point can be a minimum, a maximum, or a saddle point. For example, $f(x)=x^3$ has a stationary point at $x=0$, but it is neither a local minimum nor a local maximum. By contrast, $f(x)=x^2$ has a stationary point at $x=0$, and it is a local and global minimum.

The connection to mechanics is therefore direct: equilibrium corresponds to a point where the first-order change in energy is zero. In a one-dimensional potential well, the force is proportional to the negative derivative, so equilibrium occurs where the derivative is zero.

## 2. Smoothness and convexity

The first-order methods discussed here rely on smoothness. A function is smooth if it is differentiable and its derivative changes in a controlled way. In practice, smoothness means that the function does not have sharp corners or jumps, so that local information, such as the gradient, is informative.

The gradient of a function $f:\mathbb{R}^n\to\mathbb{R}$ is the vector of first partial derivatives:

$$
\nabla f(x)=\left(\frac{\partial f}{\partial x_1}, \frac{\partial f}{\partial x_2}, \dots, \frac{\partial f}{\partial x_n}\right)^T.
$$

If the gradient is available, we can use it to determine the direction in which the function increases most rapidly. The gradient points uphill. Therefore, the negative gradient points downhill, which is the direction that should reduce the objective.

Convexity is another key idea. A function is convex if, for any two points $x$ and $y$ and any $0\le t\le 1$,

$$
 f(tx+(1-t)y) \le t f(x) + (1-t)f(y).
$$

Geometrically, the line segment joining two points on the graph lies above the graph. Convex functions have a particularly friendly structure: any local minimum is also a global minimum. That is why convexity is so important in optimisation theory. For a differentiable convex function, a stationary point satisfies

$$
\nabla f(x^*)=0 \quad \Longrightarrow \quad x^* \text{ is a global minimiser.}
$$

In engineering terms, convexity means that the energy landscape is well behaved: there are no misleading valleys that trap the search in the wrong place. Many practical problems are not globally convex, but local convexity often appears near a solution.

## 3. The gradient descent update

The central idea of gradient descent is simple. If we are at a point $x_k$, then the gradient tells us the direction of steepest increase. So we move in the opposite direction.

The update is

$$
 x_{k+1} = x_k - \eta_k \nabla f(x_k),
$$

where $\eta_k>0$ is a step size, or learning rate.

To see why this makes sense, consider the first-order Taylor approximation around $x_k$:

$$
 f(x_k + d) \approx f(x_k) + \nabla f(x_k)^T d.
$$

If we choose $d=-\eta\nabla f(x_k)$, then

$$
 f(x_k + d) \approx f(x_k) - \eta \|\nabla f(x_k)\|^2.
$$

As long as the gradient is non-zero and $\eta$ is small enough, this decreases the objective. The method is therefore a numerical relaxation procedure: each step moves the iterate closer to a lower-energy state.

In one dimension, the update becomes

$$
 x_{k+1} = x_k - \eta f'(x_k).
$$

This is exactly the same idea, just without the vector notation.

## 4. Step-size selection

Choosing the step size is the most important practical issue. If $\eta$ is too large, the method can overshoot and even diverge. If $\eta$ is too small, progress is painfully slow.

A fixed step size is the simplest choice. For example,

$$
 x_{k+1}=x_k-0.1\nabla f(x_k).
$$

This can work well when the function is well scaled and the gradient is not too large. In many cases, however, a better strategy is to adapt the step size during the iteration.

A common approach is backtracking line search. Start with an initial step size, try the step, and if the objective does not decrease sufficiently, reduce the step size. In symbols, one may accept the step only if

$$
 f(x_k - \eta_k\nabla f(x_k)) < f(x_k) - c\eta_k\|\nabla f(x_k)\|^2,
$$

for some constant $c\in(0,1)$. This condition ensures that the update gives a meaningful decrease.

The lesson is that gradient descent does not merely move downhill; it must move downhill enough to be useful.

## 5. Convergence behaviour

Gradient descent is reliable, but it is not instantaneous. In a well-behaved convex problem, the method usually converges gradually. For strongly convex functions, the error often decreases geometrically, meaning the distance to the minimum shrinks by a roughly constant factor each iteration. For general convex functions, the decrease can be slower and more irregular.

A useful way to think about it is this: gradient descent is a relaxation method. It does not jump to the answer; it slowly cools the system, like a mechanical structure settling into a minimum-energy configuration. The iterate moves through a sequence of states,

$$
 x_0, x_1, x_2, \dots,
$$

and the objective values typically decrease as the iteration proceeds.

The rate of convergence depends on the shape of the function. A narrow valley, for instance, causes slow progress because the gradient is steep in one direction and shallow in another. This is why the step size and scaling of the variables matter so much.

## 6. Momentum and acceleration

A basic weakness of gradient descent is that it can zig-zag when the objective is elongated or poorly scaled. Imagine moving down a narrow valley: the method may bounce from one side to the other, taking many small steps.

Momentum adds memory to the update. Instead of relying only on the current gradient, we carry a velocity term:

$$
 v_{k+1} = \beta v_k - \eta \nabla f(x_k),
$$

$$
 x_{k+1} = x_k + v_{k+1}.
$$

Here $0\le \beta <1$ controls how much previous direction is retained. If the update was moving in a useful direction, the momentum keeps it going. This often reduces oscillation and can accelerate convergence.

A related idea is Nesterov acceleration, where the update uses a look-ahead point. The intuition is that you should not only follow the current slope; you should anticipate the direction of the next step. These methods are more sophisticated, but they are still rooted in the same first-order idea: use gradient information to move downhill.

## 7. Stochastic and adaptive optimisation

So far we have assumed that the full gradient is available. That is often true in small problems and in many engineering calculations. But in large-scale problems, evaluating the full gradient may be expensive. Suppose the objective is a sum of many terms,

$$
 f(x)=\sum_{i=1}^m f_i(x).
$$

Then one may use stochastic gradient descent, where at each step only one random term is used:

$$
 g_k = \nabla f_{i_k}(x_k).
$$

The update becomes

$$
 x_{k+1}=x_k-\eta_k g_k.
$$

This is noisier than full-gradient descent, but it can be much cheaper per iteration. In machine learning and large-scale fitting problems, this trade-off is often worthwhile.

Adaptive methods such as Adam and Adagrad adjust the step size for each coordinate using past gradient information. The basic idea is that variables that have been large or noisy in the past receive different scaling. Such methods are very popular in practice because they often converge faster on difficult problems, although the behaviour can be less transparent than plain gradient descent.

## 8. A brief introduction to second-order methods

First-order methods use only the gradient. Second-order methods use curvature as well. The most important object is the Hessian matrix,

$$
 H(x)=\nabla^2 f(x),
$$

which contains second derivatives. A Newton step is

$$
 x_{k+1}=x_k - H(x_k)^{-1}\nabla f(x_k).
$$

This is powerful because it uses information about the local shape of the function. Near a minimum of a smooth function, the Hessian captures how sharply the function curves. In a quadratic problem, Newton’s method can reach the minimiser in one step if the Hessian is well conditioned. In practice, second-order methods are more accurate and often faster, but they cost more because the Hessian and its inverse are expensive to compute.

That is why first-order methods remain important. They are simple, cheap, and often sufficient for engineering problems where the exact optimum is not required and the objective is smooth enough.

## 9. Executable Python example

Here is a very small Python implementation of gradient descent for the simple quadratic function

$$
 f(x)=\tfrac{1}{2}(x-3)^2.
$$

The gradient is

$$
 \nabla f(x)=x-3.
$$

The code below uses the update

$$
 x_{k+1}=x_k-\eta(x_k-3).
$$

```python
def objective(x):
    return 0.5 * (x - 3.0) ** 2


def gradient(x):
    return x - 3.0


def gradient_descent(x0, learning_rate, steps):
    x = x0
    history = []
    for k in range(steps):
        g = gradient(x)              # g = ∇f(x)
        x = x - learning_rate * g   # x_{k+1} = x_k - η∇f(x_k)
        history.append((k + 1, x, objective(x)))
    return x, history


x_star, history = gradient_descent(6.0, 0.2, 20)
print("Estimated minimiser:", round(x_star, 6))
print("Objective value:", round(objective(x_star), 6))
for step, x, value in history[:5]:
    print(f"step {step}: x={x:.4f}, f(x)={value:.4f}")
```

The link between the mathematics and the code is explicit. The function `gradient(x)` implements the derivative $x-3$. The line `x = x - learning_rate * g` is the gradient descent update. The loop repeats the relaxation process until the point moves close to the minimiser. In this example, the minimum is at $x=3$, and the method should converge to that value.

## Exercises

1. For $f(x)=x^2+4x+1$, compute the gradient and find the stationary point.
2. Consider $f(x)=x^2$. What happens to the gradient descent update for a step size of $\eta=1.5$? Explain why this is problematic.
3. Show that $f(x)=x^2$ is convex by using the definition of convexity or the second derivative test.
4. In a mechanical-energy setting, explain why a stationary point of the potential energy corresponds to an equilibrium point.
5. Compare gradient descent and momentum on a narrow valley-shaped function. Which method is likely to be more stable, and why?

Gradient descent is not just a numerical trick. It is a direct translation of the physical idea that a system can move towards a lower-energy state by following the local slope. That is why it is so useful in engineering, science and optimisation more broadly. The key message is that first-order methods are simple, interpretable, and surprisingly powerful when the objective is smooth and the step size is chosen carefully.
