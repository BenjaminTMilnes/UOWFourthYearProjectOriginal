import libraries
import glob
import sys
import RooTrackerTools
import math
import datetime
import os
import array
import ROOT

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
import StackedHistogram

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
		
		sys.stdout = DataWriter.DataWriter(self.OutputTextFileLocator)
		
		self.LoadInputFiles()
	
	
		self.TruthStatistics = StatisticsCollection.StatisticsCollection("Truth Statistics")
				
		self.TruthStatistics.NewStatistic("NEvents", "Number of Events", 0)
		self.TruthStatistics.NewStatistic("NVertices", "Number of Vertices", 0)
		self.TruthStatistics.NewStatistic("NDeltaToProtonPhoton", "Number of Delta to Proton-Photon Events", 0)
		self.TruthStatistics.NewStatistic("NDeltaToProtonPhotonCC", "Number of Delta to Proton-Photon Charged-Current Events", 0)
		self.TruthStatistics.NewStatistic("NDeltaToProtonPhotonNC", "Number of Delta to Proton-Photon Neutral-Current Events", 0)		
				
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
		
		self.FGD1Fiducial = ThreeDimensionalObject.ThreeDimensionalObject(-874.51, 874.51, -819.51, 929.51, 136.875, 446.955)#NB: in email he said 1446.955 but i am guessing this is typo
		self.FGD2Fiducial = ThreeDimensionalObject.ThreeDimensionalObject(-874.51, 874.51, -819.51, 929.51, 1481.5, 1810)
		
		self.ROOTFile1 = ROOTFile.ROOTFile(self.OutputROOTFileLocator)
		self.ROOTFile1.Open()
		
		self.ROOTFile1.NewHistogram1D("Reconstructed_Delta1Hadron_Energy", "Energy of the Unknown Particle which created the Reconstructed Proton and Photon", "", "", 100, 0, 5000)
		self.ROOTFile1.NewHistogram1D("Reconstructed_Delta1Hadron_MomentumModulus", "Momentum Modulus of the Unknown Particle which created the Reconstructed Proton and Photon", "", "", 100, 0, 3000)
		self.ROOTFile1.NewHistogram1D("Reconstructed_Delta1Hadron_Mass", "Mass of the Unknown Particle which created the Reconstructed Proton and Photon", "", "", 100, 0, 3000)
		
		self.ROOTFile1.NewHistogram1D("Truth_Delta1Hadron_Energy", "Energy of the Delta 1 Hadrons", "", "", 100, 0, 5000)
		self.ROOTFile1.NewHistogram1D("Truth_Delta1Hadron_MomentumModulus", "Energy of the Delta 1 Hadrons", "", "", 100, 0, 3000)
		
		self.ReconProtonTrueEnergy=StackedHistogram.StackedHistogram("Recon_Proton_True_Energy", "True energy of particles reconstructed as protons", 0.7, 0.65, 0.86, 0.88, "Energy (GeV)", "Number")

		self.ReconProtonTrueEnergy.NewHistogram1D("Proton_Recon:ProtonEnergyTrue", "True energy of correctly reconstructed protons", "", "", 100, 0, 5000, "Protons")
		self.ReconProtonTrueEnergy.NewHistogram1D("Proton_Recon:MuonEnergyTrue", "True energy of muons incorrectly reconstructed as protons", "", "", 100, 0, 5000, "Muons")
		self.ReconProtonTrueEnergy.NewHistogram1D("Proton_Recon:ElectronEnergyTrue", "True energy of electrons incorrectly reconstructed as protons", "", "", 100, 0, 5000, "Electrons")
		self.ReconProtonTrueEnergy.NewHistogram1D("Proton_Recon:AntiElectronEnergyTrue", "True energy of electrons incorrectly reconstructed as protons", "", "", 100, 0, 5000, "Anti-Electrons")
		
		self.ReconProtonReconMomentum=StackedHistogram.StackedHistogram("Recon_Proton_Recon_Momentum", "Reconstructed momentum of particles reconstructed as protons", 0.7, 0.65, 0.86, 0.88, "Momentum (GeV)", "Number")
		
		self.ReconProtonReconMomentum.NewHistogram1D("Proton_Recon:ProtonMomentumRecon", "Recon momentum of correctly reconstructed protons", "", "", 100, 0, 5000, "Protons")
		self.ReconProtonReconMomentum.NewHistogram1D("Proton_Recon:MuonMomentumRecon", "Recon momentum of muons incorrectly reconstructed as protons", "", "", 100, 0, 5000, "Muons")
		self.ReconProtonReconMomentum.NewHistogram1D("Proton_Recon:ElectronMomentumRecon", "Recon momentum of electrons incorrectly reconstructed as protons", "", "", 100, 0, 5000, "Electrons")
		self.ReconProtonReconMomentum.NewHistogram1D("Proton_Recon:AntiElectronMomentumRecon", "Recon momentum of electrons incorrectly reconstructed as protons", "", "", 100, 0, 5000, "Anti-Electrons")
	
		self.ROOTFile1.NewHistogram1D("Recon_Truth_Proton_Momentum", "Recon momentum minus truth momentum for PIDs reconstructed as protons", "", "", 100, -500, 500)
		self.ROOTFile1.NewHistogram1D("Truth_Proton_Momentum", "Truth momentum for PIDs reconstructed as protons", "", "", 100, 0, 5000)
		
		print TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine, TextConstants.LineSeparator
		print "Reading", n, "Events"
		print TextConstants.LineSeparator
								
		n = min(n, self.BasicInformation.GetEntries())
		
		for i in range(n):
			for module in self.Modules:
				module.GetEntry(i)
			
			EventInFGD=False
				
			for GRTVertex1 in self.Truth_GRTVertices.Vtx:
				inFGDX = (GRTVertex1.EvtVtx[0] >= self.FGD1Fiducial.X1 and GRTVertex1.EvtVtx[0] <= self.FGD1Fiducial.X2)
				inFGDY = (GRTVertex1.EvtVtx[1] >= self.FGD1Fiducial.Y1 and GRTVertex1.EvtVtx[1] <= self.FGD1Fiducial.Y2)
				inFGDZ = (GRTVertex1.EvtVtx[2] >= self.FGD1Fiducial.Z1 and GRTVertex1.EvtVtx[2] <= self.FGD1Fiducial.Z2) or (GRTVertex1.EvtVtx[2] >= self.FGD2Fiducial.Z1 and GRTVertex1.EvtVtx[2] <= self.FGD2Fiducial.Z2)
				
				if(inFGDX and inFGDY and inFGDZ):
					EventInFGD=True

			ProgressMeter(i,n)

			if(EventInFGD):
				self.runEvent()

		self.ReconProtonTrueEnergy.AutoPrepare("f")
		
		self.ROOTFile1.NewStackedHistogramCanvas("Recon_Proton_True_Energy", self.ReconProtonTrueEnergy.StackedHistogramCanvas("Recon_Proton_True_Energy", "Canvas of true energies of reconstructed proton-like tracks", 700, 500))
		
		self.ReconProtonReconMomentum.AutoPrepare("f")
		
		self.ROOTFile1.NewStackedHistogramCanvas("Recon_Proton_Recon_Momentum", self.ReconProtonReconMomentum.StackedHistogramCanvas("Recon_Proton_Recon_Momentum", "Canvas of reconstructed momenta of reconstructed proton-like tracks", 700, 500))
		
				
		################################ Cuts
		
		self.SelectionCriteriaList[0].EventsRemaining = self.TruthStatistics.Statistics["NEvents"].Quantity

		CutNumber = len(self.SelectionCriteriaList)
		
		for CriteriaListCounter in xrange(CutNumber):
			
			try:
				self.SelectionCriteriaList[CriteriaListCounter].AbsoluteEfficiency = float(self.SelectionCriteriaList[CriteriaListCounter].EventsRemaining)/float(self.SelectionCriteriaList[0].EventsRemaining)
			except:
				self.SelectionCriteriaList[CriteriaListCounter].AbsoluteEfficiency = 1
			
			if (CriteriaListCounter > 0):
				
				try:
					self.SelectionCriteriaList[CriteriaListCounter].RelativeEfficiency = float(self.SelectionCriteriaList[CriteriaListCounter].EventsRemaining)/float(self.SelectionCriteriaList[CriteriaListCounter-1].EventsRemaining)
				except:
					self.SelectionCriteriaList[CriteriaListCounter].RelativeEfficiency = 1
				
			try:
				self.SelectionCriteriaList[CriteriaListCounter].Purity = float(self.SelectionCriteriaList[CriteriaListCounter].TrueDelta) / float(self.SelectionCriteriaList[CriteriaListCounter].EventsRemaining)
			except:
				self.SelectionCriteriaList[CriteriaListCounter].Purity = 1

		self.SelectionCriteriaList[0].TrueDelta = self.TruthStatistics.Statistics["NDeltaToProtonPhoton"].Quantity
		
		try:
			self.SelectionCriteriaList[0].Purity = float(self.SelectionCriteriaList[0].TrueDelta)/float(self.SelectionCriteriaList[0].EventsRemaining)
		except:
			self.SelectionCriteriaList[0].Purity = 1
			
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
		
		self.CutPurity=StackedHistogram.StackedHistogram("Cut_Purity", "Constituent Processes for the Events after every Selection",0.7,0.65,0.86,0.88, "Cut Number", "Events Remaining")
		
		if(self.SelectionCriteriaList[0].TrueDelta>0):
			self.CutPurity.NewHistogram1D("Delta_True", "True Delta->p gamma interactions for each cut", "", "",CutNumber,0,CutNumber, "Delta -> p gamma")
			
		if(self.SelectionCriteriaList[0].Pi0MesonDelta>0):
			self.CutPurity.NewHistogram1D("Delta1HadronToProtonPi0Meson", "Number of Delta 1 Hadrons to Protons and Pi 0 Mesons", "", "",CutNumber,0,CutNumber, "Delta -> p pi0")
		
		if(self.SelectionCriteriaList[0].OtherResonance>0):
			self.CutPurity.NewHistogram1D("Other_Resonance_True", "True other resonances interactions for each cut", "", "",CutNumber,0,CutNumber, "Other Resonance")
		
		if(self.SelectionCriteriaList[0].QESInteraction>0):
			self.CutPurity.NewHistogram1D("QES_True", "True QES interactions for each cut", "", "",CutNumber,0,CutNumber, "QES Interaction")
		
		if(self.SelectionCriteriaList[0].DISInteraction>0):
			self.CutPurity.NewHistogram1D("DIS_True", "True DIS interactions for each cut", "", "",CutNumber,0,CutNumber, "DIS Interaction")
		
		if(self.SelectionCriteriaList[0].COHInteraction>0):
			self.CutPurity.NewHistogram1D("COH_True", "True COH interactions for each cut", "", "",CutNumber,0,CutNumber, "COH Interaction")

		for CutCounter in xrange(len(self.SelectionCriteriaList)):
			for FillCounter in xrange(self.SelectionCriteriaList[CutCounter].TrueDelta):
				self.CutPurity.HistogramDictionary["Delta_True"].Histogram.Fill(CutCounter)
			for FillCounter in xrange(self.SelectionCriteriaList[CutCounter].Pi0MesonDelta):
				self.CutPurity.HistogramDictionary["Delta1HadronToProtonPi0Meson"].Histogram.Fill(CutCounter)
			for FillCounter in xrange(self.SelectionCriteriaList[CutCounter].OtherResonance):
				self.CutPurity.HistogramDictionary["Other_Resonance_True"].Histogram.Fill(CutCounter)
			for FillCounter in xrange(self.SelectionCriteriaList[CutCounter].QESInteraction):
				self.CutPurity.HistogramDictionary["QES_True"].Histogram.Fill(CutCounter)
			for FillCounter in xrange(self.SelectionCriteriaList[CutCounter].DISInteraction):
				self.CutPurity.HistogramDictionary["DIS_True"].Histogram.Fill(CutCounter)
			for FillCounter in xrange(self.SelectionCriteriaList[CutCounter].COHInteraction):
				self.CutPurity.HistogramDictionary["COH_True"].Histogram.Fill(CutCounter)

		self.CutPurity.AutoPrepare("f")
		
		self.ROOTFile1.NewStackedHistogramCanvas("Cut_Purity_Canvas", self.CutPurity.StackedHistogramCanvas("Cut_Purity_Canvas", "Canvas of Cut Purity", 700, 500))
			
		###############

		print TextConstants.NewLine
		
		print "First Cut: Every event with at least one PID"
		print "Events remaining:" , str(self.SelectionCriteriaList[1].EventsRemaining)
		
		print "Second Cut: Every event with at least one PID that has at least 18 nodes"
		print "Events remaining:" , str(self.SelectionCriteriaList[2].EventsRemaining)
		
		print "Third Cut: Of the second cut, the events that have at least one proton identified PID"
		print "Events remaining:" , str(self.SelectionCriteriaList[3].EventsRemaining)
		
		print "Fourth Cut: Of the second cut, the events that have only one proton identified PID"
		print "Events remaining:" , str(self.SelectionCriteriaList[4].EventsRemaining)
		
		print "Fifth Cut: Of the fourth cut, the events where the proton track is the earliest (in Z) start position in the detector"
		print "Events remaining:" , str(self.SelectionCriteriaList[5].EventsRemaining)
		
		print "Fourth Cut: Of the fifth cut, the events where at least one ECal cluster was recorded"
		print "Events remaining:" , str(self.SelectionCriteriaList[6].EventsRemaining)
		
		print TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine
	
		print self.TruthStatistics.ToText()
		print self.ReconstructedStatistics.ToText()
		print self.EfficiencyStatistics.ToText()
	
		del sys.stdout#Closes .txt file and returns to printing only to console
	
		self.ROOTFile1.Close()
		
	
	def runEvent(self):
	
		self.TruthStatistics.Statistics["NEvents"].Quantity+=1
	
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

			if (Delta1HadronToProtonPi0MesonInteraction):
				Delta1HadronToProtonPi0MesonEvent = True

		################################ Recon ###########################

		NPIDs=self.Reconstructed_Global.NPIDs#Number of reconstructed PIDs

		if (NPIDs > 0):
			
			self.ReconstructedStatistics.Statistics["NEventsWithRPID"].Quantity += 1

		ProtonCorrectlyReconstructed = False
	
		ProtonEnergyList = []#List of energies of reconstructed proton PIDs
		
		ProtonMomentumListX = []#List of momenta of reconstructed proton PIDs
		ProtonMomentumListY = []
		ProtonMomentumListZ = []
		PIDParticleList = []
		PIDObjectList = []
		
		PIDNumber=0
		TPCValidPIDNumber=0
		
		for PID in self.Reconstructed_Global.PIDs:#Loop over the PIDs if they exist
			
			PIDNumber+=1
								
			SuitableTPCNodeNumber = False
										
			for TPCCounter in xrange(PID.NTPCs):#Loop over TPC PIDs
				TPCTrack = PID.TPC[TPCCounter]
						
				if (TPCTrack.NNodes>18):
					SuitableTPCNodeNumber = True		
					
			if (SuitableTPCNodeNumber):
				
				TPCValidPIDNumber+=1	
					
				if (len(PID.ParticleIds)>0):
					
					PIDObject = PIDParticle.PIDParticle()
					
					PIDObject.ReconParticleID = PID.ParticleIds[0]
					PIDObject.ReconParticleIDWeight = PID.PIDWeights[0]
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
				self.ReconProtonTrueEnergy.HistogramDictionary["Proton_Recon:ProtonEnergyTrue"].Histogram.Fill(PIDObject1.TrueEnergy)
				self.ReconProtonReconMomentum.HistogramDictionary["Proton_Recon:ProtonMomentumRecon"].Histogram.Fill(PIDObject1.ReconFrontMomentum)
				
			elif (PIDObject1.ReconParticleID == ParticleCodes.Proton and PIDObject1.TrueParticleID == ParticleCodes.MuLepton):
				self.ReconProtonTrueEnergy.HistogramDictionary["Proton_Recon:MuonEnergyTrue"].Histogram.Fill(PIDObject1.TrueEnergy)
				self.ReconProtonReconMomentum.HistogramDictionary["Proton_Recon:MuonMomentumRecon"].Histogram.Fill(PIDObject1.ReconFrontMomentum)
				
			elif (PIDObject1.ReconParticleID == ParticleCodes.Proton and PIDObject1.TrueParticleID == ParticleCodes.Electron):
				self.ReconProtonTrueEnergy.HistogramDictionary["Proton_Recon:ElectronEnergyTrue"].Histogram.Fill(PIDObject1.TrueEnergy)
				self.ReconProtonReconMomentum.HistogramDictionary["Proton_Recon:ElectronMomentumRecon"].Histogram.Fill(PIDObject1.ReconFrontMomentum)
				
			elif (PIDObject1.ReconParticleID == ParticleCodes.Proton and PIDObject1.TrueParticleID == ParticleCodes.AntiElectron):
				self.ReconProtonTrueEnergy.HistogramDictionary["Proton_Recon:AntiElectronEnergyTrue"].Histogram.Fill(PIDObject1.TrueEnergy)
				self.ReconProtonReconMomentum.HistogramDictionary["Proton_Recon:AntiElectronMomentumRecon"].Histogram.Fill(PIDObject1.ReconFrontMomentum)
		
		if (ReconstructedProtonTrackNumber == 1):
			
			for PIDObject1 in PIDObjectList:
				
				if (PIDObject1.ReconParticleID == ParticleCodes.Proton):#Looking for reconstructed proton track
					ProtonTrackFrontPositionZ=PIDObject1.ReconFrontPositionZ
					
			SingleProtonTrackFirst=True
					
			for PIDObject1 in PIDObjectList:
				
				if (PIDObject1.ReconFrontPositionZ < ProtonTrackFrontPositionZ):
					
					SingleProtonTrackFirst=False
					
		else:
			SingleProtonTrackFirst = False
		
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
		
		Criteria.append(True)#Zeroeth Cut
		
		if (PIDNumber > 0):
			Criteria.append(True)
		else:
			Criteria.append(False)
		
		if (TPCValidPIDNumber > 0 and Criteria[0]):
			Criteria.append(True)			
		else:
			Criteria.append(False)
					
		if (ReconstructedProtonTrackNumber > 0 and Criteria[1]):
			Criteria.append(True)
		else:
			Criteria.append(False)
		
		if (ReconstructedProtonTrackNumber == 1 and Criteria[2]):
			Criteria.append(True)
		else:
			Criteria.append(False)
		
		if (SingleProtonTrackFirst and Criteria[3]):
			Criteria.append(True)
		else:
			Criteria.append(False)
		
		if (NTrackerECalRecon > 0 and Criteria[4]):
			Criteria.append(True)
		else:
			Criteria.append(False)
		
		CutNumber = len(Criteria)
		
		if (self.TruthStatistics.Statistics["NEvents"].Quantity == 1):
			for CutCounter in xrange(CutNumber):
				
				SelectionCriterion1 = SelectionCriteria.SelectionCriteria()
				
				self.SelectionCriteriaList.append(SelectionCriterion1)
										
					
		for CutCounter in xrange(CutNumber):
			if (Criteria[CutCounter]):
				self.SelectionCriteriaList[CutCounter].EventsRemaining += 1
				if (DeltaPGammaEvent):
					self.SelectionCriteriaList[CutCounter].TrueDelta += 1
				elif (Delta1HadronToProtonPi0MesonEvent):
					self.SelectionCriteriaList[CutCounter].Pi0MesonDelta += 1
				elif (InteractionType == "RES" and not DeltaPGammaEvent and not Delta1HadronToProtonPi0MesonEvent):
					self.SelectionCriteriaList[CutCounter].OtherResonance += 1
				elif (InteractionType == "QES"):
					self.SelectionCriteriaList[CutCounter].QESInteraction += 1
				elif (InteractionType == "DIS"):
					self.SelectionCriteriaList[CutCounter].DISInteraction += 1
				elif (InteractionType == "COH"):
					self.SelectionCriteriaList[CutCounter].COHInteraction += 1
			
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

def ProgressMeter(Counter, EndCounter):
	
	if (Counter == 0):
		print "Analysis progress:"
		print "0 %"
	
	if(EndCounter>100):
	
		ProgressPercentageCurrent=100*float(Counter+1)/float(EndCounter)
		ProgressPercentagePrevious=100*float(Counter)/float(EndCounter)
	
		RoundedProgressPercentageCurrent=math.floor(ProgressPercentageCurrent)
		RoundedProgressPercentagePrevious=math.floor(ProgressPercentagePrevious)
	
		if(RoundedProgressPercentageCurrent != RoundedProgressPercentagePrevious):

			print "%d" % RoundedProgressPercentageCurrent + " %"
			
	if(Counter == EndCounter-1):
		print "Analysis of ROOT files complete."


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
