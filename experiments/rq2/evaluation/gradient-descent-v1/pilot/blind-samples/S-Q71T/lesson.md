# Gradient Descent for Engineering Model Calibration

Gradient descent is a first-order optimisation method for reducing an objective by repeatedly moving in the direction of steepest local decrease. In mechanical engineering, a useful idealised setting is calibration: a model has adjustable parameters, measurements define a mismatch or energy-like objective, and the task is to find parameter values that make that objective small. The mathematics below applies to the stated assumptions, not automatically to every engineering design or calibration problem. In particular, an engineering objective may be nonconvex, a stationary point need not be a minimum, and gradient descent is not universally appropriate.

This lesson develops the objective, the update, step-size reasoning, convexity assumptions, convergence rates, and a bounded backtracking alternative. Keep an iteration table while working: record the iteration number, parameter vector, objective value, gradient, step size, and stopping quantity. That table connects the equations to the numerical behaviour of a calibration calculation.

<!-- section: SEC-01 -->
## 1. Formulating an objective and recognising stationarity

Suppose a parameter vector $x\in\mathbb{R}^d$ describes an idealised engineering model. An unconstrained differentiable optimisation problem has the form

$$
\min_{x\in\mathbb{R}^d} f(x),
$$

where $f:\mathbb{R}^d\to\mathbb{R}$ is at least continuously differentiable, written $f\in C^1$. For example, $f(x)$ could represent a scaled squared mismatch between predicted and measured responses for a fixed experiment. This is a framing example: it does not assert that every calibration objective has this form or that its parameters are physically unconstrained.

The goal is to find a parameter vector with a small objective value, or more specifically a minimiser when the assumptions justify discussing one. The gradient $\nabla f(x)$ collects the first partial derivatives. It indicates the local direction in which the objective increases most rapidly under the Euclidean inner product. Consequently, $-\nabla f(x)$ is the local steepest-descent direction. This directional interpretation is local; it does not by itself establish a globally best direction or a guaranteed physical interpretation.

A necessary first-order condition is the following. If $x^*$ is a local minimiser of a differentiable $f$, then

$$
\nabla f(x^*)=0.
$$

This is a stationarity condition, not a sufficient condition for a minimum. A differentiable function can have zero gradient at a local maximum or at a saddle point. In an engineering calculation, therefore, a small gradient is evidence of stationarity only; it is not by itself evidence that the calibrated model is globally or physically optimal. Additional assumptions, checks, or domain knowledge are needed for that stronger conclusion.

For a one-parameter illustration, let $f(q)$ measure an idealised mismatch as a function of a scalar stiffness parameter $q$. At an interior differentiable local minimum $q^*$, $f'(q^*)=0$. The equation tells us what a candidate solution must satisfy, while gradient descent supplies a procedure for approaching such a candidate from an initial value.

<!-- section: SEC-02 -->
## 2. The gradient-descent update and an iteration trace

Start from an initial point $x_0\in\mathbb{R}^d$. Given positive step sizes $\alpha_k$, standard gradient descent uses

$$
x_{k+1}=x_k-\alpha_k\nabla f(x_k),\qquad k=0,1,2,\ldots.
$$

The gradient is evaluated at the current iterate $x_k$, and the subtraction sign moves against the local increase direction. The step size controls how far the method travels in that direction. A positive step size is part of the rule. This is not a look-ahead update: no gradient at a future iterate is used.

For a calibration interpretation, each row of an iteration table can be read as a proposed parameter adjustment. First evaluate the current model mismatch $f(x_k)$ and sensitivity $\nabla f(x_k)$. Then multiply the sensitivity by $\alpha_k$, subtract that vector from $x_k$, and evaluate the new mismatch. A decrease in the objective is useful evidence that the chosen step is behaving as intended, but one successful decrease does not prove convergence.

The following small, deterministic example uses an objective with a known gradient. It demonstrates the mechanics of the update and prints a traceable history. The variables can be read as two idealised calibration parameters; the example is not a claim about a particular machine or material.

