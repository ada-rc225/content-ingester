# Power iteration: structure, convergence, and computation

Power iteration is a deliberately simple way to approximate one eigenpair using repeated matrix–vector products. Its value is not merely computational: in the symmetric case, its behaviour follows transparently from spectral decomposition. We will derive that mechanism, identify exactly where it can fail, and turn the mathematics into a safeguarded implementation whose residual gives a meaningful stopping decision.

<!-- section: SEC-01 -->
## Eigenpairs and the direct route

Let \(A\in\mathbb R^{n\times n}\). A nonzero vector \(v\in\mathbb R^n\) is an eigenvector if some scalar \(\lambda\) satisfies

\[
Av=\lambda v.
\]

The scalar \(\lambda\) is the associated eigenvalue. Requiring \(v\ne0\) is essential: \(A0=\lambda0\) holds for every scalar, so the zero vector supplies no eigenvalue information.

Eigenvalues are roots of

\[
\det(A-\lambda I)=0,
\]

where \(I\) has compatible dimension. This characteristic equation is useful for deriving exact answers for small matrices. For large matrices, however, explicitly forming its polynomial is usually a poor numerical strategy. Power iteration instead uses repeated matrix–vector products to estimate a selected eigenpair; this is a numerical alternative, not an algebraic replacement for the characteristic equation.

There is also a useful geometric reading of the defining equation. Applying \(A\) to an eigenvector changes its scale, and possibly its sign, but not its eigendirection. Power iteration searches for a direction with this property rather than solving simultaneously for every root of a determinant. Keep the distinction between vector and scalar explicit: the iterate approximates the vector, while a later quotient estimates the associated scalar.

<!-- section: SEC-02 -->
## Spectral structure and the target

Suppose now that \(A=A^T\) is real and symmetric. The spectral theorem gives an orthonormal basis of real eigenvectors, so

\[
A=Q\Lambda Q^T,\qquad
\Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n),
\]

with the eigenvectors as columns of the orthogonal matrix \(Q\). Every vector has the expansion

\[
x=\sum_{i=1}^n c_i v_i,\qquad c_i=v_i^Tx.
\]

Order eigenvalues by magnitude and assume a strict first gap:

\[
|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.
\]

Thus \(\lambda_1\) is uniquely dominant in magnitude. “Dominant” does not mean most positive: between eigenvalues \(5\) and \(-8\), the target is \(-8\), since \(8>5\).

The coefficient formula makes decomposition practical for reasoning. Each \(c_i\) records the signed projection of the current vector onto one orthonormal eigenvector. Consequently, the method’s initial information is entirely visible in these coefficients. The strict inequality is not decorative terminology: it creates one component whose magnitude grows relative to every other component under repeated multiplication.

<!-- section: SEC-03 -->
## The normalized update and why it works

Choose \(x_0\ne0\). At each step compute

\[
y_{k+1}=Ax_k,\qquad
x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.
\]

The denominator must be nonzero. Normalization controls scale and produces a unit vector without changing the direction of \(Ax_k\).

To expose the convergence mechanism, expand \(x_0=\sum_i c_i v_i\). Before normalization,

\[
A^kx_0=\sum_{i=1}^n c_i\lambda_i^kv_i
=\lambda_1^k\left(c_1v_1+
\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^kv_i\right).
\]

If \(c_1=v_1^Tx_0\ne0\) and the strict magnitude gap holds, every subordinate factor \(|\lambda_i/\lambda_1|^k\) tends to zero. Normalization removes the common growth or decay \(\lambda_1^k\), leaving a direction increasingly aligned with \(v_1\).

For a real symmetric matrix, therefore, direction error generally decreases asymptotically at a rate governed by

\[
\left|\frac{\lambda_2}{\lambda_1}\right|^k,
\]

provided the dominant magnitude is unique, \(v_1^Tx_0\ne0\), and no iterate produces \(Ax_k=0\). This is an asymptotic rate description, not an unconditional finite-step error bound. A smaller ratio predicts faster eventual convergence; a ratio near one predicts slow progress.

For example, compare hypothetical magnitude ratios one half and nine tenths. After \(k\) powers, their leading subordinate factors behave like \((1/2)^k\) and \((9/10)^k\). Both decay, but at markedly different speeds. This comparison isolates the spectral effect; actual direction error also depends on the starting coefficients. It therefore supports a qualitative prediction about eventual behaviour without promising a precise error after a chosen number of steps.

<!-- section: SEC-04 -->
## Counterexamples clarify the assumptions

Several superficially similar behaviours have different meanings. If \(\lambda_1<0\), successive normalized iterates may alternate sign. That is not directional failure: \(v_1\) and \(-v_1\) represent the same eigendirection.

If instead \(v_1^Tx_0=0\), the initial vector contains no dominant component. In exact arithmetic, multiplication by \(A\) cannot create that missing eigencomponent, so the iterates do not converge to \(v_1\). This is not merely slow convergence.

If \(|\lambda_1|=|\lambda_2|\), there is no unique dominant magnitude. The method need not select one eigenvector and may remain in, or oscillate within, the associated invariant subspace. By contrast, when \(|\lambda_2/\lambda_1|<1\) but is close to one, the target is unique yet convergence can be very slow.

The orthogonal derivation above belongs to the real symmetric setting. Power iteration can apply to some nonsymmetric matrices, but a clean orthogonal eigenbasis is not generally available. Defective matrices, complex dominant eigenvalues, and non-normal behaviour require additional care and lie outside our present scope.

