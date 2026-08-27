# Power Iteration Through an Idealized Modal Lens

Power iteration is a repeated matrix-vector calculation for finding a dominant eigendirection. In this lesson, an idealized modal-analysis interpretation will help connect the algebra to mode shapes, while the assumptions and limits of that interpretation remain explicit.

<!-- section: SEC-01 -->
## Eigenpairs and the dominant direction

For a real square matrix (A\in\mathbb{R}^{n\times n}), a non-zero vector (v) is an eigenvector when

\[
Av=\lambda v.
\]

The scalar \(\lambda\) is its associated eigenvalue. The requirement \(v\ne0\) matters: the zero vector satisfies the displayed equation for every scalar, so it carries no information that identifies an eigenvalue. In an idealized vibration model, an eigenvector can be viewed as a mode-shape direction, but here that interpretation is only a bridge to the matrix problem.

Power iteration targets the eigenvalue with the largest **magnitude**, not necessarily the most positive eigenvalue. For example, if two eigenvalues are \(5\) and \(-8\), then \(-8\) is dominant because \(|-8|>|5|\). The corresponding eigenvector gives the dominant eigendirection sought by the iteration.

The defining equation also gives a useful way to read an eigenpair. Multiplication by \(A\) takes the non-zero vector to a scalar multiple of itself: the scalar records the eigenvalue, while the vector records the direction. Power iteration is designed to approximate both pieces, first concentrating on the direction and later estimating its scalar. Throughout the lesson, “dominant” will always mean dominant in absolute value.

<!-- section: SEC-02 -->
## Projection coordinates in the symmetric setting

First recall the geometry needed to describe components. Real vectors \(u\) and \(v\) are orthogonal when \(u^Tv=0\). A family \(v_1,\ldots,v_k\) is orthonormal when different vectors have zero cross-products and every vector has unit Euclidean norm:

\[
v_i^Tv_j=0\quad(i\ne j),\qquad \|v_i\|_2=1.
\]

For a unit vector \(v\), the scalar \(v^Tx\) is the coefficient of \(x\) in the \(v\) direction. Thus, for \(v=(1,0)^T\) and \(x=(3,4)^T\), the coefficient is \(v^Tx=3\).

This coefficient is a compact coordinate calculation. Test orthogonality by taking a cross-product; test unit length by taking a vector's norm. Only when the direction vector has unit length does the coefficient take the simple form \(v^Tx\) used here. These checks prepare the notation needed for an orthonormal eigenvector basis without yet making any claim about which matrices possess one.

Now restrict attention to a real symmetric matrix, \(A=A^T\). The spectral theorem supplies an orthonormal basis of real eigenvectors. With these eigenvectors as the columns of an orthogonal matrix \(Q\),

\[
A=Q\Lambda Q^T,\qquad
\Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n).
\]

Every vector therefore has the expansion

\[
x=\sum_{i=1}^n c_i v_i,qquad c_i=v_i^Tx.
\]

This clean orthogonal description depends on symmetry. Order the eigenvalues by magnitude and assume a strict first gap:

\[
|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.
\]

The strict inequality makes the dominant magnitude unique; it must not be replaced by an ordering based on algebraic value.

Together, orthonormality and symmetry make the expansion especially readable. Each \(c_i\) is found by one projection calculation, and the full vector is recovered by combining those coefficients with their basis vectors. The matrix decomposition and coefficient formula are being used only under the real symmetric hypothesis. That restriction is part of every later appeal to this clean coordinate picture.

<!-- section: SEC-03 -->
## Normalize each matrix-vector update

For \(x=(x_1,\ldots,x_n)^T\), the Euclidean norm is

\[
\|x\|_2=\sqrt{x_1^2+\cdots+x_n^2}=\sqrt{x^Tx}.
\]

If \(x\ne0\), set \(u=x/\|x\|_2\); then \(\|u\|_2=1\). For instance, \((3,4)^T\) has norm \(5\) and normalizes to \((3/5,4/5)^T\). The zero vector has norm zero and cannot be normalized, so a calculation must stop before dividing by that norm.

Starting with a non-zero \(x_0\), one power step is

\[
y_{k+1}=Ax_k,\qquad
x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.
\]

This is valid only when \(y_{k+1}\ne0\). Normalization controls scale without changing the direction produced by the matrix-vector multiplication. If the dominant eigenvalue is negative, successive normalized vectors may alternate sign. That alone is not failure: \(v_1\) and \(-v_1\) represent the same eigendirection and hence the same mode-shape direction.