```python
import numpy as np

"""The two-parameter objective is f(x) = 0.5 * ||x - target||^2."""
x = np.array([2.0, -1.0])
target = np.array([0.5, 1.0])
alpha = 0.25

for k in range(6):
    error = x - target
    value = 0.5 * np.dot(error, error)
    gradient = error
    print(f"k={k}, x={x}, f={value:.6f}, grad={gradient}")
    x = x - alpha * gradient
```

When you inspect the output, verify the sign and the current-iterate evaluation. The objective values should decrease for this example because its simple quadratic structure is compatible with the selected step. That observation belongs to this example; it is not a universal guarantee for arbitrary engineering objectives.

<!-- section: SEC-03 -->
## 3. Smoothness, the descent bound, and constant steps

A step-size argument needs a way to control how rapidly the gradient changes. A continuously differentiable function $f:\mathbb{R}^d\to\mathbb{R}$ is $L$-smooth, with $L>0$, when its gradient is Lipschitz with respect to the Euclidean norm:

$$
\|\nabla f(x)-\nabla f(y)\|\leq L\|x-y\|,\qquad\forall x,y\in\mathbb{R}^d.
$$

This is a statement about gradient differences, not about the function value itself being Lipschitz. In practical model work, $L$ can be viewed as a bound on how abruptly the sensitivity changes across parameter space, when such a bound is justified. It is an assumption to assess, not a property to assume merely because the model is engineering-related.

Under $L$-smoothness, the Descent Lemma gives the quadratic upper bound

$$
f(y)\leq f(x)+\langle\nabla f(x),y-x\rangle+\frac{L}{2}\|y-x\|^2.
$$

The inequality holds for all $x,y\in\mathbb{R}^d$. The first-order term describes the local linear prediction, while the quadratic term limits the error in that prediction. Substituting the gradient-descent trial point $y=x-\alpha\nabla f(x)$ makes the negative linear contribution compete with a positive quadratic contribution. This is why a step that is too large can lose the descent behaviour suggested by the local gradient.

A constant-step scheme sets $\alpha_k=\alpha$. When $L$ is known, a common choice is $\alpha=1/L$. Under the usual smooth-convex assumptions, another stated choice is $\alpha\in(0,2/L)$. The interval must retain those assumptions; it is not a universal permission for any differentiable objective. In an engineering workflow, scaling, units, and the reliability of the estimate for $L$ matter. A conservative step may make progress slowly, while an overly large step can produce oscillation or increasing objective values.

For an iteration table, compare $f(x_{k+1})$ with $f(x_k)$ and record the step. If the observed trend disagrees with the expected bound, investigate the smoothness assumption, gradient calculation, parameter scaling, and step size rather than silently interpreting the result as convergence.

<!-- section: SEC-04 -->
## 4. Convexity, strong convexity, and conditioning

Smoothness controls an upper model for change. Convexity supplies a complementary global lower model. A differentiable function is convex when, for all $x,y\in\mathbb{R}^d$,

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle.
$$

The tangent-plane expression on the right is therefore a global lower bound. If a convex objective has a stationary point, the global structure helps connect that point to minimisation. This statement still depends on convexity; the fact that a problem comes from mechanics or calibration does not establish convexity.

A function is $\mu$-strongly convex, with $\mu>0$, if, for all $x,y\in\mathbb{R}^d$,

$$
f(y)\geq f(x)+\langle\nabla f(x),y-x\rangle+\frac{\mu}{2}\|y-x\|^2.
$$

The positive quadratic term makes the lower bound stronger than ordinary convexity. Intuitively, it rules out arbitrarily flat directions in the idealised objective at the scale represented by $\mu$. It is a mathematical condition, not a statement that every physical energy landscape has one unique best design.

When the same objective is both $L$-smooth and $\mu$-strongly convex, its condition number is

$$
\kappa=\frac{L}{\mu}\geq 1.
$$

A large $\kappa$ indicates a wide separation between the upper curvature scale and the lower curvature scale. In a parameter-calibration picture, this can correspond to an objective whose level sets are elongated: one parameter combination changes the objective rapidly while another changes it slowly. Gradient descent may then make progress cautiously in the steep direction while still moving slowly in the shallow direction. This interpretation is a useful idealised representation, not a diagnostic that can replace checking the actual model.

