# Gradient Descent and Optimisation

## 1. Why optimisation matters in mechanical engineering

Optimisation is the systematic search for a design, operating condition, or model parameter that gives the best possible performance. In mechanical engineering, “best” might mean minimum mass subject to a stiffness requirement, minimum drag at a required lift, minimum temperature error in a controller, or the smallest discrepancy between a simulation and measured data. We write the quantity to be improved as an objective function $f(x)$, where the vector $x$ contains the decision variables. For example, $x$ could contain beam dimensions, motor-control parameters, or coefficients in a constitutive model.

An optimisation problem usually has the form

$$
\min_{x\in\mathbb{R}^n} f(x).
$$

This chapter concentrates on unconstrained, differentiable problems first. Constraints are important in engineering, but understanding the geometry of an unconstrained objective is the foundation for constrained methods as well. The central idea is to replace a difficult global search with a sequence of local improvements. At a current point $x_k$, calculate information about the slope or curvature of the objective, then choose an update that should reduce $f$.

The gradient is the vector of first partial derivatives. It points in the direction of steepest local increase under the usual Euclidean distance, so $-\nabla f(x_k)$ is the direction of steepest local decrease. The Hessian, $\nabla^2 f(x_k)$, contains second derivatives and describes local curvature. A good optimisation method balances these two kinds of information: gradients are comparatively cheap and often robust, while curvature can provide much faster progress when it is estimated reliably.

## 2. Optimality conditions and local geometry

If $x^*$ is an interior local minimiser and $f$ is differentiable, the first-order necessary condition is

$$
\nabla f(x^*)=0.
$$

This condition says that there is no first-order direction of improvement. It is necessary, not sufficient: a stationary point can be a minimum, a maximum, or a saddle point. In one dimension, $f(x)=x^3$ has a zero derivative at $x=0$ but does not have a local minimum there.

For a twice-differentiable function, the second-order necessary condition at a local minimum is

$$
\nabla^2 f(x^*)\succeq 0,
$$

meaning that $d^T\nabla^2 f(x^*)d\geq 0$ for every direction $d$. The Hessian must have no negative-curvature direction. The second-order sufficient condition is stronger: if $\nabla f(x^*)=0$ and

$$
\nabla^2 f(x^*)\succ 0,
$$

then $x^*$ is a strict local minimum. Positive definiteness means $d^T\nabla^2 f(x^*)d>0$ for every nonzero $d$.

These tests have a useful mechanical interpretation. Imagine moving a small distance $t$ from $x^*$ in direction $d$. A Taylor approximation gives

$$
 f(x^*+td)\approx f(x^*)+t\nabla f(x^*)^Td+\tfrac12t^2d^T\nabla^2 f(x^*)d.
$$

At a stationary point, the linear term vanishes. The sign of the quadratic term then determines whether the surface curves upward, downward, or flatly in that direction. A flexible design variable may create a very small positive eigenvalue of the Hessian, producing a long, shallow valley and slow optimisation.

## 3. Smoothness, convexity, and strong convexity

A function is $L$-smooth if its gradient is Lipschitz continuous:

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|.
$$

For twice-differentiable functions, a sufficient interpretation is that the largest Hessian eigenvalue is at most $L$ everywhere. Smoothness prevents the gradient from changing arbitrarily rapidly. It gives the descent lemma,

$$
 f(y)\leq f(x)+\nabla f(x)^T(y-x)+\frac{L}{2}\|y-x\|^2.
$$

This inequality is the main tool behind basic gradient-descent convergence proofs.

A differentiable function is convex if

$$
 f(y)\geq f(x)+\nabla f(x)^T(y-x)
$$

for all $x,y$. Its graph lies above every tangent plane. If twice differentiable, convexity is equivalent to $\nabla^2f(x)\succeq0$ everywhere. Every local minimum of a convex function is global, which is a major reason convexity is valuable in engineering estimation and design.

Strong convexity adds a uniform upward curvature. A function is $\mu$-strongly convex when

$$
 f(y)\geq f(x)+\nabla f(x)^T(y-x)+\frac{\mu}{2}\|y-x\|^2,
$$

where $\mu>0$. In the twice-differentiable case, this corresponds to $\nabla^2f(x)\succeq\mu I$. If the function is also $L$-smooth, its condition number is $\kappa=L/\mu$. A large $\kappa$ means that some directions are much steeper than others. Quadratic valleys with large condition numbers are common after physical variables are expressed in poorly scaled units.

