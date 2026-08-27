# Power iteration: finding a dominant eigenpair

Power iteration is a simple method for approximating one eigenvalue and its eigenvector using repeated matrix-vector multiplication. In this lesson, you will build the method from its eigenpair definition, see why it converges in a clean symmetric setting, learn how to judge an approximation with a residual, and implement the complete algorithm with essential safeguards.

<!-- section: SEC-01 -->
## Eigenpairs and why iteration is useful

Let $A\in\mathbb{R}^{n\times n}$. A non-zero vector $v\in\mathbb{R}^n$ is an eigenvector of $A$ when there is a scalar $\lambda$ such that

$$
Av=\lambda v.
$$

The scalar $\lambda$ is the eigenvalue associated with $v$. The condition $v\ne 0$ matters: the zero vector satisfies $A0=\lambda 0$ for every scalar, so it cannot carry information about a particular eigenvalue.

Eigenvalues are roots of the characteristic equation

$$
\det(A-\lambda I)=0,
$$

where $I$ is the identity matrix of the same dimension as $A$. This equation is useful algebraically, but explicitly forming a characteristic polynomial is usually a poor numerical strategy for a large matrix. Iterative methods instead use repeated matrix-vector products to estimate selected eigenpairs.

Power iteration targets the eigenvalue with the largest absolute value, often called the dominant eigenvalue. “Largest” therefore means largest magnitude, not largest algebraic value. If two eigenvalues are $5$ and $-8$, then $-8$ is dominant because $|-8|>|5|$. This distinction will also explain why signs may alternate during an otherwise successful iteration.

The method is therefore selective rather than a way to list every eigenpair at once. Its basic operation is deliberately modest: apply the matrix to a vector and observe how the vector’s direction changes. Repeating that operation is attractive because it avoids constructing the characteristic polynomial. The remaining questions are whether one direction becomes dominant, which assumptions make that happen, and how a computation can recognize that its current vector and scalar form a good approximate pair.

<!-- section: SEC-02 -->
## The symmetric spectral setting

The convergence mechanism is especially clear when $A$ is real and symmetric, so $A=A^T$. The spectral theorem then gives an orthonormal basis of real eigenvectors. If these eigenvectors form the columns of the orthogonal matrix $Q$, then

$$
A=Q\Lambda Q^T,
\qquad
\Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n).
$$

Every vector $x$ can consequently be expanded in the eigenvector basis:

$$
x=\sum_{i=1}^n c_i v_i,
\qquad c_i=v_i^T x.
$$

For the main convergence result, order the eigenvalues by magnitude and assume a strict gap at the top:

$$
|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.
$$

Thus $\lambda_1$ is unique in magnitude. The strict inequality is important: it creates one dominant eigendirection and makes every subordinate eigenvalue smaller relative to $\lambda_1$. These statements concern absolute values throughout; they do not require $\lambda_1$ to be positive.

Orthonormality makes the coefficients especially easy to interpret. Taking the inner product with $v_i$ isolates $c_i$, so the expansion records precisely how much of each eigenvector direction is present. Multiplying by $A$ then scales the component along $v_i$ by $\lambda_i$. This component-by-component description is the bridge between the spectral theorem and the iterative algorithm; it is also why the real symmetric setting supports such a clean explanation.

<!-- section: SEC-03 -->
## The normalized power update

Choose a non-zero starting vector $x_0$. Power iteration repeatedly performs

$$
y_{k+1}=Ax_k,
\qquad
x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.
$$

The matrix-vector product changes the mixture of eigenvector components. Normalization then controls the scale: provided $y_{k+1}\ne0$, the new vector has unit 2-norm. Dividing by a non-zero scalar does not change its direction, which is the quantity of interest for an eigenvector. A zero normalizing denominator is a breakdown and must be detected before division.

As a quick trace, begin with a chosen $x_0$, normalize it, compute $Ax_0$, measure the result’s 2-norm, and divide. Repeating these two operations—multiply and normalize—is the computational core of the method.

