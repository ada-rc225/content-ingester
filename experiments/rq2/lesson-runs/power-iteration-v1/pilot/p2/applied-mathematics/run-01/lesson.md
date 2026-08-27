# Power Iteration: Derivation, Diagnostics, and a Reliable Implementation

Power iteration is an iterative way to approximate an eigenpair when repeated matrix–vector products are more useful than explicitly forming a characteristic polynomial. This lesson develops the method in the real symmetric setting, where the spectral theorem gives a particularly transparent derivation. We will also distinguish an approximate eigenpair from a merely plausible-looking vector, and finish with an implementation whose safeguards make its numerical behaviour inspectable.

<!-- section: SEC-01 -->
## Eigenpairs and the small-matrix viewpoint

Let $A\in\mathbb{R}^{n\times n}$. A non-zero vector $v\in\mathbb{R}^n$ is an eigenvector when there is a scalar $\lambda$ such that

$$Av=\lambda v.$$

The scalar $\lambda$ is the associated eigenvalue. The condition $v\ne0$ matters: the zero vector satisfies the equation for every scalar and therefore cannot identify an eigenvalue.

For a small matrix, eigenvalues can be found as roots of the characteristic equation

$$\det(A-\lambda I)=0,$$

where $I$ is the identity matrix of compatible size. This equation is an algebraic characterization, but explicitly forming a characteristic polynomial is usually a poor numerical strategy for a large matrix. Power iteration instead uses repeated matrix–vector products to estimate a selected eigenpair. The two viewpoints are complementary: the determinant equation helps check a small example, while iteration avoids making the characteristic polynomial the computational object.

<!-- section: SEC-02 -->
## Spectral structure and the target of the iteration

Assume now that $A=A^T$ is real and symmetric. The spectral theorem supplies an orthonormal eigenbasis, so

$$A=Q\Lambda Q^T,\qquad \Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n).$$

If $v_1,\ldots,v_n$ are the orthonormal eigenvectors, every vector $x$ can be written as

$$x=\sum_{i=1}^n c_i v_i,\qquad c_i=v_i^T x.$$

This orthogonal expansion is the foundation for the convergence explanation below. It is not a permission to use the same proof for every matrix: the real symmetric hypothesis is doing important work.

Order the eigenvalues by magnitude:

$$|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.$$

The strict first inequality gives a unique dominant magnitude. Power iteration therefore targets the eigenvalue of largest absolute value, not necessarily the most positive eigenvalue. For example, between $5$ and $-8$, the target by magnitude is $-8$ because $|-8|>|5|$. Keeping this distinction explicit prevents a common misinterpretation of the output.

<!-- section: SEC-03 -->
## The normalized update and why it converges

Choose a non-zero initial vector $x_0$. One power step is

$$y_{k+1}=Ax_k,\qquad x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.$$

The denominator must be non-zero. Normalization controls scale but does not change the direction of $y_{k+1}$.

To see the mechanism, expand $x_0=\sum_i c_i v_i$. Repeated multiplication gives

$$A^k x_0=\sum_{i=1}^n c_i\lambda_i^k v_i
=\lambda_1^k\left(c_1v_1+\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^k v_i\right).$$

The dominant projection must be present: $c_1=v_1^Tx_0\ne0$. Since $|\lambda_i/\lambda_1|<1$ for $i\ge2$, the subordinate ratios decay as $|\lambda_i/\lambda_1|^k$. After normalization, the direction is consequently governed by $v_1$, subject to the assumptions already stated.

For a real symmetric matrix, the useful convergence statement requires all of the following: a unique dominant magnitude, a non-zero initial projection onto $v_1$, and no iterate for which $Ax_k=0$. Under those conditions, direction error generally decreases asymptotically at a rate governed by

$$\left|\frac{\lambda_2}{\lambda_1}\right|^k.$$

