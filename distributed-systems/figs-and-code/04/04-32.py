import matplotlib.pyplot as plt
import numpy as np
import os

x = [int(i) for i in range(5000)]

def f(p,x):
	return float(p)/2 * float(x) * (float(x)-1)

y1 = [f(0.2,n) for n in range(5000)]
y2 = [f(0.4,n) for n in range(5000)]
y3 = [f(0.6,n) for n in range(5000)]

plt.rcParams['figure.figsize'] = [4.5,2]
plt.rcParams.update({'font.sans-serif':'Arial'})
plt.rc('font', size=8)

plt.plot(x,y1,'k-.',linewidth=0.7, label="$p_{edge}$ = 0.2")
plt.plot(x,y2,'k-', linewidth=0.7, label="$p_{edge}$ = 0.4")
plt.plot(x,y3,'k:', linewidth=0.7, label="$p_{edge}$ = 0.6")
plt.legend(loc='upper left',ncol=1)
plt.xlabel("Number of nodes")
plt.ylabel("Number of edges")
plt.yticks([0,1000000,2000000,3000000,4000000,5000000,6000000,7000000],['0','1M','2M','3M','4M','5M','6M','7M'])

plt.tight_layout()
fname = os.path.basename(__file__)[:-3]+'.pdf'
plt.savefig(fname,format='pdf')
#plt.show()
