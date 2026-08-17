# Gradient descent and optimisation for mechanical engineering

<!-- section: SEC-01 -->
## From potential energy to an optimisation problem

### Equilibrium as an entry point

A useful first picture is a mechanical system settling toward a low potential-energy configuration. If a configuration is represented by $x\in\mathbb{R}^d$ and its modelled potential energy by $f(x)$, then looking for a resting configuration can look like finding a low value of $f$. This is an analogy, not an identity: real equilibrium may involve constraints, dynamics, contact, and modelling uncertainty. Here we return to the canonical mathematical problem of unconstrained optimisation:

$$\min_{x\in\mathbb{R}^d} f(x),$$

where $f:\mathbb{R}^d\to\mathbb{R}$ is continuously differentiable. The word *unconstrained* matters: every vector in $\mathbb{R}^d$ is an allowed candidate. Later engineering models may require a different problem setting when they impose bounds or compatibility conditions.

Numerical relaxation is a practical mental model. Begin from a trial configuration, inspect how the objective changes locally, and move in a direction predicted to reduce it. The objective need not literally be energy: it might be a design loss or a calibration mismatch. The same canonical formulation remains the guide.

### Stationarity is a test, not a verdict

At a differentiable local minimizer $x^*$, the gradient vanishes:

$$\nabla f(x^*)=0.$$

This is a necessary condition when $x^*$ is a local minimizer and $f$ is differentiable at $x^*$. It resembles zero net generalized force in the energy picture, but zero gradient alone does not establish a minimum. A stationary point can be a maximum or another non-minimizing configuration.

When $f$ is twice continuously differentiable, curvature adds a second test. At a local minimizer, stationarity together with a positive-semidefinite Hessian is necessary. In contrast, stationarity together with a positive-definite Hessian is sufficient for a strict local minimizer. Positive semidefinite and positive definite are therefore not interchangeable: the first condition belongs to a necessary test, while the second gives the stated strict local conclusion.

<!-- section: SEC-02 -->
## Landscape geometry: smoothness and curvature

### Smooth changes and a usable upper bound

An objective is $L$-smooth when its gradient is $L$-Lipschitz in the Euclidean norm:

$$\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|,\qquad \forall x,y\in\mathbb{R}^d,$$

with $L>0$. This controls how quickly the gradient can change as a trial configuration changes. It is a condition on the gradient, not a claim that function values themselves are Lipschitz.

Smoothness yields the Descent Lemma. For every $x,y\in\mathbb{R}^d$,

$$f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle+\frac{L}{2}\|y-x\|^2.$$

The inequality is a quadratic upper bound. In relaxation language, the linear gradient prediction is accompanied by a curvature allowance. It is precisely this allowance that explains why a step length should be chosen with care.

### Bowls, curvature, and conditioning

Differentiable convexity has the global first-order lower bound

$$f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle,\qquad \forall x,y\in\mathbb{R}^d.$$

Strong convexity adds a positive quadratic term:

$$f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle+\frac{\mu}{2}\|y-x\|^2,$$

for every $x,y\in\mathbb{R}^d$ and $
\mu>0$. The additional term rules out a completely flat direction in this global inequality. It is often pictured as a bowl, but the mathematical formulation is the inequality above.

For a $C^2$ objective, Hessian bounds express these ideas. Smooth convexity is characterized by

$$0\preceq\nabla^2 f(x)\preceq LI,\qquad \forall x,$$

where the lower positive-semidefinite bound uses the convexity qualifier. Strong convexity is characterized by

$$\nabla^2 f(x)\succeq\mu I,\qquad \forall x.$$

If an objective is both $L$-smooth and $\mu$-strongly convex, its condition number is

$$\kappa=\frac{L}{\mu}\geq 1.$$

A large ratio signals uneven curvature in this description: one direction can require a much more cautious step than another. This helps explain why a simple relaxation may progress slowly in some problems.

### Reading the geometry before choosing a method

