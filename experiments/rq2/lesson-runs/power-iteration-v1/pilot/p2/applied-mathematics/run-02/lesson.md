# Power iteration: structure, convergence, and computation

Power iteration is a matrix-vector method for approximating an eigenpair associated with an eigenvalue of largest magnitude. The central question is not merely how to repeat an update, but why the update isolates one spectral component, when that reasoning is valid, and what computation can legitimately use as a stopping signal.

<!-- section: SEC-01 -->
## From eigenpairs to an iterative question

Let \(A\in\mathbb{R}^{n\times n}\). A vector \(v\ne0\) is an eigenvector of \(A\) when a scalar \(\lambda\) satisfies

\[
Av=\lambda v.
\]

Then \(\lambda\) is the eigenvalue associated with \(v\). Excluding the zero vector is essential: \(A0=\lambda0\) holds for every scalar, so that equation would carry no eigenvalue information.

Eigenvalues are roots of the characteristic equation

\[
\det(A-\lambda I)=0,
\]

where \(I\) has the same dimension as \(A\). This is a useful derivation route for a small matrix. For a large matrix, however, explicitly forming the characteristic polynomial is usually a poor numerical strategy. Power iteration instead uses repeated matrix-vector products to estimate a selected eigenpair. Thus the determinant equation identifies the algebraic target, while the iteration supplies a numerical route; the two statements are not interchangeable procedures.

Keep the definition in view when reading the iteration. The desired output is a non-zero direction that is preserved by multiplication by \(A\), together with the scalar by which that direction is multiplied. The zero-vector warning is therefore more than a technicality: an algorithm that returned zero would not have identified an eigenpair. Likewise, the characteristic equation explains what qualifies as an eigenvalue, but it does not say that forming its polynomial is the operation power iteration performs. That distinction separates the exact definition from the numerical process used to approximate it.

<!-- section: SEC-02 -->
## The symmetric spectral setting and the target

The clean convergence argument begins with a real symmetric matrix, \(A=A^T\). The spectral theorem gives an orthonormal basis of real eigenvectors and a factorisation

\[
A=Q\Lambda Q^T,\qquad
\Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n).
\]

Writing the columns of \(Q\) as \(v_1,\ldots,v_n\), every vector has the expansion

\[
x=\sum_{i=1}^n c_i v_i,qquad c_i=v_i^Tx.
\]

Order the eigenvalues by magnitude and assume a strict first gap:

\[
|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.
\]

The strict inequality makes \(\lambda_1\) unique in magnitude. “Dominant” therefore means largest absolute value, not largest algebraic value. If two eigenvalues are \(5\) and \(-8\), the target is \(-8\), since \(|-8|>|5|\). This distinction will also explain why iterates can alternate sign without losing their limiting eigendirection.

The coefficient formula makes the representation operational. For a given starting vector, \(v_i^Tx_0\) measures its component in the \(i\)-th eigenvector direction. Power iteration does not choose these coefficients; they are fixed by the start. Multiplication then changes their relative sizes through powers of the associated eigenvalues. Before proceeding, check the logic of the ordering with the pair \(5,-8\): algebraic ordering would favour \(5\), whereas magnitude ordering compares \(5\) and \(8\) and favours \(-8\). Every later use of “dominant” follows the second comparison.

<!-- section: SEC-03 -->
## The update and its convergence mechanism

Choose a non-zero \(x_0\). One power step computes

\[
y_{k+1}=Ax_k,\qquad
x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.
\]

The denominator must be non-zero. Normalisation controls scale while preserving the direction of \(Ax_k\), and it makes each completed iterate have unit Euclidean norm.

To see the mechanism, expand \(x_0=\sum_i c_i v_i\) in the orthonormal eigenbasis. Before normalisation,

\[
A^kx_0
=\sum_{i=1}^n c_i\lambda_i^kv_i
=\lambda_1^k\left(c_1v_1+
\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^kv_i\right).
\]

If \(c_1=v_1^Tx_0\ne0\), every subordinate factor has magnitude bounded by the spectral ratio, and

\[
\left|\frac{\lambda_i}{\lambda_1}\right|^k\longrightarrow0
\quad (i\ge2).
\]

