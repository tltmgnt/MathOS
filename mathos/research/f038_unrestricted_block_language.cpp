#include <array>
#include <vector>
#include <iostream>
#include <cstdint>
#include <algorithm>
#include <unordered_map>
#include <stdexcept>
#include <string>
using U=uint64_t;
struct Tr{int a,w,m;};
Tr tr(int v){return {v/9,v/3%3,v%3-1};}
int memo[1000000]; int cls;
int pw[6]={1,10,100,1000,10000,100000};
int high(int p){int &c=memo[p];if(c>=0)return c;int d[6];for(int i=0;i<6;i++){d[i]=p/pw[i]%10;if(!d[i]){int z=0;for(int v=1;v<=9;v++)z+=high(p+v*pw[i]);return c=z;}}if((d[1]-1)/3==2)return c=0;int reach=1;for(int k=0;k<2;k++)for(int i=0;i<6;i++)if(reach>>(i/3)&1){int a=(d[i]-1)/3;if(a<2)reach|=1<<a;}bool halt=false;int l=0,r=0;for(int i=0;i<6;i++)if(reach>>(i/3)&1){int a=(d[i]-1)/3,m=(d[i]-1)%3-1;if(a==2)halt=true;else if(m<0)l|=1<<a;else if(m>0)r|=1<<a;}return c=halt&&l&&r&&(cls==0?(l!=3&&r==3):cls==1?(l==3&&r!=3):(l==3&&r==3));}
struct Sim{int n,cap,off;std::vector<unsigned char>A;int T[6];std::vector<std::pair<int,int>>undo;U cnt[4]={},nodes=0,steps=0; U H[3][3]={}; U rate[258][3]={}; U types[4]={}, finiteL=0,finiteR=0, mixedL=0,mixedR=0;int p3[7]={1,3,9,27,81,243,729};
static U mix(U x){x+=0x9e3779b97f4a7c15ULL;x=(x^(x>>30))*0xbf58476d1ce4e5b9ULL;x=(x^(x>>27))*0x94d049bb133111ebULL;return x^(x>>31);}
Sim(int n0,int c):n(n0),cap(c),off(c+2),A(2*c+n+8,0){std::fill(A.begin(),A.begin()+off,2);std::fill_n(A.begin()+off,n,1);std::fill(T,T+6,-1);}
// Language of departures from a zero block. DFA states are sets of saved
// block patterns, with a separate initial vertex. Unknown external excursions
// are overapproximated by arbitrary returns from the allowed state alphabets.
int capacity(int l,int r,int dir,int len,int& gap){
 gap=0;
 int ret=dir==1?l:r,other=dir==1?r:l;
 int cells=len==1?3:len==2?9:27;
 auto exits=[&](U mask,int incoming,int head){std::array<int,2> e{};bool seen[162]={};int Q[162],end=0;
  auto add=[&](int p,int h,int a){int k=2*len*p+2*h+a;if(!seen[k]){seen[k]=true;Q[end++]=k;}};
  for(int p=0;p<cells;p++)if(mask>>p&1)for(int a=0;a<2;a++)if(incoming>>a&1)add(p,head,a);
  for(int i=0;i<end;i++){int k=Q[i],p=k/(2*len),h=k/2%len,a=k%2,weight=h==0?1:h==1?3:9,sym=p/weight%3;
   auto z=tr(T[3*a+sym]);if(z.a==2)continue;
   p+=(z.w-sym)*weight;h+=z.m;
   if(h>=0&&h<len)add(p,h,z.a);
   else if(z.m==dir)e[z.a]|=1<<p;
   else for(int a0=0;a0<2;a0++)if(other>>a0&1)add(p,dir==-1?len-1:0,a0);
  }return e;};
 const int maxv=256;std::array<std::array<int,2>,maxv>edge{};std::array<int,maxv>keys{};int num=1;
 for(int v=0;v<num;v++){auto e=v?exits(keys[v],ret,dir==1?len-1:0):exits(1,r,0);
  for(int a=0;a<2;a++)if(e[a]){int j=1;while(j<num&&keys[j]!=e[a])j++;if(j==num){if(num==maxv)return -1;keys[num++]=e[a];}edge[v][a]=j;}}
 // Longest consecutive run of binary choices, with a branching-only
 // cycle treated as unconstrained. Every gap-length path has a unary step.
 int lens[maxv]={};auto longest=[&](auto&&self,int v)->int{
  if(!edge[v][0]||!edge[v][1])return 0;
  if(lens[v])return lens[v];
  lens[v]=-1;
  int a=self(self,edge[v][0]),b=self(self,edge[v][1]);
  return lens[v]=(a<0||b<0)?-1:1+std::max(a,b);
 };
 int maxrun=0;bool unrestricted=false;for(int v=0;v<num;v++){int w=longest(longest,v);if(w<0)unrestricted=true;else maxrun=std::max(maxrun,w);}if(!unrestricted)gap=maxrun+1;
 for(int v=0;v<num;v++)if(edge[v][0]&&edge[v][1]){bool R[maxv]={};int Q[maxv],end=0;for(int a:edge[v])if(!R[a]){R[a]=true;Q[end++]=a;}for(int i=0;i<end;i++)for(int a:edge[Q[i]])if(a&&!R[a]){R[a]=true;Q[end++]=a;}if(R[v])return -1;}
 int memo2[maxv]={};auto f=[&](auto&&self,int v)->int{if(memo2[v])return memo2[v]<0?1:memo2[v];memo2[v]=-1;int s=0;for(int a:edge[v])if(a){int b=self(self,a);if(b<0||b>100000-s)return -2;s+=b;}return memo2[v]=std::max(1,s);};
 int v=f(f,0);return v<0?-1:v;
}
void classify(int p,int u){
 if(!high(p))return;
 if(u){int i=0;while(T[i]>=0)i++;for(int v=0;v<27;v++){T[i]=v;auto z=tr(v);classify(p+(2+3*z.a+z.m)*pw[i],u-1);}T[i]=-1;return;}
 int l=0,r=0;for(int i=0;i<6;i++){auto z=tr(T[i]);if(z.a<2){if(z.m<0)l|=1<<z.a;if(z.m>0)r|=1<<z.a;}}
 for(int iter=0;iter<4;iter++){
 int seen=r<<0,processed=0,el=0,er=0;
 while(seen&~processed){int k=__builtin_ctz(unsigned(seen&~processed));processed|=1<<k;int a=k%2,b=k/2;auto z=tr(T[3*a+b]);if(z.a==2)continue;
  if(z.m<0){el|=1<<z.a;seen|=r<<(2*z.w);}
  else if(z.m>0){er|=1<<z.a;seen|=l<<(2*z.w);}
  else seen|=1<<(2*z.w+z.a);
 }
 l=el;r=er;
 }
 H[__builtin_popcount(unsigned(l))][__builtin_popcount(unsigned(r))]++;
 int da=0,db=0,a=-1,b=-1;for(int len=1;len<=3;len++){if(a<0)a=capacity(l,r,-1,len,da);if(b<0)b=capacity(l,r,1,len,db);}int kind=(a<0?2:0)+(b<0?1:0);
 types[kind]++;
 if(kind)rate[kind==1?db:kind==2?da:(!da||!db?0:std::max(da,db))][kind-1]++;
 if(kind==0){finiteL+=a;finiteR+=b;}
 else if(kind==1)mixedL+=a;else if(kind==2)mixedR+=b;
}
bool drift(int a,int h){
 const int W=16, origin=64; std::array<unsigned char,81> v{};v.fill(2);
 for(int j=1;j<=W;j++)v[origin+j]=A[h+j];
 auto initial=v;
 int x=origin,b=a,edge=x;
 for(int j=0;j<64;j++){
  if(x<0||x>origin+W)return false;
  int z=T[3*b+v[x]];if(z<0||z>=18)return false;
  auto r=tr(z);v[x]=r.w;x+=r.m;b=r.a;
  if(x<edge){edge=x;if(b==a&&x>=0){bool eq=true;for(int k=0;k<=W;k++)if(v[x+k]!=initial[origin+k]){eq=false;break;}if(eq)return true;}}
 }return false;
}
void visit(int a,int h,int t,int p,int u,U hash,int lo){int count=high(p);if(!count)return;size_t root=undo.size(),cu=root;int ca=a,ch=h,ct=t,span=1;U ck=hash;while(t<cap){if(h<lo){if(drift(a,h)){cnt[3]+=U(count)*p3[u];break;}lo=h;}if(t>ct&&a==ca&&h==ch&&hash==ck){std::unordered_map<int,int>before;for(size_t j=cu;j<undo.size();j++)before.emplace(undo[j].first,undo[j].second);bool eq=true;for(auto [i,v]:before)if(A[i]!=v){eq=false;break;}if(eq){cnt[1]+=U(count)*p3[u];break;}}if(t-ct>=span){ca=a;ch=h;ct=t;ck=hash;cu=undo.size();span*=2;}int sym=A[h],k=3*a+sym,v=T[k];if(v<0){nodes++;for(int b=0;b<27;b++){T[k]=b;auto z=tr(b);visit(a,h,t,p+(1+3*z.a+z.m+1)*pw[k],u-1,hash,lo);}T[k]=-1;break;}auto z=tr(v);if(z.w!=sym){undo.emplace_back(h,sym);A[h]=z.w;hash^=mix(U(h)*3+sym)^mix(U(h)*3+z.w);}h+=z.m;a=z.a;t++;steps++;if(a==2){cnt[0]+=U(count)*p3[u];break;}if(t==cap){cnt[2]+=U(count)*p3[u];classify(p,u);break;}}
while(undo.size()>root){auto [i,v]=undo.back();undo.pop_back();A[i]=v;}}
};
int main(int argc,char**argv){
 if(argc!=4)throw std::runtime_error("n cap class required");
 int n=std::stoi(argv[1]),cap=std::stoi(argv[2]);cls=std::stoi(argv[3]);
 if(n<186||n>188||(cap!=8&&cap!=2048)||cls<0||cls>2||cap+n>n+1+2*n*n)throw std::runtime_error("fixture geometry");
 std::fill(memo,memo+1000000,-1);Sim s(n,cap);s.visit(0,s.off,0,0,6,0,s.off);
 U total=U(high(0))*729,mass=0,rates=0;
 for(U v:s.cnt)mass+=v;
 if(mass!=total)throw std::runtime_error("prefix partition");
 mass=0;for(U v:s.types)mass+=v;
 for(auto &row:s.rate)for(U v:row)rates+=v;
 if(mass!=s.cnt[2]||rates+s.types[0]!=mass)throw std::runtime_error("language partition");
 std::cout<<n<<" "<<cap<<" "<<cls;for(U v:s.cnt)std::cout<<" "<<v;
 std::cout<<" "<<s.nodes<<" "<<s.steps<<" "<<total<<"\n";
 for(U v:s.types)std::cout<<v<<" ";
 std::cout<<s.finiteL<<" "<<s.finiteR<<" "<<s.mixedL<<" "<<s.mixedR<<"\n";
 for(int d=0;d<258;d++)if(s.rate[d][0]||s.rate[d][1]||s.rate[d][2])std::cout<<d<<" "<<s.rate[d][0]<<" "<<s.rate[d][1]<<" "<<s.rate[d][2]<<"\n";
}
