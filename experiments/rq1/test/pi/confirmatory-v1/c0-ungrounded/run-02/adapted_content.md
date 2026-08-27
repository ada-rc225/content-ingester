# Eigenvalues, Eigenvectors, and the Power Iteration

## 1. Why these ideas matter

Many engineering calculations ask whether a system has a preferred direction of response. For example, a simplified mechanical model may represent a stiffness, mass, or stress-related operation by a matrix. Applying that matrix to a vector changes both its magnitude and, usually, its direction. An eigenvector is a special direction that does not turn under the matrix: the matrix only stretches it or reverses it. The associated stretching factor is an eigenvalue.

This idea gives a useful bridge to mechanics, but the central subject is linear algebra. A mechanical system is not required in order to define or compute an eigenpair. We will work with real matrices, especially real symmetric matrices, because they have particularly clear geometry and reliable numerical behaviour.

The power iteration is a simple iterative eigensolver. Starting from a vector, it repeatedly applies a matrix and rescales the result. Under appropriate assumptions, the vector approaches an eigenvector associated with the eigenvalue of largest absolute value. This last phrase is important: power iteration does not automatically find the largest eigenvalue in the ordinary algebraic ordering.

## 2. Eigenvalues and eigenvectors

Let $A$ be an $n\times n$ matrix. A nonzero vector $v$ is an eigenvector of $A$ if there is a scalar $\lambda$ such that

$$Av=\lambda v.$$

The scalar $\lambda$ is the corresponding eigenvalue. The vector must be nonzero because the zero vector satisfies the equation for every scalar and therefore carries no useful directional information.

The equation can be rearranged as

$$ (A-\lambda I)v=0, $$

where $I$ is the identity matrix. A nonzero solution exists only when $A-\lambda I$ is singular, so eigenvalues satisfy the characteristic equation

$$\det(A-\lambda I)=0.$$

For a small matrix, this determinant can be expanded directly. For realistic engineering matrices, directly forming a characteristic polynomial is generally not the preferred numerical method. Iterative methods such as power iteration can obtain selected eigenpairs without computing every eigenvalue.

Eigenvectors are not unique in scale. If $v$ is an eigenvector, then $cv$ is also an eigenvector for every nonzero scalar $c$. In particular, $v$ and $-v$ represent the same eigendirection. This sign ambiguity is normal and should not be interpreted as a disagreement between two correct computations.

## 3. Symmetric matrices and the dominant eigenpair

A real matrix is symmetric when $A=A^T$. Real symmetric matrices have real eigenvalues and an orthonormal basis of eigenvectors. Thus, for such a matrix, we can write

$$A=Q\Lambda Q^T,$$

where the columns of $Q$ are mutually perpendicular unit eigenvectors and $\Lambda$ contains the eigenvalues on its diagonal.

Suppose the eigenvalues are ordered by magnitude so that

$$|\lambda_1|>|\lambda_2|\geq\cdots\geq|\lambda_n|.$$

The dominant eigenvalue for power iteration is $\lambda_1$, meaning the eigenvalue with largest absolute value. Its eigenvector is the dominant eigenvector. If instead we order eigenvalues algebraically, the largest one is the most positive value. These are different notions when negative eigenvalues are present. For example, $-10$ is smaller algebraically than $3$, but has larger magnitude; power iteration is attracted to the eigenvalue $-10$ rather than $3$.

The mechanics analogy is bounded and useful: a dominant eigendirection can describe a mode that is amplified most strongly by one application of a linear model. However, whether a particular stiffness or dynamic model has that interpretation depends on how the matrix was constructed. The mathematical algorithm only sees repeated matrix-vector products.

## 4. Deriving power iteration

Take an initial nonzero vector $x_0$ and express it in the eigenvector basis:

$$x_0=c_1v_1+c_2v_2+\cdots+c_nv_n.$$

After applying $A$ repeatedly,

$$A^kx_0=c_1\lambda_1^kv_1+c_2\lambda_2^kv_2+\cdots+c_n\lambda_n^kv_n.$$

Factor out $\lambda_1^k$:

$$A^kx_0=\lambda_1^k\left(c_1v_1+c_2\left(\frac{\lambda_2}{\lambda_1}\right)^kv_2+\cdots+c_n\left(\frac{\lambda_n}{\lambda_1}\right)^kv_n\right).$$

