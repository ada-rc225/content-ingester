# Power Iteration: An Iterative Spectral Computation

Power iteration estimates an eigenpair by repeatedly applying a matrix to a vector and normalising the result. It is a compact example of an iterative numerical algorithm: each update preserves a useful invariant, the stopping rule is based on an error indicator, and the assumptions determine what the result means. A ranking or spectral-computation example can motivate the method, but this simplified algorithm should not be equated with a production ranking system.

This lesson develops the mathematics first and then turns it into pseudocode and guarded Python. By the end, you should be able to trace the matrix–vector update, explain why a dominant eigendirection can survive, identify failure conditions, interpret a residual, and reason about basic stopping and iteration costs.

<!-- section: SEC-01 -->
## Eigenpairs and the motivation for iteration

Let $A\in\mathbb{R}^{n\times n}$. A non-zero vector $v\in\mathbb{R}^n$ is an eigenvector when a scalar $\lambda$ satisfies

$$
Av=\lambda v.
$$

The scalar is the eigenvalue associated with $v$. The non-zero condition is essential: the zero vector satisfies $A0=\lambda0$ for every scalar, so it provides no eigenvalue information. In an algorithm, this means that an initial state must contain an actual direction, not an all-zero placeholder.

Eigenvalues are also roots of the characteristic equation

$$
\det(A-\lambda I)=0,
$$

where $I$ is the compatible identity matrix. For a small matrix, this equation can be a useful verification tool. For a large matrix, explicitly forming the characteristic polynomial is usually a poor numerical strategy. An iterative method can instead use repeated matrix–vector products to estimate a selected eigenpair. That is a computational strategy, not an exact algebraic equivalence to constructing the polynomial.

Power iteration targets the eigenvalue of largest magnitude. This is different from choosing the largest algebraic value: between $5$ and $-8$, the dominant value by magnitude is $-8$. Keep “dominant” tied to absolute value throughout the algorithm and its analysis.

<!-- section: SEC-02 -->
## The symmetric spectral setting

The clearest convergence explanation assumes that $A=A^T$ is real and symmetric. The spectral theorem then supplies an orthonormal basis of real eigenvectors. If these eigenvectors form the columns of $Q$, then

$$
A=Q\Lambda Q^T,
\qquad
\Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n).
$$

Every vector can be represented as

$$
x=\sum_{i=1}^n c_i v_i,
\qquad c_i=v_i^T x.
$$

This representation is useful computationally because it describes the state as a collection of eigendirection components. The orthonormality makes each coefficient a dot product, which is easy to calculate conceptually and numerically.

Order the eigenvalues by magnitude:

$$
|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.
$$

The strict first inequality is an invariant of the convergence argument: it gives one unique dominant magnitude. It does not mean that $\lambda_1$ is necessarily the most positive value. Also, the orthogonal real decomposition just used belongs to the real-symmetric setting. Do not generalise it automatically to arbitrary non-symmetric matrices.

<!-- section: SEC-03 -->
## The normalised power update

Start with a non-zero vector $x_0$. One update has two stages:

$$
y_{k+1}=Ax_k,
\qquad
x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.
$$

The matrix–vector product is the main computational operation. Normalisation divides by the Euclidean norm, controlling scale without changing direction when $y_{k+1}\ne0$. A useful iteration invariant after each successful update is $\|x_k\|_2=1$.

In pseudocode, the core is:

```text
x <- x0 / norm(x0)
repeat:
    y <- A * x
    if norm(y) == 0: report breakdown
    x <- y / norm(y)
```

The check must occur before division. The basic matrix–vector product costs $O(n^2)$ for a dense $n\times n$ matrix, while a sparse representation can have a cost related to its number of non-zero entries. The number of iterations is data- and tolerance-dependent; the loop limit is therefore a safety bound rather than a convergence guarantee.

<!-- section: SEC-04 -->
## Why the dominant direction survives

Write the starting vector in the symmetric eigenbasis, $x_0=\sum_i c_i v_i$. After $k$ unnormalised applications,

