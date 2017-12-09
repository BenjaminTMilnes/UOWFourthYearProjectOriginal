# Analysis
#
# T. R. Bromley and B. T. Milnes
#

import sys
import os

import math
import glob
import array
import copy

import datetime
import time

import libraries
import ROOT
import RooTrackerTools

ROOT.gROOT.SetBatch(True)

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


import ProgressMeter

import CommandLine
import FileAdministrator

import Simulation
import Charts
import Particles

Now = datetime.datetime.now()
DataLocation = "/storage/epp2/phujce/Final Year Project/Main/Data Archive/"


class Analysis:
	
	def __init__(This, InputFileLocatorList, OutputROOTFileLocator, SimulationInformationFileLocator, SimulationInformation):
		
		This.InputFileLocatorList = InputFileLocatorList
		This.OutputROOTFileLocator = OutputROOTFileLocator
		This.SimulationInformationFileLocator = SimulationInformationFileLocator
		This.SimulationInformation = SimulationInformation
		
		OutputListFileLocator = FileAdministrator.CreateFilePath(DataLocation, ".list", SimulationInformation)
		This.OutputListFile = open(OutputListFileLocator, "w")
				
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
		This.SelectionDictionary["ProtonPhotonToElectrons"] = []		
		
		This.InputTimeTest = False
		This.SelectBackgroundEvents = False
				
		This.EventCollection1 = Simulation.EventCollection()
		
		This.HistogramCollection1 = Charts.HistogramCollection()
		
		
		This.Parameters = {} # In some cases we have parameters which we could vary to improve purity, and which are used throughout the analysis. They can be assigned here.
		
		This.Parameters["LocalityLimit"] = 50 # In millimetres
		This.Parameters["PhotonAngularLocalityLimit"] = 20 # In degrees
		This.Parameters["PairProductionAngularLocalityLimit"] = 20 # In degrees
		This.Parameters["SynchronicityLimit"] = 250 # In nanoseconds
		
		This.Parameters["PathMultiplicityLimit"] = 3
		This.Parameters["TorrentMultiplicityLimit"] = 100 # Effectively no limit
		
		This.Parameters["PullLimits"] = {}
		
		This.Parameters["PullLimits"][ParticleCodes.Electron] = 3
		This.Parameters["PullLimits"][ParticleCodes.K1Meson] = 4
		This.Parameters["PullLimits"][ParticleCodes.MuLepton] = 2
		This.Parameters["PullLimits"][ParticleCodes.Pi1Meson] = 2
		This.Parameters["PullLimits"][ParticleCodes.Proton] = 4
		
		This.Parameters["InvariantMassVarianceLimit"] = 250
				
				
		This.Processes = {} # This dictionary contains titles for the interactions and processes we expect to see.
		
		This.Processes["Delta1ToProtonPhoton"] = "Delta 1 to Proton-Photon Interactions"
		This.Processes["Delta1ToProtonPi0"] = "Delta 1 to Proton-Pi-0 Interactions"
		This.Processes["OtherResonance"] = "Other Resonance Production Interactions"
		This.Processes["QS"] = "Quasielastic Scattering"
		This.Processes["ES"] = "Elastic Scattering"
		This.Processes["DIS"] = "Deep Inelastic Scattering"
		This.Processes["C"] = "Coherent Scattering"
		This.Processes["Other"] = "Other Interactions"
		
		This.ROOTFile1 = ROOTFile.ROOTFile(This.OutputROOTFileLocator)
		
	
	def LoadInputFiles(This, DesiredEventNumber):		
		# Adds each file in the list of input file names to each module we want to use		

		for FileLocator in This.InputFileLocatorList:
			
			if (This.Modules[0].GetEntries() <= DesiredEventNumber):
			
				for Module in This.Modules:
					Module.Add(FileLocator)
					
				This.OutputListFile.write(str(FileLocator) + TextConstants.NewLine)
					
			else:
				break
				
		This.OutputListFile.close()
				
		MaximumEventNumber = Module.GetEntries()
				
		return MaximumEventNumber
		
	def LoadModule(This, Module_Reference):	
		
		Module = ROOT.TChain(Module_Reference)
		This.Modules.append(Module)
		
		return Module
	
		
	def Analyse(This, DesiredEventNumber = 999999999):

		if (This.SelectBackgroundEvents):
			
			This.DeltaPGammaEventFileLocator = FileAdministrator.CreateFilePath(DataLocation, "_DeltaPGamma.Event", This.SimulationInformation)
			This.DeltaPPiEventFileLocator = FileAdministrator.CreateFilePath(DataLocation, "_DeltaPPi.Event", This.SimulationInformation)
			This.DeltaPGammaPPEventFileLocator = FileAdministrator.CreateFilePath(DataLocation, "_DeltaPGammaPP.Event", This.SimulationInformation)

		MaximumEventNumber = This.LoadInputFiles(DesiredEventNumber)

		This.FGD1 = Geometry.ThreeDimensionalObject(-832.2, 832.2, -777.2, 887.2, 123.45, 446.95)
		This.FGD2 = Geometry.ThreeDimensionalObject(-832.2, 832.2, -777.2, 887.2, 1481.45, 1807.95)
		
		This.FGD1Fiducial = Geometry.ThreeDimensionalObject(-874.51, 874.51, -819.51, 929.51, 136.875, 446.955)#NB: in email he said 1446.955 but i am guessing this is typo
		This.FGD2Fiducial = Geometry.ThreeDimensionalObject(-874.51, 874.51, -819.51, 929.51, 1481.5, 1810)
		
		This.StackedHistograms = {}
	
		This.InitialiseStatistics()		
		This.InitialiseHistograms()				
		
		
			
		EventNumber = min(MaximumEventNumber, DesiredEventNumber)

		print TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine, TextConstants.LineSeparator
		if (MaximumEventNumber < DesiredEventNumber):
			print "Warning: the number of events within the file list is less than the number of events requested."
		print "Reading", EventNumber, "Events"
		print TextConstants.LineSeparator
		
		ProgressMeter1 = ProgressMeter.ProgressMeter(EventNumber - 1)
		
		SuitableEvents = 0
		
		StartTime = time.time()
		PreviousTime = 0
		
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
		
				if (ProgressMeter1.Update(i)):
					
					del sys.stdout
					del sys.stderr
					
					sys.stdout = DataWriter.DataWriterStdOut(This.SimulationInformationFileLocator, "a")
					sys.stderr = DataWriter.DataWriterStdErr(This.SimulationInformationFileLocator, "a")
				
				OutputData = False
				
				if (SuitableEvent):
					
					SuitableEvents += 1
					
					This.runEvent()
					
					CurrentTime = ElapsedTime(StartTime, 500000000000000000000)#One Hour

					if ((CurrentTime != PreviousTime)):
						OutputData = True
						
					PreviousTime = CurrentTime
					
				if ((OutputData or (i == EventNumber - 1)) and (SuitableEvents > 0)):
					
					print "ROOT Histograms and text data have been outputted to file after an elapsed time of" , CurrentTime , "hours."
					
					TimeOutputFile = copy.deepcopy(This.ROOTFile1)
					TimeStackedHistograms = copy.deepcopy(This.StackedHistograms)
					
					TimeOutputFile.Open()
													
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
								SelectionStatistics1.MixedPurity = float(SelectionStatistics1.MixedEvent) / float(EventsRemaining)
							
							else:
								SelectionStatistics1.Purity = 0
								SelectionStatistics1.PionPurity = 0
								SelectionStatistics1.RPPurity = 0
								SelectionStatistics1.QSPurity = 0
								SelectionStatistics1.ESPurity = 0
								SelectionStatistics1.DISPurity = 0
								SelectionStatistics1.CSPurity = 0
								SelectionStatistics1.OtherPurity = 0
								SelectionStatistics1.MixedPurity = 0
								
									
							PreviousEventsRemaining = SelectionStatistics1.EventsRemaining

						SelectionChannel[0].TruthDelta = This.TruthStatistics.Statistics["NDeltaToProtonPhoton"].Quantity

						SelectionChannel[0].RelativeEfficiency = 1
						SelectionChannel[0].AbsoluteEfficiency = 1
			
					############################# Graphs of cuts

					for Key, SelectionChannel in This.SelectionDictionary.iteritems():

						Location = "Cuts/" + Key + "/"
						CutNumber = len(SelectionChannel)

						AbsoluteEfficiencyReference = "AbsoluteEfficiency" + Key

						TimeOutputFile.NewHistogram1D(AbsoluteEfficiencyReference, "Absolute Efficiency for the Selections", "Selections", "Absolute Efficiency", CutNumber, 0, CutNumber, Location)

						for CriteriaListCounter in xrange(CutNumber):
							
							TimeOutputFile.HistogramDictionary[AbsoluteEfficiencyReference].Histogram.Fill(CriteriaListCounter,SelectionChannel[CriteriaListCounter].AbsoluteEfficiency)
							
						for CutCounter in xrange(len(SelectionChannel)):
							
							if(CutCounter == 0):
								BinLabel = "Starting Events"
							else:
								BinLabel = "Criterion " + str(CutCounter)
							
							TimeOutputFile.HistogramDictionary[AbsoluteEfficiencyReference].Histogram.GetXaxis().SetBinLabel(CutCounter+1, BinLabel)

						TimeOutputFile.HistogramDictionary[AbsoluteEfficiencyReference].Histogram.SetMarkerStyle(3)
						TimeOutputFile.HistogramDictionary[AbsoluteEfficiencyReference].Histogram.SetOption("LP")
						TimeOutputFile.HistogramDictionary[AbsoluteEfficiencyReference].Histogram.SetStats(0)

						RelativeEfficiencyReference = "RelativeEfficiency" + Key

						TimeOutputFile.NewHistogram1D(RelativeEfficiencyReference, "Relative Efficiency for the Selections", "Selections", "Relative Efficiency", CutNumber, 0, CutNumber, Location)

						for CriteriaListCounter in xrange(CutNumber):
							
							TimeOutputFile.HistogramDictionary[RelativeEfficiencyReference].Histogram.Fill(CriteriaListCounter, SelectionChannel[CriteriaListCounter].RelativeEfficiency)
							
						for CutCounter in xrange(len(SelectionChannel)):
							
							if(CutCounter == 0):
								BinLabel = "Starting Events"
							else:
								BinLabel = "Criterion " + str(CutCounter)
							
							TimeOutputFile.HistogramDictionary[RelativeEfficiencyReference].Histogram.GetXaxis().SetBinLabel(CutCounter+1, BinLabel)
						
						TimeOutputFile.HistogramDictionary[RelativeEfficiencyReference].Histogram.SetMarkerStyle(3)
						TimeOutputFile.HistogramDictionary[RelativeEfficiencyReference].Histogram.SetOption("LP")
						TimeOutputFile.HistogramDictionary[RelativeEfficiencyReference].Histogram.SetStats(0)
						
						PurityReference = "Purity" + Key
						
						TimeOutputFile.NewHistogram1D(PurityReference, "Purity for the Selections", "Selections", "Purity", CutNumber, 0, CutNumber, Location)

						for CriteriaListCounter in xrange(CutNumber):

							if	(Key == "DeltaPGamma"):
								TimeOutputFile.HistogramDictionary[PurityReference].Histogram.Fill(CriteriaListCounter,SelectionChannel[CriteriaListCounter].Purity)
								
								if (SelectionChannel[CriteriaListCounter].EventsRemaining > 0 and SelectionChannel[CriteriaListCounter].Purity < 1):
									PurityError = math.sqrt(float(SelectionChannel[CriteriaListCounter].Purity - (SelectionChannel[CriteriaListCounter].Purity * SelectionChannel[CriteriaListCounter].Purity)) / float(SelectionChannel[CriteriaListCounter].EventsRemaining))
								else:
									PurityError = 0
									
								TimeOutputFile.HistogramDictionary[PurityReference].Histogram.SetBinError(CriteriaListCounter + 1, PurityError)
								
							elif (Key == "DeltaPPi"):
								TimeOutputFile.HistogramDictionary[PurityReference].Histogram.Fill(CriteriaListCounter,SelectionChannel[CriteriaListCounter].PionPurity)
								
								if (SelectionChannel[CriteriaListCounter].EventsRemaining > 0 and SelectionChannel[CriteriaListCounter].PionPurity < 1):
									PurityError = math.sqrt(float(SelectionChannel[CriteriaListCounter].PionPurity - (SelectionChannel[CriteriaListCounter].PionPurity * SelectionChannel[CriteriaListCounter].PionPurity)) / float(SelectionChannel[CriteriaListCounter].EventsRemaining))
								else:
									PurityError = 0
									
								TimeOutputFile.HistogramDictionary[PurityReference].Histogram.SetBinError(CriteriaListCounter + 1, PurityError)
								
							elif (Key == "ProtonPhotonToElectrons"):
								TimeOutputFile.HistogramDictionary[PurityReference].Histogram.Fill(CriteriaListCounter,SelectionChannel[CriteriaListCounter].Purity)
								
								if (SelectionChannel[CriteriaListCounter].EventsRemaining > 0 and SelectionChannel[CriteriaListCounter].Purity < 1):
									PurityError = math.sqrt(float(SelectionChannel[CriteriaListCounter].Purity - (SelectionChannel[CriteriaListCounter].Purity * SelectionChannel[CriteriaListCounter].Purity)) / float(SelectionChannel[CriteriaListCounter].EventsRemaining))
								else:
									PurityError = 0
									
								TimeOutputFile.HistogramDictionary[PurityReference].Histogram.SetBinError(CriteriaListCounter + 1, PurityError)
								
						for CutCounter in xrange(len(SelectionChannel)):
							
							if(CutCounter == 0):
								BinLabel = "Starting Events"
							else:
								BinLabel = "Criterion " + str(CutCounter)
							
							TimeOutputFile.HistogramDictionary[PurityReference].Histogram.GetXaxis().SetBinLabel(CutCounter+1, BinLabel)
						
						TimeOutputFile.HistogramDictionary[PurityReference].Histogram.SetMarkerStyle(3)
						TimeOutputFile.HistogramDictionary[PurityReference].Histogram.SetOption("E1")
						TimeOutputFile.HistogramDictionary[PurityReference].Histogram.SetStats(0)
										
						NormalisedPurityReference = "NormalisedPurity" + Key
						
						TimeStackedHistograms[NormalisedPurityReference]=StackedHistogram.StackedHistogram(NormalisedPurityReference, "Constituent processes after each cut (Normalised)", 0.7, 0.65, 0.86, 0.88, "Cuts", "Events Remaining", Location + "Normalised/")

						NormalisedPurityTitle = "Purity as a function of selection for"

						for CriteriaListCounter in xrange(CutNumber):
											
							if(SelectionChannel[CriteriaListCounter].Purity > 0):
								
								TimeStackedHistograms[NormalisedPurityReference].AttemptToFill2D(NormalisedPurityTitle, "Delta -> p gamma interactions", "NormalisedPurity:DeltaPGamma" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Normalised/Constituent Histograms/", CriteriaListCounter, SelectionChannel[CriteriaListCounter].Purity, "Delta -> p gamma Interactions")
							
							if(SelectionChannel[CriteriaListCounter].PionPurity > 0):
								
								TimeStackedHistograms[NormalisedPurityReference].AttemptToFill2D(NormalisedPurityTitle, "Delta -> p pi interactions", "NormalisedPurity:DeltaPPi" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Normalised/Constituent Histograms/", CriteriaListCounter, SelectionChannel[CriteriaListCounter].PionPurity, "Delta -> p pi Interactions")
						
							if(SelectionChannel[CriteriaListCounter].RPPurity > 0):
								
								TimeStackedHistograms[NormalisedPurityReference].AttemptToFill2D(NormalisedPurityTitle, "Other Resonance Production", "NormalisedPurity:OtherResonance" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Normalised/Constituent Histograms/", CriteriaListCounter, SelectionChannel[CriteriaListCounter].RPPurity, "Other Resonance Production")
								
							if(SelectionChannel[CriteriaListCounter].QSPurity > 0):
								
								TimeStackedHistograms[NormalisedPurityReference].AttemptToFill2D(NormalisedPurityTitle, "Quasi-Elastic Scattering", "NormalisedPurity:QES" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Normalised/Constituent Histograms/", CriteriaListCounter, SelectionChannel[CriteriaListCounter].QSPurity, "Quasi-Elastic Scattering")
							
							if(SelectionChannel[CriteriaListCounter].ESPurity > 0):
													
								TimeStackedHistograms[NormalisedPurityReference].AttemptToFill2D(NormalisedPurityTitle, "Elastic Scattering", "NormalisedPurity:ES" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Normalised/Constituent Histograms/", CriteriaListCounter, SelectionChannel[CriteriaListCounter].ESPurity, "Elastic Scattering")
						
							if(SelectionChannel[CriteriaListCounter].DISPurity > 0):
								
								TimeStackedHistograms[NormalisedPurityReference].AttemptToFill2D(NormalisedPurityTitle, "Deep Inelastic Scattering", "NormalisedPurity:DIS" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Normalised/Constituent Histograms/", CriteriaListCounter, SelectionChannel[CriteriaListCounter].DISPurity, "Deep Inelastic Scattering")
								
							if(SelectionChannel[CriteriaListCounter].CSPurity > 0):
								
								TimeStackedHistograms[NormalisedPurityReference].AttemptToFill2D(NormalisedPurityTitle, "Coherent Scattering", "NormalisedPurity:C" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Normalised/Constituent Histograms/", CriteriaListCounter, SelectionChannel[CriteriaListCounter].CSPurity, "Coherent Scattering")
													
							if(SelectionChannel[CriteriaListCounter].OtherPurity > 0):
								
								TimeStackedHistograms[NormalisedPurityReference].AttemptToFill2D(NormalisedPurityTitle, "Other Interactions", "NormalisedPurity:Other" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Normalised/Constituent Histograms/", CriteriaListCounter, SelectionChannel[CriteriaListCounter].OtherPurity, "Other Interactions")
								
							if(SelectionChannel[CriteriaListCounter].MixedPurity > 0):

								TimeStackedHistograms[NormalisedPurityReference].AttemptToFill2D(NormalisedPurityTitle, "Mixed Events", "NormalisedPurity:Mixed" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Normalised/Constituent Histograms/", CriteriaListCounter, SelectionChannel[CriteriaListCounter].MixedPurity, "Mixed Events")
						
						for Histogram1 in TimeStackedHistograms[NormalisedPurityReference].HistogramDictionary.itervalues():
							for CutCounter in xrange(len(SelectionChannel)):
								
								if(CutCounter == 0):
									BinLabel = "Starting Events"
								else:
									BinLabel = "Criterion " + str(CutCounter)
								
								Histogram1.Histogram.GetXaxis().SetBinLabel(CutCounter+1, BinLabel)
		
					############## Application of truth to criteria
						
						CutPurityReference = "CutPurity" + Key
						
						TimeStackedHistograms[CutPurityReference]=StackedHistogram.StackedHistogram(CutPurityReference, "Constituent Processes for the Events after every Selection",0.7,0.65,0.86,0.88, "Cuts", "Events Remaining", Location + "/Energy/")

						for CutCounter in xrange(len(SelectionChannel)):
							for FillCounter in xrange(SelectionChannel[CutCounter].TruthDelta):
								TimeStackedHistograms[CutPurityReference].AttemptToFill1D(NormalisedPurityTitle, "Delta -> p gamma interactions", "Purity:DeltaPGamma" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Energy/Constituent Histograms/", CutCounter, "Delta -> p gamma Interactions")
							for FillCounter in xrange(SelectionChannel[CutCounter].ReconstructedDelta):
								TimeStackedHistograms[CutPurityReference].AttemptToFill1D(NormalisedPurityTitle, "Delta -> p pi interactions", "Purity:DeltaPPi" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Energy/Constituent Histograms/", CutCounter, "Delta -> p pi Interactions")
							for FillCounter in xrange(SelectionChannel[CutCounter].OtherRPInteraction):
								TimeStackedHistograms[CutPurityReference].AttemptToFill1D(NormalisedPurityTitle, "Other Resonance Production", "Purity:OtherResonance" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Energy/Constituent Histograms/", CutCounter, "Other Resonance Production")
							for FillCounter in xrange(SelectionChannel[CutCounter].QSInteraction):
								TimeStackedHistograms[CutPurityReference].AttemptToFill1D(NormalisedPurityTitle, "Quasi-Elastic Scattering", "Purity:QES" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Energy/Constituent Histograms/", CutCounter, "Quasi-Elastic Scattering")
							for FillCounter in xrange(SelectionChannel[CutCounter].ESInteraction):
								TimeStackedHistograms[CutPurityReference].AttemptToFill1D(NormalisedPurityTitle, "Elastic Scattering", "Purity:ES" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Energy/Constituent Histograms/", CutCounter, "Elastic Scattering")
							for FillCounter in xrange(SelectionChannel[CutCounter].DISInteraction):
								TimeStackedHistograms[CutPurityReference].AttemptToFill1D(NormalisedPurityTitle, "Deep Inelastic Scattering", "Purity:DIS" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Energy/Constituent Histograms/", CutCounter, "Deep Inelastic Scattering")
							for FillCounter in xrange(SelectionChannel[CutCounter].CSInteraction):
								TimeStackedHistograms[CutPurityReference].AttemptToFill1D(NormalisedPurityTitle, "Coherent Scattering", "Purity:C" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Energy/Constituent Histograms/", CutCounter, "Coherent Scattering")
							for FillCounter in xrange(SelectionChannel[CutCounter].OtherInteraction):
								TimeStackedHistograms[CutPurityReference].AttemptToFill1D(NormalisedPurityTitle, "Other Interactions", "Purity:Other" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Energy/Constituent Histograms/", CutCounter, "Other Interactions")
							for FillCounter in xrange(SelectionChannel[CutCounter].MixedEvent):
								TimeStackedHistograms[CutPurityReference].AttemptToFill1D(NormalisedPurityTitle, "Mixed Events", "Purity:Mixed" + Key, "Selections", "Purity", CutNumber, 0, CutNumber, Location + "/Energy/Constituent Histograms/", CutCounter, "Mixed Events")
								
						for Histogram1 in TimeStackedHistograms[CutPurityReference].HistogramDictionary.itervalues():
							for CutCounter in xrange(len(SelectionChannel)):
							
								if(CutCounter == 0):
									BinLabel = "Starting Events"
								else:
									BinLabel = "Criterion " + str(CutCounter)
							
								Histogram1.Histogram.GetXaxis().SetBinLabel(CutCounter+1, BinLabel)

					################# Finalising histograms and writing to file #########
						
					for StackedHistogramName1, StackedHistogram1 in TimeStackedHistograms.iteritems():

						StackedHistogram1.AutoPrepare("f")
					
						CanvasTitle = "Canvas of " + StackedHistogramName1
						
						TimingStamp = "NE" + str(i)#Im not really sure why this is needed, I think it is a problem with ROOT's draw command

						(Canvas, Directory) = StackedHistogram1.StackedHistogramCanvas(StackedHistogramName1 + TimingStamp, CanvasTitle, 700, 500)
					
						try:
							TimeOutputFile.NewStackedHistogramCanvas(StackedHistogramName1, Canvas, Directory)

						except:
							pass
					
						StackedHistogram1.DrawConstituentHistograms(TimeOutputFile)
					
					# This is transitional code and will be altered later.
					
					#TimeOutputFile.HistogramDictionary["Final_Invariant_Mass"] = This.HistogramCollection1.Histograms["Final_Invariant_Mass"].ToHistogramStorage()
					#TimeOutputFile.HistogramDictionary["Invariant_Mass_All_ECal"] = This.HistogramCollection1.Histograms["Invariant_Mass_All_ECal"].ToHistogramStorage()
					#TimeOutputFile.HistogramDictionary["Pi0_Meson_Mass"] = This.HistogramCollection1.Histograms["Pi0_Meson_Mass"].ToHistogramStorage()
					#TimeOutputFile.HistogramDictionary["Single_Proton_PID_Multiplicity"] = This.HistogramCollection1.Histograms["Single_Proton_PID_Multiplicity"].ToHistogramStorage()
					#TimeOutputFile.HistogramDictionary["Single_Proton_ECal_Multiplicity"] = This.HistogramCollection1.Histograms["Single_Proton_ECal_Multiplicity"].ToHistogramStorage()
					#TimeOutputFile.HistogramDictionary["Proton_Muon_Separation"] = This.HistogramCollection1.Histograms["Proton_Muon_Separation"].ToHistogramStorage()
										
					#TimeOutputFile.HistogramDictionary["ElectronPull2"] = This.HistogramCollection1.Histograms["ElectronPull"].ToHistogramStorage()
					#TimeOutputFile.HistogramDictionary["KaonPull2"] = This.HistogramCollection1.Histograms["KaonPull"].ToHistogramStorage()
					#TimeOutputFile.HistogramDictionary["MuonPull2"] = This.HistogramCollection1.Histograms["MuonPull"].ToHistogramStorage()
					#TimeOutputFile.HistogramDictionary["PionPull2"] = This.HistogramCollection1.Histograms["PionPull"].ToHistogramStorage()
					#TimeOutputFile.HistogramDictionary["ProtonPull2"] = This.HistogramCollection1.Histograms["ProtonPull"].ToHistogramStorage()

					TimeOutputFile.Write()
					TimeOutputFile.Close()
								
					del TimeOutputFile
					del TimeStackedHistograms
														
					This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents0EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPGamma"][0].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents0Delta"].Quantity = This.SelectionDictionary["DeltaPGamma"][0].TruthDelta
					This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents1EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPGamma"][1].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents1Delta"].Quantity = This.SelectionDictionary["DeltaPGamma"][1].TruthDelta
					This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents2EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPGamma"][2].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents2Delta"].Quantity = This.SelectionDictionary["DeltaPGamma"][2].TruthDelta
					This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents3EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPGamma"][3].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents3Delta"].Quantity = This.SelectionDictionary["DeltaPGamma"][3].TruthDelta
					This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents4EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPGamma"][4].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents4Delta"].Quantity = This.SelectionDictionary["DeltaPGamma"][4].TruthDelta
					This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents5EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPGamma"][5].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents5Delta"].Quantity = This.SelectionDictionary["DeltaPGamma"][5].TruthDelta
					This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents6EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPGamma"][6].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents6Delta"].Quantity = This.SelectionDictionary["DeltaPGamma"][6].TruthDelta
					#!! nb the descriptions must be updated
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents7EventsRemaining"].Title = "Selection 7 - Fewer than " + str(This.Parameters["PathMultiplicityLimit"]) + " PIDs in total - Events Remaining"
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents7EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPGamma"][7].EventsRemaining
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents7Delta"].Title = "Selection 7 - Fewer than " + str(This.Parameters["PathMultiplicityLimit"]) + " PIDs in total - Delta -> p gamma Events Remaining"
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents7Delta"].Quantity = This.SelectionDictionary["DeltaPGamma"][7].TruthDelta
						
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents8EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPGamma"][8].EventsRemaining			
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents8Delta"].Quantity = This.SelectionDictionary["DeltaPGamma"][8].TruthDelta
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents9EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPGamma"][9].EventsRemaining					
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents9Delta"].Quantity = This.SelectionDictionary["DeltaPGamma"][9].TruthDelta
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents10EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPGamma"][10].EventsRemaining
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents10Delta"].Quantity = This.SelectionDictionary["DeltaPGamma"][10].TruthDelta
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents11EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPGamma"][11].EventsRemaining
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents11Delta"].Quantity = This.SelectionDictionary["DeltaPGamma"][11].TruthDelta

					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents12EventsRemaining"].Title = "Selection 12 - The smallest photon angle was less than " + str(This.Parameters["PhotonAngularLocalityLimit"]) + " degees - Events Remaining"
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents12EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPGamma"][12].EventsRemaining
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents12Delta"].Title = "Selection 12 - The smallest photon angle was less than " + str(This.Parameters["PhotonAngularLocalityLimit"]) + " degees - Delta -> p gamma Events Remaining"
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents12Delta"].Quantity = This.SelectionDictionary["DeltaPGamma"][12].TruthDelta
					
					
					
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents0EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][0].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents0Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][0].ReconstructedDelta
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents1EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][1].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents1Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][1].ReconstructedDelta
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents2EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][2].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents2Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][2].ReconstructedDelta
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents3EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][3].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents3Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][3].ReconstructedDelta
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents4EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][4].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents4Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][4].ReconstructedDelta
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents5EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][5].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents5Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][5].ReconstructedDelta
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents6EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][6].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents6Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][6].ReconstructedDelta
					
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents7EventsRemaining"].Title = "Selection 7 - Fewer than " + str(This.Parameters["PathMultiplicityLimit"]) + " PIDs in total - Events Remaining"
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents7EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][7].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents7Delta"].Title = "Selection 7 - Fewer than " + str(This.Parameters["PathMultiplicityLimit"]) + " PIDs in total - Delta -> p pi Events Remaining"
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents7Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][7].ReconstructedDelta
					
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents8EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][8].EventsRemaining			
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents8Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][8].ReconstructedDelta
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents9EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][9].EventsRemaining					
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents9Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][9].ReconstructedDelta
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents10EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][10].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents10Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][10].ReconstructedDelta
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents11EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][11].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents11Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][11].ReconstructedDelta

					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents0EventsRemaining"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][0].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents0Delta"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][0].TruthDelta
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents1EventsRemaining"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][1].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents1Delta"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][1].TruthDelta
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents2EventsRemaining"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][2].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents2Delta"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][2].TruthDelta
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents3EventsRemaining"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][3].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents3Delta"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][3].TruthDelta
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents4EventsRemaining"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][4].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents4Delta"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][4].TruthDelta
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents5EventsRemaining"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][5].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents5Delta"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][5].TruthDelta
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents6EventsRemaining"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][6].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents6Delta"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][6].TruthDelta
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents7EventsRemaining"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][7].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents7Delta"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][7].TruthDelta
					"""This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents8EventsRemaining"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][8].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents8Delta"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][8].TruthDelta
					
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents9EventsRemaining"].Title = "Selection 9 - The smallest pair production angle was less than " + str(This.Parameters["PairProductionAngularLocalityLimit"]) + " degees - Events Remaining"
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents9EventsRemaining"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][9].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents9Delta"].Title = "Selection 9 - The smallest pair production angle was less than " + str(This.Parameters["PairProductionAngularLocalityLimit"]) + " degees - Delta -> p gamma Events Remaining"
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents9Delta"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][9].TruthDelta
					
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents10EventsRemaining"].Title = "Selection 10 - The time separation was less than " + str(This.Parameters["SynchronicityLimit"]) + " ms - Events Remaining"
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents10EventsRemaining"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][10].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents10Delta"].Title = "Selection 10 - The time separation was less than " + str(This.Parameters["SynchronicityLimit"]) + " ms - Delta -> p gamma Events Remaining"
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents10Delta"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][10].TruthDelta"""

					#####
					if not (float(This.ReconstructedStatistics.Statistics["NPIDsWithCRProton"].Quantity + This.ReconstructedStatistics.Statistics["NPIDsWithIRProton"].Quantity) == 0):
						This.ReconstructedStatistics.Statistics["NPIDsWithRProtonRatio"].Quantity = float(This.ReconstructedStatistics.Statistics["NPIDsWithCRProton"].Quantity) / float(This.ReconstructedStatistics.Statistics["NPIDsWithCRProton"].Quantity + This.ReconstructedStatistics.Statistics["NPIDsWithIRProton"].Quantity)
						
					if not (This.TruthStatistics.Statistics["NDeltaToProtonPhoton"].Quantity == 0):
						This.TruthStatistics.Statistics["NDeltaPairProductionProportion"].Quantity = float(This.TruthStatistics.Statistics["NDeltaEventsWithElectronPositronPairs"].Quantity) / float(This.TruthStatistics.Statistics["NDeltaToProtonPhoton"].Quantity)

					OutputDataFileLocator = FileAdministrator.CreateFilePath(DataLocation, ".output", This.SimulationInformation)
					
					OutputDataFile = open(OutputDataFileLocator, "w")

					if (i == EventNumber - 1):
									
						del sys.stdout
						del sys.stderr
												
						print This.TruthStatistics.ToText()
						print This.ReconstructedStatistics.ToText()
						print This.EfficiencyStatistics_Delta1ToProtonPhoton.ToText()
						print This.EfficiencyStatistics_Delta1ToProtonPi0.ToText()
						print This.EfficiencyStatistics_Delta1ToProtonPhotonPP.ToText()
					
						print TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine
						
						OutputDataFile.write(This.TruthStatistics.ToText())
						OutputDataFile.write(This.ReconstructedStatistics.ToText())
						OutputDataFile.write(This.EfficiencyStatistics_Delta1ToProtonPhoton.ToText())
						OutputDataFile.write(This.EfficiencyStatistics_Delta1ToProtonPi0.ToText())
						OutputDataFile.write(This.EfficiencyStatistics_Delta1ToProtonPhotonPP.ToText())
						
					else:
						
						OutputDataFile.write(This.TruthStatistics.ToText())
						OutputDataFile.write(This.ReconstructedStatistics.ToText())
						OutputDataFile.write(This.EfficiencyStatistics_Delta1ToProtonPhoton.ToText())
						OutputDataFile.write(This.EfficiencyStatistics_Delta1ToProtonPi0.ToText())
						OutputDataFile.write(This.EfficiencyStatistics_Delta1ToProtonPhotonPP.ToText())
						
	
	def InitialiseStatistics(This):
	
		This.TruthStatistics = Statistics.Collection("Truth Statistics")
				
		This.TruthStatistics.NewStatistic("NEvents", "Number of Events")
		This.TruthStatistics.NewStatistic("NVertices", "Number of Vertices")
		This.TruthStatistics.NewStatistic("NDeltaToProtonPhoton", "Number of Delta to Proton-Photon Events")
		This.TruthStatistics.NewStatistic("NDeltaToProtonPhotonCC", "Number of Delta to Proton-Photon Charged-Current Events")
		This.TruthStatistics.NewStatistic("NDeltaToProtonPhotonNC", "Number of Delta to Proton-Photon Neutral-Current Events")
		This.TruthStatistics.NewStatistic("NDeltaToProtonPion", "Number of Delta to Proton-Pi0 Events")
		This.TruthStatistics.NewStatistic("NDeltaToProtonPhotonPP", "Number of Delta to Proton-Photon Events Where Electron Positron Pair Production Occurs")
		This.TruthStatistics.NewStatistic("NDeltaToProtonPhotonPC", "Number of Delta to Proton-Photon Events Where a Photon Does Not Interact")
		
		This.TruthStatistics.NewStatistic("NEventsWithElectrons", "Number of events which contain electrons")
		This.TruthStatistics.NewStatistic("NEventsWithPositrons", "Number of events which contain positrons")
		This.TruthStatistics.NewStatistic("NEventsWithMuons", "Number of events which contain muons")
		This.TruthStatistics.NewStatistic("NEventsWithElectronsAndPositrons", "Number of events which contain both electrons and positrons")
		This.TruthStatistics.NewStatistic("NEventsWithElectronsPositronsAndMuons", "Number of events which contain electrons, positrons, and muons")
		This.TruthStatistics.NewStatistic("NEventsWithElectronPositronPairs", "Number of events which contain electron-positron pairs")
		
		This.TruthStatistics.NewStatistic("NDeltaEventsWithElectrons", "Number of events which contain electrons and have a Delta -> p gamma interaction present")
		This.TruthStatistics.NewStatistic("NDeltaEventsWithPositrons", "Number of events which contain positrons and have a Delta -> p gamma interaction present")
		This.TruthStatistics.NewStatistic("NDeltaEventsWithMuons", "Number of events which contain muons and have a Delta -> p gamma interaction present")
		This.TruthStatistics.NewStatistic("NDeltaEventsWithElectronsAndPositrons", "Number of events which contain both electrons and positrons and have a Delta -> p gamma interaction present")
		This.TruthStatistics.NewStatistic("NDeltaEventsWithElectronsPositronsAndMuons", "Number of events which contain electrons, positrons, muons and have a Delta -> p gamma interaction present")
		This.TruthStatistics.NewStatistic("NDeltaEventsWithElectronPositronPairs", "Number of events which contain electron-positron pairs and have a Delta -> p gamma interaction present")
		This.TruthStatistics.NewStatistic("NDeltaPairProductionProportion", "Proportion of Delta -> p gamma events with electron positron pair production present.")
				
				
		This.ReconstructedStatistics = Statistics.Collection("Reconstructed Statistics")
		
		This.ReconstructedStatistics.NewStatistic("NEventsWithRPID", "Number of Events with at least one Reconstructed PID")
		This.ReconstructedStatistics.NewStatistic("NEventsWithRProton", "Number of Events with at least one Reconstructed Proton Track")
		This.ReconstructedStatistics.NewStatistic("NEventsWithCRProton", "Number of Events with at least one Correctly Reconstructed Proton Track")
		This.ReconstructedStatistics.NewStatistic("NEventsWithIRProton", "Number of Events with Incorrectly Reconstructed Proton Tracks")
		This.ReconstructedStatistics.NewStatistic("NEventsWithCRProton18TPC", "Number of Events with at least one Correctly Reconstructed Proton Track with at least 18 TPC Nodes")		
		This.ReconstructedStatistics.NewStatistic("NEventsWithTECC", "Number of Events with at least one Tracker EC Cluster")		
		This.ReconstructedStatistics.NewStatistic("NEventsWithTECCAndCRProton", "Number of Events with at least one Tracker EC Cluster and one Correctly Reconstructed Proton Track")	
		This.ReconstructedStatistics.NewStatistic("NEventsWithTECCAndCRProtonWithin10D", "Number of Events with at least one Tracker EC Cluster and one Correctly Reconstructed Proton Track where the Photon Direction points to within 10 Degrees of the Proton Track Start")	
		This.ReconstructedStatistics.NewStatistic("NEventsWithTECCAndCRProtonWithin10DWithin500ns", "Number of Events with at least one Tracker EC Cluster and one Correctly Reconstructed Proton Track where the Photon Direction points to within 10 Degrees of the Proton Track Start and where the timing is less than 500ns")
		This.ReconstructedStatistics.NewStatistic("NPIDsWithCRProton", "Number of PIDs Correctly Reconstructed as a Proton Track")
		This.ReconstructedStatistics.NewStatistic("NPIDsWithIRProton", "Number of PIDs Incorrectly Reconstructed as a Proton Track")
		This.ReconstructedStatistics.NewStatistic("NPIDsWithRProtonRatio", "Ratio of Correctly Reconstructed Proton Track PIDs")		
		
		This.ReconstructedStatistics.NewStatistic("NEventsWithElectrons", "Number of events which contain electrons")
		This.ReconstructedStatistics.NewStatistic("NEventsWithPositrons", "Number of events which contain positrons")
		This.ReconstructedStatistics.NewStatistic("NEventsWithMuons", "Number of events which contain muons")
		This.ReconstructedStatistics.NewStatistic("NEventsWithElectronsAndPositrons", "Number of events which contain both electrons and positrons")
		This.ReconstructedStatistics.NewStatistic("NEventsWithElectronsPositronsAndMuons", "Number of events which contain electrons, positrons, and muons")
		This.ReconstructedStatistics.NewStatistic("NEventsWithElectronPositronPairs", "Number of events which contain electron-positron pairs")
		
		This.ReconstructedStatistics.NewStatistic("PIDNumber", "Number of PIDs")
		This.ReconstructedStatistics.NewStatistic("NTrueElectronPIDs", "Number of PIDs that are true electrons")
		This.ReconstructedStatistics.NewStatistic("NTruePositronPIDs", "Number of PIDs that are true positrons")
		This.ReconstructedStatistics.NewStatistic("NTrueMuonPIDs", "Number of PIDs that are true muons")
		This.ReconstructedStatistics.NewStatistic("NTrueProtonPIDs", "Number of PIDs that are true Protons")
		This.ReconstructedStatistics.NewStatistic("NReconElectronPIDs", "Number of PIDs that are reconstructed electrons")
		This.ReconstructedStatistics.NewStatistic("NReconPositronPIDs", "Number of PIDs that are reconstructed positrons")
		This.ReconstructedStatistics.NewStatistic("NReconMuonPIDs", "Number of PIDs that are reconstructed muons")
		This.ReconstructedStatistics.NewStatistic("NReconProtonPIDs", "Number of PIDs that are reconstructed Protons")
		
		This.ReconstructedStatistics.NewStatistic("TPCPIDNumber", "Number of TPC Suitable PIDs")
		This.ReconstructedStatistics.NewStatistic("IdentifiedPIDNumber", "Number of Identified PIDs")
		This.ReconstructedStatistics.NewStatistic("NTrueElectronPIDsTPCSatisfied", "Number of TPC Suitable PIDs that are true electrons")
		This.ReconstructedStatistics.NewStatistic("NTruePositronPIDsTPCSatisfied", "Number of TPC Suitable PIDs that are true positrons")
		This.ReconstructedStatistics.NewStatistic("NTrueMuonPIDsTPCSatisfied", "Number of TPC Suitable PIDs that are true muons")
		This.ReconstructedStatistics.NewStatistic("NTrueProtonPIDsTPCSatisfied", "Number of TPC Suitable PIDs that are true Protons")
		
		This.ReconstructedStatistics.NewStatistic("NTrueElectronPIDsReconIdentified", "Number of TPC Suitable PIDs that are true electrons and have been assigned a recon particle ID")
		This.ReconstructedStatistics.NewStatistic("NTruePositronPIDsReconIdentified", "Number of TPC Suitable PIDs that are true positrons and have been assigned a recon particle ID")
		This.ReconstructedStatistics.NewStatistic("NTrueMuonPIDsReconIdentified", "Number of TPC Suitable PIDs that are true muons and have been assigned a recon particle ID")
		This.ReconstructedStatistics.NewStatistic("NTrueProtonPIDsReconIdentified", "Number of TPC Suitable PIDs that are true Protons and have been assigned a recon particle ID")
	
	
		This.EfficiencyStatistics_Delta1ToProtonPhoton = Statistics.Collection("Efficiency Statistics for the Delta 1 to Proton-Photon ECal Channel")
		
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents0EventsRemaining", "Initial Number of Events")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents0Delta", "Initial Number of Delta -> p gamma Events")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents1EventsRemaining", "Selection 1 - At least one reconstructed track was recorded - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents1Delta", "Selection 1 - At least one reconstructed track was recorded -  Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents2EventsRemaining", "Selection 2 - The track has at least 18 TPC nodes - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents2Delta", "Selection 2 - The track has at least 18 TPC nodes -  Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents3EventsRemaining", "Selection 3 - At least one proton-identified track - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents3Delta", "Selection 3 - At least one proton-identified track -  Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents4EventsRemaining", "Selection 4 - Only one proton-identified track - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents4Delta", "Selection 4 - Only one proton-identified track -  Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents5EventsRemaining", "Selection 5 - Proton track is the first track into the detector - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents5Delta", "Selection 5 - Proton track is the first track into the detector - Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents6EventsRemaining", "Selection 6 - Proton track began in the FGDs - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents6Delta", "Selection 6 - Proton track began in the FGDs - Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents7EventsRemaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents7Delta")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents8EventsRemaining", "Selection 8 - No Muon PIDs - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents8Delta", "Selection 8 - No Muon PIDs - Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents9EventsRemaining", "Selection 9 - No Electron PIDs - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents9Delta", "Selection 9 - No Electron PIDs - Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents10EventsRemaining", "Selection 10 - No Positron PIDs - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents10Delta", "Selection 10 - No Positron PIDs - Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents11EventsRemaining", "Selection 11 - At least one ECal cluster - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents11Delta", "Selection 11 - At least one ECal cluster - Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents12EventsRemaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents12Delta")
		
		This.EfficiencyStatistics_Delta1ToProtonPi0 = Statistics.Collection("Efficiency Statistics for the Delta 1 to Proton-Pi-0 channel")

		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents0EventsRemaining", "Initial Number of Events")
		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents0Delta", "Initial Number of Delta -> p pi Events")
		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents1EventsRemaining", "Selection 1 - At least one reconstructed track was recorded - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents1Delta", "Selection 1 - At least one reconstructed track was recorded -  Delta -> p pi Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents2EventsRemaining", "Selection 2 - The track has at least 18 TPC nodes - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents2Delta", "Selection 2 - The track has at least 18 TPC nodes -  Delta -> p pi Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents3EventsRemaining", "Selection 3 - At least one proton-identified track - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents3Delta", "Selection 3 - At least one proton-identified track -  Delta -> p pi Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents4EventsRemaining", "Selection 4 - Only one proton-identified track - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents4Delta", "Selection 4 - Only one proton-identified track -  Delta -> p pi Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents5EventsRemaining", "Selection 5 - Proton track is the first track into the detector - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents5Delta", "Selection 5 - Proton track is the first track into the detector - Delta -> p pi Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents6EventsRemaining", "Selection 6 - Proton track began in the FGDs - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents6Delta", "Selection 6 - Proton track began in the FGDs - Delta -> p pi Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents7EventsRemaining")
		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents7Delta")
		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents8EventsRemaining", "Selection 8 - No Muon PIDs - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents8Delta", "Selection 8 - No Muon PIDs - Delta -> p pi Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents9EventsRemaining", "Selection 9 - No Electron PIDs - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents9Delta", "Selection 9 - No Electron PIDs - Delta -> p pi Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents10EventsRemaining", "Selection 10 - No Positron PIDs - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents10Delta", "Selection 10 - No Positron PIDs - Delta -> p pi Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents11EventsRemaining", "Selection 11 - At least one ECal cluster - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPi0.NewStatistic("NEvents11Delta", "Selection 11 - At least one ECal cluster - Delta -> p pi Events Remaining")
		
		
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP = Statistics.Collection("Efficiency Statistics for the Delta 1 to Proton-Photon Pair Production Channel")

		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents0EventsRemaining", "Initial Number of Events")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents0Delta", "Initial Number of Delta -> p gamma Events")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents1EventsRemaining", "Selection 1 - At least one reconstructed track was recorded - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents1Delta", "Selection 1 - At least one reconstructed track was recorded -  Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents2EventsRemaining", "Selection 2 - The track has at least 18 TPC nodes - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents2Delta", "Selection 2 - The track has at least 18 TPC nodes -  Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents3EventsRemaining", "Selection 3 - At least one proton-identified track - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents3Delta", "Selection 3 - At least one proton-identified track -  Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents4EventsRemaining", "Selection 4 - Only one proton-identified track - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents4Delta", "Selection 4 - Only one proton-identified track -  Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents5EventsRemaining", "Selection 5 - Proton track is the first track into the detector - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents5Delta", "Selection 5 - Proton track is the first track into the detector - Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents6EventsRemaining", "Selection 6 - Proton track began in the FGDs - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents6Delta", "Selection 6 - Proton track began in the FGDs - Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents7EventsRemaining", "Selection 7 - No Muon PIDs - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents7Delta", "Selection 7 - No Muon PIDs - Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents8EventsRemaining", "Selection 8 - Pair Produced electron positron present - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents8Delta", "Selection 8 - Pair Produced electron positron present - Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents9EventsRemaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents9Delta")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents10EventsRemaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents10Delta")
	
	
	def InitialiseHistograms(This):
		
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
		"""
		This.StackedHistograms["FinalInvariantMass"]=StackedHistogram.StackedHistogram("Final_Invariant_Mass", "Invariant Mass of Delta Baryon after all cuts have been applied", 0.7, 0.65, 0.86, 0.88, "Mass (GeV)", "Number", "Cuts/DeltaPGamma/Invariant Mass/")
		This.StackedHistograms["InvariantMassAllECal"]=StackedHistogram.StackedHistogram("Invariant_Mass_All_ECal", "Invariant Mass of Delta Baryon from comparison of single photon to all ECals", 0.7, 0.65, 0.86, 0.88, "Mass (GeV)", "Number", "Cuts/DeltaPGamma/Invariant Mass/All ECal/")
		
		This.StackedHistograms["Pi0MesonMass"] = StackedHistogram.StackedHistogram("Pi0_Meson_Mass", "Invariant Mass of Pi0 Meson from matching of ECal clusters", 0.7, 0.65, 0.86, 0.88, "Mass (GeV)", "Number", "Pi0Meson/Invariant Mass/")
		
		This.StackedHistograms["SingleProtonPIDMultiplicity"]=StackedHistogram.StackedHistogram("Single_Proton_PID_Multiplicity", "PID Multiplicity for events with single proton tracks", 0.7, 0.65, 0.86, 0.88, "Multiplicity", "Number",  "Proton/")
		
		This.StackedHistograms["SingleProtonECalMultiplicity"]=StackedHistogram.StackedHistogram("Single_Proton_ECal_Multiplicity", "ECal Multiplicity for events with single proton tracks", 0.7, 0.65, 0.86, 0.88, "Number", "Number",  "Photon/")	
		
		This.StackedHistograms["ProtonMuonSeparation"]=StackedHistogram.StackedHistogram("Proton_Muon_Separation", "Separation between the single proton and single Muon in suitable events", 0.7, 0.65, 0.86, 0.88, "Separation (cm)", "Number",  "Proton/")	
		
		This.StackedHistograms["ElectronPull"]=StackedHistogram.StackedHistogram("Electron_Pull", "Electron Pull", 0.7, 0.65, 0.86, 0.88, "Pull", "Number",  "PIDs/Recon/Particle Pulls/Electron/")	
		This.StackedHistograms["KaonPull"]=StackedHistogram.StackedHistogram("Kaon_Pull", "Kaon Pull", 0.7, 0.65, 0.86, 0.88, "Pull", "Number",  "PIDs/Recon/Particle Pulls/Kaon/")	
		This.StackedHistograms["MuonPull"]=StackedHistogram.StackedHistogram("Muon_Pull", "Muon Pull", 0.7, 0.65, 0.86, 0.88, "Pull)", "Number",  "PIDs/Recon/Particle Pulls/Muon/")	
		This.StackedHistograms["PionPull"]=StackedHistogram.StackedHistogram("Pion_Pull", "Pion Pull", 0.7, 0.65, 0.86, 0.88, "Pull", "Number",  "PIDs/Recon/Particle Pulls/Pion/")	
		This.StackedHistograms["ProtonPull"]=StackedHistogram.StackedHistogram("Proton_Pull", "Proton Pull", 0.7, 0.65, 0.86, 0.88, "Pull", "Number",  "PIDs/Recon/Particle Pulls/Proton/")	
		"""
		
		# This is transitional code, not the finished thing.


		This.HistogramCollection1.NewStackedHistogram1D("Final_Invariant_Mass", "Cuts/DeltaPGamma/Invariant Mass/", "Invariant Mass of Delta Baryon after all cuts have been applied", "Mass (GeV)", 100, 0, 3000, "Number")
		This.HistogramCollection1.NewStackedHistogram1D("Invariant_Mass_All_ECal", "Cuts/DeltaPGamma/Invariant Mass/All ECal/", "Invariant Mass of Delta Baryon from comparison of single photon to all ECals", "Mass (GeV)", 100, 0, 3000, "Number")
		
		This.HistogramCollection1.NewStackedHistogram1D("Pi0_Meson_Mass", "Pi0Meson/Invariant Mass/", "Invariant Mass of Pi0 Meson from matching of ECal clusters", "Mass (GeV)", 100, 0, 1000, "Number")
		
		This.HistogramCollection1.NewStackedHistogram1D("Single_Proton_PID_Multiplicity", "Proton/", "PID Multiplicity for events with single proton tracks", "Multiplicity", 10, 0, 10, "Number")
		This.HistogramCollection1.NewStackedHistogram1D("Single_Proton_ECal_Multiplicity", "Photon/", "ECal Multiplicity for events with single proton tracks", "Number", 10, 0, 10, "Number")	
		
		This.HistogramCollection1.NewStackedHistogram1D("Proton_Muon_Separation", "Proton/", "Separation between the single proton and single Muon in suitable events", "Separation (cm)", 100, 0, int(This.Parameters["LocalityLimit"] * 5), "Number")	
		
		This.HistogramCollection1.NewStackedHistogram1D("ElectronPull", "PIDs/Recon/Particle Pulls/Electron/", "Electron Pull", "Pull", 100, -100, 100, "Number")	
		This.HistogramCollection1.NewStackedHistogram1D("KaonPull", "PIDs/Recon/Particle Pulls/Kaon/", "Kaon Pull", "Pull", 100, -100, 100, "Number")	
		This.HistogramCollection1.NewStackedHistogram1D("MuonPull", "PIDs/Recon/Particle Pulls/Muon/", "Muon Pull", "Pull", 100, -100, 100, "Number")	
		This.HistogramCollection1.NewStackedHistogram1D("PionPull", "PIDs/Recon/Particle Pulls/Pion/", "Pion Pull", "Pull", 100, -100, 100, "Number")	
		This.HistogramCollection1.NewStackedHistogram1D("ProtonPull", "PIDs/Recon/Particle Pulls/Proton/", "Proton Pull", "Pull", 100, -100, 100, "Number")	
		
	
	def runEvent(This):

		This.TruthStatistics.Statistics["NEvents"].Quantity += 1
	
		NVertices = This.Truth_GRTVertices.NVtx	
		
		########################################
		# TRUTH DATA #
		########################################
		
		TrueDelta1Baryons = []
		
		TrueProtons = []
		TruePi0Mesons = []
		
		TrueElectrons = []
		TrueAntielectrons = []
		TrueElectronAntielectronPairs = []
		DeltaVertexList = []
		
		TrueMuLeptons = []
		
		EventContainsElectrons = False
		EventContainsAntielectrons = False
		EventContainsElectronAntielectronPairs = False
		EventContainsMuLeptons = False
		
		TrueEventContainsDelta1ToProtonPhoton = False
		TrueEventContainsDelta1ToProtonPi0 = False
		
		InteractionType = ""
		
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

					TrueDelta1Baryons.append(GRTParticle1)
				
				if (GRTParticle1.pdg == ParticleCodes.Electron):
					EventContainsElectrons = True
				
				if (GRTParticle1.pdg == ParticleCodes.AntiElectron):
					EventContainsAntielectrons = True
					
				if (GRTParticle1.pdg == ParticleCodes.MuLepton):
					EventContainsMuLeptons = True
																			
			######################################## Search for current and interaction type. This method can look at electron neutrinos and anti muon neutrinos for any possible extension

			This.EventCodeDeconstructor1.ReadCode(GRTVertex1.EvtCode)
			
			TruthCurrent = This.EventCodeDeconstructor1.Elements["Current Code"].Content
			TruthInteractionType = This.EventCodeDeconstructor1.Elements["Process Code"].Content					
							
			###################################### Categorisation of various interesting interactions ############
							
			DeltaPGammaInteraction = (IncidentMuonNeutrino and ProtonFromDelta and PhotonFromDelta and TruthInteractionType == "RP")
			
			Delta1BaryonToProtonPi0MesonInteraction = (IncidentMuonNeutrino and ProtonFromDelta and Pi0MesonFromDelta and TruthInteractionType == "RP")
			
			if (DeltaPGammaInteraction):
				This.TruthStatistics.Statistics["NDeltaToProtonPhoton"].Quantity += 1
				TrueEventContainsDelta1ToProtonPhoton=True
				
				DeltaVertexList.append(GRTVertex1.TruthVertexID)
			
			if (Delta1BaryonToProtonPi0MesonInteraction):
				This.TruthStatistics.Statistics["NDeltaToProtonPion"].Quantity += 1
			
			if (DeltaPGammaInteraction and TruthCurrent == "CC"):
				This.TruthStatistics.Statistics["NDeltaToProtonPhotonCC"].Quantity += 1
				
			if (DeltaPGammaInteraction and TruthCurrent == "NC"):
				This.TruthStatistics.Statistics["NDeltaToProtonPhotonNC"].Quantity += 1

			if (Delta1BaryonToProtonPi0MesonInteraction):
				TrueEventContainsDelta1ToProtonPi0 = True
		
			
		######################### True Pair Production ###############
		
		ElectronParentList = []
		PositronParentList = []
		MuonParentList = []
		
		for Trajectory1 in This.Truth_Trajectories.Trajectories:
			
			if (Trajectory1.PDG == ParticleCodes.Electron):
			
				ElectronParentList.append(Trajectory1.ParentID)#Creates a list of the parent trajectory IDs for all electrons
				
			if(Trajectory1.PDG == ParticleCodes.AntiElectron):
				
				PositronParentList.append(Trajectory1.ParentID)#Creates a list of the parent trajectory IDs for all positrons
				
			if(Trajectory1.PDG == ParticleCodes.MuLepton):
				
				MuonParentList.append(Trajectory1.ParentID)#Creates a list of the parent trajectory IDs for all muons
		
		if (TrueEventContainsDelta1ToProtonPhoton):#This is mainly to prevent the large number of for loops initiating for every event
			
			DeltaToPhotonTrajectoryIDs = []
		
			for Vertex1 in This.Truth_Vertices.Vertices: #Then Loop over all vertices
				
				for DeltaVertexID in DeltaVertexList:#Looping over Delta Baryon vertex IDs
					
					if(Vertex1.ID == DeltaVertexID):#Selects the Delta Baryon vertices
				
				
				
						for Trajectory1 in This.Truth_Trajectories.Trajectories:#First loop over all trajectories in an event
				
							for TrajectoryID in Vertex1.PrimaryTrajIDs:#Each Delta Baryon Vertex has a list of daughter trajectories --- Are these daughter trajectories the "final state particles" of GRT vertices?
												
								if (Trajectory1.ID == TrajectoryID):#Selects the trajectories that are part of Delta Baryon daughter trajectories
								
									if (Trajectory1.PDG == ParticleCodes.Photon):
										
										DeltaToPhotonTrajectoryIDs.append(Trajectory1.ID)
			
			for ElectronParent in ElectronParentList:
				
				for PositronParent in PositronParentList:
					
					if (ElectronParent == PositronParent):#Finds Electron Positron pairs
						
						for DeltaPhotonTrajectoryID in DeltaToPhotonTrajectoryIDs:
							
							if (DeltaPhotonTrajectoryID == ElectronParent):#Finds if the electron positron pairs are from a 
														
								EventContainsElectronAntielectronPairs = True
								
			#########################
			
			if (len(ElectronParentList) > 0):				
				This.TruthStatistics.Statistics["NDeltaEventsWithElectrons"].Quantity += 1
				
			if (len(PositronParentList) > 0):				
				This.TruthStatistics.Statistics["NDeltaEventsWithPositrons"].Quantity += 1
				
			if ((len(ElectronParentList) > 0) and (len(PositronParentList) > 0)):				
				This.TruthStatistics.Statistics["NDeltaEventsWithElectronsAndPositrons"].Quantity += 1
				
			if (EventContainsElectronAntielectronPairs == True):	
				This.TruthStatistics.Statistics["NDeltaEventsWithElectronPositronPairs"].Quantity += 1
				
			if (len(MuonParentList) > 0):				
				This.TruthStatistics.Statistics["NDeltaEventsWithMuons"].Quantity += 1
				
			if ((len(ElectronParentList) > 0) and (len(PositronParentList) > 0) and (len(MuonParentList) > 0)):				
				This.TruthStatistics.Statistics["NDeltaEventsWithElectronsPositronsAndMuons"].Quantity += 1

		if (len(ElectronParentList) > 0):				
			This.TruthStatistics.Statistics["NEventsWithElectrons"].Quantity += 1
			
		if (len(PositronParentList) > 0):				
			This.TruthStatistics.Statistics["NEventsWithPositrons"].Quantity += 1
			
		if ((len(ElectronParentList) > 0) and (len(PositronParentList) > 0)):				
			This.TruthStatistics.Statistics["NEventsWithElectronsAndPositrons"].Quantity += 1
			
		if (EventContainsElectronAntielectronPairs == True):	
			This.TruthStatistics.Statistics["NEventsWithElectronPositronPairs"].Quantity += 1
			
		if (len(MuonParentList) > 0):				
			This.TruthStatistics.Statistics["NEventsWithMuons"].Quantity += 1
			
		if ((len(ElectronParentList) > 0) and (len(PositronParentList) > 0) and (len(MuonParentList) > 0)):				
			This.TruthStatistics.Statistics["NEventsWithElectronsPositronsAndMuons"].Quantity += 1

		####################################################################################################
		# RECONSTRUCTED DATA #
		####################################################################################################

		NPIDs = This.Reconstructed_Global.NPIDs#Number of reconstructed PIDs

		if (NPIDs > 0):
			
			This.ReconstructedStatistics.Statistics["NEventsWithRPID"].Quantity += 1

					
		ReconstructedObjects1 = []
		ReconstructedObjects2 = []
		
		ReconstructedProtons1 = []
		ReconstructedPhotons1 = []
		ReconstructedPi0Mesons1 = []
		ReconstructedElectrons1 = []
		ReconstructedAntiElectrons1 = []		
		ReconstructedMuLeptons1 = []
		
		PIDNumber = 0
		TPCValidPIDNumber = 0
		
		TrackMultiplicity = 0
		ChargedTrackMultiplicity = 0
		
		TorrentMultiplicity = 0
		ChargedTorrentMultiplicity = 0
		
		NumberOfReconstructedProtonTracks = 0
		NumberOfReconstructedMuLeptonTracks = 0
		NumberOfReconstructedElectronTracks = 0
		NumberOfReconstructedAntiElectronTracks = 0
		
		NumberOfProtonsAndPhotonsWithinAngle = 0
		NumberOfProtonsAndPhotonsWithinSynchronicity = 0
				
		ProtonIsCorrectlyReconstructed = False
		ProtonIsIncorrectlyReconstructed = False
		
		NumberOfCorrectlyReconstructedProtons = 0
		NumberOfIncorrectlyReconstructedProtons = 0
		
		MuonTrackIsHighestEnergy = False
		
		SingleProtonTrackFirst = False
		SingleProtonInFGDFiducial = False
		ProtonSelected = False
		
		EventContainsElectron = False
		EventContainsPositron = False
		EventContainsMuon = False
				
		####################################################################################################
		# TPC and FGD Track Objects #
		####################################################################################################
		
		for PID in This.Reconstructed_Global.PIDs: # Loop over the PIDs if they exist
			
			This.ReconstructedStatistics.Statistics["PIDNumber"].Quantity += 1
			PIDNumber += 1
								
			NumberOfTPCPoints = 0
			SuitableTPCNodeNumber = False
										
			for TPCTrack1 in PID.TPC: # Loop over TPC PIDs						
				if (TPCTrack1.NNodes > 18):
					NumberOfTPCPoints += TPCTrack1.NNodes#This was: NumberOfTPCPoints += TPCTrack1.NNodes but didn't seem to make sense
					SuitableTPCNodeNumber = True	

			ReconstructedObject1 = Particles.ReconstructedObject()
			
			ReconstructedObject1.Identification = PID.UniqueID
			
			ReconstructedObject1.ReconFrontMomentum = PID.FrontMomentum
				
			ReconstructedObject1.ReconFrontDirectionX = PID.FrontDirection.X()
			ReconstructedObject1.ReconFrontDirectionY = PID.FrontDirection.Y()
			ReconstructedObject1.ReconFrontDirectionZ = PID.FrontDirection.Z()
			
			ReconstructedObject1.FrontPosition.T = PID.FrontPosition.T()	
			ReconstructedObject1.FrontPosition.X = PID.FrontPosition.X()
			ReconstructedObject1.FrontPosition.Y = PID.FrontPosition.Y()
			ReconstructedObject1.FrontPosition.Z = PID.FrontPosition.Z()
			
			ReconstructedObject1.Charge = PID.Charge
			
			ReconstructedObject1.NumberOfTPCPoints = NumberOfTPCPoints
			ReconstructedObject1.GoodNumberOfTPCPoints = SuitableTPCNodeNumber
			
			ReconstructedObject1.Detectors = str(PID.Detectors)	
			
			for TrueTrajectory in This.Truth_Trajectories.Trajectories:#Loop over the truth trajectories for comparison
				if (TrueTrajectory.ID == PID.TrueParticle.ID):
					if (TrueTrajectory.PDG == ParticleCodes.Electron):
						This.ReconstructedStatistics.Statistics["NTrueElectronPIDs"].Quantity += 1
						
					if (TrueTrajectory.PDG == ParticleCodes.AntiElectron):
						This.ReconstructedStatistics.Statistics["NTruePositronPIDs"].Quantity += 1
						
					if (TrueTrajectory.PDG == ParticleCodes.MuLepton):
						This.ReconstructedStatistics.Statistics["NTrueMuonPIDs"].Quantity += 1
					
					if (TrueTrajectory.PDG == ParticleCodes.Proton):
						This.ReconstructedStatistics.Statistics["NTrueProtonPIDs"].Quantity += 1	
						
				
			if (SuitableTPCNodeNumber):
				
				This.ReconstructedStatistics.Statistics["TPCPIDNumber"].Quantity += 1
				TPCValidPIDNumber+=1	

				(ReconstructedObject1.TrueVertex, ReconstructedObject1.TrueTrajectory) = PIDTruth(This.Truth_GRTVertices.Vtx, This.Truth_Trajectories.Trajectories, PID)

				######### For particle pulls - There are possibly multiple TPCs with different pulls for track, so this code looks for the TPC with the most nodes
						
				NodeNumber = 0
						
				for i, TPCTrack1 in enumerate(PID.TPC):
					if (TPCTrack1.NNodes > NodeNumber):
						
						NodeNumber = TPCTrack1.NNodes#!! Correction here, this loop was not working
						BestTPCTrack = i
					
				for j , TPCTrack1 in enumerate(PID.TPC):
					if (j == i):
						ReconstructedObject1.ParticlePull[ParticleCodes.Electron] = TPCTrack1.PullEle
						ReconstructedObject1.ParticlePull[ParticleCodes.K1Meson] = TPCTrack1.PullKaon
						ReconstructedObject1.ParticlePull[ParticleCodes.MuLepton] = TPCTrack1.PullMuon
						ReconstructedObject1.ParticlePull[ParticleCodes.Pi1Meson] = TPCTrack1.PullPion
						ReconstructedObject1.ParticlePull[ParticleCodes.Proton] = TPCTrack1.PullProton
				
				for ECalTrack in PID.ECAL:
					ReconstructedObject1.ECalEnergyList.append(ECalTrack.EMEnergy)#A list of the energies of this ECal in the PID (normally should only be one)
				
				LowestPull=100

				for Particle , ParticlePull in ReconstructedObject1.ParticlePull.iteritems():
					
					if (math.fabs(ParticlePull) < math.fabs(LowestPull) and math.fabs(ParticlePull) < math.fabs(This.Parameters["PullLimits"][Particle])):
						
						LowestPull = math.fabs(ParticlePull)
						
						ReconstructedObject1.ReconParticleID = Particle

				if (ReconstructedObject1.ReconParticleID != -1):
					This.ReconstructedStatistics.Statistics["IdentifiedPIDNumber"].Quantity += 1

				for TrueTrajectory in This.Truth_Trajectories.Trajectories:#Loop over the truth trajectories for comparison
					if (TrueTrajectory.ID == PID.TrueParticle.ID):
																	
						ReconstructedObject1.TrueParticleID = TrueTrajectory.PDG
								
						ReconstructedObject1.TrueEnergy = TrueTrajectory.InitMomentum.E()
								
						ReconstructedObject1.TrueFrontMomentum = math.sqrt(TrueTrajectory.InitMomentum.X() * TrueTrajectory.InitMomentum.X()+TrueTrajectory.InitMomentum.Y() * TrueTrajectory.InitMomentum.Y()+TrueTrajectory.InitMomentum.Z() * TrueTrajectory.InitMomentum.Z())
						
						if (TrueTrajectory.PDG == ParticleCodes.Electron):
							This.ReconstructedStatistics.Statistics["NTrueElectronPIDsTPCSatisfied"].Quantity += 1
							
							if (ReconstructedObject1.ReconParticleID != -1):
								This.ReconstructedStatistics.Statistics["NTrueElectronPIDsReconIdentified"].Quantity += 1
							
						if (TrueTrajectory.PDG == ParticleCodes.AntiElectron):
							This.ReconstructedStatistics.Statistics["NTruePositronPIDsTPCSatisfied"].Quantity += 1
							
							if (ReconstructedObject1.ReconParticleID != -1):
								This.ReconstructedStatistics.Statistics["NTruePositronPIDsReconIdentified"].Quantity += 1
							
						if (TrueTrajectory.PDG == ParticleCodes.MuLepton):
							This.ReconstructedStatistics.Statistics["NTrueMuonPIDsTPCSatisfied"].Quantity += 1
							
							if (ReconstructedObject1.ReconParticleID != -1):
								This.ReconstructedStatistics.Statistics["NTrueMuonPIDsReconIdentified"].Quantity += 1
						
						if (TrueTrajectory.PDG == ParticleCodes.Proton):
							This.ReconstructedStatistics.Statistics["NTrueProtonPIDsTPCSatisfied"].Quantity += 1
							
							if (ReconstructedObject1.ReconParticleID != -1):
								This.ReconstructedStatistics.Statistics["NTrueProtonPIDsReconIdentified"].Quantity += 1

				if (ReconstructedObject1.ReconParticleID == ParticleCodes.Electron and ReconstructedObject1.Charge == -1):
					This.ReconstructedStatistics.Statistics["NReconElectronPIDs"].Quantity += 1
					EventContainsElectron = True
				
				if (ReconstructedObject1.ReconParticleID == ParticleCodes.Electron and ReconstructedObject1.Charge == 1):
					This.ReconstructedStatistics.Statistics["NReconPositronPIDs"].Quantity += 1
					EventContainsPositron = True
							
				if (ReconstructedObject1.ReconParticleID == ParticleCodes.MuLepton):
					This.ReconstructedStatistics.Statistics["NReconMuonPIDs"].Quantity += 1
					EventContainsMuon = True		
							
				if (ReconstructedObject1.ReconParticleID == ParticleCodes.Proton):
					This.ReconstructedStatistics.Statistics["NReconProtonPIDs"].Quantity += 1							
				
				ReconstructedObject1.TrueParticle = PID.TrueParticle
				
				#This.HistogramCollection1.Histograms["ElectronPull"].Populate(ReconstructedObject1.TrueParticleID, ReconstructedObject1.ParticlePull[ParticleCodes.Electron], str(ParticleCodes.ParticleDictionary[ReconstructedObject1.TrueParticleID]))
				#This.HistogramCollection1.Histograms["KaonPull"].Populate(ReconstructedObject1.TrueParticleID, ReconstructedObject1.ParticlePull[ParticleCodes.K1Meson], str(ParticleCodes.ParticleDictionary[ReconstructedObject1.TrueParticleID]))
				#This.HistogramCollection1.Histograms["MuonPull"].Populate(ReconstructedObject1.TrueParticleID, ReconstructedObject1.ParticlePull[ParticleCodes.MuLepton], str(ParticleCodes.ParticleDictionary[ReconstructedObject1.TrueParticleID]))
				#This.HistogramCollection1.Histograms["PionPull"].Populate(ReconstructedObject1.TrueParticleID, ReconstructedObject1.ParticlePull[ParticleCodes.Pi1Meson], str(ParticleCodes.ParticleDictionary[ReconstructedObject1.TrueParticleID]))
				#This.HistogramCollection1.Histograms["ProtonPull"].Populate(ReconstructedObject1.TrueParticleID, ReconstructedObject1.ParticlePull[ParticleCodes.Proton], str(ParticleCodes.ParticleDictionary[ReconstructedObject1.TrueParticleID]))
				"""
				This.StackedHistograms["ElectronPull"].ConstituentFill1D(ParticleCodes.ParticleDictionary, ReconstructedObject1.TrueParticleID, ReconstructedObject1.ParticlePull[ParticleCodes.Electron],"Electron Pull contribution from a true", "Pull", "Number", 100, -100, 100, "PullElectron")
				This.StackedHistograms["KaonPull"].ConstituentFill1D(ParticleCodes.ParticleDictionary, ReconstructedObject1.TrueParticleID, ReconstructedObject1.ParticlePull[ParticleCodes.K1Meson],"Kaon Pull contribution from a true", "Pull", "Number", 100, -100, 100, "PullKaon")
				This.StackedHistograms["MuonPull"].ConstituentFill1D(ParticleCodes.ParticleDictionary, ReconstructedObject1.TrueParticleID, ReconstructedObject1.ParticlePull[ParticleCodes.MuLepton],"Muon Pull contribution from a true", "Pull", "Number", 100, -100, 100, "PullMuon")
				This.StackedHistograms["PionPull"].ConstituentFill1D(ParticleCodes.ParticleDictionary, ReconstructedObject1.TrueParticleID, ReconstructedObject1.ParticlePull[ParticleCodes.Pi1Meson],"Pion Pull contribution from a true", "Pull", "Number", 100, -100, 100, "PullPion")
				This.StackedHistograms["ProtonPull"].ConstituentFill1D(ParticleCodes.ParticleDictionary, ReconstructedObject1.TrueParticleID, ReconstructedObject1.ParticlePull[ParticleCodes.Proton],"Proton Pull contribution from a true", "Pull", "Number", 100, -100, 100, "PullProton")
				"""
				ReconstructedObjects1.append(ReconstructedObject1)
				ReconstructedObjects2.append(ReconstructedObject1)
				
			else:
				
				ReconstructedObjects2.append(ReconstructedObject1)

		if (EventContainsElectron == True):
			This.ReconstructedStatistics.Statistics["NEventsWithElectrons"].Quantity += 1
			
		if (EventContainsPositron == True):
			This.ReconstructedStatistics.Statistics["NEventsWithPositrons"].Quantity += 1
		
		if ((EventContainsElectron == True) and (EventContainsPositron == True)):
			This.ReconstructedStatistics.Statistics["NEventsWithElectronsAndPositrons"].Quantity += 1
		
		if (EventContainsMuon == True):
			This.ReconstructedStatistics.Statistics["NEventsWithMuons"].Quantity += 1
		
		if ((EventContainsElectron == True) and (EventContainsPositron == True) and (EventContainsMuon == True)):
			This.ReconstructedStatistics.Statistics["NEventsWithElectronsPositronsAndMuons"].Quantity += 1
					
		for ReconstructedObject1 in ReconstructedObjects1:

			TrackMultiplicity += 1

			if (ReconstructedObject1.Charge != 0):
				ChargedTrackMultiplicity += 1

			This.ROOTFile1.HistogramDictionary["PID_Electron_Pull"].Histogram.Fill(ReconstructedObject1.ParticlePull[ParticleCodes.Electron])
			This.ROOTFile1.HistogramDictionary["PID_Kaon_Pull"].Histogram.Fill(ReconstructedObject1.ParticlePull[ParticleCodes.K1Meson])
			This.ROOTFile1.HistogramDictionary["PID_Muon_Pull"].Histogram.Fill(ReconstructedObject1.ParticlePull[ParticleCodes.MuLepton])
			This.ROOTFile1.HistogramDictionary["PID_Pion_Pull"].Histogram.Fill(ReconstructedObject1.ParticlePull[ParticleCodes.Pi1Meson])
			This.ROOTFile1.HistogramDictionary["PID_Proton_Pull"].Histogram.Fill(ReconstructedObject1.ParticlePull[ParticleCodes.Proton])
			
			This.ROOTFile1.HistogramDictionary["PID_Proton_Against_Muon_Pull"].Histogram.Fill(ReconstructedObject1.ParticlePull[ParticleCodes.Proton],ReconstructedObject1.ParticlePull[ParticleCodes.MuLepton])
									
			ReconstructedObject1.FrontEnergyMomentum.T = ReconstructedObject1.ReconstructedParticleEnergy()
			ReconstructedObject1.FrontEnergyMomentum.X = ReconstructedObject1.ReconFrontMomentum * ReconstructedObject1.ReconFrontDirectionX
			ReconstructedObject1.FrontEnergyMomentum.Y = ReconstructedObject1.ReconFrontMomentum * ReconstructedObject1.ReconFrontDirectionY
			ReconstructedObject1.FrontEnergyMomentum.Z = ReconstructedObject1.ReconFrontMomentum * ReconstructedObject1.ReconFrontDirectionZ

			if (ReconstructedObject1.ReconParticleID == ParticleCodes.Proton):#Looking for reconstructed proton track
				
				NumberOfReconstructedProtonTracks += 1
									
				Proton1 = Particles.ReconstructedParticle()
		
				Proton1.Identification = ReconstructedObject1.Identification
		
				Proton1.EnergyMomentum.T = ReconstructedObject1.ReconstructedParticleEnergy()
				Proton1.EnergyMomentum.X = ReconstructedObject1.ReconFrontMomentum * ReconstructedObject1.ReconFrontDirectionX
				Proton1.EnergyMomentum.Y = ReconstructedObject1.ReconFrontMomentum * ReconstructedObject1.ReconFrontDirectionY
				Proton1.EnergyMomentum.Z = ReconstructedObject1.ReconFrontMomentum * ReconstructedObject1.ReconFrontDirectionZ
									
				This.ROOTFile1.HistogramDictionary["Recon_Truth_Proton_Momentum"].Histogram.Fill(ReconstructedObject1.ReconTrueMomentumDifference())	
				This.ROOTFile1.HistogramDictionary["Truth_Proton_Momentum"].Histogram.Fill(ReconstructedObject1.TrueFrontMomentum)
					
				Proton1.Position.T = ReconstructedObject1.FrontPosition.T
				Proton1.Position.X = ReconstructedObject1.FrontPosition.X
				Proton1.Position.Y = ReconstructedObject1.FrontPosition.Y
				Proton1.Position.Z = ReconstructedObject1.FrontPosition.Z
				
				Proton1.TrueTrajectory = ReconstructedObject1.TrueTrajectory
				Proton1.TrueVertex = ReconstructedObject1.TrueVertex					
				
				Proton1.GetProcess(This.RTTools)
				
				ReconstructedProtons1.append(Proton1)
				
				This.ROOTFile1.HistogramDictionary["Proton_PID_Electron_Pull"].Histogram.Fill(ReconstructedObject1.ParticlePull[ParticleCodes.Electron])
				This.ROOTFile1.HistogramDictionary["Proton_PID_Kaon_Pull"].Histogram.Fill(ReconstructedObject1.ParticlePull[ParticleCodes.K1Meson])
				This.ROOTFile1.HistogramDictionary["Proton_PID_Muon_Pull"].Histogram.Fill(ReconstructedObject1.ParticlePull[ParticleCodes.MuLepton])
				This.ROOTFile1.HistogramDictionary["Proton_PID_Pion_Pull"].Histogram.Fill(ReconstructedObject1.ParticlePull[ParticleCodes.Pi1Meson])
				This.ROOTFile1.HistogramDictionary["Proton_PID_Proton_Pull"].Histogram.Fill(ReconstructedObject1.ParticlePull[ParticleCodes.Proton])
				
				This.ROOTFile1.HistogramDictionary["Proton_PID_Proton_Against_Muon_Pull"].Histogram.Fill(ReconstructedObject1.ParticlePull[ParticleCodes.Proton],ReconstructedObject1.ParticlePull[ParticleCodes.MuLepton])
				
			############### Non-proton reconstructions ###########
			
			if (ReconstructedObject1.ReconParticleID == ParticleCodes.MuLepton):
				NumberOfReconstructedMuLeptonTracks += 1
									
				Muon1 = Particles.ReconstructedParticle()
		
				Muon1.Identification = ReconstructedObject1.Identification
		
				Muon1.EnergyMomentum.T = ReconstructedObject1.ReconstructedParticleEnergy()
				Muon1.EnergyMomentum.X = ReconstructedObject1.ReconFrontMomentum * ReconstructedObject1.ReconFrontDirectionX
				Muon1.EnergyMomentum.Y = ReconstructedObject1.ReconFrontMomentum * ReconstructedObject1.ReconFrontDirectionY
				Muon1.EnergyMomentum.Z = ReconstructedObject1.ReconFrontMomentum * ReconstructedObject1.ReconFrontDirectionZ
					
				Muon1.Position.T = ReconstructedObject1.FrontPosition.T
				Muon1.Position.X = ReconstructedObject1.FrontPosition.X
				Muon1.Position.Y = ReconstructedObject1.FrontPosition.Y
				Muon1.Position.Z = ReconstructedObject1.FrontPosition.Z
				
				Muon1.TrueTrajectory = ReconstructedObject1.TrueTrajectory
				Muon1.TrueVertex = ReconstructedObject1.TrueVertex					
				
				Muon1.GetProcess(This.RTTools)
				
				ReconstructedMuLeptons1.append(Muon1)
				
			if (ReconstructedObject1.ReconParticleID == ParticleCodes.Electron):
				NumberOfReconstructedElectronTracks += 1
				
			if (ReconstructedObject1.ReconParticleID == ParticleCodes.AntiElectron):
				NumberOfReconstructedAntiElectronTracks += 1
				
			############## Incorrect reconstructions #############
				
			if (ReconstructedObject1.CorrectlyReconstructed() and ReconstructedObject1.ReconParticleID == ParticleCodes.Proton):
				NumberOfCorrectlyReconstructedProtons += 1
				
				This.ReconstructedStatistics.Statistics["NPIDsWithCRProton"].Quantity += 1
				
			elif (ReconstructedObject1.ReconParticleID == ParticleCodes.Proton):
				NumberOfIncorrectlyReconstructedProtons += 1
				This.ReconstructedStatistics.Statistics["NPIDsWithIRProton"].Quantity += 1
	
			if (ReconstructedObject1.ReconParticleID == ParticleCodes.Proton):

				This.StackedHistograms["ReconProtonTrueEnergy"].ConstituentFill1D(ParticleCodes.ParticleDictionary, ReconstructedObject1.TrueParticleID, ReconstructedObject1.TrueEnergy,"The Proton-Like Track reconstructed front momentum contribution from a true", "Energy (GeV)", "Number", 100, 0, 5000, "ProtonLikeTrueEnergy")
				This.StackedHistograms["ReconProtonReconMomentum"].ConstituentFill1D(ParticleCodes.ParticleDictionary, ReconstructedObject1.TrueParticleID, ReconstructedObject1.ReconFrontMomentum,"The Proton-Like Track true energy contribution from a true", "Momentum (GeV)", "Number", 100, 0, 3000, "ProtonLikeReconFrontMomentum")

		
		#This.EventContainsElectronPositron(ReconstructedObjects1, ReconstructedProtons1)
		
		Protons_HighestEnergy = 0
		MuLeptons_HighestEnergy = 0
		
		for Proton1 in ReconstructedProtons1:			
			if (Proton1.EnergyMomentum.T > Protons_HighestEnergy):
				Protons_HighestEnergy = Proton1.EnergyMomentum.T
				
		for MuLepton1 in ReconstructedMuLeptons1:			
			if (MuLepton1.EnergyMomentum.T > MuLeptons_HighestEnergy):
				MuLeptons_HighestEnergy = MuLepton1.EnergyMomentum.T
		
		if (MuLeptons_HighestEnergy > Protons_HighestEnergy):
			MuonTrackIsHighestEnergy = True			
		
		
		if (NumberOfReconstructedProtonTracks == 1):
			
			SelectedProton = ReconstructedProtons1[0]
			
			ProtonSelected = True
			
			for ReconstructedObject1 in ReconstructedObjects1:
				
				if (ReconstructedObject1.ReconParticleID == ParticleCodes.Proton):#Looking for reconstructed proton track
			
					ProtonTrackFrontPositionZ = ReconstructedObject1.FrontPosition.Z

					X1 = ReconstructedObject1.FrontPosition.X
					Y1 = ReconstructedObject1.FrontPosition.Y
					Z1 = ReconstructedObject1.FrontPosition.Z

					if ((This.FGD1Fiducial.Contains(X1, Y1, Z1) == True) or (This.FGD2Fiducial.Contains(X1, Y1, Z1) == True)):
						SingleProtonInFGDFiducial = True
	
					
					This.ROOTFile1.HistogramDictionary["Single_Proton_PID_Electron_Pull"].Histogram.Fill(ReconstructedObject1.ParticlePull[ParticleCodes.Electron])
					This.ROOTFile1.HistogramDictionary["Single_Proton_PID_Kaon_Pull"].Histogram.Fill(ReconstructedObject1.ParticlePull[ParticleCodes.K1Meson])
					This.ROOTFile1.HistogramDictionary["Single_Proton_PID_Muon_Pull"].Histogram.Fill(ReconstructedObject1.ParticlePull[ParticleCodes.MuLepton])
					This.ROOTFile1.HistogramDictionary["Single_Proton_PID_Pion_Pull"].Histogram.Fill(ReconstructedObject1.ParticlePull[ParticleCodes.Pi1Meson])
					This.ROOTFile1.HistogramDictionary["Single_Proton_PID_Proton_Pull"].Histogram.Fill(ReconstructedObject1.ParticlePull[ParticleCodes.Proton])
					
					This.ROOTFile1.HistogramDictionary["Single_Proton_PID_Proton_Against_Muon_Pull"].Histogram.Fill(ReconstructedObject1.ParticlePull[ParticleCodes.Proton], ReconstructedObject1.ParticlePull[ParticleCodes.MuLepton])
					
			SingleProtonTrackFirst = True
					
			for ReconstructedObject1 in ReconstructedObjects1:
				
				if (ReconstructedObject1.FrontPosition.Z < ProtonTrackFrontPositionZ):
					
					SingleProtonTrackFirst = False
							
		if (NumberOfCorrectlyReconstructedProtons > 0):
			ProtonIsCorrectlyReconstructed = True
			
		if (NumberOfIncorrectlyReconstructedProtons > 0):
			ProtonIsIncorrectlyReconstructed = True
			
		if (NumberOfReconstructedProtonTracks > 0):
			ReconstructedProtonTrack = True
		else:
			ReconstructedProtonTrack = False
						
		####################################################################################################
		# EC Torrent Objects #
		####################################################################################################
				
		#I think we will only look at the Tracker ECal (TPC+FGD) as the POD ECal is mainly used for POD !! What about downstream ECal
						
		SmallestAngle = 180
		
		for TECObject in This.Reconstructed_TEC.ReconObject:#Loop over these reconstructed objects

			TorrentMultiplicity += 1
			
			ECEnergy = TECObject.EMEnergyFit_Result#The energy of photon
			
			Photon1 = Particles.ReconstructedParticle()
			
			Photon1.EnergyMomentum.T = ECEnergy
			
			ECalPID = False
			
			for ReconstructedObject1 in ReconstructedObjects2:
				for ECalEnergy in ReconstructedObject1.ECalEnergyList:
				
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
					
					for Proton1 in ReconstructedProtons1:

						Angle1 = AngleBetweenDirections(Proton1.Position, Photon1.Position, ECUnitDirection)

						This.StackedHistograms["PhotonAnglesStackedShower"].ConstituentFill1D(This.Processes, Proton1.Process, Angle1, "Angle for constituent", "Mass (GeV)", "Number", 100, 0, 180, "PhotonAngleShower")
					
					if (len(ReconstructedProtons1) == 1):
						
						Proton1 = ReconstructedProtons1[0]
						
						Angle1 = AngleBetweenDirections(Proton1.Position, Photon1.Position, ECUnitDirection)

						if (math.fabs(Angle1) < math.fabs(SmallestAngle)):
							
							SmallestAngle = Angle1
						
						This.StackedHistograms["SelectedPhotonAnglesStackedShower"].ConstituentFill1D(This.Processes, Proton1.Process, SmallestAngle, "Angle for constituent", "Mass (GeV)", "Number", 100, 0, 180, "SelectedPhotonAngleShower")
					
				SmallestAngle = 180
					
				if (TECObject.IsTrackLike):
					ECUnitDirection = Geometry.ThreeVector(TECObject.Track.Direction.X(), TECObject.Track.Direction.Y(), TECObject.Track.Direction.Z())
							
					Photon1.Position.T = TECObject.Track.Position.T()
					Photon1.Position.X = TECObject.Track.Position.X()
					Photon1.Position.Y = TECObject.Track.Position.Y()
					Photon1.Position.Z = TECObject.Track.Position.Z()
					
					Photon1.DirectionType = "TrackLike"
					
					for Proton1 in ReconstructedProtons1:
						
						Angle1 = AngleBetweenDirections(Proton1.Position, Photon1.Position, ECUnitDirection)	

						This.StackedHistograms["PhotonAnglesStackedTrack"].ConstituentFill1D(This.Processes, Proton1.Process, Angle1, "Angle for constituent", "Mass (GeV)", "Number", 100, 0, 180, "PhotonAngleShowerTrack")
						
					if (len(ReconstructedProtons1) == 1):
												
						Proton1 = ReconstructedProtons1[0]
						
						Angle1 = AngleBetweenDirections(Proton1.Position, Photon1.Position, ECUnitDirection)	
						
						if (math.fabs(Angle1) < math.fabs(SmallestAngle)):
							
							SmallestAngle = Angle1
						
						This.StackedHistograms["SelectedPhotonAnglesStackedTrack"].ConstituentFill1D(This.Processes, Proton1.Process, SmallestAngle, "Angle for constituent", "Mass (GeV)", "Number", 100, 0, 180, "SelectedPhotonAngleTrack")
					
				#For some reason there sometimes are occurences where the magnitude is far above 1. This if filters them out. We should probably look into this further
				#This thing has the potential to mess up later if you are looping over NTrackerECalRecon!!!!
				Photon1.EnergyMomentum.X = ECUnitDirection.X * ECEnergy / ECUnitDirection.Modulus()#Solution: Renormalisation
				Photon1.EnergyMomentum.Y = ECUnitDirection.Y * ECEnergy / ECUnitDirection.Modulus()
				Photon1.EnergyMomentum.Z = ECUnitDirection.Z * ECEnergy / ECUnitDirection.Modulus()
											
				Photon1.Direction.X = ECUnitDirection.X
				Photon1.Direction.Y = ECUnitDirection.Y
				Photon1.Direction.Z = ECUnitDirection.Z
				
				ReconstructedPhotons1.append(Photon1)
				
		NTrackerECalRecon = len(ReconstructedPhotons1)#Number of reconstructed objects in the ECal	!!This is a temporary fix to look at the Modulus problem	

		####################################################################################################
		# Multiplicity Histograms for the Different Interactions #
		####################################################################################################
		
		#This.HistogramCollection1.Histograms["TrackMultiplicity"].Populate(TruthInteractionType, TrackMultiplicity)
		#This.HistogramCollection1.Histograms["TorrentMultiplicity"].Populate(TruthInteractionType, TorrentMultiplicity)

		#################### Toms new photon cut section ####### Currently we have many potential photons and a single proton.
		# First, the photon with the "best" angle (smallest) is chosen as the single photon ... then we can look at invariant mass
		
		SmallestAngle = 180
		DeltaBaryonMass = 0
		
		for ReconstructedProton1 in ReconstructedProtons1:
			
			for ReconstructedPhoton1 in ReconstructedPhotons1:
			
				Angle1 = AngleBetweenDirections(ReconstructedProton1.Position, ReconstructedPhoton1.Position, ReconstructedPhoton1.Direction)
				
				TimeSeparation = math.fabs(float(ReconstructedProton1.Position.T) - float(ReconstructedPhoton1.Position.T))
				
				if (TimeSeparation < This.Parameters["SynchronicityLimit"]):
					
					NumberOfProtonsAndPhotonsWithinSynchronicity += 1
					
				if (math.fabs(Angle1) < math.fabs(SmallestAngle)):
						
					NumberOfProtonsAndPhotonsWithinAngle += 1
		
		"""if (NumberOfReconstructedProtonTracks == 1):
			
			PhotonAndProtonAreSelected = False
			
			for Photon1 in ReconstructedPhotons1:
						
				Angle1 = AngleBetweenDirections(Proton1.Position, Photon1.Position, Photon1.Direction)	

				TimeSeparation = math.fabs(float(Proton1.Position.T) - float(Photon1.Position.T))
				
				if (math.fabs(Angle1) < math.fabs(SmallestAngle) and TimeSeparation < This.Parameters["SynchronicityLimit"]):
					
					SmallestAngle = Angle1
					
					SelectedPhoton = Photon1
					
					PhotonAndProtonAreSelected = True
				
				for Photon2 in ReconstructedPhotons1:#For finding invariant mass of pi0
					
					if (Photon2 != Photon1):#Is this valid in python?
						
						Angle2 = AngleBetweenDirections(Proton1.Position, Photon2.Position, Photon2.Direction)

						if ((Angle1 < This.Parameters["PhotonAngularLocalityLimit"]) and (Angle2 < This.Parameters["PhotonAngularLocalityLimit"])):
						
							Pi0Meson = Geometry.FourVector()
							
							Pi0Meson = Photon1.EnergyMomentum + Photon2.EnergyMomentum
							
							This.HistogramCollection1.Histograms["Pi0_Meson_Mass"].Populate(SelectedProton.Process, Pi0Meson.InvariantModulus(), str(SelectedProton.Process))
							
							#This.StackedHistograms["Pi0MesonMass"].ConstituentFill1D(This.Processes, SelectedProton.Process, Pi0Meson.InvariantModulus(), "Pi0Meson mass contribution for constituent", "Mass (GeV)", "Number", 100, 0, 1000, "Pi0MesonMass")
					
					
			This.ROOTFile1.HistogramDictionary["SelectedPhotonAngles"].Histogram.Fill(SmallestAngle)
			This.StackedHistograms["SelectedPhotonAnglesStacked"].ConstituentFill1D(This.Processes, SelectedProton.Process, SmallestAngle, "Angle for constituent", "Mass (GeV)", "Number", 100, 0, 180, "SelectedPhotonAngle")

			if ((len(ReconstructedPhotons1) > 0) and (PhotonAndProtonAreSelected)):
			
				DeltaBaryon = Geometry.FourVector()
						
				DeltaBaryon = SelectedPhoton.EnergyMomentum + SelectedProton.EnergyMomentum # Delta Baryon Energy
				
				DeltaBaryonMass = DeltaBaryon.InvariantModulus()
										
			if (ProtonSelected):
				
				
				This.HistogramCollection1.Histograms["Single_Proton_ECal_Multiplicity"].Populate(SelectedProton.Process, len(ReconstructedPhotons1), str(SelectedProton.Process))
				This.HistogramCollection1.Histograms["Single_Proton_PID_Multiplicity"].Populate(SelectedProton.Process, len(ReconstructedObjects1), str(SelectedProton.Process))"""
				
				#This.StackedHistograms["SingleProtonECalMultiplicity"].ConstituentFill1D(This.Processes, SelectedProton.Process, len(ReconstructedPhotons1), "ECal Multiplicity for single proton track events", "Multiplicity", "Number", 10, 0, 10, "ECalMultiplicity")
				#This.StackedHistograms["SingleProtonPIDMultiplicity"].ConstituentFill1D(This.Processes, SelectedProton.Process, len(ReconstructedObjects1), "PID Multiplicity for single proton track events", "Multiplicity", "Number", 10, 0, 10, "ProtonMultiplicity")

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
		if (math.fabs(DeltaBaryonMass - PhysicalConstants.Delta1BaryonMass) < This.Parameters["InvariantMassVarianceLimit"]):
			SatisfiesInvariantMass = True
		else:
			SatisfiesInvariantMass = False
				
		############################ Cuts #########################
		
		#DeltaPGammaCriteria = [True, False, False, False, False, False, False, False, False, False, False, False, False]
		
		DeltaPGammaCriteria = [True, False, False, False, False, False, False]
				
		if (PIDNumber > 0):
			DeltaPGammaCriteria[1] = True
		
		if (TPCValidPIDNumber > 0 and DeltaPGammaCriteria[1]):
			DeltaPGammaCriteria[2] = True
					
		if (NumberOfReconstructedProtonTracks > 0 and DeltaPGammaCriteria[2]):
			DeltaPGammaCriteria[3] = True
		
		if (NumberOfReconstructedProtonTracks >= 1 and DeltaPGammaCriteria[3]):
			DeltaPGammaCriteria[4] = True
			
		#DeltaPGammaProtonSelectionCut = 4

		#if (len(ReconstructedObjects1) <= This.Parameters["PathMultiplicityLimit"] and DeltaPGammaCriteria[4]): #Multiplicity cut can be applied later when protons have been selected?
		#	DeltaPGammaCriteria[5] = True

		#if (NumberOfReconstructedMuLeptonTracks == 0 and DeltaPGammaCriteria[4]): # Type cuts can also be applied to the identified PID later on
		#	DeltaPGammaCriteria[5] = True
			
		#if (NumberOfReconstructedElectronTracks == 0 and DeltaPGammaCriteria[5]):
		#	DeltaPGammaCriteria[6] = True	
		
		#if (NumberOfReconstructedAntiElectronTracks == 0 and DeltaPGammaCriteria[6]):
		#	DeltaPGammaCriteria[7] = True	
		
		#if ((NTrackerECalRecon > 0) and DeltaPGammaCriteria[7]):
		#	DeltaPGammaCriteria[8] = True
				
		if ((NumberOfProtonsAndPhotonsWithinSynchronicity > 0) and DeltaPGammaCriteria[4]):
			DeltaPGammaCriteria[5] = True
			
		if ((NumberOfProtonsAndPhotonsWithinAngle > 0) and DeltaPGammaCriteria[5]):
			DeltaPGammaCriteria[6] = True
		
		DeltaPGammaProtonSelectionCut = 100
		
		
		"""if (SingleProtonTrackFirst and DeltaPGammaCriteria[4]):
			DeltaPGammaCriteria[5] = True
		
		if (SingleProtonInFGDFiducial and DeltaPGammaCriteria[5]):
			DeltaPGammaCriteria[6] = True
			
		if (len(ReconstructedObjects1) <= This.Parameters["PathMultiplicityLimit"] and DeltaPGammaCriteria[6]):
			DeltaPGammaCriteria[7] = True

		if (NumberOfReconstructedMuLeptonTracks == 0 and DeltaPGammaCriteria[7]):
			DeltaPGammaCriteria[8] = True
			
		if (NumberOfReconstructedElectronTracks == 0 and DeltaPGammaCriteria[8]):
			DeltaPGammaCriteria[9] = True	
		
		if (NumberOfReconstructedAntiElectronTracks == 0 and DeltaPGammaCriteria[9]):
			DeltaPGammaCriteria[10] = True	
		
		if ((NTrackerECalRecon > 0) and DeltaPGammaCriteria[10]):
			DeltaPGammaCriteria[11] = True

		if (SmallestAngle <= This.Parameters["PhotonAngularLocalityLimit"] and DeltaPGammaCriteria[11]):
			DeltaPGammaCriteria[12] = True"""
					
		DeltaPGammaCutNumber = len(DeltaPGammaCriteria)
		
		#### P Pi0
		
		DeltaPPiCriteria = [True, False, False, False, False, False, False, False, False, False, False, False]
				
		if (PIDNumber > 0):
			DeltaPPiCriteria[1] = True
		
		if (TPCValidPIDNumber > 0 and DeltaPPiCriteria[1]):
			DeltaPPiCriteria[2] = True
					
		if (NumberOfReconstructedProtonTracks > 0 and DeltaPPiCriteria[2]):
			DeltaPPiCriteria[3] = True
		
		if (NumberOfReconstructedProtonTracks == 1 and DeltaPPiCriteria[3]):
			DeltaPPiCriteria[4] = True
		
		DeltaPPiProtonSelectionCut = 4
		
		if (SingleProtonTrackFirst and DeltaPPiCriteria[4]):
			DeltaPPiCriteria[5] = True
		
		if (SingleProtonInFGDFiducial and DeltaPPiCriteria[5]):
			DeltaPPiCriteria[6] = True
			
		if ((len(ReconstructedObjects1) <= This.Parameters["PathMultiplicityLimit"]) and DeltaPPiCriteria[6]):
			DeltaPPiCriteria[7] = True
		
		if (NumberOfReconstructedMuLeptonTracks == 0 and DeltaPPiCriteria[7]):
			DeltaPPiCriteria[8] = True
			
		if (NumberOfReconstructedElectronTracks == 0 and DeltaPPiCriteria[8]):
			DeltaPPiCriteria[9] = True	
		
		if (NumberOfReconstructedAntiElectronTracks == 0 and DeltaPPiCriteria[9]):
			DeltaPPiCriteria[10] = True	
		
		if (NTrackerECalRecon > 0 and DeltaPPiCriteria[10]):
			DeltaPPiCriteria[11] = True
		
		DeltaPPiCutNumber = len(DeltaPPiCriteria)
		
		EventContainsElectronPositronPair = False
		ElectronPositronPairPointsWithinAngle = False
		ElectronPositronPairPointsWithinTime = False
			
		
		ProtonPhotonToElectrons = [True, False, False, False, False, False, False, False]
		
		if (PIDNumber > 0):
			ProtonPhotonToElectrons[1] = True
		
		if (TPCValidPIDNumber > 0 and ProtonPhotonToElectrons[1]):
			ProtonPhotonToElectrons[2] = True
					
		if (NumberOfReconstructedProtonTracks > 0 and ProtonPhotonToElectrons[2]):
			ProtonPhotonToElectrons[3] = True
		
		if (NumberOfReconstructedProtonTracks >= 1 and ProtonPhotonToElectrons[3]):
			ProtonPhotonToElectrons[4] = True
		
			(EventContainsElectronPositronPair, ElectronPositronPairPointsWithinAngle, ElectronPositronPairPointsWithinTime) = This.EventContainsElectronPositron(ReconstructedObjects1, ReconstructedProtons1, None)
			
		if (EventContainsElectronPositronPair and ProtonPhotonToElectrons[4]):
			ProtonPhotonToElectrons[5] = True
			
		if (ElectronPositronPairPointsWithinAngle >= 1 and ProtonPhotonToElectrons[5]):
			ProtonPhotonToElectrons[6] = True
		
		if (ElectronPositronPairPointsWithinTime >= 1 and ProtonPhotonToElectrons[6]):
			ProtonPhotonToElectrons[7] = True
		
		ProtonPhotonToElectronsProtonSelectionCut = 100
		
		"""ProtonPhotonToElectrons = [True, False, False, False, False, False, False, False, False, False, False]
				
		if (PIDNumber > 0):
			ProtonPhotonToElectrons[1] = True
		
		if (TPCValidPIDNumber > 0 and ProtonPhotonToElectrons[1]):
			ProtonPhotonToElectrons[2] = True
					
		if (NumberOfReconstructedProtonTracks > 0 and ProtonPhotonToElectrons[2]):
			ProtonPhotonToElectrons[3] = True
		
		if (NumberOfReconstructedProtonTracks == 1 and ProtonPhotonToElectrons[3]):
			ProtonPhotonToElectrons[4] = True
		
		ProtonPhotonToElectronsProtonSelectionCut = 4
		
		if (SingleProtonTrackFirst and ProtonPhotonToElectrons[4]):
			ProtonPhotonToElectrons[5] = True
		
		if (SingleProtonInFGDFiducial and ProtonPhotonToElectrons[5]):
			ProtonPhotonToElectrons[6] = True			
			
			(EventContainsElectronPositronPair, ElectronPositronPairPointsWithinAngle, ElectronPositronPairPointsWithinTime) = This.EventContainsElectronPositron(ReconstructedObjects1, ReconstructedProtons1, SelectedProton.Process)
		
		if (NumberOfReconstructedMuLeptonTracks == 0 and ProtonPhotonToElectrons[6]):
			ProtonPhotonToElectrons[7] = True
		
		if (EventContainsElectronPositronPair and ProtonPhotonToElectrons[7]):
			ProtonPhotonToElectrons[8] = True		
		
		if (ElectronPositronPairPointsWithinAngle and ProtonPhotonToElectrons[8]):
			ProtonPhotonToElectrons[9] = True		
		
		if (ElectronPositronPairPointsWithinTime and ProtonPhotonToElectrons[9]):
			ProtonPhotonToElectrons[10] = True"""
			
		ProtonPhotonToElectronsCutNumber = len(ProtonPhotonToElectrons)	
	
		### Creation of Selection Lists:
		
		# Note from Tom: I have changed this part back to its original. Your new implementation did not work, but can be found in Analysis_43 if you want to improve it.
		
		if (This.TruthStatistics.Statistics["NEvents"].Quantity == 1):
			
			for CutCounter in xrange(DeltaPGammaCutNumber):
				
				SelectionCriterion1 = SelectionStatistics.SelectionStatistics()
				
				This.SelectionDictionary["DeltaPGamma"].append(SelectionCriterion1)
				
			for CutCounter in xrange(DeltaPPiCutNumber):
				
				SelectionCriterion1 = SelectionStatistics.SelectionStatistics()
				
				This.SelectionDictionary["DeltaPPi"].append(SelectionCriterion1)
				
			for CutCounter in xrange(ProtonPhotonToElectronsCutNumber):
				
				SelectionCriterion1 = SelectionStatistics.SelectionStatistics()
				
				This.SelectionDictionary["ProtonPhotonToElectrons"].append(SelectionCriterion1)
				
		for CutCounter in xrange(DeltaPGammaCutNumber):
			if (DeltaPGammaCriteria[CutCounter]):
				This.SelectionDictionary["DeltaPGamma"][CutCounter].EventsRemaining += 1
				
				if (CutCounter < DeltaPGammaProtonSelectionCut):
					
					
					if (TrueEventContainsDelta1ToProtonPhoton):
						This.SelectionDictionary["DeltaPGamma"][CutCounter].TruthDelta += 1
					else:
						This.SelectionDictionary["DeltaPGamma"][CutCounter].MixedEvent += 1
				
				elif (CutCounter >= DeltaPGammaProtonSelectionCut):

					if (SelectedProton.Process == "DeltaPGamma"):
						This.SelectionDictionary["DeltaPGamma"][CutCounter].TruthDelta += 1
					elif (SelectedProton.Process == "DeltaPPi"):
						This.SelectionDictionary["DeltaPGamma"][CutCounter].ReconstructedDelta += 1
					elif (SelectedProton.Process == "OtherResonance"):
						This.SelectionDictionary["DeltaPGamma"][CutCounter].OtherRPInteraction += 1
					elif (SelectedProton.Process == "QS"):
						This.SelectionDictionary["DeltaPGamma"][CutCounter].QSInteraction += 1
					elif (SelectedProton.Process == "ES"):
						This.SelectionDictionary["DeltaPGamma"][CutCounter].ESInteraction += 1
					elif (SelectedProton.Process == "DIS"):
						This.SelectionDictionary["DeltaPGamma"][CutCounter].DISInteraction += 1
					elif (SelectedProton.Process == "C"):
						This.SelectionDictionary["DeltaPGamma"][CutCounter].CSInteraction += 1
					
		for CutCounter in xrange(DeltaPPiCutNumber):
			if (DeltaPPiCriteria[CutCounter]):
				This.SelectionDictionary["DeltaPPi"][CutCounter].EventsRemaining += 1
				
				if (CutCounter < DeltaPPiProtonSelectionCut):
					
					if (TrueEventContainsDelta1ToProtonPi0):
						This.SelectionDictionary["DeltaPPi"][CutCounter].ReconstructedDelta += 1
					else:
						This.SelectionDictionary["DeltaPPi"][CutCounter].MixedEvent += 1
				
				elif (CutCounter >= DeltaPPiProtonSelectionCut):
				
					if (SelectedProton.Process == "DeltaPGamma"):
						This.SelectionDictionary["DeltaPPi"][CutCounter].TruthDelta += 1
					elif (SelectedProton.Process == "DeltaPPi"):
						This.SelectionDictionary["DeltaPPi"][CutCounter].ReconstructedDelta += 1
					elif (SelectedProton.Process == "OtherResonance"):
						This.SelectionDictionary["DeltaPPi"][CutCounter].OtherRPInteraction += 1
					elif (SelectedProton.Process == "QS"):
						This.SelectionDictionary["DeltaPPi"][CutCounter].QSInteraction += 1
					elif (SelectedProton.Process == "ES"):
						This.SelectionDictionary["DeltaPPi"][CutCounter].ESInteraction += 1
					elif (SelectedProton.Process == "DIS"):
						This.SelectionDictionary["DeltaPPi"][CutCounter].DISInteraction += 1
					elif (SelectedProton.Process == "C"):
						This.SelectionDictionary["DeltaPPi"][CutCounter].CSInteraction += 1
					
		for CutCounter in xrange(ProtonPhotonToElectronsCutNumber):
			if (ProtonPhotonToElectrons[CutCounter]):
				This.SelectionDictionary["ProtonPhotonToElectrons"][CutCounter].EventsRemaining += 1
				
				if (CutCounter < ProtonPhotonToElectronsProtonSelectionCut):
					
					if (TrueEventContainsDelta1ToProtonPhoton):
						This.SelectionDictionary["ProtonPhotonToElectrons"][CutCounter].TruthDelta += 1
					else:
						This.SelectionDictionary["ProtonPhotonToElectrons"][CutCounter].MixedEvent += 1
				
				elif (CutCounter >= ProtonPhotonToElectronsProtonSelectionCut):
					
					if (SelectedProton.Process == "DeltaPGamma"):
						This.SelectionDictionary["ProtonPhotonToElectrons"][CutCounter].TruthDelta += 1
					elif (SelectedProton.Process == "DeltaPPi"):
						This.SelectionDictionary["ProtonPhotonToElectrons"][CutCounter].ReconstructedDelta += 1
					elif (SelectedProton.Process == "OtherResonance"):
						This.SelectionDictionary["ProtonPhotonToElectrons"][CutCounter].OtherRPInteraction += 1
					elif (SelectedProton.Process == "QS"):
						This.SelectionDictionary["ProtonPhotonToElectrons"][CutCounter].QSInteraction += 1
					elif (SelectedProton.Process == "ES"):
						This.SelectionDictionary["ProtonPhotonToElectrons"][CutCounter].ESInteraction += 1
					elif (SelectedProton.Process == "DIS"):
						This.SelectionDictionary["ProtonPhotonToElectrons"][CutCounter].DISInteraction += 1
					elif (SelectedProton.Process == "C"):
						This.SelectionDictionary["ProtonPhotonToElectrons"][CutCounter].CSInteraction += 1
		
		################ Invariant Mass Section #########
		
		# Keep
		
		#if (DeltaPGammaCriteria[len(DeltaPGammaCriteria) - 1] == True):
			
		#	This.HistogramCollection1.Histograms["Final_Invariant_Mass"].Populate(SelectedProton.Process, DeltaBaryonMass, str(SelectedProton.Process))
			
			#This.StackedHistograms["FinalInvariantMass"].ConstituentFill1D(This.Processes, SelectedProton.Process, DeltaBaryonMass, "Invariant Mass after all cuts for constituent", "Mass (GeV)", "Number", 100, 0, 3000, "FinalInvariantMass")
		
		
		
		## Get rid?
		
					
		#if (DeltaPGammaCriteria[7] and PhotonAndProtonAreSelected):#Matching Single proton to Every ECal cluster# Not sure if this is needed anymore
			
		#	for Photon1 in ReconstructedPhotons1:
				
		#		DeltaBaryon = Geometry.FourVector()
				
		#		DeltaBaryon = Photon1.EnergyMomentum + SelectedProton.EnergyMomentum # Delta Baryon Energy
			
		#		This.HistogramCollection1.Histograms["Invariant_Mass_All_ECal"].Populate(SelectedProton.Process, DeltaBaryon.InvariantModulus(), str(SelectedProton.Process))
				
				#This.StackedHistograms["InvariantMassAllECal"].ConstituentFill1D(This.Processes, SelectedProton.Process, DeltaBaryon.InvariantModulus(), "Invariant Mass for constituent", "Mass (GeV)", "Number", 100, 0, 3000, "InvariantMassAllECal")

		######### Background Events ##########		

		"""if (This.SelectBackgroundEvents == True):

			if (DeltaPGammaCriteria[len(DeltaPGammaCriteria) - 1] == True):

				This.DeltaPGammaEventFile = open(This.DeltaPGammaEventFileLocator, "a")
				This.DeltaPGammaEventFile.write(str(SelectedProton.Process) + " " + str(This.BasicInformation.RunID) + " " + str(This.BasicInformation.SubrunID) + " " + str(This.BasicInformation.EventID) + TextConstants.NewLine)					
				This.DeltaPGammaEventFile.close()
				
			if (DeltaPPiCriteria[len(DeltaPPiCriteria) - 1] == True):

				This.DeltaPPiCriteriaEventFile = open(This.DeltaPPiEventFileLocator, "a")
				This.DeltaPPiCriteriaEventFile.write(str(SelectedProton.Process) + " " + str(This.BasicInformation.RunID) + " " + str(This.BasicInformation.SubrunID) + " " + str(This.BasicInformation.EventID) + TextConstants.NewLine)					
				This.DeltaPPiCriteriaEventFile.close()
				
			if (ProtonPhotonToElectrons[len(ProtonPhotonToElectrons) - 1] == True):

				This.DeltaPGammaPPEventFile = open(This.DeltaPGammaPPEventFileLocator, "a")
				This.DeltaPGammaPPEventFile.write(str(SelectedProton.Process) + " " + str(This.BasicInformation.RunID) + " " + str(This.BasicInformation.SubrunID) + " " + str(This.BasicInformation.EventID) + TextConstants.NewLine)					
				This.DeltaPGammaPPEventFile.close()	"""#Must Select a proton!
				
		########################################
		# Delta Baryon Mass #
		########################################


		if (len(ReconstructedPhotons1) > 0 and len(ReconstructedProtons1) > 0):
			# If both a photon cluster and proton track were found ...

			for Photon1 in ReconstructedPhotons1:
				for Proton1 in ReconstructedProtons1:
					# Consider every possible combination of one photon and one proton and add the derived particle kinematics to the relevant histogram.
					
					DeltaBaryon = Geometry.FourVector()
					
					DeltaBaryon = Photon1.EnergyMomentum + Proton1.EnergyMomentum # Delta Baryon Energy
																					
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
						
						if (TimeSeparation < This.Parameters["SynchronicityLimit"]):
							This.ReconstructedStatistics.Statistics["NEventsWithTECCAndCRProtonWithin10DWithin500ns"].Quantity += 1
					
					This.ROOTFile1.HistogramDictionary["PhotonAngles"].Histogram.Fill(Angle1)
					This.StackedHistograms["PhotonAnglesStacked"].ConstituentFill1D(This.Processes, Proton1.Process, Angle1, "Angle for constituent", "Mass (GeV)", "Number", 100, 0, 180, "PhotonAngle")
					This.ROOTFile1.HistogramDictionary["ProtonPhotonTimeSeparations"].Histogram.Fill(TimeSeparation)
					
					
					if (TimeSeparation < This.Parameters["SynchronicityLimit"]):
																						
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
	
	def MuonProtonSameVertex(This, Muon, Proton):

		MuonProtonSameVertex = False

		MuonFrontPosition = Muon.FrontPosition.ToThreeVector()
		ProtonFrontPosition = Proton.Position.ToThreeVector()
				
		FrontPositionSeparation = ProtonFrontPosition - MuonFrontPosition

		This.HistogramCollection1.Histograms["Proton_Muon_Separation"].Populate(Proton.Process, FrontPositionSeparation.Modulus(), str(Proton.Process))
		
		#This.StackedHistograms["ProtonMuonSeparation"].ConstituentFill1D(This.Processes, Proton.Process, FrontPositionSeparation.Modulus(), "Proton Muon Separation for constituent", "Separation (cm)", "Number", 100, 0, This.Parameters["LocalityLimit"] * 5, "ProtonMuonSeparation")

		if (FrontPositionSeparation.Modulus() < This.Parameters["LocalityLimit"]):
				
			MuonProtonSameVertex = True
			
		return MuonProtonSameVertex
		
	def SelectMuons(This, PIDParticles1):
		
		Muons = []
		
		for PIDParticle1 in PIDParticles1:		
			if (PIDParticle1.GoodNumberOfTPCPoints == True):						
				if (PIDParticle1.ReconParticleID == ParticleCodes.MuLepton):
					
					Muons.append(PIDParticle1)
		
		return Muons
			
	def EventContainsElectronPositron(This, PIDParticles1, Protons, TruthInteractionType):
		
		EventContainsElectron = False
		EventContainsPositron = False
		EventContainsElectronPositronPair = False
		EventContainsElectronPositronPairWithinAngle = False
		EventContainsElectronPositronPairWithinTime = False
		
		EventContainsMuon = False		
		
		Electrons = []
		Positrons = []		
		ElectronPositronPairs = []
		
		Muons = []
		
		for PIDParticle1 in PIDParticles1:		
			if (PIDParticle1.GoodNumberOfTPCPoints == True):
					
				if ((PIDParticle1.ReconParticleID == ParticleCodes.Electron) and (PIDParticle1.Charge == -1)):				
					EventContainsElectron = True		
					Electrons.append(PIDParticle1)
						
				if ((PIDParticle1.ReconParticleID == ParticleCodes.Electron) and (PIDParticle1.Charge == +1)):				
					EventContainsPositron = True		
					Positrons.append(PIDParticle1)	
						
				if (PIDParticle1.ReconParticleID == ParticleCodes.MuLepton):
					EventContainsMuon = True	
					Muons.append(PIDParticle1)	
		
		for Electron1 in Electrons:
			for Positron1 in Positrons:
					
				if (Geometry.WithinLocality(Electron1.FrontPosition, Positron1.FrontPosition, This.Parameters["LocalityLimit"])):
					
					EventContainsElectronPositronPair = True
					
					ElectronPositronPairs.append([Electron1, Positron1])
					
					RParticle1 = Particles.ReconstructedParticle()
					RParticle2 = Particles.ReconstructedParticle()
					
					RParticle1.EnergyMomentum.T = Electron1.ReconstructedParticleEnergy()
					RParticle1.EnergyMomentum.X = Electron1.ReconFrontDirectionX * Electron1.ReconFrontMomentum
					RParticle1.EnergyMomentum.Y = Electron1.ReconFrontDirectionY * Electron1.ReconFrontMomentum
					RParticle1.EnergyMomentum.Z = Electron1.ReconFrontDirectionZ * Electron1.ReconFrontMomentum
					
					RParticle2.EnergyMomentum.T = Positron1.ReconstructedParticleEnergy()
					RParticle2.EnergyMomentum.X = Positron1.ReconFrontDirectionX * Positron1.ReconFrontMomentum
					RParticle2.EnergyMomentum.Y = Positron1.ReconFrontDirectionY * Positron1.ReconFrontMomentum
					RParticle2.EnergyMomentum.Z = Positron1.ReconFrontDirectionZ * Positron1.ReconFrontMomentum
					
					PossiblePhoton1 = Particles.ReconstructedParticle()
															
					PossiblePhoton1.Position = Geometry.AverageLocation(Electron1.FrontPosition, Positron1.FrontPosition)
					PossiblePhoton1.EnergyMomentum = RParticle1.EnergyMomentum + RParticle2.EnergyMomentum
					
					This.HistogramCollection1.Histograms["ElectronPositronInvariantMass"].Populate(PossiblePhoton1.EnergyMomentum.InvariantModulus())
															
					for Proton1 in Protons:
												
						Angle1 = AngleBetweenDirections(Proton1.Position, PossiblePhoton1.Position, PossiblePhoton1.EnergyMomentum.SpatialDirection())
						TimeSeparation = math.fabs(float(Proton1.Position.T) - float(PossiblePhoton1.Position.T))

						if (Angle1 < This.Parameters["PairProductionAngularLocalityLimit"]):
							EventContainsElectronPositronPairWithinAngle = True
						
						if (TimeSeparation < This.Parameters["SynchronicityLimit"]):
							EventContainsElectronPositronPairWithinTime = True
						
						if (EventContainsElectronPositronPairWithinAngle and EventContainsElectronPositronPairWithinTime):#Getting problems
						
							#This.ROOTFile1.HistogramDictionary["ElectronPositronPairs_Photon_AngleToProton"].Histogram.Fill(Angle1)
							"""
							#This.HistogramCollection1.Histograms["ElectronPositronPairs_Photon_AngleToProton"].Populate(TruthInteractionType, Angle1)
							"""
					
		if (EventContainsElectronPositronPair == True):
			This.ReconstructedStatistics.Statistics["NEventsWithElectronPositronPairs"].Quantity += 1
			
						
		return (EventContainsElectronPositronPair, EventContainsElectronPositronPairWithinAngle, EventContainsElectronPositronPairWithinTime)
		

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
	
