# Analysis
#
# T. R. Bromley and B. T. Milnes
#

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

import DataWriter
import ROOTFile

import TextConstants
import PhysicalConstants
import ParticleCodes

import EventCodes

import Geometry

import TheoreticalParticle
import ReconstructedParticle
import PIDParticle

import SelectionStatistics

import Statistics
import StackedHistogram
import NumericalCuts
import ProcessSeparator


import ProgressMeter

import CommandLine
import FileAdministrator

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
		
		self.EventCodeDeconstructor1 = EventCodes.Deconstructor()
	
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
		
		Module = ROOT.TChain(Module_Reference)
		self.Modules.append(Module)
		
		return Module
	
		
	def Analyse(self, DesiredEventNumber = 999999999):

		sys.stdout = DataWriter.DataWriter(self.OutputTextFileLocator)
		
		MaximumEventNumber = self.LoadInputFiles(DesiredEventNumber)

		self.FGD1 = Geometry.ThreeDimensionalObject(-832.2, 832.2, -777.2, 887.2, 123.45, 446.95)
		self.FGD2 = Geometry.ThreeDimensionalObject(-832.2, 832.2, -777.2, 887.2, 1481.45, 1807.95)
		
		self.FGD1Fiducial = Geometry.ThreeDimensionalObject(-874.51, 874.51, -819.51, 929.51, 136.875, 446.955)#NB: in email he said 1446.955 but i am guessing this is typo
		self.FGD2Fiducial = Geometry.ThreeDimensionalObject(-874.51, 874.51, -819.51, 929.51, 1481.5, 1810)
		
		self.StackedHistograms = {}
	
		self.TruthStatistics = Statistics.Collection("Truth Statistics")
				
		self.TruthStatistics.NewStatistic("NEvents", "Number of Events", 0)
		self.TruthStatistics.NewStatistic("NVertices", "Number of Vertices", 0)
		self.TruthStatistics.NewStatistic("NDeltaToProtonPhoton", "Number of Delta to Proton-Photon Events", 0)
		self.TruthStatistics.NewStatistic("NDeltaToProtonPhotonCC", "Number of Delta to Proton-Photon Charged-Current Events", 0)
		self.TruthStatistics.NewStatistic("NDeltaToProtonPhotonNC", "Number of Delta to Proton-Photon Neutral-Current Events", 0)		
				
		self.ReconstructedStatistics = Statistics.Collection("Reconstructed Statistics")
		
		self.ReconstructedStatistics.NewStatistic("NEventsWithRPID", "Number of Events with at least one Reconstructed PID", 0)
		self.ReconstructedStatistics.NewStatistic("NEventsWithRProton", "Number of Events with at least one Reconstructed Proton Track", 0)
		self.ReconstructedStatistics.NewStatistic("NEventsWithCRProton", "Number of Events with at least one Correctly Reconstructed Proton Track", 0)
		self.ReconstructedStatistics.NewStatistic("NEventsWithIRProton", "Number of Events with Incorrectly Reconstructed Proton Tracks", 0)
		self.ReconstructedStatistics.NewStatistic("NEventsWithCRProton18TPC", "Number of Events with at least one Correctly Reconstructed Proton Track with at least 18 TPC Nodes", 0)		
		self.ReconstructedStatistics.NewStatistic("NEventsWithTECC", "Number of Events with at least one Tracker EC Cluster", 0)		
		self.ReconstructedStatistics.NewStatistic("NEventsWithTECCAndCRProton", "Number of Events with at least one Tracker EC Cluster and one Correctly Reconstructed Proton Track", 0)	
		self.ReconstructedStatistics.NewStatistic("NEventsWithTECCAndCRProtonWithin10D", "Number of Events with at least one Tracker EC Cluster and one Correctly Reconstructed Proton Track where the Photon Direction points to within 10 Degrees of the Proton Track Start", 0)	
		self.ReconstructedStatistics.NewStatistic("NEventsWithTECCAndCRProtonWithin10DWithin500ns", "Number of Events with at least one Tracker EC Cluster and one Correctly Reconstructed Proton Track where the Photon Direction points to within 10 Degrees of the Proton Track Start and where the timing is less than 500ns", 0)
		self.ReconstructedStatistics.NewStatistic("NPIDsWithCRProton", "Number of PIDs Correctly Reconstructed as a Proton Track", 0)
		self.ReconstructedStatistics.NewStatistic("NPIDsWithIRProton", "Number of PIDs Incorrectly Reconstructed as a Proton Track", 0)
		self.ReconstructedStatistics.NewStatistic("NPIDsWithRProtonRatio", "Ratio of Correctly Reconstructed Proton Track PIDs", 0)
	
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
		
		self.StackedHistograms["ReconProtonTrueEnergy"]=StackedHistogram.StackedHistogram("Recon_Proton_True_Energy", "True energy of particles reconstructed as protons", 0.7, 0.65, 0.86, 0.88, "Energy (GeV)", "Number",  "Proton/Truth/Energy")
		
		self.StackedHistograms["ReconProtonReconMomentum"]=StackedHistogram.StackedHistogram("Recon_Proton_Recon_Momentum", "Reconstructed momentum of particles reconstructed as protons", 0.7, 0.65, 0.86, 0.88, "Momentum (GeV)", "Number", "Proton/Recon/Momentum/")
			
		self.ROOTFile1.NewHistogram1D("Recon_Truth_Proton_Momentum", "Recon momentum minus truth momentum for PIDs reconstructed as protons", "Momentum (GeV)", "Number", 100, -500, 500, "PIDs/Recon/Momentum")
		self.ROOTFile1.NewHistogram1D("Truth_Proton_Momentum", "Truth momentum for PIDs reconstructed as protons", "Momentum (GeV)", "Number", 100, 0, 5000, "PIDs/Truth/Momentum")
				
		self.ROOTFile1.NewHistogram1D("PhotonAngles", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position", "Angle", "Number", 100, -90, 90, "Photon/Recon/All/")
		self.ROOTFile1.NewHistogram1D("ProtonPhotonTimeSeparations", "Time Separation between the Reconstructed Proton Track and Photon EC Cluster", "Time Separation", "Number", 100, 0, 4000, "Photon/Recon/")
		self.StackedHistograms["PhotonAnglesStacked"]=StackedHistogram.StackedHistogram("Photon_Angles_Stacked", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position", 0.7, 0.65, 0.86, 0.88, "Angle", "Number",  "Photon/Recon/All/")
		
		self.ROOTFile1.NewHistogram1D("SelectedPhotonAngles", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position for the single proton and the single selected photon", "Angle", "Number", 100, -90, 90, "Photon/Recon/Selected/")
		self.StackedHistograms["SelectedPhotonAnglesStacked"]=StackedHistogram.StackedHistogram("Selected_Photon_Angles_Stacked", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position for the single proton and the single selected photon", 0.7, 0.65, 0.86, 0.88, "Angle", "Number",  "Photon/Recon/Selected/")
		
		self.StackedHistograms["PhotonAnglesStackedTrack"]=StackedHistogram.StackedHistogram("Photon_Angles_Stacked_Track", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position for the single proton and the single selected photon", 0.7, 0.65, 0.86, 0.88, "Angle", "Number",  "Photon/Recon/Track/")
		self.StackedHistograms["PhotonAnglesStackedShower"]=StackedHistogram.StackedHistogram("Photon_Angles_Stacked_Shower", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position for the single proton and the single selected photon", 0.7, 0.65, 0.86, 0.88, "Angle", "Number",  "Photon/Recon/Shower/")
		self.StackedHistograms["SelectedPhotonAnglesStackedTrack"]=StackedHistogram.StackedHistogram("Selected_Photon_Angles_Stacked_Track", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position for the single proton and the single selected photon", 0.7, 0.65, 0.86, 0.88, "Angle", "Number",  "Photon/Recon/Selected/Track/")
		self.StackedHistograms["SelectedPhotonAnglesStackedShower"]=StackedHistogram.StackedHistogram("Selected_Photon_Angles_Stacked_Track", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position for the single proton and the single selected photon", 0.7, 0.65, 0.86, 0.88, "Angle", "Number",  "Photon/Recon/Selected/Shower/")

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
		
		self.StackedHistograms["FinalInvariantMass"]=StackedHistogram.StackedHistogram("Final_Invariant_Mass", "Invariant Mass of Delta Baryon after all cuts have been applied", 0.7, 0.65, 0.86, 0.88, "Mass (GeV)", "Number", "Cuts/Invariant Mass/")
		self.StackedHistograms["InvariantMassAllECal"]=StackedHistogram.StackedHistogram("Invariant_Mass_All_ECal", "Invariant Mass of Delta Baryon from comparison of single photon to all ECals", 0.7, 0.65, 0.86, 0.88, "Mass (GeV)", "Number", "Cuts/Invariant Mass/All ECal/")
		
		self.StackedHistograms["Pi0MesonMass"] = StackedHistogram.StackedHistogram("Pi0_Meson_Mass", "Invariant Mass of Pi0 Meson from matching of ECal clusters", 0.7, 0.65, 0.86, 0.88, "Mass (GeV)", "Number", "Pi0Meson/Invariant Mass/")
			
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
				
			
			self.StackedHistograms["NormalisedPurity"]=StackedHistogram.StackedHistogram("Normalised_Purity", "Constituent processes after each cut (Normalised)", 0.7, 0.65, 0.86, 0.88, "Cuts", "Events Remaining", "Cuts/Normalised/")

			NormalisedPurityTitle = "Purity as a function of selection for"

			for CriteriaListCounter in xrange(CutNumber):
								
				if(self.SelectionStatisticsList[CriteriaListCounter].Purity > 0):
					
					self.StackedHistograms["NormalisedPurity"].AttemptToFill2D(NormalisedPurityTitle, "Delta -> p gamma interactions", "NormalisedPurity:DeltaPGamma", "Selections", "Purity", CutNumber, 0, CutNumber, "Cuts/Normalised/Constituent Histograms/", CriteriaListCounter, self.SelectionStatisticsList[CriteriaListCounter].Purity, "Delta -> p gamma Interactions")
				
				if(self.SelectionStatisticsList[CriteriaListCounter].PionPurity > 0):
					
					self.StackedHistograms["NormalisedPurity"].AttemptToFill2D(NormalisedPurityTitle, "Delta -> p pi interactions", "NormalisedPurity:DeltaPPi", "Selections", "Purity", CutNumber, 0, CutNumber, "Cuts/Normalised/Constituent Histograms/", CriteriaListCounter, self.SelectionStatisticsList[CriteriaListCounter].PionPurity, "Delta -> p pi Interactions")
			
				if(self.SelectionStatisticsList[CriteriaListCounter].RPPurity > 0):
					
					self.StackedHistograms["NormalisedPurity"].AttemptToFill2D(NormalisedPurityTitle, "Other Resonance Production", "NormalisedPurity:OtherResonance", "Selections", "Purity", CutNumber, 0, CutNumber, "Cuts/Normalised/Constituent Histograms/", CriteriaListCounter, self.SelectionStatisticsList[CriteriaListCounter].RPPurity, "Other Resonance Production")
					
				if(self.SelectionStatisticsList[CriteriaListCounter].QSPurity > 0):
					
					self.StackedHistograms["NormalisedPurity"].AttemptToFill2D(NormalisedPurityTitle, "Quasi-Elastic Scattering", "NormalisedPurity:QES", "Selections", "Purity", CutNumber, 0, CutNumber, "Cuts/Normalised/Constituent Histograms/", CriteriaListCounter, self.SelectionStatisticsList[CriteriaListCounter].QSPurity, "Quasi-Elastic Scattering")
				
				if(self.SelectionStatisticsList[CriteriaListCounter].ESPurity > 0):
										
					self.StackedHistograms["NormalisedPurity"].AttemptToFill2D(NormalisedPurityTitle, "Elastic Scattering", "NormalisedPurity:ES", "Selections", "Purity", CutNumber, 0, CutNumber, "Cuts/Normalised/Constituent Histograms/", CriteriaListCounter, self.SelectionStatisticsList[CriteriaListCounter].ESPurity, "Elastic Scattering")
			
				if(self.SelectionStatisticsList[CriteriaListCounter].DISPurity > 0):
					
					self.StackedHistograms["NormalisedPurity"].AttemptToFill2D(NormalisedPurityTitle, "Deep Inelastic Scattering", "NormalisedPurity:DIS", "Selections", "Purity", CutNumber, 0, CutNumber, "Cuts/Normalised/Constituent Histograms/", CriteriaListCounter, self.SelectionStatisticsList[CriteriaListCounter].DISPurity, "Deep Inelastic Scattering")
					
				if(self.SelectionStatisticsList[CriteriaListCounter].CSPurity > 0):
					
					self.StackedHistograms["NormalisedPurity"].AttemptToFill2D(NormalisedPurityTitle, "Coherent Scattering", "NormalisedPurity:C", "Selections", "Purity", CutNumber, 0, CutNumber, "Cuts/Normalised/Constituent Histograms/", CriteriaListCounter, self.SelectionStatisticsList[CriteriaListCounter].CSPurity, "Coherent Scattering")
										
				if(self.SelectionStatisticsList[CriteriaListCounter].OtherPurity > 0):
					
					self.StackedHistograms["NormalisedPurity"].AttemptToFill2D(NormalisedPurityTitle, "Other Interactions", "NormalisedPurity:Other", "Selections", "Purity", CutNumber, 0, CutNumber, "Cuts/Normalised/Constituent Histograms/", CriteriaListCounter, self.SelectionStatisticsList[CriteriaListCounter].OtherPurity, "Other Interactions")
			
			for Histogram1 in self.StackedHistograms["NormalisedPurity"].HistogramDictionary.itervalues():
				for CutCounter in xrange(len(self.SelectionStatisticsList)):
					
					if(CutCounter == 0):
						BinLabel = "Starting Events"
					else:
						BinLabel = "Criterion " + str(CutCounter)
					
					Histogram1.Histogram.GetXaxis().SetBinLabel(CutCounter+1, BinLabel)
	
			############## Application of truth to criteria
				
			self.StackedHistograms["CutPurity"]=StackedHistogram.StackedHistogram("Cut_Purity", "Constituent Processes for the Events after every Selection",0.7,0.65,0.86,0.88, "Cuts", "Events Remaining", "Cuts/Energy/")

			for CutCounter in xrange(len(self.SelectionStatisticsList)):
				for FillCounter in xrange(self.SelectionStatisticsList[CutCounter].TruthDelta):
					self.StackedHistograms["CutPurity"].AttemptToFill1D(NormalisedPurityTitle, "Delta -> p gamma interactions", "Purity:DeltaPGamma", "Selections", "Purity", CutNumber, 0, CutNumber, "Cuts/Energy/Constituent Histograms/", CutCounter, "Delta -> p gamma Interactions")
				for FillCounter in xrange(self.SelectionStatisticsList[CutCounter].ReconstructedDelta):
					self.StackedHistograms["CutPurity"].AttemptToFill1D(NormalisedPurityTitle, "Delta -> p pi interactions", "Purity:DeltaPPi", "Selections", "Purity", CutNumber, 0, CutNumber, "Cuts/Energy/Constituent Histograms/", CutCounter, "Delta -> p pi Interactions")
				for FillCounter in xrange(self.SelectionStatisticsList[CutCounter].OtherRPInteraction):
					self.StackedHistograms["CutPurity"].AttemptToFill1D(NormalisedPurityTitle, "Other Resonance Production", "Purity:OtherResonance", "Selections", "Purity", CutNumber, 0, CutNumber, "Cuts/Energy/Constituent Histograms/", CutCounter, "Other Resonance Production")
				for FillCounter in xrange(self.SelectionStatisticsList[CutCounter].QSInteraction):
					self.StackedHistograms["CutPurity"].AttemptToFill1D(NormalisedPurityTitle, "Quasi-Elastic Scattering", "Purity:QES", "Selections", "Purity", CutNumber, 0, CutNumber, "Cuts/Energy/Constituent Histograms/", CutCounter, "Quasi-Elastic Scattering")
				for FillCounter in xrange(self.SelectionStatisticsList[CutCounter].ESInteraction):
					self.StackedHistograms["CutPurity"].AttemptToFill1D(NormalisedPurityTitle, "Elastic Scattering", "Purity:ES", "Selections", "Purity", CutNumber, 0, CutNumber, "Cuts/Energy/Constituent Histograms/", CutCounter, "Elastic Scattering")
				for FillCounter in xrange(self.SelectionStatisticsList[CutCounter].DISInteraction):
					self.StackedHistograms["CutPurity"].AttemptToFill1D(NormalisedPurityTitle, "Deep Inelastic Scattering", "Purity:DIS", "Selections", "Purity", CutNumber, 0, CutNumber, "Cuts/Energy/Constituent Histograms/", CutCounter, "Deep Inelastic Scattering")
				for FillCounter in xrange(self.SelectionStatisticsList[CutCounter].CSInteraction):
					self.StackedHistograms["CutPurity"].AttemptToFill1D(NormalisedPurityTitle, "Coherent Scattering", "Purity:C", "Selections", "Purity", CutNumber, 0, CutNumber, "Cuts/Energy/Constituent Histograms/", CutCounter, "Coherent Scattering")
				for FillCounter in xrange(self.SelectionStatisticsList[CutCounter].OtherInteraction):
					self.StackedHistograms["CutPurity"].AttemptToFill1D(NormalisedPurityTitle, "Other Interactions", "Purity:Other", "Selections", "Purity", CutNumber, 0, CutNumber, "Cuts/Energy/Constituent Histograms/", CutCounter, "Other Interactions")
					
			for Histogram1 in self.StackedHistograms["CutPurity"].HistogramDictionary.itervalues():
				for CutCounter in xrange(len(self.SelectionStatisticsList)):
				
					if(CutCounter == 0):
						BinLabel = "Starting Events"
					else:
						BinLabel = "Criterion " + str(CutCounter)
				
					Histogram1.Histogram.GetXaxis().SetBinLabel(CutCounter+1, BinLabel)
					
			###############			
						
			self.EfficiencyStatistics = Statistics.Collection("Efficiency Statistics")
			
			self.EfficiencyStatistics.NewStatistic("NEvents0", "Initial Number of Events", self.SelectionStatisticsList[0].EventsRemaining)
			self.EfficiencyStatistics.NewStatistic("NEvents1", "Selection 1 - At least one reconstructed track was recorded - Events Remaining", self.SelectionStatisticsList[1].EventsRemaining)
			self.EfficiencyStatistics.NewStatistic("NEvents2", "Selection 2 - The track has at least 18 TPC nodes - Events Remaining", self.SelectionStatisticsList[2].EventsRemaining)
			self.EfficiencyStatistics.NewStatistic("NEvents3", "Selection 3 - At least one proton-identified track - Events Remaining", self.SelectionStatisticsList[3].EventsRemaining)
			self.EfficiencyStatistics.NewStatistic("NEvents4", "Selection 4 - Only one proton-identified track - Events Remaining", self.SelectionStatisticsList[4].EventsRemaining)
			self.EfficiencyStatistics.NewStatistic("NEvents5", "Selection 5 - Proton track is the first track into the detector - Events Remaining", self.SelectionStatisticsList[5].EventsRemaining)
			self.EfficiencyStatistics.NewStatistic("NEvents6", "Selection 6 - Proton track began in the FGDs - Events Remaining", self.SelectionStatisticsList[6].EventsRemaining)
			
			Selection7 = "Selection 7 - Fewer than " + str(NumericalCuts.DeltaPGammaMultiplicity) + " PIDs in total - Events Remaining"
			self.EfficiencyStatistics.NewStatistic("NEvents7", Selection7, self.SelectionStatisticsList[7].EventsRemaining)
			self.EfficiencyStatistics.NewStatistic("NEvents8", "Selection 8 - At least one EC cluster was recorded - Events Remaining", self.SelectionStatisticsList[8].EventsRemaining)
			
			Selection9 = "Selection 9 - The smallest angle was less than " + str(NumericalCuts.MinimumAngle) + " degees - Events Remaining"
			self.EfficiencyStatistics.NewStatistic("NEvents9", Selection9, self.SelectionStatisticsList[9].EventsRemaining)
			
			Selection10 = "Selection 10 - The calculated invariant mass was within " + str(NumericalCuts.InvariantMassVariance) + " MeV of the true Delta1 Baryon mass, " + str(PhysicalConstants.Delta1BaryonMass) + " MeV - Events Remaining"
			self.EfficiencyStatistics.NewStatistic("NEvents10", Selection10, self.SelectionStatisticsList[10].EventsRemaining)
			
			self.ReconstructedStatistics.Statistics["NPIDsWithRProtonRatio"].Quantity= float(self.ReconstructedStatistics.Statistics["NPIDsWithCRProton"].Quantity)/float(self.ReconstructedStatistics.Statistics["NPIDsWithCRProton"].Quantity+self.ReconstructedStatistics.Statistics["NPIDsWithIRProton"].Quantity)
			
	
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
		
		for StackedHistogramName1, StackedHistogram1 in self.StackedHistograms.iteritems():
			
			StackedHistogram1.AutoPrepare("f")
		
			CanvasTitle = "Canvas of " + StackedHistogramName1
		
			try:
				self.ROOTFile1.NewStackedHistogramCanvas(StackedHistogramName1, *StackedHistogram1.StackedHistogramCanvas(StackedHistogramName1, CanvasTitle, 700, 500))
			except:
				pass
		
			StackedHistogram1.DrawConstituentHistograms(self.ROOTFile1)
		
		del sys.stdout#Closes .txt file and returns to printing only to console

		self.ROOTFile1.Close()
		
	
	def runEvent(self):
	
		self.TruthStatistics.Statistics["NEvents"].Quantity += 1
	
		###### First loop over the true genie data to look for information about the delta interactions
	
		DeltaPGammaEvent = False
		Delta1BaryonToProtonPi0MesonEvent = False
	
		NVertices = self.Truth_GRTVertices.NVtx

		InteractionType = ""
		
		
		
		########################################
		# TRUTH DATA #
		########################################
		
		Delta1Hardons = []
		TruePhotons = []
		
		
		"""
		SelectionReferences = ["A", "B", "C", "D", "E"]
		
		Event1 = Simulation.Event()
		
		Event1 = self.EventCollection1.InterpretEvent(self.Truth_GRTVertices.Vtx, self.Reconstructed_Global.PIDs, self.Truth_Trajectories.Trajectories, self.Reconstructed_TEC.ReconObject, SelectionReferences) 
		
		self.TruthStatistics.Statistics["NVertices"].Quantity += Event1.TrueEvent.NumberOfTrueVertices
		
		if (Event1.TrueEvent.
		self.TruthStatistics.Statistics["NDeltaToProtonPhoton"].Quantity += 1
		self.TruthStatistics.Statistics["NDeltaToProtonPhotonCC"].Quantity += 1
		self.TruthStatistics.Statistics["NDeltaToProtonPhotonNC"].Quantity += 1
		
		"""
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
			
			Current = self.EventCodeDeconstructor1.Elements["Current Code"].Content
			InteractionType = self.EventCodeDeconstructor1.Elements["Process Code"].Content
			
			
			#for Element1 in self.EventCodeDeconstructor1.Elements:
			#	if (Element1.Reference == "Current Code"):
			#		Current = Element1.Content
			#	if (Element1.Reference == "Process Code"):
			#		InteractionType = Element1.Content
													
							
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

		EventProcess = ProcessSeparator.EventProcess(DeltaPGammaEvent, Delta1BaryonToProtonPi0MesonEvent, InteractionType)


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
		IncorrectlyReconstructedProton = 0
		
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
				
				self.ReconstructedStatistics.Statistics["NPIDsWithCRProton"].Quantity += 1
				
			elif (PIDObject1.ReconParticleID == ParticleCodes.Proton):
				IncorrectlyReconstructedProton +=1
				self.ReconstructedStatistics.Statistics["NPIDsWithIRProton"].Quantity += 1
	
			if (PIDObject1.ReconParticleID == ParticleCodes.Proton):

				self.StackedHistograms["ReconProtonTrueEnergy"].ConstituentFill1D(ParticleCodes.ParticleDictionary, PIDObject1.TrueParticleID, PIDObject1.TrueEnergy,"The Proton-Like Track reconstructed front momentum contribution from a true", "Energy (GeV)", "Number", 100, 0, 5000, "ProtonLikeTrueEnergy")
				self.StackedHistograms["ReconProtonReconMomentum"].ConstituentFill1D(ParticleCodes.ParticleDictionary, PIDObject1.TrueParticleID, PIDObject1.ReconFrontMomentum,"The Proton-Like Track true energy contribution from a true", "Momentum (GeV)", "Number", 100, 0, 3000, "ProtonLikeReconFrontMomentum")

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
			
		if (IncorrectlyReconstructedProton > 0):
			ProtonIsIncorrectlyReconstructed = True
		else:
			ProtonIsIncorrectlyReconstructed = False
			
		if (ReconstructedProtonTrackNumber > 0):
			ReconstructedProtonTrack = True
		else:
			ReconstructedProtonTrack = False
		
		############################## ECal cluster section ###################################
				
		#I think we will only look at the Tracker ECal (TPC+FGD) as the POD ECal is mainly used for POD !! What about downstream ECal
				
		PhotonEnergyMomentumList = []
		PhotonList = []
		
		SmallestAngle = 180
		
		for TECObject in self.Reconstructed_TEC.ReconObject:#Loop over these reconstructed objects
			
			ECEnergy = TECObject.EMEnergyFit_Result#The energy of photon
			
			Photon1 = ReconstructedParticle.ReconstructedParticle()
			
			Photon1.EnergyMomentum.T = ECEnergy
										
			if (TECObject.IsShowerLike):#Check if ECal reconstruction is tracklike or showerlike, it shouldnt matter which for the photon, but the directions are different
				ECUnitDirection = Geometry.ThreeVector(TECObject.Shower.Direction.X(), TECObject.Shower.Direction.Y(), TECObject.Shower.Direction.Z())
				
				Photon1.DirectionIsValid = True
				
				Photon1.Position.T = TECObject.Shower.Position.T()
				Photon1.Position.X = TECObject.Shower.Position.X()
				Photon1.Position.Y = TECObject.Shower.Position.Y()
				Photon1.Position.Z = TECObject.Shower.Position.Z()
				
				for Proton1 in ProtonList:

					Angle1 = 180
						
					Line1 = Geometry.ThreeVector()
					Line2 = Geometry.ThreeVector()
					
					Line1.X = Proton1.Position.X - Photon1.Position.X
					Line1.Y = Proton1.Position.Y - Photon1.Position.Y
					Line1.Z = Proton1.Position.Z - Photon1.Position.Z
					
					Line2.X = - ECUnitDirection.X
					Line2.Y = - ECUnitDirection.Y
					Line2.Z = - ECUnitDirection.Z
					
					Angle1 = Geometry.FindAngle(Line1, Line2)
			
					self.StackedHistograms["PhotonAnglesStackedShower"].ConstituentFill1D(ProcessSeparator.ProcessDictionary, EventProcess, Angle1, "Angle for constituent", "Mass (GeV)", "Number", 100, -90, 90, "PhotonAngleShower")
				
				if (len(ProtonList) > 0):
					
					Proton1 = ProtonList[0]
					
					Angle1 = 180
						
					Line1 = Geometry.ThreeVector()
					Line2 = Geometry.ThreeVector()
					
					Line1.X = Proton1.Position.X - Photon1.Position.X
					Line1.Y = Proton1.Position.Y - Photon1.Position.Y
					Line1.Z = Proton1.Position.Z - Photon1.Position.Z
					
					Line2.X = - ECUnitDirection.X
					Line2.Y = - ECUnitDirection.Y
					Line2.Z = - ECUnitDirection.Z
					
					Angle1 = Geometry.FindAngle(Line1, Line2)
					
					if (math.fabs(Angle1) < math.fabs(SmallestAngle)):
						
						SmallestAngle = Angle1
					
				self.StackedHistograms["SelectedPhotonAnglesStackedShower"].ConstituentFill1D(ProcessSeparator.ProcessDictionary, EventProcess, SmallestAngle, "Angle for constituent", "Mass (GeV)", "Number", 100, -90, 90, "SelectedPhotonAngleShower")
			
			SmallestAngle = 180
				
			if (TECObject.IsTrackLike):
				ECUnitDirection = Geometry.ThreeVector(TECObject.Track.Direction.X(), TECObject.Track.Direction.Y(), TECObject.Track.Direction.Z())
						
				Photon1.Position.T = TECObject.Track.Position.T()
				Photon1.Position.X = TECObject.Track.Position.X()
				Photon1.Position.Y = TECObject.Track.Position.Y()
				Photon1.Position.Z = TECObject.Track.Position.Z()
				
				for Proton1 in ProtonList:

					Angle1 = 180
						
					Line1 = Geometry.ThreeVector()
					Line2 = Geometry.ThreeVector()
					
					Line1.X = Proton1.Position.X - Photon1.Position.X
					Line1.Y = Proton1.Position.Y - Photon1.Position.Y
					Line1.Z = Proton1.Position.Z - Photon1.Position.Z
					
					Line2.X = - ECUnitDirection.X
					Line2.Y = - ECUnitDirection.Y
					Line2.Z = - ECUnitDirection.Z
					
					Angle1 = Geometry.FindAngle(Line1, Line2)
			
					self.StackedHistograms["PhotonAnglesStackedTrack"].ConstituentFill1D(ProcessSeparator.ProcessDictionary, EventProcess, Angle1, "Angle for constituent", "Mass (GeV)", "Number", 100, -90, 90, "PhotonAngleShowerTrack")
					
				if (len(ProtonList) > 0):
					
					Proton1 = ProtonList[0]
					
					Angle1 = 180
						
					Line1 = Geometry.ThreeVector()
					Line2 = Geometry.ThreeVector()
					
					Line1.X = Proton1.Position.X - Photon1.Position.X
					Line1.Y = Proton1.Position.Y - Photon1.Position.Y
					Line1.Z = Proton1.Position.Z - Photon1.Position.Z
					
					Line2.X = - ECUnitDirection.X
					Line2.Y = - ECUnitDirection.Y
					Line2.Z = - ECUnitDirection.Z
					
					Angle1 = Geometry.FindAngle(Line1, Line2)
					
					if (math.fabs(Angle1) < math.fabs(SmallestAngle)):
						
						SmallestAngle = Angle1
					
				self.StackedHistograms["SelectedPhotonAnglesStackedTrack"].ConstituentFill1D(ProcessSeparator.ProcessDictionary, EventProcess, SmallestAngle, "Angle for constituent", "Mass (GeV)", "Number", 100, -90, 90, "SelectedPhotonAngleTrack")
				
				
				
						
			#if (ECUnitDirection.Modulus() < 1.1):#For some reason there sometimes are occurences where the magnitude is far above 1. This if filters them out. We should probably look into this further
			#This thing has the potential to mess up later if you are looping over NTrackerECalRecon!!!!
			Photon1.EnergyMomentum.X = ECUnitDirection.X * ECEnergy / ECUnitDirection.Modulus()#Solution: Renormalisation
			Photon1.EnergyMomentum.Y = ECUnitDirection.Y * ECEnergy / ECUnitDirection.Modulus()
			Photon1.EnergyMomentum.Z = ECUnitDirection.Z * ECEnergy / ECUnitDirection.Modulus()
										
			Photon1.Direction.X = ECUnitDirection.X
			Photon1.Direction.Y = ECUnitDirection.Y
			Photon1.Direction.Z = ECUnitDirection.Z
			
			PhotonList.append(Photon1)
				
		NTrackerECalRecon = len(PhotonList)#Number of reconstructed objects in the ECal	!!This is a temporary fix to look at the Modulus problem	
		
		#################### Toms new photon cut section ####### Currently we have many potential photons and a single proton.
		# First, the photon with the "best" angle (smallest) is chosen as the single photon ... then we can look at invariant mass
		
		SmallestAngle = 180
		DeltaBaryonMass = 0
		
		if (ReconstructedProtonTrackNumber == 1):
			
			Proton1 = ProtonList[0]
			
			for Photon1 in PhotonList:
							
				Angle1 = 180
					
				Line1 = Geometry.ThreeVector()
				Line2 = Geometry.ThreeVector()
				
				Line1.X = Proton1.Position.X - Photon1.Position.X
				Line1.Y = Proton1.Position.Y - Photon1.Position.Y
				Line1.Z = Proton1.Position.Z - Photon1.Position.Z
				
				Line2.X = - Photon1.Direction.X
				Line2.Y = - Photon1.Direction.Y
				Line2.Z = - Photon1.Direction.Z
				
				Angle1 = Geometry.FindAngle(Line1, Line2)
				
				if (math.fabs(Angle1) < math.fabs(SmallestAngle)):
					
					SmallestAngle = Angle1
					
					SelectedPhoton = Photon1
					SelectedProton = Proton1
				
				for Photon2 in PhotonList:#For finding invariant mass of pi0
					
					if (Photon2 != Photon1):#Is this valid in python?
					
						Pi0Meson = Geometry.FourVector()
						
						Pi0Meson.T = Photon1.EnergyMomentum.T + Photon2.EnergyMomentum.T
						Pi0Meson.X = Photon1.EnergyMomentum.X + Photon2.EnergyMomentum.X
						Pi0Meson.Y = Photon1.EnergyMomentum.Y + Photon2.EnergyMomentum.Y
						Pi0Meson.Z = Photon1.EnergyMomentum.Z + Photon2.EnergyMomentum.Z
						
						self.StackedHistograms["Pi0MesonMass"].ConstituentFill1D(ProcessSeparator.ProcessDictionary, EventProcess, Pi0Meson.InvariantModulus(), "Pi0Meson mass contribution for constituent", "Mass (GeV)", "Number", 100, 0, 1000, "Pi0MesonMass")
					
					
			self.ROOTFile1.HistogramDictionary["SelectedPhotonAngles"].Histogram.Fill(SmallestAngle)
			self.StackedHistograms["SelectedPhotonAnglesStacked"].ConstituentFill1D(ProcessSeparator.ProcessDictionary, EventProcess, SmallestAngle, "Angle for constituent", "Mass (GeV)", "Number", 100, -90, 90, "SelectedPhotonAngle")

			if (len(PhotonList) > 0):
			
				DeltaBaryon = Geometry.FourVector()
						
				DeltaBaryon.T = SelectedPhoton.EnergyMomentum.T + SelectedProton.EnergyMomentum.T # Delta Baryon Energy
				DeltaBaryon.X = SelectedPhoton.EnergyMomentum.X + SelectedProton.EnergyMomentum.X
				DeltaBaryon.Y = SelectedPhoton.EnergyMomentum.Y + SelectedProton.EnergyMomentum.Y
				DeltaBaryon.Z = SelectedPhoton.EnergyMomentum.Z + SelectedProton.EnergyMomentum.Z
				
				DeltaBaryonMass = DeltaBaryon.InvariantModulus()
		
		############################## Summary Section ########################################

		if (ReconstructedProtonTrack):#Counts number of events with at least one reconstructed proton track
			self.ReconstructedStatistics.Statistics["NEventsWithRProton"].Quantity += 1
		if (ProtonIsCorrectlyReconstructed):
			self.ReconstructedStatistics.Statistics["NEventsWithCRProton"].Quantity += 1
		if (ProtonIsIncorrectlyReconstructed):
			self.ReconstructedStatistics.Statistics["NEventsWithIRProton"].Quantity += 1
		if (NTrackerECalRecon > 0):
			self.ReconstructedStatistics.Statistics["NEventsWithTECC"].Quantity += 1
		if (ReconstructedProtonTrack and NTrackerECalRecon > 0):
			self.ReconstructedStatistics.Statistics["NEventsWithTECCAndCRProton"].Quantity += 1
		if (math.fabs(DeltaBaryonMass - PhysicalConstants.Delta1BaryonMass) < NumericalCuts.InvariantMassVariance):
			SatisfiesInvariantMass = True
		else:
			SatisfiesInvariantMass = False
		
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
			
		if (len(PIDObjectList) <= NumericalCuts.DeltaPGammaMultiplicity and Criteria[6]):
			Criteria.append(True)
		else:
			Criteria.append(False)
			
		if (NTrackerECalRecon > 0 and Criteria[7]):
			Criteria.append(True)
		else:
			Criteria.append(False)

		if (SmallestAngle <= NumericalCuts.MinimumAngle and Criteria[8]):
			Criteria.append(True)
		else:
			Criteria.append(False)
			
		if (SatisfiesInvariantMass and Criteria[9]):
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
						
			self.StackedHistograms["FinalInvariantMass"].ConstituentFill1D(ProcessSeparator.ProcessDictionary, EventProcess, DeltaBaryon.InvariantModulus(), "Invariant Mass after all cuts for constituent", "Mass (GeV)", "Number", 100, 0, 3000, "FinalInvariantMass")
						
		if (Criteria[7]):#Matching Single proton to Every ECal cluster
			
			for Photon1 in PhotonList:
				
				DeltaBaryon = Geometry.FourVector()
						
				DeltaBaryon.T = Photon1.EnergyMomentum.T + SelectedProton.EnergyMomentum.T # Delta Baryon Energy
				DeltaBaryon.X = Photon1.EnergyMomentum.X + SelectedProton.EnergyMomentum.X
				DeltaBaryon.Y = Photon1.EnergyMomentum.Y + SelectedProton.EnergyMomentum.Y
				DeltaBaryon.Z = Photon1.EnergyMomentum.Z + SelectedProton.EnergyMomentum.Z
			
				self.StackedHistograms["InvariantMassAllECal"].ConstituentFill1D(ProcessSeparator.ProcessDictionary, EventProcess, DeltaBaryon.InvariantModulus(), "Invariant Mass for constituent", "Mass (GeV)", "Number", 100, 0, 3000, "InvariantMassAllECal")
						
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
					
					DeltaBaryon = Geometry.FourVector()
					
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
					
					Line1 = Geometry.ThreeVector()
					Line2 = Geometry.ThreeVector()
					
					Line1.X = Proton1.Position.X - Photon1.Position.X
					Line1.Y = Proton1.Position.Y - Photon1.Position.Y
					Line1.Z = Proton1.Position.Z - Photon1.Position.Z
					
					Line2.X = - Photon1.Direction.X
					Line2.Y = - Photon1.Direction.Y
					Line2.Z = - Photon1.Direction.Z
					
					Angle1 = Geometry.FindAngle(Line1, Line2)
					TimeSeparation = math.fabs(float(Proton1.Position.T) - float(Photon1.Position.T))
						
					if (ReconstructedProtonTrack and NTrackerECalRecon > 0 and Angle1 < 10 and Angle1 > -10 and Photon1.DirectionIsValid == True):
						self.ReconstructedStatistics.Statistics["NEventsWithTECCAndCRProtonWithin10D"].Quantity += 1
						
						if (TimeSeparation < 250):
							self.ReconstructedStatistics.Statistics["NEventsWithTECCAndCRProtonWithin10DWithin500ns"].Quantity += 1
					
					self.ROOTFile1.HistogramDictionary["PhotonAngles"].Histogram.Fill(Angle1)#!! Should this not be Angle1? Ive now changed it
					self.StackedHistograms["PhotonAnglesStacked"].ConstituentFill1D(ProcessSeparator.ProcessDictionary, EventProcess, Angle1, "Angle for constituent", "Mass (GeV)", "Number", 100, -90, 90, "PhotonAngle")
					self.ROOTFile1.HistogramDictionary["ProtonPhotonTimeSeparations"].Histogram.Fill(TimeSeparation)
					
					
					if (TimeSeparation < 250):
																						
						self.ROOTFile1.HistogramDictionary["Reconstructed_Delta1Baryon_Energy_TimeSeparated"].Histogram.Fill(DeltaBaryon.T)
						self.ROOTFile1.HistogramDictionary["Reconstructed_Delta1Baryon_MomentumModulus_TimeSeparated"].Histogram.Fill(DeltaBaryon.SpatialModulus())
						self.ROOTFile1.HistogramDictionary["Reconstructed_Delta1Baryon_Mass_TimeSeparated"].Histogram.Fill(DeltaBaryon.InvariantModulus())
					
				
			for GRTVertex1 in self.Truth_GRTVertices.Vtx: 
				for GRTParticle1 in self.RTTools.getParticles(GRTVertex1):
					# Consider the truth data events. If it contains a Delta Baryon, then retrieve its kinematics for comparison.
					
					if (GRTParticle1.pdg == ParticleCodes.Delta1Baryon):
						
						DeltaBaryon = Geometry.FourVector()
					
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
	
	CommandLineDeconstructor1 = CommandLine.Deconstructor(sys.argv)
		
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
