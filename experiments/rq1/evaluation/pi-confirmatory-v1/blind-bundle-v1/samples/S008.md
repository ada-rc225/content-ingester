# Eigenvalues, Eigenvectors, and the Power Iteration

## 1. Why eigenpairs matter

A matrix usually changes both the length and direction of a vector. An eigenvector is a special non-zero vector whose direction is preserved by the matrix. If $A\in\mathbb{R}^{n\times n}$ and $v\ne0$, then $v$ is an eigenvector when

$$
Av=\lambda v.
$$

The scalar $\lambda$ is its eigenvalue. A positive eigenvalue preserves the direction of $v$ while scaling it; a negative eigenvalue reverses the direction as well as scaling it. The zero vector is excluded because it would satisfy this equation for every scalar and would therefore provide no useful information.

For a small matrix, eigenvalues can be found from the characteristic equation

$$
\det(A-\lambda I)=0.
$$

For large engineering models, however, explicitly forming and solving a characteristic polynomial is often an unattractive numerical strategy. An iterative method can instead use repeated matrix-vector products. This is useful when applying $A$ to a vector is feasible but computing every eigenpair is unnecessary.

A mechanical-engineering connection is helpful only as a bridge: an eigenvector can resemble a mode shape, and an eigenvalue can be related to a characteristic scaling in an idealised model. The discussion here is strictly about the algebraic matrix problem $Av=\lambda v$; it does not assume a particular mass or stiffness formulation.

## 2. The special structure of real symmetric matrices

Suppose $A=A^T$ is real and symmetric. The spectral theorem says that $A$ has an orthonormal basis of real eigenvectors. Thus there are eigenvectors $v_1,\ldots,v_n$ with $v_i^Tv_j=0$ for $i\ne j$, and

$$
A=Q\Lambda Q^T,
$$

where $Q=[v_1,\ldots,v_n]$ is orthogonal and $\Lambda$ is the diagonal matrix of eigenvalues. Consequently, every vector can be expanded as

$$
x=\sum_{i=1}^n c_i v_i,
\qquad c_i=v_i^Tx.
$$

This orthogonal expansion is the main reason symmetric matrices provide a clean setting for understanding power iteration. Order the eigenvalues by magnitude:

$$
|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.
$$

Under this ordering, $\lambda_1$ is dominant by magnitude. It is not necessarily the largest algebraic, or most positive, eigenvalue. For example, between $5$ and $-8$, the dominant eigenvalue for power iteration is $-8$, because $|-8|>5$.

## 3. Deriving the power iteration

Choose a non-zero starting vector $x_0$ and expand it in the eigenvector basis:

$$
x_0=\sum_{i=1}^n c_i v_i.
$$

Applying $A$ repeatedly gives

$$
A^k x_0=\sum_{i=1}^n c_i\lambda_i^k v_i
=\lambda_1^k\left(c_1v_1+\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^k v_i\right).
$$

If $c_1=v_1^Tx_0\ne0$, the first term is present. If also $|\lambda_i/\lambda_1|<1$ for every $i\ge2$, the other terms become relatively smaller as $k$ increases. The direction of $A^kx_0$ therefore approaches the direction of $v_1$. The overall scalar $\lambda_1^k$ can become extremely large or extremely small, so the practical algorithm normalises after every multiplication.

Starting with a normalised $x_k$, compute

$$
y_{k+1}=Ax_k,
\qquad x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.
$$

Normalisation changes only scale, not direction. If the dominant eigenvalue is negative, multiplication by $A$ can reverse the dominant component on each step. The vectors may alternate between approximately $v_1$ and $-v_1$. This is normal convergence to an eigendirection, because an eigenvector and its negative represent the same one-dimensional subspace.

For a real symmetric matrix, the useful convergence assumptions are therefore a unique dominant magnitude, a non-zero initial projection onto its eigenvector, and no zero matrix-vector product during the iteration. The asymptotic direction error is governed generally by

$$
\left|\frac{\lambda_2}{\lambda_1}\right|^k.
$$

The ratio is the asymptotic factor. A ratio near zero gives rapid improvement; a ratio close to one gives slow improvement. In mechanical terms, closely competing characteristic scales may require many updates before one direction visibly dominates, but this is only an analogy for the spectral gap.

## 4. Eigenvalue estimates and stopping criteria

Once an approximate eigenvector $x$ is available, estimate its eigenvalue with the Rayleigh quotient

$$
\rho(x)=\frac{x^TAx}{x^Tx}.
$$

If $x$ has unit norm, this becomes $\rho(x)=x^TAx$. For a symmetric matrix, the quotient approaches the eigenvalue associated with the limiting eigenvector. It is an estimate, not a replacement for checking the eigenvector equation.

