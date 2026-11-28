"""Outcome registry: explicit acceptance conditions, never inferred from tests."""
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Obligation:
    id: str
    statement: str
    dependencies: tuple = ()


OBLIGATIONS = {o.id: o for o in (
    Obligation("O01", "Representation preserves signed CNF truth"),
    Obligation("O02", "Induced-width certificate replay is sound", ("O01",)),
    Obligation("O03", "Boolean elimination is correct", ("O01",)),
    Obligation("O04", "Polynomial total overhead for fixed logarithmic width", ("O02", "O03")),
    Obligation("O05", "Normalization preserves SAT and removes specified redundancy", ("O01",)),
    Obligation("O06", "Higher homology yields a proved tractability relation", ("O01",)),
    Obligation("O07", "Spectral criterion is proved tractable", ("O01",)),
    Obligation("O08", "Reduction preserves satisfiability, size and structural bound", ("O01",)),
    Obligation("O09", "Generalized criterion and solver are correct", ("O04", "O05")),
    Obligation("O10", "Universal efficient transformation for all SAT", ("O08", "O09")),
    Obligation("O11", "Algorithm-independent superpolynomial obstruction"),
    Obligation("O12", "Independent formal proof of the exact novel statement"),
)}

# name, agent, acceptance condition, starting obligations.
OBJECTIVES = {
    "E01": ("P = NP", "algorithm synthesis", "universal polynomial-time SAT proof", ("O10", "O12")),
    "E02": ("P != NP", "complexity obstruction", "algorithm-independent lower-bound proof", ("O11", "O12")),
    "E03": ("Independence", "foundations", "independence from explicitly named axiom system", ("O12",)),
    "E04": ("Conditional P = NP", "conditional reasoning", "implication proof under explicit hypotheses", ("O10", "O12")),
    "E05": ("Conditional P != NP", "complexity", "conditional lower-bound proof", ("O11", "O12")),
    "E06": ("Topological tractability", "topology", "proved sufficient criterion and solver bound", ("O09", "O12")),
    "E07": ("Exact subclass", "classification", "necessity and sufficiency proof", ("O09", "O12")),
    "E08": ("Restricted lower bound", "lower bound", "proof in precisely specified model", ("O12",)),
    "E09": ("New transformation", "reduction", "correctness and complexity proof", ("O08", "O12")),
    "E10": ("Improved SAT algorithm", "optimization", "correctness and improved asymptotic bound", ("O03", "O04", "O12")),
    "E11": ("Complexity taxonomy", "knowledge", "verified classification rules", ("O09", "O12")),
    "E12": ("Conjecture refutation", "adversarial", "replayed counterexample to exact claim", ("O05",)),
    "E13": ("Topological limitation", "obstruction", "representation impossibility theorem", ("O01", "O12")),
    "E14": ("Empirical relationship", "experimental", "reproducible statistical study with stated scope", ("O01",)),
    "E15": ("Known theorem reproduction", "verification", "independent theorem verification; finite regression separately labeled", ("O12",)),
    "E16": ("No algorithmic improvement", "benchmarking", "controlled comparative benchmark", ("O04",)),
    "E17": ("Resource exhaustion", "resource management", "recoverable execution checkpoint", ()),
    "E18": ("System inconsistency", "diagnostic", "reproduced inconsistency and root cause", ("O01", "O02", "O03")),
    "E19": ("Incomplete proof", "proof decomposition", "explicit unresolved lemmas", ("O12",)),
    "E20": ("Research stagnation", "strategy", "documented bounded search limitations", ()),
}


def decompose(objective):
    if objective not in OBJECTIVES:
        raise ValueError("unknown research objective")
    name, agent, acceptance, roots = OBJECTIVES[objective]
    ordered = {}

    def visit(key):
        if key not in ordered:
            o = OBLIGATIONS[key]
            for dep in o.dependencies:
                visit(dep)
            ordered[key] = {**asdict(o), "status": "unresolved"}

    for root in roots:
        visit(root)
    return {"id": objective, "name": name, "agent": agent,
            "acceptance": acceptance, "obligations": list(ordered.values())}
