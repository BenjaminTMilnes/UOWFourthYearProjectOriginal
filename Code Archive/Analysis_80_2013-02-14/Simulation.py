# Simulation
#
# This class reads the ROOT objects and creates its own data collection, which has the analytic boolean and numeric variables which we need. Though
# it does not manage the creation or editing of histograms.
#
# Last Modified: 2013-01-22 22:37
#

####################################################################################################
# DO NOT EDIT - PROTOTYPE CODE
####################################################################################################

import sys
import math

import ROOT
import RooTrackerTools

import ParticleCodes
import EventCodes

import Geometry


class EventCollection:
	
	def __init__(This):
		
		This.Events = []
		
	def InterpretEvent(This, TrueGRTVertices, ReconstructedPIDs, TrueTrajectories, ReconstructedTECTs, SelectionReferences):
		
		Event1 = Event()
		
		Event1.TrueEvent.InterpretGRTVertices(TrueGRTVertices)
		Event1.ReconstructedEvent.InterpretPIDs(ReconstructedPIDs, TrueTrajectories)
		Event1.ReconstructedEvent.InterpretTECTs(ReconstructedTECTs)
		
		for SelectionReference in SelectionReferences:
			Event1.SelectionResponses[SelectionReference] = False
		
		This.Events.append(Event1)
		
		return Event1

class Event:
	
	def __init__(This):
		
		This.TrueEvent = TrueEvent()
		This.ReconstructedEvent = ReconstructedEvent()
	
		This.SelectionResponses = {}
	

class TrueEvent:
	
	def __init__(This):
		
		This.TrueVertices = []
		This.NumberOfTrueVertices = 0
		
		This.EventCodeDeconstructor = EventCodes.Deconstructor()
		
		This.ContainsDelta1HadronToProtonPhotonInteraction = False
		This.ContainsDelta1HadronToProtonPi0MesonInteraction = False
		
		This.NumberOfDelta1HadronToProtonPhotonInteractions = 0
		This.NumberOfDelta1HadronToProtonPhotonCCInteractions = 0
		This.NumberOfDelta1HadronToProtonPhotonNCInteractions = 0
		This.NumberOfDelta1HadronToProtonPi0MesonInteractions = 0
		
		This.RTTools = RooTrackerTools.RooTrackerTools()
		
	def InterpretGRTVertices(This, GRTVertices):
				
		for GRTVertex1 in GRTVertices:
			
			TrueVertex1 = TrueVertex()
								
														
			This.EventCodeDeconstructor.ReadCode(GRTVertex1.EvtCode)
			
			TrueVertex1.CurrentCode = This.EventCodeDeconstructor.Elements["Current Code"].Content
			TrueVertex1.ProcessCode = This.EventCodeDeconstructor.Elements["Process Code"].Content
													
									
			for GRTParticle1 in This.RTTools.getParticles(GRTVertex1): # Look through each particle in the vertex.
			
				TrueParticle1 = TrueParticle()
				
				TrueParticle1.PDG = GRTParticle1.pdg
				
				
				if ((GRTParticle1.pdg == ParticleCodes.MuNeutrino) and (GRTParticle1.status == 0)): # See whether there is an incident mu neutrino.
					TrueVertex1.ContainsIncidentMuonNeutrino = True
							
							
				if (GRTParticle1.pdg == ParticleCodes.Delta1Baryon): # See whether there is a Delta 1 Hadron

					FirstProduct = GRTParticle1.first_daughter
					LastProduct = GRTParticle1.last_daughter
					NumberOfProducts = LastProduct - FirstProduct + 1

					if (NumberOfProducts == 2):	# The Delta 1 Hadron must deteriorate to two particles.
						
						for GRTParticle2 in This.RTTools.getParticles(GRTVertex1):
							
							if (GRTParticle2.i >= FirstProduct and GRTParticle2.i <= LastProduct):
							
								if (GRTParticle2.pdg == ParticleCodes.Proton):
									TrueVertex1.ContainsProtonFromDelta1Hadron = True
									
								if (GRTParticle2.pdg == ParticleCodes.Photon):
									TrueVertex1.ContainsPhotonFromDelta1Hadron = True
									
								if (GRTParticle2.pdg == ParticleCodes.Pi0Meson):
									TrueVertex1.ContainsPi0MesonFromDelta1Hadron = True
				
				TrueVertex1.TrueParticles.append(TrueParticle1)
				
				
			TrueVertex1.IsDelta1HadronToProtonPhotonInteraction	= (TrueVertex1.ContainsIncidentMuonNeutrino and TrueVertex1.ContainsProtonFromDelta1Hadron and TrueVertex1.ContainsPhotonFromDelta1Hadron and TrueVertex1.CurrentCode == "RP")
			TrueVertex1.IsDelta1HadronToProtonPi0MesonInteraction = (TrueVertex1.ContainsIncidentMuonNeutrino and TrueVertex1.ContainsProtonFromDelta1Hadron and TrueVertex1.ContainsPi0MesonFromDelta1Hadron and TrueVertex1.CurrentCode == "RP")		
			
			if (TrueVertex1.IsDelta1HadronToProtonPhotonInteraction):
				
				This.NumberOfDelta1HadronToProtonPhotonInteractions += 1
				
				if (TrueVertex1.CurrentCode == "CC"):
					This.NumberOfDelta1HadronToProtonPhotonCCInteractions += 1
				if (TrueVertex1.CurrentCode == "NC"):
					This.NumberOfDelta1HadronToProtonPhotonCCInteractions += 1
					
			if (TrueVertex1.IsDelta1HadronToProtonPi0MesonInteraction):
				This.NumberOfDelta1HadronToProtonPi0MesonInteractions += 1
			
			This.TrueVertices.append(TrueVertex1)
		
		This.NumberOfTrueVertices = len(This.TrueVertices)											


