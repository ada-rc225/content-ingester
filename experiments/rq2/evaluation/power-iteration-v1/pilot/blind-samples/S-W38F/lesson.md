# Power iteration: from matrix-vector updates to trustworthy stopping

Power iteration is a compact algorithm with an important lesson for numerical computing: a short loop can be easy to run but still require careful assumptions, safeguards, and output checks. We will build the method from its linear-algebra foundations, turn it into executable NumPy, and then examine when its answer should—and should not—be trusted.

<!-- section: SEC-01 -->
## Eigenpairs as fixed directions

Let $A\in\mathbb{R}^{n\times n}$. A non-zero vector $v\in\mathbb{R}^n$ is an eigenvector of $A$ when there is a scalar $\lambda$ such that

$$
Av=\lambda v.
$$

The scalar $\lambda$ is the eigenvalue associated with $v$. Multiplication by $A$ therefore leaves the direction represented by $v$ unchanged, apart from a possible sign reversal, while scaling it by $\lambda$. The condition $v\ne 0$ matters: $A0=\lambda 0$ holds for every scalar, so the zero vector cannot identify an eigenvalue. Computationally, our goal is to discover a non-zero direction that behaves approximately this way.

When tracing a candidate pair, keep the types of the objects clear: $A$ maps an $n$-component vector to another $n$-component vector, $v$ supplies the direction, and $\lambda$ is one scalar. The equation says that the two vectors $Av$ and $\lambda v$ coincide. It does not say that $v$ and $\lambda$ can exchange roles. This simple type check prevents a common notation error before we build the iterative algorithm.

<!-- section: SEC-02 -->
## The target is largest in magnitude

Power iteration targets an eigenvalue of largest **magnitude**, not necessarily the most positive eigenvalue. If two eigenvalues are $5$ and $-8$, then $-8$ is the target because $|-8|>|5|$. This distinction should be an invariant in your mental model and in any implementation notes: “dominant” refers to absolute value.

Repeated matrix-vector products can amplify one direction relative to others, which makes the method useful as a basic spectral-computation routine. A ranking matrix can motivate such a computation, but this simplified iteration is not by itself a production ranking system; its convergence still depends on assumptions that we will state explicitly.

Whenever you see the word “largest,” translate it into an explicit absolute-value comparison. For the pair above, compare $|5|=5$ with $|-8|=8$ before choosing. A program that sorts eigenvalue estimates by ordinary numerical order would choose the wrong target in this example. Magnitude ordering is therefore part of the problem specification, not a display convention.

<!-- section: SEC-03 -->
## Orthogonality and projection coefficients

For real vectors $u$ and $v$, the inner product $u^Tv$ is a scalar. The vectors are orthogonal when $u^Tv=0$. A family $v_1,\ldots,v_k$ is orthonormal when

$$
v_i^Tv_j=0\quad(i\ne j),
\qquad \|v_i\|_2=1.
$$

Orthonormal directions provide particularly simple coordinates. If $v$ is a unit vector, then $v^Tx$ is the scalar coefficient of $x$ in the $v$ direction. For example, with $v=(1,0)^T$ and $x=(3,4)^T$, the coefficient is $v^Tx=3$. This calculation tells us whether an initial vector contains a component in a chosen direction; it does not yet make any claim about eigenvectors or convergence.

There are two checks in the word “orthonormal.” Distinct vectors must have zero cross-products, and every vector must have unit Euclidean norm. Orthogonality alone does not guarantee the unit-length condition. Once both checks hold, each coefficient can be computed independently with a dot product. In the example, the result $3$ is a scalar coordinate, not the projected vector itself. Later, the distinction between a zero and non-zero coordinate will decide whether a direction is present initially.

<!-- section: SEC-04 -->
## The symmetric spectral setting

The clean convergence explanation uses a real symmetric matrix, $A=A^T$. In this setting, the spectral theorem gives an orthonormal basis of real eigenvectors. If those eigenvectors are the columns of the orthogonal matrix $Q$, then

