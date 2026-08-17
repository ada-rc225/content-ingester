# Gradient Descent and Optimisation: From Equilibrium to Numerical Relaxation

## 1. Why optimisation looks like equilibrium

In mechanical engineering, a useful starting picture is a system settling toward equilibrium. A configuration with no remaining driving force is analogous to a point where the gradient of an objective vanishes. Numerical relaxation uses repeated updates to move a trial configuration toward a more favourable one. Gradient descent makes this idea precise: it repeatedly moves opposite to the local gradient.

This is a pedagogical analogy, not a universal identity. An optimisation objective need not be a physical potential energy, and an algorithmic iteration is not necessarily physical time evolution. The analogy is useful for direction, stability, and settling, while the mathematical assumptions determine what can actually be guaranteed.

The unconstrained optimisation problem is

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where $f:\mathbb{R}^d\to\mathbb{R}$ is at least continuously differentiable, written $f\in C^1$. The vector $x$ may represent design variables, parameters, or a discretised configuration. The aim is to find a minimiser, but an algorithm may first reach only a stationary point. Its behaviour depends on the shape of $f$, the step-size rule, and the update method.

## 2. Stationary points and local optimality

### First-order information

If $x^*$ is a local minimiser and $f$ is differentiable at $x^*$, then the first-order necessary condition is

$$
\nabla f(x^*)=0.
$$

The gradient is therefore a natural measure of local driving direction. A zero gradient is necessary for a differentiable local minimum, but it is not sufficient: a stationary point can also be a maximum or a saddle point.

### Second-order information

When $f\in C^2$, the Hessian $\nabla^2f(x^*)$ describes local curvature. At a local minimiser,

$$
\nabla f(x^*)=0\quad\text{and}\quad \nabla^2f(x^*)\succeq 0
$$

are necessary. Here $\succeq0$ means positive semidefinite: the quadratic curvature is nonnegative in every direction. A sufficient condition for a strict local minimiser is

$$
\nabla f(x^*)=0\quad\text{and}\quad \nabla^2f(x^*)\succ0,
$$

where positive definiteness means strictly positive curvature in every nonzero direction. These conditions are local. They do not, by themselves, establish that the point is the global minimiser over all of $\mathbb{R}^d$.

## 3. Smoothness, convexity, and conditioning

Convergence results require assumptions that control how the objective changes.

### Smoothness and the quadratic upper bound

A continuously differentiable function is $L$-smooth, with $L>0$, if its gradient is Lipschitz continuous:

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|,
\qquad \forall x,y\in\mathbb{R}^d.
$$

The descent lemma then gives the quadratic upper bound

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle+\frac{L}{2}\|y-x\|^2.
$$

The linear term predicts the immediate change, while the quadratic term limits the error caused by curvature. For a step $y=x-\alpha\nabla f(x)$, this bound explains why an excessively large step can overshoot rather than relax.

If $f\in C^2$, $L$-smoothness is equivalent to

$$
\|\nabla^2f(x)\|_2\leq L\quad\text{for all }x.
$$

If the function is also convex, this becomes

$$
0\preceq\nabla^2f(x)\preceq LI.
$$

### Convexity and strong convexity

A differentiable function is convex if

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle,
\qquad \forall x,y.
$$

The graph lies above each tangent-plane approximation. For a convex objective, a stationary point is a global minimiser when a global minimiser exists.

A function is $\mu$-strongly convex, with $\mu>0$, if

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle+\frac{\mu}{2}\|y-x\|^2,
\qquad \forall x,y.
$$

Strong convexity adds a uniform positive-curvature term. For $C^2$ functions it is equivalent to

$$
\nabla^2f(x)\succeq\mu I\quad\text{for all }x.
$$

If $f$ is both $L$-smooth and $\mu$-strongly convex, its condition number is

$$
\kappa=\frac{L}{\mu}\geq1.
$$

A large $\kappa$ represents an ill-conditioned problem: curvature varies substantially between directions. In a relaxation picture, one direction may be steep while another is relatively flat, so a step small enough for the steep direction can make progress slowly in the flat direction.

## 4. Gradient descent and choosing a step