This is a rate description, not an unconditional finite-iteration error bound. A ratio close to one can make convergence slow. If $\lambda_1<0$, normalized iterates may alternate sign; that is not a directional failure because $v_1$ and $-v_1$ represent the same eigendirection.

<!-- section: SEC-04 -->
## Failure conditions and scope boundaries

The initial vector can permanently miss the target. If $v_1^Tx_0=0$, there is no component in the dominant eigendirection. In exact arithmetic, repeated multiplication cannot create that missing component, so the method does not converge to $v_1$; this is different from ordinary slow convergence.

A second distinction concerns the spectrum. If $|\lambda_1|=|\lambda_2|$, a unique eigenvector need not be selected. Iterates may remain in, or oscillate within, the invariant subspace associated with the dominant magnitudes. If the magnitudes are separated but $|\lambda_2/\lambda_1|$ is close to one, the conclusion is instead slow convergence. These cases should not be conflated.

The clean orthogonal decomposition used above is also a scope boundary. Power iteration can apply to some non-symmetric matrices, but an orthogonal real eigenbasis is not generally available there. Defective matrices, complex dominant eigenvalues, and non-normal behaviour require additional care and are outside this lesson's convergence proof.

<!-- section: SEC-05 -->
## Eigenvalue estimates and residual-based stopping

Once a normalized approximate eigenvector $x_k$ is available, estimate its eigenvalue with the Rayleigh quotient

$$\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.$$

For a unit-norm vector, this simplifies to $\rho(x_k)=x_k^TAx_k$. In the symmetric setting, if $x_k$ approaches $v_1$, then $\rho(x_k)$ approaches $\lambda_1$. The denominator must be retained for a non-normalized vector.

A more direct quality diagnostic is the eigenpair residual

$$r_k=Ax_k-\rho(x_k)x_k.$$

An exact eigenpair has zero residual. The norm $\|r_k\|_2$ is therefore a meaningful stopping measure. Comparing only successive vectors can be misleading because a negative dominant eigenvalue may cause sign flips even while the direction improves. A practical stopping decision is to stop when $\|r_k\|_2\le\varepsilon$, while also retaining a maximum iteration count.

The complete safeguarded algorithm is: normalize non-zero $x_0$; compute $y=Ax_k$; check whether $\|y\|_2=0$ before division; normalize; compute the Rayleigh estimate; compute the residual; stop if its norm is at most $\varepsilon$; otherwise continue until $K$ iterations have been performed. Here $\varepsilon>0$ and $K$ is a positive maximum count.

It is useful to separate three questions when reading a run. First, what direction is being produced? The normalized vector is the current directional approximation, and its overall sign is not intrinsically meaningful for an eigendirection. Second, what scalar is being estimated? The Rayleigh quotient uses the current vector and the matrix, and the simplified expression is valid only after unit normalization. Third, is the pair accurate enough for the purpose at hand? The residual answers this question more directly than a visual inspection of the vector. A small residual means that the computed pair nearly satisfies the defining relation $Ax=\lambda x$; it does not by itself remove the assumptions behind the convergence explanation.

Consider the logical order of the safeguards. A zero initial vector must be rejected before it is normalized. During an iteration, a zero value of $Ax_k$ must be detected before the code divides by its norm. Only after a non-zero product has been normalized is it meaningful to compute the Rayleigh estimate and residual for the new iterate. If the residual threshold is not met, the maximum count gives a definite outcome instead of allowing an unbounded loop. These checks are numerical translations of the mathematical preconditions, not optional decoration.

For a hand trace, begin with $x_0$, compute $y_1=Ax_0$, and calculate its two-norm. Divide by that norm to obtain $x_1$. Then evaluate $\rho(x_1)$ and $r_1$. Repeating this table of four quantities—matrix product, normalized vector, estimate, and residual norm—makes it possible to tell whether progress is genuine. A changing sign with a decreasing residual can be compatible with a negative dominant eigenvalue. A nearly unchanged residual may instead indicate a small spectral gap, a missing dominant projection, or an input outside the assumptions of the symmetric derivation.

