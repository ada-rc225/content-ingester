# Eigenvalues, Eigenvectors, and Power Iteration for Structural Vibration

Mechanical engineers often study structures by asking a simple question: how does a system move when it is disturbed? In vibration problems, the answer is encoded in the system’s eigenvalues and eigenvectors. These quantities tell us the natural frequencies and the corresponding mode shapes. In other words, they describe the patterns in which a structure tends to vibrate.

This lesson introduces the mathematics behind eigenvalues and eigenvectors, shows why they matter for modal analysis, and explains the power iteration method, which is one of the simplest numerical algorithms for finding the dominant eigenpair.

## 1. Why eigenvalues appear in vibration

Consider a linear vibrating system written in matrix form as

$$
M\ddot{x}+Kx=0,
$$

where $M$ is the mass matrix, $K$ is the stiffness matrix, and $x(t)$ is the displacement vector. For a structure with several degrees of freedom, both $M$ and $K$ may be large matrices, but the underlying physics is still simple.

To look for a harmonic motion, assume

$$
x(t)=\phi\sin(\omega t),
$$

where $\phi$ is a fixed vector describing the shape of motion and $\omega$ is the natural frequency. Substituting this into the governing equation gives

$$
(K-\omega^2 M)\phi = 0.
$$

This is a generalized eigenvalue problem. The unknowns are the scalar values $\lambda = \omega^2$ and the vectors $\phi$ that satisfy

$$
K\phi = \lambda M\phi.
$$

If the mass matrix is the identity, the problem simplifies to the standard eigenvalue problem

$$
A\phi = \lambda \phi.
$$

In structural dynamics, each eigenvalue corresponds to a natural frequency squared, and each eigenvector is a mode shape. The dominant vibration mode usually refers to the mode associated with the largest eigenvalue magnitude, because it often controls the most energetic response.

## 2. Mathematical definition of eigenvalues and eigenvectors

For a square matrix $A$, a nonzero vector $v$ is an eigenvector if there exists a scalar $\lambda$ such that

$$
Av = \lambda v.
$$

The scalar $\lambda$ is the eigenvalue. The equation says that multiplying the vector by $A$ does not change its direction; it only scales its length by $\lambda$.

This is why eigenvectors are so important in engineering: they identify special directions in which the system behaves in a particularly simple way. For a vibration problem, those directions are the mode shapes.

A useful observation is that if $v$ is an eigenvector, then any nonzero scalar multiple $cv$ is also an eigenvector. The eigenvector is therefore not unique in a strict sense; only its direction matters. In practice, we often normalize the vector so that its length is 1.

For symmetric matrices, the eigenvalues are real and the eigenvectors can be chosen orthogonal. This is very helpful in modal analysis because it allows us to decompose a complicated vibration into independent modes.

## 3. The dominant eigenpair and why it matters

Suppose the eigenvalues of a matrix are ordered by magnitude as

$$
|\lambda_1| > |\lambda_2| \geq |\lambda_3| \geq \cdots.
$$

Then $\lambda_1$ is the dominant eigenvalue and any corresponding eigenvector is the dominant eigenvector. Power iteration is designed to find this pair.

The reason is intuitive. If we repeatedly apply the matrix to a starting vector $x_0$, we obtain

$$
x_1 = Ax_0,
$$

$$
x_2 = A^2x_0,
$$

and so on. If the initial vector has any component along the dominant eigenvector, that component grows faster than the others. After many iterations, the vector direction becomes dominated by the dominant eigenvector.

A simple way to see this is to expand the initial vector in the eigenvector basis:

$$
x_0 = c_1v_1 + c_2v_2 + \cdots.
$$

After $k$ steps,

$$
A^k x_0 = c_1\lambda_1^k v_1 + c_2\lambda_2^k v_2 + \cdots.
$$

Because $|\lambda_1| > |\lambda_2|$, the first term grows or decays faster than the rest. The vector direction therefore approaches $v_1$.

## 4. Convergence conditions and failure modes

Power iteration works well under several conditions.

First, the matrix must have a strictly dominant eigenvalue:

$$
|\lambda_1| > |\lambda_2|.
$$

If this condition fails, convergence can be slow or may not occur in the expected way. For example, if two eigenvalues have the same magnitude, the iteration may oscillate between two directions, and the method may not isolate one mode cleanly.