$$
A^k x_0
=\sum_{i=1}^n c_i\lambda_i^k v_i
=\lambda_1^k\left(c_1v_1+\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^k v_i\right).
$$

The dominant coefficient is $c_1=v_1^Tx_0$. If $c_1\ne0$ and $|\lambda_1|>|\lambda_2|$, the subordinate ratios have magnitude below one, so their powers become small. The factor $\lambda_1^k$ controls overall scale and possibly sign; after normalisation, the direction increasingly reflects $v_1$.

For a real symmetric matrix, a unique dominant magnitude, non-zero initial projection onto $v_1$, and no zero $Ax_k$ iterate imply that direction error generally decreases asymptotically at a rate governed by

$$
\left|\frac{\lambda_2}{\lambda_1}\right|^k.
$$

This is an asymptotic rate, not an unconditional finite-iteration error bound. A smaller ratio generally gives faster alignment. A ratio close to one predicts slow progress, so a fixed number of loop iterations should not be interpreted as a proof of accuracy.

<!-- section: SEC-05 -->
## Failure modes and scope boundaries

If $\lambda_1<0$, successive normalised vectors may alternate sign. This is not necessarily algorithm failure because $v_1$ and $-v_1$ describe the same eigendirection. An implementation or evaluator that compares vectors only by entrywise closeness can therefore report a false warning.

If $v_1^Tx_0=0$, the initial vector has no component in the dominant eigendirection. In exact arithmetic, repeated multiplication cannot create that missing eigendirection component, so the iteration will not converge to $v_1$. This is a structural failure, not ordinary slow convergence.

If $|\lambda_1|=|\lambda_2|$, a unique eigenvector need not be selected. If the magnitudes are separated but $|\lambda_2/\lambda_1|$ is close to one, convergence can be very slow. These cases have different meanings: one lacks unique dominance, while the other has unique but weak dominance.

Power iteration applies to some non-symmetric matrices, but the clean orthogonal decomposition is not generally available. Defective matrices, complex dominant eigenvalues, and non-normal behaviour require additional care and are outside this lesson’s scope. Similarly, a toy spectral computation may illustrate the loop without representing the full assumptions, preprocessing, and validation of a production ranking system.

<!-- section: SEC-06 -->
## Rayleigh estimates and residual stopping

For a non-zero iterate, use the Rayleigh quotient

$$
\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.
$$

When $x_k$ is normalised, the denominator is one and this reduces to $x_k^TAx_k$. For symmetric $A$, as $x_k$ approaches $v_1$, the quotient estimates $\lambda_1$. The denominator must not be omitted for an unnormalised vector.

The eigenpair residual is

$$
r_k=Ax_k-\rho(x_k)x_k.
$$

An exact eigenpair has zero residual. Thus $\|r_k\|_2$ is a meaningful computational stopping measure: it tests the defining relation for the current vector and eigenvalue estimate. It is more reliable than using only successive-vector similarity, because a sign flip can make two vectors appear far apart even when they represent the same direction. A sound stopping decision records the tolerance and residual rather than claiming exactness from a finite computation.

<!-- section: SEC-07 -->
## Algorithm and guarded implementation

The complete algorithm normalises $x_0$, repeats matrix–vector multiplication and normalisation, checks breakdown before division, computes the Rayleigh estimate and residual, returns early when the residual norm is at most $\epsilon$, and otherwise returns after $K$ iterations. Here is a self-contained implementation. It validates a square matrix, a compatible one-dimensional vector, a non-zero initial vector, positive tolerance, and a valid iteration limit. Each return contains the eigenvalue estimate, vector, residual norm, and iteration count.

