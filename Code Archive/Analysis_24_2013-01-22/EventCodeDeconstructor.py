# Event Code Deconstructor
#
# This class reads through an event code character sequence, and separates it out into the various properties, so that they can be accessed programmaticaly.
#
# Modified 2013.01.13 19:50
# Last Modified 2013.01.13 22:15
#

import EventCodeElement
import re

class EventCodeDeconstructor:
	
	def __init__(self):
		
		self.EventCode = "" # The full event code character sequence, which is retained in case it is not properly deconstructed.
		self.Elements = [] # An array of the invidiual properties and their values, populated by EventCodeElement.
		
	def ReadCode(self, Code):
		
		self.EventCode = str(Code)
		self.Elements = []
				
		TextElements = self.EventCode.split(";") # The event code properties seem to be consistently separated by a semi-colon, therefore this is the first splitting.
		
		for i in TextElements:
			
			Text1 = i.split(":") # The property and its value seem to be consistently separated by a colon, therefore for each property sequence, we split it at the colon.
			
			Element1 = EventCodeElement.EventCodeElement()
			if (len(Text1) == 2): # In the event that there was more than one colon, something has gone wrong, so ignore this property.
				if (Text1[0] != "") and (Text1[1] != ""): # If either the property name or value was missing, don't record this property.
					Element1.Reference = self.GetCorrectReference(Text1[0])
					Element1.Content = self.GetCorrectContent(Text1[1])
					self.Elements.append(Element1)
					
					if (Text1[0] == "proc"): # If there is a process property, then add in another element to provide a shorthand code for the process.
						
						Element2 = EventCodeElement.EventCodeElement()
						Element2.Reference = "Interaction Code"
						
						Element3 = EventCodeElement.EventCodeElement()
						Element3.Reference = "Current Code"
						
						Element4 = EventCodeElement.EventCodeElement()
						Element4.Reference = "Process Code"
						
						if (Text1[1] == "Weak[CC],QES"):
							Element2.Content = "W-CC-QS"
							Element3.Content = "CC"
							Element4.Content = "QS"
						elif (Text1[1] == "Weak[CC],RES"):
							Element2.Content = "W-CC-RP"
							Element3.Content = "CC"
							Element4.Content = "RP"
						elif (Text1[1] == "Weak[CC],DIS"):
							Element2.Content = "W-CC-DIS"
							Element3.Content = "CC"
							Element4.Content = "DIS"
						elif (Text1[1] == "Weak[CC],COH"):
							Element2.Content = "W-CC-C"
							Element3.Content = "CC"
							Element4.Content = "C"
						elif (Text1[1] == "Weak[NC],QES"):
							Element2.Content = "W-NC-ES"
							Element3.Content = "NC"
							Element4.Content = "ES"
						elif (Text1[1] == "Weak[NC],RES"):
							Element2.Content = "W-NC-RP"
							Element3.Content = "NC"
							Element4.Content = "RP"
						elif (Text1[1] == "Weak[NC],DIS"):
							Element2.Content = "W-NC-DIS"
							Element3.Content = "NC"
							Element4.Content = "DIS"
						elif (Text1[1] == "Weak[NC],COH"):
							Element2.Content = "W-NC-C"
							Element3.Content = "NC"
							Element4.Content = "C"
							
						self.Elements.append(Element2)	
						self.Elements.append(Element3)	
						self.Elements.append(Element4)	
			
	def WriteCode(self):
		
		Text = ""
		
		for Element1 in self.Elements: # Go through each of the elements and write it clearly.
			Text += Element1.WriteClearly()
		
		return Text
		
	def WriteProcessCode(self):
		
		Text = ""
		
		for Element1 in self.Elements:
			if (Element1.Reference == "Process Code"): # Get just the process code.
				Text += Element1.WriteClearly()
		
		return Text
		
	def GetCorrectReference(self, IncorrectReference): # Correct the property references to make them more readable.
		
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
			CorrectReference = IncorrectReference # In the event that a particular property reference is not recognised, don't change it.
		
		return CorrectReference
		
	def GetCorrectContent(self, IncorrectContent): # Correct the property contents to make them more readable.
		
		CorrectContent = ""
		
		if IncorrectContent == "Weak[CC],QES":
			CorrectContent = "Weak Interaction, Charged-Current (CC) Quasielastic Scattering (QS)"
		elif IncorrectContent == "Weak[CC],RES":
			CorrectContent = "Weak Interaction, Charged-Current (CC) Resonance Production (RP)"
		elif IncorrectContent == "Weak[CC],DIS":
			CorrectContent = "Weak Interaction, Charged-Current (CC) Deep Inelastic Scattering (DIS)"
		elif IncorrectContent == "Weak[NC],QES":
			CorrectContent = "Weak Interaction, Neutral-Current (NC) Elastic Scattering (ES)"
		elif IncorrectContent == "Weak[NC],RES":
			CorrectContent = "Weak Interaction, Neutral-Current (NC) Resonance Production (RP)"
		elif IncorrectContent == "Weak[NC],DIS":
			CorrectContent = "Weak Interaction, Neutral-Current (NC) Deep Inelastic Scattering (DIS)"
		else:
			CorrectContent = IncorrectContent # In the event that a particular property content is not recognised, don't change it.
		
		return CorrectContent
		
	
