import EventCodeElement
import re
class EventCodeDeconstructor:
	
	def __init__(self):
		
		self.EventCode = ""
		self.Elements = []
		
	def ReadCode(self, Code):
		
		self.EventCode = Code
				
		TextElements = Code.split(";")
		
		for i in TextElements:
			
			Text1 = i.split(":")
			
			Element1 = EventCodeElement.EventCodeElement()
			if (len(Text1) == 2):
				if (Text1[0] != "") and (Text1[0] != ""):
					Element1.Reference = self.GetCorrectReference(Text1[0])
					Element1.Content = self.GetCorrectContent(Text1[1])
					self.Elements.append(Element1)
			
	def WriteCode(self):
		
		Text = ""
		
		for Element1 in self.Elements:
			Text += Element1.WriteClearly()
		
		return Text
		
	def GetCorrectReference(self, IncorrectReference):
		
		CorrectReference = ""
		
		if IncorrectReference == "nu":
			CorrectReference = "Neutrino"
		elif IncorrectReference == "tgt":
			CorrectReference = "Nucleus"
		elif IncorrectReference == "N":
			CorrectReference = "Nucleon"
		elif IncorrectReference == "proc":
			CorrectReference = "Process"
		else:
			CorrectReference = IncorrectReference
		
		return CorrectReference
		
	def GetCorrectContent(self, IncorrectContent):
		
		CorrectContent = ""
		
		if IncorrectContent == "Weak[CC],QES":
			CorrectContent = "Weak Interaction, Charged-Current Quasielastic Scattering"
		elif IncorrectContent == "Weak[CC],RES":
			CorrectContent = "Weak Interaction, Charged-Current Resonant Elastic Scattering"
		elif IncorrectContent == "Weak[CC],DIS":
			CorrectContent = "Weak Interaction, Charged-Current Deep Inelastic Scattering"
		elif IncorrectContent == "Weak[NC],QES":
			CorrectContent = "Weak Interaction, Neutral-Current Quasielastic Scattering"
		elif IncorrectContent == "Weak[NC],RES":
			CorrectContent = "Weak Interaction, Neutral-Current Resonant Elastic Scattering"
		elif IncorrectContent == "Weak[NC],DIS":
			CorrectContent = "Weak Interaction, Neutral-Current Deep Inelastic Scattering"
		else:
			CorrectContent = IncorrectContent
		
		return CorrectContent
		
	
