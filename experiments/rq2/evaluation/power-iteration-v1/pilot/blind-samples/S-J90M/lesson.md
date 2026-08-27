# Power Iteration for Modal-Analysis Thinking

Power iteration is a way to estimate an eigenpair using repeated matrix–vector products rather than solving for every eigenvalue at once. In mechanical engineering, an idealised modal-analysis example gives a useful mental model: a vector can represent a combination of mode shapes, and a matrix can transform that combination. The example is only a bridge to the mathematics. Not every engineering eigenproblem is symmetric, and not every one is solved appropriately by basic power iteration.

By the end of this lesson, you should be able to trace the update, explain why one eigendirection becomes prominent, judge an approximation with a residual, recognise failure conditions, and read a guarded NumPy implementation.

<!-- section: SEC-01 -->
## Eigenpairs and why iteration is useful

Let $A\in\mathbb{R}^{n\times n}$. A non-zero vector $v\in\mathbb{R}^n$ is an eigenvector when there is a scalar $\lambda$ such that

$$
Av=\lambda v.
$$

The scalar $\lambda$ is the eigenvalue associated with $v$. The condition $v\ne0$ matters: $A0=\lambda0$ for every $\lambda$, so the zero vector carries no eigenvalue information. In a modal picture, the eigenvector is a mode shape and the eigenvalue is the associated scaling quantity, but the algebraic definition does not depend on that interpretation.

Eigenvalues can also be characterised by the characteristic equation

$$
\det(A-\lambda I)=0,
$$

where $I$ is the identity matrix of compatible size. For a small matrix this equation can be useful for checking an answer. For a large matrix, explicitly forming a characteristic polynomial is usually a poor numerical strategy. Power iteration instead uses repeated matrix–vector products to estimate a selected eigenpair; this is a numerical strategy, not an exact algebraic equivalence to forming that polynomial.

The target is the eigenvalue of largest magnitude, not necessarily the most positive eigenvalue. For example, between $5$ and $-8$, the dominant eigenvalue by magnitude is $-8$. This distinction will matter when interpreting signs and convergence.

<!-- section: SEC-02 -->
## The symmetric spectral setting

The cleanest convergence explanation assumes that $A=A^T$ is real and symmetric. The spectral theorem then gives an orthonormal basis of real eigenvectors. If the eigenvectors are the columns of $Q$, then

$$
A=Q\Lambda Q^T,
\qquad
\Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n).
$$

Every vector $x$ can be decomposed into these eigendirections:

$$
x=\sum_{i=1}^n c_i v_i,
\qquad c_i=v_i^T x.
$$

The coefficient $c_i$ measures the component of $x$ in direction $v_i$. For a mechanical interpretation, think of an initial displacement or velocity as a combination of idealised mode shapes. The orthonormal expansion lets us track how each component is scaled. This is specifically a real-symmetric setting; the orthogonal decomposition should not be extended automatically to arbitrary non-symmetric matrices.

Order the eigenvalues by magnitude:

$$
|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.
$$

The strict first inequality means that $\lambda_1$ is unique in magnitude. “Dominant” therefore means largest absolute value, not largest algebraic value.

<!-- section: SEC-03 -->
## The normalised power update

Choose a non-zero initial vector $x_0$. Each power-iteration step first applies the matrix and then controls the scale:

$$
y_{k+1}=Ax_k,
\qquad
x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.
$$

The multiplication changes the vector according to the matrix. Normalisation divides by the Euclidean norm, so it changes the scale but not the direction, provided $y_{k+1}\ne0$. Consequently, every successful new iterate has unit 2-norm. The direction is the important quantity when estimating an eigenvector; otherwise the magnitude could grow or shrink rapidly as powers of $|\lambda_1|$ are applied.

For a two-component mode mixture, the practical trace is therefore: compute the transformed vector, calculate its norm, divide every component by that norm, and use the result as the next input. A zero initial vector is invalid, and a zero transformed vector must be detected before division.

<!-- section: SEC-04 -->
## Why the dominant direction survives

Using the symmetric eigenbasis, write $x_0=\sum_i c_i v_i$. The unnormalised sequence is

