# Optimisation and Gradient-Based Methods for Mechanical Engineering

## 1. Unconstrained optimisation and local conditions

An unconstrained optimisation problem has the form

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where $x$ collects design or state variables and $f$ is the objective. In a mechanical setting, $f$ might represent a cost, error, compliance measure, or potential energy. However, an optimisation objective is not necessarily a physical energy: it may be an artificial performance measure with no units of joules. Likewise, the iteration index $k$ is an algorithmic counter, not necessarily physical time. A numerical relaxation can resemble a system settling toward equilibrium, but that analogy does not make the iterates a physical time evolution.

For a differentiable objective, a local minimiser $x^*$ must satisfy the first-order necessary condition (FONC)

$$
\nabla f(x^*)=0.
$$

This says that there is no first-order change in any direction. It does not by itself identify a minimum: a stationary point can be a maximum or a saddle point. For example, the gradient of a saddle surface can vanish even though some directions decrease the objective.

If $f\in C^2$, the Hessian supplies curvature information. A local minimiser must satisfy

$$
\nabla f(x^*)=0,\qquad \nabla^2 f(x^*)\succeq 0,
$$

where positive semidefinite means $z^T\nabla^2 f(x^*)z\geq0$ for every direction $z$. This is a second-order necessary condition. A useful sufficient condition is

$$
\nabla f(x^*)=0,\qquad \nabla^2 f(x^*)\succ0.
$$

Positive definiteness makes the curvature strictly positive in every nonzero direction, so $x^*$ is a strict local minimiser. These tests are local; they do not establish that the point is the best point everywhere.

## 2. Smoothness, convexity, and conditioning

A differentiable function is $L$-smooth when its gradient is Lipschitz continuous:

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|\quad\text{for all }x,y.
$$

The constant $L$ bounds how rapidly the slope can change. The associated Descent Lemma gives a quadratic upper model:

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle+\frac{L}{2}\|y-x\|^2.
$$

Thus, once the local linear prediction and the curvature allowance are known, this inequality bounds the objective above. It is the basic tool for proving that a sufficiently short gradient step decreases $f$.

Convexity means that the graph lies above each tangent plane:

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle.
$$

For a differentiable convex function, every stationary point is a global minimiser. Strong convexity adds a positive quadratic gap:

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle+\frac{\mu}{2}\|y-x\|^2,
$$

with $\mu>0$. It implies a unique global minimiser when one exists and prevents arbitrarily flat directions.

For $C^2$ objectives, the Hessian characterisations are especially useful. $L$-smoothness is equivalent to $\|\nabla^2f(x)\|_2\leq L$ everywhere. If the function is also convex, this becomes

$$
0\preceq\nabla^2f(x)\preceq LI.
$$

Strong convexity is equivalent to

$$
\nabla^2f(x)\succeq\mu I.
$$

When both properties hold, the condition number is

$$
\kappa=\frac{L}{\mu}\geq1.
$$

A large $\kappa$ indicates strongly unequal curvature scales: numerical movement is easy in some directions and restricted in others. This is why a mechanical design objective with a narrow valley may require many first-order iterations.

## 3. Gradient descent and step-size selection

Gradient descent starts at $x_0$ and repeatedly moves opposite the gradient:

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),\qquad k=0,1,2,\ldots.
$$

The gradient points toward local increase, so its negative is a first-order decrease direction whenever the gradient is nonzero. The step length controls how far the numerical relaxation moves.

With a constant step, $\alpha_k=\alpha$. If $L$ is known, $\alpha=1/L$ is a standard choice. Under the usual smooth convex assumptions, any constant $\alpha\in(0,2/L)$ is a common admissible range for descent behaviour. A step that is too large can overshoot, while a very small one is safe but slow.

Exact line search chooses the best distance along the current negative-gradient ray:

$$
\alpha_k=\arg\min_{\alpha>0}f\bigl(x_k-\alpha\nabla f(x_k)\bigr).
$$

