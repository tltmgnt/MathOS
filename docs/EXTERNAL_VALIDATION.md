# External validation and domain expansion

Status: validation infrastructure implemented; external study not yet conducted.
No participant has been recruited or contacted by this change. A package passing the
audit below is ready for inspection, not scientifically validated.

## Evaluation tracks

The framework is extended here through domain-specific evaluation contracts. The
offline package auditor supports all four domain labels. Domain solvers, equipment
integration and causal inference engines are not added by this extension.

| Domain label | Bounded claim to evaluate | Comparator and reference | Outcomes and transfer boundary |
|---|---|---|---|
| mathematics | Dependency-assisted review reduces missed obligations | Existing expert review; independently adjudicated arguments and route sufficiency | Missed obligations, false positives, preparation and review time; test unseen proof families |
| computational | A proposed numerical method reproduces specified results | Pinned reference implementation and held-out inputs | Error tolerance, failures, runtime and full preparation cost; test changed inputs and environments |
| experimental | A specified intervention changes a measured outcome | Prospectively assigned control and independently calibrated measurements | Prespecified effect and uncertainty, adverse outcomes, exclusions; test another batch or instrument |
| operations | A bounded workflow change improves a specified bottleneck | Matched or randomized control where feasible; timestamped source records | Throughput, latency, errors and coordination cost; test another team or time period |

These are hypotheses, not demonstrated benefits. Graph structure, temporal capacity,
decision costs and empirical effects retain separate definitions and units. No common
"intelligence score" or automatic cross-domain promotion is introduced. A valid
mathematical derivation cannot substitute for empirical or causal evidence.

## External operator handoff

1. Choose one track and one falsifiable claim. Pin a full source commit, dependencies,
   comparator version, environment and commands. Record data access restrictions.
2. An independent operator supplies their affiliation, contribution and conflict
   disclosures through an appropriate private channel. A human reviewer verifies
   identity and independence against project authorship, funding, data and methods.
   Different model agents or repeated local runs do not supply this independence.
3. Complete the manifest template and a protocol: dataset version, independent unit,
   sample-size rationale, assignment/counterbalancing, practical threshold, uncertainty
   method, multiplicity policy, exclusions, timeouts and missing-data treatment.
   Use held-out references inaccessible to the candidate workflow.
4. Deposit the protocol with a verifiable external timestamp before outcome collection.
   Freeze source, analysis and references; record later amendments without overwriting
   the original. Have another reviewer adjudicate references before scoring candidates.
5. Collect real observations. Record baseline and assisted outputs, setup costs,
   failures and negative findings. For proof review use the formats and commands in
   [the evaluation guide](PROOF_REVIEW_EVALUATION.md); its paired importer produces
   descriptive results and does not itself establish causal benefit.
6. Run the prespecified analysis. Report uncertainty at the independent unit level;
   account for reviewer/case clustering and order effects. A domain statistician or
   qualified reviewer must assess the design before interpreting benefit.
7. Produce a replication report listing source, environment, deviations, raw-data
   availability, results and limitations. Retain restricted records privately; share
   only approved, deidentified material. A separate external reviewer signs a scoped
   acceptance or rejection with reasons and references.

## Audit a study package

Copy [the manifest template](../validation/manifest.template.json) into a study
directory as `manifest.json`. Fill its fields with genuine study details. Add files
for each required artifact role, with paths relative to that directory and SHA-256
digests. The preregistration artifact should include its external timestamp reference;
the replication report should include verifiable operator and review references.

```sh
python -m mathos.validation /path/to/study
python -m unittest discover -s tests -p 'test_validation.py' -v
```

Exit 1 means the package is incomplete or invalid. Exit 0 means only that required
metadata and artifact bytes are present and consistent. The auditor reads files only,
does not fetch URLs or execute submitted analysis, and does not authenticate identities,
establish preregistration timing, detect invented observations or assess scientific truth.
Run it on a stable copy; concurrent edits are outside its integrity guarantee.

## Acceptance and current blockers

| Milestone | Evidence required | Current state |
|---|---|---|
| Software package audit | Passing tamper, missing-data and path-boundary tests | Implemented and locally tested |
| Prospective study ready | Named operator, frozen protocol, dataset, comparator, sample-size rationale and external timestamp | Not supplied |
| Scoped external replication | Genuine observations, reproducible analysis and independently reviewed report | Not supplied |
| Broader framework support | Repeated representative evaluations, transfer tests and negative findings across domains | Not established |

Keep `docs/portfolio/STATUS.json` external-reproduction flags false until actual evidence
is reviewed. A future status change must cite the scoped claim, pinned commit, protocol,
operator verification, report and acceptance decision. A successful domain study does
not validate other domains, universal reasoning or deployment readiness.
