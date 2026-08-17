# Gradient Descent and Optimisation Through Mechanical Equilibrium

## 1. Potential energy as an optimisation problem

A useful mechanical starting point is equilibrium. Imagine a component, linkage, or elastic structure whose configuration is described by a vector $x\in\mathbb{R}^d$. The vector may contain displacements, rotations, or other coordinates. Let $U(x)$ denote its potential energy. A stable configuration is associated with a local minimum of $U$: a small admissible change from that configuration cannot reduce the energy. Finding equilibrium can therefore be posed as the unconstrained optimisation problem

$$
\min_{x\in\mathbb{R}^d} f(x).
$$

In this lesson, $f$ is a general objective; $U$ is the mechanical example that motivates it. Gradient descent is then a numerical relaxation procedure: calculate the direction in which the objective increases most rapidly, and move in the opposite direction. For a potential-energy objective, this direction corresponds to reducing energy and, in an appropriate coordinate model, relaxing the system toward equilibrium. This analogy is limited: an optimisation iteration is not automatically a physical time evolution, and its step size need not have the units or dynamics of a real mechanical process.

The objective is assumed to be at least continuously differentiable, $f\in C^1$. A first-order method uses evaluations of $f(x)$ and its gradient $\nabla f(x)$ to construct a sequence $\{x_k\}_{k=0}^{\infty}$. The result of the sequence depends on the objective's structure, the step-size rule, and the algorithm. Without suitable assumptions, reaching a stationary point or a global minimiser is not guaranteed.

For a one-dimensional illustration, suppose $U(q)=\tfrac12 kq^2-rq$, where $q$ is a displacement, $k>0$ is a stiffness-like coefficient, and $r$ represents loading. Then $U'(q)=kq-r$. Equilibrium occurs at $U'(q)=0$, so $q^*=r/k$. Gradient descent repeatedly corrects the displacement using the residual slope. The same principle applies in many dimensions, where the scalar derivative becomes a gradient vector.

## 2. Stationarity and curvature

If $x^*$ is a local minimiser of a differentiable function, the first-order necessary condition (FONC) is

$$
\nabla f(x^*)=0.
$$

This condition says that there is no first-order direction of decrease at the candidate configuration. It is necessary, but not by itself sufficient: a stationary point could be a maximum or a saddle point. When $f\in C^2$, the second-order necessary conditions for a local minimum are

$$
\nabla f(x^*)=0,
\qquad
\nabla^2f(x^*)\succeq 0.
$$

The Hessian must be positive semidefinite. The sufficient condition is stronger: if

$$
\nabla f(x^*)=0,
\qquad
\nabla^2f(x^*)\succ0,
$$

then $x^*$ is a strict local minimiser. In mechanical language, positive curvature means that small perturbations increase the local energy to second order. A semidefinite Hessian can indicate a flat direction, so it does not provide the same strict conclusion.

These local conditions should be distinguished from global claims. A global minimiser has objective value no larger than that at any other point. Convexity, introduced next, is what allows a stationary point to have a global interpretation. The numerical method does not discover this distinction from a single gradient value; the assumptions on $f$ supply the theoretical meaning.

## 3. Smoothness and convexity foundations

### $L$-smoothness

A continuously differentiable function $f:\mathbb{R}^d\to\mathbb{R}$ is $L$-smooth, or has an $L$-Lipschitz continuous gradient, when $L>0$ and

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|,
\qquad \forall x,y\in\mathbb{R}^d.
$$

The Euclidean norm is used here. The condition limits how quickly the slope can change. It leads to the descent lemma, also called the quadratic upper bound:

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle
+\frac{L}{2}\|y-x\|^2.
$$

Thus, near $x$, a quadratic with curvature $L$ bounds the objective from above. To see why, write the integral form

$$
f(y)-f(x)=\int_0^1\left\langle
\nabla f\bigl(x+t(y-x)\bigr),y-x\right\rangle\,dt.
$$

Subtract and add $\langle\nabla f(x),y-x\rangle$. Cauchy--Schwarz and Lipschitz continuity bound the remaining integral by $\tfrac L2\|y-x\|^2$, giving the stated inequality.

If $f\in C^2$, $L$-smoothness is equivalent to $\|\nabla^2f(x)\|_2\leq L$ for every $x$. If the function is also convex, this becomes

$$
0\preceq\nabla^2f(x)\preceq LI,
\qquad \forall x.
$$

### Convexity and strong convexity

