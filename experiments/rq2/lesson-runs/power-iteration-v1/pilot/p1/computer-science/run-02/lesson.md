# Power iteration: from repeated updates to a trustworthy eigenpair

Power iteration is a compact algorithm for estimating a matrix eigenpair. The update itself is short, but using it well requires three layers of reasoning: what eigenpair it targets, why repeated multiplication reveals that target, and how to decide whether a numerical answer is credible. We will develop those layers in order and finish with executable NumPy code.

<!-- section: SEC-01 -->
## The computational target

Let \(A\in\mathbb{R}^{n\times n}\). A non-zero vector \(v\in\mathbb{R}^n\) is an eigenvector of \(A\) when a scalar \(\lambda\) satisfies

\[
Av=\lambda v.
\]

The scalar is the eigenvalue associated with \(v\). The requirement \(v\ne 0\) matters: the zero vector satisfies \(A0=\lambda 0\) for every scalar, so it cannot identify an eigenvalue. An eigenvector therefore describes a direction that a matrix-vector multiplication preserves, while the eigenvalue gives the signed scaling along that direction.

In principle, eigenvalues are roots of the characteristic equation

\[
\det(A-\lambda I)=0,
\]

where \(I\) has compatible dimension. For a large matrix, explicitly forming that polynomial is usually a poor numerical strategy. Power iteration takes a different computational route: it uses repeated matrix-vector products to estimate a selected eigenpair. This is a numerical strategy, not an algebraic claim that iteration and the determinant equation are identical operations.

The selected target is the eigenvalue of largest **magnitude**. “Largest” does not mean most positive. If two eigenvalues are \(5\) and \(-8\), then \(-8\) is dominant because \(|-8|>|5|\). That distinction will also explain why the signs of successive vectors can alternate.

A useful way to check the definition is to imagine passing an exact eigenvector into a matrix-vector routine. Its output must be a scalar multiple of its input: the data may be stretched, shrunk, or sign-reversed, but it stays on one line through the origin. A general input vector does not have this property. Power iteration is designed to make its evolving state align with a particular preserved direction, rather than to calculate every eigenpair. Keep that limited objective in mind when reading the later stopping test.

<!-- section: SEC-02 -->
## A setting where the mechanism is visible

The clean explanation begins with a real symmetric matrix, \(A=A^T\). The spectral theorem then supplies an orthonormal basis of real eigenvectors \(v_1,\ldots,v_n\). If these vectors are the columns of the orthogonal matrix \(Q\), then

\[
A=Q\Lambda Q^T,
\qquad
\Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n).
\]

Every vector \(x\) has the representation

\[
x=\sum_{i=1}^n c_i v_i,
\qquad c_i=v_i^T x.
\]

You can read the coefficients as the vector’s stored components in the eigenvector basis. Because the basis is orthonormal, the transpose formula extracts each component directly.

Order the eigenvalues by magnitude:

\[
|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.
\]

The strict first inequality is essential: it says that \(\lambda_1\) has a unique dominant magnitude. It is this magnitude gap, rather than algebraic ordering, that supports the convergence statement below.

This representation also gives a precise vocabulary for tracing state. The vector is not treated as an indivisible object: it is a collection of coefficients attached to eigendirections. Multiplication by \(A\) scales each coefficient by its corresponding eigenvalue. Repeating the operation repeatedly scales those same components, while orthonormality lets us reason about them separately. This component view is the bridge between the two-line update that a program executes and the convergence behavior that we want to explain.

<!-- section: SEC-03 -->
## The normalized update

Choose a non-zero initial vector \(x_0\). One iteration computes

\[
y_{k+1}=Ax_k,
\qquad
x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.
\]

The first line applies the matrix; the second rescales the result to unit 2-norm. Normalization controls scale without changing direction, which keeps repeated multiplication numerically manageable. It is defined only when \(y_{k+1}\ne0\), so an implementation must test for a zero norm before dividing. At each successful update, the useful invariant is simple: \(x_k\) has unit norm, while its direction records the accumulated effect of the matrix powers.

Trace the update as a small state machine. The current state is a valid unit vector. Matrix multiplication produces a candidate next direction. A zero candidate takes the breakdown branch; a non-zero candidate takes the normalization branch and restores the unit-norm invariant. This separation is more than coding style: normalization cannot be executed safely until the branch condition has been checked. It also distinguishes “the algorithm cannot form its next iterate” from “the algorithm has formed an iterate but has not yet met its accuracy target.”

<!-- section: SEC-04 -->
## Why a dominant direction emerges

Expand the initial vector in the symmetric eigenbasis. Before normalization, repeated multiplication gives

\[
A^k x_0
=\sum_{i=1}^n c_i\lambda_i^k v_i
=\lambda_1^k\left(c_1v_1+
\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^k v_i\right).
\]

This factorization exposes the algorithm’s mechanism. The dominant component is \(c_1v_1\), whereas every other component is weighted by a power of \(\lambda_i/\lambda_1\). If

\[
c_1=v_1^Tx_0\ne0
\]

and \(|\lambda_1|>|\lambda_2|\), then every subordinate ratio has magnitude below one. Its powers decay, so normalization increasingly reveals the dominant eigendirection.

The convergence claim must retain all its conditions. For real symmetric \(A\), suppose the dominant magnitude is unique, the initial vector has non-zero projection onto \(v_1\), and no iterate produces \(Ax_k=0\). Then the direction error generally decreases asymptotically at a rate governed by

\[
\left|\frac{\lambda_2}{\lambda_1}\right|^k.
\]

This is an asymptotic description, not an unconditional finite-step error bound. As an algorithm-design intuition, the ratio acts like a contraction factor for unwanted eigenvector components: a smaller ratio usually means faster eventual separation of the dominant direction.