<!-- section: SEC-06 -->
## NumPy operations as executable mathematics

The implementation uses a small, explicit set of NumPy patterns. Convert compatible inputs with `np.asarray(..., dtype=float)` and inspect `A.shape` and `x.shape` before arithmetic. For a two-dimensional matrix and compatible one-dimensional vector, `A @ x` is the matrix–vector product. `np.linalg.norm(x)` gives the default Euclidean norm for a one-dimensional vector, and a scalar zero check must happen before division.

Shape and value checks should raise specific exceptions rather than allowing an obscure later failure. Array comparisons are elementwise, so a single diagnostic decision must use a scalar quantity such as a norm. Finally, a function can return several diagnostics in one tuple; the caller can unpack the eigenvalue estimate, vector, residual norm, and iteration count into four names.

The code below keeps the mathematical safeguards visible. It validates the square matrix, compatible vector shape, non-zero initial vector, positive tolerance, and positive iteration limit. It checks for a zero matrix–vector product before normalization, computes the Rayleigh estimate and residual, returns early on the residual test, and otherwise returns the final values at the iteration cap.

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
    if x_norm == 0.0:
        raise ValueError("x0 must be non-zero")
    x = x / x_norm
    eigenvalue = None
    residual_norm = None
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
eigenvalue, eigenvector, residual, iterations = power_iteration(
    A, np.array([1.0, 1.0])
)
print("Estimated dominant eigenvalue:", eigenvalue)
print("Estimated eigenvector:", eigenvector)
print("Residual norm:", residual)
print("Iterations:", iterations)
```

<!-- section: SEC-07 -->
## Worked consolidation

For

$$A=\begin{bmatrix}4&1\\1&2\end{bmatrix},\qquad x_0=\begin{bmatrix}1\\1\end{bmatrix},$$

the characteristic equation gives the exact eigenvalues $3+\sqrt{2}$ and $3-\sqrt{2}$. The first is dominant by magnitude, so the iteration should estimate $3+\sqrt{2}$, approximately $4.4142$, rather than the smaller value. The starting vector is non-zero; for this matrix it also supplies a non-zero component in the dominant eigendirection, so the spectral derivation predicts convergence.

At each pass, the code forms a matrix–vector product, normalizes it, estimates the eigenvalue with the unit-vector Rayleigh quotient, and measures the residual. The printed residual should be small when the stopping tolerance is reached. The eigenvector may appear with either overall sign; that does not change the eigendirection or the quality of the eigenpair. If the tolerance is deliberately made very strict, the iteration cap remains a transparent fallback rather than an implicit claim of exact convergence.

Several checks can be made without knowing the exact eigenvector in advance. Verify that the reported vector has approximately unit two-norm, compare the estimated eigenvalue with the two exact values, and recompute the residual from the displayed estimate and vector. The residual calculation is especially useful because it tests the defining equation directly. If the vector is negated, both sides of the eigenvector relation are negated together, while the Rayleigh estimate and residual norm retain the same interpretation. Thus a sign difference between two valid runs is not, by itself, evidence of disagreement.

The example also illustrates why a worked result should report more than one number. An eigenvalue estimate close to $3+\sqrt{2}$ identifies the intended spectral target, but the residual indicates whether the accompanying vector actually supports that estimate. The iteration count records whether the tolerance was reached early or whether the maximum count was used. Together, these outputs make the stopping decision auditable and leave room for a later comparison with a different initial vector or tolerance without changing the algorithm's meaning.

The main lesson is therefore conditional rather than magical: power iteration is a repeated normalized multiplication whose direction is explained by spectral components, whose target is selected by magnitude, and whose output must be judged by a residual. A trustworthy implementation exposes the assumptions, checks breakdown before division, rejects invalid inputs, and reports enough diagnostics to distinguish convergence, slow progress, and failure.
