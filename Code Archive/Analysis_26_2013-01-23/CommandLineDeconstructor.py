class CommandLineDeconstructor:
	
	
	def __init__(self, Arguments):
		
		self.Arguments = Arguments
		self.Commands = {}
		
		if (len(Arguments) > 1):
			for i in range(len(Arguments)):
				if (i > 0):
				
					ArgumentText = str(Arguments[i])
					
					ArgumentComponents = ArgumentText.split(":")
					
					if (len(ArgumentComponents) == 2):						
						self.Commands[ArgumentComponents[0]] = ArgumentComponents[1]
														
					elif (len(ArgumentComponents) == 1):				
						self.Commands[ArgumentComponents[0]] = ArgumentComponents[0]
					
					
	def Command(self, Key):
		
		return self.Commands[Key]
		
