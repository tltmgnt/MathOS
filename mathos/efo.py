"""MathOS EFO v1: offline, reproducible empirical observation and falsification.

Independent from r3b.Observation (benchmark metrics) and formal proof verification.
Digests verify internal consistency, not authorship or empirical truth.
"""
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import math

VERSION = "mathos-efo-v1"
KINDS = frozenset({"experience", "observation", "fact", "hypothesis"})
OPERATORS = {"gt": lambda a, b: a > b, "ge": lambda a, b: a >= b,
             "lt": lambda a, b: a < b, "le": lambda a, b: a <= b}

def canonical_json(value):
    def check(item):
        if item is None or type(item) in (str, bool, int):
            return
        if type(item) is float and math.isfinite(item):
            return
        if type(item) in (tuple, list):
            for v in item:
                check(v)
            return
        if type(item) is dict and all(type(k) is str for k in item):
            for v in item.values():
                check(v)
            return
        raise ValueError("noncanonical or nonfinite JSON data")
    check(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)

def digest(value):
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()

def _timestamp(value):
    if type(value) is not str or not value.strip():
        raise ValueError("ISO 8601 timestamp required")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid ISO 8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timezone offset required")
    return parsed.astimezone(timezone.utc)

def _label(value):
    if type(value) is not str or not value.strip():
        raise ValueError("nonempty label required")
    return value

def _sha(value):
    if type(value) is not str or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError("invalid SHA-256 reference")

@dataclass(frozen=True)
class EFORecord:
    kind: str
    observed_at: str
    recorded_at: str
    source_id: str
    claim: str
    measurements_json: str
    evidence_digests: tuple = ()
    schema_version: str = VERSION
    research_only: bool = True

    def __post_init__(self):
        if self.kind not in KINDS or self.schema_version != VERSION or self.research_only is not True:
            raise ValueError("invalid EFO record")
        if _timestamp(self.observed_at) > _timestamp(self.recorded_at):
            raise ValueError("observation postdates recording")
        _label(self.source_id)
        _label(self.claim)
        if type(self.measurements_json) is not str:
            raise ValueError("measurements_json must be canonical JSON")
        try:
            measurements = json.loads(self.measurements_json)
        except (ValueError, TypeError) as exc:
            raise ValueError("invalid measurements JSON") from exc
        if type(measurements) is not dict or canonical_json(measurements) != self.measurements_json:
            raise ValueError("measurements must be a canonical JSON object")
        if type(self.evidence_digests) is not tuple:
            raise ValueError("evidence references must be a tuple")
        for reference in self.evidence_digests:
            _sha(reference)
        if len(set(self.evidence_digests)) != len(self.evidence_digests):
            raise ValueError("duplicate evidence references")
        if self.kind in {"fact", "hypothesis"} and not self.evidence_digests:
            raise ValueError("fact/hypothesis requires evidence")

    @property
    def measurements(self):
        """Return a new mutable copy, never the archived snapshot."""
        return json.loads(self.measurements_json)

    @property
    def digest(self):
        return digest(asdict(self))

def record(kind, observed_at, recorded_at, source_id, claim, measurements, evidence_digests=()):
    return EFORecord(kind, observed_at, recorded_at, source_id, claim,
                     canonical_json(measurements), tuple(evidence_digests))

@dataclass(frozen=True)
class FalsificationTest:
    hypothesis_digest: str
    criterion: str
    operator: str
    threshold: float
    registered_at: str
    horizon_end: str
    schema_version: str = VERSION
    research_only: bool = True

    def __post_init__(self):
        if self.schema_version != VERSION or self.research_only is not True:
            raise ValueError("invalid test")
        _sha(self.hypothesis_digest)
        _label(self.criterion)
        if self.operator not in OPERATORS:
            raise ValueError("invalid operator")
        if type(self.threshold) not in (int, float) or not math.isfinite(self.threshold):
            raise ValueError("finite threshold required")
        if _timestamp(self.registered_at) >= _timestamp(self.horizon_end):
            raise ValueError("registration must precede horizon")

    @property
    def digest(self):
        return digest(asdict(self))

