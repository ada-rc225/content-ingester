# Gradient Descent and Optimisation

<!-- section: SEC-01 -->
## The optimisation problem and what a minimum means

Mechanical design often asks us to choose several quantities together: a thickness, a material parameter, or a controller setting. In the mathematical model, collect those quantities in a vector $x\in\mathbb{R}^d$. Unconstrained optimisation studies

$$\min_{x\in\mathbb{R}^d} f(x).$$

Here $f:\mathbb{R}^d\to\mathbb{R}$ is the objective, and the baseline assumption is that it is continuously differentiable, or at least $C^1$. The formulation is unconstrained: bounds, contact conditions, and design rules would create a different problem that needs additional treatment.

A local minimiser $x^*$ is a point whose objective is no larger than that of sufficiently nearby points. If $f$ is differentiable there, every directional first-order change must disappear, so the necessary first-order condition is

$$\nabla f(x^*)=0.$$

This is a test for a candidate, not a certificate that the candidate is a minimum. A stationary point may be a maximum or a saddle point. For example, the derivative of a curve can vanish at a turning point that is not a low point.

### Second-order information

Suppose now that the objective is $C^2$. At a local minimiser, stationarity is still necessary and the Hessian must be positive semidefinite:

$$\nabla f(x^*)=0,\qquad \nabla^2 f(x^*)\succeq 0.$$

Positive semidefinite means that $z^T\nabla^2f(x^*)z\geq0$ for every direction $z$. Curvature can be flat in one direction, so this condition does not by itself establish a strict minimum. Conversely, if

$$\nabla f(x^*)=0,\qquad \nabla^2f(x^*)\succ0,$$

then the Hessian is positive definite and $x^*$ is a strict local minimiser. The distinction between necessary and sufficient conditions matters when interpreting a numerical stopping point: a small gradient is evidence for stationarity, but curvature and the objective landscape determine what that stationarity means.

<!-- section: SEC-02 -->
## Geometry of smooth and convex objectives

### Smoothness as a bound on changing slopes

An objective is $L$-smooth when its gradient is $L$-Lipschitz in the Euclidean norm:

$$\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|,\qquad\forall x,y\in\mathbb{R}^d,$$

where $L>0$. This controls how quickly slopes can change; it is not a claim that function values themselves are Lipschitz. Smoothness gives the Descent Lemma, a quadratic upper model valid for every pair of points:

$$f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle+\frac{L}{2}\|y-x\|^2.$$

The linear term predicts the local change and the quadratic term protects us against curvature that the linear approximation misses. In a design calculation, $L$ is a conservative scale for how aggressively a step can respond to the current sensitivity.

### Convexity and strong convexity

A differentiable function is convex when its tangent plane is a global lower bound:

$$f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle,\qquad\forall x,y\in\mathbb{R}^d.$$

Thus every tangent supports the graph from below. If a differentiable convex objective has a stationary point, that point is globally optimal, which is stronger than the general first-order statement above.

A function is $\mu$-strongly convex when the lower bound includes positive curvature:

$$f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle+\frac{\mu}{2}\|y-x\|^2,$$

with $\mu>0$. Strong convexity rules out arbitrarily flat directions and gives a unique minimiser when one exists. An analogy can help: a convex bowl has no misleading downward basin, while a strongly convex bowl also has a guaranteed minimum amount of curvature; this picture is only an interpretation of the inequalities, not an extra assumption.

For a $C^2$ objective, the Hessian supplies a local curvature test across the whole domain. Smooth convexity corresponds to

$$0\preceq\nabla^2f(x)\preceq LI,\qquad\forall x,$$

where the positive-semidefinite lower bound includes the convexity qualifier. Strong convexity corresponds to

$$\nabla^2f(x)\succeq\mu I,\qquad\forall x.$$

When both properties hold, the condition number is

$$\kappa=\frac{L}{\mu}\geq1.$$

A large $\kappa$ describes an elongated landscape: a step safe for a steep direction may be unnecessarily cautious along a shallow one. This is why scaling and preconditioning are important in engineering models.

