import matplotlib.pyplot as plt
import os

f = open("nan.txt", "r")

dataY = []

numbers = f.readlines()

for n in numbers:
	dataY.append(int(n))

dataX = [i for i in range(len(dataY))]

f.close()

plt.rcParams['figure.figsize'] = [3.5,1.75]
plt.rcParams.update({'font.sans-serif':'Arial'})
plt.rc('font', size=8)

plt.plot(dataX, dataY, linewidth=0.5, color='black')
plt.xlabel("Number of rounds")
plt.ylabel("Number of affected nodes")

plt.tight_layout()
figname = os.path.basename(__file__)[:-3]
plt.savefig(figname + '.pdf',format='pdf')
plt.show()