A differentiable function is convex when

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle,
\qquad \forall x,y\in\mathbb{R}^d.
$$

The tangent plane is therefore a global lower bound. For a convex objective, any point satisfying the first-order condition is a global minimiser, provided a minimiser is attained.

A function is $\mu$-strongly convex, with $\mu>0$, when

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle
+\frac\mu2\|y-x\|^2,
\qquad \forall x,y\in\mathbb{R}^d.
$$

For a twice continuously differentiable function, strong convexity is equivalent to

$$
\nabla^2f(x)\succeq\mu I,
\qquad \forall x.
$$

If $f$ is both $L$-smooth and $\mu$-strongly convex, its condition number is

$$
\kappa=\frac L\mu\geq1.
$$

A large $\kappa$ represents an elongated objective: some directions have much greater curvature than others. This is important for mechanical systems with very different stiffnesses, and it helps explain slow relaxation along shallow directions when the step is restricted by a steep one.

## 4. Standard gradient descent

Given $x_0\in\mathbb{R}^d$ and positive step sizes $\alpha_k$, standard gradient descent (GD) is

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),
\qquad k=0,1,2,\ldots.
$$

The gradient points in the direction of greatest local increase, so its negative is a local descent direction whenever the gradient is nonzero. The step size controls how far the numerical relaxation moves. A step that is too small may be safe but inefficient; a step that is too large can overshoot and may fail to decrease the objective.

### Choosing the step size

With a constant step, $\alpha_k=\alpha$. If $L$ is known, $\alpha=1/L$ is a common choice. Under the usual smooth convex assumptions, a constant step in $(0,2/L)$ is also used. The endpoint and the precise guarantee depend on the theorem being applied, so the assumptions and selected value must be stated together.

Exact line search chooses the best positive step along the current negative-gradient ray:

$$
\alpha_k=\arg\min_{\alpha>0}f\bigl(x_k-\alpha\nabla f(x_k)\bigr).
$$

This can be expensive because it requires solving a one-dimensional minimisation problem. Backtracking line search instead begins with a trial step $\bar\alpha>0$, a contraction factor $\eta\in(0,1)$, and $c\in(0,1)$. It selects the smallest integer $m\geq0$ such that $\alpha_k=\eta^m\bar\alpha$ satisfies the Armijo condition

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)
\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
$$

The right-hand side demands a decrease proportional to the step and squared gradient norm.

### Convergence for smooth convex objectives

If $f$ is $L$-smooth and convex, $x^*$ is a global minimiser, and $\alpha_k=1/L$, then for $k\geq1$,

$$
f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k}.
$$

This is an $O(1/k)$ objective-gap rate. The descent lemma gives

$$
f(x_{k+1})\leq f(x_k)-\frac{1}{2L}\|\nabla f(x_k)\|^2.
$$

Convexity gives

$$
f(x_k)-f(x^*)\leq\langle\nabla f(x_k),x_k-x^*\rangle.
$$

Combining these and using $x_{k+1}=x_k-\nabla f(x_k)/L$ yields

$$
f(x_{k+1})-f(x^*)\leq\frac L2\left(\|x_k-x^*\|^2-\|x_{k+1}-x^*\|^2\right).
$$

Summing from $i=0$ to $k-1$ telescopes the squared-distance terms:

$$
\sum_{i=0}^{k-1}\bigl(f(x_{i+1})-f(x^*)\bigr)
\leq\frac L2\|x_0-x^*\|^2.
$$

The descent inequality makes $f(x_i)$ non-increasing, so the final gap is no larger than the average of the preceding gaps. This proves the bound. The theorem is specifically for an $L$-smooth convex function with a global minimiser and the stated step; it is not a blanket claim for arbitrary objectives.

### Strongly convex objectives

If $f$ is $L$-smooth and $\mu$-strongly convex, GD with

$$
\alpha=\frac{2}{L+\mu}
$$

satisfies

$$
\|x_k-x^*\|^2\leq
\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}
\|x_0-x^*\|^2,
\qquad \kappa=L/\mu.
$$

With $\alpha=1/L$, the objective gap satisfies

$$
f(x_k)-f(x^*)\leq
\left(1-\frac\mu L\right)^k\bigl(f(x_0)-f(x^*)\bigr).
$$

This is linear, or geometric, convergence: each iteration multiplies the bound by a fixed factor below one. The condition number controls how quickly that factor approaches one.

