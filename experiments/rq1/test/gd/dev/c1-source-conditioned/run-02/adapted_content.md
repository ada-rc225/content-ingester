# Gradient Descent and Optimisation for Mechanical Engineering

## 1. Unconstrained optimisation and local tests

Many engineering calculations can be written as the unconstrained problem

$$\min_{x\in\mathbb{R}^d} f(x).$$

Here $x$ may collect design variables, displacements, or model parameters, and $f$ is an objective. A useful mechanical analogy is potential energy: an equilibrium configuration can be a stationary point of an energy function. This is only an analogy. An optimisation objective is not necessarily a physical energy; it may be a fitting error or computational cost. Similarly, the sequence of algorithmic iterates is not necessarily a physical time evolution. It is a numerical relaxation procedure whose index $k$ counts updates.

Assume first that $f$ is differentiable. If $x^*$ is a local minimiser and there are no constraints, then the first-order necessary condition (FONC) is

$$\nabla f(x^*)=0.$$

The condition is necessary, not sufficient: a stationary point can be a maximum or a saddle point. If $f\in C^2$, a local minimiser also satisfies the second-order necessary condition

$$\nabla^2f(x^*)\succeq 0,$$

meaning that $z^T\nabla^2f(x^*)z\geq0$ for every direction $z$. If instead

$$\nabla f(x^*)=0,\qquad \nabla^2f(x^*)\succ0,$$

then $x^*$ is a strict local minimiser. Positive definiteness means $z^T\nabla^2f(x^*)z>0$ for every nonzero $z$. In mechanics, this resembles an equilibrium with positive local stiffness in every direction, but the same mathematics applies when $f$ has no physical interpretation.

## 2. Smoothness, curvature, and convexity

### L-smoothness and the Descent Lemma

A differentiable function is $L$-smooth when its gradient is Lipschitz continuous:

$$\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|\quad\text{for all }x,y.$$

The constant $L$ limits how rapidly the slope can change. The Descent Lemma gives the corresponding quadratic upper model:

$$f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle+\frac{L}{2}\|y-x\|^2.$$

The linear term predicts the change using the current gradient, while the final term allows for curvature. Substituting $y=x-\alpha\nabla f(x)$ gives

$$f(x-\alpha\nabla f(x))\leq f(x)-\alpha\left(1-\frac{L\alpha}{2}\right)\|\nabla f(x)\|^2.$$

Thus a step with $0<\alpha<2/L$ decreases the objective unless the gradient is zero. This is a sufficient smoothness argument, not a statement that every objective has the same behaviour without assumptions.

### Convexity and strong convexity

A differentiable function is convex if

$$f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle.$$

Every tangent plane is therefore a global lower bound. A stationary point of a differentiable convex function is a global minimiser. Strong convexity adds a quadratic lower bound: $f$ is $\mu$-strongly convex when

$$f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle+\frac{\mu}{2}\|y-x\|^2,$$

with $\mu>0$. It ensures a unique minimiser when one exists and quantifies a minimum amount of curvature.

For a twice continuously differentiable function, the Hessian characterisations are especially useful. $L$-smoothness is equivalent to $\|\nabla^2f(x)\|_2\leq L$ everywhere. If the function is also convex, this becomes

$$0\preceq\nabla^2f(x)\preceq LI.$$

Strong convexity is equivalent to

$$\nabla^2f(x)\succeq\mu I.$$

If both properties hold, the condition number is

$$\kappa=\frac{L}{\mu}\geq1.$$

A large $\kappa$ indicates strongly different curvature scales: numerical relaxation can move quickly along stiff directions but slowly along shallow ones. This is why elongated quadratic energy landscapes are difficult for basic gradient descent.

## 3. Gradient descent and step selection

### Update and constant steps

Starting from $x_0$, gradient descent (GD) applies

$$x_{k+1}=x_k-\alpha_k\nabla f(x_k).$$

The negative gradient is a local descent direction. With known smoothness constant $L$, a common constant choice is $\alpha=1/L$. Under the usual smooth convex assumptions, constant steps in $(0,2/L)$ are also permitted for descent behaviour. The step is an algorithmic scale, not a physical time increment.

### Exact line search and Armijo backtracking

