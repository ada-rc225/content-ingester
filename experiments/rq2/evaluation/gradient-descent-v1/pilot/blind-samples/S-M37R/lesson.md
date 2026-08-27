# Gradient Descent: From First-Order Information to Convergence

Gradient descent is an iterative method for reducing a differentiable objective. This lesson develops the method from its optimisation problem, through the update rule and step-size logic, to convergence statements under increasingly strong assumptions. The order matters: a formula for an update is useful only when its direction and step size are related to properties of the objective. By the end, you should be able to formulate the basic problem, trace several updates, explain the role of smoothness, distinguish convex from strongly convex guarantees, and describe a backtracking choice of step size.

The discussion concerns unconstrained optimisation in a finite-dimensional Euclidean space. It is deliberately general: the vector could represent any collection of adjustable quantities, and the objective could measure any scalar criterion that is to be made smaller. Keep the assumptions attached to each conclusion. A method can be meaningful without every theorem below applying to it, and a stationary point need not be a minimum unless additional structure is available.

<!-- section: SEC-01 -->
## 1. The optimisation objective and stationarity

The canonical unconstrained problem is

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where $f:\mathbb{R}^d\to\mathbb{R}$ is at least continuously differentiable, written $f\in C^1$. The variable $x$ is a vector with $d$ components, and the objective assigns one real number to each possible vector. “Unconstrained” means that no additional feasible-set restriction is included in this formulation: every vector in $\mathbb{R}^d$ is a candidate. Adding a condition such as a bound or an equality would create a different problem setting and would require a corresponding change to the method.

At a differentiable local minimizer $x^*$, the first-order necessary condition is

$$
\nabla f(x^*)=0.
$$

The gradient collects the first partial derivatives and points in the direction of locally greatest increase under the Euclidean inner product. Consequently, its negative points in a locally decreasing direction when the gradient is nonzero. The stationarity condition says that there is no first-order change at the local minimizer. It does not say that every point satisfying $\nabla f(x)=0$ is a minimum. A stationary point may instead be a maximum or a saddle point, so stationarity is a necessary condition here, not a sufficient one.

A useful way to read the problem is therefore: seek a point whose objective is small, using gradients as local information, while checking which assumptions justify claims about the resulting sequence. The next section turns that local direction into an explicit iteration.

<!-- section: SEC-02 -->
## 2. The gradient-descent update

Start from an initial point $x_0\in\mathbb{R}^d$. For positive step sizes $\alpha_k$, gradient descent uses

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),\qquad k=0,1,2,\ldots.
$$

At iteration $k$, evaluate the gradient at the current point $x_k$, multiply it by the positive scalar $\alpha_k$, and subtract the result. The subtraction is essential: the gradient indicates local increase, so its negative is the first-order decrease direction. Standard gradient descent does not evaluate the gradient at a future or look-ahead point.

For a scalar example, let $f(x)=\tfrac12x^2$ and choose $x_0=3$ and $\alpha_k=\tfrac12$. Since $\nabla f(x)=x$, the first step is $x_1=3-\tfrac12(3)=1.5$, and the second is $x_2=1.5-\tfrac12(1.5)=0.75$. The iterates move toward the stationary point $0$. This calculation illustrates the mechanics, but it is not by itself a convergence theorem for every differentiable objective.

For a vector, the same operation is componentwise after the gradient has been evaluated. A practical trace should record the current point, the gradient, the step size, and the next point. That record makes sign errors visible. It also separates two questions: which direction is suggested by the gradient, and how far the algorithm should move in that direction. Smoothness supplies a way to connect those questions.

The following small implementation traces the scalar example. It is self-contained and uses no external data.

```python
def gradient_descent(gradient, x0, step, iterations):
    x = float(x0)
    trace = [x]
    for _ in range(iterations):
        x = x - step * gradient(x)
        trace.append(x)
    return trace


def quadratic_gradient(x):
    return x


trace = gradient_descent(quadratic_gradient, 3.0, 0.5, 4)
print([round(value, 4) for value in trace])
```

<!-- section: SEC-03 -->
## 3. Smoothness, descent, and a constant step

