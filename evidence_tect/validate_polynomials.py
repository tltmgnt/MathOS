#!/usr/bin/env python3
"""Reproducible local C++/Python cross-check; not external replication."""
import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / 'cpp_model/model.cpp'
REPORT = ROOT / 'evidence_tect/polynomial-validation.json'
COEFFS = range(-2, 3)
POINTS = (-2, -1, 0, 1, 2)
HARNESS = r'''
#define main original_model_main
#include "model.cpp"
#undef main
int main() {
    std::size_t n, m;
    while (std::cin >> n >> m) {
        model::Poly a(n), b(m);
        for (auto& x : a) if (!(std::cin >> x)) return 2;
        for (auto& x : b) if (!(std::cin >> x)) return 2;
        auto c = model::multiply(a, b);
        std::cout << c.size();
        for (auto x : c) std::cout << ' ' << x;
        std::cout << '\n';
    }
    return std::cin.eof() ? 0 : 2;
}
'''


def evaluate(poly, x):
    value = 0
    for coefficient in reversed(poly):
        value = value * x + coefficient
    return value


def verify(a, b, c):
    size = len(a) + len(b) - 1 if a and b else 0
    if len(c) != size:
        raise ValueError(f'wrong length for {a}, {b}: {c}')
    for x in POINTS:
        if evaluate(c, x) != evaluate(a, x) * evaluate(b, x):
            raise ValueError(f'wrong product for {a}, {b} at {x}: {c}')


def run():
    # Degree <= 4: five distinct evaluation points uniquely identify the product.
    polys = [p for n in range(4) for p in itertools.product(COEFFS, repeat=n)]
    cases = list(itertools.product(polys, repeat=2))
    # Negative oracle control: an incorrect same-length product must be rejected.
    try:
        verify((1, 1), (1, -1), (1, 0, 1))
    except ValueError:
        pass
    else:
        raise RuntimeError('negative oracle control failed')
    data = ''.join(' '.join(map(str, (len(a), len(b), *a, *b))) + '\n'
                   for a, b in cases)
    with tempfile.TemporaryDirectory() as tmp:
        harness = Path(tmp) / 'harness.cpp'
        binary = Path(tmp) / 'harness'
        harness.write_text(HARNESS, encoding='utf-8')
        subprocess.run([os.environ.get('CXX', 'g++'), '-std=c++17', '-O2',
                        '-Wall', '-Wextra', '-pedantic', '-Werror',
                        '-I', str(MODEL.parent), str(harness), '-o', str(binary)],
                       check=True, timeout=120)
        result = subprocess.run([str(binary)], input=data, text=True,
                                capture_output=True, check=True, timeout=60)
    lines = result.stdout.splitlines()
    if len(lines) != len(cases):
        raise ValueError('missing or extra model results')
    for (a, b), line in zip(cases, lines):
        fields = list(map(int, line.split()))
        if not fields or fields[0] != len(fields) - 1:
            raise ValueError('invalid result encoding')
        verify(a, b, fields[1:])
    return {'claim_id': 'bounded-polynomial-multiply', 'result': 'PASS',
            'model_sha256': hashlib.sha256(MODEL.read_bytes()).hexdigest(),
            'input_lengths': [0, 1, 2, 3], 'coefficient_range': [-2, 2],
            'evaluation_points': list(POINTS), 'ordered_pairs': len(cases),
            'negative_oracle_control': 'PASS',
            'external_independent_reproduction': False,
            'deployment_authorized': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    report = run()
    if args.check and report != json.loads(REPORT.read_text(encoding='utf-8')):
        raise SystemExit('validation report mismatch; review and version evidence')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
