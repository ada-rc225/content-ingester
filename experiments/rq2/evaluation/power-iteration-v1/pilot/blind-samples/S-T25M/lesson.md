# Power iteration: from matrix updates to a checked eigenpair

<!-- section: SEC-01 -->
## The computational object we want

Let $A\in\mathbb{R}^{n\times n}$. An eigenvector is a **non-zero** vector $v$ for which

\[
Av=\lambda v,
\]

and the scalar $\lambda$ is its associated eigenvalue. The non-zero requirement is essential: if $v=0$, then $A0=\lambda 0$ is true for every scalar $\lambda$, so the equation carries no eigenvalue information.

The relation says that multiplying an eigenvector by $A$ changes only its scale, and possibly its sign, not its direction. Power iteration reverses this viewpoint. Instead of starting with a known eigenvector, it repeatedly applies $A$ to a starting vector and looks for a direction that becomes stable.

Think of the desired output as a pair with two linked parts: a direction and a scalar. Returning only a scalar would leave the defining equation unchecked, while returning only a direction would omit the scale factor associated with that direction. This is why the later implementation computes both an approximate vector and an approximate eigenvalue.

<!-- section: SEC-02 -->
## Dominant means largest magnitude

Power iteration targets an eigenvalue of largest **magnitude**, not necessarily the most positive eigenvalue. If two eigenvalues are $5$ and $-8$, then $|-8|>|5|$, so $-8$ is dominant. This distinction matters in code: sorting eigenvalues by their numerical value would answer a different question.

The method is attractive for spectral computation because its main repeated operation is a matrix-vector product. Its convergence is conditional, however, so we will make the relevant assumptions explicit before interpreting a result. In particular, “dominant” will always retain its magnitude-based meaning. A negative estimate is therefore not suspicious merely because another eigenvalue is positive.

<!-- section: SEC-03 -->
## Orthogonality and projection coefficients

For real vectors $u$ and $v$, orthogonality means $u^Tv=0$. A family $v_1,\ldots,v_k$ is orthonormal when different vectors have zero inner product and every vector has Euclidean norm one:

\[
v_i^Tv_j=0\quad(i\ne j),\qquad \|v_i\|_2=1.
\]

When $v$ is a unit vector, the scalar $v^Tx$ is the coefficient of $x$ in the $v$ direction. For example, with $v=(1,0)^T$ and $x=(3,4)^T$, the coefficient is $v^Tx=3$. Later, such a coefficient will tell us whether a starting vector contains any component in a particular eigenvector direction.

There are two separate checks here. To test orthogonality, compute a cross-product and ask whether it is zero. To test whether a family is orthonormal, also compute each vector’s norm and ask whether it is one. Only after the direction vector is known to be a unit vector can its dot product with $x$ be read directly as the stated scalar coefficient.

<!-- section: SEC-04 -->
## The symmetric setting and the gap assumption

Our convergence explanation is for a real symmetric matrix, $A=A^T$. In this setting, the spectral theorem gives an orthonormal basis of real eigenvectors. If those eigenvectors form the columns of an orthogonal matrix $Q$, then

\[
A=Q\Lambda Q^T,\qquad
\Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n),
\]

and every vector can be represented as

\[
x=\sum_{i=1}^n c_i v_i,\qquad c_i=v_i^Tx.
\]

Order the eigenvalues by magnitude and assume a strict first gap:

\[
|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.
\]

The strict inequality makes $\lambda_1$ unique in magnitude. We will not silently weaken it when making the convergence claim.

<!-- section: SEC-05 -->
## Norms and safe normalization

For $x=(x_1,\ldots,x_n)^T\in\mathbb{R}^n$, the Euclidean norm is

\[
\|x\|_2=\sqrt{x_1^2+\cdots+x_n^2}=\sqrt{x^Tx}.
\]

If $x\ne0$, set $r=\|x\|_2$ and $u=x/r$. Then $\|u\|_2=1$, while $u$ points in the same direction as $x$. For $x=(3,4)^T$, the norm is $5$ and the normalized vector is $(3/5,4/5)^T$.

The zero vector is the guard case. Its norm is zero, so division by its norm is undefined. An algorithm must detect this situation before normalizing.

<!-- section: SEC-06 -->
## The power-iteration update

Starting with a non-zero $x_0$, one update is

\[
y_{k+1}=Ax_k,\qquad
x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.
\]

