# Power iteration: structure, convergence, and diagnostics

Power iteration is a deliberately narrow eigenvalue method: it repeatedly applies a matrix to a vector so that, under suitable assumptions, the direction associated with the eigenvalue of largest magnitude becomes dominant. The method is simple enough to derive from a spectral decomposition, but that derivation also exposes exactly where it can be slow or fail. Our aim is therefore not merely to produce an iterate. We will connect the update to its assumptions, estimate the associated eigenvalue, and judge the result through a residual.

<!-- section: SEC-01 -->
## Eigenpairs and the direct route

For a real square matrix $A\in\mathbb{R}^{n\times n}$, a non-zero vector $v$ is an eigenvector if

$$
Av=\lambda v,
$$

where the scalar $\lambda$ is its associated eigenvalue. The condition $v\ne0$ is essential: the equation $A0=\lambda0$ holds for every scalar, so the zero vector carries no information about a particular eigenvalue.

Eigenvalues can also be characterised as roots of

$$
\det(A-\lambda I)=0,
$$

with $I$ the identity matrix of compatible size. For a small matrix this characteristic equation is a useful derivation route. For a large matrix, however, explicitly forming the characteristic polynomial is usually a poor numerical strategy. Power iteration instead works through repeated matrix-vector products to estimate a selected eigenpair; this is a numerical strategy, not an algebraic replacement of the determinant identity.

The contrast is worth keeping in view. The characteristic equation describes all eigenvalues through a determinant condition, whereas one run of power iteration seeks the direction selected by repeated multiplication. The iteration therefore answers a more focused computational question. We will still use the defining eigenpair equation as the standard against which its output is checked.

<!-- section: SEC-02 -->
## The spectral setting and the update

The cleanest analysis begins with a real symmetric matrix, $A=A^T$. The spectral theorem then supplies an orthonormal basis of real eigenvectors $v_1,\ldots,v_n$. If $Q$ has these vectors as columns, then

$$
A=Q\Lambda Q^T,\qquad
\Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n),
$$

and every vector has the expansion

$$
x=\sum_{i=1}^n c_i v_i,qquad c_i=v_i^Tx.
$$

Order the eigenvalues by magnitude and assume a strict first gap:

$$
|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.
$$

Thus $\lambda_1$ is dominant by absolute value, not necessarily the most positive eigenvalue. If two eigenvalues are $5$ and $-8$, power iteration targets $-8$ because $|-8|>|5|$.

Starting from $x_0\ne0$, one update is

$$
y_{k+1}=Ax_k,\qquad
x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.
$$

The normalization controls scale without changing the direction of $y_{k+1}$. It is defined only when $Ax_k\ne0$, a condition that will become an explicit breakdown check in the algorithm.

In eigenbasis coordinates, multiplication by the matrix has a transparent effect: it multiplies each coefficient by its associated eigenvalue. Normalization then rescales all coefficients by one common non-zero factor. Consequently, normalization cannot manufacture an absent component or change the ratios created by the eigenvalue magnitudes; it only keeps the numerical representation at unit length. This separation between directional change and scale control is central to reading the method correctly.

<!-- section: SEC-03 -->
## Why a dominant direction emerges

Expand the initial vector in the orthonormal eigenbasis, $x_0=\sum_i c_i v_i$. Before normalization, repeated multiplication gives

$$
A^k x_0
=\sum_{i=1}^n c_i\lambda_i^k v_i
=\lambda_1^k\left(c_1v_1+
\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^k v_i\right).
$$

This factorisation isolates the mechanism. If $c_1=v_1^Tx_0\ne0$ and $|\lambda_1|>|\lambda_2|$, every subordinate ratio has magnitude below one, so its contribution decays relative to the $v_1$ component. Normalization then removes the overall scale $\lambda_1^k$ while preserving the increasingly dominant direction.

The convergence statement must keep its hypotheses attached. For a real symmetric $A$, suppose the dominant magnitude is unique, the initial projection onto $v_1$ is non-zero, and no iterate produces $Ax_k=0$. Then the direction error generally decreases asymptotically at a rate governed by

$$
\left|\frac{\lambda_2}{\lambda_1}\right|^k.
$$

