# Optimisation and Numerical Relaxation: A Practical Guide to Gradient-Based Methods

## 1. The optimisation problem and local tests

Unconstrained optimisation asks us to choose any vector $x\in\mathbb{R}^d$ to minimise an objective:

$$\min_{x\in\mathbb{R}^d} f(x).$$

The word objective is deliberate. In a mechanical model, $f$ might be potential energy, and a minimiser may represent a stable equilibrium. In many computational problems, however, $f$ is a loss, fitting error, or design score rather than a physical energy. Likewise, an iteration index $k$ is an algorithmic counter, not necessarily physical time. Numerical relaxation can resemble a system settling, but its update law and its convergence theory are mathematical rather than dynamical claims.

For a differentiable function, an interior local minimiser $x^*$ must satisfy the first-order necessary condition (FONC)

$$\nabla f(x^*)=0.$$

This says that every small directional change has zero first-order effect. It does not prove that $x^*$ is a minimum: a stationary point can be a maximum or a saddle. If $f\in C^2$, a local minimiser must also satisfy the second-order necessary condition

$$\nabla^2f(x^*)\succeq0,$$

meaning that the Hessian is positive semidefinite. If instead

$$\nabla f(x^*)=0\quad\text{and}\quad \nabla^2f(x^*)\succ0,$$

then the second-order sufficient condition gives a strict local minimiser. In physical language, positive curvature in every direction means a small displacement raises the local quadratic approximation of energy; in an arbitrary objective it simply means the same local mathematical geometry.

## 2. Smoothness, convexity, and conditioning

A differentiable function is $L$-smooth when its gradient is Lipschitz continuous:

$$\|\nabla f(x)-\nabla f(y)\|\le L\|x-y\|\qquad\forall x,y.$$

The constant $L$ bounds how rapidly the slope can change. The Descent Lemma, also called the quadratic upper-bound inequality, follows from this assumption:

$$f(y)\le f(x)+\langle\nabla f(x),y-x\rangle+\frac{L}{2}\|y-x\|^2.$$

Thus a smooth objective lies below a quadratic model built from its value and gradient at $x$. This is the key inequality behind safe gradient steps.

A differentiable $f$ is convex when its graph lies above every tangent plane:

$$f(y)\ge f(x)+\langle\nabla f(x),y-x\rangle.$$

For a convex function, every local minimiser is global. Strong convexity adds a quadratic margin, with parameter $\mu>0$:

$$f(y)\ge f(x)+\langle\nabla f(x),y-x\rangle+\frac\mu2\|y-x\|^2.$$

A strongly convex function has a unique minimiser when one exists, and its curvature is bounded away from zero.

For $f\in C^2$, the Hessian characterisations are especially useful. $L$-smoothness is equivalent to $\|\nabla^2f(x)\|_2\le L$ everywhere. If the function is also convex, this becomes

$$0\preceq\nabla^2f(x)\preceq LI.$$

Strong convexity is equivalent to

$$\nabla^2f(x)\succeq\mu I.$$

When both properties hold, the condition number is

$$\kappa=\frac L\mu\ge1.$$

A large $\kappa$ indicates a narrow valley: curvature changes greatly between directions. Such a geometry often explains slow numerical relaxation even when the gradient is easy to evaluate.

## 3. Gradient descent and step-size choices

Starting from $x_0$, gradient descent (GD) repeatedly moves opposite the gradient:

$$x_{k+1}=x_k-\alpha_k\nabla f(x_k).$$

The gradient is normal to a level surface, so the negative gradient is a local steepest-descent direction in the Euclidean norm. In code, the mathematical update consists of evaluating a gradient, multiplying it by a scalar step size, and subtracting the result from the current vector.

With a known smoothness constant, a constant step such as $\alpha=1/L$ is standard. Under the usual smooth convex assumptions, constant steps in $(0,2/L)$ are also commonly considered for descent behaviour. The step must be positive; too large a step can overshoot the useful local model.

Exact line search chooses the best distance along the current negative-gradient ray:

$$\alpha_k=\arg\min_{\alpha>0}f\bigl(x_k-\alpha\nabla f(x_k)\bigr).$$

It can be expensive because it requires solving a one-dimensional optimisation problem, but it removes the need to guess the best distance along that direction.

