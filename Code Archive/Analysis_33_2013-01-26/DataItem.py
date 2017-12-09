# Data Item
#
# Last Modified: 2012-01-13-18-14
#
# A class for containing information intended to be displayed on screen.
#

class DataItem:

	def __init__(self):
	
		self.Reference = ""
		self.Content = ""
		
		self.Items = []
		
	def ToDisplay(self):
		
		print self.Reference, ": ", self.Content
		
		for Item1 in self.Items:
			Item1.ToDisplay;
		
