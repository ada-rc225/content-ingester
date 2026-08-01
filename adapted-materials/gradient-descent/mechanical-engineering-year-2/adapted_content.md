# Gradient Descent for Mechanical Engineering Year 2

## 1. Potential Energy, Equilibrium, and the Optimization Problem

In many mechanical engineering problems, a configuration of a system is stable when its potential energy is as low as possible.
A mass in a gravitational field, a spring at rest, or a frame sitting in a minimum-energy shape are all examples of equilibrium found by minimizing potential energy.

We can express this as a mathematical problem:

$$\min_{x \in \mathbb{R}^d} f(x)$$

Here, $x$ represents the coordinates of the mechanical system, and $f(x)$ represents its potential energy.
The goal is to find the configuration $x$ where the system is in equilibrium with minimal stored energy.

### Stationary Equilibrium and Forces

If $x^*$ is a local minimizer of $f$ and $f$ is differentiable at $x^*$, then the first-order necessary condition is:

$$\nabla f(x^*) = 0$$

In physical terms, the gradient of potential energy is the force vector. When the gradient is zero, the net conservative force on the system is zero, which is the condition for static equilibrium.

### Second-Order Conditions and Stability

If $f$ is twice continuously differentiable ($f \in C^2$), then we can inspect the Hessian matrix $\nabla^2 f(x^*)$.

- Necessary condition: If $x^*$ is a local minimizer, then $\nabla f(x^*) = 0$ and $\nabla^2 f(x^*) \succeq 0$.
- Sufficient condition: If $\nabla f(x^*) = 0$ and $\nabla^2 f(x^*) \succ 0$, then $x^*$ is a strict local minimizer.

In engineering terms, positive definiteness of the Hessian means the energy surface is locally bowl-shaped, so small displacements increase energy and the equilibrium is stable.

## 2. Gradient Descent as Numerical Relaxation

Gradient descent is a simple way to move a mechanical system down the energy surface toward equilibrium.
The update rule is:

$$x_{k+1} = x_k - \alpha_k \nabla f(x_k), \quad k = 0, 1, 2, \dots$$

Here, $x_k$ is the current configuration, $\nabla f(x_k)$ is the force vector, and $\alpha_k > 0$ is a step size that controls how far we move in the downhill direction.

Think of this as a numerical relaxation method: at each step, the system is pushed in the direction of greatest decrease in potential energy.

### Interpreting the Update

- If $\alpha_k$ is too small, the system relaxes slowly.
- If $\alpha_k$ is too large, the system can overshoot the minimum and oscillate.

This is similar to choosing a time step in an explicit dynamic simulation: the step size must be chosen to keep the iteration stable.

## 3. Step Size, Stability, and Energy Decrease

To explain why certain step sizes work, we use a mathematical condition on the energy surface.

### $L$-Smoothness

A continuously differentiable energy function $f: \mathbb{R}^d \to \mathbb{R}$ is $L$-smooth ($L > 0$) if:

$$\|\nabla f(x) - \nabla f(y)\| \le L \|x - y\|, \quad \forall x, y \in \mathbb{R}^d$$

This means the gradient does not change too rapidly as the configuration moves.
For a mechanical system, it bounds how quickly the force can change with position.

### Descent Lemma

If $f$ is $L$-smooth, then for any configurations $x$ and $y$:

$$f(y) \le f(x) + \langle \nabla f(x), y - x \rangle + \frac{L}{2} \|y - x\|^2$$

This inequality gives a quadratic upper bound on the change in energy, and it is useful to show that a gradient descent step reduces energy when the step size is chosen correctly.

### Practical Step Size Rule

A safe constant step size is:

$$\alpha_k = \frac{1}{L}$$

Under this choice, the energy decreases and the iteration is stable for $L$-smooth functions.

## 4. Energy Wells, Convexity, and Strong Stability

### Convexity

A differentiable function $f$ is convex if for all $x, y \in \mathbb{R}^d$:

$$f(y) \ge f(x) + \langle \nabla f(x), y - x \rangle$$

Convexity means the energy surface lies above every tangent plane. In a convex energy well, any stationary point is a global minimum.

### Strong Convexity

A differentiable function $f$ is $\mu$-strongly convex ($\mu > 0$) if for all $x, y \in \mathbb{R}^d$:

$$f(y) \ge f(x) + \langle \nabla f(x), y - x \rangle + \frac{\mu}{2} \|y - x\|^2$$

This stronger condition means the energy surface has a uniformly positive curvature, like a well with a guaranteed steepness.

If $f \in C^2$, then strong convexity corresponds to:

- $\nabla^2 f(x) \succeq \mu I$ for all $x$,
- and $L$-smoothness corresponds to $\nabla^2 f(x) \preceq L I$ for all $x$.

The condition number is:

$$\kappa = \frac{L}{\mu} \ge 1$$

In mechanical terms, a large condition number means the energy well is much stiffer in some directions than in others.

## 5. Convergence of Gradient Descent

### Energy Decrease for Convex, Smooth Energy

If $f$ is $L$-smooth and convex, and $x^*$ is a global minimizer, then with constant step size $\alpha_k = 1/L$ the iterates satisfy:

$$f(x_k) - f(x^*) \le \frac{L \|x_0 - x^*\|^2}{2k}$$

This means the energy difference decreases like $O(1/k)$ as the iteration proceeds.
For an engineering student, this quantifies how the relaxation method improves the estimate of the equilibrium configuration.

