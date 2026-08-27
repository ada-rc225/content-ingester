# Power iteration: finding a dominant mode step by step

This lesson develops power iteration as a matrix-vector process, explains when it converges, and turns the mathematics into a guarded NumPy implementation. An idealized modal interpretation will help connect the vectors to mode shapes, but it is only a pedagogical bridge: not every engineering eigenproblem is symmetric or appropriately solved by basic power iteration.

<!-- section: SEC-01 -->
## Eigenpairs and why an iterative method is useful

For a real square matrix $A\in\mathbb{R}^{n\times n}$, a vector $v\ne 0$ is an eigenvector if there is a scalar $\lambda$ such that

$$
Av=\lambda v.
$$

The scalar $\lambda$ is the eigenvalue associated with $v$. The condition $v\ne0$ matters: the zero vector satisfies $A0=\lambda0$ for every scalar, so it carries no information about a particular eigenvalue.

In an idealized modal model, an eigenvector can be viewed as a mode-shape direction and its eigenvalue as the associated scalar from the model. This analogy concerns the algebraic eigenproblem only; it does not assert that every physical modal problem has the same matrix properties.

Eigenvalues are roots of the characteristic equation

$$
\det(A-\lambda I)=0,
$$

where $I$ is the identity matrix of compatible size. For small matrices this equation is useful for analysis. For large matrices, explicitly forming the characteristic polynomial is usually a poor numerical strategy. Iterative methods instead use repeated matrix-vector products to estimate selected eigenpairs.

Power iteration seeks the eigenvalue of largest **magnitude**, not necessarily the most positive eigenvalue. If two eigenvalues are $5$ and $-8$, then $-8$ is dominant because $|-8|>|5|$. That distinction will matter both for convergence and for the signs of successive vectors.

It helps to separate the problem being solved from the strategy used to solve it. The eigen-equation defines the desired pair, while power iteration is a numerical route toward one particular pair. Repeated matrix-vector products avoid constructing a full characteristic polynomial, but they do not redefine an eigenvalue. Before moving on, check that you can explain why a zero vector is excluded, identify which member of the pair is a vector and which is a scalar, and compare candidate eigenvalues by absolute value. These small distinctions prevent three common errors from being carried into the iteration.

<!-- section: SEC-02 -->
## The real symmetric setting

The cleanest explanation begins with a real symmetric matrix, $A=A^T$. The spectral theorem then gives an orthonormal basis of real eigenvectors. Placing those eigenvectors in the columns of an orthogonal matrix $Q$ gives

$$
A=Q\Lambda Q^T,
\qquad
\Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n).
$$

Because the eigenvectors $v_1,\ldots,v_n$ are an orthonormal basis, every vector $x$ has the expansion

$$
x=\sum_{i=1}^n c_i v_i,
\qquad c_i=v_i^Tx.
$$

This decomposition lets us track separately how a matrix-vector multiplication changes every eigendirection. Order the eigenvalues by magnitude:

$$
|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.
$$

The strict first inequality says that $\lambda_1$ is unique in magnitude. Throughout the convergence argument, “dominant” means largest absolute value, not largest algebraic value.

The orthonormal expansion is useful because the coefficients are obtained directly by projection. For a given starting vector, $c_i=v_i^Tx$ measures its component along the corresponding eigenvector. You can therefore picture the starting vector as a mixture of mode-shape directions, each with its own coefficient. This picture is exact for the stated real symmetric setting. The strict gap in the magnitude ordering is a separate assumption: symmetry supplies the orthonormal basis, while the gap makes one magnitude uniquely dominant. Keeping those roles separate will make the convergence argument easier to audit.

<!-- section: SEC-03 -->
## The normalized matrix-vector update

Choose a nonzero initial vector $x_0$. One power-iteration step computes

$$
y_{k+1}=Ax_k,
\qquad
x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.
$$

This step requires $\|y_{k+1}\|_2\ne0$. Normalization controls the scale and makes $x_{k+1}$ a unit vector; multiplying by the positive scalar $1/\|y_{k+1}\|_2$ does not change the direction of $y_{k+1}$. In mode-shape language, the iteration repeatedly applies the matrix and then removes an arbitrary amplitude so that directions can be compared.

