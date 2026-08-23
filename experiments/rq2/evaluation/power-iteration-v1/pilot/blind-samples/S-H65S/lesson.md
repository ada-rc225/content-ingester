# Power Iteration as a Safeguarded Spectral Algorithm

Power iteration is a compact algorithm for approximating an eigenpair using repeated matrix–vector multiplication. Its computational simplicity can make it look universally reliable, but the output is meaningful only when its assumptions, invariants, stopping rule, and failure paths are made explicit. This lesson develops those pieces in an order that supports both pseudocode tracing and executable NumPy code.

<!-- section: SEC-01 -->
## The eigenpair target

Let $A\in\mathbb{R}^{n\times n}$. A non-zero vector $v\in\mathbb{R}^n$ is an eigenvector when

$$Av=\lambda v,$$

for a scalar $\lambda$, called its associated eigenvalue. The non-zero condition is essential: $A0=\lambda0$ holds for every scalar, so the zero vector contains no eigenvalue information.

The standard power iteration target is the eigenvalue of largest magnitude, not necessarily the most positive eigenvalue. Between $5$ and $-8$, for example, $-8$ is dominant because $|-8|>|5|$. An implementation or its documentation should therefore say “largest magnitude” rather than silently substituting “largest value.”

<!-- section: SEC-02 -->
## The spectral assumptions behind the invariant

The clean convergence explanation used here assumes that $A=A^T$ is real and symmetric. The spectral theorem then gives an orthonormal basis of real eigenvectors and a decomposition

$$A=Q\Lambda Q^T,\qquad \Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n).$$

The orthonormal basis supports projection coordinates: for an eigenvector $v_i$, the coefficient of a vector $x$ in that direction is $c_i=v_i^Tx$. In algorithmic terms, these coefficients describe which spectral components are present in the input. They are useful for reasoning about an iteration invariant, but the spectral theorem and convergence claims must not be extended automatically to arbitrary non-symmetric matrices.

Order the eigenvalues by magnitude:

$$|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.$$

The strict first inequality means that the dominant magnitude is unique. It is a precondition for the usual directional convergence statement, not a result guaranteed by the loop itself.

<!-- section: SEC-03 -->
## Norms, normalization, and the update invariant

For a real vector $x=(x_1,\ldots,x_n)^T$, the Euclidean norm is

$$\|x\|_2=\sqrt{x_1^2+\cdots+x_n^2}=\sqrt{x^Tx}.$$

If $x\ne0$, define $u=x/\|x\|_2$. Then $\|u\|_2=1$. If $x=0$, division by its norm is undefined, so a robust implementation must stop before dividing.

Power iteration applies this idea after every matrix–vector product. Starting from a non-zero $x_0$,

$$y_{k+1}=Ax_k,\qquad x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.$$

The key invariant is that each successful $x_k$ has unit Euclidean norm. The matrix product changes the direction and possibly the scale; normalization removes the scale without changing the direction of a non-zero product. The second safeguard is therefore a check that $\|y_{k+1}\|_2\ne0$ before the division.

A pseudocode trace should record the input vector, product, product norm, normalized vector, and whether the invariant $\|x_k\|_2=1$ holds. These records distinguish a real update from a failed normalization.

This invariant is a useful debugging contract. It does not say that the vector is already an eigenvector; it says only that successful updates keep scale controlled. A vector can have unit norm and still have a large residual. Conversely, changing the sign of a unit vector preserves its norm and can preserve its eigendirection. When implementing the loop, check the invariant at the point where normalization has completed, rather than treating the input or the unnormalized product as if it already satisfied it.

<!-- section: SEC-04 -->
## Estimates, inner products, and residuals

For compatible real vectors, $x^Ty$ is the scalar inner product. To compute $x^TAx$, first form $y=Ax$ and then compute $x^Ty$. Also, $x^Tx=\|x\|_2^2$. These operations provide the quantities needed for an approximate eigenvalue.

The Rayleigh quotient is

$$\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.$$

It requires a non-zero vector. When $x_k$ is normalized, $x_k^Tx_k=1$, so the expression simplifies to $\rho(x_k)=x_k^TAx_k$. For symmetric $A$, as $x_k$ approaches the dominant eigendirection, this estimate approaches the associated dominant eigenvalue.

The approximate-eigenpair quality measure is the residual

$$r_k=Ax_k-\rho(x_k)x_k.$$

An exact eigenpair gives a zero residual. In code, use $\|r_k\|_2$ as the operational diagnostic. Comparing successive vectors alone is unsafe because a negative dominant eigenvalue can make normalized iterates alternate sign even while their eigendirection improves. A residual threshold is therefore more robust than a raw vector-difference test.

<!-- section: SEC-05 -->
## Safeguarded pseudocode and stopping policy

Given a non-zero initial vector, positive tolerance $\varepsilon$, and maximum iteration count $K$, the algorithm is:

1. Normalize $x_0$.
2. Compute $y=Ax_k$.
3. If $\|y\|_2=0$, stop with a breakdown message before division.
4. Set $x_{k+1}=y/\|y\|_2$.
5. Compute $\rho_{k+1}=x_{k+1}^TAx_{k+1}$.
6. Compute $r_{k+1}=Ax_{k+1}-\rho_{k+1}x_{k+1}$.
7. Stop if $\|r_{k+1}\|_2\le\varepsilon$.
8. Otherwise continue, but stop after $K$ iterations.

This order is part of the algorithm's meaning. The breakdown check must precede division, the residual check must be connected to the current normalized iterate, and the iteration cap must remain available when the tolerance is not reached. A production implementation should also reject a zero initial vector and invalid tolerance or iteration-limit values before entering the loop.