Exact line search chooses the best positive distance along the current descent ray:

$$\alpha_k=\arg\min_{\alpha>0}f(x_k-\alpha\nabla f(x_k)).$$

It can be expensive because it requires solving a one-dimensional minimisation problem. Armijo backtracking instead starts with a trial $\bar\alpha>0$, contraction factor $\eta\in(0,1)$, and sufficient-decrease constant $c\in(0,1)$. Test $\alpha_k=\eta^m\bar\alpha$ for increasing $m$ until

$$f(x_k-\alpha_k\nabla f(x_k))\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.$$

The accepted step is the first one meeting this condition. The right side demands a decrease proportional to the predicted first-order decrease. Backtracking reduces an over-large trial step without requiring $L$ explicitly.

## 4. Convergence of gradient descent

### Smooth convex objectives

Suppose $f$ is $L$-smooth and convex, has a global minimiser $x^*$, and GD uses $\alpha_k=1/L$. Then, for $k\geq1$,

$$f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k}.$$

This is an objective-gap bound with an $O(1/k)$ rate. The Descent Lemma first gives

$$f(x_{k+1})\leq f(x_k)-\frac{1}{2L}\|\nabla f(x_k)\|^2.$$

Convexity gives $f(x_k)-f(x^*)\leq\langle\nabla f(x_k),x_k-x^*\rangle$. Combining this with the identity $x_{k+1}=x_k-\nabla f(x_k)/L$ yields

$$f(x_{k+1})-f(x^*)\leq\frac{L}{2}\left(\|x_k-x^*\|^2-\|x_{k+1}-x^*\|^2\right).$$

Summing telescopes the squared distances. Since the objective gaps are non-increasing, the last gap is no larger than their average, producing the stated bound. Convexity is essential for interpreting a stationary solution as globally optimal; smoothness and the specified step support the quantitative decrease.

### Smooth strongly convex objectives

If $f$ is both $L$-smooth and $\mu$-strongly convex, GD has a unique minimiser and a linear (geometric) guarantee. With

$$\alpha=\frac{2}{L+\mu},$$

one has the distance bound

$$\|x_k-x^*\|^2\leq\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}\|x_0-x^*\|^2.$$

With the simpler step $\alpha=1/L$, the objective gap satisfies

$$f(x_k)-f(x^*)\leq\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).$$

The factor is below one because $0<\mu\leq L$. Strong curvature changes the sublinear convex guarantee into a geometric one, although a high condition number still makes the factor close to one.

## 5. Momentum and acceleration

### Heavy Ball

Polyak's Heavy Ball method adds the previous displacement:

$$x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1}),\qquad\beta\in[0,1).$$

The old motion can help cross shallow regions, but parameters must preserve stability. For the specific strongly convex quadratic $f(x)=\tfrac12x^TAx$, with symmetric positive-definite $A$ whose spectrum lies in $[\mu,L]$, the parameter result is

$$\alpha^*=\frac{4}{(\sqrt L+\sqrt\mu)^2},\qquad\beta^*=\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^2.$$

In this stated quadratic setting, the contraction dependence improves from $1-O(1/\kappa)$ to $1-O(1/\sqrt\kappa)$. This claim should not be silently extended to arbitrary nonquadratic objectives.

### Nesterov accelerated gradient

For the smooth-convex variant, set $y_0=x_0$ and $\lambda_0=1$. At iteration $k$, evaluate the gradient at the look-ahead point:

$$x_{k+1}=y_k-\frac1L\nabla f(y_k),$$

then compute

$$\lambda_{k+1}=\frac{1+\sqrt{1+4\lambda_k^2}}2,$$

and

$$y_{k+1}=x_{k+1}+\frac{\lambda_k-1}{\lambda_{k+1}}(x_{k+1}-x_k).$$

For an $L$-smooth convex function with global minimiser $x^*$,

$$f(x_k)-f(x^*)\leq\frac{2L\|x_0-x^*\|^2}{(k+1)^2}=O(1/k^2).$$

The order improves on ordinary convex GD, but it depends on the smooth-convex assumptions and on evaluating the gradient at $y_k$, not accidentally at $x_k$.

## 6. Stochastic and adaptive methods