It is worth separating the roles of the two steps. Multiplication is responsible for changing the relative sizes of the eigenvector components. Normalization prevents the overall length from growing or shrinking uncontrollably and produces a comparable unit vector at every stage. It does not repair a poor starting direction, create a missing component, or choose a different mathematical target. When tracing an update by hand, check the product first, verify that its norm is non-zero, and only then normalize.

<!-- section: SEC-04 -->
## Why a dominant component emerges

Use the symmetric eigenbasis to write the starting vector as $x_0=\sum_i c_i v_i$. Before normalization, $k$ repeated multiplications give

$$
A^k x_0
=\sum_{i=1}^n c_i\lambda_i^k v_i
=\lambda_1^k\left(c_1v_1+
\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^k v_i\right).
$$

Suppose the starting vector actually contains the dominant component, meaning

$$
c_1=v_1^Tx_0\ne0.
$$

Under the strict magnitude gap, every subordinate ratio has magnitude below one. Its contribution therefore decays relative to the dominant term as $k$ grows. Normalization removes the overall scale $\lambda_1^k$ while retaining the increasingly dominant direction.

More precisely, for a real symmetric matrix, direction convergence requires a unique dominant magnitude, a non-zero initial projection onto $v_1$, and no iterate for which $Ax_k=0$. Under those assumptions, the direction error generally decreases asymptotically at a rate governed by

$$
\left|\frac{\lambda_2}{\lambda_1}\right|^k.
$$

This is an asymptotic rate description, not an unconditional error bound for a fixed finite iteration. It does explain the main trend: a smaller magnitude ratio produces faster eventual decay of non-dominant components.

The factorization also explains why all of the convergence assumptions appear together. The coefficient $c_1$ ensures that a dominant term is present. The strict gap makes each relative subordinate factor smaller than one in magnitude. The non-breakdown condition ensures that every requested normalization is defined. If these conditions hold, normalization exposes the direction already becoming dominant in the unnormalized sequence; it is not itself the source of dominance. For a fixed ratio, increasing $k$ repeatedly applies the same relative suppression, which is the origin of the power in the rate expression.

<!-- section: SEC-05 -->
## Failure modes and boundaries

Several cases qualify or prevent the preceding conclusion. First, if the dominant eigenvalue is negative, successive normalized iterates may alternate sign. This alone is not failure: $v_1$ and $-v_1$ describe the same eigendirection. Comparing successive vectors without accounting for this ambiguity could therefore give a misleading impression.

Second, if $v_1^Tx_0=0$, the initial vector contains no dominant component. In exact arithmetic, repeated multiplication cannot create that missing eigenvector component, so the method does not converge to $v_1$. This is different from slow convergence.

Third, if $|\lambda_1|=|\lambda_2|$, the dominant magnitude is not unique. The iteration need not select one eigenvector; it may remain in, or oscillate within, the invariant subspace associated with those dominant magnitudes. If instead $|\lambda_2/\lambda_1|$ is below but close to one, the dominant direction is unique but convergence may be very slow. Repeated dominance and a small spectral gap are distinct situations.

Finally, the orthonormal eigenbasis argument above belongs to real symmetric matrices. Power iteration can be applied to some non-symmetric matrices, but a clean orthogonal decomposition is not generally available. Defective matrices, complex dominant eigenvalues, and non-normal behavior need additional care and lie outside this lesson’s scope. Do not transfer the symmetric convergence argument to every non-symmetric matrix.

These cases suggest a useful diagnostic sequence. A sign change should first be interpreted at the level of direction, where opposite signs are equivalent. Persistent failure to approach the intended direction calls for checking the starting projection. Lack of a unique result calls for checking whether the largest magnitudes are tied. Slow progress with a unique dominant magnitude calls for examining whether the ratio is close to one. Each diagnosis points to a different condition, so none should be used as a catch-all explanation for every disappointing run.

<!-- section: SEC-06 -->
## Estimating the eigenvalue and measuring quality

Once $x_k$ is an approximate eigenvector, estimate its eigenvalue with the Rayleigh quotient

$$
\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.
$$

The vector must be non-zero. When it has unit norm, $x_k^Tx_k=1$, so the expression simplifies to

$$
\rho(x_k)=x_k^TAx_k.
$$

