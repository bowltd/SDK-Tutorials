import curses

class DisplayInfo:
	def __init__(self, name, valueMin, valueMax, value):
		self.Name = name
		self.ValueMin = valueMin
		self.ValueMax = valueMax
		self.ValueMin = valueMin
		self.SetValue(value)
		self.SetName(10)

	def SetValue(self,v):
		self.Value = v
		if self.Value<self.ValueMin:
			self.Value = self.ValueMin
		if self.Value>self.ValueMax:
			self.Value = self.ValueMax

	def SetName(self,length):
		self.NameChar = self.Name[:length]

	def GetValue(self,length):
		return str(self.Value)[:length]

	def GetBar(self,length):
		prop = (self.Value - self.ValueMin) / (self.ValueMax - self.ValueMin)
		j = round(prop * (length-1))
		s = '|'
		for i in range(length):
			if i==j:
				s+='!'
			else:
				s+="."
		return s+'|'

class Display:

	def __init__(self):
		self.list = []
		self.mainwin = curses.initscr()
		self.height = 15
		self.width = 50
		self.listStart = 4
		self.listIndex = 0
		self.listFlankers = 3
		self.increment = 0.05
		curses.noecho()
		self.content = curses.newwin(self.height,self.width,1,5)
		self.mainwin.keypad(True)
		self.Update()

	# update the ncurses display
	def Update(self):
		self.content.clear()
		self.content.addstr(2,2,"Joints:")
		
		org = self.listIndex - self.listFlankers
		if org<0:
			org = 0
		end = org + 2*self.listFlankers + 1
		if end >= len(self.list):
			end = len(self.list)
		org = end - 2*self.listFlankers-1
		if org<0:
			org = 0
		j=self.listStart

		for i in range(org,end):
			if i==self.listIndex:
				self.content.addstr(j,2,"*")

			self.content.addstr(j,5,self.list[i].NameChar)
			self.content.addstr(j,20,self.list[i].GetBar(11))
			self.content.addstr(j,40,self.list[i].GetValue(6))
			j+=1
		
		self.content.box(0,0)
		self.content.addstr(0,2," BOW Tutorial ")
		self.content.addstr(self.height-1,2," use arrow keys, or 'q' to quit ")
		self.content.refresh()
	
	# main loop handling key presses
	def Run(self):
		self.Update()
		while True:
			c = self.mainwin.getch()
			ch = chr(c)
			if ch == 'q':
				raise SystemExit
			elif c == curses.KEY_DOWN:
				if self.listIndex<len(self.list)-1:
					self.listIndex +=1		
			elif c == curses.KEY_UP:
				if self.listIndex>0:
					self.listIndex-=1
			elif c == curses.KEY_LEFT:
				self.list[self.listIndex].SetValue(self.list[self.listIndex].Value - self.increment)
				self.SetCurrentJoint()
			elif c == curses.KEY_RIGHT:
				self.list[self.listIndex].SetValue(self.list[self.listIndex].Value + self.increment)
				self.SetCurrentJoint()
			self.Update()

	# should be overwritten by derived class
	def SetCurrentJoint(self):
		pass
	
	def __del__(self):
		curses.nocbreak() 
		curses.echo()
		self.mainwin.keypad(False)
		self.mainwin.refresh()
		curses.endwin()