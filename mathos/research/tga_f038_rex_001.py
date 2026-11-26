"""RE-X-001: backward acceptance contract and forward evidence frontier.

No promotion; the codec primitives do not implement the separator solver.
"""
import json
from mathos.proof_analysis.gap_analysis import Claim
from mathos.proof_analysis.rex import inspect_routes, authorize_one, self_test
from mathos.research.tga_pnp_resolution_gap import graph as global_graph
from mathos.research.tga_f038_sep_003 import report as sep_report


def graph():
    g = {}
    tasks = {
        'REX-01': ('Raw normalized recognition and actual witness semantics',
                   'SEP-003 host tests; independent review open'),
        'REX-02': ('Raw binary to full product-track layout',
                   'Fixed 18-state binary repetition primitive tested; full layout conversion open'),
        'REX-03': ('Fixed sequential bit implementation with production batch cost',
                   'Host implementation and analytical ledger only'),
        'REX-04': ('Product-track witness projection and contiguous halt output',
                   'Fixed 18-state repetition packer tested; general output projection open'),
        'REX-05': ('Same fixed three-symbol single-head machine composition',
                   '36-state payload codec composed; solver compilation absent'),
        'REX-06': ('Worst-case same-program clock and eligible description',
                   'No complete solver descriptor or exact-stage guarantee'),
        'REX-07': ('Independent mathematical and implementation review',
                   'Outstanding'),
        'REX-08': ('Unrestricted coverage or distinct uniform route',
                   'Restricted structural admission does not establish uniform coverage'),
    }
    for k, (label, note) in tasks.items():
        g[k] = Claim(label, 'open', note=note)
    g['interface'] = Claim('Original tape interface', 'derived', (('REX-01', 'REX-02', 'REX-04'),))
    g['machine'] = Claim('Integrated witness machine for admitted SAT inputs', 'derived',
                         (('interface', 'REX-03', 'REX-05'),))
    g['restricted_stage'] = Claim('Eventual exact cubic-stage coverage on admitted SAT inputs',
                                  'derived', (('machine', 'REX-06'),),
                                  'Sufficient authored route; correctness and bound must use the same program')
    g['restricted_evidence'] = Claim('Restricted route evidence readiness', 'derived',
                                     (('restricted_stage', 'REX-07'),))
    g['uniform_evidence'] = Claim('Uniform route evidence readiness', 'derived',
                                  (('restricted_evidence', 'REX-08'),))
    return g


def report():
    local = {k: inspect_routes(graph(), k) for k in
             ('interface', 'machine', 'restricted_stage', 'restricted_evidence', 'uniform_evidence')}
    glob = global_graph()
    global_routes = {k: inspect_routes(glob, k) for k in
                     ('direct_sat', 'selector_route', 'certificate_route', 'negative',
                      'mathematical_resolution', 'resolution_evidence_gate')}
    old = sep_report()
    assert all(r['status'] == 'BLOCKED' for r in (*local.values(), *global_routes.values()))
    assert all(r['status'] == 'BLOCKED' for r in old['local_routes'].values())
    assert old['PNP_RESOLUTION_STATUS'] == 'OPEN' and old['PROMOTION'] == 'NONE'
    assert len(global_routes['mathematical_resolution']['minimal_completion_sets']) == 4
    assert global_routes['resolution_evidence_gate']['common_to_all_modeled_routes'] == ['independent_review']
    assert local['restricted_evidence']['minimal_completion_sets'] == [
        ['REX-%02d' % i for i in range(1, 8)]]
    assert local['uniform_evidence']['minimal_completion_sets'] == [
        ['REX-%02d' % i for i in range(1, 9)]]
    # No automatic follow-on mission after the bounded user-requested work.
    decision = authorize_one(local['restricted_evidence'], {}, 0)
    return {
        'system': 'MRA-X-TGA-2.0 + RE-X',
        'mission': 'F038-REX-001',
        'PNP_RESOLUTION_STATUS': 'OPEN', 'PROMOTION': 'NONE',
        'scope': 'BIDIRECTIONAL_AUTHORED_ROUTES_AND_PAYLOAD_CODEC_ONLY',
        'local_routes': local, 'global_routes': global_routes,
        'inherited_local_routes': old['local_routes'],
        'governance': decision, 'self_test': self_test(),
        'rejected_inferences': [
            'Backward prerequisite is evidence of its truth',
            'Binary payload codec is a complete product-track compiler',
            'Roundtrip returns a satisfying assignment for every raw selector',
            'Finite clock tests establish unrestricted cubic coverage',
            'Modeled route counts measure mathematical difficulty',
        ],
    }


if __name__ == '__main__':
    print(json.dumps(report(), indent=2))
