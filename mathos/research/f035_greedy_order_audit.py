"""Exhaustive order audit for the exact unsimplified elimination fixture."""
from itertools import permutations

TRAP = ((2,4,5),(1,2,-3),(2,-3,-4),(-1,-2,-4),
        (3,-4,-5),(3,-4,5),(-3,-4,-5),(-1,-3,5),
        (-2,3,4),(1,2,3),(-2,-4,5),(1,-3,-4))

def eliminate(f,v):
    common,left,right=[],[],[]
    for row in f:
        p,n=v in row,-v in row
        if p and n:
            continue
        if p:
            left.append(tuple(x for x in row if x!=v))
        elif n:
            right.append(tuple(x for x in row if x!=-v))
        else:
            common.append(row)
    return tuple(common+[a+b for a in left for b in right])

def trace(f,order):
    counts=[len(f)]
    for v in order:
        f=eliminate(f,v)
        counts.append(len(f))
    return counts

def greedy(f,vs):
    vs=list(vs)
    order=[]
    while vs:
        sizes=[len(eliminate(f,v)) for v in vs]
        i=sizes.index(min(sizes))
        v=vs.pop(i)
        order.append(v)
        f=eliminate(f,v)
    return tuple(order)

if __name__=="__main__":
    vs=tuple(range(1,6))
    order=greedy(TRAP,vs)
    assert order==vs
    assert trace(TRAP,order)==[12,13,16,22,0,0]
    data=[(max(trace(TRAP,p)),p) for p in permutations(vs)]
    assert len(data)==120
    assert min(data)==(14,(5,4,1,2,3))
    assert max(data)==(2285,(3,5,2,1,4))
    assert sum(peak==14 for peak,_ in data)==4
    print("F035_GREEDY_ORDER_AUDIT_OK orders=120 minimum=14 greedy=22 maximum=2285")