As a quick trace, start with any nonzero $x_k$, form the matrix-vector product, calculate its Euclidean norm, and divide each component by that same norm. Checking the denominator before dividing is part of the algorithm, not an optional numerical detail.

After division, verify two properties. First, the new vector has Euclidean norm one. Second, it is a scalar rescaling of the matrix-vector product, so it points in the same direction. The normalization does not itself decide which eigendirection wins; that comes from repeated multiplication and the relative eigenvalue magnitudes. It simply prevents the scale from growing or shrinking unchecked and gives every step a consistent representation. If the product is zero, neither of these checks can be completed, which is why the algorithm must report breakdown before attempting the division.

<!-- section: SEC-04 -->
## Why the dominant component emerges

Suppose the symmetric-basis assumptions above hold and expand $x_0=\sum_i c_i v_i$. Before normalization, repeated multiplication gives

$$
A^k x_0
=\sum_{i=1}^n c_i\lambda_i^k v_i
=\lambda_1^k\left(c_1v_1+
\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^k v_i\right).
$$

The coefficient of the dominant direction must be present initially:

$$
c_1=v_1^Tx_0\ne0.
$$

When $|\lambda_1|>|\lambda_2|$, each subordinate ratio has magnitude below one, so terms containing $|\lambda_i/\lambda_1|^k$ decay relative to the dominant term. Normalization removes the common growth or decay represented by $\lambda_1^k$, leaving a direction that approaches the line spanned by $v_1$.

More precisely, for a real symmetric matrix, direction convergence requires a unique dominant magnitude, a nonzero initial projection onto $v_1$, and no iterate for which $Ax_k=0$. Under those conditions, the direction error generally decreases asymptotically at a rate governed by

$$
\left|\frac{\lambda_2}{\lambda_1}\right|^k.
$$

This is an asymptotic rate, not an unconditional finite-iteration error bound. A smaller magnitude ratio usually produces faster eventual convergence; a ratio near one predicts slow separation of the two leading components.

To read the factored expression, focus on relative rather than absolute scale. The dominant coefficient remains inside the parentheses, while every subordinate coefficient is multiplied by a power of an eigenvalue ratio. For example, powers of a ratio with magnitude well below one decay much more quickly than powers of a ratio close to one. This comparison explains the qualitative rate without promising an exact error after a particular number of steps. It also shows why the nonzero projection and strict gap must be stated next to the convergence claim: without the former there is no dominant term to preserve, and without the latter at least one competing ratio does not decay in magnitude.

<!-- section: SEC-05 -->
## Failure modes and boundaries of the argument

Several different behaviours must be distinguished.

If $\lambda_1<0$, successive normalized iterates may alternate sign. This alone is not failure: $v_1$ and $-v_1$ represent the same eigendirection. A comparison based only on $\|x_{k+1}-x_k\|_2$ can therefore look poor even while directional alignment improves.

If $v_1^Tx_0=0$, the initial vector has no dominant component. In exact arithmetic, repeated multiplication cannot create that missing component, so the method does not converge to $v_1$. This is not merely slow convergence; the iterates remain in a non-dominant invariant subspace.

If $|\lambda_1|=|\lambda_2|$, there is no unique dominant magnitude. The method need not select a unique eigenvector and may remain in, or oscillate within, the associated dominant invariant subspace. By contrast, when $|\lambda_2/\lambda_1|$ is below but close to one, dominance is unique but convergence can be very slow.

Finally, the orthonormal-basis explanation is restricted to real symmetric matrices. Power iteration can be applied to some nonsymmetric matrices, but the clean orthogonal decomposition is not generally available. Defective matrices, complex dominant eigenvalues, and non-normal behaviour need additional care and lie outside this lesson. In particular, the idealized modal framing must not be used to generalize the symmetric convergence argument to every engineering eigenproblem.

When diagnosing a run, classify the evidence before choosing a response. Alternating signs with improving alignment can be normal for a negative dominant eigenvalue. A starting vector exactly orthogonal to the dominant eigenvector is a structural failure to reach that direction in exact arithmetic. Equal leading magnitudes remove unique selection, whereas a separated ratio close to one retains unique dominance but can demand many iterations. These cases may look similar in a short numerical history, yet their mathematical explanations differ. The classification should always be made under the real symmetric assumptions used here; observations from a nonsymmetric matrix do not inherit this proof automatically.

