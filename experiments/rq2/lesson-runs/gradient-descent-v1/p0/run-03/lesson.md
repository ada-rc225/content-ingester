# Gradient Descent: From an Update Rule to Convergence Guarantees

<!-- section: SEC-01 -->
## The optimisation problem and stationarity

Gradient descent addresses an unconstrained optimisation problem of the form

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where the objective $f:\mathbb{R}^d\to\mathbb{R}$ assigns a real value to every candidate vector $x$. The word *unconstrained* matters: every vector in $\mathbb{R}^d$ is an admissible candidate. Throughout this lesson, $f$ is assumed to be at least continuously differentiable, written $f\in C^1$. Its gradient $\nabla f(x)$ therefore exists and collects the first derivatives at $x$.

A point $x^*$ is a local minimiser if its objective value is no larger than the values at all sufficiently nearby points. If $f$ is differentiable at such a point, then the first-order necessary condition is

$$
\nabla f(x^*)=0.
$$

This condition is necessary, not sufficient: a point with zero gradient is called stationary, but stationarity alone does not prove that the point is a minimum. The distinction prevents a common logical reversal. A differentiable local minimum must be stationary; an arbitrary stationary point need not be a local minimum without additional assumptions.

The gradient gives local first-order information. Its components describe how the objective changes with the components of $x$. The optimisation task is therefore linked to a measurable target: seek points where this first-order signal becomes zero while trying to reduce the objective. Gradient descent turns that motivation into a repeated update. It does not begin by claiming that every stationary point is globally best. Instead, it generates a sequence of candidate vectors and, under assumptions introduced later, allows particular descent and convergence statements to be made.

Keep the roles of the symbols separate. The vector $x$ is a candidate, $f(x)$ is its scalar objective value, and $\nabla f(x)$ is a vector evaluated at that candidate. The superscript star marks a minimiser in statements where one is assumed to exist; it is not an iteration counter. Iterations will instead use subscripts such as $x_0,x_1,x_2$. This notation lets us distinguish the point currently available from the minimiser used to state a guarantee.

A useful way to check the logic is to read the stationarity statement in two stages. First verify the hypotheses: the proposed point is a local minimiser and the objective is differentiable there. Only then conclude that its gradient vanishes. If instead you are merely told that a gradient vanishes, you have reached the conclusion of the necessary condition without establishing its hypotheses in reverse. This careful reading will matter later, because convergence formulas also have hypotheses that cannot be reconstructed from their conclusions. The optimisation problem, differentiability assumption, and stationarity condition are therefore more than notation: they establish what is being minimised and precisely what first-order information can and cannot certify on its own.

<!-- section: SEC-02 -->
## The gradient-descent update

Choose an initial point $x_0\in\mathbb{R}^d$. For positive step sizes $\alpha_k$, standard gradient descent generates

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),
\qquad k=0,1,2,\ldots.
$$

The order of operations is precise. At iteration $k$, evaluate the gradient at the current point $x_k$, multiply that vector by the positive number $\alpha_k$, and subtract the result from $x_k$. The gradient is not evaluated at a future or look-ahead point. The minus sign is also part of the rule: changing it would change the algorithm described here.

The step size controls the length of the move relative to the gradient. Positivity preserves the negative-gradient direction, but positivity by itself does not supply a convergence guarantee. Such a guarantee requires a step choice paired with assumptions about the objective. For now, the update should be read as a traceable algorithmic rule rather than a universal promise that every step will work well.

Here is a self-contained trace for one particular two-dimensional objective. The example only demonstrates how to evaluate and apply the update; it does not establish a general convergence result.

```python
import numpy as np

def objective(x):
    return 0.5 * (x[0] ** 2 + 4.0 * x[1] ** 2)

def gradient(x):
    return np.array([x[0], 4.0 * x[1]], dtype=float)

x = np.array([2.0, -1.0], dtype=float)
alpha = 0.2

for k in range(5):
    print(k, x.copy(), objective(x))
    x = x - alpha * gradient(x)
print(5, x.copy(), objective(x))
```

