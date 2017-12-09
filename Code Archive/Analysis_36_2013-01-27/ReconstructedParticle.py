# Reconstructed Particle
#
# Last Modified 2013.01.17 14:23
#

import math
import Geometry

class ReconstructedParticle:
	
	def __init__(self):
		
		self.Position = Geometry.FourVector()
		self.Direction = Geometry.ThreeVector()
		self.EnergyMomentum = Geometry.FourVector()
		
		self.DirectionIsValid = False
