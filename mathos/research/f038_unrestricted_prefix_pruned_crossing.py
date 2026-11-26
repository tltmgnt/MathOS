"""Common-prefix pruning and mixed-direction Kraft bounds for exact U cubic stage."""
import json
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path
from math import comb
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_unrestricted_quadratic_stage import length,count
from mathos.research.f038_unrestricted_kraft_crossing import shapes
from mathos.research.f038_unrestricted_cubic_crossing_census import ceil

PLAN='docs/research/tga-universal/f038-unrestricted-prefix-pruned-crossing.json'
CPP=Path('mathos/research/f038_unrestricted_prefix_pruned_crossing.cpp')


def run(exe,n,cap,c,S):
    out=subprocess.check_output([str(exe),str(n),str(cap),str(c)],text=True,timeout=90)
    R=list(map(int,out.split()))
    H=S['matrix']
    total=(H[1][2],H[2][1],H[2][2])[c]
    require(len(R)==9 and R[:3]==[n,cap,c] and R[-1]==total
            and sum(R[3:6])==total,'prefix partition mismatch')
    return R


def bound(n,m,R,S):
    L=n+1+2*n*n+8*comb(n,3)
    s=3*(L-1).bit_length()
    g=8*(comb(n-1,3)-comb(n-m,3))+1
    h=g-n
    require(s==72 and s<length(4) and s-3<n and
            (1<<(s-length(3)))+n<=n+1+2*n*n and 512+n<=n+1+2*n*n,
            'actual clock and prefix geometry')
    k,r=divmod(((1<<(s-length(2)))+g)//2,h)
    A,B=1<<m,1<<(n-m)
    x,y,z=R
    C=0
    for l in range(3):
        for rr in range(3):
            if l==0 or rr==0 or l==rr==1:
                C+=S['matrix'][l][rr]*(A+(0 if rr==0 else 2 if rr==2 and l==0 else 1)*B)
    F=count(1)+count(3)+4+S['initial']+S['high']-x-y-z
    u=(Fraction(g*(x*B+y*A+z*(A+B))*(1<<(k+1)),2*h-r)
       +Fraction(g*C,h)+g*(x*A+y*B)+F)/(1<<n)
    return u,[n,m,k,g,str(ceil(10**9*u)),str(ceil((1-u)*(1<<n))) if u<1 else None]


def audit():
    S=shapes()
    with tempfile.TemporaryDirectory() as tmp:
        exe=Path(tmp)/'audit'
        subprocess.run(['g++','-O3','-std=c++17','-Wall','-Wextra','-Werror',str(CPP),'-o',str(exe)],check=True)
        short=[run(exe,186,8,c,S) for c in range(3)]
        census=[run(exe,n,512,c,S) for n in range(186,191) for c in range(3)]
    # Independent JS no-cycle replay at the short horizon.
    require([[r[3],r[4]+r[5]] for r in short]==
            [[9688563,14788341],[13790259,10686645],[2770335,3239541]],
            'short horizon reference mismatch')
    bounds=[]
    for n in range(186,191):
        R=[r[5] for r in census if r[0]==n]
        u,row=min((bound(n,m,R,S) for m in range(2*n//5,(13*n+19)//20+1)),key=lambda a:a[0])
        require((u<1)==(n>=189),'finite gap boundary changed')
        bounds.append(row)
    require([length(q) for q in (1,2,3,4)]==[20,42,61,92],'decoder geometry')
    result={'bounds':bounds,'census':census,'controls':3,'short':short}
    print('F038_UNRESTRICTED_PREFIX_PRUNED_CROSSING_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
