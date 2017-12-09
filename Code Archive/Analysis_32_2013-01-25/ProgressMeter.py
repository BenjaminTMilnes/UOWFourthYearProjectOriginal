# Progress Meter
#
# Modified 2013.01.16 22:50
# Last Modified 2013.01.16 23:16
#

import math

class ProgressMeter:
	
	def __init__(self, EndCount):
		
		self.Count = 0
		self.EndCount = EndCount
	
	def Update(self, Count):
		
		self.Count = Count
		
		if (self.Count < self.EndCount):
			
			Progress1 = int(math.floor(100 * float(self.Count) / float(self.EndCount)))
			Progress2 = int(math.floor(100 * float(self.Count + 1) / float(self.EndCount)))
			
			if (Progress2 > Progress1):
			
				print str(Progress1), "%"	
		
		elif (self.Count == self.EndCount):
			
			print "100%"				
			print "Complete"				
				