The corresponding residual is

$$
r=Ax-\rho(x)x.
$$

An exact eigenpair has $r=0$. In floating-point computation, the residual norm $\|r\|_2$ gives a direct measure of how well the computed pair satisfies the defining equation. It is generally a better stopping measure than comparing consecutive vectors. In particular, $\|x_{k+1}-x_k\|_2$ can be large merely because the sign flips, even though both vectors describe nearly the same eigendirection.

A practical iteration first normalises the starting vector. At each step it forms $y=Ax$, checks whether $\|y\|_2=0$, normalises $y$, computes the Rayleigh quotient and residual, and stops if the residual norm is below a tolerance. A maximum iteration count is also needed so that an unfavourable problem does not run indefinitely.

## 5. NumPy implementation

The following implementation returns an eigenvalue estimate, a unit-norm eigenvector estimate, the residual norm, and the iteration count. Its input checks make assumptions about dimensions and the starting vector explicit.

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

For this symmetric example, the exact eigenvalues are $3+\sqrt{2}$ and $3-\sqrt{2}$. Since $3+\sqrt{2}$ has the larger magnitude, the routine should approach that eigenvalue and its eigendirection. The returned vector may have the opposite sign from a reference eigenvector without being wrong. The residual norm is the appropriate numerical evidence that the returned pair is accurate.

## 6. Failure modes and limitations

If $v_1^Tx_0=0$, the starting vector has no dominant component. In exact arithmetic, multiplying by $A$ cannot create that missing component, so the iteration remains in the subspace generated by the other eigenvectors and cannot converge to $v_1$. A different starting vector can avoid this failure.

If two eigenvalues have the same largest magnitude, there is no unique dominant direction for the method to select. The iteration can remain in, or oscillate within, the invariant subspace associated with those magnitudes. A small spectral gap is less severe but still important: when $|\lambda_2/\lambda_1|$ is close to one, many iterations may be required.

A zero value of $Ax_k$ causes a direct breakdown because the next normalisation would divide by zero. This is distinct from slow convergence. It should be reported rather than hidden.

The clean derivation above relies on symmetry. Power iteration can work for some non-symmetric matrices, but an orthogonal real eigenvector decomposition is not generally available. Defective matrices, complex dominant eigenvalues, and non-normal transient behaviour need additional analysis. Thus success on a symmetric test matrix should not be treated as a universal guarantee.

## Final chapter: Exercises and worked solutions

### Exercise 1 — concept_check

A real symmetric matrix has eigenvalues $5$ and $-8$. Which eigenvalue does power iteration target, and what does a sign change between successive vectors mean?

**Worked solution.** Power iteration targets $-8$, because it has the largest magnitude: $|-8|=8>5$. A negative dominant eigenvalue reverses the dominant component at each multiplication, so successive normalised vectors may alternate between approximately $v$ and $-v$. This is not failure: both vectors represent the same eigendirection. The method is targeting the eigenvalue of largest magnitude, not necessarily the largest algebraic eigenvalue.

### Exercise 2 — hand_calculation

Let $A=\operatorname{diag}(5,2)$ and $x_0=(1,1)^T$. Compute the first three unnormalised iterates $A^kx_0$, describe the limiting direction, and use a consistency check to verify the result.

**Worked solution.** The iterates are

$$
Ax_0=(5,2)^T,
\qquad A^2x_0=(25,4)^T,
\qquad A^3x_0=(125,8)^T.
$$

The ratio of the second component to the first is $2/5$, then $(2/5)^2$, then $(2/5)^3$. It tends to zero, so the direction approaches $(1,0)^T$, the eigenvector associated with eigenvalue $5$. The consistency check is direct substitution:

$$
A(1,0)^T=(5,0)^T=5(1,0)^T.
$$

Thus the proposed limiting direction satisfies the eigenvector equation, and the observed component ratio agrees with the predicted factor $|\lambda_2/\lambda_1|=2/5$.

### Exercise 3 — code_diagnostic

A student writes a power-iteration program that stops only when `np.linalg.norm(x_next - x) < tolerance`. It reports failure on a matrix whose dominant eigenvalue is negative, even though the vectors alternate sign. What should be changed?

**Worked solution.** The stopping test should use the Rayleigh quotient and residual. After normalising the new vector, compute `eigenvalue = x @ (A @ x)`, then compute `residual = A @ x - eigenvalue * x`, and stop when `np.linalg.norm(residual) <= tolerance`. The difference between consecutive vectors is unreliable because a sign flip makes nearly equivalent eigendirections appear far apart. The implementation should also keep a maximum iteration limit and check whether `A @ x` has zero norm before normalisation. These changes distinguish sign ambiguity from a genuine failure to satisfy the eigenpair equation.
