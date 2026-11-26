"""Export and audit standalone certificates; the checker imports no solver code."""
import argparse
import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path
import mra_x_kernel as k
import mra_x_gap_agent as gap
import mra_x_topology as ref
import mra_x_indexed as idx
import mra_x_arbitrate as arb
import mra_x_separator as sep
import mra_x_formal as formal


def pack(f):
    s,tab=f; return [list(s),[[list(a),c] for a,c in sorted(tab.items())]]


def export(e,r):
    return dict(schema=1,problem=dict(domains=dict(e.d),factors=[pack(f) for f in e.inputs.values()]),result=copy.deepcopy(r),messages=[pack(f) for f in e.outputs])


def audit(root):
    root=root.resolve(); root.mkdir(); certs=root/'certificates'; certs.mkdir(); standalone=root/'standalone'; standalone.mkdir(); shutil.copyfile(Path(k.__file__),standalone/'mra_x_kernel.py')
    smt=formal.SMT(); rows=[]; queries=0; controls=0
    def test(e,r,name,global_check=False):
        nonlocal queries
        doc=export(e,r); path=certs/(name+'.json'); path.write_bytes(k.canonical(doc)); expected=k.digest(doc['problem'])
        p=subprocess.run([sys.executable,'-I','-S',str(standalone/'mra_x_kernel.py'),str(path),'--expect-problem',expected],cwd=standalone,capture_output=True,text=True,timeout=15)
        k.require(p.returncode==0); receipt=json.loads(p.stdout); k.require(receipt==k.check(doc,expected))
        if global_check: queries+=formal.verify(smt,e.d,list(e.inputs.values()),r)
        rows.append(dict(name=name,bytes=path.stat().st_size,**receipt))
    for i,kind in enumerate(gap.FAMILIES):
        for j in range(2):
            d,variants=gap.build(kind,23100+i*100+j,j); fs=variants[0][1]; inputs={str(z):f for z,f in enumerate(fs)}; e=idx.Indexed(d,ref.min_fill(d,fs)); prefix=f'{kind}-{j}'
            r=e.update(inputs)['result']; test(e,r,prefix+'-initial',True)
            nd=dict(d); nd[e.order[0]]+=1; e,x=arb.transfer(e,nd,inputs,ref.min_fill(nd,fs)); test(e,x['result'],prefix+'-migrate',True)
            for label,edits in [('forbid',{'test':((e.order[-1],),{})}),('restore',{'test':None})]: test(e,e.update(edits)['result'],prefix+'-'+label)
    d,fs=sep.instance(23999,128,'chain'); e=idx.Indexed(d,ref.min_fill(d,fs)); test(e,e.update({str(i):f for i,f in enumerate(fs)})['result'],'large-initial'); test(e,e.update({'test':((e.order[0],),{(0,):0})})['result'],'large-edit')
    for i,(d,fs) in enumerate((({},[]),({},[((),{})]),({'a':1},[]),({},[((),{():-9})]))):
        e=idx.Indexed(d,sorted(d)); test(e,e.update({str(j):f for j,f in enumerate(fs)})['result'],f'boundary-{i}',True)
    e=idx.Indexed({'a':2,'b':2},['a','b']); r=e.update({'f':(('a','b'),{(0,0):0,(1,0):0,(1,1):2})})['result']; good=export(e,r); expected=k.digest(good['problem'])
    def reject(doc,identity=expected):
        nonlocal controls
        try: k.check(doc,identity)
        except ValueError: controls+=1
        else: raise ValueError('accepted corrupted proof')
    for case in ('cost','missing','tie','scope','witness','order','count','bool','schema','input','duplicate','extra'):
        bad=copy.deepcopy(good)
        if case=='cost': bad['messages'][0][1][0][1]+=1
        if case=='missing': bad['messages'][0][1].pop(); bad['result']['trace'][0][2].pop()
        if case=='tie': bad['result']['trace'][0][2][0][1]=1
        if case=='scope': bad['messages'][0][0]=[]
        if case=='witness': bad['result']['witness']['a']=1
        if case=='order': bad['result']['order'].reverse()
        if case=='count': bad['result']['assignments_evaluated']+=1
        if case=='bool': bad['result']['trace'][0][2][0][1]=False
        if case=='schema': bad['schema']=True
        if case=='input': bad['problem']['factors'][0][1][0][1]+=1
        if case=='duplicate': bad['messages'][0][1].append(bad['messages'][0][1][0])
        if case=='extra': bad['extra']=0
        reject(bad)
    reject(good,'0'*64)
    bad=copy.deepcopy(good); vs=[str(i) for i in range(12)]; bad['problem']=dict(domains={v:4 for v in vs},factors=[[vs,[]]]); bad['result']['order']=vs; bad['result']['trace']=[None]*12; bad['messages']=[None]*12; reject(bad,None)
    for label,raw in [('duplicate-key',b'{"schema":1,"schema":1}'),('oversize',b' '* (k.MAX_BYTES+1)),('truncated',b'{')]:
        path=root/(label+'.bad'); path.write_bytes(raw); p=subprocess.run([sys.executable,'-I','-S',str(standalone/'mra_x_kernel.py'),str(path)],capture_output=True,timeout=15); k.require(p.returncode==1); path.unlink(); controls+=1
    out=dict(rows=rows,controls=controls,global_queries=queries,scope='portable local exhaustive inequality and attainment certificates; standalone standard-library checker; no SMT proof objects, program refinement or physical machine proof')
    out['evidence_sha256']=k.digest(out); return out


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--directory',type=Path,required=True); a=p.parse_args(); r=audit(a.directory); (a.directory/'evidence.json').write_bytes(k.canonical(r)); print(json.dumps(dict(cases=len(r['rows']),controls=r['controls'],global_queries=r['global_queries'],feasible=sum(x['optimum'] is not None for x in r['rows']),**{key:sum(x[key] for x in r['rows']) for key in ('bytes','visits','lookups')}),indent=2))