<!-- section: SEC-03 -->
## Gradient descent and choosing a step

Gradient descent uses the negative current gradient as its search direction. Starting from $x_0\in\mathbb{R}^d$ and using a positive step size $\alpha_k$, its update is

$$x_{k+1}=x_k-\alpha_k\nabla f(x_k),\qquad k=0,1,2,\ldots.$$

The gradient is evaluated at the current iterate, not at a future point. The minus sign is essential: the gradient points toward local increase, so its negative is the first-order descent direction whenever the gradient is nonzero.

A constant-step method sets $\alpha_k=\alpha$. If $L$ is known, $1/L$ is a common choice. Under the usual smooth-convex assumptions, a constant step in $(0,2/L)$ is also a common safe interval for the basic iteration. These statements are conditional: an unknown or badly estimated curvature scale makes a nominal step unreliable.

### Line searches

Exact line search chooses the positive scalar that minimises the objective along the current negative-gradient ray:

$$\alpha_k=\arg\min_{\alpha>0}f\bigl(x_k-\alpha\nabla f(x_k)\bigr).$$

It can be effective for a quadratic when the one-dimensional minimisation is inexpensive, but solving a line problem at every iteration may cost more than it saves.

Armijo backtracking instead tests a trial $\bar\alpha>0$. With $\eta\in(0,1)$ and $c\in(0,1)$, it tries $\alpha_k=\bar\alpha\eta^m$ and chooses the smallest nonnegative accepted integer $m$ for which

$$f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.$$

The right side requires sufficient decrease relative to the squared gradient norm. Backtracking contracts the trial step until this inequality holds, so it adapts to local curvature without solving the line search exactly.

<!-- section: SEC-04 -->
## What convergence guarantees require

A convergence rate is a conditional statement, not a promise attached to every data set or implementation. For an $L$-smooth convex objective with a global minimiser $x^*$, gradient descent using $\alpha_k=1/L$ satisfies, for $k\geq1$,

$$f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k}.$$

The objective gap therefore has an $O(1/k)$ bound. The hypotheses include smoothness, convexity, existence of a global minimiser, and the specified step size. If strong convexity is available, the behaviour is faster. For an $L$-smooth, $\mu$-strongly convex objective, the distance bound uses

$$\alpha=\frac{2}{L+\mu},\qquad
\|x_k-x^*\|^2\leq\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}\|x_0-x^*\|^2.$$

The objective-gap contraction uses a different step size, $\alpha=1/L$:

$$f(x_k)-f(x^*)\leq\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).$$

Do not transfer the distance rate to $1/L$ or the objective rate to $2/(L+\mu)$. In practice, estimates of $L$ and $\mu$ may be difficult, and the observed curve can be affected by finite precision, stopping rules, or an inaccurate model.

<!-- section: SEC-05 -->
## Momentum and acceleration

### Heavy Ball

Heavy Ball retains a memory of the previous displacement:

$$x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1}),$$

where $\beta\in[0,1)$ and the parameters must keep the iteration stable. The gradient is still evaluated at $x_k$; the extra term is not a look-ahead gradient. Momentum can reduce zig-zagging in a long, narrow quadratic, but excessive momentum can overshoot.

The sharp parameter statement has a narrow scope. For

$$f(x)=\frac12x^TAx,$$

with $A$ symmetric positive definite and spectrum in $[\mu,L]$, the stated optimal parameters are

$$\alpha^*=\frac{4}{(\sqrt L+\sqrt\mu)^2},\qquad
\beta^*=\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^2.$$

The improved condition-number dependence belongs to this quadratic setting; it should not be generalised automatically to an arbitrary nonlinear objective.

### Nesterov acceleration

The specified Nesterov variant uses auxiliary points. Initialise $y_0=x_0$ and $\lambda_0=1$. At iteration $k=0,1,\ldots$, evaluate the gradient at $y_k$:

