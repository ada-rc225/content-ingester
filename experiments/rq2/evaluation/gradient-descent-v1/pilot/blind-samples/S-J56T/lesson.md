# Gradient Descent: From an Update Rule to Its Guarantees

Gradient descent is an iterative method for minimizing a differentiable function. Its update is compact enough to fit on one line, but reading that line responsibly requires more than memorizing a minus sign. We need to separate the algorithm from the assumptions used to analyze it, understand what the step size controls, and recognize exactly what a convergence statement does and does not promise.

You can view the iterate as program state: compute a gradient from the current state, use it to produce the next state, and record diagnostics. A machine-learning loss is one possible motivation for the objective, but it is only a bounded mathematical model here. Real production training objectives need not be convex, and basic full-batch gradient descent is not a complete training system.

<!-- section: SEC-01 -->
## The optimisation problem and stationarity

We begin with the unconstrained problem

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where $f:\mathbb{R}^d\to\mathbb{R}$ is at least continuously differentiable, written $f\in C^1$. The vector $x$ is the decision variable, and $f(x)$ is the scalar objective value. “Unconstrained” matters: every vector in $\mathbb{R}^d$ is in the domain of the optimization problem. Adding restrictions on $x$ would define a different problem setting.

This formulation separates the representation of a state from the score assigned to it. In a computer program, the state can be stored as a length-$d$ array, while the objective behaves like a function that accepts that array and returns one real number. Differentiability adds a gradient query to that interface. The mathematical problem asks for a state with minimum objective value; it does not say that simply evaluating the interface reveals that state directly. Iteration becomes relevant because the program can use local derivative information to construct a sequence of candidate states.

The gradient

$$
\nabla f(x)=\begin{bmatrix}
\frac{\partial f}{\partial x_1}(x)&\cdots&\frac{\partial f}{\partial x_d}(x)
\end{bmatrix}^{\mathsf T}
$$

collects the first partial derivatives at $x$. It is the local first-order information that gradient descent will query.

Suppose $x^*$ is a local minimizer and $f$ is differentiable at $x^*$. A necessary first-order condition is

$$
\nabla f(x^*)=0.
$$

Such a point is called stationary. The direction of this implication is important: a differentiable local minimizer must be stationary. Stationarity alone is not sufficient to conclude that a point is a minimum without additional assumptions. Thus a small gradient can be a useful state diagnostic, but the equation $\nabla f(x)=0$ by itself does not classify the point.

When inspecting a candidate solution, keep three statements separate. “This point is a local minimizer” is a property of nearby objective values. “The function is differentiable here” is a regularity assumption. “The gradient vanishes here” is the necessary conclusion obtained when the first two statements both hold. Reversing that reasoning would add a claim not supplied by the first-order condition. This disciplined direction of implication will matter later, when convexity is introduced as an additional assumption that changes what stationarity can tell us.

For the simple objective $f(x_1,x_2)=\tfrac12(x_1^2+4x_2^2)$, the gradient is $(x_1,4x_2)^{\mathsf T}$, so the origin is stationary. This example will provide a transparent state trace; it does not turn the necessary condition into a general sufficiency claim.

<!-- section: SEC-02 -->
## The gradient-descent update

Choose an initial state $x_0\in\mathbb{R}^d$ and positive step sizes $\alpha_k$. Gradient descent performs

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),
\qquad k=0,1,2,\ldots.
$$

The evaluation point and sign are part of the algorithm. The gradient is evaluated at the current iterate $x_k$, not at a future or look-ahead point, and its positive multiple is subtracted. One iteration can therefore be read as a state transition with three values worth tracing: the current objective, the current gradient, and the accepted next state.

Indexing makes this data flow precise. At iteration $k$, both $x_k$ and the gradient computed from it are available before $x_{k+1}$ is formed. Once the assignment is complete, the new vector becomes the current state for the next iteration. If an implementation overwrites the vector before computing the recorded gradient, its log no longer corresponds to the displayed update. Likewise, changing subtraction to addition changes the state transition itself. These are algorithm-definition checks, independent of any later theorem about how quickly a valid trace converges.

In pseudocode, the basic loop is:

```text
x <- initial point
for k = 0, 1, 2, ...:
    g <- gradient evaluated at x
    choose a positive step alpha
    x <- x - alpha * g
```

