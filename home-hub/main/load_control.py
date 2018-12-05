"""
Heuristic control of storage and loads
"""
from __future__ import print_function

__author__ = 'Thomas N., Gustavo C. & Jonathan G.'
__copyright__ = 'Stanford University'
__version__ = '0.2'
__email__ = 'tnavidi@stanford.edu, gcezar@stanford.edu, jongon@stanford.edu'
__status__ = 'Beta'

# Heuristic control of storage and loads

import numpy as np 

import matplotlib.pyplot as plt

class Controller(object):
	# takes load objects and schedules them
	def __init__(self, s_loads=None, d_loads=None, batteries=None):
		# dictionaries of device objects
		self.s_loads = s_loads
		self.d_loads = d_loads
		self.batteries = batteries
		#self.device_id = 0
		#self.device_names = []

	def addDevice(self, device):
		# not needed
		self.devices[self.device_id] = device
		self.device_id += 1
		self.device_names.append(device.name)

	def calcSchedule(self, agg, t_step):
		# agg is sum of signal + baseline
		# first schdule negative side of batteries
		
		#plt.figure()
		#plt.plot(agg)

		#extract variable names from self
		s_loads = self.s_loads
		d_loads = self.d_loads
		batteries = self.batteries
		
		period = agg.size
		base = np.zeros(period)
		# make aggregate baseline signal
		if s_loads is not None:
			for key in s_loads.keys():
				base += s_loads[key].base
		if d_loads is not None:
			for key in d_loads.keys():
				base += d_loads[key].base

		if batteries is not None:
			SOC0 = 0
			umax = 0
			umin = 0
			qmax = 0
			b_count = 0
			q_req = np.zeros(period)
			# combine batteries into one battery
			for key in batteries.keys():
				batt = batteries[key]
				SOC0 += batt.SOC0
				umax += batt.umax
				umin += batt.umin
				qmax += batt.capacity
				b_count += 1
				if batt.q_req is not None:
					q_req += batt.q_req
				if batt.base is not None:
					base += batt.base

			SOC0 = SOC0/b_count # take average SOC instead of sum since SOC is percentage of capacity

		self.base = np.copy(base)
		#print base
		agg = agg + base # make new signal to track include baseline
		self.agg = np.copy(agg)
		#print np.max(agg)
		#print agg

		#plt.figure()
		#plt.plot(agg)

		#print 'combined qmax umax', qmax, umax

		# schedule batteries for negative portion of agg
		if batteries is not None:
			b_schedule = np.zeros(period)
			b_schedule[agg < 0] = agg[agg < 0]

			Q = np.cumsum(b_schedule)*t_step + SOC0*qmax
			#print Q
			if np.any(Q<0):
				b_where = np.where(Q < 0)[0] # times when batteries need to have some extra charge
				b_where = np.split(b_where, np.where(np.diff(b_where) != 1)[0]+1)
				b_start = b_where[0][0]
				b_end = b_where[0][-1]
				b_charge = np.max(-Q[b_where[0]]) # amount of charge needed to ensure batteries are not negative
				# print 'required charge to be done by battery', b_charge
			else:
				b_charge = 0
		else:
			b_charge = -1e3 # schedules better when it does not delay scheduling when there are no batteries


		if s_loads is not None:
			s_list = []
			sp_list = []
			# order scheduled loads so that largest is first
			for key in s_loads.keys():
				#print key
				device = s_loads[key]
				s_list.append(device)
				sp_list.append(np.max(device.shapes))
			sp_list = np.array(sp_list)
			ordering = np.argsort(sp_list)[::-1]
			#print ordering
			#print sp_list[ordering]

			for idx in ordering:
				#print idx
				device = s_list[idx]
				shape, duration = device.getSchedulingInfo()
				p_fit = -1e8 # initialize as very bad value
				skippedFlag = 0
				for i in range(device.last_time):
					if i+duration >= period: # if load continues past horizon then skip
						skippedFlag = 1
						break
					p_fit_n = np.sum(agg[i:i+duration] - shape)
					if p_fit_n > p_fit:
						p_fit = p_fit_n
						s_time = i
						#print p_fit

				# if there is extra time past horizon and the fit is bad then schedule later
				if skippedFlag and p_fit < b_charge:
					# print 'Scheduling device later', key
					device.makeSchedule(period, 0, op_mode=0) # add empty schedule
				else:
					device.makeSchedule(period, s_time) # add start time to device schedule
					agg[s_time:s_time+duration] += -shape # remove device shape from profile

		if d_loads is not None:
			for key in d_loads.keys():
				device = d_loads[key]
				d_SOC = device.SOC0
				c_where = np.where(agg < 0)[0] # times when batteries can charge
				c_where = np.split(c_where, np.where(np.diff(c_where) != 1)[0]+1)
				c_start = c_where[0][0]
				c_end = c_where[0][-1]
				c_avail = np.sum(agg[c_where[0]])
				schedule = np.zeros(period)
				for i in range(period):
					SOC_up, SOC_down = device.nextCapacity(d_SOC)
					#print SOC_up, SOC_down
					if SOC_up > 1:
						schedule[i] = 0
						d_SOC = SOC_down
					elif SOC_down < 0:
						schedule[i] = 1
						d_SOC = SOC_up
						agg[i] += -device.on_power
						if i in c_where[0]:
							c_avail += -device.on_power
					elif agg[i] - device.on_power > 0:
						# greedy in time should search next few steps and pick largest not just > 0
						if i in c_where[0] and c_avail - agg[i] > b_charge:
							schedule[i] = 1
							d_SOC = SOC_up
							c_avail += -device.on_power
							agg[i] += -device.on_power
						elif i in c_where[0]:
							schedule[i] = 0
							d_SOC = SOC_down
						else:
							schedule[i] = 1
							d_SOC = SOC_up
							agg[i] += -device.on_power
					else:
						schedule[i] = device.base[i]/device.on_power
						if schedule[i] > 0:
							d_SOC = SOC_up
							if i in c_where[0]:
								c_avail += -device.on_power
						else:
							d_SOC = SOC_down

				device.makeSchedule(schedule)

		if batteries is not None:
			b_schedule = agg # batteries take remaining signal
			EV_cap = 0
			EV_SOC0 = 1
			s_cap = qmax
			s_SOC0 = SOC0
			s_umin = umin
			for key in batteries.keys():
				if 'EV' in key:
					device = batteries[key]
					EV_cap = device.capacity
					EV_SOC0 = device.SOC0
				else:
					device_s = batteries[key]
					s_cap = device_s.capacity
					s_SOC0 = device_s.SOC0
					s_umin = device_s.umin
			b1_schedule = np.zeros(period)
			for i in range(period):
				if i == device.arrive:
					EV_SOC0 = 0.1 # car arrives discharged
				if b_schedule[i] > 0 and EV_SOC0 < 1:
					b1_schedule[i] = np.min((device.umax,b_schedule[i],(1-EV_SOC0)*EV_cap/t_step))
					b_schedule[i] += -b1_schedule[i]
					EV_SOC0 += b1_schedule[i]*t_step
				elif b_schedule[i] < 0 and b_schedule[i] < s_umin:
					b1_schedule = b_schedule[i] - s_umin
					b_schedule[i] += -b1_schedule[i]
					EV_SOC0 += b1_schedule[i]*t_step

			Q = np.cumsum(b_schedule)*t_step + s_SOC0*s_cap
			device.makeSchedule(b1_schedule)
			device_s.makeSchedule(b_schedule)
			
			#print Q
			#print b1_schedule
			#print EV_SOC0

			#plt.figure()
			#plt.plot(b_schedule)
			#plt.show()


	# need to include aggregate battery and function to split agggregate battery accross EV and powerwall
	def rapidControl(self, agg, actual, umax, umin, SOC):
		b = agg - actual
		umin, umax = self.batteries['powerwall'] 
		return b



