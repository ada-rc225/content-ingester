# Power Iteration: From Repeated Multiplication to an Approximate Eigenpair

<!-- section: SEC-01 -->
## Eigenpairs and why an iterative method helps

Let (A\in\mathbb{R}^{n\times n}). A non-zero vector (v\in\mathbb{R}^n) is an eigenvector of (A) if a scalar \(\lambda\) satisfies

\[
Av=\lambda v.
\]

The scalar \(\lambda\) is the eigenvalue associated with \(v\). The condition \(v\ne 0\) is essential: the zero vector satisfies \(A0=\lambda 0\) for every scalar, so it cannot identify an eigenvalue or an eigendirection.

Eigenvalues are roots of the characteristic equation

\[
\det(A-\lambda I)=0,
\]

where \(I\) is the identity matrix of compatible size. This equation is useful for characterising eigenvalues, but explicitly forming a characteristic polynomial is usually a poor numerical strategy for a large matrix. Power iteration takes a different numerical route: it repeatedly uses matrix-vector products to estimate a selected eigenpair. This is a computational strategy, not an algebraic replacement of the characteristic equation.

The word *dominant* will always refer to magnitude. Power iteration targets an eigenvalue with largest absolute value, not necessarily the most positive eigenvalue. For instance, if the relevant eigenvalues are \(5\) and \(-8\), then \(-8\) is dominant because \(|-8|>|5|\).

There are therefore two linked tasks. The vector iteration seeks a direction that approximately reproduces itself after multiplication by \(A\), apart from a scalar factor. Once that direction is available, the scalar factor can be estimated. Keeping these tasks separate helps explain why the method first updates and normalises a vector and only later evaluates an eigenvalue estimate and its residual.

<!-- section: SEC-02 -->
## The symmetric spectral setting

A clean explanation is available when \(A\) is real and symmetric, so \(A=A^T\). The spectral theorem then supplies an orthonormal basis of real eigenvectors. If the eigenvectors form the columns of an orthogonal matrix \(Q\), then

\[
A=Q\Lambda Q^T,
\qquad
\Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n).
\]

Because the eigenvectors \(v_1,\ldots,v_n\) are an orthonormal basis, every vector \(x\) has the expansion

\[
x=\sum_{i=1}^n c_i v_i,
\qquad c_i=v_i^T x.
\]

This coefficient formula matters: it identifies exactly how much of each eigendirection is present in a starting vector.

To read the expansion, think of the coefficients as coordinates in the eigenvector basis. Multiplication by \(A\) does not replace those basis directions; it scales the component along \(v_i\) by its associated \(\lambda_i\). Repeating the multiplication repeats those scalings. Orthonormality is what makes the coordinate formula \(c_i=v_i^Tx\) available here, so the explanation depends specifically on the stated symmetric setting.

Order the eigenvalues by magnitude as

\[
|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.
\]

The strict first inequality makes \(\lambda_1\) unique in magnitude. It is the dominant eigenvalue in this lesson. The real-symmetric hypothesis and this strict gap must remain attached to the convergence explanation; neither may be silently replaced by a claim about arbitrary matrices or by ordering eigenvalues according to their algebraic values.

<!-- section: SEC-03 -->
## The normalised power update

Choose a non-zero initial vector \(x_0\). At each step, compute

\[
y_{k+1}=Ax_k,
\qquad
x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.
\]

The denominator must be non-zero. Multiplication by \(A\) changes the mixture of eigenvector components; normalisation then controls the scale without changing the direction of \(y_{k+1}\). Consequently, every successfully normalised iterate has unit Euclidean norm. Normalisation is not optional bookkeeping: without it, repeated multiplication can make the vector's scale grow or shrink dramatically, even though the direction is the quantity of interest.

To trace one step, first calculate the complete matrix-vector product. Check its norm before dividing, and then divide every component by that same norm. Keeping multiplication and normalisation as separate operations makes both the mathematics and a later implementation easier to inspect.

After a successful update, verify two facts. The vector \(x_{k+1}\) should have unit norm, and it should be a scalar rescaling of \(Ax_k\). The first confirms the normalisation; the second confirms that normalisation did not introduce a new direction. If \(Ax_k=0\), neither check can be completed because division by its norm would be division by zero. That case requires a breakdown message rather than another iterate.

<!-- section: SEC-04 -->
## Why the dominant component emerges

Write the starting vector in the symmetric eigenbasis as \(x_0=\sum_i c_i v_i\). Before normalisation, repeated multiplication gives

\[
A^k x_0
=\sum_{i=1}^n c_i\lambda_i^k v_i
=\lambda_1^k\left(c_1v_1+
\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^k v_i\right).
\]

This factorisation displays the mechanism. Suppose \(A\) is real and symmetric, \(|\lambda_1|>|\lambda_2|\), and

\[
c_1=v_1^Tx_0\ne0.
\]

For each subordinate component, \(\left|\lambda_i/\lambda_1\right|^k\) tends to zero. The dominant component survives because it was present initially, while the other components become small relative to it. Normalising the result therefore reveals the dominant eigendirection.

More precisely, if the initial projection onto \(v_1\) is non-zero and no iterate produces \(Ax_k=0\), the direction error generally decreases asymptotically at a rate governed by

\[
\left|\frac{\lambda_2}{\lambda_1}\right|^k.
\]

This is an asymptotic rate statement under all the listed assumptions, not an unconditional finite-iteration error bound. It also explains a useful comparison: a smaller magnitude ratio gives faster asymptotic decay, whereas a ratio near one gives slow decay.

