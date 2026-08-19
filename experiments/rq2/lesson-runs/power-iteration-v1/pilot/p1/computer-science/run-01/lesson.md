# Power Iteration: A Traceable Spectral Computation

Power iteration is an iterative algorithm for estimating an eigenpair when repeatedly applying a matrix is more practical than solving a full characteristic equation. This lesson uses a computer-science perspective: the emphasis is on a precise update invariant, the cost of matrix-vector products, defensible stopping criteria, and failure diagnostics. The ranking and spectral-computation examples below are deliberately bounded: a simplified power iteration is not a production ranking system, and any application must state its matrix assumptions.

<!-- section: SEC-01 -->
## Why an eigenpair is an algorithmic target

Let $A\in\mathbb{R}^{n\times n}$. A non-zero vector $v\in\mathbb{R}^n$ is an eigenvector when there is a scalar $\lambda$ such that

$$
Av=\lambda v.
$$

The scalar $\lambda$ is the eigenvalue associated with $v$. The non-zero condition matters: $A0=\lambda0$ holds for every scalar, so the zero vector contains no eigenvalue information. In software terms, an eigenvector is a direction that a matrix maps to the same direction, up to scaling; the eigenvalue records that scaling, including a possible sign reversal.

Eigenvalues can be characterised as roots of

$$
\det(A-\lambda I)=0,
$$

where $I$ is the compatible identity matrix. For a small matrix, this equation can be useful for analysis or checking an implementation. For a large matrix, explicitly forming a characteristic polynomial is usually a poor numerical strategy. Repeated matrix-vector products offer an iterative alternative: they estimate a selected eigenpair without requiring that polynomial to be formed. This is a computational strategy, not an exact algebraic equivalence.

A useful invariant to keep in mind is that the algorithm stores a direction, not an arbitrary scale. That is why the next section's structural assumptions and the normalisation step are central.

<!-- section: SEC-02 -->
## The symmetric setting and the target definition

For a real symmetric matrix, $A=A^T$, the spectral theorem gives an orthonormal basis of real eigenvectors. Writing those eigenvectors as the columns of $Q$ gives

$$
A=Q\Lambda Q^T,
\qquad
\Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n).
$$

Every vector $x$ can then be expressed as

$$
x=\sum_{i=1}^n c_i v_i,
\qquad c_i=v_i^T x.
$$

The coefficient formula is an algorithmically useful projection: it tells us how much of each eigendirection is present in the current vector. The clean orthogonal decomposition in this explanation depends on symmetry; it must not be silently extended to arbitrary non-symmetric matrices.

Order eigenvalues by magnitude:

$$
|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.
$$

The strict first inequality means that $\lambda_1$ is unique in magnitude. “Dominant” therefore means largest absolute value, not largest algebraic value. For example, between eigenvalues $5$ and $-8$, the target by magnitude is $-8$. A program that assumes “largest” means most positive can select the wrong spectral quantity.

<!-- section: SEC-03 -->
## The normalised update

Choose a non-zero initial vector $x_0$. Each power-iteration step first computes a matrix-vector product and then controls its scale:

$$
y_{k+1}=Ax_k,
\qquad
x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.
$$

The denominator must be non-zero. Normalisation changes the magnitude but not the direction of $y_{k+1}$, so it prevents repeated multiplication from overflowing or underflowing while preserving the direction being amplified. In pseudocode:

1. start with a non-zero vector;
2. compute `y = A @ x`;
3. reject the step if `||y||₂ == 0`;
4. replace `x` with `y / ||y||₂`.

After the replacement, the useful invariant is $\|x\|_2=1$. For a dense $n\times n$ matrix, one matrix-vector product costs $O(n^2)$ arithmetic operations and stores $O(n^2)$ matrix entries; a sparse representation can make the product depend instead on the number of stored non-zero entries. The normalisation itself is linear in the vector length.

<!-- section: SEC-04 -->
## Why the direction can converge

In the symmetric eigenbasis, write $x_0=\sum_i c_i v_i$. The unnormalised sequence is

$$
A^k x_0
=\sum_{i=1}^n c_i\lambda_i^k v_i
=\lambda_1^k\left(c_1v_1+
\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^k v_i\right),
$$

where $c_1=v_1^Tx_0$. If $c_1\ne0$ and $|\lambda_1|>|\lambda_2|$, every subordinate ratio has magnitude below one and its $k$th power tends to zero. Normalisation removes the common factor $\lambda_1^k$; it does not remove the relative dominance of the $v_1$ component.