$$x_{k+1}=y_k-\frac1L\nabla f(y_k),$$
$$\lambda_{k+1}=\frac{1+\sqrt{1+4\lambda_k^2}}2,$$
$$y_{k+1}=x_{k+1}+\frac{\lambda_k-1}{\lambda_{k+1}}(x_{k+1}-x_k).$$

The gradient location and indices are part of the method. For an $L$-smooth convex objective with a global minimiser, this recurrence has

$$f(x_k)-f(x^*)\leq\frac{2L\|x_0-x^*\|^2}{(k+1)^2}=O\left(\frac1{k^2}\right).$$

That rate requires the stated recurrence, convexity, smoothness, and a global minimiser.

<!-- section: SEC-06 -->
## Noisy gradients and adaptive coordinates

### Stochastic gradients

For an empirical objective,

$$f(x)=\frac1N\sum_{i=1}^N f_i(x),$$

a stochastic estimate $g_k(x_k)$ is modelled by conditional unbiasedness and bounded conditional variance:

$$\mathbb E[g_k(x_k)\mid x_k]=\nabla f(x_k),$$
$$\mathbb E[\|g_k(x_k)-\nabla f(x_k)\|^2\mid x_k]\leq\sigma^2.$$

Conditioning on the current iterate matters because the sample and the current state are not treated as unrelated. Stochastic gradient descent uses

$$x_{k+1}=x_k-\eta_k g_k(x_k).$$

With persistent nonzero variance and a small constant step, the usual smooth strongly convex setting generally produces a nonzero error floor rather than exact convergence. Diminishing steps can reduce the noise, but the Robbins–Monro series conditions alone are not sufficient:

$$\sum_{k=1}^{\infty}\eta_k=\infty,\qquad\sum_{k=1}^{\infty}\eta_k^2<\infty.$$

A full convergence theorem also needs appropriate assumptions on the objective, bias, moments, and stability of the iterates.

### Coordinate-wise scaling

Adaptive methods change the scale of each coordinate using gradient history. AdaGrad starts with $v_{-1}=0$ and accumulates element-wise squared gradients:

$$v_k=v_{k-1}+g_k\odot g_k,$$
$$x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k,$$

where $\epsilon>0$. Its cumulative memory can make frequently active coordinates receive progressively smaller steps.

RMSProp replaces cumulative memory with an exponential moving average. With $\gamma\in[0,1)$ and $\epsilon>0$,

$$v_k=\gamma v_{k-1}+(1-\gamma)g_k\odot g_k,$$
$$x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k.$$

Adam maintains both first and second exponential moments, starting both at index $-1$:

$$m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,$$
$$v_k=\beta_2v_{k-1}+(1-\beta_2)(g_k\odot g_k).$$

For $k$ starting at zero, bias correction is

$$\hat m_k=\frac{m_k}{1-\beta_1^{k+1}},\qquad
\hat v_k=\frac{v_k}{1-\beta_2^{k+1}},$$

and the update is

$$x_{k+1}=x_k-\frac{\eta}{\sqrt{\hat v_k}+\epsilon}\odot\hat m_k.$$

Here $\beta_1,\beta_2\in[0,1)$ and $\epsilon>0$. The correction is important at early iterations because the moments begin at zero. These methods alter coordinate scales; they do not remove the need to inspect units, conditioning, stochastic noise, and stopping behaviour in a mechanical model.

<!-- section: SEC-07 -->
## Second-order information and reliable Python updates

### Newton's method

Newton's method uses a second-order Taylor model around the current point. For a step $p$,

$$f(x_k+p)\approx f(x_k)+\nabla f(x_k)^Tp+\frac12p^T\nabla^2f(x_k)p.$$

This is an approximation, not an exact identity for a general objective. Minimising the model gives the linear system

$$\nabla^2f(x_k)p_k=-\nabla f(x_k),\qquad x_{k+1}=x_k+p_k.$$

When the Hessian is invertible, the mathematically equivalent expression is

$$x_{k+1}=x_k-[\nabla^2f(x_k)]^{-1}\nabla f(x_k).$$

