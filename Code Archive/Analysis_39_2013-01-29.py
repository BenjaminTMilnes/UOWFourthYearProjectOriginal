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

import SelectionStatistics

import Statistics
import StackedHistogram
import NumericalCuts
import ProcessSeparator


import ProgressMeter

import CommandLine
import FileAdministrator

import Simulation
import Charts
import Particles

Now = datetime.datetime.now()
DataLocation = "/storage/epp2/phujce/Final Year Project/Main/Data Archive/"

class Analysis:
	
	def __init__(This, InputFileLocatorList, OutputROOTFileLocator, OutputTextFileLocator):
		
		This.InputFileLocatorList = InputFileLocatorList
		This.OutputROOTFileLocator = OutputROOTFileLocator
		This.OutputTextFileLocator = OutputTextFileLocator
		
		This.Histograms = {}
		This.DataCollections = []
		This.Modules = []
		
		This.BasicInformation = This.LoadModule("HeaderDir/BasicHeader")
		
		This.Truth_GRTVertices = This.LoadModule("TruthDir/GRooTrackerVtx")
		This.Truth_Vertices = This.LoadModule("TruthDir/Vertices")
		This.Truth_Trajectories = This.LoadModule("TruthDir/Trajectories")
		
		This.Reconstructed_Global = This.LoadModule("ReconDir/Global")
		This.Reconstructed_TEC = This.LoadModule("ReconDir/TrackerECal")
		
		This.RTTools = RooTrackerTools.RooTrackerTools()
		
		This.EventCodeDeconstructor1 = EventCodes.Deconstructor()
	
		This.SelectionDictionary = {}
		
		This.SelectionDictionary["DeltaPGamma"] = []
		This.SelectionDictionary["DeltaPPi"] = []
		
		This.InputTimeTest = False
		This.SelectBackgroundEvents = False
		
		This.BackgroundEventNumbers = []
		This.BackgroundPiMesonEventNumbers = []
		
		This.EventCollection1 = Simulation.EventCollection()
		
		This.HistogramCollection1 = Charts.HistogramCollection()
		
		This.EventPrintoutString = ""
		
		This.EventPrinoutFile = open("Test.txt", "w")
	
	def LoadInputFiles(This, DesiredEventNumber):		
		# Adds each file in the list of input file names to each module we want to use		

		for FileLocator in This.InputFileLocatorList:
			
			if (This.Modules[0].GetEntries() <= DesiredEventNumber):
			
				for Module in This.Modules:
					Module.Add(FileLocator)
					
			else:
				break
				
		MaximumEventNumber = Module.GetEntries()
				
		return MaximumEventNumber
		
	def LoadModule(This, Module_Reference):	
		
		Module = ROOT.TChain(Module_Reference)
		This.Modules.append(Module)
		
		return Module
	
		
	def Analyse(This, DesiredEventNumber = 999999999):

		sys.stdout = DataWriter.DataWriter(This.OutputTextFileLocator)
		
		MaximumEventNumber = This.LoadInputFiles(DesiredEventNumber)

		This.FGD1 = Geometry.ThreeDimensionalObject(-832.2, 832.2, -777.2, 887.2, 123.45, 446.95)
		This.FGD2 = Geometry.ThreeDimensionalObject(-832.2, 832.2, -777.2, 887.2, 1481.45, 1807.95)
		
		This.FGD1Fiducial = Geometry.ThreeDimensionalObject(-874.51, 874.51, -819.51, 929.51, 136.875, 446.955)#NB: in email he said 1446.955 but i am guessing this is typo
		This.FGD2Fiducial = Geometry.ThreeDimensionalObject(-874.51, 874.51, -819.51, 929.51, 1481.5, 1810)
		
		This.StackedHistograms = {}
	
		This.TruthStatistics = Statistics.Collection("Truth Statistics")
				
		This.TruthStatistics.NewStatistic("NEvents", "Number of Events", 0)
		This.TruthStatistics.NewStatistic("NVertices", "Number of Vertices", 0)
		This.TruthStatistics.NewStatistic("NDeltaToProtonPhoton", "Number of Delta to Proton-Photon Events", 0)
		This.TruthStatistics.NewStatistic("NDeltaToProtonPhotonCC", "Number of Delta to Proton-Photon Charged-Current Events", 0)
		This.TruthStatistics.NewStatistic("NDeltaToProtonPhotonNC", "Number of Delta to Proton-Photon Neutral-Current Events", 0)
		This.TruthStatistics.NewStatistic("NDeltaToProtonPion", "Number of Delta to Proton-Pi0 Events", 0)
		This.TruthStatistics.NewStatistic("NDeltaToProtonPhotonPP", "Number of Delta to Proton-Photon Events Where Electron Positron Pair Production Occurs", 0)
		This.TruthStatistics.NewStatistic("NDeltaToProtonPhotonPC", "Number of Delta to Proton-Photon Events Where a Photon Does Not Interact", 0)
				
		This.ReconstructedStatistics = Statistics.Collection("Reconstructed Statistics")
		
		This.ReconstructedStatistics.NewStatistic("NEventsWithRPID", "Number of Events with at least one Reconstructed PID", 0)
		This.ReconstructedStatistics.NewStatistic("NEventsWithRProton", "Number of Events with at least one Reconstructed Proton Track", 0)
		This.ReconstructedStatistics.NewStatistic("NEventsWithCRProton", "Number of Events with at least one Correctly Reconstructed Proton Track", 0)
		This.ReconstructedStatistics.NewStatistic("NEventsWithIRProton", "Number of Events with Incorrectly Reconstructed Proton Tracks", 0)
		This.ReconstructedStatistics.NewStatistic("NEventsWithCRProton18TPC", "Number of Events with at least one Correctly Reconstructed Proton Track with at least 18 TPC Nodes", 0)		
		This.ReconstructedStatistics.NewStatistic("NEventsWithTECC", "Number of Events with at least one Tracker EC Cluster", 0)		
		This.ReconstructedStatistics.NewStatistic("NEventsWithTECCAndCRProton", "Number of Events with at least one Tracker EC Cluster and one Correctly Reconstructed Proton Track", 0)	
		This.ReconstructedStatistics.NewStatistic("NEventsWithTECCAndCRProtonWithin10D", "Number of Events with at least one Tracker EC Cluster and one Correctly Reconstructed Proton Track where the Photon Direction points to within 10 Degrees of the Proton Track Start", 0)	
		This.ReconstructedStatistics.NewStatistic("NEventsWithTECCAndCRProtonWithin10DWithin500ns", "Number of Events with at least one Tracker EC Cluster and one Correctly Reconstructed Proton Track where the Photon Direction points to within 10 Degrees of the Proton Track Start and where the timing is less than 500ns", 0)
		This.ReconstructedStatistics.NewStatistic("NPIDsWithCRProton", "Number of PIDs Correctly Reconstructed as a Proton Track", 0)
		This.ReconstructedStatistics.NewStatistic("NPIDsWithIRProton", "Number of PIDs Incorrectly Reconstructed as a Proton Track", 0)
		This.ReconstructedStatistics.NewStatistic("NPIDsWithRProtonRatio", "Ratio of Correctly Reconstructed Proton Track PIDs", 0)
	
		This.EfficiencyStatisticsDeltaPGamma = Statistics.Collection("Efficiency Statistics for the Delta -> p gamma channel")
		This.EfficiencyStatisticsDeltaPPi = Statistics.Collection("Efficiency Statistics for the Delta -> p pi0 channel")
	
		This.ROOTFile1 = ROOTFile.ROOTFile(This.OutputROOTFileLocator)
		This.ROOTFile1.Open()
		
		#This.HistogramCollection1.NewHistogram1D("Reconstructed_Delta1Baryon_Energy", "Energy of the Unknown Particle which created the Reconstructed Proton and Photon", "Energy (GeV)", 100, 0, 5000, "Number")
		
		This.HistogramCollection1.NewHistogram1D("ElectronPositronInvariantMass", "Invariant Mass Distribution of Electron-Positron Pairs", "Mass (MeV)", 100, -100, 100, "Number")
		
		This.ROOTFile1.NewHistogram1D("Reconstructed_Delta1Baryon_Energy", "Energy of the Unknown Particle which created the Reconstructed Proton and Photon", "Energy (GeV)", "Number", 100, 0, 5000, "DeltaBaryon/Recon/")
		This.ROOTFile1.NewHistogram1D("Reconstructed_Delta1Baryon_MomentumModulus", "Momentum Modulus of the Unknown Particle which created the Reconstructed Proton and Photon", "Momentum (GeV)", "Number", 100, 0, 3000, "DeltaBaryon/Recon/")
		This.ROOTFile1.NewHistogram1D("Reconstructed_Delta1Baryon_Mass", "Mass of the Unknown Particle which created the Reconstructed Proton and Photon", "Mass (GeV)", "Number", 100, 0, 3000, "DeltaBaryon/Recon/")
		
		This.ROOTFile1.NewHistogram1D("Reconstructed_Delta1Baryon_Energy_TimeSeparated", "Energy of the Unknown Particle which created the Reconstructed Proton and Photon (Time Separated)", "Energy (GeV)", "Number", 100, 0, 5000, "DeltaBaryon/Recon/")
		This.ROOTFile1.NewHistogram1D("Reconstructed_Delta1Baryon_MomentumModulus_TimeSeparated", "Momentum Modulus of the Unknown Particle which created the Reconstructed Proton and Photon (Time Separated)", "Momentum (GeV)", "Number", 100, 0, 3000, "DeltaBaryon/Recon/")
		This.ROOTFile1.NewHistogram1D("Reconstructed_Delta1Baryon_Mass_TimeSeparated", "Mass of the Unknown Particle which created the Reconstructed Proton and Photon (Time Separated)", "Mass (GeV)", "Number", 100, 0, 3000, "DeltaBaryon/Recon/")
		
		This.ROOTFile1.NewHistogram1D("Truth_Delta1Baryon_Energy", "Energy of the Delta 1 Baryons", "Energy (GeV)", "Number", 100, 0, 5000, "DeltaBaryon/Truth/")
		This.ROOTFile1.NewHistogram1D("Truth_Delta1Baryon_MomentumModulus", "Momentum of the Delta 1 Baryons", "Momentum (GeV)", "Number", 100, 0, 3000, "DeltaBaryon/Truth/")
		This.ROOTFile1.NewHistogram1D("Truth_Delta1Baryon_Mass", "Mass of the Delta 1 Baryons", "Mass (GeV)", "Number", 100, 0, 3000, "DeltaBaryon/Truth/")
		
		This.StackedHistograms["ReconProtonTrueEnergy"]=StackedHistogram.StackedHistogram("Recon_Proton_True_Energy", "True energy of particles reconstructed as protons", 0.7, 0.65, 0.86, 0.88, "Energy (GeV)", "Number",  "Proton/Truth/Energy")
		
		This.StackedHistograms["ReconProtonReconMomentum"]=StackedHistogram.StackedHistogram("Recon_Proton_Recon_Momentum", "Reconstructed momentum of particles reconstructed as protons", 0.7, 0.65, 0.86, 0.88, "Momentum (GeV)", "Number", "Proton/Recon/Momentum/")
			
		This.ROOTFile1.NewHistogram1D("Recon_Truth_Proton_Momentum", "Recon momentum minus truth momentum for PIDs reconstructed as protons", "Momentum (GeV)", "Number", 100, -500, 500, "PIDs/Recon/Momentum")
		This.ROOTFile1.NewHistogram1D("Truth_Proton_Momentum", "Truth momentum for PIDs reconstructed as protons", "Momentum (GeV)", "Number", 100, 0, 5000, "PIDs/Truth/Momentum")
				
		This.ROOTFile1.NewHistogram1D("PhotonAngles", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position", "Angle", "Number", 100, 0, 180, "Photon/Recon/All/")
		This.ROOTFile1.NewHistogram1D("ProtonPhotonTimeSeparations", "Time Separation between the Reconstructed Proton Track and Photon EC Cluster", "Time Separation", "Number", 100, 0, 4000, "Photon/Recon/")
		This.StackedHistograms["PhotonAnglesStacked"]=StackedHistogram.StackedHistogram("Photon_Angles_Stacked", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position", 0.7, 0.65, 0.86, 0.88, "Angle", "Number",  "Photon/Recon/All/")
		
		This.ROOTFile1.NewHistogram1D("SelectedPhotonAngles", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position for the single proton and the single selected photon", "Angle", "Number", 100, 0, 180, "Photon/Recon/Selected/")
		This.StackedHistograms["SelectedPhotonAnglesStacked"]=StackedHistogram.StackedHistogram("Selected_Photon_Angles_Stacked", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position for the single proton and the single selected photon", 0.7, 0.65, 0.86, 0.88, "Angle", "Number",  "Photon/Recon/Selected/")
		
		This.StackedHistograms["PhotonAnglesStackedTrack"]=StackedHistogram.StackedHistogram("Photon_Angles_Stacked_Track", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position for the single proton and the single selected photon", 0.7, 0.65, 0.86, 0.88, "Angle", "Number",  "Photon/Recon/Track/")
		This.StackedHistograms["PhotonAnglesStackedShower"]=StackedHistogram.StackedHistogram("Photon_Angles_Stacked_Shower", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position for the single proton and the single selected photon", 0.7, 0.65, 0.86, 0.88, "Angle", "Number",  "Photon/Recon/Shower/")
		This.StackedHistograms["SelectedPhotonAnglesStackedTrack"]=StackedHistogram.StackedHistogram("Selected_Photon_Angles_Stacked_Track", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position for the single proton and the single selected photon", 0.7, 0.65, 0.86, 0.88, "Angle", "Number",  "Photon/Recon/Selected/Track/")
		This.StackedHistograms["SelectedPhotonAnglesStackedShower"]=StackedHistogram.StackedHistogram("Selected_Photon_Angles_Stacked_Track", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position for the single proton and the single selected photon", 0.7, 0.65, 0.86, 0.88, "Angle", "Number",  "Photon/Recon/Selected/Shower/")

		This.ROOTFile1.NewHistogram1D("PID_Electron_Pull", "Electron pull for every PID", "Electron Pull", "Number", 100, -100, 100, "PIDs/Recon/Particle Pulls/")
		This.ROOTFile1.NewHistogram1D("PID_Kaon_Pull", "Kaon pull for every PID", "Kaon Pull", "Number", 100, -100, 100, "PIDs/Recon/Particle Pulls/")
		This.ROOTFile1.NewHistogram1D("PID_Muon_Pull", "Muon pull for every PID", "Muon Pull", "Number", 100, -100, 100, "PIDs/Recon/Particle Pulls/")
		This.ROOTFile1.NewHistogram1D("PID_Pion_Pull", "Pion pull for every PID", "Pion Pull", "Number", 100, -100, 100, "PIDs/Recon/Particle Pulls/")
		This.ROOTFile1.NewHistogram1D("PID_Proton_Pull", "Proton pull for every PID", "Proton Pull", "Number", 100, -100, 100, "PIDs/Recon/Particle Pulls/")
		
		This.ROOTFile1.NewHistogram2D("PID_Proton_Against_Muon_Pull", "Proton pull plotted against muon pull for every PID", "Proton Pull", "Muon Pull", 100, -100, 100, 100, -100, 100, "PIDs/Recon/Particle Pulls/")
		
		This.ROOTFile1.NewHistogram1D("Proton_PID_Electron_Pull", "Electron pull for all PIDs identified as proton-like", "Electron Pull", "Number", 100, -100, 100, "Proton/Recon/Particle Pulls/All Protons/")
		This.ROOTFile1.NewHistogram1D("Proton_PID_Kaon_Pull", "Kaon pull for all PIDs identified as proton-like", "Kaon Pull", "Number", 100, -100, 100, "Proton/Recon/Particle Pulls/All Protons/")
		This.ROOTFile1.NewHistogram1D("Proton_PID_Muon_Pull", "Muon pull for all PIDs identified as proton-like", "Muon Pull", "Number", 100, -100, 100, "Proton/Recon/Particle Pulls/All Protons/")
		This.ROOTFile1.NewHistogram1D("Proton_PID_Pion_Pull", "Pion pull for all PIDs identified as proton-like", "Pion Pull", "Number", 100, -100, 100, "Proton/Recon/Particle Pulls/All Protons/")
		This.ROOTFile1.NewHistogram1D("Proton_PID_Proton_Pull", "Proton pull for all PIDs identified as proton-like", "Proton Pull", "Number", 100, -100, 100, "Proton/Recon/Particle Pulls/All Protons/")
		
		This.ROOTFile1.NewHistogram2D("Proton_PID_Proton_Against_Muon_Pull", "Proton pull plotted against muon pull for all PIDs identified as proton-like", "Proton Pull", "Muon Pull", 100, -100, 100, 100, -100, 100, "Proton/Recon/Particle Pulls/All Protons/")
		This.ROOTFile1.HistogramDictionary["Proton_PID_Proton_Against_Muon_Pull"].Histogram.SetMarkerStyle(3)
		
		This.ROOTFile1.NewHistogram1D("Single_Proton_PID_Electron_Pull", "Electron pull for single PIDs identified as proton-like", "Electron Pull", "Number", 100, -100, 100, "Proton/Recon/Particle Pulls/Single Proton/")
		This.ROOTFile1.NewHistogram1D("Single_Proton_PID_Kaon_Pull", "Kaon pull for single PIDs identified as proton-like", "Kaon Pull", "Number", 100, -100, 100, "Proton/Recon/Particle Pulls/Single Proton/")
		This.ROOTFile1.NewHistogram1D("Single_Proton_PID_Muon_Pull", "Muon pull for single PIDs identified as proton-like", "Muon Pull", "Number", 100, -100, 100, "Proton/Recon/Particle Pulls/Single Proton/")
		This.ROOTFile1.NewHistogram1D("Single_Proton_PID_Pion_Pull", "Pion pull for single PIDs identified as proton-like", "Pion Pull", "Number", 100, -100, 100, "Proton/Recon/Particle Pulls/Single Proton/")
		This.ROOTFile1.NewHistogram1D("Single_Proton_PID_Proton_Pull", "Proton pull for single PIDs identified as proton-like", "Proton Pull", "Number", 100, -100, 100, "Proton/Recon/Particle Pulls/Single Proton/")
		
		This.ROOTFile1.NewHistogram2D("Single_Proton_PID_Proton_Against_Muon_Pull", "Proton pull plotted against muon pull for single PIDs identified as proton-like", "Proton Pull", "Muon Pull", 100, -100, 100, 100, -100, 100, "Proton/Recon/Particle Pulls/Single Proton/")
		This.ROOTFile1.HistogramDictionary["Single_Proton_PID_Proton_Against_Muon_Pull"].Histogram.SetMarkerStyle(3)
		
		This.StackedHistograms["FinalInvariantMass"]=StackedHistogram.StackedHistogram("Final_Invariant_Mass", "Invariant Mass of Delta Baryon after all cuts have been applied", 0.7, 0.65, 0.86, 0.88, "Mass (GeV)", "Number", "Cuts/DeltaPGamma/Invariant Mass/")
		This.StackedHistograms["InvariantMassAllECal"]=StackedHistogram.StackedHistogram("Invariant_Mass_All_ECal", "Invariant Mass of Delta Baryon from comparison of single photon to all ECals", 0.7, 0.65, 0.86, 0.88, "Mass (GeV)", "Number", "Cuts/DeltaPGamma/Invariant Mass/All ECal/")
		
		This.StackedHistograms["Pi0MesonMass"] = StackedHistogram.StackedHistogram("Pi0_Meson_Mass", "Invariant Mass of Pi0 Meson from matching of ECal clusters", 0.7, 0.65, 0.86, 0.88, "Mass (GeV)", "Number", "Pi0Meson/Invariant Mass/")
			
		EventNumber = min(MaximumEventNumber, DesiredEventNumber)

		print TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine, TextConstants.LineSeparator
		if (MaximumEventNumber < DesiredEventNumber):
			print "Warning: the number of events within the file list is less than the number of events requested."
		print "Reading", EventNumber, "Events"
		print TextConstants.LineSeparator
		
		ProgressMeter1 = ProgressMeter.ProgressMeter(EventNumber - 1)
		
		SuitableEvents = 0
		
		for i in range(EventNumber):
			for module in This.Modules:
				module.GetEntry(i)
			
			if (This.InputTimeTest == False):
			
				SuitableEvent = False
			
				for PID in This.Reconstructed_Global.PIDs:

					X1 = PID.FrontPosition.X()
					Y1 = PID.FrontPosition.Y()
					Z1 = PID.FrontPosition.Z()

					if ((This.FGD1Fiducial.Contains(X1, Y1, Z1) == True) or (This.FGD2Fiducial.Contains(X1, Y1, Z1) == True)):
						SuitableEvent = True
	
				ProgressMeter1.Update(i)
				
				if (SuitableEvent):
					
					SuitableEvents += 1
					
					This.runEvent()
		
		if ((This.InputTimeTest == False) and (SuitableEvents > 0)):
			
			################################ Cuts
			
			for Key, SelectionChannel in This.SelectionDictionary.iteritems():
				
				SelectionChannel[0].EventsRemaining = This.TruthStatistics.Statistics["NEvents"].Quantity
		
				CutNumber = len(SelectionChannel)
				
				PreviousEventsRemaining = SelectionChannel[0].EventsRemaining

				for SelectionStatistics1 in SelectionChannel:
					
					
					if (float(PreviousEventsRemaining) != 0):
						SelectionStatistics1.RelativeEfficiency = float(SelectionStatistics1.EventsRemaining) / float(PreviousEventsRemaining)
					else:
						SelectionStatistics1.RelativeEfficiency = 0
					
					
					if (float(SelectionChannel[0].EventsRemaining) != 0):
						SelectionStatistics1.AbsoluteEfficiency = float(SelectionStatistics1.EventsRemaining) / float(SelectionChannel[0].EventsRemaining)
					else:
						SelectionStatistics1.AbsoluteEfficiency = 0
					
					
					EventsRemaining = SelectionStatistics1.EventsRemaining
						
					if (float(EventsRemaining) != 0):
						SelectionStatistics1.Purity = float(SelectionStatistics1.TruthDelta) / float(EventsRemaining)
						SelectionStatistics1.PionPurity = float(SelectionStatistics1.ReconstructedDelta) / float(EventsRemaining)
						SelectionStatistics1.RPPurity = float(SelectionStatistics1.OtherRPInteraction) / float(EventsRemaining)
						SelectionStatistics1.QSPurity = float(SelectionStatistics1.QSInteraction) / float(EventsRemaining)
						SelectionStatistics1.ESPurity = float(SelectionStatistics1.ESInteraction) / float(EventsRemaining)
						SelectionStatistics1.DISPurity = float(SelectionStatistics1.DISInteraction) / float(EventsRemaining)
						SelectionStatistics1.CSPurity = float(SelectionStatistics1.CSInteraction) / float(EventsRemaining)
						SelectionStatistics1.OtherPurity = float(SelectionStatistics1.OtherInteraction) / float(EventsRemaining)
					else:
						SelectionStatistics1.Purity = 0
						SelectionStatistics1.PionPurity = 0
						SelectionStatistics1.RPPurity = 0
						SelectionStatistics1.QSPurity = 0
						SelectionStatistics1.ESPurity = 0
						SelectionStatistics1.DISPurity = 0
						SelectionStatistics1.CSPurity = 0
						SelectionStatistics1.OtherPurity = 0
						
							
					PreviousEventsRemaining = SelectionStatistics1.EventsRemaining
				
				#if	(Key == "DeltaPGamma"):#This is a bit messy, could improve
				SelectionChannel[0].TruthDelta = This.TruthStatistics.Statistics["NDeltaToProtonPhoton"].Quantity
				#elif (Key == "DeltaPPi"):
				#	SelectionChannel[0].TruthDelta = This.TruthStatistics.Statistics["NDeltaToProtonPion"].Quantity
				
				try:
					SelectionChannel[0].Purity = float(SelectionChannel[0].TruthDelta)/float(SelectionChannel[0].EventsRemaining)
				except:
					SelectionChannel[0].Purity = 1
					
				SelectionChannel[0].RelativeEfficiency = 1
				SelectionChannel[0].AbsoluteEfficiency = 1
	
			############################# Graphs of cuts

			for Key, SelectionChannel in This.SelectionDictionary.iteritems():

				Location = "Cuts/" + Key + "/"
				CutNumber = len(SelectionChannel)

				AbsoluteEfficiencyReference = "AbsoluteEfficiency" + Key

				This.ROOTFile1.NewHistogram1D(AbsoluteEfficiencyReference, "Absolute Efficiency for the Selections", "Selections", "Absolute Efficiency", CutNumber, 0, CutNumber, Location)

				This.ROOTFile1.HistogramDictionary[AbsoluteEfficiencyReference].Histogram.SetMarkerStyle(3)
				This.ROOTFile1.HistogramDictionary[AbsoluteEfficiencyReference].Histogram.SetOption("LP")
				This.ROOTFile1.HistogramDictionary[AbsoluteEfficiencyReference].Histogram.SetStats(0)

				for CriteriaListCounter in xrange(CutNumber):
					
					This.ROOTFile1.HistogramDictionary[AbsoluteEfficiencyReference].Histogram.Fill(CriteriaListCounter,SelectionChannel[CriteriaListCounter].AbsoluteEfficiency)
					
				for CutCounter in xrange(len(SelectionChannel)):
					
					if(CutCounter == 0):
						BinLabel = "Starting Events"
					else:
						BinLabel = "Criterion " + str(CutCounter)
					
					This.ROOTFile1.HistogramDictionary[AbsoluteEfficiencyReference].Histogram.GetXaxis().SetBinLabel(CutCounter+1, BinLabel)

				RelativeEfficiencyReference = "RelativeEfficiency" + Key

				This.ROOTFile1.NewHistogram1D(RelativeEfficiencyReference, "Relative Efficiency for the Selections", "Selections", "Relative Efficiency", CutNumber, 0, CutNumber, Location)

				This.ROOTFile1.HistogramDictionary[RelativeEfficiencyReference].Histogram.SetMarkerStyle(3)
				This.ROOTFile1.HistogramDictionary[RelativeEfficiencyReference].Histogram.SetOption("LP")
				This.ROOTFile1.HistogramDictionary[RelativeEfficiencyReference].Histogram.SetStats(0)

				for CriteriaListCounter in xrange(CutNumber):
					
					This.ROOTFile1.HistogramDictionary[RelativeEfficiencyReference].Histogram.Fill(CriteriaListCounter, SelectionChannel[CriteriaListCounter].RelativeEfficiency)
					
				for CutCounter in xrange(len(SelectionChannel)):
					
					if(CutCounter == 0):
						BinLabel = "Starting Events"
					else:
						BinLabel = "Criterion " + str(CutCounter)
					
					This.ROOTFile1.HistogramDictionary[RelativeEfficiencyReference].Histogram.GetXaxis().SetBinLabel(CutCounter+1, BinLabel)
				
				PurityReference = "Purity" + Key
				
				This.ROOTFile1.NewHistogram1D(PurityReference, "Purity for the Selections", "Selections", "Purity", CutNumber, 0, CutNumber, Location)

				This.ROOTFile1.HistogramDictionary[PurityReference].Histogram.SetMarkerStyle(3)
				This.ROOTFile1.HistogramDictionary[PurityReference].Histogram.SetOption("LP")
				This.ROOTFile1.HistogramDictionary[PurityReference].Histogram.SetStats(0)

				for CriteriaListCounter in xrange(CutNumber):
					#print CriteriaListCounter, SelectionChannel[CriteriaListCounter].PionPurity, SelectionChannel[CriteriaListCounter].Purity, Key
					if	(Key == "DeltaPGamma"):
						This.ROOTFile1.HistogramDictionary[PurityReference].Histogram.Fill(CriteriaListCounter,SelectionChannel[CriteriaListCounter].Purity)
					elif (Key == "DeltaPPi"):
						This.ROOTFile1.HistogramDictionary[PurityReference].Histogram.Fill(CriteriaListCounter,SelectionChannel[CriteriaListCounter].PionPurity)
										
				for CutCounter in xrange(len(SelectionChannel)):
					
					if(CutCounter == 0):
						BinLabel = "Starting Events"
					else:
						BinLabel = "Criterion " + str(CutCounter)
					
					This.ROOTFile1.HistogramDictionary[PurityReference].Histogram.GetXaxis().SetBinLabel(CutCounter+1, BinLabel)
								
				NormalisedPurityReference = "NormalisedPurity" + Key
				
				This.StackedHistograms[NormalisedPurityReference]=StackedHistogram.StackedHistogram(NormalisedPurityReference, "Constituent processes after each cut (Normalised)", 0.7, 0.65, 0.86, 0.88, "Cuts", "Events Remaining", Location + "Normalised/")

				NormalisedPurityTitle = "Purity as a function of selection for"

				for CriteriaListCounter in xrange(CutNumber):
									
					if(SelectionChannel[CriteriaListCounter].Purity > 0):
						
						This.StackedHistograms[NormalisedPurityReference].AttemptToFill2D(NormalisedPurityTitle, "Delta -> p gamma interactions", "NormalisedPurity:DeltaPGamma" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Normalised/Constituent Histograms/", CriteriaListCounter, SelectionChannel[CriteriaListCounter].Purity, "Delta -> p gamma Interactions")
					
					if(SelectionChannel[CriteriaListCounter].PionPurity > 0):
						
						This.StackedHistograms[NormalisedPurityReference].AttemptToFill2D(NormalisedPurityTitle, "Delta -> p pi interactions", "NormalisedPurity:DeltaPPi" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Normalised/Constituent Histograms/", CriteriaListCounter, SelectionChannel[CriteriaListCounter].PionPurity, "Delta -> p pi Interactions")
				
					if(SelectionChannel[CriteriaListCounter].RPPurity > 0):
						
						This.StackedHistograms[NormalisedPurityReference].AttemptToFill2D(NormalisedPurityTitle, "Other Resonance Production", "NormalisedPurity:OtherResonance" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Normalised/Constituent Histograms/", CriteriaListCounter, SelectionChannel[CriteriaListCounter].RPPurity, "Other Resonance Production")
						
					if(SelectionChannel[CriteriaListCounter].QSPurity > 0):
						
						This.StackedHistograms[NormalisedPurityReference].AttemptToFill2D(NormalisedPurityTitle, "Quasi-Elastic Scattering", "NormalisedPurity:QES" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Normalised/Constituent Histograms/", CriteriaListCounter, SelectionChannel[CriteriaListCounter].QSPurity, "Quasi-Elastic Scattering")
					
					if(SelectionChannel[CriteriaListCounter].ESPurity > 0):
											
						This.StackedHistograms[NormalisedPurityReference].AttemptToFill2D(NormalisedPurityTitle, "Elastic Scattering", "NormalisedPurity:ES" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Normalised/Constituent Histograms/", CriteriaListCounter, SelectionChannel[CriteriaListCounter].ESPurity, "Elastic Scattering")
				
					if(SelectionChannel[CriteriaListCounter].DISPurity > 0):
						
						This.StackedHistograms[NormalisedPurityReference].AttemptToFill2D(NormalisedPurityTitle, "Deep Inelastic Scattering", "NormalisedPurity:DIS" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Normalised/Constituent Histograms/", CriteriaListCounter, SelectionChannel[CriteriaListCounter].DISPurity, "Deep Inelastic Scattering")
						
					if(SelectionChannel[CriteriaListCounter].CSPurity > 0):
						
						This.StackedHistograms[NormalisedPurityReference].AttemptToFill2D(NormalisedPurityTitle, "Coherent Scattering", "NormalisedPurity:C" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Normalised/Constituent Histograms/", CriteriaListCounter, SelectionChannel[CriteriaListCounter].CSPurity, "Coherent Scattering")
											
					if(SelectionChannel[CriteriaListCounter].OtherPurity > 0):
						
						This.StackedHistograms[NormalisedPurityReference].AttemptToFill2D(NormalisedPurityTitle, "Other Interactions", "NormalisedPurity:Other" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Normalised/Constituent Histograms/", CriteriaListCounter, SelectionChannel[CriteriaListCounter].OtherPurity, "Other Interactions")
				
				for Histogram1 in This.StackedHistograms[NormalisedPurityReference].HistogramDictionary.itervalues():
					for CutCounter in xrange(len(SelectionChannel)):
						
						if(CutCounter == 0):
							BinLabel = "Starting Events"
						else:
							BinLabel = "Criterion " + str(CutCounter)
						
						Histogram1.Histogram.GetXaxis().SetBinLabel(CutCounter+1, BinLabel)
	
	
			############## Application of truth to criteria
				
				CutPurityReference = "CutPurity" + Key
				
				This.StackedHistograms[CutPurityReference]=StackedHistogram.StackedHistogram(CutPurityReference, "Constituent Processes for the Events after every Selection",0.7,0.65,0.86,0.88, "Cuts", "Events Remaining", Location + "/Energy/")

				for CutCounter in xrange(len(SelectionChannel)):
					for FillCounter in xrange(SelectionChannel[CutCounter].TruthDelta):
						This.StackedHistograms[CutPurityReference].AttemptToFill1D(NormalisedPurityTitle, "Delta -> p gamma interactions", "Purity:DeltaPGamma" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Energy/Constituent Histograms/", CutCounter, "Delta -> p gamma Interactions")
					for FillCounter in xrange(SelectionChannel[CutCounter].ReconstructedDelta):
						This.StackedHistograms[CutPurityReference].AttemptToFill1D(NormalisedPurityTitle, "Delta -> p pi interactions", "Purity:DeltaPPi" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Energy/Constituent Histograms/", CutCounter, "Delta -> p pi Interactions")
					for FillCounter in xrange(SelectionChannel[CutCounter].OtherRPInteraction):
						This.StackedHistograms[CutPurityReference].AttemptToFill1D(NormalisedPurityTitle, "Other Resonance Production", "Purity:OtherResonance" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Energy/Constituent Histograms/", CutCounter, "Other Resonance Production")
					for FillCounter in xrange(SelectionChannel[CutCounter].QSInteraction):
						This.StackedHistograms[CutPurityReference].AttemptToFill1D(NormalisedPurityTitle, "Quasi-Elastic Scattering", "Purity:QES" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Energy/Constituent Histograms/", CutCounter, "Quasi-Elastic Scattering")
					for FillCounter in xrange(SelectionChannel[CutCounter].ESInteraction):
						This.StackedHistograms[CutPurityReference].AttemptToFill1D(NormalisedPurityTitle, "Elastic Scattering", "Purity:ES" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Energy/Constituent Histograms/", CutCounter, "Elastic Scattering")
					for FillCounter in xrange(SelectionChannel[CutCounter].DISInteraction):
						This.StackedHistograms[CutPurityReference].AttemptToFill1D(NormalisedPurityTitle, "Deep Inelastic Scattering", "Purity:DIS" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Energy/Constituent Histograms/", CutCounter, "Deep Inelastic Scattering")
					for FillCounter in xrange(SelectionChannel[CutCounter].CSInteraction):
						This.StackedHistograms[CutPurityReference].AttemptToFill1D(NormalisedPurityTitle, "Coherent Scattering", "Purity:C" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Energy/Constituent Histograms/", CutCounter, "Coherent Scattering")
					for FillCounter in xrange(SelectionChannel[CutCounter].OtherInteraction):
						This.StackedHistograms[CutPurityReference].AttemptToFill1D(NormalisedPurityTitle, "Other Interactions", "Purity:Other" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Energy/Constituent Histograms/", CutCounter, "Other Interactions")
						
				for Histogram1 in This.StackedHistograms[CutPurityReference].HistogramDictionary.itervalues():
					for CutCounter in xrange(len(SelectionChannel)):
					
						if(CutCounter == 0):
							BinLabel = "Starting Events"
						else:
							BinLabel = "Criterion " + str(CutCounter)
					
						Histogram1.Histogram.GetXaxis().SetBinLabel(CutCounter+1, BinLabel)

			###############			
									
			This.EfficiencyStatisticsDeltaPGamma.NewStatistic("NEvents0", "Initial Number of Events", This.SelectionDictionary["DeltaPGamma"][0].EventsRemaining)
			This.EfficiencyStatisticsDeltaPGamma.NewStatistic("NEvents1", "Selection 1 - At least one reconstructed track was recorded - Events Remaining", This.SelectionDictionary["DeltaPGamma"][1].EventsRemaining)
			This.EfficiencyStatisticsDeltaPGamma.NewStatistic("NEvents2", "Selection 2 - The track has at least 18 TPC nodes - Events Remaining", This.SelectionDictionary["DeltaPGamma"][2].EventsRemaining)
			This.EfficiencyStatisticsDeltaPGamma.NewStatistic("NEvents3", "Selection 3 - At least one proton-identified track - Events Remaining", This.SelectionDictionary["DeltaPGamma"][3].EventsRemaining)
			This.EfficiencyStatisticsDeltaPGamma.NewStatistic("NEvents4", "Selection 4 - Only one proton-identified track - Events Remaining", This.SelectionDictionary["DeltaPGamma"][4].EventsRemaining)
			This.EfficiencyStatisticsDeltaPGamma.NewStatistic("NEvents5", "Selection 5 - Proton track is the first track into the detector - Events Remaining", This.SelectionDictionary["DeltaPGamma"][5].EventsRemaining)
			This.EfficiencyStatisticsDeltaPGamma.NewStatistic("NEvents6", "Selection 6 - Proton track began in the FGDs - Events Remaining", This.SelectionDictionary["DeltaPGamma"][6].EventsRemaining)
			
			Selection7DeltaPGamma = "Selection 7 - Fewer than " + str(NumericalCuts.DeltaPGammaMultiplicity) + " PIDs in total - Events Remaining"
			This.EfficiencyStatisticsDeltaPGamma.NewStatistic("NEvents7", Selection7DeltaPGamma, This.SelectionDictionary["DeltaPGamma"][7].EventsRemaining)
			This.EfficiencyStatisticsDeltaPGamma.NewStatistic("NEvents8", "Selection 8 - At least one EC cluster was recorded - Events Remaining", This.SelectionDictionary["DeltaPGamma"][8].EventsRemaining)
			
			Selection9DeltaPGamma = "Selection 9 - The smallest angle was less than " + str(NumericalCuts.MinimumAngle) + " degees - Events Remaining"
			This.EfficiencyStatisticsDeltaPGamma.NewStatistic("NEvents9", Selection9DeltaPGamma, This.SelectionDictionary["DeltaPGamma"][9].EventsRemaining)
			
			Selection10DeltaPGamma = "Selection 10 - The calculated invariant mass was within " + str(NumericalCuts.InvariantMassVariance) + " MeV of the true Delta1 Baryon mass, " + str(PhysicalConstants.Delta1BaryonMass) + " MeV - Events Remaining"
			This.EfficiencyStatisticsDeltaPGamma.NewStatistic("NEvents10", Selection10DeltaPGamma, This.SelectionDictionary["DeltaPGamma"][10].EventsRemaining)
			
			#####			
					
			This.EfficiencyStatisticsDeltaPPi.NewStatistic("NEvents0", "Initial Number of Events", This.SelectionDictionary["DeltaPPi"][0].EventsRemaining)
			This.EfficiencyStatisticsDeltaPPi.NewStatistic("NEvents1", "Selection 1 - At least one reconstructed track was recorded - Events Remaining", This.SelectionDictionary["DeltaPPi"][1].EventsRemaining)
			This.EfficiencyStatisticsDeltaPPi.NewStatistic("NEvents2", "Selection 2 - The track has at least 18 TPC nodes - Events Remaining", This.SelectionDictionary["DeltaPPi"][2].EventsRemaining)
			This.EfficiencyStatisticsDeltaPPi.NewStatistic("NEvents3", "Selection 3 - At least one proton-identified track - Events Remaining", This.SelectionDictionary["DeltaPPi"][3].EventsRemaining)
			This.EfficiencyStatisticsDeltaPPi.NewStatistic("NEvents4", "Selection 4 - Only one proton-identified track - Events Remaining", This.SelectionDictionary["DeltaPPi"][4].EventsRemaining)
			This.EfficiencyStatisticsDeltaPPi.NewStatistic("NEvents5", "Selection 5 - Proton track is the first track into the detector - Events Remaining", This.SelectionDictionary["DeltaPPi"][5].EventsRemaining)
			This.EfficiencyStatisticsDeltaPPi.NewStatistic("NEvents6", "Selection 6 - Proton track began in the FGDs - Events Remaining", This.SelectionDictionary["DeltaPPi"][6].EventsRemaining)
			
			Selection7DeltaPPi = "Selection 7 - Fewer than " + str(NumericalCuts.DeltaPGammaMultiplicity) + " PIDs in total - Events Remaining"
			This.EfficiencyStatisticsDeltaPPi.NewStatistic("NEvents7", Selection7DeltaPGamma, This.SelectionDictionary["DeltaPPi"][7].EventsRemaining)
			
			
			#####
			
			This.ReconstructedStatistics.Statistics["NPIDsWithRProtonRatio"].Quantity= float(This.ReconstructedStatistics.Statistics["NPIDsWithCRProton"].Quantity)/float(This.ReconstructedStatistics.Statistics["NPIDsWithCRProton"].Quantity+This.ReconstructedStatistics.Statistics["NPIDsWithIRProton"].Quantity)
			
	
		print This.TruthStatistics.ToText()
		print This.ReconstructedStatistics.ToText()
		print This.EfficiencyStatisticsDeltaPGamma.ToText()
		print This.EfficiencyStatisticsDeltaPPi.ToText()
	
		print TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine
		
		if (len(This.BackgroundEventNumbers) > 0):
		
			print "Background Event Indices: "
	
			for n in This.BackgroundEventNumbers:
				print str(n)
	
			print TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine
		
		if (len(This.BackgroundPiMesonEventNumbers) > 0):
		
			print "Background Pi Meson Event Indices: "
	
			for n in This.BackgroundPiMesonEventNumbers:
				print str(n)
	
			print TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine
				
		for StackedHistogramName1, StackedHistogram1 in This.StackedHistograms.iteritems():
			
			StackedHistogram1.AutoPrepare("f")
		
			CanvasTitle = "Canvas of " + StackedHistogramName1
		
			try:
				This.ROOTFile1.NewStackedHistogramCanvas(StackedHistogramName1, *StackedHistogram1.StackedHistogramCanvas(StackedHistogramName1, CanvasTitle, 700, 500))
			except:
				pass
		
			StackedHistogram1.DrawConstituentHistograms(This.ROOTFile1)
		
		del sys.stdout#Closes .txt file and returns to printing only to console

		This.ROOTFile1.Close()
		
	
	def runEvent(This):

		This.TruthStatistics.Statistics["NEvents"].Quantity += 1
	
		###### First loop over the true genie data to look for information about the delta interactions
	
		DeltaPGammaEvent = False
		Delta1BaryonToProtonPi0MesonEvent = False
	
		NVertices = This.Truth_GRTVertices.NVtx

		InteractionType = ""
		
		
		
		########################################
		# TRUTH DATA #
		########################################
		
		Delta1Hardons = []
		TruePhotons = []
		
		
		"""
		SelectionReferences = ["A", "B", "C", "D", "E"]
		
		Event1 = Simulation.Event()
		
		Event1 = This.EventCollection1.InterpretEvent(This.Truth_GRTVertices.Vtx, This.Reconstructed_Global.PIDs, This.Truth_Trajectories.Trajectories, This.Reconstructed_TEC.ReconObject, SelectionReferences) 
		
		This.TruthStatistics.Statistics["NVertices"].Quantity += Event1.TrueEvent.NumberOfTrueVertices
		
		
		This.TruthStatistics.Statistics["NDeltaToProtonPhoton"].Quantity += Event1.TrueEvent.NumberOfDelta1HadronToProtonPhotonInteractions
		This.TruthStatistics.Statistics["NDeltaToProtonPhotonCC"].Quantity += Event1.TrueEvent.NumberOfDelta1HadronToProtonPhotonCCInteractions
		This.TruthStatistics.Statistics["NDeltaToProtonPhotonNC"].Quantity += Event1.TrueEvent.NumberOfDelta1HadronToProtonPhotonNCInteractions
		
		"""
		for GRTVertex1 in This.Truth_GRTVertices.Vtx: #Loop over vertices in event
						
			This.TruthStatistics.Statistics["NVertices"].Quantity += 1
						
			IncidentMuonNeutrino = False#For a later check of whether incident particle is a neutrino
			ProtonFromDelta = False#For logical check on Delta interaction of interest
			PhotonFromDelta = False
			Pi0MesonFromDelta = False
			ElectronFromPhoton = False
			AntiElectronFromPhoton = False
			PhotonConserved = False
			
			for GRTParticle1 in This.RTTools.getParticles(GRTVertex1):
				
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
						
						for DaughterParticle in This.RTTools.getParticles(GRTVertex1):#Loop again over particles in vertex
						
							if (DaughterParticle.i >= DeltaDaughterFirst and DaughterParticle.i <= DeltaDaughterLast):#Only looks for when counter is in range of Delta daughter particles
							
								if (DaughterParticle.pdg == ParticleCodes.Proton):
									ProtonFromDelta = True
									
								if (DaughterParticle.pdg == ParticleCodes.Photon):
									PhotonFromDelta = True
									
									PhotonDaughterFirst = DaughterParticle.first_daughter#To find whether the photon decays to electron positron
									PhotonDaughterLast = DaughterParticle.last_daughter
									
								if (DaughterParticle.pdg == ParticleCodes.Pi0Meson):
									Pi0MesonFromDelta = True

					Delta1Hardons.append(GRTParticle1)
				
				if ((GRTParticle1.pdg == ParticleCodes.Photon)):#Looks for photon before final state
				
					PhotonDaughterFirst = GRTParticle1.first_daughter
					PhotonDaughterLast = GRTParticle1.last_daughter
					
					for PhotonDaughter in This.RTTools.getParticles(GRTVertex1):
			
						if (PhotonDaughterLast == PhotonDaughterFirst):
							
							if (((PhotonDaughter.i == PhotonDaughterFirst) and (PhotonDaughter.pdg == ParticleCodes.Photon) and (PhotonDaughter.pdg == 1)) or (PhotonDaughterFirst == -1)):
								PhotonConserved = True

			
						elif (PhotonDaughterLast - PhotonDaughterFirst == 1):
							
							if (PhotonDaughter.i >= PhotonDaughterFirst and PhotonDaughter.i <= PhotonDaughterLast):
								
								if (PhotonDaughter == ParticleCodes.Electron):
									ElectronFromPhoton = True
								elif (PhotonDaughter == ParticleCodes.AntiElectron):
									AntiElectronFromPhoton = True
				
					if (GRTParticle1.status == 1):
					
						TruePhotons.append(GRTParticle1)
																
			######################################## Search for current and interaction type. This method can look at electron neutrinos and anti muon neutrinos for any possible extension

			This.EventCodeDeconstructor1.ReadCode(GRTVertex1.EvtCode)
			
			Current = This.EventCodeDeconstructor1.Elements["Current Code"].Content
			InteractionType = This.EventCodeDeconstructor1.Elements["Process Code"].Content					
							
			###################################### Categorisation of various interesting interactions ############
							
			DeltaPGammaInteraction = (IncidentMuonNeutrino and ProtonFromDelta and PhotonFromDelta and InteractionType == "RP")
			
			Delta1BaryonToProtonPi0MesonInteraction = (IncidentMuonNeutrino and ProtonFromDelta and Pi0MesonFromDelta and InteractionType == "RP")
			
			DeltaPGammaInteractionPairProduced = (DeltaPGammaInteraction and ElectronFromPhoton and AntiElectronFromPhoton)
			
			DeltaPGammaInteractionPhotonConserved = (DeltaPGammaInteraction and PhotonConserved)
			
			if (DeltaPGammaInteraction):
				This.TruthStatistics.Statistics["NDeltaToProtonPhoton"].Quantity += 1
				DeltaPGammaEvent=True
			
			if (Delta1BaryonToProtonPi0MesonInteraction):
				This.TruthStatistics.Statistics["NDeltaToProtonPion"].Quantity += 1
			
			if (DeltaPGammaInteraction and Current == "CC"):
				This.TruthStatistics.Statistics["NDeltaToProtonPhotonCC"].Quantity += 1
				
			if (DeltaPGammaInteraction and Current == "NC"):
				This.TruthStatistics.Statistics["NDeltaToProtonPhotonNC"].Quantity += 1
				
			if (DeltaPGammaInteractionPairProduced):
				This.TruthStatistics.Statistics["NDeltaToProtonPhotonPP"].Quantity += 1
				
			if (DeltaPGammaInteractionPhotonConserved):
				This.TruthStatistics.Statistics["NDeltaToProtonPhotonPC"].Quantity += 1

			if (Delta1BaryonToProtonPi0MesonInteraction):
				Delta1BaryonToProtonPi0MesonEvent = True

		EventProcess = ProcessSeparator.EventProcess(DeltaPGammaEvent, Delta1BaryonToProtonPi0MesonEvent, InteractionType)
		
		
		"""for Photon in TruePhotons:
			
			PhotonDaughterFirst = Photon.first_daughter
			PhotonDaughterLast = Photon.last_daughter
			
			for PhotonDaughter in 
			
			if (Photon.i >= PhotonDaughterFirst and Photon.i <= PhotonDaughterLast):
			
				print Photon.pdg"""


		########################################
		# RECONSTRUCTED DATA #
		########################################

		NPIDs = This.Reconstructed_Global.NPIDs#Number of reconstructed PIDs

		if (NPIDs > 0):
			
			This.ReconstructedStatistics.Statistics["NEventsWithRPID"].Quantity += 1

		ProtonIsCorrectlyReconstructed = False
	
		ProtonList = []
			
		PIDParticleList = []
		PIDObjectList = []
		
		PIDNumber = 0
		TPCValidPIDNumber = 0
		
		for PID in This.Reconstructed_Global.PIDs: # Loop over the PIDs if they exist
			
			PIDNumber += 1
								
			SuitableTPCNodeNumber = False
										
			for TPCTrack1 in PID.TPC: # Loop over TPC PIDs						
				if (TPCTrack1.NNodes > 18):
					SuitableTPCNodeNumber = True		
					
			if (SuitableTPCNodeNumber):
				
				TPCValidPIDNumber+=1	

				PIDObject = Particles.PIDParticle()
					
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
				
				for ECalTrack in PID.ECAL:
					PIDObject.ECalEnergyList.append(ECalTrack.EMEnergy)#A list of the energies of this ECal in the PID (normally should only be one)
				
				LowestPull=100

				for Particle , ParticlePull in PIDObject.ParticlePull.iteritems():
					
					if (math.fabs(ParticlePull) < math.fabs(LowestPull) and math.fabs(ParticlePull) < math.fabs(NumericalCuts.ParticlePullCut[Particle])):
						
						LowestPull = math.fabs(ParticlePull)
						
						PIDObject.ReconParticleID = Particle

				for TrueTrajectory in This.Truth_Trajectories.Trajectories:#Loop over the truth trajectories for comparison
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
		
		#EventContainsElectronPositron(PIDObjectList)
		
		for PIDObject1 in PIDObjectList:

			This.ROOTFile1.HistogramDictionary["PID_Electron_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Electron])
			This.ROOTFile1.HistogramDictionary["PID_Kaon_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Kaon1])
			This.ROOTFile1.HistogramDictionary["PID_Muon_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.MuLepton])
			This.ROOTFile1.HistogramDictionary["PID_Pion_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Pi1Meson])
			This.ROOTFile1.HistogramDictionary["PID_Proton_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Proton])
			
			This.ROOTFile1.HistogramDictionary["PID_Proton_Against_Muon_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Proton],PIDObject1.ParticlePull[ParticleCodes.MuLepton])

			if (PIDObject1.ReconParticleID == ParticleCodes.Proton):#Looking for reconstructed proton track
				
				ReconstructedProtonTrackNumber += 1
									
				Proton1 = Particles.ReconstructedParticle()
		
				Proton1.EnergyMomentum.T = PIDObject1.ReconstructedParticleEnergy()
				Proton1.EnergyMomentum.X = PIDObject1.ReconFrontMomentum * PIDObject1.ReconFrontDirectionX
				Proton1.EnergyMomentum.Y = PIDObject1.ReconFrontMomentum * PIDObject1.ReconFrontDirectionY
				Proton1.EnergyMomentum.Z = PIDObject1.ReconFrontMomentum * PIDObject1.ReconFrontDirectionZ
									
				This.ROOTFile1.HistogramDictionary["Recon_Truth_Proton_Momentum"].Histogram.Fill(PIDObject1.ReconTrueMomentumDifference())	
				This.ROOTFile1.HistogramDictionary["Truth_Proton_Momentum"].Histogram.Fill(PIDObject1.TrueFrontMomentum)
					
				Proton1.Position.T = PIDObject1.ReconFrontPositionT
				Proton1.Position.X = PIDObject1.ReconFrontPositionX
				Proton1.Position.Y = PIDObject1.ReconFrontPositionY
				Proton1.Position.Z = PIDObject1.ReconFrontPositionZ
								
				ProtonList.append(Proton1)
				
				This.ROOTFile1.HistogramDictionary["Proton_PID_Electron_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Electron])
				This.ROOTFile1.HistogramDictionary["Proton_PID_Kaon_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Kaon1])
				This.ROOTFile1.HistogramDictionary["Proton_PID_Muon_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.MuLepton])
				This.ROOTFile1.HistogramDictionary["Proton_PID_Pion_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Pi1Meson])
				This.ROOTFile1.HistogramDictionary["Proton_PID_Proton_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Proton])
				
				This.ROOTFile1.HistogramDictionary["Proton_PID_Proton_Against_Muon_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Proton],PIDObject1.ParticlePull[ParticleCodes.MuLepton])

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
				
				This.ReconstructedStatistics.Statistics["NPIDsWithCRProton"].Quantity += 1
				
			elif (PIDObject1.ReconParticleID == ParticleCodes.Proton):
				IncorrectlyReconstructedProton +=1
				This.ReconstructedStatistics.Statistics["NPIDsWithIRProton"].Quantity += 1
	
			if (PIDObject1.ReconParticleID == ParticleCodes.Proton):

				This.StackedHistograms["ReconProtonTrueEnergy"].ConstituentFill1D(ParticleCodes.ParticleDictionary, PIDObject1.TrueParticleID, PIDObject1.TrueEnergy,"The Proton-Like Track reconstructed front momentum contribution from a true", "Energy (GeV)", "Number", 100, 0, 5000, "ProtonLikeTrueEnergy")
				This.StackedHistograms["ReconProtonReconMomentum"].ConstituentFill1D(ParticleCodes.ParticleDictionary, PIDObject1.TrueParticleID, PIDObject1.ReconFrontMomentum,"The Proton-Like Track true energy contribution from a true", "Momentum (GeV)", "Number", 100, 0, 3000, "ProtonLikeReconFrontMomentum")

		SingleProtonInFGDFiducial = False
		
		if (ReconstructedProtonTrackNumber == 1):
			
			for PIDObject1 in PIDObjectList:
				
				if (PIDObject1.ReconParticleID == ParticleCodes.Proton):#Looking for reconstructed proton track
					ProtonTrackFrontPositionZ=PIDObject1.ReconFrontPositionZ



					X1 = PIDObject1.ReconFrontPositionX
					Y1 = PIDObject1.ReconFrontPositionY
					Z1 = PIDObject1.ReconFrontPositionZ

					if ((This.FGD1Fiducial.Contains(X1, Y1, Z1) == True) or (This.FGD2Fiducial.Contains(X1, Y1, Z1) == True)):
						SingleProtonInFGDFiducial=True
	
					"""
					inFGDX = (PIDObject1.ReconFrontPositionX >= This.FGD1Fiducial.X1 and PIDObject1.ReconFrontPositionX <= This.FGD1Fiducial.X2)
					inFGDY = (PIDObject1.ReconFrontPositionY >= This.FGD1Fiducial.Y1 and PIDObject1.ReconFrontPositionY <= This.FGD1Fiducial.Y2)
					inFGDZ = (PIDObject1.ReconFrontPositionZ >= This.FGD1Fiducial.Z1 and PIDObject1.ReconFrontPositionZ <= This.FGD1Fiducial.Z2) or (PIDObject1.ReconFrontPositionZ >= This.FGD2Fiducial.Z1 and PIDObject1.ReconFrontPositionZ <= This.FGD2Fiducial.Z2)
					
					if(inFGDX and inFGDY and inFGDZ):
						SingleProtonInFGDFiducial=True
					"""
					
					This.ROOTFile1.HistogramDictionary["Single_Proton_PID_Electron_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Electron])
					This.ROOTFile1.HistogramDictionary["Single_Proton_PID_Kaon_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Kaon1])
					This.ROOTFile1.HistogramDictionary["Single_Proton_PID_Muon_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.MuLepton])
					This.ROOTFile1.HistogramDictionary["Single_Proton_PID_Pion_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Pi1Meson])
					This.ROOTFile1.HistogramDictionary["Single_Proton_PID_Proton_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Proton])
					
					This.ROOTFile1.HistogramDictionary["Single_Proton_PID_Proton_Against_Muon_Pull"].Histogram.Fill(PIDObject1.ParticlePull[ParticleCodes.Proton],PIDObject1.ParticlePull[ParticleCodes.MuLepton])
					
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
		
		for TECObject in This.Reconstructed_TEC.ReconObject:#Loop over these reconstructed objects
			
			ECEnergy = TECObject.EMEnergyFit_Result#The energy of photon
			
			Photon1 = Particles.ReconstructedParticle()
			
			Photon1.EnergyMomentum.T = ECEnergy
			
			ECalPID = False
			
			for PIDObject1 in PIDObjectList:
				for ECalEnergy in PIDObject1.ECalEnergyList:
				
					if (math.fabs(ECalEnergy - ECEnergy) < 1):# Expect that they are equal but I am just allowing for rounding errors
						ECalPID = True
						
			if (ECalPID):
										
				if (TECObject.IsShowerLike):#Check if ECal reconstruction is tracklike or showerlike, it shouldnt matter which for the photon, but the directions are different
					ECUnitDirection = Geometry.ThreeVector(TECObject.Shower.Direction.X(), TECObject.Shower.Direction.Y(), TECObject.Shower.Direction.Z())
					
					Photon1.DirectionIsValid = True
					
					Photon1.Position.T = TECObject.Shower.Position.T()
					Photon1.Position.X = TECObject.Shower.Position.X()
					Photon1.Position.Y = TECObject.Shower.Position.Y()
					Photon1.Position.Z = TECObject.Shower.Position.Z()
					
					Photon1.DirectionType = "ShowerLike"
					
					for Proton1 in ProtonList:

						Angle1 = AngleBetweenDirections(Proton1.Position, Photon1.Position, ECUnitDirection)

						This.StackedHistograms["PhotonAnglesStackedShower"].ConstituentFill1D(ProcessSeparator.ProcessDictionary, EventProcess, Angle1, "Angle for constituent", "Mass (GeV)", "Number", 100, 0, 180, "PhotonAngleShower")
					
					if (len(ProtonList) > 0):
						
						Proton1 = ProtonList[0]
						
						Angle1 = AngleBetweenDirections(Proton1.Position, Photon1.Position, ECUnitDirection)

						if (math.fabs(Angle1) < math.fabs(SmallestAngle)):
							
							SmallestAngle = Angle1
						
					This.StackedHistograms["SelectedPhotonAnglesStackedShower"].ConstituentFill1D(ProcessSeparator.ProcessDictionary, EventProcess, SmallestAngle, "Angle for constituent", "Mass (GeV)", "Number", 100, 0, 180, "SelectedPhotonAngleShower")
				
				SmallestAngle = 180
					
				if (TECObject.IsTrackLike):
					ECUnitDirection = Geometry.ThreeVector(TECObject.Track.Direction.X(), TECObject.Track.Direction.Y(), TECObject.Track.Direction.Z())
							
					Photon1.Position.T = TECObject.Track.Position.T()
					Photon1.Position.X = TECObject.Track.Position.X()
					Photon1.Position.Y = TECObject.Track.Position.Y()
					Photon1.Position.Z = TECObject.Track.Position.Z()
					
					Photon1.DirectionType = "TrackLike"
					
					for Proton1 in ProtonList:
						
						Angle1 = AngleBetweenDirections(Proton1.Position, Photon1.Position, ECUnitDirection)	

						This.StackedHistograms["PhotonAnglesStackedTrack"].ConstituentFill1D(ProcessSeparator.ProcessDictionary, EventProcess, Angle1, "Angle for constituent", "Mass (GeV)", "Number", 100, 0, 180, "PhotonAngleShowerTrack")
						
					if (len(ProtonList) > 0):
												
						Proton1 = ProtonList[0]
						
						Angle1 = AngleBetweenDirections(Proton1.Position, Photon1.Position, ECUnitDirection)	
						
						if (math.fabs(Angle1) < math.fabs(SmallestAngle)):
							
							SmallestAngle = Angle1
						
					This.StackedHistograms["SelectedPhotonAnglesStackedTrack"].ConstituentFill1D(ProcessSeparator.ProcessDictionary, EventProcess, SmallestAngle, "Angle for constituent", "Mass (GeV)", "Number", 100, 0, 180, "SelectedPhotonAngleTrack")

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
			
			PhotonAndProtonAreSelected = False
			
			for Photon1 in PhotonList:
						
				Angle1 = AngleBetweenDirections(Proton1.Position, Photon1.Position, Photon1.Direction)	

				TimeSeparation = math.fabs(float(Proton1.Position.T) - float(Photon1.Position.T))
				
				if (math.fabs(Angle1) < math.fabs(SmallestAngle) and TimeSeparation < 250):
					
					SmallestAngle = Angle1
					
					SelectedPhoton = Photon1
					SelectedProton = Proton1
					
					PhotonAndProtonAreSelected = True
				
				for Photon2 in PhotonList:#For finding invariant mass of pi0
					
					if (Photon2 != Photon1):#Is this valid in python?
						
						Angle2 = AngleBetweenDirections(Proton1.Position, Photon2.Position, Photon2.Direction)

						if ((Angle1 < NumericalCuts.MinimumAngle) and (Angle2 < NumericalCuts.MinimumAngle)):
						
							Pi0Meson = Geometry.FourVector()
							
							Pi0Meson.T = Photon1.EnergyMomentum.T + Photon2.EnergyMomentum.T
							Pi0Meson.X = Photon1.EnergyMomentum.X + Photon2.EnergyMomentum.X
							Pi0Meson.Y = Photon1.EnergyMomentum.Y + Photon2.EnergyMomentum.Y
							Pi0Meson.Z = Photon1.EnergyMomentum.Z + Photon2.EnergyMomentum.Z
							
							This.StackedHistograms["Pi0MesonMass"].ConstituentFill1D(ProcessSeparator.ProcessDictionary, EventProcess, Pi0Meson.InvariantModulus(), "Pi0Meson mass contribution for constituent", "Mass (GeV)", "Number", 100, 0, 1000, "Pi0MesonMass")
					
					
			This.ROOTFile1.HistogramDictionary["SelectedPhotonAngles"].Histogram.Fill(SmallestAngle)
			This.StackedHistograms["SelectedPhotonAnglesStacked"].ConstituentFill1D(ProcessSeparator.ProcessDictionary, EventProcess, SmallestAngle, "Angle for constituent", "Mass (GeV)", "Number", 100, 0, 180, "SelectedPhotonAngle")

			if ((len(PhotonList) > 0) and (PhotonAndProtonAreSelected)):
			
				DeltaBaryon = Geometry.FourVector()
						
				DeltaBaryon.T = SelectedPhoton.EnergyMomentum.T + SelectedProton.EnergyMomentum.T # Delta Baryon Energy
				DeltaBaryon.X = SelectedPhoton.EnergyMomentum.X + SelectedProton.EnergyMomentum.X
				DeltaBaryon.Y = SelectedPhoton.EnergyMomentum.Y + SelectedProton.EnergyMomentum.Y
				DeltaBaryon.Z = SelectedPhoton.EnergyMomentum.Z + SelectedProton.EnergyMomentum.Z
				
				DeltaBaryonMass = DeltaBaryon.InvariantModulus()
		
		############################## Summary Section ########################################

		if (ReconstructedProtonTrack):#Counts number of events with at least one reconstructed proton track
			This.ReconstructedStatistics.Statistics["NEventsWithRProton"].Quantity += 1
		if (ProtonIsCorrectlyReconstructed):
			This.ReconstructedStatistics.Statistics["NEventsWithCRProton"].Quantity += 1
		if (ProtonIsIncorrectlyReconstructed):
			This.ReconstructedStatistics.Statistics["NEventsWithIRProton"].Quantity += 1
		if (NTrackerECalRecon > 0):
			This.ReconstructedStatistics.Statistics["NEventsWithTECC"].Quantity += 1
		if (ReconstructedProtonTrack and NTrackerECalRecon > 0):
			This.ReconstructedStatistics.Statistics["NEventsWithTECCAndCRProton"].Quantity += 1
		if (math.fabs(DeltaBaryonMass - PhysicalConstants.Delta1BaryonMass) < NumericalCuts.InvariantMassVariance):
			SatisfiesInvariantMass = True
		else:
			SatisfiesInvariantMass = False
		
		if (DeltaBaryonMass > 0):
			This.StackedHistograms["FinalInvariantMass"].ConstituentFill1D(ProcessSeparator.ProcessDictionary, EventProcess, DeltaBaryonMass, "Invariant Mass after all cuts for constituent", "Mass (GeV)", "Number", 100, 0, 3000, "FinalInvariantMass")
		
		############################ Cuts #########################
		
		DeltaPGammaCriteria = [True, False, False, False, False, False, False, False, False, False, False]
				
		if (PIDNumber > 0):
			DeltaPGammaCriteria[1] = True
		
		if (TPCValidPIDNumber > 0 and DeltaPGammaCriteria[1]):
			DeltaPGammaCriteria[2] = True
					
		if (ReconstructedProtonTrackNumber > 0 and DeltaPGammaCriteria[2]):
			DeltaPGammaCriteria[3] = True
		
		if (ReconstructedProtonTrackNumber == 1 and DeltaPGammaCriteria[3]):
			DeltaPGammaCriteria[4] = True
		
		if (SingleProtonTrackFirst and DeltaPGammaCriteria[4]):
			DeltaPGammaCriteria[5] = True
		
		if (SingleProtonInFGDFiducial and DeltaPGammaCriteria[5]):
			DeltaPGammaCriteria[6] = True
			
		if (len(PIDObjectList) <= NumericalCuts.DeltaPGammaMultiplicity and DeltaPGammaCriteria[6]):
			DeltaPGammaCriteria[7] = True
			
		if (NTrackerECalRecon > 0 and DeltaPGammaCriteria[7]):
			DeltaPGammaCriteria[8] = True

		if (SmallestAngle <= NumericalCuts.MinimumAngle and DeltaPGammaCriteria[8]):
			DeltaPGammaCriteria[9] = True
			
		if (SatisfiesInvariantMass and DeltaPGammaCriteria[9]):
			DeltaPGammaCriteria[10] = True
		
		DeltaPGammaCutNumber = len(DeltaPGammaCriteria)
		
		#### P Pi0
		
		DeltaPPiCriteria = [True, False, False, False, False, False, False, False, False]
				
		if (PIDNumber > 0):
			DeltaPPiCriteria[1] = True
		
		if (TPCValidPIDNumber > 0 and DeltaPPiCriteria[1]):
			DeltaPPiCriteria[2] = True
					
		if (ReconstructedProtonTrackNumber > 0 and DeltaPPiCriteria[2]):
			DeltaPPiCriteria[3] = True
		
		if (ReconstructedProtonTrackNumber == 1 and DeltaPPiCriteria[3]):
			DeltaPPiCriteria[4] = True
		
		if (SingleProtonTrackFirst and DeltaPPiCriteria[4]):
			DeltaPPiCriteria[5] = True
		
		if (SingleProtonInFGDFiducial and DeltaPPiCriteria[5]):
			DeltaPPiCriteria[6] = True
			
		if ((len(PIDObjectList) <= NumericalCuts.DeltaPGammaMultiplicity) and DeltaPPiCriteria[6]):
			DeltaPPiCriteria[7] = True
			
		if (NTrackerECalRecon > 0 and DeltaPPiCriteria[7]):
			DeltaPPiCriteria[8] = True
		
		DeltaPPiCutNumber = len(DeltaPPiCriteria)
		
		### Creation of Selection Lists:
				
		if (This.TruthStatistics.Statistics["NEvents"].Quantity == 1):
			
			#This.EventPrintoutString += "Evt #"
			
			for CutCounter in xrange(DeltaPGammaCutNumber):
				
				SelectionCriterion1 = SelectionStatistics.SelectionStatistics()
				
				This.SelectionDictionary["DeltaPGamma"].append(SelectionCriterion1)
				
				#This.EventPrintoutString += "\tCut" + str(CutCounter) + ":ER"#
				
			#for CutCounter in xrange(DeltaPGammaCutNumber):
			#	This.EventPrintoutString += "\tCut" + str(CutCounter) + ":P"
				
			for CutCounter in xrange(DeltaPPiCutNumber):
				
				SelectionCriterion1 = SelectionStatistics.SelectionStatistics()
				
				This.SelectionDictionary["DeltaPPi"].append(SelectionCriterion1)	
				
			#This.EventPrintoutString +=	"\n"

		This.EventPrintoutString = str(This.TruthStatistics.Statistics["NEvents"].Quantity)
				
		for CutCounter in xrange(DeltaPGammaCutNumber):
			if (DeltaPGammaCriteria[CutCounter]):
				This.SelectionDictionary["DeltaPGamma"][CutCounter].EventsRemaining += 1
				if (DeltaPGammaEvent):
					This.SelectionDictionary["DeltaPGamma"][CutCounter].TruthDelta += 1
				elif (Delta1BaryonToProtonPi0MesonEvent):
					This.SelectionDictionary["DeltaPGamma"][CutCounter].ReconstructedDelta += 1
				elif ((InteractionType == "RP") and (not DeltaPGammaEvent) and (not Delta1BaryonToProtonPi0MesonEvent)):
					This.SelectionDictionary["DeltaPGamma"][CutCounter].OtherRPInteraction += 1
				elif (InteractionType == "QS"):
					This.SelectionDictionary["DeltaPGamma"][CutCounter].QSInteraction += 1
				elif (InteractionType == "ES"):
					This.SelectionDictionary["DeltaPGamma"][CutCounter].ESInteraction += 1
				elif (InteractionType == "DIS"):
					This.SelectionDictionary["DeltaPGamma"][CutCounter].DISInteraction += 1
				elif (InteractionType == "C"):
					This.SelectionDictionary["DeltaPGamma"][CutCounter].CSInteraction += 1
				
			This.EventPrintoutString += "\t" + str(This.SelectionDictionary["DeltaPGamma"][CutCounter].EventsRemaining)# + "\t" + str(This.SelectionDictionary["DeltaPGamma"][CutCounter].TruthDelta)
			
		for CutCounter in xrange(DeltaPGammaCutNumber):
			if (This.SelectionDictionary["DeltaPGamma"][CutCounter].EventsRemaining > 0):
				Purity = float(This.SelectionDictionary["DeltaPGamma"][CutCounter].TruthDelta) / float(This.SelectionDictionary["DeltaPGamma"][CutCounter].EventsRemaining)
			else:
				Purity = 0
				
			This.EventPrintoutString += "\t" + str(Purity)
		
		if (DeltaPGammaEvent):
			This.EventPrintoutString +=	"\t1" + "\n"
		else:
			This.EventPrintoutString +=	"\t0" + "\n"
		
		This.EventPrinoutFile.write(This.EventPrintoutString)
					
		for CutCounter in xrange(DeltaPPiCutNumber):
			if (DeltaPPiCriteria[CutCounter]):
				This.SelectionDictionary["DeltaPPi"][CutCounter].EventsRemaining += 1
				if (DeltaPGammaEvent):
					This.SelectionDictionary["DeltaPPi"][CutCounter].TruthDelta += 1
				elif (Delta1BaryonToProtonPi0MesonEvent):
					This.SelectionDictionary["DeltaPPi"][CutCounter].ReconstructedDelta += 1
				elif ((InteractionType == "RP") and (not DeltaPGammaEvent) and (not Delta1BaryonToProtonPi0MesonEvent)):
					This.SelectionDictionary["DeltaPPi"][CutCounter].OtherRPInteraction += 1
				elif (InteractionType == "QS"):
					This.SelectionDictionary["DeltaPPi"][CutCounter].QSInteraction += 1
				elif (InteractionType == "ES"):
					This.SelectionDictionary["DeltaPPi"][CutCounter].ESInteraction += 1
				elif (InteractionType == "DIS"):
					This.SelectionDictionary["DeltaPPi"][CutCounter].DISInteraction += 1
				elif (InteractionType == "C"):
					This.SelectionDictionary["DeltaPPi"][CutCounter].CSInteraction += 1
		
		################ Invariant Mass Section #########
		
		if (DeltaPGammaCriteria[len(DeltaPGammaCriteria) - 1] == True):
						
			pass#This.StackedHistograms["FinalInvariantMass"].ConstituentFill1D(ProcessSeparator.ProcessDictionary, EventProcess, DeltaBaryonMass, "Invariant Mass after all cuts for constituent", "Mass (GeV)", "Number", 100, 0, 3000, "FinalInvariantMass")
						
		if (DeltaPGammaCriteria[7] and PhotonAndProtonAreSelected):#Matching Single proton to Every ECal cluster
			
			SelectedProton = ProtonList[0]#This is possibly a wasted line but the above bit is a bit messy
			
			for Photon1 in PhotonList:
				
				DeltaBaryon = Geometry.FourVector()
						
				DeltaBaryon.T = Photon1.EnergyMomentum.T + SelectedProton.EnergyMomentum.T # Delta Baryon Energy
				DeltaBaryon.X = Photon1.EnergyMomentum.X + SelectedProton.EnergyMomentum.X
				DeltaBaryon.Y = Photon1.EnergyMomentum.Y + SelectedProton.EnergyMomentum.Y
				DeltaBaryon.Z = Photon1.EnergyMomentum.Z + SelectedProton.EnergyMomentum.Z
			
				This.StackedHistograms["InvariantMassAllECal"].ConstituentFill1D(ProcessSeparator.ProcessDictionary, EventProcess, DeltaBaryon.InvariantModulus(), "Invariant Mass for constituent", "Mass (GeV)", "Number", 100, 0, 3000, "InvariantMassAllECal")
						
		######### Background Events ##########
			
		
		if (This.SelectBackgroundEvents == True):
			if (DeltaPGammaCriteria[len(DeltaPGammaCriteria) - 1] == True):
				if (InteractionType != "RP"):
					This.BackgroundEventNumbers.append(This.BasicInformation.EventID)
				if (Delta1BaryonToProtonPi0MesonInteraction == True):
					This.BackgroundPiMesonEventNumbers.append(This.BasicInformation.EventID)
				
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
																					
					This.ROOTFile1.HistogramDictionary["Reconstructed_Delta1Baryon_Energy"].Histogram.Fill(DeltaBaryon.T)
					This.ROOTFile1.HistogramDictionary["Reconstructed_Delta1Baryon_MomentumModulus"].Histogram.Fill(DeltaBaryon.SpatialModulus())
					This.ROOTFile1.HistogramDictionary["Reconstructed_Delta1Baryon_Mass"].Histogram.Fill(DeltaBaryon.InvariantModulus())
					
					########################################
					# Angle between Photon Direction and Proton Position #
					########################################
								
								
								
					Angle1 = AngleBetweenDirections(Proton1.Position, Photon1.Position, Photon1.Direction)
					TimeSeparation = math.fabs(float(Proton1.Position.T) - float(Photon1.Position.T))
						
					if (ReconstructedProtonTrack and NTrackerECalRecon > 0 and Angle1 < 10 and Angle1 > -10 and Photon1.DirectionIsValid == True):
						This.ReconstructedStatistics.Statistics["NEventsWithTECCAndCRProtonWithin10D"].Quantity += 1
						
						if (TimeSeparation < 250):
							This.ReconstructedStatistics.Statistics["NEventsWithTECCAndCRProtonWithin10DWithin500ns"].Quantity += 1
					
					This.ROOTFile1.HistogramDictionary["PhotonAngles"].Histogram.Fill(Angle1)#!! Should this not be Angle1? Ive now changed it
					This.StackedHistograms["PhotonAnglesStacked"].ConstituentFill1D(ProcessSeparator.ProcessDictionary, EventProcess, Angle1, "Angle for constituent", "Mass (GeV)", "Number", 100, 0, 180, "PhotonAngle")
					This.ROOTFile1.HistogramDictionary["ProtonPhotonTimeSeparations"].Histogram.Fill(TimeSeparation)
					
					
					if (TimeSeparation < 250):
																						
						This.ROOTFile1.HistogramDictionary["Reconstructed_Delta1Baryon_Energy_TimeSeparated"].Histogram.Fill(DeltaBaryon.T)
						This.ROOTFile1.HistogramDictionary["Reconstructed_Delta1Baryon_MomentumModulus_TimeSeparated"].Histogram.Fill(DeltaBaryon.SpatialModulus())
						This.ROOTFile1.HistogramDictionary["Reconstructed_Delta1Baryon_Mass_TimeSeparated"].Histogram.Fill(DeltaBaryon.InvariantModulus())
					
				
			for GRTVertex1 in This.Truth_GRTVertices.Vtx: 
				for GRTParticle1 in This.RTTools.getParticles(GRTVertex1):
					# Consider the truth data events. If it contains a Delta Baryon, then retrieve its kinematics for comparison.
					
					if (GRTParticle1.pdg == ParticleCodes.Delta1Baryon):
						
						DeltaBaryon = Geometry.FourVector()
					
						DeltaBaryon.T = GRTParticle1.momentum[3] * 1000 # Unit Conversion
						DeltaBaryon.X = GRTParticle1.momentum[0] * 1000
						DeltaBaryon.Y = GRTParticle1.momentum[1] * 1000
						DeltaBaryon.Z = GRTParticle1.momentum[2] * 1000
						
						This.ROOTFile1.HistogramDictionary["Truth_Delta1Baryon_Energy"].Histogram.Fill(DeltaBaryon.T)
						This.ROOTFile1.HistogramDictionary["Truth_Delta1Baryon_MomentumModulus"].Histogram.Fill(DeltaBaryon.SpatialModulus())
						This.ROOTFile1.HistogramDictionary["Truth_Delta1Baryon_Mass"].Histogram.Fill(DeltaBaryon.InvariantModulus())

		########################################
		
"""
def (This, PIDParticles1):
		
	EventContainsElectronPositron = False
	
	for PIDParticle1 in PIDParticles1:
		for PIDParticle2 in PIDParticles1:
			
			if ((PIDParticle1.ReconParticleID == ParticleCodes.Electron) and (PIDParticle2.ReconParticleID == ParticleCodes.MuLepton)):
				if ((PIDParticle1.ReconFrontPositionX - PIDParticle2.ReconFrontPositionX < 1) and (PIDParticle1.ReconFrontPositionY - PIDParticle2.ReconFrontPositionY < 1) and (PIDParticle1.ReconFrontPositionZ - PIDParticle2.ReconFrontPositionZ < 1)):
					
					EventContainsElectronPositron = True
					
					RParticle1 = Particles.ReconstructedParticle()
					RParticle2 = Particles.ReconstructedParticle()
					
					RParticle1.EnergyMomentum.T = PIDParticle1.ReconstructedParticleEnergy()
					RParticle1.EnergyMomentum.X = PIDParticle1.ReconFrontDirectionX * PIDParticle1.ReconFrontMomentum
					RParticle1.EnergyMomentum.Y = PIDParticle1.ReconFrontDirectionY * PIDParticle1.ReconFrontMomentum
					RParticle1.EnergyMomentum.Z = PIDParticle1.ReconFrontDirectionZ * PIDParticle1.ReconFrontMomentum
					
					RParticle2.EnergyMomentum.T = PIDParticle2.ReconstructedParticleEnergy()
					RParticle2.EnergyMomentum.X = PIDParticle2.ReconFrontDirectionX * PIDParticle2.ReconFrontMomentum
					RParticle2.EnergyMomentum.Y = PIDParticle2.ReconFrontDirectionY * PIDParticle2.ReconFrontMomentum
					RParticle2.EnergyMomentum.Z = PIDParticle2.ReconFrontDirectionZ * PIDParticle2.ReconFrontMomentum
					
					FourVector1 = Geometry.FourVector()
					
					FourVector1.T = RParticle1.EnergyMomentum.T - RParticle2.EnergyMomentum.T
					FourVector1.X = RParticle1.EnergyMomentum.X - RParticle2.EnergyMomentum.X
					FourVector1.Y = RParticle1.EnergyMomentum.Y - RParticle2.EnergyMomentum.Y
					FourVector1.Z = RParticle1.EnergyMomentum.Z - RParticle2.EnergyMomentum.Z
					
					This.HistogramCollection1.Histograms["ElectronPositronInvariantMass"].Populate(FourVector1.InvariantModulus())
	
	return EventContainsElectronPositron
"""#I've just blanked out this for now				
		
		
		

def AngleBetweenDirections(Position1, Position2, Direction2):

	Angle1 = 180
	
	Line1 = Geometry.ThreeVector()
	Line2 = Geometry.ThreeVector()
	
	Line1.X = Position2.X - Position1.X
	Line1.Y = Position2.Y - Position1.Y
	Line1.Z = Position2.Z - Position1.Z
	
	Line2.X = Direction2.X
	Line2.Y = Direction2.Y
	Line2.Z = Direction2.Z
					
	Angle1 = Geometry.FindAngle(Line1, Line2)
	
	return Angle1
	

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