# Particles
#
# This collection of classes describes the various objects that we use in the main analysis.
#
# Last Modified 2013.01.17 14:23
#

import math
import Geometry

import PhysicalConstants
import ParticleCodes
import EventCodes
import ProcessSeparator

class TheoreticalParticle:
	
	def __init__(This, Mass, PDGCode):
		
		This.PDGCode = PDGCode
		This.Mass = Mass

class ReconstructedParticle:
	
	def __init__(This):
		
		This.Position = Geometry.FourVector()
		This.Direction = Geometry.ThreeVector()
		This.EnergyMomentum = Geometry.FourVector()
		
		This.DirectionIsValid = False
		
		This.TrueTrajectory = None
		This.TrueVertex = None
		
		This.Current = None
		This.InteractionType = None
		
		This.Process = None
		
	def GetProcess(This, RTTools):
		
		This.EventCodeDeconstructor1 = EventCodes.Deconstructor()
		
		This.EventCodeDeconstructor1.ReadCode(This.TrueVertex.EvtCode)
		
		This.Current = This.EventCodeDeconstructor1.Elements["Current Code"].Content
		This.InteractionType = This.EventCodeDeconstructor1.Elements["Process Code"].Content
		
		################# TIDY UP ##################### Looking through ALL vertices and if they are associated with a Delta Baryon
		
		IncidentMuonNeutrino = False#For a later check of whether incident particle is a neutrino
		ProtonFromDelta = False#For logical check on Delta interaction of interest
		PhotonFromDelta = False
		Pi0MesonFromDelta = False
		
		for GRTParticle1 in RTTools.getParticles(This.TrueVertex):
			
			if (GRTParticle1.pdg == ParticleCodes.MuNeutrino):#Looks for a neutrino
			
				if (GRTParticle1.status == 0):#Checks if neutrino is initial state
				
					IncidentMuonNeutrino = True

			if (GRTParticle1.pdg == ParticleCodes.Delta1Baryon):

				DeltaDaughterFirst = GRTParticle1.first_daughter#Finds first Delta daughter
				DeltaDaughterLast = GRTParticle1.last_daughter#Finds last Delta daughter
				DeltaDaughterNumber = DeltaDaughterLast - DeltaDaughterFirst+1#Finds number of daughters of the delta

				if (DeltaDaughterNumber == 2):#Delta -> p gamma must have 2 daughters
					
					for DaughterParticle in RTTools.getParticles(This.TrueVertex):#Loop again over particles in vertex
					
						if (DaughterParticle.i >= DeltaDaughterFirst and DaughterParticle.i <= DeltaDaughterLast):#Only looks for when counter is in range of Delta daughter particles
						
							if (DaughterParticle.pdg == ParticleCodes.Proton):
								ProtonFromDelta = True
								
							if (DaughterParticle.pdg == ParticleCodes.Photon):
								PhotonFromDelta = True
								
								PhotonDaughterFirst = DaughterParticle.first_daughter#To find whether the photon decays to electron positron
								PhotonDaughterLast = DaughterParticle.last_daughter
								
							if (DaughterParticle.pdg == ParticleCodes.Pi0Meson):
								Pi0MesonFromDelta = True
									
		ContainsDelta1ToProtonPhoton = (IncidentMuonNeutrino and ProtonFromDelta and PhotonFromDelta and This.InteractionType == "RP")
			
		ContainsDelta1ToProtonPi0 = (IncidentMuonNeutrino and ProtonFromDelta and Pi0MesonFromDelta and This.InteractionType == "RP")	
								
		####################################

		This.Process = ProcessSeparator.EventProcess(ContainsDelta1ToProtonPhoton, ContainsDelta1ToProtonPi0, This.InteractionType)


class ReconstructedObject:
	
	def __init__(This):
		This.ReconParticleID=-1
		This.ReconParticleIDWeight=-1
		This.ReconParticleIDWeightSecondary=-1
		This.ReconFrontMomentum=-1
		This.TrueParticleID=-1
		This.TrueEnergy=-1
		This.TrueFrontMomentum=-1
		This.ReconFrontDirectionX=0
		This.ReconFrontDirectionY=0
		This.ReconFrontDirectionZ=0
		This.SuitableTPCNodeNumber=False
		This.ReconFrontPositionT=-99999
		This.ReconFrontPositionX=-99999
		This.ReconFrontPositionY=-99999
		This.ReconFrontPositionZ=-99999
		
		This.TrueTrajectory = None
		This.TrueVertex = None
		
		####
		# The PID Particle and Reconstructed Particle classes overlay, so these object properties form a temporary bridge to merge the two classes.
		
		This.ReconstructedParticleCode = None
		This.NumberOfTPCPoints = None
		This.GoodNumberOfTPCPoints = False
		This.Charge = None
		This.FrontPosition = Geometry.FourVector()
		This.FrontEnergyMomentum = Geometry.FourVector()
		
		####
		
		This.Detectors=""

		This.ParticlePull = {}
		
		This.ECalEnergyList = []
				
	def CorrectlyReconstructed(This):
		return(This.ReconParticleID == This.TrueParticleID)
		
	def ReconTrueMomentumDifference(This):
		
		Difference=This.ReconFrontMomentum-This.TrueFrontMomentum
		
		return(Difference)
		
	def ReconstructedParticleEnergy(This):
		
		Mass = This.ReconstructedMass()

		Energy = math.sqrt(This.ReconFrontMomentum * This.ReconFrontMomentum + Mass * Mass)
		
		return(Energy)
		
	def ReconstructedMass(This):
		
		ReconstructedMass = 0
		
		if(This.ReconParticleID == 2212):
			ReconstructedMass = Proton.Mass
		elif(This.ReconParticleID == 13):
			ReconstructedMass = MuLepton.Mass
		elif(This.ReconParticleID == 11):
			ReconstructedMass = Electron.Mass
		elif(This.ReconParticleID == -11):			
			ReconstructedMass = AntiElectron.Mass
			
		return(ReconstructedMass)
		
		
Proton = TheoreticalParticle(PhysicalConstants.ProtonMass, ParticleCodes.Proton)
MuLepton = TheoreticalParticle(PhysicalConstants.MuLeptonMass, ParticleCodes.MuLepton)
Electron = TheoreticalParticle(PhysicalConstants.ElectronMass, ParticleCodes.Electron)
AntiElectron = TheoreticalParticle(PhysicalConstants.ElectronMass, ParticleCodes.AntiElectron)