$$
A^k x_0
=\sum_{i=1}^n c_i\lambda_i^k v_i
=\lambda_1^k\left(c_1v_1+\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^k v_i\right).
$$

Here $c_1=v_1^Tx_0$. If $c_1\ne0$ and $|\lambda_1|>|\lambda_2|$, each subordinate ratio has magnitude below one and its $k$th power tends to zero. The common factor $\lambda_1^k$ affects scale and possibly sign, while the bracket increasingly reflects the dominant eigendirection.

Thus, for a real symmetric matrix, a unique dominant magnitude, a non-zero initial projection onto $v_1$, and no iterate with $Ax_k=0$ imply that direction error generally decreases asymptotically at a rate governed by

$$
\left|\frac{\lambda_2}{\lambda_1}\right|^k.
$$

This is an asymptotic rate, not an unconditional finite-iteration error bound. A smaller ratio generally means faster asymptotic alignment; a ratio close to one means that many updates may be needed.

<!-- section: SEC-05 -->
## Failure modes and scope boundaries

A negative dominant eigenvalue can make successive normalised iterates alternate sign. That is not, by itself, failure: $v_1$ and $-v_1$ represent the same eigendirection. This is why comparing vector entries directly can be misleading.

There is a more fundamental failure when $v_1^Tx_0=0$. The initial vector then has no component in the dominant eigendirection. In exact arithmetic, multiplication by $A$ cannot create a component that is absent from this eigenbasis expansion, so the iteration will not converge to $v_1$. This is not merely ordinary slow convergence.

If $|\lambda_1|=|\lambda_2|$, a unique dominant eigenvector need not be selected. If the magnitudes are separated but $|\lambda_2/\lambda_1|$ is close to one, convergence can instead be very slow. These cases must not be conflated.

Finally, power iteration applies to some non-symmetric matrices, but the clean orthogonal decomposition and the convergence explanation used here are not generally available there. Defective matrices, complex dominant eigenvalues, and non-normal behaviour require additional care and are outside this lesson’s scope. Treat the modal-analysis setting as an idealised pedagogical bridge, not as a claim about every engineering eigenproblem.

<!-- section: SEC-06 -->
## Rayleigh estimates and residual-based stopping

Once an iterate has been computed, estimate its eigenvalue with the Rayleigh quotient

$$
\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.
$$

If $x_k$ is normalised, then $x_k^Tx_k=1$ and the quotient reduces to $x_k^TAx_k$. For a symmetric matrix, as $x_k$ approaches $v_1$, this estimate approaches $\lambda_1$. The denominator must be retained for an unnormalised vector.

A more informative quality check is the eigenpair residual

$$
r_k=Ax_k-\rho(x_k)x_k.
$$

An exact eigenpair has zero residual. Therefore $\|r_k\|_2$ measures the remaining mismatch in the defining relation and provides a sensible computational stopping measure. It is preferable to relying only on successive-vector similarity because a negative dominant eigenvalue can cause sign flips even while the eigendirection is stable. A practical stopping decision should report the tolerance used and the residual value rather than claiming exactness from a finite calculation.

<!-- section: SEC-07 -->
## A guarded implementation

The following implementation mirrors the mathematics. It converts inputs to floating NumPy arrays, checks that $A$ is square and that $x_0$ is a compatible one-dimensional vector, rejects a zero initial vector, and normalises before iterating. Each iteration checks for a zero transformed vector before division, computes the Rayleigh estimate and residual, stops when the residual norm is at most `tolerance`, and otherwise falls back after `max_iterations` updates. The returned tuple is the eigenvalue estimate, vector, residual norm, and iteration count.