This describes an asymptotic rate, not an unconditional finite-iteration error bound. It also gives a practical comparison: a smaller magnitude ratio predicts faster eventual convergence, whereas a ratio just below one predicts slow separation of the two leading components.

For example, compare two valid symmetric settings having leading magnitude ratios one half and nine tenths, with non-zero dominant projections and no breakdown. After each successive power, the first rate factor decays more rapidly than the second. This comparison does not specify the exact error at a chosen finite step, because coefficients in the initial expansion also matter; it illustrates only the stated asymptotic mechanism. When analysing a new matrix, separate these two questions: whether the convergence hypotheses hold, and, if they do, what the leading magnitude ratio suggests about eventual speed.

<!-- section: SEC-04 -->
## Counterexamples that test the assumptions

First consider sign. If the dominant eigenvalue is negative, successive normalized iterates may alternate sign. That alone is not failure: $v_1$ and $-v_1$ represent the same eigendirection. A diagnostic based only on $\|x_{k+1}-x_k\|_2$ could therefore look large even while directional alignment improves.

Next consider the initial projection. If $v_1^Tx_0=0$, the dominant component is absent. In exact arithmetic, multiplication by $A$ cannot create that missing eigencomponent, so the iterates remain in the non-dominant invariant subspace rather than converging slowly to $v_1$.

Two different spectral cases should also remain distinct. When $|\lambda_1|=|\lambda_2|$, there is no unique dominant magnitude, and the method need not select a unique eigenvector; it may remain in or oscillate within the associated invariant subspace. When $|\lambda_2/\lambda_1|$ is merely close to one but still below it, the dominant magnitude is unique but convergence can be very slow.

Finally, the orthogonal derivation above is a scope boundary. Power iteration can be applied to some non-symmetric matrices, but a real orthonormal eigenbasis is not generally available. Defective matrices, complex dominant eigenvalues, and non-normal behaviour need additional care and are outside the present analysis. The symmetric proof must not be silently transferred to all non-symmetric problems.

These cases suggest an assumption audit before trusting an iteration history. Check first that the analysis is being made in the real symmetric setting. Next ask whether the largest magnitude is unique, rather than merely whether one eigenvalue is algebraically largest. Then ask whether the starting vector has a non-zero dominant projection and whether multiplication has produced a zero vector. A negative dominant eigenvalue changes the signs of successive representatives but does not change their common line. A tied dominant magnitude removes unique selection, while a separated ratio close to one retains selection but makes it slow. Naming the failed assumption gives a more precise diagnosis than simply saying that the method did not converge.

<!-- section: SEC-05 -->
## Estimating the eigenvalue and measuring quality

Given a non-zero approximate eigenvector $x_k$, estimate its eigenvalue with the Rayleigh quotient

$$
\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.
$$

For a unit-norm iterate this simplifies to $\rho(x_k)=x_k^TAx_k$. The denominator may be omitted only under that normalization. For symmetric $A$, if $x_k$ approaches $v_1$, then the quotient approaches $\lambda_1$.

An estimate is not yet a quality certificate. Form the eigenpair residual

$$
r_k=Ax_k-\rho(x_k)x_k.
$$

For an exact eigenpair, substituting $Av=\lambda v$ and $\rho(v)=\lambda$ gives the zero vector. Computationally, $\|r_k\|_2$ measures how closely the estimated pair satisfies the defining equation and supplies a meaningful stopping measure. This residual test should not be replaced by successive-vector similarity, because sign flips can distort vector differences without changing the eigendirection.

To interpret a reported step, read the vector, quotient, and residual together. The normalized vector proposes a direction; the Rayleigh quotient proposes the scalar paired with it; the residual substitutes both proposals back into the eigenpair equation. A residual norm below the chosen positive tolerance justifies the algorithm's stopping decision. A residual above tolerance says that this decision has not yet been reached, even if consecutive printed eigenvalue estimates look similar. Conversely, alternating vector signs need not prevent the residual from becoming small.

<!-- section: SEC-06 -->
## A safeguarded algorithm

Take $x_0\ne0$, a tolerance $\varepsilon>0$, and a positive maximum iteration count $K$. First normalize $x_0$. At each iteration, compute $y=Ax_k$ and check whether $\|y\|_2=0$; if so, report breakdown before attempting any division. Otherwise set $x_{k+1}=y/\|y\|_2$, compute $\rho_{k+1}=x_{k+1}^TAx_{k+1}$, and then compute the residual.