These cases suggest a compact diagnostic checklist before trusting a run. Ask whether the matrix is in the symmetric setting used by the derivation, whether one eigenvalue magnitude is strictly largest, whether the starting vector has a dominant projection, and whether multiplication has produced zero. Then separate harmless sign alternation from a tied dominant subspace or a genuinely absent component. The observations can look similar in a short trace, but the assumptions explain them differently.

<!-- section: SEC-05 -->
## Estimating and checking an eigenpair

Given a nonzero approximate eigenvector \(x_k\), estimate its eigenvalue with the Rayleigh quotient

\[
\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.
\]

For a normalized iterate this simplifies to \(\rho(x_k)=x_k^TAx_k\). For symmetric \(A\), if \(x_k\) approaches \(v_1\), then the estimate approaches \(\lambda_1\).

An estimate alone does not measure whether the two sides of the eigenpair equation agree. Define

\[
r_k=Ax_k-\rho(x_k)x_k.
\]

An exact eigenpair has zero residual, while \(\|r_k\|_2\) measures the equation mismatch of an approximation. This is a useful stopping diagnostic. Testing only \(\|x_{k+1}-x_k\|\) can be misleading when a negative dominant eigenvalue makes signs alternate, even as the eigendirection improves.

Residual size should be interpreted as a property of the reported pair. It asks how nearly \(Ax_k\) equals \(\rho(x_k)x_k\), using the same vector and estimate on both sides. A small value therefore supports stopping on equation mismatch, but it does not erase the earlier scope assumptions or prove that an arbitrary run found a uniquely dominant target. Diagnostics complement the convergence argument; they do not replace it.

<!-- section: SEC-06 -->
## A safeguarded mathematical algorithm

Start with a square matrix \(A\), nonzero \(x_0\), tolerance \(\varepsilon>0\), and positive maximum count \(K\). Normalize \(x_0\). For each iteration, compute \(y=Ax_k\); if \(\|y\|_2=0\), report breakdown before attempting division. Otherwise set \(x_{k+1}=y/\|y\|_2\), compute \(\rho_{k+1}=x_{k+1}^TAx_{k+1}\), and form \(r_{k+1}=Ax_{k+1}-\rho_{k+1}x_{k+1}\). Stop successfully when \(\|r_{k+1}\|_2\le\varepsilon\). If that never happens, stop after \(K\) iterations and report the final diagnostics. The tolerance stop and iteration cap answer different questions: one detects achieved equation accuracy; the other bounds work.

A practical trace should record the estimate, residual norm, and iteration number together. If the residual passes the tolerance, the stated accuracy test has succeeded. If the cap arrives first, the final pair remains an approximation whose reported residual must be examined, not silently labelled converged. Breakdown is different again: it means normalization cannot continue because the new product is zero. Keeping these three outcomes separate prevents a numerical safeguard from being confused with a spectral conclusion and makes the returned status interpretable alongside the assumptions already established in the derivation.

<!-- section: SEC-07 -->
## NumPy operations used below

The implementation needs only a small NumPy vocabulary. `np.asarray(value, dtype=float)` converts compatible inputs to floating arrays. Inspect `A.shape` and `x.shape` before arithmetic: a matrix is two-dimensional, while the intended vector is one-dimensional. For compatible shapes, `A @ x` is the matrix–vector product. For a one-dimensional vector, `np.linalg.norm(x)` gives its Euclidean norm; compare that scalar with zero before division.

Input checks can raise a specific exception. Array comparisons are elementwise, so conditions needing one truth value should use shapes or scalar diagnostics rather than an unreduced array comparison. Finally, returning comma-separated diagnostics creates a tuple, which a caller can unpack into separate names. These patterns are confined to the operations required by power iteration.

Read `y = A @ x` as the computational counterpart of \(y=Ax\), and `x = y / y_norm` as the normalization rule. The order matters: shape checks precede multiplication, and the zero-norm test precedes division. Likewise, the four returned objects have distinct roles—estimated scalar, normalized vector, residual norm, and iteration count—so tuple unpacking makes each diagnostic available for inspection.

<!-- section: SEC-08 -->
## Executable implementation and worked case

The function below converts and validates inputs before iterating. It rejects a nonsquare matrix, an incompatible or zero vector, a nonpositive tolerance, and a maximum count that is not a positive integer. Each loop performs the product, checks breakdown before normalization, computes the Rayleigh estimate and residual, and returns four diagnostics either at tolerance or at the cap.

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
    if not isinstance(max_iterations, int) or isinstance(max_iterations, bool) or max_iterations <= 0:
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
eigenvalue, eigenvector, residual, iterations = power_iteration(
    A, np.array([1.0, 1.0])
)
print("Estimated dominant eigenvalue:", eigenvalue)
print("Estimated eigenvector:", eigenvector)
print("Residual norm:", residual)
print("Iterations:", iterations)
```

For this matrix, the characteristic equation gives exact eigenvalues

\[
3+\sqrt2\qquad\text{and}\qquad3-\sqrt2.
\]

The first has larger magnitude. With \(x_0=(1,1)^T\), the code should estimate \(3+\sqrt2\) and produce a small residual. The eigenvector’s displayed sign is immaterial. To interpret the run, compare the estimate with the exact dominant value, inspect the residual against the tolerance, and note whether the returned count records early convergence or the maximum-iteration fallback. Together, these outputs connect the spectral derivation, the normalized update, and a defensible computational stopping decision.