It can be expensive because it requires solving a one-dimensional minimisation problem. Armijo backtracking is cheaper and adaptive. Choose a trial $\bar\alpha>0$, contraction factor $\eta\in(0,1)$, and $c\in(0,1)$. Test $\alpha_k=\eta^m\bar\alpha$ for increasing $m$ until

$$
f(x_k-\alpha_k\nabla f(x_k))\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
$$

The right-hand side demands a sufficient decrease relative to the linear prediction. The trial is repeatedly shortened until the test succeeds.

## 4. Convergence of gradient descent

For an $L$-smooth convex function with a global minimiser $x^*$, use $\alpha_k=1/L$. The Descent Lemma gives

$$
f(x_{k+1})\leq f(x_k)-\frac{1}{2L}\|\nabla f(x_k)\|^2.
$$

Combining this with convexity and the update yields a telescoping distance inequality. Consequently, for $k\geq1$,

$$
f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k}.
$$

This is an $O(1/k)$ objective-gap bound. Its assumptions matter: smoothness controls the quadratic upper model, convexity relates gradient information to the global optimum, and existence of $x^*$ supplies the reference value. The rate does not claim that each coordinate or each physical quantity has a particular time response.

If $f$ is both $L$-smooth and $\mu$-strongly convex, gradient descent has a stronger guarantee. With

$$
\alpha=\frac{2}{L+\mu},
$$

its distance satisfies

$$
\|x_k-x^*\|^2\leq\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}\|x_0-x^*\|^2.
$$

Alternatively, with $\alpha=1/L$, the objective gap obeys

$$
f(x_k)-f(x^*)\leq\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).
$$

This is linear (geometric) convergence. The condition number explains the speed: as $\kappa$ grows, the factor approaches one and more iterations are needed.

## 5. Momentum and acceleration

Polyak's Heavy Ball method adds the previous displacement:

$$
x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1}),
$$

with $\beta\in[0,1)$. The extra term carries numerical momentum and can reduce zig-zagging in elongated valleys. Stability depends on the parameters; momentum is not automatically safe for every objective.

For the specific strongly convex quadratic $f(x)=\tfrac12x^TAx$, with $A$ symmetric positive definite and spectrum in $[\mu,L]$, the parameter result is

$$
\alpha^*=\frac{4}{(\sqrt L+\sqrt\mu)^2},\qquad
\beta^*=\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^2.
$$

In this stated quadratic setting, the contraction dependence improves from $1-O(1/\kappa)$ to $1-O(1/\sqrt\kappa)$. The qualification is important: these parameter claims are not a general guarantee for arbitrary nonquadratic objectives.

Nesterov's accelerated-gradient recurrence uses a look-ahead point. Set $y_0=x_0$ and $\lambda_0=1$. For each $k$, compute

$$
x_{k+1}=y_k-\frac1L\nabla f(y_k),
$$

then

$$
\lambda_{k+1}=\frac{1+\sqrt{1+4\lambda_k^2}}2,
$$

and

$$
y_{k+1}=x_{k+1}+\frac{\lambda_k-1}{\lambda_{k+1}}(x_{k+1}-x_k).
$$

The gradient is evaluated at $y_k$, not at $x_k$. For an $L$-smooth convex function with a global minimiser,

$$
f(x_k)-f(x^*)\leq\frac{2L\|x_0-x^*\|^2}{(k+1)^2}=O(1/k^2).
$$

## 6. Stochastic objectives and adaptive updates

For data or repeated simulations, consider the finite-sum objective

$$
f(x)=\frac1N\sum_{i=1}^Nf_i(x).
$$

A full gradient costs $O(N)$ component contributions. Stochastic gradient descent uses $g_k(x_k)$ and updates

$$
x_{k+1}=x_k-\eta_kg_k(x_k).
$$

The standard assumptions are conditional unbiasedness and bounded conditional variance:

$$
\mathbb E[g_k(x_k)\mid x_k]=\nabla f(x_k),
$$