The following self-contained NumPy program applies that update to the two-dimensional objective introduced above. The fixed positive step is illustrative; the assumptions supporting particular constant steps come in the next section.

```python
import numpy as np

def objective(x):
    return 0.5 * (x[0] ** 2 + 4.0 * x[1] ** 2)

def gradient(x):
    return np.array([x[0], 4.0 * x[1]], dtype=float)

x = np.array([2.0, -1.0], dtype=float)
alpha = 0.2

for k in range(6):
    g = gradient(x)
    print(f"k={k}, x={x}, f={objective(x):.6f}, ||g||={np.linalg.norm(g):.6f}")
    x = x - alpha * g
```

The trace lets you verify that each printed gradient belongs to the state printed on the same line and that the update creates the following state. A decreasing objective in this one run is evidence about the run, not yet a general guarantee.

The step size and gradient have different roles. The gradient supplies the vector used by the transition, while the positive scalar controls how far the state moves along its negative. Positivity alone is part of the update specification, but it does not say that every positive value has desirable behavior for every differentiable objective. This is why the loop can be implemented before it is analyzed, yet the implementation should not advertise a convergence guarantee until the relevant objective assumptions and step rule have been stated.

<!-- section: SEC-03 -->
## Smoothness, descent, and a constant step

To connect a local gradient to a controlled change in the objective, assume $f$ is $L$-smooth for some $L>0$. This means its gradient is $L$-Lipschitz in the Euclidean norm:

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|,
\qquad \text{for every }x,y\in\mathbb{R}^d.
$$

This condition limits how rapidly the gradient can change between two states. It is a statement about differences of gradients, not a claim that the function values themselves are Lipschitz.

Read the quantifiers as part of the definition. One constant must bound the gradient change for every pair of points in the domain. Observing a small change along a few iterates is therefore not the same as establishing global smoothness. Conversely, the definition does not require gradients to be equal or constant; it allows them to vary, but controls that variation relative to the Euclidean distance between the two inputs. The constant supplies the scale used in the step statements below.

An $L$-smooth function obeys the Descent Lemma, the quadratic upper bound

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle
+\frac{L}{2}\|y-x\|^2,
\qquad \text{for every }x,y\in\mathbb{R}^d.
$$

The inequality is an upper bound, and its quadratic coefficient is $L/2$. Substitute one gradient-descent transition, $y=x-\alpha\nabla f(x)$, into this bound. Direct simplification gives

$$
f\bigl(x-\alpha\nabla f(x)\bigr)
\leq f(x)-\alpha\left(1-\frac{L\alpha}{2}\right)
\|\nabla f(x)\|^2.
$$

This calculation exposes the role of the step. Under $L$-smoothness, if $0<\alpha<2/L$ and the current gradient is nonzero, the term subtracted on the right is positive. The bound therefore certifies a decrease for that transition. It does not, by itself, establish one of the later convergence rates.

The substitution is also a useful way to audit the signs. The inner-product term contributes a negative multiple of the squared gradient norm because the proposed displacement points along the negative gradient. The quadratic term contributes a positive multiple because it contains the squared length of that same displacement. Their combination produces the factor in parentheses. If either the update sign or the coefficient in the Descent Lemma were altered, this reasoning would no longer match the displayed bound.

A constant-step implementation sets $\alpha_k=\alpha$ for every iteration. When $L$ is known, a common choice is $\alpha=1/L$. Under the usual smooth-convex assumptions, common constant choices also include $\alpha\in(0,2/L)$. Keep those qualifications attached: the interval is not a universal setting for an arbitrary objective.

“Constant” describes reuse across iteration indices, not a value inferred anew from each state. Once such a step has been fixed, a trace can record it once or repeat it on every row. The mathematical justification still travels with the choice: knowing that a program used the same scalar throughout does not establish smoothness or convexity. It only establishes that the program followed the constant-step rule.

At $\alpha=1/L$, the substituted upper bound becomes especially readable:

$$
f\bigl(x-L^{-1}\nabla f(x)\bigr)
\leq f(x)-\frac{1}{2L}\|\nabla f(x)\|^2.
$$

For a diagnostic, a program can record objective values before and after an update and check the relevant upper bound. That check can reveal an implementation mismatch for a specified example. It cannot establish that an unknown objective satisfies the smoothness assumption; the mathematical assumption and the runtime observation remain distinct.