```python
import numpy as np


def power_iteration(A, x0, tolerance=1e-10, max_iterations=1000):
    A = np.asarray(A, dtype=float)
    x = np.asarray(x0, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("A must be square")
    if x.ndim != 1 or x.shape[0] != A.shape[0]:
        raise ValueError("x0 must be one-dimensional and compatible with A")
    if np.linalg.norm(x) == 0:
        raise ValueError("x0 must be non-zero")
    if tolerance <= 0 or max_iterations < 1:
        raise ValueError("tolerance must be positive and max_iterations at least 1")

    x = x / np.linalg.norm(x)
    for iteration in range(1, max_iterations + 1):
        y = A @ x
        y_norm = np.linalg.norm(y)
        if y_norm == 0:
            raise RuntimeError("power iteration broke down: A @ x is zero")
        x = y / y_norm
        eigenvalue = float(x @ A @ x / (x @ x))
        residual_norm = float(np.linalg.norm(A @ x - eigenvalue * x))
        if residual_norm <= tolerance:
            return eigenvalue, x, residual_norm, iteration
    return eigenvalue, x, residual_norm, max_iterations


A = np.array([[4.0, 1.0], [1.0, 2.0]])
result = power_iteration(A, np.array([1.0, 1.0]))
print("estimate =", result[0])
print("residual =", result[2])
print("iterations =", result[3])
```

For dense matrices, each loop performs a matrix–vector multiplication and a small number of vector operations. The implementation uses $K$ as a maximum iteration count, so its dense arithmetic work is bounded at a high level by $O(Kn^2)$. This estimate describes the loop’s computational cost; it does not certify convergence or numerical accuracy.

The distinction between a loop invariant and a stopping condition is important. The unit-norm property is maintained after successful normalisation, so it helps keep the representation numerically manageable. The residual tolerance is not maintained automatically; it is measured and used to decide whether to return early. A vector can have unit norm while still being a poor eigenvector, and an eigenvalue estimate can look stable while the residual remains larger than the required tolerance. Good numerical code keeps these roles separate.

The maximum-iteration fallback is part of the algorithm’s interface. Reaching $K$ means that the function has produced its best available state under the configured budget, not that the residual is necessarily acceptable. A caller can inspect the returned residual and iteration count, then decide whether to increase $K$, adjust the tolerance, change the initial vector, or investigate the matrix assumptions. This is an algorithmic decision process rather than an implicit promise that every input converges.

<!-- section: SEC-08 -->
## Worked consolidation

Consider

$$
A=\begin{bmatrix}4&1\\1&2\end{bmatrix},
\qquad x_0=(1,1)^T.
$$

The matrix is real and symmetric. Its exact eigenvalues are

$$
3+\sqrt{2}\quad\text{and}\quad 3-\sqrt{2}.
$$

The dominant target is $3+\sqrt{2}$ because it has the larger magnitude. Starting with the supplied non-zero vector, the implementation normalises it, repeatedly computes $A@x$, and monitors the residual. It should estimate $3+\sqrt{2}$ and produce a small residual under the default stopping process. The returned eigenvector may have either sign; a small residual does not require one particular sign.

A useful trace table has columns for the iteration number, $y$, $\|y\|_2$, $x$, $\rho(x)$, and $\|r\|_2$. The first columns expose the update and the invariant, while the final columns separate an eigenvalue estimate from a quality check. For each row, ask: did the loop avoid breakdown, is the vector normalised, is the residual decreasing, and did the run stop by tolerance or by the maximum count?

For a final algorithmic review, separate three questions. What target is selected? The largest magnitude eigenvalue. Why should the direction approach it? The symmetric decomposition, strict magnitude gap, non-zero dominant projection, and non-breakdown assumptions. Is the reported pair acceptable? Inspect the Rayleigh estimate, residual, iteration count, and stopping reason. This separation prevents a plausible output from being treated as a guaranteed result outside the assumptions supporting the iteration.

As a self-check, explain what each guard contributes. The square-shape check prevents an invalid matrix operation; the dimension check prevents an incompatible state; the non-zero check ensures that the initial direction exists; the breakdown check prevents division by zero; and the residual test gives the early-return criterion. Then compare two hypothetical runs with the same matrix and tolerance but different initial vectors. If both have non-zero dominant projections, they may approach the same dominant eigendirection at different rates. If one starts with an exactly zero dominant projection, repeated multiplication cannot repair that missing component in exact arithmetic. The data structure, control flow, and mathematical assumptions therefore need to be read together.
