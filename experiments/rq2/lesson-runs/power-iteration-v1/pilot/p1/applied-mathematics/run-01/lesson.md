# Power Iteration: Structure, Convergence, and Reliable Computation

Power iteration is an iterative method for approximating an eigenpair without explicitly forming a characteristic polynomial. This lesson develops the method from the eigenvalue equation, explains its convergence through a spectral decomposition, identifies cases in which its assumptions fail, and ends with a guarded NumPy implementation and a worked calculation. The emphasis is on the mathematical structure: computation is useful because it reflects the decomposition, not because iteration automatically guarantees an answer.

<!-- section: SEC-01 -->
## Eigenpairs and the numerical motivation

Let $A\in\mathbb{R}^{n\times n}$. A non-zero vector $v\in\mathbb{R}^n$ is an eigenvector of $A$ if there is a scalar $\lambda$ such that

$$
Av=\lambda v.
$$

The scalar $\lambda$ is the eigenvalue associated with $v$. The condition $v\ne0$ matters: substituting the zero vector gives $A0=\lambda0$ for every scalar, so the equation would contain no information with which to identify an eigenvalue. Eigenvectors are directions whose image under the matrix is a rescaling of the same direction; the rescaling factor is the eigenvalue.

For a finite matrix, eigenvalues can be characterised by the characteristic equation

$$
\det(A-\lambda I)=0,
$$

where $I$ is the identity matrix of compatible dimension. This is an important algebraic characterisation, but explicitly forming a characteristic polynomial is usually a poor numerical strategy for large matrices. Power iteration instead uses repeated matrix-vector products to estimate a selected eigenpair. That is a numerical strategy, not an exact algebraic equivalence between the two procedures.

The standard method targets the eigenvalue of largest magnitude. For example, if the relevant eigenvalues are $5$ and $-8$, then $-8$ is dominant for power iteration because $|-8|>|5|$; it is not the most positive eigenvalue.

<!-- section: SEC-02 -->
## The symmetric spectral setting

The cleanest analysis assumes that $A=A^T$ is real and symmetric. The spectral theorem then supplies an orthonormal basis of real eigenvectors. If the eigenvectors are the columns of $Q$, then

$$
A=Q\Lambda Q^T,
\qquad
\Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n).
$$

Every vector $x$ can be resolved into this eigenvector basis:

$$
x=\sum_{i=1}^n c_i v_i,
\qquad c_i=v_i^T x.
$$

The coefficient formula depends on orthonormality. It says that $c_i$ measures the component of $x$ in the direction $v_i$. In this lesson, order eigenvalues by magnitude:

$$
|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.
$$

Thus $\lambda_1$ is unique in magnitude, and $v_1$ is the dominant eigendirection. The strict first inequality is not a cosmetic convention: it creates a spectral gap on which the usual convergence explanation depends. The orthogonal real decomposition above is a symmetric-matrix result and should not be silently extended to arbitrary non-symmetric matrices.

<!-- section: SEC-03 -->
## The normalized power update

Choose a non-zero initial vector $x_0$. One power step first multiplies by the matrix and then removes the changing scale:

$$
y_{k+1}=Ax_k,
\qquad
x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.
$$

The denominator must be non-zero. Normalisation gives the new iterate unit Euclidean norm and controls its size; it does not change the direction of $y_{k+1}$, apart from the harmless choice of sign. In practice, one should check for a zero norm before dividing.

To see the mechanism, start with the eigenbasis expansion $x_0=\sum_i c_i v_i$. Repeated multiplication gives

$$
A^k x_0
=\sum_{i=1}^n c_i\lambda_i^k v_i
=\lambda_1^k\left(c_1v_1+
\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^k v_i\right).
$$

The dominant projection is

$$
c_1=v_1^Tx_0.
$$

If $c_1\ne0$, the expression contains a dominant component. If the strict magnitude gap holds, each subordinate ratio satisfies

$$
\left|\frac{\lambda_i}{\lambda_1}\right|^k\longrightarrow0
\quad\text{as }k\text{ increases}.
$$

