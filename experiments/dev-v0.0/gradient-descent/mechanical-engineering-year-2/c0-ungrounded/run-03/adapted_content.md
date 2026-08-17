# Gradient descent through the lens of potential energy, equilibrium and relaxation

## What this lesson is really about

Gradient descent is often introduced as an abstract algorithm for minimising a function. For mechanical engineering students, it is much easier to understand if you see it as a way of finding equilibrium in a physical system.

A common idea in mechanics is that a system tends to move toward lower potential energy. If we can describe a system by an energy function, then the force acting on it is related to the slope of that energy surface. In other words:

- energy tells us what is “cheap” or “expensive” for the system;
- the gradient tells us which way the system should move to lower that energy;
- repeated movement downhill leads to a state of equilibrium.

That is the core connection between mechanics and optimisation.

---

## Learning goals

By the end of this lesson, you should be able to:

- explain how potential energy and force are linked;
- interpret equilibrium as a point where the gradient vanishes;
- describe gradient descent as a numerical relaxation process;
- implement a simple gradient descent algorithm in Python;
- recognise why step size matters.

---

## 1. From force to energy

In mechanics, a conservative force can be written as the negative gradient of a potential energy function.

If the potential energy is $U(x)$, then

$$
F(x) = -\frac{dU}{dx}
$$

in one dimension, and in multiple dimensions,

$$
\mathbf{F}(\mathbf{x}) = -\nabla U(\mathbf{x}).
$$

The minus sign matters. A force points in the direction that reduces potential energy.

### Example: a simple spring

For a spring with stiffness $k$, the potential energy is

$$
U(x) = \frac{1}{2}kx^2.
$$

Its derivative is

$$
\frac{dU}{dx} = kx,
$$

so the force is

$$
F(x) = -kx.
$$

This is the familiar restoring force: if the spring is stretched or compressed, the force pulls the system back toward the equilibrium position $x=0$.

This is a first example of a very important idea:

- the system moves to reduce energy;
- the equilibrium point is where the force becomes zero.

---

## 2. Equilibrium as a stationary point

An equilibrium point is where the system experiences no net force. In terms of energy, this means the gradient is zero:

$$
\nabla U(\mathbf{x}) = \mathbf{0}.
$$

So finding equilibrium is the same as finding a stationary point of the potential energy function.

### Why “stationary” matters

A stationary point is not automatically a stable equilibrium. Consider a function with a maximum or a saddle point:

- at a maximum, the system is unstable;
- at a minimum, the system is stable;
- at a saddle point, the system may move away in some directions and toward in others.

For a one-dimensional function, the second derivative tells us the type of point:

- if $U''(x) > 0$, the point is a local minimum and therefore stable;
- if $U''(x) < 0$, the point is a local maximum and therefore unstable;
- if $U''(x) = 0$, the test is inconclusive.

For a multidimensional system, the second derivative is replaced by the Hessian matrix. A local minimum corresponds to a positive definite Hessian.

### A mechanical interpretation

Imagine a ball rolling on a curved surface. The surface height is the potential energy. The ball rolls downhill because gravity tends to reduce its potential energy. Eventually it comes to rest near a valley, which is a local minimum of the energy surface.

That is exactly what gradient descent is doing in a mathematical setting.

---

## 3. Why gradient descent is a numerical relaxation method

In many engineering problems, the exact equilibrium point is difficult to find analytically. That is where numerical methods come in.

The basic idea is simple:

1. start from an initial guess;
2. compute the gradient of the energy function;
3. move in the direction of steepest descent;
4. repeat until the change becomes small.

For a scalar function $U(x)$, the update rule is

$$
x_{k+1} = x_k - \eta \, U'(x_k),
$$

where $\eta > 0$ is a step size, sometimes called the learning rate.

The term “gradient descent” comes from the fact that the update moves opposite to the gradient. The term “relaxation” comes from the idea that the system gradually settles toward a lower-energy state.

### Why does this work?

Suppose we are at a point $x_k$. The derivative tells us the local slope. If the slope is positive, then moving to the left lowers the function. If the slope is negative, then moving to the right lowers the function.

So the update rule

$$
x_{k+1} = x_k - \eta U'(x_k)
$$

moves us downhill.

For a small step size $\eta$, this behaves like a discrete version of the continuous motion toward lower energy.

---

## 4. A simple worked example

Take the quadratic energy function

$$
U(x) = x^2.
$$

Then

$$
U'(x) = 2x.
$$

The update rule becomes

$$
x_{k+1} = x_k - \eta (2x_k).
$$

If we start from $x_0 = 3$ and choose $\eta = 0.1$, then

$$
x_1 = 3 - 0.1(2\cdot 3) = 2.4,
$$

$$
x_2 = 2.4 - 0.1(2\cdot 2.4) = 1.92,
$$

$$
x_3 = 1.92 - 0.1(2\cdot 1.92) = 1.536.
$$

The values are getting closer to $0$, which is the minimum of the energy function. The system is relaxing toward equilibrium.

### What if the step size is too large?

