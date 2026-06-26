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

struct Rec {
    uint32_t U, d;
    std::array<uint32_t, 5> sigma{};
    uint32_t r, t, e, a, b, n;
};

struct Key {
    uint32_t U, d;
    std::array<uint32_t, 5> sigma{};
    bool operator<(const Key& o) const {
        return std::tie(U, d, sigma) < std::tie(o.U, o.d, o.sigma);
    }
};

struct PairRow {
    Rec x, y;
    uint32_t D, corr_bound, role_bound;
    bool operator<(const PairRow& o) const {
        return std::tie(x.U, x.d, x.sigma, D, x.r, x.a, x.b, y.r, y.a, y.b, x.t, x.e, y.t, y.e) <
               std::tie(o.x.U, o.x.d, o.x.sigma, o.D, o.x.r, o.x.a, o.x.b, o.y.r, o.y.a, o.y.b, o.x.t, o.x.e, o.y.t, o.y.e);
    }
    bool operator==(const PairRow& o) const {
        return x.U == o.x.U && x.d == o.x.d && x.sigma == o.x.sigma &&
               D == o.D && x.r == o.x.r && x.t == o.x.t && x.e == o.x.e &&
               x.a == o.x.a && x.b == o.x.b && y.r == o.y.r && y.t == o.y.t &&
               y.e == o.y.e && y.a == o.y.a && y.b == o.y.b;
    }
};

static std::vector<uint32_t> support(uint32_t x) {
    std::vector<uint32_t> out;
    if (x % 2 == 0) {
        out.push_back(2);
        while (x % 2 == 0) x /= 2;
    }
    for (uint32_t p = 3; (uint64_t)p * p <= x; p += 2) {
        if (x % p == 0) {
            out.push_back(p);
            while (x % p == 0) x /= p;
        }
    }
    if (x > 1) out.push_back(x);
    return out;
}

static uint32_t role_value(uint32_t p, const Rec& z) {
    uint32_t hits = 0, v = 0;
    for (uint32_t q : {z.a, z.b, z.n}) {
        if (q % p == 0) {
            ++hits;
            v = q;
        }
    }
    if (hits != 1) throw std::runtime_error("primitive role invariant failed");
    return v;
}

static std::set<uint32_t> shape_support(const Rec& z) {
    std::set<uint32_t> S;
    for (uint32_t q : {z.a, z.b, z.n}) {
        auto s = support(q);
        S.insert(s.begin(), s.end());
    }
    return S;
}

static bool disjoint(const Rec& x, const Rec& y) {
    std::array<uint64_t, 3> A = {(uint64_t)x.r * x.a, (uint64_t)x.r * x.b, (uint64_t)x.r * x.n};
    std::array<uint64_t, 3> B = {(uint64_t)y.r * y.a, (uint64_t)y.r * y.b, (uint64_t)y.r * y.n};
    for (auto a : A) {
        for (auto b : B) {
            if (a == b) return false;
        }
    }
    return true;
}

static bool same_package(const Rec& x, const Rec& y) {
    uint64_t xa = (uint64_t)x.r * x.a, xb = (uint64_t)x.r * x.b;
    uint64_t ya = (uint64_t)y.r * y.a, yb = (uint64_t)y.r * y.b;
    if (xa > xb) std::swap(xa, xb);
    if (ya > yb) std::swap(ya, yb);
    return xa == ya && xb == yb;
}

static bool same_unordered_shape(const Rec& x, const Rec& y) {
    return (x.a == y.a && x.b == y.b) || (x.a == y.b && x.b == y.a);
}

static bool support_compatible(const Rec& x, const Rec& y) {
    auto X = shape_support(x);
    auto Y = shape_support(y);
    auto cu = support(x.U);
    std::set<uint32_t> C(cu.begin(), cu.end());
    for (uint32_t p : X) {
        if (p >= 5 && !Y.count(p) && !C.count(p) && y.r % p != 0) return false;
    }
    for (uint32_t p : Y) {
        if (p >= 5 && !X.count(p) && !C.count(p) && x.r % p != 0) return false;
    }
    return true;
}

