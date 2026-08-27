# Power iteration: structure, convergence, and diagnostics

Power iteration is a compact example of numerical linear algebra in which an algorithm, a spectral argument, and practical diagnostics fit together. The central operation is only a matrix-vector product, but understanding when the iteration works requires careful attention to magnitude, initial data, and the distinction between a vector and its direction. We will develop those ideas in that order and finish with an executable implementation.

<!-- section: SEC-01 -->
## Eigenpairs and the motivation for iteration

Let $A\in\mathbb{R}^{n\times n}$. A non-zero vector $v\in\mathbb{R}^n$ is an eigenvector of $A$ if there is a scalar $\lambda$ such that

$$
Av=\lambda v.
$$

The scalar $\lambda$ is the associated eigenvalue. Requiring $v\ne 0$ is essential: the zero vector satisfies $A0=\lambda 0$ for every scalar, so that equation would carry no information about an eigenvalue.

Algebraically, eigenvalues are roots of

$$
\det(A-\lambda I)=0,
$$

where $I$ has the same dimension as $A$. For a small matrix, this characteristic equation can be useful. For a large matrix, explicitly forming its polynomial is usually a poor numerical strategy. An iterative method instead uses repeated matrix-vector products to estimate a selected eigenpair.

Power iteration selects by absolute value. Its target is an eigenvalue of largest magnitude, not necessarily the most positive eigenvalue. If two eigenvalues are $5$ and $-8$, then $-8$ is dominant because $|-8|>|5|$. This distinction between algebraic order and magnitude order will govern every convergence statement below.

A useful preliminary check is to separate verification from discovery. If a candidate pair is supplied, multiply the candidate vector by the matrix and compare the result with the proposed scalar multiple. That tests the defining relation, provided the candidate vector is not zero. Power iteration addresses a different task: it seeks a particular eigenpair without first constructing all roots of a characteristic polynomial. Keep that numerical motivation in view, because the attraction of the method lies in repeated matrix-vector products rather than determinant expansion.

<!-- section: SEC-02 -->
## The real symmetric spectral setting

The cleanest derivation begins with a real symmetric matrix, $A=A^T$. The spectral theorem then provides an orthonormal basis of real eigenvectors $v_1,\ldots,v_n$. If these vectors form the columns of the orthogonal matrix $Q$, then

$$
A=Q\Lambda Q^T,
\qquad
\Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n).
$$

Consequently, any vector $x$ has the expansion

$$
x=\sum_{i=1}^n c_i v_i,
\qquad c_i=v_i^T x.
$$

This representation is especially useful in applied mathematics: multiplication by $A$ acts separately on each spectral component, replacing $c_i v_i$ by $c_i\lambda_i v_i$.

For the main convergence argument, order the eigenvalues by magnitude and assume a strict first gap:

$$
|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.
$$

Thus $\lambda_1$ is unique in magnitude. The strict inequality is not decorative; it is the assumption that permits one eigendirection to separate from the others. All claims derived from the orthonormal expansion in the next sections remain restricted to this real symmetric setting.

To read the expansion geometrically, regard each coefficient $c_i=v_i^Tx$ as the signed amount of $x$ in the $v_i$ direction. Orthonormality makes these components independent coordinates. Applying $A$ does not mix them in this basis: it scales the component in direction $v_i$ by $\lambda_i$. This observation is the bridge between the matrix factorization and the iteration. It also shows why every assumption should remain visible. Without symmetry, the orthonormal-coordinate argument used here is not automatically available; without the strict magnitude gap, scaling does not force a single component to dominate.

<!-- section: SEC-03 -->
## The normalized power update

Choose a non-zero starting vector $x_0$. At step $k$, compute

$$
y_{k+1}=Ax_k,
\qquad
x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.
$$

The second operation is valid only when $y_{k+1}\ne0$. It gives $x_{k+1}$ unit Euclidean norm and controls numerical scale, while leaving the direction of $Ax_k$ unchanged. Repeated multiplication amplifies some spectral components relative to others; normalization prevents their common scale from obscuring this relative change.

It is useful to distinguish the normalized vectors used in computation from the unnormalized expression $A^k x_0$ used in analysis. They have the same direction whenever all required normalizations are defined, so the latter reveals why the former can converge.

