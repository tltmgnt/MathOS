"""Ω-R3B measurement infrastructure; no architectural superiority is assumed."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import combinations
import hashlib
import json
import math
import random
from statistics import mean, stdev
from typing import Mapping, Protocol

COMPONENTS = ('tga', 'dti', 'hedgeops', 'evidence')
BASELINES = {'B0': (), 'B1': ('tga',), 'B2': ('dti',),
             'B3': ('hedgeops',), 'B4': ('evidence',),
             'B5': COMPONENTS, 'B6': COMPONENTS}
CONDITIONS = ('complete', 'missing_structure', 'temporal_disruption',
              'economic_uncertainty', 'conflicting_incentives',
              'incomplete_evidence', 'adversarial', 'simultaneous_constraints')
FIDELITY_DIMENSIONS = ('functional', 'mathematical', 'behavioral',
                       'integration', 'operational')


def finite(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('Expected a finite number')
    return value


def unit(value):
    if not 0 <= finite(value) <= 1:
        raise ValueError('Expected a score in [0, 1]')
    return value


def weighted_score(scores: Mapping[str, float], weights: Mapping[str, float]):
    if not scores or scores.keys() != weights.keys():
        raise ValueError('Scores and weights must have identical nonempty dimensions')
    if not math.isclose(sum(unit(w) for w in weights.values()), 1, abs_tol=1e-9):
        raise ValueError('Weights must sum to one')
    return sum(unit(scores[k]) * weights[k] for k in scores)


def replication_fidelity(scores, weights):
    if set(scores) != set(FIDELITY_DIMENSIONS):
        raise ValueError('All five fidelity dimensions are required')
    return weighted_score(scores, weights)


def replication_resistance(rf, nrp, integration_fidelity, weights):
    """NRP normalization and fidelity rubrics must be preregistered externally."""
    return weighted_score({'rf': 1-unit(rf), 'nrp': 1-unit(nrp),
                           'if': 1-unit(integration_fidelity)}, weights)


def advantage(integrated, separated, *, higher_is_better=True):
    finite(integrated)
    finite(separated)
    sign = 1 if higher_is_better else -1
    delta = sign * (integrated-separated)
    return {'advantage': delta, 'separation_loss': delta,
            'relative_advantage_pct': 100*delta/abs(separated) if separated else None,
            'relative_separation_loss_pct': 100*delta/abs(integrated) if integrated > 0 else None}


def interaction(joint, first, second, baseline, *, higher_is_better=True):
    return (1 if higher_is_better else -1) * (finite(joint)-finite(first)-finite(second)+finite(baseline))


def factorial_design():
    """All 16 subsets, including B0 and the full integrated system."""
    return tuple(group for n in range(5) for group in combinations(COMPONENTS, n))


@dataclass(frozen=True)
class LayerResult:
    representation: Mapping
    claims: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    disposition: str = 'defer'

    def __post_init__(self):
        if self.disposition not in {'accept', 'reject', 'defer', 'revise'}:
            raise ValueError('Unknown disposition')


class IntelligenceLayer(Protocol):
    """TGA S=(V,E,D,C,B,A), DTI T=(C,F,K,I,R,X), HedgeOps and evidence adapters.

    A result is a proposal, never an automatic knowledge promotion. Implementations
    must route acceptance through their independently evaluated evidence policy.
    """
    def evaluate(self, task: Mapping, shared_state: Mapping) -> LayerResult: ...


@dataclass(frozen=True)
class Observation:
    implementation: str
    task_id: str
    trial: int
    condition: str
    metrics: Mapping[str, float]

    def __post_init__(self):
        if not self.implementation.strip() or not self.task_id.strip():
            raise ValueError('Implementation and task identifiers are required')
        if type(self.trial) is not int or self.trial < 0 or self.condition not in CONDITIONS:
            raise ValueError('Invalid trial or condition')
        if not self.metrics or any(not k.strip() for k in self.metrics):
            raise ValueError('Named metrics are required')
        for value in self.metrics.values():
            finite(value)


def paired_comparison(reference, replica, *, higher_is_better=True, seed=0, resamples=2000):
    """Paired bootstrap over independent experimental units, not correlated rows.

    Missing units are rejected. Callers must aggregate within-unit repeated tasks
    before invoking this function. CI is percentile, two-sided 95%.
    """
    if reference.keys() != replica.keys() or len(reference) < 2:
        raise ValueError('At least two identical paired units are required; no silent deletion')
    if type(resamples) is not int or resamples < 100:
        raise ValueError('At least 100 bootstrap resamples required')
    sign = 1 if higher_is_better else -1
    delta = [sign*(finite(reference[k])-finite(replica[k])) for k in sorted(reference)]
    rng = random.Random(seed)
    boot = sorted(mean(rng.choices(delta, k=len(delta))) for _ in range(resamples))
    sd = stdev(delta)
    return {'n': len(delta), 'mean_difference': mean(delta), 'standard_deviation': sd,
            'ci95': [boot[int(.025*(resamples-1))], boot[int(.975*(resamples-1))]],
            'paired_effect_size_dz': mean(delta)/sd if sd else None,
            'seed': seed, 'resamples': resamples, 'missing_data': 'reject'}


def holm_adjust(p_values):
    """Holm family-wise correction; p-values supplied by a justified test."""
    ordered = sorted((unit(p), name) for name, p in p_values.items())
    result, previous = {}, 0.0
    for i, (p, name) in enumerate(ordered):
        previous = max(previous, min(1., (len(ordered)-i)*p))
        result[name] = previous
    return result


REQUIRED_METADATA = {'dataset_version', 'dataset_split', 'model_version', 'configuration',
                     'seed', 'environment', 'timestamp', 'source_provenance',
                     'scenario', 'access_log', 'personnel', 'tools', 'time_budget',
                     'compute_budget', 'external_dependencies'}


def write_record(path, observations, metadata):
    """Persist raw observations with provenance and a canonical SHA-256 digest."""
    if REQUIRED_METADATA - metadata.keys():
        raise ValueError('Missing metadata: '+', '.join(sorted(REQUIRED_METADATA-metadata.keys())))
    if metadata['scenario'] not in {'A', 'B', 'C', 'D'}:
        raise ValueError('Unknown reconstruction scenario')
    if metadata['dataset_split'] not in {'development', 'validation', 'hidden', 'adversarial', 'operational'}:
        raise ValueError('Unknown dataset split')
    rows = list(observations)
    keys = [(r.implementation, r.task_id, r.trial, r.condition) for r in rows]
    if not rows or len(keys) != len(set(keys)):
        raise ValueError('Empty or duplicate observations')
    payload = {'schema_version': '1.0', 'status': 'proposed_empirical_validation_required',
               'metadata': metadata, 'observations': [asdict(r) for r in rows]}
    canonical = json.dumps(payload, sort_keys=True, separators=(',', ':'), allow_nan=False)
    payload['sha256'] = hashlib.sha256(canonical.encode()).hexdigest()
    with open(path, 'w', encoding='utf-8') as stream:
        json.dump(payload, stream, indent=2, sort_keys=True, allow_nan=False)
    return payload


class BenchmarkSystem(Protocol):
    def evaluate(self, task: Mapping, *, seed: int, budget: Mapping) -> Mapping[str, float]: ...


def run_matched(systems: Mapping[str, BenchmarkSystem], tasks, *, trials, seed, budget):
    """Run B0–B6 against identical isolated inputs and declared budgets.

    Adapters must enforce resource/time limits in their execution environment.
    This in-process runner cannot sandbox untrusted code or verify independence.
    Ground truth must remain in a separate evaluator owned by the adapter operator.
    """
    from copy import deepcopy
    if set(systems) != set(BASELINES):
        raise ValueError('Exactly B0 through B6 must be supplied')
    if type(trials) is not int or trials < 1:
        raise ValueError('Positive trial count required')
    tasks = list(tasks)
    ids = [task['task_id'] for task in tasks]
    if not tasks or len(ids) != len(set(ids)):
        raise ValueError('Nonempty uniquely identified tasks required')
    for task in tasks:
        if task['condition'] not in CONDITIONS:
            raise ValueError('Unknown condition')
    rows = []
    for trial in range(trials):
        for task in tasks:
            for name in sorted(systems):
                metrics = systems[name].evaluate(deepcopy(task['input']), seed=seed+trial,
                                                 budget=deepcopy(budget))
                rows.append(Observation(name, task['task_id'], trial, task['condition'], dict(metrics)))
    return rows
