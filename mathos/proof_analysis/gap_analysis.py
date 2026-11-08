"""Proof-dependency bookkeeping, not a theorem prover. Python 3.10+, stdlib only.

Edges describe user-authored sufficient proof routes. Computed sets are minimal
unresolved obligations RELATIVE TO THIS MODEL, not mathematical necessity.
Run: python -m mathos.proof_analysis --output-dir artifacts/proof-analysis; python -m unittest discover -s tests -p "test_proof_*.py" -v
"""
from dataclasses import dataclass
from itertools import product
import json
from pathlib import Path


@dataclass(frozen=True)
class Claim:
    label: str
    state: str  # established_external, open, derived
    routes: tuple[tuple[str, ...], ...] = ()  # OR of AND dependencies
    note: str = ''


def minimal(sets):
    unique = set(sets)
    return sorted((s for s in unique if not any(t < s for t in unique)),
                  key=lambda s: (len(s), sorted(s)))


def analyze(graph, target):
    # Validate the whole graph, including unused alternative routes.
    seen, active = set(), set()
    def validate(k):
        if k not in graph:
            raise ValueError('Missing dependency: ' + k)
        if k in active:
            raise ValueError('Dependency cycle: ' + k)
        if k in seen:
            return
        c = graph[k]
        if c.state not in {'established_external', 'open', 'derived'}:
            raise ValueError('Unknown state: ' + c.state)
        if c.state == 'derived' and (not c.routes or any(not r for r in c.routes)):
            raise ValueError('Derived claims need nonempty proof routes')
        if c.state != 'derived' and c.routes:
            raise ValueError('Leaf states cannot carry proof routes')
        active.add(k)
        for route in c.routes:
            for d in route:
                validate(d)
        active.remove(k)
        seen.add(k)
    for k in graph:
        validate(k)
    memo = {}
    def obligations(k):
        if k in memo:
            return memo[k]
        c = graph[k]
        if c.state == 'established_external':
            answer = [frozenset()]
        elif c.state == 'open':
            answer = [frozenset([k])]
        else:
            candidates = []
            for route in c.routes:
                for combination in product(*(obligations(d) for d in route)):
                    candidates.append(frozenset().union(*combination))
            answer = minimal(candidates)
        memo[k] = answer
        return answer
    sets = obligations(target)
    required = set.intersection(*(set(s) for s in sets)) if sets else set()
    return {'target': target, 'status': 'EXTERNAL_RESULT_OR_ROUTE_CLOSED' if frozenset() in sets else 'BLOCKED',
            'minimal_completion_sets': [sorted(s) for s in sets],
            'common_to_all_modeled_routes': sorted(required),
            'claims': {k: {'label': c.label, 'state': c.state, 'routes': c.routes,
                           'note': c.note} for k, c in graph.items()}}


def model(name, gaps, note):
    graph = {'background': Claim('Established mathematical background (externally accepted)',
                                'established_external', note='Assumed; not independently proof-checked here.')}
    for k, label in gaps:
        graph[k] = Claim(label, 'open')
    graph['target'] = Claim(name, 'derived', (tuple(['background'] + [k for k, _ in gaps]),), note)
    return graph


