# Power Iteration for an Idealized Modal Problem

Power iteration is a repeated matrix-vector calculation for finding the eigendirection associated with an eigenvalue of largest magnitude. In this lesson, an eigenvector is interpreted as an idealized mode shape. That interpretation is useful, but deliberately limited: the clean explanation below assumes a real symmetric matrix and is not a model of every engineering eigenproblem.

<!-- section: SEC-01 -->
## Eigenpairs and the dominant mode

For a real square matrix \(A\in\mathbb{R}^{n\times n}\), a non-zero vector \(v\) is an eigenvector when

\[
Av=\lambda v,
\]

where the scalar \(\lambda\) is the associated eigenvalue. Multiplication by \(A\) therefore changes the length, and possibly the sign, of \(v\), but not its eigendirection. The requirement \(v\ne0\) is essential: substituting the zero vector makes the equation true for every value of \(\lambda\), so it carries no eigenvalue information.

You can test a proposed eigenpair without solving a larger problem: calculate \(Av\) and compare it with \(\lambda v\). Matching components establish the defining relation, provided the proposed vector is non-zero. Multiplying an eigenvector by any non-zero scalar changes its scale but preserves its eigendirection. For a mode-shape representation, this focuses attention on the relative components rather than on an arbitrary displayed amplitude.

In an idealized modal interpretation, the direction of \(v\) represents a mode shape and \(\lambda\) supplies the corresponding eigenvalue information. Power iteration targets the eigenvalue with the largest **magnitude**, not necessarily the largest algebraic value. If two eigenvalues are \(5\) and \(-8\), then \(-8\) is dominant because \(|-8|>|5|\). This distinction matters whenever negative eigenvalues are possible.

<!-- section: SEC-02 -->
## Components in a symmetric modal basis

First recall the geometry needed to describe components. Real vectors \(u\) and \(v\) are orthogonal when \(u^Tv=0\). Vectors \(v_1,\ldots,v_k\) are orthonormal when every cross-product \(v_i^Tv_j\) is zero for \(i\ne j\), while every vector has unit norm. For a unit vector \(v\), the scalar \(v^Tx\) is the coefficient of \(x\) in the \(v\) direction. For example, with \(v=(1,0)^T\) and \(x=(3,4)^T\), the coefficient is \(v^Tx=3\).

Now impose the controlled setting used for the convergence explanation: \(A\) is real and symmetric, so \(A=A^T\). The spectral theorem then supplies an orthonormal basis of real eigenvectors. If those eigenvectors are the columns of an orthogonal matrix \(Q\), then

\[
A=Q\Lambda Q^T,\qquad
\Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n),
\]

and every vector can be written as

\[
x=\sum_{i=1}^n c_i v_i,\qquad c_i=v_i^Tx.
\]

This orthogonal real decomposition is not being claimed for an arbitrary non-symmetric matrix.

The coefficient formula gives a practical component check. Take the inner product of \(x\) with each unit basis vector; the resulting scalars state how much of each orthogonal direction appears in \(x\). Because the basis vectors are mutually orthogonal and have unit norm, these coefficients can be used directly in the expansion. This geometric preparation does not itself assert any convergence result; it only supplies the vocabulary used later.

Order the eigenvalues by magnitude and assume

\[
|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.
\]

The strict first inequality means that \(\lambda_1\) is unique in magnitude. It is the dominant eigenvalue in the sense required by basic power iteration.

<!-- section: SEC-03 -->
## Normalized matrix-vector updates

For \(x=(x_1,\ldots,x_n)^T\), the Euclidean norm is

\[
\|x\|_2=\sqrt{x_1^2+\cdots+x_n^2}=\sqrt{x^Tx}.
\]

When \(x\ne0\), setting \(u=x/\|x\|_2\) gives \(\|u\|_2=1\). Thus \((3,4)^T\) has norm \(5\) and normalizes to \((3/5,4/5)^T\). The zero vector cannot be normalized: its norm is zero, so division by that norm is undefined and must be stopped before it occurs.

Starting from a non-zero \(x_0\), power iteration repeats

\[
y_{k+1}=Ax_k,\qquad
x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.
\]

The denominator must be non-zero. Normalization controls scale but does not change the direction of \(Ax_k\); each accepted iterate has unit Euclidean norm.

When tracing an iteration by hand, keep the two operations separate. First record the raw matrix-vector product \(y_{k+1}\). Next compute its Euclidean norm, stop if that norm is zero, and otherwise divide every component by the same scalar. A quick check is to square and sum the components of the new iterate: the result should be one, apart from numerical rounding. This check verifies normalization, not convergence.

A mode shape also has a sign ambiguity. If the dominant eigenvalue is negative, successive normalized iterates may alternate sign. That alone is not failure: \(v_1\) and \(-v_1\) describe the same eigendirection, so comparisons should allow for sign-equivalent mode shapes.

