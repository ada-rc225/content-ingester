# Gradient Descent and Optimisation for Mechanical Engineering

<!-- section: SEC-01 -->
## From equilibrium to an optimisation problem

### A mechanical entry point

In mechanics, an equilibrium configuration is one in which a small admissible displacement does not produce a first-order change in potential energy. That idea gives a useful entry to optimisation. We can imagine a scalar objective $f(x)$ measuring a design cost, residual, or model error, with a vector $x$ collecting design or state variables. A numerical relaxation method changes $x$ repeatedly in an attempt to reduce $f$.

The energy picture is a teaching analogy: an optimisation objective need not be physical energy, and an algorithmic iterate is not automatically a physical time state. The analogy is useful because it suggests looking for low objective values, zero first derivatives, and curvature that describes how sharply the objective bends.

For unconstrained optimisation, the mathematical problem is
$$
\min_{x\in\mathbb{R}^d} f(x).
$$
Here $f$ is continuously differentiable, so its gradient exists and varies continuously. “Unconstrained” means that every vector in $\mathbb{R}^d$ is part of the mathematical search domain. Bounds on a displacement, a stress limit, or a manufacturing restriction would create a different, constrained problem and would require additional ideas.

### Stationarity is necessary, not sufficient

Suppose $x^*$ is a differentiable local minimiser. Moving a small distance in any direction cannot lower the objective to first order. Therefore
$$
\nabla f(x^*)=0.
$$
This is a necessary stationarity condition. It does not say that every stationary point is a minimum: a maximum and a saddle point can also have zero gradient.

When $f$ is twice continuously differentiable, the Hessian adds local curvature information. At a local minimiser, stationarity and a positive-semidefinite Hessian are necessary. For a strict local minimiser, stationarity and a positive-definite Hessian are sufficient. These statements have different logical directions. Positive semidefiniteness does not by itself certify a strict minimum, and positive definiteness is not a license to remove the stationarity condition.

For a two-variable potential-like objective, the Hessian is a $2\times2$ matrix of second derivatives. Its eigenvalues describe principal curvatures. A zero or negative eigenvalue warns that a stationary configuration may be flat or unstable in at least one direction. This is why checking only the norm of a gradient can be misleading: a small gradient locates approximate stationarity, not necessarily the desired type of stationary point.

<!-- exercise: EX-001 -->
### Exercise 1: Check the scope of a convergence theorem

A colleague says: “The objective gap after $k$ gradient-descent steps is always proportional to $1/k$, so the estimate can be used for any nonlinear mechanical design objective.” Give a short correction. State the essential assumptions for the convex $1/k$ objective-gap result, and explain why the strongly convex result uses a different statement and an additional assumption.

<!-- solution: EX-001 -->
### Worked solution 1

The $1/k$ objective-gap estimate requires an $L$-smooth convex objective, a global minimiser $x^*$, and the step choice $\alpha_k=1/L$, with $k\geq1$. It has the form
$$
f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k}.
$$
It is not an unconditional claim about every nonlinear design objective. The strongly convex result assumes both $L$-smoothness and $\mu$-strong convexity. With the specified step sizes, it gives a geometric contraction: the distance result uses $2/(L+\mu)$, whereas the objective-gap result uses $1/L$. Strong convexity supplies a positive curvature lower bound, so the theorem can say more than a sublinear $1/k$ estimate. Independent review is still needed for the conceptual explanation of a particular mechanical model.

<!-- section: SEC-02 -->
## Smoothness, convexity, and conditioning

### Smoothness as a gradient-change bound

An objective is $L$-smooth when its gradient is Lipschitz with respect to the Euclidean norm:
$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|,\qquad\forall x,y\in\mathbb{R}^d.
$$
The constant $L$ limits how rapidly the slope can change. It is not a statement that function values themselves are Lipschitz. For a mechanical interpretation, a large $L$ can represent a direction in which the local force-like gradient changes rapidly, although the objective is still an abstract mathematical quantity.

Smoothness gives the Descent Lemma, a quadratic upper model:
$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle+\frac{L}{2}\|y-x\|^2.
$$
This inequality holds for all $x,y\in\mathbb{R}^d$ when $f$ is $L$-smooth. The linear term predicts the immediate change; the quadratic term controls the error in that prediction. A step that is too large can make the quadratic term dominate the expected decrease.