A numerical implementation should solve the linear system rather than explicitly forming the inverse. Local quadratic convergence requires stationarity at $x^*$, a positive-definite Hessian there, locally Lipschitz Hessian, and an initial point sufficiently close to $x^*$. It is a local result, not a global guarantee.

### BFGS and implementation checks

BFGS avoids forming a fresh exact Hessian. After a step, define

$$s_k=x_{k+1}-x_k,\qquad y_k=\nabla f(x_{k+1})-\nabla f(x_k).$$

The next Hessian approximation obeys the secant equation $B_{k+1}s_k=y_k$. In inverse-Hessian form, when $y_k^Ts_k>0$, use

$$H_{k+1}=(I-\rho_ks_ky_k^T)H_k(I-\rho_ky_ks_k^T)+\rho_ks_ks_k^T,$$
$$\rho_k=\frac1{y_k^Ts_k}.$$

A suitable line search supports the positive-curvature condition. The search direction is $p_k=-H_k\nabla f(x_k)$, so the negative sign remains part of the descent convention.

In Python, keep the mathematical order visible: evaluate the gradient at the intended point, compute a direction, multiply by a positive step, and subtract. Store vectors as arrays with consistent shapes and avoid replacing a linear solve with an explicit inverse. 

### Choosing a representation

The vector $x$ can represent physical design variables, calibration coefficients, or the state of a reduced simulation. The optimisation mathematics does not depend on the names of those entries, but the model does depend on their scaling. If one coordinate is measured in millimetres and another in radians, their raw numerical magnitudes need not reflect equal physical changes. A gradient component is a rate of change with respect to its own coordinate, so comparing components without considering units can give a misleading picture of which variable deserves attention.

 A large ratio $L/\mu$ means that the objective can be steep in one direction and shallow in another. Gradient descent then tends to make progress in the steep direction while moving slowly in the shallow direction. Adaptive coordinate methods respond to observed gradient history, while second-order methods respond to curvature estimates. Neither choice excuses checking the physical model: a numerically small objective can still represent an unacceptable engineering design if the objective was scaled poorly or omitted an important contribution.

### From a derivative to an iteration

For a one-variable function, the update is familiar: move opposite the slope by a chosen distance. In several variables, the gradient collects all partial derivatives and the same idea becomes a vector subtraction. The step size is a scalar, so it changes the length of the move without changing the direction. This separation is useful when debugging. If the direction is wrong, changing the step size cannot repair the sign. If the direction is correct but the step is too large, a line search or a smaller trial step can help.

The Descent Lemma explains why a curvature scale appears in step selection. The inner-product term in the upper model is negative when we choose $y=x-\alpha\nabla f(x)$. The quadratic term grows with $\alpha^2$. A useful step balances these terms rather than trusting the linear approximation indefinitely. Exact line search performs that balance on one ray; Armijo backtracking tests a sufficient-decrease inequality and is often simpler to combine with a general numerical model.

### Interpreting rates in a computation

The convex $O(1/k)$ statement concerns an objective gap, not necessarily the distance between iterates. Two successive vectors can be close while the objective is still far from its optimum, or the objective can change little while the vectors move through a flat region. Strong convexity links curvature and distance more tightly, which is why a geometric contraction can be stated. When reporting an experiment, identify the measured quantity: objective value, objective gap, gradient norm, or parameter distance.

The constants also matter. A rate containing $L$ and an initial distance may be informative for comparing theoretical regimes even when those quantities are not known exactly in code. It should not be read as a prediction of the iteration count for a particular finite-precision run. A stopping tolerance, noisy function evaluation, line-search failure, or inaccurate gradient can dominate the asymptotic pattern. The theorem remains useful because it tells us which assumptions a diagnostic must investigate when observed behaviour disagrees with expectation.

### Comparing momentum methods

