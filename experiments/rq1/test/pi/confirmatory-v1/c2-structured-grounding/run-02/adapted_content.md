# Eigenvalues, Eigenvectors, and the Power Iteration

<!-- section: SEC-01 -->
## Eigenpairs as special matrix directions

### The defining equation

For a real square matrix $A$, a non-zero vector $v$ is an eigenvector when multiplication by $A$ changes only its scale. The defining relation is

$$Av=\lambda v.$$

The scalar $\lambda$ is the associated eigenvalue. The vector must be non-zero: the zero vector satisfies $A0=\lambda0$ for every scalar, so it cannot identify an eigenvalue. In a mechanical-vibration model, an eigenvector can be viewed as a relative pattern of coordinates, while its eigenvalue supplies a scale associated with that pattern. This vibration language is a bounded teaching frame; the definition and calculations are mathematical statements.

For a small matrix, eigenvalues are roots of the characteristic equation

$$\det(A-\lambda I)=0,$$

where $I$ is the identity matrix of compatible size. The determinant is zero when $A-\lambda I$ has a non-trivial null direction. For a large matrix, explicitly constructing a characteristic polynomial may be less attractive than repeatedly applying $A$ to vectors. These are different numerical approaches, not an assertion that iteration algebraically replaces the characteristic equation.

Power iteration compares eigenvalues by absolute value. It seeks the largest magnitude, not necessarily the largest algebraic value. Between $5$ and $-8$, its dominant value is $-8$. Eigenvectors also have sign ambiguity: $v$ and $-v$ describe the same eigendirection.

<!-- section: SEC-02 -->
## Symmetric matrices and modal components

### An orthonormal eigenbasis

When $A$ is real and symmetric, $A=A^T$, its eigenvectors can be chosen as an orthonormal basis. If these vectors are the columns of $Q$ and the eigenvalues are placed in $\Lambda$, then

$$A=Q\Lambda Q^T,\qquad \Lambda=\operatorname{diag}(\lambda_1,\ldots,\lambda_n).$$

Every vector can be expressed as

$$x=\sum_{i=1}^n c_i v_i,\qquad c_i=v_i^Tx.$$

Thus $c_i$ measures the component of $x$ in direction $v_i$. Order the eigenvalues by magnitude:

$$|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|.$$

The strict first inequality gives a unique dominant magnitude. The pair $(\lambda_1,v_1)$ is the dominant eigenpair for power iteration, even if $\lambda_1$ is negative. The orthonormal decomposition is a particularly clear setting for following modal components, but it should not be transferred to arbitrary non-symmetric matrices.

### Why multiplication selects a direction

Starting from $x_0=\sum_i c_i v_i$, repeated multiplication gives

$$A^kx_0=\sum_{i=1}^n c_i\lambda_i^k v_i
=\lambda_1^k\left(c_1v_1+\sum_{i=2}^n c_i\left(\frac{\lambda_i}{\lambda_1}\right)^k v_i\right).$$

If $c_1=v_1^Tx_0\ne0$, the strict magnitude gap makes every subordinate ratio shrink in magnitude as $k$ grows. The factor $\lambda_1^k$ controls overall scale and may change sign; normalization removes that scale. The remaining direction increasingly reflects $v_1$.

<!-- section: SEC-03 -->
## Power iteration and convergence behaviour

### The normalized update

Choose a non-zero starting vector $x_0$. At each step, first form

$$y_{k+1}=Ax_k,$$

then normalize it:

$$x_{k+1}=\frac{y_{k+1}}{\|y_{k+1}\|_2}.$$

Normalization controls size without changing direction. It is only defined when $\|y_{k+1}\|_2\ne0$, so a zero product is a breakdown that must be detected before division.

For a real symmetric matrix, direction generally converges when $|\lambda_1|>|\lambda_2|$, the initial projection $v_1^Tx_0$ is non-zero, and no iterate produces $Ax_k=0$. The asymptotic direction error is governed by

$$\left|\frac{\lambda_2}{\lambda_1}\right|^k.$$

This describes asymptotic behaviour rather than an unconditional finite-iteration error bound. A ratio close to one means a small spectral gap and potentially slow convergence. If $|\lambda_1|=|\lambda_2|$, a unique eigenvector need not be selected. These cases differ: repeated dominant magnitude removes uniqueness, whereas a close but strict gap preserves uniqueness but can be slow.

If $v_1^Tx_0=0$, exact multiplication cannot create the missing dominant component, so increasing the iteration count does not make the method converge to $v_1$. If $\lambda_1<0$, normalized vectors may alternate sign. That is not failure of direction convergence because the two signs represent the same eigendirection.

<!-- section: SEC-04 -->
## Estimates, residuals, and a NumPy implementation

### Diagnostics that explain the output

For a non-zero iterate, use the Rayleigh quotient

$$\rho(x_k)=\frac{x_k^TAx_k}{x_k^Tx_k}.$$

