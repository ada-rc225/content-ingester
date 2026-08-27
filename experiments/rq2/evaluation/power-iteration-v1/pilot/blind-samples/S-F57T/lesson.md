# Power Iteration: Structure, Convergence, and Diagnostics

Power iteration is a compact example of a recurring idea in applied mathematics: use a simple repeated operation, expose its spectral structure, and diagnose the approximation without knowing the exact answer in advance. Our aim is to understand both the mechanism and its boundaries, then turn that understanding into a guarded numerical procedure.

<!-- section: SEC-01 -->
## Why iterate toward an eigenpair?

Let $A\in\mathbb{R}^{n\times n}$. A non-zero vector $v\in\mathbb{R}^n$ is an eigenvector of $A$ if there is a scalar $\lambda$ such that

$$
Av=\lambda v.
$$

The scalar $\lambda$ is the eigenvalue associated with $v$. Requiring $v\ne 0$ matters: the zero vector satisfies $A0=\lambda0$ for every scalar, so that equation would carry no information about any particular eigenvalue.

Eigenvalues are roots of the characteristic equation

$$
\det(A-\lambda I)=0,
$$

where $I$ is the identity matrix of compatible dimension. For large matrices, however, explicitly forming the characteristic polynomial is usually a poor numerical strategy. Power iteration instead uses repeated matrix-vector products to estimate a selected eigenpair; this is a numerical strategy, not an algebraic replacement of the characteristic equation.

The method targets the eigenvalue of largest **magnitude**, not necessarily the most positive eigenvalue. If two eigenvalues are $5$ and $-8$, then $-8$ is dominant because $|-8|>|5|$. Keeping this distinction visible prevents a common mistake later when signs begin to alternate.

There are therefore two complementary views of the same problem. The characteristic equation states exactly which scalars are eigenvalues, whereas the iterative view asks whether repeated applications of the matrix reveal one selected eigendirection. The second view is especially natural when matrix-vector multiplication is the operation we want to repeat. It does not attempt to recover every root at once. Instead, it exploits the different ways in which the matrix scales components of a vector, with “largest” interpreted through absolute value from the outset.

<!-- section: SEC-02 -->
## Spectral coordinates for the symmetric case

The clean derivation begins with a real symmetric matrix, $A=A^T$. The spectral theorem then supplies an orthonormal basis of real eigenvectors. Writing those eigenvectors as the columns of an orthogonal matrix $Q$ gives

$$
A=Q\Lambda Q^T,
\qquad
\Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n).
$$

Consequently every vector $x$ has the expansion

$$
x=\sum_{i=1}^n c_i v_i,
\qquad c_i=v_i^Tx.
$$

These spectral coordinates reveal what multiplication by $A$ does: it scales each eigenvector component independently by its eigenvalue. Order the eigenvalues by magnitude as

$$
|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.
$$

The strict first inequality is essential: it says that $\lambda_1$ is unique in magnitude. “Dominant” will always refer to this magnitude ordering, never to algebraic ordering.

Orthonormality makes the coordinates particularly transparent. Taking the inner product of the expansion with one basis vector isolates its coefficient, which is why the formula $c_i=v_i^Tx$ accompanies the decomposition. Once a vector has been written this way, applying $A$ replaces each coefficient $c_i$ by $c_i\lambda_i$. Repeating the operation replaces it by $c_i\lambda_i^k$. The basis vectors themselves do not compete by rotating into one another in this representation; the comparison is between the magnitudes of their scalar multipliers. That is the structural reason the strict ordering will control the iteration.

<!-- section: SEC-03 -->
## The normalised power update

Choose a non-zero initial vector $x_0$. Provided the next matrix-vector product is non-zero, repeat

$$
y_{k+1}=Ax_k,
\qquad
x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.
$$

The first operation amplifies or suppresses the spectral components according to their eigenvalues. The second controls scale: it makes $x_{k+1}$ a unit vector but does not change the direction of $y_{k+1}$. Normalisation is therefore numerically useful without altering the direction-selection mechanism.

It is helpful to separate these two roles while tracing an iteration. First calculate the matrix-vector product and regard its entries as an unnormalised candidate. Then compute its Euclidean norm. If that norm is non-zero, division produces the next unit vector. Multiplying by a non-zero scalar changes length and possibly sign, but not the eigendirection being represented. If the product is the zero vector, however, the denominator vanishes and the update cannot be completed; this case must be detected rather than hidden inside the normalisation.

