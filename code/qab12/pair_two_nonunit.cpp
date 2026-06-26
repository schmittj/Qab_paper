#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

struct Rec{uint32_t U,V,d;std::array<uint32_t,5>su{},sv{};uint32_t r,t,e,a,b,n;};
struct Key{uint32_t U,V,d;std::array<uint32_t,5>su{},sv{};bool operator<(const Key&o)const{return std::tie(U,V,d,su,sv)<std::tie(o.U,o.V,o.d,o.su,o.sv);}};
struct Row{Rec x,y;uint32_t D,corr,role;bool operator<(const Row&o)const{return std::tie(x.U,x.V,x.d,D,x.r,x.a,x.b,y.r,y.a,y.b,x.t,x.e,y.t,y.e)<std::tie(o.x.U,o.x.V,o.x.d,o.D,o.x.r,o.x.a,o.x.b,o.y.r,o.y.a,o.y.b,o.x.t,o.x.e,o.y.t,o.y.e);}bool operator==(const Row&o)const{return x.U==o.x.U&&x.V==o.x.V&&x.d==o.x.d&&x.r==o.x.r&&x.t==o.x.t&&x.e==o.x.e&&x.a==o.x.a&&x.b==o.x.b&&y.r==o.y.r&&y.t==o.y.t&&y.e==o.y.e&&y.a==o.y.a&&y.b==o.y.b;}};
static std::vector<uint32_t> supp(uint32_t x){std::vector<uint32_t>o;if(x%2==0){o.push_back(2);while(x%2==0)x/=2;}for(uint32_t p=3;(uint64_t)p*p<=x;p+=2)if(x%p==0){o.push_back(p);while(x%p==0)x/=p;}if(x>1)o.push_back(x);return o;}
static std::set<uint32_t> shape_supp(const Rec&z){std::set<uint32_t>S;for(uint32_t q:{z.a,z.b,z.n}){auto v=supp(q);S.insert(v.begin(),v.end());}return S;}
static uint32_t role_value(uint32_t p,const Rec&z){uint32_t hits=0,v=0;for(uint32_t q:{z.a,z.b,z.n})if(q%p==0){++hits;v=q;}if(hits!=1)throw std::runtime_error("role invariant");return v;}
static bool same_pkg(const Rec&x,const Rec&y){uint64_t xa=(uint64_t)x.r*x.a,xb=(uint64_t)x.r*x.b,ya=(uint64_t)y.r*y.a,yb=(uint64_t)y.r*y.b;if(xa>xb)std::swap(xa,xb);if(ya>yb)std::swap(ya,yb);return xa==ya&&xb==yb;}
static bool disjoint(const Rec&x,const Rec&y){std::array<uint64_t,3>A={(uint64_t)x.r*x.a,(uint64_t)x.r*x.b,(uint64_t)x.r*x.n},B={(uint64_t)y.r*y.a,(uint64_t)y.r*y.b,(uint64_t)y.r*y.n};for(auto a:A)for(auto b:B)if(a==b)return false;return true;}
static uint64_t corr(const Rec&x,const Rec&y){uint64_t g0=std::gcd((uint64_t)x.r*x.b,(uint64_t)y.r*y.b),g1=std::gcd((uint64_t)x.r*x.a,(uint64_t)y.r*y.a);return ((uint64_t)y.r*y.b/g0)*((uint64_t)x.r*x.a/g1)+((uint64_t)x.r*x.b/g0)*((uint64_t)y.r*y.a/g1);}
static bool same_shape(const Rec&x,const Rec&y){return (x.a==y.a&&x.b==y.b)||(x.a==y.b&&x.b==y.a);}
static uint32_t flog(uint32_t n,uint32_t p){uint32_t k=0,q=1;while(q<=n/p){q*=p;++k;}return k;}
static Rec parse(const std::string&line){std::stringstream ss(line);std::string s;std::vector<uint32_t>v;while(std::getline(ss,s,','))v.push_back((uint32_t)std::stoul(s));if(v.size()!=19)throw std::runtime_error("bad row");Rec z;z.U=v[0];z.V=v[1];z.d=v[2];for(int i=0;i<5;++i)z.su[i]=v[3+i];for(int i=0;i<5;++i)z.sv[i]=v[8+i];z.r=v[13];z.t=v[14];z.e=v[15];z.a=v[16];z.b=v[17];z.n=v[18];return z;}
int main(int argc,char**argv){std::string input,output,pairs;for(int i=1;i<argc;++i){std::string a=argv[i];if(a=="--input"&&i+1<argc)input=argv[++i];else if(a=="--output"&&i+1<argc)output=argv[++i];else if(a=="--pairs-output"&&i+1<argc)pairs=argv[++i];else throw std::runtime_error("bad command");}if(input.empty()||output.empty()||pairs.empty())throw std::runtime_error("missing path");std::ifstream f(input);std::string line;std::getline(f,line);if(!line.empty()&&line.back()=='\r')line.pop_back();if(line!="U,V,d,su1,su2,su3,su4,su5,sv1,sv2,sv3,sv4,sv5,r,t,e,a,b,n")throw std::runtime_error("bad header");std::map<Key,std::vector<Rec>>G;uint64_t nr=0;while(std::getline(f,line))if(!line.empty()){auto z=parse(line);G[{z.U,z.V,z.d,z.su,z.sv}].push_back(z);++nr;}
 uint64_t raw=0,cg=0,rg=0,eg=0,dg=0,sg=0,deg=0,rolec=0,corrn=0;std::vector<Row>O;
 for(auto&kv:G){auto&g=kv.second;for(size_t i=0;i<g.size();++i)for(size_t j=i+1;j<g.size();++j){++raw;Rec x=g[i],y=g[j];if(std::gcd(x.r,y.r)!=1)continue;++cg;if(same_pkg(x,y))continue;uint32_t D=std::max(x.r*x.n,y.r*y.n);if(D>16583||D>=19*x.d)continue;++rg;if(x.d>(uint64_t)x.e*y.e)continue;++eg;if(!disjoint(x,y))continue;++dg;auto X=shape_supp(x),Y=shape_supp(y);auto uv=supp(x.U*x.V);std::set<uint32_t>C(uv.begin(),uv.end());bool ok=true;for(uint32_t p:X)if(p>=5&&!Y.count(p)&&!C.count(p)&&y.r%p)ok=false;for(uint32_t p:Y)if(p>=5&&!X.count(p)&&!C.count(p)&&x.r%p)ok=false;if(!ok)continue;++sg;if((__int128)x.d*x.d*x.d>=(__int128)64*D*D||x.d>std::min(x.n,y.n)-2||x.d>2*flog(D,2)*flog(D,3))continue;++deg;uint64_t rb=UINT32_MAX;bool used=false;std::set<uint32_t>P=X;P.insert(Y.begin(),Y.end());for(uint32_t p:P){if(C.count(p))continue;uint64_t v;if(X.count(p)&&Y.count(p))v=std::gcd((uint64_t)x.r*role_value(p,x),(uint64_t)y.r*role_value(p,y));else if(X.count(p))v=(uint64_t)x.r*role_value(p,x);else v=(uint64_t)y.r*role_value(p,y);rb=std::min(rb,v);used=true;}if(used&&x.d>rb)continue;++rolec;uint64_t cb=corr(x,y);if(same_shape(x,y))cb=std::min<uint64_t>(cb,(uint64_t)2*x.r*y.r);if(x.d>cb)continue;++corrn;if(std::tie(y.r,y.a,y.b,y.t,y.e)<std::tie(x.r,x.a,x.b,x.t,x.e))std::swap(x,y);O.push_back({x,y,D,(uint32_t)cb,(uint32_t)rb});}}
 std::sort(O.begin(),O.end());O.erase(std::unique(O.begin(),O.end()),O.end());std::ofstream o(output);o<<"U,V,d,su1,su2,su3,su4,su5,sv1,sv2,sv3,sv4,sv5,r,t,e1,a,b,n,s,u,e2,c,f,m,D,correspondence_bound,role_bound\n";for(auto&z:O){o<<z.x.U<<','<<z.x.V<<','<<z.x.d;for(auto q:z.x.su)o<<','<<q;for(auto q:z.x.sv)o<<','<<q;o<<','<<z.x.r<<','<<z.x.t<<','<<z.x.e<<','<<z.x.a<<','<<z.x.b<<','<<z.x.n<<','<<z.y.r<<','<<z.y.t<<','<<z.y.e<<','<<z.y.a<<','<<z.y.b<<','<<z.y.n<<','<<z.D<<','<<z.corr<<','<<z.role<<'\n';}
 using PK=std::tuple<uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t>;std::set<PK>Q;for(auto&z:O)Q.emplace(z.x.U,z.x.V,z.x.r,z.x.a,z.x.b,z.x.n,z.y.r,z.y.a,z.y.b,z.y.n);std::ofstream p(pairs);p<<"U,V,r,a,b,n,s,c,f,m\n";for(auto q:Q){auto[U,V,r,a,b,n,s,c,e,m]=q;p<<U<<','<<V<<','<<r<<','<<a<<','<<b<<','<<n<<','<<s<<','<<c<<','<<e<<','<<m<<'\n';}
 std::cout<<"package_states="<<nr<<" groups="<<G.size()<<" raw_state_pairs="<<raw<<" after_coprime_scales="<<cg<<" after_range="<<rg<<" after_extraction="<<eg<<" after_disjoint="<<dg<<" after_support="<<sg<<" after_degree="<<deg<<" after_role="<<rolec<<" after_correspondence="<<corrn<<" unique_state_pairs="<<O.size()<<" unique_orientation_pairs="<<Q.size()<<"\n";
}
