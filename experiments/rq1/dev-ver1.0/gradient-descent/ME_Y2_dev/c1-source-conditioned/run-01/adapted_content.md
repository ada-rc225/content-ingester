# Gradient Descent and Optimisation for Mechanical Engineering

## 1. From equilibrium to an optimisation problem

A useful mechanical starting point is a system that settles into equilibrium. A mass attached to a spring moves until its potential energy can no longer be reduced by a small displacement. Numerical relaxation imitates this process: begin with an admissible configuration, compute the direction in which the energy decreases most rapidly, take a step in that direction, and repeat.

This is an intuition, not a definition. The mathematical problem studied here is the **unconstrained optimisation** problem

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where $x$ is a vector of design or state variables and $f:\mathbb{R}^d\to\mathbb{R}$ is at least continuously differentiable. In a mechanical model, $f$ might represent potential energy, but it could instead be a least-squares error, compliance surrogate, or another objective. “Unconstrained” means that, in this model, every vector in $\mathbb{R}^d$ is allowed; bounds, contact conditions, and other restrictions require additional methods and are not included in the basic algorithm below.

At a differentiable local minimiser $x^*$, every small displacement has zero first-order effect. Therefore the first-order necessary condition is

$$
\nabla f(x^*)=0.
$$

A point satisfying this equation is called stationary. Stationarity alone does not guarantee a minimum: it can also describe a maximum or a saddle point. If $f\in C^2$, a local minimiser must satisfy

$$
\nabla f(x^*)=0,\qquad \nabla^2 f(x^*)\succeq 0,
$$

where the Hessian is positive semidefinite. Conversely, if

$$
\nabla f(x^*)=0,\qquad \nabla^2f(x^*)\succ0,
$$

then $x^*$ is a strict local minimiser. In mechanical language, a positive-definite Hessian is analogous to positive stiffness for all small perturbations. The correspondence should not be overextended: the Hessian is a mathematical curvature matrix of the objective, and may not be the physical stiffness matrix of the original structure.

## 2. Smoothness, convexity, and curvature

Convergence statements require assumptions describing how rapidly the gradient can change and how the objective curves.

A continuously differentiable function is **$L$-smooth**, or has an $L$-Lipschitz continuous gradient, when $L>0$ and

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|,
\qquad \forall x,y\in\mathbb{R}^d.
$$

Thus, $L$ limits the rate at which the slope changes. For an energy landscape, it prevents arbitrarily sharp curvature. Smoothness gives the descent lemma, also called a quadratic upper bound:

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle
+\frac{L}{2}\|y-x\|^2.
$$

The right-hand side is a quadratic model that lies above the function. It follows by writing the change in $f$ as an integral along the line from $x$ to $y$ and applying Cauchy–Schwarz together with Lipschitz continuity of the gradient.

A differentiable function is **convex** if

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle,
\qquad \forall x,y\in\mathbb{R}^d.
$$

The tangent plane is therefore a global lower bound. If a convex function has a stationary point, that point is a global minimiser. This is stronger than the local equilibrium intuition: for a general non-convex function, a force-free state may not be globally best, whereas convexity rules out misleading local wells and saddles as global candidates.

A differentiable function is **$\mu$-strongly convex**, with $\mu>0$, if

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle
+\frac{\mu}{2}\|y-x\|^2,
\qquad \forall x,y\in\mathbb{R}^d.
$$

Strong convexity supplies a uniform positive curvature. In a mechanical analogy, it resembles an energy well with a strictly positive restoring stiffness in every direction, but it is a property of $f$ over the stated domain, not merely a local observation.

When $f\in C^2$, the assumptions can be read from the Hessian. $L$-smoothness is equivalent to

$$
\|\nabla^2f(x)\|_2\leq L,
$$

for every $x$. If the function is also convex, this becomes

$$
0\preceq\nabla^2f(x)\preceq LI.
$$

Strong convexity is equivalent to

$$
\nabla^2f(x)\succeq\mu I.
$$

If both properties hold, the condition number is

$$
\kappa=\frac{L}{\mu}\geq1.
$$