### Faster Convergence for Strongly Convex Energy

If the energy is also $\mu$-strongly convex, gradient descent can converge much faster.
With step size $\alpha = 1/L$:

$$f(x_k) - f(x^*) \le \left( 1 - \frac{\mu}{L} \right)^k (f(x_0) - f(x^*))$$

This is a linear convergence rate: the error shrinks by a constant factor each step.
In mechanical terms, a uniformly curved energy well leads to predictable and stable relaxation behavior.

## 6. A Quadratic Energy Example and Python Implementation

A common mechanical example is a quadratic potential energy:

$$f(x) = \frac{1}{2} x^T A x$$

where $A$ is a symmetric positive definite matrix.
For this function:

$$\nabla f(x) = A x$$

and the gradient descent update becomes:

$$x_{k+1} = x_k - \alpha A x_k = (I - \alpha A) x_k$$

This is analogous to relaxing a linear spring system or a small-displacement finite element model.

### Python Code Example

```python
import numpy as np

A = np.array([[5.0, 1.0], [1.0, 3.0]])

def f(x):
    return 0.5 * x.T @ A @ x

def grad_f(x):
    return A @ x

x = np.array([2.0, -1.0])
L = np.linalg.eigvalsh(A).max()
alpha = 1.0 / L

for k in range(20):
    x = x - alpha * grad_f(x)
    print(k, f(x), x)
```

This simple code demonstrates the core algorithm: evaluate the gradient, take a step downhill, and repeat.

## 7. Momentum and Accelerated Relaxation

### Polyak's Heavy-Ball Method

To improve relaxation on stiff systems, we can add momentum:

$$x_{k+1} = x_k - \alpha \nabla f(x_k) + \beta (x_k - x_{k-1})$$

The term $\beta (x_k - x_{k-1})$ carries the previous displacement forward, which can help move through shallow directions more quickly.

For a quadratic energy with eigenvalues $\mu \le \dots \le L$, the optimal parameters are:

$$\alpha^* = \frac{4}{(\sqrt{L} + \sqrt{\mu})^2}, \quad \nabla^* = \left( \frac{\sqrt{\kappa} - 1}{\sqrt{\kappa} + 1} \right)^2$$

This improves the effective convergence factor from $1 - O(1/\kappa)$ to $1 - O(1/\sqrt{\kappa})$.

### Nesterov's Accelerated Gradient

Nesterov acceleration uses a look-ahead point:

$$y_k = x_k + \beta_k (x_k - x_{k-1})$$
$$x_{k+1} = y_k - \alpha \nabla f(y_k)$$

With $\alpha = 1/L$ and

$$\lambda_0 = 0, \quad \lambda_k = \frac{1 + \sqrt{1 + 4\lambda_{k-1}^2}}{2}, \quad \beta_k = \frac{\lambda_{k-1} - 1}{\lambda_k},$$

Nesterov's method achieves:

$$f(x_k) - f(x^*) \le \frac{2 L \|x_0 - x^*\|^2}{(k + 1)^2}$$

This is a faster $O(1/k^2)$ decrease in energy for smooth convex functions.

In physical language, the method uses a predictive relaxation step before evaluating the force.

## 8. Advanced Tools: Adaptive and Second-Order Methods

### Adaptive Methods

For more complex or noisy systems, it can be useful to adjust the step size using gradient history.

- AdaGrad accumulates squared gradient components.
- RMSProp uses an exponential moving average of squared gradients.
- Adam combines momentum with adaptive scaling.

These methods are most useful when the system has components that vary in stiffness or when the gradient is noisy.

### Newton's Method and Quasi-Newton Methods

Newton's method uses a second-order approximation of the energy:

$$f(x_k + p) \approx f(x_k) + \nabla f(x_k)^T p + \frac{1}{2} p^T \nabla^2 f(x_k) p$$

Setting the derivative with respect to $p$ to zero gives:

$$x_{k+1} = x_k - [\nabla^2 f(x_k)]^{-1} \nabla f(x_k)$$

This method can converge very quickly when the Hessian is available and positive definite.

Quasi-Newton methods such as BFGS approximate the Hessian using gradient differences:

$$y_k = \nabla f(x_{k+1}) - \nabla f(x_k), \quad s_k = x_{k+1} - x_k$$
$$B_{k+1} s_k = y_k$$

These are useful when second-order information is too expensive to compute exactly.

## 9. Exercises

1. Consider a one-dimensional spring with potential energy $f(x) = \frac{1}{2} k x^2$.
   - Write the gradient descent update.
   - Explain why $\nabla f(x) = k x$ is the force.
   - What is the stable equilibrium?

2. For the quadratic energy $f(x) = \frac{1}{2} x^T A x$ with $A$ symmetric positive definite:
   - Show that $\nabla f(x) = A x$.
   - Explain how the condition number $\kappa = L/\mu$ relates to stiffness in different directions.

3. Use Python to implement gradient descent for the quadratic example in Section 6.
   - Plot the energy $f(x_k)$ over iterations.
   - Try a step size $\alpha = 1/L$ and a larger step size. Describe what happens.

4. Explain in your own words why strong convexity gives a faster convergence rate than simple convexity.

5. Describe the mechanical analogy for the Heavy-Ball update and for Nesterov acceleration.

---

This lesson connects the core mathematics of gradient descent with mechanical engineering concepts of potential energy, equilibrium, and numerical relaxation.
