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
	
	
	def beforeLoop(self):
		"""Opens input and output files, creates histograms and intitialises any other necessary variables"""
		self.loadInputFiles()
		self.loadOutputFile()
		self.addHistogram1D("True_Enu", "True Neutrino Energy [GeV]", 100, 0.0, 5.0)
	
	
	def addHistogram1D(self, name, title, n_bins, minimum, maximum):
		""" Add a 1D histogram to the histogram list """
		self.histograms[ name ] = ROOT.TH1F(name, title, n_bins, minimum, maximum)
	
	
	def addHistogram2D(self, name, title, n_bins_x, minimum_x, maximum_x, n_bins_y, minimum_y, maximum_y):
		""" Add a 1D histogram to the histogram list """
		self.histograms[ name ] = ROOT.TH1F(name, title, n_bins_x, minimum_x, maximum_x, n_bins_y, minimum_y, maximum_y)
	
	
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
		
		print "Event", self.basic_header.EventID
		
		for i,vertex in enumerate(self.genievtx.Vtx):
			print "Genie Vertex -- ",i
			for particle in self.Rootools.getParticles(vertex):
 				if (particle.isIncoming() and particle.pdg==14):
					enu = particle.momentum.E()
					self.histograms["True_Enu"].Fill(enu)

		
def main():
	
	if( len(sys.argv) != 3 ):
		print "[USAGE]: python example_analysis.py path/to/files/input_file_pattern output_filename.root"
		return
	
	# Always load the libraries, or nothing will work
	# Make sure the libraries were made with the same version of ROOT as the analysis files were produced with
	libraries.load("nd280/nd280.so")
	
	# glob returns a list of all files mathing the expression given to it
	input_filename_list = ( glob.glob( sys.argv[1]+"*" ) )
	
	output_filename = sys.argv[2]
	
	analysis = Analysis(input_filename_list, output_filename)
	analysis.run(10)

	

if __name__ == "__main__":
	main()
