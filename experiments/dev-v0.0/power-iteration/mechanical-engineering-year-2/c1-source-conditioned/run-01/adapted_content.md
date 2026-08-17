# Structural Vibration, Modal Analysis, and the Power Iteration

## Learning objectives

After studying this lesson, you should be able to:

1. define eigenvalues and eigenvectors in the context of a vibration system;
2. explain why the dominant vibration mode corresponds to the eigenvector of largest magnitude;
3. derive and implement the power iteration for a real symmetric stiffness or dynamic matrix;
4. state the convergence assumptions and recognise when the method can fail;
5. use the Rayleigh quotient and residual to assess a vibration mode estimate;
6. connect the mathematics to a working Python example.

## 1. Vibrating structures and eigenpairs

In mechanical engineering, a simple model of a vibrating structure is often written as a matrix equation. For a linear system with mass-normalised coordinates, the stiffness and mass behaviour reduce to a symmetric matrix $A\in\mathbb{R}^{n\times n}$. The natural vibration modes of the structure are given by eigenvectors $v$ and eigenvalues $\lambda$ that satisfy

$$
Av=\lambda v.
$$

Here, $v$ is a mode shape and $\lambda$ is associated with the square of a natural frequency when $A$ is a stiffness-like matrix.

The condition $v\ne0$ is essential. The zero vector is not a physical mode shape because it contains no shape information. An eigenpair $(\lambda,v)$ means the system can vibrate with a consistent shape $v$ while scaling by the factor $\lambda$ under the matrix action.

For a symmetric matrix $A=A^T$, the eigenvectors are real and orthogonal. This symmetry appears in structural vibration because stiffness and mass matrices are usually symmetric when the system is made of linear elastic components and the coordinate basis is chosen consistently.

## 2. Modal analysis and the dominant vibration mode

The spectral theorem for real symmetric matrices gives us an orthonormal basis of eigenvectors, so we can write

$$
A=Q\Lambda Q^T,
$$

with

$$
Q=[v_1,\ldots,v_n],
\qquad
\Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n).
$$

Every displacement vector $x$ in the structure can be decomposed as

$$
x=\sum_{i=1}^n c_i v_i,
\qquad c_i=v_i^T x.
$$

In modal analysis, the coefficient $c_i$ measures how much the initial displacement or loading projects onto the $i$th mode shape. The dominant mode is the mode with the largest eigenvalue magnitude, ordered as

$$
|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.
$$

The eigenvector $v_1$ is the dominant vibration mode. Physically, if the structure is repeatedly excited by the matrix action represented by $A$, the component along $v_1$ will eventually dominate the response because its eigenvalue has the largest magnitude.

This is especially useful when you only need the most significant mode, such as the first bending or first torsional mode in a beam or frame.

## 3. How the power iteration finds the dominant mode

The power iteration is an algorithm that uses repeated matrix-vector products to extract the dominant eigendirection $v_1$. Starting from any non-zero initial vector $x_0$, the method computes:

$$
y_{k+1}=Ax_k,
\qquad
x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.
$$

In a vibration context, $x_k$ can be thought of as a sequence of approximate mode shapes. Each multiplication by $A$ amplifies components of $x_k$ in the directions of the eigenvectors. Normalising preserves the direction without letting the vector grow too large.

The unnormalised sequence satisfies:

$$
A^k x_0
=\sum_{i=1}^n c_i\lambda_i^k v_i
=\lambda_1^k\left(c_1 v_1 + \sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^k v_i\right).
$$

If the starting vector has a non-zero component in the dominant mode,

$$
c_1=v_1^T x_0\ne0,
$$

and if the dominant magnitude is unique,

$$
|\lambda_1|>|\lambda_2|,
$$

then the terms with $i\ge2$ shrink because

$$
\left|\frac{\lambda_i}{\lambda_1}\right|^k\to0.
$$