<!-- section: SEC-05 -->
## 5. Convergence guarantees and their boundaries

The convergence statements now combine the update with explicit assumptions. First consider an $L$-smooth and convex function $f:\mathbb{R}^d\to\mathbb{R}$, a global minimiser $x^*$, and the step choice $\alpha_k=1/L$. For $k\geq1$, the objective gap satisfies

$$
f(x_k)-f(x^*)\leq\frac{L\|x_0-x^*\|^2}{2k}.
$$

This is the stated $O(1/k)$ behaviour. The right-hand side decreases as $k$ increases, but the expression also depends on $L$ and on the initial distance from the global minimiser. The guarantee is conditional: it does not apply simply because an iteration table appears to decrease, and it does not remove the need for the smoothness, convexity, minimiser, and step-size hypotheses.

Under the stronger assumptions that $f$ is $L$-smooth and $\mu$-strongly convex, two related contractions can be stated. With

$$
\alpha=\frac{2}{L+\mu},
$$

the squared distance to the minimiser obeys

$$
\|x_k-x^*\|^2\leq\left(\frac{\kappa-1}{\kappa+1}\right)^{2k}\|x_0-x^*\|^2,
$$

where $\kappa=L/\mu$. With the different step choice $\alpha=1/L$, the objective gap obeys

$$
f(x_k)-f(x^*)\leq\left(1-\frac{\mu}{L}\right)^k\bigl(f(x_0)-f(x^*)\bigr).
$$

Keep the step-size pairings attached to the bounds: the distance contraction uses $2/(L+\mu)$, while the objective-gap contraction uses $1/L$. Both require smoothness and strong convexity. A large condition number makes the factors closer to one and therefore indicates slower predicted contraction. These are asymptotic or bound-based statements under ideal assumptions, not promises about all physical experiments, noisy measurements, constraints, or nonconvex design landscapes.

Use the following exercise to test interpretation. Suppose an idealised objective is $L$-smooth and convex, has a global minimiser, and begins at a point with $\|x_0-x^*\|=3$, with $L=6$. Under the $1/L$ theorem conditions, the bound at $k=4$ is $6\cdot9/(2\cdot4)=6.75$. This is an upper bound on the objective gap, not a prediction that the actual gap equals 6.75. If strong convexity is also established with $\mu=2$, then $\kappa=3$; the strongly convex expressions may be considered, but each still requires its own stated step choice.

There are several distinctions worth making when interpreting a convergence history. An objective value can fall while the parameter vector still moves substantially, particularly when the objective is shallow in one direction. Conversely, a parameter vector can move only a little because the step is small even though the objective remains far from its minimising value. The objective gap, parameter distance, gradient norm, and change between successive objective values measure different aspects of progress. A report should identify which of these was used as a stopping criterion.

The theorem with the $1/k$ factor also contains information about initialisation. The quantity $\|x_0-x^*\|^2$ means that a starting point farther from the minimiser permits a looser bound. The theorem does not require that $x^*$ be known in order to run the algorithm, but it uses $x^*$ in the analysis. In an actual calibration problem, one may not be able to evaluate the theorem's right-hand side because the minimiser and exact objective constants are unknown. That practical limitation does not invalidate the result; it means the result is an assumption-conditioned analytical statement rather than a directly observable certificate.

Strong convexity changes the interpretation further. If $\mu$ is small compared with $L$, then $\kappa=L/\mu$ is large and the factor $1-\mu/L$ is close to one. The linear label describes geometric decay in the bound as a function of iteration count, but a linear rate is not synonymous with a fixed amount of objective decrease per iteration. The multiplicative factor acts on the current gap. Also, the distance and objective bounds in this lesson use different step sizes, so they should not be combined by substituting one step into the other formula.

