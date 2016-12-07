###########################################
# @author:	AbdAlMoniem AlHifnawy			#
#														#
# @email:	hifnawy_moniem@hotmail.com 	#
#														#
# @date:		Thu Dec 1 5:28:03 PM 			#
###########################################

from tkinter import *
import time
from GridWorld import GridWorld
from Policy import Policy
from idlelib.textView import TextViewer

#===============================================================================
# MDPGUI - shows the map, q-values, utilities and 
#	      the interface with which you can compute the policy
#===============================================================================

class MDPGUI:
	
	w = None #GridWorld
	p = None #Policy
	master = None #the form
	c = None #canvas
	whatToShow = None #callback function to call from the debug callback
	computationStarted = False
	algorithm = None #algorihm to use, is a string "vi" for value iteration, "pi" for policy iteration
	superMode = None
	
	def cbShowMap(self):
		self.c.delete(ALL)
		self.whatToShow = self.cbShowMap
		self.p.world.draw(self.c)
		
	def cbShowUtilities(self):
		self.whatToShow = self.cbShowUtilities
		self.c.delete(ALL)
		self.p.world.draw(self.c)
		self.p.drawUtilities(self.c)
		
	def cbShowQValues(self):
		self.whatToShow = self.cbShowQValues
		self.c.delete(ALL)
		self.p.world.draw(self.c)
		self.p.drawUtilities(self.c)
		self.p.drawQValues(self.c)
	
	def cbShowPolicy(self):
		self.whatToShow = self.cbShowPolicy
		self.p.draw(self.c)
	
	def debugCallBack(self, policy, isEnded):
		try:
			if isEnded and self.computationStarted: 
				self.tDebugModeIterations.config(text="Iterations: %d (complete)" % policy.numOfIterations)
				self.tDebugModeTimer.config(text="Elapsed: %.3f secs (complete)" % policy.elapsed)
				self.bComputation.config(state=DISABLED)
				self.bResetResults.config(state=NORMAL)
				self.superModeCheck.config(state=NORMAL)
				for b in self.radioBAlgorithms: b.config(state=NORMAL)
				self.computationStarted = False
				self.bComputation.config(text="Start Computation")
				self.bComputation.config(state=NORMAL)

				self.computationStarted = False
				return False
			
			if self.computationStarted:
				self.tDebugModeIterations.config(text="Iterations: %d" % policy.numOfIterations)
				self.tDebugModeTimer.config(text="Elapsed: %.3f secs" % policy.elapsed)
				if self.whatToShow: self.whatToShow()
				self.c.update()

				time.sleep(float(self.eSleep.get()))
				return True
				
		except Exception as ex: #when the window is closed
			print(ex)
			return False
	
	def toggleComputation(self):
		if not self.computationStarted:
			self.p.resetResults()
			self.bComputation.config(text="Stop Computation")
			self.computationStarted = True
			self.bResetResults.config(state=DISABLED)
			self.superModeCheck.config(state=DISABLED)
			for b in self.radioBAlgorithms: b.config(state=DISABLED)
			if self.algorithm.get() == "vi": 
				self.p.valueIteration(self.debugCallBack, self.superMode.get())
			else: 
				self.p.policyIteration(self.debugCallBack, self.superMode.get())
		else:
			self.bComputation.config(text="Start Computation")
			self.bResetResults.config(state=NORMAL)
			self.superModeCheck.config(state=NORMAL)
			for b in self.radioBAlgorithms: b.config(state=NORMAL)
			self.computationStarted = False
			
	def resetResults(self):
		self.bComputation.config(state=NORMAL)
		self.p.resetResults()
		if self.whatToShow: self.whatToShow()
		self.tDebugModeIterations.config(text="Iterations: 0")
		self.tDebugModeTimer.config(text="Elapsed: 0 secs")

	
	
	def __init__(self, world):
		self.w = world
		self.p = Policy(world)
		self.master = Tk()
		self.master.title("MDP GridWorld")
		self.master.resizable(0,0)
		self.c = self.w.newCanvasToDraw(self.master)
		self.c.pack(side=LEFT, padx=10, pady=10)
		self.p.world.draw(self.c)
	
		self.frame = Frame(self.master, relief=RAISED, borderwidth=1)
		self.frame.pack(fill=BOTH, side=LEFT, expand=1)
	
		self.whatToShow = None
		self.superMode = BooleanVar()
		self.algorithm = StringVar()
		self.algorithm.set("vi")
		
		self.bShowMap = Button(self.frame, text="Show Map", command=self.cbShowMap)
	
		self.bUtilities = Button(self.frame, text="Show Utilities", command=self.cbShowUtilities)
		
		self.bShowQvalues = Button(self.frame, text="Show Q-Values", command=self.cbShowQValues)
	
		self.bShowPolicy = Button(self.frame, text="Show Policy", command=self.cbShowPolicy)
	
		self.whatToShow = self.cbShowMap
	
		#COMPUTATION------------------------------------------
		self.frameComputation = Frame(self.frame)
	
		self.computationStarted = False
		self.bComputation = Button(self.frameComputation, text="Start Computation")
	
		self.bComputation.config(command=self.toggleComputation)
		self.bComputation.pack(side=TOP, padx=10, pady=5)
	
		self.radioBAlgorithms = []
		for text, mode in (("Value iteration", "vi"), ("Policy iteration", "pi")):
			b = Radiobutton(self.frameComputation, text=text, variable=self.algorithm, value=mode, command=self.resetResults)
			b.pack(anchor=W, padx=10, pady=5)
			self.radioBAlgorithms.append(b)

		self.frameSleep = Frame(self.frameComputation)
		self.tSleep = Label(self.frameSleep, text="Sleep (sec): ")
		self.eSleep = Spinbox(self.frameSleep, from_=0, to=10, increment=0.1, width=5)
		self.tSleep.pack(side=LEFT)
		self.eSleep.pack(side=LEFT)
		self.frameSleep.pack(side=TOP, padx=10, pady=5)
	
		self.superModeCheck = Checkbutton(self.frameComputation, text="Super", variable=self.superMode)
		self.superModeCheck.pack(side=TOP)
	
		self.tDebugModeIterations = Label(self.frameComputation, text="Iterations: 0")
		self.tDebugModeIterations.pack(side=TOP, padx=10, pady=5)
		self.tDebugModeTimer = Label(self.frameComputation, text="Elapsed: 0 secs")
		self.tDebugModeTimer.pack(side=TOP, padx=10, pady=5)
	
		self.bResetResults = Button(self.frameComputation, text="Reset Results")
	
		self.bResetResults.config(command=self.resetResults)
		self.bResetResults.pack(side=TOP, padx=10, pady=5)
	
		self.bShowMap.pack(side=TOP, padx=10, pady=5)
		self.bUtilities.pack(side=TOP, pady=5)
		self.bShowQvalues.pack(side=TOP, padx=10, pady=5)
		self.bShowPolicy.pack(side=TOP, pady=5)
		self.frameComputation.pack(side=BOTTOM, pady=20)
		