A large $\kappa$ describes an ill-conditioned landscape: it is steep in some directions and shallow in others. A numerical relaxation can then move rapidly across the steep direction while making slow progress along the shallow one.

## 3. Gradient descent

Given $x_0$ and positive step sizes $\alpha_k$, gradient descent is

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),
\qquad k=0,1,2,\ldots.
$$

The negative gradient is the direction of greatest instantaneous decrease in the Euclidean norm. The update is not a physical time integrator unless the problem has been formulated so that such an interpretation is valid; it is an optimisation iteration.

### Choosing the step size

If $L$ is known, a common constant choice is $\alpha=1/L$. Under the usual smooth convex assumptions, constant steps in $(0,2/L)$ are also standard. A step that is too large can overshoot the minimum and become unstable, just as an overly aggressive relaxation can oscillate around equilibrium. The precise stability conclusion depends on the assumptions on $f$ and the chosen method.

Three useful rules are:

1. **Constant step:** $\alpha_k=\alpha$, often $1/L$ when a reliable smoothness bound is available.
2. **Exact line search:** choose the best distance along the current descent direction,
   $$
   \alpha_k=\arg\min_{\alpha>0}f\bigl(x_k-\alpha\nabla f(x_k)\bigr).
   $$
3. **Backtracking line search:** choose an initial $\bar\alpha>0$, contraction factor $\eta\in(0,1)$, and $c\in(0,1)$. Reduce $\bar\alpha$ until the first $\alpha_k=\eta^m\bar\alpha$ satisfying the Armijo condition
   $$
   f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)
   \leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2
   $$
   is found.

The Armijo test checks actual decrease rather than trusting an estimated curvature value.

### Convex smooth convergence

Let $f$ be $L$-smooth and convex, let $x^*$ be a global minimiser, and use $\alpha_k=1/L$. Then, for $k\geq1$,

$$
f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k}.
$$

The rate is $O(1/k)$ in objective error. The main proof mechanism is worth understanding. The descent lemma gives

$$
f(x_{k+1})\leq f(x_k)-\frac{1}{2L}\|\nabla f(x_k)\|^2.
$$

Convexity gives

$$
f(x_k)-f(x^*)\leq\langle\nabla f(x_k),x_k-x^*\rangle.
$$

Using $x_{k+1}=x_k-\nabla f(x_k)/L$, these combine to give

$$
f(x_{k+1})-f(x^*)
\leq\frac{L}{2}\left(\|x_k-x^*\|^2-\|x_{k+1}-x^*\|^2\right).
$$

Summing from $i=0$ to $k-1$ telescopes the distance terms. Since the objective values are non-increasing, the final objective error is no larger than the average of the preceding errors, producing the stated bound. Notice the scope: this is a global-minimiser and convexity result, not a claim about every differentiable objective.

If $f$ is $L$-smooth and $\mu$-strongly convex, gradient descent with

$$
\alpha=\frac{2}{L+\mu}
$$

satisfies

$$
\|x_k-x^*\|^2\leq
\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}
\|x_0-x^*\|^2.
$$

With $\alpha=1/L$, the objective error satisfies

$$
f(x_k)-f(x^*)\leq
\left(1-\frac{\mu}{L}\right)^k
\bigl(f(x_0)-f(x^*)\bigr).
$$

This is linear (geometric) convergence. The condition number controls how quickly it occurs.

### A small executable example

The following code applies gradient descent to a quadratic energy. The quadratic is a convenient test problem because its gradient is explicit and its minimiser is known. It illustrates numerical relaxation, while the code itself implements the mathematical update rather than a physical dynamics model.

```python
import numpy as np

A = np.diag([1.0, 10.0])
b = np.array([-1.0, 2.0])

def energy(x):
    return 0.5 * x @ A @ x + b @ x

def gradient(x):
    return A @ x + b

# For this quadratic, L is the largest eigenvalue of A.
L = np.linalg.eigvalsh(A).max()
x = np.array([4.0, -3.0])
for k in range(1000):
    x = x - (1.0 / L) * gradient(x)
    if np.linalg.norm(gradient(x)) < 1e-8:
        break

x_star = -np.linalg.solve(A, b)
print("iterations:", k + 1)
print("computed minimiser:", x)
print("exact minimiser:", x_star)
print("energy:", energy(x))
```