At the first iteration, the code computes the gradient from the original value of `x` and then replaces `x` with the new vector. Each later iteration repeats the same pattern. The printed rows make the indexing visible: the row labelled $k$ reports $x_k$ before the update producing $x_{k+1}$. Although this example uses one constant value of $\alpha_k$, the general update permits the positive step size to depend on $k$. We next identify objective assumptions that justify particular constant choices.

You can trace any stated iteration without code by keeping four entries on each line: the index, the current vector, the gradient at that vector, and the positive step size. Form the scaled gradient only after evaluating it at the current vector, then subtract it to obtain the next line. This layout exposes two frequent transcription errors: using the newly computed point inside the gradient on the same line, or adding the scaled gradient instead of subtracting it. It also clarifies the special case of a stationary current point. If the current gradient is zero, the scaled gradient is the zero vector and this update leaves the point unchanged, whatever positive step size is recorded. That observation concerns the update itself; it does not turn the stationary point into a certified minimum.

<!-- section: SEC-03 -->
## Smoothness, descent, and a constant step

A continuously differentiable objective is called $L$-smooth, for $L>0$, when its gradient is $L$-Lipschitz with respect to the Euclidean norm:

$$
\|\nabla f(x)-\nabla f(y)\|
\leq L\|x-y\|,
\qquad \text{for all }x,y\in\mathbb{R}^d.
$$

This controls changes in the gradient, not changes in the function value itself. The constant $L$ bounds how rapidly the gradient can vary as the input moves.

The central consequence used for a gradient-descent step is the Descent Lemma. If $f$ is $L$-smooth, then, for every $x,y\in\mathbb{R}^d$,

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle
+\frac{L}{2}\|y-x\|^2.
$$

This is a quadratic upper bound. Its inequality points upward from the right-hand model to $f(y)$: reversing the sign would give a different statement. To connect it to the update, set $y=x-\alpha\nabla f(x)$. Direct substitution yields

$$
f\bigl(x-\alpha\nabla f(x)\bigr)
\leq f(x)-\alpha\left(1-\frac{L\alpha}{2}\right)
\|\nabla f(x)\|^2.
$$

In particular, when $L$ is known and $\alpha=1/L$, the bound becomes

$$
f\bigl(x-\tfrac{1}{L}\nabla f(x)\bigr)
\leq f(x)-\frac{1}{2L}\|\nabla f(x)\|^2.
$$

Thus the upper bound certifies a decrease whenever the gradient is nonzero for this stated smoothness condition and step. Notice how the condition, the step, and the conclusion remain together.

A constant-step version of gradient descent sets $\alpha_k=\alpha$ at every iteration. When $L$ is known, a common choice is $\alpha=1/L$. Under the usual smooth convex assumptions, another standard statement is that the constant may be chosen from the interval $\alpha\in(0,2/L)$. That interval is not an assumption-free rule; its smooth convex qualification must travel with it.

Smoothness has so far provided an upper model and a route to objective decrease. It has not yet supplied the global geometry needed for the convergence results later in the lesson. For that purpose, we distinguish convexity from the stronger condition of strong convexity.

It helps to unpack the upper model term by term. The first term is the objective at the current point. The inner-product term records the first-order change associated with moving from the current point to the proposed point. The final squared-norm term, with coefficient one half of $L$, accounts for the permitted variation in the gradient. The lemma says that their sum is an upper bound under smoothness; it does not say that this model equals the next objective value. When the proposed displacement is the negative scaled gradient, the inner product becomes a negative squared gradient norm, while the quadratic term is positive. The step size determines their balance. The displayed substitution makes that balance explicit and explains why a step statement should always be read beside the value of $L$ and the assumptions under which it is offered.

<!-- section: SEC-04 -->
## Convexity, strong convexity, and conditioning

For a differentiable objective, convexity can be expressed by a global first-order lower bound. The function $f$ is convex if, for all $x,y\in\mathbb{R}^d$,

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle.
$$

Unlike the smoothness upper bound, this inequality places the function above its first-order expression at every pair of points. The universal quantifier is essential: the statement is global rather than a claim about just one chosen pair.