### Reading a convergence statement correctly

Convergence rates are conditional descriptions, not promises attached to the name of an algorithm. Before applying a rate, identify four items: the property assumed of the objective, the quantity being bounded, the step-size rule, and the initialisation or minimiser assumption. For the smooth-convex result, the quantity is the objective gap $f(x_k)-f(x^*)$, the step is exactly $1/L$, and the theorem assumes a global minimiser. For the strongly convex result, the curvature lower bound $\mu>0$ provides a positive curvature scale and produces geometric bounds. Changing the step, dropping convexity, or replacing a full gradient with a noisy estimate changes the problem being analysed.

The condition number also gives a practical diagnostic. If $\kappa$ is large, a step safe for the steepest direction can be too cautious in a shallow direction. The iterates may make visible progress while the objective gap decreases slowly. Rescaling coordinates can change this geometry, but it does not change the basic GD update or automatically establish a new theorem. In a mechanical calculation, this is analogous to recognising that different stiffness scales can make a direct relaxation procedure poorly balanced. The mathematics tells us what guarantee follows from the stated assumptions; plots, residuals, and objective values then help us check whether an implementation behaves consistently with those assumptions.

## 5. Momentum and acceleration

### Heavy-ball method

Polyak's heavy-ball method adds the previous displacement to GD:

$$
x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1}),
$$

where $\beta\in[0,1)$. The additional term carries directional memory, which can help traverse a shallow valley rather than repeatedly correcting across it. The parameters must be chosen to keep the iteration stable.

For the specific strongly convex quadratic

$$
f(x)=\frac12x^TAx,
$$

where $A$ is symmetric positive definite and its spectrum lies in $[\mu,L]$, the choices

$$
\alpha^*=\frac{4}{(\sqrt L+\sqrt\mu)^2},
\qquad
\beta^*=\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^2
$$

improve the dependence of the contraction factor on the condition number from $1-O(1/\kappa)$ to $1-O(1/\sqrt\kappa)$. These parameter claims apply to the stated quadratic setting; they should not be transferred unqualified to every nonlinear mechanical objective.

### Nesterov accelerated gradient

For the supplied smooth-convex NAG variant, initialise $y_0=x_0$ and $\lambda_0=1$. For $k\geq0$, evaluate the gradient at the look-ahead point and take

$$
x_{k+1}=y_k-\frac1L\nabla f(y_k).
$$

Then update

$$
\lambda_{k+1}=\frac{1+\sqrt{1+4\lambda_k^2}}2,
$$

and

$$
y_{k+1}=x_{k+1}+\frac{\lambda_k-1}{\lambda_{k+1}}(x_{k+1}-x_k).
$$

The gradient is evaluated at $y_k$, not necessarily at $x_k$. For an $L$-smooth convex function with a global minimiser, this parameterisation satisfies

$$
f(x_k)-f(x^*)\leq\frac{2L\|x_0-x^*\|^2}{(k+1)^2}=O(1/k^2).
$$

The faster rate comes with a more involved update and greater sensitivity to implementation details.

## 6. Stochastic gradient optimisation

Suppose the objective is empirical:

$$
f(x)=\frac1N\sum_{i=1}^Nf_i(x).
$$

A full gradient costs $O(N)$ if all terms must be evaluated. Stochastic gradient descent (SGD) replaces it by an estimate $g_k(x_k)$ and uses

$$
x_{k+1}=x_k-\eta_kg_k(x_k).
$$

A common model assumes conditional unbiasedness and bounded conditional variance:

$$
\mathbb E[g_k(x_k)\mid x_k]=\nabla f(x_k),
$$

$$
\mathbb E[\|g_k(x_k)-\nabla f(x_k)\|^2\mid x_k]\leq\sigma^2.
$$

The estimate is therefore correct on average, but individual updates fluctuate. With persistent nonzero variance, a sufficiently small constant step generally gives a nonzero error floor rather than exact convergence. Under standard smooth strongly convex assumptions, the expected error approaches a neighbourhood whose size depends on step size and noise variance.

For diminishing-step convergence results, the Robbins--Monro conditions are

$$
\sum_{k=1}^{\infty}\eta_k=\infty,
\qquad
\sum_{k=1}^{\infty}\eta_k^2<\infty.
$$

These conditions are not sufficient by themselves. A complete convergence theorem must also specify suitable assumptions on the objective, stochastic-gradient bias and moments, and stability of the iterates. In a mechanical analogy, noisy force or residual measurements can make relaxation jitter around equilibrium; reducing the step can reduce the jitter, but the guarantee depends on more than that reduction alone.

