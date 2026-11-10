# Topology compatibility and curriculum v2 — MathOS

Version 2 adapts the explicit-molecular-graph teaching pattern to this repository's actual role. This is documentation and a learning/decision framework; it introduces no mathematical engine, runtime dependency or operational permission.

## Repository decision

| Question | Repository-specific answer |
| --- | --- |
| Architectural role | foundational research workspace |
| Minimum useful mathematics | Dependency graphs; TDA only for an explicitly defined representation study |
| Relationships to preserve | Methods, captured activations, benchmark conditions and evidence lineage |
| Concrete operation / capstone | Read activation capture without downloading a model; specify the distance, baseline and permutation control needed before applying TDA |
| Necessity and scope boundary | A hidden-state vector is not a demonstrated reasoning mechanism; no new model download or paid run is required |

The decision is a source-based recommendation, not measured proof that a new specialty improves this repository. Start with the existing implementation and compare any proposed abstraction against a simpler alternative.

## Six-criterion compatibility scorecard

Complete one scorecard per proposed candidate and per concrete operation. Leave unmeasured entries unknown. Scores are human judgments from 0 (no fit) to 5 (strong evidenced fit); unknown is not zero. Do not sum an incomplete card. A total out of 30 is a heuristic, not adoption approval, and feasibility or necessity can veto a high total.

| Criterion | Score | Required evidence |
| --- | --- | --- |
| Structural compatibility | Not yet scored | Map the repository objects and the relationships above without losing direction, labels, units or missingness. |
| Transformation support | Not yet scored | Demonstrate the capstone operation on accepted and rejected inputs. |
| Invariant preservation | Not yet scored | State the property preserved and supply a counterexample or perturbation. |
| Computational feasibility | Not yet scored | Measure size, time and memory on bounded fixtures; record limits. |
| Integration compatibility | Not yet scored | Verify existing schemas, APIs and neighboring contracts remain compatible. |
| Mathematical necessity | Not yet scored | Compare with dependency graphs and explain the additional capability, if any. |

## Curriculum

Prerequisites: basic programming, sets, functions and graph vocabulary. Work in six competency-gated sessions, approximately 60–90 minutes each; empirical evaluation is a separate research activity.

| Session | Learning objective | Exercise | Completion evidence |
| --- | --- | --- | --- |
| 1. Model | Identify methods, captured activations, benchmark conditions and evidence lineage. | Draw a minimal valid example and one excluded relationship. | Annotated object/relation inventory with explicit assumptions. |
| 2. Contract | Distinguish schema validity from substantive correctness. | Trace validation and propose malformed, missing and boundary inputs. | Input-to-rejection table grounded in current source. |
| 3. Operation | Explain dependency graphs; tda only for an explicitly defined representation study. | Read activation capture without downloading a model; specify the distance, baseline and permutation control needed before applying TDA. | Hand trace compared with existing software, or a clearly labeled specification when no runtime exists. |
| 4. Preservation | State what a transformation must preserve. | Rename identifiers, reorder records, then alter one meaningful relation; predict each effect under the actual contract. | Separate invariant, expected change and unsupported transformation. |
| 5. Comparison | Justify mathematical necessity and cost. | Complete the six-criterion card for the existing approach and one proposed alternative; record unknowns honestly. | Evidence-backed recommendation with baseline and explicit veto conditions. |
| 6. Reproduction | Communicate the bounded result. | Reproduce the capstone using existing offline fixtures and record software version, inputs, outputs and limitations. | Reviewable notebook or report distinguishing computation, replay, independent evaluation and authorization. |

## Source-linked reading laboratory

The table is a guided selection of source lines, not an assertion that the whole repository is covered. Line numbers refer to the inspected source blob `0b54e4e5eae1bb1aab0f773f2b6523c6cba77db7` in [experiments/internal_reasoning/activation_capture.py](../../experiments/internal_reasoning/activation_capture.py). Recheck anchors after source changes.

| Line | Statement | Learning check |
| --- | --- | --- |
| [9](../../experiments/internal_reasoning/activation_capture.py#L9) | `def capture_activations(model_name, prompt):` | State the input/output contract and trace one normal and one failing case. |
| [16](../../experiments/internal_reasoning/activation_capture.py#L16) | `raise RuntimeError(` | Construct the triggering input and explain why rejection preserves the contract. |
| [45](../../experiments/internal_reasoning/activation_capture.py#L45) | `return {` | Predict the returned value and distinguish a computed result from authorization. |
| [46](../../experiments/internal_reasoning/activation_capture.py#L46) | `"schema_version": "1.0",` | Separate type, shape and value checks; test a missing field and an invalid value. |
| [56](../../experiments/internal_reasoning/activation_capture.py#L56) | `def main():` | State the input/output contract and trace one normal and one failing case. |
## Assessment and verification

A learner must explain the model, trace the capstone, identify a counterexample and state the scope boundary. Assess these four competencies equally; a numerical score cannot compensate for an unsupported scientific or operational claim.

Relevant existing checks:

- [tests/test_activation_capture.py](../../tests/test_activation_capture.py)
- [tests/test_internal_reasoning_adapter.py](../../tests/test_internal_reasoning_adapter.py)
- [tests/test_mathos_agents.py](../../tests/test_mathos_agents.py)

Follow [README](../../README.md) for environment and installed-package instructions. Read scripts before execution; source-reading exercises do not authorize provider calls, model downloads, live orders, hardware actions or messages. Synthetic fixtures establish software behavior only. This documentation change does not report those exercises as already executed.

## Interoperability and adoption gate

Retain explicit domain contracts. Shared assurance records should refer to domain evidence and its assumptions rather than relabeling graph reachability, homology, statistical calibration and epistemic acceptance as interchangeable quantities. The canonical ResearchOs controller remains owned by ResearchOs; this curriculum does not create another controller fork.

Adopt additional mathematics only after a versioned experiment demonstrates a useful operation, the scorecard has evidence, the simpler baseline is inadequate and existing conformance checks remain satisfied. A hidden-state vector is not a demonstrated reasoning mechanism; no new model download or paid run is required.
