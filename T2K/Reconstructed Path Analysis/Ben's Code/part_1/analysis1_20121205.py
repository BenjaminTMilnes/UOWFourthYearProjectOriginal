import libraries
import glob
import sys
import ROOT
import RooTrackerTools
import ParticleCodes
import math


class Analysis:
	
		
	def __init__(self, IntputFileNameList, OutputFileName):
		self.IntputFileNameList = IntputFileNameList
		self.OutputFileName = OutputFileName
		self.Histograms = {}
		self.Modules = []
		self.BasicHeader = self.LoadModule("HeaderDir/BasicHeader")
		self.GRTVertex = self.LoadModule("TruthDir/GRooTrackerVtx")
		self.Truth_Vertices = self.LoadModule("TruthDir/Vertices")
		self.Reconstructed_Global = self.LoadModule("ReconDir/Global")
		self.Rootools = RooTrackerTools.RooTrackerTools()


	def NewHistogram1D(self, Reference, Title, XAxisTitle, YAxisTitle, NumberOfBinsX, MinimumX, MaximumX):
		self.Histograms[Reference] = ROOT.TH1D(Reference, Title, NumberOfBinsX, MinimumX, MaximumX)
		self.Histograms[Reference].SetXTitle(XAxisTitle)
		self.Histograms[Reference].SetYTitle(YAxisTitle)

	
	def NewHistogram2D(self, Reference, Title, XAxisTitle, YAxisTitle, NumberOfBinsX, MinimumX, MaximumX, NumberOfBinsY, MinimumY, MaximumY):
		self.Histograms[Reference] = ROOT.TH2D(Reference, Title, NumberOfBinsX, MinimumX, MaximumX, NumberOfBinsY, MinimumY, MaximumY)
		self.Histograms[Reference].SetXTitle(XAxisTitle)
		self.Histograms[Reference].SetYTitle(YAxisTitle)

	
	def NewHistogram3D(self, Reference, Title, XAxisTitle, YAxisTitle, ZAxisTitle, NumberOfBinsX, MinimumX, MaximumX, NumberOfBinsY, MinimumY, MaximumY, NumberOfBinsZ, MinimumZ, MaximumZ):
		self.Histograms[Reference] = ROOT.TH3D(Reference, Title, NumberOfBinsX, MinimumX, MaximumX, NumberOfBinsY, MinimumY, MaximumY, NumberOfBinsZ, MinimumZ, MaximumZ)
		self.Histograms[Reference].SetXTitle(XAxisTitle)
		self.Histograms[Reference].SetYTitle(YAxisTitle)
		self.Histograms[Reference].SetZTitle(ZAxisTitle)

	
	def afterLoop(self):
		
		# Saves histograms to the output file and prints out any summary information
		
		self.output_file.cd()
		for Histogram in self.Histograms.itervalues():
			Histogram.Write()
	
	
	def LoadInputFiles(self):
		# Adds each file in the list of input file names to each module we want to use
		for filename in self.IntputFileNameList:
			for Module in self.Modules:
				Module.Add(filename)
	
	
	def LoadModule(self, module_name):
		# Load all the appropriate modules from the oaAnalysis file that we have defined
		Module = ROOT.TChain(module_name)
		self.Modules.append(Module)
		return Module
	
	
	def LoadOutputFile(self):
		self.output_file = ROOT.TFile(self.OutputFileName, "RECREATE")
	
	
	def run(self, n = 999999999):
		
		self.LoadInputFiles()
		self.LoadOutputFile()
		
		NPID = self.Reconstructed_Global.NPIDs
		
		for i in xrange(NPID):
			PID = self.Reconstructed_Global.PID[i]
			print PID
				
		#n = min(n, self.BasicHeaders.GetEntries())
		#print "Reading ", n, " events."
		
		#for i in range(n):
		#	for Module in self.Modules:
		#		Module.GetEntry(i)
		#	self.runEvent()
			
		#self.afterLoop()
	
		
	
	def runEvent(self):
		
		print "asd" #"EVENT NUMBER ", self.BasicHeader.EventID
				
		#for i, Vertex1 in enumerate(self.GRTVertex.Vtx):
			
		#	print "VERTEX NUMBER ", i


InputFileName = "/storage/physics/phujbk/4_reconstructed_path_analysis/part_1/production5_analysis_n.list"
OutputFileName = "output1_20121205.root"

def main():
	
	IsCorrectNumberOfCommands = False
	
	if ( len(sys.argv) != 2 ):
		
		IsCorrectNumberOfCommands = False
		print "Type something like this: python analysis.py 10"
		
	else:
		
		IsCorrectNumberOfCommands = True
	
	
	if IsCorrectNumberOfCommands == True:
			
		libraries.load("nd280/nd280.so")
		
		#InputFileNameList = ( glob.glob( InputFileName + "*" ) )
		
		#FileList = open(InputFileName)
		
		#InputFileNameList = FileList.read().splitlines()
		InputFileNameList = []
				
		Analysis1 = Analysis(InputFileNameList, OutputFileName)
		Analysis1.run(int(sys.argv[1]))
	

if __name__ == "__main__":
	main()
