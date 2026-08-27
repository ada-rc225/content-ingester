# Gradient Descent: Structure, Steps, and Guarantees

Gradient descent is a first-order method for moving through a continuous optimisation problem. Its update is compact, but interpreting it correctly requires more than memorising a formula. We need to distinguish a necessary condition from a guarantee of optimality, connect the step to assumptions on how the gradient changes, and keep each convergence conclusion beside the hypotheses that support it. The mathematical structure will also tell us what a numerical trace does—and does not—demonstrate.

<!-- section: SEC-01 -->
## The optimisation problem and first-order stationarity

We begin with the unconstrained problem

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where $f:\mathbb{R}^d\to\mathbb{R}$ is at least continuously differentiable, written $f\in C^1$. “Unconstrained” matters: every vector in $\mathbb{R}^d$ is an admissible point. Adding a feasible set would change the problem and the appropriate optimality conditions.

The variable $x$ may be viewed as a column of $d$ real components, while $f(x)$ is a single real number to be made small. The gradient $\nabla f(x)$ is another vector in $\mathbb{R}^d$, so it can describe sensitivity in the same coordinate space as $x$. Continuous differentiability ensures that this gradient exists and varies continuously. At this stage we have not assumed convexity, strong convexity, or even the existence of a global minimiser. The problem statement and its differentiability assumption should therefore be kept separate from the stronger structures introduced later.

Suppose $x^*$ is a local minimiser and $f$ is differentiable at $x^*$. Then the necessary first-order condition is

$$
\nabla f(x^*)=0.
$$

Geometrically, the gradient contains the directional derivatives along the coordinate directions. If it were nonzero at an interior, unconstrained point, moving a sufficiently small amount along its negative direction would provide a locally decreasing direction. A differentiable local minimiser therefore cannot have a nonzero gradient.

The logical direction of this statement is essential. A local minimiser must be stationary, but a stationary point need not be a minimiser. For example, the one-dimensional function $f(x)=x^3$ has derivative zero at $x=0$, although values on one side are smaller and values on the other are larger. Thus $\nabla f(x)=0$ identifies a candidate requiring interpretation; it is not, on its own, a certificate of minimality. Later, convexity will supply additional global structure that changes what stationarity implies.

The word “local” also limits the premise. It compares $f(x^*)$ with values at points sufficiently near $x^*$, not automatically with values throughout $\mathbb{R}^d$. The conclusion is nevertheless an exact vector equation: every component of the gradient must vanish. In a calculation, a nonzero component is enough to rule out differentiable local minimality at that point. Conversely, finding all zero components only tells us that the necessary test has been passed. This careful separation between premise, necessary conclusion, and possible converse will recur when we read convergence theorems.

<!-- section: SEC-02 -->
## Turning the gradient into an iteration

Choose an initial point $x_0\in\mathbb{R}^d$ and positive step sizes $\alpha_k$. Gradient descent generates a sequence by

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),
\qquad k=0,1,2,\ldots.
$$

Three details define the method. The gradient is evaluated at the current iterate $x_k$; it is multiplied by a positive step size; and it is subtracted. The result is a new point in the same Euclidean space. A trace of the method should therefore expose at least the current point, its current gradient, the chosen step, and the resulting point. Evaluating the gradient at a future or look-ahead point would describe a different update.

Written component by component, the same update subtracts $\alpha_k$ times the corresponding partial derivative from each component of $x_k$. The gradient supplies the direction and relative component sizes, while $\alpha_k$ supplies one common positive scale. The index is temporal bookkeeping: data labelled by $k$ are available before $x_{k+1}$ is formed. Once the new vector has been formed, the gradient for the next iteration is evaluated there. This makes the recurrence traceable without introducing any information from a later iterate.

Why the negative sign? At $x_k$, the first-order change associated with a displacement $s$ is represented by $\langle\nabla f(x_k),s\rangle$. With $s=-\alpha_k\nabla f(x_k)$, this quantity is

$$
-\alpha_k\|\nabla f(x_k)\|^2,
$$

which is negative whenever the gradient is nonzero. This is a local, first-order calculation, not yet a claim that every finite step decreases $f$. A step can move beyond the region in which the local linear picture is informative. Controlling that discrepancy is the role of smoothness.

