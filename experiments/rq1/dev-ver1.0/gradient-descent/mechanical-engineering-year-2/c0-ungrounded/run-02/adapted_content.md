# Gradient Descent and Optimisation Through Mechanical Relaxation

## 1. Why optimisation appears in mechanics

A mechanical system often settles into an equilibrium configuration. A spring stretches until the forces balance; a frame deforms until its internal forces balance the applied loads; a linkage finds a configuration in which small virtual movements do not reduce its potential energy. This idea gives a useful entry point to optimisation.

Suppose a vector $x\in\mathbb{R}^n$ describes unknown design or state variables, such as nodal displacements, joint angles, or geometric parameters. Let $f(x)$ be a scalar objective. In a potential-energy problem, $f$ might be the total potential energy. A configuration at which the system can no longer reduce $f$ by an infinitesimal change is a candidate equilibrium:

$$\nabla f(x^*)=0.$$

Numerical relaxation methods imitate the idea of repeatedly making a small change that reduces an objective. Gradient descent is the simplest example. However, the analogy has a boundary: an optimisation objective need not be a physical energy, and algorithmic iterations are not automatically physical time evolution. We use the mechanical picture to build intuition, not to identify every objective or iteration with a real physical quantity.

In engineering, optimisation can mean selecting a shape, material, control input, or operating point. The objective may combine weight, compliance, temperature, cost, error, and safety margins. This lesson develops methods for unconstrained smooth optimisation, then connects the mathematics to short Python implementations.

## 2. Local optimality: what derivatives can and cannot tell us

Consider minimising a differentiable function $f:\mathbb{R}^n\to\mathbb{R}$. A point $x^*$ is a local minimum if there is a neighbourhood around it in which $f(x^*)\leq f(x)$ for every nearby $x$. It is a strict local minimum if the inequality is strict for every nearby $x\ne x^*$. A global minimum satisfies the inequality for every point in the whole domain.

### First-order necessary condition

If $x^*$ is an interior local minimum and $f$ is differentiable, then

$$\nabla f(x^*)=0.$$

This is a necessary condition, not usually a sufficient one. A stationary point can be a minimum, maximum, or saddle point. For example, $f(x)=x^3$ has $f'(0)=0$, but $0$ is neither a minimum nor a maximum. In several dimensions, a saddle can decrease in one direction and increase in another.

The gradient points in the direction of steepest local increase under the Euclidean norm. Therefore $-\nabla f(x)$ is a steepest-descent direction. If the gradient is nonzero, sufficiently small steps in that direction reduce $f$ for a smooth function.

### Second-order tests

For twice-differentiable $f$, the Hessian is the matrix of second partial derivatives:

$$\nabla^2 f(x)=\left[\frac{\partial^2f}{\partial x_i\partial x_j}\right]_{i,j=1}^n.$$

At a stationary point $x^*$:

- if the Hessian is positive definite, $x^*$ is a strict local minimum;
- if it is negative definite, $x^*$ is a strict local maximum;
- if it is indefinite, $x^*$ is a saddle point;
- if it is only positive semidefinite, the test is inconclusive.

Positive definiteness means $v^T\nabla^2f(x^*)v>0$ for every nonzero direction $v$. Mechanically, this resembles positive stiffness for every admissible infinitesimal displacement, although the Hessian and a physical stiffness matrix are not universally the same object.

The second-order Taylor approximation makes the test intuitive:

$$f(x^*+p)\approx f(x^*)+\nabla f(x^*)^Tp+\frac12p^T\nabla^2f(x^*)p.$$

At a stationary point the linear term vanishes. The quadratic term determines the local curvature when it is nondegenerate.

## 3. Smoothness, convexity, and conditioning

Gradient methods work especially predictably when the objective has controlled curvature.

### Smoothness

A differentiable function is $L$-smooth if its gradient is Lipschitz continuous:

$$\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|.$$

The number $L$ is an upper bound on curvature in the relevant norm. Smoothness gives the descent lemma:

$$f(y)\leq f(x)+\nabla f(x)^T(y-x)+\frac{L}{2}\|y-x\|^2.$$

Set $y=x-\alpha\nabla f(x)$. Then

$$f(x-\alpha\nabla f(x))\leq f(x)-\alpha\left(1-\frac{L\alpha}{2}\right)\|\nabla f(x)\|^2.$$

Thus any $0<\alpha<2/L$ guarantees a decrease at that step under the assumptions. The commonly used conservative choice is $\alpha\leq1/L$.

### Convexity

A function is convex if the line segment between any two points lies above the graph:

$$f(\theta x+(1-\theta)y)\leq\theta f(x)+(1-\theta)f(y),\qquad 0\leq\theta\leq1.$$

