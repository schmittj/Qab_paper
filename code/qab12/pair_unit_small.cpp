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

struct Rec {uint32_t d,r,e,a,b,n;};
struct Row {
    Rec x,y; uint32_t D,role_bound,corr_bound;
    bool operator<(const Row&o)const{
        return std::tie(x.d,D,x.r,x.a,x.b,y.r,y.a,y.b)<
               std::tie(o.x.d,o.D,o.x.r,o.x.a,o.x.b,o.y.r,o.y.a,o.y.b);
    }
    bool operator==(const Row&o)const{
        return x.d==o.x.d&&x.r==o.x.r&&x.a==o.x.a&&x.b==o.x.b&&
               y.r==o.y.r&&y.a==o.y.a&&y.b==o.y.b;
    }
};
static std::vector<uint32_t> support(uint32_t x){
    std::vector<uint32_t> out;
    if(x%2==0){out.push_back(2);while(x%2==0)x/=2;}
    for(uint32_t p=3;(uint64_t)p*p<=x;p+=2)if(x%p==0){out.push_back(p);while(x%p==0)x/=p;}
    if(x>1)out.push_back(x);
    return out;
}
static Rec parse(const std::string& line){
    std::stringstream ss(line);std::string s;std::vector<uint32_t> v;
    while(std::getline(ss,s,','))v.push_back((uint32_t)std::stoul(s));
    if(v.size()!=6)throw std::runtime_error("bad row");
    return {v[0],v[1],v[2],v[3],v[4],v[5]};
}
static bool same_package(const Rec&x,const Rec&y){
    uint64_t xa=(uint64_t)x.r*x.a,xb=(uint64_t)x.r*x.b,ya=(uint64_t)y.r*y.a,yb=(uint64_t)y.r*y.b;
    if(xa>xb)std::swap(xa,xb);
    if(ya>yb)std::swap(ya,yb);
    return xa==ya&&xb==yb;
}
static bool disjoint(const Rec&x,const Rec&y){
    std::array<uint64_t,3>A={(uint64_t)x.r*x.a,(uint64_t)x.r*x.b,(uint64_t)x.r*x.n};
    std::array<uint64_t,3>B={(uint64_t)y.r*y.a,(uint64_t)y.r*y.b,(uint64_t)y.r*y.n};
    for(uint64_t a:A)for(uint64_t b:B)if(a==b)return false;
    return true;
}
static std::set<uint32_t> shape_support(const Rec&x){
    std::set<uint32_t>S;for(uint32_t v:{x.a,x.b,x.n}){auto q=support(v);S.insert(q.begin(),q.end());}return S;
}
static bool support_compatible(const Rec&x,const Rec&y){
    auto X=shape_support(x),Y=shape_support(y);
    for(uint32_t p:X)if(p>=5&&!Y.count(p)&&y.r%p!=0)return false;
    for(uint32_t p:Y)if(p>=5&&!X.count(p)&&x.r%p!=0)return false;
    return true;
}
static uint32_t role_value(uint32_t p,const Rec&x){
    uint32_t hits=0,v=0;for(uint32_t q:{x.a,x.b,x.n})if(q%p==0){++hits;v=q;}
    if(hits!=1)throw std::runtime_error("primitive role invariant");
    return v;
}
static uint32_t role_bound(const Rec&x,const Rec&y){
    auto X=shape_support(x),Y=shape_support(y),P=X;P.insert(Y.begin(),Y.end());
    uint64_t best=UINT32_MAX;
    for(uint32_t p:P){
        uint64_t v;
        if(X.count(p)&&Y.count(p))v=std::gcd((uint64_t)x.r*role_value(p,x),(uint64_t)y.r*role_value(p,y));
        else if(X.count(p))v=(uint64_t)x.r*role_value(p,x);
        else v=(uint64_t)y.r*role_value(p,y);
        best=std::min(best,v);
    }
    return (uint32_t)std::min<uint64_t>(best,UINT32_MAX);
}
static uint64_t correspondence_bound(const Rec&x,const Rec&y){
    uint64_t g0=std::gcd((uint64_t)x.r*x.b,(uint64_t)y.r*y.b);
    uint64_t g1=std::gcd((uint64_t)x.r*x.a,(uint64_t)y.r*y.a);
    uint64_t B0=(uint64_t)x.r*x.b/g0,E0=(uint64_t)y.r*y.b/g0;
    uint64_t A0=(uint64_t)x.r*x.a/g1,C0=(uint64_t)y.r*y.a/g1;
    return E0*A0+B0*C0;
}
static bool same_unordered_shape(const Rec&x,const Rec&y){return (x.a==y.a&&x.b==y.b)||(x.a==y.b&&x.b==y.a);}

