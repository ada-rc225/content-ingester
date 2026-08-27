# Gradient Descent: From an Engineering Objective to Convergence Guarantees

Gradient descent is a first-order method: it uses the value of the gradient at the current parameter vector to choose the next vector. In this lesson, an idealized calibration objective provides a concrete setting, while every guarantee will be kept beside the mathematical assumptions that make it valid. The engineering framing is deliberately limited. Real design and calibration objectives need not be convex, a stationary point need not be a physical optimum, and gradient descent is not automatically suitable for every engineering problem.

<!-- section: SEC-01 -->
## From an objective to an iterative update

Let a parameter vector be \(x\in\mathbb{R}^d\), and let the scalar \(f(x)\) measure an idealized energy or calibration mismatch. The unconstrained differentiable problem is

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where \(f:\mathbb{R}^d\to\mathbb{R}\) is at least continuously differentiable, written \(f\in C^1\). “Unconstrained” matters: the search domain here is all of \(\mathbb{R}^d\). Bounds, equality constraints, or feasibility rules would define a different problem setting.

Suppose \(x^*\) is a local minimizer and \(f\) is differentiable at \(x^*\). A necessary first-order condition is

$$
\nabla f(x^*)=0.
$$

This condition says that every first-order directional tendency vanishes at a differentiable local minimum. It is necessary, not sufficient: finding a zero gradient alone does not establish that the point is a minimum. That distinction is especially important when an objective comes from a physical model, because mathematical stationarity by itself does not certify physical relevance.

Starting from \(x_0\in\mathbb{R}^d\), gradient descent uses positive step sizes \(\alpha_k\) and the update

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),
\qquad k=0,1,2,\ldots.
$$

The gradient is evaluated at the current iterate \(x_k\), and the minus sign makes the update point opposite to it. An iteration table should therefore record the current vector, current objective, current gradient, step size, and resulting next vector. For an idealized two-parameter calibration example, take

$$
f(x)=\frac12\left[(x_1-1)^2+4(x_2+1)^2\right],
\qquad
\nabla f(x)=\begin{bmatrix}x_1-1\\4(x_2+1)\end{bmatrix}.
$$

To trace a single update, keep the roles of those quantities separate. At the initial vector \(x_0=(3,2)^T\), the current gradient is \((2,12)^T\). With the positive step \(\alpha_0=1/4\), the scaled gradient is \((1/2,3)^T\), so the next iterate is \(x_1=(5/2,-1)^T\). The calculation uses no future gradient: only after forming the new vector would the algorithm evaluate \(\nabla f(x_1)\). Repeating this bookkeeping produces a convergence history rather than one unexplained final answer. A small gradient norm can be recorded as numerical information, but the exact stationarity condition remains the vector equation \(\nabla f(x^*)=0\), with the earlier warning about necessity rather than general sufficiency.

The following block is a complete trace with a positive constant step. It recomputes the gradient from the current vector on every pass.

```python
import numpy as np

def objective(x):
    return 0.5 * ((x[0] - 1.0) ** 2 + 4.0 * (x[1] + 1.0) ** 2)

def gradient(x):
    return np.array([x[0] - 1.0, 4.0 * (x[1] + 1.0)])

x = np.array([3.0, 2.0])
alpha = 0.25

print(" k        x1        x2       f(x)    ||grad||")
for k in range(6):
    g = gradient(x)
    print(f"{k:2d}  {x[0]:9.5f} {x[1]:9.5f} {objective(x):10.6f} {np.linalg.norm(g):10.6f}")
    x = x - alpha * g
```

Read each row before mentally applying the update. In this particular sum-of-squares example, \(f(x)\geq0\), and \(f(1,-1)=0\); those observations identify its minimizer without turning stationarity into a general sufficiency claim.

<!-- section: SEC-02 -->
## Measuring change and defining smoothness

To control how the gradient changes, first recall the Euclidean norm. For \(z\in\mathbb{R}^d\),

$$
\|z\|_2=\sqrt{z^Tz},
$$

and \(\|x-y\|_2\) is the Euclidean distance between two vectors. If \(G\) is vector-valued, it is \(L\)-Lipschitz for \(L>0\) when

$$
\|G(x)-G(y)\|_2\leq L\|x-y\|_2
$$

