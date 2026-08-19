# Power Iteration for an Idealized Modal Analysis

This lesson develops power iteration as a practical way to approximate a dominant eigenpair. The setting is an idealized modal-analysis bridge: a matrix represents a linear model, vectors represent directions such as mode shapes, and repeated matrix-vector updates reveal a direction associated with an eigenvalue of largest magnitude. The method is useful only when its assumptions and numerical checks are respected. You will work from the eigenpair definition through implementation, convergence limitations, and a worked calculation.

<!-- section: SEC-01 -->
## Eigenpairs as modal directions

Let $A\in\mathbb{R}^{n\times n}$. A non-zero vector $v\in\mathbb{R}^n$ is an eigenvector when there is a scalar $\lambda$ such that

$$Av=\lambda v.$$

The scalar $\lambda$ is the eigenvalue associated with $v$. The non-zero condition matters: the zero vector satisfies $A0=\lambda0$ for every scalar, so it cannot identify an eigenvalue or a meaningful direction. In modal language, an eigenvector supplies a direction whose image under the matrix is merely a rescaling of that direction.

<!-- section: SEC-02 -->
## Which mode does the method seek?

Power iteration targets the eigenvalue of largest magnitude, not necessarily the most positive eigenvalue. For example, between $5$ and $-8$, the dominant value by magnitude is $-8$ because $|-8|>|5|$. This distinction is essential when interpreting a computed mode: “dominant” means largest absolute eigenvalue, not largest algebraic value.

<!-- section: SEC-03 -->
## Orthogonality and projection

For real vectors $u$ and $v$, orthogonality means $u^Tv=0$. A family $v_1,\ldots,v_k$ is orthonormal when different vectors have zero inner product and each vector has unit Euclidean norm:

$$v_i^Tv_j=0\quad(i\ne j),\qquad \|v_i\|_2=1.$$

If $v$ is a unit vector, the scalar coefficient of a vector $x$ in the $v$ direction is $v^Tx$. For example, with $v=(1,0)^T$ and $x=(3,4)^T$, the coefficient is $v^Tx=3$. This projection coefficient will tell us whether an initial vector contains some of the dominant direction.

<!-- section: SEC-04 -->
## The symmetric modal setting

For a real symmetric matrix, $A=A^T$, the spectral theorem provides an orthonormal basis of real eigenvectors. With those eigenvectors as the columns of $Q$,

$$A=Q\Lambda Q^T,\qquad \Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n).$$

Every vector can then be expanded as

$$x=\sum_{i=1}^n c_i v_i,\qquad c_i=v_i^Tx.$$

This is a clean idealized setting for understanding modal directions. The orthogonal decomposition and the convergence explanation below are not claims about arbitrary engineering matrices.

<!-- section: SEC-05 -->
## The dominant-magnitude assumption

Order the eigenvalues by magnitude so that

$$|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.$$

The strict first inequality gives a unique dominant magnitude. It is a condition for the standard convergence story, not a detail to be silently omitted. A matrix may have a most positive eigenvalue that is not the target, and two values can be close in magnitude even when one is technically larger.

<!-- section: SEC-06 -->
## Norms and safe normalization

For $x=(x_1,\ldots,x_n)^T$, its Euclidean norm is

$$\|x\|_2=\sqrt{x_1^2+\cdots+x_n^2}=\sqrt{x^Tx}.$$

For a non-zero vector, compute $r=\|x\|_2$ and set $u=x/r$. Then $\|u\|_2=1$. The zero vector cannot be normalized because division by its zero norm is undefined. For instance, $(3,4)^T$ has norm $5$, so its normalized version is $(3/5,4/5)^T$.

Normalization controls scale while preserving direction. That is why it is inserted between matrix-vector products: the entries do not grow or shrink uncontrollably, but the direction produced by multiplication is retained.

<!-- section: SEC-07 -->
## The matrix-vector update

Choose a non-zero initial vector $x_0$. At each step, first multiply and then normalize:

$$y_{k+1}=Ax_k,\qquad x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.$$