It is helpful to separate three questions that are easily mixed together. First, is a point locally stationary? The gradient test addresses that question. Second, what curvature is present nearby? The Hessian tests and the smoothness bound describe that. Third, is the landscape globally well behaved enough for a global convergence statement? Convexity and strong convexity address this third question through inequalities that hold for every pair of points. A numerical trace that appears to settle answers none of these questions by itself.

For a multi-coordinate mechanical model, coordinates can have different units or physical meanings before nondimensionalisation. The Euclidean norm and the constants $L$ and $\mu$ belong to the mathematical model being optimised. Consequently, a reported condition number describes that chosen formulation. It is useful for reasoning about the stated algorithms, but it should not be casually read as a direct measurement of the condition of an entire physical machine.

<!-- section: SEC-03 -->
## Gradient descent as numerical relaxation

### The current-gradient rule

Gradient descent uses the gradient at the current iterate and subtracts a positive multiple:

$$x_{k+1}=x_k-\alpha_k\nabla f(x_k),\qquad k=0,1,2,\ldots.$$

Here $x_0\in\mathbb{R}^d$ and $\alpha_k>0$. The negative sign is essential: $\nabla f(x_k)$ points locally uphill, so its negative is the local descent direction. Standard gradient descent does not evaluate the gradient at a future or look-ahead iterate. For a potential-energy interpretation, this is an iterative numerical procedure, not a time-accurate dynamics simulation.

A constant-step version takes $\alpha_k=\alpha$. When $L$ is known, a common choice is $\alpha=1/L$; under the usual smooth-convex assumptions, common constant steps also include $\alpha\in(0,2/L)$. The assumptions belong to that interval statement, so it is not a universal stability range.

### Searching for a step

Rather than fix a step, exact line search chooses the positive length that minimizes the objective along the negative *current*-gradient direction:

$$\alpha_k=\arg\min_{\alpha>0}f\bigl(x_k-\alpha\nabla f(x_k)\bigr).$$

It is an exact minimisation over positive $\alpha$, not merely a test that a trial step reduces the objective.

Armijo backtracking instead begins with a positive trial step $\bar\alpha$, contracts it by $\eta^m$, and takes the smallest nonnegative integer $m$ for which the selected $\alpha_k=\eta^m\bar\alpha$ satisfies

$$f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.$$

The parameters obey $\bar\alpha>0$, $\eta\in(0,1)$, and $c\in(0,1)$. The squared gradient norm and the direction of this sufficient-decrease inequality are part of the rule.

### An iteration is a sequence of decisions

When implementing gradient descent, record which quantity is evaluated first. At iteration $k$, form the gradient from $x_k$, choose the step rule, and then construct $x_{k+1}$. This order makes it easier to audit a script: a gradient stored after the state has already been overwritten may correspond to a different iterate. A constant step, exact line search, and backtracking all retain the same negative current-gradient direction; they differ in how the positive scalar is selected.

The potential-energy picture also suggests a useful diagnostic habit. Compare objective values across iterates, but do not use a decrease observed in one run as a replacement for the hypotheses of a theorem. A step can be numerically small because the gradient is small, because the selected step is small, or because the model has a direction of difficult curvature. The formulas above distinguish these possibilities more clearly than a plot alone.

<!-- section: SEC-04 -->
## What convergence guarantees actually say

### Convex objectives

Convergence statements are conditional tools, not promises that every numerical relaxation succeeds. Suppose $f$ is $L$-smooth and convex, has a global minimizer $x^*$, and gradient descent uses $\alpha_k=1/L$. For $k\geq1$,

$$f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k}.$$

This is an objective-gap bound. It says how the stated gap is bounded under all of those hypotheses; removing convexity, the global minimizer, smoothness, or the specified step changes the scope.

### Strongly convex objectives

If $f$ is $L$-smooth and $\mu$-strongly convex, two related but distinct contractions are available. With

$$\alpha=\frac{2}{L+\mu},$$

one has the distance bound

$$\|x_k-x^*\|^2\leq\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}\|x_0-x^*\|^2.$$