The factorised expression also shows why the initial projection condition cannot be detached from the conclusion. The ratio powers suppress components that are already present, but they do not manufacture the coefficient \(c_1\). When \(c_1\ne0\), the dominant term provides the reference against which subordinate terms shrink. When it is zero, the displayed dominant term vanishes, so the convergence argument toward \(v_1\) no longer applies. The spectral gap and non-zero projection play different, equally necessary roles.

<!-- section: SEC-05 -->
## Failure modes and limits of the explanation

Several behaviours must be distinguished rather than labelled collectively as failure.

First, if the dominant eigenvalue is negative, successive normalised iterates may alternate sign. This alone is not failure: \(v_1\) and \(-v_1\) represent the same eigendirection. A test based only on the difference between successive vectors can therefore be misleading.

Second, if \(v_1^Tx_0=0\), the starting vector contains no dominant component. In exact arithmetic, repeated multiplication cannot create that missing eigencomponent, so the iterates will not converge to \(v_1\). This is different from slow convergence: the required component is absent, rather than merely taking many iterations to dominate.

Third, if \(|\lambda_1|=|\lambda_2|\), there is no unique dominant magnitude. The method need not select a unique eigenvector; it may remain in or oscillate within the invariant subspace associated with those dominant magnitudes. By contrast, when \(|\lambda_2/\lambda_1|\) is below but close to one, dominance is unique but convergence can be very slow. Repeated dominance and a small spectral gap are therefore separate cases.

Finally, power iteration can be applied to some non-symmetric matrices, but the orthogonal decomposition used above is not generally available for them. Defective matrices, complex dominant eigenvalues, and non-normal behaviour require additional care. They are outside the scope of this symmetric convergence explanation, which must not be generalised to every non-symmetric matrix.

These cases suggest a careful diagnostic order. Check first whether the starting vector can contain the required dominant component, then whether a unique dominant magnitude exists, and then whether the magnitude ratio predicts slow progress. If iterates alternate sign, compare directions modulo sign before calling the behaviour a failure. Each observation corresponds to a different assumption, so it should lead to a different interpretation.

<!-- section: SEC-06 -->
## Estimating the eigenvalue and deciding when to stop

Once a non-zero approximate eigenvector \(x_k\) is available, estimate its eigenvalue with the Rayleigh quotient

\[
\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.
\]

For a normalised iterate, \(x_k^Tx_k=1\), so this simplifies to

\[
\rho(x_k)=x_k^TAx_k.
\]

The simplified expression must not be used for an unnormalised vector without its denominator. In the real-symmetric setting, if \(x_k\) approaches \(v_1\), then \(\rho(x_k)\) approaches \(\lambda_1\).

An eigenvalue estimate becomes more informative when paired with the eigenpair residual

\[
r_k=Ax_k-\rho(x_k)x_k.
\]

For an exact eigenpair, substituting \(Av=\lambda v\) and \(\rho(v)=\lambda\) gives the zero vector. Thus \(\|r_k\|_2\) measures how closely the computed pair satisfies the eigenvector equation and provides a meaningful computational stopping measure. It is preferable to stopping only when successive vectors look similar, because sign flips can make two representatives of the same eigendirection look far apart. A practical rule is to stop when \(\|r_k\|_2\le\varepsilon\) for a chosen \(\varepsilon>0\), while retaining a maximum-iteration fallback.

Computing these quantities in the right order avoids ambiguity. Begin with the new unit vector, use it in the Rayleigh quotient, and use that same vector and estimate in the residual. Then compare the residual norm with the positive tolerance. The iteration cap handles the distinct outcome in which the tolerance has not been met after the permitted number of updates; it must remain available even though early stopping is possible.

<!-- section: SEC-07 -->
## A safeguarded algorithm and worked consolidation

A complete procedure begins by converting the matrix and starting vector to floating arrays. It checks that the matrix is square, that the starting vector is one-dimensional with a compatible length, and that the starting vector is non-zero before normalising it. It also requires a positive tolerance and a positive integer iteration cap.

Each iteration computes \(y=Ax\), checks for breakdown when \(\|y\|_2=0\), and only then divides by the norm. It next computes the Rayleigh estimate, residual, and residual norm. The procedure returns early when the residual norm is at most the tolerance; otherwise, it returns the final values after the iteration cap. In either case, the four returned values are the eigenvalue estimate, normalised vector, residual norm, and iterations performed.

The following block is self-contained and executable.

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
    if (isinstance(max_iterations, (bool, np.bool_)) or
            not isinstance(max_iterations, (int, np.integer)) or
            max_iterations <= 0):
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
result = power_iteration(A, np.array([1.0, 1.0]))
eigenvalue, eigenvector, residual_norm, iterations = result
print("Estimated dominant eigenvalue:", eigenvalue)
print("Estimated eigenvector:", eigenvector)
print("Residual norm:", residual_norm)
print("Iterations:", iterations)
```

For this symmetric matrix and starting vector, the exact eigenvalues are

\[
3+\sqrt{2}
\quad\text{and}\quad
3-\sqrt{2}.
\]

The first has larger magnitude, so the code should estimate \(3+\sqrt{2}\) and report a small residual. The eigenvector may appear with either sign; that sign choice does not change its eigendirection or the quality of the residual.

Read the four printed values together. The estimated eigenvalue can be compared with the dominant exact value, while the residual norm reports the defect in the approximate eigenpair equation. The iteration count tells whether the tolerance was reached before the cap. The printed vector supplies a unit representative of the estimated direction, but its overall sign is not a criterion for accepting or rejecting the result.

To consolidate the lesson, trace how the initial vector is normalised, identify the matrix-vector product and breakdown check in one loop pass, and connect the returned estimate to the Rayleigh quotient. Then use the residual norm—not a preferred eigenvector sign—to judge whether the approximate pair has met the stopping rule.
