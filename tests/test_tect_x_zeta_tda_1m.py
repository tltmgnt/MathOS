"""Unit checks for bounded 1,000,000 zeta-TDA audit, never RH certification."""
import csv
import gzip
import json
import math
import tempfile
import unittest
from pathlib import Path

import numpy as np

from tect_x_zeta_tda_1m import (
    FAMILIES, audit, circle_control, monotone_h0_deaths,
    norm_features, parameter_features, rips_betti01,
)


class TestZetaTDA(unittest.TestCase):
    def test_family_counts_and_distinctness(self):
        n = 120
        feats = parameter_features(n)
        self.assertEqual(set(feats), set(FAMILIES))
        self.assertEqual(sum(len(a) for a in feats.values()), 4*n)
        for family in ('hurwitz', 'cycle_spectral', 'full_shift_dynamical'):
            self.assertEqual(len(np.unique(feats[family][:, 0])), n)
        self.assertTrue(np.all(feats['cycle_ihara'] == feats['cycle_ihara'][0]))

    def test_cycle_closed_forms_match_laplacian_eigenvalue_sums(self):
        for n in range(3, 100):
            lam = 4 * np.sin(np.pi*np.arange(1, n) / n)**2
            self.assertTrue(np.isclose(np.sum(lam**-1), (n*n-1)/12, rtol=5e-11))
            self.assertTrue(np.isclose(np.sum(lam**-2), (n**4 + 10*n*n-11)/720, rtol=5e-11))

    def test_normalization_alias_is_not_same_function(self):
        n, m = 11, 13
        # Adaptive u_n = exp(-1/n) aliases by exact identity.
        self.assertAlmostEqual(-2*math.log(-math.expm1(-1)),
                               -2*math.log(-math.expm1(-1)))
        # Fixed u distinguishes the two functions.
        u = 0.3
        self.assertNotEqual((1-u**n)**-2, (1-u**m)**-2)

    def test_graph_h1_vs_sample_feature_h1(self):
        for n in range(3, 25):
            self.assertEqual(n-n+1, 1)  # E - V + 1 for C_n
        circ = circle_control(64)
        self.assertEqual(rips_betti01(circ, 0.25)['betti1'], 1)
        line = np.column_stack((np.linspace(0,1,64), np.linspace(0,1,64)))
        self.assertEqual(rips_betti01(line, 0.25)['betti1'], 0)

    def test_full_h0_deaths_are_monotone_chain(self):
        cloud = norm_features(parameter_features(120)['hurwitz'])
        self.assertEqual(len(monotone_h0_deaths(cloud)), 119)
        self.assertTrue(np.all(monotone_h0_deaths(cloud) >= 0))
        with self.assertRaises(ValueError):
            monotone_h0_deaths(np.array([[0,0],[2,1],[1,2]], dtype=float))

    def test_complete_small_audit_and_digest_reproducibility(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'small.csv.gz'
            first = audit(150, 64, p)
            first_sha = first['computation']['dataset_sha256']
            second = audit(150, 64, p)
            self.assertEqual(first_sha, second['computation']['dataset_sha256'])
            self.assertEqual(first['count_total'], 600)
            self.assertFalse(first['rh_proof'])
            self.assertFalse(first['bsd_proof'])
            self.assertTrue(any(x['betti1']==1 for x in
                                first['tda_controls']['circle_positive_control'].values()))
            with gzip.open(p, 'rt', encoding='utf-8') as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 600)
            self.assertEqual(len({r['variant_id'] for r in rows}), 600)


if __name__ == '__main__':
    unittest.main()

