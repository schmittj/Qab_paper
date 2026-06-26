#include <algorithm>
#include <array>
#include <cstdint>
#include <cmath>
#include <fstream>
#include <iostream>
#include <map>
#include <numeric>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>
#ifdef _OPENMP
#include <omp.h>
#endif

struct PE{uint32_t p,a;};
struct Core{uint32_t r,t,d;std::vector<PE> defects;};
struct Choice{uint32_t coeff;std::array<uint32_t,5> sigma{};uint8_t len=0;};
struct Rec{
 uint32_t U,V,d,r,t,e,a,b,n;std::array<uint32_t,5> su{},sv{};uint8_t lu=0,lv=0;
 bool operator<(const Rec&o)const{return std::tie(U,V,d,su,sv,r,t,e,n,a,b)<std::tie(o.U,o.V,o.d,o.su,o.sv,o.r,o.t,o.e,o.n,o.a,o.b);} 
 bool operator==(const Rec&o)const{return U==o.U&&V==o.V&&d==o.d&&r==o.r&&t==o.t&&e==o.e&&a==o.a&&b==o.b&&n==o.n&&su==o.su&&sv==o.sv;}
};
static std::vector<PE> factor(uint32_t x){std::vector<PE>o;if(x%2==0){uint32_t a=0;do{x/=2;++a;}while(x%2==0);o.push_back({2,a});}for(uint32_t p=3;(uint64_t)p*p<=x;p+=2)if(x%p==0){uint32_t a=0;do{x/=p;++a;}while(x%p==0);o.push_back({p,a});}if(x>1)o.push_back({x,1});return o;}
static uint32_t val(uint32_t x,uint32_t p){uint32_t a=0;while(x%p==0){x/=p;++a;}return a;}
static std::vector<uint32_t> supp(uint32_t x){std::vector<uint32_t>o;for(auto z:factor(x))o.push_back(z.p);return o;}
static void smooth_rec(const std::vector<uint32_t>&ps,size_t i,uint64_t x,uint32_t lim,std::vector<uint32_t>&o){if(i==ps.size()){o.push_back((uint32_t)x);return;}uint32_t p=ps[i];while(x<=lim){smooth_rec(ps,i+1,x,lim,o);if(x>lim/p)break;x*=p;}}
static std::vector<uint32_t> radical_sieve(uint32_t L){std::vector<uint32_t>r((size_t)L+1,1);r[0]=0;for(uint32_t p=2;p<=L;++p)if(r[p]==1)for(uint64_t j=p;j<=L;j+=p)r[(size_t)j]*=p;return r;}
static std::vector<uint8_t> prime_sieve(uint32_t L){std::vector<uint8_t>p((size_t)L+1,1);p[0]=p[1]=0;for(uint32_t q=2;(uint64_t)q*q<=L;++q)if(p[q])for(uint64_t j=(uint64_t)q*q;j<=L;j+=q)p[(size_t)j]=0;return p;}
static bool powerful(uint32_t n,uint32_t r){return n%((uint64_t)r*r)==0;}
static bool known_irred(uint32_t x,uint32_t y,uint32_t n,const std::vector<uint32_t>&rad,const std::vector<uint8_t>&prime){if(x>y)std::swap(x,y);if(x>1&&rad[x]==x&&rad[y]==y)return true;if(x==2||y==2)return true;if(x==1&&rad[n]==n)return true;if(prime[n])return true;if(n%2==0&&n>4&&prime[n/2])return true;if(x>1&&!powerful(x,rad[x])){long double th=(long double)x*std::max(11.21685874L,std::log2((long double)x));if((long double)y>=th)return true;}return false;}
static std::vector<Core> cores_for_e(uint32_t e,uint32_t rmax){std::vector<Core>o;for(uint32_t r=1;r<=rmax;++r){auto rf=factor(r);for(uint32_t t=1;t<=r;++t){uint32_t d=t*e;if(d>224)break;Core c{r,t,d,{}};for(auto z:rf)if(val(t,z.p)<z.a)c.defects.push_back(z);o.push_back(std::move(c));}}return o;}