When $x_k$ is normalized, this becomes $\rho(x_k)=x_k^TAx_k$. For symmetric $A$, the quotient estimates $\lambda_1$ as $x_k$ approaches $v_1$. The eigenpair residual is

$$r_k=Ax_k-\rho(x_k)x_k.$$

An exact eigenpair has zero residual. The norm $\|r_k\|_2$ is a useful stopping measure because comparing successive vectors can be misleading when a negative dominant eigenvalue causes a sign flip.

### Implementation semantics

A robust routine converts $A$ and $x_0$ to floating NumPy arrays, checks that $A$ is square, checks that $x_0$ is one-dimensional with a matching dimension, rejects a zero starting vector, and normalizes the start. It also validates that `max_iterations` is a positive integer before entering the loop. Each iteration computes $y=Ax$, checks for breakdown before division, normalizes, evaluates the Rayleigh quotient and residual, stops when the residual norm is at most positive `epsilon`, and otherwise returns after the maximum count. The returned tuple is $(\text{eigenvalue},x,\text{residual norm},\text{iteration count})$.

```python
import numpy as np

def power_iteration(A, x0, epsilon=1e-10, max_iterations=1000):
    A = np.asarray(A, dtype=float)
    x = np.asarray(x0, dtype=float)
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("A must be square")
    if x.ndim != 1 or x.shape[0] != A.shape[0]:
        raise ValueError("x0 must be one-dimensional and compatible")
    if np.linalg.norm(x) == 0:
        raise ValueError("x0 must be non-zero")
    if not isinstance(max_iterations, (int, np.integer)) or max_iterations <= 0:
        raise ValueError("max_iterations must be a positive integer")
    x = x / np.linalg.norm(x)
    for iteration in range(1, max_iterations + 1):
        y = A @ x
        y_norm = np.linalg.norm(y)
        if y_norm == 0:
            raise ValueError("power iteration broke down")
        x = y / y_norm
        eigenvalue = float(x @ A @ x)
        residual = A @ x - eigenvalue * x
        residual_norm = float(np.linalg.norm(residual))
        if residual_norm <= epsilon:
            return eigenvalue, x, residual_norm, iteration
    return eigenvalue, x, residual_norm, max_iterations

A = np.array([[4., 1.], [1., 2.]])
value, vector, residual, iterations = power_iteration(A, [1., 1.])
print(round(value, 6), round(residual, 12), iterations)
```

For $A=\begin{bmatrix}4&1\\1&2\end{bmatrix}$ and $x_0=(1,1)$, the exact eigenvalues are $3+\sqrt{2}$ and $3-\sqrt{2}$. The first is dominant because its magnitude is larger. The routine approaches it with a small residual; either sign of the returned vector is acceptable. The iteration count is evidence about the stopping path, not a substitute for the estimate and residual.

### Scope of the convergence explanation

Power iteration can be useful for some non-symmetric matrices, but the clean orthogonal decomposition is not generally available. Defective matrices, complex dominant eigenvalues, and non-normal behaviour require additional care and are outside this lesson’s convergence explanation. Therefore the derivation above is specifically a real symmetric argument, while the implementation’s input checks and residual diagnostics remain practical safeguards more broadly.

The complete reasoning chain is: identify the eigenpair relation, compare magnitudes, expand the initial vector into eigen-directions, multiply and normalize, estimate with the Rayleigh quotient, and test the residual. In a matrix-based engineering computation, this separates a plausible direction from a direction that actually satisfies the approximate eigenpair equation.

### How to read a run as an engineer

Start by checking the inputs before interpreting any numerical result. A square matrix requirement ensures that the product $Ax$ has the same coordinate dimension as $x$. A one-dimensional, dimension-matched starting array makes the matrix-vector operation unambiguous. Rejecting a zero starting vector is also essential because it has no direction to normalize. These checks prevent an apparently numerical problem from actually being a shape or initialization problem.

Next, separate the roles of the iteration quantities. The product $y$ is the unscaled direction produced by the matrix. Its norm is used only to control scale, so the normalized vector can be compared across iterations. The Rayleigh quotient is a scalar estimate associated with the current vector, whereas the residual tests the pair together. A vector may look stable in a few components while still having a residual that is too large for the intended calculation.

The stopping rule therefore has two distinct safeguards. A residual threshold can stop an easy problem early, once the approximate eigenpair relation is sufficiently close. A positive maximum iteration count guarantees a finite fallback when the threshold is not reached. The fallback is not a convergence guarantee: it reports the best state reached within the configured loop. Validating the count before the loop also prevents an empty loop from being mistaken for a meaningful computation.

