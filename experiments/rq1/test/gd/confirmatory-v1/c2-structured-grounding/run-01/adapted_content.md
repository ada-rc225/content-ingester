# Gradient Descent and Optimisation

<!-- section: SEC-01 -->
## From engineering design to an optimisation problem

Mechanical design often asks for a good vector of adjustable quantities: dimensions, material parameters, controller gains, or coefficients in a reduced model. Let $x\in\mathbb{R}^d$ collect those quantities and let $f(x)$ measure the performance we want to reduce. In unconstrained optimisation the mathematical problem is

$$\min_{x\in\mathbb{R}^d} f(x).$$

Here $f:\mathbb{R}^d\to\mathbb{R}$ is assumed to be at least continuously differentiable. “Unconstrained” is important: bounds on a thickness or a stress limit would create a different constrained problem, whereas this lesson studies the unconstrained core.

A local minimiser $x^*$ is a point whose objective is no larger than that of nearby points. If $f$ is differentiable at a local minimiser, the first-order necessary condition is

$$\nabla f(x^*)=0.$$

The condition says that every first-order directional change vanishes. It does not say that every stationary point is a minimum: a saddle point can also have zero gradient. In a calibration model, a zero residual gradient therefore identifies a candidate, not a complete certificate.

When $f$ is $C^2$, the Hessian supplies the second-order test. At a local minimiser, stationarity together with a positive-semidefinite Hessian is necessary. Conversely, stationarity together with a positive-definite Hessian is sufficient for a strict local minimiser. These statements have different logical directions. Positive semidefiniteness allows flat directions; positive definiteness rules them out locally. The test is local, so it does not by itself prove that the point is the best design in all of $\mathbb{R}^d$.

<!-- section: SEC-02 -->
## Smoothness, convexity, and the geometry of curvature

### Two useful bounds

A gradient is $L$-Lipschitz, or $L$-smooth, when $L>0$ and

$$\|\nabla f(x)-\nabla f(y)\|\le L\|x-y\|,\qquad\forall x,y\in\mathbb{R}^d.$$

This controls how quickly slopes change. It is not the same as saying that function values are Lipschitz. Integrating this gradient control gives the Descent Lemma, the quadratic upper bound

$$f(y)\le f(x)+\langle\nabla f(x),y-x\rangle+\frac{L}{2}\|y-x\|^2,$$

for all $x,y$. The linear term predicts the immediate change; the quadratic term is a safety allowance for curvature.

Differentiable convexity is described by a global first-order lower bound:

$$f(y)\ge f(x)+\langle\nabla f(x),y-x\rangle,$$

for all $x,y$. Every tangent plane lies below the graph. Strong convexity adds a positive quadratic gap: for $\mu>0$,

$$f(y)\ge f(x)+\langle\nabla f(x),y-x\rangle+\frac{\mu}{2}\|y-x\|^2,$$

again for all $x,y$. Thus strong convexity supplies curvature in every direction rather than merely forbidding a tangent plane from crossing above the function.

### Hessians and conditioning

For a $C^2$ objective, the Hessian description makes these ideas concrete. Smooth convexity has

$$0\preceq\nabla^2 f(x)\preceq LI,\qquad\forall x,$$

where the positive-semidefinite lower bound includes the convexity assumption. Strong convexity has $\nabla^2 f(x)\succeq\mu I$ for every $x$. If both properties hold, the condition number is

$$\kappa=\frac{L}{\mu}\ge1.$$

A large $\kappa$ means that some directions can be much more curved than others. In a mechanical model this resembles a design surface with a stiff direction and a compliant direction: an isotropic step must respect the stiff direction even while progress in the compliant direction remains slow. This geometric picture motivates momentum, coordinate scaling, and curvature methods, but it does not change the definitions or their assumptions.

<!-- section: SEC-03 -->
## Gradient descent and choosing a step

### The basic update

Gradient descent evaluates the gradient at the current iterate and moves opposite to it:

$$x_{k+1}=x_k-\alpha_k\nabla f(x_k),\qquad k=0,1,2,\ldots,$$

with $x_0\in\mathbb{R}^d$ and positive $\alpha_k$. The minus sign is essential: the gradient points in the direction of local increase. A constant-step method sets $\alpha_k=\alpha$. If $L$ is known, $1/L$ is a common choice, and under the usual smooth-convex assumptions the source also gives the interval $\alpha\in(0,2/L)$. That interval is not a universal guarantee without those assumptions.