### Convexity and strong convexity

For a differentiable function, convexity is characterised by the global first-order lower bound
$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle,
$$
for every $x,y\in\mathbb{R}^d$. The tangent plane is therefore a global under-estimator. Convexity means that any local minimiser is global, which is a major reason the theory is attractive for optimisation.

Strong convexity strengthens this lower bound. An objective is $\mu$-strongly convex when $\mu>0$ and
$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle+\frac{\mu}{2}\|y-x\|^2
$$
for all $x,y$. The quadratic term rules out completely flat directions at the scale described by $\mu$. It is a lower curvature bound, not a replacement for smoothness.

For a $C^2$ objective, Hessian bounds express these properties. Under convexity,
$$
0\preceq\nabla^2f(x)\preceq LI,\qquad\forall x,
$$
characterises the relevant smooth convex curvature bounds. Strong convexity is represented by
$$
\nabla^2f(x)\succeq\mu I,\qquad\forall x.
$$
The convexity qualifier matters for the two-sided bound: a positive-semidefinite lower Hessian bound must not be silently detached from its stated setting.

### Conditioning and numerical difficulty

When an objective is both $L$-smooth and $\mu$-strongly convex, its condition number is
$$
\kappa=\frac{L}{\mu}\geq1.
$$
A large $\kappa$ means that the objective has a wide range of curvature scales. A contour plot of a quadratic with large condition number looks like a long, narrow valley. A relaxation step that is safe across the steep direction may move only a small distance along the shallow direction. This is a numerical version of stiffness: the algorithm must accommodate different scales at once.

Conditioning is not the same as physical stiffness, but the comparison helps explain why rescaling variables or changing coordinates can improve an optimisation calculation. Any theorem about a rate still depends on the exact assumptions that accompany it; a visual valley is not itself a proof of smoothness or strong convexity.

<!-- section: SEC-03 -->
## Gradient descent and choosing a step

### The basic update

Gradient descent evaluates the gradient at the current iterate and moves opposite to it:
$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),\qquad k=0,1,2,\ldots.
$$
The initial point $x_0$ lies in $\mathbb{R}^d$, and each step size $\alpha_k$ is positive. The minus sign is essential: the gradient points in the direction of steepest local increase, so its negative is the local descent direction.

The update is a numerical relaxation rule, not a claim about physical time integration. It uses local slope information to propose a new configuration. A stopping test might monitor $\|\nabla f(x_k)\|$, the change in objective value, or the change in $x_k$, but a small value of one diagnostic does not automatically establish all the assumptions of a theorem.

### Fixed, exact, and backtracking choices

A constant-step method sets $\alpha_k=\alpha$. If $L$ is known, $\alpha=1/L$ is a common choice. Under the usual smooth-convex assumptions, another common admissible interval is $\alpha\in(0,2/L)$. The interval must not be quoted without those assumptions.

Exact line search chooses the positive step that minimises the objective along the current negative-gradient ray:
$$
\alpha_k=\arg\min_{\alpha>0}f\bigl(x_k-\alpha\nabla f(x_k)\bigr).
$$
This is an exact one-dimensional minimisation, not merely an acceptance test. It can be expensive, but it illustrates what a step-size rule is trying to achieve.

Armijo backtracking starts with a positive trial step $\bar\alpha$, contracts it by a factor $\eta\in(0,1)$, and accepts the smallest nonnegative integer $m$ for which $\alpha_k=\bar\alpha\eta^m$ satisfies
$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2,
$$
where $c\in(0,1)$. The squared gradient norm appears because the test measures sufficient decrease relative to the current descent direction. In code, evaluate the candidate with the current gradient, test the inequality, and then contract the trial step if it fails.

<!-- exercise: EX-002 -->
### Exercise 2: Relax a quadratic surrogate by hand

Consider
$$
f(x,y)=\frac12(2x^2+2xy+4y^2)-2x.
$$
At $(x_0,y_0)=(2,-1)$, use gradient descent with $\alpha=0.25$. Derive the gradient, calculate one update, and state the new point.

<!-- solution: EX-002 -->
### Worked solution 2