$$
\mathbb E[\|g_k(x_k)-\nabla f(x_k)\|^2\mid x_k]\leq\sigma^2.
$$

With persistent nonzero variance, a small constant step generally reaches a nonzero error floor rather than exact convergence. Diminishing steps are governed by the Robbins--Monro conditions

$$
\sum_{k=1}^{\infty}\eta_k=\infty,\qquad
\sum_{k=1}^{\infty}\eta_k^2<\infty.
$$

These conditions alone are not a theorem: suitable objective, bias, moment, and iterate-stability assumptions are also required.

Adaptive methods rescale coordinates element by element. Here $\odot$ denotes element-wise multiplication, square roots and divisions are element-wise, and $\epsilon>0$ prevents division by zero.

AdaGrad starts with $v_{-1}=0$:

$$
v_k=v_{k-1}+g_k\odot g_k,\qquad
x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k.
$$

RMSProp also starts with $v_{-1}=0$, but uses an exponential average with $\gamma\in[0,1)$:

$$
v_k=\gamma v_{k-1}+(1-\gamma)g_k\odot g_k,
$$

followed by the same rescaled update. Adam starts with $m_{-1}=v_{-1}=0$ and uses $\beta_1,\beta_2\in[0,1)$:

$$
m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,
$$

$$
v_k=\beta_2v_{k-1}+(1-\beta_2)(g_k\odot g_k).
$$

Because zero initialisation makes early averages biased toward zero, Adam applies, for zero-based iteration $k$,

$$
\hat m_k=\frac{m_k}{1-\beta_1^{k+1}},\qquad
\hat v_k=\frac{v_k}{1-\beta_2^{k+1}}.
$$

Its parameter update is

$$
x_{k+1}=x_k-\frac{\eta}{\sqrt{\hat v_k}+\epsilon}\odot\hat m_k.
$$

## 7. Newton and BFGS methods

Newton's method retains curvature through the second-order model

$$
f(x_k+p)\approx f(x_k)+\nabla f(x_k)^Tp+\frac12p^T\nabla^2f(x_k)p.
$$

Minimising this quadratic model gives the linear system

$$
\nabla^2f(x_k)p_k=-\nabla f(x_k),
$$

then $x_{k+1}=x_k+p_k$. Although this is equivalent to multiplying by an inverse Hessian, implementations should solve the linear system rather than explicitly form the inverse. If $\nabla f(x^*)=0$, the Hessian at $x^*$ is positive definite, the Hessian is Lipschitz continuous nearby, and the initial point is sufficiently close, then locally

$$
\|x_{k+1}-x^*\|\leq C\|x_k-x^*\|^2.
$$

This quadratic convergence is local, not a promise from an arbitrary starting point.

BFGS avoids computing the Hessian directly. Define the step and gradient-difference vectors

$$
s_k=x_{k+1}-x_k,\qquad y_k=\nabla f(x_{k+1})-\nabla f(x_k).
$$

A Hessian approximation $B_{k+1}$ is required to satisfy the secant equation $B_{k+1}s_k=y_k$. Using an inverse-Hessian approximation $H_k$, the BFGS update is

$$
H_{k+1}=(I-\rho_ks_ky_k^T)H_k(I-\rho_ky_ks_k^T)+\rho_ks_ks_k^T,
\qquad \rho_k=\frac1{y_k^Ts_k}.
$$

The curvature condition $y_k^Ts_k>0$ is essential. The search direction is $p_k=-H_k\nabla f(x_k)$, and a line search selects $\alpha_k$ so that $x_{k+1}=x_k+\alpha_kp_k$ while supporting the curvature condition. BFGS therefore combines gradient differences with controlled steps rather than explicitly assembling second derivatives.

## 8. Exercises and worked solutions

### Exercise 1 — Conceptual theorem-scope check

