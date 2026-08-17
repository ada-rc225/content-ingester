## 1. From equilibrium to optimisation

Mechanical engineering often asks for a configuration in which a system is in equilibrium. A useful entry point is potential energy: a stable configuration can be associated with a locally low value of an energy-like quantity, and numerical relaxation can move a trial configuration towards a lower value. We will use this picture to build intuition for optimisation. The limitation is important: an optimisation objective need not be a physical energy, and the iterations of an algorithm should not automatically be interpreted as physical time evolution.

The mathematical problem considered here is unconstrained optimisation:

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where $f:\mathbb{R}^d\to\mathbb{R}$ is at least continuously differentiable, written $f\in C^1$. The vector $x$ may contain design variables, parameters, or coordinates describing a trial state. “Unconstrained” means that, in this model, every vector in $\mathbb{R}^d$ is an allowable input; there are no explicit bounds or equality constraints.

### Stationarity and local optimality

At a differentiable local minimiser $x^*$, the first-order necessary condition is

$$
\nabla f(x^*)=0.
$$

This says that there is no first-order downhill direction at the point. It is a necessary condition, not by itself a guarantee of a minimum: a stationary point can also be a maximum or a saddle point.

If $f\in C^2$, the Hessian $\nabla^2 f(x^*)$ describes the second-order curvature. A local minimiser must satisfy

$$
\nabla f(x^*)=0,\qquad \nabla^2 f(x^*)\succeq 0,
$$

where positive semidefinite means that $z^T\nabla^2f(x^*)z\geq0$ for every vector $z$. Conversely, if

$$
\nabla f(x^*)=0,\qquad \nabla^2 f(x^*)\succ0,
$$

then $x^*$ is a strict local minimiser. Positive definiteness means strictly positive quadratic curvature in every nonzero direction. These conditions are local: they do not, without further assumptions, identify a global minimiser.

First-order algorithms use values of $f$ and gradients to generate a sequence $x_0,x_1,x_2,\ldots$. Whether the sequence approaches a stationary point or a global minimiser depends on the objective assumptions, the step-size rule, and the algorithm.

## 2. Smoothness, convexity, and conditioning

Convergence statements become quantitative when the objective has useful structure.

### Smoothness and the descent bound

A continuously differentiable function is $L$-smooth, or has an $L$-Lipschitz continuous gradient, if $L>0$ and

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|,
\qquad \forall x,y\in\mathbb{R}^d.
$$

The gradient cannot change arbitrarily rapidly. The corresponding descent lemma gives the quadratic upper bound

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle+\frac{L}{2}\|y-x\|^2.
$$

The linear term predicts the immediate change from the gradient; the quadratic term controls the error in that prediction. For a trial displacement $y-x=-\alpha\nabla f(x)$, the bound becomes

$$
f(y)\leq f(x)-\alpha\|\nabla f(x)\|^2+\frac{L\alpha^2}{2}\|\nabla f(x)\|^2.
$$

Thus a sufficiently controlled step can lower the objective.

If $f\in C^2$, $L$-smoothness is equivalent to $\|\nabla^2f(x)\|_2\leq L$ for every $x$. If the function is also convex, this is equivalently

$$
0\preceq\nabla^2f(x)\preceq LI.
$$

### Convexity and strong convexity

A differentiable function is convex if

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle,
\qquad \forall x,y.
$$

The graph lies above every tangent-plane approximation. Convexity is valuable because any local minimiser is then a global minimiser, provided a minimiser exists.

A function is $\mu$-strongly convex for $\mu>0$ if

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle+\frac{\mu}{2}\|y-x\|^2,
\qquad \forall x,y.
$$

The extra quadratic term expresses a uniform amount of upward curvature. For $C^2$ functions,

$$
f\text{ is $\mu$-strongly convex}\iff \nabla^2f(x)\succeq\mu I\quad\forall x.
$$

If $f$ is both $L$-smooth and $\mu$-strongly convex, its condition number is

