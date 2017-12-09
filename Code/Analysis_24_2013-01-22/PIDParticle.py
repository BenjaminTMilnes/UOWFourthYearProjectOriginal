import TheoreticalParticle
import math

class PIDParticle:
	
	def __init__(self):
		self.ReconParticleID=-1
		self.ReconParticleIDWeight=-1
		self.ReconParticleIDWeightSecondary=-1
		self.ReconFrontMomentum=-1
		self.TrueParticleID=-1
		self.TrueEnergy=-1
		self.TrueFrontMomentum=-1
		self.ReconFrontDirectionX=0
		self.ReconFrontDirectionY=0
		self.ReconFrontDirectionZ=0
		self.SuitableTPCNodeNumber=False
		self.ReconFrontPositionT=-99999
		self.ReconFrontPositionX=-99999
		self.ReconFrontPositionY=-99999
		self.ReconFrontPositionZ=-99999
		
		self.Detectors=""

		self.ParticlePull = {}
		
	def CorrectlyReconstructed(self):
		return(self.ReconParticleID==self.TrueParticleID)
		
	def ReconTrueMomentumDifference(self):
		
		Difference=self.ReconFrontMomentum-self.TrueFrontMomentum
		
		return(Difference)
		
	def ReconstructedParticleEnergy(self):
		
		Mass=self.ReconstructedMass()

		ReconstructedEnergy=math.sqrt(self.ReconFrontMomentum*self.ReconFrontMomentum+Mass*Mass)
		
		return(ReconstructedEnergy)
		
	def ReconstructedMass(self):
		
		if(self.ReconParticleID==2212):
			ReconstructedMass=TheoreticalParticle.Proton.Mass
		elif(self.ReconParticleID==13):
			ReconstructedMass=TheoreticalParticle.MuLepton.Mass
		elif(self.ReconParticleID==11):
			ReconstructedMass=TheoreticalParticle.Electron.Mass
		elif(self.ReconParticleID==-11):			
			ReconstructedMass=TheoreticalParticle.AntiElectron.Mass
			
		return(ReconstructedMass)
