
class Selector:
	
	def __init__(This, FileLocator = ""):
		
		This.FileLocator = FileLocator
		This.FileIdentifiers = []

		if (This.FileLocator != ""):

			File1 = open(This.FileLocator, "r")

			Text1 = File1.read()
			
			Text2 = Text1.split("\n")

			for Text3 in Text2:
				
				Text4 = Text3.split(" ")
				
				if (len(Text4) >= 4):
					
					FileIdentifier1 = FileIdentifier()
					
					FileIdentifier1.Group = Text4[1]
					FileIdentifier1.Subgroup = Text4[2]
					
					This.FileIdentifiers.append(FileIdentifier1)
						
	def ToText(This):
		
		Response = ""
		
		for FileIdentifier1 in This.FileIdentifiers:
			Response += FileIdentifier1.ToText() + "\n"
		
		return Response

class FileIdentifier:
	
	def __init__(This, Group = None, Subgroup = None):
		
		This.Group = Group
		This.Subgroup = Subgroup
	
	def ToText(This, WithTitles = False):
		
		Response = ""
		
		if (WithTitles == True):
			Response = "Group: " + str(This.Group) + " Subgroup:" + str(This.Subgroup)
		else:
			Response = str(This.Group) + ", " + str(This.Subgroup)
		
		return Response


Selector1 = Selector("test.txt")

print Selector1.ToText()