$$
\kappa=\frac{L}{\mu}\geq1.
$$

A large $\kappa$ indicates a badly conditioned objective: curvature varies substantially between directions. In a mechanical analogy, a relaxation path can make progress rapidly in a stiff direction while moving slowly along a soft direction. The numerical method must respect the largest curvature while trying to make progress in the smallest-curvature direction.

## 3. Gradient descent and step-size selection

Standard gradient descent starts at a specified $x_0\in\mathbb{R}^d$ and uses positive step sizes $\alpha_k$:

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),\qquad k=0,1,2,\ldots.
$$

The negative gradient is the direction of steepest local decrease in the Euclidean norm. The step size controls how far the algorithm moves in that direction. A step that is too small may be safe but slow; a step that is too large can overshoot and fail to descend.

### Common choices

If $L$ is known, a constant step often used is $\alpha_k=\alpha=1/L$. Under the usual smooth convex assumptions, a constant step in $(0,2/L)$ is also a common allowable range. The relevant assumptions still matter: a numerical value selected without regard to smoothness can be unsuitable.

Exact line search chooses the best positive distance along the current negative-gradient ray:

$$
\alpha_k=\arg\min_{\alpha>0}f\bigl(x_k-\alpha\nabla f(x_k)\bigr).
$$

This can be expensive because it requires solving a one-dimensional optimisation problem at every iteration.

Backtracking line search starts with a trial step $\bar\alpha>0$, a contraction factor $\eta\in(0,1)$, and $c\in(0,1)$. It tests $\alpha_k=\eta^m\bar\alpha$ and chooses the smallest integer $m\geq0$ satisfying the Armijo condition

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)
\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
$$

The right-hand side demands a sufficient reduction relative to the gradient magnitude. If the trial step fails, multiplying it by $\eta$ makes the next trial smaller.

## 4. What convergence guarantees say

For an $L$-smooth convex function with a global minimiser $x^*$, gradient descent with $\alpha_k=1/L$ satisfies, for $k\geq1$,

$$
f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k}.
$$

This is an $O(1/k)$ objective-gap rate. It is a bound under the stated assumptions, not a claim that every objective or every step-size choice behaves this way.

The key calculation starts with the descent lemma:

$$
f(x_{k+1})\leq f(x_k)-\frac{1}{2L}\|\nabla f(x_k)\|^2.
$$

Convexity gives

$$
f(x_k)-f(x^*)\leq\langle\nabla f(x_k),x_k-x^*\rangle.
$$

Using $x_{k+1}=x_k-\nabla f(x_k)/L$, these combine into

$$
f(x_{k+1})-f(x^*)
\leq\frac{L}{2}\left(\|x_k-x^*\|^2-\|x_{k+1}-x^*\|^2\right).
$$

Summing over iterations makes the distance terms telescope. Since the objective values are non-increasing, the sum yields the stated $1/k$ bound.

Strong convexity gives a faster form of convergence. If $f$ is both $L$-smooth and $\mu$-strongly convex, then with

$$
\alpha=\frac{2}{L+\mu},
$$

we have

$$
\|x_k-x^*\|^2\leq
\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}\|x_0-x^*\|^2.
$$

Alternatively, with $\alpha=1/L$,

$$
f(x_k)-f(x^*)\leq
\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).
$$

The factor is geometric, often called linear convergence in optimisation terminology. Conditioning appears directly: when $\kappa=L/\mu$ is large, the factor is closer to one and progress is slower.

## 5. Momentum and acceleration

Gradient descent uses only the current gradient. Momentum also uses recent displacement. Polyak’s heavy-ball update is

$$
x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1}),
$$

where $\beta\in[0,1)$. The previous movement can help carry the iteration through directions in which successive gradients point consistently, but parameters must be chosen to keep the iteration stable.

For the strongly convex quadratic

$$
f(x)=\frac12x^TAx,
$$