A gradient may change sharply from one point to another. The assumption used to control that change is $L$-smoothness: $f$ is continuously differentiable, $L>0$, and

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|,\qquad \forall x,y\in\mathbb{R}^d,
$$

where the norm is the Euclidean norm. This is a Lipschitz condition on the gradient, not on the function values. It says that the gradient difference cannot exceed $L$ times the distance between the points, uniformly over all $x$ and $y$.

For an $L$-smooth function, the Descent Lemma gives the quadratic upper bound

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle+\frac{L}{2}\|y-x\|^2,
$$

for all $x,y\in\mathbb{R}^d$. The right-hand side is a local linear prediction plus a nonnegative quadratic allowance for curvature. The inequality is an upper bound, so its direction and the coefficient $L/2$ matter.

Substitute the gradient-descent candidate $y=x-\alpha\nabla f(x)$ into this bound. The displacement is $y-x=-\alpha\nabla f(x)$, so the inner-product term becomes $-\alpha\|\nabla f(x)\|^2$ and the quadratic term becomes $\tfrac{L}{2}\alpha^2\|\nabla f(x)\|^2$. Thus

$$
f(x-\alpha\nabla f(x))
\leq f(x)-\alpha\left(1-\frac{L\alpha}{2}\right)\|\nabla f(x)\|^2.
$$

This expression explains why the step size is not an arbitrary scaling. If $0<\alpha<2/L$, the displayed coefficient is positive, and the upper bound predicts a decrease whenever the gradient is nonzero. The result is conditional on $L$-smoothness; it is not a universal statement for an arbitrary differentiable objective.

A common constant-step rule sets $\alpha_k=\alpha$. When $L$ is known, one listed choice is $\alpha=1/L$. Under the usual smooth-convex assumptions, another stated range is $\alpha\in(0,2/L)$. The qualifier belongs to the interval: do not detach it from the assumptions that support it. A constant step simplifies the algorithm and makes the hypotheses of later convergence results easy to check.

To practise the substitution, take $L=4$ and $\alpha=1/4$. Then $1-L\alpha/2=1-1/2=1/2$. The bound says that the objective decrease is at least represented by a term proportional to $\tfrac14\cdot\tfrac12\|\nabla f(x)\|^2$, provided the smoothness assumption holds. This is a bound on the upper-model change, not a claim that the exact decrease is always equal to that quantity.

<!-- section: SEC-04 -->
## 4. Convexity, strong convexity, and conditioning

Smoothness controls how quickly the gradient changes. Convexity supplies global geometry. A differentiable function $f:\mathbb{R}^d\to\mathbb{R}$ is convex when, for all $x,y\in\mathbb{R}^d$,

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle.
$$

The tangent-plane expression on the right is a global lower bound for the function. In particular, the objective does not dip below any of its first-order tangent models. This is a global statement, and the inequality points upward from the tangent model; reversing it would describe a different property.

Strong convexity adds a positive quadratic gap. A differentiable function is $\mu$-strongly convex for $\mu>0$ when, for all $x,y\in\mathbb{R}^d$,

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle+\frac{\mu}{2}\|y-x\|^2.
$$

The additional term says that the function lies above its tangent model by at least a quadratic amount away from the reference point. Strong convexity is therefore a stronger assumption than the first-order convex lower bound. It should be stated explicitly whenever a strongly convex convergence rate is invoked.

When an objective is both $L$-smooth and $\mu$-strongly convex, its condition number is

$$
\kappa=\frac{L}{\mu}\geq1.
$$

The ratio compares an upper scale for gradient variation with a lower curvature scale. A larger ratio indicates a wider separation between these scales. In the results that follow, $\kappa$ appears in the contraction factor, so conditioning affects how quickly the stated bound shrinks. This interpretation does not replace the theorem: it explains a parameter in the theorem while retaining its smoothness and strong-convexity assumptions.

<!-- section: SEC-05 -->
## 5. Convergence guarantees and their boundaries

The first selected guarantee is for an $L$-smooth and convex function $f:\mathbb{R}^d\to\mathbb{R}$ that has a global minimizer $x^*$. If gradient descent uses the constant step $\alpha_k=1/L$, then for $k\geq1$,