class TrueVertex:
	
	def __init__(This):
		
		This.EventCode = ""
		
		This.CurrentCode = ""
		This.ProcessCode = ""
		
		This.TrueParticles = []
		
		This.ContainsIncidentMuonNeutrino = False
		This.ContainsProtonFromDelta1Hadron = False
		This.ContainsPhotonFromDelta1Hadron = False
		This.ContainsPi0MesonFromDelta1Hadron = False
		
		This.IsDelta1HadronToProtonPhotonInteraction = False
		This.IsDelta1HadronToProtonPi0MesonInteraction = False


class TrueParticle:
	
	def __init__(This):
		
		This.PDGCode = 0
		This.Position = Geometry.FourVector()


class ReconstructedEvent:
	
	def __init__(This):
		
		This.ReconstructedObjects = []
		This.ReconstructedPaths = []
		This.ReconstructedTorrents = []
		This.ReconstructedParticles = []
		
		This.Protons = []
		This.Photons = []
		
		This.PullVariableLimits = {}

		This.PullVariableLimits[ParticleCodes.Electron] = 0.5
		This.PullVariableLimits[ParticleCodes.Kaon1] = 0.5
		This.PullVariableLimits[ParticleCodes.MuLepton] = 0.5
		This.PullVariableLimits[ParticleCodes.Pi1Meson] = 0.5
		This.PullVariableLimits[ParticleCodes.Proton] = 0.5
		
		This.NumberOfProtonPaths = 0
		This.NumberOfCorrectlyReconstructedProtonPaths = 0
		This.NumberOfMuLeptonPaths = 0
		This.NumberOfElectronPaths = 0
		This.NumberOfAntielectronPaths = 0
				
	def InterpretPIDs(This, PIDs, Truth_Trajectories):
		
		for PID in PIDs:
			
			ReconstructedObject1 = ReconstructedObject()
													
			for TPCTrack1 in PID.TPC:
				ReconstructedObject1.NumberOfPoints = TPCTrack1.NNodes
				
				if (TPCTrack1.NNodes > 18):
					ReconstructedObject1.ContainsCorrectNumberOfPoints = True
					
					
			if (len(PID.ParticleIds) > 0):
				
				ReconstructedObject1.EnergyMomentum = PID.FrontMomentum
				ReconstructedObject1.EnergyMomentum_Initial.Y = PID.FrontMomentum
				ReconstructedObject1.EnergyMomentum_Initial.Z = PID.FrontMomentum
				ReconstructedObject1.EnergyMomentum_Initial.T = PID.FrontMomentum
				
				ReconstructedObject1.Position_Initial.X = PID.FrontPosition.X()
				ReconstructedObject1.Position_Initial.Y = PID.FrontPosition.Y()
				ReconstructedObject1.Position_Initial.Z = PID.FrontPosition.Z()
				ReconstructedObject1.Position_Initial.T = PID.FrontPosition.T()
				
				ReconstructedObject1.Direction_Initial.X = PID.FrontDirection.X()
				ReconstructedObject1.Direction_Initial.Y = PID.FrontDirection.Y()
				ReconstructedObject1.Direction_Initial.Z = PID.FrontDirection.Z()
					
				ReconstructedObject1.DetectorCode = str(PID.Detectors)

				BestTPCTrackIndex = 0
				MaximumNumberOfPoints = 0
						
				for i, TPCTrack1 in enumerate(PID.TPC):
					if (TPCTrack1.NNodes > MaximumNumberOfPoints):
						BestTPCTrackIndex = i
					
				for j , TPCTrack1 in enumerate(PID.TPC):
					if (j == i):
						ReconstructedObject1.PullVariables[ParticleCodes.Electron] = TPCTrack1.PullEle
						ReconstructedObject1.PullVariables[ParticleCodes.Kaon1] = TPCTrack1.PullKaon
						ReconstructedObject1.PullVariables[ParticleCodes.MuLepton] = TPCTrack1.PullMuon
						ReconstructedObject1.PullVariables[ParticleCodes.Pi1Meson] = TPCTrack1.PullPion
						ReconstructedObject1.PullVariables[ParticleCodes.Proton] = TPCTrack1.PullProton

				LowestPull = 100
				
				for ParticleCode, ParticlePull in ReconstructedObject1.PullVariables.iteritems():
					
					if (math.fabs(ParticlePull) < math.fabs(LowestPull) and math.fabs(ParticlePull) < math.fabs(This.PullVariableLimits[ParticleCode])):
						
						LowestPull = math.fabs(ParticlePull)
						
						ReconstructedObject1.ParticleCode = ParticleCode


				for Trajectory1 in Truth_Trajectories: # Compare to truth trajectories.
					if (Trajectory1.ID == PID.TrueParticle.ID):
																	
						ReconstructedObject1.TrueParticleCode = Trajectory1.PDG
								
						ReconstructedObject1.TrueEnergyMomentum_Initial.X = Trajectory1.InitMomentum.X()
						ReconstructedObject1.TrueEnergyMomentum_Initial.Y = Trajectory1.InitMomentum.Y()
						ReconstructedObject1.TrueEnergyMomentum_Initial.Z = Trajectory1.InitMomentum.Z()
						ReconstructedObject1.TrueEnergyMomentum_Initial.T = Trajectory1.InitMomentum.E()
											
			
			This.ReconstructedObjects.append(ReconstructedObject1)
		
		
		for ReconstructedObject2 in This.ReconstructedObjects:
			
			if (ReconstructedObject2.ParticleCode == ParticleCodes.Proton):				
				This.NumberOfProtonPaths += 1
									
				if (ReconstructedObject2.IsCorrectlyReconstructed()):
					This.NumberOfCorrectlyReconstructedProtonPaths += 1
				
				Proton1 = ReconstructedParticle()
		
				Proton1.EnergyMomentum_Initial = ReconstructedObject2.EnergyMomentum_Initial
				Proton1.Position_Initial = ReconstructedObject2.Position_Initial
								
				This.Protons.append(Proton1)
							
			if (ReconstructedObject2.ParticleCode == ParticleCodes.MuLepton):				
				This.NumberOfMuLeptonPaths += 1
				
			if (ReconstructedObject2.ParticleCode == ParticleCodes.Electron):				
				This.NumberOfElectronPaths += 1
				
			if (ReconstructedObject2.ParticleCode == ParticleCodes.AntiElectron):				
				This.NumberOfAntielectronPaths += 1
				
				
	def InterpretTECTs(This, TECTs):
				
		for TECT1 in TECTs:
			
			ReconstructedTorrent1 = ReconstructedTorrent()
									
			TECT_Energy = TECT1.EMEnergyFit_Result
										
			if (TECT1.IsShowerLike): # Determine whether the TEC reconstruction is track-like or torrent-like, it shouldn't matter which for the photon, but the directions are different.
			
				TECT_UnitDirection = Geometry.ThreeVector(TECT1.Shower.Direction.X(), TECT1.Shower.Direction.Y(), TECT1.Shower.Direction.Z())
				
				ReconstructedTorrent1.Position_Initial.T = TECT1.Shower.Position.T()
				ReconstructedTorrent1.Position_Initial.X = TECT1.Shower.Position.X()
				ReconstructedTorrent1.Position_Initial.Y = TECT1.Shower.Position.Y()
				ReconstructedTorrent1.Position_Initial.Z = TECT1.Shower.Position.Z()
				
			elif (TECT1.IsTrackLike):
				
				TECT_UnitDirection = Geometry.ThreeVector(TECT1.Track.Direction.X(), TECT1.Track.Direction.Y(), TECT1.Track.Direction.Z())
				
				ReconstructedTorrent1.Position_Initial.T = TECT1.Track.Position.T()
				ReconstructedTorrent1.Position_Initial.X = TECT1.Track.Position.X()
				ReconstructedTorrent1.Position_Initial.Y = TECT1.Track.Position.Y()
				ReconstructedTorrent1.Position_Initial.Z = TECT1.Track.Position.Z()
						
			if (TECT_UnitDirection.Modulus() < 1.1):#For some reason there sometimes are occurences where the magnitude is far above 1. This if filters them out. We should probably look into this further
									
				ReconstructedTorrent1.EnergyMomentum_Initial.T = TECT_Energy
				ReconstructedTorrent1.EnergyMomentum_Initial.X = TECT_UnitDirection.X * TECT_Energy
				ReconstructedTorrent1.EnergyMomentum_Initial.Y = TECT_UnitDirection.Y * TECT_Energy
				ReconstructedTorrent1.EnergyMomentum_Initial.Z = TECT_UnitDirection.Z * TECT_Energy
											
				ReconstructedTorrent1.Direction_Initial.X = TECT_UnitDirection.X
				ReconstructedTorrent1.Direction_Initial.Y = TECT_UnitDirection.Y
				ReconstructedTorrent1.Direction_Initial.Z = TECT_UnitDirection.Z
				
				This.ReconstructedTorrents.append(ReconstructedTorrent1)		
		