Thus, for a real symmetric matrix, the usual convergence explanation requires all of these conditions: a unique dominant magnitude, a non-zero initial projection onto $v_1$, and no iterate for which $Ax_k=0$. Under those conditions, direction error generally decreases asymptotically at a rate governed by

$$
\left|\frac{\lambda_2}{\lambda_1}\right|^k.
$$

This is an asymptotic rate, not an unconditional finite-iteration error bound. A smaller ratio suggests faster asymptotic alignment; it does not by itself guarantee a particular iteration count for every tolerance.

<!-- section: SEC-05 -->
## Failure modes and scope checks

Several outcomes that look similar in a trace have different meanings. If $\lambda_1<0$, normalised iterates may alternate sign. That is not failure of directional convergence: $v_1$ and $-v_1$ represent the same eigendirection. A stopping rule should therefore not rely only on the raw difference between consecutive vectors.

If $v_1^Tx_0=0$, the initial vector has no dominant component. In exact arithmetic, multiplication by $A$ cannot create that missing eigencomponent, so the iterates do not converge to $v_1$. This is not ordinary slow convergence. It is a projection failure, and changing the initial vector is the relevant remedy.

If $|\lambda_1|=|\lambda_2|$, a unique eigenvector need not be selected; the iterates may remain in or oscillate within the associated dominant invariant subspace. If the magnitudes are separated but $|\lambda_2/\lambda_1|$ is close to one, convergence can instead be very slow. Repeated dominance and a small spectral gap must not be conflated.

The method targets largest magnitude, not necessarily the most positive eigenvalue. Also, although power iteration can apply to some non-symmetric matrices, the real orthogonal decomposition used here is not generally available. Defective matrices, complex dominant eigenvalues, and non-normal behaviour require additional care and are outside this lesson's convergence result.

<!-- section: SEC-06 -->
## Estimating the eigenvalue and deciding when to stop

Once $x_k$ is an approximate eigenvector, use the Rayleigh quotient

$$
\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.
$$

If $x_k$ has unit norm, then $x_k^Tx_k=1$ and this simplifies to

$$
\rho(x_k)=x_k^TAx_k.
$$

For symmetric $A$, as $x_k$ approaches $v_1$, the estimate approaches $\lambda_1$. The denominator must still be retained for an unnormalised vector.

A stronger computational diagnostic is the eigenpair residual:

$$
r_k=Ax_k-\rho(x_k)x_k,
\qquad \|r_k\|_2.
$$

An exact eigenpair has zero residual. A residual threshold is preferable to only comparing successive vectors because a sign flip can make two equally valid representatives look far apart. A practical stopping decision is to stop when $\|r_k\|_2\le\varepsilon$, while also retaining a maximum iteration limit so a slow or unsuitable case cannot run indefinitely.

<!-- section: SEC-07 -->
## An implementation with explicit invariants

