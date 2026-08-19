# Power iteration: structure, convergence, and diagnosis

Power iteration is a deliberately simple way to approximate a matrix eigenpair. Its value is not merely that it works in favourable cases: its spectral derivation makes the assumptions, rate, and failures unusually visible. We will develop the method for real symmetric matrices, then turn the derivation into diagnostics and executable code.

<!-- section: SEC-01 -->
## Eigenpairs and why iterate

For a real square matrix $A\in\mathbb{R}^{n\times n}$, a nonzero vector $v$ is an eigenvector if some scalar $\lambda$ satisfies

$$
Av=\lambda v.
$$

The scalar is the associated eigenvalue. Excluding $v=0$ is essential: $A0=\lambda0$ holds for every $\lambda$, so the equation would convey no eigenvalue information. Algebraically, eigenvalues are roots of

$$
\det(A-\lambda I)=0,
$$

where $I$ has compatible dimension. For a small matrix this characteristic equation is informative, but explicitly forming its polynomial is usually a poor numerical strategy for a large matrix. Power iteration instead repeatedly uses matrix-vector products to estimate a selected eigenpair; that is a numerical strategy, not an algebraic replacement for the determinant identity.

The target is determined by magnitude. If the eigenvalues include $5$ and $-8$, then $-8$ is dominant because $|-8|>|5|$, even though it is not the most positive eigenvalue. Keep this distinction in view throughout.

This focus is useful when the entire spectrum is unnecessary. The iteration asks a narrower question than a full eigendecomposition: which direction is amplified most strongly in magnitude? In an applied-mathematics workflow, an inexpensive matrix-vector product may be available even when constructing a characteristic polynomial is unattractive. The aim is therefore to connect a computable recurrence to the spectral structure that governs it.

<!-- section: SEC-02 -->
## The symmetric spectral setting

Assume now that $A=A^T$ is real and symmetric. The spectral theorem gives an orthonormal basis of real eigenvectors $v_1,\ldots,v_n$. With these vectors as the columns of an orthogonal matrix $Q$,

$$
A=Q\Lambda Q^T,\qquad
\Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n).
$$

Every vector has the expansion

$$
x=\sum_{i=1}^n c_i v_i,\qquad c_i=v_i^Tx.
$$

This representation is the central analytical tool: multiplication by $A$ scales each eigenvector component independently. Order the eigenvalues by magnitude and impose the strict gap

$$
|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.
$$

Thus $\lambda_1$ is unique in magnitude. The strict first inequality is an assumption, not a cosmetic convention, and “dominant” never means largest algebraic value here.

Orthonormality makes component tracking transparent. Taking the inner product of an expansion with one basis vector eliminates all cross terms and recovers exactly its coefficient. A component attached to a negative eigenvalue changes sign under multiplication, whereas its magnitude is scaled by that eigenvalue’s absolute value. Separating sign, magnitude, and direction now prevents several common misinterpretations later.

<!-- section: SEC-03 -->
## The normalized update

Choose a nonzero $x_0$. Given $x_k$, compute

$$
y_{k+1}=Ax_k,\qquad
x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.
$$

This step requires $y_{k+1}\ne0$. Normalization controls scale and makes the iterate unit length; it does not alter the direction of $Ax_k$. Conceptually, multiplication amplifies spectral components at different rates, while normalization prevents their common scale from growing or shrinking uncontrollably. When tracing a step by hand, keep those two operations separate: first form the matrix-vector product, then calculate its Euclidean norm, then divide.

A trace also reveals what normalization cannot do. It cannot insert a component absent from the product, and it cannot decide which eigenvalue is dominant. It only rescales the current result. The useful information lies in changing proportions of eigenvector components. Writing down the unnormalized product first exposes a zero product before any invalid division.

<!-- section: SEC-04 -->
## Why a dominant direction emerges

Write $x_0=\sum_i c_i v_i$ in the orthonormal eigenbasis. Before normalization, repeated multiplication gives

$$
A^kx_0=\sum_{i=1}^n c_i\lambda_i^kv_i
=\lambda_1^k\left(c_1v_1+\sum_{i=2}^n c_i
\left(\frac{\lambda_i}{\lambda_1}\right)^kv_i\right).
$$