class ScheduledLoad(object):
	# object containing info for loads that follow a set schedule
	# Clothes washer, dryer, dish washer
	def __init__(self, Nmodes, shapes=np.nan, p_start=0.03/12):
		#self.name = name
		self.Nmodes = Nmodes # number of operating modes I.E. high power, low power, off
		if Nmodes == 2:
			self.shapes = shapes # dictionary of power profiles for each operating mode or just array if only 2 modes (on / off)
		else:
			self.shapes = {}
			self.shapes[0] = shapes
			# do more things

		self.p_start = p_start # probability of load starting each hour
		self.base = 0
		self.last_time = None
		self.op_mode = 0

	def preferences(self, last_time, mode):
		# agg is aggregate load shape to be tracked
		# last_time is the latest the device can turn on
		# mode is the operating mode requested by the user
		self.last_time = last_time
		self.op_mode = mode

	def makeSchedule(self, period, s_time, op_mode=None):
		if op_mode is None:
			op_mode = self.op_mode
		self.schedule = np.zeros(period)
		self.schedule[s_time:s_time+self.l_time] = op_mode # value of 1 for each time period device is on
		self.p_schedule = np.zeros(period)
		self.p_schedule[s_time:s_time+self.l_time] = self.c_shape # current shape to power schedule

	def getSchedulingInfo(self):
		if self.Nmodes == 2:
			self.l_time = self.shapes.size
			self.c_shape = self.shapes
		else:
			self.l_time = self.shapes[self.op_mode].size
			self.c_shape = self.shapes[self.op_mode]

		return self.c_shape, self.l_time

	def getBaseline(self, period, random=True, p_start=None):
		# period is number of hours in period
		starts = []
		if p_start is None:
			p_start = self.p_start
		for i in range(period):
			starts.append(np.random.binomial(1,p_start))

		starts = np.array(starts)
		#print np.sum(starts)
		if np.any(starts > 0):
			s_when = np.where(starts > 0)
			#print starts
			s_when = s_when[0][0]
			self.base = np.zeros(period)
			duration = self.shapes.size
			self.base[s_when:s_when+duration] = self.shapes
		else:
			self.base = np.zeros(period)