<!-- section: SEC-04 -->
## Convexity, strong convexity, and conditioning

Smoothness controls gradient variation and supplies an upper bound. Convexity supplies a different kind of structure: a global first-order lower bound. A differentiable function is convex when, for every $x,y\in\mathbb{R}^d$,

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle.
$$

The affine expression on the right lies below the function everywhere. This assumption also shows why stationarity becomes more informative in the convex setting. If $\nabla f(x)=0$, the inequality reduces to $f(y)\geq f(x)$ for every $y$, so that stationary $x$ is a global minimizer under this added assumption.

For $\mu>0$, a differentiable function is $\mu$-strongly convex when, for every $x,y\in\mathbb{R}^d$,

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle
+\frac{\mu}{2}\|y-x\|^2.
$$

The positive quadratic term strengthens the convex lower bound. Notice its sign and coefficient: it is added, and it is $\mu/2$ times the squared Euclidean distance.

The smoothness and convexity inequalities play complementary roles without being interchangeable. The Descent Lemma places a quadratic expression above the function at a comparison point, while convexity places a first-order expression below it. Strong convexity strengthens that lower expression with a positive quadratic term. Keeping “upper” and “lower” attached to the correct assumptions prevents a common reading error: neither inequality can be reversed merely because the other kind of bound is also present.

When an objective is both $L$-smooth and $\mu$-strongly convex, its condition number is

$$
\kappa=\frac{L}{\mu}\geq 1.
$$

The ratio is $L/\mu$, not its inverse. It packages the two constants into one dimensionless quantity. A value near one means the two constants are close, while a larger value means they are more separated. In the next section, $\kappa$ will appear explicitly in a contraction factor; that formula, rather than the word “conditioning” alone, determines the stated guarantee.

Conditioning is therefore not a separate update and does not modify the state transition. It summarizes constants belonging to an objective that satisfies both assumptions. Before using the ratio, check that the same objective has the stated positive smoothness and strong-convexity constants. If only convexity has been assumed, the strong-convexity constant and this condition number have not been supplied. This keeps the later comparison between general convex and strongly convex results tied to their distinct hypotheses.

<!-- section: SEC-05 -->
## Convergence guarantees and their boundaries

We can now pair algorithm settings with their assumptions. First suppose that $f$ is $L$-smooth and convex, that a global minimizer $x^*$ exists, and that gradient descent uses $\alpha_k=1/L$. Then, for every $k\geq1$,

$$
f(x_k)-f(x^*)
\leq
\frac{L\|x_0-x^*\|^2}{2k}.
$$

This is an objective-gap guarantee. The right side decreases proportionally to $1/k$ and depends on the initial squared distance to a global minimizer. It does not state the same bound for an arbitrary positive step, and it must not be detached from smoothness, convexity, existence of $x^*$, or the step $1/L$.

The two sides answer different but related questions. The left measures how far the current objective value is above the minimum objective value. The right provides an iteration-dependent ceiling constructed from the smoothness constant and the initial distance. The result does not claim that every individual objective gap equals that ceiling. It says the gap cannot exceed it under all the listed conditions. Calling the behavior sublinear or order one-over-$k$ summarizes the denominator while leaving the full bound, including its constants and assumptions, in view.

Strong convexity supports geometric contractions. If $f$ is both $L$-smooth and $\mu$-strongly convex, there are two distinct step-and-bound pairings. With

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

With the different step $\alpha=1/L$, the objective gap satisfies

$$
f(x_k)-f(x^*)
\leq
\left(1-\frac{\mu}{L}\right)^k
\bigl(f(x_0)-f(x^*)\bigr).
$$

Do not swap the two steps between the two formulas. Both results require $L$-smoothness and $\mu$-strong convexity. Since $\mu/L=1/\kappa$, a larger condition number makes the displayed objective-gap factor $1-1/\kappa$ closer to one, so that this bound contracts more slowly with $k$.

These are geometric, often called linear-rate, statements because a fixed factor is raised to the iteration count. “Linear” here does not mean that the objective gap is a straight-line function of $k$. It describes repeated multiplication by a contraction factor. The distance statement concerns squared Euclidean distance and uses the step based on both constants. The objective statement concerns function values and uses the step based on $L$. Naming the measured quantity beside the step is a compact way to prevent the two cases from being blended.

