# Power Iteration for the Dominant Vibration Mode

Mechanical structures do not just move randomly when they vibrate. In many engineering systems, the motion can be described as a combination of a few natural shapes, or modes, each with its own natural frequency. The dominant vibration mode is the one that grows most strongly in a given dynamic system and is often the first mode engineers need to understand when checking resonance or fatigue.

In this lesson, we use the language of matrices and eigenvalues to explain how a numerical method called power iteration can find that dominant mode.

<!-- section: SEC-01 -->
## From vibration modes to eigenvalue problems

Think of a small structural system with a few degrees of freedom, such as a mass-spring model or a simplified beam discretised into nodes. If the system is vibrating freely, the displacement vector $u(t)$ can be written in terms of a spatial shape $v$ and a time dependence. After applying the governing equations, one arrives at a matrix relation of the form

$$
A v = \lambda v.
$$

This is the defining equation for an eigenvalue problem. The non-zero vector $v$ is an eigenvector, and the scalar $\lambda$ is its eigenvalue. In vibration analysis, the eigenvectors are often interpreted as mode shapes, while the eigenvalues encode the associated natural frequencies or scaling behaviour.

The condition $v \neq 0$ is essential. The zero vector satisfies $A0 = \lambda 0$ for every $\lambda$, but it does not reveal any genuine mode shape. In the same way, a structure does not have a meaningful vibration shape if we start from a zero displacement field.

For a real symmetric matrix, the spectral theorem guarantees that there is an orthonormal set of real eigenvectors. We may write

$$
A = Q\Lambda Q^T,
$$

where $Q$ contains the eigenvectors and $\Lambda$ is diagonal with the eigenvalues. This is the mathematical reason why symmetric systems are especially convenient for modal analysis: their vibration modes can be treated as orthogonal directions in the state space.

<!-- section: SEC-02 -->
## Why the dominant mode matters

In many practical problems, one mode is much more important than the others. The dominant vibration mode is the mode associated with the eigenvalue of largest magnitude. If the matrix is symmetric and the eigenvalues are ordered by magnitude as

$$
|\lambda_1| > |\lambda_2| \ge \cdots \ge |\lambda_n|,
$$

then $\lambda_1$ is the unique dominant eigenvalue and $v_1$ is the dominant eigendirection. This matters because the largest-magnitude mode often controls the strongest response in the system.

The power iteration is designed for exactly this situation. It does not try to compute all modes at once. Instead, it repeatedly amplifies the component along the dominant mode and suppresses the weaker ones. In structural terms, if one vibration shape is more strongly excited or more energetically significant, the iteration will gradually reveal it.

There is an important caveat. The method only works well when the dominant magnitude is unique. If two modes have the same magnitude, the iteration may not pick one clearly. Also, if the initial guess has no component in the dominant eigendirection, the method cannot recover it in exact arithmetic.

A negative dominant eigenvalue is also possible. In that case, the iterates may alternate sign, but the underlying eigendirection is still being found. The sign flip is not a failure; it only means that $v_1$ and $-v_1$ represent the same physical mode shape up to direction.

<!-- section: SEC-03 -->
## Power iteration as a repeated vibration update

Power iteration starts from a non-zero vector $x_0$ and repeatedly applies the matrix. At each step,

$$
 y_{k+1} = A x_k,
$$

and then we normalise the vector so the iteration does not explode or collapse:

$$
 x_{k+1} = \frac{y_{k+1}}{\|y_{k+1}\|_2}.
$$

The normalisation does not change direction; it only keeps the iterate on the unit sphere. In code, this means we repeatedly form a matrix-vector product and then divide by the Euclidean norm.

To understand why this works, write the initial vector as a combination of eigenvectors:

$$
x_0 = \sum_{i=1}^n c_i v_i.
$$

After $k$ applications of $A$, we get

$$
A^k x_0 = \sum_{i=1}^n c_i \lambda_i^k v_i.
$$