## 4. Gradient descent and selecting a step size

Gradient descent uses the update

$$
 x_{k+1}=x_k-\alpha_k\nabla f(x_k),
$$

where $\alpha_k>0$ is the step size or learning rate. The gradient supplies a direction, but the step size determines how far to trust the local linear model. A step that is too small gives safe but slow progress. A step that is too large can overshoot, oscillate, or diverge.

For an $L$-smooth convex objective, a fixed step satisfying $0<\alpha\leq1/L$ guarantees decrease. A commonly used conservative choice is $\alpha=1/L$. For a quadratic $f(x)=\tfrac12x^TAx-b^Tx$ with symmetric positive-definite $A$, stability requires $0<\alpha<2/\lambda_{\max}(A)$. The iterates may oscillate when the step approaches this upper limit.

Exact line search chooses the best step along the current descent direction:

$$
\alpha_k=\arg\min_{\alpha\geq0}f(x_k-\alpha\nabla f(x_k)).
$$

For a quadratic with Hessian $A$, the exact step is

$$
\alpha_k=\frac{\nabla f(x_k)^T\nabla f(x_k)}{\nabla f(x_k)^TA\nabla f(x_k)}.
$$

Exact line search can be expensive because it requires solving a one-dimensional optimisation problem, although it is useful for analysis and some small simulations.

Armijo backtracking is a practical alternative. Start with a trial step $\alpha$, often $1$, and repeatedly replace it by $\rho\alpha$, where $0<\rho<1$, until

$$
 f(x-\alpha g)\leq f(x)-c\alpha\|g\|^2,
$$

where $g=\nabla f(x)$ and $0<c<1$. The right side demands a decrease proportional to the predicted first-order decrease. Backtracking adapts to local scale without requiring a known global $L$. In a mechanical model whose stiffness changes significantly between configurations, this local adaptation can be more useful than a single globally conservative step.

## 5. Convergence of basic gradient descent

Suppose $f$ is convex and $L$-smooth, has a minimiser $x^*$, and gradient descent uses $\alpha=1/L$. Then the objective error satisfies a sublinear bound of the form

$$
 f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k}.
$$

Thus the error decreases on the order of $1/k$. This is convergence, but not necessarily rapid convergence to high precision. The guarantee is about objective value; the iterates themselves may behave differently when minimisers are not unique.

If $f$ is additionally $\mu$-strongly convex, the minimiser is unique and gradient descent has a geometric, or linear, rate. With a suitable fixed step, for example $\alpha=1/L$, one obtains a bound such as

$$
 f(x_k)-f(x^*)\leq\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).
$$

The factor is close to one when $L/\mu$ is large. Rescaling variables can reduce this anisotropy. For instance, expressing a length in metres and a force in newtons rather than mixing millimetres and kilonewtons can substantially improve numerical conditioning.

These theorems assume exact gradients and an objective satisfying the stated global properties. Real finite-element, fluid, or contact simulations may be noisy, nonsmooth, or only locally smooth. A convergence statement should therefore be matched to the model and to the accuracy of the derivative calculation.

## 6. Heavy Ball and Nesterov acceleration

Momentum methods use previous motion to avoid repeatedly correcting direction in a long valley. The Heavy Ball method is

$$
 x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1}),
$$

with momentum parameter $\beta$. The extra term can carry the iterate through shallow directions, while the gradient controls the current descent. Poor parameters can cause oscillation, so momentum is not a guarantee of improvement for every objective.

Nesterov’s accelerated gradient evaluates the gradient at a look-ahead point. One form is

$$
 y_k=x_k+\beta_k(x_k-x_{k-1}),\qquad x_{k+1}=y_k-\alpha\nabla f(y_k).
$$

The distinction from Heavy Ball is important: the gradient is computed at $y_k$, not at $x_k$. For smooth convex objectives, appropriately selected Nesterov parameters improve the objective bound from order $1/k$ to order $1/k^2$. For strongly convex objectives, variants achieve rates depending on $\sqrt{L/\mu}$ rather than $L/\mu$. These results rely on carefully chosen schedules and assumptions; casually adding momentum does not reproduce the theorem.

## 7. Stochastic gradients and adaptive methods

When an objective is an average over many data samples or expensive simulation cases, use a stochastic gradient $g_k$ based on a mini-batch. A standard assumption is unbiasedness:

$$
\mathbb{E}[g_k\mid x_k]=\nabla f(x_k),
$$

