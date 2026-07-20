import random
import math
import sys
import os

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

inDegree = [] # list of indegree distributions

def inDegreeHistogram(ax, inDegree):
	counts = np.array(inDegree)
	ax.hist(counts, bins=[i for i in range(100)], density = True, rwidth = 0.75, color = 'gray')
	
degfile = open("degree.txt", "r")

arguments = degfile.readline()
argSet    = arguments.split(" ")
assert(len(argSet) == 5)

m = int(argSet[0]) # size of partial views
s = int(argSet[1]) # number of entries to exchange
n = int(argSet[2]) # total number of nodes
c = int(argSet[3]) # total number of colluders
r = int(argSet[4].rstrip()) # number of rounds between first 4 indegree datasets

print(m,s,n,c,r)

degfile.readline() # empty line

degrees = [0 for i in range(n)]
line    = degfile.readline()
p       = 0
sample  = 1
while len(line) > 0:
	if line[0] == '#': # Just started a new series of indegrees
		if p > 0:
			inDegree.append(degrees)
			degrees = [0 for i in range(n)]			
		p = 0
	else:
		degrees[p] = int(line.rstrip())
		p = p + 1
	line = degfile.readline()

inDegree.append(degrees)

figext = ['a','b','c','d','e','f']
for t in range(len(inDegree)):
	plt.rc('font', size=8)
	matplotlib.rcParams['font.family'] = 'Arial'
	fig, axis = plt.subplots(tight_layout = True,figsize=(2.25,1.75))
	if t == 0:
		legend = 'The initial situation'
	elif t == 5:
		legend = 'After 280 rounds'
	else:
		legend = 'After ' + str(t*10) + ' rounds'
	axis.set_title(legend, fontsize=8)
	inDegreeHistogram(axis, inDegree[t])
	fname = "dist-" + str(m) + "-" + str(s) + "-" + str(n) + "-" + str(c) + "-" + str(r) + "-" + str(t) + ".pdf"
	figname = os.path.basename(__file__)[:-3]
	plt.savefig(fname,format='pdf')
	plt.savefig(figname + figext[t] + '.pdf',format='pdf')

