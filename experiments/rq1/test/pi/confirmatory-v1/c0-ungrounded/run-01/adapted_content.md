# Eigenvalues, Eigenvectors, and the Power Iteration

## 1. Why eigenpairs matter

Many engineering calculations ask whether a system has a preferred direction of response. A matrix may transform a vector by stretching it, shrinking it, and rotating it. An eigenvector is a special direction that the transformation does not rotate away from itself. Its associated eigenvalue tells us the signed scale factor in that direction. These ideas are useful in vibration, stability, repeated loading, data reduction, and numerical simulation.

For a square matrix $A$, a nonzero vector $v$ is an eigenvector if

$$Av=\lambda v,$$

for some scalar $\lambda$. The scalar is the eigenvalue associated with $v$. The vector must be nonzero because the zero vector satisfies the equation for every possible scalar and therefore gives no information.

The equation says that applying $A$ to $v$ produces a vector parallel to $v$. If $\lambda=3$, the vector keeps its direction and becomes three times as long. If $\lambda=-3$, it becomes three times as long but reverses direction. If $0<|\lambda|<1$, repeated application reduces its magnitude. If $|\lambda|>1$, repeated application increases its magnitude.

In a mechanical-engineering bridge, imagine a linear map that relates a displacement pattern to a force-like or response-like pattern. An eigenvector can represent a pattern that is preserved by that map, while the eigenvalue measures the scale of the response. This bridge is only an interpretation aid: an arbitrary matrix need not be a stiffness, mass, stress, or dynamic matrix, and the eigenvalue is not automatically a physical frequency or load factor. The mathematical definitions always come first.

## 2. Finding eigenvalues and eigenvectors

Rearranging the eigenvalue equation gives

$$(A-\lambda I)v=0,$$

where $I$ is the identity matrix. A nonzero solution exists only when $A-\lambda I$ is singular. Therefore the eigenvalues are roots of the characteristic equation

$$\det(A-\lambda I)=0.$$

For a $2\times2$ matrix, this determinant can be expanded directly. For larger matrices, forming a characteristic polynomial is usually not the preferred numerical method because polynomial coefficients can be sensitive to rounding. Practical software uses algorithms designed for eigenvalue computation, and power iteration is one of the simplest methods when only one eigenpair is needed.

Consider the symmetric matrix

$$A=\begin{bmatrix}4&1\\1&4\end{bmatrix}.$$

Its characteristic equation is $(4-\lambda)^2-1=0$, so the eigenvalues are $5$ and $3$. For $\lambda=5$, an eigenvector is proportional to $(1,1)^T$. For $\lambda=3$, an eigenvector is proportional to $(1,-1)^T$. These two directions are perpendicular, as is generally true for eigenvectors belonging to distinct eigenvalues of a real symmetric matrix.

An eigenvector is not unique as a signed or scaled object. If $v$ is an eigenvector, then every nonzero multiple $cv$ is also an eigenvector because $A(cv)=cAv=c\lambda v=\lambda(cv)$. In numerical work, vectors are commonly normalized to have Euclidean norm one. Even then, both $v$ and $-v$ are valid. This sign ambiguity is not an error and should not be interpreted as a change in the underlying eigendirection.

## 3. The dominant eigenpair of a real symmetric matrix

The eigenvalue with the largest absolute value is called a dominant eigenvalue, when it is uniquely dominant. Thus, dominance means

$$|\lambda_1|>|\lambda_2|\geq |\lambda_3|\geq\cdots,$$

after ordering the eigenvalues by magnitude. The corresponding eigenvector is the dominant eigenvector. This is different from the largest algebraic eigenvalue, which is the numerically greatest value on the number line. For example, between $-10$ and $4$, the largest algebraic eigenvalue is $4$, but the dominant-by-magnitude eigenvalue is $-10$.

For a real symmetric matrix, the spectral theorem gives an orthonormal eigenbasis. We can write

$$A=Q\Lambda Q^T,$$

where the columns of $Q$ are orthonormal eigenvectors and $\Lambda$ is diagonal with eigenvalues on its diagonal. Any starting vector $x_0$ can therefore be expressed as

$$x_0=c_1v_1+c_2v_2+\cdots+c_nv_n.$$

Applying $A$ repeatedly gives

$$A^kx_0=c_1\lambda_1^kv_1+c_2\lambda_2^kv_2+\cdots+c_n\lambda_n^kv_n.$$

If $c_1\neq0$ and $|\lambda_1|$ is strictly greater than all the other eigenvalue magnitudes, the first term eventually dominates. After normalization, the direction approaches $v_1$ or alternates between its two signs. This is the central reason that power iteration works.

