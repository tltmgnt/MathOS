# MathOS BSD Milestone 08 — independent 2-Selmer calculations on selected original-family fibers

**Status:** executable computational experiment; **observed numerical certificates are recorded only after actual PARI/GP execution**. The current manuscript does **not** assert a new infinite exact-rank-3 theorem, a novel mathematical result, analytic rank equality, or a solution of Birch–Swinnerton–Dyer.

This work is stacked on [MathOS Milestone 07](BSD_CUBIC_DESCENT_INFINITE_UPPER_07.md). Unlike the large parameter-dependent Minkowski bound there, we now use **the independently developed PARI/GP 2-descent and Cassels-pairing implementation** to seek much sharper upper bounds at **specified, individual fibers**. The implementation also invokes the actual, SHA-pinned ResearchOs/TECT offline runtime; its state is not allowed to exceed **SUPPORTED** on a single computational run without independently authenticated reproduction and adversarial evidence.

## 1. Exact mathematical input

For every integer parameter \(u\), set \(s=u(u+1)\) and

\[
E_u:\quad y^2+y=x^3+\frac{s}{2}x^2-\frac{s+2}{2}x.
\]

The family discriminant is

\[
D(u)=s^4+10s^3+34s^2+60s+37>0.
\]

Three distinguished rational points are \(P=(0,0)\), \(Q=(1,0)\), \(R=(-1,u)\). Their mere existence does **not** prove their independence at every parameter: \(u=0\) has previously known rank one and \(u=1\) rank two. Two rank-three benchmark fibers are \(u=2\) (LMFDB 5077.a1) and \(u=3\) (LMFDB 43669.a1), but the audit below calls a **different implementation of 2-descent**, rather than relying on the rank entries of those databases. This distinguishes calculation from citation-based repetition.

The earlier MathOS result gives exact generic algebraic rank \(3\) over \(\mathbb Q(U)\), using an older published rank formula. The issue is whether infinitely many individual specializations also have exact rank three.

## 2. Selected-fiber, unconditional 2-descent

For \(u\in\{0,1,2,3\}\), an **external** PARI/GP program receives the exact Weierstrass coefficients

\[
[a_1,a_2,a_3,a_4,a_6]
=\left[0,\frac{s}{2},1,-\frac{s+2}{2},0\right].
\]

For \(u=2,3\) the displayed rational points are additionally supplied as known inputs to assist rank computations; the source itself checks all three equations first.

