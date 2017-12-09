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
import EventCodeDeconstructor

import ThreeVector
import FourVector


class EventCollection:
	
	def __init__(self):
		
		self.Events = []
		
	def InterpretEvent(self, TrueGRTVertices, ReconstructedPIDs, TrueTrajectories, ReconstructedTECTs, SelectionReferences):
		
		Event1 = Event()
		
		Event1.TrueEvent.InterpretGRTVertices(TrueGRTVertices)
		Event1.ReconstructedEvent.InterpretPIDs(ReconstructedPIDs, TrueTrajectories, ReconstructedTECTs)
		
		for SelectionReference in SelectionReferences:
			Event1.SelectionResponses[SelectionReference] = False
		
		self.Events.append(Event1)
		
		return Event1

class Event:
	
	def __init__(self):
		
		self.TrueEvent = TrueEvent()
		self.ReconstructedEvent = ReconstructedEvent()
	
		self.SelectionResponses = {}
	

class TrueEvent:
	
	def __init__(self):
		
		self.TrueVertices = []
		
		self.EventCodeDeconstructor = EventCodeDeconstructor.EventCodeDeconstructor()
		
		self.ContainsDelta1HadronToProtonPhotonInteraction = False
		self.ContainsDelta1HadronToProtonPi0MesonInteraction = False
		
		self.RTTools = RooTrackerTools.RooTrackerTools()
		
	def InterpretGRTVertices(self, GRTVertices):
				
		for GRTVertex1 in GRTVertices:
			
			TrueVertex1 = TrueVertex()
								
														
			self.EventCodeDeconstructor.ReadCode(GRTVertex1.EvtCode)
			
			for Element1 in self.EventCodeDeconstructor.Elements:
				if (Element1.Reference == "Current Code"):
					TrueVertex1.CurrentCode = Element1.Content
				if (Element1.Reference == "Process Code"):
					TrueVertex1.ProcessCode = Element1.Content
									
									
			for GRTParticle1 in self.RTTools.getParticles(GRTVertex1): # Look through each particle in the vertex.
			
				TrueParticle1 = TrueParticle()
				
				
				if ((GRTParticle1.pdg == ParticleCodes.MuNeutrino) and (GRTParticle1.status == 0)): # See whether there is an incident mu neutrino.
					TrueVertex1.ContainsIncidentMuonNeutrino = True
							
							
				if (GRTParticle1.pdg == ParticleCodes.Delta1Baryon): # See whether there is a Delta 1 Hadron

					FirstProduct = GRTParticle1.first_daughter
					LastProduct = GRTParticle1.last_daughter
					NumberOfProducts = LastProduct - FirstProduct + 1

					if (NumberOfProducts == 2):	# The Delta 1 Hadron must deteriorate to two particles.
						
						for GRTParticle2 in self.RTTools.getParticles(GRTVertex1):
							
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
			
			self.TrueVertices.append(TrueVertex1)
													


class TrueVertex:
	
	def __init__(self):
		
		self.EventCode = ""
		
		self.CurrentCode = ""
		self.ProcessCode = ""
		
		self.TrueParticles = []
		
		self.ContainsIncidentMuonNeutrino = False
		self.ContainsProtonFromDelta1Hadron = False
		self.ContainsPhotonFromDelta1Hadron = False
		self.ContainsPi0MesonFromDelta1Hadron = False
		
		self.IsDelta1HadronToProtonPhotonInteraction = False
		self.IsDelta1HadronToProtonPi0MesonInteraction = False


class TrueParticle:
	
	def __init__(self):
		
		self.Position = FourVector.FourVector()


