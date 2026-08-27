# Gradient Descent: From an Objective to a Traceable Iteration

Gradient descent is a first-order method for reducing a differentiable objective. In this lesson, the objective can be read abstractly or as an idealized engineering quantity such as an energy or a parameter-misfit measure. That framing is deliberately limited: real engineering objectives need not have the mathematical structure used in the guarantees below, a stationary point need not be a physical optimum, and gradient descent is not automatically suitable for every design problem.

<!-- section: SEC-01 -->
## Formulating the objective and recognizing stationarity

We begin with the unconstrained problem

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where $f:\mathbb{R}^d\to\mathbb{R}$ is at least continuously differentiable, written $f\in C^1$. The vector $x$ collects the quantities being adjusted, while $f(x)$ assigns one scalar objective value to each possible vector. For example, $x$ might contain parameters in an idealized calibration model and $f(x)$ might measure mismatch. This is still the stated unconstrained problem over all of $\mathbb{R}^d$; adding feasibility limits would define a different problem setting.

The gradient $\nabla f(x)$ gathers the partial derivatives of the objective at $x$. Its entries describe the objective's local first-order sensitivity to changes in the entries of $x$. A fundamental necessary condition connects minimization with the gradient: if $x^*$ is a local minimizer and $f$ is differentiable at $x^*$, then

$$
\nabla f(x^*)=0.
$$

Such a point is called stationary. The direction of the implication matters. A differentiable local minimizer must be stationary, but stationarity alone is not sufficient to establish a minimum without additional assumptions. In an engineering interpretation, it is therefore unsafe to label every zero-gradient parameter vector as a physically meaningful optimum. The condition instead motivates a computational aim: move from an initial vector toward points where the gradient becomes small, while separately tracking how the objective behaves.

It helps to separate the mathematical objects before starting an iteration. The vector is the proposed state or parameter choice, the objective is the scalar quantity being minimized, and the gradient is evaluated from that objective at a particular vector. Changing the meaning of the vector does not change these roles. If two calibration parameters are collected into $x$, for instance, the gradient has two corresponding components, but the objective still returns one value. The formulation also says nothing yet about whether a minimizer exists or whether it is unique. At this stage, the conclusion is deliberately narrow: differentiability lets us state the necessary zero-gradient condition at a local minimizer. Later assumptions will support particular descent and convergence statements; they should not be read backward into every differentiable problem.

<!-- section: SEC-02 -->
## Turning the gradient into an iteration

Choose an initial point $x_0\in\mathbb{R}^d$. Given a positive step size $\alpha_k$, gradient descent generates

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),
\qquad k=0,1,2,\ldots.
$$

There are three details to retain when tracing the method. The gradient is evaluated at the current iterate $x_k$, its multiple is subtracted, and the step size is positive. The result becomes the next iterate. The index $k$ is therefore an iteration counter, not a component index of the vector.

A reliable hand calculation follows the formula from the inside outward. First evaluate the full gradient using the current vector. Next multiply every gradient component by the same scalar step size for that iteration. Finally subtract the resulting vector from the current vector. Only after that subtraction should the iteration index advance. This order prevents two common tracing mistakes: mixing components from different iterates and recomputing part of the gradient after one component has already changed. It also clarifies what “first-order” means here: the update uses the objective's first derivatives at the current point. The displayed rule does not evaluate a gradient at the proposed next point and does not use a look-ahead point.

The following self-contained example traces this rule for an idealized two-coordinate energy. It is an illustration of the update, not a claim about every mechanical system. Each row is recorded before its update, so the printed gradient and objective belong to the same current iterate.

```python
import numpy as np

def objective(x):
    return 0.5 * (x[0] ** 2 + 4.0 * x[1] ** 2)

def gradient(x):
    return np.array([x[0], 4.0 * x[1]], dtype=float)

x = np.array([2.0, -1.0], dtype=float)
alpha = 0.20

print(" k        x[0]        x[1]          f(x)       ||grad||")
for k in range(6):
    g = gradient(x)
    print(f"{k:2d}  {x[0]:11.6f}  {x[1]:11.6f}  "
          f"{objective(x):12.6f}  {np.linalg.norm(g):12.6f}")
    x = x - alpha * g
```