The Descent Lemma explains why a short enough step works. Substituting $y=x-\alpha\nabla f(x)$ produces a linear decrease opposed by a quadratic curvature cost. The step-size problem is therefore a balance between moving far enough to make progress and avoiding an unstable overshoot.

Exact line search chooses the positive step that minimises the objective along the current negative-gradient ray:

$$\alpha_k=\arg\min_{\alpha>0}f\bigl(x_k-\alpha\nabla f(x_k)\bigr).$$

It can be expensive because each trial needs objective information. Armijo backtracking is cheaper and adaptive. Start from a positive trial $\bar\alpha$, use a contraction factor $\eta\in(0,1)$, and choose $c\in(0,1)$. The smallest nonnegative $m$ is accepted when $\alpha_k=\bar\alpha\eta^m$ satisfies

$$f(x_k-\alpha_k\nabla f(x_k))\le f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.$$

The squared gradient norm makes the required decrease scale with the local direction. Exact search minimises along the ray; Armijo accepts sufficient decrease.

### What convergence claims mean

For an $L$-smooth convex objective with a global minimiser $x^*$, gradient descent with $\alpha_k=1/L$ satisfies, for $k\ge1$,

$$f(x_k)-f(x^*)\le\frac{L\|x_0-x^*\|^2}{2k}.$$

This is an objective-gap guarantee with an $O(1/k)$ dependence, and every hypothesis matters. Strong convexity gives sharper results. For an $L$-smooth, $\mu$-strongly convex objective, the step $\alpha=2/(L+\mu)$ gives

$$\|x_k-x^*\|^2\le\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}\|x_0-x^*\|^2,$$

whereas the objective contraction uses the stated step $\alpha=1/L$:

$$f(x_k)-f(x^*)\le\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).$$

Do not attach the distance rate to $1/L$, or the objective rate to $2/(L+\mu)$. Rates are statements about a method under a specified step and specified geometry.

The implementation mirrors the mathematics: compute `gradient = grad(x)`, then `x = x - alpha * gradient`. A vector library performs the subtraction component by component. Logging objective values and gradient norms helps diagnose a poor step, but logging is not a substitute for the assumptions behind a theorem.

<!-- section: SEC-04 -->
## Momentum, acceleration, and stochastic gradients

### Heavy Ball and Nesterov acceleration

Heavy Ball adds a memory term to the current-gradient step:

$$x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1}),$$

where $\beta\in[0,1)$ and the parameters must keep the iteration stable. The gradient is evaluated at $x_k$, not at a look-ahead point. For the special quadratic $f(x)=\frac12x^TAx$, with $A$ symmetric positive definite and spectrum in $[\mu,L]$, the stated optimal parameters are

$$\alpha^*=\frac{4}{(\sqrt L+\sqrt\mu)^2},\qquad\beta^*=\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^2.$$

The improved condition-number dependence belongs specifically to that quadratic setting; it is not a general claim for every nonlinear engineering objective.

The Nesterov variant here starts with $y_0=x_0$ and $\lambda_0=1$. For $k$ starting at zero, it evaluates the gradient at $y_k$:

$$x_{k+1}=y_k-\frac1L\nabla f(y_k),$$
$$\lambda_{k+1}=\frac{1+\sqrt{1+4\lambda_k^2}}2,$$
$$y_{k+1}=x_{k+1}+\frac{\lambda_k-1}{\lambda_{k+1}}(x_{k+1}-x_k).$$

This indexing is part of the algorithm. For an $L$-smooth convex objective with a global minimiser and this recurrence, the objective gap obeys

$$f(x_k)-f(x^*)\le\frac{2L\|x_0-x^*\|^2}{(k+1)^2}=O(1/k^2).$$

The rate belongs to this parameterisation and convex scope.

### Stochastic gradients

For an empirical objective $f(x)=\frac1N\sum_{i=1}^Nf_i(x)$, a stochastic estimate $g_k(x_k)$ is modelled conditionally on the current iterate. The assumptions are

$$\mathbb E[g_k(x_k)\mid x_k]=\nabla f(x_k),$$
$$\mathbb E[\|g_k(x_k)-\nabla f(x_k)\|^2\mid x_k]\le\sigma^2.$$