For a differentiable convex function, the tangent plane is a global lower bound:

$$f(y)\geq f(x)+\nabla f(x)^T(y-x).$$

Every local minimum is then global. For a twice-differentiable function on a convex domain, convexity is equivalent to a positive-semidefinite Hessian everywhere. Convexity does not require a unique minimiser: a flat valley can contain many equally good points.

A function is $\mu$-strongly convex when

$$f(y)\geq f(x)+\nabla f(x)^T(y-x)+\frac{\mu}{2}\|y-x\|^2,$$

for some $\mu>0$. For a twice-differentiable function, this corresponds to $\nabla^2f(x)\succeq\mu I$. Strong convexity gives a unique minimiser and rules out arbitrarily flat directions.

### Conditioning

For a quadratic objective

$$f(x)=\frac12x^TAx-b^Tx+c,$$

with symmetric positive-definite $A$, the smallest and largest eigenvalues are $\mu=\lambda_{\min}(A)$ and $L=\lambda_{\max}(A)$. The condition number is

$$\kappa=\frac{L}{\mu}.$$

A large $\kappa$ means a long, narrow valley. Contours look like elongated ellipses, and ordinary gradient descent tends to zig-zag across the steep direction while progressing slowly along the shallow direction. Rescaling variables or preconditioning can make the geometry more nearly circular.

## 4. Gradient descent and step-size selection

The gradient-descent update is

$$x_{k+1}=x_k-\alpha_k\nabla f(x_k).$$

The gradient is evaluated at the current iterate, and $\alpha_k>0$ is the step size, also called the learning rate. In a mechanical relaxation interpretation, the update moves opposite the local slope. It is not a force-balance solver unless the objective and scaling make that interpretation appropriate.

A step that is too small is safe but slow. A step that is too large can overshoot, oscillate, or diverge. For a one-dimensional quadratic $f(x)=\frac12ax^2$ with $a>0$,

$$x_{k+1}=(1-\alpha a)x_k.$$

Convergence requires $|1-\alpha a|<1$, so $0<\alpha<2/a$. At $\alpha=1/a$, the solution is reached in one step for this one-dimensional quadratic. In multiple dimensions, a single step size must accommodate the largest curvature direction.

If $L$ is known, $\alpha=1/L$ is a basic choice. For a strongly convex quadratic, the theoretically best constant step size for the worst eigen-direction is $2/(L+\mu)$, with contraction factor $(\kappa-1)/(\kappa+1)$ in the appropriate norm. In practical engineering work, $L$ may not be known, so backtracking line search starts with a trial step and reduces it until a sufficient-decrease condition holds. A schedule that decreases the step size can help noisy methods, but decreasing too quickly may stop useful learning.

Stopping criteria should reflect the task. Common choices include $\|\nabla f(x_k)\|$ below a tolerance, a small change in $x_k$, a small change in $f(x_k)$, or a maximum iteration count. Always inspect the objective history and, when possible, a residual relevant to the engineering model.

## 5. What convergence guarantees mean

For an $L$-smooth convex function bounded below, gradient descent with a suitable constant step size has a sublinear objective-error guarantee of the form

$$f(x_k)-f(x^*)=O\left(\frac{L\|x_0-x^*\|^2}{k}\right).$$

The notation means that the error decreases proportionally to roughly $1/k$ up to problem-dependent constants. This is a guarantee, not a claim that every iteration decreases by exactly the same amount.

For an $L$-smooth, $\mu$-strongly convex function, gradient descent converges geometrically. With $\alpha=1/L$, one standard bound is

$$f(x_k)-f(x^*)\leq\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).$$

The factor is less than one, so each group of iterations reduces the bound by a fixed proportion. The rate becomes slow as $\kappa=L/\mu$ grows. In a nonconvex problem, gradient descent may converge to a stationary point rather than a global minimum, and guarantees typically concern the size of the gradient or the best objective value seen rather than global optimality.

## 6. Momentum and acceleration

Momentum stores a direction from previous gradients. One common form is

$$v_{k+1}=\beta v_k+\nabla f(x_k),\qquad x_{k+1}=x_k-\alpha v_{k+1},$$

where $0\leq\beta<1$. Another convention stores the displacement and writes $x_{k+1}=x_k+\beta(x_k-x_{k-1})-\alpha\nabla f(x_k)$. These forms differ in indexing and parameter interpretation, so implementations must be checked carefully.

Momentum can reduce zig-zagging in narrow valleys: repeated gradients pointing along a shallow direction accumulate, while rapidly changing transverse directions partially cancel. It can also overshoot if the step size or momentum is too large. A useful mental model is a damped numerical motion, but the stored velocity is an algorithmic state, not necessarily a physical velocity.