with symmetric positive-definite $A$ whose spectrum lies in $[\mu,L]$, the parameter choices

$$
\alpha^*=\frac{4}{(\sqrt L+\sqrt\mu)^2},\qquad
\beta^*=\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^2
$$

improve the condition-number dependence of the contraction factor from $1-O(1/\kappa)$ to $1-O(1/\sqrt\kappa)$. These particular parameter claims apply to the stated quadratic setting.

Nesterov’s accelerated-gradient variant for smooth convex functions uses a look-ahead point. Initialise $y_0=x_0$ and $\lambda_0=1$. For $k\geq0$,

$$
x_{k+1}=y_k-\frac1L\nabla f(y_k),
$$

then compute

$$
\lambda_{k+1}=\frac{1+\sqrt{1+4\lambda_k^2}}2,
$$

and

$$
y_{k+1}=x_{k+1}+\frac{\lambda_k-1}{\lambda_{k+1}}(x_{k+1}-x_k).
$$

The gradient is evaluated at $y_k$, not at $x_k$. For an $L$-smooth convex function with global minimiser $x^*$, this parameterisation gives

$$
f(x_k)-f(x^*)\leq\frac{2L\|x_0-x^*\|^2}{(k+1)^2}=O(1/k^2).
$$

## 6. Stochastic and adaptive methods

Suppose the objective is an empirical average,

$$
f(x)=\frac1N\sum_{i=1}^Nf_i(x).
$$

A full gradient costs $O(N)$ evaluations. Stochastic gradient descent replaces it with $g_k(x_k)$ and updates

$$
x_{k+1}=x_k-\eta_kg_k(x_k).
$$

The source assumptions are conditional unbiasedness,

$$
\mathbb E[g_k(x_k)\mid x_k]=\nabla f(x_k),
$$

and bounded conditional variance,

$$
\mathbb E[\|g_k(x_k)-\nabla f(x_k)\|^2\mid x_k]\leq\sigma^2.
$$

With persistent nonzero variance, a sufficiently small constant step generally approaches a nonzero error floor rather than exact convergence. Diminishing steps may satisfy the Robbins–Monro conditions

$$
\sum_{k=1}^{\infty}\eta_k=\infty,\qquad
\sum_{k=1}^{\infty}\eta_k^2<\infty,
$$

but these conditions alone are not sufficient for a convergence theorem. Objective assumptions, stochastic-gradient bias and moments, and iterate stability must also be specified.

Adaptive methods rescale coordinates using accumulated gradient information. With element-wise products denoted by $\odot$ and $\epsilon>0$ preventing division by zero, AdaGrad starts at $v_{-1}=0$ and uses

$$
v_k=v_{k-1}+g_k\odot g_k,
$$

$$
x_{k+1}=x_k-\frac\eta{\sqrt{v_k}+\epsilon}\odot g_k.
$$

RMSProp instead uses $v_{-1}=0$, $\gamma\in[0,1)$, and

$$
v_k=\gamma v_{k-1}+(1-\gamma)g_k\odot g_k,
$$

with the same rescaled update. Adam maintains first and second moments, starting at $m_{-1}=v_{-1}=0$:

$$
m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,
$$

$$
v_k=\beta_2v_{k-1}+(1-\beta_2)(g_k\odot g_k).
$$

For zero-based indexing, bias correction is essential in the supplied update:

$$
\hat m_k=\frac{m_k}{1-\beta_1^{k+1}},\qquad
\hat v_k=\frac{v_k}{1-\beta_2^{k+1}},
$$

followed by

$$
x_{k+1}=x_k-\frac\eta{\sqrt{\hat v_k}+\epsilon}\odot\hat m_k.
$$

## 7. Newton and quasi-Newton methods

Gradient descent approximates the objective locally with a plane plus a controlled curvature bound. Newton’s method uses the local quadratic model