## 7. Adaptive learning-rate methods

The following formulas act element by element. In every method, $\epsilon>0$ prevents division by zero.

### AdaGrad

Starting with $v_{-1}=0$ and indexing gradients from $k=0$, AdaGrad accumulates squared gradients:

$$
v_k=v_{k-1}+g_k\odot g_k,
$$

$$
x_{k+1}=x_k-\frac\eta{\sqrt{v_k}+\epsilon}\odot g_k.
$$

Coordinates with a history of large gradients receive progressively smaller effective steps.

### RMSProp

Starting with $v_{-1}=0$ and using $\gamma\in[0,1)$, RMSProp replaces the unbounded accumulation by an exponential moving average:

$$
v_k=\gamma v_{k-1}+(1-\gamma)g_k\odot g_k,
$$

$$
x_{k+1}=x_k-\frac\eta{\sqrt{v_k}+\epsilon}\odot g_k.
$$

Recent squared gradients have greater influence than remote ones, allowing the scale estimate to adapt as the iteration proceeds.

### Adam

Starting with $m_{-1}=v_{-1}=0$ and using $\beta_1,\beta_2\in[0,1)$, Adam maintains a first-moment estimate and a second-moment estimate:

$$
m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,
$$

$$
v_k=\beta_2v_{k-1}+(1-\beta_2)(g_k\odot g_k).
$$

Because zero initial states bias early averages toward zero, for indices beginning at $k=0$ use

$$
\hat m_k=\frac{m_k}{1-\beta_1^{k+1}},
\qquad
\hat v_k=\frac{v_k}{1-\beta_2^{k+1}}.
$$

The update is

$$
x_{k+1}=x_k-\frac\eta{\sqrt{\hat v_k}+\epsilon}\odot\hat m_k.
$$

The moving average of gradients supplies directional smoothing, while the second moment supplies coordinate scaling. These methods change the update rule; they do not remove the need to choose a suitable learning rate or to understand the objective.

## 8. Second-order methods

### Newton's method

Newton's method uses the second-order Taylor model

$$
f(x_k+p)\approx f(x_k)+\nabla f(x_k)^Tp+\frac12p^T\nabla^2f(x_k)p.
$$

The Newton step solves

$$
\nabla^2f(x_k)p_k=-\nabla f(x_k),
$$

and the iterate is

$$
x_{k+1}=x_k+p_k.
$$

When the Hessian is invertible, this is mathematically equivalent to

$$
x_{k+1}=x_k-[\nabla^2f(x_k)]^{-1}\nabla f(x_k).
$$

In implementation, solve the linear system rather than explicitly forming the Hessian inverse. If $\nabla f(x^*)=0$, $\nabla^2f(x^*)$ is positive definite, and the Hessian is Lipschitz continuous near $x^*$, then sufficiently close initialisation gives locally well-defined iterates satisfying

$$
\|x_{k+1}-x^*\|\leq C\|x_k-x^*\|^2
$$

for some $C>0$. This local quadratic convergence theorem requires the listed conditions and a sufficiently close $x_0$.

### Quasi-Newton BFGS

Quasi-Newton methods approximate the Hessian or its inverse using changes in iterates and gradients:

$$
s_k=x_{k+1}-x_k,
\qquad
y_k=\nabla f(x_{k+1})-\nabla f(x_k).
$$

A Hessian approximation satisfies the secant equation

$$
B_{k+1}s_k=y_k.
$$

For $y_k^Ts_k>0$, the inverse-Hessian BFGS update is

$$
H_{k+1}=(I-\rho_ks_ky_k^T)H_k(I-\rho_ky_ks_k^T)+\rho_ks_ks_k^T,
\qquad
\rho_k=\frac1{y_k^Ts_k}.
$$

The search direction is $p_k=-H_k\nabla f(x_k)$. In practice, a suitable line search obtains $x_{k+1}=x_k+\alpha_kp_k$ and supports the curvature condition $y_k^Ts_k>0$. BFGS uses curvature information without directly computing a new Hessian at every step.

## 9. Translating the mathematics into Python

