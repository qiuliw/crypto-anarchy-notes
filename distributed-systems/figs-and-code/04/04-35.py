import matplotlib.pyplot as plt
import os

N=10000
R=25

pulldata=[]
pushdata=[]
pushpull=[]

def pull(i):
	if i > 1:
		p = pull(i-1)
		return p * p
	else:
		return 1.0 - 1.0/(N-1)

def push(i):
	if i > 1:
		p = push(i-1)
		return p * pow(1.0 - 1.0/(N-1),N * (1-p))
	else:
		return 1.0 - 1.0/(N-1)

for i in range(R):
	pulldata.append(pull(i+1))

for i in range(1,R+1):
	pushdata.append(push(i+1))

for i in range(0,R):
	pushpull.append(pushdata[i]*pulldata[i])

x = [i+1 for i in range(R)]

plt.rcParams['figure.figsize'] = [5,2]
plt.rcParams.update({'font.sans-serif':'Arial'})
plt.rc('font', size=8)

plt.figure(1)
SI=0
plt.plot(x[SI:],[int(N*pulldata[i]) for i in range(SI,R)],'k-.',linewidth=0.7, label="pull")
plt.plot(x[SI:],[int(N*pushdata[i]) for i in range(SI,R)],'k-', linewidth=0.7, label="push")
plt.plot(x[SI:],[int(N*pushpull[i]) for i in range(SI,R)],'k:', linewidth=1.0, label="pushpull")
plt.legend(loc='lower left',ncol=1)
plt.xlabel("Number of rounds")
plt.ylabel("# of oblivious nodes")
plt.tight_layout()
fname = os.path.basename(__file__)[:-3]+'a.pdf'
plt.savefig(fname, format='pdf')

plt.figure(2)
SI=10
plt.yscale('log')
plt.yticks([0,10,100,1000,10000],['0','10','100','1000','10000'])
plt.plot(x[SI:],[int(N*pulldata[i]) for i in range(SI,R)],'k-.',linewidth=0.7, label="pull")
plt.plot(x[SI:],[int(N*pushdata[i]) for i in range(SI,R)],'k-', linewidth=0.7, label="push")
plt.plot(x[SI:],[int(N*pushpull[i]) for i in range(SI,R)],'k:', linewidth=1.0, label="pushpull")
plt.legend(loc='lower left',ncol=1)
plt.xlabel("Number of rounds (detailed)\n")
plt.ylabel("# of oblivious nodes")
plt.tight_layout()
fname = os.path.basename(__file__)[:-3]+'b.pdf'
plt.savefig(fname, format='pdf')
