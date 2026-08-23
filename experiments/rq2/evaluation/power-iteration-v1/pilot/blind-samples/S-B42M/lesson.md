# Power Iteration

Power iteration is an iterative method for estimating an eigenvalue and its associated eigendirection. This lesson develops the method from the eigenpair definition, explains the assumptions behind its convergence, defines practical quality and stopping measures, and then connects the mathematics to an executable implementation.

<!-- section: SEC-01 -->
## Eigenpairs and the motivation for iteration

Let $A\in\mathbb{R}^{n\times n}$. A non-zero vector $v\in\mathbb{R}^n$ is an eigenvector of $A$ if there is a scalar $\lambda$ such that

$$
Av=\lambda v.
$$

The scalar $\lambda$ is the eigenvalue associated with $v$. The requirement $v\ne0$ matters: the zero vector satisfies $A0=\lambda0$ for every scalar $\lambda$, so it cannot identify an eigenvalue or eigendirection.

The equation is a relationship between a transformation and a direction. Applying $A$ to an eigenvector does not generally leave the vector unchanged; it multiplies that vector by the scalar $\lambda$. The sign and size of $\lambda$ therefore describe how the transformation acts along that direction. Power iteration does not try to discover every eigenpair at once. It repeatedly applies the transformation and uses the resulting direction to focus attention on one eigenpair, normally the one associated with the largest magnitude.

One classical route to eigenvalues is the characteristic equation

$$
\det(A-\lambda I)=0,
$$

where $I$ is the identity matrix of compatible dimension. For a small matrix, solving this equation can be useful. For a large matrix, explicitly forming the characteristic polynomial is usually a poor numerical strategy. An iterative method instead uses repeated matrix–vector products to estimate selected eigenpairs. Power iteration is one such method.

A crucial point about what it selects is that it targets an eigenvalue of largest magnitude, not necessarily the most positive eigenvalue. For example, between $5$ and $-8$, the dominant value by magnitude is $-8$, because $|-8|>|5|$.

<!-- section: SEC-02 -->
## The symmetric spectral setting

The cleanest convergence explanation uses a real symmetric matrix, so assume $A=A^T$. The spectral theorem then supplies an orthonormal basis of real eigenvectors. With the eigenvectors as the columns of an orthogonal matrix $Q$,

$$
A=Q\Lambda Q^T,
\qquad
\Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n).
$$

Every vector $x$ can be expressed in this eigenvector basis:

$$
x=\sum_{i=1}^n c_i v_i,
\qquad c_i=v_i^T x.
$$

The coefficient formula depends on orthonormality. These statements should not be silently extended to arbitrary non-symmetric matrices: a general non-symmetric matrix does not necessarily have this clean orthogonal real decomposition.

This representation is useful because multiplication by $A$ becomes especially transparent in the eigenvector coordinates. If a component points along $v_i$, multiplication scales that component by $\lambda_i$. The iteration can therefore be understood by comparing how quickly the different components are scaled, rather than by treating each matrix product as an unrelated calculation. The symmetric assumption is doing real work here: it provides both real eigenvectors and the orthonormal coefficient rule used in the argument.

Order the eigenvalues by magnitude as

$$
|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.
$$

The strict first inequality says that $\lambda_1$ is unique in magnitude. It is the dominant eigenvalue for power iteration. “Dominant” here always means largest absolute value, not largest algebraic value.

<!-- section: SEC-03 -->
## The normalized power update

Choose a non-zero initial vector $x_0$. At each step, first multiply by the matrix and then control the scale:

$$
y_{k+1}=Ax_k,
\qquad
x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.
$$

The denominator must be non-zero. Normalisation changes the length of the matrix–vector product but not its direction, so it prevents the size of the iterates from growing or shrinking uncontrollably while preserving the direction being investigated. The initial vector must also be non-zero; otherwise it cannot be normalised and contains no useful direction.

For one update, compute $y_{k+1}$, calculate its Euclidean norm, and divide every component of $y_{k+1}$ by that norm. The result has unit 2-norm. Repeating this update is the power iteration.

