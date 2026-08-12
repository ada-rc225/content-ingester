# Gradient Descent and Optimisation

## 1. Why optimisation matters in mechanical engineering

Many mechanical-engineering decisions can be expressed as choosing a vector of design or model parameters. Let $x\in\mathbb{R}^d$ contain quantities such as a beam thickness, a damping coefficient, or parameters in a reduced-order model. An objective $f(x)$ measures cost, weight, tracking error, or disagreement with experimental data. Unconstrained optimisation asks for

$$
\min_{x\in\mathbb{R}^d} f(x).
$$

Although real designs often have bounds and safety constraints, the unconstrained problem is an important local model and the foundation for the algorithms studied here. A method generates iterates $x_0,x_1,\ldots$ using values of the objective, its derivatives, or estimates of its derivatives.

At a local minimiser $x^*$, no sufficiently small displacement can reduce the objective. If $f$ is differentiable, this implies the first-order necessary condition

$$
\nabla f(x^*)=0.
$$

This condition identifies a stationary point, not necessarily a minimum. For example, a stationary point can be a maximum or a saddle point. If $f\in C^2$, a local minimiser must also satisfy the second-order necessary condition

$$
\nabla^2 f(x^*)\succeq 0,
$$

meaning that the Hessian is positive semidefinite: $z^T\nabla^2 f(x^*)z\geq0$ for every direction $z$. Conversely, if the gradient vanishes and

$$
\nabla^2f(x^*)\succ0,
$$

then $x^*$ is a strict local minimiser. Positive definiteness means that every nonzero direction has positive second directional curvature. These tests are local; they do not, by themselves, compare distant designs.

## 2. Smoothness, convexity, and curvature

A quantitative analysis needs assumptions on how rapidly the objective can change. A function is $L$-smooth, or has an $L$-Lipschitz gradient, when

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|\quad\text{for all }x,y.
$$

The number $L$ bounds gradient variation. For a twice differentiable function, $\|\nabla^2f(x)\|_2\leq L$ is an equivalent characterisation. Smoothness gives the descent lemma, a quadratic upper bound:

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle+\frac{L}{2}\|y-x\|^2.
$$

The linear term predicts the change using the current gradient; the quadratic term allows for curvature. In a mechanical interpretation, $L$ is a worst-case stiffness of the objective landscape in parameter space. Taking $y=x-\alpha\nabla f(x)$ makes the linear term negative, while the quadratic term limits how large a safe step can be.

A differentiable function is convex when every tangent plane lies below its graph:

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle.
$$

For a twice differentiable function this is equivalent to $\nabla^2f(x)\succeq0$ everywhere. Convexity is powerful because every local minimiser is global, and a stationary point is therefore a global minimiser.

A function is $\mu$-strongly convex when the tangent-plane inequality includes a uniform quadratic gap:

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle+\frac{\mu}{2}\|y-x\|^2,
$$

where $\mu>0$. In the $C^2$ case, this means $\nabla^2f(x)\succeq\mu I$. Strong convexity gives a unique minimiser and prevents very flat directions. If a function is both $L$-smooth and $\mu$-strongly convex, its condition number is $\kappa=L/\mu$. A large $\kappa$ describes an elongated valley, much like a poorly scaled stiffness or parameter-identification problem, and usually slows basic gradient descent.

## 3. Gradient descent and choosing a step

The gradient points in the direction of greatest local increase, so the negative gradient is a descent direction whenever the gradient is nonzero. Gradient descent updates according to

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),
$$

with positive step size $\alpha_k$. The formula is simple, but its behaviour depends critically on the step rule. If the step is too small, progress is safe but slow; if it is too large, the iteration can overshoot or diverge.

When $L$ is known, the standard choice $\alpha=1/L$ is guaranteed to provide useful descent for smooth convex objectives. More generally, the usual smooth setting permits constant steps in $(0,2/L)$, with the precise guarantee depending on the assumptions and rate being claimed. Estimating $L$ can be difficult for a simulation with changing stiffness, so line searches are useful.

Exact line search chooses the best distance along the current descent ray:

$$
\alpha_k=\arg\min_{\alpha>0}f\bigl(x_k-\alpha\nabla f(x_k)\bigr).
$$

For a quadratic this one-dimensional minimisation may have a closed form; otherwise it requires additional objective evaluations and a one-dimensional solver. It can be computationally expensive, but it illustrates the idea of separating a direction choice from a distance choice.

Armijo backtracking is cheaper and more robust. Choose a trial step $\bar\alpha>0$, a reduction factor $\eta\in(0,1)$, and a small constant $c\in(0,1)$. Test $\alpha=\bar\alpha,\eta\bar\alpha,\eta^2\bar\alpha,\ldots$ until