<!-- section: SEC-04 -->
## Estimating the eigenvalue and checking the residual

For equal-length real vectors, \(x^Ty\) is the scalar sum of componentwise products. To compute \(x^TAx\), first form \(y=Ax\), then compute \(x^Ty\), checking that \(A\) is square and compatible with \(x\). Also, \(x^Tx=\|x\|_2^2\ge0\). For instance, if

\[
A=\begin{bmatrix}2&0\\0&1\end{bmatrix},\qquad x=\begin{bmatrix}1\\2\end{bmatrix},
\]

then \(Ax=(2,2)^T\) and \(x^TAx=1(2)+2(2)=6\).

For a non-zero iterate, the Rayleigh quotient is

\[
\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.
\]

Because power iteration normalizes \(x_k\), the denominator is one and the expression reduces to \(\rho(x_k)=x_k^TAx_k\). For symmetric \(A\), as \(x_k\) approaches \(v_1\), this estimates \(\lambda_1\). The simplified expression must not be used for an unnormalized vector without accounting for its denominator.

The eigenpair residual is

\[
r_k=Ax_k-\rho(x_k)x_k.
\]

An exact eigenpair gives the zero residual. Consequently, \(\|r_k\|_2\) measures how closely the current pair satisfies the eigenvector equation and provides a practical stopping quantity. It is preferable to relying only on the difference between successive vectors, which can look large when equivalent directions flip sign.

A useful calculation table has four columns: the current normalized vector, \(Ax_k\), the scalar estimate, and the residual norm. This keeps two judgments distinct. The estimate answers “which eigenvalue is currently indicated?”, while the residual answers “how well does this vector-estimate pair satisfy the equation?” Reaching a chosen tolerance is a computational stopping decision; it does not remove the need to check that the matrix and starting vector satisfy the assumptions used to interpret the result.

<!-- section: SEC-05 -->
## A safeguarded executable algorithm

The algorithm first normalizes the initial vector. At each iteration it computes \(y=Ax\), checks for zero norm before division, normalizes, evaluates the Rayleigh estimate and residual, and returns early if the residual norm is no greater than a positive tolerance. Otherwise it returns the final values at a positive maximum iteration count.

The implementation below converts both inputs to floating NumPy arrays. It requires a square matrix, a compatible one-dimensional initial vector, and a non-zero initial vector. Invalid shapes, a non-positive tolerance, or a non-positive or non-integer iteration limit raise `ValueError`. A zero \(Ax\) during iteration raises `RuntimeError`. Every successful return has four entries: the eigenvalue estimate, normalized vector, residual norm, and iteration count.

Read the safeguards in execution order. Shape and initial-vector failures are rejected before normalization. A breakdown is checked after multiplication but before division. Only then are the estimate and residual formed. The tolerance return records the actual iteration that met the test; if no iteration meets it, the fallback records the specified cap. Reaching that cap is therefore a return condition, not a claim that the approximation is sufficiently accurate.

```python
import numpy as np

def power_iteration(A, x0, tolerance=1e-10, max_iterations=1000):
    A = np.asarray(A, dtype=float)
    x = np.asarray(x0, dtype=float)

    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("A must be a square matrix")
    if x.ndim != 1 or x.shape[0] != A.shape[0]:
        raise ValueError("x0 must be a compatible one-dimensional vector")
    if np.linalg.norm(x) == 0:
        raise ValueError("x0 must be non-zero")
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    if isinstance(max_iterations, (bool, np.bool_)) or not isinstance(max_iterations, (int, np.integer)) or max_iterations <= 0:
        raise ValueError("max_iterations must be a positive integer")

    x = x / np.linalg.norm(x)
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
```

<!-- section: SEC-06 -->
## Why one direction emerges

Write the initial vector in the symmetric eigenbasis. After \(k\) unnormalized multiplications,

\[
A^kx_0
=\sum_{i=1}^n c_i\lambda_i^kv_i
=\lambda_1^k\left(c_1v_1+
\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^kv_i\right).
\]

The dominant coefficient must satisfy \(c_1=v_1^Tx_0\ne0\). With the strict magnitude gap, every subordinate ratio has magnitude below one, so \(\left|\lambda_i/\lambda_1\right|^k\) tends to zero. Normalization removes the overall scale \(\lambda_1^k\) while retaining the increasingly dominant direction.

Accordingly, for a real symmetric matrix, a unique dominant magnitude, a non-zero initial projection onto \(v_1\), and no iterate for which \(Ax_k=0\), the direction error generally decreases asymptotically at a rate governed by

\[
\left|\frac{\lambda_2}{\lambda_1}\right|^k.
\]