<!-- section: SEC-06 -->
## Estimating the eigenvalue and judging the residual

Once $x_k\ne0$ approximates an eigenvector, estimate its eigenvalue with the Rayleigh quotient

$$
\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.
$$

For a normalized iterate, $x_k^Tx_k=1$, so this simplifies to $\rho(x_k)=x_k^TAx_k$. In the symmetric setting, if $x_k$ approaches $v_1$, then $\rho(x_k)$ approaches $\lambda_1$.

An estimate alone does not reveal how well the eigen-equation is satisfied. Define the eigenpair residual

$$
r_k=Ax_k-\rho(x_k)x_k.
$$

For an exact eigenpair, the residual is zero. Computationally, $\|r_k\|_2$ is therefore a meaningful stopping measure: stop when it is at most a chosen positive tolerance. It also avoids the sign ambiguity that can distort differences between successive vectors. A small residual says that the computed pair nearly satisfies the matrix equation; it does not require a particular sign for the eigenvector.

The quotient and residual answer different questions. The quotient supplies the scalar paired with the current vector, whereas the residual checks the equation produced by that pairing. To assess an iterate, first confirm that the general quotient has a nonzero denominator, or use the simplified expression only after confirming unit norm. Then form the full residual vector and take its Euclidean norm. Do not replace this calculation with a comparison of two successive vectors: a sign flip can make those vectors appear far apart even when they describe essentially the same eigendirection. A tolerance decision should be attached to the residual norm actually computed for the current approximate pair.

<!-- section: SEC-07 -->
## A guarded implementation and worked consolidation

The full algorithm first normalizes a nonzero $x_0$. At each iteration it forms $y=Ax$, checks for zero norm before division, normalizes, computes the Rayleigh estimate and residual, and returns early if the residual norm meets the positive tolerance. Otherwise it returns the final four values after a positive maximum number of iterations.

The implementation below converts inputs to floating NumPy arrays, requires a square matrix and a compatible one-dimensional vector, rejects a zero start, and validates the iteration controls. Its return tuple is the eigenvalue estimate, normalized eigenvector, residual norm, and iteration count.

Read the safeguards in the same order as the mathematics. Invalid shapes are rejected before any matrix-vector product. The initial norm is tested before normalizing. Inside the loop, the product norm is tested before division. Only after a valid normalized update does the code calculate the Rayleigh estimate and residual. The residual test can return early, while the iteration cap guarantees a final return if the tolerance has not been met. Requiring a positive tolerance and a positive integer cap also prevents the control parameters from creating an undefined or meaningless run.

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
    if (not isinstance(max_iterations, (int, np.integer))
            or isinstance(max_iterations, (bool, np.bool_))
            or max_iterations <= 0):
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
eigenvalue, eigenvector, residual_norm, iterations = result

print("Estimated dominant eigenvalue:", eigenvalue)
print("Estimated eigenvector:", eigenvector)
print("Residual norm:", residual_norm)
print("Iterations:", iterations)
```

For this symmetric matrix, the exact eigenvalues are

$$
3+\sqrt{2}
\quad\text{and}\quad
3-\sqrt{2}.
$$

The first has larger magnitude, so the computation should estimate $3+\sqrt{2}$ and report a small residual. The eigenvector may appear with either sign; both outputs describe the same direction. To interpret the run, compare the estimate with $3+\sqrt{2}$, inspect the residual norm against the tolerance, and note whether the reported count indicates an early residual-based stop or arrival at the iteration cap.

This example consolidates the whole process without changing its scope. The matrix is real and symmetric, the supplied starting vector is nonzero, and the exact eigenvalues identify a unique dominant magnitude. The program then produces a unit direction, an eigenvalue estimate, and a residual-based quality measure. A successful run should be interpreted through all three outputs rather than through the vector components alone. In particular, changing the sign of the reported eigenvector would not change the eigendirection or invalidate a small residual.

The central workflow is now complete: apply and normalize, explain convergence through eigenvector components, check the assumptions before trusting that explanation, estimate the eigenvalue with the Rayleigh quotient, and judge the approximate pair through its residual.