$$
f(x_k-\alpha\nabla f(x_k))
\leq f(x_k)-c\alpha\|\nabla f(x_k)\|^2.
$$

The right side demands a sufficient decrease proportional to the predicted first-order decrease. In code, evaluate the gradient once for the iteration, test trial points, and only accept a step when the condition holds. Backtracking is particularly helpful when a single global curvature estimate is unavailable.

## 4. What convergence means

For an $L$-smooth convex function with a global minimiser $x^*$, gradient descent with $\alpha=1/L$ has the objective guarantee

$$
f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k},\qquad k\geq1.
$$

This is an $O(1/k)$ rate. It does not mean that the error is exactly a fixed fraction smaller at every iteration. Rather, the upper bound decreases inversely with iteration count. The proof uses the descent lemma to obtain

$$
f(x_{k+1})\leq f(x_k)-\frac{1}{2L}\|\nabla f(x_k)\|^2,
$$

then combines convexity with the update to produce a telescoping bound on successive squared distances to $x^*$. The objective values are non-increasing, so the average bound also controls the final iterate.

Strong convexity improves the result from sublinear to linear, meaning geometric decay. If $f$ is both $L$-smooth and $\mu$-strongly convex, the step $\alpha=2/(L+\mu)$ gives

$$
\|x_k-x^*\|^2\leq\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}\|x_0-x^*\|^2.
$$

With $\alpha=1/L$, a standard objective bound is

$$
f(x_k)-f(x^*)\leq\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).
$$

Thus conditioning matters: when $\mu$ is small compared with $L$, the contraction factor is close to one. These theorems require their stated assumptions. Applying an $O(1/k)$ or geometric claim to a nonconvex engineering model without justification is not valid, even if the iteration appears to work numerically.

## 5. Momentum and acceleration

Momentum uses recent motion to avoid repeatedly correcting across a narrow valley. Polyak's Heavy Ball method is

$$
x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1}),
$$

where $\beta\in[0,1)$. The second term carries velocity from the previous step. It can accelerate progress along a shallow direction, but inappropriate parameters can create oscillations or instability.

For the strongly convex quadratic $f(x)=\tfrac12x^TAx$, with symmetric positive-definite $A$ whose eigenvalues lie in $[\mu,L]$, the classical parameter choices are

$$
\alpha^*=\frac{4}{(\sqrt L+\sqrt\mu)^2},\qquad
\beta^*=\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^2.
$$

In that stated quadratic setting, the condition-number dependence improves from $1-O(1/\kappa)$ to $1-O(1/\sqrt\kappa)$. The qualification matters: these parameters are not an unconditional guarantee for every nonlinear objective.

Nesterov's accelerated gradient method uses a look-ahead point. Set $y_0=x_0$ and $\lambda_0=1$. For each iteration,

$$
x_{k+1}=y_k-\frac1L\nabla f(y_k),
$$

$$
\lambda_{k+1}=\frac{1+\sqrt{1+4\lambda_k^2}}2,
$$

$$
y_{k+1}=x_{k+1}+\frac{\lambda_k-1}{\lambda_{k+1}}(x_{k+1}-x_k).
$$

The gradient must be evaluated at $y_k$, not inadvertently at $x_k$. For an $L$-smooth convex objective with a global minimiser, this parameterisation gives

$$
f(x_k)-f(x^*)\leq\frac{2L\|x_0-x^*\|^2}{(k+1)^2},
$$

an $O(1/k^2)$ rate. Acceleration is therefore a principled change to the iteration, not merely a larger learning rate.

## 6. Stochastic gradients and adaptive methods

Suppose an objective is an average over $N$ measurements or loading cases:

$$
f(x)=\frac1N\sum_{i=1}^Nf_i(x).
$$

A full gradient costs work proportional to $N$. SGD uses a random sample or mini-batch to form $g_k(x_k)$ and updates

$$
x_{k+1}=x_k-\eta_kg_k(x_k).
$$

The usual assumptions are conditional unbiasedness and bounded conditional variance:

$$
\mathbb E[g_k(x_k)\mid x_k]=\nabla f(x_k),
$$

$$
\mathbb E[\|g_k(x_k)-\nabla f(x_k)\|^2\mid x_k]\leq\sigma^2.
$$

With persistent noise, a small constant step generally reaches an error neighbourhood rather than exactly settling at the minimiser. The neighbourhood becomes smaller with suitable step-size and noise control. For diminishing-step convergence, the Robbins--Monro conditions are

$$
\sum_{k=1}^{\infty}\eta_k=\infty,\qquad
\sum_{k=1}^{\infty}\eta_k^2<\infty.
$$