static uint64_t correspondence_bound(const Rec& x, const Rec& y) {
    uint64_t g0 = std::gcd((uint64_t)x.r * x.b, (uint64_t)y.r * y.b);
    uint64_t g1 = std::gcd((uint64_t)x.r * x.a, (uint64_t)y.r * y.a);
    uint64_t B0 = (uint64_t)x.r * x.b / g0;
    uint64_t E0 = (uint64_t)y.r * y.b / g0;
    uint64_t A0 = (uint64_t)x.r * x.a / g1;
    uint64_t C0 = (uint64_t)y.r * y.a / g1;
    return E0 * A0 + B0 * C0;
}

static uint32_t role_bound(const Rec& x, const Rec& y) {
    auto X = shape_support(x);
    auto Y = shape_support(y);
    auto cu = support(x.U);
    std::set<uint32_t> C(cu.begin(), cu.end());
    std::set<uint32_t> P = X;
    P.insert(Y.begin(), Y.end());
    uint64_t best = UINT32_MAX;
    bool used = false;
    for (uint32_t p : P) {
        if (C.count(p)) continue;
        uint64_t v;
        if (X.count(p) && Y.count(p)) {
            v = std::gcd((uint64_t)x.r * role_value(p, x), (uint64_t)y.r * role_value(p, y));
        } else if (X.count(p)) {
            v = (uint64_t)x.r * role_value(p, x);
        } else {
            v = (uint64_t)y.r * role_value(p, y);
        }
        best = std::min(best, v);
        used = true;
    }
    return used ? (uint32_t)std::min<uint64_t>(best, UINT32_MAX) : UINT32_MAX;
}

static Rec parse(const std::string& line) {
    std::stringstream ss(line);
    std::string s;
    std::vector<uint32_t> v;
    while (std::getline(ss, s, ',')) v.push_back((uint32_t)std::stoul(s));
    if (v.size() != 13) throw std::runtime_error("bad CSV row");
    Rec z;
    z.U = v[0];
    z.d = v[1];
    for (size_t i = 0; i < 5; ++i) z.sigma[i] = v[2 + i];
    z.r = v[7];
    z.t = v[8];
    z.e = v[9];
    z.a = v[10];
    z.b = v[11];
    z.n = v[12];
    return z;
}

