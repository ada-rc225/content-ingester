# Gradient Descent and Optimisation

## 1. Why optimisation matters in mechanical engineering

Many mechanical-engineering calculations can be expressed as the search for a vector of design or state variables that makes a scalar objective as small as possible. The vector might contain beam dimensions, spring parameters, control settings, or coordinates describing a configuration. In the unconstrained model, we write

$$
\min_{x\in\mathbb{R}^d} f(x).
$$

The objective $f$ could represent mass, strain energy, tracking error, or a least-squares residual. The methods in this chapter generate a sequence $x_0,x_1,x_2,\ldots$ that hopefully approaches a useful solution. Their behaviour depends on the geometry of $f$, the quality of its derivatives, and the choice of step sizes.

A differentiable local minimiser must satisfy the first-order necessary condition

$$
\nabla f(x^*)=0.
$$

This condition says that there is no first-order change in any direction. It does not, by itself, distinguish a minimum from a maximum or a saddle point. If $f$ is twice continuously differentiable, a local minimiser also satisfies the second-order necessary condition

$$
\nabla^2 f(x^*)\succeq 0,
$$

meaning that the Hessian is positive semidefinite. Conversely, if the gradient vanishes and

$$
\nabla^2 f(x^*)\succ0,
$$

then $x^*$ is a strict local minimiser. The Hessian therefore describes local curvature: positive curvature in every nonzero direction gives a bowl-shaped local model, whereas a negative curvature direction warns that the stationary point is not a minimum.

These are local statements. Convexity will later provide a stronger conclusion: for a differentiable convex function, any point satisfying the first-order condition is a global minimiser.

## 2. Smoothness, convexity, and curvature

A function is $L$-smooth when its gradient is Lipschitz continuous:

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|.
$$

The constant $L$ limits how rapidly the gradient can change. For a twice differentiable function, it is equivalent to requiring the spectral norm of the Hessian to be at most $L$. If the function is also convex, this can be written

$$
0\preceq\nabla^2f(x)\preceq LI.
$$

Smoothness gives the descent lemma, or quadratic upper bound,

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle+\frac{L}{2}\|y-x\|^2.
$$

The linear term predicts the immediate change, and the quadratic term allows for curvature. This inequality is the basic tool for selecting a safe gradient-descent step.

A differentiable function is convex when its graph lies above every tangent plane:

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle.
$$

For mechanical interpretation, convexity means that mixing two designs cannot produce an objective larger than the corresponding mixture of their objective values. It rules out misleading local wells. A differentiable function is $\mu$-strongly convex when the tangent-plane bound includes a positive quadratic term:

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle+\frac{\mu}{2}\|y-x\|^2.
$$

For a $C^2$ function, strong convexity is equivalent to

$$
\nabla^2f(x)\succeq\mu I.
$$

Thus $\mu$ is a lower curvature bound, while $L$ is an upper curvature bound. If both hold, the condition number is

$$
\kappa=\frac{L}{\mu}.
$$

A large condition number describes a long, narrow valley. Gradient descent then makes progress across the steep direction while taking many small zig-zagging steps along the shallow direction. This is common in engineering models whose variables have different physical scales.

## 3. Gradient descent and choosing a step

The gradient points in the direction of steepest increase, so the negative gradient is a local descent direction whenever the gradient is nonzero. Standard gradient descent uses

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k).
$$

The mathematical update maps directly to Python: store the current vector, evaluate its gradient, multiply by a scalar learning rate, and subtract. A constant step $\alpha=1/L$ is a standard choice when a valid smoothness bound is known. Under the usual smooth-convex assumptions, constant steps in $(0,2/L)$ are also associated with descent behaviour, although $1/L$ is particularly convenient for the stated rate.

The descent lemma makes the role of the step explicit. Substituting $y=x-\alpha\nabla f(x)$ gives

$$
f(x-\alpha\nabla f(x))
\leq f(x)-\alpha\left(1-\frac{L\alpha}{2}\right)\|\nabla f(x)\|^2.
$$

For a sufficiently small positive step, the right side is below $f(x)$. A step that is too large can overshoot the valley.

Exact line search chooses the best distance along the current descent ray:

$$
\alpha_k=\arg\min_{\alpha>0}f(x_k-\alpha\nabla f(x_k)).
$$

