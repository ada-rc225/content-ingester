# Eigenvalues, Eigenvectors, and the Power Iteration

## 1. Why eigenpairs matter

A matrix can transform a vector by changing both its length and its direction. An eigenvector is a special non-zero vector whose direction is unchanged by the transformation. For a real square matrix $A$, a vector $v\ne0$ is an eigenvector when

$$Av=\lambda v.$$

The scalar $\lambda$ is its eigenvalue. If $\lambda$ is positive, the transformation preserves the vector’s direction and scales it by $\lambda$. If it is negative, the direction reverses as well as being scaled. The zero vector is excluded: $A0=\lambda0$ for every $\lambda$, so it cannot identify a meaningful direction.

Eigenvalues can be found in principle from the characteristic equation $\det(A-\lambda I)=0$. For small matrices this equation is useful for analysis. For large matrices, explicitly forming and solving a characteristic polynomial is often a poor numerical approach. An iterative method can instead use repeated matrix–vector products, which is especially useful when only one important eigenpair is required.

In mechanical engineering, an eigenvector may serve as a mode shape and an eigenvalue may be related to a stiffness, growth, or squared-frequency scale, depending on the model. That interpretation is only a bridge: the power iteration itself is a general linear-algebra method, and the eigenvalue is not automatically a physical frequency without the appropriate governing equations and units.

## 2. Symmetric matrices and the dominant eigenpair

For a real symmetric matrix, $A=A^T$, the spectral theorem gives an orthonormal basis of real eigenvectors. We can write

$$A=Q\Lambda Q^T,$$

where the columns of $Q$ are orthonormal eigenvectors and $\Lambda$ contains their eigenvalues. Consequently, every vector $x$ can be expanded as

$$x=\sum_{i=1}^n c_i v_i,\qquad c_i=v_i^Tx.$$

Order the eigenvalues by magnitude:

$$|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.$$

Under this ordering, $\lambda_1$ is the dominant eigenvalue by magnitude and $v_1$ is a corresponding dominant eigenvector. This is not necessarily the largest algebraic, or most positive, eigenvalue. For example, between $5$ and $-8$, the dominant eigenvalue is $-8$ because $|-8|> |5|$.

The distinction matters in applications. If a mechanical model needs the largest positive eigenvalue, power iteration may not answer that question when a negative eigenvalue has larger magnitude. The requested spectral quantity must be identified before selecting an algorithm.

## 3. Deriving power iteration

Start with a non-zero vector $x_0$ and repeatedly multiply by $A$. Using the eigenvector expansion of the starting vector,

$$x_0=\sum_{i=1}^n c_i v_i,$$

we obtain

$$A^kx_0=\sum_{i=1}^n c_i\lambda_i^k v_i.$$

Factor out the dominant term:

$$A^kx_0=\lambda_1^k\left(c_1v_1+\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^k v_i\right).$$

Suppose $c_1=v_1^Tx_0\ne0$ and $|\lambda_1|>|\lambda_2|$. Then every ratio $|\lambda_i/\lambda_1|^k$ tends to zero. Relative to the dominant component, the other directions disappear. Normalising the vector removes the potentially enormous factor $\lambda_1^k$ and leaves a vector approaching $v_1$ or $-v_1$.

The practical iteration is therefore

$$y_{k+1}=Ax_k,\qquad x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.$$

Normalisation is not intended to improve the eigenvector direction directly. It prevents overflow from repeated growth and underflow from repeated decay. The direction of a non-zero vector is unchanged by division by its norm.

The asymptotic direction error is governed by

$$\left|\frac{\lambda_2}{\lambda_1}\right|^k.$$

Thus the method is linearly convergent in this asymptotic sense. A ratio close to one means slow convergence; a small ratio means rapid convergence. The assumptions are important: there must be a unique dominant magnitude, the initial vector must have a non-zero dominant projection, and no step may produce $Ax_k=0$.

## 4. Eigenvalue estimates and stopping

After obtaining an approximate unit eigenvector $x$, estimate its eigenvalue with the Rayleigh quotient:

$$\rho(x)=\frac{x^TAx}{x^Tx}.$$

When $\|x\|_2=1$, this becomes $\rho(x)=x^TAx$. For a symmetric matrix, the quotient approaches the eigenvalue associated with the converged eigendirection.

The more informative quality check is the residual

$$r=Ax-\rho(x)x.$$

An exact eigenpair has $r=0$. Therefore, a small residual norm $\|r\|_2$ indicates that the computed vector and scalar nearly satisfy the defining eigenvalue equation. Checking only $\|x_{k+1}-x_k\|_2$ can be misleading. If the dominant eigenvalue is negative, successive vectors can alternate sign even while representing the same eigendirection, making their direct difference large. The residual is insensitive to this representation issue because replacing $x$ by $-x$ also replaces $r$ by $-r$, leaving its norm unchanged.

