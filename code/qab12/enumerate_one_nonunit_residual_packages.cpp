#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>
#ifdef _OPENMP
#include <omp.h>
#endif

struct PrimeExp { uint32_t p, a; };

struct Core {
    uint32_t r, t, d;
    std::vector<uint32_t> defects;
};

struct Choice {
    uint32_t coeff;
    std::array<uint32_t, 5> sigma{};
};

struct Record {
    uint32_t U, d, r, t, e, a, b, n;
    std::array<uint32_t, 5> sigma{};

    bool operator<(const Record& o) const {
        return std::tie(U, d, sigma, r, t, e, n, a, b) <
               std::tie(o.U, o.d, o.sigma, o.r, o.t, o.e, o.n, o.a, o.b);
    }
    bool operator==(const Record& o) const {
        return U == o.U && d == o.d && r == o.r && t == o.t && e == o.e &&
               a == o.a && b == o.b && n == o.n && sigma == o.sigma;
    }
};

static std::vector<PrimeExp> factorization(uint32_t x) {
    std::vector<PrimeExp> out;
    if (x == 0) return out;
    if ((x & 1u) == 0) {
        uint32_t a = 0;
        do {
            x >>= 1;
            ++a;
        } while ((x & 1u) == 0);
        out.push_back({2, a});
    }
    for (uint32_t p = 3; (uint64_t)p * p <= x; p += 2) {
        if (x % p == 0) {
            uint32_t a = 0;
            do {
                x /= p;
                ++a;
            } while (x % p == 0);
            out.push_back({p, a});
        }
    }
    if (x > 1) out.push_back({x, 1});
    return out;
}

static uint32_t valuation(uint32_t x, uint32_t p) {
    uint32_t a = 0;
    while (x % p == 0) {
        x /= p;
        ++a;
    }
    return a;
}

static std::vector<std::vector<PrimeExp>> factor_table(uint32_t limit) {
    std::vector<std::vector<PrimeExp>> table((size_t)limit + 1);
    for (uint32_t n = 1; n <= limit; ++n) table[n] = factorization(n);
    return table;
}

static std::vector<uint32_t> support_from_factorization(const std::vector<PrimeExp>& f) {
    std::vector<uint32_t> out;
    out.reserve(f.size());
    for (auto z : f) out.push_back(z.p);
    return out;
}

static void generate_smooth_rec(
    const std::vector<uint32_t>& primes,
    size_t i,
    uint64_t cur,
    uint32_t limit,
    std::vector<uint32_t>& out
) {
    if (i == primes.size()) {
        out.push_back((uint32_t)cur);
        return;
    }
    const uint32_t p = primes[i];
    while (cur <= limit) {
        generate_smooth_rec(primes, i + 1, cur, limit, out);
        if (cur > limit / p) break;
        cur *= p;
    }
}

static std::vector<uint32_t> generate_smooth(std::vector<uint32_t> primes, uint32_t limit) {
    std::sort(primes.begin(), primes.end());
    primes.erase(std::unique(primes.begin(), primes.end()), primes.end());
    std::vector<uint32_t> out;
    generate_smooth_rec(primes, 0, 1, limit, out);
    std::sort(out.begin(), out.end());
    out.erase(std::unique(out.begin(), out.end()), out.end());
    return out;
}

static uint32_t degree_upper(uint32_t D) {
    uint32_t lo = 0, hi = 200000;
    while (lo < hi) {
        uint32_t m = lo + (hi - lo + 1) / 2;
        if ((__int128)m * m * m < (__int128)64 * D * D) {
            lo = m;
        } else {
            hi = m - 1;
        }
    }
    return lo;
}

static std::vector<Core> cores_for_e(uint32_t e, uint32_t rmax, uint32_t dmax) {
    std::vector<Core> out;
    for (uint32_t r = 1; r <= rmax; ++r) {
        auto rf = factorization(r);
        for (uint32_t t = 1; t <= r; ++t) {
            uint64_t d64 = (uint64_t)t * e;
            if (d64 > dmax) break;
            Core c{r, t, (uint32_t)d64, {}};
            for (auto z : rf) {
                if (valuation(t, z.p) < z.a) c.defects.push_back(z.p);
            }
            out.push_back(std::move(c));
        }
    }
    return out;
}

