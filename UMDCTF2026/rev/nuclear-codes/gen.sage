R.<x,y,z> = QQ[]

#cubic = x*(z+x)*(x+y) + y*(y+z)*(x+y) + z*(y+z)*(z+x) - 6*(y+z)*(z+x)*(x+y)
#cubic = x/(x-z) + (x-y)/(x+y-z) + (y-z)/(2*x-y)
cubic = x*(x+y-z)*(2*x-y) + (x-y)*(x-z)*(2*x-y) + (y-z)*(x-z)*(x+y-z) - 6*(x-z)*(x+y-z)*(2*x-y)

P = None
f = EllipticCurve_from_cubic(cubic, P, morphism=True)
E = f.codomain()
print(E)
finv = f.inverse()

def sol(point):
	p,q,r = finv(point)
	d = lcm([p.denominator(), q.denominator(), r.denominator()])
	p,q,r = p*d, q*d, r*d
	g = gcd([p,q,r])
	return (p/g, q/g, r/g)
gens = E.gens()
print(gens)
assert len(gens) == 1
tgens = E.torsion_subgroup().gens()
print(tgens)
assert len(tgens) == 1
tgen = tgens[0]
tgen_order = tgen.order()
P = gens[0]
cur = P
for p in range(1, 10000):
	solns = []
	for _ in range(tgen_order):
		s = sol(cur)
		#print(s)
		a,b,c = s
		if all(j>0 for j in s) and a-b>0 and b-c>0:
			solns.append(s)
		cur += tgen
	if solns:
		print(p, solns)
	cur += P