int main(int argc, char** argv) {
    std::string input, output, pairs_output;
    uint32_t Dcap = 16583;
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "--input" && i + 1 < argc) input = argv[++i];
        else if (a == "--output" && i + 1 < argc) output = argv[++i];
        else if (a == "--pairs-output" && i + 1 < argc) pairs_output = argv[++i];
        else if (a == "--D-cap" && i + 1 < argc) Dcap = std::stoul(argv[++i]);
        else throw std::runtime_error("bad command line");
    }
    if (input.empty() || output.empty() || pairs_output.empty() || Dcap < 1) throw std::runtime_error("missing paths");

    std::ifstream in(input);
    if (!in) throw std::runtime_error("cannot open input");
    std::string line;
    std::getline(in, line);
    if (!line.empty() && line.back() == '\r') line.pop_back();
    if (line != "U,d,sigma1,sigma2,sigma3,sigma4,sigma5,r,t,e,a,b,n") throw std::runtime_error("bad header");

    std::map<Key, std::vector<Rec>> groups;
    uint64_t records = 0;
    while (std::getline(in, line)) {
        if (line.empty()) continue;
        Rec z = parse(line);
        groups[{z.U, z.d, z.sigma}].push_back(z);
        ++records;
    }

    uint64_t raw = 0, after_gcd = 0, after_range = 0, after_extraction = 0;
    uint64_t after_disjoint = 0, after_support = 0, after_degree = 0, after_role = 0, after_corr = 0;
    std::vector<PairRow> out;

    for (auto& kv : groups) {
        auto& g = kv.second;
        for (size_t i = 0; i < g.size(); ++i) {
            for (size_t j = i + 1; j < g.size(); ++j) {
                ++raw;
                Rec x = g[i], y = g[j];
                if (std::gcd(x.r, y.r) != 1) continue;
                ++after_gcd;
                if (same_package(x, y)) continue;
                uint64_t D64 = std::max((uint64_t)x.r * x.n, (uint64_t)y.r * y.n);
                if (D64 > Dcap) continue;
                uint32_t D = (uint32_t)D64;
                ++after_range;
                if (x.d > (uint64_t)x.e * y.e) continue;
                ++after_extraction;
                if (!disjoint(x, y)) continue;
                ++after_disjoint;
                if (!support_compatible(x, y)) continue;
                ++after_support;
                if ((__int128)x.d * x.d * x.d >= (__int128)64 * D * D || x.d > std::min(x.n, y.n) - 2) continue;
                ++after_degree;
                uint32_t rb = role_bound(x, y);
                if (rb != UINT32_MAX && x.d > rb) continue;
                ++after_role;
                uint64_t cb = correspondence_bound(x, y);
                if (same_unordered_shape(x, y)) cb = std::min<uint64_t>(cb, (uint64_t)2 * x.r * y.r);
                if (x.d > cb) continue;
                ++after_corr;
                if (std::tie(y.r, y.a, y.b, y.t, y.e) < std::tie(x.r, x.a, x.b, x.t, x.e)) std::swap(x, y);
                out.push_back({x, y, D, (uint32_t)std::min<uint64_t>(cb, UINT32_MAX), rb});
            }
        }
    }

    std::sort(out.begin(), out.end());
    out.erase(std::unique(out.begin(), out.end()), out.end());

    std::ofstream f(output);
    f << "U,d,sigma1,sigma2,sigma3,sigma4,sigma5,r,t,e1,a,b,n,s,u,e2,c,f,m,D,correspondence_bound,role_bound\n";
    for (const auto& p : out) {
        f << p.x.U << ',' << p.x.d;
        for (uint32_t s : p.x.sigma) f << ',' << s;
        f << ',' << p.x.r << ',' << p.x.t << ',' << p.x.e << ',' << p.x.a << ',' << p.x.b << ',' << p.x.n
          << ',' << p.y.r << ',' << p.y.t << ',' << p.y.e << ',' << p.y.a << ',' << p.y.b << ',' << p.y.n
          << ',' << p.D << ',' << p.corr_bound << ',' << p.role_bound << '\n';
    }

    using PKey = std::tuple<uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t>;
    std::set<PKey> uniq;
    for (const auto& p : out) {
        uniq.emplace(p.x.U, p.x.r, p.x.a, p.x.b, p.x.n, p.y.r, p.y.a, p.y.b, p.y.n);
    }
    std::ofstream pf(pairs_output);
    pf << "U,r,a,b,n,s,c,f,m\n";
    for (auto z : uniq) {
        auto [U, r, a, b, n, s, c, endpoint, m] = z;
        pf << U << ',' << r << ',' << a << ',' << b << ',' << n << ','
           << s << ',' << c << ',' << endpoint << ',' << m << '\n';
    }

    std::cout << "package_records=" << records
              << " groups=" << groups.size()
              << " raw_state_pairs=" << raw
              << " after_coprime_scales=" << after_gcd
              << " after_range=" << after_range
              << " after_extraction=" << after_extraction
              << " after_disjoint=" << after_disjoint
              << " after_support=" << after_support
              << " after_degree=" << after_degree
              << " after_role=" << after_role
              << " after_correspondence=" << after_corr
              << " unique_state_pairs=" << out.size()
              << " unique_orientation_pairs=" << uniq.size()
              << "\n";
}
