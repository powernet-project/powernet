"""Local Controller Algorithms
	v0.1 - July 2018
	Thomas Navidi

	This module contains the algorithms for the local scheduling controller
"""

import numpy as np
from cvxpy import *

class Local_Controllers(object):
	"""
	main controller object
	"""

	def __init__(self, network, forecaster, GC_horizon, LCscens, NLweight, sellFactor, ramp_weight, nodesStorage, q0):

		self.network=network
		self.forecaster=forecaster
		self.LCscens=LCscens
		self.nodesStorage=nodesStorage
		self.GC_horizon=GC_horizon
		self.sellFactor=sellFactor
		self.ramp_weight=ramp_weight
		self.NLweight=NLweight

		self.q0=q0

		self.t_idx = 0
		
	def LC_Combined(self, LowBounds, UpBounds, realS, NLweight, prices, sellFactor, q0, LCscens, GCtime, pre_pDemands, umaxo, umino, qmaxo, qmino, battnodes, pMeans, pCovs):
		"""
		NLFC Local controller
		Inputs: realS - real net power from GC for only storage notes
		q0 - initial state of charge
		LCscens - number of local scenarios
		GCtime - time between GC steps
		pre_pDemands - previous time real power of storage nodes used for local forecasts
		umaxo, umino, qmaxo, qmino
		Outputs: Qfinal, Ufinal
		"""

		nS, T = LowBounds.shape
		Qfinal = np.matrix(np.zeros((nS,GCtime+1)))
		Ufinal = np.matrix(np.zeros((nS,GCtime)))
		boundsFlag = np.zeros((1,GCtime))
		Qfinal[:,0] = q0[:,0]

		for t in range(GCtime):
			# Resize parameters to match new time
			umin = np.tile(umino, (1,T-t))
			umax = np.tile(umaxo, (1,T-t))
			qmax = np.tile(qmaxo, (1,T-t+1))
			qmin = np.tile(qmino, (1,T-t+1))
			pricesCurrent = np.tile(prices[:,t:], (nS,LCscens))
			LowBoundsCurr = LowBounds[:,t:]
			UpBoundsCurr = UpBounds[:,t:]

			# generate local forecasts
			#LCforecast = forecaster then LCforecasts = scenario gen from forecast
			LCforecasts = self.forecaster.scenarioGen(pre_pDemands[:,t:], LCscens, battnodes)

			# initialize variables
			Y = Variable(nS,(T-t)*LCscens)
			U = Variable(nS,T-t)
			Q = Variable(nS,T-t+1)

			# Battery Constraints
			constraints = [Q[:,0] == q0,
						Q[:,1:T-t+1] == Q[:,0:T-t] + U,
						U <= umax,
						U >= umin,
						Q <= qmax,
						Q >= qmin
						]
			
			for i in range(LCscens):
				# Demand and battery action constraints
				constraints.append( Y[:,(i*(T-t)):((i+1)*(T-t))] == -LCforecasts[i] - U )

				# Bounds Constraints
				constraints.append( Y[:,(i*(T-t)):((i+1)*(T-t))] >= LowBoundsCurr )
				constraints.append( Y[:,(i*(T-t)):((i+1)*(T-t))] <= UpBoundsCurr )

			if sellFactor == 0:
				obj = Minimize( sum_entries(mul_elemwise(pricesCurrent, neg(Y))) + NLweight*norm(Y - np.tile(realS[:,t:], (1,LCscens)), 'fro') )
			else:
				obj = Minimize( sum_entries(mul_elemwise(pricesCurrent, -Y)) + NLweight*norm(Y - np.tile(realS[:,t:], (1,LCscens)), 'fro') )
			if sellFactor == 3:
				constraints.append( Y <= 0) # nodes cannot sell

			prob = Problem(obj, constraints)

			#data = prob.get_problem_data(MOSEK)
			#data = []

			prob.solve(solver = MOSEK)

			# Store values
			if prob.status != "optimal":
				print 'LC status is: ', prob.status
			Qfinal[:,t+1] = Q[:,1].value
			q0 = Q[:,1].value
			if np.any(np.less(q0, qmino)): # Correct for computational inaccuracies
				q0 += .00001
			elif np.any(np.greater(q0, qmaxo)):
				q0 += -.00001
			Ufinal[:,t] = U[:,0].value
			LowBoundsRep = np.tile(LowBoundsCurr, (1,LCscens))
			UpBoundsRep = np.tile(UpBoundsCurr, (1,LCscens))

			if np.any(np.greater(Y.value, UpBoundsRep-.0001)):
				print 'LC Upper Bound Reached'
				boundsFlag[:,t] = 1
			if np.any(np.less(Y.value, LowBoundsRep+.0001)):
				print 'LC Lower Bound Reached'
				boundsFlag[:,t] = 1

		return Qfinal, Ufinal, boundsFlag


	def LC_Combined_No_Bounds(self, realS, NLweight, prices, sellFactor, q0, LCscens, GCtime, pre_pDemands, umaxo, umino, qmaxo, qmino, battnodes, pMeans, pCovs):
		"""
		NLFC Local controller
		Inputs: realS - real net power from GC for only storage notes
		NLWeight - net load following weight in objective
		sellFactor - 1 for selling 0 for selling not profitable
		q0 - initial state of charge
		LCscens - number of local scenarios
		GCtime - time between GC steps
		pre_pDemands - previous time real power of storage nodes used for local forecasts or dictionary of scenarios
		umaxo, umino, qmaxo, qmino
		Outputs: Qfinal, Ufinal
		"""

		nS, T = realS.shape
		Qfinal = np.matrix(np.zeros((nS,GCtime+1)))
		Ufinal = np.matrix(np.zeros((nS,GCtime)))
		boundsFlag = np.zeros((1,GCtime))
		Qfinal[:,0] = q0[:,0]

		for t in range(GCtime):
			# Resize parameters to match new time
			umin = np.tile(umino, (1,T-t))
			umax = np.tile(umaxo, (1,T-t))
			qmax = np.tile(qmaxo, (1,T-t+1))
			qmin = np.tile(qmino, (1,T-t+1))
			pricesCurrent = np.tile(prices[:,t:], (nS,LCscens))

			# generate local forecasts
			#LCforecast = forecaster then LCforecasts = scenario gen from forecast
			if pre_pDemands is dict:
				LCforecasts = pre_pDemands
			else:
				LCforecasts = self.forecaster.scenarioGen(pre_pDemands[:,t:], LCscens, battnodes)

			# initialize variables
			Y = Variable(nS,(T-t)*LCscens)
			U = Variable(nS,T-t)
			Q = Variable(nS,T-t+1)

			# Battery Constraints
			constraints = [Q[:,0] == q0,
						Q[:,1:T-t+1] == Q[:,0:T-t] + U,
						U <= umax,
						U >= umin,
						Q <= qmax,
						Q >= qmin
						]
			
			for i in range(LCscens):
				# Demand and battery action constraints
				constraints.append( Y[:,(i*(T-t)):((i+1)*(T-t))] == -LCforecasts[i] - U )

			if sellFactor == 0:
				obj = Minimize( sum_entries(mul_elemwise(pricesCurrent, neg(Y))) + NLweight*norm(Y - np.tile(realS[:,t:], (1,LCscens)), 'fro') )
			else:
				obj = Minimize( sum_entries(mul_elemwise(pricesCurrent, -Y)) + NLweight*norm(Y - np.tile(realS[:,t:], (1,LCscens)), 'fro') )
			if sellFactor == 3:
				constraints.append( Y <= 0) # nodes cannot sell

			prob = Problem(obj, constraints)

			#data = prob.get_problem_data(MOSEK)
			#data = []

			prob.solve(solver = MOSEK)

			# Store values
			if prob.status != "optimal":
				print 'LC status is: ', prob.status
			Qfinal[:,t+1] = Q[:,1].value
			q0 = Q[:,1].value
			if np.any(np.less(q0, qmino)): # Correct for computational inaccuracies
				q0 += .00001
			elif np.any(np.greater(q0, qmaxo)):
				q0 += -.00001
			Ufinal[:,t] = U[:,0].value
			
		return Qfinal, Ufinal, boundsFlag

	def LC_Ramp(self, LowBounds, UpBounds, realS, NLweight, prices, sellFactor, q0, LCscens, GCtime, pre_pDemands, umaxo, umino, qmaxo, qmino, battnodes, ramp_weight, RstartListo, QiList, RsignList):
		"""
		NLFC Local controller with ramps
		Inputs: realS - real net power from GC for only storage notes
		q0 - initial state of charge
		LCscens - number of local scenarios
		GCtime - time between GC steps
		pre_pDemands - previous time real power of storage nodes used for local forecasts
		umaxo, umino, qmaxo, qmino
		Outputs: Qfinal, Ufinal
		"""

		nS, T = LowBounds.shape
		Qfinal = np.matrix(np.zeros((nS,GCtime+1)))
		Ufinal = np.matrix(np.zeros((nS,GCtime)))
		boundsFlag = np.zeros((1,GCtime))
		Qfinal[:,0] = q0[:,0]

		for t in range(GCtime):
			# Resize parameters to match new time
			umin = np.tile(umino, (1,T-t))
			umax = np.tile(umaxo, (1,T-t))
			qmax = np.tile(qmaxo, (1,T-t+1))
			qmin = np.tile(qmino, (1,T-t+1))
			pricesCurrent = np.tile(prices[:,t:], (nS,LCscens))
			LowBoundsCurr = LowBounds[:,t:]
			UpBoundsCurr = UpBounds[:,t:]
			RstartList = RstartListo - t

			# generate local forecasts
			#LCforecast = forecaster then LCforecasts = scenario gen from forecast
			LCforecasts = self.forecaster.scenarioGen(pre_pDemands[:,t:], LCscens, battnodes)

			# initialize variables
			Y = Variable(nS,(T-t)*LCscens)
			U = Variable(nS,T-t)
			Q = Variable(nS,T-t+1)

			# Battery Constraints
			constraints = [Q[:,0] == q0,
						Q[:,1:T-t+1] == Q[:,0:T-t] + U,
						U <= umax,
						U >= umin,
						Q <= qmax,
						Q >= qmin
						]
			
			for i in range(LCscens):
				# Demand and battery action constraints
				constraints.append( Y[:,(i*(T-t)):((i+1)*(T-t))] == -LCforecasts[i] - U )

				# Bounds Constraints
				constraints.append( Y[:,(i*(T-t)):((i+1)*(T-t))] >= LowBoundsCurr )
				constraints.append( Y[:,(i*(T-t)):((i+1)*(T-t))] <= UpBoundsCurr )

			if sellFactor == 0:
				obj = Minimize( sum_entries(mul_elemwise(pricesCurrent, neg(Y))) + NLweight*norm(Y - np.tile(realS[:,t:], (1,LCscens)), 'fro')
					+ ramp_weight*norm(max_elemwise(0, mul_elemwise(RsignList,(Q[:,RstartList] - QiList))), 'fro') )
			else:
				obj = Minimize( sum_entries(mul_elemwise(pricesCurrent, -Y)) + NLweight*norm(Y - np.tile(realS[:,t:], (1,LCscens)), 'fro')
					+ ramp_weight*norm(max_elemwise(0, mul_elemwise(RsignList,(Q[:,RstartList] - QiList))), 'fro') )
			if sellFactor == 3:
				constraints.append( Y <= 0) # nodes cannot sell

			prob = Problem(obj, constraints)

			#data = prob.get_problem_data(MOSEK)
			#data = []

			prob.solve(solver = MOSEK)

			# Store values
			if prob.status != "optimal":
				print 'LC status is: ', prob.status
			Qfinal[:,t+1] = Q[:,1].value
			q0 = Q[:,1].value
			if np.any(np.less(q0, qmino)): # Correct for computational inaccuracies
				q0 += .00001
			elif np.any(np.greater(q0, qmaxo)):
				q0 += -.00001
			Ufinal[:,t] = U[:,0].value
			LowBoundsRep = np.tile(LowBoundsCurr, (1,LCscens))
			UpBoundsRep = np.tile(UpBoundsCurr, (1,LCscens))

			if np.any(np.greater(Y.value, UpBoundsRep-.0001)):
				print 'LC Upper Bound Reached'
				boundsFlag[:,t] = 1
			if np.any(np.less(Y.value, LowBoundsRep+.0001)):
				print 'LC Lower Bound Reached'
				boundsFlag[:,t] = 1

		return Qfinal, Ufinal, boundsFlag

	def LC_Ramp_No_Bounds(self, realS, NLweight, prices, sellFactor, q0, LCscens, GCtime, pre_pDemands, umaxo, umino, qmaxo, qmino, battnodes, ramp_weight, RstartListo, QiList, RsignList):
		"""
		NLFC Local controller with ramps
		Inputs: realS - real net power from GC for only storage notes
		q0 - initial state of charge
		LCscens - number of local scenarios
		GCtime - time between GC steps
		pre_pDemands - previous time real power of storage nodes used for local forecasts
		umaxo, umino, qmaxo, qmino
		Outputs: Qfinal, Ufinal
		"""

		nS, T = realS.shape
		Qfinal = np.matrix(np.zeros((nS,GCtime+1)))
		Ufinal = np.matrix(np.zeros((nS,GCtime)))
		Qfinal[:,0] = q0[:,0]

		for t in range(GCtime):
			# Resize parameters to match new time
			umin = np.tile(umino, (1,T-t))
			umax = np.tile(umaxo, (1,T-t))
			qmax = np.tile(qmaxo, (1,T-t+1))
			qmin = np.tile(qmino, (1,T-t+1))
			pricesCurrent = np.tile(prices[:,t:], (nS,LCscens))
			RstartList = RstartListo - t

			# generate local forecasts
			#LCforecast = forecaster then LCforecasts = scenario gen from forecast
			LCforecasts = self.forecaster.scenarioGen(pre_pDemands[:,t:], LCscens, battnodes)

			# initialize variables
			Y = Variable(nS,(T-t)*LCscens)
			U = Variable(nS,T-t)
			Q = Variable(nS,T-t+1)

			# Battery Constraints
			constraints = [Q[:,0] == q0,
						Q[:,1:T-t+1] == Q[:,0:T-t] + U,
						U <= umax,
						U >= umin,
						Q <= qmax,
						Q >= qmin
						]
			
			for i in range(LCscens):
				# Demand and battery action constraints
				constraints.append( Y[:,(i*(T-t)):((i+1)*(T-t))] == -LCforecasts[i] - U )

			if sellFactor == 0:
				obj = Minimize( sum_entries(mul_elemwise(pricesCurrent, neg(Y))) + NLweight*norm(Y - np.tile(realS[:,t:], (1,LCscens)), 'fro')
					+ ramp_weight*norm(max_elemwise(0, mul_elemwise(RsignList,(Q[:,RstartList] - QiList))), 'fro') )
			else:
				obj = Minimize( sum_entries(mul_elemwise(pricesCurrent, -Y)) + NLweight*norm(Y - np.tile(realS[:,t:], (1,LCscens)), 'fro')
					+ ramp_weight*norm(max_elemwise(0, mul_elemwise(RsignList,(Q[:,RstartList] - QiList))), 'fro') )
			if sellFactor == 3:
				constraints.append( Y <= 0) # nodes cannot sell

			prob = Problem(obj, constraints)

			#data = prob.get_problem_data(MOSEK)
			#data = []

			prob.solve(solver = MOSEK)

			# Store values
			if prob.status != "optimal":
				print 'LC status is: ', prob.status
			Qfinal[:,t+1] = Q[:,1].value
			q0 = Q[:,1].value
			if np.any(np.less(q0, qmino)): # Correct for computational inaccuracies
				q0 += .00001
			elif np.any(np.greater(q0, qmaxo)):
				q0 += -.00001
			Ufinal[:,t] = U[:,0].value

		return Qfinal, Ufinal

	def runPeriod(self, t_idx, realS, pricesCurrent, LCtime, rampFlag=0, RstartList=[], QiList=[], RsignList=[]):

		#get variables for readability
		nodesStorage=self.nodesStorage
		GC_horizon = self.GC_horizon
		ramp_weight=self.ramp_weight
		qmax = self.network.qmax
		qmin = self.network.qmin
		umax = self.network.umax
		umin = self.network.umin
			
		# Get data from network
		# should be historical data when using real forecaster, but this is current data
		preDemand, rDemand, pricesCurrent = self.network.returnData(t_idx, GC_horizon, nodesStorage)

		if rampFlag == 1: # if there is a ramp run ramp LC
			#Q, U, boundsFlag = self.LC_Ramp(LowBounds, UpBounds, realS, NLweight, pricesCurrent, sellFactor, q0, LCscens, LCtime, preDemand, 
			#	umax, umin, qmax, qmin, nodesStorage, ramp_weight, RstartList, QiList, RsignList)

			Q, U = self.LC_Ramp_No_Bounds(realS, self.NLweight, pricesCurrent, self.sellFactor, self.q0, self.LCscens, LCtime, preDemand, 
				umax, umin, qmax, qmin, nodesStorage, ramp_weight, RstartList, QiList, RsignList)
		else: # if there is not a ramp run regular LC
			#Q, U, boundsFlag = self.LC_Combined(LowBounds, UpBounds, realS, NLweight, pricesCurrent, sellFactor, q0, LCscens, LCtime, preDemand, 
			#	umax, umin, qmax, qmin, nodesStorage, self.forecaster.pMeans, self.forecaster.pCovs)

			Q, U, boundsFlag = self.LC_Combined_No_Bounds(realS, self.NLweight, pricesCurrent, self.sellFactor, self.q0, self.LCscens, LCtime, preDemand, 
				umax, umin, qmax, qmin, nodesStorage, self.forecaster.pMeans, self.forecaster.pCovs)

		self.t_idx = t_idx + LCtime

		return U, Q[:,1:], self.t_idx



