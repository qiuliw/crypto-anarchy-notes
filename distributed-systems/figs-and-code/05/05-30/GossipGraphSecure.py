import random
import math
import sys

import matplotlib.pyplot as plt
import numpy as np

m = int(sys.argv[1]) # size of partial views
s = int(sys.argv[2]) # number of entries to exchange
n = int(sys.argv[3]) # total number of nodes
c = int(sys.argv[4]) # total number of colluders
r = int(sys.argv[5]) # number of rounds between first 4 indegree datasets

Ncols = 3
Nrows = 2

assert(n > c)

viewPSS	 = [] # list of all partial views
inDegree = [] # list of indegree distributions
checked	 = [False for k in range(n)]

def initViews():
	for i in range(n):
		viewPSS.append(random.sample(range(n),m))

def exchangeEntries(i,j,k):
	colluders = [t for t in range(c)]
	if (i < c):
		select_i = random.sample(colluders, k)
	else:
		select_i = random.sample(viewPSS[i],k)

	if (j < c):
		select_j = random.sample(colluders, k)
	else:
		select_j = random.sample(viewPSS[j],k)

	viewPSS[i] = list(set(viewPSS[i]).union(set(select_j)))
	viewPSS[j] = list(set(viewPSS[j]).union(set(select_i)))
	viewPSS[i].append(j)
	viewPSS[j].append(i)
	viewPSS[i] = list(set(viewPSS[i]))
	viewPSS[j] = list(set(viewPSS[j]))
		
	# For Cyclon, make sure that you keep the entries received from the other
	selectFrom = list(set(viewPSS[i]).difference(set(select_j)))
	keepInView = random.sample(selectFrom, min(len(selectFrom),m-k))
	viewPSS[i] = list(set(keepInView).union(set(select_j)))
	selectFrom = list(set(viewPSS[j]).difference(set(select_i)))
	keepInView = random.sample(selectFrom, min(len(selectFrom),m-k))
	viewPSS[j] = list(set(keepInView).union(set(select_i)))
						
def doPSSRound():
	order = random.sample(range(n),n)
	assert(len(order) == n)
	for i in order:
		j = viewPSS[i][random.randint(0,len(viewPSS[i])-1)]
		exchangeEntries(i,j,s)
	
def computeInDegrees(f):
	degrees = [0 for i in range(n)]
	for i in range(n):
		for k in range(len(viewPSS[i])):
			p = viewPSS[i][k]
			degrees[p] = degrees[p] + 1
	f.write('#*****************************************\n')
	for d in range(len(degrees)):
		f.write(str(degrees[d])+'\n')
	return degrees

def numOfAffectedNodes():
	colluders = [t for t in range(c)]
	nAffected = 0
	for i in range(c,n):
		if all(t in colluders for t in viewPSS[i]):
			nAffected = nAffected + 1
	return nAffected
			
def inDegreeHistogram(ax, inDegree):
	counts = np.array(inDegree)
	ax.hist(counts, bins=[i for i in range(100)], density = True, rwidth = 0.75, color = 'gray')
	
initViews()
nanfile = open("nan.txt","w")
degfile = open("degree.txt", "w")
degfile.write(str(m) + " " + str(s) + " " + str(n) + " " + str(c) + " " + str(r) + '\n\n')

inDegree.append(computeInDegrees(degfile))
nr = 0
for i in range(4):
	for j in range(r):
		doPSSRound()
		nr = nr + 1
		nan = numOfAffectedNodes()		
		print("##### Number of affected nodes:", numOfAffectedNodes() , "[", nr, "]")
		nanfile.write(str(nan) + "\n")
	inDegree.append(computeInDegrees(degfile))

while True:
	doPSSRound()
	nr = nr + 1
	nan = numOfAffectedNodes()
	print("##### Number of affected nodes:", numOfAffectedNodes(), "[", nr, "]")
	nanfile.write(str(nan) + "\n")
	if nan > int(0.98 * (n - c)): break

print("Number of rounds:", nr)
inDegree.append(computeInDegrees(degfile))
nanfile.close()
degfile.close()

fig, axis = plt.subplots(nrows = Nrows, ncols = Ncols, tight_layout = True, figsize = (3*Ncols, 3*Nrows))

t = 0
for i in range(Nrows):
	for j in range(Ncols):
		inDegreeHistogram(axis[i][j], inDegree[t])
		t = t+1

for i in range(Nrows):
	for j in range(Ncols):
		axis[i][j].xaxis.set_ticks([])
		axis[i][j].yaxis.set_ticks([])
		
fname = "distributions-" + str(m) + "-" + str(s) + "-" + str(n) + "-" + str(c) + "-" + str(r) + ".pdf"
plt.savefig(fname,format='pdf')
plt.show()

