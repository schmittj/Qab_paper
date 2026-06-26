#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_set>
#include <vector>
#ifdef _OPENMP
#include <omp.h>
#endif

struct PrimeExp { uint32_t p, a; };
struct Core {
    uint32_t r, t;
    std::vector<uint32_t> lambda; // aligned with coefficient primes
    std::vector<uint32_t> good_defect;
    std::vector<uint32_t> endpoint_defect;
};
struct Record {
    uint32_t U,r,t,e,d,a,b,n;
    std::array<uint32_t,3> sigma{};
    uint8_t sigma_len=0;
    bool operator<(const Record& o) const {
        return std::tie(U,d,sigma_len,sigma,r,t,e,n,a,b) <
               std::tie(o.U,o.d,o.sigma_len,o.sigma,o.r,o.t,o.e,o.n,o.a,o.b);
    }
    bool operator==(const Record& o) const {
        return U==o.U&&r==o.r&&t==o.t&&e==o.e&&d==o.d&&a==o.a&&b==o.b&&n==o.n&&sigma_len==o.sigma_len&&sigma==o.sigma;
    }
};

static std::vector<PrimeExp> factorization(uint32_t x) {
    std::vector<PrimeExp> out;
    if ((x&1u)==0) { uint32_t a=0; do{x>>=1;++a;}while((x&1u)==0); out.push_back({2,a}); }
    for(uint32_t p=3;(uint64_t)p*p<=x;p+=2) if(x%p==0){uint32_t a=0;do{x/=p;++a;}while(x%p==0);out.push_back({p,a});}
    if(x>1) out.push_back({x,1});
    return out;
}
static uint32_t valuation(uint32_t x,uint32_t p){uint32_t a=0;while(x%p==0){x/=p;++a;}return a;}
static std::vector<uint32_t> support(uint32_t x){std::vector<uint32_t> o;for(auto z:factorization(x))o.push_back(z.p);return o;}
static void generate_smooth(const std::vector<uint32_t>& ps,size_t i,uint64_t cur,uint32_t lim,std::vector<uint32_t>& out){
    if(i==ps.size()){out.push_back((uint32_t)cur);return;} generate_smooth(ps,i+1,cur,lim,out); while(cur<=lim/ps[i]){cur*=ps[i];generate_smooth(ps,i+1,cur,lim,out);} }
static std::vector<uint32_t> radical_sieve(uint32_t limit){std::vector<uint32_t> rad((size_t)limit+1,1);rad[0]=0;for(uint32_t p=2;p<=limit;++p)if(rad[p]==1)for(uint64_t j=p;j<=limit;j+=p)rad[(size_t)j]*=p;return rad;}
static std::vector<uint8_t> prime_sieve(uint32_t limit){std::vector<uint8_t> pr((size_t)limit+1,1);pr[0]=0;if(limit>=1)pr[1]=0;for(uint32_t p=2;(uint64_t)p*p<=limit;++p)if(pr[p])for(uint64_t j=(uint64_t)p*p;j<=limit;j+=p)pr[(size_t)j]=0;return pr;}
static bool powerful(uint32_t n,uint32_t rad){uint64_t rr=(uint64_t)rad*rad;return rr&&n%rr==0;}
static bool known_irreducible(uint32_t x,uint32_t y,uint32_t n,const std::vector<uint32_t>& rad,const std::vector<uint8_t>& prime){
    if(x>y)std::swap(x,y);
    if(x>1 && rad[x]==x && rad[y]==y)return true;
    if(x==2||y==2)return true;
    if(x==1&&rad[n]==n)return true;
    if(prime[n])return true;
    if((n&1u)==0&&n>4&&prime[n/2])return true;
    if(x>1&&!powerful(x,rad[x])){constexpr long double c=11.21685874L; long double threshold=(long double)x*std::max(c,std::log2((long double)x));if((long double)y>=threshold)return true;}
    return false;
}
static uint32_t degree_upper(uint32_t D){uint32_t lo=0,hi=200000;while(lo<hi){uint32_t m=lo+(hi-lo+1)/2;__int128 lhs=(__int128)m*m*m,rhs=(__int128)64*D*D;if(lhs<rhs)lo=m;else hi=m-1;}return lo;}
static uint32_t coefficient_D_cap(uint32_t U){
    static const uint32_t caps[27]={0,0,6816241,1230611,508652,286175,188395,136208,104733,84090,69701,59198,51249,45056,40115,36095,32767,29975,27601,25561,23792,22244,20880,19670,18589,17619,16743};
    return caps[U];
}
static uint32_t linear_D_factor(uint32_t U){
    static const uint32_t factors[27]={0,0,48,27,20,17,15,13,12,11,11,10,10,9,9,9,8,8,8,8,8,8,7,7,7,7,7};
    return factors[U];
}
static std::vector<Core> build_cores(uint32_t U,uint32_t rmax){
    auto uf=factorization(U); std::vector<Core> out;
    for(uint32_t r=1;r<=rmax;++r){auto rf=factorization(r);for(uint32_t t=1;t<=r;++t){
        Core c; c.r=r;c.t=t;bool ok=true;
        for(auto z:uf){uint64_t num=(uint64_t)r*z.a;if(num%t){ok=false;break;}c.lambda.push_back((uint32_t)(num/t));}
        if(!ok)continue;
        for(auto z:rf)if(valuation(t,z.p)<z.a){
            bool coeff=false;for(auto w:uf)if(w.p==z.p){coeff=true;break;}
            if(coeff){if(z.p>7){ok=false;break;}c.endpoint_defect.push_back(z.p);}else c.good_defect.push_back(z.p);
        }
        if(ok)out.push_back(std::move(c));
    }} return out;
}

