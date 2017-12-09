import libraries
import glob
import sys
import ROOT
import RooTrackerTools
import math

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

		self.ProtonPhotonDecayNumber=0
	
	
	def beforeLoop(self):
		"""Opens input and output files, creates histograms and intitialises any other necessary variables"""
		self.loadInputFiles()
		self.loadOutputFile()
		self.addHistogram1D("True_Enu", "True Neutrino Energy [GeV]", 100, 0.0, 10.0)#Histogram of neutrino energy
		self.addHistogram1D("True_Enu_Delta", "True Neutrino Energy from Delta producing events [GeV]", 100, 0.0, 10.0)#Histogram of neutrino energy from Delta producing events
		self.addHistogram1D("Interaction_Mode_Delta", "NEUT interaction codes of Delta producing events", 53, 0, 53)#Histogram of interaction modes of Delta producing events
		self.addHistogram2D("Vertex_Location_XY", "Location of interaction vertices in the X-Y plane of the detector",100,-3000,3000,100,-3000,3000)#Histogram of vertex location in XY plane
		self.addHistogram2D("Vertex_Location_YZ", "Location of interaction vertices in the Y-Z plane of the detector",100,-3000,3000,100,-3000,3000)#Histogram of vertex location in YZ plane
		self.addHistogram1D("True_Enu_Delta_inFGD", "Neutrino energies of FGD Delta producing events (GeV)",100,0,10)#Histogram of neutrino energy of Deltas produced in the FGD
		self.addHistogram1D("Delta_Momentum", "Momentum of Delta baryons (GeV/c)",100,0,5)#Histogram of neutrino energy of Deltas produced in the FGD
		self.addHistogram1D("Proton_Momentum", "Momentum of Protons from Delta decays (GeV/c)",100,0,4)#Histogram of proton momentum from Delta decays
		self.addHistogram1D("Pion_Momentum", "Momentum of Pions from Delta decays (GeV/c)",100,0,4)#Histogram of pion momentum from Delta decays
	
	
	def addHistogram1D(self, name, title, n_bins, minimum, maximum):
		""" Add a 1D histogram to the histogram list """
		self.histograms[ name ] = ROOT.TH1F(name, title, n_bins, minimum, maximum)
	
	
	def addHistogram2D(self, name, title, n_bins_x, minimum_x, maximum_x, n_bins_y, minimum_y, maximum_y):
		""" Add a 1D histogram to the histogram list """
		self.histograms[ name ] = ROOT.TH2F(name, title, n_bins_x, minimum_x, maximum_x, n_bins_y, minimum_y, maximum_y)
	
	
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

		print(self.ProtonPhotonDecayNumber)
	
	
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
			
			OutgoingDelta=False
			inFGD=False
			DaughterNumber=0
			ProtonDaughter=0
			PionDaughter=0
			ProtonPresent=0
			PhotonPresent=0

			for particle in self.Rootools.getParticles(vertex):#Loop for analysis of vertices
 				if (particle.pdg==2214):#The delta is never set as a final state particle so unable to use particle.isOutgoing()
					OutgoingDelta=True

					inFGDX=(particle.position[0]>=-832.2 and particle.position[0]<=832.2)#Checks if Delta was produced in PGD
					inFGDY=(particle.position[1]>=-777.2 and particle.position[1]<=887.2)
					inFGDZ=(particle.position[3]>=123.45 and particle.position[3]<=446.95) or (particle.position[3]>=1481.45 and particle.position[3]<=1807.95)

					inFGD=(inFGDX and inFGDY and inFGDZ)

					DaughterNumber=particle.last_daughter-particle.first_daughter+1
					DeltaDaughterFirst=particle.first_daughter
					DeltaDaughterLast=particle.last_daughter

					if(DaughterNumber==2):#Final bullet point 2.
						for particle in self.Rootools.getParticles(vertex):
							if(particle.i>=DeltaDaughterFirst and particle.i<=DeltaDaughterLast):
								if(particle.pdg==2212):
									ProtonDaughter=particle.i
								if(particle.pdg==111):
									PionDaughter=particle.i

					if(DaughterNumber==2):#Final bullet point 2.
						for particle in self.Rootools.getParticles(vertex):
							if(particle.i>=DeltaDaughterFirst and particle.i<=DeltaDaughterLast):
								if(particle.pdg==2212):
									ProtonPresent=True
								if(particle.pdg==22):
									PhotonPresent=True
								
			for particle in self.Rootools.getParticles(vertex):#Loop to fill histograms
 				if (particle.isIncoming() and particle.pdg==14):#All neutrino energy histogram
					enu = particle.momentum.E()
					self.histograms["True_Enu"].Fill(enu)

				if (particle.isIncoming() and particle.pdg==14 and OutgoingDelta):#Delta neutrino energy histogram
					enu = particle.momentum.E()
					self.histograms["True_Enu_Delta"].Fill(enu)
					
				if (OutgoingDelta):#Interaction mode histogram
					self.histograms["Interaction_Mode_Delta"].Fill(self.Rootools.getNeutCode(vertex))

				#XY vertex histogram
				self.histograms["Vertex_Location_XY"].Fill(self.Rootools.getVertexPosition(vertex)[0],self.Rootools.getVertexPosition(vertex)[1])

				#YZ vertex histogram
				self.histograms["Vertex_Location_YZ"].Fill(self.Rootools.getVertexPosition(vertex)[1],self.Rootools.getVertexPosition(vertex)[2])

				if (particle.isIncoming() and particle.pdg==14 and inFGD):#Neutrino energy of Delta producing interactions where the Delta was created in the FGD
					enu = particle.momentum.E()
					self.histograms["True_Enu_Delta_inFGD"].Fill(enu)

				if(particle.pdg==2214):#Considering the Delta baryons
					DeltaMomentum=math.sqrt(particle.momentum[0]*particle.momentum[0]+particle.momentum[1]*particle.momentum[1]+particle.momentum[2]*particle.momentum[2])
					self.histograms["Delta_Momentum"].Fill(DeltaMomentum)

				if(ProtonDaughter!=0 and PionDaughter!=0):
					if(particle.i==ProtonDaughter):
						ProtonMomentum=math.sqrt(particle.momentum[0]*particle.momentum[0]+particle.momentum[1]*particle.momentum[1]+particle.momentum[2]*particle.momentum[2])
						self.histograms["Proton_Momentum"].Fill(ProtonMomentum)
					if(particle.i==PionDaughter):
						PionMomentum=math.sqrt(particle.momentum[0]*particle.momentum[0]+particle.momentum[1]*particle.momentum[1]+particle.momentum[2]*particle.momentum[2])
						self.histograms["Pion_Momentum"].Fill(PionMomentum)

			if(PhotonPresent and ProtonPresent):
				self.ProtonPhotonDecayNumber+=1
		
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
	analysis.run(100000000000000000000000000)

if __name__ == "__main__":
	main()