This can be attractive for a simple quadratic, where the one-dimensional minimisation may be solved analytically. It can be expensive for a complicated simulation because it requires repeated objective evaluations.

Armijo backtracking avoids solving that one-dimensional problem exactly. Choose a trial step $\bar\alpha>0$, a contraction factor $\eta\in(0,1)$, and a small sufficient-decrease constant $c\in(0,1)$. Test $\alpha_k=\eta^m\bar\alpha$ for $m=0,1,2,\ldots$ until

$$
f(x_k-\alpha_k\nabla f(x_k))
\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
$$

The test compares actual reduction with a fraction of the linear prediction. Backtracking is practical when $L$ is unknown or varies across the design space. In code, the trial step must be reduced inside a loop, and the candidate objective must be evaluated at the candidate point rather than at the unchanged current point.

## 4. What convergence means

Suppose $f$ is convex and $L$-smooth, has a global minimiser $x^*$, and gradient descent uses $\alpha=1/L$. Then

$$
f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k}.
$$

This is an $O(1/k)$ objective-gap rate. It says that accuracy improves indefinitely, but reducing the error by another fixed factor becomes progressively more costly. The proof combines the descent lemma with convexity. The resulting one-step inequality is

$$
f(x_{k+1})-f(x^*)
\leq\frac{L}{2}\left(\|x_k-x^*\|^2-\|x_{k+1}-x^*\|^2\right).
$$

Summing makes the intermediate distance terms cancel; this telescoping is why the initial distance controls the bound.

If $f$ is both $L$-smooth and $\mu$-strongly convex, the geometry is more favourable. With $\alpha=1/L$,

$$
f(x_k)-f(x^*)\leq\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).
$$

This is linear, or geometric, convergence. The word linear refers to the error being multiplied by a fixed factor below one, not to a straight-line graph. With the tuned constant step $\alpha=2/(L+\mu)$, the distance satisfies

$$
\|x_k-x^*\|^2\leq\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}\|x_0-x^*\|^2.
$$

Strong convexity supplies a unique minimiser and turns curvature information into a contraction estimate.

## 5. Momentum and acceleration

Momentum uses recent displacement to reduce zig-zagging. Polyak's Heavy Ball method is

$$
x_{k+1}=x_k-\alpha\nabla f(x_k)+\beta(x_k-x_{k-1}),
$$

with $\beta\in[0,1)$. The additional term carries motion through a shallow valley, like inertia in a mechanical system. It can also destabilise the iteration, so parameters must respect the objective's curvature.

For the quadratic $f(x)=\tfrac12x^TAx$, with $A$ symmetric positive definite and eigenvalues in $[\mu,L]$, the specifically tuned values

$$
\alpha^*=\frac{4}{(\sqrt L+\sqrt\mu)^2},\qquad
\beta^*=\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^2
$$

improve the condition-number dependence from roughly $1-O(1/\kappa)$ to $1-O(1/\sqrt\kappa)$. These parameter claims belong to this stated quadratic setting and should not automatically be transferred to every nonlinear problem.

Nesterov's accelerated gradient method uses a look-ahead point. Set $y_0=x_0$ and $\lambda_0=1$, then calculate

$$
x_{k+1}=y_k-\frac1L\nabla f(y_k),
$$

$$
\lambda_{k+1}=\frac{1+\sqrt{1+4\lambda_k^2}}2,
$$

$$
y_{k+1}=x_{k+1}+\frac{\lambda_k-1}{\lambda_{k+1}}(x_{k+1}-x_k).
$$

The gradient is evaluated at $y_k$, not at $x_k$. For smooth convex objectives, this parameterisation gives

$$
f(x_k)-f(x^*)\leq\frac{2L\|x_0-x^*\|^2}{(k+1)^2},
$$

an $O(1/k^2)$ rate. Acceleration improves the theoretical rate, but its extra state variables and sensitivity to assumptions make careful implementation important.

## 6. Stochastic and adaptive methods

For an empirical objective

$$
f(x)=\frac1N\sum_{i=1}^Nf_i(x),
$$

computing the full gradient may require processing every experiment or data record. Stochastic gradient descent uses an estimate $g_k(x_k)$ and updates

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