You can make that comparison without guessing a fixed number of iterations. Suppose two valid symmetric cases have the required non-zero initial projection and no breakdown, but their magnitude ratios differ. At the same step \(k\), the subordinate factor with the smaller ratio has decayed further. Thus the ratio explains relative eventual speed while the initial coefficients still affect what is visible early in a run. The statement remains qualitative and asymptotic: it does not license a universal finite-step guarantee based on the ratio alone.

<!-- section: SEC-05 -->
## Failure modes and scope boundaries

A negative dominant eigenvalue can make successive normalized iterates alternate sign. That alone is not failure: \(v_1\) and \(-v_1\) describe the same eigendirection. Any diagnostic based only on \(x_{k+1}-x_k\) can therefore look poor even while directional alignment improves.

Initialization can cause a genuine failure to reach the desired direction. If \(v_1^Tx_0=0\), the initial state contains no dominant eigenvector component. In exact arithmetic, repeated multiplication cannot create that missing component, so the iterates will not converge to \(v_1\). This is different from slow convergence.

The eigenvalue configuration creates two more distinct cases. If \(|\lambda_1|=|\lambda_2|\), power iteration need not select a unique eigenvector; it may remain in or oscillate within the invariant subspace associated with the tied dominant magnitudes. If instead \(|\lambda_2/\lambda_1|\) is below but close to one, the dominant magnitude is unique, yet convergence can be very slow. A tie removes the unique target assumed above; a small gap preserves that target but reveals it gradually.

Power iteration can be applied to some non-symmetric matrices, but the clean orthogonal decomposition used here is not generally available. Defective matrices, complex dominant eigenvalues, and non-normal behavior need additional care and lie outside this lesson. Likewise, repeated multiplication can resemble a ranking computation, but this simplified iteration should not be equated with a production ranking system; such a system has additional modeling and engineering assumptions.

Before trusting a run, classify what you observe. Alternating signs with improving eigendirection alignment may be normal when the dominant eigenvalue is negative. Persistent exclusion of the desired direction can result from an exactly missing initial component. Motion inside a multi-directional dominant subspace can indicate tied magnitudes. Gradual progress can reflect a separated but small magnitude gap. These cases are not interchangeable, so changing the stopping tolerance cannot repair all of them. First check whether the assumptions define a unique reachable target; only then interpret slow progress as a convergence-rate issue.

<!-- section: SEC-06 -->
## Estimating the eigenvalue and measuring quality

Once \(x_k\ne0\) approximates an eigenvector, estimate its eigenvalue with the Rayleigh quotient

\[
\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.
\]

For the unit vectors maintained by power iteration, \(x_k^Tx_k=1\), so this simplifies to

\[
\rho(x_k)=x_k^TAx_k.
\]

For symmetric \(A\), as \(x_k\) approaches \(v_1\), this estimate approaches \(\lambda_1\). The estimate alone is not the stopping test. Pair it with the eigenpair residual

\[
r_k=Ax_k-\rho(x_k)x_k.
\]

An exact eigenpair has zero residual. Therefore \(\|r_k\|_2\) directly measures how nearly the computed pair satisfies the defining eigenvector equation. It is a meaningful computational stopping measure and avoids the sign-flip problem that affects successive-vector differences. A small residual supports stopping; it does not require choosing one particular sign for the eigenvector.

The residual also connects the mathematical specification to an executable assertion. Given the current unit vector, compute one matrix-vector product, compute its Rayleigh estimate, subtract the estimated scaling, and take the 2-norm. If that norm is no larger than the chosen positive tolerance, the approximate pair passes the algorithm’s stopping rule. If not, the run continues unless it has reached its iteration budget. Notice what is and is not asserted: the test checks the approximate eigenpair equation; it does not identify vector sign as part of correctness.

<!-- section: SEC-07 -->
## A safeguarded algorithm

The full control flow is: validate and normalize \(x_0\); compute \(y=Ax_k\); stop with a breakdown message if \(\|y\|_2=0\); normalize \(y\); compute the Rayleigh estimate and residual; return when the residual norm is at most a positive tolerance; otherwise continue until the positive iteration cap is reached. The breakdown check must precede division, and the iteration cap must remain as a fallback.

The following self-contained implementation also validates array shapes and the two iteration parameters. Its return value always contains the eigenvalue estimate, unit vector, residual norm, and iterations performed.

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
    if (not isinstance(max_iterations, (int, np.integer))
            or isinstance(max_iterations, (bool, np.bool_))
            or max_iterations <= 0):
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


A = np.array([[4.0, 1.0],
              [1.0, 2.0]])
estimate, vector, residual, iterations = power_iteration(
    A, np.array([1.0, 1.0])
)
print(f"Estimated dominant eigenvalue: {estimate:.12f}")
print("Estimated eigenvector:", vector)
print(f"Residual norm: {residual:.3e}")
print("Iterations:", iterations)
```

<!-- section: SEC-08 -->
## Consolidating the trace

For the matrix in the program, the exact eigenvalues are

\[
3+\sqrt{2}
\quad\text{and}\quad
3-\sqrt{2}.
\]

The dominant value is \(3+\sqrt{2}\), because it has the larger magnitude. Starting from \((1,1)^T\) gives a non-zero component in its eigendirection, and the matrix is real symmetric with a unique dominant magnitude. The program should therefore estimate \(3+\sqrt{2}\) and report a small residual with the default settings.

When reading the output, treat the four returned fields as a compact execution record. The estimate says which scaling is being approached; the vector represents the direction, up to sign; the residual checks the approximate eigenpair equation; and the iteration count says whether the tolerance was met early or the cap was reached. This separates an answer from evidence about its quality—the essential habit when turning a short spectral algorithm into dependable numerical computation.
