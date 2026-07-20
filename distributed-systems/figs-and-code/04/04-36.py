import matplotlib.pyplot as plt
import os

dataX = [i/20 for i in range(1,21)]

dataY = [0.00000758256,
				 0.0000167048,
				 0.000469865,
				 0.00251646,
				 0.00697715,
				 0.013941,
				 0.023097,
				 0.0340152,
				 0.0462771,
				 0.0595202,
				 0.0734467,
				 0.0878184,
				 0.102448,
				 0.117189,
				 0.131928,
				 0.146578,
				 0.161072,
				 0.175362,
				 0.18941,
				 0.203188]

plt.rcParams['figure.figsize'] = [3,2]
plt.rcParams.update({'font.sans-serif':'Arial'})
plt.rc('font', size=8)

plt.plot(dataX,dataY,'k-', linewidth=0.7)
plt.xlabel("Probability that a node stops spreading a rumor")
plt.ylabel("Number of oblivious nodes")

plt.tight_layout()

fname = os.path.basename(__file__)[:-3]+'.pdf'
plt.savefig(fname, format='pdf')
