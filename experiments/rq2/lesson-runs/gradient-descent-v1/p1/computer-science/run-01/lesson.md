# Gradient Descent: From Objective to Reliable Iteration

Gradient descent is a first-order optimisation method: it uses the gradient, rather than a Hessian or a second-order model, to move an iterate toward a smaller objective value. This lesson develops the method as an algorithm and then attaches each guarantee to the assumptions that make it valid. The running viewpoint is useful for computer science because a loss function can be inspected through values, gradients, iteration traces, and stopping diagnostics. A loss function is only a bounded motivation here: real production objectives need not be convex, and full-batch gradient descent is not a complete training system.

The central habit is to keep three things together: the mathematical problem, the update actually executed, and the assumptions behind any claim about convergence. A small program can show an iteration, but a trace alone cannot prove a theorem. Conversely, a theorem with missing hypotheses is not a safe algorithmic specification.

<!-- section: SEC-01 -->
## 1. The optimisation target and stationarity

An unconstrained differentiable optimisation problem has the form

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where the objective is a function $f:\mathbb{R}^d\to\mathbb{R}$ and is assumed to be at least continuously differentiable, $f\in C^1$. “Unconstrained” means that the mathematical domain is all of $\mathbb{R}^d$; no feasible-set boundary or inequality constraint is being added. In a program, $x$ is commonly represented by a NumPy array, but that representation does not change the problem's domain.

The gradient $\nabla f(x)$ collects the partial derivatives. It gives the local direction of greatest increase under the Euclidean inner product. Therefore $-\nabla f(x)$ is the local direction in which a sufficiently small move is expected to decrease the objective. This is motivation for the update developed next, not yet a guarantee for an arbitrary step size.

A differentiable local minimizer $x^*$ must satisfy the first-order necessary condition

$$
\nabla f(x^*)=0.
$$

The word “necessary” matters. A zero gradient is a stationary point, but stationarity alone is not sufficient to establish that the point is a minimum. It may describe another type of stationary behaviour, and the result above requires that $x^*$ is already known to be a local minimizer and that $f$ is differentiable there. Keep those hypotheses beside the equation when interpreting a diagnostic such as a small gradient norm.

For a machine-learning-flavoured example, one may regard $f$ as a deliberately simple loss over a parameter vector. This example motivates why an implementation might minimise an objective; it does not assert that every deployed loss has the assumptions used later. The mathematical task remains unconstrained minimisation over $\mathbb{R}^d$.

<!-- section: SEC-02 -->
## 2. The gradient-descent state transition

Gradient descent starts from an initial point $x_0\in\mathbb{R}^d$ and uses positive step sizes $\alpha_k$. Its state transition is

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),\qquad k=0,1,2,\ldots.
$$

The gradient is evaluated at the current state $x_k$. The subtraction sign is essential: the step follows the negative gradient. A positive step size controls how far the algorithm travels in that direction. This is standard full-gradient descent: the rule calls for the gradient of the objective at the current iterate, rather than a gradient at a look-ahead point or a randomly selected partial estimate.

A useful implementation trace records $k$, the current vector, the objective value, the gradient, its Euclidean norm, and the chosen step size. Reading a trace as a state machine makes errors easier to find: compute the gradient from the displayed state, multiply it by the displayed positive step, subtract, and use the result as the next state. A decreasing objective in a short trace is evidence about that run, not a universal convergence proof. The index is part of the state record because it distinguishes the initial point from the result after one update. It also makes it possible to compare a reported value with a theorem whose bound is stated for a particular $k$.

Before running an implementation, write down the interface between the objective and the optimiser. The objective accepts one vector and returns one scalar. The gradient accepts the same vector and returns a vector of the same dimension. The optimiser owns the current state and the step-size policy, but it should not quietly change the objective or evaluate a different gradient. This separation is a practical way to catch shape errors, stale gradients, and accidental sign changes. It also makes the mathematical update visible in the program rather than hiding it inside an unexplained library call.

```python
import numpy as np

def objective(x):
    return 0.5 * np.dot(x, x)

def gradient(x):
    return x.copy()

x = np.array([3.0, -2.0])
alpha = 0.25
for k in range(6):
    g = gradient(x)
    print(f"k={k}, x={x}, f={objective(x):.6f}, ||g||={np.linalg.norm(g):.6f}")
    x = x - alpha * g
```

For this example, the gradient is the current vector, so each update scales the vector by $1-\alpha$. The code is an executable trace of one chosen objective and one chosen step; it does not replace the conditions attached to the general results. In particular, the program does not silently establish that an arbitrary objective is smooth, convex, or strongly convex. Notice also that a program can continue iterating even when its mathematical interpretation is wrong. If the implementation adds the gradient instead of subtracting it, or computes the gradient before updating a different state, it is executing a different algorithm. Explicit state traces turn that difference into something inspectable.

