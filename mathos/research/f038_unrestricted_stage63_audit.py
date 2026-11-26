"""Stage 63 partial audit; the full two-state clock is NOT certified by this test."""
import json
import subprocess
import tempfile
from itertools import product
from pathlib import Path
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import (
    encoded,valid,BUILTINS,run_program,encode_tm,decode_tm)
from mathos.research.f038_unrestricted_quadratic_stage import length,count

PLAN='docs/research/tga-universal/f038-unrestricted-stage63-audit.json'
CPP=Path('mathos/research/f038_unrestricted_stage63_audit.cpp')
PIN=0x123456789abcdef0|(0x1234567<<64)


def fixture():
    n=93
    C=pool(n)
    F=tuple((i if PIN>>(i-1)&1 else -i,a,b)
            for i in range(1,92) for a,b in product((-92,92),(-93,93)))
    set_F=set(F)
    I={c:j for j,c in enumerate(C) if c in set_F}
    p=sum(1<<I[c] for c in F)
    L=n+1+len(C)
    s=3*(L-1).bit_length()
    P=n+1+2*n+2*n*(n-1)
    require(len(F)==p.bit_count()==364 and valid(C,n,p,PIN),'fixture witness')
    require(all(length(q)==v for q,v in ((1,20),(2,42),(3,61),(4,92))),
            'description boundary')
    require((L,s,P)==(1055520,63,17392) and s-3<n and length(4)>s,
            'clock geometry')
    # All four-step outputs have bit 13 equal to one if well formed.
    require(PIN>>13&1==0 and 13-4>4 and 13+4<n,'three-state untouched bit')
    for d in BUILTINS:
        w=run_program(C,n,p,d,1<<(s-len(d)))
        require(w is None or w>=1<<n or w&((1<<91)-1)!=PIN,'builtin witness')
    for q in (1,2,3):
        for a,w,m in product(range(q+1),range(3),(-1,0,1)):
            T=[(a,w,m)]*(3*q)
            d=encode_tm(T,q)
            require(len(d)==length(q) and decode_tm(d)==(q,T),'transition syntax')
    tape=encoded(n,p,C)
    require(tape[:P]=='1'*n+'0'*(P-n),'parent prefix')
    return tape,[n,len(C),L,s,len(F),P,str(PIN),*(1<<(s-length(q)) for q in (1,2,3)),count(3)]


def audit():
    tape,geometry=fixture()
    with tempfile.TemporaryDirectory() as tmp:
        exe=Path(tmp)/'audit'
        subprocess.run(['g++','-O3','-std=c++17','-Wall','-Wextra','-Werror',str(CPP),'-o',str(exe)],check=True)
        r=subprocess.run([str(exe)],input=tape+'\n',text=True,capture_output=True,check=True,timeout=240)
    result=json.loads(r.stdout)
    result['geometry']=geometry
    require(sum(result['one'][0])==count(1) and result['one'][0][5:]==[0,0],
            'one-state incomplete')
    require(sum(result['scalar4096'][0])==count(2) and result['scalar4096'][0][5]>0
            and result['scalar4096'][0][6]==0,'partial census')
    print('F038_UNRESTRICTED_STAGE63_PARTIAL_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