For an engineering student, a useful working checklist is: define the parameter vector and objective; state whether the problem is unconstrained; verify how the gradient is computed; identify any evidence for a global smoothness bound; test whether convexity is justified; record the chosen step and its units; and inspect the iteration history. If the model includes bounds, contact conditions, discontinuities, or multiple physically plausible solutions, the unconstrained theorem may not describe the full problem. Those features should be reported rather than hidden behind a decreasing numerical trace.

<!-- section: SEC-06 -->
## 6. Armijo backtracking as a bounded step-selection extension

When a trustworthy $L$ is unavailable or a fixed step is inconvenient, the selected pathway includes Armijo backtracking. This does not change the gradient-descent direction. Choose an initial trial step $\bar{\alpha}>0$, a contraction factor $\eta\in(0,1)$, and $c\in(0,1)$. For the current iterate, test trial steps of the form

$$
\alpha_k=\eta^m\bar{\alpha},
$$

and choose the smallest integer $m\geq0$ for which

$$
f\bigl(x_k-\alpha_k\nabla f(x_k)\bigr)\leq f(x_k)-c\alpha_k\|\nabla f(x_k)\|^2.
$$

The right side requires a sufficient decrease proportional to the step length and the squared gradient norm. If the first trial fails, multiply it by $\eta$ and test again. The accepted step is positive because $\bar{\alpha}>0$ and $\eta\in(0,1)$. The smallest-accepted-$m$ rule is part of the procedure.

Here is a self-contained implementation for a quadratic calibration-style objective. It uses fixed parameters and no external data so that the acceptance decisions can be inspected.

```python
import numpy as np

center = np.array([0.5, -1.0])
def f(x):
    error = x - center
    return 0.5 * np.dot(error, error)
def grad_f(x):
    return x - center

x = np.array([3.0, 2.0])
eta = 0.5
c = 0.25
trial = 4.0
for k in range(5):
    g = grad_f(x)
    m = 0
    while True:
        alpha = (eta ** m) * trial
        candidate = x - alpha * g
        if f(candidate) <= f(x) - c * alpha * np.dot(g, g):
            break
        m += 1
    print(f"k={k}, f={f(x):.6f}, alpha={alpha:.6f}, m={m}")
    x = candidate
```

Armijo acceptance is a step-selection rule, not evidence that the objective is convex or that a global engineering optimum has been found. Read the resulting history alongside the assumptions of the earlier guarantees. A sound report should state the objective, the gradient source, the accepted steps, the stopping criterion, and which mathematical conditions were actually checked.

The Armijo test has a clear interpretation in the iteration table. The left side is the objective at the proposed next parameter vector. The right side is the current objective reduced by a specified fraction of a first-order decrease measure. The squared norm makes the required reduction vanish as the gradient becomes small, so the acceptance test is tied to the local stationarity signal. It does not compare the trial point with an unknown optimum, and it does not certify that the accepted point is globally best.

For a hand calculation, begin with $x_k$, calculate $g_k=\nabla f(x_k)$, and compute the trial candidate for $m=0$. If the inequality fails, set $m=1$ and replace the trial step by $\eta\bar{\alpha}$; continue until the smallest accepted nonnegative integer is found. Then use that accepted candidate as $x_{k+1}$. Do not change the gradient while testing the trial steps: all candidates for this iteration use the gradient evaluated at the current $x_k$. Recomputing the gradient for each rejected trial would describe a different procedure.

As a final practice task, make two short tables for the same idealised objective: one using a fixed constant step and one using Armijo backtracking. Include $k$, $x_k$, $f(x_k)$, $\|\nabla f(x_k)\|$, and the accepted step. Compare the tables without claiming that the shorter table is automatically better. Ask which assumptions are known, which are estimated, and which observations are merely empirical. In a mechanical-engineering report, this disciplined separation helps prevent a numerical method from being presented as a physical law.

To finish, explain the method in your own words: formulate the unconstrained differentiable objective, compute the current gradient, choose a positive step, update against that gradient, and distinguish observed decrease from a theorem-backed convergence claim. Then identify whether your chosen model has evidence for smoothness, convexity, or strong convexity. This separation between computation and assumptions is as important as the update itself.
