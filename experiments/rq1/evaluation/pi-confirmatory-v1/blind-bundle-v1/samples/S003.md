# Eigenvalues, Eigenvectors, and the Power Iteration

## 1. Why these ideas matter

Many matrix calculations describe how a system changes a vector. If a matrix represents a linearized mechanical model, a transformation of coordinates, or a stiffness-related calculation, most input directions are changed in both length and direction. There are, however, special directions that keep their direction under the transformation. These directions and their associated scale factors are eigenvectors and eigenvalues.

For a mechanical-engineering bridge, imagine applying a matrix to a displacement pattern. An eigenvector can be viewed as a deformation pattern that is reproduced up to a scale factor; the eigenvalue is that scale factor in the mathematical model. This picture is useful for intuition, but it is not a substitute for checking the matrix, units, boundary conditions, or physical interpretation of a particular engineering problem.

The power iteration is a simple iterative eigensolver. It is especially useful when only one eigenpair is needed and the matrix is large enough that computing every eigenvalue is unnecessary. Its simplicity also exposes important numerical ideas: normalization, convergence, residuals, spectral gaps, and failure modes.

## 2. Eigenvalues and eigenvectors

Let $A$ be an $n \times n$ matrix. A nonzero vector $v$ is an eigenvector of $A$ if there is a scalar $\lambda$ such that

$$Av = \lambda v.$$

The scalar $\lambda$ is the corresponding eigenvalue. The vector must be nonzero because the zero vector satisfies this equation for every scalar and therefore provides no useful direction. Rearranging gives $(A-\lambda I)v=0$. A nonzero solution exists only when

$$\det(A-\lambda I)=0,$$

which is the characteristic equation. For a small matrix, this equation can sometimes be solved directly. For larger matrices, direct eigenvalue algorithms or iterative methods are usually more practical.

An eigenvector is not unique as a vector with a particular scale. If $v$ is an eigenvector, then $cv$ is also an eigenvector for every nonzero scalar $c$. In particular, both $v$ and $-v$ represent the same one-dimensional eigendirection. This sign ambiguity is normal, not an error. Numerical methods may return opposite signs on different runs or for slightly different starting vectors.

For a real symmetric matrix, all eigenvalues are real, and there is an orthonormal basis of eigenvectors. Thus, for symmetric $A$, we can write

$$A = Q\Lambda Q^T,$$

where the columns of $Q$ are orthonormal eigenvectors and $\Lambda$ contains the eigenvalues. If the eigenvalues are ordered by magnitude, the dominant eigenvalue is one with largest absolute value, $|\lambda_1| \geq |\lambda_2| \geq \cdots$. Its eigenvector is a dominant eigenvector. This is different from the largest algebraic eigenvalue, which means the greatest value on the ordinary number line.

For example, the eigenvalues $-5$ and $3$ have dominant magnitude $-5$, because $|-5|> |3|$, but their largest algebraic eigenvalue is $3$. Power iteration naturally targets largest magnitude, not necessarily largest algebraic value. If the matrix is symmetric positive definite, all eigenvalues are positive, so these two meanings coincide.

## 3. The power iteration derivation

Start with a nonzero vector $x_0$ and repeatedly multiply by $A$. Ignoring normalization for a moment, write the starting vector in the orthonormal eigenbasis:

$$x_0 = c_1q_1+c_2q_2+\cdots+c_nq_n.$$

After $k$ multiplications,

$$A^kx_0 = c_1\lambda_1^kq_1+c_2\lambda_2^kq_2+\cdots+c_n\lambda_n^kq_n.$$

Factor out $\lambda_1^k$ when $\lambda_1$ has uniquely largest magnitude:

$$A^kx_0 = \lambda_1^k\left(c_1q_1+\sum_{j=2}^n c_j(\lambda_j/\lambda_1)^kq_j\right).$$

If $c_1\neq0$, every ratio $(\lambda_j/\lambda_1)^k$ tends to zero. The direction therefore approaches $q_1$, although its length may become extremely large or small. Normalizing after each multiplication prevents that scale problem.

A practical iteration is

$$y_k=Ax_k, \qquad x_{k+1}=\frac{y_k}{\|y_k\|_2}.$$

The vector $x_k$ estimates the dominant eigenvector. To estimate the eigenvalue, use the Rayleigh quotient

