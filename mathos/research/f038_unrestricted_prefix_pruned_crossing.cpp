// Exact common-prefix audit. Horizon survivors are NOT full-clock failures.
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
int memo[1000000],cls;
const int pw[6]={1,10,100,1000,10000,100000};
// Partial shape digits: 0=undefined, 1+3*next+(move+1) otherwise.
// Return number of full shape completions in the chosen directional class.
int high(int p){
 int &c=memo[p];if(c>=0)return c;
 int d[6];
 for(int i=0;i<6;i++){
  d[i]=p/pw[i]%10;
  if(!d[i]){
   int z=0;for(int v=1;v<=9;v++)z+=high(p+v*pw[i]);return c=z;
  }
 }
 if((d[1]-1)/3==2)return c=0;
 int reach=1;
 for(int k=0;k<2;k++)for(int i=0;i<6;i++)if(reach>>(i/3)&1){
  int a=(d[i]-1)/3;if(a<2)reach|=1<<a;
 }
 bool halt=false;int l=0,r=0;
 for(int i=0;i<6;i++)if(reach>>(i/3)&1){
  int a=(d[i]-1)/3,m=(d[i]-1)%3-1;
  if(a==2)halt=true;else if(m<0)l|=1<<a;else if(m>0)r|=1<<a;
 }
 return c=halt&&l&&r&&(cls==0?(l!=3&&r==3):cls==1?(l==3&&r!=3):(l==3&&r==3));
}
struct Sim{
 int n,cap,off;
 std::vector<unsigned char>A;
 int T[6];
 std::vector<std::pair<int,int>>undo;
 U cnt[3]={},nodes=0,steps=0;
 const int p3[7]={1,3,9,27,81,243,729};
 static U mix(U x){
  x+=0x9e3779b97f4a7c15ULL;
  x=(x^(x>>30))*0xbf58476d1ce4e5b9ULL;
  x=(x^(x>>27))*0x94d049bb133111ebULL;
  return x^(x>>31);
 }
 Sim(int n0,int c):n(n0),cap(c),off(c+2),A(2*c+n+8,0){
  std::fill(A.begin(),A.begin()+off,2);
  std::fill_n(A.begin()+off,n,1);
  std::fill(T,T+6,-1);
 }
 void visit(int a,int h,int t,int p,int u,U hash){
  int count=high(p);if(!count)return;
  size_t root=undo.size(),cu=root;
  int ca=a,ch=h,ct=t,span=1;U ck=hash;
  while(t<cap){
   if(t>ct&&a==ca&&h==ch&&hash==ck){
    // Hash only proposes recurrence; compare the first prior value of every
    // changed cell since checkpoint with its exact current value.
    std::unordered_map<int,int>before;
    for(size_t j=cu;j<undo.size();j++)before.emplace(undo[j].first,undo[j].second);
    bool eq=true;for(auto [i,v]:before)if(A[i]!=v){eq=false;break;}
    if(eq){cnt[1]+=U(count)*p3[u];break;}
   }
   if(t-ct>=span){ca=a;ch=h;ct=t;ck=hash;cu=undo.size();span*=2;}
   int sym=A[h],k=3*a+sym,v=T[k];
   if(v<0){
    nodes++;
    for(int b=0;b<27;b++){
     T[k]=b;auto z=tr(b);
     visit(a,h,t,p+(2+3*z.a+z.m)*pw[k],u-1,hash);
    }
    T[k]=-1;break;
   }
   auto z=tr(v);
   if(z.w!=sym){
    undo.emplace_back(h,sym);A[h]=z.w;
    hash^=mix(U(h)*3+sym)^mix(U(h)*3+z.w);
   }
   h+=z.m;a=z.a;t++;steps++;
   if(a==2){cnt[0]+=U(count)*p3[u];break;}
   if(t==cap){cnt[2]+=U(count)*p3[u];break;}
  }
  while(undo.size()>root){auto [i,v]=undo.back();undo.pop_back();A[i]=v;}
 }
};
int main(int argc,char**argv){
 if(argc!=4)throw std::runtime_error("n horizon class required");
 int n=std::stoi(argv[1]),cap=std::stoi(argv[2]);cls=std::stoi(argv[3]);
 if(n<186||n>190||(cap!=8&&cap!=512)||cls<0||cls>2)
  throw std::runtime_error("unsupported fixture");
 if(cap+n>n+1+2*n*n)throw std::runtime_error("not prefix local");
 std::fill(memo,memo+1000000,-1);
 Sim s(n,cap);s.visit(0,s.off,0,0,6,0);
 U total=U(high(0))*729;
 if(s.cnt[0]+s.cnt[1]+s.cnt[2]!=total)throw std::runtime_error("partition");
 std::cout<<n<<" "<<cap<<" "<<cls<<" "<<s.cnt[0]<<" "<<s.cnt[1]<<" "<<s.cnt[2]<<" "
          <<s.nodes<<" "<<s.steps<<" "<<total<<"\n";
}