<!-- section: SEC-04 -->
## Why a dominant component emerges

Suppose $x_0=\sum_i c_i v_i$ in the real symmetric eigenbasis. Before normalisation, repeated multiplication gives

$$
A^k x_0
=\sum_{i=1}^n c_i\lambda_i^k v_i
=\lambda_1^k\left(c_1v_1+
\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^k v_i\right).
$$

If $c_1=v_1^Tx_0\ne0$ and $|\lambda_1|>|\lambda_2|$, every subordinate ratio has magnitude below one. Its power therefore decays, while the dominant component remains. Normalising removes the overall factor $\lambda_1^k$ and exposes the surviving eigendirection.

The convergence statement must retain all of its hypotheses. For a real symmetric $A$, assume a unique dominant magnitude $|\lambda_1|>|\lambda_2|$, a non-zero initial projection onto $v_1$, and no iterate for which $Ax_k=0$. Under these conditions, the direction error generally decreases asymptotically at a rate governed by

$$
\left|\frac{\lambda_2}{\lambda_1}\right|^k.
$$

This explains a trend, not an unconditional finite-iteration error bound. A smaller magnitude ratio predicts faster asymptotic separation of the dominant component.

The factored expression is also a checklist for reading the convergence claim. The factor outside the parentheses controls overall scale, so normalisation removes its size from consideration. Inside the parentheses, the desired term is present only when its coefficient is non-zero. Every competing term carries a power of an eigenvalue ratio, and the strict magnitude gap is what makes those powers decay. Finally, the update must remain defined at every step. If any one of these ingredients is removed, the displayed algebra no longer supports the same conclusion. In particular, the rate describes the eventual behaviour of direction error under the stated assumptions; it should not be read as a guaranteed numerical error after a prescribed small number of steps.

<!-- section: SEC-05 -->
## Counterexamples and scope boundaries

Several cases sharpen the assumptions. First, if the dominant eigenvalue is negative, successive normalised iterates may alternate sign. That is not failure: $v_1$ and $-v_1$ describe the same eigendirection. A diagnostic based only on $\|x_{k+1}-x_k\|_2$ could therefore be misleading.

Second, if $v_1^Tx_0=0$, the initial vector contains no dominant component. In exact arithmetic, multiplication by $A$ cannot create the missing eigencomponent, so the iterates do not converge to $v_1$. This is structural failure, not merely slow convergence.

Third, distinguish two spectral-gap cases. If $|\lambda_1|=|\lambda_2|$, the method need not select a unique eigenvector; it may remain in or oscillate within the invariant subspace associated with the tied dominant magnitudes. If instead $|\lambda_2/\lambda_1|<1$ but is close to one, the dominant direction is separated, yet convergence can be very slow.

Finally, power iteration can be applied to some non-symmetric matrices, but the orthogonal decomposition used above is not generally available. Defective matrices, complex dominant eigenvalues, and non-normal behaviour require additional care and lie outside this derivation. The symmetric argument must not be silently generalised to every non-symmetric matrix.

These cases diagnose different phenomena and should not be merged into one vague label of “non-convergence.” Alternating signs can coexist with improving alignment. An exactly missing dominant projection keeps the sequence inside a non-dominant invariant subspace. Repeated dominant magnitude removes the uniqueness needed to select one direction, while a separated but small gap retains that uniqueness and merely weakens the asymptotic rate. The final scope boundary is different again: it warns that the orthonormal spectral coordinates used in the derivation are not a universal model for arbitrary matrices. Naming the violated assumption is more informative than observing only that an iterate behaves unexpectedly.

<!-- section: SEC-06 -->
## Estimating the eigenvalue and testing the residual

Once a non-zero approximate eigenvector $x_k$ is available, estimate its eigenvalue with the Rayleigh quotient

$$
\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.
$$

Because power iteration normalises its vectors, $x_k^Tx_k=1$ and the quotient simplifies to $\rho(x_k)=x_k^TAx_k$. For symmetric $A$, if $x_k$ approaches $v_1$, then this estimate approaches $\lambda_1$.

An estimate still needs a quality measure. Define the eigenpair residual by

$$
r_k=Ax_k-\rho(x_k)x_k.
$$