$$\rho(x)=\frac{x^TAx}{x^Tx}.$$

For a unit vector, this simplifies to $\rho(x)=x^TAx$. When $x$ is an exact eigenvector, the quotient equals its eigenvalue. The residual

$$r=Ax-\rho(x)x$$

measures how well the current pair satisfies the eigenvalue equation. Its norm, $\|r\|_2$, should become small as the iteration converges. A small change between successive vectors is helpful, but a residual is a more direct test of the eigenpair equation.

## 4. Convergence assumptions and rate

The standard convergence statement assumes that $A$ has a unique dominant eigenvalue in magnitude, $|\lambda_1|>|\lambda_2|$, and that the initial vector has a nonzero component in the dominant eigenvector direction, $c_1\neq0$. Under these assumptions, the normalized iterates converge in direction to $q_1$.

The asymptotic error is controlled by the ratio

$$\left|\frac{\lambda_2}{\lambda_1}\right|.$$

This is called the power-method convergence factor. A small ratio means rapid convergence. A ratio close to one means a small spectral gap and slow convergence. For instance, eigenvalues with magnitudes $10$ and $2$ give a factor of $0.2$, while magnitudes $10$ and $9.8$ give a factor of $0.98$. In the second case, many iterations may be needed.

If the dominant eigenvalue is negative, the direction can alternate sign from one iteration to the next. The vector may appear not to settle because $x_{k+1}$ points approximately opposite to $x_k$. The Rayleigh quotient and residual still provide useful convergence information. Comparing vectors using absolute inner products, or allowing either sign, avoids mistaking this normal behaviour for failure.

Several cases violate the simple guarantee. If the starting vector has exactly zero dominant projection, multiplication cannot create that missing component in an exact eigenbasis, so the method follows another eigenspace. In floating-point arithmetic an exact zero may be perturbed, but relying on that is poor practice; choose a different starting vector. If two eigenvalues share the largest magnitude, such as $\lambda_1=5$ and $\lambda_2=-5$, the iteration generally does not converge to one direction. It may alternate or remain in a combination of dominant eigendirections. A zero product $Ax_k=0$ causes normalization to break down, indicating that the current vector lies in the nullspace.

For non-symmetric matrices, eigenvalues can be complex, eigenvectors need not be orthogonal, and defective matrices may not have a complete eigenbasis. The basic power iteration can still work in some cases, but the symmetric derivation and its clean assumptions no longer apply. Complex dominant eigenvalues can cause rotation rather than convergence to a real vector. For a non-symmetric problem, use an algorithm designed for that setting and interpret residuals carefully.

## 5. A NumPy implementation

The following function normalizes each iterate, estimates the eigenvalue with the Rayleigh quotient, and stops when the residual is below a requested tolerance. It also detects a zero vector before division.

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
        x = np.asarray(x0, dtype=float).reshape(-1)
        if x.size != n:
            raise ValueError("x0 must have one entry per row of A")

    norm_x = np.linalg.norm(x)
    if norm_x == 0:
        raise ValueError("x0 must be nonzero")
    x = x / norm_x

    for iteration in range(1, max_iter + 1):
        y = A @ x
        norm_y = np.linalg.norm(y)
        if norm_y == 0:
            raise ValueError("power iteration broke down: A @ x is zero")

        x = y / norm_y
        eigenvalue = float(x @ A @ x)
        residual = A @ x - eigenvalue * x
        residual_norm = np.linalg.norm(residual)

        if residual_norm <= tol:
            return eigenvalue, x, iteration, residual_norm

    return eigenvalue, x, max_iter, residual_norm