The common factor $\lambda_1^k$ can become very large or very small, which is why normalisation is computationally essential. After normalisation, the remaining direction is increasingly governed by $v_1$, subject to the assumptions just stated.

<!-- section: SEC-04 -->
## Convergence and what the rate means

For a real symmetric matrix, the usual directional convergence statement requires all of the following: $|\lambda_1|>|\lambda_2|$; the initial vector has non-zero projection onto $v_1$; and no iterate produces $Ax_k=0$. Under these conditions, direction error generally decreases asymptotically at a rate governed by

$$
\left|\frac{\lambda_2}{\lambda_1}\right|^k.
$$

This is an asymptotic rate, not an unconditional finite-iteration error bound. A smaller ratio indicates faster asymptotic suppression of subordinate components. A ratio close to one indicates slow progress, even though the dominant magnitude is still unique.

The sign of the dominant eigenvalue also matters for interpretation. If $\lambda_1<0$, successive normalised iterates may alternate sign. This does not by itself indicate failure: $v_1$ and $-v_1$ represent the same eigendirection. A comparison that treats opposite signs as completely different vectors can therefore report apparent oscillation where the direction is actually becoming accurate.

<!-- section: SEC-05 -->
## Failure modes and scope boundaries

The assumptions distinguish several different phenomena. First, if $v_1^Tx_0=0$, the initial vector has no component in the dominant eigendirection. In the symmetric eigenbasis and exact arithmetic, matrix multiplication cannot create that missing component. The iterates remain in the relevant non-dominant invariant subspace, so this is not merely slow convergence to $v_1$.

Second, if $|\lambda_1|=|\lambda_2|$, power iteration need not select a unique eigenvector. The iterates may remain in, or oscillate within, the invariant subspace associated with the dominant magnitudes. This is different from the separated case in which $|\lambda_2/\lambda_1|$ is close to one: there the target direction is unique in magnitude, but convergence can be very slow.

Finally, the symmetric setting is a deliberate scope boundary. Power iteration can apply to some non-symmetric matrices, but the clean orthogonal decomposition used here is not generally available. Defective matrices, complex dominant eigenvalues, and non-normal behaviour require additional care and are outside this lesson's convergence explanation. Do not use the symmetric proof as an unconditional theorem for all matrices.

<!-- section: SEC-06 -->
## Rayleigh estimates and a residual stopping test

Once a non-zero approximate eigenvector $x_k$ is available, estimate its eigenvalue with the Rayleigh quotient

$$
\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.
$$

Power iteration normally keeps $x_k$ normalised, so $x_k^Tx_k=1$ and the quotient simplifies to

$$
\rho(x_k)=x_k^TAx_k.
$$

The simplification must not be used for an unnormalised vector without the denominator. For symmetric $A$, if $x_k$ approaches $v_1$, then $\rho(x_k)$ approaches $\lambda_1$.

A more direct quality measure is the eigenpair residual

$$
r_k=Ax_k-\rho(x_k)x_k.
$$

An exact eigenpair has zero residual. Therefore $\|r_k\|_2$ is a meaningful computational stopping measure: stop when it is at most a chosen positive tolerance $\varepsilon$. Comparing only successive vectors is less reliable because sign flips can make two vectors look far apart even when they describe the same eigendirection.

<!-- section: SEC-07 -->
## A guarded algorithm and implementation

Given $A$, a non-zero $x_0$, tolerance $\varepsilon>0$, and a positive maximum iteration count $K$, the algorithm is: normalise $x_0$; compute $y=Ax_k$; check whether $\|y\|_2=0$ before division; set $x_{k+1}=y/\|y\|_2$; compute the Rayleigh estimate and residual; stop if the residual norm is at most $\varepsilon$; otherwise continue until $K$ iterations have been performed. The implementation below also validates the input shape, rejects a zero initial vector, and rejects invalid iteration controls before entering the loop.

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
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")
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

The breakdown check must precede division. The residual stop is checked after the new iterate and estimate are formed, while the iteration cap provides a defined return even when the requested tolerance is not reached. The returned values are the estimate, the final unit vector, the residual norm, and the iteration count.

