# Reconstructed Particle
#
# Last Modified 2013.01.17 14:23
#

import math
import ThreeVector
import FourVector

class ReconstructedParticle:
	
	def __init__(self):
		
		self.Position = FourVector.FourVector()
		self.Direction = ThreeVector.ThreeVector()
		self.EnergyMomentum = FourVector.FourVector()