$$
A=Q\Lambda Q^T,
\qquad
\Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n).
$$

Every vector can be represented in that basis as

$$
x=\sum_{i=1}^n c_i v_i,
\qquad c_i=v_i^Tx.
$$

For the convergence result used later, order eigenvalues by magnitude and require a strict leading gap:

$$
|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.
$$

The strict first inequality makes the dominant magnitude unique. Symmetry, orthonormal coordinates, and this strict gap are conditions, not properties of every matrix.

The decomposition also gives a concrete representation pipeline. The columns of $Q$ are the directions, the diagonal entries of $\Lambda$ are their associated scale factors, and $Q^T$ computes orthonormal coordinates. The expansion of $x$ is exact because these eigenvectors form a basis. Keep that conclusion beside its hypothesis: the orthogonal real decomposition here follows from $A=A^T$ and must not be assumed merely because a matrix is square.

<!-- section: SEC-05 -->
## Norms and safe normalization

For $x=(x_1,\ldots,x_n)^T$, the Euclidean norm is

$$
\|x\|_2=\sqrt{x_1^2+\cdots+x_n^2}=\sqrt{x^Tx}.
$$

When $x\ne0$, set $r=\|x\|_2$ and $u=x/r$; then $\|u\|_2=1$. Thus $(3,4)^T$ has norm $5$ and normalizes to $(3/5,4/5)^T$. Normalization controls scale without changing direction. If $\|x\|_2=0$, however, then $x$ is the zero vector and division by its norm is undefined. A safe algorithm checks for this breakdown before dividing.

You can verify normalization without relying on intuition: square the new components, add them, and take the square root. For $(3/5,4/5)^T$, the result is $\sqrt{9/25+16/25}=1$. Division by a positive length rescales every component equally, which preserves direction. The zero case is different rather than merely inconvenient: it offers no positive divisor and no direction to preserve.

<!-- section: SEC-06 -->
## The normalized matrix-vector loop

Choose a non-zero initial vector $x_0$. One power-iteration update is

$$
y_{k+1}=Ax_k,
\qquad
x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.
$$

The loop invariant after normalization is $\|x_{k+1}\|_2=1$. Each iteration first applies $A$, then rescales the result. Provided $y_{k+1}\ne0$, the second step changes only scale, not direction. In pseudocode: compute `y = A @ x`; if its norm is zero, report breakdown; otherwise replace `x` by `y / norm(y)`. Keeping the zero check before division is essential.

For a one-step trace, take $A=\operatorname{diag}(2,1)$ and start from the unit vector $(1/\sqrt2,1/\sqrt2)^T$. Multiplication produces $(\sqrt2,1/\sqrt2)^T$, whose norm is $\sqrt{5/2}$. Dividing by that norm gives $(2/\sqrt5,1/\sqrt5)^T$. The output again has unit norm, while the first coordinate has become larger relative to the second. This trace illustrates the update rule only; convergence still needs the later assumptions.

<!-- section: SEC-07 -->
## Inner products and quadratic forms

For equal-length real vectors, $x^Ty$ is the scalar sum of componentwise products. To compute $x^TAx$, first form $y=Ax$ and then compute $x^Ty$; $A$ must be square and dimensionally compatible with $x$. Also, $x^Tx=\|x\|_2^2\ge0$.

For

$$
A=\begin{bmatrix}2&0\\0&1\end{bmatrix},
\qquad x=\begin{bmatrix}1\\2\end{bmatrix},
$$

we obtain $Ax=(2,2)^T$ and $x^TAx=1\cdot2+2\cdot2=6$. This is only the computation pattern for a quadratic form; its use as an eigenvalue estimate comes next.

Shape reasoning makes the evaluation unambiguous. First, the matrix-vector product returns a vector with the same length as $x$. Second, multiplying on the left by $x^T$ turns that vector into one scalar. Trying to compute the final scalar before forming a compatible $Ax$ obscures these dimensions. The identity $x^Tx=\|x\|_2^2$ will also let us recognize when a denominator equals one.