### Finite sums, noise, and step conditions

For data, samples, or repeated simulations, consider

$$f(x)=\frac1N\sum_{i=1}^Nf_i(x).$$

A full gradient costs $O(N)$, so SGD uses a random estimate $g_k(x_k)$:

$$x_{k+1}=x_k-\eta_kg_k(x_k).$$

The standard assumptions are conditional unbiasedness,

$$\mathbb E[g_k(x_k)\mid x_k]=\nabla f(x_k),$$

and bounded conditional variance,

$$\mathbb E[\|g_k(x_k)-\nabla f(x_k)\|^2\mid x_k]\leq\sigma^2.$$

With persistent nonzero variance, a small constant step generally reaches a nonzero error floor: it approaches a neighbourhood whose size depends on the step and noise, rather than exact convergence. Diminishing steps commonly satisfy the Robbins-Monro conditions

$$\sum_{k=1}^{\infty}\eta_k=\infty,\qquad\sum_{k=1}^{\infty}\eta_k^2<\infty.$$

These conditions alone do not prove convergence; objective assumptions, bias and moment assumptions, and iterate stability are also required.

### AdaGrad, RMSProp, and Adam

For vectors, $\odot$, square roots, and divisions below are element-wise. A small $\epsilon>0$ prevents division by zero.

AdaGrad starts with $v_{-1}=0$ and accumulates squared gradients:

$$v_k=v_{k-1}+g_k\odot g_k,\qquad x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k.$$

RMSProp also starts with $v_{-1}=0$, but forgets old information using $\gamma\in[0,1)$:

$$v_k=\gamma v_{k-1}+(1-\gamma)g_k\odot g_k,$$

followed by the same element-wise update. AdaGrad's accumulated scale can keep growing, whereas RMSProp's moving average can adapt to changing scales.

Adam starts with $m_{-1}=v_{-1}=0$. For $\beta_1,\beta_2\in[0,1)$,

$$m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,$$

$$v_k=\beta_2v_{k-1}+(1-\beta_2)(g_k\odot g_k).$$

Because zero initialisation biases early averages toward zero, for zero-based iteration indexing use

$$\hat m_k=\frac{m_k}{1-\beta_1^{k+1}},\qquad\hat v_k=\frac{v_k}{1-\beta_2^{k+1}}.$$

The update is

$$x_{k+1}=x_k-\frac{\eta}{\sqrt{\hat v_k}+\epsilon}\odot\hat m_k.$$

Initialisation, indexing, element-wise operations, and epsilon are part of the algorithm, not implementation details to omit.

## 7. Newton and BFGS second-order methods

### Newton's method

Newton uses the local second-order model

$$f(x_k+p)\approx f(x_k)+\nabla f(x_k)^Tp+\frac12p^T\nabla^2f(x_k)p.$$

Minimising this model with respect to $p$ gives the linear system

$$\nabla^2f(x_k)p_k=-\nabla f(x_k),\qquad x_{k+1}=x_k+p_k.$$

Although this is formally $p_k=-[\nabla^2f(x_k)]^{-1}\nabla f(x_k)$, numerical code should solve the linear system rather than explicitly forming the inverse. If $\nabla f(x^*)=0$, the Hessian at $x^*$ is positive definite, and the Hessian is Lipschitz continuous near $x^*$, then sufficiently close initialisation gives local quadratic convergence:

$$\|x_{k+1}-x^*\|\leq C\|x_k-x^*\|^2.$$

The result is local: it does not promise safe global behaviour from every starting point.

### BFGS

BFGS avoids repeatedly forming exact Hessians. Define

$$s_k=x_{k+1}-x_k,\qquad y_k=\nabla f(x_{k+1})-\nabla f(x_k).$$

An approximation $B_{k+1}$ to the Hessian is required to satisfy the secant equation $B_{k+1}s_k=y_k$. Equivalently, maintain an inverse-Hessian approximation $H_k$. When the curvature condition $y_k^Ts_k>0$ holds, set $\rho_k=1/(y_k^Ts_k)$ and update

$$H_{k+1}=(I-\rho_ks_ky_k^T)H_k(I-\rho_ky_ks_k^T)+\rho_ks_ks_k^T.$$