class DutyLoad(object):
	# object containing info for loads that are always running with adjustable duty cycle
	# AC, refridgerator, water heater, pool pump
	# assumed to have only on/off control

	def __init__(self, lower_limit, upper_limit, capacity, leakage, on_power, SOC0, t_step):
		# lower and upper limit on operating regime (temperature, pool water quality, etc)
		# virtual capacity of upper - lower limit I.E. how much energy is needed to be spent to go from upper to lower limit
		# virtual leakage of energy I.E how much energy is lost to the environment over time
		# average power consumed when turned on
		# t_step is fraction of an hour for each time step
		self.lower_limit = lower_limit
		self.upper_limit = upper_limit
		self.capacity = capacity
		self.leakage = leakage
		self.on_power = on_power
		self.SOC0 = SOC0 # initial SOC
		self.base = 0
		self.t_step = t_step


	def getBaseline(self, period, random=True):

		duty_on = self.capacity/2./((self.on_power - self.leakage)*self.t_step)
		#print duty_on
		duty_off = self.capacity/2./(self.leakage*self.t_step)
		pattern = np.concatenate([np.zeros(int(duty_on)), np.ones(int(duty_off))])
		#print pattern
		reps = int(period/pattern.size) + 1
		self.base = np.tile(pattern, reps) * self.on_power
		self.base = self.base[0:period]
		#print self.base
		#print self.base.shape


	def preferences(self, lower_limit, upper_limit, SOC0):
		# redifine temperature limits
		self.lower_limit = lower_limit
		self.upper_limit = upper_limit
		self.SOC0 = SOC0

	def nextCapacity(self, SOC):
		SOC_up = SOC + (self.on_power - self.leakage)*self.t_step/self.capacity
		SOC_down = SOC - self.leakage*self.t_step/self.capacity
		return SOC_up, SOC_down

	def makeSchedule(self, schedule):
		self.schedule = schedule
		self.p_schedule = schedule*self.on_power


class Battery(object):
	# object containing info for batteries like EV or powerwall

	def __init__(self, umin, umax, capacity, SOC0, leakage=0):
		self.umin = umin
		self.umax = umax
		self.capacity = capacity
		self.leakage = leakage
		self.SOC0 = SOC0 # initial SOC
		self.base = None
		self.q_req = None

	def preferences(self, q_req):
		# q_req is minimum required state of charge profile
		self.q_req = q_req
		c_where = np.where(q_req > 0)[0] # times when EV is gone
		c_where = np.split(c_where, np.where(np.diff(c_where) != 1)[0]+1)
		c_start = c_where[0][0]
		c_end = c_where[0][-1]
		self.leave = c_start
		self.arrive = c_end


	def getBaseline(self, period):
		mod = 1 + 0.1*np.random.randn(1)
		self.base = np.zeros(period)
		mask = self.q_req == 0
		# take max required SOC and split approximate charge of that over parked hours
		self.base[mask] = np.max(self.q_req)*mod/np.sum(mask) / 2 # reduce EV baseline
		#print self.base

	def makeSchedule(self, p_schedule):
		self.p_schedule = p_schedule

	def getLimits(self, SOC):
		umax = np.min(self.umax,(1-SOC)*self.capacity/t_step)
		umin = np.max(self.umin,-SOC*self.capacity/t_step)
		return umin, umax