To trace one iteration, keep the two operations separate. First multiply the current unit vector by the matrix and call the result \(y\). Next compute its Euclidean norm, check that the norm is not zero, and divide. The new vector has unit norm and points along the direction produced by the multiplication. Repeating these two operations creates the sequence; normalization is never a substitute for the multiplication itself.

<!-- section: SEC-04 -->
## Estimate an eigenvalue and measure the residual

For real vectors of equal length, \(x^Ty\) is the scalar sum of their componentwise products. To compute \(x^TAx\), first form \(y=Ax\), then calculate \(x^Ty\); the square matrix and vector dimensions must be compatible. Also, \(x^Tx=\|x\|_2^2\ge0\). As a short example, with

\[
A=\begin{bmatrix}2&0\\0&1\end{bmatrix},\qquad x=(1,2)^T,
\]

we obtain \(Ax=(2,2)^T\) and \(x^TAx=1(2)+2(2)=6\).

For a non-zero approximate eigenvector \(x_k\), estimate its eigenvalue with the Rayleigh quotient

\[
\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.
\]

When \(x_k\) is normalized, the denominator is one, so \(\rho(x_k)=x_k^TAx_k\). For a symmetric matrix, as \(x_k\) approaches \(v_1\), this estimate approaches \(\lambda_1\).

The eigenpair residual is

\[
r_k=Ax_k-\rho(x_k)x_k.
\]

An exact eigenpair has zero residual. Consequently, \(\|r_k\|_2\) is a useful quality measure and stopping signal. Merely comparing successive vectors is weaker because a sign flip can make equivalent eigendirections look far apart.

The residual should be read as a direct consistency check. Compute the matrix action \(Ax_k\), compute the proposed eigenvalue scaling \(\rho(x_k)x_k\), subtract them, and measure what remains. A small norm means those two vectors nearly agree in this equation. This does not require choosing whether \(x_k\) or \(-x_k\) is the preferred representative, because both signs describe the same direction and lead to the same residual norm.

<!-- section: SEC-05 -->
## A safeguarded NumPy implementation

A practical algorithm first converts the inputs to floating NumPy arrays. It checks that the matrix is square, the starting vector is one-dimensional with compatible length, and the starting vector is non-zero. It then normalizes that vector. Each iteration forms \(y=Ax\), checks for zero norm before division, normalizes, computes the Rayleigh estimate and residual norm, and returns early when the residual norm is at most a positive tolerance. A maximum iteration count supplies the fallback stop. The return values are the estimate, normalized vector, residual norm, and iteration count.

```python
import numpy as np

def power_iteration(A, x0, tolerance=1e-10, max_iterations=1000):
    A = np.asarray(A, dtype=float)
    x = np.asarray(x0, dtype=float)

    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("A must be square")
    if x.ndim != 1 or x.shape[0] != A.shape[0]:
        raise ValueError("x0 must be one-dimensional and compatible with A")
    if tolerance <= 0 or max_iterations < 1:
        raise ValueError("use a positive tolerance and iteration count")

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
        Ax = A @ x
        eigenvalue = float(x @ Ax)
        residual_norm = float(np.linalg.norm(Ax - eigenvalue * x))
        if residual_norm <= tolerance:
            return eigenvalue, x, residual_norm, iteration

    return eigenvalue, x, residual_norm, max_iterations
```

Notice that the breakdown check occurs before normalization, never after division. Both exit routes preserve the same four-value return structure.

Read the loop in the same order as the mathematics. The matrix-vector product proposes a new direction; the zero-norm check protects the next division; normalization fixes the scale; and the Rayleigh quotient supplies the current scalar estimate. The residual then decides whether the pair is adequate for the requested tolerance. If it is not, the next iteration begins. Reaching the iteration limit does not silently alter the result format: the function still reports the final estimate, vector, residual norm, and number of completed iterations.

<!-- section: SEC-06 -->
## Why a dominant component emerges

In the real symmetric setting, expand the starting vector in the orthonormal eigenbasis. The unnormalized sequence is

\[
A^kx_0
=\sum_{i=1}^n c_i\lambda_i^kv_i
=\lambda_1^k\left(c_1v_1+
\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^kv_i\right).
\]

The dominant coefficient must be present: \(c_1=v_1^Tx_0\ne0\). With the strict magnitude gap, every subordinate ratio has magnitude below one, so its power decays as \(k\) grows. Normalization controls the overall factor \(\lambda_1^k\) while the direction becomes dominated by \(v_1\).