A mechanical-engineering interpretation can be useful for a symmetric operator associated with a suitable energy model. Orthogonal eigenvectors may describe independent patterns, and a dominant magnitude may identify the pattern most strongly amplified by repeated application. However, the interpretation depends on how the matrix was constructed. Symmetry alone guarantees useful mathematical properties, not a particular engineering meaning.

## 4. Deriving power iteration

Suppose we want the dominant eigenvector but do not want to compute every eigenpair. Start with a nonzero vector $x_0$. At each step, multiply by $A$ and normalize:

$$y_{k+1}=Ax_k,$$

$$x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.$$

The vector $x_{k+1}$ is the next direction estimate. Once the direction is approximately stable, estimate its eigenvalue with the Rayleigh quotient

$$\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.$$

When $x_k$ is normalized, this simplifies to $x_k^TAx_k$. The quotient is exactly the eigenvalue if $x_k$ is an eigenvector. Otherwise, it is a useful scalar estimate, especially for symmetric matrices.

The residual measures how well the estimated pair satisfies the defining equation:

$$r_k=Ax_k-\rho(x_k)x_k.$$

A small residual norm means that the computed vector and scalar nearly satisfy the eigenvalue equation. A small change between successive vectors can also indicate apparent convergence, but the residual is more directly tied to the problem being solved. In a robust computation, both should be considered, along with a maximum iteration limit.

To understand the rate, assume $|\lambda_1|>|\lambda_2|$ and $c_1\neq0$. Relative to the dominant term, the next-largest contribution is multiplied approximately by

$$\left|\frac{\lambda_2}{\lambda_1}\right|^k.$$

Thus the asymptotic direction error decreases geometrically at a ratio controlled by $|\lambda_2/\lambda_1|$. The spectral gap in magnitude is important. A ratio close to one means a small relative gap and slow convergence; a much smaller ratio means rapid convergence. Normalization prevents overflow or underflow, but it does not change this fundamental rate.

## 5. A NumPy implementation

The following implementation returns the normalized vector, the Rayleigh quotient, the residual norm, and a convergence flag. It uses a deterministic initial vector by default, but the initial vector can be supplied explicitly.

```python
import numpy as np


def power_iteration(A, x0=None, tol=1e-10, max_iter=1000):
    A = np.asarray(A, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("A must be a square matrix")

    n = A.shape[0]
    if x0 is None:
        x = np.ones(n, dtype=float)
    else:
        x = np.asarray(x0, dtype=float).copy()
        if x.shape != (n,):
            raise ValueError("x0 must have one entry per matrix row")

    norm_x = np.linalg.norm(x)
    if norm_x == 0:
        raise ValueError("x0 must be nonzero")
    x /= norm_x

    for iteration in range(1, max_iter + 1):
        y = A @ x
        norm_y = np.linalg.norm(y)
        if norm_y == 0:
            raise ValueError("iteration broke down: A @ x became zero")

        x_next = y / norm_y
        eigenvalue = float(x_next @ A @ x_next / (x_next @ x_next))
        residual = A @ x_next - eigenvalue * x_next
        residual_norm = np.linalg.norm(residual)

        # x and x_next may differ only by sign near convergence.
        direction_change = min(
            np.linalg.norm(x_next - x), np.linalg.norm(x_next + x)
        )
        x = x_next
        if residual_norm <= tol and direction_change <= np.sqrt(tol):
            return x, eigenvalue, residual_norm, iteration, True

    return x, eigenvalue, residual_norm, max_iter, False


A = np.array([[4.0, 1.0], [1.0, 4.0]])
x, lam, residual, steps, converged = power_iteration(A)
print(x)
print(lam, residual, steps, converged)
```

The sign-aware direction change is important. For a dominant negative eigenvalue, the unnormalized vector may reverse sign at every step. Comparing $x_{k+1}$ only with $x_k$ would incorrectly report a large change even when the eigendirection has converged. The residual does not have this problem because replacing $x$ by $-x$ also changes the sign of the residual, not its norm.

For production code, it is often useful to record a history of estimates rather than return only the final result. A history can reveal whether the residual is decreasing, whether the iteration is stagnating, or whether the requested tolerance is unrealistic for the available floating-point precision. It is also good practice to compare a result against `numpy.linalg.eigh` during testing for symmetric matrices, while remembering that the direct routine is the reference check, not part of the power iteration itself.

## 6. Assumptions, failure modes, and diagnostics

