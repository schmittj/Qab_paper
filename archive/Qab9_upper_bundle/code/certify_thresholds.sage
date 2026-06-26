# Sage/Arb certificates for the two analytic transition points in Qab9.
R = RealBallField(256)
P.<x> = PolynomialRing(ZZ)
theta = max(z for z, mult in (x^3 - x - 1).roots(ring=R))

def F(N):
    cube_root = (R(N).log() / 3).exp()
    return 8 * R(2*N).log() / cube_root

assert F(175394637) > theta.log()
assert F(175394638) < theta.log()
assert F(6816241) > R(2).log()
assert F(6816242) < R(2).log()
print("analytic_thresholds=PASS")
