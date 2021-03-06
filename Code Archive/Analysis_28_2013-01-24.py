import libraries
import glob
import sys
import RooTrackerTools
import math
import datetime
import os
import array
import time
import ROOT

import EventCodeDeconstructor
import DataWriter
import TheoreticalParticle
import ParticleCodes
import PIDParticle
import SelectionStatistics

import ROOTFile
import TextConstants
import PhysicalConstants
import StatisticsCollection
import StackedHistogram
import ReconstructedParticle
import NumericalCuts

import ThreeVector
import ThreeDimensionalObject

import FourVector

import ProgressMeter

import CommandLineDeconstructor
import FileAdministrator

import DataCollection
import Simulation

Now = datetime.datetime.now()
DataLocation = "/storage/epp2/phujce/Final Year Project/Main/Data Archive/"

class Analysis:
	
	def __init__(self, InputFileLocatorList, OutputROOTFileLocator, OutputTextFileLocator):
		
		self.InputFileLocatorList = InputFileLocatorList
		self.OutputROOTFileLocator = OutputROOTFileLocator
		self.OutputTextFileLocator = OutputTextFileLocator
		
		self.Histograms = {}
		self.DataCollections = []
		self.Modules = []
		
		self.BasicInformation = self.LoadModule("HeaderDir/BasicHeader")
		
		self.Truth_GRTVertices = self.LoadModule("TruthDir/GRooTrackerVtx")
		self.Truth_Vertices = self.LoadModule("TruthDir/Vertices")
		self.Truth_Trajectories = self.LoadModule("TruthDir/Trajectories")
		
		self.Reconstructed_Global = self.LoadModule("ReconDir/Global")
		self.Reconstructed_TEC = self.LoadModule("ReconDir/TrackerECal")
		
		self.RTTools = RooTrackerTools.RooTrackerTools()
		
		self.EventCodeDeconstructor1 = EventCodeDeconstructor.EventCodeDeconstructor()
	
		self.SelectionStatisticsList = []
		
		self.InputTimeTest = False
		self.SelectBackgroundEvents = False
		
		self.BackgroundEventNumbers = []
		self.BackgroundPiMesonEventNumbers = []
		
		self.EventCollection1 = Simulation.EventCollection()
					
	
	def LoadInputFiles(self, DesiredEventNumber):		
		# Adds each file in the list of input file names to each module we want to use		

		for FileLocator in self.InputFileLocatorList:
			
			if (self.Modules[0].GetEntries() <= DesiredEventNumber):
			
				for Module in self.Modules:
					Module.Add(FileLocator)
					
			else:
				break
				
		MaximumEventNumber = Module.GetEntries()
				
		return MaximumEventNumber
		
	def LoadModule(self, Module_Reference):		
		# Load all the appropriate modules from the oaAnalysis file that we have defined	
		
		#DataCollection1 = DataCollection.DataCollection(Module_Reference)
		#self.DataCollections.append(DataCollection1)
		
		#return DataCollection1
		
		Module = ROOT.TChain(Module_Reference)
		self.Modules.append(Module)
		
		return Module
	
		
	def Analyse(self, DesiredEventNumber = 999999999):

		sys.stdout = DataWriter.DataWriter(self.OutputTextFileLocator)
		
		MaximumEventNumber = self.LoadInputFiles(DesiredEventNumber)

		self.FGD1 = ThreeDimensionalObject.ThreeDimensionalObject(-832.2, 832.2, -777.2, 887.2, 123.45, 446.95)
		self.FGD2 = ThreeDimensionalObject.ThreeDimensionalObject(-832.2, 832.2, -777.2, 887.2, 1481.45, 1807.95)
		
		self.FGD1Fiducial = ThreeDimensionalObject.ThreeDimensionalObject(-874.51, 874.51, -819.51, 929.51, 136.875, 446.955)#NB: in email he said 1446.955 but i am guessing this is typo
		self.FGD2Fiducial = ThreeDimensionalObject.ThreeDimensionalObject(-874.51, 874.51, -819.51, 929.51, 1481.5, 1810)
		
	
	
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
		self.ReconstructedStatistics.NewStatistic("NEventsWithTECCAndCRProtonWithin10D", "Number of Events with at least one Tracker EC Cluster and one Correctly Reconstructed Proton Track where the Photon Direction points to within 10 Degrees of the Proton Track Start", 0)	
		self.ReconstructedStatistics.NewStatistic("NEventsWithTECCAndCRProtonWithin10DWithin500ns", "Number of Events with at least one Tracker EC Cluster and one Correctly Reconstructed Proton Track where the Photon Direction points to within 10 Degrees of the Proton Track Start and where the timing is less than 500ns", 0)	
	
		self.ROOTFile1 = ROOTFile.ROOTFile(self.OutputROOTFileLocator)
		self.ROOTFile1.Open()
		
		self.ROOTFile1.NewHistogram1D("Reconstructed_Delta1Baryon_Energy", "Energy of the Unknown Particle which created the Reconstructed Proton and Photon", "Energy (GeV)", "Number", 100, 0, 5000, "DeltaBaryon/Recon/")
		self.ROOTFile1.NewHistogram1D("Reconstructed_Delta1Baryon_MomentumModulus", "Momentum Modulus of the Unknown Particle which created the Reconstructed Proton and Photon", "Momentum (GeV)", "Number", 100, 0, 3000, "DeltaBaryon/Recon/")
		self.ROOTFile1.NewHistogram1D("Reconstructed_Delta1Baryon_Mass", "Mass of the Unknown Particle which created the Reconstructed Proton and Photon", "Mass (GeV)", "Number", 100, 0, 3000, "DeltaBaryon/Recon/")
		
		self.ROOTFile1.NewHistogram1D("Reconstructed_Delta1Baryon_Energy_TimeSeparated", "Energy of the Unknown Particle which created the Reconstructed Proton and Photon (Time Separated)", "Energy (GeV)", "Number", 100, 0, 5000, "DeltaBaryon/Recon/")
		self.ROOTFile1.NewHistogram1D("Reconstructed_Delta1Baryon_MomentumModulus_TimeSeparated", "Momentum Modulus of the Unknown Particle which created the Reconstructed Proton and Photon (Time Separated)", "Momentum (GeV)", "Number", 100, 0, 3000, "DeltaBaryon/Recon/")
		self.ROOTFile1.NewHistogram1D("Reconstructed_Delta1Baryon_Mass_TimeSeparated", "Mass of the Unknown Particle which created the Reconstructed Proton and Photon (Time Separated)", "Mass (GeV)", "Number", 100, 0, 3000, "DeltaBaryon/Recon/")
		
		self.ROOTFile1.NewHistogram1D("Truth_Delta1Baryon_Energy", "Energy of the Delta 1 Baryons", "Energy (GeV)", "Number", 100, 0, 5000, "DeltaBaryon/Truth/")
		self.ROOTFile1.NewHistogram1D("Truth_Delta1Baryon_MomentumModulus", "Momentum of the Delta 1 Baryons", "Momentum (GeV)", "Number", 100, 0, 3000, "DeltaBaryon/Truth/")
		self.ROOTFile1.NewHistogram1D("Truth_Delta1Baryon_Mass", "Mass of the Delta 1 Baryons", "Mass (GeV)", "Number", 100, 0, 3000, "DeltaBaryon/Truth/")
		
		self.ReconProtonTrueEnergy=StackedHistogram.StackedHistogram("Recon_Proton_True_Energy", "True energy of particles reconstructed as protons", 0.7, 0.65, 0.86, 0.88, "Energy (GeV)", "Number")

		self.ReconProtonTrueEnergy.NewHistogram1D("Proton_Recon:ProtonEnergyTrue", "True energy of correctly reconstructed protons", "Energy (GeV)", "Number", 100, 0, 5000, "Protons", "Proton/Truth/Energy/Constituent Histograms")
		self.ReconProtonTrueEnergy.NewHistogram1D("Proton_Recon:MuonEnergyTrue", "True energy of muons incorrectly reconstructed as protons", "Energy (GeV)", "Number", 100, 0, 5000, "Muons", "Proton/Truth/Energy/Constituent Histograms")
		self.ReconProtonTrueEnergy.NewHistogram1D("Proton_Recon:ElectronEnergyTrue", "True energy of electrons incorrectly reconstructed as protons", "Energy (GeV)", "Number", 100, 0, 5000, "Electrons", "Proton/Truth/Energy/Constituent Histograms")
		self.ReconProtonTrueEnergy.NewHistogram1D("Proton_Recon:AntiElectronEnergyTrue", "True energy of electrons incorrectly reconstructed as protons", "Energy (GeV)", "Number", 100, 0, 5000, "Anti-Electrons", "Proton/Truth/Energy/Constituent Histograms")
		
		self.ReconProtonReconMomentum=StackedHistogram.StackedHistogram("Recon_Proton_Recon_Momentum", "Reconstructed momentum of particles reconstructed as protons", 0.7, 0.65, 0.86, 0.88, "Momentum (GeV)", "Number")
		
		self.ReconProtonReconMomentum.NewHistogram1D("Proton_Recon:ProtonMomentumRecon", "Recon momentum of correctly reconstructed protons", "Momentum (GeV)", "Number", 100, 0, 5000, "Protons", "Proton/Recon/Momentum/Constituent Histograms")
		self.ReconProtonReconMomentum.NewHistogram1D("Proton_Recon:MuonMomentumRecon", "Recon momentum of muons incorrectly reconstructed as protons", "Momentum (GeV)", "Number", 100, 0, 5000, "Muons", "Proton/Recon/Momentum/Constituent Histograms")
		self.ReconProtonReconMomentum.NewHistogram1D("Proton_Recon:ElectronMomentumRecon", "Recon momentum of electrons incorrectly reconstructed as protons", "Momentum (GeV)", "Number", 100, 0, 5000, "Electrons", "Proton/Recon/Momentum/Constituent Histograms")
		self.ReconProtonReconMomentum.NewHistogram1D("Proton_Recon:AntiElectronMomentumRecon", "Recon momentum of electrons incorrectly reconstructed as protons", "Momentum (GeV)", "Number", 100, 0, 5000, "Anti-Electrons", "Proton/Recon/Momentum/Constituent Histograms")
	
		self.ROOTFile1.NewHistogram1D("Recon_Truth_Proton_Momentum", "Recon momentum minus truth momentum for PIDs reconstructed as protons", "Momentum (GeV)", "Number", 100, -500, 500, "PIDs/Recon/Momentum")
		self.ROOTFile1.NewHistogram1D("Truth_Proton_Momentum", "Truth momentum for PIDs reconstructed as protons", "Momentum (GeV)", "Number", 100, 0, 5000, "PIDs/Truth/Momentum")
				
		self.ROOTFile1.NewHistogram1D("PhotonAngles", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position", "Angle", "Number", 100, 0, 180, "Photon/Recon/")
		self.ROOTFile1.NewHistogram1D("ProtonPhotonTimeSeparations", "Time Separation between the Reconstructed Proton Track and Photon EC Cluster", "Time Separation", "Number", 100, 0, 4000, "Photon/Recon/")
		
		self.ROOTFile1.NewHistogram1D("SelectedPhotonAngles", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position for the single proton and the single selected photon", "Angle", "Number", 100, -90, 90, "Photon/Recon/")
		
		self.ROOTFile1.NewHistogram1D("PID_Electron_Pull", "Electron pull for every PID", "Electron Pull", "Number", 100, -100, 100, "PIDs/Recon/Particle Pulls/")
		self.ROOTFile1.NewHistogram1D("PID_Kaon_Pull", "Kaon pull for every PID", "Kaon Pull", "Number", 100, -100, 100, "PIDs/Recon/Particle Pulls/")
		self.ROOTFile1.NewHistogram1D("PID_Muon_Pull", "Muon pull for every PID", "Muon Pull", "Number", 100, -100, 100, "PIDs/Recon/Particle Pulls/")
		self.ROOTFile1.NewHistogram1D("PID_Pion_Pull", "Pion pull for every PID", "Pion Pull", "Number", 100, -100, 100, "PIDs/Recon/Particle Pulls/")
		self.ROOTFile1.NewHistogram1D("PID_Proton_Pull", "Proton pull for every PID", "Proton Pull", "Number", 100, -100, 100, "PIDs/Recon/Particle Pulls/")
		
		self.ROOTFile1.NewHistogram2D("PID_Proton_Against_Muon_Pull", "Proton pull plotted against muon pull for every PID", "Proton Pull", "Muon Pull", 100, -100, 100, 100, -100, 100, "PIDs/Recon/Particle Pulls/")
		
		self.ROOTFile1.NewHistogram1D("Proton_PID_Electron_Pull", "Electron pull for all PIDs identified as proton-like", "Electron Pull", "Number", 100, -100, 100, "Proton/Recon/Particle Pulls/All Protons/")
		self.ROOTFile1.NewHistogram1D("Proton_PID_Kaon_Pull", "Kaon pull for all PIDs identified as proton-like", "Kaon Pull", "Number", 100, -100, 100, "Proton/Recon/Particle Pulls/All Protons/")
		self.ROOTFile1.NewHistogram1D("Proton_PID_Muon_Pull", "Muon pull for all PIDs identified as proton-like", "Muon Pull", "Number", 100, -100, 100, "Proton/Recon/Particle Pulls/All Protons/")
		self.ROOTFile1.NewHistogram1D("Proton_PID_Pion_Pull", "Pion pull for all PIDs identified as proton-like", "Pion Pull", "Number", 100, -100, 100, "Proton/Recon/Particle Pulls/All Protons/")
		self.ROOTFile1.NewHistogram1D("Proton_PID_Proton_Pull", "Proton pull for all PIDs identified as proton-like", "Proton Pull", "Number", 100, -100, 100, "Proton/Recon/Particle Pulls/All Protons/")
		
		self.ROOTFile1.NewHistogram2D("Proton_PID_Proton_Against_Muon_Pull", "Proton pull plotted against muon pull for all PIDs identified as proton-like", "Proton Pull", "Muon Pull", 100, -100, 100, 100, -100, 100, "Proton/Recon/Particle Pulls/All Protons/")
		self.ROOTFile1.HistogramDictionary["Proton_PID_Proton_Against_Muon_Pull"].Histogram.SetMarkerStyle(3)
		
		self.ROOTFile1.NewHistogram1D("Single_Proton_PID_Electron_Pull", "Electron pull for single PIDs identified as proton-like", "Electron Pull", "Number", 100, -100, 100, "Proton/Recon/Particle Pulls/Single Proton/")
		self.ROOTFile1.NewHistogram1D("Single_Proton_PID_Kaon_Pull", "Kaon pull for single PIDs identified as proton-like", "Kaon Pull", "Number", 100, -100, 100, "Proton/Recon/Particle Pulls/Single Proton/")
		self.ROOTFile1.NewHistogram1D("Single_Proton_PID_Muon_Pull", "Muon pull for single PIDs identified as proton-like", "Muon Pull", "Number", 100, -100, 100, "Proton/Recon/Particle Pulls/Single Proton/")
		self.ROOTFile1.NewHistogram1D("Single_Proton_PID_Pion_Pull", "Pion pull for single PIDs identified as proton-like", "Pion Pull", "Number", 100, -100, 100, "Proton/Recon/Particle Pulls/Single Proton/")
		self.ROOTFile1.NewHistogram1D("Single_Proton_PID_Proton_Pull", "Proton pull for single PIDs identified as proton-like", "Proton Pull", "Number", 100, -100, 100, "Proton/Recon/Particle Pulls/Single Proton/")
		
		self.ROOTFile1.NewHistogram2D("Single_Proton_PID_Proton_Against_Muon_Pull", "Proton pull plotted against muon pull for single PIDs identified as proton-like", "Proton Pull", "Muon Pull", 100, -100, 100, 100, -100, 100, "Proton/Recon/Particle Pulls/Single Proton/")
		self.ROOTFile1.HistogramDictionary["Single_Proton_PID_Proton_Against_Muon_Pull"].Histogram.SetMarkerStyle(3)
		
		self.FinalInvariantMass=StackedHistogram.StackedHistogram("Final_Invariant_Mass", "Invariant Mass of Delta Baryon after all cuts have been applied", 0.7, 0.65, 0.86, 0.88, "Mass (GeV)", "Number")
		self.InvariantMassAllECal=StackedHistogram.StackedHistogram("Invariant_Mass_All_ECal", "Invariant Mass of Delta Baryon from comparison of single photon to all ECals", 0.7, 0.65, 0.86, 0.88, "Mass (GeV)", "Number")
			
		EventNumber = min(MaximumEventNumber, DesiredEventNumber)

		print TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine, TextConstants.LineSeparator
		if (MaximumEventNumber < DesiredEventNumber):
			print "Warning: the number of events within the file list is less than the number of events requested."
		print "Reading", EventNumber, "Events"
		print TextConstants.LineSeparator
		
		ProgressMeter1 = ProgressMeter.ProgressMeter(EventNumber - 1)
		
		for i in range(EventNumber):
			for module in self.Modules:
				module.GetEntry(i)
			
			if (self.InputTimeTest == False):
			
				SuitableEvent = False
			
				for PID in self.Reconstructed_Global.PIDs:

					inFGDX = (PID.FrontPosition.X() >= self.FGD1Fiducial.X1 and PID.FrontPosition.X() <= self.FGD1Fiducial.X2)
					inFGDY = (PID.FrontPosition.Y() >= self.FGD1Fiducial.Y1 and PID.FrontPosition.Y() <= self.FGD1Fiducial.Y2)
					inFGDZ = (PID.FrontPosition.Z() >= self.FGD1Fiducial.Z1 and PID.FrontPosition.Z() <= self.FGD1Fiducial.Z2) or (PID.FrontPosition.Z() >= self.FGD2Fiducial.Z1 and PID.FrontPosition.Z() <= self.FGD2Fiducial.Z2)
				
					if(inFGDX and inFGDY and inFGDZ):
						SuitableEvent=True
	
				ProgressMeter1.Update(i)
	
				if (SuitableEvent):
					self.runEvent()


		self.ReconProtonTrueEnergy.AutoPrepare("f")
		
		self.ROOTFile1.NewStackedHistogramCanvas("Recon_Proton_True_Energy", self.ReconProtonTrueEnergy.StackedHistogramCanvas("Recon_Proton_True_Energy", "Canvas of true energies of reconstructed proton-like tracks", 700, 500), "Proton/Truth/Energy")
		
		self.ReconProtonTrueEnergy.DrawConstituentHistograms(self.ROOTFile1)
		
		
		self.ReconProtonReconMomentum.AutoPrepare("f")
		
		self.ROOTFile1.NewStackedHistogramCanvas("Recon_Proton_Recon_Momentum", self.ReconProtonReconMomentum.StackedHistogramCanvas("Recon_Proton_Recon_Momentum", "Canvas of reconstructed momenta of reconstructed proton-like tracks", 700, 500), "Proton/Recon/Momentum")
		
		self.ReconProtonReconMomentum.DrawConstituentHistograms(self.ROOTFile1)
					
		"""if(self.SelectionStatisticsList[0].TruthDelta>0):
				self.CutPurity.NewHistogram1D("Delta_True", "True Delta->p gamma interactions for each cut", "Cut Number", "Events Remaining",CutNumber,0,CutNumber, "Delta -> p gamma", "Cuts/Energy/Constituent Histograms/")
				
		if(self.SelectionStatisticsList[0].ReconstructedDelta>0):
			self.CutPurity.NewHistogram1D("Delta1BaryonToProtonPi0Meson", "Number of Delta 1 Baryons to Protons and Pi 0 Mesons", "Cut Number", "Events Remaining",CutNumber,0,CutNumber, "Delta -> p pi0", "Cuts/Energy/Constituent Histograms/")
		
		if(self.SelectionStatisticsList[0].OtherRPInteraction>0):
			self.CutPurity.NewHistogram1D("Other_Resonance_True", "True other resonances interactions for each cut", "Cut Number", "Events Remaining",CutNumber,0,CutNumber, "Other Resonance", "Cuts/Energy/Constituent Histograms/")
		
		if(self.SelectionStatisticsList[0].QSInteraction>0):
			self.CutPurity.NewHistogram1D("QES_True", "True QES interactions for each cut", "Cut Number", "Events Remaining",CutNumber,0,CutNumber, "QES Interaction", "Cuts/Energy/Constituent Histograms/")
		
		if(self.SelectionStatisticsList[0].DISInteraction>0):
			self.CutPurity.NewHistogram1D("DIS_True", "True DIS interactions for each cut", "Cut Number", "Events Remaining",CutNumber,0,CutNumber, "DIS Interaction", "Cuts/Energy/Constituent Histograms/")
		
		if(self.SelectionStatisticsList[0].CSInteraction>0):
			self.CutPurity.NewHistogram1D("COH_True", "True COH interactions for each cut", "Cut Number", "Events Remaining",CutNumber,0,CutNumber, "COH Interaction", "Cuts/Energy/Constituent Histograms/")"""
			
		if (self.InputTimeTest == False):
			
			################################ Cuts
			
			self.SelectionStatisticsList[0].EventsRemaining = self.TruthStatistics.Statistics["NEvents"].Quantity
	
			CutNumber = len(self.SelectionStatisticsList)
			
			PreviousEventsRemaining = self.SelectionStatisticsList[0].EventsRemaining
			
			for SelectionStatistics1 in self.SelectionStatisticsList:
				
				try:
					SelectionStatistics1.RelativeEfficiency = float(SelectionStatistics1.EventsRemaining) / float(PreviousEventsRemaining)
				except:
					SelectionStatistics1.RelativeEfficiency = 1
				
				try:
					SelectionStatistics1.AbsoluteEfficiency = float(SelectionStatistics1.EventsRemaining) / float(self.SelectionStatisticsList[0].EventsRemaining)
				except:
					SelectionStatistics1.AbsoluteEfficiency = 1
				
				try:
					SelectionStatistics1.Purity = float(SelectionStatistics1.TruthDelta) / float(SelectionStatistics1.EventsRemaining)
				except:
					SelectionStatistics1.Purity = 0
				
				try:
					SelectionStatistics1.PionPurity = float(SelectionStatistics1.ReconstructedDelta) / float(SelectionStatistics1.EventsRemaining)
				except:
					SelectionStatistics1.PionPurity = 0
					
				try:
					SelectionStatistics1.RPPurity = float(SelectionStatistics1.OtherRPInteraction) / float(SelectionStatistics1.EventsRemaining)
				except:
					SelectionStatistics1.RPPurity = 0
					
				try:
					SelectionStatistics1.QSPurity = float(SelectionStatistics1.QSInteraction) / float(SelectionStatistics1.EventsRemaining)
				except:
					SelectionStatistics1.QSPurity = 0
					
				try:
					SelectionStatistics1.ESPurity = float(SelectionStatistics1.ESInteraction) / float(SelectionStatistics1.EventsRemaining)
				except:
					SelectionStatistics1.ESPurity = 0
					
				try:
					SelectionStatistics1.DISPurity = float(SelectionStatistics1.DISInteraction) / float(SelectionStatistics1.EventsRemaining)
				except:
					SelectionStatistics1.DISPurity = 0
					
				try:
					SelectionStatistics1.CSPurity = float(SelectionStatistics1.CSInteraction) / float(SelectionStatistics1.EventsRemaining)
				except:
					SelectionStatistics1.CSPurity = 0
				
				try:
					SelectionStatistics1.OtherPurity = float(SelectionStatistics1.OtherInteraction) / float(SelectionStatistics1.EventsRemaining)
				except:
					SelectionStatistics1.OtherPurity = 0
				
				PreviousEventsRemaining = SelectionStatistics1.EventsRemaining
				
			self.SelectionStatisticsList[0].TruthDelta = self.TruthStatistics.Statistics["NDeltaToProtonPhoton"].Quantity
			
			try:
				self.SelectionStatisticsList[0].Purity = float(self.SelectionStatisticsList[0].TruthDelta)/float(self.SelectionStatisticsList[0].EventsRemaining)
			except:
				self.SelectionStatisticsList[0].Purity = 1
				
			self.SelectionStatisticsList[0].RelativeEfficiency = 1
			self.SelectionStatisticsList[0].AbsoluteEfficiency = 1
	
			############################# Graphs of cuts

			self.ROOTFile1.NewHistogram1D("AbsoluteEfficiency", "Absolute Efficiency for the Selections", "Selections", "Absolute Efficiency", CutNumber, 0, CutNumber, "Cuts/")

			self.ROOTFile1.HistogramDictionary["AbsoluteEfficiency"].Histogram.SetMarkerStyle(3)
			self.ROOTFile1.HistogramDictionary["AbsoluteEfficiency"].Histogram.SetOption("LP")
			self.ROOTFile1.HistogramDictionary["AbsoluteEfficiency"].Histogram.SetStats(0)

			for CriteriaListCounter in xrange(CutNumber):
				
				self.ROOTFile1.HistogramDictionary["AbsoluteEfficiency"].Histogram.Fill(CriteriaListCounter,self.SelectionStatisticsList[CriteriaListCounter].AbsoluteEfficiency)
				
			for CutCounter in xrange(len(self.SelectionStatisticsList)):
				
				if(CutCounter == 0):
					BinLabel = "Starting Events"
				else:
					BinLabel = "Criterion " + str(CutCounter)
				
				self.ROOTFile1.HistogramDictionary["AbsoluteEfficiency"].Histogram.GetXaxis().SetBinLabel(CutCounter+1, BinLabel)

			self.ROOTFile1.NewHistogram1D("RelativeEfficiency", "Relative Efficiency for the Selections", "Selections", "Relative Efficiency", CutNumber, 0, CutNumber, "Cuts/")

			self.ROOTFile1.HistogramDictionary["RelativeEfficiency"].Histogram.SetMarkerStyle(3)
			self.ROOTFile1.HistogramDictionary["RelativeEfficiency"].Histogram.SetOption("LP")
			self.ROOTFile1.HistogramDictionary["RelativeEfficiency"].Histogram.SetStats(0)

			for CriteriaListCounter in xrange(CutNumber):
				
				self.ROOTFile1.HistogramDictionary["RelativeEfficiency"].Histogram.Fill(CriteriaListCounter, self.SelectionStatisticsList[CriteriaListCounter].RelativeEfficiency)
				
			for CutCounter in xrange(len(self.SelectionStatisticsList)):
				
				if(CutCounter == 0):
					BinLabel = "Starting Events"
				else:
					BinLabel = "Criterion " + str(CutCounter)
				
				self.ROOTFile1.HistogramDictionary["RelativeEfficiency"].Histogram.GetXaxis().SetBinLabel(CutCounter+1, BinLabel)
	
			"""self.ROOTFile1.NewHistogram1D("Purity", "Purity for the Selections", "Selections", "Purity", CutNumber, 0, CutNumber, "Cuts/")
			
			self.ROOTFile1.HistogramDictionary["Purity"].Histogram.SetMarkerStyle(3)
			self.ROOTFile1.HistogramDictionary["Purity"].Histogram.SetOption("LP")
			self.ROOTFile1.HistogramDictionary["Purity"].Histogram.SetStats(0)
			
			for CriteriaListCounter in xrange(CutNumber):
				
				self.ROOTFile1.HistogramDictionary["Purity"].Histogram.Fill(CriteriaListCounter,self.SelectionStatisticsList[CriteriaListCounter].Purity)
				
			for CutCounter in xrange(len(self.SelectionStatisticsList)):
				
				if(CutCounter == 0):
					BinLabel = "Starting Events"
				else:
					BinLabel = "Criterion " + str(CutCounter)
				
				self.ROOTFile1.HistogramDictionary["Purity"].Histogram.GetXaxis().SetBinLabel(CutCounter+1, BinLabel)"""
			
			
			self.ROOTFile1.NewHistogram1D("PurityGraph", "Purity for the Selections", "Selections", "Purity", CutNumber, 0, CutNumber, "Cuts/")

			self.ROOTFile1.HistogramDictionary["PurityGraph"].Histogram.SetMarkerStyle(3)
			self.ROOTFile1.HistogramDictionary["PurityGraph"].Histogram.SetOption("LP")
			self.ROOTFile1.HistogramDictionary["PurityGraph"].Histogram.SetStats(0)

			for CriteriaListCounter in xrange(CutNumber):
				
				self.ROOTFile1.HistogramDictionary["PurityGraph"].Histogram.Fill(CriteriaListCounter,self.SelectionStatisticsList[CriteriaListCounter].Purity)
				
			for CutCounter in xrange(len(self.SelectionStatisticsList)):
				
				if(CutCounter == 0):
					BinLabel = "Starting Events"
				else:
					BinLabel = "Criterion " + str(CutCounter)
				
				self.ROOTFile1.HistogramDictionary["PurityGraph"].Histogram.GetXaxis().SetBinLabel(CutCounter+1, BinLabel)
				
			
			self.NormalisedPurity=StackedHistogram.StackedHistogram("Normalised_Purity", "Constituent processes after each cut (Normalised)", 0.7, 0.65, 0.86, 0.88, "Cuts", "Events Remaining")

			for CriteriaListCounter in xrange(CutNumber):
								
				if(self.SelectionStatisticsList[CriteriaListCounter].Purity > 0):
										
					try:
						self.NormalisedPurity.HistogramDictionary["Purity"].Histogram.Fill(CriteriaListCounter,self.SelectionStatisticsList[CriteriaListCounter].Purity)
					except:
						self.NormalisedPurity.NewHistogram1D("Purity", "Purity for the Selections", "Selections", "Purity", CutNumber, 0, CutNumber, "Delta -> p gamma", "Cuts/Normalised/Constituent Histograms/")
						self.NormalisedPurity.HistogramDictionary["Purity"].Histogram.Fill(CriteriaListCounter,self.SelectionStatisticsList[CriteriaListCounter].Purity)
				
				if(self.SelectionStatisticsList[CriteriaListCounter].PionPurity > 0):
					try:
						self.NormalisedPurity.HistogramDictionary["PionPurity"].Histogram.Fill(CriteriaListCounter,self.SelectionStatisticsList[CriteriaListCounter].PionPurity)
					except:
						self.NormalisedPurity.NewHistogram1D("PionPurity", "Purity for the Selections", "Selections", "Purity", CutNumber, 0, CutNumber, "Delta -> p pi", "Cuts/Normalised/Constituent Histograms/")
						self.NormalisedPurity.HistogramDictionary["PionPurity"].Histogram.Fill(CriteriaListCounter,self.SelectionStatisticsList[CriteriaListCounter].PionPurity)
			
				if(self.SelectionStatisticsList[CriteriaListCounter].RPPurity > 0):
					try:
						self.NormalisedPurity.HistogramDictionary["RPPurity"].Histogram.Fill(CriteriaListCounter,self.SelectionStatisticsList[CriteriaListCounter].RPPurity)
					except:
						self.NormalisedPurity.NewHistogram1D("RPPurity", "Purity for the Selections", "Selections", "Purity", CutNumber, 0, CutNumber, "Other Resonance", "Cuts/Normalised/Constituent Histograms/")
						self.NormalisedPurity.HistogramDictionary["RPPurity"].Histogram.Fill(CriteriaListCounter,self.SelectionStatisticsList[CriteriaListCounter].RPPurity)
					
				if(self.SelectionStatisticsList[CriteriaListCounter].QSPurity > 0):
					try:
						self.NormalisedPurity.HistogramDictionary["QSPurity"].Histogram.Fill(CriteriaListCounter,self.SelectionStatisticsList[CriteriaListCounter].QSPurity)
					except:
						self.NormalisedPurity.NewHistogram1D("QSPurity", "Purity for the Selections", "Selections", "Purity", CutNumber, 0, CutNumber, "QES", "Cuts/Normalised/Constituent Histograms/")
						self.NormalisedPurity.HistogramDictionary["QSPurity"].Histogram.Fill(CriteriaListCounter,self.SelectionStatisticsList[CriteriaListCounter].QSPurity)
				
				if(self.SelectionStatisticsList[CriteriaListCounter].ESPurity > 0):
					try:
						self.NormalisedPurity.HistogramDictionary["ESPurity"].Histogram.Fill(CriteriaListCounter,self.SelectionStatisticsList[CriteriaListCounter].ESPurity)
					except:
						self.NormalisedPurity.NewHistogram1D("ESPurity", "Purity for the Selections", "Selections", "Purity", CutNumber, 0, CutNumber, "ES", "Cuts/Normalised/Constituent Histograms/")
						self.NormalisedPurity.HistogramDictionary["ESPurity"].Histogram.Fill(CriteriaListCounter,self.SelectionStatisticsList[CriteriaListCounter].ESPurity)
			
				if(self.SelectionStatisticsList[CriteriaListCounter].DISPurity > 0):
					try:
						self.NormalisedPurity.HistogramDictionary["DISPurity"].Histogram.Fill(CriteriaListCounter,self.SelectionStatisticsList[CriteriaListCounter].DISPurity)
					except:
						self.NormalisedPurity.NewHistogram1D("DISPurity", "Purity for the Selections", "Selections", "Purity", CutNumber, 0, CutNumber, "DIS", "Cuts/Normalised/Constituent Histograms/")
						self.NormalisedPurity.HistogramDictionary["DISPurity"].Histogram.Fill(CriteriaListCounter,self.SelectionStatisticsList[CriteriaListCounter].DISPurity)
					
				if(self.SelectionStatisticsList[CriteriaListCounter].CSPurity > 0):
					try:
						self.NormalisedPurity.HistogramDictionary["CSPurity"].Histogram.Fill(CriteriaListCounter,self.SelectionStatisticsList[CriteriaListCounter].CSPurity)
					except:
						self.NormalisedPurity.NewHistogram1D("CSPurity", "Purity for the Selections", "Selections", "Purity", CutNumber, 0, CutNumber, "COH", "Cuts/Normalised/Constituent Histograms/")
						self.NormalisedPurity.HistogramDictionary["CSPurity"].Histogram.Fill(CriteriaListCounter,self.SelectionStatisticsList[CriteriaListCounter].CSPurity)
					
				if(self.SelectionStatisticsList[CriteriaListCounter].OtherPurity > 0):
					try:
						self.NormalisedPurity.HistogramDictionary["OtherPurity"].Histogram.Fill(CriteriaListCounter,self.SelectionStatisticsList[CriteriaListCounter].OtherPurity)
					except:
						self.NormalisedPurity.NewHistogram1D("OtherPurity", "Purity for the Selections", "Selections", "Purity", CutNumber, 0, CutNumber, "Other", "Cuts/Normalised/Constituent Histograms/")
						self.NormalisedPurity.HistogramDictionary["OtherPurity"].Histogram.Fill(CriteriaListCounter,self.SelectionStatisticsList[CriteriaListCounter].OtherPurity)
			
			for Histogram1 in self.NormalisedPurity.HistogramDictionary.itervalues():
				for CutCounter in xrange(len(self.SelectionStatisticsList)):
					
					if(CutCounter == 0):
						BinLabel = "Starting Events"
					else:
						BinLabel = "Criterion " + str(CutCounter)
					
					Histogram1.Histogram.GetXaxis().SetBinLabel(CutCounter+1, BinLabel)
			
		
			self.NormalisedPurity.AutoPrepare("f")
				
			self.ROOTFile1.NewStackedHistogramCanvas("Normalised_Purity_Canvas", self.NormalisedPurity.StackedHistogramCanvas("Normalised_Purity_Canvas", "Canvas of Normalised Cut Purity", 700, 500), "Cuts/Normalised/")
						
			self.NormalisedPurity.DrawConstituentHistograms(self.ROOTFile1)
		
		
			"""for CriteriaListCounter in xrange(CutNumber):
				
				self.ROOTFile1.HistogramDictionary["PionPurity"].Histogram.Fill(CriteriaListCounter,self.SelectionStatisticsList[CriteriaListCounter].PionPurity)
				
			for CutCounter in xrange(len(self.SelectionStatisticsList)):
				
				if(CutCounter == 0):
					BinLabel = "Starting Events"
				else:
					BinLabel = "Criterion " + str(CutCounter)
				
				self.ROOTFile1.HistogramDictionary["PionPurity"].Histogram.GetXaxis().SetBinLabel(CutCounter+1, BinLabel)"""
		
		
		
			############## Application of truth to criteria
				
			self.CutPurity=StackedHistogram.StackedHistogram("Cut_Purity", "Constituent Processes for the Events after every Selection",0.7,0.65,0.86,0.88, "Cuts", "Events Remaining")
			
			if(self.SelectionStatisticsList[0].TruthDelta>0):
				self.CutPurity.NewHistogram1D("Delta_True", "True Delta->p gamma interactions for each cut", "Cut Number", "Events Remaining",CutNumber,0,CutNumber, "Delta -> p gamma", "Cuts/Energy/Constituent Histograms/")
				
			if(self.SelectionStatisticsList[0].ReconstructedDelta>0):
				self.CutPurity.NewHistogram1D("Delta1BaryonToProtonPi0Meson", "Number of Delta 1 Baryons to Protons and Pi 0 Mesons", "Cut Number", "Events Remaining",CutNumber,0,CutNumber, "Delta -> p pi0", "Cuts/Energy/Constituent Histograms/")
			
			if(self.SelectionStatisticsList[0].OtherRPInteraction>0):
				self.CutPurity.NewHistogram1D("Other_Resonance_True", "True other resonances interactions for each cut", "Cut Number", "Events Remaining",CutNumber,0,CutNumber, "Other Resonance", "Cuts/Energy/Constituent Histograms/")
			
			if(self.SelectionStatisticsList[0].QSInteraction>0):
				self.CutPurity.NewHistogram1D("QES_True", "True QES interactions for each cut", "Cut Number", "Events Remaining",CutNumber,0,CutNumber, "QES Interaction", "Cuts/Energy/Constituent Histograms/")
				
			if(self.SelectionStatisticsList[0].ESInteraction>0):
				self.CutPurity.NewHistogram1D("ES_True", "True ES interactions for each cut", "Cut Number", "Events Remaining",CutNumber,0,CutNumber, "ES Interaction", "Cuts/Energy/Constituent Histograms/")
			
			if(self.SelectionStatisticsList[0].DISInteraction>0):
				self.CutPurity.NewHistogram1D("DIS_True", "True DIS interactions for each cut", "Cut Number", "Events Remaining",CutNumber,0,CutNumber, "DIS Interaction", "Cuts/Energy/Constituent Histograms/")
			
			if(self.SelectionStatisticsList[0].CSInteraction>0):
				self.CutPurity.NewHistogram1D("COH_True", "True COH interactions for each cut", "Cut Number", "Events Remaining",CutNumber,0,CutNumber, "COH Interaction", "Cuts/Energy/Constituent Histograms/")
				
			if(self.SelectionStatisticsList[0].OtherInteraction>0):
				self.CutPurity.NewHistogram1D("Other_True", "True other interactions for each cut", "Cut Number", "Events Remaining",CutNumber,0,CutNumber, "Other Interaction", "Cuts/Energy/Constituent Histograms/")

			for CutCounter in xrange(len(self.SelectionStatisticsList)):
				for FillCounter in xrange(self.SelectionStatisticsList[CutCounter].TruthDelta):
					self.CutPurity.HistogramDictionary["Delta_True"].Histogram.Fill(CutCounter)
				for FillCounter in xrange(self.SelectionStatisticsList[CutCounter].ReconstructedDelta):
					self.CutPurity.HistogramDictionary["Delta1BaryonToProtonPi0Meson"].Histogram.Fill(CutCounter)
				for FillCounter in xrange(self.SelectionStatisticsList[CutCounter].OtherRPInteraction):
					self.CutPurity.HistogramDictionary["Other_Resonance_True"].Histogram.Fill(CutCounter)
				for FillCounter in xrange(self.SelectionStatisticsList[CutCounter].QSInteraction):
					self.CutPurity.HistogramDictionary["QES_True"].Histogram.Fill(CutCounter)
				for FillCounter in xrange(self.SelectionStatisticsList[CutCounter].ESInteraction):
					self.CutPurity.HistogramDictionary["ES_True"].Histogram.Fill(CutCounter)
				for FillCounter in xrange(self.SelectionStatisticsList[CutCounter].DISInteraction):
					self.CutPurity.HistogramDictionary["DIS_True"].Histogram.Fill(CutCounter)
				for FillCounter in xrange(self.SelectionStatisticsList[CutCounter].CSInteraction):
					self.CutPurity.HistogramDictionary["COH_True"].Histogram.Fill(CutCounter)
				for FillCounter in xrange(self.SelectionStatisticsList[CutCounter].OtherInteraction):
					self.CutPurity.HistogramDictionary["Other_True"].Histogram.Fill(CutCounter)


			self.CutPurity.AutoPrepare("f")
				
			self.ROOTFile1.NewStackedHistogramCanvas("Cut_Purity_Canvas", self.CutPurity.StackedHistogramCanvas("Cut_Purity_Canvas", "Canvas of Cut Purity", 700, 500), "Cuts/Energy/")
						
			self.CutPurity.DrawConstituentHistograms(self.ROOTFile1)
					
			for Histogram1 in self.CutPurity.HistogramDictionary.itervalues():
				for CutCounter in xrange(len(self.SelectionStatisticsList)):
				
					if(CutCounter == 0):
						BinLabel = "Starting Events"
					else:
						BinLabel = "Criterion " + str(CutCounter)
				
					Histogram1.Histogram.GetXaxis().SetBinLabel(CutCounter+1, BinLabel)
					
			self.FinalInvariantMass.AutoPrepare("f")
		
			self.ROOTFile1.NewStackedHistogramCanvas("Final_Invariant_Mass", self.FinalInvariantMass.StackedHistogramCanvas("Final_Invariant_Mass", "Canvas of the invariant mass of the delta baryon after all cuts have been applied", 700, 500), "Cuts/Invariant Mass/")
		
			self.FinalInvariantMass.DrawConstituentHistograms(self.ROOTFile1)
			
			self.InvariantMassAllECal.AutoPrepare("f")
		
			self.ROOTFile1.NewStackedHistogramCanvas("Invariant_Mass_All_ECal", self.InvariantMassAllECal.StackedHistogramCanvas("Invariant_Mass_All_ECal", "Canvas of the invariant mass of the delta baryon from comparison of single photon to all ECals", 700, 500), "Cuts/Invariant Mass/All ECal/")
		
			self.InvariantMassAllECal.DrawConstituentHistograms(self.ROOTFile1)
					
			###############			
						
			self.EfficiencyStatistics = StatisticsCollection.StatisticsCollection("Efficiency Statistics")
			
			self.EfficiencyStatistics.NewStatistic("NEvents0", "Initial Number of Events", self.SelectionStatisticsList[0].EventsRemaining)
			self.EfficiencyStatistics.NewStatistic("NEvents1", "Selection 1 - At least one reconstructed track was recorded - Events Remaining", self.SelectionStatisticsList[1].EventsRemaining)
			self.EfficiencyStatistics.NewStatistic("NEvents2", "Selection 2 - The track has at least 18 TPC nodes - Events Remaining", self.SelectionStatisticsList[2].EventsRemaining)
			self.EfficiencyStatistics.NewStatistic("NEvents3", "Selection 3 - At least one proton-identified track - Events Remaining", self.SelectionStatisticsList[3].EventsRemaining)
			self.EfficiencyStatistics.NewStatistic("NEvents4", "Selection 4 - Only one proton-identified track - Events Remaining", self.SelectionStatisticsList[4].EventsRemaining)
			self.EfficiencyStatistics.NewStatistic("NEvents5", "Selection 5 - Proton track is the first track into the detector - Events Remaining", self.SelectionStatisticsList[5].EventsRemaining)
			self.EfficiencyStatistics.NewStatistic("NEvents6", "Selection 6 - Proton track began in the FGDs - Events Remaining", self.SelectionStatisticsList[6].EventsRemaining)
			self.EfficiencyStatistics.NewStatistic("NEvents7", "Selection 7 - At least one EC cluster was recorded - Events Remaining", self.SelectionStatisticsList[7].EventsRemaining)
			
			Selection8 = "Selection 8 - The smallest angle was less than " + str(NumericalCuts.MinimumAngle) + " degees - Events Remaining"
			self.EfficiencyStatistics.NewStatistic("NEvents8", Selection8, self.SelectionStatisticsList[8].EventsRemaining)
			
	
		print self.TruthStatistics.ToText()
		print self.ReconstructedStatistics.ToText()
		print self.EfficiencyStatistics.ToText()
	
		print TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine
		
		if (len(self.BackgroundEventNumbers) > 0):
		
			print "Background Event Indices: "
	
			for n in self.BackgroundEventNumbers:
				print str(n)
	
			print TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine
		
		if (len(self.BackgroundPiMesonEventNumbers) > 0):
		
			print "Background Pi Meson Event Indices: "
	
			for n in self.BackgroundPiMesonEventNumbers:
				print str(n)
	
			print TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine
	
		del sys.stdout#Closes .txt file and returns to printing only to console
	
		self.ROOTFile1.Close()
		
	
	def runEvent(self):
	
		self.TruthStatistics.Statistics["NEvents"].Quantity += 1
	
		###### First loop over the true genie data to look for information about the delta interactions
	
		DeltaPGammaEvent = False
		Delta1BaryonToProtonPi0MesonEvent = False
	
		NVertices = self.Truth_GRTVertices.NVtx

		InteractionType = ""
		
		
		
		#SelectionReferences = ["A", "B", "C", "D", "E"]
		
		#Event1 = Simulation.Event()
		
		#Event1 = self.EventCollection1.InterpretEvent(self.Truth_GRTVertices.Vtx, self.Reconstructed_Global.PIDs, self.Truth_Trajectories.Trajectories, self.Reconstructed_TEC.ReconObject, SelectionReferences) 
		
		#self.TruthStatistics.Statistics["NVertices"].Quantity += len(Event1.TrueEvent.TrueVertices)
		#self.TruthStatistics.Statistics["NDeltaToProtonPhoton"].Quantity += 1
		#self.TruthStatistics.Statistics["NDeltaToProtonPhotonCC"].Quantity += 1
		#self.TruthStatistics.Statistics["NDeltaToProtonPhotonNC"].Quantity += 1
		
		########################################
		# TRUTH DATA #
		########################################
		
		Delta1Hardons = []
		TruePhotons = []
		
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
				
				if (GRTParticle1.pdg == ParticleCodes.Delta1Baryon):

					DeltaDaughterFirst = GRTParticle1.first_daughter#Finds first Delta daughter
					DeltaDaughterLast = GRTParticle1.last_daughter#Finds last Delta daughter
					DeltaDaughterNumber = DeltaDaughterLast - DeltaDaughterFirst+1#Finds number of daughters of the delta

					if (DeltaDaughterNumber == 2):#Delta -> p gamma must have 2 daughters
						
						for DaughterParticle in self.RTTools.getParticles(GRTVertex1):#Loop again over particles in vertex
						
							if (DaughterParticle.i >= DeltaDaughterFirst and DaughterParticle.i <= DeltaDaughterLast):#Only looks for when counter is in range of Delta daughter particles
							
								if (DaughterParticle.pdg == ParticleCodes.Proton):
									ProtonFromDelta = True
									
								if (DaughterParticle.pdg == ParticleCodes.Photon):
									PhotonFromDelta = True
									
								if (DaughterParticle.pdg == ParticleCodes.Pi0Meson):
									Pi0MesonFromDelta = True
									
					
					Delta1Hardons.append(GRTParticle1)
				
				if (GRTParticle1.pdg == ParticleCodes.Photon):#Looks for a neutrino
				
					if (GRTParticle1.status == 1):#Checks if neutrino is initial state
					
						TruePhotons.append(GRTParticle1)					
				
												
			######################################## Search for current and interaction type. This method can look at electron neutrinos and anti muon neutrinos for any possible extension
			
			self.EventCodeDeconstructor1.ReadCode(GRTVertex1.EvtCode)
			
			for Element1 in self.EventCodeDeconstructor1.Elements:
				if (Element1.Reference == "Current Code"):
					Current = Element1.Content
				if (Element1.Reference == "Process Code"):
					InteractionType = Element1.Content
													
							
			###################################### Categorisation of various interesting interactions ############
							
			DeltaPGammaInteraction = (IncidentMuonNeutrino and ProtonFromDelta and PhotonFromDelta and InteractionType == "RP")
			
			Delta1BaryonToProtonPi0MesonInteraction = (IncidentMuonNeutrino and ProtonFromDelta and Pi0MesonFromDelta and InteractionType == "RP")
			
			if (DeltaPGammaInteraction):
				self.TruthStatistics.Statistics["NDeltaToProtonPhoton"].Quantity += 1
				DeltaPGammaEvent=True
				
			if (DeltaPGammaInteraction and Current == "CC"):
				self.TruthStatistics.Statistics["NDeltaToProtonPhotonCC"].Quantity += 1
				
			if (DeltaPGammaInteraction and Current == "NC"):
				self.TruthStatistics.Statistics["NDeltaToProtonPhotonNC"].Quantity += 1

			if (Delta1BaryonToProtonPi0MesonInteraction):
				Delta1BaryonToProtonPi0MesonEvent = True




		########################################
		# RECONSTRUCTED DATA #
		########################################

		NPIDs = self.Reconstructed_Global.NPIDs#Number of reconstructed PIDs

		if (NPIDs > 0):
			
			self.ReconstructedStatistics.Statistics["NEventsWithRPID"].Quantity += 1

		ProtonIsCorrectlyReconstructed = False
	
		ProtonList = []
			
		PIDParticleList = []
		PIDObjectList = []
		
		PIDNumber = 0
		TPCValidPIDNumber = 0
		
		for PID in self.Reconstructed_Global.PIDs: # Loop over the PIDs if they exist
			
			PIDNumber += 1
								
			SuitableTPCNodeNumber = False
										
			for TPCTrack1 in PID.TPC: # Loop over TPC PIDs						
				if (TPCTrack1.NNodes > 18):
					SuitableTPCNodeNumber = True		
					
			if (SuitableTPCNodeNumber):
				
				TPCValidPIDNumber+=1	

				PIDObject = PIDParticle.PIDParticle()
					
				PIDObject.ReconFrontMomentum = PID.FrontMomentum
					
				PIDObject.ReconFrontDirectionX = PID.FrontDirection.X()
				PIDObject.ReconFrontDirectionY = PID.FrontDirection.Y()
				PIDObject.ReconFrontDirectionZ = PID.FrontDirection.Z()
				
				PIDObject.ReconFrontPositionT = PID.FrontPosition.T()	
				PIDObject.ReconFrontPositionX = PID.FrontPosition.X()
				PIDObject.ReconFrontPositionY = PID.FrontPosition.Y()
				PIDObject.ReconFrontPositionZ = PID.FrontPosition.Z()
					
				PIDObject.Detectors = str(PID.Detectors)

				NodeNumber = 0
			
				######### For particle pulls - There are possibly multiple TPCs with different pulls for track, so this code looks for the TPC with the most nodes
			
				for i, TPCTrack1 in enumerate(PID.TPC):
					if (TPCTrack1.NNodes > NodeNumber):
						BestTPCTrack = i
					
				for j , TPCTrack1 in enumerate(PID.TPC):
					if (j == i):
						PIDObject.ParticlePull[ParticleCodes.Electron] = TPCTrack1.PullEle
						PIDObject.ParticlePull[ParticleCodes.Kaon1] = TPCTrack1.PullKaon
						PIDObject.ParticlePull[ParticleCodes.MuLepton] = TPCTrack1.PullMuon
						PIDObject.ParticlePull[ParticleCodes.Pi1Meson] = TPCTrack1.PullPion
						PIDObject.ParticlePull[ParticleCodes.Proton] = TPCTrack1.PullProton

				LowestPull=100
				
				for Particle , ParticlePull in PIDObject.ParticlePull.iteritems():
					
					if (math.fabs(ParticlePull) < math.fabs(LowestPull) and math.fabs(ParticlePull) < math.fabs(NumericalCuts.ParticlePullCut[Particle])):
						
						LowestPull = math.fabs(ParticlePull)
						
						PIDObject.ReconParticleID = Particle

				for TrueTrajectory in self.Truth_Trajectories.Trajectories:#Loop over the truth trajectories for comparison
					if (TrueTrajectory.ID == PID.TrueParticle.ID):
																	
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

			self.ROOTFile1.HistogramDictionary["PID_Electron_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Electron])
			self.ROOTFile1.HistogramDictionary["PID_Kaon_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Kaon1])
			self.ROOTFile1.HistogramDictionary["PID_Muon_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.MuLepton])
			self.ROOTFile1.HistogramDictionary["PID_Pion_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Pi1Meson])
			self.ROOTFile1.HistogramDictionary["PID_Proton_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Proton])
			
			self.ROOTFile1.HistogramDictionary["PID_Proton_Against_Muon_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Proton],PIDObject1.ParticlePull[ParticleCodes.MuLepton])

			if (PIDObject1.ReconParticleID == ParticleCodes.Proton):#Looking for reconstructed proton track
				
				ReconstructedProtonTrackNumber += 1
									
				Proton1 = ReconstructedParticle.ReconstructedParticle()
		
				Proton1.EnergyMomentum.T = PIDObject1.ReconstructedParticleEnergy()
				Proton1.EnergyMomentum.X = PIDObject1.ReconFrontMomentum * PIDObject1.ReconFrontDirectionX
				Proton1.EnergyMomentum.Y = PIDObject1.ReconFrontMomentum * PIDObject1.ReconFrontDirectionY
				Proton1.EnergyMomentum.Z = PIDObject1.ReconFrontMomentum * PIDObject1.ReconFrontDirectionZ
									
				self.ROOTFile1.HistogramDictionary["Recon_Truth_Proton_Momentum"].Histogram.Fill(PIDObject1.ReconTrueMomentumDifference())	
				self.ROOTFile1.HistogramDictionary["Truth_Proton_Momentum"].Histogram.Fill(PIDObject1.TrueFrontMomentum)
					
				Proton1.Position.T = PIDObject1.ReconFrontPositionT
				Proton1.Position.X = PIDObject1.ReconFrontPositionX
				Proton1.Position.Y = PIDObject1.ReconFrontPositionY
				Proton1.Position.Z = PIDObject1.ReconFrontPositionZ
								
				ProtonList.append(Proton1)
				
				self.ROOTFile1.HistogramDictionary["Proton_PID_Electron_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Electron])
				self.ROOTFile1.HistogramDictionary["Proton_PID_Kaon_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Kaon1])
				self.ROOTFile1.HistogramDictionary["Proton_PID_Muon_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.MuLepton])
				self.ROOTFile1.HistogramDictionary["Proton_PID_Pion_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Pi1Meson])
				self.ROOTFile1.HistogramDictionary["Proton_PID_Proton_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Proton])
				
				self.ROOTFile1.HistogramDictionary["Proton_PID_Proton_Against_Muon_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Proton],PIDObject1.ParticlePull[ParticleCodes.MuLepton])

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
		
		SingleProtonInFGDFiducial = False
		
		if (ReconstructedProtonTrackNumber == 1):
			
			for PIDObject1 in PIDObjectList:
				
				if (PIDObject1.ReconParticleID == ParticleCodes.Proton):#Looking for reconstructed proton track
					ProtonTrackFrontPositionZ=PIDObject1.ReconFrontPositionZ

					inFGDX = (PIDObject1.ReconFrontPositionX >= self.FGD1Fiducial.X1 and PIDObject1.ReconFrontPositionX <= self.FGD1Fiducial.X2)
					inFGDY = (PIDObject1.ReconFrontPositionY >= self.FGD1Fiducial.Y1 and PIDObject1.ReconFrontPositionY <= self.FGD1Fiducial.Y2)
					inFGDZ = (PIDObject1.ReconFrontPositionZ >= self.FGD1Fiducial.Z1 and PIDObject1.ReconFrontPositionZ <= self.FGD1Fiducial.Z2) or (PIDObject1.ReconFrontPositionZ >= self.FGD2Fiducial.Z1 and PIDObject1.ReconFrontPositionZ <= self.FGD2Fiducial.Z2)
					
					if(inFGDX and inFGDY and inFGDZ):
						SingleProtonInFGDFiducial=True
					
					self.ROOTFile1.HistogramDictionary["Single_Proton_PID_Electron_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Electron])
					self.ROOTFile1.HistogramDictionary["Single_Proton_PID_Kaon_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Kaon1])
					self.ROOTFile1.HistogramDictionary["Single_Proton_PID_Muon_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.MuLepton])
					self.ROOTFile1.HistogramDictionary["Single_Proton_PID_Pion_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Pi1Meson])
					self.ROOTFile1.HistogramDictionary["Single_Proton_PID_Proton_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Proton])
					
					self.ROOTFile1.HistogramDictionary["Single_Proton_PID_Proton_Against_Muon_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Proton],PIDObject1.ParticlePull[ParticleCodes.MuLepton])
					
			SingleProtonTrackFirst=True
					
			for PIDObject1 in PIDObjectList:
				
				if (PIDObject1.ReconFrontPositionZ < ProtonTrackFrontPositionZ):
					
					SingleProtonTrackFirst=False
					
		else:
			SingleProtonTrackFirst = False
		
		if (CorrectlyReconstructedProton > 0):
			ProtonIsCorrectlyReconstructed = True
		else:
			ProtonIsCorrectlyReconstructed = False
			
		if (ReconstructedProtonTrackNumber > 0):
			ReconstructedProtonTrack = True
		else:
			ReconstructedProtonTrack = False
		
		############################## ECal cluster section ###################################
				
		#I think we will only look at the Tracker ECal (TPC+FGD) as the POD ECal is mainly used for POD !! What about downstream ECal
				
		PhotonEnergyMomentumList = []
		PhotonList = []
		
		for TECObject in self.Reconstructed_TEC.ReconObject:#Loop over these reconstructed objects
			
			ECEnergy = TECObject.EMEnergyFit_Result#The energy of photon
			
			Photon1 = ReconstructedParticle.ReconstructedParticle()
			
			Photon1.EnergyMomentum.T = ECEnergy
										
			if (TECObject.IsShowerLike):#Check if ECal reconstruction is tracklike or showerlike, it shouldnt matter which for the photon, but the directions are different
				ECUnitDirection = ThreeVector.ThreeVector(TECObject.Shower.Direction.X(), TECObject.Shower.Direction.Y(), TECObject.Shower.Direction.Z())
				
				Photon1.DirectionIsValid = True
				
				Photon1.Position.T = TECObject.Shower.Position.T()
				Photon1.Position.X = TECObject.Shower.Position.X()
				Photon1.Position.Y = TECObject.Shower.Position.Y()
				Photon1.Position.Z = TECObject.Shower.Position.Z()
				
			elif (TECObject.IsTrackLike):
				ECUnitDirection = ThreeVector.ThreeVector(TECObject.Track.Direction.X(), TECObject.Track.Direction.Y(), TECObject.Track.Direction.Z())
						
				Photon1.Position.T = TECObject.Track.Position.T()
				Photon1.Position.X = TECObject.Track.Position.X()
				Photon1.Position.Y = TECObject.Track.Position.Y()
				Photon1.Position.Z = TECObject.Track.Position.Z()
						
			#if (ECUnitDirection.Modulus() < 1.1):#For some reason there sometimes are occurences where the magnitude is far above 1. This if filters them out. We should probably look into this further
			#This thing has the potential to mess up later if you are looping over NTrackerECalRecon!!!!
			Photon1.EnergyMomentum.X = ECUnitDirection.X * ECEnergy
			Photon1.EnergyMomentum.Y = ECUnitDirection.Y * ECEnergy
			Photon1.EnergyMomentum.Z = ECUnitDirection.Z * ECEnergy
										
			Photon1.Direction.X = ECUnitDirection.X
			Photon1.Direction.Y = ECUnitDirection.Y
			Photon1.Direction.Z = ECUnitDirection.Z
			
			PhotonList.append(Photon1)
				
		NTrackerECalRecon = len(PhotonList)#Number of reconstructed objects in the ECal	!!This is a temporary fix to look at the Modulus problem	
		
		#################### Toms new photon cut section ####### Currently we have many potential photons and a single proton.
		# First, the photon with the "best" angle (smallest) is chosen as the single photon ... then we can look at invariant mass
		
		SmallestAngle = 180
		
		if (ReconstructedProtonTrackNumber == 1):
			
			Proton1 = ProtonList[0]
			
			for Photon1 in PhotonList:
							
				Angle1 = 180
					
				Line1 = ThreeVector.ThreeVector()
				Line2 = ThreeVector.ThreeVector()
				
				Line1.X = Proton1.Position.X - Photon1.Position.X
				Line1.Y = Proton1.Position.Y - Photon1.Position.Y
				Line1.Z = Proton1.Position.Z - Photon1.Position.Z
				
				Line2.X = Photon1.Direction.X
				Line2.Y = Photon1.Direction.Y
				Line2.Z = Photon1.Direction.Z
				
				Angle1 = ThreeVector.FindAngle(Line1, Line2)
				
				if (math.fabs(Angle1) < SmallestAngle):
					
					SmallestAngle = math.fabs(Angle1)
					self.ROOTFile1.HistogramDictionary["SelectedPhotonAngles"].Histogram.Fill(Angle1)
					
					SelectedPhoton = Photon1
					SelectedProton = Proton1
		
			if (len(PhotonList) > 0):
			
				DeltaBaryon = FourVector.FourVector()
						
				DeltaBaryon.T = SelectedPhoton.EnergyMomentum.T + SelectedProton.EnergyMomentum.T # Delta Baryon Energy
				DeltaBaryon.X = SelectedPhoton.EnergyMomentum.X + SelectedProton.EnergyMomentum.X
				DeltaBaryon.Y = SelectedPhoton.EnergyMomentum.Y + SelectedProton.EnergyMomentum.Y
				DeltaBaryon.Z = SelectedPhoton.EnergyMomentum.Z + SelectedProton.EnergyMomentum.Z
		
		############################## Summary Section ########################################

		if (ReconstructedProtonTrack):#Counts number of events with at least one reconstructed proton track
			self.ReconstructedStatistics.Statistics["NEventsWithRProton"].Quantity += 1
		if (ProtonIsCorrectlyReconstructed):
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
		
		if (TPCValidPIDNumber > 0 and Criteria[1]):
			Criteria.append(True)			
		else:
			Criteria.append(False)
					
		if (ReconstructedProtonTrackNumber > 0 and Criteria[2]):
			Criteria.append(True)
		else:
			Criteria.append(False)
		
		if (ReconstructedProtonTrackNumber == 1 and Criteria[3]):
			Criteria.append(True)
		else:
			Criteria.append(False)
		
		if (SingleProtonTrackFirst and Criteria[4]):
			Criteria.append(True)
		else:
			Criteria.append(False)
		
		if (SingleProtonInFGDFiducial and Criteria[5]):
			Criteria.append(True)
		else:
			Criteria.append(False)
			
		if (NTrackerECalRecon > 0 and Criteria[6]):
			Criteria.append(True)
		else:
			Criteria.append(False)
	
	
	
	
			
		if (SmallestAngle <= NumericalCuts.MinimumAngle and Criteria[7]):
			Criteria.append(True)
		else:
			Criteria.append(False)
		
		
		
		CutNumber = len(Criteria)
		
		if (self.TruthStatistics.Statistics["NEvents"].Quantity == 1):
			for CutCounter in xrange(CutNumber):
				
				SelectionCriterion1 = SelectionStatistics.SelectionStatistics()
				
				self.SelectionStatisticsList.append(SelectionCriterion1)
										
					
		for CutCounter in xrange(CutNumber):
			if (Criteria[CutCounter]):
				self.SelectionStatisticsList[CutCounter].EventsRemaining += 1
				if (DeltaPGammaEvent):
					self.SelectionStatisticsList[CutCounter].TruthDelta += 1
				elif (Delta1BaryonToProtonPi0MesonEvent):
					self.SelectionStatisticsList[CutCounter].ReconstructedDelta += 1
				elif (InteractionType == "RP" and not DeltaPGammaEvent and not Delta1BaryonToProtonPi0MesonEvent):
					self.SelectionStatisticsList[CutCounter].OtherRPInteraction += 1
				elif (InteractionType == "QS"):
					self.SelectionStatisticsList[CutCounter].QSInteraction += 1
				elif (InteractionType == "ES"):
					self.SelectionStatisticsList[CutCounter].ESInteraction += 1
				elif (InteractionType == "DIS"):
					self.SelectionStatisticsList[CutCounter].DISInteraction += 1
				elif (InteractionType == "C"):
					self.SelectionStatisticsList[CutCounter].CSInteraction += 1
		
		################ Invariant Mass Section #########
		
		if (Criteria[len(Criteria) - 1] == True):
			
			if (DeltaPGammaEvent):
				
				try:
					self.FinalInvariantMass.HistogramDictionary["Final_Invariant_Mass_DeltaPGamma"].Histogram.Fill(DeltaBaryon.InvariantModulus())
				except:
					self.FinalInvariantMass.NewHistogram1D("Final_Invariant_Mass_DeltaPGamma", "Invariant Mass contribution from true Delta -> p gamma interactions", "Mass (GeV)", "Number", 100, 0, 3000, "Delta -> p gamma", "Cuts/Invariant Mass/Constituent Histograms/")
					self.FinalInvariantMass.HistogramDictionary["Final_Invariant_Mass_DeltaPGamma"].Histogram.Fill(DeltaBaryon.InvariantModulus())
				
			elif (Delta1BaryonToProtonPi0MesonEvent):

				try:
					self.FinalInvariantMass.HistogramDictionary["Final_Invariant_Mass_DeltaPPi"].Histogram.Fill(DeltaBaryon.InvariantModulus())
				except:
					self.FinalInvariantMass.NewHistogram1D("Final_Invariant_Mass_DeltaPPi", "Invariant Mass contribution from true Delta -> p pi interactions", "Mass (GeV)", "Number", 100, 0, 3000, "Delta -> p pi", "Cuts/Invariant Mass/Constituent Histograms/")
					self.FinalInvariantMass.HistogramDictionary["Final_Invariant_Mass_DeltaPPi"].Histogram.Fill(DeltaBaryon.InvariantModulus())
				
			elif (InteractionType == "RP" and not DeltaPGammaEvent and not Delta1BaryonToProtonPi0MesonEvent):

				try:	
					self.FinalInvariantMass.HistogramDictionary["Final_Invariant_Mass_RP"].Histogram.Fill(DeltaBaryon.InvariantModulus())
				except:
					self.FinalInvariantMass.NewHistogram1D("Final_Invariant_Mass_RP", "Invariant Mass contribution from true other resonance interactions", "Mass (GeV)", "Number", 100, 0, 3000, "Other Resonance", "Cuts/Invariant Mass/Constituent Histograms/")
					self.FinalInvariantMass.HistogramDictionary["Final_Invariant_Mass_RP"].Histogram.Fill(DeltaBaryon.InvariantModulus())
			
			elif (InteractionType == "QES"):

				try:	
					self.FinalInvariantMass.HistogramDictionary["Final_Invariant_Mass_QES"].Histogram.Fill(DeltaBaryon.InvariantModulus())
				except:
					self.FinalInvariantMass.NewHistogram1D("Final_Invariant_Mass_QES", "Invariant Mass contribution from true QES interactions", "Mass (GeV)", "Number", 100, 0, 3000, "QES", "Cuts/Invariant Mass/Constituent Histograms/")
					self.FinalInvariantMass.HistogramDictionary["Final_Invariant_Mass_QES"].Histogram.Fill(DeltaBaryon.InvariantModulus())
			
			elif (InteractionType == "ES"):

				try:	
					self.FinalInvariantMass.HistogramDictionary["Final_Invariant_Mass_ES"].Histogram.Fill(DeltaBaryon.InvariantModulus())
				except:
					self.FinalInvariantMass.NewHistogram1D("Final_Invariant_Mass_ES", "Invariant Mass contribution from true ES interactions", "Mass (GeV)", "Number", 100, 0, 3000, "ES", "Cuts/Invariant Mass/Constituent Histograms/")
					self.FinalInvariantMass.HistogramDictionary["Final_Invariant_Mass_ES"].Histogram.Fill(DeltaBaryon.InvariantModulus())
				
			elif (InteractionType == "DIS"):

				try:	
					self.FinalInvariantMass.HistogramDictionary["Final_Invariant_Mass_DIS"].Histogram.Fill(DeltaBaryon.InvariantModulus())
				except:
					self.FinalInvariantMass.NewHistogram1D("Final_Invariant_Mass_DIS", "Invariant Mass contribution from true DIS interactions", "Mass (GeV)", "Number", 100, 0, 3000, "DIS", "Cuts/Invariant Mass/Constituent Histograms/")
					self.FinalInvariantMass.HistogramDictionary["Final_Invariant_Mass_DIS"].Histogram.Fill(DeltaBaryon.InvariantModulus())
				
			elif (InteractionType == "C"):

				try:	
					self.FinalInvariantMass.HistogramDictionary["Final_Invariant_Mass_C"].Histogram.Fill(DeltaBaryon.InvariantModulus())
				except:
					self.FinalInvariantMass.NewHistogram1D("Final_Invariant_Mass_C", "Invariant Mass contribution from true COH interactions", "Mass (GeV)", "Number", 100, 0, 3000, "COH", "Cuts/Invariant Mass/Constituent Histograms/")
					self.FinalInvariantMass.HistogramDictionary["Final_Invariant_Mass_C"].Histogram.Fill(DeltaBaryon.InvariantModulus())
					
			else:

				try:	
					self.FinalInvariantMass.HistogramDictionary["Final_Invariant_Mass_Other"].Histogram.Fill(DeltaBaryon.InvariantModulus())
				except:
					self.FinalInvariantMass.NewHistogram1D("Final_Invariant_Mass_Other", "Invariant Mass contribution from true Other interactions", "Mass (GeV)", "Number", 100, 0, 3000, "Other", "Cuts/Invariant Mass/Constituent Histograms/")
					self.FinalInvariantMass.HistogramDictionary["Final_Invariant_Mass_Other"].Histogram.Fill(DeltaBaryon.InvariantModulus())
					
					
			
		if (Criteria[7]):#Matching Single proton to Every ECal cluster
			
			for Photon1 in PhotonList:
				
				DeltaBaryon = FourVector.FourVector()
						
				DeltaBaryon.T = Photon1.EnergyMomentum.T + SelectedProton.EnergyMomentum.T # Delta Baryon Energy
				DeltaBaryon.X = Photon1.EnergyMomentum.X + SelectedProton.EnergyMomentum.X
				DeltaBaryon.Y = Photon1.EnergyMomentum.Y + SelectedProton.EnergyMomentum.Y
				DeltaBaryon.Z = Photon1.EnergyMomentum.Z + SelectedProton.EnergyMomentum.Z
			
				if (DeltaPGammaEvent):
					
					try:
						self.InvariantMassAllECal.HistogramDictionary["Invariant_Mass_DeltaPGamma"].Histogram.Fill(DeltaBaryon.InvariantModulus())
					except:
						self.InvariantMassAllECal.NewHistogram1D("Invariant_Mass_DeltaPGamma", "Invariant Mass contribution from true Delta -> p gamma interactions", "Mass (GeV)", "Number", 100, 0, 3000, "Delta -> p gamma", "Cuts/Invariant Mass/All ECal/Constituent Histograms/")
						self.InvariantMassAllECal.HistogramDictionary["Invariant_Mass_DeltaPGamma"].Histogram.Fill(DeltaBaryon.InvariantModulus())
					
				elif (Delta1BaryonToProtonPi0MesonEvent):

					try:
						self.InvariantMassAllECal.HistogramDictionary["Invariant_Mass_DeltaPPi"].Histogram.Fill(DeltaBaryon.InvariantModulus())
					except:
						self.InvariantMassAllECal.NewHistogram1D("Invariant_Mass_DeltaPPi", "Invariant Mass contribution from true Delta -> p pi interactions", "Mass (GeV)", "Number", 100, 0, 3000, "Delta -> p pi", "Cuts/Invariant Mass/All ECal/Constituent Histograms/")
						self.InvariantMassAllECal.HistogramDictionary["Invariant_Mass_DeltaPPi"].Histogram.Fill(DeltaBaryon.InvariantModulus())
					
				elif (InteractionType == "RP" and not DeltaPGammaEvent and not Delta1BaryonToProtonPi0MesonEvent):

					try:	
						self.InvariantMassAllECal.HistogramDictionary["Invariant_Mass_RP"].Histogram.Fill(DeltaBaryon.InvariantModulus())
					except:
						self.InvariantMassAllECal.NewHistogram1D("Invariant_Mass_RP", "Invariant Mass contribution from true other resonance interactions", "Mass (GeV)", "Number", 100, 0, 3000, "Other Resonance", "Cuts/Invariant Mass/All ECal/Constituent Histograms/")
						self.InvariantMassAllECal.HistogramDictionary["Invariant_Mass_RP"].Histogram.Fill(DeltaBaryon.InvariantModulus())
					
				elif (InteractionType == "QES"):

					try:	
						self.InvariantMassAllECal.HistogramDictionary["Invariant_Mass_QES"].Histogram.Fill(DeltaBaryon.InvariantModulus())
					except:
						self.InvariantMassAllECal.NewHistogram1D("Invariant_Mass_QES", "Invariant Mass contribution from true QES interactions", "Mass (GeV)", "Number", 100, 0, 3000, "QES", "Cuts/Invariant Mass/All ECal/Constituent Histograms/")
						self.InvariantMassAllECal.HistogramDictionary["Invariant_Mass_QES"].Histogram.Fill(DeltaBaryon.InvariantModulus())
					
				elif (InteractionType == "ES"):

					try:	
						self.InvariantMassAllECal.HistogramDictionary["Invariant_Mass_ES"].Histogram.Fill(DeltaBaryon.InvariantModulus())
					except:
						self.InvariantMassAllECal.NewHistogram1D("Invariant_Mass_ES", "Invariant Mass contribution from true ES interactions", "Mass (GeV)", "Number", 100, 0, 3000, "ES", "Cuts/Invariant Mass/All ECal/Constituent Histograms/")
						self.InvariantMassAllECal.HistogramDictionary["Invariant_Mass_ES"].Histogram.Fill(DeltaBaryon.InvariantModulus())
					
				elif (InteractionType == "DIS"):

					try:	
						self.InvariantMassAllECal.HistogramDictionary["Invariant_Mass_DIS"].Histogram.Fill(DeltaBaryon.InvariantModulus())
					except:
						self.InvariantMassAllECal.NewHistogram1D("Invariant_Mass_DIS", "Invariant Mass contribution from true DIS interactions", "Mass (GeV)", "Number", 100, 0, 3000, "DIS", "Cuts/Invariant Mass/All ECal/Constituent Histograms/")
						self.InvariantMassAllECal.HistogramDictionary["Invariant_Mass_DIS"].Histogram.Fill(DeltaBaryon.InvariantModulus())
					
				elif (InteractionType == "C"):

					try:	
						self.InvariantMassAllECal.HistogramDictionary["Invariant_Mass_C"].Histogram.Fill(DeltaBaryon.InvariantModulus())
					except:
						self.InvariantMassAllECal.NewHistogram1D("Invariant_Mass_C", "Invariant Mass contribution from true COH interactions", "Mass (GeV)", "Number", 100, 0, 3000, "COH", "Cuts/Invariant Mass/All ECal/Constituent Histograms/")
						self.InvariantMassAllECal.HistogramDictionary["Invariant_Mass_C"].Histogram.Fill(DeltaBaryon.InvariantModulus())
						
				else:

					try:	
						self.InvariantMassAllECal.HistogramDictionary["Invariant_Mass_Other"].Histogram.Fill(DeltaBaryon.InvariantModulus())
					except:
						self.InvariantMassAllECal.NewHistogram1D("Invariant_Mass_Other", "Invariant Mass contribution from true Other interactions", "Mass (GeV)", "Number", 100, 0, 3000, "Other", "Cuts/Invariant Mass/All ECal/Constituent Histograms/")
						self.InvariantMassAllECal.HistogramDictionary["Invariant_Mass_Other"].Histogram.Fill(DeltaBaryon.InvariantModulus())
			
			
			
			
			
		######### Background Events ##########
			
		
		if (self.SelectBackgroundEvents == True):
			if (Criteria[len(Criteria) - 1] == True):
				if (InteractionType != "RP"):
					self.BackgroundEventNumbers.append(self.BasicInformation.EventID)
				if (Delta1BaryonToProtonPi0MesonInteraction == True):
					self.BackgroundPiMesonEventNumbers.append(self.BasicInformation.EventID)
				
		########################################
		# Delta Baryon Mass #
		########################################

		if (len(PhotonList) > 0 and len(ProtonList) > 0):
			# If both a photon cluster and proton track were found ...

			for Photon1 in PhotonList:
				for Proton1 in ProtonList:
					# Consider every possible combination of one photon and one proton and add the derived particle kinematics to the relevant histogram.
					
					DeltaBaryon = FourVector.FourVector()
					
					DeltaBaryon.T = Photon1.EnergyMomentum.T + Proton1.EnergyMomentum.T # Delta Baryon Energy
					DeltaBaryon.X = Photon1.EnergyMomentum.X + Proton1.EnergyMomentum.X
					DeltaBaryon.Y = Photon1.EnergyMomentum.Y + Proton1.EnergyMomentum.Y
					DeltaBaryon.Z = Photon1.EnergyMomentum.Z + Proton1.EnergyMomentum.Z
																					
					self.ROOTFile1.HistogramDictionary["Reconstructed_Delta1Baryon_Energy"].Histogram.Fill(DeltaBaryon.T)
					self.ROOTFile1.HistogramDictionary["Reconstructed_Delta1Baryon_MomentumModulus"].Histogram.Fill(DeltaBaryon.SpatialModulus())
					self.ROOTFile1.HistogramDictionary["Reconstructed_Delta1Baryon_Mass"].Histogram.Fill(DeltaBaryon.InvariantModulus())
					
					########################################
					# Angle between Photon Direction and Proton Position #
					########################################
										
					Angle1 = 180
					
					Line1 = ThreeVector.ThreeVector()
					Line2 = ThreeVector.ThreeVector()
					
					Line1.X = Proton1.Position.X - Photon1.Position.X
					Line1.Y = Proton1.Position.Y - Photon1.Position.Y
					Line1.Z = Proton1.Position.Z - Photon1.Position.Z
					
					Line2.X = - Photon1.Direction.X
					Line2.Y = - Photon1.Direction.Y
					Line2.Z = - Photon1.Direction.Z
					
					Angle1 = ThreeVector.FindAngle(Line1, Line2)
					TimeSeparation = math.fabs(float(Proton1.Position.T) - float(Photon1.Position.T))
						
					if (ReconstructedProtonTrack and NTrackerECalRecon > 0 and Angle1 < 10 and Angle1 > -10 and Photon1.DirectionIsValid == True):
						self.ReconstructedStatistics.Statistics["NEventsWithTECCAndCRProtonWithin10D"].Quantity += 1
						
						if (TimeSeparation < 250):
							self.ReconstructedStatistics.Statistics["NEventsWithTECCAndCRProtonWithin10DWithin500ns"].Quantity += 1
					
					self.ROOTFile1.HistogramDictionary["PhotonAngles"].Histogram.Fill(Angle1)#!! Should this not be Angle1? Ive now changed it
					self.ROOTFile1.HistogramDictionary["ProtonPhotonTimeSeparations"].Histogram.Fill(TimeSeparation)
					
					
					if (TimeSeparation < 250):
																						
						self.ROOTFile1.HistogramDictionary["Reconstructed_Delta1Baryon_Energy_TimeSeparated"].Histogram.Fill(DeltaBaryon.T)
						self.ROOTFile1.HistogramDictionary["Reconstructed_Delta1Baryon_MomentumModulus_TimeSeparated"].Histogram.Fill(DeltaBaryon.SpatialModulus())
						self.ROOTFile1.HistogramDictionary["Reconstructed_Delta1Baryon_Mass_TimeSeparated"].Histogram.Fill(DeltaBaryon.InvariantModulus())
					
				
			for GRTVertex1 in self.Truth_GRTVertices.Vtx: 
				for GRTParticle1 in self.RTTools.getParticles(GRTVertex1):
					# Consider the truth data events. If it contains a Delta Baryon, then retrieve its kinematics for comparison.
					
					if (GRTParticle1.pdg == ParticleCodes.Delta1Baryon):
						
						DeltaBaryon = FourVector.FourVector()
					
						DeltaBaryon.T = GRTParticle1.momentum[3] * 1000 # Unit Conversion
						DeltaBaryon.X = GRTParticle1.momentum[0] * 1000
						DeltaBaryon.Y = GRTParticle1.momentum[1] * 1000
						DeltaBaryon.Z = GRTParticle1.momentum[2] * 1000
						
						self.ROOTFile1.HistogramDictionary["Truth_Delta1Baryon_Energy"].Histogram.Fill(DeltaBaryon.T)
						self.ROOTFile1.HistogramDictionary["Truth_Delta1Baryon_MomentumModulus"].Histogram.Fill(DeltaBaryon.SpatialModulus())
						self.ROOTFile1.HistogramDictionary["Truth_Delta1Baryon_Mass"].Histogram.Fill(DeltaBaryon.InvariantModulus())

		########################################

def main():
	
	Time1 = time.time()
	
	NumberOfEventsToRead = 0
	DefaultNumberOfEventsToRead = 200
	
	InputFileLocator = ""
	DefaultInputFileLocatorUnpurified = "Unpurified_Events.list"
	DefaultInputFileLocatorPurified = "Purified_Events.list"
		
	NumberOfEventsToRead = DefaultNumberOfEventsToRead
	InputFileLocator = DefaultInputFileLocatorPurified
	IsTimingTest = False
	SelectBackgroundEvents = False
	
	CommandLineDeconstructor1 = CommandLineDeconstructor.CommandLineDeconstructor(sys.argv)
		
	if (len(sys.argv) > 1):
		
		for i in range(len(sys.argv)):
			if (i > 0):
				
				ArgumentText = str(sys.argv[i])
				
				ArgumentComponents = ArgumentText.split(":")
				
				if (len(ArgumentComponents) == 2):
					
					if (ArgumentComponents[0] == "NE"):
						print "Desired number of Events: ", ArgumentComponents[1]
						NumberOfEventsToRead = int(ArgumentComponents[1])
						
					if (ArgumentComponents[0] == "P"):
						if (ArgumentComponents[1] == str(0)):
							print "Reading events from:" , DefaultInputFileLocatorUnpurified
							InputFileLocator = DefaultInputFileLocatorUnpurified
						elif (ArgumentComponents[1] == str(1)):
							print "Reading events from:" , DefaultInputFileLocatorPurified
							InputFileLocator = DefaultInputFileLocatorPurified
							
				elif (len(ArgumentComponents) == 1):
					
					if (ArgumentComponents[0] == "TT"):
						print "Perform Timing Test"
						IsTimingTest = True
						
					if (ArgumentComponents[0] == "BE"):
						print "Select Background Events"
						SelectBackgroundEvents = True
	elif (len(sys.argv) == 1):
		print "Reading events from:" , InputFileLocator
	
	libraries.load("nd280/nd280.so")
	
	FileList = open(InputFileLocator)
	
	InputFileLocatorList = FileList.read().splitlines()
		
	OutputROOTFileLocator = FileAdministrator.CreateFilePath(DataLocation, "ROOT/", ".root")
	OutputTextFileLocator = FileAdministrator.CreateFilePath(DataLocation, "Text/", ".txt")
	
	FileAdministrator.CreateLocatorsListFile(DataLocation, InputFileLocatorList)
		
	Analysis1 = Analysis(InputFileLocatorList, OutputROOTFileLocator, OutputTextFileLocator)
	Analysis1.InputTimeTest = IsTimingTest
	Analysis1.SelectBackgroundEvents = SelectBackgroundEvents
	Analysis1.Analyse(NumberOfEventsToRead)
	
	Time2 = time.time()
	
	TotalTime = Time2 - Time1
	
	print TotalTime
	

if __name__ == "__main__":
	main()