```python
import numpy as np


def power_iteration(A, x0, tolerance=1e-10, max_iterations=1000):
    A = np.asarray(A, dtype=float)
    x = np.asarray(x0, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("A must be square")
    if x.ndim != 1 or x.shape[0] != A.shape[0]:
        raise ValueError("x0 must be one-dimensional and compatible with A")
    if np.linalg.norm(x) == 0:
        raise ValueError("x0 must be non-zero")
    if tolerance <= 0 or max_iterations < 1:
        raise ValueError("tolerance must be positive and max_iterations at least 1")

    x = x / np.linalg.norm(x)
    for iteration in range(1, max_iterations + 1):
        y = A @ x
        y_norm = np.linalg.norm(y)
        if y_norm == 0:
            raise RuntimeError("power iteration broke down: A @ x is zero")
        x = y / y_norm
        eigenvalue = float(x @ A @ x / (x @ x))
        residual_norm = float(np.linalg.norm(A @ x - eigenvalue * x))
        if residual_norm <= tolerance:
            return eigenvalue, x, residual_norm, iteration
    return eigenvalue, x, residual_norm, max_iterations


A = np.array([[4.0, 1.0], [1.0, 2.0]])
result = power_iteration(A, np.array([1.0, 1.0]))
print("estimate =", result[0])
print("residual =", result[2])
print("iterations =", result[3])
```

<!-- section: SEC-08 -->
## Worked consolidation

Use $A=\begin{bmatrix}4&1\\1&2\end{bmatrix}$ and $x_0=(1,1)^T$. The matrix is real and symmetric. Its exact eigenvalues are

$$
3+\sqrt{2}\quad\text{and}\quad 3-\sqrt{2}.
$$

Because $3+\sqrt{2}$ has the larger magnitude, it is the dominant target. The initial vector is non-zero and is not orthogonal to the dominant eigendirection, so the usual convergence mechanism applies. One first normalises $(1,1)^T$, repeatedly forms $Ax_k$, normalises again, and monitors the residual. The implementation should estimate $3+\sqrt{2}$ and produce a small residual when its tolerance is reached. The eigenvector may be returned with either sign; a small residual does not require one particular sign.

For a final engineering-style reading, distinguish three questions. First, what direction is being selected? Power iteration seeks the dominant magnitude eigendirection. Second, how credible is the current pair? Inspect $\rho(x_k)$ together with $\|r_k\|_2$. Third, should the result be trusted for a particular model? Check symmetry and the spectral-gap and initial-projection assumptions; also check for breakdown and the maximum-iteration fallback. This separation prevents a plausible-looking mode shape from being treated as a guaranteed answer outside the assumptions that support it.

A useful hand-trace is to make a small table with columns for the iteration number, the unnormalised vector $y_{k+1}$, its 2-norm, the normalised vector $x_{k+1}$, the Rayleigh estimate, and the residual norm. The first two columns show the direct matrix action. The norm column makes the scale control visible, while the next column shows the direction that is actually carried forward. The last two columns separate an eigenvalue estimate from a check of the whole eigenpair. A stable-looking estimate alone is not enough: the residual tests whether the matrix action and the estimated scaling agree.

When reading the output, remember that the returned vector is a representative of a direction. If a later run reports a vector close to the negative of an earlier vector, that is compatible with the same eigendirection. Compare residuals and, where appropriate, compare directions up to sign. Also distinguish a small residual from a proof that the model satisfies the symmetric assumptions. The residual describes the computed pair for the supplied matrix; the assumptions explain why the iteration was expected to approach the selected target.

As a short self-check, explain why replacing the residual test with only $\|x_{k+1}-x_k\|_2$ can be unreliable when the dominant eigenvalue is negative. Then state the three key convergence requirements in your own words: a strict dominant magnitude, a non-zero starting projection onto its eigenvector, and no zero matrix–vector iterate. Finally, identify which implementation guard would respond to each of these inputs: a non-square matrix, a zero initial vector, and an iteration whose transformed vector is zero. These checks connect the mathematical conditions to decisions that a numerical program can actually make.

The same checklist is useful before reporting a result from a larger model. Confirm that the input dimensions describe one square matrix and one compatible vector, and record the tolerance and iteration limit. During the run, look for a breakdown rather than allowing a division by zero to pass unnoticed. At the end, report the estimate, the residual norm, and the iteration count together. If the maximum is reached, describe that outcome accurately as a fallback result rather than silently presenting it as tolerance-certified. This reporting habit makes the numerical calculation easier to audit and keeps the computational conclusion aligned with the mathematical conditions.