class ReconstructedObject:
	
	def __init__(This):
		
		This.ParticleCode = 0
		
		This.NumberOfPoints = 0
		This.ContainsCorrectNumberOfPoints = False
		
		This.DetectorCode = ""
		
		This.EnergyMomentum = 0
		
		This.EnergyMomentum_Initial = Geometry.FourVector()
		This.EnergyMomentum_Final = Geometry.FourVector()
		
		This.Position_Initial = Geometry.FourVector()
		This.Position_Final = Geometry.FourVector()
		
		This.Direction_Initial = Geometry.ThreeVector()
		This.Direction_Final = Geometry.ThreeVector()
		
		This.PullVariables = {}
		
		
		This.TrueParticleCode = 0
		
		This.TrueEnergyMomentum_Initial = Geometry.FourVector()
		This.TrueEnergyMomentum_Final = Geometry.FourVector()
		
	def IsCorrectlyReconstructed(This):
		
		return (This.ParticleCode == This.TrueParticleCode)
		
	def IsWithinVolume(This, ThreeDimensionalObject1):
		
		return ThreeDimensionalObject1.Contains(Position_Initial)
		
class ReconstructedPath(ReconstructedObject):
	
	def __init__(This):
		ReconstructedObject.__init__(This)
		
		This.ObjectType = "Path"

class ReconstructedTorrent(ReconstructedObject):
	
	def __init__(This):
		ReconstructedObject.__init__(This)
		
		This.ObjectType = "Torrent"

class ReconstructedParticle(ReconstructedObject):
	
	def __init__(This):
		ReconstructedObject.__init__(This)
		
		This.ObjectType = "Particle"