The search direction is

$$p_k=-H_k\nabla f(x_k).$$

A line search chooses $x_{k+1}=x_k+\alpha_kp_k$ and, in practice, helps obtain the positive curvature needed for a useful update. The vectors $s_k$ and $y_k$ therefore connect the actual step to the observed gradient change.

## 8. Exercises and worked solutions

### Exercise 1 — theorem-scope check

A student claims: “Because $f$ is differentiable and an iteration has reached $\nabla f(x)=0$, $x$ is the unique global minimiser, and the iterates represent the physical time history of a mechanical system.” Identify every unsupported conclusion and state assumptions that would justify the relevant mathematical conclusions.

**Worked solution.** The FONC only says that a differentiable local minimiser must have zero gradient; the converse is false. A stationary point may be a maximum or saddle. If $f$ is $C^2$, positive semidefinite Hessian is necessary at a local minimiser, while a zero gradient and positive definite Hessian are sufficient for a strict local minimiser. To obtain a global conclusion, convexity is needed: a stationary point of a differentiable convex function is global. To obtain uniqueness and quantitative strong curvature, use $\mu$-strong convexity. The statement about physical time is also unsupported. The index $k$ labels numerical updates, and an optimisation objective need not be physical potential energy. Iterates can be interpreted as numerical relaxation only unless a separate physical model establishes a time interpretation.

### Exercise 2 — hand calculation

Let $f(x)=\tfrac12x^TAx$ with $A=\operatorname{diag}(1,4)$ and $x_0=(2,1)^T$. Use one GD update with $\alpha=1/L$, where $L=4$, and compute $x_1$ and $f(x_1)$. Then state the condition number if $\mu=1$.

**Worked solution.** Since $\nabla f(x)=Ax$,

$$\nabla f(x_0)=(2,4)^T.$$

The update is $x_1=x_0-\tfrac14(2,4)^T=(3/2,0)^T$. Therefore

$$f(x_1)=\frac12\left[(3/2)^2+4(0)^2\right]=\frac98=1.125.$$

The eigenvalues are $1$ and $4$, so $\mu=1$, $L=4$, and $\kappa=L/\mu=4$. The two coordinates relax at different rates because their curvatures differ.

### Exercise 3 — Python code diagnosis

The following program is executable, but its Adam implementation is mathematically incorrect. Identify the algorithmic error.

```python
import numpy as np

x = np.array([4.0, -2.0])
m = np.zeros_like(x)
v = np.zeros_like(x)
beta1, beta2 = 0.9, 0.999
eta, eps = 0.1, 1e-8

for k in range(20):
    g = x                         # gradient of 0.5 * x.T @ x
    m = beta1 * m + (1 - beta1) * g
    v = beta2 * v + (1 - beta2) * (g * g)
    x -= eta * m / (np.sqrt(v) + eps)

print(x)
```

**Worked solution.** The moving averages start at zero, so the early $m$ and $v$ values are biased toward zero. The program updates with uncorrected moments. It should use $\hat m_k=m_k/(1-\beta_1^{k+1})$ and $\hat v_k=v_k/(1-\beta_2^{k+1})$, then update using the corrected quantities. The corrected executable program is:

```python
import numpy as np

x = np.array([4.0, -2.0])
m = np.zeros_like(x)
v = np.zeros_like(x)
beta1, beta2 = 0.9, 0.999
eta, eps = 0.1, 1e-8

for k in range(20):
    g = x                         # gradient of 0.5 * x.T @ x
    m = beta1 * m + (1 - beta1) * g
    v = beta2 * v + (1 - beta2) * (g * g)
    m_hat = m / (1 - beta1 ** (k + 1))
    v_hat = v / (1 - beta2 ** (k + 1))
    x -= eta * m_hat / (np.sqrt(v_hat) + eps)

print(x)
```

For $f(x)=\tfrac12\|x\|^2$, the minimiser is the zero vector and $g=x$. Thus both programs should generally move toward zero, but the incorrect one takes distorted early steps because its moment estimates are too small. The corrected program removes that initialisation bias. The operations are element-wise: each coordinate is scaled by its own corrected second-moment estimate, with $\epsilon$ protecting the denominator.