The first condition ensures that learning does not stop too soon; the second controls accumulated noise. They are not sufficient alone: a theorem must also specify objective regularity, bias and moment assumptions, and stability of the iterates.

Adaptive methods rescale coordinates according to past gradients. With element-wise operations and $\epsilon>0$, AdaGrad accumulates all squared gradients:

$$
v_k=v_{k-1}+g_k\odot g_k,
$$

$$
x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k.
$$

Coordinates that have repeatedly received large gradients acquire smaller effective steps. RMSProp replaces the ever-growing sum with an exponential moving average:

$$
v_k=\gamma v_{k-1}+(1-\gamma)g_k\odot g_k,
$$

and uses the same rescaled update. This allows the scale to adapt to more recent information.

Adam combines a first-moment estimate and a second-moment estimate:

$$
m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,
$$

$$
v_k=\beta_2v_{k-1}+(1-\beta_2)(g_k\odot g_k).
$$

Because both start at zero, correct their initial bias, for gradients indexed from zero:

$$
\hat m_k=\frac{m_k}{1-\beta_1^{k+1}},\qquad
\hat v_k=\frac{v_k}{1-\beta_2^{k+1}}.
$$

Then use

$$
x_{k+1}=x_k-\frac{\eta}{\sqrt{\hat v_k}+\epsilon}\odot\hat m_k.
$$

The denominator is element-wise. A coding error that uses matrix multiplication, omits bias correction, or shifts the index can change the algorithm. Adaptive methods can be convenient for differently scaled engineering parameters, but their practical success should not be confused with the assumptions of deterministic convergence theorems.

## 7. Newton and BFGS methods

Gradient descent uses a tangent model. Newton's method includes curvature through the second-order Taylor model

$$
f(x_k+p)\approx f(x_k)+\nabla f(x_k)^Tp+\frac12p^T\nabla^2f(x_k)p.
$$

Minimising this model gives the linear system

$$
\nabla^2f(x_k)p_k=-\nabla f(x_k),
$$

followed by $x_{k+1}=x_k+p_k$. Implementations should solve this system, rather than explicitly computing a matrix inverse. Near a solution, if the Hessian at $x^*$ is positive definite and the Hessian is Lipschitz continuous, Newton's method has local quadratic convergence:

$$
\|x_{k+1}-x^*\|\leq C\|x_k-x^*\|^2.
$$

This is extremely fast near the solution, but each step needs Hessian information and a linear solve, and an undamped Newton step can be unsuitable far from the solution.

BFGS is a quasi-Newton method. It builds an inverse-Hessian approximation $H_k$ from displacement and gradient-change vectors

$$
s_k=x_{k+1}-x_k,\qquad y_k=\nabla f(x_{k+1})-\nabla f(x_k).
$$

The corresponding Hessian approximation satisfies the secant equation $B_{k+1}s_k=y_k$. When $y_k^Ts_k>0$, the inverse update is

$$
H_{k+1}=(I-\rho_ks_ky_k^T)H_k(I-\rho_ky_ks_k^T)+\rho_ks_ks_k^T,
\qquad \rho_k=\frac1{y_k^Ts_k}.
$$

The direction is $p_k=-H_k\nabla f(x_k)$, and a line search obtains $x_{k+1}=x_k+\alpha_kp_k$. The curvature condition and line search help preserve a useful positive-definite approximation. BFGS often offers a practical middle ground: more curvature awareness than gradient descent without storing exact Hessians.

## 8. From equations to Python

An update equation is also an implementation checklist. Store parameters as a NumPy array, compute a gradient array of the same shape, and create a new iterate rather than accidentally changing a value needed later. For deterministic gradient descent, one loop evaluates the gradient and performs `x = x - alpha * grad`. For SGD, the gradient function should receive a randomly selected batch, while the objective and sampling procedure must match the stated stochastic assumptions.

For line search, retain the current objective value and gradient, form trial points, and reduce the trial step until Armijo's inequality is true. For momentum, retain the previous iterate. For Nesterov, retain both $x_k$ and $y_k$ and update the acceleration parameter in the specified order. For Adam, retain $m$ and $v$, increment the iteration counter consistently, and use element-wise square roots and products. For Newton, use a linear-system solver. For BFGS, check $y_k^Ts_k$ before applying the formula. In every method, monitor objective values, gradient norms, and finite numerical values; a plot of these quantities can reveal divergence even when the code runs without a syntax error.

## 9. Final worked exercises

### Exercise 1 — Conceptual scope of a convergence theorem

A colleague claims: “Because gradient descent with $\alpha=1/L$ has an $O(1/k)$ guarantee, it will converge at that rate for any differentiable mechanical-engineering objective.” State the missing assumptions and explain what changes under strong convexity, stochastic gradients, and nonconvexity.

