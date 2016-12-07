#!/usr/bin/env python3

###########################################
# @author:	AbdAlMoniem AlHifnawy			#
#														#
# @email:	hifnawy_moniem@hotmail.com 	#
#														#
# @date:		Thu Dec 1 5:28:03 PM 			#
###########################################

from GridWorld import GridWorld
from tkinter import *
from tkinter import messagebox
import math
import time

class Policy:
	valueIterationEpsilon = 0.1
	maxNumberOfIterations = 0		#for example the maps that have no exits
	timeToLive = 0			#number of seconds to iterate before exiting (if algorithm stucks)
	_pe_maxk = 50	#for policy evaluation, max number of iteration
		
	world = None
	
	numOfIterations = 0
	elapsed = 0
	utilities = None #memorized as the world grid [y][x]
	policy = None #created 
	
	def __init__(self, world):
		self.world = world
		self.resetResults()

		Policy.maxNumberOfIterations = self.world.numberOfIterations
		Policy.timeToLive = self.world.timeToLive
		
	def __createEmptyUtilityVector(self):
		'''creates an empty utility vector (that in this case is a matrix), with all number to 0'''
		c, r = self.world.size 
		return [ [ 0 for _ in range(c) ] for _ in range(r) ]
				
	def resetResults(self):
		self.numOfIterations = 0
		self.utilities = self.__createEmptyUtilityVector()
	
	#===========================================================================
	# Value Iteration 
	#===========================================================================
	
	def valueIteration(self, debugCallback = None, turbo = False):
		'''using the value iteration algorithm (see AI: A Modern Approach (Third ed.) pag. 652)
		   calculate the utilities for all states in the grid world
		   
		   the debugCallback must be a function that has three parameters:
				policy: that the function can use to display intermediate results
				isEnded: that the function can use to know if the valueIteration is ended
			the debugCallback must return True, and can stop the algorithm returning False
			
			the algorithm has a maximum number of iterations, in this way we can compute an
			example with a discount factor = 1 that converge.
			
			the turbo mode uses the utility vector of the (i-1)-th iteration to compute
			the utility vector of the i-th iteration. The classic approach is different because
			we compute the i-th iteration using the utility vector of the (i-1)-th iteration.
			With this algorithm, using the turbo mode, we have an improvement of 30%
		   
		   returns the number of iterations it needs for converge
		'''
		eps = Policy.valueIterationEpsilon
		dfact = self.world.discFactor
		c, r = self.world.size
		if turbo: newUv = self.utilities
		
		reiterate = True
		start = time.process_time()
		while(reiterate):
			self.numOfIterations += 1
			maxNorm = 0 #see the max norm definition in AI: A Modern Approach (Third ed.) pag. 654
			
			if not turbo: newUv = self.__createEmptyUtilityVector()
			
			for x in range(c):
				for y in range(r):
					v = self.__cellUtility(x, y) #calculate using the self.utilities (i.e. the previous step)
					if not v is None: maxNorm = max(maxNorm, abs(self.utilities[y][x] - v))
					newUv[y][x] = v #update the new utility vector that we are creating
					
			if not turbo: self.utilities = newUv
			
			if debugCallback: reiterate = debugCallback(self, False)
			
			if maxNorm <= eps * (1 - dfact)/dfact: reiterate = False

			end = time.process_time()
			self.elapsed = end - start
			if self.numOfIterations >= Policy.maxNumberOfIterations or self.elapsed > Policy.timeToLive:
				reiterate = False
				print("warning: max number of iterations exceeded")
				messagebox.showwarning("Warning", "max number of iterations exceeded")
		
		if debugCallback: reiterate = debugCallback(self, True)
					
		return self.numOfIterations
	
	def __cellUtility(self, x, y):
		'''calculate the utility of a function using an utilities that is less precise (i.e. using the 
			utility vector of the previous step. In the turbo mode it use the current step, 
			it leads the computation to end soon)
			
			this is the Bellman update (see AI: A Modern Approach (Third ed.) pag. 652)
		'''
		if self.world.cellAt(x,y) == GridWorld.CELL_VOID:
			maxSum = None
			for action in GridWorld.actionSet:
				summ = 0
				possibilities = self.world.possiblePositionsFromAction((x,y), action) 
				for _, nextPos, prob in possibilities:
					summ += prob * self.utilities[nextPos[1]][nextPos[0]]
				if (maxSum is None) or (summ > maxSum): maxSum = summ
			res = self.world.rewardAtCell(x, y) + self.world.discFactor * maxSum
		else:
			#we don't have any action to do, we have only own reward (i.w. V*(s) = R(s) + 0)
			res = self.world.rewardAtCell(x, y) 
		return res
	
	#===========================================================================
	# Policy Iteration 
	#===========================================================================
	
	def __createEmptyPolicy(self):
		'''we create a partial function that is undefined in all points'''
		c, r = self.world.size
		return [ [ (None if self.world.cellAt(x,y) == GridWorld.CELL_VOID else GridWorld.randomAction()) for x in range(c) ] for y in range(r) ]
	
	def policyIteration(self, debugCallback = None, turbo = False):
		'''Policy iteration algorithm (see AI: A Modern Approach (Third ed.) pag. 656)
		   
		   the debugCallback must be a function that has three parameters:
				policy: that the function can use to display intermediate results
				isEnded: that the function can use to know if the policyIteration is ended
			the debugCallback must return True, and can stop the algorithm returning False
		   
		   returns the number of iterations it needs to find the fixed point
		'''
		
		c, r = self.world.size
		policy = self.__createEmptyPolicy()
		
		reiterate = True
		start = time.time()
		while(reiterate):
			self.numOfIterations += 1
			
			self.policyEvaluation(policy, turbo)
			
			someChanges = False
			for x in range(c):
				for y in range(r):
					if self.world.cellAt(x,y) == GridWorld.CELL_VOID:
						newMax = None
						argMax = None
						for action in GridWorld.actionSet:
							summ = 0
							possibilities = self.world.possiblePositionsFromAction((x,y), action) 
							for _, nextPos, prob in possibilities:
								summ += prob * self.utilities[nextPos[1]][nextPos[0]]
							if (newMax is None) or (summ > newMax):
								argMax = action
								newMax = summ
						
						summ = 0
						possibilities = self.world.possiblePositionsFromAction((x,y), policy[y][x]) 
						for _, nextPos, prob in possibilities:
							summ += prob * self.utilities[nextPos[1]][nextPos[0]]
						if newMax > summ:
							policy[y][x] = argMax
							someChanges = True
			
			if debugCallback:
				reiterate = debugCallback(self, False)
			
			reiterate = someChanges
			
			end = time.time()
			self.elapsed = end - start
			if self.numOfIterations >= Policy.maxNumberOfIterations or self.elapsed > Policy.timeToLive:
				reiterate = False
				print("warning: newMax number of iterations exceeded")
				messagebox.showwarning("Warning", "max number of iterations exceeded")
		
		if debugCallback:
					reiterate = debugCallback(self, True)
					
		return self.numOfIterations
	
	def policyEvaluation(self, policy, turbo = False):
		'''Policy Evaluation (see AI: A Modern Approach (Third ed.) pag. 656)
			used by the policy iteration
		'''
		eps = Policy.valueIterationEpsilon
		dfact = self.world.discFactor
		c, r = self.world.size
		
		turbo = False
		if turbo: newUv = self.utilities
		
		numOfIterations = 0
		reiterate = True
		while(reiterate):
			maxNorm = 0
			numOfIterations += 1
			
			if not turbo: newUv = self.__createEmptyUtilityVector()
			
			for x in range(c):
				for y in range(r):
					newUv[y][x] = self.world.rewardAtCell(x,y)
					if self.world.cellAt(x,y) == GridWorld.CELL_VOID:
						action = policy[y][x]
						#if action is None: action = policy[y][x] = GridWorld.randomAction()
						
						possibilities = self.world.possiblePositionsFromAction((x,y), action) 
						for _, nextPos, prob in possibilities:
							newUv[y][x] += prob * self.utilities[nextPos[1]][nextPos[0]]
						newUv[y][x] *= self.world.discFactor
					maxNorm = max(maxNorm, abs(self.utilities[y][x] - newUv[y][x]))
					
			if not turbo: self.utilities = newUv
			
			if maxNorm <= eps * (1 - dfact)/dfact: reiterate = False
			elif numOfIterations >= Policy._pe_maxk: reiterate = False
				
		# print(numOfIterations)
			
	#===========================================================================
	# Other functions
	#===========================================================================
	
	def getQValues(self, s, action = None):
		'''calculate the q-value Q(s, a). It is the utility of the state s if we perform the action a 
			if action is None it returns a list with the possible q-value for the state s 
			for all possible actions.
		'''
		x,y = s
		
		if self.world.cellAt(x,y) != GridWorld.CELL_VOID: return None
		
		if action is None:
			res = {}
			for action in GridWorld.actionSet:
				res[action] = self.getQValues(s, action) 
		else:
			
			summ = 0
			possibilities = self.world.possiblePositionsFromAction((x,y), action) 
			for _, nextPos, prob in possibilities:
				summ += prob * self.utilities[nextPos[1]][nextPos[0]]
			res = self.world.rewardAtCell(x, y) + self.world.discFactor * summ
		
		return res
		
	def getPolicyFromQValues(self, s):
		'''calculate the policy of the state s
			the policy for the state s is the best action to do if you want to have the best possible reward
		'''
		def argmaxQValues(s):
			qv = self.getQValues(s)
			return (max(qv.items(), key = lambda c: c[1])[0] if qv else None) 
		return argmaxQValues(s)
	
	def getPolicyFromUtilityVector(self, s):
		'''calculate the policy of the state s
			the policy for the state s is the best action to do if you want to have the best possible reward
		'''
		x,y = s
		if self.world.cellAt(x,y) != GridWorld.CELL_VOID: return None
		def argmaxValues(s):
			res = {}
			for action in GridWorld.actionSet:
				res[action] = 0
				possibilities = self.world.possiblePositionsFromAction((x,y), action) 
				for _, nextPos, prob in possibilities:
					res[action] += prob * self.utilities[nextPos[1]][nextPos[0]]
			return (max(res.items(), key = lambda c: c[1])[0] if res else None) 
		return argmaxValues(s)
		
	#===========================================================================
	# String representation 
	#===========================================================================
	
	def utilityVectorToString(self):
		'''utilities string representation''' 
		c, r = self.world.size 
		ris = ""		
		for y in range(r):
			for x in range(c):
				u = self.utilities[y][x]
				ris += "       " if u is None else "% 2.3f " % u
			if y < r - 1: ris += "\n"
		return ris
	
	def qValuesToString(self):
		'''qValues string representation'''
		c, r = self.world.size 
		ris = ""
		for y in range(r):
			for x in range(c):
				ris += "[ "
				for a in GridWorld.actionSet:
					v = self.getQValues((x, y), a)
					if not v is None: ris += "%s : % 2.3f, " % (a, v)
				ris += "] "
			if y < r - 1: ris += "\n"
		return ris

	def policyToString(self):
		'''policy string representation''' 
		c, r = self.world.size 
		ris = ""		
		for y in range(r):
			for x in range(c):
				a = self.getPolicyFromQValues((x,y))
				ris += "_ " if a is None else "%c " % a
			if y < r - 1: ris += "\n"
		return ris
		
	#===========================================================================
	# Graphical representation 
	#===========================================================================
	
	def __getColorFromValue(self, v):
		if v > 0:
			u = 255 * min(v, self.world.rew[GridWorld.CELL_EXIT]) / self.world.rew[GridWorld.CELL_EXIT]			
			return "#%02x%02x%02x" % (255 - int(u), 255, 255 - int(u))
		else:
			u = 255 * max(v, self.world.rew[GridWorld.CELL_PIT]) / self.world.rew[GridWorld.CELL_PIT]
			return "#%02x%02x%02x" % (255, 255 - int(u), 255 - int(u))
		
	def drawUtilities(self, canvas):
		'''draw only the utilities, you must call the other draw methods to draw the other things'''
		m = GridWorld.drawing_BoxMargin
		s = GridWorld.drawing_BoxSide
		s2 = math.ceil(s/2)
		ox, oy = GridWorld.drawing_offset
		for x in range(self.world.size[0]):
			for y in range(self.world.size[1]):
				if self.world.cellAt(x,y) == GridWorld.CELL_WALL: continue
				if self.world.cellAt(x,y) == GridWorld.CELL_EXIT: 
					color = "#00ff64"
				elif self.world.cellAt(x,y) == GridWorld.CELL_PIT: 
					color = "#ff0000" 
				elif (self.world.cellAt(x,y) == GridWorld.CELL_VOID) and self.utilities[y][x]:
					color = self.__getColorFromValue(self.utilities[y][x])
				else:
					color = "#ffffff"
				xp, yp = x*(s+m) + ox, y*(s+m) + oy
				canvas.create_rectangle(xp, yp, xp + s, yp + s, fill=color)
				canvas.create_text(xp + s2, yp + s2, anchor = CENTER, font = ("AgencyFB", "20", "bold"),
													 text = ("%2.3f" % self.utilities[y][x]))

	def drawQValues(self, canvas):
		'''draw only the q-values, you must call the other draw methods to draw the other things'''
		m = GridWorld.drawing_BoxMargin
		tm = 4 #text margin from the border
		s = GridWorld.drawing_BoxSide
		s2 = math.ceil(s/2)
		ox, oy = GridWorld.drawing_offset
		for x in range(self.world.size[0]):
			for y in range(self.world.size[1]):
				qvalues = self.getQValues((x, y))
				if not qvalues: continue
				xp, yp = x*(s+m) + ox, y*(s+m) + oy
				xc, yc = xp + s2, yp + s2

				for q in (qvalues).items():
					color = self.__getColorFromValue(q[1])
					if q[0] == GridWorld.ACTION_EAST:
						points = [xp + s, yp, xp + s, y*(s+m) + oy + s, xc, yc]
					elif q[0] == GridWorld.ACTION_WEST:
						points = [xp, yp, xp, yp + s, xc, yc]
					elif q[0] == GridWorld.ACTION_NORTH:
						points = [xp, yp, xp + s, yp, xc, yc]
					else:
						points = [xp, yp + s, xp + s, yp + s, xc, yc]
					canvas.create_polygon(points, fill = color, width = 1, outline = "black")

				largest_utility = ''
				maxs = -999;
				for key, val in qvalues.items():
					k = key
					v = val
					if val > maxs:
						maxs = val
						largest_utility = k


				normal_style = ("AgencyFB", "12")
				bold_style = ("AgencyFB", "14", "bold")

				if largest_utility == GridWorld.ACTION_WEST:
					canvas.create_text(xp + tm, yc, anchor = W, font = bold_style, 
													text = ("%2.2f" % qvalues[GridWorld.ACTION_WEST]))
					canvas.create_text(xp + s - tm, yc, anchor = E, font = normal_style, 
														text = ("%2.2f" % qvalues[GridWorld.ACTION_EAST]))
					canvas.create_text(xc, yp + tm, anchor = N, font = normal_style, 
													text = ("%2.2f" % qvalues[GridWorld.ACTION_NORTH]))
					canvas.create_text(xc, yp + s - tm, anchor = S, font = normal_style, 
														text = ("%2.2f" % qvalues[GridWorld.ACTION_SOUTH]))
				elif largest_utility == GridWorld.ACTION_EAST:
					canvas.create_text(xp + tm, yc, anchor = W, font = normal_style, 
													text = ("%2.2f" % qvalues[GridWorld.ACTION_WEST]))
					canvas.create_text(xp + s - tm, yc, anchor = E, font = bold_style, 
														text = ("%2.2f" % qvalues[GridWorld.ACTION_EAST]))
					canvas.create_text(xc, yp + tm, anchor = N, font = normal_style, 
													text = ("%2.2f" % qvalues[GridWorld.ACTION_NORTH]))
					canvas.create_text(xc, yp + s - tm, anchor = S, font = normal_style, 
														text = ("%2.2f" % qvalues[GridWorld.ACTION_SOUTH]))
				elif largest_utility == GridWorld.ACTION_NORTH:
					canvas.create_text(xp + tm, yc, anchor = W, font = normal_style, 
													text = ("%2.2f" % qvalues[GridWorld.ACTION_WEST]))
					canvas.create_text(xp + s - tm, yc, anchor = E, font = normal_style, 
														text = ("%2.2f" % qvalues[GridWorld.ACTION_EAST]))
					canvas.create_text(xc, yp + tm, anchor = N, font = bold_style, 
													text = ("%2.2f" % qvalues[GridWorld.ACTION_NORTH]))
					canvas.create_text(xc, yp + s - tm, anchor = S, font = normal_style, 
														text = ("%2.2f" % qvalues[GridWorld.ACTION_SOUTH]))
				elif largest_utility == GridWorld.ACTION_SOUTH:
					canvas.create_text(xp + tm, yc, anchor = W, font = normal_style, 
													text = ("%2.2f" % qvalues[GridWorld.ACTION_WEST]))
					canvas.create_text(xp + s - tm, yc, anchor = E, font = normal_style, 
														text = ("%2.2f" % qvalues[GridWorld.ACTION_EAST]))
					canvas.create_text(xc, yp + tm, anchor = N, font = normal_style, 
													text = ("%2.2f" % qvalues[GridWorld.ACTION_NORTH]))
					canvas.create_text(xc, yp + s - tm, anchor = S, font = bold_style, 
														text = ("%2.2f" % qvalues[GridWorld.ACTION_SOUTH]))

	
	def drawPolicy(self, canvas):
		'''draw only the policy, you must call the other draw methods to draw the other things'''
		#commented lines are part of an alternative way to draw the arrows
		m = GridWorld.drawing_BoxMargin
		arrs = int(GridWorld.drawing_BoxSide/4) #arrow base size
		arrh = int(GridWorld.drawing_BoxSide/5) #arrow height
		s = GridWorld.drawing_BoxSide
		s2 = math.ceil(s/2)
		#s4 = math.ceil(s/4)
		ox, oy = GridWorld.drawing_offset
		for x in range(self.world.size[0]):
			for y in range(self.world.size[1]):
				xp, yp = x*(s+m) + ox, y*(s+m) + oy
				xc, yc = xp + s2, yp + s2
				#policy = self.getPolicyFromQValues((x,y))
				policy = self.getPolicyFromUtilityVector((x,y))
				if policy:
					if policy == GridWorld.ACTION_NORTH:
						#points = [xc - arrs/2, yp + s4 + arrh/2, xc + arrs/2, yp + s4 + arrh/2, xc, yp + s4 - arrh/2]
						points = [xc - arrs/2, yc + arrh/2, xc + arrs/2, yc + arrh/2, xc, yc - arrh/2]
					elif policy == GridWorld.ACTION_SOUTH:
						#points = [xc - arrs/2, yp + s - s4 - arrh/2, xc + arrs/2, yp + s - s4 - arrh/2, xc, yp + s - s4 + arrh/2]
						points = [xc - arrs/2, yc - arrh/2, xc + arrs/2, yc - arrh/2, xc, yc + arrh/2]
					elif policy == GridWorld.ACTION_WEST:
						#points = [xp + s4 + arrh/2, yp + s2 - arrs/2, xp + s4 + arrh/2, yc + arrs/2, xp + s4 - arrh/2, yc]
						points = [xc + arrh/2, yp + s2 - arrs/2, xc + arrh/2, yc + arrs/2, xc - arrh/2, yc]
					else: #EAST
						#points = [xp + s - s4 - arrh/2, yc - arrs/2, xp + s - s4 - arrh/2, yc + arrs/2, xp + s - s4 + arrh/2, yc]
						points = [xc - arrh/2, yc - arrs/2, xc - arrh/2, yc + arrs/2, xc + arrh/2, yc]
					canvas.create_polygon(points, fill='black', width=1, outline="white")
		
	def draw(self, canvas):
		'''a method to draw all in the right order'''
		canvas.delete(ALL)
		self.world.draw(canvas)
		self.drawUtilities(canvas)
		self.drawQValues(canvas)
		self.drawPolicy(canvas)
	
		