$$
f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k}.
$$

The objective gap is the difference between the value at the current iterate and the global minimum value. The factor $1/k$ is the sublinear part of the guarantee: increasing $k$ reduces the bound, but the reduction is not a fixed multiplicative contraction at each iteration. Every hypothesis matters: smoothness, convexity, existence of a global minimizer, the step $1/L$, and $k\geq1$.

Under the stronger assumption that $f$ is $L$-smooth and $\mu$-strongly convex, two related contractions are available with their own step-size pairings. With

$$
\alpha=\frac{2}{L+\mu},
$$

the squared distance satisfies

$$
\|x_k-x^*\|^2\leq\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}\|x_0-x^*\|^2,
$$

where $\kappa=L/\mu$. With the different step $\alpha=1/L$, the objective gap satisfies

$$
f(x_k)-f(x^*)\leq\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).
$$

These are linear, or geometric, rates because the right sides contain a factor raised to $k$. Do not attach the distance contraction to $1/L$, or the objective contraction to $2/(L+\mu)$: each expression has the step size stated with it. Nor should either result be reported without $L$-smoothness and $\mu$-strong convexity. The stronger rate is a consequence of stronger geometry, not a property of gradient descent on every differentiable function.

For a short comparison, if $L=10$ and $\mu=2$, then $\kappa=5$. The distance-rate factor before exponentiation is $(5-1)/(5+1)=2/3$, while the objective-gap factor for the $1/L$ choice is $1-2/10=0.8$. These numbers belong to different bounds and different step-size statements. Their numerical comparison is only an interpretation of the displayed formulas, not a new convergence theorem.

It is useful to separate three levels of language when interpreting these results. An update rule tells you how to produce $x_{k+1}$ from $x_k$. A descent estimate tells you what an upper model permits you to conclude about one proposed move, provided the relevant smoothness condition holds. A convergence theorem describes a whole sequence, but only under its complete list of geometric and step-size assumptions. Moving from one level to the next without checking the hypotheses is a common source of overstatement.

Consider the convex result as a checklist rather than as a slogan. First ask whether the objective is known to be $L$-smooth. Next ask whether it is convex in the global first-order sense and whether a global minimizer $x^*$ exists. Then check that the iteration uses $\alpha_k=1/L$, not merely some positive step. Finally, make sure the index is in the theorem's range $k\geq1$. Only after these checks may the objective-gap expression be used as the stated bound. If one of the checks fails, the formula may still be a useful comparison or design target, but it has not been established as that theorem's guarantee.

The strongly convex result has a parallel checklist with a different emphasis. Smoothness supplies the upper curvature scale $L$, while strong convexity supplies the positive lower scale $\mu$. Together they define $\kappa=L/\mu$. The distance statement uses the step $2/(L+\mu)$ and the factor involving $\kappa$; the objective statement uses the step $1/L$ and the factor $1-\mu/L$. Writing the step directly beside the bound prevents the two cases from being accidentally blended. It also makes clear why conditioning is relevant: the quantities governing the contraction depend on the ratio of the two scales.

As a paper exercise, suppose the current point is $x_k=(2,-1)$ and the gradient there is $\nabla f(x_k)=(4,-2)$. With $\alpha_k=0.1$, compute the displacement and the next point. The displacement is $-\alpha_k\nabla f(x_k)=(-0.4,0.2)$, so $x_{k+1}=(1.6,-0.8)$. The calculation does not require a value of the objective. To decide whether a theorem applies, however, you would still need information about smoothness, convexity, a minimizer, and the step-size conditions. A numerical update and a convergence certificate answer different questions.

Another useful exercise is to inspect the sign in the Descent Lemma substitution. The linear term is $\langle\nabla f(x),-\alpha\nabla f(x)\rangle=-\alpha\|\nabla f(x)\|^2$, which is nonpositive for positive $\alpha$. The quadratic term is nonnegative and competes with that decrease. If a derivation produces a positive linear term, the update sign has probably been reversed. If it produces $L$ instead of $L/2$ in the upper model, the bound has also changed. Checking these small algebraic details is part of tracing an algorithm, not an optional decoration.