A = np.array([[4.0, 1.0], [1.0, 3.0]])
lam, v, steps, res = power_iteration(A)
print(lam)
print(v)
print(steps, res)
print(np.linalg.norm(A @ v - lam * v))
```

For the symmetric matrix in the example, the dominant eigenvalue is the largest positive eigenvalue, because both eigenvalues are positive. The final printed quantity independently evaluates the residual norm. In a real program, it is also sensible to compare the result with `np.linalg.eigh(A)` while testing, although the iterative routine itself does not require that reference calculation.

A useful diagnostic is to monitor the Rayleigh quotient and residual at every iteration. The quotient may stabilize before the vector components look stable, particularly when the vector sign alternates. Conversely, a visually stable vector is not enough if the residual is still large. Normalization means the vector's scale is controlled, but it does not guarantee convergence.

## 6. Mechanical interpretation and practical limits

In a simplified mechanical model, eigenvectors can resemble characteristic deformation or vibration patterns, and eigenvalues can be related to stiffness, amplification, or squared frequencies depending on how the governing equations are formed. The exact interpretation depends on the model, mass matrix, units, and boundary conditions. The ordinary eigenproblem $Av=\lambda v$ should not automatically be substituted for a generalized problem such as $K v=\lambda M v$.

The main computational advantage of power iteration is that each step needs a matrix-vector product, costing roughly $O(n^2)$ for a dense matrix and potentially much less for a sparse matrix. Its main limitation is that it returns only the dominant-magnitude direction and can be slow when the spectral gap is small. Shifting, deflation, inverse iteration, or specialized symmetric eigensolvers may be preferable when other eigenvalues or higher accuracy are required.

## 7. Exercises and worked solutions

### Exercise 1: concept_check

A real symmetric matrix has eigenvalues $-8$, $6$, and $2$. Which eigenvalue does basic power iteration target under its usual assumptions? Is it the largest algebraic eigenvalue? State one additional assumption about the initial vector.

**Worked solution.** Power iteration targets $-8$, because its magnitude is $8$, larger than $6$ and $2$. It is not the largest algebraic eigenvalue; that is $6$. The initial vector must have a nonzero component in the eigenvector direction associated with $-8$. A unique largest magnitude is also required, and that condition holds here.

### Exercise 2: hand_calculation

Let

$$A=\begin{bmatrix}3&1\\1&3\end{bmatrix}, \qquad x_0=\begin{bmatrix}1\\0\end{bmatrix}.$$

Perform two normalized power iterations using the Euclidean norm. Then compute the Rayleigh quotient and residual for the second normalized vector. Include a consistency check using the known eigenvectors.

**Worked solution.** First,

$$y_0=Ax_0=\begin{bmatrix}3\\1\end{bmatrix}, \qquad \|y_0\|=\sqrt{10},$$

so $x_1=(3,1)^T/\sqrt{10}$. Next,

$$y_1=Ax_1=\frac{1}{\sqrt{10}}\begin{bmatrix}10\\6\end{bmatrix}.$$

Its norm is $\sqrt{136/10}=\sqrt{13.6}$, so

$$x_2=\frac{1}{\sqrt{136}}\begin{bmatrix}10\\6\end{bmatrix}=\frac{1}{\sqrt{34}}\begin{bmatrix}5\\3\end{bmatrix}.$$

The Rayleigh quotient is

$$\rho(x_2)=x_2^TAx_2=\frac{1}{34}[5\ \ 3]\begin{bmatrix}18\\14\end{bmatrix}=\frac{132}{34}=\frac{66}{17}\approx3.882.$$

The residual is

$$r=Ax_2-\rho(x_2)x_2=\frac{1}{17\sqrt{34}}\begin{bmatrix}6\\-10\end{bmatrix},$$

so its norm is approximately $0.363$. As a consistency check, the exact eigenvectors are proportional to $(1,1)^T$ and $(1,-1)^T$, with eigenvalues $4$ and $2$. The vector $(5,3)^T$ is closer to $(1,1)^T$ than to $(1,-1)^T$, and the quotient lies between $2$ and $4$ while moving toward $4$, as expected.

### Exercise 3: code_diagnostic

A student writes this loop:

```python
x = np.ones(A.shape[0])
for _ in range(100):
    x = A @ x
lam = x @ A @ x
```

Identify two problems and describe a correction for each. Why should the final result be checked with a residual?

**Worked solution.** First, the vector is never normalized, so its entries can overflow or underflow even when its direction is converging. The correction is to replace each product by `x = (A @ x) / np.linalg.norm(A @ x)`, while checking that the norm is nonzero. Second, `x @ A @ x` is the Rayleigh quotient only when divided by `x @ x`; if `x` is not unit length, the correction is `lam = (x @ A @ x) / (x @ x)`. A residual check computes `A @ x - lam * x` and its norm. This directly tests the eigenvalue equation and can reveal that a plausible-looking vector has not actually converged, that the method is oscillating, or that the stopping iteration was insufficient.