class ReconstructedEvent:
	
	def __init__(self):
		
		self.Objects = []
		self.Paths = []
		self.Torrents = []
		self.Particles = []
		
		self.Protons = []
		self.Photons = []
		
		self.PullVariableLimits = {}

		self.PullVariableLimits[ParticleCodes.Electron] = 0.5
		self.PullVariableLimits[ParticleCodes.Kaon1] = 0.5
		self.PullVariableLimits[ParticleCodes.MuLepton] = 0.5
		self.PullVariableLimits[ParticleCodes.Pi1Meson] = 0.5
		self.PullVariableLimits[ParticleCodes.Proton] = 0.5
		
		self.NumberOfProtonPaths = 0
		self.NumberOfCorrectlyReconstructedProtonPaths = 0
		self.NumberOfMuLeptonPaths = 0
		self.NumberOfElectronPaths = 0
		self.NumberOfAntielectronPaths = 0
				
	def InterpretPIDs(self, PIDs, Truth_Trajectories, TECTs):
		
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
					
					if (math.fabs(ParticlePull) < math.fabs(LowestPull) and math.fabs(ParticlePull) < math.fabs(self.PullVariableLimits[ParticleCode])):
						
						LowestPull = math.fabs(ParticlePull)
						
						ReconstructedObject1.ParticleCode = ParticleCode


				for Trajectory1 in Truth_Trajectories: # Compare to truth trajectories.
					if (Trajectory1.ID == PID.TrueParticle.ID):
																	
						ReconstructedObject1.TrueParticleCode = Trajectory1.PDG
								
						ReconstructedObject1.TrueEnergyMomentum_Initial.X = Trajectory1.InitMomentum.X()
						ReconstructedObject1.TrueEnergyMomentum_Initial.Y = Trajectory1.InitMomentum.Y()
						ReconstructedObject1.TrueEnergyMomentum_Initial.Z = Trajectory1.InitMomentum.Z()
						ReconstructedObject1.TrueEnergyMomentum_Initial.T = Trajectory1.InitMomentum.E()
											
			
			self.Objects.append(ReconstructedObject1)
		
		
		for ReconstructedObject2 in self.Objects:
			
			if (ReconstructedObject2.ParticleCode == ParticleCodes.Proton):				
				self.NumberOfProtonPaths += 1
									
				if (ReconstructedObject2.IsCorrectlyReconstructed()):
					self.NumberOfCorrectlyReconstructedProtonPaths += 1
				
				Proton1 = ReconstructedParticle()
		
				Proton1.EnergyMomentum_Initial = ReconstructedObject2.EnergyMomentum_Initial
				Proton1.Position_Initial = ReconstructedObject2.Position_Initial
								
				self.Protons.append(Proton1)
							
			if (ReconstructedObject2.ParticleCode == ParticleCodes.MuLepton):				
				self.NumberOfMuLeptonPaths += 1
				
			if (ReconstructedObject2.ParticleCode == ParticleCodes.Electron):				
				self.NumberOfElectronPaths += 1
				
			if (ReconstructedObject2.ParticleCode == ParticleCodes.AntiElectron):				
				self.NumberOfAntielectronPaths += 1
				
				
				
		for TECT1 in TECTs:
			
			ReconstructedTorrent1 = ReconstructedTorrent()
									
			TECT_Energy = TECT1.EMEnergyFit_Result
										
			if (TECT1.IsShowerLike): # Determine whether the TEC reconstruction is track-like or torrent-like, it shouldn't matter which for the photon, but the directions are different.
			
				TECT_UnitDirection = ThreeVector.ThreeVector(TECT1.Shower.Direction.X(), TECT1.Shower.Direction.Y(), TECT1.Shower.Direction.Z())
				
				ReconstructedTorrent1.Position_Initial.T = TECT1.Shower.Position.T()
				ReconstructedTorrent1.Position_Initial.X = TECT1.Shower.Position.X()
				ReconstructedTorrent1.Position_Initial.Y = TECT1.Shower.Position.Y()
				ReconstructedTorrent1.Position_Initial.Z = TECT1.Shower.Position.Z()
				
			elif (TECT1.IsTrackLike):
				
				TECT_UnitDirection = ThreeVector.ThreeVector(TECT1.Track.Direction.X(), TECT1.Track.Direction.Y(), TECT1.Track.Direction.Z())
				
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
				
				self.Torrents.append(ReconstructedTorrent1)		
		

class ReconstructedObject:
	
	def __init__(self):
		
		self.ParticleCode = 0
		
		self.NumberOfPoints = 0
		self.ContainsCorrectNumberOfPoints = False
		
		self.DetectorCode = ""
		
		self.EnergyMomentum = 0
		
		self.EnergyMomentum_Initial = FourVector.FourVector()
		self.EnergyMomentum_Final = FourVector.FourVector()
		
		self.Position_Initial = FourVector.FourVector()
		self.Position_Final = FourVector.FourVector()
		
		self.Direction_Initial = ThreeVector.ThreeVector()
		self.Direction_Final = ThreeVector.ThreeVector()
		
		self.PullVariables = {}
		
		
		self.TrueParticleCode = 0
		
		self.TrueEnergyMomentum_Initial = FourVector.FourVector()
		self.TrueEnergyMomentum_Final = FourVector.FourVector()
		
	def IsCorrectlyReconstructed(self):
		
		return (self.ParticleCode == self.TrueParticleCode)
		
	def IsWithinVolume(self, ThreeDimensionalObject1):
		
		return ThreeDimensionalObject1.Contains(Position_Initial)
		
class ReconstructedPath(ReconstructedObject):
	
	def __init__(self):
		ReconstructedObject.__init__(self)
		
		self.asd = 0

class ReconstructedTorrent(ReconstructedObject):
	
	def __init__(self):
		ReconstructedObject.__init__(self)
		
		self.asd = 0

class ReconstructedParticle(ReconstructedObject):
	
	def __init__(self):
		ReconstructedObject.__init__(self)
		
		self.asd = 0