Strong convexity adds a positive quadratic term. A differentiable function is $\mu$-strongly convex, with $\mu>0$, if, for all $x,y\in\mathbb{R}^d$,

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle
+\frac{\mu}{2}\|y-x\|^2.
$$

The sign, coefficient, and squared Euclidean norm are all part of the definition. Dropping the quadratic term recovers the convex lower-bound form, whereas keeping it records the stronger assumption used by the linear convergence result below.

When one objective is both $L$-smooth and $\mu$-strongly convex, its condition number is

$$
\kappa=\frac{L}{\mu}\geq 1.
$$

The ratio is $L$ divided by $\mu$, not the reverse. It combines the upper control on gradient variation with the strength of the convex lower bound. A value near one means the two constants are close, while a larger value means $L$ is large relative to $\mu$. The convergence factors in the next section make the effect of this ratio explicit.

These definitions must not be blended into one vague notion of a “well-behaved” objective. Smoothness, convexity, and strong convexity play different roles and appear in different combinations in the guarantees. A claim that assumes only smoothness cannot silently borrow strong convexity, and a rate stated for a strongly convex objective must retain that hypothesis. Reading a theorem therefore begins by checking which of these inequalities is actually assumed.

One comparison keeps the directions straight. Smoothness supplies a quadratic upper bound, whereas convexity supplies a first-order lower bound. Strong convexity retains that lower-bound direction and adds a positive quadratic amount. Because these are statements for every pair of points, inspecting one successful gradient-descent step cannot by itself establish any of the definitions. Conversely, once the relevant properties are assumed, their constants must keep their assigned meanings: $L$ belongs to gradient smoothness, and positive $\mu$ belongs to strong convexity. The condition number records both without replacing either. Thus reporting only a condition number is meaningful here only in the simultaneous smooth and strongly convex setting in which the ratio was defined.

<!-- section: SEC-05 -->
## Convergence guarantees and their boundaries

Consider first an objective $f:\mathbb{R}^d\to\mathbb{R}$ that is both $L$-smooth and convex. Assume that a global minimiser $x^*$ exists, and run gradient descent with the constant step $\alpha_k=1/L$. Then, for every $k\geq1$,

$$
f(x_k)-f(x^*)
\leq
\frac{L\|x_0-x^*\|^2}{2k}.
$$

The quantity on the left is the objective gap. The bound says it is no larger than a constant determined by $L$ and the initial squared distance, divided by $k$. This is the stated $O(1/k)$ behaviour. It is an objective-value result under all four listed ingredients: smoothness, convexity, existence of a global minimiser, and the step $1/L$. Removing one of those hypotheses does not leave this theorem intact.

Now strengthen the objective assumption to simultaneous $L$-smoothness and $\mu$-strong convexity. Two useful contraction statements are available, and each must remain paired with its own step size. With

$$
\alpha=\frac{2}{L+\mu},
$$

gradient descent satisfies the squared-distance bound

$$
\|x_k-x^*\|^2
\leq
\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}
\|x_0-x^*\|^2,
\qquad \kappa=\frac{L}{\mu}.
$$

By contrast, with the step $\alpha=1/L$, the corresponding stated objective-gap bound is

$$
f(x_k)-f(x^*)
\leq
\left(1-\frac{\mu}{L}\right)^k
\bigl(f(x_0)-f(x^*)\bigr).
$$

Both are linear convergence statements in the optimisation sense: the relevant error bound is multiplied geometrically by a fixed factor raised to the iteration count. “Linear” here describes that geometric contraction; it does not mean that the iterates follow a straight line. The first formula controls squared distance and uses $2/(L+\mu)$. The second controls objective gap and uses $1/L$. Exchanging those labels would misstate the results.

Conditioning is visible in both factors. In the distance result the factor is built directly from $\kappa$. In the objective result, $1-\mu/L=1-1/\kappa$. As $\kappa$ becomes larger, these factors approach one, so the displayed upper bounds contract more slowly with $k$. This interpretation depends on the same smooth and strongly convex setting in which $\kappa$ was defined.

