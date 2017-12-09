import libraries
import glob
import sys
import RooTrackerTools
import math
import datetime
import os
import array

import ROOT
ROOT.gROOT.SetBatch(True)

import EventCodeDeconstructor
import DataWriter
import TheoreticalParticle
import ParticleCodes
import PIDParticle
import SelectionCriteria

import ROOTFile
import TextConstants
import PhysicalConstants
import StatisticsCollection

import ThreeVector
import ThreeDimensionalObject

Now = datetime.datetime.now()
DataLocation = "/storage/epp2/phujce/Final Year Project/Main/Data Archive/"

class Analysis:
	
	def __init__(self, InputFileLocatorList, OutputROOTFileLocator, OutputTextFileLocator):
		
		self.InputFileLocatorList = InputFileLocatorList
		self.OutputROOTFileLocator = OutputROOTFileLocator
		self.OutputTextFileLocator = OutputTextFileLocator
		
		self.Histograms = {}
		self.Modules = []
		
		self.BasicInformation = self.LoadModule("HeaderDir/BasicHeader")
		
		self.Truth_GRTVertices = self.LoadModule("TruthDir/GRooTrackerVtx")
		self.Truth_Vertices = self.LoadModule("TruthDir/Vertices")
		self.Truth_Trajectories = self.LoadModule("TruthDir/Trajectories")
		
		self.Reconstructed_Global = self.LoadModule("ReconDir/Global")
		self.Reconstructed_TEC = self.LoadModule("ReconDir/TrackerECal")
		
		self.RTTools = RooTrackerTools.RooTrackerTools()
		
		self.EventCodeDeconstructor1 = EventCodeDeconstructor.EventCodeDeconstructor()
				
		self.EventNumber = 0
		
		self.SelectionCriteriaList = []
					
	
	def LoadInputFiles(self):		
		# Adds each file in the list of input file names to each module we want to use		
		
		for FileLocator in self.InputFileLocatorList:
			for Module in self.Modules:
				Module.Add(FileLocator)
		
		
	def LoadModule(self, Module_Reference):		
		# Load all the appropriate modules from the oaAnalysis file that we have defined	
			
		Module = ROOT.TChain(Module_Reference)
		self.Modules.append(Module)
		
		return Module
	
		
	def Analyse(self, n = 999999999):
		
		self.LoadInputFiles()
	
	
		self.TruthStatistics = StatisticsCollection.StatisticsCollection("Truth Statistics")
				
		self.TruthStatistics.NewStatistic("NEvents", "Number of Events", 0)
		self.TruthStatistics.NewStatistic("NVertices", "Number of Vertices", 0)
		self.TruthStatistics.NewStatistic("NVerticesFGD", "Number of Vertices in the FGDs", 0)		
		self.TruthStatistics.NewStatistic("NDeltaToProtonPhoton", "Number of Delta to Proton-Photon Events", 0)
		self.TruthStatistics.NewStatistic("NDeltaToProtonPhotonCC", "Number of Delta to Proton-Photon Charged-Current Events", 0)
		self.TruthStatistics.NewStatistic("NDeltaToProtonPhotonNC", "Number of Delta to Proton-Photon Neutral-Current Events", 0)		
		self.TruthStatistics.NewStatistic("NDeltaToProtonPhotonFGD", "Number of Delta to Proton-Photon Events in the FGDs", 0)
		self.TruthStatistics.NewStatistic("NDeltaToProtonPhotonCCFGD", "Number of Delta to Proton-Photon Charged-Current Events in the FGDs", 0)
		self.TruthStatistics.NewStatistic("NDeltaToProtonPhotonNCFGD", "Number of Delta to Proton-Photon Neutral-Current Events in the FGDs", 0)
				
				
		self.ReconstructedStatistics = StatisticsCollection.StatisticsCollection("Reconstructed Statistics")
		
		self.ReconstructedStatistics.NewStatistic("NEventsWithRPID", "Number of Events with at least one Reconstructed PID", 0)
		self.ReconstructedStatistics.NewStatistic("NEventsWithRProton", "Number of Events with at least one Reconstructed Proton Track", 0)
		self.ReconstructedStatistics.NewStatistic("NEventsWithCRProton", "Number of Events with at least one Correctly Reconstructed Proton Track", 0)
		self.ReconstructedStatistics.NewStatistic("NEventsWithCRProton18TPC", "Number of Events with at least one Correctly Reconstructed Proton Track with at least 18 TPC Nodes", 0)		
		self.ReconstructedStatistics.NewStatistic("NEventsWithTECC", "Number of Events with at least one Tracker EC Cluster", 0)		
		self.ReconstructedStatistics.NewStatistic("NEventsWithTECCAndCRProton", "Number of Events with at least one Tracker EC Cluster and one Correctly Reconstructed Proton Track", 0)		
		
		
		self.EfficiencyStatistics = StatisticsCollection.StatisticsCollection("Efficiency Statistics")
		
		self.EfficiencyStatistics.NewStatistic("NEvents0", "Initial Number of Events", 0)
		self.EfficiencyStatistics.NewStatistic("NEvents1", "Selection 1 - Number of Events with at least one Reconstructed Proton Track - Events Remaining", 0)
		self.EfficiencyStatistics.NewStatistic("NEvents2", "Selection 2 - Number of Events with at least one Reconstructed Proton Track that passes through at least 18 TPC Nodes - Events Remaining", 0)
		self.EfficiencyStatistics.NewStatistic("NEvents3", "Selection 3 - Number of Events with only one Reconstructed Proton Track - Events Remaining", 0)
		self.EfficiencyStatistics.NewStatistic("NEvents4", "Selection 4 - Number of Events with at least one EC Cluster - Events Remaining", 0)


		self.FGD1 = ThreeDimensionalObject.ThreeDimensionalObject(-832.2, 832.2, -777.2, 887.2, 123.45, 446.95)
		self.FGD2 = ThreeDimensionalObject.ThreeDimensionalObject(-832.2, 832.2, -777.2, 887.2, 1481.45, 1807.95)
		
	
		sys.stdout = DataWriter.DataWriter(self.OutputTextFileLocator)
		
		self.ROOTFile1 = ROOTFile.ROOTFile(self.OutputROOTFileLocator)
		self.ROOTFile1.Open()
		
		self.ROOTFile1.NewHistogram1D("Reconstructed_Delta1Hadron_Energy", "Energy of the Unknown Particle which created the Reconstructed Proton and Photon", "", "", 100, 0, 5000)
		self.ROOTFile1.NewHistogram1D("Reconstructed_Delta1Hadron_MomentumModulus", "Momentum Modulus of the Unknown Particle which created the Reconstructed Proton and Photon", "", "", 100, 0, 3000)
		self.ROOTFile1.NewHistogram1D("Reconstructed_Delta1Hadron_Mass", "Mass of the Unknown Particle which created the Reconstructed Proton and Photon", "", "", 100, 0, 3000)
		
		self.ROOTFile1.NewHistogram1D("Truth_Delta1Hadron_Energy", "Energy of the Delta 1 Hadrons", "", "", 100, 0, 5000)
		self.ROOTFile1.NewHistogram1D("Truth_Delta1Hadron_MomentumModulus", "Energy of the Delta 1 Hadrons", "", "", 100, 0, 3000)
		
		self.ROOTFile1.NewHistogram1DStack("Proton_Recon_Efficiency:TrueEnergy","Efficiency of reconstructed proton tracks for varying true energy")
		self.ROOTFile1.NewHistogram1D("Proton_Recon:ProtonEnergyTrue", "True energy of correctly reconstructed protons", "", "", 100, 0, 5000)
		self.ROOTFile1.NewHistogram1D("Proton_Recon:MuonEnergyTrue", "True energy of muons incorrectly reconstructed as protons", "", "", 100, 0, 5000)
		self.ROOTFile1.NewHistogram1D("Proton_Recon:ElectronEnergyTrue", "True energy of electrons incorrectly reconstructed as protons", "", "", 100, 0, 5000)
		self.ROOTFile1.NewHistogram1D("Proton_Recon:AntiElectronEnergyTrue", "True energy of electrons incorrectly reconstructed as protons", "", "", 100, 0, 5000)
		
		self.ROOTFile1.NewHistogram1DStack("Proton_Recon_Efficiency:ReconMomentum","Efficiency of reconstructed proton tracks for varying recon momentum")
		self.ROOTFile1.NewHistogram1D("Proton_Recon:ProtonMomentumRecon", "Recon momentum of correctly reconstructed protons", "", "", 100, 0, 5000)
		self.ROOTFile1.NewHistogram1D("Proton_Recon:MuonMomentumRecon", "Recon momentum of muons incorrectly reconstructed as protons", "", "", 100, 0, 5000)
		self.ROOTFile1.NewHistogram1D("Proton_Recon:ElectronMomentumRecon", "Recon momentum of electrons incorrectly reconstructed as protons", "", "", 100, 0, 5000)
		self.ROOTFile1.NewHistogram1D("Proton_Recon:AntiElectronMomentumRecon", "Recon momentum of electrons incorrectly reconstructed as protons", "", "", 100, 0, 5000)
	
		self.ROOTFile1.NewHistogram1D("Recon_Truth_Proton_Momentum", "Recon momentum minus truth momentum for PIDs reconstructed as protons", "", "", 100, -500, 500)
		self.ROOTFile1.NewHistogram1D("Truth_Proton_Momentum", "Truth momentum for PIDs reconstructed as protons", "", "", 100, 0, 5000)
		
						
		n = min(n, self.BasicInformation.GetEntries())
		
		self.TruthStatistics.Statistics["NEvents"].Quantity = n
		
		for i in range(n):
			for module in self.Modules:
				module.GetEntry(i)
			self.runEvent()

		self.ROOTFile1.Histograms["Proton_Recon:ProtonEnergyTrue"].SetFillColor(2)
		self.ROOTFile1.Histograms["Proton_Recon_Efficiency:TrueEnergy"].Add(self.ROOTFile1.Histograms["Proton_Recon:ProtonEnergyTrue"])
		self.ROOTFile1.Histograms["Proton_Recon:MuonEnergyTrue"].SetFillColor(3)
		self.ROOTFile1.Histograms["Proton_Recon_Efficiency:TrueEnergy"].Add(self.ROOTFile1.Histograms["Proton_Recon:MuonEnergyTrue"])
		self.ROOTFile1.Histograms["Proton_Recon:ElectronEnergyTrue"].SetFillColor(4)
		self.ROOTFile1.Histograms["Proton_Recon_Efficiency:TrueEnergy"].Add(self.ROOTFile1.Histograms["Proton_Recon:ElectronEnergyTrue"])
		self.ROOTFile1.Histograms["Proton_Recon:AntiElectronEnergyTrue"].SetFillColor(5)
		self.ROOTFile1.Histograms["Proton_Recon_Efficiency:TrueEnergy"].Add(self.ROOTFile1.Histograms["Proton_Recon:AntiElectronEnergyTrue"])
		
		self.ROOTFile1.Histograms["Proton_Recon:ProtonMomentumRecon"].SetFillColor(2)
		self.ROOTFile1.Histograms["Proton_Recon_Efficiency:ReconMomentum"].Add(self.ROOTFile1.Histograms["Proton_Recon:ProtonMomentumRecon"])
		self.ROOTFile1.Histograms["Proton_Recon:MuonMomentumRecon"].SetFillColor(3)
		self.ROOTFile1.Histograms["Proton_Recon_Efficiency:ReconMomentum"].Add(self.ROOTFile1.Histograms["Proton_Recon:MuonMomentumRecon"])
		self.ROOTFile1.Histograms["Proton_Recon:ElectronMomentumRecon"].SetFillColor(4)
		self.ROOTFile1.Histograms["Proton_Recon_Efficiency:ReconMomentum"].Add(self.ROOTFile1.Histograms["Proton_Recon:ElectronMomentumRecon"])
		self.ROOTFile1.Histograms["Proton_Recon:AntiElectronMomentumRecon"].SetFillColor(5)
		self.ROOTFile1.Histograms["Proton_Recon_Efficiency:ReconMomentum"].Add(self.ROOTFile1.Histograms["Proton_Recon:AntiElectronMomentumRecon"])
		
				
		################################ Cuts
		
		self.SelectionCriteriaList[0].EventsRemaining = self.TruthStatistics.Statistics["NEvents"].Quantity

		CutNumber = len(self.SelectionCriteriaList)
		
		for CriteriaListCounter in xrange(CutNumber):
			self.SelectionCriteriaList[CriteriaListCounter].AbsoluteEfficiency = float(self.SelectionCriteriaList[CriteriaListCounter].EventsRemaining)/float(self.SelectionCriteriaList[0].EventsRemaining)
			
			if (CriteriaListCounter > 0):
				self.SelectionCriteriaList[CriteriaListCounter].RelativeEfficiency = float(self.SelectionCriteriaList[CriteriaListCounter].EventsRemaining)/float(self.SelectionCriteriaList[CriteriaListCounter-1].EventsRemaining)
				
			self.SelectionCriteriaList[CriteriaListCounter].Purity = float(self.SelectionCriteriaList[CriteriaListCounter].TrueDelta) / float(self.SelectionCriteriaList[CriteriaListCounter].EventsRemaining)

		self.SelectionCriteriaList[0].TrueDelta = self.TruthStatistics.Statistics["NDeltaToProtonPhoton"].Quantity
		self.SelectionCriteriaList[0].Purity = float(self.SelectionCriteriaList[0].TrueDelta)/float(self.SelectionCriteriaList[0].EventsRemaining)
		self.SelectionCriteriaList[0].RelativeEfficiency = 1
		self.SelectionCriteriaList[0].AbsoluteEfficiency = 1

		############################# Graphs of cuts

		XList = []
		YList = []
		
		for CriteriaListCounter in xrange(CutNumber):
			XList.append(CriteriaListCounter)
			YList.append(self.SelectionCriteriaList[CriteriaListCounter].AbsoluteEfficiency)
			
		XArray = array.array("d",XList)
		YArray = array.array("d",YList)
			
		self.ROOTFile1.NewGraph("Absolute_Efficiency","Absolute Efficiency for the series of cuts",CutNumber, "Selection Criteria", XArray, "Absolute Efficiency", YArray)
		
		XList = []
		YList = []
		
		for CriteriaListCounter in xrange(CutNumber):
			XList.append(CriteriaListCounter)
			YList.append(self.SelectionCriteriaList[CriteriaListCounter].RelativeEfficiency)
			
		XArray = array.array("d",XList)
		YArray = array.array("d",YList)
			
		self.ROOTFile1.NewGraph("Relative_Efficiency","Relative Efficiency for the series of cuts",CutNumber, "Selection Criteria", XArray, "Relative Efficiency", YArray)
		
		XList = []
		YList = []
		
		for CriteriaListCounter in xrange(CutNumber):
			XList.append(CriteriaListCounter)
			YList.append(self.SelectionCriteriaList[CriteriaListCounter].Purity)
			
		XArray = array.array("d",XList)
		YArray = array.array("d",YList)
			
		self.ROOTFile1.NewGraph("Purity","Purity for the series of cuts",CutNumber, "Selection Criteria", XArray, "Purity", YArray)
		
		############## Application of truth to criteria
				
		
		self.ROOTFile1.NewHistogram1DStack("Cut_Purity","Constituent Processes for the Events after every Selection")
		self.ROOTFile1.NewHistogram1D("Delta_True", "True Delta->p gamma interactions for each cut", "", "",CutNumber,0,CutNumber)
		self.ROOTFile1.NewHistogram1D("Delta1HadronToProtonPi0Meson", "Number of Delta 1 Hadrons to Protons and Pi 0 Mesons", "", "",CutNumber,0,CutNumber)
		self.ROOTFile1.NewHistogram1D("Other_Resonance_True", "True other resonances interactions for each cut", "", "",CutNumber,0,CutNumber)
		self.ROOTFile1.NewHistogram1D("QES_True", "True QES interactions for each cut", "", "",CutNumber,0,CutNumber)
		self.ROOTFile1.NewHistogram1D("DIS_True", "True DIS interactions for each cut", "", "",CutNumber,0,CutNumber)
		self.ROOTFile1.NewHistogram1D("COH_True", "True COH interactions for each cut", "", "",CutNumber,0,CutNumber)
		
		
		for CutCounter in xrange(len(self.SelectionCriteriaList)):
			for FillCounter in xrange(self.SelectionCriteriaList[CutCounter].TrueDelta):
				self.ROOTFile1.Histograms["Delta_True"].Fill(CutCounter)
			for FillCounter in xrange(self.SelectionCriteriaList[CutCounter].Pi0MesonDelta):
				self.ROOTFile1.Histograms["Delta1HadronToProtonPi0Meson"].Fill(CutCounter)
			for FillCounter in xrange(self.SelectionCriteriaList[CutCounter].OtherResonance):
				self.ROOTFile1.Histograms["Other_Resonance_True"].Fill(CutCounter)
			for FillCounter in xrange(self.SelectionCriteriaList[CutCounter].QESInteraction):
				self.ROOTFile1.Histograms["QES_True"].Fill(CutCounter)
			for FillCounter in xrange(self.SelectionCriteriaList[CutCounter].DISInteraction):
				self.ROOTFile1.Histograms["DIS_True"].Fill(CutCounter)
			for FillCounter in xrange(self.SelectionCriteriaList[CutCounter].COHInteraction):
				self.ROOTFile1.Histograms["COH_True"].Fill(CutCounter)
				
		self.ROOTFile1.Histograms["Delta_True"].SetFillColor(2)
		self.ROOTFile1.Histograms["Cut_Purity"].Add(self.ROOTFile1.Histograms["Delta_True"])
		
		self.ROOTFile1.Histograms["Delta1HadronToProtonPi0Meson"].SetFillColor(7)
		self.ROOTFile1.Histograms["Cut_Purity"].Add(self.ROOTFile1.Histograms["Delta1HadronToProtonPi0Meson"])
		
		self.ROOTFile1.Histograms["Other_Resonance_True"].SetFillColor(3)
		self.ROOTFile1.Histograms["Cut_Purity"].Add(self.ROOTFile1.Histograms["Other_Resonance_True"])
		
		self.ROOTFile1.Histograms["QES_True"].SetFillColor(4)
		self.ROOTFile1.Histograms["Cut_Purity"].Add(self.ROOTFile1.Histograms["QES_True"])
		
		self.ROOTFile1.Histograms["DIS_True"].SetFillColor(5)
		self.ROOTFile1.Histograms["Cut_Purity"].Add(self.ROOTFile1.Histograms["DIS_True"])
		
		self.ROOTFile1.Histograms["COH_True"].SetFillColor(6)
		self.ROOTFile1.Histograms["Cut_Purity"].Add(self.ROOTFile1.Histograms["COH_True"])
		
		
		
		print TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine, TextConstants.LineSeparator
		print "Reading", n, "Events"
		print TextConstants.LineSeparator
		
		
		print "Starting events:" , str(self.TruthStatistics.Statistics["NEvents"].Quantity)
		
		print TextConstants.NewLine
		
		print "First Cut: Every event with at least one proton reconstructed PID"
		print "Events remaining:" , str(self.SelectionCriteriaList[1].EventsRemaining)
		
		print "Second Cut: Events with at least one reconstructed proton track that pass through at least 18 TPC nodes"
		print "Events remaining:" , str(self.SelectionCriteriaList[2].EventsRemaining)
		
		print "Third Cut: Requirement of single proton track"
		print "Events remaining:" , str(self.SelectionCriteriaList[3].EventsRemaining)
		
		print "Fourth Cut: Requirement of at least one ECal cluster detection"
		print "Events remaining:" , str(self.SelectionCriteriaList[4].EventsRemaining)
		
		print TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine
	
		print self.TruthStatistics.ToText()
		print self.ReconstructedStatistics.ToText()
		print self.EfficiencyStatistics.ToText()
	
		del sys.stdout#Closes .txt file and returns to printing only to console
	
		self.ROOTFile1.Close()
		
	
	def runEvent(self):
	
		self.EventNumber += 1
	
		###### First loop over the true genie data to look for information about the delta interactions
	
		DeltaPGammaEvent = False
		Delta1HadronToProtonPi0MesonEvent = False
	
		NVertices = self.Truth_GRTVertices.NVtx

		InteractionType = ""
		
		for GRTVertex1 in self.Truth_GRTVertices.Vtx: #Loop over vertices in event
						
			self.TruthStatistics.Statistics["NVertices"].Quantity += 1
						
			IncidentMuonNeutrino = False#For a later check of whether incident particle is a neutrino
			ProtonFromDelta = False#For logical check on Delta interaction of interest
			PhotonFromDelta = False
			Pi0MesonFromDelta = False
			
			for GRTParticle1 in self.RTTools.getParticles(GRTVertex1):
				
				###################################### Check for initial neutrino
				
				if (GRTParticle1.pdg == ParticleCodes.MuNeutrino):#Looks for a neutrino
				
					if (GRTParticle1.status == 0):#Checks if neutrino is initial state
					
						IncidentMuonNeutrino = True						
				
				###################################### Check for Delta interactions
				
				if (GRTParticle1.pdg == ParticleCodes.Delta1Hadron):

					DeltaDaughterFirst = GRTParticle1.first_daughter#Finds first Delta daughter
					DeltaDaughterLast = GRTParticle1.last_daughter#Finds last Delta daughter
					DeltaDaughterNumber = DeltaDaughterLast-DeltaDaughterFirst+1#Finds number of daughters of the delta

					if (DeltaDaughterNumber == 2):#Delta -> p gamma must have 2 daughters
						
						for DaughterParticle in self.RTTools.getParticles(GRTVertex1):#Loop again over particles in vertex
						
							if (DaughterParticle.i >= DeltaDaughterFirst and DaughterParticle.i <= DeltaDaughterLast):#Only looks for when counter is in range of Delta daughter particles
							
								if (DaughterParticle.pdg == ParticleCodes.Proton):
									ProtonFromDelta = True
									
								if (DaughterParticle.pdg == ParticleCodes.Photon):
									PhotonFromDelta = True
									
								if (DaughterParticle.pdg == ParticleCodes.Pi0Meson):
									Pi0MesonFromDelta = True
									
			######################################## Check if in FGD (target mass for neutrino interactions)
									
			inFGDX = (GRTVertex1.EvtVtx[0] >= self.FGD1.X1 and GRTVertex1.EvtVtx[0] <= self.FGD1.X2)#Checks if interaction began in FGD: X axis
			inFGDY = (GRTVertex1.EvtVtx[1] >= self.FGD1.Y1 and GRTVertex1.EvtVtx[1] <= self.FGD1.Y2)#Y axis
			inFGDZ = (GRTVertex1.EvtVtx[2] >= self.FGD1.Z1 and GRTVertex1.EvtVtx[2] <= self.FGD1.Z2) or (GRTVertex1.EvtVtx[2] >= self.FGD2.Z1 and GRTVertex1.EvtVtx[2] <= self.FGD2.Z2)#Z axis
			
			inFGD = (inFGDX and inFGDY and inFGDZ)
			
			if (inFGD == True):
				self.TruthStatistics.Statistics["NVerticesFGD"].Quantity += 1
			
			######################################## Search for current and interaction type. This method can look at electron neutrinos and anti muon neutrinos for any possible extension
			
			self.EventCodeDeconstructor1.ReadCode(GRTVertex1.EvtCode)
			
			
			for Element1 in self.EventCodeDeconstructor1.Elements:
				if (Element1.Reference == "Process Code"):
					if (Element1.Content == "W-CC-QS"):
						Current = "CC"
						InteractionType = "QES"
					elif (Element1.Content == "W-CC-RP"):
						Current = "CC"
						InteractionType = "RES"
					elif (Element1.Content == "W-CC-DIS"):
						Current = "CC"
						InteractionType = "DIS"	
					elif (Element1.Content == "W-CC-C"):
						Current = "CC"
						InteractionType = "COH"				
					elif (Element1.Content == "W-NC-ES"):
						Current = "NC"
						InteractionType = "QES"				
					elif (Element1.Content == "W-NC-RP"):
						Current = "NC"
						InteractionType = "RES"				
					elif (Element1.Content == "W-NC-DIS"):
						Current = "NC"
						InteractionType = "DIS"				
					elif (Element1.Content == "W-NC-C"):
						Current = "NC"
						InteractionType = "COH"
								
							
			###################################### Categorisation of various interesting interactions ############
							
			DeltaPGammaInteraction = (IncidentMuonNeutrino and ProtonFromDelta and PhotonFromDelta and InteractionType == "RES")
			
			Delta1HadronToProtonPi0MesonInteraction = (IncidentMuonNeutrino and ProtonFromDelta and Pi0MesonFromDelta and InteractionType == "RES")
			
			if (DeltaPGammaInteraction):
				self.TruthStatistics.Statistics["NDeltaToProtonPhoton"].Quantity += 1
				DeltaPGammaEvent=True
				
			if (DeltaPGammaInteraction and Current == "CC"):
				self.TruthStatistics.Statistics["NDeltaToProtonPhotonCC"].Quantity += 1
				
			if (DeltaPGammaInteraction and Current == "NC"):
				self.TruthStatistics.Statistics["NDeltaToProtonPhotonNC"].Quantity += 1
				
			if (DeltaPGammaInteraction and inFGD):
				self.TruthStatistics.Statistics["NDeltaToProtonPhotonFGD"].Quantity += 1
				
			if (DeltaPGammaInteraction and inFGD and Current == "CC"):
				self.TruthStatistics.Statistics["NDeltaToProtonPhotonCCFGD"].Quantity += 1
				
			if (DeltaPGammaInteraction and inFGD and Current == "NC"):
				self.TruthStatistics.Statistics["NDeltaToProtonPhotonNCFGD"].Quantity += 1

			if (Delta1HadronToProtonPi0MesonInteraction):
				Delta1HadronToProtonPi0MesonEvent = True

		################################ Recon ###########################

		NPIDs=self.Reconstructed_Global.NPIDs#Number of reconstructed PIDs

		if (NPIDs > 0):
			
			self.ReconstructedStatistics.Statistics["NEventsWithRPID"].Quantity += 1

		ProtonCorrectlyReconstructed = False
		
		PIDDetectorList = []#List of detectors a PID has passed through
		
		ProtonEnergyList = []#List of energies of reconstructed proton PIDs
		
		ProtonMomentumListX = []#List of momenta of reconstructed proton PIDs
		ProtonMomentumListY = []
		ProtonMomentumListZ = []
		PIDParticleList = []
		PIDObjectList = []
		
		for PID in self.Reconstructed_Global.PIDs:#Loop over the PIDs if they exist
			
			PIDDetectorList.append(str(PID.Detectors))#This is a list of the detector paths for all the PIDs in the event
			
			############################# Looking at PIDs #######################
						
			if (len(PID.ParticleIds)>0):	#The reconstructed PID is put into a vector of possible PDGs: The best fitting PDG is given first and then the whole list (including the best
										#fitting  PDG) is given, ordered by PDG. See /home/theory/phujce/FinalYearProject/Recon/Data/FirstCut/Text/2012-12-31-11:46:57.txt
										#Sometimes the PDG vector is not given (because the reconstruction cannot decide?) so I ignore these PIDs
				
				TPCNumber = PID.NTPCs
				
				if (PID.ParticleIds[0] != 0 and PID.PIDWeights[0] >= 0):	#PDG is only nonzero if the event was in the inner, particle sensitive part of detector (eg not ECal)
																	#There is also the option of requiring the certainty of the particle identification to above be a set amount (not used yet)
					ParticleId = PID.ParticleIds[0]
				else:
					ParticleId = None
				
				if (ParticleId != None):
					
					SuitableTPCNodeNumber = False
					
					for TPCCounter in xrange(TPCNumber):#Loop over TPC PIDs
						TPCTrack = PID.TPC[TPCCounter]
						
						if (TPCTrack.NNodes>18):
							SuitableTPCNodeNumber = True
							self.ReconstructedStatistics.Statistics["NEventsWithCRProton18TPC"].Quantity += 1
							
					
					PIDObject = PIDParticle.PIDParticle()
					
					if (SuitableTPCNodeNumber):
						PIDObject.SuitableTPCNodeNumber = True
									
					PIDObject.ReconParticleID = ParticleId
					PIDObject.ReconFrontMomentum = PID.FrontMomentum
					
					PIDObject.ReconFrontDirectionX = PID.FrontDirection.X()
					PIDObject.ReconFrontDirectionY = PID.FrontDirection.Y()
					PIDObject.ReconFrontDirectionZ = PID.FrontDirection.Z()
					
					PIDObject.ReconFrontPositionX = PID.FrontPosition.X()
					PIDObject.ReconFrontPositionY = PID.FrontPosition.Y()
					PIDObject.ReconFrontPositionZ = PID.FrontPosition.Z()
					
					PIDObject.Detectors = str(PID.Detectors)

					for TrueTrajectoryCounter in xrange(self.Truth_Trajectories.NTraj):#Loop over the truth trajectories for comparison
						if (self.Truth_Trajectories.Trajectories[TrueTrajectoryCounter].ID == PID.TrueParticle.ID):
								
							TrueTrajectory = self.Truth_Trajectories.Trajectories[TrueTrajectoryCounter]
								
							PIDObject.TrueParticleID = TrueTrajectory.PDG
								
							PIDObject.TrueEnergy = TrueTrajectory.InitMomentum.E()
								
							PIDObject.TrueFrontMomentum = math.sqrt(TrueTrajectory.InitMomentum.X() * TrueTrajectory.InitMomentum.X()+TrueTrajectory.InitMomentum.Y() * TrueTrajectory.InitMomentum.Y()+TrueTrajectory.InitMomentum.Z() * TrueTrajectory.InitMomentum.Z())
							
					PIDObjectList.append(PIDObject)
		
		ReconstructedProtonTrackNumber = 0
		ReconstructedMuonTrackNumber = 0
		ReconstructedElectronTrackNumber = 0
		ReconstructedAntiElectronTrackNumber = 0
		ProtonTrackNumberBeforeTPC = 0
		FGDReconstructedProtonNumber = 0
		
		CorrectlyReconstructedProton = 0
		
		for PIDObject1 in PIDObjectList:
			
			if (PIDObject1.ReconParticleID == ParticleCodes.Proton):#Looking for reconstructed proton track
				ProtonTrackNumberBeforeTPC += 1
			
			if (PIDObject1.SuitableTPCNodeNumber):
			
				if (PIDObject1.ReconParticleID == ParticleCodes.Proton):#Looking for reconstructed proton track
					ReconstructedProtonTrackNumber += 1
					
					if (PIDObject1.Detectors[0] == "4" or PIDObject1.Detectors[0] == "5"):
											
						ProtonEnergyList.append(PIDObject1.ReconstructedParticleEnergy())
						self.ROOTFile1.Histograms["Recon_Truth_Proton_Momentum"].Fill(PIDObject1.ReconTrueMomentumDifference())	
						self.ROOTFile1.Histograms["Truth_Proton_Momentum"].Fill(PIDObject1.TrueFrontMomentum)
						
						ProtonMomentumListX.append(PIDObject1.ReconFrontMomentum * PIDObject1.ReconFrontDirectionX)#Momentum_x = Momentum Magnitude * Unit Vector_x
						ProtonMomentumListY.append(PIDObject1.ReconFrontMomentum * PIDObject1.ReconFrontDirectionY)
						ProtonMomentumListZ.append(PIDObject1.ReconFrontMomentum * PIDObject1.ReconFrontDirectionZ)
				
				############### Non-proton reconstructions ###########
				
				if (PIDObject1.ReconParticleID == ParticleCodes.MuLepton):
					ReconstructedMuonTrackNumber += 1
					
				if (PIDObject1.ReconParticleID == ParticleCodes.Electron):
					ReconstructedElectronTrackNumber += 1
					
				if (PIDObject1.ReconParticleID == ParticleCodes.AntiElectron):
					ReconstructedAntiElectronTrackNumber += 1
					
				############## Incorrect reconstructions #############
					
				if (PIDObject1.CorrectlyReconstructed() and PIDObject1.ReconParticleID == ParticleCodes.Proton):
					CorrectlyReconstructedProton += 1
					self.ROOTFile1.Histograms["Proton_Recon:ProtonEnergyTrue"].Fill(PIDObject1.TrueEnergy)
					self.ROOTFile1.Histograms["Proton_Recon:ProtonMomentumRecon"].Fill(PIDObject1.ReconFrontMomentum)
					
				elif (PIDObject1.ReconParticleID == ParticleCodes.Proton and PIDObject1.TrueParticleID == ParticleCodes.MuLepton):
					self.ROOTFile1.Histograms["Proton_Recon:MuonEnergyTrue"].Fill(PIDObject1.TrueEnergy)
					self.ROOTFile1.Histograms["Proton_Recon:MuonMomentumRecon"].Fill(PIDObject1.ReconFrontMomentum)
					
				elif (PIDObject1.ReconParticleID == ParticleCodes.Proton and PIDObject1.TrueParticleID == ParticleCodes.Electron):
					self.ROOTFile1.Histograms["Proton_Recon:ElectronEnergyTrue"].Fill(PIDObject1.TrueEnergy)
					self.ROOTFile1.Histograms["Proton_Recon:ElectronMomentumRecon"].Fill(PIDObject1.ReconFrontMomentum)
					
				elif (PIDObject1.ReconParticleID == ParticleCodes.Proton and PIDObject1.TrueParticleID == ParticleCodes.AntiElectron):
					self.ROOTFile1.Histograms["Proton_Recon:AntiElectronEnergyTrue"].Fill(PIDObject1.TrueEnergy)
					self.ROOTFile1.Histograms["Proton_Recon:AntiElectronMomentumRecon"].Fill(PIDObject1.ReconFrontMomentum)
		
		if (CorrectlyReconstructedProton > 0):
			ProtonCorrectlyReconstructed = True
		else:
			ProtonCorrectlyReconstructed = False
			
		if (ReconstructedProtonTrackNumber > 0):
			ReconstructedProtonTrack = True
		else:
			ReconstructedProtonTrack = False
		
		############################## ECal cluster section ###################################
				
		TrackerECal = self.Reconstructed_TEC #I think we will only look at the Tracker ECal (TPC+FGD) as the POD ECal is mainly used for POD !! What about downstream ECal
		
		NTrackerECalRecon = TrackerECal.NReconObject#Number of reconstructed objects in the ECal
		
		PhotonEnergyList = []#A list of the photon energies in each event
		PhotonMomentumListX = []
		PhotonMomentumListY = []
		PhotonMomentumListZ = []
		
		for TECReconstructedObject in TrackerECal.ReconObject:#Loop over these reconstructed objects
			
			ECEnergy = TECReconstructedObject.EMEnergyFit_Result#The energy of photon

			PhotonEnergyList.append(ECEnergy)#Add to the photon energy list
							
			if (TECReconstructedObject.IsShowerLike):#Check if ECal reconstruction is tracklike or showerlike, it shouldnt matter which for the photon, but the directions are different
				ECUnitDirection = ThreeVector.ThreeVector(TECReconstructedObject.Shower.Direction.X(), TECReconstructedObject.Shower.Direction.Y(), TECReconstructedObject.Shower.Direction.Z())
			elif (TECReconstructedObject.IsTrackLike):
				ECUnitDirection = ThreeVector.ThreeVector(TECReconstructedObject.Track.Direction.X(), TECReconstructedObject.Track.Direction.Y(), TECReconstructedObject.Track.Direction.Z())
						
			if (ECUnitDirection.Modulus() < 1.1):#For some reason there sometimes are occurences where the magnitude is far above 1. This if filters them out. We should probably look into this further
				PhotonMomentumListX.append(ECUnitDirection.X * ECEnergy)#E = p ... p_x = E_x  *  unit vector_x
				PhotonMomentumListY.append(ECUnitDirection.Y * ECEnergy)
				PhotonMomentumListZ.append(ECUnitDirection.Z * ECEnergy)
		
		############################## Summary Section ########################################

		if (ReconstructedProtonTrack):#Counts number of events with at least one reconstructed proton track
			self.ReconstructedStatistics.Statistics["NEventsWithRProton"].Quantity += 1
		if (ProtonCorrectlyReconstructed):
			self.ReconstructedStatistics.Statistics["NEventsWithCRProton"].Quantity += 1
		if (NTrackerECalRecon > 0):
			self.ReconstructedStatistics.Statistics["NEventsWithTECC"].Quantity += 1
		if (ReconstructedProtonTrack and NTrackerECalRecon > 0):
			self.ReconstructedStatistics.Statistics["NEventsWithTECCAndCRProton"].Quantity += 1
		
		############################ Cuts #########################
		
		Criteria = []
		
		if (ProtonTrackNumberBeforeTPC > 0):#1
			Criteria.append(True)
		else:
			Criteria.append(False)
		
		if (ReconstructedProtonTrackNumber > 0 and Criteria[0]):#2
			Criteria.append(True)			
		else:
			Criteria.append(False)
					
		if (ReconstructedProtonTrackNumber == 1 and Criteria[1]):
			Criteria.append(True)
		else:
			Criteria.append(False)
		
		if (NTrackerECalRecon > 0 and Criteria[2]):
			Criteria.append(True)
		else:
			Criteria.append(False)
		
		CutNumber = len(Criteria)
		
		if (self.EventNumber == 1):
			for CutCounter in xrange(CutNumber+1):
				
				SelectionCriterion1 = SelectionCriteria.SelectionCriteria()
				
				self.SelectionCriteriaList.append(SelectionCriterion1)
										
					
		for CutCounter in xrange(CutNumber):
			if (Criteria[CutCounter]):
				self.SelectionCriteriaList[CutCounter + 1].EventsRemaining += 1
				if (DeltaPGammaEvent):
					self.SelectionCriteriaList[CutCounter + 1].TrueDelta += 1
				elif (Delta1HadronToProtonPi0MesonEvent):
					self.SelectionCriteriaList[CutCounter + 1].Pi0MesonDelta += 1
				elif (InteractionType == "RES" and not DeltaPGammaEvent and not Delta1HadronToProtonPi0MesonEvent):
					self.SelectionCriteriaList[CutCounter + 1].OtherResonance += 1
				elif (InteractionType == "QES"):
					self.SelectionCriteriaList[CutCounter + 1].QESInteraction += 1
				elif (InteractionType == "DIS"):
					self.SelectionCriteriaList[CutCounter + 1].DISInteraction += 1
				elif (InteractionType == "COH"):
					self.SelectionCriteriaList[CutCounter + 1].COHInteraction += 1
			
		###### Delta Mass Histogram ####
		
		DeltaMomentumList = []
		
		if (len(PhotonEnergyList) > 0 and len(ProtonEnergyList) > 0):#Including only events where both photon and proton reconstruction happened
			for PhotonEnergyCounter in xrange(len(PhotonEnergyList)):#Loop over every item in both proton and photon lists and match them up
				for ProtonEnergyCounter in xrange(len(ProtonEnergyList)):
					
					UnknownObjectEnergy = PhotonEnergyList[PhotonEnergyCounter]+ProtonEnergyList[ProtonEnergyCounter]#Energy of Delta ... E_D = E_gamma + E_p
					
					self.ROOTFile1.Histograms["Reconstructed_Delta1Hadron_Energy"].Fill(UnknownObjectEnergy)
										
					if (PhotonEnergyCounter < len(PhotonMomentumListX) and ProtonEnergyCounter < len(ProtonMomentumListX)):#To account for earlier trick of not including unit vectors > 1.1
						DeltaMomentumX = PhotonMomentumListX[PhotonEnergyCounter]+ProtonMomentumListX[ProtonEnergyCounter]#In component form p_{x D} = p_{x gamma} + p_{x proton}
						DeltaMomentumY = PhotonMomentumListY[PhotonEnergyCounter]+ProtonMomentumListY[ProtonEnergyCounter]
						DeltaMomentumZ = PhotonMomentumListZ[PhotonEnergyCounter]+ProtonMomentumListZ[ProtonEnergyCounter]
					
						DeltaMomentumMagnitude = math.sqrt(DeltaMomentumX * DeltaMomentumX+DeltaMomentumY * DeltaMomentumY+DeltaMomentumZ * DeltaMomentumZ)#|p_{D}|^{2}
						
						if (UnknownObjectEnergy > DeltaMomentumMagnitude):#As this is statistical approach, sometimes can get sqrt(negative number)
							DeltaMass = math.sqrt(UnknownObjectEnergy * UnknownObjectEnergy-DeltaMomentumMagnitude * DeltaMomentumMagnitude)#m^2 = E^2 - p^2
							self.ROOTFile1.Histograms["Reconstructed_Delta1Hadron_Mass"].Fill(DeltaMass)
										
						self.ROOTFile1.Histograms["Reconstructed_Delta1Hadron_MomentumModulus"].Fill(DeltaMomentumMagnitude)
				
			for GRTVertex1 in self.Truth_GRTVertices.Vtx: # Can loop over truth for comparison
				for GRTParticle1 in self.RTTools.getParticles(GRTVertex1):
					
					if (GRTParticle1.pdg == ParticleCodes.Delta1Hadron):
						
						DeltaEnergy = GRTParticle1.momentum[3] * 1000 #GeV->MeV
						DeltaMomentumTrue = ThreeVector.ThreeVector(GRTParticle1.momentum[0], GRTParticle1.momentum[1], GRTParticle1.momentum[2])
												
						DeltaMomentumMagnitudeTrue = DeltaMomentumTrue.M() * 1000
						
						self.ROOTFile1.Histograms["Truth_Delta1Hadron_Energy"].Fill(DeltaEnergy)
						self.ROOTFile1.Histograms["Truth_Delta1Hadron_MomentumModulus"].Fill(DeltaMomentumMagnitudeTrue)

	
