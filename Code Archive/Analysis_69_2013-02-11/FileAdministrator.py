# File Administrator
#

import os
import datetime
import time

import TextConstants

Now = datetime.datetime.now()

def CreateDTLocator(SimulationInformation): 
	# Creates file and folder locators based on the date and time (DT).

	Identifier = CreateSimulationIdentifier(SimulationInformation)

	FolderDTLocator = Now.strftime("%Y/%m/%d/%H-%M-%S") + Identifier + "/"
	FileDTLocator = Now.strftime("%Y-%m-%d-%H-%M-%S") + Identifier
	
	return FolderDTLocator, FileDTLocator

def CreateSimulationIdentifier(SimulationInformation):
	
	Identifier = ""
	ValueIdentifier = []
	FlagIdentifier = []
	
	for Parameter in SimulationInformation.itervalues():
		if (len(Parameter) > 0):
			
			Description = Parameter[0]
			
			if (":" in Parameter[0]):
				
				ValueIdentifier.append(Parameter[1])
				
			else:
				
				FlagIdentifier.append(Parameter[1])
				
	ValueIdentifier.sort()
	FlagIdentifier.sort()
	
	for Value in ValueIdentifier:
		Identifier += "_" + Value
		
	for Flag in FlagIdentifier:
		Identifier += "_" + Flag
		
	return Identifier
	

def CreateFilePath(ApplicationFolder, Extension, SimulationInformation):
	# Creates the folders necessary for a date-time file path and then returns the complete path.	
	
	(FolderDTLocator, FileDTLocator) = CreateDTLocator(SimulationInformation)
	
	
	
	FolderLocator = ApplicationFolder + FolderDTLocator
	
	if (not os.path.exists(FolderLocator)):
		os.makedirs(FolderLocator)
		
	FileLocator = FolderLocator + FileDTLocator + Extension
	
	return FileLocator
		
	
def CreateLocatorsListFile(ApplicationFolder, Locators1):
		
	CreateNewFile = False
		
	(FolderDTLocator, FileDTLocator) = CreateDTLocator(SimulationInformation)
		
	Folder1 = ApplicationFolder + FolderDTLocator + "Input List/"

	try:
		ExistingFiles = os.listdir(Folder1)
		NumberOfExistingFiles = len(ExistingFiles)
	except:
		NumberOfExistingFiles = 0

	if (NumberOfExistingFiles > 0):
		
		LastFile = open(Folder1 + ExistingFiles[NumberOfExistingFiles - 1])		
		LastFile_Locators = LastFile.read().splitlines()			
		LastFile.close()
	
		if (LastFile_Locators != Locators1):			
			CreateNewFile = True
	
	else:		
		CreateNewFile = True
	
	if (CreateNewFile == True):
	
		FilePath1 = CreateFilePath(ApplicationFolder, ".list") # For archiving the .list file used
	
		File1 = open(FilePath1,"w")

		for ListItem1 in Locators1:
			File1.write(str(ListItem1) + TextConstants.NewLine)