When tracing a step by hand, perform the operations in their stated order. First form the full product $y_{k+1}$, then inspect its norm, and only then divide. After normalization, verify that the new vector has unit norm. This check detects arithmetic slips without changing the algorithm. It also reinforces that normalization is a rescaling operation: it cannot add a spectral component that was absent from the product, and it cannot rescue a zero product.

<!-- section: SEC-04 -->
## Why a dominant component emerges

Expand the initial vector in the symmetric eigenbasis as $x_0=\sum_i c_i v_i$. After $k$ unnormalized multiplications,

$$
A^k x_0
=\sum_{i=1}^n c_i\lambda_i^k v_i
=\lambda_1^k\left(c_1v_1+
\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^k v_i\right).
$$

Suppose $c_1=v_1^Tx_0\ne0$. Under the strict magnitude gap, every subordinate ratio satisfies $|\lambda_i/\lambda_1|<1$, so its $k$th power tends to zero. After ignoring the overall scalar $\lambda_1^k$ and normalizing, the surviving direction is therefore the one spanned by $v_1$.

Putting the conditions together gives the convergence statement precisely. If $A$ is real symmetric, $|\lambda_1|>|\lambda_2|$, the initial vector has non-zero projection onto $v_1$, and no iterate produces $Ax_k=0$, then the direction error generally decreases asymptotically at a rate governed by

$$
\left|\frac{\lambda_2}{\lambda_1}\right|^k.
$$

This is an asymptotic description, not an unconditional finite-step error bound. It also explains a useful comparison: a smaller magnitude ratio normally yields faster eventual separation, while a ratio close to one leaves subordinate components visible for many iterations.

You can use the factored expression as a proof template. Identify the dominant coefficient, divide the whole expression by the dominant power, and inspect each remaining ratio. The conclusion depends jointly on a non-zero dominant coefficient and ratios whose magnitudes are strictly below one. If either ingredient is missing, the limit argument stops. Notice also that normalization removes the growing or shrinking common factor but does not alter these relative ratios. Thus the computational update and spectral derivation describe the same directional mechanism from two complementary viewpoints.

<!-- section: SEC-05 -->
## Failure modes and scope boundaries

The derivation makes several apparent and genuine failures easy to separate.

First, if $\lambda_1<0$, successive normalized iterates may alternate sign. This is not failure of convergence in direction: $v_1$ and $-v_1$ represent the same eigendirection. A test based only on $\|x_{k+1}-x_k\|_2$ could therefore be misleading.

Second, if $v_1^Tx_0=0$, the start has no dominant component. In exact arithmetic, repeated multiplication cannot create that missing component, so the method does not converge to $v_1$. For example, with a diagonal matrix and a start orthogonal to its first coordinate direction, every iterate stays in the non-dominant invariant subspace. This is not merely slow convergence toward $v_1$.

Third, two distinct spectral situations must not be conflated. If $|\lambda_1|=|\lambda_2|$, power iteration need not select a unique eigenvector; it may remain in, or oscillate within, the invariant subspace belonging to the tied dominant magnitudes. If instead $|\lambda_2/\lambda_1|$ is below but close to one, the dominant magnitude is unique, yet convergence may be very slow.

Finally, the orthogonal decomposition above is not a general proof for arbitrary non-symmetric matrices. Power iteration can apply to some such matrices, but a clean orthogonal eigenbasis is no longer generally available. Defective matrices, complex dominant eigenvalues, and non-normal behaviour require additional care and lie outside this lesson's analysis.

For counterexample analysis, diagnose which assumption has changed before describing the observed iterate. Sign alternation retains a unique eigendirection and is only an orientation effect. An exactly missing dominant projection traps the sequence in a non-dominant invariant subspace. Tied dominant magnitudes remove unique selection, whereas a separated but nearly tied pair preserves the convergence mechanism while making it slow. These cases may look similar over a short run, but their mathematical explanations differ. Reporting the relevant projection, magnitude relation, and residual is therefore more informative than simply saying that the vectors “have not settled.”

<!-- section: SEC-06 -->
## Estimating the eigenvalue and measuring quality

Once $x_k\ne0$ approximates an eigenvector, estimate its eigenvalue using the Rayleigh quotient

$$
\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.
$$

For the unit vectors produced by power iteration, this simplifies to $\rho(x_k)=x_k^TAx_k$. In the real symmetric setting, if $x_k$ approaches $v_1$ in direction, then this estimate approaches $\lambda_1$.

An estimate alone does not say how closely the defining eigenpair equation is satisfied. Define the residual

