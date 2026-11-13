"""Exact, narrowly scoped stress tests for proposed proof shortcuts.

No theorem prover and no Millennium counterexamples. Abstract-model witnesses
are distinguished from examples satisfying an actual problem's hypotheses.
Python 3.10+, standard library only.
"""
from dataclasses import asdict, dataclass
from fractions import Fraction
from itertools import permutations
from pathlib import Path
import json


@dataclass(frozen=True)
class Finding:
    problem: str
    tested_claim: str
    evidence_kind: str
    outcome: str
    witness: dict
    reasoning: str
    limitation: str
    next_obligation: str


# Exact sparse polynomials in x,y,z, used to verify the initial velocity field.
ZERO = (0, 0, 0)
def add(*polys):
    out = {}
    for p in polys:
        for k, v in p.items():
            out[k] = out.get(k, 0) + v
    return {k: v for k, v in out.items() if v}


def mul(p, q):
    out = {}
    for a, ca in p.items():
        for b, cb in q.items():
            k = tuple(x+y for x, y in zip(a, b))
            out[k] = out.get(k, 0) + ca*cb
    return {k: v for k, v in out.items() if v}


def neg(p):
    return {k: -v for k, v in p.items()}


def gaussian_derivative(p, axis):
    """Returns Q with d_axis(P exp(-r^2)) = Q exp(-r^2)."""
    derivative = {}
    for powers, coefficient in p.items():
        if powers[axis]:
            key = list(powers); key[axis] -= 1
            derivative[tuple(key)] = coefficient*powers[axis]
    x = [0, 0, 0]; x[axis] = 1
    return add(derivative, mul(p, {tuple(x): -2}))


def gaussian_field():
    # u = curl(0,0,-exp(-r^2)); all fields are smooth and rapidly decaying.
    u = [{(0, 1, 0): 2}, {(1, 0, 0): -2}, {}]
    div = add(*(gaussian_derivative(u[i], i) for i in range(3)))
    curl = [add(gaussian_derivative(u[2], 1), neg(gaussian_derivative(u[1], 2))),
            add(gaussian_derivative(u[0], 2), neg(gaussian_derivative(u[2], 0))),
            add(gaussian_derivative(u[1], 0), neg(gaussian_derivative(u[0], 1)))]
    helicity_density = add(*(mul(a, b) for a, b in zip(u, curl)))
    return u, div, curl, helicity_density


def ns_attack():
    _, div, omega, helicity = gaussian_field()
    if div or helicity or omega[2].get(ZERO) != -4:
        raise AssertionError('Exact Gaussian field certificate failed')
    return Finding('Navier-Stokes',
        'Helicity and dilation-preserved vortex topology alone bound vorticity magnitude for all smooth decaying divergence-free initial fields.',
        'EXACT_FIELD_AND_SCALING', 'SHORTCUT_REFUTED',
        {'field': 'u=(2y,-2x,0) exp(-(x^2+y^2+z^2))',
         'divergence_polynomial': {}, 'helicity_density_polynomial': {},
         'vorticity_at_origin': [0, 0, -4],
         'scale_examples': [{'lambda': n, 'absolute_vorticity_at_origin': 4*n*n,
                             'helicity': 0} for n in [1, 2, 10, 100]],
         'scaling_exponents_3d': {'vorticity_sup': 2, 'kinetic_energy': -1,
                                 'enstrophy': 1, 'helicity': 0}},
        'Positive dilation preserves vortex-line topology. The family u_lambda(x)=lambda*u(lambda*x) has identical zero helicity and |omega_lambda(0)|=4*lambda^2. Thus no finite bound depending only on these fixed invariants can hold on this family.',
        'Initial fields only, not a singular evolving solution. Does not reject estimates using additional quantitative hypotheses or all possible geometric approaches.',
        'Prove a quantitative bound with enough geometric and analytic information to close a continuation criterion.')


def complex_mul(a, b):
    return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])