The distinction can be phrased analytically. The inner product above describes the linear contribution associated with the proposed displacement. The actual difference $f(x_{k+1})-f(x_k)$ also reflects how the gradient varies between the two points. Positivity of $\alpha_k$ makes the linear contribution nonpositive, but positivity alone places no upper bound on the omitted variation. We therefore resist reading the update formula as a stand-alone descent theorem. It defines the iteration; an assumption such as smoothness is needed to control the finite change.

For a concrete trace, consider the quadratic objective

$$
f(x)=\tfrac12 x^TQx-b^Tx,
\qquad \nabla f(x)=Qx-b,
$$

with a symmetric matrix $Q$. Starting from a supplied vector, one iteration first forms $Qx_k-b$ and then subtracts its scaled value. This example illustrates the mechanics of the update; the iteration formula by itself does not establish that the resulting sequence converges.

<!-- section: SEC-03 -->
## Smoothness, descent, and a constant step

A continuously differentiable function is $L$-smooth, for $L>0$, when its gradient is $L$-Lipschitz in the Euclidean norm:

$$
\|\nabla f(x)-\nabla f(y)\|
\leq L\|x-y\|,
\qquad \text{for every }x,y\in\mathbb{R}^d.
$$

This condition controls changes in the gradient; it is not a statement that the function values themselves are Lipschitz. Its key consequence here is the Descent Lemma. If $f$ is $L$-smooth, then for every $x,y\in\mathbb{R}^d$,

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle
+\frac{L}{2}\|y-x\|^2.
$$

The right-hand side is a quadratic upper bound around $x$. Substitute one gradient-descent step, $y=x-\alpha\nabla f(x)$, into this inequality. The linear term becomes $-\alpha\|\nabla f(x)\|^2$, while the quadratic term becomes $(L\alpha^2/2)\|\nabla f(x)\|^2$. Hence

$$
f\bigl(x-\alpha\nabla f(x)\bigr)
\leq f(x)-\alpha\left(1-\frac{L\alpha}{2}\right)
\|\nabla f(x)\|^2.
$$

Each part of this derivation has a distinct source. The subtraction direction comes from the algorithm, and the quadratic correction comes from $L$-smoothness. The factor multiplying the squared gradient norm is determined by both $L$ and $\alpha$. If the gradient vanishes, the update leaves the point unchanged. If it does not vanish, the sign of that factor determines what this particular upper bound can establish about the objective change. This is a conclusion about the displayed bound, not permission to discard the smoothness hypothesis that produced it.

This calculation makes the relation between scale and descent explicit. A constant-step method sets $\alpha_k=\alpha$ for every $k$. When $L$ is known, a common choice is $\alpha=1/L$; under the usual smooth convex assumptions, common constant choices also satisfy $\alpha\in(0,2/L)$. In particular, inserting $\alpha=1/L$ in the displayed upper bound gives

$$
f(x_{k+1})\leq f(x_k)-\frac{1}{2L}\|\nabla f(x_k)\|^2.
$$

For this choice, the amount subtracted in the upper bound is scaled by the current squared gradient norm. The statement compares two successive objective values; it is not yet the global objective-gap rate proved later. It also does not say that $1/L$ is meaningful when no valid smoothness constant has been identified. The nested logic is: smoothness gives the Descent Lemma, the update supplies a particular $y$, and the chosen step simplifies the resulting coefficient. Keeping that chain visible prevents a numerical step convention from being mistaken for an assumption-free rule.

The following self-contained computation traces that choice for a two-dimensional quadratic. Here the eigenvalues of the diagonal matrix are $1$ and $4$, so the gradient changes at scales up to $L=4$. The printed values are observations from this objective, while the preceding inequality explains the assumption-based descent statement.

```python
import numpy as np

Q = np.diag([1.0, 4.0])
b = np.array([1.0, -2.0])
L = 4.0
alpha = 1.0 / L
x = np.array([3.0, 2.0])

def objective(z):
    return 0.5 * z @ Q @ z - b @ z

def gradient(z):
    return Q @ z - b

for k in range(6):
    g = gradient(x)
    print(k, x.copy(), objective(x), np.linalg.norm(g))
    x = x - alpha * g
```

<!-- section: SEC-04 -->
## Convexity, strong convexity, and conditioning

Smoothness supplied an upper model. Convexity supplies a global lower model. A differentiable function is convex when, for every $x,y\in\mathbb{R}^d$,

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle.
$$

The affine approximation at any $x$ lies below the function everywhere. Consequently, if $x$ is stationary, the inequality reduces to $f(y)\geq f(x)$ for every $y$, so that stationary point is a global minimiser. This conclusion uses convexity; it could not be drawn from differentiability and stationarity alone.