For the two-by-two worked matrix, the characteristic equation gives two exact values, while the iteration uses only matrix-vector products. The initial vector $(1,1)$ has a component in the dominant direction, so the dominant component is amplified relative to the other one. Each normalization removes the common growth in scale. The Rayleigh estimate approaches $3+\sqrt{2}$, and the residual provides the numerical evidence used by the stopping test. The returned vector can be multiplied by $-1$ without changing the eigendirection, so its sign should not be used as a pass/fail criterion.

This workflow also clarifies what power iteration does not provide. It does not automatically identify every eigenpair, and it does not turn a repeated dominant magnitude into a unique direction. It is aimed at a dominant magnitude under the stated symmetric assumptions. When the spectral gap is small, planning should allow more iterations or use a different numerical strategy; when the dominant projection is absent in exact arithmetic, changing only the iteration count cannot repair the starting direction. The residual remains the most direct check of the approximate eigenpair relation produced by the selected routine.

<!-- section: SEC-05 -->
## Exercises and worked solutions

<!-- exercise: EX-001 -->
### Exercise 1 — concept check

A real symmetric matrix has eigenvalues $8$, $-7$, and $2$. The starting vector has a non-zero component along the eigenvector for $8$. State the target, the asymptotic factor, and two situations in which the usual convergence conclusion does not apply. Also state the limitation when the matrix is non-symmetric.

<!-- solution: EX-001 -->
### Worked solution

The target is $8$, since $|8|>|-7|>|2|$. The asymptotic factor is $(7/8)^k$. The conclusion does not apply when the dominant projection is exactly zero, when the two largest magnitudes are equal, or when an iterate gives a zero matrix-vector product. A ratio close to one gives slow convergence, which is distinct from repeated dominance. For a general non-symmetric matrix, the orthogonal eigenbasis argument is not generally available; defective, complex, and non-normal cases need additional care.

<!-- exercise: EX-002 -->
### Exercise 2 — hand calculation

Let $A=\operatorname{diag}(4,1)$ and $x_0=(3,1)$. Carry out one power-iteration step without initially normalizing $x_0$. Report the product, normalized next vector, Rayleigh quotient, residual, and residual norm. As a consistency check, verify that the next vector has unit Euclidean norm and that the residual is computed from the same quotient.

<!-- solution: EX-002 -->
### Worked solution

The product is $y_1=Ax_0=(12,1)$. Its norm is $\sqrt{145}$, so the normalized vector is $(12/\sqrt{145},1/\sqrt{145})$. Substituting this vector into the Rayleigh quotient gives $\rho=577/145$. Using the same vector and quotient in $r=Ax_1-\rho x_1$ gives the residual shown below. The squared components sum to $145/145=1$, which is the consistency check for normalization; the residual norm is the Euclidean norm of those two residual components.

<!-- derived-answer: EX-002 -->
**Result from the derivation:** `{"initial_vector_used":[3.0,1.0],"product":[12.0,1.0],"next_vector":[0.9965457582448796,0.08304547985373997],"rayleigh_quotient":3.979310344827586,"residual":[0.02061818810161853,-0.24741825721941837],"residual_norm":0.24827586206896554}`

<!-- answer: EX-002 -->
**Checked answer:** `{"initial_vector_used":[3.0,1.0],"product":[12.0,1.0],"next_vector":[0.9965457582448796,0.08304547985373997],"rayleigh_quotient":3.979310344827586,"residual":[0.02061818810161853,-0.24741825721941837],"residual_norm":0.24827586206896554}`

<!-- exercise: EX-003 -->
### Exercise 3 — code diagnostic

A colleague writes the routine below. Identify at least four problems relative to the implementation semantics taught above, and describe the correction for each.

```python
def buggy_iteration(A, x, max_iterations):
    x = x / np.linalg.norm(x)
    for k in range(max_iterations):
        x = A @ x
        x = x / np.linalg.norm(x)
    return x
```

<!-- solution: EX-003 -->
### Worked solution

The routine does not check that $A$ is square or that `x` is one-dimensional with a compatible length. It can divide by zero when the initial vector or a later product is zero, and it accepts zero or non-integer iteration counts without the required positive-integer validation. It omits the Rayleigh quotient, residual stopping test, residual tolerance, and maximum-iteration diagnostics. Finally, it returns only a vector rather than the four values needed to interpret the computation. The correction is to validate all inputs first, normalize the initial vector, check the product norm before division, compute the scalar estimate and residual after each normalized step, stop on the residual threshold, and return the estimate, vector, residual norm, and iteration count.

<!-- expected-stdout: EX-003/1 -->
**Expected output:** `""`

```python
import json
import numpy as np

def validate_iterations(max_iterations):
    if not isinstance(max_iterations, (int, np.integer)) or max_iterations <= 0:
        raise ValueError("max_iterations must be a positive integer")

try:
    validate_iterations(0)
except ValueError as error:
    print(json.dumps({"error": str(error)}))
```

<!-- expected-stdout: EX-003/2 -->
**Expected output:** `"{\"error\": \"max_iterations must be a positive integer\"}\n"`