Finally, distinguish objective gap from distance to a minimizer. The convex theorem bounds $f(x_k)-f(x^*)$ by a quantity involving the initial distance. The first strongly convex contraction displayed above bounds $\|x_k-x^*\|^2$ directly, while the second bounds the objective gap. These measures are related by the assumptions, but they are not interchangeable labels. State which quantity is being bounded before interpreting a rate, and retain the exponent and coefficient exactly as displayed.

Before moving to adaptive step selection, test your understanding with a verbal reconstruction. Explain why the negative gradient is used, identify the assumption that limits gradient variation, and say what convexity contributes beyond smoothness. Then identify the strongest assumption in the strongly convex case and name the parameter that combines the two curvature scales. A clear answer should use the words direction, step size, upper bound, lower bound, and condition number in their mathematical roles rather than treating them as interchangeable descriptions.

You can also compare two proposed algorithm descriptions. The first computes a gradient at $x_k$, chooses a positive step, and tests the objective at $x_k-\alpha_k\nabla f(x_k)$. The second computes a gradient at a different point and tests $x_k+\alpha_k\nabla f(x_k)$. The first matches the standard update and the Armijo trial expression; the second changes both the evaluation point or sign and therefore is not the rule developed here. Such a comparison is a simple audit: locate the current iterate, the gradient evaluation point, the sign, and the positivity condition before considering performance.

For a final written response, describe what you would record in an experiment or a hand calculation: the initial point, the gradient at each current point, the selected step, the objective value when it is available, and whether an Armijo trial was accepted. A trace makes it possible to distinguish an arithmetic error from a failure of an assumption. It also makes the boundary of the lesson visible: the procedure can be executed from local evaluations, whereas a theorem-level statement requires independently justified global properties of the objective.

<!-- section: SEC-06 -->
## 6. Armijo backtracking and a complete trace

When a useful constant step is not supplied, Armijo backtracking offers a bounded step-selection procedure. Choose an initial trial step $\bar{\alpha}>0$, a contraction factor $\eta\in(0,1)$, and $c\in(0,1)$. At iteration $k$, consider trial steps

$$
\alpha_k=\eta^m\bar{\alpha},\qquad m=0,1,2,\ldots,
$$

and choose the smallest nonnegative integer $m$ for which

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)
\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
$$

The left side evaluates the objective at the proposed gradient step. The right side requires a sufficient decrease measured using the squared gradient norm. If the trial fails, multiply the trial step by $\eta$ and test again. The acceptance inequality is not reversed, and the squared norm is part of the rule. Once accepted, use the selected step in the update and continue at the next iterate.

The following self-contained code implements this rule for $f(x)=\tfrac12x^2$, whose gradient is $x$. It prints the accepted step and the new point at each iteration. The parameters satisfy the required ranges, and the loop searches $m$ from zero so the first accepted integer is selected.

```python
def objective(x):
    return 0.5 * x * x


def gradient(x):
    return x


x = 3.0
trial_step = 1.0
eta = 0.5
c = 0.25

for iteration in range(4):
    g = gradient(x)
    if g == 0.0:
        print(iteration, "stationary", x)
        break
    for m in range(20):
        step = (eta ** m) * trial_step
        candidate = x - step * g
        if objective(candidate) <= objective(x) - c * step * (g * g):
            x = candidate
            print(iteration, "m=", m, "step=", round(step, 4), "x=", round(x, 4))
            break
    else:
        raise RuntimeError("no Armijo step accepted")
```

To consolidate the method, trace one iteration by writing down $x_k$, $\nabla f(x_k)$, each trial step, and the two sides of the acceptance inequality. Then state which assumptions would be needed before replacing that trace with a convergence claim. The update rule itself only describes an iteration. The $O(1/k)$ and linear results require the separate smoothness, convexity, minimizer, and step-size hypotheses stated earlier. Keeping the algorithm, the diagnostics, and the theorem conditions distinct is the central habit for using gradient descent responsibly.