## 4. Momentum and acceleration

Plain gradient descent can zig-zag in an ill-conditioned valley. Momentum retains part of the previous displacement, much as a moving object has inertia, but the analogy is limited: momentum here is an algorithmic recurrence and its parameters must be selected for stability.

Polyak’s heavy-ball method is

$$
x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1}),
$$

with $\beta\in[0,1)$. For the strongly convex quadratic

$$
f(x)=\frac12x^TAx,
$$

where $A$ is symmetric positive definite and its spectrum lies in $[\mu,L]$, the stated parameter choices are

$$
\alpha^*=\frac{4}{(\sqrt L+\sqrt\mu)^2},\qquad
\beta^*=\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^2.
$$

They improve the dependence of the contraction factor on the condition number from $1-O(1/\kappa)$ to $1-O(1/\sqrt\kappa)$. These claims are specific to the stated quadratic setting; they should not automatically be transferred to arbitrary nonlinear objectives.

Nesterov’s accelerated gradient method for the smooth-convex case starts with $y_0=x_0$ and $\lambda_0=1$. For $k\geq0$,

$$
x_{k+1}=y_k-\frac1L\nabla f(y_k),
$$

followed by

$$
\lambda_{k+1}=\frac{1+\sqrt{1+4\lambda_k^2}}2,
$$

and

$$
y_{k+1}=x_{k+1}+\frac{\lambda_k-1}{\lambda_{k+1}}(x_{k+1}-x_k).
$$

The gradient is evaluated at $y_k$, the look-ahead point. For an $L$-smooth convex function with global minimiser $x^*$, this parameterisation satisfies

$$
f(x_k)-f(x^*)\leq\frac{2L\|x_0-x^*\|^2}{(k+1)^2}
=O\left(\frac1{k^2}\right).
$$

Acceleration improves the theoretical rate, but it can be more sensitive to modelling and step-size errors than basic gradient descent.

## 5. Stochastic gradients

Suppose the objective is an empirical average,

$$
f(x)=\frac1N\sum_{i=1}^N f_i(x).
$$

A full gradient costs $O(N)$ evaluations. Stochastic gradient descent uses an estimate $g_k(x_k)$ and updates

$$
x_{k+1}=x_k-\eta_k g_k(x_k).
$$

A common model assumes conditional unbiasedness and bounded conditional variance:

$$
\mathbb E[g_k(x_k)\mid x_k]=\nabla f(x_k),
$$

$$
\mathbb E[\|g_k(x_k)-\nabla f(x_k)\|^2\mid x_k]\leq\sigma^2.
$$

For a mechanical application, the individual terms could represent sampled load cases or measurements. That interpretation is appropriate only when the objective really is an average over such cases.

With persistent nonzero variance, a sufficiently small constant step generally reaches an error neighbourhood rather than exact convergence. The neighbourhood size depends on the step and noise variance. For diminishing-step convergence, the Robbins–Monro conditions are

$$
\sum_{k=1}^{\infty}\eta_k=\infty,\qquad
\sum_{k=1}^{\infty}\eta_k^2<\infty.
$$

These conditions are not sufficient by themselves: a theorem also needs assumptions on the objective, stochastic-gradient bias and moments, and stability of the iterates.

Element-wise adaptive methods modify the scale of each coordinate. With $\epsilon>0$ preventing division by zero, AdaGrad uses $v_{-1}=0$ and

$$
v_k=v_{k-1}+g_k\odot g_k,
$$

$$
x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k.
$$

RMSProp instead uses $v_{-1}=0$ and $\gamma\in[0,1)$:

$$
v_k=\gamma v_{k-1}+(1-\gamma)g_k\odot g_k,
$$

$$
x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k.
$$

Adam tracks first and second moments. Starting with $m_{-1}=v_{-1}=0$ and $\beta_1,\beta_2\in[0,1)$,

