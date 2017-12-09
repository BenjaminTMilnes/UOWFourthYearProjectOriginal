# Command Line
#
# This class takes command line arguments, which are separated by spaces, and deconstructs them to link a command to an option or quantity.
#
# Modified 2013.01.27 09:15
#

class Deconstructor:
		
	def __init__(This, Arguments):
		
		This.Arguments = Arguments
		This.Commands = {}
		
		if (len(Arguments) > 1):
			for i in range(len(Arguments)):
				if (i > 0):
				
					ArgumentText = str(Arguments[i])
					
					ArgumentComponents = ArgumentText.split(":")
					
					if (len(ArgumentComponents) == 2):						
						This.Commands[ArgumentComponents[0]] = ArgumentComponents[1]
														
					elif (len(ArgumentComponents) == 1):				
						This.Commands[ArgumentComponents[0]] = ArgumentComponents[0]
					
					
	def Command(This, Key):
		
		return This.Commands[Key]
		
