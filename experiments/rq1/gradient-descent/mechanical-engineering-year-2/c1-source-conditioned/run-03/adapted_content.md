# Gradient Descent as a Mechanical Relaxation Process

## A practical introduction for second-year mechanical engineering students

Many engineering problems can be viewed as a search for a state of lowest energy. A mass on a spring, a beam under load, or a mechanism settling into a stable position all share the same basic idea: the system moves in a direction that reduces its potential energy until it reaches equilibrium.

The same mathematical idea appears in optimization. We often want to find a point $x$ that makes a function $f(x)$ as small as possible. In this setting, $f$ is treated as an energy-like quantity, and gradient descent is a numerical method for moving downhill toward a minimum.

This note keeps the mathematical definitions and update rules from the source material, but rephrases them in a way that is more natural for mechanical engineering students.

---

## 1. From mechanics to optimization

In mechanics, a system is often described by a potential energy function $U(q)$, where $q$ is a generalized coordinate such as displacement, angle, or position. The force is related to the gradient of the potential energy:

$$
F(q) = -\nabla U(q)
$$

A system is at equilibrium when the net force is zero:

$$
\nabla U(q^*) = 0
$$

This is the same mathematical condition that appears in optimization. If we define a scalar objective function $f(x)$ as an energy-like function, then a minimizer satisfies

$$
\min_{x \in \mathbb{R}^d} f(x)
$$

and a stationary point $x^*$ satisfies

$$
\nabla f(x^*) = 0.
$$

So, in both mechanics and optimization, the problem is to find a point where the “driving tendency” disappears.

### First-order necessary condition (FONC)

If $x^*$ is a local minimizer of $f$ and $f$ is differentiable at $x^*$, then:

$$
\nabla f(x^*) = 0.
$$

In mechanical language, this means the slope of the energy landscape is zero at equilibrium.

### Second-order conditions

If $f \in C^2$:

- Necessary: if $x^*$ is a local minimizer, then $\nabla f(x^*) = 0$ and the Hessian matrix $\nabla^2 f(x^*) \succeq 0$ (positive semi-definite).
- Sufficient: if $\nabla f(x^*) = 0$ and $\nabla^2 f(x^*) \succ 0$ (positive definite), then $x^*$ is a strict local minimizer.

A positive definite Hessian means the energy surface curves upward in every direction near the minimum, so the point is genuinely stable.

---

## 2. Why smoothness and convexity matter

A numerical method can only be reliable if the underlying energy landscape is not too irregular. In engineering terms, we want the energy function to behave smoothly enough that the force changes gradually as the system moves.

### 2.1 $L$-smoothness

A continuously differentiable function $f: \mathbb{R}^d \to \mathbb{R}$ is $L$-smooth ($L > 0$) if:

$$
\|\nabla f(x) - \nabla f(y)\| \le L \|x - y\|, \quad \forall x, y \in \mathbb{R}^d.
$$

The constant $L$ measures how quickly the slope can change. A larger $L$ means the energy surface can be steeper and more curved.

A useful consequence is the descent lemma. If $f$ is $L$-smooth, then for all $x, y \in \mathbb{R}^d$:

$$
f(y) \le f(x) + \langle \nabla f(x), y - x \rangle + \frac{L}{2} \|y - x\|^2.
$$

This says that, near any point $x$, the function is bounded above by a quadratic model. In mechanics, this is like replacing a complicated potential by a local parabola.

### 2.2 Convexity and strong convexity

A differentiable function $f: \mathbb{R}^d \to \mathbb{R}$ is convex if for all $x, y \in \mathbb{R}^d$:

$$
f(y) \ge f(x) + \langle \nabla f(x), y - x \rangle.
$$

This means the function lies above all of its tangent lines. For a mechanical engineer, a convex energy function has a single bowl-shaped landscape with no local traps.

A differentiable function is $\mu$-strongly convex ($\mu > 0$) if for all $x, y \in \mathbb{R}^d$:

$$
f(y) \ge f(x) + \langle \nabla f(x), y - x \rangle + \frac{\mu}{2} \|y - x\|^2.
$$

This is a stronger statement: the energy landscape is not just bowl-shaped, but curved enough that the minimum is well defined and the system settles reliably.

#### Characterization by second derivatives

If $f \in C^2$:

- $f$ is $L$-smooth if and only if $\nabla^2 f(x) \preceq L I$ for all $x$.
- $f$ is $\mu$-strongly convex if and only if $\nabla^2 f(x) \succeq \mu I$ for all $x$.
- The condition number is defined as

$$
\kappa = \frac{L}{\mu} \ge 1.
$$

A large condition number means the energy landscape is long and narrow, like a shallow valley, and the descent process can be slow.

---

## 3. Gradient descent as a relaxation method

The basic gradient descent iteration is:

$$
x_{k+1} = x_k - \alpha_k \nabla f(x_k), \quad k = 0, 1, 2, \dots
$$

Here $\alpha_k > 0$ is the step size, or learning rate. The method moves in the direction opposite to the gradient, which is the direction of steepest decrease in the objective.

In mechanical terms, the gradient plays the role of a force-like quantity. The update says: move a little in the direction that reduces energy most rapidly.

This is exactly what a relaxing system does. If a structure is displaced from equilibrium, the restoring force pushes it back toward the lower-energy state.

### The idea in one sentence

Gradient descent is numerical relaxation: repeatedly take a small step downhill until the system reaches a point where the gradient is nearly zero.

---