An implementation should mirror the notation rather than hide it. Store the current iterate in an array `x`, compute the gradient at that same iterate, choose a scalar or element-wise step according to the selected method, and then form the next iterate. For GD, the essential order is: evaluate `gradient = grad(x)`, then assign `x = x - alpha * gradient`. Evaluating the gradient after overwriting `x` would describe a different procedure. For NAG, keep separate arrays for `x` and the look-ahead point `y`; the gradient must be evaluated at $y_k$. For Adam, initialise both moment arrays to zero and use the iteration index consistently in the bias-correction powers.

Useful diagnostics are simple. Print or record the objective, gradient norm, and iterate at regular intervals. On a test quadratic, compare the observed objective sequence with the expected decrease and check that the gradient has the same shape as the iterate. If the objective increases immediately, inspect the sign of the update and the step size. If one coordinate changes much faster than another, inspect curvature and conditioning before changing the algorithm. A code result is evidence about the implementation; it is not, by itself, a proof that the assumptions of a convergence theorem hold.

## Worked exercises

### Exercise 1 — theorem scope: identify a valid guarantee

An engineer applies GD with $\alpha=1/L$ to an objective and reports the bound

$$
f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k}.
$$

What assumptions must be checked before this report is justified? Explain why the same statement cannot automatically be used for a nonconvex objective or for SGD with persistent noise.

**Solution.** The bound requires that $f$ is $L$-smooth and convex, that $x^*$ is a global minimiser, and that the GD step is $\alpha_k=1/L$. The quantity bounded is the objective gap, not necessarily the distance to the minimiser. For a nonconvex objective, the convexity inequality used in the proof is unavailable, so the stated global objective-gap result does not follow. For SGD with persistent nonzero variance, the update uses a noisy estimate rather than the full gradient; with a constant step, the expected error generally approaches a noise-dependent neighbourhood rather than converging exactly. A different theorem would require its own assumptions and conclusion.

$$
f(y)-f(x)=\int_0^1\langle\nabla f(x+td),d\rangle\,dt.
$$

Add and subtract $\nabla f(x)$ inside the inner product:

$$
f(y)-f(x)=\langle\nabla f(x),d\rangle+
\int_0^1\langle\nabla f(x+td)-\nabla f(x),d\rangle\,dt.
$$

By Cauchy--Schwarz and $L$-smoothness, the integrand is at most $Lt\|d\|^2$. Integrating $Lt$ from zero to one gives $L\|d\|^2/2$. Substituting $d=y-x$ produces

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle+\frac L2\|y-x\|^2.
$$

### Exercise 2 — numerical relaxation: one-dimensional GD

Let $f(q)=\tfrac12q^2$, with $q_0=4$ and constant $\alpha=1/2$. Compute three updates and explain the result.

**Solution.** Since $f'(q)=q$, the update is $q_{k+1}=q_k-\tfrac12q_k=\tfrac12q_k$. Hence

$$
q_1=2,
\qquad q_2=1,
\qquad q_3=0.5.
$$

The equilibrium minimiser is $q^*=0$. The displacement approaches zero geometrically, while the energy values are $8$, $2$, $0.5$, and $0.125$ at $q_0,q_1,q_2,q_3$, respectively. The step is stable here because the quadratic has $L=1$ and $\alpha=1/2$ lies in $(0,2/L)$.

### Exercise 3 — code diagnostic: implement and test GD

The following executable Python program minimises $f(x)=\tfrac12x^TAx$ for a diagonal positive-definite matrix. Identify the update, run it, and state why the objective decreases.

```python
import numpy as np

A = np.diag([1.0, 4.0])
x = np.array([4.0, -2.0])
alpha = 1.0 / 4.0

for k in range(6):
    value = 0.5 * x @ A @ x
    gradient = A @ x
    print(k, x, value)
    x = x - alpha * gradient
```

**Solution.** For this quadratic, $\nabla f(x)=Ax$, so the assignment `x = x - alpha * gradient` is exactly the GD update. The eigenvalues of $A$ are $1$ and $4$, hence $L=4$. The program uses $\alpha=1/L$, the step in the smooth-convex convergence result. Each printed objective is non-increasing because the descent lemma gives

$$
f(x_{k+1})\leq f(x_k)-\frac1{2L}\|\nabla f(x_k)\|^2.
$$

The second coordinate contracts more rapidly because its curvature is larger: its multiplier is $1-\alpha\cdot4=0$, whereas the first coordinate's multiplier is $1-\alpha\cdot1=0.75$. The code is diagnostic because printing the state and objective makes a wrong sign, wrong gradient, or unsuitable step visible immediately.