For an exact eigenpair, the residual is zero. Computationally, $\|r_k\|_2$ measures how nearly the proposed pair satisfies the defining equation, so stopping when it falls below a chosen tolerance is meaningful. Unlike a raw difference between successive vectors, this residual remains interpretable when the iterate flips sign.

The quotient and residual answer distinct but connected questions. The quotient supplies the scalar paired with the current vector, while the residual substitutes both approximations back into the eigenvector equation. This makes the stopping decision about the defining relation rather than about visual stability of the vector entries. A small residual does not require choosing whether $x_k$ or $-x_k$ is the preferred representative: changing both vector terms by the same sign leaves their mismatch equally small. For floating-point computation, the tolerance must be positive and the iteration cap still matters, because a requested threshold may not be reached within the available steps.

<!-- section: SEC-07 -->
## A guarded numerical algorithm

A robust procedure accepts $A$, a non-zero $x_0$, a positive tolerance $\varepsilon$, and a positive integer iteration cap $K$. It converts inputs to floating arrays; checks that $A$ is square and $x_0$ is a compatible one-dimensional vector; normalises $x_0$; and then performs multiplication, a breakdown check, normalisation, Rayleigh estimation, and residual testing. The zero-product check must occur before division. A successful tolerance test returns early; otherwise the final approximation is returned after exactly $K$ iterations.

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
    if not isinstance(max_iterations, (int, np.integer)) or max_iterations <= 0:
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
```

The four returned values record the Rayleigh estimate, unit eigenvector approximation, residual norm, and iteration count. Invalid shapes and a zero starting vector produce `ValueError`; a zero matrix-vector product during iteration produces `RuntimeError`. These outcomes distinguish bad inputs, mathematical breakdown, residual convergence, and exhaustion of the iteration budget.

Reading the loop in mathematical order helps connect the implementation to the derivation. The initial normalisation establishes the unit-vector convention. Each pass forms the next unnormalised vector, refuses to divide when its norm is zero, and only then constructs the next direction. Because that direction is normalised, the code uses the simplified Rayleigh expression. It forms the residual from the same vector and estimate, checks the tolerance, and reports the current iteration if the test succeeds. If no test succeeds, the loop has still produced a final four-part result at the declared cap. Validating a positive integer cap before the loop guarantees that these return values have actually been computed.

<!-- section: SEC-08 -->
## Worked consolidation

Consider

$$
A=\begin{pmatrix}4&1\\1&2\end{pmatrix},
\qquad x_0=\begin{pmatrix}1\\1\end{pmatrix}.
$$

The exact eigenvalues are

$$
3+\sqrt{2}
\quad\text{and}\quad
3-\sqrt{2}.
$$

Thus the expected dominant value is $3+\sqrt{2}\approx4.4142$. The matrix is symmetric, the dominant magnitude is unique, and the starting vector has a non-zero component in the dominant eigendirection. The following independent computation applies the update and residual stop directly.

```python
import numpy as np

A = np.array([[4.0, 1.0], [1.0, 2.0]])
x = np.array([1.0, 1.0])
x = x / np.linalg.norm(x)
tolerance = 1e-10
max_iterations = 1000

for iteration in range(1, max_iterations + 1):
    y = A @ x
    y_norm = np.linalg.norm(y)
    if y_norm == 0:
        raise RuntimeError("power iteration broke down because A @ x is zero")
    x = y / y_norm
    eigenvalue = float(x @ (A @ x))
    residual_norm = float(np.linalg.norm(A @ x - eigenvalue * x))
    if residual_norm <= tolerance:
        break

print("Estimated dominant eigenvalue:", eigenvalue)
print("Estimated eigenvector:", x)
print("Residual norm:", residual_norm)
print("Iterations:", iteration)
```

The estimate should be close to $3+\sqrt{2}$ and the reported residual should be small. The eigenvector may appear with either sign; that ambiguity does not change its eigendirection. Together, the spectral derivation and the residual diagnostic explain both why this approximation is expected and how its computed quality is assessed.

This example closes the full reasoning chain. The exact eigenvalues identify the target by magnitude, while the spectral assumptions explain why the chosen starting vector can reveal it. The program follows the normalised update rather than constructing the characteristic polynomial, and the Rayleigh quotient turns the final direction into an eigenvalue estimate. Most importantly, the residual checks that the reported scalar-vector pair nearly satisfies the original eigenvector equation. The exact answer is useful here for comparison, but the residual is the diagnostic that the iterative algorithm can compute without being given that answer.