def rh_attack():
    # z=(1+i)/sqrt(2); z^2=(1+i)^2/2=i. All arithmetic below is rational.
    square_numerator = complex_mul((1, 1), (1, 1))
    z_squared = tuple(Fraction(v, 2) for v in square_numerator)
    z_fourth = complex_mul(z_squared, z_squared)
    if z_squared != (0, 1) or z_fourth != (-1, 0):
        raise AssertionError('Root witness failed')
    return Finding('Riemann',
        'Evenness, real coefficients and strict positivity on the real axis force all zeros of an entire function to be real.',
        'EXACT_POLYNOMIAL_COUNTEREXAMPLE', 'SHORTCUT_REFUTED',
        {'polynomial': 't^4+1', 'nonreal_root': '(1+i)/sqrt(2)',
         'root_squared': [str(x) for x in z_squared],
         'root_fourth': [str(x) for x in z_fourth]},
        'The polynomial is even and >=1 on the real axis. The displayed nonreal z satisfies z^4+1=0 exactly.',
        'Not the zeta or xi function; only refutes a symmetry/positivity-only implication.',
        'Construct a noncircular spectral realization and prove the exact zero correspondence.')


def sat_polynomial(m):
    if not isinstance(m, int) or m < 0 or m > 10:
        raise ValueError('Exact expansion supports integer m from 0 through 10')
    p = {frozenset(): 1}
    for i in range(m):
        terms = [(frozenset([2*i]), 1), (frozenset([2*i+1]), 1),
                 (frozenset([2*i, 2*i+1]), -1)]
        q = {}
        for a, ca in p.items():
            for b, cb in terms:
                k = a | b
                q[k] = q.get(k, 0)+ca*cb
        p = {k: v for k, v in q.items() if v}
    return p


def sat_attack():
    counts = [len(sat_polynomial(m)) for m in range(9)]
    if counts != [3**m for m in range(9)]:
        raise AssertionError('Expansion count failed')
    return Finding('P-versus-NP',
        'Explicit expansion of the satisfaction polynomial always has polynomially many monomials.',
        'EXACT_EXPANSION_AND_GENERAL_COUNTING_ARGUMENT', 'SHORTCUT_REFUTED',
        {'formula': 'AND_i (x_i OR y_i) on disjoint pairs',
         'polynomial': 'PRODUCT_i (x_i+y_i-x_i*y_i)', 'counts_m_0_to_8': counts},
        'Each factor has three choices with distinct variable-pair supports. Different choices yield distinct monomials of coefficient +/-1. Hence there are exactly 3^m nonzero monomials for every m>=0.',
        'No lower bound for arbitrary SAT algorithms or compressed representations. Does not resolve P versus NP.',
        'Specify an algorithm and bound its full bit complexity; a topological invariant also needs an efficient construction and evaluation theorem.')


def ym_attack():
    # Abstract lattice spectral model, not a gauge theory or continuum construction.
    rows = []
    for n in [1, 2, 10, 100]:
        a = Fraction(1, n); lattice_gap = a*a
        rows.append({'n': n, 'spacing': str(a), 'dimensionless_gap': str(lattice_gap),
                     'physical_gap': str(lattice_gap/a)})
    return Finding('Yang-Mills',
        'A positive gap at every regulator value necessarily gives a positive limiting physical gap.',
        'EXACT_ABSTRACT_LIMIT_COUNTERMODEL', 'SHORTCUT_REFUTED',
        {'sequence': rows, 'physical_gap_formula': '1/n', 'limit': 0},
        'Let spacing a_n=1/n and dimensionless gap mu_n=a_n^2>0. The physical gap mu_n/a_n=1/n tends to zero despite positivity at each n.',
        'Abstract sequence, not Yang-Mills. No assertion that this sequence occurs in that theory; fixed topological sectors would not supply the missing energy estimate.',
        'Establish a nontrivial continuum theory and a strictly positive regulator-uniform physical gap.')