The convergence statement therefore has several inseparable hypotheses: \(A\) is real symmetric, \(|\lambda_1|>|\lambda_2|\), the initial projection onto \(v_1\) is non-zero, and no iterate produces \(Ax_k=0\). Under these conditions, direction error generally decreases asymptotically at a rate governed by

\[
\left|\frac{\lambda_2}{\lambda_1}\right|^k.
\]

This is an asymptotic rate description, not an unconditional finite-iteration error bound.

The factored expression explains the role of the ratio without requiring a full convergence proof. Relative to the first component, every other component carries a power of \(\lambda_i/\lambda_1\). The strict ordering makes the magnitude of each such ratio less than one. As the exponent increases, those relative contributions decay, provided the first component was present initially. A smaller value of \(|\lambda_2/\lambda_1|\) indicates faster asymptotic directional separation than a value close to one, but the formula is not a promise about a specific finite step.

<!-- section: SEC-07 -->
## Diagnose limitations before trusting the result

Three checks clarify what can go wrong. First, if \(v_1^Tx_0=0\) exactly, the starting vector contains no dominant component. Exact repeated multiplication cannot create that missing component, so the method does not converge to \(v_1\); this is not merely slow convergence.

Second, if \(|\lambda_1|=|\lambda_2|\), the dominant magnitude is tied and the iteration need not select a unique eigenvector. This differs from the separated case in which \(|\lambda_2/\lambda_1|\) is below but close to one: then convergence can occur, but very slowly.

Third, the orthogonal eigenbasis explanation above is restricted to real symmetric matrices. Power iteration can apply to some non-symmetric matrices, but an orthogonal decomposition is not generally available. Defective matrices, complex dominant eigenvalues, and non-normal behavior require additional care and lie outside this lesson. The idealized modal picture must therefore not be taken as a claim that every engineering eigenproblem is symmetric or appropriately solved by basic power iteration.

These cases call for different diagnoses. A missing projection removes the required component altogether in exact arithmetic. A tied dominant magnitude removes uniqueness. A close but strict magnitude ratio preserves separation while making its effect slow to appear. A non-symmetric problem removes the basis for the clean orthogonal explanation used here. Before trusting a computed mode-like direction, identify which setting applies, retain the residual as the numerical check, and avoid treating a changing sign by itself as evidence of failure.

<!-- section: SEC-08 -->
## Consolidation with an idealized two-coordinate model

Consider

\[
A=\begin{bmatrix}4&1\\1&2\end{bmatrix},\qquad x_0=(1,1)^T.
\]

The exact eigenvalues are supplied as \(3+\sqrt2\) and \(3-\sqrt2\). Their magnitudes show locally that \(3+\sqrt2\) is dominant. Running the safeguarded implementation with this starting vector and its default settings should produce an estimate near that value and a small residual. The sign of the returned eigenvector is immaterial.

```python
import numpy as np

def power_iteration(A, x0, tolerance=1e-10, max_iterations=1000):
    A = np.asarray(A, dtype=float)
    x = np.asarray(x0, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("A must be square")
    if x.ndim != 1 or x.shape[0] != A.shape[0]:
        raise ValueError("x0 must be one-dimensional and compatible with A")
    if tolerance <= 0 or max_iterations < 1:
        raise ValueError("use a positive tolerance and iteration count")
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
        Ax = A @ x
        eigenvalue = float(x @ Ax)
        residual_norm = float(np.linalg.norm(Ax - eigenvalue * x))
        if residual_norm <= tolerance:
            return eigenvalue, x, residual_norm, iteration
    return eigenvalue, x, residual_norm, max_iterations

A = np.array([[4.0, 1.0], [1.0, 2.0]])
estimate, mode, residual, steps = power_iteration(A, np.array([1.0, 1.0]))
exact_dominant = 3.0 + np.sqrt(2.0)
assert abs(estimate - exact_dominant) < 1e-8
assert residual <= 1e-10
print(estimate, mode, residual, steps)
```

The estimate answers “which eigenvalue?”, the normalized vector supplies the corresponding direction, and the residual reports how closely those two quantities satisfy the eigenpair equation.

For this supplied example, the three outputs reinforce one another. The estimate can be compared with \(3+\sqrt2\), the vector can be interpreted only up to sign, and the residual can be checked against the stopping tolerance. Agreement of the estimate and a small residual complete the calculation for this idealized model; they do not erase the symmetry, dominance, starting-projection, and non-breakdown assumptions established earlier.