The denominator must be non-zero. The normalized iterate has unit norm and points in the same direction as $Ax_k$, up to a possible sign. This repeated update is the central computational action of power iteration.

<!-- section: SEC-08 -->
## Sign-equivalent mode shapes

If the dominant eigenvalue is negative, successive normalized iterates may alternate sign. This is not, by itself, failure. The vectors $v_1$ and $-v_1$ describe the same eigendirection, so a sign flip can represent the same modal shape direction. Comparing raw vector differences without accounting for this ambiguity can therefore be misleading.

<!-- section: SEC-09 -->
## Inner products for scalar calculations

The expression $x^Ty$ is a scalar dot product, formed by multiplying corresponding components and adding them. To compute $x^TAx$, first form $y=Ax$, then calculate $x^Ty$. The dimensions must be compatible and $A$ must be square for the power-iteration setting. Also,

$$x^Tx=\|x\|_2^2,$$

so this self-inner-product is non-negative. For $A=\begin{bmatrix}2&0\\0&1\end{bmatrix}$ and $x=(1,2)^T$, $Ax=(2,2)^T$ and $x^TAx=1\cdot2+2\cdot2=6$.

<!-- section: SEC-10 -->
## Estimating the eigenvalue

For a non-zero approximate eigenvector $x_k$, use the Rayleigh quotient

$$\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.$$

When $x_k$ has been normalized, $x_k^Tx_k=1$, so this becomes

$$\rho(x_k)=x_k^TAx_k.$$

For a symmetric matrix, if $x_k$ approaches the dominant eigendirection $v_1$, then $\rho(x_k)$ approaches $\lambda_1$. The denominator must be retained whenever the vector is not known to be unit length.

<!-- section: SEC-11 -->
## The residual as a quality check

An estimated eigenvalue and direction should be checked together. Define the eigenpair residual by

$$r_k=Ax_k-\rho(x_k)x_k.$$

For an exact eigenpair, the residual is the zero vector. In computation, $\|r_k\|_2$ measures how closely the pair satisfies the defining equation and supplies a useful stopping signal. A small residual is preferable to relying only on successive-vector similarity, because sign alternation can make two equally valid representatives look far apart.

<!-- section: SEC-12 -->
## The complete algorithm

Given a square matrix $A$, non-zero $x_0$, positive tolerance $\varepsilon$, and a positive maximum iteration count $K$, normalize $x_0$. For each iteration, compute $y=Ax_k$ and check whether $\|y\|_2=0$ before dividing. If it is zero, report breakdown. Otherwise normalize, compute the Rayleigh estimate, compute the residual, and return when the residual norm is at most $\varepsilon$. If that does not happen, stop after $K$ iterations and return the final estimate, vector, residual norm, and iteration count.

The following implementation makes these safeguards executable. It also validates the positive tolerance and iteration count before entering the loop, preventing an empty-loop return from referring to values that were never computed.

When tracing the routine by hand, keep the roles of the variables separate. The current `x` is a normalized direction, `y` is the unnormalized result of applying the matrix, and `y_norm` is the scalar used to restore unit length. The next estimate is formed from the new normalized vector, not from the old one. The residual is then evaluated for that same new vector and its associated Rayleigh estimate. This ordering makes the stopping decision internally consistent.

There are two different kinds of protection in the routine. Shape and initial-vector checks prevent an invalid mathematical input from reaching the iteration. The breakdown check protects the normalization step inside the iteration. The tolerance check asks whether the current approximate eigenpair is good enough, while the iteration cap guarantees termination when the requested tolerance is not reached. These checks answer different questions and should not be replaced by a single test.