def PIDTruth(GRTVertices, TrueTrajectories, PID):
	
	TrueVertex = None
	TrueTrajectory = None
		
	for GRTVertex1 in GRTVertices:
					
		if (GRTVertex1.TruthVertexID == PID.TrueParticle.Vertex.ID):
						
			TrueVertex = GRTVertex1
			
	for Trajectory1 in TrueTrajectories:
				
		if (Trajectory1.ID == PID.TrueParticle.ID):
			
			TrueTrajectory = Trajectory1
			
	return TrueVertex, TrueTrajectory
			
def ElapsedTime(StartTime, TimeDelta):
	
	CurrentTime = time.time()
	
	TimeDifference = CurrentTime - StartTime
	
	return int(TimeDifference)/int(TimeDelta)

def main():
	
	Time1 = time.time()
	
	NumberOfEventsToRead = 0
	DefaultNumberOfEventsToRead = 200

	InputFileLocator = ""
	DefaultInputFileLocatorUnpurified = "/storage/epp2/t2k/data/nd280/production005/C/mcp/genie/2010-11-water/magnet/beamb/anal/"
	DefaultInputFileLocatorPurified = "/storage/epp2/phseaj/2012_Delta/delta_pgamma_prod/ana/"
		
	NumberOfEventsToRead = DefaultNumberOfEventsToRead
	InputFileLocator = DefaultInputFileLocatorPurified
	IsTimingTest = False
	SelectBackgroundEvents = False
	
	CommandLineDeconstructor1 = CommandLine.Deconstructor(sys.argv)
		
	SimulationInformation = {}
	
	SimulationInformation["DesiredNumberOfEvents"] = ""
	SimulationInformation["InputFilePurity"] = ("Reading events from:" + str(InputFileLocator), "P1")
	SimulationInformation["TimingTestFlag"] = ""
	SimulationInformation["BackgroundEventsFlag"] = ""
	
	if (len(sys.argv) > 1):
		
		for i in range(len(sys.argv)):
			if (i > 0):
				
				ArgumentText = str(sys.argv[i])
				
				ArgumentComponents = ArgumentText.split(":")
				
				if (len(ArgumentComponents) == 2):
					
					if (ArgumentComponents[0] == "NE"):
						NumberOfEventsToRead = int(ArgumentComponents[1])
						
					if (ArgumentComponents[0] == "P"):
						if (ArgumentComponents[1] == str(0)):
							SimulationInformation["InputFilePurity"] = ("Reading events from: " + str(DefaultInputFileLocatorUnpurified), "P0")
							InputFileLocator = DefaultInputFileLocatorUnpurified
						elif (ArgumentComponents[1] == str(1)):
							SimulationInformation["InputFilePurity"] = ("Reading events from:" + str(DefaultInputFileLocatorPurified), "P1")
							InputFileLocator = DefaultInputFileLocatorPurified
							
				elif (len(ArgumentComponents) == 1):
					
					if (ArgumentComponents[0] == "TT"):
						SimulationInformation["TimingTestFlag"] = ("Perform Timing Test", "TT")
						IsTimingTest = True
						
					if (ArgumentComponents[0] == "BE"):
						SimulationInformation["BackgroundEventsFlag"] = ("Select Background Events", "BE")
						SelectBackgroundEvents = True
						
	elif (len(sys.argv) == 1):
		SimulationInformation["InputFilePurity"] = ("Reading events from:" + str(DefaultInputFileLocatorPurified), "P1")
	
	SimulationInformation["DesiredNumberOfEvents"] = ("Desired number of Events: " + str(int(NumberOfEventsToRead)), "NE" + str(int(NumberOfEventsToRead)))
		
	OutputROOTFileLocator = FileAdministrator.CreateFilePath(DataLocation, ".root", SimulationInformation)
	SimulationInformationFileLocator = FileAdministrator.CreateFilePath(DataLocation, ".log", SimulationInformation)
	
	sys.stdout = DataWriter.DataWriterStdOut(SimulationInformationFileLocator, "w")
	sys.stderr = DataWriter.DataWriterStdErr(SimulationInformationFileLocator, "a")
	
	print TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine, TextConstants.LineSeparator
	print "File Information"
	print TextConstants.LineSeparator
	
	print "Running Script:" , os.path.basename( __file__ )
	print "Outputting data to:" , DataLocation + str(FileAdministrator.CreateDTLocator(SimulationInformation)[0])
	print "File name stamp:" , str(FileAdministrator.CreateDTLocator(SimulationInformation)[1])
	
	print TextConstants.NewLine, TextConstants.NewLine, TextConstants.LineSeparator
	print "Simulation Information"
	print TextConstants.LineSeparator
	
	for Parameter in SimulationInformation.itervalues():
		
		if (len(Parameter) > 0):
			
			print Parameter[0]

	libraries.load("nd280/nd280.so")

	InputFileLocatorList = glob.glob(InputFileLocator + "*.root")
	
	del sys.stdout
	del sys.stderr
	
	sys.stdout = DataWriter.DataWriterStdOut(SimulationInformationFileLocator, "a")
	sys.stderr = DataWriter.DataWriterStdErr(SimulationInformationFileLocator, "a")
	
	Analysis1 = Analysis(InputFileLocatorList, OutputROOTFileLocator, SimulationInformationFileLocator, SimulationInformation)
	Analysis1.InputTimeTest = IsTimingTest
	Analysis1.SelectBackgroundEvents = SelectBackgroundEvents
	Analysis1.Analyse(NumberOfEventsToRead)
	
	sys.stdout = DataWriter.DataWriterStdOut(SimulationInformationFileLocator, "a")
	sys.stderr = DataWriter.DataWriterStdErr(SimulationInformationFileLocator, "a")
	
	Time2 = time.time()
	
	TotalTime = Time2 - Time1
	
	print "Total time taken for program to run:" , "%.1f" % TotalTime , "seconds."
	
	del sys.stdout
	del sys.stderr

if __name__ == "__main__":
	main()
