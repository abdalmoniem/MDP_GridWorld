#!/usr/bin/env python3

###########################################
# @author:	AbdAlMoniem AlHifnawy			#
#														#
# @email:	hifnawy_moniem@hotmail.com 	#
#														#
# @date:		Thu Dec 1 5:28:03 PM 			#
###########################################

import tkinter.ttk
import random

class GridWorld:
	
	'''The GridWorld has four types of cell:
			we can walk through the void __cells
			we complete the game if we go to the exit cell
			we loose if we fall into a pit
	'''
	CELL_VOID = 0
	CELL_PIT  = 1
	CELL_EXIT = 2
	CELL_WALL = 3
	__cells = None
	size = (0, 0) #(columns, rows)
	
	ACTION_NORTH = 'N'
	ACTION_SOUTH = 'S'
	ACTION_WEST  = 'W'
	ACTION_EAST  = 'E'
	actionSet = (ACTION_NORTH, ACTION_SOUTH, ACTION_WEST, ACTION_EAST)
	
	# Probabilities
	PROB_FORWARD  = 'F'
	PROB_BACKWARD = 'B'
	PROB_LEFT     = 'L'
	PROB_RIGHT    = 'R'
	prob = None
	
	rew = None
	discFactor = 0
	
	# Drawing parameters
	drawing_BoxSide = 120
	drawing_BoxMargin = 2
	drawing_offset = (5,5)
	
	def __init__(self, cells, discountFactor = 1):
		'''the __cells is a matrix memorized in this way 
			[[[cell 1 of first row, cell 2 of first row, ...]],[row2], ...]
		'''


		cells_width = len(cells[0])
		inc = (cells_width * 120) / 480
		if inc != 1: GridWorld.drawing_BoxSide /= inc * 0.5
		
		self.__cells = cells
		self.size = (len(self.__cells[0]), len(self.__cells))
		self.discFactor = discountFactor
		
	def transitionFunction(self, position, action):
		''' this function describes the movements that we can do (deterministic)
			if we are in a pit, in a exit or in a wall cell we can't do anything
			we can't move into a wall
			we can't move out the border of the grid
			returns the new position
		'''
		if action not in self.actionSet:
			raise Exception("unknown action")
		if self.__cells[position[1]][position[0]] != self.CELL_VOID: 
			raise Exception("no action allowed")
		
		if action == self.ACTION_NORTH:
			ris = (position[0], max(0, position[1] - 1))
		elif action == self.ACTION_SOUTH:
			ris = (position[0], min(len(self.__cells) - 1, position[1] + 1))
		elif action == self.ACTION_WEST:
			ris = (max(0, position[0] - 1), position[1])
		else:
			ris = (min(len(self.__cells[0]) - 1, position[0] + 1), position[1])
			
		if self.__cells[ris[1]][ris[0]] == self.CELL_WALL: return position
		return ris
	
	def cellTypeAt(self, x, y):
		return self.__cells[y][x]
	
	def cellAt(self, x, y): 
		'''pos is a tuple (x,y)'''
		return self.__cells[y][x]
	
	def setDiscountFactor(self, df):
		self.discFactor = df
		
	def setRewards(self, rewOfVoidCell, rewOfPitCell, rewOfExitCell):
		self.rew = {self.CELL_VOID : rewOfVoidCell, 
					self.CELL_EXIT : rewOfExitCell, 
					self.CELL_PIT  : rewOfPitCell,
					self.CELL_WALL : 0}
	
	def setProbabilities(self, probToGoForward, probToGoLeft, probToGoRight, probToGoBackward):
		if probToGoForward + probToGoLeft + probToGoRight + probToGoBackward != 1:
			raise Exception('the prob must have 1 as sum')
		self.prob = {self.PROB_FORWARD  : probToGoForward, 
				     self.PROB_LEFT     : probToGoLeft, 
				     self.PROB_RIGHT    : probToGoRight, 
				     self.PROB_BACKWARD : probToGoBackward}
		
	def possiblePositionsFromAction(self, position, worldAction):
		'''
			given an action worldAction, return a dictionary D, 
			where for each action a, D[a] is the probability to do the action a
		'''
		
		def getProbabilitiesFromAction(worldAction):
			if worldAction == self.ACTION_NORTH:
				return {self.ACTION_NORTH : self.prob[self.PROB_FORWARD], 
						self.ACTION_SOUTH : self.prob[self.PROB_BACKWARD], 
						self.ACTION_WEST  : self.prob[self.PROB_LEFT], 
						self.ACTION_EAST  : self.prob[self.PROB_RIGHT]}
			elif worldAction == self.ACTION_SOUTH:
				return {self.ACTION_NORTH : self.prob[self.PROB_BACKWARD], 
						self.ACTION_SOUTH : self.prob[self.PROB_FORWARD], 
						self.ACTION_WEST  : self.prob[self.PROB_RIGHT], 
						self.ACTION_EAST  : self.prob[self.PROB_LEFT]}
			elif worldAction == self.ACTION_WEST:
				return {self.ACTION_NORTH : self.prob[self.PROB_RIGHT], 
						self.ACTION_SOUTH : self.prob[self.PROB_LEFT], 
						self.ACTION_WEST  : self.prob[self.PROB_FORWARD], 
						self.ACTION_EAST  : self.prob[self.PROB_BACKWARD]}
			else:
				return {self.ACTION_NORTH : self.prob[self.PROB_LEFT], 
						self.ACTION_SOUTH : self.prob[self.PROB_RIGHT], 
						self.ACTION_WEST  : self.prob[self.PROB_BACKWARD], 
						self.ACTION_EAST  : self.prob[self.PROB_FORWARD]}
			
		if not (self.__cells[position[1]][position[0]] == self.CELL_VOID):
			return [] #we can do anything in the wall, in a pit or in a exit
		
		prob = getProbabilitiesFromAction(worldAction)
		result = []  
		for a in self.actionSet:
			result.append((a, self.transitionFunction(position, a), prob[a]))
		return result
	
	@staticmethod
	def randomAction():
		return GridWorld.actionSet[int(random.random() * 4)]
	
	def rewardAtCell(self, x, y):
		return self.rew[self.__cells[y][x]]

	def __str__(self):
		ris = ""
		numRows = len(self.__cells)
		for r in self.__cells:
			for c in r:
				if c == self.CELL_EXIT: ris += "E "
				elif c == self.CELL_PIT: ris += "P "
				elif c == self.CELL_WALL: ris += "W "
				else: ris += "V "
			numRows -= 1
			if numRows > 0: ris += "\n"
		return ris
	
	def newCanvasToDraw(self, master):
		return tkinter.Canvas(master, width  = self.drawing_offset[0] 
											 + self.size[0] * self.drawing_BoxSide 
											 + (self.size[0] - 1) * self.drawing_BoxMargin, 
									  height = self.drawing_offset[1] 
									  		 + self.size[1] * self.drawing_BoxSide 
									  		 + (self.size[1] - 1) * self.drawing_BoxMargin)
		
	def draw(self, canvas):
		m = self.drawing_BoxMargin
		s = self.drawing_BoxSide
		ox, oy = self.drawing_offset
		for x in range(self.size[0]):
			for y in range(self.size[1]):
				xp, yp = x*(s+m) + ox, y*(s+m) + oy
				if self.__cells[y][x] == self.CELL_WALL:
					color = "#%02x%02x%02x" % (50,50,50)
				elif self.__cells[y][x] == self.CELL_EXIT:
					color = "#%02x%02x%02x" % (0,255,100)
				elif self.__cells[y][x] == self.CELL_PIT:
					color = "#%02x%02x%02x" % (255,0,0)
				else:
					color = "#%02x%02x%02x" % (255,255,255)
				canvas.create_rectangle(xp, yp, xp + s, yp + s, fill=color)
		
	