<!-- section: SEC-08 -->
## Worked consolidation

Consider

$$
A=\begin{bmatrix}4&1\\1&2\end{bmatrix},
\qquad x_0=\begin{bmatrix}1\\1\end{bmatrix}.
$$

This matrix is real and symmetric. Its exact eigenvalues are

$$
3+\sqrt{2}
\quad\text{and}\quad
3-\sqrt{2}.
$$

The first is dominant by magnitude because both are positive and $3+\sqrt2>3-\sqrt2$. The initial vector is non-zero, and the implementation repeatedly multiplies, normalises, estimates the eigenvalue, and measures the residual. Running the following self-contained experiment should produce an estimate close to $3+\sqrt2$, a unit eigenvector up to sign, a small residual, and an iteration count no greater than the maximum.

```python
import numpy as np


def power_iteration(A, x0, tolerance=1e-10, max_iterations=1000):
    A = np.asarray(A, dtype=float)
    x = np.asarray(x0, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("A must be square")
    if x.shape != (A.shape[0],):
        raise ValueError("x0 has incompatible dimensions")
    if tolerance <= 0 or max_iterations <= 0:
        raise ValueError("tolerance and max_iterations must be positive")
    norm = np.linalg.norm(x)
    if norm == 0:
        raise ValueError("x0 must be non-zero")
    x = x / norm
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
result = power_iteration(A, np.array([1.0, 1.0]))
print("Estimated dominant eigenvalue:", result[0])
print("Estimated eigenvector:", result[1])
print("Residual norm:", result[2])
print("Iterations:", result[3])
print("Exact dominant eigenvalue:", 3 + np.sqrt(2))
```

When interpreting the output, compare the eigenvalue estimate with $3+\sqrt2$ and inspect the residual rather than demanding a particular eigenvector sign. The complete reasoning is conditional: the algorithm traces the dominant eigendirection when the required spectral gap, initial projection, and non-breakdown assumptions hold; the residual tells us how well the returned pair satisfies the eigenpair equation for the computed matrix.

There are several useful checks to perform by hand before trusting this run. The matrix is symmetric, so the orthogonal spectral framework applies. Its two eigenvalues have different magnitudes, so the dominant magnitude is unique. The starting vector is not zero, but non-zero norm alone is not the same statement as a non-zero dominant projection; the latter is the condition used in the convergence argument. In this particular two-dimensional example, the supplied start is not aligned with a missing dominant component, and the numerical run can therefore reveal the expected dominant direction.

The first update also illustrates the algorithm concretely. The unnormalised product is

$$
Ax_0=\begin{bmatrix}5\\3\end{bmatrix},
$$

and the next iterate is $(5,3)^T/\sqrt{34}$. The vector has unit 2-norm, while its direction is unchanged by the positive rescaling. Subsequent products repeatedly amplify the component associated with $3+\sqrt2$ relative to the component associated with $3-\sqrt2$. The Rayleigh estimate uses the current normalised vector, and the residual tests the remaining defect directly.

As a final self-check, explain each of these cases without changing the method's target. If the dominant eigenvalue is negative, alternating signs can still represent improving alignment. If the dominant projection is exactly zero, exact iteration cannot manufacture it. If the two largest magnitudes tie, a unique target direction is not guaranteed. If the ratio is separated but close to one, the issue is slow convergence rather than non-unique dominance. These distinctions connect the algebraic assumptions, the observed iterates, and the implementation diagnostics.

A useful reporting habit is to record the matrix, initial vector, tolerance, iteration cap, estimate, residual norm, and stopping reason together. An estimate by itself does not say whether the computation met its requested accuracy. Conversely, a small residual certifies closeness to the eigenpair equation for the returned estimate and vector, but it does not remove the need to understand which eigenvalue the method can target. The spectral assumptions explain that interpretation. They are part of the numerical result, not merely background theory.

This separation between identity, direction, and accuracy is central: the eigenvalue is a scalar, the eigenvector is defined only up to non-zero scaling, and the residual evaluates their combined equation directly.