The contrast is therefore conditional rather than universal. General smooth convex structure gives the displayed inverse-$k$ objective-gap guarantee at step $1/L$. Adding positive strong convexity supports the displayed geometric contractions. If the assumptions have not been established for an objective, these particular bounds cannot be invoked merely because the gradient-descent update can still be written down.

When interpreting any of the three bounds, distinguish an upper bound from an exact trajectory. The right-hand side limits the relevant error; it need not equal the observed error at an iteration. It also carries information about the starting point. In the convex result, the initial squared distance appears in the numerator. In the strongly convex distance result, the initial squared distance is multiplied by the geometric factor. In the strongly convex objective result, the initial objective gap is multiplied instead. These different quantities should not be interchanged. To audit a proposed use of a formula, name the measured error first, then the objective assumptions, then the prescribed step, and finally the allowed indices. This sequence immediately separates the convex objective-gap result from the two strongly convex cases and prevents the attractive phrase “linear convergence” from being detached from the quantity and hypotheses it describes.

<!-- section: SEC-06 -->
## Armijo backtracking for step selection

The constant choice $1/L$ requires a value of $L$. Armijo backtracking is a bounded alternative for selecting a positive step from trial values. Choose an initial trial step $\bar\alpha>0$, a contraction factor $\eta\in(0,1)$, and a constant $c\in(0,1)$. At iteration $k$, find the smallest nonnegative integer $m$ for which

$$
\alpha_k=\eta^m\bar\alpha
$$

satisfies the sufficient-decrease condition

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)
\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
$$

The procedure starts at $m=0$, so it tests $\bar\alpha$ first. If the inequality fails, increase $m$ by one, multiply the trial step by another factor of $\eta$, and test again. Accept the first trial that satisfies the inequality. “First” is important because it implements the smallest-$m$ rule; continuing to contract after an acceptable trial would select a different member of the trial sequence.

The following block implements exactly that test for a particular objective. It is self-contained, and each call begins again with the same positive initial trial step.

```python
import numpy as np

def objective(x):
    return 0.5 * (x[0] ** 2 + 4.0 * x[1] ** 2)

def gradient(x):
    return np.array([x[0], 4.0 * x[1]], dtype=float)

def armijo_step(x, bar_alpha=1.0, eta=0.5, c=0.25):
    g = gradient(x)
    m = 0
    alpha = bar_alpha
    while objective(x - alpha * g) > objective(x) - c * alpha * np.dot(g, g):
        m += 1
        alpha = (eta ** m) * bar_alpha
    return alpha, m

x = np.array([2.0, -1.0], dtype=float)
for k in range(6):
    alpha, m = armijo_step(x)
    print(k, objective(x), alpha, m)
    x = x - alpha * gradient(x)
print(6, objective(x))
```

The `while` condition is the negation of the acceptance inequality: contraction continues only while the candidate objective value is too large. The squared gradient norm appears as `np.dot(g, g)`. Once the loop stops, the code applies the standard update using the accepted positive $\alpha_k$.

To trace backtracking by hand, make a row for each nonnegative trial index. Start with the uncontracted trial and compute both sides of the acceptance inequality using the same current point and gradient. If the candidate fails, move to the next row and contract the original trial by the stated power of the contraction factor. Stop at the first passing row and record both its index and its positive step. This trace shows the separate jobs of the parameters: the initial trial starts the sequence, the contraction factor generates smaller trials, and the constant in the sufficient-decrease test sets the right-hand comparison. All three must remain in their stated ranges. The test compares objective values, but the accepted move is still produced by the standard current-gradient update.

Backtracking changes how the step is selected; it does not change where the gradient is evaluated or the subtraction sign in gradient descent. Nor should the constant-step convergence formulas from the previous section be silently reassigned to this rule. Those formulas were stated with their particular steps and assumptions. Armijo backtracking here supplies the selected practical sufficient-decrease test, completing a traceable path from the optimisation problem, through the gradient update and its structural assumptions, to two kinds of step selection.
