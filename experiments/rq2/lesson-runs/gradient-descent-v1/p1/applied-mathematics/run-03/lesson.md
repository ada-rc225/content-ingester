# Gradient Descent: Assumptions, Updates, and Guarantees

Gradient descent is simple to write down, but interpreting it well requires more than memorising an iteration. The useful applied-mathematics habit is to keep three layers separate: the optimisation problem, the assumptions imposed on its objective, and the conclusion those assumptions support. We will build those layers in order. Along the way, a small quadratic example will make the algebra traceable, but it should be read as an example rather than as evidence that every differentiable objective has the same geometry.

<!-- section: SEC-01 -->
## The optimisation problem and stationarity

We consider the unconstrained problem

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where $f:\mathbb{R}^d\to\mathbb{R}$ is at least continuously differentiable, written $f\in C^1$. The vector $x$ collects the quantities we can vary, while the scalar $f(x)$ measures the objective value. “Unconstrained” is important: the admissible set here is all of $\mathbb{R}^d$. Adding a constraint would define a different problem and would require additional ideas.

In an applied model, the objective might summarise a mismatch between a model and observations, an energy, or another scalar quantity of interest. That interpretation can motivate why smaller values are desirable, but it does not determine the mathematical shape of the objective. In particular, differentiability does not imply convexity. We will therefore keep the modelling interpretation separate from the assumptions used in each result.

Differentiability gives a necessary first-order condition. If $x^*$ is a local minimiser and $f$ is differentiable at $x^*$, then

$$
\nabla f(x^*)=0.
$$

Such a point is called stationary. The logical direction matters: a differentiable local minimiser must be stationary, but stationarity alone does not certify a minimum. For example, for

$$
f(t)=(t^2-1)^2,
$$

the derivative is $f'(t)=4t(t^2-1)$, so $t=0$ is stationary. Yet $f(0)=1$, while nearby nonzero values can be smaller. This counterexample prevents a common reversal of the necessary condition.

It is useful to phrase the logic as a diagnostic question. If a proposed local minimiser has a nonzero gradient, it cannot satisfy the necessary condition. If its gradient is zero, it has passed that necessary check, but no classification has yet been earned. The one-dimensional example passes the stationarity check at the origin and still fails to be a local minimum. Thus “stationary” describes a first-order equation, not a complete optimisation verdict.

The gradient therefore supplies a target condition without, by itself, classifying every stationary point. Gradient descent will generate a sequence of candidate points intended to move toward lower objective values. Whether the values actually decrease, and what convergence statement is justified, will depend on assumptions introduced later rather than on the update formula alone.

<!-- section: SEC-02 -->
## From the gradient to an iteration

Choose an initial point $x_0\in\mathbb{R}^d$ and positive step sizes $\alpha_k$. Standard gradient descent is

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),
\qquad k=0,1,2,\ldots.
$$

There are three details worth reading literally. The gradient is evaluated at the current iterate $x_k$; the update subtracts rather than adds it; and the step size is positive. No future or look-ahead point appears in this rule.

One way to audit an iteration is to name its quantities before doing any arithmetic. At iteration $k$, first evaluate $g_k=\nabla f(x_k)$. Next form the displacement $s_k=-\alpha_k g_k$. Finally set $x_{k+1}=x_k+s_k$. This is merely the same update decomposed into observable pieces, but it makes the indexing and sign harder to lose. It also distinguishes the direction $-g_k$ from the displacement: the step size scales the direction, so two positive step sizes use the same direction but produce different candidate points.

The sign has a local geometric motivation. If $g=\nabla f(x_k)$, then the inner product of $g$ with the proposed direction $-g$ is

$$
\langle g,-g\rangle=-\|g\|^2.
$$

Thus the first-order change associated with that direction is negative whenever $g\ne0$. This is a local, first-order observation, not yet a guarantee about the finite step $x_k-\alpha_k g$. A step can extend beyond the region where a local linear picture is informative, so a separate bound is needed to justify actual descent.

As a traceable example, take

$$
f(x)=\tfrac12(x_1^2+4x_2^2),
\qquad \nabla f(x)=(x_1,4x_2).
$$

Starting from $x_0=(2,1)$ with $α_0=1/4$ gives

$$
x_1=(2,1)-\tfrac14(2,4)=(3/2,0).
$$

This calculation illustrates the componentwise action of one update. It does not establish a general step-size rule; for that, we next connect gradient variation to a bound on the objective.

