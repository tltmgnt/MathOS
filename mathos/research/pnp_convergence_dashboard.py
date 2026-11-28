"""Render a saved convergence report as an offline, non-verifying HTML dashboard."""
import argparse
from html import escape
import json
from pathlib import Path


def render_report(report):
    if report.get("schema") != "mathos-pnp-convergence/1":
        raise ValueError("expected a convergence report")
    ev = report.get("evidence", {})
    rows = []
    for label, key in (("Normalized input graph", "original_graph_bounds"),
                       ("Transformed graph", "transformed_graph_bounds")):
        if key not in ev:
            continue
        b = ev[key]
        lo, hi, gap = (b.get(k) for k in ("lower", "upper", "gap"))
        for value in (lo, hi, gap):
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError("invalid numeric bound")
        if hi is not None and (lo is None or hi < lo or gap != hi - lo):
            raise ValueError("inconsistent bound values")
        bar = ""
        if hi is not None:
            scale = max(1, hi)
            bar = (f'<div class="track" aria-label="lower bound {lo}, upper bound {hi}">'
                   f'<span class="known" style="width:{100*lo/scale:.3f}%"></span>'
                   f'<span class="gap" style="width:{100*gap/scale:.3f}%"></span></div>')
        history = "".join(
            "<li>" + escape(str(h.get("side"))) + ": " +
            escape(str(h.get("source"))) + " — [" +
            escape(str(h.get("lower"))) + ", " + escape(str(h.get("upper"))) + "]</li>"
            for h in b.get("history", []))
        rows.append(f"<section><h2>{label}</h2><p>L = {lo}, U = {hi}, gap = {gap}</p>"
                    + bar + "<p>" + escape(str(b.get("width_classification", ""))) +
                    "</p><ol>" + history + "</ol></section>")
    obligations = []
    for plan in report.get("plans", []):
        obligations.append("<h3>" + escape(str(plan.get("name"))) + "</h3><ul>" +
                           "".join("<li>" + escape(str(o.get("id"))) + " — " +
                                   escape(str(o.get("statement"))) + " (" +
                                   escape(str(o.get("status"))) + ")</li>"
                                   for o in plan.get("obligations", [])) + "</ul>")
    return """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MathOS convergence evidence</title>
<style>body{font:16px system-ui,sans-serif;max-width:900px;margin:32px auto;padding:0 20px;
color:#1e293b;background:#f8fafc}section{background:white;border:1px solid #cbd5e1;
padding:16px;margin:16px 0;border-radius:8px}h1,h2,h3{line-height:1.2}
.track{display:flex;height:18px;background:#e2e8f0;border-radius:4px;overflow:hidden}
.known{background:#475569}.gap{background:#a78bfa}li{margin:5px 0}</style>
<h1>Bidirectional convergence</h1><p>Report view only; no certificates rechecked here.
Bars display the reported lower bound (gray) and remaining uncertainty (purple)
relative to the upper bound for each graph. Exact treewidth is not a SAT-time lower bound.</p>
<p>Universal P versus NP obligation remains unresolved by this engine.</p>
""" + "<p>Completion: " + escape(str(report.get("completion"))) + "</p>" + \
        "".join(rows) + "<h2>Proof obligations</h2>" + "".join(obligations) + "</html>\n"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    a = p.parse_args(argv)
    try:
        if a.input.stat().st_size > 2_000_000:
            raise ValueError("report exceeds 2 MB")
        if a.input.resolve() == a.output.resolve():
            raise ValueError("output must not overwrite input")
        a.output.write_text(render_report(json.loads(a.input.read_text(encoding="utf-8"))),
                            encoding="utf-8")
    except (OSError, ValueError, TypeError) as exc:
        p.exit(1, str(exc) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