for every pair \(x,y\) in its domain. This compares an output-vector change with an input-vector change. For example, \(G(x)=2x\) satisfies \(\|G(x)-G(y)\|_2=2\|x-y\|_2\). No optimization conclusion is contained in that vector-map example.

Apply this language to the gradient map. A continuously differentiable \(f:\mathbb{R}^d\to\mathbb{R}\) is \(L\)-smooth, with \(L>0\), if

$$
\|\nabla f(x)-\nabla f(y)\|_2
\leq L\|x-y\|_2,
\qquad \forall x,y\in\mathbb{R}^d.
$$

The left side measures change in gradient vectors. It is not a statement that bounds \(|f(x)-f(y)|\). Smoothness is an explicit assumption about how rapidly the gradient can vary; an engineering label such as “energy” does not establish it.

Two short calculations help distinguish the ingredients. First, if \(z=(3,4)^T\), then \(\|z\|_2=\sqrt{3^2+4^2}=5\); the norm turns a vector into a nonnegative scalar size. Second, for the calibration objective above, write \(d=x-y\). Its gradient difference is \((d_1,4d_2)^T\), so

$$
\|\nabla f(x)-\nabla f(y)\|_2^2
=d_1^2+16d_2^2
\leq16(d_1^2+d_2^2)
=16\|x-y\|_2^2.
$$

Taking square roots gives the required inequality with \(L=4\) for this particular objective. This verification concerns the gradient map and all pairs of points. Checking only that two sampled objective values are close would not verify the stated smoothness condition.

<!-- section: SEC-03 -->
## From smoothness to step selection

When \(f\) is \(L\)-smooth, the Descent Lemma provides the quadratic upper bound

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle
+\frac{L}{2}\|y-x\|_2^2,
\qquad \forall x,y\in\mathbb{R}^d.
$$

Insert the gradient-descent trial point \(y=x-\alpha\nabla f(x)\). Direct substitution gives

$$
f\bigl(x-\alpha\nabla f(x)\bigr)
\leq f(x)-\alpha\left(1-\frac{L\alpha}{2}\right)
\|\nabla f(x)\|_2^2.
$$

This calculation exposes the decrease mechanism supplied by smoothness: the linear change points downward, while the quadratic term limits how large a trial displacement can be. The conclusion remains conditional on \(L\)-smoothness and says nothing about objectives for which that assumption is unavailable.

The algebra can be read one piece at a time. The displacement is \(y-x=-\alpha\nabla f(x)\). Therefore the inner-product term becomes \(-\alpha\|\nabla f(x)\|_2^2\), while the quadratic term becomes \((L\alpha^2/2)\|\nabla f(x)\|_2^2\). Combining them produces the coefficient shown above; neither the minus sign nor the factor \(L/2\) may be discarded. This is why the smoothness bound is useful for step reasoning: it converts a statement about every pair \(x,y\) into an upper bound for this particular trial point.

A constant-step implementation sets \(\alpha_k=\alpha\). When \(L\) is known, a common choice is \(\alpha=1/L\). Under the usual smooth convex assumptions, another common statement is \(\alpha\in(0,2/L)\). The interval must not be treated as a universal engineering rule; it belongs with those assumptions.

Armijo backtracking is a bounded alternative for selecting a step at the current iterate. Choose an initial trial \(\bar\alpha>0\), a contraction factor \(\eta\in(0,1)\), and \(c\in(0,1)\). Starting with \(m=0\), form \(\alpha_k=\eta^m\bar\alpha\) and accept the smallest nonnegative \(m\) for which

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)
\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|_2^2.
$$

Thus the procedure tests a precisely stated sufficient-decrease inequality, contracting the positive trial step until it holds. The squared gradient norm and the direction of the inequality are essential. Here is one self-contained trace of the search and the accepted update.

```python
import numpy as np

def objective(x):
    return 0.5 * ((x[0] - 1.0) ** 2 + 4.0 * (x[1] + 1.0) ** 2)

def gradient(x):
    return np.array([x[0] - 1.0, 4.0 * (x[1] + 1.0)])

x = np.array([3.0, 2.0])
bar_alpha = 1.0
eta = 0.5
c = 1.0e-4
g = gradient(x)
m = 0

while True:
    alpha = (eta ** m) * bar_alpha
    trial = x - alpha * g
    right_side = objective(x) - c * alpha * np.linalg.norm(g) ** 2
    print(f"m={m}, alpha={alpha:.5f}, trial f={objective(trial):.6f}, bound={right_side:.6f}")
    if objective(trial) <= right_side:
        break
    m += 1

x_next = x - alpha * g
print("accepted m:", m)
print("accepted alpha:", alpha)
print("next x:", x_next)
```

