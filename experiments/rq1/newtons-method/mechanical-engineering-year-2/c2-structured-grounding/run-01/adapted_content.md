# Newton's Method for Nonlinear Spring Equilibrium

Mechanical engineers often meet nonlinear behaviour when a component is loaded beyond the small-deformation range. A simple coil spring is a good example: the force required to stretch it is not always proportional to the displacement, so the equilibrium position is found by solving a nonlinear equation rather than using a straight-line formula.

In this lesson, we treat the problem as a force-balance equation. The unknown is the displacement $x$ that makes the internal spring force and the applied load agree. That is exactly the kind of equation Newton's method is designed to solve.

<!-- section: SEC-01 -->
## From a nonlinear spring to a root-finding problem

Suppose a spring is attached to a load and we want the displacement $x$ at which the spring force balances the applied load. If the spring force is written as $g(x)$ and the applied load is a known value $L$, then the equilibrium condition is

$$
 g(x)=L.
$$

It is often more convenient to rearrange this as a residual equation

$$
 f(x)=g(x)-L=0.
$$

The quantity $f(x)$ is the force imbalance. A root $r$ satisfies

$$
f(r)=0,
$$
so the displacement $r$ makes the spring force exactly equal to the load. In mechanical terms, the root is the displacement at which the system is in static equilibrium.

The same idea appears in many engineering calculations. A nonlinear constitutive law, a geometric constraint, or an implicit design relation can all be written as a residual equation. The numerical task is then to find the displacement or state that makes the residual vanish.

<!-- section: SEC-02 -->
## Deriving Newton's step from a tangent line

Newton's method begins with a guess $x_k$ and replaces the nonlinear residual by a line tangent to the curve at $x_k$. If the residual is smooth, then near $x_k$

$$
 f(x)
 \approx
 f(x_k)+f'(x_k)(x-x_k).
$$

We want the next iterate to make this linear approximation equal to zero. Setting the approximation to zero gives

$$
0=f(x_k)+f'(x_k)(x_{k+1}-x_k).
$$

Solving for $x_{k+1}$ yields

$$
 x_{k+1}=x_k-rac{f(x_k)}{f'(x_k)}.
$$

This is the Newton update. In the spring problem, $f(x_k)$ is the current force imbalance and $f'(x_k)$ is the local slope of the force-displacement relation. The method moves to the point where the tangent line predicts zero imbalance.

A root is called simple when

$$
 f'(r)\ne0.
$$

That condition matters because the Newton step uses the derivative in the denominator. If the derivative is zero or nearly zero at the current iterate, the step becomes undefined or extremely large.

<!-- section: SEC-03 -->
## When the method is locally reliable

Newton's method is a local method. Its strongest guarantee applies when the initial guess is already close to a suitable root and the residual behaves well near that point. If $r$ is a simple root of $f$, then the method is locally well behaved and converges quadratically.

If we define the error at iteration $k$ by

$$
 e_k=x_k-r,
$$

then, near the root, the error satisfies approximately

$$
 |e_{k+1}|\le C|e_k|^2
$$

for some constant $C>0$. This is the key reason Newton's method is attractive: once the iterates are in the right neighbourhood, the number of correct digits usually grows very rapidly.

In practice, this means that for a modest initial guess near the equilibrium displacement, Newton's method can produce a very accurate answer quickly. But if the starting value is poor, the tangent-line approximation may be a bad model and the iteration may behave badly.

<!-- section: SEC-04 -->
## Stopping criteria and practical checks

A numerical solver should not rely on one test alone. Two common checks are used together.

The step test stops when the change in the iterate is small:

$$
 |x_{k+1}-x_k|\le \varepsilon_x(1+|x_{k+1}|).
$$

The residual test stops when the force imbalance is small:

$$
 |f(x_{k+1})|\le \varepsilon_f.
$$

These two measures complement each other. A small update does not always mean the residual is small, and a small residual does not necessarily mean the displacement error is small. In engineering work, it is sensible to inspect both. A robust implementation also uses a maximum iteration count and reports failure if the iteration has not converged by then.

A derivative threshold is another important safeguard. If

$$
 |f'(x_k)|<\delta,
$$

then the Newton step may be too large to trust. The algorithm should stop with a breakdown message rather than continue with an unstable update.

<!-- section: SEC-05 -->
## Why Newton can fail and how damping helps

Newton's method is not globally reliable. Several failure boundaries are important.

First, a poor initial guess can send the iteration far away from the local convergence region. Second, a near-zero derivative can make the step enormous. Third, if the root is multiple rather than simple, the standard quadratic convergence result no longer applies. Fourth, the iteration can leave the physically allowed domain, such as a displacement that makes a model invalid. Finally, the algorithm can cycle or jump between values instead of settling.

To improve robustness, engineers often use damping. Instead of accepting the full Newton step, they use a factor $\alpha_k$ with $0<\alpha_k\le1$:

$$
 x_{k+1}=x_k-\alpha_k\frac{f(x_k)}{f'(x_k)}.
$$

The full Newton step corresponds to $\alpha_k=1$. Smaller values reduce the step size and can prevent a poor tangent-line prediction from overshooting the solution. Damping does not guarantee convergence in every case, but it usually improves the behaviour of the method when the starting point is not close to the root.

<!-- section: SEC-06 -->
## Python implementation and exercises

The following Python example uses a simple nonlinear spring model. The residual is the force imbalance, and the derivative is its local slope. The code follows the Newton update directly.

```python
import numpy as np


def newton_spring_solve(x0, load=10.0, max_iter=20):
    x = float(x0)
    for k in range(max_iter):
        f = x**3 - load
        fp = 3 * x**2
        if abs(fp) < 1e-10:
            return None, k, "breakdown"
        step = -f / fp
        x_new = x + step
        if abs(x_new - x) <= 1e-8 * (1 + abs(x_new)) or abs(f) <= 1e-8:
            return x_new, k + 1, "converged"
        x = x_new
    return x, max_iter, "max-iterations"


root, iterations, status = newton_spring_solve(1.5, load=10.0)
print(root, iterations, status)
```

How does this code match the mathematics?

- The residual is defined as $f(x)=x^3-L$, which is the difference between the spring force and the applied load.
- The derivative $f'(x)=3x^2$ is the local slope of that force-displacement relation.
- The update $x_{k+1}=x_k-f(x_k)/f'(x_k)$ is implemented exactly as the formula above.
- The stopping logic checks both a step size and a residual size, just as the theory suggests.
- The derivative threshold prevents the code from dividing by a near-zero slope.

For this example, the solution is the cube root of the load, so the equilibrium displacement is approximately $\sqrt[3]{10}$.

Exercises:

1. Derive the Newton update for the residual $f(x)=x^3-10$ and show the first iteration starting from $x_0=1.5$.
2. Explain why the derivative condition $f'(x)=0$ is a practical warning sign in this spring model.
3. Compare the full Newton step with a damped step using $\alpha=0.5$ for the same starting value.
4. In the code, which line implements the tangent-line approximation, and which line implements the stopping test?
5. Suppose the load is changed so that the equation becomes $f(x)=x^3-100$. What happens to the equilibrium displacement and why?
6. For a different residual such as $f(x)=x^2-4$, explain why Newton's method may behave differently from the cubic example.
