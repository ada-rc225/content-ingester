# Power Iteration: From Repeated Updates to a Trustworthy Eigenpair

<!-- section: SEC-01 -->
## Eigenpairs and why we iterate

Let \(A\in\mathbb{R}^{n\times n}\). A non-zero vector \(v\in\mathbb{R}^n\) is an eigenvector of \(A\) if a scalar \(\lambda\) satisfies

\[
Av=\lambda v.
\]

The scalar \(\lambda\) is the eigenvalue associated with \(v\). The non-zero requirement matters: \(A0=\lambda 0\) holds for every scalar, so the zero vector cannot identify an eigenvalue.

Eigenvalues are roots of the characteristic equation

\[
\det(A-\lambda I)=0,
\]

where \(I\) has the same dimension as \(A\). Although this equation characterises eigenvalues, explicitly forming a characteristic polynomial is usually a poor numerical strategy for a large matrix. Power iteration instead uses repeated matrix-vector products to estimate a selected eigenpair; this is a numerical strategy, not an algebraic replacement for the determinant equation.

The method targets the eigenvalue of largest **magnitude**, not the largest algebraic value. Between eigenvalues \(5\) and \(-8\), for example, \(-8\) is dominant because \(|-8|>|5|\). In a simplified spectral-computation or ranking exercise, you might interpret the vector entries as evolving scores, but that interpretation adds no new mathematics: the algorithm here is only repeated multiplication and normalisation, not a production ranking system.

It helps to separate the mathematical target from the computational route. The defining equation describes an exact relationship: multiplying an eigenvector by the matrix changes only its scale. The iterative route starts with a vector that is usually not an eigenvector and repeatedly transforms it, hoping that one eigendirection becomes visible. A candidate vector must still be non-zero, and the target is still chosen by absolute eigenvalue size. These requirements do not disappear merely because the calculation is expressed as a loop.

<!-- section: SEC-02 -->
## The symmetric spectral setting

We will explain convergence in the clean case where \(A=A^T\) is real and symmetric. The spectral theorem then gives an orthonormal basis of real eigenvectors. If the eigenvectors \(v_1,\ldots,v_n\) are the columns of an orthogonal matrix \(Q\), then

\[
A=Q\Lambda Q^T,
\qquad
\Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n).
\]

Every vector \(x\) can therefore be decomposed into eigenvector components:

\[
x=\sum_{i=1}^n c_i v_i,
\qquad c_i=v_i^T x.
\]

You can read this as a change of representation. The vector \(x\) is the program state in ordinary coordinates, while the values \(c_i\) say how much of each orthonormal eigendirection it contains. Because the basis is orthonormal, each coefficient is obtained by the dot product \(v_i^Tx\). This representation is valuable for reasoning even when an implementation never constructs \(Q\), \(\Lambda\), or the coefficients explicitly.

This representation lets us track each component independently under multiplication by \(A\). Order the eigenvalues by magnitude as

\[
|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.
\]

The strict first inequality says that \(\lambda_1\) is unique in magnitude. It is the dominant eigenvalue in this lesson. Keep both restrictions attached to what follows: the decomposition argument uses a real symmetric matrix, and the convergence result needs a strict dominant-magnitude gap.

<!-- section: SEC-03 -->
## The normalised update

Choose a non-zero initial vector \(x_0\). One iteration consists of

\[
y_{k+1}=Ax_k,
\qquad
x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.
\]

The denominator must be non-zero. The matrix-vector product changes the relative sizes of the eigenvector components; normalisation controls scale without changing the direction of \(y_{k+1}\). Thus a useful loop invariant after each successful update is \(\|x_{k+1}\|_2=1\). You should think of the stored state as a direction represented by a unit vector, rather than as the rapidly growing or shrinking unnormalised vector.