An iteration table makes the algorithm auditable: you can recompute a row's gradient, multiply it by the stated step, subtract it from the row's vector, and recover the next row. The observed decrease in this particular trace is evidence about this example only. To explain when a step is supported more generally, we need a condition controlling how rapidly the gradient can change.

<!-- section: SEC-03 -->
## Relating smoothness, descent, and a constant step

A continuously differentiable function is $L$-smooth, for a positive constant $L$, when its gradient is $L$-Lipschitz in the Euclidean norm:

$$
\|\nabla f(x)-\nabla f(y)\|
\leq L\|x-y\|,
\qquad \text{for all }x,y\in\mathbb{R}^d.
$$

This condition concerns changes in the gradient, not a Lipschitz bound on the function values. You can read $L$ as a global bound in this definition: larger changes in position are allowed proportionally larger changes in gradient, but the ratio is controlled for every pair of points.

For interpretation, compare two points rather than focusing on one gradient in isolation. The left side measures how much the two gradient vectors differ, and the right side scales the separation of the two points by $L$. The definition requires the comparison everywhere in the domain. A few nearby evaluations in a convergence table cannot establish that global requirement. In the idealized energy framing, smoothness may be viewed as an explicit mathematical assumption about sensitivity variation; it should not be inferred merely because the plotted objective appears visually smooth or because a numerical run did not fail.

Smoothness supplies a quadratic upper model called the Descent Lemma. If $f$ is $L$-smooth, then for all $x,y\in\mathbb{R}^d$,

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle
+\frac{L}{2}\|y-x\|^2.
$$

The inequality is an upper bound, and the quadratic coefficient is $L/2$. To connect it to the iteration, substitute $x=x_k$ and $y=x_k-\alpha_k\nabla f(x_k)$. Direct simplification gives

$$
f(x_{k+1})
\leq f(x_k)
-\alpha_k\left(1-\frac{L\alpha_k}{2}\right)
\|\nabla f(x_k)\|^2.
$$

This calculation shows why the step size cannot be discussed independently of smoothness. The negative gradient supplies the direction in the update, while the multiplier determines how far the iteration moves before the local first-order information is used again.

Notice how the conclusion was obtained without changing algorithms. The proposed point in the Descent Lemma was chosen to be exactly the gradient-descent update. Its displacement from the current point is therefore the negative step times the current gradient. The inner-product term contributes a negative multiple of the squared gradient norm, while the quadratic term contributes a positive multiple. Their combination produces the coefficient in the displayed bound. Keeping both terms visible explains why simply saying “move downhill” is incomplete: the upper model and the step together support the conditional decrease statement.

One simple policy is a constant step, $\alpha_k=\alpha$ for every iteration. When $L$ is known, a common choice is

$$
\alpha=\frac{1}{L}.
$$

Under the usual smooth convex assumptions, constant choices in the interval $\alpha\in(0,2/L)$ are also used. That interval must retain its assumptions; it is not a universal prescription for an arbitrary engineering objective. In the displayed smoothness calculation, choosing $1/L$ makes the coefficient of the squared gradient norm equal to $1/(2L)$, so the bound becomes

$$
f(x_{k+1})\leq f(x_k)-\frac{1}{2L}\|\nabla f(x_k)\|^2.
$$

This is a conditional descent statement: it follows from $L$-smoothness and the stated update and step. If the assumptions have not been justified for a model, a decreasing computed history may still be useful to inspect, but it does not manufacture those assumptions.

Constant means that the value of $\alpha$ is reused, not that the iterates or gradients remain constant. A trace can therefore show different displacements at different iterations because the gradient changes. When reading such a trace, record the chosen $L$ and step alongside the objective history. That makes clear whether $1/L$ was actually used and prevents an observed sequence from being detached from the condition that supports its interpretation.

