import argparse
from .runner import run


def main():
    parser = argparse.ArgumentParser(description='Run scoped proof-dependency and adversarial checks; no Millennium certification.')
    parser.add_argument('--output-dir', default='artifacts/proof-analysis',
                        help='Directory for regenerated evidence and content hashes')
    parser.add_argument('--run-tests', action='store_true',
                        help='Run repository test_proof_*.py tests before generating reports')
    args = parser.parse_args()
    result = run(args.output_dir, run_tests=args.run_tests)
    print('Reports written to ' + str(result['output_dir']))


if __name__ == '__main__':
    main()