The first is conditional unbiasedness; the second is a conditional variance bound. SGD uses

$$x_{k+1}=x_k-\eta_kg_k(x_k).$$

With persistent nonzero variance and a small constant step, the usual smooth strongly convex setting generally has a nonzero error floor rather than exact convergence. Decreasing steps reduce the noise influence. The Robbins–Monro conditions are

$$\sum_{k=1}^{\infty}\eta_k=\infty,\qquad\sum_{k=1}^{\infty}\eta_k^2<\infty.$$

They are not sufficient alone: a convergence theorem also needs appropriate objective, bias, moment, and iterate-stability assumptions. In practice, minibatch size and step schedule are modelling choices, not merely coding details.

<!-- section: SEC-05 -->
## Coordinate scaling and adaptive methods

Adaptive methods alter the effective scale of each coordinate using gradient history. AdaGrad starts with $v_{-1}=0$ and, for gradients indexed from $k=0$, accumulates

$$v_k=v_{k-1}+g_k\odot g_k,$$
$$x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k,$$

where $\epsilon>0$ and all products and square roots are element-wise. A coordinate that has repeatedly received large gradients is reduced more strongly. The accumulation is permanent.

RMSProp replaces permanent accumulation by an exponential moving average:

$$v_k=\gamma v_{k-1}+(1-\gamma)g_k\odot g_k,$$
$$x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k,$$

with $\gamma\in[0,1)$ and $\epsilon>0$. The factor $(1-\gamma)$ is part of the average. RMSProp can forget old scales, unlike AdaGrad.

Adam tracks both a first moment and a second moment. Initialise $m_{-1}=v_{-1}=0$, use $\beta_1,\beta_2\in[0,1)$, and for $k=0,1,\ldots$ compute

$$m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,$$
$$v_k=\beta_2v_{k-1}+(1-\beta_2)(g_k\odot g_k).$$

Because both moments start at zero, correct them using $k+1$:

$$\hat m_k=\frac{m_k}{1-\beta_1^{k+1}},\qquad\hat v_k=\frac{v_k}{1-\beta_2^{k+1}},$$
$$x_{k+1}=x_k-\frac{\eta}{\sqrt{\hat v_k}+\epsilon}\odot\hat m_k.$$

The final update uses corrected moments, not raw moments. In Python, `*` and `/` on array objects are element-wise, while matrix multiplication has a different meaning. That distinction is as important as choosing the correct recurrence.

<!-- section: SEC-06 -->
## Using curvature: Newton and BFGS

### Newton's method

Gradient descent uses slope information. Newton's method also uses local curvature through the second-order Taylor model

$$f(x_k+p)\approx f(x_k)+\nabla f(x_k)^Tp+\frac12p^T\nabla^2f(x_k)p.$$

The approximation is a model in the step $p$, not an exact identity for a general objective. Minimising the model gives the linear system

$$\nabla^2f(x_k)p_k=-\nabla f(x_k),\qquad x_{k+1}=x_k+p_k.$$

The inverse expression $x_{k+1}=x_k-[\nabla^2f(x_k)]^{-1}\nabla f(x_k)$ is mathematically equivalent only when the Hessian is invertible. Numerical code should solve the linear system rather than explicitly form the inverse. A Hessian can also be indefinite away from a minimiser, so a practical method may need a line search; that implementation choice does not alter the stated Newton step.

Under stationarity at $x^*$, a positive-definite Hessian there, locally Lipschitz Hessian, and sufficiently close initialisation, Newton iterates have local quadratic convergence:

$$\|x_{k+1}-x^*\|\le C\|x_k-x^*\|^2.$$

“Local” and “sufficiently close” are essential. This is not a global convergence claim.

### BFGS without an explicit Hessian

BFGS learns curvature from successive iterates. Define

$$s_k=x_{k+1}-x_k,\qquad y_k=\nabla f(x_{k+1})-\nabla f(x_k).$$

The next Hessian approximation satisfies the secant equation $B_{k+1}s_k=y_k$. In inverse-Hessian form, for positive curvature $y_k^Ts_k>0$,

$$H_{k+1}=(I-\rho_ks_ky_k^T)H_k(I-\rho_ky_ks_k^T)+\rho_ks_ks_k^T,$$
$$\rho_k=\frac1{y_k^Ts_k}.$$