For an engineering interpretation, a small residual supports the statement that the computed direction and scalar satisfy the eigenpair equation approximately. It does not by itself prove that the direction is the physically relevant mode, that the matrix is symmetric, or that the method has found a desired algebraically largest eigenvalue. Those conclusions require the assumptions and scope checks discussed later.

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
    if not isinstance(max_iterations, (int, np.integer)) or max_iterations <= 0:
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
```

<!-- section: SEC-13 -->
## Why the dominant direction emerges

In the symmetric eigenbasis, write the initial vector as $x_0=\sum_i c_i v_i$, where $c_i=v_i^Tx_0$. Before normalization, repeated multiplication gives

$$A^k x_0=\sum_{i=1}^n c_i\lambda_i^k v_i
=\lambda_1^k\left(c_1v_1+\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^k v_i\right).$$

If $c_1=v_1^Tx_0\ne0$ and $|\lambda_1|>|\lambda_2|$, the subordinate ratios have magnitude below one and decay as $k$ grows. After the common scale factor is removed by normalization, the dominant direction becomes increasingly influential.

<!-- section: SEC-14 -->
## What convergence means here

For a real symmetric matrix, convergence toward the dominant eigendirection is generally asymptotic when three requirements hold: $|\lambda_1|>|\lambda_2|$, the initial vector has non-zero projection onto $v_1$, and no iterate produces $Ax_k=0$. The direction-error rate is governed qualitatively by

$$\left|\frac{\lambda_2}{\lambda_1}\right|^k.$$

This is not an unconditional finite-iteration error bound. A smaller ratio usually means faster asymptotic improvement; a ratio near one means that many iterations may be needed.

<!-- section: SEC-15 -->
## Missing dominant projection

If $v_1^Tx_0=0$, the initial vector contains no component in the dominant eigendirection. In exact arithmetic, multiplication by $A$ cannot create that missing eigencomponent. The iterates remain in the relevant non-dominant invariant subspace, so the method does not converge to $v_1$. This is a structural failure condition, not merely slow convergence.

<!-- section: SEC-16 -->
## Ties and slow separation

If $|\lambda_1|=|\lambda_2|$, power iteration need not select a unique eigenvector. It may remain in, or oscillate within, the invariant subspace associated with the tied dominant magnitudes. This differs from the case $|\lambda_2/\lambda_1|<1$ but close to one: there is a unique dominant magnitude then, yet convergence can be very slow. Do not promise a unique mode in the tied case.

<!-- section: SEC-17 -->
## Scope of the engineering interpretation

Idealized modal analysis provides an authentic bridge for seeing why directions, projections, and residuals matter. It does not imply that every engineering eigenproblem is symmetric or that every one should be solved by basic power iteration. Power iteration can apply to some non-symmetric matrices, but the clean orthogonal decomposition used here is not generally available. Defective matrices, complex dominant eigenvalues, and non-normal behavior require additional care and are outside this lesson's scope.

<!-- section: SEC-18 -->
## Worked modal calculation

Consider

$$A=\begin{bmatrix}4&1\\1&2\end{bmatrix},\qquad x_0=(1,1)^T.$$

The exact eigenvalues for this example are $3+\sqrt{2}$ and $3-\sqrt{2}$. A short magnitude comparison identifies $3+\sqrt{2}$ as the dominant value. The implementation above uses the supplied initial vector and default parameters, repeatedly normalizes the matrix-vector update, and estimates this dominant value. Its reported residual norm should be small, showing that the returned vector and scalar form an approximate eigenpair. The sign of the returned vector is not prescribed: its negative represents the same eigendirection.

To interpret the output, check all three reported numerical quantities. The eigenvalue should be close to $3+\sqrt{2}$, the vector should have unit norm and align with the dominant modal direction up to sign, and the residual norm should be small. The iteration count indicates whether the residual tolerance was reached early or whether the maximum-iteration fallback was used. This final check connects the update, eigenvalue estimate, residual, and implementation safeguards without deriving a characteristic polynomial.

## Practice checklist

For a new problem, first verify that the matrix and initial vector have compatible shapes and that the initial vector is non-zero. Ask whether the symmetric, unique-dominant-magnitude assumptions are appropriate for the conclusion you want. Trace one multiplication and normalization, then compute the Rayleigh estimate and residual. Finally, distinguish a residual-based stopping decision from a sign-sensitive comparison of vectors, and report any breakdown, missing projection, tied magnitude, or slow separation that limits your interpretation.
