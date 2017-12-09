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
		NewCount = False
		
		if (self.Count < self.EndCount):
			
			Progress1 = int(math.floor(100 * float(self.Count) / float(self.EndCount)))
			Progress2 = int(math.floor(100 * float(self.Count + 1) / float(self.EndCount)))
			
			if (Progress2 > Progress1):
			
				NewCount = True

				print str(Progress1), "%"

		elif (self.Count == self.EndCount):
			
			NewCount = True
			
			print "100%"				
			print "Complete"
			
		return NewCount