According to the current [PARI/GP reference manual](https://pari.math.u-bordeaux.fr/dochtml/html/Elliptic_curves.html#ellrank), \`ellrank(E)\` performs 2-descent and Cassels-pairing arithmetic and returns

\[
[r_{\rm lower},r_{\rm upper},\sigma,L],\quad
r_{\rm lower}\le \operatorname{rank}E(\mathbb Q)\le r_{\rm upper}.
\]

Here \(\sigma\) is the even Cassels-pairing correction; PARI also computes the 2-Selmer dimension \(C\), which satisfies the documented identity

\[
C = r_{\rm upper}+\dim_{\mathbb F_2}E(\mathbb Q)[2]+\sigma.
\]

The GP audit obtains \(\dim E(\mathbb Q)[2]\) from the independent \`elltors(E)\` computation. A strict parser rejects any malformed or inconsistent record or failed/expired subprocess. It preserves SHA-256 digests, PARI version, and the exact committed input source.

**A successful machine-executed upper bound** is a conditional-on-software-correctness computer-assisted certificate for **that specified curve**, not a standalone, independently peer-reviewed proof or a theorem about infinitely many parameters. If \(\dim \operatorname{Sel}_2(E_u)\le3\) and three points have independently proved positive rank, then \(\operatorname{rank}E_u(\mathbb Q)=3\) for that \(u\). The simple inequalities never give an analytic-rank equality without additional mathematics.

**Execution transparency:** Exact numerical outcomes are in the linked GitHub Actions run's uploaded \`MathOS-BSD08-PARI-Tect-cas-evidence\` artifact, not fabricated in this manuscript. If any solver invocation times out or errors, its status is \`INCONCLUSIVE\` and **must not be counted as a rank certificate**. Any later summary must cite the actual run ID and raw logs.

## 3. ResearchOS / TECT X — authentic offline controller execution

Milestone 08 clones the **canonical ResearchOs repository** and checks out commit \`4692b75db52c91ab36622bda36d1c26247433d2a\`. It executes

    python -m tect_runtime evaluate tect-scenario.json --output tect-bundle
    python -m tect_runtime verify tect-bundle

on a scenario generated from the real PARI/GP JSON output. The preserved replay bundle includes \`scenario.json\`, \`ledger.json\`, and \`report.json\`. A single local validation receipt may raise a narrowly worded claim about **observed computed output** to \`SUPPORTED\`, but the workflow deliberately rejects any state \`VALIDATED\`, \`STABLE\`, or \`ASSURED\`. TECT's actor names and receipt hashes do **not** authenticate human reviewers, confer scientific independence, or prove a mathematical theorem.

### TECT X five adversarial gates

| Gate | Question | Acceptance threshold / current limitation |
|---|---|---|
| 1. Mathematical input provenance | Does every PARI run match the **original MathOS** model and specified integer \(u\)? | Exact Weierstrass coefficients, checked points, source SHA and GP version; audit rejects mismatches |
| 2. Descent output integrity | Are 2-Selmer dimensions consistent with PARI's returned lower/upper ranks, \(E[2]\), and pairing correction? | One exact, complete marker with \(C=r_{\rm upper}+t_2+\sigma\), zero exit code, raw-log SHA-256 |
| 3. Independent computational implementation | Is this actually distinct from repeating LMFDB's rank display? | PARI/GP implements its own descent; executed logs are required; **not** independent human peer review |
| 4. Infinite-set extension | Is there a proven infinite \(S\) of parameters with a **uniform** Selmer bound at most three? | **NOT ESTABLISHED**: finite certificates cannot imply infinitude |
| 5. Scientific novelty and truth-status control | Are original theorem, analytic comparison, and BSD claims left unresolved absent proofs? | Required no-promotion assertions and canonical replay; scientific assurance remains below VALIDATED |

## 4. Why the finite computations do not solve the infinite-family problem

Consider the explicit infinite progression from Milestone 07,

\[
A=\{24k:k\in\mathbb Z\}.
\]

Its cubic 2-division polynomial is irreducible, so there is no rational 2-torsion for \(u\in A\). For such fibers, the 2-descent inequality is particularly simple:

\[
\operatorname{rank}E_{24k}(\mathbb Q)
\le\dim_{\mathbb F_2}\operatorname{Sel}_2(E_{24k}/\mathbb Q).
\]

Set

\[
S_3=\{\,24k:k\in\mathbb Z,\quad
\dim_{\mathbb F_2}\operatorname{Sel}_2(E_{24k}/\mathbb Q)\le3\,\}.
\]

For every member of \(S_3\) outside the **finite** set where Silverman's specialization may fail, the three generic sections are independent and

\[
\operatorname{rank}E_{24k}(\mathbb Q)=3.
\]

**This is a conditional criterion, not an infinite-rank-3 theorem:** the **infinitude of \(S_3\)** is *not* proved. In particular, no number of separate u-values computed by a CAS implies \(|S_3|=\infty\). A genuine next breakthrough would prove \(S_3\) infinite by a **family-level Selmer comparison, sieve, or uniform local-condition argument**, with a noncircular proof of all hypotheses.

The known rank-three fibers \(u=2,3\) lie outside \(A=24\mathbb Z\); they are **validation controls**, not members of the proposed infinite progression. It remains a separate research problem to identify a tractable infinite subfamily with uniformly bounded 2-Selmer ranks.

## 5. Files and reproduction

- \`mathos/research/bsd_selmer_selected_08.gp\` — actual PARI/GP input, four selected parameters (\(0,1,2,3\)); source is versioned in MathOS.
- \`mathos/research/bsd_selmer_selected_08.py\` — fail-closed provenance parser and canonical TECT scenario builder.
- \`tests/test_bsd_selmer_selected_08.py\` — **synthetic fixtures explicitly identified as synthetic**, malicious-record rejection tests, and no-promotion checks.
- \`.github/workflows/bsd-selmer-selected-08.yml\` — PARI installation, actual 2-descent runs, artifact upload, pinned canonical ResearchOs controller and replay verification.

The parser anticipates \(u=\pm24\) as optional later tests but **does not claim those fibers were run** in the standard workflow.

Source references: [PARI/GP elliptic curves documentation](https://pari.math.u-bordeaux.fr/dochtml/html/Elliptic_curves.html#ellrank); [Magma independent 2-Selmer specification](https://docs.magma-maths.org/v2.30-1/ArithmeticGeometry/EllipticCurvesOverQAndNumberFields/mordell-weil.html); [ResearchOs TECT specification](https://github.com/tltmgnt/ResearchOs/blob/main/TECT_SPEC.md); [MathOS 07 manuscript](BSD_CUBIC_DESCENT_INFINITE_UPPER_07.md).

**Research and AI disclosure:** ChatGPT designed the computational research workflow and wrote the code/documentation. Published mathematical theorems and original software are attributed to their respective authors. Neither automated tests nor a TECT replay should be misrepresented as five independent mathematical proofs or a peer-reviewed new theorem.