def SubDetectorReorder(InputDetectorNumber):#Reorders the detector number labels into the order in which an incoming neutrino sees them
											# TPC1 -> FGD1 -> TPC2 -> FGD2 -> TPC3
	if (InputDetectorNumber == 4):# TPC1: 1 -> 1 , FGD1: 4 -> 2
		OutputDetectorNumber = 2
	elif (InputDetectorNumber == 2):#TPC2: 2 -> 3
		OutputDetectorNumber = 3
	elif (InputDetectorNumber == 5):#FGD2: 5 -> 4
		OutputDetectorNumber = 4
	elif (InputDetectorNumber == 3):#TPC3: 3 -> 5
		OutputDetectorNumber = 5
	else:#Ignoring the PIDs reconstructed in the ECal and SMRD and Tracker ECal
		OutputDetectorNumber = None
					
	return OutputDetectorNumber
	
	
def FileNameGenerator(): # Generates a unique file name based on current time (without file extension)

	FolderName = Now.strftime("%Y/%m/%d/")
	FileName = Now.strftime("%Y-%m-%d-%H-%M-%S")
	
	return FolderName , FileName
	
def FilePathGenerator(Subfolder,Extension):
	
	(FolderName, FileName) = FileNameGenerator()
		
	FileLocation = DataLocation + FolderName + Subfolder
	
	if (not os.path.exists(FileLocation)):#Found from http://stackoverflow.com/questions/1274405/how-to-create-new-folder
		os.makedirs(FileLocation)#Makes the file directory if it doesn't already exist
		
	FilePath = FileLocation+FileName+Extension
	
	return FilePath
		