Armijo backtracking is a practical alternative. Choose a trial step $\bar\alpha>0$, contraction factor $\eta\in(0,1)$, and sufficient-decrease constant $c\in(0,1)$. Test $\alpha_k=\eta^m\bar\alpha$ for $m=0,1,\ldots$ until

$$f(x_k-\alpha_k\nabla f(x_k))\le f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.$$

The trial step is repeatedly shortened until the measured decrease is adequate.

## 4. Convergence of gradient descent

Suppose $f$ is convex and $L$-smooth, has a global minimiser $x^*$, and GD uses $\alpha=1/L$. Then for $k\ge1$,

$$f(x_k)-f(x^*)\le\frac{L\|x_0-x^*\|^2}{2k}.$$

This is an objective-gap bound of order $O(1/k)$. The Descent Lemma gives

$$f(x_{k+1})\le f(x_k)-\frac{1}{2L}\|\nabla f(x_k)\|^2,$$

and convexity converts the gradient-direction expression into a telescoping difference of squared distances. The bound requires convexity, smoothness, existence of a global minimiser, and the stated step size; it is not a guarantee for an arbitrary differentiable objective.

If $f$ is both $L$-smooth and $\mu$-strongly convex, GD has a faster linear, or geometric, guarantee. With the constant step

$$\alpha=\frac{2}{L+\mu},$$

one has the distance bound

$$\|x_k-x^*\|^2\le\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}\|x_0-x^*\|^2.$$

Alternatively, with $\alpha=1/L$, the objective gap satisfies

$$f(x_k)-f(x^*)\le\left(1-\frac\mu L\right)^k\bigl(f(x_0)-f(x^*)\bigr).$$

The factor depends on $\kappa=L/\mu$: a poorly conditioned problem contracts slowly. These are global results under the global smoothness and strong-convexity assumptions, not merely local curvature observations.

## 5. Momentum and acceleration

Polyak's Heavy Ball method adds the previous displacement to GD:

$$x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1}),\qquad\beta\in[0,1).$$

The momentum term can carry the iteration through a shallow direction while damping zig-zagging in a steep direction. Stability depends on the parameters and the objective; momentum is not automatically beneficial.

For the specific strongly convex quadratic $f(x)=\tfrac12x^TAx$, with $A$ symmetric positive definite and eigenvalues in $[\mu,L]$, the stated parameter choice is

$$\alpha^*=\frac4{(\sqrt L+\sqrt\mu)^2},\qquad\beta^*=\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^2.$$

In this quadratic setting, the contraction dependence improves from $1-O(1/\kappa)$ to $1-O(1/\sqrt\kappa)$. This claim is specifically for that spectral quadratic setting, not a universal promise for every nonlinear objective.

Nesterov's accelerated gradient (NAG) uses a look-ahead point. Set $y_0=x_0$ and $\lambda_0=1$. For each $k\ge0$,

$$x_{k+1}=y_k-\frac1L\nabla f(y_k),$$

$$\lambda_{k+1}=\frac{1+\sqrt{1+4\lambda_k^2}}2,$$

$$y_{k+1}=x_{k+1}+\frac{\lambda_k-1}{\lambda_{k+1}}(x_{k+1}-x_k).$$

The gradient is evaluated at $y_k$, not at $x_k$. For an $L$-smooth convex function with a global minimiser,

$$f(x_k)-f(x^*)\le\frac{2L\|x_0-x^*\|^2}{(k+1)^2}=O(1/k^2).$$

## 6. Stochastic objectives and adaptive methods

For a finite data or simulation set, consider

$$f(x)=\frac1N\sum_{i=1}^Nf_i(x).$$

A full gradient costs contributions from all $N$ terms. A stochastic gradient $g_k(x_k)$ is cheaper and is assumed conditionally unbiased:

$$\mathbb E[g_k(x_k)\mid x_k]=\nabla f(x_k).$$

A common noise model also assumes bounded conditional variance:

$$\mathbb E[\|g_k(x_k)-\nabla f(x_k)\|^2\mid x_k]\le\sigma^2.$$

SGD uses $x_{k+1}=x_k-\eta_kg_k(x_k)$. With persistent nonzero variance, a small constant step generally reaches a nonzero error floor: random gradient fluctuations keep the iterates in a neighbourhood rather than yielding exact convergence. Diminishing steps are governed by the Robbins--Monro conditions

