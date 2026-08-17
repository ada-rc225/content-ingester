# Gradient Descent and Optimisation

## 1. Why optimisation matters in mechanical engineering

Many mechanical-engineering tasks can be expressed as choosing a vector of design or model parameters to minimise a scalar objective. The vector might contain beam dimensions, material parameters, controller gains, or coefficients in a reduced-order model. The objective might measure mass, deflection error, energy, or a weighted combination of several requirements. In the unconstrained mathematical model, the problem is

$$
\min_{x\in\mathbb{R}^d} f(x).
$$

Here, $x$ is the vector being designed and $f(x)$ is a differentiable objective. Optimisation methods generate a sequence of estimates $x_0,x_1,\ldots$ by evaluating the objective and, usually, its derivatives. The result is not automatically a global design: the assumptions about $f$, the initial point, and the update rule determine what can be guaranteed.

A stationary point satisfies $\nabla f(x^*)=0$. For a differentiable objective, this is a first-order necessary condition for a local minimum. It is not sufficient: a stationary point can be a maximum or a saddle point. If $f$ is twice continuously differentiable, a local minimiser must also satisfy

$$
\nabla^2 f(x^*)\succeq 0,
$$

meaning that the Hessian is positive semidefinite. The second-order sufficient condition is stronger. If

$$
\nabla f(x^*)=0\quad\text{and}\quad\nabla^2f(x^*)\succ0,
$$

then $x^*$ is a strict local minimiser. Physically, the gradient says that no infinitesimal direction improves the design, while a positive-definite Hessian says that the local surface curves upwards in every nonzero direction. The sufficient condition does not claim that every local minimum is strictly curved; a flat direction can occur at a minimum.

## 2. Smoothness, convexity, and curvature

A function has an $L$-Lipschitz continuous gradient, or is $L$-smooth, when

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|\quad\text{for all }x,y.
$$

Smoothness limits how rapidly the slope can change. For a $C^2$ function, it is characterised by $\|\nabla^2f(x)\|_2\leq L$. The associated descent lemma gives a quadratic upper model:

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle+\frac{L}{2}\|y-x\|^2.
$$

The linear term predicts the change using the current gradient; the quadratic term protects against curvature that the linear prediction misses. For a mechanical model, $L$ can be viewed as a worst-case curvature scale over the region under consideration.

A differentiable function is convex when its graph lies above every tangent plane:

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle.
$$

Every local minimiser of a convex function is global. If $f$ is differentiable and convex, $\nabla f(x^*)=0$ is therefore enough to identify a global minimiser, although the minimiser need not be unique.

Strong convexity adds a uniform quadratic curvature term. A function is $\mu$-strongly convex when

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle+\frac{\mu}{2}\|y-x\|^2,
$$

for some $\mu>0$. If $f$ is $C^2$, this is equivalent to $\nabla^2f(x)\succeq\mu I$. For a convex $C^2$ function, smoothness and convexity together can be written as

$$
0\preceq\nabla^2f(x)\preceq LI.
$$

When both $L$-smoothness and $\mu$-strong convexity hold, the condition number is $\kappa=L/\mu$. A large $\kappa$ describes an elongated objective valley: gradients point partly across the valley, where a safe step is small, even though progress along the long direction is slow. This is familiar in stiffness and parameter-fitting problems with quantities on very different scales.

## 3. Gradient descent and choosing a step

Gradient descent moves opposite to the gradient:

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k).
$$

The negative gradient is the direction of steepest local decrease in the Euclidean norm. The step size $\alpha_k$ converts that direction into a physical or parameter displacement. A step that is too small is safe but inefficient; a step that is too large can overshoot or diverge.

If $L$ is known, $\alpha=1/L$ is a standard choice. Under the usual smooth convex setting, constant steps in $(0,2/L)$ are also associated with descent behaviour, with the precise guarantee depending on the theorem and objective assumptions. The descent lemma explains the scale: substituting $y=x-\alpha\nabla f(x)$ gives

$$
f(x-\alpha\nabla f(x))\leq f(x)-\left(\alpha-\frac{L\alpha^2}{2}\right)\|\nabla f(x)\|^2.
$$

Thus a sufficiently conservative step makes the bracket positive.

Exact line search chooses the best step along the current descent ray:

$$
\alpha_k=\arg\min_{\alpha>0}f\bigl(x_k-\alpha\nabla f(x_k)\bigr).
$$