<!-- section: SEC-08 -->
## Estimating the eigenvalue

Given a non-zero approximate eigenvector $x_k$, its Rayleigh quotient is

$$
\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.
$$

Because power iteration normalizes its vectors, $x_k^Tx_k=1$ and the expression simplifies to $\rho(x_k)=x_k^TAx_k$. For a symmetric matrix, if $x_k$ approaches the eigendirection of $v_1$, this estimate approaches $\lambda_1$. The simplified expression must not be used for an unnormalized vector without restoring its denominator.

Treat the quotient as a function of the current vector, not as an extra update to that vector. A reliable trace records $x_k$, forms $Ax_k$, computes the numerator and denominator as scalars, and only then reports $\rho(x_k)$. Even when code is expected to maintain unit norm, the general formula explains which assumption permits the denominator to disappear.

<!-- section: SEC-09 -->
## Residuals measure eigenpair quality

An estimate should be checked as a pair: the vector and its estimated eigenvalue. Define

$$
r_k=Ax_k-\rho(x_k)x_k.
$$

An exact eigenpair has residual zero, while $\|r_k\|_2$ measures how closely the computed pair satisfies the defining equation. This is a useful stopping quantity. Merely comparing successive vectors can be misleading because $v$ and $-v$ represent the same eigendirection, so a sign flip can make two directionally equivalent vectors appear far apart.

The residual test is operational: form the two vectors $Ax_k$ and $\rho(x_k)x_k$, subtract them, and take the Euclidean norm. A small value means that the returned pair nearly satisfies the eigenpair equation used at the start of the lesson. It does not require selecting a preferred sign for $x_k$. The tolerance supplies the program’s threshold for deciding when this mismatch is small enough to stop.

<!-- section: SEC-10 -->
## A safeguarded NumPy implementation

A complete stopping policy needs both a positive tolerance and a positive iteration cap. Normalize the initial vector, then repeatedly multiply, check for breakdown, normalize, estimate the eigenvalue, and compute the residual. Return early when the residual norm is at most the tolerance; otherwise return the final state after the cap. Input validation should reject a non-square matrix, an incompatible or zero initial vector, a non-positive tolerance, and a non-positive or non-integer cap before iteration.

```python
import numpy as np

def power_iteration(A, x0, tolerance=1e-10, max_iterations=1000):
    A = np.asarray(A, dtype=float)
    x = np.asarray(x0, dtype=float)

    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("A must be square")
    if x.shape != (A.shape[0],):
        raise ValueError("x0 has incompatible dimensions")
    tolerance = float(tolerance)
    if not np.isfinite(tolerance) or tolerance <= 0:
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
```

The four returned values are the eigenvalue estimate, normalized vector, residual norm, and iteration count. The breakdown exception precedes division by the zero norm, and the iteration range includes the stated maximum.

There are three distinct termination paths to reason about. Invalid inputs are rejected before the loop. A zero matrix-vector product raises a breakdown error inside the loop before normalization. Otherwise, the function either returns as soon as the residual threshold is reached or returns after exactly the permitted number of iterations. Keeping these paths separate makes a trace easier to audit: reaching the cap is a normal fallback, whereas division by a zero norm is never attempted.

<!-- section: SEC-11 -->
## Why the dominant component can emerge

Return to the real symmetric setting. Expand the initial vector as $x_0=\sum_i c_i v_i$. Before normalization, repeated multiplication gives

$$
A^k x_0
=\sum_{i=1}^n c_i\lambda_i^k v_i
=\lambda_1^k\left(c_1v_1+
\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^k v_i\right).
$$

If $c_1=v_1^Tx_0\ne0$ and $|\lambda_1|>|\lambda_2|$, every subordinate ratio has magnitude below one. Discretely, each additional multiplication contributes another factor $\lambda_i/\lambda_1$, so those components shrink relative to the dominant component. With a real symmetric matrix, non-zero dominant projection, a unique dominant magnitude, and no iterate producing $Ax_k=0$, the direction error generally decreases asymptotically at a rate governed by