Suppose $c_1=v_1^Tx_0\ne0$. Under the strict magnitude gap, every subordinate ratio has magnitude below one, so its $k$th power tends to zero. Normalizing therefore leaves a direction approaching the line spanned by $v_1$.

More precisely, for real symmetric $A$, direction convergence requires a unique dominant magnitude, nonzero initial projection onto $v_1$, and no iterate for which $Ax_k=0$. Subject to these conditions, direction error generally decreases asymptotically at a rate governed by

$$
\left|\frac{\lambda_2}{\lambda_1}\right|^k.
$$

This is an asymptotic description, not an unconditional finite-iteration error bound. It also explains a practical comparison: a smaller magnitude ratio usually produces visibly faster eventual convergence.

Read the factored expression as a relative-error calculation. After removing the common factor, the dominant coefficient stays fixed while every competing coefficient receives a shrinking multiplier. The initial dominant coefficient still matters: if nonzero but tiny, subordinate components may control early iterates before the asymptotic pattern appears. The rate describes eventual geometric suppression, not every early step.

For intuition, compare magnitude ratios $0.2$ and $0.95$. Their powers both approach zero, but the first collapses far sooner. An iteration history can therefore progress slowly even while satisfying the convergence assumptions. The derivation makes that behaviour an interpretable spectral diagnostic rather than a mysterious iteration count.

<!-- section: SEC-05 -->
## Failure modes and boundaries

The derivation supplies counterexamples as readily as it supplies convergence. If $\lambda_1<0$, multiplication reverses the dominant component each time, so normalized iterates may alternate sign. This is not failure in direction: $v_1$ and $-v_1$ span the same eigendirection.

If $v_1^Tx_0=0$, however, the initial vector has no dominant component. In exact arithmetic, repeated multiplication cannot create that missing component; the iterates remain in the corresponding nondominant invariant subspace and do not converge to $v_1$. This is qualitatively different from slow convergence.

If $|\lambda_1|=|\lambda_2|$, the method need not select a unique eigenvector and may remain in, or oscillate within, the dominant invariant subspace. If instead $|\lambda_2/\lambda_1|$ is below but close to one, dominance is unique but convergence can be very slow. Equality and a small spectral gap therefore have distinct consequences.

Finally, the orthogonal decomposition above belongs to the real symmetric setting. Power iteration can apply to some nonsymmetric matrices, but an orthogonal eigenbasis is not generally available. Defective matrices, complex dominant eigenvalues, and nonnormal behaviour require additional care and lie outside this lesson’s analysis.

These cases suggest a disciplined checklist. Alternating signs can coexist with directional convergence. An exactly missing dominant projection prevents convergence to that direction in exact arithmetic. Equal dominant magnitudes remove unique directional selection, while a close but strict ratio preserves selection and merely slows it. Keeping these diagnoses separate is more useful than labeling every unusual history as failure.

<!-- section: SEC-06 -->
## Estimating the eigenvalue and deciding when to stop

A direction estimate needs a scalar partner. For any nonzero $x_k$, the Rayleigh quotient is

$$
\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.
$$

For a normalized iterate, this simplifies to $\rho(x_k)=x_k^TAx_k$. When $A$ is symmetric and $x_k$ approaches $v_1$, this quotient approaches $\lambda_1$.

Assess the approximate pair with its residual

$$
r_k=Ax_k-\rho(x_k)x_k.
$$

An exact eigenpair has zero residual, so $\|r_k\|_2$ is a meaningful computational stopping measure. Merely comparing $x_k$ and $x_{k-1}$ can be misleading when a negative dominant eigenvalue causes sign flips. A small residual measures how nearly the defining eigenvalue equation holds without requiring either sign for the eigenvector.

The quotient and residual answer different questions. The quotient proposes a scalar estimate; the residual tests its compatibility with the current vector. If the residual is not small, a stable-looking quotient alone is insufficient reason to stop. Changing the vector’s sign leaves its eigendirection and residual norm unchanged, making this diagnostic natural despite eigenvector sign ambiguity.

Interpret tolerance as a requested residual scale, not as a guarantee about every downstream error. Here, stopping means that the pair satisfies the matrix equation to that threshold. An iteration cap is still necessary because slow or nonconvergent cases may not reach the tolerance within a practical budget.