For a concrete trace, take \(A\) to be the diagonal matrix with diagonal entries \(2\) and \(1\), and start from the already normalised vector \((1,1)^T/\sqrt{2}\). The product is proportional to \((2,1)^T\), so the next normalised state is \((2,1)^T/\sqrt{5}\). Dividing by the norm changes the length but not the direction of the product. Before every division, however, the algorithm must check that the product is not the zero vector.

<!-- section: SEC-04 -->
## Why a dominant direction emerges

Expand the initial vector in the symmetric eigenbasis. Before normalisation, repeated multiplication gives

\[
\begin{aligned}
A^k x_0
&=\sum_{i=1}^n c_i\lambda_i^k v_i\\
&=\lambda_1^k\left(c_1v_1+
\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^k v_i\right).
\end{aligned}
\]

If \(c_1=v_1^Tx_0\ne0\), the dominant component is present from the start. Under the strict magnitude gap, every subordinate factor satisfies \(|\lambda_i/\lambda_1|<1\), so its magnitude raised to the \(k\)-th power tends to zero. Normalisation removes the common scale \(\lambda_1^k\), leaving the direction increasingly aligned with \(v_1\).

Consequently, for a real symmetric \(A\), direction convergence requires all of the following: \(|\lambda_1|>|\lambda_2|\), a non-zero initial projection onto \(v_1\), and no iterate for which \(Ax_k=0\). Under those assumptions, the direction error generally decreases asymptotically at a rate governed by

\[
\left|\frac{\lambda_2}{\lambda_1}\right|^k.
\]

This is an asymptotic rate description, not an unconditional finite-iteration error bound.

The ratio also gives a useful qualitative comparison between runs. A subordinate component multiplied repeatedly by a ratio of magnitude \(0.2\) fades much faster than one multiplied by a ratio of magnitude \(0.95\). The rate expression explains that contrast only when the stated symmetric setting, strict gap, non-zero dominant projection, and non-breakdown conditions hold. It does not tell you that an arbitrary requested accuracy will be reached after a particular number of steps without further analysis.

<!-- section: SEC-05 -->
## Failure modes and boundaries

Several behaviours that look similar in a trace have different causes. First, if \(\lambda_1<0\), successive normalised iterates may alternate sign. That alone is not failure: \(v_1\) and \(-v_1\) represent the same eigendirection. Comparing raw successive vectors can therefore be misleading.

Second, if \(v_1^Tx_0=0\), the initial state contains no dominant component. In exact arithmetic, multiplication by \(A\) cannot create that missing component, so the method will not converge to \(v_1\). This is not merely slow convergence.

Third, if \(|\lambda_1|=|\lambda_2|\), there is no unique dominant magnitude for the argument above to isolate. Iterates may remain in or oscillate within the invariant subspace associated with those magnitudes, rather than selecting one unique eigenvector. By contrast, when \(|\lambda_2/\lambda_1|\) is below but close to one, dominance is unique but convergence can be very slow. Equality and a small gap are distinct cases.

Finally, power iteration can be applied to some non-symmetric matrices, but the orthogonal real decomposition used here is not generally available. Defective matrices, complex dominant eigenvalues, and non-normal behaviour require additional care and lie outside this lesson. Do not generalise the symmetric convergence explanation to every non-symmetric matrix.

When diagnosing a run, ask questions in that order. Are successive vectors merely negatives of one another while representing the same improving direction? Was the dominant component absent from the initial vector? Is the dominant magnitude tied, so that selecting one vector is not guaranteed? Or is the magnitude ratio simply close to one, making valid convergence slow? These explanations lead to different conclusions, so a trace of vectors alone is not enough. Also verify that the matrix lies in the real symmetric setting before using the component argument as justification.

<!-- section: SEC-06 -->
## Estimating and checking an eigenpair

For a non-zero approximate eigenvector \(x_k\), estimate its eigenvalue using the Rayleigh quotient

\[
\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.
\]

Because successful iterates are normalised, this simplifies to \(\rho(x_k)=x_k^TAx_k\). For symmetric \(A\), as \(x_k\) approaches \(v_1\), the quotient approaches \(\lambda_1\).