static bool contains_prime(const std::vector<uint32_t>& primes, uint32_t p) {
    return std::find(primes.begin(), primes.end(), p) != primes.end();
}

static void choices_rec(
    const std::vector<PrimeExp>& endpoint_factor,
    const Core& c,
    uint32_t other,
    uint32_t e,
    size_t i,
    uint32_t coeff,
    std::array<uint32_t, 5> sigma,
    uint8_t len,
    std::vector<Choice>& out
) {
    if (i == endpoint_factor.size()) {
        if (coeff > 1) out.push_back({coeff, sigma});
        return;
    }

    const uint32_t p = endpoint_factor[i].p;
    const uint32_t kappa = endpoint_factor[i].a;
    const bool deficient = contains_prime(c.defects, p);

    if (!deficient && (e % p == 0 || e % p == (p + p - 2) % p)) {
        choices_rec(endpoint_factor, c, other, e, i + 1, coeff, sigma, len, out);
    }

    uint32_t p_power = 1;
    for (uint32_t A = 1; A <= kappa; ++A) {
        p_power *= p;
        if (((uint64_t)c.r * A) % c.t != 0) continue;
        const uint32_t lambda = (uint32_t)(((uint64_t)c.r * A) / c.t);
        if (lambda == 0 || lambda > kappa) continue;
        if (((uint64_t)other * lambda) % kappa != 0) continue;
        const uint32_t w = (uint32_t)(((uint64_t)other * lambda) / kappa);
        if (w < 1 || w > other || w > e) continue;
        if ((e + p - (w % p)) % p != 0 && (e + p - (w % p)) % p != (p + p - 2) % p) continue;
        if (deficient && (p > 7 || kappa < p || ((uint64_t)e * kappa) % ((uint64_t)p * other) != 0)) continue;
        if (len >= sigma.size()) throw std::runtime_error("too many coefficient primes");
        std::array<uint32_t, 5> next_sigma = sigma;
        next_sigma[len] = (uint32_t)((uint64_t)c.t * w);
        choices_rec(endpoint_factor, c, other, e, i + 1, coeff * p_power, next_sigma, (uint8_t)(len + 1), out);
    }
}

static std::vector<Choice> endpoint_choices(
    const std::vector<PrimeExp>& endpoint_factor,
    const Core& c,
    uint32_t other,
    uint32_t e
) {
    std::vector<Choice> out;
    std::array<uint32_t, 5> sigma{};
    choices_rec(endpoint_factor, c, other, e, 0, 1, sigma, 0, out);
    std::sort(out.begin(), out.end(), [](const Choice& x, const Choice& y) {
        return std::tie(x.coeff, x.sigma) < std::tie(y.coeff, y.sigma);
    });
    out.erase(std::unique(out.begin(), out.end(), [](const Choice& x, const Choice& y) {
        return x.coeff == y.coeff && x.sigma == y.sigma;
    }), out.end());
    return out;
}

int main(int argc, char** argv) {
    uint32_t e_start = 2, e_end = 0, Dcap = 16583, dmax = 0, rmax = 139;
    int threads = 25;
    std::string output;

    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        if (a == "--e-start" && i + 1 < argc) e_start = std::stoul(argv[++i]);
        else if (a == "--e-end" && i + 1 < argc) e_end = std::stoul(argv[++i]);
        else if (a == "--D-cap" && i + 1 < argc) Dcap = std::stoul(argv[++i]);
        else if (a == "--d-max" && i + 1 < argc) dmax = std::stoul(argv[++i]);
        else if (a == "--r-max" && i + 1 < argc) rmax = std::stoul(argv[++i]);
        else if (a == "--threads" && i + 1 < argc) threads = std::stoi(argv[++i]);
        else if (a == "--output" && i + 1 < argc) output = argv[++i];
        else throw std::runtime_error("bad command line");
    }

    if (Dcap < 6 || rmax < 1 || rmax > 139 || output.empty()) throw std::runtime_error("invalid domain");
    if (dmax == 0) dmax = degree_upper(Dcap);
    if (e_end == 0) e_end = dmax;
    if (e_start < 2 || e_start > e_end || e_end > dmax) throw std::runtime_error("invalid e range");