together with bounded variance, for example

$$
\mathbb{E}[\|g_k-\nabla f(x_k)\|^2\mid x_k]\leq\sigma^2.
$$

The update remains $x_{k+1}=x_k-\alpha_kg_k$, but individual steps need not reduce the objective. For nonconvex problems, decreasing step sizes such as $\alpha_k\to0$ and conditions

$$
\sum_{k=0}^{\infty}\alpha_k=\infty,
\qquad
\sum_{k=0}^{\infty}\alpha_k^2<\infty
$$

are classical sufficient patterns. A schedule $\alpha_k=a/(k+1)^p$ satisfies both when $1/2<p\leq1$. Constant steps are often useful in practice, but they generally leave a noise-dependent error neighbourhood rather than converging exactly.

AdaGrad accumulates coordinate-wise squared gradients:

$$
 s_k=s_{k-1}+g_k\odot g_k,
\qquad
 x_{k+1}=x_k-\frac{\alpha}{\sqrt{s_k}+\varepsilon}\odot g_k.
$$

Coordinates with consistently large gradients receive smaller future steps. This is useful when design variables have different scales, but the ever-growing accumulator can eventually make learning too slow.

RMSProp replaces the unbounded sum with an exponential average:

$$
 v_k=\rho v_{k-1}+(1-\rho)g_k\odot g_k,
\qquad
 x_{k+1}=x_k-\frac{\alpha}{\sqrt{v_k}+\varepsilon}\odot g_k.
$$

Adam combines an exponential first-moment estimate and second-moment estimate:

$$
 m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,
\qquad
 v_k=\beta_2v_{k-1}+(1-\beta_2)g_k\odot g_k.
$$

Because both start at zero, use bias corrections $\hat m_k=m_k/(1-\beta_1^k)$ and $\hat v_k=v_k/(1-\beta_2^k)$, followed by

$$
 x_{k+1}=x_k-\alpha\frac{\hat m_k}{\sqrt{\hat v_k}+\varepsilon}.
$$

Adaptive methods are convenient, but their practical success is not the same as a basic convex convergence theorem. Monitor validation performance, gradient magnitudes, and physical feasibility, and remember that a dimensionless numerical update still needs variables with sensible units or scaling.

## 8. Newton and BFGS methods

Newton’s method uses a local quadratic model. At $x_k$, approximate

$$
 f(x_k+p)\approx f(x_k)+g_k^Tp+\tfrac12p^TH_kp,
$$

where $g_k=\nabla f(x_k)$ and $H_k=\nabla^2f(x_k)$. Setting the model gradient to zero gives the Newton direction from

$$
 H_kp_k=-g_k,
\qquad x_{k+1}=x_k+p_k.
$$

Near a solution with a positive-definite Hessian and an accurate model, Newton’s method can converge quadratically: the number of correct digits can roughly double near the optimum. However, forming and factorising a large Hessian is expensive. An indefinite Hessian can also produce an ascent direction, so line search, trust regions, or regularisation may be needed.

BFGS avoids computing the Hessian directly. It maintains a positive-definite approximation $B_k$ to the inverse Hessian. With $s_k=x_{k+1}-x_k$ and $y_k=g_{k+1}-g_k$, the inverse-Hessian update is

$$
 B_{k+1}=(I-\rho_ks_ky_k^T)B_k(I-\rho_ky_ks_k^T)+\rho_ks_ks_k^T,
\qquad
 \rho_k=\frac{1}{y_k^Ts_k}.
$$

The direction is $p_k=-B_kg_k$, normally combined with a line search. If $y_k^Ts_k>0$, BFGS preserves positive definiteness when $B_k$ starts positive definite. Limited-memory BFGS stores only a few vector pairs, making it suitable for large parameter spaces. Newton uses explicit second derivatives; BFGS learns curvature from successive gradients.

## 9. From equations to Python

A mathematical update becomes a short, testable Python loop. Use NumPy arrays, keep the gradient function separate, and avoid accidentally changing the current point before evaluating all quantities for one step. For gradient descent, the essential structure is:

```python
import numpy as np

def f(x):
    return 0.5 * x @ A @ x - b @ x

def grad_f(x):
    return A @ x - b

x = x0.copy()
for k in range(1000):
    g = grad_f(x)
    if np.linalg.norm(g) < 1e-8:
        break
    x = x - alpha * g
```

