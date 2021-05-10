import networkx as nx
import itertools
from dimacs import Formula, Clause, Prop


def labEUL_to_SAT(G,cycle_length=8):
	## cycle length
	labels = set()

	F = EUL_to_SAT(G,cycle_length=cycle_length)
		
	## list labels used
	for (u,v,data) in G.edges(data=True):
		for i in range(cycle_length):
			p = Prop("edge_used({0:02d}:{1},{2})".format(i,u,v))
			q = Prop("label_used({0:02d}:{1})".format(i,data.get('label','')))
			F.add(Clause(-p,q))
			labels.add(data.get('label',''))

	## don't use same label twice
	for lab in labels:
		for i,j in itertools.combinations(range(cycle_length),2):
			p = Prop("label_used({0:02d}:{1})".format(i,lab))
			q = Prop("label_used({0:02d}:{1})".format(j,lab))
			F.add(Clause(-p,-q))


	return F

def EUL_to_SAT(G,cycle_length=None):
	## cycle length
	if cycle_length==None:
		cycle_length = len(G.edges())

	F = Formula()

	## Initial vertex
	initial_vertex,d = max(G.nodes(data=True),key=lambda (n, d): d.get('initial',False) == True)
	p = Prop("position({0:02d},{1})".format(0,initial_vertex))
	F.add(Clause(p))

	## ith edge must be adjacent to vertex in position i
	for u in G.nodes():
		for i in range(cycle_length):
			p = Prop("position({0:02d},{1})".format(i,u))
			C = Clause(-p)
			for v in G.successors(u):
				q = Prop("edge_used({0:02d}:{1},{2})".format(i,u,v))
				C.add(q)
			F.add(C)

	## don't use edges that don't exist (might be redundant)
	for (u,v) in itertools.permutations(G.nodes(),2):
		if (u,v) not in G.edges():
			for i in range(cycle_length):
				p = Prop("edge_used({0:02d}:{1},{2})".format(i,u,v))
				F.add(Clause(-p))


	## path coherence (if edge (u,v) is ith edge then u is ith vertex and v is (i+1)th vertex)
	for (u,v) in G.edges():
		for i in range(cycle_length):
			j = (i+1)%cycle_length
			p = Prop("position({0:02d},{1})".format(i,u))
			q = Prop("position({0:02d},{1})".format(j,v))
			r = Prop("edge_used({0:02d}:{1},{2})".format(i,u,v))
			F.add(Clause(-r,p))
			F.add(Clause(-r,q))

	## two vertices can't be in same position i
	for u,v in itertools.permutations(G.nodes(),2):
		for i in range(cycle_length):
			p = Prop("position({0:02d},{1})".format(i,u))
			q = Prop("position({0:02d},{1})".format(i,v))
			F.add(Clause(-p,-q))

	## don't use same edge twice
	for u,v in G.edges():
		for i,j in itertools.combinations(range(cycle_length),2):
			p = Prop("edge_used({0:02d}:{1},{2})".format(i,u,v))
			q = Prop("edge_used({0:02d}:{1},{2})".format(j,u,v))
			F.add(Clause(-p,-q))

	return F


def HAM_to_SAT(G):
	## cycle length
	cycle_length = len(G.nodes())
	must_visit = G.nodes()

	F = Formula()
	## For each vertex, at most one successor edge is traversed
	for u in G.nodes():
		for (v1,v2) in itertools.combinations(G.successors(u),2):
			p = Prop("edge_used({0},{1})".format(u,v1))
			q = Prop("edge_used({0},{1})".format(u,v2))
			F.add(Clause(-p,-q))

	## For each vertex, at most one predecessor edge is traversed
	for v in G.nodes():
		for (u1,u2) in itertools.combinations(G.predecessors(v),2):
			p = Prop("edge_used({0},{1})".format(u1,v))
			q = Prop("edge_used({0},{1})".format(u2,v))
			F.add(Clause(-p,-q))


	## at least one successor edge is traversed
	for u in must_visit:
		C = Clause()
		for v in G.successors(u):
			p = Prop("edge_used({0},{1})".format(u,v))
			C.add(p)
		F.add(C)

	## at least one predecessor edge is traversed
	for v in must_visit:
		C = Clause()
		for u in G.predecessors(v):
			p = Prop("edge_used({0},{1})".format(u,v))
			C.add(p)
		F.add(C)

	## coherence between position and edges used
	for (i,j) in zip(range(cycle_length), list(range(1,cycle_length))+[0]):
		for (u,v) in itertools.permutations(G.nodes(),2):
			p = Prop("position({0},{1})".format(i,u))
			q = Prop("position({0},{1})".format(j,v))
			r = Prop("edge_used({0},{1})".format(u,v))
			F.add(Clause(-p,-q,r))
			F.add(Clause(-p,q,-r))

	
	## ensure each visited vertex is on the cycle
	for v in must_visit:
		C = Clause()
		for i in range(cycle_length):
			p = Prop("position({0},{1})".format(i,v))
			C.add(p)
		F.add(C)

	## ensure no overlap of positions
	for u,v in itertools.combinations(must_visit,2):
		for i in range(cycle_length):
			p = Prop("position({0},{1})".format(i,u))
			q = Prop("position({0},{1})".format(i,v))
			F.add(Clause(-p,-q))


	return F


if __name__=="__main__":
	G = nx.DiGraph()

	G.add_nodes_from([1,2,3,4,5])
	G.add_edges_from([(1,2),(2,3),(3,4),(4,5),(5,1),(2,4),(1,4),(2,5)])
	G.add_edges_from([(2,1),(3,2),(4,3),(5,4),(1,5),(4,2),(4,1),(5,2)])

	G = nx.dodecahedral_graph(create_using=None).to_directed()

	print(nx.info(G))

	F = labEUL_to_SAT(G)

	print(F)


	# for x in F.is_satisfiable():
	# 	print(x)