If the dominant eigenvalue satisfies $|\lambda_1| > |\lambda_2|$ and $c_1 \neq 0$, then the term involving $\lambda_1^k$ eventually dominates because the ratios

$$
\left|\frac{\lambda_i}{\lambda_1}\right|^k
$$

go to zero for $i \ge 2$. The iteration therefore converges to the direction of the dominant eigenvector, up to sign.

The convergence is faster when the spectral gap is large. If $|\lambda_2/\lambda_1|$ is close to one, the iteration is slow because the second mode remains nearly as strong as the dominant one.

<!-- section: SEC-04 -->
## Estimating the modal frequency and checking the approximation

Once the vector $x_k$ is close to an eigenvector, we can estimate the corresponding eigenvalue using the Rayleigh quotient:

$$
\rho(x_k)=\frac{x_k^T A x_k}{x_k^T x_k}.
$$

If $x_k$ is normalised, this simplifies to

$$
\rho(x_k)=x_k^T A x_k.
$$

This quantity is important because it gives a scalar estimate of the modal scaling associated with the current approximate mode shape. In vibration language, it plays the role of an estimated modal value linked to the current approximate mode.

To assess the quality of the approximation, we compute the residual

$$
 r_k = A x_k - \rho(x_k) x_k.
$$

If the pair $(x_k, \rho(x_k))$ were exact, the residual would be zero. In practice, a small residual norm $\|r_k\|_2$ is a better stopping test than simply checking whether two successive vectors look similar. This is especially important because eigenvectors are only defined up to sign: $x_k$ and $-x_k$ describe the same direction, even though their difference can be large in a naive componentwise comparison.

The practical algorithm is therefore:

1. start with a non-zero vector $x_0$;
2. compute $y = A x_k$;
3. if $\|y\|_2 = 0$, stop because the iteration has broken down;
4. normalise to get $x_{k+1}$;
5. compute $\rho_{k+1}$ and the residual;
6. stop when the residual is below a chosen tolerance.

<!-- section: SEC-05 -->
## Python implementation and exercises

The following short NumPy example implements the method for a symmetric $2\times 2$ matrix. The matrix is small enough that we can compare the result with the known eigenvalues, but the same structure works for larger systems.

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

lambda_est, mode_est, residual, iterations = power_iteration(
    A, np.array([1.0, 1.0])
)

print("Estimated dominant eigenvalue:", lambda_est)
print("Estimated dominant mode shape:", mode_est)
print("Residual norm:", residual)
print("Iterations:", iterations)
```

How does this connect to the mathematics? The line `y = A @ x` performs the repeated matrix-vector multiplication that pushes the iterate toward the dominant eigendirection. The line `x = y / np.linalg.norm(y)` is the normalisation step. The Rayleigh quotient is computed as `x @ (A @ x)`, and the residual is built from the difference between `A @ x` and that scalar times `x`. When the residual becomes small, the approximate eigenpair is trustworthy.

For this matrix, the eigenvalues are

$$
3 + \sqrt{2}
\quad\text{and}\quad
3 - \sqrt{2},
$$

so the dominant eigenvalue is $3 + \sqrt{2}$. The code should recover that dominant mode and produce a small residual.

Exercises:

1. For a simple diagonal matrix $A = \operatorname{diag}(5,2)$ and $x_0 = (1,1)^T$, write down the first three unnormalised iterates and explain which mode dominates.
2. Repeat the exercise with $x_0 = (0,1)^T$. Which assumption fails, and why?
3. A structure has a dominant eigenvalue $-8$ and another eigenvalue $5$. Explain why the power iteration still targets $-8$ even though $5$ is algebraically larger.
4. Explain why the residual norm is a better stopping test than the difference between two successive vectors when the eigenvector is only defined up to sign.
5. Modify the Python function to store the residual norm at each iteration and print it after every step. What does the trend tell you about convergence?
6. Compare the computed eigenvalue with `numpy.linalg.eigh` and justify whether the approximation is good using the residual rather than decimal agreement alone.