<!-- section: SEC-03 -->
## 3. Smoothness, the descent bound, and constant steps

The step-size question is governed in part by how quickly the gradient can change. A continuously differentiable function is $L$-smooth, with $L>0$, when its gradient is Lipschitz with respect to the Euclidean norm:

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|,\qquad \forall x,y\in\mathbb{R}^d.
$$

This is a statement about gradient differences, not about the function values themselves. The universal quantifier matters: the same positive constant $L$ controls every pair of points in the domain under discussion.

For an $L$-smooth function, the Descent Lemma gives the quadratic upper bound

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle+\frac{L}{2}\|y-x\|^2,
$$

for all $x,y\in\mathbb{R}^d$. The direction is an upper bound, and the coefficient is $L/2$. To see why this is relevant, substitute the gradient-descent candidate $y=x-\alpha\nabla f(x)$. The linear term becomes negative, while the quadratic term penalises a step that is too large. Thus smoothness supplies a controlled comparison between the current objective and the objective after a proposed update.

A constant-step scheme sets $\alpha_k=\alpha$. When $L$ is known, one common choice is $\alpha=1/L$. Under the usual smooth-convex assumptions, another stated choice is $\alpha\in(0,2/L)$. That interval must not be detached from its assumptions or treated as a universal safe rule for every differentiable objective. The safe engineering habit is to state the assumptions, the value of $L$ being used, and the step-size rule together.

In a diagnostic implementation, compare the observed objective change with the expected direction and inspect the gradient norm. If an objective rises, possible explanations include an unsuitable step, an incorrect gradient, or a mismatch between the actual objective and the assumptions used to choose the step. A diagnostic can reveal a problem in one run; it cannot by itself identify which theorem applies. Similarly, a falling objective does not prove that the gradient was implemented correctly: a particular test path can conceal an error. Use small analytically understood objectives as checks, then state separately what is known about the objective used in the real task.

<!-- section: SEC-04 -->
## 4. Convexity, strong convexity, and conditioning

Smoothness limits gradient variation. Convexity adds global shape information through a first-order lower bound. A differentiable function is convex when, for all $x,y\in\mathbb{R}^d$,

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle.
$$

The inequality points upward from the tangent-plane expression: the tangent is a global lower bound. This is different from the Descent Lemma's smoothness upper bound. Keeping the two directions distinct prevents a common implementation-and-proof error.

A differentiable function is $\mu$-strongly convex for $\mu>0$ when, for all $x,y\in\mathbb{R}^d$,

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle+\frac{\mu}{2}\|y-x\|^2.
$$

Strong convexity is a strengthened lower bound: the positive quadratic term is present, with coefficient $\mu/2$. It is not merely a label for a function that “looks curved” in a plot. The quantified inequality and its positive parameter are the definition used by the convergence result.

When an objective is both $L$-smooth and $\mu$-strongly convex, its condition number is

$$
\kappa=\frac{L}{\mu}\geq 1.
$$

A larger $\kappa$ indicates a wider separation between the two constants in the available bound. In an algorithmic trace, conditioning helps explain why progress can be uneven across directions, but the formula alone does not license a claim about an arbitrary objective. The assumptions must hold, and the relevant step size must be paired with the relevant rate.

For computer science, this separation is particularly useful when reading optimisation code. A loss plot and a small final gradient norm are observations. Convexity and strong convexity are mathematical properties that must be justified separately. A production loss may be nonconvex, and the simple full-batch algorithm here is intentionally narrower than a complete training pipeline. In code review, ask whether the claimed property belongs to the function, to the particular data set, or only to a local experiment. Do not infer a global theorem from a graph with a finite number of samples. The purpose of the definitions is precisely to make the scope of an assertion checkable.

<!-- section: SEC-05 -->
## 5. Convergence guarantees and their boundaries

The selected convex guarantee has precise hypotheses. Let $f:\mathbb{R}^d\to\mathbb{R}$ be $L$-smooth and convex, let $x^*$ be a global minimizer, and use the constant step $\alpha_k=1/L$. Then for $k\geq1$,

$$
f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k}.
$$

The objective gap therefore has an $O(1/k)$ upper bound under those assumptions. The bound includes the initial distance, the smoothness constant, and the iteration index. It is not a promise that every objective decreases at exactly that visible rate, nor does it apply after silently dropping convexity, smoothness, the global-minimizer condition, or the step-size condition.

The strongly convex result is different. If $f$ is $L$-smooth and $\mu$-strongly convex, then with

$$
\alpha=\frac{2}{L+\mu},
$$

the squared-distance contraction is

$$
\|x_k-x^*\|^2\leq\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}\|x_0-x^*\|^2,
$$