Nesterov acceleration evaluates the gradient at a look-ahead point. In convex settings, carefully selected versions improve the theoretical objective rate from $O(1/k)$ to $O(1/k^2)$ for smooth convex problems. These guarantees depend on assumptions and exact parameter choices; acceleration is not simply “more momentum” and can be less forgiving in noisy or badly scaled problems.

## 7. Stochastic and adaptive methods

When an objective is a sum over many measurements or simulations,

$$f(x)=\frac1N\sum_{i=1}^N f_i(x),$$

using the full gradient may be expensive. A mini-batch gradient $g_k$ estimates the full gradient using a subset. Stochastic gradient descent uses

$$x_{k+1}=x_k-\alpha_k g_k.$$

The noise can make the objective fluctuate rather than decrease at every step. It can nevertheless make large datasets tractable and sometimes helps escape shallow regions. For convergence, step sizes often decrease over time; a constant step can maintain a neighbourhood around a solution rather than converge exactly.

Adaptive methods maintain coordinate-wise statistics. AdaGrad scales updates using accumulated squared gradients, making frequently active coordinates receive smaller later steps. RMSProp replaces the unbounded sum with an exponentially weighted average. Adam combines a momentum-like first moment and a second-moment estimate, with bias corrections in its standard form. These methods can be effective when variables have different scales, but their practical success does not remove the need for sensible units, monitoring, validation, and stopping rules. An adaptive method may converge to a point with a less desirable generalisation or engineering performance than a carefully tuned simpler method.

## 8. Newton and quasi-Newton methods

Newton's method uses the local quadratic model. If the Hessian is invertible,

$$x_{k+1}=x_k-\left[\nabla^2f(x_k)\right]^{-1}\nabla f(x_k).$$

It is better to solve the linear system $\nabla^2f(x_k)p_k=-\nabla f(x_k)$ than to form an explicit inverse. Near a solution with a positive-definite Hessian and sufficient smoothness, Newton's method can have quadratic convergence: roughly, the number of correct digits doubles near the solution. Far from a solution, an indefinite Hessian can produce an ascent direction, and solving large systems can be expensive. Damping or a line search makes the method safer:

$$x_{k+1}=x_k+\lambda p_k,\qquad 0<\lambda\leq1.$$

Quasi-Newton methods approximate curvature without explicitly computing the Hessian. BFGS builds a positive-definite approximation from changes in iterates and gradients. L-BFGS stores only limited history, making it useful for large problems. These methods often outperform gradient descent on small or medium smooth deterministic problems, while stochastic first-order methods are attractive when gradients are cheap but Hessians are unavailable or data are huge.

## 9. Translating the mathematics into Python

The implementation should make the update rule visible. A minimal gradient-descent function accepts an objective, its gradient, an initial vector, a step size, and a stopping tolerance.

```python
import numpy as np

def gradient_descent(f, grad_f, x0, alpha=0.1, tol=1e-6, max_iter=10_000):
    x = np.asarray(x0, dtype=float).copy()
    history = [float(f(x))]

    for _ in range(max_iter):
        g = np.asarray(grad_f(x), dtype=float)
        if not np.all(np.isfinite(g)):
            raise ValueError("non-finite gradient")
        if np.linalg.norm(g) <= tol:
            break
        x = x - alpha * g
        history.append(float(f(x)))

    return x, history

A = np.diag([1.0, 10.0])
b = np.array([2.0, -5.0])
f = lambda x: 0.5 * x @ A @ x - b @ x
grad_f = lambda x: A @ x - b
x, history = gradient_descent(f, grad_f, np.zeros(2), alpha=0.1)
print(x, history[-1])
```

For the quadratic above, the minimiser solves $Ax=b$, giving $x^*=A^{-1}b$. The largest eigenvalue is $10$, so $\alpha=0.1$ is at the edge of the conservative $1/L$ choice. A step larger than $2/L=0.2$ would make the steep coordinate diverge. Notice that `x` is copied, the gradient is evaluated before updating, and the history records objective values after updates. These details prevent common aliasing, ordering, and monitoring errors.

For stochastic code, pass a mini-batch to the gradient function and choose a schedule such as $\alpha_k=\alpha_0/(1+\rho k)$ when theoretical convergence of noisy updates matters. For adaptive code, maintain moment arrays with the same shape as `x`, add a small numerical constant to denominators, and ensure that the gradient and parameter units have been considered.

## Exercise 1 — Conceptual and theorem-scope check

A colleague makes four statements about a differentiable objective:

1. Every point where $\nabla f(x)=0$ is a local minimum.
2. Every local minimum of a convex function is global.
3. For an $L$-smooth function, choosing $\alpha=1/L$ guarantees convergence to a global minimum.
4. Strong convexity implies a unique minimiser.