#ifdef _OPENMP
    omp_set_num_threads(threads);
    int nt = omp_get_max_threads();
#else
    (void)threads;
    int nt = 1;
#endif

    const auto factors = factor_table(std::max<uint32_t>(Dcap, e_end + 2));
    std::vector<std::vector<Record>> local((size_t)nt);
    std::vector<uint64_t> smooth_totals(nt), shape_tests(nt), core_tests(nt), coefficient_choices(nt), raw_states(nt);
    auto T = std::chrono::steady_clock::now();

#pragma omp parallel for schedule(dynamic, 1)
    for (int64_t ee = e_start; ee <= (int64_t)e_end; ++ee) {
        int tid = 0;
#ifdef _OPENMP
        tid = omp_get_thread_num();
#endif
        const uint32_t e = (uint32_t)ee;
        auto cores = cores_for_e(e, rmax, dmax);
        std::vector<Core> active;
        active.reserve(cores.size());
        uint32_t nmax = 0;
        for (auto& c : cores) {
            uint32_t lim = Dcap / c.r;
            if (lim >= e + 4) {
                nmax = std::max(nmax, lim);
                active.push_back(std::move(c));
            }
        }
        if (active.empty()) continue;

        auto primes = support_from_factorization(factors[e]);
        auto ep2 = support_from_factorization(factors[e + 2]);
        primes.insert(primes.end(), ep2.begin(), ep2.end());
        auto vals = generate_smooth(primes, nmax);
        smooth_totals[tid] += vals.size();

        for (uint32_t n : vals) {
            if (n < e + 4) continue;
            auto b_stop = std::lower_bound(vals.begin(), vals.end(), n);
            for (auto it = vals.begin(); it != b_stop; ++it) {
                uint32_t b = *it;
                uint32_t a = n - b;
                if (a < 2 || std::gcd(a, b) != 1) continue;
                ++shape_tests[tid];
                const auto& af = factors[a];
                for (const auto& c : active) {
                    if (n > Dcap / c.r) continue;
                    bool defect_ok = true;
                    for (uint32_t q : c.defects) {
                        if (b % q == 0 || n % q == 0) {
                            defect_ok = false;
                            break;
                        }
                        if (a % q == 0) continue;
                        if (e > q - 2) {
                            defect_ok = false;
                            break;
                        }
                    }
                    if (!defect_ok) continue;
                    ++core_tests[tid];
                    auto choices = endpoint_choices(af, c, b, e);
                    coefficient_choices[tid] += choices.size();
                    for (const auto& ch : choices) {
                        Record z;
                        z.U = ch.coeff;
                        z.d = c.d;
                        z.r = c.r;
                        z.t = c.t;
                        z.e = e;
                        z.a = a;
                        z.b = b;
                        z.n = n;
                        z.sigma = ch.sigma;
                        local[tid].push_back(z);
                        ++raw_states[tid];
                    }
                }
            }
        }
    }

    std::vector<Record> records;
    for (auto& v : local) records.insert(records.end(), v.begin(), v.end());
    std::sort(records.begin(), records.end());
    records.erase(std::unique(records.begin(), records.end()), records.end());

    std::ofstream out(output);
    out << "U,d,sigma1,sigma2,sigma3,sigma4,sigma5,r,t,e,a,b,n\n";
    for (const auto& z : records) {
        out << z.U << ',' << z.d;
        for (uint32_t s : z.sigma) out << ',' << s;
        out << ',' << z.r << ',' << z.t << ',' << z.e << ',' << z.a << ',' << z.b << ',' << z.n << '\n';
    }

    uint64_t A = 0, B = 0, C = 0, D = 0, E = 0;
    for (int i = 0; i < nt; ++i) {
        A += smooth_totals[i];
        B += shape_tests[i];
        C += core_tests[i];
        D += coefficient_choices[i];
        E += raw_states[i];
    }
    std::cout << "smooth_totals=" << A
              << " shape_tests=" << B
              << " core_tests=" << C
              << " coefficient_choices=" << D
              << " raw_states=" << E
              << " unique_states=" << records.size()
              << " seconds=" << std::chrono::duration<double>(std::chrono::steady_clock::now() - T).count()
              << "\n";
}