where $\kappa=L/\mu$. With the different step $\alpha=1/L$, the objective contraction is

$$
f(x_k)-f(x^*)\leq\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).
$$

The pairing is part of the theorem: $2/(L+\mu)$ belongs to the distance bound, while $1/L$ belongs to the objective-gap bound. Both require the smoothness and strong-convexity assumptions. The results explain why conditioning matters, but they do not certify a run when those assumptions have not been established.

A practical review of an implementation should therefore ask: which objective is being evaluated, where is the gradient taken, which step was used, what properties of the objective are known, and which quantity is being bounded? If the answers are unclear, report the observation without upgrading it into a theorem. The distinction between an objective gap and a distance gap is also important. The convex result bounds $f(x_k)-f(x^*)$, whereas the first strongly convex statement bounds $\|x_k-x^*\|^2$. These quantities are related only through additional assumptions; they are not interchangeable labels for “error.”

The iteration count in a bound is not a promise about wall-clock time. Each full gradient evaluation may have a different computational cost depending on the objective and its data. Thus an asymptotic iteration statement and an implementation performance report answer different questions. The theorem describes a mathematical sequence under its hypotheses; a systems report may also need memory, data-access, and evaluation-cost measurements. Keeping those questions separate avoids turning a rate in $k$ into an unsupported claim about a deployed system.

<!-- section: SEC-06 -->
## 6. Armijo backtracking as an explicit step-selection procedure

A constant step is simple when a suitable $L$ is known. Armijo backtracking offers a bounded practical alternative that tests sufficient decrease at the current state. Choose an initial trial step $\bar{\alpha}>0$, a contraction factor $\eta\in(0,1)$, and $c\in(0,1)$. For the current iterate $x_k$, test trial steps of the form

$$
\alpha_k=\eta^m\bar{\alpha},\qquad m=0,1,2,\ldots,
$$

and select the smallest nonnegative integer $m$ for which

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
$$

The right-hand side requires a decrease proportional to the trial step and the squared gradient norm. The acceptance inequality is written in this direction; reversing it would change the test. The parameters also matter: the initial trial must be positive, and both $\eta$ and $c$ lie strictly between zero and one.

The following implementation makes the state and acceptance test visible. It uses the same simple quadratic objective as the earlier trace, so the code is a demonstration of the procedure rather than a claim about all objectives.

```python
import numpy as np

def f(x):
    return 0.5 * np.dot(x, x)

def grad_f(x):
    return x.copy()

x = np.array([3.0, -2.0])
eta, c, trial = 0.5, 0.1, 2.0
for k in range(5):
    g = grad_f(x)
    m = 0
    alpha = trial
    while f(x - alpha * g) > f(x) - c * alpha * np.dot(g, g):
        m += 1
        alpha = (eta ** m) * trial
    print(f"k={k}, alpha={alpha:.6f}, m={m}, f={f(x):.6f}")
    x = x - alpha * g
```

The loop computes the current gradient once, contracts the positive trial step, accepts the first step satisfying the stated inequality, and then performs the gradient-descent transition. In a larger system, one would also define stopping and failure policies; those are implementation choices beyond the selected mathematical statements. The important transferable skill is traceability: every accepted step can be related to its current state, its tested objective value, its parameters, and its sufficient-decrease condition. A trace should make clear whether the displayed objective is measured before or after the update, because mixing those conventions can make a correct implementation appear to violate a decrease test. It is also useful to record the accepted value of $m$, not only $\alpha_k$, since $m$ explains how many contractions were needed.

Armijo backtracking does not remove the need to understand the objective. It provides a rule for selecting a step based on a sufficient-decrease comparison at the current iterate. The selected inequality contains the squared gradient norm, so the test becomes less demanding as the gradient becomes small, while still requiring the stated proportional decrease. The parameters influence the procedure: $\eta$ controls how aggressively trial steps are contracted, and $c$ controls the required fraction of the first-order decrease. These observations describe the rule; they are not additional convergence guarantees beyond the selected statement.

When communicating results, distinguish four layers. First, report the objective and gradient definitions. Second, report the update and the step policy. Third, report empirical observations such as values in a trace. Finally, state any theorem with every hypothesis and its matched quantity. This layered format is useful in algorithm documentation because another reader can reproduce the computation without mistaking a local diagnostic for a global guarantee. It also makes clear what must be revisited when the objective, representation, or step policy changes.

To summarise, gradient descent is the current-state update $x_{k+1}=x_k-\alpha_k\nabla f(x_k)$. Smoothness explains a quadratic upper bound, convexity and strong convexity supply distinct global assumptions, and the convergence rates apply only with their complete hypotheses and paired step sizes. Use traces to inspect executions, and use theorems only when the objective and algorithm satisfy the conditions those theorems require.