If $|\lambda_j/\lambda_1|<1$ for every $j>1$, the terms involving the other eigenvectors shrink relative to the first term. Provided $c_1\neq0$, the direction of $A^kx_0$ approaches the direction of $v_1$.

In practice, the vector magnitude can become extremely large or extremely small. We therefore normalize after each multiplication. With the Euclidean norm, one iteration is

$$y_k=Ax_k,\qquad x_{k+1}=\frac{y_k}{\|y_k\|_2}.$$

The sign of $x_{k+1}$ may alternate when the dominant eigenvalue is negative. This is not failure: the direction, considered up to sign, can still converge. A normalized vector does not itself provide the eigenvalue, so we estimate it with the Rayleigh quotient.

## 5. Rayleigh quotient and residual

For a nonzero vector $x$, the Rayleigh quotient is

$$\rho(x)=\frac{x^TAx}{x^Tx}.$$

When $x$ is an exact eigenvector, $\rho(x)$ equals its eigenvalue. For a unit vector, this simplifies to $x^TAx$. During power iteration, the Rayleigh quotient provides an eigenvalue estimate that is often more accurate than simply using the norm of $Ax$.

A second, essential diagnostic is the residual

$$r=Ax-\rho(x)x.$$

Its norm measures how far the computed pair $(\rho(x),x)$ is from satisfying the eigenvalue equation. A small residual means the equation is nearly satisfied, whereas a stable-looking vector alone is not sufficient evidence. In code, it is useful to monitor both the change in the vector and the residual. Because of sign ambiguity, compare $x_{k+1}$ with both $x_k$ and $-x_k$ when measuring directional change.

For a symmetric matrix, the Rayleigh quotient lies between the smallest and largest algebraic eigenvalues. It does not necessarily approach the largest algebraic eigenvalue under power iteration; it approaches the eigenvalue associated with the dominant magnitude, assuming convergence conditions hold.

## 6. Convergence assumptions and rate

The basic convergence assumptions are these:

1. The target eigenvalue is unique in magnitude: $|\lambda_1|>|\lambda_2|$.
2. The initial vector has a nonzero component in the dominant eigenvector direction: $c_1\neq0$.
3. The matrix-vector products and normalization can be computed without numerical breakdown.

The asymptotic direction error is governed by the ratio

$$\left|\frac{\lambda_2}{\lambda_1}\right|.$$

A smaller ratio means faster convergence. Equivalently, a large spectral gap in magnitude gives rapid progress. If the ratio is close to one, the spectral gap is small and many iterations may be needed, even though the method is theoretically convergent.

If the starting vector has no dominant projection, power iteration cannot discover that component through exact arithmetic: applying $A$ preserves the subspace spanned by the other eigenvectors. In floating-point arithmetic, roundoff may introduce a tiny component, but relying on this is poor practice. A new starting vector is the appropriate remedy.

If two eigenvalues have the same largest magnitude, the strict dominance assumption fails. For example, eigenvalues $5$ and $-5$ can produce alternating or nonconvergent directions. A repeated dominant eigenvalue may also leave the result dependent on the initial vector. Power iteration then does not generally select one unique eigenvector.

## 7. A NumPy implementation

The following implementation normalizes each iterate, estimates the eigenvalue with the Rayleigh quotient, and stops when the residual is small. The returned vector may have either sign compared with another correct result.

```python
import numpy as np


def power_iteration(A, x0=None, max_iter=1000, tol=1e-10):
    A = np.asarray(A, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("A must be a square matrix")

    n = A.shape[0]
    if x0 is None:
        x = np.ones(n, dtype=float)
    else:
        x = np.asarray(x0, dtype=float).reshape(n)

    norm_x = np.linalg.norm(x)
    if norm_x == 0:
        raise ValueError("x0 must be nonzero")
    x = x / norm_x

    for iteration in range(1, max_iter + 1):
        y = A @ x
        norm_y = np.linalg.norm(y)
        if norm_y == 0:
            raise ValueError("iteration produced the zero vector")
        x = y / norm_y
        eigenvalue = float(x @ A @ x)
        residual = np.linalg.norm(A @ x - eigenvalue * x)
        if residual <= tol:
            return eigenvalue, x, iteration, residual

    return eigenvalue, x, max_iter, residual


A = np.array([[4.0, 1.0], [1.0, 3.0]])
lam, vec, iterations, residual = power_iteration(A)
print(lam)
print(vec)
print(iterations, residual)
```