def models():
    return {
      'Birch-Swinnerton-Dyer': model('Full BSD for elliptic curves over Q', [
          ('analytic_selmer', 'Prove the general complex analytic rank / Selmer corank comparison'),
          ('sha_finiteness', 'Prove finiteness of the Tate-Shafarevich group'),
          ('leading_term', 'Prove the full leading-term identity with specified normalizations')],
          'Full leading-term identity overlaps the other obligations. Graph tracks work packages, not independent axioms.'),
      'Hodge': model('Rational Hodge conjecture', [
          ('primitive_cycles', 'Construct rational algebraic cycle representatives for all remaining primitive rational Hodge classes on all smooth projective varieties'),
          ('reduction', 'Prove coverage of all classes from primitive cases, including rationality and algebraicity of every reduction')],
          'The primitive-class obligation remains a major geometric theorem, not an implemented construction.'),
      'Navier-Stokes': model('Unforced global smoothness branch', [
          ('critical_bound', 'Prove an a priori L^4_t L^6_x bound up to every finite candidate breakdown time for all admissible data')],
          'Uses the established continuation criterion. This is one sufficient branch, not a review of announced forced-breakdown proofs.'),
      'P-versus-NP': model('P=NP via SAT', [
          ('sat_correctness', 'Supply a fully specified deterministic SAT algorithm and prove correctness'),
          ('sat_runtime', 'Prove polynomial worst-case total bit complexity, including all intermediate representations')],
          'Only a P=NP route is modeled. Failure does not imply P!=NP. Explicit expansion route is refuted separately.'),
      'Poincare': {
          'published': Claim('Poincare conjecture via established Perelman proof', 'established_external',
                             note='External established result; not newly verified by this program.'),
          'reconstruction': Claim('Supply a complete independently checked reconstruction of the proof', 'open'),
          'target': Claim('Our independent proof reconstruction', 'derived', (('reconstruction',),))},
      'Riemann': model('Riemann hypothesis via spectral realization', [
          ('operator', 'Construct an independently defined self-adjoint operator with a rigorous domain'),
          ('zero_identity', 'Prove a spectral/determinant identity accounting for every nontrivial zero with multiplicity')],
          'The identity must be noncircular and include any determinant regularization and nonvanishing factors.'),
      'Yang-Mills': model('Four-dimensional Yang-Mills existence and mass gap', [
          ('continuum', 'Construct a nontrivial continuum limit for each required compact simple gauge group'),
          ('axioms', 'Verify the required quantum-field axioms and reconstruction hypotheses'),
          ('uniform_gap', 'Prove regulator-uniform bounds yielding a strictly positive physical spectral gap')],
          'These are coupled work packages. No continuum construction or gap proof is supplied.')}


def main(output_dir="."):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results = {name: analyze(g, 'target') for name, g in models().items()}
    results['Poincare']['established_result'] = analyze(models()['Poincare'], 'published')['status']
    payload = {'scope': 'Author-modeled proof dependencies; no theorem proving or new mathematical certification.',
               'sources': ['https://github.com/tltmgnt/ResearchOs/blob/main/core.py',
                           'https://github.com/tltmgnt/ResearchOs/blob/main/TECT_SPEC.md'],
               'integration': 'MathOS repository implementation inspired by ResearchOS; not the ResearchOS controller or a theorem prover.',
               'results': results,
               'sat_counterexample': {'formula': 'AND_i (x_i OR y_i), disjoint variable pairs',
                 'polynomial': 'PRODUCT_i (x_i + y_i - x_i*y_i)',
                 'exact_monomials': '3**m',
                 'proof': 'Each factor has three nonzero terms on disjoint variables; choices yield distinct monomials, so no cancellation is possible.',
                 'counts_m_1_to_8': [3**m for m in range(1, 9)]}}
    (output_dir / 'results.json').write_text(json.dumps(payload, indent=2) + '\n')
    lines = ['# Proof dependency gap analysis', '', payload['scope'], '',
             'These are sufficient-route work packages, not minimal mathematical axioms. Counts are not difficulty scores.', '',
             '| Problem / attempted route | Status | Unresolved work packages |', '|---|---|---|']
    for name, r in results.items():
        lines.append(f"| {name} | {r['status']} | {len(r['minimal_completion_sets'][0])} |")
    for name, r in results.items():
        lines += ['', '## ' + name, '', r['claims']['target']['note'] or 'Independent reconstruction remains incomplete.', '']
        for completion in r['minimal_completion_sets']:
            lines += ['- ' + r['claims'][k]['label'] for k in completion]
    lines += ['', 'Poincare is externally established; only our independent reconstruction is blocked.', '',
              '## SAT route rejection', '', payload['sat_counterexample']['proof'],
              'Exact monomial count: 3**m. This rejects explicit expansion as a generally polynomial-size step; it does not resolve P versus NP.', '',
              '## Reproduce', '', '`python -m unittest discover -s tests -p "test_proof_*.py" -v`', '', '`python -m mathos.proof_analysis --output-dir artifacts/proof-analysis`', '',
              'No numerical confidence, independent-verification Boolean, or graph status is treated as mathematical proof.']
    (output_dir / 'results.md').write_text('\n'.join(lines) + '\n')
    for name, r in results.items():
        print(f"{name}: {r['status']}; {len(r['minimal_completion_sets'][0])} unresolved work packages")


if __name__ == '__main__':
    main()
