"""Exact finite cubic-stage counterexample, replaying a C++ coverage certificate."""
import json
import subprocess
import tempfile
from pathlib import Path
from itertools import product
from mathos.research.f038_tectx_cycle import require
from mathos.research.f038_mrax_cycle import run_mrax
from mathos.research.f038_universal_witness_layout import pool
from mathos.research.f038_unrestricted_universal_search import (
    encoded,valid,BUILTINS,run_program,encode_tm,decode_tm)
from mathos.research.f038_unrestricted_quadratic_stage import length,count

PLAN='docs/research/tga-universal/f038-unrestricted-cubic-fixture.json'
CPP=Path('mathos/research/f038_unrestricted_cubic_fixture.cpp')
PIN=0x123456789abcd


def fixture():
    n=52
    C=pool(n)
    I={c:j for j,c in enumerate(C)}
    F=tuple((i if PIN>>(i-1)&1 else -i,a,b)
            for i in range(1,51) for a,b in product((-51,51),(-52,52)))
    p=sum(1<<I[c] for c in F)
    tape=encoded(n,p,C)
    L=len(tape)
    s=3*(L-1).bit_length()
    P=n+1+2*n+4*(n*(n-1)//2)
    R=P-n
    require(len(F)==200 and p.bit_count()==200 and valid(C,n,p,PIN),'invalid fixture')
    require(tape[:P]=='1'*n+'0'*(P-n) and (L,s,P,R)==(182261,54,5461,5409),
            'prefix or stage geometry')
    require(length(1)==20 and length(2)==42 and length(3)==61 and
            count(1)==5832 and count(2)==387420489 and length(3)>s and
            (1<<(s-length(2)))<=R,'description coverage')
    # All built-ins are checked by the original interpreter, not guessed.
    require(all(not valid(C,n,p,run_program(C,n,p,d,1<<(s-len(d)))) for d in BUILTINS),
            'built-in succeeded')
    require(all(valid(C,n,p,PIN|(g<<50)) for g in range(4)),'guard extension failed')
    for i in range(50):
        require(not valid(C,n,p,PIN^(1<<i)),'pin not forced')
    for q in (1,2):
        for a,w,m in product(range(q+1),range(3),(-1,0,1)):
            T=[(a,w,m)]*(3*q)
            d=encode_tm(T,q)
            require(len(d)==length(q) and decode_tm(d)==(q,T),'transition syntax mismatch')
    return tape,[n,len(C),L,s,P,R,len(F),PIN,len(BUILTINS),1<<(s-length(1)),1<<(s-length(2))]


def audit():
    tape,geometry=fixture()
    with tempfile.TemporaryDirectory() as tmp:
        exe=Path(tmp)/'cubic'
        subprocess.run(['g++','-O3','-std=c++17','-Wall','-Wextra','-Werror',str(CPP),'-o',str(exe)],check=True)
        r=subprocess.run([str(exe)],input=tape+'\n',text=True,capture_output=True,check=True,timeout=300)
    result=json.loads(r.stdout)
    result['geometry']=geometry
    require(result['two'][1]==count(2) and sum(result['one'][:6])==count(1),'coverage failed')
    print('F038_UNRESTRICTED_CUBIC_FIXTURE_OK '+json.dumps(result,sort_keys=True,separators=(',',':')))
    return result


if __name__=='__main__':
    run_mrax(PLAN,audit)