$$\sum_{k=1}^{\infty}\eta_k=\infty,\qquad\sum_{k=1}^{\infty}\eta_k^2<\infty.$$

These conditions alone are not a complete theorem: objective regularity, bias and moment assumptions, and iterate stability are also needed.

Adaptive methods rescale coordinates element by element. In every formula below, $\odot$ means element-wise multiplication, the square root and division are element-wise, and $\epsilon>0$ prevents division by zero.

AdaGrad starts with $v_{-1}=0$:

$$v_k=v_{k-1}+g_k\odot g_k,\qquad x_{k+1}=x_k-\frac\eta{\sqrt{v_k}+\epsilon}\odot g_k.$$

RMSProp also starts with $v_{-1}=0$, but forgets old gradients using $\gamma\in[0,1)$:

$$v_k=\gamma v_{k-1}+(1-\gamma)(g_k\odot g_k),\qquad x_{k+1}=x_k-\frac\eta{\sqrt{v_k}+\epsilon}\odot g_k.$$

Adam starts with $m_{-1}=v_{-1}=0$ and uses first and second moving averages:

$$m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,$$

$$v_k=\beta_2v_{k-1}+(1-\beta_2)(g_k\odot g_k).$$

Because zero initialisation biases early averages toward zero, correct them (for zero-based indexing) by

$$\hat m_k=\frac{m_k}{1-\beta_1^{k+1}},\qquad\hat v_k=\frac{v_k}{1-\beta_2^{k+1}}.$$

The Adam update is

$$x_{k+1}=x_k-\frac\eta{\sqrt{\hat v_k}+\epsilon}\odot\hat m_k.$$

These methods change coordinate scaling; they do not change the distinction between an algorithmic iteration and physical time.

## 7. Newton and BFGS second-order methods

Newton's method minimises a local second-order model. For a trial displacement $p$,

$$f(x_k+p)\approx f(x_k)+\nabla f(x_k)^Tp+\frac12p^T\nabla^2f(x_k)p.$$

Setting the model gradient to zero gives the linear system

$$\nabla^2f(x_k)p_k=-\nabla f(x_k),\qquad x_{k+1}=x_k+p_k.$$

Although this is algebraically an inverse-Hessian multiplication, numerical implementations solve the linear system rather than explicitly forming an inverse. If $\nabla f(x^*)=0$, the Hessian at $x^*$ is positive definite, the Hessian is Lipschitz continuous near $x^*$, and the initial point is sufficiently close, Newton is locally well defined and satisfies

$$\|x_{k+1}-x^*\|\le C\|x_k-x^*\|^2.$$

This quadratic local convergence is powerful but local; far from the solution, a line search or damping may be needed.

BFGS avoids calculating the Hessian directly. Define the step and gradient difference

$$s_k=x_{k+1}-x_k,\qquad y_k=\nabla f(x_{k+1})-\nabla f(x_k).$$

An approximation $B_{k+1}$ to the Hessian is required to satisfy the secant equation $B_{k+1}s_k=y_k$. The inverse-Hessian form updates $H_k\approx[\nabla^2f(x_k)]^{-1}$ by

$$H_{k+1}=(I-\rho_ks_ky_k^T)H_k(I-\rho_ky_ks_k^T)+\rho_ks_ks_k^T,$$

where $\rho_k=1/(y_k^Ts_k)$. The curvature condition $y_k^Ts_k>0$ is essential for the usual positive-definite behaviour. The search direction is

$$p_k=-H_k\nabla f(x_k).$$

A line search chooses $x_{k+1}=x_k+\alpha_kp_k$ and helps obtain a useful step and curvature pair. BFGS therefore combines gradient information, an evolving curvature approximation, and line search rather than requiring a fresh Hessian factorisation at every iteration.

## 8. A short executable implementation

The following program applies GD to a quadratic potential-like objective. It makes each mathematical operation visible: the gradient is evaluated at the current vector, the scalar step is multiplied by that gradient, and the result is subtracted. The objective is merely an example; the iteration is not asserted to be physical time evolution.