Notice what can and cannot be concluded from this arithmetic. The new point has been computed exactly from the rule, and its second coordinate becomes zero for this particular starting point and step. Nothing in the update formula says that a coordinate must generally vanish, that the sequence must reach a minimiser in finitely many iterations, or even that this chosen step must lower an arbitrary objective. Those questions concern the objective and the step together, which is why the next assumption is stated globally over pairs of points.

<!-- section: SEC-03 -->
## Smoothness, descent, and a constant step

A continuously differentiable function is $L$-smooth, with $L>0$, when its gradient is Lipschitz continuous in the Euclidean norm:

$$
\|\nabla f(x)-\nabla f(y)\|
\le L\|x-y\|,
\qquad \text{for every }x,y\in\mathbb{R}^d.
$$

This condition controls changes in the gradient. It must not be confused with a claim that the function values themselves are Lipschitz continuous.

The universal quantifier is doing real work. The inequality compares gradients at any two points, not only at consecutive iterates and not only near a minimiser. The constant $L$ provides a uniform upper control on how much the gradient can change relative to the displacement. This is precisely the kind of information missing from the local sign calculation in the previous section: it connects behaviour at the current point with behaviour at the finite candidate point.

The analytic payoff is the Descent Lemma. If $f$ is $L$-smooth, then for every $x,y\in\mathbb{R}^d$,

$$
f(y)\le f(x)+\langle\nabla f(x),y-x\rangle
+\frac{L}{2}\|y-x\|^2.
$$

This is a quadratic upper bound: the linear term describes the gradient at $x$, and the final term controls departure from that linear description. Substitute $x=x_k$ and $y=x_k-\alpha\nabla f(x_k)$. Writing $g_k=\nabla f(x_k)$ gives

$$
\begin{aligned}
f(x_{k+1})
&\le f(x_k)-\alpha\|g_k\|^2
+\frac{L\alpha^2}{2}\|g_k\|^2\\
&=f(x_k)-\alpha\left(1-\frac{L\alpha}{2}\right)\|g_k\|^2.
\end{aligned}
$$

The substitution exposes the entire argument. The inner-product term becomes $-\alpha\|g_k\|^2$ because the displacement is $-\alpha g_k$. The quadratic term becomes $(L\alpha^2/2)\|g_k\|^2$ because the displacement norm is $\alpha\|g_k\|$. Combining them leaves a competition between a negative term proportional to $\alpha$ and a positive correction proportional to $\alpha^2$. This explains analytically why the sign of the final coefficient, rather than the negative-gradient direction alone, determines what the upper bound certifies.

The coefficient $α(1-Lα/2)$ is positive when $0<\alpha<2/L$. Hence this bound certifies a strict objective decrease at a nonstationary iterate under $L$-smoothness and such a step. At a stationary iterate, the update leaves the point unchanged.

At the endpoint $\alpha=2/L$, the coefficient in this particular bound is zero, so the displayed argument no longer certifies a strict decrease. For a step beyond that endpoint, the coefficient is negative and the right-hand side no longer provides a decrease statement. This is a statement about what the bound proves; it should not be replaced by an unsupported prediction about every individual numerical run.

For the constant-step rule, $α_k=α$. When $L$ is known, a common choice is $α=1/L$; under the usual smooth-convex assumptions, the standard interval stated for the constant choice is $α\in(0,2/L)$. With $α=1/L$, the preceding bound becomes

$$
f(x_{k+1})\le f(x_k)-\frac{1}{2L}\|\nabla f(x_k)\|^2.
$$

This specialisation is easy to interpret without hiding the assumptions. If the current gradient is nonzero, the certified reduction is at least the positive quantity shown on the right of the subtraction. If the gradient norm is small, the bound certifies a correspondingly small reduction. The statement concerns objective values from one iteration to the next; it is not yet a rate for the distance to a minimiser or for the objective gap after $k$ iterations.

The following self-contained trace uses the earlier quadratic with $L=4$ and the constant step $1/L$. Each row is produced from the current gradient before the next update.

```python
import numpy as np

A = np.diag([1.0, 4.0])
L = 4.0
alpha = 1.0 / L
x = np.array([2.0, 1.0])

def objective(z):
    return 0.5 * z @ A @ z

def gradient(z):
    return A @ z

for k in range(6):
    print(k, x.copy(), objective(x), np.linalg.norm(gradient(x)))
    x = x - alpha * gradient(x)
```

The printed objective values decrease in this example, consistently with the smoothness-based bound. The table is a computation, while the lemma explains which assumption makes the decrease defensible.

<!-- section: SEC-04 -->
## Convexity, strong convexity, and conditioning