It can be attractive for a cheap one-dimensional minimisation, but it may require many objective evaluations and is not always worth its cost. Armijo backtracking is more practical when a reliable $L$ is unavailable. Start with a trial $\bar\alpha$, choose $\eta\in(0,1)$ and $c\in(0,1)$, and repeatedly replace $\alpha$ by $\eta\alpha$ until

$$
f(x_k-\alpha\nabla f(x_k))\leq f(x_k)-c\alpha\|\nabla f(x_k)\|^2.
$$

The right side requires a sufficient decrease relative to the linear prediction. Backtracking usually accepts a large step when the local surface is gentle and shrinks it near high curvature. In implementation, the objective must be evaluated at the trial point, not at the current point by mistake.

## 4. What convergence means

For an $L$-smooth convex objective with global minimiser $x^*$, gradient descent with $\alpha=1/L$ satisfies

$$
f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k},\qquad k\geq1.
$$

This is an $O(1/k)$ objective-gap rate. A proof applies the descent lemma, uses convexity to bound the objective gap by a gradient inner product, and rearranges the result into a telescoping difference of squared distances. Summing the inequalities makes all intermediate distances cancel. The rate is sublinear: reducing the error by another fixed factor takes progressively more iterations.

Strong convexity gives a sharper result. With $\alpha=1/L$,

$$
f(x_k)-f(x^*)\leq\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).
$$

This is linear, or geometric, convergence. The error is multiplied by a fixed factor below one at every iteration. An alternative step $\alpha=2/(L+\mu)$ gives the distance estimate

$$
\|x_k-x^*\|^2\leq\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}\|x_0-x^*\|^2.
$$

These results require their stated assumptions. Without convexity, gradient descent may approach a stationary point rather than a global minimiser; without smoothness, the displayed step-size guarantees do not follow. Poor conditioning also makes even a valid method appear slow.

## 5. Momentum and acceleration

Momentum uses recent motion as well as the current gradient. Polyak's Heavy Ball update is

$$
x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1}),
$$

where $\beta\in[0,1)$. The second term carries velocity through a shallow part of a valley, while the gradient term corrects the direction. Momentum can overshoot when parameters are poorly chosen, so stability is not automatic.

For the strongly convex quadratic $f(x)=\tfrac12x^TAx$, with symmetric positive-definite $A$ whose eigenvalues lie in $[\mu,L]$, the specialised choices

$$
\alpha^*=\frac{4}{(\sqrt L+\sqrt\mu)^2},\qquad
\beta^*=\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^2
$$

improve the condition-number dependence from $1-O(1/\kappa)$ to $1-O(1/\sqrt\kappa)$. These parameter claims are for that quadratic setting, not a universal recipe for every nonlinear engineering objective.

Nesterov's accelerated gradient method uses a look-ahead point. Set $y_0=x_0$ and $\lambda_0=1$, then compute

$$
x_{k+1}=y_k-\frac1L\nabla f(y_k),
$$

$$
\lambda_{k+1}=\frac{1+\sqrt{1+4\lambda_k^2}}2,
$$

$$
y_{k+1}=x_{k+1}+\frac{\lambda_k-1}{\lambda_{k+1}}(x_{k+1}-x_k).
$$

The gradient is evaluated at $y_k$, not at $x_k$. For an $L$-smooth convex function with a global minimiser, this parameterisation has

$$
f(x_k)-f(x^*)\leq\frac{2L\|x_0-x^*\|^2}{(k+1)^2},
$$

an $O(1/k^2)$ rate. The faster bound comes with greater sensitivity to implementation details and assumptions.

## 6. Stochastic and adaptive methods

For a large empirical objective,

$$
f(x)=\frac1N\sum_{i=1}^Nf_i(x),
$$

computing the full gradient costs $O(N)$ evaluations. Stochastic gradient descent uses an estimate $g_k(x_k)$ and updates

$$
x_{k+1}=x_k-\eta_kg_k(x_k).
$$

A common assumption is conditional unbiasedness,

$$
\mathbb E[g_k(x_k)\mid x_k]=\nabla f(x_k),
$$

with bounded conditional variance,

$$
\mathbb E[\|g_k(x_k)-\nabla f(x_k)\|^2\mid x_k]\leq\sigma^2.
$$

The batch gradient is cheaper but noisy. With persistent nonzero variance, a small constant step generally reaches an error neighbourhood rather than exact convergence; its size depends on the step and noise level. Diminishing steps used in Robbins--Monro results obey

