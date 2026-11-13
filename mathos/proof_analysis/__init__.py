"""Finite proof-dependency analysis and scoped adversarial examples.

This package is not a mathematical truth oracle or a proof assistant.
"""

from .gap_analysis import Claim, analyze, models

__all__ = ['Claim', 'analyze', 'models']