Power iteration has specific assumptions. First, the matrix must have a uniquely dominant eigenvalue in magnitude for the usual convergence statement. If two eigenvalues have equal dominant magnitude, such as $\lambda_1=5$ and $\lambda_2=-5$, their contributions do not become relatively smaller. The iteration may oscillate or fail to settle on one direction.

Second, the starting vector must have a nonzero component in the dominant eigendirection. If $x_0$ is exactly orthogonal to $v_1$ for a symmetric matrix, then $c_1=0$, and the iteration remains in the subspace spanned by the other eigenvectors. It may converge to the largest-magnitude eigenvector within that subspace, giving a perfectly small residual for the wrong eigenpair. In exact arithmetic this can persist indefinitely. In floating-point arithmetic, tiny accidental components may eventually appear, but relying on that is poor practice.

Third, the multiplication must not produce zero. If $Ax_k=0$, normalization is impossible. This can happen when the current vector lies in the nullspace, particularly if the matrix is singular. The implementation should detect this breakdown rather than divide by zero.

A small spectral gap causes slow convergence. For eigenvalues $10$ and $9.9$, the ratio is $0.99$, so many iterations may be required. Increasing `max_iter` does not remove the slow rate; it only allows more of the same geometric progress. Possible alternatives include shifted or deflated methods, inverse iteration, Arnoldi methods, or a direct symmetric eigensolver, depending on the desired eigenpair and computational setting.

A residual should be interpreted with scale in mind. A useful relative residual is

$$\frac{\|Ax-\rho x\|_2}{\|A\|_2\|x\|_2},$$

when $\|A\|_2$ is available or can be estimated. An absolute tolerance that works for a matrix with entries near one may be unsuitable for a matrix with entries near $10^8$ or $10^{-8}$. The residual is a diagnostic, not merely a stopping number.

## 7. Symmetric and non-symmetric matrices

For real symmetric matrices, eigenvalues are real, eigenvectors can be chosen orthonormal, and the expansion used in the convergence explanation is especially clean. The Rayleigh quotient is real, and the dominant-eigenvector interpretation is reliable under the stated assumptions.

For a non-symmetric matrix, eigenvalues may be complex, eigenvectors may not be orthogonal, and the matrix may even be defective so that it does not have a complete eigenvector basis. Power iteration can still work in some non-symmetric cases, especially when there is a simple dominant eigenvalue and suitable spectral structure, but the symmetric derivation should not be transferred without qualification. A real non-symmetric matrix may produce real iterates whose directions rotate because the relevant dominant eigenvalues are complex. In that situation, basic real power iteration is not a general solution.

The Rayleigh quotient also changes character. For a real non-symmetric matrix and real vector, $x^TAx/(x^Tx)$ is real, but it is not generally the same kind of sharply informative eigenvalue estimator as in the symmetric case. The residual remains meaningful, because it still tests $Ax\approx\lambda x$, but choosing and interpreting the scalar estimate may require a different method.

Finally, never confuse “dominant” with “largest algebraic.” Power iteration follows magnitude because repeated powers amplify $|\lambda|$. If the target is the largest algebraic eigenvalue of a symmetric matrix and a negative eigenvalue has larger magnitude, ordinary power iteration returns the negative one instead. A shift, transformation, or a solver designed for the requested ordering is needed when the algebraic target is the actual objective.

## 8. A practical workflow

Begin by checking that the matrix represents the problem you intend to solve and, when appropriate, checking symmetry with `np.allclose(A, A.T)`. Select a nonzero starting vector and normalize it. Run the matrix-vector iteration with a breakdown check and a maximum iteration count. Compute the Rayleigh quotient and residual after each update. Inspect convergence using a sign-invariant direction comparison and a scale-aware residual. Then compare against a trusted eigensolver on small test cases.

Test cases should include a matrix with a clear positive dominant eigenvalue, one with a negative dominant eigenvalue, a matrix with a small spectral gap, a starting vector missing the dominant projection, and a matrix with repeated dominant magnitude. These cases test both ordinary success and the boundaries of the assumptions. In engineering software, documenting those boundaries is as important as documenting the successful example.

The main conceptual chain is therefore: eigenvectors are invariant directions; eigenvalues are their scale factors; spectral decomposition explains repeated multiplication; normalization makes repeated multiplication numerically manageable; the Rayleigh quotient estimates the scalar; and the residual tests the final pair. Power iteration is simple because it exploits this chain, but its simplicity does not eliminate the need to inspect assumptions.

## 9. Exercises and worked solutions

