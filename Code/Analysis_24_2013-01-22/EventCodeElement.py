# Event Code Element
#
# This is a container class for sections of an event code, used by the Event Code Deconstructor.
#
# Last Modified 2013.01.13 19:50
#

class EventCodeElement:
	
	def __init__(self):
		self.Reference = ""
		self.Content = ""
		
	def Write(self): # Write in the normal way.
		Text = self.Reference + ":" + self.Content + ";"
		return Text
		
	def WriteClearly(self): # Write in a way which is easily readable.
		Text = self.Reference + ": " + self.Content + ". "
		return Text
		