Given $x_0\in\mathbb{R}^d$ and positive step sizes $\alpha_k$, gradient descent is

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),
\qquad k=0,1,2,\ldots.
$$

The gradient points toward local increase, so the negative gradient is the local decrease direction. In code, the update must use the gradient evaluated at the current iterate, not at an accidentally stale or future value.

### Constant steps and line searches

A constant step uses $\alpha_k=\alpha$. When $L$ is known, $\alpha=1/L$ is a standard choice. Under the usual smooth convex assumptions, a constant step in $(0,2/L)$ is also included among common choices. The value is not a universal engineering unit conversion: it is tied to the smoothness scale of the particular objective.

Exact line search chooses the best positive step along the current negative-gradient direction:

$$
\alpha_k=\arg\min_{\alpha>0}f\bigl(x_k-\alpha\nabla f(x_k)\bigr).
$$

Backtracking line search starts from $\bar\alpha>0$, chooses $\eta\in(0,1)$ and $c\in(0,1)$, and tests $\alpha_k=\eta^m\bar\alpha$ for the smallest integer $m\geq0$ satisfying the Armijo condition

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)
\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
$$

The trial step is contracted until the observed decrease is sufficient according to this condition.

### Convex convergence

Suppose $f$ is $L$-smooth and convex, $x^*$ is a global minimiser, and $\alpha_k=1/L$. Then for $k\geq1$,

$$
f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k}.
$$

Thus the objective error is $O(1/k)$. The descent lemma first gives

$$
f(x_{k+1})\leq f(x_k)-\frac{1}{2L}\|\nabla f(x_k)\|^2.
$$

Convexity gives

$$
f(x_k)-f(x^*)\leq\langle\nabla f(x_k),x_k-x^*\rangle.
$$

Using $x_{k+1}=x_k-\nabla f(x_k)/L$ combines these into

$$
f(x_{k+1})-f(x^*)\leq\frac{L}{2}\left(\|x_k-x^*\|^2-\|x_{k+1}-x^*\|^2\right).
$$

Summing this telescoping inequality, and using that the objective values are non-increasing, produces the stated bound. The theorem requires smoothness, convexity, a global minimiser, and the specified step; it is not a claim about arbitrary nonconvex objectives.

### Strongly convex convergence

If $f$ is both $L$-smooth and $\mu$-strongly convex, gradient descent with

$$
\alpha=\frac{2}{L+\mu}
$$

satisfies

$$
\|x_k-x^*\|^2\leq\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}\|x_0-x^*\|^2.
$$

With $\alpha=1/L$, the objective error satisfies

$$
f(x_k)-f(x^*)\leq\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).
$$

This is linear, or geometric, convergence. The condition number controls the rate: large $\kappa=L/\mu$ makes the factor closer to one.

## 5. Momentum and acceleration

### Heavy-ball momentum

Polyak’s heavy-ball method retains a part of the previous displacement:

$$
x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1}),
$$

where $\beta\in[0,1)$. The extra term can carry useful progress through directions where ordinary descent is slow, but parameters must preserve stability.

For the specific strongly convex quadratic

$$
f(x)=\frac12x^TAx,
$$

where $A$ is symmetric positive definite and its spectrum lies in $[\mu,L]$, the stated choices are

$$
\alpha^*=\frac{4}{(\sqrt L+\sqrt\mu)^2},
\qquad
\beta^*=\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^2.
$$

In that quadratic setting, the contraction dependence improves from $1-O(1/\kappa)$ to $1-O(1/\sqrt\kappa)$. This parameter claim is specific to that stated quadratic setting, not a guarantee for every objective.

### Nesterov accelerated gradient

For the supplied smooth-convex variant, initialise $y_0=x_0$ and $\lambda_0=1$. For $k\geq0$,

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

The gradient is evaluated at the look-ahead point $y_k$. For an $L$-smooth convex function with a global minimiser, this parameterisation gives

$$
f(x_k)-f(x^*)\leq\frac{2L\|x_0-x^*\|^2}{(k+1)^2}=O(1/k^2).
$$

## 6. Stochastic and adaptive methods