Notice how this lower bound complements rather than duplicates the smoothness upper bound. Convexity says where the graph must lie relative to its affine approximation; smoothness says how far above that approximation it can lie through a quadratic correction. One inequality points upward from a lower model, and the other points downward from an upper model. Reversing either inequality would change its content. When both apply, they surround the function’s change with useful structure, but their constants and conclusions remain different.

For $\mu>0$, a differentiable function is $\mu$-strongly convex when, for every $x,y\in\mathbb{R}^d$,

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle
+\frac{\mu}{2}\|y-x\|^2.
$$

The positive quadratic term strengthens the convex lower bound. We can now see two distinct controls around a point: $L$-smoothness limits the function from above through a quadratic term with coefficient $L/2$, whereas strong convexity limits it from below through a quadratic term with coefficient $\mu/2$. Neither condition should be silently substituted for the other.

Strong convexity includes the same affine expression as convexity and adds a nonnegative separation term that is positive whenever $x\ne y$. The sign, the square on the norm, and the coefficient $\mu/2$ are all structural. Removing the quadratic term would return only the convex inequality; changing its sign would no longer state strong convexity. This assumption supplies the additional structure used by the later geometric contraction bounds.

If an objective is both $L$-smooth and $\mu$-strongly convex, its condition number is

$$
\kappa=\frac{L}{\mu}\geq 1.
$$

For an applied-mathematics picture, consider a quadratic with different curvature scales along different coordinate directions. The larger scale contributes to $L$, and the smaller positive scale contributes to $\mu$. Their ratio measures the disparity. The ratio is $L/\mu$, not its reciprocal. This conditioning parameter will occur directly in the contraction factor for gradient descent, so its role is quantitative rather than merely descriptive.

If the two scales are equal, the ratio is one. If the largest scale grows while the smallest remains fixed, the ratio grows. This comparison does not add a convergence result by itself; it prepares a compact way to read the rate once the theorem’s other assumptions and its specified step are present. In particular, a reported value of $\kappa$ already presupposes that the same objective has valid positive constants $L$ and $\mu$ for the two stated inequalities.

<!-- section: SEC-05 -->
## Convergence guarantees and their boundaries

We can now attach precise conclusions to precise assumptions. First suppose $f:\mathbb{R}^d\to\mathbb{R}$ is $L$-smooth and convex, $x^*$ is a global minimiser, and gradient descent uses $\alpha_k=1/L$. Then, for every $k\geq1$,

$$
f(x_k)-f(x^*)
\leq \frac{L\|x_0-x^*\|^2}{2k}.
$$

This is an objective-gap guarantee. It says that the difference between the current objective value and the minimum is bounded above by a quantity proportional to $1/k$. The numerator retains both the smoothness scale $L$ and the squared initial distance to a global minimiser. The statement does not apply merely because a numerical run appears to decrease: it requires smoothness, convexity, a global minimiser, the specified step $1/L$, and $k\geq1$.

Reading the bound at a chosen iteration requires substituting that positive integer for $k$ while leaving the numerator fixed by the problem and initial point. Doubling $k$ halves this upper bound. That observation concerns the guaranteed envelope, not an assertion that the actual objective gap equals the right-hand side at every iteration. The theorem controls function values rather than directly giving a displayed bound on $\|x_k-x^*\|$. Distinguishing the measured quantity is as important as distinguishing the assumptions.

Strong convexity gives a different form of result. Suppose $f$ is both $L$-smooth and $\mu$-strongly convex, and recall $\kappa=L/\mu$. With the constant step

$$
\alpha=\frac{2}{L+\mu},
$$

gradient descent satisfies the squared-distance contraction

$$
\|x_k-x^*\|^2
\leq
\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}
\|x_0-x^*\|^2.
$$

The step and the bound form one matched case. The ratio inside the power lies between zero and one under the stated assumptions. As $\kappa$ increases, $(\kappa-1)/(\kappa+1)$ approaches one, so the upper bound contracts more slowly. This is the explicit connection between conditioning and the selected rate.

Here the measured quantity is squared Euclidean distance to $x^*$, and the initial squared distance appears as a multiplicative scale. Increasing $k$ multiplies the envelope by another squared copy of the contraction base. This geometric dependence is what is meant by a linear convergence rate in this setting; it should not be confused with a function that decreases by the same additive amount per iteration. The exponent $2k$ belongs to the squared-distance formula and must remain attached to it.

