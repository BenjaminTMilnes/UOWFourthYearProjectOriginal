# ROOT File
#
# Last Modified: 2013.01.13 20:21
#
# This is a container class for ROOT histograms, graphs, charts, and other objects.
#

import ROOT 
ROOT.gROOT.SetBatch(True)

class ROOTFile:
		
	def __init__(self, FileLocator):
				
		self.FileLocator = FileLocator
		
		self.HistogramDictionary = {}
	
	
	def Open(self):		
	
		self.File = ROOT.TFile(self.FileLocator, "RECREATE")
		
			
	def Close(self):		

		self.File.cd()

		TrueDirectoryList=[]#For the list of true directories created

		for Histogram1 in self.HistogramDictionary.itervalues():
			
			DirectoryList=Histogram1.HistogramDirectory.split("/")#Folders in form: ROOTFILE/folder1/folder 2/
			
			ParentDirectory=self.File.CurrentDirectory()

			TrueDirectoryString=""#True directory is for the possibility that the created directory is not equal to the input string

			for SubDirectory in DirectoryList:#Looping over the subfolders of a file path and creates the folders
				
				Directory=ParentDirectory.GetDirectory(SubDirectory)#First try to get the directory

				if (Directory == None):
						
					Directory=ParentDirectory.mkdir(SubDirectory)#Makes the directory if it does not exist
				
				if (Directory != None):
						
					ParentDirectory=Directory
					
					if(SubDirectory != ""):#Input string can contain /// or // etc, any number of consecutive /'s constitute the folder delimiter
						TrueDirectoryString+=SubDirectory+"/"
					
			TrueDirectoryList.append(TrueDirectoryString)

		for i, Histogram1 in enumerate(self.HistogramDictionary.itervalues()):
			
			HistogramDirectory=self.File.GetDirectory(TrueDirectoryList[i])
			
			if(HistogramDirectory != None):
				HistogramDirectory.cd()
				
			else:#If the indended folder cannot be found, the file is printed to the root folder
				self.File.cd()
			
			Histogram1.Histogram.Write()
			
		self.File.Close
			
						
	def NewHistogram1D(self, Reference, Title, XAxisTitle, YAxisTitle, NumberOfBinsX, MinimumX, MaximumX, Directory):
		
		HistogramObject=HistogramStorage()
		HistogramObject.Histogram = ROOT.TH1D(Reference, Title, NumberOfBinsX, MinimumX, MaximumX)
		HistogramObject.Histogram.SetXTitle(XAxisTitle)
		HistogramObject.Histogram.SetYTitle(YAxisTitle)
		HistogramObject.HistogramDirectory = Directory
		
		self.HistogramDictionary[Reference]=HistogramObject
	
	
	def NewHistogram2D(self, Reference, Title, XAxisTitle, YAxisTitle, NumberOfBinsX, MinimumX, MaximumX, NumberOfBinsY, MinimumY, MaximumY, Directory):
		
		HistogramObject=HistogramStorage()
		HistogramObject.Histogram = ROOT.TH2D(Reference, Title, NumberOfBinsX, MinimumX, MaximumX, NumberOfBinsY, MinimumY, MaximumY)
		HistogramObject.Histogram.SetXTitle(XAxisTitle)
		HistogramObject.Histogram.SetYTitle(YAxisTitle)
		HistogramObject.HistogramDirectory = Directory
	
		self.HistogramDictionary[Reference]=HistogramObject
	
	def NewHistogram3D(self, Reference, Title, XAxisTitle, YAxisTitle, ZAxisTitle, NumberOfBinsX, MinimumX, MaximumX, NumberOfBinsY, MinimumY, MaximumY, NumberOfBinsZ, MinimumZ, MaximumZ, Directory):
		
		HistogramObject=HistogramStorage()
		HistogramObject.Histogram = ROOT.TH3D(Reference, Title, NumberOfBinsX, MinimumX, MaximumX, NumberOfBinsY, MinimumY, MaximumY, NumberOfBinsZ, MinimumZ, MaximumZ)
		HistogramObject.Histogram.SetXTitle(XAxisTitle)
		HistogramObject.Histogram.SetYTitle(YAxisTitle)
		HistogramObject.Histogram.SetZTitle(ZAxisTitle)
		HistogramObject.HistogramDirectory = Directory
		
		self.HistogramDictionary[Reference]=HistogramObject
					
	def NewStackedHistogramCanvas(self, Reference, Canvas, Directory):
		
		HistogramObject=HistogramStorage()
		HistogramObject.Histogram = Canvas
		HistogramObject.HistogramDirectory = Directory
		
		self.HistogramDictionary[Reference]=HistogramObject
		

class HistogramStorage:
	
	def __init__(self):
		
		self.Histogram=""
		self.HistogramDirectory=""
		self.LegendLabel=""