$$
\left|\frac{\lambda_2}{\lambda_1}\right|^k.
$$

This describes an asymptotic mechanism, not an unconditional finite-iteration error bound.

The ratio gives a useful qualitative comparison between valid cases. A ratio such as $0.2$ contributes powers that decrease much faster than powers of $0.9$. However, that comparison only applies after confirming the symmetric setting, non-zero dominant coefficient, strict gap, and absence of breakdown. The formula explains relative component suppression; it does not remove the need to inspect the computed residual.

<!-- section: SEC-12 -->
## Failure modes, slow cases, and scope

Several cases break or complicate that argument. If $\lambda_1<0$, normalized iterates may alternate sign; this is not failure because $v_1$ and $-v_1$ are the same eigendirection. If $v_1^Tx_0=0$, the dominant component is absent. In exact arithmetic, repeated multiplication cannot create it, so the method does not converge to $v_1$.

If $|\lambda_1|=|\lambda_2|$, there is no unique dominant magnitude. Iterates may remain in or oscillate within the corresponding invariant subspace rather than selecting one eigenvector. This differs from the separated case where $|\lambda_2/\lambda_1|$ is below but close to one: convergence may occur, yet be very slow, increasing iteration cost before a residual tolerance is met.

Finally, power iteration can apply to some non-symmetric matrices, but the orthogonal decomposition used here is then not generally available. Defective matrices, complex dominant eigenvalues, and non-normal behavior require additional care and lie outside this lesson. The symmetric convergence argument must not be silently generalized to them.

These cases support a compact diagnostic order. First ask whether the mathematical setting matches the symmetric argument. Then check whether the dominant magnitude is unique and whether the initial vector contains its direction. During execution, guard against a zero product. Finally, interpret iteration cost through the magnitude ratio and accept the computed pair through its residual. Different failed checks have different meanings; a tied magnitude is not the same problem as a close but strict gap.

<!-- section: SEC-13 -->
## A complete worked run

Consider

$$
A=\begin{bmatrix}4&1\\1&2\end{bmatrix},
\qquad x_0=\begin{bmatrix}1\\1\end{bmatrix}.
$$

The exact eigenvalues are supplied as $3+\sqrt2$ and $3-\sqrt2$. A local magnitude comparison gives approximately $4.414$ and $1.586$, so $3+\sqrt2$ is dominant for this example. We can now run the same safeguarded algorithm and check both its estimate and residual without deriving a characteristic polynomial.

```python
import numpy as np

def power_iteration(A, x0, tolerance=1e-10, max_iterations=1000):
    A = np.asarray(A, dtype=float)
    x = np.asarray(x0, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("A must be square")
    if x.shape != (A.shape[0],):
        raise ValueError("x0 has incompatible dimensions")
    tolerance = float(tolerance)
    if not np.isfinite(tolerance) or tolerance <= 0:
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
eigenvalue, eigenvector, residual, iterations = power_iteration(
    A, np.array([1.0, 1.0])
)
print("Estimated dominant eigenvalue:", eigenvalue)
print("Estimated eigenvector:", eigenvector)
print("Residual norm:", residual)
print("Iterations:", iterations)
assert abs(eigenvalue - (3.0 + np.sqrt(2.0))) < 1e-8
assert residual <= 1e-10
```

The estimated value should be close to $3+\sqrt2$, and the small residual confirms that the returned vector and value nearly satisfy $Ax=\lambda x$. The eigenvector’s sign is not prescribed: reversing it represents the same eigendirection and leaves the residual test meaningful.

Read the four printed fields together. The estimate identifies the scalar target, the vector supplies its direction, the residual quantifies the defining-equation mismatch, and the iteration count reports how long the stopping policy ran. Agreement with the supplied dominant value plus a residual below tolerance provides the intended computational check for this worked run.