For example, if a matrix–vector product is twice as long but points in the same direction, normalisation makes the two products produce the same next iterate. This illustrates why the scale is not the information being retained by the basic method. The direction is retained, while the magnitude is reset to one at every successful step. The zero-product check is essential because division by a zero norm is undefined and because such a product gives no direction to continue with.

<!-- section: SEC-04 -->
## Why convergence can occur

Using the symmetric eigenbasis, write the initial vector as
$x_0=\sum_{i=1}^n c_i v_i$, where $c_i=v_i^Tx_0$. After $k$ unnormalised multiplications,

$$
A^k x_0
=\sum_{i=1}^n c_i\lambda_i^k v_i
=\lambda_1^k\left(c_1v_1+
\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^k v_i\right).
$$

The dominant component is multiplied by $\lambda_1^k$. Each other component is multiplied by a ratio whose magnitude is below one when $|\lambda_1|>|\lambda_2|$. Consequently, those subordinate terms become relatively smaller as $k$ increases. This argument requires the initial dominant projection

$$
c_1=v_1^Tx_0\ne0.
$$

Under the real-symmetric assumptions, a unique dominant magnitude, a non-zero initial projection onto $v_1$, and no iterate with $Ax_k=0$ imply that the direction error generally decreases asymptotically at a rate governed by

$$
\left|\frac{\lambda_2}{\lambda_1}\right|^k.
$$

This is an asymptotic rate, not an unconditional finite-iteration error bound. A smaller ratio normally means faster asymptotic alignment; a ratio close to one means that many iterations may be needed.

The factorisation also explains why the initial vector matters. A vector can be non-zero and still have no component in the dominant direction. Non-zero length is enough to start the arithmetic, but it is not enough to guarantee that the desired component is present. The convergence argument needs both a usable starting vector and a spectral separation. In a numerical calculation, the residual and a maximum iteration limit help report what happened without claiming more accuracy than the calculation supports.

<!-- section: SEC-05 -->
## Failure modes and scope boundaries

Several different behaviours must be distinguished. If $\lambda_1<0$, successive normalised iterates may alternate sign. This is not, by itself, failure: $v_1$ and $-v_1$ represent the same eigendirection. A direction-based assessment should therefore not reject an iteration merely because the sign changes.

If $v_1^Tx_0=0$, the initial vector has no component in the dominant eigendirection. In exact arithmetic, repeated multiplication cannot create that missing component. The iterates remain in the relevant non-dominant invariant subspace, so the method will not converge to $v_1$; this is not merely slow convergence.

If $|\lambda_1|=|\lambda_2|$, the method need not select a unique eigenvector. It may remain in, or oscillate within, the invariant subspace associated with the dominant magnitudes. This is different from the separated case in which $|\lambda_2/\lambda_1|$ is close to one: there the dominant magnitude is unique, but convergence can be very slow.

Power iteration can be applied to some non-symmetric matrices, but the orthogonal decomposition used in the convergence explanation is not generally available. Defective matrices, complex dominant eigenvalues, and non-normal behaviour require additional care and are outside this lesson’s scope. Thus the convergence claims above must be read with their real-symmetric assumptions intact.

<!-- section: SEC-06 -->
## Eigenvalue estimates and residual stopping

Once an approximate eigenvector $x_k$ is available, estimate its eigenvalue with the Rayleigh quotient

$$
\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.
$$

This formula requires $x_k\ne0$. When $x_k$ is normalised, $x_k^Tx_k=1$, so it reduces to

$$
\rho(x_k)=x_k^TAx_k.
$$

For a symmetric matrix, if $x_k$ approaches $v_1$, then $\rho(x_k)$ approaches $\lambda_1$. The estimate alone does not fully describe the quality of the pair, so also compute the eigenpair residual

$$
r_k=Ax_k-\rho(x_k)x_k.
$$

An exact eigenpair has zero residual. The norm $\|r_k\|_2$ measures how far the computed pair is from satisfying the eigenvector equation with its estimated eigenvalue, and it provides a practical stopping measure. Comparing successive vectors alone can be misleading because a sign flip can make two representatives look far apart even when they describe the same eigendirection.