$$
f(x_k+p)\approx f(x_k)+\nabla f(x_k)^Tp+\frac12p^T\nabla^2f(x_k)p.
$$

Its step solves the linear system

$$
\nabla^2f(x_k)p_k=-\nabla f(x_k),
$$

and then $x_{k+1}=x_k+p_k$. Although this is mathematically equivalent to multiplying by the inverse Hessian when it is invertible, an implementation should solve the linear system rather than explicitly form the inverse.

If $\nabla f(x^*)=0$, the Hessian at $x^*$ is positive definite, and $\nabla^2f$ is Lipschitz continuous near $x^*$, then sufficiently close initialisation gives local quadratic convergence:

$$
\|x_{k+1}-x^*\|\leq C\|x_k-x^*\|^2
$$

for some $C>0$. The “local” and “sufficiently close” qualifications are part of the theorem.

Quasi-Newton methods avoid computing the exact Hessian by building $B_k\approx\nabla^2f(x_k)$ or $H_k\approx[\nabla^2f(x_k)]^{-1}$. Define

$$
s_k=x_{k+1}-x_k,\qquad y_k=\nabla f(x_{k+1})-\nabla f(x_k).
$$

The Hessian approximation obeys the secant equation $B_{k+1}s_k=y_k$. For $y_k^Ts_k>0$, inverse-Hessian BFGS uses

$$
H_{k+1}=(I-\rho_ks_ky_k^T)H_k(I-\rho_ky_ks_k^T)+\rho_ks_ks_k^T,
\qquad \rho_k=\frac1{y_k^Ts_k}.
$$

The search direction is $p_k=-H_k\nabla f(x_k)$. In practice, a line search gives $x_{k+1}=x_k+\alpha_kp_k$ and supports the curvature condition.

## 8. Translating updates into Python

A direct implementation should keep the mathematical roles visible: store the current vector, evaluate the gradient at the point required by the method, update any state variables, and then form the next vector. For basic gradient descent, `grad(x)` returns a NumPy vector and `alpha` is a positive scalar. The loop below records objective values so that numerical relaxation can be inspected.

```python
import numpy as np

def gradient_descent(x0, grad, value, alpha, steps):
    x = np.array(x0, dtype=float)
    history = [value(x)]
    for _ in range(steps):
        g = grad(x)
        x = x - alpha * g
        history.append(value(x))
    return x, history

# f(x) = 0.5 * x^T A x, with A positive definite
A = np.diag([1.0, 4.0])
value = lambda x: 0.5 * x @ A @ x
grad = lambda x: A @ x
x_final, history = gradient_descent([2.0, 1.0], grad, value,
                                    alpha=1.0 / 4.0, steps=20)
print(x_final)
print(history[-1])
```

For a code check, verify the sign, the point at which the gradient is evaluated, the step-size scale, and the indexing of stored state. For Adam, for example, `m` and `v` must be initialised to zero before the first gradient, and zero-based iteration requires the powers $k+1$ in bias correction.

## Exercises

### Exercise 1 — Conceptual and theorem-scope check

A student says: “If gradient descent is run on any differentiable objective with a small positive step, the iterates must converge to the global minimum at the $O(1/k)$ rate.” Identify every part of this statement that is not justified by the supplied convergence theorem. State the assumptions and step-size rule that do justify the $O(1/k)$ objective-gap bound.

#### Worked solution

The statement is too broad in four ways. Differentiability alone does not provide the smoothness bound needed for the descent analysis. The theorem assumes an $L$-smooth function. It also assumes convexity and a global minimiser $x^*$. Without convexity, a stationary point need not be globally optimal, and the theorem does not apply. “A small positive step” is not the theorem’s specified rule: the stated result uses $\alpha_k=1/L$. Finally, the theorem gives an objective-gap bound, not an unrestricted claim that every sequence converges to a global minimiser. Under the correct assumptions—$f$ is $L$-smooth and convex, $x^*$ is a global minimiser, and $\alpha_k=1/L$—the result is

