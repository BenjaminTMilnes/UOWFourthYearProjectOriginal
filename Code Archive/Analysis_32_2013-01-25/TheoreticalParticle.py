import ParticleCodes

class TheoreticalParticle:
	
	def __init__(self, Mass, PDGCode):
		
		self.PDGCode = PDGCode
		self.Mass = Mass
		
Proton = TheoreticalParticle(938.272046, ParticleCodes.Proton)
MuLepton = TheoreticalParticle(105.6583715, ParticleCodes.MuLepton)
Electron = TheoreticalParticle(0.510998928, ParticleCodes.Electron)
AntiElectron = TheoreticalParticle(0.510998910, ParticleCodes.AntiElectron)
