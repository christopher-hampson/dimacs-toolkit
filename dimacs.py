#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================================
# Created By  : Christopher Hampson
# Created Date: 31-May-2021
# =============================================================================
import subprocess

class Formula:

	def __init__(self,*clauses):
		self.clauses = [C for C in clauses]
		self.solutions = []

	def add(self,C):
		self.clauses.append(C)

	def info(self):
		return "Number of Clauses: {0}\nNumber of Variables: {1}".format(len(self.clauses),len(self.get_props()))

	def get_props(self):
		return set.union(*[C.get_props() for C in self.clauses])

	def __repr__(self):
		return "\n\t".join([str(C) for C in self.clauses])

	def get_proposition_dict(self):
		order = sorted(self.get_props())
		self.prop_to_int = dict([(L,order.index(L)+1) for L in order]+[(-L,-1*(order.index(L)+1)) for L in order])
		self.int_to_prop = dict([(order.index(L)+1,L) for L in order]+[(-1*(order.index(L)+1),-L) for L in order])


	def to_dimacs(self):
		## returns a dimacs representation of the formula
		self.get_proposition_dict()
		header = "p cnf {0} {1}\n".format(len(self.prop_to_int.keys()),len(self.clauses))
		return header + "\n".join([C.to_dimacs(self.prop_to_int) for C in self.clauses])


	def solve(self,filename="test_sat.dimacs"):
		## write dimacs to file
		with open(filename,'w') as f:
			f.write(self.to_dimacs())

		## call MiniSat SAT-solver (from file)
		try:
			proc = subprocess.Popen(["./MiniSat {0} output".format(filename)],shell=True,stdout=subprocess.PIPE)
			proc.communicate()[0]
		except:
			raise Exception("Failed to solve DIMACS; MiniSat failed.")

		## call MiniSat SAT-solver (from stdin)
		# proc = subprocess.Popen(["./MiniSat"],shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
		# proc.stdin.write(dimacs)
		# print(proc.communicate()[0])
		# exit()

		## process output
		val = None
		with open('output','r') as f:
			line = f.read().split("\n")
			if line[0]=="SAT":
				val = [int(x) for x in line[1].split(" ") if int(x)!=0]
				val =  sorted([self.int_to_prop.get(x) for x in val])
		return val

	def all_solutions(self):
		## generator to yield all solutions
		F = Formula(*self.clauses)
		soln = True
		while soln is not None:
			soln = F.solve()
			if soln is not None:
				## yield solution
				yield soln

				## append negated solution
				F.add(Clause(*[-L for L in soln]))

	def count_solutions(self):
		## return number of solutions
		return len(list(self.all_solutions()))


	def is_satisfiable(self):
		## return True iff fomula has at least 1 solution
		return self.solve() != None



class Clause:

	def __init__(self,*literals):
		self.literals = [L for L in literals]

	def get_props(self):
		return set([abs(L) for L in self.literals])

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

	def __eq__(self,other):
		return self.label == other.label and self.parity==other.parity

	def __abs__(self):
		if self.parity<1:
			return -self
		else:
			return self

	def __repr__(self):
		if self.parity>0:
			return str(self.label)
		else:
			return "-" + str(self.label)

	def __neg__(self):
		return Prop(self.label,parity=-1*self.parity)

	def to_dimacs(self,prop_dict):
		## returns a dimacs representation of the literal
		return str(prop_dict.get(self))



if __name__=="__main__":

	F = Formula()

	p = Prop("p")
	q = Prop("q")
	F.add(Clause(-p,q))
	F.add(Clause(-q,p))

	print(F.to_dimacs())
	print(list(F.all_solutions()))

	print(F.count_solutions())