<!-- section: SEC-04 -->
## Distinguishing convexity, strong convexity, and conditioning

Smoothness controls gradient variation and gives an upper bound. Convexity supplies a different kind of structure: a global first-order lower bound. A differentiable function is convex when, for every $x,y\in\mathbb{R}^d$,

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle.
$$

Thus the affine expression built from the value and gradient at $x$ lies below the function at every $y$. The universal phrase “for every” is essential; behavior along one computed trajectory does not by itself establish this definition.

For a positive constant $\mu$, the function is $\mu$-strongly convex when, for every $x,y\in\mathbb{R}^d$,

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle
+\frac{\mu}{2}\|y-x\|^2.
$$

Strong convexity strengthens the convex lower bound by the positive quadratic term with coefficient $\mu/2$. It is not simply another name for smoothness: the two conditions bound different sides of a first-order description.

The shared affine part of the two lower bounds makes their relationship easy to see. Convexity requires the function to remain above that affine expression. Strong convexity requires it to remain above the affine expression plus a positive quadratic amount that grows with squared distance from $x$. Because $\mu$ is positive, the additional term cannot be discarded or given a negative sign. These are definitions quantified over all pairs of points, not labels assigned from the appearance of one curve or one iteration history. They provide the vocabulary needed to read the guarantees that follow, but they do not assert that a chosen mechanical model satisfies either definition.

When an objective is both $L$-smooth and $\mu$-strongly convex, its condition number is

$$
\kappa=\frac{L}{\mu}\geq 1.
$$

The order of this ratio matters. It combines the two constants used in the selected convergence statements and gives a compact way to interpret their contraction factors. This mathematical definition applies only when both conditions hold. Idealized energy or calibration examples can make the notation concrete, but they do not imply that every engineering objective is convex or strongly convex.

<!-- section: SEC-05 -->
## Reading convergence guarantees with their boundaries

A convergence statement is a package: assumptions, step choice, measured quantity, and bound must stay together. First suppose $f:\mathbb{R}^d\to\mathbb{R}$ is both $L$-smooth and convex, $x^*$ is a global minimizer, and gradient descent uses $\alpha_k=1/L$. Then, for $k\geq1$,

$$
f(x_k)-f(x^*)
\leq
\frac{L\|x_0-x^*\|^2}{2k}.
$$

The measured quantity here is the objective gap. The numerator records the smoothness constant and the initial squared distance to a global minimizer; the denominator grows as $2k$. This is the stated $O(1/k)$ behavior, but the shorthand must not hide the hypotheses or the exact bound. It is not a guarantee for an objective known only to be differentiable.

Read the inequality from left to right as a comparison between the current suboptimality and a computable form involving the iteration number, provided the theorem's quantities and assumptions are available. The gap compares objective values, whereas the numerator contains a distance between vectors. Those two measures should not be casually exchanged. The statement begins at $k=1$, uses the initial point in the numerator, and keeps the same global minimizer throughout. Its denominator is exactly $2k$. Each detail matters when matching a theoretical curve to an iteration record.

Now strengthen the structure: suppose $f$ is $L$-smooth and $\mu$-strongly convex, so $\kappa=L/\mu$. Two useful contractions are paired with two different constant steps. With

$$
\alpha=\frac{2}{L+\mu},
$$

the squared distance satisfies

$$
\|x_k-x^*\|^2
\leq
\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}
\|x_0-x^*\|^2.
$$

With the different choice $\alpha=1/L$, the objective gap satisfies

$$
f(x_k)-f(x^*)
\leq
\left(1-\frac{\mu}{L}\right)^k
\bigl(f(x_0)-f(x^*)\bigr).
$$

Do not exchange the step sizes attached to these bounds. The first statement pairs $2/(L+\mu)$ with a squared-distance contraction; the second pairs $1/L$ with an objective-gap contraction. Both require smoothness and strong convexity.

