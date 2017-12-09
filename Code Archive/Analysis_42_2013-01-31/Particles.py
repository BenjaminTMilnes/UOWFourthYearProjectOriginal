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