A colleague makes four claims: (a) $\nabla f(x)=0$ proves that $x$ is a strict local minimum; (b) the $O(1/k)$ convex gradient-descent bound applies to every differentiable objective; (c) the Heavy Ball parameters above are guaranteed for every smooth function; (d) Robbins--Monro step conditions alone guarantee stochastic convergence. Identify which claims are false and state the missing condition or qualification for each.

#### Solution

All four claims are false as stated. A zero gradient is only a first-order necessary condition and may describe a maximum or saddle. For a strict local minimum, the source gives the sufficient conditions $f\in C^2$, zero gradient, and positive-definite Hessian. The $O(1/k)$ bound requires an $L$-smooth convex function, a global minimiser, and step $1/L$. Heavy Ball's displayed parameter result is specific to a strongly convex quadratic with symmetric positive-definite matrix spectrum in $[\mu,L]$; stability is not automatic in general. Finally, Robbins--Monro requires additional assumptions on the objective, stochastic-gradient bias and moments, and iterate stability.

### Exercise 2 — Hand calculation

Let $f(x)=\tfrac12x^TAx$ with $A=\operatorname{diag}(1,4)$ and $x_0=(2,1)^T$. Use gradient descent with the constant step $\alpha=1/L$, where $L$ is the largest Hessian eigenvalue. Compute $x_1$, $f(x_0)$, and $f(x_1)$. Then state the strong-convexity parameters and the objective-gap factor from the source theorem.

#### Solution

Here $\nabla f(x)=Ax$, the Hessian is $A$, $L=4$, and $\mu=1$. Therefore $\alpha=1/4$. Since $\nabla f(x_0)=(2,4)^T$,

$$
x_1=x_0-\tfrac14(2,4)^T=(2,1)^T-(0.5,1)^T=(1.5,0)^T.
$$

The minimiser is $x^*=(0,0)^T$. The initial objective is $f(x_0)=\tfrac12(4+4)=4$, while $f(x_1)=\tfrac12(2.25)=1.125$. The condition number is $\kappa=L/\mu=4$. The theorem with $\alpha=1/L$ gives the objective-gap factor $1-\mu/L=3/4$ per iteration, as an upper-bound factor under the stated assumptions. The actual first-step ratio here is $1.125/4=0.28125$, which can be smaller than the guaranteed factor.

### Exercise 3 — Python code diagnostic

The following program is executable, but its Adam implementation is mathematically incorrect. Identify the algorithmic error.

```python
import numpy as np

x = np.array([4.0, -2.0])
m = np.zeros_like(x)
v = np.zeros_like(x)
for k in range(100):
    g = x
    m = 0.9 * m + 0.1 * g
    v = 0.999 * v + 0.001 * (g * g)
    # Incorrect: uses uncorrected moments and adds epsilon to the numerator.
    x = x - 0.1 * (m + 1e-8) / np.sqrt(v)
print(x)
```

#### Solution

The program uses zero-initialised moving averages but omits Adam's bias correction. It also places $\epsilon$ in the numerator and does not protect the denominator. The corrected executable program is:

```python
import numpy as np

x = np.array([4.0, -2.0])
m = np.zeros_like(x)
v = np.zeros_like(x)
beta1, beta2 = 0.9, 0.999
eta, epsilon = 0.1, 1e-8
for k in range(100):
    g = x
    m = beta1 * m + (1 - beta1) * g
    v = beta2 * v + (1 - beta2) * (g * g)
    m_hat = m / (1 - beta1 ** (k + 1))
    v_hat = v / (1 - beta2 ** (k + 1))
    x = x - eta * m_hat / (np.sqrt(v_hat) + epsilon)
print(x)
```

The code mirrors the mathematics: `g * g` is element-wise squaring, the moving averages start at zero, the powers use the one-based iteration count $k+1$, and $\epsilon$ is added to the denominator. For this objective, $g=x$ and the minimiser is zero. The corrected iterates should move both coordinates toward zero, with coordinate-wise scaling determined by the estimated first and second moments. The result is numerical convergence toward the minimiser up to floating-point and stopping effects; it should not be interpreted as a physical time history.