$$
f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k},\qquad k\geq1.
$$

### Exercise 2 — Hand calculation

Let $f(x)=\tfrac12x^TAx$ with $A=\operatorname{diag}(1,4)$, and start at $x_0=(2,1)^T$. Use gradient descent with $\alpha=1/L$, where $L=4$. Calculate $x_1$, $f(x_0)$, and $f(x_1)$. Then calculate the strongly convex bound using $\mu=1$, $L=4$, and $k=1$:

$$
f(x_1)-f(x^*)\leq\left(1-\frac\mu L\right)(f(x_0)-f(x^*)).
$$

#### Worked solution

Here $\nabla f(x)=Ax$, so

$$
\nabla f(x_0)=A\begin{bmatrix}2\\1\end{bmatrix}
=\begin{bmatrix}2\\4\end{bmatrix}.
$$

Since $\alpha=1/4$,

$$
x_1=x_0-\frac14\nabla f(x_0)
=\begin{bmatrix}2\\1\end{bmatrix}-\frac14\begin{bmatrix}2\\4\end{bmatrix}
=\begin{bmatrix}1.5\\0\end{bmatrix}.
$$

The minimiser is $x^*=(0,0)^T$, and

$$
f(x_0)=\frac12(1\cdot2^2+4\cdot1^2)=4,
$$

$$
f(x_1)=\frac12(1\cdot1.5^2+4\cdot0^2)=1.125.
$$

The bound’s factor is $1-\mu/L=1-1/4=0.75$. Therefore it predicts

$$
f(x_1)-f(x^*)\leq0.75(4-0)=3.
$$

The actual gap, $1.125$, satisfies the bound. The bound is not required to equal the observed decrease.

### Exercise 3 — Code diagnosis with executable Python

The following program is intended to run gradient descent on the same quadratic, but it has two update errors. Identify and correct them, then run the corrected code and explain why the objective should decrease for the selected step.

```python
import numpy as np

A = np.diag([1.0, 4.0])
x = np.array([2.0, 1.0])
alpha = 1.0 / 4.0

for _ in range(20):
    g = A @ x
    x = x + alpha * g

print(x)
```

#### Worked solution

The first error is the sign. Gradient descent subtracts the gradient, so the update must be `x = x - alpha * g`. The second issue is not a mistaken line of algebra but a missing diagnostic: the program does not evaluate the objective, so it cannot demonstrate descent. The corrected executable version is:

```python
import numpy as np

A = np.diag([1.0, 4.0])
x = np.array([2.0, 1.0], dtype=float)
alpha = 1.0 / 4.0

for _ in range(20):
    value_before = 0.5 * x @ A @ x
    g = A @ x
    x = x - alpha * g
    value_after = 0.5 * x @ A @ x
    print(value_before, value_after)

print("final x:", x)
```

The original plus sign moves in the uphill direction for this quadratic. The corrected minus sign follows $x_{k+1}=x_k-\alpha\nabla f(x_k)$. Here $L=4$ and $\alpha=1/L$, so the smooth-convex descent result applies; the printed objective values should be non-increasing. The first coordinate is multiplied by $1-\alpha\cdot1=0.75$, while the second coordinate is multiplied by $1-\alpha\cdot4=0$, so the second component becomes zero after one update. The code therefore provides a concrete check of both the mathematical update and its implementation meaning.

## Closing perspective

The central workflow is to identify the objective assumptions, select an update and step-size rule compatible with them, and inspect the resulting numerical sequence. Smoothness controls how far a gradient model can be trusted; convexity connects local information to global minimisation; strong convexity and conditioning determine a geometric rate; momentum changes the iteration using previous displacement; stochastic methods trade exact gradients for cheaper noisy estimates; and Newton or quasi-Newton methods incorporate curvature. In every case, the equations specify exactly where gradients are evaluated, how state is initialised, and which theorem conditions support the expected behaviour.