For a numerical implementation, normalise the initial vector, multiply, check for zero norm, normalise again, compute the Rayleigh quotient, and then compute the residual. Stop when the residual norm is below a chosen tolerance or when a maximum iteration count is reached. A maximum protects the program when convergence assumptions are not met.

## 5. NumPy implementation

The following implementation validates the matrix and starting vector, reports breakdown explicitly, and returns the approximate eigenvalue, unit eigenvector, residual norm, and iteration count.

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

For this symmetric matrix, the exact eigenvalues are $3+\sqrt{2}$ and $3-\sqrt{2}$. The routine should approach $3+\sqrt{2}$, the eigenvalue of larger magnitude, and should return a small residual. Comparing with `numpy.linalg.eigh` is useful as an additional diagnostic, but residual size is essential evidence that the returned pair satisfies the matrix equation.

## 6. Limitations and failure modes

If $v_1^Tx_0=0$, the starting vector has no dominant component. Exact multiplication by $A$ cannot create one, so the method remains in the subspace generated by the other eigenvectors and may converge to a different eigenpair. In floating-point arithmetic, tiny round-off components can sometimes change what is observed, but that is not a reliable remedy.

If $|\lambda_1|=|\lambda_2|$, no single direction is dominant. The iteration may retain a mixture of directions or oscillate in the associated invariant subspace. A repeated magnitude, including opposite signs, violates the unique-dominance assumption.

A small spectral gap is less dramatic but often costly: when $|\lambda_2/\lambda_1|$ is close to one, many iterations may be needed. A maximum iteration count then provides useful information rather than silently claiming convergence.

A zero product $Ax_k$ causes breakdown because the next normalisation is impossible. Finally, for a non-symmetric matrix the orthogonal eigenvector expansion used in the derivation is not generally available. Some non-symmetric problems still work, but defective matrices, complex dominant eigenvalues, and non-normal behaviour require further analysis. The symmetric theory should not be transferred automatically.

## 7. Final chapter: Exercises and worked solutions

### Exercise 1 — concept_check

A real symmetric matrix has eigenvalues $5$ and $-8$. Which eigenvalue does ordinary power iteration target, and what may happen to the signs of successive normalised vectors?

**Worked solution.** It targets $-8$, because power iteration selects the eigenvalue with largest magnitude and $|-8|=8>5$. Since the dominant eigenvalue is negative, multiplication reverses the dominant direction at each step. The normalised iterates may therefore alternate between vectors close to $v$ and $-v$. This is convergence of the eigendirection, not failure. The Rayleigh quotient approaches $-8$, not $5$.

### Exercise 2 — hand_calculation

Let $A=\operatorname{diag}(5,2)$ and $x_0=(1,1)^T$. Compute the first three unnormalised iterates $A^kx_0$, identify the limiting direction, and perform a consistency check using the eigenvalue equation for that direction.

**Worked solution.** The iterates are

$$A^0x_0=(1,1)^T,$$
$$Ax_0=(5,2)^T,$$
$$A^2x_0=(25,4)^T,$$
$$A^3x_0=(125,8)^T.$$

The first component grows by a factor of $5$ per multiplication, while the second grows by a factor of $2$. Their ratio is $2^k/5^k=(2/5)^k$, which tends to zero. After normalisation, the direction therefore approaches $(1,0)^T$ (up to sign). Consistency check: $A(1,0)^T=(5,0)^T=5(1,0)^T$, so the limiting direction is an eigenvector and its eigenvalue is $5$. The starting vector has a non-zero first component, so the dominant projection assumption is satisfied.

### Exercise 3 — code_diagnostic

A student changes the implementation to stop when `np.linalg.norm(x_new - x_old) < tolerance`. On a matrix whose dominant eigenvalue is negative, the code reaches the maximum iteration count even though the residual is small. Diagnose the issue and state the correction.

**Worked solution.** The direct difference treats $x$ and $-x$ as different vectors, although they represent the same eigendirection. A negative dominant eigenvalue can make successive normalised iterates alternate signs, so `x_new - x_old` need not become small. The correction is to compute `eigenvalue = x @ (A @ x)`, then `residual = A @ x - eigenvalue * x`, and stop when `np.linalg.norm(residual) <= tolerance`. The residual norm is unchanged by a global sign change and directly tests the eigenpair equation. A maximum iteration limit should still be retained for cases such as a missing dominant projection, equal dominant magnitudes, or a very small spectral gap.
