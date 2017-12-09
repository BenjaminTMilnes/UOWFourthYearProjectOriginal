class SelectionStatistics:
	
	def __init__(self):
		
		self.EventsRemaining = 0
		self.AbsoluteEfficiency = -1
		self.RelativeEfficiency = -1
		
		self.Purity = -1
		self.PionPurity = -1
		self.RPPurity = -1
		self.QSPurity = -1
		self.ESPurity = -1
		self.DISPurity = -1
		self.CSPurity = -1
		self.OtherPurity = -1
		
		self.TruthDelta = 0
		self.ReconstructedDelta = 0
		self.OtherRPInteraction = 0
		self.QSInteraction = 0
		self.ESInteraction = 0
		self.DISInteraction = 0
		self.CSInteraction = 0
		self.OtherInteraction = 0