For an empirical objective,

$$
f(x)=\frac1N\sum_{i=1}^Nf_i(x),
$$

computing the full gradient costs $O(N)$. Stochastic gradient descent uses an estimate $g_k(x_k)$:

$$
x_{k+1}=x_k-\eta_kg_k(x_k).
$$

The source model assumes conditional unbiasedness and bounded conditional variance:

$$
\mathbb E[g_k(x_k)\mid x_k]=\nabla f(x_k),
$$

$$
\mathbb E[\|g_k(x_k)-\nabla f(x_k)\|^2\mid x_k]\leq\sigma^2.
$$

Persistent nonzero variance with a sufficiently small constant step generally leaves a nonzero error floor. For diminishing-step convergence results, the Robbins–Monro conditions are

$$
\sum_{k=1}^{\infty}\eta_k=\infty,
\qquad
\sum_{k=1}^{\infty}\eta_k^2<\infty.
$$

These conditions alone are not sufficient: assumptions on the objective, bias and moments of the stochastic gradients, and iterate stability are also needed.

Adaptive methods rescale coordinates using recent gradient information. With $\epsilon>0$ preventing division by zero, AdaGrad starts with $v_{-1}=0$ and uses

$$
v_k=v_{k-1}+g_k\odot g_k,
\qquad
x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k.
$$

RMSProp instead uses $v_{-1}=0$, $\gamma\in[0,1)$, and

$$
v_k=\gamma v_{k-1}+(1-\gamma)g_k\odot g_k,
$$

followed by the same rescaled update. Adam starts with $m_{-1}=v_{-1}=0$:

$$
m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,
$$

$$
v_k=\beta_2v_{k-1}+(1-\beta_2)(g_k\odot g_k).
$$

For zero-based indexing, bias correction is essential:

$$
\hat m_k=\frac{m_k}{1-\beta_1^{k+1}},
\qquad
\hat v_k=\frac{v_k}{1-\beta_2^{k+1}}.
$$

Adam then uses

$$
x_{k+1}=x_k-\frac{\eta}{\sqrt{\hat v_k}+\epsilon}\odot\hat m_k.
$$

## 7. Newton and quasi-Newton methods

Gradient descent uses slope but not explicit curvature. Newton’s method uses the second-order model

$$
f(x_k+p)\approx f(x_k)+\nabla f(x_k)^Tp+\frac12p^T\nabla^2f(x_k)p.
$$

The Newton step solves

$$
\nabla^2f(x_k)p_k=-\nabla f(x_k),
$$

and updates $x_{k+1}=x_k+p_k$. Although this is mathematically equivalent to multiplying by the inverse Hessian, implementations should solve the linear system rather than explicitly forming the inverse.

If $\nabla f(x^*)=0$, $\nabla^2f(x^*)$ is positive definite, and the Hessian is Lipschitz continuous near $x^*$, then sufficiently close initialisation gives local quadratic convergence:

$$
\|x_{k+1}-x^*\|\leq C\|x_k-x^*\|^2
$$

for some $C>0$. The local and sufficiently-close qualifications matter.

Quasi-Newton methods build curvature approximations from

$$
s_k=x_{k+1}-x_k,
\qquad y_k=\nabla f(x_{k+1})-\nabla f(x_k).
$$

The Hessian approximation satisfies $B_{k+1}s_k=y_k$. For $y_k^Ts_k>0$, inverse-Hessian BFGS uses

$$
H_{k+1}=(I-\rho_ks_ky_k^T)H_k(I-\rho_ky_ks_k^T)+\rho_ks_ks_k^T,
\qquad \rho_k=\frac1{y_k^Ts_k}.
$$

The direction is $p_k=-H_k\nabla f(x_k)$. A suitable line search obtains $x_{k+1}=x_k+\alpha_kp_k$ and supports the curvature condition.

## 8. From equations to Python

A direct gradient-descent implementation stores the current vector, evaluates its gradient, and applies the update. For a quadratic such as $f(x)=\tfrac12x^TAx$, the gradient is $Ax$ when $A$ is symmetric. A diagnostic should check that the step uses the current $x$, that the sign is negative, that the step size is positive and appropriate, and that the objective decreases when the assumptions and step support descent. It is also useful to record iterates and objective values rather than judging success from the final vector alone.