The normalised vectors $x_k$ therefore approach $\pm v_1$. The sign is not important in vibration mode shapes because $v$ and $-v$ represent the same physical mode shape.

### Convergence statement

For a real symmetric matrix, the power iteration converges under these assumptions:

1. $|\lambda_1|>|\lambda_2|$;
2. the initial vector has non-zero projection onto $v_1$;
3. no iterate gives $Ax_k=0$.

Under these conditions, the direction error decreases roughly like

$$
\left|\frac{\lambda_2}{\lambda_1}\right|^k.
$$

The smaller the ratio $|\lambda_2/\lambda_1|$, the faster the dominant mode emerges. If the ratio is close to one, the convergence is slow because the second mode competes strongly with the dominant mode.

If $\lambda_1$ is negative, the iterates may alternate sign. This still converges to the correct mode shape, because sign reversal does not change the physical mode.

## 4. Estimating the dominant frequency from the mode shape

Once $x_k$ is close to the dominant mode shape, the corresponding eigenvalue can be estimated with the Rayleigh quotient:

$$
\rho(x_k)=\frac{x_k^T A x_k}{x_k^T x_k}.
$$

If $x_k$ is normalised, this simplifies to:

$$
\rho(x_k)=x_k^T A x_k.
$$

For a symmetric matrix, $\rho(x_k)$ approaches $\lambda_1$ when $x_k$ approaches $v_1$. In vibration terms, this means the computed frequency estimate becomes the natural frequency associated with the dominant mode.

The quality of the approximate eigenpair $(x_k,\rho(x_k))$ is measured by the residual:

$$
r_k = A x_k - \rho(x_k) x_k.
$$

If $r_k=0$, then $x_k$ is an exact eigenvector. In practice, a small residual norm

$$
\|r_k\|_2
$$

shows that the approximate mode shape and frequency satisfy the eigenvalue equation closely.

A residual is more reliable than comparing successive vectors because two approximate mode shapes may differ by sign while still representing the same physical vibration mode.

## 5. Practical algorithm for modal extraction

The power iteration algorithm for a symmetric matrix $A$ with initial vector $x_0\ne0$, tolerance $\varepsilon>0$, and maximum iterations $K$ is:

1. normalise $x_0$;
2. compute $y=A x_k$;
3. if $\|y\|_2=0$, stop with a breakdown message;
4. set $x_{k+1}=y/\|y\|_2$;
5. compute $\rho_{k+1}=x_{k+1}^T A x_{k+1}$;
6. compute $r_{k+1}=A x_{k+1} - \rho_{k+1} x_{k+1}$;
7. if $\|r_{k+1}\|_2 \le \varepsilon$, stop;
8. otherwise continue until $K$ iterations are done.

The algorithm returns:

- an approximate dominant eigenvalue $\rho$;
- a unit-norm approximate eigenvector $x$;
- the residual norm $\|r\|_2$;
- the number of iterations used.

This is directly useful in vibration analysis when you only need the first mode and natural frequency of a large symmetric matrix.

## 6. Failure modes in vibration terms

Understanding when power iteration can fail helps avoid incorrect mode estimates.

### Missing the dominant mode

If the initial vector $x_0$ has zero projection on the dominant mode, i.e.

$$
v_1^T x_0 = 0,
$$

then the algorithm cannot recover $v_1$. In vibration terms, if the initial shape contains no component in the strongest mode, repeated application of $A$ cannot create that mode.

### No unique dominant magnitude

If two largest eigenvalues have equal magnitude, $|\lambda_1|=|\lambda_2|$, there is no unique dominant mode direction. The iterates may stay in a subspace spanned by both modes and fail to settle on a single eigenvector.

### Small spectral gap

If $|\lambda_2/\lambda_1|$ is close to one, the energy in the second mode decays slowly. This means the algorithm will take many iterations to isolate the dominant mode from nearby competing modes.

### Dominant versus most positive eigenvalue

