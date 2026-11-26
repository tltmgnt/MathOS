# MRA-X Curriculum Research Agent

The 24-module curriculum across MATH, TGA, MRA, RE-X, AI, VER, OPT and RES is now an executable dependency-aware research registry. The original 52-week educational curriculum remains a proposed syllabus; passing these narrow automated labs is not mastery or a qualification.

## Process
Observe the module and prerequisites → plan its registered lab → execute the bounded deterministic computation → verify acceptance conditions → arbitrate LAB_PASS, LAB_FAIL, BLOCKED or OPEN_RESEARCH → record evidence and recommend dependency-ready research tasks. An optional language model tests advisory planning only; its output cannot authorize proof promotion or arbitrary code execution. Learning in the held-out lab selects strategies using training observations and evaluates on disjoint seeds; the SQLite ledger stores run evidence but does not train a model or adapt across runs.

## Run
From repository root, Python 3.11+, standard library only for offline mode:

    python tools/mra_x_curriculum_agent.py --output curriculum-evidence.json --ledger curriculum.sqlite

Use fresh output filenames and a trusted ledger directory. Use --seed for another bounded run. Optional --model YOUR_AVAILABLE_MODEL requires the OpenAI SDK and API key; live API execution was not tested. AI-503's offline lab verifies fallback only. The command returns failure on failed or blocked executable labs; open research items remain separately disclosed.

## Local results (seed 38019)
18 bounded labs passed; 6 open research items; no failed or blocked executable labs. 52 instances / 208 candidate checks in the nested gap campaign, 729 finite projection identities, 22 synthetic held-out candidate checks. The training-selected strategy required 2,195 logical assignments versus 2,152 for min-fill on the held-out sample (43 more, not a gain). Exact replay, report digest, injected failure propagation and SQLite duplicate prevention also checked. The source blob matches the locally executed file.

## Research frontier
Dependency-ready: REX-402 actual single-tape encoding, VER-603 mechanized proof, OPT-703 incremental repair, RES-802 external matched benchmark. REX-403 and RES-803 retain unmet prerequisites. The unary-increment toy tape lab does not establish physical RE-X integration. No general theorem, competitive superiority, self-modifying agent or continuous service is claimed.