Smoothness supplies an upper model, but the convergence results ahead also need global lower structure. A differentiable function $f:\mathbb{R}^d\to\mathbb{R}$ is convex when, for all $x,y\in\mathbb{R}^d$,

$$
f(y)\ge f(x)+\langle\nabla f(x),y-x\rangle.
$$

The affine expression on the right is a global lower bound. Consequently, if a convex differentiable function has a stationary point $x^*$, inserting $∇f(x^*)=0$ shows that $f(y)\ge f(x^*)$ for every $y$. In this setting, stationarity does identify a global minimiser. This conclusion uses convexity; it does not retroactively make stationarity sufficient for arbitrary differentiable objectives.

This lower-bound inequality points in the opposite direction from the Descent Lemma. There is no conflict: the two statements answer different questions. Smoothness places a quadratic upper bound on a function value at $y$ using information at $x$. Convexity places an affine lower bound on that value. When both assumptions hold, the objective is controlled from above and below in distinct ways, and each control appears in a different part of the convergence analysis.

For $μ>0$, the function is $μ$-strongly convex when, for all $x,y\in\mathbb{R}^d$,

$$
f(y)\ge f(x)+\langle\nabla f(x),y-x\rangle
+\frac{\mu}{2}\|y-x\|^2.
$$

Strong convexity strengthens the convex lower bound by a positive quadratic term. Compare the roles carefully: $L$-smoothness limits how rapidly gradients can change and produces an upper bound, whereas strong convexity supplies the displayed lower bound with parameter $μ$.

The quantifier again ranges over every pair of points in the domain. Strong convexity is therefore a global structural assumption in the theorem used here, not a visual impression from a small neighbourhood. The positive quadratic term records a definite separation above the affine lower model as $y$ moves away from $x$. Removing that term returns the convex inequality, so the value of $μ$ belongs to the stronger statement and must remain positive.

When an objective is both $L$-smooth and $μ$-strongly convex, its condition number is

$$
\kappa=\frac{L}{\mu}\ge1.
$$

The ratio is $L/μ$, not its reciprocal. Its algorithmic significance will appear directly in a contraction factor, allowing conditioning to be interpreted through a stated rate rather than through a visual analogy alone.

<!-- section: SEC-05 -->
## Convergence guarantees and their boundaries

We can now read convergence theorems in assumption-to-conclusion form. First suppose that $f$ is $L$-smooth and convex, that a global minimiser $x^*$ exists, and that gradient descent uses $α_k=1/L$. Then, for every $k\ge1$,

$$
f(x_k)-f(x^*)
\le
\frac{L\|x_0-x^*\|^2}{2k}.
$$

The left side is an objective gap, not an iterate-distance claim. The bound decays like $1/k$, with its scale determined by $L$ and the initial squared distance to the chosen global minimiser. Every hypothesis belongs with the conclusion: differentiability alone, or smoothness without convexity, does not yield this theorem.

The formula can be read as a guaranteed envelope over iteration count. Doubling $k$ halves the right-hand side, while changing the starting point changes the prefactor through its squared distance from $x^*$. The theorem does not say that the observed gap equals the bound at every iteration. A computed sequence may lie below the envelope; the inequality states the maximum certified by these quantities. It also begins at $k=1$, exactly as specified, rather than making a separate claim at the initial index.

Strong convexity supports geometric contraction. Suppose instead that $f$ is both $L$-smooth and $μ$-strongly convex, and recall $κ=L/μ$. There are two distinct step-and-bound pairings.

With


$$
\alpha=\frac{2}{L+\mu},
$$

the squared distance satisfies

$$
\|x_k-x^*\|^2
\le
\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}
\|x_0-x^*\|^2.
$$

With the different step $α=1/L$, the objective gap satisfies

$$
f(x_k)-f(x^*)
\le
\left(1-\frac{\mu}{L}\right)^k
\bigl(f(x_0)-f(x^*)\bigr).
$$

The first result pairs $2/(L+μ)$ with squared-distance contraction; the second pairs $1/L$ with objective-gap contraction. Swapping the steps between the displayed conclusions would change the theorem.

It helps to track both the measured quantity and the exponent. In the first case, the base $(κ-1)/(κ+1)$ is raised to $2k$ and multiplies an initial squared distance. In the second, the base $1-μ/L$ is raised to $k$ and multiplies an initial objective gap. Calling both results “linear convergence” refers to geometric decay with iteration count; it does not make their left-hand sides or their step sizes interchangeable.