An estimate is more useful when paired with a check. Define the eigenpair residual

\[
r_k=Ax_k-\rho(x_k)x_k.
\]

An exact eigenpair has zero residual, while \(\|r_k\|_2\) measures how nearly the defining eigenvector equation is satisfied. It is therefore a meaningful stopping measure. Unlike a test based only on \(x_k-x_{k-1}\), it is not confused merely because equivalent eigenvector representatives flip sign.

To see why zero is the correct reference value, substitute an exact pair into the residual: \(Av-\lambda v=0\). For an approximate pair, the residual is the mismatch left after the proposed scalar multiple is removed from the matrix-vector product. A small norm therefore supports a stopping decision about the pair currently held by the program. It does not force the eigenvector to use one preferred sign, and it should be interpreted together with the assumptions governing which eigenpair the iteration targets.

<!-- section: SEC-07 -->
## A safeguarded algorithm

Given \(A\), \(x_0\ne0\), a tolerance \(\varepsilon>0\), and a positive integer iteration cap \(K\), the control flow is:

1. Convert and validate the inputs, then normalise \(x_0\).
2. Compute \(y=Ax_k\); if \(\|y\|_2=0\), report breakdown before dividing.
3. Set \(x_{k+1}=y/\|y\|_2\).
4. Compute the Rayleigh estimate and residual.
5. Return when the residual norm is at most \(\varepsilon\); otherwise continue until \(K\) iterations have been performed, then return the final estimate.

The following block is self-contained. It preserves the four-value return structure and rejects invalid iteration parameters before entering the loop.

Read the implementation as a direct translation of the control flow. Array conversion gives floating-point matrix and vector data. Shape checks ensure that the multiplication is defined for one square matrix and one compatible one-dimensional vector. Parameter checks guarantee a positive tolerance and at least one loop iteration. The initial norm check precedes initial normalisation, just as the product norm check precedes every later normalisation. On either normal return path, the tuple contains the eigenvalue estimate, unit vector, residual norm, and number of iterations actually reported.

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

A = np.array([[4.0, 1.0],
              [1.0, 2.0]])
result = power_iteration(A, np.array([1.0, 1.0]))
print("Estimated dominant eigenvalue:", result[0])
print("Estimated eigenvector:", result[1])
print("Residual norm:", result[2])
print("Iterations:", result[3])
```

<!-- section: SEC-08 -->
## Worked consolidation

For the matrix and initial vector in the code, the exact eigenvalues are

\[
3+\sqrt{2}
\quad\text{and}\quad
3-\sqrt{2}.
\]

The first has the larger magnitude, so the iteration should estimate \(3+\sqrt{2}\), approximately \(4.4142\), and return a small residual under the default tolerance. The returned eigenvector may have either sign; both signs describe the same eigendirection.

Trace the data flow as you read the output. The initial vector is compatible and non-zero, each successful update restores unit norm, the Rayleigh quotient supplies the scalar estimate, and the residual checks the pair rather than only the vector. The matrix is real symmetric, its dominant magnitude is unique, and the chosen initial vector has a non-zero component in the dominant direction, so this example fits the convergence setting developed above. The iteration count tells you when the residual criterion was met; if it were not met, the function would still terminate at the stated cap and return its final values.

The complete workflow is therefore: identify the assumptions, update by a matrix-vector product and normalisation, interpret convergence through eigenvector components, distinguish failure modes from slow or sign-alternating progress, and judge the computed eigenpair using its Rayleigh estimate and residual.

As a final trace exercise, predict the meaning of each printed field before running the block. The eigenvalue should be near the larger exact value; the vector should have unit norm but an unconstrained sign; the residual should satisfy the default threshold on an early return; and the iteration count should not exceed the cap. Then connect each observation to one line of the algorithm. This turns the numerical output into evidence about the update, estimate, safeguard, or stopping condition instead of treating it as an unexplained answer.
