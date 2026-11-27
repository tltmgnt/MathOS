# MRA-X Ω / RE-X reproducibility release v0.1

Research-only source snapshot, Apache-2.0 (see repository LICENSE). This branch is not a theorem promotion or a resolution of P versus NP.

## Provenance and scope

Base source commit: f788454ad6871df5598fda7848ce3ed190081850 (REX-024D5F independent audit). The package covers normalized nine-group finite-domain inputs with width at most three, not arbitrary SAT. Domain cardinality m >= 2; n = 19m-7; dense input length L = n+1+2n^2+8*C(n,3); H = ceil(log2 L). The candidate physical transition envelope 8(H+1)^3 L^(8/3) is conditional on universal phase-bound premises. The arithmetic implication is not a proof of those premises.

The fixed source includes the producer, direct mask loader, finite-control forest and witness IR, physical bridge, single-tape compiler, descriptor quotient and original-format native interpreter. No production source, acceptance gate or main-branch file was modified.

## Environment and fast reproduction

Use Node.js 22, Python 3.11 and a C++17 compiler (g++ for native tests), as in historical CI. Run commands from repository root. No external npm packages are needed for the new reference harness. Obtain source via the repository's public branch research/mra-x-omega-reproducibility-v0.1, or an exact commit checkout/archive of that branch; record git rev-parse HEAD and tool versions.

    node --version
    python --version
    g++ --version
    node mathos/research/f038_rex_reproducibility_v01.js
    node mathos/research/f038_rex_width_three_independent_audit.js
    node mathos/research/f038_rex_width_three_cubic_bound_audit.js arithmetic
    python -m mathos.research.tga_f038_rex_024d5e

The new host-only harness uses an independent exhaustive domain oracle and an independently written width-three forest semijoin reference, plus the pinned source encoder/decoder, original witness validator and existing sharpened arithmetic checks. It does not execute the compiled RE-X machine. It checks decoded constraint semantics against the raw forbidden-tuple clauses, feasibility and witness validity, fixed and seeded cases, and malformed input. A structural refusal is not UNSAT. Expected counts: 30 cases, 296163 complete domain assignments examined, 8 SAT, 21 UNSAT, 1 satisfiable structural refusal (96 models), 4 malformed controls, 10018 arithmetic cases. The report must retain PNP_RESOLUTION_STATUS=OPEN and PROMOTION=NONE.

## IR and physical reproduction (separate from fast tests)

Run the existing differential reference/IR audits:

    node --max-old-space-size=6144 mathos/research/f038_rex_width_three_witness_ir_audit.js ir
    node --max-old-space-size=6144 mathos/research/f038_rex_width_three_witness_ir_audit.js larger
    node --max-old-space-size=6144 mathos/research/f038_rex_width_three_witness_ir_audit.js forced

For the worker clock checks:

    for c in empty edge-SAT edge-UNSAT m3-forced m4-forced; do
      node mathos/research/f038_rex_width_three_time_envelope_audit.js "$c" || exit 1
    done

For the native original-format physical replay, use a Linux environment with substantial memory and disk (the descriptor alone is 928445994 ASCII bytes; the compiler heap limit is 6 GiB). Full replay simulates very large transition counts; run the small domain suite before larger cases. Do not confuse simulator wall-clock time with physical transitions. These are source-based replay commands, not a claim that they were freshly executed at the release head.

    set -e
    out=$(mktemp -d)
    p=mathos/research/f038_rex_width_three
    node --max-old-space-size=6144 "${p}_admission.js" descriptor > "$out/machine.desc" 2> "$out/descriptor.json"
    node "${p}_admission.js" fixtures > "$out/all.fixtures"
    g++ -std=c++17 -O3 -Wall -Wextra "${p}_native.cpp" -o "$out/native"
    grep -E '^(empty|edge-SAT|edge-UNSAT|K5-refusal) ' "$out/all.fixtures" > "$out/small.fixtures"
    "$out/native" "$out/machine.desc" "$out/small.fixtures" > "$out/small.out"
    python -m mathos.research.f038_rex_width_three_native_verify "$out/small.fixtures" "$out/small.out"
    grep '^m4-forced ' "$out/all.fixtures" > "$out/four.fixtures"
    "$out/native" "$out/machine.desc" "$out/four.fixtures" > "$out/four.out"
    python -m mathos.research.f038_rex_width_three_native_verify "$out/four.fixtures" "$out/four.out"
    sha256sum "$out/machine.desc" "$out/all.fixtures"
    cat "$out/descriptor.json"

Expected quotient: 10922894 states, 928445994 descriptor bits, 32768682 transition entries. Historical domain-four physical regression: 299944027294 transitions, head 568801, span 574997, valid 69-bit witness. Historical original-format verifier distinguishes a witness from blank output; a blank output alone is not an UNSAT certificate.

## Historical evidence (not release-head CI)

- D5F independent arithmetic and host audit passed: https://github.com/tltmgnt/MathOS/actions/runs/45937466854 (base source commit above).
- D5D native domain-four and worker-envelope audit passed: https://github.com/tltmgnt/MathOS/actions/runs/45934056192/job/140293064394 (ffacc50caae015ff47d0b2939234729e2f87854a).
- New reference harness was run in an isolated JavaScript environment against source modules read from the pinned base, before committing it. The results above are that run, not new GitHub Actions evidence.

## Verification boundaries

Finite checks cannot establish universal physical refinement, the phase-bound premises, unrestricted SAT coverage, all finite cubic-stage admissions, or superiority over competing single-tape machines. The new reference solver is a host model, not an equivalent physical-machine performance baseline. No theorem status is changed. Report failures as failures; preserve the exact checkout, input, stdout, stderr and tool versions. Independent mathematical and machine-level review remains required.

PNP_RESOLUTION_STATUS = OPEN

PROMOTION = NONE