Stop successfully when $\|r_{k+1}\|_2\le\varepsilon$. If that never occurs, stop after $K$ iterations and return the final diagnostics. Both exits matter: the tolerance expresses the requested approximate-eigenpair quality, while the iteration cap prevents an unbounded run when convergence is slow or the assumptions are unsuitable.

A careful trace preserves this order. Normalize the valid starting vector once. For each numbered step, form the matrix-vector product, inspect its norm, normalize only after the non-zero check, then calculate the quotient and residual from the new unit vector. Compare the scalar residual norm with the tolerance. If the comparison succeeds, return that step number; otherwise begin the next step, unless the cap has been reached. Reaching the cap is not the same claim as satisfying the tolerance, so the returned residual remains necessary for interpreting a capped result.

<!-- section: SEC-07 -->
## NumPy operations used by the implementation

The implementation needs only a small set of array operations. Convert inputs to floating-point arrays, inspect shapes before arithmetic, use `@` for a compatible two-dimensional matrix times a one-dimensional vector, and use `np.linalg.norm` for the vector's Euclidean norm. Test a scalar norm against zero before dividing by it. Array comparisons are elementwise, so a program needing one truth value should compare a scalar diagnostic or explicitly reduce an array result.

Invalid shapes or values should raise a specific exception. A function can return several diagnostics in one tuple, which the caller can unpack into the same number of names. This compact example exercises the required operations without invoking an eigensolver:

Shape checks distinguish objects that may look similar when printed. A square matrix has two dimensions and equal row and column counts; the compatible vector here has one dimension and length equal to the matrix dimension. After matrix-vector multiplication, the result is again one-dimensional. The norm is a scalar, so comparing it with zero supplies a single truth value suitable for a safeguard. These facts explain why conversion and validation occur before the arithmetic rather than after an operation has already failed ambiguously.

```python
import numpy as np

A = np.asarray([[2, 1], [1, 2]], dtype=float)
x = np.asarray([1, -1], dtype=float)
if A.ndim != 2 or A.shape[0] != A.shape[1]:
    raise ValueError("A must be square")
if x.shape != (A.shape[0],):
    raise ValueError("x has incompatible dimensions")

y = A @ x
n = np.linalg.norm(y)
if n == 0.0:
    raise RuntimeError("cannot normalize a zero vector")
unit_y = y / n
diagnostics = (float(n), unit_y, 1, "normalized")
norm_value, vector_value, step_count, status = diagnostics
assert np.isclose(np.linalg.norm(vector_value), 1.0)
```

<!-- section: SEC-08 -->
## Validated initialization and iteration diagnostics

The complete function adds checks that the matrix is square, the initial vector has compatible one-dimensional shape, and the initial vector is non-zero. It also requires a positive tolerance and a positive integer iteration cap. Inside the loop, breakdown is tested before normalization; successful and capped runs both return the eigenvalue estimate, vector, residual norm, and iteration count.

The four returned values have distinct diagnostic roles. The estimate and vector form the proposed eigenpair; the residual norm measures its defining-equation defect; and the iteration count shows where the run stopped. The test calls below exercise three control paths. One convergent run may return early, a deliberately strict tolerance with a two-step cap must return at step two, and a zero matrix-vector product must raise a breakdown error before division. Input errors remain separate from iteration breakdown: incompatible data raises a value error, while a validly shaped run that produces a zero product raises a runtime error.