There is also an objective-gap contraction for the strongly convex setting, paired with the different constant step $\alpha=1/L$:

$$
f(x_k)-f(x^*)
\leq
\left(1-\frac{\mu}{L}\right)^k
\bigl(f(x_0)-f(x^*)\bigr).
$$

It is important not to exchange the step sizes attached to these displayed conclusions. The squared-distance bound above uses $2/(L+\mu)$; the objective-gap bound uses $1/L$. Both require $L$-smoothness and $\mu$-strong convexity. They therefore say more than the convex $1/k$ result only because they assume more structure.

The objective contraction can also be written using conditioning because $\mu/L=1/\kappa$, but the displayed formula keeps the two structural constants visible. At each increase of $k$, its upper envelope is multiplied by $1-\mu/L$. Again, this is a bound on the objective gap, not the distance bound from the preceding case. Matching the quantity, step, assumptions, base, and exponent is a reliable way to prevent the two valid statements from being blended into an unsupported third one.

For example, with $L=4$ and $\mu=1$, the condition number is $4$. The distance-bound base is $(4-1)/(4+1)=3/5$, which is raised to $2k$ for squared distance. With step $1/L$, the objective-gap base is $1-1/4=3/4$, raised to $k$. These numbers interpret the formulas; they do not replace checking whether an objective actually satisfies the hypotheses.

<!-- section: SEC-06 -->
## Armijo backtracking for step selection

A constant step such as $1/L$ asks us to know an appropriate smoothness constant. Armijo backtracking instead tests a geometric sequence of trial steps against a sufficient-decrease inequality. Choose an initial trial step $\bar\alpha>0$, a contraction factor $\eta\in(0,1)$, and a parameter $c\in(0,1)$. At iterate $x_k$, find the smallest integer $m\geq0$ for which

$$
\alpha_k=\eta^m\bar\alpha
$$

satisfies

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)
\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
$$

The inequality compares the objective at the proposed gradient step with a required decrease measured from the current objective value. If the initial trial fails, multiplication by $\eta$ contracts it; testing continues until the first accepted member of the sequence is found. “First” is captured by the smallest nonnegative $m$. The inequality direction and the squared gradient norm are part of the rule.

The candidate list is $\bar\alpha,\eta\bar\alpha,\eta^2\bar\alpha,$ and so on. Since $m$ starts at zero, the initial trial is tested before any contraction. The same current point and current gradient occur on both sides of each acceptance test; only the trial step changes while searching at iteration $k$. After acceptance, that $\alpha_k$ is used in the standard gradient-descent update. Backtracking therefore selects the positive scale but does not change the negative-gradient direction or its current-iterate evaluation point.

This implementation applies exactly that acceptance test to the same quadratic structure, but it is self-contained and starts from its own data. The outer loop is fixed only to make a finite trace; it is not a termination claim. Each line reports the accepted step and the number of contractions for that iteration.

The parameters in the example meet their required ranges: the initial trial is positive, and both the contraction factor and sufficient-decrease parameter lie strictly between zero and one. Inside the loop, a failed inequality increases $m$ and reconstructs the trial as $\eta^m\bar\alpha$. The accepted step is then used once. Printing $m=0$ would mean that the original trial passed; a larger printed value records exactly how many geometric contractions preceded acceptance. These diagnostics describe the rule’s trace without adding a separate stopping criterion.

```python
import numpy as np

Q = np.diag([1.0, 4.0])
b = np.array([1.0, -2.0])
x = np.array([3.0, 2.0])
bar_alpha = 1.0
eta = 0.5
c = 0.25

def objective(z):
    return 0.5 * z @ Q @ z - b @ z

def gradient(z):
    return Q @ z - b

for k in range(6):
    g = gradient(x)
    m = 0
    alpha = bar_alpha
    while objective(x - alpha * g) > objective(x) - c * alpha * (g @ g):
        m += 1
        alpha = (eta ** m) * bar_alpha
    x = x - alpha * g
    print(k, alpha, m, x.copy(), objective(x))
```

The complete chain is now visible. Stationarity motivates seeking points with vanishing gradient, the update uses the negative current gradient, smoothness connects a finite step to descent, and convexity assumptions determine which global convergence statements are available. Strong convexity and conditioning sharpen that analysis, while Armijo backtracking supplies a bounded step-selection extension through an explicit acceptance test. At every stage, the conclusion is only as broad as its adjacent assumptions.