int main(int argc,char**argv){
    std::string input,output,pairs_output;
    for(int i=1;i<argc;++i){std::string a=argv[i];
        if(a=="--input"&&i+1<argc)input=argv[++i];
        else if(a=="--output"&&i+1<argc)output=argv[++i];
        else if(a=="--pairs-output"&&i+1<argc)pairs_output=argv[++i];
        else throw std::runtime_error("bad command line");}
    if(input.empty()||output.empty()||pairs_output.empty())throw std::runtime_error("missing path");
    std::ifstream in(input);if(!in)throw std::runtime_error("cannot open input");
    std::string line;std::getline(in,line);if(!line.empty()&&line.back()=='\r')line.pop_back();
    if(line!="d,r,e,a,b,n")throw std::runtime_error("bad header");
    std::map<uint32_t,std::vector<Rec>> groups;uint64_t records=0;
    while(std::getline(in,line))if(!line.empty()){Rec z=parse(line);groups[z.d].push_back(z);++records;}
    uint64_t raw=0,after_gcd=0,after_distinct=0,after_disjoint=0,after_support=0,after_toric=0,after_role=0,after_corr=0;
    std::vector<Row> rows;
    for(auto&kv:groups){auto&g=kv.second;
        for(size_t i=0;i<g.size();++i)for(size_t j=i+1;j<g.size();++j){
            ++raw;Rec x=g[i],y=g[j];
            if(std::gcd(x.r,y.r)!=1)continue;
            ++after_gcd;
            if(same_package(x,y))continue;
            ++after_distinct;
            if(!disjoint(x,y))continue;
            ++after_disjoint;
            if(!support_compatible(x,y))continue;
            ++after_support;
            uint32_t D=std::max(x.r*x.n,y.r*y.n),d=x.d;
            if((__int128)d*d*d>=(__int128)64*D*D||d>std::min(x.n,y.n)-2)continue;
            ++after_toric;
            uint32_t rb=role_bound(x,y);
            if(d>rb)continue;
            ++after_role;
            uint64_t cb=correspondence_bound(x,y);
            if(same_unordered_shape(x,y))cb=std::min<uint64_t>(cb,(uint64_t)2*x.r*y.r);
            if(d>cb)continue;
            ++after_corr;
            if(std::tie(y.r,y.a,y.b)<std::tie(x.r,x.a,x.b))std::swap(x,y);
            rows.push_back({x,y,D,rb,(uint32_t)std::min<uint64_t>(cb,UINT32_MAX)});
        }
    }
    std::sort(rows.begin(),rows.end());rows.erase(std::unique(rows.begin(),rows.end()),rows.end());
    std::ofstream out(output);out<<"d,r,e1,a,b,n,s,e2,c,f,m,D,role_bound,correspondence_bound\n";
    for(auto&p:rows)out<<p.x.d<<','<<p.x.r<<','<<p.x.e<<','<<p.x.a<<','<<p.x.b<<','<<p.x.n<<','<<p.y.r<<','<<p.y.e<<','<<p.y.a<<','<<p.y.b<<','<<p.y.n<<','<<p.D<<','<<p.role_bound<<','<<p.corr_bound<<'\n';
    using K=std::tuple<uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t>;
    std::set<K> pairs;for(auto&p:rows)pairs.emplace(p.x.r,p.x.a,p.x.b,p.x.n,p.y.r,p.y.a,p.y.b,p.y.n);
    std::ofstream po(pairs_output);po<<"r,a,b,n,s,c,f,m\n";for(auto z:pairs){auto[r,a,b,n,s,c,f,m]=z;po<<r<<','<<a<<','<<b<<','<<n<<','<<s<<','<<c<<','<<f<<','<<m<<'\n';}
    std::cout<<"package_records="<<records<<" groups="<<groups.size()<<" raw_state_pairs="<<raw
             <<" after_coprime_scales="<<after_gcd<<" after_distinct_packages="<<after_distinct
             <<" after_disjoint="<<after_disjoint<<" after_support="<<after_support
             <<" after_toric="<<after_toric<<" after_role="<<after_role
             <<" after_correspondence="<<after_corr<<" unique_state_pairs="<<rows.size()
             <<" unique_orientation_pairs="<<pairs.size()<<"\n";
}