Differentiate the objective:
$$
\nabla f(x,y)=\begin{bmatrix}2x+y-2\\x+4y\end{bmatrix}.
$$
At $(2,-1)$ the gradient is $(1,-2)$. Therefore
$$
\begin{bmatrix}x_1\\y_1\end{bmatrix}
=\begin{bmatrix}2\\-1\end{bmatrix}-0.25\begin{bmatrix}1\\-2\end{bmatrix}
=\begin{bmatrix}1.75\\-0.5\end{bmatrix}.
$$
The supplied objective and gradient are consistent: direct evaluation gives $f(2,-1)=0$ and the gradient $(1,-2)$. The checked coordinate update is $[1.75,-0.5]$.

<!-- answer: EX-002 -->
**Checked answer:** `[1.75, -0.5]`

<!-- section: SEC-04 -->
## What convergence guarantees actually assume

### The smooth convex estimate

If $f$ is $L$-smooth and convex, has a global minimiser $x^*$, and gradient descent uses $\alpha_k=1/L$, then for $k\geq1$,
$$
f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k}.
$$
The objective gap decreases at an $O(1/k)$ rate. The initial distance and the smoothness constant set the scale of the bound. The statement is about an objective gap, not necessarily a direct bound on every coordinate or on physical error.

### The strongly convex estimate

If $f$ is both $L$-smooth and $\mu$-strongly convex, the condition number enters the rates. With
$$
\alpha=\frac{2}{L+\mu},
$$
the squared distance contracts according to
$$
\|x_k-x^*\|^2\leq\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}\|x_0-x^*\|^2.
$$
With the different step size $\alpha=1/L$, the objective gap satisfies
$$
f(x_k)-f(x^*)\leq\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).
$$
Do not attach the distance rate to $1/L$ or the objective rate to $2/(L+\mu). Both results require the strong-convexity assumption, and each rate is tied to its stated step. As $\kappa$ grows, the factor approaches one, reflecting slow progress through a narrow valley.

<!-- section: SEC-05 -->
## Momentum and acceleration

### Heavy Ball

Heavy Ball adds a memory term to the current gradient step:
$$
x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1}),
$$
where $\beta\in[0,1)$ and the parameters must keep the iteration stable. The difference of recent iterates carries directional memory. It is not a look-ahead gradient evaluation, so it should not be conflated with NAG.

For the quadratic
$$
f(x)=\frac12x^TAx,
$$
where $A$ is symmetric positive definite with spectrum in $[\mu,L]$, the stated optimal parameters are
$$
\alpha^*=\frac{4}{(\sqrt L+\sqrt\mu)^2},\qquad
\beta^*=\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^2.
$$
The improved condition-number dependence belongs specifically to this quadratic setting. It must not be generalised to arbitrary nonlinear objectives without a separate result.

### The specified NAG recurrence

The NAG variant here starts with $y_0=x_0$ and $\lambda_0=1$. At iteration $k=0,1,2,\ldots$, it evaluates the gradient at $y_k$:
$$
x_{k+1}=y_k-\frac1L\nabla f(y_k),
$$
then updates
$$
\lambda_{k+1}=\frac{1+\sqrt{1+4\lambda_k^2}}2,
$$
and
$$
y_{k+1}=x_{k+1}+\frac{\lambda_k-1}{\lambda_{k+1}}(x_{k+1}-x_k).
$$
The index placement is part of the algorithm. Evaluating at $x_k$ instead of $y_k$, or shifting the coefficient by one index, produces a different recurrence.

For an $L$-smooth convex objective with a global minimiser, this parameterisation has
$$
f(x_k)-f(x^*)\leq\frac{2L\|x_0-x^*\|^2}{(k+1)^2}=O\left(\frac1{k^2}\right).
$$
The rate requires convexity, smoothness, a global minimiser, and exactly the recurrence just stated. Momentum can be effective, but it also makes indexing and stability more important.

<!-- section: SEC-06 -->
## Stochastic and adaptive updates

### Stochastic gradients

For an empirical objective,
$$
f(x)=\frac1N\sum_{i=1}^Nf_i(x),
$$
the stochastic model assumes conditional unbiasedness and bounded conditional variance:
$$
\mathbb E[g_k(x_k)\mid x_k]=\nabla f(x_k),
$$
$$
\mathbb E\left[\|g_k(x_k)-\nabla f(x_k)\|^2\mid x_k\right]\leq\sigma^2.
$$
The conditioning is on the current iterate. This says that the random estimate is correct on average, while individual samples fluctuate.