The next program checks the objective-gap inequality for one strongly convex quadratic with declared constants $L=4$ and $\mu=1$. It recomputes the theoretical right side from the initial objective value. Passing assertions show that this particular trace agrees with the bound; they are not a numerical proof of the general theorem.

```python
import numpy as np

def objective(x):
    return 0.5 * (x[0] ** 2 + 4.0 * x[1] ** 2)

def gradient(x):
    return np.array([x[0], 4.0 * x[1]], dtype=float)

L = 4.0
mu = 1.0
alpha = 1.0 / L
x = np.array([2.0, -1.0], dtype=float)
initial_gap = objective(x)  # Here x* is the zero vector and f(x*) is zero.

for k in range(1, 7):
    x = x - alpha * gradient(x)
    gap = objective(x)
    bound = (1.0 - mu / L) ** k * initial_gap
    assert gap <= bound + 1e-12
    print(f"k={k}, gap={gap:.8f}, bound={bound:.8f}")
```

This assumptions-first reading is essential when the objective is motivated as a loss function. If convexity or strong convexity is absent, these displayed convex guarantees cannot simply be cited for that objective. The state trace still implements the update, but an execution log and a theorem answer different questions.

<!-- section: SEC-06 -->
## Armijo backtracking for step selection

A constant step such as $1/L$ requires a usable value of $L$. Armijo backtracking is a bounded alternative for selecting the step at the current iterate. Choose an initial trial step $\bar\alpha>0$, a contraction factor $\eta\in(0,1)$, and a constant $c\in(0,1)$. Find the smallest integer $m\geq0$ for which

$$
\alpha_k=\eta^m\bar\alpha
$$

satisfies the sufficient-decrease condition

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)
\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
$$

The algorithm tests $m=0$ first. If the inequality fails, it increments $m$, contracts the trial step by another factor of $\eta$, and tests again. It accepts the first passing value, which enforces the smallest-nonnegative-integer rule. The inequality direction and the squared gradient norm are part of the acceptance test.

At a fixed outer iteration, the current state and its gradient remain unchanged while the inner search examines trial steps. Each trial creates a candidate using that same current gradient. Only after a candidate passes the sufficient-decrease inequality does the algorithm commit the candidate as the next state. This separation is visible in code as an inner loop nested inside the iteration loop. It also explains why recomputing the current gradient after every rejected trial would describe a different data flow from the stated rule.

```text
g <- gradient evaluated at current x
for m = 0, 1, 2, ...:
    alpha <- eta^m * initial_trial_step
    if f(x - alpha * g) <= f(x) - c * alpha * ||g||^2:
        accept alpha and stop the search
x <- x - alpha * g
```

Here is a self-contained implementation. Each outer iteration restarts from the stated initial trial step, and the trace reports how many contractions were needed.

```python
import numpy as np

def objective(x):
    return 0.5 * (x[0] ** 2 + 4.0 * x[1] ** 2)

def gradient(x):
    return np.array([x[0], 4.0 * x[1]], dtype=float)

x = np.array([2.0, -1.0], dtype=float)
bar_alpha = 1.0
eta = 0.5
c = 1e-4

for k in range(6):
    g = gradient(x)
    m = 0
    while True:
        alpha = (eta ** m) * bar_alpha
        candidate = x - alpha * g
        if objective(candidate) <= objective(x) - c * alpha * np.linalg.norm(g) ** 2:
            break
        m += 1
    print(f"k={k}, f={objective(x):.8f}, alpha={alpha:.6f}, contractions={m}")
    x = candidate
```

The printed step is selected by the acceptance condition, not by a convergence-rate formula. Backtracking changes how the step is obtained; the accepted state still uses the same current-gradient update. Together, the constant-step and backtracking views illustrate a useful separation in algorithm reasoning: specify the state transition, state the assumptions beside any guarantee, and use traces to inspect implementation behavior without promoting a single run into a theorem.

When reading the final trace, treat the contraction count as an explanation of the accepted step: zero means the initial trial passed, while a positive count means that many powers of the contraction factor were applied. The listed parameter values illustrate the required ranges but are not a universal prescription. What is authoritative in the procedure is the positive initial trial, both open-interval parameter conditions, the search from the smallest nonnegative integer, and the exact sufficient-decrease test. Those pieces complete the step-selection rule without changing the gradient-descent transition it serves.
