# Power iteration: finding a dominant eigendirection

Power iteration is a deliberately simple way to estimate one eigenpair using repeated matrix-vector multiplication. For a mechanical-engineering learner, an idealized mode shape is a useful picture for an eigenvector: the vector describes a direction or pattern, while its overall scale is secondary. That picture is only a pedagogical bridge. It does not mean that every engineering eigenproblem is symmetric or that basic power iteration is the right solver for every modal-analysis problem.

<!-- section: SEC-01 -->
## Eigenpairs and why an iterative method is useful

Let $A\in\mathbb{R}^{n\times n}$. A non-zero vector $v\in\mathbb{R}^n$ is an eigenvector of $A$ when a scalar $\lambda$ exists such that

$$
Av=\lambda v.
$$

The scalar $\lambda$ is the eigenvalue associated with $v$. Requiring $v\ne0$ is essential: $A0=\lambda0$ holds for every scalar, so the zero vector carries no information about a particular eigenvalue.

Eigenvalues are roots of the characteristic equation

$$
\det(A-\lambda I)=0,
$$

where $I$ has the same dimension as $A$. This equation is useful conceptually and for small hand calculations. For a large matrix, however, explicitly forming the characteristic polynomial is usually a poor numerical strategy. Iterative methods instead use matrix-vector products to estimate selected eigenpairs; power iteration targets an eigenvalue of largest **magnitude**. It does not necessarily target the most positive eigenvalue. If two eigenvalues are $5$ and $-8$, then $-8$ is dominant because $|-8|>|5|$.

In an idealized modal picture, you can therefore think of the calculation as repeatedly updating a candidate shape while asking which eigendirection becomes most prominent. Keep the magnitude rule in view: “dominant” always refers to absolute value here.

<!-- section: SEC-02 -->
## The real symmetric setting

The clean convergence explanation begins with a real symmetric matrix, $A=A^T$. The spectral theorem then gives an orthonormal basis of real eigenvectors $v_1,\ldots,v_n$. If these eigenvectors are the columns of the orthogonal matrix $Q$, then

$$
A=Q\Lambda Q^T,
\qquad
\Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n).
$$

Consequently, any vector $x$ can be resolved into eigenvector components:

$$
x=\sum_{i=1}^n c_i v_i,
\qquad c_i=v_i^Tx.
$$

This resembles resolving a displacement into idealized modal directions: the coefficients say how much of each direction is present. The mathematical statement depends on the real-symmetric hypothesis and the orthonormal basis; it is not a general decomposition for every matrix arising in engineering.

Order the eigenvalues by magnitude:

$$
|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.
$$

The strict first inequality matters. It says that $\lambda_1$ has a unique dominant magnitude. Replacing it with a non-strict comparison would remove the assumption that lets the iteration select one dominant eigendirection.

<!-- section: SEC-03 -->
## The normalized power update

Choose a non-zero initial vector $x_0$. One power step is

$$
y_{k+1}=Ax_k,
\qquad
x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.
$$

The denominator must be non-zero. Multiplication by $A$ changes the relative eigenvector components; normalization then controls the scale without changing the direction of $y_{k+1}$. Thus every accepted iterate has unit 2-norm. In a mode-shape representation, this is convenient because multiplying a shape vector by a non-zero scalar does not create a new direction.

To trace a step by hand, first compute every entry of $y_{k+1}=Ax_k$, then calculate $\|y_{k+1}\|_2$, and only then divide. Do not normalize before checking for a zero norm. That ordering is both mathematically necessary and important in code.

A useful bookkeeping habit is to keep the intermediate vector $y_{k+1}$ visible rather than trying to combine multiplication and normalization mentally. Check its dimension, square and add its components to obtain the 2-norm, and verify that the normalized result has norm one. The entries of $x_{k+1}$ will usually differ from those of $y_{k+1}$, but their component ratios describe the same direction. This separates the part of the step that changes direction from the part that merely resets scale.

<!-- section: SEC-04 -->
## Why a dominant component emerges