Notice the order of operations: the gradient is fixed at the current iterate during this search, candidate steps shrink geometrically, and the first accepted candidate supplies the update.

When reading the printed trials, verify three facts rather than judging a step by size alone. Each \(\alpha\) is positive, each new candidate is obtained by multiplying the preceding one by \(\eta\), and acceptance compares the trial objective with the full right-hand side containing \(c\), \(\alpha\), and the squared current-gradient norm. The accepted index is the smallest one because the program tests \(m=0,1,2,\ldots\) in order and stops at the first true inequality.

<!-- section: SEC-04 -->
## Reading inner products and convex combinations

The next assumptions use inner products and convex combinations. For real vectors \(u\) and \(v\) of the same dimension, \(u^Tv\) is the scalar sum of their componentwise products. To read \(g^T(y-x)\), first form the displacement \(d=y-x\), then calculate the scalar \(g^Td\). Its sign describes the alignment of \(g\) with that displacement, but this arithmetic alone proves no convexity result.

For \(x,y\in\mathbb{R}^d\) and \(\theta\in[0,1]\), the vector \(\theta x+(1-\theta)y\) is a convex combination. A set is convex if it contains every such combination of every pair of its points. For example, with \(x=(0,0)^T\), \(y=(2,4)^T\), and \(\theta=1/4\), the combination is \((3/2,3)^T\). If \(g=(1,-1)^T\), then \(g^T(y-x)=-2\). These are definitions and computations, not yet an optimization theorem.

Work through that arithmetic in its stated order. The displacement is \(y-x=(2,4)^T\), and the scalar inner product is \(1\cdot2+(-1)\cdot4=-2\). Separately, the coefficients in the convex combination are \(1/4\) and \(3/4\): they are nonnegative and sum to one. The combination therefore lies on the segment joining the two vectors. Whether a particular set contains that entire segment is a property to check; it cannot be inferred from the word “feasible” or from one computed combination.

<!-- section: SEC-05 -->
## Convexity and its stronger form

A differentiable function \(f:\mathbb{R}^d\to\mathbb{R}\) is convex when, for every \(x,y\in\mathbb{R}^d\),

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle.
$$

The affine expression on the right is a global lower bound on the function. The inequality must hold for all pairs, not merely along one observed iteration history. If \(\nabla f(x)=0\) at a point satisfying this convexity assumption, the inequality reduces to \(f(y)\geq f(x)\) for every \(y\), so that stationary point is a global minimizer. This conclusion comes from convexity; it does not repair the earlier warning that stationarity alone is insufficient.

For \(\mu>0\), differentiable \(f\) is \(\mu\)-strongly convex when, for every \(x,y\in\mathbb{R}^d\),

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle
+\frac{\mu}{2}\|y-x\|_2^2.
$$

Strong convexity adds a positive quadratic term to the convex lower bound. It is a stronger stated assumption, not a property inferred from an objective being described as energy, mismatch, or calibration error. Keeping the assumption visible is what later permits a stronger convergence result.

Compare the two inequalities carefully. Convexity supplies the affine lower bound \(f(x)+\langle\nabla f(x),y-x\rangle\). Strong convexity retains that same bound and adds \((\mu/2)\|y-x\|_2^2\), which is nonnegative because \(\mu>0\). The quantifier “for every \(x,y\)” belongs to both definitions. An iteration plot showing decrease at a finite list of points does not establish either definition, because the definitions make global pairwise statements. In an engineering analysis, these conditions therefore need justification separate from the numerical run.

<!-- section: SEC-06 -->
## A condition ratio beside the convergence history

For positive constants satisfying \(0<\mu\leq L\), define the ratio

$$
\kappa=\frac{L}{\mu}.
$$