This update is defined only when $y_{k+1}\ne0$. The normalization controls numerical scale without changing the direction produced by the matrix-vector product. After each successful update, a useful iteration invariant is $\|x_{k+1}\|_2=1$. In an implementation, check the norm of $y_{k+1}$ first and divide only after that check passes.

For a one-step trace, take $A=\operatorname{diag}(2,1)$ and begin with $x_0=(1,1)^T$. Normalize the start, multiply by $A$, and normalize again. Equivalently, the unnormalized new direction is $(2,1)^T$, whose norm is $\sqrt5$, so the next iterate is $(2/\sqrt5,1/\sqrt5)^T$. Squaring and adding its components confirms the invariant that the updated norm is one.

<!-- section: SEC-07 -->
## Inner products and quadratic expressions

For real vectors of equal length, $x^Ty$ is the scalar sum of componentwise products. The special case $x^Tx=\|x\|_2^2$ is non-negative.

To compute $x^TAx$, first form $y=Ax$, then take the inner product $x^Ty$. Dimensions must be compatible, and $A$ must be square in our eigenvalue problem. For

\[
A=\begin{bmatrix}2&0\\0&1\end{bmatrix},\qquad x=(1,2)^T,
\]

we get $Ax=(2,2)^T$ and $x^TAx=1\cdot2+2\cdot2=6$. No classification of general quadratic forms is needed here.

<!-- section: SEC-08 -->
## Estimating the eigenvalue

For a non-zero iterate, the Rayleigh quotient is

\[
\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.
\]

Because power iteration normalizes its iterates, $x_k^Tx_k=1$, and the computation simplifies to $\rho(x_k)=x_k^TAx_k$. For a symmetric matrix, as $x_k$ approaches the dominant eigenvector direction, this quotient estimates $\lambda_1$. The denominator must be retained if the vector is not normalized.

The calculation can be traced as three operations: form $Ax_k$, take its dot product with $x_k$, and, when necessary, divide by the squared norm of $x_k$. Keeping those operations explicit is useful when reviewing array shapes. The final quantity is a scalar even though the intermediate matrix-vector product is a vector.

<!-- section: SEC-09 -->
## Measuring approximate-eigenpair quality

An eigenvalue estimate alone does not show how closely its vector satisfies the defining equation. Use the residual

\[
r_k=Ax_k-\rho(x_k)x_k
\]

and measure $\|r_k\|_2$. An exact eigenpair has zero residual. A small residual means the computed pair nearly satisfies the eigenpair equation, making it a practical stopping measure.

This test is robust to eigenvector sign: $v$ and $-v$ represent the same eigendirection. In contrast, a test based only on $\|x_{k+1}-x_k\|_2$ can look large when successive vectors differ mainly by sign.

The residual also reconnects the output to the original definition. Substitute the estimated scalar and vector into the two sides of the eigenpair equation, subtract them, and measure what remains. For an exact pair the two sides agree and the remainder is zero. For an approximation, the norm reports the size of that disagreement without requiring either sign for the vector.

<!-- section: SEC-10 -->
## A safeguarded stopping policy

Given $A$, a non-zero $x_0$, a positive tolerance $\varepsilon$, and a positive maximum iteration count $K$, use this control flow:

1. Normalize $x_0$.
2. Compute $y=Ax_k$.
3. If $\|y\|_2=0$, report breakdown before any division.
4. Set $x_{k+1}=y/\|y\|_2$.
5. Compute $\rho_{k+1}=x_{k+1}^TAx_{k+1}$.
6. Compute $r_{k+1}=Ax_{k+1}-\rho_{k+1}x_{k+1}$.
7. Return when $\|r_{k+1}\|_2\le\varepsilon$.
8. Otherwise continue until $K$ iterations have been performed, then return the final approximation.

The residual stop and iteration cap serve different purposes: one declares that the requested numerical criterion has been met; the other guarantees finite execution.

<!-- section: SEC-11 -->
## Validate inputs before iterating

A NumPy implementation first converts (A) and (x_0) to floating arrays. It must then reject a non-square matrix, an initial vector whose one-dimensional shape is incompatible with the matrix, and a zero initial vector. These cases raise `ValueError` before iteration. The initial vector is normalized only after the checks pass.

The parameters also need explicit contracts: the tolerance must be positive and the maximum iteration count must be a positive integer. Validating them before the loop avoids an undefined final return when no iteration runs.

<!-- section: SEC-12 -->
## Executable iteration semantics