#===========================================================================
# TEST
#===========================================================================
if __name__ == '__main__':

	w = GridWorld([[GridWorld.CELL_VOID, GridWorld.CELL_VOID, GridWorld.CELL_VOID, GridWorld.CELL_EXIT], 
			   [GridWorld.CELL_VOID, GridWorld.CELL_WALL, GridWorld.CELL_VOID, GridWorld.CELL_PIT],
			   [GridWorld.CELL_VOID, GridWorld.CELL_VOID, GridWorld.CELL_VOID, GridWorld.CELL_VOID]], discountFactor = 1 )
	w.setRewards(-0.04, -1, 1)
	w.setProbabilities(0.8, 0.1, 0.1, 0)
	print("GridWorld-----------")
	print(w)
	print("----------------")
	
	print("\nPolicy----------")
	p = Policy(w)
	
	print("ValueIteration iterations: %d" % p.valueIteration())
	print("")
	print(p.utilityVectorToString())
	print("")
	print(p.qValuesToString())
	print("")
	print(p.policyToString())
	print("----------------")
	
	p.resetResults()
	print("Policy iterations: %d" % p.policyIteration(turbo=True))
	print(p.utilityVectorToString())
	print(p.policyToString())
	print("----------------")
	
	print(p.getQValues((0, 1)))