$$
\sum_{k=1}^{\infty}\eta_k=\infty,\qquad
\sum_{k=1}^{\infty}\eta_k^2<\infty.
$$

The two conditions mean that learning continues indefinitely but accumulated squared noise remains controlled. They are not sufficient alone: objective regularity, bias and moment assumptions, and stability of the iterates must also be specified.

Adaptive methods rescale each coordinate using recent gradient history. With element-wise multiplication denoted by $\odot$ and $\epsilon>0$ preventing division by zero, AdaGrad accumulates all squared gradients:

$$
v_k=v_{k-1}+g_k\odot g_k,
$$

$$
x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k.
$$

Coordinates that have repeatedly received large gradients receive smaller future steps. This is useful when parameter sensitivities have different scales, although the accumulated denominator can keep growing.

RMSProp replaces the unbounded sum by an exponential moving average:

$$
v_k=\gamma v_{k-1}+(1-\gamma)g_k\odot g_k,
$$

$$
x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k,
$$

where $\gamma\in[0,1)$. Recent gradient magnitudes therefore dominate the scale. Adam combines a first-moment average and a second-moment average:

$$
m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,
$$

$$
v_k=\beta_2v_{k-1}+(1-\beta_2)(g_k\odot g_k).
$$

Starting both at zero makes early averages biased towards zero, so for gradients indexed from zero use

$$
\hat m_k=\frac{m_k}{1-\beta_1^{k+1}},\qquad
\hat v_k=\frac{v_k}{1-\beta_2^{k+1}},
$$

and update

$$
x_{k+1}=x_k-\frac{\eta}{\sqrt{\hat v_k}+\epsilon}\odot\hat m_k.
$$

These algorithms change the effective coordinate-wise step; they do not remove the need to monitor objective values, gradients, scaling, and stopping criteria.

## 7. Newton and BFGS methods

Gradient descent uses a plane. Newton's method uses a local quadratic model:

$$
f(x_k+p)\approx f(x_k)+\nabla f(x_k)^Tp+\frac12p^T\nabla^2f(x_k)p.
$$

Minimising this model gives the linear system

$$
\nabla^2f(x_k)p_k=-\nabla f(x_k),
$$

followed by $x_{k+1}=x_k+p_k$. A numerical program should solve this system rather than explicitly forming the inverse Hessian. Near a solution, if the Hessian at $x^*$ is positive definite and the Hessian is Lipschitz continuous, sufficiently close Newton iterates satisfy

$$
\|x_{k+1}-x^*\|\leq C\|x_k-x^*\|^2,
$$

which is local quadratic convergence. Newton can be expensive because forming and solving with a Hessian costs more, and an indefinite Hessian can produce an unsuitable direction far from a minimum. A line search or damping is often needed in practice.

BFGS is a quasi-Newton method that builds curvature information from gradient changes rather than calculating a Hessian explicitly. Define

$$
s_k=x_{k+1}-x_k,\qquad y_k=\nabla f(x_{k+1})-\nabla f(x_k).
$$

The inverse-Hessian approximation $H_k$ is updated using

$$
H_{k+1}=(I-\rho_ks_ky_k^T)H_k(I-\rho_ky_ks_k^T)+\rho_ks_ks_k^T,
\qquad \rho_k=\frac1{y_k^Ts_k},
$$

provided $y_k^Ts_k>0$. It satisfies the secant equation in Hessian form, $B_{k+1}s_k=y_k$. The direction is $p_k=-H_k\nabla f(x_k)$, and a line search chooses $\alpha_k$ before setting $x_{k+1}=x_k+\alpha_kp_k$. BFGS often gives a useful compromise between gradient and Newton methods.

## 8. From equations to Python

An update equation maps directly to array operations. A gradient function should accept a parameter vector and return a vector of identical shape. The assignment must be explicit: compute the gradient at the current point, construct a new point, and then continue. In-place modification can be useful, but accidental aliasing makes debugging difficult. For Adam, moment arrays must be initialised with the same shape as $x$, and the exponent in bias correction must match the indexing convention. For Newton, use a linear solve. For any method, inspect objective history and stop when a meaningful condition, such as a small gradient norm or small step, is met.

A mechanical interpretation is helpful: $x$ might contain stiffness coefficients in a calibrated model, while $f$ measures squared prediction error. The gradient gives sensitivity of error to each coefficient. The Hessian describes coupling and curvature between coefficients. Scaling variables and choosing a method whose assumptions fit the model can matter as much as adding iterations.

