# Standalone Curriculum: AI, Zeta Functions, and Topological Data Analysis

**ResearchOS / TECT-X — independent teaching edition**  
**Format:** six weeks · two 90-minute meetings per week (18 contact hours), plus 2–3 hours of independent work per week  
**Level:** advanced secondary / undergraduate bridge; optional advanced mathematics track  
**Language:** English · **Software:** Python 3.11+ standard library only (optional)  
**Status:** instructional / mathematical-literacy curriculum; **not** a proof of the Riemann hypothesis, BSD, or a Selmer-infinitude theorem

## Guiding question

**Can a million AI-assisted computations settle a mathematical statement that quantifies over infinitely many cases?** Students learn to distinguish exploration, reproducibility, a counterexample, a theorem with a complete proof, and claims that remain open.

The question was motivated by the user-supplied screenshot of the video [*AI & Math: Solving Riemann Hypothesis by Brute Force? #shorts*](https://www.youtube.com/watch?v=M7eQUHH-oWI), **Superintelligence**, published March 21, 2026. Only the title and screenshot-visible description inform this course; the full audio/transcript was not reviewed. The course is not sponsored by or endorsed by the video's creator and does not copy its video or transcript.

This curriculum is **fully standalone**. A teacher or learner needs only this directory; no MathOS runtime, TECT-X dataset, one-million-variant experiment, internet connection, special package, or research repository knowledge is required. The external video and advanced references are optional enrichment.

## Learning outcomes

By the end, learners can:

1. State a universal mathematical assertion and explain why finitely many verified instances do not establish it.
2. Distinguish the Riemann, Hurwitz, finite graph spectral, Ihara, and Artin–Mazur dynamical zeta functions by **definition, domain, and underlying object**.
3. Verify exact spectral-zeta identities for cycles and prove that adaptive Ihara probes can erase parameter information.
4. Compute small Vietoris–Rips complexes and their \(\beta_0\) and \(\beta_1\) using boundary maps over \(\mathbb F_2\).
5. Explain the distinction between topology of a graph, its zeta function, and a point cloud of measured features.
6. Run controlled computational experiments with exact known answers, positive/negative controls, sensitivity analysis, and a reproducibility record.
7. Write an honest, checkable **claim–evidence–gap** assessment rather than promoting a numerical pattern to a theorem.

## Prerequisites and accessibility

Essential: algebra, functions, exponentials and logarithms, elementary geometry, and comfort with quantifiers (for all / there exists). We introduce every special function and topology term used in assessed exercises. Optional mathematical depth: complex numbers, eigenvalues, finite graphs, linear algebra over \(\mathbb F_2\), and Python.

**No-code route:** all exercises involving the included Python program have parallel hand-computable cases; learners can complete the entire curriculum without coding. **Code route:** run the included standard-library lab and unit tests; no pip installation.

## Six-week scope and sequence

| Week | Meeting A (90 min) | Meeting B (90 min) | Evidence collected |
|---|---|---|---|
| 1. Proof versus enumeration | Quantifiers, evidence hierarchy, finite testing | Design a finite-test counterexample and limitations paragraph | Proof-gap worksheet |
| 2. Zeta taxonomy | Riemann and Hurwitz series in \(\Re(s)>1\) | Spectral, Ihara and dynamical zeta definitions | Five-family definition chart |
| 3. Exact bridges | Cycle graph eigenvalues and spectral values | Closed forms, rescaling and rigorous vs numerical identities | Exact calculation sheet |
| 4. Identifiability | Cycle Ihara zeta; fixed vs adaptive probing | Graph topology vs descriptor topology | Alias proof and revised experiment |
| 5. Persistent homology | VR filtration, \(\beta_0,\beta_1\), filled triangles | Square/circle/line controls; boundary ranks | Hand-worked filtration and lab log |
| 6. Research integrity | Stability, permutations, precision and pre-registration | Capstone defense: claim–evidence–gap with peer review | Final report and revision |

Detailed timed lessons: [LESSONS.md](LESSONS.md). Student assignments: [EXERCISES.md](EXERCISES.md). Complete instructor solutions and marking guidance: [INSTRUCTOR_KEY.md](INSTRUCTOR_KEY.md).

## Instructional method

Each 90-minute meeting follows this default structure: 10 minutes retrieval and misconception check, 20 minutes direct concept instruction, 30 minutes worked individual or pair tasks, 20 minutes evidence/gap review, and 10 minutes an exit ticket. The detailed plans vary this schedule where helpful. Use exact small models **before** any large-scale calculation. Do not claim that missing a homology loop, observing a large sample, or verifying many numerical zeros proves RH.

### Assessment plan

| Component | Weight | Requirement |
|---|---:|---|
| Weekly practice (Weeks 1–5) | 25% | At least one complete worked answer per week |
| Exact mathematical arguments | 25% | Cycle identities, alias counterexample, and finite-field boundary reasoning |
| Reproducibility mini-lab | 20% | Input, algorithm, controls, outputs, and limitations |
| Week 6 capstone report and defense | 30% | A bounded result and its explicit unclosed proof obligations |

**Passing standard:** at least 70/100 overall and no claim that finite computation proves an infinite theorem. A learner making that category error must correct the capstone before certification, regardless of numerical score.

Capstone deliverable: 1,200–1,800 words or a 10–12 minute presentation with a one-page reproducibility note, including a definition of the mathematical object, one exact argument, one finite computational experiment (or a hand-computed analogue), an adversarial control, and a falsifiable open gap. See [EXERCISES.md](EXERCISES.md) for the checklist and [INSTRUCTOR_KEY.md](INSTRUCTOR_KEY.md) for grading anchors.

## Self-contained lab

From this directory:

```sh
python lab.py
python lab.py --radius 1
python -m unittest discover -s . -p 'test_lab.py' -v
```

The lab computes small cycle spectral sums, closed-form checks, fixed/adaptive Ihara probes, and a 4-point square's Vietoris–Rips Betti numbers. Its only imports are from the Python standard library; no network and no proprietary data. The program is a **finite learning tool**, not a zeta-zero finder.

## Materials and reference boundaries

- **Primary curriculum:** this README, [LESSONS.md](LESSONS.md), [EXERCISES.md](EXERCISES.md), [INSTRUCTOR_KEY.md](INSTRUCTOR_KEY.md), [lab.py](lab.py), and [test_lab.py](test_lab.py). All instructional mathematics needed for assessment is reproduced inside these files.
- **Motivational video (optional):** [Superintelligence, *AI & Math: Solving Riemann Hypothesis by Brute Force? #shorts*](https://www.youtube.com/watch?v=M7eQUHH-oWI) (March 21, 2026). Source context is limited to the screenshot-visible description; not a proof source.
- **Optional deeper reading:** [NIST DLMF: Hurwitz zeta](https://dlmf.nist.gov/25.11), [NIST DLMF: Riemann zeta](https://dlmf.nist.gov/25.2), and standard treatments of Ihara graph zeta, persistent homology, and Li's criterion.

### Scope guardrail

**The Riemann hypothesis concerns actual nontrivial zeros of the analytically continued Riemann zeta function**, not arbitrary functions named zeta, graph cycles, numerical plots, synthetic zero lists, or topology of a feature point cloud. The course neither tests the RH in full nor claims to solve it. Its connection to Birch–Swinnerton-Dyer or elliptic-curve 2-Selmer groups is methodological (proof versus computation) rather than a proved mathematical bridge.

**Suggested certificate wording:** “Completed the standalone AI, Zeta Functions & TDA course; can evaluate the limits of numerical evidence and provide reproducible bounded mathematical examples.” Not “proved RH” or “established a new zeta theorem.”


## Two-valley terrain control

Run `python curriculum/tect_x_zeta_tda_standalone/terrain.py` from the repository root. The JSON includes the integer-metre grid, endpoints, connectivity, and result. Follow the middle row to exhibit a path whose maximum is 140 m. Every four-neighbour path must cross column 2, whose minimum is 140 m. These two bounds prove the merge elevation for this grid. Exactly two local minima are born, at 100 and 110 m, so the younger component persists for 30 m.

The solver computes a connection level between marked cells. Interpreting the difference as a persistence lifetime requires knowing which component dies at the merge. Missing heights exclude paths through those cells. A disconnected result describes the observed grid only. The tests independently flood each sublevel set, remove the saddle, and vary diagonal connectivity. These checks establish a finite synthetic baseline. Ground elevations, mapped saddle locations, and survey accuracy require georeferenced data and independent validation.

## Choose the next measurement

Run the lab as above and inspect the omission study in the JSON report. It masks each observed cell except the two endpoints, restores it, and recalculates the threshold with the original adjacency. Coordinates are zero-based row and column. Loss of every observed path ranks first, followed by the largest increase in the original units. The report lists all tied leaders in row order. When all changes are zero it suggests investigating a plausible joint omission. If the baseline is already disconnected it asks which missing observations could bridge the gap.

Before viewing the ranking, predict the most influential cell. Compare your prediction with the complete ranking, choose a flagged assumption, and record what independent measurement or adjacency check would resolve it. This exhaustive single-omission exercise is intended for small synthetic grids. A high rank measures sensitivity within the fixture; field accuracy and market outcomes require independent observations.

Instructor key: on the terrain fixture, either (1, 1) or (1, 3) raises the pass from 140 m to 160 m. Both outrank the central saddle omission (150 m).