Identify which statements are correct as written and briefly explain what is missing from any incorrect statement.

### Worked solution

Statements 2 and 4 are correct, with the usual assumptions that the domain is convex and the minimum exists. Convexity makes every local minimum global. Strong convexity gives strict curvature and therefore at most one minimiser; existence still depends on the function and domain.

Statement 1 is false. A stationary point can be a maximum or saddle, as shown by $f(x)=x^3$ at zero. A positive-definite Hessian at a stationary point is a sufficient condition for a strict local minimum.

Statement 3 is too strong. Smoothness and the step size alone do not guarantee a global minimum unless additional assumptions, such as convexity and an appropriate lower-bounded objective, are present. For a nonconvex function, gradient descent may approach a non-global stationary point. Even in convex problems, one must distinguish objective convergence from convergence of iterates and account for existence of a minimiser.

## Exercise 2 — Hand calculation on an anisotropic quadratic

Let

$$f(x,y)=\frac12(x^2+10y^2)-2x+5y.$$

(a) Find the minimiser. (b) Starting from $(x_0,y_0)=(0,0)$, perform two gradient-descent steps with $\alpha=0.1$. (c) Explain why a much larger step size is unsafe.

### Worked solution

The gradient is

$$\nabla f(x,y)=\begin{bmatrix}x-2\\10y+5\end{bmatrix}.$$

Set it to zero. This gives $x^*=2$ and $y^*=-0.5$. The Hessian is $\operatorname{diag}(1,10)$, so the function is strongly convex with $L=10$ and $\mu=1$.

At $(0,0)$, the gradient is $( -2,5)$. Therefore

$$x_1=(0,0)-0.1(-2,5)=(0.2,-0.5).$$

At this point the gradient is

$$\nabla f(x_1)=(-1.8,0),$$

so the second step is

$$x_2=(0.2,-0.5)-0.1(-1.8,0)=(0.38,-0.5).$$

The steep $y$ direction reached its optimum immediately because its curvature is $10$ and $\alpha=1/10$. The $x$ direction moves more slowly. For the steep direction, stability requires $0<\alpha<2/10=0.2$. A larger step can produce alternating overshoots and, if it exceeds $0.2$, divergence in that coordinate.

## Exercise 3 — Code diagnostic with executable Python

The following program is intended to minimise $f(x)=\frac12x^2$ from $x=4$. It runs, but its result is not the intended minimiser. Diagnose and correct the update-related bug. Then state what the corrected program should print approximately.

```python
import numpy as np

def f(x):
    return 0.5 * x**2

def grad_f(x):
    return x

x = np.array([4.0])
alpha = 0.25
for _ in range(20):
    x = x + alpha * grad_f(x)

print(x, f(x))
```

### Worked solution

The gradient points toward increasing $f$, so minimisation must move in the negative-gradient direction. The line uses `+` rather than `-`. The corrected executable program is:

```python
import numpy as np

def f(x):
    return 0.5 * x**2

def grad_f(x):
    return x

x = np.array([4.0])
alpha = 0.25
for _ in range(20):
    x = x - alpha * grad_f(x)

print(x, f(x))
```

Here the scalar recurrence is $x_{k+1}=0.75x_k$, so after 20 steps $x_{20}=4(0.75)^{20}\approx0.0127$. The objective is approximately $0.000081$. The program should therefore print a value near `[0.0127]` followed by a value near `8.1e-05`, with small differences caused only by rounding. The positive sign instead gives $x_{k+1}=1.25x_k$, so the magnitude grows and the objective increases.

## 10. A practical workflow for engineering problems

Begin by defining variables, units, objective, and any constraints. Even when studying the unconstrained case, write down what has been omitted. Check a gradient against finite differences at several random points; an incorrect derivative can make a sound algorithm appear unstable. Estimate scaling and, if possible, curvature bounds. Start with a conservative step, plot objective and gradient-norm histories, and inspect the final design rather than trusting one number.

Use gradient descent when the gradient is inexpensive and simplicity matters. Consider momentum when a well-scaled deterministic problem has long valleys. Use stochastic or adaptive methods when data or simulations make full gradients costly, while monitoring noise and validation performance. Use Newton or quasi-Newton methods when reliable curvature information can justify their memory and computational cost. Finally, remember that an unconstrained optimum may violate stress, displacement, geometry, or manufacturing requirements. Constraints require additional methods—such as penalty, barrier, projected, or constrained optimisation techniques—beyond the scope of this first relaxation-based view.

The central pattern is simple: understand the local geometry, choose an update that respects that geometry, and verify the computed result against both mathematics and engineering meaning.