## 9. Final worked exercises

### Exercise 1 — Conceptual scope of a convergence theorem

Suppose an engineer reports: “Gradient descent always finds the global optimum because the gradient points downhill.” Identify two missing assumptions needed for the standard $O(1/k)$ guarantee, state the guarantee in its usual smooth-convex form, and explain why the statement does not automatically apply to an arbitrary nonlinear mechanical model.

#### Worked solution

Two essential assumptions are that the objective is convex and that its gradient is $L$-Lipschitz continuous. A global minimiser $x^*$ must also exist, and the stated algorithm uses the constant step $\alpha=1/L$. Under these conditions,

$$
f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k},\qquad k\geq1.
$$

The negative gradient gives local decrease, but nonconvexity permits local minima and saddle points, so a stationary point need not be globally optimal. If the gradient is not smooth, a step based on a global curvature bound may not exist or may not provide the descent lemma. A realistic nonlinear mechanical model may therefore require line search, damping, multiple initial points, or a different analysis. The phrase “points downhill” describes a local direction, not a global theorem.

### Exercise 2 — One hand-calculated gradient update

Consider the two-parameter objective

$$
f(x_1,x_2)=\frac12(2x_1^2+4x_2^2)+x_1-2x_2.
$$

Find its gradient, evaluate the gradient at $x_0=(1,-1)^T$, and perform one gradient-descent update with $\alpha=0.1$. Compute the new objective value.

#### Worked solution

Differentiate each component:

$$
\nabla f(x)=\begin{bmatrix}2x_1+1\\4x_2-2\end{bmatrix}.
$$

At $x_0=(1,-1)^T$,

$$
\nabla f(x_0)=\begin{bmatrix}3\\-6\end{bmatrix}.
$$

The update is

$$
x_1=x_0-0.1\nabla f(x_0)
=\begin{bmatrix}1\\-1\end{bmatrix}-0.1\begin{bmatrix}3\\-6\end{bmatrix}
=\begin{bmatrix}0.7\\-0.4\end{bmatrix}.
$$

Evaluate the objective at this point:

$$
f(0.7,-0.4)=\frac12\bigl(2(0.7)^2+4(-0.4)^2\bigr)+0.7-2(-0.4).
$$

Thus $f(0.7,-0.4)=0.49+0.32+0.7+0.8=2.31$. At the starting point, $f(1,-1)=1+2+1+2=6$. The single update therefore reduces the objective from $6$ to $2.31$. This calculation also illustrates the implementation order: evaluate the gradient at the old vector, then subtract the scaled gradient.

### Exercise 3 — Diagnose and correct a Python update

The following code is intended to minimise $f(x)=\tfrac12\|x\|^2$, whose gradient is $x$. Identify the bugs and provide corrected code.

```python
import numpy as np

def gradient_descent(x, alpha, steps):
    history = []
    for k in range(steps):
        grad = x**2
        x = x + alpha * grad
        history.append(0.5 * np.dot(x, x))
    return x, history

x0 = np.array([2.0, -1.0])
solution, history = gradient_descent(x0, 0.1, 50)
```

#### Worked solution

There are three main bugs. First, the gradient of $\tfrac12\|x\|^2$ is $x$, not $x**2$. Squaring also loses the sign of the second component. Second, gradient descent subtracts the gradient, so the update must use $x-alpha*grad$, not addition. Third, the recorded objective is evaluated after the update; that is not mathematically wrong, but it should be deliberate. The corrected implementation is:

```python
import numpy as np

def gradient_descent(x, alpha, steps):
    x = np.asarray(x, dtype=float).copy()
    history = [0.5 * np.dot(x, x)]
    for _ in range(steps):
        grad = x
        x = x - alpha * grad
        history.append(0.5 * np.dot(x, x))
    return x, history

x0 = np.array([2.0, -1.0])
solution, history = gradient_descent(x0, 0.1, 50)
```

The copy prevents the caller's array from being changed unexpectedly. The initial objective is included, so `history` contains one value per recorded iterate, including $x_0$. Since the Hessian is the identity, $L=\mu=1$; $\alpha=0.1$ is a safe constant step, and each update multiplies the vector by $0.9$. Consequently the iterates approach $(0,0)^T$, while the objective decreases toward zero.