Heavy Ball and Nesterov both use information from earlier iterations, but their recurrences are not interchangeable. Heavy Ball adds a multiple of the previous displacement to a current-gradient step. Nesterov first forms a gradient step from an auxiliary point and then updates that auxiliary point with the specified coefficient. In code, a variable named `lookahead` should therefore be tied to the exact recurrence rather than treated as a generic synonym for momentum.

Acceleration can be valuable for a poorly conditioned quadratic, yet a larger apparent movement is not automatically better. Momentum stores information that can amplify oscillation when the curvature estimate or step size is unsuitable. For this reason, a stable parameter range and the scope of a rate should be documented beside the implementation. A mechanical engineer comparing solvers should record the objective definition, scaling, initial point, stopping rule, and any line search, rather than comparing iteration counts without context.

### Noise, samples, and memory

An empirical objective is an average over component losses. A mini-batch gradient is useful because it estimates the full gradient at lower cost, but its randomness changes what convergence means. Conditional unbiasedness says that, given the current iterate, the average estimate points in the correct direction. The variance bound says that the random error is controlled in mean square. If either property is questionable, the standard stochastic conclusions cannot simply be imported.

The two Robbins–Monro sums illustrate a deliberate compromise. The sum of step sizes must diverge so that the algorithm can continue to travel toward a solution, while the sum of squared step sizes must converge so that accumulated noise is controlled. These arithmetic conditions are necessary ingredients in the stated framework, not a complete theorem. Objective regularity, bias control, moment bounds, and bounded or stable iterates still have to be considered.

AdaGrad, RMSProp, and Adam store different kinds of history. AdaGrad remembers all squared gradients, so its accumulator never forgets an active coordinate. RMSProp forgets gradually through an exponential average, which allows the scale to respond to more recent behaviour. Adam combines a first-moment direction with a second-moment scale and corrects the initial zero bias. In all three cases, the element-wise operations are deliberate: a vector square is not a matrix product, and the small positive $ epsilon$ term prevents a zero denominator in the stated update.

### Curvature in practice

Newton's model uses the Hessian to predict how the gradient changes. Solving the Hessian system can turn a narrow valley into a more direct step, but the system may be expensive or poorly conditioned. Positive definiteness near a solution supports the local result, whereas an indefinite Hessian can point toward a saddle or a direction that does not reduce the objective. A line search or damping strategy may be needed in practical algorithms, but it must not be confused with the undamped update or its local theorem.

BFGS replaces direct Hessian calculation with curvature information collected from successive iterates. The secant equation says that the approximate Hessian maps the observed displacement to the observed gradient change. The positive-curvature condition is therefore not a decorative test: it is the condition that makes the inverse update well defined in the stated form. In software, check the denominator before applying the rank-two formula and preserve the transpose placement. A silent shape or transpose error can produce a symmetric-looking array that nevertheless represents the wrong update.

### A repeatable implementation workflow

Begin with a tiny objective whose gradient can be differentiated by hand. Evaluate the objective and gradient at one known point, apply one update, and compare the result with the hand calculation. Next, test a point close to a known stationary point and inspect whether the objective changes in the expected direction. Only then introduce batches, momentum, adaptive state, or a Hessian approximation. This staged workflow separates a mathematical error from a data-pipeline error.

Keep state initialisation explicit. AdaGrad and RMSProp start their accumulator at index $-1$; Adam starts both moments there and uses the $k+1$ exponents in its correction. Nesterov starts with $y_0=x_0$ and $\lambda_0=1$. Off-by-one changes can be hard to see after many iterations, so a first-iteration test is especially valuable. Likewise, Newton should call a linear solver with the Hessian and negative gradient, while BFGS should update its approximation only after computing both $s_k$ and $y_k$.


<!-- section: SEC-08 -->
## Exercises and worked solutions

<!-- exercise: EX-001 -->
### Exercise 1: Reading theorem scope

A colleague makes four claims. Decide whether each is justified by the results in this lesson.