With the different step $\alpha=1/L$, one has the objective-gap bound

$$f(x_k)-f(x^*)\leq\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).$$

Do not attach either formula to the other step size. Mechanically, unequal curvature can make a first-order relaxation feel slow; mathematically, the bounds state the dependence through $L$, $\mu$, and $\kappa$.

<!-- section: SEC-05 -->
## Momentum and accelerated first-order methods

### Heavy Ball momentum

Heavy Ball retains a difference between the two most recent iterates:

$$x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1}).$$

The gradient remains at $x_k$, $\beta\in[0,1)$, and the parameters must keep the iteration stable. The extra term can be compared with carry-over in a relaxation process, but it is an update rule rather than a physical mass-and-damper model.

For the specific quadratic

$$f(x)=\frac{1}{2}x^TAx,$$

with $A$ symmetric positive definite and spectrum in $[\mu,L]$, the stated optimal parameters are

$$\alpha^*=\frac{4}{(\sqrt{L}+\sqrt{\mu})^2},\qquad
\beta^*=\left(\frac{\sqrt{\kappa}-1}{\sqrt{\kappa}+1}\right)^2.$$

The improved condition-number dependence belongs specifically to this quadratic, spectral setting. It is not a parameter guarantee for an arbitrary nonlinear engineering objective.

### A look-ahead recurrence

A stated Nesterov accelerated gradient parameterisation begins with $y_0=x_0$ and $\lambda_0=1$. For $k$ starting at zero,

$$x_{k+1}=y_k-\frac{1}{L}\nabla f(y_k),$$

$$\lambda_{k+1}=\frac{1+\sqrt{1+4\lambda_k^2}}{2},$$

$$y_{k+1}=x_{k+1}+\frac{\lambda_k-1}{\lambda_{k+1}}(x_{k+1}-x_k).$$

Unlike standard gradient descent and Heavy Ball above, this recurrence evaluates its gradient at $y_k$. For an $L$-smooth convex objective with a global minimizer, this exact parameterisation satisfies

$$f(x_k)-f(x^*)\leq\frac{2L\|x_0-x^*\|^2}{(k+1)^2}=O\left(\frac{1}{k^2}\right).$$

The recurrence and convex, smooth, globally minimized setting travel together with this rate.

<!-- section: SEC-06 -->
## Stochastic and second-order directions

### When the gradient is estimated

For an empirical objective,

$$f(x)=\frac{1}{N}\sum_{i=1}^N f_i(x),$$

a stochastic estimate $g_k(x_k)$ is modelled with conditional unbiasedness and bounded conditional variance:

$$\mathbb{E}[g_k(x_k)\mid x_k]=\nabla f(x_k),$$

$$\mathbb{E}\left[\|g_k(x_k)-\nabla f(x_k)\|^2\mid x_k\right]\leq\sigma^2.$$

The conditioning on $x_k$ and the variance bound are part of the model. Stochastic gradient descent then uses

$$x_{k+1}=x_k-\eta_k g_k(x_k).$$

With persistent nonzero variance and a small constant step, the standard smooth strongly convex setting generally produces a nonzero error floor rather than exact convergence. A noisy measurement-based objective can motivate this setting, but the equations define the method.

Diminishing steps are often organised by the Robbins--Monro conditions

$$\sum_{k=1}^{\infty}\eta_k=\infty,\qquad \sum_{k=1}^{\infty}\eta_k^2<\infty.$$

These two series conditions are not sufficient by themselves for convergence: a theorem also needs objective, bias, moment, and iterate-stability assumptions.

### Curvature in a second-order model

Newton's method begins with the second-order Taylor approximation around $x_k$:

$$f(x_k+p)\approx f(x_k)+\nabla f(x_k)^Tp+\frac{1}{2}p^T\nabla^2f(x_k)p.$$

This is an approximation in $p$, not a general exact identity. The Newton step solves

$$\nabla^2f(x_k)p_k=-\nabla f(x_k),\qquad x_{k+1}=x_k+p_k.$$