The zero-vector check matters because normalization by zero is undefined. In production work, the tolerance should reflect the scale of the matrix and the desired accuracy. A relative residual, such as $\|r\|_2/(\|A\|_2\|x\|_2)$, is often more informative when matrix magnitudes vary substantially.

## 8. Important failure modes and non-symmetric limitations

A negative dominant eigenvalue causes sign alternation: successive iterates may approximately satisfy $x_{k+1}\approx -x_k$. The Rayleigh quotient can still settle near the negative eigenvalue, and the residual can become small. Do not stop merely because consecutive vectors differ in sign.

A zero dominant projection, equal dominant magnitudes, and a small spectral gap are structural issues rather than coding bugs. Diagnose them by considering the spectrum, trying a different initial vector, and examining residuals and iteration counts. A residual that remains large indicates that the returned vector is not yet a reliable eigenvector approximation.

For non-symmetric matrices, eigenvalues can be complex, eigenvectors may not be orthogonal, and the clean orthonormal expansion used above may not apply. Power iteration can still work in some cases, especially when there is a unique dominant eigenvalue and suitable diagonalizability, but convergence can be less predictable. A real implementation restricted to real vectors may not represent a complex dominant eigenpair at all. The symmetric assumptions should therefore be stated explicitly rather than silently extended to every matrix.

## 9. Exercises and worked solutions

### Exercise 1: concept_check

A matrix has eigenvalues $-8$, $5$, and $2$. Which eigenvalue does basic power iteration target under the usual assumptions, and is it the largest algebraic eigenvalue?

**Worked solution.** The target is $-8$, because its magnitude, $8$, is larger than $5$ and $2$. It is not the largest algebraic eigenvalue; algebraically, $5$ is largest. This distinction follows from the factor $|\lambda_j/\lambda_1|$ in the convergence argument.

### Exercise 2: hand_calculation

Let

$$A=\begin{bmatrix}3&1\\1&3\end{bmatrix},\qquad x_0=\begin{bmatrix}1\\0\end{bmatrix}.$$

Perform one normalized power iteration, then compute the Rayleigh quotient and residual for the new vector. Include a consistency check.

**Worked solution.** First,

$$y_0=Ax_0=\begin{bmatrix}3\\1\end{bmatrix},\qquad \|y_0\|_2=\sqrt{10}.$$

Therefore,

$$x_1=\frac{1}{\sqrt{10}}\begin{bmatrix}3\\1\end{bmatrix}.$$

The Rayleigh quotient is

$$\rho(x_1)=x_1^TAx_1=\frac{1}{10}[3\;1]\begin{bmatrix}10\\6\end{bmatrix}=3.6.$$

The residual is

$$r=Ax_1-3.6x_1=\frac{1}{\sqrt{10}}\begin{bmatrix}10\\6\end{bmatrix}-\frac{3.6}{\sqrt{10}}\begin{bmatrix}3\\1\end{bmatrix}=\frac{1}{\sqrt{10}}\begin{bmatrix}-0.8\\2.4\end{bmatrix}.$$

Its norm is $\|r\|_2=\sqrt{6.4/10}=0.8$. As a consistency check, $x_1$ has unit norm because $(3^2+1^2)/10=1$, and the exact eigenvalues are $4$ and $2$, so the quotient $3.6$ lies between them as expected for a real symmetric matrix.

### Exercise 3: code_diagnostic

A power-iteration program reports vectors that alternate sign, while the Rayleigh quotient approaches $-6$ and the residual decreases toward zero. Is this necessarily a failure? What code-level diagnostic should be used?

**Worked solution.** It is not necessarily a failure. The behaviour is expected when the dominant eigenvalue is negative. The vector direction is converging up to sign. The primary diagnostic should be the residual norm, such as `np.linalg.norm(A @ x - rho * x)`, together with the Rayleigh quotient. A raw test based only on `np.linalg.norm(x_new - x_old)` can falsely reject convergence because $x_new$ may be close to `-x_old`. A sign-insensitive directional test can compare `min(norm(x_new - x_old), norm(x_new + x_old))`.