In the real symmetric eigenbasis, write $x_0=\sum_i c_i v_i$. Before normalization, repeated multiplication gives

$$
A^k x_0
=\sum_{i=1}^n c_i\lambda_i^k v_i
=\lambda_1^k\left(c_1v_1+
\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^k v_i\right).
$$

This factorization exposes the mechanism. If $c_1=v_1^Tx_0\ne0$ and $|\lambda_1|>|\lambda_2|$, every subordinate ratio has magnitude below one, so its relative contribution decays as $k$ grows. Normalization prevents the common factor $\lambda_1^k$ from simply making the vector very large or very small.

The complete convergence statement needs its assumptions kept together. For a real symmetric $A$, suppose the dominant magnitude is unique, the initial vector has non-zero projection onto $v_1$, and no iterate produces $Ax_k=0$. Then the direction error generally decreases asymptotically at a rate governed by

$$
\left|\frac{\lambda_2}{\lambda_1}\right|^k.
$$

This is an asymptotic rate description, not an unconditional error bound for a particular finite iteration. It also suggests a comparison: a smaller magnitude ratio gives faster asymptotic separation, whereas a ratio near one gives slow separation.

Notice what normalization does not change in this argument. The unnormalized expression makes relative component growth easy to see; dividing by a norm removes a common scale but leaves those relative weights to determine the direction. The dominant term is not appearing from nowhere. It must already be present through $c_1\ne0$, and it becomes prominent only relative to subordinate terms whose ratios decay. When explaining convergence, name the symmetric setting, strict magnitude gap, non-zero dominant projection, and absence of a zero product before giving the rate. This keeps the mechanism and its conditions connected.

<!-- section: SEC-05 -->
## Failure modes and limits of the picture

Several cases must be distinguished rather than labelled collectively as “non-convergence.”

First, if $\lambda_1<0$, successive normalized iterates may alternate sign. This alone is not failure: $v_1$ and $-v_1$ are the same eigendirection. Comparing $x_{k+1}$ directly with $x_k$ can therefore make good directional convergence look poor.

Second, if $v_1^Tx_0=0$, the initial vector contains no dominant component. In exact arithmetic, repeated multiplication cannot create that missing eigencomponent, so the method will not converge to $v_1$. This is different from starting with a small but non-zero dominant component, which may merely delay its emergence.

Third, if $|\lambda_1|=|\lambda_2|$, the method need not select a unique eigenvector. It may remain in, or oscillate within, the invariant subspace associated with the tied dominant magnitudes. By contrast, when $|\lambda_2/\lambda_1|$ is below but close to one, dominance is unique but convergence can be very slow.

Finally, power iteration can be applied to some non-symmetric matrices, but the clean orthogonal decomposition above is not generally available. Defective matrices, complex dominant eigenvalues, and non-normal behavior require additional care and are outside this lesson. This boundary is especially important when transferring the idealized modal analogy to an actual engineering model.

You can diagnose an observed run by asking separate questions. Are alternate signs the only change? Then compare directions modulo sign. Was the dominant projection absent from the starting vector? Then exact iteration cannot recover it. Are the two largest magnitudes tied? Then a unique target direction is not assured. Are they distinct but close? Then slow progress is consistent with the asymptotic ratio. These questions prevent four mathematically different situations from being treated as one generic failure.

<!-- section: SEC-06 -->
## Estimating the eigenvalue and measuring quality

Once $x_k\ne0$ is available, estimate its eigenvalue with the Rayleigh quotient

$$
\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.
$$

For a normalized iterate, $x_k^Tx_k=1$, so this simplifies to

$$
\rho(x_k)=x_k^TAx_k.
$$

For symmetric $A$, if $x_k$ approaches the eigenvector $v_1$, then $\rho(x_k)$ approaches $\lambda_1$. The quotient supplies an estimate, but an estimated value alone does not show how closely the pair satisfies the eigenvalue equation. For that, form the residual

$$
r_k=Ax_k-\rho(x_k)x_k.
$$