The function below follows the guarded order exactly. Each loop computes the matrix-vector product, checks breakdown, normalizes, forms the Rayleigh estimate and residual, and returns four values: the estimate, vector, residual norm, and iteration count. If tolerance is not reached, the final return reports the iteration cap.

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

result = power_iteration([[2.0, 0.0], [0.0, 1.0]], [1.0, 1.0],
                         tolerance=1e-30, max_iterations=1)
assert len(result) == 4 and result[3] == 1
```

<!-- section: SEC-13 -->
## Why the dominant component emerges

Write the starting vector in the symmetric eigenbasis as $x_0=\sum_i c_i v_i$. Before normalization, repeated multiplication gives

\[
A^kx_0=\sum_{i=1}^n c_i\lambda_i^kv_i
=\lambda_1^k\left(c_1v_1+
\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^kv_i\right).
\]

This discrete coefficient view explains the mechanism. If $c_1=v_1^Tx_0\ne0$ and $|\lambda_1|>|\lambda_2|$, then every subordinate magnitude ratio is below one. Its $k$-th power shrinks, while normalization removes the overall scale $\lambda_1^k$. The dominant direction therefore becomes increasingly prominent.

For a real symmetric matrix, a unique dominant magnitude, non-zero initial projection, and no iterate with $Ax_k=0$ imply that direction error generally decreases asymptotically at a rate governed by

\[
\left|\frac{\lambda_2}{\lambda_1}\right|^k.
\]

This is an asymptotic rate description, not an unconditional finite-iteration error bound.

The ratio is also a useful comparison tool. A subordinate ratio with magnitude $0.2$ has powers that shrink more rapidly than one with magnitude $0.9$. Thus the smaller ratio corresponds to faster asymptotic separation of the dominant component, provided all the stated symmetry, gap, projection, and non-breakdown conditions hold.

<!-- section: SEC-14 -->
## Failure modes and scope limits

Several cases change how a run should be interpreted:

- If $\lambda_1<0$, normalized iterates may alternate sign. That is not failure: $v_1$ and $-v_1$ are the same eigendirection, and the residual remains the appropriate check.
- If $v_1^Tx_0=0$, the starting vector has no dominant component. Exact arithmetic cannot create that missing component, so the method does not converge to $v_1$; this is not merely slow convergence.
- If $|\lambda_1|=|\lambda_2|$, a unique eigenvector need not be selected. The run may oscillate or remain within a dominant invariant subspace.
- If $|\lambda_2/\lambda_1|$ is below but close to one, the dominant magnitude is unique, yet convergence can be very slow. This is distinct from tied dominance.
- If some $Ax_k=0$, normalization is impossible and the algorithm reports breakdown.

Finally, the clean argument above is restricted to real symmetric matrices. Power iteration can apply to some non-symmetric matrices, but an orthogonal real eigenbasis is not generally available. Defective matrices, complex dominant eigenvalues, and non-normal behavior require additional care and lie outside this lesson's scope.

<!-- section: SEC-15 -->
## Worked run and interpretation

Consider

\[
A=\begin{bmatrix}4&1\\1&2\end{bmatrix},\qquad x_0=(1,1)^T.
\]

The exact eigenvalues, supplied for this example, are

\[
3+\sqrt{2}\quad\text{and}\quad3-\sqrt{2}.
\]

A short local comparison gives $|3+\sqrt2|>|3-\sqrt2|$, so the dominant value here is $3+\sqrt2$. Run the self-contained program and compare its estimate with that value.

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

A = np.array([[4.0, 1.0], [1.0, 2.0]])
eigenvalue, eigenvector, residual, iterations = power_iteration(
    A, np.array([1.0, 1.0])
)
print("Estimated dominant eigenvalue:", eigenvalue)
print("Estimated eigenvector:", eigenvector)
print("Residual norm:", residual)
print("Iterations:", iterations)
print("Absolute eigenvalue error:", abs(eigenvalue - (3 + np.sqrt(2))))
```

The estimated eigenvalue should be close to $3+\sqrt2$, and the residual norm should be small. The eigenvector may appear with either sign; neither sign is preferred, because both represent the same eigendirection.

Read the five printed lines as a compact run report. The eigenvalue error compares the estimate with the supplied exact dominant value, while the residual checks the estimated pair directly. The iteration count tells you when the stopping rule fired. None of these checks requires the vector to have a prescribed sign, and the small residual—not sign agreement—is the operational quality signal.
