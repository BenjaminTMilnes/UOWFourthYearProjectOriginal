# Statistic
#
# This is a container class for simple statistical data.
#
# Last Modified 2013.01.13 21:07
#

class Statistic:
	
	def __init__(self, Title = "", Quantity = 0):
		
		self.Title = Title
		self.Quantity = Quantity
		
	def ToText(self):
		
		Text = self.Title + ": " + str(self.Quantity) + "."
		
		return Text
	
	 