Noise makes individual steps imperfect. With persistent nonzero variance, a small constant step generally approaches an error neighbourhood rather than exactly converging. Diminishing steps can support convergence when, in addition to suitable objective, bias, moment, and stability assumptions, they satisfy the Robbins--Monro conditions

$$
\sum_{k=1}^{\infty}\eta_k=\infty,
\qquad
\sum_{k=1}^{\infty}\eta_k^2<\infty.
$$

The first condition ensures that learning does not stop too soon; the second controls accumulated noise. These conditions alone are not a complete convergence theorem.

Adaptive methods change each coordinate's effective step according to recent gradients. For AdaGrad, start with $v_{-1}=0$ and accumulate

$$
v_k=v_{k-1}+g_k\odot g_k,
$$

then use

$$
x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k.
$$

Coordinates with large historical gradients receive smaller future steps. This is useful when parameters have very different scales, although the ever-growing accumulator can eventually make steps extremely small.

RMSProp replaces the unbounded sum by an exponential moving average:

$$
v_k=\gamma v_{k-1}+(1-\gamma)g_k\odot g_k,
$$

$$
x_{k+1}=x_k-\frac{\eta}{\sqrt{v_k}+\epsilon}\odot g_k.
$$

Recent gradient magnitudes dominate, so the method can remain responsive. Adam combines a moving average of gradients with a moving average of squared gradients:

$$
m_k=\beta_1m_{k-1}+(1-\beta_1)g_k,
$$

$$
v_k=\beta_2v_{k-1}+(1-\beta_2)(g_k\odot g_k).
$$

Because both averages start at zero, use bias corrections for zero-based iteration:

$$
\hat m_k=\frac{m_k}{1-\beta_1^{k+1}},\qquad
\hat v_k=\frac{v_k}{1-\beta_2^{k+1}}.
$$

The update is

$$
x_{k+1}=x_k-\frac{\eta}{\sqrt{\hat v_k}+\epsilon}\odot\hat m_k.
$$

The element-wise products and square roots must be implemented component by component. The small $\epsilon$ prevents division by zero.

## 7. Newton and BFGS methods

Gradient descent uses a linear local model. Newton's method retains the quadratic Taylor model:

$$
f(x_k+p)\approx f(x_k)+\nabla f(x_k)^Tp+\frac12p^T\nabla^2f(x_k)p.
$$

Setting the model gradient to zero gives the Newton system

$$
\nabla^2f(x_k)p_k=-\nabla f(x_k),
$$

followed by $x_{k+1}=x_k+p_k$. In numerical Python, solve this linear system rather than explicitly computing a matrix inverse. Newton can be very fast near a solution: if the Hessian at a stationary point is positive definite and the Hessian is Lipschitz continuous nearby, sufficiently close iterates satisfy

$$
\|x_{k+1}-x^*\|\leq C\|x_k-x^*\|^2.
$$

This local quadratic convergence is powerful, but forming and factoring a Hessian can be costly, and an undamped Newton step may be poor far from the solution.

BFGS is a quasi-Newton method. It builds an inverse-Hessian approximation $H_k$ from displacement and gradient-change vectors,

$$
s_k=x_{k+1}-x_k,\qquad y_k=\nabla f(x_{k+1})-\nabla f(x_k).
$$

It enforces the secant relation through a curvature update. When $y_k^Ts_k>0$, the inverse-Hessian formula is

$$
H_{k+1}=(I-\rho_ks_ky_k^T)H_k(I-\rho_ky_ks_k^T)+\rho_ks_ks_k^T,
\qquad \rho_k=\frac1{y_k^Ts_k}.
$$

The search direction is $p_k=-H_k\nabla f(x_k)$, usually combined with a line search. BFGS avoids explicitly storing the exact Hessian while learning curvature from successive iterates. For engineering problems, this often offers a useful compromise between first-order simplicity and Newton's rapid local behaviour.

## 8. From equations to reliable Python

A vector update should preserve the mathematical order of operations. A basic implementation accepts an objective and gradient, copies the initial vector, and repeatedly computes the gradient before subtracting the scaled result. The stopping test should use a meaningful quantity such as the gradient norm, and the iteration limit protects against indefinite execution. Arrays should use floating-point values so that division and square roots behave as intended. For stochastic methods, the gradient function may sample a mini-batch; for Newton, a linear solver replaces an explicit inverse; for adaptive methods, state arrays must persist between iterations.

