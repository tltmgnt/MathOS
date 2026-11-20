\\ MathOS BSD 08: independent PARI/GP 2-descent work order.
\\ Invoked with __U__ substituted by a *checked* integer parameter.
\\ ellrank returns unconditional [lower, upper, sha2_correction, rational_points].
\\ PARI's documented 2-Selmer rank: C = upper + t2 + sha2_correction,
\\ where t2 = dim_F2 E(Q)[2].  GP is an external, independently developed CAS.
\\ NEVER use ellanalyticrank/ellbsd to promote algebraic-rank claims.
default(parisize, 200000000);
u=__U__;
s=u*(u+1);
if(s%2, error("S is not even"));
E=ellinit([0,s/2,1,-(s+2)/2,0]);
if(!ellisoncurve(E,[0,0])||!ellisoncurve(E,[1,0])||!ellisoncurve(E,[-1,u]),error("Section equation mismatch"));
tr=elltors(E);
t2=0;
for(i=1,#tr[2],if(tr[2][i]%2==0,t2++));
if(u==2||u==3,
  rr=ellrank(E,0,[[0,0],[1,0],[-1,u]]),
  rr=ellrank(E,0)
);
if(rr[1]>rr[2],error("lower rank exceeds upper"));
if(rr[3]%2,error("Cassels pairing correction must be even"));
c2=rr[2]+t2+rr[3];
if(c2<rr[2]+t2,error("Invalid Selmer dimension"));
print("MATHOS08|",u,"|",rr[1],"|",rr[2],"|",rr[3],"|",t2,"|",c2,"|",#rr[4]);
quit;
