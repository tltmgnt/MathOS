"""Phase XLIII: frozen empirical cost policy, with independently checked fallback."""
import math
import mra_x_boundproof as p
import mra_x_kernel as k
import mra_x_proofarbitrate as q

DEMAND=(1,2,4,8,16)


def features(doc):
    d,fs=p.problem(doc['problem']); _,groups=p.components(d,fs)
    rows=sum(len(t) for _,t in fs); visits=doc['result']['assignments_evaluated']
    optimum=doc['result']['optimum']; minima=sum(min(t.values(),default=0) for _,t in fs)
    spread=sum(max(t.values(),default=0)-min(t.values(),default=0) for _,t in fs)
    return [math.log1p(len(d)),math.log1p(rows),math.log1p(visits),
            max((sum(math.log(d[v]) for v in g) for g,_ in groups),default=0),
            float(max((len(scope) for scope,_ in fs),default=0)),
            1.0 if optimum is None else 0.0,
            0.0 if optimum is None else (optimum-minima)/max(1,spread)]


def fit(rows):
    p.require(len(rows)>=5)
    scale=[max(.25,max(x['features'][j] for x in rows)-min(x['features'][j] for x in rows)) for j in range(7)]
    return dict(schema=1,scale=scale,rows=rows,margin=None)


def neighbors(model,x):
    return sorted(model['rows'],key=lambda r:sum(((a-b)/s)**2 for a,b,s in zip(x,r['features'],model['scale'])))[:5]


def predict(model,x,reads):
    near=neighbors(model,x)
    # Conservative local maximum, not a statistical confidence guarantee.
    return max((r['first']+(reads-1)*r['replay'])/reads for r in near)


def choose(model,doc,reads):
    p.require(type(reads) is int and 1<=reads<=10000)
    if reads==1 or model['margin'] is None or doc['result']['assignments_evaluated']<64: return False
    return predict(model,features(doc),reads)*model['margin']<=.85


def select(model,doc,expected,*,reads=4):
    """Model affects search only; it cannot authorize an unchecked proof."""
    if choose(model,doc,reads):
        out=q.select(doc,expected,reads=reads); out['attempted']=True; return out
    receipt=k.check(doc,expected)
    return dict(kind='elimination',proof=doc,receipt=receipt,reason='cost_guard',attempted=False)


def calibrate(model,rows):
    """Choose margin on disjoint calibration states, using observed cost proxy."""
    options=[]
    for margin in (1.0,1.15,1.35,1.6,None):
        total=base=0.; worst=0.; attempts=0
        for r in rows:
            for reads in DEMAND:
                attempt=margin is not None and reads>1 and r['visits']>=64 and predict(model,r['features'],reads)*margin<=.85
                ratio=(r['first']+(reads-1)*r['replay'])/reads if attempt else 1.
                total+=ratio*reads*r['baseline_ns']; base+=reads*r['baseline_ns']; worst=max(worst,ratio); attempts+=attempt
        options.append(dict(margin=margin,ratio=total/base,worst=worst,attempts=attempts))
    # Demand-weighted latency proxy, constrained by worst observed ratio.
    best=min((r for r in options if r['worst']<=1.2),key=lambda r:(r['ratio'],r['attempts']))
    return dict(model,margin=best['margin']),options