For stochastic code, distinguish a minibatch estimate from the full gradient and remember that noisy objective values need not decrease at every iteration. For Adam, initialise both moment arrays to zero and apply the zero-based bias corrections shown above. For Newton’s method, use a linear solve for the step. These implementation details are the computational meaning of the mathematical updates.

## 9. Exercises and worked solutions

### Exercise 1 — Conceptual and theorem-scope check

A colleague says: “If gradient descent uses $\alpha=1/L$, then every differentiable objective converges at the $O(1/k)$ rate.” Identify the missing assumptions and explain what the first- and second-order conditions do, and do not, establish.

#### Worked solution

The $O(1/k)$ theorem requires that $f$ is $L$-smooth and convex, that a global minimiser $x^*$ exists, and that the step is $\alpha_k=1/L$. Differentiability alone does not supply a Lipschitz gradient, convexity, or a global minimiser. The theorem’s conclusion is the objective bound

$$
f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k},
$$

not a universal statement about arbitrary objectives. The first-order condition says that a differentiable local minimiser must have zero gradient. The second-order necessary condition adds positive-semidefinite Hessian curvature at a $C^2$ local minimiser. Positive-definite Hessian together with zero gradient is sufficient for a strict local minimum, but these conditions are local and do not alone prove global optimality.

### Exercise 2 — Hand calculation

Let $f(x)=\tfrac12x^2$, start from $x_0=4$, and use gradient descent with $\alpha=1/2$. Compute $x_1$, $x_2$, and $f(x_2)$. State the smoothness and strong-convexity constants and the condition number.

#### Worked solution

Here $\nabla f(x)=x$ and $\nabla^2f(x)=1$. Therefore $L=1$ and $\mu=1$, so $\kappa=L/\mu=1$. The update is

$$
x_{k+1}=x_k-\frac12x_k=\frac12x_k.
$$

Hence $x_1=2$ and $x_2=1$. Finally,

$$
f(x_2)=\frac12(1)^2=\frac12.
$$

The iterates move toward the equilibrium point $x^*=0$. The calculation also illustrates that a step can be selected from the smoothness scale: here $\alpha=1/2$ lies in $(0,2/L)=(0,2)$.

### Exercise 3 — Code diagnostic with executable Python

The following program is intended to minimise $f(x)=\tfrac12x^2$ by gradient descent. Identify the bug, correct it, and explain what the printed sequence should show.

```python
import numpy as np

def f(x):
    return 0.5 * x * x

def grad_f(x):
    return x

x = 4.0
alpha = 0.5
values = []
for _ in range(5):
    values.append(f(x))
    x = x + alpha * grad_f(x)

print(values)
print(x)
```

#### Worked solution

The gradient-descent update is $x_{k+1}=x_k-\alpha\nabla f(x_k)$. The program uses a plus sign, so it moves in the direction of increasing $f$. The corrected executable program is:

```python
import numpy as np

def f(x):
    return 0.5 * x * x

def grad_f(x):
    return x

x = 4.0
alpha = 0.5
values = []
for _ in range(5):
    values.append(f(x))
    x = x - alpha * grad_f(x)

print(values)
print(x)
```

The corrected values are $[8.0, 2.0, 0.5, 0.125, 0.03125]$, and the final value is $0.125$. The objective decreases and $x$ approaches zero. The unused NumPy import does not affect this scalar calculation; the substantive diagnostic is the update direction. In a vector implementation, the same sign check applies componentwise through the vector gradient.

## 10. Closing perspective

The central workflow is to identify the objective and its gradients, inspect curvature assumptions, choose a stable step or line search, and monitor both objective and iterate behaviour. Convexity links stationary points to global minimisation; strong convexity supplies a curvature scale and geometric convergence; smoothness controls allowable steps. Momentum, stochastic estimates, adaptive rescaling, Newton curvature, and quasi-Newton approximations modify the basic relaxation process, but every rate statement remains tied to its stated assumptions and initialisation rules.