For a symmetric matrix, as $x_k$ approaches the eigendirection of $v_1$, this estimate approaches $\lambda_1$. To assess the approximate pair, compute the residual

$$
r_k=Ax_k-\rho(x_k)x_k.
$$

An exact eigenpair has zero residual. Accordingly, $\|r_k\|_2$ is a meaningful stopping measure: it directly measures how closely the defining eigenpair equation is satisfied. A test based only on $\|x_k-x_{k-1}\|_2$ can be distorted by a harmless sign flip, whereas the residual remains tied to the eigenpair relation. A practical algorithm stops when the residual norm is at most a chosen positive tolerance.

The Rayleigh estimate and the residual answer different but connected questions. The quotient supplies the scalar paired with the current vector, while the residual tests that pairing in the original equation. A small change in successive vectors is not a substitute for this test, because direction has a sign ambiguity and apparent stability alone does not state how well $Ax_k$ matches a scalar multiple of $x_k$. Always compute the residual using the same Rayleigh estimate and current vector.

<!-- section: SEC-07 -->
## A safeguarded algorithm

Given $A$, non-zero $x_0$, tolerance $\varepsilon>0$, and a positive integer iteration limit $K$, first normalize $x_0$. Each iteration computes $y=Ax_k$, checks for zero norm before division, normalizes to obtain $x_{k+1}$, and then computes the Rayleigh estimate and residual. Stop if the residual norm is no larger than $\varepsilon$; otherwise stop after $K$ iterations. The following implementation also converts inputs to floating arrays and validates matrix shape, vector dimensions, and parameters.

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
    if (isinstance(max_iterations, (bool, np.bool_)) or
            not isinstance(max_iterations, (int, np.integer)) or
            max_iterations <= 0):
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
result = power_iteration(A, np.array([1.0, 1.0]))
print("Estimated dominant eigenvalue:", result[0])
print("Estimated eigenvector:", result[1])
print("Residual norm:", result[2])
print("Iterations:", result[3])
```

The function returns four values: the eigenvalue estimate, normalized eigenvector estimate, residual norm, and iterations performed. A successful tolerance test returns early; if it never succeeds, the final estimates are returned at the iteration cap.

Notice the order of the safeguards. Invalid shapes and parameters are rejected before iteration, and a zero starting vector is rejected before initial normalization. Inside the loop, the norm of $A x$ is checked before division. Only after a new unit vector exists does the code form its eigenvalue estimate and residual. The tolerance and iteration cap provide two distinct exit routes: satisfying the requested residual quality or exhausting the permitted work. Reaching the cap returns an approximation but does not claim that the tolerance was met.

<!-- section: SEC-08 -->
## Worked consolidation

For the matrix used in the code,

$$
A=\begin{bmatrix}4&1\\1&2\end{bmatrix},
\qquad x_0=\begin{bmatrix}1\\1\end{bmatrix},
$$

the exact eigenvalues are

$$
3+\sqrt{2}
\quad\text{and}\quad
3-\sqrt{2}.
$$

Both are positive, and $3+\sqrt{2}$ has the larger magnitude. The supplied starting vector has a non-zero component in its eigendirection, so the safeguarded iteration should estimate $3+\sqrt{2}$ and report a small residual with the default tolerance. The sign of the returned eigenvector is not prescribed; changing it does not change the eigendirection or the residual quality.

To consolidate the full process, identify the dominant eigenvalue by magnitude, verify the symmetric setting and the starting-vector projection assumption, trace multiply-and-normalize updates, form the Rayleigh estimate, and inspect the residual norm. The convergence rate explains how quickly subordinate components fade, while the safeguards and iteration cap ensure that the computation has defined behavior even when convergence is not achieved within the allotted iterations.

When reading the program’s output, connect each field back to this chain of reasoning. The eigenvalue should be compared with the dominant exact value, the vector should be interpreted up to sign, the residual should be compared with the tolerance, and the iteration count should reveal whether stopping occurred before the cap. Together these observations consolidate the mathematical mechanism and the computational stopping decision without treating any one printed quantity as sufficient on its own.