```python
import numpy as np

def power_iteration(A, x0, tolerance=1e-10, max_iterations=1000):
    A = np.asarray(A, dtype=float)
    x = np.asarray(x0, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("A must be square")
    if x.shape != (A.shape[0],):
        raise ValueError("x0 has incompatible dimensions")
    x_norm = np.linalg.norm(x)
    if x_norm == 0.0:
        raise ValueError("x0 must be non-zero")
    if tolerance <= 0.0:
        raise ValueError("tolerance must be positive")
    if (isinstance(max_iterations, (bool, np.bool_)) or
            not isinstance(max_iterations, (int, np.integer)) or
            max_iterations <= 0):
        raise ValueError("max_iterations must be a positive integer")
    x = x / x_norm

    for iteration in range(1, max_iterations + 1):
        y = A @ x
        y_norm = np.linalg.norm(y)
        if y_norm == 0.0:
            raise RuntimeError("power iteration broke down because A @ x is zero")
        x = y / y_norm
        eigenvalue = float(x @ (A @ x))
        residual = A @ x - eigenvalue * x
        residual_norm = float(np.linalg.norm(residual))
        if residual_norm <= tolerance:
            return eigenvalue, x, residual_norm, iteration

    return eigenvalue, x, residual_norm, max_iterations

early = power_iteration([[3.0, 0.0], [0.0, 1.0]], [1.0, 1.0])
capped = power_iteration([[3.0, 0.0], [0.0, 1.0]], [1.0, 1.0],
                         tolerance=1e-30, max_iterations=2)
assert capped[3] == 2
try:
    power_iteration([[1.0, 0.0], [0.0, 0.0]], [0.0, 1.0])
except RuntimeError:
    pass
else:
    raise AssertionError("expected breakdown")
```

<!-- section: SEC-09 -->
## Worked consolidation

Consider

$$
A=\begin{pmatrix}4&1\\1&2\end{pmatrix},\qquad x_0=(1,1)^T.
$$

The characteristic equation gives the exact eigenvalues $3+\sqrt2$ and $3-\sqrt2$, so the dominant value is $3+\sqrt2$. The normalized starting vector is $(1,1)^T/\sqrt2$. Its first matrix-vector product is $(5,3)^T/\sqrt2$, and normalizing gives $(5,3)^T/\sqrt{34}$. Repeating the update increasingly suppresses the component associated with $3-\sqrt2$.

Run the function from the preceding section with this matrix and starting vector. The returned eigenvalue should approach $3+\sqrt2$, while the residual norm should fall below the default tolerance before the iteration cap. The eigenvector may be returned with either sign; quality is judged by the residual, not by agreement with a prescribed sign. The following self-contained check reproduces the calculation directly.

```python
import numpy as np

def power_iteration(A, x0, tolerance=1e-10, max_iterations=1000):
    A = np.asarray(A, dtype=float)
    x = np.asarray(x0, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("A must be square")
    if x.shape != (A.shape[0],):
        raise ValueError("x0 has incompatible dimensions")
    x_norm = np.linalg.norm(x)
    if x_norm == 0.0:
        raise ValueError("x0 must be non-zero")
    if tolerance <= 0.0:
        raise ValueError("tolerance must be positive")
    if (isinstance(max_iterations, (bool, np.bool_)) or
            not isinstance(max_iterations, (int, np.integer)) or
            max_iterations <= 0):
        raise ValueError("max_iterations must be a positive integer")
    x = x / x_norm
    for iteration in range(1, max_iterations + 1):
        y = A @ x
        y_norm = np.linalg.norm(y)
        if y_norm == 0.0:
            raise RuntimeError("power iteration broke down because A @ x is zero")
        x = y / y_norm
        eigenvalue = float(x @ (A @ x))
        residual = A @ x - eigenvalue * x
        residual_norm = float(np.linalg.norm(residual))
        if residual_norm <= tolerance:
            return eigenvalue, x, residual_norm, iteration
    return eigenvalue, x, residual_norm, max_iterations

A = np.array([[4.0, 1.0], [1.0, 2.0]])
estimate, vector, residual_norm, iterations = power_iteration(A, [1.0, 1.0])
exact_dominant = 3.0 + np.sqrt(2.0)
assert abs(estimate - exact_dominant) < 1e-9
assert residual_norm <= 1e-10
print(estimate, vector, residual_norm, iterations)
```

The worked calculation ties the lesson together: spectral structure explains which component is amplified, normalization keeps the representation controlled, the Rayleigh quotient supplies the eigenvalue estimate, and the residual tests whether the returned pair nearly satisfies its defining equation.

When reporting this result, include the assumptions and the stopping evidence rather than only the estimated scalar. Here the matrix is real symmetric, its two eigenvalue magnitudes are distinct, and the supplied starting vector has a non-zero component in the dominant direction. The computation then reports both an estimate near the exact dominant value and a residual below tolerance. That chain of reasoning connects the derivation, the code path, and the numerical diagnostic without treating any one of them as sufficient on its own.