The following implementation makes input and control-flow assumptions visible. It converts inputs to floating NumPy arrays, checks that $A$ is square and that $x_0$ has compatible one-dimensional shape, rejects a zero initial vector, validates the positive tolerance and iteration cap, checks for breakdown before division, and returns four values: estimate, vector, residual norm, and iteration count.

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
```

The ordering is intentional: shape and initial-vector checks precede iteration; the zero-product check precedes division; the residual test precedes the fallback return. The maximum iteration count is an operational safeguard, not evidence that the desired eigenpair has been reached.

<!-- section: SEC-08 -->
## Worked consolidation and trace

Consider

$$
A=\begin{bmatrix}4&1\\1&2\end{bmatrix},
\qquad x_0=\begin{bmatrix}1\\1\end{bmatrix}.
$$

This matrix is real and symmetric. Its exact eigenvalues are $3+\sqrt{2}$ and $3-\sqrt{2}$, so the dominant value by magnitude is $3+\sqrt{2}\approx4.4142$. The initial vector is non-zero and has a non-zero projection onto the dominant eigendirection. The following self-contained run traces the matrix-vector update, the Rayleigh estimate, and the residual-based decision.

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
        residual_norm = float(np.linalg.norm(A @ x - eigenvalue * x))
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

Read the output as a contract between mathematics and implementation: the estimate should be close to $3+\sqrt{2}$, the residual should be small, and the vector may have either sign. A negative of the reported eigenvector represents the same eigendirection. For a final self-check, explain why normalisation preserves direction, identify which assumption would fail when the dominant projection is zero, and state why a residual threshold is more reliable than raw vector difference when signs can alternate.

For an implementation trace, separate three quantities that are often mixed together. The matrix-vector product supplies the next direction, the norm removes its scale, and the spectral ratio explains why the direction can become more informative over time. The quotient and residual are diagnostics computed after the direction has been normalised. This separation is useful when debugging: a bad product, a zero norm, and a slow spectral gap are different causes even if all three lead to a long run.

The phrase “dominant component survives” is conditional. It means that the initial coefficient $c_1$ is non-zero and that the dominant magnitude is strictly separated. It does not mean that every initial vector converges, nor that a fixed number of updates gives a specified error. A computational report should therefore record the starting vector, tolerance, iteration cap, and observed residual rather than reporting only an eigenvalue.

These distinctions matter in a computer-science pipeline. A ranking-style toy matrix might be interpreted as describing influence between a few states, but that interpretation is valid only after its construction, signs, symmetry assumptions, and intended output have been specified. Power iteration returns a spectral direction under the stated numerical conditions; it does not automatically establish that the direction is a useful ranking, that entries have a causal meaning, or that the method replaces a production solver. Treat the application story as a bounded interpretation layered on top of the algorithm, not as an extra convergence theorem.

When diagnosing a run, ask the following questions in order: Is the input valid? Did a matrix-vector product become zero? Is the dominant projection absent? Are the two leading magnitudes tied or nearly tied? Is the matrix outside the symmetric setting used by this explanation? This checklist preserves the difference between a programming error, a mathematical failure condition, and a limitation of the theorem's scope.

For a code review, the residual is a meaningful certificate of the computed pair, but it is not a universal certificate of application quality. A small value says that the returned vector approximately satisfies $Ax\approx\rho(x)x$ for the computed matrix. It does not say that the matrix was modelled appropriately or that a non-symmetric use case inherits the symmetric convergence explanation. The iteration cap has the complementary role of making non-convergence observable: reaching $K$ should be reported as the final state, not silently labelled success.

One useful exercise is to compare two stopping policies on paper. A raw vector-difference test can report apparent movement when the sign alternates, while the residual can remain small because both signs encode the same eigendirection. Conversely, a residual that remains above tolerance asks for more computation or a diagnosis of the assumptions; it should not be hidden by a visually stable-looking plot. In production-quality code, log both the stopping reason and the final residual.

Notice also what the function does not infer. It does not test that the matrix is symmetric, so callers must not claim that the theorem has been verified merely because this function runs. It does not promise that the returned estimate is the most positive eigenvalue. It returns the best state reached under its update and stopping policy, together with enough information for a caller to inspect that state. The explicit checks for positive tolerance and positive iteration count avoid the unbound-result problem that would occur if the loop had no iterations.

For complexity reasoning, let $K$ be the number of performed iterations. A dense run uses approximately $K$ matrix-vector products, so its dominant arithmetic cost is $O(Kn^2)$; vector norms and inner products add lower-order $O(Kn)$ work. With a sparse matrix, the product cost can instead be described using the number of stored non-zero entries. These are operation-count statements, not convergence guarantees: the required $K$ depends on the spectral ratio, the initial projection, the tolerance, and whether the assumptions are satisfied.

To make the worked trace reproducible, compute the first update manually before trusting the loop. The initial vector has norm $\sqrt{2}$, so the normalised starting direction is $(1,1)^T/\sqrt{2}$. Multiplication gives a vector proportional to $(5,3)^T$, which is then normalised. The next Rayleigh estimate is formed from that unit vector, and the residual measures how far the matrix image is from being a scalar multiple of it. Repeating this process favours the eigendirection associated with $3+\sqrt{2}$ because its magnitude exceeds that of $3-\sqrt{2}$.

The result also illustrates why a worked numerical value should be tied to a stated input. If the initial vector were changed to one with zero dominant projection in a diagonal example, the same loop would still execute, but its iterates would remain in the non-dominant invariant subspace. If the leading magnitudes were equal, a small residual could describe a vector in a dominant subspace without identifying one unique eigenvector. The algorithm and the interpretation must therefore be read together.

Before using this pattern in another spectral-computation task, record the matrix class being assumed, the intended meaning of “dominant,” the initial vector, the tolerance, the iteration cap, the stopping reason, and the final residual. That record makes the implementation traceable and prevents an approximate eigenpair from being presented as more than the computation supports.