static void choices_rec(const std::vector<PE>&pf,size_t i,uint32_t endpoint,uint32_t other,uint32_t e,const Core&c,bool leading,uint32_t coeff,std::array<uint32_t,5> sig,uint8_t len,std::vector<Choice>&out){
 if(i==pf.size()){if(coeff>1)out.push_back({coeff,sig,len});return;}
 uint32_t p=pf[i].p,kappa=pf[i].a;bool deficient=false;for(auto z:c.defects)if(z.p==p){deficient=true;break;}
 // Leave p outside the endpoint coefficient.  This is allowed only in a unit packet and never at a deficient endpoint prime.
 if(!deficient && (e%p==0 || e%p==(p-2)%p))choices_rec(pf,i+1,endpoint,other,e,c,leading,coeff,sig,len,out);
 // Put p into the endpoint coefficient. lambda is the exponent in the primitive factor coefficient.
 for(uint32_t lambda=1;lambda<=kappa;++lambda){
   if(((uint64_t)c.t*lambda)%c.r)continue;uint32_t A=(uint32_t)(((uint64_t)c.t*lambda)/c.r);if(A==0||A>kappa)continue;
   uint64_t num=(uint64_t)other*lambda;if(num%kappa)continue;uint32_t w=(uint32_t)(num/kappa);if(w<1||w>other||w>e)continue;
   if((e-w)%p!=0 && (e-w)%p!=(p-2)%p)continue;
   if(deficient){if(p>7||kappa<p||((uint64_t)e*kappa)%((uint64_t)p*other))continue;}
   uint64_t next=(uint64_t)coeff;for(uint32_t z=0;z<A;++z)next*=p;if(next>endpoint)continue;
   auto ns=sig;if(len>=5)throw std::runtime_error("too many coefficient primes");ns[len]=(uint32_t)((uint64_t)c.t*w);
   choices_rec(pf,i+1,endpoint,other,e,c,leading,(uint32_t)next,ns,(uint8_t)(len+1),out);
 }
}
static std::vector<Choice> endpoint_choices(uint32_t endpoint,uint32_t other,uint32_t e,const Core&c,bool leading){std::vector<Choice>o;std::array<uint32_t,5>s{};choices_rec(factor(endpoint),0,endpoint,other,e,c,leading,1,s,0,o);std::sort(o.begin(),o.end(),[](auto&a,auto&b){return std::tie(a.coeff,a.sigma)<std::tie(b.coeff,b.sigma);});o.erase(std::unique(o.begin(),o.end(),[](auto&a,auto&b){return a.coeff==b.coeff&&a.sigma==b.sigma;}),o.end());return o;}