These factors also expose conditioning. Since $κ\ge1$, $(κ-1)/(κ+1)$ lies between zero and one. As $κ$ grows, it approaches one, so the displayed distance bound contracts more slowly. Likewise, $1-μ/L=1-1/κ$ approaches one as $κ$ grows. This interpretation follows from the stated bounds: it says how their certified contraction depends on conditioning, not that every run must match a bound exactly.

For a concrete reading of the formulas, if $κ=9$, the squared-distance factor after $k$ iterations is $(8/10)^{2k}$ for the step $2/(L+μ)$. With the step $1/L$, the objective-gap factor is $(8/9)^k$. These numbers are evaluations of different bounds, not a contest between two observed trajectories. Their purpose is to make visible how the condition number enters each theorem while preserving the quantity and step attached to that theorem.

The boundaries are as important as the rates. The convex result certifies a sublinear objective-gap bound under smoothness, convexity, existence of a global minimiser, and the step $1/L$. The strongly convex results certify geometric bounds under the stronger global assumption, with each conclusion tied to its own step. None of these statements turns the earlier nonconvex stationary-point example into a convex problem, and none should be quoted after dropping its hypotheses.

<!-- section: SEC-06 -->
## Armijo backtracking for choosing a step

A constant step such as $1/L$ requires a usable value of $L$. Armijo backtracking is a bounded alternative rule for selecting the step at the current iterate. Choose an initial trial step $\bar\alpha>0$, a contraction factor $η\in(0,1)$, and $c\in(0,1)$. For $m=0,1,2,\ldots$, form

$$
\alpha_k=\eta^m\bar\alpha.
$$

Select the smallest nonnegative integer $m$ for which

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)
\le f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
$$

Then use the standard update with that accepted $α_k$. Beginning at $m=0$ tests the full trial step. Each rejection increments $m$, multiplying the trial by $η$; the first accepted trial is therefore the one associated with the smallest acceptable integer. The inequality is a sufficient-decrease test: its right side is below $f(x_k)$ whenever the current gradient is nonzero.

The same quadratic gives a manual view of the acceptance logic. At $x=(2,1)$, the gradient is $(2,4)$, its squared norm is $20$, and the objective value is $4$. Take $\bar\alpha=1$, $\eta=1/2$, and $c=1/4$. For $m=0$, the trial step is $1$, the candidate is $(0,-3)$, and its objective value is $18$; the right side of the test is $-1$, so this trial is rejected. For $m=1$, the step is $1/2$, the candidate is $(1,-1)$, and its value is $5/2$; the right side is $3/2$, so that trial is also rejected. For $m=2$, the step is $1/4$, the candidate is $(3/2,0)$, and its value is $9/8$; the right side is $11/4$, so the inequality holds. Because the trials were checked in increasing order of $m$, this accepted value is associated with the smallest acceptable nonnegative integer.

Here is a self-contained implementation of exactly that rule on the same quadratic. A fixed number of outer iterations keeps the trace focused on trial contraction and acceptance.

```python
import numpy as np

A = np.diag([1.0, 4.0])
x = np.array([2.0, 1.0])
bar_alpha = 1.0
eta = 0.5
c = 0.25

def objective(z):
    return 0.5 * z @ A @ z

def gradient(z):
    return A @ z

for k in range(6):
    g = gradient(x)
    m = 0
    alpha = (eta ** m) * bar_alpha
    while objective(x - alpha * g) > objective(x) - c * alpha * (g @ g):
        m += 1
        alpha = (eta ** m) * bar_alpha
    print(k, objective(x), alpha, m)
    x = x - alpha * g
```

This trace reports the accepted step and contraction count at each iterate. The line search does not alter the gradient-descent direction: it still evaluates $∇f(x_k)$ at the current point and subtracts a positive multiple. It changes only how that multiple is selected.

The parameters have separate roles in the stated construction. The positive value $\bar\alpha$ is the first trial at every displayed outer iteration. The factor $η$, strictly between zero and one, contracts a rejected trial. The value $c$, also strictly between zero and one, appears in the required-decrease side of the acceptance inequality. Keeping these roles explicit makes the code a direct translation of the mathematical rule rather than an unrelated numerical heuristic.

Armijo acceptance should not be used to silently inherit the two convergence formulas from the previous section. Those formulas were stated with their own fixed steps and assumptions. What backtracking supplies here is the displayed sufficient-decrease selection rule. The broader lesson is to keep the chain explicit: identify the problem, compute the current gradient, apply the selected step rule, and attach a descent or convergence conclusion only when its stated assumptions are present.
