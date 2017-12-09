# Four-Vector
#
# This is a container class for four-component vectors.
#
# Last Modified 2013.01.16 22:11
#

import math

class FourVector:
	
	def __init__(self, T = 0, X = 0, Y = 0, Z = 0):
		
		self.T = float(T)
		self.X = float(X)
		self.Y = float(Y)
		self.Z = float(Z)
		
	def SpatialModulus(self):
		
		M = math.sqrt(self.X * self.X + self.Y * self.Y + self.Z * self.Z)
		
		return M
		
	def InvariantModulus(self):
		
		IM = 0
		
		IMSquared = self.T * self.T - self.X * self.X - self.Y * self.Y - self.Z * self.Z
		
		if (IMSquared > 0):

			IM = math.sqrt(IMSquared)
				
		return IM