The exponents also tell you what is being repeated. In the distance result, the ratio involving the condition number is raised to $2k$ and multiplies the initial squared distance. In the objective result, the factor involving $\mu/L$ is raised to $k$ and multiplies the initial objective gap. A table intended to illustrate the first result would therefore record distances to $x^*$; one intended to illustrate the second would record objective gaps. An objective column alone does not directly display a distance bound, even if both quantities happen to decline in a particular example.

The role of conditioning is visible in the factors. Because $\mu/L=1/\kappa$, the second factor is $1-1/\kappa$. As $\kappa$ becomes larger, that factor lies closer to one, so its bound contracts more slowly per iteration. This interpretation is conditional on the same assumptions. A convergence history from an idealized parameter calibration can be compared with these forms only after identifying which quantity is plotted and which conditions and step were used.

The distinction between the convex and strongly convex cases is therefore structural, not cosmetic. The general convex result bounds the objective gap with a term proportional to $1/k$. The strongly convex results repeatedly multiply an initial error by a factor below one. None of these statements says that every stationary point in an unverified engineering model is a physical optimum, and none makes gradient descent universally appropriate.

<!-- section: SEC-06 -->
## Selecting a step by Armijo backtracking

A constant step is convenient when an appropriate $L$ is known. Armijo backtracking is a bounded practical alternative for selecting a step at the current iterate. Choose an initial trial step $\bar\alpha>0$, a contraction factor $\eta\in(0,1)$, and a constant $c\in(0,1)$. Find the smallest integer $m\geq0$ such that $\alpha_k=\eta^m\bar\alpha$ satisfies

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)
\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
$$

The left side evaluates the objective at the proposed gradient-descent point. The right side demands sufficient decrease relative to the current value, the trial step, and the squared gradient norm. If the condition fails, increasing $m$ by one multiplies the trial step by $η$ again. Accepting the first successful trial enforces the smallest-nonnegative-$m$ rule.

The trial sequence begins with $m=0$, so the first candidate is the full initial trial step. Only a failed inequality triggers contraction. Since $η$ lies strictly between zero and one, each subsequent candidate is smaller and remains positive. The parameter $c$ also lies strictly between zero and one and appears on the sufficient-decrease side of the test. These ranges are part of the rule, not optional tuning descriptions. At the next outer iteration, the same process evaluates a new current gradient and searches for that iteration's accepted $\alpha_k$. Thus the backtracking loop is nested inside the gradient-descent loop: it chooses the positive multiplier before the accepted update is taken.

This implementation is self-contained and records the accepted step at each iteration for the same idealized objective used earlier.

```python
import numpy as np

def objective(x):
    return 0.5 * (x[0] ** 2 + 4.0 * x[1] ** 2)

def gradient(x):
    return np.array([x[0], 4.0 * x[1]], dtype=float)

x = np.array([2.0, -1.0], dtype=float)
bar_alpha = 1.0
eta = 0.5
c = 0.1

print(" k    accepted alpha          f(x)")
for k in range(6):
    g = gradient(x)
    m = 0
    alpha = (eta ** m) * bar_alpha
    while objective(x - alpha * g) > objective(x) - c * alpha * np.dot(g, g):
        m += 1
        alpha = (eta ** m) * bar_alpha
    x = x - alpha * g
    print(f"{k:2d}    {alpha:12.6f}    {objective(x):12.6f}")
```

Backtracking changes how the positive step is chosen; the accepted update is still $x_{k+1}=x_k-\alpha_k\nabla f(x_k)$ with the gradient evaluated at the current iterate. The sufficient-decrease test must keep its inequality direction and squared gradient norm. It should also be described for what it is: a step-selection rule, not evidence that an arbitrary objective has the convexity or strong-convexity assumptions required by the earlier rates.

Taken together, the workflow is now traceable. Formulate the unconstrained differentiable objective, recognize stationarity as necessary rather than sufficient, apply the current-gradient update, connect constant steps to smoothness, distinguish the structures behind the convergence bounds, and use Armijo backtracking when following that selected alternative. At every stage, the mathematical condition belongs beside the conclusion it supports.