A useful diagnostic habit is to inspect shapes, compare one hand-calculated update with the program's first update, and test on a quadratic whose gradient is known. A wrong sign, a missing copy, evaluating the gradient at the new point, or confusing element-wise multiplication with a matrix product can make a program appear to run while implementing a different algorithm.

## 9. Final worked exercises

### Exercise 1 — Conceptual scope of convergence

A student says: “If gradient descent reaches a point with zero gradient, that point is the unique global minimiser, regardless of the objective.” Explain precisely why this statement is too strong. State what first- and second-order conditions establish, and identify assumptions under which the conclusion does become global and unique.

#### Worked solution

A zero gradient is only the first-order necessary condition for a differentiable local minimum; it is also satisfied at maxima and saddle points. The second-order necessary condition at a twice differentiable local minimum is a positive-semidefinite Hessian, while a positive-definite Hessian together with zero gradient gives a strict local minimum. Neither local test alone guarantees a global minimum for a nonconvex function.

If the function is differentiable and convex, every stationary point is a global minimiser because the tangent-plane inequality puts every other function value above the stationary value. If the function is additionally strongly convex with parameter $\mu>0$, its curvature is bounded below, so the global minimiser is unique. Thus “zero gradient” is enough for a global conclusion under convexity, and uniqueness requires strong convexity or another suitable uniqueness condition. Convergence of an algorithm must still be justified by its step-size rule and the relevant smoothness assumptions.

### Exercise 2 — One hand-calculated update

Consider the mechanical-style quadratic objective

$$
f(x_1,x_2)=\frac12(4x_1^2+x_2^2),
$$

which can represent differently scaled penalty terms for two design variables. Starting from $x_0=(2,-1)^T$, calculate the gradient and perform one gradient-descent update with step size $\alpha=0.1$.

#### Worked solution

Differentiate each term:

$$
\nabla f(x)=\begin{bmatrix}4x_1\\x_2\end{bmatrix}.
$$

At the initial point,

$$
\nabla f(x_0)=\begin{bmatrix}8\\-1\end{bmatrix}.
$$

The update is

$$
x_1=x_0-0.1\nabla f(x_0)
=\begin{bmatrix}2\\-1\end{bmatrix}
-0.1\begin{bmatrix}8\\-1\end{bmatrix}
=\begin{bmatrix}1.2\\-0.9\end{bmatrix}.
$$

The first coordinate moves substantially because its curvature and gradient are larger; the second changes less. This illustrates why scaling and conditioning matter. The Hessian is $\operatorname{diag}(4,1)$, so the objective is strongly convex with lower curvature 1 and has upper curvature 4.

### Exercise 3 — Diagnose and correct Python

The following code is intended to minimise $f(x)=\tfrac12\|x\|^2$ using gradient descent, but it contains bugs. Identify them and provide corrected code.

```python
import numpy as np

def gradient(x):
    return x

def gradient_descent(x0, alpha=0.1, steps=5):
    x = x0
    for _ in range(steps):
        x = x + alpha * gradient(x)
    return x

x0 = np.array([2, -1])
print(gradient_descent(x0))
```

#### Worked solution

The mathematical update subtracts the gradient, so the plus sign is wrong. It moves away from the minimiser instead of towards the origin. Also, assigning `x = x0` is safe for this particular expression because a new array is created by the arithmetic, but copying the input is a robust interface choice: it prevents an in-place implementation from unexpectedly changing the caller's array. Finally, floating-point initial data make the intended numerical type explicit.

A corrected implementation is:

```python
import numpy as np

def gradient(x):
    return x

def gradient_descent(x0, alpha=0.1, steps=5):
    x = np.asarray(x0, dtype=float).copy()
    for _ in range(steps):
        g = gradient(x)
        x = x - alpha * g
    return x

x0 = np.array([2.0, -1.0])
print(gradient_descent(x0))
```

Here `g` is evaluated at the current iterate, and the subtraction exactly matches $x_{k+1}=x_k-\alpha\nabla f(x_k)$. The first update is $(1.8,-0.9)^T$, and subsequent updates multiply both coordinates by $0.9$. Consequently, after five updates the result is $(2,-1)^T(0.9)^5$, approximately $(1.18098,-0.59049)^T$, which is closer to the unique minimiser $(0,0)^T$.