$$
r_k=Ax_k-\rho(x_k)x_k.
$$

For an exact eigenpair the residual is zero. Computationally, $\|r_k\|_2$ is therefore a meaningful stopping measure: it directly measures the defect in the eigenvalue equation and is not confused by replacing an approximate eigenvector with its negative. A tolerance should be interpreted as a finite-precision diagnostic threshold, not as proof that the returned pair is exact.

In practice, interpret the estimate and residual together. The Rayleigh quotient supplies the scalar paired with the current direction; the residual checks how well that pair satisfies the matrix equation. Before using the unit-vector simplification, confirm that normalization has actually occurred. At termination, record the residual norm and the number of iterations as well as the estimate. This makes it possible to distinguish reaching the requested threshold from merely exhausting the allowed work. Comparing successive vectors alone is insufficient because a negative dominant eigenvalue can reverse their signs even while the eigendirection improves.

<!-- section: SEC-07 -->
## A safeguarded algorithm

Start by converting $A$ and $x_0$ to floating arrays. Require $A$ to be square, require $x_0$ to be a compatible one-dimensional vector, reject a zero start, and normalize it. Also require a positive tolerance and a positive integer iteration limit; these checks prevent ambiguous stopping behavior and an undefined final return.

For iterations numbered from one through the limit, compute $y=Ax$. Check $\|y\|_2$ before division: if it is zero, stop with a breakdown message. Otherwise normalize $x=y/\|y\|_2$, compute the unit-vector Rayleigh estimate $x^TAx$, and form the residual $Ax-(x^TAx)x$. If its norm is at most the tolerance, return the estimate, vector, residual norm, and current iteration number. If the threshold is never reached, return the same four quantities from the final allowed iteration. Thus residual stopping and the finite iteration cap serve different purposes, and both are retained.

The return values form a compact diagnostic record. The scalar and vector state the approximate eigenpair, the residual norm quantifies its equation defect, and the iteration count identifies the stopping point. A breakdown is different from an ordinary capped return and should raise an explicit error before normalization. Likewise, invalid shapes, a zero start, a non-positive tolerance, or an invalid iteration cap are input errors rather than convergence outcomes. Keeping these cases distinct prevents the implementation from presenting an unusable result as though it were a completed approximation.

<!-- section: SEC-08 -->
## Worked consolidation

Consider

$$
A=\begin{pmatrix}4&1\\1&2\end{pmatrix},
\qquad x_0=\begin{pmatrix}1\\1\end{pmatrix}.
$$

Its exact eigenvalues are $3+\sqrt{2}$ and $3-\sqrt{2}$, so the dominant value is $3+\sqrt{2}$. The following self-contained implementation applies the safeguards and reports an approximate eigenpair. The eigenvector's sign is not prescribed; a small residual is compatible with either orientation.

Before running the code, predict what should be visible. The dominant estimate should approach the larger-magnitude exact value, not the smaller one. The reported vector should have unit norm, but its sign may be the negative of another equally valid output. The residual norm should meet the default tolerance if the routine returns early; otherwise the iteration count should equal the cap. These predictions turn the example into a check of the algorithm's semantics rather than a list of unexplained numbers.

```python
import numpy as np


def power_iteration(A, x0, tolerance=1e-10, max_iterations=1000):
    A = np.asarray(A, dtype=float)
    x = np.asarray(x0, dtype=float)

    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("A must be square")
    if x.shape != (A.shape[0],):
        raise ValueError("x0 has incompatible dimensions")
    if not isinstance(tolerance, (int, float, np.integer, np.floating)) or isinstance(tolerance, (bool, np.bool_)) or tolerance <= 0:
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
estimate, vector, residual_norm, iterations = power_iteration(
    A, np.array([1.0, 1.0])
)

print("Estimated dominant eigenvalue:", estimate)
print("Exact dominant eigenvalue:", 3.0 + np.sqrt(2.0))
print("Estimated eigenvector:", vector)
print("Residual norm:", residual_norm)
print("Iterations:", iterations)
```

To consolidate the analysis, connect each output to an assumption. The symmetric matrix supplies the orthonormal spectral setting; the start has a non-zero dominant projection; the two eigenvalue magnitudes are separated; and the residual gives the stopping decision. Agreement of the estimate with $3+\sqrt{2}$ and a small reported residual are the relevant numerical checks, while the iteration count records the computational effort needed for the chosen tolerance.
