
class EventCodeElement:
	
	def __init__(self):
		self.Reference = ""
		self.Content = ""
		
	def Write(self):
		Text = self.Reference + ":" + self.Content + ";"
		return Text
		
	def WriteClearly(self):
		Text = self.Reference + ": " + self.Content + ". "
		return Text
		
