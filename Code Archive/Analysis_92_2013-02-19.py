########################################################################################################################
####
#### ANALYSIS
#### 
########################################################################################################################

import sys
import os

import math
import glob
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
import SubdetectorCodes

import Geometry

import SelectionStatistics

import Statistics
import StackedHistogram


import ProgressMeter

import CommandLine
import FileAdministrator

import Simulation
import Charts
import Colours
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
		This.MonteCarloFull = False
		This.NoSelection = False
				
		This.EventCollection1 = Simulation.EventCollection()
		
		This.HistogramCollection1 = Charts.HistogramCollection()
		
		
		This.Parameters = {} # In some cases we have parameters which we could vary to improve purity, and which are used throughout the analysis. They can be assigned here.
		
		This.Parameters["MuonProtonLocalityLimit"] = 50
		This.Parameters["LocalityLimit"] = Geometry.ThreeVector
		
		This.Parameters["LocalityLimit"].X = 50 # In millimetres
		This.Parameters["LocalityLimit"].Y = 50 # In millimetres
		This.Parameters["LocalityLimit"].Z = 50 # In millimetres
		This.Parameters["PhotonAngularLocalityLimit"] = 20 # In degrees
		This.Parameters["PairProductionAngularLocalityLimit"] = 20 # In degrees
		This.Parameters["SynchronicityLimit"] = 250 # In nanoseconds
		
		This.Parameters["ProtonTrackMultiplicityLimitECalChannel"] = 3
		This.Parameters["ECalMultiplicityLimitECalChannel"] = 4
		
		This.Parameters["ProtonTrackMultiplicityLimitPPChannel"] = 3
		This.Parameters["ECalMultiplicityLimitPPChannel"] = 4
		
		This.Parameters["PathMultiplicityLimit"] = 3
		
		This.Parameters["MuonMultiplicityCut"] = 1
		This.Parameters["ElectronMultiplicityCut"] = 1
		This.Parameters["PositronMultiplicityCut"] = 1
		
		This.Parameters["TorrentMultiplicityLimit"] = 100 # Effectively no limit
		
		This.Parameters["PullLimits"] = {}
		
		This.Parameters["PullLimits"][ParticleCodes.Electron] = 3
		This.Parameters["PullLimits"][ParticleCodes.K1Meson] = 4
		This.Parameters["PullLimits"][ParticleCodes.MuLepton] = 2
		This.Parameters["PullLimits"][ParticleCodes.Pi1Meson] = 2
		This.Parameters["PullLimits"][ParticleCodes.Proton] = 4
		
		This.Parameters["InvariantMassVarianceLimit"] = 250
		This.Parameters["Pi0MesonMassCut"] = 50
				
				
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
			
			This.DeltaPGammaEventFileLocator = FileAdministrator.CreateFilePath(DataLocation, "_DeltaPGamma.Event", This.SimulationInformation, "Event/")
			This.DeltaPPiEventFileLocator = FileAdministrator.CreateFilePath(DataLocation, "_DeltaPPi.Event", This.SimulationInformation, "Event/")
			This.DeltaPGammaPPEventFileLocator = FileAdministrator.CreateFilePath(DataLocation, "_DeltaPGammaPP.Event", This.SimulationInformation, "Event/")

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
		
		n10 = 0
		
		for i in range(EventNumber):
			for module in This.Modules:
				module.GetEntry(i)
			
			This.TruthStatistics.Statistics["NPEvents"].Quantity = i + 1
			
			if (This.MonteCarloFull):
			
				This.MonteCarloFullTruthStatistics.Statistics["NPEvents"].Quantity = i + 1
			
			if (This.InputTimeTest == False):
			
				SuitableEvent = False
			
				for PID in This.Reconstructed_Global.PIDs:

					X1 = PID.FrontPosition.X()
					Y1 = PID.FrontPosition.Y()
					Z1 = PID.FrontPosition.Z()

					if ((This.FGD1Fiducial.Contains(X1, Y1, Z1) == True) or (This.FGD2Fiducial.Contains(X1, Y1, Z1) == True)):
						SuitableEvent = True
		
				if (This.MonteCarloFull):
					
					for GRTVertex1 in This.Truth_GRTVertices.Vtx:
						
						IncidentNeutrino = False
						
						ProtonFromDelta = False
						PhotonFromDelta = False
						Pi0MesonFromDelta = False
						
						for GRTParticle1 in This.RTTools.getParticles(GRTVertex1):
							
							if (GRTParticle1.pdg == ParticleCodes.MuNeutrino):
							
								if (GRTParticle1.status == 0):
								
									IncidentMuonNeutrino = True						
							
							if (GRTParticle1.pdg == ParticleCodes.Delta1Baryon):

								DeltaDaughterFirst = GRTParticle1.first_daughter
								DeltaDaughterLast = GRTParticle1.last_daughter
								DeltaDaughterNumber = DeltaDaughterLast - DeltaDaughterFirst + 1

								if (DeltaDaughterNumber == 2):
									
									for DaughterParticle in This.RTTools.getParticles(GRTVertex1):
									
										if (DaughterParticle.i >= DeltaDaughterFirst and DaughterParticle.i <= DeltaDaughterLast):
										
											if (DaughterParticle.pdg == ParticleCodes.Proton):
												ProtonFromDelta = True
												
											if (DaughterParticle.pdg == ParticleCodes.Photon):
												PhotonFromDelta = True
												
											if (DaughterParticle.pdg == ParticleCodes.Pi0Meson):
												Pi0MesonFromDelta = True
													
						This.EventCodeDeconstructor1.ReadCode(GRTVertex1.EvtCode)
						
						TruthCurrent = This.EventCodeDeconstructor1.Elements["Current Code"].Content
						TruthInteractionType = This.EventCodeDeconstructor1.Elements["Process Code"].Content
					
						DeltaPGammaInteraction = (IncidentMuonNeutrino and ProtonFromDelta and PhotonFromDelta and TruthInteractionType == "RP")
						
						Delta1BaryonToProtonPi0MesonInteraction = (IncidentMuonNeutrino and ProtonFromDelta and Pi0MesonFromDelta and TruthInteractionType == "RP")
						
						This.MonteCarloFullTruthStatistics.Statistics["NFullVertices"].Quantity += 1
						
						if (DeltaPGammaInteraction):
							This.MonteCarloFullTruthStatistics.Statistics["NFullDeltaToProtonPhoton"].Quantity += 1
						if (DeltaPGammaInteraction and TruthCurrent == "CC"):
							This.MonteCarloFullTruthStatistics.Statistics["NFullDeltaToProtonPhotonCC"].Quantity += 1
						if (DeltaPGammaInteraction and TruthCurrent == "NC"):
							This.MonteCarloFullTruthStatistics.Statistics["NFullDeltaToProtonPhotonNC"].Quantity += 1
						
						if (Delta1BaryonToProtonPi0MesonInteraction):
							This.MonteCarloFullTruthStatistics.Statistics["NFullDeltaToProtonPion"].Quantity += 1
						if (Delta1BaryonToProtonPi0MesonInteraction and TruthCurrent == "CC"):
							This.MonteCarloFullTruthStatistics.Statistics["NFullDeltaToProtonPionCC"].Quantity += 1
						if (Delta1BaryonToProtonPi0MesonInteraction and TruthCurrent == "NC"):
							This.MonteCarloFullTruthStatistics.Statistics["NFullDeltaToProtonPionNC"].Quantity += 1


						for Vertex1 in This.Truth_Vertices.Vertices:
							
							if (GRTVertex1.TruthVertexID == Vertex1.ID):#See ToaAnalysisUtils.cxx in Code Archive, looking for TPC or FGD
								
								if ((Vertex1.Subdetector == 0) or (Vertex1.Subdetector == 1) or (Vertex1.Subdetector == 6) or (Vertex1.Subdetector == 7) or (Vertex1.Subdetector == 8)):
									
									This.MonteCarloFullTruthStatistics.Statistics["NTrackerVertices"].Quantity += 1
									
									if (DeltaPGammaInteraction):
										This.MonteCarloFullTruthStatistics.Statistics["NTrackerDeltaToProtonPhoton"].Quantity += 1
									if (DeltaPGammaInteraction and TruthCurrent == "CC"):
										This.MonteCarloFullTruthStatistics.Statistics["NTrackerDeltaToProtonPhotonCC"].Quantity += 1
									if (DeltaPGammaInteraction and TruthCurrent == "NC"):
										This.MonteCarloFullTruthStatistics.Statistics["NTrackerDeltaToProtonPhotonNC"].Quantity += 1
									
									if (Delta1BaryonToProtonPi0MesonInteraction):
										This.MonteCarloFullTruthStatistics.Statistics["NTrackerDeltaToProtonPion"].Quantity += 1
									if (Delta1BaryonToProtonPi0MesonInteraction and TruthCurrent == "CC"):
										This.MonteCarloFullTruthStatistics.Statistics["NTrackerDeltaToProtonPionCC"].Quantity += 1
									if (Delta1BaryonToProtonPi0MesonInteraction and TruthCurrent == "NC"):
										This.MonteCarloFullTruthStatistics.Statistics["NTrackerDeltaToProtonPionNC"].Quantity += 1
									
								if ((Vertex1.Subdetector == 0) or (Vertex1.Subdetector == 1)):
								
									This.MonteCarloFullTruthStatistics.Statistics["NFGDVertices"].Quantity += 1
								
									if (DeltaPGammaInteraction):
										This.MonteCarloFullTruthStatistics.Statistics["NFGDDeltaToProtonPhoton"].Quantity += 1
									if (DeltaPGammaInteraction and TruthCurrent == "CC"):
										This.MonteCarloFullTruthStatistics.Statistics["NFGDDeltaToProtonPhotonCC"].Quantity += 1
									if (DeltaPGammaInteraction and TruthCurrent == "NC"):
										This.MonteCarloFullTruthStatistics.Statistics["NFGDDeltaToProtonPhotonNC"].Quantity += 1
									
									if (Delta1BaryonToProtonPi0MesonInteraction):
										This.MonteCarloFullTruthStatistics.Statistics["NFGDDeltaToProtonPion"].Quantity += 1
									if (Delta1BaryonToProtonPi0MesonInteraction and TruthCurrent == "CC"):
										This.MonteCarloFullTruthStatistics.Statistics["NFGDDeltaToProtonPionCC"].Quantity += 1
									if (Delta1BaryonToProtonPi0MesonInteraction and TruthCurrent == "NC"):
										This.MonteCarloFullTruthStatistics.Statistics["NFGDDeltaToProtonPionNC"].Quantity += 1
					
				if (ProgressMeter1.Update(i)):
					
					del sys.stdout
					del sys.stderr
					
					sys.stdout = DataWriter.DataWriterStdOut(This.SimulationInformationFileLocator, "a")
					sys.stderr = DataWriter.DataWriterStdErr(This.SimulationInformationFileLocator, "a")
				
				OutputData = False
				
				if (SuitableEvent and (This.NoSelection == False)):
					
					SuitableEvents += 1
					
					This.runEvent()
					
					CurrentTime = ElapsedTime(StartTime, 3600)#One Hour

					if ((CurrentTime != PreviousTime)):
						OutputData = True
						
					PreviousTime = CurrentTime
					
				if ((OutputData or (i == EventNumber - 1)) and (SuitableEvents > 0)):
					
					print "ROOT Histograms and text data have been outputted to file after an elapsed time of" , CurrentTime , "hours."
					
					l1 = This.OutputROOTFileLocator
					l2 = l1.split(".")
					
					n10 += 1
					
					l3 = l2[0] + "_I" + str(n10) + "." + l2[1]
					
					TimeOutputFile = ROOTFile.ROOTFile(l3)
					
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
								SelectionStatistics1.MultipleTrackerPurity = float(SelectionStatistics1.MultipleTracker) / float(EventsRemaining)
								SelectionStatistics1.NonTrackerPurity = float(SelectionStatistics1.NonTracker) / float(EventsRemaining)
							
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

						Location = "Selections/" + Key + "/"
						CutNumber = len(SelectionChannel)					
										
						############################################
						# Efficiency and Purity Graphs #
						############################################

						# This section is still being worked on, but when last tested it produced the correct graphs, so there should be no need to change it.

						AbsoluteEfficiencyReference = "AbsoluteEfficiency" + Key
						RelativeEfficiencyReference = "RelativeEfficiency" + Key
						PurityReference = "Purity" + Key
						NormalisedPurityReference = "NormalisedPurity" + Key
						CutPurityReference = "SelectionPurity" + Key
						
						if (n10 == 1):
							
							This.HistogramCollection1.NewHistogram1D(AbsoluteEfficiencyReference, Location, "Absolute efficiency for the selections", "Selections", CutNumber, 0, CutNumber, "Absolute Efficiency")
							This.HistogramCollection1.NewHistogram1D(RelativeEfficiencyReference, Location, "Relative efficiency for the selections", "Selections", CutNumber, 0, CutNumber, "Relative Efficiency")
							This.HistogramCollection1.NewHistogram1D(PurityReference, Location, "Purity for the selections", "Selections", CutNumber, 0, CutNumber, "Purity")
							This.HistogramCollection1.NewStackedHistogram1D(NormalisedPurityReference, Location + "Normalised/", "Constituent processes after each selection (Normalised)", "Selections", CutNumber, 0, CutNumber, "Events Remaining")
							This.HistogramCollection1.NewStackedHistogram1D(CutPurityReference, Location + "/Energy/", "Constituent Processes for the Events after every Selection", "Selections", CutNumber, 0, CutNumber, "Events Remaining")

						for CriteriaListCounter in xrange(CutNumber):
							
							This.HistogramCollection1.Histograms[AbsoluteEfficiencyReference].Populate(CriteriaListCounter, SelectionChannel[CriteriaListCounter].AbsoluteEfficiency)
							This.HistogramCollection1.Histograms[RelativeEfficiencyReference].Populate(CriteriaListCounter, SelectionChannel[CriteriaListCounter].RelativeEfficiency)
							
							PurityWeight = 0
							PurityError = 0

							if	(Key == "DeltaPGamma"):
								PurityWeight = SelectionChannel[CriteriaListCounter].Purity
							elif (Key == "DeltaPPi"):
								PurityWeight = SelectionChannel[CriteriaListCounter].PionPurity
							elif (Key == "ProtonPhotonToElectrons"):
								PurityWeight = SelectionChannel[CriteriaListCounter].Purity
								
							This.HistogramCollection1.Histograms[PurityReference].Populate(CriteriaListCounter, PurityWeight)
														
							if (SelectionChannel[CriteriaListCounter].EventsRemaining > 0 and PurityWeight < 1):
								PurityError = math.sqrt(float(PurityWeight - (PurityWeight * PurityWeight)) / float(SelectionChannel[CriteriaListCounter].EventsRemaining))
							
							This.HistogramCollection1.Histograms[PurityReference].BinErrors.append([CriteriaListCounter + 1, PurityError])
									
						if (n10 == 1):
								
							This.HistogramCollection1.Histograms[AbsoluteEfficiencyReference].Colour = Colours.White
							This.HistogramCollection1.Histograms[AbsoluteEfficiencyReference].MarkerStyle = 8
							This.HistogramCollection1.Histograms[AbsoluteEfficiencyReference].Options = "LP"
							This.HistogramCollection1.Histograms[AbsoluteEfficiencyReference].Statistics = 0
							
							This.HistogramCollection1.Histograms[RelativeEfficiencyReference].Colour = Colours.White
							This.HistogramCollection1.Histograms[RelativeEfficiencyReference].MarkerStyle = 8
							This.HistogramCollection1.Histograms[RelativeEfficiencyReference].Options = "LP"
							This.HistogramCollection1.Histograms[RelativeEfficiencyReference].Statistics = 0
							
							This.HistogramCollection1.Histograms[PurityReference].Colour = Colours.White
							This.HistogramCollection1.Histograms[PurityReference].MarkerStyle = 8
							This.HistogramCollection1.Histograms[PurityReference].Options = "E1"
							This.HistogramCollection1.Histograms[PurityReference].Statistics = 0
													
							for n1 in xrange(len(SelectionChannel)):
								
								if (n1 == 0):
									BinLabel = "Starting Events"
								else:
									BinLabel = "Criterion " + str(n1)
								
								This.HistogramCollection1.Histograms[AbsoluteEfficiencyReference].BinTitles.append([n1 + 1, BinLabel])
								This.HistogramCollection1.Histograms[RelativeEfficiencyReference].BinTitles.append([n1 + 1, BinLabel])
								This.HistogramCollection1.Histograms[PurityReference].BinTitles.append([n1 + 1, BinLabel])
								This.HistogramCollection1.Histograms[NormalisedPurityReference].BinTitles.append([n1 + 1, BinLabel])
								This.HistogramCollection1.Histograms[CutPurityReference].BinTitles.append([n1 + 1, BinLabel])
													
						for CriteriaListCounter in xrange(CutNumber):
											
							if(SelectionChannel[CriteriaListCounter].Purity > 0):
								
								This.HistogramCollection1.Histograms[NormalisedPurityReference].PopulateWeighted("Delta -> p gamma interactions", CriteriaListCounter, SelectionChannel[CriteriaListCounter].Purity, "Delta -> p gamma interactions")
							
							if(SelectionChannel[CriteriaListCounter].PionPurity > 0):
								
								This.HistogramCollection1.Histograms[NormalisedPurityReference].PopulateWeighted("Delta -> p pi interactions", CriteriaListCounter, SelectionChannel[CriteriaListCounter].PionPurity, "Delta -> p pi interactions")
						
							if(SelectionChannel[CriteriaListCounter].RPPurity > 0):
								
								This.HistogramCollection1.Histograms[NormalisedPurityReference].PopulateWeighted("Other Resonance Production", CriteriaListCounter, SelectionChannel[CriteriaListCounter].RPPurity, "Other Resonance Production")
								
							if(SelectionChannel[CriteriaListCounter].QSPurity > 0):
								
								This.HistogramCollection1.Histograms[NormalisedPurityReference].PopulateWeighted("Quasi-Elastic Scattering", CriteriaListCounter, SelectionChannel[CriteriaListCounter].QSPurity, "Quasi-Elastic Scattering")
							
							if(SelectionChannel[CriteriaListCounter].ESPurity > 0):
													
								This.HistogramCollection1.Histograms[NormalisedPurityReference].PopulateWeighted("Elastic Scattering", CriteriaListCounter, SelectionChannel[CriteriaListCounter].ESPurity, "Elastic Scattering")
						
							if(SelectionChannel[CriteriaListCounter].DISPurity > 0):
								
								This.HistogramCollection1.Histograms[NormalisedPurityReference].PopulateWeighted("Deep Inelastic Scattering", CriteriaListCounter, SelectionChannel[CriteriaListCounter].DISPurity, "Deep Inelastic Scattering")
								
							if(SelectionChannel[CriteriaListCounter].CSPurity > 0):
								
								This.HistogramCollection1.Histograms[NormalisedPurityReference].PopulateWeighted("Coherent Scattering", CriteriaListCounter, SelectionChannel[CriteriaListCounter].CSPurity, "Coherent Scattering")
													
							if(SelectionChannel[CriteriaListCounter].OtherPurity > 0):
								
								This.HistogramCollection1.Histograms[NormalisedPurityReference].PopulateWeighted("Other Interactions", CriteriaListCounter, SelectionChannel[CriteriaListCounter].OtherPurity, "Other Interactions")
								
							if(SelectionChannel[CriteriaListCounter].MixedPurity > 0):

								This.HistogramCollection1.Histograms[NormalisedPurityReference].PopulateWeighted("Mixed Events", CriteriaListCounter, SelectionChannel[CriteriaListCounter].MixedPurity, "Mixed Events")
								
							if(SelectionChannel[CriteriaListCounter].MultipleTrackerPurity > 0):

								This.HistogramCollection1.Histograms[NormalisedPurityReference].PopulateWeighted("Multiple Tracker", CriteriaListCounter, SelectionChannel[CriteriaListCounter].MultipleTrackerPurity, "Multiple Tracker Vertex Events")
								
							if(SelectionChannel[CriteriaListCounter].NonTrackerPurity > 0):

								This.HistogramCollection1.Histograms[NormalisedPurityReference].PopulateWeighted("Non Tracker", CriteriaListCounter, SelectionChannel[CriteriaListCounter].NonTrackerPurity, "Non Tracker Vertex Events")
						
					############## Application of truth to criteria
						
						
						for SelectionChannel1 in SelectionChannel:
							This.HistogramCollection1.Histograms[CutPurityReference].Populate("Delta -> p gamma Interactions", SelectionChannel1.TruthDelta, "Delta -> p gamma Interactions")
							This.HistogramCollection1.Histograms[CutPurityReference].Populate("Delta -> p pi interactions", SelectionChannel1.ReconstructedDelta, "Delta -> p pi interactions")							
							This.HistogramCollection1.Histograms[CutPurityReference].Populate("Other Resonance Production", SelectionChannel1.OtherRPInteraction, "Other Resonance Production")							
							This.HistogramCollection1.Histograms[CutPurityReference].Populate("Quasi-Elastic Scattering", SelectionChannel1.QSInteraction, "Quasi-Elastic Scattering")							
							This.HistogramCollection1.Histograms[CutPurityReference].Populate("Elastic Scattering", SelectionChannel1.ESInteraction, "Elastic Scattering")							
							This.HistogramCollection1.Histograms[CutPurityReference].Populate("Deep Inelastic Scattering", SelectionChannel1.DISInteraction, "Deep Inelastic Scattering")							
							This.HistogramCollection1.Histograms[CutPurityReference].Populate("Coherent Scattering", SelectionChannel1.CSInteraction, "Coherent Scattering")							
							This.HistogramCollection1.Histograms[CutPurityReference].Populate("Other Interactions", SelectionChannel1.OtherInteraction, "Other Interactions")							
							This.HistogramCollection1.Histograms[CutPurityReference].Populate("Mixed Events", SelectionChannel1.MixedEvent, "Mixed Events")
							This.HistogramCollection1.Histograms[CutPurityReference].Populate("Multiple Tracker", SelectionChannel1.MultipleTracker, "Multiple Tracker Vertex Events")
							This.HistogramCollection1.Histograms[CutPurityReference].Populate("Non Tracker", SelectionChannel1.NonTracker, "Non Tracker Vertex Events")
						
						
					################# Finalising histograms and writing to file #########
					
					# This is transitional code and will be altered later.
														
					m2 = This.HistogramCollection1.ToHistogramStorage()
					
					for Key1 in m2.keys():
						TimeOutputFile.HistogramDictionary[Key1] = m2[Key1]
						
					TimeOutputFile.Write()
					TimeOutputFile.Close()
								
					del TimeOutputFile
														
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
					This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents7EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPGamma"][7].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents7Delta"].Quantity = This.SelectionDictionary["DeltaPGamma"][7].TruthDelta
					This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents8EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPGamma"][8].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents8Delta"].Quantity = This.SelectionDictionary["DeltaPGamma"][8].TruthDelta
					This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents9EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPGamma"][9].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents9Delta"].Quantity = This.SelectionDictionary["DeltaPGamma"][9].TruthDelta
					
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents10EventsRemaining"].Title = "Selection 10 - Events containing pairs of protons and photons that begin within " + str(This.Parameters["SynchronicityLimit"]) + " ns of each other - Events Remaining"
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents10EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPGamma"][10].EventsRemaining
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents10Delta"].Title = "Selection 10 - Events containing pairs of protons and photons that begin within " + str(This.Parameters["SynchronicityLimit"]) + " ms of each other - Delta -> p gamma Events Remaining"
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents10Delta"].Quantity = This.SelectionDictionary["DeltaPGamma"][10].TruthDelta

					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents11EventsRemaining"].Title = "Selection 11 - Events containing pairs of protons and photons that correlate in angle to within " + str(This.Parameters["PhotonAngularLocalityLimit"]) + " degrees of each other - Events Remaining"
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents11EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPGamma"][11].EventsRemaining
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents11Delta"].Title = "Selection 11 - Fewer than " + str(This.Parameters["PhotonAngularLocalityLimit"]) + " PIDs in total - Delta -> p gamma Events Remaining"
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents11Delta"].Quantity = This.SelectionDictionary["DeltaPGamma"][11].TruthDelta

					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents12EventsRemaining"].Title = "Selection 12 - Fewer than (or equal to) " + str(This.Parameters["ProtonTrackMultiplicityLimitECalChannel"]) + " proton tracks in total - Events Remaining"
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents12EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPGamma"][12].EventsRemaining
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents12Delta"].Title = "Selection 12 - Fewer than (or equal to) " + str(This.Parameters["ProtonTrackMultiplicityLimitECalChannel"]) + " proton tracks in total - Delta -> p gamma Events Remaining"
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents12Delta"].Quantity = This.SelectionDictionary["DeltaPGamma"][12].TruthDelta
					
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents13EventsRemaining"].Title = "Selection 13 - Fewer than (or equal to) " + str(This.Parameters["ECalMultiplicityLimitECalChannel"]) + " ECal clusters in total - Events Remaining"
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents13EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPGamma"][13].EventsRemaining
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents13Delta"].Title = "Selection 13 - Fewer than (or equal to) " + str(This.Parameters["ECalMultiplicityLimitECalChannel"]) + " ECal clusters in total - Delta -> p gamma Events Remaining"
					#This.EfficiencyStatistics_Delta1ToProtonPhoton.Statistics["NEvents13Delta"].Quantity = This.SelectionDictionary["DeltaPGamma"][13].TruthDelta
					
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents0EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][0].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents0Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][0].ReconstructedDelta
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents1EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][1].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents1Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][1].ReconstructedDelta
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents2EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][2].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents2Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][2].ReconstructedDelta
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents3EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][3].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents3Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][3].ReconstructedDelta
					#This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents4EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][4].EventsRemaining
					#This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents4Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][4].ReconstructedDelta
					#This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents5EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][5].EventsRemaining
					#This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents5Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][5].ReconstructedDelta
					#This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents6EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][6].EventsRemaining
					#This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents6Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][6].ReconstructedDelta
					
					#This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents7EventsRemaining"].Title = "Selection 7 - Fewer than " + str(This.Parameters["PathMultiplicityLimit"]) + " PIDs in total - Events Remaining"
					#This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents7EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][7].EventsRemaining
					#This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents7Delta"].Title = "Selection 7 - Fewer than " + str(This.Parameters["PathMultiplicityLimit"]) + " PIDs in total - Delta -> p pi Events Remaining"
					#This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents7Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][7].ReconstructedDelta
					
					#This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents8EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][8].EventsRemaining			
					#This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents8Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][8].ReconstructedDelta
					#This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents9EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][9].EventsRemaining					
					#This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents9Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][9].ReconstructedDelta
					#This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents10EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][10].EventsRemaining
					#This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents10Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][10].ReconstructedDelta
					#This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents11EventsRemaining"].Quantity = This.SelectionDictionary["DeltaPPi"][11].EventsRemaining
					#This.EfficiencyStatistics_Delta1ToProtonPi0.Statistics["NEvents11Delta"].Quantity = This.SelectionDictionary["DeltaPPi"][11].ReconstructedDelta

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

					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents7EventsRemaining"].Title = "Selection 7 - Event contains an electron and positron pair that begin within X: " + str(This.Parameters["LocalityLimit"].X) + " Y: " + str(This.Parameters["LocalityLimit"].Y) + " Z: " + str(This.Parameters["LocalityLimit"].Z) + " (mm) of each other - Events Remaining"
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents7EventsRemaining"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][7].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents7Delta"].Title = "Selection 7 - Event contains an electron and positron pair that begin within X: " + str(This.Parameters["LocalityLimit"].X) + " Y: " + str(This.Parameters["LocalityLimit"].Y) + " Z: " + str(This.Parameters["LocalityLimit"].Z) + " (mm) of each other - Events Remaining"
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents7Delta"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][7].TruthDelta
					
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents8EventsRemaining"].Title = "Selection 8 - Event contains an electron and positron pair that correlate in angle to within " + str(This.Parameters["PairProductionAngularLocalityLimit"]) + " degrees - Events Remaining"
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents8EventsRemaining"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][8].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents8Delta"].Title = "Selection 8 - Event contains an electron and positron pair that correlate in angle to within " + str(This.Parameters["PairProductionAngularLocalityLimit"]) + " degrees - Delta -> p gamma Events Remaining"
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents8Delta"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][8].TruthDelta
					
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents9EventsRemaining"].Title = "Selection 9 - Event contains an electron and positron pair that are within a time synchronicity of " + str(This.Parameters["SynchronicityLimit"]) + " ms - Events Remaining"
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents9EventsRemaining"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][9].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents9Delta"].Title = "Selection 9 - Event contains an electron and positron pair that are within a time synchronicity of " + str(This.Parameters["SynchronicityLimit"]) + " ms - Delta -> p gamma Events Remaining"
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents9Delta"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][9].TruthDelta
					
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents10EventsRemaining"].Title = "Selection 10 - Fewer than (or equal to) " + str(This.Parameters["ProtonTrackMultiplicityLimitPPChannel"]) + " proton tracks in total - Events Remaining"
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents10EventsRemaining"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][10].EventsRemaining
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents10Delta"].Title = "Selection 10 - Fewer than (or equal to) " + str(This.Parameters["ProtonTrackMultiplicityLimitPPChannel"]) + " proton tracks in total - Delta -> p gamma Events Remaining"
					This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents10Delta"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][10].TruthDelta
					
					#This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents11EventsRemaining"].Title = "Selection 11 - Fewer than (or equal to) " + str(This.Parameters["ECalMultiplicityLimitPPChannel"]) + " ECal clusters in total - Events Remaining"
					#This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents11EventsRemaining"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][11].EventsRemaining
					#This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents11Delta"].Title = "Selection 11 - Fewer than (or equal to) " + str(This.Parameters["ECalMultiplicityLimitPPChannel"]) + " ECal clusters in total - Delta -> p gamma Events Remaining"
					#This.EfficiencyStatistics_Delta1ToProtonPhotonPP.Statistics["NEvents11Delta"].Quantity = This.SelectionDictionary["ProtonPhotonToElectrons"][11].TruthDelta

					#####
					if not (float(This.ReconstructedStatistics.Statistics["NPIDsWithCRProton"].Quantity + This.ReconstructedStatistics.Statistics["NPIDsWithIRProton"].Quantity) == 0):
						This.ReconstructedStatistics.Statistics["NPIDsWithRProtonRatio"].Quantity = float(This.ReconstructedStatistics.Statistics["NPIDsWithCRProton"].Quantity) / float(This.ReconstructedStatistics.Statistics["NPIDsWithCRProton"].Quantity + This.ReconstructedStatistics.Statistics["NPIDsWithIRProton"].Quantity)
						
					if not (This.TruthStatistics.Statistics["NDeltaToProtonPhoton"].Quantity == 0):
						This.TruthStatistics.Statistics["NDeltaPairProductionProportion"].Quantity = float(This.TruthStatistics.Statistics["NDeltaEventsWithElectronPositronPairs"].Quantity) / float(This.TruthStatistics.Statistics["NDeltaToProtonPhoton"].Quantity)

					OutputDataFileLocator = FileAdministrator.CreateFilePath(DataLocation, ".output", This.SimulationInformation, "Data/")
										
					OutputDataFileSplit = OutputDataFileLocator.split(".")
					
					OutputDataFileLocation = OutputDataFileSplit[0] + "_I" + str(n10) + "." + OutputDataFileSplit[1]
					
					OutputDataFile = open(OutputDataFileLocation, "w")

					if (i == EventNumber - 1):
									
						del sys.stdout
						del sys.stderr
						
						if (This.MonteCarloFull):
							
							print This.MonteCarloFullTruthStatistics.ToText()
									
						print This.TruthStatistics.ToText()
						print This.ReconstructedStatistics.ToText()
						print This.EfficiencyStatistics_Delta1ToProtonPhoton.ToText()
						print This.EfficiencyStatistics_Delta1ToProtonPi0.ToText()
						print This.EfficiencyStatistics_Delta1ToProtonPhotonPP.ToText()
					
						print TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine, TextConstants.NewLine
						
						if (This.MonteCarloFull):
							
							print OutputDataFile.write(This.MonteCarloFullTruthStatistics.ToText())
						
						OutputDataFile.write(This.TruthStatistics.ToText())
						OutputDataFile.write(This.ReconstructedStatistics.ToText())
						OutputDataFile.write(This.EfficiencyStatistics_Delta1ToProtonPhoton.ToText())
						OutputDataFile.write(This.EfficiencyStatistics_Delta1ToProtonPi0.ToText())
						OutputDataFile.write(This.EfficiencyStatistics_Delta1ToProtonPhotonPP.ToText())
						
					else:
						
						if (This.MonteCarloFull):
							
							OutputDataFile.write(This.MonteCarloFullTruthStatistics.ToText())
						
						OutputDataFile.write(This.TruthStatistics.ToText())
						OutputDataFile.write(This.ReconstructedStatistics.ToText())
						OutputDataFile.write(This.EfficiencyStatistics_Delta1ToProtonPhoton.ToText())
						OutputDataFile.write(This.EfficiencyStatistics_Delta1ToProtonPi0.ToText())
						OutputDataFile.write(This.EfficiencyStatistics_Delta1ToProtonPhotonPP.ToText())
						
					OutputDataFile.close()
						
	
	def InitialiseStatistics(This):
	
		if (This.MonteCarloFull):
			
			This.MonteCarloFullTruthStatistics = Statistics.Collection("Monte Carlo Full Truth Statistics")
			
			This.MonteCarloFullTruthStatistics.NewStatistic("NPEvents", "Number of Processed Events")
			
			This.MonteCarloFullTruthStatistics.NewStatistic("NFullVertices", "Number of vertices in the whole sample")
			This.MonteCarloFullTruthStatistics.NewStatistic("NTrackerVertices", "Number of vertices from Tracker")
			This.MonteCarloFullTruthStatistics.NewStatistic("NFGDVertices", "Number of vertices from FGDs")
			
			This.MonteCarloFullTruthStatistics.NewStatistic("NFullDeltaToProtonPhoton", "Number of Delta -> p gamma events from whole sample")
			This.MonteCarloFullTruthStatistics.NewStatistic("NFullDeltaToProtonPhotonCC", "Number of CC Delta -> p gamma events from whole sample")
			This.MonteCarloFullTruthStatistics.NewStatistic("NFullDeltaToProtonPhotonNC", "Number of NC Delta -> p gamma events from whole sample")
			
			This.MonteCarloFullTruthStatistics.NewStatistic("NTrackerDeltaToProtonPhoton", "Number of Delta -> p gamma events from Tracker")
			This.MonteCarloFullTruthStatistics.NewStatistic("NTrackerDeltaToProtonPhotonCC", "Number of CC Delta -> p gamma events from Tracker")
			This.MonteCarloFullTruthStatistics.NewStatistic("NTrackerDeltaToProtonPhotonNC", "Number of NC Delta -> p gamma events from Tracker")
			
			This.MonteCarloFullTruthStatistics.NewStatistic("NFGDDeltaToProtonPhoton", "Number of Delta -> p gamma events from FGDs")
			This.MonteCarloFullTruthStatistics.NewStatistic("NFGDDeltaToProtonPhotonCC", "Number of CC Delta -> p gamma events from FGDs")
			This.MonteCarloFullTruthStatistics.NewStatistic("NFGDDeltaToProtonPhotonNC", "Number of NC Delta -> p gamma events from FGDs")
			
			
			This.MonteCarloFullTruthStatistics.NewStatistic("NFullDeltaToProtonPion", "Number of Delta -> p pi events from whole sample")
			This.MonteCarloFullTruthStatistics.NewStatistic("NFullDeltaToProtonPionCC", "Number of CC Delta -> p pi events from whole sample")
			This.MonteCarloFullTruthStatistics.NewStatistic("NFullDeltaToProtonPionNC", "Number of NC Delta -> p pi events from whole sample")
			
			This.MonteCarloFullTruthStatistics.NewStatistic("NTrackerDeltaToProtonPion", "Number of Delta -> p pi events from Tracker")
			This.MonteCarloFullTruthStatistics.NewStatistic("NTrackerDeltaToProtonPionCC", "Number of CC Delta -> p pi events from Tracker")
			This.MonteCarloFullTruthStatistics.NewStatistic("NTrackerDeltaToProtonPionNC", "Number of NC Delta -> p pi events from Tracker")
			
			This.MonteCarloFullTruthStatistics.NewStatistic("NFGDDeltaToProtonPion", "Number of Delta -> p pi events from FGDs")
			This.MonteCarloFullTruthStatistics.NewStatistic("NFGDDeltaToProtonPionCC", "Number of CC Delta -> p pi events FGDs")
			This.MonteCarloFullTruthStatistics.NewStatistic("NFGDDeltaToProtonPionNC", "Number of NC Delta -> p pi events FGDs")
			
	
		This.TruthStatistics = Statistics.Collection("Truth Statistics")
				
		This.TruthStatistics.NewStatistic("NPEvents", "Number of Processed Events")
		This.TruthStatistics.NewStatistic("NEvents", "Number of Valid Events")
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
				
		This.ReconstructedStatistics.NewStatistic("NRProtonsInFGD1", "Number of reconstructed protons in FGD 1")
		This.ReconstructedStatistics.NewStatistic("NRProtonsInFGD2", "Number of reconstructed protons in FGD 2")
		This.ReconstructedStatistics.NewStatistic("NRProtonsNotInFGDs", "Number of reconstructed protons not in FGD1 or FGD2")
		This.ReconstructedStatistics.NewStatistic("DNRProtonsInFGD12", "Difference in the number of reconstructed protons in FGDs 1 and 2")
		
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
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents4EventsRemaining", "Selection 4 - No PID activity before FGD1 - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents4Delta", "Selection 4 - No PID activity before FGD1 -  Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents5EventsRemaining", "Selection 5 - At least one proton track begins in the FGD - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents5Delta", "Selection 5 - At least one proton track begins in the FGD - Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents6EventsRemaining", "Selection 6 - No Muon PIDs - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents6Delta", "Selection 6 - No Muon PIDs - Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents7EventsRemaining", "Selection 7 - No Electron PIDs - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents7Delta", "Selection 7 - No Electron PIDs - Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents8EventsRemaining", "Selection 8 - No Positron PIDs - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents8Delta", "Selection 8 - No Positron PIDs - Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents9EventsRemaining", "Selection 9 - At least one ECal cluster - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents9Delta", "Selection 9 - At least one ECal cluster - Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents10EventsRemaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents10Delta")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents11EventsRemaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents11Delta")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents12EventsRemaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents12Delta")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents13EventsRemaining")
		This.EfficiencyStatistics_Delta1ToProtonPhoton.NewStatistic("NEvents13Delta")
		
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
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents4EventsRemaining", "Selection 4 - No PID activity before FGD1 - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents4Delta", "Selection 4 - No PID activity before FGD1 -  Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents5EventsRemaining", "Selection 5 - At least one proton track begins in the FGD - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents5Delta", "Selection 5 - At least one proton track begins in the FGD - Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents6EventsRemaining", "Selection 6 - No Muon PIDs - Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents6Delta", "Selection 6 - No Muon PIDs - Delta -> p gamma Events Remaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents7EventsRemaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents7Delta")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents8EventsRemaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents8Delta")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents9EventsRemaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents9Delta")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents10EventsRemaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents10Delta")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents11EventsRemaining")
		This.EfficiencyStatistics_Delta1ToProtonPhotonPP.NewStatistic("NEvents11Delta")
	
	def InitialiseHistograms(This):
				
		############################################
		# Delta 1 Baryon Data #
		############################################
		
		This.HistogramCollection1.NewHistogram1D("Reconstructed_Delta1Baryon_Energy", "DeltaBaryon/Recon/", "Energy of the Unknown Particle which created the Reconstructed Proton and Photon", "Energy (GeV)", 100, 0, 5000, "Number")
		This.HistogramCollection1.NewHistogram1D("Reconstructed_Delta1Baryon_MomentumModulus", "DeltaBaryon/Recon/", "Momentum Modulus of the Unknown Particle which created the Reconstructed Proton and Photon", "Momentum (GeV)", 100, 0, 3000, "Number")
		This.HistogramCollection1.NewHistogram1D("Reconstructed_Delta1Baryon_Mass", "DeltaBaryon/Recon/", "Mass of the Unknown Particle which created the Reconstructed Proton and Photon", "Mass (GeV)", 100, 0, 3000, "Number")
		
		This.HistogramCollection1.NewHistogram1D("Reconstructed_Delta1Baryon_Energy_TimeSeparated", "DeltaBaryon/Recon/", "Energy of the Unknown Particle which created the Reconstructed Proton and Photon (Time Separated)", "Energy (GeV)", 100, 0, 5000, "Number")
		This.HistogramCollection1.NewHistogram1D("Reconstructed_Delta1Baryon_MomentumModulus_TimeSeparated", "DeltaBaryon/Recon/", "Momentum Modulus of the Unknown Particle which created the Reconstructed Proton and Photon (Time Separated)", "Momentum (GeV)", 100, 0, 3000, "Number")
		This.HistogramCollection1.NewHistogram1D("Reconstructed_Delta1Baryon_Mass_TimeSeparated", "DeltaBaryon/Recon/", "Mass of the Unknown Particle which created the Reconstructed Proton and Photon (Time Separated)", "Mass (GeV)", 100, 0, 3000, "Number")
		
		This.HistogramCollection1.NewHistogram1D("Truth_Delta1Baryon_Energy", "DeltaBaryon/Truth/", "Energy of the Delta 1 Baryons", "Energy (GeV)", 100, 0, 5000, "Number")
		This.HistogramCollection1.NewHistogram1D("Truth_Delta1Baryon_MomentumModulus", "DeltaBaryon/Truth/", "Momentum of the Delta 1 Baryons", "Momentum (GeV)", 100, 0, 3000, "Number")
		This.HistogramCollection1.NewHistogram1D("Truth_Delta1Baryon_Mass", "DeltaBaryon/Truth/", "Mass of the Delta 1 Baryons", "Mass (GeV)", 100, 0, 3000, "Number")
		
		############################################
		# Proton Data #
		############################################
		
		This.HistogramCollection1.NewStackedHistogram1D("Recon_Proton_True_Energy", "Proton/Truth/Energy", "True energy of particles reconstructed as protons", "Energy (GeV)", 100, 0, 5000, "Number")
		
		This.HistogramCollection1.NewStackedHistogram1D("Recon_Proton_Recon_Momentum", "Proton/Recon/Momentum/", "Reconstructed momentum of particles reconstructed as protons", "Momentum (GeV)", 100, 0, 3000, "Number")
			
		This.HistogramCollection1.NewHistogram1D("Recon_Truth_Proton_Momentum", "PIDs/Recon/Momentum", "Recon momentum minus truth momentum for PIDs reconstructed as protons", "Momentum (GeV)", 100, -500, 500, "Number")
		This.HistogramCollection1.NewHistogram1D("Truth_Proton_Momentum", "PIDs/Truth/Momentum", "Truth momentum for PIDs reconstructed as protons", "Momentum (GeV)", 100, 0, 5000, "Number")
				
		############################################
		# Photon Data #
		############################################
				
		This.HistogramCollection1.NewHistogram1D("PhotonAngles", "Photons/Recon/All/", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position", "Angle", 100, 0, 180, "Number")
		This.HistogramCollection1.NewHistogram1D("ProtonPhotonTimeSeparations", "Photons/Recon/", "Time Separation between the Reconstructed Proton Track and Photon EC Cluster", "Time Separation", 100, 0, 4000, "Number")
		This.HistogramCollection1.NewStackedHistogram1D("Photon_Angles_Stacked", "Photons/Recon/All/", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position", "Angle", 100, 0, 180, "Number")
		
		This.HistogramCollection1.NewHistogram1D("SelectedPhotonAngles", "Photons/Recon/Selected/", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position for the single proton and the single selected photon", "Angle", 100, 0, 180, "Number")
		This.HistogramCollection1.NewStackedHistogram1D("Selected_Photon_Angles_Stacked", "Photons/Recon/Selected/", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position for the single proton and the single selected photon", "Angle", 100, 0, 180, "Number")
		
		This.HistogramCollection1.NewStackedHistogram1D("Photon_Angles_Stacked_Track", "Photons/Recon/Track/", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position for the single proton and the single selected photon", "Angle", 100, 0, 180, "Number")
		This.HistogramCollection1.NewStackedHistogram1D("Photon_Angles_Stacked_Shower", "Photons/Recon/Shower/", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position for the single proton and the single selected photon", "Angle", 100, 0, 180, "Number")
		This.HistogramCollection1.NewStackedHistogram1D("Selected_Photon_Angles_Stacked_Track", "Photons/Recon/Selected/Track/", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position for the single proton and the single selected photon", "Angle", 100, 0, 180, "Number")
		This.HistogramCollection1.NewStackedHistogram1D("Selected_Photon_Angles_Stacked_Shower", "Photons/Recon/Selected/Shower/", "Distribution of the angle between the Photon Direction and the start of the Proton Track Position for the single proton and the single selected photon", "Angle", 100, 0, 180, "Number")

		This.HistogramCollection1.NewHistogram1D("PID_Electron_Pull", "PIDs/Recon/Particle Pulls/", "Electron pull for every PID", "Electron Pull", 100, -100, 100, "Number")
		This.HistogramCollection1.NewHistogram1D("PID_Kaon_Pull", "PIDs/Recon/Particle Pulls/", "Kaon pull for every PID", "Kaon Pull", 100, -100, 100, "Number")
		This.HistogramCollection1.NewHistogram1D("PID_Muon_Pull", "PIDs/Recon/Particle Pulls/", "Muon pull for every PID", "Muon Pull", 100, -100, 100, "Number")
		This.HistogramCollection1.NewHistogram1D("PID_Pion_Pull", "PIDs/Recon/Particle Pulls/", "Pion pull for every PID", "Pion Pull", 100, -100, 100, "Number")
		This.HistogramCollection1.NewHistogram1D("PID_Proton_Pull", "PIDs/Recon/Particle Pulls/", "Proton pull for every PID", "Proton Pull", 100, -100, 100, "Number")
		
		This.HistogramCollection1.NewHistogram2D("PID_Proton_Against_Muon_Pull", "PIDs/Recon/Particle Pulls/", "Proton pull plotted against muon pull for every PID", "Proton Pull", 100, -100, 100, "Muon Pull", 100, -100, 100)
		
		This.HistogramCollection1.NewHistogram1D("Proton_PID_Electron_Pull", "Proton/Recon/Particle Pulls/All Protons/", "Electron pull for all PIDs identified as proton-like", "Electron Pull", 100, -100, 100, "Number")
		This.HistogramCollection1.NewHistogram1D("Proton_PID_Kaon_Pull", "Proton/Recon/Particle Pulls/All Protons/", "Kaon pull for all PIDs identified as proton-like", "Kaon Pull", 100, -100, 100, "Number")
		This.HistogramCollection1.NewHistogram1D("Proton_PID_Muon_Pull", "Proton/Recon/Particle Pulls/All Protons/", "Muon pull for all PIDs identified as proton-like", "Muon Pull", 100, -100, 100, "Number")
		This.HistogramCollection1.NewHistogram1D("Proton_PID_Pion_Pull", "Proton/Recon/Particle Pulls/All Protons/", "Pion pull for all PIDs identified as proton-like", "Pion Pull", 100, -100, 100, "Number")
		This.HistogramCollection1.NewHistogram1D("Proton_PID_Proton_Pull", "Proton/Recon/Particle Pulls/All Protons/", "Proton pull for all PIDs identified as proton-like", "Proton Pull", 100, -100, 100, "Number")
		
		This.HistogramCollection1.NewHistogram2D("Proton_PID_Proton_Against_Muon_Pull", "Proton/Recon/Particle Pulls/All Protons/", "Proton pull plotted against muon pull for all PIDs identified as proton-like", "Proton Pull", 100, -100, 100, "Muon Pull", 100, -100, 100)
		This.HistogramCollection1.Histograms["Proton_PID_Proton_Against_Muon_Pull"].MarkerStyle = 8
		
		This.HistogramCollection1.NewHistogram1D("Single_Proton_PID_Electron_Pull", "Proton/Recon/Particle Pulls/Single Proton/", "Electron pull for single PIDs identified as proton-like", "Electron Pull", 100, -100, 100, "Number")
		This.HistogramCollection1.NewHistogram1D("Single_Proton_PID_Kaon_Pull", "Proton/Recon/Particle Pulls/Single Proton/", "Kaon pull for single PIDs identified as proton-like", "Kaon Pull", 100, -100, 100, "Number")
		This.HistogramCollection1.NewHistogram1D("Single_Proton_PID_Muon_Pull", "Proton/Recon/Particle Pulls/Single Proton/", "Muon pull for single PIDs identified as proton-like", "Muon Pull", 100, -100, 100, "Number")
		This.HistogramCollection1.NewHistogram1D("Single_Proton_PID_Pion_Pull", "Proton/Recon/Particle Pulls/Single Proton/", "Pion pull for single PIDs identified as proton-like", "Pion Pull", 100, -100, 100, "Number")
		This.HistogramCollection1.NewHistogram1D("Single_Proton_PID_Proton_Pull", "Proton/Recon/Particle Pulls/Single Proton/", "Proton pull for single PIDs identified as proton-like", "Proton Pull", 100, -100, 100, "Number")
		
		This.HistogramCollection1.NewHistogram2D("Single_Proton_PID_Proton_Against_Muon_Pull", "Proton/Recon/Particle Pulls/Single Proton/", "Proton pull plotted against muon pull for single PIDs identified as proton-like", "Proton Pull", 100, -100, 100, "Muon Pull", 100, -100, 100)
		This.HistogramCollection1.Histograms["Proton_PID_Proton_Against_Muon_Pull"].MarkerStyle = 8
		
		This.HistogramCollection1.NewStackedHistogram1D("Proton_Photon_Synchronicity", "Photons/Recon/Synchronicity/", "Distribution of the time separation between proton tracks and photon ECal clusters", "Time separation (ns)", 100, 0, This.Parameters["SynchronicityLimit"] * 5, "Number")
		
		############################################
		# Electron-Antielectron Data #
		############################################
		
		This.HistogramCollection1.NewHistogram1D("ElectronsAndAntielectrons_SeparationX", "Photons/ElectronsAndAntielectrons/", "Electron positron separation in X axis", "Separation (mm)", 100, 0, This.Parameters["LocalityLimit"].X * 10, "Number")
		This.HistogramCollection1.NewHistogram1D("ElectronsAndAntielectrons_SeparationY", "Photons/ElectronsAndAntielectrons/", "Electron positron separation in Y axis", "Separation (mm)", 100, 0, This.Parameters["LocalityLimit"].Y * 10, "Number")
		This.HistogramCollection1.NewHistogram1D("ElectronsAndAntielectrons_SeparationZ", "Photons/ElectronsAndAntielectrons/", "Electron positron separation in Z axis", "Separation (mm)", 100, 0, This.Parameters["LocalityLimit"].Z * 10, "Number")
		This.HistogramCollection1.NewStackedHistogram1D("ElectronsAndAntielectrons_Separation_StackedX", "Photons/ElectronsAndAntielectrons/", "Separation in X axis between electrons and antielectrons", "Separation (mm)", 100, 0, This.Parameters["LocalityLimit"].X * 10, "Number")
		This.HistogramCollection1.NewStackedHistogram1D("ElectronsAndAntielectrons_Separation_StackedY", "Photons/ElectronsAndAntielectrons/", "Separation in Y axis between electrons and antielectrons", "Separation (mm)", 100, 0, This.Parameters["LocalityLimit"].Y * 10, "Number")
		This.HistogramCollection1.NewStackedHistogram1D("ElectronsAndAntielectrons_Separation_StackedZ", "Photons/ElectronsAndAntielectrons/", "Separation in Z axis between electrons and antielectrons", "Separation (mm)", 100, 0, This.Parameters["LocalityLimit"].Z * 10, "Number")
		
		This.HistogramCollection1.NewHistogram1D("ElectronsAndAntielectrons_InvariantMass", "Photons/ElectronsAndAntielectrons/", "Invariant Mass Distribution of Electron-Positron Pairs", "Mass (MeV)", 100, -100, 100, "Number")
		
		############################################
		# Mu Lepton Data #
		############################################
		
		This.HistogramCollection1.NewStackedHistogram1D("Proton_Muon_Separation", "MuLeptons/", "Separation between the single proton and single mu lepton in suitable events", "Separation (cm)", 100, 0, int(This.Parameters["MuonProtonLocalityLimit"] * 5), "Number")	
				
		############################################
		# Multiplicities #
		############################################
		
		This.HistogramCollection1.NewHistogram1D("ProtonTrackMultiplicityECal", "Proton/Recon/Multiplicity/", "Proton track multiplicity for events that have a proton and photon within angle and synchronicity", "Multiplicity", 10, 0, 10, "Number")
		This.HistogramCollection1.NewHistogram1D("ECalMultiplicityECal", "Photons/Recon/Multiplicity/", "ECal multiplicity for events that have a proton and photon within angle and synchronicity", "Multiplicity", 10, 0, 10, "Number")
		
		This.HistogramCollection1.NewHistogram1D("ProtonTrackMultiplicityPP", "Proton/Recon/Multiplicity/", "Proton track multiplicity for events that have a proton and photon within angle and synchronicity", "Multiplicity", 10, 0, 10, "Number")
		This.HistogramCollection1.NewHistogram1D("ECalMultiplicityPP", "Photons/Recon/Multiplicity/", "ECal multiplicity for events that have a proton and photon within angle and synchronicity", "Multiplicity", 10, 0, 10, "Number")
				
		This.HistogramCollection1.NewStackedHistogram1D("Single_Proton_PID_Multiplicity", "Proton/", "PID multiplicity for events with single proton tracks", "Multiplicity", 10, 0, 10, "Number")
		This.HistogramCollection1.NewStackedHistogram1D("Single_Proton_ECal_Multiplicity", "Photons/", "Calorimeter multiplicity for events with single proton tracks", "Multiplicity", 10, 0, 10, "Number")	
		
		############################################
		# Pulls #
		############################################
		
		This.HistogramCollection1.NewStackedHistogram1D("ElectronPull", "PIDs/Reconstructed/Particle Pulls/", "Electron pull for all reconstructed objects", "Pull", 100, -100, 100, "Number")	
		This.HistogramCollection1.NewStackedHistogram1D("KaonPull", "PIDs/Reconstructed/Particle Pulls/", "Kaon pull for all reconstructed objects", "Pull", 100, -100, 100, "Number")	
		This.HistogramCollection1.NewStackedHistogram1D("MuonPull", "PIDs/Reconstructed/Particle Pulls/", "Muon pull for all reconstructed objects", "Pull", 100, -100, 100, "Number")	
		This.HistogramCollection1.NewStackedHistogram1D("PionPull", "PIDs/Reconstructed/Particle Pulls/", "Pion pull for all reconstructed objects", "Pull", 100, -100, 100, "Number")	
		This.HistogramCollection1.NewStackedHistogram1D("ProtonPull", "PIDs/Reconstructed/Particle Pulls/", "Proton pull for all reconstructed objects", "Pull", 100, -100, 100, "Number")	
		
		
		This.HistogramCollection1.NewStackedHistogram1D("Final_Invariant_Mass", "Selections/DeltaPGamma/Invariant Mass/", "Invariant Mass of Delta Baryon after all cuts have been applied", "Mass (GeV)", 100, 0, 3000, "Number")
		This.HistogramCollection1.NewStackedHistogram1D("Invariant_Mass_All_ECal", "Selections/DeltaPGamma/Invariant Mass/All ECal/", "Invariant Mass of Delta Baryon from comparison of single photon to all ECals", "Mass (GeV)", 100, 0, 3000, "Number")
		
		This.HistogramCollection1.NewStackedHistogram1D("Pi0_Meson_Mass", "Pi0Meson/Invariant Mass/", "Invariant Mass of Pi0 Meson from matching of ECal clusters", "Mass (GeV)", 100, 0, 1000, "Number")
		
	
	def runEvent(This):

		This.TruthStatistics.Statistics["NEvents"].Quantity += 1
	
		NVertices = This.Truth_GRTVertices.NVtx	
		
		########################################################################################################################
		# TRUTH DATA #
		########################################################################################################################
		
		TrueDelta1Baryons = []
		
		TrueProtons = []
		TruePi0Mesons = []
		
		TrueElectrons = []
		TrueAntielectrons = []
		TrueElectronAntielectronPairs = []
		DeltaVertexList = []
		
		TrueMuLeptons = []
		
		TrackerTrueInteractions = []
		
		EventContainsElectrons = False
		EventContainsAntielectrons = False
		EventContainsElectronAntielectronPairs = False
		EventContainsMuLeptons = False
		
		TrueEventContainsDelta1ToProtonPhoton = False
		TrueEventContainsDelta1ToProtonPi0 = False
		
		InteractionType = ""

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

			for Vertex1 in This.Truth_Vertices.Vertices:
				
				if (GRTVertex1.TruthVertexID == Vertex1.ID):#See ToaAnalysisUtils.cxx in Code Archive, looking for TPC or FGD
					
					if ((Vertex1.Subdetector == 0) or (Vertex1.Subdetector == 1) or (Vertex1.Subdetector == 6) or (Vertex1.Subdetector == 7) or (Vertex1.Subdetector == 8)):

						TrueInteraction = Particles.EventProcess(DeltaPGammaInteraction, Delta1BaryonToProtonPi0MesonInteraction, TruthInteractionType)
						
						TrackerTrueInteractions.append(TrueInteraction)
		
		if (TrueEventContainsDelta1ToProtonPhoton):# Looking for a Delta -> p gamma anywhere
			
			TrueEventInteraction = "DeltaPGamma"
			
		elif (TrueEventContainsDelta1ToProtonPi0):
			
			TrueEventInteraction = "DeltaPPi"
			
		else:
		
			if (len(TrackerTrueInteractions) == 1):# One interaction in Tracker
				
				TrueEventInteraction = TrackerTrueInteractions[0]
				
			elif (len(TrackerTrueInteractions) > 1):# Multiple Tracker interactions, happens rarely

				TrueEventInteraction = "MultipleTrackerBackgroundInteractions"				
				
			elif (len(TrackerTrueInteractions) == 0):# Interactions not in Tracker, happens sometimes
				
				TrueEventInteraction = "NonTrackerInteraction"
			
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

		####################################################################################################################################
		# RECONSTRUCTED DATA #
		####################################################################################################################################

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
		
		FGD1Protons = []
		FGD2Protons = []
		
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
		
		EarliestZPID = 9999999999
				
		ProtonIsCorrectlyReconstructed = False
		ProtonIsIncorrectlyReconstructed = False
		
		NumberOfCorrectlyReconstructedProtons = 0
		NumberOfIncorrectlyReconstructedProtons = 0
		
		MuonTrackIsHighestEnergy = False
		
		SingleProtonTrackFirst = False
		SingleProtonInFGDFiducial = False
		ProtonSelected = False
		
		ProtonsInFGD1 = False
		ProtonsInFGD2 = False
		
		EventContainsElectron = False
		EventContainsPositron = False
		EventContainsMuon = False
				
		############################################
		# TPC and FGD Track Objects #
		############################################
		
		for PID in This.Reconstructed_Global.PIDs: # Loop over the PIDs if they exist
			
			This.ReconstructedStatistics.Statistics["PIDNumber"].Quantity += 1
			PIDNumber += 1

			SuitableTPCNodeNumber = False
										
			for TPCTrack1 in PID.TPC: # Loop over TPC PIDs				
				if (TPCTrack1.NNodes > 18):
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

				(ReconstructedObject1.TrueGRTVertex, ReconstructedObject1.TrueVertex, ReconstructedObject1.TrueTrajectory) = PIDTruth(This.Truth_GRTVertices.Vtx, This.Truth_Vertices.Vertices, This.Truth_Trajectories.Trajectories, PID)

				######### For particle pulls - There are possibly multiple TPCs with different pulls for track, so this code looks for the TPC with the most nodes
						
				HighestTPCNodeNumber = 0
						
				for i, TPCTrack1 in enumerate(PID.TPC):
					if (TPCTrack1.NNodes > HighestTPCNodeNumber):
						
						HighestTPCNodeNumber = TPCTrack1.NNodes#!! Correction here, this loop was not working
						BestTPCTrack = i

				for j , TPCTrack1 in enumerate(PID.TPC):
					if (j == BestTPCTrack):
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
								
				if (ReconstructedObject1.TrueParticleID in ParticleCodes.ParticleDictionary.keys()):
					
					This.HistogramCollection1.Histograms["ElectronPull"].Populate(ReconstructedObject1.TrueParticleID, ReconstructedObject1.ParticlePull[ParticleCodes.Electron], str(ParticleCodes.ParticleDictionary[ReconstructedObject1.TrueParticleID]))
					This.HistogramCollection1.Histograms["KaonPull"].Populate(ReconstructedObject1.TrueParticleID, ReconstructedObject1.ParticlePull[ParticleCodes.K1Meson], str(ParticleCodes.ParticleDictionary[ReconstructedObject1.TrueParticleID]))
					This.HistogramCollection1.Histograms["MuonPull"].Populate(ReconstructedObject1.TrueParticleID, ReconstructedObject1.ParticlePull[ParticleCodes.MuLepton], str(ParticleCodes.ParticleDictionary[ReconstructedObject1.TrueParticleID]))
					This.HistogramCollection1.Histograms["PionPull"].Populate(ReconstructedObject1.TrueParticleID, ReconstructedObject1.ParticlePull[ParticleCodes.Pi1Meson], str(ParticleCodes.ParticleDictionary[ReconstructedObject1.TrueParticleID]))
					This.HistogramCollection1.Histograms["ProtonPull"].Populate(ReconstructedObject1.TrueParticleID, ReconstructedObject1.ParticlePull[ParticleCodes.Proton], str(ParticleCodes.ParticleDictionary[ReconstructedObject1.TrueParticleID]))

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

			if (ReconstructedObject1.ReconFrontDirectionZ < EarliestZPID):

				EarliestZPID = ReconstructedObject1.FrontPosition.Z

			This.HistogramCollection1.Histograms["PID_Electron_Pull"].Populate(ReconstructedObject1.ParticlePull[ParticleCodes.Electron])
			This.HistogramCollection1.Histograms["PID_Kaon_Pull"].Populate(ReconstructedObject1.ParticlePull[ParticleCodes.K1Meson])
			This.HistogramCollection1.Histograms["PID_Muon_Pull"].Populate(ReconstructedObject1.ParticlePull[ParticleCodes.MuLepton])
			This.HistogramCollection1.Histograms["PID_Pion_Pull"].Populate(ReconstructedObject1.ParticlePull[ParticleCodes.Pi1Meson])
			This.HistogramCollection1.Histograms["PID_Proton_Pull"].Populate(ReconstructedObject1.ParticlePull[ParticleCodes.Proton])
			
			This.HistogramCollection1.Histograms["PID_Proton_Against_Muon_Pull"].Populate(ReconstructedObject1.ParticlePull[ParticleCodes.Proton],ReconstructedObject1.ParticlePull[ParticleCodes.MuLepton])
									
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
									
				This.HistogramCollection1.Histograms["Recon_Truth_Proton_Momentum"].Populate(ReconstructedObject1.ReconTrueMomentumDifference())	
				This.HistogramCollection1.Histograms["Truth_Proton_Momentum"].Populate(ReconstructedObject1.TrueFrontMomentum)
					
				Proton1.Position.T = ReconstructedObject1.FrontPosition.T
				Proton1.Position.X = ReconstructedObject1.FrontPosition.X
				Proton1.Position.Y = ReconstructedObject1.FrontPosition.Y
				Proton1.Position.Z = ReconstructedObject1.FrontPosition.Z
				
				Proton1.TrueTrajectory = ReconstructedObject1.TrueTrajectory
				Proton1.TrueGRTVertex = ReconstructedObject1.TrueGRTVertex
							
				Proton1.GetProcess(This.RTTools)
				
				ReconstructedProtons1.append(Proton1)
				
				This.HistogramCollection1.Histograms["Proton_PID_Electron_Pull"].Populate(ReconstructedObject1.ParticlePull[ParticleCodes.Electron])
				This.HistogramCollection1.Histograms["Proton_PID_Kaon_Pull"].Populate(ReconstructedObject1.ParticlePull[ParticleCodes.K1Meson])
				This.HistogramCollection1.Histograms["Proton_PID_Muon_Pull"].Populate(ReconstructedObject1.ParticlePull[ParticleCodes.MuLepton])
				This.HistogramCollection1.Histograms["Proton_PID_Pion_Pull"].Populate(ReconstructedObject1.ParticlePull[ParticleCodes.Pi1Meson])
				This.HistogramCollection1.Histograms["Proton_PID_Proton_Pull"].Populate(ReconstructedObject1.ParticlePull[ParticleCodes.Proton])
				
				This.HistogramCollection1.Histograms["Proton_PID_Proton_Against_Muon_Pull"].Populate(ReconstructedObject1.ParticlePull[ParticleCodes.Proton],ReconstructedObject1.ParticlePull[ParticleCodes.MuLepton])
				
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
				Muon1.TrueGRTVertex = ReconstructedObject1.TrueGRTVertex					
				
				Muon1.GetProcess(This.RTTools)
				
				ReconstructedMuLeptons1.append(Muon1)
				
			if (ReconstructedObject1.ReconParticleID == ParticleCodes.Electron):
				NumberOfReconstructedElectronTracks += 1
				
			if (ReconstructedObject1.ReconParticleID == ParticleCodes.AntiElectron):
				NumberOfReconstructedAntiElectronTracks += 1
				
			############## Incorrect reconstructions #############
				
			if (ReconstructedObject1.TrueParticleID == ParticleCodes.Proton and ReconstructedObject1.ReconParticleID == ParticleCodes.Proton):
				NumberOfCorrectlyReconstructedProtons += 1
				
				This.ReconstructedStatistics.Statistics["NPIDsWithCRProton"].Quantity += 1
				
			elif (ReconstructedObject1.ReconParticleID == ParticleCodes.Proton):
				NumberOfIncorrectlyReconstructedProtons += 1
				This.ReconstructedStatistics.Statistics["NPIDsWithIRProton"].Quantity += 1
	
			if (ReconstructedObject1.ReconParticleID == ParticleCodes.Proton):
				if (ReconstructedObject1.TrueParticleID in ParticleCodes.ParticleDictionary.keys()):
					
					This.HistogramCollection1.Histograms["Recon_Proton_True_Energy"].Populate(ReconstructedObject1.TrueParticleID, ReconstructedObject1.TrueEnergy, ParticleCodes.ParticleDictionary[ReconstructedObject1.TrueParticleID])
					This.HistogramCollection1.Histograms["Recon_Proton_Recon_Momentum"].Populate(ReconstructedObject1.TrueParticleID, ReconstructedObject1.ReconFrontMomentum, ParticleCodes.ParticleDictionary[ReconstructedObject1.TrueParticleID])

				
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
				
		############################################
		# Proton Track Multiplicity Comparison for FGDs 1 and 2 #
		############################################
		
		# For those tracks which have been reconstructed as protons, see which FGD they occurred in, and add to the statistics collection.
		
		""""""
				
		for Proton1 in ReconstructedProtons1:	

			if (This.FGD1Fiducial.Contains(Proton1.Position.X, Proton1.Position.Y, Proton1.Position.Z) == True):
				ProtonsInFGD1 = True
				This.ReconstructedStatistics.Statistics["NRProtonsInFGD1"].Quantity += 1
				
				FGD1Protons.append(Proton1)

			elif (This.FGD2Fiducial.Contains(Proton1.Position.X, Proton1.Position.Y, Proton1.Position.Z) == True):
				ProtonsInFGD2 = True
				This.ReconstructedStatistics.Statistics["NRProtonsInFGD2"].Quantity += 1
				
				FGD2Protons.append(Proton1)
				
			else:
				This.ReconstructedStatistics.Statistics["NRProtonsNotInFGDs"].Quantity += 1
		
		This.ReconstructedStatistics.Statistics["DNRProtonsInFGD12"].Quantity = This.ReconstructedStatistics.Statistics["NRProtonsInFGD1"].Quantity - This.ReconstructedStatistics.Statistics["NRProtonsInFGD2"].Quantity
			
		if (len(FGD1Protons) == 0):# For later on when we loop over these protons
			
			FGDProtons = FGD2Protons
			
		else:
			
			FDGProtons = FGD1Protons
			
		############################################
		# Untitled Section #
		############################################			
		
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
	
					
					This.HistogramCollection1.Histograms["Single_Proton_PID_Electron_Pull"].Populate(ReconstructedObject1.ParticlePull[ParticleCodes.Electron])
					This.HistogramCollection1.Histograms["Single_Proton_PID_Kaon_Pull"].Populate(ReconstructedObject1.ParticlePull[ParticleCodes.K1Meson])
					This.HistogramCollection1.Histograms["Single_Proton_PID_Muon_Pull"].Populate(ReconstructedObject1.ParticlePull[ParticleCodes.MuLepton])
					This.HistogramCollection1.Histograms["Single_Proton_PID_Pion_Pull"].Populate(ReconstructedObject1.ParticlePull[ParticleCodes.Pi1Meson])
					This.HistogramCollection1.Histograms["Single_Proton_PID_Proton_Pull"].Populate(ReconstructedObject1.ParticlePull[ParticleCodes.Proton])
					
					This.HistogramCollection1.Histograms["Single_Proton_PID_Proton_Against_Muon_Pull"].Populate(ReconstructedObject1.ParticlePull[ParticleCodes.Proton], ReconstructedObject1.ParticlePull[ParticleCodes.MuLepton])
					
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

						This.HistogramCollection1.Histograms["Photon_Angles_Stacked_Shower"].Populate(Proton1.Process, Angle1, Proton1.Process)
					
					if (len(ReconstructedProtons1) == 1):
						
						Proton1 = ReconstructedProtons1[0]
						
						Angle1 = AngleBetweenDirections(Proton1.Position, Photon1.Position, ECUnitDirection)

						if (math.fabs(Angle1) < math.fabs(SmallestAngle)):
							
							SmallestAngle = Angle1
						
						This.HistogramCollection1.Histograms["Selected_Photon_Angles_Stacked_Shower"].Populate(Proton1.Process, SmallestAngle, Proton1.Process)
					
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

						This.HistogramCollection1.Histograms["Photon_Angles_Stacked_Track"].Populate(Proton1.Process, Angle1, Proton1.Process)
						
					if (len(ReconstructedProtons1) == 1):
												
						Proton1 = ReconstructedProtons1[0]
						
						Angle1 = AngleBetweenDirections(Proton1.Position, Photon1.Position, ECUnitDirection)	
						
						if (math.fabs(Angle1) < math.fabs(SmallestAngle)):
							
							SmallestAngle = Angle1
						
						This.HistogramCollection1.Histograms["Selected_Photon_Angles_Stacked_Track"].Populate(Proton1.Process, SmallestAngle, Proton1.Process)
					
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
		

		#################### Toms new photon cut section ####### Currently we have many potential photons and a single proton.
		# First, the photon with the "best" angle (smallest) is chosen as the single photon ... then we can look at invariant mass
		
		SmallestAngle = 180
		DeltaBaryonMass = 0
		
		PionMassCondition = False
		
		for ReconstructedProton1 in ReconstructedProtons1:
			
			for ReconstructedPhoton1 in ReconstructedPhotons1:
			
				Angle1 = AngleBetweenDirections(ReconstructedProton1.Position, ReconstructedPhoton1.Position, ReconstructedPhoton1.Direction)
				
				TimeSeparation = math.fabs(float(ReconstructedProton1.Position.T) - float(ReconstructedPhoton1.Position.T))
				
				This.HistogramCollection1.Histograms["Proton_Photon_Synchronicity"].Populate(ReconstructedProton1.Process, TimeSeparation, ReconstructedProton1.Process)
				
				if (TimeSeparation < This.Parameters["SynchronicityLimit"]):
					
					NumberOfProtonsAndPhotonsWithinSynchronicity += 1
					
				if (math.fabs(Angle1) < math.fabs(SmallestAngle)):
						
					NumberOfProtonsAndPhotonsWithinAngle += 1
					
		for ReconstructedPhoton1 in ReconstructedPhotons1:
			
			for ReconstructedPhoton2 in ReconstructedPhotons1:
				
				Pi0Meson = Geometry.FourVector()
							
				Pi0Meson = ReconstructedPhoton1.EnergyMomentum + ReconstructedPhoton2.EnergyMomentum
							
				This.HistogramCollection1.Histograms["Pi0_Meson_Mass"].Populate(TrueEventInteraction, Pi0Meson.InvariantModulus(), str(TrueEventInteraction))
				
				if (math.fabs(Pi0Meson.InvariantModulus() - 135) < This.Parameters["Pi0MesonMassCut"]):
					
					PionMassCondition = True
				
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
		
		DeltaPGammaCriteria = [True, False, False, False, False, False, False, False, False, False, False, False, False]
				
		if (PIDNumber > 0):
			DeltaPGammaCriteria[1] = True
		
		if (TPCValidPIDNumber > 0 and DeltaPGammaCriteria[1]):
			DeltaPGammaCriteria[2] = True
					
		if (NumberOfReconstructedProtonTracks > 0 and DeltaPGammaCriteria[2]):
			DeltaPGammaCriteria[3] = True
		
		#if ((EarliestZPID > This.FGD1.Z1) and DeltaPGammaCriteria[3]):
		#	DeltaPGammaCriteria[4] = True
			
		if ((ProtonsInFGD1 or ProtonsInFGD2) and DeltaPGammaCriteria[3]):
			DeltaPGammaCriteria[4] = True
				
		if (NumberOfReconstructedMuLeptonTracks <= This.Parameters["MuonMultiplicityCut"] and DeltaPGammaCriteria[4]):
			DeltaPGammaCriteria[5] = True
			
		if (NumberOfReconstructedElectronTracks <= This.Parameters["ElectronMultiplicityCut"] and DeltaPGammaCriteria[5]):
			DeltaPGammaCriteria[6] = True	
		
		if (NumberOfReconstructedAntiElectronTracks <= This.Parameters["PositronMultiplicityCut"] and DeltaPGammaCriteria[6]):
			DeltaPGammaCriteria[7] = True
		
		if ((NTrackerECalRecon > 0) and DeltaPGammaCriteria[7]):
			DeltaPGammaCriteria[8] = True
		
		if ((NumberOfProtonsAndPhotonsWithinSynchronicity > 0) and DeltaPGammaCriteria[8]):
			DeltaPGammaCriteria[9] = True
			
		if ((NumberOfProtonsAndPhotonsWithinAngle > 0) and DeltaPGammaCriteria[9]):
			DeltaPGammaCriteria[10] = True
			
		if (NumberOfReconstructedProtonTracks <= This.Parameters["ProtonTrackMultiplicityLimitECalChannel"] and DeltaPGammaCriteria[10]):
			DeltaPGammaCriteria[11] = True
			
		if (NTrackerECalRecon <= This.Parameters["ECalMultiplicityLimitECalChannel"] and DeltaPGammaCriteria[11]):
			DeltaPGammaCriteria[12] = True
		
		DeltaPGammaProtonSelectionCut = 0
					
		DeltaPGammaCutNumber = len(DeltaPGammaCriteria)
		
		#### P Pi0
		
		DeltaPPiCriteria = [True, False, False, False]
				
		#if (PIDNumber > 0):
		#	DeltaPPiCriteria[1] = True
		
		#if (TPCValidPIDNumber > 0 and DeltaPPiCriteria[1]):
		#	DeltaPPiCriteria[2] = True
					
		#if (NumberOfReconstructedProtonTracks > 0 and DeltaPPiCriteria[2]):
		#	DeltaPPiCriteria[3] = True
		
		#if (NumberOfReconstructedProtonTracks == 1 and DeltaPPiCriteria[3]):
		#	DeltaPPiCriteria[4] = True
		
		DeltaPPiProtonSelectionCut = 0
		
		#if (SingleProtonTrackFirst and DeltaPPiCriteria[4]):
		#	DeltaPPiCriteria[5] = True
		
		#if (SingleProtonInFGDFiducial and DeltaPPiCriteria[5]):
		#	DeltaPPiCriteria[6] = True
			
		#if ((len(ReconstructedObjects1) <= This.Parameters["PathMultiplicityLimit"]) and DeltaPPiCriteria[6]):
		#	DeltaPPiCriteria[7] = True
		
		#if (NumberOfReconstructedMuLeptonTracks == 0 and DeltaPPiCriteria[7]):
		#	DeltaPPiCriteria[8] = True
			
		#if (NumberOfReconstructedElectronTracks == 0 and DeltaPPiCriteria[8]):
		#	DeltaPPiCriteria[9] = True	
		
		#if (NumberOfReconstructedAntiElectronTracks == 0 and DeltaPPiCriteria[9]):
		#	DeltaPPiCriteria[10] = True	
		
		if (NTrackerECalRecon > 0):
			DeltaPPiCriteria[1] = True

		if (PionMassCondition and DeltaPPiCriteria[1]):
			DeltaPPiCriteria[2] = True
		
		if (NumberOfReconstructedProtonTracks > 0 and DeltaPPiCriteria[2]):
			DeltaPPiCriteria[3] = True
		
		DeltaPPiCutNumber = len(DeltaPPiCriteria)
		
		EventContainsElectronPositronPair = False
		ElectronPositronPairPointsWithinAngle = False
		ElectronPositronPairPointsWithinTime = False

		ProtonPhotonToElectrons = [True, False, False, False, False, False, False, False, False, False, False]
		
		if (PIDNumber > 0):
			ProtonPhotonToElectrons[1] = True
		
		if (TPCValidPIDNumber > 0 and ProtonPhotonToElectrons[1]):
			ProtonPhotonToElectrons[2] = True
					
		if (NumberOfReconstructedProtonTracks > 0 and ProtonPhotonToElectrons[2]):
			ProtonPhotonToElectrons[3] = True
		
		#if ((EarliestZPID > This.FGD1.Z1) and ProtonPhotonToElectrons[3]):
		#	ProtonPhotonToElectrons[4] = True
			
		if ((ProtonsInFGD1 or ProtonsInFGD2) and ProtonPhotonToElectrons[3]):
			ProtonPhotonToElectrons[4] = True
				
		if (NumberOfReconstructedMuLeptonTracks <= This.Parameters["MuonMultiplicityCut"] and ProtonPhotonToElectrons[4]):
			ProtonPhotonToElectrons[5] = True
		
			(EventContainsElectronPositronPair, ElectronPositronPairPointsWithinAngle, ElectronPositronPairPointsWithinTime) = This.EventContainsElectronPositron(ReconstructedObjects1, ReconstructedProtons1, None)
				
		if (EventContainsElectronPositronPair and ProtonPhotonToElectrons[5]):
			ProtonPhotonToElectrons[6] = True
			
		if (ElectronPositronPairPointsWithinAngle >= 1 and ProtonPhotonToElectrons[6]):
			ProtonPhotonToElectrons[7] = True
		
		if (ElectronPositronPairPointsWithinTime >= 1 and ProtonPhotonToElectrons[7]):
			ProtonPhotonToElectrons[8] = True
			
		if (NumberOfReconstructedProtonTracks <= This.Parameters["ProtonTrackMultiplicityLimitPPChannel"] and ProtonPhotonToElectrons[8]):
			ProtonPhotonToElectrons[9] = True
			
		if (NTrackerECalRecon <= This.Parameters["ECalMultiplicityLimitPPChannel"] and ProtonPhotonToElectrons[9]):
			ProtonPhotonToElectrons[10] = True
		
		ProtonPhotonToElectronsProtonSelectionCut = 0
		
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

					if (TrueEventInteraction == "DeltaPGamma"):
						This.SelectionDictionary["DeltaPGamma"][CutCounter].TruthDelta += 1
					elif (TrueEventInteraction == "DeltaPPi"):
						This.SelectionDictionary["DeltaPGamma"][CutCounter].ReconstructedDelta += 1
					elif (TrueEventInteraction == "OtherResonance"):
						This.SelectionDictionary["DeltaPGamma"][CutCounter].OtherRPInteraction += 1
					elif (TrueEventInteraction == "QS"):
						This.SelectionDictionary["DeltaPGamma"][CutCounter].QSInteraction += 1
					elif (TrueEventInteraction == "ES"):
						This.SelectionDictionary["DeltaPGamma"][CutCounter].ESInteraction += 1
					elif (TrueEventInteraction == "DIS"):
						This.SelectionDictionary["DeltaPGamma"][CutCounter].DISInteraction += 1
					elif (TrueEventInteraction == "C"):
						This.SelectionDictionary["DeltaPGamma"][CutCounter].CSInteraction += 1
					elif (TrueEventInteraction == "MultipleTrackerBackgroundInteractions"):
						This.SelectionDictionary["DeltaPGamma"][CutCounter].MultipleTracker += 1
					elif (TrueEventInteraction == "NonTrackerInteraction"):
						This.SelectionDictionary["DeltaPGamma"][CutCounter].NonTracker += 1
					
		for CutCounter in xrange(DeltaPPiCutNumber):
			if (DeltaPPiCriteria[CutCounter]):
				This.SelectionDictionary["DeltaPPi"][CutCounter].EventsRemaining += 1
				
				if (CutCounter < DeltaPPiProtonSelectionCut):
					
					if (TrueEventContainsDelta1ToProtonPi0):
						This.SelectionDictionary["DeltaPPi"][CutCounter].ReconstructedDelta += 1
					else:
						This.SelectionDictionary["DeltaPPi"][CutCounter].MixedEvent += 1
				
				elif (CutCounter >= DeltaPPiProtonSelectionCut):
				
					if (TrueEventInteraction == "DeltaPGamma"):
						This.SelectionDictionary["DeltaPPi"][CutCounter].TruthDelta += 1
					elif (TrueEventInteraction == "DeltaPPi"):
						This.SelectionDictionary["DeltaPPi"][CutCounter].ReconstructedDelta += 1
					elif (TrueEventInteraction == "OtherResonance"):
						This.SelectionDictionary["DeltaPPi"][CutCounter].OtherRPInteraction += 1
					elif (TrueEventInteraction == "QS"):
						This.SelectionDictionary["DeltaPPi"][CutCounter].QSInteraction += 1
					elif (TrueEventInteraction == "ES"):
						This.SelectionDictionary["DeltaPPi"][CutCounter].ESInteraction += 1
					elif (TrueEventInteraction == "DIS"):
						This.SelectionDictionary["DeltaPPi"][CutCounter].DISInteraction += 1
					elif (TrueEventInteraction == "C"):
						This.SelectionDictionary["DeltaPPi"][CutCounter].CSInteraction += 1
					elif (TrueEventInteraction == "MultipleTrackerBackgroundInteractions"):
						This.SelectionDictionary["DeltaPPi"][CutCounter].MultipleTracker += 1
					elif (TrueEventInteraction == "NonTrackerInteraction"):
						This.SelectionDictionary["DeltaPPi"][CutCounter].NonTracker += 1
					
		for CutCounter in xrange(ProtonPhotonToElectronsCutNumber):
			if (ProtonPhotonToElectrons[CutCounter]):
				This.SelectionDictionary["ProtonPhotonToElectrons"][CutCounter].EventsRemaining += 1
				
				if (CutCounter < ProtonPhotonToElectronsProtonSelectionCut):
					
					if (TrueEventContainsDelta1ToProtonPhoton):
						This.SelectionDictionary["ProtonPhotonToElectrons"][CutCounter].TruthDelta += 1
					else:
						This.SelectionDictionary["ProtonPhotonToElectrons"][CutCounter].MixedEvent += 1
				
				elif (CutCounter >= ProtonPhotonToElectronsProtonSelectionCut):
					
					if (TrueEventInteraction == "DeltaPGamma"):
						This.SelectionDictionary["ProtonPhotonToElectrons"][CutCounter].TruthDelta += 1
					elif (TrueEventInteraction == "DeltaPPi"):
						This.SelectionDictionary["ProtonPhotonToElectrons"][CutCounter].ReconstructedDelta += 1
					elif (TrueEventInteraction == "OtherResonance"):
						This.SelectionDictionary["ProtonPhotonToElectrons"][CutCounter].OtherRPInteraction += 1
					elif (TrueEventInteraction == "QS"):
						This.SelectionDictionary["ProtonPhotonToElectrons"][CutCounter].QSInteraction += 1
					elif (TrueEventInteraction == "ES"):
						This.SelectionDictionary["ProtonPhotonToElectrons"][CutCounter].ESInteraction += 1
					elif (TrueEventInteraction == "DIS"):
						This.SelectionDictionary["ProtonPhotonToElectrons"][CutCounter].DISInteraction += 1
					elif (TrueEventInteraction == "C"):
						This.SelectionDictionary["ProtonPhotonToElectrons"][CutCounter].CSInteraction += 1
					elif (TrueEventInteraction == "MultipleTrackerBackgroundInteractions"):
						This.SelectionDictionary["ProtonPhotonToElectrons"][CutCounter].MultipleTracker += 1
					elif (TrueEventInteraction == "NonTrackerInteraction"):
						This.SelectionDictionary["ProtonPhotonToElectrons"][CutCounter].NonTracker += 1
		
		################ Invariant Mass Section #########
		
		if (DeltaPGammaCriteria[6]):

			This.HistogramCollection1.Histograms["ProtonTrackMultiplicityECal"].Populate(NumberOfReconstructedProtonTracks)
			This.HistogramCollection1.Histograms["ECalMultiplicityECal"].Populate(NTrackerECalRecon)
			
		if (ProtonPhotonToElectrons[6]):
			This.HistogramCollection1.Histograms["ProtonTrackMultiplicityPP"].Populate(NumberOfReconstructedProtonTracks)
			This.HistogramCollection1.Histograms["ECalMultiplicityPP"].Populate(NTrackerECalRecon)
		
		if (DeltaPGammaCriteria[len(DeltaPGammaCriteria) - 1] == True):
			
			This.HistogramCollection1.Histograms["Final_Invariant_Mass"].Populate(TrueEventInteraction, DeltaBaryonMass, str(TrueEventInteraction))
			
		######### Background Events ##########		
		if (This.SelectBackgroundEvents == True):

			if (DeltaPGammaCriteria[len(DeltaPGammaCriteria) - 1] == True):

				This.DeltaPGammaEventFile = open(This.DeltaPGammaEventFileLocator, "a")
				This.DeltaPGammaEventFile.write(str(TrueEventInteraction) + " " + str(This.BasicInformation.RunID) + " " + str(This.BasicInformation.SubrunID) + " " + str(This.BasicInformation.EventID) + TextConstants.NewLine)					
				This.DeltaPGammaEventFile.close()
				
			if (DeltaPPiCriteria[len(DeltaPPiCriteria) - 1] == True):

				This.DeltaPPiCriteriaEventFile = open(This.DeltaPPiEventFileLocator, "a")
				This.DeltaPPiCriteriaEventFile.write(str(TrueEventInteraction) + " " + str(This.BasicInformation.RunID) + " " + str(This.BasicInformation.SubrunID) + " " + str(This.BasicInformation.EventID) + TextConstants.NewLine)					
				This.DeltaPPiCriteriaEventFile.close()
				
			if (ProtonPhotonToElectrons[len(ProtonPhotonToElectrons) - 1] == True):

				This.DeltaPGammaPPEventFile = open(This.DeltaPGammaPPEventFileLocator, "a")
				This.DeltaPGammaPPEventFile.write(str(TrueEventInteraction) + " " + str(This.BasicInformation.RunID) + " " + str(This.BasicInformation.SubrunID) + " " + str(This.BasicInformation.EventID) + TextConstants.NewLine)					
				This.DeltaPGammaPPEventFile.close()
				
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
																					
					This.HistogramCollection1.Histograms["Reconstructed_Delta1Baryon_Energy"].Populate(DeltaBaryon.T)
					This.HistogramCollection1.Histograms["Reconstructed_Delta1Baryon_MomentumModulus"].Populate(DeltaBaryon.SpatialModulus())
					This.HistogramCollection1.Histograms["Reconstructed_Delta1Baryon_Mass"].Populate(DeltaBaryon.InvariantModulus())
					
					########################################
					# Angle between Photon Direction and Proton Position #
					########################################
								
								
								
					Angle1 = AngleBetweenDirections(Proton1.Position, Photon1.Position, Photon1.Direction)
					TimeSeparation = math.fabs(float(Proton1.Position.T) - float(Photon1.Position.T))
						
					if (ReconstructedProtonTrack and NTrackerECalRecon > 0 and Angle1 < 10 and Angle1 > -10 and Photon1.DirectionIsValid == True):
						This.ReconstructedStatistics.Statistics["NEventsWithTECCAndCRProtonWithin10D"].Quantity += 1
						
						if (TimeSeparation < This.Parameters["SynchronicityLimit"]):
							This.ReconstructedStatistics.Statistics["NEventsWithTECCAndCRProtonWithin10DWithin500ns"].Quantity += 1
					
					This.HistogramCollection1.Histograms["PhotonAngles"].Populate(Angle1)
					This.HistogramCollection1.Histograms["Photon_Angles_Stacked"].Populate(Proton1.Process, Angle1, Proton1.Process)
					This.HistogramCollection1.Histograms["ProtonPhotonTimeSeparations"].Populate(TimeSeparation)
					
					
					if (TimeSeparation < This.Parameters["SynchronicityLimit"]):
																						
						This.HistogramCollection1.Histograms["Reconstructed_Delta1Baryon_Energy_TimeSeparated"].Populate(DeltaBaryon.T)
						This.HistogramCollection1.Histograms["Reconstructed_Delta1Baryon_MomentumModulus_TimeSeparated"].Populate(DeltaBaryon.SpatialModulus())
						This.HistogramCollection1.Histograms["Reconstructed_Delta1Baryon_Mass_TimeSeparated"].Populate(DeltaBaryon.InvariantModulus())
					
				
			for GRTVertex1 in This.Truth_GRTVertices.Vtx: 
				for GRTParticle1 in This.RTTools.getParticles(GRTVertex1):
					# Consider the truth data events. If it contains a Delta Baryon, then retrieve its kinematics for comparison.
					
					if (GRTParticle1.pdg == ParticleCodes.Delta1Baryon):
						
						DeltaBaryon = Geometry.FourVector()
					
						DeltaBaryon.T = GRTParticle1.momentum[3] * 1000 # Unit Conversion
						DeltaBaryon.X = GRTParticle1.momentum[0] * 1000
						DeltaBaryon.Y = GRTParticle1.momentum[1] * 1000
						DeltaBaryon.Z = GRTParticle1.momentum[2] * 1000
						
						This.HistogramCollection1.Histograms["Truth_Delta1Baryon_Energy"].Populate(DeltaBaryon.T)
						This.HistogramCollection1.Histograms["Truth_Delta1Baryon_MomentumModulus"].Populate(DeltaBaryon.SpatialModulus())
						This.HistogramCollection1.Histograms["Truth_Delta1Baryon_Mass"].Populate(DeltaBaryon.InvariantModulus())

		########################################
	
	def MuonProtonSameVertex(This, Muon, Proton):

		MuonProtonSameVertex = False

		MuonFrontPosition = Muon.FrontPosition.ToThreeVector()
		ProtonFrontPosition = Proton.Position.ToThreeVector()
				
		FrontPositionSeparation = ProtonFrontPosition - MuonFrontPosition

		This.HistogramCollection1.Histograms["Proton_Muon_Separation"].Populate(Proton.Process, FrontPositionSeparation.Modulus(), str(Proton.Process))
		
		if (FrontPositionSeparation.Modulus() < This.Parameters["MuonProtonLocalityLimit"]):
				
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
				
				Separation = Electron1.FrontPosition - Positron1.FrontPosition
				
				This.HistogramCollection1.Histograms["ElectronsAndAntielectrons_SeparationX"].Populate(math.fabs(Separation.X))
				This.HistogramCollection1.Histograms["ElectronsAndAntielectrons_SeparationY"].Populate(math.fabs(Separation.Y))
				This.HistogramCollection1.Histograms["ElectronsAndAntielectrons_SeparationZ"].Populate(math.fabs(Separation.Z))
				
				if (Electron1.TrueVertex.ID == Positron1.TrueVertex.ID):
					PairProduced = True
					
				else:
					PairProduced = False
				
				if ((Electron1.CorrectlyReconstructed() == True) and (Positron1.CorrectlyReconstructed() == True) and PairProduced):
					This.HistogramCollection1.Histograms["ElectronsAndAntielectrons_Separation_StackedX"].Populate("0", math.fabs(Separation.X), "Correctly Reconstructed Electron-Antielectron pairs")
					This.HistogramCollection1.Histograms["ElectronsAndAntielectrons_Separation_StackedY"].Populate("0", math.fabs(Separation.Y), "Correctly Reconstructed Electron-Antielectron pairs")
					This.HistogramCollection1.Histograms["ElectronsAndAntielectrons_Separation_StackedZ"].Populate("0", math.fabs(Separation.Z), "Correctly Reconstructed Electron-Antielectron pairs")
				elif ((Electron1.CorrectlyReconstructed() == True) and (Positron1.CorrectlyReconstructed() == True) and (not PairProduced)):
					This.HistogramCollection1.Histograms["ElectronsAndAntielectrons_Separation_StackedX"].Populate("1", math.fabs(Separation.X), "Correctly Reconstructed Electron-Antielectrons")
					This.HistogramCollection1.Histograms["ElectronsAndAntielectrons_Separation_StackedY"].Populate("1", math.fabs(Separation.Y), "Correctly Reconstructed Electron-Antielectrons")
					This.HistogramCollection1.Histograms["ElectronsAndAntielectrons_Separation_StackedZ"].Populate("1", math.fabs(Separation.Z), "Correctly Reconstructed Electron-Antielectrons")
				elif (Electron1.CorrectlyReconstructed() == True and Positron1.CorrectlyReconstructed() == False):
					This.HistogramCollection1.Histograms["ElectronsAndAntielectrons_Separation_StackedX"].Populate("2", math.fabs(Separation.X), "Correctly Reconstructed Electron")
					This.HistogramCollection1.Histograms["ElectronsAndAntielectrons_Separation_StackedY"].Populate("2", math.fabs(Separation.Y), "Correctly Reconstructed Electron")
					This.HistogramCollection1.Histograms["ElectronsAndAntielectrons_Separation_StackedZ"].Populate("2", math.fabs(Separation.Z), "Correctly Reconstructed Electron")
				elif (Electron1.CorrectlyReconstructed() == False and Positron1.CorrectlyReconstructed() == True):
					This.HistogramCollection1.Histograms["ElectronsAndAntielectrons_Separation_StackedX"].Populate("3", math.fabs(Separation.X), "Correctly Reconstructed Antielectron")
					This.HistogramCollection1.Histograms["ElectronsAndAntielectrons_Separation_StackedY"].Populate("3", math.fabs(Separation.Y), "Correctly Reconstructed Antielectron")
					This.HistogramCollection1.Histograms["ElectronsAndAntielectrons_Separation_StackedZ"].Populate("3", math.fabs(Separation.Z), "Correctly Reconstructed Antielectron")
				else:
					This.HistogramCollection1.Histograms["ElectronsAndAntielectrons_Separation_StackedX"].Populate("4", math.fabs(Separation.X), "Incorrectly Reconstructed Electron-Antielectrons")
					This.HistogramCollection1.Histograms["ElectronsAndAntielectrons_Separation_StackedY"].Populate("4", math.fabs(Separation.Y), "Incorrectly Reconstructed Electron-Antielectrons")
					This.HistogramCollection1.Histograms["ElectronsAndAntielectrons_Separation_StackedZ"].Populate("4", math.fabs(Separation.Z), "Incorrectly Reconstructed Electron-Antielectrons")
				
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
					
					This.HistogramCollection1.Histograms["ElectronsAndAntielectrons_InvariantMass"].Populate(PossiblePhoton1.EnergyMomentum.InvariantModulus())
															
					for Proton1 in Protons:
												
						Angle1 = AngleBetweenDirections(Proton1.Position, PossiblePhoton1.Position, PossiblePhoton1.EnergyMomentum.SpatialDirection())
						TimeSeparation = math.fabs(float(Proton1.Position.T) - float(PossiblePhoton1.Position.T))

						if (Angle1 < This.Parameters["PairProductionAngularLocalityLimit"]):
							EventContainsElectronPositronPairWithinAngle = True
						
						if (TimeSeparation < This.Parameters["SynchronicityLimit"]):
							EventContainsElectronPositronPairWithinTime = True
						
						#if (EventContainsElectronPositronPairWithinAngle and EventContainsElectronPositronPairWithinTime):
							"""This.HistogramCollection1.Histograms["ElectronPositronPairs_Photon_AngleToProton"].Populate(TruthInteractionType, Angle1)"""
							
					
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
	
def PIDTruth(GRTVertices, TrueVertices, TrueTrajectories, PID):
	
	TrueGRTVertex = None
	TrueTrajectory = None
	TrueVertex = None

	for Vertex1 in TrueVertices:
		
		if (Vertex1.ID == PID.TrueParticle.Vertex.ID):
			
			TrueVertex = Vertex1
						
	for GRTVertex1 in GRTVertices:
					
		if (GRTVertex1.TruthVertexID == TrueVertex.ID):
						
			TrueGRTVertex = GRTVertex1
						
	for Trajectory1 in TrueTrajectories:
				
		if (Trajectory1.ID == PID.TrueParticle.ID):
			
			TrueTrajectory = Trajectory1
			
	return TrueGRTVertex, TrueVertex, TrueTrajectory
			
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
	MonteCarloFull = False
	NoSelection = False
	
	CommandLineDeconstructor1 = CommandLine.Deconstructor(sys.argv)
		
	SimulationInformation = {}
	
	SimulationInformation["DesiredNumberOfEvents"] = ""
	SimulationInformation["InputFilePurity"] = ("Reading events from: " + str(InputFileLocator), "P1")
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
						
					if (ArgumentComponents[0] == "MC"):
						SimulationInformation["MonteCarloFullFlag"] = ("Perform Delta -> p gamma Monte Carlo analysis of all events", "MC")
						MonteCarloFull = True
						
					if (ArgumentComponents[0] == "NS"):
						SimulationInformation["NoSelectionFlag"] = ("Not performing any selection analysis", "NS")
						NoSelection = True
						
	elif (len(sys.argv) == 1):
		SimulationInformation["InputFilePurity"] = ("Reading events from:" + str(DefaultInputFileLocatorPurified), "P1")
	
	SimulationInformation["DesiredNumberOfEvents"] = ("Desired number of Events: " + str(int(NumberOfEventsToRead)), "NE" + str(int(NumberOfEventsToRead)))
		
	OutputROOTFileLocator = FileAdministrator.CreateFilePath(DataLocation, ".root", SimulationInformation, "ROOT/")
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
	Analysis1.MonteCarloFull = MonteCarloFull
	Analysis1.NoSelection = NoSelection
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
