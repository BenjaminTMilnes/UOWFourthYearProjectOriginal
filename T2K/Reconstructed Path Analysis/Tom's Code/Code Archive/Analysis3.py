import libraries
import glob
import sys
import ROOT
import RooTrackerTools



class Analysis:
	
	
	def __init__(self, input_filename_list, output_filename):
		self.input_filename_list = input_filename_list
		self.output_filename = output_filename
		self.histograms = {}
		self.modules = []
		# Load the modules needed in this analysis
		self.basic_header = self.loadModule("HeaderDir/BasicHeader")
		self.genievtx = self.loadModule("TruthDir/GRooTrackerVtx")
		# Declare GRooTrackerTools class instance
		self.Rootools = RooTrackerTools.RooTrackerTools()
		self.ReconDir_Global = self.loadModule("ReconDir/Global")
		self.TruthDir_Vertices = self.loadModule("TruthDir/Vertices")
	
	
	def beforeLoop(self):
		"""Opens input and output files, creates histograms and intitialises any other necessary variables"""
		self.loadInputFiles()
		self.loadOutputFile()
		self.addHistogram3D("XYZ_Position", "Position of CCQE interaction in FGDs", 100, -850, 850, 100, -800, 900, 100, 100, 2000)#Histogram of CCQE neutrino interaction location
		self.addHistogram1D("Neutrino_Momentum", "Momentum of the interacting neutrino(GeV/c)",100,0,10)#Histogram of interacting neutrino momentum
	
	def addHistogram1D(self, name, title, n_bins, minimum, maximum):
		""" Add a 1D histogram to the histogram list """
		self.histograms[ name ] = ROOT.TH1F(name, title, n_bins, minimum, maximum)
	
	
	def addHistogram2D(self, name, title, n_bins_x, minimum_x, maximum_x, n_bins_y, minimum_y, maximum_y):
		""" Add a 1D histogram to the histogram list """
		self.histograms[ name ] = ROOT.TH2F(name, title, n_bins_x, minimum_x, maximum_x, n_bins_y, minimum_y, maximum_y)
		
	def addHistogram3D(self, name, title, n_bins_x, minimum_x, maximum_x, n_bins_y, minimum_y, maximum_y, n_bins_z, minimum_z, maximum_z):
		""" Add a 1D histogram to the histogram list """
		self.histograms[ name ] = ROOT.TH3F(name, title, n_bins_x, minimum_x, maximum_x, n_bins_y, minimum_y, maximum_y, n_bins_z, minimum_z, maximum_z)
	
	
	def afterLoop(self):
		"""Saves histograms to the output file and prints out any summary information"""
		self.output_file.cd()
		for histogram in self.histograms.itervalues():
			histogram.Write()
	
	
	def loadInputFiles(self):
		"""Adds each file in the list of input file names to each module we want to use"""
		for filename in self.input_filename_list:
			for module in self.modules:
				module.Add(filename)
	
	
	def loadModule(self, module_name):
		"""Load all the appropriate modules from the oaAnalysis file that we have defined"""
		module = ROOT.TChain(module_name)
		self.modules.append(module)
		return module
	
	
	def loadOutputFile(self):
		self.output_file = ROOT.TFile(self.output_filename, "RECREATE")
	
	
	def run(self, n = 999999999):
		"""What the user should call when they're ready to run"""
		self.beforeLoop()
		self.runLoop(n)
		self.afterLoop()
	
	
	def runLoop(self, n):
		"""Loops through every event in the files and calls runEvent for each one"""
		
		n = min(n, self.basic_header.GetEntries())
		print "Reading", n, "events"
		
		for i in range(n):
			for module in self.modules:
				module.GetEntry(i)
			self.runEvent()
	
	
	def runEvent(self):
		"""Called for every event in the files"""
 				
		NVtx=self.TruthDir_Vertices.NVtx

		for ivtx in xrange(NVtx):
			vtx=self.TruthDir_Vertices.Vertices[ivtx]
			
			EvtCode=vtx.ReactionCode

			EvtCodeSplitList=EvtCode.split(";")
			
			IncomingPDG=EvtCodeSplitList[0][3:]
						
			TargetNucleus=EvtCodeSplitList[1][4:]		

			if(EvtCodeSplitList[2][:2]=="N:"):
				TargetNucleon=EvtCodeSplitList[2][2:]
				
				if(EvtCodeSplitList[3][:2]=="q:"):
					Current=EvtCodeSplitList[4][10:12]
					InteractionType=EvtCodeSplitList[4].split(",")[1]#could just say coherent?
				else:
					Current=EvtCodeSplitList[3][10:12]
					InteractionType=EvtCodeSplitList[3].split(",")[1]				
					
				
			else:#For coherent scattering
				TargetNucleon=None
				
				Current=EvtCodeSplitList[2][10:12]
				InteractionType=EvtCodeSplitList[2].split(",")[1]
			
			inFGDX=(vtx.Position[0]>=-832.2 and vtx.Position[0]<=832.2)
			inFGDY=(vtx.Position[1]>=-777.2 and vtx.Position[1]<=887.2)
			inFGDZ=(vtx.Position[3]>=123.45 and vtx.Position[3]<=446.95) or (vtx.Position[3]>=1481.45 and vtx.Position[3]<=1807.95)

			inFGD=(inFGDX and inFGDY and inFGDZ)
			
			if(inFGD and Current=="CC" and InteractionType=="QES"):#Checks if in FGD and CCQE interaction
				self.histograms["XYZ_Position"].Fill(vtx.Position[0],vtx.Position[1],vtx.Position[2])

			Momentum=vtx.NeutrinoMomentum
			
			print Momentum.X()

		
def main():
	
	if( len(sys.argv) != 3 ):
		print "[USAGE]: python example_analysis.py path/to/files/input_file_pattern output_filename.root"
		return
	
	# Always load the libraries, or nothing will work
	# Make sure the libraries were made with the same version of ROOT as the analysis files were produced with
	libraries.load("nd280/nd280.so")
	
	# glob returns a list of all files mathing the expression given to it
	#input_filename_list = ( glob.glob( sys.argv[1]+"*" ) )
	
	FileList = open("prod5_analysis.list")
	
	input_filename_list = FileList.read().splitlines()
	
	output_filename = sys.argv[2]
	
	analysis = Analysis(input_filename_list, output_filename)
	analysis.run(100)

	

if __name__ == "__main__":
	main()