#===============================================================================
# MDPChooser - to choose the map and the values
#===============================================================================
		
class MDPChooser:
	rew = (("Step Reward", -0.04, "negative"), 
				("Pit Reward", -1, "negative"),
				("Exit Reward", 1, "positive"))
	rewValue = []
	

	algorithm_rest = (("Number of iterations", 1000),
							("Max. calculation time (secs)", 3))
	algorithm_restValue = []

	prob = (("Forward Probability", 0.8), 
			("Left Probability", 0.1),
			("Right Probability", 0.1),
			("Backward Probability", 0))
	probValue = []
	
	discFactor = None
	
	def checkSettingValues(self):
		self.errorLabel.config(text="")
		
		#check rewards
		for i in range(len(self.rew)):
			try:
				v = float(self.rewValue[i].get())
			except ValueError:
				self.errorLabel.config(text=("Error: %s is not a float number" % self.rew[i][0]))
				return False
			if (self.rew[i][2] == "negative") and (v > 0):
				self.errorLabel.config(text=("Error: %s must be negative" % self.rew[i][0]))
				return False
			elif (self.rew[i][2] == "positive") and (v < 0): 
				self.errorLabel.config(text=("Error: %s must be positive" % self.rew[i][0]))
				return False
		
		#check probabilities
		psum = 0
		for i in range(len(self.prob)):
			try:
				v = float(self.probValue[i].get())
			except ValueError:
				self.errorLabel.config(text=("Error: %s is not a float number" % self.prob[i][0]))
				return False
			if v < 0: 
				self.errorLabel.config(text=("Error: %s must be positive" % self.prob[i][0]))
				return False
			psum += v
		if psum != 1:
			self.errorLabel.config(text="Probabilities summation must be 1")
			return False
		
		#check discount factor
		try:
			v = float(self.discFactor.get())
		except ValueError:
			self.errorLabel.config(text="Error: Discount Factor is not a float number")
			return False
		if v < 0 or v > 1: 
			self.errorLabel.config(text="Error: Discount Factor must be a value between 0 and 1")
			return False
		
		return True
			
	def openMDPGUI(self):
		global w, g
		if self.checkSettingValues():
			self.master.destroy()
			
			df = float(self.discFactor.get())
			rews = list(map(lambda x: float(x.get()), self.rewValue))
			probs = list(map(lambda x: float(x.get()), self.probValue))
			
			w = self.world
			w.setDiscountFactor(df)
			w.setRewards(rews[0], rews[1], rews[2])
			w.setProbabilities(probs[0], probs[1], probs[2], probs[3])
			w.setAlgorithmRestrictions(float(self.algorithm_restValue[0].get()), float(self.algorithm_restValue[1].get()))
			
			g = MDPGUI(w)
			
		
	def __init__(self, world):
		self.world = world
		self.master = Tk()
		self.master.title("MDP Settings")
		self.master.resizable(0,0)
		
		label = Label(self.master, text="Rewards", bg="gray")
		label.pack(side=TOP, pady=10)
		
		for labelText, defaultValue, valueSign in self.rew:
			frame = Frame(self.master)
			label = Label(frame, text=("%s (%s): " % (labelText, valueSign)))
			label.pack(side=LEFT)
			value = StringVar()
			value.set(defaultValue)
			self.rewValue.append(value)
			entry = Entry(frame, textvariable=value, width=5)
			entry.pack(side=LEFT)
			frame.pack(side=TOP, padx=10, pady=5)
		
		label = Label(self.master, text="Probabilities", bg="gray")
		label.pack(side=TOP, pady=10)
		
		for labelText, defaultValue in self.prob:
			frame = Frame(self.master)
			label = Label(frame, text=("%s: " % labelText))
			label.pack(side=LEFT)
			value = StringVar()
			value.set(defaultValue)
			self.probValue.append(value)
			entry = Entry(frame, textvariable=value, width=5)
			entry.pack(side=LEFT)
			frame.pack(side=TOP, padx=10, pady=5)
			
		label = Label(self.master, text="Other rewards", bg="gray")
		label.pack(side=TOP, pady=10)
		
		frame = Frame(self.master)
		label = Label(frame, text="Discount Factor: ")
		label.pack(side=LEFT)
		self.discFactor = StringVar()
		self.discFactor.set("1")
		entry = Entry(frame, textvariable=self.discFactor, width=5)
		entry.pack(side=LEFT)
		frame.pack(side=TOP, padx=10, pady=5)

		label = Label(self.master, text="Algorithms' restrictions", bg="gray")
		label.pack(side=TOP, pady=10)

		for labelText, defaultValue in self.algorithm_rest:
			frame = Frame(self.master)
			label = Label(frame, text=("%s: " % labelText))
			label.pack(side=LEFT)
			value = StringVar()
			value.set(defaultValue)
			self.algorithm_restValue.append(value)
			entry = Entry(frame, textvariable=value, width=5)
			entry.pack(side=LEFT)
			frame.pack(side=TOP, padx=10, pady=5)
	
		bOpenMDPGUI = Button(self.master, text="Show MDP", command=self.openMDPGUI)
		bOpenMDPGUI.pack(padx=10, pady=20)
		
		self.errorLabel = Label(self.master, text="")
		self.errorLabel.pack(side=TOP, padx=5, pady=10)