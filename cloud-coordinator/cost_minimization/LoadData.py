from CCAlgs_working1 import *
#from pypower.api import runpf
#import cvxpy as cvx
import time
import matplotlib.pyplot as plt

DSCdict = np.load('DSCdata.npy')
DSCdict = DSCdict[()]
Networkdict = np.load('NetworkData.npy')
Networkdict = Networkdict[()]
optVal = 329288

"""
print('Variable DSCdict is a dictionary with the keys:')
print('battnodes, Pd_array, Qd_array, Prices, qmax, Scenarios, Steps, umin, umax')
print('Dimensions of Pd_array and Qd_array are buses X time X scenarios \n')
print('Networkdict is a dictionary with the keys: \n Ybus, Yt, Yf \n')
print('optVal contains the optimal value of the DSC optimization but is not correct and not accurate due to numeric instability')
"""

pDemand = DSCdict['Pd_array']
qDemand = DSCdict['Qd_array']

deltaGC = 24
Ttotal = DSCdict['Steps']
Vmin = .95
Vmax = 1.05
sparseYbus = Networkdict['Ybus']
Ybus = sparseYbus.todense()
battnodes = DSCdict['battnodes']-1
battnodes = battnodes.flatten()
prices = DSCdict['Prices']

tnetwork = Network(Ybus, 0, battnodes,
			np.zeros(DSCdict['battnodes'].shape), DSCdict['qmax'],
	 		DSCdict['umin'], DSCdict['umax'], Vmin, Vmax)

q0 = tnetwork.qmax/2

pDemando = pDemand
qDemando = qDemand

scens = pDemando.shape[2]

pDemandfull = {}
qDemandfull = {}

scens = 3

for scen in range(scens):
	pDemandfull[scen] = np.matrix(pDemando[:,:,0])
	qDemandfull[scen] = np.matrix(qDemando[:,:,0])

pDemand = pDemandfull
qDemand = qDemandfull

horizon = 24

#pDemand[0] = pDemandfull[0][:,0:horizon]
#qDemand[0] = qDemandfull[0][:,0:horizon]

start = time.time()

Q, U, status, cost = GC_DSC(tnetwork, pDemand, qDemand, q0, prices)

end = time.time()
print("comp time: ", end - start)
print(status)
print('cost: ', cost)

Usmall = U[:,0:horizon]

ARB = prices[:,0:horizon]*np.sum(Usmall,0).T

print('ARB: ', ARB)

plt.figure(0)
plt.plot(Q.T)
#plt.figure(1)
#plt.plot(U.T)
plt.show()
