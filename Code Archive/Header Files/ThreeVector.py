# Three-Vector
#
# This is a container class for three-component vectors.
#
# Modified 2013.01.13 22:21
# Last Modified 2013.01.13 22:45
#

import math

class ThreeVector:
	
	def __init__(self, X = 0, Y = 0, Z = 0):
		
		self.X = float(X)
		self.Y = float(Y)
		self.Z = float(Z)
		
	def Modulus(self):
		
		M = math.sqrt(self.X * self.X + self.Y * self.Y + self.Z * self.Z)
		
		return M
