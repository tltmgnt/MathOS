"""Graph density and anchored decoding reference, not a compiled U solver."""
import json


def require(ok, msg):
    if not ok:
        raise AssertionError(msg)


def audit():
    seed=421
    def rnd(n):
        nonlocal seed
        seed=(1664525*seed+1013904223)&0xffffffff
        return seed%n
    rows=[]
    for m in (2,3,4,6):
        M=m**3
        Q=M*M
        P=Q//6
        row=[m,0,0,0,0,0]
        for mode in range(4):
            order=list(range(Q))
            if mode==1:
                order.sort(key=lambda a:(a%M,a))
            elif mode==2:
                for i in range(Q-1,0,-1):
                    j=rnd(i+1)
                    order[i],order[j]=order[j],order[i]
            elif mode==3:
                order.sort(key=lambda a:((a//M+a%M)%M,a))
            anchors=[set(),set()]
            high=[]
            for E in (order[:P],order[-P:]):
                adj=[[[] for _ in range(M)] for _ in range(2)]
                for e in E:
                    x,y=divmod(e,M)
                    adj[0][x].append(y)
                    adj[1][y].append(x)
                H=[[i for i,A in enumerate(B) if 500*len(A)>=M] for B in adj]
                for s in range(2):
                    for i in H[s]:
                        if not any(v in anchors[1-s] for v in adj[s][i]):
                            anchors[1-s].add(adj[s][i][0])
                HX,HY=map(set,H)
                dense=sum(e//M in HX and e%M in HY for e in E)
                require(500*dense>=500*P-2*Q and len(HX)*len(HY)>=dense,
                        'high degree edge bound')
                high.append((H,adj))
                row[1]+=1
                row[2]+=len(E)
            for k in range(16):
                S=[1 if i in anchors[0] else rnd(2) for i in range(M)]
                T=[1 if i in anchors[1] else rnd(2) for i in range(M)]
                for H,adj in high:
                    for s in range(2):
                        for i in H[s]:
                            v=next(v for v in adj[s][i] if v in anchors[1-s])
                            x,y=(v,i) if s else (i,v)
                            require(S[x]*T[y]==(T[i] if s else S[i]),'anchor decode')
                            row[3]+=1
                    row[4]+=1
            row[5]+=sum(map(len,anchors))
        rows.append(row)
    require(rows==[[2,8,80,1552,128,34],[3,8,968,5488,128,54],
                   [4,8,5456,12960,128,64],[6,8,62208,43776,128,70]],
            'independent JS rows')
    require([sum(r[i] for r in rows) for i in (1,2,3,4)]==
            [32,68712,63776,512],'aggregate')
    require(40*21**3*9146**3<9*20**3*2**42,'inherited clock slack')
    # P-2Q/500 >= 4Q/25 once the loss of one floor cell is absorbed.
    # 1/6 - 2/500 - 4/25 = 1/375 > 0.
    require(500*25-2*6*25-4*6*500>0,'strict density margin')
    print('F038_UNRESTRICTED_LAYOUT_INDEPENDENT_BARRIER_OK '+
          json.dumps(rows,separators=(',',':')))
    return rows


if __name__=='__main__':
    audit()
