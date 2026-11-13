"""
MathOS Omega Welfare Optimization Model.

Defines a discounted welfare objective with
utility, risk, and governance penalties.
"""

MODEL_ID = "OMEGA-WELFARE-001"

MODEL_NAME = "Omega Welfare Maximization"

LATEX = r"""
\mathcal{W}_{\Omega}^{*}
=
\max_{\pi \in \Pi}
\int_{0}^{T}
e^{-\rho t}
\left[
\sum_{i=1}^{n} w_i U_i(t)
-
\lambda R(t)
-
\mu G(t)
\right]
\,dt
"""

SYMBOLS = {
    "pi": "Decision strategy",
    "Pi": "Admissible strategy set",
    "T": "Time horizon",
    "rho": "Discount rate",
    "w_i": "Utility weight",
    "U_i": "Participant utility",
    "R": "Risk cost",
    "G": "Governance cost",
    "lambda": "Risk penalty weight",
    "mu": "Governance penalty weight",
}


def get_model():
    return {
        "id": MODEL_ID,
        "name": MODEL_NAME,
        "latex": LATEX.strip(),
        "symbols": SYMBOLS,
        "status": "defined_not_solved",
    }
