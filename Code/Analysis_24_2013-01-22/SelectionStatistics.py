class SelectionStatistics:
	
	def __init__(self):
		
		self.EventsRemaining = 0
		self.AbsoluteEfficiency = -1
		self.RelativeEfficiency = -1
		self.Purity = -1
		
		self.TruthDelta = 0
		self.ReconstructedDelta = 0
		self.OtherRPInteraction = 0
		self.QSInteraction = 0
		self.DISInteraction = 0
		self.CSInteraction = 0