If $\eta$ is too large, the method can overshoot and may even diverge. For example, with $U(x)=x^2$ and $\eta=1$, the update becomes

$$
x_{k+1} = x_k - 2x_k = -x_k,
$$

which oscillates rather than converging.

So step size matters:

- small $\eta$: slow but stable;
- large $\eta$: faster but may overshoot;
- very large $\eta$: may fail to converge.

This is the same kind of issue as choosing a damping coefficient in a mechanical system.

---

## 5. The algorithmic meaning of gradient descent

In general, we are trying to solve

$$
\min_{\mathbf{x}} f(\mathbf{x}),
$$

where $f$ could represent an energy, a cost, or a loss function. The update rule is

$$
\mathbf{x}_{k+1} = \mathbf{x}_k - \eta \, \nabla f(\mathbf{x}_k).
$$

This tells us that each iteration moves in the direction that most rapidly decreases the function value.

### Pseudocode

```text
Choose an initial guess x0
Choose a step size eta
Repeat for many iterations:
    compute gradient g = gradient of f at x
    update x = x - eta * g
    stop when the gradient is very small
```

### Important practical points

- The gradient is zero at a stationary point, so the method stops there.
- Gradient descent usually finds a local minimum, not necessarily the global minimum.
- The starting point matters.
- The function may have many valleys, and the algorithm may settle in one of them.

This is why optimisation is not just about algebra; it is also about geometry and iteration.

---

## 6. A Python example: relaxing toward a minimum

The following script uses plain Python to minimise a two-variable energy function:

$$
U(x,y) = (x-1)^2 + 2(y+0.5)^2.
$$

This has a single minimum at $(1,-0.5)$.

```python
def energy(x, y):
    return (x - 1) ** 2 + 2 * (y + 0.5) ** 2


def gradient(x, y):
    # Partial derivatives of the energy function
    dU_dx = 2 * (x - 1)
    dU_dy = 4 * (y + 0.5)
    return dU_dx, dU_dy


def gradient_descent(x0, y0, learning_rate=0.1, steps=20):
    x, y = x0, y0
    print("Initial point:", (x, y))
    print("Initial energy:", energy(x, y))

    for i in range(steps):
        dx, dy = gradient(x, y)
        x = x - learning_rate * dx
        y = y - learning_rate * dy
        print(f"Step {i+1}: x={x:.4f}, y={y:.4f}, energy={energy(x, y):.4f}")

    print("Final point:", (x, y))
    print("Final energy:", energy(x, y))


if __name__ == "__main__":
    gradient_descent(3.0, -2.0, learning_rate=0.1, steps=20)
```

### What to expect

The values of $x$ and $y$ should move toward $1$ and $-0.5$, respectively. The energy should decrease at each step until it becomes very small.

You can change the starting point and the learning rate to see what happens.

### A useful experiment

Try these variations:

- start from $(3, -2)$ with learning rate $0.1$;
- start from $(3, -2)$ with learning rate $0.3$;
- start from $(10, 10)$ with learning rate $0.1$.

You will see that the algorithm behaves differently in each case.

---

## 7. Why this matters in engineering

The connection between gradient descent and mechanics is not just a teaching device. It appears in many engineering contexts:

- finite element solvers often relax toward equilibrium;
- control systems use optimisation to reduce tracking error;
- structural mechanics uses energy minimisation to find stable states;
- machine learning uses gradient-based algorithms to reduce loss functions.

In all of these cases, the same core idea appears: update the state in the direction that lowers an objective until the system settles into a useful balance.

---

## 8. Exercises

### Exercise 1: a one-dimensional energy function

Consider the potential energy

$$
U(x) = x^2 + 4x + 1.
$$

1. Find the equilibrium point by solving $U'(x)=0$.
2. Determine whether that point is a minimum or maximum.
3. If you start from $x_0 = 3$ and use $\eta = 0.1$, compute the first three gradient descent updates.

### Exercise 2: a nonlinear potential

Consider

$$
U(x) = \frac{1}{2}(x^2 - 1)^2.
$$

1. Compute the derivative $U'(x)$.
2. Find the equilibrium points.
3. Explain which of these are stable and which are unstable.

### Exercise 3: change the step size

Use the Python example above and try the following learning rates:

- $0.01$
- $0.1$
- $0.3$
- $1.0$

Describe what happens in each case.

### Exercise 4: a two-variable energy function

Consider

$$
U(x,y) = x^2 + y^2 + xy.
$$

1. Compute the gradient $\nabla U(x,y)$.
2. Write the gradient descent update rule for this function.
3. Explain what the equilibrium point should be.

---

## Summary

Gradient descent can be understood as a numerical way of finding equilibrium by moving downhill in an energy landscape.

The key ideas are:

- potential energy tells us how “expensive” a state is;
- the gradient tells us the direction of steepest change;
- moving opposite to the gradient lowers the energy;
- repeated updates relax the system toward a minimum;
- the step size controls how quickly and how safely this happens.

That is why gradient descent is not just a computational trick. It is a natural mathematical language for describing relaxation, equilibrium and stability.