int main(int argc,char**argv){uint32_t emin=2,emax=224,rmax=139;int threads=25;bool keep=true;std::string output;for(int i=1;i<argc;++i){std::string a=argv[i];if(a=="--e-start"&&i+1<argc)emin=std::stoul(argv[++i]);else if(a=="--e-end"&&i+1<argc)emax=std::stoul(argv[++i]);else if(a=="--r-max"&&i+1<argc)rmax=std::stoul(argv[++i]);else if(a=="--threads"&&i+1<argc)threads=std::stoi(argv[++i]);else if(a=="--output"&&i+1<argc)output=argv[++i];else if(a=="--keep-known-irreducible")keep=true;else if(a=="--use-known-irreducible-filter")keep=false;else throw std::runtime_error("bad command line");}if(output.empty()||emin<2||emin>emax||emax>224||rmax<1||rmax>139)throw std::runtime_error("bad domain");
#ifdef _OPENMP
 omp_set_num_threads(threads);int nt=omp_get_max_threads();
#else
 (void)threads;int nt=1;
#endif
 auto rad=radical_sieve(16583);auto prime=prime_sieve(16583);std::vector<std::vector<Rec>>local(nt);std::vector<uint64_t>totals(nt),shapes(nt),coretests(nt),choicepairs(nt),kept(nt);
#pragma omp parallel for schedule(dynamic,1)
 for(int64_t ee=emin;ee<=(int64_t)emax;++ee){int tid=0;
#ifdef _OPENMP
 tid=omp_get_thread_num();
#endif
  uint32_t e=(uint32_t)ee;auto cores=cores_for_e(e,rmax);if(cores.empty())continue;uint32_t nmax=0;for(auto&c:cores)nmax=std::max<uint32_t>(nmax,std::min<uint32_t>(28*e,(19*c.d-1)/c.r));if(nmax<e+4)continue;auto ps=supp(e);auto q=supp(e+2);ps.insert(ps.end(),q.begin(),q.end());std::sort(ps.begin(),ps.end());ps.erase(std::unique(ps.begin(),ps.end()),ps.end());std::vector<uint32_t>ns;smooth_rec(ps,0,1,nmax,ns);std::sort(ns.begin(),ns.end());ns.erase(std::unique(ns.begin(),ns.end()),ns.end());
  for(uint32_t n:ns){if(n<e+4)continue;++totals[tid];for(uint32_t a=2;a<n-1;++a){uint32_t b=n-a;if(b<2||std::gcd(a,b)!=1)continue;if(a>14*e||b>14*e)continue;if(!keep&&known_irred(a,b,n,rad,prime))continue;++shapes[tid];for(const auto&c:cores){if(n<c.d+2||n>16583/c.r||c.r*n>=19*c.d)continue;bool defect_ok=true;for(auto z:c.defects){if(n%z.p==0){defect_ok=false;break;}if(a%z.p==0||b%z.p==0)continue;if(e>z.p-2){defect_ok=false;break;}}if(!defect_ok)continue;++coretests[tid];auto L=endpoint_choices(a,b,e,c,true);if(L.empty())continue;auto R=endpoint_choices(b,a,e,c,false);if(R.empty())continue;choicepairs[tid]+=(uint64_t)L.size()*R.size();for(auto&u:L)for(auto&v:R){if(std::gcd(u.coeff,v.coeff)!=1)continue;Rec z;z.U=u.coeff;z.V=v.coeff;z.d=c.d;z.r=c.r;z.t=c.t;z.e=e;z.a=a;z.b=b;z.n=n;z.su=u.sigma;z.sv=v.sigma;z.lu=u.len;z.lv=v.len;local[tid].push_back(z);++kept[tid];}}
  }}
 }
 std::vector<Rec>out;for(auto&v:local)out.insert(out.end(),v.begin(),v.end());std::sort(out.begin(),out.end());out.erase(std::unique(out.begin(),out.end()),out.end());std::ofstream f(output);f<<"U,V,d,su1,su2,su3,su4,su5,sv1,sv2,sv3,sv4,sv5,r,t,e,a,b,n\n";for(auto&z:out)f<<z.U<<','<<z.V<<','<<z.d<<','<<z.su[0]<<','<<z.su[1]<<','<<z.su[2]<<','<<z.su[3]<<','<<z.su[4]<<','<<z.sv[0]<<','<<z.sv[1]<<','<<z.sv[2]<<','<<z.sv[3]<<','<<z.sv[4]<<','<<z.r<<','<<z.t<<','<<z.e<<','<<z.a<<','<<z.b<<','<<z.n<<'\n';uint64_t A=0,B=0,C=0,D=0,E=0;for(int i=0;i<nt;++i){A+=totals[i];B+=shapes[i];C+=coretests[i];D+=choicepairs[i];E+=kept[i];}std::cout<<"smooth_totals="<<A<<" reducible_shape_tests="<<B<<" core_tests="<<C<<" coefficient_choice_pairs="<<D<<" raw_states="<<E<<" unique_states="<<out.size()<<"\n";
}
