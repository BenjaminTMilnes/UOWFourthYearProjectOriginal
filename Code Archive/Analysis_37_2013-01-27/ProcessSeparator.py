def EventProcess(DeltaPGamma, DeltaPPi, InteractionType):
				
		if(DeltaPGamma):
			Key = "DeltaPGamma"
			
		elif(DeltaPPi):
			Key = "DeltaPPi"
			
		elif(InteractionType == "RP" and not DeltaPGamma and not DeltaPPi):
			Key = "OtherResonance"
			
		elif (InteractionType == "QS"):
			Key = "QS"
			
		elif (InteractionType == "ES"):
			Key = "ES"
			
		elif (InteractionType == "DIS"):
			Key = "DIS"
			
		elif (InteractionType == "C"):
			Key = "C"
			
		return Key

ProcessList = ["DeltaPGamma", "DeltaPPi", "OtherResonance", "QS", "ES", "DIS", "C"]

ProcessDictionary = dict((ProcessKey1,0) for ProcessKey1 in ProcessList)

ProcessDictionary["DeltaPGamma"] = "Delta -> p gamma Interactions"
ProcessDictionary["DeltaPPi"] = "Delta -> p pi0 Interactions"
ProcessDictionary["OtherResonance"] = "Other Resonances"
ProcessDictionary["QS"] = "Quasi-Elastic Scattering"
ProcessDictionary["ES"] = "Elastic Scattering"
ProcessDictionary["DIS"] = "Deep Inelastic Scattering"
ProcessDictionary["C"] = "Coherent Scattering"
ProcessDictionary["Other"] = "Other Interactions"