Consequently, for a real symmetric matrix, direction convergence requires all of the following: a unique dominant magnitude \(|\lambda_1|>|\lambda_2|\), a non-zero initial projection onto \(v_1\), and no iterate for which \(Ax_k=0\). Under these assumptions, the asymptotic direction error is generally governed by

\[
\left|\frac{\lambda_2}{\lambda_1}\right|^k.
\]

This is an asymptotic rate description, not an unconditional finite-step error bound. A smaller ratio predicts faster eventual decay; a ratio near one predicts slow decay.

The factorisation shows each assumption doing a separate job. Symmetry supplies the orthonormal eigenbasis used in the expansion. The non-zero coefficient \(c_1\) ensures that the desired term is actually present. The strict magnitude gap makes every subordinate absolute ratio less than one. Finally, the non-breakdown condition makes each normalisation well-defined. Removing any one of these ingredients invalidates this particular convergence chain.

You can trace one symbolic step without choosing numerical entries. From \(x_0=\sum_i c_iv_i\), multiplication gives \(Ax_0=\sum_i c_i\lambda_i v_i\). After \(k\) multiplications it gives \(A^kx_0=\sum_i c_i\lambda_i^kv_i\). Factoring out \(\lambda_1^k\) does not discard the other terms; it exposes their relative factors. Normalisation then removes the overall scale while leaving those relative factors to determine direction. This is why the argument concerns an eigendirection even when the magnitude of the unnormalised sequence grows or shrinks.

<!-- section: SEC-04 -->
## Assumptions tested by counterexamples

Each hypothesis has a visible failure mode. First, if \(\lambda_1<0\), multiplying the dominant component by \(\lambda_1\) can make successive normalised iterates alternate sign. That alone is not failure: \(v_1\) and \(-v_1\) represent the same eigendirection.

Second, suppose \(v_1^Tx_0=0\). The initial vector has no component in the dominant eigendirection. In exact arithmetic, multiplication by \(A\) only rescales the eigenbasis components already present, so it cannot create the missing component. The method therefore does not converge to \(v_1\); this is different from ordinary slow convergence.

Third, if \(|\lambda_1|=|\lambda_2|\), there is no unique dominant magnitude. The iteration need not select one eigenvector and may remain in, or oscillate within, the associated invariant subspace. By contrast, when \(|\lambda_2/\lambda_1|<1\) but is close to one, the target is separated yet convergence can be very slow.

Finally, the orthogonal derivation above belongs to the real symmetric setting. Power iteration can apply to some non-symmetric matrices, but a real orthonormal eigenbasis is not generally available. Defective matrices, complex dominant eigenvalues, and non-normal behaviour need additional care and lie outside this lesson's convergence argument.

Use these cases as an assumption checklist rather than one undifferentiated warning. Sign alternation can coexist with direction convergence. Zero dominant projection prevents convergence to the desired direction in exact arithmetic. Equal dominant magnitudes remove unique selection, while a separated ratio near one retains the target but slows the asymptotic process. The non-symmetric case is a scope boundary: the update may still be applied in some instances, but the orthogonal proof just used must not be carried over as a general result.

A quick counterexample analysis can therefore begin by asking four questions: Is the dominant magnitude unique? Is its coefficient in the start non-zero? Can a multiplication produce the zero vector? Is the matrix inside the real symmetric setting of the derivation? Those questions connect observed behaviour to the precise assumption that controls it.

<!-- section: SEC-05 -->
## Estimating quality and deciding when to stop

Given a non-zero approximate eigenvector \(x_k\), estimate its eigenvalue with the Rayleigh quotient

\[
\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.
\]

For a unit vector this simplifies to \(\rho(x_k)=x_k^TAx_k\). In the symmetric setting, as \(x_k\) approaches \(v_1\), the quotient approaches \(\lambda_1\).

The corresponding eigenpair residual is

\[
r_k=Ax_k-\rho(x_k)x_k.
\]

An exact eigenpair has zero residual, so \(\|r_k\|_2\) is a meaningful computational stopping measure. Comparing only successive vectors is unreliable because a negative dominant eigenvalue can cause a sign flip even as the eigendirection improves.