There are two distinct stopping outcomes to report. Reaching the residual threshold means the current computed pair met the requested numerical criterion. Reaching $K$ means the algorithm returned its best current diagnostics at the allowed work limit without satisfying that criterion. The second outcome is not proof of failure, but it must not be reported as successful tolerance convergence. Keeping these outcomes separate is important when comparing implementations, choosing a tolerance, or diagnosing a small spectral gap.

For a matrix with $n$ rows and columns, one dense matrix–vector product costs $O(n^2)$ arithmetic operations and stores $O(n^2)$ matrix data, apart from the vectors and scalar diagnostics. If the matrix is sparse, the product cost depends on the number of stored nonzero entries; that is an implementation consideration, not a new convergence guarantee. The stopping tolerance and spectral gap determine how many iterations may be useful, while the cap gives a deterministic upper bound on loop work.
The cap is also a reproducibility control: two runs with the same inputs and parameters have the same maximum number of update attempts, even if neither reaches the tolerance. A tolerance should be interpreted together with the residual scale and the matrix problem, not as a universal accuracy promise. These distinctions keep complexity statements and numerical claims appropriately local to the run being inspected.

<!-- section: SEC-06 -->
## NumPy input and iteration semantics

NumPy makes the pseudocode concrete. Convert inputs with `np.asarray(..., dtype=float)`, inspect the matrix and vector shapes, use `A @ x` for matrix–vector multiplication, and use `np.linalg.norm` for Euclidean norms. Shape checks and scalar diagnostic checks should raise specific exceptions. A function can return several diagnostics as one tuple, which the caller can unpack.

The implementation below preserves the required input checks, checks breakdown before division, validates positive control parameters, stops on the residual, and otherwise returns the final values at the iteration cap.

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
    if x_norm == 0.0:
        raise ValueError("x0 must be non-zero")
    x = x / x_norm
    eigenvalue = None
    residual_norm = None
    for iteration in range(1, max_iterations + 1):
        y = A @ x
        y_norm = np.linalg.norm(y)
        if y_norm == 0.0:
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

<!-- section: SEC-07 -->
## Spectral explanation and failure modes

In the symmetric eigenbasis, write $x_0=\sum_i c_i v_i$. Repeated multiplication gives

$$A^k x_0=\sum_{i=1}^n c_i\lambda_i^k v_i
=\lambda_1^k\left(c_1v_1+\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^k v_i\right).$$

The dominant projection must be present: $c_1=v_1^Tx_0\ne0$. With $|\lambda_1|>|\lambda_2|$, subordinate ratios have magnitude below one and decay as $|\lambda_i/\lambda_1|^k$. Thus, when $A$ is real symmetric, the dominant magnitude is unique, the initial projection is non-zero, and no iterate produces $Ax_k=0$, direction error generally decreases asymptotically at a rate governed by

$$\left|\frac{\lambda_2}{\lambda_1}\right|^k.$$

This is not an unconditional finite-iteration error bound. If $v_1^Tx_0=0$, exact arithmetic cannot create the missing dominant component, so the method does not converge to $v_1$. If $|\lambda_1|=|\lambda_2|$, a unique eigenvector need not be selected; iterates may stay in or oscillate within the dominant invariant subspace. If the magnitudes are separated but the ratio is close to one, convergence can be very slow. These are different diagnoses: missing projection, tied dominance, and a small spectral gap.

Power iteration can apply to some non-symmetric matrices, but the orthogonal real decomposition used here is not generally available. Defective matrices, complex dominant eigenvalues, and non-normal behaviour require additional care and are outside this lesson's proof scope. Similarly, a simplified spectral computation should not be described as a production ranking system without stating the application-specific assumptions.

<!-- section: SEC-08 -->
## Worked trace and interpretation

For

$$A=\begin{bmatrix}4&1\\1&2\end{bmatrix},\qquad x_0=\begin{bmatrix}1\\1\end{bmatrix},$$

the exact eigenvalues supplied for this example are $3+\sqrt{2}$ and $3-\sqrt{2}$. The example-specific dominant value is $3+\sqrt{2}$, approximately $4.4142$. Running the code should produce an estimate close to that value, a small residual, an approximately unit vector, and an iteration count showing whether the tolerance was reached before the cap.

A useful trace table has one row per iteration and columns for the iteration number, $\|Ax_k\|_2$, the new vector, $\rho_k$, and $\|r_k\|_2$. Check the norm invariant after normalization. Check that the residual is computed from the same vector and estimate that are returned. Check that a sign change is not incorrectly labelled failure. Finally, compare the observed work with the chosen iteration cap and tolerance.

The returned tuple has four roles: estimated eigenvalue, estimated eigenvector, residual norm, and iteration count. No single field is sufficient on its own. An eigenvalue estimate without a residual does not establish an approximate eigenpair; a small residual without assumptions does not prove the expected target was reached; and an iteration count without the stopping reason does not explain the run. Together, the invariant, safeguards, residual, and cap make the algorithm's behaviour inspectable.

That inspection is the bridge between mathematical specification and software testing: each claim about the method has a corresponding value, branch, or invariant that can be checked during execution.

The same discipline prevents a plausible number from being mistaken for a validated result.
It makes numerical claims reproducible and reviewable for review.

For an algorithm trace, ask the same questions at every row: was the matrix product defined, was its norm non-zero, was the new vector normalized, and was the residual computed from that new vector? Then ask whether the loop stopped for the threshold or for the cap. This turns a numerical result into an auditable execution trace rather than a single opaque answer. It also makes the code easier to test with deliberately invalid shapes, a zero initial vector, a breakdown matrix, and a strict tolerance.