Power iteration finds the eigenvalue with largest magnitude, not necessarily the largest positive one. For instance, if the eigenvalues are $5$ and $-8$, the dominant eigenvalue is $-8$. In structural vibration, this can matter if the matrix is not positive definite or if negative stiffness-like behaviour appears in an idealised model.

### Non-symmetric systems

For non-symmetric matrices, the clean mode decomposition is not guaranteed. Defective or complex eigenvalues require more advanced methods than the simple power iteration. In this lesson, we keep to symmetric matrices so the physical vibration interpretation remains clear.

## 7. Python example: dominant vibration mode of a 2-DOF system

A simple two-degree-of-freedom structure can be represented by a symmetric stiffness-like matrix. The power iteration below extracts the dominant mode shape and its eigenvalue estimate.

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


if __name__ == "__main__":
    A = np.array([[4.0, 1.0],
                  [1.0, 2.0]])
    x0 = np.array([1.0, 1.0])

    eigenvalue, eigenvector, residual, iterations = power_iteration(A, x0)

    print("Estimated dominant eigenvalue:", eigenvalue)
    print("Estimated dominant eigenvector:", eigenvector)
    print("Residual norm:", residual)
    print("Iterations:", iterations)
```

### Connecting the code to the math

- The matrix `A` is symmetric, so the spectral theorem applies and the dominant mode is real.
- The initial vector `x0` is non-zero and has a projection on the dominant mode.
- The loop computes `y = A @ x`, which is the matrix action on the approximate mode shape.
- Normalising `y` gives `x = y / y_norm`, matching the mathematical step $x_{k+1} = y_{k+1} / \|y_{k+1}\|_2$.
- The Rayleigh quotient is computed as `eigenvalue = float(x @ (A @ x))`.
- The residual `A @ x - eigenvalue * x` measures how close the pair is to satisfying $Ax = \lambda x$.
- The stopping test uses `residual_norm <= tolerance`.

For the example matrix, the exact eigenvalues are

$$
3+\sqrt{2}
\quad\text{and}\quad
3-\sqrt{2}. 
$$

The power iteration should estimate the dominant eigenvalue $3+\sqrt{2}$ and return a unit-length approximate eigenvector aligned with the dominant vibration mode.

## 8. Exercises

1. For the symmetric matrix $A=\operatorname{diag}(5,2)$ and $x_0=(1,1)^T$, compute the first three unnormalised iterates $A^k x_0$ and explain why the mode shape moves toward the first coordinate direction.
2. Repeat the previous exercise with $x_0=(0,1)^T$. Identify which convergence assumption fails and explain the physical meaning in the vibration model.
3. Suppose a symmetric vibration matrix has eigenvalues $-7$ and $2$. Explain why the iterates may alternate sign while still converging to the dominant mode direction.
4. Construct a symmetric $2\times2$ matrix with eigenvalues $4$ and $3.9$. Use the convergence rate formula $|\lambda_2/\lambda_1|^k$ to explain why the power iteration is slow for this system.
5. Modify the Python implementation to return the residual norm at every iteration, then print the sequence of residual norms for the example matrix. Comment on how quickly the residual decreases.
6. Use `numpy.linalg.eigh` on the example matrix to compute the exact eigenvalues. Compare the dominant eigenvalue from power iteration with the exact result, and explain why the residual norm is the better indicator of accuracy.
7. Describe a physical scenario where the matrix $A$ might not have a unique dominant magnitude and why the power iteration would struggle in that case.

## Summary

The power iteration is a simple modal extraction method for symmetric vibration matrices. It finds the dominant eigenvector by repeatedly applying the matrix and normalising, and it estimates the associated eigenvalue with the Rayleigh quotient. Convergence depends on a unique dominant magnitude, a non-zero projection on the dominant mode, and the absence of breakdown when $Ax_k=0$. The eigenpair residual is the best stopping criterion for a reliable estimate.
