"""Optional independent MILP comparison; requires SciPy/HiGHS."""
import argparse
from pathlib import Path
import scipy
import mra_x_archive as a
import mra_x_system_audit as v
from mra_x_frontier import highs


def run():
    rows=[]
    for name,domains,edits in v.corpus():
        d=dict(domains); fs={}
        for j,(es,ds) in enumerate(edits,1):
            v.inputs_after(d,fs,es,ds)
            if j not in (1,6,9,10,18): continue
            value,work=v.oracle(d,list(fs.values())); result,w,status=highs(d,list(fs.values()))
            a.require(value==result)
            if result is not None:
                a.require(set(w)==set(d) and all(0<=w[x]<d[x] for x in d))
                a.require(sum(t[tuple(w[x] for x in scope)] for scope,t in fs.values())==result)
            rows.append(dict(stream=name,version=j,optimum=result,status=status,oracle_visits=work))
    report=dict(scipy=scipy.__version__,rows=rows,scope='sampled original-factor MILP comparison; empty-factor short circuit is not a MILP solve; no timing comparison or independent third-party replication')
    report['evidence_sha256']=a.digest(report); return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args();out=run();args.output.write_bytes(a.canonical(out));print(len(out['rows']))