$$
m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,
$$

$$
v_k=\beta_2v_{k-1}+(1-\beta_2)(g_k\odot g_k).
$$

For indexing from $k=0$, bias correction gives

$$
\hat m_k=\frac{m_k}{1-\beta_1^{k+1}},\qquad
\hat v_k=\frac{v_k}{1-\beta_2^{k+1}},
$$

and

$$
x_{k+1}=x_k-\frac{\eta}{\sqrt{\hat v_k}+\epsilon}\odot\hat m_k.
$$

These formulas are algorithm definitions; their practical success does not replace checking assumptions or monitoring the objective.

## 6. Second-order optimisation

First-order methods use gradients. Newton’s method also uses curvature through the second-order Taylor model

$$
f(x_k+p)\approx f(x_k)+\nabla f(x_k)^Tp
+\frac12p^T\nabla^2f(x_k)p.
$$

The Newton step solves

$$
\nabla^2f(x_k)p_k=-\nabla f(x_k),
$$

then updates $x_{k+1}=x_k+p_k$. When the Hessian is invertible this is equivalent to

$$
x_{k+1}=x_k-[\nabla^2f(x_k)]^{-1}\nabla f(x_k).
$$

In computation, solve the linear system rather than explicitly forming the inverse. Near a well-behaved minimiser, if $\nabla f(x^*)=0$, $\nabla^2f(x^*)$ is positive definite, and the Hessian is Lipschitz continuous nearby, then sufficiently close Newton iterates satisfy

$$
\|x_{k+1}-x^*\|\leq C\|x_k-x^*\|^2
$$

for some $C>0$. This is local quadratic convergence: once close enough, correct digits can increase rapidly. It is not a global guarantee, and an indefinite Hessian or a poor starting point can make an undamped step unsuitable.

Quasi-Newton methods estimate curvature from successive steps. Define

$$
s_k=x_{k+1}-x_k,\qquad
y_k=\nabla f(x_{k+1})-\nabla f(x_k).
$$

An approximate Hessian $B_k$ is required to satisfy the secant equation

$$
B_{k+1}s_k=y_k.
$$

For $y_k^Ts_k>0$, the inverse-Hessian BFGS update is

$$
H_{k+1}=(I-\rho_ks_ky_k^T)H_k(I-\rho_ky_ks_k^T)
+\rho_ks_ks_k^T,\qquad
\rho_k=\frac1{y_k^Ts_k}.
$$

The direction is $p_k=-H_k\nabla f(x_k)$. A suitable line search obtains $x_{k+1}=x_k+\alpha_kp_k$ and helps support the curvature condition. BFGS can reduce the cost of forming exact Hessians while retaining curvature information.

## 7. Practical checks and exercises

When implementing a relaxation algorithm, record the objective, gradient norm, step size, and iterate norm. Ask whether the observed behaviour agrees with the assumptions: a non-convex energy may have several stationary points; noisy gradients may produce an error floor; and a large condition number may cause slow progress.

Exercises:

1. Prove the descent lemma using the integral form of Taylor’s theorem.
2. For $f(x)=\tfrac12x^TAx$ with symmetric positive-definite $A$, write the heavy-ball method as a linear dynamical system for $(x_{k+1},x_k)$ and determine its spectral radius.
3. Suppose $f$ is $L$-smooth, attains $f^*$, and satisfies the PL condition
   $$
   \frac12\|\nabla f(x)\|^2\geq\mu(f(x)-f^*).
   $$
   Prove that gradient descent with $\alpha=1/L$ converges linearly in objective value, even though $f$ need not be convex.
4. Show that convexity and $L$-smoothness imply co-coercivity:
   $$
   \langle\nabla f(x)-\nabla f(y),x-y\rangle
   \geq\frac1L\|\nabla f(x)-\nabla f(y)\|^2.
   $$

The central lesson is to separate the physical picture from the mathematical guarantee. Potential energy and equilibrium provide an excellent route into descent and curvature, but convergence follows only after the objective, assumptions, step-size rule, and algorithm have been stated precisely.