An exact eigenpair has zero residual. The quantity $\|r_k\|_2$ is therefore a meaningful computational stopping measure: it directly measures the mismatch in the eigenvalue equation. A residual tolerance is preferable to relying only on $\|x_{k+1}-x_k\|_2$, because a negative dominant eigenvalue can cause sign flips even while the eigendirection improves. In numerical work, report the Rayleigh estimate and residual norm together so that the approximation and its equation mismatch can be interpreted together.

The order of this quality check is worth rehearsing. Begin with the non-zero candidate vector. Form its Rayleigh quotient, retaining the denominator unless the vector is known to have unit norm. Use that same quotient in the residual rather than mixing estimates from different iterates. Finally, take the residual's 2-norm and compare it with the chosen positive tolerance. If the threshold is satisfied, the algorithm has a clear equation-based reason to stop. If not, another power update may be performed, subject to the iteration cap and breakdown check.

<!-- section: SEC-07 -->
## A safeguarded algorithm and worked calculation

The full algorithm starts with a matrix $A$, non-zero $x_0$, tolerance $\varepsilon>0$, and positive maximum iteration count $K$. Normalize $x_0$. At each iteration, compute $y=Ax_k$ and test for zero norm before division. Normalize to obtain $x_{k+1}$, compute its Rayleigh estimate and residual, and return when the residual norm is at most $\varepsilon$. If that never happens, return the final values after exactly $K$ iterations.

The implementation below converts the inputs to floating NumPy arrays. It checks that $A$ is square, that $x_0$ is a compatible one-dimensional vector, and that $x_0$ is non-zero. It also rejects a non-positive tolerance or a maximum iteration count that is not a positive integer. Each successful return is a four-value tuple containing the eigenvalue estimate, eigenvector estimate, residual norm, and iteration count.

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
            raise RuntimeError(
                "power iteration broke down because A @ x is zero"
            )

        x = y / y_norm
        eigenvalue = float(x @ (A @ x))
        residual = A @ x - eigenvalue * x
        residual_norm = float(np.linalg.norm(residual))

        if residual_norm <= tolerance:
            return eigenvalue, x, residual_norm, iteration

    return eigenvalue, x, residual_norm, max_iterations

A = np.array([[4.0, 1.0],
              [1.0, 2.0]])

eigenvalue, eigenvector, residual, iterations = power_iteration(
    A, np.array([1.0, 1.0])
)

print("Estimated dominant eigenvalue:", eigenvalue)
print("Estimated eigenvector:", eigenvector)
print("Residual norm:", residual)
print("Iterations:", iterations)
```

For this symmetric matrix, the exact eigenvalues are

$$
3+\sqrt{2}
\quad\text{and}\quad
3-\sqrt{2}.
$$

The first has the larger magnitude, so the printed estimate should be close to $3+\sqrt{2}\approx4.4142$, with a small residual norm. The estimated eigenvector may appear with either sign; both signs describe the same eigendirection. As a final reading exercise, connect the output to the theory: the eigenvalue line gives the Rayleigh estimate, the vector gives the normalized candidate direction, the residual quantifies equation mismatch, and the iteration count tells you whether the tolerance was reached before the cap.

You can also trace the beginning of this run without relying on the final output. With $x_0=(1,1)^T$, normalization first gives $(1,1)^T/\sqrt{2}$. Multiplication by the displayed matrix then produces a vector proportional to $(5,3)^T$; its normalized direction is $(5,3)^T/\sqrt{34}$. This first update has not solved the whole problem, but it exhibits the exact multiply-check-normalize sequence used in every iteration. The implementation then forms the Rayleigh estimate and residual for that normalized direction before deciding whether to stop.

When reading the function, test its control flow against three possibilities. A regular run either returns early because the residual norm reaches tolerance or returns the last four values after the iteration cap. A zero matrix-vector product instead raises the breakdown error before division. Invalid shapes, a zero initial vector, a non-positive tolerance, or an invalid cap are rejected before iteration. These outcomes make the returned iteration count and residual interpretable rather than leaving an ambiguous partial result.