Dividing \(0<\mu\leq L\) by positive \(\mu\) shows that \(\kappa\geq1\). A value near one means that \(L\) and \(\mu\) are close; a larger value means they are separated by a larger multiplicative factor. For instance, \(L=12\) and \(\mu=3\) give \(\kappa=4\), while \(L=\mu\) gives \(\kappa=1\). The ratio requires \(\mu>0\); it is not finite when \(\mu=0\).

For an objective that is both \(L\)-smooth and \(\mu\)-strongly convex, this ratio is its condition number. Keep it beside an iteration table or convergence history as a label for the separation between the two constants. Do not import a matrix or spectral condition-number definition here, and do not infer a convergence rate from the ratio alone. The precise rate statements, with their hypotheses and step sizes, come next.

The ratio is dimensionless when \(L\) and \(\mu\) carry the same units, and its reading is multiplicative: \(\kappa=4\) means \(L=4\mu\). It does not mean that an objective value, a gradient norm, or a parameter error is four times another quantity. Thus a useful history keeps \(\kappa\) as contextual information and labels the actual vertical quantity independently. Only a theorem connecting that history to \(\kappa\) licenses a rate interpretation.

<!-- section: SEC-07 -->
## Reading the convergence guarantees and their limits

First consider the convex case. Let \(f:\mathbb{R}^d\to\mathbb{R}\) be \(L\)-smooth and convex, let \(x^*\) be a global minimizer, and run gradient descent with \(\alpha_k=1/L\). Then, for every \(k\geq1\),

$$
f(x_k)-f(x^*)
\leq
\frac{L\|x_0-x^*\|_2^2}{2k}.
$$

This is an objective-gap statement. Its upper bound decreases in proportion to \(1/k\), and it depends on the initial squared distance and on \(L\). It is not a guarantee about an arbitrary calibration model: smoothness, convexity, existence of a global minimizer, the particular step \(1/L\), and \(k\geq1\) are all part of the result.

The bound also clarifies what a plotted curve can and cannot show. Doubling \(k\) halves the displayed upper bound, but it does not assert that every observed objective gap exactly equals that bound. The left side is the actual gap; the right side is a guarantee above it. Neither a gradient-norm curve nor a distance curve can be substituted for the objective gap in this statement.

Now strengthen the assumptions: suppose \(f\) is both \(L\)-smooth and \(\mu\)-strongly convex, and let \(\kappa=L/\mu\). Two useful contractions must be paired with their own step sizes. With

$$
\alpha=\frac{2}{L+\mu},
$$

the squared distance to the minimizer satisfies

$$
\|x_k-x^*\|_2^2
\leq
\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}
\|x_0-x^*\|_2^2.
$$

By contrast, with \(\alpha=1/L\), the objective gap satisfies

$$
f(x_k)-f(x^*)
\leq
\left(1-\frac{\mu}{L}\right)^k
\bigl(f(x_0)-f(x^*)\bigr).
$$

These are geometric contractions under the simultaneous smoothness and strong-convexity assumptions. The first concerns squared distance and uses \(2/(L+\mu)\); the second concerns objective gap and uses \(1/L\). Swapping those pairings would change the stated theorem.

The condition number now helps you read a convergence history without becoming a guarantee on its own. In the objective-gap factor, \(1-\mu/L=1-1/\kappa\). Within this theorem, a \(\kappa\) closer to one gives a smaller contraction factor, while a larger \(\kappa\) gives a factor closer to one. That interpretation is limited to the stated smooth, strongly convex setting.

For a purely arithmetic reading, if the stated assumptions hold with \(\kappa=4\), the objective-gap factor associated with the \(1/L\) step is \(1-1/4=3/4\). The distance result instead uses the base \((4-1)/(4+1)=3/5\), raised to \(2k\), and it belongs to the \(2/(L+\mu)\) step. These numbers illustrate how to annotate two different histories; they do not make the hypotheses true for a new engineering model.

When examining any engineering iteration history, finish with three questions. Which quantity is being recorded: objective value, objective gap, gradient norm, or distance? Which step rule produced it? Which assumptions have actually been established for the model? A decreasing numerical history can be informative, but it does not manufacture convexity or strong convexity. Likewise, a stationary computed point is not automatically a physical optimum. Gradient descent offers a traceable update and precise conditional guarantees; responsible use means keeping the algorithm, the observed history, and the assumptions visibly separate.