```python
import numpy as np

A = np.diag([1.0, 4.0])
x = np.array([3.0, -2.0])
alpha = 1.0 / 4.0  # 1/L because the largest eigenvalue is L = 4

for k in range(12):
    value = 0.5 * x @ A @ x       # f(x)
    gradient = A @ x               # nabla f(x)
    print(f"{k:2d}: f={value:.6f}, x={x}")
    x = x - alpha * gradient       # x_{k+1}=x_k-alpha*nabla f(x_k)
```

## 9. Exercises and worked solutions

### Exercise 1 — Conceptual theorem-scope check

A colleague claims: “If an objective is differentiable and GD uses a positive step, then the iterates converge to its global minimiser at rate $O(1/k)$.” Identify which parts of this statement are unsupported. State the assumptions and step size needed for the convex objective-gap theorem, and separately state the stronger assumptions behind a linear strongly convex result.

#### Worked solution

Differentiability and a positive step are insufficient. The objective may be non-convex, may have no global minimiser, and a large step may fail to decrease it. For the $O(1/k)$ bound, the source requires convexity, $L$-smoothness, a global minimiser $x^*$, and the constant step $\alpha=1/L$. Then

$$f(x_k)-f(x^*)\le L\|x_0-x^*\|^2/(2k).$$

For the linear objective-gap result, require both $L$-smoothness and $\mu$-strong convexity and use $\alpha=1/L$:

$$f(x_k)-f(x^*)\le(1-\mu/L)^k(f(x_0)-f(x^*)).$$

The theorem assumptions, rather than the fact that a method is called GD, supply the guarantee.

### Exercise 2 — Hand calculation

Let $f(x)=\tfrac12x^TAx$ with $A=\operatorname{diag}(1,4)$, $x_0=(2,-1)^T$, and use $\alpha=1/4$. Compute $\nabla f(x_0)$, $x_1$, $f(x_0)$, and $f(x_1)$. Interpret the result as numerical relaxation without calling $k$ physical time.

#### Worked solution

For this quadratic, $\nabla f(x)=Ax$. Therefore

$$\nabla f(x_0)=\begin{pmatrix}1&0\\0&4\end{pmatrix}\begin{pmatrix}2\\-1\end{pmatrix}=\begin{pmatrix}2\\-4\end{pmatrix}.$$

The update is

$$x_1=x_0-\frac14\nabla f(x_0)=\begin{pmatrix}2\\-1\end{pmatrix}-\frac14\begin{pmatrix}2\\-4\end{pmatrix}=\begin{pmatrix}1.5\\0\end{pmatrix}.$$

The initial value is

$$f(x_0)=\tfrac12(1\cdot2^2+4\cdot(-1)^2)=4,$$

and the new value is

$$f(x_1)=\tfrac12(1\cdot1.5^2+4\cdot0^2)=1.125.$$

The objective has decreased substantially in one algorithmic iteration. This resembles relaxation toward equilibrium, but it is a discrete numerical update, not a claim about the physical trajectory or elapsed time of a mechanical system.

### Exercise 3 — Python code-diagnostic exercise

The following program is executable, but its update is mathematically incorrect for gradient descent on $f(x)=\tfrac12x^2$. Identify the algorithmic error and predict its behaviour.

```python
x = 2.0
alpha = 0.2
for k in range(10):
    gradient = x
    x = x + alpha * gradient       # claimed gradient-descent update
    print(k, x)
```

#### Worked solution

The gradient is $\nabla f(x)=x$. Gradient descent must subtract the step, $x_{k+1}=x_k-\alpha x_k$. The program adds it, so it performs ascent on this positive-curvature quadratic. Its recurrence is $x_{k+1}=1.2x_k$, hence $x_k=2(1.2)^k$: the magnitude grows and the objective increases.

A corrected, distinct executable program is:

```python
x = 2.0
alpha = 0.2
for k in range(10):
    value = 0.5 * x * x
    gradient = x
    x = x - alpha * gradient       # x_{k+1}=x_k-alpha*nabla f(x_k)
    print(k, value, x)
```

The corrected recurrence is $x_{k+1}=0.8x_k$, so $x_k=2(0.8)^k$ tends to zero and $f(x_k)$ decreases toward its minimum value $0$. The code uses a constant step with $0<\alpha<2/L$ because here $L=1$; the sign and the step-size range are both relevant to the expected numerical behaviour.