1. For an $L$-smooth convex objective with a global minimiser and step $1/L$, gradient descent has an $O(1/k)$ objective-gap bound.
2. For an $L$-smooth strongly convex objective, the distance contraction using step $2/(L+\mu)$ can be quoted as the objective-gap contraction using step $1/L$.
3. The stated Nesterov recurrence has an $O(1/k^2)$ objective-gap bound under smoothness, convexity, and a global minimiser.
4. Newton's method is globally quadratically convergent whenever its Hessian is positive definite at the solution.

Explain each decision and name the missing or matching hypothesis where relevant.

<!-- solution: EX-001 -->
### Worked solution

Claim 1 is justified: the convex result has exactly the listed smoothness, convexity, global-minimiser, and step-size assumptions, and gives the objective gap bounded by a constant divided by $k$.

Claim 2 is not justified. The distance contraction is attached to $2/(L+\mu)$, while the objective contraction is attached to $1/L$. Strong convexity is required for both, but the rates cannot be swapped between step sizes.

Claim 3 is justified only for the specified Nesterov initialisation, gradient-at-$y_k$ recurrence, and the stated smooth convex setting. The recurrence is therefore part of the hypothesis, not an implementation detail that can be changed freely.

Claim 4 is false. The Newton result is local and also requires stationarity, locally Lipschitz Hessian, and an initial point sufficiently close to the solution. Positive definiteness at the solution alone does not create a global quadratic guarantee.

<!-- exercise: EX-002 -->
### Exercise 2: One engineering-style gradient step

Consider the unconstrained objective

$$f(x,y)=(x-3)^2+2(y+1)^2.$$

At $(x_0,y_0)=(1,2)$, use step size $\alpha=0.25$. Compute the gradient and perform one standard gradient-descent update. Show the subtraction explicitly and report the updated vector.

<!-- solution: EX-002 -->
### Worked solution

Differentiate component by component:

$$\nabla f(x,y)=\begin{bmatrix}2(x-3)\\4(y+1)\end{bmatrix}.$$

At $(1,2)$ this is $[-4,12]$. The standard update subtracts the positive step-size multiple of the current gradient:

$$\begin{bmatrix}x_1\\y_1\end{bmatrix}=
\begin{bmatrix}1\\2\end{bmatrix}-0.25\begin{bmatrix}-4\\12\end{bmatrix}
=\begin{bmatrix}1+1\\2-3\end{bmatrix}
=\begin{bmatrix}2\\-1\end{bmatrix}.$$

The consistency check is that the point moves toward the stationary point $(3,-1)$ in both coordinates. Thus the checked update is the same vector as the visible derivation.

<!-- derived-answer: EX-002 -->
**Result from the derivation:** `[2, -1]`

<!-- answer: EX-002 -->
**Checked answer:** `[2, -1]`

<!-- exercise: EX-003 -->
### Exercise 3: Diagnose a Python update

The following code is intended to perform one gradient-descent step, but it contains a sign error. Identify the bug and rewrite the function. Then use the corrected function on `x = [1.0, -2.0]`, `gradient = [2.0, -4.0]`, and `alpha = 0.1`.

```python
import json

def buggy_step(x, gradient, alpha):
    return [xi + alpha * gi for xi, gi in zip(x, gradient)]

def corrected_step(x, gradient, alpha):
    return [xi - alpha * gi for xi, gi in zip(x, gradient)]

x = [1.0, -2.0]
gradient = [2.0, -4.0]
print(json.dumps(corrected_step(x, gradient, 0.1)))
```

<!-- solution: EX-003 -->
### Worked solution

The buggy function adds the gradient term. Gradient descent must subtract it, because the gradient points in the direction of local increase. The corrected function uses `xi - alpha * gi`, as shown in the code. It also leaves the input list unchanged and returns a new list, which makes the single-step calculation easy to inspect.

For the first component, $1.0-0.1(2.0)=0.8$. For the second, $-2.0-0.1(-4.0)=-1.6$. The corrected code therefore prints the JSON list shown above. This small test checks both the sign convention and the numerical values without claiming a general convergence result for arbitrary code.

<!-- expected-stdout: EX-003/1 -->
**Expected output:** `"[0.8, -1.6]\n"`