The residual test is tied directly to the eigenpair equation. If $r_k$ is small, then $Ax_k$ is close to $\rho(x_k)x_k$ in the Euclidean norm. It is therefore a test of the computed pair, rather than merely a test of whether two successive representatives look similar. The tolerance $\varepsilon$ expresses the desired numerical threshold, while $K$ ensures that the procedure has a defined fallback when the threshold is not reached. Reaching the iteration cap should be reported as a capped result, not automatically described as convergence.

<!-- section: SEC-07 -->
## A safeguarded algorithm

Given $A$, a non-zero $x_0$, a positive tolerance $\varepsilon$, and a positive maximum iteration count $K$, the complete sequence is:

1. Normalise $x_0$.
2. Compute $y=Ax_k$.
3. If $\|y\|_2=0$, stop with a breakdown error before dividing.
4. Set $x_{k+1}=y/\|y\|_2$.
5. Compute $\rho_{k+1}=x_{k+1}^TAx_{k+1}$.
6. Compute $r_{k+1}=Ax_{k+1}-\rho_{k+1}x_{k+1}$.
7. Stop if $\|r_{k+1}\|_2\le\varepsilon$.
8. Otherwise continue until $K$ iterations have been performed.

The following implementation makes the input and stopping safeguards explicit. It returns the estimated eigenvalue, the final unit vector, the residual norm, and the iteration count. It also rejects non-positive iteration limits and tolerances before entering the loop.

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
result = power_iteration(A, np.array([1.0, 1.0]))
print("Estimated dominant eigenvalue:", result[0])
print("Estimated eigenvector:", result[1])
print("Residual norm:", result[2])
print("Iterations:", result[3])
```

<!-- section: SEC-08 -->
## Worked consolidation

Consider

$$
A=\begin{bmatrix}4&1\\1&2\end{bmatrix},
\qquad x_0=\begin{bmatrix}1\\1\end{bmatrix}.
$$

The matrix is real and symmetric. Its exact eigenvalues are

$$
3+\sqrt{2}
\quad\text{and}\quad
3-\sqrt{2}.
$$

Because $3+\sqrt{2}$ has the larger magnitude, it is the dominant eigenvalue. The starting vector is non-zero, and its component in the dominant eigendirection is not zero for this example, so the power update can reveal that direction. Each cycle forms $Ax_k$, normalises the result, estimates the eigenvalue with the Rayleigh quotient, and checks the residual norm. The implementation should therefore estimate a value close to $3+\sqrt{2}$ and produce a small residual, subject to the chosen tolerance and iteration cap. The eigenvector may have either overall sign; both signs represent the same eigendirection.

To consolidate the method, trace one update by hand: calculate $y_1=Ax_0$, find $\|y_1\|_2$, and form $x_1=y_1/\|y_1\|_2$. Then calculate $\rho(x_1)$ and $\|Ax_1-\rho(x_1)x_1\|_2$. Finally, explain which assumption would be violated in each of these cases: a zero starting vector, a starting vector with zero dominant projection, equal dominant magnitudes, and a zero matrix–vector product during an iteration. A complete explanation should distinguish invalid input, failure to target the dominant direction, non-unique or slow convergence, and breakdown before normalisation.

When tracing the example, keep the order of operations visible. First form the product, then measure its norm, then normalise, and only after that compute the Rayleigh estimate and residual. This order matches the algorithm and avoids using an unnormalised vector with the simplified Rayleigh formula. Check the result in several ways: the returned vector should have approximately unit 2-norm, the estimated eigenvalue should be near the dominant exact value, and the residual norm should be small if the tolerance was reached. These checks answer different questions, so agreement in one does not replace the others.

The broader lesson is to separate an algorithm’s intended target from the conditions under which its explanation is valid. Power iteration is simple because each step needs only a matrix–vector product and a normalisation, but its interpretation depends on magnitude dominance, an initial dominant component, and the absence of breakdown. When those conditions fail, the correct response is to diagnose the specific limitation rather than to label every unexpected sequence as a coding error.