The search direction is $p_k=-H_k\nabla f(x_k)$, and a suitable line search supports the curvature condition. The order of $s_k$ and $y_k$, the transpose placement, the negative direction, and the line search all matter. BFGS is attractive when forming a full Hessian is costly, while Newton is attractive when accurate curvature and reliable linear solves are available.

Across all methods, implementation follows a disciplined loop: represent the current vector, evaluate the method-specific gradient or moments at the specified point, form the stated direction, choose or apply the step, and record diagnostics. The equations tell you exactly which value must be current, stored, corrected, or solved for.

### Reading an optimisation loop as an engineer

Suppose a reduced structural model predicts a displacement vector from a small set of stiffness parameters. A scalar objective might compare predicted and measured responses, but the optimisation routine does not need to know whether a coordinate represents a thickness, a modulus, or a damping coefficient. It needs a vector, an objective evaluation, and the derivative information promised by the selected method. That separation is useful: the model expresses engineering meaning, while the optimiser manages a repeatable numerical search.

Before choosing a method, inspect the objective and the information available. If derivatives are available and the dimension is moderate, gradient descent is a transparent baseline. If a reliable global smoothness estimate is available, $1/L$ gives a reproducible reference step. If estimating $L$ is inconvenient, backtracking can test actual objective decrease. Exact line search is useful for understanding the ideal one-dimensional choice, even when its repeated objective evaluations would be too expensive inside a large simulation.

The geometry should influence expectations. A convex objective has no misleading local basin: every local minimum is global, although a flat direction can still make progress slow. Strong convexity adds a unique-curvature scale and supports the stated geometric contractions. A large condition number warns that a circular step may zig-zag across a narrow valley. In that situation, rescaling variables before optimisation can be as important as changing the optimiser. Rescaling is a modelling decision; it does not permit silently changing a theorem's $L$ or $\mu$.

### A practical comparison of methods

Gradient descent is easiest to inspect and is therefore a good first implementation. Heavy Ball stores one previous iterate and can use its displacement as directional memory. The memory is helpful only when the parameters are stable; a larger momentum coefficient is not automatically better. Nesterov acceleration uses a different point for the gradient evaluation and a specific recurrence for its auxiliary sequence. Confusing these two methods is not a harmless naming difference: it changes the update and the scope of the associated rate.

Stochastic methods trade exact gradients for cheaper, noisier estimates. A batch assembled from simulation cases or measured tests may give an unbiased estimate conditionally on the current parameter vector, but a single batch still has variance. A constant step can be appropriate when tracking a changing target, yet in the persistent-variance setting it should be interpreted with the error-floor qualification. Diminishing steps change that long-run balance, and the two series conditions are a useful diagnostic rather than a complete convergence theorem.

Adaptive methods are often convenient when parameter coordinates have different numerical scales. AdaGrad remembers all past squared gradients and can eventually make an active coordinate's steps very small. RMSProp forgets old information through its moving average. Adam combines a moving average of gradients with a moving average of squared gradients and corrects the startup bias from zero initial moments. In each case, epsilon protects the denominator, but it does not repair a wrong sign, a wrong index, or a mismatch between matrix and element-wise operations.

Newton and BFGS use curvature differently. Newton computes a Hessian at the current point and solves for a step, so its per-iteration work can be high but its local model is rich. BFGS builds an inverse-Hessian approximation from observed changes. The secant equation says that the approximation reproduces the latest gradient change along the latest step; it is a precise algebraic requirement, not merely a smoothing heuristic. Both methods still need sensible globalisation when the initial point is not in the local regime described by their convergence statements.

### A Python checklist

Start a routine with an explicit initial vector and a named positive step size. Keep the gradient function separate from the update so that it can be tested at a known point. For standard gradient descent, the order should be current vector, current gradient, new vector. For Nesterov, name both $x$ and $y$ so that evaluating the gradient at the auxiliary point is visible. For Adam, initialise both moment arrays with the same shape as the gradient and use the current zero-based index in the bias corrections.

For array code, inspect whether an operation is element-wise or a matrix operation. AdaGrad, RMSProp, and Adam require element-wise products, square roots, and divisions. Newton requires a linear solve with the Hessian and gradient, not an explicit inverse. A short diagnostic run should print the objective, gradient norm, and iterate for a few steps. If the objective rises immediately, check the sign and the point at which the gradient was evaluated before changing the algorithm.