#### Worked solution

The claim is too broad. The stated $O(1/k)$ objective bound assumes an $L$-smooth convex function with a global minimiser and the specified constant step. Smoothness controls gradient variation, while convexity converts a stationary point into a global minimiser and supports the distance-telescoping proof. Without these assumptions, the theorem cannot be invoked merely because the function is differentiable.

If the objective is also $\mu$-strongly convex, it has a unique minimiser and gradient descent has geometric objective or distance bounds, with factors depending on $\mu/L$. If gradients are stochastic, unbiasedness, variance or moment bounds, objective assumptions, and step-size conditions must be stated. A constant step with persistent noise generally leaves an error floor; diminishing steps can satisfy the Robbins--Monro conditions. For a nonconvex objective, a global-minimum $O(1/k)$ claim is unavailable without additional structure; one instead needs a theorem about a stationary-point measure and suitable assumptions. Therefore theorem scope is part of the result, not an optional footnote.

### Exercise 2 — One hand-calculated update

Consider the mechanical calibration objective

$$
f(x_1,x_2)=\frac12\left[(x_1-2)^2+4(x_2+1)^2\right].
$$

Find its gradient, evaluate it at $x_0=(0,0)^T$, and perform one gradient-descent update with $\alpha=0.1$. Also identify the Hessian and its curvature bounds.

#### Worked solution

Differentiate each squared residual:

$$
\nabla f(x)=\begin{bmatrix}x_1-2\\4(x_2+1)\end{bmatrix}.
$$

At $x_0=(0,0)^T$,

$$
\nabla f(x_0)=\begin{bmatrix}-2\\4\end{bmatrix}.
$$

The update is

$$
x_1=x_0-0.1\nabla f(x_0)
=\begin{bmatrix}0\\0\end{bmatrix}
-0.1\begin{bmatrix}-2\\4\end{bmatrix}
=\begin{bmatrix}0.2\\-0.4\end{bmatrix}.
$$

The Hessian is constant:

$$
\nabla^2f(x)=\begin{bmatrix}1&0\\0&4\end{bmatrix}.
$$

Its eigenvalues are $1$ and $4$, so the quadratic is $L$-smooth with $L=4$ and $\mu$-strongly convex with $\mu=1$. The chosen step $0.1$ is below $1/L=0.25$, so it is conservative under the standard smooth-convex rule. The unequal eigenvalues also show why the level sets are elongated and why scaling can affect iteration speed.

### Exercise 3 — Diagnose and correct Python

The following code is intended to perform five Adam updates on the quadratic objective $f(x)=\tfrac12\|x\|^2$, whose gradient is `x`. Identify the bugs and provide corrected code.

```python
import numpy as np

x = np.array([2.0, -1.0])
m = np.zeros_like(x)
v = np.zeros_like(x)
beta1, beta2 = 0.9, 0.999
eta, eps = 0.1, 1e-8

for k in range(5):
    g = x
    m = beta1 * m + (1 - beta1) * g
    v = beta2 * v + (1 - beta2) * g * g
    m_hat = m / (1 - beta1 ** k)
    v_hat = v / (1 - beta2 ** k)
    x = x - eta * m_hat / np.sqrt(v_hat) + eps

print(x)
```

#### Worked solution

There are three main errors. First, with zero-based loop indexing the bias-correction powers must be `k + 1`, because the first stored moment contains only $(1-\beta)$ times the first gradient. Using power zero divides by zero on the first pass. Second, `eps` has been added after the division; it belongs inside the denominator, `sqrt(v_hat) + eps`, to prevent division by zero. Third, the correction should be applied element-wise to the complete fraction, so parentheses make the intended update unambiguous.

A corrected version is:

```python
import numpy as np

x = np.array([2.0, -1.0], dtype=float)
m = np.zeros_like(x)
v = np.zeros_like(x)
beta1, beta2 = 0.9, 0.999
eta, eps = 0.1, 1e-8

for k in range(5):
    g = x.copy()
    m = beta1 * m + (1.0 - beta1) * g
    v = beta2 * v + (1.0 - beta2) * (g * g)
    m_hat = m / (1.0 - beta1 ** (k + 1))
    v_hat = v / (1.0 - beta2 ** (k + 1))
    x = x - eta * m_hat / (np.sqrt(v_hat) + eps)

print(x)
```

Here `g` is an element-wise gradient, `m` and `v` preserve state between iterations, and the first and second moments are bias-corrected consistently with zero-based indexing. The code now implements the mathematical Adam update and moves the parameters toward the minimiser at the origin.