def ListFileCreator(input_filename_list):
		
	(FolderName,FileName) = FileNameGenerator()
	
	FileLocation = DataLocation+FolderName+"Input List/"

	try:
		ExistingFileList = os.listdir(FileLocation)
		ExistingFileNumber = len(ExistingFileList)
	except:
		ExistingFileNumber = 0

	if (ExistingFileNumber > 0):
		LastFile = open(FileLocation+ExistingFileList[ExistingFileNumber-1])
		
		LastFileList = LastFile.read().splitlines()
			
		LastFile.close()
	
		if (LastFileList != input_filename_list):
			
			output_ListFilename = FilePathGenerator("Input List/",".list")#For archiving the .list file used
	
			OutputListFile = open(output_ListFilename,"w")
	
			for ListCounter in xrange(len(input_filename_list)):
				OutputListFile.write(str(input_filename_list[ListCounter])+"\n")
	
	else:
	
		output_ListFilename = FilePathGenerator("Input List/",".list")#For archiving the .list file used
	
		OutputListFile = open(output_ListFilename,"w")
	
		for ListCounter in xrange(len(input_filename_list)):
			OutputListFile.write(str(input_filename_list[ListCounter])+"\n")
		
def main():
	
	NumberOfEventsToRead = 0
	DefaultNumberOfEventsToRead = 200
	
	InputFileLocator = ""
	DefaultInputFile1Locator = "Production5_Analysis_Purified_Short.list"
	DefaultInputFile2Locator = "Production5_Analysis_Purified_Long.list"
	DefaultInputFile3Locator = "Production5_Analysis_Unpurified_Short.list"
	DefaultInputFile4Locator = "Production5_Analysis_Unpurified_Long.list"
	DefaultInputFile5Locator = "Production5_Analysis_Unpurified_Short_2.list"
	
	if ( len(sys.argv) == 1 ):
		
		NumberOfEventsToRead = DefaultNumberOfEventsToRead
		InputFileLocator = DefaultInputFile1Locator
		
	elif ( len(sys.argv) == 2 ):
		
		NumberOfEventsToRead = int(sys.argv[1])
		InputFileLocator = DefaultInputFile1Locator
		
	elif ( len(sys.argv) == 3 ):
		
		NumberOfEventsToRead = int(sys.argv[1])
		
		if (int(sys.argv[2]) == 1):
			InputFileLocator = DefaultInputFile1Locator
		elif (int(sys.argv[2]) == 2):
			InputFileLocator = DefaultInputFile2Locator
		elif (int(sys.argv[2]) == 3):
			InputFileLocator = DefaultInputFile3Locator
		elif (int(sys.argv[2]) == 4):
			InputFileLocator = DefaultInputFile4Locator
		elif (int(sys.argv[2]) == 5):
			InputFileLocator = DefaultInputFile5Locator
		else:
			InputFileLocator = DefaultInputFile1Locator
		
	else:
		
		NumberOfEventsToRead = DefaultNumberOfEventsToRead
		InputFileLocator = DefaultInputFile1Locator
	
				
	libraries.load("nd280/nd280.so")
			
	#input_filename_list = ( glob.glob( sys.argv[1]+"*" ) )
	
	FileList = open(InputFileLocator)
	
	InputFileLocatorList = FileList.read().splitlines()
		
	OutputROOTFileLocator = FilePathGenerator("ROOT/", ".root")
	OutputTextFileLocator = FilePathGenerator("Text/", ".txt")
	
	ListFileCreator(InputFileLocatorList)
	
	Analysis1 = Analysis(InputFileLocatorList, OutputROOTFileLocator, OutputTextFileLocator)
	Analysis1.Analyse(NumberOfEventsToRead)
	

if __name__ == "__main__":
	main()
