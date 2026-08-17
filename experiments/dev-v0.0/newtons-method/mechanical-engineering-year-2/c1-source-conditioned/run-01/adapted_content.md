# Newton's Method for Nonlinear Spring Equilibrium

## Learning objectives

After studying this lesson, you should be able to:

1. describe a scalar nonlinear equilibrium problem in terms of force balance;
2. derive Newton's method from local linearisation of the load-displacement relation;
3. state the conditions for local quadratic convergence;
4. implement stopping and breakdown checks in Python;
5. explain how damping helps when the current estimate is far from equilibrium;
6. see how the method extends conceptually to systems of nonlinear equations.

## 1. Nonlinear equilibrium in a spring system

Consider a mechanical system where the net restoring force depends nonlinearly on a displacement $x$. The equilibrium displacement satisfies the force-balance equation:

$$
F(x)=0.
$$

In this lesson, $F(x)$ plays the role of the net force on a nonlinear spring or an element in a mechanical linkage. Solving $F(x)=0$ means finding the displacement $x$ at which the internal restoring force balances the external load.

A root $r$ of $F$ is called simple if

$$
F'(r)\ne0.
$$

In a spring model, this means the stiffness at the equilibrium point is nonzero. If the stiffness vanishes ($F'(r)=0$), the equilibrium is degenerate and the standard Newton convergence guarantee does not apply.

## 2. Deriving Newton's method from the tangent line

Given a current estimate $x_k$ of the equilibrium displacement, approximate the net force by its linear tangent:

$$
F(x)\approx F(x_k)+F'(x_k)(x-x_k).
$$

Setting this linear approximation to zero defines the next estimate:

$$
0 = F(x_k) + F'(x_k)(x_{k+1}-x_k).
$$

Provided $F'(x_k)\ne0$, solve for $x_{k+1}$:

$$
x_{k+1} = x_k - \frac{F(x_k)}{F'(x_k)}.
$$

This is Newton's iteration. In mechanical language, the step

$$
-\frac{F(x_k)}{F'(x_k)}
$$

is the displacement correction obtained from the current residual force divided by the local stiffness. A good estimate of the equilibrium displacement follows from using the tangent-line model of the nonlinear force.

If $F'(x_k)$ is zero or very small, the correction step is undefined or excessively large. That corresponds to a vanishing or nearly vanishing stiffness, which is dangerous for a physical solver.

## 3. Local convergence near a simple equilibrium

Newton's method is strongest when the initial guess is already close to the equilibrium root.

### Local quadratic convergence theorem

Suppose that:

1. $F$ is twice continuously differentiable near a root $r$;
2. $F(r)=0$;
3. $F'(r)\ne0$;
4. the initial guess $x_0$ is sufficiently close to $r$.

Then the Newton iterates are well defined near $r$ and converge to $r$ quadratically. If we define the error

$$
e_k = x_k - r,
$$

then asymptotically

$$
|e_{k+1}| \le C |e_k|^2
$$

for some constant $C>0$.

Quadratic convergence means that once the method is close enough, the error typically squares at each step. In engineering terms, the estimate improves very rapidly after the iterates enter the local convergence region.

### Error relation from Taylor expansion

Using Taylor's theorem about $x_k$ gives:

$$
0 = F(r) = F(x_k) + F'(x_k)(r-x_k) + \frac{1}{2} F''(\xi_k)(r-x_k)^2
$$

for some $\xi_k$ between $x_k$ and $r$. Substituting the Newton update yields:

$$
e_{k+1} = \frac{F''(\xi_k)}{2F'(x_k)} e_k^2.
$$

If the stiffness $F'(x_k)$ remains bounded away from zero and the second derivative is bounded, this gives the quadratic error estimate.

## 4. Multiple equilibria and multiplicity

When an equilibrium $r$ has multiplicity $m>1$, the slope of $F$ at the root is zero and the simple-root theory does not apply. For example, if

$$
F(x)=(x-r)^m,
$$
then the Newton iteration becomes:

$$
x_{k+1}-r = \left(1-\frac{1}{m}\right)(x_k-r).
$$

This yields only linear convergence. In mechanical terms, a multiple root corresponds to a flat region in the load-displacement curve, where the restoring force is zero over a range of displacements rather than crossing the axis sharply.

If the multiplicity $m$ is known, the modified iteration

$$
x_{k+1} = x_k - m \frac{F(x_k)}{F'(x_k)}
$$

can restore quadratic convergence under the same smoothness assumptions.

## 5. Stopping criteria for equilibrium solvers

A solver must decide when the estimate is close enough to equilibrium. Two common measures are:

### Step test

Stop when

$$
|x_{k+1}-x_k| \le \varepsilon_x (1 + |x_{k+1}|).
$$

This relative step test scales with the size of the solution. In a mechanical solver, it means that the displacement correction is small compared to the current displacement.

### Residual test

Stop when

$$
|F(x_{k+1})| \le \varepsilon_f.
$$

This residual test checks whether the net force is sufficiently close to zero. A small step does not guarantee a small residual, and a small residual does not guarantee a small displacement error when the problem is poorly conditioned. Both tests are useful in practice.

The algorithm should also stop if it reaches a maximum number of iterations and report non-convergence rather than claim success.

## 6. Failure modes in mechanical equilibrium

Newton's method is not guaranteed to succeed for every initial guess.

### Poor initial guess

If the starting displacement is far from the equilibrium, the tangent-line approximation of the force may be poor, and the iterates can diverge, cycle, or converge to a different root.

### Small stiffness

If $|F'(x_k)|$ is very small, the Newton correction step

$$
-\frac{F(x_k)}{F'(x_k)}
$$

can become very large. Physically, this is a point of near-zero stiffness, and the solver should detect it and avoid making an unreliable step.

### Multiple roots

If the root is multiple, then $F'(r)=0$ and the standard quadratic convergence result no longer holds. The solver may only converge linearly.

### Domain restrictions

An iterate may leave the valid domain of the model. For example, if the nonlinear force is defined only for positive displacement, a step to a negative $x$ may be invalid.

### Cycling

Newton's method can enter a cycle and fail to converge. It is not globally convergent for arbitrary differentiable functions and arbitrary starting points.

## 7. Damped Newton iteration for robustness

To reduce the risk of an overly large correction, use a damping factor $\alpha_k \in (0,1]$:

$$
x_{k+1} = x_k - \alpha_k \frac{F(x_k)}{F'(x_k)}.
$$

The full Newton method is recovered when $\alpha_k=1$. A smaller step can prevent excursions far from the local convergence region.

One practical approach is backtracking damping. Start with $\alpha_k = 1$ and reduce it until the trial point improves a merit function such as

$$
\phi(x) = \frac{1}{2} F(x)^2.
$$

This function measures the squared net force. Damping can improve robustness, but it does not guarantee convergence in every case. The choice of acceptance rule and merit function matters.

## 8. Systems of nonlinear equations in mechanics

Many mechanical equilibrium problems are vector-valued: displacement, rotation, or multiple degrees of freedom. For a system

$$
F(x)=0,
\qquad
F:\mathbb{R}^n\to\mathbb{R}^n,
$$

replace the scalar derivative with the Jacobian matrix

$$
J_F(x) = \begin{bmatrix}
\partial F_1/\partial x_1 & \cdots & \partial F_1/\partial x_n \\
\vdots & \ddots & \vdots \\
\partial F_n/\partial x_1 & \cdots & \partial F_n/\partial x_n
\end{bmatrix}.
$$

At iteration $k$, solve the linear system

$$
J_F(x_k) s_k = -F(x_k)
$$

and update

$$
x_{k+1} = x_k + s_k.
$$

In numerical practice, solving this linear system is preferable to computing $J_F(x_k)^{-1}$ explicitly. An explicit inverse is usually less efficient and may be less numerically stable.

## 9. Scalar Newton algorithm for a nonlinear spring

Given a nonlinear function $F$, its derivative $F'$, an initial guess $x_0$, tolerances $\varepsilon_x$ and $\varepsilon_f$, a derivative threshold $\delta$, and a maximum iteration count $K$:

1. evaluate $F(x_k)$ and $F'(x_k)$;
2. stop with a breakdown message if $|F'(x_k)|<\delta$;
3. compute $s_k=-F(x_k)/F'(x_k)$;
4. set $x_{k+1}=x_k+s_k$;
5. evaluate $F(x_{k+1})$;
6. declare convergence only if the selected stopping tests are satisfied;
7. otherwise continue until $K$ iterations have been performed;
8. report non-convergence if the maximum is reached.

This algorithm is suitable for a nonlinear spring equilibrium equation, provided the root is simple and the current estimate remains in a region where the derivative is not too small.

## 10. Python implementation with a nonlinear force model

The code below solves a nonlinear spring equilibrium defined by a force function $F(x)$ and its derivative. It includes step and residual stopping tests, a derivative threshold, and iterative damping.

```python
import math


def newton(
    function,
    derivative,
    initial_value,
    step_tolerance=1e-12,
    residual_tolerance=1e-12,
    derivative_threshold=1e-14,
    max_iterations=50,
):
    x = float(initial_value)

    for iteration in range(1, max_iterations + 1):
        fx = function(x)
        dfx = derivative(x)

        if abs(dfx) < derivative_threshold:
            raise RuntimeError("derivative is too small for a reliable Newton step")

        step = -fx / dfx
        next_x = x + step
        next_residual = abs(function(next_x))

        step_small = abs(step) <= step_tolerance * (1.0 + abs(next_x))
        residual_small = next_residual <= residual_tolerance

        if step_small and residual_small:
            return next_x, next_residual, iteration

        x = next_x

    raise RuntimeError("Newton iteration did not converge within the limit")


def F(x):
    # Example nonlinear spring force: F(x) = k x + c x^3 - P
    k = 10.0
    c = 2.0
    P = 5.0
    return k * x + c * x**3 - P


def dF(x):
    k = 10.0
    c = 2.0
    return k + 3.0 * c * x**2


if __name__ == "__main__":
    initial_guess = 0.5
    root, residual, iterations = newton(F, dF, initial_guess)

    print("Equilibrium displacement:", root)
    print("Residual force:", residual)
    print("Iterations:", iterations)
```

### Connecting the code to the math

- `F(x)` models the net force in a nonlinear spring system, including a cubic stiffness term and an external load $P$.
- `dF(x)` is the derivative of the force with respect to displacement, representing the tangent stiffness.
- The line `step = -fx / dfx` implements the Newton correction from
  $-F(x_k)/F'(x_k)$.
- The next displacement `next_x = x + step` updates the estimate by applying the tangent-line correction.
- The residual `abs(function(next_x))` measures the net force magnitude at the new displacement.
- Both the step size and the residual are checked before declaring convergence.
- The derivative threshold prevents division by a near-zero stiffness.

This example is directly related to finding the equilibrium displacement of a nonlinear spring under a fixed load.

## 11. Exercises

1. For the force function $F(x)=x^3-x-2$, apply three Newton steps starting from $x_0=1.5$ and compute the approximate displacement at each iteration.
2. Suppose a nonlinear spring has the force law $F(x)=x^3-8$. Derive the Newton iteration and explain how it relates to computing the real cube root of 8.
3. For $F(x)=(x-2)^3$, show that Newton's method converges only linearly and identify the convergence factor.
4. Give an example of a function $F(x)$ and a point $x_k$ where $|F'(x_k)|$ is small, and explain why the Newton step may fail.
5. Modify the Python implementation to store every iterate and residual. Print the sequence of residuals and comment on whether they decrease monotonically.
6. Implement a simple damped Newton update with a backtracking merit function $\phi(x)=F(x)^2/2$. Describe why damping can help when the current guess is not close to the equilibrium.
7. For a two-degree-of-freedom nonlinear system $F(x)=[F_1(x_1,x_2), F_2(x_1,x_2)]^T$, write down the Jacobian matrix and the Newton linear system. Explain why solving $J_F(x_k) s_k = -F(x_k)$ is preferred over forming $J_F(x_k)^{-1}$.

## Summary

Newton's method solves nonlinear equilibrium equations by replacing the force-displacement relation locally with its tangent line. Near a simple root with nonzero tangent stiffness, the iterations can converge quadratically. In practical mechanical solvers, robust stopping criteria and derivative checks are essential. Damping can improve the behaviour when the estimate is far from equilibrium, but it does not eliminate the need for a reasonable initial guess and attention to failure modes.