SGD uses
$$
x_{k+1}=x_k-\eta_kg_k(x_k).
$$
With persistent nonzero variance and a small constant step, the usual smooth strongly convex example generally approaches a nonzero error floor rather than converging exactly. Diminishing steps can reduce noise, but the Robbins–Monro series conditions
$$
\sum_{k=1}^{\infty}\eta_k=\infty,\qquad
\sum_{k=1}^{\infty}\eta_k^2<\infty
$$
are not sufficient alone. A complete theorem also needs suitable assumptions on the objective, bias, moments, and iterate stability.

### Adaptive scaling

AdaGrad starts with $v_{-1}=0$, accumulates element-wise squared gradients, and updates
$$
v_k=v_{k-1}+g_k\odot g_k,
$$
$$
x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k,
$$
where $\epsilon>0$. Because the accumulator grows, repeatedly active coordinates are progressively scaled down. This is cumulative accumulation, not exponential averaging.

RMSProp also starts with $v_{-1}=0$, but uses an exponential moving average:
$$
v_k=\gamma v_{k-1}+(1-\gamma)g_k\odot g_k,
$$
$$
x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k,
$$
with $\gamma\in[0,1)$ and $\epsilon>0$. The $(1-\gamma)$ factor is essential.

Adam keeps two moments, both initialised at index $-1$:
$$
m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,
$$
$$
v_k=\beta_2v_{k-1}+(1-\beta_2)(g_k\odot g_k).
$$
For $k$ starting at zero, it corrects the initial bias using
$$
\hat m_k=\frac{m_k}{1-\beta_1^{k+1}},\qquad
\hat v_k=\frac{v_k}{1-\beta_2^{k+1}},
$$
and applies
$$
x_{k+1}=x_k-\frac{\eta}{\sqrt{\hat v_k}+\epsilon}\odot\hat m_k.
$$
The $k+1$ exponents, bias correction, positive $\epsilon$, and element-wise operations are implementation details with mathematical consequences.

<!-- section: SEC-07 -->
## Newton and quasi-Newton methods

### A local second-order model

Newton's method begins with the second-order Taylor model around $x_k$:
$$
f(x_k+p)\approx f(x_k)+\nabla f(x_k)^Tp+\frac12p^T\nabla^2f(x_k)p.
$$
The approximation is in the step $p$; it is not an exact identity for a general objective. Minimising this local quadratic model leads to the linear system
$$
\nabla^2f(x_k)p_k=-\nabla f(x_k),
$$
and then
$$
x_{k+1}=x_k+p_k.
$$
Although the equivalent inverse expression is
$$
x_{k+1}=x_k-[\nabla^2f(x_k)]^{-1}\nabla f(x_k),
$$
that form requires an invertible Hessian and should not be implemented by explicitly forming the inverse. A numerical implementation should solve the linear system. This is generally more stable and avoids unnecessary work.

Under stationarity at $x^*$, a positive-definite Hessian there, locally Lipschitz Hessian, and an initial point sufficiently close to $x^*$, Newton iterates converge locally quadratically:
$$
\|x_{k+1}-x^*\|\leq C\|x_k-x^*\|^2.
$$
“Locally” and “sufficiently close” are essential. The result is not a global quadratic-convergence claim, and an indefinite or singular Hessian can require different safeguards.

### BFGS learns curvature

Quasi-Newton methods avoid recomputing an exact Hessian. Define
$$
s_k=x_{k+1}-x_k,\qquad y_k=\nabla f(x_{k+1})-\nabla f(x_k).
$$
The next Hessian approximation satisfies the secant equation
$$
B_{k+1}s_k=y_k.
$$
For inverse-Hessian BFGS, when $y_k^Ts_k>0$, define $\rho_k=1/(y_k^Ts_k)$ and update
$$
H_{k+1}=(I-\rho_ks_ky_k^T)H_k(I-\rho_ky_ks_k^T)+\rho_ks_ks_k^T.
$$
The search direction is $p_k=-H_k\nabla f(x_k)$, and a suitable line search supports the curvature condition. The transpose placement and the negative direction matter. BFGS is therefore not simply “Newton with a cheaper matrix”: it is a curvature-learning update with its own state and conditions.