### Exercise 1 — concept_check

A real symmetric matrix has eigenvalues $-12$, $5$, and $2$. Which eigenvalue is selected by ordinary power iteration under a generic starting vector, and is it the largest algebraic eigenvalue? Explain briefly.

**Worked solution.** Ordinary power iteration selects the eigenvalue with the largest magnitude, so it selects $-12$ because $|-12|=12$ is greater than $5$ and $2$. It is not the largest algebraic eigenvalue: the largest number on the number line is $5$. The distinction matters because repeated multiplication amplifies magnitude, including the magnitude of a negative eigenvalue. The iterates may alternate sign while their direction approaches the eigenvector associated with $-12$.

### Exercise 2 — hand_calculation

Apply two normalized power-iteration steps to

$$A=\begin{bmatrix}4&1\\1&4\end{bmatrix},\qquad x_0=\begin{bmatrix}1\\0\end{bmatrix}.$$

Then compute the Rayleigh quotient and residual norm after the second step. Include a consistency check using the known eigenvalues.

**Worked solution.** The initial vector already has unit norm. The first multiplication gives $y_1=(4,1)^T$, whose norm is $\sqrt{17}$. Therefore

$$x_1=\frac{1}{\sqrt{17}}\begin{bmatrix}4\\1\end{bmatrix}.$$

The next multiplication is

$$y_2=Ax_1=\frac{1}{\sqrt{17}}\begin{bmatrix}17\\8\end{bmatrix}.$$

Its norm is $\sqrt{17^2+8^2}/\sqrt{17}=\sqrt{353/17}$, so the normalized second iterate is

$$x_2=\frac{1}{\sqrt{353}}\begin{bmatrix}17\\8\end{bmatrix}.$$

The Rayleigh quotient is

$$\rho(x_2)=\frac{x_2^TAx_2}{x_2^Tx_2}=\frac{2(17)(8)+4(17^2+8^2)}{17^2+8^2}=\frac{816+1412}{353}=\frac{2228}{353}\approx6.312.$$

The residual is $r_2=Ax_2-\rho(x_2)x_2$. Numerically, $Ax_2=(76,49)^T/\sqrt{353}$, so

$$\|r_2\|_2\approx0.953.$$

The residual is not yet tiny, which is reasonable after only two steps. The consistency check is that the known dominant eigenvalue is $5$, with eigenvector proportional to $(1,1)^T$. The quotient estimate is moving toward $5$ from above, and the vector ratio $17/8=2.125$ is moving toward the dominant-vector ratio $1$. Also, the quotient must lie between the smallest and largest eigenvalues of a symmetric matrix, namely between $3$ and $5$ only if the matrix is evaluated correctly; here the calculation exposes an arithmetic error because $A(17,8)^T=(76,49)^T$, while $x^TAx=17(76)+8(49)=1680$, not $2228$. Thus

$$\rho(x_2)=\frac{1680}{353}\approx4.759,$$

which is correctly between $3$ and $5$. Using this corrected value gives $\|r_2\|_2\approx0.344$. This correction is the required consistency check: the spectral bound catches the mistaken numerator.

### Exercise 3 — code_diagnostic

A student writes the following code and reports that it never converges for a matrix whose dominant eigenvalue is negative:

```python
x = np.array([1.0, 1.0])
for _ in range(100):
    x_new = A @ x
    x_new = x_new / np.linalg.norm(x_new)
    if np.linalg.norm(x_new - x) < 1e-8:
        print("converged")
        break
    x = x_new
```

Identify the diagnostic problem and give a corrected stopping comparison. What additional quantity should be checked?

**Worked solution.** A negative dominant eigenvalue reverses the sign of the vector at each multiplication. Thus $x_{k+1}$ can be close to $-x_k$ even when both represent the same converged eigendirection. The test `norm(x_new - x)` treats this harmless sign reversal as a large change. A sign-invariant comparison is

```python
direction_change = min(np.linalg.norm(x_new - x),
                       np.linalg.norm(x_new + x))
if direction_change < 1e-8:
    print("converged")
```

The code should also compute the Rayleigh quotient and residual, for example:

```python
lam = x_new @ A @ x_new / (x_new @ x_new)
residual = np.linalg.norm(A @ x_new - lam * x_new)
```

The residual confirms that the vector and scalar form an approximate eigenpair. A maximum iteration limit and a zero-norm check for `A @ x` should also remain in the implementation. A sign-aware direction test alone can stop at a stable direction without guaranteeing that the eigenvalue equation is accurate, whereas the residual directly checks that equation.