@dataclass(frozen=True)
class TestOutcome:
    test_digest: str
    criterion: str
    observed_at: str
    recorded_at: str
    source_id: str
    value: float | None
    verdict: str
    schema_version: str = VERSION
    research_only: bool = True

    def __post_init__(self):
        if self.schema_version != VERSION or self.research_only is not True:
            raise ValueError("invalid outcome")
        _sha(self.test_digest)
        _label(self.criterion)
        _label(self.source_id)
        if _timestamp(self.observed_at) > _timestamp(self.recorded_at):
            raise ValueError("outcome postdates recording")
        if self.value is not None and (type(self.value) not in (int, float) or not math.isfinite(self.value)):
            raise ValueError("finite outcome required")
        if self.verdict not in {"supported", "falsified", "inconclusive"}:
            raise ValueError("invalid verdict")
        if (self.value is None) != (self.verdict == "inconclusive"):
            raise ValueError("missing outcome must be inconclusive")

    @property
    def digest(self):
        return digest(asdict(self))

def register_test(hypothesis, *, criterion, operator, threshold, registered_at, horizon_end):
    if not isinstance(hypothesis, EFORecord) or hypothesis.kind != "hypothesis":
        raise ValueError("hypothesis required")
    if _timestamp(hypothesis.recorded_at) > _timestamp(registered_at):
        raise ValueError("hypothesis recorded after registration")
    return FalsificationTest(hypothesis.digest, criterion, operator, threshold, registered_at, horizon_end)

def evaluate_test(test, *, criterion, observed_at, recorded_at, source_id, value):
    if not isinstance(test, FalsificationTest):
        raise ValueError("test required")
    if criterion != test.criterion:
        raise ValueError("outcome criterion differs from preregistered criterion")
    if _timestamp(observed_at) < _timestamp(test.horizon_end):
        raise ValueError("outcome before horizon")
    if value is not None and (type(value) not in (int, float) or not math.isfinite(value)):
        raise ValueError("finite outcome required")
    verdict = "inconclusive" if value is None else (
        "supported" if OPERATORS[test.operator](value, test.threshold) else "falsified")
    return TestOutcome(test.digest, criterion, observed_at, recorded_at, source_id, value, verdict)

def verify_chain(records, tests=(), outcomes=()):
    try:
        if any(type(seq) not in (list, tuple) for seq in (records, tests, outcomes)):
            return False
        if any(type(r) is not EFORecord for r in records) or any(type(t) is not FalsificationTest for t in tests) or any(type(o) is not TestOutcome for o in outcomes):
            return False
        rmap = {r.digest: r for r in records}
        tmap = {t.digest: t for t in tests}
        if len(rmap) != len(records) or len(tmap) != len(tests) or len({o.digest for o in outcomes}) != len(outcomes):
            return False
        for r in records:
            for reference in r.evidence_digests:
                parent = rmap.get(reference)
                if parent is None or _timestamp(parent.recorded_at) > _timestamp(r.recorded_at):
                    return False
                if r.kind == "fact" and parent.kind not in {"experience", "observation"}:
                    return False
        for t in tests:
            h = rmap.get(t.hypothesis_digest)
            if h is None or h.kind != "hypothesis" or _timestamp(h.recorded_at) > _timestamp(t.registered_at):
                return False
        for o in outcomes:
            t = tmap.get(o.test_digest)
            if t is None or o.criterion != t.criterion or _timestamp(o.observed_at) < _timestamp(t.horizon_end):
                return False
            expected = evaluate_test(t, criterion=o.criterion, observed_at=o.observed_at,
                                     recorded_at=o.recorded_at, source_id=o.source_id, value=o.value)
            if o.verdict != expected.verdict:
                return False
        return True
    except (ValueError, TypeError, AttributeError, OverflowError):
        return False

def export_chain(records, tests=(), outcomes=()):
    if not verify_chain(records, tests, outcomes):
        raise ValueError("invalid EFO chain")
    payload = {"schema_version": VERSION, "research_only": True,
               "records": [asdict(r) for r in records],
               "tests": [asdict(t) for t in tests],
               "outcomes": [asdict(o) for o in outcomes]}
    return {"payload": payload, "digest": digest(payload)}

def verify_export(document):
    try:
        if type(document) is not dict or set(document) != {"payload", "digest"}:
            return False
        p = document["payload"]
        if type(p) is not dict or set(p) != {"schema_version", "research_only", "records", "tests", "outcomes"}:
            return False
        if p["schema_version"] != VERSION or p["research_only"] is not True or digest(p) != document["digest"]:
            return False
        return verify_chain([EFORecord(**{**r, "evidence_digests": tuple(r["evidence_digests"])}) for r in p["records"]],
                            [FalsificationTest(**t) for t in p["tests"]],
                            [TestOutcome(**o) for o in p["outcomes"]])
    except (ValueError, TypeError, KeyError, AttributeError, OverflowError):
        return False
