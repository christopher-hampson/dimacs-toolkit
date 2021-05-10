import subprocess

class Formula:

	def __init__(self,*clauses):
		self.clauses = [C for C in clauses]

	def add(self,C):
		self.clauses.append(C)

	def get_props(self):
		return set.union(*[C.get_props() for C in self.clauses])

	def __repr__(self):
		return "\n\t".join([str(C) for C in self.clauses])

	def get_proposition_dict(self):
		order = sorted(self.get_props())
		self.prop_to_int = dict([(L,order.index(L)+1) for L in order])
		self.int_to_prop = dict([(order.index(L)+1,L) for L in order])


	def to_dimacs(self):
		## returns a dimacs representation of the formula
		self.get_proposition_dict()
		header = "p cnf {0} {1}\n".format(len(self.prop_to_int.keys()),len(self.clauses))
		return header + "\n".join([C.to_dimacs(self.prop_to_int) for C in self.clauses])

	def is_satisfiable(self):
		try:
			is_sat, T, F = solve_dimacs(self.to_dimacs())
		except:
			raise Exception("Failed to Solve DIMACS")
		
		if is_sat:
			self.get_proposition_dict()
			return sorted([self.int_to_prop.get(L) for L in T])
		else:
			return False



class Clause:

	def __init__(self,*literals):
		self.literals = [L for L in literals]

	def get_props(self):
		return set([L.label for L in self.literals])

	def add(self,L):
		self.literals.append(L)

	def __repr__(self):
		return "({0})".format(" v ".join([str(L) for L in self.literals]))

	def to_dimacs(self,prop_dict):
		## returns a dimacs representation of the clause
		return "{0} 0".format(" ".join([L.to_dimacs(prop_dict) for L in self.literals]))


class Prop:
	def __init__(self,label,parity=1):
		self.label = label
		self.parity = parity

	def __hash__(self):
		return hash(self.label)

	def __repr__(self):
		if self.parity>0:
			return str(self.label)
		else:
			return "-" + str(self.label)

	def __neg__(self):
		return Prop(self.label,parity=-1*self.parity)

	def to_dimacs(self,prop_dict):
		## returns a dimacs representation of the literal
		if self.parity>0:
			return str(prop_dict.get(self.label))
		else:
			return "-" + str(prop_dict.get(self.label))


def solve_dimacs(dimacs,filename="test_sat.dimacs"):
	## write dimacs to file
	with open(filename,'w') as f:
		f.write(dimacs)
	# print("Dimacs successfully written to file.")

	# call MiniSat SAT-solver
	proc = subprocess.Popen(["./MiniSat {0} output".format(filename)],shell=True,stdout=subprocess.PIPE)
	print(proc.communicate()[0])

	## process output
	with open('output','r') as f:
		line = f.read().split("\n")
		if line[0]=="SAT":
			T_set, F_set = set(), set()
			for L in [int(x) for x in line[1].split(" ")]:
				if L>0:
					T_set.add(L)
				else:
					F_set.add(-1*L)

			return True, T_set, F_set
		else:
			return False, None, None