int main(int argc,char**argv){
    uint32_t U=2,e_start=2,e_end=143799,Dmin=16584,Doverride=0,Coverride=0,rmax=139;int threads=25;bool keep_known=false;std::string output;
    for(int i=1;i<argc;++i){std::string a=argv[i];if(a=="--U"&&i+1<argc)U=std::stoul(argv[++i]);else if(a=="--e-start"&&i+1<argc)e_start=std::stoul(argv[++i]);else if(a=="--e-end"&&i+1<argc)e_end=std::stoul(argv[++i]);else if(a=="--threads"&&i+1<argc)threads=std::stoi(argv[++i]);else if(a=="--output"&&i+1<argc)output=argv[++i];else if(a=="--D-min"&&i+1<argc)Dmin=std::stoul(argv[++i]);else if(a=="--D-cap"&&i+1<argc)Doverride=std::stoul(argv[++i]);else if(a=="--linear-factor"&&i+1<argc)Coverride=std::stoul(argv[++i]);else if(a=="--r-max"&&i+1<argc)rmax=std::stoul(argv[++i]);else if(a=="--keep-known-irreducible")keep_known=true;else throw std::runtime_error("bad command line");}
    if(U<2||U>26||e_start<2||e_start>e_end||output.empty()||rmax<1||rmax>139||Dmin<1)throw std::runtime_error("invalid domain");
#ifdef _OPENMP
    omp_set_num_threads(threads);
#else
    (void)threads;
#endif
    const uint32_t Dcap=Doverride?Doverride:coefficient_D_cap(U), dcap=degree_upper(Dcap), C=Coverride?Coverride:linear_D_factor(U);
    const uint32_t max_n=Dcap; // sieve shared by all e
    auto rad=radical_sieve(max_n); auto prime=prime_sieve(max_n); auto uf=factorization(U); auto cores=build_cores(U,rmax);
    int nt=1;
#ifdef _OPENMP
    nt=omp_get_max_threads();
#endif
    std::vector<std::vector<Record>> local((size_t)nt);
    std::vector<uint64_t> smooth_count(nt),generic_pairs(nt),additive_hits(nt),reducible_hits(nt),state_tests(nt),state_kept(nt);
    auto T=std::chrono::steady_clock::now();
#pragma omp parallel for schedule(dynamic,1)
    for(int64_t ee=e_start;ee<=(int64_t)e_end;++ee){
        int tid=0;
#ifdef _OPENMP
        tid=omp_get_thread_num();
#endif
        uint32_t e=(uint32_t)ee;
        std::vector<const Core*> active; uint32_t nlim_max=0;
        for(const auto& c:cores){uint64_t d=(uint64_t)c.t*e;if(d>dcap)continue; if((uint64_t)C*d<Dmin)continue; bool ok=true;for(uint32_t q:c.good_defect)if(e>q-2){ok=false;break;}if(!ok)continue;uint32_t nlim=(uint32_t)std::min<uint64_t>(Dcap/c.r,(uint64_t)C*d/c.r);if(nlim<e+4)continue;active.push_back(&c);nlim_max=std::max(nlim_max,nlim);} if(active.empty())continue;
        auto ps=support(U);auto pe=support(e);auto pe2=support(e+2);ps.insert(ps.end(),pe.begin(),pe.end());ps.insert(ps.end(),pe2.begin(),pe2.end());std::sort(ps.begin(),ps.end());ps.erase(std::unique(ps.begin(),ps.end()),ps.end());
        std::vector<uint32_t> vals;generate_smooth(ps,0,1,nlim_max,vals);std::sort(vals.begin(),vals.end());vals.erase(std::unique(vals.begin(),vals.end()),vals.end());smooth_count[tid]+=vals.size();std::unordered_set<uint32_t> mem(vals.begin(),vals.end());
        for(uint32_t a:vals){
            bool coeff_ok=true;std::array<uint32_t,3> kappas{};for(size_t j=0;j<uf.size();++j){kappas[j]=valuation(a,uf[j].p);if(kappas[j]==0){coeff_ok=false;break;}}if(!coeff_ok)continue;
            uint64_t bmax=nlim_max-a;for(size_t j=0;j<uf.size();++j)bmax=std::min<uint64_t>(bmax,(uint64_t)e*kappas[j]);auto stop=std::upper_bound(vals.begin(),vals.end(),bmax);
            for(auto it=vals.begin();it!=stop;++it){uint32_t b=*it;if(std::gcd(a,b)!=1)continue;++generic_pairs[tid];uint32_t n=a+b;if(!mem.count(n)||n<e+4)continue;++additive_hits[tid];if(!keep_known&&known_irreducible(a,b,n,rad,prime))continue;++reducible_hits[tid];
                for(const Core* cp:active){const Core& c=*cp;uint64_t d=(uint64_t)c.t*e;uint32_t nlim=(uint32_t)std::min<uint64_t>(Dcap/c.r,(uint64_t)C*d/c.r);if(n>nlim)continue;++state_tests[tid];bool ok=true;std::array<uint32_t,3> sigma{};
                    for(size_t j=0;j<uf.size();++j){uint32_t lam=c.lambda[j],kap=kappas[j];if(lam>kap){ok=false;break;}uint64_t num=(uint64_t)b*lam;if(num%kap){ok=false;break;}uint32_t w=(uint32_t)(num/kap);if(w<1||w>b||w>e){ok=false;break;}uint32_t p=uf[j].p;if(e%p!=w%p && e%p!=(w+p-2)%p){ok=false;break;}uint64_t sig=(uint64_t)c.t*w;if(sig>UINT32_MAX){ok=false;break;}sigma[j]=(uint32_t)sig;}
                    if(!ok)continue;
                    for(uint32_t q:c.good_defect){
                        if(a%q==0||b%q==0||n%q==0){ok=false;break;}
                    }
                    if(!ok)continue;
                    for(uint32_t q:c.endpoint_defect){uint32_t kap=valuation(a,q);if(kap<q||((uint64_t)e*kap)%((uint64_t)q*b)!=0){ok=false;break;}}if(!ok)continue;
                    ++state_kept[tid];Record rec;rec.U=U;rec.r=c.r;rec.t=c.t;rec.e=e;rec.d=(uint32_t)d;rec.a=a;rec.b=b;rec.n=n;rec.sigma_len=(uint8_t)uf.size();rec.sigma=sigma;local[tid].push_back(rec);
                }
            }
        }
    }
    std::vector<Record> records;for(auto&v:local)records.insert(records.end(),v.begin(),v.end());std::sort(records.begin(),records.end());records.erase(std::unique(records.begin(),records.end()),records.end());
    std::ofstream out(output);out<<"U,d,sigma1,sigma2,sigma3,r,t,e,a,b,n\n";for(auto&x:records)out<<x.U<<','<<x.d<<','<<x.sigma[0]<<','<<x.sigma[1]<<','<<x.sigma[2]<<','<<x.r<<','<<x.t<<','<<x.e<<','<<x.a<<','<<x.b<<','<<x.n<<'\n';
    uint64_t sc=0,gp=0,ah=0,rh=0,st=0,sk=0;for(int i=0;i<nt;++i){sc+=smooth_count[i];gp+=generic_pairs[i];ah+=additive_hits[i];rh+=reducible_hits[i];st+=state_tests[i];sk+=state_kept[i];}
    std::cout<<"U="<<U<<" cores="<<cores.size()<<" smooth_entries="<<sc<<" generic_pairs="<<gp<<" additive_hits="<<ah<<" reducible_hits="<<rh<<" state_tests="<<st<<" state_kept_raw="<<sk<<" unique_states="<<records.size()<<" seconds="<<std::chrono::duration<double>(std::chrono::steady_clock::now()-T).count()<<"\n";
}
