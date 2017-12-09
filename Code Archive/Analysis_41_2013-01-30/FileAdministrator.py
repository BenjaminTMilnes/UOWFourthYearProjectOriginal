# File Administrator
#

import os
import datetime
import time

import TextConstants

Now = datetime.datetime.now()

def CreateDTLocator(): 
	# Creates file and folder locators based on the date and time (DT).

	FolderDTLocator = Now.strftime("%Y/%m/%d/")
	FileDTLocator = Now.strftime("%Y-%m-%d-%H-%M-%S")
	
	return FolderDTLocator, FileDTLocator
	

def CreateFilePath(ApplicationFolder, CollectionFolder, Extension):
	# Creates the folders necessary for a date-time file path and then returns the complete path.	
	
	(FolderDTLocator, FileDTLocator) = CreateDTLocator()
		
	FolderLocator = ApplicationFolder + FolderDTLocator + CollectionFolder
	
	if (not os.path.exists(FolderLocator)):
		os.makedirs(FolderLocator)
		
	FileLocator = FolderLocator + FileDTLocator + Extension
	
	return FileLocator
		
	
def CreateLocatorsListFile(ApplicationFolder, Locators1):
		
	CreateNewFile = False
		
	(FolderDTLocator, FileDTLocator) = CreateDTLocator()
		
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
	
		FilePath1 = CreateFilePath(ApplicationFolder, "Input List/", ".list") # For archiving the .list file used
	
		File1 = open(FilePath1,"w")

		for ListItem1 in Locators1:
			File1.write(str(ListItem1) + TextConstants.NewLine)
