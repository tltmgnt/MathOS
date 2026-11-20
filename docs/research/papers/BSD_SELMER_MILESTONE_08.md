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

For \(u\in\{0,1,2,3,24,-24\}\), an **external** PARI/GP program receives the exact Weierstrass coefficients

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


## 2A. **Actually observed PARI/GP result** — six specializations

The GitHub Actions run [44654855201](https://github.com/tltmgnt/MathOS/actions/runs/44654855201) executed **PARI/GP 2.17.3-1** on six specified fibers, including the two intended arithmetic-progression probes \(u=\pm24\). All six exact computer-algebra invocations exited with status zero; the program independently reported rank intervals, \(2\)-Selmer dimensions and the number of non-torsion points it returned. The raw CAS logs, source and hash manifest, parsed JSON, and actual canonical TECT replay bundle are preserved in that workflow's **MathOS-BSD08-PARI-Tect-cas-evidence** artifact. The source commit used was \`a1dcf76596971782ae32a682443c42aecbd01642\`. An immutable observation snapshot with raw log hashes is in [computed evidence JSON](BSD_SELMER_08_COMPUTED_EVIDENCE.v1.json).

| \(u\) | \(D(u)\) | PARI rank interval | \(2\)-Selmer dimension | Returned independent points |
|---:|---:|:---:|---:|---:|
| \(0\) | 37 | [1,1] | 1 | 1 |
| \(1\) | 389 | [2,2] | 2 | 2 |
| \(2\) | 5,077 | [3,3] | 3 | 3 |
| \(3\) | 43,669 | [3,3] | 3 | 3 |
| \(24\) | 131,772,276,037 | **[4,4]** | **4** | 4 |
| \(-24\) | 94,536,886,789 | **[4,4]** | **4** | 4 |

For all six runs \(\dim E_u(\mathbb Q)[2]=0\) and PARI's Cassels correction \(\sigma=0\), so its output satisfied \(C=r_{\rm upper}\) with no inference from numerical \(L\)-values. The exact rank-three cases \(u=2,3\) reproduce the externally recorded rank-three benchmarks via an independently developed 2-descent implementation; the rank-four examples \(u=24,-24\) are **newly certified within this MathOS audit** but are **not asserted to be previously unknown in the mathematical literature**. They do not provide a theorem for infinitely many parameters.

**Important falsification:** The original proposal to prove \(\operatorname{rank}E_{24k}(\mathbb Q)\le3\) for **every** \(k\in\mathbb Z\) is **false**: the two computed rank-four counterexamples are \(k=1\) and \(k=-1\). The revised question is whether there exists a *proper infinite subset* \(S\subset24\mathbb Z\) for which the \(2\)-Selmer dimension is uniformly at most three. **No such infinite subset has been proved.**

The canonical ResearchOs controller was genuinely executed at pinned commit \`4692b75db52c91ab36622bda36d1c26247433d2a\`. It returned the narrowly scoped claim state **SUPPORTED** and replayed its hash-linked evidence successfully. This is **not** \`VALIDATED\` or \`ASSURED\`: no independent reviewer, separate reproduction, or proof of infinitude is represented by the TECT receipt.

---

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

## 5. Recorded independent CAS execution — six selected fibers

An actual [GitHub Actions run 44654855201](https://github.com/tltmgnt/MathOS/actions/runs/44654855201), using **PARI/GP 2.17.3-1**, completed successfully and executed the original MathOS family at the six parameters below. Its PARI logs emitted one valid \`MATHOS08\` record each. The pinned ResearchOs TECT offline controller independently replayed the evidence ledger, reaching **SUPPORTED for the narrow claim "these computations were observed"**; it did **not** certify mathematical originality or a general theorem.

| u | PARI lower rank | PARI upper rank | pairing correction | dim E(Q)[2] | 2-Selmer dimension |
|---:|---:|---:|---:|---:|---:|
| 0 | 1 | 1 | 0 | 0 | 1 |
| 1 | 2 | 2 | 0 | 0 | 2 |
| 2 | 3 | 3 | 0 | 0 | 3 |
| 3 | 3 | 3 | 0 | 0 | 3 |
| 24 | 4 | 4 | 0 | 0 | 4 |
| -24 | 4 | 4 | 0 | 0 | 4 |

**Source provenance:** [machine-readable observed data](BSD_SELMER_MILESTONE_08_OBSERVED.json); run ID \`44654855201\`; original GitHub job ID \`136018446386\`; source SHA \`a1dcf76596971782ae32a682443c42aecbd01642\`; workflow artifact \`14593136191\` (SHA-256 \`3bae7379ff0f60397b059109e956bcf5868fc5c299dc16006db63d31c2736681\`). Workflow artifacts can expire; the evidence file stores the provenance and rank outputs, not a formal arithmetic certificate. The code was checked under \`ellrank\`'s **unconditional** method, not an invocation of BSD-dependent analytic-rank routines.

**Key falsification:** The integer progression \(u=24k\) includes \(u=24\) and \(u=-24\). The independent PARI implementation returned an exact Mordell–Weil rank interval \([4,4]\) at both parameters (conditional on trusting CAS implementation). Therefore **a claim that all \(u\in24\mathbb Z\) have rank at most three is false**. The existence of some proper **infinite subset** of \(24\mathbb Z\) with exact rank three is **still open** in this project. These two rank-four fibers do not disprove that weaker existence claim.

**Scientific caveat:** The computation is source-auditable, repeatable and stronger than the coarse bounds \(B(24)=71\), \(B(-24)=74\) in Milestone 07. However, it remains a single-CAS computational result awaiting an independently implemented second calculation or a specialist's explicit descent certificate. It is not yet an independent formal proof of the rank, nor a peer-reviewed discovery. No result above yields an exact **analytic** rank equality.

## 6. A concrete noncircular route to an infinite rank-three subset

Define

\[
S_{3}^{\rm Sel}:=\{24k: k\in\mathbb Z,\;
\dim_{\mathbb F_2}\operatorname{Sel}_2(E_{24k}/\mathbb Q)\le3\}.
\]

Every \(u\in S_{3}^{\rm Sel}\) outside the (not explicitly determined) finite bad-specialization set has **exact algebraic rank three**: the three-section lower bound holds there, and the upper bound is at most the 2-Selmer dimension because the 2-division cubic is irreducible throughout \(24\mathbb Z\). Importantly, **the infinitude of \(S_3^{\rm Sel}\) has not been shown**. The recorded \(u=\pm24\) have 2-Selmer dimension four, so neither belongs to this candidate set; \(u=0\) has 2-Selmer dimension one, so it belongs to the low-Selmer criterion but is a rank-drop specialization. This does not contradict the finite-exception principle.

To turn the criterion into a theorem, one would need a uniform family-level control of local Kummer images and cubic class-group 2-torsion for an explicitly defined infinite subclass; analytic-rank equality remains an additional independent requirement. We have **not** produced such a uniform argument. Do not infer infinitude from the six numerical points.

## 7. Files and reproduction

- \`mathos/research/bsd_selmer_selected_08.gp\` — actual PARI/GP input, six selected parameters (\(0,1,2,3,24,-24\)); source is versioned in MathOS.
- \`mathos/research/bsd_selmer_selected_08.py\` — fail-closed provenance parser and canonical TECT scenario builder.
- \`tests/test_bsd_selmer_selected_08.py\` — **synthetic fixtures explicitly identified as synthetic**, malicious-record rejection tests, and no-promotion checks.
- \`.github/workflows/bsd-selmer-selected-08.yml\` — PARI installation, actual 2-descent runs, artifact upload, pinned canonical ResearchOs controller and replay verification.

The reproducible standard workflow now executes \(u=\pm24\) alongside the four small benchmark fibers. The two rank-four outcomes block a uniform rank ≤3 claim on the entire progression.

Source references: [PARI/GP elliptic curves documentation](https://pari.math.u-bordeaux.fr/dochtml/html/Elliptic_curves.html#ellrank); [Magma independent 2-Selmer specification](https://docs.magma-maths.org/v2.30-1/ArithmeticGeometry/EllipticCurvesOverQAndNumberFields/mordell-weil.html); [ResearchOs TECT specification](https://github.com/tltmgnt/ResearchOs/blob/main/TECT_SPEC.md); [MathOS 07 manuscript](BSD_CUBIC_DESCENT_INFINITE_UPPER_07.md).

**Research and AI disclosure:** ChatGPT designed the computational research workflow and wrote the code/documentation. Published mathematical theorems and original software are attributed to their respective authors. Neither automated tests nor a TECT replay should be misrepresented as five independent mathematical proofs or a peer-reviewed new theorem.