def rank(matrix):
    a = [[Fraction(v) for v in row] for row in matrix]
    if not a:
        return 0
    if any(len(row) != len(a[0]) for row in a):
        raise ValueError('Ragged matrix')
    r = 0
    for c in range(len(a[0])):
        pivot = next((i for i in range(r, len(a)) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        v = a[r][c]; a[r] = [x/v for x in a[r]]
        for i in range(len(a)):
            if i != r:
                v = a[i][c]; a[i] = [x-v*y for x,y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def bsd_attack():
    ranks = []
    for pairs in [1, 2, 4]:
        n = 2*pairs; j = [[0]*n for _ in range(n)]
        for k in range(0, n, 2):
            j[k][k+1] = 1; j[k+1][k] = -1
        ranks.append(rank(j))
    return Finding('Birch-Swinnerton-Dyer',
        'Existence of a nondegenerate alternating pairing alone determines the dimension of the underlying vector space.',
        'EXACT_LINEAR_ALGEBRA_COUNTERMODEL', 'ABSTRACT_SHORTCUT_REFUTED',
        {'nondegenerate_alternating_form_dimensions': ranks},
        'Block diagonal symplectic forms are nondegenerate in dimensions 2,4,8, and in every positive even dimension. Duality alone does not select one dimension.',
        'These vector spaces are not Selmer groups or elliptic curves; no counterexample to BSD or its actual arithmetic duality statements is claimed.',
        'Prove the precise analytic/arithmetic comparison; additional arithmetic input is indispensable.')


def hodge_attack():
    ambient = [[1, 0], [0, 1]]
    cycles = [[1, 0]]
    return Finding('Hodge',
        'Declaring a rational cohomological space to be of type (p,p) forces a specified cycle map onto it.',
        'EXACT_ABSTRACT_LINEAR_MAP_COUNTERMODEL', 'ABSTRACT_SHORTCUT_REFUTED',
        {'ambient_dimension': rank(ambient), 'declared_cycle_image_dimension': rank(cycles),
         'missing_vector': [0, 1]},
        'In Q^2, the image of q -> (q,0) misses (0,1), regardless of an assigned type label. Surjectivity does not follow from these abstract data.',
        'Not realized as the cycle map of a smooth projective variety. Thus this is not a Hodge counterexample and cannot refute arguments using additional geometric structure.',
        'Use the actual geometry to construct rational algebraic cycles and prove coverage.')


# Permutations composed as a(b(i)); exact group certificate for a weak topology proxy.
def compose(a, b):
    return tuple(a[b[i]] for i in range(len(a)))


def inverse(a):
    out = [0]*len(a)
    for i, v in enumerate(a): out[v] = i
    return tuple(out)


def even(a):
    return sum(a[i] > a[j] for i in range(len(a)) for j in range(i+1, len(a))) % 2 == 0


def a5_certificate():
    group = {a for a in permutations(range(5)) if even(a)}
    identity = tuple(range(5))
    inv = {a: inverse(a) for a in group}
    commutators = {compose(compose(compose(a,b), inv[a]), inv[b]) for a in group for b in group}
    # Commutators generate the derived subgroup; direct finite closure checks its size.
    subgroup = {identity}; frontier = [identity]
    while frontier:
        current = frontier.pop()
        for generator in commutators:
            nxt = compose(current, generator)
            if nxt not in subgroup:
                subgroup.add(nxt); frontier.append(nxt)
    return len(group), len(subgroup)


def poincare_attack():
    order, derived_order = a5_certificate()
    if (order, derived_order) != (60, 60):
        raise AssertionError('Perfect-group certificate failed')
    return Finding('Poincare',
        'Trivial abelianization of a fundamental group implies that the group is trivial.',
        'EXACT_FINITE_GROUP_COUNTERMODEL', 'WEAK_TOPOLOGICAL_PROXY_REFUTED',
        {'group': 'A5', 'order': order, 'commutator_subgroup_order': derived_order,
         'abelianization_order': order//derived_order},
        'A5 is nontrivial but equals its commutator subgroup. First homology detects the abelianization and cannot generally replace a simple-connectivity check.',
        'No closed three-manifold is constructed here, and no challenge to Perelman is implied. Refutes the group-theoretic shortcut only.',
        'Retain exact fundamental-group hypotheses and reconstruct the established geometric argument.')


ATTACKS = [bsd_attack, hodge_attack, ns_attack, sat_attack, poincare_attack, rh_attack, ym_attack]


def route_statuses(findings):
    """Propagate a challenge to its candidate shortcut route, never to the conjecture."""
    out = {}
    for finding in findings:
        if finding.problem in out:
            raise ValueError('Duplicate problem finding')
        if finding.outcome not in {'SHORTCUT_REFUTED', 'ABSTRACT_SHORTCUT_REFUTED',
                                   'WEAK_TOPOLOGICAL_PROXY_REFUTED'}:
            raise ValueError('Unsupported finding outcome')
        out[finding.problem] = {
            'tested_shortcut': 'CONTESTED', 'route_using_that_shortcut': 'CONTESTED',
            'original_proof_obligations': 'UNRESOLVED',
            'underlying_problem': 'EXTERNALLY_ESTABLISHED' if finding.problem == 'Poincare' else 'NO_STATUS_CHANGE_FROM_THIS_RUN',
            'next_obligation': finding.next_obligation}
    return out


def main(output_dir="."):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    from .gap_analysis import analyze, models
    from .certification_audit import exhaustive_check, graph_hash
    findings = [f() for f in ATTACKS]
    original_models = models()
    if {f.problem for f in findings} != set(original_models):
        raise ValueError('Adversarial suite does not cover the supplied model register')
    original_checks = {}
    for name, graph in original_models.items():
        result = analyze(graph, 'target')
        original_checks[name] = {
            'status': result['status'],
            'minimal_completion_sets': result['minimal_completion_sets'],
            'graph_sha256': graph_hash(graph),
            'check': exhaustive_check(graph, 'target', result['minimal_completion_sets'])}
    report = {'scope': 'Stress tests of seven precisely stated shortcuts; no automatic theorem discovery or Millennium solutions.',
              'formal_proof_assistant_checked': False, 'independent_external_review': False,
              'new_millennium_proofs': 0, 'findings': [asdict(f) for f in findings],
              'routes': route_statuses(findings), 'original_graph_checks': original_checks}
    (output_dir / 'adversarial_results.json').write_text(json.dumps(report, indent=2)+'\n')
    lines = ['# Topological adversarial analysis', '', report['scope'], '',
             'All findings below are scoped to the stated shortcut. Abstract witnesses do not satisfy the full geometric or arithmetic hypotheses of the Millennium Problems.', '',
             '| Problem | Evidence | Outcome |', '|---|---|---|']
    for f in findings:
        lines.append(f'| {f.problem} | {f.evidence_kind} | {f.outcome} |')
    for f in findings:
        lines += ['', '## '+f.problem, '', '**Tested claim:** '+f.tested_claim, '',
                  '**Result:** '+f.reasoning, '', '**Limit:** '+f.limitation, '',
                  '**Next obligation:** '+f.next_obligation]
    lines += ['', '## Reproduce', '', 'Python 3.10+ and standard library only.', '',
              '```sh', 'python -m unittest discover -s tests -p "test_proof_*.py" -v', 'python -m mathos.proof_analysis --output-dir artifacts/proof-analysis',
               '```', '',
              'This is a fixed suite of exact witnesses and authored arguments, not a general counterexample search engine. Passing tests establish program behavior; formal proof checking and external mathematical review remain outstanding.']
    (output_dir / 'adversarial_results.md').write_text('\n'.join(lines)+'\n')
    for f in findings:
        print(f.problem+': '+f.outcome+' ['+f.evidence_kind+']')


if __name__ == '__main__':
    main()