#===========================================================================
# TEST
#===========================================================================
if __name__ == '__main__':

	w = GridWorld([[GridWorld.CELL_VOID, GridWorld.CELL_VOID, GridWorld.CELL_VOID, GridWorld.CELL_EXIT], 
			   		[GridWorld.CELL_VOID, GridWorld.CELL_WALL, GridWorld.CELL_VOID, GridWorld.CELL_PIT],
			   		[GridWorld.CELL_VOID, GridWorld.CELL_VOID, GridWorld.CELL_VOID, GridWorld.CELL_VOID]])
	
	print("GridWorld:")
	print(w)
	
	print("\nSome transitions:")
	print(w.transitionFunction((1,0), GridWorld.ACTION_NORTH))
	print(w.transitionFunction((0,0), GridWorld.ACTION_NORTH))
	print(w.transitionFunction((1,0), GridWorld.ACTION_SOUTH))
	print(w.transitionFunction((1,0), GridWorld.ACTION_SOUTH))
	
	w.setRewards(-0.04, -1, 1)
	w.setProbabilities(0.7, 0.1, 0.2, 0)
	
	print("\nPossible positions:")
	print(w.possiblePositionsFromAction((0,0), GridWorld.ACTION_NORTH))
	print(w.possiblePositionsFromAction((0,0), GridWorld.ACTION_SOUTH))
	
	print("\nRewards:")
	print("%5.2f" %w.rewardAtCell(0, 0))
	print("%5.2f" %w.rewardAtCell(1, 1))
	print("%5.2f" %w.rewardAtCell(3, 0))
	print("%5.2f" %w.rewardAtCell(3, 1))