### Choosing a method for a model

The assumptions provide a useful decision map. If only first derivatives are cheap and the objective is large, standard GD gives the clearest baseline. If $L$ is known or can be estimated, a fixed step provides a reproducible reference. If the scale is uncertain, exact line search or Armijo backtracking makes the step respond to the current objective, although each choice adds computation. These are algorithmic choices, not claims about how a real component relaxes in time.

If the problem is convex but not strongly convex, the smooth-convex bound gives a sublinear objective-gap guarantee. If a positive lower curvature bound is justified, strong convexity explains a geometric rate and makes the condition number meaningful. In either case, the phrase “justified” matters: a numerical plot or a plausible physical interpretation does not establish the required global inequalities.

Momentum changes the state of the algorithm. Heavy Ball stores a previous iterate, while the stated NAG method stores both $x_k$ and $y_k$ and updates $\lambda_k$. This extra state can improve a theoretical rate in the stated settings, but it also creates more opportunities for an off-by-one error. Stochastic and adaptive methods add yet another layer of state: a sampled gradient, an accumulator, or one or two moment estimates. A short implementation is not necessarily a simple implementation.

Newton and BFGS trade memory or derivative work for curvature information. Newton uses the Hessian at the current point and solves a linear system. BFGS uses observed changes in iterates and gradients to impose a secant relation on an approximation. Their attractive local behaviour should be read with the corresponding conditions beside it: Newton's quadratic result is local, and BFGS requires positive curvature and a suitable line search for the stated update. This prevents a common mistake in engineering computation, namely selecting a method from its best-case slogan while ignoring the model and initialisation that make the result applicable.

For a practical workflow, first write down the objective and the variables. Next identify which derivatives and constants are available. Then record the exact update, initial state, and stopping quantities before coding. During a run, retain enough information to inspect objective values, gradient norms, and step lengths. If a result looks surprising, test a small known objective where the gradient and update can be calculated by hand. Such a test separates a mathematical modelling issue from an indexing or sign error.

<!-- section: SEC-08 -->
## Turning update rules into reliable Python

A trustworthy implementation mirrors the mathematics visibly. Store the current iterate, calculate the gradient at the point named by the update rule, and apply the negative sign before changing the iterate. For methods with memory, initialise every state variable at the specified index and update it in the stated order. Use element-wise operations for adaptive methods. For Newton, call a linear solver rather than constructing an inverse.

When diagnosing a loop, check four questions: Which point was used for the gradient? Is the sign descending? Are old and new state variables kept separate? Are the denominators, accumulators, and index exponents exactly the ones in the rule? Plotting an objective history can help, but an apparently decreasing history does not prove that an implementation matches the intended algorithm.

<!-- exercise: EX-003 -->
### Exercise 3: Diagnose a NumPy update

The following corrected loop is intended to perform standard gradient descent on $f(x)=\tfrac12\|x\|^2$. Explain which two changes would be needed if a draft instead used the gradient at `x_new` and added the gradient. Then run the corrected code and report the final iterate.

```python
import numpy as np

def gradient(x):
    return x

x = np.array([2.0, -1.0])
alpha = 0.25
for _ in range(4):
    g = gradient(x)
    x = x - alpha * g
print(np.round(x, 6))
```

<!-- solution: EX-003 -->
### Worked solution 3

Standard gradient descent evaluates $\nabla f$ at the current iterate and subtracts a positive multiple. Thus the draft must replace `gradient(x_new)` with `gradient(x)` and replace addition by subtraction. The corrected loop starts at $(2,-1)$ and multiplies the vector by $1-0.25=0.75$ at every iteration. After four steps,
$$
x_4=0.75^4(2,-1)=(0.6328125,-0.31640625).
$$
The code prints the rounded vector `[0.632812, -0.316406]`. The diagnostic also illustrates why a code review should inspect evaluation point and sign independently: a look-ahead evaluation belongs to a different method, while a plus sign is ascent for this objective.

```python
import numpy as np

def gradient(x):
    return x

x = np.array([2.0, -1.0])
alpha = 0.25
for _ in range(4):
    g = gradient(x)
    x = x - alpha * g
print(np.round(x, 6))
```