The matrix `A` should be symmetric for the stated quadratic interpretation, and positive definite for a unique unconstrained minimiser. Check array shapes and use `x0.copy()` so that the caller’s initial array is not unexpectedly modified. A line search must evaluate the trial objective before accepting the trial point. Adaptive methods need state arrays such as `m` and `v`, and they must use elementwise multiplication and division rather than matrix multiplication.

Numerical diagnostics include plotting objective value against iteration, checking whether the gradient norm decreases, and comparing results under different step sizes. In engineering, also inspect the final design in physical units. A decreasing objective does not by itself prove that stresses, temperatures, displacements, or safety factors remain acceptable when constraints have not been modelled.

## 10. Final exercise chapter

### Exercise 1: Scope of an optimality theorem

Let $f$ be differentiable and convex, and suppose $x^*$ satisfies $\nabla f(x^*)=0$. Explain why $x^*$ is a global minimiser. Then explain why the same conclusion cannot be drawn from the zero-gradient condition alone when convexity is removed.

#### Worked solution

Convexity gives

$$
 f(y)\geq f(x^*)+\nabla f(x^*)^T(y-x^*)
$$

for every $y$. Since the gradient is zero, this reduces to $f(y)\geq f(x^*)$. Therefore no point has a smaller objective value, so $x^*$ is a global minimiser. Without convexity, a stationary point can be a maximum or saddle point. For example, $f(x)=-x^2$ has $f'(0)=0$, but $x=0$ is a maximum, not a minimum. The theorem requires both differentiability and convexity; the stationarity condition by itself is only necessary for an interior differentiable local minimum.

### Exercise 2: One hand-calculated update

Consider the mechanical-design surrogate

$$
 f(x_1,x_2)=\tfrac12(4x_1^2+x_2^2),
$$

which penalises two scaled design variables. Starting from $x_0=(2,-1)^T$ and using step size $\alpha=0.2$, calculate the gradient at $x_0$, perform one gradient-descent update, and calculate the new objective value.

#### Worked solution

The gradient is

$$
\nabla f(x)=\begin{pmatrix}4x_1\\x_2\end{pmatrix}.
$$

At $x_0=(2,-1)^T$, this is $g_0=(8,-1)^T$. The update is

$$
 x_1=x_0-0.2g_0
 =\begin{pmatrix}2\\-1\end{pmatrix}
 -0.2\begin{pmatrix}8\\-1\end{pmatrix}
 =\begin{pmatrix}0.4\\-0.8\end{pmatrix}.
$$

The initial objective is $f(x_0)=\tfrac12(4\cdot2^2+(-1)^2)=8.5$. At the new point,

$$
 f(x_1)=\tfrac12\left(4(0.4)^2+(-0.8)^2\right)
 =\tfrac12(0.64+0.64)=0.64.
$$

The objective decreases substantially because the chosen step is below the stability limit for this quadratic. Notice that the first coordinate has the larger curvature and therefore makes the larger absolute movement.

### Exercise 3: Diagnosing Python gradient-descent code

The intended objective is $f(x)=\tfrac12x^TAx-b^Tx$, with symmetric positive-definite `A` and vectors `b` and `x0`. The following code is buggy:

```python
x = x0
for k in range(100):
    x = x - alpha * (A @ x)
    value = 0.5 * x @ A @ x - b @ x
    if np.linalg.norm(A @ x - b) < 1e-8:
        break
```

Identify the errors and provide corrected code that performs gradient descent and tests the gradient at the current iterate.

#### Worked solution

The gradient of the stated objective is $Ax-b$, not $Ax$. Omitting `- b` optimises a different function. Also, assigning `x = x0` makes `x` refer to the same mutable array as `x0`; a copy is safer when the initial point must be preserved. The objective evaluation is not wrong after the update, but recording the value after each accepted update is clearer. A corrected version is:

```python
import numpy as np

x = x0.copy()
for k in range(100):
    g = A @ x - b
    if np.linalg.norm(g) < 1e-8:
        break
    x = x - alpha * g
    value = 0.5 * x @ A @ x - b @ x
```

The stopping test now uses the true gradient before taking the next step. If the code needs the objective at the initial point or at every iteration, calculate it before the update as well. The step size must satisfy an appropriate stability condition, such as $0<\alpha<2/\lambda_{\max}(A)$ for this quadratic. If convergence is unexpectedly slow, inspect the condition number, scale the variables, or use a line search or a curvature-informed method such as BFGS.