<!-- section: SEC-07 -->
## A safeguarded algorithm

The implementation below follows the mathematical sequence and makes fragile numerical cases explicit. It converts inputs to floating arrays, requires a square matrix and a compatible one-dimensional starting vector, rejects a zero start, and normalizes before iterating. A positive tolerance and positive integer iteration cap are checked before the loop. Each iteration tests for breakdown before division, then computes the Rayleigh estimate and residual. It returns the four-tuple `(eigenvalue, eigenvector, residual_norm, iteration_count)` either when the residual meets tolerance or at the cap.

```python
import numpy as np

def power_iteration(A, x0, tolerance=1e-10, max_iterations=1000):
    A = np.asarray(A, dtype=float)
    x = np.asarray(x0, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("A must be square")
    if x.shape != (A.shape[0],):
        raise ValueError("x0 has incompatible dimensions")
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    if not isinstance(max_iterations, (int, np.integer)) or isinstance(max_iterations, (bool, np.bool_)) or max_iterations <= 0:
        raise ValueError("max_iterations must be a positive integer")
    x_norm = np.linalg.norm(x)
    if x_norm == 0:
        raise ValueError("x0 must be non-zero")
    x = x / x_norm

    for iteration in range(1, max_iterations + 1):
        y = A @ x
        y_norm = np.linalg.norm(y)
        if y_norm == 0:
            raise RuntimeError("power iteration broke down because A @ x is zero")
        x = y / y_norm
        eigenvalue = float(x @ (A @ x))
        residual = A @ x - eigenvalue * x
        residual_norm = float(np.linalg.norm(residual))
        if residual_norm <= tolerance:
            return eigenvalue, x, residual_norm, iteration
    return eigenvalue, x, residual_norm, max_iterations

A_test = np.array([[4.0, 1.0], [1.0, 2.0]])
result = power_iteration(A_test, np.array([1.0, 1.0]))
assert abs(result[0] - (3.0 + np.sqrt(2.0))) < 1e-8
assert result[2] <= 1e-10
print(result)
```

Notice the logical order around breakdown: compute $y$, check $\|y\|_2$, and only then divide. The iteration cap is a fallback rather than evidence of convergence; inspect the returned residual when the cap is reached.

When adapting the function, preserve the relation between checks and return semantics. Shape and starting-vector errors are rejected before iteration. A zero product raises a breakdown error before normalization. Successful termination always returns the same four kinds of information, allowing a caller to distinguish an early residual stop from exhaustion of the cap. That consistency is itself an implementation diagnostic.

<!-- section: SEC-08 -->
## Worked consolidation

Consider

$$
A=\begin{pmatrix}4&1\\1&2\end{pmatrix},\qquad x_0=\begin{pmatrix}1\\1\end{pmatrix}.
$$

The matrix is real symmetric, and its exact eigenvalues are

$$
3+\sqrt2\qquad\text{and}\qquad3-\sqrt2.
$$

The first has larger magnitude, and the supplied start has a nonzero component in its eigendirection. One hand step gives $Ax_0=(5,3)^T$, hence $x_1=(5,3)^T/\sqrt{34}$. Subsequent normalized products increasingly align with the dominant eigenvector. Running the code estimates $3+\sqrt2$ and reports a small residual; the eigenvector may appear with either sign.

Use this example as a compact diagnostic template. First verify the structural assumptions and the starting projection. Then trace multiplication and normalization. Finally pair the Rayleigh estimate with the residual rather than trusting iteration count alone. The spectral expansion explains what should happen, while the residual tests what the computed pair currently satisfies.

For a final self-check, explain each observed feature twice: once from the recurrence and once from the spectral expansion. The recurrence states what the program calculates. The expansion predicts selection of the dominant direction and relates speed to the eigenvalue ratio. Agreement between those views, together with a small residual, yields an interpreted approximate eigenpair rather than a bare numerical answer.

Before accepting the result, compare the estimated eigenvalue with the exact dominant value and confirm that the residual is below tolerance. Then inspect the returned iteration count: it records computational effort, not accuracy by itself. Repeating the first matrix-vector product by hand provides an independent check on orientation, normalization, and the connection between theory and implementation for this example specifically.