Finally, record which assumptions your result uses. A plot that decreases on one test is empirical evidence about that test, not a proof of a global rate. A local quadratic Newton pattern does not establish global convergence. A stochastic run that reaches a small loss does not remove the variance assumption. This habit of pairing every numerical observation with its mathematical scope is central to using optimisation responsibly in mechanical simulation and design.

The most reliable workflow is therefore incremental. First test the objective and gradient on a point where the derivative can be checked by hand. Next run one update and verify its sign and scale. Then compare objective values over several iterations, varying the step only after the baseline behaves sensibly. Once the baseline is understood, add backtracking, momentum, stochastic sampling, adaptive scaling, or curvature information one change at a time. This makes a failure informative: an unexpected result can be traced to a model, a derivative, an update, or an assumption rather than being hidden inside a large software stack.

<!-- section: SEC-07 -->
## Exercises and worked solutions

<!-- exercise: EX-001 -->
### Exercise 1: Match a theorem to its scope

A finite-element calibration objective is smooth and convex, has a global minimiser, and uses gradient descent with step $1/L$. Which conclusion is justified: (a) the objective gap has the $O(1/k)$ bound; (b) the Nesterov $O(1/k^2)$ bound; (c) Heavy Ball's parameters are optimal; or (d) Newton is globally quadratically convergent? State the missing assumptions that prevent the other choices.

<!-- solution: EX-001 -->
### Worked solution

Choice (a) is justified. The convex gradient-descent result requires smoothness, convexity, a global minimiser, step $1/L$, and $k\ge1$. The Nesterov rate additionally requires the specified Nesterov recurrence. Heavy Ball's displayed parameters require a symmetric-positive-definite quadratic with spectrum in $[\mu,L]$. Newton's quadratic result is local and requires stationarity, positive-definite Hessian, locally Lipschitz Hessian, and sufficiently close initialisation. The exercise therefore tests theorem scope rather than just the appearance of a rate.

<!-- exercise: EX-002 -->
### Exercise 2: One design-variable update

For the objective $f(x,y)=(x-2)^2+0.5(y+1)^2$, use the point $(x_0,y_0)=(1,2)$ and step size $\alpha=0.25$. Find the gradient and perform one gradient-descent update. Check that the step is positive and that the update uses the gradient at the current point.

The derivatives are $\partial f/\partial x=2(x-2)$ and $\partial f/\partial y=y+1$. At $(1,2)$, the gradient is $(-2,3)$. Therefore

$$\begin{bmatrix}x_1\\y_1\end{bmatrix}=\begin{bmatrix}1\\2\end{bmatrix}-0.25\begin{bmatrix}-2\\3\end{bmatrix}=\begin{bmatrix}1.5\\1.25\end{bmatrix}.$$

<!-- solution: EX-002 -->
### Worked solution

The gradient calculation gives $\nabla f(1,2)=(-2,3)$. Since $0.25>0$, the standard update subtracts $0.25$ times that current gradient: the first coordinate increases by $0.5$, and the second decreases by $0.75$. Thus the checked point is $(1.5,1.25)$.

<!-- derived-answer: EX-002 -->
**Result from the derivation:** `[1.5, 1.25]`

<!-- answer: EX-002 -->
**Checked answer:** `[1.5, 1.25]`

<!-- exercise: EX-003 -->
### Exercise 3: Diagnose a Python update

The following routine is intended to minimise $q(z)=0.5z^2$ from $z=2.0$:

```text
z = 2.0
alpha = 0.25
for _ in range(2):
    gradient = z
    z = z + alpha * gradient
print(z)
```

Identify the bug and provide corrected code. The corrected routine should evaluate the gradient at the current iterate and subtract a positive step-size multiple.

<!-- solution: EX-003 -->
### Worked solution

The bug is the plus sign. For $q(z)=0.5z^2$, the gradient is $z$, so the intended update is `z = z - alpha * gradient`. The two corrected steps are $2\mapsto1.5\mapsto1.125$.

```python
z = 2.0
alpha = 0.25
for _ in range(2):
    gradient = z
    z = z - alpha * gradient
print(z)
```

<!-- expected-stdout: EX-003/1 -->
**Expected output:** `"1.125\n"`