## 4. Choosing the step size

The step size controls how aggressively the system moves.

### 4.1 Constant step size

A simple choice is

$$
\alpha_k = \alpha.
$$

Typical choices are $\alpha = 1/L$ or $\alpha \in (0, 2/L)$.

### 4.2 Exact line search

One can select the step size by solving

$$
\alpha_k = \arg\min_{\alpha > 0} f(x_k - \alpha \nabla f(x_k)).
$$

This means: at each step, choose the best distance to move along the downhill direction.

### 4.3 Backtracking line search

In practice, a common approach is backtracking. Choose an initial step size $\bar{\alpha}$ and reduce it by a factor $\eta \in (0,1)$ until the Armijo-Goldstein condition is satisfied:

$$
f(x_k - \alpha_k \nabla f(x_k)) \le f(x_k) - c \alpha_k \|\nabla f(x_k)\|^2,
\quad c \in (0, 1/2).
$$

The condition ensures that the step actually reduces the energy enough to be worthwhile.

---

## 5. Convergence ideas

Although the full proof is not the focus here, the key conclusions are important.

### For $L$-smooth convex functions

If $f$ is $L$-smooth and convex, and $x^*$ is a global minimizer, then with a constant step size $\alpha_k = 1/L$, the sequence satisfies

$$
f(x_k) - f(x^*) \le \frac{L \|x_0 - x^*\|^2}{2k}.
$$

This is an $O(1/k)$ rate: the objective gap shrinks roughly like $1/k$.

### For $\mu$-strongly convex functions

If $f$ is $L$-smooth and $\mu$-strongly convex, then with $\alpha = 2/(L+\mu)$, gradient descent achieves linear convergence:

$$
\|x_k - x^*\|^2 \le \left( \frac{\kappa - 1}{\kappa + 1} \right)^{2k} \|x_0 - x^*\|^2,
$$

where $\kappa = L/\mu$.

With $\alpha = 1/L$, one also has

$$
f(x_k) - f(x^*) \le \left( 1 - \frac{\mu}{L} \right)^k (f(x_0) - f(x^*)).
$$

In words, strong convexity gives a more reliable and faster approach to equilibrium because the energy landscape has a clear minimum.

---

## 6. A simple Python example

The following example minimizes a one-dimensional energy function

$$
f(x) = \frac{1}{2}(x-3)^2.
$$

This corresponds to a quadratic potential with a unique minimum at $x=3$. The gradient is

$$
\nabla f(x) = x - 3.
$$

The gradient descent update becomes

$$
x_{k+1} = x_k - \alpha (x_k - 3).
$$

Here is an executable Python script:

```python
import numpy as np


def f(x):
    return 0.5 * (x - 3) ** 2


def grad_f(x):
    return x - 3

x = 8.0
alpha = 0.2

for k in range(10):
    g = grad_f(x)
    x = x - alpha * g
    print(f"k={k:2d}, x={x:.4f}, f(x)={f(x):.4f}")
```

What happens here? Starting from $x=8$, the algorithm repeatedly moves toward the minimum at $x=3$. Each iteration reduces the energy, and the system relaxes toward equilibrium.

If you change the initial value to something else, such as $x_0 = -2$, the method still converges to the same minimum.

---

## 7. Why this matters in engineering

The same idea appears in many engineering contexts:

- A spring-mass system settles toward a minimum of potential energy.
- A control system may adjust parameters to reduce an error function.
- A numerical model may seek a state that minimizes a residual or cost.

In all of these cases, the method is not magic; it is a systematic way of moving downhill in an energy landscape.

The main difficulty is that real engineering problems can be complicated, non-convex, and noisy. A simple gradient descent method may converge slowly or get stuck in poor local minima. That is why more advanced methods exist, but the basic idea remains the same: use information from the gradient to move toward lower energy.

---

## 8. Exercises

1. Spring potential and equilibrium
   - A linear spring has potential energy
     $$
     U(x) = \frac{1}{2}kx^2.
     $$
   - Derive the force using $F(x) = -\nabla U(x)$.
   - Explain why the equilibrium point is at $x=0$.

2. Quadratic energy and gradient descent
   - Consider the function
     $$
     f(x) = \frac{1}{2}(x-3)^2.
     $$
   - Compute $\nabla f(x)$.
   - Write the gradient descent update for a constant step size $\alpha$.
   - What is the equilibrium point of this system?

3. Step-size sensitivity
   - For the same function, discuss what happens if $\alpha$ is too large.
   - Why might the method overshoot the minimum?
   - What is the role of the gradient in this process?

4. Python implementation
   - Write a short Python script that applies gradient descent to
     $$
     f(x) = \frac{1}{2}(x-2)^2 + 0.1x.
     $$
   - Plot the values of $x_k$ over iterations.
   - Explain why the method converges to a point where $\nabla f(x)=0$.

5. Convexity and stability
   - Explain, in your own words, why convexity is useful in optimization.
   - Why does a strongly convex energy function tend to give a more stable and predictable relaxation process?

---

## 9. Summary

Gradient descent is a numerical method for finding a point where the gradient is zero. In mechanics, that is the same as finding equilibrium where the restoring force vanishes. The key ideas are:

- minimize an energy-like function $f(x)$;
- use the gradient to move in the direction of steepest descent;
- choose the step size carefully to avoid overshooting;
- rely on smoothness and convexity to make the descent process reliable.

In this way, optimization becomes a modern, computational version of relaxation toward equilibrium.