A safeguarded algorithm takes \(x_0\ne0\), a tolerance \(\varepsilon>0\), and a positive maximum iteration count \(K\). It normalises \(x_0\), forms \(y=Ax_k\), and checks \(\|y\|_2=0\) before any division. If breakdown does not occur, it normalises \(y\), computes the Rayleigh estimate and residual, and stops when \(\|r_{k+1}\|_2\le\varepsilon\). Otherwise it continues until \(K\) iterations have been performed. The tolerance stop and iteration cap answer different questions: one detects the requested residual level; the other ensures termination when that level is not reached.

The order of these diagnostics matters. The norm of \(y\) must be checked before forming \(y/\|y\|_2\); otherwise breakdown would cause division by zero. The Rayleigh estimate is computed from the new unit vector, so its denominator is one and the simplified expression applies. The residual then tests the candidate pair produced at that step. Only after that scalar residual norm is available can it be compared with the positive tolerance.

To interpret a reported run, read all four outputs together. The estimate and vector specify the approximate eigenpair, the residual norm records how closely that pair satisfies the eigenvalue equation, and the iteration count says whether the return occurred early or at the cap. A sign change in the vector is not by itself a reason to reject the result; the residual avoids that ambiguity.

<!-- section: SEC-06 -->
## A focused NumPy bridge

The implementation below uses only a small set of NumPy operations. `np.asarray(input, dtype=float)` converts compatible input to a floating-point array. Inspect `A.shape` and `x.shape` before arithmetic: the matrix must be two-dimensional and square, while the vector must be one-dimensional with the matching length.

For compatible arrays, `A @ x` is the matrix-vector product. For a one-dimensional vector, `np.linalg.norm(x)` gives its Euclidean norm. Test a scalar norm against zero before dividing. Shape and value faults should raise specific exceptions. Array comparisons are elementwise, so a program needing one decision should compare a scalar diagnostic such as a norm rather than treating an entire comparison array as one truth value.

A function can return several diagnostics in a tuple. The caller can unpack the returned eigenvalue estimate, vector, residual norm, and iteration count into four names. These patterns support the algorithm only; no alternative eigensolver or unrelated array operation is needed.

For a concrete shape trace, a two-by-two array has shape `(2, 2)` and a compatible one-dimensional vector has shape `(2,)`. Their product `A @ x` is another length-two vector. Its norm is a scalar, so the zero test gives one program decision, and division by a non-zero scalar produces the next unit vector. This small trace mirrors the mathematical update without adding array operations beyond those the implementation needs.

<!-- section: SEC-07 -->
## Executable implementation and worked consolidation

The function first validates and normalises the inputs. It rejects a non-square matrix, an incompatible vector, a zero initial vector, a non-positive tolerance, and a non-positive or non-integer iteration cap. Inside the loop it checks breakdown before division, then returns early on the residual threshold or returns the final four diagnostics at the cap.

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
    if (isinstance(max_iterations, (bool, np.bool_))
            or not isinstance(max_iterations, (int, np.integer))
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
eigenvalue, eigenvector, residual, iterations = power_iteration(
    A, np.array([1.0, 1.0])
)
print("Estimated dominant eigenvalue:", eigenvalue)
print("Estimated eigenvector:", eigenvector)
print("Residual norm:", residual)
print("Iterations:", iterations)
```

For this matrix, the characteristic equation gives the exact eigenvalues

\[
3+\sqrt{2}\qquad\text{and}\qquad3-\sqrt{2}.
\]

The dominant value is \(3+\sqrt{2}\). Starting from \((1,1)^T\) with the displayed default parameters, the program should estimate that value and report a small residual. The eigenvector may appear with either sign; a small residual does not require a prescribed sign.

Use the exact values to interpret the printout rather than to replace the iteration. Compare the reported eigenvalue with \(3+\sqrt{2}\), inspect whether the residual is below the default tolerance, and note the returned iteration count. The example thereby joins the characteristic-equation result, repeated normalised multiplication, Rayleigh estimation, and residual-based stopping in one calculation.