Second, the starting vector must not be orthogonal to the dominant eigenvector. In practice, a random initial vector almost always has some component along the dominant direction, so the algorithm usually succeeds. If the initial vector happens to be exactly orthogonal to the dominant eigenvector, the method will not find it.

Third, the dominant eigenvalue may be negative. In that case, the sign of the vector may alternate from one iteration to the next, but the direction still converges up to a sign change. This is not a serious issue.

A few important failure modes are:

- The matrix has no strictly dominant eigenvalue.
- The starting vector has no component along the dominant eigenvector.
- The matrix is poorly scaled, causing numerical overflow or underflow.
- The problem is actually a generalized eigenvalue problem, and the algorithm is applied to the wrong matrix.

For structural vibration, the relevant operator is often $A=M^{-1}K$, because the generalized problem $K\phi=\lambda M\phi$ can be rewritten as

$$
M^{-1}K\phi = \lambda \phi.
$$

## 5. The power iteration algorithm

The basic algorithm is straightforward.

1. Choose an initial vector $x_0$.
2. Compute $y_k = Ax_k$.
3. Normalize the vector so that its length is 1.
4. Use the new vector as the next iterate.
5. Repeat until the change is small enough.

In symbols,

$$
\tilde{x}_{k+1} = Ax_k,
$$

$$
x_{k+1} = \frac{\tilde{x}_{k+1}}{\|\tilde{x}_{k+1}\|}.
$$

Once the iterate has stabilized, we estimate the eigenvalue using the Rayleigh quotient:

$$
\lambda_k = \frac{x_k^T A x_k}{x_k^T x_k}.
$$

This quantity converges to the eigenvalue associated with the dominant eigenvector.

## 6. Connecting the mathematics to Python

Here is an executable example using NumPy. The matrix below has a dominant eigenvalue of $5$ and a smaller one of $2$.

```python
import numpy as np

A = np.array([[4.0, 1.0],
              [1.0, 3.0]])

x = np.array([1.0, 0.0])

for k in range(8):
    y = A @ x
    x = y / np.linalg.norm(y)
    lam = x @ (A @ x)
    print(f"iteration {k+1}: x = {x}, lambda ≈ {lam:.6f}")
```

What is happening in the code?

- `A @ x` performs the matrix-vector multiplication $Ax$, which is the core of the iteration.
- `np.linalg.norm(y)` scales the vector to avoid growing without bound.
- `x = y / norm(y)` implements the normalization step from the theory.
- `x @ (A @ x)` computes the Rayleigh quotient, which estimates the eigenvalue.

The output will show that the vector approaches the dominant eigenvector, and the Rayleigh quotient approaches the dominant eigenvalue. The exact direction may be positive or negative depending on the starting vector, but that sign difference is not physically important.

## 7. Stopping criteria

In numerical work, we need a practical stopping rule. Two common choices are:

- Stop when the change in the eigenvector is small:

$$
\|x_{k+1} - x_k\| < \varepsilon.
$$

- Stop when the change in the Rayleigh quotient is small:

$$
|\lambda_{k+1} - \lambda_k| < \varepsilon.
$$

A typical tolerance might be $10^{-6}$ or $10^{-8}$, depending on the desired accuracy. In engineering calculations, the stopping criterion should also reflect the scale of the problem. A very small tolerance is unnecessary if the matrix entries are only known approximately.

## 8. Exercises

1. Prove that if $v$ is an eigenvector of $A$ with eigenvalue $\lambda$, then $cv$ is also an eigenvector for any nonzero scalar $c$.
2. For the matrix
   $$
   A = \begin{bmatrix} 2 & 0 \\ 0 & 5 \end{bmatrix},
   $$
   identify the eigenvalues and eigenvectors. Which eigenpair is dominant?
3. Derive the generalized eigenvalue problem for a mass-spring system from the equation $M\ddot{x}+Kx=0$ and explain why the mode shapes are found from $K\phi=\lambda M\phi$.
4. Modify the Python example so that it stops when $\|x_{k+1}-x_k\| < 10^{-6}$. Report the number of iterations required.
5. Explain what happens if the initial vector is exactly orthogonal to the dominant eigenvector. Why does power iteration fail in that case?
6. Why can the power method struggle when two eigenvalues have equal magnitude? Give a short physical interpretation in terms of vibration modes.

Power iteration is not the most sophisticated eigenvalue algorithm, but it is deeply important because it shows the central idea behind modern numerical linear algebra: repeated application of a matrix reveals the dominant direction of action. In vibration analysis, that dominant direction is often the most important mode of the structure.
