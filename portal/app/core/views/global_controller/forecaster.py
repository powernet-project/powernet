"""Forecaster_v0.1
	v0.1 - July 2018
	Thomas Navidi

	This module contains the Forecaster object for the control algorithms

	Current version uses gaussian random noise as artificial forecaster
"""

import numpy as np

class Forecaster:
	def __init__(self, error, pMeans, pCovs):
		self.error = error
		self.pMeans = pMeans
		self.pCovs = pCovs

	def predict(self, data):
		mu, sigma = 0, self.error
		data_size = data.shape
		result = np.multiply(data, (1 + np.random.normal(mu, sigma, data_size)))
		return result

	def scenarioGen(self, pForecast, scens, battnodes):
		"""
		Inputs: battnodes - nodes with storage
			pForecast - real power forecast for only storage nodes
			pMeans/Covs - dictionaries of real power mean vector and covariance matrices
							keys are ''b'+node#' values are arrays
			scens - number of scenarios to generate
		Outputs: sScenarios - dictionary with keys scens and vals (nS X time)
		"""
		nS, T = pForecast.shape
		sScenarios = {}
		for j in range(scens):
			counter = 0
			tmpArray = np.zeros((nS,T))
			for i in battnodes:
				resi = np.random.multivariate_normal(self.pMeans['b'+str(i+1)],self.pCovs['b'+str(i+1)])
				tmpArray[counter,:] = pForecast[counter,:] + resi[0:T]
				counter += 1
			sScenarios[j] = tmpArray

		return sScenarios

	def netPredict(self, netDemandFull, t_idx, time):
		# just use random noise function predict
		pForecast = self.predict(netDemandFull[:,t_idx:(t_idx+time)])
		return pForecast

	def rPredict(self, rDemandFull, t_idx, time):
		# just use random noise function predict
		rForecast = self.predict(rDemandFull[:,t_idx:(t_idx+time)])
		return rForecast