When the Hessian is invertible, the mathematical equivalent is $x_{k+1}=x_k-[\nabla^2f(x_k)]^{-1}\nabla f(x_k)$. In an implementation, solve the linear system rather than explicitly form the inverse.

Newton iterates converge locally quadratically when $\nabla f(x^*)=0$, the Hessian at $x^*$ is positive definite, the Hessian is locally Lipschitz, and $x_0$ is sufficiently close to $x^*$. Under those conditions,

$$\|x_{k+1}-x^*\|\leq C\|x_k-x^*\|^2.$$

This is a local statement, not a global quadratic-convergence claim.

### Choosing the level of model detail

First-order methods request gradients. Their attraction is that one update has a simple form, and smoothness or convexity can be used to state precise scopes for their behaviour. Momentum changes the recurrence by retaining iterates; accelerated gradient changes where the gradient is evaluated. These differences are algorithmic, so similar-looking code should not be assumed to represent the same method.

Stochastic methods change another part of the calculation: the vector replacing the exact gradient is an estimate. Conditional unbiasedness says what that estimate averages to once the current iterate is fixed; bounded conditional variance quantifies a stated fluctuation model. Neither condition says that a particular sampled step is downhill. This is why constant-step stochastic behaviour and deterministic gradient-descent convergence should not be conflated.

Second-order information adds a local curvature model and requires solving a Hessian linear system. Near a point satisfying the listed conditions, the local quadratic conclusion can be very powerful. Away from that neighbourhood, the Taylor expression is still an approximation rather than a certificate of global behaviour. The practical progression is therefore to state the objective and assumptions, select the update whose information is available, and interpret observed iterations through the scope of its corresponding result.

<!-- section: SEC-07 -->
## Exercises and worked solutions

<!-- exercise: EX-001 -->
### Exercise 1: equilibrium checks

A two-coordinate potential-energy model is twice continuously differentiable. A candidate configuration has zero gradient and a positive-semidefinite Hessian. What can be concluded? Can it be declared a strict local minimizer from these facts alone? State the additional curvature condition that gives the stated strict local conclusion.

<!-- solution: EX-001 -->
### Worked solution 1

Zero gradient and a positive-semidefinite Hessian are necessary conditions at a local minimizer for a twice continuously differentiable objective. They do not by themselves establish a strict local minimum. The stated sufficient test for a strict local minimizer is stationarity together with a positive-definite Hessian.

<!-- exercise: EX-002 -->
### Exercise 2: one relaxation update

For the generated two-coordinate energy $f(u,v)=u^2+v^2$, start at $x_0=(u_0,v_0)=(1,-2)$ and use the positive step $\alpha_0=0.25$. Compute $\nabla f(x_0)$ and then one gradient-descent update.

<!-- solution: EX-002 -->
### Worked solution 2

The gradient is $\nabla f(u,v)=(2u,2v)$, so $\nabla f(x_0)=(2,-4)$. Applying the current-gradient rule gives

$$x_1=(1,-2)-0.25(2,-4)=(0.5,-1).$$

<!-- answer: EX-002 -->
**Checked answer:** `[0.5, -1.0]`

<!-- exercise: EX-003 -->
### Exercise 3: diagnose a relaxation script

The scalar objective is $f(q)=q^2$. A classmate writes a gradient-descent step with $q_0=3$ and $\alpha=0.25$. Identify the required correction if the script is to use the gradient at the current iterate and subtract a positive step times that gradient. Then run the corrected version and report $q_1$.

<!-- solution: EX-003 -->
### Worked solution 3

The gradient is $2q$. The update must subtract $\alpha(2q)$ evaluated at the current value of `q`; it should not add the gradient or evaluate it after changing `q`. The corrected script produces $q_1=1.5$.

```python
q = 3.0
alpha = 0.25
gradient = 2.0 * q
q_next = q - alpha * gradient
assert q_next == 1.5
print(q_next)
```