This is an asymptotic explanation, not an unconditional finite-iteration error bound. Each stated hypothesis is part of the result.

The ratio offers a qualitative comparison between suitable problems. A smaller magnitude ratio makes subordinate components shrink more rapidly with repeated powers, whereas a ratio close to one leaves them visible for longer. In the modal picture, repeated updating increasingly emphasizes the initially present dominant-mode component. This picture is valid only after confirming symmetry, a strict dominant-magnitude gap, non-zero dominant projection, and absence of zero-product breakdown; it is not a substitute for those checks.

<!-- section: SEC-07 -->
## Recognizing limitations before trusting the result

If \(v_1^Tx_0=0\), the initial vector has no dominant eigendirection component. In exact arithmetic, repeated multiplication cannot create that missing component, so the iterates remain in a non-dominant invariant subspace and do not converge to \(v_1\). This is not merely slow convergence.

If \(|\lambda_1|=|\lambda_2|\), a unique eigenvector need not be selected; an iterate may oscillate or remain within a dominant invariant subspace. This differs from a separated case where \(|\lambda_2/\lambda_1|\) is below but close to one: then the method can converge, but slowly.

Finally, the clean orthogonal-basis argument is restricted to real symmetric matrices. Basic power iteration can apply to some non-symmetric matrices, but a general orthogonal decomposition is unavailable. Defective matrices, complex dominant eigenvalues, and non-normal behavior require additional care and lie outside this lesson. Idealized modal analysis is therefore a teaching bridge, not a claim that every engineering eigenproblem is symmetric or appropriately solved by this basic method.

Before trusting a run, ask three diagnostic questions. Is there a unique eigenvalue of largest magnitude? Does the starting vector contain some component in its eigendirection? Does the observed residual become small before the cap? A negative dominant eigenvalue may explain sign alternation, but it does not excuse a large residual. Equal dominant magnitudes and a merely small magnitude gap also require different interpretations: the former can prevent unique selection, while the latter predicts slow progress.

<!-- section: SEC-08 -->
## Worked idealized modal calculation

Consider the symmetric matrix and initial vector

\[
A=\begin{bmatrix}4&1\\1&2\end{bmatrix},\qquad x_0=(1,1)^T.
\]

The exact eigenvalues are supplied as

\[
3+\sqrt{2}\quad\text{and}\quad3-\sqrt{2}.
\]

Because both are positive and \(3+\sqrt{2}>3-\sqrt{2}\), the dominant eigenvalue for this example is \(3+\sqrt{2}\). The self-contained calculation below runs the safeguarded update with the supplied initial vector and default parameters, then compares the estimate with that exact value.

```python
import numpy as np

def power_iteration(A, x0, tolerance=1e-10, max_iterations=1000):
    A = np.asarray(A, dtype=float)
    x = np.asarray(x0, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("A must be a square matrix")
    if x.ndim != 1 or x.shape[0] != A.shape[0]:
        raise ValueError("x0 must be a compatible one-dimensional vector")
    if np.linalg.norm(x) == 0:
        raise ValueError("x0 must be non-zero")
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    if isinstance(max_iterations, (bool, np.bool_)) or not isinstance(max_iterations, (int, np.integer)) or max_iterations <= 0:
        raise ValueError("max_iterations must be a positive integer")
    x = x / np.linalg.norm(x)
    for iteration in range(1, max_iterations + 1):
        y = A @ x
        y_norm = np.linalg.norm(y)
        if y_norm == 0:
            raise RuntimeError("power iteration broke down because A @ x is zero")
        x = y / y_norm
        eigenvalue = float(x @ (A @ x))
        residual_norm = float(np.linalg.norm(A @ x - eigenvalue * x))
        if residual_norm <= tolerance:
            return eigenvalue, x, residual_norm, iteration
    return eigenvalue, x, residual_norm, max_iterations

A = np.array([[4.0, 1.0], [1.0, 2.0]])
estimate, mode_shape, residual, iterations = power_iteration(A, np.array([1.0, 1.0]))
exact_dominant = 3.0 + np.sqrt(2.0)
print("Estimated dominant eigenvalue:", estimate)
print("Absolute eigenvalue error:", abs(estimate - exact_dominant))
print("Estimated mode-shape direction:", mode_shape)
print("Residual norm:", residual)
print("Iterations:", iterations)
```

The expected interpretation is an estimate close to \(3+\sqrt{2}\) and a small residual norm. The reported vector may have either sign; a small residual does not require one particular sign for the mode-shape direction.

Use the printed quantities as a compact audit of the calculation. Compare the estimate with the supplied exact dominant value, inspect the absolute error, and then inspect the residual independently. The iteration count tells you how much repeated work was needed under the default tolerance; it does not alter which exact eigenvalue is dominant.
